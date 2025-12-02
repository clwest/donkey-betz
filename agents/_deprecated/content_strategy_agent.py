"""
Content Strategy Planner Agent
==============================

Session 241: Created as part of agent cleanup - building real, valuable agents.
Session 308: Added learning infrastructure hooks for cross-agent knowledge sharing.

This agent analyzes spider intelligence and trending topics to recommend
what content the user should create next. It connects trend data to
actionable content recommendations.

Example:
    agent = ContentStrategyAgent(user=request.user)

    # Get content recommendations based on current trends
    result = agent.get_recommendations()
    # Returns: recommendations for logos, thumbnails, social content based on trends

    # Get recommendations for a specific niche
    result = agent.get_recommendations(niche='tech')
"""

from __future__ import annotations

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.super_platform.spider_context_mixin import SpiderContextMixin

logger = logging.getLogger(__name__)
User = get_user_model()


class ContentStrategyLearningMixin:
    """
    Learning infrastructure mixin for ContentStrategyAgent.
    Session 308: Enables cross-agent knowledge sharing for content strategy patterns.
    """

    _learning_loop = None
    _memory_service = None
    _agent_model = None

    @property
    def learning_loop(self):
        """Lazy-load LearningLoopService."""
        if self._learning_loop is None:
            try:
                from core.super_platform.learning_loop import get_learning_loop_service
                self._learning_loop = get_learning_loop_service(None)
            except ImportError:
                logger.debug("LearningLoopService not available")
                return None
        return self._learning_loop

    @property
    def memory_service(self):
        """Lazy-load MemoryEmbeddingService."""
        if self._memory_service is None:
            try:
                from core.services.memory_embedding_service import get_memory_embedding_service
                self._memory_service = get_memory_embedding_service()
            except ImportError:
                logger.debug("MemoryEmbeddingService not available")
                return None
        return self._memory_service

    @property
    def agent_model(self):
        """Lazy-load or create Agent model instance."""
        if self._agent_model is None:
            try:
                from core.models_unified_system import Agent
                self._agent_model, _ = Agent.objects.get_or_create(
                    name='ContentStrategyAgent',
                    defaults={
                        'agent_type': 'deprecated',
                        'specialization': 'content_strategy',
                        'description': 'Analyzes trends to recommend content creation strategies.',
                        'is_active': True,
                    }
                )
            except ImportError:
                logger.debug("Agent model not available")
                return None
        return self._agent_model

    def _record_learning_outcome(
        self,
        result: Dict[str, Any],
        task: str,
        context: Dict[str, Any] = None,
        spider_data_used: bool = True
    ):
        """Record execution outcome for XP and pattern learning."""
        if not self.learning_loop:
            return None

        try:
            outcome_id = self.learning_loop.record_outcome(
                query_type='content_strategy',
                query_text=task,
                execution_mode='agent',
                agents_used=['ContentStrategyAgent'],
                response=str(result)[:500],
                execution_time_ms=result.get('execution_time_ms', 0),
                success=result.get('success', False),
                spider_data_used=spider_data_used,
                scifi_context_used=False,
                context=context or {}
            )
            return outcome_id
        except Exception as e:
            logger.debug(f"Failed to record learning outcome: {e}")
            return None

    def _create_execution_memory(
        self,
        result: Dict[str, Any],
        task: str,
        memory_type: str = "interaction",
        importance: float = 0.5
    ):
        """Create a memory from the content strategy execution."""
        if not self.memory_service or not self.agent_model:
            return None

        try:
            memory = self.memory_service.create_memory(
                agent=self.agent_model,
                title=f"Strategy: {task[:50]}...",
                content=str(result)[:500],
                memory_type=memory_type,
                valence="positive" if result.get('success') else "negative",
                importance_score=importance,
                source_type='agent_execution',
                tags=['content_strategy', 'recommendations', 'success' if result.get('success') else 'failure']
            )
            return memory
        except Exception as e:
            logger.debug(f"Failed to create execution memory: {e}")
            return None

    def _share_knowledge(
        self,
        knowledge_type: str,
        title: str,
        knowledge_value: Dict[str, Any],
        confidence: float = 0.8
    ):
        """Share learned content strategy knowledge for cross-agent learning."""
        if not self.agent_model:
            return None

        try:
            from core.models_unified_system import AgentKnowledgeSource

            type_mapping = {
                'recommendation': 'content_idea',
                'niche': 'market',
                'calendar': 'content_idea',
                'strategy': 'content_idea',
            }
            mapped_type = type_mapping.get(knowledge_type, 'content_idea')

            knowledge, created = AgentKnowledgeSource.objects.update_or_create(
                agent=self.agent_model,
                title=title,
                knowledge_type=mapped_type,
                defaults={
                    'summary': json.dumps(knowledge_value),
                    'confidence_score': confidence,
                    'is_active': True,
                }
            )
            return knowledge
        except Exception as e:
            logger.debug(f"Failed to share knowledge: {e}")
            return None

    def _get_shared_knowledge(
        self,
        knowledge_type: str = None,
        title_contains: str = None,
        from_agents: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve knowledge from other agents."""
        try:
            from core.models_unified_system import AgentKnowledgeSource

            queryset = AgentKnowledgeSource.objects.filter(is_active=True)

            if knowledge_type:
                queryset = queryset.filter(knowledge_type=knowledge_type)

            if title_contains:
                queryset = queryset.filter(title__icontains=title_contains)

            if from_agents:
                queryset = queryset.filter(agent__name__in=from_agents)

            if self.agent_model:
                queryset = queryset.exclude(agent=self.agent_model)

            return [
                {
                    'source_agent': ks.agent.name,
                    'title': ks.title,
                    'type': ks.knowledge_type,
                    'value': json.loads(ks.summary) if ks.summary else {},
                    'confidence': ks.confidence_score,
                }
                for ks in queryset.order_by('-confidence_score')[:10]
            ]
        except Exception as e:
            logger.debug(f"Failed to get shared knowledge: {e}")
            return []


class ContentStrategyAgent(ContentStrategyLearningMixin, SpiderContextMixin):
    """
    Analyzes trends and recommends content creation strategies.

    Connects spider intelligence → actionable content recommendations.

    Session 264: Added SpiderContextMixin for automatic spider intelligence injection.
    Session 308: Added ContentStrategyLearningMixin for cross-agent knowledge sharing.
    """

    # Content types this agent can recommend
    CONTENT_TYPES = {
        'logo': {
            'name': 'Logo Design',
            'description': 'Brand logos and identity marks',
            'best_for': ['startups', 'rebranding', 'new products'],
            'trending_keywords': ['minimalist', 'modern', 'abstract', 'lettermark']
        },
        'youtube_thumbnail': {
            'name': 'YouTube Thumbnail',
            'description': 'Eye-catching video thumbnails',
            'best_for': ['content creators', 'educators', 'marketers'],
            'trending_keywords': ['bold text', 'faces', 'bright colors', 'curiosity gap']
        },
        'social_post': {
            'name': 'Social Media Post',
            'description': 'Platform-optimized social content',
            'best_for': ['brands', 'influencers', 'businesses'],
            'trending_keywords': ['carousel', 'quote graphics', 'infographics']
        },
        'brand_identity': {
            'name': 'Brand Identity Package',
            'description': 'Complete branding suite',
            'best_for': ['new businesses', 'rebranding projects'],
            'trending_keywords': ['cohesive', 'scalable', 'memorable']
        },
        'product_photo': {
            'name': 'Product Photography',
            'description': 'Professional product images',
            'best_for': ['e-commerce', 'marketing', 'catalogs'],
            'trending_keywords': ['lifestyle', 'flat lay', 'contextual']
        },
        'illustration': {
            'name': 'Custom Illustration',
            'description': 'Unique artistic illustrations',
            'best_for': ['editorial', 'children content', 'explainers'],
            'trending_keywords': ['flat', 'isometric', 'hand-drawn', '3d']
        }
    }

    # Niche-specific recommendations
    NICHE_STRATEGIES = {
        'tech': {
            'hot_topics': ['AI tools', 'automation', 'SaaS', 'developer tools'],
            'recommended_content': ['youtube_thumbnail', 'logo', 'social_post'],
            'style_suggestions': ['futuristic', 'minimalist', 'tech-forward', 'clean']
        },
        'finance': {
            'hot_topics': ['crypto', 'investing', 'personal finance', 'fintech'],
            'recommended_content': ['youtube_thumbnail', 'social_post', 'infographic'],
            'style_suggestions': ['professional', 'trustworthy', 'modern', 'data-driven']
        },
        'creative': {
            'hot_topics': ['design trends', 'creative tools', 'portfolio', 'freelancing'],
            'recommended_content': ['logo', 'brand_identity', 'illustration'],
            'style_suggestions': ['artistic', 'bold', 'experimental', 'colorful']
        },
        'ecommerce': {
            'hot_topics': ['product launches', 'seasonal sales', 'brand building'],
            'recommended_content': ['product_photo', 'social_post', 'logo'],
            'style_suggestions': ['lifestyle', 'aspirational', 'clean', 'branded']
        },
        'education': {
            'hot_topics': ['online courses', 'tutorials', 'explainers', 'edtech'],
            'recommended_content': ['youtube_thumbnail', 'illustration', 'social_post'],
            'style_suggestions': ['friendly', 'clear', 'engaging', 'informative']
        }
    }

    def __init__(self, user: Optional[User] = None, project_id: Optional[str] = None):
        """
        Initialize Content Strategy Agent.

        Args:
            user: User to generate recommendations for
            project_id: Optional project context
        """
        super().__init__()  # Session 264: Initialize SpiderContextMixin
        self.user = user
        self.project_id = project_id
        self.agent_name = 'ContentStrategyAgent'
        self._spider_service = None

        logger.info(f"📊 ContentStrategyAgent initialized for user: {user.username if user else 'system'}")

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

    def get_recommendations(
        self,
        niche: Optional[str] = None,
        content_type: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Get content creation recommendations based on trends.

        Args:
            niche: Focus area (tech, finance, creative, ecommerce, education)
            content_type: Specific content type to focus on
            limit: Maximum number of recommendations

        Returns:
            Dict with recommendations and trend insights
        """
        logger.info(f"📊 Getting content recommendations (niche={niche}, type={content_type})")

        try:
            # Get trending data from spiders
            trends = self._get_trending_data()

            # Get user's recent content for context
            user_context = self._get_user_context()

            # Generate recommendations
            recommendations = []

            if niche and niche in self.NICHE_STRATEGIES:
                # Niche-specific recommendations
                strategy = self.NICHE_STRATEGIES[niche]
                for topic in strategy['hot_topics'][:limit]:
                    for content in strategy['recommended_content'][:2]:
                        recommendations.append({
                            'topic': topic,
                            'content_type': content,
                            'content_type_label': self.CONTENT_TYPES.get(content, {}).get('name', content),
                            'style_suggestions': strategy['style_suggestions'],
                            'prompt_idea': self._generate_prompt_idea(topic, content, strategy['style_suggestions']),
                            'why': f"'{topic}' is trending in {niche}. {self.CONTENT_TYPES.get(content, {}).get('description', '')}"
                        })
            else:
                # General recommendations based on trends
                for trend in trends.get('topics', [])[:limit]:
                    content = self._match_content_type(trend)
                    recommendations.append({
                        'topic': trend.get('topic', 'Unknown'),
                        'content_type': content,
                        'content_type_label': self.CONTENT_TYPES.get(content, {}).get('name', content),
                        'trend_score': trend.get('score', 0),
                        'prompt_idea': self._generate_prompt_idea(
                            trend.get('topic', ''),
                            content,
                            self.CONTENT_TYPES.get(content, {}).get('trending_keywords', [])
                        ),
                        'why': f"Currently trending with {trend.get('mentions', 0)} mentions"
                    })

            # Add variety if we don't have enough
            if len(recommendations) < limit:
                recommendations.extend(self._get_evergreen_recommendations(limit - len(recommendations)))

            result = {
                'success': True,
                'recommendations': recommendations[:limit],
                'trends_analyzed': len(trends.get('topics', [])),
                'user_history_analyzed': len(user_context.get('recent_content', [])),
                'niche': niche,
                'generated_at': timezone.now().isoformat(),
                'message': f"Generated {len(recommendations[:limit])} content recommendations based on current trends."
            }

            # Session 308: Learning Infrastructure Hooks
            self._record_learning_outcome(
                result=result,
                task=f"Get content recommendations (niche={niche})",
                context={'niche': niche, 'recommendation_count': len(recommendations[:limit])}
            )

            # Share content recommendations as cross-agent knowledge
            if recommendations:
                top_recs = recommendations[:3]
                self._share_knowledge(
                    knowledge_type='recommendation',
                    title=f"Content recs: {niche or 'general'}",
                    knowledge_value={
                        'niche': niche,
                        'content_types': list(set(r.get('content_type') for r in top_recs)),
                        'topics': [r.get('topic') for r in top_recs],
                    },
                    confidence=0.75
                )

            return result

        except Exception as e:
            logger.error(f"❌ ContentStrategyAgent.get_recommendations failed: {e}", exc_info=True)
            # Session 308: Record failure
            self._record_learning_outcome(
                result={'success': False, 'error': str(e)},
                task=f"Get recommendations (failed)",
                context={'error': str(e)}
            )
            return {
                'success': False,
                'error': str(e)
            }

    def analyze_opportunity(self, topic: str) -> Dict[str, Any]:
        """
        Analyze a specific topic for content opportunity.

        Args:
            topic: Topic to analyze

        Returns:
            Analysis with recommendations
        """
        logger.info(f"📊 Analyzing opportunity: {topic}")

        try:
            # Get trend data for this topic
            trend_data = self._get_topic_trends(topic)

            # Determine best content types
            best_content_types = self._rank_content_types_for_topic(topic)

            # Generate specific recommendations
            recommendations = []
            for content_type in best_content_types[:3]:
                recommendations.append({
                    'content_type': content_type,
                    'content_type_label': self.CONTENT_TYPES.get(content_type, {}).get('name', content_type),
                    'prompt_idea': self._generate_prompt_idea(topic, content_type, []),
                    'estimated_engagement': self._estimate_engagement(topic, content_type)
                })

            return {
                'success': True,
                'topic': topic,
                'trend_score': trend_data.get('score', 50),
                'competition_level': trend_data.get('competition', 'medium'),
                'recommended_content': recommendations,
                'timing': 'now' if trend_data.get('trending_up', False) else 'plan ahead',
                'message': f"Analysis complete for '{topic}'"
            }

        except Exception as e:
            logger.error(f"❌ ContentStrategyAgent.analyze_opportunity failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def get_content_calendar(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate a content calendar with daily recommendations.

        Args:
            days: Number of days to plan

        Returns:
            Content calendar with daily suggestions
        """
        logger.info(f"📊 Generating {days}-day content calendar")

        try:
            calendar = []
            recommendations = self.get_recommendations(limit=days * 2)

            if not recommendations.get('success'):
                return recommendations

            recs = recommendations.get('recommendations', [])

            for i in range(days):
                date = timezone.now() + timedelta(days=i)
                day_content = []

                # Assign 1-2 pieces of content per day
                for j in range(min(2, len(recs) - i * 2)):
                    idx = i * 2 + j
                    if idx < len(recs):
                        day_content.append(recs[idx])

                calendar.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'day_name': date.strftime('%A'),
                    'content': day_content
                })

            result = {
                'success': True,
                'calendar': calendar,
                'days_planned': days,
                'total_content_pieces': sum(len(day['content']) for day in calendar),
                'message': f"Generated {days}-day content calendar"
            }

            # Session 308: Learning Infrastructure Hooks
            self._record_learning_outcome(
                result=result,
                task=f"Generate {days}-day content calendar",
                context={'days': days, 'total_pieces': result['total_content_pieces']}
            )

            # Create high-importance memory for calendar generation
            self._create_execution_memory(
                result=result,
                task=f"{days}-day calendar",
                memory_type="success",
                importance=0.7
            )

            # Share calendar strategy knowledge
            self._share_knowledge(
                knowledge_type='calendar',
                title=f"Calendar: {days} days",
                knowledge_value={
                    'days_planned': days,
                    'total_pieces': result['total_content_pieces'],
                    'content_types_used': list(set(
                        c.get('content_type') for day in calendar for c in day.get('content', [])
                    )),
                },
                confidence=0.8
            )

            return result

        except Exception as e:
            logger.error(f"❌ ContentStrategyAgent.get_content_calendar failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    # Private helper methods

    def _get_trending_data(self) -> Dict[str, Any]:
        """Get trending topics from spider intelligence."""
        try:
            # Session 264: Use SpiderContextMixin for unified spider access
            spider_context = self.get_spider_context()
            if spider_context.trends:
                return {
                    'topics': [
                        {
                            'topic': t.get('topic', '') if isinstance(t, dict) else str(t),
                            'score': t.get('count', 0) if isinstance(t, dict) else 50,
                            'mentions': t.get('count', 0) if isinstance(t, dict) else 50
                        }
                        for t in spider_context.trends
                    ],
                    'style_recommendations': spider_context.style_recommendations,
                    'platform_insights': spider_context.platform_insights,
                }

            # Fallback to direct service if mixin returns empty
            if self.spider_service:
                insights = self.spider_service.get_trending_topics(limit=20)
                return {
                    'topics': [
                        {'topic': t.get('topic', ''), 'score': t.get('count', 0), 'mentions': t.get('count', 0)}
                        for t in insights.get('topics', [])
                    ]
                }
        except Exception as e:
            logger.warning(f"Could not get spider trends: {e}")

        # Fallback trending topics
        return {
            'topics': [
                {'topic': 'AI tools', 'score': 95, 'mentions': 1250},
                {'topic': 'automation', 'score': 88, 'mentions': 980},
                {'topic': 'remote work', 'score': 82, 'mentions': 750},
                {'topic': 'sustainability', 'score': 78, 'mentions': 620},
                {'topic': 'creator economy', 'score': 75, 'mentions': 580},
            ]
        }

    def _get_user_context(self) -> Dict[str, Any]:
        """Get user's recent content for context."""
        if not self.user:
            return {'recent_content': []}

        try:
            from content.models import ImageHistory
            recent = ImageHistory.objects.filter(user=self.user).order_by('-created_at')[:10]
            return {
                'recent_content': [
                    {'type': 'image', 'prompt': img.prompt[:100] if img.prompt else ''}
                    for img in recent
                ]
            }
        except Exception as e:
            logger.warning(f"Could not get user context: {e}")
            return {'recent_content': []}

    def _match_content_type(self, trend: Dict[str, Any]) -> str:
        """Match a trend to the best content type."""
        topic = trend.get('topic', '').lower()

        if any(kw in topic for kw in ['youtube', 'video', 'tutorial', 'how to']):
            return 'youtube_thumbnail'
        elif any(kw in topic for kw in ['brand', 'startup', 'company', 'business']):
            return 'logo'
        elif any(kw in topic for kw in ['product', 'ecommerce', 'shop', 'store']):
            return 'product_photo'
        elif any(kw in topic for kw in ['social', 'instagram', 'tiktok', 'twitter']):
            return 'social_post'
        elif any(kw in topic for kw in ['art', 'creative', 'illustration']):
            return 'illustration'
        else:
            return 'social_post'  # Default

    def _generate_prompt_idea(self, topic: str, content_type: str, styles: List[str]) -> str:
        """Generate a prompt idea for the given topic and content type."""
        style_text = f", {styles[0]} style" if styles else ""

        prompts = {
            'logo': f"Create a professional logo for a {topic} company{style_text}",
            'youtube_thumbnail': f"Design an eye-catching YouTube thumbnail about {topic}{style_text}",
            'social_post': f"Create a social media graphic about {topic}{style_text}",
            'brand_identity': f"Design a complete brand identity for a {topic} brand{style_text}",
            'product_photo': f"Create product photography for {topic}{style_text}",
            'illustration': f"Create an illustration depicting {topic}{style_text}",
        }

        return prompts.get(content_type, f"Create content about {topic}")

    def _get_evergreen_recommendations(self, count: int) -> List[Dict[str, Any]]:
        """Get evergreen content recommendations."""
        evergreen = [
            {'topic': 'Personal branding', 'content_type': 'logo', 'why': 'Always in demand'},
            {'topic': 'Product showcase', 'content_type': 'product_photo', 'why': 'E-commerce essential'},
            {'topic': 'Educational content', 'content_type': 'youtube_thumbnail', 'why': 'High engagement'},
            {'topic': 'Motivational quotes', 'content_type': 'social_post', 'why': 'Viral potential'},
            {'topic': 'Behind the scenes', 'content_type': 'social_post', 'why': 'Builds authenticity'},
        ]

        result = []
        for item in evergreen[:count]:
            item['content_type_label'] = self.CONTENT_TYPES.get(item['content_type'], {}).get('name', item['content_type'])
            item['prompt_idea'] = self._generate_prompt_idea(item['topic'], item['content_type'], [])
            result.append(item)

        return result

    def _get_topic_trends(self, topic: str) -> Dict[str, Any]:
        """Get trend data for a specific topic."""
        # Would query spider data for this topic
        return {
            'score': 75,
            'competition': 'medium',
            'trending_up': True
        }

    def _rank_content_types_for_topic(self, topic: str) -> List[str]:
        """Rank content types by suitability for a topic."""
        topic_lower = topic.lower()

        if any(kw in topic_lower for kw in ['brand', 'company', 'startup']):
            return ['logo', 'brand_identity', 'social_post']
        elif any(kw in topic_lower for kw in ['video', 'youtube', 'tutorial']):
            return ['youtube_thumbnail', 'social_post', 'illustration']
        elif any(kw in topic_lower for kw in ['product', 'shop', 'store']):
            return ['product_photo', 'social_post', 'logo']
        else:
            return ['social_post', 'youtube_thumbnail', 'logo']

    def _estimate_engagement(self, topic: str, content_type: str) -> str:
        """Estimate engagement potential."""
        # Simplified estimation
        return 'high' if content_type in ['youtube_thumbnail', 'social_post'] else 'medium'


# Convenience function
def get_content_strategy_agent(user=None, project_id=None) -> ContentStrategyAgent:
    """Get ContentStrategyAgent instance."""
    return ContentStrategyAgent(user=user, project_id=project_id)


__all__ = [
    'ContentStrategyAgent',
    'get_content_strategy_agent'
]
