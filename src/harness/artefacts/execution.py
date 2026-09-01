from harness.artefacts.artefact import Artefact
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class ExecutionArtefact(Artefact):
    tool_input: str
    permitted: str
    execution_status: str
    termination_reason: str
    exit_code: int
    started_at: datetime
    finished_at: datetime
    image: str
    input_path: str
    output_path: str
    workspace_path: str
    payload: str | None
    error: str | None


