from tool import Tool
import subprocess
import os

class BashTool(Tool):

    def __init__(self, command: str):
        self.name = "bash"
        self.description = "Run a shell command."
        self.input_schema = {
                "type": "object",
                "properties": {"command": {"type": string}},
                "required": ["command"]
                }
        self.command = command

    def run_bash(self, command: str):
        if any(blocked in command for blocked in PermissionManager.permission_levels.get(PermissionLevel.ALWAYS_BLOCKED, [])):
            return ArtefactStore.builder(ExecutionArtefact())
        result = subprocess.run([self.command], shell=True, cwd=os.getcwd(), capture_output=True, text=True, timeout=120)
