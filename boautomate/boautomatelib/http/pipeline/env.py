
from . import BasePipelineHandler


class EnvHandler(BasePipelineHandler):  # pragma: no cover
    """
    Developer-friendly controller that returns part of a command for manual execution on worker NodeExecutor
    """

    async def post(self, pipeline_id: str):
        pipeline = self._get_pipeline(pipeline_id)
        if not pipeline:
            return

        self.write(self.container.supervisor.env_to_string(
            self.container.supervisor.prepare_environment(
                execution=self.container.execution_repository.create(pipeline, '0.0.0.0', '', ''),
                payload=self.request.body.decode('utf-8'),
                communication_token='test-token',  # @todo: Token generator and token management
                query=self._get_serializable_query_arguments(),
                headers=dict(self.request.headers.get_all()),
                configuration_payloads=pipeline.get_configuration_payloads()
            )
        ))
