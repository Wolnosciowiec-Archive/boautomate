
import os

from . import Filesystem, StorageSpec
from ..exceptions import StorageException
from ..logging import Logger
from ..resolver import Resolver


class LocalFilesystem(Filesystem):
    path: str
    ro: bool

    def __init__(self, spec: StorageSpec, resolver: Resolver):
        self.spec = spec

        if not 'path' in spec.params:
            raise StorageException('Cannot construct LocalFilesystem, missing "path" in params')

        self.ro = bool(spec.params.get('readonly', False))
        self.path = spec.params.get('path')

    def file_exists(self, name: str) -> bool:
        return os.path.isfile(self.path + '/' + name)

    def add_file(self, name: str, content: str) -> bool:
        if self.ro:
            raise StorageException('Read-only filesystem')

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
