from enum import Enum, auto

class TerminationReason(Enum):
    SUCCESS = auto()
    MAX_ROUNDS_REACHED = auto()
    PERMISSION_DENIED = auto()
    EXECUTION_FAILURE = auto()
    EVALUATION_FAILURE = auto()
    USER_CANCELLED = auto()
    RUNTIME_ERROR = auto()
