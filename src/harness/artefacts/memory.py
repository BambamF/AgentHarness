from .artefact import Artefact
from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class MemoryArtefact(Artefact):
    memory_path: str
    topology_confidence: Dict[str, Any]
    topology: Dict[str, Any]
    known_facts: list[str]
    previous_decisions: list[str]
    relevant_history: list[str]
    compressed_context: list[str]
