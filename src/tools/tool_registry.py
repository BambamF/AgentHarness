from .tool import Tool
from typing import Dict, List
from collections import deque

class ToolRegistry:
    def __init__(self):
        self.register: Dict[type(Tool), List[Tool]] = {}
        self.tool_history: deque[Tuple[type(Tool), int]] = deque([])

    def register_tool(self, tool: Tool):
        if len(self.register) < 1:
            self.register[type(tool)] = [tool]
        else:
            self.register[type(tool)].append(tool)
        self.tool_history.append(tool.hash())

    def get_all(self):
        return self.register

    def get_latest(self) -> Tool | None:
        latest: int = self.tool_history[-1][-1]
        tool_type: type(Tool) = self.tool_history[-1][0]
        if self.register[tool_type][-1].hash() != latest:
            raise Exception("ToolRegistry: Latest tool mismatch between registry and history")
        return self.register[tool_type][-1]

    def get_latest(self, tool_type: type(Tool)) -> Tool | None:
        return self.register[tool_type][-1]
