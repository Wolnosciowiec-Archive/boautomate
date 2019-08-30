
from .. import BasePipelineHandler


class LocksListHandler(BasePipelineHandler):
    async def get(self):
        """
        Lists all defined Locks

        ---
        tags: ['pipeline/api/locks']
        summary: Lists all locks
        description: Lock is a resource/pipeline block, that prevents code from execution
        produces: ['application/json']
        responses:
            200:
              description: List of locks
        """

        self.write({
            'locks': list(map(
                lambda lock: lock.to_dict(),
                self.container.lock_repository.find_all()
            ))
        })
