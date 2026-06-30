"""Session 1265 — stale-worker guard for ``_impl_process_core_spider_data``.

After S1243 renamed ``core.SpiderData → core.LegacySpiderData`` (commit
``83892860``), 50 ``ProgrammingError: relation "core_spiderdata" does not
exist`` rows fired across 2026-06-27 from a celery worker that still held
the pre-rename class in its ``sys.modules`` cache. The workers recycled
~22 min later and the task has been clean since. The S1265 guard
preflight-checks that the imported model's ``db_table`` actually exists
in the database; if missing, it logs a greppable
``[STALE_WORKER_MODEL_TABLE_MISSING]`` marker and returns a diagnostic
result instead of letting the same ``ProgrammingError`` flap every 2 min.

These tests lock in the contract:

1. **Missing table short-circuits with diagnostic result** — the guard
   returns ``skipped=True, reason='stale_worker_model_table_missing'``,
   does NOT raise, and logs the greppable marker so ops can act.
2. **Present table takes normal path** — when the table exists (the
   real-DB case), the guard is invisible and the task returns its usual
   shape.

Real PostgreSQL (per the S1234 memory rule).

Run::

    .venv/bin/python manage.py test \\
        core.tests.test_process_core_spider_data_stale_worker_guard_s1265 \\
        -v 2 --keepdb
"""

from __future__ import annotations

from unittest.mock import patch

from django.db import connection
from django.test import TestCase

from core.tasks_spiders import _impl_process_core_spider_data


class StaleWorkerModelTableGuardTest(TestCase):
    """S1265 PR: defensive guard at ``_impl_process_core_spider_data`` entry."""

    def test_missing_table_short_circuits_with_diagnostic_result(self):
        """When ``db_table`` is missing, log marker + soft-fail diagnostic dict.

        Locks the post-S1243 stale-worker scenario: model resolves but
        the table it points at was renamed/dropped. Guard must catch this
        before the SELECT fires.
        """
        # Return a table list that does NOT include core_legacyspiderdata.
        with patch.object(
            connection.introspection,
            'table_names',
            return_value=['core_unrelated_table'],
        ):
            with self.assertLogs('core.tasks_spiders', level='ERROR') as log_cm:
                result = _impl_process_core_spider_data()

        # Contract — soft-fail diagnostic result, not an exception
        self.assertTrue(result.get('skipped'))
        self.assertEqual(result.get('reason'), 'stale_worker_model_table_missing')
        self.assertEqual(result.get('processed'), 0)
        self.assertEqual(result.get('errors'), 0)
        self.assertEqual(result.get('remaining'), 0)
        self.assertIn('expected_table', result)
        self.assertEqual(result['expected_table'], 'core_legacyspiderdata')

        # Contract — forensic enrichment per Rigby SIGN: worker git SHA is captured
        # so post-incident triage can identify which deployed code held the stale
        # model class. ``_git_sha()`` returns either a short SHA or '(unavailable)';
        # both are acceptable non-empty strings.
        self.assertIn('worker_git_sha', result)
        worker_git_sha = result['worker_git_sha']
        self.assertIsInstance(worker_git_sha, str)
        assert isinstance(worker_git_sha, str)  # type narrow for the next assertion
        self.assertGreater(len(worker_git_sha), 0)

        # Contract — greppable marker landed in logs for ops triage
        self.assertTrue(
            any('[STALE_WORKER_MODEL_TABLE_MISSING]' in line for line in log_cm.output),
            f"missing marker in logs: {log_cm.output}",
        )
        # Contract — log line carries worker_git_sha for forensic
        self.assertTrue(
            any('worker_git_sha=' in line for line in log_cm.output),
            f"missing worker_git_sha in log line: {log_cm.output}",
        )

    def test_present_table_takes_normal_path(self):
        """When ``db_table`` exists, guard is invisible.

        Real-DB run with empty ``LegacySpiderData`` — should produce the
        normal zero-counter result, NOT the guard's diagnostic shape.
        """
        result = _impl_process_core_spider_data()

        # Contract — guard MUST NOT trip on the present-table happy path
        self.assertNotIn('skipped', result)
        self.assertNotIn('reason', result)
        self.assertNotIn('expected_table', result)

        # Normal result shape preserved
        self.assertEqual(result.get('processed'), 0)
        self.assertEqual(result.get('errors'), 0)
        self.assertIn('remaining', result)
