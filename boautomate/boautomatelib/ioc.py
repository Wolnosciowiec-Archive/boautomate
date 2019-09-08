
from sqlalchemy.orm.session import Session

from .persistence import ORM
from .filesystem import Filesystem
from .filesystem.factory import FSFactory
from .filesystem.templating import Templating
from .repository import PipelineRepository, ExecutionRepository, TokenRepository, LocksRepository
from .supervisor import Supervisor
from .supervisor.factory import SupervisorFactory
from .tokenmanager import TokenManager
from .locks import LocksManager
from .resolver import Resolver
from .logger import Logger


class Container:
    """
        Simple Inversion Of Control container

        In other words: Application context, contains ready-to-use core objects
    """

    connection: ORM
    orm: Session  # type: Session
    fs_factory: FSFactory
    filesystem: Filesystem
    fs_tpl: Templating
    pipeline_repository: PipelineRepository
    execution_repository: ExecutionRepository
    lock_repository: LocksRepository
    token_repository: TokenRepository
    token_manager: TokenManager
    supervisor: Supervisor
    self_url: str
    local_path: str
    resolver: Resolver
    supervisor_factory: SupervisorFactory

    def __init__(self, params: dict):
        Logger.debug('Initializing the IoC container')

        self.resolver = Resolver(params)
        self.local_path = params['local_path']

        # http
        self.self_url = params['node_master_url']

        # database related
        self.connection = ORM(params['db_string'])
        self.orm = self.connection.session
        self.execution_repository = ExecutionRepository(self.orm)
        self.token_repository = TokenRepository(orm=self.orm)
        self.lock_repository = LocksRepository(orm=self.orm)
        self.token_manager = TokenManager(repository=self.token_repository)

        # filesystem related
        self.fs_factory = FSFactory(self.resolver)
        self.filesystem = self.fs_factory.create()
        self.fs_tpl = Templating(self.filesystem, self.fs_factory)
        self.pipeline_repository = PipelineRepository(self.filesystem, self.fs_tpl)

        self.locks_manager = LocksManager(repository=self.lock_repository, fs_templating=self.fs_tpl)

        # supervisors related
        self.supervisor_factory = SupervisorFactory(self.resolver, self.self_url, self.pipeline_repository)
        self.supervisor = self.supervisor_factory.create()
