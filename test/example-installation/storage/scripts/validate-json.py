# standard bootstrap code
import sys
import os

sys.path = [os.environ.get('BOAUTOMATE_PATH', '/opt/boautomate')] + sys.path
# end of standard bootstrap code


"""
    Just an example pipeline to do something for testing
"""

from boautomate.boautomatelib.nodeexecutor import NodeExecutor
from json import loads as json_loads, JSONDecodeError, dumps as json_dumps


class ValidateJson(NodeExecutor):
    def main(self):
        try:
            json_loads(self._payload.encode('utf-8'))
        except JSONDecodeError as e:
            print(json_dumps({'status': 'error', 'error': str(e)}))
            return

        print(json_dumps({'status': 'OK'}))


ValidateJson().main()
