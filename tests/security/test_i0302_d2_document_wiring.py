"""
tests/security/test_i0302_d2_document_wiring.py — I-0302 Phase 3
Sub-phase D2 Document + observability aggregate wiring regression suite.

Ratified via Rigby SIGN Q5 (2026-07-10): D2 wires 3 sites — the
`dashboard/views.py` global type aggregate (superuser-gated at the
aggregate branch), `rag_run_classification` endpoint (superuser_required),
and `_video_document_details` helper (signature refactored to accept
`user` + predicate scoping). The bulk of the Document surface at
`content/views.py` + `core/views_rag_embeddings.py` is already
`.filter(owner=user)` scoped — verified, no wiring needed.

Coverage per Q5 SIGN minimum:
  1. `rag_run_classification` anonymous → 401.
  2. `rag_run_classification` non-superuser → 403.
  3. `dashboard/views.py:embeddings_stats` — the `by_type` gate is a
     unit-level assertion because the `dashboard.views` module is
     currently URL-orphaned (Session 872 removed the include; core.urls
     wires `views_rag_embeddings.embeddings_stats` at `/api/v1/rag/stats/`
     instead). Wiring lands as defense-in-depth for future re-wiring.

Contract refs:
  docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase2_predicate_module.md §8
  docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md §5.5.a
"""
from __future__ import annotations

import uuid

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory

User = get_user_model()


@pytest.fixture
def user_a(db):
    return User.objects.create_user(
        username=f"user-a-{uuid.uuid4().hex[:6]}",
        email=f"a-{uuid.uuid4().hex[:6]}@example.com",
        password="pw",
    )


# ==========================================================================
# core/views_rag_observability.py — rag_run_classification superuser gate
# ==========================================================================


class TestRagClassificationSuperuserGate:
    """Ops-only mutating batch classification job must be superuser-gated."""

    def test_anonymous_gets_401(self):
        resp = Client().post("/api/rag/observability/classify/")
        assert resp.status_code == 401, (
            f"Anonymous caller must be 401 on classification endpoint; "
            f"got {resp.status_code}"
        )

    def test_non_superuser_gets_403(self, client, user_a):
        client.force_login(user_a)
        resp = client.post("/api/rag/observability/classify/")
        assert resp.status_code == 403, (
            f"Non-superuser must be 403 on classification endpoint; "
            f"got {resp.status_code}"
        )


# ==========================================================================
# dashboard/views.py — embeddings_stats `by_type` gate (unit-level)
# ==========================================================================


class TestDashboardByTypeGateUnit:
    """The type-breakdown aggregate must be gated to superuser at the
    branch level. The `dashboard.views` module is URL-orphaned currently
    (Session 872), so this test asserts the branch logic directly via
    RequestFactory instead of an HTTP round-trip."""

    def _run(self, user):
        # Import inside the test so we get the D2-wired function.
        from dashboard.views import embeddings_stats

        factory = RequestFactory()
        req = factory.get("/embeddings-stats/")
        req.user = user
        resp = embeddings_stats(req)
        return resp

    def test_non_superuser_receives_default_no_type_leak(self, user_a):
        resp = self._run(user_a)
        assert resp.status_code == 200
        # DRF Response object exposes .data.
        by_type = getattr(resp, "data", {}).get("by_type") or {}
        assert by_type in ({}, {"unknown": 0}), (
            f"Non-superuser must not see the true type distribution; "
            f"got {by_type} (§5.5.a Document dashboard gate)"
        )
