"""Session 1238 PR-4 — Lane 3 adaptive no-signal + MUSCULAR plain-English.

Four test classes:

1. ``LaneThreeNoSignalDetectorTests`` — `_lane_3_is_no_signal` heuristic.

2. ``LaneThreeNoSignalFallbackContentTests`` — fallback template
   includes coverage map + 3 watch items + action line.

3. ``MuscularPlainEnglishHumanizerTests`` — `_humanize_body_system_jargon`
   replaces insider terms with plain English while preserving the
   `[MUSCULAR]` tag.

4. ``MorningBriefSynthesisInputsIntegrationTests`` — both helpers fire
   from `_execute_strategic_synthesis_step` morning_brief mode and
   inject the expected keys / substitutions.

Per `feedback_test_real_db_for_queryset_semantics`: real DB; mocks at
`openai_client_factory.get_openai_client` boundary.

Run::

    python manage.py test core.tests.test_lane_3_adaptive_and_muscular_terminology -v 2 --keepdb
"""

import uuid
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.services.workflow_orchestration_agent import (
    WorkflowOrchestrationAgent,
)

User = get_user_model()


class LaneThreeNoSignalDetectorTests(TestCase):

    def test_empty_text_is_no_signal(self):
        self.assertTrue(WorkflowOrchestrationAgent._lane_3_is_no_signal(''))

    def test_short_text_is_no_signal(self):
        self.assertTrue(WorkflowOrchestrationAgent._lane_3_is_no_signal('Brief.'))

    def test_no_confirmed_marker_is_no_signal(self):
        text = "Findings: No confirmed competitor change events surfaced today."
        self.assertTrue(WorkflowOrchestrationAgent._lane_3_is_no_signal(text))

    def test_no_changes_detected_marker_is_no_signal(self):
        text = "No changes detected in the last 72h scan."
        self.assertTrue(WorkflowOrchestrationAgent._lane_3_is_no_signal(text))

    def test_substantive_text_is_not_no_signal(self):
        text = (
            "Three competitor changes surfaced overnight. Anthropic shipped "
            "Claude 4.7 with extended context window. OpenAI announced "
            "pricing tier changes effective next month. A Series B competitor "
            "raised $40M for enterprise-only expansion. Each represents a "
            "potential GTM shift worth examining in our pipeline reviews."
        )
        self.assertFalse(WorkflowOrchestrationAgent._lane_3_is_no_signal(text))


class LaneThreeNoSignalFallbackContentTests(TestCase):

    def test_fallback_includes_coverage_map(self):
        text = WorkflowOrchestrationAgent._lane_3_no_signal_fallback()
        self.assertIn('Coverage map', text)
        # At least Crunchbase + a press wire source named
        self.assertIn('Crunchbase', text)

    def test_fallback_includes_watch_items(self):
        text = WorkflowOrchestrationAgent._lane_3_no_signal_fallback()
        self.assertIn('Top 3 watch items', text)

    def test_fallback_includes_action(self):
        text = WorkflowOrchestrationAgent._lane_3_no_signal_fallback()
        self.assertIn('Action', text)

    def test_fallback_is_substantive(self):
        text = WorkflowOrchestrationAgent._lane_3_no_signal_fallback()
        self.assertGreater(len(text), 500)

    def test_fallback_acknowledges_uncertainty(self):
        """Per Rigby's verdict: 'No confirmed changes detected' should
        not be sold as proof of no change."""
        text = WorkflowOrchestrationAgent._lane_3_no_signal_fallback()
        self.assertIn('not necessarily proof', text)


class MuscularPlainEnglishHumanizerTests(TestCase):

    def test_capital_muscular_substituted_with_tag_preserved(self):
        text = "MUSCULAR: No Agent Activity. Some details."
        out = WorkflowOrchestrationAgent._humanize_body_system_jargon(text)
        self.assertIn('Agent activity anomaly', out)
        self.assertIn('possible worker stall', out)
        self.assertIn('[MUSCULAR]', out)
        # Original jargon form gone
        self.assertNotIn('MUSCULAR: No Agent Activity', out)

    def test_lowercase_variant_also_handled(self):
        text = "Warning -- MUSCULAR: no agent activity in 24h"
        out = WorkflowOrchestrationAgent._humanize_body_system_jargon(text)
        self.assertIn('agent activity anomaly', out)
        self.assertIn('[MUSCULAR]', out)

    def test_no_jargon_unchanged(self):
        text = "Everything nominal. Workers healthy. 200 executions logged."
        out = WorkflowOrchestrationAgent._humanize_body_system_jargon(text)
        self.assertEqual(out, text)

    def test_idempotent(self):
        text = "MUSCULAR: No Agent Activity"
        once = WorkflowOrchestrationAgent._humanize_body_system_jargon(text)
        twice = WorkflowOrchestrationAgent._humanize_body_system_jargon(once)
        self.assertEqual(once, twice)

    def test_empty_text_returns_empty(self):
        self.assertEqual(WorkflowOrchestrationAgent._humanize_body_system_jargon(''), '')


class MuscularBroadenedSweepTests(TestCase):
    """Session 1242: PR #2658's 2 literal substitutions missed 3 of 4
    MUSCULAR mentions in the 06-27 brief. The broadened humanizer
    catches the remaining shapes too.

    Each test uses the exact escape pattern from the 06-27 brief
    (Deliverable 7ba30cc0-5fa9-44fb-a316-cf728c3ce1d7), so the test
    suite acts as a regression guard against the specific shapes that
    leaked through PR #2658.
    """

    def test_tl_dr_prose_bare_muscular_demoted_to_tag(self):
        """Site 1 from 06-27 brief — TL;DR prose."""
        text = (
            'DevOps should validate Celery worker health and restart if '
            'needed — MUSCULAR warning exists but a 30-min recheck shows '
            'low confidence; follow Decision 1 if DevOps sees an '
            'execution stall.'
        )
        out = WorkflowOrchestrationAgent._humanize_body_system_jargon(text)
        # Bare 'MUSCULAR warning' replaced with humanized phrase + tag
        self.assertNotIn('— MUSCULAR warning', out)
        self.assertIn('agent-activity [MUSCULAR] warning', out)

    def test_lane_1_subsystem_warning_collapses_to_single_subsystem(self):
        """Site 2 from 06-27 brief — Lane 1 body. The phrase 'MUSCULAR
        subsystem WARNING' should NOT produce 'agent-activity [MUSCULAR]
        subsystem WARNING' (awkward double 'subsystem'). The dedicated
        'MUSCULAR subsystem' pattern collapses to a single subsystem."""
        text = (
            'Agent activity anomaly: MUSCULAR subsystem WARNING — '
            '"No recent agent activity; agents not running."'
        )
        out = WorkflowOrchestrationAgent._humanize_body_system_jargon(text)
        # No double 'subsystem subsystem'
        self.assertNotIn('subsystem subsystem', out)
        # Tag preserved
        self.assertIn('[MUSCULAR]', out)
        # Reads as plain English
        self.assertIn('agent-activity subsystem [MUSCULAR] WARNING', out)

    def test_dashboard_path_bare_muscular(self):
        """Site 3 from 06-27 brief — 'Where to verify' line referring to
        the Body Health Dashboard nav crumb."""
        text = 'Where to verify: Body Health Dashboard > MUSCULAR; /ai-studio/.'
        out = WorkflowOrchestrationAgent._humanize_body_system_jargon(text)
        self.assertNotIn('> MUSCULAR;', out)
        self.assertIn('> agent-activity [MUSCULAR];', out)

    def test_the_muscular_subsystem_pattern(self):
        """Site 4 from 06-27 brief — Decision 1 'Why now' phrasing."""
        text = (
            'The MUSCULAR subsystem reports "No Agent Activity — WARNING" '
            'and is BLOCKING content generation pipelines.'
        )
        out = WorkflowOrchestrationAgent._humanize_body_system_jargon(text)
        self.assertNotIn('The MUSCULAR subsystem', out)
        self.assertIn('The agent-activity subsystem [MUSCULAR]', out)

    def test_broadened_pass_is_idempotent(self):
        """All 4 06-27 leak shapes survive a second humanizer pass
        unchanged. Critical: the synthesis step + decision_card step
        both run the humanizer on overlapping text, so non-idempotent
        replacement would compound."""
        text = (
            'MUSCULAR warning exists. MUSCULAR subsystem WARNING. '
            'Dashboard > MUSCULAR. The MUSCULAR subsystem reports.'
        )
        once = WorkflowOrchestrationAgent._humanize_body_system_jargon(text)
        twice = WorkflowOrchestrationAgent._humanize_body_system_jargon(once)
        self.assertEqual(once, twice)
        # And the legacy literal still rewrites correctly after broaden:
        legacy = WorkflowOrchestrationAgent._humanize_body_system_jargon(
            'MUSCULAR: No Agent Activity'
        )
        self.assertIn('Agent activity anomaly', legacy)
        self.assertNotIn('agent-activity [MUSCULAR]: No', legacy)

    def test_already_tagged_muscular_left_alone(self):
        """The negative lookbehind/lookahead must skip MUSCULAR already
        wrapped in brackets so PR #2658's [MUSCULAR] tag survives
        intact when the humanizer runs over its own output (or over
        text already humanized at an upstream layer)."""
        text = 'Agent activity anomaly (possible worker stall) [MUSCULAR] — re-checked.'
        out = WorkflowOrchestrationAgent._humanize_body_system_jargon(text)
        self.assertEqual(out, text)


class MorningBriefSynthesisInputsIntegrationTests(TestCase):
    """`_execute_strategic_synthesis_step` morning_brief mode wires
    both helpers into synthesis_inputs."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f'test_l3_l1_pr4_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def _run(self, lane_1, lane_3):
        agent = WorkflowOrchestrationAgent(user=self.user)
        captured = []
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'mock'
        mock_response.choices[0].finish_reason = 'stop'

        def _capture(**kwargs):
            captured.append(kwargs['messages'][0]['content'])
            return mock_response

        mock_client.chat.completions.create.side_effect = _capture
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=mock_client,
        ):
            agent._execute_strategic_synthesis_step({
                '_synthesis_mode': 'morning_brief',
                'lane_1_text': lane_1,
                'lane_2_text': 'l2',
                'lane_3_text': lane_3,
                'lane_4_text': 'l4',
                'decision_card_text': 'dc',
            })
        return captured[0] if captured else ''

    def test_muscular_jargon_in_lane_1_humanized_in_prompt(self):
        prompt = self._run(
            lane_1='MUSCULAR: No Agent Activity detected.',
            lane_3='Substantive Lane 3 content with many words and a complete sentence ending in a period and at least 200 characters of real signal to bypass the no-signal detector.',
        )
        self.assertIn('Agent activity anomaly', prompt)
        self.assertIn('[MUSCULAR]', prompt)
        # Original jargon GONE from the prompt body
        self.assertNotIn('MUSCULAR: No Agent Activity', prompt)

    def test_lane_3_no_signal_injects_fallback_key(self):
        prompt = self._run(
            lane_1='All systems nominal.',
            lane_3='No confirmed competitor change events.',
        )
        self.assertIn('_lane_3_fallback', prompt)
        self.assertIn('Coverage map', prompt)
        self.assertIn('Top 3 watch items', prompt)

    def test_lane_3_substantive_no_fallback_injection(self):
        prompt = self._run(
            lane_1='All systems nominal.',
            lane_3='Three competitor changes surfaced overnight. Anthropic shipped Claude 4.7. OpenAI announced pricing tier changes effective next month. A Series B competitor raised $40M for enterprise expansion. Each represents a potential GTM shift worth examining in our pipeline reviews this week.',
        )
        # Fallback block content (not the Rules-section mention of the
        # marker name) should be ABSENT when Lane 3 is substantive.
        self.assertNotIn('Coverage map', prompt)
        self.assertNotIn('Top 3 watch items', prompt)
        # The substantive Lane 3 content is in the prompt as input
        self.assertIn('Three competitor changes', prompt)

    def test_prompt_includes_lane_3_fallback_consumption_rule(self):
        """Whether or not the fallback fires, the rule must always be
        in the prompt's Rules section so the LLM knows what to do
        when it's present."""
        prompt = self._run(
            lane_1='All systems nominal.',
            lane_3='Substantive Lane 3 content with many words and a complete sentence ending in a period and at least 200 characters of real signal to bypass the no-signal detector.',
        )
        self.assertIn('_lane_3_fallback', prompt)  # rule text references the key
        self.assertIn('Lane 3 is informational on no-signal days', prompt)
