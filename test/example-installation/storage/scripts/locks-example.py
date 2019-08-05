import sys
from time import sleep

"""
    Pipeline resource locking example
    =================================
"""

sys.path.append('/opt/boautomate')

from boautomate.boautomatelib.nodeexecutor import NodeExecutor
from boautomate.boautomatelib.nodeexecutor.pipeline import info
from datetime import timedelta


class LocksExample(NodeExecutor):
    def main(self):
       with self.locks.lock('locks-example', mode=self.locks.MODE_WAIT_UNTIL_RELEASED, expires_in=timedelta(hours=2)):
           info('Hello, the pipeline is now locked')
           sleep(5)

LocksExample().main()
