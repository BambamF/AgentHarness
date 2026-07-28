from dataclasses import dataclass
from .artefact import Artefact
# from .validation import ValidationStatus

@dataclass(frozen=True)
class PromptArtefact(Artefact):
    original_prompt: str
    sanitised_prompt:str
    # validation_status: ValidationStatus
    source: str
    prompt_hash: int
