from tool import Tool
import subprocess
import os
from uuid import UUID
from ../harness/artefacts/artefact import ExecutionArtefact
from ../../permissions/permissions import PermissionLevel, PermissionManager

class BashTool(Tool):

    def __init__(self, command: str, exec_id: UUID, caller: str):
        self.name = "bash"
        self.description = "Run a shell command."
        self.input_schema = {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"]
                }
        self.command = command
        self.execution_id = exec_id
        self.caller = caller

    def run_bash(self, command: str) -> ExecutionArtefact:
        if any(blocked in command for blocked in PermissionManager.permission_levels.get(PermissionLevel.ALWAYS_BLOCK, [])):
            return ArtefactStore.builder(ExecutionArtefact, execution_status="FAILED", termination_reason="blocked", exec_id=self.execution_id, caller=self.caller)
        try:
            result = subprocess.run([self.command], shell=True, cwd=os.getcwd(), capture_output=True, text=True, timeout=120)
            payload = {"stdout": result.stdout if result.stdout else "(no output)", "stderr": result.stderr}
            return ArtefactStore.builder(ExecutionArtefact, execution_status="SUCCESS", termination_status="completed", exec_id=self.execution_id, caller=self.caller, payload=payload)
        except subprocess.TimoutExpired:
            # handle cases where the command runs longer than 120s limit
            return ArtefactStore.builder(ExecutionArtefact, execution_status="FAILED", termination_reason="timeout", exec_id=self.execution_id, caller=self.caller)
        except Exception as e:
            # return any other execution errors as part of an execution artefact
            return ArtefactStore.builder(ExecutionArtefact, execution_status="FAILED", termination_status="error", exec_id=self.execution_id, caller=self.caller, error=e)
