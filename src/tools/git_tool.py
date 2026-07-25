from typing import List
from .tool import Tool
from .tool_dispatcher import ToolDispatcher
import subprocess

class GitTool(Tool):
    def __init__(self, command: str, caller: str):
        self.name = "git"
        self.description = "Run a git command."
        self.input_schema = {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": "command"
                }
        self.command = command
        self.caller = caller
    
    def run_git(self):
        response = subprocess.run([self.command], capture_output=True, text=True)
        return response
