from dataclasses import dataclass
from typing import Literal, List, Optional

Role = Literal["system", "user", "assistant"]

@dataclass
class ChatMessage:
    role: Role
    content: str

class LLMProvider:
    name: str = "base"

    def chat(self, messages: List[ChatMessage], model: Optional[str] = None, **opts) -> str:
        raise NotImplementedError