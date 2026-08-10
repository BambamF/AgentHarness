
from typing import List
from harness.artefacts.artefact_factory import ArtefactFactory
from harness.artefacts.execution import ExecutionArtefact
from tool import Tool
from uuid import UUID
from dataclasses import dataclass
from tool.snapshots import SNAPSHOTS
import os

@dataclass(frozen=True)
class RevertTool(Tool):
    def __init__(self):
        name = "revert"
        description = "Restore a file to its state before the last write call. Use when a write operation produced incorrect results."
        input_schema = {"type": "object",
                             "properties": {"path": {"type": "string"}},
                             "required": ["path"]}
        super.__init__(name, description, input_schema)

    def run(self, path: str, caller: str, execution_id: UUID, snapshots: SNAPSHOTS) -> ExecutionArtefact:
        return self.run_revert(path, caller, execution_id)

    def run_revert(self, path: str, caller: str, execution_id: UUID, snapshots: SNAPSHOTS) -> ExecutionArtefact:
        if path not in snapshots.all():
            payload = f"No snapshot for {path}"
        original_content = snapshots.pop(path)

        # If original content is none, the file didn't exist before the write
        if original_content is None:
            try:
                os.remove(path) # Revert by deleting the new file
                payload = f"Reverted: deleted {path} (it was a new file)"
            except Exception as e:
                caught_error = e
        else:
            # If the original content existed, write it back to the file
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                    payload = f"Reverted: restored content {original_content}"
            except Exception as e:
                caught_error = e

        params = {"execution_status": "SUCCESS" if payload else "FAILED",
                  "termination_reason": "completed" if original_content else "no original content",
                  "execution_id": execution_id,
                  "producer": caller, 
                  "payload": payload if payload else None,
                  "error": caught_error if caught_error else None}
                    
        execution_artefact = ArtefactFactory.builder(artefact_type=ExecutionArtefact, params=params)
        return execution_artefact
