from typing import List
from .tool import Tool
from .tool_dispatcher import ToolDispatcher
import subprocess

class GitTool(Tool):
    def __init__(self, command: str):
        self.name = "git"
        self.description = "Run a git command."
        self.input_schema = {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": "command"
                }
        self.command = command
    
    def run(self):
        response = subprocess.run([self.command], capture_output=True, text=True)
        return response
