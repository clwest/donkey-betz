"""
Solution Explorer API Views
Provides comprehensive access to agent solutions, learning paths, and application interfaces
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging

from core.models_unified_system import (
    Agent, AgentSolution, AgentLearning,
    SpiderData
)

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def get_solutions(request):
    """Get paginated list of agent solutions with filtering"""
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        search = request.GET.get('search', '')
        agent_id = request.GET.get('agent_id')
        solution_type = request.GET.get('type')
        sort_by = request.GET.get('sort', '-created_at')

        # Build query
        solutions = AgentSolution.objects.select_related('agent')

        if search:
            solutions = solutions.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(agent__name__icontains=search)
            )

        if agent_id:
            solutions = solutions.filter(agent_id=agent_id)

        if solution_type:
            solutions = solutions.filter(solution_type=solution_type)

        # Apply sorting
        solutions = solutions.order_by(sort_by)

        # Paginate
        paginator = Paginator(solutions, page_size)
        page_obj = paginator.get_page(page)

        # Serialize solutions
        solutions_data = []
        for solution in page_obj:
            solutions_data.append({
                'id': str(solution.id),
                'title': solution.title,
                'description': solution.description,
                'solution_type': solution.solution_type,
                'agent': {
                    'id': str(solution.agent.id),
                    'name': solution.agent.name,
                    'specialty': solution.agent.specialization
                },
                'code_snippet': solution.code_snippet,
                'language': solution.language,
                'metrics': solution.metrics,
                'tags': solution.tags,
                'times_used': solution.times_used,
                'success_rate': solution.success_rate,
                'created_at': solution.created_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'solutions': solutions_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })

    except Exception as e:
        logger.error(f"Error fetching solutions: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_solution_detail(request, solution_id):
    """Get detailed information about a specific solution"""
    try:
        solution = AgentSolution.objects.select_related('agent').get(id=solution_id)

        # Get related learning paths
        learning_paths = AgentLearning.objects.filter(
            knowledge_acquired__contains=str(solution.id)
        ).select_related('teacher_agent', 'student_agent')[:5]

        # Get spider data that contributed to this solution
        # Session 807: Defer embedding fields to reduce egress costs
        spider_sources = SpiderData.objects.filter(
            processed=True,
            created_at__lte=solution.created_at,
            created_at__gte=solution.created_at - timedelta(hours=1)
        ).defer('embedding', 'item_embeddings', 'embedding_text')[:5]

        return JsonResponse({
            'success': True,
            'solution': {
                'id': str(solution.id),
                'title': solution.title,
                'description': solution.description,
                'solution_type': solution.solution_type,
                'agent': {
                    'id': str(solution.agent.id),
                    'name': solution.agent.name,
                    'specialty': solution.agent.specialization,
                    'description': solution.agent.description
                },
                'code_snippet': solution.code_snippet,
                'language': solution.language,
                'metrics': solution.metrics,
                'tags': solution.tags,
                'times_used': solution.times_used,
                'success_rate': solution.success_rate,
                'created_at': solution.created_at.isoformat(),
                'updated_at': solution.updated_at.isoformat()
            },
            'learning_paths': [
                {
                    'id': str(path.id),
                    'teacher': path.teacher_agent.name,
                    'student': path.student_agent.name if path.student_agent else 'System',
                    'topic': path.topic,
                    'created_at': path.created_at.isoformat()
                }
                for path in learning_paths
            ],
            'spider_sources': [
                {
                    'id': str(spider.id),
                    'spider_name': spider.spider_name,
                    'data_type': spider.data_type,
                    'source_url': spider.source_url,
                    'created_at': spider.created_at.isoformat()
                }
                for spider in spider_sources
            ]
        })

    except AgentSolution.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Solution not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error fetching solution detail: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def apply_solution(request, solution_id):
    """Apply a solution to user's context"""
    try:
        data = json.loads(request.body or b"{}")
        solution = AgentSolution.objects.get(id=solution_id)

        # Update usage metrics
        solution.times_used += 1
        solution.save()

        # Create application record (extend models if needed)
        application_context = {
            'user_context': data.get('context', {}),
            'parameters': data.get('parameters', {}),
            'timestamp': datetime.now().isoformat()
        }

        # Process the solution application (customize based on solution type)
        result = process_solution_application(solution, application_context)

        return JsonResponse({
            'success': True,
            'application_id': result.get('id'),
            'status': 'applied',
            'result': result.get('output'),
            'next_steps': result.get('next_steps', [])
        })

    except AgentSolution.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Solution not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error applying solution: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_data_flow(request):
    """Get complete data flow from spider to solution"""
    try:
        # Get recent spider data with solutions
        flows = []

        # Session 807: Defer embedding fields to reduce egress costs
        spider_data = SpiderData.objects.filter(
            processed=True
        ).defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')[:20]

        for spider in spider_data:
            # Find solutions created around the same time
            solutions = AgentSolution.objects.filter(
                created_at__gte=spider.created_at,
                created_at__lte=spider.created_at + timedelta(hours=1)
            ).select_related('agent')[:3]

            if solutions:
                flows.append({
                    'spider': {
                        'id': str(spider.id),
                        'name': spider.spider_name,
                        'type': spider.data_type,
                        'url': spider.source_url,
                        'created_at': spider.created_at.isoformat()
                    },
                    'agents': [
                        {
                            'id': str(sol.agent.id),
                            'name': sol.agent.name,
                            'specialty': sol.agent.specialization
                        }
                        for sol in solutions
                    ],
                    'solutions': [
                        {
                            'id': str(sol.id),
                            'title': sol.title,
                            'type': sol.solution_type,
                            'created_at': sol.created_at.isoformat()
                        }
                        for sol in solutions
                    ]
                })

        return JsonResponse({
            'success': True,
            'flows': flows,
            'total_spiders': SpiderData.objects.count(),
            'total_solutions': AgentSolution.objects.count(),
            'total_agents': Agent.objects.filter(is_active=True).count()
        })

    except Exception as e:
        logger.error(f"Error fetching data flow: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_learning_progress(request):
    """Get agent learning progress over time"""
    try:
        # Get time range
        days = int(request.GET.get('days', 7))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get learning metrics by day
        progress_data = []
        current_date = start_date

        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)

            day_learning = AgentLearning.objects.filter(
                created_at__gte=current_date,
                created_at__lt=next_date
            ).count()

            day_solutions = AgentSolution.objects.filter(
                created_at__gte=current_date,
                created_at__lt=next_date
            ).count()

            progress_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'learning_events': day_learning,
                'solutions_created': day_solutions
            })

            current_date = next_date

        # Get top learning agents
        top_teachers = Agent.objects.annotate(
            teaching_count=Count('teachings')
        ).order_by('-teaching_count')[:5]

        top_learners = Agent.objects.annotate(
            learning_count=Count('learnings')
        ).order_by('-learning_count')[:5]

        return JsonResponse({
            'success': True,
            'progress': progress_data,
            'summary': {
                'total_learning_events': AgentLearning.objects.count(),
                'total_solutions': AgentSolution.objects.count(),
                'active_agents': Agent.objects.filter(is_active=True).count(),
                'avg_success_rate': AgentSolution.objects.aggregate(
                    Avg('success_rate'))['success_rate__avg'] or 0
            },
            'top_teachers': [
                {
                    'id': str(agent.id),
                    'name': agent.name,
                    'teaching_count': agent.teaching_count
                }
                for agent in top_teachers
            ],
            'top_learners': [
                {
                    'id': str(agent.id),
                    'name': agent.name,
                    'learning_count': agent.learning_count
                }
                for agent in top_learners
            ]
        })

    except Exception as e:
        logger.error(f"Error fetching learning progress: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def personalize_learning(request):
    """Get personalized learning recommendations based on user context"""
    try:
        data = json.loads(request.body or b"{}")
        user_interests = data.get('interests', [])
        user_skills = data.get('skills', [])
        user_goals = data.get('goals', [])

        # Find relevant agents
        relevant_agents = Agent.objects.filter(
            Q(specialization__in=user_interests) |
            Q(tags__overlap=user_skills) if hasattr(Agent, 'tags') else Q()
        ).distinct()[:10]

        # Find relevant solutions
        relevant_solutions = AgentSolution.objects.filter(
            Q(tags__overlap=user_interests) |
            Q(tags__overlap=user_goals) |
            Q(agent__in=relevant_agents)
        ).distinct().order_by('-success_rate', '-times_used')[:20]

        # Find learning paths
        learning_paths = AgentLearning.objects.filter(
            Q(topic__in=user_interests) |
            Q(teacher_agent__in=relevant_agents)
        ).order_by('-created_at')[:10]

        return JsonResponse({
            'success': True,
            'personalized': {
                'recommended_agents': [
                    {
                        'id': str(agent.id),
                        'name': agent.name,
                        'specialty': agent.specialization,
                        'match_reason': 'Matches your interests'
                    }
                    for agent in relevant_agents
                ],
                'recommended_solutions': [
                    {
                        'id': str(sol.id),
                        'title': sol.title,
                        'description': sol.description,
                        'relevance_score': calculate_relevance(sol, user_interests, user_goals)
                    }
                    for sol in relevant_solutions
                ],
                'learning_paths': [
                    {
                        'id': str(path.id),
                        'topic': path.topic,
                        'teacher': path.teacher_agent.name,
                        'difficulty': path.difficulty_level
                    }
                    for path in learning_paths
                ]
            }
        })

    except Exception as e:
        logger.error(f"Error personalizing learning: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def process_solution_application(solution, context):
    """Process the application of a solution"""
    # This would be extended based on solution types
    return {
        'id': str(solution.id) + '_applied',
        'output': f"Applied {solution.title} with context",
        'next_steps': [
            'Monitor results',
            'Provide feedback',
            'Explore related solutions'
        ]
    }


def calculate_relevance(solution, interests, goals):
    """Calculate relevance score for a solution"""
    score = 0
    solution_tags = solution.tags or []

    for interest in interests:
        if interest in solution_tags:
            score += 10
        if interest.lower() in solution.description.lower():
            score += 5

    for goal in goals:
        if goal in solution_tags:
            score += 15
        if goal.lower() in solution.title.lower():
            score += 10

    # Factor in success metrics
    score += solution.success_rate * 10
    score += min(solution.times_used / 10, 10)

    return min(score, 100)