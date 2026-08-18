from tools.tool import Tool
from tools.tool_dispatch import ToolDispatch
from uuid import UUID
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.arefact_factory import ArtefactFactory
from permissions.permissions import PermissionManager
from harness.artefacts.generation import GenerationArtefact

class GenerationManager:

    def __init__(self, agent, model, artefact_store: ArtefactStore, execution_id: UUID, caller: str = "agent"):
        self.agent = agent
        self.model = model
        self.artefact_store = artefact_store
        self.execution_id = execution_id
        self.caller = caller

    def generate(self):
        pass
