"""
Context Aggregator - Gathers All System Intelligence

This module aggregates context from all platform components:
- Spider Intelligence Service (real-time data)
- Memory Palace (past interactions)
- Mood System (agent emotional states)
- Agent Registry (available agents)
- User Profile (preferences)
- Opportunity Engine (revenue context)
- Platform Intelligence (Session 565: agent knowledge, dreams, policies)

Session 264: Phase 1 Foundation
Session 565: Added PAIntelligenceEnricher integration
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from django.utils import timezone

from .query_classifier import ClassificationResult, QueryType

logger = logging.getLogger(__name__)


@dataclass
class AggregatedContext:
    """Complete context gathered from all sources."""
    # Spider data
    spider_data: Dict[str, Any] = field(default_factory=dict)
    spider_fetch_time: Optional[datetime] = None

    # Memory data
    memories: List[Dict[str, Any]] = field(default_factory=list)
    memory_tags: List[str] = field(default_factory=list)  # Session 284: Replaced memory_clusters with tags

    # Mood data
    agent_mood: Dict[str, Any] = field(default_factory=dict)
    mood_history: List[Dict[str, Any]] = field(default_factory=list)

    # Agent data
    available_agents: List[str] = field(default_factory=list)
    agent_relationships: Dict[str, Any] = field(default_factory=dict)

    # User data
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    user_history: List[Dict[str, Any]] = field(default_factory=list)

    # Opportunity data
    active_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    revenue_summary: Dict[str, Any] = field(default_factory=dict)

    # Session 565: Platform Intelligence (agent knowledge, dreams, policies)
    intelligence_context: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    aggregation_time: datetime = field(default_factory=timezone.now)
    sources_used: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'spider_data': self.spider_data,
            'memories': self.memories,
            'agent_mood': self.agent_mood,
            'available_agents': self.available_agents,
            'user_preferences': self.user_preferences,
            'active_opportunities': self.active_opportunities,
            'intelligence_context': self.intelligence_context,  # Session 565
            'sources_used': self.sources_used,
            'aggregation_time': self.aggregation_time.isoformat(),
        }


class ContextAggregator:
    """
    Aggregates context from all platform data sources.

    This is the central intelligence gathering point that collects
    relevant data based on the query classification.
    """

    def __init__(self, user=None):
        """
        Initialize the context aggregator.

        Args:
            user: Optional user for personalization
        """
        self.user = user
        self._spider_service = None
        self._memory_service = None
        self._intelligence_enricher = None  # Session 565

    @property
    def spider_service(self):
        """Lazy load spider intelligence service."""
        if self._spider_service is None:
            try:
                from core.services.spider_intelligence import SpiderIntelligenceService
                self._spider_service = SpiderIntelligenceService()
            except ImportError:
                logger.warning("SpiderIntelligenceService not available")
        return self._spider_service

    @property
    def intelligence_enricher(self):
        """Session 565: Lazy load PA intelligence enricher."""
        if self._intelligence_enricher is None:
            try:
                from core.services.pa_intelligence_enricher import PAIntelligenceEnricher
                self._intelligence_enricher = PAIntelligenceEnricher()
            except ImportError:
                logger.warning("PAIntelligenceEnricher not available")
        return self._intelligence_enricher

    def aggregate(
        self,
        classification: ClassificationResult,
        query: str
    ) -> AggregatedContext:
        """
        Aggregate all relevant context based on classification.

        Args:
            classification: The query classification result
            query: The original user query

        Returns:
            AggregatedContext with all gathered data
        """
        context = AggregatedContext()

        # Always get available agents
        context.available_agents = self._get_available_agents()
        context.sources_used.append('agent_registry')

        # Get spider data if needed
        if classification.requires_spider_data:
            spider_data = self._get_spider_context(query, classification)
            context.spider_data = spider_data
            context.spider_fetch_time = timezone.now()
            context.sources_used.append('spider_intelligence')
            # Session 483: Debug logging
            logger.info(f"🕷️ [Session 483] ContextAggregator got spider_data with {len(spider_data.get('trends', []))} trends")
            if spider_data.get('trends'):
                logger.info(f"🕷️ [Session 483] First trend: {spider_data['trends'][0]}")

        # Get memory data if needed
        if classification.requires_memory:
            memories = self._get_memory_context(query, classification)
            context.memories = memories.get('memories', [])
            context.memory_tags = memories.get('tags', [])  # Session 284: Use tags instead of clusters
            context.sources_used.append('memory_palace')

        # Get mood data if needed
        if classification.requires_mood_check:
            mood_data = self._get_mood_context(classification.suggested_agents)
            context.agent_mood = mood_data.get('current', {})
            context.mood_history = mood_data.get('history', [])
            context.sources_used.append('mood_system')

        # Get user preferences
        if self.user:
            context.user_preferences = self._get_user_preferences()
            context.user_history = self._get_user_history()
            context.sources_used.append('user_profile')

        # Get opportunity data if relevant
        if classification.primary_type == QueryType.OPPORTUNITY:
            opp_data = self._get_opportunity_context()
            context.active_opportunities = opp_data.get('opportunities', [])
            context.revenue_summary = opp_data.get('revenue', {})
            context.sources_used.append('opportunity_engine')

        # Get agent relationships for collaboration
        if classification.primary_type == QueryType.COLLABORATION:
            context.agent_relationships = self._get_agent_relationships(
                classification.suggested_agents
            )
            context.sources_used.append('agent_relationships')

        # Session 565: Get platform intelligence (agent knowledge, dreams, policies)
        # Always enrich with platform intelligence for richer context
        intelligence = self._get_intelligence_context(query, classification)
        if intelligence:
            context.intelligence_context = intelligence
            context.sources_used.append('platform_intelligence')
            logger.info(
                f"🧠 [Session 565] Intelligence enrichment: "
                f"{intelligence.get('metadata', {}).get('knowledge_count', 0)} knowledge, "
                f"{intelligence.get('metadata', {}).get('experts_count', 0)} experts, "
                f"{intelligence.get('metadata', {}).get('dreams_count', 0)} dreams"
            )

        return context

    def _get_spider_context(
        self,
        query: str,
        classification: ClassificationResult
    ) -> Dict[str, Any]:
        """Get relevant spider intelligence for the query."""
        if not self.spider_service:
            return {}

        try:
            # Get insights based on query
            insights = self.spider_service.get_insights_for_prompt(query)

            # Add trending topics
            trends = self.spider_service.get_trending_topics(hours=24)

            # Add market data if relevant entities detected
            market_data = {}
            entities = classification.detected_entities

            if 'topic' in entities:
                topics = entities['topic']
                if any(t in ['crypto', 'bitcoin', 'ethereum', 'nft'] for t in topics):
                    market_data = self.spider_service.get_market_insights()

            # Add job market data if opportunity-focused
            jobs_data = {}
            if classification.primary_type in [QueryType.OPPORTUNITY, QueryType.ANALYSIS]:
                jobs_data = self.spider_service.get_job_market_summary()

            # Search for specific content if query is specific
            search_results = []
            if len(query) > 10:  # Only search if query has substance
                search_results = self.spider_service.search_spider_data(query)

            return {
                'insights': insights,
                'trends': trends[:10] if trends else [],
                'market': market_data,
                'jobs': jobs_data,
                'search_results': search_results[:5] if search_results else [],
                'news': insights.get('relevant_trends', [])[:5],
            }

        except Exception as e:
            logger.error(f"Error getting spider context: {e}")
            return {'error': str(e)}

    def _get_memory_context(
        self,
        query: str,
        classification: ClassificationResult
    ) -> Dict[str, Any]:
        """
        Get relevant memories from the Memory Palace.

        Session 284: Updated to use tags instead of MemoryCluster.
        MemoryCluster is deprecated - use AgentMemory.tags for grouping.
        """
        try:
            from core.models_unified_system import AgentMemory

            memories = []
            tags = []

            # Get recent relevant memories
            if self.user:
                memory_qs = AgentMemory.objects.filter(
                    user=self.user
                ).order_by('-created_at')[:10]

                memories = [
                    {
                        'id': str(m.id),
                        'content': m.content[:200] if hasattr(m, 'content') else str(m),
                        'title': getattr(m, 'title', '')[:100],
                        'created_at': m.created_at.isoformat() if hasattr(m, 'created_at') else '',
                        'agent': m.agent.name if hasattr(m, 'agent') and m.agent else 'Unknown',
                        'tags': getattr(m, 'tags', []),  # Session 284: Use tags instead of clusters
                    }
                    for m in memory_qs
                ]

                # Session 284: Get unique tags instead of clusters
                # This is more efficient than MemoryCluster queries
                all_tags = set()
                for m in memory_qs:
                    if hasattr(m, 'tags') and m.tags:
                        all_tags.update(m.tags)
                tags = sorted(all_tags)[:10]

            return {
                'memories': memories,
                'tags': tags,  # Session 284: Renamed from 'clusters' to 'tags'
            }

        except Exception as e:
            logger.error(f"Error getting memory context: {e}")
            return {'memories': [], 'tags': [], 'error': str(e)}

    def _get_mood_context(self, agents: List[str]) -> Dict[str, Any]:
        """Get mood data for relevant agents."""
        try:
            from core.models_unified_system import AgentMood, MoodHistory

            # Get current mood (system-wide or for primary agent)
            current_mood = {
                'name': 'focused',
                'description': 'Balanced and attentive',
                'intensity': 0.7,
            }

            try:
                latest_mood = AgentMood.objects.order_by('-updated_at').first()
                if latest_mood:
                    current_mood = {
                        'name': getattr(latest_mood, 'mood_type', 'focused'),
                        'description': getattr(latest_mood, 'description', ''),
                        'intensity': getattr(latest_mood, 'intensity', 0.7),
                    }
            except Exception as _e:
                logger.warning(
                    "context_aggregator._get_mood_context: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

            # Get recent mood history
            mood_history = []
            try:
                history_qs = MoodHistory.objects.order_by('-timestamp')[:5]
                mood_history = [
                    {
                        'mood': getattr(h, 'mood_type', 'unknown'),
                        'timestamp': h.timestamp.isoformat() if hasattr(h, 'timestamp') else '',
                        'trigger': getattr(h, 'trigger', ''),
                    }
                    for h in history_qs
                ]
            except Exception as _e:
                logger.warning(
                    "context_aggregator._get_mood_context: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

            return {
                'current': current_mood,
                'history': mood_history,
            }

        except Exception as e:
            logger.error(f"Error getting mood context: {e}")
            return {
                'current': {'name': 'focused', 'description': 'Default mood', 'intensity': 0.5},
                'history': [],
                'error': str(e),
            }

    def _get_available_agents(self) -> List[str]:
        """Get list of available agents from registry."""
        try:
            from core.agents.registry import get_agent_registry
            registry = get_agent_registry()
            agents = registry.list_agents() if hasattr(registry, 'list_agents') else []
            return [a.get('name', str(a)) if isinstance(a, dict) else str(a) for a in agents]
        except Exception as e:
            logger.warning(f"Could not get agent registry: {e}")
            # Return known agents as fallback
            return [
                'ImageAgent', 'VideoAgent', 'AudioAgent', '3DGenerationAgent',
                'ResearchAgent', 'TrendAnalysisAgent', 'ContentStrategyAgent',
                'SEOOptimizerAgent', 'BrandIdentityAgent', 'SocialMediaAgent',
                'CreativeDirectorAgent', 'WorkflowOrchestrationAgent',
                'OpportunityScoringAgent', 'PromptEngineeringAgent',
            ]

    def _get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences and settings."""
        if not self.user:
            return {}

        try:
            # Try to get from user profile or settings
            preferences = {
                'username': self.user.username,
                'favorite_styles': [],
                'default_size': '1024x1024',
                'tone': 'professional',
            }

            # Check for extended profile
            if hasattr(self.user, 'profile'):
                profile = self.user.profile
                if hasattr(profile, 'preferences'):
                    preferences.update(profile.preferences)

            return preferences

        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}

    def _get_user_history(self) -> List[Dict[str, Any]]:
        """Get recent user interaction history."""
        if not self.user:
            return []

        try:
            from content.models import ImageHistory

            # Get recent image generations
            recent = ImageHistory.objects.filter(
                user=self.user
            ).order_by('-created_at')[:10]

            return [
                {
                    'type': 'image',
                    'prompt': img.prompt[:100] if hasattr(img, 'prompt') else '',
                    'style': getattr(img, 'style', ''),
                    'created_at': img.created_at.isoformat() if hasattr(img, 'created_at') else '',
                }
                for img in recent
            ]

        except Exception as e:
            logger.error(f"Error getting user history: {e}")
            return []

    def _get_opportunity_context(self) -> Dict[str, Any]:
        """Get active opportunities and revenue data."""
        try:
            from core.models_unified_system import Opportunity, Revenue

            # Get top opportunities
            opportunities = []
            try:
                opp_qs = Opportunity.objects.filter(
                    status='active'
                ).order_by('-score')[:10]

                opportunities = [
                    {
                        'id': o.id,
                        'type': getattr(o, 'opportunity_type', 'unknown'),
                        'score': getattr(o, 'score', 0),
                        'profit_potential': float(getattr(o, 'profit_potential', 0)),
                        'description': getattr(o, 'description', '')[:100],
                    }
                    for o in opp_qs
                ]
            except Exception as _e:
                logger.warning(
                    "context_aggregator._get_opportunity_context: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

            # Get revenue summary
            revenue = {}
            try:
                from django.db.models import Sum
                thirty_days_ago = timezone.now() - timedelta(days=30)

                revenue_qs = Revenue.objects.filter(
                    created_at__gte=thirty_days_ago
                ).aggregate(
                    total=Sum('amount')
                )

                revenue = {
                    'last_30_days': float(revenue_qs.get('total') or 0),
                    'currency': 'USD',
                }
            except Exception as _e:
                logger.warning(
                    "context_aggregator._get_opportunity_context: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

            return {
                'opportunities': opportunities,
                'revenue': revenue,
            }

        except Exception as e:
            logger.error(f"Error getting opportunity context: {e}")
            return {'opportunities': [], 'revenue': {}, 'error': str(e)}

    def _get_agent_relationships(self, agents: List[str]) -> Dict[str, Any]:
        """Get relationships between agents for collaboration."""
        try:
            from core.models_unified_system import AgentRelationship

            relationships = {}

            for agent in agents:
                agent_rels = []
                try:
                    rels = AgentRelationship.objects.filter(
                        agent_name=agent
                    )[:5]

                    agent_rels = [
                        {
                            'with_agent': getattr(r, 'related_agent', ''),
                            'type': getattr(r, 'relationship_type', 'neutral'),
                            'strength': getattr(r, 'strength', 0.5),
                        }
                        for r in rels
                    ]
                except Exception as _e:
                    logger.warning(
                        "context_aggregator._get_agent_relationships: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

                relationships[agent] = agent_rels

            return relationships

        except Exception as e:
            logger.error(f"Error getting agent relationships: {e}")
            return {}

    def get_quick_context(self, query_type: QueryType) -> Dict[str, Any]:
        """
        Get minimal context for quick responses.

        Used when we don't need full aggregation.
        """
        context = {
            'available_agents': self._get_available_agents()[:5],
            'timestamp': timezone.now().isoformat(),
        }

        if query_type == QueryType.QUESTION:
            # Just get trending topics
            if self.spider_service:
                try:
                    trends = self.spider_service.get_trending_topics(hours=6)
                    context['trends'] = trends[:5] if trends else []
                except Exception as _e:
                    logger.warning(
                        "context_aggregator.get_quick_context: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

        return context

    def _get_intelligence_context(
        self,
        query: str,
        classification: ClassificationResult
    ) -> Dict[str, Any]:
        """
        Session 565: Get platform intelligence from PA Intelligence Enricher.

        This queries agent knowledge, expert agents, high-value dreams,
        canonical policies, and spider trends to enrich the PA context.

        Args:
            query: The user's query
            classification: Query classification result

        Returns:
            Dict with knowledge, experts, dreams, policies, spider_trends,
            context_text (formatted for prompt), and attribution.
        """
        if not self.intelligence_enricher:
            return {}

        try:
            # Build user context from aggregator state
            user_context = {}
            if self.user:
                user_context = {
                    'user_id': str(self.user.id) if hasattr(self.user, 'id') else None,
                    'username': self.user.username if hasattr(self.user, 'username') else None,
                }

            # Enrich context using PAIntelligenceEnricher
            enriched = self.intelligence_enricher.enrich_context(
                message=query,
                user_context=user_context
            )

            # Only return if we got meaningful data
            if enriched and not enriched.get('error'):
                metadata = enriched.get('metadata', {})
                total_sources = (
                    metadata.get('knowledge_count', 0) +
                    metadata.get('experts_count', 0) +
                    metadata.get('dreams_count', 0) +
                    metadata.get('policies_count', 0) +
                    metadata.get('trends_count', 0)
                )

                if total_sources > 0:
                    return enriched

            return {}

        except Exception as e:
            logger.error(f"Error getting intelligence context: {e}")
            return {'error': str(e)}
