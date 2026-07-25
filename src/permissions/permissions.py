from enum import Enum, auto
from uuid import uuid4
from ../harness/action import ActionProvider
from ../harness/artefacts/permission_artefact import PermissionArtefact
from datetime import datetime

class PermissionLevel(Enum):
    READ_ONLY = auto()
    READ_WRITE = auto()
    EXECUTE = auto()
    ALWAYS_BLOCK = auto()

class AgentPermissions(Enum):


class PermissionManager:
    def __init__(self):
        self.permission_levels = {
                PermissionLevel.READ_ONLY: ["git branch", "git log", "git status", "ls", "echo", "cat"],
                PermissionLevel.READ_WRITE: ["mkdir", "touch", "mv", "git checkout"]
                PermissionLevel.EXECUTE: ["python", "python3", "pip", "pip3", "apt-get install", "apt upgrade", "docker run", "rm", "node", "git commit", "git merge"],
                PermissionLevel.ALWAYS_BLOCK: ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/", ":(){ :|:& };:"]
                }
        self.requires_sub = ["git", "apt", "docker"]

    def get_permission(self, action_artefact: ActionArtefact) -> PermissionArtefact:
        command = action_artefact.command
        if list(command)[0] in self.requires_sub:
            start = 1
        else:
            start = 0
        for level, commands in self.permission_levels.items():
            if command[:start] in commands:
                command_access = level
            else:
                command_access = PermissionLevel.READ_ONLY
        if action_artefact.provider == ActionProvider.SYSTEM:
            return PermissionArtefact(artefact_id=uuid4(),
                                      execution_id=action_artefact.execution_id,
                                      producer=action_artefact.provider,
                                      timestamp=datetime.now(),
                                      confidence=1.0,
                                      allowed=True,
                                      reason="system operation"
                                      metadata=None)
        else:
            return PermissionArtefact(
                        artefact_id=uuid4(),
                        execution_id=action_artefact.execution_id,
                        producer=action_artefact.provider,
                        timestamp=datetime.now(),
                        confidence=1.0,
                        allowed=action_artefact.required_permission == command_access,
                        reason=f"agent action: current permission level: {command_access}",
                        metadata=None
                    )
