#!/usr/bin/env python3


import logging
import os
from pathlib import Path
from time import sleep
from typing import Any

# import request
import yaml

# from dynaconf import settings

from ansible_lightspeed_service_client.api.ai import (
    ai_completions_create,
)
from ansible_lightspeed_service_client.client import (
    AuthenticatedClient,
)
from ansible_lightspeed_service_client.client import Client
from ansible_lightspeed_service_client.models.completion_request import (  # noqa # pylint: disable=line-too-long
    CompletionRequest,
)
from ansible_lightspeed_service_client.models.completion_response import (  # noqa # pylint: disable=line-too-long
    CompletionResponse,
)

from ansible_lightspeed.photon.utils.predictions_utils import Task

logging.basicConfig(filename="model-validator.log", level=logging.INFO)


TaskDictT = dict[str, Any]

# TODO
settings = {"SERVICE": "http://localhost:8000"}


def get_prediction(api_client, prompt: str, context: str) -> Task:
    if not prompt.lstrip().startswith("- name: "):
        prompt = f"- name: {prompt}"
    if context:
        prompt = context + prompt
    payload = CompletionRequest(prompt=prompt)  # type: ignore
    for i in range(10):
        response = ai_completions_create.sync_detailed(client=api_client, json_body=payload)
        if response.status_code == 429:
            sleep(1 * i)
        else:
            break
    assert isinstance(response.parsed, CompletionResponse)
    assert response.status_code == 200
    task = Task(yaml.safe_load(response.parsed.predictions[0]))
    return task
