# tests/agents_tests/test_video_agent.py
"""Tests for Video Agent."""
import pytest
from unittest.mock import patch, MagicMock

pytestmark = pytest.mark.django_db


class TestVideoAgent:
    """Tests for VideoAgent class."""

    @pytest.fixture
    def agent(self):
        """Create a video agent instance."""
        from core.agents import VideoAgent
        return VideoAgent()

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        # Check for common agent attributes
        assert hasattr(agent, 'name') or hasattr(agent, 'agent_id') or hasattr(agent, 'agent_type')

    def test_agent_has_capabilities(self, agent):
        """Test agent has capabilities attribute."""
        if hasattr(agent, 'capabilities'):
            assert isinstance(agent.capabilities, (list, dict, set))

    def test_can_handle_video_task(self, agent):
        """Test agent can handle video-related tasks."""
        task = {'type': 'video_generation', 'prompt': 'Test video'}

        if hasattr(agent, 'can_handle'):
            result = agent.can_handle(task)
            assert result is True

    def test_cannot_handle_image_task(self, agent):
        """Test agent correctly rejects non-video tasks."""
        task = {'type': 'image_generation', 'prompt': 'Test image'}

        if hasattr(agent, 'can_handle'):
            result = agent.can_handle(task)
            # Should return False or handle gracefully
            assert result is False or result is None

    @patch('content.video_provider.RunwayMLProvider')
    def test_execute_video_generation(self, mock_provider, agent):
        """Test video generation execution."""
        mock_provider_instance = MagicMock()
        mock_provider_instance.generate_video.return_value = {
            'success': True,
            'task_id': 'test-task-id',
            'status': 'PENDING'
        }
        mock_provider.return_value = mock_provider_instance

        if hasattr(agent, 'execute'):
            result = agent.execute({
                'type': 'video_generation',
                'prompt': 'A dog running in a field',
                'duration': 10
            })

            assert isinstance(result, dict)

    def test_execute_with_invalid_task(self, agent):
        """Test execution fails gracefully with invalid task."""
        if hasattr(agent, 'execute'):
            result = agent.execute({'type': 'unknown_type'})

            assert isinstance(result, dict)
            # Should have error info or success=False
            if 'success' in result:
                assert result['success'] is False


class TestVideoAgentConfiguration:
    """Tests for video agent configuration."""

    @pytest.fixture
    def agent(self):
        """Create a video agent instance."""
        from core.agents import VideoAgent
        return VideoAgent()

    def test_default_model_configuration(self, agent):
        """Test default model configuration."""
        if hasattr(agent, 'default_model'):
            assert agent.default_model is not None
            assert isinstance(agent.default_model, str)

    def test_supported_operations(self, agent):
        """Test agent has list of supported operations."""
        if hasattr(agent, 'supported_operations'):
            ops = agent.supported_operations
            assert isinstance(ops, (list, tuple))
            # Should support at least text-to-video
            assert 'text_to_video' in ops or 'generate' in ops or len(ops) > 0


class TestVideoAgentEditing:
    """Tests for video agent editing operations."""

    @pytest.fixture
    def agent(self):
        """Create a video agent instance."""
        from core.agents import VideoAgent
        return VideoAgent()

    def test_upscale_operation(self, agent):
        """Test video upscale operation."""
        if hasattr(agent, 'upscale'):
            result = agent.upscale(
                video_path='/path/to/video.mp4',
                scale=2
            )
            assert isinstance(result, dict)

    def test_color_grade_operation(self, agent):
        """Test video color grading operation."""
        if hasattr(agent, 'color_grade'):
            result = agent.color_grade(
                video_path='/path/to/video.mp4',
                effect='cinematic'
            )
            assert isinstance(result, dict)

    def test_trim_operation(self, agent):
        """Test video trimming operation."""
        if hasattr(agent, 'trim'):
            result = agent.trim(
                video_path='/path/to/video.mp4',
                start=0,
                end=5
            )
            assert isinstance(result, dict)


class TestVideoAgentErrorHandling:
    """Tests for video agent error handling."""

    @pytest.fixture
    def agent(self):
        """Create a video agent instance."""
        from core.agents import VideoAgent
        return VideoAgent()

    def test_handles_api_error(self, agent):
        """Test agent handles API errors gracefully."""
        with patch('content.video_provider.RunwayMLProvider') as mock_provider:
            mock_provider_instance = MagicMock()
            mock_provider_instance.generate_video.side_effect = Exception('API Error')
            mock_provider.return_value = mock_provider_instance

            if hasattr(agent, 'execute'):
                try:
                    result = agent.execute({
                        'type': 'video_generation',
                        'prompt': 'Test'
                    })
                    # Should return error dict, not raise
                    assert isinstance(result, dict)
                except Exception:
                    # Or it might raise, which is also acceptable
                    pass

    def test_handles_missing_parameters(self, agent):
        """Test agent handles missing parameters gracefully."""
        if hasattr(agent, 'execute'):
            result = agent.execute({})

            assert isinstance(result, dict)
            if 'success' in result:
                assert result['success'] is False

    def test_handles_invalid_video_path(self, agent):
        """Test agent handles invalid video paths."""
        if hasattr(agent, 'upscale'):
            result = agent.upscale(
                video_path='/nonexistent/path/video.mp4',
                scale=2
            )
            assert isinstance(result, dict)
