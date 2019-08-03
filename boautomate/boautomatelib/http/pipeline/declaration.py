
from json import loads as json_loads
from . import BasePipelineHandler


class DeclarationHandler(BasePipelineHandler):  # pragma: no cover
    """
    DevOps/Developer-friendly controller that allows to preview the final pipeline code (already processed)
    """

    async def get(self, pipeline_id: str):
        pipeline = self._get_pipeline(pipeline_id)
        if not pipeline:
            return

        self.assert_has_access(pipeline)

        self.write({
            'id': pipeline.id,
            'script': pipeline.retrieve_script(),
            'configs': json_loads(pipeline.configs)
        })
