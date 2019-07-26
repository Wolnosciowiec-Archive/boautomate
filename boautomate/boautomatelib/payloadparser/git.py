
from .base import BaseParser
from .facts import GitFact, GitCredentialsFact, FactsCollection

"""
    {
        "fact": {
            "type": "Git+Credentials",
            "remote": "git@github.com:riotkit-org/boautomate.git",
            "branch": "master",
            "user": "my-user",
            "password": "hello",
            "public_key": "ssh-rsa ......"
        }
    }
"""


class InternalGitFactsParser(BaseParser):
    def can_handle(self, payload) -> bool:
        return type(payload) == dict \
            and 'fact' in payload and 'type' in payload['fact'] \
            and payload['fact']['type'] == 'Git+Credentials'

    def parse(self, payload) -> FactsCollection:
        git_fact = GitFact(
            remote=payload['fact']['remote'],
            branch=payload['fact']['branch']
        )

        return FactsCollection({git_fact.identify(): git_fact})

    def what_is_going_on(self, payload) -> list:
        return []


class InternalGitCredentialsParser(InternalGitFactsParser):
    def parse(self, payload) -> FactsCollection:
        cred_fact = GitCredentialsFact(
            user=payload['fact'].get('user', ''),
            password=payload['fact'].get('password', ''),
            public_key=payload['fact'].get('public_key', '')
        )

        return FactsCollection({cred_fact.identify(): cred_fact})
