
import json
import tornado.web
import traceback
from abc import ABC
from typing import Optional, Awaitable, Any, Union
from tornado_swagger.model import register_swagger_model
from ..exceptions import HttpError, SchemaValidationException
from ..logger import Logger
from ..ioc import Container


@register_swagger_model
class RequestError:
    """
    ---
    type: object
    description: Request error (validation, resource not found, no permissions)
    properties:
        error:
            type: string
        type:
            type: string
    """


@register_swagger_model
class ServerError:
    """
    ---
    type: object
    description: Server error
    properties:
        details:
            type: array
            items:
                type: string
        status:
            type: integer
        type:
            type: string
    """


class BaseHandler(ABC, tornado.web.RequestHandler):
    container = None  # type: Container
    _error_already_written_as_json = False

    @staticmethod
    def inject_container(container: Container):
        BaseHandler.container = container

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def raise_not_found_error(self, msg: str = 'Not found') -> None:
        Logger.error(msg)
        raise HttpError(404, json.dumps({'error': msg, 'type': 'not_found'}))

    def raise_validation_error(self, msg: str = 'Configuration error'):
        Logger.error(msg)
        raise HttpError(400, json.dumps({'error': msg, 'type': 'validation_error'}))

    def write_no_access_error(self, msg: str) -> None:
        raise HttpError(403, json.dumps({'error': msg, 'type': 'no_access'}))

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        details = []

        if "exc_info" in kwargs:
            try:
                raise
            except SchemaValidationException as e:
                self.raise_validation_error(str(e))
                return
            except HttpError as e:
                self.set_status(e.http_code)
                self.finish(str(e))
                return
            except:
                pass

            details = traceback.format_exception(*kwargs["exc_info"])

        self.set_status(status_code)
        self.finish({
            'status': status_code,
            'type': 'server_error',
            'details': details
        })


    def _get_serializable_query_arguments(self):
        output = dict()

        for query_param, values in self.request.query_arguments.items():
            str_values = []

            for value in values:
                str_values.append(value.decode('utf-8'))

            output[query_param] = str_values

        return output

    def write(self, chunk: Union[str, bytes, dict]) -> None:
        if type(chunk) == dict:
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            chunk = json.dumps(chunk, indent=4, sort_keys=True)

        return super().write(chunk)
