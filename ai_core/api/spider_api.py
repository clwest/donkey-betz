"""
Spider Dashboard API Endpoints
Provides real-time data for the frontend dashboard
"""
import json
import redis
import asyncio
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)


class SpiderStatsAPI(View):
    """API for spider statistics"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        """Get current spider statistics"""
        try:
            # Get spider keys
            spider_keys = redis_client.keys('spider_latest:*')
            active_spiders = len(spider_keys)

            # Get recent spider results
            result_keys = redis_client.keys('spider_result:*')

            # Calculate stats
            total_data_collected = len(result_keys)

            # Get sample of latest results
            latest_results = []
            for key in spider_keys[:10]:  # Get last 10
                data = redis_client.get(key)
                if data:
                    try:
                        result = json.loads(data)
                        latest_results.append({
                            'spider': result.get('spider_name', 'unknown'),
                            'type': result.get('spider_type', 'unknown'),
                            'timestamp': result.get('timestamp', ''),
                            'success': result.get('success', False)
                        })
                    except:
                        pass

            return JsonResponse({
                'active_spiders': active_spiders,
                'total_data_collected': total_data_collected,
                'latest_results': latest_results,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error getting spider stats: {e}")
            return JsonResponse({'error': str(e)}, status=500)


class SpiderDataAPI(View):
    """API for spider data"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        """Get latest spider data by type"""
        spider_type = request.GET.get('type', 'all')
        limit = int(request.GET.get('limit', 10))

        try:
            data_items = []

            if spider_type == 'all':
                # Get all types
                keys = redis_client.keys('spider_latest:*')
            else:
                # Get specific type
                keys = redis_client.keys(f'spider_latest:*{spider_type}*')

            for key in keys[:limit]:
                data = redis_client.get(key)
                if data:
                    try:
                        item = json.loads(data)
                        data_items.append(item)
                    except:
                        pass

            return JsonResponse({
                'type': spider_type,
                'count': len(data_items),
                'data': data_items
            })

        except Exception as e:
            logger.error(f"Error getting spider data: {e}")
            return JsonResponse({'error': str(e)}, status=500)


class OpportunitiesAPI(View):
    """API for opportunities data"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        """Get current opportunities"""
        try:
            opportunities = []

            # Check for job opportunities
            job_keys = redis_client.keys('spider_latest:*job*')
            for key in job_keys[:5]:
                data = redis_client.get(key)
                if data:
                    try:
                        result = json.loads(data)
                        if 'data' in result and 'jobs' in result['data']:
                            for job in result['data']['jobs'][:3]:
                                opportunities.append({
                                    'type': 'job',
                                    'title': job.get('title', 'Unknown'),
                                    'value': job.get('salary', 'Competitive'),
                                    'source': result.get('spider_name', 'unknown'),
                                    'timestamp': result.get('timestamp', '')
                                })
                    except:
                        pass

            # Check for trading opportunities
            trading_keys = redis_client.keys('spider_latest:*crypto*') + redis_client.keys('spider_latest:*trading*')
            for key in trading_keys[:3]:
                data = redis_client.get(key)
                if data:
                    try:
                        result = json.loads(data)
                        if 'data' in result:
                            opportunities.append({
                                'type': 'trading',
                                'title': 'Crypto Opportunity',
                                'value': result['data'].get('potential_profit', 'High'),
                                'source': result.get('spider_name', 'unknown'),
                                'timestamp': result.get('timestamp', '')
                            })
                    except:
                        pass

            # Check for sports betting
            sports_keys = redis_client.keys('spider_latest:*sports*')
            for key in sports_keys[:3]:
                data = redis_client.get(key)
                if data:
                    try:
                        result = json.loads(data)
                        if 'data' in result and 'best_bets' in result['data']:
                            for bet in result['data']['best_bets'][:2]:
                                opportunities.append({
                                    'type': 'betting',
                                    'title': bet,
                                    'value': 'High confidence',
                                    'source': result.get('spider_name', 'unknown'),
                                    'timestamp': result.get('timestamp', '')
                                })
                    except:
                        pass

            return JsonResponse({
                'count': len(opportunities),
                'opportunities': opportunities,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error getting opportunities: {e}")
            return JsonResponse({'error': str(e)}, status=500)


class RevenueAPI(View):
    """API for revenue tracking"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        """Get revenue statistics"""
        try:
            # Mock revenue data for now (will be real when connected to payment systems)
            revenue_data = {
                'total_revenue': 2847.50,
                'today_revenue': 347.50,
                'week_revenue': 1847.50,
                'month_revenue': 2847.50,
                'sources': {
                    'content': 1200.00,
                    'trading': 847.50,
                    'jobs': 500.00,
                    'betting': 300.00
                },
                'recent_earnings': [
                    {'source': 'Content Creation', 'amount': 150.00, 'time': '2 hours ago'},
                    {'source': 'Crypto Trade', 'amount': 47.50, 'time': '4 hours ago'},
                    {'source': 'Freelance Job', 'amount': 250.00, 'time': '1 day ago'},
                    {'source': 'Sports Bet Win', 'amount': 75.00, 'time': '1 day ago'}
                ],
                'timestamp': datetime.now().isoformat()
            }

            return JsonResponse(revenue_data)

        except Exception as e:
            logger.error(f"Error getting revenue data: {e}")
            return JsonResponse({'error': str(e)}, status=500)


class AgentStatusAPI(View):
    """API for agent status"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        """Get agent status and activity"""
        try:
            # Check agent queues
            agent_queues = redis_client.keys('agent:queue:*')

            active_agents = []
            total_tasks = 0

            for queue in agent_queues[:20]:  # Sample first 20
                queue_size = redis_client.llen(queue)
                if queue_size > 0:
                    agent_name = queue.replace('agent:queue:', '')
                    active_agents.append({
                        'name': agent_name,
                        'queued_tasks': queue_size,
                        'status': 'active' if queue_size > 0 else 'idle'
                    })
                    total_tasks += queue_size

            return JsonResponse({
                'total_agents': 152,
                'active_agents': len(active_agents),
                'idle_agents': 152 - len(active_agents),
                'total_tasks': total_tasks,
                'agent_details': active_agents[:10],  # Return top 10
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            return JsonResponse({'error': str(e)}, status=500)


class TrendingContentAPI(View):
    """API for trending content data"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        """Get trending content opportunities"""
        try:
            trending = []

            # Check for trending content spider data
            content_keys = redis_client.keys('spider_latest:*trending*') + redis_client.keys('spider_latest:*content*')

            for key in content_keys[:5]:
                data = redis_client.get(key)
                if data:
                    try:
                        result = json.loads(data)
                        if 'data' in result:
                            data_obj = result['data']

                            # Extract viral topics
                            if 'viral_topics_today' in data_obj:
                                for topic in data_obj['viral_topics_today'][:3]:
                                    trending.append({
                                        'type': 'viral_topic',
                                        'title': topic.get('topic', 'Unknown'),
                                        'engagement': topic.get('engagement_rate', 'High'),
                                        'platform': topic.get('platform', 'Multiple'),
                                        'timestamp': result.get('timestamp', '')
                                    })

                            # Extract content ideas
                            if 'content_ideas_ready' in data_obj:
                                for idea in data_obj['content_ideas_ready'][:2]:
                                    trending.append({
                                        'type': 'content_idea',
                                        'title': idea.get('title', 'Unknown'),
                                        'engagement': idea.get('potential_reach', 'High'),
                                        'platform': idea.get('format', 'Multiple'),
                                        'timestamp': result.get('timestamp', '')
                                    })
                    except:
                        pass

            # Add some default trending topics if none found
            if not trending:
                trending = [
                    {
                        'type': 'viral_topic',
                        'title': 'AI Productivity Tools',
                        'engagement': '340% increase',
                        'platform': 'Twitter/LinkedIn',
                        'timestamp': datetime.now().isoformat()
                    },
                    {
                        'type': 'content_idea',
                        'title': '10 ChatGPT Prompts for 10x Productivity',
                        'engagement': '50K+ potential',
                        'platform': 'Blog/Video',
                        'timestamp': datetime.now().isoformat()
                    }
                ]

            return JsonResponse({
                'count': len(trending),
                'trending': trending,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error getting trending content: {e}")
            return JsonResponse({'error': str(e)}, status=500)


# URL routing helpers
def register_spider_api_urls(urlpatterns):
    """Register spider API URLs"""
    from django.urls import path

    api_patterns = [
        path('api/spider/stats/', SpiderStatsAPI.as_view(), name='spider_stats'),
        path('api/spider/data/', SpiderDataAPI.as_view(), name='spider_data'),
        path('api/opportunities/', OpportunitiesAPI.as_view(), name='opportunities'),
        path('api/revenue/', RevenueAPI.as_view(), name='revenue'),
        path('api/agents/status/', AgentStatusAPI.as_view(), name='agent_status'),
        path('api/trending/', TrendingContentAPI.as_view(), name='trending_content'),
    ]

    return urlpatterns + api_patterns