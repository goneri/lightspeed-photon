#!/usr/bin/env python3


import logging
from time import sleep

# import request
import yaml

from ansible_lightspeed.photon.remote import Remote
from ansible_lightspeed.photon.utils.predictions_utils import Task
from ansible_lightspeed_service_client.api.ai import (
    ai_completions_create,
)
from ansible_lightspeed_service_client.models.completion_request import (  # noqa # pylint: disable=line-too-long
    CompletionRequest,
)
from ansible_lightspeed_service_client.models.completion_response import (  # noqa # pylint: disable=line-too-long
    CompletionResponse,
)

logging.basicConfig(filename="model-validator.log", level=logging.INFO)


def get_prediction(remote: "Remote", prompt: str, context: str) -> Task:
    if not prompt.lstrip().startswith("- name: "):
        prompt = f"- name: {prompt}"
    if context:
        prompt = context + prompt
    payload = CompletionRequest(prompt=prompt)  # type: ignore
    for i in range(10):
        response = ai_completions_create.sync_detailed(client=remote.client, json_body=payload)
        if response.status_code == 429:
            sleep(1 * i)
        else:
            break
    assert isinstance(response.parsed, CompletionResponse)
    assert response.status_code == 200
    task = Task(yaml.safe_load(response.parsed.predictions[0]))
    return task
