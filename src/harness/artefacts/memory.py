from .artefact import Artefact
from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class MemoryArtefact(Artefact):
    memory_path: str
    topology_confidence: Dict[str, Any]
    topology: Dict[str, Any]
    typed_topology: Dict[str, Any]
    known_facts_path: str
    previous_decisions_path: str
    relevant_history_path: str
    compressed_context_path: str
