
import os
import json

from .context import ExecutionContext
from .api import Api
from .api.locks import Locks
from ..exceptions import ScriptExpectationsNotMetException


class NodeExecutor:
    """
        Base class for each script launched on a node.
        Gives access to facts, repositories, parameters, api etc.
    """

    _payloads: list
    _token: str
    _query: dict
    _headers: dict
    _params: dict
    _ctx: ExecutionContext
    _api: Api
    locks: Locks

    def __init__(self):
        self._payload = os.getenv('TRIGGER_PAYLOAD', '{}')
        self._config = json.loads(os.getenv('CONFIG_PAYLOADS', '[]'))
        self._token = os.getenv('COMMUNICATION_TOKEN', '')
        self._query = json.loads(os.getenv('HTTP_QUERY', '{}'))
        self._headers = json.loads(os.getenv('HTTP_HEADERS', '{}'))
        self._params = json.loads(os.getenv('PARAMS', '{}'))
        self._populate_context()
        self._create_api_client()

    def get_query_argument(self, arg: str, default = None):
        """
        Returns a parameter from user's HTTP query string that started this Pipeline Execution

        Be careful! Escape this value, it comes from the user.

        :param arg:
        :param default:
        :return:
        """

        if arg in self._query:
            if len(self._query[arg]) == 1:
                return self._query[arg][0]

            return self._query.get(arg)

        return default

    def get_param(self, arg: str, default = None):
        """
        Returns parameter configured in the Pipeline definition

        :param arg:
        :param default:
        :return:
        """

        return self._params.get(arg) if arg in self._params else default

    def get_overridable_param(self, arg: str, default = None):
        """
        Parameter taken in order from:
          - QUERY STRING
          - PIPELINE PARAMS

        Be careful! Escape this value, it comes from the user.

        :param arg:
        :param default:
        :return:
        """

        if arg in self._query:
            return self.get_query_argument(arg)

        if arg in self._params:
            return self._params[arg]

        return default

    def get_header(self, arg: str, default = None):
        """
        Returns a HTTP header value from a request that triggered this Pipeline execution

        :param arg:
        :param default:
        :return:
        """

        return self._headers.get(arg) if arg in self._headers else default

    def get_build_number(self) -> int:
        """
        Build number of a Pipeline (Execution number)

        :return:
        """

        return int(os.getenv('BUILD_NUMBER', 1))

    def get_pipeline_id(self) -> str:
        """
        Pipeline name/id
        :return:
        """

        return os.getenv('PIPELINE_ID')

    def _create_api_client(self):
        self._api = Api(os.getenv('MASTER_BASE_URL', ''), self._token)
        self.locks = Locks(self._api, self.get_pipeline_id())

    def _populate_context(self):
        self._ctx = ExecutionContext(self._payload, self._config)

    def context(self) -> ExecutionContext:
        """
        Facts and tools context
        :return:
        """

        return self._ctx

    def assert_what_is_going_on_at_least_one_of(self, actions: list):
        matching = filter(
            lambda action: action in actions,
            self.context().what_is_going_on
        )

        if len(list(matching)) == 0:
            raise ScriptExpectationsNotMetException('The input data/payload does not met script action. Example: '
                                                    'The script is going to push a tag, but requires a git '
                                                    'repository push')

    def assert_facts_present(self, facts: list):
        present = self.context().facts.keys()

        for fact in facts:
            if fact not in present:
                raise ScriptExpectationsNotMetException('Expected "' + fact + '" to be met, have: ' +
                                                        str(self.context().facts.describe()))
