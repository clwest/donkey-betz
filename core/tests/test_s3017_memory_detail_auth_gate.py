"""Session 3017 (F-2 remediation): Auth gate on `/api/memory-palace/memory/<uuid>/`.

The S3016 Fold G audit (`docs/audits/PUBLIC_PATHS_BARE_PREFIX_AUDIT_S3016.md`)
surfaced that `get_memory_detail` lived under the bare-prefix PUBLIC_PATHS
entry `/api/memory-palace/memory/` with no permission decorator. Any anon
caller with a valid `memory_id` UUID could fetch the row and silently
trigger the `access_count += 1` auto-increment at
`core/views_memory_palace.py:112-114`.

The remediation gates the view with `@token_auth_required` (matches the
S2789 pattern for PUBLIC_PATHS endpoints that need auth). These tests lock:

1. anon → 401 with `not_authenticated` reason_code (envelope contract).
2. anon does NOT bump `access_count` (side-effect hardening).
3. session-auth caller reaches the view + gets `success=True`.
4. Token-auth caller reaches the view + gets `success=True` (parity — the
   very failure mode Fold E was written for, applied to this endpoint).

**F-3 (Rigby T1 SIGN zoom-out 5b):** sibling routes under the same
`/api/memory-palace/memory/` bare-prefix bypass — `get_memory_connections`
(same-class read leak) and `delete_memory` (worse-than-F-2 anon-DELETE
mutation) — also gated in the same PR. Two additional tests below lock
the anon-401 behavior on the siblings; deferring session/token parity for
the siblings since the gate mechanism is identical to the detail view
already covered above.
"""
from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from core.models_unified_system import Agent, AgentMemory
from core.tests.helpers.agent_assignment import assign_agent_to_user
from core.tests.helpers.token_auth import token_client_for


User = get_user_model()


class MemoryDetailAuthGateTests(TestCase):
    """F-2 remediation: `/api/memory-palace/memory/<uuid>/` requires auth."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="mp_auth_gate_user",
            email="mp_auth_gate_user@example.com",
            password="test-pw",
        )
        # AgentMemory needs an Agent FK.
        self.agent = Agent.objects.create(
            name="memory_gate_agent",
            agent_type="test",
            description="",
            specialization="",
        )
        # S3019 (ADR-0008): assign the agent to `self.user` so scope predicate
        # doesn't 404 the positive-path tests. The S3017 tests originally
        # predated A.2 and relied on the unscoped `.get()`.
        assign_agent_to_user(self.agent, self.user)
        self.memory = AgentMemory.objects.create(
            agent=self.agent,
            title="F-2 remediation seed",
            content="anon must not reach this row",
            memory_type="insight",
        )

    def _url(self, memory_id: uuid.UUID) -> str:
        return f"/api/memory-palace/memory/{memory_id}/"

    def test_anonymous_returns_401_envelope(self) -> None:
        resp = Client(HTTP_HOST="localhost:8000").get(self._url(self.memory.id))
        self.assertEqual(resp.status_code, 401)
        body = resp.json()
        self.assertEqual(body.get("reason_code"), "not_authenticated")

    def test_anonymous_does_not_bump_access_count(self) -> None:
        """Side-effect hardening: pre-fix, anon reads bumped `access_count`.

        Post-fix the view body never runs for anon, so the counter stays put.
        """
        before = AgentMemory.objects.get(id=self.memory.id).access_count
        Client(HTTP_HOST="localhost:8000").get(self._url(self.memory.id))
        after = AgentMemory.objects.get(id=self.memory.id).access_count
        self.assertEqual(after, before)

    def test_session_auth_reaches_view(self) -> None:
        c = Client(HTTP_HOST="localhost:8000")
        c.force_login(self.user)
        resp = c.get(self._url(self.memory.id))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))

    def test_token_auth_reaches_view(self) -> None:
        """Parity with session-auth — Fold E shape applied to this endpoint."""
        resp = token_client_for(self.user).get(self._url(self.memory.id))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))

    # ---- F-3: sibling routes under the same bare-prefix ---------------

    def test_anonymous_connections_returns_401(self) -> None:
        """`/api/memory-palace/memory/<uuid>/connections/` — same-class
        F-2 read leak (anon could enumerate a memory's connection graph
        pre-fix). Post-fix: 401 envelope."""
        url = f"/api/memory-palace/memory/{self.memory.id}/connections/"
        resp = Client(HTTP_HOST="localhost:8000").get(url)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json().get("reason_code"), "not_authenticated")

    def test_anonymous_delete_returns_401_and_row_survives(self) -> None:
        """`/api/memory-palace/memory/<uuid>/delete/` — worse-than-F-2
        MUTATION leak (anon-DELETE-any-row pre-fix). Post-fix: 401
        envelope + row still exists (no delete side effect)."""
        url = f"/api/memory-palace/memory/{self.memory.id}/delete/"
        resp = Client(HTTP_HOST="localhost:8000").delete(url)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json().get("reason_code"), "not_authenticated")
        self.assertTrue(AgentMemory.objects.filter(id=self.memory.id).exists())
