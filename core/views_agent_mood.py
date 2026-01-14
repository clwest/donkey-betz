"""
Session 252: Agent Mood System - API Endpoints

Provides REST API for managing agent moods, viewing mood history,
and configuring mood trigger rules.
"""

import json
import logging
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Avg

from .models_unified_system import (
    Agent, AgentMood, MoodHistory, MoodTriggerRule, AgentMemory, AgentPersonality
)

logger = logging.getLogger(__name__)


# =============================================================================
# Mood Overview & Dashboard
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_mood_overview(request):
    """
    GET /api/agent-mood/
    Overview of all agent moods with statistics.
    """
    try:
        # Get all agents with their moods and personalities (Session 310)
        agents = Agent.objects.filter(is_active=True).prefetch_related('mood', 'personality')

        agent_moods = []
        mood_distribution = {}

        for agent in agents:
            try:
                mood = agent.mood

                # Session 310: Get personality data if available
                personality_data = None
                try:
                    if hasattr(agent, 'personality') and agent.personality:
                        personality_data = {
                            'type_code': agent.personality.get_type_code(),
                            'archetype': agent.personality.archetype,
                            'emoji': agent.personality.get_personality_emoji(),
                            'color': agent.personality.get_personality_color(),
                        }
                except AgentPersonality.DoesNotExist:
                    pass

                # Session 749: Field names to match frontend expectations
                mood_data = {
                    'id': str(mood.id) if hasattr(mood, 'id') else str(agent.id),
                    'agent_id': str(agent.id),
                    'agent_name': agent.name,
                    'current_mood': mood.current_mood,
                    'emoji': mood.get_mood_emoji(),
                    'color': mood.get_mood_color(),
                    'intensity': int(mood.intensity * 100),  # Convert to percentage
                    'creativity_level': mood.creativity_level,
                    'precision_level': mood.precision_level,
                    'sociability_level': mood.sociability_level,
                    'risk_tolerance': mood.risk_tolerance,
                    'trigger_type': mood.trigger_type,
                    'last_updated': mood.mood_started_at.isoformat() if mood.mood_started_at else None,
                    'mood_streak': mood.total_mood_changes,
                    'personality': personality_data,  # Session 310: Add personality
                    # Keep original names for backward compatibility
                    'name': agent.name,
                    'mood_started_at': mood.mood_started_at.isoformat() if mood.mood_started_at else None,
                    'total_mood_changes': mood.total_mood_changes,
                }
                agent_moods.append(mood_data)

                # Track distribution
                mood_distribution[mood.current_mood] = mood_distribution.get(mood.current_mood, 0) + 1

            except AgentMood.DoesNotExist:
                # Create default mood for agent
                mood = AgentMood.objects.create(agent=agent)

                # Session 310: Get personality for new mood agents too
                personality_data = None
                try:
                    if hasattr(agent, 'personality') and agent.personality:
                        personality_data = {
                            'type_code': agent.personality.get_type_code(),
                            'archetype': agent.personality.archetype,
                            'emoji': agent.personality.get_personality_emoji(),
                            'color': agent.personality.get_personality_color(),
                        }
                except AgentPersonality.DoesNotExist:
                    pass

                # Session 749: Field names to match frontend expectations
                agent_moods.append({
                    'id': str(mood.id),
                    'agent_id': str(agent.id),
                    'agent_name': agent.name,
                    'current_mood': 'calm',
                    'emoji': '😌',
                    'color': '#06b6d4',
                    'intensity': 50,  # Percentage
                    'creativity_level': 0.5,
                    'precision_level': 0.5,
                    'sociability_level': 0.5,
                    'risk_tolerance': 0.5,
                    'trigger_type': 'idle',
                    'last_updated': timezone.now().isoformat(),
                    'mood_streak': 0,
                    'personality': personality_data,  # Session 310: Add personality
                    # Keep original names for backward compatibility
                    'name': agent.name,
                    'mood_started_at': timezone.now().isoformat(),
                    'total_mood_changes': 0,
                })
                mood_distribution['calm'] = mood_distribution.get('calm', 0) + 1

        # Sort by mood (group similar moods together)
        agent_moods.sort(key=lambda x: (x['current_mood'], x['name']))

        return JsonResponse({
            'success': True,
            'overview': {
                'total_agents': len(agent_moods),
                'mood_distribution': [
                    {'mood': k, 'count': v} for k, v in sorted(mood_distribution.items(), key=lambda x: -x[1])
                ],
            },
            'agents': agent_moods,
        })

    except Exception as e:
        logger.error(f"Error getting mood overview: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Agent Mood Management
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_agent_mood(request, agent_id):
    """
    GET /api/agent-mood/agent/{agent_id}/
    Get detailed mood for a specific agent.
    """
    try:
        agent = Agent.objects.get(id=agent_id)

        # Get or create mood
        mood, created = AgentMood.objects.get_or_create(agent=agent)

        # Get recent mood history
        history = MoodHistory.objects.filter(agent=agent).order_by('-created_at')[:10]

        return JsonResponse({
            'success': True,
            'agent': {
                'id': str(agent.id),
                'name': agent.name,
            },
            'mood': {
                'current_mood': mood.current_mood,
                'emoji': mood.get_mood_emoji(),
                'color': mood.get_mood_color(),
                'intensity': mood.intensity,
                'creativity_level': mood.creativity_level,
                'precision_level': mood.precision_level,
                'sociability_level': mood.sociability_level,
                'risk_tolerance': mood.risk_tolerance,
                'trigger_type': mood.trigger_type,
                'trigger_source': mood.trigger_source,
                'mood_started_at': mood.mood_started_at.isoformat() if mood.mood_started_at else None,
                'mood_expires_at': mood.mood_expires_at.isoformat() if mood.mood_expires_at else None,
                'total_mood_changes': mood.total_mood_changes,
                'prompt_modifier': mood.get_prompt_modifier(),
            },
            'recent_history': [
                {
                    'mood': h.mood,
                    'intensity': h.intensity,
                    'trigger_type': h.trigger_type,
                    'trigger_source': h.trigger_source,
                    'duration_minutes': h.duration_minutes,
                    'created_at': h.created_at.isoformat(),
                }
                for h in history
            ],
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting agent mood: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def set_agent_mood(request, agent_id):
    """
    POST /api/agent-mood/agent/{agent_id}/set/
    Manually set an agent's mood.

    Body: {
        "mood": "inspired",
        "intensity": 0.8,
        "duration_minutes": 60,
        "reason": "User requested creative boost"
    }
    """
    try:
        agent = Agent.objects.get(id=agent_id)
        data = json.loads(request.body)

        new_mood = data.get('mood', 'calm')
        intensity = float(data.get('intensity', 0.5))
        duration_minutes = int(data.get('duration_minutes', 60))
        reason = data.get('reason', 'Manual override')

        # Validate mood
        valid_moods = [c[0] for c in AgentMood.MOOD_CHOICES]
        if new_mood not in valid_moods:
            return JsonResponse({
                'success': False,
                'error': f'Invalid mood. Valid options: {valid_moods}'
            }, status=400)

        # Get or create mood
        mood, created = AgentMood.objects.get_or_create(agent=agent)

        # Calculate duration of previous mood
        previous_duration = None
        if mood.mood_started_at:
            previous_duration = int((timezone.now() - mood.mood_started_at).total_seconds() / 60)

        # Record history of previous mood
        if not created:
            MoodHistory.objects.create(
                agent=agent,
                mood=mood.current_mood,
                intensity=mood.intensity,
                trigger_type=mood.trigger_type,
                trigger_source=mood.trigger_source,
                creativity_level=mood.creativity_level,
                precision_level=mood.precision_level,
                sociability_level=mood.sociability_level,
                risk_tolerance=mood.risk_tolerance,
                duration_minutes=previous_duration,
            )

        # Update mood dimensions based on mood type
        mood_dimensions = {
            'inspired': {'creativity': 0.9, 'precision': 0.5, 'sociability': 0.7, 'risk': 0.8},
            'focused': {'creativity': 0.4, 'precision': 0.95, 'sociability': 0.3, 'risk': 0.2},
            'curious': {'creativity': 0.7, 'precision': 0.6, 'sociability': 0.8, 'risk': 0.7},
            'confident': {'creativity': 0.6, 'precision': 0.7, 'sociability': 0.7, 'risk': 0.6},
            'contemplative': {'creativity': 0.6, 'precision': 0.7, 'sociability': 0.4, 'risk': 0.4},
            'energetic': {'creativity': 0.7, 'precision': 0.5, 'sociability': 0.9, 'risk': 0.7},
            'calm': {'creativity': 0.5, 'precision': 0.6, 'sociability': 0.5, 'risk': 0.4},
            'frustrated': {'creativity': 0.3, 'precision': 0.4, 'sociability': 0.6, 'risk': 0.3},
            'tired': {'creativity': 0.3, 'precision': 0.4, 'sociability': 0.2, 'risk': 0.2},
            'playful': {'creativity': 0.85, 'precision': 0.4, 'sociability': 0.9, 'risk': 0.85},
        }

        dims = mood_dimensions.get(new_mood, {'creativity': 0.5, 'precision': 0.5, 'sociability': 0.5, 'risk': 0.5})

        # Apply intensity scaling
        mood.current_mood = new_mood
        mood.intensity = intensity
        mood.creativity_level = dims['creativity'] * intensity
        mood.precision_level = dims['precision'] * intensity
        mood.sociability_level = dims['sociability'] * intensity
        mood.risk_tolerance = dims['risk'] * intensity
        mood.trigger_type = 'manual'
        mood.trigger_source = reason
        mood.mood_started_at = timezone.now()
        mood.mood_expires_at = timezone.now() + timedelta(minutes=duration_minutes) if duration_minutes > 0 else None
        mood.total_mood_changes += 1
        mood.save()

        logger.info(f"Set {agent.name}'s mood to {new_mood} ({intensity:.0%}) for {duration_minutes}min")

        return JsonResponse({
            'success': True,
            'message': f"Set {agent.name}'s mood to {new_mood}",
            'mood': {
                'current_mood': mood.current_mood,
                'emoji': mood.get_mood_emoji(),
                'color': mood.get_mood_color(),
                'intensity': mood.intensity,
                'expires_at': mood.mood_expires_at.isoformat() if mood.mood_expires_at else None,
            },
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error setting agent mood: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Mood History
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_mood_history(request, agent_id):
    """
    GET /api/agent-mood/agent/{agent_id}/history/
    Get mood history for an agent.
    """
    try:
        agent = Agent.objects.get(id=agent_id)

        limit = int(request.GET.get('limit', 50))
        history = MoodHistory.objects.filter(agent=agent).order_by('-created_at')[:limit]

        # Aggregate statistics
        stats = MoodHistory.objects.filter(agent=agent).values('mood').annotate(
            count=Count('id'),
            avg_intensity=Avg('intensity'),
            avg_duration=Avg('duration_minutes'),
        )

        return JsonResponse({
            'success': True,
            'agent': {
                'id': str(agent.id),
                'name': agent.name,
            },
            # Session 749: Field names to match frontend expectations
            'history': [
                {
                    'id': str(h.id),
                    'mood': h.mood,
                    'intensity': int(h.intensity * 100) if h.intensity else 50,  # Percentage
                    'reason': h.trigger_source or h.trigger_type or 'Unknown',  # Frontend expects 'reason'
                    'recorded_at': h.created_at.isoformat(),  # Frontend expects 'recorded_at'
                    # Keep original fields for backward compatibility
                    'trigger_type': h.trigger_type,
                    'trigger_source': h.trigger_source,
                    'creativity_level': h.creativity_level,
                    'precision_level': h.precision_level,
                    'duration_minutes': h.duration_minutes,
                    'created_at': h.created_at.isoformat(),
                }
                for h in history
            ],
            'statistics': list(stats),
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting mood history: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Mood Trigger Rules
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_mood_rules(request):
    """
    GET /api/agent-mood/rules/
    Get all mood trigger rules.
    """
    try:
        rules = MoodTriggerRule.objects.all().select_related('agent')

        return JsonResponse({
            'success': True,
            'rules': [
                {
                    'id': str(r.id),
                    'name': r.name,
                    'description': r.description,
                    'agent': {
                        'id': str(r.agent.id),
                        'name': r.agent.name,
                    } if r.agent else None,
                    'is_active': r.is_active,
                    'condition_type': r.condition_type,
                    'condition_value': r.condition_value,
                    'target_mood': r.target_mood,
                    'target_intensity': r.target_intensity,
                    'duration_minutes': r.duration_minutes,
                    'priority': r.priority,
                }
                for r in rules
            ],
        })

    except Exception as e:
        logger.error(f"Error getting mood rules: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_mood_rule(request):
    """
    POST /api/agent-mood/rules/create/
    Create a new mood trigger rule.

    Body: {
        "name": "Success Streak Boost",
        "description": "Boost confidence after 3 successful tasks",
        "agent_id": null,  // null for global rule
        "condition_type": "task_success_streak",
        "condition_value": {"streak_count": 3},
        "target_mood": "confident",
        "target_intensity": 0.8,
        "duration_minutes": 120,
        "priority": 75
    }
    """
    try:
        data = json.loads(request.body)

        agent = None
        if data.get('agent_id'):
            agent = Agent.objects.get(id=data['agent_id'])

        rule = MoodTriggerRule.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            agent=agent,
            condition_type=data['condition_type'],
            condition_value=data.get('condition_value', {}),
            target_mood=data['target_mood'],
            target_intensity=float(data.get('target_intensity', 0.7)),
            duration_minutes=int(data.get('duration_minutes', 60)),
            priority=int(data.get('priority', 50)),
        )

        return JsonResponse({
            'success': True,
            'message': f"Created mood rule: {rule.name}",
            'rule': {
                'id': str(rule.id),
                'name': rule.name,
            },
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except KeyError as e:
        return JsonResponse({'success': False, 'error': f'Missing field: {e}'}, status=400)
    except Exception as e:
        logger.error(f"Error creating mood rule: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_mood_rule(request, rule_id):
    """
    DELETE /api/agent-mood/rules/{rule_id}/delete/
    Delete a mood trigger rule.
    """
    try:
        rule = MoodTriggerRule.objects.get(id=rule_id)
        name = rule.name
        rule.delete()

        return JsonResponse({
            'success': True,
            'message': f"Deleted mood rule: {name}",
        })

    except MoodTriggerRule.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Rule not found'}, status=404)
    except Exception as e:
        logger.error(f"Error deleting mood rule: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Memory-Mood Integration
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def trigger_mood_from_memory(request):
    """
    POST /api/agent-mood/trigger-from-memory/
    Trigger a mood change based on a memory being recalled.

    Body: {
        "agent_id": "uuid",
        "memory_id": "uuid"
    }
    """
    try:
        data = json.loads(request.body)

        agent = Agent.objects.get(id=data['agent_id'])
        memory = AgentMemory.objects.get(id=data['memory_id'], agent=agent)

        # Determine mood based on memory valence and type
        mood_map = {
            ('success', 'positive'): ('confident', 0.8),
            ('success', 'neutral'): ('calm', 0.6),
            ('failure', 'negative'): ('contemplative', 0.6),
            ('failure', 'neutral'): ('focused', 0.7),
            ('technique', 'positive'): ('focused', 0.7),
            ('technique', 'neutral'): ('calm', 0.5),
            ('insight', 'positive'): ('inspired', 0.85),
            ('insight', 'neutral'): ('curious', 0.7),
            ('preference', 'positive'): ('playful', 0.6),
            ('interaction', 'positive'): ('energetic', 0.7),
            ('interaction', 'negative'): ('frustrated', 0.5),
            ('feedback', 'positive'): ('confident', 0.75),
            ('feedback', 'negative'): ('contemplative', 0.6),
        }

        key = (memory.memory_type, memory.valence)
        target_mood, base_intensity = mood_map.get(key, ('calm', 0.5))

        # Scale intensity by memory importance
        intensity = min(1.0, base_intensity * (0.5 + memory.importance_score * 0.5))

        # Get or create mood
        mood, created = AgentMood.objects.get_or_create(agent=agent)

        # Record previous mood in history
        if not created and mood.current_mood != target_mood:
            previous_duration = None
            if mood.mood_started_at:
                previous_duration = int((timezone.now() - mood.mood_started_at).total_seconds() / 60)

            MoodHistory.objects.create(
                agent=agent,
                mood=mood.current_mood,
                intensity=mood.intensity,
                trigger_type=mood.trigger_type,
                trigger_source=mood.trigger_source,
                creativity_level=mood.creativity_level,
                precision_level=mood.precision_level,
                sociability_level=mood.sociability_level,
                risk_tolerance=mood.risk_tolerance,
                duration_minutes=previous_duration,
            )

        # Update mood
        mood_dimensions = {
            'inspired': {'creativity': 0.9, 'precision': 0.5, 'sociability': 0.7, 'risk': 0.8},
            'focused': {'creativity': 0.4, 'precision': 0.95, 'sociability': 0.3, 'risk': 0.2},
            'curious': {'creativity': 0.7, 'precision': 0.6, 'sociability': 0.8, 'risk': 0.7},
            'confident': {'creativity': 0.6, 'precision': 0.7, 'sociability': 0.7, 'risk': 0.6},
            'contemplative': {'creativity': 0.6, 'precision': 0.7, 'sociability': 0.4, 'risk': 0.4},
            'energetic': {'creativity': 0.7, 'precision': 0.5, 'sociability': 0.9, 'risk': 0.7},
            'calm': {'creativity': 0.5, 'precision': 0.6, 'sociability': 0.5, 'risk': 0.4},
            'frustrated': {'creativity': 0.3, 'precision': 0.4, 'sociability': 0.6, 'risk': 0.3},
            'tired': {'creativity': 0.3, 'precision': 0.4, 'sociability': 0.2, 'risk': 0.2},
            'playful': {'creativity': 0.85, 'precision': 0.4, 'sociability': 0.9, 'risk': 0.85},
        }

        dims = mood_dimensions.get(target_mood, {'creativity': 0.5, 'precision': 0.5, 'sociability': 0.5, 'risk': 0.5})

        mood.current_mood = target_mood
        mood.intensity = intensity
        mood.creativity_level = dims['creativity'] * intensity
        mood.precision_level = dims['precision'] * intensity
        mood.sociability_level = dims['sociability'] * intensity
        mood.risk_tolerance = dims['risk'] * intensity
        mood.trigger_type = 'memory'
        mood.trigger_source = f"Memory: {memory.title[:50]}"
        mood.mood_started_at = timezone.now()
        mood.mood_expires_at = timezone.now() + timedelta(minutes=30)  # Memory-triggered moods last 30 min
        mood.total_mood_changes += 1
        mood.save()

        # Update memory access stats
        memory.access_count += 1
        memory.last_accessed_at = timezone.now()
        memory.save()

        logger.info(f"Memory '{memory.title}' triggered {target_mood} mood for {agent.name}")

        return JsonResponse({
            'success': True,
            'message': f"Memory triggered {target_mood} mood",
            'mood': {
                'current_mood': mood.current_mood,
                'emoji': mood.get_mood_emoji(),
                'intensity': mood.intensity,
            },
            'memory': {
                'title': memory.title,
                'type': memory.memory_type,
                'valence': memory.valence,
            },
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except AgentMemory.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Memory not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error triggering mood from memory: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Prompt Integration
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_mood_prompt_context(request, agent_id):
    """
    GET /api/agent-mood/agent/{agent_id}/prompt-context/
    Get mood-aware prompt context for an agent.
    This can be injected into agent prompts to influence behavior.
    """
    try:
        agent = Agent.objects.get(id=agent_id)
        mood, created = AgentMood.objects.get_or_create(agent=agent)

        context = f"""
## Current Emotional State
**Mood:** {mood.current_mood.title()} {mood.get_mood_emoji()}
**Intensity:** {mood.intensity:.0%}

### Behavioral Guidelines
{mood.get_prompt_modifier()}

### Dimensional Profile
- Creativity: {mood.creativity_level:.0%}
- Precision: {mood.precision_level:.0%}
- Sociability: {mood.sociability_level:.0%}
- Risk Tolerance: {mood.risk_tolerance:.0%}
"""

        return JsonResponse({
            'success': True,
            'agent': {
                'id': str(agent.id),
                'name': agent.name,
            },
            'prompt_context': context.strip(),
            'mood_data': {
                'mood': mood.current_mood,
                'emoji': mood.get_mood_emoji(),
                'intensity': mood.intensity,
                'creativity_level': mood.creativity_level,
                'precision_level': mood.precision_level,
                'sociability_level': mood.sociability_level,
                'risk_tolerance': mood.risk_tolerance,
            },
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting mood prompt context: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
