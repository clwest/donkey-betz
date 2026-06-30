"""Session 1263 — Claude Code Agent row consolidation tests.

Validates two surfaces:

1. **Canonicalization at deliverable_factory._synthesize_pa_execution_receipt** —
   without the S1263 fix, callers passing aliased names like
   ``'ClaudeCode'`` would spawn a fresh Agent row (the root cause that
   re-created the duplicate after S1226 migration 0365). With the fix,
   the canonical ``'claude-code'`` row is reused.

2. **Migration 0374 consolidation behavior** — invoked directly via
   importlib (the migration module's filename starts with digits and
   isn't a standard Python import name). Verifies FK repointing,
   ``owner_agent`` string normalization, the safety gate, idempotent
   skip when the duplicate is absent, and the defensive
   rename-in-place branch when only the duplicate exists on a fresh DB.

Real PostgreSQL (per the S1234 memory rule).

Run::

    .venv/bin/python manage.py test \\
        core.tests.test_claude_code_agent_consolidation_s1263 \\
        -v 2 --keepdb
"""

from __future__ import annotations

import importlib
from unittest.mock import patch

from django.apps import apps as django_apps
from django.db.models.query import QuerySet
from django.test import TestCase

from core.models import Agent, AgentExecution


CANONICAL = 'claude-code'
DUPLICATE = 'ClaudeCode'

MIGRATION_MODULE_PATH = (
    'core.migrations.0374_session_1263_consolidate_claude_code_agent'
)


def _ensure_canonical_row() -> Agent:
    agent, _ = Agent.objects.get_or_create(
        name=CANONICAL,
        defaults={'agent_type': 'tool_direct', 'is_active': True},
    )
    return agent


def _ensure_duplicate_row() -> Agent:
    agent, _ = Agent.objects.get_or_create(
        name=DUPLICATE,
        defaults={'agent_type': 'tool_direct', 'is_active': True},
    )
    return agent


def _run_migration():
    """Invoke the migration's RunPython callable against the live apps."""
    mod = importlib.import_module(MIGRATION_MODULE_PATH)
    mod.consolidate_claude_code_agent(django_apps, None)


# ═════════════════════════════════════════════════════════════════════
# §1 — _synthesize_pa_execution_receipt canonicalization (Phase 2 code fix)
# ═════════════════════════════════════════════════════════════════════


class SynthesizePaReceiptCanonicalizationTests(TestCase):
    """The deliverable_factory.py:697 fix: alias names route to canonical row."""

    def setUp(self):
        _ensure_canonical_row()
        # Confirm no duplicate exists at test start.
        Agent.objects.filter(name=DUPLICATE).delete()

    def test_aliased_agent_name_routes_to_canonical_row(self):
        """Calling _synthesize_pa_execution_receipt with 'ClaudeCode' must NOT
        spawn a new Agent row. The receipt's agent FK must point at
        the canonical 'claude-code' row.
        """
        from core.services.deliverable_factory import _synthesize_pa_execution_receipt

        receipt_id = _synthesize_pa_execution_receipt(
            agent_name=DUPLICATE,  # alias — should canonicalize
            task_summary='S1263 contract test',
            trace_id=None,
            user=None,
            workspace_id=None,
            metadata={'test': True},
        )
        self.assertIsNotNone(receipt_id, '_synthesize_pa_execution_receipt returned None')

        receipt = AgentExecution.objects.get(id=receipt_id)
        self.assertEqual(
            receipt.agent.name, CANONICAL,
            'aliased name must route to canonical Agent row',
        )

        # Critical assertion — the duplicate row was NOT spawned.
        self.assertFalse(
            Agent.objects.filter(name=DUPLICATE).exists(),
            "_synthesize_pa_execution_receipt(agent_name='ClaudeCode') spawned a "
            "fresh 'ClaudeCode' Agent row — canonicalization fix broken.",
        )

    def test_canonical_agent_name_passes_through(self):
        """Passing the canonical name directly works unchanged."""
        from core.services.deliverable_factory import _synthesize_pa_execution_receipt

        receipt_id = _synthesize_pa_execution_receipt(
            agent_name=CANONICAL,
            task_summary='S1263 contract test passthrough',
            trace_id=None,
            user=None,
            workspace_id=None,
            metadata={},
        )
        self.assertIsNotNone(receipt_id)
        receipt = AgentExecution.objects.get(id=receipt_id)
        self.assertEqual(receipt.agent.name, CANONICAL)

    def test_unknown_agent_name_passes_through_unchanged(self):
        """The alias map is intentionally not an opinion engine.
        Unknown names should NOT be coerced — only mapped aliases."""
        from core.services.deliverable_factory import _synthesize_pa_execution_receipt

        receipt_id = _synthesize_pa_execution_receipt(
            agent_name='SomeUnusualAgent',
            task_summary='S1263 contract test unknown',
            trace_id=None,
            user=None,
            workspace_id=None,
            metadata={},
        )
        self.assertIsNotNone(receipt_id)
        receipt = AgentExecution.objects.get(id=receipt_id)
        self.assertEqual(receipt.agent.name, 'SomeUnusualAgent')


# ═════════════════════════════════════════════════════════════════════
# §2 — Migration 0374 consolidation behavior
# ═════════════════════════════════════════════════════════════════════


class Migration0374ConsolidationTests(TestCase):
    """Forward migration: FK repoint + owner_agent normalize + dup delete."""

    def setUp(self):
        # Wipe both rows so each test sets up its own fixture state.
        Agent.objects.filter(name__in=(CANONICAL, DUPLICATE)).delete()

    def test_repoints_fk_and_normalizes_owner_agent_then_deletes_dup(self):
        canonical = _ensure_canonical_row()
        duplicate = _ensure_duplicate_row()

        for i in range(2):
            AgentExecution.objects.create(
                agent=duplicate,
                task=f'pre-migration test row {i}',
                status='completed',
                owner_agent='ClaudeCode',
            )
        self.assertEqual(
            AgentExecution.objects.filter(agent=duplicate).count(), 2
        )

        _run_migration()

        # Duplicate row deleted; canonical row gained the executions
        self.assertFalse(Agent.objects.filter(name=DUPLICATE).exists())
        self.assertEqual(
            AgentExecution.objects.filter(agent=canonical).count(), 2,
            'all repointed AgentExecution rows must reference canonical',
        )
        # owner_agent string normalized on the repointed rows
        self.assertEqual(
            AgentExecution.objects.filter(
                owner_agent='ClaudeCode'
            ).count(), 0,
            "owner_agent='ClaudeCode' rows must be normalized to "
            "'claude-code' by the migration",
        )
        self.assertEqual(
            AgentExecution.objects.filter(
                owner_agent='claude-code', agent=canonical
            ).count(), 2,
        )

    def test_idempotent_when_duplicate_missing(self):
        """Replays / fresh DBs that lack the duplicate row must skip cleanly."""
        _ensure_canonical_row()
        _run_migration()
        self.assertTrue(Agent.objects.filter(name=CANONICAL).exists())
        self.assertFalse(Agent.objects.filter(name=DUPLICATE).exists())

    def test_renames_in_place_when_canonical_missing(self):
        """Defensive branch: if only duplicate exists (fresh DB before
        any claude_code_engineer_task dispatch), the migration renames
        it in-place rather than dropping history."""
        Agent.objects.filter(name=CANONICAL).delete()
        duplicate = _ensure_duplicate_row()
        AgentExecution.objects.create(
            agent=duplicate,
            task='history must survive rename',
            status='completed',
            owner_agent='ClaudeCode',
        )

        _run_migration()

        # The original row is now renamed to the canonical name.
        renamed = Agent.objects.get(id=duplicate.id)
        self.assertEqual(renamed.name, CANONICAL)
        # No second 'claude-code' row was created.
        self.assertEqual(
            Agent.objects.filter(name=CANONICAL).count(), 1
        )
        # History preserved on the renamed row.
        self.assertEqual(
            AgentExecution.objects.filter(agent=renamed).count(), 1
        )

    def test_safety_gate_blocks_delete_on_orphan_reference(self):
        """If a reverse-FK still points at the duplicate after the
        repoint step (e.g. an unaccounted model that future code adds),
        the migration must RAISE rather than orphan the references.

        Simulated by patching ``QuerySet.update`` to no-op the FK
        update on AgentExecution. The owner_agent string normalization
        still runs (it filters on owner_agent, not agent), so the
        safety gate sees a remaining reference and aborts.
        """
        _ensure_canonical_row()
        duplicate = _ensure_duplicate_row()
        AgentExecution.objects.create(
            agent=duplicate,
            task='will not be repointed',
            status='completed',
            owner_agent='ClaudeCode',
        )

        original_update = QuerySet.update

        def selective_no_op_update(self, *args, **kwargs):
            if (
                'agent' in kwargs
                and self.model.__name__ == 'AgentExecution'
            ):
                return 0
            return original_update(self, *args, **kwargs)

        with patch.object(QuerySet, 'update', selective_no_op_update):
            with self.assertRaises(RuntimeError) as ctx:
                _run_migration()
            self.assertIn('ABORT', str(ctx.exception))
            self.assertIn('reverse-FK references', str(ctx.exception))

        # Duplicate row was NOT deleted (safety gate worked).
        self.assertTrue(Agent.objects.filter(name=DUPLICATE).exists())
