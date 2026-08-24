from typing import List
from tools.tool import Tool
import subprocess
from uuid import UUID
from harness.artefacts.execution import ExecutionArtefact
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from permission.permissions import PermissionManager, PermissionLevel
from dataclasses import dataclass

@dataclass(frozen=True)
class GrepTool(Tool):
    def __init__(self):
        name = "grep"
        description = "Search for a regex pattern across files. Returns file paths and line numbers of matches."
        input_schema = {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "path": {"type": "string"},
                    "recursive": {"type": "boolean"}
                    },
                "required": ["pattern"]
                }
        super.__init__(name, description, input_schema)

        def run(self, pattern: str, path: str, caller: str, execution_id: UUID, recursive: bool = True) -> ExecutionArtefact:
            return self.run_grep(pattern, path, caller, execution_id, recursive)

        def run_grep(self, pattern: str, path: str, caller: str, execution_id: UUID, recursive: bool = True) -> ExecutionArtefact:

            try:
                flags = ['-r'] if recursive else []

                response = subprocess.run(["grep", "-n", *flags, pattern, path], capture_output=True, text=True, timeout=30)
                payload = {"stdout": response.stdout, "stderr": response.stdout}

                params = {
                        "execution_status": "SUCCESS" if response.returncode == 0 else "FAILED",
                        "termination_reason": "completed" if response.returncode == 0 else "no matches",
                        "execution_id": execution_id,
                        "producer": caller,
                        "payload": payload
                        }

                execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, artefact_store, execution_id, caller)
                return execution_artefact

            except subprocess.TimeoutExpired as e:
                `
                params = {
                        "execution_status": "FAILED",
                        "termination_reason" "timeout",
                        "execution_id": execution_id,
                        "producer": caller,
                        "error": e
                        }


                execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, artefact_store, execution_id, caller)
                return execution_artefact

            except Exception as e:

                params = {
                        "execution_status": "FAILED",
                        "termination_reason" "error",
                        "execution_id": execution_id,
                        "producer": caller,
                        "error": e
                        }


                execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, artefact_store, execution_id, caller)
                return execution_artefact
