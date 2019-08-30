import sys
from time import sleep

"""
    Pipeline resource locking example
    =================================
"""

sys.path.append('/opt/boautomate')

from boautomate.boautomatelib.nodeexecutor import NodeExecutor
from boautomate.boautomatelib.nodeexecutor.pipeline import info
from boautomate.boautomatelib.nodeexecutor.api.execution import pipeline
from datetime import timedelta


class LocksExample(NodeExecutor):
    def main(self):
        info('Setting a lock on other pipeline "validate-json", and trying to trigger it that pipeline')

        # @todo: Timezone in the container must match host's timezone

        self.locks.create_lock('quay-push', expires_in=timedelta(hours=5),
                               regexp='riotkit',
                               pipeline='validate-json'
                               )

        info('Spawning a pipeline "validate-json"')
        info('Log:', pipeline(name='validate-json', payload=self._get_payload_example()))

        # @todo: Move to second example
        with self.locks.lock('locks-example', mode=self.locks.MODE_WAIT_UNTIL_RELEASED,
                             expires_in=timedelta(hours=2), partial=True):
            info('Hello, any next execution will need to wait until this block ends, because its partial=True')
            sleep(1)

        with self.locks.lock('locks-example', mode=self.locks.MODE_WAIT_UNTIL_RELEASED, partial=False):
            info('No any new Pipeline execution can be started while this block is executing.')
            sleep(1)

    def _get_payload_example(self) -> str:
        return '''
            {
                "name": "repository",
                "repository": "riotkit/test",
                "namespace": "riotkit",
                "docker_url": "quay.io/riotkit/test",
                "homepage": "https://quay.io/repository/riotkit/test",
                "updated_tags": [
                    "latest", "1.3.4", "v3.7.1.4"
                ]
            }
        '''


LocksExample().main()
