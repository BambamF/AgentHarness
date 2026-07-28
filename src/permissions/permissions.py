from enum import Enum, auto
from harness.artefacts.action import ActionProvider, ActionArtefact
from harness.artefacts.permission import PermissionArtefact
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from datetime import datetime
from .permission_level import PermissionLevel

class PermissionManager:
    def __init__(self):
        self.permission_levels = {
                PermissionLevel.READ_ONLY: ["git branch", "git log", "git status", "ls", "echo", "cat"],
                PermissionLevel.READ_WRITE: ["mkdir", "touch", "mv", "git checkout"],
                PermissionLevel.EXECUTE: ["python", "python3", "pip", "pip3", "apt-get install", "apt upgrade", "docker run", "rm", "node", "git commit", "git merge"],
                PermissionLevel.ALWAYS_BLOCK: ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/", ":(){ :|:& };:"]
                }
        self.requires_sub = ["git", "apt", "docker"]

    def get_permission(self, action_artefact: ActionArtefact, artefact_store: ArtefactStore) -> PermissionArtefact:
        command = action_artefact.command

        if any(blocked in command for blocked in self.permission_levels.get(PermissionLevel.ALWAYS_BLOCK, [])):

            params = {"execution_id": action_artefact.execution_id,
                      "producer": action_artefact.provider,
                      "allowed": False,
                      "reason": "restricted_command"}
            full_params = {"artefact_id": uuid.uuid4(),
                           "producer": role,
                           "timestamp": datetime.now(),
                           "confidence": 1.0, # compute later
                           "metadata": None,
                           "payload": False}
            full_params.update(params)

            return ArtefactFactory.builder(artefact_type=PermissionArtefact, params=params, artefact_store=artefact_store)
        if list(command)[0] in self.requires_sub:
            start = 2
        else:
            start = 1
        for level, command_starts in self.permission_levels.items():
            if command[:start] in command_starts:
                command_access = level
            else:
                command_access = PermissionLevel.READ_ONLY
        if action_artefact.provider == ActionProvider.SYSTEM:
            params = {"execution_id": action_artefact.execution_id,
                      "producer": action_artefact.provider,
                      "allowed": True,
                      "reason": "system operation"}
            full_params = {"artefact_id": uuid.uuid4(),
                           "producer": role,
                           "timestamp": datetime.now(),
                           "confidence": 1.0, # compute later
                           "metadata": None,
                           "payload": True}
            full_params.update(params)
            logging.info(f"[PERMISSION ARTEFACT] Execution ID: {params.get('execution_id')} | Producer: {params.get('producer')} | Allowed: {params.get('allowed')} | Reason: {params.get('reason')}")
            return ArtefactFactory.builder(artefact_type=PermissionArtefact, params=full_params, artefact_store=artefact_store)
        else:
            params = {"execution_id": action_artefact.execution_id,
                      "producer": action_artefact.provider,
                      "allowed": True if action_artefact.required_permission == command_access else False,
                      "reason": f"agent action: current permission level - {command_access}"
                      }
            full_params = {"artefact_id": uuid.uuid4(),
                           "producer": role,
                           "timestamp": datetime.now(),
                           "confidence": 1.0, # compute later
                           "metadata": None,
                           "payload": True}
            full_params.update(params)
            logging.info(f"[PERMISSION ARTEFACT] Execution ID: {params.get('execution_id')} | Producer: {params.get('producer')} | Allowed: {params.get('allowed')} | Reason: {params.get('reason')}")
            return ArtefactFactory.builder(artefact_type=PermissionArtefact, params=full_params, artefact_store=artefact_store)
