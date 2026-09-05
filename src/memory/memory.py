from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.memory import MemoryArtefact
from harness.artefacts.repository.repository import RepositoryArtefact
import logging
from uuid import UUID
import uuid
from datetime import datetime
from harness.artefacts.artefact_factory import ArtefactFactory
import os
from typing import Dict, Any
import random

class MemoryManager:

    def __init__(self, memory_path: str, artefact_store: ArtefactStore, known_facts_path: str = None, decisions_path: str = None, history_path: str = None, comp_context_path: str = None):
        self.memory_path = memory_path
        self.artefact_store = artefact_store
        self.relative_path = os.getcwd()
        self.known_facts_path = known_facts_path if known_facts_path else 'known_facts.md'
        self.previous_decisions_path = decisions_path if decisions_path else 'previous_decisions.md'
        self.relevant_history_path = history_path if history_path else 'relevant_history.md'
        self.compressed_context_path = comp_context_path if comp_context_path else'compressed_context.md'

    def scan_memory(self, execution_id: UUID) -> MemoryArtefact:
        
        memory_artefact = self.artefact_store.latest(MemoryArtefact)
        if memory_artefact == None:
            repository_artefact = self.artefact_store.latest(RepositoryArtefact)
            topology = repository_artefact.topology
            confidence_agg = {}
            topology_confidence = self.initialise_confidence("", confidence_agg, topology, memory_artefact)
            dir_name = os.path.dirname(os.path.abspath(__file__))
            params = {"memory_path": self.memory_path,
                      "topology_confidence": topology_confidence,
                      "topology": topology,
                      "known_facts":  self._read_memory(os.path.join(dir_name, self.known_facts_path)) if os.path.isfile(self.known_facts_path) else None,
                      "previous_decisions": self._read_memory(os.path.join(dir_name, self.previous_decisions_path)) if os.path.isfile(self.previous_decisions_path) else None,
                      "relevant_history": self._read_memory(os.path.join(dir_name, self.relevant_history_path)) if os.path.isfile(self.relevant_history_path) else None,
                      "compressed_context": self._read_memory(os.path.join(dir_name, self.compressed_context_path)) if os.path.isfile(self.compressed_context_path) else None}
            full_params = {"artefact_id": uuid.uuid4(),
                           "execution_id": execution_id,
                           "producer": "system",
                           "timestamp": datetime.now(),
                           "metadata": None,
                           "caller": "system",
                           "payload": topology_confidence}
            full_params.update(params)
            logging.info(f"[MEMORY ARTEFACT] Producer: System | Memory Path: {self.memory_path if self.memory_path else None} | Execution ID: {execution_id}")
            memory_artefact = ArtefactFactory.builder(artefact_type=MemoryArtefact, params=full_params, artefact_store=self.artefact_store, execution_id=execution_id, caller="system")
        return memory_artefact

    def hydrate_memory(self, execution_id: UUID):
        memory_artefact = self.artefact_store.latest(MemoryArtefact)
        print(f"[MEMORY HYDRATION] Execution ID: {execution_id} | Topology Length: {len(memory_artefact.topology)} | Topology Confidence Length: {len(memory_artefact.topology_confidence)} | Topology Confidence Sample: {self.sample_from_dict(memory_artefact.topology_confidence, 10)}")

    def _read_memory(self, memory_path: str) -> str:
        with open(memory_path, 'r', encoding='utf-8') as f:
            return f.read()

    def sample_from_dict(self, d: Dict[Any, Any], n_sample: int):
        keys = random.sample(list(d), n_sample)
        values = [d[k] for k in keys]
        return dict(zip(keys, values))

    def initialise_confidence(self, acc:str, confidence_agg: Dict[str, float], topology: Dict[str, Any], memory_artefact: MemoryArtefact) -> Dict[str, float]:
        if memory_artefact == None:
            if topology.get("type") == "directory":
                absolute_key = (acc + "/" + topology.get("name")).strip("/")
                confidence_agg[absolute_key] = 0.0
                for child in topology.get("children"):
                    self.initialise_confidence(absolute_key, confidence_agg, child, memory_artefact)
            return confidence_agg
        else: 
            return memory_artefact.topology_confidence # CHANGE TO EVALUATE RECENT CHANGES AND COMPARE WITH MEMORY ARTEFACT
