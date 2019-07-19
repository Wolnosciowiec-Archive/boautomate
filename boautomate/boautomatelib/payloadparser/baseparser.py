

class BaseParser:
    def can_handle(self, payload: str) -> bool:
        pass

    def parse(self, payload: str):
        pass


class FactsCollection:
    pass


class ParsedFact:
    pass

