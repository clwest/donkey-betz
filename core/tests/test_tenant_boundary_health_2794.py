"""S2794 — Tenant Boundary Health contract tests.

Locks the shape + posture of the RUR-C1 tenant boundary health surface
across:

  * Runner service (``core.services.cross_tenant_regression_service``) —
    JUnit XML parsing + provenance detection + coverage/gaps constants.
  * Model (``core.models.TenantBoundaryHealthReport``) — overall_status
    advisory property.
  * REST endpoint (``/api/governance/tenant-boundary-health/``) —
    staff-gated, advisory envelope, F1 no-toggle guard, F2 coverage
    metadata + known gaps present, F3 provenance fields present in
    the latest_report block.

Contracts locked (12 across 3 classes):

  Runner service:
    1. JUnit XML with 3 passing tests parses to correct counts.
    2. JUnit XML with failures + errors + skipped parses correctly.
    3. Missing XML file returns zero-count shape without raising.
    4. COVERAGE_METADATA values start with covered/partial/not_yet_covered.
    5. KNOWN_GAPS is non-empty.
    6. CROSS_TENANT_TEST_PATHS non-empty and all under tests/security/.

  Model:
    7. overall_status = 'green' when no failures/errors.
    8. overall_status = 'red' when any failure or error.
    9. overall_status = 'unknown' when total_tests == 0.

  REST endpoint:
   10. Anonymous requests are denied (staff-only).
   11. Envelope carries F1 advisory + is_gate=False + policy.
   12. F2 coverage_metadata + known_gaps present in response.

Ratified: S2794 T1 Rigby joint SIGN — SIGN-with-edits; 3 folds
(F1 same_pr_mitigatable, F2 same_pr_mitigatable, F3 same_pr_actionable)
persisted BEFORE Chris D-verdict per PLAYBOOK-6.10.8. Chris D-verdict:
"Got with i." (Option i single PR full stack.)
"""
from __future__ import annotations

import os
import tempfile

from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class RunnerServiceTests(SimpleTestCase):
    """Contracts 1-6 — runner service shape + JUnit XML parsing."""

    def _write_junit(self, xml_body: str) -> str:
        with tempfile.NamedTemporaryFile(
            prefix="tbr_test_junit_",
            suffix=".xml",
            delete=False,
            mode="w",
        ) as tf:
            tf.write(xml_body)
            return tf.name

    def test_junit_all_pass_parses_correctly(self):
        from core.services.cross_tenant_regression_service import _parse_junit_xml

        xml_path = self._write_junit(
            '<?xml version="1.0" encoding="utf-8"?>'
            '<testsuites>'
            '  <testsuite tests="3" failures="0" errors="0" skipped="0">'
            '    <testcase classname="tests.security.test_a" name="test_x" time="0.1" />'
            '    <testcase classname="tests.security.test_a" name="test_y" time="0.1" />'
            '    <testcase classname="tests.security.test_b" name="test_z" time="0.1" />'
            '  </testsuite>'
            '</testsuites>'
        )
        try:
            summary = _parse_junit_xml(xml_path)
        finally:
            os.unlink(xml_path)
        self.assertEqual(summary["total_tests"], 3)
        self.assertEqual(summary["passed"], 3)
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["errored"], 0)
        self.assertEqual(summary["failing_test_ids"], [])

    def test_junit_mixed_outcomes_parses_correctly(self):
        from core.services.cross_tenant_regression_service import _parse_junit_xml

        xml_path = self._write_junit(
            '<?xml version="1.0" encoding="utf-8"?>'
            '<testsuites>'
            '  <testsuite tests="4" failures="1" errors="1" skipped="1">'
            '    <testcase classname="tests.security.test_a" name="passing_test" time="0.1" />'
            '    <testcase classname="tests.security.test_a" name="failing_test" time="0.1">'
            '      <failure message="expected 1 got 2" type="AssertionError"/>'
            '    </testcase>'
            '    <testcase classname="tests.security.test_b" name="erroring_test" time="0.1">'
            '      <error message="boom" type="RuntimeError"/>'
            '    </testcase>'
            '    <testcase classname="tests.security.test_b" name="skipped_test" time="0.0">'
            '      <skipped/>'
            '    </testcase>'
            '  </testsuite>'
            '</testsuites>'
        )
        try:
            summary = _parse_junit_xml(xml_path)
        finally:
            os.unlink(xml_path)
        self.assertEqual(summary["total_tests"], 4)
        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["errored"], 1)
        self.assertEqual(summary["skipped"], 1)
        # Both failure + error contribute to failing_test_ids
        self.assertEqual(len(summary["failing_test_ids"]), 2)
        for nodeid in summary["failing_test_ids"]:
            self.assertIn("::", nodeid)  # module::test format

    def test_missing_junit_returns_zero_shape(self):
        from core.services.cross_tenant_regression_service import _parse_junit_xml

        summary = _parse_junit_xml("/nonexistent/path/junit.xml")
        self.assertEqual(summary["total_tests"], 0)
        self.assertEqual(summary["failing_test_ids"], [])

    def test_coverage_metadata_values_use_recognized_status_heads(self):
        from core.services.cross_tenant_regression_service import COVERAGE_METADATA

        for surface, status in COVERAGE_METADATA.items():
            head = status.split(" ", 1)[0]
            self.assertIn(
                head, {"covered", "partial", "not_yet_covered"},
                f"coverage status for {surface!r} must start with covered/"
                f"partial/not_yet_covered; got {status!r}",
            )

    def test_known_gaps_populated(self):
        """F2 mitigation — a green suite must ship with an honest gap list."""
        from core.services.cross_tenant_regression_service import KNOWN_GAPS

        self.assertIsInstance(KNOWN_GAPS, list)
        self.assertGreater(len(KNOWN_GAPS), 0)

    def test_test_paths_all_under_tests_security(self):
        from core.services.cross_tenant_regression_service import (
            CROSS_TENANT_TEST_PATHS,
        )

        self.assertGreater(len(CROSS_TENANT_TEST_PATHS), 0)
        for p in CROSS_TENANT_TEST_PATHS:
            self.assertTrue(
                p.startswith("tests/security/"),
                f"path {p!r} outside tests/security/",
            )


class ModelAdvisoryStatusTests(SimpleTestCase):
    """Contracts 7-9 — overall_status advisory property (S2794 F1)."""

    def test_status_green_when_no_failures_or_errors(self):
        from core.models import TenantBoundaryHealthReport

        row = TenantBoundaryHealthReport(
            env='local', git_sha='deadbeef', runner_identity='test',
            elapsed_secs=1.0, total_tests=10, passed=10, failed=0, errored=0,
            skipped=0, failing_test_ids=[], coverage_metadata={},
            summary_json={},
        )
        self.assertEqual(row.overall_status, 'green')

    def test_status_red_when_any_failure(self):
        from core.models import TenantBoundaryHealthReport

        row = TenantBoundaryHealthReport(
            env='local', git_sha='deadbeef', runner_identity='test',
            elapsed_secs=1.0, total_tests=10, passed=9, failed=1, errored=0,
            skipped=0, failing_test_ids=[], coverage_metadata={},
            summary_json={},
        )
        self.assertEqual(row.overall_status, 'red')

    def test_status_red_when_any_error(self):
        from core.models import TenantBoundaryHealthReport

        row = TenantBoundaryHealthReport(
            env='local', git_sha='deadbeef', runner_identity='test',
            elapsed_secs=1.0, total_tests=10, passed=9, failed=0, errored=1,
            skipped=0, failing_test_ids=[], coverage_metadata={},
            summary_json={},
        )
        self.assertEqual(row.overall_status, 'red')

    def test_status_unknown_when_no_tests(self):
        from core.models import TenantBoundaryHealthReport

        row = TenantBoundaryHealthReport(
            env='local', git_sha='deadbeef', runner_identity='test',
            elapsed_secs=0.0, total_tests=0, passed=0, failed=0, errored=0,
            skipped=0, failing_test_ids=[], coverage_metadata={},
            summary_json={},
        )
        self.assertEqual(row.overall_status, 'unknown')


class TenantBoundaryHealthEndpointTests(TestCase):
    """Contracts 10-12 — REST envelope + auth + F1/F2/F3 mitigations."""

    def setUp(self):
        self.url = '/api/governance/tenant-boundary-health/'
        User = get_user_model()
        self.staff = User.objects.create_user(
            username='s2794-staff', email='staff@example.com', password='pw'
        )
        self.staff.is_staff = True
        self.staff.save()

    def test_anonymous_denied(self):
        """Contract 10: unauthenticated requests are rejected."""
        client = Client()
        response = client.get(self.url)
        # login_required either redirects (302 to /login/) or DRF-401s;
        # in either case, un-authenticated MUST NOT see the payload.
        self.assertIn(response.status_code, (302, 401, 403))

    def test_non_staff_denied(self):
        """Contract 10 (extended): non-staff logged-in users are rejected."""
        User = get_user_model()
        non_staff = User.objects.create_user(
            username='s2794-non-staff', email='ns@example.com', password='pw'
        )
        client = Client()
        client.force_login(non_staff)
        response = client.get(self.url)
        # user_passes_test denies with 302→login by default
        self.assertIn(response.status_code, (302, 401, 403))

    def test_staff_gets_envelope_with_f1_advisory_and_no_gate(self):
        """Contract 11: F1 mitigation — advisory + is_gate=False + policy."""
        client = Client()
        client.force_login(self.staff)
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        # F1: advisory language + explicit is_gate=False + launch approval.
        self.assertIn('advisory', body)
        self.assertIn('not a launch gate', body['advisory'].lower())
        self.assertIn('is_gate', body)
        self.assertFalse(body['is_gate'])
        self.assertIn('policy', body)
        self.assertIn('launch_approval', body['policy'])
        self.assertIn('Manual', body['policy']['launch_approval'])

    def test_staff_gets_coverage_metadata_and_known_gaps(self):
        """Contract 12: F2 mitigation — coverage_metadata + known_gaps present.

        A green suite with silent gaps is a false-confidence signal.
        The envelope MUST surface both.
        """
        client = Client()
        client.force_login(self.staff)
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn('coverage_metadata', body)
        self.assertIsInstance(body['coverage_metadata'], dict)
        self.assertGreater(len(body['coverage_metadata']), 0)
        self.assertIn('known_gaps', body)
        self.assertIsInstance(body['known_gaps'], list)
        self.assertGreater(len(body['known_gaps']), 0)

    def test_latest_report_carries_f3_provenance_when_present(self):
        """Contract 12 (extended): F3 mitigation — env / git_sha / runner /
        timestamp / elapsed present in latest_report when the row exists.
        """
        from core.models import TenantBoundaryHealthReport

        TenantBoundaryHealthReport.objects.create(
            env='local',
            git_sha='deadbeefcafe1234',
            runner_identity='s2794-test',
            elapsed_secs=1.5,
            total_tests=3,
            passed=3,
            failed=0,
            errored=0,
            skipped=0,
            failing_test_ids=[],
            coverage_metadata={'sync_http': 'covered'},
            summary_json={'shape': 'test'},
        )
        client = Client()
        client.force_login(self.staff)
        response = client.get(self.url)
        body = response.json()
        latest = body.get('latest_report')
        self.assertIsNotNone(latest, 'latest_report should be present after row create')
        # F3: provenance quartet
        self.assertEqual(latest['env'], 'local')
        self.assertEqual(latest['git_sha'], 'deadbeefcafe1234')
        self.assertEqual(latest['runner_identity'], 's2794-test')
        self.assertIn('created_at', latest)
        self.assertIn('elapsed_secs', latest)
        # advisory status pass-through
        self.assertEqual(latest['overall_status'], 'green')

    def test_unknown_query_param_rejected(self):
        """Allowlist discipline (mirrors zoom-out-ledger)."""
        client = Client()
        client.force_login(self.staff)
        response = client.get(self.url + '?bogus_param=1')
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertEqual(body.get('code'), 'unknown_query_params')
