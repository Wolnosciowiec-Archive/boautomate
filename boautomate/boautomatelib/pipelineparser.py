
import json
from .exceptions import ConfigurationException, SchemaValidationException
from .persistence import Pipeline
from .schema import Schema


class PipelineParser:
    @staticmethod
    def parse(id: str, content: str) -> Pipeline:
        parsed = json.loads(content.encode('utf-8'))

        try:
            Schema.validate_parsed_payload(parsed, parsed.get('schema', ''))

        except SchemaValidationException as validation_error:
            raise ConfigurationException('Pipeline configuration error, details: ' + str(validation_error)) \
                from validation_error

        pipe = Pipeline()
        pipe.id = id
        pipe.script = parsed['script']
        pipe.secret = parsed['secret']
        pipe.supervisor_label = parsed.get('supervisor_label', '')
        pipe.configs = parsed['configs']
        pipe.title = parsed['title']
        pipe.params = parsed['params']

        return pipe
