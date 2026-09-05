from tools.tool import Tool
from typing import Dict, Any, List, Optional
import subprocess
from uuid import UUID
from harness.artefacts.execution import ExecutionArtefact
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from permissions.permissions import PermissionManager, PermissionLevel
from dataclasses import dataclass

try:
    import readline
except Exception as e:
    print(e)



@dataclass(frozen=True)
class ReadTool(Tool):
    name = "read"
    description = "Read a file and return numbered lines. Use when you need to inspect file content or reference specific line numbers. Returns up to 50,000 characters. Use start_line/end_line for large files."
    input_schema = {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "start_line": {"type": "integer"},
                    "end_line": {"type": "integer"}
                    },
                "required": ["path"]
                }

    @staticmethod
    def run(path: str, artefact_store: ArtefactStore, caller: str, execution_id: UUID, start_line: Optional[int] = None, end_line: Optional = None) -> ExecutionArtefact:
        return run_read(path, artefact_store, caller, execution_id, start_line, end_line)

    @staticmethod
    def run_read(path: str, artefact_store: ArtefactStore, caller: str, execution_id: UUID, start_line: Optional[int] = None, end_line: Optional = None) -> ExecutionArtefact:
        try:
            with open(path, 'r', encoding='utf-8', errors="replace") as f:
                lines = f.readlines()

            start_index = (start_line - 1) or 1
            end_index = end_line or len(lines)
            numbered_lines = "".join(f"{start_index + 1 + i:4d}\t{line}" for i, line in enumerate(lines[start_index:end_index]))

            params = {"execution_status": "SUCCESS" if numbered_lines else "FAILED",
                              "termination_reason": "completed" if numbered_lines else "null return",
                              "execution_id": execution_id,
                              "producer": caller,
                              "payload": numbered_lines}
                    
            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, artefact_store, execution_id, caller)
            return execution_artefact

        except Exception as e:
            params = {"execution_status": "FAILED",
                              "termination_reason": "error",
                              "execution_id": execution_id,
                              "producer": caller,
                              "error": e}

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, artefact_store, execution_id, caller)
            return execution_artefact

