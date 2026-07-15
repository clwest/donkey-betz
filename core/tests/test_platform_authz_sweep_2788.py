"""S2788 Fold C follow-up — 3 platform-command endpoints previously lacking staff-only gate.

Mirrors ``test_platform_auth_regression_2784.py`` for the 3 endpoints S2788
closed in ``core/views_platform_command.py``:

- ``celery_debug_view`` (GET) — was in PUBLIC_PATHS, leaked redis/beat/periodic-task state
  to anonymous callers. Fix: removed from PUBLIC_PATHS + added @login_required +
  @_platform_staff_only.
- ``cleanup_stale_executions_view`` (POST) — was in PUBLIC_PATHS = anon-reachable
  mutation. Fix: removed from PUBLIC_PATHS + added @login_required +
  @_platform_staff_only + removed @csrf_exempt.
- ``delete_failed_executions_view`` (POST/DELETE) — was NOT in PUBLIC_PATHS
  (middleware enforced authN) but lacked staff-only gate. Fix: added
  @login_required + @_platform_staff_only + removed @csrf_exempt.

Contract per S2772 N16 (Rigby-ratified): every platform mutation OR sensitive-
info-leaking endpoint MUST be both ``@login_required`` AND staff-only.
Anonymous → blocked. Authenticated non-staff → blocked. Authenticated staff →
reachable. Token-authed staff → reachable (S887 preservation via
``DisableCSRFForAuthEndpoints`` middleware).
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework.authtoken.models import Token


_BLOCKED_STATUSES = {302, 401, 403}

# S2788 sweep — the 3 endpoints closed in this arc.
_GET_ENDPOINTS: list[tuple[str, str]] = [
    ('platform-celery-debug', '/api/platform/celery-debug/'),
]

_POST_ENDPOINTS: list[tuple[str, str]] = [
    ('platform-cleanup-stale', '/api/platform/cleanup-stale-executions/'),
    ('platform-delete-failed', '/api/platform/delete-failed-executions/'),
]


class PlatformAuthzSweepAnonymousTest(TestCase):
    """Anonymous callers must be blocked on all 3 endpoints (was gap for celery-debug + cleanup)."""

    def setUp(self):
        self.client = Client()

    def _assert_blocked_get(self, path: str) -> None:
        response = self.client.get(path)
        self.assertIn(
            response.status_code, _BLOCKED_STATUSES,
            f"GET {path} returned {response.status_code}; expected one of {_BLOCKED_STATUSES}",
        )

    def _assert_blocked_post(self, path: str) -> None:
        response = self.client.post(path, data='{}', content_type='application/json')
        self.assertIn(
            response.status_code, _BLOCKED_STATUSES,
            f"POST {path} returned {response.status_code}; expected one of {_BLOCKED_STATUSES}",
        )

    def test_celery_debug_blocks_anonymous(self):
        self._assert_blocked_get('/api/platform/celery-debug/')

    def test_cleanup_stale_blocks_anonymous(self):
        self._assert_blocked_post('/api/platform/cleanup-stale-executions/')

    def test_delete_failed_blocks_anonymous(self):
        self._assert_blocked_post('/api/platform/delete-failed-executions/')


class PlatformAuthzSweepNonStaffTest(TestCase):
    """Authenticated non-staff must also be blocked (was gap for all 3)."""

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.non_staff = U.objects.create_user(
            username='s2788-non-staff-fixture',
            email='s2788-non-staff@donkeybetz.test',
        )
        cls.non_staff.is_staff = False
        cls.non_staff.is_superuser = False
        cls.non_staff.save()

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.non_staff)

    def test_celery_debug_blocks_non_staff(self):
        response = self.client.get('/api/platform/celery-debug/')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)

    def test_cleanup_stale_blocks_non_staff(self):
        response = self.client.post('/api/platform/cleanup-stale-executions/',
                                     data='{}', content_type='application/json')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)

    def test_delete_failed_blocks_non_staff(self):
        response = self.client.post('/api/platform/delete-failed-executions/',
                                     data='{}', content_type='application/json')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)


class PlatformAuthzSweepStaffReachableTest(TestCase):
    """Authenticated staff must reach the view (may 200 or soft-500, never 401/403)."""

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.staff = U.objects.create_user(
            username='s2788-staff-fixture',
            email='s2788-staff@donkeybetz.test',
            is_staff=True,
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.staff)

    def test_celery_debug_reachable_by_staff(self):
        response = self.client.get('/api/platform/celery-debug/')
        self.assertNotIn(response.status_code, _BLOCKED_STATUSES,
                          f"GET celery-debug returned {response.status_code}; staff should reach it")

    def test_cleanup_stale_reachable_by_staff(self):
        response = self.client.post('/api/platform/cleanup-stale-executions/',
                                     data='{}', content_type='application/json')
        self.assertNotIn(response.status_code, _BLOCKED_STATUSES,
                          f"POST cleanup-stale returned {response.status_code}; staff should reach it")

    def test_delete_failed_reachable_by_staff(self):
        response = self.client.post('/api/platform/delete-failed-executions/',
                                     data='{}', content_type='application/json')
        self.assertNotIn(response.status_code, _BLOCKED_STATUSES,
                          f"POST delete-failed returned {response.status_code}; staff should reach it")


class PlatformAuthzSweepTokenAuthS887PreservationTest(TestCase):
    """Token-authed staff must reach the view (S887 codepath preserved via DisableCSRFForAuthEndpoints)."""

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.staff = U.objects.create_user(
            username='s2788-token-staff-fixture',
            email='s2788-token-staff@donkeybetz.test',
            is_staff=True,
        )
        cls.token, _ = Token.objects.get_or_create(user=cls.staff)

    def setUp(self):
        # enforce_csrf_checks=True + no session — pure Token-header auth.
        self.client = Client(enforce_csrf_checks=True)

    def _auth(self) -> dict:
        return {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_celery_debug_token_authed_reachable(self):
        response = self.client.get('/api/platform/celery-debug/', **self._auth())
        self.assertNotIn(response.status_code, _BLOCKED_STATUSES,
                          f"GET celery-debug returned {response.status_code} for Token auth; S887 codepath broken")

    def test_cleanup_stale_token_authed_reachable(self):
        response = self.client.post('/api/platform/cleanup-stale-executions/',
                                     data='{}', content_type='application/json', **self._auth())
        self.assertNotIn(response.status_code, _BLOCKED_STATUSES,
                          f"POST cleanup-stale returned {response.status_code} for Token auth; S887 codepath broken")

    def test_delete_failed_token_authed_reachable(self):
        response = self.client.post('/api/platform/delete-failed-executions/',
                                     data='{}', content_type='application/json', **self._auth())
        self.assertNotIn(response.status_code, _BLOCKED_STATUSES,
                          f"POST delete-failed returned {response.status_code} for Token auth; S887 codepath broken")
