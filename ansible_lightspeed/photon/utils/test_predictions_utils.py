# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
import pytest
import yaml

from utils.predictions_utils import Task

sample_file = """
name: Foo bar
file:
  path: /etc/fstab
  state: absent
"""


@pytest.mark.unittests
def test_basic():
    t = Task(yaml.safe_load(sample_file))
    assert t.module == "file"
    assert t.args == {"path": "/etc/fstab", "state": "absent"}
    assert t.use_loop() is False
    assert t.use_ignore_errors() is False
    assert t.use_privilege_escalation() is False
    assert t.oldstyle_inline_args() is False


sample_complex = """
name: Foo bar
file:
  path: /etc/fstab
  state: absent
with_items: ["a", "b"]
become: true
ignore_errors: true
"""


@pytest.mark.unittests
def test_complex():
    t = Task(yaml.safe_load(sample_complex))
    assert t.module == "file"
    assert t.args == {"path": "/etc/fstab", "state": "absent"}
    assert t.use_loop() is True
    assert t.use_ignore_errors() is True
    assert t.use_privilege_escalation() is True
    assert t.oldstyle_inline_args() is False


sample_fails_when_false = """
name: Foo bar
file:
  path: /etc/fstab
  state: absent
fails_when: false
"""


@pytest.mark.unittests
def test_fails_when_false():
    t = Task(yaml.safe_load(sample_fails_when_false))
    assert t.use_ignore_errors() is True


sample_oldstyle_args = """
name: Foo bar
file: path=/etc/fstab state=absent
"""


@pytest.mark.unittests
def test_oldstyle_args():
    t = Task(yaml.safe_load(sample_oldstyle_args))
    assert t.module == "file"
    assert t.oldstyle_inline_args() is True


sample_jinja_vars_generic = """
name: Foo bar
file:
  path: "{{ var1 }}"
  state: "{{ var2 }}"
with_items: "{{ var3 }}"
become: "{{var4}}"
when:
- var5
"""


@pytest.mark.unittests
def test_jinja_vars():
    t = Task(yaml.safe_load(sample_jinja_vars_generic))
    assert t.jinja2_inputs() == [f"var{i}" for i in range(1, 6)]


sample_jinja_vars_special_cases = """
name: Foo bar
assert:
  that:
    - var1 is defined
when:
- (var2 is defined) or (var3 is defined)
"""


@pytest.mark.unittests
def test_jinja_vars_special_cases():
    t = Task(yaml.safe_load(sample_jinja_vars_special_cases))
    assert t.jinja2_inputs() == [
        "var1 is defined",
        "(var2 is defined) or (var3 is defined)",
    ]


sample_jinja_handler_str = """
name: Foo bar
dosoemthing:
  var: poule
notify: foo
"""


@pytest.mark.unittests
def test_read_handler_str():
    t = Task(yaml.safe_load(sample_jinja_handler_str))
    assert t.handlers() == {"foo"}


sample_jinja_handler_list = """
name: Foo bar
dosoemthing:
  var: poule
notify:
- foo
- bar
"""


@pytest.mark.unittests
def test_read_handler_list():
    t = Task(yaml.safe_load(sample_jinja_handler_list))
    assert t.handlers() == {"foo", "bar"}


sample_jinja_tags_str = """
name: Foo bar
dosoemthing:
  var: poule
tags: foo
"""


@pytest.mark.unittests
def test_read_tags_str():
    t = Task(yaml.safe_load(sample_jinja_tags_str))
    assert t.tags() == {"foo"}


sample_jinja_tags_list = """
name: Foo bar
dosoemthing:
  var: poule
tags:
- foo
- bar
"""


@pytest.mark.unittests
def test_read_tags_list():
    t = Task(yaml.safe_load(sample_jinja_tags_list))
    assert t.tags() == {"foo", "bar"}
