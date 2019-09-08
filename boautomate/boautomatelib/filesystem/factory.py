
"""
    Filesystem Factory
    ==================

    Creates adapters, wraps them into MultipleFilesystemAdapter
"""

import os
import typing

from .localfs import LocalFilesystem
from .gitfs import GitFilesystem
from .multiplefs import MultipleFilesystemAdapter
from . import StorageSpec, Filesystem
from ..logger import Logger
from ..schema import Schema
from ..exceptions import StorageException, SchemaNotFoundError
from ..resolver import Resolver


class FSFactory:
    _annotation_regexp: typing.Pattern
    _storage_config_path: str
    _resolver: Resolver

    mapping = {
        '': LocalFilesystem,
        'local': LocalFilesystem,
        'git': GitFilesystem
    }

    constructed: dict

    def __init__(self, resolver: Resolver):
        self.constructed = {}
        self._storage_config_path = resolver.get('storage')
        self._resolver = resolver

    def create(self) -> MultipleFilesystemAdapter:
        storage_specs = self._parse(self._storage_config_path)

        adapters = [
            self._create_adapter(
                StorageSpec(name='boautomate-local', type='local', default=True, params={
                    'path': self._get_local_boautomate_location(),
                })
            )
        ]

        for name, spec in storage_specs.items():
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

        # @todo: Add support for pluggable filesystem adapters

        instance = self.mapping[spec.type](spec, self._resolver)
        self.constructed[spec.name] = instance

        Logger.debug('Initialized filesystem under name "%s"' % spec.name)

        return instance

    def _get_local_boautomate_location(self) -> str:
        return os.path.dirname(os.path.abspath(__file__)) + '/../../'

    def _parse(self, storage_config_file: str):
        """
        Parse configuration file (default: storage.yaml)

        :param storage_config_file:
        :return:
        """

        if not os.path.isfile(storage_config_file):
            raise StorageException('Configuration file "%s" does not exist' % storage_config_file)

        with open(storage_config_file, 'rb') as f:
            fs_config = Schema.parse_yaml_with_validation(f.read().decode('utf-8'), 'config/storage')

            for name, spec_as_dict in fs_config.items():
                try:
                    Schema.validate_parsed_payload(spec_as_dict['params'],
                                                   'config/filesystems/%s.fs' % spec_as_dict['type'])
                except SchemaNotFoundError:
                    Logger.warning('Schema validation for filesystem "%s" not found' % spec_as_dict['type'])
                    continue
                # @todo: Add schema exception catching with adding a proper message and converting it into storage exception

            return fs_config
