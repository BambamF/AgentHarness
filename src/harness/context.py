from .state import HarnessState

class HarnessContext:
    def __init__(self, log_handle, config, artefacts: dict[str, Artefact]):
        self.execution_id = 0
        self.current_state = HarnessState.INITIALISING
        self.current_round = 0
        self.artefact_store = artefacts
        self.logger_handle = log_handle
        self.config = config
        self.termination_reason = None
