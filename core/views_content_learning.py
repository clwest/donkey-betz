"""
Content Learning API - Session 886
===================================

API endpoints for the content feedback loop system.

Provides visibility into:
- Blog performance context (what gets injected into ContentWriterAgent)
- Performance metrics
- Learning rules
- Content engagement data
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

logger = logging.getLogger(__name__)


class BlogPerformanceContextView(APIView):
    """
    GET /api/content-learning/performance-context/

    Returns the performance context that gets injected into ContentWriterAgent.
    Useful for debugging and understanding what the agent "knows" about past performance.
    """
    permission_classes = [AllowAny]  # Public for debugging, change to IsAuthenticated in production

    def get(self, request):
        try:
            from core.services.blog_performance_context import (
                get_blog_performance_context,
                get_performance_metrics_dict
            )

            # Get query params
            limit = int(request.query_params.get('limit', 10))
            include_rules = request.query_params.get('include_rules', 'true').lower() == 'true'
            include_engagement = request.query_params.get('include_engagement', 'true').lower() == 'true'
            format_type = request.query_params.get('format', 'text')  # 'text' or 'json'

            if format_type == 'json':
                # Return structured data
                data = get_performance_metrics_dict(limit=limit)
                return Response({
                    'success': True,
                    'data': data,
                    'format': 'json',
                })
            else:
                # Return the actual context string that gets injected
                context = get_blog_performance_context(
                    limit=limit,
                    include_learning_rules=include_rules,
                    include_engagement=include_engagement
                )
                return Response({
                    'success': True,
                    'context': context,
                    'context_length': len(context),
                    'format': 'text',
                    'note': 'This is the exact context injected into ContentWriterAgent prompts'
                })

        except Exception as e:
            logger.error(f"Failed to get performance context: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BlogPerformanceMetricsView(APIView):
    """
    GET /api/content-learning/metrics/

    Returns structured performance metrics for dashboards.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            from core.services.blog_performance_context import get_performance_metrics_dict

            limit = int(request.query_params.get('limit', 10))
            data = get_performance_metrics_dict(limit=limit)

            return Response({
                'success': True,
                **data
            })

        except Exception as e:
            logger.error(f"Failed to get metrics: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LearningRulesView(APIView):
    """
    GET /api/content-learning/rules/

    Returns active learning rules from PipelineLearningInsight.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            from core.models_pipeline_feedback import PipelineLearningInsight
            from decimal import Decimal

            insights = PipelineLearningInsight.objects.filter(
                is_active=True,
                confidence__gte=Decimal('0.5')
            ).order_by('-confidence', '-estimated_impact')[:20]

            rules = []
            for insight in insights:
                rules.append({
                    'id': str(insight.id),
                    'stage': insight.stage,
                    'type': insight.insight_type,
                    'summary': insight.insight_summary,
                    'confidence': float(insight.confidence),
                    'impact': float(insight.estimated_impact) if insight.estimated_impact else None,
                    'sample_size': insight.sample_size,
                    'times_applied': insight.times_applied,
                    'applicable_to': insight.applicable_to,
                })

            return Response({
                'success': True,
                'rules': rules,
                'total_active': len(rules),
            })

        except Exception as e:
            logger.error(f"Failed to get learning rules: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContentQualityTrendsView(APIView):
    """
    GET /api/content-learning/trends/

    Returns quality score trends over time.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            from core.models_unified_system import SelfBlog
            from django.db.models import Avg, Count
            from django.db.models.functions import TruncDate
            from django.utils import timezone
            from datetime import timedelta

            days = int(request.query_params.get('days', 30))
            cutoff = timezone.now() - timedelta(days=days)

            # Daily quality trends
            daily_trends = SelfBlog.objects.filter(
                created_at__gte=cutoff,
                quality_score__isnull=False
            ).annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                avg_quality=Avg('quality_score'),
                avg_novelty=Avg('novelty_score'),
                avg_structure=Avg('structure_score'),
                count=Count('id')
            ).order_by('date')

            # Status distribution
            status_dist = SelfBlog.objects.filter(
                created_at__gte=cutoff
            ).values('status').annotate(
                count=Count('id')
            )

            # Category distribution
            category_dist = SelfBlog.objects.filter(
                created_at__gte=cutoff
            ).values('category').annotate(
                count=Count('id'),
                avg_quality=Avg('quality_score')
            ).order_by('-count')

            return Response({
                'success': True,
                'period_days': days,
                'daily_trends': list(daily_trends),
                'status_distribution': list(status_dist),
                'category_distribution': list(category_dist),
            })

        except Exception as e:
            logger.error(f"Failed to get trends: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# URL patterns to be added to urls.py:
# path('api/content-learning/performance-context/', BlogPerformanceContextView.as_view()),
# path('api/content-learning/metrics/', BlogPerformanceMetricsView.as_view()),
# path('api/content-learning/rules/', LearningRulesView.as_view()),
# path('api/content-learning/trends/', ContentQualityTrendsView.as_view()),
