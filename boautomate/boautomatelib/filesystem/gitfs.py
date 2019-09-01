
import re
import os
import git
import threading
import time
import traceback
from hashlib import sha256
from git.exc import GitCommandError

from . import Filesystem, StorageSpec
from .localfs import LocalFilesystem
from ..resolver import Resolver
from ..logging import Logger


class GitFilesystem(LocalFilesystem):
    """
    GitFS allows to use GIT as a storage to keep ex. pipeline configuration, scripts
    It's a wrapper on a local filesystem.

    :param Filesystem:
    :return:
    """

    _git_repository: str
    _git_branch: str
    _git_passphrase: str
    _git_key: str
    _git_readonly: bool
    _git_chroot: str
    _git_pull_interval: int
    _git_repo_path: str

    _repo: git.Repo
    _git_repositories_path: str
    _pull_thread: threading.Thread

    def __init__(self, spec: StorageSpec, resolver: Resolver):
        self._prepare_local_path(resolver)
        self.spec = spec

        self._git_repository = spec.params.get('url')
        self._git_branch = self.spec.params.get('branch', 'master')
        self._git_key = os.path.expanduser(spec.params.get('key'))
        self._git_passphrase = spec.params.get('passphrase')
        self._git_readonly = spec.params.get('readonly', False)
        self._git_chroot = spec.params.get('chroot', '')
        self._git_pull_interval = spec.params.get('pull_interval', 60)

        self._git_repo_path = self._initialize_git_repository()

        # initialize local filesystem storage after cloning a remote repository
        super().__init__(
            StorageSpec(
                name=spec.name,
                type='localfs',
                params={
                    'path': (self._git_repo_path + '/' + self._git_chroot).rstrip('/'),
                    'readonly': self._git_readonly
                },
                default=spec.default
            ),
            resolver
        )

        self._schedule_git_pull()

    def _schedule_git_pull(self):
        Logger.info('Scheduling a git pull every %i seconds' % self._git_pull_interval)
        self._pull_thread = threading.Thread(target=self._pull_thread_main)
        self._pull_thread.start()

    def _pull_thread_main(self):
        while True:
            Logger.debug('Pulling branch "%s" for filesystem at "%s"' % (self._git_branch, self._git_repo_path))

            try:
                self._repo.remote('origin').pull(self._git_branch)
            except Exception:
                Logger.info(traceback.format_exc())

            time.sleep(self._git_pull_interval)

    def _initialize_git_repository(self):
        """ Initialize the repository directory """

        self._repo = git.Repo()
        self._repo.git.update_environment(GIT_SSH_COMMAND=self._build_ssh_command())

        repo_path = self._get_constant_path(self.spec.params.get('url'))
        Logger.info('Cloning into "%s"' % repo_path)

        try:
            os.mkdir(repo_path)
        except FileExistsError:
            pass

        self._repo.init(repo_path)
        self._repo.git._working_dir = repo_path

        try:
            origin = self._repo.create_remote('origin', self.spec.params.get('url'))
        except GitCommandError:
            Logger.info('Remote already exists, not recreating')
            origin = self._repo.remote('origin')

        origin.fetch()
        origin.pull(self._git_branch)

        return repo_path

    def _build_ssh_command(self) -> str:
        """ Adds support for username and password entering """

        cmd = 'ssh'

        if self._git_key:
            cmd += ' -i %s' % self._git_key
            return cmd

        cmd = 'sshpass -p "%s" ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no'
        return cmd

    def _get_constant_path(self, spec: str):
        """ Creates a path for repository. That path will be always the same """

        repo_path = self._git_repositories_path + '/' + self._normalize_repo_name(spec) + '/'

        if not os.path.isdir(repo_path):
            os.mkdir(repo_path)

        return repo_path

    def add_file(self, name: str, content: str) -> bool:
        if super(GitFilesystem, self).add_file(name=name, content=content):
            self._repo.git.add(name)
            self._repo.commit('Modify "%s"' % name)
            self._repo.remote('origin').push()

        return False

    @staticmethod
    def _normalize_repo_name(url: str):
        """ Normalize the repository name by removing all special characters """

        groups = url.split('@')

        if len(groups) > 1:
            secret = sha256()
            secret.update(groups[0].encode('utf-8'))

            url = url.replace(groups[0], secret.hexdigest()[0:8])

        repo_name = url.replace('@', '_at_') \
            .replace('/', '-') \
            .replace(':', '-')

        return re.sub('[^a-zA-Z0-9_\-.]+', '', repo_name)

    def _prepare_local_path(self, resolver: Resolver):
        """ Create a local path where we will store local git repositories (parent path for each repository) """

        self._git_repositories_path = resolver.resolve_string('%local_path%/git')

        if not os.path.isdir(self._git_repositories_path):
            os.mkdir(self._git_repositories_path)

