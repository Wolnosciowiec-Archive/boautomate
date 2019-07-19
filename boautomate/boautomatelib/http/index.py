
import json
import typing
from .base import BaseHandler


class MainHandler(BaseHandler):  # pragma: no cover
    callback: typing.Callable

    def get(self):
        self.add_header('Content-Type', 'application/json')
        self.write(
            json.dumps("Hello from snake world.", sort_keys=True, indent=4, separators=(',', ': '))
        )
