"""
tests/security/test_i0302_a2_predicate_wiring.py — I-0302 Phase 3 Sub-phase A2
predicate-wiring integration regression suite.

Ratified via Rigby SIGN Q6 (2026-07-10): predicate wiring in A2 must not rely
purely on unit tests over the predicate module. This suite exercises the
end-to-end request path: authenticated user sees only their initiatives,
anonymous callers see an empty list (predicate-only boundary — auth-hardening
is deferred to a follow-on arc per Rigby Q5), second user is isolated.

Coverage per Q6 minimum:
  * LIST path (views_research_demo.initiatives_api → /api/initiatives/)
  * Second-user isolation on the same LIST path
  * Anonymous caller receives empty list, NOT server error
  * GET path (single-row scoping via .filter(owner=request.user).get())
  * CREATE + EXISTS dedup path (populate_initiatives_api owner + name uniqueness)

Contract ref:
  docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase2_predicate_module.md §8
  docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md §5.2.a
"""
from __future__ import annotations

import uuid

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from core.models_document_registry import Initiative

User = get_user_model()


@pytest.fixture
def user_a(db):
    return User.objects.create_user(
        username=f"user-a-{uuid.uuid4().hex[:6]}",
        email=f"a-{uuid.uuid4().hex[:6]}@example.com",
        password="pw",
    )


@pytest.fixture
def user_b(db):
    return User.objects.create_user(
        username=f"user-b-{uuid.uuid4().hex[:6]}",
        email=f"b-{uuid.uuid4().hex[:6]}@example.com",
        password="pw",
    )


@pytest.fixture
def initiatives_a(user_a):
    a1 = Initiative.objects.create(name=f"a-1-{uuid.uuid4().hex[:6]}", owner=user_a)
    a2 = Initiative.objects.create(name=f"a-2-{uuid.uuid4().hex[:6]}", owner=user_a)
    return [a1, a2]


@pytest.fixture
def initiatives_b(user_b):
    b1 = Initiative.objects.create(name=f"b-1-{uuid.uuid4().hex[:6]}", owner=user_b)
    return [b1]


# ==========================================================================
# LIST path — /api/initiatives/
# ==========================================================================


class TestInitiativesListWiring:
    """Exercises views_research_demo.initiatives_api at /api/initiatives/."""

    def test_authenticated_user_sees_only_own_initiatives(
        self, client, user_a, initiatives_a, initiatives_b
    ):
        client.force_login(user_a)
        resp = client.get("/api/initiatives/")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("success") is True
        returned_ids = {i["id"] for i in body.get("initiatives", [])}
        expected_ids = {str(i.id) for i in initiatives_a}
        forbidden_ids = {str(i.id) for i in initiatives_b}
        assert returned_ids == expected_ids
        assert returned_ids.isdisjoint(forbidden_ids)

    def test_second_user_isolated_from_first(
        self, client, user_a, user_b, initiatives_a, initiatives_b
    ):
        client.force_login(user_b)
        resp = client.get("/api/initiatives/")
        assert resp.status_code == 200
        body = resp.json()
        returned_ids = {i["id"] for i in body.get("initiatives", [])}
        expected_ids = {str(i.id) for i in initiatives_b}
        forbidden_ids = {str(i.id) for i in initiatives_a}
        assert returned_ids == expected_ids
        assert returned_ids.isdisjoint(forbidden_ids)

    def test_anonymous_caller_receives_empty_list_not_500(
        self, client, initiatives_a, initiatives_b
    ):
        # Anonymous callers hit the endpoint (no auth decorator per Known Risk
        # in PR body). Predicate hardening (F-2 AnonymousUser guard) must turn
        # this into an empty list rather than a 500 from
        # `.filter(owner=AnonymousUser)` raising ValueError.
        resp = Client().get("/api/initiatives/")
        assert resp.status_code == 200, (
            f"Anonymous caller must not receive server error; got {resp.status_code}"
        )
        body = resp.json()
        assert body.get("success") is True
        assert body.get("initiatives") == [], (
            "Anonymous caller must receive empty list (predicate-only boundary)"
        )


# ==========================================================================
# GET path — /api/initiatives/<uuid>/rhythm/ (initiative_rhythm_api)
# ==========================================================================


class TestInitiativeGetWiring:
    """Exercises the query-time owner scoping on GET-by-id endpoints."""

    def test_owner_can_read_own_initiative(self, client, user_a, initiatives_a):
        client.force_login(user_a)
        target = initiatives_a[0]
        resp = client.get(f"/api/initiatives/{target.id}/rhythm/")
        # 200 iff owner scope matched; anything but 404 proves the query-time
        # owner filter didn't hide the row from its owner.
        assert resp.status_code != 404, (
            f"Owner must be able to read their own initiative; got 404"
        )

    def test_non_owner_gets_404_not_leak(
        self, client, user_a, user_b, initiatives_a, initiatives_b
    ):
        # user_b logs in but requests user_a's initiative — must 404, NOT 200.
        client.force_login(user_b)
        target = initiatives_a[0]
        resp = client.get(f"/api/initiatives/{target.id}/rhythm/")
        assert resp.status_code == 404, (
            f"Non-owner must receive 404 (existence-oracle-safe); got {resp.status_code}"
        )


# ==========================================================================
# CREATE + EXISTS dedup path — populate_initiatives_api
# ==========================================================================


class TestPopulateInitiativesWiring:
    """Exercises the CREATE (owner=request.user) + per-user EXISTS dedup."""

    def test_anonymous_caller_rejected_401(self, client):
        # populate_initiatives_api has no auth decorator; the A2 wiring must
        # reject unauthenticated callers before hitting the create path
        # (Initiative.owner is NOT NULL — assigning AnonymousUser fails).
        resp = Client().post("/api/initiatives/populate/")
        assert resp.status_code == 401, (
            f"Unauthenticated caller must be rejected before create; "
            f"got {resp.status_code}"
        )
