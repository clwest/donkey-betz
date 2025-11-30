"""
Unit tests for BaseAgent and AgentResult.

Tests the foundation of the clean architecture agent system.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass

from core.agents.base_agent import BaseAgent, AgentResult


class TestAgentResult:
    """Tests for AgentResult dataclass."""

    def test_create_success_result(self):
        """Test creating a successful result."""
        result = AgentResult(
            success=True,
            message="Task completed",
            data={"images": ["img1.png"]},
            agent_name="ImageAgent"
        )

        assert result.success is True
        assert result.message == "Task completed"
        assert result.data == {"images": ["img1.png"]}
        assert result.agent_name == "ImageAgent"
        assert result.error is None

    def test_create_error_result(self):
        """Test creating an error result."""
        result = AgentResult(
            success=False,
            message="Task failed",
            error="API rate limit exceeded",
            agent_name="ImageAgent"
        )

        assert result.success is False
        assert result.error == "API rate limit exceeded"

    def test_default_values(self):
        """Test default values are set correctly."""
        result = AgentResult(success=True)

        assert result.message == ""
        assert result.data == {}
        assert result.error is None
        assert result.agent_name == ""
        assert result.execution_time_ms == 0
        assert result.decisions_made == 0
        assert result.tool_calls == []

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = AgentResult(
            success=True,
            message="Done",
            data={"key": "value"},
            agent_name="TestAgent",
            execution_time_ms=150,
            decisions_made=3,
            tool_calls=[{"name": "generate_image"}]
        )

        d = result.to_dict()

        assert d['success'] is True
        assert d['message'] == "Done"
        assert d['data'] == {"key": "value"}
        assert d['agent_name'] == "TestAgent"
        assert d['execution_time_ms'] == 150
        assert d['decisions_made'] == 3
        assert d['tool_calls'] == [{"name": "generate_image"}]

    def test_to_dict_serializable(self):
        """Test that to_dict output is JSON serializable."""
        import json

        result = AgentResult(
            success=True,
            data={"nested": {"key": [1, 2, 3]}}
        )

        # Should not raise
        json_str = json.dumps(result.to_dict())
        assert json_str is not None


class ConcreteTestAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    name = "TestAgent"
    system_prompt = "You are a test agent."
    tools = [
        {
            "type": "function",
            "function": {
                "name": "test_tool",
                "description": "A test tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string"}
                    }
                }
            }
        }
    ]

    def execute(self, task, context, scifi_context, spider_context):
        """Simple implementation for testing."""
        if not task:
            return AgentResult(success=False, error="No task provided")

        return AgentResult(
            success=True,
            message=f"Executed: {task}",
            agent_name=self.name
        )


class TestBaseAgent:
    """Tests for BaseAgent abstract class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that BaseAgent cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAgent()

    def test_concrete_agent_initialization(self):
        """Test concrete agent initializes correctly."""
        agent = ConcreteTestAgent()

        assert agent.name == "TestAgent"
        assert agent.system_prompt == "You are a test agent."
        assert len(agent.tools) == 1
        assert agent.user is None
        assert agent.agent_name == "TestAgent"

    def test_agent_with_user(self):
        """Test agent initialization with user."""
        mock_user = Mock()
        mock_user.username = "testuser"

        agent = ConcreteTestAgent(user=mock_user)

        assert agent.user == mock_user

    def test_execute_returns_agent_result(self):
        """Test that execute returns AgentResult."""
        agent = ConcreteTestAgent()

        result = agent.execute("Test task", {}, {}, {})

        assert isinstance(result, AgentResult)
        assert result.success is True

    def test_execute_with_empty_task(self):
        """Test execute with empty task returns error."""
        agent = ConcreteTestAgent()

        result = agent.execute("", {}, {}, {})

        assert result.success is False
        assert result.error == "No task provided"

    def test_validate_task_with_valid_task(self):
        """Test task validation with valid task."""
        agent = ConcreteTestAgent()

        assert agent._validate_task("Create an image") is True

    def test_validate_task_with_empty_task(self):
        """Test task validation with empty task."""
        agent = ConcreteTestAgent()

        assert agent._validate_task("") is False
        assert agent._validate_task("   ") is False
        assert agent._validate_task(None) is False

    def test_repr(self):
        """Test string representation."""
        agent = ConcreteTestAgent()

        assert repr(agent) == "<TestAgent>"

    def test_execute_tool_call_not_implemented(self):
        """Test that _execute_tool_call raises NotImplementedError."""
        agent = ConcreteTestAgent()

        with pytest.raises(NotImplementedError) as exc_info:
            agent._execute_tool_call("unknown_tool", {})

        assert "not implemented" in str(exc_info.value).lower()


class TestBaseAgentPromptBuilding:
    """Tests for BaseAgent prompt building."""

    def test_build_prompt_basic(self):
        """Test basic prompt building."""
        agent = ConcreteTestAgent()

        prompt = agent._build_prompt("Create a logo", {}, {})

        assert "You are a test agent" in prompt
        assert "Create a logo" in prompt
        assert "## Task" in prompt

    def test_build_prompt_with_mood(self):
        """Test prompt building with mood context."""
        agent = ConcreteTestAgent()

        scifi_context = {
            'mood': {
                'mood_type': 'inspired',
                'style_modifier': 'creative'
            }
        }

        prompt = agent._build_prompt("Create a logo", scifi_context, {})

        assert "Current Mood" in prompt
        assert "inspired" in prompt
        assert "creative" in prompt

    def test_build_prompt_with_evolution(self):
        """Test prompt building with evolution context."""
        agent = ConcreteTestAgent()

        scifi_context = {
            'evolution': {
                'level': 5,
                'title': 'Master'
            }
        }

        prompt = agent._build_prompt("Create a logo", scifi_context, {})

        assert "Experience Level" in prompt
        assert "Level 5" in prompt
        assert "Master" in prompt

    def test_build_prompt_with_memory(self):
        """Test prompt building with memory context."""
        agent = ConcreteTestAgent()

        scifi_context = {
            'memory': {
                'learned_patterns': [
                    'Users prefer minimalist logos',
                    'Blue colors work well for tech',
                    'Avoid complex gradients'
                ]
            }
        }

        prompt = agent._build_prompt("Create a logo", scifi_context, {})

        assert "Learned from past" in prompt
        assert "minimalist logos" in prompt

    def test_build_prompt_with_dreams(self):
        """Test prompt building with dreams context."""
        agent = ConcreteTestAgent()

        scifi_context = {
            'dreams': [
                {'content': 'A futuristic city with neon lights'}
            ]
        }

        prompt = agent._build_prompt("Create a logo", scifi_context, {})

        assert "creative thought" in prompt
        assert "futuristic city" in prompt

    def test_build_prompt_with_spider_trends(self):
        """Test prompt building with spider trends."""
        agent = ConcreteTestAgent()

        spider_context = {
            'relevant_trends': [
                {'topic': 'AI Art'},
                {'topic': 'Minimalism'},
                {'topic': 'Retro Design'}
            ]
        }

        prompt = agent._build_prompt("Create a logo", {}, spider_context)

        assert "Current Trends" in prompt
        assert "AI Art" in prompt
        assert "Minimalism" in prompt

    def test_build_prompt_with_creative_trends(self):
        """Test prompt building with creative trends."""
        agent = ConcreteTestAgent()

        spider_context = {
            'creative_trends': {
                'trending_styles': [
                    {'style': 'Glassmorphism'},
                    {'style': 'Neubrutalism'}
                ],
                'trending_colors': [
                    {'palette': 'Earth tones'},
                    {'palette': 'Neon'}
                ]
            }
        }

        prompt = agent._build_prompt("Create a logo", {}, spider_context)

        assert "Glassmorphism" in prompt
        assert "Earth tones" in prompt

    def test_build_prompt_empty_contexts(self):
        """Test prompt building with empty contexts."""
        agent = ConcreteTestAgent()

        prompt = agent._build_prompt("Create a logo", {}, {})

        assert "You are a test agent" in prompt
        assert "Create a logo" in prompt
        # Should not crash with empty contexts


class TestBaseAgentOpenAI:
    """Tests for BaseAgent OpenAI integration."""

    def test_client_lazy_loading(self):
        """Test that OpenAI client is lazy loaded."""
        agent = ConcreteTestAgent()

        # Should not have client yet
        assert agent._client is None

    @patch('core.agents.base_agent.OpenAI')
    def test_call_openai_success(self, mock_openai_class):
        """Test successful OpenAI API call."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_choice = MagicMock()
        mock_choice.message.content = "I will generate that image"
        mock_choice.message.tool_calls = []
        mock_choice.finish_reason = "stop"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        agent = ConcreteTestAgent()
        agent._client = mock_client

        result = agent._call_openai("Create a logo")

        assert result['content'] == "I will generate that image"
        assert result['tool_calls'] == []
        assert result['finish_reason'] == "stop"

    @patch('core.agents.base_agent.OpenAI')
    def test_call_openai_with_tool_calls(self, mock_openai_class):
        """Test OpenAI API call with tool calls."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Create mock tool call
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "generate_image"
        mock_tool_call.function.arguments = '{"prompt": "a logo"}'

        mock_choice = MagicMock()
        mock_choice.message.content = None
        mock_choice.message.tool_calls = [mock_tool_call]
        mock_choice.finish_reason = "tool_calls"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        agent = ConcreteTestAgent()
        agent._client = mock_client

        result = agent._call_openai("Create a logo")

        assert len(result['tool_calls']) == 1
        assert result['tool_calls'][0]['name'] == "generate_image"
        assert result['tool_calls'][0]['arguments'] == {"prompt": "a logo"}

    @patch('core.agents.base_agent.OpenAI')
    def test_call_openai_with_history(self, mock_openai_class):
        """Test OpenAI API call with conversation history."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_choice = MagicMock()
        mock_choice.message.content = "Done"
        mock_choice.message.tool_calls = []
        mock_choice.finish_reason = "stop"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        agent = ConcreteTestAgent()
        agent._client = mock_client

        history = [
            {"role": "user", "content": "Create a logo"},
            {"role": "assistant", "content": "What style?"}
        ]

        agent._call_openai("Minimalist style", conversation_history=history)

        # Check that history was included in messages
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs['messages']

        # Should have system + 2 history messages
        assert len(messages) == 3

    @patch('core.agents.base_agent.OpenAI')
    def test_call_openai_error_handling(self, mock_openai_class):
        """Test OpenAI API error handling."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        agent = ConcreteTestAgent()
        agent._client = mock_client

        with pytest.raises(Exception) as exc_info:
            agent._call_openai("Create a logo")

        assert "API Error" in str(exc_info.value)
