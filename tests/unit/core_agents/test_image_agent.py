"""
Unit tests for ImageAgent.

Tests the specialized image generation agent from clean architecture.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from core.agents.image_agent import ImageAgent
from core.agents.base_agent import AgentResult


class TestImageAgentConfiguration:
    """Tests for ImageAgent configuration."""

    def test_agent_name(self):
        """Test agent has correct name."""
        agent = ImageAgent()
        assert agent.name == "ImageAgent"

    def test_agent_has_system_prompt(self):
        """Test agent has system prompt."""
        agent = ImageAgent()
        assert "image" in agent.system_prompt.lower()
        assert "generate_image" in agent.system_prompt

    def test_agent_has_tools(self):
        """Test agent has tools defined."""
        agent = ImageAgent()
        assert len(agent.tools) >= 1

    def test_agent_has_generate_image_tool(self):
        """Test agent has generate_image tool."""
        agent = ImageAgent()
        tool_names = [t['function']['name'] for t in agent.tools]
        assert 'generate_image' in tool_names

    def test_agent_does_not_have_video_tools(self):
        """Test agent does NOT have video tools (isolation)."""
        agent = ImageAgent()
        tool_names = [t['function']['name'] for t in agent.tools]
        assert 'generate_video' not in tool_names
        assert 'text_to_video' not in tool_names

    def test_agent_does_not_have_audio_tools(self):
        """Test agent does NOT have audio tools (isolation)."""
        agent = ImageAgent()
        tool_names = [t['function']['name'] for t in agent.tools]
        assert 'text_to_speech' not in tool_names
        assert 'generate_audio' not in tool_names


class TestImageAgentExecution:
    """Tests for ImageAgent execution."""

    def test_execute_returns_agent_result(self):
        """Test execute returns AgentResult."""
        agent = ImageAgent()

        with patch.object(agent, '_call_openai') as mock_call:
            mock_call.return_value = {
                'content': 'I will generate an image',
                'tool_calls': [],
                'finish_reason': 'stop'
            }

            result = agent.execute(
                task="create a logo",
                context={},
                scifi_context={},
                spider_context={}
            )

        assert isinstance(result, AgentResult)

    def test_execute_with_empty_task(self):
        """Test execute with empty task returns error."""
        agent = ImageAgent()

        result = agent.execute(
            task="",
            context={},
            scifi_context={},
            spider_context={}
        )

        assert result.success is False
        assert result.error is not None

    @patch('core.agents.image_agent.ImageAgent._call_openai')
    @patch('core.agents.image_agent.ImageAgent._execute_tool_call')
    def test_execute_with_tool_call(self, mock_execute_tool, mock_call_openai):
        """Test execution with tool call."""
        mock_call_openai.return_value = {
            'content': None,
            'tool_calls': [
                {
                    'id': 'call_123',
                    'name': 'generate_image',
                    'arguments': {
                        'prompt': 'A cyberpunk logo',
                        'style': 'cyberpunk',
                        'width': 1024,
                        'height': 1024
                    }
                }
            ],
            'finish_reason': 'tool_calls'
        }

        mock_execute_tool.return_value = {
            'success': True,
            'images': [{'url': 'http://example.com/image.png'}]
        }

        agent = ImageAgent()
        result = agent.execute(
            task="create a cyberpunk logo",
            context={},
            scifi_context={},
            spider_context={}
        )

        # Should have called the tool
        mock_execute_tool.assert_called_once()


class TestImageAgentToolExecution:
    """Tests for ImageAgent tool execution."""

    @patch('core.views_image._execute_generate_image')
    def test_execute_generate_image_tool(self, mock_generate):
        """Test generate_image tool execution."""
        mock_generate.return_value = {
            'success': True,
            'images': [
                {'url': '/media/images/test.png', 'id': 1, 'prompt': 'test'}
            ]
        }

        agent = ImageAgent()
        agent.user = Mock()
        agent.user.id = 1

        result = agent._execute_tool_call(
            'generate_image',
            {
                'prompt': 'A beautiful sunset',
                'style': 'photorealistic',
                'size': '1024x1024'
            }
        )

        assert result['success'] is True
        mock_generate.assert_called_once()

    def test_execute_unknown_tool_returns_error(self):
        """Test unknown tool returns error dict."""
        agent = ImageAgent()

        result = agent._execute_tool_call('unknown_tool', {})

        assert result['success'] is False
        assert 'error' in result
        assert 'Unknown tool' in result['error']


class TestImageAgentPromptEnhancement:
    """Tests for ImageAgent prompt enhancement."""

    def test_build_prompt_includes_image_focus(self):
        """Test prompt building includes image-specific guidance."""
        agent = ImageAgent()

        prompt = agent._build_prompt(
            "create a logo",
            {},
            {}
        )

        assert "image" in prompt.lower() or "ImageAgent" in prompt

    def test_build_prompt_with_style_context(self):
        """Test prompt building with style context."""
        agent = ImageAgent()

        spider_context = {
            'creative_trends': {
                'trending_styles': [
                    {'style': 'Glassmorphism'},
                ]
            }
        }

        prompt = agent._build_prompt(
            "create a modern logo",
            {},
            spider_context
        )

        assert "Glassmorphism" in prompt


class TestImageAgentValidation:
    """Tests for ImageAgent validation."""

    def test_validate_image_request(self):
        """Test validation of image requests."""
        agent = ImageAgent()

        # Valid image requests
        assert agent._validate_task("create a logo") is True
        assert agent._validate_task("generate an image") is True
        assert agent._validate_task("make a banner") is True

    def test_validate_empty_request(self):
        """Test validation rejects empty requests."""
        agent = ImageAgent()

        assert agent._validate_task("") is False
        assert agent._validate_task("   ") is False


class TestImageAgentIntegration:
    """Integration-style tests for ImageAgent."""

    def test_agent_inherits_from_base(self):
        """Test agent properly inherits from BaseAgent."""
        from core.agents.base_agent import BaseAgent

        agent = ImageAgent()
        assert isinstance(agent, BaseAgent)

    def test_agent_has_time_travel_mixin(self):
        """Test agent has TimeTravelMixin functionality."""
        from agents.time_travel_mixin import TimeTravelMixin

        agent = ImageAgent()
        # Agent should have record_decision method from the mixin
        assert hasattr(agent, 'record_decision')
        assert callable(getattr(agent, 'record_decision', None))

    def test_agent_result_serializable(self):
        """Test that agent results are JSON serializable."""
        import json

        agent = ImageAgent()

        result = AgentResult(
            success=True,
            message="Generated 2 images",
            data={
                "images": [
                    {"url": "/media/test1.png"},
                    {"url": "/media/test2.png"}
                ]
            },
            agent_name="ImageAgent"
        )

        # Should not raise
        json_str = json.dumps(result.to_dict())
        assert json_str is not None
