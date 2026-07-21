from .artefact import Artefact
from uuid import UUID
from collections import deque

"""
    ArtefactStore is the execution knowledge repository for a single Harness run.
    It stores immutable artefacts and provides retrieval methods without exposing internal storage implementation
"""
class ArtefactStore:
    def __init__(self):
        self.artefacts: dict[type(Artefact), list[Artefact]] = {}
        self.artefact_history: deque[tuple[type(Artefact), UUID]] = deque([])

    def add(self, candidate: Artefact):
        if type(candidate) not in self.artefacts:
            self.artefacts[type(candidate)] = [candidate]
        else:
            self.artefacts[type(candidate)].append(candidate)
        self.artefact_history.append((type(candidate), candidate.artefact_id))

    def latest_any(self) -> Artefact | None:
        if len(self.artefact_history) < 1:
            last: tuple[type(Artefact), UUID] = self.artefact_history[-1]
            id: UUID = last[1]
            candidate_type: type(Artefact) = last[0]
            for candidate in self.artefacts[candidate_type]:
                if candidate.artefact_id == id:
                    return candidate
        return None

    def latest(self, artefact_type: Artefact):
        return self.artefacts.get(artefact_type, [])[-1]

    def get(self, candidate_type: type(Artefact), candidate_id: UUID) -> Artefact | None:
        for k, v in self.artefacts.items():
            if k == candidate_type:
                for candidate in v:
                    if candidate.artefact_id == candidate_id:
                        return candidate
        return None

    def get_all(self, artefact_type: type(Artefact)):
        return self.artefacts.get(artefact_type, [])

