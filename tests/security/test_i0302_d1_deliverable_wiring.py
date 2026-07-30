"""
tests/security/test_i0302_d1_deliverable_wiring.py — I-0302 Phase 3
Sub-phase D1 Deliverable predicate-wiring integration regression suite.

Ratified via Rigby SIGN Q5 (2026-07-10): D1 wires ~11-13 Deliverable
sites across 6 view files + applies Option A staff-tightening (replaces
legacy `is_staff sees ALL deliverables` bypass with the ratified
workspace-scoped predicate).

Coverage per Q5 SIGN minimum:
  1. Regular user can list own deliverables (200 + content).
  2. Non-staff user cannot fetch another user's deliverable by id (404/403).
  3. `clone_deliverable` source-fetch now enforces scoping (predicate
     replaces prior `get_object_or_404` unscoped fetch).
  4. Anonymous safety on the primary list endpoint.

Contract refs:
  docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase2_predicate_module.md §8
  docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md §5.1.a
"""
from __future__ import annotations

import uuid

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace

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
def workspace_a(user_a):
    return ProjectWorkspace.objects.create(
        user=user_a, name=f"ws-a-{uuid.uuid4().hex[:6]}"
    )


@pytest.fixture
def workspace_b(user_b):
    return ProjectWorkspace.objects.create(
        user=user_b, name=f"ws-b-{uuid.uuid4().hex[:6]}"
    )


@pytest.fixture
def deliverable_a(user_a, workspace_a):
    return Deliverable.objects.create(
        user=user_a,
        workspace=workspace_a,
        title=f"deliv-a-{uuid.uuid4().hex[:6]}",
        deliverable_type="text",
        content="hello from a",
    )


@pytest.fixture
def deliverable_b(user_b, workspace_b):
    return Deliverable.objects.create(
        user=user_b,
        workspace=workspace_b,
        title=f"deliv-b-{uuid.uuid4().hex[:6]}",
        deliverable_type="text",
        content="hello from b",
    )


# ==========================================================================
# LIST — /api/deliverables/
# ==========================================================================


class TestDeliverableListWiring:
    """Exercises list_deliverables predicate scoping."""

    def test_regular_user_sees_only_own_deliverables(
        self, client, user_a, deliverable_a, deliverable_b
    ):
        # user_a owns deliverable_a; user_b owns deliverable_b.
        # Under predicate scoping, user_a's list must NOT include
        # deliverable_b.
        client.force_login(user_a)
        resp = client.get("/api/deliverables/")
        assert resp.status_code == 200
        body = resp.json()
        # Response shape may vary; probe the deliverable id list.
        deliverables = body.get("deliverables") or body.get("results") or []
        ids = {d.get("id") for d in deliverables if isinstance(d, dict)}
        assert str(deliverable_a.id) in ids, (
            "user_a must see own deliverable"
        )
        assert str(deliverable_b.id) not in ids, (
            "user_a must not see user_b's deliverable"
        )

    def test_anonymous_receives_empty_not_500(
        self, deliverable_a, deliverable_b
    ):
        # F-2 predicate hardening (from A2) means anonymous callers get
        # `.none()` (empty result), not a 500.
        resp = Client().get("/api/deliverables/")
        assert resp.status_code in (200, 401, 403), (
            f"Anonymous list must not 500; got {resp.status_code}"
        )
        if resp.status_code == 200:
            body = resp.json()
            deliverables = body.get("deliverables") or body.get("results") or []
            assert deliverables == [] or all(
                d.get("id") not in {str(deliverable_a.id), str(deliverable_b.id)}
                for d in deliverables
                if isinstance(d, dict)
            ), "Anonymous must not receive owned deliverables"


# ==========================================================================
# OWNER FILTER — /api/deliverables/?owner=me | ?owner=<id>
# S3050 PR 1 (RaaS UI arc Phase 2, Gap 4 / Gap 2 backend / Gap 7)
# ==========================================================================


class TestDeliverableListOwnerFilter:
    """Exercises the S3050 PR 1 owner= query param.

    Contract:
    - owner=me → filter to request.user's rows
    - owner=<user_id> as staff/superuser → filter to that user's rows
    - owner=<user_id> as non-staff → coerced to self (defense before PR 4)
    - No owner param → unchanged (backwards-compat with predicate scoping)
    """

    @pytest.fixture
    def staff_with_workspace(self, db):
        staff = User.objects.create_user(
            username=f"staff-owner-{uuid.uuid4().hex[:6]}",
            email=f"so-{uuid.uuid4().hex[:6]}@example.com",
            password="pw",
            is_staff=True,
            is_superuser=False,
        )
        ws = ProjectWorkspace.objects.create(
            user=staff, name=f"ws-staff-{uuid.uuid4().hex[:6]}"
        )
        return staff, ws

    def _ids(self, resp) -> set[str]:
        body = resp.json()
        deliverables = body.get("deliverables") or body.get("results") or []
        return {d.get("id") for d in deliverables if isinstance(d, dict)}

    def test_owner_me_filters_to_self(
        self, client, user_a, deliverable_a, deliverable_b
    ):
        client.force_login(user_a)
        resp = client.get("/api/deliverables/?owner=me")
        assert resp.status_code == 200
        ids = self._ids(resp)
        assert str(deliverable_a.id) in ids
        assert str(deliverable_b.id) not in ids

    def test_non_staff_arbitrary_owner_coerced_to_self(
        self, client, user_a, user_b, deliverable_a, deliverable_b
    ):
        # user_a passes owner=<user_b.id> — coercion forces to self.
        # user_a must never see deliverable_b via this branch.
        client.force_login(user_a)
        resp = client.get(f"/api/deliverables/?owner={user_b.id}")
        assert resp.status_code == 200
        ids = self._ids(resp)
        assert str(deliverable_b.id) not in ids, (
            "Non-staff must not reach other user's rows via owner param"
        )
        assert str(deliverable_a.id) in ids

    def test_staff_can_query_other_owner_within_own_scope(
        self, client, staff_with_workspace, user_b
    ):
        # Staff creates a Deliverable owned by user_b but attached to
        # staff's workspace — mirrors the shape where staff cleans up
        # rows on behalf of other users. Staff's `scope_queryset_deliverable`
        # already includes staff's workspaces + workspace-null rows; the
        # owner=<user_b.id> filter narrows to just user_b's within that scope.
        staff, ws = staff_with_workspace
        cross = Deliverable.objects.create(
            user=user_b,
            workspace=ws,
            title=f"cross-{uuid.uuid4().hex[:6]}",
            deliverable_type="text",
            content="cross-user row inside staff workspace",
        )
        # Also create a staff-owned row to prove filter narrows.
        own = Deliverable.objects.create(
            user=staff,
            workspace=ws,
            title=f"own-{uuid.uuid4().hex[:6]}",
            deliverable_type="text",
            content="staff own row",
        )
        client.force_login(staff)
        resp = client.get(f"/api/deliverables/?owner={user_b.id}")
        assert resp.status_code == 200
        ids = self._ids(resp)
        assert str(cross.id) in ids, "Staff owner=<user_b> must include cross"
        assert str(own.id) not in ids, "owner=<user_b> must exclude staff's own"

    def test_no_owner_param_preserves_existing_scope(
        self, client, user_a, deliverable_a, deliverable_b
    ):
        # Backwards-compat: without owner=, list matches pre-PR-1 behavior
        # (workspace-scoped predicate output).
        client.force_login(user_a)
        resp = client.get("/api/deliverables/")
        assert resp.status_code == 200
        ids = self._ids(resp)
        assert str(deliverable_a.id) in ids
        assert str(deliverable_b.id) not in ids


# ==========================================================================
# CLONE source-fetch scoping — POST /api/deliverables/<id>/clone/
# ==========================================================================


class TestDeliverableCloneSourceFetchScoping:
    """clone_deliverable source-fetch must reject cross-user id."""

    def test_user_cannot_clone_another_users_deliverable(
        self, client, user_a, deliverable_b
    ):
        # user_a is not the owner of deliverable_b; the source-fetch
        # must return 404 rather than allowing the clone.
        client.force_login(user_a)
        resp = client.post(f"/api/deliverables/{deliverable_b.id}/clone/")
        assert resp.status_code == 404, (
            f"Non-owner clone must be rejected with 404; got "
            f"{resp.status_code} — regression against §5.1.a source-fetch scoping"
        )


# ==========================================================================
# Option A staff-tightening — non-superuser staff no longer bypass
# ==========================================================================


class TestStaffTighteningStats:
    """`get_deliverable_stats` — non-superuser staff no longer bypass."""

    @pytest.fixture
    def staff_user(self, db):
        # is_staff=True, is_superuser=False — the exact population
        # Option A tightens against.
        return User.objects.create_user(
            username=f"staff-{uuid.uuid4().hex[:6]}",
            email=f"s-{uuid.uuid4().hex[:6]}@example.com",
            password="pw",
            is_staff=True,
            is_superuser=False,
        )

    def test_non_superuser_staff_sees_only_own_workspace_stats(
        self, client, staff_user, user_a, deliverable_a, deliverable_b
    ):
        # Pre-D1: `is_staff sees ALL deliverables` — staff would see
        # both deliverable_a and deliverable_b in the stats total.
        # Post-D1: staff sees own workspaces (+ workspace-null rows via
        # F3 carve-out). Since staff_user has no workspaces, total is 0.
        client.force_login(staff_user)
        resp = client.get("/api/deliverables/stats/")
        assert resp.status_code == 200
        body = resp.json()
        total = (
            body.get("stats", {}).get("total")
            if isinstance(body.get("stats"), dict)
            else body.get("total")
        )
        # staff_user has no workspaces; total must exclude user_a's and
        # user_b's deliverables. Allow total to be None or 0 depending
        # on response shape.
        assert total in (0, None), (
            f"Non-superuser staff must not see cross-user stats; got "
            f"total={total} (regression against §5.1.a Option A "
            f"staff-tightening)"
        )


# ==========================================================================
# DELETE — /api/deliverables/<uuid>/delete/ — §5.1.b hotfix regression
# ==========================================================================


class TestDeleteDeliverableScoping:
    """Exercises §5.1.b hotfix (2026-07-10, S2748).

    Pre-hotfix: `delete_deliverable` fetched via
    `get_object_or_404(Deliverable, id=deliverable_id)` with no
    ownership filter — any authenticated caller could DELETE any
    deliverable whose id they knew.

    Post-hotfix: source-fetch wrapped in `scope_queryset_deliverable`
    (mirrors the D1 clone_deliverable pattern) — non-owners receive
    404 instead of destructive success.
    """

    def _url(self, deliverable_id) -> str:
        return f"/api/deliverables/{deliverable_id}/delete/"

    def test_owner_can_delete_own_deliverable(
        self, client, user_a, deliverable_a
    ):
        client.force_login(user_a)
        resp = client.post(self._url(deliverable_a.id))
        assert resp.status_code == 200, (
            f"Owner must be able to delete own deliverable; got {resp.status_code}"
        )
        # Confirm the row is actually gone.
        assert not Deliverable.objects.filter(id=deliverable_a.id).exists()

    def test_non_owner_cannot_delete(
        self, client, user_a, user_b, deliverable_a
    ):
        # Pre-hotfix: this succeeded with 200 and deleted deliverable_a.
        # Post-hotfix: predicate scoping returns .none() for user_b, so
        # get_object_or_404 raises Http404.
        client.force_login(user_b)
        resp = client.post(self._url(deliverable_a.id))
        assert resp.status_code == 404, (
            f"Non-owner must receive 404 on delete of another user's "
            f"deliverable; got {resp.status_code} (regression against §5.1.b hotfix)"
        )
        # Confirm the row is NOT gone.
        assert Deliverable.objects.filter(id=deliverable_a.id).exists(), (
            "Non-owner delete must NOT destroy the row — §5.1.b hotfix contract."
        )

    def test_anonymous_blocked(self, deliverable_a):
        # @token_auth_required on delete_deliverable → 401 for anon.
        resp = Client().post(self._url(deliverable_a.id))
        assert resp.status_code in (401, 403), (
            f"Anonymous caller must be blocked from delete; got {resp.status_code}"
        )
        # Row must still exist.
        assert Deliverable.objects.filter(id=deliverable_a.id).exists()


# ==========================================================================
# LINK — /api/deliverables/<uuid>/link-workspace/ — §5.1.b hotfix regression
# ==========================================================================


class TestLinkDeliverableWorkspaceScoping:
    """Exercises §5.1.b hotfix (2026-07-10, S2748) for `link_deliverable_workspace`.

    Pre-hotfix: both the source deliverable fetch AND the target workspace
    fetch were unscoped. Attacker could (a) hijack an unclaimed deliverable
    into their own workspace, OR (b) dump their own deliverable into
    another user's workspace.

    Post-hotfix: source-fetch via `scope_queryset_deliverable`; target
    workspace gate via `user_can_access_workspace`.
    """

    def _url(self, deliverable_id) -> str:
        return f"/api/deliverables/{deliverable_id}/link-workspace/"

    def _body(self, workspace_id) -> str:
        import json

        return json.dumps({"workspace_id": str(workspace_id)})

    def test_non_owner_cannot_link_source_deliverable(
        self, client, user_a, user_b, workspace_a, workspace_b, deliverable_a
    ):
        # user_b tries to link user_a's deliverable to user_b's own workspace.
        # Predicate scoping means user_b's queryset returns .none() for
        # deliverable_a, so source-fetch 404s.
        client.force_login(user_b)
        resp = client.post(
            self._url(deliverable_a.id),
            data=self._body(workspace_b.id),
            content_type="application/json",
        )
        assert resp.status_code == 404, (
            f"Non-owner must not be able to link another user's deliverable; "
            f"got {resp.status_code} (regression against §5.1.b hotfix)"
        )
        # Original workspace unchanged.
        deliverable_a.refresh_from_db()
        assert deliverable_a.workspace_id == workspace_a.id

    def test_owner_cannot_link_to_foreign_workspace(
        self, client, user_a, workspace_b, deliverable_a
    ):
        # user_a owns deliverable_a and requests it be linked to user_b's
        # workspace. Source-fetch passes (owner), but target-workspace
        # gate rejects (`user_can_access_workspace` returns False).
        client.force_login(user_a)
        resp = client.post(
            self._url(deliverable_a.id),
            data=self._body(workspace_b.id),
            content_type="application/json",
        )
        assert resp.status_code == 404, (
            f"Owner must not be able to link deliverable to a foreign "
            f"workspace; got {resp.status_code} (regression against §5.1.b)"
        )

    def test_anonymous_blocked(self, deliverable_a, workspace_a):
        # @token_auth_required on link_deliverable_workspace → 401 for anon.
        resp = Client().post(
            self._url(deliverable_a.id),
            data=self._body(workspace_a.id),
            content_type="application/json",
        )
        assert resp.status_code in (401, 403)


# ==========================================================================
# RECORD EVENT — /api/deliverables/<uuid>/event/ — §5.1.b hotfix regression
# ==========================================================================


class TestRecordDeliverableEventScoping:
    """Exercises §5.1.b hotfix (2026-07-10, S2748) for `record_deliverable_event`.

    Pre-hotfix: (a) NO auth gate — anonymous callers could poison the
    audit log with false event rows; (b) NO ownership check —
    authenticated non-owners could attribute events (e.g., fake "shared")
    to another user's deliverable.

    Post-hotfix: @token_auth_required + scope_queryset_deliverable
    source-fetch.
    """

    def _url(self, deliverable_id) -> str:
        return f"/api/deliverables/{deliverable_id}/event/"

    def _body(self) -> str:
        import json

        return json.dumps({"event_type": "shared", "metadata": {}})

    def test_anonymous_blocked(self, deliverable_a):
        # Pre-hotfix: anonymous → 200 + DeliverableEvent row created
        # (audit-log poisoning). Post-hotfix: @token_auth_required
        # returns 401.
        from core.models_deliverables import DeliverableEvent

        pre_count = DeliverableEvent.objects.filter(
            deliverable=deliverable_a
        ).count()
        resp = Client().post(
            self._url(deliverable_a.id),
            data=self._body(),
            content_type="application/json",
        )
        assert resp.status_code in (401, 403), (
            f"Anonymous caller must be blocked from event emission; "
            f"got {resp.status_code} (regression against §5.1.b auth gate)"
        )
        # No new event row created.
        assert (
            DeliverableEvent.objects.filter(deliverable=deliverable_a).count()
            == pre_count
        )

    def test_non_owner_blocked(
        self, client, user_a, user_b, deliverable_a
    ):
        from core.models_deliverables import DeliverableEvent

        pre_count = DeliverableEvent.objects.filter(
            deliverable=deliverable_a
        ).count()
        client.force_login(user_b)
        resp = client.post(
            self._url(deliverable_a.id),
            data=self._body(),
            content_type="application/json",
        )
        assert resp.status_code == 404, (
            f"Non-owner must not be able to emit events on another user's "
            f"deliverable; got {resp.status_code} (regression against §5.1.b)"
        )
        assert (
            DeliverableEvent.objects.filter(deliverable=deliverable_a).count()
            == pre_count
        )

    def test_owner_can_emit_event(
        self, client, user_a, deliverable_a
    ):
        from core.models_deliverables import DeliverableEvent

        pre_count = DeliverableEvent.objects.filter(
            deliverable=deliverable_a
        ).count()
        client.force_login(user_a)
        resp = client.post(
            self._url(deliverable_a.id),
            data=self._body(),
            content_type="application/json",
        )
        assert resp.status_code == 200, (
            f"Owner must be able to emit events on own deliverable; "
            f"got {resp.status_code}"
        )
        # New event row created.
        assert (
            DeliverableEvent.objects.filter(deliverable=deliverable_a).count()
            == pre_count + 1
        )
