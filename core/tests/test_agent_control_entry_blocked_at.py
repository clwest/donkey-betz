"""Session 1092: AgentControlEntry.blocked_at hygiene tests.

Locks in the save() override + the backfill command behavior, both of
which exist because CTOAgent's reliability audit surfaced AudioAgent's
entry as ``status='blocked', blocked_at=None`` — making "when was this
block originally set?" unanswerable.
"""

from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import AgentControlEntry


class TestSaveOverridePopulatesBlockedAt(TestCase):
    def test_new_blocked_entry_gets_blocked_at(self):
        before = timezone.now()
        entry = AgentControlEntry.objects.create(
            agent_name='TestNewBlock',
            status='blocked',
            reason='unit test',
        )
        entry.refresh_from_db()
        self.assertIsNotNone(entry.blocked_at, 'blocked_at must auto-populate')
        self.assertGreaterEqual(entry.blocked_at, before)

    def test_enabled_entry_does_not_get_blocked_at(self):
        entry = AgentControlEntry.objects.create(
            agent_name='TestEnabled',
            status='enabled',
        )
        entry.refresh_from_db()
        self.assertIsNone(entry.blocked_at, 'enabled rows must not get a timestamp')

    def test_transition_enabled_to_blocked_populates_blocked_at(self):
        entry = AgentControlEntry.objects.create(
            agent_name='TestTransition',
            status='enabled',
        )
        self.assertIsNone(entry.blocked_at)

        entry.status = 'blocked'
        entry.save()
        entry.refresh_from_db()
        self.assertIsNotNone(entry.blocked_at)

    def test_re_save_does_not_overwrite_existing_blocked_at(self):
        """Repeated re-blocks must preserve the historical first-block time."""
        entry = AgentControlEntry.objects.create(
            agent_name='TestNoOverwrite',
            status='blocked',
        )
        original_blocked_at = entry.blocked_at
        self.assertIsNotNone(original_blocked_at)

        # Simulate a later re-save (e.g. someone updating the reason)
        entry.reason = 'updated reason'
        entry.save()
        entry.refresh_from_db()

        self.assertEqual(
            entry.blocked_at, original_blocked_at,
            'blocked_at must not be overwritten on subsequent saves',
        )

    def test_blocked_at_persists_through_unblock(self):
        """When blocked → enabled, blocked_at stays as historical."""
        entry = AgentControlEntry.objects.create(
            agent_name='TestUnblockHistory',
            status='blocked',
        )
        original_blocked_at = entry.blocked_at

        entry.status = 'enabled'
        entry.reason = 'credits restored'
        entry.save()
        entry.refresh_from_db()

        self.assertEqual(entry.blocked_at, original_blocked_at)
        self.assertEqual(entry.status, 'enabled')


class TestBackfillCommand(TestCase):
    def test_backfill_only_touches_blocked_rows_with_null_blocked_at(self):
        from django.core.management import call_command
        from io import StringIO

        # Setup: one blocked row WITHOUT blocked_at (legacy gap), one
        # blocked row WITH blocked_at (already correct), one enabled row.
        # We bypass the save() override by using update() to seed the
        # legacy state directly.
        AgentControlEntry.objects.create(agent_name='LegacyGap', status='blocked')
        AgentControlEntry.objects.filter(agent_name='LegacyGap').update(blocked_at=None)

        AgentControlEntry.objects.create(agent_name='AlreadyTimestamped', status='blocked')
        # save() above set blocked_at — keep it.

        AgentControlEntry.objects.create(agent_name='EnabledRow', status='enabled')

        out = StringIO()
        call_command('backfill_agent_control_blocked_at', stdout=out)

        legacy = AgentControlEntry.objects.get(agent_name='LegacyGap')
        self.assertIsNotNone(legacy.blocked_at, 'legacy gap must be filled')

        already = AgentControlEntry.objects.get(agent_name='AlreadyTimestamped')
        # Pre-existing timestamp should still be set; not overwritten.
        self.assertIsNotNone(already.blocked_at)

        enabled = AgentControlEntry.objects.get(agent_name='EnabledRow')
        self.assertIsNone(enabled.blocked_at, 'enabled rows must not get backfilled')

    def test_backfill_dry_run_makes_no_changes(self):
        from django.core.management import call_command
        from io import StringIO

        AgentControlEntry.objects.create(agent_name='DryRunCanary', status='blocked')
        AgentControlEntry.objects.filter(agent_name='DryRunCanary').update(blocked_at=None)

        out = StringIO()
        call_command('backfill_agent_control_blocked_at', '--dry-run', stdout=out)

        canary = AgentControlEntry.objects.get(agent_name='DryRunCanary')
        self.assertIsNone(canary.blocked_at, 'dry-run must not write')

    def test_backfill_reports_no_work_when_clean(self):
        from django.core.management import call_command
        from io import StringIO

        AgentControlEntry.objects.create(agent_name='AlreadyOK', status='blocked')

        out = StringIO()
        call_command('backfill_agent_control_blocked_at', stdout=out)
        self.assertIn('No backfill needed', out.getvalue())
