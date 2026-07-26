from typing import Dict, Any
from ../permissions/permissions import PermissionLevel

class Tool(name: str, description: str: input_schema: Dict[str, Any], required_persmission: PermissionLevel):
    self.name = name
    self.description = description
    self.input_schema = input_schema
    self.required_permission = required_permission
