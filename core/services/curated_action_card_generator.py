"""Session 1140 (A) — LLM action-card generator for curated picks.

Generates one action card per curated cluster in a snapshot. The card
suggests a concrete action_type + 3-5 ordered steps + (optional)
outreach draft a user could send. Cards land as `entry_type='action_card'`
rows on `CuratedSignalEntry` paired 1:1 with their `cluster_pick`.

Per Rigby's lock #2 (conversation pa-d19c1674b936): this runs
**asynchronously after snapshot creation**, NOT inside the curator's
deterministic snapshot transaction. Snapshot success must not depend
on OpenAI uptime. The generator's job is to fill in action_card rows
post-hoc, with retries + bounded budget.

Per Rigby's lock #3: mirror signal-studio's existing ActionCard shape
(action_type / title / steps / outreach_draft / status) so the
frontend can reuse what it already renders. `generated_by` carries
audit metadata (model name or "fallback_placeholder" when the LLM
call fails — we always write SOMETHING so the UI never has to render
a half-row).

────────────────────────────────────────────────────────────────────────
Idempotency: `generate_for_snapshot` is safe to re-run. It looks up
existing `action_card` rows by `(snapshot, cluster)` and skips
clusters that already have one. So the celery follow-on can retry on
transient OpenAI errors without doubling spend.
────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Iterable

from django.db import transaction

from core.models_signal_intelligence import (
    CuratedSignalEntry,
    CuratedSignalSnapshot,
    SignalCluster,
)

logger = logging.getLogger(__name__)


# ─── Contract constants ───────────────────────────────────────────────


GENERATOR_MODEL = "gpt-5-mini"
GENERATOR_VERSION = "v1_session_1140"
# Output budget: action cards themselves are short (1 title + 3-5
# steps + 1-2 sentence outreach ≈ ~250 tokens). BUT gpt-5-mini is a
# reasoning model — reasoning tokens consume `max_completion_tokens`
# BEFORE any output is emitted. With a 600-token cap, the empirical
# observation was 100% empty-content responses (reasoning ate it all),
# triggering 100% fallback rate. 1500 leaves comfortable headroom:
# ~1000 reasoning + ~500 output for the JSON action card. Cost impact
# is negligible (~$0.003/card on gpt-5-mini at current pricing).
MAX_OUTPUT_TOKENS = 1500

# Action type vocab — must match CuratedSignalEntry.ACTION_TYPE_CHOICES.
VALID_ACTION_TYPES = {"investigate", "invest", "build", "hire", "pitch"}
DEFAULT_ACTION_TYPE = "investigate"  # safe fallback when LLM disagrees

# Step count guard. We accept anything in [MIN_STEPS, MAX_STEPS]; outside
# that range we treat the LLM output as malformed and fall back.
MIN_STEPS = 2
MAX_STEPS = 6

# Priority enum for individual steps. Anything else gets normalized to
# "medium" so the frontend doesn't have to defend against arbitrary
# values.
VALID_STEP_PRIORITIES = {"high", "medium", "low"}


# ─── System prompt ────────────────────────────────────────────────────


SYSTEM_PROMPT = """You convert clustered intelligence signals into a single concrete action card a busy founder could execute today.

Each cluster represents a real-world trend / opportunity / risk detected from web/news/social signals. Your job is to read the cluster summary + sample evidence and propose ONE next action.

Output JSON with exactly these keys:
  - action_type: one of investigate, invest, build, hire, pitch
  - title: short imperative (≤80 chars) e.g. "Open a discovery call with two Spacex customers"
  - steps: array of 3-5 objects, each {step: str, priority: "high"|"medium"|"low"}
  - outreach_draft: 1-3 sentence DM/email the user could copy + send (optional, "" if not applicable)

Rules:
  - Be CONCRETE. "Research more" is rejected; "Email Sara at Anthropic re. Claude 4.7 enterprise pricing" is accepted.
  - Match action_type to cluster character: investigate (unclear/early signal), invest (capital deployment), build (product opportunity), hire (talent signal), pitch (sales opportunity).
  - Steps in execution order, highest priority first.
  - Outreach is for hire/pitch/invest types primarily; for investigate/build it's often "".
  - JSON only. No prose around it. No markdown fences."""


# ─── Cluster → prompt ─────────────────────────────────────────────────


def _build_user_prompt(cluster: SignalCluster) -> str:
    """Render the cluster context the LLM uses to write the action card.

    Keeps the prompt small (≤~1500 tokens) by capping evidence at the
    first 5 spider items and truncating long fields. Cost discipline
    matters because this fires for every curated cluster.
    """
    # Pull a few representative sample signals from the cluster row.
    sample_signals = []
    raw_samples = (cluster.sample_signals or [])[:5] if hasattr(cluster, 'sample_signals') else []
    for s in raw_samples:
        if not isinstance(s, dict):
            continue
        headline = (s.get("headline") or s.get("title") or "")[:200]
        source = (s.get("source") or s.get("source_domain") or "")[:80]
        if headline:
            sample_signals.append(f"  - {headline} [{source}]")

    evidence_block = "\n".join(sample_signals) if sample_signals else "  (no sample signals available)"

    lines = [
        f"Cluster: {cluster.name or '(unnamed)'}",
        f"Pattern type: {cluster.pattern_type or 'unknown'}",
        f"Strength: {(cluster.strength or 0.0):.2f}",
        f"Confidence: {(cluster.confidence or 0.0):.2f}",
        "",
        "Sample evidence:",
        evidence_block,
        "",
        "Write the action card now. JSON only.",
    ]
    return "\n".join(lines)


# ─── LLM call + parse ─────────────────────────────────────────────────


def _strip_fences(text: str) -> str:
    """Remove ```json ... ``` markdown fences if the LLM ignored the rule."""
    t = text.strip()
    if t.startswith("```"):
        # Strip opening fence (with optional language tag) + trailing fence.
        t = re.sub(r"^```(?:json)?\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    return t.strip()


def _normalize_card(raw: dict) -> dict:
    """Coerce a raw LLM JSON dict into the storage shape.

    Validates required keys, normalizes action_type + step priorities
    to the allowed vocab, and enforces step count bounds. Raises
    ValueError on hard failures (missing required field, invalid
    JSON shape) so the caller can fall back to the placeholder card.
    """
    if not isinstance(raw, dict):
        raise ValueError(f"expected JSON object, got {type(raw).__name__}")

    action_type = str(raw.get("action_type") or "").strip().lower()
    if action_type not in VALID_ACTION_TYPES:
        # Don't fail — soft-fall to investigate. The point is to ALWAYS
        # produce a card; bad action_type is a UI quirk, not a blocker.
        logger.info(
            "[action-card-gen] LLM returned action_type=%r — coercing to %r",
            action_type, DEFAULT_ACTION_TYPE,
        )
        action_type = DEFAULT_ACTION_TYPE

    title = str(raw.get("title") or "").strip()
    if not title:
        raise ValueError("title is required")
    title = title[:500]  # match column max_length

    steps_raw = raw.get("steps") or []
    if not isinstance(steps_raw, list):
        raise ValueError(f"steps must be a list, got {type(steps_raw).__name__}")
    if len(steps_raw) < MIN_STEPS:
        raise ValueError(f"steps count {len(steps_raw)} < MIN_STEPS {MIN_STEPS}")
    # Truncate over-long step lists rather than reject — the LLM
    # sometimes overshoots and we don't want to throw away a perfectly
    # good first 6 steps.
    steps_raw = steps_raw[:MAX_STEPS]

    steps: list[dict] = []
    for s in steps_raw:
        if isinstance(s, str):
            steps.append({"step": s.strip(), "priority": "medium"})
            continue
        if not isinstance(s, dict):
            continue
        step_text = str(s.get("step") or "").strip()
        if not step_text:
            continue
        priority = str(s.get("priority") or "medium").strip().lower()
        if priority not in VALID_STEP_PRIORITIES:
            priority = "medium"
        steps.append({"step": step_text, "priority": priority})

    if len(steps) < MIN_STEPS:
        raise ValueError(f"only {len(steps)} valid step objects after normalize")

    outreach = str(raw.get("outreach_draft") or "").strip()

    return {
        "action_type": action_type,
        "action_title": title,
        "action_steps": steps,
        "outreach_draft": outreach,
    }


def _fallback_card(cluster: SignalCluster) -> dict:
    """Last-resort card when the LLM fails or returns junk.

    Mirrors signal-studio's existing placeholder from
    `/api/signals/{id}/generate-action` so UX stays consistent.
    Generic but valid — the user gets SOMETHING to look at rather
    than an empty card slot. `generated_by='fallback_placeholder'`
    on the row marks it for audit.
    """
    category = (cluster.pattern_type or "signal").replace("_", " ")
    return {
        "action_type": DEFAULT_ACTION_TYPE,
        "action_title": f"Next steps: {cluster.name or 'unnamed cluster'}"[:500],
        "action_steps": [
            {"step": f"Research deeper into {category} signal", "priority": "high"},
            {"step": "Validate key claims with primary sources", "priority": "high"},
            {"step": "Identify stakeholders who need to know", "priority": "medium"},
            {"step": "Draft action plan with 30/60/90 day milestones", "priority": "medium"},
        ],
        "outreach_draft": "",
    }


def _llm_generate_card(cluster: SignalCluster) -> tuple[dict, str]:
    """Single LLM call. Returns (card_dict, generated_by_label).

    Always returns a usable card. On any failure (network, JSON parse,
    normalize), logs + returns the fallback card with the label
    'fallback_placeholder' so the caller can persist regardless.
    """
    try:
        from core.services.openai_client_factory import get_openai_client
        client = get_openai_client()
        response = client.chat.completions.create(
            model=GENERATOR_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(cluster)},
            ],
            max_completion_tokens=MAX_OUTPUT_TOKENS,
        )
        text = response.choices[0].message.content or ""
    except Exception as e:
        logger.warning(
            "[action-card-gen] LLM call failed for cluster=%s: %s",
            cluster.id, e,
        )
        return _fallback_card(cluster), "fallback_placeholder"

    if not text.strip():
        # gpt-5-mini reasoning consumed the entire token budget without
        # emitting any output — most common failure mode in practice.
        # Distinct log so we know to bump MAX_OUTPUT_TOKENS if this
        # spikes (vs. genuine JSON parse failures which mean the prompt
        # needs work).
        logger.warning(
            "[action-card-gen] empty response from %s for cluster=%s "
            "(likely max_completion_tokens consumed by reasoning) — "
            "falling back",
            GENERATOR_MODEL, cluster.id,
        )
        return _fallback_card(cluster), "fallback_placeholder"

    try:
        raw = json.loads(_strip_fences(text))
        card = _normalize_card(raw)
    except (ValueError, json.JSONDecodeError) as e:
        logger.info(
            "[action-card-gen] parse/normalize failed for cluster=%s "
            "(falling back): %s\nraw=%r",
            cluster.id, e, text[:400],
        )
        return _fallback_card(cluster), "fallback_placeholder"

    return card, GENERATOR_MODEL


# ─── Public API ───────────────────────────────────────────────────────


@dataclass
class GenerationResult:
    """Summary of one `generate_for_snapshot` run."""
    snapshot_id: str
    generated: int = 0
    skipped_existing: int = 0
    fallback_count: int = 0
    entries_created: list[CuratedSignalEntry] = field(default_factory=list)


def generate_for_snapshot(
    snapshot_id: str,
    *,
    only_missing: bool = True,
) -> GenerationResult:
    """Generate action_card rows for every cluster_pick in a snapshot.

    `only_missing=True` (default) skips clusters that already have an
    `action_card` row — makes this safe to re-invoke from a retried
    celery task. Set `False` if you want to regenerate everything (will
    fail on the unique constraint without first deleting old rows;
    caller is responsible for cleanup in that case).
    """
    try:
        snapshot = (
            CuratedSignalSnapshot.objects
            .prefetch_related('entries__cluster')
            .get(id=snapshot_id)
        )
    except CuratedSignalSnapshot.DoesNotExist:
        logger.warning(
            "[action-card-gen] snapshot %s not found — nothing to do",
            snapshot_id,
        )
        return GenerationResult(snapshot_id=str(snapshot_id))

    result = GenerationResult(snapshot_id=str(snapshot.id))

    picks = list(
        snapshot.entries.filter(entry_type='cluster_pick').select_related('cluster')
    )
    if not picks:
        logger.info(
            "[action-card-gen] snapshot %s has no cluster_picks — skipping",
            snapshot.id,
        )
        return result

    # Build a set of (snapshot, cluster) pairings that already have
    # action cards so we can skip in O(1).
    existing_action_cluster_ids: set = set()
    if only_missing:
        existing_action_cluster_ids = set(
            snapshot.entries
            .filter(entry_type='action_card')
            .values_list('cluster_id', flat=True)
        )

    for pick in picks:
        if pick.cluster_id in existing_action_cluster_ids:
            result.skipped_existing += 1
            continue

        cluster = pick.cluster
        card, generated_by = _llm_generate_card(cluster)
        if generated_by == "fallback_placeholder":
            result.fallback_count += 1

        # Persist as a sibling row — same snapshot, same cluster, same
        # rank (so action_cards sort alongside their pick), entry_type
        # switches to action_card and the action_* fields populate.
        with transaction.atomic():
            entry = CuratedSignalEntry.objects.create(
                snapshot=snapshot,
                cluster=cluster,
                rank=pick.rank,
                entry_type='action_card',
                # cluster_pick-only fields stay NULL.
                curated_score=None,
                group_key=None,
                strength_at_pick=None,
                cluster_size_at_pick=None,
                age_hours_at_pick=None,
                # action_card fields from the LLM (or fallback).
                action_type=card["action_type"],
                action_title=card["action_title"],
                action_steps=card["action_steps"],
                outreach_draft=card["outreach_draft"],
                action_status='draft',
                generated_by=generated_by,
            )
        result.entries_created.append(entry)
        result.generated += 1

    logger.info(
        "[action-card-gen] snapshot=%s done: generated=%d skipped_existing=%d "
        "fallback=%d",
        snapshot.id, result.generated, result.skipped_existing,
        result.fallback_count,
    )
    return result


__all__ = [
    "GenerationResult",
    "GENERATOR_MODEL",
    "GENERATOR_VERSION",
    "MAX_OUTPUT_TOKENS",
    "VALID_ACTION_TYPES",
    "VALID_STEP_PRIORITIES",
    "_build_user_prompt",
    "_fallback_card",
    "_normalize_card",
    "_strip_fences",
    "generate_for_snapshot",
]
