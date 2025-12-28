"""
Learning Loop API Views - Session 449

API endpoints for:
1. Recording user feedback on pipeline stages
2. Getting style/voice recommendations
3. Viewing learning statistics and insights
4. Managing engagement tracking

Endpoints:
- POST /api/learning/feedback/ - Record stage feedback
- POST /api/learning/engagement/ - Record engagement metrics
- GET /api/learning/recommend/style/ - Get style recommendation
- GET /api/learning/recommend/voice/ - Get voice recommendation
- GET /api/learning/leaderboard/styles/ - Get style performance leaderboard
- GET /api/learning/insights/ - Get active learning insights
- GET /api/learning/stats/ - Get overall learning statistics
"""

import logging

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from core.services.pipeline_learning import get_pipeline_learning_service

logger = logging.getLogger(__name__)


def get_json_body(request):
    """Parse JSON body from request."""
    try:
        return json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return {}


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def record_feedback(request):
    """
    Record feedback for a pipeline stage.

    POST /api/learning/feedback/

    Body:
    {
        "stage": "image",  // research, script, image, voice, video, package
        "rating": 4.5,     // 1.0 - 5.0
        "context": {
            "style_preset": "pixar",
            "target_audience": "kids",
            "series_type": "educational"
        },
        "series_id": "uuid",        // optional
        "episode_id": "uuid",       // optional
        "feedback_type": "user_rating",  // user_rating, implicit, automated, ab_test
        "comment": "Great style!"   // optional
    }
    """
    try:
        data = get_json_body(request)

        # Validate required fields
        stage = data.get('stage')
        rating = data.get('rating')

        if not stage:
            return JsonResponse({
                'success': False,
                'error': 'Missing required field: stage'
            }, status=400)

        if rating is None:
            return JsonResponse({
                'success': False,
                'error': 'Missing required field: rating'
            }, status=400)

        try:
            rating = float(rating)
            if not (1.0 <= rating <= 5.0):
                return JsonResponse({
                    'success': False,
                    'error': 'Rating must be between 1.0 and 5.0'
                }, status=400)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Rating must be a number'
            }, status=400)

        # Valid stages
        valid_stages = ['research', 'script', 'image', 'voice', 'video', 'package']
        if stage not in valid_stages:
            return JsonResponse({
                'success': False,
                'error': f'Invalid stage. Must be one of: {", ".join(valid_stages)}'
            }, status=400)

        service = get_pipeline_learning_service()
        feedback = service.record_stage_feedback(
            stage=stage,
            rating=rating,
            context=data.get('context', {}),
            series_id=data.get('series_id'),
            episode_id=data.get('episode_id'),
            content_package_id=data.get('content_package_id'),
            user_id=request.user.id,
            feedback_type=data.get('feedback_type', 'user_rating'),
            comment=data.get('comment', '')
        )

        if feedback:
            return JsonResponse({
                'success': True,
                'feedback_id': str(feedback.id),
                'message': f'Recorded {stage} feedback: {rating}/5'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to record feedback'
            }, status=500)

    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def record_engagement(request):
    """
    Record engagement metrics for published content.

    POST /api/learning/engagement/

    Body:
    {
        "platform": "youtube",
        "series_id": "uuid",     // optional
        "episode_id": "uuid",    // optional
        "metrics": {
            "views": 1000,
            "likes": 50,
            "shares": 10,
            "comments": 5,
            "completion_rate": 75.5,
            "revenue": 10.50
        },
        "outcome": "published",  // pending, delivered, approved, rejected, published, viral
        "content_context": {
            "style_preset": "pixar",
            "series_type": "educational"
        }
    }
    """
    try:
        data = get_json_body(request)

        platform = data.get('platform')
        if not platform:
            return JsonResponse({
                'success': False,
                'error': 'Missing required field: platform'
            }, status=400)

        service = get_pipeline_learning_service()
        engagement = service.record_engagement(
            platform=platform,
            series_id=data.get('series_id'),
            episode_id=data.get('episode_id'),
            metrics=data.get('metrics', {}),
            outcome=data.get('outcome', 'pending'),
            content_context=data.get('content_context', {})
        )

        if engagement:
            return JsonResponse({
                'success': True,
                'engagement_id': str(engagement.id),
                'engagement_score': engagement.engagement_score
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to record engagement'
            }, status=500)

    except Exception as e:
        logger.error(f"Error recording engagement: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def recommend_style(request):
    """
    Get style recommendation based on historical performance.

    GET /api/learning/recommend/style/?audience=kids&series_type=educational

    Query params:
    - audience: Target audience (required)
    - series_type: Type of series (optional)

    Response:
    {
        "success": true,
        "recommendation": {
            "style_preset": "pixar",
            "avg_rating": 4.5,
            "approval_rate": 85.0,
            "confidence": 0.75,
            "sample_size": 15,
            "source": "learned"  // or "default"
        }
    }
    """
    try:
        audience = request.GET.get('audience', '')
        series_type = request.GET.get('series_type', '')

        if not audience:
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameter: audience'
            }, status=400)

        service = get_pipeline_learning_service()
        recommendation = service.get_best_style_for_context(
            target_audience=audience,
            series_type=series_type
        )

        return JsonResponse({
            'success': True,
            'recommendation': recommendation
        })

    except Exception as e:
        logger.error(f"Error getting style recommendation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def recommend_voice(request):
    """
    Get voice recommendation based on historical performance.

    GET /api/learning/recommend/voice/?series_type=educational&audience=kids

    Query params:
    - series_type: Type of series (optional)
    - audience: Target audience (optional)

    Response:
    {
        "success": true,
        "recommendation": {
            "voice_id": "...",
            "voice_name": "Rachel",
            "avg_rating": 4.3,
            "completion_rate": 80.5,
            "confidence": 0.6,
            "source": "learned"
        }
    }
    """
    try:
        series_type = request.GET.get('series_type', '')
        audience = request.GET.get('audience', '')

        service = get_pipeline_learning_service()
        recommendation = service.get_best_voice_for_context(
            series_type=series_type,
            target_audience=audience
        )

        return JsonResponse({
            'success': True,
            'recommendation': recommendation
        })

    except Exception as e:
        logger.error(f"Error getting voice recommendation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def style_leaderboard(request):
    """
    Get leaderboard of best-performing styles.

    GET /api/learning/leaderboard/styles/?series_type=educational&audience=kids&limit=10

    Query params:
    - series_type: Filter by series type (optional)
    - audience: Filter by target audience (optional)
    - limit: Max results (default 10)

    Response:
    {
        "success": true,
        "leaderboard": [
            {
                "style_preset": "pixar",
                "target_audience": "kids",
                "series_type": "educational",
                "avg_rating": 4.7,
                "approval_rate": 90.0,
                "engagement_score": 75.5,
                "total_uses": 25,
                "viral_count": 2,
                "confidence": 0.85
            },
            ...
        ]
    }
    """
    try:
        series_type = request.GET.get('series_type', '')
        audience = request.GET.get('audience', '')
        limit = int(request.GET.get('limit', 10))

        service = get_pipeline_learning_service()
        leaderboard = service.get_style_leaderboard(
            series_type=series_type,
            target_audience=audience,
            limit=limit
        )

        return JsonResponse({
            'success': True,
            'leaderboard': leaderboard
        })

    except Exception as e:
        logger.error(f"Error getting style leaderboard: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_insights(request):
    """
    Get active learning insights.

    GET /api/learning/insights/?stage=image

    Query params:
    - stage: Filter by pipeline stage (optional)

    Response:
    {
        "success": true,
        "insights": [
            {
                "id": "uuid",
                "stage": "image",
                "type": "best_style",
                "summary": "Pixar style performs 23% better for kids content",
                "data": {...},
                "confidence": 0.85,
                "sample_size": 20,
                "estimated_impact": 23.0,
                "times_applied": 5
            },
            ...
        ]
    }
    """
    try:
        stage = request.GET.get('stage')

        service = get_pipeline_learning_service()
        insights = service.get_active_insights(stage=stage)

        return JsonResponse({
            'success': True,
            'insights': insights
        })

    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_statistics(request):
    """
    Get overall learning system statistics.

    GET /api/learning/stats/

    Response:
    {
        "success": true,
        "stats": {
            "feedback": {
                "total_count": 150,
                "by_stage": {"image": 50, "voice": 30, ...},
                "avg_rating": 4.2
            },
            "styles": {
                "tracked_count": 10,
                "top_style": "pixar",
                "total_uses": 100
            },
            "voices": {
                "tracked_count": 5,
                "total_uses": 30
            },
            "engagement": {
                "total_tracked": 25,
                "total_views": 50000,
                "viral_count": 3
            },
            "insights": {
                "active_count": 8,
                "total_applied": 15
            }
        }
    }
    """
    try:
        service = get_pipeline_learning_service()
        stats = service.get_learning_statistics()

        return JsonResponse({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def generate_insights(request):
    """
    Generate new learning insights from collected data.

    POST /api/learning/insights/generate/

    This analyzes feedback and engagement data to create actionable insights.

    Response:
    {
        "success": true,
        "generated_count": 5,
        "insights": [...]
    }
    """
    try:
        service = get_pipeline_learning_service()
        insights = service.generate_insights()

        return JsonResponse({
            'success': True,
            'generated_count': len(insights),
            'insights': [
                {
                    'id': str(i.id),
                    'stage': i.stage,
                    'summary': i.insight_summary,
                    'confidence': float(i.confidence)
                }
                for i in insights
            ]
        })

    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
