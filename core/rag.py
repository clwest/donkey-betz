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

# S2818 (2799 §8 item #1) — discovery-layer enforcement pilot for
# DOC_LIFECYCLE §2c "sole authoritative counts source" convention.
# Applied ALWAYS in top_k (independent of boost_hints) so PA search_docs
# calls (which pass boost_hints=False) benefit. Exact-path match (not
# regex) to reduce rot fragility. Pilot scope is 1 doc; expand only after
# empirical evidence of success@3 movement on T3 (c) counts scenarios.
# Follow-up: migrate authority weighting into embedding-based retrieval
# once that becomes the default (kb_tool.semantic_search).
AUTHORITY_FILE_BONUS = {
    # Magnitude matches legacy _file_bonus (8). S2818 OP3 post-authoring
    # SIGN empirically showed +20 satisfies the counts-query success
    # criterion but degrades non-counts how-to retrieval (T3 B1 shape:
    # "add a new spider to the network" gets dominated by inventory
    # chunks; topics/spider-network.md falls out of top-3). +8 is the
    # tuned value tried first per Rigby's ship/iterate stop-condition.
    "PLATFORM_INVENTORY.md": 8,
}

# S2820 — orientation-doc exclusion (last lexical policy in the discovery-
# layer pilot chain S2818/S2819/S2820, declared "feature complete" at
# S2820 close per Chris directive; S2821+ evaluates embedding-based
# retrieval against the benchmark corpus this arc built).
#
# Rationale: 00-START-NEXT-SESSION.md is a transient orientation doc
# regenerated every session close. It frequently contains raw example
# text ("Q5 non-counts query: 'add a new spider to the network'") to
# describe queued work items. When docs cascade re-embeds it, that
# example text becomes searchable and the doc dominates queries that
# literally reference the example — a same-class instance of T3 §7 C2
# start-here-doc-example-text contamination, surfaced live during S2819.
#
# Skip these paths entirely in top_k. Documents are still on disk,
# still readable, still in _index.json — just not searchable via the
# lexical top_k lane. Empirical evidence from S2820 open SIGN Q1
# baseline: 00-START-NEXT-SESSION.md#3 was #1 for "add a new spider to
# the network" AND its exclusion causes zero regression on 3 unrelated
# baseline queries (counts / handoff-intent / self-reference).
_EXCLUDED_FILE_PATHS = frozenset({
    "00-START-NEXT-SESSION.md",
})

# S2819 Shape C — query-intent gating for AUTHORITY_FILE_BONUS.
# Per S2818 envelope §6 follow-on: static per-chunk boost floods the
# ranker on non-counts queries. This gate applies the boost only when the
# query has count/inventory-listing intent. "list all" added per Rigby
# open SIGN Q2 empirical evidence: PLATFORM_INVENTORY.md already dominates
# "list all spiders" today (post-S2818) and gating on counts alone would
# regress that legitimate inventory query. Pattern set kept minimal —
# extension requires fresh SIGN cycle.
_COUNT_INTENT_PATTERNS = (
    "how many",
    "how much",
    "number of",
    "count of",
    "total",
    "list all",
)


def _looks_like_count_query(question: str | None) -> bool:
    """S2819 pilot — detect count/inventory intent in a query."""
    if not question:
        return False
    q = question.lower()
    return any(p in q for p in _COUNT_INTENT_PATTERNS)

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

def _authority_bonus(path: str) -> int:
    """S2818 pilot — exact-path authority boost per DOC_LIFECYCLE §2c."""
    if not path:
        return 0
    # Corpus stores paths without the leading 'docs/' prefix, but callers
    # may pass a full path. Normalize by stripping the prefix once.
    key = path[5:] if path.startswith("docs/") else path
    return AUTHORITY_FILE_BONUS.get(key, 0)

def top_k(
    question: str,
    k: int = 8,
    boost_hints: bool = True,
    authority_gate: bool | None = None,
) -> list[dict]:
    """Rank corpus chunks by token-overlap against ``question``.

    boost_hints=True preserves the legacy askdocs CLI behavior (learning-
    loop bias from LEARNING_LOOP_HINTS + PREF_FILE_BONUS). Pass False for
    general-purpose doc search where that bias is wrong (e.g., the
    Session 1142 ``search_docs`` PA tool).

    Authority-anchor boosts (AUTHORITY_FILE_BONUS) are GATED on query
    intent per S2819 Shape C. When ``authority_gate`` is None (default),
    it's computed from the question via ``_looks_like_count_query`` —
    boost fires only for count/inventory-listing intent, preserving the
    S2818 primary criterion while eliminating the non-counts regression.
    Callers may pass ``True`` / ``False`` to force the gate on/off (used
    by tests and any future intent-aware layers).
    """
    if not CORPUS_PATH.exists():
        return []
    q = question.lower()
    q_terms = set(q.split())
    if authority_gate is None:
        authority_gate = _looks_like_count_query(question)
    scored = []
    with CORPUS_PATH.open() as f:
        for line in f:
            row = json.loads(line)
            # S2820: skip orientation-only docs entirely.
            if row.get("file", "") in _EXCLUDED_FILE_PATHS:
                continue
            t = row["text"]
            tl = t.lower()

            # base: shared token overlap
            base = sum(1 for w in q_terms if w in tl)

            if boost_hints:
                base += _hint_score(tl)
                base += _file_bonus(row.get("file", ""))

            # S2819: authority boost is gated on query intent (S2818 shipped
            # unconditional; empirical monoculture regression required
            # gating — see S2819 envelope §5).
            if authority_gate:
                base += _authority_bonus(row.get("file", ""))

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