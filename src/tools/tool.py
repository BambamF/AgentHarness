from typing import Dict, Any
from permissions.permissions import PermissionLevel
from dataclasses import dataclass

@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
