
from .persistence import Pipeline, Execution, Token, Lock
from .filesystem import Filesystem
from .filesystem.templating import Templating
from .pipelineparser import PipelineParser
from .exceptions import EntityNotFound
from sqlalchemy.orm.session import Session
from sqlalchemy import func, desc
from sqlalchemy.orm.exc import NoResultFound as ORMNoResultFound
from uuid import uuid4
import datetime


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
        execution.execution_number = int(self.find_last_execution_number(pipeline)) + 1

        return execution

    def flush(self, execution: Execution):
        self.orm.add(execution)
        self.orm.flush([execution])

    def find_last_executions(self, pipeline: Pipeline, limit: int):
        return self.orm.query(Execution)\
            .filter(Execution.pipeline_id == pipeline.id) \
            .order_by(desc(Execution.id)) \
            .limit(limit)\
            .all()

    def find_last_execution_number(self, pipeline: Pipeline):
        last_num = self.orm.query(func.max(Execution.execution_number)).filter(Execution.pipeline_id == pipeline.id)\
            .scalar()

        if not last_num:
            last_num = 0

        return last_num


class TokenRepository(BaseRepository):
    def create(self, pipeline: Pipeline, execution: Execution):
        token = Token()
        token.id = str(uuid4())
        token.pipeline_id = pipeline.id
        token.execution_id = execution.id
        token.execution = execution
        token.active = True
        token.expires_at = datetime.datetime.now() + datetime.timedelta(hours=2)

        return token

    def flush(self, token: Token):
        self.orm.add(token)
        self.orm.flush([token])

    def find_by_id(self, id: str) -> Token:
        try:
            return self.orm.query(Token)\
                .filter(Token.id == id) \
                .limit(1)\
                .one()
        except ORMNoResultFound:
            raise EntityNotFound('No token found by id=%s' % id)


class LocksRepository(BaseRepository):
    def create(self, lock_id: str, pipeline_id: str, expiration: datetime.datetime = None):
        if not expiration:
            expiration = datetime.datetime.now() + datetime.timedelta(hours=2)

        lock = Lock()
        lock.id = lock_id
        lock.pipeline_id = pipeline_id
        lock.expires_at = expiration

        return lock

    def find_all(self) -> list:
        return self.orm.query(Lock).all()

    def find_by(self, lock_id: str, pipeline_id: str) -> Lock:
        try:
            return self.orm.query(Lock) \
                .filter(Lock.pipeline_id == pipeline_id and Lock.id == lock_id) \
                .limit(1) \
                .one()
        except ORMNoResultFound:
            raise EntityNotFound('Lock not found')

    def delete(self, lock: Lock):
        self.orm.delete(lock)
        self.orm.flush([lock])

    def flush(self, lock: Lock):
        self.orm.add(lock)
        self.orm.flush([lock])
