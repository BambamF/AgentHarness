
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from harness.artefacts.repository.repository import RepositoryArtefact
from harness.artefacts.plan import PlanArtefact
from harness.artefacts.execution import ExecutionArtefact
from harness.artefacts.action import ActionArtefact
from harness.artefacts.memory import MemoryArtefact
from uuid import UUID
import logging
import json

class ReflectionManager:
    def __init__(self, model: str, agent, execution_id: UUID, artefact_store: ArtefactStore):
        self.execution_id = execution_id
        self.artefact_store = artefact_store

    def reflect(self):
        session_artefacts = self.artefact_store.get_session_artefacts(self.execution_id)
        execution_artefacts = []
        action_artefacts = []
        repository_artefact = None
        plan_artefact = None
        memory_artefact = None
        for artefact in session_artefacts:
            if type(artefact) == PlanArtefact:
                plan_artefact = artefact
                continue
            if type(artefact) == ExecutionArtefact:
                execution_artefacts.append(artefact)
                continue
            if type(artefact) == ActionArtefact:
                action_artefacts.append(artefact)
                continue
            if type(artefact) == MemoryArtefact:
                memory_artefact = artefact
            if type(artefact) == RepositoryArtefact:
                repository_artefact = artefact
                continue
        reflection_context = {"execution_artefacts": execution_artefact.to_json() for execution_artefact in execution_artefacts,
                              "action_artefacts": action_artefact.to_json() for action_artefact in action_artefacts,
                              "repository_artefact": repository_artefact.to_json(),
                              "plan_artefact": plan_artefact.to_json(),
                              "memory_artefact": memory_artefact.to_json()}

    
        SYSTEM_PROMPT = """
        You are a coding execution session analysis agent.

        Analyse the complete excution session using the supplied artefacts and query the supplied log file when additional evidence is required.

        Compare the original requirement and planned success criteria against the observed execution.

        Determine which criteria where satisfied, partially satisfied or unsatisfied.

        Identify deviations from the plan, failed or corrective actions, unresolved issues and evidence supporting your conclusions.

        Based on this analysis, produce your reflection and propose updated memory and repository confidence information for future executions.

        Your proposed memory confidence and repository confidence structure should follow the observed repository and memory confidence schema.

        Repository confidence scores range from  0.0 to 10.0, with files and directories scoring closer to 0.0 if the contents of the files or directories have not been observed recently.

        Memory confidence scores range from 0.0 to 10.0 with entries within the memory file ordered using a two tier system where memory entities are identified following the pattern of <execution_id>/<memory_uuid>: and sub entities identified following the pattern <path/to/file>:(memory point relating to file)
        """ 

        messages = [{"role": "user",
                     "content": json.dumps(reflection_context)}]
        while True:
            response = self.agent.messages.create(
                    model=self.model,
                    system=SYSTEM_PROMPT,
                    cache_control={"type": "ephemeral"},
                    messages=messages,
                    tools=permission_manager.get_tools(),
                    max_tokens=8000
                    )
            messages.append({"role": "assistant",
                             "content": response.content})
            tool_calls = [i for i in response.content if i.type == "tool_use"]
            if not tool_calls:
                break
            tool_results = []
            for tool in tool_calls:
                tool = self.tool_dispatch.tools.get(tool_call.name)

                if not tool:
                    tool_result.append({"type": "tool_result",
                                        "tool_use_id": tool_call.id,
                                        "is_error": True,
                                        "content": f"Tool not found {tool_call.name}"})
                    logging.error(f"[REFLECT TOOL DISPATCH] Tool {tool_call.name} tool not found... | Execution ID: {self.execution_id} | Tool Input: {str(list(tool_call.input.values())[0][:80]) if tool_call.input else ''}")

                    print(f"[REFLECT DISPATCH] {tool_call.name} tool not found...")

                first_val = (str(next(iter(tool_call.input.values())))[:80] if tool_call.input else "")
                print(f"\033[33m[{tool_call.name}] {first_val}...\033[0m")

                tool_input = dict(tool_call.input or {})
                tool_input["tool_name"] = tool_call.name



        

