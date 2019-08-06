
import re
import os
import git

from . import Filesystem, StorageSpec
from ..resolver import Resolver
from ..exceptions import StorageException


class GitFilesystem(Filesystem):
    """
    GitFS allows to use GIT as a storage to keep ex. pipeline configuration, scripts

    :param Filesystem:
    :return:
    """

    repository: str
    branch: str
    user: str
    passphrase: str
    key: str

    _repo: git.Repo
    repositories_path: str

    def __init__(self, spec: StorageSpec, resolver: Resolver):
        self._prepare_local_path(resolver)
        self.spec = spec
        self._repo = git.Repo()
        self._branch = self.spec.params.get('branch', 'master')

        try:
            self._repo.clone(self._get_constant_path(spec.params.get('url')), branch=self._branch)

        except git.exc.GitCommandError as err:
            if "already exists and is not an empty directory" in str(err):
                self._do_checkout()
            else:
                raise

        self._repo.remote('origin').pull(self._branch)

    def _do_checkout(self):
        try:
            branch = self._repo.heads[self._branch]
            branch.checkout()
        except IndexError as e:
            raise StorageException('Branch "%s" not found, %s' % (self._branch, str(e)))

    def _get_constant_path(self, spec: str):
        repo_path = self.repositories_path + '/' + self._normalize_repo_name(spec) + '/'

        if not os.path.isdir(repo_path):
            os.mkdir(repo_path)

        return repo_path

    def file_exists(self, name: str) -> bool:
        pass

    def add_file(self, name: str, content: str) -> bool:
        pass

    def retrieve_file(self, name: str) -> str:
        pass

    def _normalize_repo_name(self, url: str):
        repo_name = url.replace('@', '_at_') \
            .replace('/', '-') \
            .replace(':', '-')

        return re.sub('[^a-zA-Z_\-.]+', '', repo_name)

    def _prepare_local_path(self, resolver: Resolver):
        self.repositories_path = resolver.resolve_string('%local_path%/git')

        if not os.path.isdir(self.repositories_path):
            os.mkdir(self.repositories_path)

