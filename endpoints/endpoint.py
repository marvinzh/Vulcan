import json
import logging
from typing import Generator
from enum import Enum, unique, auto
from workflow import WorkflowInstance
from fastapi import Request, FastAPI
from fastapi.responses import StreamingResponse
from endpoints.models import TextRequest


@unique
class EndpointType(Enum):
    SYNC = auto()
    STREAM = auto()


class Endpoint:
    def __init__(self, endpoint_config: dict, wfi: WorkflowInstance = None) -> None:
        self.load_config(endpoint_config, wfi)

    def load_config(self, endpoint_config: dict, wfi: WorkflowInstance = None) -> None:
        self.path = endpoint_config.get("path")
        self.wfi = wfi

    def set_runnable(self):
        raise NotImplementedError()

    def run_workflow(self, request: Request) -> dict:
        raise NotImplementedError()

    def wrap_response(self, response: dict) -> dict:
        final_output = response.get("final_output")
        data = {"content": final_output, "additional_kwargs": response, "type": "ai"}
        logging.info(f"endpoint response: {json.dumps(data)}")
        return data

    def handle(self, input: TextRequest, request: Request) -> dict:
        self.set_runnable()
        vars = self.run_workflow(input)
        response = self.wrap_response(vars)
        return response

    def bind(self, app: FastAPI):
        app.add_api_route(self.path, self.handle, methods=["POST"])

    @staticmethod
    def create(endpoint_config: dict, wfi: WorkflowInstance = None):
        endpoint_type = endpoint_config.get("type")
        if endpoint_type == "sync":
            return SyncEndpoint(endpoint_config, wfi)
        elif endpoint_type == "stream":
            return StreamEndpoint(endpoint_config, wfi)
        else:
            raise ValueError(f"Invalid endpoint type: {endpoint_type}")


class SyncEndpoint(Endpoint):
    def __init__(self, endpoint_config: dict, wfi: WorkflowInstance = None) -> None:
        super().__init__(endpoint_config, wfi)
        self.endpoint_type = EndpointType.SYNC

    def set_runnable(self):
        self.runnable = self.wfi.execute

    def run_workflow(self, request: Request) -> dict:
        input_json = json.loads(request.json())
        global_variables = self.runnable(input_json)
        return global_variables


class StreamEndpoint(Endpoint):
    def __init__(self, endpoint_config: dict, wfi: WorkflowInstance = None) -> None:
        super().__init__(endpoint_config, wfi)
        self.endpoint_type = EndpointType.STREAM

    def set_runnable(self):
        self.runnable = self.wfi.execute_as_stream

    def run_workflow(self, request: Request) -> Generator:
        input_json = json.loads(request.json())
        for global_variables in self.runnable(input_json):
            yield self.wrap_response(global_variables)

    def wrap_response(self, response: dict):
        data = super().wrap_response(response)
        data["is_stream"] = True
        return json.dumps(data)

    def handle(self, input: TextRequest, request: Request):
        self.set_runnable()
        return StreamingResponse(
            self.run_workflow(input), media_type="application/json"
        )
