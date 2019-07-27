
import abc
import os
import re
import tornado.log
import typing
from collections import namedtuple
from .exceptions import StorageException


class Filesystem(abc.ABC):
    """ Filesystem proxy """

    SCRIPTS_PATH = 'scripts'
    PIPELINES_PATH = 'pipelines'

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
        tornado.log.app_log.error('fs.retrieve_file(' + name + ')')

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

        raise StorageException('File "%s" not found by any configured storage (--storage option)' % name)

    def file_exists(self, name: str) -> bool:
        for adapter in self.adapters:
            if adapter.file_exists(name):
                return True

        return False

    def add_file(self, name: str, content: str) -> bool:
        return self.primary.add_file(name, content)


class FSFactory:
    _annotation_regexp: typing.Pattern

    mapping = {
        '': LocalFilesystem,
        'file': LocalFilesystem
    }

    constructed: dict

    def __init__(self):
        self.constructed = {}
        self._annotation_regexp = re.compile('@([a-zA-Z-0-9_]+)\((.*)\)')

    def create(self, storagespecs: list) -> MultipleFilesystemAdapter:
        adapters = [
            self._create_adapter('file://' + self._get_local_scripts_location())
        ]

        for spec in storagespecs:
            adapters.append(self._create_adapter(spec))

        return MultipleFilesystemAdapter(adapters, adapters[1])

    def get(self, adapter_id_or_spec: str) -> Filesystem:
        """ Get already constructed storage """

        if adapter_id_or_spec in self.constructed:
            return self.constructed[adapter_id_or_spec]

        return self._create_adapter(adapter_id_or_spec)

    def _create_adapter(self, spec: str) -> Filesystem:
        named_adapter = self._annotation_regexp.match(spec)
        name = spec

        if named_adapter:
            name = named_adapter.group(1)
            spec = named_adapter.group(2)

        split = spec.split('://')
        mapping_type = split[0] if len(split) > 1 else 'file'
        details = split[1] if len(split) > 1 else split[0]

        if mapping_type not in self.mapping:
            raise StorageException('Unknown storage type or name: "' + mapping_type + '"')

        instance = self.mapping[mapping_type](details)
        self.constructed[name] = instance

        return instance

    def _get_local_scripts_location(self) -> str:
        return os.path.dirname(os.path.abspath(__file__)) + '/../scripts/'


Syntax = namedtuple('Syntax', "regexp name callback")


class Templating:
    fs: Filesystem
    fs_factory: FSFactory

    def __init__(self, fs: Filesystem, fs_factory: FSFactory):
        self.fs = fs
        self.fs_factory = fs_factory

    def inject_includes(self, content: str):
        """
            Injects file contents in place of, example:
              - @storedAtPath(boautomate/hello-world.py)
              - @storedAtFilesystem(file://./test/example-installation/configs/hello-world.conf.json)

            Works recursively, until the syntax occurs in the content.
        """

        syntax_list = [
            Syntax(
                name="@storedAtPath",
                regexp=re.compile('@storedAtPath\(([A-Za-z.0-9\-_+/,:;()%!$ ]+)\)', re.IGNORECASE),
                callback=self._stored_at_path
            ),

            Syntax(
                name="@storedOnFilesystem",
                regexp=re.compile(
                    '@storedOnFilesystem\(([A-Za-z.0-9\-_+/,:;()%!$ ]+)\).atPath\(([A-Za-z.0-9\-_+/,:;()%!$ ]+)\)',
                    re.IGNORECASE),
                callback=self._stored_on_filesystem
            )
        ]

        for syntax in syntax_list:
            while syntax.name in content:
                match = syntax.regexp.match(content)

                if not match:
                    raise Exception('Logic error, marker "%s" found, but regexp failed to parse it' % syntax.name)

                tornado.log.app_log.debug('fs.Templating injecting template ' + str(match.groups()))
                content = content.replace(match.string, syntax.callback(match))

        return content

    def _stored_at_path(self, match: typing.Match):
        return self.fs.retrieve_file(match.group(1))

    def _stored_on_filesystem(self, match: typing.Match):
        return self.fs_factory.get(match.group(1)).retrieve_file(match.group(2))
