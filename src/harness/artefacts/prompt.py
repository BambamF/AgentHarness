from .source import PromptSource
from dataclasses import dataclass
from .artefact import Artefact
from .validation import ValidationStatus

@dataclass(frozen=True)
class PromptArteface(Artefact):
    original_prompt: str
    sanitised_prompt:str
    validation_status: ValidationStatus
    source: PromptSource
    prompt_hash: int
