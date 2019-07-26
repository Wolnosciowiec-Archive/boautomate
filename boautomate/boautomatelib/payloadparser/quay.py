
from .base import BaseParser
from .facts import DockerRepositoryFact, FactsCollection
from .actions import *

"""
    Quay.io push event parser

    {
        "name": "repository",
        "repository": "mynamespace/repository",
        "namespace": "mynamespace",
        "docker_url": "quay.io/mynamespace/repository",
        "homepage": "https://quay.io/repository/mynamespace/repository",
        "updated_tags": [
            "latest"
        ]
    }
"""


class QuayParser(BaseParser):
    def can_handle(self, payload) -> bool:
        return type(payload) == dict \
            and "name" in payload and payload['name'] == 'repository' \
            and "updated_tags" in payload

    def what_is_going_on(self, payload) -> list:
        return [ACTION_DOCKER_PUSH]

    def parse(self, payload) -> FactsCollection:
        registry_fact = DockerRepositoryFact(
            url=payload['docker_url'],
            repository_name=payload['repository'],
            updated_tags=payload['updated_tags']
        )

        return FactsCollection({
            registry_fact.identify(): registry_fact
        })

