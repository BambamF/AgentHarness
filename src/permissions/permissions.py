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
import shlex

class PermissionManager:
    def __init__(self):
        self.permission_levels = {
                PermissionLevel.READ_ONLY: ["grep", "echo", "read", "git branch", "git log", "git status", "ls", "cat", "glob", "git rev-parse", "pwd"],
                PermissionLevel.READ_WRITE: ["write", "create", "edit", "patch", "mkdir", "touch", "mv", "git checkout", "revert"],
                PermissionLevel.EXECUTE: ["python", "python3", "pip", "pip3", "apt-get install", "apt upgrade", "docker run", "rm", "node", "git commit", "git merge"],
                PermissionLevel.ALWAYS_BLOCK: ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/", ":(){ :|:& };:"]
                }
        self.requires_sub = ["git", "apt", "apt-get", "docker", "rm", "pip"]

    def get_command_targets(self, command, prefix: str | None = None) -> list[str]:
        """
        Get the command targets from every command in a shell command chain
        """
        if isinstance(command, list):
            tokens = [str(token) for token in command]
        else:
            try:
                lexer = shlex.shlex(str(command), posix=True, punctuation_chars = ";&|")
                lexer.whitespace_split = True
                tokens = list(lexer)
            except ValueError:
                # an invalid or oddly formed shell syntax should not be treated as safe
                return [str(command)]

        targets = []
        current_command = []

        separators = {";", "&&", "||", "|", "&", "\n"}

        for token in tokens:
            if token in separators:
                if current_command:
                    target = self.get_command_target(current_command, prefix=prefix)
                    if target:
                        targets.append(target)
                    current_command = []
            else:
                current_command.append(token)

        if current_command:
            target = self.get_command_target(current_command, prefix)
            if target:
                targets.append(target)
        return targets

    def is_blocked_command(self, command, prefix: str | None = None) -> bool:
        """
        Return True if any command in the chain appears in ALWAYS_BLOCK
        """
        if isinstance(command, list):
            raw_command = " ".join(str(token) for token in command)
        else:
            raw_command = str(command)

        # handle whitespace
        normalised = " ".join(raw_command.split())

        # check each command in the chain
        targets = self.get_command_targets(command, prefix)

        for target in targets:
            if target in self.permission_levels[PermissionLevel.ALWAYS_BLOCK]:
                return True
        # check the complete command for dangerous arguments
        blocked_patterns = ["rm -rf /", "> /dev/", ":(){ :|:& };:", "sudo"]

        for pattern in blocked_patterns:
            if pattern in normalised:
                return True
        return False

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
        tool_name = tool_input.get("tool_name") or getattr(action_artefact, "tool_name", None)

        if tool_name in {"bash", "git"}:
            command = tool_input.get("command", "")
            return self.get_command_target(command, prefix=tool_name)

        return tool_name

    def get_command_target(self, command, prefix: str | None = None) -> str | None:
        if isinstance(command, list):
            tokens = [str(token) for token in command]
        else:
            tokens = str(command).split()

        if not tokens:
            return prefix

        if prefix == "git":
            return f"git {tokens[0]}"

        if prefix == "bash":
            if tokens[0] in self.requires_sub and len(tokens) > 1:
                return f"{tokens[0]} {tokens[1]}"
            return tokens[0]
        if tokens[0] in self.requires_sub and len(tokens) > 1:
            return f"{tokens[0]} {tokens[1]}"
        return tokens[0]

    def get_permission(self, action_artefact: ActionArtefact, artefact_store: ArtefactStore, current_level: PermissionLevel) -> PermissionArtefact:
        permission_target = self.get_permission_target(action_artefact)

        tool_input = action_artefact.input or {}
        command = tool_input.get("command")
        if command and self.is_blocked_command(command):

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

        LEVEL_ORDER = {
                PermissionLevel.READ_ONLY: 0,
                PermissionLevel.READ_WRITE: 1,
                PermissionLevel.EXECUTE: 2
                }

        required_level = current_level


        allowed = (required_level is not None
                   and required_level != PermissionLevel.ALWAYS_BLOCK
                   and LEVEL_ORDER[current_level] >= LEVEL_ORDER[required_level])


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
                      "allowed": allowed,
                      "reason": f"agent action: current permission level - {str(required_level)}"
                      }
            full_params = {"artefact_id": uuid.uuid4(),
                           "timestamp": datetime.now(),
                           "metadata": None,
                           "payload": True if params.get("allowed") else False}
            full_params.update(params)
            logging.info(f"[PERMISSION ARTEFACT] Execution ID: {params.get('execution_id')} | Producer: {params.get('producer')} | Allowed: {params.get('allowed')} | Reason: {params.get('reason')}")
            return ArtefactFactory.builder(PermissionArtefact, full_params, artefact_store, action_artefact.execution_id, action_artefact.caller)
