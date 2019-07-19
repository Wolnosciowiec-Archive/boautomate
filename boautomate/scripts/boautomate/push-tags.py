
import os
import sys

sys.path.append('/boautomate')

from boautomate.boautomatelib.localexecutor import LocalExecutor

class PushTags(LocalExecutor):
    def main(self):
        print(self.get_build_number())

PushTags().main()
