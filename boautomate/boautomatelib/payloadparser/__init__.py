
from .baseparser import BaseParser, FactsCollection
from .quay import QuayParser


class PayloadParser(BaseParser):
    _parsers = [
        QuayParser
    ]

    def can_handle(self, payload: str) -> bool:
        parser: BaseParser

        for parser in self._parsers:
            if parser.can_handle(payload):
                return True

        return False

    def parse(self, payload: str) -> FactsCollection:
        parser: BaseParser

        for parser in self._parsers:
            if parser.can_handle(payload):
                return parser.parse(payload)

        return FactsCollection()
