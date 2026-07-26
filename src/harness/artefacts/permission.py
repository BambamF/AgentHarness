from dataclasses import dataclass
from artefact import Artefact

@dataclass(frozen=True)
class PermissionArtefact(Artefact):
    allowed: bool
    reason: str
