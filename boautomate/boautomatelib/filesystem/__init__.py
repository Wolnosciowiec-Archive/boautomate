
import abc
from collections import namedtuple


StorageSpec = namedtuple('StorageSpec', 'name type params default')
Syntax = namedtuple('Syntax', "regexp name callback")


class Filesystem(abc.ABC):
    """ Filesystem proxy """

    SCRIPTS_PATH = 'scripts'
    PIPELINES_PATH = 'pipelines'

    spec: StorageSpec

    def get_specification(self) -> StorageSpec:
        return self.spec

    def is_default(self) -> bool:
        return self.spec.default is True

    @abc.abstractmethod
    def retrieve_file(self, name: str) -> str:
        pass

    @abc.abstractmethod
    def file_exists(self, name: str) -> bool:
        pass

    @abc.abstractmethod
    def add_file(self, name: str, content: str) -> bool:
        pass

