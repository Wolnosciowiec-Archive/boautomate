
from . import Filesystem
from ..exceptions import StorageException
from ..logging import Logger


class MultipleFilesystemAdapter(Filesystem):
    """
    Adapter that contains other adapters and finds file on first one that contains the file
    """

    adapters: list
    primary: Filesystem

    def __init__(self, adapters: list, primary: Filesystem):
        self.adapters = adapters
        self.primary = primary

    def retrieve_file(self, name: str) -> str:
        for adapter in self.adapters:
            if adapter.is_default() and adapter.file_exists(name):
                return adapter.retrieve_file(name)

            Logger.debug('"%s" file does not exist in fs=%s' % (name, str(adapter)))

        raise StorageException('File "%s" not found by any configured storage (--storage option)' % name)

    def file_exists(self, name: str) -> bool:
        for adapter in self.adapters:
            if adapter.file_exists(name):
                return True

        return False

    def add_file(self, name: str, content: str) -> bool:
        return self.primary.add_file(name, content)
