from dataclasses import dataclass
from .artefact import Artefact

@dataclass(frozen=True)
class PlanArtefact(Artefact):
    objective: str
    ordered_tasks: list
    assumptions: list
    risks: list
    dependencies: list
    success_criteria: list

