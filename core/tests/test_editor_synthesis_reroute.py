"""
Session 1098 Fix A: EditorAgent synthesis-intent reroute.
========================================================

Rigby's priority #4 remediation (conversation pa-3c7ddc058db1). When an
LLM-generated next_step asks EditorAgent to synthesize multiple briefs,
the dispatcher layer should reroute to ContentWriterAgent — EditorAgent
edits, it does not generate from thin air (editor_fail_loud memory rule).

Tests the dispatcher-layer helper:
    core.services.editor_dispatch_helpers.reroute_synthesis_to_content_writer

And covers the four scenarios Rigby asked for:
    1. Synthesis task with no content → reroute
    2. Non-synthesis task (edit) → no reroute
    3. Synthesis task BUT explicit blog_id/content → no reroute
    4. Feature flag off → no reroute

Plus pattern-matching coverage on detect_synthesis_intent so false
positives stay low (the regex is intentionally conservative — we would
rather miss a synthesis-intent case than misroute a legitimate edit).

Run:
    python manage.py test core.tests.test_editor_synthesis_reroute -v2
"""

from unittest import mock

from django.test import SimpleTestCase, override_settings

from core.services.editor_dispatch_helpers import (
    detect_synthesis_intent,
    reroute_synthesis_to_content_writer,
)


# =========================================================================
# detect_synthesis_intent — pure regex, no DB
# =========================================================================


class DetectSynthesisIntentTests(SimpleTestCase):

    def test_synthesize_with_briefs(self):
        self.assertTrue(detect_synthesis_intent(
            "Synthesize the Platform Audit, CTO Analysis, and COO "
            "Analysis into a publish-ready Executive Brief."
        ))

    def test_combine_analyses(self):
        self.assertTrue(detect_synthesis_intent(
            "Combine these two analyses into one memo"
        ))

    def test_merge_briefs(self):
        self.assertTrue(detect_synthesis_intent(
            "Merge the research briefs into a single summary"
        ))

    def test_consolidate_sources(self):
        self.assertTrue(detect_synthesis_intent(
            "Consolidate these sources into a final report"
        ))

    def test_integrate_findings(self):
        self.assertTrue(detect_synthesis_intent(
            "Integrate the findings from all three reports"
        ))

    def test_edit_is_not_synthesis(self):
        """Pure edit task does not look like synthesis."""
        self.assertFalse(detect_synthesis_intent(
            "Tighten the opening paragraph and fix typos"
        ))

    def test_rewrite_is_not_synthesis(self):
        """Rewrite + blog_id is a classic edit task, not synthesis."""
        self.assertFalse(detect_synthesis_intent(
            "Rewrite the blog (blog_id=abc-123) for a different audience"
        ))

    def test_synthesis_as_object_is_not_trigger(self):
        """'Edit the synthesis' — synthesis here is the object, not the
        action. Must NOT reroute.

        The verb/object window forces a verb (synthesize/combine/...)
        to be immediately followed by a source-target noun within 60
        chars. 'Edit the synthesis for clarity' has no verb in that
        form so the pattern does not match.
        """
        self.assertFalse(detect_synthesis_intent(
            "Edit the synthesis for clarity"
        ))

    def test_empty_task_is_false(self):
        self.assertFalse(detect_synthesis_intent(""))
        self.assertFalse(detect_synthesis_intent(None))

    def test_synthesis_noun_without_verb_is_false(self):
        """Mentioning 'briefs' alone is not enough — verb must be there."""
        self.assertFalse(detect_synthesis_intent(
            "Please review the briefs and tell me what's missing"
        ))


# =========================================================================
# reroute_synthesis_to_content_writer — the dispatcher-level swap
# =========================================================================


class RerouteSynthesisTests(SimpleTestCase):

    def _reroute(self, agent_name, task_text, context):
        # Patch gather_workspace_content_for_editor so tests don't
        # touch the DB — we only care about the dispatch decision here.
        with mock.patch(
            'core.services.editor_dispatch_helpers.'
            'gather_workspace_content_for_editor',
            return_value=None,
        ):
            return reroute_synthesis_to_content_writer(
                agent_name, task_text, context,
            )

    def test_synthesis_task_reroutes(self):
        new_agent, new_ctx = self._reroute(
            'EditorAgent',
            'Synthesize the CTO brief and COO brief into an executive memo',
            {'workspace_id': 'ws-1'},
        )
        self.assertEqual(new_agent, 'ContentWriterAgent')
        self.assertEqual(
            new_ctx.get('routing_hint'),
            'synthesis_reroute_from_EditorAgent',
        )

    def test_edit_task_does_not_reroute(self):
        new_agent, new_ctx = self._reroute(
            'EditorAgent',
            'Tighten this blog post and fix typos',
            {'workspace_id': 'ws-1'},
        )
        self.assertEqual(new_agent, 'EditorAgent')
        self.assertNotIn('routing_hint', new_ctx)

    def test_synthesis_task_with_blog_id_does_not_reroute(self):
        """Explicit blog_id means 'edit this specific blog' — keep Editor."""
        new_agent, _ = self._reroute(
            'EditorAgent',
            'Synthesize the briefs into this doc',
            {'workspace_id': 'ws-1', 'blog_id': 'abc-123'},
        )
        self.assertEqual(new_agent, 'EditorAgent')

    def test_synthesis_task_with_content_does_not_reroute(self):
        """Explicit content means caller knows what to edit — keep Editor."""
        new_agent, _ = self._reroute(
            'EditorAgent',
            'Combine these analyses into one doc',
            {'workspace_id': 'ws-1', 'content': {'full_text': 'existing'}},
        )
        self.assertEqual(new_agent, 'EditorAgent')

    def test_non_editor_agent_passes_through(self):
        new_agent, new_ctx = self._reroute(
            'ResearchAgent',
            'Synthesize the briefs',
            {},
        )
        self.assertEqual(new_agent, 'ResearchAgent')
        self.assertNotIn('routing_hint', new_ctx)

    @override_settings(EDITOR_SYNTHESIS_REROUTE_ENABLED=False)
    def test_feature_flag_off_skips_reroute(self):
        new_agent, new_ctx = self._reroute(
            'EditorAgent',
            'Synthesize the briefs into one memo',
            {'workspace_id': 'ws-1'},
        )
        self.assertEqual(new_agent, 'EditorAgent')
        self.assertNotIn('routing_hint', new_ctx)

    def test_gathered_sources_populate_research(self):
        """When gather returns sources, they land in context['research']
        under ContentWriterAgent's expected key."""
        fake_sources = {
            'sources': [
                {'title': 'CTO Brief', 'content': 'CTO body'},
                {'title': 'COO Brief', 'content': 'COO body'},
            ],
        }
        with mock.patch(
            'core.services.editor_dispatch_helpers.'
            'gather_workspace_content_for_editor',
            return_value=fake_sources,
        ):
            new_agent, new_ctx = reroute_synthesis_to_content_writer(
                'EditorAgent',
                'Synthesize the briefs into an exec memo',
                {'workspace_id': 'ws-1'},
            )
        self.assertEqual(new_agent, 'ContentWriterAgent')
        self.assertIn('## CTO Brief', new_ctx['research'])
        self.assertIn('CTO body', new_ctx['research'])
        self.assertIn('## COO Brief', new_ctx['research'])
        self.assertIn('COO body', new_ctx['research'])

    def test_reroute_without_sources_still_swaps_agent(self):
        """Gather returns None → still reroute, just no research context.
        ContentWriterAgent can fall back to generating from the task
        text alone — that's preferable to EditorAgent's fail-loud.
        """
        new_agent, new_ctx = self._reroute(
            'EditorAgent',
            'Synthesize the 3 briefs into an executive brief',
            {'workspace_id': 'ws-1'},
        )
        self.assertEqual(new_agent, 'ContentWriterAgent')
        self.assertNotIn('research', new_ctx)
        self.assertEqual(
            new_ctx['routing_hint'],
            'synthesis_reroute_from_EditorAgent',
        )

    def test_original_context_is_not_mutated(self):
        """The helper returns a NEW dict — caller's dict must be untouched
        so a reroute is a pure functional swap at dispatch time.
        """
        original = {'workspace_id': 'ws-1'}
        new_agent, new_ctx = self._reroute(
            'EditorAgent',
            'Synthesize the briefs',
            original,
        )
        self.assertIsNot(new_ctx, original)
        self.assertNotIn('routing_hint', original)
