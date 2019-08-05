

class Resolver:
    """ Resolves params """

    _params: dict

    def __init__(self, params: dict):
        self._params = params

    def resolve_string(self, string: str):
        for key, value in self._params.items():
            string = string.replace('%' + key + '%', str(value))

        return string

    def get(self, param_name: str):
        if param_name in self._params:
            return self.resolve_string(self._params[param_name])

        return None

