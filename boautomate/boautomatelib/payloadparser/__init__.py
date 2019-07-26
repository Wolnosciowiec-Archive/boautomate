
from .base import BaseParser, FactsCollection
from .quay import QuayParser
from .git import InternalGitFactsParser, InternalGitCredentialsParser
from .docker import DockerAuthorizationParser


class PayloadParser(BaseParser):
    _parsers = [
        QuayParser(),
        InternalGitFactsParser(),
        InternalGitCredentialsParser(),
        DockerAuthorizationParser()
    ]

    def can_handle(self, payload) -> bool:
        parser: BaseParser

        for parser in self._parsers:
            if parser.can_handle(payload):
                return True

        return False

    def what_is_going_on(self, payload) -> list:
        events = []
        parser: BaseParser

        for parser in self._parsers:
            if parser.can_handle(payload):
                events = events + parser.what_is_going_on(payload)

        return events

    def parse(self, payload) -> FactsCollection:
        parser: BaseParser
        facts = FactsCollection()

        for parser in self._parsers:
            if parser.can_handle(payload=payload):
                facts.merge(parser.parse(payload=payload))

        return facts
