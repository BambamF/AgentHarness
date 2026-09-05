from harness.context import HarnessContext
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from harness.artefacts.prompt import PromptArtefact
from harness.artefacts.plan import PlanArtefact
from harness.artefacts.repository.repository import RepositoryArtefact
from harness.artefacts.memory import MemoryArtefact
from agents.agent_config import AgentConfig
import logging
from uuid import UUID
import uuid
import json

class Planner:
    def __init__(self, agent, model, artefact_store: ArtefactStore, execution_id):
        self.artefact_store = artefact_store
        self.agent = agent
        self.model = model
        self.execution_id = execution_id

    def create_plan(self, execution_id: UUID):
        prompt_artefact = self.artefact_store.latest(PromptArtefact)
        repository_artefact = self.artefact_store.latest(RepositoryArtefact)
        memory_artefact = self.artefact_store.latest(MemoryArtefact)
        
        max_tokens = AgentConfig.max_tokens

        planning_context = self._build_context(prompt_artefact, memory_artefact, repository_artefact)

        

        system_prompt = """

            You are the planning component of an artefact-driven coding agent harness.

            Your task is to produce a concrete implementation plan from the supplied prompt, repository observations and memory.

            Do not invent repository facts.

            Distinguish between:
            - Established repository facts
            - Historical memory
            - Planner observations
            - Assumptions

            For every repository location you reference, provide a confidence score representing your confidence in the observation.

            Your output must conform to the supplied plan schema.
        """

        user_prompt = f"""

            ## USER OBJECTIVE
            
            {planning_context.get('objective')}

            ## REPOSITORY

            {json.dumps(planning_context.get('repository'), indent=2)}

            ## MEMORY

            {json.dumps(planning_context.get('memory'), indent=2)}

            Produce the planning artefact according to the required schema

        """

        try:
            message = self.agent.messages.create(
                    system=system_prompt,
                    model=self.model,
                    max_tokens=AgentConfig.max_tokens,
                    cache_control={"type": "ephemeral"},
                    messages=[{"role": "user", "content": user_prompt}],
                    output_config={"format": {
                        "type": "json_schema",
                        "schema": self.get_plan_schema()
                        }
                                   }
                    )

            raw = message.content[0].text
            plan_dict = json.loads(raw)
            
            params = {"objective": plan_dict.get("objective"),
                      "ordered_tasks": plan_dict.get("ordered_tasks"),
                      "assumptions": plan_dict.get("assumptions"),
                      "risks": plan_dict.get("risks"),
                      "dependencies_length": plan_dict.get("dependencies_length"),
                      "success_criteria": plan_dict.get("success_criteria"),
                      "repo_observations": plan_dict.get("repo_observations"),
                      "memory_references": plan_dict.get("memory_references"),
                      "topology_references": plan_dict.get("topology_references"),
                      "error": None}

            logging.info(f"[PLAN ARTEFACT] Producer: Agent | Objective: {plan_dict.get('objective')} | Tasks Head: {' -- '.join(str(task) for task in plan_dict.get('ordered_tasks')[:5])} | Sample Risk: {plan_dict.get('risks')[0] or None} | Sample Repo Observations: {' -- '.join(i.get('observation') for i in plan_dict.get('repo_observations')[:3]) or None}")

            print(f"\n[PLAN ARTEFACT] Producer: Agent | Objective: {plan_dict.get('objective')} | Tasks Head: {' -- '.join(str(task) for task in plan_dict.get('ordered_tasks')[:5])} | Sample Risk: {plan_dict.get('risks')[0] or None} | Sample Repo Observations: {' -- '.join(i.get('observation') for i in plan_dict.get('repo_observations')[:3]) or None}")
            plan_artefact = ArtefactFactory.builder(artefact_type=PlanArtefact, params=params, artefact_store=self.artefact_store, execution_id=self.execution_id, caller="agent")
            return plan_artefact

        except Exception as e:

            prompt = self.artefact_store.latest(PromptArtefact).sanitised_prompt
            params = {"objective": prompt,
                      "ordered_tasks": None,
                      "assumptions": None,
                      "risks": None,
                      "dependencies_length": None,
                      "success_criteria": None,
                      "repo_observations": None,
                      "memory_references": None,
                      "topology_references": None,
                      "error": str(e)}

            logging.error(f"[PLAN ARTEFACT] Producer: Agent | Objective: {prompt} | Error: {str(e)}")
            print(f"[PLAN ARTEFACT] Producer: Agent | Objective: {prompt} | Error: {str(e)}")
            plan_artefact = ArtefactFactory.builder(artefact_type=PlanArtefact, params=params, execution_id=self.execution_id, artefact_store=self.artefact_store, caller="agent")
            return plan_artefact

    def _build_context(self, prompt_artefact: PromptArtefact, memory_artefact: MemoryArtefact, repository_artefact: RepositoryArtefact) -> dict[str, str]:

        return {"objective": prompt_artefact.sanitised_prompt,

                "repository": {
                    "root": repository_artefact.repository_root,
                    "languages": repository_artefact.languages,
                    "entry_points": repository_artefact.entry_points,
                    "topology_depth": 4,
                    "dependency_graph_length": len(repository_artefact.dependency_graph),
                    "config_files_length": len(repository_artefact.config_files),
                    "commit_hash": repository_artefact.commit_hash
                    },
                "memory": {
                    "topology_confidence": memory_artefact.topology_confidence,
                    "known_facts": memory_artefact.known_facts,
                    "previoous_decisions": memory_artefact.previous_decisions,
                    "relevant_history": memory_artefact.relevant_history,
                    "compressed_context": memory_artefact.compressed_context
                    }
                }

    def get_plan_schema(self):
                return {"type": "object",
                        "properties": {
                            "objective": {"type": "string"},
                            "ordered_tasks": {"type": "array", 
                                              "items": {"type": "string"}},
                            "assumptions": {"type": "array", 
                                            "items": {"type": "string"}},
                            "risks": {"type": "array", 
                                      "items": {"type": "string"}},
                            "dependencies": {"type": "array", 
                                             "items": {"type": "string"}},
                            "success_criteria": {"type": "array", 
                                                 "items": {"type": "string"}},
                            "repo_observations": {
                                "type": "array", 
                                "items": {"type": "object", 
                                          "properties": {"path": {"type": "string"}, 
                                                         "observation": {"type": "string"}, 
                                                         "confidence": {"type": "number"}}, 
                                          "required": ["path", "observation", "confidence"], 
                                          "additionalProperties": False}},
                            "memory_references": {"type": "array", 
                                                  "items": {"type": "object",
                                                            "properties": {"reference_id": {"type": "string"},
                                                                           "confidence": {"type": "number"}},
                                                            "required": ["reference_id", "confidence"],
                                                            "additionalProperties": False}},
                            "topology_references": {"type": "array",
                                                    "items": {"type": "object",
                                                              "properties": {"path": {"type": "string"},
                                                                   "observation": {"type": "string"},
                                                                   "confidence": {"type": "number"}},
                                                    "required": ["path", "observation", "confidence"],
                                                    "additionalProperties": False}}
                            },
                        "required": ["objective", "ordered_tasks", "assumptions", "risks", "dependencies", "success_criteria", "repo_observations", "memory_references", "topology_references"],
                        "additionalProperties": False}
