=================
Lightspeed Photon
=================

Your tool to validate the behaviour of Ansible Lightspeed.

With the help of Lightspeed Photon, you can run a series of test-cases against Ansible Lightspeed and validate the results. Lightspeed Photon is designed to fit nicely in a CI context.

Example
=======


.. shell::

   $ lightspeed-photon test-directory/
   (...)


Test format
===========

A minimal test is composed of a name, a prompt and a series of accepted answers that will be used to evaluate the server answer.


.. yaml::
    - name: test_container_flow_with_podman_1
      prompt: Stop a podman container named my_app
      accepted_answers:
      - module: containers.podman.podman_container
        module_called_with:
        - name: my_app
        - state: stopped

- `name`: the internal name of the test
- `prompt`: the string to send to the server (the name of the task)
- `accepted_answers`: a list of accepted answer blocks as explain below.


accept_answers
--------------

Photon will evaluate each `accepted_answers` entry against the answer coming from the server. Each criterion can bring points and Photon will keep the accepted_answer with the highest amount of points. An `accepted_answers` is a dictionary with the following keys:

- `module`: the name of the module we expect.
- `module_called_with`: a list of expected keys, e.g. `- state` if we expect the `state` parameter, and `- state: present` if we want to also check the value.
- `module_not_called_with`: is the opposite, a list of arguments that we don't want to see.
- `task_uses_loop`: if the answer should use a loop condition.
- `task_uses_become`: if we task can use any kind of privilege escalation.

Context
-------

Sometimes we want to give some context to improve the quality of the answer. You can use the `context` or `context_from_file` for this:

- `context`: is a inline string that will be used as the context.
- `context_from_file`: is the location of a file that should be used as the context.

.. yaml::
    - name: create_an_aws_instance_with_context
      prompt: "    - name: create a new AWS instance called test_vm"
      context_from_file: context/aws_long_context.yaml

.. yaml::
    - name: create_an_aws_instance_with_context
      prompt: "    - name: create a new AWS instance called test_vm"
      context: "- set_fact:\n    foo: bar\n"


scoring
=======

Score are computed based on these weights:

- correct module: +40
- use loop is correct: +10
- use become is correct: +5
- an expected key is present: +10
- an expected key/val is present: +15
- an unwanted key is present: -10
- an unwanted key/val is present: -15
