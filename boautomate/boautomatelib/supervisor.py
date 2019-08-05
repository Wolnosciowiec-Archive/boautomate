
import abc
import tarfile
import io
import json
import os
from docker import DockerClient
from docker.models.containers import Container as DockerContainer, ExecResult
from .persistence import Execution
from .logging import Logger


class ExecutionResult:
    output: str
    exit_code: int

    def __init__(self, output: str, exit_code: int):
        self.output = output
        self.exit_code = exit_code

    def is_success(self) -> bool:
        return self.exit_code == 0


class Supervisor(abc.ABC):
    _master_url: str

    def __init__(self, master_url: str):
        self._master_url = master_url

    @abc.abstractmethod
    def execute(self, execution: Execution, script: str, payload: str, communication_token: str,
                query: dict, headers: dict, configuration_payloads: list, params: dict) -> ExecutionResult:
        pass

    def prepare_environment(self, payload: str,
                            communication_token: str,
                            query: dict,
                            headers: dict,
                            configuration_payloads: list,
                            execution: Execution,
                            params: dict):
        return {
            'TRIGGER_PAYLOAD': payload,
            'CONFIG_PAYLOADS': json.dumps(configuration_payloads),
            'COMMUNICATION_TOKEN': communication_token,
            'HTTP_QUERY': json.dumps(query),
            'PARAMS': json.dumps(params),
            'HTTP_HEADERS': json.dumps(headers),
            'BUILD_NUMBER': execution.execution_number,
            'MASTER_BASE_URL': self._master_url,
            'PIPELINE_ID': execution.pipeline_id
        }

    @staticmethod
    def env_to_string(env: dict) -> str:
        env_as_str = ''

        for key, value in env.items():
            env_as_str += ' ' + key + '="' + str(value).replace('"', '\\"') + '"'

        return env_as_str.replace("\n", ' ')


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
        tar.add(self._get_boautomate_path() + '/../requirements.txt', 'requirements.txt')

        # write
        tar.close()

        tar_in_bytes.seek(0)
        return tar_in_bytes.read()

    def _get_boautomate_path(self):
        return os.path.dirname(os.path.abspath(__file__)) + '/../'
