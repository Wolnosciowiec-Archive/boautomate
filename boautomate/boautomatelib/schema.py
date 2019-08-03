
import os
from json import loads as json_loads, JSONDecodeError
from jsonschema import validate


class Schema:
    @staticmethod
    def load(name: str):
        path = Schema._get_schema_dir() + '/schema/' + name + '.schema.json'

        if not os.path.isfile(path):
            raise Exception('Cannot find schema "%s"' % name)

        with open(path, 'rb') as f:
            return dict(json_loads(f.read()))

    @staticmethod
    def validate_payload(payload: str, schema_name: str):
        # @todo: Regexp validation
        validate(instance=Schema.parse_json(payload), schema=Schema.load(schema_name))

    @staticmethod
    def parse_json(payload: str):
        try:
            parsed = dict(json_loads(payload.encode('utf-8')))
        except JSONDecodeError:
            parsed = {}

        return parsed

    @staticmethod
    def _get_schema_dir():
        return os.path.dirname(os.path.abspath(__file__))
