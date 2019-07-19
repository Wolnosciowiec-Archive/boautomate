
from .persistence import ORM
from .locator import ScriptLocator
from .repository import PipelineRepository, ExecutionRepository
from .locator import LocatorFactory
from .executor import Executor, DockerRunExecutor
from sqlalchemy.orm.session import Session


class Container:
    """ Simple Inversion Of Control container """

    connection: ORM
    orm: Session  # type: Session
    locator: ScriptLocator
    pipeline_repository: PipelineRepository
    execution_repository: ExecutionRepository
    executor: Executor

    def __init__(self, params: dict):
        self.connection = ORM(params['db_string'])
        self.orm = self.connection.session
        self.locator = LocatorFactory().create(params['storage'])
        self.pipeline_repository = PipelineRepository(self.orm)
        self.execution_repository = ExecutionRepository(self.orm)
        self.executor = DockerRunExecutor(base_url=None, image=params['docker_image'])
