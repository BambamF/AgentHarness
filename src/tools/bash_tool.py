from tool import Tool
import subprocess
import os
from ..harness.artefacts.execution_artefact import ExecutionArtefact
from ..harness.artefacrs.artefact_store import ArtefactStore
from ..harness.artefacrs.artefact_factory import ArtefactFactory

class BashTool(Tool):

    def __init__(self, command: str):
        self.name = "bash"
        self.description = "Run a shell command."
        self.input_schema = {
                "type": "object",
                "properties": {"command": {"type": string}},
                "required": ["command"]
                }

    def run(command: str):
        return run_bash(command)


    def run_bash(self, command: str) -> ExecutionArtefact:
        if any(blocked in command for blocked in PermissionManager.permission_levels.get(PermissionLevel.ALWAYS_BLOCK, [])):

            params = {"execution_status": "FAILED",
                      "termination_reason": "blocked",
                      "execution_id": self.execution_id,
                      "producer": self.caller}

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params)
            ArtefactStore.add(execution_artefact)

        try:

            result = subprocess.run([self.command], shell=True, cwd=os.getcwd(), capture_output=True, text=True, timeout=120)
            payload = {"stdout": result.stdout if result.stdout else "(no output)", "stderr": result.stderr}
            params = {"execution_status": "SUCCESS",
                      "termination_reason": "completed",
                      "execution_id": self.execution_id,
                      "producer": self.caller,
                      "payload": payload}

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params)
            ArtefactStore.add(execution_artefact)

        except subprocess.TimoutExpired:
            # handle cases where the command runs longer than 120s limit

            params = {"execution_status": "FAILED",
                      "termination_reason": "timeout",
                      "execution_id": self.execution_id,
                      "producer": self.caller}

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params)
            ArtefactStore.add(execution_artefact)
        except Exception as e:
            # return any other execution errors as part of an execution artefact

            params = {"execution_status": "FAILED",
                      "termination_reason": "error",
                      "execution_id": self.execution_id,
                      "producer": self.caller,
                      "error": e
                      }

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params)
            ArtefactStore.add(execution_artefact)
