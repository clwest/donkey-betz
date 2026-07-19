"""S2831 — GET /api/rag/observability/intent-gate/ diagnostics endpoint.

Thin observability tab shipped as a canary for the S2830 DORMANT
pointer-intent registry (Pattern B/C/D). Tests verify:

  1. Registry canary — matched_patterns computed via
     INTENT_MECHANISMS[*].detect(query), producing correct names for
     Pattern B/C/D queries + empty for boring semantic queries.
  2. Hard-capped params — limit clamped 1..20; threshold clamped 0.0..1.0.
  3. Missing query → 400.
  4. Unauthenticated → 401.
  5. schema_version present + notice string marks filter_summary as debug.
  6. Wrong HTTP method (POST) → 405.

Test-DB is empty (django_db without fixtures), so search_embeddings()
returns []; assertions ignore result-row content and check the
observable branches (matched_patterns, intent_gates, notice, hard-caps).
This mirrors the log-driven-observability contract used by
tests/regression/rag_registry_parity/.
"""
from __future__ import annotations

import json

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from core.views_rag_observability import rag_intent_gate_diagnostics


ENDPOINT = "/api/rag/observability/intent-gate/"


pytestmark = pytest.mark.django_db


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username="s2831-tester", password="x"
    )


@pytest.fixture
def rf():
    return RequestFactory()


def _call(rf, user, params=None):
    req = rf.get(ENDPOINT, params or {})
    req.user = user
    return rag_intent_gate_diagnostics(req)


def _payload(response):
    return json.loads(response.content)


class TestRegistryCanary:
    """matched_patterns must reflect INTENT_MECHANISMS[*].detect(query)."""

    def test_pattern_b_count_query(self, rf, user):
        r = _call(rf, user, {"query": "How many spiders do we have"})
        d = _payload(r)
        assert d["matched_patterns"] == ["count"]
        assert d["intent_gates"] == {
            "count_active": True,
            "self_reference_active": False,
            "literal_filename_active": False,
        }

    def test_pattern_c_self_reference_query(self, rf, user):
        r = _call(rf, user, {"query": "where do I start"})
        d = _payload(r)
        assert d["matched_patterns"] == ["self_reference"]
        assert d["intent_gates"]["self_reference_active"] is True
        assert d["intent_gates"]["count_active"] is False
        assert d["intent_gates"]["literal_filename_active"] is False

    def test_pattern_d_literal_filename_query(self, rf, user):
        r = _call(rf, user, {"query": "PLATFORM_INVENTORY"})
        d = _payload(r)
        assert d["matched_patterns"] == ["literal_filename"]
        assert d["intent_gates"]["literal_filename_active"] is True

    def test_no_pattern_boring_query(self, rf, user):
        r = _call(rf, user, {"query": "celery worker configuration"})
        d = _payload(r)
        assert d["matched_patterns"] == []
        assert all(v is False for v in d["intent_gates"].values())


class TestHardCaps:
    """Server-side hard-caps enforce limit 1..20 + threshold 0.0..1.0."""

    def test_limit_clamped_to_max_20(self, rf, user):
        r = _call(rf, user, {"query": "foo", "limit": 999})
        assert _payload(r)["limit"] == 20

    def test_limit_clamped_to_min_1(self, rf, user):
        r = _call(rf, user, {"query": "foo", "limit": 0})
        assert _payload(r)["limit"] == 1

    def test_limit_default_when_invalid(self, rf, user):
        r = _call(rf, user, {"query": "foo", "limit": "not-an-int"})
        assert _payload(r)["limit"] == 5

    def test_threshold_clamped_to_max_1(self, rf, user):
        r = _call(rf, user, {"query": "foo", "threshold": 5.0})
        assert _payload(r)["threshold"] == 1.0

    def test_threshold_clamped_to_min_0(self, rf, user):
        r = _call(rf, user, {"query": "foo", "threshold": -1.0})
        assert _payload(r)["threshold"] == 0.0

    def test_threshold_default_when_invalid(self, rf, user):
        r = _call(rf, user, {"query": "foo", "threshold": "bad"})
        assert _payload(r)["threshold"] == 0.4


class TestValidation:
    def test_missing_query_returns_400(self, rf, user):
        assert _call(rf, user, {}).status_code == 400

    def test_empty_query_returns_400(self, rf, user):
        assert _call(rf, user, {"query": ""}).status_code == 400

    def test_whitespace_only_query_returns_400(self, rf, user):
        assert _call(rf, user, {"query": "   "}).status_code == 400


class TestAuth:
    def test_unauthenticated_returns_401(self, rf):
        req = rf.get(ENDPOINT, {"query": "foo"})
        req.user = AnonymousUser()
        assert rag_intent_gate_diagnostics(req).status_code == 401


class TestContract:
    """Schema versioning + best-effort disclaimer per Rigby Q5 STRENGTHEN."""

    def test_schema_version_present(self, rf, user):
        d = _payload(_call(rf, user, {"query": "foo"}))
        assert d["schema_version"] == "1"

    def test_notice_marks_filter_summary_as_debug(self, rf, user):
        d = _payload(_call(rf, user, {"query": "foo"}))
        assert "best-effort" in d["notice"].lower()
        assert "not a stable contract" in d["notice"].lower()

    def test_response_shape_keys(self, rf, user):
        d = _payload(_call(rf, user, {"query": "foo"}))
        assert set(d.keys()) >= {
            "success",
            "schema_version",
            "query",
            "limit",
            "threshold",
            "matched_patterns",
            "intent_gates",
            "results",
            "filter_summary",
            "notice",
        }

    def test_filter_summary_echoes_intent_gates(self, rf, user):
        d = _payload(_call(rf, user, {"query": "How many spiders"}))
        fs = d["filter_summary"]
        assert fs["count_intent_active"] is True
        assert fs["self_reference_intent_active"] is False
        assert fs["literal_filename_intent_active"] is False


class TestMethod:
    def test_post_returns_405(self, rf, user):
        req = rf.post(ENDPOINT, {"query": "foo"})
        req.user = user
        assert rag_intent_gate_diagnostics(req).status_code == 405
