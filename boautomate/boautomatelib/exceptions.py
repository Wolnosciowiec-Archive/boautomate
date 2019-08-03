

class StorageException(Exception):
    pass


class ExecutorException(Exception):
    pass


class TimeoutException(ExecutorException):
    pass


class ScriptExpectationsNotMetException(ExecutorException):
    pass


class NoContextException(Exception):
    pass


class PipelineException(Exception):
    pass


class PipelineSyntaxError(PipelineException):
    pass


class PipelineLockedException(PipelineException):
    pass


class ConfigurationException(Exception):
    pass


class EntityNotFound(Exception):
    pass


class HttpError(Exception):
    http_code: int

    def __init__(self, http_code: int, message: str):
        super().__init__(message)
        self.http_code = http_code
