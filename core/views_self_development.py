"""
Self-Development API Views
API endpoints for autonomous self-improvement system
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def self_awareness_api(request):
    """Get system self-awareness data"""
    try:
        from core.self_development import self_awareness

        user = request.user

        capabilities = self_awareness.get_system_capabilities()
        performance = self_awareness.assess_performance(user)
        gaps = self_awareness.identify_knowledge_gaps(user)

        return JsonResponse({
            'success': True,
            'capabilities': capabilities,
            'performance': performance,
            'gaps': gaps
        })

    except Exception as e:
        logger.error(f"Error in self_awareness_api: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def self_awareness_report(request):
    """Generate self-awareness report"""
    try:
        from core.self_development import self_awareness

        user = request.user
        report = self_awareness.generate_self_report(user)

        return JsonResponse({
            'success': True,
            'report': report
        })

    except Exception as e:
        logger.error(f"Error in self_awareness_report: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def suggest_team_api(request):
    """Suggest optimal agent team for task"""
    try:
        from core.self_development import collaboration_optimizer

        data = json.loads(request.body)
        task = data.get('task', '')

        if not task:
            return JsonResponse({
                'success': False,
                'error': 'Task description required'
            }, status=400)

        team = collaboration_optimizer.suggest_optimal_team(
            task_description=task,
            user=request.user,
            max_agents=5
        )

        # Get insights
        insights = collaboration_optimizer.get_collaboration_insights(request.user)

        return JsonResponse({
            'success': True,
            'team': team,
            'insights': insights
        })

    except Exception as e:
        logger.error(f"Error in suggest_team_api: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def execute_agent_api(request):
    """Execute agent and trigger learning cycle"""
    try:
        data = json.loads(request.body)
        agent_name = data.get('agent')
        task = data.get('task')

        if not agent_name or not task:
            return JsonResponse({
                'success': False,
                'error': 'Agent name and task required'
            }, status=400)

        # Execute agent (pass user to enable automatic learning via Django signals)
        from ai_core.agents.concrete_executor import execute_agent_sync

        logger.info(f"🤖 Executing agent: {agent_name}")
        result = execute_agent_sync(agent_name, task, user=request.user)

        # Note: Learning cycle is automatically triggered via Django signal
        # When AgentExecution record is saved, agent_execution_bridge fires
        # and triggers learning_orchestrator for autonomous improvement

        return JsonResponse({
            'success': True,
            'result': result,
            'message': f'✅ Agent {agent_name} executed successfully! Autonomous learning activated.',
            'learning_activated': True
        })

    except Exception as e:
        logger.error(f"Error in execute_agent_api: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def learning_status_api(request):
    """Get learning orchestrator status"""
    try:
        from core.self_development import learning_orchestrator

        status = learning_orchestrator.get_system_learning_status(request.user)

        return JsonResponse({
            'success': True,
            'status': status
        })

    except Exception as e:
        logger.error(f"Error in learning_status_api: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def list_agents_api(request):
    """List all available agents"""
    try:
        from core.models_unified_system import Agent

        agents = Agent.objects.filter(is_active=True).values(
            'name', 'specialization', 'description', 'effectiveness_score'
        )

        return JsonResponse({
            'success': True,
            'agents': list(agents)
        })

    except Exception as e:
        logger.error(f"Error in list_agents_api: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
