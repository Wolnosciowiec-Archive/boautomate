
from typing import Union

from ...persistence import Pipeline
from ...exceptions import StorageException, ConfigurationException
from ..base import BaseHandler


class BasePipelineHandler(BaseHandler):
    def _get_secret(self):
        return self.request.arguments.get('secret', [b''])[0].decode('utf-8')

    def _get_pipeline(self, pipeline_id: str) -> Union[Pipeline, None]:
        try:
            pipeline = self.container.pipeline_repository.find_by_id(pipeline_id)

            if not pipeline:
                self.write_not_found_error()
                return

            if pipeline.secret != self._get_secret():
                self.write_no_access_error('Invalid secret code')
                return

            return pipeline

        except StorageException as e:
            self.write_not_found_error('"' + pipeline_id + '" not found on the storage. Details: ' + str(e))
            return

        except ConfigurationException as e:
            self.write_validation_error('Configuration error: ' + str(e))
            return