import sys
from datetime import datetime
from contextlib import contextmanager


@contextmanager
def stage(title=''):
    yield


def info(*args):
    print('[' + str(datetime.now()) + ']', '#', *args)


def fail(*args):
    info('(!) ~> Failure:', *args)
    sys.exit(1)


def success(*args):
    info('=> Success:', *args)
    sys.exit(0)


