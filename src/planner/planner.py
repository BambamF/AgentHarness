from ..harness.context import HarnessContext
from ..harness.artefacts.artefact_store import ArtefactStore
from ..harness.artefacts.prompt impoer PromptArtefact

class Planner:
    def __init__(self, context: HarnessContext, artefact_store: ArtefactStore)
        self.context = context

    def create_plan(self):
        prompt_artefact = artefact_store.get(PromptArtefact)
        repo_artefact = artefact_store.get(RepositoryArtefact)
        pass
