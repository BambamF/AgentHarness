from .state import HarnessState
from .context import HarnessContext
import argparse
from typing import Dict, Callable

class Harness:
    def __init__(self, agent, prompt, memory, planner, runtime, evaluator, logger, permission_manager):
        self.agent = agent
        self.prompt = prompt
        self.memory = memory
        self.planner = planner
        self.runtime = runtime
        self.evaluator = evaluator
        self.logger = logger
 
        self.state = HarnessState.INITIALISING
        self.context = HarnessContext(prompt)

        self.transitions: Dict[HarnessState, Callable] = {self.state.INITIALISING: self._initialise(),
                            self.state.REPO_ANALYSIS: self._analyse_repo(),
                            self.state.HYDRATING_MEMORY: self._hydrate_memory(),
                            self.state.PLANNING: self._create_plan(),
                            self.state.GENERATING: self._generate(),
                            self.state.PERMISSIONS: self._run_permissions(),
                            self.state.EXECUTING: self._execute(),
                            self.state.REFLECTING: self._reflect(),
                            self.state.MEMORY_UPDATE: self._update_memory(),
                            self.state.TERMINATE: self._terminate()}

        self.permission_manager = permission_manager

    def run(self):
        pass        

    def _initialise(self):
        
