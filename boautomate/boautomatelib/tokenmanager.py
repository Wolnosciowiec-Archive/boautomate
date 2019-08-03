
from contextlib import contextmanager
from .persistence import Pipeline, Execution, Token
from .repository import TokenRepository


class TokenManager:
    _repository: TokenRepository

    def __init__(self, repository: TokenRepository):
        self._repository = repository

    def request(self, pipeline: Pipeline, execution: Execution) -> str:
        token = self._repository.create(pipeline, execution)
        self._repository.flush(token)

        return token.id

    def get(self, token_id: str) -> Token:
        return self._repository.find_by_id(token_id)

    def revoke(self, id: str):
        token = self._repository.find_by_id(id)
        token.active = False

        self._repository.flush(token)

    @contextmanager
    def transaction(self, pipeline: Pipeline, execution: Execution):
        token = self.request(pipeline, execution)
        try:
            yield token
        finally:
            self.revoke(token)
