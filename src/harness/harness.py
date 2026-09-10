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
from agents.generate import GenerationManager
from runtime.runtime import RuntimeManager
from agents.reflect import ReflectionManager
import os

class Harness:
    """
    Provides methods to initialise the harness, transition the harness through the defined states and terminate the process.
    """
    def __init__(self, agent, model, memory_path, memory_manager: MemoryManager, runtime_manager: RuntimeManager, config_path, charter_path, repository_root, messages: List[Dict[str, Any]], permission_manager: PermissionManager, generation_manager: GenerationManager, reflection_manager: ReflectionManager, artefact_store: ArtefactStore, execution_id: UUID):
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
        self.runtime_manager = runtime_manager
        self.transitions: Dict[HarnessState, Callable] = {HarnessState.INITIALISING: self._initialise,
                           HarnessState.REPO_ANALYSIS: self._analyse_repo,
                           HarnessState.HYDRATING_MEMORY: self._hydrate_memory,
                           HarnessState.PLANNING: self._create_plan,
                           HarnessState.GENERATING: self._generate,
                           HarnessState.REFLECTING: self._reflect,
                           HarnessState.MEMORY_UPDATE: self._update_memory,
                            HarnessState.TERMINATE: self._terminate}

        self.permission_manager = permission_manager
        self.generation_manager = generation_manager
        self.reflection_manager = reflection_manager
        self.ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.tools_dir = os.path.join(self.ROOT_DIR, 'src/tools')
        self.workspace = os.path.join(self.repository_root,"runtime", "executions", str(execution_id), "workspace")

    def run(self):
        """
        Runs the orchestration process for the harness state transitions
        """

        # Initialises the state machine
        self.runtime_manager.start(self.execution_id)

        # State transition run
        try:

            # State loop
            while self.state != HarnessState.TERMINATE:
                for transition, handler in self.transitions.items():
                    self.state = transition
                    handler()

            # Degrades the runtime process gracefully       
            self.runtime_manager.finalise()
        finally:

            # Closes the runtime environment
            self.runtime_manager.close()

    def _initialise(self):
        """
        Initialises the state machine
        """

        # Sets the harness context
        self.context = HarnessContext(self.memory_path, self.config_path, self.workspace, self.artefact_store)
        
        
    def _analyse_repo(self):
        """
        Launches the Repo Analysis state via repository scan
        """
        self.context.scan_repository(self.execution_id)

    def _hydrate_memory(self):
        """
        Hydrates the session memory from cache
        """
        self.context.scan_memory(execution_id=self.execution_id, memory_manager=self.memory_manager)
        self.memory_manager.hydrate_memory(execution_id=self.execution_id)

    def _create_plan(self):
        """
        Creates a plan for the session via the planner
        """
        self.planner = Planner(self.agent, self.model, self.artefact_store, self.execution_id)
        self.plan = self.planner.create_plan(self.execution_id)

    def _generate(self):
        """
        Starts the generation loop
        """
        self.generation_manager.generate(self.tools_dir)

    def _reflect(self):
        """
        Launches the Reflection state
        """
        self.reflection_manager.reflect()

    def _update_memory(self):
        """
        Persists the session memory for future sessions
        """
        self.memory_manager.update_memory(self.execution_id)

    def _terminate(self):
        """
        Indicates session termination to the user
        """
        print("Terminating...")
