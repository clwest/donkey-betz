"""Session 1200 — factory-entry instrumentation tests.

Verifies that ``deliverable_factory.create_deliverable`` emits a single
structured ``[DELIVERABLE-FACTORY-ENTRY]`` log line at function entry,
BEFORE any quality gate or DB work, so the inference accuracy watch can
count:

- (A) total create_deliverable calls (= ENTRY line count)
- (B) eligible-for-inference subset (= ENTRY lines where
  ``initiative_id_present=False``)
- (C) actual inference matches (= existing ``[INFERENCE-MATCH]`` count)

Required fields: ``agent``, ``workspace``, ``initiative_id_present``,
``tool_context_initiative_id_present``, ``initiative_source``,
``has_provenance``.

Run::

    python manage.py test core.tests.test_deliverable_factory_entry_log -v2
"""
from __future__ import annotations

from django.test import TestCase

from core.services.deliverable_factory import create_deliverable
from core.services.tool_context import tool_context_scope


class FactoryEntryLogTests(TestCase):
    """The entry log line must fire before gate rejection."""

    def test_entry_log_fires_before_gate_reject(self):
        with self.assertLogs(
            'core.services.deliverable_factory', level='INFO'
        ) as cm:
            result = create_deliverable(
                title='Smoke test entry log',
                content='x' * 400,
                agent_name='SomeAgent',
                metadata={'trigger_source': 'pa_tool'},
            )
        self.assertIsNone(result)
        entry_lines = [
            r for r in cm.output if '[DELIVERABLE-FACTORY-ENTRY]' in r
        ]
        self.assertEqual(
            len(entry_lines), 1,
            f'Expected exactly 1 ENTRY line; got {len(entry_lines)}: '
            f'{entry_lines}',
        )

    def test_entry_log_carries_required_fields(self):
        with self.assertLogs(
            'core.services.deliverable_factory', level='INFO'
        ) as cm:
            create_deliverable(
                title='Real title for required-fields test',
                content='x' * 50,  # short → gate rejects
                agent_name='ResearchAgent',
                workspace_id='b4503364-2573-4401-9e28-61a739e0ce50',
                initiative_id=None,
            )
        entry = [r for r in cm.output if '[DELIVERABLE-FACTORY-ENTRY]' in r][0]
        # required tokens
        self.assertIn('agent=ResearchAgent', entry)
        self.assertIn('workspace=b4503364-2573-4401-9e28-61a739e0ce50', entry)
        self.assertIn('initiative_id_present=False', entry)
        self.assertIn('tool_context_initiative_id_present=False', entry)
        self.assertIn('initiative_source=none', entry)
        self.assertIn('has_provenance=False', entry)

    def test_entry_log_when_initiative_explicit(self):
        with self.assertLogs(
            'core.services.deliverable_factory', level='INFO'
        ) as cm:
            create_deliverable(
                title='Real title for explicit-initiative test',
                content='x' * 50,
                agent_name='SomeAgent',
                workspace_id='ws-1',
                initiative_id='init-1',
                parent_execution_id='exec-1',
            )
        entry = [r for r in cm.output if '[DELIVERABLE-FACTORY-ENTRY]' in r][0]
        self.assertIn('initiative_id_present=True', entry)
        self.assertIn('initiative_source=explicit_kwarg', entry)
        self.assertIn('has_provenance=True', entry)

    def test_entry_log_detects_tool_context_initiative(self):
        with self.assertLogs(
            'core.services.deliverable_factory', level='INFO'
        ) as cm:
            with tool_context_scope({'initiative_id': 'tc-init-1'}):
                create_deliverable(
                    title='Real title for tool-context-init test',
                    content='x' * 50,
                    agent_name='SomeAgent',
                    workspace_id='ws-1',
                    initiative_id=None,
                )
        entry = [r for r in cm.output if '[DELIVERABLE-FACTORY-ENTRY]' in r][0]
        self.assertIn('initiative_id_present=False', entry)
        self.assertIn('tool_context_initiative_id_present=True', entry)
        self.assertIn('initiative_source=none', entry)
