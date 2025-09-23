"""
API endpoints for the Living AI Ecosystem visualization
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.models_unified_system import Agent, AgentSolution, AgentLearning, SpiderData
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import timedelta
import json
import random

@csrf_exempt
def get_ecosystem_stats(request):
    """Get real-time statistics for the AI ecosystem"""

    # Get real data from the database
    total_agents = Agent.objects.filter(is_active=True).count()
    total_solutions = AgentSolution.objects.count()
    total_learning = AgentLearning.objects.count()

    # Calculate recent activity
    last_hour = timezone.now() - timedelta(hours=1)
    recent_solutions = AgentSolution.objects.filter(created_at__gte=last_hour).count()
    recent_learning = AgentLearning.objects.filter(created_at__gte=last_hour).count()

    # Calculate collective IQ (based on average effectiveness)
    avg_effectiveness = AgentLearning.objects.aggregate(
        avg=Avg('effectiveness_improvement')
    )['avg'] or 0
    collective_iq = min(999, 500 + (avg_effectiveness * 100))

    # Calculate value created (based on solutions)
    value_per_solution = 15  # Average $15 per solution
    total_value = total_solutions * value_per_solution

    return JsonResponse({
        'stats': {
            'active_agents': total_agents,
            'knowledge_transfers': total_learning,
            'solutions': total_solutions,
            'collective_iq': round(collective_iq),
            'value_created': total_value,
            'recent_activity': {
                'solutions_per_min': round(recent_solutions / 60, 1),
                'learning_per_min': round(recent_learning / 60, 1),
                'value_per_hour': round(recent_solutions * value_per_solution, 0)
            }
        }
    })

@csrf_exempt
def get_live_learning_feed(request):
    """Get recent learning events for the live feed"""

    # Get recent learning events
    recent = timezone.now() - timedelta(minutes=5)
    recent_events = AgentLearning.objects.filter(
        created_at__gte=recent
    ).select_related('teacher_agent', 'student_agent').order_by('-created_at')[:20]

    feed_items = []

    for event in recent_events:
        # Calculate time ago
        time_diff = timezone.now() - event.created_at
        seconds_ago = int(time_diff.total_seconds())

        if seconds_ago < 60:
            time_str = f"{seconds_ago} seconds ago"
        elif seconds_ago < 3600:
            time_str = f"{seconds_ago // 60} minutes ago"
        else:
            time_str = f"{seconds_ago // 3600} hours ago"

        # Determine event type
        event_type = 'learning'
        if random.random() < 0.3:
            event_type = 'collaboration'
        elif random.random() < 0.2:
            event_type = 'solution'

        # Create feed item
        if event_type == 'learning':
            message = f"{event.teacher_agent.name} shared {event.learning_type} knowledge with {event.student_agent.name if event.student_agent else 'the network'}"
        elif event_type == 'collaboration':
            message = f"Multiple agents collaborating on {event.learning_type} optimization"
        else:
            message = f"New solution generated with {event.effectiveness_improvement:.1f}% improvement"

        feed_items.append({
            'type': event_type,
            'time': time_str,
            'message': message,
            'agents': [
                event.teacher_agent.name,
                event.student_agent.name if event.student_agent else 'Network'
            ],
            'effectiveness': event.effectiveness_improvement
        })

    return JsonResponse({'feed': feed_items})

@csrf_exempt
def get_agent_network(request):
    """Get the agent network structure for visualization"""

    agents = Agent.objects.filter(is_active=True)[:149]  # Limit to 149 for performance

    # Group agents by category
    categories = {
        'technical': [],
        'creative': [],
        'business': [],
        'analytics': []
    }

    for agent in agents:
        # Categorize based on specialization
        spec = agent.specialization.lower() if agent.specialization else ''

        if any(word in spec for word in ['developer', 'engineer', 'backend', 'frontend', 'devops', 'security', 'database']):
            category = 'technical'
        elif any(word in spec for word in ['writer', 'designer', 'creative', 'content', 'video', 'social']):
            category = 'creative'
        elif any(word in spec for word in ['business', 'sales', 'marketing', 'growth', 'revenue', 'finance']):
            category = 'business'
        else:
            category = 'analytics'

        categories[category].append({
            'id': agent.id,
            'name': agent.name,
            'specialization': agent.specialization,
            'solutions': AgentSolution.objects.filter(agent=agent).count(),
            'learning_events': AgentLearning.objects.filter(
                Q(teacher_agent=agent) | Q(student_agent=agent)
            ).count()
        })

    # Get connections (learning relationships)
    connections = []
    learning_pairs = AgentLearning.objects.values(
        'teacher_agent', 'student_agent'
    ).annotate(count=Count('id')).order_by('-count')[:200]

    for pair in learning_pairs:
        if pair['teacher_agent'] and pair['student_agent']:
            connections.append({
                'source': pair['teacher_agent'],
                'target': pair['student_agent'],
                'strength': min(1.0, pair['count'] / 10)  # Normalize strength
            })

    return JsonResponse({
        'agents': categories,
        'connections': connections,
        'total': agents.count()
    })

@csrf_exempt
def trigger_learning_event(request):
    """Trigger a new learning event (for demo purposes)"""

    if request.method == 'POST':
        # Get two random agents
        agents = list(Agent.objects.filter(is_active=True))
        if len(agents) >= 2:
            teacher = random.choice(agents)
            student = random.choice(agents)

            # Create learning event
            learning_event = AgentLearning.objects.create(
                teacher_agent=teacher,
                student_agent=student if student != teacher else None,
                learning_type=random.choice(['pattern_recognition', 'optimization', 'strategy', 'technique']),
                knowledge_gained={
                    'topic': random.choice(['API design', 'async patterns', 'ML optimization', 'UI/UX principles']),
                    'improvement': random.uniform(1, 10)
                },
                effectiveness_improvement=random.uniform(0.5, 5.0)
            )

            return JsonResponse({
                'success': True,
                'event': {
                    'teacher': teacher.name,
                    'student': student.name if student != teacher else 'Network',
                    'type': learning_event.learning_type,
                    'improvement': learning_event.effectiveness_improvement
                }
            })

    return JsonResponse({'success': False})