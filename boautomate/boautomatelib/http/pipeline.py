
import typing
from ..exceptions import StorageException, ConfigurationException
from .base import BaseHandler


class PipelineHandler(BaseHandler):  # pragma: no cover
    callback: typing.Callable

    def _get_secret(self):
        return self.request.arguments.get('secret', [b''])[0].decode('utf-8')

    async def post(self, pipeline_id: str):
        try:
            pipeline = self.container.pipeline_repository.find_by_id(pipeline_id)

            if not pipeline:
                self.write_not_found_error()
                return

            if pipeline.secret != self._get_secret():
                self.write_no_access_error('Invalid secret code')
                return

            script = pipeline.retrieve_script()

        except StorageException as e:
            self.write_not_found_error('File "' + pipeline.script + '" not found in the storage. Details: ' + str(e))
            return

        except ConfigurationException as e:
            self.write_validation_error('Configuration error: ' + str(e))
            return

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
            communication_token='test-token', #  @todo: Token generator and token management
            query=self._get_serializable_query_arguments(),
            headers=dict(self.request.headers.get_all()),
            configuration_payloads=pipeline.get_configuration_payloads()
        )

        execution.mark_as_finished(run.is_success(), run.output)
        self.container.execution_repository.flush(execution)

        self.write(execution.log)
