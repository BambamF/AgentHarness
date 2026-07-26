from tool import Tool
import subprocess
import os
<<<<<<< HEAD
<<<<<<< HEAD

class BashTool(Tool):

    def __init__(self, command: str):
=======
from uuid import UUID
from ../harness/artefacts/artefact import Artefact
from ../harness/artefacts/artefact import ExecutionArtefact
=======
from uuid import UUID
from ../harness/artefacts/artefact import ExecutionArtefact
from ../../permissions/permissions import PermissionLevel, PermissionManager
>>>>>>> feat/implement-initialising-state

class BashTool(Tool):

<<<<<<< HEAD
    def __init__(self, command: str, exec_id: UUID, caller: str):
<<<<<<< HEAD
>>>>>>> feat/implement-initialising-state
=======
>>>>>>> feat/implement-initialising-state
=======
    def __init__(self, command: str, exec_id: UUID, caller: UUID):
>>>>>>> feat/implement-initialising-state
        self.name = "bash"
        self.description = "Run a shell command."
        self.input_schema = {
                "type": "object",
<<<<<<< HEAD
                "properties": {"command": {"type": string}},
                "required": ["command"]
                }
        self.command = command
<<<<<<< HEAD

    def run_bash(self, command: str):
        if any(blocked in command for blocked in PermissionManager.permission_levels.get(PermissionLevel.ALWAYS_BLOCKED, [])):
            return ArtefactStore.builder(ExecutionArtefact())
        result = subprocess.run([self.command], shell=True, cwd=os.getcwd(), capture_output=True, text=True, timeout=120)
=======
=======
                "properties": {"command": {"type": "string"}},
                "required": ["command"]
                }
        self.command = command
>>>>>>> feat/implement-initialising-state
        self.execution_id = exec_id
        self.caller = caller

    def run_bash(self, command: str) -> ExecutionArtefact:
<<<<<<< HEAD
<<<<<<< HEAD
        if any(blocked in command for blocked in PermissionManager.permission_levels.get(PermissionLevel.ALWAYS_BLOCKED, [])):
            return ArtefactStore.builder(ExecutionArtefact, execution_status="FAILED", termination_reason="blocked", exec_id=self.execution_id, caller=self.caller)
        try:
            result = subprocess.run([self.command], shell=True, cwd=os.getcwd(), capture_output=True, text=True, timeout=120)
            output = (result.stdout + result.stderr).strip()
            return output[:50000] if output else "(no output)"
=======
=======

>>>>>>> feat/implement-initialising-state
        if any(blocked in command for blocked in PermissionManager.permission_levels.get(PermissionLevel.ALWAYS_BLOCK, [])):

            params = {"execution_status": "FAILED",
                      "termination_reason": "blocked",
                      "execution_id": self.execution_id,
                      "producer": self.caller}

            return ArtefactStore.builder(ExecutionArtefact, params)

        try:

            result = subprocess.run([self.command], shell=True, cwd=os.getcwd(), capture_output=True, text=True, timeout=120)
            payload = {"stdout": result.stdout if result.stdout else "(no output)", "stderr": result.stderr}
<<<<<<< HEAD
            return ArtefactStore.builder(ExecutionArtefact, execution_status="SUCCESS", termination_status="completed", exec_id=self.execution_id, caller=self.caller, payload=payload)
>>>>>>> feat/implement-initialising-state
=======

            params = {"execution_status": "SUCCESS",
                      "termination_reason": "completed",
                      "execution_id": self.execution_id,
                      "producer": self.caller,
                      "payload": payload}

            return ArtefactStore.builder(ExecutionArtefact, params)

>>>>>>> feat/implement-initialising-state
        except subprocess.TimoutExpired:
            # handle cases where the command runs longer than 120s limit

            params = {"execution_status": "FAILED",
                      "termination_reason": "timeout",
                      "execution_id": self.execution_id,
                      "producer": self.caller}

            return ArtefactStore.builder(ExecutionArtefact, params)
        except Exception as e:
            # return any other execution errors as part of an execution artefact
<<<<<<< HEAD
<<<<<<< HEAD
            return ArtefactStore.builder(ExecutionArtefact, execution_status="FAILED", termination_status="error", exec_id=self.execution_id, caller=self.caller)
>>>>>>> feat/implement-initialising-state
=======
            return ArtefactStore.builder(ExecutionArtefact, execution_status="FAILED", termination_status="error", exec_id=self.execution_id, caller=self.caller, error=e)
>>>>>>> feat/implement-initialising-state
=======

            params = {"execution_status": "FAILED",
                      "termination_reason": "error",
                      "execution_id": self.execution_id,
                      "producer": self.caller,
                      "error": e
                      }

            return ArtefactStore.builder(ExecutionArtefact, params)
>>>>>>> feat/implement-initialising-state
