"""
Blog Performance Context Builder - Session 886
===============================================

Builds performance context to inject into ContentWriterAgent prompts,
closing the feedback loop so the agent learns from past content performance.

This service queries:
1. SelfBlog - Recent quality scores, topics, performance
2. ContentEngagement - Views, completion rates, engagement metrics (when available)
3. PipelineLearningInsight - Active learning insights to apply

The context is injected into the agent's system prompt WITHOUT modifying
the base prompt (following the layered architecture principle).

Architecture:
    Base Prompt (stable)
    + Performance Context (dynamic) <-- THIS SERVICE
    + Learning Rules (dynamic)
    + Human Feedback (dynamic)

Usage:
    from core.services.blog_performance_context import get_blog_performance_context

    context = get_blog_performance_context(limit=10)
    # Returns formatted string ready for prompt injection
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Q, F
from django.db.models.functions import TruncDate
from django.utils import timezone

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Aggregated performance metrics from recent blogs."""
    avg_quality_score: float
    avg_novelty_score: float
    avg_structure_score: float
    total_blogs: int
    published_count: int
    needs_enhancement_count: int
    top_performing_topics: List[Dict[str, Any]]
    weak_performing_topics: List[Dict[str, Any]]
    common_weaknesses: List[str]
    common_strengths: List[str]


@dataclass
class LearningRule:
    """An actionable learning rule derived from insights."""
    rule: str
    impact: str
    confidence: float
    source: str


class BlogPerformanceContextBuilder:
    """
    Builds performance context for ContentWriterAgent.

    Session 886: Implements Phase 1 of the feedback loop system.

    Key Responsibilities:
    1. Aggregate quality metrics from recent SelfBlog records
    2. Identify patterns (what works, what doesn't)
    3. Extract active learning insights
    4. Format into prompt-injectable context
    """

    def __init__(self):
        self._cache = {}
        self._cache_ttl = timedelta(minutes=15)  # Cache for 15 mins
        self._last_cache_time = None

    def build_context(
        self,
        limit: int = 10,
        include_learning_rules: bool = True,
        include_engagement: bool = True,
        content_type: Optional[str] = None
    ) -> str:
        """
        Build the complete performance context string for prompt injection.

        Args:
            limit: Number of recent blogs to analyze
            include_learning_rules: Whether to include PipelineLearningInsight rules
            include_engagement: Whether to include ContentEngagement metrics
            content_type: Filter by content type ('public', 'internal', 'strategic')

        Returns:
            Formatted string ready for system prompt injection
        """
        try:
            # Get performance metrics
            metrics = self._get_performance_metrics(limit, content_type)

            # Get learning rules
            learning_rules = []
            if include_learning_rules:
                learning_rules = self._get_learning_rules()

            # Get engagement data (if available)
            engagement_summary = None
            if include_engagement:
                engagement_summary = self._get_engagement_summary()

            # Build the context string
            context = self._format_context(
                metrics=metrics,
                learning_rules=learning_rules,
                engagement_summary=engagement_summary
            )

            logger.info(f"📊 Session 886: Built blog performance context ({len(context)} chars)")
            return context

        except Exception as e:
            logger.warning(f"Failed to build blog performance context: {e}")
            return self._get_fallback_context()

    def _get_performance_metrics(
        self,
        limit: int,
        content_type: Optional[str] = None
    ) -> PerformanceMetrics:
        """Query SelfBlog for performance metrics."""
        from core.models_unified_system import SelfBlog

        # Base queryset - recent blogs
        queryset = SelfBlog.objects.all().order_by('-created_at')

        if content_type:
            queryset = queryset.filter(content_type=content_type)

        recent_blogs = queryset[:limit]

        # Calculate averages (only for blogs with scores)
        scored_blogs = queryset.filter(
            quality_score__isnull=False
        )[:limit]

        aggregates = scored_blogs.aggregate(
            avg_quality=Avg('quality_score'),
            avg_novelty=Avg('novelty_score'),
            avg_structure=Avg('structure_score'),
        )

        # Count by status
        status_counts = queryset[:limit].values('status').annotate(
            count=Count('id')
        )
        status_map = {s['status']: s['count'] for s in status_counts}

        # Identify top performing topics (highest quality scores)
        top_topics = self._analyze_topics_by_quality(queryset, 'top', limit=3)
        weak_topics = self._analyze_topics_by_quality(queryset, 'weak', limit=3)

        # Identify common patterns
        strengths, weaknesses = self._analyze_content_patterns(recent_blogs)

        return PerformanceMetrics(
            avg_quality_score=float(aggregates['avg_quality'] or 0),
            avg_novelty_score=float(aggregates['avg_novelty'] or 0),
            avg_structure_score=float(aggregates['avg_structure'] or 0),
            total_blogs=recent_blogs.count(),
            published_count=status_map.get('published', 0),
            needs_enhancement_count=status_map.get('needs_enhancement', 0),
            top_performing_topics=top_topics,
            weak_performing_topics=weak_topics,
            common_strengths=strengths,
            common_weaknesses=weaknesses,
        )

    def _analyze_topics_by_quality(
        self,
        queryset,
        mode: str = 'top',
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Analyze which topics/categories perform best or worst."""
        from core.models_unified_system import SelfBlog

        # Group by category and calculate avg quality
        category_stats = queryset.filter(
            quality_score__isnull=False
        ).values('category').annotate(
            avg_quality=Avg('quality_score'),
            count=Count('id')
        ).filter(count__gte=2)  # Only categories with 2+ samples

        if mode == 'top':
            category_stats = category_stats.order_by('-avg_quality')
        else:
            category_stats = category_stats.order_by('avg_quality')

        results = []
        for stat in category_stats[:limit]:
            # Get a sample title from this category
            sample = queryset.filter(
                category=stat['category'],
                quality_score__isnull=False
            ).first()

            results.append({
                'category': stat['category'],
                'avg_quality': round(float(stat['avg_quality']), 2),
                'sample_count': stat['count'],
                'sample_title': sample.title[:50] if sample else 'N/A',
            })

        return results

    def _analyze_content_patterns(
        self,
        recent_blogs
    ) -> tuple:
        """Analyze content for common strengths and weaknesses."""
        strengths = []
        weaknesses = []

        # Track score distributions
        high_structure = 0
        low_structure = 0
        high_novelty = 0
        low_novelty = 0
        has_sources = 0
        no_sources = 0

        for blog in recent_blogs:
            # Structure analysis
            if blog.structure_score and blog.structure_score >= 0.7:
                high_structure += 1
            elif blog.structure_score and blog.structure_score < 0.5:
                low_structure += 1

            # Novelty analysis
            if blog.novelty_score and blog.novelty_score >= 0.7:
                high_novelty += 1
            elif blog.novelty_score and blog.novelty_score < 0.5:
                low_novelty += 1

            # Check for sources in content
            sections = blog.sections or []
            content_text = str(sections).lower()
            if 'source' in content_text or 'according to' in content_text:
                has_sources += 1
            else:
                no_sources += 1

        total = recent_blogs.count() or 1

        # Determine strengths
        if high_structure / total >= 0.6:
            strengths.append("Clear structure and organization")
        if high_novelty / total >= 0.6:
            strengths.append("Fresh, unique perspectives")
        if has_sources / total >= 0.5:
            strengths.append("Good source attribution")

        # Determine weaknesses
        if low_structure / total >= 0.3:
            weaknesses.append("Weak structure (needs better headers/flow)")
        if low_novelty / total >= 0.3:
            weaknesses.append("Content feels generic or repetitive")
        if no_sources / total >= 0.5:
            weaknesses.append("Lacks source citations and evidence")

        # Add defaults if empty
        if not strengths:
            strengths = ["Consistent output quality"]
        if not weaknesses:
            weaknesses = ["No major issues identified"]

        return strengths, weaknesses

    def _get_learning_rules(self) -> List[LearningRule]:
        """Extract active learning insights and convert to rules."""
        try:
            from core.models_pipeline_feedback import PipelineLearningInsight

            # Get active insights relevant to content/writing
            insights = PipelineLearningInsight.objects.filter(
                is_active=True,
                confidence__gte=Decimal('0.5'),  # Only confident insights
            ).order_by('-confidence', '-estimated_impact')[:10]

            rules = []
            for insight in insights:
                # Convert insight to actionable rule
                rule = self._insight_to_rule(insight)
                if rule:
                    rules.append(rule)

            return rules[:5]  # Top 5 rules max

        except Exception as e:
            logger.warning(f"Could not fetch learning insights: {e}")
            return []

    def _insight_to_rule(self, insight) -> Optional[LearningRule]:
        """Convert a PipelineLearningInsight to an actionable rule."""
        try:
            summary = insight.insight_summary
            impact = f"+{insight.estimated_impact}%" if insight.estimated_impact else "positive"

            # Make the insight actionable
            if 'performs' in summary.lower() or 'better' in summary.lower():
                rule_text = f"PREFER: {summary}"
            elif 'lower' in summary.lower() or 'worse' in summary.lower():
                rule_text = f"AVOID: {summary}"
            else:
                rule_text = summary

            return LearningRule(
                rule=rule_text,
                impact=str(impact),
                confidence=float(insight.confidence),
                source=insight.insight_type
            )
        except Exception as _e:
            logger.warning(
                "blog_performance_context._insight_to_rule: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return None

    def _get_engagement_summary(self) -> Optional[Dict[str, Any]]:
        """Get engagement metrics summary if available."""
        try:
            from core.models_pipeline_feedback import ContentEngagement

            # Get recent engagement data
            cutoff = timezone.now() - timedelta(days=30)
            recent_engagement = ContentEngagement.objects.filter(
                created_at__gte=cutoff,
                views__gt=0
            )

            if not recent_engagement.exists():
                return None

            aggregates = recent_engagement.aggregate(
                avg_views=Avg('views'),
                avg_completion=Avg('completion_rate'),
                avg_likes=Avg('likes'),
                avg_shares=Avg('shares'),
            )

            return {
                'avg_views': int(aggregates['avg_views'] or 0),
                'avg_completion_rate': float(aggregates['avg_completion'] or 0),
                'avg_likes': int(aggregates['avg_likes'] or 0),
                'avg_shares': int(aggregates['avg_shares'] or 0),
                'sample_size': recent_engagement.count(),
            }

        except Exception as e:
            logger.debug(f"Could not fetch engagement data: {e}")
            return None

    def _format_context(
        self,
        metrics: PerformanceMetrics,
        learning_rules: List[LearningRule],
        engagement_summary: Optional[Dict[str, Any]]
    ) -> str:
        """Format all data into a prompt-injectable context string."""
        parts = []

        # Header
        parts.append("## PERFORMANCE CONTEXT (Session 886 - Feedback Loop)")
        parts.append("Use this data to improve your writing based on what has worked before.\n")

        # Quality metrics summary
        parts.append("### Recent Blog Performance (Last 10)")
        parts.append(f"- Avg Quality Score: {metrics.avg_quality_score:.2f}/1.0")
        parts.append(f"- Avg Structure Score: {metrics.avg_structure_score:.2f}/1.0")
        parts.append(f"- Avg Novelty Score: {metrics.avg_novelty_score:.2f}/1.0")
        parts.append(f"- Published: {metrics.published_count} | Needs Enhancement: {metrics.needs_enhancement_count}")
        parts.append("")

        # Top performing topics
        if metrics.top_performing_topics:
            parts.append("### Highest Performing Topics")
            for topic in metrics.top_performing_topics:
                parts.append(f"- {topic['category'].title()}: {topic['avg_quality']:.2f} avg quality ({topic['sample_count']} samples)")
            parts.append("")

        # Weak performing topics
        if metrics.weak_performing_topics:
            parts.append("### Topics Needing Improvement")
            for topic in metrics.weak_performing_topics:
                parts.append(f"- {topic['category'].title()}: {topic['avg_quality']:.2f} avg quality")
            parts.append("")

        # Strengths and weaknesses
        parts.append("### Your Strengths")
        for strength in metrics.common_strengths:
            parts.append(f"- {strength}")
        parts.append("")

        parts.append("### Areas to Improve")
        for weakness in metrics.common_weaknesses:
            parts.append(f"- {weakness}")
        parts.append("")

        # Learning rules (if any)
        if learning_rules:
            parts.append("### Active Learning Rules (Apply These)")
            for rule in learning_rules:
                parts.append(f"- {rule.rule} ({rule.impact} impact, {rule.confidence:.0%} confidence)")
            parts.append("")

        # Engagement data (if available)
        if engagement_summary:
            parts.append("### Engagement Metrics (Last 30 Days)")
            parts.append(f"- Avg Views: {engagement_summary['avg_views']:,}")
            parts.append(f"- Avg Completion Rate: {engagement_summary['avg_completion_rate']:.1f}%")
            parts.append(f"- Avg Likes: {engagement_summary['avg_likes']}")
            parts.append(f"- Avg Shares: {engagement_summary['avg_shares']}")
            parts.append(f"- Sample Size: {engagement_summary['sample_size']} pieces of content")
            parts.append("")

        # Closing guidance
        parts.append("### How to Use This Data")
        parts.append("- Emulate patterns from high-performing topics")
        parts.append("- Address the identified weaknesses in your writing")
        parts.append("- Follow the active learning rules")
        parts.append("- Aim for quality score >= 0.8")

        return "\n".join(parts)

    def _get_fallback_context(self) -> str:
        """Return minimal context if data fetching fails."""
        return """## PERFORMANCE CONTEXT (Session 886)
Note: Performance data temporarily unavailable. Using defaults.

### General Guidelines
- Aim for clear structure with distinct sections
- Include concrete examples and data
- Cite sources where possible
- Write for the target audience
- Quality score target: >= 0.8"""


# Singleton instance
_builder_instance = None


def get_blog_performance_context(
    limit: int = 10,
    include_learning_rules: bool = True,
    include_engagement: bool = True,
    content_type: Optional[str] = None
) -> str:
    """
    Get the blog performance context string for prompt injection.

    This is the main entry point for ContentWriterAgent.

    Args:
        limit: Number of recent blogs to analyze
        include_learning_rules: Whether to include learning insights
        include_engagement: Whether to include engagement metrics
        content_type: Filter by content type

    Returns:
        Formatted context string for system prompt injection
    """
    global _builder_instance

    if _builder_instance is None:
        _builder_instance = BlogPerformanceContextBuilder()

    return _builder_instance.build_context(
        limit=limit,
        include_learning_rules=include_learning_rules,
        include_engagement=include_engagement,
        content_type=content_type
    )


def get_performance_metrics_dict(limit: int = 10) -> Dict[str, Any]:
    """
    Get performance metrics as a dictionary (for API/debugging).

    Returns structured data instead of formatted string.
    """
    global _builder_instance

    if _builder_instance is None:
        _builder_instance = BlogPerformanceContextBuilder()

    try:
        metrics = _builder_instance._get_performance_metrics(limit, None)
        rules = _builder_instance._get_learning_rules()
        engagement = _builder_instance._get_engagement_summary()

        return {
            'metrics': {
                'avg_quality_score': metrics.avg_quality_score,
                'avg_novelty_score': metrics.avg_novelty_score,
                'avg_structure_score': metrics.avg_structure_score,
                'total_blogs': metrics.total_blogs,
                'published_count': metrics.published_count,
                'needs_enhancement_count': metrics.needs_enhancement_count,
                'strengths': metrics.common_strengths,
                'weaknesses': metrics.common_weaknesses,
            },
            'top_topics': metrics.top_performing_topics,
            'weak_topics': metrics.weak_performing_topics,
            'learning_rules': [
                {'rule': r.rule, 'impact': r.impact, 'confidence': r.confidence}
                for r in rules
            ],
            'engagement': engagement,
        }
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        return {'error': str(e)}
