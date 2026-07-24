"""Session 2945 — Ledger #38 batch 4: dry_run alignment for content_tool.run_cleanup.

Closes content_tool's last unaligned mutation. The handler dry_run branch
at ``core/services/td_handlers_content.py`` (run_cleanup) now calls the
shared ``_gather_cleanup_preview`` helper in ``core/tasks_misc.py`` — same
helper the real ``_impl_cleanup_stale_content`` task calls for the archive
filter. Single source of truth: preview count/breakdown cannot drift from
what the real task will archive.

Envelope shape (dry_run branch):

- ``dry_run: True``
- ``would_action: 'dispatch_celery'``
- ``would_task: 'cleanup_stale_content'``
- ``no_writes: True``
- ``would_archive_count: N`` + ``top_by_type`` + ``top_by_category`` preview
- Zero Celery dispatch / zero DB writes

Extends S2942 (blog_tool + feedback_tool) + S2943 (bulk_archive_published) +
S2944 (bulk_archive + generate_newsletter) Ledger #38 arc. Per-action
alignment count in ``content_tool`` grows from 3 → 4 (all mutations aligned).
"""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models_deliverables import Deliverable
from core.services.tool_dispatcher import get_tool_dispatcher
from core.tasks_misc import _gather_cleanup_preview

User = get_user_model()


def _run(tool_name: str, payload: dict, user_id=None) -> dict:
    dispatcher = get_tool_dispatcher()
    handler = dispatcher._tool_handlers[tool_name]
    return handler(
        tool_name=tool_name,
        payload=payload,
        user_id=user_id,
        trace_id='test-s2945-trace',
    )


# ── run_cleanup dry_run envelope ────────────────────────────────────────────


class RunCleanupDryRunTests(TestCase):
    """run_cleanup dry_run envelope + no-dispatch/no-writes guarantees."""

    def setUp(self):
        self.user = User.objects.create(
            username='s2945-cleanup', email='s2945@example.com',
        )
        old = timezone.now() - timedelta(days=30)
        # 3 stale draft deliverables (>7 days old, matches default cleanup filter)
        for i in range(3):
            d = Deliverable.objects.create(
                title=f'S2945 stale draft #{i}',
                slug=f's2945-stale-draft-{i}',
                agent_name='TestAgent',
                content='body',
                status='draft',
                category='TestCategoryS2945',
                deliverable_type='test_type_a',
                user=self.user,
                is_saved=False,
            )
            Deliverable.objects.filter(pk=d.pk).update(created_at=old)
        # 2 fresh drafts (< 7 days old — should NOT match cleanup filter)
        for i in range(2):
            Deliverable.objects.create(
                title=f'S2945 fresh draft #{i}',
                slug=f's2945-fresh-draft-{i}',
                agent_name='TestAgent',
                content='body',
                status='draft',
                category='TestCategoryS2945',
                deliverable_type='test_type_b',
                user=self.user,
                is_saved=False,
            )
        # 1 saved stale draft (is_saved=True — should NOT match)
        d_saved = Deliverable.objects.create(
            title='S2945 saved stale',
            slug='s2945-saved-stale',
            agent_name='TestAgent',
            content='body',
            status='draft',
            category='TestCategoryS2945',
            deliverable_type='test_type_a',
            user=self.user,
            is_saved=True,
        )
        Deliverable.objects.filter(pk=d_saved.pk).update(created_at=old)

    def test_dry_run_default_true_returns_s2942_envelope(self):
        """Default (no dry_run in payload) is TRUE; S2942 sentinel fields present."""
        with patch('core.tasks.cleanup_stale_content.delay') as mock_dispatch:
            result = _run('content_tool', {'action': 'run_cleanup'})

        self.assertEqual(result['gateway'], 'content_tool')
        self.assertEqual(result['action'], 'run_cleanup')
        self.assertTrue(result['dry_run'], 'dry_run must default TRUE')
        self.assertEqual(result['mode'], 'dry_run')
        self.assertEqual(result['would_action'], 'dispatch_celery')
        self.assertEqual(result['would_task'], 'cleanup_stale_content')
        self.assertTrue(result['no_writes'])
        mock_dispatch.assert_not_called()

    def test_dry_run_true_explicit_returns_would_envelope(self):
        """Explicit dry_run=True behaves identically to default."""
        with patch('core.tasks.cleanup_stale_content.delay') as mock_dispatch:
            result = _run('content_tool', {'action': 'run_cleanup', 'dry_run': True})

        self.assertTrue(result['dry_run'])
        self.assertEqual(result['would_action'], 'dispatch_celery')
        self.assertTrue(result['no_writes'])
        mock_dispatch.assert_not_called()

    def test_dry_run_preview_matches_actual_filter(self):
        """Preview count MUST equal what the real task would archive
        (single source of truth via _gather_cleanup_preview).
        Setup has 3 stale drafts, 2 fresh drafts, 1 saved stale.
        Filter should match only the 3 stale un-saved drafts.
        """
        with patch('core.tasks.cleanup_stale_content.delay'):
            result = _run('content_tool', {'action': 'run_cleanup'})

        self.assertEqual(result['total_found'], 3)
        self.assertEqual(result['would_archive_count'], 3)
        self.assertEqual(result['safe_statuses'], ['ready', 'draft'])
        self.assertEqual(result['cutoff_days'], 7)

    def test_dry_run_no_db_writes(self):
        """dry_run branch leaves all rows unchanged (no status transitions)."""
        before_drafts = Deliverable.objects.filter(status='draft').count()
        before_archived = Deliverable.objects.filter(status='archived').count()

        with patch('core.tasks.cleanup_stale_content.delay'):
            _run('content_tool', {'action': 'run_cleanup'})

        after_drafts = Deliverable.objects.filter(status='draft').count()
        after_archived = Deliverable.objects.filter(status='archived').count()
        self.assertEqual(before_drafts, after_drafts)
        self.assertEqual(before_archived, after_archived)

    def test_dry_run_preview_includes_top_breakdowns(self):
        """Envelope carries top_by_type + top_by_category previews (Option B value-add)."""
        with patch('core.tasks.cleanup_stale_content.delay'):
            result = _run('content_tool', {'action': 'run_cleanup'})

        self.assertIn('top_by_type', result)
        self.assertIn('top_by_category', result)
        # Should show test_type_a (3 stale drafts) — test_type_b is fresh, filtered out
        type_counts = {row['deliverable_type']: row['count'] for row in result['top_by_type']}
        self.assertEqual(type_counts.get('test_type_a'), 3)

    def test_dry_run_message_carries_would_count_summary(self):
        """Message includes N/M summary + explicit dispatch instruction."""
        with patch('core.tasks.cleanup_stale_content.delay'):
            result = _run('content_tool', {'action': 'run_cleanup'})

        self.assertIn('dry_run=true', result['message'])
        self.assertIn('3 of 3', result['message'])
        self.assertIn('No Celery task enqueued', result['message'])
        self.assertIn('Set dry_run=false', result['message'])

    def test_dry_run_false_dispatches_celery(self):
        """Regression sanity — dry_run=false enqueues the real Celery task."""
        with patch('core.tasks.cleanup_stale_content.delay') as mock_dispatch:
            fake_task = type('FakeTask', (), {'id': 'fake-task-uuid-s2945'})()
            mock_dispatch.return_value = fake_task

            result = _run('content_tool', {'action': 'run_cleanup', 'dry_run': False})

        self.assertEqual(result['mode'], 'async')
        self.assertEqual(result['task_id'], 'fake-task-uuid-s2945')
        mock_dispatch.assert_called_once()

    def test_dry_run_invalid_statuses_returns_handler_error(self):
        """Statuses stripped to empty by safety filter → invalid_params error, not envelope."""
        with patch('core.tasks.cleanup_stale_content.delay') as mock_dispatch:
            result = _run(
                'content_tool',
                {'action': 'run_cleanup', 'statuses': ['published', 'archived']},
            )

        self.assertFalse(result.get('success'))
        self.assertEqual(result.get('error_code'), 'invalid_params')
        mock_dispatch.assert_not_called()

    def test_dry_run_autofilled_empty_statuses_coerces_to_default(self):
        """S2945 2nd-trigger fix of S2944 statuses-autofill quirk.

        GPT-5.2 autofills ``statuses:[]`` (empty list) where the schema
        expects omission. Before the fix: empty list survived
        ``payload.get('statuses', default)`` and reached the safety filter,
        producing an invalid_params error. After the fix: helper's
        ``if not statuses`` treats empty-list as "use default".
        """
        with patch('core.tasks.cleanup_stale_content.delay') as mock_dispatch:
            result = _run('content_tool', {'action': 'run_cleanup', 'statuses': []})

        self.assertTrue(result.get('dry_run'), 'empty statuses must NOT produce error envelope')
        self.assertEqual(result['safe_statuses'], ['ready', 'draft'], 'empty must coerce to default')
        self.assertEqual(result['would_action'], 'dispatch_celery')
        mock_dispatch.assert_not_called()

    def test_dry_run_protected_types_excludes_matching_rows(self):
        """protected_types filter excludes matching deliverables from would-archive count."""
        with patch('core.tasks.cleanup_stale_content.delay'):
            result = _run(
                'content_tool',
                {'action': 'run_cleanup', 'protected_types': ['test_type_a']},
            )

        # All 3 stale drafts are test_type_a → excluded → 0 remain
        self.assertEqual(result['would_archive_count'], 0)
        self.assertEqual(result['total_found'], 0)


# ── _gather_cleanup_preview helper (single-source-of-truth guarantee) ───────


class GatherCleanupPreviewHelperTests(TestCase):
    """Helper returns identical filter output the real _impl_cleanup_stale_content uses."""

    def setUp(self):
        self.user = User.objects.create(
            username='s2945-helper', email='s2945helper@example.com',
        )
        old = timezone.now() - timedelta(days=14)
        for i in range(4):
            d = Deliverable.objects.create(
                title=f'S2945 helper stale #{i}',
                slug=f's2945-helper-stale-{i}',
                agent_name='HelperAgent',
                content='body',
                status='ready',
                category='HelperCatS2945',
                deliverable_type='helper_type',
                user=self.user,
            )
            Deliverable.objects.filter(pk=d.pk).update(created_at=old)

    def test_helper_returns_no_writes(self):
        """Helper is read-only — no status transitions."""
        preview = _gather_cleanup_preview(cutoff_days=7)
        self.assertEqual(preview['total_found'], 4)
        self.assertEqual(preview['would_archive_count'], 4)
        # Verify nothing archived
        archived = Deliverable.objects.filter(status='archived').count()
        self.assertEqual(archived, 0)

    def test_helper_respects_cap(self):
        """cap limits would_archive_count to min(total, cap)."""
        preview = _gather_cleanup_preview(cutoff_days=7, cap=2)
        self.assertEqual(preview['total_found'], 4)
        self.assertEqual(preview['would_archive_count'], 2)
        self.assertEqual(len(preview['archive_ids']), 2)

    def test_helper_invalid_statuses_returns_error(self):
        """Empty safe_statuses returns error dict, not None."""
        preview = _gather_cleanup_preview(statuses=['published', 'archived'])
        self.assertEqual(preview.get('error'), 'no_valid_statuses')

    def test_helper_zero_matches_returns_empty_shape(self):
        """No matching rows returns zero counts, not None."""
        preview = _gather_cleanup_preview(cutoff_days=999)  # far-future cutoff → 0 matches
        self.assertEqual(preview['total_found'], 0)
        self.assertEqual(preview['would_archive_count'], 0)
        self.assertEqual(preview['archive_ids'], [])
