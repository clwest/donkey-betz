"""
Session 256: Agent Personality API Views

Provides API endpoints for the Agent Personality System:
- Get personality overview (all agents with personalities)
- Get specific agent personality
- Create/update personality for an agent
- Generate personality based on agent specialization
- Get compatibility between agents based on personality
"""

import json
import random
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from core.models_unified_system import Agent, AgentPersonality

logger = logging.getLogger(__name__)


# =============================================================================
# PERSONALITY TYPE PRESETS (Based on Agent Specializations)
# =============================================================================

PERSONALITY_PRESETS = {
    'research': {
        'type_code': 'INTJ',
        'traits': {'formality': 0.7, 'verbosity': 0.8, 'humor': 0.2, 'assertiveness': 0.6,
                   'leadership': 0.4, 'team_orientation': 0.5, 'teaching_tendency': 0.7, 'competitiveness': 0.3,
                   'risk_appetite': 0.3, 'creativity': 0.6, 'patience': 0.8, 'perfectionism': 0.7},
        'archetype': 'analyst'
    },
    'creative': {
        'type_code': 'ENFP',
        'traits': {'formality': 0.3, 'verbosity': 0.6, 'humor': 0.7, 'assertiveness': 0.5,
                   'leadership': 0.5, 'team_orientation': 0.7, 'teaching_tendency': 0.6, 'competitiveness': 0.3,
                   'risk_appetite': 0.8, 'creativity': 0.9, 'patience': 0.4, 'perfectionism': 0.4},
        'archetype': 'visionary'
    },
    'technical': {
        'type_code': 'ISTP',
        'traits': {'formality': 0.5, 'verbosity': 0.4, 'humor': 0.3, 'assertiveness': 0.5,
                   'leadership': 0.4, 'team_orientation': 0.4, 'teaching_tendency': 0.5, 'competitiveness': 0.4,
                   'risk_appetite': 0.5, 'creativity': 0.5, 'patience': 0.7, 'perfectionism': 0.8},
        'archetype': 'explorer'
    },
    'leadership': {
        'type_code': 'ENTJ',
        'traits': {'formality': 0.7, 'verbosity': 0.5, 'humor': 0.3, 'assertiveness': 0.9,
                   'leadership': 0.9, 'team_orientation': 0.7, 'teaching_tendency': 0.6, 'competitiveness': 0.7,
                   'risk_appetite': 0.7, 'creativity': 0.5, 'patience': 0.4, 'perfectionism': 0.6},
        'archetype': 'commander'
    },
    'support': {
        'type_code': 'ISFJ',
        'traits': {'formality': 0.5, 'verbosity': 0.5, 'humor': 0.4, 'assertiveness': 0.3,
                   'leadership': 0.3, 'team_orientation': 0.8, 'teaching_tendency': 0.7, 'competitiveness': 0.2,
                   'risk_appetite': 0.3, 'creativity': 0.4, 'patience': 0.9, 'perfectionism': 0.7},
        'archetype': 'sentinel'
    },
    'strategy': {
        'type_code': 'INTP',
        'traits': {'formality': 0.6, 'verbosity': 0.7, 'humor': 0.4, 'assertiveness': 0.5,
                   'leadership': 0.5, 'team_orientation': 0.4, 'teaching_tendency': 0.6, 'competitiveness': 0.4,
                   'risk_appetite': 0.6, 'creativity': 0.8, 'patience': 0.6, 'perfectionism': 0.6},
        'archetype': 'analyst'
    },
    'communication': {
        'type_code': 'ENFJ',
        'traits': {'formality': 0.5, 'verbosity': 0.7, 'humor': 0.6, 'assertiveness': 0.6,
                   'leadership': 0.7, 'team_orientation': 0.9, 'teaching_tendency': 0.8, 'competitiveness': 0.2,
                   'risk_appetite': 0.5, 'creativity': 0.6, 'patience': 0.7, 'perfectionism': 0.5},
        'archetype': 'advocate'
    },
    'default': {
        'type_code': 'ENTJ',
        'traits': {'formality': 0.5, 'verbosity': 0.5, 'humor': 0.3, 'assertiveness': 0.5,
                   'leadership': 0.5, 'team_orientation': 0.5, 'teaching_tendency': 0.5, 'competitiveness': 0.3,
                   'risk_appetite': 0.5, 'creativity': 0.5, 'patience': 0.5, 'perfectionism': 0.5},
        'archetype': 'analyst'
    }
}


def get_preset_for_agent(agent):
    """Get personality preset based on agent's specialization/type."""
    specialization = agent.specialization.lower() if agent.specialization else ''
    agent_type = agent.agent_type.lower() if agent.agent_type else ''
    name = agent.name.lower()

    # Match based on keywords
    if any(kw in specialization or kw in name for kw in ['research', 'analysis', 'investigation']):
        return PERSONALITY_PRESETS['research']
    elif any(kw in specialization or kw in name for kw in ['creative', 'image', 'video', 'art', 'design']):
        return PERSONALITY_PRESETS['creative']
    elif any(kw in specialization or kw in name for kw in ['tech', '3d', 'generation', 'audio']):
        return PERSONALITY_PRESETS['technical']
    elif any(kw in specialization or kw in name for kw in ['orchestration', 'cto', 'coo', 'director', 'coordinator']):
        return PERSONALITY_PRESETS['leadership']
    elif any(kw in specialization or kw in name for kw in ['support', 'assistant', 'helper']):
        return PERSONALITY_PRESETS['support']
    elif any(kw in specialization or kw in name for kw in ['strategy', 'seo', 'content']):
        return PERSONALITY_PRESETS['strategy']
    elif any(kw in specialization or kw in name for kw in ['social', 'brand', 'communication']):
        return PERSONALITY_PRESETS['communication']
    else:
        return PERSONALITY_PRESETS['default']


# =============================================================================
# API ENDPOINTS
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def personality_overview(request):
    """
    GET /api/personality/
    Get overview of all agent personalities.
    """
    try:
        agents = Agent.objects.filter(is_active=True).prefetch_related('personality')

        agents_data = []
        personality_count = 0
        archetype_counts = {}

        for agent in agents:
            agent_data = {
                'id': str(agent.id),
                'name': agent.name,
                'agent_type': agent.agent_type,
                'specialization': agent.specialization,
                'has_personality': hasattr(agent, 'personality') and agent.personality is not None,
                'personality': None
            }

            try:
                if agent.personality:
                    personality_count += 1
                    archetype = agent.personality.archetype
                    archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
                    agent_data['personality'] = {
                        'type_code': agent.personality.get_type_code(),
                        'archetype': archetype,
                        'archetype_display': agent.personality.get_archetype_display(),
                        'emoji': agent.personality.get_personality_emoji(),
                        'color': agent.personality.get_personality_color(),
                    }
            except AgentPersonality.DoesNotExist:
                pass

            agents_data.append(agent_data)

        return JsonResponse({
            'success': True,
            'stats': {
                'total_agents': len(agents_data),
                'with_personality': personality_count,
                'without_personality': len(agents_data) - personality_count,
                'archetype_distribution': archetype_counts
            },
            'agents': agents_data
        })

    except Exception as e:
        logger.error(f"Error in personality_overview: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST", "PUT"])
def agent_personality(request, agent_id):
    """
    GET /api/personality/agent/<agent_id>/
    Get personality for a specific agent.

    POST /api/personality/agent/<agent_id>/
    Create or update personality for an agent.
    """
    try:
        agent = Agent.objects.get(id=agent_id)
    except Agent.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Agent {agent_id} not found'
        }, status=404)

    if request.method == 'GET':
        try:
            personality = agent.personality
            return JsonResponse({
                'success': True,
                'personality': personality.to_dict()
            })
        except AgentPersonality.DoesNotExist:
            return JsonResponse({
                'success': False,
                'has_personality': False,
                'agent': {
                    'id': str(agent.id),
                    'name': agent.name,
                    'agent_type': agent.agent_type,
                    'specialization': agent.specialization
                },
                'suggested_preset': get_preset_for_agent(agent)
            })

    elif request.method in ['POST', 'PUT']:
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = {}

        with transaction.atomic():
            personality, created = AgentPersonality.objects.get_or_create(
                agent=agent,
                defaults={}
            )

            # Update dimensions if provided
            if 'energy_direction' in data:
                personality.energy_direction = data['energy_direction']
            if 'information_processing' in data:
                personality.information_processing = data['information_processing']
            if 'decision_making' in data:
                personality.decision_making = data['decision_making']
            if 'work_style' in data:
                personality.work_style = data['work_style']

            # Update traits if provided
            traits = data.get('traits', {})
            for trait_category in ['communication', 'collaboration', 'decision']:
                if trait_category in traits:
                    for trait, value in traits[trait_category].items():
                        if hasattr(personality, trait):
                            setattr(personality, trait, float(value))

            # Update custom traits
            if 'custom_traits' in data:
                personality.custom_traits = data['custom_traits']

            personality.save()

            return JsonResponse({
                'success': True,
                'created': created,
                'personality': personality.to_dict()
            })

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
@require_http_methods(["POST"])
def generate_personality(request, agent_id):
    """
    POST /api/personality/agent/<agent_id>/generate/
    Generate personality for an agent based on their specialization.
    """
    try:
        agent = Agent.objects.get(id=agent_id)
    except Agent.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Agent {agent_id} not found'
        }, status=404)

    preset = get_preset_for_agent(agent)

    # Add some randomness for uniqueness
    def add_variation(value, variance=0.1):
        return max(0.0, min(1.0, value + random.uniform(-variance, variance)))

    with transaction.atomic():
        personality, created = AgentPersonality.objects.get_or_create(
            agent=agent
        )

        # Set type dimensions from preset
        type_code = preset['type_code']
        personality.energy_direction = type_code[0]
        personality.information_processing = type_code[1]
        personality.decision_making = type_code[2]
        personality.work_style = type_code[3]

        # Set traits with slight variation for uniqueness
        traits = preset['traits']
        personality.formality = add_variation(traits['formality'])
        personality.verbosity = add_variation(traits['verbosity'])
        personality.humor = add_variation(traits['humor'])
        personality.assertiveness = add_variation(traits['assertiveness'])
        personality.leadership = add_variation(traits['leadership'])
        personality.team_orientation = add_variation(traits['team_orientation'])
        personality.teaching_tendency = add_variation(traits['teaching_tendency'])
        personality.competitiveness = add_variation(traits['competitiveness'])
        personality.risk_appetite = add_variation(traits['risk_appetite'])
        personality.creativity = add_variation(traits['creativity'])
        personality.patience = add_variation(traits['patience'])
        personality.perfectionism = add_variation(traits['perfectionism'])

        personality.save()

        return JsonResponse({
            'success': True,
            'created': created,
            'message': f"Generated {personality.get_type_code()} personality for {agent.name}",
            'personality': personality.to_dict()
        })


@csrf_exempt
@require_http_methods(["POST"])
def generate_all_personalities(request):
    """
    POST /api/personality/generate-all/
    Generate personalities for all agents that don't have one.
    """
    try:
        agents_without_personality = []
        for agent in Agent.objects.filter(is_active=True):
            try:
                _ = agent.personality
            except AgentPersonality.DoesNotExist:
                agents_without_personality.append(agent)

        generated = []
        for agent in agents_without_personality:
            preset = get_preset_for_agent(agent)

            def add_variation(value, variance=0.1):
                return max(0.0, min(1.0, value + random.uniform(-variance, variance)))

            personality = AgentPersonality.objects.create(
                agent=agent,
                energy_direction=preset['type_code'][0],
                information_processing=preset['type_code'][1],
                decision_making=preset['type_code'][2],
                work_style=preset['type_code'][3],
                formality=add_variation(preset['traits']['formality']),
                verbosity=add_variation(preset['traits']['verbosity']),
                humor=add_variation(preset['traits']['humor']),
                assertiveness=add_variation(preset['traits']['assertiveness']),
                leadership=add_variation(preset['traits']['leadership']),
                team_orientation=add_variation(preset['traits']['team_orientation']),
                teaching_tendency=add_variation(preset['traits']['teaching_tendency']),
                competitiveness=add_variation(preset['traits']['competitiveness']),
                risk_appetite=add_variation(preset['traits']['risk_appetite']),
                creativity=add_variation(preset['traits']['creativity']),
                patience=add_variation(preset['traits']['patience']),
                perfectionism=add_variation(preset['traits']['perfectionism']),
            )

            generated.append({
                'agent_id': str(agent.id),
                'agent_name': agent.name,
                'type_code': personality.get_type_code(),
                'archetype': personality.archetype
            })

        return JsonResponse({
            'success': True,
            'message': f"Generated personalities for {len(generated)} agents",
            'generated': generated
        })

    except Exception as e:
        logger.error(f"Error in generate_all_personalities: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def personality_compatibility(request, agent1_id, agent2_id):
    """
    GET /api/personality/compatibility/<agent1_id>/<agent2_id>/
    Calculate personality compatibility between two agents.
    """
    try:
        agent1 = Agent.objects.get(id=agent1_id)
        agent2 = Agent.objects.get(id=agent2_id)
    except Agent.DoesNotExist as e:
        return JsonResponse({
            'success': False,
            'error': f'Agent not found: {e}'
        }, status=404)

    try:
        p1 = agent1.personality
        p2 = agent2.personality
    except AgentPersonality.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'One or both agents do not have a personality profile'
        }, status=400)

    # Calculate compatibility based on complementary traits
    # High compatibility when agents have complementary rather than identical traits

    # Leadership compatibility (one leader, one supporter)
    leadership_compat = 1 - abs(p1.leadership - (1 - p2.leadership))

    # Team orientation (both should be team-oriented for good collaboration)
    team_compat = (p1.team_orientation + p2.team_orientation) / 2

    # Communication style similarity (similar formality works better)
    comm_compat = 1 - abs(p1.formality - p2.formality)

    # Complementary energy (introverts and extroverts balance)
    energy_compat = 0.7 if p1.energy_direction != p2.energy_direction else 0.5

    # Similar patience levels help
    patience_compat = 1 - abs(p1.patience - p2.patience)

    # Overall compatibility score
    overall = (
        leadership_compat * 0.2 +
        team_compat * 0.25 +
        comm_compat * 0.2 +
        energy_compat * 0.15 +
        patience_compat * 0.2
    )

    # Determine compatibility level
    if overall >= 0.75:
        level = 'excellent'
        description = 'These agents work exceptionally well together'
    elif overall >= 0.6:
        level = 'good'
        description = 'These agents collaborate effectively'
    elif overall >= 0.45:
        level = 'moderate'
        description = 'These agents can work together with some adjustments'
    else:
        level = 'challenging'
        description = 'These agents may have communication challenges'

    return JsonResponse({
        'success': True,
        'compatibility': {
            'overall_score': round(overall, 2),
            'level': level,
            'description': description,
            'breakdown': {
                'leadership_balance': round(leadership_compat, 2),
                'team_orientation': round(team_compat, 2),
                'communication_style': round(comm_compat, 2),
                'energy_balance': round(energy_compat, 2),
                'patience_alignment': round(patience_compat, 2)
            }
        },
        'agents': [
            {
                'id': str(agent1.id),
                'name': agent1.name,
                'type_code': p1.get_type_code(),
                'archetype': p1.archetype
            },
            {
                'id': str(agent2.id),
                'name': agent2.name,
                'type_code': p2.get_type_code(),
                'archetype': p2.archetype
            }
        ]
    })


@csrf_exempt
@require_http_methods(["GET"])
def personality_archetypes(request):
    """
    GET /api/personality/archetypes/
    Get all personality archetypes and their descriptions.
    """
    archetypes = [
        {
            'id': 'analyst',
            'name': 'The Analyst',
            'emoji': '\U0001F9E0',  # Brain
            'color': '#6366f1',
            'description': 'Deep thinker and strategic planner. Excels at research and complex problem-solving.',
            'type_codes': ['INTJ', 'INTP'],
            'strengths': ['Strategic thinking', 'Research', 'Analysis', 'Problem-solving'],
            'best_roles': ['Research Agent', 'Strategy Agent', 'Analysis Agent']
        },
        {
            'id': 'diplomat',
            'name': 'The Diplomat',
            'emoji': '\U0001F54A\uFE0F',  # Dove
            'color': '#8b5cf6',
            'description': 'Harmonizer and idealist. Builds consensus and maintains positive relationships.',
            'type_codes': ['INFJ', 'INFP'],
            'strengths': ['Empathy', 'Mediation', 'Vision', 'Inspiration'],
            'best_roles': ['Communication Agent', 'Brand Agent', 'Social Agent']
        },
        {
            'id': 'sentinel',
            'name': 'The Sentinel',
            'emoji': '\U0001F6E1\uFE0F',  # Shield
            'color': '#64748b',
            'description': 'Reliable and detail-oriented. Ensures quality and consistency.',
            'type_codes': ['ISTJ', 'ISFJ'],
            'strengths': ['Reliability', 'Attention to detail', 'Organization', 'Follow-through'],
            'best_roles': ['Quality Agent', 'Support Agent', 'Compliance Agent']
        },
        {
            'id': 'explorer',
            'name': 'The Explorer',
            'emoji': '\U0001F9ED',  # Compass
            'color': '#22c55e',
            'description': 'Adaptable and practical. Finds innovative solutions through experimentation.',
            'type_codes': ['ISTP', 'ISFP'],
            'strengths': ['Adaptability', 'Hands-on problem-solving', 'Crisis response', 'Experimentation'],
            'best_roles': ['Technical Agent', 'Development Agent', 'Testing Agent']
        },
        {
            'id': 'commander',
            'name': 'The Commander',
            'emoji': '\U0001F451',  # Crown
            'color': '#ef4444',
            'description': 'Natural leader and organizer. Drives projects forward with vision and determination.',
            'type_codes': ['ENTJ', 'ESTJ'],
            'strengths': ['Leadership', 'Organization', 'Efficiency', 'Strategic execution'],
            'best_roles': ['CTO Agent', 'COO Agent', 'Orchestration Agent']
        },
        {
            'id': 'visionary',
            'name': 'The Visionary',
            'emoji': '\U0001F52E',  # Crystal ball
            'color': '#f59e0b',
            'description': 'Innovator and enthusiast. Generates creative ideas and inspires others.',
            'type_codes': ['ENTP', 'ENFP'],
            'strengths': ['Innovation', 'Creativity', 'Inspiration', 'Brainstorming'],
            'best_roles': ['Creative Agent', 'Image Agent', 'Content Agent']
        },
        {
            'id': 'advocate',
            'name': 'The Advocate',
            'emoji': '\U0001F49A',  # Green heart
            'color': '#ec4899',
            'description': 'Supporter and caregiver. Helps others succeed and maintains team morale.',
            'type_codes': ['ENFJ', 'ESFJ'],
            'strengths': ['Support', 'Team building', 'Mentoring', 'Encouragement'],
            'best_roles': ['Social Agent', 'Training Agent', 'Support Agent']
        },
        {
            'id': 'entertainer',
            'name': 'The Entertainer',
            'emoji': '\U0001F3AD',  # Theatre masks
            'color': '#06b6d4',
            'description': 'Dynamic and spontaneous. Brings energy and engagement to projects.',
            'type_codes': ['ESTP', 'ESFP'],
            'strengths': ['Engagement', 'Presentation', 'Spontaneity', 'Energy'],
            'best_roles': ['Video Agent', 'Audio Agent', 'Social Media Agent']
        }
    ]

    return JsonResponse({
        'success': True,
        'archetypes': archetypes
    })
