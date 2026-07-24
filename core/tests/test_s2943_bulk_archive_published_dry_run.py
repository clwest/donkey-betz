"""Session 2943 — Ledger #38 batch 2: dry_run affordance for content_tool.bulk_archive_published.

Extends S2942 (blog_tool + feedback_tool) pattern to admin-only, category-scoped
bulk_archive of PUBLISHED deliverables. Handler: `_handle_bulk_archive_published`
at `core/services/td_handlers_content.py:5065+`.

Dry_run envelope shape (aligns with S2942 blog_tool.reject / feedback_tool.submit):

- `dry_run: True`
- `would_action: 'archive_published'`
- `would_change_to: 'archived'`
- `would_archive_count: N`
- `no_writes: True`
- Zero DB writes performed

Tests cover:

1. dry_run=True (default) — envelope shape + no writes
2. dry_run=True explicit — envelope shape + no writes
3. dry_run=False without confirm — refuses to execute, echoes preview
4. dry_run=False + confirm=True — actually archives (regression sanity)
5. Permission gate — non-admin refused
6. blog block — types=['blog'] refused

Moves Metric B (per_mutation_safety=dry_run_supported) from 2 → 3.
"""
from __future__ import annotations

from datetime import timedelta

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
        trace_id='test-s2943-trace',
    )


class BulkArchivePublishedDryRunTests(TestCase):
    """Core dry_run envelope shape + no-writes guarantee."""

    def setUp(self):
        self.admin = User.objects.create(
            username='s2943-admin', email='s2943admin@example.com', is_staff=True,
        )
        # Create 3 published deliverables in a target category, all older than cutoff.
        old = timezone.now() - timedelta(days=30)
        for i in range(3):
            d = Deliverable.objects.create(
                title=f'S2943 pub #{i}',
                slug=f's2943-pub-{i}',
                agent_name='TestAgent',
                content='body',
                status='published',
                category='TestCategoryS2943',
                user=self.admin,
            )
            # Backdate created_at so it's before cutoff.
            Deliverable.objects.filter(id=d.id).update(created_at=old)

    def _payload(self, **overrides) -> dict:
        base = {
            'action': 'bulk_archive_published',
            'categories': ['TestCategoryS2943'],
            'created_before': timezone.now().isoformat(),
        }
        base.update(overrides)
        return base

    def test_dry_run_true_default_returns_would_envelope(self):
        """Default dry_run is TRUE; envelope carries S2942-aligned fields, no writes."""
        before_status_counts = list(
            Deliverable.objects.filter(category='TestCategoryS2943').values('status').distinct()
        )

        result = _run('content_tool', self._payload(), user_id=self.admin.id)

        self.assertEqual(result['action'], 'bulk_archive_published')
        self.assertTrue(result['dry_run'], 'dry_run must default TRUE')
        self.assertEqual(result['would_action'], 'archive_published')
        self.assertEqual(result['would_change_to'], 'archived')
        self.assertEqual(result['would_archive_count'], 3)
        self.assertTrue(result['no_writes'])
        self.assertIn('dry_run=true', result['message'])

        # No writes performed — all 3 rows stay 'published'
        after_pub = Deliverable.objects.filter(
            category='TestCategoryS2943', status='published',
        ).count()
        self.assertEqual(after_pub, 3, 'dry_run=true must leave all rows published')

    def test_dry_run_true_explicit_returns_would_envelope(self):
        """Explicit dry_run=True behaves identically to default."""
        result = _run('content_tool', self._payload(dry_run=True), user_id=self.admin.id)

        self.assertTrue(result['dry_run'])
        self.assertEqual(result['would_action'], 'archive_published')
        self.assertTrue(result['no_writes'])

        after_pub = Deliverable.objects.filter(
            category='TestCategoryS2943', status='published',
        ).count()
        self.assertEqual(after_pub, 3)

    def test_dry_run_false_without_confirm_refuses(self):
        """dry_run=False without confirm=true is an error — belt-and-suspenders."""
        result = _run(
            'content_tool',
            self._payload(dry_run=False),
            user_id=self.admin.id,
        )
        # Handler returns typed error envelope
        self.assertIn('error', result)
        self.assertEqual(result.get('error_code'), 'invalid_params')

        # No writes
        after_pub = Deliverable.objects.filter(
            category='TestCategoryS2943', status='published',
        ).count()
        self.assertEqual(after_pub, 3, 'refused write must not archive anything')

    def test_dry_run_false_with_confirm_actually_archives(self):
        """dry_run=False + confirm=True executes the archive (regression sanity)."""
        result = _run(
            'content_tool',
            self._payload(dry_run=False, confirm=True),
            user_id=self.admin.id,
        )
        self.assertEqual(result['action'], 'bulk_archive_published')
        self.assertEqual(result['archived_count'], 3)

        after_pub = Deliverable.objects.filter(
            category='TestCategoryS2943', status='published',
        ).count()
        after_arch = Deliverable.objects.filter(
            category='TestCategoryS2943', status='archived',
        ).count()
        self.assertEqual(after_pub, 0)
        self.assertEqual(after_arch, 3)


class BulkArchivePublishedPermissionTests(TestCase):
    """Permission gate + blog block — pre-existing safeguards, regression cover."""

    def setUp(self):
        self.non_admin = User.objects.create(
            username='s2943-noadmin', email='s2943no@example.com',
        )
        self.admin = User.objects.create(
            username='s2943-admin2', email='s2943admin2@example.com', is_staff=True,
        )

    def test_non_admin_denied(self):
        result = _run(
            'content_tool',
            {
                'action': 'bulk_archive_published',
                'categories': ['x'],
                'created_before': timezone.now().isoformat(),
            },
            user_id=self.non_admin.id,
        )
        self.assertIn('error', result)
        self.assertEqual(result.get('error_code'), 'permission_denied')

    def test_blog_type_blocked(self):
        result = _run(
            'content_tool',
            {
                'action': 'bulk_archive_published',
                'categories': ['x'],
                'created_before': timezone.now().isoformat(),
                'types': ['blog'],
            },
            user_id=self.admin.id,
        )
        self.assertIn('error', result)
        self.assertEqual(result.get('error_code'), 'invalid_params')
