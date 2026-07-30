from .state import HarnessState
from datetime import datetime
from uuid import UUID
import logging
import os
from typing import Dict, Any
from pathlib import Path
from .artefacts.memory import MemoryArtefact
from memory.memory import MemoryManager
from .artefacts.artefact_factory import ArtefactFactory
from repositories.repository_manager import RepositoryManager
from .artefacts.repository.repository import RepositoryArtefact
from uuid import UUID
import uuid

class HarnessContext:
    def __init__(self, memory_path: str, config_path: str, repository_root: str, artefact_store: ArtefactStore):
        self.current_round = 0
        self.memory_path = memory_path
        self.repository_root = repository_root
        self.artefact_store = artefact_store
        self.config_path = config_path
        self.termination_reason = None

    def scan_memory(self, execution_id: UUID, memory_manager: MemoryManager) -> MemoryArtefact:
        return memory_manager.scan_memory(execution_id=execution_id)

    def scan_repository(self, execution_id: UUID) -> RepositoryArtefact:
        return RepositoryManager.get_repository_artefact(repository_root=self.repository_root, artefact_store=self.artefact_store, execution_id=execution_id)

    def increment_round(self):
        self.current_round += 1
