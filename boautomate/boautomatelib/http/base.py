
from abc import ABC
from typing import Optional, Awaitable

import json
import tornado.log
import tornado.web
import traceback
from typing import Any, Union
from ..ioc import Container


class BaseHandler(ABC, tornado.web.RequestHandler):
    container = None  # type: Container

    @staticmethod
    def inject_container(container: Container):
        BaseHandler.container = container

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def write_not_found_error(self, msg: str = 'Not found') -> None:
        tornado.log.app_log.error(msg)
        self.write(json.dumps({'error': msg, 'type': 'no_access'}))
        self.set_status(404)

    def write_validation_error(self, msg: str = 'Configuration error'):
        tornado.log.app_log.error(msg)
        self.write(json.dumps({'error': msg, 'type': 'validation_error'}))
        self.set_status(400)

    def write_no_access_error(self, msg: str) -> None:
        self.write(json.dumps({'error': msg, 'type': 'not_found'}))
        self.set_status(403)

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        details = []

        if "exc_info" in kwargs:
            details = traceback.format_exception(*kwargs["exc_info"])

        self.set_status(status_code)
        self.finish({
            'error': "Server error",
            'status': status_code,
            'type': 'server_error',
            'details': details}
        )


    def _get_serializable_query_arguments(self):
        output = dict()

        for query_param, values in self.request.query_arguments.items():
            str_values = []

            for value in values:
                str_values.append(value.decode('utf-8'))

            output[query_param] = str_values

        return output

    def write(self, chunk: Union[str, bytes, dict]) -> None:
        if type(chunk) == dict:
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            chunk = json.dumps(chunk, indent=4, sort_keys=True)

        return super().write(chunk)
