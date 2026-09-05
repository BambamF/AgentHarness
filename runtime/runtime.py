import os
import shutil
from typing import Any
from src.harness.artefacts.action import ActionArtefact
from src.harness.artefacts.execution import ExecutionArtefact
import docker
import json
from datetime import datetime
from src.harness.artefacts.permission import PermissionArtefact
from src.harness.artefacts.artefact_store import ArtefactStore
from src.harness.artefacts.artefact import Artefact
from src.harness.artefacts.artefact_factory import ArtefactFactory
import logging
from repositories.repository_manager import RepositoryManager
from uuid import UUID

class RuntimeManager:
    def __init__(self, image: str, executions_dir: str, repository_root: str, artefact_store: ArtefactStore, git_user_name: str = "HarnessAgent", git_user_email: str = "harness@localhost"):
        self.executions_dir = executions_dir
        self.client = docker.from_env()
        self.image = image
        self.repository_root = repository_root
        self.git_user_name = git_user_name
        self.git_user_email = git_user_email

        self.container = None
        self.execution_id = None
        self.execution_dir = None
        self.input_dir = None
        self.output_dir = None
        self.logs_dir = None
        self.workspace_dir = None

    def start(self, execution_id: UUID):

        if self.container is not None:
            raise RuntimeError("A runtime container is already active")

        self.execution_id = execution_id

        self.execution_dir = os.path.join(self.executions_dir, str(execution_id))
        self.input_dir = os.path.join(self.execution_dir, 'input')
        self.output_dir = os.path.join(self.execution_dir, 'output')
        self.logs_dir = os.path.join(self.execution_dir, 'logs')
        self.workspace_dir = os.path.join(self.execution_dir, 'workspace')


        for directory in (
        self.input_dir,
        self.output_dir,
        self.logs_dir,
        ):
            os.makedirs(directory, exist_ok=True)

        shutil.copytree(
                self.repository_root,
                self.workspace_dir,
                ignore=shutil.ignore_patterns(
                    ".venv",
                    "__pycache__",
                    ".pytest_cache",
                    "node_modules",
                    "runtime"
                    )
                )

        #self.workspace_dir.chown(1000, 1000)
        #self.output_dir.chown(1000, 1000)

        
        self.container = self.client.containers.run(
                image=self.image,
                command=["sleep", "infinity"],
                detach=True,
                working_dir="/workspace",
                volumes={
                    str(self.input_dir): {
                        "bind": "/input",
                        "mode": "ro",
                        },
                    str(self.output_dir): {
                        "bind": "/output",
                        "mode": "rw"
                        },
                    str(self.workspace_dir): {
                        "bind": "/workspace",
                        "mode": "rw"
                        }
                    },
                network_disabled=True,
                mem_limit="512m",
                nano_cpus=1_000_000_000,
                pids_limit=128,
                read_only=True,
                tmpfs={"/tmp": "rw,noexec,nosuid,size=64m"},
                user="1000:1000"
                )

        self.container.exec_run(["git", "config", "user.name", self.git_user_name])

        self.container.exec_run(["git", "config", "user.email", self.git_user_email])

        logging.info(f"[RUNTIME] Containter Started | Container ID: {self.container.id} | Execution ID: {execution_id}")


    def execute(self, action_artefact: ActionArtefact, permission_artefact: PermissionArtefact) -> ExecutionArtefact:

        if self.container is None:
            raise RuntimeError("Runtime has not been started")

        if action_artefact.execution_id != self.execution_id:
            raise RuntimeError("ActionArtefact Execution ID does not match active runtime Execution ID")

        self._write_json(os.path.join(self.execution_dir, "action.json"), action_artefact)
        
        self._write_json(os.path.join(self.execution_dir, "permission.json"), permission_artefact)

        started_at = datetime.now()

        if not permission_artefact.allowed:
            return self.get_blocked_execution_artefact(action_artefact, permission_artefact) 
        try:

            result =  self.container.exec_run(
                    cmd=["sh", "-lc", action_artefact.input],
                    workdir="/workspace",
                    stdout=True,
                    stderr=True
                    )
            exit_code = result.exit_code
            output = result.output.decode("utf-8", errors="replace")
            logs = self.container.logs().decode("utf-8", errors="replace")

            logging.info(f"[RUNTIME EXECUTE] Execution ID: {execution_id} | Input: {action_artefact.input} | Execution Output: {output}")

            if exit_code == 0:
                status = "SUCCESS"
                error = None
            else:
                status = "FAILED"
                error = output

            with open(os.path.join(logs_dir, "container.log"), "a", encoding="utf-8") as log_file:
                log_file.write(logs)

            params = {
                    "execution_id": action_artefact.execution_id,
                    "producer": action_artefact.producer,
                    "tool_input": action_artefact.input,
                    "permitted": permission_artefact.allowed,
                    "execution_status": status,
                    "termination_reason": "completed" if exit_code == 0 else "non zero exit code",
                    "exit_code": exit_code,
                    "started_at": started_at,
                    "finished_at": datetime.now(),
                    "image": self.image,
                    "input_path": str(self.input_dir),
                    "output_path": str(self.output_dir),
                    "workspace_path": str(self.workspace_dir),
                    "payload": None,
                    "error": error
                    }

            logging.info(f"[RUNTIME] Execution Complete | Input: {action_artefact.input} | Execution Status: {params.get('execution_status')} | Permission: {permission_artefact.allowed} | Execution ID: {action_artefact.execution_id}")

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, self.artefact_store, action_artefact.execution_id, action_artefact.producer)
            self._write_artefact(execution_artefact)

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
                    "input_path": str(self.input_dir),
                    "output_path": str(self.output_dir),
                    "workspace_path": str(self.workspace_dir),
                    "payload": None,
                    "error": {"type": type(e).__name__,
                              "message": str(e)}
                    }
            logging.exception(f"[RUNTIME EXCEPTION] Input: {action_artefact.input} | Execution Status: {params.get('execution_status')} | Permission: {permission_artefact.allowed} | Execution ID: {action_artefact.execution_id}")

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, self.artefact_store, action_artefact.execution_id, action_artefact.producer)
            self._write_artefact(execution_artefact)
        
        self._write_json(os.path.join(self.execution_dir, "execution.json"), execution_artefact)
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
        self._write_artefact(execution_artefact)
        return execution_artefact

    def finalise(self) -> str | None:

        if self.container is None:
            raise RuntimeError("Cannot finalise an inactive runtime")

        try:
            result = self.container.exec_run(
                    cmd=["sh", "-lc", (
                        "git add -A && "
                        "git diff --cached --quiet || "
                        "git commit -m 'agent execution'")],
                    workdir="/workspace"
                    )
            if result.exit_code != 0:
                output = result.output.decode("utf-8", errors="replace")
                raise RuntimeError(f"Could not finalise repository {output}")

            hash_result = self.container.exec_run(
                    cmd=["git", "rev-parse", "HEAD"],
                    workdir="/workspace"
                    )
            if hash_result.exit_code != 0:
                raise RuntimeError("Could not obtain final commit hash")
            commit_hash = hash_result.output.decode("utf-8").strip()

            logging.info(f"[RUNTIME FINALISE] Execution ID: {self.execution_id} | Commit: {commit_hash}")
            return commit_hash

        except Exception as e:
            logging.exception(f"[RUNTIME FINALISE EXCEPTION] Execution ID: {self.execution_id} | Exception: {str(e)}")
            raise

    def close(self):
        if self.container is None:
            return

        container_id = self.container.id

        try:
            logging.info(f"[RUNTIME CLOSE] Closing container | Container ID: {container_id} | Execution ID: {self.execution_id}")

            self.container.reload()

            if self.container.status == "running":
                self.container.stop(timeout=10)
        except Exception as e:
            logging.exception(f"[RUNTIME CLOSE EXCEPTION] Error stopping container | Container ID: {container_id} | Execution ID: {self.execution_id}")
        finally:
            try:
                self.container.remove(force=True)
                logging.info(f"[RUNTIME CLOSE FINALLY] Container removed | Container ID: {container_id} | Execution ID: {self.execution_id}")
            except Exception:
                logging.exception(f"[RUNTIME CLOSE FINALLY EXCEPTION] Error removing container | Container ID: {container_id} | Execution ID: {self.execution_id}")
            finally:
                self.container = None
                self.execution_id = None

    def _write_artefact(self, artefact: Artefact):
        artefact_path = os.path.join(self.execution_dir, "artefacts")
        os.makedirs(artefact_path, exist_ok=True)
        path = os.path.join(artefact_path, f"{artefact.artefact_id}.json")
        with open(path, 'w', encoding='utf-8') as path_file:
            path_file.write(artefact.to_json())


    @staticmethod
    def _write_json(path: str, artefact: Artefact):
        with open(path, 'a', encoding='utf-8', newline="") as f:
            f.write(artefact.to_json())
