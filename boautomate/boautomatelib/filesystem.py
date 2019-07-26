
import abc
import os
from .exceptions import StorageException


class Filesystem(abc.ABC):
    """ Filesystem proxy """

    @abc.abstractmethod
    def retrieve_file(self, name: str) -> str:
        pass

    @abc.abstractmethod
    def file_exists(self, name: str) -> bool:
        pass

    @abc.abstractmethod
    def add_file(self, name: str, content: str) -> bool:
        pass


class LocalFilesystem(Filesystem):
    path: str

    def __init__(self, path: str):
        self.path = path

    def file_exists(self, name: str) -> bool:
        return os.path.isfile(self.path + '/' + name)

    def add_file(self, name: str, content: str) -> bool:
        f = open(self.path + '/' + name, 'wb')
        f.write(content.encode('utf-8'))
        f.close()

        return self.retrieve_file(self.path + '/' + name) == content

    def retrieve_file(self, name: str) -> str:
        if not self.file_exists(name):
            raise StorageException('File does not exist')

        f = open(self.path + '/' + name, 'rb')
        content = f.read()
        f.close()

        return content.decode('utf-8')


class MultipleFilesystemAdapter(Filesystem):
    adapters: list
    primary: Filesystem

    def __init__(self, adapters: list, primary: Filesystem):
        self.adapters = adapters
        self.primary = primary

    def retrieve_file(self, name: str) -> str:
        for adapter in self.adapters:
            if adapter.file_exists(name):
                return adapter.retrieve_file(name)

        raise StorageException('File not found by any configured storage (--storage option)')

    def file_exists(self, name: str) -> bool:
        for adapter in self.adapters:
            if adapter.file_exists(name):
                return True

        return False

    def add_file(self, name: str, content: str) -> bool:
        return self.primary.add_file(name, content)


class FSFactory:
    mapping = {
        '': LocalFilesystem,
        'file': LocalFilesystem
    }

    def create(self, storagespecs: list) -> MultipleFilesystemAdapter:
        adapters = [
            self._create_adapter('file://' + self._get_local_scripts_location())
        ]

        for spec in storagespecs:
            adapters.append(self._create_adapter(spec))

        return MultipleFilesystemAdapter(adapters, adapters[1])

    def _create_adapter(self, spec: str) -> Filesystem:
        split = spec.split('://')
        mapping_type = split[0] if len(split) > 1 else 'file'
        details = split[1] if len(split) > 1 else split[0]

        if mapping_type not in self.mapping:
            raise Exception('Unknown storage type "' + mapping_type + '"')

        return self.mapping[mapping_type](details)

    def _get_local_scripts_location(self) -> str:
        return os.path.dirname(os.path.abspath(__file__)) + '/../scripts/'

