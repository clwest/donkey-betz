"""
Session 1098 Fix B-full canary adoption — BaseAgent gate tests.
==============================================================

Covers the three paths through the canary gate in
``BaseAgent._save_to_deliverable`` (see the addendum doc for the gate
contract):

    1. Canary OFF (flag False) → falls through to ``create_deliverable``
    2. Canary ON + agent IN allowlist → routes to ``append_to_deliverable``
    3. Canary ON + agent NOT in allowlist → falls through

Plus two regression cases:
    4. No append_to_deliverable_id kwarg → falls through regardless
    5. Canary ON path returns a Deliverable-like object (same contract
       as the create path)

Run::

    python manage.py test core.tests.test_deliverable_append_canary -v2
"""

import uuid
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from core.models import Deliverable, Initiative
from core.models_deliverable_appends import DeliverableAppend
from core.models_skin_layer import ProjectWorkspace


User = get_user_model()


def _make_test_data(cls):
    cls.user = User.objects.create_user(
        username=f'canary-test-{uuid.uuid4().hex[:8]}',
        email='canary@example.com',
        password='x',
        is_superuser=True,
    )
    cls.workspace = ProjectWorkspace.objects.create(
        user=cls.user, name='Canary Test Workspace',
        allow_autonomous_writes=True,
    )
    cls.initiative = Initiative.objects.create(
        name='Canary Test Initiative', status='ACTIVE', current_stage=1,
    )
    cls.deliverable = Deliverable.objects.create(
        title='Canary Target Deliverable',
        content='initial — ',
        agent_name='ContentWriterAgent',
        category='Test',
        deliverable_type='document',
        user=cls.user,
        workspace_id=str(cls.workspace.id),
        initiative_id=str(cls.initiative.id),
    )


def _make_agent(user):
    """Use a real BaseAgent subclass. Using EditorAgent here only
    because it's already importable + concrete — we override .name
    to match the canary allowlist entry."""
    from core.agents.editor_agent import EditorAgent

    agent = EditorAgent(user=user)
    agent.name = 'ContentWriterAgent'  # Match Step-1 allowlist
    agent._workspace_id = None
    return agent


class CanaryGateTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        _make_test_data(cls)

    # ── 1. Canary OFF: flag=False, allowlist=[] ──────────────────────

    @override_settings(
        DELIVERABLE_APPEND_ENABLED=False,
        DELIVERABLE_APPEND_CANARY_AGENTS=[],
    )
    def test_canary_off_falls_through_to_create(self):
        """When the flag is False, the explicit append kwargs are
        ignored and create_deliverable runs normally. Confirms no
        silent routing."""
        agent = _make_agent(self.user)
        before_appends = DeliverableAppend.objects.count()

        with mock.patch(
            'core.services.deliverable_factory.create_deliverable',
            return_value=self.deliverable,
        ) as mocked_create:
            result = agent._save_to_deliverable(
                title='canary-off test',
                content='x' * 400,  # above quality gate
                workspace_id=str(self.workspace.id),
                append_to_deliverable_id=str(self.deliverable.id),
                append_call_id=str(uuid.uuid4()),
            )

        mocked_create.assert_called_once()
        self.assertIs(result, self.deliverable)
        # No DeliverableAppend row written.
        self.assertEqual(
            DeliverableAppend.objects.count(), before_appends,
            'canary-off must not create append rows',
        )

    # ── 2. Canary ON + agent IN allowlist ────────────────────────────

    @override_settings(
        DELIVERABLE_APPEND_ENABLED=True,
        DELIVERABLE_APPEND_CANARY_AGENTS=['ContentWriterAgent'],
    )
    def test_canary_on_matching_agent_routes_to_append(self):
        """ContentWriterAgent with flag+allowlist both on → routes to
        append_to_deliverable. A DeliverableAppend row gets committed
        and Deliverable.content grows."""
        agent = _make_agent(self.user)
        call_id = str(uuid.uuid4())
        before_content = self.deliverable.content

        result = agent._save_to_deliverable(
            title='canary-on test',
            content='CANARY_ADDITION',
            workspace_id=str(self.workspace.id),
            append_to_deliverable_id=str(self.deliverable.id),
            append_call_id=call_id,
            expected_initiative_id=str(self.initiative.id),
        )

        # Return value is a Deliverable-like object (the target).
        self.assertIsNotNone(result)
        self.assertEqual(str(result.id), str(self.deliverable.id))

        # Deliverable.content now includes the append.
        self.deliverable.refresh_from_db()
        self.assertIn('CANARY_ADDITION', self.deliverable.content)
        self.assertNotEqual(before_content, self.deliverable.content)

        # A DeliverableAppend row committed for this call_id.
        append = DeliverableAppend.objects.get(
            call_id=call_id,
            deliverable_id=self.deliverable.id,
        )
        self.assertEqual(append.status, 'committed')
        self.assertEqual(append.agent_name, 'ContentWriterAgent')

    # ── 3. Canary ON + agent NOT in allowlist ─────────────────────────

    @override_settings(
        DELIVERABLE_APPEND_ENABLED=True,
        DELIVERABLE_APPEND_CANARY_AGENTS=['ContentWriterAgent'],
    )
    def test_canary_on_non_matching_agent_falls_through(self):
        """Flag is on but this agent isn't on the allowlist → falls
        through to create_deliverable. No DeliverableAppend row."""
        from core.agents.editor_agent import EditorAgent

        agent = EditorAgent(user=self.user)
        agent.name = 'SomeOtherAgent'  # NOT in allowlist
        agent._workspace_id = None
        before_appends = DeliverableAppend.objects.count()

        with mock.patch(
            'core.services.deliverable_factory.create_deliverable',
            return_value=self.deliverable,
        ) as mocked_create:
            result = agent._save_to_deliverable(
                title='non-matching agent test',
                content='x' * 400,
                workspace_id=str(self.workspace.id),
                append_to_deliverable_id=str(self.deliverable.id),
                append_call_id=str(uuid.uuid4()),
            )

        mocked_create.assert_called_once()
        self.assertIs(result, self.deliverable)
        self.assertEqual(
            DeliverableAppend.objects.count(), before_appends,
            'non-matching agent must not route to append',
        )

    # ── 4. No append_to_deliverable_id — default create path ─────────

    @override_settings(
        DELIVERABLE_APPEND_ENABLED=True,
        DELIVERABLE_APPEND_CANARY_AGENTS=['ContentWriterAgent'],
    )
    def test_no_append_target_id_falls_through(self):
        """Flag+allowlist both on, but no append_to_deliverable_id →
        canary is OPT-IN per call site. Falls through."""
        agent = _make_agent(self.user)
        before_appends = DeliverableAppend.objects.count()

        with mock.patch(
            'core.services.deliverable_factory.create_deliverable',
            return_value=self.deliverable,
        ) as mocked_create:
            agent._save_to_deliverable(
                title='no target id test',
                content='x' * 400,
                workspace_id=str(self.workspace.id),
                # NOTE: no append_to_deliverable_id
            )

        mocked_create.assert_called_once()
        self.assertEqual(
            DeliverableAppend.objects.count(), before_appends,
            'missing append_to_deliverable_id must not trigger canary',
        )

    # ── 5. Empty allowlist but flag ON → falls through ────────────────

    @override_settings(
        DELIVERABLE_APPEND_ENABLED=True,
        DELIVERABLE_APPEND_CANARY_AGENTS=[],
    )
    def test_flag_on_empty_allowlist_falls_through(self):
        """Empty allowlist = no agents opted in yet. Flag alone is not
        sufficient — must have explicit agent-name membership.
        Protects against accidental global activation via a single env
        flip."""
        agent = _make_agent(self.user)
        before_appends = DeliverableAppend.objects.count()

        with mock.patch(
            'core.services.deliverable_factory.create_deliverable',
            return_value=self.deliverable,
        ) as mocked_create:
            agent._save_to_deliverable(
                title='empty allowlist test',
                content='x' * 400,
                workspace_id=str(self.workspace.id),
                append_to_deliverable_id=str(self.deliverable.id),
            )

        mocked_create.assert_called_once()
        self.assertEqual(
            DeliverableAppend.objects.count(), before_appends,
            'empty allowlist must not activate canary',
        )
