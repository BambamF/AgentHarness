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
        self.known_facts_path = known_facts_path if known_facts_path else 'memory/known_facts.md'
        self.previous_decisions_path = decisions_path if decisions_path else 'memory/previous_decisions.md'
        self.relevant_history_path = history_path if history_path else 'memory/relevant_history.md'
        self.compressed_context_path = comp_context_path if comp_context_path else'memory/compressed_context.md'

    def scan_memory(self, execution_id: UUID) -> MemoryArtefact:
        
        memory_artefact = self.artefact_store.latest(MemoryArtefact)
        if memory_artefact == None:
            repository_artefact = self.artefact_store.latest(RepositoryArtefact)
            topology = repository_artefact.topology
            typed_topology = repository_artefact.typed_topology
            confidence_agg = {}
            topology_confidence = self.initialise_confidence("", confidence_agg, typed_topology, memory_artefact)
            params = {"memory_path": self.memory_path,
                      "topology_confidence": topology_confidence,
                      "topology": topology,
                      "typed_topology": typed_topology,
                      "known_facts_path": self.known_facts_path,
                      "previous_decisions_path": self.previous_decisions_path,
                      "relevant_history_path": self.relevant_history_path,
                      "compressed_context_path": self.compressed_context_path}
            full_params = {"artefact_id": uuid.uuid4(),
                           "execution_id": execution_id,
                           "producer": "system",
                           "timestamp": datetime.now(),
                           "metadata": None,
                           "caller": "system",
                           "payload": topology_confidence}
            full_params.update(params)
            logging.info(f"[MEMORY ARTEFACT] Producer: System | Memory Path: {self.memory_path if self.memory_path else None} | Execution ID: {execution_id}")
            memory_artefact = ArtefactFactory.builder(artefact_type=MemoryArtefact, params=full_params, artefact_store=self.artefact_store)
        return memory_artefact

    def hydrate_memory(self, execution_id: UUID):
        memory_artefact = self.artefact_store.latest(MemoryArtefact)
        print(f"[MEMORY HYDRATION] Execution ID: {execution_id} | Topology Length: {len(memory_artefact.topology)} | Topology Confidence Length: {len(memory_artefact.topology_confidence)} | Topology Confidence Sample: {self.sample_from_dict(memory_artefact.topology_confidence, 10)}")

    def sample_from_dict(self, d: Dict[Any, Any], n_sample: int):
        keys = random.sample(list(d), n_sample)
        values = [d[k] for k in keys]
        return dict(zip(keys, values))

    def initialise_confidence(self, acc:str, confidence_agg: Dict[str, float], typed_topology: Dict[str, Any], memory_artefact: MemoryArtefact) -> Dict[str, float]:
        if memory_artefact == None:
            if typed_topology.get("type") == "directory":
                absolute_key = (acc + "/" + typed_topology.get("name")).strip("/")
                confidence_agg[absolute_key] = 0.0
                for child in typed_topology.get("children"):
                    self.initialise_confidence(absolute_key, confidence_agg, child, memory_artefact)
            return confidence_agg
        else: 
            return memory_artefact.topology_confidence # CHANGE TO EVALUATE RECENT CHANGES AND COMPARE WITH MEMORY ARTEFACT
