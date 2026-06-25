"""Session 1234 D5 — ResearchAgent pre-save duplicate detection.

Surface from 2026-06-25 morning_brief investigation: ResearchAgent
produced 8 identical ``Research: Market trends and industry landscape``
deliverables in workspace cf708a2e-… within 4.5 hours (00:58 → 05:23),
all root dispatches (parent_execution_id=None — not workflow-tree
retries, but operator/PA iteration storms). Pre-fix the agent saved
unconditionally, turning the workspace into a junk drawer of
near-identical titles.

Fix: ``_find_recent_duplicate_deliverable(title, window_minutes)``
returns a prior Deliverable matching (agent_name=self.name, title,
workspace_id=self._workspace_id) within the last ``window_minutes``.
The save site logs ``[RESEARCH_DUP_SKIPPED]`` and skips on match.

Run::

    python manage.py test core.tests.test_research_agent_dup_skip -v2
"""

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.agents.research_agent import ResearchAgent
from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace

User = get_user_model()


class ResearchAgentDuplicateDetectionTests(TestCase):
    """Verify ``_find_recent_duplicate_deliverable`` behavior."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f"test_dup_{uuid.uuid4().hex[:8]}",
            password='test',
        )
        self.workspace = ProjectWorkspace.objects.create(
            user=self.user,
            name=f'Test WS {uuid.uuid4().hex[:8]}',
            workspace_type='local',
            root_path='/tmp/test',
            tech_stack={},
        )
        self.agent = ResearchAgent(user=self.user)
        # Router normally sets this; test sets it directly.
        self.agent._workspace_id = str(self.workspace.id)

    def _seed_prior_deliverable(self, title, minutes_ago=0):
        d = Deliverable.objects.create(
            title=title,
            content='prior research content',
            agent_name='ResearchAgent',
            deliverable_type='research',
            user=self.user,
            workspace=self.workspace,
            status='ready',
        )
        if minutes_ago:
            new_ts = timezone.now() - timedelta(minutes=minutes_ago)
            Deliverable.objects.filter(id=d.id).update(created_at=new_ts)
            d.refresh_from_db()
        return d

    def test_returns_none_when_no_prior(self):
        result = self.agent._find_recent_duplicate_deliverable(
            title='Research: brand-new topic',
        )
        self.assertIsNone(result)

    def test_returns_prior_when_same_title_within_window(self):
        prior = self._seed_prior_deliverable(
            title='Research: market trends', minutes_ago=10,
        )
        result = self.agent._find_recent_duplicate_deliverable(
            title='Research: market trends', window_minutes=60,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.id, prior.id)

    def test_does_not_return_prior_outside_window(self):
        """A 60min window MUST NOT match a 90-minute-old prior."""
        self._seed_prior_deliverable(
            title='Research: market trends', minutes_ago=90,
        )
        result = self.agent._find_recent_duplicate_deliverable(
            title='Research: market trends', window_minutes=60,
        )
        self.assertIsNone(result)

    def test_different_title_not_a_duplicate(self):
        self._seed_prior_deliverable(
            title='Research: topic A', minutes_ago=10,
        )
        result = self.agent._find_recent_duplicate_deliverable(
            title='Research: topic B', window_minutes=60,
        )
        self.assertIsNone(result)

    def test_different_workspace_not_a_duplicate(self):
        """Same title in a different workspace MUST NOT match — the
        dedupe is scoped per workspace (Chris can run the same query
        in different contexts and expect separate deliverables)."""
        other_ws = ProjectWorkspace.objects.create(
            user=self.user,
            name=f'Other WS {uuid.uuid4().hex[:8]}',
            workspace_type='local',
            root_path='/tmp/test_other',
            tech_stack={},
        )
        Deliverable.objects.create(
            title='Research: shared title',
            content='other workspace content',
            agent_name='ResearchAgent',
            deliverable_type='research',
            user=self.user,
            workspace=other_ws,
            status='ready',
        )
        result = self.agent._find_recent_duplicate_deliverable(
            title='Research: shared title', window_minutes=60,
        )
        self.assertIsNone(result)

    def test_different_agent_name_not_a_duplicate(self):
        """A deliverable saved by a DIFFERENT agent with the same
        title doesn't suppress this agent's write."""
        Deliverable.objects.create(
            title='Research: shared title',
            content='from another agent',
            agent_name='TrendAnalysisAgent',  # not ResearchAgent
            deliverable_type='research',
            user=self.user,
            workspace=self.workspace,
            status='ready',
        )
        result = self.agent._find_recent_duplicate_deliverable(
            title='Research: shared title', window_minutes=60,
        )
        self.assertIsNone(result)

    def test_returns_most_recent_when_multiple_priors(self):
        """If multiple priors exist in the window, return the most recent."""
        old = self._seed_prior_deliverable(
            title='Research: same query', minutes_ago=30,
        )
        recent = self._seed_prior_deliverable(
            title='Research: same query', minutes_ago=5,
        )
        result = self.agent._find_recent_duplicate_deliverable(
            title='Research: same query', window_minutes=60,
        )
        self.assertEqual(result.id, recent.id)
        self.assertNotEqual(result.id, old.id)

    def test_no_workspace_id_returns_none(self):
        """If the agent has no workspace context, skip the check
        (don't fall through to a global dedupe)."""
        self.agent._workspace_id = None
        Deliverable.objects.create(
            title='Research: market trends',
            content='exists',
            agent_name='ResearchAgent',
            deliverable_type='research',
            user=self.user,
            workspace=self.workspace,
            status='ready',
        )
        result = self.agent._find_recent_duplicate_deliverable(
            title='Research: market trends',
        )
        self.assertIsNone(result)

    def test_empty_title_returns_none(self):
        result = self.agent._find_recent_duplicate_deliverable(title='')
        self.assertIsNone(result)


class ResearchAgentDupSkipSourceGuardTests(TestCase):
    """Source-level guard: the save-site checks for duplicates BEFORE
    calling ``_save_to_deliverable``, and emits the structured
    [RESEARCH_DUP_SKIPPED] log line.
    """

    def test_save_site_has_dup_check_before_save(self):
        import inspect
        src = inspect.getsource(ResearchAgent.execute)
        dup_check_pos = src.find('_find_recent_duplicate_deliverable')
        log_pos = src.find('[RESEARCH_DUP_SKIPPED]')
        save_pos = src.find('self._save_to_deliverable(')

        self.assertGreater(dup_check_pos, -1,
                           "execute() must call _find_recent_duplicate_deliverable.")
        self.assertGreater(log_pos, -1,
                           "execute() must emit [RESEARCH_DUP_SKIPPED] on match.")
        self.assertGreater(save_pos, -1,
                           "execute() must still call _save_to_deliverable.")

        self.assertLess(
            dup_check_pos, save_pos,
            "_find_recent_duplicate_deliverable must be called BEFORE "
            "_save_to_deliverable so duplicates can short-circuit.",
        )
        self.assertLess(
            log_pos, save_pos,
            "[RESEARCH_DUP_SKIPPED] log must fire BEFORE the save site "
            "(it's the alternative branch, not a follow-up).",
        )
