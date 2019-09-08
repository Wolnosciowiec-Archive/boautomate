
"""
    Multiple Supervisor
    ===================

    A scheduler that decides which Supervisor could be picked for given job.
    The "children" and "settings" should be prepared in a factory and passed there as parsed objects.

    There are multiple strategies of selecting a supervisor - see STRATEGY_* class variables
"""

from typing import List
from random import randrange
from ..persistence import Execution
from ..repository import PipelineRepository
from ..logger import Logger
from .base import Supervisor, ExecutionResult, SupervisorDefinition, Settings


class MultipleSupervisor(Supervisor):
    STRATEGY_RANDOM = 'random'
    STRATEGY_ROUND_ROBIN = 'round-robin'

    children: List[SupervisorDefinition]
    settings: Settings
    pipe_repo: PipelineRepository
    round_robin_memory: {}

    def __init__(self, master_url: str, children: List[SupervisorDefinition],
                 settings: Settings, repository: PipelineRepository):

        super().__init__(master_url)
        self.children = children
        self.settings = settings
        self.pipe_repo = repository
        self.round_robin_memory = {}

    def execute(self, **kwargs) -> ExecutionResult:
        supervisor: Supervisor = self.find_supervisor_for_execution(kwargs['execution'])

        return supervisor.execute(**kwargs)

    def find_supervisor_for_execution(self, execution: Execution) -> Supervisor:
        """ Find proper Supervisor that will execute the pipeline """

        pipeline = self.pipe_repo.find_by_id(execution.pipeline_id)

        if not pipeline.supervisor_label:
            return self.select_supervisor_considering_strategy(self.children, self.settings.selection_strategy, True)

        label = pipeline.supervisor_label
        matching_supervisors = []

        for child in self.children:
            if label in child.labels or child.name == label:
                matching_supervisors.append(child)

        if not matching_supervisors:
            raise Exception('Cannot match any supervisor for "%s" pipeline' % pipeline.id)

        return self.select_supervisor_considering_strategy(matching_supervisors, self.STRATEGY_RANDOM, False)

    def select_supervisor_considering_strategy(self, supervisors: List[SupervisorDefinition],
                                               strategy: str, only_default: bool) -> Supervisor:

        """
        Selects a supervisor considering the strategy

        :param only_default:
        :param supervisors:
        :param strategy:
        :return:
        """

        selected = None

        if only_default:
            supervisors = list(filter(
                lambda child: child.default,
                supervisors
            ))

        if strategy == self.STRATEGY_RANDOM:
            selected = supervisors[randrange(0, len(supervisors))]
        elif strategy == self.STRATEGY_ROUND_ROBIN:
            selected = self._round_robin_find_next(supervisors)

        if selected:
            self._round_robin_increment(selected.name)
            return selected.supervisor

        raise Exception('Cannot match supervisor, invalid selection_strategy')

    def _round_robin_find_next(self, supervisors: List[SupervisorDefinition]) -> SupervisorDefinition:
        min_used = 0
        min_sv: SupervisorDefinition = None

        for supervisor in supervisors:
            # first time
            if supervisor.name not in self.round_robin_memory:
                return supervisor

            count = self.round_robin_memory[supervisor.name]

            if count < min_used or min_sv is None:
                min_used = count
                min_sv = supervisor

        Logger.debug('Supervisor: Selected "%s" using round-robin strategy' % min_sv.name)

        return min_sv

    def _round_robin_increment(self, supervisor_name: str):
        if supervisor_name not in self.round_robin_memory:
            self.round_robin_memory[supervisor_name] = 0

        self.round_robin_memory[supervisor_name] += 1

        Logger.debug('Supervisor round_robin_memory[%s] = %i' % (
            supervisor_name,
            self.round_robin_memory[supervisor_name])
        )
