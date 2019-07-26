
import os
import json

from .context import ExecutionContext
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
    _ctx: ExecutionContext

    def __init__(self):
        self._payload = os.getenv('TRIGGER_PAYLOAD', '{}')
        self._config = json.loads(os.getenv('CONFIG_PAYLOADS', '[]'))
        self._token = os.getenv('COMMUNICATION_TOKEN', '')
        self._query = json.loads(os.getenv('HTTP_QUERY', '{}'))
        self._headers = json.loads(os.getenv('HTTP_HEADERS', '{}'))
        self._populate_context()

    def get_query_argument(self, arg: str, default = None):
        return self._query.get(arg) if arg in self._query else default

    def get_header(self, arg: str, default = None):
        return self._headers.get(arg) if arg in self._headers else default

    def get_build_number(self):
        return os.getenv('BUILD_NUMBER', 1)

    def _populate_context(self):
        self._ctx = ExecutionContext(self._payload, self._config)

    def context(self) -> ExecutionContext:
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
