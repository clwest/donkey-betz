"""
Integration tests for agent workflow execution.

Tests the complete flow from router through agent execution.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from core.agent_router import AgentRouter, get_agent_router
from core.agents.base_agent import AgentResult


@pytest.mark.integration
class TestAgentWorkflowIntegration:
    """Integration tests for agent workflows."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        user = Mock()
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        return user

    @pytest.fixture
    def router(self, mock_user):
        """Create a router with mocked context services."""
        router = AgentRouter(user=mock_user)

        # Mock the context services
        router._scifi_service = Mock()
        router._scifi_service.get_scifi_context.return_value = Mock(
            to_dict=lambda: {
                'mood': {'mood_type': 'focused', 'style_modifier': 'precise'},
                'evolution': {'level': 5, 'title': 'Expert'}
            }
        )

        router._spider_service = Mock()
        router._spider_service.get_insights_for_prompt.return_value = {
            'relevant_trends': [{'topic': 'AI Art'}]
        }
        router._spider_service.get_creative_trends.return_value = {
            'trending_styles': [{'style': 'minimalist'}]
        }

        return router

    def test_image_generation_workflow(self, router):
        """Test complete image generation workflow."""
        with patch('core.agents.image_agent.ImageAgent._call_openai') as mock_call:
            mock_call.return_value = {
                'content': 'I will generate a logo for you.',
                'tool_calls': [],
                'finish_reason': 'stop'
            }

            result = router.route(
                "ImageAgent",
                "create a minimalist logo for a tech startup",
                context={'count': 1, 'style': 'minimalist'}
            )

        assert isinstance(result, AgentResult)
        assert result.agent_name == "ImageAgent"

    def test_research_to_creation_workflow(self, router):
        """Test research followed by creation workflow."""
        # First do research
        with patch('core.agents.research_agent.ResearchAgent._call_openai') as mock_call:
            mock_call.return_value = {
                'content': 'Based on my research...',
                'tool_calls': [],
                'finish_reason': 'stop'
            }

            research_result = router.route(
                "ResearchAgent",
                "research current logo design trends"
            )

        assert isinstance(research_result, AgentResult)

        # Then create based on research
        with patch('core.agents.image_agent.ImageAgent._call_openai') as mock_call:
            mock_call.return_value = {
                'content': 'Creating image with trending styles...',
                'tool_calls': [],
                'finish_reason': 'stop'
            }

            create_result = router.route(
                "ImageAgent",
                "create a logo using current trends",
                context={'research_context': research_result.data}
            )

        assert isinstance(create_result, AgentResult)

    def test_multi_agent_coordination(self, router):
        """Test coordination between multiple agents."""
        agents_called = []

        def track_agent(agent_name):
            """Track which agents were called."""
            agents_called.append(agent_name)
            return {
                'content': f'{agent_name} completed task',
                'tool_calls': [],
                'finish_reason': 'stop'
            }

        # Call multiple agents
        with patch('core.agents.image_agent.ImageAgent._call_openai') as mock_image:
            mock_image.return_value = track_agent('ImageAgent')
            router.route("ImageAgent", "create logo")

        with patch('core.agents.video_agent.VideoAgent._call_openai') as mock_video:
            mock_video.return_value = track_agent('VideoAgent')
            router.route("VideoAgent", "create animation")

        with patch('core.agents.audio_agent.AudioAgent._call_openai') as mock_audio:
            mock_audio.return_value = track_agent('AudioAgent')
            router.route("AudioAgent", "create voiceover")

        assert len(agents_called) == 3

    def test_context_flows_through_workflow(self, router):
        """Test that context properly flows through workflow."""
        captured_context = {}

        def capture_execute(self_agent, task, context, scifi_context, spider_context):
            captured_context['task'] = task
            captured_context['context'] = context
            captured_context['scifi'] = scifi_context
            captured_context['spider'] = spider_context
            return AgentResult(success=True, agent_name="ImageAgent")

        with patch.object(
            router.AGENT_MAP['ImageAgent'],
            'execute',
            capture_execute
        ):
            router.route(
                "ImageAgent",
                "create a logo",
                context={'brand': 'TechCorp', 'colors': ['blue', 'white']}
            )

        assert captured_context.get('context', {}).get('brand') == 'TechCorp'
        assert 'mood' in captured_context.get('scifi', {})
        assert 'relevant_trends' in captured_context.get('spider', {})


@pytest.mark.integration
class TestAgentErrorHandling:
    """Integration tests for error handling across agents."""

    def test_graceful_degradation_on_context_failure(self):
        """Test agents work even when context services fail."""
        router = AgentRouter()

        # Make context services fail
        router._scifi_service = Mock()
        router._scifi_service.get_scifi_context.side_effect = Exception("DB down")

        router._spider_service = Mock()
        router._spider_service.get_insights_for_prompt.side_effect = Exception("Network error")

        with patch('core.agents.image_agent.ImageAgent._call_openai') as mock_call:
            mock_call.return_value = {
                'content': 'Generated image',
                'tool_calls': [],
                'finish_reason': 'stop'
            }

            # Should still work, just without context
            result = router.route("ImageAgent", "create a logo")

        assert isinstance(result, AgentResult)

    def test_agent_execution_error_captured(self):
        """Test agent execution errors are captured."""
        router = AgentRouter()
        router._scifi_service = Mock()
        router._scifi_service.get_scifi_context.return_value = Mock(to_dict=lambda: {})
        router._spider_service = Mock()
        router._spider_service.get_insights_for_prompt.return_value = {}

        with patch('core.agents.image_agent.ImageAgent.execute') as mock_exec:
            mock_exec.side_effect = Exception("GPU memory exhausted")

            result = router.route("ImageAgent", "create 100 high-res images")

        assert result.success is False
        assert "GPU memory" in result.error


@pytest.mark.integration
class TestAgentChaining:
    """Integration tests for chaining multiple agents."""

    def test_image_to_video_chain(self):
        """Test creating image then animating to video."""
        router = AgentRouter()
        router._scifi_service = Mock()
        router._scifi_service.get_scifi_context.return_value = Mock(to_dict=lambda: {})
        router._spider_service = Mock()
        router._spider_service.get_insights_for_prompt.return_value = {}

        # Generate image
        with patch('core.agents.image_agent.ImageAgent.execute') as mock_exec:
            mock_exec.return_value = AgentResult(
                success=True,
                data={'images': [{'id': 123, 'url': '/media/test.png'}]}
            )
            image_result = router.route("ImageAgent", "create a landscape")

        assert image_result.success
        image_id = image_result.data['images'][0]['id']

        # Animate the image
        with patch('core.agents.video_agent.VideoAgent.execute') as mock_exec:
            mock_exec.return_value = AgentResult(
                success=True,
                data={'video': {'id': 456, 'url': '/media/test.mp4'}}
            )
            video_result = router.route(
                "VideoAgent",
                "animate this image with subtle motion",
                context={'source_image_id': image_id}
            )

        assert video_result.success

    def test_research_strategy_creation_chain(self):
        """Test research -> strategy -> creation chain."""
        router = AgentRouter()
        router._scifi_service = Mock()
        router._scifi_service.get_scifi_context.return_value = Mock(to_dict=lambda: {})
        router._spider_service = Mock()
        router._spider_service.get_insights_for_prompt.return_value = {}

        # Step 1: Research
        with patch('core.agents.research_agent.ResearchAgent.execute') as mock_exec:
            mock_exec.return_value = AgentResult(
                success=True,
                data={'findings': {'top_trends': ['AI', 'Sustainability']}}
            )
            research = router.route("ResearchAgent", "research tech industry trends")

        # Step 2: Strategy
        with patch('core.agents.strategy.ContentStrategyAgent.execute') as mock_exec:
            mock_exec.return_value = AgentResult(
                success=True,
                data={'strategy': {'focus': 'AI innovation', 'tone': 'professional'}}
            )
            strategy = router.route(
                "ContentStrategyAgent",
                "create content strategy",
                context={'research': research.data}
            )

        # Step 3: Create
        with patch('core.agents.image_agent.ImageAgent.execute') as mock_exec:
            mock_exec.return_value = AgentResult(
                success=True,
                data={'images': [{'id': 789}]}
            )
            creation = router.route(
                "ImageAgent",
                "create brand image following strategy",
                context={'strategy': strategy.data}
            )

        assert research.success
        assert strategy.success
        assert creation.success
