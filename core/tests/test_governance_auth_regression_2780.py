"""S2780 N22 v3 — /api/governance/* auth regression.

Mirrors ``test_ops_auth_regression_2772.py`` for the new
``/api/governance/*`` namespace introduced by S2780 (dedicated home for
governance-scope REST endpoints, factored out from ``/api/ops/*`` per
S2779 V6 fold + S2780 T1 SIGN V7 fold A).

Contract per S2772 N16 (Rigby-ratified): every governance endpoint MUST
be both ``@login_required`` AND staff-only. Anon → blocked. Authenticated
non-staff → blocked. Authenticated staff → reachable (may return 200 or
soft-500, but never a blocking status).

Adding a new ``/api/governance/*`` endpoint? Add matching
``test_<name>_blocks_anonymous`` + ``test_<name>_blocks_non_staff``
methods below. The route-inventory guard at the bottom fails loud on
drift.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


_BLOCKED_STATUSES = {302, 401, 403}

# S2780 route inventory — mirror the S2772 pattern.
_GOVERNANCE_ENDPOINTS: list[tuple[str, str]] = [
    ('governance-zoom-out-ledger', '/api/governance/zoom-out-ledger/'),
]


class GovernanceAuthRegressionAnonymousTest(TestCase):
    """Anonymous requests to /api/governance/* must be blocked."""

    def setUp(self):
        self.client = Client()

    def test_zoom_out_ledger_blocks_anonymous(self):
        response = self.client.get('/api/governance/zoom-out-ledger/')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)


class GovernanceAuthRegressionNonStaffTest(TestCase):
    """Authenticated non-staff users must also be blocked from /api/governance/*."""

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.non_staff = U.objects.create_user(
            username='s2780-non-staff-fixture',
            email='s2780-non-staff@donkeybetz.test',
        )
        cls.non_staff.is_staff = False
        cls.non_staff.is_superuser = False
        cls.non_staff.save()

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.non_staff)

    def test_zoom_out_ledger_blocks_non_staff(self):
        response = self.client.get('/api/governance/zoom-out-ledger/')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)


class GovernanceAuthStaffAllowedTest(TestCase):
    """Sanity check: authenticated staff CAN reach /api/governance/*.

    Fail-soft is acceptable (200 or 500), but blocking statuses are not.
    """

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.staff = U.objects.create_user(
            username='s2780-staff-fixture',
            email='s2780-staff@donkeybetz.test',
        )
        cls.staff.is_staff = True
        cls.staff.save()

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.staff)

    def test_zoom_out_ledger_reachable_by_staff(self):
        response = self.client.get('/api/governance/zoom-out-ledger/?limit=1')
        self.assertNotIn(response.status_code, _BLOCKED_STATUSES)


class GovernanceRouteInventoryGuardTest(TestCase):
    """Route inventory guard — every entry in ``_GOVERNANCE_ENDPOINTS`` must
    have matching anon + non-staff test methods above. Fails loud on drift.
    """

    def test_all_governance_endpoints_have_auth_tests(self):
        expected_anon = {
            f'test_{name.removeprefix("governance-").replace("-", "_")}_blocks_anonymous'
            for name, _path in _GOVERNANCE_ENDPOINTS
        }
        expected_non_staff = {
            f'test_{name.removeprefix("governance-").replace("-", "_")}_blocks_non_staff'
            for name, _path in _GOVERNANCE_ENDPOINTS
        }
        anon_methods = {m for m in dir(GovernanceAuthRegressionAnonymousTest) if m.startswith('test_')}
        non_staff_methods = {m for m in dir(GovernanceAuthRegressionNonStaffTest) if m.startswith('test_')}
        missing_anon = expected_anon - anon_methods
        missing_non_staff = expected_non_staff - non_staff_methods
        self.assertFalse(missing_anon, f"Missing anon tests: {missing_anon}")
        self.assertFalse(missing_non_staff, f"Missing non-staff tests: {missing_non_staff}")

    def test_url_space_matches_inventory(self):
        from django.urls import reverse
        for name, expected_path in _GOVERNANCE_ENDPOINTS:
            resolved = reverse(name)
            self.assertEqual(
                resolved,
                expected_path,
                f"Route name {name!r} resolves to {resolved!r}, not {expected_path!r}",
            )
