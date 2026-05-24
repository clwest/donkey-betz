"""Pure-function tests for signal-studio Phase 1 (Session 1131).

DB-dependent surfaces (endpoint integration, emit_event hook firing,
cursor advancement) are exercised by live smoke against the running
stack rather than the Django test DB — the test DB lacks pgvector
on this machine. See SESSION_1131 handoff for the smoke recipe.

What's covered here:
- `_parse_replay_query` in views_fleet_signals — since/limit parsing,
  clamping, error messages
- `cluster_envelope` in fleet_signals — translator output shape,
  drop-on-size-violation, evidence cap, headline truncation,
  tags pass-through
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from core.services.fleet_signals import (
    EVIDENCE_CAP_PER_CLUSTER,
    EVIDENCE_HEADLINE_MAX,
    QUALITY_BAR_MIN_CLUSTER_SIZE,
    cluster_envelope,
    iter_cluster_envelopes,
)
from core.views_fleet_signals import (
    REPLAY_DEFAULT_LIMIT,
    REPLAY_MAX_LIMIT,
    _parse_replay_query,
)


def _request_with_get(get_params: dict):
    req = MagicMock()
    req.GET = get_params
    return req


def _fake_cluster(**overrides):
    """Build a minimal duck-typed SignalCluster substitute for translator tests.

    cluster_envelope() reads attributes (.id, .name, .pattern_type, ...);
    it doesn't call ORM methods on the row.  SimpleNamespace is enough.
    """
    base = dict(
        id="11111111-2222-3333-4444-555555555555",
        seq=42,
        name="Test cluster",
        pattern_type="demand_spike",
        strength=0.8,
        confidence=0.9,
        source_breakdown={"reddit": 3, "twitter": 2, "rss": 1},
        sample_signals=[
            {"source": "reddit", "text": "First signal text"},
            {"source": "twitter", "text": "Second signal text"},
        ],
        keywords=["foo", "bar", "baz"],
        detected_at=SimpleNamespace(isoformat=lambda: "2026-05-22T20:00:00+00:00"),
    )
    base.update(overrides)
    return SimpleNamespace(**base)


# ─── _parse_replay_query ──────────────────────────────────────────────


class TestParseReplayQuery:
    def test_defaults_when_no_params(self):
        since, limit, err = _parse_replay_query(_request_with_get({}))
        assert since == 0
        assert limit == REPLAY_DEFAULT_LIMIT
        assert err is None

    def test_explicit_since_and_limit(self):
        since, limit, err = _parse_replay_query(
            _request_with_get({"since": "42", "limit": "100"})
        )
        assert since == 42
        assert limit == 100
        assert err is None

    def test_limit_clamps_to_max(self):
        since, limit, err = _parse_replay_query(
            _request_with_get({"since": "0", "limit": "999999"})
        )
        assert limit == REPLAY_MAX_LIMIT
        assert err is None

    def test_limit_floor_is_one(self):
        _, limit, err = _parse_replay_query(
            _request_with_get({"limit": "0"})
        )
        assert limit == 1
        assert err is None

    def test_negative_since_rejected(self):
        _, _, err = _parse_replay_query(_request_with_get({"since": "-5"}))
        assert err is not None
        assert "since must be >= 0" in err

    def test_non_integer_since_rejected(self):
        _, _, err = _parse_replay_query(_request_with_get({"since": "abc"}))
        assert err is not None
        assert "invalid since" in err

    def test_non_integer_limit_rejected(self):
        _, _, err = _parse_replay_query(_request_with_get({"limit": "abc"}))
        assert err is not None
        assert "invalid limit" in err


# ─── cluster_envelope ─────────────────────────────────────────────────


class TestClusterEnvelope:
    def test_basic_envelope_shape(self):
        env = cluster_envelope(_fake_cluster())
        assert env is not None
        # Every key the start-here doc names must be present, plus
        # Session 1139's `cluster_method` discriminator that propagates
        # the upstream clusterer's version downstream so signal-studio
        # can measure rejection-rate-per-method as the SLO for the
        # entity-token rewrite.
        expected_keys = {
            "seq", "external_cluster_id", "title", "summary",
            "pattern_type", "category", "cluster_method",
            "signal_strength", "confidence_score", "cluster_size",
            "evidence", "tags", "created_at",
        }
        assert set(env.keys()) == expected_keys

    def test_envelope_includes_cluster_method(self):
        """Session 1139: discriminator must appear and default safely.

        Legacy rows in the DB are tagged 'legacy' by migration 0351
        backfill; new rows default to 'entity_token_v1'. The envelope
        must surface whatever the row carries, falling back to 'legacy'
        if the attribute is missing entirely (defensive for back-compat
        with any out-of-band fixture).
        """
        c = _fake_cluster()
        c.cluster_method = "entity_token_v1"
        env = cluster_envelope(c)
        assert env is not None
        assert env["cluster_method"] == "entity_token_v1"

        c.cluster_method = "legacy"
        env2 = cluster_envelope(c)
        assert env2 is not None
        assert env2["cluster_method"] == "legacy"

    def test_external_cluster_id_is_string(self):
        env = cluster_envelope(_fake_cluster())
        assert isinstance(env["external_cluster_id"], str)

    def test_cluster_size_is_source_breakdown_sum(self):
        c = _fake_cluster(source_breakdown={"a": 4, "b": 6, "c": 2})
        env = cluster_envelope(c)
        assert env["cluster_size"] == 12

    def test_category_mirrors_pattern_type_for_phase_1(self):
        # Phase 1 contract: SignalCluster has no semantic category column;
        # we surface pattern_type as the category honestly until Phase 2
        # SignalCuratorAgent categorizes.
        c = _fake_cluster(pattern_type="opportunity_window")
        env = cluster_envelope(c)
        assert env["category"] == "opportunity_window"

    def test_summary_is_factual_restate_not_fabricated(self):
        c = _fake_cluster(
            source_breakdown={"a": 5, "b": 5},
            pattern_type="trend_emergence",
        )
        env = cluster_envelope(c)
        assert "10 signals" in env["summary"]
        assert "2 sources" in env["summary"]
        assert "trend emergence" in env["summary"]

    def test_drops_cluster_below_size_floor(self):
        # MIN_CLUSTER_SIZE = 3 — size=2 row should be dropped (logged).
        c = _fake_cluster(source_breakdown={"a": 1, "b": 1})
        assert cluster_envelope(c) is None

    def test_empty_source_breakdown_drops(self):
        c = _fake_cluster(source_breakdown={})
        assert cluster_envelope(c) is None

    def test_evidence_caps_at_max(self):
        many_signals = [
            {"source": f"s{i}", "text": f"text {i}"}
            for i in range(EVIDENCE_CAP_PER_CLUSTER + 5)
        ]
        c = _fake_cluster(sample_signals=many_signals)
        env = cluster_envelope(c)
        assert len(env["evidence"]) == EVIDENCE_CAP_PER_CLUSTER

    def test_evidence_headline_truncates(self):
        long_text = "x" * (EVIDENCE_HEADLINE_MAX + 200)
        c = _fake_cluster(sample_signals=[{"source": "s", "text": long_text}])
        env = cluster_envelope(c)
        assert len(env["evidence"][0]["headline"]) == EVIDENCE_HEADLINE_MAX

    def test_evidence_skips_non_dict_entries(self):
        # Defensive: sample_signals is JSONField, junk might creep in.
        c = _fake_cluster(sample_signals=[
            {"source": "s1", "text": "ok"},
            "not a dict",
            None,
            {"source": "s2", "text": "ok2"},
        ])
        env = cluster_envelope(c)
        assert len(env["evidence"]) == 2

    def test_evidence_url_is_empty_in_phase_1(self):
        # SignalCluster has no URL field on sample_signals today; Phase 1
        # honestly returns empty url rather than fabricating one.
        env = cluster_envelope(_fake_cluster())
        for e in env["evidence"]:
            assert e["url"] == ""

    def test_tags_pass_through_as_list(self):
        c = _fake_cluster(keywords=["one", "two", "three"])
        env = cluster_envelope(c)
        assert env["tags"] == ["one", "two", "three"]

    def test_handles_none_strength_gracefully(self):
        c = _fake_cluster(strength=None, confidence=None)
        env = cluster_envelope(c)
        assert env["signal_strength"] == 0.0
        assert env["confidence_score"] == 0.0


class TestIterClusterEnvelopes:
    def test_drops_nones_from_output(self):
        good = _fake_cluster()
        bad = _fake_cluster(source_breakdown={"a": 1})  # below size floor
        out = iter_cluster_envelopes([good, bad, good])
        assert len(out) == 2

    def test_empty_input_returns_empty_list(self):
        assert iter_cluster_envelopes([]) == []


# ─── Quality-bar constants — locked Session 1131 ──────────────────────


class TestQualityBarConstants:
    def test_size_floor_matches_min_cluster_size(self):
        # If MIN_CLUSTER_SIZE upstream changes, the fleet-side floor
        # should stay in lockstep. This test pins the contract.
        from core.services.signal_aggregation_service import (
            SignalAggregationService,
        )
        assert QUALITY_BAR_MIN_CLUSTER_SIZE == SignalAggregationService.MIN_CLUSTER_SIZE
