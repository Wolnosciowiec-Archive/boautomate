
from sqlalchemy.orm.session import Session
from .persistence import Pipeline, Execution
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func


class BaseRepository:
    orm: Session

    def __init__(self, orm: Session):
        self.orm = orm


class PipelineRepository(BaseRepository):
    def find_by_id(self, pipeline_id: str) -> Pipeline:
        try:
            return self.orm.query(Pipeline).filter(Pipeline.id == pipeline_id).one()

        except NoResultFound:
            return


class ExecutionRepository(BaseRepository):
    def create(self, pipeline: Pipeline, ip_address: str, payload: str, log: str) -> Execution:
        execution = Execution()
        execution.pipeline = pipeline
        execution.pipeline_id = pipeline.id
        execution.invoked_by_ip = ip_address
        execution.payload = payload
        execution.log = log
        execution.execution_number = int(self.find_last_build_number(pipeline)) + 1

        print(self.find_last_build_number(pipeline))

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
