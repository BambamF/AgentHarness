from .artefact import Artefact
from dataclasses import dataclass
from permissions.permission_level import PermissionLevel
from enum import Enum, auto

@dataclass(frozen=True)
class ActionArtefact(Artefact):
    intention: str
    input: dict
    dependencies_length: int | None
    success_criteria: list[str]

class ActionProvider(Enum):
    AGENT=auto()
    SYSTEM=auto()
