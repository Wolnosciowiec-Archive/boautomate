# standard bootstrap code
import sys
import os

sys.path = [os.environ.get('BOAUTOMATE_PATH', '/opt/boautomate')] + sys.path
# end of standard bootstrap code

from time import sleep

"""
    Parameters example
    ==================
"""

from boautomate.boautomatelib.nodeexecutor import NodeExecutor
from boautomate.boautomatelib.nodeexecutor.pipeline import info


class ParamsExample(NodeExecutor):
    def main(self):
        info('Message from query string "message": ' + str(self.get_query_argument('message')))
        info('Message from header "Message": ' + str(self.get_header('Message')))
        info('Message from overridable parameter "message": ' + str(self.get_overridable_param('message')))
        info('Message from pipeline parameter "message": ' + str(self.get_param('message')))


ParamsExample().main()
