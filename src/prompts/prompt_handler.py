import html
from harness.artefacts.prompt import PromptArtefact
from harness.artefacts.artefact_store import ArtefactStore
# from .import ValidationStatus
# from . import PromptSource

class PromptHandler:

    def sanitise_prompt(self, prompt: str) -> str:
        return html.escape()

    def validate_prompt(self, prompt: str):
        # will call validator model against charter
        pass

    def handle_prompt(self, prompt: str, source: PromptSource, artefact_store: ArtefactStore) -> PromptArtefact:
        sanitised = self.sanitise_prompt(prompt)
        validated = self.validate_prompt(sanitised)
        prompt_artefact = PromptArtefact(prompt, sanitised, validated, source, prompt.hash())
        artefact_store.add(prompt_artefact)
        return prompt_artefact
