import json, urllib.request
from typing import List, Optional
from django.conf import settings
from .base import LLMProvider, ChatMessage

BASE = getattr(settings, "OLLAMA_BASE_URL", "http://127.0.0.1:11434")
TIMEOUT = getattr(settings, "LLM_HTTP_TIMEOUT", 30)

def _post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(f"{BASE}{path}", method="POST")
    req.add_header("Content-Type", "application/json")
    body = json.dumps(payload).encode("utf-8")
    with urllib.request.urlopen(req, body, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))

class OllamaProvider(LLMProvider):
    name = "ollama"

    def chat(self, messages: List[ChatMessage], model: Optional[str] = None, **opts) -> str:
        model = model or settings.LLM_DEFAULTS["chat"]["ollama"]
        payload = {
            "model": model,
            "messages": [m.__dict__ for m in messages],
            "stream": False,
        }
        data = _post("/api/chat", payload)
        return (data.get("message") or {}).get("content", "")