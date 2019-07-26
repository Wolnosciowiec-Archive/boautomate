
import abc
from .facts import FactsCollection


class BaseParser(abc.ABC):
    @abc.abstractmethod
    def can_handle(self, payload) -> bool:
        pass

    @abc.abstractmethod
    def what_is_going_on(self, payload) -> list:
        pass

    @abc.abstractmethod
    def parse(self, payload) -> FactsCollection:
        pass

    def _is_payload_fact_of_type(self, payload, fact_type: str):
        return type(payload) == dict \
               and 'fact' in payload and 'type' in payload['fact'] \
               and payload['fact']['type'] == fact_type

