from typing import List
from tools.tool import Tool
import subprocess
from uuid import UUID
from harness.artefacts.execution import ExecutionArtefact
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from permissions.permissions import PermissionLevel, PermissionManager
from harness.artefacts.action import ActionProvider
from dataclasses import dataclass

@dataclass(frozen=True)
class GitTool(Tool):
    name = "git"
    description = "Run a git command."
    input_schema = {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"]
                }
    @staticmethod
    def run(command: str, artefact_store: ArtefactStore, execution_id: UUID, caller: str) -> ExecutionArtefact:
        return run_git(command, artefact_store, execution_id, caller)
    
    @staticmethod
    def run_git(commmand: str, artefact_store: ArtefactStore, execution_id: UUID, caller: str) -> ExecutionArtefact:
        try:

            response = subprocess.run([command], capture_output=True, text=True, timeout=120)
            hash_response = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, timeout=120)

            payload = {"stdout": response.stdout, "stderr": response.stderr, "git_hash": hash_response.stdout}

            params = {"execution_status": "SUCCESS" if response.returncode == 0 else "FAILED",
                      "termination_reason": "completed" if response.returncode == 0 else "null return",
                      "execution_id": execution_id,
                      "producer": caller,
                      "payload": payload
                      }

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, artefact_store, execution_id, caller)
            return execution_artefact

        except subprocess.TimeoutExpired as e:
            
            params = {"execution_status": "FAILED",
                      "termination_reason": "timeout",
                      "execution_id": self.execution_id,
                      "producer": self.caller,
                      "error": e}

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, artefact_store, execution_id, caller)
            return execution_artefact

        except Exception as e:

            params = {"execution_status": "FAILED",
                      "termination_reason": "error",
                      "execution_id": self.execution_id,
                      "producer": self.caller,
                      "error": e}

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, artefact_store, execution_id, caller)
            return execution_artefact
