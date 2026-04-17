"""
Session 1098 PR-B — EditorAgent canary wire-up.

EditorAgent's `_save_to_deliverable` call at the end of execute() must
forward canary kwargs (append_to_deliverable_id, expected_initiative_id,
append_chunk_index) when the caller passes them in context. This is the
organic trigger path for the DELIVERABLE_APPEND canary once the env
allowlist includes EditorAgent.

Run::

    python manage.py test core.tests.test_editor_agent_canary_wire -v2
"""

from unittest import mock

from django.test import SimpleTestCase

from core.agents.editor_agent import EditorAgent


class _FakeLLM:
    """Stand-in for the LLM call inside EditorAgent._enhance_with_llm."""

    def __call__(self, *args, **kwargs):
        return {
            'title': 'Enhanced Title',
            'intro': 'Enhanced intro paragraph.',
            'sections': [{'heading': 'S1', 'content': 'Enhanced section one.'}],
            'conclusion': 'Enhanced conclusion.',
            'meta_description': 'meta',
            'changes_made': ['tightened lede', 'added citation'],
        }


class EditorAgentCanaryWireTests(SimpleTestCase):

    def _base_context(self, **overrides):
        ctx = {
            'content': {
                'title': 'Original Title',
                'intro': 'Original intro.',
                'sections': [{'heading': 'Old', 'content': 'Old body'}],
                'conclusion': 'Old conclusion.',
                'meta_description': 'old meta',
            },
            'focus_areas': ['engagement', 'structure'],
            'save': False,
            'workspace_id': 'ws-123',
        }
        ctx.update(overrides)
        return ctx

    def test_append_kwargs_forwarded_to_save(self):
        """When context contains append_to_deliverable_id +
        expected_initiative_id, _save_to_deliverable is called with both
        (plus append_chunk_index=0 default)."""
        agent = EditorAgent()

        ctx = self._base_context(
            append_to_deliverable_id='deliv-abc',
            expected_initiative_id='init-xyz',
        )

        with mock.patch.object(
            EditorAgent, '_enhance_with_llm', _FakeLLM()
        ), mock.patch.object(
            EditorAgent, '_save_to_deliverable'
        ) as mocked_save:
            result = agent.execute(
                task='Repair blog (enhance): Test blog',
                context=ctx,
                scifi_context={},
                spider_context={},
            )

        self.assertTrue(result.success, f'execute failed: {result.error}')
        mocked_save.assert_called_once()
        _, kwargs = mocked_save.call_args
        self.assertEqual(kwargs.get('append_to_deliverable_id'), 'deliv-abc')
        self.assertEqual(kwargs.get('expected_initiative_id'), 'init-xyz')
        self.assertEqual(kwargs.get('append_chunk_index'), 0)

    def test_missing_append_kwargs_passes_none(self):
        """Pre-canary callers don't set these keys — save gets
        None for both (gate in BaseAgent falls through to create)."""
        agent = EditorAgent()
        ctx = self._base_context()  # no append kwargs

        with mock.patch.object(
            EditorAgent, '_enhance_with_llm', _FakeLLM()
        ), mock.patch.object(
            EditorAgent, '_save_to_deliverable'
        ) as mocked_save:
            result = agent.execute(
                task='Edit blog',
                context=ctx,
                scifi_context={},
                spider_context={},
            )

        self.assertTrue(result.success)
        mocked_save.assert_called_once()
        _, kwargs = mocked_save.call_args
        self.assertIsNone(kwargs.get('append_to_deliverable_id'))
        self.assertIsNone(kwargs.get('expected_initiative_id'))
