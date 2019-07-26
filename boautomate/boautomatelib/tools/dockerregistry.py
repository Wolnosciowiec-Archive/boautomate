
from ..exceptions import NoContextException
from ..payloadparser.facts import DockerRepositoryFact, DockerRegistryFact
from .lib.docker import DockerRegistryClient

"""
    Docker registry interaction support
    
    Example scenarios:
       - Pushing tags
       - Listing tags
"""


class Repository:
    """ Context of a image repository in a docker registry """

    _client: DockerRegistryClient
    _repository: str

    def __init__(self, client: DockerRegistryClient, repository: str):
        self._client = client
        self._repository = repository

    def tags(self):
        return self._client.list_tags(self._repository)

    def tag(self, name: str, origin_name: str):
        return self._client.tag(self._repository, origin_name, name)


class DockerRegistry:
    """ Basic docker registry client """

    _client: DockerRegistryClient
    _repository: Repository

    def __init__(self, registry_fact: DockerRegistryFact, repository_fact: DockerRepositoryFact = None):
        self._client = DockerRegistryClient(
            host=registry_fact.url,
            username=registry_fact.user if registry_fact.user else None,
            password=registry_fact.password if registry_fact.password else None
        )

        if repository_fact:
            self._repository = self.repository(repository_fact.repository_name)

    def current_repository(self):
        """
            Returns current contextual repository
            Possible case: When we receive a push notification to hub.docker.com, quay.io etc., then
                           we get a repository name that we can use
       """

        if not self._repository:
            raise NoContextException('Not in a context of a repository')

        return self._repository

    def repository(self, name: str):
        """ Gets any repository by name from the registry """

        return Repository(self._client, name)

