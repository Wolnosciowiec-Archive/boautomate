
from abc import ABC
from typing import Optional, Awaitable

import json
import tornado.web
from ..ioc import Container


class BaseHandler(tornado.web.RequestHandler, ABC):
    container = None  # type: Container

    @staticmethod
    def inject_container(container: Container):
        BaseHandler.container = container

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def writeNotFoundError(self, msg: str = 'Not found') -> None:
        self.write(json.dumps({'error': msg, 'type': 'no_access'}))
        self.set_status(404)

    def writeNoAccessError(self, msg: str) -> None:
        self.write(json.dumps({'error': msg, 'type': 'not_found'}))
        self.set_status(403)

    def _get_serializable_query_arguments(self):
        output = dict()

        for query_param, values in self.request.query_arguments.items():
            str_values = []

            for value in values:
                str_values.append(value.decode('utf-8'))

            output[query_param] = str_values

        return output
