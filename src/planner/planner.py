from harness.context import HarnessContext
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.prompt import PromptArtefact

class Planner:
    def __init__(self, context: HarnessContext, artefact_store: ArtefactStore):
        self.context = context
        self.artefact_store = artefact_store

    def create_plan(self):
        prompt_artefact = self.artefact_store.get(PromptArtefact)
        repo_artefact = self.artefact_store.get(RepositoryArtefact)
        pass
