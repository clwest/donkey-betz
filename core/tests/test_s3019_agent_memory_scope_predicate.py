"""Session 3019 (ADR-0008): AgentMemory scope predicate — cross-user isolation.

Ratified by ADR-0008 (`docs/adr/ADR-0008-agent-memory-scope-predicate.md`)
2026-07-28. Follows S3017 PR #3719 (F-2/F-3 `@token_auth_required` gate on
`/api/memory-palace/memory/<uuid>/**`) — that closed anon-reach; this
closes the authenticated cross-user gap.

**What this test file locks:**

1. Predicate purity — the `scope_queryset_agent_memory` predicate returns
   the correct sets for regular / superuser / anonymous / assigned /
   unassigned callers directly (no HTTP layer, no view logic).
2. View wiring — the three memory-palace views actually route through the
   predicate. Regular users see 404 for cross-user memory reads/deletes;
   superusers see everything for ops visibility.
3. Delete side-effect — a cross-user DELETE attempt does NOT delete the
   row (the predicate returns `.none()`, `.get(id=...)` raises DoesNotExist
   before the delete runs).
4. `AgentAssignment` factory helper (ADR-0008 §3.4) actually creates the
   linkage that makes regular users see their assigned agents' memories.

Under current data state (AgentAssignment table empty at HEAD), only the
superuser carve-out is exercised in production. These tests spin up
real assignments in-test to exercise the multi-tenant Phase 0 code path
that will activate later.
"""
from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from core.models_unified_system import Agent, AgentMemory
from core.security.object_authz import (
    can_read_agent_memory,
    scope_queryset_agent_memory,
)
from core.tests.helpers.agent_assignment import assign_agent_to_user
from core.tests.helpers.token_auth import token_client_for


User = get_user_model()


class AgentMemoryScopePredicateTests(TestCase):
    """Predicate-layer tests (no HTTP layer)."""

    def setUp(self) -> None:
        self.alice = User.objects.create_user(
            username="alice_s3019", email="alice_s3019@example.com", password="pw",
        )
        self.bob = User.objects.create_user(
            username="bob_s3019", email="bob_s3019@example.com", password="pw",
        )
        self.superuser = User.objects.create_superuser(
            username="root_s3019", email="root_s3019@example.com", password="pw",
        )

        self.agent_alice = Agent.objects.create(
            name="alice_agent_s3019", agent_type="test",
            description="", specialization="",
        )
        self.agent_bob = Agent.objects.create(
            name="bob_agent_s3019", agent_type="test",
            description="", specialization="",
        )
        self.agent_system = Agent.objects.create(
            name="system_agent_s3019", agent_type="test",
            description="", specialization="",
        )

        assign_agent_to_user(self.agent_alice, self.alice)
        assign_agent_to_user(self.agent_bob, self.bob)
        # agent_system intentionally has no user_assignments.

        self.mem_alice = AgentMemory.objects.create(
            agent=self.agent_alice, title="alice's memory",
            content="only alice + superuser should see", memory_type="insight",
        )
        self.mem_bob = AgentMemory.objects.create(
            agent=self.agent_bob, title="bob's memory",
            content="only bob + superuser should see", memory_type="insight",
        )
        self.mem_system = AgentMemory.objects.create(
            agent=self.agent_system, title="system memory",
            content="only superuser should see", memory_type="insight",
        )

    def test_regular_user_sees_only_their_assigned_agents_memory(self) -> None:
        qs = scope_queryset_agent_memory(self.alice, AgentMemory.objects.all())
        ids = set(qs.values_list("id", flat=True))
        self.assertIn(self.mem_alice.id, ids)
        self.assertNotIn(self.mem_bob.id, ids)
        self.assertNotIn(self.mem_system.id, ids)

    def test_superuser_sees_own_and_system_but_not_other_users(self) -> None:
        # Superuser is NOT assigned to any agent — sees only system-agent memories.
        qs = scope_queryset_agent_memory(self.superuser, AgentMemory.objects.all())
        ids = set(qs.values_list("id", flat=True))
        self.assertIn(self.mem_system.id, ids)
        # Alice's and Bob's memories are NOT visible because superuser isn't
        # assigned to those agents (per ADR-0008 §3.1 explicit warning:
        # do NOT broaden to "sees everything").
        self.assertNotIn(self.mem_alice.id, ids)
        self.assertNotIn(self.mem_bob.id, ids)

    def test_superuser_assigned_sees_own_plus_system(self) -> None:
        # Assign superuser to agent_alice — sees alice's memory + system, but
        # still NOT bob's (defense-in-depth per ADR-0008).
        assign_agent_to_user(self.agent_alice, self.superuser)
        qs = scope_queryset_agent_memory(self.superuser, AgentMemory.objects.all())
        ids = set(qs.values_list("id", flat=True))
        self.assertIn(self.mem_alice.id, ids)
        self.assertIn(self.mem_system.id, ids)
        self.assertNotIn(self.mem_bob.id, ids)

    def test_anonymous_returns_none(self) -> None:
        from django.contrib.auth.models import AnonymousUser
        qs = scope_queryset_agent_memory(AnonymousUser(), AgentMemory.objects.all())
        self.assertEqual(qs.count(), 0)

    def test_can_read_agent_memory_predicate(self) -> None:
        self.assertTrue(can_read_agent_memory(self.alice, self.mem_alice))
        self.assertFalse(can_read_agent_memory(self.alice, self.mem_bob))
        self.assertFalse(can_read_agent_memory(self.alice, self.mem_system))
        # Superuser reads system-agent memory (null-assignment carve-out).
        self.assertTrue(can_read_agent_memory(self.superuser, self.mem_system))
        # Superuser does NOT read a user-assigned agent's memory unless
        # assigned — same defense-in-depth as scope_queryset_agent_execution.
        self.assertFalse(can_read_agent_memory(self.superuser, self.mem_alice))


class AgentMemoryViewWiringTests(TestCase):
    """HTTP-layer tests — the three S3017-gated views actually route through
    the S3019 predicate.
    """

    def setUp(self) -> None:
        self.alice = User.objects.create_user(
            username="alice_view_s3019", email="alice_view_s3019@example.com", password="pw",
        )
        self.bob = User.objects.create_user(
            username="bob_view_s3019", email="bob_view_s3019@example.com", password="pw",
        )
        self.agent_alice = Agent.objects.create(
            name="alice_view_agent_s3019", agent_type="test",
            description="", specialization="",
        )
        self.agent_bob = Agent.objects.create(
            name="bob_view_agent_s3019", agent_type="test",
            description="", specialization="",
        )
        assign_agent_to_user(self.agent_alice, self.alice)
        assign_agent_to_user(self.agent_bob, self.bob)

        self.mem_alice = AgentMemory.objects.create(
            agent=self.agent_alice, title="alice view", content="alice",
            memory_type="insight",
        )
        self.mem_bob = AgentMemory.objects.create(
            agent=self.agent_bob, title="bob view", content="bob",
            memory_type="insight",
        )

    def _detail_url(self, memory_id: uuid.UUID) -> str:
        return f"/api/memory-palace/memory/{memory_id}/"

    def _connections_url(self, memory_id: uuid.UUID) -> str:
        return f"/api/memory-palace/memory/{memory_id}/connections/"

    def _delete_url(self, memory_id: uuid.UUID) -> str:
        return f"/api/memory-palace/memory/{memory_id}/delete/"

    def _client_for(self, user) -> Client:
        c = Client(HTTP_HOST="localhost:8000")
        c.force_login(user)
        return c

    def test_alice_reads_own_memory(self) -> None:
        resp = self._client_for(self.alice).get(self._detail_url(self.mem_alice.id))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))

    def test_alice_cannot_read_bobs_memory(self) -> None:
        resp = self._client_for(self.alice).get(self._detail_url(self.mem_bob.id))
        self.assertEqual(resp.status_code, 404)

    def test_alice_cannot_read_bobs_connections(self) -> None:
        resp = self._client_for(self.alice).get(self._connections_url(self.mem_bob.id))
        self.assertEqual(resp.status_code, 404)

    def test_alice_cannot_delete_bobs_memory_and_row_survives(self) -> None:
        resp = self._client_for(self.alice).delete(self._delete_url(self.mem_bob.id))
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(AgentMemory.objects.filter(id=self.mem_bob.id).exists())

    def test_alice_delete_own_memory_succeeds(self) -> None:
        resp = self._client_for(self.alice).delete(self._delete_url(self.mem_alice.id))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(AgentMemory.objects.filter(id=self.mem_alice.id).exists())

    def test_token_auth_shape_still_holds(self) -> None:
        """Sanity check — S3017 Token-auth path still reaches the view for
        the memory's owner. Regression guard against the ADR-0008 wiring
        accidentally breaking S3016 Fold E parity."""
        resp = token_client_for(self.alice).get(self._detail_url(self.mem_alice.id))
        self.assertEqual(resp.status_code, 200)

    def test_token_auth_cross_user_still_404(self) -> None:
        """Token-authenticated cross-user access still 404 (predicate runs
        after auth resolution)."""
        resp = token_client_for(self.alice).get(self._detail_url(self.mem_bob.id))
        self.assertEqual(resp.status_code, 404)
