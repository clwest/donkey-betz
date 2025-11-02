# core/llm_ollama.py
from __future__ import annotations
import os, json, httpx

OLLAMA_URL   = os.environ.get("LLM_BASE_URL", "http://127.0.0.1:11434/v1")
OLLAMA_MODEL = os.environ.get("LLM_MODEL", "qwen2.5:14b-instruct")
OLLAMA_KEY   = os.environ.get("LLM_API_KEY", "local")

def chat(messages, num_ctx: int = 32768, num_parallel: int = 1, temperature: float = 0.2) -> str:
    url = f"{OLLAMA_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OLLAMA_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "options": {"num_ctx": num_ctx, "num_parallel": num_parallel, "temperature": temperature},
    }
    with httpx.Client(timeout=120) as client:
        r = client.post(url, headers=headers, json=payload)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()