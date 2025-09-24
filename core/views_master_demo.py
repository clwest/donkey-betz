"""
Master Demo View - Unified AI Learning System Showcase
"""

from django.shortcuts import render
from django.http import JsonResponse
from agents.models import UnifiedAgentTemplate
from core.models import GeneratedProject, GeneratedCode
import redis
import json
from datetime import datetime

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
    """API endpoint for real-time learning statistics"""

    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    # Calculate aggregated learning metrics
    total_real_executions = 0
    total_demo_executions = 0
    total_quality_score = 0
    quality_count = 0

    # Get agent-specific stats and calculate totals
    agents = []
    agent_keys = r.keys('agent:*:stats')

    for key in agent_keys[:50]:  # Process up to 50 agents
        agent_name = key.split(':')[1]
        agent_data = r.hgetall(key)
        if agent_data:
            # Extract real execution data
            real_execs = int(agent_data.get('real_executions', 0))
            demo_execs = int(agent_data.get('demo_executions', 0))
            quality = int(agent_data.get('last_quality_score', 0))

            # Add to totals
            total_real_executions += real_execs
            total_demo_executions += demo_execs
            if quality > 0:
                total_quality_score += quality
                quality_count += 1

            agents.append({
                'name': agent_name,
                'real_executions': real_execs,
                'demo_executions': demo_execs,
                'code_generated': agent_data.get('code_generated', 0),
                'total_lines': int(agent_data.get('total_lines', 0)),
                'quality': quality,
                'complexity': int(agent_data.get('last_complexity_score', 0)),
                'last_task': agent_data.get('last_real_task', 'none')
            })

    # Sort agents by real executions (most active first)
    agents.sort(key=lambda x: x['real_executions'], reverse=True)

    # Calculate average quality score
    avg_quality = total_quality_score / quality_count if quality_count > 0 else 0

    stats = {
        'active_sessions': r.scard('active_learning_sessions') or 0,
        'total_real_executions': total_real_executions,
        'total_demo_executions': total_demo_executions,
        'average_quality_score': round(avg_quality, 1),
        'active_agents': len([a for a in agents if a['real_executions'] > 0]),
        'total_agents': len(agents),
        'code_generated_today': r.hget('stats:code_generated:today', 'count') or 0,
        'total_lines': sum(a['total_lines'] for a in agents),
        'timestamp': datetime.now().isoformat(),
        'agents': agents[:20]  # Return top 20 most active agents
    }

    return JsonResponse(stats)