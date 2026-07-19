from typing import List
from .tool import Tool
from .tool_dispatcher import ToolDispatcher
import subprocess

class GitTool(Tool):
    def __init__(self, subcommand: str, flags: List[str] | None, args: List[str]):
        self.name = "git"
        self.subcommand = subcommand
        self.flags = flags
        self.args = args
    
    def run(self):
        subprocess.run([self.name, self.subcommand, self.flags if self.flags, self.args if self.args], capture_output=True, text=True)    
