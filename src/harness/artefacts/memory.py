from .artefact import Artefact
from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class MemoryArtefact(Artefact):
    memory_path: str
    topology_confidence: Dict[str, Any]
