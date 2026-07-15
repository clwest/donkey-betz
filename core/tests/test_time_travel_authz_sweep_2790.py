"""S2790 — 11 /api/time-travel/ mutation endpoints previously ungated.

Closes S2789 Fold B row 41 audit doc entry for prefix ``/api/time-travel/``
(largest remaining bucket at 11 endpoints). All 11 endpoints in
``core/views_time_travel.py`` were ``@csrf_exempt @require_http_methods([...])``
with **no auth decorator** — anon-reachable mutations against
``AgentSession`` / ``DecisionPoint`` / ``ReplayBookmark`` / ``DebugAnnotation``
DB rows.

**S2790 T1 SIGN adopted (fold rows 45-47):**

- Row 45 ``same_pr_mitigatable`` — Rigby's decorator-order suggestion (auth
  outermost) deferred; canonical S891 pattern in ``views_agent_learning.py`` +
  S2789 pilot-gates use ``@require_http_methods`` outermost. Match convention.
- Row 46 ``same_pr_actionable`` — Rigby Fold B: belt-and-suspenders
  session-auth-without-CSRF → 403 test class. **Adopted this PR** as
  ``TimeTravelAuthzSweepSessionWithoutCSRFTest`` — catches regressions if the
  S2787 CSRF interceptor in ``frontend/src/lib/api.ts:32-56`` breaks.
- Row 47 ``future_trigger`` — "per-prefix authZ sweep" pattern now 4-consecutive
  (S2787/S2788/S2789/S2790); PLAYBOOK-6.10.11+ codification candidate.

**S2787 CSRF cleanup pattern applied:** removed ``@csrf_exempt`` from all 11
views. Token/Bearer/X-API-Key callers bypass CSRF via the
``DisableCSRFForAuthEndpoints`` middleware (core/middleware.py:15-45); session
callers get CSRF protection per Django default (S1088 targeted exemption).

Endpoints gated this session:

- ``start_session`` (POST /api/time-travel/session/start/)
- ``end_session`` (POST /api/time-travel/session/<uuid>/end/)
- ``toggle_bookmark_session`` (POST /api/time-travel/session/<uuid>/bookmark/)
- ``record_decision`` (POST /api/time-travel/decision/)
- ``update_decision_outcome`` (POST /api/time-travel/decision/<uuid>/outcome/)
- ``flag_decision`` (POST /api/time-travel/decision/<uuid>/flag/)
- ``create_bookmark`` (POST /api/time-travel/bookmark/)
- ``delete_bookmark`` (DELETE /api/time-travel/bookmark/<uuid>/)
- ``add_annotation`` (POST /api/time-travel/annotation/)
- ``delete_annotation`` (DELETE /api/time-travel/annotation/<uuid>/)
- ``simulate_session`` (POST /api/time-travel/agent/<uuid>/simulate/)

Contract:

- Anonymous → 401 (blocked by ``@token_auth_required``).
- Authenticated (session or Token) → reachable (may 404/400/500 downstream
  when target DB row doesn't exist; assertion here is only "not 401").
- Session-auth without CSRF → 403 (S1088 CSRF gating).
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework.authtoken.models import Token


_BLOCKED_STATUS = 401  # token_auth_required returns exactly 401 for anon
_CSRF_MISSING_STATUS = 403  # CsrfViewMiddleware default rejection

# Bogus UUIDs so views reach their DB lookup and return 404 for authed callers
# (proving auth passed) instead of us needing to fixture a full
# AgentSession / DecisionPoint / ReplayBookmark / DebugAnnotation chain.
_S = '00000000-0000-0000-0000-000000000001'  # session_id
_D = '00000000-0000-0000-0000-000000000002'  # decision_id
_B = '00000000-0000-0000-0000-000000000003'  # bookmark_id
_A = '00000000-0000-0000-0000-000000000004'  # annotation_id
_G = '00000000-0000-0000-0000-000000000005'  # agent_id

# (name, method, path) — 11 endpoints.
_ENDPOINTS: list[tuple[str, str, str]] = [
    ('start-session',        'POST',   '/api/time-travel/session/start/'),
    ('end-session',          'POST',   f'/api/time-travel/session/{_S}/end/'),
    ('toggle-bookmark',      'POST',   f'/api/time-travel/session/{_S}/bookmark/'),
    ('record-decision',      'POST',   '/api/time-travel/decision/'),
    ('update-outcome',       'POST',   f'/api/time-travel/decision/{_D}/outcome/'),
    ('flag-decision',        'POST',   f'/api/time-travel/decision/{_D}/flag/'),
    ('create-bookmark',      'POST',   '/api/time-travel/bookmark/'),
    ('delete-bookmark',      'DELETE', f'/api/time-travel/bookmark/{_B}/'),
    ('add-annotation',       'POST',   '/api/time-travel/annotation/'),
    ('delete-annotation',    'DELETE', f'/api/time-travel/annotation/{_A}/'),
    ('simulate-session',     'POST',   f'/api/time-travel/agent/{_G}/simulate/'),
]


def _dispatch(client: Client, method: str, path: str, **extra) -> int:
    """Fire request with the given method + return status_code."""
    if method == 'POST':
        return client.post(path, data='{}', content_type='application/json', **extra).status_code
    if method == 'DELETE':
        return client.delete(path, **extra).status_code
    raise AssertionError(f"Unsupported method: {method}")


class TimeTravelAuthzSweepAnonymousTest(TestCase):
    """Anon callers must be blocked with 401 on all 11 endpoints."""

    def setUp(self):
        self.client = Client()

    def _assert_blocked(self, method: str, path: str) -> None:
        status = _dispatch(self.client, method, path)
        self.assertEqual(
            status, _BLOCKED_STATUS,
            f"{method} {path} returned {status}; expected 401 for anon",
        )

    def test_start_session_blocks_anonymous(self):
        self._assert_blocked(*_ENDPOINTS[0][1:])

    def test_end_session_blocks_anonymous(self):
        self._assert_blocked(*_ENDPOINTS[1][1:])

    def test_toggle_bookmark_blocks_anonymous(self):
        self._assert_blocked(*_ENDPOINTS[2][1:])

    def test_record_decision_blocks_anonymous(self):
        self._assert_blocked(*_ENDPOINTS[3][1:])

    def test_update_outcome_blocks_anonymous(self):
        self._assert_blocked(*_ENDPOINTS[4][1:])

    def test_flag_decision_blocks_anonymous(self):
        self._assert_blocked(*_ENDPOINTS[5][1:])

    def test_create_bookmark_blocks_anonymous(self):
        self._assert_blocked(*_ENDPOINTS[6][1:])

    def test_delete_bookmark_blocks_anonymous(self):
        self._assert_blocked(*_ENDPOINTS[7][1:])

    def test_add_annotation_blocks_anonymous(self):
        self._assert_blocked(*_ENDPOINTS[8][1:])

    def test_delete_annotation_blocks_anonymous(self):
        self._assert_blocked(*_ENDPOINTS[9][1:])

    def test_simulate_session_blocks_anonymous(self):
        self._assert_blocked(*_ENDPOINTS[10][1:])


class TimeTravelAuthzSweepAuthenticatedTest(TestCase):
    """Session-authed callers must reach the view (not 401)."""

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.user = U.objects.create_user(
            username='s2790-time-travel-fixture',
            email='s2790-time-travel@donkeybetz.test',
        )

    def setUp(self):
        # enforce_csrf_checks=False so session auth doesn't need CSRF token
        # (this class asserts auth reachability only; CSRF gap covered separately).
        self.client = Client()
        self.client.force_login(self.user)

    def _assert_reachable(self, method: str, path: str) -> None:
        status = _dispatch(self.client, method, path)
        self.assertNotEqual(
            status, _BLOCKED_STATUS,
            f"{method} {path} returned {status} for session-authed user; "
            f"expected view reached (not 401)",
        )

    def test_start_session_reachable_authed(self):
        self._assert_reachable(*_ENDPOINTS[0][1:])

    def test_end_session_reachable_authed(self):
        self._assert_reachable(*_ENDPOINTS[1][1:])

    def test_toggle_bookmark_reachable_authed(self):
        self._assert_reachable(*_ENDPOINTS[2][1:])

    def test_record_decision_reachable_authed(self):
        self._assert_reachable(*_ENDPOINTS[3][1:])

    def test_update_outcome_reachable_authed(self):
        self._assert_reachable(*_ENDPOINTS[4][1:])

    def test_flag_decision_reachable_authed(self):
        self._assert_reachable(*_ENDPOINTS[5][1:])

    def test_create_bookmark_reachable_authed(self):
        self._assert_reachable(*_ENDPOINTS[6][1:])

    def test_delete_bookmark_reachable_authed(self):
        self._assert_reachable(*_ENDPOINTS[7][1:])

    def test_add_annotation_reachable_authed(self):
        self._assert_reachable(*_ENDPOINTS[8][1:])

    def test_delete_annotation_reachable_authed(self):
        self._assert_reachable(*_ENDPOINTS[9][1:])

    def test_simulate_session_reachable_authed(self):
        self._assert_reachable(*_ENDPOINTS[10][1:])


class TimeTravelAuthzSweepTokenAuthS887PreservationTest(TestCase):
    """Token-authed callers must reach the view (S887 codepath preserved via DisableCSRFForAuthEndpoints)."""

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.user = U.objects.create_user(
            username='s2790-time-travel-token-fixture',
            email='s2790-time-travel-token@donkeybetz.test',
        )
        cls.token, _ = Token.objects.get_or_create(user=cls.user)

    def setUp(self):
        # enforce_csrf_checks=True + no session — pure Token-header auth (S887 shape).
        self.client = Client(enforce_csrf_checks=True)

    def _auth(self) -> dict:
        return {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def _assert_reachable(self, method: str, path: str) -> None:
        status = _dispatch(self.client, method, path, **self._auth())
        self.assertNotEqual(
            status, _BLOCKED_STATUS,
            f"{method} {path} returned {status} for Token auth; "
            f"S887 codepath broken",
        )

    def test_start_session_token_reachable(self):
        self._assert_reachable(*_ENDPOINTS[0][1:])

    def test_end_session_token_reachable(self):
        self._assert_reachable(*_ENDPOINTS[1][1:])

    def test_toggle_bookmark_token_reachable(self):
        self._assert_reachable(*_ENDPOINTS[2][1:])

    def test_record_decision_token_reachable(self):
        self._assert_reachable(*_ENDPOINTS[3][1:])

    def test_update_outcome_token_reachable(self):
        self._assert_reachable(*_ENDPOINTS[4][1:])

    def test_flag_decision_token_reachable(self):
        self._assert_reachable(*_ENDPOINTS[5][1:])

    def test_create_bookmark_token_reachable(self):
        self._assert_reachable(*_ENDPOINTS[6][1:])

    def test_delete_bookmark_token_reachable(self):
        self._assert_reachable(*_ENDPOINTS[7][1:])

    def test_add_annotation_token_reachable(self):
        self._assert_reachable(*_ENDPOINTS[8][1:])

    def test_delete_annotation_token_reachable(self):
        self._assert_reachable(*_ENDPOINTS[9][1:])

    def test_simulate_session_token_reachable(self):
        self._assert_reachable(*_ENDPOINTS[10][1:])


class TimeTravelAuthzSweepSessionWithoutCSRFTest(TestCase):
    """Rigby Fold B — session-auth without CSRF token must be rejected (403).

    Belt-and-suspenders: catches regressions if the S2787 CSRF interceptor in
    ``frontend/src/lib/api.ts:32-56`` breaks. Session auth without CSRF should
    NOT reach the view — CsrfViewMiddleware rejects with 403 for unsafe methods.
    """

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.user = U.objects.create_user(
            username='s2790-time-travel-nocsrf-fixture',
            email='s2790-time-travel-nocsrf@donkeybetz.test',
        )

    def setUp(self):
        # enforce_csrf_checks=True + session cookie (no Authorization header).
        # CsrfViewMiddleware should reject unsafe methods without X-CSRFToken.
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.user)

    def _assert_csrf_blocked(self, method: str, path: str) -> None:
        status = _dispatch(self.client, method, path)
        self.assertEqual(
            status, _CSRF_MISSING_STATUS,
            f"{method} {path} returned {status} for session-auth without CSRF; "
            f"expected 403 (CsrfViewMiddleware rejection)",
        )

    def test_start_session_csrf_gap(self):
        self._assert_csrf_blocked(*_ENDPOINTS[0][1:])

    def test_end_session_csrf_gap(self):
        self._assert_csrf_blocked(*_ENDPOINTS[1][1:])

    def test_toggle_bookmark_csrf_gap(self):
        self._assert_csrf_blocked(*_ENDPOINTS[2][1:])

    def test_record_decision_csrf_gap(self):
        self._assert_csrf_blocked(*_ENDPOINTS[3][1:])

    def test_update_outcome_csrf_gap(self):
        self._assert_csrf_blocked(*_ENDPOINTS[4][1:])

    def test_flag_decision_csrf_gap(self):
        self._assert_csrf_blocked(*_ENDPOINTS[5][1:])

    def test_create_bookmark_csrf_gap(self):
        self._assert_csrf_blocked(*_ENDPOINTS[6][1:])

    def test_delete_bookmark_csrf_gap(self):
        self._assert_csrf_blocked(*_ENDPOINTS[7][1:])

    def test_add_annotation_csrf_gap(self):
        self._assert_csrf_blocked(*_ENDPOINTS[8][1:])

    def test_delete_annotation_csrf_gap(self):
        self._assert_csrf_blocked(*_ENDPOINTS[9][1:])

    def test_simulate_session_csrf_gap(self):
        self._assert_csrf_blocked(*_ENDPOINTS[10][1:])
