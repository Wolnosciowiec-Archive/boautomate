
import json
import typing
from .base import BaseHandler


class MainHandler(BaseHandler):  # pragma: no cover
    callback: typing.Callable

    def get(self):
        """
        ---
        tags:
        - Home
        summary: Landing page
        description: Just a landing page
        produces:
        - application/json
        responses:
            200:
              description: Hello message
        :return:
        """

        self.add_header('Content-Type', 'application/json')
        self.write(
            json.dumps("Hello from snake world.", sort_keys=True, indent=4, separators=(',', ': '))
        )
