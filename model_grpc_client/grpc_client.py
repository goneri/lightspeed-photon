# pylint: disable-all
import logging
from dataclasses import dataclass
from typing import Any

import grpc
import yaml

from .exceptions import ModelTimeoutError
from .grpc_pb import common_service_pb2, common_service_pb2_grpc

logger = logging.getLogger(__name__)


prediction_t = dict["str", list[str]]


@dataclass
class GrpcPayload:
    context: str = ""
    prompt: str = ""


task_t = dict[str, Any]


def unwrap_grpc_prediction(prompt: str, data: str) -> task_t:
    """Unwrap a given response to dict."""
    first_prediction = prompt + "\n" + data
    try:
        tasks: list[task_t] = yaml.safe_load(first_prediction)
    except yaml.YAMLError:
        logger.debug(f"CANNOT LOAD YAML:\n{first_prediction}")
        raise
    return tasks[0]


class GrpcClient:
    def __init__(self, inference_url: str):
        self._inference_url = inference_url
        self._inference_stub = self.get_inference_stub()

    def get_inference_stub(self) -> common_service_pb2_grpc.WisdomExtServiceStub:
        logger.debug("Inference URL: " + self._inference_url)
        channel = grpc.insecure_channel(self._inference_url)
        stub = common_service_pb2_grpc.WisdomExtServiceStub(channel)  # type: ignore # noqa: PGH003
        logger.debug("Inference Stub: " + str(stub))
        return stub

    def infer(self, payload: GrpcPayload, model_name: str) -> task_t:
        request = common_service_pb2.AnsibleRequest(prompt=payload.prompt, context=payload.context)  # type: ignore # noqa: PGH003,E501
        try:
            response = self._inference_stub.AnsiblePredict(
                request=request,
                metadata=[("mm-vmodel-id", model_name)],
                timeout=60,
            )

            logger.debug(f"inference response: {response}")
            logger.debug(f"inference response: {response.text}")
            data = response.text
        except grpc.RpcError as exc:
            if exc.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                raise ModelTimeoutError from None
            else:
                logger.exception("gRPC client error")
                raise
        return unwrap_grpc_prediction(payload.prompt, data)
