from permissions.permissions import PermissionManager, PermissionLevel
import os
import importlib
from tools.tool import Tool
from datetime import datetime
from harness.artefacts.action import ActionArtefact, ActionProvider
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from harness.artefacts.permission import PermissionArtefact
from harness.artefacts.execution import ExecutionArtefact
import logging
from typing import Any
import inspect
from runtime.runtime import RuntimeManager


class ToolDispatch:

    def __init__(self, tools_path: str, permission_manager: PermissionManager, runtime_manager: RuntimeManager):
        self.tool_dicts, self.tools = self._parse_tools(tools_path)
        self.permission_manager = permission_manager
        self.runtime_manager = runtime_manager
        self._snapshots = {}

    def dispatch(self, action_artefact: ActionArtefact, artefact_store: ArtefactStore) -> ExecutionArtefact:
        
        tool_name = (action_artefact.input or {}).get("tool_name")
        tool = self.tools.get(tool_name)

        if tool is not None and hasattr(tool, "name") and getattr(tool, "name") == "write":
            inp = {k:v for k, v in action_artefact.input.items() if k != "tool_name"}
            return tool.run(**inp, artefact_store=artefact_store, caller=action_artefact.producer, execution_id=action_artefact.execution_id, snapshots=self._snapshots)

        permission_artefact = self.permission_manager.get_permission(action_artefact, artefact_store, PermissionLevel.EXECUTE)

        execution_artefact = self.runtime_manager.execute(action_artefact, permission_artefact)
        return execution_artefact


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
                output = self.dispatch(tool, execution_id, caller, artefact_store)
            except Exception as e:
                output = f"Error during tool execution: {e}"
            print(str(output)[:300]) # Print a preview of the output

            results.append({"type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": str(output)})

        return results


    def _parse_tools(self, tools_path: str) -> list[dict[str, Any]]:
        tool_dicts = []
        candidates = {}

        package_name = os.path.basename(os.path.abspath(tools_path))

        for file_name in os.listdir(tools_path):
            if not file_name.endswith('_tool.py'):
                continue
            module_name = file_name[:-3]
            full_module_name = f"{package_name}.{module_name}"

            module = importlib.import_module(full_module_name)
            for _, candidate in inspect.getmembers(module, inspect.isclass):
                if candidate is Tool:
                    continue
                if issubclass(candidate, Tool):
                    tool_dicts.append({"name": candidate.name,
                                       "description": candidate.description,
                                       "input_schema": candidate.input_schema})
                    candidates[candidate.name] = candidate
        return tool_dicts, candidates
