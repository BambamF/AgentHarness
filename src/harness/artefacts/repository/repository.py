from dataclasses import dataclass
from ..artefact import Artefact
from pathlib import Path
from typing import Dict, Any

@dataclass(frozen=True)
class RepositoryArtefact(Artefact):
    repository_root: str | Path
    commit_hash: str
    topology: Dict[str, Any]
    dependency_graph: dict
    languages: list
    entry_points: list
    config_files: list
