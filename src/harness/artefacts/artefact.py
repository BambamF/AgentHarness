from dataclasses import dataclass
from ..state import HarnessState
from typing import Any
from uuid import UUID

@dataclass(frozen=True)
class Artefact:
    artefact_id: UUID
    execution_id: UUID
    producer: str
    timestamp: float
    caller: str
    metadata: Any
    payload: Any

    def _to_dict(self):
        return {"artefact_id":self.artefact_id,
                "execution_id": self.execution_id,
                "producer": self.producer,
                "timestamp": self.timestamp,
                "caller": self.caller,
                "metadata": self.metadata,
                "payload": self.payload}
