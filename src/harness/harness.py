from .state import HarnessState
from .context import HarnessContext
from ../prompt/prompt_handler import PromptHandler
from ../permissions/permissions import PermissionManager
from .artefacts/artefact_store import ArtefactStore

class Harness:
    def __init__(self, agent, memory, planner, runtime, evaluator, prompt: PromptArtefact, logger: logging.logger, permission_manager: PermissionManager, artefact_store: ArtefactStore):
        self.agent = agent
        self.prompt = prompt
        self.memory = memory
        self.planner = planner
        self.runtime = runtime
        self.evaluator = evaluator
        self.logger = logger
        self.exec_id_history = []
        self.state = HarnessState.INITIALISING
        self.artefact_store = artefact_store
        self.transitions: Dict[HarnessState, Callable] = {self.state.INITIALISING: self._initialise,
                            self.state.REPO_ANALYSIS: self._analyse_repo,
                            self.state.HYDRATING_MEMORY: self._hydrate_memory,
                            self.state.PLANNING: self._create_plan,
                            self.state.GENERATING: self._generate,
                            self.state.PERMISSIONS: self._run_permissions,
                            self.state.EXECUTING: self._execute,
                            self.state.REFLECTING: self._reflect,
                            self.state.MEMORY_UPDATE: self._update_memory,
                            self.state.TERMINATE: self._terminate}

        self.permission_manager = permission_manager

    def run(self):
        pass        

    def _initialise(self):
        
        context = HarnessContext(logger, config, uuid.uuid5(), artefact_store)
