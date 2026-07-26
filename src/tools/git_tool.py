from typing import List
from .tool import Tool
from .tool_dispatcher import ToolDispatcher
import subprocess

class GitTool(Tool):
<<<<<<< HEAD
    def __init__(self, command: str):
=======
    def __init__(self, command: str, caller: str):
>>>>>>> feat/implement-initialising-state
        self.name = "git"
        self.description = "Run a git command."
        self.input_schema = {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": "command"
                }
        self.command = command
<<<<<<< HEAD
    
    def run(self):
=======
        self.caller = caller
    
    def run_git(self):
>>>>>>> feat/implement-initialising-state
        response = subprocess.run([self.command], capture_output=True, text=True)
        return response
