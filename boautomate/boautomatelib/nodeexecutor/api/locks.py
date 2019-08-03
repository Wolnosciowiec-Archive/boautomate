
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta

from ...exceptions import PipelineSyntaxError, PipelineLockedException, TimeoutException
from . import Api
from ...http.pipeline.api.locks import route_put_lock, route_delete_lock, route_get_lock
from ..pipeline import wait_until


class Locks:
    _api: Api
    _pipeline_id: str

    MODE_WAIT_UNTIL_RELEASED = 'wait'
    MODE_EXIT = 'exit'

    def __init__(self, api: Api, pipeline_id: str):
        self._api = api
        self._pipeline_id = pipeline_id

    @contextmanager
    def lock(self, lock: str, mode: str, expires_in: timedelta = None, regexp: str = '', seconds: int = 5):
        if self.lock_exists(lock):
            if mode == self.MODE_WAIT_UNTIL_RELEASED:
                try:
                    wait_until(callback=lambda: not self.lock_exists(lock), seconds=seconds)
                except TimeoutException as e:
                    raise PipelineLockedException('Resource is locked. ' + str(e))

            elif mode == self.MODE_EXIT:
                sys.exit(1)
            else:
                raise PipelineSyntaxError('Invalid locking mode specified')

        self.create_lock(lock, expires_in, regexp)
        try:
            yield
        finally:
            self.delete_lock(lock)

    def create_lock(self, lock: str, expires_in: timedelta = None, regexp: str = ''):
        response = self._api.put(route_put_lock(self._pipeline_id, lock), json={
            'regexp': regexp,
            'expires_at': str(datetime.now() + (expires_in if expires_in else timedelta(hours=2)))
        })
        print(response.text)

    def delete_lock(self, lock: str):
        self._api.delete(route_delete_lock(self._pipeline_id, lock))

    def lock_exists(self, lock: str):
        response = self._api.get(route_get_lock(self._pipeline_id, lock))

        return response.status_code == 200
