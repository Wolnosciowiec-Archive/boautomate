
import requests
from urllib.parse import urljoin


class Api:
    client: requests.Session
    _url: str

    def __init__(self, base_url: str, token: str):
        self._url = base_url
        self.client = requests.Session()
        self.client.headers.setdefault('Token', token)

    def get(self, path: str, **kwargs):
        return self.client.get(url=self._construct_url(path), **kwargs)

    def post(self, path: str, **kwargs):
        return self.client.post(url=self._construct_url(path), **kwargs)

    def put(self, path: str, **kwargs):
        return self.client.put(url=self._construct_url(path), **kwargs)

    def delete(self, path: str, **kwargs):
        return self.client.delete(url=self._construct_url(path), **kwargs)

    def _construct_url(self, path: str) -> str:
        return urljoin(self._url, path)
