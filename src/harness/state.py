from enum import Enum, auto

class HarnessState(Enum):
    INITIALISING = auto()
    REPO_ANALYSIS = auto()
    HYDRATING_MEMORY = auto()
    PLANNING = auto()
    GENERATING = auto()
    EVALUATING = auto()
    REFLECTING = auto()
    MEMORY_UPDATE = auto()
    TERMINATE = auto()

