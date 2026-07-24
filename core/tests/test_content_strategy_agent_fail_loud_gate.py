"""Session 2932: Regression coverage for the ContentStrategyAgent
tool_calls-branch fail-loud gate — the strategy-arch analog of the
S2929 BaseBusinessResearchAgent Content-Shape FAIL Fold gate.

Pre-S2932: when GPT dispatched strategy tools but every tool returned
zero recommendations, the agent returned `AgentResult(success=True,
message="Generated 0 content recommendations", data={'recommendations': []})`.
Downstream callers treated the false-success shape as a real answer.

Post-S2932: same input path returns `AgentResult(success=False,
error=<explicit message>)`.

Scoped strictly to the tool_calls branch per Rigby T0 SIGN concern #1 —
the conversational branch stays success=True (see the persistence test
in test_content_strategy_agent_persistence.py). This test covers only
the tool_calls-branch behavior.
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.agents.strategy.content_strategy_agent import ContentStrategyAgent
from core.models_skin_layer import ProjectWorkspace

User = get_user_model()


class TestContentStrategyAgentFailLoudGate(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='cs-fl-test', email='cs-fl-test@example.com', password='x'
        )
        self.workspace = ProjectWorkspace.objects.create(
            name='cs-fl-test-ws', user=self.user
        )
        self.agent = ContentStrategyAgent(user=self.user)
        self.agent._workspace_id = str(self.workspace.id)

    def _run_with_gpt_response(self, gpt_response, tool_result):
        """Drive execute() with a stubbed GPT response + stubbed tool result."""
        with patch.object(
            self.agent, '_call_openai', return_value=gpt_response
        ), patch.object(
            self.agent, '_execute_tool_call', return_value=tool_result
        ):
            return self.agent.execute(
                task='What content should I create for tech audience?',
                context={'niche': 'tech'},
                scifi_context={},
                spider_context={},
            )

    def test_fail_loud_when_all_tools_return_empty_recommendations(self):
        """The gate fires when GPT dispatches tools that all return recommendations=[]."""
        gpt_response = {
            'content': None,
            'tool_calls': [
                {'name': 'analyze_trends', 'arguments': {'niche': 'tech'}},
            ],
        }
        tool_result = {'success': True, 'recommendations': []}

        result = self._run_with_gpt_response(gpt_response, tool_result)

        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        assert result.error is not None
        self.assertIn('empty recommendations', result.error)

    def test_fail_loud_when_tool_fails_silently_no_recommendations(self):
        """Same gate fires when the tool succeeded but returned no recommendations key at all."""
        gpt_response = {
            'content': None,
            'tool_calls': [
                {'name': 'recommend_content', 'arguments': {'niche': 'tech'}},
            ],
        }
        tool_result = {'success': True}

        result = self._run_with_gpt_response(gpt_response, tool_result)

        self.assertFalse(result.success)
        assert result.error is not None
        self.assertIn('empty recommendations', result.error)

    def test_success_when_tools_produce_recommendations(self):
        """Positive-path guard: real recommendations must pass through cleanly."""
        gpt_response = {
            'content': None,
            'tool_calls': [
                {'name': 'analyze_trends', 'arguments': {'niche': 'tech'}},
            ],
        }
        tool_result = {
            'success': True,
            'recommendations': [
                {'content_type': 'youtube_thumbnail', 'name': 'YouTube Thumbnail'},
                {'content_type': 'social_post', 'name': 'Social Media Post'},
            ],
        }

        result = self._run_with_gpt_response(gpt_response, tool_result)

        self.assertTrue(result.success)
        self.assertEqual(len(result.data['recommendations']), 2)
        self.assertIn('Generated 2', result.message)

    def test_conversational_branch_untouched_by_gate(self):
        """Rigby T0 SIGN concern #1: the gate is scoped to the tool_calls
        branch. A conversational response (no tool_calls) must still succeed
        even though `recommendations` will not exist in the result."""
        long_narrative = (
            "For a tech audience, focus on three content pillars: "
            "practical tutorials, tool comparisons, and trend commentary. "
            "Publish weekly with a mix of long-form YouTube explainers "
            "and short-form X threads. Ground every piece in a specific "
            "developer pain point — vague opinion pieces underperform. "
            "Rotate between beginner, intermediate, and advanced audiences "
            "to keep growth broad while retaining depth."
        )
        gpt_response = {'content': long_narrative, 'tool_calls': []}

        with patch.object(
            self.agent, '_call_openai', return_value=gpt_response
        ):
            result = self.agent.execute(
                task='What content should I create for tech audience?',
                context={'niche': 'tech'},
                scifi_context={},
                spider_context={},
            )

        self.assertTrue(
            result.success,
            'Conversational branch must not be affected by the tool_calls-branch gate',
        )
        self.assertIn('practical tutorials', result.message)
