
import os

from . import Filesystem, StorageSpec
from ..exceptions import StorageException
from ..logging import Logger


class LocalFilesystem(Filesystem):
    path: str

    def __init__(self, params: dict, spec: StorageSpec):
        self.spec = spec

        if not 'path' in params:
            raise StorageException('Cannot construct LocalFilesystem, missing "path" in params')

        self.path = params.get('path')

    def file_exists(self, name: str) -> bool:
        return os.path.isfile(self.path + '/' + name)

    def add_file(self, name: str, content: str) -> bool:
        f = open(self.path + '/' + name, 'wb')
        f.write(content.encode('utf-8'))
        f.close()

        return self.retrieve_file(self.path + '/' + name) == content

    def retrieve_file(self, name: str) -> str:
        Logger.debug('fs.retrieve_file(' + name + ')')

        if not self.file_exists(name):
            raise StorageException(('File "%s" does not exist. ' +
                                   'Check if it exists, and if a valid filesystem was selected') % name)

        f = open(self.path + '/' + name, 'rb')
        content = f.read()
        f.close()

        return content.decode('utf-8')
