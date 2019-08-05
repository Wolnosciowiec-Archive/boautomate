# -*- coding: utf-8 -*-

from .ioc import Container
from .persistence import ORM
from .http import HttpServer
from .repository import PipelineRepository
from .logging import setup_logger, Logger


class Boautomate:
    container: Container
    http: HttpServer

    def __init__(self, params: dict):
        setup_logger(params['log_path'], params['log_level'])
        self.container = Container(params)
        self.http = HttpServer(params['http_address'], params['http_port'], params['http_prefix'])

    def main(self):
        self.http.run(self.container)
        pass
