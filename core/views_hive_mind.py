"""
Session 250: Hive Mind Mode API Views

All agents work on a problem simultaneously, each contributing their specialty.
Creates a "collective intelligence" experience.
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from core.models import HiveMindSession, HiveMindContribution, Agent

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def start_hive_mind_session(request):
    """
    Start a new Hive Mind session where all relevant agents work on a problem.

    POST /api/hive-mind/start/
    {
        "question": "Design a brand for a sustainable coffee company",
        "context": "Optional additional context",
        "max_agents": 8  # Optional, default 8
    }
    """
    try:
        data = json.loads(request.body) if request.body else {}
        question = data.get('question', '').strip()
        context = data.get('context', '').strip()
        max_agents = min(int(data.get('max_agents', 8)), 12)  # Cap at 12

        if not question:
            return JsonResponse({
                'success': False,
                'error': 'Question is required'
            }, status=400)

        # Select relevant agents for this question
        selected_agents = HiveMindSession.select_relevant_agents(question, max_agents)

        if not selected_agents:
            return JsonResponse({
                'success': False,
                'error': 'No relevant agents found for this question'
            }, status=400)

        # Create the session
        session = HiveMindSession.objects.create(
            question=question,
            context=context,
            status='initializing',
            participant_ids=[str(agent.id) for agent in selected_agents]
        )

        # Create pending contributions for each agent
        for agent in selected_agents:
            HiveMindContribution.objects.create(
                session=session,
                agent=agent,
                contribution='',
                status='pending'
            )

        # Trigger the Celery task to start gathering contributions
        from core.tasks import run_hive_mind_session
        run_hive_mind_session.delay(str(session.id))

        # Update status
        session.status = 'gathering'
        session.started_at = timezone.now()
        session.save()

        return JsonResponse({
            'success': True,
            'session_id': str(session.id),
            'question': question,
            'status': 'gathering',
            'participants': [
                {
                    'id': str(agent.id),
                    'name': agent.name,
                    'specialization': agent.specialization,
                    'status': 'pending'
                }
                for agent in selected_agents
            ],
            'participant_count': len(selected_agents),
            'message': f'Hive Mind activated! {len(selected_agents)} agents are now thinking...'
        })

    except Exception as e:
        logger.exception(f"Error starting Hive Mind session: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_hive_mind_session(request, session_id):
    """
    Get the status and contributions of a Hive Mind session.

    GET /api/hive-mind/session/{session_id}/
    """
    try:
        session = HiveMindSession.objects.get(id=session_id)
        contributions = session.contributions.all().select_related('agent')

        # Calculate progress
        total = contributions.count()
        completed = contributions.filter(status='completed').count()
        progress = (completed / total * 100) if total > 0 else 0

        return JsonResponse({
            'success': True,
            'session': {
                'id': str(session.id),
                'question': session.question,
                'context': session.context,
                'status': session.status,
                'synthesis': session.synthesis,
                'synthesis_summary': session.synthesis_summary,
                'created_at': session.created_at.isoformat(),
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'contribution_count': session.contribution_count,
                'total_thinking_time': session.total_thinking_time,
            },
            'progress': round(progress, 1),
            'contributions': [
                {
                    'id': str(c.id),
                    'agent': {
                        'id': str(c.agent.id),
                        'name': c.agent.name,
                        'specialization': c.agent.specialization,
                    },
                    'contribution': c.contribution,
                    'key_points': c.key_points,
                    'perspective_type': c.perspective_type,
                    'confidence_score': c.confidence_score,
                    'status': c.status,
                    'thinking_time': c.thinking_time,
                    'created_at': c.created_at.isoformat(),
                    'completed_at': c.completed_at.isoformat() if c.completed_at else None,
                }
                for c in contributions
            ]
        })

    except HiveMindSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Session not found'
        }, status=404)
    except Exception as e:
        logger.exception(f"Error getting Hive Mind session: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_hive_mind_sessions(request):
    """
    List recent Hive Mind sessions.

    GET /api/hive-mind/sessions/?limit=10
    """
    try:
        limit = min(int(request.GET.get('limit', 10)), 50)
        sessions = HiveMindSession.objects.all()[:limit]

        return JsonResponse({
            'success': True,
            'sessions': [
                {
                    'id': str(s.id),
                    'question': s.question[:100] + '...' if len(s.question) > 100 else s.question,
                    'status': s.status,
                    'participant_count': len(s.participant_ids),
                    'contribution_count': s.contribution_count,
                    'created_at': s.created_at.isoformat(),
                    'completed_at': s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in sessions
            ],
            'count': sessions.count()
        })

    except Exception as e:
        logger.exception(f"Error listing Hive Mind sessions: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_available_agents(request):
    """
    Get list of agents available for Hive Mind sessions.

    GET /api/hive-mind/agents/
    """
    try:
        agents = Agent.objects.filter(is_active=True)

        return JsonResponse({
            'success': True,
            'agents': [
                {
                    'id': str(agent.id),
                    'name': agent.name,
                    'specialization': agent.specialization,
                    'description': agent.description[:200] if agent.description else '',
                    'effectiveness_score': agent.effectiveness_score,
                }
                for agent in agents
            ],
            'count': agents.count()
        })

    except Exception as e:
        logger.exception(f"Error getting available agents: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def preview_agents(request):
    """
    Preview which agents would be selected for a question without starting a session.

    POST /api/hive-mind/preview/
    {
        "question": "Design a brand for a sustainable coffee company",
        "max_agents": 8
    }
    """
    try:
        data = json.loads(request.body) if request.body else {}
        question = data.get('question', '').strip()
        max_agents = min(int(data.get('max_agents', 8)), 12)

        if not question:
            return JsonResponse({
                'success': False,
                'error': 'Question is required'
            }, status=400)

        selected_agents = HiveMindSession.select_relevant_agents(question, max_agents)

        return JsonResponse({
            'success': True,
            'question': question,
            'agents': [
                {
                    'id': str(agent.id),
                    'name': agent.name,
                    'specialization': agent.specialization,
                    'description': agent.description[:200] if agent.description else '',
                }
                for agent in selected_agents
            ],
            'count': len(selected_agents)
        })

    except Exception as e:
        logger.exception(f"Error previewing agents: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
