from dataclasses import dataclass
from .artefact import Artefact
from ..context import HarnessContext

@dataclass(frozen=True)
class PlanArtefact(Artefact):
    objective: str
    ordered_tasks: list
    assumptions: list
    risks: list
    dependencies: list
    success_criteria: list
    repo_observations: dict
    memory_references: dict
    topology_references: dict
    error: Any | None

