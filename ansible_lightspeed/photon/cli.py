#!/usr/bin/env python3

import os
import argparse
import re
import sys
from dataclasses import InitVar, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union
import textwrap

import yaml

from ansible_lightspeed.photon.logger import logger
from ansible_lightspeed.photon.remote import PredictionFailure, Remote
from ansible_lightspeed.photon.utils.predictions_utils import Task


def load_args(args: list[str]) -> argparse.Namespace:
    """Parse the CLI argument."""
    parser = argparse.ArgumentParser(description="Run prediction tests")
    parser.add_argument("path", type=Path, help="Location of the prediction tests")
    parser.add_argument(
        "--test-case-filter", type=str, help="Only run the testcases matching this name (regexp)"
    )
    parser.add_argument("--verbose", action="store_true", help="Increase the verbosity")
    parser.add_argument(
        "--debug", action="store_true", help="Give more information to troubleshoot a test"
    )
    parser.add_argument("--remote", type=str, help="Run the checks with the following remote only")
    return parser.parse_args(args=args)


class ResultStatus(Enum):
    NOT_EVALUATED = 1
    FAILURE = 2
    SUCCESS = 3


@dataclass
class EvaluationResult:
    task: Task

    score: int = 0
    module_name_is_correct: ResultStatus = ResultStatus.NOT_EVALUATED
    # The module arguments are correct
    module_args_are_correct: ResultStatus = ResultStatus.NOT_EVALUATED
    # The task parameters, at the root level of the task, are correct
    task_parameters_are_correct: ResultStatus = ResultStatus.NOT_EVALUATED


CheckListT = list[Union[str, dict[str, Any]]]


def check_list_to_kwargs(check_list: CheckListT) -> tuple[list[str], dict[str, Any]]:
    """Convert a list as found with module_called_with to *args, **kwargs output."""
    v: list[str] = []
    kv = {}
    for i in check_list:
        if isinstance(i, dict):
            kv.update(i)
        else:
            v += [i]
    return list(v), kv


@dataclass
class AnswerCheck:
    """A check that can be evaluate against an Answer."""

    module: str
    module_called_with: CheckListT = field(default_factory=list)
    module_not_called_with: CheckListT = field(default_factory=list)
    task_called_with: CheckListT = field(default_factory=list)
    task_not_called_with: CheckListT = field(default_factory=list)
    task_uses_loop: Optional[bool] = None
    task_uses_become: Optional[bool] = None

    def __post_init__(self) -> None:
        not_called_with_default = ["delegate_to", "ignore_errors"]

        def _need_default(key: str) -> bool:
            for i in not_called_with_default:
                for j in self.task_called_with:
                    if isinstance(j, dict) and i in j:
                        return False
                    elif i == j:
                        return False
            return True

        for i in not_called_with_default:
            if _need_default(i):
                self.task_not_called_with.append(i)

    def evaluate(self, task: Task) -> EvaluationResult:
        """Evaluate the check against the answer."""
        result = EvaluationResult(task)
        if self.module != task.module:
            result.module_name_is_correct = ResultStatus.FAILURE
            logger.debug(f"Module name is not {self.module}")
            return result
        result.score += 40

        v, kv = check_list_to_kwargs(self.module_called_with)
        result.score += task.module_called_with(*v, **kv)

        v, kv = check_list_to_kwargs(self.module_not_called_with)
        result.score += task.module_not_called_with(*v, **kv)

        v, kv = check_list_to_kwargs(self.task_called_with)
        result.score += task.task_called_with(*v, **kv)

        v, kv = check_list_to_kwargs(self.task_not_called_with)
        result.score += task.task_not_called_with(*v, **kv)

        if self.task_uses_loop is not None:
            if self.task_uses_loop == task.use_loop():
                result.score += 10
            else:
                logger.debug("Unexpected setting for the loop key")

        if self.task_uses_become is not None:
            if task.use_privilege_escalation() == self.task_uses_become:
                result.score += 5
            else:
                logger.debug("Unexpected setting for the become key")

        result.module_name_is_correct = ResultStatus.SUCCESS

        return result


@dataclass
class TestCase:
    """Class for keeping track of the test case."""

    name: str
    prompt: str
    test_file: Path
    context_file: Optional[Path] = None
    context: str = ""
    accepted_answers: list[AnswerCheck] = field(default_factory=list)
    task: Optional[Task] = None
    context_from_file: InitVar[Union[Path, None]] = None

    def __post_init__(self, context_from_file: Optional[Path] = None) -> None:
        """Load the context from a file."""
        if not context_from_file:
            return
        self.context_file: Path = self.test_file.parent / context_from_file
        self.context = self.context_file.read_text()

    def context_origin(self) -> str:
        if self.context_file:
            return f"from {self.context_file}"
        if self.context:
            return "from inline string"
        return "none"

    def evaluate(self, remote: Remote) -> int:
        """Query the API with context/prompt and evaluate all the checks."""
        logger.debug(f"Testing with {remote.name}")
        logger.debug(f"📹context: {self.context_origin()}")
        logger.debug(f"📝test path {self.test_file}")
        logger.verbose(f"🔮Sending prompt: {self.prompt}")
        # TODO read configuration from CLI arguments

        try:
            task = remote.get_prediction(self.prompt, self.context)
        except PredictionFailure:
            logger.verbose("🔥Invalid answer from the server.")
            return 0
        logger.verbose(
            "🧙Answer:\n\n" + textwrap.indent(yaml.dump(task.struct), "    \x1B[3m") + "\x1B[0m"
        )
        best_score: int = 0
        for check in self.accepted_answers:
            logger.debug(f"Checking with {check}")
            result = check.evaluate(task)
            if len(self.accepted_answers):
                logger.verbose(f"... score {result.score}")
            if result.score > best_score:
                best_score = result.score
        return best_score


def load_test_file(test_file: Path) -> list[TestCase]:
    """Load all the TestCase from a test file."""
    print(f"Loading {test_file}")
    with test_file.open() as stream:
        content = yaml.safe_load(stream)

    if not isinstance(content, list):
        raise TypeError(f"{test_file} should be a list")  # noqa: TRY003

    for c in content:
        c["test_file"] = test_file
        c["accepted_answers"] = [AnswerCheck(**i) for i in c["accepted_answers"]]

    return [
        TestCase(
            **i,
        )
        for i in content
    ]


def test_loader(test_path: Path) -> list[TestCase]:
    """Load all the TestCases."""
    test_cases: list[TestCase] = []
    if test_path.is_file():
        test_cases = load_test_file(test_path)
    elif test_path.is_dir():
        for i in test_path.glob("**/test_*.yaml"):
            test_cases += load_test_file(i)
    return test_cases


def main() -> None:
    """Entry point."""
    args = load_args(sys.argv[1:])

    if args.debug:
        logger.setLevel("DEBUG")
    elif args.verbose:
        logger.setLevel("VERBOSE")
    else:
        logger.setLevel("INFO")

    remotes = [
        Remote(
            name="prod",
            remote_type="service",
            end_point="https://c.ai.ansible.redhat.com",
            token=os.environ.get("LIGHTSPEED_TOKEN", ""),
        ),
    ]

    if args.remote:
        remotes = [r for r in remotes if args.remote == r.name]

    test_cases = test_loader(args.path)

    @dataclass
    class ResultEntry:
        remote: Remote
        test_case: TestCase
        value: int

    results: list[ResultEntry] = []
    for test_case in test_cases:
        if args.test_case_filter and not re.match(args.test_case_filter, test_case.name):
            continue
        logger.info(f"\n🎬starting: {test_case.name}")
        from typing import TypedDict

        for remote in remotes:
            result = ResultEntry(remote, test_case, test_case.evaluate(remote))
            results.append(result)
            icon = "✅" if result.value else "⭕"
            logger.info(f"{icon} [{result.remote.name}]: {result.value}")

    results_per_remote: dict[str, list[ResultEntry]] = {r.name: [] for r in remotes}
    for score in results:
        results_per_remote[score.remote.name].append(score)

    from collections import defaultdict

    results_per_file: dict[str, list[ResultEntry]] = {
        result.test_case.test_file.name: [] for result in results
    }
    for result in results:
        results_per_file[result.test_case.test_file.name].append(result)

    logger.info("\n🏁Score per file(s)")
    for test_file, results in results_per_file.items():
        print(f"📄 {test_file}")
        per_test_case: dict[str, dict[str, list[ResultEntry]]] = defaultdict(dict)
        for result in results:
            if result.remote.name not in per_test_case[result.test_case.name]:
                per_test_case[result.test_case.name][result.remote.name] = []
            per_test_case[result.test_case.name][result.remote.name].append(result)

        for test_case_name, r_per_remote in per_test_case.items():
            print(f"   test_case_name={test_case_name}")
            max_value = max(result.value for results in r_per_remote.values() for result in results)
            for remote_name, results in sorted(r_per_remote.items()):
                sum_value = sum(r.value for r in results)
                ascii_code = "\033[1m" if max_value == sum_value else ""
                print(f"     {remote_name}: {ascii_code}{sum_value}\033[0m")

    logger.info("\n🏁Final score(s)")
    for remote_name, results in results_per_remote.items():
        sum_value = sum(r.value for r in results)
        logger.info(f"  - {remote_name}: \033[1m{sum_value}\033[0m")
