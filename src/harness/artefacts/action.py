from .artefacts import Artefact
from dataclasses import dataclass
from permissions/permissions import PermissionLevel

@dataclass(frozen=True)
class ActionArtefact(Artefact):
    provider: str
    intention: str
    required_permission: PermissionLevel
    dependencies: list[str]
    success_criteria: list[str]
