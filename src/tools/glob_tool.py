from typing import List
from tools.tool import Tool
from uuid import UUID
from harness.artefacts.execution import ExecutionArtefact
from harness.artefacts.artefact_factory import ArtefactFactory
from harness.artefacts.artefact_store import ArtefactStore
from permissions.permissions import PermissionManager, PermissionLevel
from dataclasses import dataclass
import glob as _glob

@dataclass(frozen=True)
class GlobTool:
    def __init__(self):
        name = "glob"
        description = "Find files matching a glob pattern, e.g. '**/*.py'. Returns sorted list of matching paths."
        input_schema = {"type": "object",
                             "properties": {"pattern": {"type": "string"}},
                             "required": ["pattern"]
                             }
        super.__init__(name, description, input_schema)

    def run(self, pattern: str, artefact_store: ArtefactStore, caller: str, execution_id: UUID) -> ExecutionArtefact:
        return self.run_glob(pattern, caller, execution_id)

    def run_glob(self, pattern: str, artefact_store: ArtefactStore, caller: str,  execution_id: UUID) -> ExecutionArtefact:

        matches = _glob.glob(pattern, recursive=True)
        
        params = {"execution_status": "SUCCESS" if matches else "FAILED",
                  "termination_reason": "completed" if matches else "no matches",
                  "execution_id": execution_id,
                  "producer": caller,
                  "payload": "\n".join(sorted(matches)[:200])}

        excution_artefact = ArtefactFactory.builder(ExecutionArtefact, params, artefact_store, execution_id, caller)
        return execution_artefact
