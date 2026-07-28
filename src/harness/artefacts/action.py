from .artefact import Artefact
from dataclasses import dataclass
from permissions.permissions import PermissionLevel
from enum import Enum, auto

@dataclass(frozen=True)
class ActionArtefact(Artefact):
    provider: str
    intention: str
    required_permission: PermissionLevel
    dependencies: list[str] | None
    success_criteria: list[str]

class ActionProvider(Enum):
    AGENT=auto()
    SYSTEM=auto()
