from  dataclasses import dataclass
from enum import Enum, auto

class PermissionLevel(Enum):
    READ_ONLY = auto()
    READ_WRITE = auto()
    EXECUTE = auto()
    ALWAYS_BLOCK = auto()
