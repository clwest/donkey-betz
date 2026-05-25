# core/rag.py
from __future__ import annotations
import json
import re
from pathlib import Path

CORPUS_PATH = Path(".rag/corpus.jsonl")

LEARNING_LOOP_HINTS = [
    "learning loop", "UserEmbedding", "UserAgentLearning",
    "similarity search", "cosine", "successful application",
    "recommend", "embedding", "pgvector", "similar jobs"
]

PREF_FILE_BONUS = [
    re.compile(r"audits/.*learning[-_ ]loop", re.I),
    re.compile(r"completions/.*learning[-_ ]loop", re.I),
    re.compile(r"LEARNING_LOOP.*", re.I),
]

def _hint_score(text: str) -> int:
    t = text.lower()
    score = 0
    # phrase boost
    if "learning loop" in t:
        score += 10
    # token boosts
    for h in LEARNING_LOOP_HINTS:
        if h in t:
            score += 2
    return score

def _file_bonus(path: str) -> int:
    for rx in PREF_FILE_BONUS:
        if rx.search(path):
            return 8
    return 0

def top_k(question: str, k: int = 8, boost_hints: bool = True) -> list[dict]:
    """Rank corpus chunks by token-overlap against ``question``.

    boost_hints=True preserves the legacy askdocs CLI behavior (learning-
    loop bias from LEARNING_LOOP_HINTS + PREF_FILE_BONUS). Pass False for
    general-purpose doc search where that bias is wrong (e.g., the
    Session 1142 ``search_docs`` PA tool).
    """
    if not CORPUS_PATH.exists():
        return []
    q = question.lower()
    q_terms = set(q.split())
    scored = []
    with CORPUS_PATH.open() as f:
        for line in f:
            row = json.loads(line)
            t = row["text"]
            tl = t.lower()

            # base: shared token overlap
            base = sum(1 for w in q_terms if w in tl)

            if boost_hints:
                base += _hint_score(tl)
                base += _file_bonus(row.get("file", ""))

            if base:
                scored.append((base, row))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:k]]

def build_docs_context(question: str, k: int = 10, max_chars: int = 9000, boost_hints: bool = True) -> str:
    rows = top_k(question, k=k, boost_hints=boost_hints)
    parts, total = [], 0
    for r in rows:
        cite = f"[{r['file']}#{r['chunk_id']}]"
        snippet = " ".join(r["text"].split())
        piece = f"{cite} {snippet}"
        if total + len(piece) > max_chars:
            break
        parts.append(piece)
        total += len(piece)
    return "\n".join(f"- {p}" for p in parts) if parts else "No matching /docs context found."