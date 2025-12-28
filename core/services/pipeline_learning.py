"""
Pipeline Learning Service - Session 449

Service for collecting feedback and generating learning insights
across the AI content pipeline stages.

Features:
1. Record stage-level feedback
2. Track style preset performance
3. Track voice performance
4. Generate and apply learning insights
5. Recommend best configurations based on history

Usage:
    from core.services.pipeline_learning import PipelineLearningService

    service = PipelineLearningService()

    # Record feedback
    service.record_stage_feedback(
        series_id='...',
        stage='image',
        rating=4.5,
        context={'style_preset': 'pixar', 'audience': 'kids'}
    )

    # Get recommendations
    best_style = service.get_best_style_for_context('kids', 'educational')
"""

import logging
from decimal import Decimal
from typing import Dict, Any, Optional, List
from datetime import timedelta

from django.db.models import Avg, Count
from django.utils import timezone

logger = logging.getLogger(__name__)


class PipelineLearningService:
    """
    Service for managing pipeline learning loops.

    Collects feedback at each pipeline stage and uses it to improve
    future content generation through data-driven recommendations.
    """

    # Minimum data points needed for confident recommendations
    MIN_SAMPLE_SIZE = 3

    # Insight refresh interval (days)
    INSIGHT_REFRESH_DAYS = 7

    def __init__(self):
        self._insights_cache = {}
        self._cache_timestamp = None

    # =========================================================================
    # FEEDBACK COLLECTION
    # =========================================================================

    def record_stage_feedback(
        self,
        stage: str,
        rating: float,
        context: Dict[str, Any],
        series_id: str = None,
        episode_id: str = None,
        content_package_id: str = None,
        user_id: int = None,
        feedback_type: str = 'user_rating',
        comment: str = ''
    ) -> Optional['PipelineStageFeedback']:
        """
        Record feedback for a pipeline stage.

        Args:
            stage: Pipeline stage (research, script, image, voice, video, package)
            rating: Rating from 1.0 to 5.0
            context: Stage-specific context (style, voice, audience, etc.)
            series_id: Optional series UUID
            episode_id: Optional episode UUID
            content_package_id: Optional content package UUID
            user_id: Optional user ID
            feedback_type: Type of feedback (user_rating, implicit, automated, ab_test)
            comment: Optional text comment

        Returns:
            Created PipelineStageFeedback instance
        """
        try:
            from core.models_pipeline_feedback import (
                PipelineStageFeedback
            )
            from core.models_ai_series import AISeries, SeriesEpisode
            from django.contrib.auth import get_user_model

            User = get_user_model()

            # Validate rating
            rating = max(1.0, min(5.0, float(rating)))

            # Build feedback record
            feedback_data = {
                'stage': stage,
                'feedback_type': feedback_type,
                'rating': Decimal(str(rating)),
                'context': context,
                'comment': comment,
            }

            # Link to related objects if provided
            if series_id:
                try:
                    feedback_data['series'] = AISeries.objects.get(id=series_id)
                except AISeries.DoesNotExist:
                    logger.warning(f"Series {series_id} not found")

            if episode_id:
                try:
                    feedback_data['episode'] = SeriesEpisode.objects.get(id=episode_id)
                except SeriesEpisode.DoesNotExist:
                    logger.warning(f"Episode {episode_id} not found")

            if user_id:
                try:
                    feedback_data['user'] = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    pass

            # Create feedback record
            feedback = PipelineStageFeedback.objects.create(**feedback_data)
            logger.info(f"Recorded {stage} feedback: {rating}/5")

            # Update aggregate performance tables
            self._update_performance_aggregates(stage, rating, context)

            return feedback

        except Exception as e:
            logger.error(f"Failed to record stage feedback: {e}")
            return None

    def _update_performance_aggregates(
        self,
        stage: str,
        rating: float,
        context: Dict[str, Any]
    ):
        """Update aggregate performance tables based on feedback."""
        try:
            from core.models_pipeline_feedback import (
                StylePresetPerformance,
                VoicePerformance,
                ResearchQueryPerformance
            )

            target_audience = context.get('target_audience', context.get('audience', '')).lower()
            series_type = context.get('series_type', '').lower()

            # Update style preset performance for image stage
            if stage == 'image' and 'style_preset' in context:
                StylePresetPerformance.record_usage(
                    style_preset=context['style_preset'],
                    target_audience=target_audience,
                    series_type=series_type,
                    rating=rating
                )
                logger.debug(f"Updated style performance for {context['style_preset']}")

            # Update voice performance for voice stage
            if stage == 'voice' and 'voice_id' in context:
                voice_id = context['voice_id']
                voice_name = context.get('voice_name', 'Unknown')
                voice_style = context.get('voice_style', '')

                obj, created = VoicePerformance.objects.get_or_create(
                    voice_id=voice_id,
                    series_type=series_type,
                    target_audience=target_audience,
                    defaults={
                        'voice_name': voice_name,
                        'voice_style': voice_style,
                        'total_uses': 0
                    }
                )

                obj.total_uses += 1
                obj.avg_rating = (obj.avg_rating * (obj.total_uses - 1) + Decimal(str(rating))) / obj.total_uses
                obj.confidence_score = min(Decimal('1.0'), Decimal(str(obj.total_uses / 100)))
                obj.save()
                logger.debug(f"Updated voice performance for {voice_name}")

            # Update research query performance
            if stage == 'research' and 'query_type' in context:
                query_type = context['query_type']
                keywords = context.get('keywords', [])

                obj, created = ResearchQueryPerformance.objects.get_or_create(
                    query_type=query_type,
                    series_type=series_type,
                    target_audience=target_audience,
                    defaults={'query_keywords': keywords, 'total_uses': 0}
                )

                obj.total_uses += 1
                obj.avg_content_rating = (obj.avg_content_rating * (obj.total_uses - 1) + Decimal(str(rating))) / obj.total_uses
                obj.save()
                logger.debug(f"Updated research query performance for {query_type}")

        except Exception as e:
            logger.error(f"Failed to update performance aggregates: {e}")

    # =========================================================================
    # ENGAGEMENT TRACKING
    # =========================================================================

    def record_engagement(
        self,
        platform: str,
        series_id: str = None,
        episode_id: str = None,
        metrics: Dict[str, Any] = None,
        outcome: str = 'pending',
        content_context: Dict[str, Any] = None
    ) -> Optional['ContentEngagement']:
        """
        Record engagement metrics for published content.

        Args:
            platform: Platform where content was published (youtube, tiktok, etc.)
            series_id: Optional series UUID
            episode_id: Optional episode UUID
            metrics: Dict with views, likes, shares, comments, etc.
            outcome: Content outcome (pending, delivered, approved, rejected, published, viral)
            content_context: Configuration used when creating content

        Returns:
            Created ContentEngagement instance
        """
        try:
            from core.models_pipeline_feedback import ContentEngagement
            from core.models_ai_series import AISeries, SeriesEpisode

            metrics = metrics or {}
            content_context = content_context or {}

            engagement_data = {
                'platform': platform,
                'views': metrics.get('views', 0),
                'likes': metrics.get('likes', 0),
                'shares': metrics.get('shares', 0),
                'comments': metrics.get('comments', 0),
                'saves': metrics.get('saves', 0),
                'avg_watch_time_seconds': metrics.get('watch_time', 0),
                'completion_rate': Decimal(str(metrics.get('completion_rate', 0.0))),
                'revenue': Decimal(str(metrics.get('revenue', 0.0))),
                'outcome': outcome,
                'content_context': content_context,
            }

            if series_id:
                try:
                    engagement_data['series'] = AISeries.objects.get(id=series_id)
                except AISeries.DoesNotExist:
                    pass

            if episode_id:
                try:
                    engagement_data['episode'] = SeriesEpisode.objects.get(id=episode_id)
                except SeriesEpisode.DoesNotExist:
                    pass

            if outcome in ['published', 'viral']:
                engagement_data['published_at'] = timezone.now()

            engagement = ContentEngagement.objects.create(**engagement_data)
            logger.info(f"Recorded engagement for {platform}: {metrics.get('views', 0)} views")

            # Update performance based on engagement
            self._update_performance_from_engagement(engagement)

            return engagement

        except Exception as e:
            logger.error(f"Failed to record engagement: {e}")
            return None

    def _update_performance_from_engagement(self, engagement):
        """Update performance aggregates based on engagement data."""
        try:
            from core.models_pipeline_feedback import StylePresetPerformance

            context = engagement.content_context
            if not context:
                return

            style_preset = context.get('style_preset')
            target_audience = context.get('target_audience', '').lower()
            series_type = context.get('series_type', '').lower()

            if style_preset:
                approved = engagement.outcome in ['approved', 'published', 'viral']
                engagement_score = engagement.engagement_score

                StylePresetPerformance.record_usage(
                    style_preset=style_preset,
                    target_audience=target_audience,
                    series_type=series_type,
                    approved=approved,
                    engagement=engagement_score
                )

                # Track viral content
                if engagement.outcome == 'viral':
                    try:
                        perf = StylePresetPerformance.objects.get(
                            style_preset=style_preset.lower(),
                            target_audience=target_audience,
                            series_type=series_type
                        )
                        perf.viral_content_count += 1
                        perf.save(update_fields=['viral_content_count', 'updated_at'])
                    except StylePresetPerformance.DoesNotExist:
                        pass

        except Exception as e:
            logger.error(f"Failed to update performance from engagement: {e}")

    # =========================================================================
    # RECOMMENDATIONS
    # =========================================================================

    def get_best_style_for_context(
        self,
        target_audience: str,
        series_type: str = '',
        fallback: str = 'pixar'
    ) -> Dict[str, Any]:
        """
        Get the best performing style preset for a given context.

        Args:
            target_audience: Target audience description
            series_type: Type of series (educational, entertainment, marketing)
            fallback: Default style if no data available

        Returns:
            Dict with recommended style and confidence
        """
        try:
            from core.models_pipeline_feedback import StylePresetPerformance

            best = StylePresetPerformance.get_best_style(
                target_audience=target_audience,
                series_type=series_type,
                min_uses=self.MIN_SAMPLE_SIZE
            )

            if best:
                return {
                    'style_preset': best.style_preset,
                    'avg_rating': float(best.avg_rating),
                    'approval_rate': float(best.approval_rate),
                    'confidence': float(best.confidence_score),
                    'sample_size': best.total_uses,
                    'source': 'learned'
                }

            return {
                'style_preset': fallback,
                'avg_rating': 0.0,
                'approval_rate': 0.0,
                'confidence': 0.0,
                'sample_size': 0,
                'source': 'default'
            }

        except Exception as e:
            logger.error(f"Failed to get best style: {e}")
            return {
                'style_preset': fallback,
                'source': 'error'
            }

    def get_best_voice_for_context(
        self,
        series_type: str = '',
        target_audience: str = '',
        fallback_voice_id: str = None
    ) -> Dict[str, Any]:
        """
        Get the best performing voice for a given context.

        Args:
            series_type: Type of series
            target_audience: Target audience
            fallback_voice_id: Default voice if no data available

        Returns:
            Dict with recommended voice and confidence
        """
        try:
            from core.models_pipeline_feedback import VoicePerformance

            best = VoicePerformance.get_best_voice(
                series_type=series_type,
                target_audience=target_audience,
                min_uses=self.MIN_SAMPLE_SIZE
            )

            if best:
                return {
                    'voice_id': best.voice_id,
                    'voice_name': best.voice_name,
                    'voice_style': best.voice_style,
                    'avg_rating': float(best.avg_rating),
                    'completion_rate': float(best.completion_rate),
                    'confidence': float(best.confidence_score),
                    'sample_size': best.total_uses,
                    'source': 'learned'
                }

            return {
                'voice_id': fallback_voice_id,
                'voice_name': 'Default',
                'confidence': 0.0,
                'sample_size': 0,
                'source': 'default'
            }

        except Exception as e:
            logger.error(f"Failed to get best voice: {e}")
            return {
                'voice_id': fallback_voice_id,
                'source': 'error'
            }

    def get_style_leaderboard(
        self,
        series_type: str = '',
        target_audience: str = '',
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get leaderboard of best-performing styles.

        Args:
            series_type: Filter by series type
            target_audience: Filter by audience
            limit: Max results

        Returns:
            List of style performance dicts
        """
        try:
            from core.models_pipeline_feedback import StylePresetPerformance

            queryset = StylePresetPerformance.objects.filter(
                total_uses__gte=1
            )

            if series_type:
                queryset = queryset.filter(series_type=series_type.lower())
            if target_audience:
                queryset = queryset.filter(target_audience__icontains=target_audience.lower())

            results = queryset.order_by('-avg_rating', '-total_uses')[:limit]

            return [
                {
                    'style_preset': r.style_preset,
                    'target_audience': r.target_audience,
                    'series_type': r.series_type,
                    'avg_rating': float(r.avg_rating),
                    'approval_rate': float(r.approval_rate),
                    'engagement_score': float(r.engagement_score),
                    'total_uses': r.total_uses,
                    'viral_count': r.viral_content_count,
                    'confidence': float(r.confidence_score)
                }
                for r in results
            ]

        except Exception as e:
            logger.error(f"Failed to get style leaderboard: {e}")
            return []

    # =========================================================================
    # INSIGHT GENERATION
    # =========================================================================

    def generate_insights(self) -> List['PipelineLearningInsight']:
        """
        Analyze feedback data and generate learning insights.

        Creates insights like:
        - "Pixar style performs 23% better than cartoon for kids educational content"
        - "Rachel voice has 40% higher completion rate for marketing content"

        Returns:
            List of generated PipelineLearningInsight instances
        """
        try:
            pass

            insights = []

            # Generate style insights for image stage
            style_insights = self._generate_style_insights()
            insights.extend(style_insights)

            # Generate voice insights for voice stage
            voice_insights = self._generate_voice_insights()
            insights.extend(voice_insights)

            logger.info(f"Generated {len(insights)} learning insights")
            return insights

        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return []

    def _generate_style_insights(self) -> List['PipelineLearningInsight']:
        """Generate insights about style preset performance."""
        try:
            from core.models_pipeline_feedback import (
                PipelineLearningInsight,
                StylePresetPerformance,
                PipelineStage
            )

            insights = []

            # Find top performers per audience type
            audiences = StylePresetPerformance.objects.values_list(
                'target_audience', flat=True
            ).distinct()

            for audience in audiences:
                if not audience:
                    continue

                # Get top style for this audience
                top = StylePresetPerformance.objects.filter(
                    target_audience=audience,
                    total_uses__gte=self.MIN_SAMPLE_SIZE
                ).order_by('-avg_rating').first()

                if not top:
                    continue

                # Get average for comparison
                avg_rating = StylePresetPerformance.objects.filter(
                    target_audience=audience,
                    total_uses__gte=1
                ).aggregate(avg=Avg('avg_rating'))['avg'] or 0

                if float(top.avg_rating) <= float(avg_rating):
                    continue

                improvement = ((float(top.avg_rating) - float(avg_rating)) / float(avg_rating) * 100) if avg_rating else 0

                insight, created = PipelineLearningInsight.objects.update_or_create(
                    stage=PipelineStage.IMAGE,
                    insight_type='best_style',
                    applicable_to={'target_audience': audience},
                    defaults={
                        'insight_summary': f"{top.style_preset.title()} style performs {improvement:.0f}% better for {audience} content",
                        'insight_data': {
                            'recommended_style': top.style_preset,
                            'avg_rating': float(top.avg_rating),
                            'baseline_rating': float(avg_rating),
                            'improvement_pct': improvement
                        },
                        'confidence': top.confidence_score,
                        'sample_size': top.total_uses,
                        'estimated_impact': Decimal(str(improvement)),
                        'is_active': True,
                        'expires_at': timezone.now() + timedelta(days=self.INSIGHT_REFRESH_DAYS)
                    }
                )

                insights.append(insight)

            return insights

        except Exception as e:
            logger.error(f"Failed to generate style insights: {e}")
            return []

    def _generate_voice_insights(self) -> List['PipelineLearningInsight']:
        """Generate insights about voice performance."""
        try:
            from core.models_pipeline_feedback import (
                PipelineLearningInsight,
                VoicePerformance,
                PipelineStage
            )

            insights = []

            # Find top voices per series type
            series_types = VoicePerformance.objects.values_list(
                'series_type', flat=True
            ).distinct()

            for series_type in series_types:
                if not series_type:
                    continue

                top = VoicePerformance.objects.filter(
                    series_type=series_type,
                    total_uses__gte=self.MIN_SAMPLE_SIZE
                ).order_by('-avg_rating').first()

                if not top:
                    continue

                insight, created = PipelineLearningInsight.objects.update_or_create(
                    stage=PipelineStage.VOICE,
                    insight_type='best_voice',
                    applicable_to={'series_type': series_type},
                    defaults={
                        'insight_summary': f"{top.voice_name} voice performs best for {series_type} content ({float(top.avg_rating):.1f}/5 rating)",
                        'insight_data': {
                            'recommended_voice_id': top.voice_id,
                            'recommended_voice_name': top.voice_name,
                            'avg_rating': float(top.avg_rating),
                            'completion_rate': float(top.completion_rate)
                        },
                        'confidence': top.confidence_score,
                        'sample_size': top.total_uses,
                        'is_active': True,
                        'expires_at': timezone.now() + timedelta(days=self.INSIGHT_REFRESH_DAYS)
                    }
                )

                insights.append(insight)

            return insights

        except Exception as e:
            logger.error(f"Failed to generate voice insights: {e}")
            return []

    def get_active_insights(
        self,
        stage: str = None,
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Get active learning insights.

        Args:
            stage: Filter by pipeline stage
            context: Filter by applicable context

        Returns:
            List of insight dicts
        """
        try:
            from core.models_pipeline_feedback import PipelineLearningInsight

            queryset = PipelineLearningInsight.objects.filter(is_active=True)

            if stage:
                queryset = queryset.filter(stage=stage)

            # Filter by context (basic containment check)
            if context:
                for key, value in context.items():
                    queryset = queryset.filter(
                        applicable_to__contains={key: value}
                    )

            return [
                {
                    'id': str(insight.id),
                    'stage': insight.stage,
                    'type': insight.insight_type,
                    'summary': insight.insight_summary,
                    'data': insight.insight_data,
                    'confidence': float(insight.confidence),
                    'sample_size': insight.sample_size,
                    'estimated_impact': float(insight.estimated_impact),
                    'times_applied': insight.times_applied
                }
                for insight in queryset.order_by('-confidence', '-sample_size')
            ]

        except Exception as e:
            logger.error(f"Failed to get active insights: {e}")
            return []

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def get_learning_statistics(self) -> Dict[str, Any]:
        """
        Get overall learning system statistics.

        Returns:
            Dict with counts, averages, and trends
        """
        try:
            from core.models_pipeline_feedback import (
                PipelineStageFeedback,
                StylePresetPerformance,
                VoicePerformance,
                ContentEngagement,
                PipelineLearningInsight
            )

            return {
                'feedback': {
                    'total_count': PipelineStageFeedback.objects.count(),
                    'by_stage': dict(
                        PipelineStageFeedback.objects.values('stage')
                        .annotate(count=Count('id'))
                        .values_list('stage', 'count')
                    ),
                    'avg_rating': float(
                        PipelineStageFeedback.objects.aggregate(avg=Avg('rating'))['avg'] or 0
                    )
                },
                'styles': {
                    'tracked_count': StylePresetPerformance.objects.count(),
                    'top_style': (
                        StylePresetPerformance.objects.order_by('-avg_rating').first()
                    ) and StylePresetPerformance.objects.order_by('-avg_rating').first().style_preset or 'N/A',
                    'total_uses': sum(
                        s.total_uses for s in StylePresetPerformance.objects.all()
                    )
                },
                'voices': {
                    'tracked_count': VoicePerformance.objects.count(),
                    'total_uses': sum(
                        v.total_uses for v in VoicePerformance.objects.all()
                    )
                },
                'engagement': {
                    'total_tracked': ContentEngagement.objects.count(),
                    'total_views': sum(
                        e.views for e in ContentEngagement.objects.all()
                    ),
                    'viral_count': ContentEngagement.objects.filter(outcome='viral').count()
                },
                'insights': {
                    'active_count': PipelineLearningInsight.objects.filter(is_active=True).count(),
                    'total_applied': sum(
                        i.times_applied for i in PipelineLearningInsight.objects.all()
                    )
                }
            }

        except Exception as e:
            logger.error(f"Failed to get learning statistics: {e}")
            return {}

    # =========================================================================
    # SESSION 452: COLLECTIVE INTELLIGENCE BRIDGE
    # =========================================================================

    def share_insights_to_collective(self) -> int:
        """
        Bridge pipeline learning insights to the collective intelligence system.

        Takes active pipeline insights and shares them as knowledge items
        that agents can access and learn from.

        Returns:
            Number of insights shared
        """
        try:
            from core.models_pipeline_feedback import PipelineLearningInsight
            from core.services.agent_collaboration_hub import get_collaboration_hub

            hub = get_collaboration_hub()
            insights = PipelineLearningInsight.objects.filter(is_active=True)
            shared_count = 0

            for insight in insights:
                # Convert pipeline insight to knowledge item
                knowledge_content = {
                    'insight_type': 'pipeline_learning',
                    'stage': insight.stage,
                    'finding': insight.insight_text,
                    'improvement': insight.improvement_percentage,
                    'context': {
                        'target_audience': insight.target_audience,
                        'series_type': insight.series_type,
                        'style_preset': insight.style_preset,
                        'voice_id': insight.voice_id,
                    },
                    'sample_size': insight.sample_size,
                    'times_applied': insight.times_applied,
                    'created_at': insight.created_at.isoformat() if insight.created_at else None,
                }

                # Determine relevant tags based on insight content
                tags = ['pipeline_learning', insight.stage]
                if insight.target_audience:
                    tags.append(f"audience:{insight.target_audience}")
                if insight.series_type:
                    tags.append(f"type:{insight.series_type}")
                if insight.style_preset:
                    tags.append(f"style:{insight.style_preset}")

                # Share to collective intelligence
                hub.share_knowledge(
                    agent_name='PipelineLearningService',
                    category='content_optimization',
                    title=f"Pipeline Insight: {insight.insight_text[:100]}",
                    content=knowledge_content,
                    confidence=min(1.0, 0.5 + (insight.sample_size / 20)),  # Higher sample = higher confidence
                    tags=tags
                )

                shared_count += 1
                logger.debug(f"Shared pipeline insight to collective: {insight.insight_text[:50]}...")

            logger.info(f"Shared {shared_count} pipeline insights to collective intelligence")
            return shared_count

        except Exception as e:
            logger.error(f"Failed to share insights to collective: {e}")
            return 0

    def sync_collective_knowledge_to_recommendations(self) -> Dict[str, Any]:
        """
        Pull relevant knowledge from collective intelligence to enhance recommendations.

        Checks if other agents have shared content optimization knowledge
        that could improve pipeline recommendations.

        Returns:
            Dict with synced knowledge summary
        """
        try:
            from core.services.agent_collaboration_hub import get_collaboration_hub

            hub = get_collaboration_hub()
            synced = {'style_hints': [], 'voice_hints': [], 'general_tips': []}

            # Query for content optimization knowledge
            knowledge_items = hub.query_knowledge(
                category='content_optimization',
                tags=['style', 'voice', 'audience'],
                min_confidence=0.6,
                limit=20
            )

            for item in knowledge_items:
                content = item.content if hasattr(item, 'content') else item.get('content', {})

                # Extract style-related knowledge
                if 'style' in str(content).lower():
                    synced['style_hints'].append({
                        'source': item.source_agent if hasattr(item, 'source_agent') else 'unknown',
                        'hint': str(content)[:200],
                        'confidence': item.confidence if hasattr(item, 'confidence') else 0.7
                    })

                # Extract voice-related knowledge
                if 'voice' in str(content).lower():
                    synced['voice_hints'].append({
                        'source': item.source_agent if hasattr(item, 'source_agent') else 'unknown',
                        'hint': str(content)[:200],
                        'confidence': item.confidence if hasattr(item, 'confidence') else 0.7
                    })

            logger.info(f"Synced {len(synced['style_hints'])} style hints, {len(synced['voice_hints'])} voice hints from collective")
            return synced

        except Exception as e:
            logger.error(f"Failed to sync from collective: {e}")
            return {'style_hints': [], 'voice_hints': [], 'general_tips': [], 'error': str(e)}


# Singleton instance for easy access
_learning_service = None

def get_pipeline_learning_service() -> PipelineLearningService:
    """Get the singleton PipelineLearningService instance."""
    global _learning_service
    if _learning_service is None:
        _learning_service = PipelineLearningService()
    return _learning_service


# =============================================================================
# Session 452: A/B Testing Integration for Series Generation
# =============================================================================

def get_ab_test_style_for_series(
    user_id: int,
    series_type: str,
    target_audience: str = None
) -> Optional[Dict[str, Any]]:
    """
    Check for an active style A/B test and return a variant if enrolled.

    This function is called during series creation to potentially override
    the GPT-selected style with an A/B test variant.

    Args:
        user_id: User creating the series
        series_type: educational, entertainment, marketing
        target_audience: Optional audience description

    Returns:
        Dict with 'style_preset' and 'experiment_id' if enrolled, None otherwise
    """
    try:
        from core.services.ab_testing import get_ab_testing_service

        service = get_ab_testing_service()

        # Get active experiments for style domain
        experiments = service.get_active_experiments(domain='content_style')

        if not experiments:
            return None

        # Check each experiment (prefer most specific match)
        for exp in experiments:
            # Check if experiment matches this series type
            exp_config = exp.get('config', {})
            exp_series_types = exp_config.get('series_types', [])

            if exp_series_types and series_type not in exp_series_types:
                continue  # Experiment doesn't apply to this series type

            # Get variant for user
            variant = service.get_variant_for_user(
                experiment_id=exp['id'],
                user_id=user_id
            )

            if variant and variant.config:
                style_preset = variant.config.get('style_preset')
                if style_preset:
                    # Mark exposure
                    service.mark_exposure(
                        experiment_id=exp['id'],
                        user_id=user_id
                    )

                    logger.info(
                        f"[SESSION 452] A/B test assigning style '{style_preset}' "
                        f"(variant: {variant.variant_name}, experiment: {variant.experiment_name})"
                    )

                    return {
                        'style_preset': style_preset,
                        'experiment_id': exp['id'],
                        'variant_id': variant.variant_id,
                        'variant_name': variant.variant_name,
                        'is_control': variant.is_control
                    }

        return None

    except Exception as e:
        logger.error(f"[SESSION 452] A/B test style lookup failed: {e}")
        return None


def track_ab_test_series_feedback(
    experiment_id: str,
    user_id: int,
    series_id: str,
    feedback_type: str,
    rating: float = None,
    metadata: Dict = None
):
    """
    Track A/B test feedback when a series receives ratings/engagement.

    Called from the Discord reaction feedback or explicit ratings.

    Args:
        experiment_id: The A/B experiment
        user_id: User who reacted
        series_id: The series that received feedback
        feedback_type: engagement, completion, rating, share
        rating: Optional rating value (1-5)
        metadata: Additional data
    """
    try:
        from core.services.ab_testing import get_ab_testing_service

        service = get_ab_testing_service()

        # Determine conversion value based on feedback type
        value = 1.0
        if feedback_type == 'rating' and rating:
            value = rating / 5.0  # Normalize to 0-1
        elif feedback_type == 'completion':
            value = 1.0  # Series was completed
        elif feedback_type == 'share':
            value = 2.0  # Higher value for shares

        conversion_meta = {
            'series_id': series_id,
            'feedback_type': feedback_type,
            'rating': rating,
            **(metadata or {})
        }

        service.track_conversion(
            experiment_id=experiment_id,
            conversion_type=feedback_type,
            user_id=user_id,
            value=value,
            metadata=conversion_meta
        )

        logger.info(
            f"[SESSION 452] A/B test conversion tracked: "
            f"{feedback_type} (value={value}) for series {series_id[:8]}..."
        )

    except Exception as e:
        logger.error(f"[SESSION 452] Failed to track A/B conversion: {e}")


def create_style_ab_test(
    name: str,
    styles: List[str],
    series_types: List[str] = None,
    traffic_percentage: int = 50,
    created_by_id: int = None
) -> Dict[str, Any]:
    """
    Create an A/B test for comparing different style presets.

    Example:
        create_style_ab_test(
            name="Pixar vs Disney for Kids",
            styles=["pixar", "disney", "dreamworks"],
            series_types=["educational", "entertainment"],
            traffic_percentage=30
        )

    Args:
        name: Experiment name
        styles: List of style presets to test (first is control)
        series_types: Limit to these series types (or None for all)
        traffic_percentage: % of users to include in test
        created_by_id: User creating the test

    Returns:
        Created experiment info
    """
    try:
        from core.services.ab_testing import get_ab_testing_service

        service = get_ab_testing_service()

        # Build variants from styles
        variants = []
        weight = 100 // len(styles)

        for i, style in enumerate(styles):
            variants.append({
                'name': f'{style}_variant' if i > 0 else 'control',
                'is_control': (i == 0),
                'weight': weight if i < len(styles) - 1 else (100 - weight * (len(styles) - 1)),
                'config': {
                    'style_preset': style
                }
            })

        experiment = service.create_experiment(
            name=name,
            description=f"Testing style presets: {', '.join(styles)} for content series",
            experiment_type='content',
            domain='content_style',
            traffic_percentage=traffic_percentage,
            variants=variants,
            config={
                'series_types': series_types or [],
                'styles_tested': styles,
            },
            created_by_id=created_by_id
        )

        # Auto-start the experiment
        if experiment.get('id'):
            service.start_experiment(experiment['id'])
            experiment['status'] = 'running'

        logger.info(f"[SESSION 452] Created style A/B test: {name} with {len(styles)} variants")
        return experiment

    except Exception as e:
        logger.error(f"[SESSION 452] Failed to create style A/B test: {e}")
        raise
