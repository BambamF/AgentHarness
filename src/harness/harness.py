from .state import HarnessState
from .context import HarnessContext

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

        self.transitions = {self.state.INITIALISING: self.initialise,
                            self.state.REPO_ANALYSIS: self.analyse_repo,
                            self.state.HYDRATING_MEMORY: self.hydrate_memory,
                            self.state.PLANNING: self.create_plan,
                            self.state.GENERATING: self.generate,
                            self.state.PERMISSIONS: self.run_permissions,
                            self.state.EXECUTING: self.execute,
                            self.state.REFLECTING: self.reflect,
                            self.state.MEMORY_UPDATE: self.update_memory,
                            self.state.TERMINATE: self.terminate}

        self.permission_manager = permission_manager

    def run(self):
        pass        
        
