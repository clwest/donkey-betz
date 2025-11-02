from typing import List, Optional
from .base import ChatMessage
from .ollama_provider import OllamaProvider

def _get_provider(name: Optional[str] = None):
    name = (name or "ollama").lower()
    if name == "ollama":
        return OllamaProvider()
    raise ValueError(f"Unknown provider: {name}")

def chat(messages: List[ChatMessage], provider: Optional[str] = None, model: Optional[str] = None, **opts) -> str:
    p = _get_provider(provider)
    return p.chat(messages, model=model, **opts)