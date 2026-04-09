"""
Agent Test Suite - Session 637
==============================

Tests all 71 routable agents for:
1. Import verification
2. Class instantiation
3. Execute method signature
4. Basic execution (optional, time-consuming)

Usage:
    # Quick test (imports and instantiation only)
    python manage.py test core.tests.test_all_agents.AgentImportTest

    # Full test (includes execution - slow, requires API keys)
    python manage.py test core.tests.test_all_agents
"""

import time
from unittest import TestCase
from django.test import TestCase as DjangoTestCase, override_settings
from django.contrib.auth import get_user_model
import inspect


class AgentImportTest(DjangoTestCase):
    """Test that all agents can be imported and instantiated."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Import router to get all agents
        from core.agent_router import AgentRouter
        cls.router = AgentRouter
        cls.agent_map = AgentRouter.AGENT_MAP

    def test_agent_count(self):
        """Verify we have expected number of agents."""
        agent_count = len(self.agent_map)
        self.assertEqual(agent_count, 71, f"Expected 71 agents, found {agent_count}")

    def test_all_agents_import(self):
        """Test that all agents can be imported."""
        from core.agent_router import AgentRouter

        for agent_name, agent_class in self.agent_map.items():
            with self.subTest(agent=agent_name):
                self.assertIsNotNone(agent_class, f"{agent_name} class is None")

    def test_all_agents_instantiate(self):
        """Test that all agents can be instantiated."""
        for agent_name, agent_class in self.agent_map.items():
            with self.subTest(agent=agent_name):
                try:
                    agent = agent_class(user=None)
                    self.assertIsNotNone(agent, f"{agent_name} instantiation returned None")
                except Exception as e:
                    self.fail(f"{agent_name} failed to instantiate: {e}")

    def test_all_agents_have_execute(self):
        """Test that all agents have an execute method."""
        for agent_name, agent_class in self.agent_map.items():
            with self.subTest(agent=agent_name):
                self.assertTrue(
                    hasattr(agent_class, 'execute'),
                    f"{agent_name} missing execute method"
                )
                self.assertTrue(
                    callable(getattr(agent_class, 'execute')),
                    f"{agent_name}.execute is not callable"
                )

    def test_execute_method_signature(self):
        """Test that all execute methods have the expected signature."""
        required_params = {'task', 'context', 'scifi_context', 'spider_context'}

        for agent_name, agent_class in self.agent_map.items():
            with self.subTest(agent=agent_name):
                sig = inspect.signature(agent_class.execute)
                params = set(sig.parameters.keys())
                # Remove 'self' from params
                params.discard('self')

                for req_param in required_params:
                    self.assertIn(
                        req_param, params,
                        f"{agent_name}.execute missing required param: {req_param}"
                    )


class AgentRouterTest(DjangoTestCase):
    """Test the AgentRouter functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from core.agent_router import AgentRouter
        cls.router_class = AgentRouter

    def test_router_instantiation(self):
        """Test router can be created."""
        router = self.router_class(user=None)
        self.assertIsNotNone(router)

    def test_get_available_agents(self):
        """Test getting available agents list."""
        router = self.router_class(user=None)
        agents = router.get_available_agents()
        self.assertEqual(len(agents), 71)

    def test_is_valid_agent(self):
        """Test agent validation."""
        router = self.router_class(user=None)
        self.assertTrue(router.is_valid_agent('ImageAgent'))
        self.assertTrue(router.is_valid_agent('ResearchAgent'))
        self.assertFalse(router.is_valid_agent('FakeAgent'))

    def test_invalid_agent_raises_error(self):
        """Test that routing to invalid agent raises error."""
        from core.agent_router import AgentNotFoundError
        router = self.router_class(user=None)

        with self.assertRaises(AgentNotFoundError):
            router.route('InvalidAgent', 'test task')


class AgentCategoryTest(DjangoTestCase):
    """Test agents by category."""

    EXPECTED_CATEGORIES = {
        'creation': ['ImageAgent', 'VideoAgent', 'AudioAgent', 'ThreeDAgent'],
        'editing': ['ImageEditingAgent', 'VideoEditingAgent'],
        'research': ['ResearchAgent'],
        'writing': ['ContentWriterAgent'],
        'strategy': ['ContentStrategyAgent', 'BrandIdentityAgent', 'SEOOptimizerAgent', 'SocialMediaAgent'],
        'executive': ['CTOAgent', 'COOAgent', 'CreativeDirectorAgent', 'MeetingCoordinatorAgent'],
        'analysis': ['TrendAnalysisAgent', 'OpportunityScoringAgent', 'MarketIntelligenceAgent'],
        'training': ['CharacterTrainingAgent', 'TrainedCreationAgent'],
        'security': ['MemoryIsolationAgent', 'ContentAuditAgent'],
        'business': ['CompetitorAnalysisAgent', 'CustomerResearchAgent', 'BrandStrategyAgent', 'MarketingStrategyAgent'],
        'legal': ['LegalDocDrafterAgent'],
        'development': ['CodeGeneratorAgent', 'FullStackDeveloperAgent', 'CodeReviewAgent', 'DevOpsAgent'],
        'stocks': [
            'StockAuditCoordinator', 'StockAnalystAgent', 'MarketMovementMonitorAgent',
            'InstitutionalWatcherAgent', 'MarketAnomalyDetectorAgent', 'BullCaseAgent',
            'BearCaseAgent', 'SignalScannerAgent', 'MarketIntelligenceCoordinator'
        ],
        'blockchain': [
            'BlockchainAuditCoordinator', 'SmartContractAuditorAgent',
            'TransactionMonitorAgent', 'WhaleWatcherAgent', 'ExploitDetectorAgent'
        ],
        'narrative': [
            'NarrativeDriftCoordinator', 'NarrativeHistorianAgent',
            'TrendBreakDetectorAgent', 'CulturalImpactAgent'
        ],
        'content_studio': [
            'AutonomousContentStudioCoordinator', 'TopicMinerAgent',
            'ContrarianAgent', 'PerformanceAnalystAgent'
        ],
        'podcast': ['PodcastCoordinatorAgent', 'DebateAdvocateAgent', 'DebateSkepticAgent', 'ModeratorAgent'],
        'rendering': ['ResolveAgent'],
        'orchestration': [
            'WorkflowAgent', 'WorkflowOrchestrationAgent', 'OpportunityPipelineAgent',
            'ContentExecutorAgent', 'CampaignOrchestratorAgent', 'AISeriesWorkflowAgent'
        ],
        'markets': ['PredictionMarketAnalyst', 'SportsOddsAnalyst', 'ArbitrageDetector'],
        'utility': ['ThinkingAgent', 'TechnicalDocumentAgent'],
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from core.agent_router import AgentRouter
        cls.agent_map = AgentRouter.AGENT_MAP

    def test_all_expected_agents_exist(self):
        """Verify all expected agents from categories exist in router."""
        all_expected = set()
        for agents in self.EXPECTED_CATEGORIES.values():
            all_expected.update(agents)

        for agent_name in all_expected:
            with self.subTest(agent=agent_name):
                self.assertIn(
                    agent_name, self.agent_map,
                    f"Expected agent {agent_name} not in AGENT_MAP"
                )

    def test_category_coverage(self):
        """Verify all agents are categorized."""
        all_categorized = set()
        for agents in self.EXPECTED_CATEGORIES.values():
            all_categorized.update(agents)

        router_agents = set(self.agent_map.keys())
        uncategorized = router_agents - all_categorized

        # Print uncategorized for debugging
        if uncategorized:
            print(f"\nUncategorized agents: {sorted(uncategorized)}")

        self.assertEqual(
            len(uncategorized), 0,
            f"Agents not in any category: {sorted(uncategorized)}"
        )


class AgentSummaryTest(DjangoTestCase):
    """Generate a summary report of all agents."""

    def test_generate_summary(self):
        """Generate and print agent summary."""
        from core.agent_router import AgentRouter

        print("\n" + "=" * 60)
        print("AGENT SUMMARY REPORT - Session 637")
        print("=" * 60)

        agents = sorted(AgentRouter.AGENT_MAP.keys())
        print(f"\nTotal Routable Agents: {len(agents)}")

        # Group by first letter
        current_letter = ""
        for agent in agents:
            if agent[0] != current_letter:
                current_letter = agent[0]
                print(f"\n{current_letter}:")
            print(f"  - {agent}")

        print("\n" + "=" * 60)
        self.assertTrue(True)  # Test always passes, just generates report


# Optional: Slow execution tests (commented out by default)
# Uncomment to run full execution tests (requires API keys)
#
# class AgentExecutionTest(DjangoTestCase):
#     """Test actual agent execution (slow, requires API keys)."""
#
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         from core.agent_router import AgentRouter
#         cls.router = AgentRouter(user=None)
#
#     def test_research_agent_execution(self):
#         """Test ResearchAgent can execute."""
#         result = self.router.route('ResearchAgent', 'What is Python?', {})
#         self.assertIsNotNone(result)
#         # Don't assert success - depends on API availability
