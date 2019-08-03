import sys
import re
from time import sleep

"""
    Pipeline resource locking example
    =================================
"""

sys.path.append('/opt/boautomate')

from boautomate.boautomatelib.nodeexecutor import NodeExecutor
from boautomate.boautomatelib.nodeexecutor.pipeline import info, sh
from datetime import timedelta


class LocksExample(NodeExecutor):
    # configurable settings
    regexp: re.Pattern
    separator: str
    latest_stable_name: str

    present_tags: list

    def main(self):
       with self.locks.lock('locks-example', mode=self.locks.MODE_EXIT, expires_in=timedelta(hours=2)):
           info('Hello, the pipeline is now locked')
           sleep(5)

LocksExample().main()
