"""Session 2942 — Ledger #38 MVP: dry_run affordance for blog_tool + feedback_tool.

Covers five mutation actions across three handler paths:

- `feedback_tool.submit` → `_handle_feedback` (UserFeedback.create)
- `feedback_tool.update` → `_handle_feedback` (UserFeedback.save)
- `blog_tool.approve` (Deliverable path) → `_handle_content_review.publish`
- `blog_tool.reject` (Deliverable path) → `_handle_content_review.archive`
- `blog_tool.approve` (SelfBlog path, type='blog') → `_handle_blog_query.publish`
- `blog_tool.reject` (SelfBlog path, type='blog') → `_handle_blog_query.archive`
- `blog_tool.generate` → `_handle_generate_blog` (Celery `.delay()`)

Each `dry_run=true` test asserts:

1. Response includes `dry_run=True`, `would_action=<verb>`, `no_writes=True`.
2. No DB state changes (row counts + statuses unchanged).
3. For `generate`: no Celery `.delay()` invocation.

Each `dry_run=false` sanity test asserts the real mutation lands (regression cover).
"""
from __future__ import annotations

from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.models_unified_system import SelfBlog
from core.models_user_feedback import UserFeedback
from core.services.tool_dispatcher import get_tool_dispatcher

User = get_user_model()


def _run(tool_name: str, payload: dict) -> dict:
    """Route a tool call through the registered handler (mirrors S2931 pattern)."""
    dispatcher = get_tool_dispatcher()
    handler = dispatcher._tool_handlers[tool_name]
    return handler(
        tool_name=tool_name,
        payload=payload,
        user_id=None,
        trace_id='test-s2942-trace',
    )


# ─────────────────────────────────────────────────────────────────────────────
# feedback_tool.submit
# ─────────────────────────────────────────────────────────────────────────────


class FeedbackSubmitDryRunTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='s2942-fb-sub', email='s2942fb@example.com')

    def test_submit_dry_run_returns_would_envelope_no_write(self):
        before = UserFeedback.objects.count()

        result = _run('feedback_tool', {
            'action': 'submit',
            'comment': 'Testing dry_run',
            'target_type': 'bug',
            'dry_run': True,
        })

        self.assertEqual(result['action'], 'submit')
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['would_action'], 'create')
        self.assertTrue(result['no_writes'])
        would = result['would_write']
        self.assertEqual(would['model'], 'UserFeedback')
        self.assertEqual(would['feedback_type'], 'bug')
        self.assertEqual(would['message'], 'Testing dry_run')
        self.assertEqual(would['status'], 'open')

        self.assertEqual(UserFeedback.objects.count(), before,
                         'dry_run=true must not create a UserFeedback row')

    def test_submit_dry_run_false_actually_creates(self):
        before = UserFeedback.objects.count()

        result = _run('feedback_tool', {
            'action': 'submit',
            'comment': 'Baseline mutation still lands',
            'dry_run': False,
        })

        self.assertTrue(result.get('success'))
        self.assertNotIn('dry_run', result)
        self.assertEqual(UserFeedback.objects.count(), before + 1)


# ─────────────────────────────────────────────────────────────────────────────
# feedback_tool.update
# ─────────────────────────────────────────────────────────────────────────────


class FeedbackUpdateDryRunTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='s2942-fb-upd', email='s2942fbu@example.com')
        self.fb = UserFeedback.objects.create(
            user=self.user,
            feedback_type='bug',
            message='pre-existing',
            status='open',
        )

    def test_update_dry_run_returns_would_envelope_no_write(self):
        result = _run('feedback_tool', {
            'action': 'update',
            'id': str(self.fb.id),
            'new_status': 'acknowledged',
            'notes': 'reviewed',
            'dry_run': True,
        })

        self.assertEqual(result['action'], 'update')
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['would_action'], 'update')
        self.assertEqual(result['current_status'], 'open')
        self.assertEqual(result['would_change_to'], 'acknowledged')
        self.assertEqual(result['notes_would_be'], 'reviewed')
        self.assertTrue(result['no_writes'])

        self.fb.refresh_from_db()
        self.assertEqual(self.fb.status, 'open',
                         'dry_run=true must leave UserFeedback.status unchanged')

    def test_update_dry_run_false_actually_saves(self):
        result = _run('feedback_tool', {
            'action': 'update',
            'id': str(self.fb.id),
            'new_status': 'acknowledged',
            'dry_run': False,
        })
        self.assertTrue(result.get('success'))
        self.fb.refresh_from_db()
        self.assertEqual(self.fb.status, 'acknowledged')


# ─────────────────────────────────────────────────────────────────────────────
# blog_tool.approve / reject — Deliverable path (type unset)
# ─────────────────────────────────────────────────────────────────────────────


class BlogToolDeliverableDryRunTests(TestCase):
    def setUp(self):
        self.deliverable = Deliverable.objects.create(
            title='S2942 test deliverable',
            slug='s2942-test',
            agent_name='TestAgent',
            content='body',
            status='ready',
        )

    def test_approve_dry_run_returns_would_publish_no_write(self):
        result = _run('blog_tool', {
            'action': 'approve',
            'id': str(self.deliverable.id),
            'dry_run': True,
        })

        self.assertEqual(result['action'], 'publish')
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['would_action'], 'publish')
        self.assertEqual(result['current_status'], 'ready')
        self.assertEqual(result['would_change_to'], 'published')
        self.assertTrue(result['no_writes'])

        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.status, 'ready',
                         'dry_run=true must leave Deliverable.status unchanged')

    def test_reject_dry_run_returns_would_archive_no_write(self):
        result = _run('blog_tool', {
            'action': 'reject',
            'id': str(self.deliverable.id),
            'feedback': 'off-brand',
            'dry_run': True,
        })

        self.assertEqual(result['action'], 'archive')
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['would_action'], 'archive')
        self.assertEqual(result['current_status'], 'ready')
        self.assertEqual(result['would_change_to'], 'archived')
        self.assertEqual(result['would_archive_reason'], 'off-brand')
        self.assertTrue(result['no_writes'])

        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.status, 'ready',
                         'dry_run=true must leave Deliverable unchanged')
        self.assertNotIn('archive_reason', self.deliverable.metadata or {})

    def test_approve_dry_run_false_actually_publishes(self):
        result = _run('blog_tool', {
            'action': 'approve',
            'id': str(self.deliverable.id),
            'dry_run': False,
        })
        self.assertTrue(result.get('success'))
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.status, 'published')


# ─────────────────────────────────────────────────────────────────────────────
# blog_tool.approve / reject — SelfBlog path (type='blog')
# ─────────────────────────────────────────────────────────────────────────────


class BlogToolSelfBlogDryRunTests(TestCase):
    def setUp(self):
        self.blog = SelfBlog.objects.create(
            title='S2942 SelfBlog',
            full_text='body body body',
            status='approved',
            publish_ready=True,
            category='blog',
        )

    def test_selfblog_approve_dry_run_returns_would_publish_no_write(self):
        result = _run('blog_tool', {
            'action': 'approve',
            'id': str(self.blog.id),
            'type': 'blog',
            'dry_run': True,
        })

        self.assertEqual(result['action'], 'publish')
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['would_action'], 'publish')
        self.assertEqual(result['source'], 'SelfBlog')
        self.assertEqual(result['current_status'], 'approved')
        self.assertEqual(result['would_change_to'], 'published')
        self.assertTrue(result['no_writes'])

        self.blog.refresh_from_db()
        self.assertEqual(self.blog.status, 'approved',
                         'dry_run=true must leave SelfBlog.status unchanged')

    def test_selfblog_reject_dry_run_returns_would_archive_no_write(self):
        result = _run('blog_tool', {
            'action': 'reject',
            'id': str(self.blog.id),
            'type': 'blog',
            'feedback': 'quality issue',
            'dry_run': True,
        })

        self.assertEqual(result['action'], 'archive')
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['would_action'], 'archive')
        self.assertEqual(result['source'], 'SelfBlog')
        self.assertEqual(result['current_status'], 'approved')
        self.assertEqual(result['would_change_to'], 'draft')
        self.assertTrue(result['would_clear_publish_ready'])
        self.assertTrue(result['no_writes'])

        self.blog.refresh_from_db()
        self.assertEqual(self.blog.status, 'approved')
        self.assertTrue(self.blog.publish_ready,
                        'dry_run=true must not flip publish_ready')


# ─────────────────────────────────────────────────────────────────────────────
# blog_tool.generate — Celery dispatch skipped under dry_run
# ─────────────────────────────────────────────────────────────────────────────


class BlogToolGenerateDryRunTests(TestCase):
    def test_generate_with_topic_dry_run_skips_celery(self):
        target = 'core.tasks.generate_blog_with_topic_task.delay'
        with mock.patch(target) as mocked_delay:
            result = _run('blog_tool', {
                'action': 'generate',
                'topic': 'test topic',
                'tone': 'analytical',
                'dry_run': True,
            })

        self.assertEqual(result['action'], 'generate_blog')
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['would_action'], 'dispatch_celery')
        self.assertEqual(result['would_task'], 'generate_blog_with_topic_task')
        self.assertEqual(result['topic'], 'test topic')
        self.assertEqual(result['tone'], 'analytical')
        self.assertTrue(result['no_writes'])
        mocked_delay.assert_not_called()

    def test_generate_open_topic_dry_run_skips_celery(self):
        target = 'core.tasks.generate_self_blog_deliberation_task.delay'
        with mock.patch(target) as mocked_delay:
            result = _run('blog_tool', {
                'action': 'generate',
                'tone': 'concise',
                'dry_run': True,
            })

        self.assertEqual(result['action'], 'generate_blog')
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['would_task'], 'generate_self_blog_deliberation_task')
        self.assertEqual(result['tone'], 'concise')
        self.assertTrue(result['no_writes'])
        mocked_delay.assert_not_called()
