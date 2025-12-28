"""
Session 253: Agent Rivalries & Alliances API Endpoints

Provides API for managing agent relationships, alliances, and rivalries.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
from django.utils import timezone

from core.models_unified_system import (
    Agent, AgentRelationship, RelationshipEvent, Alliance, Rivalry
)

logger = logging.getLogger(__name__)


# =============================================================================
# RELATIONSHIP OVERVIEW
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_relationships_overview(request):
    """Get overview of all agent relationships, alliances, and rivalries."""
    try:
        # Get relationship distribution
        relationship_counts = AgentRelationship.objects.values('relationship_type').annotate(
            count=Count('id')
        )
        relationship_distribution = {r['relationship_type']: r['count'] for r in relationship_counts}

        # Get all relationships with details
        relationships = AgentRelationship.objects.select_related(
            'agent_from', 'agent_to'
        ).order_by('-strength')[:50]

        relationships_data = []
        for rel in relationships:
            relationships_data.append({
                'id': str(rel.id),
                'agent_from': {
                    'id': str(rel.agent_from.id),
                    'name': rel.agent_from.name,
                },
                'agent_to': {
                    'id': str(rel.agent_to.id),
                    'name': rel.agent_to.name,
                },
                'relationship_type': rel.relationship_type,
                'emoji': rel.get_relationship_emoji(),
                'strength': rel.strength,
                'trust_level': rel.trust_level,
                'respect_level': rel.respect_level,
                'total_interactions': rel.total_interactions,
                'competition_wins': rel.competition_wins,
                'competition_losses': rel.competition_losses,
                'successful_collaborations': rel.successful_collaborations,
                'failed_collaborations': rel.failed_collaborations,
            })

        # Get alliances
        alliances = Alliance.objects.filter(is_active=True).prefetch_related('members')
        alliances_data = []
        for alliance in alliances:
            alliances_data.append({
                'id': str(alliance.id),
                'name': alliance.name,
                'emoji': alliance.get_alliance_emoji(),
                'purpose': alliance.purpose,
                'member_count': alliance.members.count(),
                'members': [{'id': str(m.id), 'name': m.name} for m in alliance.members.all()[:5]],
                'leader': {'id': str(alliance.leader.id), 'name': alliance.leader.name} if alliance.leader else None,
                'combined_strength': alliance.combined_strength,
                'success_rate': alliance.get_success_rate(),
            })

        # Get rivalries
        rivalries = Rivalry.objects.filter(is_active=True)
        rivalries_data = []
        for rivalry in rivalries:
            leader_type, leader_name = rivalry.get_leader()
            rivalries_data.append({
                'id': str(rivalry.id),
                'name': rivalry.name,
                'emoji': rivalry.get_rivalry_emoji(),
                'scope': rivalry.scope,
                'domain': rivalry.domain,
                'challenger': rivalry.get_challenger_name(),
                'defender': rivalry.get_defender_name(),
                'challenger_wins': rivalry.challenger_wins,
                'defender_wins': rivalry.defender_wins,
                'draws': rivalry.draws,
                'intensity': rivalry.intensity,
                'leader': leader_name,
            })

        # Session 356: Use relationship_distribution for alliance/rivalry counts
        # The separate Alliance/Rivalry models are rarely used - AgentRelationship.relationship_type is the source of truth
        alliance_count = relationship_distribution.get('alliance', 0)
        rivalry_count = relationship_distribution.get('rivalry', 0)

        return JsonResponse({
            'success': True,
            'relationship_distribution': relationship_distribution,
            'total_relationships': AgentRelationship.objects.count(),
            'total_alliances': alliance_count,  # From relationship_type field
            'total_rivalries': rivalry_count,   # From relationship_type field
            'alliances': alliance_count,        # Also expose as 'alliances' for UI compatibility
            'rivalries': rivalry_count,         # Also expose as 'rivalries' for UI compatibility
            'total': AgentRelationship.objects.count(),  # For UI compatibility
            'relationships': relationships_data,
            'alliances_data': alliances_data,   # Rename to avoid conflict
            'rivalries_data': rivalries_data,   # Rename to avoid conflict
        })

    except Exception as e:
        logger.error(f"Error getting relationships overview: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# AGENT RELATIONSHIPS
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_agent_relationships(request, agent_id):
    """Get all relationships for a specific agent."""
    try:
        agent = Agent.objects.get(id=agent_id)

        # Get relationships where agent is the initiator
        initiated = AgentRelationship.objects.filter(agent_from=agent).select_related('agent_to')
        # Get relationships where agent is the receiver
        received = AgentRelationship.objects.filter(agent_to=agent).select_related('agent_from')

        initiated_data = []
        for rel in initiated:
            initiated_data.append({
                'id': str(rel.id),
                'partner': {'id': str(rel.agent_to.id), 'name': rel.agent_to.name},
                'direction': 'outgoing',
                'relationship_type': rel.relationship_type,
                'emoji': rel.get_relationship_emoji(),
                'strength': rel.strength,
                'trust_level': rel.trust_level,
                'respect_level': rel.respect_level,
                'total_interactions': rel.total_interactions,
            })

        received_data = []
        for rel in received:
            received_data.append({
                'id': str(rel.id),
                'partner': {'id': str(rel.agent_from.id), 'name': rel.agent_from.name},
                'direction': 'incoming',
                'relationship_type': rel.relationship_type,
                'emoji': rel.get_relationship_emoji(),
                'strength': rel.strength,
                'trust_level': rel.trust_level,
                'respect_level': rel.respect_level,
                'total_interactions': rel.total_interactions,
            })

        # Get agent's alliances
        agent_alliances = Alliance.objects.filter(members=agent, is_active=True)
        alliances_data = [{'id': str(a.id), 'name': a.name, 'purpose': a.purpose} for a in agent_alliances]

        # Get agent's rivalries
        agent_rivalries = Rivalry.objects.filter(
            Q(agent_challenger=agent) | Q(agent_defender=agent),
            is_active=True
        )
        rivalries_data = []
        for r in agent_rivalries:
            rivalries_data.append({
                'id': str(r.id),
                'name': r.name,
                'opponent': r.get_defender_name() if r.agent_challenger == agent else r.get_challenger_name(),
                'domain': r.domain,
            })

        return JsonResponse({
            'success': True,
            'agent': {'id': str(agent.id), 'name': agent.name},
            'initiated_relationships': initiated_data,
            'received_relationships': received_data,
            'alliances': alliances_data,
            'rivalries': rivalries_data,
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting agent relationships: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_relationship(request):
    """Create a new relationship between two agents."""
    try:
        data = json.loads(request.body)

        agent_from = Agent.objects.get(id=data['agent_from_id'])
        agent_to = Agent.objects.get(id=data['agent_to_id'])

        if agent_from == agent_to:
            return JsonResponse({'success': False, 'error': 'Cannot create relationship with self'}, status=400)

        # Check if relationship already exists
        existing = AgentRelationship.objects.filter(agent_from=agent_from, agent_to=agent_to).first()
        if existing:
            return JsonResponse({'success': False, 'error': 'Relationship already exists', 'relationship_id': str(existing.id)}, status=400)

        relationship = AgentRelationship.objects.create(
            agent_from=agent_from,
            agent_to=agent_to,
            relationship_type=data.get('relationship_type', 'neutral'),
            strength=data.get('strength', 0.5),
            trust_level=data.get('trust_level', 0.5),
            respect_level=data.get('respect_level', 0.5),
            origin=data.get('origin', 'manual'),
            origin_details=data.get('origin_details', f'Manually created relationship'),
        )

        # Create first interaction event
        RelationshipEvent.objects.create(
            relationship=relationship,
            event_type='first_interaction',
            description=f'Relationship established between {agent_from.name} and {agent_to.name}',
            strength_at_event=relationship.strength,
            trust_at_event=relationship.trust_level,
            relationship_type_at_event=relationship.relationship_type,
            trigger_type='manual',
        )

        return JsonResponse({
            'success': True,
            'relationship_id': str(relationship.id),
            'message': f'Created {relationship.relationship_type} relationship between {agent_from.name} and {agent_to.name}',
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        logger.error(f"Error creating relationship: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def record_interaction(request, relationship_id):
    """Record an interaction between two agents, evolving their relationship."""
    try:
        data = json.loads(request.body)
        relationship = AgentRelationship.objects.get(id=relationship_id)

        old_type = relationship.relationship_type
        old_strength = relationship.strength
        old_trust = relationship.trust_level

        # Evolve the relationship
        outcome = data.get('outcome', 'neutral')  # positive, negative, neutral
        interaction_type = data.get('interaction_type', 'general')  # collaboration, competition, general

        relationship.evolve_relationship(outcome, interaction_type)

        # Record event if significant change
        new_type = relationship.relationship_type
        if old_type != new_type:
            RelationshipEvent.objects.create(
                relationship=relationship,
                event_type='type_change',
                description=f'Relationship evolved from {old_type} to {new_type}',
                strength_at_event=relationship.strength,
                trust_at_event=relationship.trust_level,
                relationship_type_at_event=new_type,
                trigger_type=interaction_type,
            )
        elif abs(relationship.strength - old_strength) >= 0.1 or abs(relationship.trust_level - old_trust) >= 0.1:
            event_type = 'trust_increase' if relationship.trust_level > old_trust else 'trust_decrease'
            RelationshipEvent.objects.create(
                relationship=relationship,
                event_type=event_type,
                description=f'Relationship strength: {old_strength:.2f} -> {relationship.strength:.2f}',
                strength_at_event=relationship.strength,
                trust_at_event=relationship.trust_level,
                relationship_type_at_event=relationship.relationship_type,
                trigger_type=interaction_type,
            )

        return JsonResponse({
            'success': True,
            'relationship_id': str(relationship.id),
            'new_type': relationship.relationship_type,
            'new_strength': relationship.strength,
            'new_trust': relationship.trust_level,
            'type_changed': old_type != new_type,
        })

    except AgentRelationship.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Relationship not found'}, status=404)
    except Exception as e:
        logger.error(f"Error recording interaction: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# ALLIANCES
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_alliance(request, alliance_id):
    """Get detailed alliance information."""
    try:
        alliance = Alliance.objects.prefetch_related('members').get(id=alliance_id)

        members = []
        for member in alliance.members.all():
            members.append({
                'id': str(member.id),
                'name': member.name,
                'is_leader': member == alliance.leader,
            })

        return JsonResponse({
            'success': True,
            'alliance': {
                'id': str(alliance.id),
                'name': alliance.name,
                'description': alliance.description,
                'emoji': alliance.get_alliance_emoji(),
                'purpose': alliance.purpose,
                'members': members,
                'leader': {'id': str(alliance.leader.id), 'name': alliance.leader.name} if alliance.leader else None,
                'total_projects': alliance.total_projects,
                'successful_projects': alliance.successful_projects,
                'success_rate': alliance.get_success_rate(),
                'combined_strength': alliance.combined_strength,
                'is_active': alliance.is_active,
                'formed_at': alliance.formed_at.isoformat(),
            }
        })

    except Alliance.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Alliance not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting alliance: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_alliance(request):
    """Create a new alliance."""
    try:
        data = json.loads(request.body)

        # Get members
        member_ids = data.get('member_ids', [])
        if len(member_ids) < 2:
            return JsonResponse({'success': False, 'error': 'Alliance requires at least 2 members'}, status=400)

        members = Agent.objects.filter(id__in=member_ids)
        if members.count() != len(member_ids):
            return JsonResponse({'success': False, 'error': 'Some agents not found'}, status=404)

        # Get optional leader
        leader = None
        if data.get('leader_id'):
            leader = Agent.objects.get(id=data['leader_id'])

        alliance = Alliance.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            purpose=data.get('purpose', 'general'),
            leader=leader,
        )
        alliance.members.set(members)
        alliance.update_combined_strength()

        # Create alliance relationships between all members
        member_list = list(members)
        for i, agent1 in enumerate(member_list):
            for agent2 in member_list[i+1:]:
                # Create bidirectional alliance relationships
                AgentRelationship.objects.get_or_create(
                    agent_from=agent1,
                    agent_to=agent2,
                    defaults={
                        'relationship_type': 'alliance',
                        'strength': 0.6,
                        'trust_level': 0.6,
                        'origin': 'auto_formed',
                        'origin_details': f'Formed alliance: {alliance.name}',
                    }
                )
                AgentRelationship.objects.get_or_create(
                    agent_from=agent2,
                    agent_to=agent1,
                    defaults={
                        'relationship_type': 'alliance',
                        'strength': 0.6,
                        'trust_level': 0.6,
                        'origin': 'auto_formed',
                        'origin_details': f'Formed alliance: {alliance.name}',
                    }
                )

        return JsonResponse({
            'success': True,
            'alliance_id': str(alliance.id),
            'message': f'Created alliance "{alliance.name}" with {len(member_ids)} members',
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        logger.error(f"Error creating alliance: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_alliance_member(request, alliance_id):
    """Add a member to an alliance."""
    try:
        data = json.loads(request.body)
        alliance = Alliance.objects.get(id=alliance_id)
        agent = Agent.objects.get(id=data['agent_id'])

        if agent in alliance.members.all():
            return JsonResponse({'success': False, 'error': 'Agent already in alliance'}, status=400)

        alliance.members.add(agent)

        # Create alliance relationships with existing members
        for member in alliance.members.exclude(id=agent.id):
            AgentRelationship.objects.get_or_create(
                agent_from=agent,
                agent_to=member,
                defaults={
                    'relationship_type': 'alliance',
                    'strength': 0.5,
                    'trust_level': 0.5,
                    'origin': 'auto_formed',
                    'origin_details': f'Joined alliance: {alliance.name}',
                }
            )
            AgentRelationship.objects.get_or_create(
                agent_from=member,
                agent_to=agent,
                defaults={
                    'relationship_type': 'alliance',
                    'strength': 0.5,
                    'trust_level': 0.5,
                    'origin': 'auto_formed',
                    'origin_details': f'New member joined alliance: {alliance.name}',
                }
            )

        alliance.update_combined_strength()

        return JsonResponse({
            'success': True,
            'message': f'Added {agent.name} to {alliance.name}',
        })

    except Alliance.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Alliance not found'}, status=404)
    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        logger.error(f"Error adding alliance member: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def disband_alliance(request, alliance_id):
    """Disband an alliance."""
    try:
        alliance = Alliance.objects.get(id=alliance_id)
        alliance.is_active = False
        alliance.disbanded_at = timezone.now()
        alliance.save()

        return JsonResponse({
            'success': True,
            'message': f'Alliance "{alliance.name}" disbanded',
        })

    except Alliance.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Alliance not found'}, status=404)
    except Exception as e:
        logger.error(f"Error disbanding alliance: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# RIVALRIES
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_rivalry(request, rivalry_id):
    """Get detailed rivalry information."""
    try:
        rivalry = Rivalry.objects.get(id=rivalry_id)
        leader_type, leader_name = rivalry.get_leader()

        return JsonResponse({
            'success': True,
            'rivalry': {
                'id': str(rivalry.id),
                'name': rivalry.name,
                'description': rivalry.description,
                'emoji': rivalry.get_rivalry_emoji(),
                'scope': rivalry.scope,
                'domain': rivalry.domain,
                'challenger': rivalry.get_challenger_name(),
                'defender': rivalry.get_defender_name(),
                'challenger_wins': rivalry.challenger_wins,
                'defender_wins': rivalry.defender_wins,
                'draws': rivalry.draws,
                'total_competitions': rivalry.challenger_wins + rivalry.defender_wins + rivalry.draws,
                'intensity': rivalry.intensity,
                'leader': leader_name,
                'leader_type': leader_type,
                'is_active': rivalry.is_active,
                'started_at': rivalry.started_at.isoformat(),
            }
        })

    except Rivalry.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Rivalry not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting rivalry: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_rivalry(request):
    """Create a new rivalry between agents or alliances."""
    try:
        data = json.loads(request.body)

        scope = data.get('scope', 'agent_vs_agent')
        rivalry_data = {
            'name': data['name'],
            'description': data.get('description', ''),
            'scope': scope,
            'domain': data.get('domain', 'general'),
            'intensity': data.get('intensity', 0.5),
        }

        if scope == 'agent_vs_agent':
            rivalry_data['agent_challenger'] = Agent.objects.get(id=data['challenger_id'])
            rivalry_data['agent_defender'] = Agent.objects.get(id=data['defender_id'])

            # Create rivalry relationship
            AgentRelationship.objects.get_or_create(
                agent_from=rivalry_data['agent_challenger'],
                agent_to=rivalry_data['agent_defender'],
                defaults={
                    'relationship_type': 'rivalry',
                    'strength': 0.5,
                    'trust_level': 0.3,
                    'origin': 'competition',
                    'origin_details': f'Rivalry: {data["name"]}',
                }
            )

        elif scope == 'alliance_vs_alliance':
            rivalry_data['alliance_challenger'] = Alliance.objects.get(id=data['challenger_id'])
            rivalry_data['alliance_defender'] = Alliance.objects.get(id=data['defender_id'])

        elif scope == 'agent_vs_alliance':
            rivalry_data['agent_challenger'] = Agent.objects.get(id=data['challenger_id'])
            rivalry_data['alliance_defender'] = Alliance.objects.get(id=data['defender_id'])

        rivalry = Rivalry.objects.create(**rivalry_data)

        return JsonResponse({
            'success': True,
            'rivalry_id': str(rivalry.id),
            'message': f'Created rivalry: {rivalry.name}',
        })

    except (Agent.DoesNotExist, Alliance.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Participant not found'}, status=404)
    except Exception as e:
        logger.error(f"Error creating rivalry: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def record_competition(request, rivalry_id):
    """Record a competition result in a rivalry."""
    try:
        data = json.loads(request.body)
        rivalry = Rivalry.objects.get(id=rivalry_id)

        winner = data.get('winner', 'draw')  # 'challenger', 'defender', or 'draw'
        rivalry.record_competition(winner)

        leader_type, leader_name = rivalry.get_leader()

        return JsonResponse({
            'success': True,
            'rivalry_id': str(rivalry.id),
            'challenger_wins': rivalry.challenger_wins,
            'defender_wins': rivalry.defender_wins,
            'draws': rivalry.draws,
            'intensity': rivalry.intensity,
            'leader': leader_name,
        })

    except Rivalry.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Rivalry not found'}, status=404)
    except Exception as e:
        logger.error(f"Error recording competition: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def end_rivalry(request, rivalry_id):
    """End a rivalry."""
    try:
        rivalry = Rivalry.objects.get(id=rivalry_id)
        rivalry.is_active = False
        rivalry.ended_at = timezone.now()
        rivalry.save()

        return JsonResponse({
            'success': True,
            'message': f'Rivalry "{rivalry.name}" ended',
        })

    except Rivalry.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Rivalry not found'}, status=404)
    except Exception as e:
        logger.error(f"Error ending rivalry: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# RELATIONSHIP EVENTS
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_relationship_events(request, relationship_id):
    """Get event history for a relationship."""
    try:
        relationship = AgentRelationship.objects.get(id=relationship_id)
        limit = int(request.GET.get('limit', 50))

        events = RelationshipEvent.objects.filter(relationship=relationship).order_by('-created_at')[:limit]

        events_data = []
        for event in events:
            events_data.append({
                'id': str(event.id),
                'event_type': event.event_type,
                'description': event.description,
                'strength_at_event': event.strength_at_event,
                'trust_at_event': event.trust_at_event,
                'relationship_type_at_event': event.relationship_type_at_event,
                'trigger_type': event.trigger_type,
                'created_at': event.created_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'relationship_id': str(relationship.id),
            'events': events_data,
        })

    except AgentRelationship.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Relationship not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting relationship events: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# AUTO-GENERATION
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def auto_generate_relationships(request):
    """Automatically generate relationships between agents based on their specialties."""
    try:
        agents = list(Agent.objects.filter(is_active=True))
        created_count = 0

        # Define compatible/competing agent types
        compatible_pairs = [
            ('ImageAgent', 'VideoAgent'),  # Visual content creators
            ('ResearchAgent', 'TrendAnalysisAgent'),  # Information gatherers
            ('WorkflowOrchestrationAgent', 'CreativeDirectorAgent'),  # Coordinators
            ('ContentStrategyAgent', 'SEOOptimizerAgent'),  # Content planners
            ('PromptEngineeringAgent', 'ImageAgent'),  # Prompt + Generation
            ('BrandIdentityAgent', 'SocialMediaAgent'),  # Brand presence
        ]

        competing_pairs = [
            ('ImageAgent', 'VideoAgent'),  # Both vie for visual content tasks
            ('ContentStrategyAgent', 'CreativeDirectorAgent'),  # Both do strategy
        ]

        for agent1 in agents:
            for agent2 in agents:
                if agent1 == agent2:
                    continue

                # Check if relationship already exists
                if AgentRelationship.objects.filter(agent_from=agent1, agent_to=agent2).exists():
                    continue

                # Determine relationship type based on agent names/specialties
                agent1_type = agent1.name
                agent2_type = agent2.name

                relationship_type = 'neutral'
                strength = 0.5
                trust = 0.5

                # Check compatible pairs
                for pair in compatible_pairs:
                    if (pair[0] in agent1_type and pair[1] in agent2_type) or \
                       (pair[1] in agent1_type and pair[0] in agent2_type):
                        relationship_type = 'alliance'
                        strength = 0.65
                        trust = 0.6
                        break

                # Check competing pairs (can override alliance to create interesting dynamics)
                for pair in competing_pairs:
                    if (pair[0] in agent1_type and pair[1] in agent2_type) or \
                       (pair[1] in agent1_type and pair[0] in agent2_type):
                        # 30% chance of rivalry instead of alliance
                        import random
                        if random.random() < 0.3:
                            relationship_type = 'rivalry'
                            strength = 0.5
                            trust = 0.4
                        break

                AgentRelationship.objects.create(
                    agent_from=agent1,
                    agent_to=agent2,
                    relationship_type=relationship_type,
                    strength=strength,
                    trust_level=trust,
                    respect_level=0.5,
                    origin='auto_formed',
                    origin_details='Auto-generated based on agent specialties',
                )
                created_count += 1

        return JsonResponse({
            'success': True,
            'created_relationships': created_count,
            'message': f'Auto-generated {created_count} relationships between {len(agents)} agents',
        })

    except Exception as e:
        logger.error(f"Error auto-generating relationships: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
