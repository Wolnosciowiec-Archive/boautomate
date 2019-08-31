
import requests
from json import dumps as json_dumps
from ..payloadparser.slack import SlackUrlFact


class Slack:
    """ Sends messages to Slack """

    _url: str

    def __init__(self, fact: SlackUrlFact):
        self._url = fact.url

    def send(self, text: str, username: str = None, icon: str = None, channel: str = None) -> str:
        payload = {'text': text, 'icon_url': icon, 'channel': channel, 'username': username}
        to_send = {k: v for k, v in payload.items() if v}

        response = requests.post(self._url, data=json_dumps(to_send), headers={
            'Content-Type': 'application/json'
        })

        if response.status_code > 299:
            raise Exception('Error while sending to Slack: %s' % response.text)

        return response.text
