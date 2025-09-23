"""
Learning Path API Views
Endpoints for triggering and monitoring agent learning paths
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import random
from datetime import datetime
from typing import List

from core.models_unified_system import Agent, AgentSolution, AgentLearning
from intelligence.learning_path_orchestrator import LearningPathOrchestrator


@csrf_exempt
@require_http_methods(["POST"])
def trigger_learning_query(request):
    """
    Trigger a learning query for an agent to learn about a new topic
    """
    try:
        data = json.loads(request.body)
        query = data.get('query')
        agent_name = data.get('agent', None)

        if not query:
            return JsonResponse({
                'error': 'Query is required'
            }, status=400)

        # Select an agent (or use specified one)
        if agent_name:
            try:
                agent = Agent.objects.get(name=agent_name)
            except Agent.DoesNotExist:
                return JsonResponse({
                    'error': f'Agent {agent_name} not found'
                }, status=404)
        else:
            # Select a relevant agent based on query
            agent = _select_best_agent_for_query(query)

        # Initialize orchestrator
        orchestrator = LearningPathOrchestrator()

        # Check for knowledge gap
        has_gap, confidence = orchestrator.detect_knowledge_gap(query, agent)

        response = {
            'agent': agent.name,
            'query': query,
            'has_knowledge_gap': has_gap,
            'current_confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }

        if has_gap:
            # Create and execute learning path
            learning_path = orchestrator.create_learning_path(query, agent)
            response['learning_path'] = learning_path
            response['status'] = 'learning_initiated'

            # Execute learning in background (in production, use Celery)
            # For demo, execute immediately
            result = orchestrator.execute_learning_path(learning_path['session_id'])
            response['learning_result'] = result

        else:
            response['status'] = 'knowledge_exists'
            response['message'] = f'{agent.name} already has knowledge about this topic'

            # Get existing knowledge
            existing_solutions = AgentSolution.objects.filter(
                agent=agent,
                description__icontains=query[:30]
            )[:3]

            response['existing_knowledge'] = [
                {
                    'title': s.title,
                    'description': s.description[:200],
                    'solution_type': s.solution_type
                }
                for s in existing_solutions
            ]

        return JsonResponse(response)

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_learning_status(request, session_id):
    """Get the status of a learning session"""
    try:
        orchestrator = LearningPathOrchestrator()
        status = orchestrator.get_learning_status(session_id)

        if 'error' in status:
            return JsonResponse(status, status=404)

        return JsonResponse(status)

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_agent_knowledge_map(request, agent_id):
    """Get a knowledge map for a specific agent"""
    try:
        agent = Agent.objects.get(id=agent_id)

        # Get agent's solutions grouped by type
        solutions_by_type = {}
        for solution in agent.solutions.all():
            solution_type = solution.solution_type
            if solution_type not in solutions_by_type:
                solutions_by_type[solution_type] = []
            solutions_by_type[solution_type].append({
                'title': solution.title,
                'description': solution.description[:100],
                'created_at': solution.created_at.isoformat() if hasattr(solution, 'created_at') else None
            })

        # Get learning history
        learning_from = AgentLearning.objects.filter(
            student_agent=agent
        ).select_related('teacher_agent', 'solution')[:10]

        learning_to = AgentLearning.objects.filter(
            teacher_agent=agent
        ).select_related('student_agent', 'solution')[:10]

        knowledge_map = {
            'agent': {
                'id': str(agent.id),
                'name': agent.name,
                'description': agent.description,
                'total_solutions': agent.solutions.count(),
                'total_learnings_received': learning_from.count(),
                'total_learnings_taught': learning_to.count()
            },
            'knowledge_domains': solutions_by_type,
            'recent_learning_from': [
                {
                    'teacher': l.teacher_agent.name,
                    'knowledge': l.solution.title,
                    'effectiveness_gain': l.effectiveness_after - l.effectiveness_before
                }
                for l in learning_from
            ],
            'recent_teaching_to': [
                {
                    'student': l.student_agent.name,
                    'knowledge': l.solution.title,
                    'effectiveness_gain': l.effectiveness_after - l.effectiveness_before
                }
                for l in learning_to
            ],
            'knowledge_gaps': _identify_knowledge_gaps(agent),
            'timestamp': datetime.now().isoformat()
        }

        return JsonResponse(knowledge_map)

    except Agent.DoesNotExist:
        return JsonResponse({
            'error': 'Agent not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_agent_solutions_recent(request, agent_name):
    """Get recent solutions for a specific agent"""
    try:
        agent = Agent.objects.get(name=agent_name)
        solutions = agent.solutions.order_by('-id')[:10]

        return JsonResponse({
            'agent': agent.name,
            'total': agent.solutions.count(),
            'solutions': [
                {
                    'id': str(s.id),
                    'title': s.title,
                    'description': s.description[:200],
                    'solution_type': s.solution_type,
                    'created_at': s.created_at.isoformat() if hasattr(s, 'created_at') else None
                }
                for s in solutions
            ]
        })
    except Agent.DoesNotExist:
        return JsonResponse({'error': 'Agent not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_learning_feed(request):
    """Get a real-time feed of learning activities"""
    try:
        # Get recent learning activities
        recent_learnings = AgentLearning.objects.select_related(
            'teacher_agent', 'student_agent', 'solution'
        ).order_by('-id')[:20]

        feed_items = []
        for learning in recent_learnings:
            # Determine learning source
            if learning.teacher_agent == learning.student_agent:
                source = 'Self-learning'
                description = f"{learning.teacher_agent.name} acquired new knowledge"
            else:
                source = 'Knowledge transfer'
                description = f"{learning.teacher_agent.name} taught {learning.student_agent.name}"

            feed_items.append({
                'timestamp': learning.created_at.isoformat() if hasattr(learning, 'created_at') else datetime.now().isoformat(),
                'type': learning.learning_type,
                'source': source,
                'description': description,
                'knowledge': learning.solution.title,
                'effectiveness_gain': learning.effectiveness_after - learning.effectiveness_before,
                'teacher': learning.teacher_agent.name,
                'student': learning.student_agent.name
            })

        return JsonResponse({
            'feed_items': feed_items,
            'total_count': len(feed_items),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


def _select_best_agent_for_query(query: str) -> Agent:
    """Select the most appropriate agent for a given query"""
    query_lower = query.lower()

    # Map query keywords to agent types
    if any(term in query_lower for term in ['job', 'career', 'employment', 'resume']):
        agent_names = ['Job Application Automator', 'Career Path Strategist', 'Resume Optimizer AI']
    elif any(term in query_lower for term in ['ai', 'machine learning', 'ml', 'deep learning']):
        agent_names = ['AI Model Trainer', 'Deep Learning Specialist', 'Data Scientist Pro']
    elif any(term in query_lower for term in ['market', 'business', 'revenue', 'growth']):
        agent_names = ['Market Research Analyst', 'Business Growth Architect', 'Revenue Stream Analyzer']
    elif any(term in query_lower for term in ['content', 'writing', 'blog', 'social']):
        agent_names = ['Content Strategy Planner', 'Blog Post Generator', 'Social Media Manager']
    elif any(term in query_lower for term in ['finance', 'investment', 'money', 'budget']):
        agent_names = ['Investment Portfolio Manager', 'Financial Advisor Bot', 'Budget Optimization Expert']
    else:
        # Default to general purpose agents
        agent_names = ['Income Builder Pro', 'Data Scientist Pro', 'Business Growth Architect']

    # Try to get one of the suggested agents
    for name in agent_names:
        try:
            return Agent.objects.get(name=name)
        except Agent.DoesNotExist:
            continue

    # Fallback to any agent
    return Agent.objects.first()


def _identify_knowledge_gaps(agent: Agent) -> List[str]:
    """Identify potential knowledge gaps for an agent"""
    gaps = []

    # Check solution diversity
    solution_types = agent.solutions.values_list('solution_type', flat=True).distinct()

    common_types = ['income', 'job_search', 'content', 'finance', 'automation', 'analytics']
    for type_name in common_types:
        if type_name not in solution_types:
            gaps.append(f"No expertise in {type_name}")

    # Check recent learning
    recent_learning = AgentLearning.objects.filter(
        student_agent=agent
    ).order_by('-id').first()

    if not recent_learning:
        gaps.append("No recent learning activities")

    # Check knowledge age (if we had timestamps)
    old_solutions = agent.solutions.filter(
        # Would filter by created_at if available
    ).count()

    if agent.solutions.count() < 10:
        gaps.append("Limited solution portfolio")

    return gaps[:5]  # Return top 5 gaps