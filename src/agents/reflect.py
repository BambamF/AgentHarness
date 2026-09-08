
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
    def __init__(self, model: str, agent, tool_dispatch: ToolDispatch, execution_id: UUID, artefact_store: ArtefactStore):
        self.execution_id = execution_id
        self.artefact_store = artefact_store
        self.tool_dispatch = tool_dispatch
        self.model = model
        self.agent = agent

    def reflect(self):
        session_artefacts = self.artefact_store.get_session_artefacts(self.execution_id)
        execution_artefacts = []
        action_artefacts = []
        repository_artefact = None
        plan_artefact = None
        memory_artefact = None
        if plan_artefact is None:
            raise RuntimeError(f"No Plan Artefact found for exectution {self.execution_id}")
        if repository_artefact is None:
            raise RuntimeError(f"No Repository Artefact found for exectution {self.execution_id}")
        for artefact in session_artefacts:
            if isinstance(artefact) == PlanArtefact:
                plan_artefact = artefact
            elif isinstance(artefact) == ExecutionArtefact:
                execution_artefacts.append(artefact)
            elif isinstance(artefact) == ActionArtefact:
                action_artefacts.append(artefact)
            elif isinstance(artefact) == MemoryArtefact:
                memory_artefact = artefact
            elif isinstance(artefact) == RepositoryArtefact:
                repository_artefact = artefact
        reflection_context = {"execution_artefacts": [execution_artefact.to_json() for execution_artefact in execution_artefacts],
                              "action_artefacts": [action_artefact.to_json() for action_artefact in action_artefacts],
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

        Memory confidence scores range from 0.0 to 10.0 with entries within the memory file ordered using a two tier system where memory entities are identified following the pattern of {<execution_id>/<memory_uuid>:confidence_score, <path/to/file>}
        """ 

        messages = [{"role": "user",
                     "content": json.dumps(reflection_context, default=str)}]
        while True:
            response = self.agent.messages.create(
                    model=self.model,
                    system=SYSTEM_PROMPT,
                    cache_control={"type": "ephemeral"},
                    messages=messages,
                    tools=self.tool_dispatch.get_tools(),
                    max_tokens=8000,
                    output_config={"format": {"type": "json_schema",
                                              "schema": self.get_reflection_schema()
                                              }
                                   }
                    )
            messages.append({"role": "assistant",
                             "content": response.content})
            tool_calls = [i for i in response.content if i.type == "tool_use"]
            if not tool_calls:
                reflection = response.content[0].text
                break
            tool_results = []
            for tool_call in tool_calls:
                tool = self.tool_dispatch.tools.get(tool_call.name)

                if not tool:
                    tool_results.append({"type": "tool_result",
                                        "tool_use_id": tool_call.id,
                                        "is_error": True,
                                        "content": f"Tool not found {tool_call.name}"})
                    logging.error(f"[REFLECT TOOL DISPATCH] Tool {tool_call.name} tool not found... | Execution ID: {self.execution_id} | Tool Input: {str(list(tool_call.input.values())[0][:80]) if tool_call.input else ''}")

                    print(f"[REFLECT DISPATCH] {tool_call.name} tool not found...")
                    continue

                first_val = (str(next(iter(tool_call.input.values())))[:80] if tool_call.input else "")
                print(f"\033[33m[{tool_call.name}] {first_val}...\033[0m")

                tool_input = dict(tool_call.input or {})
                tool_input["tool_name"] = tool_call.name

                params = {"producer": "agent",
                          "intention": "Analyse the execution session using the provided artefacts, produce your reflection and propose updated memory and repository confidence information for future executions.",
                          "input": tool_input,
                          "dependencies_length": plan_artefact.dependencies_length,
                          "success_criteria": plan_artefact.success_criteria}
                action_artefact = ArtefactFactory.builder(ActionArtefact, params, self.artefact_store, self.execution_id, "agent")
                try:
                    result = self.tool_dispatch.dispatch(action_artefact, self.artefact_store)

                    if hasattr(result, "to_json"):
                        result_content = result.to_json()
                    else:
                        result_content = str(result)

                    tool_results.append({"type": "tool_result",
                                        "tool_use_id": tool_call.id,
                                        "is_error": result.execution_status != "SUCCESS",
                                        "content": result_content})
                    logging.info(f"[REFLECT] Tool Dispatch Result: {str(result)} | Execution ID: {self.execution_id} | Producer: {params.get("producer")} | Intention: {params.get("intention")} | Tool Input: {tool_input}")

                except Exception as e:
                    result = f"Error during tool execution: {str(e)}"

                    logging.exception(f"[REFLECT] Tool Dispatch Exception: {str(e)} | Execution ID: {self.execution_id} | Producer: {params.get("producer")} | Intention: {params.get("intention")} | Tool Input: {tool_input}")

                    tool_results.append({"type": "tool_result",
                                         "tool_use_id": tool_call.id,
                                         "is_error": True,
                                         "content": str(e)}) 
                messages.append({"role": "user",
                                "content": tool_results})
        
        
        reflection_artefact = ArtefactFactory.builder(ReflectionArtefact, json.loads(reflection), self.artefact_store, self.execution_id, "agent")
        return reflection_artefact
            


    def get_reflection_schema(self):
        return {"type": "object",
                "properties": {
                    "objective": {"type": "string"},
                    "ordered_tasks": {"type": "array",
                                      "items": {"type": "string"}},
                    "risks": {"type": "array",
                              "items": {"type": "string"}},
                    "dependencies": {"type": "array",
                                     "items": {"type": "string"}},
                    "success_criteria": {"type": "array",
                                         "items": {"type": "string"}},
                    "repository_confidence": {"type": "object",
                                                "properties": {"path": {"type": "string"}.
                                                                "observation": {"type": "string"},
                                                                "confidence": {"type": "number"}},
                                                "required": ["path", "observation", "confidence"],
                                                "additionalProperties": False},
                    "memory_confidence": {"type": "object",
                                            "properties": {"reference_id": {"type": "string"},
                                                            "confidence": {"type": "number"},
                                                            "resource_path": {"type": "string"}},
                                            "required": ["reference_id", "confidence", "resource_path"],
                                            "additionalProperties": False},
                    "known_facts": {"type": "array",
                                    "items": {"type": "string"}},
                    "previous_decisions": {"type": "array",
                                           "items": {"type": "string"}},
                    "relevant_history": {"type": "array",
                                         "items": {"type": "string"}},
                    "compressed_context": {"type": "object",
                                           "properties": {"session_id": {"type": "string"},
                                                          "context": {"type": "string"}}
                                           "required": ["session_id", "context"],
                                           "additionalProperties": False},
                    "summary": {"type": "string"},
                    },
                "required": ["objective", "ordered_tasks", "risks", "dependencies", "success_criteria", "repository_confidence", "memory_confidence", "known_facts", "previous_decisions", "relevant_history", "compressed_context", "summary"],
                "additionalProperties": False}

        

