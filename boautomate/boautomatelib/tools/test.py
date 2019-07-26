
from lib.docker import DockerRegistryClient, RegistryException

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
