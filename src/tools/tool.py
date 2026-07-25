from typing import Dict, Any
from ../permissions/permissions import Permission

class Tool(name: str, description: str: input_schema: Dict[str, Any], required_permission: Permission):
    self.name = name
    self.description = description
    self.input_schema = input_schema
    self.required_permission = required_permission
