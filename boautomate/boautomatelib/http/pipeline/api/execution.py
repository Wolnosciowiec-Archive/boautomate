

from ..execution import ExecutionHandler
from ....persistence import Pipeline


def route_execute(context_pipeline_id: str, pipeline_to_execute_id: str) -> str:
    return '/pipeline/%s/api/execute-other?pipeline_id=%s' % (context_pipeline_id, pipeline_to_execute_id)


class ExecutionFromOtherPipeline(ExecutionHandler):

    async def post(self, pipeline_id: str):
        """
        Validates permissions against "pipeline_id", but executes a Pipeline by query string param "pipeline_id"

        ---
        tags: ['pipeline/api/execution']
        summary: Execute a pipeline
        description: Starts a new Pipeline execution. Exactly in same way as in the regular endpoint.
          The difference between this API endpoint and regular endpoint is, that this endpoint is validating Token
          instead of Pipeline's secret.
        produces: ['application/json']
        parameters:
            - name: pipeline_id
              in: path
              description: Name/ID of a context Pipeline the API token is associated to
              required: true
              type: string

            - name: pipeline_id
              in: query
              description: Name/ID of a Pipeline to execute
              required: true
              type: string

            - name: Token
              in: header
              description: Authentication token
              required: true
              type: string
        responses:
            200:
                description: Log from the execution
            400:
                description: When the fields are not correct, or the Pipeline is locked from execution
                schema:
                    $ref: '#/definitions/RequestError'
            403:
                description: When Token does not match, or any general authentication error
                schema:
                    $ref: '#/definitions/RequestError'
            404:
                description: When pipeline or one of its files are missing
                schema:
                    $ref: '#/definitions/RequestError'
            500:
                description: On server error
                schema:
                    $ref: '#/definitions/ServerError'

        :param pipeline_id:
        :return:
        """

        self.assert_has_access_to_internal_api(pipeline_id)

        if not self.request.query_arguments.get('pipeline_id'):
            self.raise_validation_error('Missing argument "%s" in query string' % 'pipeline_id')

        await super().post(self.request.query_arguments.get('pipeline_id')[0].decode('utf-8'))

    def get(self, pipeline_id: str):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    def options(self):
        pass

    def assert_has_access(self, pipeline: Pipeline):
        """ Makes the "code" parameter not required, later we will validate the Token """

        pass
