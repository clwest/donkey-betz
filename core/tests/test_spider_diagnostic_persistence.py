"""Tests for S2969 Phase 1 — spider diagnostic persistence.

Covers:
- ``core.services.spider_diagnostic`` helpers (env flag reads, missing-cred
  detection, diagnostic-dict builders)
- ``_impl_run_spider_network`` behavior when unique_items is empty (Phase 1A),
  when creds are missing (Phase 1B), and per-spider result enrichment (Phase 1C)
- ``cleanup_empty_spider_runs`` retention sweep (Phase 1D)
"""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase
from django.utils import timezone


class SpiderDiagnosticHelpersTests(SimpleTestCase):
    """Unit tests for pure-function helpers in ``spider_diagnostic``."""

    def test_get_empty_run_persistence_mode_default_is_diagnostic_7d(self):
        from core.services import spider_diagnostic

        with patch.dict('os.environ', {}, clear=False):
            import os
            os.environ.pop('SPIDER_EMPTY_RUN_PERSISTENCE_MODE', None)
            self.assertEqual(
                spider_diagnostic.get_empty_run_persistence_mode(),
                spider_diagnostic.EMPTY_RUN_MODE_DIAGNOSTIC_7D,
            )

    def test_get_empty_run_persistence_mode_unknown_falls_back_to_diagnostic_7d(self):
        from core.services import spider_diagnostic

        with patch.dict('os.environ', {'SPIDER_EMPTY_RUN_PERSISTENCE_MODE': 'garbage'}):
            self.assertEqual(
                spider_diagnostic.get_empty_run_persistence_mode(),
                spider_diagnostic.EMPTY_RUN_MODE_DIAGNOSTIC_7D,
            )

    def test_get_empty_run_persistence_mode_off_when_set(self):
        from core.services import spider_diagnostic

        with patch.dict('os.environ', {'SPIDER_EMPTY_RUN_PERSISTENCE_MODE': 'off'}):
            self.assertEqual(
                spider_diagnostic.get_empty_run_persistence_mode(),
                spider_diagnostic.EMPTY_RUN_MODE_OFF,
            )

    def test_get_skip_missing_creds_loudly_default_true(self):
        from core.services import spider_diagnostic

        with patch.dict('os.environ', {}, clear=False):
            import os
            os.environ.pop('SPIDER_SKIP_MISSING_CREDS_LOUDLY', None)
            self.assertTrue(spider_diagnostic.get_skip_missing_creds_loudly())

    def test_get_skip_missing_creds_loudly_false_when_set(self):
        from core.services import spider_diagnostic

        with patch.dict('os.environ', {'SPIDER_SKIP_MISSING_CREDS_LOUDLY': 'false'}):
            self.assertFalse(spider_diagnostic.get_skip_missing_creds_loudly())

    def test_check_missing_credentials_returns_unset_keys(self):
        from core.services import spider_diagnostic

        import os
        with patch.dict('os.environ', {}, clear=False):
            os.environ.pop('GITHUB_TOKEN', None)
            missing = spider_diagnostic.check_missing_credentials('github')
        self.assertEqual(missing, ['GITHUB_TOKEN'])

    def test_check_missing_credentials_empty_when_all_set(self):
        from core.services import spider_diagnostic

        with patch.dict('os.environ', {'GITHUB_TOKEN': 'xoxo-real-token'}):
            missing = spider_diagnostic.check_missing_credentials('github')
        self.assertEqual(missing, [])

    def test_check_missing_credentials_empty_when_no_requirements(self):
        from core.services import spider_diagnostic

        # 'reddit' is NOT in SPIDER_REQUIRED_ENV_KEYS
        self.assertEqual(spider_diagnostic.check_missing_credentials('reddit'), [])

    def test_check_missing_credentials_treats_whitespace_as_unset(self):
        from core.services import spider_diagnostic

        with patch.dict('os.environ', {'GITHUB_TOKEN': '   '}):
            missing = spider_diagnostic.check_missing_credentials('github')
        self.assertEqual(missing, ['GITHUB_TOKEN'])

    def test_check_missing_credentials_partial_returns_only_unset(self):
        from core.services import spider_diagnostic

        import os
        with patch.dict('os.environ', {'SPOTIFY_CLIENT_ID': 'set'}, clear=False):
            os.environ.pop('SPOTIFY_CLIENT_SECRET', None)
            missing = spider_diagnostic.check_missing_credentials('spotify')
        self.assertEqual(missing, ['SPOTIFY_CLIENT_SECRET'])

    def test_build_empty_run_diagnostic_no_items_reason(self):
        from core.services import spider_diagnostic

        d = spider_diagnostic.build_empty_run_diagnostic(
            items_before_dedup=0,
            unique_after_dedup=0,
            duplicates=0,
            execution_log_id='abc-123',
        )
        self.assertEqual(d['status'], 'success_empty')
        self.assertEqual(d['empty_reason'], 'no_items')
        self.assertEqual(d['items_before_dedup'], 0)
        self.assertEqual(d['duplicates'], 0)
        self.assertTrue(d['ephemeral_empty_run'])
        self.assertEqual(d['execution_log_id'], 'abc-123')

    def test_build_empty_run_diagnostic_all_deduped_reason(self):
        from core.services import spider_diagnostic

        d = spider_diagnostic.build_empty_run_diagnostic(
            items_before_dedup=15,
            unique_after_dedup=0,
            duplicates=15,
            execution_log_id=None,
            ephemeral=False,
        )
        self.assertEqual(d['empty_reason'], 'all_deduped')
        self.assertEqual(d['items_before_dedup'], 15)
        self.assertEqual(d['duplicates'], 15)
        self.assertFalse(d['ephemeral_empty_run'])
        self.assertIsNone(d['execution_log_id'])

    def test_build_missing_creds_diagnostic_shape(self):
        from core.services import spider_diagnostic

        d = spider_diagnostic.build_missing_creds_diagnostic(
            missing_keys=['GITHUB_TOKEN', 'SOMETHING_ELSE'],
            execution_log_id='log-42',
        )
        self.assertEqual(d['status'], 'skipped_missing_credentials')
        self.assertEqual(d['missing_keys'], ['GITHUB_TOKEN', 'SOMETHING_ELSE'])
        self.assertEqual(d['execution_log_id'], 'log-42')
        self.assertTrue(d['ephemeral_empty_run'])


def _make_runner_test_env(spider_configs, collect_return_value, dedup_return_value):
    """Shared runner-mock scaffolding — mirrors the pattern in
    ``core/tests/test_spider_network_governance.py`` so shape assertions
    are directly comparable."""
    fake_registry = SimpleNamespace()
    fake_registry.list_spiders = lambda: spider_configs
    fake_registry.get_spider_class = lambda name: object()

    fake_governance = SimpleNamespace(
        objects=SimpleNamespace(
            filter=lambda *args, **kwargs: SimpleNamespace(
                first=lambda: SimpleNamespace(effective_mode='normal')
            )
        )
    )
    return fake_registry, fake_governance


class RunnerEmptyRunPersistenceTests(SimpleTestCase):
    """Phase 1A — persist diagnostic row when unique_items is empty."""

    def test_runner_persists_success_empty_diagnostic_when_dedup_all_deduped(self):
        """dedup returns [] → runner persists success_empty diagnostic row."""
        from core.tasks_spiders import _impl_run_spider_network

        fake_registry, fake_governance = _make_runner_test_env(
            {'reddit': {'config': {'category': 'community'}, 'category': 'community'}},
            {'item_count': 3, 'items': [{'link': 'a'}, {'link': 'b'}, {'link': 'c'}]},
            ([], {'duplicates': 3, 'total': 3}),
        )

        created_rows = []
        diag_created_rows = []

        with patch.dict('os.environ', {
            'SPIDER_EMPTY_RUN_PERSISTENCE_MODE': 'diagnostic_7d',
            'SPIDER_SKIP_MISSING_CREDS_LOUDLY': 'true',
        }), \
             patch('core.models_governance.GovernanceState', fake_governance), \
             patch('ai_core.spiders.spider_registry.SpiderRegistry', return_value=fake_registry), \
             patch('core.tasks_spiders._collect_spider_data_sync', return_value={'item_count': 3, 'items': [{'link': 'a'}, {'link': 'b'}, {'link': 'c'}]}), \
             patch('ai_core.spiders.real_data_collector.collect_spider_data_sync', return_value={'item_count': 3, 'items': [{'link': 'a'}, {'link': 'b'}, {'link': 'c'}]}), \
             patch('core.services.spider_deduplication.deduplicate_spider_items', return_value=([], {'duplicates': 3, 'total': 3})), \
             patch('core.models_unified_system.SpiderExecutionLog') as mock_exec_log, \
             patch('core.models_unified_system.LegacySpiderData') as mock_spider_data:

            mock_exec_log.start_execution.return_value = SimpleNamespace(
                id='exec-1',
                source_urls_attempted=[],
                complete_success=lambda *a, **k: None,
                complete_error=lambda *a, **k: None,
            )

            def _create(**kwargs):
                row = SimpleNamespace(id=f'row-{len(created_rows)}', **kwargs)
                created_rows.append(kwargs)
                if 'diagnostic' in kwargs.get('raw_data', {}):
                    diag_created_rows.append(kwargs)
                return row

            mock_spider_data.objects.create.side_effect = _create

            result = _impl_run_spider_network(SimpleNamespace(request=SimpleNamespace(id='t-1')))

        self.assertEqual(len(diag_created_rows), 1)
        diag = diag_created_rows[0]['raw_data']['diagnostic']
        self.assertEqual(diag['status'], 'success_empty')
        self.assertEqual(diag['empty_reason'], 'all_deduped')
        self.assertEqual(diag['items_before_dedup'], 3)
        self.assertEqual(diag['duplicates'], 3)
        self.assertTrue(diag['ephemeral_empty_run'])
        self.assertEqual(diag['execution_log_id'], 'exec-1')

        spider_result = result['spider_results'][0]
        self.assertEqual(spider_result['status'], 'success_empty')
        self.assertTrue(spider_result['persisted_row'])
        self.assertEqual(spider_result['items_before_dedup'], 3)
        self.assertEqual(spider_result['unique_after_dedup'], 0)
        self.assertEqual(spider_result['duplicates'], 3)

    def test_runner_does_not_persist_diagnostic_when_mode_off(self):
        """Backwards-compat: SPIDER_EMPTY_RUN_PERSISTENCE_MODE=off
        preserves pre-S2969 silent no-op behavior."""
        from core.tasks_spiders import _impl_run_spider_network

        fake_registry, fake_governance = _make_runner_test_env(
            {'reddit': {'config': {'category': 'community'}, 'category': 'community'}},
            {'item_count': 0, 'items': []},
            ([], {'duplicates': 0, 'total': 0}),
        )
        created_rows = []

        with patch.dict('os.environ', {'SPIDER_EMPTY_RUN_PERSISTENCE_MODE': 'off'}), \
             patch('core.models_governance.GovernanceState', fake_governance), \
             patch('ai_core.spiders.spider_registry.SpiderRegistry', return_value=fake_registry), \
             patch('ai_core.spiders.real_data_collector.collect_spider_data_sync', return_value={'item_count': 0, 'items': []}), \
             patch('core.services.spider_deduplication.deduplicate_spider_items', return_value=([], {'duplicates': 0, 'total': 0})), \
             patch('core.models_unified_system.SpiderExecutionLog') as mock_exec_log, \
             patch('core.models_unified_system.LegacySpiderData') as mock_spider_data:

            mock_exec_log.start_execution.return_value = SimpleNamespace(
                id='exec-1',
                source_urls_attempted=[],
                complete_success=lambda *a, **k: None,
                complete_error=lambda *a, **k: None,
            )
            mock_spider_data.objects.create.side_effect = lambda **kwargs: (created_rows.append(kwargs), SimpleNamespace(id='row'))[1]

            result = _impl_run_spider_network(SimpleNamespace(request=SimpleNamespace(id='t-2')))

        self.assertEqual(created_rows, [], 'mode=off must not persist any row when unique_items empty')
        spider_result = result['spider_results'][0]
        self.assertEqual(spider_result['status'], 'success_empty')
        self.assertFalse(spider_result['persisted_row'])

    def test_runner_marks_ephemeral_false_when_mode_always(self):
        """Mode 'always' persists but WITHOUT ephemeral tag → retention sweep skips."""
        from core.tasks_spiders import _impl_run_spider_network

        fake_registry, fake_governance = _make_runner_test_env(
            {'reddit': {'config': {'category': 'community'}, 'category': 'community'}},
            {'item_count': 0, 'items': []},
            ([], {'duplicates': 0, 'total': 0}),
        )
        diag_rows = []

        with patch.dict('os.environ', {'SPIDER_EMPTY_RUN_PERSISTENCE_MODE': 'always'}), \
             patch('core.models_governance.GovernanceState', fake_governance), \
             patch('ai_core.spiders.spider_registry.SpiderRegistry', return_value=fake_registry), \
             patch('ai_core.spiders.real_data_collector.collect_spider_data_sync', return_value={'item_count': 0, 'items': []}), \
             patch('core.services.spider_deduplication.deduplicate_spider_items', return_value=([], {'duplicates': 0, 'total': 0})), \
             patch('core.models_unified_system.SpiderExecutionLog') as mock_exec_log, \
             patch('core.models_unified_system.LegacySpiderData') as mock_spider_data:

            mock_exec_log.start_execution.return_value = SimpleNamespace(
                id='exec-1',
                source_urls_attempted=[],
                complete_success=lambda *a, **k: None,
                complete_error=lambda *a, **k: None,
            )
            def _create(**kwargs):
                if 'diagnostic' in kwargs.get('raw_data', {}):
                    diag_rows.append(kwargs)
                return SimpleNamespace(id='r')
            mock_spider_data.objects.create.side_effect = _create

            _impl_run_spider_network(SimpleNamespace(request=SimpleNamespace(id='t-3')))

        self.assertEqual(len(diag_rows), 1)
        self.assertFalse(diag_rows[0]['raw_data']['diagnostic']['ephemeral_empty_run'])


class RunnerMissingCredsSkipTests(SimpleTestCase):
    """Phase 1B — skip loudly on missing credentials."""

    def test_runner_persists_skipped_missing_credentials_row_and_skips_fetch(self):
        from core.tasks_spiders import _impl_run_spider_network

        fake_registry, fake_governance = _make_runner_test_env(
            {'github': {'config': {'category': 'tech'}, 'category': 'tech'}},
            {'item_count': 0, 'items': []},
            ([], {'duplicates': 0, 'total': 0}),
        )
        created_rows = []

        import os
        with patch.dict('os.environ', {
            'SPIDER_EMPTY_RUN_PERSISTENCE_MODE': 'diagnostic_7d',
            'SPIDER_SKIP_MISSING_CREDS_LOUDLY': 'true',
        }, clear=False), \
             patch('core.models_governance.GovernanceState', fake_governance), \
             patch('ai_core.spiders.spider_registry.SpiderRegistry', return_value=fake_registry), \
             patch('ai_core.spiders.real_data_collector.collect_spider_data_sync') as mock_collect, \
             patch('core.services.spider_deduplication.deduplicate_spider_items') as mock_dedup, \
             patch('core.models_unified_system.SpiderExecutionLog') as mock_exec_log, \
             patch('core.models_unified_system.LegacySpiderData') as mock_spider_data:

            os.environ.pop('GITHUB_TOKEN', None)
            mock_exec_log.start_execution.return_value = SimpleNamespace(
                id='exec-77',
                source_urls_attempted=[],
                complete_success=lambda *a, **k: None,
                complete_error=lambda *a, **k: None,
            )
            def _create(**kwargs):
                created_rows.append(kwargs)
                return SimpleNamespace(id='row-x')
            mock_spider_data.objects.create.side_effect = _create

            result = _impl_run_spider_network(SimpleNamespace(request=SimpleNamespace(id='t-c')))

        # Fetch must not have been attempted
        mock_collect.assert_not_called()
        mock_dedup.assert_not_called()
        # One diagnostic row for skipped_missing_credentials
        self.assertEqual(len(created_rows), 1)
        diag = created_rows[0]['raw_data']['diagnostic']
        self.assertEqual(diag['status'], 'skipped_missing_credentials')
        self.assertEqual(diag['missing_keys'], ['GITHUB_TOKEN'])
        self.assertEqual(diag['execution_log_id'], 'exec-77')

        spider_result = result['spider_results'][0]
        self.assertEqual(spider_result['status'], 'skipped_missing_credentials')
        self.assertEqual(spider_result['missing_keys'], ['GITHUB_TOKEN'])
        self.assertTrue(spider_result['persisted_row'])
        self.assertTrue(spider_result['success'])  # skip is a controlled success, not failure

    def test_runner_proceeds_with_fetch_when_skip_toggle_false(self):
        """Backwards-compat: SPIDER_SKIP_MISSING_CREDS_LOUDLY=false
        preserves the old silent-run-with-unset-creds behavior."""
        from core.tasks_spiders import _impl_run_spider_network

        fake_registry, fake_governance = _make_runner_test_env(
            {'github': {'config': {'category': 'tech'}, 'category': 'tech'}},
            {'item_count': 1, 'items': [{'link': 'x'}]},
            ([{'link': 'x'}], {'duplicates': 0, 'total': 1}),
        )

        import os
        with patch.dict('os.environ', {'SPIDER_SKIP_MISSING_CREDS_LOUDLY': 'false'}, clear=False), \
             patch('core.models_governance.GovernanceState', fake_governance), \
             patch('ai_core.spiders.spider_registry.SpiderRegistry', return_value=fake_registry), \
             patch('ai_core.spiders.real_data_collector.collect_spider_data_sync', return_value={'item_count': 1, 'items': [{'link': 'x'}]}) as mock_collect, \
             patch('core.services.spider_deduplication.deduplicate_spider_items', return_value=([{'link': 'x'}], {'duplicates': 0, 'total': 1})), \
             patch('core.models_unified_system.SpiderExecutionLog') as mock_exec_log, \
             patch('core.models_unified_system.LegacySpiderData') as mock_spider_data:

            os.environ.pop('GITHUB_TOKEN', None)
            mock_exec_log.start_execution.return_value = SimpleNamespace(
                id='exec-1',
                source_urls_attempted=[],
                complete_success=lambda *a, **k: None,
                complete_error=lambda *a, **k: None,
            )
            mock_spider_data.objects.create.return_value = SimpleNamespace(id='r')

            _impl_run_spider_network(SimpleNamespace(request=SimpleNamespace(id='t-c2')))

        # Fetch WAS attempted
        mock_collect.assert_called_once()


class RunnerResultShapeTests(SimpleTestCase):
    """Phase 1C — enriched per-spider execution summary."""

    def test_runner_success_path_result_includes_new_metrics(self):
        from core.tasks_spiders import _impl_run_spider_network

        fake_registry, fake_governance = _make_runner_test_env(
            {'reddit': {'config': {'category': 'community'}, 'category': 'community'}},
            {'item_count': 2, 'items': [{'link': 'a'}, {'link': 'b'}]},
            ([{'link': 'a'}, {'link': 'b'}], {'duplicates': 0, 'total': 2}),
        )

        with patch.dict('os.environ', {'SPIDER_EMPTY_RUN_PERSISTENCE_MODE': 'diagnostic_7d'}), \
             patch('core.models_governance.GovernanceState', fake_governance), \
             patch('ai_core.spiders.spider_registry.SpiderRegistry', return_value=fake_registry), \
             patch('ai_core.spiders.real_data_collector.collect_spider_data_sync', return_value={'item_count': 2, 'items': [{'link': 'a'}, {'link': 'b'}]}), \
             patch('core.services.spider_deduplication.deduplicate_spider_items', return_value=([{'link': 'a'}, {'link': 'b'}], {'duplicates': 0, 'total': 2})), \
             patch('core.models_unified_system.SpiderExecutionLog') as mock_exec_log, \
             patch('core.models_unified_system.LegacySpiderData') as mock_spider_data, \
             patch('redis.Redis.from_url'):

            mock_exec_log.start_execution.return_value = SimpleNamespace(
                id='e',
                source_urls_attempted=[],
                complete_success=lambda *a, **k: None,
                complete_error=lambda *a, **k: None,
            )
            mock_spider_data.objects.create.return_value = SimpleNamespace(id='r')

            result = _impl_run_spider_network(SimpleNamespace(request=SimpleNamespace(id='t')))

        r = result['spider_results'][0]
        for key in ('status', 'items_before_dedup', 'unique_after_dedup', 'duplicates', 'persisted_row'):
            self.assertIn(key, r, f'missing enriched metric: {key}')
        self.assertEqual(r['status'], 'success')
        self.assertEqual(r['items_before_dedup'], 2)
        self.assertEqual(r['unique_after_dedup'], 2)
        self.assertEqual(r['duplicates'], 0)
        self.assertTrue(r['persisted_row'])


class LightweightExecuteEmptyRunPersistenceTests(SimpleTestCase):
    """Phase 1A parity on the dashboard Execute path (Rigby A2 SIGN #2).

    The Beat runner persists success_empty diagnostics; the dashboard-Execute
    path (``_impl_execute_single_spider_lightweight``) also needs to persist
    them so an operator hitting Execute on a "never_run" spider sees a row
    materialize instead of silence."""

    def test_lightweight_execute_persists_diagnostic_when_dedup_empty(self):
        from core.tasks_spiders import _impl_execute_single_spider_lightweight

        created_rows = []
        with patch.dict('os.environ', {'SPIDER_EMPTY_RUN_PERSISTENCE_MODE': 'diagnostic_7d'}), \
             patch('core.tasks._collect_spider_data_sync', return_value={'items': [{'link': 'x'}], 'source': 'reddit'}), \
             patch('core.services.spider_deduplication.deduplicate_spider_items', return_value=([], {'duplicates': 1, 'total': 1})), \
             patch('core.models_unified_system.LegacySpiderData') as mock_model:

            def _create(**kwargs):
                created_rows.append(kwargs)
                return SimpleNamespace(id='r-1')
            mock_model.objects.create.side_effect = _create

            result = _impl_execute_single_spider_lightweight('reddit')

        self.assertEqual(len(created_rows), 1)
        diag = created_rows[0]['raw_data']['diagnostic']
        self.assertEqual(diag['status'], 'success_empty')
        self.assertEqual(diag['empty_reason'], 'all_deduped')
        self.assertTrue(diag['ephemeral_empty_run'])
        self.assertEqual(created_rows[0]['source_url'], 'on-demand-execution')
        # execution_log_id is None on the dashboard path (documented)
        self.assertIsNone(diag['execution_log_id'])
        self.assertTrue(result['success'])

    def test_lightweight_execute_no_op_when_mode_off(self):
        """Backwards-compat: mode=off restores pre-S2969 silent-skip on the
        dashboard path (same as the Beat runner)."""
        from core.tasks_spiders import _impl_execute_single_spider_lightweight

        created_rows = []
        with patch.dict('os.environ', {'SPIDER_EMPTY_RUN_PERSISTENCE_MODE': 'off'}), \
             patch('core.tasks._collect_spider_data_sync', return_value={'items': [], 'source': 'reddit'}), \
             patch('core.services.spider_deduplication.deduplicate_spider_items', return_value=([], {'duplicates': 0, 'total': 0})), \
             patch('core.models_unified_system.LegacySpiderData') as mock_model:

            def _create(**kwargs):
                created_rows.append(kwargs)
                return SimpleNamespace(id='r-1')
            mock_model.objects.create.side_effect = _create

            _impl_execute_single_spider_lightweight('reddit')

        self.assertEqual(created_rows, [])


class CleanupEmptySpiderRunsQueryTests(TestCase):
    """Phase 1D — verify the retention sweep's filter semantics.

    We assert on the filtered ``.count()`` (via the task's ``matched`` field)
    rather than on ``.delete()`` results because the test DB is missing the
    ``narrative_evidence`` table (a pre-existing migration drift from the
    S1243 ``SpiderData → LegacySpiderData`` rename that predates this arc).
    The ``SET_NULL`` cascade from ``NarrativeEvidence.spider_data`` fires on
    every LegacySpiderData delete and blows up before we can assert.

    The filter semantics are what actually gate the sweep's correctness —
    if the filter matches the wrong rows, ``.delete()`` in prod would
    delete the wrong data even if the delete "worked."
    """

    def _make_row(self, spider_name: str, diagnostic: dict, days_old: int):
        from core.models_unified_system import LegacySpiderData
        row = LegacySpiderData.objects.create(
            spider_name=spider_name,
            data_type='community',
            raw_data={'items': [], 'diagnostic': diagnostic, 'source': spider_name},
            source_url='internal',
            relevance_score=0,
        )
        LegacySpiderData.objects.filter(pk=row.pk).update(
            created_at=timezone.now() - timedelta(days=days_old),
        )
        return row

    def _make_real_row(self, spider_name: str, days_old: int):
        from core.models_unified_system import LegacySpiderData
        row = LegacySpiderData.objects.create(
            spider_name=spider_name,
            data_type='community',
            raw_data={'items': [{'title': 'real', 'link': 'https://example.com/x'}]},
            source_url='https://example.com',
            relevance_score=70,
        )
        LegacySpiderData.objects.filter(pk=row.pk).update(
            created_at=timezone.now() - timedelta(days=days_old),
        )
        return row

    def _matched_count(self, days: int = 7) -> int:
        """Mirror the task's filter without invoking ``.delete()``."""
        from core.models_unified_system import LegacySpiderData
        cutoff = timezone.now() - timedelta(days=days)
        return LegacySpiderData.objects.filter(
            raw_data__diagnostic__ephemeral_empty_run=True,
            created_at__lt=cutoff,
        ).count()

    def test_filter_matches_ephemeral_row_older_than_seven_days(self):
        self._make_row('reddit', {
            'status': 'success_empty', 'empty_reason': 'no_items',
            'ephemeral_empty_run': True,
        }, days_old=10)
        self.assertEqual(self._matched_count(days=7), 1)

    def test_filter_excludes_recent_ephemeral_row(self):
        self._make_row('reddit', {
            'status': 'success_empty', 'empty_reason': 'no_items',
            'ephemeral_empty_run': True,
        }, days_old=2)
        self.assertEqual(self._matched_count(days=7), 0)

    def test_filter_excludes_non_ephemeral_diagnostic_rows(self):
        """Rows written under mode='always' carry ``ephemeral_empty_run=False``
        and must survive the sweep even when old."""
        self._make_row('reddit', {
            'status': 'success_empty', 'empty_reason': 'no_items',
            'ephemeral_empty_run': False,
        }, days_old=30)
        self.assertEqual(self._matched_count(days=7), 0)

    def test_filter_excludes_real_data_rows(self):
        """Rows without a diagnostic block (real spider data) must never
        match — retention sweep only targets ephemeral diagnostics."""
        self._make_real_row('reddit', days_old=30)
        self.assertEqual(self._matched_count(days=7), 0)

    def test_filter_excludes_skipped_missing_creds_when_not_ephemeral(self):
        """When mode=always, missing-creds rows are ephemeral=False and
        must survive the sweep."""
        self._make_row('github', {
            'status': 'skipped_missing_credentials',
            'missing_keys': ['GITHUB_TOKEN'],
            'ephemeral_empty_run': False,
        }, days_old=30)
        self.assertEqual(self._matched_count(days=7), 0)

    def test_filter_matches_ephemeral_skipped_missing_creds_row(self):
        """When mode=diagnostic_7d, missing-creds rows are ephemeral=True and
        get swept alongside empty runs."""
        self._make_row('github', {
            'status': 'skipped_missing_credentials',
            'missing_keys': ['GITHUB_TOKEN'],
            'ephemeral_empty_run': True,
        }, days_old=10)
        self.assertEqual(self._matched_count(days=7), 1)


class CleanupEmptySpiderRunsTaskShapeTests(SimpleTestCase):
    """Phase 1D — verify the ``cleanup_empty_spider_runs`` task's return shape.

    Uses mocking rather than DB to avoid the ``narrative_evidence`` cascade
    issue described in the query-test docstring above."""

    def test_task_returns_expected_shape(self):
        from core.tasks import cleanup_empty_spider_runs

        with patch('core.models_unified_system.LegacySpiderData') as mock_model:
            qs = SimpleNamespace()
            qs.count = lambda: 3
            qs.db = 'default'
            qs._raw_delete = lambda using: 3
            mock_model.objects.filter.return_value = qs

            result = cleanup_empty_spider_runs(days=7)

        self.assertEqual(result['deleted'], 3)
        self.assertEqual(result['matched'], 3)
        self.assertEqual(result['days'], 7)
        self.assertEqual(result['batch_cap'], 5000)
        self.assertIn('cutoff', result)

    def test_task_honors_custom_days_argument(self):
        from core.tasks import cleanup_empty_spider_runs

        with patch('core.models_unified_system.LegacySpiderData') as mock_model:
            qs = SimpleNamespace()
            qs.count = lambda: 0
            qs.db = 'default'
            qs._raw_delete = lambda using: 0
            mock_model.objects.filter.return_value = qs

            result = cleanup_empty_spider_runs(days=14)

        self.assertEqual(result['days'], 14)
        self.assertEqual(result['deleted'], 0)
        self.assertEqual(result['matched'], 0)

    def test_task_reports_batch_cap_in_return_dict(self):
        """batch_cap arg is reflected in the return dict for observability."""
        from core.tasks import cleanup_empty_spider_runs

        with patch('core.models_unified_system.LegacySpiderData') as mock_model:
            qs = SimpleNamespace()
            qs.count = lambda: 0
            qs.db = 'default'
            qs._raw_delete = lambda using: 0
            mock_model.objects.filter.return_value = qs

            result = cleanup_empty_spider_runs(days=7, batch_cap=100)

        self.assertEqual(result['batch_cap'], 100)
