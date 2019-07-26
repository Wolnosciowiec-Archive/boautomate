
from .base import BaseParser
from .facts import FactsCollection, DockerRegistryFact


class DockerAuthorizationParser(BaseParser):
    """
        Parses configuration that produces a fact allowing to connect to a Docker Registry
    """

    def what_is_going_on(self, payload) -> list:
        return []

    def can_handle(self, payload) -> bool:
        return self._is_payload_fact_of_type(payload, 'DockerAuthorization')

    def parse(self, payload) -> FactsCollection:
        fact = DockerRegistryFact(
            url=payload['fact']['url'],
            user=payload['fact']['username'],
            password=payload['fact']['password']
        )

        return FactsCollection({fact.identify(): fact})
