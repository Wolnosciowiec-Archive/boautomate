
import os
import re
from typing import Pattern

from .exceptions import ConfigurationException


class Resolver:
    """ Resolves params """

    _params: dict
    _param_pattern: Pattern
    _env_pattern: Pattern

    def __init__(self, params: dict):
        self._params = params
        self._param_pattern = re.compile('%([A-Za-z0-9-_.]+)%')
        self._env_pattern = re.compile('\${([A-Za-z0-9-_.]+)}')

    def resolve_string(self, string: str):
        # shell parameters (normalized by argsparse) ex. --this-is-a-test into "this_is_a_test"
        for key, value in self._params.items():
            string = string.replace('%' + key + '%', str(value))

        # environment variables
        for key, value in dict(os.environ).items():
            string = string.replace('${%s}' % key, str(value))

        invalid_params = self._param_pattern.findall(string)
        invalid_envs = self._env_pattern.findall(string)

        if invalid_params:
            raise ConfigurationException('Cannot resolve string "%s", undefined parameters: %s' %
                                         (string, str(invalid_params)))

        if invalid_envs:
            raise ConfigurationException('Cannot resolve string "%s", undefined environment variables: %s' %
                                         (string, str(invalid_envs)))

        return string

    def get(self, param_name: str):
        if param_name in self._params:
            return self.resolve_string(self._params[param_name])

        return None

