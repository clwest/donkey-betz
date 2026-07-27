"""
S2986 slate — remember_tool happy-path + dedupe + cap-hit + truncation tests.

Spec ba968ac1 PR1 coverage gap: S2886 covered the 5 remember_tool error
branches (permission_denied / invalid_params × 3 / unknown_action) but
never exercised the save happy path or the branches that make the tool
actually useful (dedupe hit, cap-hit response shape, content clamp).

Sites tested (7):

* Save success — returns ``{action:'save', status:'created', memory_id,
  memory_type, importance, truncated:False, original_len, message}`` and
  the row lands in the DB.
* Save dedupe hit — second save of the same normalized content +
  memory_type returns ``status='duplicate_updated'`` and does NOT create
  a second row.
* Save dedupe hit bumps importance — if new importance > existing, the
  row's importance is updated (single row still).
* Save content truncation — content > 500 chars is clamped to 500 in the
  DB and the return payload reports ``truncated=True`` + ``original_len``.
* Save cap-hit — when the user is at ``MEMORY_MAX_ITEMS``, returns the
  S2879 migrated envelope with ``error_code='cap_hit'``, ``action='save'``,
  ``current_count``, ``max_items``.
* List — returns saved memories with ``count`` matching DB.
* Search — case-insensitive substring match on ``content``.

Also covers the S2986 pre-parse gate helper:

* ``_build_remember_content_oversized_envelope`` — returns the typed
  envelope with error_code ``REMEMBER_CONTENT_TOO_LONG`` +
  retry_hint.max_content_chars=500.

Run::

    USE_PGBOUNCER=0 python manage.py test core.tests.test_s2986_remember_tool -v2 --keepdb
"""
from __future__ import annotations

import os
import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from core.models import UserMemoryContext
from core.services.tool_dispatcher import ToolDispatcher

_TEST_USER_PW = os.environ.get('DJANGO_TEST_USER_PASSWORD', 'x')


class RememberToolHappyPathTests(TransactionTestCase):
    """S2986 happy-path + dedupe + truncation coverage.

    ``TransactionTestCase`` per S2885 Fold 1 (dispatcher spins up a fresh
    asyncio loop; plain TestCase fixture-invisibility would break the
    User lookup at handler L2224).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username=f's2986_remember_{uuid.uuid4().hex[:8]}',
            password=_TEST_USER_PW,
        )

    def _dispatch(self, payload):
        tool_result = self.dispatcher.execute_sync(
            'remember_tool', payload, user_id=self.user.id,
        )
        self.assertTrue(
            tool_result.ok,
            f"remember_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    # ── save happy path ─────────────────────────────────────────────────

    def test_save_success_returns_created_status_and_persists(self):
        result = self._dispatch({
            'action': 'save',
            'content': 'Chris prefers plain-English mid-flight framing',
            'memory_type': 'preference',
            'importance': 8,
        })
        self.assertEqual(result.get('action'), 'save')
        self.assertEqual(result.get('status'), 'created')
        self.assertIn('memory_id', result)
        self.assertEqual(result.get('memory_type'), 'preference')
        self.assertEqual(result.get('importance'), 8)
        self.assertFalse(result.get('truncated'))
        self.assertEqual(
            result.get('original_len'),
            len('Chris prefers plain-English mid-flight framing'),
        )
        # Row landed in DB
        row = UserMemoryContext.objects.get(pk=result['memory_id'])
        self.assertEqual(row.user_id, self.user.id)
        self.assertEqual(row.memory_type, 'preference')
        self.assertEqual(row.importance, 8)
        self.assertEqual(row.source, 'remember_tool')
        self.assertIn('content_hash', row.context_metadata)

    # ── dedupe ──────────────────────────────────────────────────────────

    def test_save_dedupe_hit_returns_duplicate_updated_and_no_new_row(self):
        payload = {
            'action': 'save',
            'content': 'Never merge on main without --admin until CI billing is fixed',
            'memory_type': 'instruction',
            'importance': 9,
        }
        first = self._dispatch(payload)
        self.assertEqual(first.get('status'), 'created')

        second = self._dispatch(payload)
        self.assertEqual(second.get('action'), 'save')
        self.assertEqual(second.get('status'), 'duplicate_updated')
        self.assertEqual(second.get('memory_id'), first.get('memory_id'))

        row_count = UserMemoryContext.objects.filter(
            user_id=self.user.id,
            memory_type='instruction',
        ).count()
        self.assertEqual(row_count, 1)

    def test_save_dedupe_bumps_importance_when_higher(self):
        payload = {
            'action': 'save',
            'content': 'Chris drinks black coffee',
            'memory_type': 'preference',
            'importance': 3,
        }
        first = self._dispatch(payload)
        payload['importance'] = 9
        second = self._dispatch(payload)
        self.assertEqual(second.get('status'), 'duplicate_updated')
        row = UserMemoryContext.objects.get(pk=first['memory_id'])
        self.assertEqual(row.importance, 9)

    def test_save_dedupe_does_not_lower_importance(self):
        payload = {
            'action': 'save',
            'content': 'Chris drinks black coffee',
            'memory_type': 'preference',
            'importance': 9,
        }
        first = self._dispatch(payload)
        payload['importance'] = 2
        second = self._dispatch(payload)
        self.assertEqual(second.get('status'), 'duplicate_updated')
        row = UserMemoryContext.objects.get(pk=first['memory_id'])
        self.assertEqual(row.importance, 9)  # not lowered

    # ── truncation ──────────────────────────────────────────────────────

    def test_save_content_truncated_at_500_chars_signaled_in_return(self):
        long_content = 'x' * 750
        result = self._dispatch({
            'action': 'save',
            'content': long_content,
            'memory_type': 'context',
        })
        self.assertEqual(result.get('status'), 'created')
        self.assertTrue(result.get('truncated'))
        self.assertEqual(result.get('original_len'), 750)
        row = UserMemoryContext.objects.get(pk=result['memory_id'])
        self.assertEqual(len(row.content), 500)

    # ── cap-hit ─────────────────────────────────────────────────────────

    def test_save_at_cap_returns_migrated_envelope(self):
        with patch.dict(os.environ, {'MEMORY_MAX_ITEMS': '2'}):
            self._dispatch({
                'action': 'save',
                'content': 'memory one',
                'memory_type': 'preference',
            })
            self._dispatch({
                'action': 'save',
                'content': 'memory two',
                'memory_type': 'preference',
            })
            result = self._dispatch({
                'action': 'save',
                'content': 'memory three',
                'memory_type': 'preference',
            })

        # S2879 migrated envelope
        self.assertFalse(result.get('success'))
        self.assertEqual(result.get('error_code'), 'cap_hit')
        self.assertEqual(result.get('action'), 'save')
        self.assertTrue(result.get('error'))
        self.assertEqual(result.get('current_count'), 2)
        self.assertEqual(result.get('max_items'), 2)

    # ── list / search ───────────────────────────────────────────────────

    def test_list_returns_saved_memories(self):
        self._dispatch({
            'action': 'save',
            'content': 'preference one',
            'memory_type': 'preference',
        })
        self._dispatch({
            'action': 'save',
            'content': 'goal one',
            'memory_type': 'goal',
        })
        result = self._dispatch({'action': 'list'})
        self.assertEqual(result.get('action'), 'list')
        self.assertEqual(result.get('count'), 2)
        self.assertEqual(len(result.get('memories')), 2)

    def test_search_case_insensitive_substring_match(self):
        self._dispatch({
            'action': 'save',
            'content': 'Chris wants zoom-out asks per SIGN cycle',
            'memory_type': 'instruction',
        })
        result = self._dispatch({
            'action': 'search',
            'query': 'ZOOM-OUT',
        })
        self.assertEqual(result.get('action'), 'search')
        self.assertEqual(result.get('count'), 1)
        self.assertIn('zoom-out', result['memories'][0]['content'].lower())


# ────────────────────────────────────────────────────────────────────────
# S2986 pre-parse gate — envelope helper
# ────────────────────────────────────────────────────────────────────────


class RememberContentOversizedEnvelopeTests(TransactionTestCase):
    """S2986 F-D1b — typed envelope for oversize raw-args gate.

    The gate itself lives in ``unified_pa_entrypoint._execute_inner`` and
    fires from the agentic loop; unit-testing the helper is enough to lock
    the contract shape without spinning up the full PA stack (S1177 F1
    pattern for the sibling ``_build_tool_args_malformed_envelope``).
    """

    def test_envelope_shape(self):
        from core.services.unified_pa_entrypoint import (
            REMEMBER_CONTENT_OVERSIZED_ERROR_CODE,
            REMEMBER_TOOL_ARGS_RAW_MAX,
            _build_remember_content_oversized_envelope,
        )
        envelope = _build_remember_content_oversized_envelope(
            tool_name='remember_tool',
            raw_args_len=4200,
        )
        self.assertFalse(envelope['ok'])
        self.assertEqual(
            envelope['error_code'],
            REMEMBER_CONTENT_OVERSIZED_ERROR_CODE,
        )
        self.assertEqual(envelope['tool_name'], 'remember_tool')
        self.assertIn('too long', envelope['message'].lower())
        self.assertEqual(envelope['meta']['arguments_len'], 4200)
        self.assertEqual(envelope['meta']['raw_max'], REMEMBER_TOOL_ARGS_RAW_MAX)
        self.assertEqual(
            envelope['retry_hint']['recommended_action'],
            'remember_tool.save',
        )
        self.assertEqual(envelope['retry_hint']['max_content_chars'], 500)

    def test_threshold_constant_is_3000(self):
        from core.services.unified_pa_entrypoint import REMEMBER_TOOL_ARGS_RAW_MAX
        # Lock the threshold — if this changes, the operator doc must too.
        self.assertEqual(REMEMBER_TOOL_ARGS_RAW_MAX, 3000)
