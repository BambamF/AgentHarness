import os
from typing import Any
from src.harness.artefacts.action import ActionArtefact
from src.harness.artefacts.execution import ExecutionArtefact
import docker
from datetime import datetime
from src.harness.artefacts.permission import PermissionArtefact
from src.harness.artefacts.artefact_store import ArtefactStore
from src.harness.artefacts.artefact import Artefact
from src.harness.artefacts.artefact_factory import ArtefactFactory
import logging
from repositories.repository_manager import RepositoryManager

class RuntimeManager:
    def __init__(self, image: str, agent: str, model: str, executions_dir: str, permission_manager: PermissionManager, artefact_store: ArtefactStore):
        self.agent = agent
        self.model = model
        self.executions_dir = executions_dir
        self.client = docker.from_env()
        self.permission_manager = permission_manager
        self.artefact_store = artefact_store
        self.image = self.client.images.pull(image)

    def execute(self, action_artefact: ActionArtefact, permission_artefact: PermissionArtefact) -> ExecutionArtefact:

        current_execution_dir = os.path.join(self.executions_dir, str(action_artefact.execution_id))

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
            os.makedirs(directory, exist_ok=True)

        self._write_json(os.path.join(current_execution_dir, "action.json"), action_artefact)
        
        self._write_json(os.path.join(current_execution_dir, "permission.json"), action_artefact)

        started_at = datetime.now()
        
        container = None

        try:
            container = self.client.containers.run(
                    image=self.image,
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
                    network_disabled=True,
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

            params = {
                    "execution_id": action_artefact.execution_id,
                    "producer": action_artefact.producer,
                    "tool_input": action_artefact.input,
                    "permitted": permission_artefact.allowed,
                    "execution_status": "SUCCESS" if result["StatusCode"] == 0 else "FAILED",
                    "termination_reason": "completed" if result["StatusCode"] == 0 else "could not be completed",
                    "exit_code": result["StatusCode"],
                    "started_at": started_at,
                    "finished_at": datetime.now(),
                    "image": self.image,
                    "input_path": str(input_dir),
                    "output_path": str(output_dir),
                    "workspace_path": str(workspace_dir),
                    "payload": RepositoryManager.get_commit_hash(),
                    "error": None
                    }

            logging.info(f"[RUNTIME] Input: {action_artefact.input} | Execution Status: {params.get("execution_status")} | Permission: {permission_artefact.allowed} | Execution ID: {action_artefact.execution_id}")

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, self.artefact_store, action_artefact.execution_id, action_artefact.producer)
        except Exception as e:
            
            
            params = {
                    "execution_id": action_artefact.execution_id,
                    "producer": action_artefact.producer,
                    "tool_input": action_artefact.input,
                    "permitted": permission_artefact.allowed,
                    "execution_status": "FAILED",
                    "termination_reason": "exception encountered",
                    "exit_code": None,
                    "started_at": started_at,
                    "finished_at": datetime.now(),
                    "image": self.image,
                    "input_path": str(input_dir),
                    "output_path": str(output_dir),
                    "workspace_path": str(workspace_dir),
                    "payload": None,
                    "error": str(e)
                    }
            logging.exception(f"[RUNTIME EXCEPTION] Input: {action_artefact.input} | Execution Status: {params.get("execution_status")} | Permission: {permission_artefact.allowed} | Execution ID: {action_artefact.execution_id}")

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, self.artefact_store, action_artefact.execution_id, action_artefact.producer)
        
        finally:
            if container is not None:
                container.stop()

        self._write_json(os.path.join(current_execution_dir, "execution.json"), execution_artefact)
        return execution_artefact

    def get_blocked_execution_artefact(self, action_artefact: ActionArtefact, permission_artefact: PermissionArtefact) -> ExecutionArtefact:
        started_at = datetime.now()
        params = {
                "execution_id": action_artefact.execution_id,
                "producer": action_artefact.producer,
                "tool_input": action_artefact.input,
                "permitted": permission_artefact.allowed,
                "execution_status": "FAILED",
                "termination_reason": "action not permitted",
                "exit_code": None,
                "started_at": started_at,
                "finished_at": datetime.now(),
                "image": self.image,
                "input_path": None,
                "output_path": None,
                "workspace_path": None,
                "payload": None,
                "error": None
                }
        logging.exception(f"[RUNTIME EXCEPTION] Input: {action_artefact.input} | Execution Status: {params.get("execution_status")} | Permission: {permission_artefact.allowed} | Execution ID: {action_artefact.execution_id}")

        execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, self.artefact_store, action_artefact.execution_id, action_artefact.producer)
        return execution_artefact

    @staticmethod
    def _write_json(self, path: str, artefact: Artefact):
        with open(path, 'a', encoding='utf-8', newline="") as f:
            f.write(artefact.to_json())
