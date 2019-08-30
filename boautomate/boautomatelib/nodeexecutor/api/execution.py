
import sys
from requests import Response

from ...http.pipeline.api.execution import route_execute
from ...exceptions import PipelineSyntaxError
from . import Api


this = sys.modules[__name__]


class ExecutionOfAnyPipelineApi:
    _api: Api
    _context_pipeline_id: str

    def __init__(self, api: Api, _context_pipeline_id: str):
        self._api = api
        self._context_pipeline_id = _context_pipeline_id

    def execute(self, pipeline_to_execute_id: str, payload: str) -> Response:
        response = self._api.post(route_execute(self._context_pipeline_id, pipeline_to_execute_id), data=payload)

        if response.status_code > 299:
            raise PipelineSyntaxError('Pipeline trigger ended wih HTTP(%i): %s' % (response.status_code, response.text))

        return response


def setup_pipeline_api(api: Api, context_pipeline_id: str):
    this.api = ExecutionOfAnyPipelineApi(api, context_pipeline_id)


def pipeline(name: str, payload: str = ''):
    return this.api.execute(pipeline_to_execute_id=name, payload=payload).text
