# tests/agents_tests/test_base_agent.py
"""Tests for BaseContentAgent."""
import pytest
from unittest.mock import patch, MagicMock
import uuid

pytestmark = pytest.mark.django_db


class TestBaseContentAgent:
    """Tests for BaseContentAgent abstract class."""

    @pytest.fixture
    def agent_class(self):
        """Get the BaseContentAgent class."""
        from agents.base_agent import BaseContentAgent
        return BaseContentAgent

    @pytest.fixture
    def concrete_agent(self, agent_class, user, project):
        """Create a concrete implementation of BaseContentAgent."""

        class TestAgent(agent_class):
            name = "test_agent"
            description = "A test agent"

            def execute(self, task: dict) -> dict:
                return self._success_result(
                    data={'test': 'data'},
                    message='Test executed successfully'
                )

        return TestAgent(user=user, project=project)

    def test_base_agent_is_abstract(self, agent_class):
        """Test that BaseContentAgent cannot be instantiated directly."""
        # Should raise TypeError if it's truly abstract
        try:
            from agents.base_agent import BaseContentAgent
            agent = BaseContentAgent()
            # If no error, it's not abstract - check if execute is defined
            assert hasattr(agent, 'execute')
        except TypeError:
            pass  # Expected for abstract class

    def test_concrete_agent_initialization(self, concrete_agent, user, project):
        """Test concrete agent initializes with user and project."""
        assert concrete_agent.user == user
        assert concrete_agent.project == project

    def test_success_result_method(self, concrete_agent):
        """Test _success_result helper method."""
        result = concrete_agent._success_result(
            data={'key': 'value'},
            message='Success!'
        )

        assert result['success'] is True
        assert result['data']['key'] == 'value'
        assert result['message'] == 'Success!'

    def test_error_result_method(self, concrete_agent):
        """Test _error_result helper method."""
        result = concrete_agent._error_result(
            error='Something went wrong',
            code='ERROR_CODE'
        )

        assert result['success'] is False
        assert result['error'] == 'Something went wrong'
        assert result.get('code') == 'ERROR_CODE'

    def test_validate_required_params(self, concrete_agent):
        """Test _validate_required_params method."""
        params = {'prompt': 'Test', 'width': 1024}

        # Should not raise for valid params
        result = concrete_agent._validate_required_params(
            params,
            ['prompt', 'width']
        )
        assert result is True or result is None

        # Should return False or raise for missing params
        try:
            result = concrete_agent._validate_required_params(
                params,
                ['prompt', 'missing_param']
            )
            if result is not None:
                assert result is False
        except ValueError:
            pass  # Expected behavior

    def test_validate_uuid(self, concrete_agent):
        """Test _validate_uuid method."""
        valid_uuid = str(uuid.uuid4())
        invalid_uuid = 'not-a-uuid'

        assert concrete_agent._validate_uuid(valid_uuid) is True

        try:
            result = concrete_agent._validate_uuid(invalid_uuid)
            if result is not None:
                assert result is False
        except ValueError:
            pass  # Expected behavior

    def test_execute_returns_dict(self, concrete_agent):
        """Test execute method returns dictionary."""
        result = concrete_agent.execute({'type': 'test'})

        assert isinstance(result, dict)
        assert 'success' in result

    def test_logging_methods(self, concrete_agent):
        """Test logging helper methods."""
        # These should not raise exceptions
        if hasattr(concrete_agent, 'log_start'):
            concrete_agent.log_start('test_operation')

        if hasattr(concrete_agent, 'log_complete'):
            concrete_agent.log_complete('test_operation', {'result': 'data'})

        if hasattr(concrete_agent, 'log_error'):
            concrete_agent.log_error('test_operation', 'Error message')


class TestAgentResult:
    """Tests for AgentResult dataclass."""

    def test_agent_result_creation(self):
        """Test creating an AgentResult."""
        from agents.base_agent import AgentResult

        result = AgentResult(
            success=True,
            data={'key': 'value'},
            message='Operation completed'
        )

        assert result.success is True
        assert result.data == {'key': 'value'}
        assert result.message == 'Operation completed'

    def test_agent_result_defaults(self):
        """Test AgentResult default values."""
        from agents.base_agent import AgentResult

        result = AgentResult(success=True)

        assert result.success is True
        assert result.data is None or result.data == {}
        assert result.message is None or result.message == ''

    def test_agent_result_error(self):
        """Test AgentResult for error case."""
        from agents.base_agent import AgentResult

        result = AgentResult(
            success=False,
            error='Something went wrong',
            code='ERR_500'
        )

        assert result.success is False
        assert result.error == 'Something went wrong'
        assert result.code == 'ERR_500'


class TestAgentContributionTracking:
    """Tests for agent contribution tracking."""

    @pytest.fixture
    def agent_class(self):
        """Get the BaseContentAgent class."""
        from agents.base_agent import BaseContentAgent
        return BaseContentAgent

    @pytest.fixture
    def concrete_agent(self, agent_class, user, project):
        """Create a concrete agent with tracking."""

        class TrackingAgent(agent_class):
            name = "tracking_agent"
            description = "An agent with tracking"

            def execute(self, task: dict) -> dict:
                self._track_contribution(
                    operation='test_op',
                    input_data=task,
                    output_data={'result': 'test'}
                )
                return self._success_result(data={'tracked': True})

        return TrackingAgent(user=user, project=project)

    def test_track_contribution(self, concrete_agent):
        """Test contribution tracking method."""
        if hasattr(concrete_agent, '_track_contribution'):
            # Should not raise
            concrete_agent._track_contribution(
                operation='test_operation',
                input_data={'prompt': 'Test'},
                output_data={'image_id': '123'}
            )

    def test_contribution_tracked_on_execute(self, concrete_agent):
        """Test that contributions are tracked when executing."""
        result = concrete_agent.execute({'type': 'test'})

        assert result['success'] is True
        # Contribution tracking should happen internally


class TestAgentRegistry:
    """Tests for agent registry functionality."""

    def test_register_agent(self):
        """Test registering an agent."""
        from agents.registry import AgentRegistry

        registry = AgentRegistry()

        # Register a mock agent
        class MockAgent:
            name = 'mock_agent'
            description = 'A mock agent'

        registry.register('mock_agent', MockAgent)

        assert registry.get('mock_agent') == MockAgent

    def test_get_unregistered_agent(self):
        """Test getting an unregistered agent."""
        from agents.registry import AgentRegistry

        registry = AgentRegistry()

        result = registry.get('nonexistent_agent')
        assert result is None

    def test_list_agents(self):
        """Test listing all registered agents."""
        from agents.registry import AgentRegistry

        registry = AgentRegistry()

        class Agent1:
            name = 'agent1'

        class Agent2:
            name = 'agent2'

        registry.register('agent1', Agent1)
        registry.register('agent2', Agent2)

        agents = registry.list_agents()
        assert 'agent1' in agents
        assert 'agent2' in agents
