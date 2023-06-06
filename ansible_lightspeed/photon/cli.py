#!/usr/bin/env python3

import os
import argparse
import re
import sys
from dataclasses import InitVar, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

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
        elif isinstance(i, list):
            v += i
        else:
            raise TypeError()
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

    def evaluate(self, task: Task) -> EvaluationResult:
        """Evaluate the check against the answer."""
        result = EvaluationResult(task)
        if self.module != task.module:
            result.module_name_is_correct = ResultStatus.FAILURE
            logger.debug(f"Module doesn't match : {self.module} != {task.module}")
            return result
        result.score += 20

        if self.module_called_with:
            v, kv = check_list_to_kwargs(self.module_called_with)
            if task.module_called_with(*v, **kv):
                result.score += 10

        if self.module_not_called_with:
            v, kv = check_list_to_kwargs(self.module_not_called_with)
            if task.module_not_called_with(*v, **kv):
                result.score += 10

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
        logger.debug(f"\nTesting with {remote.name}")
        logger.debug(f"📹context: {self.context_origin()}")
        logger.debug(f"📝test path {self.test_file}")
        logger.verbose(f"🔮Sending prompt: {self.prompt}")
        # TODO read configuration from CLI arguments

        try:
            task = remote.get_prediction(self.prompt, self.context)
        except PredictionFailure:
            logger.verbose("🔥Invalid answer from the server.")
            return 0
        logger.verbose("🧙Answer:\n" + yaml.dump(task.struct))
        best_score: int = 0
        for index, check in enumerate(self.accepted_answers, 1):
            if len(self.accepted_answers):
                logger.verbose(f"Checking {index} accepted_answer...")
            result = check.evaluate(task)
            if len(self.accepted_answers):
                logger.verbose(f"... score {result.score}")
            if result.score > best_score:
                best_score = result.score
        return best_score


def load_test_file(test_file: Path) -> list[TestCase]:
    """Load all the TestCase from a test file."""
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

    score_per_remote = {r.name: 0 for r in remotes}
    for test_case in test_cases:
        if args.test_case_filter and not re.match(args.test_case_filter, test_case.name):
            continue
        logger.info(f"🎬starting: {test_case.name}")
        scores = [(remote, test_case.evaluate(remote)) for remote in remotes]

        logger.info("test score(s)")
        for remote, score in scores:
            if score == 0:
                logger.info(f"⭕ [{remote.name}]: 0")
            else:
                logger.info(f"✅ [{remote.name}]: {score}")
                score_per_remote[remote.name] += score

    logger.info("\n🏁Final score(s)")
    for remote_name, score in score_per_remote.items():
        logger.info(f"  - {remote_name}: {score}")
