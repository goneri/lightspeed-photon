#!/usr/bin/env python3

import json
import urllib.request
from dataclasses import dataclass
from typing import Literal
from time import sleep

import yaml

from ansible_lightspeed.photon.logger import logger
from ansible_lightspeed.photon.utils.predictions_utils import Task
from model_grpc_client.grpc_client import GrpcClient, GrpcPayload


class PredictionFailure(Exception):  # noqa: N818
    """Failed to get a prediction."""


@dataclass
class Remote:
    remote_type: Literal["service", "model_grpc"]
    name: str
    end_point: str
    token: str = ""
    grpc_model_name: str = ""

    def get_prediction(self, prompt: str, context: str) -> Task:
        if not prompt.lstrip().startswith("- name: "):
            prompt = f"- name: {prompt}"

        if self.remote_type == "service":
            if context:
                prompt = context + prompt

            payload = json.dumps({"prompt": prompt}).encode()
            req = urllib.request.Request(
                url=f"{self.end_point}/api/v0/ai/completions/",
                data=payload,
                method="POST",
                headers={
                    "content-type": "application/json",
                    "Authorization": f"Bearer {self.token}",
                },
            )

            content = ""
            # S310 Audit URL open for permitted schemes. Allowing use of `file:`
            # or custom schemes is often unexpected.
            for retry in range(10, 1, -1):
                try:
                    with urllib.request.urlopen(req) as f:  # noqa: S310
                        if f.status != 200:
                            logger.verbose(f"HTTP status: {f.status}")
                        content = f.read().decode("utf-8")
                        break
                except urllib.error.HTTPError as e:
                    if e.code == 429:
                        sleep(retry)
                        continue
                    raise
            if not content:
                raise PredictionFailure("Cannot get an answer from the server. Too many retry.")
            try:
                parsed = json.loads(content)
            except json.decoder.JSONDecodeError:
                logger.verbose("Cannot load the JSON answer")
                raise PredictionFailure from None
            task = Task(yaml.safe_load(parsed["predictions"][0]))
        else:
            client = GrpcClient(inference_url=self.end_point)
            grpc_payload = GrpcPayload(context, prompt)
            try:
                data = client.infer(grpc_payload, self.grpc_model_name)
            except yaml.YAMLError:
                raise PredictionFailure from None
            del data["name"]
            task = Task(data)
        return task
