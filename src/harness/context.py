from .state import HarnessState
from uuid import UUID
from logging import logger

class HarnessContext:
    def __init__(self, log_handle: logger, config: str | Path, exec_id: UUID, artefact_store: ArtefactStore):
        self.execution_id = exec_id
        self.current_state = HarnessState.INITIALISING
        self.current_round = 0
        self.artefact_store = artefact_store
        self.logger_handle = log_handle
        self.config = config
        self.termination_reason = None

    def increment_round(self):
        self.current_round += 1
