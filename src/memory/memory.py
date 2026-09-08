from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.memory import MemoryArtefact
from harness.artefacts.repository.repository import RepositoryArtefact
from harness.artefacts.reflection import ReflectionArtefact
import logging
from uuid import UUID
import uuid
from datetime import datetime
from harness.artefacts.artefact_factory import ArtefactFactory
import os
from typing import Dict, Any
import random

class MemoryManager:

    def __init__(self, memory_path: str, artefact_store: ArtefactStore):
        self.memory_path = memory_path
        self.artefact_store = artefact_store
        self.relative_path = os.getcwd()

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
            logging.info(f"[MEMORY ARTEFACT] Producer: System | Memory Path: {self.memory_path if self.memory_path else None} | Execution ID: {execution_id} | Attributes: {str(full_params)}")
            memory_artefact = ArtefactFactory.builder(artefact_type=MemoryArtefact, params=full_params, artefact_store=self.artefact_store, execution_id=execution_id, caller="system")
        return memory_artefact

    def hydrate_memory(self, execution_id: UUID):
        memory_artefact = self.artefact_store.latest(MemoryArtefact)
        print(f"[MEMORY HYDRATION] Execution ID: {execution_id} | Topology Length: {len(memory_artefact.topology)} | Topology Confidence Length: {len(memory_artefact.topology_confidence)} | Topology Confidence Sample: {self.sample_from_dict(memory_artefact.topology_confidence, 10)}")

    def update_memory(self, execution_id: UUID):
        
        reflection_artefact = self.artefact_store.latest(ReflectionArtefact)
        memory_artefact = self.artefact_store.latest(MemoryArtefact)
        known_facts = reflection_artefact.known_facts
        previous_decisions = reflection_artefact.previous_decisions
        compressed_context = reflection_artefact.compressed_context
        summary = reflection_artefact.summary
        memory_confidence = reflection_artefact.memory_confidence
        repository_confidence = reflection_artefact.repository_confidence
        memory_path = memory_artefact.memory_path

        memory_context = {"compressed_context": compressed_context,
                          "known_facts": known_facts,
                          "previous_decisions": previous_decisions,
                          "memory_path": memory_path}
        logging.info(f"[MEMORY UPDATE] Execution ID: {reflection_artefact.execution_id} | Memory Path: {memory_path} | Reflection Summary: {summary}")
        with open(memory_path, 'w') as mem_path:
            json.dump(memory_context, mem_path, indent=4)

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
