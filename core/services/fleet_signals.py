"""Translator: SignalCluster ORM rows → fleet-signals replay envelopes.

Session 1131 Phase 1 (Rigby's path B). The signal-studio fleet app
pulls these envelopes from `GET /api/fleet/signals/clusters?since=<seq>`
and upserts them locally by `external_cluster_id`.

Response shape is locked in 00-START-NEXT-SESSION.md (Session 1131 entry).
Quality bar is locked by Rigby (conversation pa-d19c1674b936): status
must be `active`, cluster_size >= 3, strength >= 0.6. The size floor is
already enforced upstream by `signal_aggregation_service.MIN_CLUSTER_SIZE`,
but we re-check defensively here — a row below the floor is a sign
that the upstream invariant slipped, so we log and skip.
"""
from __future__ import annotations

import logging
from typing import Iterable

from core.models_signal_intelligence import SignalCluster

logger = logging.getLogger(__name__)


# Locked by Rigby for Phase 1. Bar applies on the SQL filter side
# (status, strength) and the Python re-check (cluster_size).
QUALITY_BAR_STATUS = "active"
QUALITY_BAR_MIN_STRENGTH = 0.6
QUALITY_BAR_MIN_CLUSTER_SIZE = 3

# Cap on `evidence[]` entries per cluster to keep the response payload
# bounded. sample_signals can grow large for high-volume clusters; the
# UI only needs a small set to surface in cards.
EVIDENCE_CAP_PER_CLUSTER = 5

# Cap on per-evidence headline text — sample_signals stores raw spider
# snippets which can be long. 240 chars covers tweet-length + a bit.
EVIDENCE_HEADLINE_MAX = 240


def cluster_envelope(c: SignalCluster) -> dict | None:
    """Translate one SignalCluster ORM row into the response envelope.

    Returns None if the row violates the size floor (should never
    happen in practice but we log and skip rather than emit junk).
    """
    source_breakdown = c.source_breakdown or {}
    cluster_size = sum(source_breakdown.values()) if source_breakdown else 0
    if cluster_size < QUALITY_BAR_MIN_CLUSTER_SIZE:
        logger.warning(
            "[fleet-signals] dropping cluster %s — size=%s below floor %s "
            "(upstream MIN_CLUSTER_SIZE invariant slipped)",
            c.id, cluster_size, QUALITY_BAR_MIN_CLUSTER_SIZE,
        )
        return None

    sample_signals = c.sample_signals or []
    evidence: list[dict] = []
    for s in sample_signals[:EVIDENCE_CAP_PER_CLUSTER]:
        if not isinstance(s, dict):
            continue
        # sample_signals shape upstream is {'text': str, 'source': str}.
        # No URL field on the model today; we leave url="" so consumers
        # can render without a click-through until Phase 2 plumbs it.
        evidence.append({
            "source": str(s.get("source", "") or ""),
            "url": "",
            "headline": str(s.get("text", "") or "")[:EVIDENCE_HEADLINE_MAX],
        })

    return {
        "seq": c.seq,
        "external_cluster_id": str(c.id),
        "title": c.name,
        # Synthetic summary — SignalCluster has no `summary` column.
        # We restate factual structure (size + source diversity) rather
        # than fabricating prose. Phase 2 SignalCuratorAgent can replace
        # this with real LLM-generated copy.
        "summary": (
            f"{cluster_size} signals from {len(source_breakdown)} sources "
            f"({c.pattern_type.replace('_', ' ')})."
        ),
        "pattern_type": c.pattern_type,
        # Phase 1: `category` mirrors `pattern_type`. The start-here doc
        # lists semantic categories ("tech | crypto | business | career")
        # but the SignalCluster model has no equivalent field. Honest
        # placeholder until Phase 2 SignalCuratorAgent categorizes.
        "category": c.pattern_type,
        # Session 1139: clusterer discriminator. Lets signal-studio's
        # mirror (and any downstream consumer) measure summarizer
        # rejection rate per cluster_method — which is the SLO/
        # acceptance test for the entity-token rewrite. Defaults to
        # 'legacy' for safety if the field is somehow missing.
        "cluster_method": getattr(c, "cluster_method", "legacy") or "legacy",
        "signal_strength": float(c.strength or 0.0),
        "confidence_score": float(c.confidence or 0.0),
        "cluster_size": cluster_size,
        "evidence": evidence,
        "tags": list(c.keywords or []),
        "created_at": c.detected_at.isoformat() if c.detected_at else "",
    }


def iter_cluster_envelopes(rows: Iterable[SignalCluster]) -> list[dict]:
    """Translate a queryset (or list) of SignalCluster rows. Drops nones."""
    out = []
    for c in rows:
        env = cluster_envelope(c)
        if env is not None:
            out.append(env)
    return out


__all__ = [
    "cluster_envelope",
    "iter_cluster_envelopes",
    "QUALITY_BAR_STATUS",
    "QUALITY_BAR_MIN_STRENGTH",
    "QUALITY_BAR_MIN_CLUSTER_SIZE",
]
