
import re
from git import Repo as GitRepo

from . import Filesystem, StorageSpec


class GitFilesystem(Filesystem):
    """
    GitFS allows to use GIT as a storage to keep ex. pipeline configuration, scripts

    Example:
    git://git@github.com:riotkit-org/boautomate.git;passphrase=test;branch=master;key=./key

    spec = git@github.com:riotkit-org/boautomate.git
    params = {
        passphrase: test,
        branch: master,
        key: ./key
    }

    :param Filesystem:
    :return:
    """

    repository: str
    branch: str
    user: str
    passphrase: str
    key: str
    _repo: GitRepo

    # static variable  @todo: Parametrize
    reposPath = '/var/lib/boautomate/git/%s'

    def __init__(self, params: dict, spec: StorageSpec):
        self.spec = spec
        print('git')
        # self._repo = GitRepo(path=self._get_constant_path(spec))
        # self._repo.clone(spec, branch=params.get('branch', 'master'))

    def _get_constant_path(self, spec: str):
        return self.reposPath % self._normalize_repo_name(spec)

    def file_exists(self, name: str) -> bool:
        pass

    def add_file(self, name: str, content: str) -> bool:
        pass

    def retrieve_file(self, name: str) -> str:
        pass

    def _normalize_repo_name(self, spec: str):
        return re.sub('[^a-zA-Z_-]+', '', spec)

