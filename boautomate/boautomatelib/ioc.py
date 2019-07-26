
from .persistence import ORM
from .filesystem import Filesystem, FSFactory
from .repository import PipelineRepository, ExecutionRepository
from .supervisor import Supervisor, DockerRunSupervisor
from sqlalchemy.orm.session import Session


class Container:
    """
        Simple Inversion Of Control container

        In other words: Application context, contains ready-to-use core objects
    """

    connection: ORM
    orm: Session  # type: Session
    filesystem: Filesystem
    pipeline_repository: PipelineRepository
    execution_repository: ExecutionRepository
    supervisor: Supervisor

    def __init__(self, params: dict):
        self.connection = ORM(params['db_string'])
        self.orm = self.connection.session
        self.filesystem = FSFactory().create(params['storage'])
        self.pipeline_repository = PipelineRepository(self.orm)
        self.execution_repository = ExecutionRepository(self.orm)
        self.supervisor = DockerRunSupervisor(base_url=None, image=params['docker_image'])
