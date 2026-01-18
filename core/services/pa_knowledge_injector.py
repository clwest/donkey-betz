"""
PA Knowledge Injector Service
Session 773: Dynamic system knowledge injection for Personal Assistant.

This service provides the PA with real-time awareness of:
1. Body system health status
2. Agent activity statistics
3. Spider freshness information
4. Sci-Fi feature states

The goal is to make the PA aware of the FULL system it represents,
not just the 44% it currently knows about.

Usage:
    from core.services.pa_knowledge_injector import get_pa_knowledge_injector

    injector = get_pa_knowledge_injector()
    context = injector.get_context_for_query(task)
    if context.get('has_dynamic_context'):
        # Inject into prompt
        spider_context['pa_knowledge'] = context
"""

import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


class PAKnowledgeInjector:
    """
    Session 773: Provides dynamic system knowledge to the PA.

    Detects query triggers and injects relevant system state.
    Caches data to minimize API overhead.
    """

    # Query patterns that trigger different context types
    HEALTH_TRIGGERS = [
        'health', 'status', 'how is the system', 'system health',
        'what needs attention', 'any issues', 'any problems',
        'vitals', 'body', 'platform health', 'diagnostics'
    ]

    AGENT_TRIGGERS = [
        'agents', 'how many agents', 'what agents', 'agent list',
        'agent count', 'available agents', 'specialized agents',
        'who can help', 'which agent'
    ]

    SPIDER_TRIGGERS = [
        'spiders', 'data sources', 'how many spiders', 'spider network',
        'real-time data', 'live data', 'where do you get data'
    ]

    CAPABILITY_TRIGGERS = [
        'what can you do', 'capabilities', 'what are your features',
        'how can you help', 'what do you offer', 'your abilities'
    ]

    SCIFI_TRIGGERS = [
        'memory palace', 'time travel', 'agent evolution', 'dreams',
        'sci-fi', 'sci fi', 'advanced features', 'time capsules',
        'mood', 'advisors', 'collective intelligence'
    ]

    BODY_SYSTEM_TRIGGERS = [
        'heart', 'lungs', 'circulatory', 'spine', 'immune',
        'digestive', 'muscular', 'brain', 'skin', 'body systems'
    ]

    # Cache settings
    CACHE_TTL_SECONDS = 60  # 1 minute cache for body health
    AGENT_ACTIVITY_CACHE_TTL = 300  # 5 minutes for agent stats

    def __init__(self):
        self._health_cache: Dict[str, Any] = {}
        self._health_cache_time: Optional[float] = None
        self._agent_activity_cache: Dict[str, Any] = {}
        self._agent_activity_cache_time: Optional[float] = None

    def _matches_trigger(self, query: str, triggers: List[str]) -> bool:
        """Check if query matches any trigger phrases."""
        query_lower = query.lower()
        return any(trigger in query_lower for trigger in triggers)

    def detect_query_type(self, query: str) -> Dict[str, bool]:
        """
        Detect what types of system knowledge the query needs.

        Returns dict with flags for each knowledge type.
        """
        return {
            'needs_health': self._matches_trigger(query, self.HEALTH_TRIGGERS),
            'needs_agents': self._matches_trigger(query, self.AGENT_TRIGGERS),
            'needs_spiders': self._matches_trigger(query, self.SPIDER_TRIGGERS),
            'needs_capabilities': self._matches_trigger(query, self.CAPABILITY_TRIGGERS),
            'needs_scifi': self._matches_trigger(query, self.SCIFI_TRIGGERS),
            'needs_body_systems': self._matches_trigger(query, self.BODY_SYSTEM_TRIGGERS),
        }

    def _get_body_health_summary(self) -> Dict[str, Any]:
        """
        Get cached body health summary.

        Returns summary of all 9 body systems with status.
        """
        # Check cache
        now = time.time()
        if (self._health_cache_time and
            (now - self._health_cache_time) < self.CACHE_TTL_SECONDS and
            self._health_cache):
            logger.debug("Using cached body health")
            return self._health_cache

        try:
            from core.services.body_vitals import get_body_vitals_service
            vitals = get_body_vitals_service()
            health = vitals.get_all_vitals()

            summary = {
                'overall_health': health.get('overall_health', 'unknown'),
                'health_score': health.get('health_score', 0),
                'systems': {},
                'alerts': [],
            }

            # Extract per-system status
            systems = health.get('systems', {})
            for system_name, system_data in systems.items():
                if isinstance(system_data, dict):
                    summary['systems'][system_name] = {
                        'status': system_data.get('status', 'unknown'),
                        'emoji': system_data.get('emoji', '❓'),
                    }

            # Get active alerts
            alerts = health.get('alerts', [])
            summary['alerts'] = [
                {'message': a.get('message', ''), 'severity': a.get('severity', 'info')}
                for a in alerts[:5]  # Limit to 5 alerts
            ]

            # Update cache
            self._health_cache = summary
            self._health_cache_time = now

            return summary

        except Exception as e:
            logger.warning(f"Failed to get body health: {e}")
            return {
                'overall_health': 'unavailable',
                'health_score': 0,
                'systems': {},
                'alerts': [],
                'error': str(e)
            }

    def _get_agent_activity_summary(self) -> Dict[str, Any]:
        """
        Get agent activity stats for the last 24 hours.

        Returns counts and top-performing agents.
        """
        # Check cache
        now = time.time()
        if (self._agent_activity_cache_time and
            (now - self._agent_activity_cache_time) < self.AGENT_ACTIVITY_CACHE_TTL and
            self._agent_activity_cache):
            logger.debug("Using cached agent activity")
            return self._agent_activity_cache

        try:
            from core.models import AgentExecution
            from django.db.models import Count, Avg
            from django.utils import timezone

            last_24h = timezone.now() - timedelta(hours=24)

            # Get execution stats
            executions = AgentExecution.objects.filter(
                created_at__gte=last_24h
            )

            total_executions = executions.count()
            successful = executions.filter(success=True).count()
            success_rate = round((successful / total_executions * 100), 1) if total_executions > 0 else 0

            # Get top agents by execution count
            top_agents = executions.values('agent_name').annotate(
                count=Count('id')
            ).order_by('-count')[:10]

            summary = {
                'total_executions_24h': total_executions,
                'success_rate': success_rate,
                'top_agents': [
                    {'name': a['agent_name'], 'executions': a['count']}
                    for a in top_agents
                ],
                'total_agents': 72,  # Static count from CLAUDE.md
            }

            # Update cache
            self._agent_activity_cache = summary
            self._agent_activity_cache_time = now

            return summary

        except Exception as e:
            logger.warning(f"Failed to get agent activity: {e}")
            return {
                'total_executions_24h': 0,
                'success_rate': 0,
                'top_agents': [],
                'total_agents': 72,
                'error': str(e)
            }

    def _get_spider_freshness(self) -> Dict[str, Any]:
        """Get spider network freshness info."""
        try:
            from core.models_unified_system import SpiderData
            from django.utils import timezone
            from django.db.models import Max

            # Get most recent spider data
            latest = SpiderData.objects.aggregate(
                latest_data=Max('created_at')
            )

            latest_time = latest.get('latest_data')
            if latest_time:
                age_minutes = (timezone.now() - latest_time).total_seconds() / 60
                freshness = 'fresh' if age_minutes < 60 else 'stale' if age_minutes < 360 else 'old'
            else:
                age_minutes = None
                freshness = 'unknown'

            # Get count by category (simplified)
            total_spiders = 77  # From CLAUDE.md

            return {
                'total_spiders': total_spiders,
                'working_spiders': 72,
                'needs_api_keys': 5,
                'data_freshness': freshness,
                'latest_data_minutes_ago': round(age_minutes, 1) if age_minutes else None,
                'categories': [
                    'Tech News', 'Financial', 'Jobs', 'Creative',
                    'Community', 'Legal', 'Entertainment', 'E-commerce'
                ]
            }

        except Exception as e:
            logger.warning(f"Failed to get spider freshness: {e}")
            return {
                'total_spiders': 77,
                'working_spiders': 72,
                'needs_api_keys': 5,
                'data_freshness': 'unknown',
                'error': str(e)
            }

    def _get_scifi_summary(self) -> Dict[str, Any]:
        """Get summary of sci-fi feature states."""
        return {
            'total_features': 14,
            'features': [
                {'name': 'Memory Palace', 'description': 'Persistent memory with embedding-based retrieval'},
                {'name': 'Agent Evolution', 'description': 'XP, levels, and skill progression'},
                {'name': 'Time Travel', 'description': 'Decision replay and alternate timeline simulation'},
                {'name': 'Dreams', 'description': 'Off-hours processing and idea generation'},
                {'name': 'Mood System', 'description': 'Agent mood states affecting creative output'},
                {'name': 'Time Capsules', 'description': 'Store context for future retrieval'},
                {'name': 'Agent Social Network', 'description': 'Agent relationships and trust scores'},
                {'name': 'Conversation Contract', 'description': 'Quality analytics for conversations'},
                {'name': 'Spider Integration', 'description': 'Real-time data from 77 sources'},
                {'name': 'Neural Orchestra', 'description': 'Agent collaboration visualization'},
                {'name': 'Collective Intelligence', 'description': 'Cross-agent learning'},
                {'name': 'Advisors', 'description': '25 legendary advisors (Buffett, Musk, etc.)'},
                {'name': 'Relationships', 'description': 'Agent-to-agent relationship tracking'},
                {'name': 'Predictions', 'description': 'Agent predictions with accuracy tracking'},
            ]
        }

    def _get_body_systems_detail(self) -> Dict[str, Any]:
        """Get detailed info about all 9 body systems."""
        return {
            'total_systems': 9,
            'systems': [
                {'name': 'HEART', 'function': 'Core component health monitoring - overall platform vitality'},
                {'name': 'LUNGS', 'function': 'Resource & budget management - token limits, API costs'},
                {'name': 'CIRCULATORY', 'function': 'Data flow health - Redis queues, Celery tasks, WebSockets'},
                {'name': 'SPINE', 'function': 'Central API routing - 19 route patterns, health-aware routing'},
                {'name': 'IMMUNE', 'function': 'Security & threat detection - 14 patterns, IP quarantine'},
                {'name': 'DIGESTIVE', 'function': 'Data ingestion - spider processing, queue throughput'},
                {'name': 'MUSCULAR', 'function': 'Agent execution - 10 muscle groups, fatigue detection'},
                {'name': 'BRAIN', 'function': 'Cognitive processing - LLM calls, reasoning chains'},
                {'name': 'SKIN', 'function': 'Workspace output - file writes, project changes, rollback'},
            ],
            'tool_hint': 'Use get_body_vitals tool to check current health status'
        }

    def get_context_for_query(self, query: str) -> Dict[str, Any]:
        """
        Main method: Get dynamic context based on query needs.

        Args:
            query: The user's query

        Returns:
            Dict with dynamic context if needed, empty if not triggered
        """
        triggers = self.detect_query_type(query)

        # If no triggers matched, return minimal context
        if not any(triggers.values()):
            return {
                'has_dynamic_context': False,
            }

        context = {
            'has_dynamic_context': True,
            'triggered_by': [k for k, v in triggers.items() if v],
        }

        # Add relevant context based on triggers
        if triggers['needs_health']:
            context['body_health'] = self._get_body_health_summary()

        if triggers['needs_agents']:
            context['agent_activity'] = self._get_agent_activity_summary()

        if triggers['needs_spiders']:
            context['spider_info'] = self._get_spider_freshness()

        if triggers['needs_capabilities'] or triggers['needs_agents']:
            # Include agent roster for capability questions
            context['agent_roster'] = {
                'total_agents': 72,
                'routable_agents': 48,
                'categories': {
                    'Creation': ['ImageAgent', 'VideoAgent', 'AudioAgent', 'ThreeDAgent'],
                    'Editing': ['ImageEditingAgent', 'VideoEditingAgent'],
                    'Research': ['ResearchAgent'],
                    'ContentWriting': ['ContentWriterAgent'],
                    'Strategy': ['ContentStrategyAgent', 'SEOOptimizerAgent', 'BrandIdentityAgent', 'SocialMediaAgent'],
                    'Executive': ['CTOAgent', 'COOAgent', 'CreativeDirectorAgent', 'MeetingCoordinatorAgent'],
                    'Analysis': ['TrendAnalysisAgent', 'OpportunityScoringAgent', 'MarketIntelligenceAgent'],
                    'Business': ['CompetitorAnalysisAgent', 'CustomerResearchAgent', 'BrandStrategyAgent', 'MarketingStrategyAgent'],
                    'Development': ['CodeGeneratorAgent', 'FullStackDeveloperAgent', 'CodeReviewAgent', 'DevOpsAgent'],
                    'Blockchain': ['BlockchainAuditCoordinator', 'SmartContractAuditorAgent', 'TransactionMonitorAgent', 'WhaleWatcherAgent', 'ExploitDetectorAgent'],
                    'Legal': ['LegalDocDrafterAgent'],
                    'Narrative': ['NarrativeDriftCoordinator', 'NarrativeHistorianAgent', 'TrendBreakDetectorAgent', 'CulturalImpactAgent'],
                    'ContentStudio': ['AutonomousContentStudioCoordinator', 'TopicMinerAgent', 'ContrarianAgent', 'PerformanceAnalystAgent'],
                    'Podcast': ['PodcastCoordinatorAgent', 'DebateAdvocateAgent', 'DebateSkepticAgent', 'ModeratorAgent'],
                    'Rendering': ['ResolveAgent'],
                    'Orchestration': ['WorkflowAgent', 'WorkflowOrchestrationAgent', 'OpportunityPipelineAgent', 'ContentExecutorAgent'],
                    'Campaign': ['CampaignOrchestratorAgent', 'AISeriesWorkflowAgent'],
                    'Stocks': ['StockAuditCoordinator', 'StockAnalystAgent', 'MarketMovementMonitorAgent', 'InstitutionalWatcherAgent', 'MarketAnomalyDetectorAgent', 'BullCaseAgent', 'BearCaseAgent', 'SignalScannerAgent', 'MarketIntelligenceCoordinator'],
                    'Markets': ['PredictionMarketAnalyst', 'SportsOddsAnalyst', 'ArbitrageDetector'],
                    'System': ['PersonalAssistantAgent', 'ThinkingAgent', 'SystemIntelligenceAgent'],
                    'Security': ['MemoryIsolationAgent', 'ContentAuditAgent'],
                    'Training': ['CharacterTrainingAgent', 'TrainedCreationAgent'],
                }
            }

        if triggers['needs_scifi']:
            context['scifi_features'] = self._get_scifi_summary()

        if triggers['needs_body_systems']:
            context['body_systems_detail'] = self._get_body_systems_detail()
            # Also get current health if asking about body systems
            context['body_health'] = self._get_body_health_summary()

        logger.info(
            f"🧠 [Session 773] PA Knowledge injected: "
            f"triggers={context['triggered_by']}"
        )

        return context

    def format_for_prompt(self, context: Dict[str, Any]) -> str:
        """
        Format the context as a prompt section.

        Args:
            context: Context from get_context_for_query

        Returns:
            Formatted string for prompt injection
        """
        if not context.get('has_dynamic_context'):
            return ""

        parts = []
        parts.append("\n\n## Dynamic System Knowledge (Real-Time)")

        # Body health section
        if 'body_health' in context:
            health = context['body_health']
            parts.append(f"\n### Platform Health: {health.get('overall_health', 'unknown').upper()}")
            parts.append(f"Health Score: {health.get('health_score', 0)}%")

            systems = health.get('systems', {})
            if systems:
                system_line = " | ".join([
                    f"{name}: {data.get('emoji', '❓')}{data.get('status', '?')}"
                    for name, data in systems.items()
                ])
                parts.append(f"Systems: {system_line}")

            alerts = health.get('alerts', [])
            if alerts:
                parts.append("Active Alerts:")
                for alert in alerts[:3]:
                    parts.append(f"  ⚠️ {alert.get('message', '')}")

        # Agent activity section
        if 'agent_activity' in context:
            activity = context['agent_activity']
            parts.append(f"\n### Agent Activity (Last 24h)")
            parts.append(f"Total Agents: {activity.get('total_agents', 72)}")
            parts.append(f"Executions: {activity.get('total_executions_24h', 0)}")
            parts.append(f"Success Rate: {activity.get('success_rate', 0)}%")

            top = activity.get('top_agents', [])[:5]
            if top:
                top_str = ", ".join([f"{a['name']}({a['executions']})" for a in top])
                parts.append(f"Top Agents: {top_str}")

        # Spider info section
        if 'spider_info' in context:
            spider = context['spider_info']
            parts.append(f"\n### Spider Network")
            parts.append(f"Total Spiders: {spider.get('total_spiders', 77)}")
            parts.append(f"Working: {spider.get('working_spiders', 72)}")
            parts.append(f"Data Freshness: {spider.get('data_freshness', 'unknown')}")
            if spider.get('latest_data_minutes_ago'):
                parts.append(f"Latest Data: {spider['latest_data_minutes_ago']} minutes ago")

        # Agent roster section
        if 'agent_roster' in context:
            roster = context['agent_roster']
            parts.append(f"\n### Agent Roster ({roster.get('total_agents', 72)} agents)")
            for category, agents in roster.get('categories', {}).items():
                parts.append(f"**{category}**: {', '.join(agents)}")

        # Sci-Fi features section
        if 'scifi_features' in context:
            scifi = context['scifi_features']
            parts.append(f"\n### Sci-Fi Features ({scifi.get('total_features', 14)} features)")
            for feature in scifi.get('features', [])[:7]:  # Show first 7
                parts.append(f"- **{feature['name']}**: {feature['description']}")

        # Body systems detail section
        if 'body_systems_detail' in context:
            detail = context['body_systems_detail']
            parts.append(f"\n### Body Systems ({detail.get('total_systems', 9)} systems)")
            for system in detail.get('systems', []):
                parts.append(f"- **{system['name']}**: {system['function']}")

        return "\n".join(parts)


# Singleton instance
_pa_knowledge_injector: Optional[PAKnowledgeInjector] = None


def get_pa_knowledge_injector() -> PAKnowledgeInjector:
    """Get the singleton PAKnowledgeInjector instance."""
    global _pa_knowledge_injector
    if _pa_knowledge_injector is None:
        _pa_knowledge_injector = PAKnowledgeInjector()
    return _pa_knowledge_injector
