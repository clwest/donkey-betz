"""
Spider Intelligence API Views
Session 208: API endpoints for querying spider data intelligently.

Endpoints:
    GET /api/spider-intelligence/trends/      - Trending topics
    GET /api/spider-intelligence/market/      - Market insights (crypto, stocks)
    GET /api/spider-intelligence/tech/        - Tech trends
    GET /api/spider-intelligence/jobs/        - Job market summary
    GET /api/spider-intelligence/search/      - Search spider data
    GET /api/spider-intelligence/summary/     - Data summary statistics
    GET /api/spider-intelligence/insights/    - Get insights for a prompt
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from core.services.spider_intelligence import SpiderIntelligenceService


@csrf_exempt
@require_http_methods(["GET"])
def trending_topics(request):
    """
    Get trending topics from spider data.

    Query params:
        category: Filter by category (tech, financial, jobs, news, etc.)
        hours: Look back period (default: 24)
        limit: Max topics (default: 10)
    """
    try:
        service = SpiderIntelligenceService()

        category = request.GET.get('category')
        hours = int(request.GET.get('hours', 24))
        limit = int(request.GET.get('limit', 10))

        # Cap limits for performance
        hours = min(hours, 168)  # Max 1 week
        limit = min(limit, 50)

        trends = service.get_trending_topics(
            category=category,
            hours=hours,
            limit=limit
        )

        return JsonResponse({
            'status': 'success',
            'trends': trends,
            'params': {
                'category': category,
                'hours': hours,
                'limit': limit
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def market_insights(request):
    """
    Get financial/crypto market insights.
    Aggregates data from CoinGecko, Yahoo Finance, etc.
    """
    try:
        service = SpiderIntelligenceService()
        insights = service.get_market_insights()

        return JsonResponse({
            'status': 'success',
            'insights': insights
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def tech_trends(request):
    """
    Get technology trends from HackerNews, DevTo, GitHub, etc.

    Query params:
        hours: Look back period (default: 24)
        limit: Max items per category (default: 15)
    """
    try:
        service = SpiderIntelligenceService()

        hours = int(request.GET.get('hours', 24))
        limit = int(request.GET.get('limit', 15))

        # Cap limits
        hours = min(hours, 168)
        limit = min(limit, 50)

        trends = service.get_tech_trends(hours=hours, limit=limit)

        return JsonResponse({
            'status': 'success',
            'trends': trends,
            'params': {
                'hours': hours,
                'limit': limit
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def job_market(request):
    """
    Get remote job market summary.

    Query params:
        hours: Look back period (default: 48)
        limit: Max jobs (default: 20)
    """
    try:
        service = SpiderIntelligenceService()

        hours = int(request.GET.get('hours', 48))
        limit = int(request.GET.get('limit', 20))

        # Cap limits
        hours = min(hours, 168)
        limit = min(limit, 100)

        summary = service.get_job_market_summary(hours=hours, limit=limit)

        return JsonResponse({
            'status': 'success',
            'job_market': summary,
            'params': {
                'hours': hours,
                'limit': limit
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def search_data(request):
    """
    Full-text search across spider data.

    Query params:
        q: Search query (required)
        category: Filter by category
        hours: Look back period (default: 72)
        limit: Max results (default: 50)
    """
    try:
        query = request.GET.get('q', '').strip()
        if not query:
            return JsonResponse({
                'status': 'error',
                'message': 'Query parameter "q" is required'
            }, status=400)

        service = SpiderIntelligenceService()

        category = request.GET.get('category')
        hours = int(request.GET.get('hours', 72))
        limit = int(request.GET.get('limit', 50))

        # Cap limits
        hours = min(hours, 168)
        limit = min(limit, 100)

        results = service.search_spider_data(
            query=query,
            category=category,
            hours=hours,
            limit=limit
        )

        return JsonResponse({
            'status': 'success',
            'query': query,
            'results': results,
            'count': len(results),
            'params': {
                'category': category,
                'hours': hours,
                'limit': limit
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def data_summary(request):
    """
    Get summary statistics for spider data.

    Query params:
        spider: Filter by spider name
        hours: Look back period (default: 24)
    """
    try:
        service = SpiderIntelligenceService()

        spider_name = request.GET.get('spider')
        hours = int(request.GET.get('hours', 24))

        # Cap limits
        hours = min(hours, 168)

        summary = service.get_data_summary(
            spider_name=spider_name,
            hours=hours
        )

        return JsonResponse({
            'status': 'success',
            'summary': summary
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def prompt_insights(request):
    """
    Get relevant insights for an AI prompt.
    Used by agents to enhance their responses with real data.

    GET/POST params:
        prompt: The user's prompt (required)
        limit: Max insights per category (default: 5)
    """
    try:
        # Get prompt from GET or POST
        if request.method == 'POST':
            import json
            data = json.loads(request.body or b'{}')
            prompt = data.get('prompt', '')
            limit = data.get('limit', 5)
        else:
            prompt = request.GET.get('prompt', '').strip()
            limit = int(request.GET.get('limit', 5))

        if not prompt:
            return JsonResponse({
                'status': 'error',
                'message': 'Parameter "prompt" is required'
            }, status=400)

        service = SpiderIntelligenceService()

        # Cap limit
        limit = min(limit, 20)

        insights = service.get_insights_for_prompt(
            prompt=prompt,
            limit=limit
        )

        return JsonResponse({
            'status': 'success',
            'prompt': prompt,
            'insights': insights
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def daily_report(request):
    """
    Generate a daily intelligence report.
    Combines trends, market data, and notable items.
    """
    try:
        service = SpiderIntelligenceService()

        # Gather all insights
        trends = service.get_trending_topics(hours=24, limit=10)
        market = service.get_market_insights()
        tech = service.get_tech_trends(hours=24, limit=10)
        jobs = service.get_job_market_summary(hours=24, limit=5)
        summary = service.get_data_summary(hours=24)

        # Build report
        report = {
            'title': 'Daily Intelligence Report',
            'generated_at': summary.get('generated_at'),
            'period': '24 hours',

            'highlights': {
                'total_data_points': summary.get('total_items', 0),
                'active_spiders': len(summary.get('by_spider', {})),
                'top_trend': trends[0] if trends else None,
            },

            'sections': {
                'trending_topics': {
                    'title': 'Trending Topics',
                    'items': trends[:5]
                },
                'market_snapshot': {
                    'title': 'Market Snapshot',
                    'crypto': market.get('crypto', [])[:5],
                    'summary': market.get('summary', '')
                },
                'tech_pulse': {
                    'title': 'Tech Pulse',
                    'top_discussions': tech.get('discussions', [])[:5],
                    'hot_topics': tech.get('topics', [])[:10]
                },
                'job_market': {
                    'title': 'Remote Job Market',
                    'total_jobs': jobs.get('total_found', 0),
                    'top_categories': jobs.get('categories', [])[:5],
                    'featured_jobs': jobs.get('jobs', [])[:3]
                }
            },

            'data_sources': summary.get('by_spider', {})
        }

        return JsonResponse({
            'status': 'success',
            'report': report
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
