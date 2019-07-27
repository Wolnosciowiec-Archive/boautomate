
import json
import jsonschema
import os
from .exceptions import ConfigurationException
from .persistence import Pipeline


class PipelineParser:
    @staticmethod
    def parse(id: str, content: str) -> Pipeline:
        parsed = json.loads(content.encode('utf-8'))

        try:
            jsonschema.validate(instance=parsed,
                                schema=PipelineParser.get_schema(parsed['schema'] if 'schema' in parsed else ''))
        except jsonschema.exceptions.ValidationError as validation_error:
            raise ConfigurationException('Pipeline configuration error, details: ' + str(validation_error)) \
                from validation_error

        pipe = Pipeline()
        pipe.id = id
        pipe.script = parsed['script']
        pipe.secret = parsed['secret']
        pipe.configs = parsed['configs']
        pipe.title = parsed['title']

        return pipe

    @staticmethod
    def get_schema(version: str) -> dict:
        try:
            with open(os.path.dirname(os.path.abspath(__file__)) + '/schema/' + version + '.schema.json') as f:
                return json.loads(f.read())

        except FileNotFoundError as fnf_error:
            raise ConfigurationException('Invalid schema provided in field "schema". Parent error: ' + str(fnf_error)) \
                from fnf_error
