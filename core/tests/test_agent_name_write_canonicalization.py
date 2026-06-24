"""Session 1226 P1 — agent_name write-time canonicalization tests.

Companion enforcement for migration 0365_session_1226_agent_name_canonicalization.
Migration cleans up history; this layer prevents future drift by canonicalizing
agent_name on EVERY `create_deliverable` call before gates run, before dedupe,
before persistence.

Verifies:
  - `rigby` → `Rigby` on write
  - `ClaudeCode` → `claude-code` on write
  - Unknown agent_names pass through unchanged (strict alias surface)
  - Empty/None agent_name returns ''
  - The persisted Deliverable.agent_name reflects the canonical spelling
"""
from __future__ import annotations

from django.test import TestCase

from core.services.deliverable_factory import (
    _AGENT_NAME_ALIASES,
    _canonicalize_agent_name,
    create_deliverable,
)


class CanonicalizeHelperTests(TestCase):
    """Pure-function unit tests on _canonicalize_agent_name."""

    def test_rigby_lowercase_maps_to_titlecase(self):
        self.assertEqual(_canonicalize_agent_name('rigby'), 'Rigby')

    def test_claudecode_maps_to_hyphenated_lowercase(self):
        self.assertEqual(_canonicalize_agent_name('ClaudeCode'), 'claude-code')

    def test_unknown_agent_passes_through(self):
        self.assertEqual(_canonicalize_agent_name('ResearchAgent'), 'ResearchAgent')

    def test_already_canonical_passes_through(self):
        self.assertEqual(_canonicalize_agent_name('Rigby'), 'Rigby')
        self.assertEqual(_canonicalize_agent_name('claude-code'), 'claude-code')

    def test_empty_returns_empty(self):
        self.assertEqual(_canonicalize_agent_name(''), '')
        self.assertEqual(_canonicalize_agent_name(None), '')  # type: ignore

    def test_alias_map_locked_to_known_set(self):
        """If a future change adds a third alias, both this test and
        migration 0365's _ALIAS_MAP must be updated together."""
        self.assertEqual(
            _AGENT_NAME_ALIASES,
            {
                'rigby': 'Rigby',
                'ClaudeCode': 'claude-code',
            },
        )


class CreateDeliverableCanonicalizationTests(TestCase):
    """Integration: persisted agent_name reflects canonical spelling."""

    def test_create_with_rigby_lowercase_persists_titlecase(self):
        result = create_deliverable(
            title='Probe Rigby lowercase write',
            content='x' * 400,
            agent_name='rigby',
            metadata={'trigger_source': 'pa_tool'},
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.agent_name, 'Rigby')

    def test_create_with_ClaudeCode_persists_hyphenated(self):
        result = create_deliverable(
            title='Probe ClaudeCode write',
            content='x' * 400,
            agent_name='ClaudeCode',
            metadata={'trigger_source': 'pa_tool'},
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.agent_name, 'claude-code')

    def test_create_with_unknown_passes_through(self):
        result = create_deliverable(
            title='Probe ResearchAgent write',
            content='x' * 400,
            agent_name='ResearchAgent',
            metadata={'trigger_source': 'pa_tool', 'sources_count': 3},
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.agent_name, 'ResearchAgent')

    def test_create_with_already_canonical_passes_through(self):
        result = create_deliverable(
            title='Probe already-canonical Rigby',
            content='x' * 400,
            agent_name='Rigby',
            metadata={'trigger_source': 'pa_tool'},
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.agent_name, 'Rigby')
