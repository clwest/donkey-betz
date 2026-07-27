"""
Canonical Briefing service — S2985.

Generates an LLM briefing (cards + citations) for a canonical summary doc
by running scope-filtered pgvector retrieval against DocumentEmbedding and
summarizing the top chunks into per-section bullets.

Contract summary (spec deliverable 6f6c4122-a98f-48c2-a8b3-ab687b44cbf6):
- Scope root defaults to `dirname(anchor_path)` for v1 arc-folder scope.
- Retrieval joins Document.file_path startswith scope_root (Z3 keeps
  request/response ready for v2 /docs-wide toggle without API rework).
- One LLM call produces all sections (Rigby D1: cost/latency 5x over
  per-section calls); response_format={"type":"json_object"} pattern per
  core/agents/thinking_agent.py:670-683, no formal json_schema helper
  exists to reuse.
- Bullets carry citations; bullets with zero citations render "Insufficient
  support in canonical docs" (Z1 no-hallucination invariant).

Prompt version bump when the section prompt changes materially; part of
the cache key so old cached outputs invalidate.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from core.services.openai_client_factory import get_openai_client
from core.services.llm_call_wrapper import llm_call_span
from core.services.redis_lock import (
    acquire_singleton_lock,
    release_singleton_lock,
)

logger = logging.getLogger(__name__)

PROMPT_VERSION = "v2"
CACHE_TTL_SECONDS = 15 * 60
CACHE_KEY_PREFIX = "canonical_briefing:"
LOCK_TTL_SECONDS = 60
DEFAULT_MODEL = "gpt-5-mini"
DEFAULT_MAX_COMPLETION_TOKENS = 6000
SNIPPET_MAX_CHARS = 300
INSUFFICIENT_SUPPORT_MSG = "Insufficient support in canonical docs"
MAX_WORDS_PER_BULLET = 20

SECTION_ORDER = ("tldr", "decisions", "state", "risks", "next_actions")
SECTION_TITLES = {
    "tldr": "TL;DR",
    "decisions": "Key Decisions",
    "state": "Current State / Findings",
    "risks": "Risks / Unknowns",
    "next_actions": "Next Actions",
}
SECTION_QUERIES = {
    "tldr": "summary overview main points of this canonical document",
    "decisions": "key decisions made resolved verdicts approved chosen",
    "state": "current state findings observations status what is true now",
    "risks": "risks unknowns open questions blockers concerns pitfalls",
    "next_actions": "next actions follow-ups todo remaining work forward-carry",
}


class BriefingError(Exception):
    """Raised for briefing-generation failures that should surface to the caller."""


@dataclass
class Citation:
    document_id: str
    chunk_id: str
    path: str
    snippet: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "path": self.path,
            "snippet": self.snippet,
        }


def _sanitize_snippet(text: str) -> str:
    if not text:
        return ""
    cleaned = text.strip().replace("\x00", "")
    if len(cleaned) > SNIPPET_MAX_CHARS:
        cleaned = cleaned[: SNIPPET_MAX_CHARS - 1].rstrip() + "\u2026"
    return cleaned


def _cache_key(anchor_path: str, scope_root: str, anchor_mtime: float) -> str:
    raw = f"{anchor_path}|{scope_root}|{anchor_mtime}|{PROMPT_VERSION}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
    return f"{CACHE_KEY_PREFIX}{digest}"


def retrieve_scoped_chunks(
    query: str,
    scope_root: str,
    limit: int,
    similarity_threshold: float = 0.4,
) -> List[Dict[str, Any]]:
    """Scope-filtered pgvector retrieval over DocumentEmbedding.

    Mirrors the search_embeddings pattern in core/rag_integration.py but
    adds Document.file_path startswith scope_root filter pushdown BEFORE
    the slice. Arc-folder scope is small enough that the unindexed
    file_path column (Rigby C4 finding) is not a v1 perf concern.
    """
    from core.rag_integration import create_embedding
    from content.models import Document, DocumentEmbedding  # noqa: F401
    from pgvector.django import CosineDistance

    query_embedding = create_embedding(query)
    if not query_embedding:
        logger.warning("canonical_briefing: empty query embedding for %r", query[:80])
        return []

    scope_root = scope_root.rstrip("/") + "/"

    qs = (
        DocumentEmbedding.objects
        .filter(document__file_path__isnull=False)
        .exclude(document__file_path="")
        .filter(document__file_path__startswith=scope_root)
        .annotate(distance=CosineDistance("embedding_vector", query_embedding))
        .filter(distance__lte=1.0 - similarity_threshold)
        .select_related("document")
        .order_by("distance")[:limit]
    )

    results: List[Dict[str, Any]] = []
    for chunk in qs:
        doc = chunk.document
        similarity = 1.0 - float(chunk.distance)
        results.append(
            {
                "chunk_id": str(chunk.id),
                "document_id": str(doc.id),
                "path": doc.file_path,
                "content": chunk.chunk_text or "",
                "similarity": similarity,
            }
        )
    return results


def _build_prompt(
    anchor_path: str,
    scope_root: str,
    per_section_chunks: Dict[str, List[Dict[str, Any]]],
    max_bullets_per_section: int,
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for the single-call JSON summary.

    Passes the chunks with stable citation_key ordinals so the LLM can
    reference them without inventing document_ids.
    """
    system_prompt = (
        "You are a briefing writer. You will receive retrieved chunks from a "
        "canonical documentation folder and must produce a JSON-only briefing "
        "with 5 sections.\n\n"
        "Voice rules — the reader has no arc context:\n"
        f"- Each bullet ≤ {MAX_WORDS_PER_BULLET} words. One idea per bullet. Plain English.\n"
        "- Do NOT use opaque insider jargon (e.g. 'Cat D', 'xx99', 'Path A', "
        "'verdict cascade', 'T4', 'F-D-2') without expanding it in the same "
        "bullet. If a fact can't be said cleanly without such jargon, drop it.\n"
        "- No stacked sub-clauses. If a bullet needs 'and', 'while', 'along "
        "with', or 'depending on', split it into two bullets or drop the "
        "caveat. Prefer 8-15 words over 20.\n"
        "- Write concrete facts and decisions, not meta-descriptions of the "
        "document ('this summary is authored with authority X').\n\n"
        "Citation rules:\n"
        "- Each bullet MUST cite one or more chunks by their 'citation_key' "
        "(integer). If a section has no supporting chunks, return an empty "
        "bullets array; do not invent facts.\n"
        "- Do not add citations that don't appear in the provided chunks."
    )

    context_blocks: List[str] = []
    context_blocks.append(f"Anchor doc: {anchor_path}")
    context_blocks.append(f"Scope: {scope_root}")
    context_blocks.append("")

    for section_key in SECTION_ORDER:
        chunks = per_section_chunks.get(section_key, [])
        context_blocks.append(
            f"## {section_key} ({SECTION_TITLES[section_key]}) — {len(chunks)} retrieved chunk(s)"
        )
        for chunk in chunks:
            citation_key = chunk["citation_key"]
            path = chunk["path"]
            content = chunk["content"][:1200]
            context_blocks.append(
                f"[citation_key={citation_key} path={path}]\n{content}"
            )
        context_blocks.append("")

    context_text = "\n".join(context_blocks)

    user_prompt = f"""{context_text}

Return JSON with this exact shape:

{{
  "sections": [
    {{
      "key": "tldr",
      "bullets": [
        {{"text": "...", "citation_keys": [1, 4]}}
      ]
    }},
    {{"key": "decisions", "bullets": [...]}},
    {{"key": "state", "bullets": [...]}},
    {{"key": "risks", "bullets": [...]}},
    {{"key": "next_actions", "bullets": [...]}}
  ]
}}

Rules:
- Each section MUST appear in the sections array with the exact key.
- Each bullet's "citation_keys" MUST be a non-empty array of integers that appear as citation_key in the provided chunks. If a section has no supporting chunks, return {{"bullets": []}} for that section.
- Maximum {max_bullets_per_section} bullets per section. Prefer fewer, tighter bullets over the maximum.
- Bullet text: ONE idea, ≤ {MAX_WORDS_PER_BULLET} words, plain English, no markdown, no leading dash, no jargon acronyms unexpanded.
- Return ONLY the JSON object. No prose, no code fences.
"""
    return system_prompt, user_prompt


def _call_llm(system_prompt: str, user_prompt: str, model: str) -> str:
    client = get_openai_client()
    with llm_call_span(
        provider="openai",
        model=model,
        agent_name="canonical_briefing",
    ) as span:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_completion_tokens=DEFAULT_MAX_COMPLETION_TOKENS,
            response_format={"type": "json_object"},
        )
        try:
            span.attach_response(response)
        except Exception:  # noqa: BLE001 - telemetry attach must never mask body
            logger.debug("canonical_briefing: span.attach_response failed", exc_info=True)
    return response.choices[0].message.content or ""


def _parse_and_validate(
    raw_json: str,
    citation_lookup: Dict[int, Dict[str, Any]],
    max_bullets_per_section: int,
) -> tuple[List[Dict[str, Any]], bool]:
    """Parse LLM JSON, drop invalid citation keys, enforce section shape.

    Returns (sections, llm_valid_json). Rigby A2 ZO1 fold: surface JSON parse
    failure as an explicit flag so consumers can distinguish "LLM produced
    a valid empty briefing" from "LLM output was malformed and we bailed"
    (both would otherwise render as empty sections).
    """
    llm_valid_json = True
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError:
        logger.warning("canonical_briefing: LLM returned invalid JSON, falling back")
        payload = {}
        llm_valid_json = False

    raw_sections = {
        s.get("key"): s
        for s in payload.get("sections", [])
        if isinstance(s, dict)
    }

    sections: List[Dict[str, Any]] = []
    for section_key in SECTION_ORDER:
        raw = raw_sections.get(section_key, {})
        raw_bullets = raw.get("bullets") if isinstance(raw, dict) else None
        if not isinstance(raw_bullets, list):
            raw_bullets = []
        bullets: List[Dict[str, Any]] = []
        for bullet in raw_bullets[:max_bullets_per_section]:
            if not isinstance(bullet, dict):
                continue
            text = str(bullet.get("text", "")).strip()
            if not text:
                continue
            keys = bullet.get("citation_keys") or []
            citations: List[Dict[str, Any]] = []
            seen_chunk_ids: set[str] = set()
            for key in keys:
                try:
                    key_int = int(key)
                except (TypeError, ValueError):
                    continue
                chunk = citation_lookup.get(key_int)
                if chunk is None:
                    continue
                if chunk["chunk_id"] in seen_chunk_ids:
                    continue
                seen_chunk_ids.add(chunk["chunk_id"])
                citations.append(
                    Citation(
                        document_id=chunk["document_id"],
                        chunk_id=chunk["chunk_id"],
                        path=chunk["path"],
                        snippet=_sanitize_snippet(chunk["content"]),
                    ).to_dict()
                )
            if not citations:
                bullets.append(
                    {
                        "text": INSUFFICIENT_SUPPORT_MSG,
                        "citations": [],
                        "original_text": text,
                    }
                )
                continue
            bullets.append({"text": text, "citations": citations})
        sections.append(
            {
                "key": section_key,
                "title": SECTION_TITLES[section_key],
                "bullets": bullets,
            }
        )
    return sections, llm_valid_json


def build_briefing(
    anchor_path: str,
    scope_root: str,
    max_chunks_per_section: int = 12,
    max_bullets_per_section: int = 10,
    model: Optional[str] = None,
    force_refresh: bool = False,
) -> Dict[str, Any]:
    """Return the briefing payload for an anchor doc.

    Layers:
    1. Cache lookup (skipped when force_refresh=True).
    2. Singleton lock via redis_lock — prevents N concurrent identical LLM
       calls when the cache is cold (Rigby D3).
    3. Scope-filtered retrieval per section.
    4. Single LLM call for all sections; parse and validate citations
       against the chunks we actually retrieved.
    5. Cache the response for CACHE_TTL_SECONDS.

    Raises BriefingError on unrecoverable failure (e.g., anchor missing).
    """
    base = Path(settings.BASE_DIR).resolve()
    anchor_full = (base / anchor_path).resolve()
    try:
        anchor_full.relative_to(base)
    except ValueError as exc:
        raise BriefingError("Invalid anchor_path - resolves outside repository") from exc
    if not anchor_full.exists() or not anchor_full.is_file():
        raise BriefingError(f"Anchor doc not found: {anchor_path}")

    anchor_mtime = anchor_full.stat().st_mtime
    cache_key = _cache_key(anchor_path, scope_root, anchor_mtime)

    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return {**cached, "cache": {"hit": True, "ttl_seconds": CACHE_TTL_SECONDS}}

    lock_name = f"canonical_briefing:{cache_key}"
    acquired = acquire_singleton_lock(lock_name, ttl=LOCK_TTL_SECONDS)
    try:
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached is not None:
                return {**cached, "cache": {"hit": True, "ttl_seconds": CACHE_TTL_SECONDS}}

        per_section_chunks: Dict[str, List[Dict[str, Any]]] = {}
        citation_lookup: Dict[int, Dict[str, Any]] = {}
        next_key = 1
        seen_chunk_ids: Dict[str, int] = {}

        for section_key in SECTION_ORDER:
            query = SECTION_QUERIES[section_key]
            chunks = retrieve_scoped_chunks(
                query=query,
                scope_root=scope_root,
                limit=max_chunks_per_section,
            )
            annotated: List[Dict[str, Any]] = []
            for chunk in chunks:
                chunk_id = chunk["chunk_id"]
                if chunk_id in seen_chunk_ids:
                    citation_key = seen_chunk_ids[chunk_id]
                else:
                    citation_key = next_key
                    seen_chunk_ids[chunk_id] = citation_key
                    citation_lookup[citation_key] = chunk
                    next_key += 1
                annotated.append({**chunk, "citation_key": citation_key})
            per_section_chunks[section_key] = annotated

        total_chunks = len(citation_lookup)
        if total_chunks == 0:
            payload = _empty_briefing_payload(anchor_path, scope_root)
        else:
            system_prompt, user_prompt = _build_prompt(
                anchor_path=anchor_path,
                scope_root=scope_root,
                per_section_chunks=per_section_chunks,
                max_bullets_per_section=max_bullets_per_section,
            )
            raw_json = _call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=model or DEFAULT_MODEL,
            )
            sections, llm_valid_json = _parse_and_validate(
                raw_json=raw_json,
                citation_lookup=citation_lookup,
                max_bullets_per_section=max_bullets_per_section,
            )
            payload = {
                "anchor_path": anchor_path,
                "scope": {"root": scope_root},
                "generated_at": timezone.now().isoformat(),
                "prompt_version": PROMPT_VERSION,
                "sections": sections,
                "llm_valid_json": llm_valid_json,
                "retrieval": {
                    "total_unique_chunks": total_chunks,
                    "per_section_counts": {
                        k: len(per_section_chunks[k]) for k in SECTION_ORDER
                    },
                },
            }
        cache.set(cache_key, payload, CACHE_TTL_SECONDS)
        return {**payload, "cache": {"hit": False, "ttl_seconds": CACHE_TTL_SECONDS}}
    finally:
        if acquired:
            release_singleton_lock(lock_name)


def _empty_briefing_payload(anchor_path: str, scope_root: str) -> Dict[str, Any]:
    return {
        "anchor_path": anchor_path,
        "scope": {"root": scope_root},
        "generated_at": timezone.now().isoformat(),
        "prompt_version": PROMPT_VERSION,
        "sections": [
            {
                "key": key,
                "title": SECTION_TITLES[key],
                "bullets": [],
            }
            for key in SECTION_ORDER
        ],
        "retrieval": {
            "total_unique_chunks": 0,
            "per_section_counts": {k: 0 for k in SECTION_ORDER},
        },
        "empty_reason": "no_chunks_in_scope",
    }
