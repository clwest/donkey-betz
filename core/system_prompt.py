# core/system_prompt.py
from __future__ import annotations
import textwrap

RULES = """You answer ONLY using the provided Context.
- No navigation advice; do not instruct the user how to search the docs.
- If a fact is missing, say: "I don't know" for that part.
- Answer with 3–7 short bullet points.
- Include inline citations like [file#chunk] pulled from Context.
"""

def build_system_prompt(docs_context: str) -> str:
    return textwrap.dedent(f"""\
    ROLE: Productive engineer with code-writing abilities.

    RULES:
    {RULES}

    CONTEXT (from /docs):
    {docs_context}
    """)