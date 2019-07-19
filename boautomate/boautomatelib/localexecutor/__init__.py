
import os
import json


class LocalExecutor:
    _payload: str
    _token: str
    _query: dict
    _headers: dict

    def __init__(self):
        self._payload = os.getenv('PAYLOAD', '{}')
        self._token = os.getenv('COMMUNICATION_TOKEN', '')
        self._query = json.loads(os.getenv('HTTP_QUERY', '{}'))
        self._headers = json.loads(os.getenv('HTTP_HEADERS', '{}'))

    def get_query_argument(self, arg: str, default = None):
        return self._query.get(arg) if arg in self._query else default

    def get_header(self, arg: str, default = None):
        return self._headers.get(arg) if arg in self._headers else default

    def get_build_number(self):
        return os.getenv('BUILD_NUMBER', 1)
