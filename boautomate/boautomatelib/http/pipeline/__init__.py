
from typing import Union

from ...persistence import Pipeline
from ...exceptions import EntityNotFound
from ...exceptions import StorageException, ConfigurationException
from ..base import BaseHandler


class BasePipelineHandler(BaseHandler):
    def _get_secret(self):
        return self.request.arguments.get('secret', [b''])[0].decode('utf-8')

    def _get_pipeline(self, pipeline_id: str) -> Union[Pipeline, None]:
        try:
            pipeline = self.container.pipeline_repository.find_by_id(pipeline_id)

            if not pipeline:
                self.raise_not_found_error()
                raise

            return pipeline

        except StorageException as e:
            self.raise_not_found_error('"' + pipeline_id + '" not found on the storage, or one of its files. ' +
                                       'Details: ' + str(e))

        except ConfigurationException as e:
            self.raise_validation_error('Configuration error: ' + str(e))

    def assert_has_access(self, pipeline: Pipeline):
        if pipeline.secret != self._get_secret():
            self.write_no_access_error('Invalid secret code')
            raise Exception('Invalid secret code')

    def assert_payload_not_blocked(self, pipeline: Pipeline, payload: str):
        if self.container.locks_manager.is_payload_blocked_by_any_lock_on_pipeline(pipeline, payload):
            self.raise_validation_error('Pipeline cannot be started with this payload, it was locked')

    def assert_has_access_to_internal_api(self, pipeline_id: str):
        try:
            token = self.container.token_manager.get(str(self.request.headers.get('Token')))
        except EntityNotFound:
            token = None

        if not token or token.pipeline_id != pipeline_id:
            self.write_no_access_error('Token is missing or current token is not in scope of requested pipeline')
            raise Exception('Token not found')
