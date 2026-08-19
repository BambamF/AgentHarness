from tools.tool import Tool
from tools.tool_dispatch import ToolDispatch
from uuid import UUID
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.arefact_factory import ArtefactFactory
from permissions.permissions import PermissionManager
from harness.artefacts.generation import GenerationArtefact
import logging
from typing import Any
import importlib
import inspect

class GenerationManager:

    def __init__(self, agent, model, artefact_store: ArtefactStore, execution_id: UUID, caller: str = "agent"):
        self.agent = agent
        self.model = model
        self.artefact_store = artefact_store
        self.execution_id = execution_id
        self.caller = caller

    def generate(self, tools_path: str):
        plan_artefact = self.artefact_store.latest(PlanArtefact)
        if not plan_artefact:
            logging.error(f"[GENERATING] Caller: Agent | Execution ID: {self.execution_id} | Event: Plan Artefact Does Not Exist")
            print()
            print(f"[GENERATING] The Plan Artefact Does Not Exist. Cannot Run Generation Step")
            raise(NameError("[GENERATING] Plan Artefact Does Not Exist, Check PLANNING Step"))
        generation_context = {"objective": plan_artefact.obejective,
                              "ordered_tasks": plan_artefact.ordered_tasks,
                              "assumptions": plan_artefact.assumptions,
                              "risks": plan_artefact.risks,
                              "dependencies": plan_artefact.dependencies,
                              "success_criteria": plan_artefact.success_criteria,
                              "repo_observations": plan_artefact.repo_observations,
                              "memory_references": plan_artefact.memory_references,
                              "topology_references": plan_artefact.topology_references}
        messages = [{"role": "user",
                     "content": plan_artefact.objective}]

        tools = self._parse_tools(tools_path)

        SYSTEM_PROMPT = f"""
        Use the repository and executable code as your primary reasoning substrate.

        Follow the supplied plan and use available tools to inspect, modify and test the repository.

        Verify assumptions through tool use rather than inventing repository state.

        Implement the requested functionality directly.

        Do not add comments, docstrings, documentation or other repository content solely to expose or describe your reasoning.

        Use comments/docstrings only when they are appropriate to the implementation itself.
        
        """

        user_prompt = plan_artefact.objective

        while True:
            response = self.agent.messages.create(
                    model=self.model,
                    system=SYSTEM_PROMPT,
                    messages=messages,
                    tools=tools,
                    max_tokens=8000
                    )

            messages.append({"role": "agent",
                             "content": response.content})

            if not self._contains_tool_call(response):
                break

            results = self._dispatch_tools(response)

            messages.append({"role": "user",
                             "content": results})

    def _parse_tools(self, path: str) -> list[dict[str, Any]]:
        tools = []
        for file_name in os.listdir(path):
            if file_name.endswith('_tool.py'):
                mod_name = file_name[:-3].replace("_", "")
                mod_name = mod_name[0].upper()+mod_name[1:-4]+mod_name[-4].upper()+mod_name[-3:]

                module = importlib.import_module(mod_name)
                candidates = inspect.get_members(module, inspect.isclass)
                for candidate in candidates:
                    if issubclass(candidate, Tool) and candidate is not Tool:
                        tools.append({"name": candidate.name,
                                      "description": candidate.description,
                                      "input_schema": candidate.input_schema})
        return tools

    def _dispatch_tools(self)
