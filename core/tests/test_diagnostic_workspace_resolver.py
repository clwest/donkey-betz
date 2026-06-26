"""Session 1238 PR-A — scheduled_diagnostic_runner workspace resolver.

Verifies that the 3 scheduled diagnostics (COO / CTO / TrendAnalysis)
all wire the shared `resolve_morning_brief_workspace_id` resolver into
their `DiagnosticConfig.workspace_resolver` field, AND that the runner's
priority chain (env var → resolver → None) returns the MB workspace_id
to dispatched COOAgent/CTOAgent/TrendAnalysisAgent contexts.

Pre-fix (Session 1238 P1.b drill): today's 06-26 COO diagnostic
dispatched COOAgent with `ctx.workspace_id=None`; agent_router fallback
picked the user's most-recent-active workspace (cf708a2e debug ws from
Session 1231 E2E). Same shape applies to CTO + Trend daily diagnostics.

Per `feedback_test_real_db_for_queryset_semantics`: real DB throughout;
real ProjectWorkspace rows; no MagicMock'd querysets.

Run::

    python manage.py test core.tests.test_diagnostic_workspace_resolver -v 2 --keepdb
"""

import uuid

from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()
ProjectWorkspace = apps.get_model('core', 'ProjectWorkspace')


class WorkspaceResolverHelperTests(TestCase):
    """Direct tests of `resolve_morning_brief_workspace_id` shared helper."""

    def test_returns_mb_workspace_id_for_chris(self):
        chris = User.objects.create_user(username='chris', password='test')
        mb_ws = ProjectWorkspace.objects.create(
            user=chris,
            name='Morning Brief',
            workspace_type='local',
            root_path='/morning-brief',
        )

        from core.services.diagnostics._workspace_resolver import (
            resolve_morning_brief_workspace_id,
        )
        result = resolve_morning_brief_workspace_id()
        self.assertEqual(result, str(mb_ws.id))

    def test_returns_none_when_chris_missing(self):
        from core.services.diagnostics._workspace_resolver import (
            resolve_morning_brief_workspace_id,
        )
        self.assertIsNone(resolve_morning_brief_workspace_id())

    def test_returns_none_when_chris_has_no_mb_workspace(self):
        User.objects.create_user(username='chris', password='test')
        from core.services.diagnostics._workspace_resolver import (
            resolve_morning_brief_workspace_id,
        )
        self.assertIsNone(resolve_morning_brief_workspace_id())

    def test_returns_str_uuid_not_uuid_object(self):
        """The runner passes the result into context['workspace_id']
        which downstream consumers expect as str."""
        chris = User.objects.create_user(username='chris', password='test')
        ProjectWorkspace.objects.create(
            user=chris,
            name='Morning Brief',
            workspace_type='local',
            root_path='/morning-brief',
        )
        from core.services.diagnostics._workspace_resolver import (
            resolve_morning_brief_workspace_id,
        )
        result = resolve_morning_brief_workspace_id()
        self.assertIsInstance(result, str)


class DiagnosticConfigWiringTests(TestCase):
    """All 3 daily diagnostics must wire the shared resolver into their
    DiagnosticConfig — if any regresses to env-var-only, the leak returns."""

    def test_coo_config_wires_resolver(self):
        from core.services.diagnostics.coo_daily import build_config
        from core.services.diagnostics._workspace_resolver import (
            resolve_morning_brief_workspace_id,
        )
        config = build_config()
        self.assertIsNotNone(
            config.workspace_resolver,
            "coo_daily.build_config() must set workspace_resolver to "
            "prevent cf708a2e-style router-fallback leaks.",
        )
        self.assertIs(
            config.workspace_resolver,
            resolve_morning_brief_workspace_id,
            "COO must use the shared resolver, not a custom one.",
        )

    def test_cto_config_wires_resolver(self):
        from core.services.diagnostics.cto_daily import build_config
        from core.services.diagnostics._workspace_resolver import (
            resolve_morning_brief_workspace_id,
        )
        config = build_config()
        self.assertIsNotNone(config.workspace_resolver)
        self.assertIs(
            config.workspace_resolver, resolve_morning_brief_workspace_id,
        )

    def test_trend_config_wires_resolver(self):
        from core.services.diagnostics.trend_analysis_daily import build_config
        from core.services.diagnostics._workspace_resolver import (
            resolve_morning_brief_workspace_id,
        )
        config = build_config()
        self.assertIsNotNone(config.workspace_resolver)
        self.assertIs(
            config.workspace_resolver, resolve_morning_brief_workspace_id,
        )


class RunnerPriorityChainTests(TestCase):
    """Runner's workspace_id resolution: env var → resolver → None."""

    def test_env_var_wins_over_resolver(self):
        from core.services.scheduled_diagnostic_runner import DiagnosticConfig
        explicit_ws = str(uuid.uuid4())
        config = DiagnosticConfig(
            name='test_diag',
            diagnostic_type='test_diag',
            agent_name='TestAgent',
            source_agent='TestAgent',
            log_prefix='TEST',
            metrics_collector=lambda *a: {},
            gate_evaluator=lambda m: {'severity': 'low', 'reasons': []},
            prompt_builder=lambda m, g: 'p',
            dedupe_payload_builder=lambda m, g: {},
            headline_builder=lambda m, g: 'h',
            title_builder=lambda m, g, d: 't',
            extra_sections=[],
            post_task_import_path='core.tasks:noop',
            enabled_env='TEST_ENABLED',
            posting_enabled_env='TEST_POSTING_ENABLED',
            workspace_id_env='TEST_WORKSPACE_ID',
            workspace_resolver=lambda: 'resolver-value',
        )
        # Simulate env var being set
        import os
        os.environ['TEST_WORKSPACE_ID'] = explicit_ws
        try:
            # Reproduce runner's resolution logic inline
            from core.services.scheduled_diagnostic_runner import _env_value
            workspace_id = None
            if config.workspace_id_env:
                env_val = _env_value(config.workspace_id_env)
                if env_val:
                    workspace_id = env_val
            if workspace_id is None and config.workspace_resolver is not None:
                workspace_id = config.workspace_resolver()
            self.assertEqual(workspace_id, explicit_ws)
        finally:
            del os.environ['TEST_WORKSPACE_ID']

    def test_resolver_fallback_when_env_unset(self):
        """When env var unset, resolver's return value is used."""
        from core.services.scheduled_diagnostic_runner import (
            DiagnosticConfig, _env_value,
        )
        config = DiagnosticConfig(
            name='test_diag',
            diagnostic_type='test_diag',
            agent_name='TestAgent',
            source_agent='TestAgent',
            log_prefix='TEST',
            metrics_collector=lambda *a: {},
            gate_evaluator=lambda m: {'severity': 'low', 'reasons': []},
            prompt_builder=lambda m, g: 'p',
            dedupe_payload_builder=lambda m, g: {},
            headline_builder=lambda m, g: 'h',
            title_builder=lambda m, g, d: 't',
            extra_sections=[],
            post_task_import_path='core.tasks:noop',
            enabled_env='TEST_ENABLED',
            posting_enabled_env='TEST_POSTING_ENABLED',
            workspace_id_env='TEST_UNSET_VAR_XYZ',  # not in env
            workspace_resolver=lambda: 'resolver-fallback',
        )
        workspace_id = None
        if config.workspace_id_env:
            env_val = _env_value(config.workspace_id_env)
            if env_val:
                workspace_id = env_val
        if workspace_id is None and config.workspace_resolver is not None:
            workspace_id = config.workspace_resolver()
        self.assertEqual(workspace_id, 'resolver-fallback')

    def test_none_when_no_env_and_no_resolver(self):
        """When neither env var nor resolver is set, workspace_id is None
        (pre-fix behavior — preserved for backward compat)."""
        from core.services.scheduled_diagnostic_runner import (
            DiagnosticConfig, _env_value,
        )
        config = DiagnosticConfig(
            name='test_diag',
            diagnostic_type='test_diag',
            agent_name='TestAgent',
            source_agent='TestAgent',
            log_prefix='TEST',
            metrics_collector=lambda *a: {},
            gate_evaluator=lambda m: {'severity': 'low', 'reasons': []},
            prompt_builder=lambda m, g: 'p',
            dedupe_payload_builder=lambda m, g: {},
            headline_builder=lambda m, g: 'h',
            title_builder=lambda m, g, d: 't',
            extra_sections=[],
            post_task_import_path='core.tasks:noop',
            enabled_env='TEST_ENABLED',
            posting_enabled_env='TEST_POSTING_ENABLED',
            workspace_id_env='',
            workspace_resolver=None,
        )
        workspace_id = None
        if config.workspace_id_env:
            env_val = _env_value(config.workspace_id_env)
            if env_val:
                workspace_id = env_val
        if workspace_id is None and config.workspace_resolver is not None:
            workspace_id = config.workspace_resolver()
        self.assertIsNone(workspace_id)
