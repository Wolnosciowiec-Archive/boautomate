# -*- coding: utf-8 -*-

from .ioc import Container
from .persistence import ORM
from .http import HttpServer
from .locator import LocatorFactory
from .repository import PipelineRepository


class Boautomate:
    container: Container
    http: HttpServer

    def __init__(self, params: dict):
        self.container = Container(params)
        self.http = HttpServer(params['http_address'], params['http_port'], params['http_prefix'])

    def main(self):
        self.http.run(self.container)
        pass
