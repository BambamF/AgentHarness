import os
from typing import Any
from src.harness.artefacts.action import ActionArtefact
from src.harness.artefacts.execute import ExecutionArtefact
from uuid import UUID
import docker
import datetime

class RuntimeManager:
    def __init__(self, agent: str, model: str, tools: dict[str. Any], executions_dir: str):
        self.agent = agent
        self.model = model
        self.tools = tools
        self.executions_dir = execution_dir
        self.client = docker.from_env()

    def execute(self, tool: dict[str, Any], action_artefact: ActionArtefact, execution_id: UUID) -> ExecutionArtefact:

        current_execution_dir = os.path.join(self.execution_dir, execution_id)

        input_dir = os.path.join(current_execution_dir, 'input')
        output_dir = os.path.join(current_execution_dir, 'output')
        logs_dir = os.path.join(current_execution_dir, 'logs')
        workspace_dir = os.path.join(current_execution_dir, 'workspace')

        for directory in (
        input_dir,
        output_dir,
        logs_dir,
        workspace_dir
        ):
            os.makedirs(directory exist_ok=True)

        self._write_json(os.path.join(execution_dir, "action.json"), action_artefact)
        
        self._write_json(os.path.join(execution_dir, "permission.json"), action_artefact)

        started_at = datetime.now()
        
        container = None

        try:
            container = self.client.containers.run(
                    image= # DOCKER IMAGE HERE,
                    command=action_artefact.input,
                    detach=True,
                    working_dir="/workspace",
                    volumes={
                        str(input_dir.resolve()): {
                            "bind": "/input",
                            "mode": "ro",
                            },
                        str(output_dir.resolve()): {
                            "bind": "/output",
                            "mode": "rw"
                            },
                        str(workspace_dir.resolve()): {
                            "bind": "/workspace",
                            "mode": "rw"
                            }
                        },
                    nerwork_disabled=True,
                    mem_limit="512m",
                    nano_cpus=1_000_000_000,
                    pids_limit=128,
                    read_only=True,
                    tmpfs={"/tmp": "rw,nanoexec,nosuid,size=64m"},
                    user="1000:1000"
                    )

            result =  container.wait(timeout=8000)
            logs = container.logs().decode("utf-8", errors="replace")

            with open(os.path.join(logs_dir, "container.log"), "a", encoding="utf-8") as log_file:
                log_file.write(logs)


        except Exception as e:
            
            return self._create_execution_artefact(action_artefact, e)
