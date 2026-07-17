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
        self.id_history: deque[tuple[type(Artefact), UUID]] = deque([])

    def add(self, candidate: Artefact):
        if len(self.id_history) < 1:
            self.artefacts[type(candidate)] = list(candidate)
        else:
            self.artefacts[type(candidate)].append(candidate)
        self.latest = candidate
        self.id_history.append((type(candidate), candidate.artefact_id))

    def latest(self) -> Artefact | None:
        last: tuple[type(Artefact), UUID] = self.id_history.pop()
        id: UUID = last[1]
        candidate_type: type(Artefact) = last[0]
        for candidate in self.artefacts[candidate_type]:
            if candidate.artefact_id == id:
                return candidate
        return None

    def query(self, candidate_type: type(Artefact), candidate_id: UUID) -> Artefact | None:
        for k, v in self.artefacts.items():
            if k == candidate_type:
                for candidate in v:
                    if candidate.artefact_id == candidate_id:
                        return candidate
        return None

