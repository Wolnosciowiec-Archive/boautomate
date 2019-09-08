
"""
    Native Run Supervisor
    =====================

    Runs the pipeline on primary node without any kind of isolation, runs as a regular script - natively.
"""

import subprocess
import os

from .base import Supervisor, ExecutionResult
from ..persistence import Execution


class NativeRunSupervisor(Supervisor):
    _workspaces_path: str
    _read_timeout = 3600

    def __init__(self, master_url: str, workspaces_path: str):
        super().__init__(master_url)
        self._workspaces_path = workspaces_path

        if not os.path.isdir(self._workspaces_path):
            os.mkdir(self._workspaces_path)

    def execute(self, execution: Execution, script: str, payload: str, communication_token: str,
                query: dict, headers: dict, configuration_payloads: list, params: dict) -> ExecutionResult:

        env = self.prepare_environment(
            payload=payload, communication_token=communication_token,
            query=query, headers=headers, configuration_payloads=configuration_payloads,
            execution=execution,
            params=params
        )
        env['BOAUTOMATE_PATH'] = self._get_boautomate_path()

        workspace_path = self._get_workspace_path(execution.pipeline_id)

        if not os.path.isdir(workspace_path):
            os.mkdir(workspace_path)

        output, exit_code = self._execute_pipeline_code(script, workspace_path, env)

        return ExecutionResult(output, exit_code)

    def _execute_pipeline_code(self, script: str, workspace_path: str, env: dict) -> tuple:
        self._put_script_at_workspace(script, workspace_path)

        with subprocess.Popen('cd %s && ./entrypoint.py' % workspace_path, shell=True, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            proc.wait(self._read_timeout)
            return proc.stdout.read().decode('utf-8') + proc.stderr.read().decode('utf-8'), proc.returncode

    def _get_workspace_path(self, pipeline_id: str):
        return self._workspaces_path + '/' + pipeline_id

    @staticmethod
    def _put_script_at_workspace(content: str, workspace_path: str):
        script_path = workspace_path + '/entrypoint.py'

        f = open(script_path, 'wb')
        f.write(content.encode('utf-8'))
        f.close()

        os.system('chmod +x %s' % script_path)
