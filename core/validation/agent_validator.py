# core/validation/agent_validator.py
"""
Agent Orchestration Validation Agent

Validates the agent ecosystem including:
- Agent registry and imports
- Agent router functionality
- Agent database records
- Collective intelligence endpoints
"""

import logging

from .base import BaseValidationAgent

logger = logging.getLogger(__name__)

# Core agents that should always be available
CORE_AGENTS = [
    'ImageAgent',
    'VideoAgent',
    'AudioAgent',
    'ThreeDAgent',
    'ImageEditingAgent',
    'VideoEditingAgent',
    'ResearchAgent',
    'WorkflowAgent',
]

# Strategy agents
STRATEGY_AGENTS = [
    'ContentStrategyAgent',
    'BrandIdentityAgent',
    'SEOOptimizerAgent',
    'SocialMediaAgent',
]

# Executive agents
EXECUTIVE_AGENTS = [
    'CTOAgent',
    'COOAgent',
    'CreativeDirectorAgent',
    'MeetingCoordinatorAgent',
]


class AgentOrchestrationValidator(BaseValidationAgent):
    """Validates the agent orchestration subsystem."""

    section_name = "agents"

    def run_checks(self):
        """Run all agent-related validation checks."""
        # Import checks for core agents
        self.check_core_agent_imports()

        # Router check
        self.check_agent_router()

        # Database checks
        self.check_agent_database_records()

        # Endpoint checks
        self.check_agent_endpoints()

        # Collective intelligence
        self.check_collective_intelligence()

    def check_core_agent_imports(self):
        """Verify core agents can be imported."""
        for agent_name in CORE_AGENTS:
            self.check_import(
                module_path='core.agents',
                class_name=agent_name,
                name=f'import_{agent_name}'
            )

    def check_agent_router(self):
        """Verify agent router can be imported and has expected agents."""
        try:
            from core.agent_router import AgentRouter

            # Verify router can be instantiated
            router = AgentRouter()

            # Check that expected agents are in AGENT_MAP (class attribute)
            expected_agents = [
                'ImageAgent',
                'VideoAgent',
                'ResearchAgent',
            ]

            agent_map = router.AGENT_MAP
            missing = [a for a in expected_agents if a not in agent_map]
            passed = len(missing) == 0

            self.add_check(
                name='agent_router',
                passed=passed,
                message=f'Agent router has {len(agent_map)} agents mapped' if passed else f'Missing agents: {missing}',
                details={'agent_count': len(agent_map), 'missing': missing}
            )
        except Exception as e:
            self.add_check(
                name='agent_router',
                passed=False,
                message=f'Agent router error: {str(e)}'
            )

    def check_agent_database_records(self):
        """Verify agents are registered in database."""
        try:
            from core.models_unified_system import Agent
            self.check_model_count(
                model_class=Agent,
                min_count=20,  # Should have at least 20 agents
                name='agent_db_records'
            )
        except ImportError as e:
            self.add_check(
                name='agent_db_records',
                passed=False,
                message=f'Cannot import Agent model: {e}'
            )

    def check_agent_endpoints(self):
        """Verify agent-related API endpoints."""
        endpoints = [
            '/api/agents/',
            '/api/agent-dashboard/agents/',
            '/api/agent-dashboard/health/',
        ]

        for endpoint in endpoints:
            self.check_endpoint(
                path=endpoint,
                method='GET',
                expected_status=200,
                name=f'endpoint_{endpoint.replace("/", "_").strip("_")}'
            )

    def check_collective_intelligence(self):
        """Verify collective intelligence endpoints."""
        self.check_endpoint(
            path='/api/collective/stats/',
            method='GET',
            expected_status=200,
            name='collective_intelligence_stats'
        )

        # Check for agent conversations
        try:
            from core.models_unified_system import AgentConversation
            self.check_model_count(
                model_class=AgentConversation,
                min_count=0,  # Just verify model exists
                name='agent_conversations_model'
            )
        except ImportError as e:
            self.add_check(
                name='agent_conversations_model',
                passed=False,
                message=f'Cannot import AgentConversation: {e}'
            )

        # Check for agent dreams
        try:
            from core.models_unified_system import AgentDream
            self.check_model_count(
                model_class=AgentDream,
                min_count=0,
                name='agent_dreams_model'
            )
        except ImportError as e:
            self.add_check(
                name='agent_dreams_model',
                passed=False,
                message=f'Cannot import AgentDream: {e}'
            )
