
from collections import namedtuple
from datetime import datetime, timedelta
from dateutil.parser import parse as date_parse
from .. import BasePipelineHandler
from ....persistence import Lock
from ....schema import Schema
from ....locks import LocksManager
from ....exceptions import EntityNotFound, RequestValidationException

Payload = namedtuple('Payload', 'expires_at regexp keywords schema')


def route_put_lock(pipeline_id: str, lock_id: str) -> str:
    return "/pipeline/%s/api/lock/%s" % (pipeline_id, lock_id)


def route_delete_lock(pipeline_id: str, lock_id: str) -> str:
    return route_put_lock(pipeline_id, lock_id)


def route_get_lock(pipeline_id: str, lock_id: str) -> str:
    return route_put_lock(pipeline_id, lock_id)


class LocksHandler(BasePipelineHandler):
    def _get_lock(self, lock_id: str, pipeline_id: str, create: bool) -> Lock:
        try:
            return self.container.lock_repository.find_by(lock_id, pipeline_id)
        except EntityNotFound:
            if create:
                return self.container.lock_repository.create(lock_id, pipeline_id)

    def _parse(self, payload: str) -> Payload:
        Schema.validate_json_payload(payload, 'pipeline/api/lock')
        as_dict = Schema.parse_json(payload)

        expires_at = date_parse(as_dict.get('expires_at')) if as_dict.get('expires_at') \
            else datetime.now() + timedelta(hours=2)
        regexp = as_dict.get('regexp')
        keywords = as_dict.get('keywords')
        schema = self.container.fs_tpl.inject_includes(as_dict.get('schema'))

        try:
            LocksManager.validate_filters_for_lock(keywords, regexp, schema)

        except RequestValidationException as e:
            self.raise_validation_error(str(e))

        return Payload(expires_at=expires_at, regexp=regexp, keywords=keywords, schema=schema)

    async def put(self, pipeline_id: str, lock_id: str):
        """
            Create or update existing lock
        """

        pipeline = self._get_pipeline(pipeline_id)
        if not pipeline:
            return

        # can be in context of a Pipeline, but locking other Pipeline
        subject_pipeline_id = self.request.query_arguments.get('pipeline_id')[0].decode('utf-8') \
            if self.request.query_arguments.get('pipeline_id') else pipeline_id

        # 1. Verify access
        self.assert_has_access_to_internal_api(pipeline_id)

        # 2. Get subject
        lock = self._get_lock(lock_id, subject_pipeline_id, create=True)

        # 3. Parse payload
        payload = self._parse(self.request.body.decode('utf-8'))

        # 4. Fill in the subject and persist
        lock.expires_at = payload.expires_at
        lock.payload_regexp = payload.regexp
        lock.payload_schema = payload.schema
        lock.payload_keywords = payload.keywords

        self.container.lock_repository.flush(lock)
        self.write({
            'status': 'OK',
            'lock': lock.to_dict()
        })

    async def delete(self, pipeline_id: str, lock_id: str):
        """
            Delete a lock
        """

        pipeline = self._get_pipeline(pipeline_id)
        if not pipeline:
            return

        self.assert_has_access_to_internal_api(pipeline_id)
        lock = self._get_lock(lock_id, pipeline_id, create=False)

        if not lock:
            self.write({'status': 'OK', 'detail': 'already_deleted'})
            return

        self.container.lock_repository.delete(lock)
        self.write({'status': 'OK', 'detail': 'deleted'})

    async def get(self, pipeline_id: str, lock_id: str):
        pipeline = self._get_pipeline(pipeline_id)
        if not pipeline:
            return

        self.assert_has_access_to_internal_api(pipeline_id)
        lock = self._get_lock(lock_id, pipeline_id, create=False)

        if not lock:
            self.raise_not_found_error('Lock not found')
            return

        self.write({
            'status': 'OK',
            'lock': lock.to_dict()
        })
