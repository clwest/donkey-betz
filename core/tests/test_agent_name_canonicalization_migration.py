"""Session 1226 P1 — agent_name canonicalization migration tests.

Verifies the data-only function `canonicalize_agent_names` from migration
`core.migrations.0365_session_1226_agent_name_canonicalization` correctly
rewrites the two alias variants surfaced by the Rigby+Claude audit.

This test does NOT run `manage.py migrate` (that would require a fresh
migration cycle). Instead it imports the function directly and runs it
against an in-test fixture, mirroring the migration's behavior.
"""
from __future__ import annotations

import importlib

from django.test import TestCase

# Migration module names start with a digit, which Python's `import`
# statement can't handle directly. Use importlib to load it.
migration_module = importlib.import_module(
    'core.migrations.0365_session_1226_agent_name_canonicalization'
)


class AgentNameCanonicalizationTests(TestCase):
    def _make(self, agent_name, title='probe', content='x' * 400):
        from core.models_deliverables import Deliverable
        return Deliverable.objects.create(
            title=title,
            content=content,
            agent_name=agent_name,
            user=None,
        )

    def _fake_apps_facade(self):
        """The migration uses `apps.get_model('core', 'Deliverable')`.
        We can replicate that by giving it an object with a `get_model`
        method that returns the real Deliverable class.
        """
        from core.models_deliverables import Deliverable

        class _Facade:
            @staticmethod
            def get_model(app_label, model_name):
                assert (app_label, model_name) == ('core', 'Deliverable'), \
                    f'unexpected get_model call: {app_label}.{model_name}'
                return Deliverable

        return _Facade()

    def test_rigby_lowercase_normalizes_to_titlecase(self):
        self._make('rigby', title='rigby-1')
        self._make('rigby', title='rigby-2')
        already_canonical = self._make('Rigby', title='already-canonical')

        migration_module.canonicalize_agent_names(
            self._fake_apps_facade(), schema_editor=None,
        )

        from core.models_deliverables import Deliverable
        self.assertEqual(Deliverable.objects.filter(agent_name='rigby').count(), 0)
        self.assertEqual(Deliverable.objects.filter(agent_name='Rigby').count(), 3)
        # Already-canonical row was preserved
        already_canonical.refresh_from_db()
        self.assertEqual(already_canonical.agent_name, 'Rigby')

    def test_claudecode_normalizes_to_hyphenated_lowercase(self):
        self._make('ClaudeCode', title='cc-1')
        self._make('ClaudeCode', title='cc-2')
        self._make('claude-code', title='already-canonical-1')

        migration_module.canonicalize_agent_names(
            self._fake_apps_facade(), schema_editor=None,
        )

        from core.models_deliverables import Deliverable
        self.assertEqual(Deliverable.objects.filter(agent_name='ClaudeCode').count(), 0)
        self.assertEqual(Deliverable.objects.filter(agent_name='claude-code').count(), 3)

    def test_both_aliases_in_same_pass(self):
        self._make('rigby', title='rigby-1')
        self._make('ClaudeCode', title='cc-1')
        self._make('ClaudeCode', title='cc-2')

        migration_module.canonicalize_agent_names(
            self._fake_apps_facade(), schema_editor=None,
        )

        from core.models_deliverables import Deliverable
        self.assertEqual(Deliverable.objects.filter(agent_name='rigby').count(), 0)
        self.assertEqual(Deliverable.objects.filter(agent_name='ClaudeCode').count(), 0)
        self.assertEqual(Deliverable.objects.filter(agent_name='Rigby').count(), 1)
        self.assertEqual(Deliverable.objects.filter(agent_name='claude-code').count(), 2)

    def test_idempotent_when_no_aliases_present(self):
        """Running the migration on already-clean data should be a noop."""
        self._make('Rigby', title='already-canonical-rigby')
        self._make('claude-code', title='already-canonical-cc')

        from core.models_deliverables import Deliverable
        before = list(Deliverable.objects.values_list('id', 'agent_name'))

        migration_module.canonicalize_agent_names(
            self._fake_apps_facade(), schema_editor=None,
        )

        after = list(Deliverable.objects.values_list('id', 'agent_name'))
        self.assertEqual(sorted(before), sorted(after))

    def test_unrelated_agents_untouched(self):
        """Rows with agent_name outside the alias map should not change."""
        self._make('ResearchAgent', title='r-1')
        self._make('ContentWriterAgent', title='cw-1')
        self._make('rigby', title='rigby-target')

        migration_module.canonicalize_agent_names(
            self._fake_apps_facade(), schema_editor=None,
        )

        from core.models_deliverables import Deliverable
        self.assertEqual(Deliverable.objects.filter(agent_name='ResearchAgent').count(), 1)
        self.assertEqual(Deliverable.objects.filter(agent_name='ContentWriterAgent').count(), 1)
        self.assertEqual(Deliverable.objects.filter(agent_name='Rigby').count(), 1)
