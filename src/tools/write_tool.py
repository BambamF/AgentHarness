import os
from uuid import UUID
from typing import List
from tool import Tool
import subprocess
from harness.artefacts.execution import ExecutionArtefact
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from permissions.permissions import PermissionManager, PermissionLevel
from dataclasses import dataclass
from tools.snapshots import SNAPSHOTS

@dataclass(frozen=True)
class WriteTool(Tool):
    def __init__(self):
        name = "write"
        description = "Write content to a file. Automatically snapshots the previous content so you can revert. Creates parent directories if needed."
        input_schema = {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                    },
                "required": ["path", "content"]
                }
        super.__init__(name, description, input_schema)

    def run(self, path: str, content: str, caller: str, execution_id: UUID, snapshots: SNAPSHOTS) -> ExecutionArtefact:
        return self.run_write(path, content, caller, execution_id, snapshots)

    def run_write(self, path: str, content: str, caller: str, execution_id: UUID, snapshots: SNAPSHOTS) -> ExecutionArtefact:

        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    # A snapshot of the file and its contents before modification
                    snapshots.add(execution_id, path, f.read())
                termination_reason = "updated"
                execution_status = "SUCCESS"
            else:
                snapshots.add(execution_id, path, None)
                termination_reason = "created"
                execution_status = "SUCCESS"

            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            payload = "File written successfully."
            params = {"execution_status": execution_status if execution_status else "FAILED",
                      "termination_reason": termination_reason if termination_reason else "null return",
                      "execution_id": execution_id,
                      "producer": caller,
                      "payload": payload}

            execution_artefact = ArtefactFactory.builder(artefact_type=ExecutionArtefact, params=params)
            return execution_artefact

        except Exeception as e:
            
            params = {"execution_status": "FAILED",
                      "termination_reason": "error",
                      "execution_id": execution_id,
                      "producer": caller,
                      "error": e}
            
            execution_artefact = ArtefactFactory.builder(artefact_type=ExecutionArtefact, params=params)
            return execution_artefact
