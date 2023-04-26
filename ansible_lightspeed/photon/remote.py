#!/usr/bin/env python3

import json
import urllib.request
from dataclasses import dataclass
from typing import Any, Literal, Optional

import yaml

from ansible_lightspeed.photon.logger import logger
from ansible_lightspeed.photon.utils.predictions_utils import Task
from model_grpc_client.grpc_client import GrpcClient


def unwrap_prediction(prompt: str, data: dict[str, Any]) -> dict[str, Any]:
    """Unwrap a given response to dict."""
    first_prediction = prompt + "\n" + data["predictions"][0]
    try:
        tasks = yaml.safe_load(first_prediction)
    except yaml.YAMLError:
        logger.error("CANNOT LOAD YAML: %s", first_prediction)
        raise
    return tasks[0]


class PredictionFailure(Exception):
    """Failed to get a prediction."""


@dataclass
class Remote:
    remote_type: Literal["service", "model_grpc"]
    name: str
    end_point: str
    token: Optional[str | None] = None
    grpc_model_name: Optional[str | None] = None

    def get_prediction(self, prompt: str, context: str) -> Task:
        if not prompt.lstrip().startswith("- name: "):
            prompt = f"- name: {prompt}"

        if self.remote_type == "service":
            if context:
                prompt = context + prompt

            data = json.dumps({"prompt": prompt})
            req = urllib.request.Request(
                url=f"{self.end_point}/api/v0/ai/completions/",
                data=data.encode(),
                method="POST",
                headers={
                    "content-type": "application/json",
                    "Authorization": f"Bearer {self.token}",
                },
            )
            with urllib.request.urlopen(req) as f:
                if f.status != 200:
                    logger.verbose(f"HTTP status: {f.status}")
                content = f.read().decode("utf-8")
            try:
                parsed = json.loads(content)
            except json.decoder.JSONDecodeError:
                logger.verbose("Cannot load the JSON answer")
                raise PredictionFailure from None
            task = Task(yaml.safe_load(parsed["predictions"][0]))
        else:
            client = GrpcClient(inference_url=self.end_point)
            payload = {
                "instances": [
                    {
                        "context": context,
                        "prompt": prompt,
                    }
                ]
            }
            data = client.infer(payload, self.grpc_model_name)
            unwrapped = unwrap_prediction(prompt, data)
            task = Task(unwrapped)
        return task
