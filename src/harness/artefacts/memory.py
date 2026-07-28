from .artefact import Artefact
from dataclasses import dataclass

@dataclass(frozen=True)
class MemoryArtefact(Artefact):
    memory_path: str
