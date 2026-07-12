"""S2772 N16 — Ops-endpoint auth-regression tests.

Rigby S2771 meta-critique #4: /api/ops/* endpoints accumulate power over
time; the category tends to drift into "debug everything" if unattended.
This suite locks the contract that every ops endpoint refuses:

  1. Anonymous access (no login)
  2. Authenticated non-staff access

Anon fails via @login_required (redirect 302 to LOGIN_URL). Authenticated
non-staff fails via @user_passes_test (redirect 302 to LOGIN_URL under
Django default). Both are asserted as "status in {302, 401, 403}" — the
security property is "response is not the payload," not any specific code.

A route-inventory guard test (test_all_ops_endpoints_have_auth_tests)
enumerates the six URL names this module knows about and fails if the
`/api/ops/*` URL space diverges from that inventory — meaning a new
endpoint was added without adding matching tests to this file.

Ratified: Chris (S2772), Rigby joint SIGN (Q1 MODIFY accepted → tighter
assertion set; Q2 PASS → explicit per-endpoint; Q3 open-ended zoom-out
produced 7 concerns, 2 addressed same-PR).
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import get_resolver

# S2772 N16 (Rigby Q1 MODIFY): tighter assertion set. Any of {302, 401,
# 403} counts as "blocked" — 500/404 do NOT (a broken endpoint returning
# 500 is not evidence of auth working, and 404 might mean the URL got
# renamed and the test is stale).
_BLOCKED_STATUSES = {302, 401, 403}

# S2772 N16 route inventory: every /api/ops/* URL name we know about
# MUST have both a `test_<name>_blocks_anonymous` and a
# `test_<name>_blocks_non_staff` method in this file. The inventory
# guard test enforces this — if you add a new /api/ops/ endpoint,
# add tests here in the same PR or the guard test will fail loudly.
_OPS_ENDPOINTS = [
    ('ops-slo-status', '/api/ops/slo-status/'),
    ('ops-failure-signatures', '/api/ops/failure-signatures/'),
    ('ops-blocked-agents', '/api/ops/blocked-agents/'),
    ('ops-health-summary', '/api/ops/health-summary/'),
    ('ops-close-ceremony-ledger', '/api/ops/close-ceremony-ledger/'),
    ('ops-recent-recycles', '/api/ops/recent-recycles/'),
]


class OpsAuthRegressionAnonymousTest(TestCase):
    """Anonymous (unauthenticated) requests to /api/ops/* must be blocked."""

    def setUp(self):
        self.client = Client()

    def test_slo_status_blocks_anonymous(self):
        response = self.client.get('/api/ops/slo-status/')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)

    def test_failure_signatures_blocks_anonymous(self):
        response = self.client.get('/api/ops/failure-signatures/')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)

    def test_blocked_agents_blocks_anonymous(self):
        response = self.client.get('/api/ops/blocked-agents/')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)

    def test_health_summary_blocks_anonymous(self):
        response = self.client.get('/api/ops/health-summary/')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)

    def test_close_ceremony_ledger_blocks_anonymous(self):
        response = self.client.get('/api/ops/close-ceremony-ledger/')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)

    def test_recent_recycles_blocks_anonymous(self):
        response = self.client.get('/api/ops/recent-recycles/')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)


class OpsAuthRegressionNonStaffTest(TestCase):
    """Authenticated non-staff users must also be blocked from /api/ops/*."""

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.non_staff = U.objects.create_user(
            username='n16-non-staff-fixture',
            email='n16-non-staff@donkeybetz.test',
            # No password argument — force_login below bypasses password auth,
            # and passing a literal string trips the pre-commit secret scanner.
        )
        # Explicit — the fixture user has no elevated flags.
        cls.non_staff.is_staff = False
        cls.non_staff.is_superuser = False
        cls.non_staff.save()

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.non_staff)

    def test_slo_status_blocks_non_staff(self):
        response = self.client.get('/api/ops/slo-status/')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)

    def test_failure_signatures_blocks_non_staff(self):
        response = self.client.get('/api/ops/failure-signatures/')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)

    def test_blocked_agents_blocks_non_staff(self):
        response = self.client.get('/api/ops/blocked-agents/')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)

    def test_health_summary_blocks_non_staff(self):
        response = self.client.get('/api/ops/health-summary/')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)

    def test_close_ceremony_ledger_blocks_non_staff(self):
        response = self.client.get('/api/ops/close-ceremony-ledger/')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)

    def test_recent_recycles_blocks_non_staff(self):
        response = self.client.get('/api/ops/recent-recycles/')
        self.assertIn(response.status_code, _BLOCKED_STATUSES)


class OpsAuthStaffAllowedTest(TestCase):
    """Sanity check: authenticated staff users CAN reach /api/ops/*.

    Without this test, an over-eager staff gate that returned 403 for
    everyone would still pass the two suites above. This one proves the
    happy path stays open.
    """

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.staff = U.objects.create_user(
            username='n16-staff-fixture',
            email='n16-staff@donkeybetz.test',
            # No password argument — force_login below bypasses password auth,
            # and passing a literal string trips the pre-commit secret scanner.
        )
        cls.staff.is_staff = True
        cls.staff.save()

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.staff)

    def test_close_ceremony_ledger_reachable_by_staff(self):
        # One happy-path check is enough — every endpoint uses the same
        # decorator chain, so if one passes for staff, all pass.
        response = self.client.get('/api/ops/close-ceremony-ledger/?limit=1')
        # 200 (data) or 500 (upstream fail-soft) both prove the auth gate
        # didn't block; we don't want to couple this test to data-layer
        # availability. What matters is "not in blocked set."
        self.assertNotIn(response.status_code, _BLOCKED_STATUSES)


class OpsRouteInventoryGuardTest(TestCase):
    """S2772 N16 (Rigby Q3 #7): inventory guard.

    If someone adds a new /api/ops/* endpoint but forgets to add auth
    tests here, this test fails and points at the missing methods. The
    friction is deliberate — auth-regression coverage should not
    silently rot as the surface grows.
    """

    def test_all_ops_endpoints_have_auth_tests(self):
        # Every URL name in _OPS_ENDPOINTS must have both anon + non_staff
        # tests. Derive the expected method names and check the two
        # TestCase classes above define them.
        expected_anon = {
            f'test_{name.removeprefix("ops-").replace("-", "_")}_blocks_anonymous'
            for name, _path in _OPS_ENDPOINTS
        }
        expected_non_staff = {
            f'test_{name.removeprefix("ops-").replace("-", "_")}_blocks_non_staff'
            for name, _path in _OPS_ENDPOINTS
        }
        anon_actual = {
            attr for attr in dir(OpsAuthRegressionAnonymousTest)
            if attr.startswith('test_') and attr.endswith('_blocks_anonymous')
        }
        non_staff_actual = {
            attr for attr in dir(OpsAuthRegressionNonStaffTest)
            if attr.startswith('test_') and attr.endswith('_blocks_non_staff')
        }
        missing_anon = expected_anon - anon_actual
        missing_non_staff = expected_non_staff - non_staff_actual
        self.assertFalse(
            missing_anon,
            f"Ops endpoint(s) missing anonymous auth test: {missing_anon}. "
            f"Add the method to OpsAuthRegressionAnonymousTest.",
        )
        self.assertFalse(
            missing_non_staff,
            f"Ops endpoint(s) missing non-staff auth test: {missing_non_staff}. "
            f"Add the method to OpsAuthRegressionNonStaffTest.",
        )

    def test_ops_url_space_matches_inventory(self):
        # Enumerate the resolved URL names starting with 'ops-' and
        # compare against the inventory. Any drift (added endpoint, or
        # a legitimate rename) surfaces here.
        resolver = get_resolver()
        resolved_ops_names = set()
        for pattern in _walk_url_patterns(resolver.url_patterns):
            name = getattr(pattern, 'name', None)
            if name and name.startswith('ops-'):
                resolved_ops_names.add(name)
        inventory_names = {n for n, _p in _OPS_ENDPOINTS}
        added_since_inventory = resolved_ops_names - inventory_names
        removed_since_inventory = inventory_names - resolved_ops_names
        self.assertFalse(
            added_since_inventory,
            f"New /api/ops/ URL(s) registered but not in _OPS_ENDPOINTS "
            f"inventory: {added_since_inventory}. Add tests + inventory "
            f"entry in the same PR.",
        )
        self.assertFalse(
            removed_since_inventory,
            f"Inventory lists endpoint(s) no longer in URL space: "
            f"{removed_since_inventory}. Clean up the inventory + tests.",
        )


def _walk_url_patterns(patterns):
    """Yield leaf URL patterns from a nested URL resolver tree."""
    for p in patterns:
        if hasattr(p, 'url_patterns'):
            yield from _walk_url_patterns(p.url_patterns)
        else:
            yield p
