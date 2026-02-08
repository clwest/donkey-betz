"""
Session 251: Memory Palace - Agent Memory Visualization & Retrieval
API endpoints for managing agent memories, rooms, and connections
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def get_agent_memories(request, agent_id):
    """Get all memories for an agent with optional filtering

    Session 753: Added memory_outcome, last_accessed_at, tags fields
    Session 753: Added outcome filter and sort_by parameter
    Session 754: Added tag filter parameter
    """
    try:
        from core.models_unified_system import AgentMemory, Agent

        try:
            agent = Agent.objects.get(id=agent_id)
        except Agent.DoesNotExist:
            return JsonResponse({'error': 'Agent not found'}, status=404)

        # Parse query params
        memory_type = request.GET.get('type')
        valence = request.GET.get('valence')
        outcome = request.GET.get('outcome')  # Session 753: Filter by outcome
        tag = request.GET.get('tag')  # Session 754: Filter by tag
        limit = int(request.GET.get('limit', 50))
        sort_by = request.GET.get('sort_by', 'importance')  # Session 753: Sort options

        # Build query
        # Session 810: Defer embedding fields to reduce egress costs
        memories = AgentMemory.objects.filter(agent=agent).defer('embedding')

        if memory_type:
            memories = memories.filter(memory_type=memory_type)
        if valence:
            memories = memories.filter(valence=valence)
        # Session 753: Outcome filter
        if outcome:
            memories = memories.filter(memory_outcome=outcome)
        # Session 754: Tag filter (JSONField contains)
        if tag:
            memories = memories.filter(tags__contains=[tag])

        # Session 753: Sorting options
        if sort_by == 'recent':
            memories = memories.order_by('-created_at')
        elif sort_by == 'accessed':
            memories = memories.order_by('-last_accessed_at', '-created_at')
        elif sort_by == 'access_count':
            memories = memories.order_by('-access_count', '-created_at')
        else:  # default: importance
            memories = memories.order_by('-importance_score', '-created_at')

        memories = memories[:limit]

        return JsonResponse({
            'success': True,
            'agent_id': str(agent_id),
            'agent_name': agent.name,
            'memory_count': memories.count(),
            'memories': [
                {
                    'id': str(m.id),
                    'title': m.title,
                    'content': m.content[:200] + '...' if len(m.content) > 200 else m.content,
                    'memory_type': m.memory_type,
                    'valence': m.valence,
                    'importance_score': m.importance_score,
                    'access_count': m.access_count,
                    'created_at': m.created_at.isoformat(),
                    'source_type': m.source_type,
                    # Session 753: Added fields
                    'memory_outcome': m.memory_outcome,
                    'last_accessed_at': m.last_accessed_at.isoformat() if m.last_accessed_at else None,
                    'tags': m.tags or [],
                    'source_id': m.source_id or '',
                }
                for m in memories
            ]
        })
    except Exception as e:
        logger.exception(f"Error fetching memories: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_memory_detail(request, memory_id):
    """Get full details of a specific memory"""
    try:
        from core.models_unified_system import AgentMemory, AgentExecution

        try:
            # Session 810: Defer embedding fields to reduce egress costs
            memory = AgentMemory.objects.defer('embedding').get(id=memory_id)
        except AgentMemory.DoesNotExist:
            return JsonResponse({'error': 'Memory not found'}, status=404)

        # Update access tracking
        memory.access_count += 1
        memory.last_accessed_at = timezone.now()
        memory.save(update_fields=['access_count', 'last_accessed_at'])

        # Get connected memories
        connected = memory.connected_memories.all()[:10]

        # Session 757: Include execution output_data if this memory is from an execution
        execution_data = None
        if memory.source_type in ('execution', 'task') and memory.source_id:
            try:
                execution = AgentExecution.objects.get(id=memory.source_id)
                if execution.output_data:
                    execution_data = {
                        'output_data': execution.output_data,
                        'status': execution.status,
                        'execution_time_ms': execution.execution_time_ms,
                        'tokens_used': execution.tokens_used,
                        'cost': float(execution.cost) if execution.cost else None,
                    }
            except (AgentExecution.DoesNotExist, ValueError):
                # source_id might not be a valid UUID or execution doesn't exist
                pass

        return JsonResponse({
            'success': True,
            'memory': {
                'id': str(memory.id),
                'agent_id': str(memory.agent_id),
                'agent_name': memory.agent.name,
                'title': memory.title,
                'content': memory.content,
                'context': memory.context,
                'memory_type': memory.memory_type,
                'valence': memory.valence,
                'importance_score': memory.importance_score,
                'access_count': memory.access_count,
                'source_type': memory.source_type,
                'source_id': memory.source_id,
                'created_at': memory.created_at.isoformat(),
                'last_accessed_at': memory.last_accessed_at.isoformat() if memory.last_accessed_at else None,
                'connected_memories': [
                    {
                        'id': str(c.id),
                        'title': c.title,
                        'memory_type': c.memory_type
                    }
                    for c in connected
                ],
                # Session 757: Include execution data with full content
                'execution_data': execution_data,
            }
        })
    except Exception as e:
        logger.exception(f"Error fetching memory detail: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_memory(request):
    """Create a new memory for an agent"""
    try:
        from core.models_unified_system import AgentMemory, Agent

        data = json.loads(request.body)
        agent_id = data.get('agent_id')
        title = data.get('title')
        content = data.get('content')
        memory_type = data.get('memory_type', 'interaction')
        valence = data.get('valence', 'neutral')
        importance = data.get('importance', 0.5)
        context = data.get('context', '')
        source_type = data.get('source_type', '')
        source_id = data.get('source_id', '')

        if not agent_id or not title or not content:
            return JsonResponse({
                'error': 'agent_id, title, and content are required'
            }, status=400)

        try:
            agent = Agent.objects.get(id=agent_id)
        except Agent.DoesNotExist:
            return JsonResponse({'error': 'Agent not found'}, status=404)

        # Create memory using class method (triggers embedding task)
        memory = AgentMemory.create_memory(
            agent=agent,
            title=title,
            content=content,
            memory_type=memory_type,
            valence=valence,
            importance=importance,
            context=context,
            source_type=source_type,
            source_id=source_id
        )

        return JsonResponse({
            'success': True,
            'message': f'Memory created for {agent.name}',
            'memory': {
                'id': str(memory.id),
                'title': memory.title,
                'memory_type': memory.memory_type,
                'importance_score': memory.importance_score
            }
        })
    except Exception as e:
        logger.exception(f"Error creating memory: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def search_memories(request):
    """Search memories semantically"""
    try:
        from core.models_unified_system import AgentMemory, Agent

        data = json.loads(request.body)
        agent_id = data.get('agent_id')
        query = data.get('query')
        memory_types = data.get('memory_types')
        limit = data.get('limit', 5)

        if not agent_id or not query:
            return JsonResponse({
                'error': 'agent_id and query are required'
            }, status=400)

        try:
            agent = Agent.objects.get(id=agent_id)
        except Agent.DoesNotExist:
            return JsonResponse({'error': 'Agent not found'}, status=404)

        # Use the search method from the model
        memories = AgentMemory.search_memories(
            agent=agent,
            query=query,
            limit=limit,
            memory_types=memory_types
        )

        return JsonResponse({
            'success': True,
            'query': query,
            'agent_id': str(agent_id),
            'result_count': len(memories),
            'memories': [
                {
                    'id': str(m.id),
                    'title': m.title,
                    'content': m.content[:300] + '...' if len(m.content) > 300 else m.content,
                    'memory_type': m.memory_type,
                    'valence': m.valence,
                    'importance_score': m.importance_score
                }
                for m in memories
            ]
        })
    except Exception as e:
        logger.exception(f"Error searching memories: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_memory_palace_rooms(request, agent_id):
    """Get all memory palace rooms for an agent"""
    try:
        from core.models_unified_system import MemoryPalaceRoom, Agent

        try:
            agent = Agent.objects.get(id=agent_id)
        except Agent.DoesNotExist:
            return JsonResponse({'error': 'Agent not found'}, status=404)

        rooms = MemoryPalaceRoom.objects.filter(agent=agent).order_by('name')

        # If no rooms exist, create defaults
        if not rooms.exists():
            MemoryPalaceRoom.create_default_rooms(agent)
            rooms = MemoryPalaceRoom.objects.filter(agent=agent).order_by('name')

        return JsonResponse({
            'success': True,
            'agent_id': str(agent_id),
            'agent_name': agent.name,
            'room_count': rooms.count(),
            'rooms': [
                {
                    'id': str(r.id),
                    'name': r.name,
                    'room_type': r.room_type,
                    'description': r.description,
                    'color': r.color,
                    'icon': r.icon,
                    'memory_count': r.memories.count(),
                    # Session 754: Phase 3 - Include position for visual map
                    'position_x': r.position_x,
                    'position_y': r.position_y,
                }
                for r in rooms
            ]
        })
    except Exception as e:
        logger.exception(f"Error fetching rooms: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_room_memories(request, room_id):
    """Get all memories in a specific room"""
    try:
        from core.models_unified_system import MemoryPalaceRoom

        try:
            room = MemoryPalaceRoom.objects.get(id=room_id)
        except MemoryPalaceRoom.DoesNotExist:
            return JsonResponse({'error': 'Room not found'}, status=404)

        memories = room.memories.all().order_by('-importance_score', '-created_at')[:50]

        return JsonResponse({
            'success': True,
            'room': {
                'id': str(room.id),
                'name': room.name,
                'room_type': room.room_type,
                'description': room.description,
                'color': room.color
            },
            'agent_name': room.agent.name,
            'memory_count': memories.count(),
            'memories': [
                {
                    'id': str(m.id),
                    'title': m.title,
                    'content': m.content[:200] + '...' if len(m.content) > 200 else m.content,
                    'memory_type': m.memory_type,
                    'valence': m.valence,
                    'importance_score': m.importance_score
                }
                for m in memories
            ]
        })
    except Exception as e:
        logger.exception(f"Error fetching room memories: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def assign_memory_to_room(request):
    """Assign a memory to a room"""
    try:
        from core.models_unified_system import AgentMemory, MemoryPalaceRoom

        data = json.loads(request.body)
        memory_id = data.get('memory_id')
        room_id = data.get('room_id')

        if not memory_id or not room_id:
            return JsonResponse({
                'error': 'memory_id and room_id are required'
            }, status=400)

        try:
            # Session 810: Defer embedding fields to reduce egress costs
            memory = AgentMemory.objects.defer('embedding').get(id=memory_id)
            room = MemoryPalaceRoom.objects.get(id=room_id)
        except (AgentMemory.DoesNotExist, MemoryPalaceRoom.DoesNotExist) as e:
            return JsonResponse({'error': str(e)}, status=404)

        # Verify same agent
        if memory.agent_id != room.agent_id:
            return JsonResponse({
                'error': 'Memory and room must belong to same agent'
            }, status=400)

        room.memories.add(memory)

        return JsonResponse({
            'success': True,
            'message': f'Memory "{memory.title}" added to room "{room.name}"'
        })
    except Exception as e:
        logger.exception(f"Error assigning memory to room: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_memory_summary(request, agent_id):
    """Get a prompt-friendly summary of agent memories"""
    try:
        from core.models_unified_system import AgentMemory, Agent

        try:
            agent = Agent.objects.get(id=agent_id)
        except Agent.DoesNotExist:
            return JsonResponse({'error': 'Agent not found'}, status=404)

        limit = int(request.GET.get('limit', 10))
        summary = AgentMemory.get_memory_summary(agent, limit=limit)

        # Get memory stats
        total_memories = AgentMemory.objects.filter(agent=agent).count()
        memory_types = AgentMemory.objects.filter(agent=agent).values('memory_type').distinct().count()

        return JsonResponse({
            'success': True,
            'agent_id': str(agent_id),
            'agent_name': agent.name,
            'total_memories': total_memories,
            'memory_type_count': memory_types,
            'summary': summary,
            'prompt_injection': f"\n---\n{agent.name}'s Memory Context:\n{summary}\n---\n" if summary else ""
        })
    except Exception as e:
        logger.exception(f"Error getting memory summary: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def connect_memories(request):
    """Create a connection between two memories"""
    try:
        from core.models_unified_system import AgentMemory, MemoryConnection

        data = json.loads(request.body)
        source_id = data.get('source_id')
        target_id = data.get('target_id')
        connection_type = data.get('connection_type', 'similar')
        strength = data.get('strength', 0.5)

        if not source_id or not target_id:
            return JsonResponse({
                'error': 'source_id and target_id are required'
            }, status=400)

        try:
            # Session 810: Defer embedding fields to reduce egress costs
            source = AgentMemory.objects.defer('embedding').get(id=source_id)
            target = AgentMemory.objects.defer('embedding').get(id=target_id)
        except AgentMemory.DoesNotExist as e:
            return JsonResponse({'error': str(e)}, status=404)

        # Create the connection
        # Session 729: Fixed field names (source_memory/target_memory → memory_from/memory_to)
        connection, created = MemoryConnection.objects.get_or_create(
            memory_from=source,
            memory_to=target,
            defaults={
                'connection_type': connection_type,
                'strength': strength
            }
        )

        if not created:
            connection.strength = strength
            connection.save()

        # Also add to M2M relationship
        source.connected_memories.add(target)

        return JsonResponse({
            'success': True,
            'created': created,
            'connection': {
                'id': str(connection.id),
                'source': source.title,
                'target': target.title,
                'type': connection_type,
                'strength': strength
            }
        })
    except Exception as e:
        logger.exception(f"Error connecting memories: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_memory_connections(request, memory_id):
    """Get all connections for a memory"""
    try:
        from core.models_unified_system import AgentMemory, MemoryConnection

        try:
            # Session 810: Defer embedding fields to reduce egress costs
            memory = AgentMemory.objects.defer('embedding').get(id=memory_id)
        except AgentMemory.DoesNotExist:
            return JsonResponse({'error': 'Memory not found'}, status=404)

        # Get outgoing connections
        # Session 729: Fixed field names (source_memory/target_memory → memory_from/memory_to)
        outgoing = MemoryConnection.objects.filter(memory_from=memory)
        incoming = MemoryConnection.objects.filter(memory_to=memory)

        return JsonResponse({
            'success': True,
            'memory_id': str(memory_id),
            'memory_title': memory.title,
            'connections': {
                'outgoing': [
                    {
                        'id': str(c.id),
                        'target_id': str(c.memory_to_id),
                        'target_title': c.memory_to.title,
                        'type': c.connection_type,
                        'strength': c.strength
                    }
                    for c in outgoing
                ],
                'incoming': [
                    {
                        'id': str(c.id),
                        'source_id': str(c.memory_from_id),
                        'source_title': c.memory_from.title,
                        'type': c.connection_type,
                        'strength': c.strength
                    }
                    for c in incoming
                ]
            }
        })
    except Exception as e:
        logger.exception(f"Error getting memory connections: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_memory_palace_overview(request):
    """
    Get overview of all agents' memory palaces.
    Session 860: Added safety_class stats for frontend Memory Palace tab.
    """
    try:
        from core.models_unified_system import AgentMemory, Agent
        from django.db.models import Count, Avg

        # Get agents with memory stats
        agents_with_memories = Agent.objects.annotate(
            memory_count=Count('memories'),
            avg_importance=Avg('memories__importance_score')
        ).filter(memory_count__gt=0).order_by('-memory_count')[:20]

        # Get overall stats
        total_memories = AgentMemory.objects.count()
        memory_by_type = AgentMemory.objects.values('memory_type').annotate(
            count=Count('id')
        ).order_by('-count')

        # Session 860: Add safety class stats
        safety_by_class = AgentMemory.objects.values('safety_class').annotate(
            count=Count('id')
        )
        safety_counts = {item['safety_class']: item['count'] for item in safety_by_class}

        return JsonResponse({
            'success': True,
            'overview': {
                'total_memories': total_memories,
                'agents_with_memories': agents_with_memories.count(),
                'memory_types': list(memory_by_type),
                # Session 860: Safety class breakdown
                'approved_count': safety_counts.get('approved', 0),
                'candidate_count': safety_counts.get('candidate', 0),
                'exploratory_count': safety_counts.get('exploratory', 0),
                'test_only_count': safety_counts.get('test_only', 0),
            },
            'agents': [
                {
                    'id': str(a.id),
                    'name': a.name,
                    'memory_count': a.memory_count,
                    'avg_importance': round(a.avg_importance or 0, 2)
                }
                for a in agents_with_memories
            ]
        })
    except Exception as e:
        logger.exception(f"Error getting palace overview: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_memory(request, memory_id):
    """Delete a memory"""
    try:
        from core.models_unified_system import AgentMemory

        try:
            # Session 810: Defer embedding fields to reduce egress costs
            memory = AgentMemory.objects.defer('embedding').get(id=memory_id)
        except AgentMemory.DoesNotExist:
            return JsonResponse({'error': 'Memory not found'}, status=404)

        title = memory.title
        memory.delete()

        return JsonResponse({
            'success': True,
            'message': f'Memory "{title}" deleted'
        })
    except Exception as e:
        logger.exception(f"Error deleting memory: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_all_memories(request):
    """
    Session 860: List all memories across all agents with filtering.
    Supports: safety_class, memory_type, valence, limit, offset
    """
    try:
        from core.models_unified_system import AgentMemory
        from django.db.models import F

        # Parse query params
        safety_class = request.GET.get('safety_class')
        memory_type = request.GET.get('memory_type')
        valence = request.GET.get('valence')
        limit = min(int(request.GET.get('limit', 20)), 100)
        offset = int(request.GET.get('offset', 0))

        # Build query - defer embedding fields to reduce egress
        queryset = AgentMemory.objects.defer('embedding').select_related('agent')

        # Apply filters
        if safety_class:
            queryset = queryset.filter(safety_class=safety_class)
        if memory_type:
            queryset = queryset.filter(memory_type=memory_type)
        if valence:
            queryset = queryset.filter(valence=valence)

        # Get total count before pagination
        total_count = queryset.count()

        # Order by importance and recency, then paginate
        memories = queryset.order_by('-importance_score', '-created_at')[offset:offset + limit]

        return JsonResponse({
            'success': True,
            'count': total_count,
            'limit': limit,
            'offset': offset,
            'memories': [
                {
                    'id': str(m.id),
                    'title': m.title,
                    'content': m.content[:300] + '...' if len(m.content) > 300 else m.content,
                    'memory_type': m.memory_type,
                    'safety_class': m.safety_class,
                    'valence': m.valence,
                    'importance_score': m.importance_score,
                    'agent_id': str(m.agent_id),
                    'agent_name': m.agent.name if m.agent else 'Unknown',
                    'created_at': m.created_at.isoformat() if m.created_at else None,
                    'memory_outcome': getattr(m, 'memory_outcome', None),
                    'source_id': m.source_id or '',
                    'tags': m.tags or [],
                }
                for m in memories
            ]
        })
    except Exception as e:
        logger.exception(f"Error listing memories: {e}")
        return JsonResponse({'error': str(e)}, status=500)
