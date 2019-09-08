
import re
import json

from .repository import LocksRepository
from .persistence import Pipeline
from .logger import Logger
from .schema import Schema
from .exceptions import RequestValidationException, SchemaValidationException
from .filesystem.templating import Templating


class LocksManager:
    repo: LocksRepository
    templating: Templating

    def __init__(self, repository: LocksRepository, fs_templating: Templating):
        self.repo = repository
        self.templating = fs_templating

    @staticmethod
    def validate_filters_for_lock(keywords, regexp: str, schema: str):
        if keywords and type(keywords) is not list:
            raise RequestValidationException('Keywords needs be empty or a list of keywords')

        if regexp:
            try:
                re.compile(regexp)
            except re.error as e:
                raise RequestValidationException('Regexp does not compile. %s' % str(e)) from e

        if schema:
            try:
                json.loads(schema.encode('utf-8'))
            except Exception as err:
                raise RequestValidationException('Schema is not a valid JSON. %s' % str(err))

    def is_payload_blocked_by_any_lock_on_pipeline(self, pipeline: Pipeline, payload: str) -> bool:
        """
        Tells if the Pipeline should be blocked from running. Bases on Locks stored in database.
        Each Lock is assigned to a Pipeline and can block from execution:
            - Any Pipeline run
            - Blocks run that contains keywords in payload
            - Blocks run that payload schema is valid with defined schema
            - Blocks run that payload has matches by defined regexp

        :param pipeline:
        :param payload:
        :return:
        """

        all_locks_on_pipe = self.repo.find_all_for_pipe(pipeline.id)

        for lock in all_locks_on_pipe:
            if lock.is_expired():
                Logger.debug('Lock "%s" is expired' % lock.id)
                continue

            enabled_checks_count = lock.count_payload_filters()
            checks = []

            Logger.debug('Checking Lock "%s" with "%i" filters' % (lock.id, enabled_checks_count))

            if lock.payload_regexp:
                try:
                    checks.append(len(re.findall(lock.payload_regexp, payload)) > 0)
                    Logger.debug('Payload was matched by regexp "%s" on lock "%s"' % (lock.payload_regexp, str(lock.id)))

                except re.error as e:
                    Logger.error('Error compiling regexp "%s" in LocksManager, for pipeline_id=%s. %s' %
                                 (lock.payload_regexp, pipeline.id, str(e)))
                    continue

            if lock.payload_schema:
                try:
                    Schema.validate(payload=dict(json.loads(payload)),
                                    schema=dict(json.loads(lock.schema.encode('utf-8'))))
                    checks.append(True)
                    Logger.info('Payload was matched by schema')

                except SchemaValidationException as e:
                    Logger.debug('Payload not matched by schema, but schema validation present. ' + str(e))

                    checks.append(False)
                except Exception as e:
                    Logger.error('Error when validating schema in LocksManager. ' + str(e))
                    continue

            if lock.payload_keywords:
                if not type(lock.payload_keywords) == list:
                    Logger.error('Payload keywords in a Lock needs to be of a "list" type')
                    continue

                for keyword in lock.payload_keywords:
                    if keyword in payload:
                        Logger.debug('"%s" keyword matches the payload, blocking')
                        checks.append(True)
                        break

            hits = list(filter(lambda match: match is True, checks))

            if len(checks) == 0:
                """ Case: When any Pipeline Execution is blocked """

                Logger.info('Pipeline run blocked without checks')
                return True

            if enabled_checks_count == len(hits):
                """ Case: When a specific Pipeline Execution is blocked, when the payload is matching
                          some criteria. 
                """

                Logger.info('Pipeline run blocked with checks')
                return True

        Logger.debug('Pipeline run is not blocked')
        return False
