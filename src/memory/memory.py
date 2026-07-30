from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.memory import MemoryArtefact
import logging
from uuid import UUID
import uuid
from datetime import datetime
from harness.artefacts.artefact_factory import ArtefactFactory

class MemoryManager:

    def __init__(self, memory_path: str, artefact_store: ArtefactStore):
        self.memory_path = memory_path
        self.artefact_store = artefact_store

    def scan_memory(self, execution_id: UUID) -> MemoryArtefact:
        
        memory_artefact = self.artefact_store.latest(MemoryArtefact)
        if memory_artefact == None:
            params = {"memory_path": self.memory_path}
            full_params = {"artefact_id": uuid.uuid4(),
                           "execution_id": execution_id,
                           "producer": "system",
                           "timestamp": datetime.now(),
                           "confidence": 1.0, # compute later
                           "metadata": None,
                           "caller": "system",
                           "payload": self.memory_path}
            full_params.update(params)
            logging.info(f"[MEMORY ARTEFACT] Producer: System | Memory Path: {self.memory_path if self.memory_path else None} | Execution ID: {execution_id}")
            memory_artefact = ArtefactFactory.builder(artefact_type=MemoryArtefact, params=full_params, artefact_store=self.artefact_store)
        return memory_artefact

    def hydrate_memory(self):
        pass
