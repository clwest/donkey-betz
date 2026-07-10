"""
tests/security/test_i0302_c1_chat_conversation_wiring.py — I-0302 Phase 3
Sub-phase C1 predicate-wiring integration regression suite.

Ratified via Rigby SIGN Q5 (2026-07-10): C1 wires 18 sites across 3 view
files (views_personal_assistant, views_session_handoff, views_project_hub)
+ applies Option A staff-tightening (replaces legacy `is_staff` bypass
with the ratified predicate contract).

Coverage per Q5 SIGN minimum:
  1. Regular user reads own conversation (200 + content).
  2. Regular user cannot read another user's conversation (404).
  3. Non-superuser staff no longer bypass (Option A tightening probe).
  4. Anonymous safety on a representative endpoint.

Contract refs:
  docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase2_predicate_module.md §8
  docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md §5.3.a
"""
from __future__ import annotations

import uuid

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from core.models import ChatConversation

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
def staff_user(db):
    """Non-superuser staff — the population Option A tightens against."""
    return User.objects.create_user(
        username=f"staff-{uuid.uuid4().hex[:6]}",
        email=f"s-{uuid.uuid4().hex[:6]}@example.com",
        password="pw",
        is_staff=True,
        is_superuser=False,
    )


@pytest.fixture
def conversation_a(user_a):
    """A conversation owned by user_a with a single message row."""
    conv_id = f"test-conv-a-{uuid.uuid4().hex[:8]}"
    ChatConversation.objects.create(
        user=user_a,
        conversation_id=conv_id,
        user_message="hello from a",
        assistant_response="",
        source="test",
        platform="web",
    )
    return conv_id


# ==========================================================================
# GET /api/pa-conversations/<id>/ — get_pa_conversation
# ==========================================================================


class TestGetPAConversationScoping:
    """Exercises get_pa_conversation (views_personal_assistant.py :1618)."""

    def test_owner_can_read_own_conversation(
        self, client, user_a, conversation_a
    ):
        client.force_login(user_a)
        resp = client.get(f"/api/pa/conversations/{conversation_a}/")
        assert resp.status_code == 200, (
            f"Owner must be able to read own conversation; got {resp.status_code}"
        )

    def test_non_owner_gets_404(
        self, client, user_a, user_b, conversation_a
    ):
        # user_b is NOT the owner of conversation_a; must 404 (not 200,
        # not 500). Existence-oracle safe.
        client.force_login(user_b)
        resp = client.get(f"/api/pa/conversations/{conversation_a}/")
        assert resp.status_code == 404, (
            f"Non-owner must receive 404 on someone else's conversation; "
            f"got {resp.status_code}"
        )

    def test_non_superuser_staff_no_longer_bypasses(
        self, client, staff_user, user_a, conversation_a
    ):
        # Option A tightening probe (Rigby SIGN Q1 fold): non-superuser
        # staff must NOT bypass and read user_a's conversation. Before
        # C1, `if not request.user.is_staff:` let staff through freely.
        # After C1, only the predicate boundary (own + workspace) grants
        # access.
        client.force_login(staff_user)
        resp = client.get(f"/api/pa/conversations/{conversation_a}/")
        assert resp.status_code == 404, (
            f"Non-superuser staff must not bypass under Option A; got "
            f"{resp.status_code} (regression against §5.3.a staff-tightening)"
        )

    def test_anonymous_gets_401_or_403(self, conversation_a):
        # DRF IsAuthenticated → 403 by default; either 401 or 403 is
        # acceptable as "no anonymous access."
        resp = Client().get(f"/api/pa/conversations/{conversation_a}/")
        assert resp.status_code in (401, 403), (
            f"Anonymous must be blocked from PA conversation reads; got "
            f"{resp.status_code}"
        )
