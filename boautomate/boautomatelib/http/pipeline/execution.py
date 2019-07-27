
import typing
from . import BasePipelineHandler
from tornado.ioloop import IOLoop


class ExecutionHandler(BasePipelineHandler):  # pragma: no cover
    callback: typing.Callable

    async def get(self, pipeline_id: str):
        """
        List of all past and current executions of a Pipeline

        :param pipeline_id:
        :return:
        """

        pipeline = self._get_pipeline(pipeline_id)
        last_executions = self.container.execution_repository.find_last_executions(pipeline, limit=20)

        self.write({
            'last_execution_number': self.container.execution_repository.find_last_execution_number(pipeline),
            'executions': list(map(
                lambda execution: execution.to_summary_dict(),
                last_executions
            ))
        })

    async def post(self, pipeline_id: str):
        """
        Performs an Execution of a Pipeline

        :param pipeline_id:
        :return:
        """
        await IOLoop.current().run_in_executor(None, self._post, pipeline_id)

    def _post(self, pipeline_id: str):
        pipeline = self._get_pipeline(pipeline_id)
        script = pipeline.retrieve_script()

        execution = self.container.execution_repository.create(
            pipeline=pipeline,
            ip_address=self.request.remote_ip,
            payload=self.request.body.decode('utf-8'),
            log=''
        )
        self.container.execution_repository.flush(execution)

        run = self.container.supervisor.execute(
            execution=execution,
            script=script,
            payload=self.request.body.decode('utf-8'),
            communication_token='test-token',  # @todo: Token generator and token management
            query=self._get_serializable_query_arguments(),
            headers=dict(self.request.headers.get_all()),
            configuration_payloads=pipeline.get_configuration_payloads()
        )

        execution.mark_as_finished(run.is_success(), run.output)
        self.container.execution_repository.flush(execution)

        self.write(execution.log)
