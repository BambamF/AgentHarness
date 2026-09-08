from dataclasses import dataclass
from dataclasses_json import dataclass_json
from harness.artefacts.artefact import Artefact

@dataclass(frozen=True)
@dataclass_json
class ReflectionArtefact(Artefact):
    objective: str
    ordered_tasks: list
    risks: list
    dependencies: list
    success_criteria: list
    repository_confidence: dict
    memory_confidence: dict
    known_facts: list
    previous_decisions: list
    relevant_history: list
    compressed_context: dict
    summary: str
