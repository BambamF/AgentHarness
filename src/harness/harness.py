from .state import HarnessState
from .context import HarnessContext
from prompts.prompt_handler import PromptHandler
from permissions.permissions import PermissionManager
from .artefacts.artefact_store import ArtefactStore
from memory.memory import MemoryManager
from planner.planner import Planner
from .artefacts.action import ActionProvider
import logging
from typing import List, Dict, Any, Callable
from agents.generation_manager import GenerationManager

class Harness:
    def __init__(self, agent, model, memory_path, memory_manager: MemoryManager, config_path, charter_path, repository_root, messages: List[Dict[str, Any]], permission_manager: PermissionManager, generation_manager: GenerationManager, artefact_store: ArtefactStore, execution_id: UUID):
        self.agent = agent
        self.model = model
        self.memory_path = memory_path
        self.charter_path = charter_path
        self.repository_root = repository_root
        self.execution_id = execution_id
        self.config_path = config_path
        self.state = HarnessState.INITIALISING
        self.artefact_store = artefact_store
        self.memory_manager = memory_manager
        self.transitions: Dict[HarnessState, Callable] = {HarnessState.INITIALISING: self._initialise,
                            HarnessState.REPO_ANALYSIS: self._analyse_repo,
                            HarnessState.HYDRATING_MEMORY: self._hydrate_memory,
                            HarnessState.PLANNING: self._create_plan,
                            HarnessState.GENERATING: self._generate,
                            HarnessState.EVALUATING: self._evaluate,
                           # HarnessState.REFLECTING: self._reflect,
                           # HarnessState.MEMORY_UPDATE: self._update_memory,
                            HarnessState.TERMINATE: self._terminate}

        self.permission_manager = permission_manager
        self.generation_manager = generation_manager
        self.ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.tools_dir = os.path.join(self.ROOT_DIR, 'src/tools')

    def run(self):
        while self.state != HarnessState.TERMINATE:
            for transition, handler in self.transitions.items():
                self.state = transition
                handler()

    def _initialise(self):
        self.context = HarnessContext(self.memory_path, self.config_path, self.repository_root, self.artefact_store)
        
        
    def _analyse_repo(self):
        self.context.scan_repository(self.execution_id)

    def _hydrate_memory(self):
        self.context.scan_memory(execution_id=self.execution_id, memory_manager=self.memory_manager)
        self.memory_manager.hydrate_memory(execution_id=self.execution_id)

    def _create_plan(self):
        self.planner = Planner(self.agent, self.model, self.artefact_store, self.execution_id)
        self.plan = self.planner.create_plan(self.execution_id)

    def _generate(self):
        self.generation_manager.generate(self.tools_dir)


    def _evaluate(self):
        pass

    def _reflect(self):
        pass

    def _update_memory(self):
        pass

    def _terminate(self):
        print("Terminating...")
