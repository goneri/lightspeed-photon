#!/usr/bin/env python3

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


def load_args(args: list[str]) -> argparse.Namespace:
    """Parse the CLI argument."""
    parser = argparse.ArgumentParser(description="Run prediction tests")
    parser.add_argument("path", type=Path, help="Location of the prediction tests")
    return parser.parse_args(args=args)


@dataclass
class Answer:
    """An answer coming back from the API."""

    # TODO: This class should wrap the answer received from the API
    some_content: str


@dataclass
class AnswerCheck:
    """A check that can be evaluate against an Answer."""

    module: str
    additional_args: list[str | dict[str, Any]] = field(default_factory=list)
    module_called_with: list[str | dict[str, Any]] = field(default_factory=list)

    def evaluate(self, answer: Answer) -> bool:
        """Evaluate the check against the answer."""
        # TODO
        return True


@dataclass
class TestCase:
    """Class for keeping track of the test case."""

    name: str
    prompt: str
    test_file: Path
    context_from_file: str = ""
    context: str = ""
    accepted_answers: list[AnswerCheck] = field(default_factory=list)

    def __post_init__(self, context_from_file: Optional[Path] = None) -> None:
        """Load the context from a file."""
        if not context_from_file:
            return
        context_file = self.test_file.parent / context_from_file
        self.context = context_file.read_text()

    def evaluate(self) -> None:
        """Query the API with context/prompt and evaluate all the checks."""
        print(f"Send context: {self.context}")
        print(f"Send prompt: {self.prompt}")
        print("**GETTING SOME RESULT")
        answer = Answer(some_content="")
        for check in self.accepted_answers:
            print(check)
            if check.evaluate(answer):
                print("Echo success!")
                break


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

    test_cases = test_loader(args.path)
    for test_case in test_cases:
        test_case.evaluate()
