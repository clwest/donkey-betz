"""
tests/security/test_i0302_p4_matrix_harness.py — I-0302 Phase 4 regression
matrix runner substrate.

Contract refs:
  docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md
    §1.1 matrix runner (per-model × per-primitive)
    §3   assertion contract (a)-(e) + UPDATE/PATCH + CREATE parent-binding
  docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md §11
  Fixture: tests/security/fixtures/tenant_boundary.py (Rigby SIGN F2)

Sub-phase 1 coverage:
  Read-only primitives (immutable golden fixture safe here):
    - Initiative           LIST      /api/initiatives/
    - AgentExecution       AGGREGATE /api/analytics/overview/
    - ChatConversation     GET       /api/pa/conversations/<id>/
    - Deliverable          LIST      /api/deliverables/
    - Document             AGGREGATE /api/v1/rag/stats/

Sub-phase 2 coverage (hybrid B+C per Rigby SIGN 2026-07-10):
  Deliverable state-toggle mutation regression + missing read cells.
  Following S2748 endpoint discovery finding: Initiative + ChatConversation
  are intentionally-immutable (no user-facing CRUD UPDATE/DELETE); Chris
  D-verdict "treat as intentional immutability" at S2748.
    - Deliverable          SAVE       /api/deliverables/<uuid>/save/
    - Deliverable          UNSAVE     /api/deliverables/<uuid>/unsave/
    - Deliverable          TEMPLATEIZE /api/deliverables/<uuid>/templateize/
    - Deliverable          GET-ITEM   /api/deliverables/<uuid>/
    - ChatConversation     LIST       /api/pa/conversations/
    - Cross-tenant fixture (F1A)      predicate boundary probe

Sub-phase 3 will add:
  - Absence contract for Initiative + ChatConversation unsafe methods (405/404)
  - AST scan module for @ops_aggregate_allowed
  - Endpoint sentinels + deferred-surface coverage-gap report

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


# ==========================================================================
# Sub-phase 2 — Deliverable state-toggle mutations + missing read cells
# ==========================================================================


class TestMatrixDeliverableSave:
    """Matrix cell: Deliverable SAVE via /api/deliverables/<uuid>/save/.

    Endpoint uses `get_object_or_404(Deliverable, id=deliverable_id)` +
    post-fetch `if deliverable.user and deliverable.user != request.user`
    → 403. Existence-leak-tolerant (403 not 404); mutation gated.
    Not §5.1.b hotfix material — mutation IS gated, just leaks existence.
    """

    def _url(self, deliverable_id) -> str:
        return f"/api/deliverables/{deliverable_id}/save/"

    def test_owner_can_save_own(self, client, tb_golden):
        client.force_login(tb_golden["user_a"])
        d = tb_golden["deliverables_a"][0]
        resp = client.post(self._url(d.id))
        assert resp.status_code == 200
        d.refresh_from_db()
        assert d.is_saved is True

    def test_non_owner_blocked(self, client, tb_golden):
        client.force_login(tb_golden["user_b"])
        d = tb_golden["deliverables_a"][0]
        pre_saved = d.is_saved
        resp = client.post(self._url(d.id))
        # Post-fetch check: existing existence-leak-with-403 pattern.
        # Preferred future state is 404 (scope via predicate); tolerated
        # today. Regression MUST be: not 200 AND not mutating.
        assert resp.status_code in (403, 404), (
            f"Non-owner save must not succeed; got {resp.status_code}"
        )
        d.refresh_from_db()
        assert d.is_saved == pre_saved, (
            "Non-owner attempt must not mutate is_saved"
        )

    def test_anonymous_blocked(self, tb_golden):
        d = tb_golden["deliverables_a"][0]
        resp = Client().post(self._url(d.id))
        assert resp.status_code in (401, 403)

    def test_superuser_scoping(self, client, tb_golden):
        # Superuser is NOT a tenancy bypass (per I-030203 §3.6). The save
        # endpoint's post-fetch check compares `deliverable.user !=
        # request.user`. Superuser is not the owner of deliverables_a[0]
        # so gets 403. NOT a boundary bug — this is the intentional
        # posture (permission ≠ tenancy).
        #
        # Rigby Sub-phase 2 Q2 Edit 1 (2026-07-10): tightened from
        # (403, 404, 200) to (403, 404) — allowing 200 would silently
        # permit a future superuser cross-tenant mutation bypass. If
        # Chris ratifies a bypass, the change lands with an explicit
        # assertion revision.
        client.force_login(tb_golden["superuser"])
        d = tb_golden["deliverables_a"][0]
        pre_saved = d.is_saved
        resp = client.post(self._url(d.id))
        assert resp.status_code in (403, 404), (
            f"Superuser save on non-own deliverable must be denied "
            f"(permission != tenancy bypass); got {resp.status_code}"
        )
        d.refresh_from_db()
        assert d.is_saved == pre_saved, (
            "Superuser save attempt on non-own must not mutate is_saved"
        )


class TestMatrixDeliverableUnsave:
    """Matrix cell: Deliverable UNSAVE via /api/deliverables/<uuid>/unsave/.

    Endpoint scoped via `get_object_or_404(Deliverable, id=..., user=request.user)`
    — predicate-in-filter. Non-owner gets 404 (no existence leak).
    """

    def _url(self, deliverable_id) -> str:
        return f"/api/deliverables/{deliverable_id}/unsave/"

    def _setup_saved(self, tb_golden):
        # Pre-condition: the row must be saved so unsave is meaningful.
        d = tb_golden["deliverables_a"][0]
        d.is_saved = True
        d.save(update_fields=["is_saved"])
        return d

    def test_owner_can_unsave_own(self, client, tb_golden):
        d = self._setup_saved(tb_golden)
        client.force_login(tb_golden["user_a"])
        resp = client.post(self._url(d.id))
        assert resp.status_code == 200
        d.refresh_from_db()
        assert d.is_saved is False

    def test_non_owner_gets_404(self, client, tb_golden):
        d = self._setup_saved(tb_golden)
        client.force_login(tb_golden["user_b"])
        resp = client.post(self._url(d.id))
        # Filter user=request.user in the get_object_or_404 → 404.
        assert resp.status_code == 404
        d.refresh_from_db()
        assert d.is_saved is True  # unchanged

    def test_anonymous_blocked(self, tb_golden):
        d = self._setup_saved(tb_golden)
        resp = Client().post(self._url(d.id))
        assert resp.status_code in (401, 403)

    def test_superuser_scoped_by_filter(self, client, tb_golden):
        # `user=request.user` filter is a hard predicate — superuser is
        # NOT the owner, so predicate excludes the row → 404.
        d = self._setup_saved(tb_golden)
        client.force_login(tb_golden["superuser"])
        resp = client.post(self._url(d.id))
        assert resp.status_code == 404, (
            f"Superuser unsave on non-own must 404 via filter; got "
            f"{resp.status_code}"
        )


class TestMatrixDeliverableTemplateize:
    """Matrix cell: Deliverable TEMPLATEIZE via /api/deliverables/<uuid>/templateize/.

    Endpoint scoped via `get_object_or_404(Deliverable, id=..., user=request.user)`
    — same pattern as unsave. Non-owner gets 404.
    """

    def _url(self, deliverable_id) -> str:
        return f"/api/deliverables/{deliverable_id}/templateize/"

    def test_owner_can_templateize_own(self, client, tb_golden):
        client.force_login(tb_golden["user_a"])
        d = tb_golden["deliverables_a"][0]
        resp = client.post(self._url(d.id))
        assert resp.status_code == 200
        d.refresh_from_db()
        assert d.is_template is True

    def test_non_owner_gets_404(self, client, tb_golden):
        client.force_login(tb_golden["user_b"])
        d = tb_golden["deliverables_a"][0]
        pre_template = d.is_template
        resp = client.post(self._url(d.id))
        assert resp.status_code == 404
        d.refresh_from_db()
        assert d.is_template == pre_template

    def test_anonymous_blocked(self, tb_golden):
        d = tb_golden["deliverables_a"][0]
        resp = Client().post(self._url(d.id))
        assert resp.status_code in (401, 403)

    def test_superuser_scoped_by_filter(self, client, tb_golden):
        client.force_login(tb_golden["superuser"])
        d = tb_golden["deliverables_a"][0]
        resp = client.post(self._url(d.id))
        assert resp.status_code == 404


class TestMatrixDeliverableGetItem:
    """Matrix cell: Deliverable GET-item via /api/deliverables/<uuid>/.

    Endpoint uses `get_object_or_404(Deliverable, id=deliverable_id)` +
    post-fetch ownership check with VIP scope carve-out (`get_vip_scope`
    imported inside the function). Non-VIP non-owner gets 403; existence
    leak. Sub-phase 2 tests the basic 3-role scenarios without VIP
    fixture. VIP carve-out coverage deferred to Sub-phase 3.
    """

    def _url(self, deliverable_id) -> str:
        return f"/api/deliverables/{deliverable_id}/"

    def test_owner_can_read_own(self, client, tb_golden):
        client.force_login(tb_golden["user_a"])
        d = tb_golden["deliverables_a"][0]
        resp = client.get(self._url(d.id))
        assert resp.status_code == 200

    def test_non_owner_blocked(self, client, tb_golden):
        client.force_login(tb_golden["user_b"])
        d = tb_golden["deliverables_a"][0]
        resp = client.get(self._url(d.id))
        # Non-VIP non-owner: post-fetch 403 (existence leak). Preferred
        # future state is 404 (scope via predicate). Tolerated today.
        assert resp.status_code in (403, 404)

    def test_anonymous_blocked_or_scoped(self, tb_golden):
        # Post §5.1.b hotfix extension (5th site, Sub-phase 2):
        # @token_auth_required added to get_deliverable. Anonymous now
        # → 401 (previously reached the endpoint and returned 200 +
        # full content due to the `and request.user.is_authenticated`
        # guard skipping the access check for anonymous callers).
        d = tb_golden["deliverables_a"][0]
        resp = Client().get(self._url(d.id))
        assert resp.status_code in (401, 403), (
            f"Anonymous get on user-owned deliverable must be blocked "
            f"by @token_auth_required; got {resp.status_code}"
        )

    def test_cross_tenant_row_visible_to_workspace_owner(
        self, client, tb_golden
    ):
        # F1A adversarial fixture: user=user_b + workspace=workspace_a.
        # get_deliverable uses post-fetch ownership check on
        # `deliverable.user` (= user_b), so user_a fails the user-match
        # branch but the VIP carve-out checks workspace. Without VIP
        # fixture, user_a still fails and gets 403.
        # This assertion documents current behavior; Sub-phase 3 will
        # explicitly test the VIP + workspace carve-out matrix.
        client.force_login(tb_golden["user_a"])
        cross = tb_golden["cross_tenant_deliverable"]
        resp = client.get(self._url(cross.id))
        # user_a is NOT the direct owner (user_b is) — post-fetch check
        # returns 403. This is not a boundary regression; VIP-scoped
        # workspace access would be needed for user_a to read.
        assert resp.status_code in (200, 403, 404), (
            f"Cross-tenant row read by workspace-owning tenant: got "
            f"{resp.status_code} (documents current get_deliverable posture)"
        )


class TestMatrixChatConversationList:
    """Matrix cell: ChatConversation LIST via /api/pa/conversations/.

    Endpoint uses `scope_queryset_chat_conversation` predicate (C1 Phase 3
    wiring). Returns distinct conversation_ids the caller can access
    (workspace-scoped OR direct user ownership per Phase 2 predicate).
    """

    URL = "/api/pa/conversations/"

    def _conversation_ids(self, response) -> set[str]:
        body = response.json()
        assert body.get("success") is True
        return {c["conversation_id"] for c in body.get("conversations", [])}

    def test_user_a_sees_only_own(self, client, tb_golden):
        client.force_login(tb_golden["user_a"])
        resp = client.get(self.URL)
        assert resp.status_code == 200
        ids = self._conversation_ids(resp)
        expected = set(tb_golden["conversations_a"])
        forbidden = set(tb_golden["conversations_b"])
        assert expected.issubset(ids)
        assert ids.isdisjoint(forbidden)

    def test_user_b_sees_only_own(self, client, tb_golden):
        client.force_login(tb_golden["user_b"])
        resp = client.get(self.URL)
        assert resp.status_code == 200
        ids = self._conversation_ids(resp)
        expected = set(tb_golden["conversations_b"])
        forbidden = set(tb_golden["conversations_a"])
        assert expected.issubset(ids)
        assert ids.isdisjoint(forbidden)

    def test_anonymous_blocked_or_scoped(self, tb_golden):
        resp = Client().get(self.URL)
        # /api/pa/conversations/ requires auth per C1 wiring.
        assert resp.status_code in (401, 403)

    def test_superuser_workspace_scoping(self, client, tb_golden):
        # Superuser owns no ChatConversations in the fixture. Post-C1
        # Option A staff-tightening, superuser does NOT bypass (per
        # I-030203 §3.6). Superuser sees own conversations only —
        # which is zero in the fixture.
        client.force_login(tb_golden["superuser"])
        resp = client.get(self.URL)
        assert resp.status_code == 200
        ids = self._conversation_ids(resp)
        forbidden = set(tb_golden["conversations_a"]) | set(
            tb_golden["conversations_b"]
        )
        assert ids.isdisjoint(forbidden), (
            f"Superuser must not see cross-tenant conversations; got "
            f"leaked ids: {ids & forbidden}"
        )


# --------------------------------------------------------------------------
# §7 — Intentional-immutability contract (Sub-phase 3)
# --------------------------------------------------------------------------
#
# S2748 endpoint discovery finding: Initiative + ChatConversation have no
# user-facing CRUD UPDATE/DELETE endpoints. Chris D-verdict at S2748 close:
# "treat as intentional immutability." Sub-phase 3 formalizes this as an
# absence-contract.
#
# The contract: PUT / PATCH / DELETE against any of these endpoints MUST
# return one of {401, 403, 404, 405} — the request is rejected by
# middleware, method-check, or route-resolution BEFORE any handler code
# runs. Any 200 / 400 / 500 means a mutation handler was reached — that's
# a bug and a regression of the intentional-immutability invariant.
#
# Assertion posture per role: the invariant holds regardless of role. All
# 4 roles get one of {401, 403, 404, 405}. This is deliberately weaker
# than the ops-superuser-only invariant in test_i0302_p4_endpoint_sentinels.py
# — the point isn't role-scoped rejection, it's "no mutation handler exists."
#
# Refs:
#   I-030203 §6 Sub-phase 3 pipeline (steps 10-15)
#   I-030203 §6.a AgentExecution mutation semantics research input
#   S2748 handoff §5.2 (deferred formalization → Sub-phase 3)


_IMMUTABILITY_REJECT_CODES = {401, 403, 404, 405}
_UNSAFE_METHODS = ("put", "patch", "delete")


def _hit_unsafe(url: str, method: str, client_) -> int:
    """Issue the unsafe method against the URL; return the status code."""
    method_fn = getattr(client_, method.lower())
    return method_fn(url).status_code


class TestIntentionalImmutabilityInitiative:
    """Initiative is intentionally immutable — assert absence of CRUD UPDATE/DELETE.

    Endpoints under test:
      - /api/initiatives/                (LIST — GET-only per views_research_demo.py:1337)
      - /api/initiatives/<fake-uuid>/    (no detail endpoint exists — 404 expected)
    """

    LIST_URL = "/api/initiatives/"
    DETAIL_URL = "/api/initiatives/00000000-0000-0000-0000-000000000000/"

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_list_unsafe_method_anonymous(self, method):
        assert _hit_unsafe(self.LIST_URL, method, Client()) in _IMMUTABILITY_REJECT_CODES

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_list_unsafe_method_user_a(self, client, tb_golden, method):
        client.force_login(tb_golden["user_a"])
        assert _hit_unsafe(self.LIST_URL, method, client) in _IMMUTABILITY_REJECT_CODES

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_list_unsafe_method_user_b(self, client, tb_golden, method):
        client.force_login(tb_golden["user_b"])
        assert _hit_unsafe(self.LIST_URL, method, client) in _IMMUTABILITY_REJECT_CODES

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_list_unsafe_method_superuser(self, client, tb_golden, method):
        client.force_login(tb_golden["superuser"])
        assert _hit_unsafe(self.LIST_URL, method, client) in _IMMUTABILITY_REJECT_CODES

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_detail_unsafe_method_anonymous(self, method):
        assert _hit_unsafe(self.DETAIL_URL, method, Client()) in _IMMUTABILITY_REJECT_CODES

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_detail_unsafe_method_user_a(self, client, tb_golden, method):
        client.force_login(tb_golden["user_a"])
        assert _hit_unsafe(self.DETAIL_URL, method, client) in _IMMUTABILITY_REJECT_CODES

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_detail_unsafe_method_user_b(self, client, tb_golden, method):
        client.force_login(tb_golden["user_b"])
        assert _hit_unsafe(self.DETAIL_URL, method, client) in _IMMUTABILITY_REJECT_CODES

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_detail_unsafe_method_superuser(self, client, tb_golden, method):
        client.force_login(tb_golden["superuser"])
        assert _hit_unsafe(self.DETAIL_URL, method, client) in _IMMUTABILITY_REJECT_CODES


class TestIntentionalImmutabilityChatConversation:
    """ChatConversation is intentionally immutable — assert absence of CRUD UPDATE/DELETE.

    Endpoints under test:
      - /api/pa/conversations/                (LIST — GET-only per views_personal_assistant.py:1540)
      - /api/pa/conversations/<fake-id>/      (DETAIL — GET-only per views_personal_assistant.py:1618)
    """

    LIST_URL = "/api/pa/conversations/"
    DETAIL_URL = "/api/pa/conversations/pa-tb-fake-conversation-id/"

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_list_unsafe_method_anonymous(self, method):
        assert _hit_unsafe(self.LIST_URL, method, Client()) in _IMMUTABILITY_REJECT_CODES

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_list_unsafe_method_user_a(self, client, tb_golden, method):
        client.force_login(tb_golden["user_a"])
        assert _hit_unsafe(self.LIST_URL, method, client) in _IMMUTABILITY_REJECT_CODES

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_list_unsafe_method_user_b(self, client, tb_golden, method):
        client.force_login(tb_golden["user_b"])
        assert _hit_unsafe(self.LIST_URL, method, client) in _IMMUTABILITY_REJECT_CODES

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_list_unsafe_method_superuser(self, client, tb_golden, method):
        client.force_login(tb_golden["superuser"])
        assert _hit_unsafe(self.LIST_URL, method, client) in _IMMUTABILITY_REJECT_CODES

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_detail_unsafe_method_anonymous(self, method):
        assert _hit_unsafe(self.DETAIL_URL, method, Client()) in _IMMUTABILITY_REJECT_CODES

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_detail_unsafe_method_user_a(self, client, tb_golden, method):
        client.force_login(tb_golden["user_a"])
        assert _hit_unsafe(self.DETAIL_URL, method, client) in _IMMUTABILITY_REJECT_CODES

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_detail_unsafe_method_user_b(self, client, tb_golden, method):
        client.force_login(tb_golden["user_b"])
        assert _hit_unsafe(self.DETAIL_URL, method, client) in _IMMUTABILITY_REJECT_CODES

    @pytest.mark.parametrize("method", _UNSAFE_METHODS)
    def test_detail_unsafe_method_superuser(self, client, tb_golden, method):
        client.force_login(tb_golden["superuser"])
        assert _hit_unsafe(self.DETAIL_URL, method, client) in _IMMUTABILITY_REJECT_CODES
