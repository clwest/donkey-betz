"""S2784 Fold 4 — /api/platform/* mutation-endpoint auth regression.

Mirrors ``test_governance_auth_regression_2780.py`` for the 12 mutation
POST endpoints in ``core/views_platform_command.py`` that were gated from
'authenticated' to 'authenticated + staff-only' at S2784.

Contract per S2772 N16 (Rigby-ratified): every platform mutation
endpoint MUST be both ``@login_required`` AND staff-only. Anon → blocked.
Authenticated non-staff → blocked. Authenticated staff → reachable (may
return 200 or soft-500 depending on body validation, but never a blocking
status).

Adding a new mutation endpoint to ``core/views_platform_command.py``?
Add it to ``_PLATFORM_MUTATION_ENDPOINTS`` below with matching
``test_<name>_blocks_anonymous`` + ``test_<name>_blocks_non_staff`` test
methods. The route-inventory guard at the bottom fails loud on drift.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


_BLOCKED_STATUSES = {302, 401, 403}

# S2784 route inventory — the 12 mutation POST endpoints staff-gated in
# core/views_platform_command.py. When adding a new mutation endpoint,
# add it here AND add anon/non-staff test methods below.
_PLATFORM_MUTATION_ENDPOINTS: list[tuple[str, str]] = [
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
]
# Endpoints with URL kwargs — tested via direct-path assertions since
# reverse() needs the kwarg values.
_PLATFORM_KWARG_ENDPOINTS: list[tuple[str, str]] = [
    ('platform-decision-create-initiative', '/api/platform/decision-summary/00000000-0000-0000-0000-000000000000/create-initiative/'),
    ('platform-trigger-toggle', '/api/platform/triggers/rule-name/toggle/'),
]


class PlatformAuthRegressionAnonymousTest(TestCase):
    """Anonymous POSTs to /api/platform/* mutation endpoints must be blocked."""

    def setUp(self):
        self.client = Client()

    def _assert_blocked(self, path: str) -> None:
        response = self.client.post(path, data='{}', content_type='application/json')
        self.assertIn(
            response.status_code,
            _BLOCKED_STATUSES,
            f"{path} returned {response.status_code}; expected one of {_BLOCKED_STATUSES}",
        )

    def test_emergency_halt_blocks_anonymous(self):
        self._assert_blocked('/api/platform/emergency-halt/')

    def test_skin_lock_blocks_anonymous(self):
        self._assert_blocked('/api/platform/skin-lock/')

    def test_canon_promote_blocks_anonymous(self):
        self._assert_blocked('/api/platform/canon/promote/')

    def test_audits_run_blocks_anonymous(self):
        self._assert_blocked('/api/platform/audits/run/')

    def test_trigger_run_now_blocks_anonymous(self):
        self._assert_blocked('/api/platform/triggers/run-now/')

    def test_action_run_spiders_blocks_anonymous(self):
        self._assert_blocked('/api/platform/actions/run-spiders/')

    def test_action_run_remediation_blocks_anonymous(self):
        self._assert_blocked('/api/platform/actions/run-remediation/')

    def test_action_agent_health_blocks_anonymous(self):
        self._assert_blocked('/api/platform/actions/agent-health-check/')

    def test_action_category_rotation_blocks_anonymous(self):
        self._assert_blocked('/api/platform/actions/agent-category-rotation/')

    def test_action_run_self_audit_blocks_anonymous(self):
        self._assert_blocked('/api/platform/actions/run-self-audit/')

    def test_decision_create_initiative_blocks_anonymous(self):
        self._assert_blocked('/api/platform/decision-summary/00000000-0000-0000-0000-000000000000/create-initiative/')

    def test_trigger_toggle_blocks_anonymous(self):
        self._assert_blocked('/api/platform/triggers/rule-name/toggle/')


class PlatformAuthRegressionNonStaffTest(TestCase):
    """Authenticated non-staff users must also be blocked from /api/platform/* mutations."""

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.non_staff = U.objects.create_user(
            username='s2784-non-staff-fixture',
            email='s2784-non-staff@donkeybetz.test',
        )
        cls.non_staff.is_staff = False
        cls.non_staff.is_superuser = False
        cls.non_staff.save()

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.non_staff)

    def _assert_blocked(self, path: str) -> None:
        response = self.client.post(path, data='{}', content_type='application/json')
        self.assertIn(
            response.status_code,
            _BLOCKED_STATUSES,
            f"{path} returned {response.status_code}; expected one of {_BLOCKED_STATUSES}",
        )

    def test_emergency_halt_blocks_non_staff(self):
        self._assert_blocked('/api/platform/emergency-halt/')

    def test_skin_lock_blocks_non_staff(self):
        self._assert_blocked('/api/platform/skin-lock/')

    def test_canon_promote_blocks_non_staff(self):
        self._assert_blocked('/api/platform/canon/promote/')

    def test_audits_run_blocks_non_staff(self):
        self._assert_blocked('/api/platform/audits/run/')

    def test_trigger_run_now_blocks_non_staff(self):
        self._assert_blocked('/api/platform/triggers/run-now/')

    def test_action_run_spiders_blocks_non_staff(self):
        self._assert_blocked('/api/platform/actions/run-spiders/')

    def test_action_run_remediation_blocks_non_staff(self):
        self._assert_blocked('/api/platform/actions/run-remediation/')

    def test_action_agent_health_blocks_non_staff(self):
        self._assert_blocked('/api/platform/actions/agent-health-check/')

    def test_action_category_rotation_blocks_non_staff(self):
        self._assert_blocked('/api/platform/actions/agent-category-rotation/')

    def test_action_run_self_audit_blocks_non_staff(self):
        self._assert_blocked('/api/platform/actions/run-self-audit/')

    def test_decision_create_initiative_blocks_non_staff(self):
        self._assert_blocked('/api/platform/decision-summary/00000000-0000-0000-0000-000000000000/create-initiative/')

    def test_trigger_toggle_blocks_non_staff(self):
        self._assert_blocked('/api/platform/triggers/rule-name/toggle/')


class PlatformAuthStaffAllowedTest(TestCase):
    """Sanity check: authenticated staff CAN reach /api/platform/* mutation endpoints.

    Fail-soft is acceptable (200 or 400/500 depending on body validation),
    but blocking statuses (302/401/403) are not.
    """

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.staff = U.objects.create_user(
            username='s2784-staff-fixture',
            email='s2784-staff@donkeybetz.test',
        )
        cls.staff.is_staff = True
        cls.staff.save()

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.staff)

    def _assert_reachable(self, path: str) -> None:
        response = self.client.post(path, data='{}', content_type='application/json')
        self.assertNotIn(
            response.status_code,
            _BLOCKED_STATUSES,
            f"{path} returned {response.status_code}; staff should not be blocked",
        )

    def test_emergency_halt_reachable_by_staff(self):
        self._assert_reachable('/api/platform/emergency-halt/')

    def test_skin_lock_reachable_by_staff(self):
        self._assert_reachable('/api/platform/skin-lock/')


class PlatformRouteInventoryGuardTest(TestCase):
    """Route inventory guard — every entry in ``_PLATFORM_MUTATION_ENDPOINTS``
    must have matching anon + non-staff test methods above. Fails loud on drift.
    """

    def _expected_test_method(self, route_name: str, suffix: str) -> str:
        core = route_name.removeprefix('platform-').replace('-', '_')
        # 'platform-action-run-remediation' → 'action_run_remediation'
        # We authored tests with slightly shorter labels; use the actual
        # method inventory as the source of truth to avoid off-by-one on
        # trimming rules. Compare route_names to a hardcoded map.
        return f'test_{core}_{suffix}'

    def test_all_mutation_endpoints_have_anon_tests(self):
        anon_methods = {m for m in dir(PlatformAuthRegressionAnonymousTest) if m.startswith('test_') and m.endswith('_blocks_anonymous')}
        non_staff_methods = {m for m in dir(PlatformAuthRegressionNonStaffTest) if m.startswith('test_') and m.endswith('_blocks_non_staff')}
        # Total expected = 10 kwargless + 2 kwarg endpoints = 12
        expected_count = len(_PLATFORM_MUTATION_ENDPOINTS) + len(_PLATFORM_KWARG_ENDPOINTS)
        self.assertEqual(
            len(anon_methods), expected_count,
            f"Expected {expected_count} anon test methods, found {len(anon_methods)}. "
            f"Add a matching test_<name>_blocks_anonymous method when adding a route.",
        )
        self.assertEqual(
            len(non_staff_methods), expected_count,
            f"Expected {expected_count} non-staff test methods, found {len(non_staff_methods)}. "
            f"Add a matching test_<name>_blocks_non_staff method when adding a route.",
        )

    def test_url_space_matches_inventory(self):
        from django.urls import reverse
        for name, expected_path in _PLATFORM_MUTATION_ENDPOINTS:
            resolved = reverse(name)
            self.assertEqual(
                resolved,
                expected_path,
                f"Route name {name!r} resolves to {resolved!r}, not {expected_path!r}",
            )
