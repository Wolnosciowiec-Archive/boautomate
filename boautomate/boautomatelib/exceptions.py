

class StorageException(Exception):
    pass


class ExecutorException(Exception):
    pass


class ScriptExpectationsNotMetException(ExecutorException):
    pass


class NoContextException(Exception):
    pass


class ConfigurationException(Exception):
    pass

