from artefact import Artefact
from dataclasses import dataclass

@dataclass(frozen=True)
class ExecutionArtefact(Artefact):
    execution_status: str
    termination_reason: str
    error: Exception | None


