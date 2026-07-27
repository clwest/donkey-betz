"""
S2987 (spec ba968ac1 PR2) — hygiene command + supersede migration + trace tests.

Covers:

* Migration smoke — the three new UserMemoryContext fields are present
  with the expected defaults (is_active=True; superseded_by/at null).
* MemoryContextService.get_prompt_context_with_trace returns retrieved
  ids alongside the context string; ids match the underlying rows.
* MemoryContextService filters out is_active=False rows from prompt
  injection (F-D4 hygiene enforcement).
* memory_promotion_service.check_and_promote respects MEMORY_MAX_ITEMS
  via DEMOTE-oldest-auto_promotion strategy (F-PR2-2 cap-fix fold).
* memory_promotion_service SKIPS + emits capped tracker event when no
  auto_promotion rows are available to demote.
* memory_hygiene_audit --dry-run reports without writing.
* memory_hygiene_audit --apply supersedes stale rows without DELETE.

Uses ``TransactionTestCase`` per S2885 Fold 1 (dispatcher spins up fresh
asyncio loop for tests that touch handler paths; consistent across
S2986 tests).

Run::

    USE_PGBOUNCER=0 python manage.py test core.tests.test_s2987_memory_hygiene_and_trace -v2 --keepdb
"""
from __future__ import annotations

import os
import uuid
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TransactionTestCase
from django.utils import timezone

from core.models import UserMemoryContext, EnhancedUserProfile

_TEST_USER_PW = os.environ.get('DJANGO_TEST_USER_PASSWORD', 'x')


def _create_user(prefix: str = 's2987'):
    User = get_user_model()
    return User.objects.create_user(
        username=f'{prefix}_{uuid.uuid4().hex[:8]}',
        password=_TEST_USER_PW,
    )


def _create_memory(user, content: str, memory_type: str = 'preference',
                    source: str = 'test', importance: int = 7,
                    tags=None, is_active: bool = True,
                    created_at=None, last_accessed=None):
    profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)
    row = UserMemoryContext.objects.create(
        user=user,
        profile=profile,
        memory_type=memory_type,
        content=content,
        importance=importance,
        source=source,
        tags=tags or [],
        is_active=is_active,
    )
    # Backdate for stale/cap-drift tests; auto_now_add ignores explicit values on create.
    if created_at is not None or last_accessed is not None:
        UserMemoryContext.objects.filter(pk=row.pk).update(
            **{k: v for k, v in {
                'created_at': created_at,
                'last_accessed': last_accessed,
            }.items() if v is not None}
        )
        row.refresh_from_db()
    return row


# ────────────────────────────────────────────────────────────────────────
# Migration smoke — new fields present with expected defaults
# ────────────────────────────────────────────────────────────────────────


class MigrationSmokeTests(TransactionTestCase):
    def test_new_fields_default_correctly(self):
        user = _create_user('migration')
        row = _create_memory(user, 'default check')
        # Defaults from the migration
        self.assertTrue(row.is_active)
        self.assertIsNone(row.superseded_by)
        self.assertIsNone(row.superseded_at)

    def test_superseded_by_self_fk_set_null_on_delete(self):
        user = _create_user('sbfk')
        old = _create_memory(user, 'old row')
        new = _create_memory(user, 'new row')
        old.superseded_by = new
        old.superseded_at = timezone.now()
        old.is_active = False
        old.save()

        old.refresh_from_db()
        self.assertEqual(old.superseded_by_id, new.pk)

        # Deleting the new row must NOT cascade — it should set superseded_by=NULL.
        new.delete()
        old.refresh_from_db()
        self.assertIsNone(old.superseded_by)


# ────────────────────────────────────────────────────────────────────────
# MemoryContextService trace + is_active filtering
# ────────────────────────────────────────────────────────────────────────


class MemoryContextTraceTests(TransactionTestCase):
    def setUp(self):
        from core.services.memory_context_service import get_memory_context_service
        self.user = _create_user('trace')
        self.svc = get_memory_context_service()
        self.svc.clear_cache(self.user)

    def test_get_prompt_context_with_trace_returns_retrieved_ids(self):
        pref = _create_memory(self.user, 'Chris prefers concise answers',
                              memory_type='preference', importance=8)
        goal = _create_memory(self.user, 'Ship PR2 memory hygiene',
                              memory_type='goal', importance=9)

        context, retrieved_ids, layer = self.svc.get_prompt_context_with_trace(self.user)

        self.assertIn('concise', context.lower())
        self.assertIn('ship', context.lower())
        self.assertEqual(layer, 'user_memory_context')
        self.assertIn(pref.id, retrieved_ids)
        self.assertIn(goal.id, retrieved_ids)

    def test_get_prompt_context_wrapper_is_backwards_compat(self):
        _create_memory(self.user, 'Backwards compat check',
                       memory_type='preference', importance=7)
        # Bypass any cached value from a prior call
        self.svc.clear_cache(self.user)
        context = self.svc.get_prompt_context(self.user)
        self.assertIn('backwards compat', context.lower())

    def test_inactive_memories_excluded_from_prompt_injection(self):
        _create_memory(self.user, 'ACTIVE preference',
                       memory_type='preference', importance=9, is_active=True)
        _create_memory(self.user, 'SUPERSEDED preference',
                       memory_type='preference', importance=9, is_active=False)

        context, retrieved_ids, _layer = self.svc.get_prompt_context_with_trace(self.user)

        self.assertIn('active', context.lower())
        self.assertNotIn('superseded', context.lower())


# ────────────────────────────────────────────────────────────────────────
# memory_promotion_service — cap-fix + DEMOTE-oldest-auto_promotion
# ────────────────────────────────────────────────────────────────────────


class MemoryPromotionCapFixTests(TransactionTestCase):
    def _run_promotion(self, user, message: str, response: str):
        """Wrapper around check_and_promote with a stable trace_id."""
        from core.services.memory_promotion_service import check_and_promote
        return check_and_promote(
            user_message=message,
            assistant_response=response,
            tool_runs=[],
            user=user,
            trace_id=f'test-{uuid.uuid4().hex[:8]}',
        )

    def test_under_cap_creates_normally(self):
        user = _create_user('undercap')
        # Well under the default 200 cap
        with patch.dict(os.environ, {'MEMORY_MAX_ITEMS': '200'}):
            result = self._run_promotion(
                user,
                message='Deploying v2.0 to Railway now',
                response='Deployed to Railway service:api',
            )
        # Either 'saved' (new) or 'updated' (dedupe) — both are non-capped.
        self.assertIn(result.get('action'), ('saved', 'updated'))
        self.assertNotIn('demoted_memory_id', result)

    def test_at_cap_demotes_oldest_auto_promotion(self):
        user = _create_user('demote')

        # Seed the user at cap with 3 auto_promotion rows (oldest first).
        with patch.dict(os.environ, {'MEMORY_MAX_ITEMS': '3'}):
            older = _create_memory(user, 'older auto row',
                                   memory_type='project', source='auto_promotion',
                                   importance=9, is_active=True,
                                   created_at=timezone.now() - timedelta(days=30))
            _create_memory(user, 'middle auto row',
                           memory_type='project', source='auto_promotion',
                           importance=9, is_active=True,
                           created_at=timezone.now() - timedelta(days=15))
            _create_memory(user, 'recent auto row',
                           memory_type='project', source='auto_promotion',
                           importance=9, is_active=True,
                           created_at=timezone.now() - timedelta(days=1))

            # Trigger a promotion — should demote `older` and create new.
            # Message needs to score >= 7 (milestone +3, ids capped at +6,
            # wiring +2). Bundle+repo+version+railway push us to 7+.
            result = self._run_promotion(
                user,
                message='Deployed com.donkey.betz v3.0.1 (42) to Railway service:api',
                response='Successfully deployed com.donkey.betz to Railway; git@github.com:clwest/repo pushed',
            )

        self.assertEqual(result.get('action'), 'saved')
        self.assertEqual(result.get('demoted_memory_id'), older.id)

        older.refresh_from_db()
        self.assertFalse(older.is_active)
        self.assertIsNotNone(older.superseded_at)
        self.assertIsNotNone(older.superseded_by)

    def test_at_cap_no_auto_promotion_available_skips_and_reports_capped(self):
        user = _create_user('capped')

        # Seed with 3 NON-auto_promotion rows (curated). No demote candidate.
        with patch.dict(os.environ, {'MEMORY_MAX_ITEMS': '3'}):
            _create_memory(user, 'curated one', source='remember_tool',
                           memory_type='preference', importance=9)
            _create_memory(user, 'curated two', source='remember_tool',
                           memory_type='preference', importance=9)
            _create_memory(user, 'curated three', source='remember_tool',
                           memory_type='preference', importance=9)

            result = self._run_promotion(
                user,
                message='Deployed com.donkey.betz v4.0.0 (44) to Railway service:api',
                response='Successfully deployed com.donkey.betz to Railway; git@github.com:clwest/repo pushed',
            )

        self.assertEqual(result.get('action'), 'capped')
        self.assertEqual(result.get('reason'), 'no_auto_promotion_rows_available')
        self.assertEqual(result.get('max_items'), 3)
        # No new row was created.
        self.assertEqual(
            UserMemoryContext.objects.filter(user=user, is_active=True).count(),
            3,
        )


# ────────────────────────────────────────────────────────────────────────
# memory_hygiene_audit management command
# ────────────────────────────────────────────────────────────────────────


class MemoryHygieneAuditCommandTests(TransactionTestCase):
    def _run(self, *args, **kwargs):
        out = StringIO()
        call_command('memory_hygiene_audit', *args, stdout=out, **kwargs)
        return out.getvalue()

    def test_dry_run_reports_stale_without_writing(self):
        user = _create_user('stale')
        stale = _create_memory(
            user, 'old low-importance row',
            memory_type='context', source='auto_promotion',
            importance=2,
            created_at=timezone.now() - timedelta(days=120),
        )
        # Recent, high-importance row (should NOT be flagged stale)
        _create_memory(user, 'recent important', memory_type='preference', importance=9)

        output = self._run('--user', user.username)
        self.assertIn('DRY-RUN', output)
        self.assertIn('STALE', output)
        self.assertIn(str(stale.id), output)

        # No writes.
        stale.refresh_from_db()
        self.assertTrue(stale.is_active)
        self.assertIsNone(stale.superseded_at)

    def test_apply_supersedes_stale_without_deleting(self):
        user = _create_user('applystale')
        stale = _create_memory(
            user, 'stale row',
            memory_type='context', source='auto_promotion',
            importance=1,
            created_at=timezone.now() - timedelta(days=120),
        )
        output = self._run('--user', user.username, '--apply')
        self.assertIn('APPLY', output)
        self.assertIn('superseded 1', output)

        # Row still exists (no DELETE) but is superseded.
        stale.refresh_from_db()
        self.assertFalse(stale.is_active)
        self.assertIsNotNone(stale.superseded_at)

    def test_cap_drift_report_shows_source_breakdown(self):
        user = _create_user('capreport')
        for i in range(5):
            _create_memory(user, f'auto row {i}', memory_type='project',
                           source='auto_promotion', importance=9)
        for i in range(2):
            _create_memory(user, f'curated {i}', memory_type='preference',
                           source='remember_tool', importance=9)

        output = self._run('--user', user.username, '--max-items', '3')
        self.assertIn('CAP-DRIFT', output)
        self.assertIn(user.username, output)
        self.assertIn('auto_promotion: 5', output)
        self.assertIn('remember_tool: 2', output)

    def test_conflicts_report_shows_repeated_tag(self):
        user = _create_user('conflict')
        # 3 active rows with same memory_type + same tag = conflict candidate.
        for i in range(3):
            _create_memory(user, f'row {i}', memory_type='instruction',
                           tags=['ci', 'deploy'], importance=7)

        output = self._run('--user', user.username)
        self.assertIn('CONFLICTS', output)
        self.assertIn("tag='ci'", output)
