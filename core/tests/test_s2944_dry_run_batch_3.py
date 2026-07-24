"""Session 2944 — Ledger #38 batch 3: dry_run alignment for content_tool.

Bundles two mutation actions:

1. ``content_tool.generate_newsletter`` — native dry_run short-circuit at
   ``core/services/td_handlers_content.py:4707+`` (gathers cluster evidence,
   returns preview, does NOT enqueue Celery task or call LLM). Envelope
   now carries the S2942 sentinel fields alongside the existing preview
   data — pattern-aligned with the ``generate_blog`` dispatch_celery shape.

2. ``content_tool.bulk_archive`` — dry_run branch at
   ``core/services/td_handlers_content.py:5044+`` (user-scoped bulk archive
   over ready/draft/completed statuses). Envelope now carries the S2942
   sentinel fields — pattern-aligned with the S2943 ``bulk_archive_published``
   ship.

Envelope shape (both actions):

- ``dry_run: True``
- ``would_action: <action-family-verb>``
- ``no_writes: True``
- Zero Celery dispatch / zero DB writes

Extends S2942 (blog_tool + feedback_tool) + S2943 (bulk_archive_published)
Ledger #38 arc. Per-action alignment count in ``content_tool`` grows from
1 (bulk_archive_published) to 3 (bulk_archive_published + bulk_archive +
generate_newsletter). Doc-level scoreboard ``per_mutation_safety.
dry_run_supported`` stays at 3 (content_tool_validation.md already promoted
at S2943).
"""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models_deliverables import Deliverable
from core.services.tool_dispatcher import get_tool_dispatcher

User = get_user_model()


def _run(tool_name: str, payload: dict, user_id=None) -> dict:
    dispatcher = get_tool_dispatcher()
    handler = dispatcher._tool_handlers[tool_name]
    return handler(
        tool_name=tool_name,
        payload=payload,
        user_id=user_id,
        trace_id='test-s2944-trace',
    )


# ── generate_newsletter ─────────────────────────────────────────────────────

_FAKE_EVIDENCE = {
    'clusters': [
        {'name': 'cluster-A'},
        {'name': 'cluster-B'},
        {'name': 'cluster-C'},
        {'name': 'cluster-D'},
    ],
    'evidence_block': 'evidence-block-body ' * 50,  # non-empty preview text
}


class GenerateNewsletterDryRunTests(TestCase):
    """generate_newsletter dry_run envelope + no-dispatch guarantee."""

    def test_dry_run_true_returns_s2942_envelope(self):
        """All 4 S2942 sentinel fields present + no Celery dispatch."""
        with patch(
            'core.tasks_content._gather_newsletter_evidence',
            return_value=_FAKE_EVIDENCE,
        ), patch(
            'core.tasks.generate_operator_edge_newsletter.apply_async'
        ) as mock_dispatch:
            result = _run(
                'content_tool',
                {'action': 'generate_newsletter', 'dry_run': True, 'hours': 48, 'cluster_limit': 4},
            )

        self.assertEqual(result['gateway'], 'content_tool')
        self.assertEqual(result['action'], 'generate_newsletter')
        self.assertTrue(result['dry_run'], 'dry_run must be echoed True')
        self.assertEqual(result['would_action'], 'dispatch_celery')
        self.assertEqual(result['would_task'], 'generate_operator_edge_newsletter')
        self.assertTrue(result['no_writes'])
        self.assertIn('No Celery task enqueued', result['message'])
        mock_dispatch.assert_not_called()

    def test_dry_run_true_preserves_evidence_preview(self):
        """Existing preview data (clusters_found, top_clusters, evidence_preview) survives alignment."""
        with patch(
            'core.tasks_content._gather_newsletter_evidence',
            return_value=_FAKE_EVIDENCE,
        ), patch(
            'core.tasks.generate_operator_edge_newsletter.apply_async'
        ):
            result = _run(
                'content_tool',
                {'action': 'generate_newsletter', 'dry_run': True},
            )

        self.assertEqual(result['clusters_found'], 4)
        self.assertEqual(result['top_clusters'], ['cluster-A', 'cluster-B', 'cluster-C'])
        self.assertTrue(result['evidence_preview'].startswith('evidence-block-body'))
        self.assertLessEqual(len(result['evidence_preview']), 2000)

    def test_dry_run_false_dispatches_celery(self):
        """Regression sanity — non-dry-run still enqueues the Celery task."""
        with patch(
            'core.tasks.generate_operator_edge_newsletter.apply_async'
        ) as mock_dispatch:
            fake_task = type('FakeTask', (), {'id': 'fake-task-uuid-123'})()
            mock_dispatch.return_value = fake_task

            result = _run(
                'content_tool',
                {'action': 'generate_newsletter', 'dry_run': False},
            )

        self.assertEqual(result['mode'], 'async')
        self.assertEqual(result['task_id'], 'fake-task-uuid-123')
        mock_dispatch.assert_called_once()


# ── bulk_archive ────────────────────────────────────────────────────────────


class BulkArchiveDryRunTests(TestCase):
    """bulk_archive dry_run envelope + no-writes guarantee."""

    def setUp(self):
        self.user = User.objects.create(
            username='s2944-bulk', email='s2944bulk@example.com',
        )
        # Create 4 draft deliverables that would match a broad bulk_archive.
        for i in range(4):
            Deliverable.objects.create(
                title=f'S2944 draft #{i}',
                slug=f's2944-draft-{i}',
                agent_name='TestAgent',
                content='body',
                status='draft',
                category='TestCategoryS2944',
                user=self.user,
            )

    def _payload(self, **overrides) -> dict:
        base = {
            'action': 'bulk_archive',
            'category': 'TestCategoryS2944',
        }
        base.update(overrides)
        return base

    def test_dry_run_true_default_returns_would_envelope(self):
        """Default dry_run is TRUE; envelope carries S2942-aligned fields, no writes."""
        result = _run('content_tool', self._payload(), user_id=self.user.id)

        self.assertEqual(result['action'], 'bulk_archive')
        self.assertTrue(result['dry_run'], 'dry_run must default TRUE')
        self.assertEqual(result['would_action'], 'archive')
        self.assertEqual(result['would_change_to'], 'archived')
        self.assertEqual(result['would_archive_count'], 4)
        self.assertTrue(result['no_writes'])
        self.assertIn('dry_run=true', result['message'])
        self.assertIn('No writes performed', result['message'])

        after_drafts = Deliverable.objects.filter(
            category='TestCategoryS2944', status='draft',
        ).count()
        self.assertEqual(after_drafts, 4, 'dry_run=true must leave all rows unchanged')

    def test_dry_run_true_explicit_returns_would_envelope(self):
        """Explicit dry_run=True behaves identically to default."""
        result = _run(
            'content_tool',
            self._payload(dry_run=True),
            user_id=self.user.id,
        )
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['would_action'], 'archive')
        self.assertTrue(result['no_writes'])

        after_drafts = Deliverable.objects.filter(
            category='TestCategoryS2944', status='draft',
        ).count()
        self.assertEqual(after_drafts, 4)

    def test_dry_run_false_without_confirm_stays_safe(self):
        """dry_run=False without confirm=true is coerced back to dry_run — no writes.

        Uses ``require_write_authorization`` belt-and-suspenders (Session 1228 PR-A).
        """
        result = _run(
            'content_tool',
            self._payload(dry_run=False),
            user_id=self.user.id,
        )
        # Handler runs the dry_run branch — envelope + no writes.
        self.assertTrue(result['dry_run'], 'dry_run must be coerced TRUE without confirm')
        self.assertTrue(result['no_writes'])
        self.assertEqual(result['would_action'], 'archive')

        after_drafts = Deliverable.objects.filter(
            category='TestCategoryS2944', status='draft',
        ).count()
        self.assertEqual(after_drafts, 4, 'missing confirm must not archive anything')

    def test_dry_run_false_with_confirm_actually_archives(self):
        """dry_run=False + confirm=True executes the archive (regression sanity)."""
        result = _run(
            'content_tool',
            self._payload(dry_run=False, confirm=True),
            user_id=self.user.id,
        )
        self.assertEqual(result['action'], 'bulk_archive')
        self.assertEqual(result['archived_count'], 4)

        after_drafts = Deliverable.objects.filter(
            category='TestCategoryS2944', status='draft',
        ).count()
        after_archived = Deliverable.objects.filter(
            category='TestCategoryS2944', status='archived',
        ).count()
        self.assertEqual(after_drafts, 0)
        self.assertEqual(after_archived, 4)
