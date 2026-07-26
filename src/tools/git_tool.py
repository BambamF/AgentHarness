from typing import List
from .tool import Tool
import subprocess
from uuid import UUID
from ../harness/artefacts/execution import ExecutionArtefact
from ../harness/artefacts/artefact_store import ArtefactStore
from ../../permissions/permissions import PermissionLevel, PermissionManager

class GitTool(Tool):
    def __init__(self, command: str, exec_id: UUID, caller: str):
        self.name = "git"
        self.description = "Run a git command."
        self.input_schema = {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": "command"
                }
        self.execution_id = exec_id
        self.command = command
        self.caller = caller
    
    def run_git(self) -> ExecutionArtefact:
        if any(blocked in command for blocked in PermissionManager.permission_levels.get(PermissionLevel.ALWAYS_BLOCK, [])):

            params = {"execution_status": "FAILED",
                      "termination_reason": "blocked",
                      "execution_id": self.execution_id,
                      "producer": self.caller}

            return ArtefactStore.builder(ExecutionArtefact, params)

        try:

            response = subprocess.run([self.command], capture_output=True, text=True, timeout=120)
            hash_response = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, timeout=120)

            payload = {"stdout": response.stdout, "stderr": response.stderr, "git_hash": hash_response.stdout}

            params = {"execution_status": "SUCCESS" if response.returncode == 0 else "FAILED",
                      "termination_reason": "completed" if response.returncode == 0 else "null return",
                      "execution_id": self.execution_id,
                      "producer": self.caller,
                      "payload": payload
                      }

            return ArtefactStore.builder(ExecutionArtefact, params)

        except subprocess.TimeoutExpired as e:
            
            params = {"execution_status": "FAILED",
                      "termination_reason": "timeout",
                      "execution_id": self.execution_id,
                      "producer": self.caller,
                      "error": e}

            return ArtefactStore.builder(ExecutionArtefact, params)

        except Exception as e:

            params = {"execution_status": "FAILED",
                      "termination_reason": "error",
                      "execution_id": self.execution_id,
                      "producer": self.caller,
                      "error": e}

            return ArtefactStore.builder(ExecutionArtefact, params)
