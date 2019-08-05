
import abc
import os
import re
import typing
from collections import namedtuple
from git import Repo as GitRepo
from ..exceptions import StorageException
from ..logging import Logger
from ..schema import Schema


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


class GitFilesystem(Filesystem):
    """
    GitFS allows to use GIT as a storage to keep ex. pipeline configuration, scripts

    Example:
    git://git@github.com:riotkit-org/boautomate.git;passphrase=test;branch=master;key=./key

    spec = git@github.com:riotkit-org/boautomate.git
    params = {
        passphrase: test,
        branch: master,
        key: ./key
    }

    :param Filesystem:
    :return:
    """

    repository: str
    branch: str
    user: str
    passphrase: str
    key: str
    _repo: GitRepo

    # static variable  @todo: Parametrize
    reposPath = '/var/lib/boautomate/git/%s'

    def __init__(self, params: dict, spec: StorageSpec):
        self.spec = spec
        print('git')
        # self._repo = GitRepo(path=self._get_constant_path(spec))
        # self._repo.clone(spec, branch=params.get('branch', 'master'))

    def _get_constant_path(self, spec: str):
        return self.reposPath % self._normalize_repo_name(spec)

    def file_exists(self, name: str) -> bool:
        pass

    def add_file(self, name: str, content: str) -> bool:
        pass

    def retrieve_file(self, name: str) -> str:
        pass

    def _normalize_repo_name(self, spec: str):
        return re.sub('[^a-zA-Z_-]+', '', spec)


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


class MultipleFilesystemAdapter(Filesystem):
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


class FSFactory:
    _annotation_regexp: typing.Pattern
    _storage_config_path: str

    mapping = {
        '': LocalFilesystem,
        'local': LocalFilesystem,
        'git': GitFilesystem
    }

    constructed: dict

    def __init__(self, _storage_config_path: str):
        self.constructed = {}
        self._storage_config_path = _storage_config_path

    def create(self) -> MultipleFilesystemAdapter:
        storagespecs = self._parse(self._storage_config_path)

        adapters = [
            self._create_adapter(
                StorageSpec(name='boautomate-local', type='local', default=True, params={
                    'path': self._get_local_boautomate_location(),
                })
            )
        ]

        for name, spec in storagespecs.items():
            spec['name'] = name

            try:
                adapters.append(self._create_adapter(StorageSpec(**spec)))
            except TypeError as err:
                hint = ''

                if 'got an unexpected keyword argument' in str(err):
                    hint = '. Possibly you added a recognized field in storage adapter configuration'

                raise StorageException('Cannot create adapter "%s", got error: %s %s' % (
                    name, str(err), hint
                ))

        return MultipleFilesystemAdapter(adapters, adapters[1])

    def get(self, adapter_name: str) -> Filesystem:
        """ Get already constructed storage """

        if adapter_name in self.constructed:
            Logger.debug('fs.get returned existing instance of fs for "%s"' % adapter_name)
            return self.constructed[adapter_name]

        raise StorageException('Filesystem needs to be defined, "%s" is undefined' % adapter_name)

    def _create_adapter(self, spec: StorageSpec) -> Filesystem:
        Logger.info('FSFactory is creating adapter from spec=%s' % str(spec))

        if spec.type not in self.mapping:
            raise StorageException('Unknown storage type or name: "' + spec.type + '"')

        instance = self.mapping[spec.type](spec.params, spec)
        self.constructed[spec.name] = instance

        Logger.debug('Initialized filesystem under name "%s"' % spec.name)

        return instance

    def _get_local_boautomate_location(self) -> str:
        return os.path.dirname(os.path.abspath(__file__)) + '/../'

    def _parse(self, storage_config_file: str):
        """
        Parse configuration file (default: storage.yaml)

        :param storage_config_file:
        :return:
        """

        if not os.path.isfile(storage_config_file):
            raise StorageException('Configuration file "%s" does not exist' % storage_config_file)

        with open(storage_config_file, 'rb') as f:
            return Schema.parse_yaml_with_validation(f.read().decode('utf-8'), 'config/storage')


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
                    '@storedOnFilesystem\(([A-Za-z.0-9\-_+/,:;()%!$@\[\]{}?<> ]+)\).atPath\(([A-Za-z.0-9\-_+/,:;()%!$ ]+)\)',
                    re.IGNORECASE),
                callback=self._stored_on_filesystem
            )
        ]

        for syntax in syntax_list:
            while syntax.name in content:
                Logger.debug('Templating.inject_includes() is matching %s' % syntax.name)
                match = syntax.regexp.match(content)

                if not match:
                    raise Exception('Logic error, marker "%s" found, but regexp failed to parse it' % syntax.name)

                Logger.debug('fs.Templating injecting template ' + str(match.groups()))
                content = content.replace(match.string, syntax.callback(match))

        return content

    def _stored_at_path(self, match: typing.Match):
        return self.fs.retrieve_file(match.group(1))

    def _stored_on_filesystem(self, match: typing.Match):
        return self.fs_factory.get(match.group(1)).retrieve_file(match.group(2))
