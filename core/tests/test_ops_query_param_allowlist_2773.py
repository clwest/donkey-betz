"""S2773 N18v2 — Ops-endpoint query-param allowlist tests.

Rigby S2772 meta-critique #4 (forward-carry from S2771 zoom-out):
ad-hoc query params on ops endpoints risk becoming an unversioned
API contract surface + accidental data exposure vector. This suite
locks the mechanical enforcement introduced at S2773:

  1. Every ops endpoint declares an `_OPS_ALLOWED_PARAMS__<NAME>`
     frozenset constant at the module level.
  2. Every endpoint calls `_reject_unknown_query_params` at the top,
     returning 400 with a machine-stable `code` field when a query
     key is not in the allowlist.
  3. `_parse_date_param` now uses `datetime.date.fromisoformat` for
     real calendar validation (Rigby Q3 #4 correctness fix).

Ratified: Chris (S2773), Rigby joint SIGN (Q1 MODIFY → add `code` field;
Q2 MODIFY → new file, not extending auth-regression file; Q3 MODIFY on
date parse behavior change; Q3 open-ended zoom-out → 5 substantive
concerns, 3 shipped same-PR, 2 forward-carry).

The S2772 auth-regression file remains focused on its charter
(auth + route inventory). This file owns the query-param contract.
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from core.views_ops_console import _parse_date_param


class OpsQueryParamAllowlistAcceptTest(TestCase):
    """Every ops endpoint accepts its documented allowlisted params (200 or
    a non-blocked non-400 status — depends on data availability).

    We don't couple these tests to precise 200 responses because the
    close_ceremony_ledger reads real filesystem state and some endpoints
    return fail-soft {'error': ...} bodies with 200 anyway. What we
    assert is: allowlisted params never produce a 400 with our
    `unknown_query_params` code.
    """

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.staff = U.objects.create_user(
            username='n18-allow-fixture',
            email='n18-allow@donkeybetz.test',
        )
        cls.staff.is_staff = True
        cls.staff.save()

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.staff)

    def _assert_not_allowlist_400(self, path: str, description: str) -> None:
        response = self.client.get(path)
        if response.status_code == 400:
            body = response.json() if hasattr(response, 'json') else {}
            self.assertNotEqual(
                body.get('code'),
                'unknown_query_params',
                f'{description}: allowlisted request returned 400 unknown_query_params. '
                f'Body: {body}',
            )

    def test_slo_status_accepts_no_params(self):
        self._assert_not_allowlist_400(
            '/api/ops/slo-status/',
            'slo_status with no params',
        )

    def test_failure_signatures_accepts_documented_params(self):
        self._assert_not_allowlist_400(
            '/api/ops/failure-signatures/?window=24h&limit=10',
            'failure_signatures with window+limit',
        )

    def test_blocked_agents_accepts_no_params(self):
        self._assert_not_allowlist_400(
            '/api/ops/blocked-agents/',
            'blocked_agents with no params',
        )

    def test_health_summary_accepts_no_params(self):
        self._assert_not_allowlist_400(
            '/api/ops/health-summary/',
            'health_summary with no params',
        )

    def test_close_ceremony_ledger_accepts_full_param_set(self):
        self._assert_not_allowlist_400(
            '/api/ops/close-ceremony-ledger/?limit=5&session_min=2770&session_max=2775'
            '&envelope_only=true&date_from=2026-07-11&date_to=2026-07-12&text=N18',
            'close_ceremony_ledger with all 7 documented params',
        )

    def test_recent_recycles_accepts_limit(self):
        self._assert_not_allowlist_400(
            '/api/ops/recent-recycles/?limit=5',
            'recent_recycles with limit',
        )


class OpsQueryParamAllowlistRejectTest(TestCase):
    """Every ops endpoint rejects unknown query params with 400 +
    `code='unknown_query_params'` + machine-readable body."""

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.staff = U.objects.create_user(
            username='n18-reject-fixture',
            email='n18-reject@donkeybetz.test',
        )
        cls.staff.is_staff = True
        cls.staff.save()

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.staff)

    def _assert_rejects(self, path: str) -> dict:
        response = self.client.get(path)
        self.assertEqual(response.status_code, 400, f'expected 400 for {path}')
        body = response.json()
        self.assertEqual(body.get('code'), 'unknown_query_params')
        self.assertIn('unknown', body)
        self.assertIn('allowed', body)
        self.assertIn('error', body)
        return body

    def test_slo_status_rejects_unknown_param(self):
        body = self._assert_rejects('/api/ops/slo-status/?raw=1')
        self.assertIn('raw', body['unknown'])

    def test_failure_signatures_rejects_unknown_param(self):
        body = self._assert_rejects('/api/ops/failure-signatures/?window=24h&limit=10&raw=1')
        self.assertIn('raw', body['unknown'])
        # Documented params should NOT appear in unknown even when co-supplied.
        self.assertNotIn('window', body['unknown'])
        self.assertNotIn('limit', body['unknown'])

    def test_blocked_agents_rejects_unknown_param(self):
        body = self._assert_rejects('/api/ops/blocked-agents/?include_body=1')
        self.assertIn('include_body', body['unknown'])

    def test_health_summary_rejects_unknown_param(self):
        body = self._assert_rejects('/api/ops/health-summary/?debug=true')
        self.assertIn('debug', body['unknown'])

    def test_close_ceremony_ledger_rejects_unknown_param(self):
        body = self._assert_rejects('/api/ops/close-ceremony-ledger/?limit=5&raw=1')
        self.assertIn('raw', body['unknown'])
        self.assertNotIn('limit', body['unknown'])

    def test_recent_recycles_rejects_unknown_param(self):
        body = self._assert_rejects('/api/ops/recent-recycles/?limit=5&extra=1')
        self.assertIn('extra', body['unknown'])

    def test_multiple_unknown_params_all_reported(self):
        body = self._assert_rejects('/api/ops/close-ceremony-ledger/?raw=1&debug=true&include_body=1')
        self.assertEqual(set(body['unknown']), {'raw', 'debug', 'include_body'})

    def test_400_body_has_expected_shape(self):
        # Exact shape contract, minus values — pins the API surface for
        # any downstream tool (frontend, other tests) that keys off it.
        body = self._assert_rejects('/api/ops/slo-status/?nope=1')
        self.assertEqual(set(body.keys()) >= {'error', 'code', 'unknown', 'allowed'}, True)
        self.assertIsInstance(body['unknown'], list)
        self.assertIsInstance(body['allowed'], list)


class OpsAllowlistMetaTest(TestCase):
    """Meta-contract: every ops endpoint URL name must have a matching
    `_OPS_ALLOWED_PARAMS__<UPPER_NAME>` frozenset constant in
    `views_ops_console`. Prevents an endpoint from silently drifting
    back to the pre-S2773 "silently ignore unknown params" default.
    """

    def test_every_ops_endpoint_declares_allowlist_constant(self):
        # Same inventory as the S2772 auth-regression file, kept local
        # here so both files can evolve independently (Rigby Q2 MODIFY
        # rationale — charter separation).
        endpoint_url_names = [
            'ops-slo-status',
            'ops-failure-signatures',
            'ops-blocked-agents',
            'ops-health-summary',
            'ops-close-ceremony-ledger',
            'ops-recent-recycles',
        ]
        from core import views_ops_console
        module_attrs = set(dir(views_ops_console))
        missing = []
        for url_name in endpoint_url_names:
            # ops-close-ceremony-ledger -> _OPS_ALLOWED_PARAMS__CLOSE_CEREMONY_LEDGER
            suffix = url_name.removeprefix('ops-').replace('-', '_').upper()
            expected = f'_OPS_ALLOWED_PARAMS__{suffix}'
            if expected not in module_attrs:
                missing.append((url_name, expected))
            else:
                constant = getattr(views_ops_console, expected)
                self.assertIsInstance(
                    constant,
                    frozenset,
                    f'{expected} must be a frozenset (got {type(constant).__name__})',
                )
        self.assertFalse(
            missing,
            f'Ops endpoints missing allowlist constants: {missing}. '
            f'Declare the constant + call _reject_unknown_query_params in the view.',
        )


class DateParamValidationTest(TestCase):
    """Rigby Q3 #4 correctness fix: `_parse_date_param` now uses
    `datetime.date.fromisoformat` for real calendar validation.
    """

    def test_valid_date_passes_through(self):
        self.assertEqual(_parse_date_param('2026-07-12'), '2026-07-12')

    def test_invalid_calendar_month_rejected(self):
        # Previously accepted (digit-only check); now rejected.
        self.assertIsNone(_parse_date_param('2026-99-99'))

    def test_invalid_calendar_day_rejected(self):
        # Feb 30 does not exist.
        self.assertIsNone(_parse_date_param('2026-02-30'))

    def test_missing_zero_padding_rejected(self):
        # fromisoformat requires strict YYYY-MM-DD; unpadded month is invalid.
        self.assertIsNone(_parse_date_param('2026-7-12'))

    def test_empty_returns_none(self):
        self.assertIsNone(_parse_date_param(''))

    def test_none_returns_none(self):
        self.assertIsNone(_parse_date_param(None))

    def test_garbage_returns_none(self):
        self.assertIsNone(_parse_date_param('not-a-date'))
