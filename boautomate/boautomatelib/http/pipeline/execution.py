
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

        self.assert_has_access(pipeline)
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

        ---
        tags: ['pipeline']
        summary: Execute a pipeline
        description: Starts a pipeline execution. Takes any payload eg. a github webhook payload, or any custom one.
           Designed to work with external services like GOGS, Github, Gitlab, Docker Registry, Quay.io and others.
           The payload is parsed into FACTS. The facts can be read, or used by tools like git, docker registry client
           and by other tools.
        produces: ['application/json']
        parameters:
            - name: pipeline_id
              in: path
              description: Name/ID of a pipeline
              required: true
              type: string

            - name: secret
              in: query
              description: Secret key for a pipeline (a passphrase to be able to run the pipeline)
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
                description: When secret code does not match, or any general authentication error
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
        """
        await IOLoop.current().run_in_executor(None, self._post, pipeline_id)

    def _post(self, pipeline_id: str):
        pipeline = self._get_pipeline(pipeline_id)

        self.assert_has_access(pipeline)
        self.assert_payload_not_blocked(pipeline, self.request.body.decode('utf-8'))

        script = pipeline.retrieve_script()

        # mark that we are "in-progress"
        execution = self.container.execution_repository.create(
            pipeline=pipeline,
            ip_address=self.request.remote_ip,
            payload=self.request.body.decode('utf-8'),
            log=''
        )
        self.container.execution_repository.flush(execution)
        get_token = self.container.token_manager.transaction

        # execute the script
        with get_token(pipeline, execution) as token:
            run = self.container.supervisor.execute(
                execution=execution,
                script=script,
                payload=self.request.body.decode('utf-8'),
                communication_token=token,
                query=self._get_serializable_query_arguments(),
                headers=dict(self.request.headers.get_all()),
                configuration_payloads=pipeline.get_configuration_payloads(),
                params=pipeline.params
            )

        # finish
        execution.mark_as_finished(run.is_success(), run.output)
        self.container.execution_repository.flush(execution)

        self.write(execution.log)
