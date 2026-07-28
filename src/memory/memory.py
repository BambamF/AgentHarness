from ../harness/artefacts/artefact_store import ArtefactStore
from ../harness/artefacts/memory_artefact import MemoryArtefact

class MemoryManager:

    def __init__(self, memory_path: str, artefact_story: ArtefactStore):
        self.memory_path = memory_path

    def hydrate_memory(self):
        pass
