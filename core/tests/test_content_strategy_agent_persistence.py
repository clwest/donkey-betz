"""Session 1092: Regression guard for ContentStrategyAgent deliverable persistence.

Bug history (canary v3): Agent ran cleanly (22s, no error, output_data had
content) but no Deliverable was persisted anywhere. _save_to_deliverable
was only called in the `if gpt_response.get('tool_calls')` branch — when
GPT responded conversationally (no tool calls), the agent fell into the
else branch which returned the AgentResult without persisting.
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.agents.strategy.content_strategy_agent import ContentStrategyAgent
from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace

User = get_user_model()


class TestContentStrategyAgentPersistence(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='cs-test', email='cs-test@example.com', password='x'
        )
        self.workspace = ProjectWorkspace.objects.create(
            name='cs-test-ws', user=self.user
        )
        self.agent = ContentStrategyAgent(user=self.user)
        self.agent._workspace_id = str(self.workspace.id)

    def _run_with_gpt_response(self, gpt_response):
        """Drive ContentStrategyAgent.execute() with a stubbed GPT response."""
        with patch.object(
            self.agent, '_call_openai', return_value=gpt_response
        ):
            return self.agent.execute(
                task='Test task: design a 5-bullet content pillar list',
                context={},
                scifi_context={},
                spider_context={},
            )

    def test_conversational_response_persists_deliverable(self):
        """The else branch (GPT replied with text, no tool_calls) must save."""
        # Realistic-length content — deliverable_factory rejects under 300 chars
        # as a stub, and any real agent response will exceed that.
        long_content = (
            "Content pillars for a sports betting newsletter:\n\n"
            "1. Sharp action analysis — daily breakdowns of where the smart "
            "money is moving, with specific examples from recent slates.\n"
            "2. Line movement playbook — how early lines shift through the "
            "week, and which games show reverse line movement worth fading.\n"
            "3. Situational angles — scheduling edges (road back-to-backs, "
            "travel fatigue, division rivalries) that markets routinely "
            "underprice in the first 24 hours.\n"
            "4. Model vs market — weekly deep-dives comparing our quant "
            "predictions against closing lines to surface consistent edges.\n"
            "5. Bankroll discipline — unit sizing, stop-loss rules, and how "
            "to survive variance across a 5,000+ bet sample."
        )
        before = Deliverable.objects.filter(agent_name='ContentStrategyAgent').count()

        result = self._run_with_gpt_response({
            'content': long_content,
            'tool_calls': [],
        })

        self.assertTrue(result.success)
        after = Deliverable.objects.filter(agent_name='ContentStrategyAgent').count()
        self.assertEqual(
            after - before, 1,
            'Conversational response must persist exactly one Deliverable',
        )
        d = Deliverable.objects.filter(agent_name='ContentStrategyAgent').latest('created_at')
        self.assertEqual(str(d.workspace_id), str(self.workspace.id))
        self.assertEqual(d.deliverable_type, 'analysis')
        self.assertIn('Sharp action', d.content)
        self.assertEqual(
            d.metadata.get('response_mode'), 'conversation',
            'metadata.response_mode marks which branch produced this row',
        )

    def test_empty_message_does_not_create_orphan_row(self):
        """If GPT returns an empty string, do not create an empty deliverable."""
        before = Deliverable.objects.filter(agent_name='ContentStrategyAgent').count()

        self._run_with_gpt_response({'content': '', 'tool_calls': []})

        after = Deliverable.objects.filter(agent_name='ContentStrategyAgent').count()
        self.assertEqual(after, before, 'Empty message must not create a row')
