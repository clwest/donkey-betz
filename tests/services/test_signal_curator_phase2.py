"""Pure-function tests for the Phase 2 SignalCuratorService.

DB-dependent paths (curate_top_n + emit) are exercised by live smoke
against the running stack — Django test DB lacks pgvector. See
SESSION_1131_SIGNAL_STUDIO_PHASE_1.md for the canonical smoke recipe.

What's covered here:
- `normalize_topic_key`: lowercase, alnum-only, collapse, trim
- `topic_key_for_cluster`: name preferred, keywords fallback,
  stop-word filtering on both, UUID-prefix last resort
- `group_key_for_cluster`: `<pattern_type>::<topic_key>` shape
- `compute_score`: 0.9*strength + 0.1*recency_decay, handles missing
  detected_at, decay tau math sanity
- `compute_pattern_type_cap`: max(2, ceil(N/4)) per Rigby's lock
- `_pick_group_winners`: best score per group, tiebreak by seq ASC,
  excluded audit shape
- `_apply_pattern_type_cap`: cap enforcement preserves ranking order
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from core.services.signal_curator_service import (
    PATTERN_TYPE_CAP_RULE,
    RECENCY_TAU_HOURS,
    RECENCY_WEIGHT,
    STRENGTH_WEIGHT,
    _apply_pattern_type_cap,
    _pick_group_winners,
    _score_pool,
    compute_pattern_type_cap,
    compute_score,
    group_key_for_cluster,
    normalize_topic_key,
    topic_key_for_cluster,
)


# ─── Fake SignalCluster (duck-typed) ──────────────────────────────────


def _fake_cluster(**overrides):
    """Build a duck-typed SignalCluster substitute for pure-function tests."""
    now = datetime.now(timezone.utc)
    base = dict(
        id=uuid4(),
        seq=42,
        name="React demand spike",
        pattern_type="demand_spike",
        strength=0.8,
        confidence=0.9,
        source_breakdown={"reddit": 3, "twitter": 2, "rss": 1},
        keywords=["react", "frontend"],
        detected_at=now - timedelta(hours=12),
    )
    base.update(overrides)
    return SimpleNamespace(**base)


# ─── normalize_topic_key ──────────────────────────────────────────────


class TestNormalizeTopicKey:
    def test_lowercases_and_strips_whitespace(self):
        assert normalize_topic_key("  REACT  ") == "react"

    def test_replaces_non_alnum_with_underscore(self):
        assert normalize_topic_key("AI/ML") == "ai_ml"

    def test_collapses_runs_of_separators(self):
        assert normalize_topic_key("a   b---c") == "a_b_c"

    def test_trims_leading_trailing_separators(self):
        assert normalize_topic_key("__react__") == "react"

    def test_empty_input_returns_empty(self):
        assert normalize_topic_key("") == ""
        assert normalize_topic_key("   ") == ""

    def test_only_separators_returns_empty(self):
        assert normalize_topic_key("///") == ""


# ─── topic_key_for_cluster ────────────────────────────────────────────


class TestTopicKeyForCluster:
    def test_name_preferred_over_keywords(self):
        # Even when keywords has a topic, name leads with one too.
        c = _fake_cluster(name="React demand spike", keywords=["javascript"])
        assert topic_key_for_cluster(c) == "react"

    def test_strips_pattern_indicator_words_from_name(self):
        # "demand" + "spike" are stop words; "React" wins.
        c = _fake_cluster(name="React demand spike", keywords=[])
        assert topic_key_for_cluster(c) == "react"

    def test_strips_pattern_indicator_words_from_keywords(self):
        # Smoke result: keywords mix indicator words + topics. Indicator
        # words must NOT become topic_keys.
        c = _fake_cluster(
            name="",
            keywords=["want", "looking for", "react", "javascript"],
        )
        # "want" + "looking for" are stop words → next non-stop = "react".
        assert topic_key_for_cluster(c) == "react"

    def test_pattern_words_in_keywords_skipped(self):
        c = _fake_cluster(
            name="",
            keywords=["suggestion", "missing", "react"],
        )
        assert topic_key_for_cluster(c) == "react"

    def test_uuid_fallback_when_no_topic(self):
        c = _fake_cluster(name="", keywords=["want", "missing"])
        topic = topic_key_for_cluster(c)
        assert topic.startswith("unknown_")
        # UUID prefix is the first 8 chars of the cluster id.
        assert topic == f"unknown_{str(c.id)[:8]}"

    def test_all_stop_words_in_name_falls_through_to_keywords(self):
        c = _fake_cluster(
            name="New emerging trend",  # all stop words
            keywords=["security"],
        )
        assert topic_key_for_cluster(c) == "security"

    def test_multi_word_topic_in_name_picks_first_content_word(self):
        c = _fake_cluster(name="Artificial Intelligence emerging trend", keywords=[])
        # 'artificial' (not in stop_words) wins.
        assert topic_key_for_cluster(c) == "artificial"


# ─── group_key_for_cluster ────────────────────────────────────────────


class TestGroupKey:
    def test_shape_is_pattern_double_colon_topic(self):
        c = _fake_cluster(pattern_type="demand_spike", name="React demand spike")
        assert group_key_for_cluster(c) == "demand_spike::react"

    def test_different_pattern_types_get_separate_groups(self):
        c1 = _fake_cluster(pattern_type="demand_spike", name="React")
        c2 = _fake_cluster(pattern_type="trend_emergence", name="React")
        assert group_key_for_cluster(c1) != group_key_for_cluster(c2)


# ─── compute_score ────────────────────────────────────────────────────


class TestComputeScore:
    def test_weights_sum_to_one(self):
        # Sanity: composite is 0.9 * strength + 0.1 * recency.
        assert STRENGTH_WEIGHT + RECENCY_WEIGHT == pytest.approx(1.0)

    def test_pure_strength_when_age_zero(self):
        now = datetime.now(timezone.utc)
        c = _fake_cluster(strength=0.8, detected_at=now)
        score, strength, recency = compute_score(c, now=now)
        # age=0 → recency_decay=1 → score = 0.9*0.8 + 0.1*1 = 0.82
        assert score == pytest.approx(0.82)
        assert strength == pytest.approx(0.8)
        assert recency == pytest.approx(1.0)

    def test_recency_decay_at_tau(self):
        now = datetime.now(timezone.utc)
        c = _fake_cluster(strength=0.0, detected_at=now - timedelta(hours=RECENCY_TAU_HOURS))
        score, _, recency = compute_score(c, now=now)
        # decay = exp(-1) ~ 0.368
        assert recency == pytest.approx(math.exp(-1.0), rel=1e-6)
        assert score == pytest.approx(0.1 * math.exp(-1.0), rel=1e-6)

    def test_recency_decays_over_time(self):
        now = datetime.now(timezone.utc)
        young = _fake_cluster(strength=0.7, detected_at=now - timedelta(hours=1))
        old = _fake_cluster(strength=0.7, detected_at=now - timedelta(hours=200))
        s_young, _, _ = compute_score(young, now=now)
        s_old, _, _ = compute_score(old, now=now)
        # Same strength but younger row scores higher.
        assert s_young > s_old

    def test_missing_detected_at_zero_recency(self):
        c = _fake_cluster(strength=0.5, detected_at=None)
        score, _, recency = compute_score(c)
        assert recency == 0.0
        assert score == pytest.approx(0.45)  # 0.9 * 0.5 + 0.1 * 0

    def test_none_strength_handled(self):
        now = datetime.now(timezone.utc)
        c = _fake_cluster(strength=None, detected_at=now)
        score, strength, _ = compute_score(c, now=now)
        assert strength == 0.0
        # 0.9*0 + 0.1*1 = 0.1
        assert score == pytest.approx(0.1)


# ─── compute_pattern_type_cap ─────────────────────────────────────────


class TestPatternTypeCap:
    def test_rule_for_n10(self):
        # Rigby's lock: max(2, ceil(N/4)). N=10 → 3.
        assert compute_pattern_type_cap(10) == 3

    def test_rule_for_n20(self):
        assert compute_pattern_type_cap(20) == 5

    def test_floor_at_2_for_small_n(self):
        assert compute_pattern_type_cap(4) == 2
        assert compute_pattern_type_cap(1) == 2
        assert compute_pattern_type_cap(7) == 2  # ceil(7/4)=2

    def test_rule_string_documented(self):
        assert PATTERN_TYPE_CAP_RULE == "max(2, ceil(N/4))"


# ─── _pick_group_winners ──────────────────────────────────────────────


def _scored(cluster, score):
    """Quick ScoredCluster builder for ranking tests."""
    from core.services.signal_curator_service import ScoredCluster
    sb = cluster.source_breakdown or {}
    return ScoredCluster(
        cluster=cluster,
        score=score,
        strength=float(cluster.strength or 0.0),
        recency_decay=0.5,
        cluster_size=sum(sb.values()),
        age_hours=10.0,
        group_key=group_key_for_cluster(cluster),
    )


class TestPickGroupWinners:
    def test_single_cluster_per_group_passes_through(self):
        a = _scored(_fake_cluster(name="React"), 0.8)
        b = _scored(_fake_cluster(name="Security"), 0.7)
        winners, excluded = _pick_group_winners([a, b])
        assert len(winners) == 2
        assert excluded == []

    def test_picks_highest_score_in_group(self):
        c1 = _fake_cluster(name="React", seq=1)
        c2 = _fake_cluster(name="React", seq=2)
        winners, excluded = _pick_group_winners([
            _scored(c1, 0.7),
            _scored(c2, 0.9),
        ])
        assert len(winners) == 1
        assert winners[0].cluster is c2
        assert len(excluded) == 1
        assert excluded[0]["cluster_id"] == str(c1.id)
        assert excluded[0]["lost_to_cluster_id"] == str(c2.id)

    def test_tiebreak_by_seq_ascending(self):
        # Same score → older seq wins.
        c1 = _fake_cluster(name="React", seq=5)
        c2 = _fake_cluster(name="React", seq=2)
        winners, excluded = _pick_group_winners([
            _scored(c1, 0.8),
            _scored(c2, 0.8),
        ])
        assert winners[0].cluster.seq == 2

    def test_different_pattern_types_dont_collapse(self):
        c1 = _fake_cluster(name="Security", pattern_type="demand_spike")
        c2 = _fake_cluster(name="Security", pattern_type="trend_emergence")
        winners, excluded = _pick_group_winners([
            _scored(c1, 0.8),
            _scored(c2, 0.8),
        ])
        # Different (pattern_type, topic) → both kept.
        assert len(winners) == 2
        assert excluded == []

    def test_excluded_audit_shape(self):
        loser = _fake_cluster(name="React", seq=1)
        winner = _fake_cluster(name="React", seq=2)
        winners, excluded = _pick_group_winners([
            _scored(loser, 0.5),
            _scored(winner, 0.7),
        ])
        assert excluded == [{
            "cluster_id": str(loser.id),
            "group_key": "demand_spike::react",
            "score": 0.5,
            "lost_to_cluster_id": str(winner.id),
        }]


# ─── _apply_pattern_type_cap ──────────────────────────────────────────


class TestApplyPatternTypeCap:
    def test_drops_entries_above_cap(self):
        # 5 demand_spike clusters, cap=3 → keep top 3 by score.
        winners = [
            _scored(_fake_cluster(name=f"t{i}", pattern_type="demand_spike"), 0.9 - i * 0.01)
            for i in range(5)
        ]
        kept, capped = _apply_pattern_type_cap(winners, cap=3)
        assert len(kept) == 3
        assert len(capped) == 2
        # First 3 by score (descending) are kept.
        kept_scores = [sc.score for sc in kept]
        assert kept_scores == sorted(kept_scores, reverse=True)
        # Lowest two scores ended up capped.
        capped_scores = [c["score"] for c in capped]
        assert max(capped_scores) <= min(kept_scores)

    def test_multiple_pattern_types_each_get_cap(self):
        winners = []
        for pt in ("demand_spike", "trend_emergence"):
            for i in range(4):
                winners.append(
                    _scored(_fake_cluster(name=f"x{i}", pattern_type=pt), 0.8 - i * 0.01)
                )
        kept, capped = _apply_pattern_type_cap(winners, cap=2)
        # 2 per pattern_type × 2 types = 4 kept; 4 capped.
        from collections import Counter
        type_counts = Counter(sc.cluster.pattern_type for sc in kept)
        assert type_counts["demand_spike"] == 2
        assert type_counts["trend_emergence"] == 2
        assert len(capped) == 4

    def test_capped_audit_has_reason(self):
        winners = [
            _scored(_fake_cluster(name=f"t{i}"), 0.9 - i * 0.01)
            for i in range(4)
        ]
        kept, capped = _apply_pattern_type_cap(winners, cap=2)
        for entry in capped:
            assert entry["reason"].startswith("pattern_type_cap_")


# ─── _score_pool integration ──────────────────────────────────────────


class TestScorePool:
    def test_produces_one_scoredcluster_per_input(self):
        now = datetime.now(timezone.utc)
        pool = [_fake_cluster(detected_at=now), _fake_cluster(detected_at=now)]
        scored = _score_pool(pool, now)
        assert len(scored) == 2

    def test_age_hours_field_populated(self):
        now = datetime.now(timezone.utc)
        c = _fake_cluster(detected_at=now - timedelta(hours=24))
        scored = _score_pool([c], now)
        assert scored[0].age_hours == pytest.approx(24.0, abs=0.01)

    def test_cluster_size_computed_from_source_breakdown(self):
        c = _fake_cluster(source_breakdown={"a": 4, "b": 6, "c": 2})
        scored = _score_pool([c], datetime.now(timezone.utc))
        assert scored[0].cluster_size == 12
