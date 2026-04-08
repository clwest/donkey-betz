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

    # Session 829: Session awareness - what has been developed/changed
    SESSION_TRIGGERS = [
        'session', 'what are we working on', 'current work', 'development',
        'what was changed', 'recent changes', 'what did we do', 'progress',
        'what have you been doing', 'updates', 'what happened'
    ]

    # Session 829: Remediation/Self-healing awareness
    REMEDIATION_TRIGGERS = [
        'remediation', 'self-healing', 'fix', 'audit', 'tasks',
        'code fixes', 'automated fixes', 'what needs fixing'
    ]

    # Session 972: Workspace/UI/feature awareness
    WORKSPACE_TRIGGERS = [
        'workspace', 'tab', 'tabs', 'page', 'pages', 'feature', 'features',
        'mythology lab', 'mythology', 'docs index', 'documentation index',
        'neural orchestra', 'advisors page', 'conversation contract', 'billing page',
        'analytics dashboard', 'blog viewer', 'command center', 'initiatives tab',
        'boardroom', 'content studio', 'system tab', 'operations tab',
        'data & intel', 'dataintel', 'knowledge tab', 'learning tab',
        'what is the', 'tell me about the', 'how do i use the', 'where is the',
        'where can i find', 'navigate to', 'how to access',
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
            'needs_session': self._matches_trigger(query, self.SESSION_TRIGGERS),
            'needs_remediation': self._matches_trigger(query, self.REMEDIATION_TRIGGERS),
            'needs_workspace': self._matches_trigger(query, self.WORKSPACE_TRIGGERS),
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

            # Session 957: Clarify Core Agents vs Persona Agents
            summary = {
                'total_executions_24h': total_executions,
                'success_rate': success_rate,
                'top_agents': [
                    {'name': a['agent_name'], 'executions': a['count']}
                    for a in top_agents
                ],
                # Core Agents: Specialized agents with dedicated Python code (76 total)
                'core_agents': 76,
                # Persona Agents: ConceptForge think-tank personas for brainstorming (139 total)
                'persona_agents': 139,
                # Total: 76 core + 139 personas = 215 AI entities
                'total_ai_entities': 215,
            }

            # Update cache
            self._agent_activity_cache = summary
            self._agent_activity_cache_time = now

            return summary

        except Exception as e:
            logger.warning(f"Failed to get agent activity: {e}")
            # Session 957: Clarify Core Agents vs Persona Agents
            return {
                'total_executions_24h': 0,
                'success_rate': 0,
                'top_agents': [],
                'core_agents': 76,
                'persona_agents': 139,
                'total_ai_entities': 215,
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

    def _get_session_summary(self) -> Dict[str, Any]:
        """
        Session 829: Get current session context from 00-START-NEXT-SESSION.md.

        This makes the PA aware of what development work has been done.
        """
        import os
        try:
            session_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                '00-START-NEXT-SESSION.md'
            )

            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    content = f.read()

                # Extract key information
                lines = content.split('\n')
                session_num = None
                status_line = None
                breakthroughs = []

                for i, line in enumerate(lines):
                    if line.startswith('# Session'):
                        session_num = line.replace('# Session ', '').split(' ')[0]
                    if line.startswith('**Status:**'):
                        status_line = line.replace('**Status:**', '').strip()
                    if line.startswith('### ') and 'breakthrough' not in line.lower():
                        # Capture section headers as progress points
                        breakthroughs.append(line.replace('### ', '').strip())

                return {
                    'current_session': session_num,
                    'status': status_line,
                    'recent_work': breakthroughs[:5],  # Limit to 5
                    'has_session_context': True,
                    'file_updated': datetime.fromtimestamp(
                        os.path.getmtime(session_file)
                    ).strftime('%Y-%m-%d %H:%M')
                }
            else:
                return {
                    'has_session_context': False,
                    'message': 'Session file not found'
                }

        except Exception as e:
            logger.warning(f"Failed to get session summary: {e}")
            return {
                'has_session_context': False,
                'error': str(e)
            }

    def _get_remediation_summary(self) -> Dict[str, Any]:
        """
        Session 829: Get self-healing remediation status.

        Shows progress on automated code fixes.
        """
        try:
            from core.models_audit_tracking import AuditRemediationTask
            from django.db.models import Count

            # Get status counts
            status_counts = dict(
                AuditRemediationTask.objects.values('status').annotate(
                    c=Count('id')
                ).values_list('status', 'c')
            )

            total = sum(status_counts.values())
            completed = status_counts.get('completed', 0)
            in_progress = status_counts.get('in_progress', 0)
            pending = status_counts.get('assigned', 0) + status_counts.get('pending', 0)

            # Get agents with most tasks
            by_agent = list(
                AuditRemediationTask.objects.filter(
                    status__in=['assigned', 'in_progress']
                ).values('assigned_agent').annotate(
                    c=Count('id')
                ).order_by('-c')[:5]
            )

            percentage = round(completed / total * 100, 1) if total > 0 else 0

            return {
                'total_tasks': total,
                'completed': completed,
                'in_progress': in_progress,
                'pending': pending,
                'percentage': percentage,
                'top_agents': [
                    {'agent': item['assigned_agent'], 'tasks': item['c']}
                    for item in by_agent
                ],
                'has_remediation_data': True
            }

        except Exception as e:
            logger.warning(f"Failed to get remediation summary: {e}")
            return {
                'has_remediation_data': False,
                'error': str(e)
            }

    def _get_workspace_knowledge(self) -> Dict[str, Any]:
        """
        Session 972: Get workspace tabs and standalone pages knowledge.

        Returns hardcoded dict describing all 9 workspace tabs and 8 standalone pages
        so the PA can accurately describe any platform feature.
        """
        return {
            'workspace_tabs': [
                {
                    'name': 'Command Center',
                    'route': '/',
                    'description': 'AI chat interface with NowHub (Attention Queue, Active Work, System Pulse), natural language command routing',
                },
                {
                    'name': 'Initiatives',
                    'route': '/workspace?tab=initiatives',
                    'description': 'Strategic project management with 5-stage pipeline (Research, Analysis, Strategy, Execution, Review), action items, signal intelligence, priority scoring',
                },
                {
                    'name': 'Boardroom',
                    'route': '/workspace?tab=boardroom',
                    'description': 'Decision tracking, self-healing remediation, governance, human attention queue',
                },
                {
                    'name': 'Content Studio',
                    'route': '/workspace?tab=content',
                    'description': 'Content creation and management hub',
                    'sub_tabs': 'Gallery, Channels, Blogs, Documents, Podcast, Distribution, Dossiers, Voices, Files, Campaigns, Deliverables',
                },
                {
                    'name': 'System',
                    'route': '/workspace?tab=system',
                    'description': 'Infrastructure monitoring and agent orchestration',
                    'sub_tabs': 'Health, Services, LLM, Integration, Monitor, Workflows, HiveMind, Triggers',
                },
                {
                    'name': 'Operations',
                    'route': '/workspace?tab=operations',
                    'description': 'Agent execution history, report provenance, workspace file operations',
                },
                {
                    'name': 'Data & Intel',
                    'route': '/workspace?tab=dataintel',
                    'description': 'Data sources and intelligence analysis',
                    'sub_tabs': 'Spiders, Feed, Learning, Reasoning, Safety, Collective',
                },
                {
                    'name': 'Knowledge',
                    'route': '/workspace?tab=knowledge',
                    'description': 'Documents, playbooks, audit dashboard, RAG observability',
                },
                {
                    'name': 'Learning',
                    'route': '/workspace?tab=learning',
                    'description': 'Learning journeys, achievements, AI learning effectiveness tracking',
                },
            ],
            'standalone_pages': [
                {
                    'name': 'Mythology Lab',
                    'route': '/mythology-lab',
                    'description': 'Hallucination detection and prevention — reviews flagged AI outputs, manages quarantine, tracks mutation patterns',
                },
                {
                    'name': 'Advisors',
                    'route': '/advisors',
                    'description': '25 legendary advisor consultations across finance, tech, leadership (Buffett, Musk, etc.)',
                },
                {
                    'name': 'Neural Orchestra',
                    'route': '/neural-orchestra',
                    'description': 'AI consciousness visualization — agent collaborations, learning insights, ecosystem feed',
                },
                {
                    'name': 'Conversation Contract',
                    'route': '/conversation-contract',
                    'description': 'Quality analytics for agent conversations, compliance metrics',
                },
                {
                    'name': 'Docs Index',
                    'route': '/docs-index',
                    'description': 'Documentation browser — 1700+ docs, status badges, cross-references, search',
                },
                {
                    'name': 'Billing',
                    'route': '/billing',
                    'description': 'Stripe subscription management, payment methods, billing history',
                },
                {
                    'name': 'Analytics',
                    'route': '/analytics',
                    'description': 'System-wide performance charts, top performers, anomaly detection',
                },
                {
                    'name': 'Blog Viewer',
                    'route': '/blog/{id}',
                    'description': 'Blog display with quality metrics, approve/publish actions, related posts',
                },
            ],
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
            # Session 957: Clarify Core Agents vs Persona Agents
            context['agent_roster'] = {
                'core_agents': 76,  # Specialized agents with Python code
                'persona_agents': 139,  # ConceptForge think-tank personas
                'total_ai_entities': 215,  # 76 + 139
                'routable_agents': 49,  # Agents accessible via AgentRouter
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
                    'System': ['ThinkingAgent', 'SystemIntelligenceAgent'],
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

        # Session 829: Session and remediation awareness
        if triggers['needs_session']:
            context['session_info'] = self._get_session_summary()

        if triggers['needs_remediation']:
            context['remediation_info'] = self._get_remediation_summary()

        # Session 972: Workspace/UI knowledge
        if triggers['needs_workspace']:
            context['workspace_info'] = self._get_workspace_knowledge()

        logger.info(
            f"🧠 [Session 773/829] PA Knowledge injected: "
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
        # Session 957: Clarify Core Agents vs Persona Agents
        if 'agent_activity' in context:
            activity = context['agent_activity']
            parts.append(f"\n### AI Entities (Last 24h)")
            parts.append(f"Core Agents: {activity.get('core_agents', 76)} (specialized Python agents)")
            parts.append(f"Persona Agents: {activity.get('persona_agents', 139)} (ConceptForge think-tank)")
            parts.append(f"Total AI Entities: {activity.get('total_ai_entities', 215)}")
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
        # Session 957: Clarify Core Agents vs Persona Agents
        if 'agent_roster' in context:
            roster = context['agent_roster']
            core = roster.get('core_agents', 76)
            personas = roster.get('persona_agents', 139)
            total = roster.get('total_ai_entities', 215)
            parts.append(f"\n### Agent Roster ({core} Core + {personas} Personas = {total} AI Entities)")
            parts.append(f"Core Agents: {core} (specialized agents with Python code)")
            parts.append(f"Persona Agents: {personas} (ConceptForge think-tank personas for brainstorming)")
            parts.append(f"Routable: {roster.get('routable_agents', 49)} (accessible via AgentRouter)")
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

        # Session 829: Session info section
        if 'session_info' in context:
            session = context['session_info']
            if session.get('has_session_context'):
                parts.append(f"\n### Current Development Session")
                parts.append(f"Session: {session.get('current_session', 'Unknown')}")
                if session.get('status'):
                    parts.append(f"Status: {session['status']}")
                if session.get('recent_work'):
                    parts.append("Recent Work:")
                    for item in session['recent_work'][:3]:
                        parts.append(f"  - {item}")
                parts.append(f"Last Updated: {session.get('file_updated', 'Unknown')}")

        # Session 829: Remediation info section
        if 'remediation_info' in context:
            rem = context['remediation_info']
            if rem.get('has_remediation_data'):
                parts.append(f"\n### Self-Healing System Status")
                parts.append(f"Progress: {rem.get('completed', 0)}/{rem.get('total_tasks', 0)} ({rem.get('percentage', 0)}%)")
                parts.append(f"Completed: {rem.get('completed', 0)} | In Progress: {rem.get('in_progress', 0)} | Pending: {rem.get('pending', 0)}")
                if rem.get('top_agents'):
                    agent_list = ", ".join([f"{a['agent']}({a['tasks']})" for a in rem['top_agents'][:3]])
                    parts.append(f"Top Agents: {agent_list}")

        # Session 972: Workspace/UI knowledge section
        if 'workspace_info' in context:
            ws = context['workspace_info']
            parts.append("\n### Platform Navigation & Features")
            parts.append("\n**Workspace Tabs (9):**")
            for tab in ws.get('workspace_tabs', []):
                line = f"- **{tab['name']}** (`{tab['route']}`) — {tab['description']}"
                if tab.get('sub_tabs'):
                    line += f" | Sub-tabs: {tab['sub_tabs']}"
                parts.append(line)
            parts.append("\n**Standalone Pages (8):**")
            for page in ws.get('standalone_pages', []):
                parts.append(f"- **{page['name']}** (`{page['route']}`) — {page['description']}")

        return "\n".join(parts)


# Singleton instance
_pa_knowledge_injector: Optional[PAKnowledgeInjector] = None


def get_pa_knowledge_injector() -> PAKnowledgeInjector:
    """Get the singleton PAKnowledgeInjector instance."""
    global _pa_knowledge_injector
    if _pa_knowledge_injector is None:
        _pa_knowledge_injector = PAKnowledgeInjector()
    return _pa_knowledge_injector
