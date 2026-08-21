from permissions.permissions import PermissionManager
from tools.tool import Tool
from tools.tool_dispatch import ToolDispatch
from datetime import datetime
from harness.artefacts.action import ActionArtefact, ActionProvider
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from harness.artefacts.permission import PermissionArtefact
import logging
from typing import Any


class ToolDispatch:

    def __init__(self, tools_path: str):
        self.tool_dicts, self.tools = self._parse_tools(tools_path)

    def dispatch(self, tool: Tool, tool_input: str, execution_id: UUID, caller: str, artefact_store: ArtefactStore):
        action_artefact: ActionArtefact = artefact_store.latest(ActionArtefact)
        permission_artefact = PermissionManager.get_permission(action_artefact, artefact_store)

        if permission_artefact.allowed:
            try:
                exec_artefact = tool.run(action_artefact.input)
                logging.info(f"[Dispatch] - Tool: {type(tool)} | Permission: {PermissionManager.get_status()} | Permitted: {permission_artefact.allowed}")
                return exec_artefact
            except Exception as e:
                params = {"execution_id": permission_artefact.execution_id,
                          "producer": caller,
                          "tool_input": tool_input,
                          "permitted": permission_artefact.allowed
                          "execution_status": "FAILED",
                          "termination_reason": "error encountered",
                          "error": e}
                logging.error(f"[Dispatch Error] - Tool: {type(tool)} | Permission: {permission_artefact.status} | Permitted: {permission_artefact.allowed}, Exception: {e}")
                print(f"[Dispatch Error] - Tool: {type(tool)} | Permission: {permission_artefact.status} | Permitted: {permission_artefact.allowed}, Exception: {e}")
                return ArtefactFactory.builder(ExecutionArtefact, params)
        else:

            params = {"execution_id": permission_artefact.execution_id,
                      "producer": caller,
                      "tool_input": tool_input,
                      "permitted": permission_artefact.allowed,
                      "execution_status": "FAILED",
                      "termination_reason": "not permitted",
                      "error": None}
            logging.error(f"[Dispatch Not Permitted] - Tool: {type(tool)} | Permission: {permission_artefact.status} | Permitted: {permission_artefact.allowed}")
            print(f"[Dispatch Not Permitted] - Tool: {type(tool)} | Permission: {permission_artefact.status} | Permitted: {permission_artefact.allowed}")
            return ArtefactFactory.builder(ExecutionArtefact, params)


    def dispatch_tools(self, response_content: list[dict[str, Any]], execution_id: UUID, caller: str, artefact_store: ArtefactStore):
        results = []

        for block in response_content:
            if block.type != "tool_use":
                continue
            tool_name = block.name
            tool_input = block.input
            tool_use_id = block.id

            tool = self.tools.get(tool_name)

            if not tool:
                logging.info(f"[DISPATCH TOOLS] {tool_name} tool not found... | Execution ID: {execution_id} | Tool Input: {str(list(tool_input.values())[0][:80]) if tool_input else ''}")
                print(f"[{tool_name}] tool not found")

            first_val = str(list(tool_input.values())[0])[:80] if tool_input else ""
            print()
            print(f"\033[33m[{tool_name}] {first_val}...\033[0m")
            try:
                output = self.dispatch(tool, tool_input, execution_id, caller, artefact_store)
            except Exception as e:
                output = f"Error during tool execution: {e}"
            print(str(output)[:300]) # Print a preview of the output

            results.append({"type": "tool_use",
                            "tool_use_id": tool_use_id,
                            "content": str(output)})

        return results


    def _parse_tools(self, tools_path: str) -> list[dict[str, Any]]:
        tool_dicts = []
        candidates = []
        for file_name in os.listdir(tools_path):
            if file_name.endswith('_tool.py'):
                mod_name = file_name[:-3].replace("_", "")
                mod_name = mod_name[0].upper()+mod_name[1:-4]+mod_name[-4].upper()+mod_name[-3:]

                module = importlib.import_module(mod_name)
                candidates = inspect.get_members(module, inspect.isclass)
                for candidate in candidates:
                    if issubclass(candidate, Tool) and candidate is not Tool:
                        tool_dicts.append({"name": candidate.name,
                                      "description": candidate.description,
                                      "input_schema": candidate.input_schema})
                        candidates.append({candidate.name: candidate})
        return tool_dicts, candidates
