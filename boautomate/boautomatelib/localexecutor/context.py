
import json
from ..payloadparser.facts import FactsCollection
from ..payloadparser import PayloadParser
from ..payloadparser.facts import DockerRegistryFact, DockerRepositoryFact
from ..exceptions import ScriptExpectationsNotMetException
from ..tools.dockerregistry import DockerRegistry


class ExecutionContext:
    what_is_going_on: list
    facts: FactsCollection
    parser: PayloadParser
    _tools: {}

    def __init__(self, trigger_payload: str, configuration: list):
        """
        :param trigger_payload: RAW HTTP payload
        :param configuration: List of decoded dicts from JSON
        """

        self._tools = {}
        self.parser = PayloadParser()
        self.facts = FactsCollection()
        self._prepare_trigger_payload(trigger_payload)
        self.facts.merge(self._to_configuration_facts(configuration))

    def get_fact(self, fact_type: str, default: any = any) -> any:
        if fact_type not in self.facts:
            if default != any:
                return default

            raise ScriptExpectationsNotMetException('Expected "' + fact_type + '" fact, '
                                                    'current input does not produce it')

        return self.facts[fact_type]

    def docker_registry(self) -> DockerRegistry:
        return self._lazy_get(
            'docker_registry',
            lambda: DockerRegistry(
                self.get_fact(DockerRegistryFact.identify()),
                self.get_fact(DockerRepositoryFact.identify(), None)
            )
        )

    def _lazy_get(self, store_as: str, func: callable):
        if store_as not in self._tools:
            self._tools[store_as] = func()

        return self._tools[store_as]

    def _prepare_trigger_payload(self, trigger_payload: str):
        decoded = self._try_to_decode(trigger_payload)
        self.facts.merge(self.parser.parse(decoded))
        self.what_is_going_on = self.parser.what_is_going_on(decoded)

    def _to_configuration_facts(self, payloads: list):
        facts = FactsCollection()

        for payload in payloads:
            decoded = self._try_to_decode(payload)
            parsed_into_facts = self.parser.parse(decoded)

            facts.merge(parsed_into_facts)

        return facts

    def _try_to_decode(self, payload):
        try:
            return json.loads(payload)
        except:
            return payload
