"""
Session 2728 — Rigby Tool Validation Engineering Campaign, Batch A tool 2
regression tests for `session_tool`.

Covers the F-S-* findings surfaced during code trace + patched at
Session 2728. See:
- `docs/research/tools/validation/session_tool_validation.md` (findings)
- `docs/research/tools/tools_validation_engineering_campaign_plan.md` (campaign)

Findings covered:
- F-S-3: list_recent silent hard cap at 25 → surface `limit_capped`,
  `requested_limit`, `effective_limit`, `hard_max`, and `total` in
  response envelope (mirrors F-D-5 pattern approved at Batch A tool 1).
- F-S-6: retire with zero rows updated now distinguishes `not_found`
  from `already_retired` via an existence query (Chris-ratified option
  (b) at Batch A tool 2 close). Old behavior returned misleading
  `retired: True + updated_count: 0` for both no-op cases.

Existing coverage NOT duplicated:
- health_check / create_fresh / retire happy path — covered in
  test_session_tool_health_check_and_create_fresh.py and
  test_session_tool_retire_set_active_seed.py.
- whoami — covered in test_session_tool_whoami.py.
- test_retire_idempotent_second_call_zero_update updated in-place to
  reflect the F-S-6 semantic change.

Run::

    python manage.py test core.tests.test_session_tool_validation_2728 -v2
"""
from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import ChatConversation
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


def _dispatch_session(user_id, payload):
    """Invoke session_tool via the dispatcher entry point."""
    dispatcher = ToolDispatcher()
    return dispatcher._handle_session(  # type: ignore[attr-defined]
        tool_name='session_tool',
        payload=payload,
        user_id=user_id,
        trace_id='test-session-2728',
    )


def _seed_conversation(user_id, conversation_id, session_active=True, n_messages=1):
    """Create `n_messages` ChatConversation rows for a target conversation."""
    for i in range(n_messages):
        ChatConversation.objects.create(
            conversation_id=conversation_id,
            user_id=user_id,
            session_title=f'seed-title-{conversation_id[-8:]}',
            user_message=f'seed user msg #{i}',
            assistant_response=f'seed assistant response #{i}',
            session_active=session_active,
        )


class SessionToolValidation2728Base(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f'session-2728-{uuid.uuid4().hex[:8]}',
            email='session-2728@example.com',
            password='x',
            is_superuser=True,
            is_staff=True,
        )


class FS3ListRecentLimitCap(SessionToolValidation2728Base):
    """F-S-3 — list_recent surfaces limit_capped envelope + total field."""

    def setUp(self):
        # Seed 30 distinct conversations to exceed the 25-row hard cap.
        for i in range(30):
            _seed_conversation(
                user_id=self.user.id,
                conversation_id=f'pa-fs3-{i:02d}-{uuid.uuid4().hex[:8]}',
                n_messages=1,
            )

    def test_list_recent_within_cap_no_capped_signal(self):
        result = _dispatch_session(
            self.user.id,
            {'action': 'list_recent', 'limit': 10},
        )
        self.assertEqual(result['count'], 10)
        self.assertEqual(result['limit'], 10)
        self.assertNotIn('limit_capped', result)
        # total is always present now.
        self.assertGreaterEqual(result['total'], 30)

    def test_list_recent_over_cap_surfaces_signal(self):
        result = _dispatch_session(
            self.user.id,
            {'action': 'list_recent', 'limit': 100},
        )
        self.assertTrue(result.get('limit_capped'))
        self.assertEqual(result.get('requested_limit'), 100)
        self.assertEqual(result.get('effective_limit'), 25)
        self.assertEqual(result.get('hard_max'), 25)
        self.assertEqual(result['count'], 25)
        self.assertEqual(result['limit'], 25)
        # total reflects the full set unbounded by the cap.
        self.assertGreaterEqual(result['total'], 30)

    def test_list_recent_default_limit_is_10(self):
        result = _dispatch_session(
            self.user.id,
            {'action': 'list_recent'},
        )
        self.assertEqual(result['count'], 10)
        self.assertEqual(result['limit'], 10)
        self.assertNotIn('limit_capped', result)


class FS6RetireDistinguishesNotFoundVsAlreadyRetired(SessionToolValidation2728Base):
    """F-S-6 — retire returns `retired: False + reason=(not_found|already_retired)`
    when updated_count would be 0. Chris ratified option (b) at Batch A tool 2 close."""

    def test_retire_not_found_returns_typed_reason(self):
        result = _dispatch_session(
            self.user.id,
            {
                'action': 'retire',
                'conversation_id': 'pa-does-not-exist-fs6',
                '_bound_conversation_id': 'pa-current-bound-fs6',
            },
        )
        self.assertFalse(result['retired'])
        self.assertEqual(result['updated_count'], 0)
        self.assertFalse(result['previously_active'])
        self.assertEqual(result['reason'], 'not_found')
        self.assertIn('No conversation found', result.get('message', ''))
        # Non-existent target cannot be currently-bound.
        self.assertFalse(result['is_current_bound'])

    def test_retire_already_retired_returns_typed_reason(self):
        # Seed a conversation with all rows session_active=False.
        target = f'pa-fs6-already-retired-{uuid.uuid4().hex[:8]}'
        _seed_conversation(
            user_id=self.user.id,
            conversation_id=target,
            session_active=False,
            n_messages=3,
        )
        result = _dispatch_session(
            self.user.id,
            {
                'action': 'retire',
                'conversation_id': target,
                '_bound_conversation_id': 'pa-current-bound-fs6',
            },
        )
        self.assertFalse(result['retired'])
        self.assertEqual(result['updated_count'], 0)
        self.assertFalse(result['previously_active'])
        self.assertEqual(result['reason'], 'already_retired')
        self.assertIn('already retired', result.get('message', ''))

    def test_retire_happy_path_still_returns_true(self):
        # Regression guard: the F-S-6 patch must NOT break the successful
        # retire path. When rows are session_active=True, retire flips them
        # and returns the standard `retired: True + updated_count: N` shape
        # WITHOUT a `reason` field (reserved for no-op cases).
        target = f'pa-fs6-happy-{uuid.uuid4().hex[:8]}'
        _seed_conversation(
            user_id=self.user.id,
            conversation_id=target,
            session_active=True,
            n_messages=3,
        )
        result = _dispatch_session(
            self.user.id,
            {
                'action': 'retire',
                'conversation_id': target,
                '_bound_conversation_id': 'pa-current-bound-fs6',
            },
        )
        self.assertTrue(result['retired'])
        self.assertEqual(result['updated_count'], 3)
        self.assertTrue(result['previously_active'])
        # Happy path must NOT surface a reason (reason is reserved for no-op).
        self.assertNotIn('reason', result)

    def test_retire_partial_state_flips_only_active_rows(self):
        # Regression guard: when a conversation has a mix of active and
        # retired rows, retire flips only the active ones and reports the
        # count accurately.
        target = f'pa-fs6-mixed-{uuid.uuid4().hex[:8]}'
        _seed_conversation(self.user.id, target, session_active=True, n_messages=2)
        _seed_conversation(self.user.id, target, session_active=False, n_messages=1)
        result = _dispatch_session(
            self.user.id,
            {
                'action': 'retire',
                'conversation_id': target,
                '_bound_conversation_id': 'pa-current-bound-fs6',
            },
        )
        self.assertTrue(result['retired'])
        self.assertEqual(result['updated_count'], 2)
        self.assertTrue(result['previously_active'])
        # Now retire again — all rows are session_active=False → already_retired.
        result2 = _dispatch_session(
            self.user.id,
            {
                'action': 'retire',
                'conversation_id': target,
                '_bound_conversation_id': 'pa-current-bound-fs6',
            },
        )
        self.assertFalse(result2['retired'])
        self.assertEqual(result2['reason'], 'already_retired')
