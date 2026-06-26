"""Session 1238 PR-2 — Lane 1 self-referential health alarm filter.

Three test classes:

1. ``HealthAlarmTriggerDetectionTests`` — `_collect_lane_1_self_check_evidence`
   only fires when lane_1_text contains health-alarm keywords (no
   trigger → empty string return → no DB hit).

2. ``SelfCheckEvidenceContentTests`` — when triggered, the evidence
   block contains the expected metrics + confidence verdict + falsifying
   condition. Uses real DB rows to validate the activity counters.

3. ``MorningBriefPromptInjectionTests`` — when lane_1_text has the
   warning, the strategic_synthesis morning_brief mode injects the
   evidence into the LLM prompt under the
   `_lane_1_self_check` key.

Per `feedback_test_real_db_for_queryset_semantics`: real DB; real
AgentExecution + CeleryTaskEvent rows; OpenAI client mocked at the
`openai_client_factory.get_openai_client` boundary.

Run::

    python manage.py test core.tests.test_lane_1_self_check_evidence -v 2 --keepdb
"""

import uuid
from unittest.mock import patch, MagicMock

from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.services.workflow_orchestration_agent import (
    WorkflowOrchestrationAgent,
)

User = get_user_model()


class HealthAlarmTriggerDetectionTests(TestCase):
    """Self-check only fires when lane_1_text contains health-alarm
    keywords. No keyword → empty return → no DB hit."""

    def test_empty_lane_1_returns_empty(self):
        result = WorkflowOrchestrationAgent._collect_lane_1_self_check_evidence('')
        self.assertEqual(result, '')

    def test_lane_1_without_health_alarm_returns_empty(self):
        text = "Lane 1: All systems nominal. 0 critical, 0 warning."
        result = WorkflowOrchestrationAgent._collect_lane_1_self_check_evidence(text)
        self.assertEqual(result, '')

    def test_paralyzed_keyword_triggers_self_check(self):
        text = "MUSCULAR: agent execution shows 'paralyzed' state"
        result = WorkflowOrchestrationAgent._collect_lane_1_self_check_evidence(text)
        self.assertIn('SELF_CHECK_EVIDENCE', result)

    def test_no_agent_activity_keyword_triggers_self_check(self):
        text = "Warning: No Agent Activity in last 24h."
        result = WorkflowOrchestrationAgent._collect_lane_1_self_check_evidence(text)
        self.assertIn('SELF_CHECK_EVIDENCE', result)

    def test_worker_stall_keyword_triggers_self_check(self):
        text = "Detected workers stalled or worker/process stall in pipeline."
        result = WorkflowOrchestrationAgent._collect_lane_1_self_check_evidence(text)
        self.assertIn('SELF_CHECK_EVIDENCE', result)


class SelfCheckEvidenceContentTests(TestCase):
    """When triggered, the evidence block contains expected metrics +
    confidence verdict + falsifying condition."""

    def test_high_recent_activity_downgrades_to_low_confidence(self):
        """When AgentExecution count > 5 in last 30min, the verdict
        says LOW confidence (warning is stale telemetry)."""
        # Seed real activity
        Agent = apps.get_model('core', 'Agent')
        AgentExecution = apps.get_model('core', 'AgentExecution')
        agent = Agent.objects.create(name='TestAgent')
        for i in range(10):
            AgentExecution.objects.create(
                agent=agent,
                task=f'task {i}',
                status='completed',
            )
        warning_text = "MUSCULAR warning: paralyzed status detected."
        result = WorkflowOrchestrationAgent._collect_lane_1_self_check_evidence(warning_text)
        self.assertIn('LOW', result)
        self.assertIn('stale telemetry', result)
        self.assertIn('AgentExecution', result)
        # Falsifying condition is always present
        self.assertIn('What would falsify', result)

    def test_zero_activity_corroborates_warning(self):
        """When no recent activity, verdict is HIGH (warning is real)."""
        warning_text = "MUSCULAR: paralyzed"
        result = WorkflowOrchestrationAgent._collect_lane_1_self_check_evidence(warning_text)
        self.assertIn('HIGH', result)
        self.assertIn('warning is real', result)

    def test_evidence_block_includes_30min_window(self):
        warning_text = "paralyzed"
        result = WorkflowOrchestrationAgent._collect_lane_1_self_check_evidence(warning_text)
        self.assertIn('30', result)  # window minutes
        self.assertIn('SELF_CHECK_EVIDENCE', result)

    def test_evidence_block_includes_falsifying_condition(self):
        warning_text = "paralyzed"
        result = WorkflowOrchestrationAgent._collect_lane_1_self_check_evidence(warning_text)
        self.assertIn('AgentExecution count > 5', result)
        self.assertIn('CeleryTaskEvent count', result)


class MorningBriefPromptInjectionTests(TestCase):
    """When lane_1_text has the warning, `_execute_strategic_synthesis_step`
    morning_brief mode injects the self-check evidence into the prompt."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f'test_l1_inj_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def _run_morning_brief_synthesis(self, lane_1_text: str):
        agent = WorkflowOrchestrationAgent(user=self.user)

        captured = []
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'Mock brief output.'
        mock_response.choices[0].finish_reason = 'stop'

        def _capture(**kwargs):
            captured.append(kwargs['messages'][0]['content'])
            return mock_response

        mock_client.chat.completions.create.side_effect = _capture

        context = {
            '_synthesis_mode': 'morning_brief',
            'lane_1_text': lane_1_text,
            'lane_2_text': 'l2',
            'lane_3_text': 'l3',
            'lane_4_text': 'l4',
            'decision_card_text': 'dc',
        }

        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=mock_client,
        ):
            agent._execute_strategic_synthesis_step(context)

        return captured[0] if captured else ''

    def test_health_alarm_text_injects_self_check_into_prompt(self):
        prompt = self._run_morning_brief_synthesis(
            'Lane 1: MUSCULAR warning paralyzed state.'
        )
        # The evidence BLOCK (not the rule-text that mentions the
        # marker) is what we're asserting. Block-only signatures:
        self.assertIn('_lane_1_self_check', prompt)
        self.assertIn('run at brief-compile time', prompt)
        self.assertIn('What would falsify', prompt)

    def test_no_health_alarm_no_self_check_in_prompt(self):
        prompt = self._run_morning_brief_synthesis(
            'Lane 1: All systems nominal.'
        )
        # Block-only signatures must be ABSENT when no health-alarm trigger.
        # (The Rules-section mention of "SELF_CHECK_EVIDENCE" is always
        # present so we can't assert on that string itself.)
        self.assertNotIn('_lane_1_self_check', prompt)
        self.assertNotIn('run at brief-compile time', prompt)
        self.assertNotIn('What would falsify', prompt)

    def test_prompt_includes_confidence_downgrade_instruction(self):
        """The morning_brief prompt must instruct the LLM how to consume
        the SELF_CHECK_EVIDENCE block."""
        prompt = self._run_morning_brief_synthesis(
            'Lane 1: paralyzed warning'
        )
        self.assertIn('SELF_CHECK_EVIDENCE', prompt)
        self.assertIn('Evidence confidence', prompt)
        self.assertIn('auto-downgraded', prompt)
