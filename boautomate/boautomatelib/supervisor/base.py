import abc
import json
import os
from collections import namedtuple
from tzlocal import get_localzone

from ..persistence import Execution


class ExecutionResult:
    output: str
    exit_code: int

    def __init__(self, output: str, exit_code: int):
        self.output = output
        self.exit_code = exit_code

    def is_success(self) -> bool:
        return self.exit_code == 0


class Supervisor(abc.ABC):
    _master_url: str

    def __init__(self, master_url: str):
        self._master_url = master_url

    @abc.abstractmethod
    def execute(self, execution: Execution, script: str, payload: str, communication_token: str,
                query: dict, headers: dict, configuration_payloads: list, params: dict) -> ExecutionResult:
        pass

    def prepare_environment(self, payload: str,
                            communication_token: str,
                            query: dict,
                            headers: dict,
                            configuration_payloads: list,
                            execution: Execution,
                            params: dict):
        return {
            'TRIGGER_PAYLOAD': payload,
            'CONFIG_PAYLOADS': json.dumps(configuration_payloads),
            'COMMUNICATION_TOKEN': communication_token,
            'HTTP_QUERY': json.dumps(query),
            'PARAMS': json.dumps(params),
            'HTTP_HEADERS': json.dumps(headers),
            'BUILD_NUMBER': str(execution.execution_number),
            'MASTER_BASE_URL': self._master_url,
            'PIPELINE_ID': str(execution.pipeline_id),
            'TZ': Supervisor.get_timezone()
        }

    @staticmethod
    def get_timezone():
        return get_localzone().zone

    @staticmethod
    def env_to_string(env: dict) -> str:
        env_as_str = ''

        for key, value in env.items():
            env_as_str += ' ' + key + '="' + str(value).replace('"', '\\"') + '"'

        return env_as_str.replace("\n", ' ')

    @staticmethod
    def _get_boautomate_path():
        return os.path.dirname(os.path.abspath(__file__)) + '/../../../'


SupervisorDefinition = namedtuple('SupervisorDefinition', 'default labels supervisor name')
Settings = namedtuple('Settings', 'selection_strategy')
