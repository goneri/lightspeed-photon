# pylint: disable=C0103
"""utils to validate and mnipulate the predictions API response."""
import logging
import re
from typing import Any, Literal, Union, cast

import yaml
from ansible.module_utils.parsing.convert_bool import BOOLEANS_FALSE, BOOLEANS_TRUE

from ansible_lightspeed.photon.logger import logger


def is_jinja2(value: Any) -> bool:
    """Validate if the input is valid jinja2."""
    return isinstance(value, str) and bool(re.search(r"{{.*}}", value))


def validate_int(value: Any) -> bool:
    """Validate if the input is valid int."""
    if isinstance(value, int):
        return True
    try:
        int(value)
        return True  # noqa: TRY300
    except ValueError:
        pass
    if is_jinja2(value):
        return True
    return False


def validate_str(value: Any) -> bool:
    """Validate if the input is valid string."""
    if isinstance(value, str):
        return True
    if validate_int(value):
        return True
    return False


def validate_bool(value: Any) -> bool:
    """Validate if the input is bool."""
    if value in BOOLEANS_FALSE:
        return True
    if value in BOOLEANS_TRUE:
        return True
    if isinstance(value, bool):
        return True
    if is_jinja2(value):
        return True
    return False


def validate_condition(value: Any) -> bool:
    """Validate if the input is a condition."""
    if isinstance(value, (str, list)):
        return True
    if validate_bool(value):
        return True
    return False


def validate_str_or_list_of_str(value: Any) -> bool:
    """Validate if the input is valid string or list of strings."""
    if isinstance(value, str):
        return True
    if isinstance(value, list):
        return all(isinstance(i, str) for i in value)
    return False


def validate_str_or_dict(value: Any) -> bool:
    """Validate if the input is dict or string."""
    if isinstance(value, (str, dict)):
        return True
    return False


def validate_dict(value: Any) -> bool:
    """Validate if the input is valid dict."""
    if isinstance(value, dict):
        return True
    if is_jinja2(value):
        return True
    return False


def validate_list(value: Any) -> bool:
    """Validate if the input is valid list."""
    if isinstance(value, list):
        return True
    if is_jinja2(value):
        return True
    return False


def invalid() -> Literal[False]:
    """Input is invalid."""
    return False


class WrongModule(AssertionError):
    """The module name is wrong."""


class MissingModuleParameter(AssertionError):
    """The module parameter is missing."""


class IncorrectModuleParameterValue(AssertionError):
    """The value of a module parameter is invalid."""


class IncorrectStateValue(AssertionError):
    """The state field is incorrect."""


class UnexpectedModuleParameter(AssertionError):
    """Unexpected module parameter."""


class ShouldNotUseALoop(AssertionError):
    """The loop is superfluous."""


class Task:
    """thit calss is used to validate the predictions made by the service."""

    known_fields = {
        "always_run": invalid,  # Not supported by Ansible since 2.2
        "args": validate_dict,
        "async": validate_int,
        "become": validate_bool,
        "become_flags": validate_str,
        "become_method": validate_str,
        "become_user": validate_str,
        "changed_when": validate_condition,
        "check_mode": validate_bool,
        "connection": validate_str,
        "delay": validate_int,
        "delegate_facts": validate_bool,
        "delegate_to": validate_str,
        "diff": validate_bool,
        "environment": validate_dict,
        "failed_when": validate_condition,
        "ignore_errors": validate_bool,
        "ignore_unreachable": validate_bool,
        "loop": validate_list,
        "loop_control": validate_dict,
        "name": validate_str,
        "no_log": validate_bool,
        "notify": validate_str_or_list_of_str,
        "poll": validate_int,
        "register": validate_str,
        "remote_user": validate_str,
        "retries": validate_int,
        "run_once": validate_bool,
        "sudo": validate_bool,
        "sudo_user": validate_str,
        "tags": validate_str_or_list_of_str,
        "until": validate_condition,
        "vars": validate_dict,
        "when": validate_condition,
        # The documentation advices to use loop instead of these with_*
        # keys, should we raise a warning.
        "with_dict": validate_dict,
        "with_fileglob": validate_list,
        "with_first_found": validate_list,
        "with_flattened": validate_list,
        "with_together": validate_list,
        "with_subelements": validate_list,
        "with_inventory_hostnames": validate_list,
        "with_items": validate_list,
        "with_indexed_items": validate_list,
        "with_nested": validate_list,
    }

    @classmethod
    def validate_input(cls: Any, struct: dict[str, Any]) -> bool:
        """Validate the sanity of the input structure."""
        for name, value in struct.items():
            if name in Task.known_fields and not cls.known_fields[name](value):
                logging.error("Type of %s is invalid `%s`", name, value)
                return False
        try:
            keys = set(struct.keys())
        except AttributeError:
            logging.error("Cannot load keys :%s", struct)  # noqa: TRY400
            return False

        candidates = list(keys - set(Task.known_fields.keys()))
        if len(candidates) == 0:
            logging.error("Cannot find a module name for this task")
            return False
        if len(candidates) > 1:
            logging.error(
                "Too many potential module names in the task suggestion, candidates=%s",
                candidates,
            )
            return False

        if not (
            re.match(r"^[-_\da-z]+$", candidates[0])
            or re.match(r"^[_a-z\d]+\.[_a-z\d]+\.[-_\da-z]+$", candidates[0])
        ):
            logging.error("Unexpected module name: `%s`", candidates[0])
            return False
        return True

    def __init__(self, struct: dict[str, Any]):
        self.struct = struct
        self.module = self.resolve_module_name()
        self.args = self.get_args()

    def get_args(self) -> dict[str, Any]:
        """Return the module argument args used to call the task."""
        if self.module in ["ansible.builtin.set_fact", "set_fact"]:
            key_value = self.struct[self.module]
            return self.struct.get("args", {"key_value": key_value})
        if isinstance(self.struct.get("args"), dict):
            return cast(dict[str, Any], self.struct.get("args"))
        if self.module and isinstance(self.struct[self.module], dict):
            return cast(dict[str, Any], self.struct[self.module])
        return {}

    def resolve_module_name(self) -> str:
        """Resolve the module name."""
        keys = set(self.struct.keys())
        candidates = list(keys - set(Task.known_fields.keys()))
        if candidates:
            return candidates[0]
        return ""

    def module_called_with(self, *args: Union[str, list[str]], **kwargs: dict[str, Any]) -> bool:
        """Assert the package name match the expectation."""
        for k in args:
            if isinstance(k, list):
                if not any(arg in self.args for arg in k):
                    logger.debug("Missing one of the parameters: %s", k)
                    return False
            else:
                if k not in self.args:
                    logger.debug("Missing parameter: %s", k)
                    return False

        for k, v in kwargs.items():
            if k not in self.args:
                logger.debug("Missing parameter: %s", k)
                return False

            if isinstance(v, (str, int, bool)):
                if self.args[k] != v:
                    logger.debug(
                        f"Incorrect parameter value for key {k}: got {self.args[k]}, "
                        f"expected: {v}"
                    )
                    return False
            elif isinstance(v, set):
                if self.args[k] not in v:
                    logger.debug(f"Incorrect parameter value for key {k}: got {self.args[k]}, ")

                logger.debug("Invalid type: %s, expect set, int, bool or str", type(v))
                return False
        return True

    def module_not_called_with(self, *args: str, **kwargs: dict[str, Any]) -> bool:
        """Assert the module was not called with unwanted parameters."""
        for k in args:
            if k in self.args:
                logger.debug(f"Unexpected key: {k}")
                return False
        for k, v in kwargs.items():
            if k in self.args and self.args[k] == v:
                logger.debug(f"Unexpected key/value: {k}, {v}")
                return False
        return True

    def yaml_print(self) -> None:
        """Print yaml file."""
        print(yaml.dump(self.struct))

    def use_loop(self) -> bool:
        """Validate a loop is used."""
        for i in [
            "loop",
            "loop_control",
            "with_cartesian",
            "with_dict",
            "with_flattened",
            "with_indexed_items",
            "with_items",
            "with_list",
            "with_nested",
            "with_random_choice",
            "with_sequence",
            "with_subelements",
            "with_together",
        ]:
            if i in self.struct:
                return True
        return False

    def use_ignore_errors(self) -> bool:
        """Validate ignore-errors is used."""
        if self.struct.get("fails_when") in BOOLEANS_FALSE:
            return True
        return self.struct.get("ignore_errors", "no") in BOOLEANS_TRUE

    def use_privilege_escalation(self) -> bool:
        """Validate privilaege escalation is used."""
        return "become" in self.struct

    def oldstyle_inline_args(self) -> bool:
        """Raise an error if old style is used."""
        if self.module in [
            "ansible.builtin.shell",
            "shell",
            "ansible.builtin.command",
            "command",
            "ansible.builtin.local_action",
            "local_action",
        ]:
            return False
        old_style_args = self.struct[self.module] and isinstance(self.struct[self.module], str)
        return old_style_args

    def jinja2_inputs(self) -> list[str]:
        """Return a list from the given input."""
        values = []
        find_var_re = r"{{\s*(.*?)\s*}}"

        def add_any(value: Any) -> None:
            if isinstance(value, list):
                for i in value:
                    add_any(i)
            elif isinstance(value, str):
                for j in re.findall(find_var_re, value) or [value]:
                    values.append(j)

        def walk(value: Any) -> None:
            if isinstance(value, list):
                for i in value:
                    walk(i)
            elif isinstance(value, dict):
                for i in value.values():
                    walk(i)
            elif isinstance(value, str):
                for var in re.findall(find_var_re, value):
                    values.append(var)

        if self.module in ["ansible.builtin.assert", "assert"]:
            add_any(self.get_args().get("that", []))
        walk(self.struct)

        # When is always a Jinja2 statement
        add_any(self.struct.get("when"))

        empty_template = r"^\s*{{\s*}}\s*$"
        values = [v for v in values if not re.match(empty_template, v)]
        values = [v.split(".")[0] for v in values]
        values = [v for v in values if not v.startswith("ansible_")]

        return values

    def handlers(self) -> set[str]:
        """Return the handlers being used."""
        value = self.struct.get("notify", [])
        return {value} if isinstance(value, str) else set(value)

    def tags(self) -> set[str]:
        """Return the tags being used."""
        value = self.struct.get("tags", [])
        return {value} if isinstance(value, str) else set(value)
