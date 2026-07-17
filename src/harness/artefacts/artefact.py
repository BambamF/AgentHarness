from dataclasses import dataclass
from .state import HarnessState
from typing import Any
from uuid import UUID

@dataclass(frozen=True)
class Artefact:
    artefact_id: UUID
    execution_id: UUID
    producer: str
    producer_state: HarnessState
    timestamp: float
    confidence: float
    metadata: Any
