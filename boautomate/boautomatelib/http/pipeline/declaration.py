
from json import loads as json_loads

from . import BasePipelineHandler


class DeclarationHandler(BasePipelineHandler):  # pragma: no cover
    async def get(self, pipeline_id: str):
        pipeline = self._get_pipeline(pipeline_id)
        self.write({
            'id': pipeline.id,
            'script': pipeline.retrieve_script(),
            'configs': json_loads(pipeline.configs)
        })
