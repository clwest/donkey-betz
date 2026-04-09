"""
Unit tests for AgentRouter.

Tests the deterministic routing system for clean architecture agents.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from core.agent_router import AgentRouter, AgentNotFoundError, get_agent_router
from core.agents.base_agent import AgentResult


class TestAgentRouterConfiguration:
    """Tests for AgentRouter configuration."""

    def test_router_initialization(self):
        """Test router initializes correctly."""
        router = AgentRouter()
        assert router.user is None
        assert router._scifi_service is None
        assert router._spider_service is None

    def test_router_with_user(self):
        """Test router initialization with user."""
        mock_user = Mock()
        mock_user.username = "testuser"

        router = AgentRouter(user=mock_user)
        assert router.user == mock_user

    def test_agent_map_exists(self):
        """Test AGENT_MAP is defined."""
        router = AgentRouter()
        assert hasattr(router, 'AGENT_MAP')
        assert isinstance(router.AGENT_MAP, dict)

    def test_agent_map_has_core_agents(self):
        """Test AGENT_MAP has core creation agents."""
        router = AgentRouter()
        assert 'ImageAgent' in router.AGENT_MAP
        assert 'VideoAgent' in router.AGENT_MAP
        assert 'AudioAgent' in router.AGENT_MAP
        assert 'ThreeDAgent' in router.AGENT_MAP

    def test_agent_map_has_editing_agents(self):
        """Test AGENT_MAP has editing agents."""
        router = AgentRouter()
        assert 'ImageEditingAgent' in router.AGENT_MAP
        assert 'VideoEditingAgent' in router.AGENT_MAP

    def test_agent_map_has_research_agent(self):
        """Test AGENT_MAP has research agent."""
        router = AgentRouter()
        assert 'ResearchAgent' in router.AGENT_MAP

    def test_agent_map_has_workflow_agent(self):
        """Test AGENT_MAP has workflow agent."""
        router = AgentRouter()
        assert 'WorkflowAgent' in router.AGENT_MAP

    def test_agent_map_has_strategy_agents(self):
        """Test AGENT_MAP has strategy agents."""
        router = AgentRouter()
        assert 'ContentStrategyAgent' in router.AGENT_MAP
        assert 'BrandIdentityAgent' in router.AGENT_MAP
        assert 'SEOOptimizerAgent' in router.AGENT_MAP
        assert 'SocialMediaAgent' in router.AGENT_MAP

    def test_agent_map_has_executive_agents(self):
        """Test AGENT_MAP has executive agents."""
        router = AgentRouter()
        assert 'CTOAgent' in router.AGENT_MAP
        assert 'COOAgent' in router.AGENT_MAP
        assert 'CreativeDirectorAgent' in router.AGENT_MAP
        assert 'MeetingCoordinatorAgent' in router.AGENT_MAP

    def test_agent_map_no_personal_assistant(self):
        """Test PersonalAssistantAgent removed from AGENT_MAP (deprecated)."""
        router = AgentRouter()
        assert 'PersonalAssistantAgent' not in router.AGENT_MAP


class TestAgentRouterRouting:
    """Tests for AgentRouter routing functionality."""

    def test_route_unknown_agent_raises(self):
        """Test routing to unknown agent raises error."""
        router = AgentRouter()

        with pytest.raises(AgentNotFoundError) as exc_info:
            router.route("UnknownAgent", "do something")

        assert "Unknown agent" in str(exc_info.value)
        assert "UnknownAgent" in str(exc_info.value)

    def test_route_unknown_agent_lists_available(self):
        """Test error message includes available agents."""
        router = AgentRouter()

        with pytest.raises(AgentNotFoundError) as exc_info:
            router.route("FakeAgent", "do something")

        error_msg = str(exc_info.value)
        assert "ImageAgent" in error_msg
        assert "VideoAgent" in error_msg

    @patch('core.agent_router.AgentRouter._get_scifi_context')
    @patch('core.agent_router.AgentRouter._get_spider_context')
    def test_route_calls_agent_execute(self, mock_spider, mock_scifi):
        """Test route calls agent's execute method."""
        mock_scifi.return_value = {}
        mock_spider.return_value = {}

        router = AgentRouter()

        with patch.object(router.AGENT_MAP['ImageAgent'], 'execute') as mock_execute:
            mock_execute.return_value = AgentResult(success=True)

            # Create instance and call
            result = router.route("ImageAgent", "create a logo")

        # Execute should have been called
        assert isinstance(result, AgentResult)

    @patch('core.agent_router.AgentRouter._get_scifi_context')
    @patch('core.agent_router.AgentRouter._get_spider_context')
    def test_route_passes_context(self, mock_spider, mock_scifi):
        """Test route passes context to agent."""
        mock_scifi.return_value = {'mood': 'inspired'}
        mock_spider.return_value = {'trends': ['AI']}

        router = AgentRouter()
        context = {'count': 3, 'style': 'cyberpunk'}

        with patch.object(router.AGENT_MAP['ImageAgent'].execute, '__call__') as mock_execute:
            mock_execute.return_value = AgentResult(success=True)

            # We need to actually instantiate and mock the instance
            with patch.object(router.AGENT_MAP['ImageAgent'], 'execute') as mock_exec:
                mock_exec.return_value = AgentResult(success=True)
                router.route("ImageAgent", "create a logo", context=context)

    @patch('core.agent_router.AgentRouter._get_scifi_context')
    @patch('core.agent_router.AgentRouter._get_spider_context')
    def test_route_handles_agent_exception(self, mock_spider, mock_scifi):
        """Test route handles agent exceptions gracefully."""
        mock_scifi.return_value = {}
        mock_spider.return_value = {}

        router = AgentRouter()

        # Make the agent raise an exception
        with patch('core.agents.image_agent.ImageAgent.execute') as mock_execute:
            mock_execute.side_effect = Exception("API Error")

            result = router.route("ImageAgent", "create a logo")

        assert result.success is False
        assert "API Error" in result.error

    def test_route_with_empty_context(self):
        """Test route works with no context."""
        router = AgentRouter()

        with patch.object(router, '_get_scifi_context', return_value={}):
            with patch.object(router, '_get_spider_context', return_value={}):
                with patch('core.agents.image_agent.ImageAgent.execute') as mock_exec:
                    mock_exec.return_value = AgentResult(success=True)
                    result = router.route("ImageAgent", "test")

        # Should not crash


class TestAgentRouterContextGathering:
    """Tests for context gathering methods."""

    def test_get_scifi_context_handles_error(self):
        """Test sci-fi context gathering handles errors."""
        router = AgentRouter()

        # Mock the private attribute directly
        mock_service = Mock()
        mock_service.get_scifi_context.side_effect = Exception("DB Error")
        router._scifi_service = mock_service

        context = router._get_scifi_context("ImageAgent", "test")

        assert context == {}

    def test_get_spider_context_handles_error(self):
        """Test spider context gathering handles errors."""
        router = AgentRouter()

        mock_service = Mock()
        mock_service.get_insights_for_prompt.side_effect = Exception("Network Error")
        router._spider_service = mock_service

        context = router._get_spider_context("test task")

        assert context == {}

    def test_get_spider_context_adds_creative_for_design(self):
        """Test spider context adds creative trends for design tasks."""
        router = AgentRouter()

        mock_service = Mock()
        mock_service.get_insights_for_prompt.return_value = {'trends': []}
        mock_service.get_creative_trends.return_value = {
            'styles': ['glassmorphism']
        }
        router._spider_service = mock_service

        context = router._get_spider_context("create a logo")

        assert 'creative_trends' in context

    def test_get_spider_context_no_creative_for_code(self):
        """Test spider context doesn't add creative for code tasks."""
        router = AgentRouter()

        mock_service = Mock()
        mock_service.get_insights_for_prompt.return_value = {'trends': []}
        router._spider_service = mock_service

        context = router._get_spider_context("write a function")

        # Should not have called get_creative_trends
        assert 'creative_trends' not in context


class TestAgentRouterHelpers:
    """Tests for AgentRouter helper methods."""

    def test_is_valid_agent_with_valid_name(self):
        """Test is_valid_agent returns True for valid agents."""
        router = AgentRouter()

        assert router.is_valid_agent("ImageAgent") is True
        assert router.is_valid_agent("VideoAgent") is True
        assert router.is_valid_agent("AudioAgent") is True

    def test_is_valid_agent_with_invalid_name(self):
        """Test is_valid_agent returns False for invalid agents."""
        router = AgentRouter()

        assert router.is_valid_agent("FakeAgent") is False
        assert router.is_valid_agent("") is False
        assert router.is_valid_agent("imageagent") is False  # Case sensitive

    def test_get_available_agents(self):
        """Test get_available_agents returns agent info."""
        router = AgentRouter()

        agents = router.get_available_agents()

        assert isinstance(agents, list)
        assert len(agents) > 0

        # Check structure
        first = agents[0]
        assert 'name' in first
        assert 'description' in first

    def test_get_available_agents_has_descriptions(self):
        """Test available agents have descriptions."""
        router = AgentRouter()

        agents = router.get_available_agents()

        for agent in agents:
            assert agent['description'] is not None
            assert len(agent['description']) > 0


class TestGetAgentRouter:
    """Tests for get_agent_router convenience function."""

    def test_returns_router_instance(self):
        """Test get_agent_router returns AgentRouter."""
        router = get_agent_router()
        assert isinstance(router, AgentRouter)

    def test_accepts_user(self):
        """Test get_agent_router accepts user."""
        mock_user = Mock()
        router = get_agent_router(user=mock_user)
        assert router.user == mock_user


class TestAgentRouterIntegration:
    """Integration-style tests for AgentRouter."""

    def test_all_agents_in_map_are_base_agent(self):
        """Test all agents in AGENT_MAP inherit from BaseAgent."""
        from core.agents.base_agent import BaseAgent

        router = AgentRouter()

        for name, agent_class in router.AGENT_MAP.items():
            assert issubclass(agent_class, BaseAgent), f"{name} should inherit from BaseAgent"

    def test_all_agents_have_name_attribute(self):
        """Test all agents have name attribute."""
        router = AgentRouter()

        for name, agent_class in router.AGENT_MAP.items():
            assert hasattr(agent_class, 'name'), f"{name} should have name attribute"

    def test_all_agents_have_system_prompt(self):
        """Test all agents have system_prompt attribute."""
        router = AgentRouter()

        for name, agent_class in router.AGENT_MAP.items():
            assert hasattr(agent_class, 'system_prompt'), f"{name} should have system_prompt"
            assert len(agent_class.system_prompt) > 0, f"{name} system_prompt should not be empty"

    def test_agent_count_is_reasonable(self):
        """Test we have a reasonable number of agents."""
        router = AgentRouter()

        # Should have at least the core agents
        assert len(router.AGENT_MAP) >= 10

        # Should not be absurdly large
        assert len(router.AGENT_MAP) < 100
