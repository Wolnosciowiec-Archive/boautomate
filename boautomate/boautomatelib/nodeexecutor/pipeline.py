
import sys
import subprocess
from time import sleep
from typing import Callable
from datetime import datetime
from contextlib import contextmanager

from ..exceptions import TimeoutException

"""
    Basic pipeline helper methods
"""


@contextmanager
def stage(title=''):
    """ Opens and closes a stage. Each stdout and log is collected and sent to a server for each stage. """

    # @todo: Implement stages by capturing logs and sending to server after stage finishes
    # @todo: Locking support

    yield


def info(*args):
    """ Logging """

    print('[' + str(datetime.now()) + ']', '#', *args)


def fail(*args):
    """ Logging """
    info('(!) ~> Failure:', *args)
    sys.exit(1)


def success(*args):
    """ Logging """

    info('=> Success:', *args)
    sys.exit(0)


def wait_until(callback: Callable, seconds: int):
    """ Wait until the callback will return success """

    to_wait = seconds
    last_exception = None

    while seconds > 0:
        try:
            if callback():
                return
        except Exception as e:
            last_exception = e
            pass

        seconds -= 1
        sleep(1)

    if last_exception:
        raise last_exception

    raise TimeoutException('Timeout in wait_until while waiting maximum of %i seconds' % to_wait)


def sh(command: str):
    """ Alias to subprocess """

    return subprocess.check_output(command, shell=True).decode('utf-8')
