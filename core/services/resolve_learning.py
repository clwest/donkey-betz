"""
Resolve Learning Service - Session 478

DaVinci Resolve Full Utilization

This service manages the learning loop for color grade selection:
1. Tracks user ratings per color grade
2. Monitors usage patterns (which grades are actually used)
3. Correlates revenue with color grades
4. Improves trend-to-grade matching over time

The learning loop makes the system smarter:
- High-rated grades get prioritized for similar trends
- Unused grades get deprioritized
- Revenue-generating grades get boosted
"""

import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import timedelta

from django.utils import timezone
from django.db.models import Avg, Sum

logger = logging.getLogger(__name__)


class ResolveLearningService:
    """
    Learning service for DaVinci Resolve color grade optimization.

    This service:
    1. Records user feedback on rendered videos
    2. Tracks which color grades perform best for different trend patterns
    3. Provides intelligent grade recommendations based on historical data
    4. Improves over time as more data is collected
    """

    def __init__(self):
        self._grade_cache = {}
        self._cache_timestamp = None
        self._cache_duration = timedelta(hours=1)

    def record_user_feedback(
        self,
        job_id: str,
        rating: int,
        feedback: Optional[str] = None,
        was_used: bool = False,
        revenue_generated: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Record user feedback for a completed render job.

        Args:
            job_id: ResolveRenderJob UUID
            rating: User rating 1-5
            feedback: Optional text feedback
            was_used: Whether the rendered video was actually used
            revenue_generated: Revenue generated from using the video

        Returns:
            Dict with recording status
        """
        logger.info(f"🎬 [RESOLVE LEARNING] Recording feedback for {job_id}")

        try:
            from core.models_unified_system import ResolveRenderJob

            job = ResolveRenderJob.objects.get(id=job_id)

            # Validate rating
            rating = max(1, min(5, rating))

            # Update job with feedback
            job.user_rating = rating
            job.was_used = was_used
            if revenue_generated:
                job.revenue_generated = revenue_generated
            job.save()

            # Invalidate cache
            self._invalidate_cache()

            logger.info(
                f"🎬 [RESOLVE LEARNING] Recorded: "
                f"job={job_id}, grade={job.color_grade}, "
                f"rating={rating}, used={was_used}"
            )

            return {
                'success': True,
                'job_id': job_id,
                'color_grade': job.color_grade,
                'rating': rating,
                'was_used': was_used,
            }

        except Exception as e:
            logger.error(f"🎬 [RESOLVE LEARNING] Record feedback failed: {e}")
            return {'success': False, 'error': str(e)}

    def get_best_grade_for_trends(
        self,
        spider_trends: Dict[str, Any],
        fallback_to_matching: bool = True
    ) -> str:
        """
        Get the best performing color grade for given spider trends.

        This combines:
        1. Historical performance data (ratings, usage, revenue)
        2. Trend matching (if no historical data)

        Args:
            spider_trends: Spider trend data with trending_styles and trending_colors
            fallback_to_matching: If True, fall back to trend matching if no data

        Returns:
            Best color grade preset name
        """
        logger.info("🎬 [RESOLVE LEARNING] Finding best grade for trends...")

        try:
            # Try to get cached or fresh performance data
            grade_performance = self._get_grade_performance()

            if grade_performance:
                # We have historical data - use it!

                # Extract trending keywords for matching
                trend_keywords = self._extract_trend_keywords(spider_trends)

                # Score grades based on:
                # 1. Historical performance (rating * 2 + usage + revenue)
                # 2. Trend relevance
                grade_scores = {}

                from resolve_node.color_grades import get_preset

                for grade_name, perf in grade_performance.items():
                    # Base score from performance
                    base_score = (
                        (perf.get('avg_rating', 3) * 2) +
                        (perf.get('usage_rate', 0.5) * 3) +
                        (min(perf.get('revenue_rate', 0), 1) * 2)
                    )

                    # Trend relevance bonus
                    preset = get_preset(grade_name)
                    if preset:
                        relevance = self._calculate_trend_relevance(
                            preset, trend_keywords
                        )
                        trend_bonus = relevance * 2
                    else:
                        trend_bonus = 0

                    grade_scores[grade_name] = base_score + trend_bonus

                # Return highest scoring grade
                if grade_scores:
                    best_grade = max(grade_scores, key=grade_scores.get)
                    logger.info(
                        f"🎬 [RESOLVE LEARNING] Selected '{best_grade}' "
                        f"(score: {grade_scores[best_grade]:.2f})"
                    )
                    return best_grade

            # No historical data - fall back to trend matching
            if fallback_to_matching:
                from resolve_node.color_grades import match_grade_to_trends
                matched = match_grade_to_trends(spider_trends)
                logger.info(f"🎬 [RESOLVE LEARNING] Fallback to matching: '{matched}'")
                return matched

            # Ultimate fallback
            return 'natural_vibrant'

        except Exception as e:
            logger.error(f"🎬 [RESOLVE LEARNING] Grade selection error: {e}")
            return 'natural_vibrant'

    def get_grade_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics for all color grades.

        Returns:
            Dict with per-grade statistics
        """
        logger.info("🎬 [RESOLVE LEARNING] Getting grade statistics...")

        try:
            from core.models_unified_system import ResolveRenderJob
            from resolve_node.color_grades import get_all_presets

            all_grades = get_all_presets()
            stats = {}

            for grade_name in all_grades:
                jobs = ResolveRenderJob.objects.filter(color_grade=grade_name)

                if not jobs.exists():
                    stats[grade_name] = {
                        'total_jobs': 0,
                        'avg_rating': None,
                        'usage_rate': None,
                        'total_revenue': Decimal('0'),
                        'auto_selected_count': 0,
                    }
                    continue

                total = jobs.count()
                rated = jobs.filter(user_rating__isnull=False)
                used = jobs.filter(was_used=True)
                auto = jobs.filter(auto_grade_selected=True)

                stats[grade_name] = {
                    'total_jobs': total,
                    'avg_rating': round(
                        rated.aggregate(Avg('user_rating'))['user_rating__avg'] or 0, 2
                    ),
                    'usage_rate': round(used.count() / total, 2) if total > 0 else 0,
                    'total_revenue': jobs.aggregate(
                        Sum('revenue_generated')
                    )['revenue_generated__sum'] or Decimal('0'),
                    'auto_selected_count': auto.count(),
                    'auto_selected_rate': round(auto.count() / total, 2) if total > 0 else 0,
                }

            return stats

        except Exception as e:
            logger.error(f"🎬 [RESOLVE LEARNING] Statistics error: {e}")
            return {}

    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get insights from the learning loop for display.

        Returns:
            Dict with learning insights and recommendations
        """
        logger.info("🎬 [RESOLVE LEARNING] Generating insights...")

        try:
            from core.models_unified_system import ResolveRenderJob

            # Get overall statistics
            total_jobs = ResolveRenderJob.objects.count()
            rated_jobs = ResolveRenderJob.objects.filter(user_rating__isnull=False).count()

            if total_jobs == 0:
                return {
                    'status': 'insufficient_data',
                    'message': 'No render jobs yet. Start rendering to generate insights!',
                    'jobs_needed': 10,
                }

            # Top performing grades
            stats = self.get_grade_statistics()
            top_rated = sorted(
                [(k, v) for k, v in stats.items() if v.get('avg_rating')],
                key=lambda x: x[1].get('avg_rating', 0),
                reverse=True
            )[:3]

            most_used = sorted(
                [(k, v) for k, v in stats.items() if v.get('usage_rate')],
                key=lambda x: x[1].get('usage_rate', 0),
                reverse=True
            )[:3]

            # Auto vs manual performance
            auto_jobs = ResolveRenderJob.objects.filter(
                auto_grade_selected=True,
                user_rating__isnull=False
            )
            manual_jobs = ResolveRenderJob.objects.filter(
                auto_grade_selected=False,
                user_rating__isnull=False
            )

            auto_avg = auto_jobs.aggregate(Avg('user_rating'))['user_rating__avg'] or 0
            manual_avg = manual_jobs.aggregate(Avg('user_rating'))['user_rating__avg'] or 0

            return {
                'status': 'ready' if rated_jobs >= 10 else 'learning',
                'total_jobs': total_jobs,
                'rated_jobs': rated_jobs,
                'rating_coverage': round(rated_jobs / total_jobs * 100, 1) if total_jobs > 0 else 0,
                'top_rated_grades': [
                    {'name': k, 'avg_rating': v.get('avg_rating')}
                    for k, v in top_rated
                ],
                'most_used_grades': [
                    {'name': k, 'usage_rate': v.get('usage_rate')}
                    for k, v in most_used
                ],
                'auto_vs_manual': {
                    'auto_avg_rating': round(auto_avg, 2),
                    'manual_avg_rating': round(manual_avg, 2),
                    'auto_better': auto_avg > manual_avg,
                },
                'recommendation': self._generate_recommendation(stats),
            }

        except Exception as e:
            logger.error(f"🎬 [RESOLVE LEARNING] Insights error: {e}")
            return {'status': 'error', 'error': str(e)}

    def _get_grade_performance(self) -> Dict[str, Dict[str, float]]:
        """Get cached or fresh grade performance data."""
        # Check cache
        if (
            self._grade_cache and
            self._cache_timestamp and
            timezone.now() - self._cache_timestamp < self._cache_duration
        ):
            return self._grade_cache

        # Fresh calculation
        try:
            from core.models_unified_system import ResolveRenderJob

            performance = {}

            grades = ResolveRenderJob.objects.values('color_grade').distinct()

            for grade_entry in grades:
                grade_name = grade_entry['color_grade']
                jobs = ResolveRenderJob.objects.filter(color_grade=grade_name)

                if not jobs.exists():
                    continue

                total = jobs.count()
                rated = jobs.filter(user_rating__isnull=False)
                used = jobs.filter(was_used=True)
                with_revenue = jobs.filter(revenue_generated__gt=0)

                performance[grade_name] = {
                    'total_jobs': total,
                    'avg_rating': rated.aggregate(
                        Avg('user_rating')
                    )['user_rating__avg'] or 3.0,
                    'usage_rate': used.count() / total if total > 0 else 0.5,
                    'revenue_rate': with_revenue.count() / total if total > 0 else 0,
                }

            # Cache results
            self._grade_cache = performance
            self._cache_timestamp = timezone.now()

            return performance

        except Exception as e:
            logger.error(f"🎬 [RESOLVE LEARNING] Performance calc error: {e}")
            return {}

    def _extract_trend_keywords(self, spider_trends: Dict[str, Any]) -> List[str]:
        """Extract keyword list from spider trends."""
        keywords = []

        if 'trending_styles' in spider_trends:
            for item in spider_trends['trending_styles']:
                if isinstance(item, dict):
                    keywords.append(item.get('style', '').lower())
                else:
                    keywords.append(str(item).lower())

        if 'trending_colors' in spider_trends:
            for item in spider_trends['trending_colors']:
                if isinstance(item, dict):
                    keywords.append(item.get('palette', '').lower())
                else:
                    keywords.append(str(item).lower())

        if 'keywords' in spider_trends:
            keywords.extend([k.lower() for k in spider_trends.get('keywords', [])])

        return keywords

    def _calculate_trend_relevance(
        self,
        preset: Dict[str, Any],
        trend_keywords: List[str]
    ) -> float:
        """Calculate how relevant a preset is to trend keywords."""
        if not trend_keywords:
            return 0.5

        matches = 0

        # Check spider_styles
        for style in preset.get('spider_styles', []):
            if style.lower() in trend_keywords:
                matches += 1
            elif any(style.lower() in kw or kw in style.lower() for kw in trend_keywords):
                matches += 0.5

        # Check spider_colors
        for color in preset.get('spider_colors', []):
            if color.lower() in trend_keywords:
                matches += 1
            elif any(color.lower() in kw or kw in color.lower() for kw in trend_keywords):
                matches += 0.5

        # Normalize to 0-1 range
        max_possible = len(preset.get('spider_styles', [])) + len(preset.get('spider_colors', []))
        return min(matches / max_possible, 1.0) if max_possible > 0 else 0.5

    def _generate_recommendation(self, stats: Dict[str, Any]) -> str:
        """Generate a recommendation based on statistics."""
        if not stats:
            return "Start rendering videos to generate recommendations!"

        # Find highest rated with good sample size
        rated_grades = [
            (k, v) for k, v in stats.items()
            if v.get('total_jobs', 0) >= 3 and v.get('avg_rating')
        ]

        if not rated_grades:
            return "Need more rated renders for accurate recommendations."

        best = max(rated_grades, key=lambda x: x[1].get('avg_rating', 0))

        if best[1].get('avg_rating', 0) >= 4.0:
            return f"'{best[0]}' is performing excellently! Consider it as your default."
        elif best[1].get('avg_rating', 0) >= 3.0:
            return f"'{best[0]}' is your current best performer. Keep rating to improve accuracy."
        else:
            return "Consider trying different color grades and rating them to find your best match."

    def _invalidate_cache(self):
        """Invalidate the performance cache."""
        self._grade_cache = {}
        self._cache_timestamp = None


# Singleton instance
_learning_service: Optional[ResolveLearningService] = None


def get_resolve_learning_service() -> ResolveLearningService:
    """Get or create the ResolveLearningService singleton."""
    global _learning_service
    if _learning_service is None:
        _learning_service = ResolveLearningService()
    return _learning_service
