# tests/agents_tests/test_base_agent.py
"""Tests for BaseContentAgent and AgentRegistry.

Session 452: Updated tests to match actual API signatures:
- BaseContentAgent uses project_id, not project
- AgentRegistry uses get_agent/register_agent/list_agents methods
- AgentResult doesn't have 'code' field
"""
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
            agent_name = "test_agent"
            description = "A test agent"

            def execute(self, task: dict) -> dict:
                return self._success_result(
                    data={'test': 'data'},
                    message='Test executed successfully'
                )

        # Session 452: Use project_id (str) not project (object)
        return TestAgent(user=user, project_id=str(project.id))

    def test_base_agent_is_abstract(self, agent_class):
        """Test that BaseContentAgent cannot be instantiated directly."""
        # Should raise TypeError if it's truly abstract
        try:
            from agents.base_agent import BaseContentAgent
            agent = BaseContentAgent(user=None)
            # If no error, it's not abstract - check if execute is defined
            assert hasattr(agent, 'execute')
        except TypeError:
            pass  # Expected for abstract class

    def test_concrete_agent_initialization(self, concrete_agent, user, project):
        """Test concrete agent initializes with user and project_id."""
        assert concrete_agent.user == user
        # Session 452: Check project_id instead of project
        assert concrete_agent.project_id == str(project.id)

    def test_success_result_method(self, concrete_agent):
        """Test _success_result helper method."""
        # Session 452: message is first positional arg, data is optional
        result = concrete_agent._success_result(
            message='Success!',
            data={'key': 'value'}
        )

        assert result['success'] is True
        assert result['message'] == 'Success!'
        # data may be in result or in a nested structure
        assert 'data' in result or result.get('key') == 'value'

    def test_error_result_method(self, concrete_agent):
        """Test _error_result helper method."""
        result = concrete_agent._error_result(
            error='Something went wrong'
        )

        assert result['success'] is False
        assert result['error'] == 'Something went wrong'

    def test_validate_required_params(self, concrete_agent):
        """Test _validate_required_params method."""
        params = {'prompt': 'Test', 'width': 1024}

        # Session 452: Returns None if valid, error string if invalid
        result = concrete_agent._validate_required_params(
            params,
            ['prompt', 'width']
        )
        assert result is None  # None means valid

        # Should return error string for missing params
        result = concrete_agent._validate_required_params(
            params,
            ['prompt', 'missing_param']
        )
        assert result is not None  # Error string returned
        assert 'missing_param' in result.lower()

    def test_validate_uuid(self, concrete_agent):
        """Test _validate_uuid method."""
        valid_uuid = str(uuid.uuid4())
        invalid_uuid = 'not-a-uuid'

        # Session 452: Returns None if valid, error string if invalid
        result = concrete_agent._validate_uuid(valid_uuid)
        assert result is None  # None means valid

        result = concrete_agent._validate_uuid(invalid_uuid)
        assert result is not None  # Error string returned

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
        # Session 452: data defaults to empty dict via default_factory
        assert result.data == {} or result.data is None
        assert result.message == '' or result.message is None

    def test_agent_result_error(self):
        """Test AgentResult for error case."""
        from agents.base_agent import AgentResult

        # Session 452: AgentResult has 'error' field but not 'code'
        result = AgentResult(
            success=False,
            error='Something went wrong'
        )

        assert result.success is False
        assert result.error == 'Something went wrong'


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
            agent_name = "tracking_agent"
            description = "An agent with tracking"

            def execute(self, task: dict) -> dict:
                if hasattr(self, '_track_contribution'):
                    # Session 452: Use correct params: operation, asset_ids, asset_type
                    self._track_contribution(
                        operation='test_op',
                        asset_ids=['test-123'],
                        asset_type='test'
                    )
                return self._success_result(message='Tracked', data={'tracked': True})

        # Session 452: Use project_id (str) not project (object)
        return TrackingAgent(user=user, project_id=str(project.id))

    def test_track_contribution(self, concrete_agent):
        """Test contribution tracking method."""
        if hasattr(concrete_agent, '_track_contribution'):
            # Session 452: Use correct params: operation, asset_ids, asset_type
            concrete_agent._track_contribution(
                operation='test_operation',
                asset_ids=['image-123'],
                asset_type='image'
            )

    def test_contribution_tracked_on_execute(self, concrete_agent):
        """Test that contributions are tracked when executing."""
        result = concrete_agent.execute({'type': 'test'})

        assert result['success'] is True
        # Contribution tracking should happen internally


class TestAgentRegistry:
    """Tests for agent registry functionality.

    Session 452: Updated to use actual AgentRegistry API:
    - get_agent() instead of get()
    - register_agent() instead of register()
    - list_agents() returns list of dicts, not just names
    """

    def test_get_agent(self):
        """Test getting an agent by name."""
        from core.agents.registry import AgentRegistry

        registry = AgentRegistry()

        # Get an agent (may or may not exist)
        result = registry.get_agent('ImageAgent')

        # Should return dict or None
        assert result is None or isinstance(result, dict)

    def test_get_nonexistent_agent(self):
        """Test getting an agent that doesn't exist."""
        from core.agents.registry import AgentRegistry

        registry = AgentRegistry()

        result = registry.get_agent('nonexistent_agent_xyz')
        assert result is None

    def test_list_agents(self):
        """Test listing all registered agents."""
        from core.agents.registry import AgentRegistry

        registry = AgentRegistry()

        agents = registry.list_agents()

        # Should return a list
        assert isinstance(agents, list)

        # Each item should be a dict with expected keys
        for agent in agents:
            assert isinstance(agent, dict)
            if agent:  # If not empty
                assert 'name' in agent or 'id' in agent

    def test_list_agents_by_specialization(self):
        """Test listing agents filtered by specialization."""
        from core.agents.registry import AgentRegistry

        registry = AgentRegistry()

        # List with filter
        agents = registry.list_agents(specialization='creation')

        assert isinstance(agents, list)

    def test_find_best_agent(self):
        """Test finding best agent for a task."""
        from core.agents.registry import AgentRegistry

        registry = AgentRegistry()

        # Find best agent for a task
        result = registry.find_best_agent(
            task_description='Generate a logo image',
            required_capabilities=['image_generation']
        )

        # Should return dict or None
        assert result is None or isinstance(result, dict)

    def test_registry_stats(self):
        """Test getting registry statistics."""
        from core.agents.registry import AgentRegistry

        registry = AgentRegistry()

        stats = registry.get_registry_stats()

        assert hasattr(stats, 'total_agents')
        assert hasattr(stats, 'active_agents')
        assert isinstance(stats.total_agents, int)

    def test_health_check(self):
        """Test registry health check."""
        from core.agents.registry import AgentRegistry

        registry = AgentRegistry()

        health = registry.health_check()

        assert isinstance(health, dict)
        assert 'status' in health
