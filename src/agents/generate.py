from tools.tool import Tool
from tools.tool_dispatch import ToolDispatch
from uuid import UUID
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from harness.artefacts.action import ActionArtefact
from permissions.permissions import PermissionManager
import logging
from typing import Any
import importlib
import inspect
from tools.tool_dispatch import ToolDispatch

class GenerationManager:

    def __init__(self, agent, model, artefact_store: ArtefactStore, execution_id: UUID, tool_dispatch: ToolDispatch, caller: str = "agent"):
        self.agent = agent
        self.model = model
        self.artefact_store = artefact_store
        self.execution_id = execution_id
        self.caller = caller
        self.tool_dispatch = tool_dispatch

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
                     "content": generation_context}]

        tools = self.tool_dispatch.tool_dicts

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

            messages.append({"role": "assistant",
                             "content": response.content})

            tool_calls = self._get_tool_calls(response)

            if not tool_calls:
                break

            results = self.tool_dispatch.dispatch_tools(tool_calls, self.execution_id, self.caller, self.artefact_store)

            messages.append({"role": "user",
                             "content": results})
            for tool_call in tool_calls:
                params = {"provider": self.caller,
                          "intention": user_prompt,
                          "input": tool_call.input,
                          "dependencies": plan_artefact.dependencies,
                          "success_criteria": plan_artefact.success_criteria}
                action_artefact = ArtefactFactory.builder(ActionArtefact, params, self.artefact_store, self.execution_id, self.caller)
            
    def _get_tool_calls(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [i for i in messages if i.content.get("type") == "tool_use"]
