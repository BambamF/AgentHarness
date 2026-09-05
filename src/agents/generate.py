from tools.tool import Tool
import json
from tools.tool_dispatch import ToolDispatch
from uuid import UUID
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from harness.artefacts.action import ActionArtefact
from harness.artefacts.plan import PlanArtefact
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
        generation_context = {"objective": plan_artefact.objective,
                              "ordered_tasks": plan_artefact.ordered_tasks,
                              "assumptions": plan_artefact.assumptions,
                              "risks": plan_artefact.risks,
                              "dependencies_length": plan_artefact.dependencies_length,
                              "success_criteria": plan_artefact.success_criteria,
                              "repo_observations": plan_artefact.repo_observations,
                              "memory_references": plan_artefact.memory_references,
                              "topology_references": plan_artefact.topology_references}
        messages = [{"role": "user",
                     "content": json.dumps(generation_context, default=str)}]

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
        results = []

        while True:
            response = self.agent.messages.create(
                    model=self.model,
                    system=SYSTEM_PROMPT,
                    cache_control={"type": "ephemeral"},
                    messages=messages,
                    tools=tools,
                    max_tokens=8000
                    )

            messages.append({"role": "assistant",
                             "content": response.content})

            tool_calls = self._get_tool_calls(response.content)

            if not tool_calls:
                break

            tool_results = []

            for tool_call in tool_calls:

                tool = self.tool_dispatch.tools.get(tool_call.name)

                if not tool:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "is_error": True,
                        "content": f"Tool not found: {tool_call.name}"
                        })
                    logging.error(f"[DISPATCH TOOL] {tool_call.name} tool not found... | Execution ID: {self.execution_id} | Tool Input: {str(list(tool_call.input.values())[0][:80]) if tool_call.input else ''}")

                    print(f"[DISPATCH] {tool_call.name} tool not found...")
                    continue

                first_val = (str(next(iter(tool_call.input.values())))[:80] if tool_call.input else "")
                print(f"\033[33m[{tool_call.name}] {first_val}...\033[0m")

                tool_input = dict(tool_call.input or {})
                tool_input["tool_name"] = tool_call.name

                params = {"producer": self.caller,
                          "intention": user_prompt,
                          "input": tool_input,
                          "dependencies_length": plan_artefact.dependencies_length,
                          "success_criteria": plan_artefact.success_criteria}
                action_artefact = ArtefactFactory.builder(ActionArtefact, params, self.artefact_store, self.execution_id, self.caller)
                try:
                    result = self.tool_dispatch.dispatch(action_artefact, self.artefact_store)

                    if hasattr(result, "to_json"):
                        result_content = result.to_json()
                    else:
                        result_content = str(result)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "is_error": result.execution_status != "SUCCESS",
                        "content": result_content
                        })

                    logging.info(f"[GENERATE] Tool Dispatch Result: str(result) | Execution ID: {self.execution_id} | Provider: {self.caller} | Intention: {user_prompt} | Tool Input: {tool_call.input}")

                except Exception as e:

                    result = f"Error during tool execution: {str(e)}"

                    logging.exception(f"[GENERATE] Tool Dispatch Exception: {str(e)} | Execution ID: {self.execution_id} | Provider: {self.caller} | Intention: {user_prompt} | Tool Input: {tool_call.input}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "is_error": True,
                        "content": str(e)
                        })
            messages.append({"role": "user",
                             "content": tool_results})

        return messages


            
    def _get_tool_calls(self, response_content):
        return [i for i in response_content if i.type == "tool_use"]
