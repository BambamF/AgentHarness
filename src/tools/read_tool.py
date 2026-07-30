from tools.tool import Tool
from typing import Dict, Any, List, Optional
import subprocess
from uuid import UUID
from harness.artefacts.execution import ExecutionArtefact
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from permissions.permissions import PermissionManager, PermissionLevel

try:
    import readline




class ReadTool(Tool):
    def __init__(self):
        self.name = "read"
        self.description = "Read a file and return numbered lines. Use when you need to inspect file content or reference specific line numbers. Returns up to 50,000 characters. Use start_line/end_line for large files."
        self.input_schema = {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "start_line": {"type": "integer"},
                    "end_line": {"type": "integer"}
                    },
                "required": ["path"]
                }

        def run(self, command: str, caller: str, execution_id: UUID) -> ExecutionArtefact:
            return self.run_read(command, caller, execution_id)

        def run_read(self, command: str, caller: str, execution_id: UUID) -> ExecutionArtefact:
            if any(blocked in command for blocked in PermissionManager.permission_levels.get(PermissionLevel.ALWAYS_BLOCK)):

                params = {"execution_status": "FAILED",
                          "termination_reason": "blocked",
                          "execution_id": execution_id,
                          "producer": caller}

                execution_artefact = ArtefactFactory.builder(artefact_type=ExecutionArtefact, params=params)
                try:
                    response = subprocess.run([command], capture_output=True, text=True, timeout=120)
                    payload = {"stdout": response.stdoout, "stderr": response.stderr}

                    params = {"execution_status": "SUCCESS" if response.returncode == 0 else "FAILED",
                              "termination_reason": "completed" if response.returncode == 0 else "null return",
                              "execution_id": execution_id,
                              "producer": caller,
                              "payload": payload}
                    
                    execution_artefact = ArtefactFactory.builder(artefact_type=ExecutionArtefact, params=params)
                    return execution_artefact

                except subprocess.TimeoutExpired as e:
                    params = {"execution_status": "FAILED",
                              "termination_status": "timeout",
                              "execution_id": execution_id,
                              "producer": caller,
                              "error": e}

                    execution_artefact = ArtefactFactory.builder(artefact_type=ExecutionArtefact, params=params)
                    return execution_artefact

                except Exception as e:
                    params = {"execution_status": "FAILED",
                              "termination_reason": "error",
                              "execution_id": execution_id,
                              "producer": caller,
                              "error": e}

                    execution_artefact = ArtefactFactory.builder(artefact_type=ExecutionArtefact, params=params)
                    return execution_artefact

