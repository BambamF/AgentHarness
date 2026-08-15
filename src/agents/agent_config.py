from dataclasses import dataclass

@dataclass(frozen=True)
class AgentConfig:
    max_tokens: int = 1024
    model: str = "claude-opus-5"


