import os
from typing import Any
from src.harness.artefacts.action import ActionArtefact
from src.harness.artefacts.execute import ExecutionArtefact
from uuid import UUID

class RuntimeManager:
    def __init__(self, agent: str, model: str, tools: dict[str. Any], executions_dir: str):
        self.agent = agent
        self.model = model
        self.tools = tools
        self.executions_dir = execution_dir

    def execute(self, tool: dict[str, Any], action_artefact: ActionArtefact, execution_id: UUID) -> ExecutionArtefact:
        
        runtime_path = self._prepare_execution_environment(action_artefact.execution_id)

        container = self._get_or_create_container(action_artefact.execution_id, runtime_path)

        try:
            result = self._execute_tool(container, tool, action_artefact.input)

            return self._create_execution_artefact(action_artefact, result)

        except Exception as e:
            
            return self._create_execution_artefact(action_artefact, e)
