
from .persistence import Pipeline, Execution
from .filesystem import Filesystem, Templating
from .pipelineparser import PipelineParser
from sqlalchemy.orm.session import Session
from sqlalchemy import func


class BaseRepository:
    orm: Session

    def __init__(self, orm: Session):
        self.orm = orm


class PipelineRepository:
    fs: Filesystem
    fs_tpl: Templating

    def __init__(self, fs: Filesystem, fs_tpl: Templating):
        self.fs = fs
        self.fs_tpl = fs_tpl

    def find_by_id(self, pipeline_id: str) -> Pipeline:
        """ Find a Pipeline by it's id (filename without extension) """

        return self._read_pipeline(
            id=pipeline_id,
            content=self.fs.retrieve_file(Filesystem.PIPELINES_PATH + '/' + pipeline_id + '.json')
        )

    def _read_pipeline(self, id: str, content: str) -> Pipeline:
        """ Create a Pipeline object from file content """

        pipeline = PipelineParser.parse(id, content)
        pipeline.configs = self.fs_tpl.inject_includes(pipeline.configs)
        pipeline.retrieve_script = lambda: self.fs_tpl.inject_includes(pipeline.script)

        return pipeline


class ExecutionRepository(BaseRepository):
    """ Each Pipeline execution is recorded there """

    def create(self, pipeline: Pipeline, ip_address: str, payload: str, log: str) -> Execution:
        execution = Execution()
        execution.pipeline_id = pipeline.id
        execution.invoked_by_ip = ip_address
        execution.payload = payload
        execution.log = log
        execution.execution_number = int(self.find_last_build_number(pipeline)) + 1

        return execution

    def flush(self, execution: Execution):
        self.orm.add(execution)
        self.orm.flush([execution])

    def find_last_build_number(self, pipeline: Pipeline):
        last_num = self.orm.query(func.max(Execution.execution_number)).filter(Execution.pipeline_id == pipeline.id)\
            .scalar()

        if not last_num:
            last_num = 0

        return last_num
