"""
tests/security/test_i0302_p4_matrix_harness.py — I-0302 Phase 4 regression
matrix runner substrate.

Contract refs:
  docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md
    §1.1 matrix runner (per-model × per-primitive)
    §3   assertion contract (a)-(e) + UPDATE/PATCH + CREATE parent-binding
  docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md §11
  Fixture: tests/security/fixtures/tenant_boundary.py (Rigby SIGN F2)

Sub-phase 1 coverage (this file's initial land):
  Read-only primitives only (immutable golden fixture is safe here):
    - Initiative           LIST      /api/initiatives/
    - AgentExecution       AGGREGATE /api/analytics/overview/
    - ChatConversation     GET       /api/pa/conversations/<id>/
    - Deliverable          LIST      /api/deliverables/
    - Document             AGGREGATE /api/v1/rag/stats/

  One representative endpoint per canonical model. All 5 models × 4 roles
  = 20 assertions. Sub-phase 2 extends to UPDATE/DELETE/EXISTS/AGGREGATE
  gap-cells + CREATE-parent-binding via per-test builders on top of the
  golden fixture.

Roles per §3.5:
  - anon      : predicate F-2 hardening must hold (401/403 or empty)
  - user_a    : sees only own N=3 rows / own aggregate
  - user_b    : sees only own N=3 rows / own aggregate (cross-isolation)
  - superuser : sees own + Session 642 null-user (AgentExecution only);
                does NOT bypass into user_a or user_b tenants except
                where §11 @ops_aggregate_allowed carve-out declared
                (zero uses at codification — none apply Sub-phase 1)
"""
from __future__ import annotations

import pytest
from django.test import Client


# --------------------------------------------------------------------------
# §1 — Initiative LIST — /api/initiatives/
# --------------------------------------------------------------------------


class TestMatrixInitiativeList:
    """5-model × read-only matrix cell: Initiative LIST via /api/initiatives/."""

    URL = "/api/initiatives/"

    def _list_ids(self, response) -> set[str]:
        body = response.json()
        assert body.get("success") is True
        return {i["id"] for i in body.get("initiatives", [])}

    def test_user_a_sees_only_own(self, client, tb_golden):
        client.force_login(tb_golden["user_a"])
        resp = client.get(self.URL)
        assert resp.status_code == 200
        expected = {str(i.id) for i in tb_golden["initiatives_a"]}
        forbidden = {str(i.id) for i in tb_golden["initiatives_b"]}
        assert self._list_ids(resp) == expected
        assert self._list_ids(resp).isdisjoint(forbidden)

    def test_user_b_sees_only_own(self, client, tb_golden):
        client.force_login(tb_golden["user_b"])
        resp = client.get(self.URL)
        assert resp.status_code == 200
        expected = {str(i.id) for i in tb_golden["initiatives_b"]}
        forbidden = {str(i.id) for i in tb_golden["initiatives_a"]}
        assert self._list_ids(resp) == expected
        assert self._list_ids(resp).isdisjoint(forbidden)

    def test_anonymous_predicate_boundary_holds(self, tb_golden):
        # /api/initiatives/ is AllowAny with predicate-only boundary
        # (per Phase 3 Sub-phase A2 wiring). Anon → empty list, not 500.
        resp = Client().get(self.URL)
        assert resp.status_code == 200
        assert resp.json().get("success") is True
        assert self._list_ids(resp) == set()

    def test_superuser_does_not_bypass_tenants(self, client, tb_golden):
        # Initiative has no Session-642-style carve-out; superuser sees
        # own initiatives only (none, in this fixture). Must NOT see
        # user_a or user_b rows.
        client.force_login(tb_golden["superuser"])
        resp = client.get(self.URL)
        assert resp.status_code == 200
        forbidden = {str(i.id) for i in tb_golden["initiatives_a"]}
        forbidden.update({str(i.id) for i in tb_golden["initiatives_b"]})
        assert self._list_ids(resp).isdisjoint(forbidden)


# --------------------------------------------------------------------------
# §2 — AgentExecution AGGREGATE — /api/analytics/overview/
# --------------------------------------------------------------------------


class TestMatrixAgentExecutionAggregate:
    """Matrix cell: AgentExecution AGGREGATE via /api/analytics/overview/.

    Exercises the Session 642 null-user superuser carve-out — the sole
    Q7 Hybrid boundary exception in the 5 canonical models.
    """

    URL = "/api/analytics/overview/"

    def test_user_a_own_count_only(self, client, tb_golden):
        client.force_login(tb_golden["user_a"])
        resp = client.get(self.URL)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("success") is True
        # user_a has 3 own executions; user_b's 3 and null-user's 1 excluded.
        assert body.get("total_executions") == 3

    def test_user_b_own_count_only(self, client, tb_golden):
        client.force_login(tb_golden["user_b"])
        resp = client.get(self.URL)
        assert resp.status_code == 200
        # user_b has 3 own; user_a's 3 and null-user's 1 excluded.
        assert resp.json().get("total_executions") == 3

    def test_anonymous_receives_zero_not_500(self, tb_golden):
        # AllowAny endpoint hit by anonymous; F-2 hardening returns
        # .none() so counts are 0, not a server error.
        resp = Client().get(self.URL)
        assert resp.status_code == 200
        assert resp.json().get("total_executions") == 0

    def test_superuser_sees_null_user_but_not_other_tenants(
        self, client, tb_golden
    ):
        # Session 642 carve-out: superuser sees own (0 here) + null-user (1).
        # Must NOT include user_a's 3 or user_b's 3.
        client.force_login(tb_golden["superuser"])
        resp = client.get(self.URL)
        assert resp.status_code == 200
        # 0 own + 1 null-user = 1. If the predicate leaked cross-tenant rows,
        # count would be 7 (0 + 1 + 3 + 3).
        assert resp.json().get("total_executions") == 1


# --------------------------------------------------------------------------
# §3 — ChatConversation GET — /api/pa/conversations/<id>/
# --------------------------------------------------------------------------


class TestMatrixChatConversationGet:
    """Matrix cell: ChatConversation GET via /api/pa/conversations/<id>/."""

    def _url(self, conv_id: str) -> str:
        return f"/api/pa/conversations/{conv_id}/"

    def test_user_a_reads_own(self, client, tb_golden):
        client.force_login(tb_golden["user_a"])
        conv_id = tb_golden["conversations_a"][0]
        resp = client.get(self._url(conv_id))
        assert resp.status_code == 200

    def test_user_b_gets_404_on_user_a_conversation(self, client, tb_golden):
        client.force_login(tb_golden["user_b"])
        conv_id = tb_golden["conversations_a"][0]
        resp = client.get(self._url(conv_id))
        # §3.1 (b): 404, not 403 — existence-oracle safe.
        assert resp.status_code == 404

    def test_anonymous_blocked(self, tb_golden):
        conv_id = tb_golden["conversations_a"][0]
        resp = Client().get(self._url(conv_id))
        assert resp.status_code in (401, 403)

    def test_superuser_does_not_bypass_predicate(self, client, tb_golden):
        # ChatConversation has no Session-642-style carve-out; superuser
        # must go through the predicate boundary. Since the superuser
        # doesn't own user_a's conversation, GET returns 404.
        client.force_login(tb_golden["superuser"])
        conv_id = tb_golden["conversations_a"][0]
        resp = client.get(self._url(conv_id))
        assert resp.status_code == 404


# --------------------------------------------------------------------------
# §4 — Deliverable LIST — /api/deliverables/
# --------------------------------------------------------------------------


class TestMatrixDeliverableList:
    """Matrix cell: Deliverable LIST via /api/deliverables/."""

    URL = "/api/deliverables/"

    def _list_titles(self, response) -> set[str]:
        body = response.json()
        assert body.get("success") is True
        return {d["title"] for d in body.get("deliverables", [])}

    def test_user_a_sees_only_own(self, client, tb_golden):
        client.force_login(tb_golden["user_a"])
        resp = client.get(self.URL)
        assert resp.status_code == 200
        expected = {d.title for d in tb_golden["deliverables_a"]}
        forbidden = {d.title for d in tb_golden["deliverables_b"]}
        titles = self._list_titles(resp)
        assert expected.issubset(titles)
        assert titles.isdisjoint(forbidden)

    def test_user_b_sees_only_own(self, client, tb_golden):
        client.force_login(tb_golden["user_b"])
        resp = client.get(self.URL)
        assert resp.status_code == 200
        expected = {d.title for d in tb_golden["deliverables_b"]}
        forbidden = {d.title for d in tb_golden["deliverables_a"]}
        titles = self._list_titles(resp)
        assert expected.issubset(titles)
        assert titles.isdisjoint(forbidden)

    def test_anonymous_predicate_boundary_holds(self, tb_golden):
        # /api/deliverables/ is AllowAny with predicate-only boundary
        # (F-2 hardening returns .none() for anonymous). Empty list, not 500.
        resp = Client().get(self.URL)
        assert resp.status_code == 200
        assert self._list_titles(resp) == set()

    def test_superuser_scoped_to_own_workspaces(self, client, tb_golden):
        # scope_queryset_deliverable filters by workspaces user owns.
        # Superuser owns NO workspaces in the fixture → sees no
        # deliverables. This is boundary-correct: unlike
        # user_can_access_workspace (single-object bypass, per its
        # docstring), scope_queryset_deliverable does NOT superuser-
        # bypass. The RUR-C1 invariant HOLDS: superuser cannot see
        # user_a's or user_b's deliverables just by being a superuser.
        # If Chris later chooses to add cross-tenant aggregate for ops
        # visibility, the mechanism is @ops_aggregate_allowed (§11) with
        # explicit F-block amendment — not silent bypass.
        client.force_login(tb_golden["superuser"])
        resp = client.get(self.URL)
        assert resp.status_code == 200
        titles = self._list_titles(resp)
        forbidden = {d.title for d in tb_golden["deliverables_a"]}
        forbidden.update({d.title for d in tb_golden["deliverables_b"]})
        assert titles.isdisjoint(forbidden)


# --------------------------------------------------------------------------
# §5 — Document AGGREGATE — /api/v1/rag/stats/
# --------------------------------------------------------------------------


class TestMatrixDocumentAggregate:
    """Matrix cell: Document AGGREGATE via /api/v1/rag/stats/.

    Response shape: `{"success": True, "embeddings_stats": {"total_documents": N, ...}}`.
    The user-facing aggregate lives at `embeddings_stats.total_documents`.
    """

    URL = "/api/v1/rag/stats/"

    def _total_documents(self, response) -> int:
        body = response.json()
        assert body.get("success") is True
        return body["embeddings_stats"]["total_documents"]

    def test_user_a_own_count_only(self, client, tb_golden):
        client.force_login(tb_golden["user_a"])
        resp = client.get(self.URL)
        assert resp.status_code == 200
        # 3 own documents; user_b's 3 excluded by owner=user filter.
        assert self._total_documents(resp) == 3

    def test_user_b_own_count_only(self, client, tb_golden):
        client.force_login(tb_golden["user_b"])
        resp = client.get(self.URL)
        assert resp.status_code == 200
        assert self._total_documents(resp) == 3

    def test_anonymous_blocked_or_scoped(self, tb_golden):
        # /api/v1/rag/stats/ requires authentication. Anonymous → 401/403.
        resp = Client().get(self.URL)
        assert resp.status_code in (401, 403)

    def test_superuser_scoped_by_default(self, client, tb_golden):
        # No @ops_aggregate_allowed decorator on /api/v1/rag/stats/ →
        # superuser aggregate is still tenant-scoped per I-030203 §3.4.
        # Superuser has 0 own documents in the fixture; count MUST be 0,
        # NOT 6 (user_a + user_b combined).
        client.force_login(tb_golden["superuser"])
        resp = client.get(self.URL)
        assert resp.status_code == 200
        assert self._total_documents(resp) == 0
