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
"""
from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from core.models_unified_system import Agent, AgentMemory
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
