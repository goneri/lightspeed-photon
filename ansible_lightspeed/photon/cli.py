#!/usr/bin/env python3

from enum import Enum
import argparse
import sys
from pprint import pformat
from dataclasses import dataclass, field, InitVar
from pathlib import Path
from typing import Any, Optional
from ansible_lightspeed.photon.utils.predictions_utils import Task

import yaml


from ansible_lightspeed.photon.logger import logger

from ansible_lightspeed.photon.client import AuthenticatedClient, get_prediction


def load_args(args: list[str]) -> argparse.Namespace:
    """Parse the CLI argument."""
    parser = argparse.ArgumentParser(description="Run prediction tests")
    parser.add_argument("path", type=Path, help="Location of the prediction tests")
    parser.add_argument("--verbose", action="store_true", help="Increase the verbosity")
    parser.add_argument(
        "--debug", action="store_true", help="Give more information to troubleshoot a test"
    )
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


CheckListT = list[str | dict[str, Any]]


def check_list_to_kwargs(check_list):
    v = []
    kv = {}
    for i in check_list:
        if isinstance(i, dict):
            kv.update(i)
        elif isinstance(i, list):
            v += i
        else:
            raise TypeError()
    return v, kv


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
        result.score += 10

        if self.module_called_with:
            v, kv = check_list_to_kwargs(self.module_called_with)
            if task.module_called_with(*v, **kv):
                return result
        result.score += 10

        if self.module_not_called_with:
            v, kv = check_list_to_kwargs(self.module_not_called_with)
            if task.module_not_called_with(*v, **kv):
                return result
        result.score += 10

        if self.task_uses_loop is not None:
            if self.task_uses_loop != task.use_loop():
                logger.info("Unexpect setting for the loop key")
                return result
        result.score += 10

        if self.task_uses_become is not None:
            if task.use_privilege_escalation() != self.task_uses_become:
                logger.info("Unexpect setting for the become key")
                return result
        result.score += 10

        result.module_name_is_correct = ResultStatus.SUCCESS

        return result


@dataclass
class TestCase:
    """Class for keeping track of the test case."""

    name: str
    prompt: str
    test_file: Path
    context_file: str = ""
    context: str = ""
    accepted_answers: list[AnswerCheck] = field(default_factory=list)
    task: Optional[Task] = None
    context_from_file: InitVar[Path | None] = None

    def __post_init__(self, context_from_file: Optional[Path] = None) -> None:
        """Load the context from a file."""
        if not context_from_file:
            return
        self.context_file = self.test_file.parent / context_from_file
        self.context = self.context_file.read_text()

    def context_origin(self):
        if self.context_file:
            return f"from {self.context_file}"
        if self.context:
            return "from inline string"
        return "none"

    def evaluate(self) -> None:
        """Query the API with context/prompt and evaluate all the checks."""
        logger.info(f"🎬starting: {self.name}")
        logger.debug(f"📹context: {self.context_origin()}")
        logger.debug(f"📝test path {self.test_file}")
        logger.verbose(f"🔮Sending prompt: {self.prompt}")
        # TODO read configuration from CLI arguments
        import os

        api_client = AuthenticatedClient("http://localhost:8000", os.environ.get("WISDOM_TOKEN"))
        task = get_prediction(api_client, self.prompt, self.context)
        logger.verbose("🧙Answer:\n" + yaml.dump(task.struct))
        best_result = None  # type: EvaluationResult
        for index, check in enumerate(self.accepted_answers, 1):
            if len(self.accepted_answers):
                logger.verbose(f"Checking {index} accepted_answer...")
            result = check.evaluate(task)
            if len(self.accepted_answers):
                logger.verbose(f"... score {result.score}")
            if best_result is None:
                best_result = result
                continue
            if result.score > best_result.score:
                best_result = result
            if best_result.score == 100:
                break
        if best_result.score == 0:
            logger.info("⭕ No test passing")
        else:
            logger.info(f"✅ Final score: {best_result.score}")


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

    test_cases = test_loader(args.path)
    for test_case in test_cases:
        test_case.evaluate()
