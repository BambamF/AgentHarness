from enum import Enum, auto

class HarnessState(Enum):
    INITIALISING = auto()
    REPO_ANALYSIS = auto()
    HYDRATING_MEMORY = auto()
    PLANNING = auto()
    GENERATING = auto()
    PERMISSIONS = auto()
    EXECUTING = auto()
    EVALUATING = auto()
    REFLECTING = auto()
    MEMORY_UPDATE = auto()
    TERMINATING = auto()

