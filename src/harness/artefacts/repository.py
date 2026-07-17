from dataclasses import dataclass
from .artefact import Artefact
from pathlib import Path
from .repository_node import RepositoryNode

@dataclass(frozen=True)
class RepositoryArtefact(Artefact):
    repository_root: str | Path
    commmit_hash: str
    topology: RepositoryNode
    dependency_graph: dict
    languages: list
    entry_points: list
