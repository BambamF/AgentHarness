import os
from uuid import UUID
from typing import List
from tools.tool import Tool
import subprocess
from harness.artefacts.execution import ExecutionArtefact
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from permissions.permissions import PermissionManager, PermissionLevel
from dataclasses import dataclass

@dataclass(frozen=True)
class WriteTool(Tool):
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

    @staticmethod
    def run(path: str, content: str, artefact_store: ArtefactStore, caller: str, execution_id: UUID, snapshots: dict) -> ExecutionArtefact:
        return run_write(path, content, artefact_store, caller, execution_id, snapshots)

    @staticmethod
    def run_write(path: str, content: str, artefact_store: ArtefactStore, caller: str, execution_id: UUID, snapshots: dict) -> ExecutionArtefact:

        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    # A snapshot of the file and its contents before modification
                    snapshots[path] = f.read()
                termination_reason = "updated"
                execution_status = "SUCCESS"
            else:
                snapshots[path] = None
                termination_reason = "created"
                execution_status = "SUCCESS"

            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            payload = "File written successfully."
            params = {"execution_status": execution_status if execution_status else "FAILED",
                      "termination_reason": termination_reason if termination_reason else "null return",
                      "execution_id": execution_id,
                      "producer": caller,
                      "payload": payload,
                      "error": None}

            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, artefact_store, execution_id, caller)
            return execution_artefact

        except Exception as e:
            
            payload = None
            params = {"execution_status": "FAILED",
                      "termination_reason": "error",
                      "execution_id": execution_id,
                      "producer": caller,
                      "payload": None,
                      "error": e}
            
            execution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, artefact_store, execution_id, caller)
            return execution_artefact
