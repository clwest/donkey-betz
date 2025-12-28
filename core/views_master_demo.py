"""
Master Demo View - Unified AI Learning System Showcase
"""

from django.shortcuts import render
from django.http import JsonResponse
from core.models.agents_registry import UnifiedAgentTemplate
from core.models import GeneratedProject
import redis

def master_ai_demo(request):
    """Master demo combining all AI capabilities"""

    # Get agent stats from Redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    # Get learning metrics
    learning_stats = {
        'total_agents': UnifiedAgentTemplate.objects.filter(is_active=True).count(),
        'active_learning_sessions': r.scard('active_learning_sessions') or 0,
        'code_generated_today': r.hget('stats:code_generated:today', 'count') or 0,
        'total_improvements': r.get('stats:improvements:total') or 0,
        'total_lines_today': r.hget('stats:code_generated:today', 'lines') or 0
    }

    # Get recent projects
    recent_projects = GeneratedProject.objects.order_by('-created_at')[:5]

    # Get agent performance stats
    agent_stats = {}
    for agent in UnifiedAgentTemplate.objects.filter(is_active=True)[:10]:
        stats = r.hgetall(f'agent:{agent.name}:stats')
        if stats:
            agent_stats[agent.name] = {
                'code_generated': stats.get('code_generated', 0),
                'total_lines': stats.get('total_lines', 0),
                'last_quality_score': stats.get('last_quality_score', 0),
                'last_complexity_score': stats.get('last_complexity_score', 0)
            }

    return render(request, 'master_ai_demo.html', {
        'learning_stats': learning_stats,
        'recent_projects': recent_projects,
        'agent_stats': agent_stats,
        'websocket_url': 'ws://localhost:8000/ws/ai-training/'
    })

def get_learning_stats(request):
    """API endpoint for real-time learning statistics - Updated 9/26/25 11:51 AM MST"""

    from ai_core.agents.execution_tracker import execution_tracker

    # Get comprehensive stats from the execution tracker
    stats = execution_tracker.get_comprehensive_stats()

    # Format for frontend compatibility
    formatted_stats = {
        'active_sessions': stats.get('active_agents', 0),  # Use active agents count
        'total_real_executions': stats['total_real_executions'],
        'total_demo_executions': stats['total_demo_executions'],
        'average_quality_score': stats.get('learning_rate', 0),  # Use learning rate as quality proxy
        'active_agents': stats['active_agents'],
        'total_agents': stats['total_agents'],
        'code_generated_today': stats['code_generated_today'],
        'total_lines': stats['lines_today'],
        'timestamp': stats['timestamp'],
        'agents': stats.get('recent_activities', []),

        # Additional frontend-specific fields
        'files_created': stats['files_created'],
        'success_rate': stats['success_rate'],
        'learning_rate': stats['learning_rate'],
        'projects_completed': stats['projects_completed']
    }

    return JsonResponse(formatted_stats)