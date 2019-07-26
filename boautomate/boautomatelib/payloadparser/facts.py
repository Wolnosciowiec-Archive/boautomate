
from collections import UserDict
import abc


class ParsedFact(abc.ABC):
    @classmethod
    def identify(cls) -> str:
        return cls.__name__


class FactsCollection(UserDict):
    def merge(self, other):
        v: ParsedFact

        for k, v in other.items():
            self.__setitem__(v.identify(), v)

    def describe(self):
        return ", ".join(
            map(lambda fact: fact, dict(self))
        )

class GitFact(ParsedFact):
    remote: str
    branch: str

    def __init__(self, remote: str, branch: str):
        self.remote = remote
        self.branch = branch


class DockerRepositoryFact(ParsedFact):
    url: str
    repository_name: str
    updated_tags: list

    def __init__(self, url: str, repository_name: str, updated_tags: list):
        self.url = url
        self.repository_name = repository_name
        self.updated_tags = updated_tags


class DockerRegistryFact(ParsedFact):
    url: str
    user: str
    password: str
    auth_service_url: str

    def __init__(self, url: str, user: str, password: str, auth_service_url: str = None):
        self.url = url
        self.user = user
        self.password = password
        self.auth_service_url = auth_service_url if auth_service_url else None


class GitCredentialsFact(ParsedFact):
    user: str
    password: str
    public_key: str

    def __init__(self, user: str, password: str, public_key: str):
        self.user = user
        self.password = password
        self.public_key = public_key
