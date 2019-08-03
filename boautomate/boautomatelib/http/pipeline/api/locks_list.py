
from .. import BasePipelineHandler


class LocksListHandler(BasePipelineHandler):
    """
    ---
    tags: ['pipeline', 'locks']
    summary: Lists all locks
    description: Lock is a resource/pipeline block, that prevents code from execution
    produces: ['application/json']
    responses:
        200:
          description: List of locks
    """

    def get(self):
        self.write({
            'locks': list(map(
                lambda lock: lock.to_dict(),
                self.container.lock_repository.find_all()
            ))
        })
