"""S2775 N15 — session-open freshness telemetry tests.

Locks two contracts introduced this session:

  1. ``core.services.process_freshness.compute_process_staleness`` — a
     module-level function extracted from
     ``OpsHandler._compute_process_staleness`` — returns the same shape
     the ops-tool version handler has always returned. The OpsHandler
     method is now a 1-line delegating wrapper.

  2. ``session_lifecycle open`` appends one lean JSONL row per
     successful mint to ``logs/session_freshness.jsonl`` for
     PLAYBOOK-7.4.4 trend detection. Capture is fail-soft — an
     exception in the freshness read must not break the pin mint
     that already committed.

  3. ``session_lifecycle history`` reads the JSONL back for eyeballing
     without touching the DB or wrapper file.

Ratified: S2775 Rigby joint SIGN (Q1/Q3 YES agree, Q2 add
`head_commit_age_seconds`, Q4 defer close-time capture to v2) +
Chris D-verdict yes.

These tests deliberately do NOT invoke the full ``session_lifecycle
open`` transaction path — that surface is exercised by manual runs +
S2746 discipline. The freshness contract is unit-testable on its own
because ``_record_session_freshness`` is a stateless helper.
"""
from __future__ import annotations

import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from core.management.commands.session_lifecycle import Command as SessionLifecycleCommand
from core.services import process_freshness
from core.services.td_handlers_ops import OpsHandlersMixin


class ComputeProcessStalenessShapeTests(TestCase):
    """Extraction parity — the module-level function returns the same keys
    the OpsHandler method used to return before S2775 N15."""

    def test_returns_verdict_key(self):
        result = process_freshness.compute_process_staleness()
        self.assertIn('staleness_verdict', result)
        self.assertIn(
            result['staleness_verdict'],
            {'FRESH', 'STALE_DAPHNE', 'STALE_CELERY', 'STALE_BOTH', 'UNKNOWN'},
        )

    def test_ok_verdict_carries_head_metadata(self):
        result = process_freshness.compute_process_staleness()
        if result['staleness_verdict'] == 'UNKNOWN':
            self.assertIn('staleness_error', result)
            return
        # Non-UNKNOWN paths must carry the git metadata used to compute the verdict.
        self.assertIn('head_commit_sha', result)
        self.assertIn('head_commit_timestamp', result)
        self.assertIn('celery_workers_status', result)
        self.assertIn('daphne_pid', result)
        self.assertIn('daphne_pid_age_seconds', result)
        self.assertIn('daphne_started_before_head_commit', result)

    def test_ops_handler_wrapper_delegates_to_extracted_function(self):
        """The OpsHandler method must forward to the extracted function
        so ops_tool.version continues to work unchanged."""
        sentinel = {'staleness_verdict': 'FRESH', 'sentinel': True}
        with patch.object(
            process_freshness, 'compute_process_staleness',
            return_value=sentinel,
        ):
            # Real handler instance is heavier than needed; delegate check
            # only requires that the wrapper imports + calls the module fn.
            class _Bag(OpsHandlersMixin):
                pass

            result = _Bag()._compute_process_staleness()
            self.assertEqual(result, sentinel)


class RecordSessionFreshnessTests(TestCase):
    """The _record_session_freshness helper writes a lean row + fails soft."""

    def _cmd(self) -> SessionLifecycleCommand:
        cmd = SessionLifecycleCommand()
        cmd.stdout = io.StringIO()
        cmd.stderr = io.StringIO()
        return cmd

    def test_writes_row_with_expected_fields(self):
        cmd = self._cmd()
        fake_verdict = {
            'staleness_verdict': 'FRESH',
            'head_commit_sha': 'b3139325831a7c51067ce56e',
            'head_commit_timestamp': '2026-07-13T21:00:00+00:00',
            'daphne_pid': 12345,
            'daphne_pid_age_seconds': 400,
            'daphne_started_before_head_commit': False,
            'celery_workers_status': [
                {'hostname': 'default@w1', 'pid': 1, 'pid_age_seconds': 400,
                 'started_before_head_commit': False},
                {'hostname': 'pa@w1', 'pid': 2, 'pid_age_seconds': 400,
                 'started_before_head_commit': False},
            ],
        }
        with TemporaryDirectory() as td:
            log_path = Path(td) / 'session_freshness.jsonl'
            with patch(
                'core.services.process_freshness.compute_process_staleness',
                return_value=fake_verdict,
            ):
                row = cmd._record_session_freshness(
                    new_pin='pa-0000000000000001',
                    label='s2775-test',
                    context='session_open',
                    log_path=log_path,
                )
            self.assertEqual(row['verdict'], 'FRESH')
            self.assertEqual(row['pin'], 'pa-0000000000000001')
            self.assertEqual(row['session_label'], 's2775-test')
            self.assertEqual(row['context'], 'session_open')
            self.assertEqual(row['head_sha_short'], 'b3139325831a')
            self.assertEqual(row['celery_worker_count'], 2)
            self.assertEqual(row['celery_stale_count'], 0)
            self.assertEqual(row['daphne_pid_age_seconds'], 400)
            self.assertIn('head_commit_age_seconds', row)
            self.assertIn('ts', row)

            # File was written exactly one row
            self.assertTrue(log_path.exists())
            lines = log_path.read_text(encoding='utf-8').splitlines()
            self.assertEqual(len(lines), 1)
            parsed = json.loads(lines[0])
            self.assertEqual(parsed['verdict'], 'FRESH')

    def test_counts_stale_celery_workers(self):
        cmd = self._cmd()
        fake_verdict = {
            'staleness_verdict': 'STALE_CELERY',
            'head_commit_sha': 'deadbeefdead',
            'head_commit_timestamp': '2026-07-13T21:00:00+00:00',
            'daphne_pid': 12345,
            'daphne_pid_age_seconds': 100,
            'daphne_started_before_head_commit': False,
            'celery_workers_status': [
                {'hostname': 'default', 'pid': 1, 'pid_age_seconds': 400,
                 'started_before_head_commit': True},
                {'hostname': 'pa', 'pid': 2, 'pid_age_seconds': 400,
                 'started_before_head_commit': True},
                {'hostname': 'broadcast', 'pid': 3, 'pid_age_seconds': 50,
                 'started_before_head_commit': False},
            ],
        }
        with TemporaryDirectory() as td:
            log_path = Path(td) / 'session_freshness.jsonl'
            with patch(
                'core.services.process_freshness.compute_process_staleness',
                return_value=fake_verdict,
            ):
                row = cmd._record_session_freshness(
                    new_pin='pa-0000000000000002',
                    label='s2775-stale',
                    context='session_open',
                    log_path=log_path,
                )
            self.assertEqual(row['verdict'], 'STALE_CELERY')
            self.assertEqual(row['celery_worker_count'], 3)
            self.assertEqual(row['celery_stale_count'], 2)

    def test_fail_soft_on_compute_exception(self):
        """A raise in compute_process_staleness must NOT propagate."""
        cmd = self._cmd()
        with TemporaryDirectory() as td:
            log_path = Path(td) / 'session_freshness.jsonl'
            with patch(
                'core.services.process_freshness.compute_process_staleness',
                side_effect=RuntimeError('psutil exploded'),
            ):
                row = cmd._record_session_freshness(
                    new_pin='pa-0000000000000003',
                    label='s2775-fail-soft',
                    context='session_open',
                    log_path=log_path,
                )
            self.assertEqual(row, {})
            # File must NOT be created on failure — no partial rows.
            self.assertFalse(log_path.exists())
            # Failure message surfaces on stderr, not raised.
            self.assertIn('freshness telemetry capture failed', cmd.stderr.getvalue())

    def test_appends_multiple_rows(self):
        cmd = self._cmd()
        fake_verdict = {
            'staleness_verdict': 'FRESH',
            'head_commit_sha': 'aaaa1111bbbb',
            'head_commit_timestamp': '2026-07-13T21:00:00+00:00',
            'daphne_pid': 1,
            'daphne_pid_age_seconds': 60,
            'daphne_started_before_head_commit': False,
            'celery_workers_status': [],
        }
        with TemporaryDirectory() as td:
            log_path = Path(td) / 'session_freshness.jsonl'
            with patch(
                'core.services.process_freshness.compute_process_staleness',
                return_value=fake_verdict,
            ):
                for i in range(3):
                    cmd._record_session_freshness(
                        new_pin=f'pa-000000000000000{i}',
                        label=f's2775-append-{i}',
                        context='session_open',
                        log_path=log_path,
                    )
            lines = log_path.read_text(encoding='utf-8').splitlines()
            self.assertEqual(len(lines), 3)
            for i, line in enumerate(lines):
                parsed = json.loads(line)
                self.assertEqual(parsed['session_label'], f's2775-append-{i}')


class HistorySubcommandTests(TestCase):
    """The history subcommand reads the JSONL back for eyeballing."""

    def test_missing_log_prints_graceful_message(self):
        with TemporaryDirectory() as td:
            log_path = Path(td) / 'nonexistent.jsonl'
            out = io.StringIO()
            call_command(
                'session_lifecycle', 'history',
                '--log-path', str(log_path),
                stdout=out,
            )
            self.assertIn('no freshness log', out.getvalue())

    def test_reads_back_rows(self):
        rows = [
            {'ts': '2026-07-13T21:00:00+00:00', 'session_label': 's2773',
             'pin': 'pa-a', 'context': 'session_open', 'verdict': 'FRESH',
             'head_sha_short': 'aaaa', 'head_commit_age_seconds': 100,
             'daphne_pid_age_seconds': 50, 'celery_worker_count': 6,
             'celery_stale_count': 0},
            {'ts': '2026-07-13T22:00:00+00:00', 'session_label': 's2774',
             'pin': 'pa-b', 'context': 'session_open', 'verdict': 'STALE_BOTH',
             'head_sha_short': 'bbbb', 'head_commit_age_seconds': 3600,
             'daphne_pid_age_seconds': 5000, 'celery_worker_count': 6,
             'celery_stale_count': 6},
        ]
        with TemporaryDirectory() as td:
            log_path = Path(td) / 'session_freshness.jsonl'
            with log_path.open('w', encoding='utf-8') as f:
                for row in rows:
                    f.write(json.dumps(row) + '\n')
            out = io.StringIO()
            call_command(
                'session_lifecycle', 'history',
                '--log-path', str(log_path),
                '--limit', '10',
                stdout=out,
            )
            text = out.getvalue()
            self.assertIn('FRESH', text)
            self.assertIn('STALE_BOTH', text)
            self.assertIn('s2773', text)
            self.assertIn('s2774', text)
            self.assertIn('2 of 2 rows', text)

    def test_limit_shows_only_most_recent(self):
        rows = [
            {'ts': f'2026-07-13T{h:02d}:00:00+00:00', 'session_label': f's{h}',
             'pin': f'pa-{h}', 'context': 'session_open', 'verdict': 'FRESH',
             'head_sha_short': 'xxxx', 'head_commit_age_seconds': 100,
             'daphne_pid_age_seconds': 50, 'celery_worker_count': 6,
             'celery_stale_count': 0}
            for h in range(1, 6)  # 5 rows
        ]
        with TemporaryDirectory() as td:
            log_path = Path(td) / 'session_freshness.jsonl'
            with log_path.open('w', encoding='utf-8') as f:
                for row in rows:
                    f.write(json.dumps(row) + '\n')
            out = io.StringIO()
            call_command(
                'session_lifecycle', 'history',
                '--log-path', str(log_path),
                '--limit', '2',
                stdout=out,
            )
            text = out.getvalue()
            self.assertIn('2 of 5 rows', text)
            # Most recent = s4 + s5; s1 not shown
            self.assertIn('s4', text)
            self.assertIn('s5', text)
            self.assertNotIn(' s1 ', text)
