# core/ask_with_docs.py
from __future__ import annotations
from core.rag import build_docs_context
from core.system_prompt import build_system_prompt
from core.llm_ollama import chat

def ask_with_docs(question: str, k: int = 8, num_ctx: int = 32768) -> str:
    ctx = build_docs_context(question, k=k)
    sys_prompt = build_system_prompt(ctx)
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"Question: {question}"},
    ]
    return chat(messages, num_ctx=num_ctx)