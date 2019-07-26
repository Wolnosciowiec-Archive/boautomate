
from requests.auth import AuthBase, HTTPBasicAuth
from requests import get as http_get, post as http_post, put as http_put, delete as http_delete, Response
from urllib.parse import urlsplit
from contextlib import contextmanager
import json
from .dockermanifest import sign_manifest

"""
    Docker registry library
    
        ```python
        d = DockerRegistryClient(
            host='https://quay.io/v2',
            username='riotkit+riotkitrobo',
            password='XXX',
            auth_url='https://quay.io/v2/auth'
        )
        
        try:
            print(d.list_tags('riotkit/test'))
            print(d.tag('riotkit/test', 'latest', 'latest-dev'))
        
        except RegistryException as e:
            print(str(e))
            print(e.response)
        ```
"""


class RegistryException(Exception):
    response: str

    def __init__(self, msg: str, response: str = ''):
        super(Exception, self).__init__(msg)
        self.response = response



class HTTPBearerAuth(AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __eq__(self, other):
        return all([
            self.token == getattr(other, 'token', None)
        ])

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.token
        return r


class DockerRegistryClient:
    _host: str
    _username: str
    _password: str
    _auth_url: str
    _token_cache: dict

    def __init__(self, host: str, username: str = '', password: str = '', auth_url: str = ''):
        self._token_cache = {}
        self._host = host
        self._username = username
        self._password = password
        self._auth_url = auth_url
        self._update_auth_url_for_popular_repositories()

    def _setup_auth(self, repository: str, scope: str):
        if self._auth_url:
            return HTTPBearerAuth(self._grab_auth_token(repository, repo_scope=scope))

        if not self._username or not self._password:
            return None

        return HTTPBasicAuth(self._username, self._password)

    def _update_auth_url_for_popular_repositories(self):
        if self._auth_url:
            return

        if "quay.io" in self._host:
            self._auth_url = 'https://quay.io/v2/auth'

        if "docker.io" in self._host:
            self._auth_url = 'https://auth.docker.io/token'

    def _grab_auth_token(self, repository: str, repo_scope: str = 'pull') -> str:
        cache_ident = repository + "_" + repo_scope

        if cache_ident in self._token_cache:
            return self._token_cache[cache_ident]

        scope = 'repository:' + repository + ':%s' % repo_scope
        service = urlsplit(self._host).netloc
        url = self._auth_url + '?scope=%s&service=%s' % (scope, service)

        response = http_get(url=url, auth=HTTPBasicAuth(self._username, self._password))
        json = response.json()

        if "token" not in json:
            raise RegistryException('Cannot get authentication token, maybe invalid user/password?', response.text)

        token = response.json()['token']
        self._token_cache[cache_ident] = token

        return token

    def list_tags(self, repository: str) -> list:
        response = http_get(self._get_url('/' + repository + '/tags/list'), auth=self._setup_auth(repository, 'pull'))

        with self.error_handling(response):
            return response.json()['tags']

    def tag(self, repository: str, origin_tag: str, destination_tag: str):
        """
        In V2 API there is no tagging. To tag we need to copy a manifest.

        :param repository:
        :param origin_tag:
        :param destination_tag:
        :return:
        """

        auth = self._setup_auth(repository, scope='*')
        origin_manifest_req = http_get(url=self._get_url('/' + repository + '/manifests/' + origin_tag), auth=auth)

        response = origin_manifest_req.text

        with self.error_handling(response):
            origin_manifest = origin_manifest_req.json()

        if "errors" in origin_manifest and "MANIFEST_UNKNOWN" in response:
            raise RegistryException('Unknown tag "' + origin_tag + '" in "' + repository + '" repository',
                                    response)

        # correct the manifest
        manifest = {}
        manifest.update(origin_manifest)
        manifest.update({'name': repository, 'tag': destination_tag})

        dest_result = http_put(
            url=self._get_url('/' + repository + '/manifests/' + destination_tag),
            auth=auth,
            data=sign_manifest(manifest),
            headers={
                'Content-Type': 'application/vnd.docker.distribution.manifest.v1+prettyjws'
            }
        )

        if "MANIFEST_INVALID" in dest_result.text:
            raise RegistryException('Tag manifest is invalid', dest_result.text)

        if dest_result.status_code != 202:
            raise RegistryException('Cannot push docker tag "%s", got non-202 response code' % destination_tag,
                                    dest_result.text)

    def _get_url(self, path: str) -> str:
        return self._host.rstrip('/') + path

    @contextmanager
    def error_handling(self, response: Response = None):
        try:
            yield
        except json.decoder.JSONDecodeError as e:
            print(response.url)

            if response and response.status_code == 404:
                raise RegistryException('Tag or repository not found', response.text)

            raise RegistryException('Registry communication error: ' + (response.text if response is not None else ''), str(e))
