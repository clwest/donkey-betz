"""S2785 Fold 4 decision-approve audit — /api/human/* + /api/boardroom/* auth regression.

Extends the auth-regression contract established at S2772 N16
(Rigby-ratified) + S2780 (governance) + S2784 (platform) to two more
surfaces reachable from GovernanceTab's DecisionDetailModal:

* ``core/views_human_interface.py`` — 15 class-based views under
  ``/api/human/*`` gated with ``_human_staff_only`` in the method
  decorator stack.
* ``core/views_agent_learning.py`` — 4 boardroom decision mutation
  endpoints under ``/api/boardroom/decisions/*`` gated via inline
  ``_require_boardroom_staff`` helper (preserves the S887 Token auth
  codepath — cannot use decorator-based ``@login_required`` because
  Token auth must resolve first).

Contract per S2772 N16: every governance/decision endpoint MUST be both
authenticated AND staff-only. Anon → blocked. Authenticated non-staff →
blocked. Authenticated staff → reachable.

Adding a new /api/human/* class-based view or /api/boardroom/decisions/*
mutation endpoint? Add it to the inventory below with matching test
methods. The route-inventory guard at the bottom fails loud on drift.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


_BLOCKED_STATUSES = {302, 401, 403}

# S2785 route inventory — 15 human interface CBVs (auth applies to all
# HTTP methods via method_decorator on dispatch).
_HUMAN_ENDPOINTS: list[tuple[str, str, str]] = [
    # (route_name, path, primary_method)
    ('human-attention', '/api/human/attention/', 'GET'),
    ('human-attention-stats', '/api/human/attention/stats/', 'GET'),
    ('human-attention-bulk-decide', '/api/human/attention/bulk-decide/', 'POST'),
    ('human-control', '/api/human/control/', 'GET'),
    ('human-control-pause', '/api/human/control/pause/', 'POST'),
    ('human-control-resume', '/api/human/control/resume/', 'POST'),
    ('human-control-quiet', '/api/human/control/quiet/', 'POST'),
    ('human-control-review', '/api/human/control/review/', 'POST'),
    ('human-control-threshold', '/api/human/control/threshold/', 'POST'),
    ('human-preferences', '/api/human/preferences/', 'GET'),
]
# UUID-kwarg endpoints — tested via direct-path assertions with sentinel UUID.
_HUMAN_KWARG_ENDPOINTS: list[tuple[str, str, str]] = [
    ('human-attention-detail', '/api/human/attention/00000000-0000-0000-0000-000000000000/', 'GET'),
    ('human-attention-decide', '/api/human/attention/00000000-0000-0000-0000-000000000000/decide/', 'POST'),
    ('human-attention-defer', '/api/human/attention/00000000-0000-0000-0000-000000000000/defer/', 'POST'),
    ('human-attention-verify', '/api/human/attention/00000000-0000-0000-0000-000000000000/verify/', 'POST'),
    ('human-attention-execute', '/api/human/attention/00000000-0000-0000-0000-000000000000/execute/', 'POST'),
]

# 4 boardroom decision-mutation endpoints gated via _require_boardroom_staff.
_BOARDROOM_ENDPOINTS: list[tuple[str, str]] = [
    ('bulk-promote-decisions', '/api/boardroom/decisions/bulk-promote/'),
    ('bulk-reject-decisions', '/api/boardroom/decisions/bulk-reject/'),
]
_BOARDROOM_KWARG_ENDPOINTS: list[tuple[str, str]] = [
    ('promote-decision', '/api/boardroom/decisions/00000000-0000-0000-0000-000000000000/promote/'),
    ('reject-decision', '/api/boardroom/decisions/00000000-0000-0000-0000-000000000000/reject/'),
]


def _request(client: Client, path: str, method: str):
    """Dispatch a request using the endpoint's primary HTTP method."""
    if method == 'POST':
        return client.post(path, data='{}', content_type='application/json')
    return client.get(path)


# ── Anonymous tests ─────────────────────────────────────────────────────

class HumanAuthRegressionAnonymousTest(TestCase):
    """Anonymous requests to /api/human/* must be blocked."""

    def setUp(self):
        self.client = Client()

    def _assert_blocked(self, path: str, method: str) -> None:
        response = _request(self.client, path, method)
        self.assertIn(
            response.status_code,
            _BLOCKED_STATUSES,
            f"{method} {path} returned {response.status_code}; expected one of {_BLOCKED_STATUSES}",
        )

    def test_attention_stream_blocks_anonymous(self):
        self._assert_blocked('/api/human/attention/', 'GET')

    def test_attention_stats_blocks_anonymous(self):
        self._assert_blocked('/api/human/attention/stats/', 'GET')

    def test_attention_bulk_decide_blocks_anonymous(self):
        self._assert_blocked('/api/human/attention/bulk-decide/', 'POST')

    def test_attention_detail_blocks_anonymous(self):
        self._assert_blocked('/api/human/attention/00000000-0000-0000-0000-000000000000/', 'GET')

    def test_attention_decide_blocks_anonymous(self):
        self._assert_blocked('/api/human/attention/00000000-0000-0000-0000-000000000000/decide/', 'POST')

    def test_attention_defer_blocks_anonymous(self):
        self._assert_blocked('/api/human/attention/00000000-0000-0000-0000-000000000000/defer/', 'POST')

    def test_attention_verify_blocks_anonymous(self):
        self._assert_blocked('/api/human/attention/00000000-0000-0000-0000-000000000000/verify/', 'POST')

    def test_attention_execute_blocks_anonymous(self):
        self._assert_blocked('/api/human/attention/00000000-0000-0000-0000-000000000000/execute/', 'POST')

    def test_control_blocks_anonymous(self):
        self._assert_blocked('/api/human/control/', 'GET')

    def test_control_pause_blocks_anonymous(self):
        self._assert_blocked('/api/human/control/pause/', 'POST')

    def test_control_resume_blocks_anonymous(self):
        self._assert_blocked('/api/human/control/resume/', 'POST')

    def test_control_quiet_blocks_anonymous(self):
        self._assert_blocked('/api/human/control/quiet/', 'POST')

    def test_control_review_blocks_anonymous(self):
        self._assert_blocked('/api/human/control/review/', 'POST')

    def test_control_threshold_blocks_anonymous(self):
        self._assert_blocked('/api/human/control/threshold/', 'POST')

    def test_preferences_blocks_anonymous(self):
        self._assert_blocked('/api/human/preferences/', 'GET')


class BoardroomAuthRegressionAnonymousTest(TestCase):
    """Anonymous POSTs to /api/boardroom/decisions/* mutations must be blocked."""

    def setUp(self):
        self.client = Client()

    def _assert_blocked(self, path: str) -> None:
        response = self.client.post(path, data='{}', content_type='application/json')
        self.assertIn(
            response.status_code,
            _BLOCKED_STATUSES,
            f"POST {path} returned {response.status_code}; expected one of {_BLOCKED_STATUSES}",
        )

    def test_promote_decision_blocks_anonymous(self):
        self._assert_blocked('/api/boardroom/decisions/00000000-0000-0000-0000-000000000000/promote/')

    def test_reject_decision_blocks_anonymous(self):
        self._assert_blocked('/api/boardroom/decisions/00000000-0000-0000-0000-000000000000/reject/')

    def test_bulk_promote_blocks_anonymous(self):
        self._assert_blocked('/api/boardroom/decisions/bulk-promote/')

    def test_bulk_reject_blocks_anonymous(self):
        self._assert_blocked('/api/boardroom/decisions/bulk-reject/')


# ── Authenticated non-staff tests ───────────────────────────────────────

class HumanAuthRegressionNonStaffTest(TestCase):
    """Authenticated non-staff users must be blocked from /api/human/*."""

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.non_staff = U.objects.create_user(
            username='s2785-non-staff-fixture',
            email='s2785-non-staff@donkeybetz.test',
        )
        cls.non_staff.is_staff = False
        cls.non_staff.is_superuser = False
        cls.non_staff.save()

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.non_staff)

    def _assert_blocked(self, path: str, method: str) -> None:
        response = _request(self.client, path, method)
        self.assertIn(
            response.status_code,
            _BLOCKED_STATUSES,
            f"{method} {path} returned {response.status_code}; expected one of {_BLOCKED_STATUSES}",
        )

    def test_attention_stream_blocks_non_staff(self):
        self._assert_blocked('/api/human/attention/', 'GET')

    def test_attention_stats_blocks_non_staff(self):
        self._assert_blocked('/api/human/attention/stats/', 'GET')

    def test_attention_bulk_decide_blocks_non_staff(self):
        self._assert_blocked('/api/human/attention/bulk-decide/', 'POST')

    def test_attention_detail_blocks_non_staff(self):
        self._assert_blocked('/api/human/attention/00000000-0000-0000-0000-000000000000/', 'GET')

    def test_attention_decide_blocks_non_staff(self):
        self._assert_blocked('/api/human/attention/00000000-0000-0000-0000-000000000000/decide/', 'POST')

    def test_attention_defer_blocks_non_staff(self):
        self._assert_blocked('/api/human/attention/00000000-0000-0000-0000-000000000000/defer/', 'POST')

    def test_attention_verify_blocks_non_staff(self):
        self._assert_blocked('/api/human/attention/00000000-0000-0000-0000-000000000000/verify/', 'POST')

    def test_attention_execute_blocks_non_staff(self):
        self._assert_blocked('/api/human/attention/00000000-0000-0000-0000-000000000000/execute/', 'POST')

    def test_control_blocks_non_staff(self):
        self._assert_blocked('/api/human/control/', 'GET')

    def test_control_pause_blocks_non_staff(self):
        self._assert_blocked('/api/human/control/pause/', 'POST')

    def test_control_resume_blocks_non_staff(self):
        self._assert_blocked('/api/human/control/resume/', 'POST')

    def test_control_quiet_blocks_non_staff(self):
        self._assert_blocked('/api/human/control/quiet/', 'POST')

    def test_control_review_blocks_non_staff(self):
        self._assert_blocked('/api/human/control/review/', 'POST')

    def test_control_threshold_blocks_non_staff(self):
        self._assert_blocked('/api/human/control/threshold/', 'POST')

    def test_preferences_blocks_non_staff(self):
        self._assert_blocked('/api/human/preferences/', 'GET')


class BoardroomAuthRegressionNonStaffTest(TestCase):
    """Authenticated non-staff users must be blocked from boardroom mutations."""

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.non_staff = U.objects.create_user(
            username='s2785-boardroom-non-staff-fixture',
            email='s2785-boardroom-non-staff@donkeybetz.test',
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
            f"POST {path} returned {response.status_code}; expected one of {_BLOCKED_STATUSES}",
        )

    def test_promote_decision_blocks_non_staff(self):
        self._assert_blocked('/api/boardroom/decisions/00000000-0000-0000-0000-000000000000/promote/')

    def test_reject_decision_blocks_non_staff(self):
        self._assert_blocked('/api/boardroom/decisions/00000000-0000-0000-0000-000000000000/reject/')

    def test_bulk_promote_blocks_non_staff(self):
        self._assert_blocked('/api/boardroom/decisions/bulk-promote/')

    def test_bulk_reject_blocks_non_staff(self):
        self._assert_blocked('/api/boardroom/decisions/bulk-reject/')


# ── Authenticated staff (sanity: reachable) ─────────────────────────────

class DecisionApproveStaffAllowedTest(TestCase):
    """Sanity check: authenticated staff CAN reach the newly-gated endpoints.

    Fail-soft is acceptable (200 / 400 / 500 depending on body validation);
    blocking statuses (302 / 401 / 403) are not.
    """

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.staff = U.objects.create_user(
            username='s2785-staff-fixture',
            email='s2785-staff@donkeybetz.test',
        )
        cls.staff.is_staff = True
        cls.staff.save()

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.staff)

    def _assert_reachable(self, path: str, method: str) -> None:
        response = _request(self.client, path, method)
        self.assertNotIn(
            response.status_code,
            _BLOCKED_STATUSES,
            f"{method} {path} returned {response.status_code}; staff should not be blocked",
        )

    def test_attention_stream_reachable_by_staff(self):
        self._assert_reachable('/api/human/attention/', 'GET')

    def test_attention_stats_reachable_by_staff(self):
        self._assert_reachable('/api/human/attention/stats/', 'GET')

    def test_control_reachable_by_staff(self):
        self._assert_reachable('/api/human/control/', 'GET')

    def test_bulk_promote_reachable_by_staff(self):
        # Empty body → 400, not 401/403
        self._assert_reachable('/api/boardroom/decisions/bulk-promote/', 'POST')


# ── Inventory guard ─────────────────────────────────────────────────────

class DecisionApproveRouteInventoryGuardTest(TestCase):
    """Fails loud if the inventory drifts from the test methods above."""

    def test_all_human_endpoints_have_anon_tests(self):
        expected = len(_HUMAN_ENDPOINTS) + len(_HUMAN_KWARG_ENDPOINTS)  # 10 + 5 = 15
        anon_methods = {m for m in dir(HumanAuthRegressionAnonymousTest) if m.startswith('test_') and m.endswith('_blocks_anonymous')}
        non_staff_methods = {m for m in dir(HumanAuthRegressionNonStaffTest) if m.startswith('test_') and m.endswith('_blocks_non_staff')}
        self.assertEqual(
            len(anon_methods), expected,
            f"Expected {expected} /api/human/* anon test methods, found {len(anon_methods)}. "
            f"Add a matching test_<name>_blocks_anonymous method when adding a route.",
        )
        self.assertEqual(
            len(non_staff_methods), expected,
            f"Expected {expected} /api/human/* non-staff test methods, found {len(non_staff_methods)}.",
        )

    def test_all_boardroom_endpoints_have_anon_tests(self):
        expected = len(_BOARDROOM_ENDPOINTS) + len(_BOARDROOM_KWARG_ENDPOINTS)  # 2 + 2 = 4
        anon_methods = {m for m in dir(BoardroomAuthRegressionAnonymousTest) if m.startswith('test_') and m.endswith('_blocks_anonymous')}
        non_staff_methods = {m for m in dir(BoardroomAuthRegressionNonStaffTest) if m.startswith('test_') and m.endswith('_blocks_non_staff')}
        self.assertEqual(
            len(anon_methods), expected,
            f"Expected {expected} /api/boardroom/* anon test methods, found {len(anon_methods)}.",
        )
        self.assertEqual(
            len(non_staff_methods), expected,
            f"Expected {expected} /api/boardroom/* non-staff test methods, found {len(non_staff_methods)}.",
        )

    def test_url_space_matches_inventory(self):
        from django.urls import reverse
        for name, expected_path, _method in _HUMAN_ENDPOINTS:
            self.assertEqual(reverse(name), expected_path, f"{name!r}")
        for name, expected_path in _BOARDROOM_ENDPOINTS:
            self.assertEqual(reverse(name), expected_path, f"{name!r}")
