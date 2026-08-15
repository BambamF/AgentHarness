from dataclasses import dataclass

@dataclass(frozen=True)
class PlanResponse:
    objective: str
    ordered_tasks: list[str]
    assumptions: list[str]
    risks: list[str]
    dependencies: list[str]
    success_criteria: list[str]
    repo_observations: dict[str, str]
    memory_references: dict[str, float]
    topology_references: dict[str, tuple[str, float]]
