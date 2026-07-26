from ../permissions import PermissionManager
from tool import Tool
from datetime import datetime
from ../harness/artefacts/action import ActionArtefact, ActionProvider
from ../harness/artefacts/artefact_store import ArtefactStore
from ../harness/artefacts/permission import PermissionArtefact

class ToolDispatch:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def dispatch(self, tool: Tool, exec_id: UUID, caller: ActionProvider.SYSTEM):
        params = {"execution_id": tool.execution_id,
                  "producer": caller,
                  "intention": tool.intention,
                  "required_permission": tool.required_permission}
        action_artefact: ActionArtefact = ArtefactStore.builder(ActionArtefact, params)
        permission_artefact = PermissionManager.get_permission(action_artefact)

        if permission_artefact.allowed:
            try:
                exec_artefact = tool.run()
                self.logger.info(f"[Dispatch] - Tool: {type(tool)} | Permission: {PermissionManager.get_status()} | Permitted: {permission} | Timestamp: {datetime.now()}")
                return exec_artefact
            except Exception as e:
                params = {"execution_id": permission_artefact.execution_id,
                          "producer": caller,
                          "intention": tool.intention,
                          "required_permission": tool.required_permission,
                          "execution_status": "FAILED",
                          "termination_reason": "error encountered",
                          "erorr": e}
                self.logger.error(f"[Dispatch Error] - Tool: {type(tool)} | Permission: {permission_artefact.status} | Permitted: {permission_artefact.allowed} | Timestamp: {datetime.now()}, Exception: {e}")
                return ArtefactStore.builder(ExecutionArtefact, params)
