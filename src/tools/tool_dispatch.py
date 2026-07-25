from permissions import PermissionManager
from .tool import Tool
from datetime import datetime
from ../harness/artefacts/action import ActionArtefact, ActionProvider
from ../harness/artefacts/artefact_store import ArtefactStore

class ToolDispatch:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def dispatch(self, tool: Tool, exec_id: UUID, caller: ActionProvider.SYSTEM):
        params = {"provider": caller,
                  "intention": tool.intention,
                  "required_permission": tool.required_permission}
        action_artefact: ActionArtefact = ArtefactStore.builder(ActionArtefact, params)
        permission = PermissionManager.get_permission(action_artefact)
        if permission:
            try:
                exec_artefact = tool.run()
                self.logger.info(f"[Dispatch] - Tool: {type(tool)} | Permission: {PermissionManager.get_status()} | Permitted: {permission} | Timestamp: {datetime.now()}")
                return exec_artefact
            except Exception as e:
                self.logger.error(f"[Dispatch] - Tool: {type(tool)} | Permission: {PermissionManager.get_status()} | Permitted: {permission} | Timestamp: {datetime.now()}")
        return ExecutionArtefact(Artefact.new_artefact_id(), exec_id, tool.name, permission.current_state(), datetime.now(), 0.0)
