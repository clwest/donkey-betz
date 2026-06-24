"""Session 1227 PR2 — deliverable_tool first-class `duplicates` action.

Closes Session 1226 audit `e2964e4a-…` §4.6 item 3:
  deliverable_tool.duplicates returning (title, count, first_created_at,
  last_created_at, last_7d_count, agent_name_distribution,
  status_distribution).

Turns the Part 3 of any future duplicates audit into a single tool call
instead of bespoke ORM queries. Stacks on PR1 (PR #2562) for
`applied_filters` echo + `show_all` semantics.
"""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models_deliverables import Deliverable
from core.services.tool_dispatcher import ToolDispatcher

User = get_user_model()


def _dup(user_id, payload):
    dispatcher = ToolDispatcher()
    return dispatcher._handle_deliverables(  # type: ignore[attr-defined]
        tool_name='deliverable_tool',
        payload={'action': 'duplicates', **payload},
        user_id=user_id,
        trace_id='test-dup',
    )


class DuplicatesActionTests(TestCase):
    """Core behavior — grouping, count threshold, response shape."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s1227-dup', password='x', is_staff=True,
        )
        # 3 dupes of "Daily Diagnostic" (Rigby) — heaviest group.
        for _ in range(3):
            Deliverable.objects.create(
                title='Daily Diagnostic',
                content='x' * 200,
                agent_name='Rigby',
                user=self.user,
                status='ready',
            )
        # 2 dupes of "Weekly Roundup" (Rigby) — mid group.
        for _ in range(2):
            Deliverable.objects.create(
                title='Weekly Roundup',
                content='x' * 200,
                agent_name='Rigby',
                user=self.user,
                status='completed',
            )
        # 1 of "Solo Note" — should NOT appear as a duplicate.
        Deliverable.objects.create(
            title='Solo Note',
            content='x' * 200,
            agent_name='ContentWriterAgent',
            user=self.user,
            status='ready',
        )
        # 1 archived dup of "Daily Diagnostic" by ResearchAgent — shifts
        # the agent distribution + tests exclude_archived gating.
        self.archived_dup = Deliverable.objects.create(
            title='Daily Diagnostic',
            content='x' * 200,
            agent_name='ResearchAgent',
            user=self.user,
            status='archived',
        )

    def _titles(self, result):
        return [g['title'] for g in result.get('groups', [])]

    def test_default_returns_groups_with_count_gte_2(self):
        result = _dup(self.user.id, {})
        titles = self._titles(result)
        self.assertIn('Daily Diagnostic', titles)
        self.assertIn('Weekly Roundup', titles)
        self.assertNotIn('Solo Note', titles)
        self.assertEqual(result['action'], 'duplicates')

    def test_count_field_matches_group_size(self):
        result = _dup(self.user.id, {})
        groups = {g['title']: g for g in result['groups']}
        # Daily Diagnostic has 3 ready (Rigby) + 1 archived (ResearchAgent) = 4
        self.assertEqual(groups['Daily Diagnostic']['count'], 4)
        self.assertEqual(groups['Weekly Roundup']['count'], 2)

    def test_sort_by_count_desc_then_last_created_at_desc(self):
        result = _dup(self.user.id, {})
        groups = result['groups']
        # Heaviest first.
        self.assertEqual(groups[0]['title'], 'Daily Diagnostic')

    def test_agent_name_distribution_shape(self):
        result = _dup(self.user.id, {})
        groups = {g['title']: g for g in result['groups']}
        dist = groups['Daily Diagnostic']['agent_name_distribution']
        self.assertEqual(dist.get('Rigby'), 3)
        self.assertEqual(dist.get('ResearchAgent'), 1)

    def test_status_distribution_shape(self):
        result = _dup(self.user.id, {})
        groups = {g['title']: g for g in result['groups']}
        dist = groups['Daily Diagnostic']['status_distribution']
        self.assertEqual(dist.get('ready'), 3)
        self.assertEqual(dist.get('archived'), 1)

    def test_min_count_threshold_overrides_default(self):
        """min_count=3 hides the 2-row Weekly Roundup group."""
        result = _dup(self.user.id, {'min_count': 3})
        titles = self._titles(result)
        self.assertIn('Daily Diagnostic', titles)
        self.assertNotIn('Weekly Roundup', titles)

    def test_total_groups_above_threshold_reflects_filter(self):
        result = _dup(self.user.id, {'min_count': 3})
        self.assertEqual(result['total_groups_above_threshold'], 1)
        self.assertEqual(result['count'], 1)


class ExcludeArchivedTests(TestCase):
    """Truthy-only check + show_all bypass semantics for exclude_archived."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s1227-dup-archived', password='x', is_staff=True,
        )
        # 2 ready dupes
        for _ in range(2):
            Deliverable.objects.create(
                title='ArchTest Dup', content='x' * 200,
                agent_name='Rigby', user=self.user, status='ready',
            )
        # 1 archived dup
        Deliverable.objects.create(
            title='ArchTest Dup', content='x' * 200,
            agent_name='Rigby', user=self.user, status='archived',
        )

    def test_default_includes_archived_rows_in_count(self):
        result = _dup(self.user.id, {})
        groups = {g['title']: g for g in result['groups']}
        # 2 ready + 1 archived = 3 total counted.
        self.assertEqual(groups['ArchTest Dup']['count'], 3)

    def test_exclude_archived_true_drops_archived_rows(self):
        result = _dup(self.user.id, {'exclude_archived': True})
        groups = {g['title']: g for g in result['groups']}
        # Only the 2 ready rows counted now.
        self.assertEqual(groups['ArchTest Dup']['count'], 2)
        self.assertTrue(
            result['applied_filters'].get('exclude_archived')
        )

    def test_exclude_archived_python_false_is_no_op_autofill_safety(self):
        """Mirror PR1 — Python bool False on optional boolean filters is autofill."""
        result = _dup(self.user.id, {'exclude_archived': False})
        groups = {g['title']: g for g in result['groups']}
        # Same as default — archived counted.
        self.assertEqual(groups['ArchTest Dup']['count'], 3)
        self.assertNotIn(
            'exclude_archived', result['applied_filters']
        )

    def test_show_all_bypasses_exclude_archived(self):
        result = _dup(
            self.user.id,
            {'exclude_archived': True, 'show_all': True},
        )
        groups = {g['title']: g for g in result['groups']}
        # show_all wins — archived rows visible again.
        self.assertEqual(groups['ArchTest Dup']['count'], 3)
        self.assertNotIn(
            'exclude_archived', result['applied_filters']
        )
        self.assertTrue(result['show_all'])


class GroupByTests(TestCase):
    """group_by accepts title / title+agent_name / title+category."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s1227-dup-groupby', password='x', is_staff=True,
        )
        # Same title, different agents — should collapse with default
        # group_by=['title'] but split with ['title','agent_name'].
        for agent in ('Rigby', 'Rigby', 'ResearchAgent', 'ResearchAgent'):
            Deliverable.objects.create(
                title='Shared Title', content='x' * 200,
                agent_name=agent, user=self.user, status='ready',
            )

    def test_default_collapses_across_agents(self):
        result = _dup(self.user.id, {})
        groups = result['groups']
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]['count'], 4)

    def test_group_by_title_and_agent_splits(self):
        result = _dup(self.user.id, {'group_by': ['title', 'agent_name']})
        groups = result['groups']
        # Two groups: (Shared Title, Rigby)=2 + (Shared Title, ResearchAgent)=2
        self.assertEqual(len(groups), 2)
        for g in groups:
            self.assertEqual(g['count'], 2)
            self.assertIn(
                g['agent_name'], ('Rigby', 'ResearchAgent'),
            )

    def test_group_by_invalid_raises(self):
        with self.assertRaises(ValueError):
            _dup(self.user.id, {'group_by': ['title', 'status']})


class WindowDaysTests(TestCase):
    """last_Nd_count uses a rolling window from now."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s1227-dup-window', password='x', is_staff=True,
        )
        # 2 dupes created NOW
        for _ in range(2):
            Deliverable.objects.create(
                title='Window Probe', content='x' * 200,
                agent_name='Rigby', user=self.user, status='ready',
            )
        # 1 dupe backdated 30 days
        old = Deliverable.objects.create(
            title='Window Probe', content='x' * 200,
            agent_name='Rigby', user=self.user, status='ready',
        )
        old.created_at = timezone.now() - timedelta(days=30)
        old.save(update_fields=['created_at'])

    def test_default_window_7_counts_only_recent(self):
        result = _dup(self.user.id, {})
        groups = {g['title']: g for g in result['groups']}
        self.assertEqual(groups['Window Probe']['count'], 3)
        self.assertEqual(groups['Window Probe']['last_7d_count'], 2)
        self.assertEqual(result['window_days'], 7)

    def test_custom_window_60_includes_all(self):
        result = _dup(self.user.id, {'window_days': 60})
        groups = {g['title']: g for g in result['groups']}
        self.assertEqual(groups['Window Probe']['last_7d_count'], 3)
        self.assertEqual(result['window_days'], 60)


class IntAutofillSafetyTests(TestCase):
    """LLM autofills declared int params with 0; treat as use-default.

    Mirror of PR1's truthy-only check on boolean filters
    (feedback_llm_autofills_boolean_params_with_false). Without this,
    `deliverable_tool action=duplicates` would always return 0 rows because
    the LLM passes `limit: 0` even when the user never asked.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='s1227-dup-intsafety', password='x', is_staff=True,
        )
        for _ in range(3):
            Deliverable.objects.create(
                title='IntAutofill Probe',
                content='x' * 200,
                agent_name='Rigby',
                user=self.user,
                status='ready',
            )

    def test_limit_zero_treated_as_default_50(self):
        """LLM passes limit=0 → handler still returns the default 50 cap."""
        result = _dup(self.user.id, {'limit': 0})
        # Group should still appear (not 0 rows).
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['applied_filters']['limit'], 50)

    def test_window_days_zero_treated_as_default_7(self):
        """LLM passes window_days=0 → handler still uses default 7-day window."""
        result = _dup(self.user.id, {'window_days': 0})
        self.assertEqual(result['window_days'], 7)
        self.assertEqual(result['applied_filters']['window_days'], 7)

    def test_min_count_zero_treated_as_default_2(self):
        """LLM passes min_count=0 → falls back to default floor of 2."""
        result = _dup(self.user.id, {'min_count': 0})
        self.assertEqual(result['applied_filters']['min_count'], 2)


class AppliedFiltersEchoTests(TestCase):
    """Response includes the param echo per PR1 convention."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s1227-dup-echo', password='x', is_staff=True,
        )
        for _ in range(2):
            Deliverable.objects.create(
                title='Echo Probe', content='x' * 200,
                agent_name='Rigby', user=self.user, status='ready',
            )

    def test_applied_filters_records_defaults(self):
        result = _dup(self.user.id, {})
        af = result['applied_filters']
        self.assertEqual(af['group_by'], ['title'])
        self.assertEqual(af['min_count'], 2)
        self.assertEqual(af['limit'], 50)
        self.assertEqual(af['window_days'], 7)

    def test_applied_filters_records_overrides(self):
        result = _dup(
            self.user.id,
            {'min_count': 3, 'window_days': 14, 'limit': 25},
        )
        af = result['applied_filters']
        self.assertEqual(af['min_count'], 3)
        self.assertEqual(af['window_days'], 14)
        self.assertEqual(af['limit'], 25)
