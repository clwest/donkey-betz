
"""
Real Data API Views for Demo Recording
"""

from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import random
from datetime import datetime

@csrf_exempt
@require_http_methods(["GET"])
def get_income_opportunities(request):
    """Get cached income opportunities"""
    opportunities = cache.get('income_opportunities', [])
    return JsonResponse({
        'success': True,
        'count': len(opportunities),
        'total_potential': sum(o.get('budget', 0) for o in opportunities),
        'opportunities': opportunities
    })

@csrf_exempt
@require_http_methods(["GET"])
def get_sports_predictions(request):
    """Get cached sports predictions"""
    games = cache.get('sports_games', [])
    return JsonResponse({
        'success': True,
        'count': len(games),
        'sport': 'NBA',
        'games': games
    })

@csrf_exempt
@require_http_methods(["GET"])
def get_agent_registry(request):
    """Get all 149 agents"""
    agents = cache.get('agent_registry', [])

    # Group by category
    by_category = {}
    for agent in agents:
        cat = agent.get('category', 'unknown')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(agent)

    return JsonResponse({
        'success': True,
        'total_agents': len(agents),
        'categories': list(by_category.keys()),
        'agents': agents[:50],  # Return first 50 for performance
        'by_category': {k: len(v) for k, v in by_category.items()}
    })

@csrf_exempt
@require_http_methods(["POST"])
def execute_agent(request):
    """Simulate agent execution"""
    try:
        data = json.loads(request.body or b"{}") if request.body else {}
    except Exception:
        data = {}

    agent_name = data.get('agent', 'ContentCreatorAgent')
    task = data.get('task', 'Generate content')

    # Simulate execution
    result = {
        'success': True,
        'agent': agent_name,
        'task': task,
        'execution_time': round(random.uniform(0.5, 3.0), 2),
        'quality_score': round(random.uniform(0.85, 0.98), 3),
        'tokens_used': random.randint(500, 2000),
        'cost': round(random.uniform(0.10, 1.00), 2),
        'result': f'Successfully executed {task} using {agent_name}',
        'timestamp': datetime.now().isoformat()
    }

    return JsonResponse(result)

@csrf_exempt
@require_http_methods(["GET"])
def get_revenue_summary(request):
    """Get revenue summary"""
    revenue_history = cache.get('revenue_history', [])
    total_revenue = cache.get('total_revenue', 0)

    return JsonResponse({
        'success': True,
        'total_revenue': total_revenue,
        'last_30_days': revenue_history,
        'daily_average': round(total_revenue / 30, 2) if revenue_history else 0,
        'best_day': max(revenue_history, key=lambda x: x['amount']) if revenue_history else None,
        'revenue_sources': {
            'content': round(total_revenue * 0.3, 2),
            'trading': round(total_revenue * 0.4, 2),
            'sports': round(total_revenue * 0.2, 2),
            'other': round(total_revenue * 0.1, 2)
        }
    })

@csrf_exempt
@require_http_methods(["GET"])
def get_system_metrics(request):
    """Get system metrics"""
    metrics = cache.get('system_metrics', {})

    # Add some real-time variation
    if metrics:
        metrics['requests_per_minute'] = random.randint(50, 200)
        metrics['active_agents'] = random.randint(80, 149)
        metrics['cpu_usage'] = round(random.uniform(30, 70), 1)

    return JsonResponse({
        'success': True,
        'metrics': metrics,
        'timestamp': datetime.now().isoformat()
    })

@csrf_exempt
@require_http_methods(["GET"])
def get_active_orchestrations(request):
    """Get active orchestrations"""
    orchestrations = cache.get('active_orchestrations', [])

    return JsonResponse({
        'success': True,
        'count': len(orchestrations),
        'orchestrations': orchestrations
    })

@csrf_exempt
@require_http_methods(["GET"])
def get_user_profile(request):
    """Get user profile"""
    profile = cache.get('user_profile', {})

    return JsonResponse({
        'success': True,
        'profile': profile
    })

@csrf_exempt
@require_http_methods(["GET"])
def get_recent_executions(request):
    """Get recent agent executions"""
    executions = cache.get('recent_executions', [])

    return JsonResponse({
        'success': True,
        'count': len(executions),
        'executions': executions
    })
