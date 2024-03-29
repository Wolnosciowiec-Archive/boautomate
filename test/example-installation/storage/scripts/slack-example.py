#!/usr/bin/env python3

# standard bootstrap code
import sys
import os

sys.path = [os.environ.get('BOAUTOMATE_PATH', '/opt/boautomate')] + sys.path
# end of standard bootstrap code

"""
    Slack example
    =============
"""

from boautomate.boautomatelib.nodeexecutor import NodeExecutor
from boautomate.boautomatelib.nodeexecutor.pipeline import info, stage
from boautomate.boautomatelib.nodeexecutor.slack import Slack


class SlackExample(NodeExecutor):
    def main(self):
        with stage('Send a notification'):
            #  More complex case: to construct with additional params use get_tool(Slack, some_param='some-value')
            slack: Slack = self.context().get_tool(Slack)
            info('Slack tool built:', slack)
            info('Attempt to send a message:', slack.send('Hello from Boautomate'))


SlackExample().main()
