from typing import List
from tool import Tool
import subprocess
from uuid import UUID
from harness.artefacts.execution import ExecutionArtefact
from harness.artefacts.artefact_factory import ArtefactFactory
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

    def run(self, pattern: str, caller: str, execution_id: UUID) -> ExecutionArtefact:
        return self.run_glob(pattern, caller, execution_id)

    def run_glob(self, pattern: str, caller: str,  execution_id: UUID) -> ExecutionArtefact:

        matches = _glob.glob(pattern, recursive=True)
        
        params = {"execution_status": "SUCCESS" if matches else "FAILED",
                  "termination_reason": "completed" if matches else "no matches",
                  "execution_id": execution_id,
                  "producer": caller,
                  "payload": "\n".join(sorted(matches)[:200])}

            excution_artefact = ArtefactFactory.builder(artefact_type=ExecutionArtefact, params=params)
            return execution_artefact
