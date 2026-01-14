"""
Agent Evolution API Views - Session 254

XP system for agents - they gain experience and level up!
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Count, F, Max

from .models_unified_system import (
    AgentEvolution, AgentAbility, XPHistory, LevelMilestone, Agent
)


# =============================================================================
# EVOLUTION OVERVIEW
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_evolution_overview(request):
    """Get overview of all agent evolution status."""
    try:
        # Get all agents with evolution data
        evolutions = AgentEvolution.objects.select_related('agent').all()

        # Calculate stats
        total_agents = Agent.objects.filter(is_active=True).count()
        evolved_agents = evolutions.count()

        # Level distribution
        level_distribution = {}
        for i in range(1, 11):
            level_distribution[str(i)] = evolutions.filter(current_level=i).count()

        # Total XP across all agents
        total_xp = evolutions.aggregate(Sum('total_xp'))['total_xp__sum'] or 0
        lifetime_xp = evolutions.aggregate(Sum('lifetime_xp'))['lifetime_xp__sum'] or 0

        # Prestige stats
        total_prestiges = evolutions.aggregate(Sum('prestige_level'))['prestige_level__sum'] or 0
        max_prestige = evolutions.aggregate(max_prestige=Max('prestige_level'))['max_prestige'] or 0

        # Top evolved agents
        top_agents = []
        for evo in evolutions.order_by('-current_level', '-total_xp')[:10]:
            top_agents.append({
                'agent_id': str(evo.agent.id),
                'agent_name': evo.agent.name,
                'level': evo.current_level,
                'level_title': evo.get_title(),
                'total_xp': evo.total_xp,
                'prestige': evo.prestige_level,
                'abilities_count': evo.abilities.filter(is_active=True).count()
            })

        # Recent level ups
        recent_milestones = []
        for milestone in LevelMilestone.objects.select_related('agent').order_by('-achieved_at')[:10]:
            recent_milestones.append({
                'agent_name': milestone.agent.name,
                'level': milestone.level_reached,
                'title': milestone.title_earned,
                'achieved_at': milestone.achieved_at.isoformat()
            })

        # XP sources breakdown
        xp_sources = XPHistory.objects.values('source').annotate(
            total=Sum('xp_amount'),
            count=Count('id')
        ).order_by('-total')[:10]

        return JsonResponse({
            'success': True,
            'overview': {
                'total_agents': total_agents,
                'evolved_agents': evolved_agents,
                'total_xp': total_xp,
                'lifetime_xp': lifetime_xp,
                'total_prestiges': total_prestiges,
                'max_prestige': max_prestige,
                'level_distribution': level_distribution
            },
            'top_agents': top_agents,
            'recent_milestones': recent_milestones,
            'xp_sources': list(xp_sources)
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# AGENT EVOLUTION DETAIL
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_agent_evolution(request, agent_id):
    """Get detailed evolution data for a specific agent."""
    try:
        agent = Agent.objects.get(id=agent_id)

        # Get or create evolution record
        evolution, created = AgentEvolution.objects.get_or_create(agent=agent)

        # Get abilities (tied to this evolution)
        abilities = []
        for ability in evolution.abilities.all():
            abilities.append({
                'id': str(ability.id),
                'ability_code': ability.ability_code,
                'ability_name': ability.ability_name,
                'description': ability.description,
                'is_active': ability.is_active,
                'is_upgraded': ability.is_upgraded,
                'upgrade_level': ability.upgrade_level,
                'unlocked_at': ability.unlocked_at.isoformat()
            })

        # Get XP history (from agent, not evolution)
        xp_history = []
        for xp in agent.xp_history.order_by('-created_at')[:20]:
            xp_history.append({
                'amount': xp.xp_amount,
                'source': xp.source,
                'details': xp.details,
                'created_at': xp.created_at.isoformat()
            })

        # Get milestones (from agent, not evolution)
        milestones = []
        for milestone in agent.level_milestones.order_by('-level_reached'):
            milestones.append({
                'level': milestone.level_reached,
                'title': milestone.title_earned,
                'achieved_at': milestone.achieved_at.isoformat(),
                'abilities_unlocked': milestone.abilities_unlocked
            })

        return JsonResponse({
            'success': True,
            'agent': {
                'id': str(agent.id),
                'name': agent.name,
                'specialty': agent.specialty
            },
            'evolution': {
                'current_level': evolution.current_level,
                'level_title': evolution.get_title(),
                'total_xp': evolution.total_xp,
                'xp_to_next_level': evolution.xp_to_next_level,
                'progress_percent': evolution.progress_percent,
                'speed_bonus': evolution.speed_bonus,
                'quality_bonus': evolution.quality_bonus,
                'creativity_bonus': evolution.creativity_bonus,
                'efficiency_bonus': evolution.efficiency_bonus,
                'prestige_level': evolution.prestige_level,
                'lifetime_xp': evolution.lifetime_xp,
                'tasks_completed': evolution.tasks_completed,
                'tasks_failed': evolution.tasks_failed,
                'created_at': evolution.created_at.isoformat()
            },
            'abilities': abilities,
            'xp_history': xp_history,
            'milestones': milestones
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# AWARD XP
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def award_agent_xp(request, agent_id):
    """Award XP to an agent."""
    try:
        data = json.loads(request.body) if request.body else {}

        amount = data.get('amount', 10)
        source = data.get('source', 'manual')
        details = data.get('details', '')

        if amount <= 0:
            return JsonResponse({'success': False, 'error': 'Amount must be positive'}, status=400)

        agent = Agent.objects.get(id=agent_id)
        evolution, created = AgentEvolution.objects.get_or_create(agent=agent)

        # Award the XP
        result = evolution.award_xp(amount, source, details)

        return JsonResponse({
            'success': True,
            'agent_name': agent.name,
            'xp_awarded': amount,
            'new_total_xp': evolution.total_xp,
            'current_level': evolution.current_level,
            'level_title': evolution.get_title(),
            'leveled_up': result.get('leveled_up', False),
            'new_level': result.get('new_level'),
            'abilities_unlocked': result.get('abilities_unlocked', [])
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# PRESTIGE
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def prestige_agent(request, agent_id):
    """Prestige a max-level agent."""
    try:
        agent = Agent.objects.get(id=agent_id)
        evolution = AgentEvolution.objects.get(agent=agent)

        # Check if at max level
        if evolution.current_level < 10:
            return JsonResponse({
                'success': False,
                'error': f'Agent must be level 10 to prestige. Currently level {evolution.current_level}'
            }, status=400)

        # Perform prestige
        evolution.prestige()

        return JsonResponse({
            'success': True,
            'agent_name': agent.name,
            'prestige_level': evolution.prestige_level,
            'current_level': evolution.current_level,
            'message': f'{agent.name} has reached Prestige {evolution.prestige_level}!'
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except AgentEvolution.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent has no evolution record'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# ABILITIES
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_available_abilities(request):
    """Get all abilities that can be unlocked."""
    try:
        # Return the default ability templates
        default_abilities = [
            {'ability_code': 'enhanced_focus', 'ability_name': 'Enhanced Focus', 'description': 'Gains 10% bonus XP from all sources', 'unlock_level': 2},
            {'ability_code': 'parallel_processing', 'ability_name': 'Parallel Processing', 'description': 'Completes tasks 5% faster', 'unlock_level': 3},
            {'ability_code': 'quality_surge', 'ability_name': 'Quality Surge', 'description': '10% higher quality output', 'unlock_level': 4},
            {'ability_code': 'creative_spark', 'ability_name': 'Creative Spark', 'description': '15% more creative solutions', 'unlock_level': 5},
            {'ability_code': 'multi_tasker', 'ability_name': 'Multi-tasker', 'description': 'Can handle 2 tasks simultaneously', 'unlock_level': 6},
            {'ability_code': 'deep_analysis', 'ability_name': 'Deep Analysis', 'description': '20% better research results', 'unlock_level': 7},
            {'ability_code': 'synergy_boost', 'ability_name': 'Synergy Boost', 'description': '25% bonus when working with others', 'unlock_level': 8},
            {'ability_code': 'mentor_mode', 'ability_name': 'Mentor Mode', 'description': '30% improved specialty performance', 'unlock_level': 9},
            {'ability_code': 'transcendence', 'ability_name': 'Transcendence', 'description': 'Can mentor other agents for bonus XP', 'unlock_level': 10}
        ]

        return JsonResponse({
            'success': True,
            'abilities': default_abilities,
            'total': len(default_abilities)
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_ability(request):
    """Create a new ability for a specific agent."""
    try:
        data = json.loads(request.body) if request.body else {}

        agent_id = data.get('agent_id')
        ability_code = data.get('ability_code')
        ability_name = data.get('ability_name')
        description = data.get('description', '')

        if not agent_id or not ability_code:
            return JsonResponse({'success': False, 'error': 'agent_id and ability_code required'}, status=400)

        agent = Agent.objects.get(id=agent_id)
        evolution = AgentEvolution.objects.get(agent=agent)

        # Check if ability already exists
        if evolution.abilities.filter(ability_code=ability_code).exists():
            return JsonResponse({'success': False, 'error': 'Agent already has this ability'}, status=400)

        ability = AgentAbility.objects.create(
            evolution=evolution,
            ability_code=ability_code,
            ability_name=ability_name or ability_code.replace('_', ' ').title(),
            description=description
        )

        return JsonResponse({
            'success': True,
            'ability': {
                'id': str(ability.id),
                'ability_code': ability.ability_code,
                'ability_name': ability.ability_name,
                'description': ability.description
            }
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except AgentEvolution.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent has no evolution record'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def unlock_ability(request, agent_id, ability_id):
    """Toggle an ability's active status."""
    try:
        agent = Agent.objects.get(id=agent_id)
        evolution = AgentEvolution.objects.get(agent=agent)
        ability = AgentAbility.objects.get(id=ability_id, evolution=evolution)

        # Toggle active status
        ability.is_active = not ability.is_active
        ability.save()

        return JsonResponse({
            'success': True,
            'agent_name': agent.name,
            'ability_name': ability.ability_name,
            'is_active': ability.is_active,
            'message': f'{ability.ability_name} is now {"active" if ability.is_active else "inactive"}!'
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except AgentEvolution.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent has no evolution record'}, status=404)
    except AgentAbility.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Ability not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# XP LEADERBOARD
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_xp_leaderboard(request):
    """Get XP leaderboard across all agents."""
    try:
        limit = int(request.GET.get('limit', 20))

        evolutions = AgentEvolution.objects.select_related('agent').prefetch_related('abilities').order_by(
            '-current_level', '-total_xp'
        )[:limit]

        leaderboard = []
        for rank, evo in enumerate(evolutions, 1):
            # Session 747: Calculate XP progress within current level
            xp_to_next = evo.calculate_xp_for_level(evo.current_level + 1) - evo.calculate_xp_for_level(evo.current_level)
            xp_in_current_level = evo.total_xp - evo.calculate_xp_for_level(evo.current_level)

            # Get unlocked abilities
            abilities_unlocked = list(evo.abilities.filter(is_active=True).values_list('ability_name', flat=True))

            leaderboard.append({
                'id': str(evo.id),  # Session 747: Add id field
                'rank': rank,
                'agent_id': str(evo.agent.id),
                'agent_name': evo.agent.name,
                'level': evo.current_level,
                'level_title': evo.get_title(),
                'xp': xp_in_current_level,  # Session 747: XP progress in current level
                'xp_to_next_level': xp_to_next,  # Session 747: XP needed for next level
                'total_xp': evo.total_xp,
                'lifetime_xp': evo.lifetime_xp,
                'prestige_level': evo.prestige_level,  # Session 747: Renamed from 'prestige'
                'abilities_unlocked': abilities_unlocked,  # Session 747: List of unlocked ability names
                'tasks_completed': evo.tasks_completed,
                'tasks_failed': evo.tasks_failed,
                'success_rate': round(
                    (evo.tasks_completed - evo.tasks_failed) / max(evo.tasks_completed, 1) * 100, 1
                ) if evo.tasks_completed > 0 else 100.0,
                'created_at': evo.created_at.isoformat() if evo.created_at else None,
                'updated_at': evo.updated_at.isoformat() if evo.updated_at else None,
            })

        return JsonResponse({
            'success': True,
            'leaderboard': leaderboard
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_recent_xp_gains(request):
    """Get recent XP gains across all agents."""
    try:
        limit = int(request.GET.get('limit', 50))

        xp_gains = XPHistory.objects.select_related('agent').order_by('-created_at')[:limit]

        gains = []
        for xp in xp_gains:
            gains.append({
                'id': str(xp.id),  # Session 747: Add id field
                'agent_name': xp.agent.name,
                'xp_amount': xp.xp_amount,  # Session 747: Renamed from 'amount'
                'reason': xp.source,  # Session 747: Renamed from 'source' to match frontend
                'details': xp.details,
                'recorded_at': xp.created_at.isoformat()  # Session 747: Renamed from 'created_at'
            })

        return JsonResponse({
            'success': True,
            'xp_gains': gains
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# INITIALIZE EVOLUTION FOR ALL AGENTS
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def initialize_all_evolutions(request):
    """Initialize evolution records for all active agents."""
    try:
        agents = Agent.objects.filter(is_active=True)

        created_count = 0
        existing_count = 0

        for agent in agents:
            evolution, created = AgentEvolution.objects.get_or_create(agent=agent)
            if created:
                created_count += 1
            else:
                existing_count += 1

        return JsonResponse({
            'success': True,
            'message': 'Evolution system initialized',
            'agents_created': created_count,
            'agents_existing': existing_count,
            'total_agents': created_count + existing_count
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# RECORD TASK COMPLETION (for XP awards)
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def record_task_completion(request, agent_id):
    """Record a task completion for an agent (awards XP based on success)."""
    try:
        data = json.loads(request.body) if request.body else {}

        success = data.get('success', True)
        task_type = data.get('task_type', 'general')
        complexity = data.get('complexity', 1.0)  # 0.5 to 2.0
        details = data.get('details', '')

        agent = Agent.objects.get(id=agent_id)
        evolution, _ = AgentEvolution.objects.get_or_create(agent=agent)

        # Update task counters
        evolution.tasks_completed = F('tasks_completed') + 1
        if not success:
            evolution.tasks_failed = F('tasks_failed') + 1
        evolution.save()
        evolution.refresh_from_db()

        # Calculate XP award
        base_xp = 10 if success else 2  # Less XP for failed tasks
        complexity_multiplier = max(0.5, min(2.0, complexity))

        # Task type bonuses
        task_type_bonuses = {
            'research': 1.2,
            'generation': 1.1,
            'analysis': 1.3,
            'collaboration': 1.5,
            'learning': 2.0,
            'general': 1.0
        }
        type_multiplier = task_type_bonuses.get(task_type, 1.0)

        # Calculate final XP
        final_xp = int(base_xp * complexity_multiplier * type_multiplier)

        # Award XP
        result = evolution.award_xp(
            final_xp,
            f'task_{task_type}',
            f"{'Completed' if success else 'Attempted'}: {details}"
        )

        return JsonResponse({
            'success': True,
            'agent_name': agent.name,
            'task_success': success,
            'xp_awarded': final_xp,
            'tasks_completed': evolution.tasks_completed,
            'tasks_failed': evolution.tasks_failed,
            'current_level': evolution.current_level,
            'leveled_up': result.get('leveled_up', False),
            'new_level': result.get('new_level'),
            'abilities_unlocked': result.get('abilities_unlocked', [])
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
