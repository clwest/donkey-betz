"""Session 1226 — deliverable_tool.list has_initiative filter tests.

Closes the agent → deliverable → initiative cross-query gap Chris flagged
at Session 1225 close: "I asked Rigby what agents' deliverables had
initiatives and she said she didn't have the tools to check that."

The canonical query becomes:
  deliverable_tool action=list agent='ResearchAgent' has_initiative=true
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.models_document_registry import Initiative
from core.services.tool_dispatcher import ToolDispatcher

User = get_user_model()


def _dispatch_list(user_id, payload):
    dispatcher = ToolDispatcher()
    return dispatcher._handle_deliverables(  # type: ignore[attr-defined]
        tool_name='deliverable_tool',
        payload={'action': 'list', **payload},
        user_id=user_id,
        trace_id='test-has-init',
    )


class HasInitiativeFilterTests(TestCase):
    def setUp(self):
        self.chris = User.objects.create_user(
            username='chris-test', password='x', is_staff=True,
        )
        self.initiative = Initiative.objects.create(
            name='Test initiative for filter',
            description='probe',
            owner=self.chris,
        )
        # Linked deliverable (ResearchAgent)
        self.linked = Deliverable.objects.create(
            title='Linked research output',
            content='x' * 400,
            agent_name='ResearchAgent',
            user=self.chris,
            initiative=self.initiative,
        )
        # Unlinked deliverable (ResearchAgent)
        self.unlinked = Deliverable.objects.create(
            title='Unlinked research output',
            content='x' * 400,
            agent_name='ResearchAgent',
            user=self.chris,
        )
        # Linked deliverable (other agent)
        self.other_linked = Deliverable.objects.create(
            title='Linked writer output',
            content='x' * 400,
            agent_name='ContentWriterAgent',
            user=self.chris,
            initiative=self.initiative,
        )

    def _ids(self, result):
        rows = result.get('deliverables', result.get('items', []))
        return {str(d['id']) for d in rows}

    def test_has_initiative_true_returns_only_linked(self):
        result = _dispatch_list(self.chris.id, {'has_initiative': True})
        ids = self._ids(result)
        self.assertIn(str(self.linked.id), ids)
        self.assertIn(str(self.other_linked.id), ids)
        self.assertNotIn(str(self.unlinked.id), ids)

    def test_has_initiative_explicit_false_string_returns_only_unlinked(self):
        # Session 1227 — Python bool False is now LLM-autofill safe (no-op).
        # To explicitly filter for deliverables WITHOUT an initiative, callers
        # must pass the STRING 'false'. See PR1 / test_deliverable_tool_session_1227.
        result = _dispatch_list(self.chris.id, {'has_initiative': 'false'})
        ids = self._ids(result)
        self.assertIn(str(self.unlinked.id), ids)
        self.assertNotIn(str(self.linked.id), ids)
        self.assertNotIn(str(self.other_linked.id), ids)

    def test_has_initiative_with_agent_filter_combined(self):
        """The canonical query: which of ResearchAgent's deliverables have initiatives?"""
        result = _dispatch_list(
            self.chris.id,
            {'agent': 'ResearchAgent', 'has_initiative': True},
        )
        ids = self._ids(result)
        self.assertEqual(ids, {str(self.linked.id)})

    def test_has_initiative_truthy_string_works(self):
        # GPT-5.2 sometimes serializes booleans as strings
        result = _dispatch_list(self.chris.id, {'has_initiative': 'true'})
        ids = self._ids(result)
        self.assertIn(str(self.linked.id), ids)
        self.assertNotIn(str(self.unlinked.id), ids)

    def test_has_initiative_omitted_returns_everything(self):
        """Omitting the filter preserves backwards-compat list behavior."""
        result = _dispatch_list(self.chris.id, {})
        ids = self._ids(result)
        self.assertIn(str(self.linked.id), ids)
        self.assertIn(str(self.unlinked.id), ids)
        self.assertIn(str(self.other_linked.id), ids)

    def test_initiative_id_filter_still_works(self):
        """Documented in Session 1226 schema fix — initiative_id has always
        been a list filter, just wasn't surfaced in the schema description."""
        result = _dispatch_list(
            self.chris.id,
            {'initiative_id': str(self.initiative.id)},
        )
        ids = self._ids(result)
        self.assertEqual(ids, {str(self.linked.id), str(self.other_linked.id)})
