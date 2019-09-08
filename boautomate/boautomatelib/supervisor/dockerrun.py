
"""
    Docker Run Supervisor
    =====================

    Runs the pipeline in a docker container spawning a new container on each run.
"""

import tarfile
import io
import os
from docker import DockerClient
from docker.models.containers import Container as DockerContainer, ExecResult

from ..persistence import Execution
from ..logger import Logger
from .base import Supervisor, ExecutionResult


class DockerRunSupervisor(Supervisor):
    docker: DockerClient
    image: str

    def __init__(self, master_url: str, base_url=None, image: str = 'python:3.7-alpine'):
        super().__init__(master_url)
        self.docker = DockerClient(base_url=base_url)
        self.image = image

    def execute(self, execution: Execution, script: str, payload: str, communication_token: str,
                query: dict, headers: dict, configuration_payloads: list, params: dict) -> ExecutionResult:

        Logger.debug('Spawning docker container')

        container: DockerContainer = self.docker.containers.run(
            image=self.image,
            remove=True,
            detach=True,
            command='sleep 7200',
            name=execution.to_ident_string(),
            stdin_open=True
        )

        container.put_archive('/', self.prepare_archive(script))
        # container.exec_run('/bin/sh -c "test -f ./requirements.txt && pip install -r ./requirements.txt"')

        env = self.prepare_environment(
            payload=payload, communication_token=communication_token,
            query=query, headers=headers, configuration_payloads=configuration_payloads,
            execution=execution,
            params=params
        )

        Logger.debug('supervisor: ' + Supervisor.env_to_string(env))

        run: ExecResult = container.exec_run('python3 entrypoint.py', environment=env)
        container.kill()

        return ExecutionResult(output=run.output.decode('utf-8'), exit_code=run.exit_code)

    def prepare_archive(self, script: str) -> bytes:
        """ Prepares the script as a TAR.GZ archive that will be natively unpacked by docker """

        Logger.debug('Preparing a tar.gz to send to docker daemon')

        tar_in_bytes = io.BytesIO()
        tar = tarfile.open(fileobj=tar_in_bytes, mode='w:gz')

        script_file = io.BytesIO(script.encode('utf-8'))
        script_file.seek(0)

        script_info = tarfile.TarInfo(name='entrypoint.py')
        script_info.size = len(script)

        # add script as entrypoint.py
        tar.addfile(tarinfo=script_info, fileobj=script_file)

        # library
        tar.add(self._get_boautomate_path() + '/../', '/opt/boautomate', recursive=True)

        # write
        tar.close()

        tar_in_bytes.seek(0)
        return tar_in_bytes.read()

    @staticmethod
    def _get_boautomate_path():
        return os.path.dirname(os.path.abspath(__file__)) + '/../../'
