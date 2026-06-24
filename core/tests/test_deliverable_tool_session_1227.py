"""Session 1227 — deliverable_tool list+stats tool-surface additions.

Covers four behaviors added in PR1 against the Session 1226 audit `e2964e4a-…`
§4.6 backlog:

1. **LLM-autofill safety on `has_initiative`** — GPT-5.2 in function-calling
   mode fills declared optional booleans with `False` whether or not the user
   asked to filter. The previous handler check `if has_init is not None:`
   then fired and silently filtered out every deliverable WITH an initiative.
   New behavior: only truthy values trigger the WITH-initiative filter; only
   the STRING `'false'`/'False' triggers the WITHOUT-initiative filter;
   Python bool `False` is intentionally a no-op (autofill compat).

2. **`show_all=true` bypass** — escape hatch that bypasses the optional
   filters most likely to be LLM-autofilled (has_initiative, orphans, saved,
   status). Other filters (agent/category/type/workspace/initiative_id)
   still respect explicit caller intent.

3. **`applied_filters` echo** — list/search responses now include the dict
   of filters that actually fired, so future bugs of the autofill class are
   diagnosable from a single tool call (no ORM round-trip needed).

4. **`full_by_agent=true` on stats** — returns the entire `agent_name`
   long tail (default top-10 was hiding ~25 agents from audit-time queries).
   Response surfaces `by_agent_truncated` so callers know whether the
   default cap was applied.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.models_document_registry import Initiative
from core.services.tool_dispatcher import ToolDispatcher

User = get_user_model()


def _dispatch(action, user_id, payload):
    dispatcher = ToolDispatcher()
    return dispatcher._handle_deliverables(  # type: ignore[attr-defined]
        tool_name='deliverable_tool',
        payload={'action': action, **payload},
        user_id=user_id,
        trace_id='test-s1227',
    )


def _list_ids(result):
    return {str(d['id']) for d in result.get('items', [])}


class HasInitiativeAutofillSafetyTests(TestCase):
    """Boolean False on has_initiative must NOT trigger the WITHOUT-init filter."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s1227-autofill', password='x', is_staff=True,
        )
        self.initiative = Initiative.objects.create(
            name='S1227 autofill probe', description='x', owner=self.user,
        )
        self.with_init = Deliverable.objects.create(
            title='S1227 with init',
            content='x' * 200,
            agent_name='Rigby',
            user=self.user,
            initiative=self.initiative,
        )
        self.without_init = Deliverable.objects.create(
            title='S1227 without init',
            content='x' * 200,
            agent_name='Rigby',
            user=self.user,
        )

    def test_python_bool_false_is_treated_as_no_filter(self):
        """The headline bug fix: Python False (LLM autofill) → both rows visible."""
        result = _dispatch('list', self.user.id, {'has_initiative': False})
        ids = _list_ids(result)
        self.assertIn(str(self.with_init.id), ids)
        self.assertIn(str(self.without_init.id), ids)
        # applied_filters must NOT list has_initiative since no filter fired.
        self.assertNotIn('has_initiative', result.get('applied_filters', {}))

    def test_explicit_string_false_still_filters_for_no_initiative(self):
        """String 'false' is the explicit caller sentinel."""
        result = _dispatch('list', self.user.id, {'has_initiative': 'false'})
        ids = _list_ids(result)
        self.assertIn(str(self.without_init.id), ids)
        self.assertNotIn(str(self.with_init.id), ids)
        self.assertEqual(
            result.get('applied_filters', {}).get('has_initiative'), False
        )

    def test_python_bool_true_still_filters_for_with_initiative(self):
        """Truthy values keep working — only False is special-cased."""
        result = _dispatch('list', self.user.id, {'has_initiative': True})
        ids = _list_ids(result)
        self.assertIn(str(self.with_init.id), ids)
        self.assertNotIn(str(self.without_init.id), ids)
        self.assertEqual(
            result.get('applied_filters', {}).get('has_initiative'), True
        )


class ShowAllBypassTests(TestCase):
    """show_all=true bypasses has_initiative + orphans + saved + status filters."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s1227-showall', password='x', is_staff=True,
        )
        self.initiative = Initiative.objects.create(
            name='S1227 show_all probe', description='x', owner=self.user,
        )
        self.with_init = Deliverable.objects.create(
            title='S1227 SA with init',
            content='x' * 200,
            agent_name='Rigby',
            user=self.user,
            initiative=self.initiative,
        )
        self.without_init = Deliverable.objects.create(
            title='S1227 SA without init',
            content='x' * 200,
            agent_name='Rigby',
            user=self.user,
        )

    def test_show_all_overrides_explicit_string_false_filter(self):
        """show_all=true beats has_initiative='false' (explicit caller filter)."""
        result = _dispatch(
            'list',
            self.user.id,
            {'has_initiative': 'false', 'show_all': True},
        )
        ids = _list_ids(result)
        # Both rows visible — show_all bypassed the explicit filter.
        self.assertIn(str(self.with_init.id), ids)
        self.assertIn(str(self.without_init.id), ids)
        self.assertTrue(result.get('show_all'))
        # has_initiative MUST NOT appear in applied_filters since show_all
        # bypassed it.
        self.assertNotIn('has_initiative', result.get('applied_filters', {}))

    def test_show_all_overrides_status_filter(self):
        """show_all=true bypasses status filter (Session 1226 audit §4.6 (B))."""
        # Create one blocked + one ready, then ask for show_all + status=ready.
        blocked = Deliverable.objects.create(
            title='S1227 SA blocked',
            content='x' * 200,
            agent_name='Rigby',
            user=self.user,
            status='blocked',
        )
        result = _dispatch(
            'list',
            self.user.id,
            {'status': 'ready', 'show_all': True},
        )
        ids = _list_ids(result)
        # Both visible despite status=ready, because show_all is set.
        self.assertIn(str(blocked.id), ids)

    def test_show_all_does_not_bypass_agent_or_category(self):
        """show_all preserves precision filters — only bypasses LLM-autofill class."""
        result = _dispatch(
            'list',
            self.user.id,
            {'agent': 'Rigby', 'show_all': True},
        )
        ids = _list_ids(result)
        # Both Rigby rows visible (with and without init).
        self.assertIn(str(self.with_init.id), ids)
        self.assertIn(str(self.without_init.id), ids)
        # applied_filters must still record agent.
        self.assertEqual(result.get('applied_filters', {}).get('agent'), 'Rigby')


class AppliedFiltersEchoTests(TestCase):
    """Response echoes which optional filters actually fired."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s1227-echo', password='x', is_staff=True,
        )
        Deliverable.objects.create(
            title='S1227 echo probe', content='x' * 200,
            agent_name='Rigby', user=self.user, status='ready',
        )

    def test_empty_args_yields_empty_applied_filters(self):
        result = _dispatch('list', self.user.id, {})
        self.assertEqual(result.get('applied_filters'), {})
        self.assertFalse(result.get('show_all'))

    def test_agent_and_status_both_echoed(self):
        result = _dispatch(
            'list', self.user.id,
            {'agent': 'Rigby', 'status': 'ready'},
        )
        af = result.get('applied_filters', {})
        self.assertEqual(af.get('agent'), 'Rigby')
        self.assertEqual(af.get('status'), 'ready')

    def test_status_alias_normalized_in_applied_filters(self):
        """Status aliases (approved/pending_review/rejected) should normalize."""
        result = _dispatch(
            'list', self.user.id, {'status': 'approved'},
        )
        # 'approved' aliases to 'ready'.
        self.assertEqual(
            result.get('applied_filters', {}).get('status'), 'ready',
        )


class FullByAgentStatsTests(TestCase):
    """stats with full_by_agent=true returns the entire agent_name long tail."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s1227-stats', password='x', is_staff=True,
        )
        # Create 15 distinct agent_name values, one deliverable each.
        for i in range(15):
            Deliverable.objects.create(
                title=f'S1227 stats probe {i}',
                content='x' * 200,
                agent_name=f'Agent_{i:02d}',
                user=self.user,
            )

    def test_default_caps_at_top_10_and_flags_truncated(self):
        result = _dispatch('stats', self.user.id, {})
        by_agent = result.get('by_agent', {})
        self.assertLessEqual(len(by_agent), 10)
        self.assertTrue(result.get('by_agent_truncated'))

    def test_full_by_agent_returns_all_agents(self):
        result = _dispatch('stats', self.user.id, {'full_by_agent': True})
        by_agent = result.get('by_agent', {})
        self.assertGreaterEqual(len(by_agent), 15)
        self.assertFalse(result.get('by_agent_truncated'))

    def test_full_by_agent_python_bool_false_is_no_op(self):
        """LLM-autofill safety on full_by_agent flag too — default truncate."""
        result = _dispatch('stats', self.user.id, {'full_by_agent': False})
        by_agent = result.get('by_agent', {})
        self.assertLessEqual(len(by_agent), 10)
