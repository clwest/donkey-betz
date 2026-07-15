"""S2789 Fold B follow-up — 7 pilot-gates mutation endpoints previously ungated.

Closes S2788 handoff row 41 ``future_trigger`` (proactive; the 4th public+unsafe-
method site trigger had not yet fired). All 7 endpoints in
``core/views_agent_learning.py`` were @require_http_methods(["POST"]) with **no
auth decorator** — anon-reachable POST mutations against
``PilotReadinessGate`` / ``PilotExecution`` / checklist item state.

**Rigby S2789 T1 SIGN correction (fold rows 42+43):** gate with
``@token_auth_required`` (existing decorator at ``core/auth_middleware.py:36-81``,
supports session OR Token/Bearer, returns JSON 401 via ``api_unauthorized``) —
**NOT** ``@login_required``, which would 302-redirect to ``LOGIN_URL`` (HTML) and
break Token clients on PUBLIC_PATHS bypass.

Endpoints gated this session:

- ``update_gate_status`` (POST /api/pilot-gates/<uuid>/status/)
- ``update_checklist_item`` (POST /api/pilot-gates/<uuid>/items/<uuid>/)
- ``create_pilot_gate`` (POST /api/pilot-gates/create/<uuid:decision_id>/) — the
  classifier missed this one (custom ``.create_for_decision()`` factory call,
  not ``.objects.create()``); included for completeness of the prefix sweep.
- ``start_pilot_execution`` (POST /api/pilot-gates/<uuid>/pilot/)
- ``complete_pilot_execution`` (POST /api/pilot-gates/<uuid>/pilot/<uuid>/complete/)
- ``regenerate_checklist_content`` (POST /api/pilot-gates/<uuid>/regenerate/)
- ``approve_all_checklist_items`` (POST /api/pilot-gates/<uuid>/approve-all/)

Contract per S2789 (Fold B row 41 proactive close):

- Anonymous → 401 (blocked by ``@token_auth_required``).
- Authenticated (any active user) → reachable (may 404/500 downstream when
  gate_id/decision_id doesn't exist; the assertion here is only "not 401").
- Token-authed → reachable (S887 preservation via
  ``DisableCSRFForAuthEndpoints`` middleware).
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework.authtoken.models import Token


_BLOCKED_STATUS = 401  # token_auth_required returns exactly 401 for anon

# Bogus UUIDs so views reach their DB lookup and return 404 for authed callers
# (proving auth passed) instead of us needing to fixture up a full
# PilotReadinessGate / PilotExecution / AgentDecisionSummary chain.
_G = '00000000-0000-0000-0000-000000000001'  # gate_id
_I = '00000000-0000-0000-0000-000000000002'  # item_id
_P = '00000000-0000-0000-0000-000000000003'  # pilot_id
_D = '00000000-0000-0000-0000-000000000004'  # decision_id

# (name, path) pairs — one per newly-gated endpoint.
_ENDPOINTS: list[tuple[str, str]] = [
    ('pilot-gate-status',           f'/api/pilot-gates/{_G}/status/'),
    ('pilot-gate-item',             f'/api/pilot-gates/{_G}/items/{_I}/'),
    ('pilot-gate-create',           f'/api/pilot-gates/create/{_D}/'),
    ('start-pilot-execution',       f'/api/pilot-gates/{_G}/pilot/'),
    ('complete-pilot-execution',    f'/api/pilot-gates/{_G}/pilot/{_P}/complete/'),
    ('regenerate-checklist',        f'/api/pilot-gates/{_G}/regenerate/'),
    ('approve-all-checklist',       f'/api/pilot-gates/{_G}/approve-all/'),
]


class PilotGatesAuthzSweepAnonymousTest(TestCase):
    """Anon callers must be blocked with 401 on all 7 endpoints (was gap: anon-reachable POST)."""

    def setUp(self):
        self.client = Client()

    def _assert_blocked(self, path: str) -> None:
        response = self.client.post(path, data='{}', content_type='application/json')
        self.assertEqual(
            response.status_code, _BLOCKED_STATUS,
            f"POST {path} returned {response.status_code}; expected 401 "
            f"(token_auth_required for anon)",
        )

    def test_pilot_gate_status_blocks_anonymous(self):
        self._assert_blocked(_ENDPOINTS[0][1])

    def test_pilot_gate_item_blocks_anonymous(self):
        self._assert_blocked(_ENDPOINTS[1][1])

    def test_pilot_gate_create_blocks_anonymous(self):
        self._assert_blocked(_ENDPOINTS[2][1])

    def test_start_pilot_execution_blocks_anonymous(self):
        self._assert_blocked(_ENDPOINTS[3][1])

    def test_complete_pilot_execution_blocks_anonymous(self):
        self._assert_blocked(_ENDPOINTS[4][1])

    def test_regenerate_checklist_blocks_anonymous(self):
        self._assert_blocked(_ENDPOINTS[5][1])

    def test_approve_all_checklist_blocks_anonymous(self):
        self._assert_blocked(_ENDPOINTS[6][1])


class PilotGatesAuthzSweepAuthenticatedTest(TestCase):
    """Authenticated callers must reach the view (not 401)."""

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.user = U.objects.create_user(
            username='s2789-pilot-gates-fixture',
            email='s2789-pilot-gates@donkeybetz.test',
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def _assert_reachable(self, path: str) -> None:
        response = self.client.post(path, data='{}', content_type='application/json')
        self.assertNotEqual(
            response.status_code, _BLOCKED_STATUS,
            f"POST {path} returned {response.status_code} for authed user; "
            f"expected view reached (not 401)",
        )

    def test_pilot_gate_status_reachable_authed(self):
        self._assert_reachable(_ENDPOINTS[0][1])

    def test_pilot_gate_item_reachable_authed(self):
        self._assert_reachable(_ENDPOINTS[1][1])

    def test_pilot_gate_create_reachable_authed(self):
        self._assert_reachable(_ENDPOINTS[2][1])

    def test_start_pilot_execution_reachable_authed(self):
        self._assert_reachable(_ENDPOINTS[3][1])

    def test_complete_pilot_execution_reachable_authed(self):
        self._assert_reachable(_ENDPOINTS[4][1])

    def test_regenerate_checklist_reachable_authed(self):
        self._assert_reachable(_ENDPOINTS[5][1])

    def test_approve_all_checklist_reachable_authed(self):
        self._assert_reachable(_ENDPOINTS[6][1])


class PilotGatesAuthzSweepTokenAuthS887PreservationTest(TestCase):
    """Token-authed callers must reach the view (S887 codepath preserved via DisableCSRFForAuthEndpoints)."""

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.user = U.objects.create_user(
            username='s2789-pilot-gates-token-fixture',
            email='s2789-pilot-gates-token@donkeybetz.test',
        )
        cls.token, _ = Token.objects.get_or_create(user=cls.user)

    def setUp(self):
        # enforce_csrf_checks=True + no session — pure Token-header auth (S887 shape).
        self.client = Client(enforce_csrf_checks=True)

    def _auth(self) -> dict:
        return {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def _assert_reachable(self, path: str) -> None:
        response = self.client.post(
            path, data='{}', content_type='application/json', **self._auth(),
        )
        self.assertNotEqual(
            response.status_code, _BLOCKED_STATUS,
            f"POST {path} returned {response.status_code} for Token auth; "
            f"S887 codepath broken",
        )

    def test_pilot_gate_status_token_reachable(self):
        self._assert_reachable(_ENDPOINTS[0][1])

    def test_pilot_gate_item_token_reachable(self):
        self._assert_reachable(_ENDPOINTS[1][1])

    def test_pilot_gate_create_token_reachable(self):
        self._assert_reachable(_ENDPOINTS[2][1])

    def test_start_pilot_execution_token_reachable(self):
        self._assert_reachable(_ENDPOINTS[3][1])

    def test_complete_pilot_execution_token_reachable(self):
        self._assert_reachable(_ENDPOINTS[4][1])

    def test_regenerate_checklist_token_reachable(self):
        self._assert_reachable(_ENDPOINTS[5][1])

    def test_approve_all_checklist_token_reachable(self):
        self._assert_reachable(_ENDPOINTS[6][1])
