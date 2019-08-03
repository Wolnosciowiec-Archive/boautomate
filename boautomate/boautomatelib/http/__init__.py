
import tornado.ioloop
import tornado.web
import threading
import asyncio
from tornado_swagger.setup import setup_swagger

from .index import MainHandler
from .pipeline.execution import ExecutionHandler
from .pipeline.declaration import DeclarationHandler
from .pipeline.env import EnvHandler
from .pipeline.api.locks import LocksHandler
from .pipeline.api.locks_list import LocksListHandler
from ..ioc import Container


class HttpServer:  # pragma: no cover
    _port: int
    _path_prefix: str
    _address: str
    _thread: threading.Thread

    def __init__(self, address: str, port: int, server_path_prefix: str):
        self._port = port
        self._address = address
        self._path_prefix = server_path_prefix

    def run(self, container: Container):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        handlers = [
            (r"" + self._path_prefix + "/", MainHandler),
            (r"" + self._path_prefix + "/pipeline/([a-z0-9-]+)/declaration", DeclarationHandler),
            (r"" + self._path_prefix + "/pipeline/([a-z0-9-]+)/environment", EnvHandler),
            (r"" + self._path_prefix + "/pipeline/([a-z0-9-]+)/api/lock/([a-z0-9-_.]+)", LocksHandler),
            (r"" + self._path_prefix + "/pipeline/([a-z0-9-]+)/execute", ExecutionHandler),
            (r"" + self._path_prefix + "/lock/list", LocksListHandler)
        ]

        for handler in handlers:
            handler[1].inject_container(container)

        handlers = list(map(
            lambda handler: tornado.web.url(handler[0], handler[1]),
            handlers
        ))

        setup_swagger(handlers)

        srv = tornado.web.Application(handlers)
        srv.listen(self._port, self._address)
        loop.run_forever()
