
from .facts import SlackUrlFact, FactsCollection
from .base import BaseParser


class InternalSlackUrlParser(BaseParser):
    def can_handle(self, payload) -> bool:
        return self._is_payload_fact_of_type(payload, 'Slack+WebhookUrl')

    def what_is_going_on(self, payload) -> list:
        return []

    def parse(self, payload) -> FactsCollection:
        fact = SlackUrlFact(url=payload['fact']['url'])

        return FactsCollection({fact.identify(): fact})

