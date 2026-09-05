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
                PermissionLevel.READ_ONLY: ["git branch", "git log", "git status", "ls", "echo", "cat"],
                PermissionLevel.READ_WRITE: ["mkdir", "touch", "mv", "git checkout"],
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

    def get_permission(self, action_artefact: ActionArtefact, artefact_store: ArtefactStore) -> PermissionArtefact:
        permission_text = self.get_permission_text(action_artefact)

        if any(blocked in permission_text for blocked in self.permission_levels.get(PermissionLevel.ALWAYS_BLOCK, [])):

            params = {"execution_id": action_artefact.execution_id,
                      "producer": action_artefact.producer,
                      "allowed": False,
                      "reason": "restricted_command"}
            full_params = {"artefact_id": uuid.uuid4(),
                           "timestamp": datetime.now(),
                           "metadata": None,
                           "payload": False}
            full_params.update(params)

            return ArtefactFactory.builder(PermissionArtefact, full_params, artefact_store, action_artefact.execution_id, action_artefact.caller)

        command_tokens = permission_text.split()

        if not command_tokens:
            print(f"[PERMISSION MANAGER] No command in tool call input | Execution ID: {action_artefact.execution_id}")
            logging.info(f"[PERMISSION MANAGER] No command in tool call input | Execution ID: {action_artefact.execution_id}")
            params = {"execution_id": action_artefact.execution_id,
                      "producer": action_artefact.producer,
                      "allowed": False,
                      "reason": "no command found"}
            full_params = {"artefact_id": uuid.uuid4(),
                           "timestamp": datetime.now(),
                           "metadata": None,
                           "payload": False}
            full_params.update(params)
            return ArtefactFactory.builder(PermissionArtefact, full_params, artefact_store, action_artefact.execution_id, action_artefact.caller)

        program = command_tokens[0]


        if program in self.requires_sub and len(command_tokens) > 1:
            permission_target = " ".join(command_tokens[:2])
        else:
            permission_target = program

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
                           "payload": True if paramd.get("allowed") else False}
            full_params.update(params)
            logging.info(f"[PERMISSION ARTEFACT] Execution ID: {params.get('execution_id')} | Producer: {params.get('producer')} | Allowed: {params.get('allowed')} | Reason: {params.get('reason')}")
            return ArtefactFactory.builder(PermissionArtefact, full_params, artefact_store, action_artefact.execution_id, action_artefact.caller)
