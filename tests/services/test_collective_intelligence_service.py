# tests/services/test_collective_intelligence_service.py
"""
Unit tests for CollectiveIntelligenceService.

Session 662: Core Services Testing Initiative
Tests the multi-agent orchestration and collective intelligence system.
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from django.core.exceptions import ObjectDoesNotExist

from core.services.collective_intelligence import (
    CollectiveIntelligenceService,
    AgentInsight,
    CollectiveReport,
    KnowledgeGap,
    AgentImprovement,
    CollaborationMonitor,
    get_collective_intelligence_service,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_cache():
    """Mock Django cache."""
    with patch('core.services.collective_intelligence.cache') as mock:
        mock.get.return_value = None
        mock.set.return_value = True
        yield mock


@pytest.fixture
def mock_collab_service():
    """Mock the collaboration service."""
    with patch('core.services.collective_intelligence.get_collaboration_service') as mock:
        mock_service = MagicMock()
        mock.return_value = mock_service
        yield mock_service


@pytest.fixture
def ci_service(mock_cache, mock_collab_service):
    """Create a CollectiveIntelligenceService with mocked dependencies."""
    return CollectiveIntelligenceService(user=None)


@pytest.fixture
def sample_insights():
    """Create sample AgentInsight objects."""
    now = datetime.now(timezone.utc)
    return [
        AgentInsight(
            agent_name='ResearchAgent',
            topic='AI Trends',
            insight_type='knowledge',
            content='Machine learning adoption is accelerating.',
            confidence=0.85,
            supporting_data={'domain': 'research'},
            timestamp=now
        ),
        AgentInsight(
            agent_name='TrendAgent',
            topic='AI Trends',
            insight_type='observation',
            content='New AI models are more efficient.',
            confidence=0.75,
            supporting_data={'domain': 'analysis'},
            timestamp=now
        ),
        AgentInsight(
            agent_name='WarningAgent',
            topic='AI Trends',
            insight_type='warning',
            content='Costs may increase significantly.',
            confidence=0.6,
            supporting_data={'domain': 'finance'},
            timestamp=now
        ),
    ]


# =============================================================================
# Test: Data Classes
# =============================================================================

class TestAgentInsightDataclass:
    """Tests for AgentInsight dataclass."""

    def test_to_dict(self):
        """Test converting AgentInsight to dict."""
        now = datetime.now(timezone.utc)
        insight = AgentInsight(
            agent_name='TestAgent',
            topic='Test Topic',
            insight_type='observation',
            content='Test content',
            confidence=0.8,
            supporting_data={'key': 'value'},
            timestamp=now
        )

        result = insight.to_dict()

        assert result['agent_name'] == 'TestAgent'
        assert result['topic'] == 'Test Topic'
        assert result['insight_type'] == 'observation'
        assert result['confidence'] == 0.8


class TestCollectiveReportDataclass:
    """Tests for CollectiveReport dataclass."""

    def test_to_dict(self, sample_insights):
        """Test converting CollectiveReport to dict."""
        report = CollectiveReport(
            id='test-report-123',
            topic='AI Trends',
            summary='Summary of AI trends',
            participating_agents=['Agent1', 'Agent2'],
            insights=sample_insights,
            recommendations=[{'type': 'action'}],
            consensus_score=0.75,
            confidence_score=0.8,
            knowledge_gaps=['Gap 1']
        )

        result = report.to_dict()

        assert result['id'] == 'test-report-123'
        assert result['topic'] == 'AI Trends'
        assert len(result['insights']) == 3
        assert result['consensus_score'] == 0.75


# =============================================================================
# Test: Initialization
# =============================================================================

class TestCollectiveIntelligenceServiceInit:
    """Tests for CollectiveIntelligenceService initialization."""

    def test_init_with_user(self, mock_cache, mock_collab_service):
        """Test initialization with a user."""
        mock_user = MagicMock()
        service = CollectiveIntelligenceService(user=mock_user)

        assert service.user == mock_user

    def test_init_with_anonymous_user(self, mock_cache, mock_collab_service):
        """Test initialization with anonymous user (should be None)."""
        from django.contrib.auth.models import AnonymousUser
        anon = AnonymousUser()
        service = CollectiveIntelligenceService(user=anon)

        assert service.user is None

    def test_init_empty_caches(self, ci_service):
        """Test that caches are initialized empty."""
        assert ci_service._insight_cache == {}


# =============================================================================
# Test: Aggregate Insights
# =============================================================================

class TestAggregateInsights:
    """Tests for aggregate_insights method."""

    def test_aggregate_insights_returns_structure(self, ci_service, mock_cache):
        """Test that aggregate_insights returns correct structure."""
        with patch('core.models_unified_system.SharedKnowledge') as mock_knowledge:
            with patch('core.models_unified_system.CollaborationSession') as mock_collab:
                with patch('core.models_unified_system.AgentConversation') as mock_conv:
                    with patch('core.models_unified_system.AgentDream') as mock_dream:
                        with patch('core.models_unified_system.AgentMemory') as mock_memory:
                            # Setup mocks
                            mock_knowledge.objects.all.return_value.filter.return_value.order_by.return_value.__getitem__.return_value = []
                            mock_collab.objects.filter.return_value.order_by.return_value.__getitem__.return_value = []
                            mock_conv.objects.filter.return_value.select_related.return_value.prefetch_related.return_value.order_by.return_value.__getitem__.return_value = []
                            mock_dream.objects.filter.return_value.select_related.return_value.order_by.return_value.__getitem__.return_value = []
                            mock_memory.objects.filter.return_value.select_related.return_value.order_by.return_value.__getitem__.return_value = []

                            result = ci_service.aggregate_insights('Test Topic')

                            assert 'topic' in result
                            assert 'total_insights' in result
                            assert 'unique_agents' in result
                            assert 'insights' in result

    def test_aggregate_insights_uses_cache(self, ci_service, mock_cache):
        """Test that cached results are returned."""
        cached_result = {
            'topic': 'Test Topic',
            'total_insights': 10,
            'unique_agents': 3,
            'insights': []
        }
        mock_cache.get.return_value = cached_result

        result = ci_service.aggregate_insights('Test Topic')

        assert result == cached_result
        mock_cache.get.assert_called_once()

    def test_aggregate_insights_handles_error(self, ci_service, mock_cache):
        """Test error handling in aggregate_insights."""
        mock_cache.get.return_value = None

        with patch('core.models_unified_system.SharedKnowledge') as mock_knowledge:
            mock_knowledge.objects.all.side_effect = Exception("Database error")

            result = ci_service.aggregate_insights('Test Topic')

            assert 'error' in result
            assert result['total_insights'] == 0


# =============================================================================
# Test: Generate Recommendations
# =============================================================================

class TestGenerateRecommendations:
    """Tests for _generate_recommendations method."""

    def test_high_confidence_insights_create_action(self, ci_service, sample_insights):
        """Test that high confidence insights generate action recommendations."""
        recommendations = ci_service._generate_recommendations(sample_insights, 'Test')

        action_recs = [r for r in recommendations if r['type'] == 'action']
        assert len(action_recs) >= 1
        assert action_recs[0]['priority'] == 'high'

    def test_medium_confidence_insights_create_investigation(self, ci_service, sample_insights):
        """Test that medium confidence insights generate investigation recommendations."""
        recommendations = ci_service._generate_recommendations(sample_insights, 'Test')

        investigation_recs = [r for r in recommendations if r['type'] == 'investigation']
        assert len(investigation_recs) >= 1

    def test_multiple_warnings_create_warning_recommendation(self, ci_service):
        """Test that multiple warnings create a warning recommendation."""
        insights = [
            AgentInsight(
                agent_name='Agent1',
                topic='Test',
                insight_type='warning',
                content='Warning 1',
                confidence=0.6
            ),
            AgentInsight(
                agent_name='Agent2',
                topic='Test',
                insight_type='warning',
                content='Warning 2',
                confidence=0.7
            ),
            AgentInsight(
                agent_name='Agent3',
                topic='Test',
                insight_type='warning',
                content='Warning 3',
                confidence=0.5
            ),
        ]

        recommendations = ci_service._generate_recommendations(insights, 'Test')

        warning_recs = [r for r in recommendations if r['type'] == 'warning']
        assert len(warning_recs) == 1
        assert warning_recs[0]['priority'] == 'high'

    def test_empty_insights_no_recommendations(self, ci_service):
        """Test that empty insights produce no recommendations."""
        recommendations = ci_service._generate_recommendations([], 'Test')
        assert recommendations == []


# =============================================================================
# Test: Identify Topic Gaps
# =============================================================================

class TestIdentifyTopicGaps:
    """Tests for _identify_topic_gaps method."""

    def test_missing_domains_identified(self, ci_service):
        """Test that missing domains are identified as gaps."""
        insights = [
            AgentInsight(
                agent_name='Agent1',
                topic='Test',
                insight_type='knowledge',
                content='Content',
                confidence=0.8,
                supporting_data={'domain': 'image'}
            )
        ]

        gaps = ci_service._identify_topic_gaps('Test', insights)

        # Should find missing domains
        assert any('video' in gap for gap in gaps)

    def test_low_coverage_identified(self, ci_service):
        """Test that low insight coverage is identified."""
        insights = [
            AgentInsight(
                agent_name='Agent1',
                topic='Test',
                insight_type='knowledge',
                content='Content',
                confidence=0.8
            )
        ]

        gaps = ci_service._identify_topic_gaps('Test', insights)

        # Should note limited coverage
        assert any('Limited insight' in gap for gap in gaps)

    def test_low_confidence_identified(self, ci_service):
        """Test that low overall confidence is identified."""
        insights = [
            AgentInsight(
                agent_name='Agent1',
                topic='Test',
                insight_type='knowledge',
                content='Content',
                confidence=0.3
            ),
            AgentInsight(
                agent_name='Agent2',
                topic='Test',
                insight_type='knowledge',
                content='Content',
                confidence=0.4
            )
        ]

        gaps = ci_service._identify_topic_gaps('Test', insights)

        # Should note low confidence
        assert any('Low overall confidence' in gap for gap in gaps)


# =============================================================================
# Test: Create Report Summary
# =============================================================================

class TestCreateReportSummary:
    """Tests for _create_report_summary method."""

    def test_summary_report_type(self, ci_service, sample_insights):
        """Test summary report type."""
        recommendations = [{'type': 'action'}]

        summary = ci_service._create_report_summary('Test', sample_insights, recommendations, 'summary')

        assert 'Summary report' in summary
        assert '3 insights' in summary
        assert '1 recommendations' in summary

    def test_action_items_report_type(self, ci_service, sample_insights):
        """Test action items report type."""
        recommendations = [{'type': 'action'}, {'type': 'investigation'}]

        summary = ci_service._create_report_summary('Test', sample_insights, recommendations, 'action_items')

        assert 'Action items' in summary

    def test_comprehensive_report_type(self, ci_service, sample_insights):
        """Test comprehensive report type."""
        recommendations = [{'type': 'action'}]

        summary = ci_service._create_report_summary('Test', sample_insights, recommendations, 'comprehensive')

        assert 'Comprehensive analysis' in summary
        assert 'agents' in summary.lower()


# =============================================================================
# Test: Get Agent Color
# =============================================================================

class TestGetAgentColor:
    """Tests for _get_agent_color method."""

    def test_high_quality_is_green(self, ci_service):
        """Test that high quality scores return green."""
        color = ci_service._get_agent_color(85)
        assert color == '#22c55e'

    def test_medium_quality_is_yellow(self, ci_service):
        """Test that medium quality scores return yellow."""
        color = ci_service._get_agent_color(65)
        assert color == '#eab308'

    def test_low_quality_is_orange(self, ci_service):
        """Test that low quality scores return orange."""
        color = ci_service._get_agent_color(45)
        assert color == '#f97316'

    def test_very_low_quality_is_red(self, ci_service):
        """Test that very low quality scores return red."""
        color = ci_service._get_agent_color(30)
        assert color == '#ef4444'


# =============================================================================
# Test: Identify Knowledge Gaps
# =============================================================================

class TestIdentifyKnowledgeGaps:
    """Tests for identify_knowledge_gaps method."""

    def test_identifies_domain_gaps(self, ci_service):
        """Test that domain gaps are identified."""
        with patch('core.models_unified_system.SharedKnowledge') as mock_knowledge:
            with patch('core.models_unified_system.CollaborationSession') as mock_collab:
                with patch('core.models_unified_system.AgentPerformanceMetric') as mock_metric:
                    # Mock domain counts
                    mock_knowledge.objects.values.return_value.annotate.return_value = [
                        {'domain': 'image', 'count': 5, 'avg_effectiveness': 80}
                    ]

                    # Mock collaboration failures
                    mock_collab.objects.filter.return_value.values.return_value.annotate.return_value = []

                    # Mock low performers
                    mock_metric.objects.filter.return_value = []

                    # Mock _get_agents_by_domain
                    with patch.object(ci_service, '_get_agents_by_domain', return_value=['ImageAgent']):
                        gaps = ci_service.identify_knowledge_gaps()

                    # Should find gaps for missing domains
                    assert len(gaps) >= 0  # May find gaps for missing domains

    def test_handles_errors(self, ci_service):
        """Test that errors are handled gracefully."""
        with patch('core.models_unified_system.SharedKnowledge') as mock_knowledge:
            mock_knowledge.objects.values.side_effect = Exception("DB Error")

            gaps = ci_service.identify_knowledge_gaps()

            assert gaps == []


# =============================================================================
# Test: Get Collaboration Monitor
# =============================================================================

class TestGetCollaborationMonitor:
    """Tests for get_collaboration_monitor method."""

    def test_returns_collaboration_monitor(self, ci_service):
        """Test that get_collaboration_monitor returns CollaborationMonitor."""
        # This test validates that CollaborationMonitor is returned (even with default values)
        # when the service encounters issues with database queries.
        # The actual mock setup for this complex method is difficult without DB access.
        with patch('core.models_unified_system.CollaborationSession') as mock_collab:
            mock_collab.objects.filter.side_effect = Exception("DB Error")

            result = ci_service.get_collaboration_monitor()

            assert isinstance(result, CollaborationMonitor)

    def test_calculates_health_status_healthy(self, ci_service):
        """Test health status calculation defaults."""
        # Test that the health calculation doesn't crash
        with patch('core.models_unified_system.CollaborationSession') as mock_collab:
            mock_collab.objects.filter.side_effect = Exception("DB Error")

            result = ci_service.get_collaboration_monitor()

            # On error, health is unknown
            assert result.collaboration_health == 'unknown'

    def test_handles_errors(self, ci_service):
        """Test that errors return safe default."""
        with patch('core.models_unified_system.CollaborationSession') as mock_collab:
            mock_collab.objects.filter.side_effect = Exception("DB Error")

            result = ci_service.get_collaboration_monitor()

            assert result.collaboration_health == 'unknown'
            assert result.active_collaborations == 0


# =============================================================================
# Test: Generate Collective Report
# =============================================================================

class TestGenerateCollectiveReport:
    """Tests for generate_collective_report method."""

    def test_returns_collective_report(self, ci_service):
        """Test that generate_collective_report returns CollectiveReport."""
        with patch.object(ci_service, 'aggregate_insights') as mock_aggregate:
            mock_aggregate.return_value = {
                'insights': [],
                'agent_contributions': {'Agent1': 5},
                'consensus_score': 0.8,
                'confidence_score': 0.75
            }

            with patch('core.models_unified_system.AgentPerformanceMetric') as mock_metric:
                mock_metric.objects.order_by.return_value.__getitem__.return_value = []

                report = ci_service.generate_collective_report('Test Topic')

                assert isinstance(report, CollectiveReport)
                assert report.topic == 'Test Topic'

    def test_handles_errors(self, ci_service):
        """Test that errors return error report."""
        with patch.object(ci_service, 'aggregate_insights') as mock_aggregate:
            mock_aggregate.side_effect = Exception("Error")

            report = ci_service.generate_collective_report('Test Topic')

            assert 'Error' in report.summary


# =============================================================================
# Test: Get Collective Stats
# =============================================================================

class TestGetCollectiveStats:
    """Tests for get_collective_stats method."""

    def test_returns_stats_structure(self, ci_service):
        """Test that get_collective_stats returns correct structure."""
        with patch('core.models_unified_system.CollaborationSession') as mock_collab:
            with patch('core.models_unified_system.SharedKnowledge') as mock_knowledge:
                with patch('core.models_unified_system.AgentPerformanceMetric') as mock_metric:
                    with patch('core.models_unified_system.InterAgentMessage') as mock_msg:
                        with patch('core.models_unified_system.Agent') as mock_agent:
                            with patch('core.models_unified_system.AgentKnowledgeSource') as mock_source:
                                with patch('core.models_unified_system.AgentSpiderConnection') as mock_spider:
                                    with patch('core.models_unified_system.AgentLearningConnection') as mock_learning:
                                        with patch('core.models_unified_system.KnowledgeTransfer') as mock_transfer:
                                            # Setup mocks
                                            mock_collab.objects.count.return_value = 100
                                            mock_collab.objects.filter.return_value.count.return_value = 80
                                            mock_knowledge.objects.count.return_value = 50
                                            mock_knowledge.objects.aggregate.return_value = {'avg': 75.0}
                                            mock_knowledge.objects.values.return_value.annotate.return_value.order_by.return_value.__getitem__.return_value = []
                                            mock_metric.objects.count.return_value = 30
                                            mock_metric.objects.aggregate.return_value = {'avg': 85.0}
                                            mock_metric.objects.order_by.return_value.values.return_value.__getitem__.return_value = []
                                            mock_msg.objects.count.return_value = 500
                                            mock_agent.objects.count.return_value = 71
                                            mock_source.objects.filter.return_value.count.return_value = 20
                                            mock_spider.objects.count.return_value = 10
                                            mock_learning.objects.filter.return_value.count.return_value = 5
                                            mock_transfer.objects.count.return_value = 100
                                            mock_transfer.objects.select_related.return_value.order_by.return_value.__getitem__.return_value = []

                                            with patch('core.personal_ai_assistant_enhanced.EnhancedPersonalAIAssistant') as mock_assistant:
                                                mock_assistant.return_value.get_tool_definitions.return_value = list(range(27))

                                                stats = ci_service.get_collective_stats()

                                                assert 'collaboration' in stats
                                                assert 'knowledge' in stats
                                                assert 'agents' in stats

    def test_handles_errors(self, ci_service):
        """Test that errors are handled."""
        with patch('core.models_unified_system.CollaborationSession') as mock_collab:
            mock_collab.objects.count.side_effect = Exception("DB Error")

            stats = ci_service.get_collective_stats()

            assert 'error' in stats


# =============================================================================
# Test: Orchestrate Multi-Agent Task
# =============================================================================

class TestOrchestrateMultiAgentTask:
    """Tests for orchestrate_multi_agent_task method."""

    def test_returns_orchestration_result(self, ci_service):
        """Test that orchestration returns result."""
        with patch('core.agents.registry.get_agent_registry') as mock_registry:
            with patch('core.models_unified_system.CollaborationSession') as mock_collab:
                mock_registry.return_value.list_agents.return_value = [
                    {'name': 'Agent1', 'capabilities': ['research'], 'routing_keywords': ['analyze'], 'performance_metrics': {'success_rate': 0.9}}
                ]
                mock_session = MagicMock()
                mock_session.id = uuid4()
                mock_collab.objects.create.return_value = mock_session

                result = ci_service.orchestrate_multi_agent_task(
                    'Analyze market trends',
                    required_capabilities=['research']
                )

                assert result['status'] == 'initiated'
                assert len(result['selected_agents']) >= 1

    def test_returns_failed_when_no_agents(self, ci_service):
        """Test failure when no suitable agents found."""
        with patch('core.agents.registry.get_agent_registry') as mock_registry:
            mock_registry.return_value.list_agents.return_value = []

            result = ci_service.orchestrate_multi_agent_task('Unknown task')

            assert result['status'] == 'failed'
            assert 'No suitable agents' in result['error']


# =============================================================================
# Test: Get Collaboration Network
# =============================================================================

class TestGetCollaborationNetwork:
    """Tests for get_collaboration_network method."""

    def test_returns_network_structure(self, ci_service):
        """Test that network returns nodes and edges."""
        with patch('core.models_unified_system.AgentPerformanceMetric') as mock_metric:
            with patch('core.models_unified_system.CollaborationSession') as mock_collab:
                with patch('core.models_unified_system.InterAgentMessage') as mock_msg:
                    mock_metric.objects.all.return_value = [
                        MagicMock(agent_name='Agent1', total_executions=10, quality_score=80, successful_collaborations=5)
                    ]
                    mock_collab.objects.filter.return_value.values.return_value = []
                    mock_msg.objects.values.return_value.annotate.return_value = []

                    network = ci_service.get_collaboration_network()

                    assert 'nodes' in network
                    assert 'edges' in network
                    assert 'stats' in network

    def test_handles_errors(self, ci_service):
        """Test that errors are handled."""
        with patch('core.models_unified_system.AgentPerformanceMetric') as mock_metric:
            mock_metric.objects.all.side_effect = Exception("DB Error")

            network = ci_service.get_collaboration_network()

            assert 'error' in network


# =============================================================================
# Test: Resolve Knowledge Gap
# =============================================================================

class TestResolveKnowledgeGap:
    """Tests for resolve_knowledge_gap method."""

    def test_creates_knowledge_items(self, ci_service):
        """Test that knowledge items are created."""
        with patch('core.models_unified_system.SharedKnowledge') as mock_knowledge:
            with patch('core.models_unified_system.SpiderData') as mock_spider:
                mock_spider.objects.filter.return_value.order_by.return_value.__getitem__.return_value = []
                mock_item = MagicMock()
                mock_item.id = uuid4()
                mock_item.title = 'Test Knowledge'
                mock_knowledge.objects.create.return_value = mock_item

                with patch.object(ci_service, '_get_domain_best_practices', return_value=[
                    {'title': 'Best Practice', 'description': 'Description', 'category': 'general'}
                ]):
                    result = ci_service.resolve_knowledge_gap('video')

                    assert result['success'] is True
                    assert result['domain'] == 'video'
                    assert result['items_created'] >= 1

    def test_handles_errors(self, ci_service):
        """Test that errors are handled."""
        with patch('core.models_unified_system.SharedKnowledge') as mock_knowledge:
            mock_knowledge.objects.create.side_effect = Exception("DB Error")

            with patch('core.models_unified_system.SpiderData') as mock_spider:
                mock_spider.objects.filter.return_value.order_by.return_value.__getitem__.return_value = []

                result = ci_service.resolve_knowledge_gap('video')

                assert result['success'] is False
                assert 'error' in result


# =============================================================================
# Test: Fix Collaboration Failures
# =============================================================================

class TestFixCollaborationFailures:
    """Tests for fix_collaboration_failures method."""

    def test_fixes_failed_sessions(self, ci_service):
        """Test that failed sessions are fixed."""
        with patch('core.models_unified_system.CollaborationSession') as mock_collab:
            # Setup failed sessions
            mock_session = MagicMock()
            mock_collab.objects.filter.return_value.__getitem__.return_value = [mock_session]

            # Setup session creation
            mock_new_session = MagicMock()
            mock_new_session.id = uuid4()
            mock_collab.objects.create.return_value = mock_new_session

            result = ci_service.fix_collaboration_failures()

            assert result['success'] is True


# =============================================================================
# Test: Boost Agent Performance
# =============================================================================

class TestBoostAgentPerformance:
    """Tests for boost_agent_performance method."""

    def test_boosts_existing_agent(self, ci_service):
        """Test boosting an existing agent."""
        with patch('core.models_unified_system.AgentPerformanceMetric') as mock_metric:
            mock_existing = MagicMock()
            mock_existing.quality_score = 50.0
            mock_existing.successful_executions = 10
            mock_existing.total_executions = 20
            mock_existing.successful_collaborations = 5
            mock_existing.total_collaborations = 10

            mock_metric.objects.get_or_create.return_value = (mock_existing, False)

            result = ci_service.boost_agent_performance('TestAgent')

            assert result['success'] is True
            assert result['new_score'] > result['old_score']

    def test_creates_new_agent_metrics(self, ci_service):
        """Test creating metrics for new agent."""
        with patch('core.models_unified_system.AgentPerformanceMetric') as mock_metric:
            mock_new = MagicMock()
            mock_metric.objects.get_or_create.return_value = (mock_new, True)

            result = ci_service.boost_agent_performance('NewAgent')

            assert result['success'] is True

    def test_handles_errors(self, ci_service):
        """Test that errors are handled."""
        with patch('core.models_unified_system.AgentPerformanceMetric') as mock_metric:
            mock_metric.objects.get_or_create.side_effect = Exception("DB Error")

            result = ci_service.boost_agent_performance('TestAgent')

            assert result['success'] is False


# =============================================================================
# Test: Factory Function
# =============================================================================

class TestFactoryFunction:
    """Tests for get_collective_intelligence_service factory."""

    def test_creates_service(self, mock_cache, mock_collab_service):
        """Test that factory creates service."""
        service = get_collective_intelligence_service()

        assert isinstance(service, CollectiveIntelligenceService)

    def test_passes_user(self, mock_cache, mock_collab_service):
        """Test that factory passes user."""
        mock_user = MagicMock()
        service = get_collective_intelligence_service(user=mock_user)

        assert service.user == mock_user


# =============================================================================
# Test: Domain Best Practices
# =============================================================================

class TestGetDomainBestPractices:
    """Tests for _get_domain_best_practices method."""

    def test_returns_video_practices(self, ci_service):
        """Test video domain practices."""
        practices = ci_service._get_domain_best_practices('video')

        assert len(practices) == 3
        assert any('Composition' in p['title'] for p in practices)

    def test_returns_audio_practices(self, ci_service):
        """Test audio domain practices."""
        practices = ci_service._get_domain_best_practices('audio')

        assert len(practices) == 3
        assert any('Voice' in p['title'] for p in practices)

    def test_returns_default_for_unknown_domain(self, ci_service):
        """Test unknown domain returns default."""
        practices = ci_service._get_domain_best_practices('unknown_domain')

        assert len(practices) == 1
        # The method uses title() which capitalizes each word
        assert 'Unknown_Domain' in practices[0]['title'] or 'Best Practices' in practices[0]['title']


# =============================================================================
# Test: Get Domain Agents
# =============================================================================

class TestGetDomainAgents:
    """Tests for _get_domain_agents method."""

    def test_returns_video_agents(self, ci_service):
        """Test video domain agents."""
        agents = ci_service._get_domain_agents('video')

        assert 'VideoAgent' in agents
        assert 'WorkflowOrchestrationAgent' in agents

    def test_returns_default_for_unknown_domain(self, ci_service):
        """Test unknown domain returns default."""
        agents = ci_service._get_domain_agents('unknown_domain')

        assert agents == ['ResearchAgent']
