"""Session 1234 D6 — DevOpsAgent pre-save duplicate detection.

Mirror of the D5 ResearchAgent pattern. Surface from 2026-06-25
morning_brief investigation: DevOpsAgent produced 4 identical
``DevOpsAgent: DevOps: Run one-shot smoke execution of internal
WORKFLOWS['morning_brief'] …`` deliverables in workspace cf708a2e
between 02:48 and 05:25 — all manual smoke retries during the D1/D2
fail-loud arc iteration. Pre-fix the agent saved unconditionally,
turning the workspace into a junk drawer of near-identical titles.

Fix: ``_find_recent_duplicate_deliverable(title, window_minutes)``
returns a prior Deliverable matching (agent_name=self.name, title,
workspace_id=self._workspace_id) within the last ``window_minutes``.
The save site logs ``[DEVOPS_DUP_SKIPPED]`` and skips on match.

Run::

    python manage.py test core.tests.test_devops_agent_dup_skip -v2
"""

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.agents.devops_agent import DevOpsAgent
from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace

User = get_user_model()


class DevOpsAgentDuplicateDetectionTests(TestCase):
    """Verify ``_find_recent_duplicate_deliverable`` behavior on DevOpsAgent."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f"test_d6_{uuid.uuid4().hex[:8]}",
            password='test',
        )
        self.workspace = ProjectWorkspace.objects.create(
            user=self.user,
            name=f'Test WS {uuid.uuid4().hex[:8]}',
            workspace_type='local',
            root_path='/tmp/test',
            tech_stack={},
        )
        self.agent = DevOpsAgent(user=self.user)
        # Router normally sets this; test sets it directly.
        self.agent._workspace_id = str(self.workspace.id)

    def _seed_prior_deliverable(self, title, minutes_ago=0):
        d = Deliverable.objects.create(
            title=title,
            content='prior devops content',
            agent_name='DevOpsAgent',
            deliverable_type='analysis',
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
            title='DevOps: brand-new task',
        )
        self.assertIsNone(result)

    def test_returns_prior_when_same_title_within_window(self):
        prior = self._seed_prior_deliverable(
            title='DevOps: Run smoke morning_brief', minutes_ago=10,
        )
        result = self.agent._find_recent_duplicate_deliverable(
            title='DevOps: Run smoke morning_brief', window_minutes=60,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.id, prior.id)

    def test_does_not_return_prior_outside_window(self):
        """60min window MUST NOT match a 90-minute-old prior."""
        self._seed_prior_deliverable(
            title='DevOps: Run smoke morning_brief', minutes_ago=90,
        )
        result = self.agent._find_recent_duplicate_deliverable(
            title='DevOps: Run smoke morning_brief', window_minutes=60,
        )
        self.assertIsNone(result)

    def test_different_title_not_a_duplicate(self):
        self._seed_prior_deliverable(
            title='DevOps: deploy A', minutes_ago=10,
        )
        result = self.agent._find_recent_duplicate_deliverable(
            title='DevOps: deploy B', window_minutes=60,
        )
        self.assertIsNone(result)

    def test_different_workspace_not_a_duplicate(self):
        """Same title in a different workspace MUST NOT match."""
        other_ws = ProjectWorkspace.objects.create(
            user=self.user,
            name=f'Other WS {uuid.uuid4().hex[:8]}',
            workspace_type='local',
            root_path='/tmp/test_other',
            tech_stack={},
        )
        Deliverable.objects.create(
            title='DevOps: shared title',
            content='other workspace content',
            agent_name='DevOpsAgent',
            deliverable_type='analysis',
            user=self.user,
            workspace=other_ws,
            status='ready',
        )
        result = self.agent._find_recent_duplicate_deliverable(
            title='DevOps: shared title', window_minutes=60,
        )
        self.assertIsNone(result)

    def test_different_agent_name_not_a_duplicate(self):
        """A deliverable saved by a DIFFERENT agent with the same
        title doesn't suppress this agent's write."""
        Deliverable.objects.create(
            title='DevOps: shared title',
            content='from another agent',
            agent_name='CTOAgent',  # not DevOpsAgent
            deliverable_type='analysis',
            user=self.user,
            workspace=self.workspace,
            status='ready',
        )
        result = self.agent._find_recent_duplicate_deliverable(
            title='DevOps: shared title', window_minutes=60,
        )
        self.assertIsNone(result)

    def test_returns_most_recent_when_multiple_priors(self):
        """If multiple priors exist in the window, return the most recent."""
        old = self._seed_prior_deliverable(
            title='DevOps: same task', minutes_ago=30,
        )
        recent = self._seed_prior_deliverable(
            title='DevOps: same task', minutes_ago=5,
        )
        result = self.agent._find_recent_duplicate_deliverable(
            title='DevOps: same task', window_minutes=60,
        )
        self.assertEqual(result.id, recent.id)
        self.assertNotEqual(result.id, old.id)

    def test_no_workspace_id_returns_none(self):
        """No workspace context → skip the check (no global dedupe)."""
        self.agent._workspace_id = None
        Deliverable.objects.create(
            title='DevOps: Run smoke',
            content='exists',
            agent_name='DevOpsAgent',
            deliverable_type='analysis',
            user=self.user,
            workspace=self.workspace,
            status='ready',
        )
        result = self.agent._find_recent_duplicate_deliverable(
            title='DevOps: Run smoke',
        )
        self.assertIsNone(result)

    def test_empty_title_returns_none(self):
        result = self.agent._find_recent_duplicate_deliverable(title='')
        self.assertIsNone(result)


class DevOpsAgentDupSkipSourceGuardTests(TestCase):
    """Source-level guard: save site checks for duplicates BEFORE
    calling ``_save_to_deliverable``, and emits the structured
    [DEVOPS_DUP_SKIPPED] log line."""

    def test_save_site_has_dup_check_before_save(self):
        import inspect
        src = inspect.getsource(DevOpsAgent.execute)
        dup_check_pos = src.find('_find_recent_duplicate_deliverable')
        log_pos = src.find('[DEVOPS_DUP_SKIPPED]')
        save_pos = src.find('self._save_to_deliverable(')

        self.assertGreater(dup_check_pos, -1,
                           "execute() must call _find_recent_duplicate_deliverable.")
        self.assertGreater(log_pos, -1,
                           "execute() must emit [DEVOPS_DUP_SKIPPED] on match.")
        self.assertGreater(save_pos, -1,
                           "execute() must still call _save_to_deliverable.")

        self.assertLess(
            dup_check_pos, save_pos,
            "_find_recent_duplicate_deliverable must be called BEFORE "
            "_save_to_deliverable so duplicates can short-circuit.",
        )
        self.assertLess(
            log_pos, save_pos,
            "[DEVOPS_DUP_SKIPPED] log must fire BEFORE the save site "
            "(it's the alternative branch, not a follow-up).",
        )
