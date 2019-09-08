
from typing import Dict

from ..resolver import Resolver
from ..schema import Schema
from ..repository import PipelineRepository
from ..plugin import PluginUtils
from .base import SupervisorDefinition, Settings, Supervisor
from .dockerrun import DockerRunSupervisor
from .native import NativeRunSupervisor
from .multiple import MultipleSupervisor


class SupervisorFactory:
    """
        Parses configuration file, and creates all Supervisor at once
    """

    MAPPING = {
        'native': NativeRunSupervisor,
        'docker-run': DockerRunSupervisor
    }

    _settings: Settings
    _supervisors: Dict[str, SupervisorDefinition]
    _master_url: str
    _pipe_repository: PipelineRepository

    def __init__(self, resolver: Resolver, master_url: str, pipe_repository: PipelineRepository):
        self._config_path = resolver.get('local_path') + '/supervisor.yaml'
        self._master_url = master_url
        self._pipe_repository = pipe_repository
        self._supervisors = {}
        self._parse_config()

    def _parse_config(self):
        with open(self._config_path, 'rb') as f:
            to_dict = Schema.parse_yaml_with_validation(f.read().decode('utf-8'), 'config/supervisor')

        self._settings = Settings(**to_dict['settings'])

        for name, attributes in to_dict['nodes'].items():
            supervisor_type = attributes['type']

            self._supervisors[name] = SupervisorDefinition(
                default=attributes['default'],
                labels=attributes['labels'],
                name=name,
                supervisor=self._create_supervisor(supervisor_type, attributes['attributes'])
            )

    def _create_supervisor(self, type_name: str, attributes: dict) -> Supervisor:
        if type_name not in self.MAPPING:
            imported = PluginUtils.import_class_if_is_a_class(type_name)

            if imported:
                return imported(master_url=self._master_url, **attributes)

            raise Exception('"%s" is not recognized supervisor type' % type_name)

        return self.MAPPING[type_name](master_url=self._master_url, **attributes)

    def create(self) -> Supervisor:
        return MultipleSupervisor(
            master_url=self._master_url,
            children=list(self._supervisors.values()),
            settings=self._settings,
            repository=self._pipe_repository
        )
