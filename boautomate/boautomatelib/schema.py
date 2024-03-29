
import os
from json import loads as json_loads, JSONDecodeError
from yaml import load as yaml_load, FullLoader as YamlFullLoader
from jsonschema import validate
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

from .exceptions import SchemaNotFoundError, SchemaValidationException


class Schema:
    """
    Parses and validates configuration schemas, input payloads
    """

    @staticmethod
    def load(name: str):
        path = Schema._get_schema_dir() + '/schema/' + name + '.schema.json'

        if not os.path.isfile(path):
            raise SchemaNotFoundError('Cannot find schema "%s"' % name)

        with open(path, 'rb') as f:
            return dict(json_loads(f.read()))

    @staticmethod
    def validate_json_payload(payload: str, schema_name: str):
        Schema.validate_parsed_payload(Schema.parse_json(payload), schema_name)

    @staticmethod
    def validate_parsed_payload(parsed_payload, schema_name: str):
        return Schema.validate(parsed_payload, Schema.load(schema_name))

    @staticmethod
    def validate(payload, schema):
        try:
            validate(instance=payload, schema=schema)

        except JsonSchemaValidationError as e:
            raise SchemaValidationException(str(e.message))

    @staticmethod
    def parse_json(payload: str):
        try:
            return dict(json_loads(payload.encode('utf-8')))
        except JSONDecodeError:
            return {}

    @staticmethod
    def parse_yaml(payload: str):
        return yaml_load(payload, YamlFullLoader)

    @staticmethod
    def parse_yaml_with_validation(payload: str, schema_name: str):
        parsed = Schema.parse_yaml(payload)
        Schema.validate_parsed_payload(parsed, schema_name)

        return parsed

    @staticmethod
    def parse_json_with_validation(payload: str, schema_name: str):
        parsed = Schema.parse_json(payload)
        Schema.validate_parsed_payload(parsed, schema_name)

        return parsed

    @staticmethod
    def _get_schema_dir():
        return os.path.dirname(os.path.abspath(__file__))
