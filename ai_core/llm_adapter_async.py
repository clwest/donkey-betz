from __future__ import annotations
import os
from typing import List, Dict, Any
from openai import AsyncOpenAI

def _normalize_base_url(url: str | None) -> str | None:
    if not url:
        return None
    return url if url.rstrip("/").endswith("/v1") else url.rstrip("/") + "/v1"

def _is_ollama(base_url: str | None) -> bool:
    return bool(base_url) and ("127.0.0.1:11434" in base_url or "localhost:11434" in base_url)

def _normalize_for_ollama(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    allowed = {"model", "messages", "temperature", "max_tokens", "top_p", "stop", "stream", "tools"}
    clean = {k: v for k, v in kwargs.items() if k in allowed}
    for k in ("response_format", "modalities", "audio", "vision", "reasoning", "tool_choice"):
        clean.pop(k, None)
    return clean

class AsyncLLMAdapter:
    def __init__(self,
                 base_url: str | None = None,
                 api_key: str | None = None,
                 default_chat_model: str | None = None,
                 default_embed_model: str | None = None):
        raw_base = base_url or os.getenv("OPENAI_BASE_URL") or os.getenv("OLLAMA_BASE_URL")
        self.base_url = _normalize_base_url(raw_base) if raw_base else None
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or "ollama"
        self.client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)
        self.default_chat_model = default_chat_model or os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:14b-instruct")
        self.default_embed_model = default_embed_model or "nomic-embed-text-v1.5"
        self.on_ollama = _is_ollama(self.base_url)

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        model = kwargs.pop("model", self.default_chat_model)
        if self.on_ollama:
            payload = _normalize_for_ollama({"model": model, "messages": messages, **kwargs})
            resp = await self.client.chat.completions.create(**payload)
            return (resp.choices[0].message.content or "") if resp.choices else ""
        else:
            # Prefer Responses API if available; otherwise fallback to chat.completions
            try:
                resp = await self.client.responses.create(model=model, input=messages)
                # Try to extract first text segment across SDK variants
                if hasattr(resp, "output") and resp.output:
                    for piece in resp.output:
                        if getattr(piece, "type", None) == "message":
                            for part in getattr(piece, "content", []) or []:
                                if getattr(part, "type", None) == "output_text":
                                    return getattr(part, "text", "") or ""
                try:
                    return resp.choices[0].message["content"]
                except Exception:
                    return ""
            except Exception:
                resp = await self.client.chat.completions.create(model=model, messages=messages, **_normalize_for_ollama(kwargs))
                return (resp.choices[0].message.content or "") if resp.choices else ""

    async def embed(self, text, **kwargs):
        model = kwargs.pop("model", self.default_embed_model)
        resp = await self.client.embeddings.create(model=model, input=text)
        if isinstance(text, list):
            return [d.embedding for d in resp.data]
        return resp.data[0].embedding
