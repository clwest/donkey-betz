"""S2787 — CSRF enforcement regression on the 31 mutation endpoints S2784+S2785 gated staff-only.

Companion to ``test_platform_auth_regression_2784.py`` and
``test_decision_approve_auth_regression_2785.py``. Those files verify authN + authZ.
This file verifies the CSRF posture after removing ``@csrf_exempt`` from the same 31
endpoints in S2787.

Contract:

1. Session-cookie caller (browser) without ``X-CSRFToken`` → **403** (CSRF middleware blocks).
2. Session-cookie caller with valid ``X-CSRFToken`` → **not 403** (CSRF middleware passes;
   downstream may return 200/400/500 depending on payload — that's not our concern here).
3. Token/Bearer caller without any CSRF header → **not 403** (S887 preservation:
   ``core/middleware.py::DisableCSRFForAuthEndpoints`` short-circuits CSRF for Token/Bearer/
   X-API-Key requests BEFORE ``CsrfViewMiddleware`` runs).

The 31-endpoint inventory below intentionally duplicates the S2784/S2785 route lists
so drift on either side is caught. Add a new mutation endpoint? Add it to the matching
list here AND the auth-regression file for that family.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token
from django.test import Client, RequestFactory, TestCase
from rest_framework.authtoken.models import Token


# S2787: Mutations that previously had @csrf_exempt (now removed). Uses (name, path, body)
# where body is a JSON string sent with content_type='application/json'.
_PLATFORM_ENDPOINTS: list[tuple[str, str]] = [
    ('platform-emergency-halt', '/api/platform/emergency-halt/'),
    ('platform-skin-lock', '/api/platform/skin-lock/'),
    ('platform-canon-promote', '/api/platform/canon/promote/'),
    ('platform-audits-run', '/api/platform/audits/run/'),
    ('platform-trigger-run-now', '/api/platform/triggers/run-now/'),
    ('platform-action-run-spiders', '/api/platform/actions/run-spiders/'),
    ('platform-action-run-remediation', '/api/platform/actions/run-remediation/'),
    ('platform-action-agent-health', '/api/platform/actions/agent-health-check/'),
    ('platform-action-category-rotation', '/api/platform/actions/agent-category-rotation/'),
    ('platform-action-run-self-audit', '/api/platform/actions/run-self-audit/'),
    ('platform-decision-create-initiative',
     '/api/platform/decision-summary/00000000-0000-0000-0000-000000000000/create-initiative/'),
    ('platform-trigger-toggle', '/api/platform/triggers/rule-name/toggle/'),
]

_HUMAN_CBV_ENDPOINTS: list[tuple[str, str]] = [
    # S2785 15 CBVs in core/views_human_interface.py — all POST/PUT surfaces stripped of
    # csrf_exempt in the method_decorator list.
    ('human-attention-stream', '/api/human/attention/'),
    ('human-attention-detail', '/api/human/attention/00000000-0000-0000-0000-000000000000/'),
    ('human-attention-stats', '/api/human/attention/stats/'),
    ('human-attention-decide', '/api/human/attention/00000000-0000-0000-0000-000000000000/decide/'),
    ('human-attention-defer', '/api/human/attention/00000000-0000-0000-0000-000000000000/defer/'),
    ('human-attention-verify', '/api/human/attention/00000000-0000-0000-0000-000000000000/verify/'),
    ('human-attention-execute', '/api/human/attention/00000000-0000-0000-0000-000000000000/execute/'),
    ('human-control', '/api/human/control/'),
    ('human-control-pause', '/api/human/control/pause/'),
    ('human-control-resume', '/api/human/control/resume/'),
    ('human-control-quiet', '/api/human/control/quiet/'),
    ('human-control-review', '/api/human/control/review/'),
    ('human-control-threshold', '/api/human/control/threshold/'),
    ('human-preferences', '/api/human/preferences/'),
    ('human-attention-bulk-decide', '/api/human/attention/bulk-decide/'),
]

_BOARDROOM_ENDPOINTS: list[tuple[str, str]] = [
    # S2785 4 function views in core/views_agent_learning.py — csrf_exempt removed.
    # These use the _require_boardroom_staff helper (S887 Token-auth preserved).
    ('boardroom-promote', '/api/boardroom/decisions/00000000-0000-0000-0000-000000000000/promote/'),
    ('boardroom-reject', '/api/boardroom/decisions/00000000-0000-0000-0000-000000000000/reject/'),
    ('boardroom-bulk-promote', '/api/boardroom/decisions/bulk-promote/'),
    ('boardroom-bulk-reject', '/api/boardroom/decisions/bulk-reject/'),
]

_ALL_ENDPOINTS = _PLATFORM_ENDPOINTS + _HUMAN_CBV_ENDPOINTS + _BOARDROOM_ENDPOINTS


class SessionAuthCsrfEnforcementTest(TestCase):
    """Session-cookie POST without X-CSRFToken must be blocked with 403."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user(
            username='s2787-csrf-staff-fixture',
            email='s2787-csrf@example.com',
            is_staff=True,
        )

    def setUp(self):
        # enforce_csrf_checks=True flips Django's test client to run CSRF like a browser.
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.staff)

    def test_session_authed_post_without_csrf_returns_403(self):
        for name, path in _ALL_ENDPOINTS:
            with self.subTest(endpoint=name, path=path):
                response = self.client.post(path, data='{}', content_type='application/json')
                self.assertEqual(
                    response.status_code, 403,
                    f"{name} ({path}) expected 403 without CSRF token, got {response.status_code}",
                )


class SessionAuthCsrfPassTest(TestCase):
    """Session-cookie POST with valid X-CSRFToken must not be blocked by CSRF."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user(
            username='s2787-csrf-pass-fixture',
            email='s2787-csrf-pass@example.com',
            is_staff=True,
        )

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.staff)
        # Mint a CSRF token bound to this client's session.
        factory = RequestFactory()
        request = factory.get('/')
        request.session = self.client.session
        self.csrf_token = get_token(request)
        # get_token also seeds the cookie for browsers; propagate to the test client.
        self.client.cookies['csrftoken'] = self.csrf_token

    def test_session_authed_post_with_csrf_not_forbidden_by_csrf(self):
        for name, path in _ALL_ENDPOINTS:
            with self.subTest(endpoint=name, path=path):
                response = self.client.post(
                    path,
                    data='{}',
                    content_type='application/json',
                    HTTP_X_CSRFTOKEN=self.csrf_token,
                )
                # 403 from CSRF middleware is the failure mode we're guarding against.
                # 404 is acceptable for endpoints with kwarg placeholders that don't resolve
                # to real records; downstream 200/400/500 is also fine — this test only
                # verifies CSRF middleware doesn't block.
                self.assertNotEqual(
                    response.status_code, 403,
                    f"{name} ({path}) returned 403 with valid CSRF token — CSRF pass path broken",
                )


class TokenAuthS887PreservationTest(TestCase):
    """Token-authed POST without CSRF must not be blocked (S887 preservation regression)."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user(
            username='s2787-token-staff-fixture',
            email='s2787-token@example.com',
            is_staff=True,
        )
        cls.token, _ = Token.objects.get_or_create(user=cls.staff)

    def setUp(self):
        # No force_login — auth is exclusively via Authorization header.
        self.client = Client(enforce_csrf_checks=True)

    def test_token_authed_post_no_csrf_not_forbidden(self):
        auth_header = f'Token {self.token.key}'
        for name, path in _ALL_ENDPOINTS:
            with self.subTest(endpoint=name, path=path):
                response = self.client.post(
                    path,
                    data='{}',
                    content_type='application/json',
                    HTTP_AUTHORIZATION=auth_header,
                )
                # Same acceptance shape as the CSRF-pass test — 403 is the specific failure.
                self.assertNotEqual(
                    response.status_code, 403,
                    f"{name} ({path}) returned 403 for Token-authed request — S887 codepath broken",
                )
