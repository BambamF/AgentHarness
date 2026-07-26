from tool import Tool
import subprocess
import os

class BashTool(Tool):

    def __init__(self, command: str, exec_id: UUID, caller: UUID):
        self.name = "bash"
        self.description = "Run a shell command."
        self.input_schema = {
                "type": "object",
                "properties": {"command": {"type": string}},
                "required": ["command"]
                }
        self.command = command
        self.execution_id = exec_id
        self.caller = caller

    def run_bash(self, command: str) -> ExecutionArtefact:
        if any(blocked in command for blocked in PermissionManager.permission_levels.get(PermissionLevel.ALWAYS_BLOCK, [])):

            params = {"execution_status": "FAILED",
                      "termination_reason": "blocked",
                      "execution_id": self.execution_id,
                      "producer": self.caller}

            return ArtefactStore.builder(ExecutionArtefact, params)

        try:

            result = subprocess.run([self.command], shell=True, cwd=os.getcwd(), capture_output=True, text=True, timeout=120)
            payload = {"stdout": result.stdout if result.stdout else "(no output)", "stderr": result.stderr}
            params = {"execution_status": "SUCCESS",
                      "termination_reason": "completed",
                      "execution_id": self.execution_id,
                      "producer": self.caller,
                      "payload": payload}

            return ArtefactStore.builder(ExecutionArtefact, params)

        except subprocess.TimoutExpired:
            # handle cases where the command runs longer than 120s limit

            params = {"execution_status": "FAILED",
                      "termination_reason": "timeout",
                      "execution_id": self.execution_id,
                      "producer": self.caller}

            return ArtefactStore.builder(ExecutionArtefact, params)
        except Exception as e:
            # return any other execution errors as part of an execution artefact

            params = {"execution_status": "FAILED",
                      "termination_reason": "error",
                      "execution_id": self.execution_id,
                      "producer": self.caller,
                      "error": e
                      }

            return ArtefactStore.builder(ExecutionArtefact, params)
