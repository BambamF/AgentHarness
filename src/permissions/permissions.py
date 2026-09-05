from enum import Enum, auto
from harness.artefacts.action import ActionProvider, ActionArtefact
from harness.artefacts.permission import PermissionArtefact
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from datetime import datetime
from .permission_level import PermissionLevel
import logging
import uuid
from uuid import UUID

class PermissionManager:
    def __init__(self):
        self.permission_levels = {
                PermissionLevel.READ_ONLY: ["grep", "echo", "read", "git branch", "git log", "git status", "ls", "cat", "glob", "rev-parse", "pwd"],
                PermissionLevel.READ_WRITE: ["write" "create", "edit", "patch", "mkdir", "touch", "mv", "git checkout"],
                PermissionLevel.EXECUTE: ["python", "python3", "pip", "pip3", "apt-get install", "apt upgrade", "docker run", "rm", "node", "git commit", "git merge"],
                PermissionLevel.ALWAYS_BLOCK: ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/", ":(){ :|:& };:"]
                }
        self.requires_sub = ["git", "apt", "apt-get", "docker"]

    def get_permission_text(self, action_artefact) -> str:
        tool_input = action_artefact.input or {}

        command = tool_input.get("command")
        if command:
            if isinstance(command, list):
                return " ".join(str(part) for part in command)
            return str(command)

        path = tool_input.get("path", "")
        pattern = tool_input.get("pattern", "")
        content = tool_input.get("content", "")

        return " ".join(value for value in (path, pattern, content) if value is not None)

    def get_permission_target(self, action_artefact: ActionArtefact):
        tool_input = action_artefact.input or {}
        tool_name = tool_input.get("tool_name")

        if tool_name == "read":
            return "read"

        if tool_name == "bash":
            command = tool_input.get("command", "")
            return self.get_command_target(command)

        return tool_name

    def get_command_target(self, command) -> str | None:
        if isinstance(command, list):
            tokens = [str(token) for token in command]
        else:
            tokens = str(command).split

        if not tokens:
            return None

        if tokens[0] in self.requires_sub:
            return f"{tokens[0]}{tokens[1]}"

        return tokens[0]

    def get_permission(self, action_artefact: ActionArtefact, artefact_store: ArtefactStore) -> PermissionArtefact:
        permission_target = self.get_permission_target(action_artefact)

        if permission_target in self.permission_levels.get(PermissionLevel.ALWAYS_BLOCK, []):

            params = {"execution_id": action_artefact.execution_id,
                      "producer": action_artefact.producer,
                      "allowed": False,
                      "reason": "restricted_command"}
            full_params = {"artefact_id": uuid.uuid4(),
                           "timestamp": datetime.now(),
                           "metadata": None,
                           "payload": False}
            full_params.update(params)

            logging.info(f"[PERMISSION ARTEFACT] Execution ID: {params.get('execution_id')} | Producer: {params.get('producer')} | Allowed: {params.get('allowed')} | Reason: {params.get('reason')}")
            print(f"[PERMISSION MANAGER] Command Blocked | Execution ID: {params.get('execution_id')} | Producer: {params.get('producer')} | Allowed: {params.get('allowed')} | Reason: {params.get('reason')}")
            return ArtefactFactory.builder(PermissionArtefact, full_params, artefact_store, action_artefact.execution_id, action_artefact.caller)

        command_access = None
        for level, command_starts in self.permission_levels.items():
            if permission_target in command_starts:
                command_access = level
                break
        if command_access is None:
            print(f"[PERMISSION MANAGER] Command denied, inadequate access level | Execution ID: {action_artefact.execution_id}")
            logging.info(f"[PERMISSION MANAGER] Command denied, inadequate access level | Execution ID: {action_artefact.execution_id}")
            params = {"execution_id": action_artefact.execution_id,
                      "producer": action_artefact.producer,
                      "allowed": False,
                      "reason": "denied"}
            full_params = {"artefact_id": uuid.uuid4(),
                           "timestamp": datetime.now(),
                           "metadata": None,
                           "payload": False}
            full_params.update(params)
            return ArtefactFactory.builder(PermissionArtefact, full_params, artefact_store, action_artefact.execution_id, action_artefact.caller)

        if action_artefact.producer == "system":
            params = {"execution_id": action_artefact.execution_id,
                      "producer": action_artefact.producer,
                      "allowed": True,
                      "reason": "system operation"}
            full_params = {"artefact_id": uuid.uuid4(),
                           "timestamp": datetime.now(),
                           "metadata": None,
                           "payload": True}
            full_params.update(params)
            logging.info(f"[PERMISSION ARTEFACT] Execution ID: {params.get('execution_id')} | Producer: {params.get('producer')} | Allowed: {params.get('allowed')} | Reason: {params.get('reason')}")
            return ArtefactFactory.builder(PermissionArtefact, full_params, artefact_store, action_artefact.execution_id, action_artefact.caller)
        else:
            params = {"execution_id": action_artefact.execution_id,
                      "producer": action_artefact.producer,
                      "allowed": True if command_access else False,
                      "reason": f"agent action: current permission level - {command_access}"
                      }
            full_params = {"artefact_id": uuid.uuid4(),
                           "timestamp": datetime.now(),
                           "metadata": None,
                           "payload": True if params.get("allowed") else False}
            full_params.update(params)
            logging.info(f"[PERMISSION ARTEFACT] Execution ID: {params.get('execution_id')} | Producer: {params.get('producer')} | Allowed: {params.get('allowed')} | Reason: {params.get('reason')}")
            return ArtefactFactory.builder(PermissionArtefact, full_params, artefact_store, action_artefact.execution_id, action_artefact.caller)
