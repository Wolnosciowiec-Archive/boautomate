
import tornado.ioloop
import tornado.web
import threading
import asyncio

from .index import MainHandler
from .pipeline.execution import ExecutionHandler
from .pipeline.declaration import DeclarationHandler
from .pipeline.env import EnvHandler
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

    # def run(self, container: Container):
    #     self._thread = threading.Thread(target=lambda: self._run())
    #     self._thread.setDaemon(True)
    #     self._thread.start()

    def run(self, container: Container):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        handlers = [
            (r"" + self._path_prefix + "/", MainHandler),
            (r"" + self._path_prefix + "/pipeline/([a-z0-9-]+)/declaration", DeclarationHandler),
            (r"" + self._path_prefix + "/pipeline/([a-z0-9-]+)/environment", EnvHandler),
            (r"" + self._path_prefix + "/pipeline/([a-z0-9-]+)", ExecutionHandler)
        ]

        for handler in handlers:
            handler[1].inject_container(container)

        srv = tornado.web.Application(handlers)
        srv.listen(self._port, self._address)
        loop.run_forever()
