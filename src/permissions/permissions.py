from enum import Enum, auto

class PermissionLevel(Enum):
    READ_ONLY = auto()
    READ_WRITE = auto()
    EXECUTE = auto()

class PermissionManager:
    
