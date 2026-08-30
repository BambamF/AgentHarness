import os
from typing import Any
from src.harness.artefacts.action import ActionArtefact
from src.harness.artefacts.execute import ExecutionArtefact

class RuntimeManager:
    def __init__(self, agent, model, tools, execution_dir, execution_id):
        self.agent = agent
        self.model = model
        self.tools = tools
        self.execution_dir = execution_dir
        self.execution_id = execution_id

    def execute(self, tool: dict[str, Any], action_artefact) -> ExecutionArtefact:
        pass
