"""SignalCuratorService — Phase 2 (Rigby's path C, Session 1131).

Selects the daily Top-N curated signal clusters from the Phase 1
quality-bar pool (`status=active AND strength>=0.6`). Persists each
run as a `CuratedSignalSnapshot` + child `CuratedSignalEntry` rows,
then emits a `signal.curated_published` fleet event so signal-studio
can refresh its Curated tab.

Rigby's four locks (conversation pa-d19c1674b936):

1. **Dedup**: hard-cap grouping, NOT a penalty term in the score.
   Group key = `f"{pattern_type}::{topic_key}"` where `topic_key`
   normalizes the first keyword (or title fallback). Pick the
   single best-scoring cluster per group; rank winners globally.
2. **Score**: `0.9 * strength + 0.1 * recency_decay`. Size dropped
   from the formula — Rigby agreed it correlates with strength
   (the binned histogram from Session 1131 close shows r≈0.7).
3. **Emission**: Top 10 per snapshot after dedup. Optional per-
   pattern_type cap at `max(2, ceil(N/4))` (= 3 for N=10) so one
   pattern type can't dominate.
4. **Snapshot metadata**: scoring_formula_version, dedup_strategy,
   pattern_type_cap, excluded_duplicates audit list. Stored
   verbatim on the snapshot row so the audit trail explains "why
   this set, why in this order" without rerunning the score.

The curator is pure-deterministic — same inputs produce same
snapshot (modulo time, which factors into recency_decay). No LLMs.

────────────────────────────────────────────────────────────────────────
Tiebreaker for equal scores: cluster.seq ASC (older row wins). Stable
ordering matters because the snapshot is the source of truth signal-
studio's Curated tab reads from.
────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass, field
from typing import Iterable

from django.utils import timezone

from core.models_signal_intelligence import (
    CuratedSignalEntry,
    CuratedSignalSnapshot,
    SignalCluster,
)
from core.services.fleet_signals import cluster_envelope

logger = logging.getLogger(__name__)


# ─── Phase 2 contract constants (Rigby's locks) ───────────────────────


SCORING_FORMULA_VERSION = "v1_strength_0.9_recency_0.1_tau72"
DEDUP_STRATEGY = "group_best_by(pattern_type, topic_key)"

# Score weights — locked: 0.9 strength, 0.1 recency_decay, size dropped.
STRENGTH_WEIGHT = 0.9
RECENCY_WEIGHT = 0.1
# Decay tau in hours: exp(-age_h / 72) = 0.5 at 50h, 0.37 at 72h, 0.14 at 144h.
RECENCY_TAU_HOURS = 72.0

# Default snapshot size.
DEFAULT_TOP_N = 10

# Per-pattern_type cap rule (Rigby's lock 1 follow-up):
#   "max(2, ceil(N/4))"
# For N=10 → cap=3. For N=20 → cap=5. For N<8 → cap=2.
# Stored in pattern_type_cap.rule on the snapshot for audit.
PATTERN_TYPE_CAP_RULE = "max(2, ceil(N/4))"


def compute_pattern_type_cap(top_n: int) -> int:
    """Cap per pattern_type. `max(2, ceil(N/4))` per Rigby's lock."""
    return max(2, math.ceil(top_n / 4))


# ─── Topic-key normalization ──────────────────────────────────────────


_TOPIC_KEY_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")


def normalize_topic_key(raw: str) -> str:
    """Normalize a string into a stable dedup key.

    lower → strip non-alphanumerics → collapse runs → trim. Empty input
    yields empty string; caller should fall back to a different source.
    """
    if not raw:
        return ""
    lowered = raw.strip().lower()
    cleaned = _TOPIC_KEY_NORMALIZE_RE.sub("_", lowered).strip("_")
    return cleaned


def topic_key_for_cluster(cluster: SignalCluster) -> str:
    """Derive the per-cluster topic_key used for dedup grouping.

    Smoke result from Session 1131 Phase 2 close: the upstream
    `keywords` field mixes pattern-type INDICATOR words (e.g. "want",
    "suggestion", "missing", "new") with actual TOPIC words (e.g.
    "react", "security", "ai"). Naively picking `keywords[0]` lands
    on indicator words ~half the time, which makes groups like
    "demand_spike::suggestion" — useless for dedup.

    Fix: prefer the cluster's NAME first (which `_generate_topic_name`
    in signal_aggregation_service explicitly leads with the topic),
    then fall back to keywords. Both paths apply the pattern-type
    stop-word filter so indicator words can't slip through.

    Priority: name (stop-word-stripped) → first non-stop keyword
    → UUID prefix.

    Examples:
        name='React demand spike'              → 'react'
        name='Marketing sentiment shift'       → 'marketing'
        name='', keywords=['ai','want']        → 'ai'
        name='', keywords=['want']             → '<uuid_prefix>'
    """
    # Pattern-type indicator words from
    # signal_aggregation_service.PATTERN_TYPE_KEYWORDS plus a few
    # leak-through cluster-name labels. Keep in sync if the upstream
    # keyword vocabulary changes.
    #
    # Includes normalized forms of multi-word phrases (e.g. "looking
    # for" → "looking_for") because keywords are normalized BEFORE
    # the stop-word check.
    stop_words = {
        # Pattern-type label suffixes from cluster name generation.
        "demand", "spike", "trend", "emerging", "emergence", "new",
        "sentiment", "shift", "opportunity", "window", "knowledge",
        "gap", "competitive", "signal", "market", "movement", "skill",
        "content", "user", "need",
        # PATTERN_TYPE_KEYWORDS indicators that bleed into the keywords
        # JSON field. List from signal_aggregation_service.py — kept
        # in both single-word and normalized-multi-word form.
        "want", "looking", "for", "looking_for", "seeking", "require",
        "how", "to", "how_to", "best", "way", "best_way", "recommend",
        "recommendation", "suggestion", "help", "with", "help_with",
        "trending", "rising", "growing", "gaining", "breakthrough",
        "innovative", "revolutionary", "next", "big", "next_big",
        "changing", "moving", "away", "moving_away", "no", "longer",
        "no_longer", "instead", "prefer", "better", "than",
        "better_than", "replaced", "obsolete", "chance", "limited",
        "time", "limited_time", "now", "urgent", "before", "deadline",
        "ending", "soon", "ending_soon", "act", "fast", "act_fast",
        "confused", "unclear", "don", "t", "understand",
        "don_t_understand", "what", "is", "what_is", "explain", "me",
        "help_me_understand", "struggling", "struggling_with",
        "hiring", "job", "position", "role", "career", "salary",
        "good", "hard", "find", "hard_to_find", "wish", "there", "was",
        "wish_there_was", "underserved", "missing", "more",
        "no_good_content", "gap_in", "need_more",
    }

    # 1. NAME first — _generate_topic_name leads with the topic.
    if cluster.name:
        for word in cluster.name.split():
            normalized = normalize_topic_key(word)
            if normalized and normalized not in stop_words:
                return normalized

    # 2. Keywords fallback — filter out pattern-type indicators.
    keywords = cluster.keywords or []
    for kw in keywords:
        normalized = normalize_topic_key(str(kw))
        if normalized and normalized not in stop_words:
            return normalized

    # 3. Last resort: UUID prefix so unrelated clusters with no
    # extractable topic don't all collapse into one group.
    return f"unknown_{str(cluster.id)[:8]}"


def group_key_for_cluster(cluster: SignalCluster) -> str:
    """Stable composite dedup key: `<pattern_type>::<topic_key>`."""
    return f"{cluster.pattern_type}::{topic_key_for_cluster(cluster)}"


# ─── Scoring ──────────────────────────────────────────────────────────


def compute_score(cluster: SignalCluster, now=None) -> tuple[float, float, float]:
    """Score one cluster. Returns `(score, strength, recency_decay)`.

    Composite: STRENGTH_WEIGHT * strength + RECENCY_WEIGHT * recency_decay.
    `recency_decay = exp(-age_hours / RECENCY_TAU_HOURS)`.

    Returns the components separately so the snapshot can record them
    on `CuratedSignalEntry` for audit.
    """
    now = now or timezone.now()
    strength = float(cluster.strength or 0.0)
    if cluster.detected_at:
        age_hours = max(
            (now - cluster.detected_at).total_seconds() / 3600.0,
            0.0,
        )
    else:
        # No detected_at → no recency credit. Pure strength.
        age_hours = float("inf")
    recency_decay = math.exp(-age_hours / RECENCY_TAU_HOURS) if math.isfinite(age_hours) else 0.0
    score = STRENGTH_WEIGHT * strength + RECENCY_WEIGHT * recency_decay
    return score, strength, recency_decay


# ─── Pool fetch (Phase 1 quality bar) ─────────────────────────────────


def fetch_pool() -> list[SignalCluster]:
    """Phase 2 pool = clusters that pass Phase 1's emit bar.

    Mirrors `core.services.fleet_signals.QUALITY_BAR_*` so the curator
    is scoring exactly the candidates that signal-studio already saw
    via the pull endpoint / event stream. Pulled into a list (not a
    queryset) so we can pass the same objects through scoring, dedup,
    and ranking without refetching.
    """
    from core.services.fleet_signals import (
        QUALITY_BAR_MIN_STRENGTH,
        QUALITY_BAR_STATUS,
    )
    return list(
        SignalCluster.objects.filter(
            status=QUALITY_BAR_STATUS,
            strength__gte=QUALITY_BAR_MIN_STRENGTH,
        ).order_by("seq")
    )


# ─── Dedup + ranking ──────────────────────────────────────────────────


@dataclass
class ScoredCluster:
    """A cluster plus its score components, ready for dedup/ranking."""
    cluster: SignalCluster
    score: float
    strength: float
    recency_decay: float
    cluster_size: int
    age_hours: float
    group_key: str


@dataclass
class CurationResult:
    """Output of `curate_top_n` — the persisted snapshot + audit."""
    snapshot: CuratedSignalSnapshot
    entries: list[CuratedSignalEntry] = field(default_factory=list)
    pool_size: int = 0
    excluded_count: int = 0


def _score_pool(pool: Iterable[SignalCluster], now) -> list[ScoredCluster]:
    """Apply the scoring formula to each cluster in the pool."""
    out: list[ScoredCluster] = []
    for c in pool:
        score, strength, recency_decay = compute_score(c, now=now)
        sb = c.source_breakdown or {}
        cluster_size = sum(sb.values()) if sb else 0
        age_hours = (
            (now - c.detected_at).total_seconds() / 3600.0
            if c.detected_at else float("inf")
        )
        out.append(ScoredCluster(
            cluster=c,
            score=score,
            strength=strength,
            recency_decay=recency_decay,
            cluster_size=cluster_size,
            age_hours=age_hours,
            group_key=group_key_for_cluster(c),
        ))
    return out


def _pick_group_winners(
    scored: list[ScoredCluster],
) -> tuple[list[ScoredCluster], list[dict]]:
    """Lock #1: pick the single best-scoring cluster per group_key.

    Returns `(winners, excluded_audit)`. excluded_audit is a list of
    `{cluster_id, group_key, score, lost_to_cluster_id}` dicts ready
    to drop into `snapshot.excluded_duplicates`.

    Tiebreaker within a group: cluster.seq ASC (older row wins). Stable
    so the same pool produces the same winners across runs.
    """
    # Pre-sort: highest score first, then lowest seq (older) on ties.
    # Then a single pass through the list claims the first cluster per
    # group_key as the winner; subsequent same-group clusters are
    # excluded.
    sort_key = lambda sc: (-sc.score, sc.cluster.seq)
    ranked_in_group = sorted(scored, key=sort_key)

    winners_by_group: dict[str, ScoredCluster] = {}
    excluded: list[dict] = []
    for sc in ranked_in_group:
        existing = winners_by_group.get(sc.group_key)
        if existing is None:
            winners_by_group[sc.group_key] = sc
            continue
        # Already have a winner for this group — sc is excluded.
        excluded.append({
            "cluster_id": str(sc.cluster.id),
            "group_key": sc.group_key,
            "score": round(sc.score, 6),
            "lost_to_cluster_id": str(existing.cluster.id),
        })
    return list(winners_by_group.values()), excluded


def _apply_pattern_type_cap(
    winners: list[ScoredCluster], cap: int,
) -> tuple[list[ScoredCluster], list[dict]]:
    """Lock #1 (cap clause): no pattern_type may exceed `cap` entries.

    Iterates the globally-ranked winners and drops any cluster whose
    pattern_type has already filled its cap. Returns `(kept, capped_audit)`.
    """
    sort_key = lambda sc: (-sc.score, sc.cluster.seq)
    ranked = sorted(winners, key=sort_key)

    per_type_count: dict[str, int] = {}
    kept: list[ScoredCluster] = []
    capped: list[dict] = []
    for sc in ranked:
        pt = sc.cluster.pattern_type
        if per_type_count.get(pt, 0) >= cap:
            capped.append({
                "cluster_id": str(sc.cluster.id),
                "group_key": sc.group_key,
                "score": round(sc.score, 6),
                "reason": f"pattern_type_cap_{pt}",
            })
            continue
        per_type_count[pt] = per_type_count.get(pt, 0) + 1
        kept.append(sc)
    return kept, capped


# ─── Public entry point ───────────────────────────────────────────────


def curate_top_n(top_n: int = DEFAULT_TOP_N, *, now=None) -> CurationResult:
    """Run one curation pass, persist the snapshot, return the result.

    Caller is responsible for emitting the `signal.curated_published`
    fleet event after this returns (kept separate so unit tests can
    invoke curation without firing fleet emits).

    Steps:
        1. Fetch the Phase 1 pool (status=active AND strength>=0.6).
        2. Score each cluster.
        3. Pick one winner per `(pattern_type, topic_key)` group.
        4. Apply per-pattern_type cap.
        5. Take top_n by score, ties broken by cluster.seq ASC.
        6. Persist snapshot + entries in one transaction.

    Idempotent at the row level only in the sense that re-running with
    the same pool + clock produces the same snapshot CONTENT — but
    each run writes a new snapshot row. History is a feature
    (Rigby's lock #2: "preserves history, last run wins" is what we
    explicitly avoided).
    """
    from django.db import transaction

    now = now or timezone.now()
    pool = fetch_pool()
    pool_size = len(pool)
    if pool_size == 0:
        logger.warning("[signal-curator] empty pool; skipping snapshot")
        # Return an empty marker snapshot so the audit trail records
        # the run. Callers can detect by `result.snapshot.top_n == 0`.
        empty = CuratedSignalSnapshot.objects.create(
            scoring_formula_version=SCORING_FORMULA_VERSION,
            dedup_strategy=DEDUP_STRATEGY,
            pattern_type_cap={
                "cap": compute_pattern_type_cap(top_n),
                "rule": PATTERN_TYPE_CAP_RULE,
            },
            pool_size=0,
            top_n=0,
            excluded_duplicates=[],
        )
        return CurationResult(snapshot=empty, entries=[], pool_size=0, excluded_count=0)

    scored = _score_pool(pool, now)
    winners, dedup_excluded = _pick_group_winners(scored)
    cap = compute_pattern_type_cap(top_n)
    kept, cap_excluded = _apply_pattern_type_cap(winners, cap)

    # Final ranking — score DESC, then cluster.seq ASC.
    sort_key = lambda sc: (-sc.score, sc.cluster.seq)
    final = sorted(kept, key=sort_key)[:top_n]

    excluded_audit = dedup_excluded + cap_excluded

    with transaction.atomic():
        snapshot = CuratedSignalSnapshot.objects.create(
            scoring_formula_version=SCORING_FORMULA_VERSION,
            dedup_strategy=DEDUP_STRATEGY,
            pattern_type_cap={
                "cap": cap,
                "rule": PATTERN_TYPE_CAP_RULE,
            },
            pool_size=pool_size,
            top_n=len(final),
            excluded_duplicates=excluded_audit,
        )

        entry_rows: list[CuratedSignalEntry] = []
        for rank_idx, sc in enumerate(final, start=1):
            entry_rows.append(CuratedSignalEntry(
                snapshot=snapshot,
                cluster=sc.cluster,
                rank=rank_idx,
                curated_score=sc.score,
                group_key=sc.group_key,
                strength_at_pick=sc.strength,
                cluster_size_at_pick=sc.cluster_size,
                # exp(-inf/72) -> 0; record inf as a sentinel-ish 999999
                # so the float column has a defined value.
                age_hours_at_pick=(
                    sc.age_hours if math.isfinite(sc.age_hours) else 999999.0
                ),
            ))
        CuratedSignalEntry.objects.bulk_create(entry_rows)

    logger.info(
        "[signal-curator] snapshot=%s pool=%d kept=%d "
        "excluded=%d (dedup=%d cap=%d)",
        snapshot.id, pool_size, len(final),
        len(excluded_audit), len(dedup_excluded), len(cap_excluded),
    )
    return CurationResult(
        snapshot=snapshot,
        entries=entry_rows,
        pool_size=pool_size,
        excluded_count=len(excluded_audit),
    )


# ─── Event emission ───────────────────────────────────────────────────


def build_curated_envelope(result: CurationResult) -> dict:
    """Build the `signal.curated_published` event payload.

    Rigby's lock #3 (payload shape): full cluster envelope per entry +
    `curated_score` + `rank` + a `snapshot_id` at the top level so the
    consumer can join back to the audit row if needed. Self-contained
    so signal-studio's consumer doesn't need to be caught up on the
    Phase 1 stream first.

    Optional `cluster_ids` secondary field included for quick diffing
    (Rigby suggested it as a convenience; cheap to add).
    """
    snapshot = result.snapshot
    items: list[dict] = []
    for entry in result.entries:
        env = cluster_envelope(entry.cluster)
        if env is None:
            # Should never happen — `cluster_envelope` only returns
            # None on size-floor violations, which the Phase 1 pool
            # filter already eliminates. Log and skip if it does.
            logger.warning(
                "[signal-curator] cluster_envelope returned None for "
                "rank=%d cluster=%s — skipping",
                entry.rank, entry.cluster_id,
            )
            continue
        items.append({
            "rank": entry.rank,
            "curated_score": entry.curated_score,
            "group_key": entry.group_key,
            "cluster": env,
        })
    return {
        "snapshot_id": str(snapshot.id),
        "scoring_formula_version": snapshot.scoring_formula_version,
        "dedup_strategy": snapshot.dedup_strategy,
        "pattern_type_cap": snapshot.pattern_type_cap,
        "pool_size": snapshot.pool_size,
        "top_n": snapshot.top_n,
        "snapshot_created_at": snapshot.created_at.isoformat(),
        "items": items,
        "cluster_ids": [str(e.cluster_id) for e in result.entries],
    }


def emit_curated_published(result: CurationResult) -> str | None:
    """Emit `signal.curated_published` after the snapshot commits."""
    if result.snapshot.top_n == 0:
        # Don't push a no-op snapshot through the fleet bus — silent
        # skip is fine here. The DB row is still on disk for audit.
        return None
    from core.services.fleet_events import emit_event

    envelope = build_curated_envelope(result)
    try:
        return emit_event(
            event_type="signal.curated_published",
            app_slug="signal-studio",
            payload=envelope,
        )
    except Exception as e:  # pragma: no cover
        logger.exception(
            "[signal-curator] emit_curated_published failed snapshot=%s: %s",
            result.snapshot.id, e,
        )
        return None


def curate_and_emit(top_n: int = DEFAULT_TOP_N) -> CurationResult:
    """Convenience wrapper for Celery: curate, then emit. Returns the result."""
    result = curate_top_n(top_n=top_n)
    emit_curated_published(result)
    return result


# ─── Session 1140 (A) — curated action_card envelope + emit ───────────


def build_curated_actions_envelope(snapshot_id: str) -> dict | None:
    """Build the `signal.curated_actions_ready` event payload.

    Self-contained shape (no need for the consumer to have already
    received the matching `signal.curated_published` snapshot). Pairs
    each action_card row with the cluster envelope of its paired
    cluster_pick so signal-studio can render the action under the
    right curated cluster without an extra DB lookup.

    Returns None if the snapshot has no action_card rows yet
    (generator hasn't fired or every cluster fell back without
    persistence).
    """
    from core.models_signal_intelligence import (
        CuratedSignalEntry, CuratedSignalSnapshot,
    )

    try:
        snapshot = CuratedSignalSnapshot.objects.get(id=snapshot_id)
    except CuratedSignalSnapshot.DoesNotExist:
        logger.warning(
            "[signal-curator] build_curated_actions_envelope: snapshot %s "
            "not found",
            snapshot_id,
        )
        return None

    action_entries = (
        CuratedSignalEntry.objects
        .filter(snapshot=snapshot, entry_type='action_card')
        .select_related('cluster')
        .order_by('rank')
    )
    if not action_entries.exists():
        return None

    items: list[dict] = []
    for entry in action_entries:
        env = cluster_envelope(entry.cluster)
        if env is None:
            # Same defensive skip as build_curated_envelope — the pool
            # filter should make this impossible, but log if it happens.
            logger.warning(
                "[signal-curator] cluster_envelope returned None for "
                "action rank=%d cluster=%s — skipping",
                entry.rank, entry.cluster_id,
            )
            continue
        items.append({
            "rank": entry.rank,
            "cluster": env,
            "action_card": {
                "id": str(entry.id),
                "action_type": entry.action_type,
                "title": entry.action_title,
                "steps": entry.action_steps or [],
                "outreach_draft": entry.outreach_draft or "",
                "status": entry.action_status,
                "generated_by": entry.generated_by,
            },
        })
    return {
        "snapshot_id": str(snapshot.id),
        "snapshot_created_at": snapshot.created_at.isoformat(),
        "items": items,
        "cluster_ids": [str(e.cluster_id) for e in action_entries],
    }


def emit_curated_actions_ready(snapshot_id: str) -> str | None:
    """Emit `signal.curated_actions_ready` after action_card rows commit.

    Separate from `emit_curated_published` because action cards are
    generated asynchronously (Rigby's lock #2: snapshot success can't
    depend on OpenAI). The consumer side joins this event back to the
    snapshot by snapshot_id.

    Returns the emit event id on success, None on no-op or failure.
    Idempotent at the content level — re-emitting the same snapshot's
    actions is harmless (downstream upsert is keyed on action_card.id).
    """
    envelope = build_curated_actions_envelope(snapshot_id)
    if envelope is None or not envelope.get("items"):
        return None
    from core.services.fleet_events import emit_event
    try:
        return emit_event(
            event_type="signal.curated_actions_ready",
            app_slug="signal-studio",
            payload=envelope,
        )
    except Exception as e:  # pragma: no cover
        logger.exception(
            "[signal-curator] emit_curated_actions_ready failed "
            "snapshot=%s: %s",
            snapshot_id, e,
        )
        return None


__all__ = [
    "CurationResult",
    "DEDUP_STRATEGY",
    "DEFAULT_TOP_N",
    "PATTERN_TYPE_CAP_RULE",
    "RECENCY_TAU_HOURS",
    "RECENCY_WEIGHT",
    "SCORING_FORMULA_VERSION",
    "STRENGTH_WEIGHT",
    "build_curated_envelope",
    "build_curated_actions_envelope",
    "emit_curated_actions_ready",
    "compute_pattern_type_cap",
    "compute_score",
    "curate_and_emit",
    "curate_top_n",
    "emit_curated_published",
    "fetch_pool",
    "group_key_for_cluster",
    "normalize_topic_key",
    "topic_key_for_cluster",
]
