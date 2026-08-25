from tools.tool import Tool
import subprocess
import os
from harness.artefacts.execution import ExecutionArtefact
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class BashTool(Tool):

    name = "bash"
    description = "Run a shell command."
    input_schema = {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"]
                }

    def run(command: str) -> ExecutionArtefact:
        return run_bash(command)


    def run_bash(command: str, artefact_store: ArtefactStore, execution_id: UUID, caller: str) -> ExecutionArtefact:
        if any(blocked in command for blocked in PermissionManager.permission_levels.get(PermissionLevel.ALWAYS_BLOCK, [])):

            params = {"execution_status": "FAILED",
                      "termination_reason": "blocked",
                      "execution_id": execution_id,
                      "producer": caller}

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, artefact_store, execution_id, caller)
            return execution_artefact

        try:

            result = subprocess.run([command], shell=True, cwd=os.getcwd(), capture_output=True, text=True, timeout=120)
            payload = {"stdout": result.stdout if result.stdout else "(no output)", "stderr": result.stderr}
            params = {"execution_status": "SUCCESS",
                      "termination_reason": "completed",
                      "execution_id": execution_id,
                      "producer": caller,
                      "payload": payload}

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, artefact_store, execution_id, caller)
            return execution_artefact

        except subprocess.TimoutExpired:
            # handle cases where the command runs longer than 120s limit

            params = {"execution_status": "FAILED",
                      "termination_reason": "timeout",
                      "execution_id": execution_id,
                      "producer": caller}

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, artefact_store, execution_id, caller)
            return execution_artefact
        except Exception as e:
            # return any other execution errors as part of an execution artefact

            params = {"execution_status": "FAILED",
                      "termination_reason": "error",
                      "execution_id": execution_id,
                      "producer": caller,
                      "error": e
                      }

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, artefact_store, execution_id, caller)
            return execution_artefact
