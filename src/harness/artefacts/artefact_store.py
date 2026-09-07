from .artefact import Artefact
from uuid import UUID
from collections import deque
from typing import Dict, Any
from datetime import datetime

"""
    ArtefactStore is the execution knowledge repository for a single Harness run.
    It stores immutable artefacts and provides retrieval methods without exposing internal storage implementation
"""
class ArtefactStore:
    def __init__(self):
        self.artefacts: dict[type(Artefact), list[Artefact]] = {}
        self.artefact_history: deque[tuple[type(Artefact), UUID, UUID]] = deque([])

    def print_artefacts_meta(self, n_artefacts: int):
        if n_artefacts <= 0:
            return
        artefacts_tuples = list(self.artefact_history)[-n_artefacts:]
        for t, id in artefacts_tuples:
            for i in self.artefacts.get(t): 
                if i.artefact_id == id:
                    print(f"Artefact Type: {t} | Artefact: {i}\n")

    def add(self, candidate: Artefact):
        if type(candidate) not in self.artefacts:
            self.artefacts[type(candidate)] = [candidate]
        else:
            self.artefacts[type(candidate)].append(candidate)
        self.artefact_history.append((type(candidate), candidate.artefact_id, candidate.execution_id))

    def get_session_artefacts(self, execution_id: UUID):
        if not self.artefact_history:
            return None
        session_artefacts = []
        for t, a_id, exec_id in self.artefact_history:
            if execution_id == exec_id:
                for artfct in self.artefacts.get(t):
                    if artfct.execution_id == execution_id:
                        session_artefacts.append(artfct)
        return session_artefacts

    def latest_any(self) -> Artefact | None:
        if self.artefact_history:
            last: tuple[type(Artefact), UUID] = self.artefact_history[-1]
            id: UUID = last[1]
            candidate_type: type(Artefact) = last[0]
            for candidate in self.artefacts[candidate_type]:
                if candidate.artefact_id == id:
                    return candidate
        return None

    def latest(self, artefact_type: type(Artefact)) -> Artefact | None:
        return self.artefacts.get(artefact_type)[-1] if self.artefacts.get(artefact_type) else None

    def get(self, candidate_type: type(Artefact), candidate_id: UUID) -> Artefact | None:
        for k, v in self.artefacts.items():
            if k == candidate_type:
                for candidate in v:
                    if candidate.artefact_id == candidate_id:
                        return candidate
        return None

    def get_all(self, artefact_type: type(Artefact)) -> List[Artefact] | None:
        return self.artefacts.get(artefact_type)

