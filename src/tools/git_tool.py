from typing import List
from .tool import Tool
import subprocess
from uuid import UUID
from ../harness/artefacts/execution import ExecutionArtefact
from ../harness/artefacts/artefact_store import ArtefactStore
from ../../permissions/permissions import PermissionLevel, PermissionManager

class GitTool(Tool):
<<<<<<< HEAD
<<<<<<< HEAD
    def __init__(self, command: str):
=======
    def __init__(self, command: str, caller: str):
>>>>>>> feat/implement-initialising-state
=======
    def __init__(self, command: str, exec_id: UUID, caller: str):
>>>>>>> feat/implement-initialising-state
        self.name = "git"
        self.description = "Run a git command."
        self.input_schema = {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": "command"
                }
<<<<<<< HEAD
        self.command = command
<<<<<<< HEAD
    
    def run(self):
=======
        self.caller = caller
    
    def run_git(self):
>>>>>>> feat/implement-initialising-state
        response = subprocess.run([self.command], capture_output=True, text=True)
        return response
=======
        self.execution_id = exec_id
        self.command = command
        self.caller = caller
    
    def run_git(self) -> ExecutionArtefact:
        if any(blocked in command for blocked in PermissionManager.permission_levels.get(PermissionLevel.ALWAYS_BLOCK, [])):
            return ArtefactStore.builder(ExecutionArtefact, execution_status="FAILED", termination_reason="blocked", exec_id=self.execution_id, caller=self.caller)
        try:
            response = subprocess.run([self.command], capture_output=True, text=True, timeout=120)
            hash_response = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, timeout=120)
            payload = {"stdout": response.stdout, "stderr": response.stderr, "git_hash": hash_response.stdout}
            return ArtefactStore.builder(ExecutionArtefact, execution_status="SUCCESS" if response.returncode == 0 else "FAILED", termination_reason="completed" if response.returncode == 0 else "null return", exec_id=self.execution_id, caller=self.caller, payload=payload)
        except subprocess.TimeoutExpired:
            return ArtefactStore.builder(ExecutionArtefact, execution_status="FAILED", termination_reason="timeout", exec_id=self.execution_id, caller=self.caller)
        except Exception as e:
            return ArtefactStore.builder(ExecutionArtefact, execution_status="FAILED", termination_reason="error", exec_id=self.execution_id, caller=caller, error=e)
>>>>>>> feat/implement-initialising-state
