# -*- coding: utf-8 -*-

from .ioc import Container
from .persistence import ORM
from .http import HttpServer
from .filesystem import FSFactory
from .repository import PipelineRepository
import logging


class Boautomate:
    container: Container
    http: HttpServer

    def __init__(self, params: dict):
        self.container = Container(params)
        self.http = HttpServer(params['http_address'], params['http_port'], params['http_prefix'])

        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    def main(self):
        self.http.run(self.container)
        pass
