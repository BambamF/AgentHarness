from .state import HarnessState
from uuid import UUID
import logging
import os
from typing import Dict, Any
from pathlib import Path
from .artefacts.memory import MemoryArtefact
from .artefacts.artefact_factory import ArtefactFactory
from repositories.repository_manager import RepositoryManager

class HarnessContext:
    def __init__(self, memory_path: str, config_path: str, repository_root: str, harness_state: HarnessState, artefact_store: ArtefactStore):
        self.current_state = harness_state
        self.current_round = 0
        self.memory_path = memory_path
        self.repository_root = repository_root
        self.artefact_store = artefact_store
        self.config_path = config_path
        self.termination_reason = None

    def scan_memory(self):
        memory_artefact = self.artefact_store.get(MemoryArtefact)
        if memory_artefact == None:
            params = {"memory_path": self.memory_path}
            memory_artefact = ArtefactFactory.builder(MemoryArtefact, params)
        return memory_artefact

    def scan_repository(self):
        return RepositoryManager.get_repository_artefact(self.repository_root, self.artefact_store)

    def increment_round(self):
        self.current_round += 1
