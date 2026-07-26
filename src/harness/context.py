from state import HarnessState
from uuid import UUID
from logging import logger
import os
from typing import Dict, Any
from pathlib import Path
from artefacts/memory import MemoryArtefact
from artefacts/artefact_factory import ArtefactFactory
fromm ../repositories/repository_manager import Repository_Manager

class HarnessContext:
    def __init__(self, memory_path: str | Path, log_handle: logger, config_path: str | Path, repository_root: str | Path, harness_state: HarnessState, artefact_store: ArtefactStore):
        self.current_state = harness_state
        self.current_round = 0
        self.memory_path = memory_path
        self.repository_root = repository_root
        self.artefact_store = artefact_store
        self.logger_handle = log_handle
        self.config_path = config_path
        self.termination_reason = None

    def scan_config(self):
        pass

    def scan_memory(self) -> MemoryArtefact:
        memory_artefact = artefact_store.get(MemoryArtefact)
        if memory_artefact == None:
            params = {"memory_path": self.memory_path}
            memory_artefact = ArtefactFactory.builder(MemoryArtefact, params)
        return memory_artefact

    def scan_repository(self) -> RepositoryArtefact:
        return RepositoryManager.get_repository_artefact(self.repository_root, self.artefact_store)

    def increment_round(self):
        self.current_round += 1
