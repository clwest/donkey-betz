"""
Session 257: Memory Clusters API Views

API endpoints for managing agent memory clusters - semantic grouping of memories
using embedding-based clustering for emergent knowledge organization.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from core.models_unified_system import (
    Agent, AgentMemory, MemoryCluster, MemoryClusterMembership, ClusterEvolution
)

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def clusters_overview(request):
    """
    GET /api/memory-clusters/

    Overview of all memory clusters across agents.
    """
    try:
        clusters = MemoryCluster.objects.select_related('agent').all()

        # Build stats
        total_clusters = clusters.count()
        clusters_by_agent = {}
        # Session 746: Track agents with clusters for easy lookup
        agents_with_clusters_map = {}

        for cluster in clusters:
            agent_name = cluster.agent.name if cluster.agent else "Cross-Agent"
            agent_id = str(cluster.agent.id) if cluster.agent else None
            if agent_name not in clusters_by_agent:
                clusters_by_agent[agent_name] = []
                # Session 746: Add to agents map
                if agent_id:
                    agents_with_clusters_map[agent_name] = {
                        'id': agent_id,
                        'name': agent_name,
                    }
            clusters_by_agent[agent_name].append({
                'id': str(cluster.id),
                'agent_id': agent_id,  # Session 746: Include agent_id for frontend navigation
                'name': cluster.name,
                'description': cluster.description,
                'memory_count': cluster.memories.count(),
                'coherence_score': cluster.coherence_score,
                'color': cluster.color,
                'icon': cluster.icon,
                'keywords': cluster.keywords,
                'created_at': cluster.created_at.isoformat(),
            })

        # Get agents without clusters (for "generate" button)
        agents_with_memories = Agent.objects.filter(
            memories__embedding__isnull=False
        ).distinct().annotate(
            memory_count_with_embeddings=models.Count('memories')
        )

        agents_needing_clusters = []
        for agent in agents_with_memories:
            if agent.name not in clusters_by_agent:
                memory_count = AgentMemory.objects.filter(
                    agent=agent, embedding__isnull=False
                ).count()
                if memory_count >= 5:
                    agents_needing_clusters.append({
                        'id': str(agent.id),
                        'name': agent.name,
                        'memory_count': memory_count,
                    })

        return JsonResponse({
            'success': True,
            'stats': {
                'total_clusters': total_clusters,
                'agents_with_clusters': len(clusters_by_agent),
            },
            'clusters_by_agent': clusters_by_agent,
            'agents_with_clusters_list': list(agents_with_clusters_map.values()),  # Session 746: Easy agent lookup
            'agents_needing_clusters': agents_needing_clusters,
        })

    except Exception as e:
        logger.error(f"Error in clusters_overview: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Fix the import at top - need to import models
from django.db import models


@csrf_exempt
@require_http_methods(["GET", "POST"])
def agent_clusters(request, agent_id):
    """
    GET /api/memory-clusters/agent/<agent_id>/
    List clusters for a specific agent.

    POST /api/memory-clusters/agent/<agent_id>/
    Generate clusters for an agent (runs clustering algorithm).
    """
    try:
        agent = Agent.objects.get(id=agent_id)
    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)

    if request.method == 'GET':
        clusters = MemoryCluster.objects.filter(agent=agent).prefetch_related('memories')

        cluster_list = []
        for cluster in clusters:
            memberships = cluster.memberships.select_related('memory').all()[:10]

            cluster_list.append({
                'id': str(cluster.id),
                'name': cluster.name,
                'description': cluster.description,
                'keywords': cluster.keywords,
                'color': cluster.color,
                'icon': cluster.icon,
                'coherence_score': cluster.coherence_score,
                'stability_score': cluster.stability_score,
                'memory_count': cluster.memories.count(),
                'cluster_method': cluster.cluster_method,
                'version': cluster.version,
                'last_clustered_at': cluster.last_clustered_at.isoformat() if cluster.last_clustered_at else None,
                'created_at': cluster.created_at.isoformat(),
                'top_memories': [
                    {
                        'id': str(m.memory.id),
                        'title': m.memory.title,
                        'memory_type': m.memory.memory_type,
                        'similarity': m.similarity_to_centroid,
                        'is_core': m.is_core_member,
                    }
                    for m in memberships
                ],
            })

        return JsonResponse({
            'success': True,
            'agent': {
                'id': str(agent.id),
                'name': agent.name,
            },
            'clusters': cluster_list,
        })

    elif request.method == 'POST':
        # Generate new clusters
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = {}

        n_clusters = data.get('n_clusters')  # None = auto-detect
        method = data.get('method', 'semantic')
        min_memories = data.get('min_memories', 5)

        # Delete existing clusters for this agent before regenerating
        old_cluster_count = MemoryCluster.objects.filter(agent=agent).count()
        if old_cluster_count > 0:
            MemoryCluster.objects.filter(agent=agent).delete()

        # Run clustering
        new_clusters = MemoryCluster.cluster_agent_memories(
            agent=agent,
            n_clusters=n_clusters,
            min_memories=min_memories,
            method=method
        )

        # Record evolution event
        ClusterEvolution.objects.create(
            agent=agent,
            event_type='created',
            details={
                'method': method,
                'n_clusters': len(new_clusters),
                'previous_clusters': old_cluster_count,
            },
            memories_after=sum(c.memories.count() for c in new_clusters),
            coherence_after=sum(c.coherence_score for c in new_clusters) / len(new_clusters) if new_clusters else 0,
        )

        return JsonResponse({
            'success': True,
            'message': f'Generated {len(new_clusters)} clusters for {agent.name}',
            'clusters': [
                {
                    'id': str(c.id),
                    'name': c.name,
                    'memory_count': c.memories.count(),
                    'coherence_score': c.coherence_score,
                    'color': c.color,
                }
                for c in new_clusters
            ],
        })


@csrf_exempt
@require_http_methods(["GET"])
def cluster_detail(request, cluster_id):
    """
    GET /api/memory-clusters/cluster/<cluster_id>/

    Get detailed view of a specific cluster including all memories and their positions.
    """
    try:
        cluster = MemoryCluster.objects.get(id=cluster_id)
    except MemoryCluster.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cluster not found'}, status=404)

    # Get all memberships with memory details
    memberships = cluster.memberships.select_related('memory').all()

    memories = []
    for m in memberships:
        memories.append({
            'id': str(m.memory.id),
            'title': m.memory.title,
            'content': m.memory.content[:300] + '...' if len(m.memory.content) > 300 else m.memory.content,
            'memory_type': m.memory.memory_type,
            'valence': m.memory.valence,
            'importance_score': m.memory.importance_score,
            'similarity_to_centroid': m.similarity_to_centroid,
            'is_core_member': m.is_core_member,
            'position_x': m.position_x,
            'position_y': m.position_y,
            'created_at': m.memory.created_at.isoformat(),
            # Session 746: Include memory outcome for filtering
            'memory_outcome': m.memory.memory_outcome,
        })

    # Get related clusters
    related = cluster.related_clusters.all()
    related_list = [
        {
            'id': str(r.id),
            'name': r.name,
            'color': r.color,
        }
        for r in related
    ]

    # Get sub-clusters if any
    sub_clusters = cluster.sub_clusters.all()
    sub_cluster_list = [
        {
            'id': str(s.id),
            'name': s.name,
            'color': s.color,
            'memory_count': s.memories.count(),
        }
        for s in sub_clusters
    ]

    return JsonResponse({
        'success': True,
        'cluster': {
            'id': str(cluster.id),
            'name': cluster.name,
            'description': cluster.description,
            'keywords': cluster.keywords,
            'color': cluster.color,
            'icon': cluster.icon,
            'coherence_score': cluster.coherence_score,
            'stability_score': cluster.stability_score,
            'cluster_method': cluster.cluster_method,
            'cluster_type': cluster.cluster_type,  # Session 746: Include cluster type
            'version': cluster.version,
            'last_clustered_at': cluster.last_clustered_at.isoformat() if cluster.last_clustered_at else None,
            'memory_count': len(memories),
            'agent': {
                'id': str(cluster.agent.id) if cluster.agent else None,
                'name': cluster.agent.name if cluster.agent else "Cross-Agent",
            },
            'parent_cluster': {
                'id': str(cluster.parent_cluster.id),
                'name': cluster.parent_cluster.name,
            } if cluster.parent_cluster else None,
        },
        'memories': memories,
        'related_clusters': related_list,
        'sub_clusters': sub_cluster_list,
    })


@csrf_exempt
@require_http_methods(["GET"])
def cluster_visualization_data(request, agent_id=None):
    """
    GET /api/memory-clusters/visualization/
    GET /api/memory-clusters/visualization/<agent_id>/

    Get data formatted for D3.js force-directed graph visualization.
    Returns nodes (clusters and memories) and links (connections).
    """
    try:
        if agent_id:
            agent = Agent.objects.get(id=agent_id)
            clusters = MemoryCluster.objects.filter(agent=agent)
        else:
            clusters = MemoryCluster.objects.all()

        nodes = []
        links = []

        for cluster in clusters:
            # Add cluster as a node
            cluster_node = {
                'id': f"cluster_{cluster.id}",
                'type': 'cluster',
                'name': cluster.name,
                'color': cluster.color,
                'size': 20 + (cluster.memories.count() * 2),  # Size based on memory count
                'coherence': cluster.coherence_score,
            }
            nodes.append(cluster_node)

            # Add memories as nodes
            memberships = cluster.memberships.select_related('memory').all()
            for m in memberships:
                memory_node = {
                    'id': f"memory_{m.memory.id}",
                    'type': 'memory',
                    'name': m.memory.title[:30],
                    'memory_type': m.memory.memory_type,
                    'color': _get_memory_color(m.memory.memory_type),
                    'size': 5 + (m.memory.importance_score * 10),
                    'similarity': m.similarity_to_centroid,
                    'is_core': m.is_core_member,
                }
                nodes.append(memory_node)

                # Link memory to cluster
                links.append({
                    'source': f"memory_{m.memory.id}",
                    'target': f"cluster_{cluster.id}",
                    'strength': m.similarity_to_centroid,
                })

            # Add links between related clusters
            for related in cluster.related_clusters.all():
                # Only add link once (avoid duplicates)
                if str(cluster.id) < str(related.id):
                    links.append({
                        'source': f"cluster_{cluster.id}",
                        'target': f"cluster_{related.id}",
                        'strength': 0.5,
                        'type': 'related',
                    })

        return JsonResponse({
            'success': True,
            'nodes': nodes,
            'links': links,
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in cluster_visualization_data: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def _get_memory_color(memory_type):
    """Get color for memory type."""
    colors = {
        'success': '#22c55e',
        'failure': '#ef4444',
        'preference': '#eab308',
        'technique': '#06b6d4',
        'insight': '#8b5cf6',
        'interaction': '#3b82f6',
        'feedback': '#f97316',
    }
    return colors.get(memory_type, '#6b7280')


@csrf_exempt
@require_http_methods(["POST"])
def generate_all_clusters(request):
    """
    POST /api/memory-clusters/generate-all/

    Generate clusters for all agents that have sufficient memories.
    """
    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = {}

    min_memories = data.get('min_memories', 5)
    method = data.get('method', 'semantic')

    # Find agents with enough memories
    agents = Agent.objects.all()
    results = []

    for agent in agents:
        memory_count = AgentMemory.objects.filter(
            agent=agent, embedding__isnull=False
        ).count()

        if memory_count >= min_memories:
            # Delete existing clusters
            MemoryCluster.objects.filter(agent=agent).delete()

            # Generate new clusters
            new_clusters = MemoryCluster.cluster_agent_memories(
                agent=agent,
                min_memories=min_memories,
                method=method
            )

            results.append({
                'agent': agent.name,
                'clusters_created': len(new_clusters),
                'total_memories': memory_count,
            })

    return JsonResponse({
        'success': True,
        'message': f'Generated clusters for {len(results)} agents',
        'results': results,
    })


@csrf_exempt
@require_http_methods(["POST"])
def add_memory_to_cluster(request, cluster_id):
    """
    POST /api/memory-clusters/cluster/<cluster_id>/add-memory/

    Manually add a memory to a cluster.
    """
    try:
        cluster = MemoryCluster.objects.get(id=cluster_id)
    except MemoryCluster.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cluster not found'}, status=404)

    try:
        data = json.loads(request.body)
        memory_id = data.get('memory_id')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    if not memory_id:
        return JsonResponse({'success': False, 'error': 'memory_id required'}, status=400)

    try:
        memory = AgentMemory.objects.get(id=memory_id)
    except AgentMemory.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Memory not found'}, status=404)

    # Create membership
    membership, created = MemoryClusterMembership.objects.get_or_create(
        cluster=cluster,
        memory=memory,
        defaults={'similarity_to_centroid': 0.5}
    )

    if not created:
        return JsonResponse({'success': False, 'error': 'Memory already in cluster'}, status=400)

    # Recalculate cluster metrics
    cluster.calculate_centroid()
    cluster.calculate_coherence()
    cluster.update_member_similarities()

    return JsonResponse({
        'success': True,
        'message': f'Added memory to cluster',
        'membership': {
            'id': str(membership.id),
            'similarity': membership.similarity_to_centroid,
        },
    })


@csrf_exempt
@require_http_methods(["DELETE"])
def remove_memory_from_cluster(request, cluster_id, memory_id):
    """
    DELETE /api/memory-clusters/cluster/<cluster_id>/memory/<memory_id>/

    Remove a memory from a cluster.
    """
    try:
        membership = MemoryClusterMembership.objects.get(
            cluster_id=cluster_id,
            memory_id=memory_id
        )
    except MemoryClusterMembership.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Membership not found'}, status=404)

    cluster = membership.cluster
    membership.delete()

    # Recalculate cluster metrics
    cluster.calculate_centroid()
    cluster.calculate_coherence()

    return JsonResponse({
        'success': True,
        'message': 'Memory removed from cluster',
    })


@csrf_exempt
@require_http_methods(["GET"])
def cluster_evolution(request, agent_id):
    """
    GET /api/memory-clusters/evolution/<agent_id>/

    Get cluster evolution history for an agent.
    """
    try:
        agent = Agent.objects.get(id=agent_id)
    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)

    events = ClusterEvolution.objects.filter(agent=agent).order_by('-created_at')[:50]

    return JsonResponse({
        'success': True,
        'agent': {
            'id': str(agent.id),
            'name': agent.name,
        },
        'events': [
            {
                'id': str(e.id),
                'event_type': e.event_type,
                'cluster_name': e.cluster.name if e.cluster else None,
                'details': e.details,
                'memories_before': e.memories_before,
                'memories_after': e.memories_after,
                'coherence_before': e.coherence_before,
                'coherence_after': e.coherence_after,
                'created_at': e.created_at.isoformat(),
            }
            for e in events
        ],
    })


@csrf_exempt
@require_http_methods(["POST"])
def find_similar_clusters(request):
    """
    POST /api/memory-clusters/find-similar/

    Find clusters similar to a given query or memory.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    query = data.get('query')
    memory_id = data.get('memory_id')
    limit = data.get('limit', 5)

    if not query and not memory_id:
        return JsonResponse({'success': False, 'error': 'query or memory_id required'}, status=400)

    import numpy as np

    # Get query embedding
    if memory_id:
        try:
            memory = AgentMemory.objects.get(id=memory_id)
            if not memory.embedding:
                return JsonResponse({'success': False, 'error': 'Memory has no embedding'}, status=400)
            query_embedding = np.array(memory.embedding)
        except AgentMemory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Memory not found'}, status=404)
    else:
        # Generate embedding for query
        from core.services.openai_client_factory import get_openai_client
        import os

        try:
            client = get_openai_client(api_key=os.environ.get('OPENAI_API_KEY'))
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            query_embedding = np.array(response.data[0].embedding)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Embedding error: {e}'}, status=500)

    # Find similar clusters
    clusters = MemoryCluster.objects.filter(centroid_embedding__isnull=False)

    similarities = []
    for cluster in clusters:
        centroid = np.array(cluster.centroid_embedding)
        similarity = np.dot(query_embedding, centroid) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(centroid)
        )
        similarities.append((cluster, float(similarity)))

    # Sort by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)

    return JsonResponse({
        'success': True,
        'similar_clusters': [
            {
                'id': str(c.id),
                'name': c.name,
                'description': c.description,
                'color': c.color,
                'similarity': sim,
                'agent': c.agent.name if c.agent else "Cross-Agent",
                'memory_count': c.memories.count(),
            }
            for c, sim in similarities[:limit]
        ],
    })
