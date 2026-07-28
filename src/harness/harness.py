from .state import HarnessState
from .context import HarnessContext
from prompts.prompt_handler import PromptHandler
from permissions.permissions import PermissionManager
from .artefacts.artefact_store import ArtefactStore
from .artefacts.plan import Planner
from .artefacts.action import ActionProvider
import logging
from typing import List, Dict, Any, Callable
# from tools.tool_map import ToolMap

class Harness:
    def __init__(self, agent, memory_path, config_path, charter_path, repository_root, messages: List[Dict[str, Any]], planner: Planner, prompt_artefact: PromptArtefact, permission_manager: PermissionManager, artefact_store: ArtefactStore):
        self.agent = agent
        self.prompt_artefact = prompt_artefact
        self.memory_path = memory_path
        self.messages = messages
        self.charter_path = charter_path
        self.repository_root = repository_root
        self.config_path = config_path
        self.state = HarnessState.INITIALISING
        self.artefact_store = artefact_store
        self.transitions: Dict[HarnessState, Callable] = {HarnessState.INITIALISING: self._initialise,
                            HarnessState.REPO_ANALYSIS: self._analyse_repo,
                            HarnessState.HYDRATING_MEMORY: self._hydrate_memory,
                           # HarnessState.PLANNING: self._create_plan,
                           # HarnessState.GENERATING: self._generate,
                           # HarnessState.PERMISSIONS: self._run_permissions,
                           # HarnessState.EXECUTING: self._execute,
                           # HarnessState.REFLECTING: self._reflect,
                           # HarnessState.MEMORY_UPDATE: self._update_memory,
                            HarnessState.TERMINATE: self._terminate}

        self.permission_manager = permission_manager
        self.DEFAULT_SYSTEM = f"You are a coding agent at {self.repository_root}. Use tools to solve tasks, Act, don't explain."

    def run(self):
        while self.state != HarnessState.TERMINATE:
            for harness_state in self.transitions.keys():
                self.state = harness_state
                self.transitions[harness_state]

    def _initialise(self):
        execution_id = uuid.uuid5()
        self.context = HarnessContext(self.memory_path, self.config_path, self.repository_root, execution_id, self.artefact_store)
        
        
    def _analyse_repo(self):
        self.context.scan_repository()

    def _hydrate_memory(self):
        self.context.scan_memory()

    def _create_plan(self):
        self.plan = planner.create_plan(self.artefact_store)

    def _generate(self):
        response = agent.messages.create(
                model=self.MODEL,
                system=self.DEFAULT_SYSTEM,
                messages=self.messages,
                max_tokens=8000
                )
        self.messages.append({"role": ActionProvider.SYSTEM, "content": response.content})

    def _run_permissions(self):
        self.permission_manager.get_permission(ArtefactStore.latest())

    def _execute(self):
        pass

    def _reflecting(self):
        pass

    def _update_memory(self):
        pass

    def _terminate(self):
        pass
