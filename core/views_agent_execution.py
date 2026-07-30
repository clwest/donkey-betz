"""
Enhanced Agent Execution Views

Provides synchronous agent execution without requiring Celery,
making agents immediately available for testing and use.
"""

import logging
import asyncio
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Import the concrete executor
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_core.agents.concrete_executor import get_concrete_executor, execute_agent_directly

from core.security.object_authz import scope_queryset_agent_execution

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow any for testing, add auth later
def execute_agent_sync(request):
    """
    Execute an agent synchronously without Celery.

    This endpoint allows immediate agent execution for testing and development.

    Request body:
    {
        "agent_name": "intelligent_job_matcher",
        "task_description": "Find AI jobs",
        "input_data": {
            "skills": ["python", "AI"],
            "location": "remote"
        }
    }
    """
    try:
        # Extract parameters
        agent_name = request.data.get('agent_name')

        if not agent_name:
            return Response({
                'success': False,
                'error': 'agent_name is required',
                'available_agents': get_concrete_executor().list_available_agents()
            }, status=400)

        # Prepare task configuration
        task = {
            'task_description': request.data.get('task_description', ''),
            'input': request.data.get('input_data', {}),
            'context': request.data.get('context', {}),
            'task_type': request.data.get('task_type', 'general')
        }

        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None

        logger.info(f"🚀 Executing agent '{agent_name}' synchronously")

        # Execute the agent using asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                execute_agent_directly(agent_name, task, user)
            )
        finally:
            loop.close()

        # Return the result
        if result['success']:
            return Response({
                'success': True,
                'data': result,
                'message': f"Agent '{agent_name}' executed successfully"
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'traceback': result.get('traceback', ''),
                'agent': agent_name
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Error in execute_agent_sync: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Failed to execute agent'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_executable_agents(request):
    """
    List all agents that can be executed directly.

    Returns information about available agents and their capabilities.
    """
    try:
        agents = get_concrete_executor().list_available_agents()

        return Response({
            'success': True,
            'data': {
                'total_agents': len(agents),
                'agents': agents,
                'executor_type': 'ConcreteAgentExecutor',
                'features': {
                    'synchronous_execution': True,
                    'ai_enforced': True,
                    'user_context_aware': True,
                    'no_celery_required': True
                }
            }
        })
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def agent_execution_history(request):
    """
    Get recent agent execution history.
    """
    try:
        limit = int(request.GET.get('limit', 10))
        history = get_concrete_executor().get_execution_history(limit)

        return Response({
            'success': True,
            'data': {
                'history': history,
                'count': len(history),
                'limit': limit
            }
        })
    except Exception as e:
        logger.error(f"Error getting execution history: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def test_agent_execution(request):
    """
    Test endpoint for agent execution with sample data.

    Provides easy testing with pre-configured examples.
    """
    try:
        agent_type = request.data.get('agent_type', 'content')

        # Sample test configurations
        test_configs = {
            'content': {
                'agent_name': 'real_content_creator',
                'task': {
                    'task_description': 'Create blog post about AI trends',
                    'input': {
                        'topic': 'AI Trends in 2025',
                        'type': 'blog',
                        'keywords': ['AI', 'machine learning', 'automation', '2025'],
                        'word_count': 500
                    }
                }
            },
            'job': {
                'agent_name': 'intelligent_job_matcher',
                'task': {
                    'task_description': 'Find remote Python developer jobs',
                    'input': {
                        'skills': ['Python', 'Django', 'React', 'AI'],
                        'experience_level': 'mid',
                        'location': 'remote',
                        'salary_range': {
                            'min': 80000,
                            'max': 150000
                        }
                    }
                }
            },
            'income': {
                'agent_name': 'zero_capital_income_generator',
                'task': {
                    'task_description': 'Generate income plan for $1000 in 30 days',
                    'input': {
                        'target_income': 1000,
                        'timeframe_days': 30,
                        'skill_level': 'intermediate'
                    }
                }
            }
        }

        if agent_type not in test_configs:
            return Response({
                'success': False,
                'error': f'Unknown agent type: {agent_type}',
                'available_types': list(test_configs.keys())
            }, status=400)

        config = test_configs[agent_type]
        user = request.user if request.user.is_authenticated else None

        logger.info(f"🧪 Testing {agent_type} agent: {config['agent_name']}")

        # Execute the test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                execute_agent_directly(config['agent_name'], config['task'], user)
            )
        finally:
            loop.close()

        return Response({
            'success': True,
            'test_type': agent_type,
            'agent': config['agent_name'],
            'result': result
        })

    except Exception as e:
        logger.error(f"❌ Error in test execution: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def execute_agent_batch(request):
    """
    Execute multiple agents in sequence or parallel.

    Request body:
    {
        "agents": [
            {
                "agent_name": "intelligent_job_matcher",
                "input_data": {...}
            },
            {
                "agent_name": "job_application_agent",
                "input_data": {...}
            }
        ],
        "execution_mode": "sequential"  # or "parallel"
    }
    """
    try:
        agents = request.data.get('agents', [])
        execution_mode = request.data.get('execution_mode', 'sequential')

        if not agents:
            return Response({
                'success': False,
                'error': 'No agents provided'
            }, status=400)

        user = request.user if request.user.is_authenticated else None
        results = []

        async def execute_agents():
            if execution_mode == 'parallel':
                # Execute all agents in parallel
                tasks = []
                for agent_config in agents:
                    task = {
                        'task_description': agent_config.get('task_description', ''),
                        'input': agent_config.get('input_data', {})
                    }
                    tasks.append(
                        execute_agent_directly(
                            agent_config['agent_name'],
                            task,
                            user
                        )
                    )
                return await asyncio.gather(*tasks)
            else:
                # Execute agents sequentially
                agent_results = []
                for agent_config in agents:
                    task = {
                        'task_description': agent_config.get('task_description', ''),
                        'input': agent_config.get('input_data', {})
                    }
                    result = await execute_agent_directly(
                        agent_config['agent_name'],
                        task,
                        user
                    )
                    agent_results.append(result)
                return agent_results

        # Run the execution
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(execute_agents())
        finally:
            loop.close()

        # Analyze results
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful

        return Response({
            'success': True,
            'data': {
                'total_agents': len(agents),
                'successful': successful,
                'failed': failed,
                'execution_mode': execution_mode,
                'results': results
            }
        })

    except Exception as e:
        logger.error(f"❌ Error in batch execution: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# Session 760: Agent Execution Detail APIs for Output Modal


def _extract_task_summary(task: str) -> str:
    """
    Session 958: Extract a clean task summary from the full task text.

    Tasks often contain:
    - Markdown headers like '## EXISTING CODEBASE CONTEXT'
    - Bullet points like '- Check if...'
    - Context sections starting with '**IMPORTANT:**'

    This extracts the first meaningful line that describes the actual task.
    """
    if not task:
        return 'Agent execution'

    # Remove common context markers
    context_markers = [
        '## EXISTING CODEBASE CONTEXT',
        '**IMPORTANT:**',
        '## Context',
        '## Background',
        'IMPORTANT:',
    ]

    # Find where context section starts and truncate
    task_clean = task
    for marker in context_markers:
        if marker in task_clean:
            task_clean = task_clean.split(marker)[0]

    # Split into lines and find first meaningful line
    lines = task_clean.strip().split('\n')
    for line in lines:
        line = line.strip()
        # Skip empty lines, headers, and pure markdown
        if not line:
            continue
        if line.startswith('#'):
            # Extract text after # header
            line = line.lstrip('#').strip()
        if line.startswith('-') or line.startswith('*'):
            # Extract text after bullet
            line = line.lstrip('-*').strip()

        # Clean up markdown formatting
        line = line.replace('`', '').replace('**', '').replace('__', '')

        # Return first substantial line
        if len(line) > 10:
            return line[:150] + ('...' if len(line) > 150 else '')

    # Fallback: return truncated original
    return task[:100] + ('...' if len(task) > 100 else '')


@api_view(['GET'])
@permission_classes([AllowAny])
def unified_execution_history(request):
    """
    Get agent execution history from the unified system with full output_data.

    Query params:
    - limit: Number of executions to return (default 20)
    - agent_name: Filter by agent name (optional)
    - status: Filter by status (optional)
    """
    try:
        from core.models_unified_system import AgentExecution

        limit = max(1, min(int(request.GET.get('limit', 20)), 200))
        offset = max(0, int(request.GET.get('offset', 0)))
        agent_name = request.GET.get('agent_name')
        status = request.GET.get('status')

        # I-0302 Phase 3 Sub-phase B2a: scoped to user via scope_queryset_agent_execution.
        queryset = scope_queryset_agent_execution(
            request.user,
            AgentExecution.objects.select_related('agent'),
        ).order_by('-created_at')

        if agent_name:
            queryset = queryset.filter(agent__name__icontains=agent_name)
        if status:
            queryset = queryset.filter(status=status)

        total_count = queryset.count()
        executions = list(queryset[offset:offset + limit])
        has_more = (offset + len(executions)) < total_count

        return Response({
            'success': True,
            'data': {
                'executions': [
                    {
                        'id': str(ex.id),
                        'agent_name': ex.agent.name if ex.agent else 'Unknown',
                        'task': ex.task[:500] if ex.task else None,  # Full task for modal
                        'task_summary': _extract_task_summary(ex.task),  # Session 958: Clean summary
                        'status': ex.status,
                        'output_data': ex.output_data,
                        'error_message': ex.error_message,
                        'tokens_used': ex.tokens_used,
                        'cost': float(ex.cost) if ex.cost else 0,
                        'execution_time_ms': ex.execution_time_ms,
                        'created_at': ex.created_at.isoformat(),
                        'completed_at': ex.completed_at.isoformat() if ex.completed_at else None,
                        'last_heartbeat_at': ex.last_heartbeat_at.isoformat() if getattr(ex, 'last_heartbeat_at', None) else None,
                    }
                    for ex in executions
                ],
                'count': len(executions),
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': has_more,
            }
        })
    except Exception as e:
        logger.error(f"Error getting unified execution history: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def execution_detail(request, execution_id):
    """
    Get detailed information about a specific execution including full output_data.

    Session 760: Created for Agent Output Detail Modal
    """
    try:
        from core.models_unified_system import AgentExecution, AgentMemory

        try:
            # I-0302 Phase 3 Sub-phase B2a: query-time scoping via
            # scope_queryset_agent_execution captures the null-user
            # superuser carve-out (a plain `.filter(user=…)` would exclude
            # null-user Celery runs for superusers).
            execution = scope_queryset_agent_execution(
                request.user,
                AgentExecution.objects.select_related('agent'),
            ).get(id=execution_id)
        except AgentExecution.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Execution {execution_id} not found'
            }, status=404)

        # Get related memory if exists
        related_memory = None
        if execution.agent:
            memory = AgentMemory.objects.filter(
                agent=execution.agent,
                source_type='execution',
                created_at__gte=execution.created_at
            ).first()
            if memory:
                related_memory = {
                    'id': str(memory.id),
                    'title': memory.title,
                    'content': memory.content,
                    'valence': memory.valence,
                    'memory_type': memory.memory_type,
                    'importance_score': memory.importance_score,
                }

        # S3047: surface S3046 lineage + fanout fields on the REST detail payload
        # via shared helper (core/services/agent_fanout.compute_fanout) so the PA
        # tool + REST endpoint cannot drift on child/subtree semantics.
        # S3047 follow-up: pass a scoped queryset into the helper so child/subtree
        # queries filter cross-user rows — discharges the A2 SIGN Q4 future_trigger
        # child-row auth-leak fold. Parent execution is already scoped above via
        # scope_queryset_agent_execution.get(); the helper scope-applies to the
        # descendant queries so a bug-written cross-user parent_execution_id
        # cannot leak child rows into the response.
        from core.services.agent_fanout import compute_fanout

        scoped_qs = scope_queryset_agent_execution(
            request.user,
            AgentExecution.objects.all(),
        )

        return Response({
            'success': True,
            'data': {
                'execution': {
                    'id': str(execution.id),
                    'agent_name': execution.agent.name if execution.agent else 'Unknown',
                    'agent_display_name': execution.agent.name if execution.agent else None,
                    'task': execution.task,
                    'status': execution.status,
                    'output_data': execution.output_data,
                    'input_data': execution.input_data,
                    'error_message': execution.error_message,
                    'tokens_used': execution.tokens_used,
                    'cost': float(execution.cost) if execution.cost else 0,
                    'execution_time_ms': execution.execution_time_ms,
                    'created_at': execution.created_at.isoformat(),
                    'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                    'last_heartbeat_at': execution.last_heartbeat_at.isoformat() if getattr(execution, 'last_heartbeat_at', None) else None,
                    **compute_fanout(execution, scoped_queryset=scoped_qs),
                },
                'related_memory': related_memory
            }
        })
    except Exception as e:
        logger.error(f"Error getting execution detail: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 761: Agent Monitoring Dashboard APIs
# Provides performance metrics, success rates, and execution statistics
# =============================================================================

def _format_uptime(boot_time):
    """Format boot time as human-readable uptime string."""
    import time
    from datetime import timedelta
    uptime_seconds = time.time() - boot_time
    td = timedelta(seconds=int(uptime_seconds))
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


@api_view(['GET'])
@permission_classes([AllowAny])
def monitoring_dashboard(request):
    """
    Get agent monitoring dashboard data with performance metrics.

    Session 761: Created for Agents Page Monitoring tab

    Query params:
        period: '1h' | '24h' | '7d' | '30d' (default: '24h')
    """
    try:
        from core.models_unified_system import AgentExecution, Agent
        from django.db.models import Count, Avg, Sum, F, Q, FloatField, Case, When, DecimalField, Value
        from django.db.models.functions import Cast, Coalesce
        from django.utils import timezone
        from datetime import timedelta
        from decimal import Decimal

        period = request.GET.get('period', '24h')
        period_map = {
            '1h': timedelta(hours=1),
            '24h': timedelta(hours=24),
            '7d': timedelta(days=7),
            '30d': timedelta(days=30),
        }
        delta = period_map.get(period, timedelta(hours=24))
        cutoff = timezone.now() - delta

        # Get executions in the period.
        # Arc I-0100 P4 §4.2 F1 fold (PR-B1 §3.3 Q5 Rigby SIGN-clean +
        # Chris agree-all 2026-07-06 → exclude_pa): performance
        # overview reflects router-agent job health/throughput; PA
        # agentic loop rows distort baseline and mislead the
        # success/failure metric family. Use agent__name form per
        # ADR-0002 F1 fold equivalent (Postgres JSONField
        # NULL-semantics make the input_data__source='pa' form
        # unsafe for pre-flag-flip rows).
        # I-0302 Phase 3 Sub-phase B2a: scoped to user via scope_queryset_agent_execution.
        executions = scope_queryset_agent_execution(
            request.user,
            AgentExecution.objects.filter(created_at__gte=cutoff),
        ).exclude(agent__name='PersonalAssistant')

        # Overall metrics
        total_executions = executions.count()
        completed = executions.filter(status='completed').count()
        failed = executions.filter(status='failed').count()
        success_rate = (completed / total_executions * 100) if total_executions > 0 else 0

        # Aggregate metrics
        agg = executions.aggregate(
            total_tokens=Coalesce(Sum('tokens_used'), Value(0)),
            total_cost=Coalesce(Sum('cost'), Value(Decimal('0.00')), output_field=DecimalField()),
            avg_execution_time=Coalesce(Avg('execution_time_ms'), Value(0.0), output_field=FloatField()),
        )

        # Per-agent performance
        agent_stats = executions.values('agent__name').annotate(
            total_executions=Count('id'),
            successful=Count('id', filter=Q(status='completed')),
            avg_execution_time=Coalesce(Avg('execution_time_ms'), Value(0.0), output_field=FloatField()),
            total_tokens=Coalesce(Sum('tokens_used'), Value(0)),
            total_cost=Coalesce(Sum('cost'), Value(Decimal('0.00')), output_field=DecimalField()),
        ).order_by('-total_executions')

        # Build agents dict for frontend
        agents_data = {}
        for stat in agent_stats:
            name = stat['agent__name'] or 'Unknown'
            total = stat['total_executions']
            success = stat['successful']
            agents_data[name] = {
                'total_executions': total,
                'success_rate': success / total if total > 0 else 0,
                'avg_execution_time': (stat['avg_execution_time'] or 0) / 1000,  # Convert to seconds
                'total_tokens': stat['total_tokens'],
                'total_cost': float(stat['total_cost'] or 0),
            }

        # Execution timeline (hourly for 24h, daily for 7d/30d)
        timeline = []
        if period in ['1h', '24h']:
            # Hourly breakdown
            from django.db.models.functions import TruncHour
            hourly = executions.annotate(
                hour=TruncHour('created_at')
            ).values('hour').annotate(
                count=Count('id'),
                successful=Count('id', filter=Q(status='completed'))
            ).order_by('hour')
            timeline = [
                {
                    'timestamp': h['hour'].isoformat() if h['hour'] else None,
                    'executions': h['count'],
                    'successful': h['successful'],
                }
                for h in hourly
            ]
        else:
            # Daily breakdown
            from django.db.models.functions import TruncDate
            daily = executions.annotate(
                day=TruncDate('created_at')
            ).values('day').annotate(
                count=Count('id'),
                successful=Count('id', filter=Q(status='completed'))
            ).order_by('day')
            timeline = [
                {
                    'timestamp': d['day'].isoformat() if d['day'] else None,
                    'executions': d['count'],
                    'successful': d['successful'],
                }
                for d in daily
            ]

        # Recent executions for activity feed
        recent = executions.select_related('agent').order_by('-created_at')[:10]
        recent_executions = [
            {
                'id': str(ex.id),
                'agent_name': ex.agent.name if ex.agent else 'Unknown',
                'status': ex.status,
                'execution_time_ms': ex.execution_time_ms,
                'tokens_used': ex.tokens_used,
                'created_at': ex.created_at.isoformat(),
            }
            for ex in recent
        ]

        # Session 761: Add system metrics (CPU, memory, uptime)
        system_metrics = {}
        try:
            import psutil
            import os
            system_metrics = {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'uptime': _format_uptime(psutil.boot_time()),
            }
        except ImportError:
            # psutil not available - provide placeholder
            system_metrics = {
                'cpu_percent': 0,
                'memory_percent': 0,
                'uptime': 'N/A',
            }

        # Session 761: Add cache metrics (Redis stats)
        cache_metrics = {}
        try:
            import redis
            from django.conf import settings
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
            r = redis.from_url(redis_url)
            info = r.info('stats')
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            cache_metrics = {
                'hits': hits,
                'misses': misses,
                'hit_rate': round((hits / total * 100) if total > 0 else 0, 1),
            }
        except Exception:
            cache_metrics = {
                'hits': 0,
                'misses': 0,
                'hit_rate': 0,
            }

        # Session 761: Calculate active agents (agents with at least one execution in period)
        active_agents = len([a for a in agents_data.keys() if agents_data[a]['total_executions'] > 0])

        return Response({
            'success': True,
            'data': {
                'period': period,
                'summary': {
                    'total_executions': total_executions,
                    'total_executions_24h': total_executions,  # Session 761: Frontend expects this field
                    'completed': completed,
                    'failed': failed,
                    'success_rate': round(success_rate, 1),
                    'total_tokens': agg['total_tokens'],
                    'total_cost': float(agg['total_cost']),
                    'avg_execution_time': round((agg['avg_execution_time'] or 0) / 1000, 2),  # seconds
                    'average_execution_time': round((agg['avg_execution_time'] or 0) / 1000, 2),  # Session 761: Frontend expects this field
                    'active_agents': active_agents,  # Session 761: Count of agents with executions
                },
                'agents': agents_data,
                'timeline': timeline,
                'recent_executions': recent_executions,
                'system': system_metrics,
                'cache': cache_metrics,
            }
        })
    except Exception as e:
        logger.error(f"Error getting monitoring dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def monitoring_alerts(request):
    """
    Get active monitoring alerts for agents.

    Session 761: Created for Agents Page Monitoring tab
    """
    try:
        from core.models_unified_system import AgentExecution
        from django.db.models import Count, Avg, Q
        from django.utils import timezone
        from datetime import timedelta
        import hashlib

        alerts = []
        now = timezone.now()
        cutoff = now - timedelta(hours=24)

        # Check for agents with high failure rates.
        # Arc I-0100 P4 §4.2 F1 fold: exclude PA meta-agent rows —
        # per-agent failure-rate alerts treat each agent__name as a
        # router-agent job target; PA failures come from a different
        # execution model. agent__name form is safer than
        # input_data__source='pa' for pre-flag-flip rows (JSON NULL).
        # I-0302 Phase 3 Sub-phase B2a: scoped to user via scope_queryset_agent_execution.
        agent_stats = scope_queryset_agent_execution(
            request.user,
            AgentExecution.objects.filter(created_at__gte=cutoff),
        ).exclude(agent__name='PersonalAssistant').values('agent__name').annotate(
            total=Count('id'),
            failed=Count('id', filter=Q(status='failed')),
        )

        for stat in agent_stats:
            if stat['total'] >= 5:  # Need enough data
                fail_rate = stat['failed'] / stat['total']
                if fail_rate > 0.3:  # >30% failure rate
                    agent_name = stat['agent__name'] or 'Unknown'
                    alerts.append({
                        'id': hashlib.md5(f"failure_{agent_name}".encode()).hexdigest()[:8],
                        'type': 'high_failure_rate',
                        'level': 'critical' if fail_rate > 0.5 else 'warning',
                        'agent_name': agent_name,
                        'message': f"{agent_name} has {int(fail_rate*100)}% failure rate",
                        'value': round(fail_rate * 100, 1),
                        'threshold': 30,
                        'timestamp': now.isoformat(),
                    })

        # Check for slow agents (avg > 60 seconds)
        # Session 761: Raised from 30s to 60s - many agents legitimately take longer
        # (coordinators orchestrate sub-agents, research agents do deep queries,
        # ThinkingAgent does multi-step reasoning ~37s)
        # Arc I-0100 P4 §4.2 F1 fold: exclude PA meta-agent rows —
        # slow-agent alerts are for router-agent latency, not PA
        # agentic loop latency (different execution model).
        # I-0302 Phase 3 Sub-phase B2a: scoped to user via scope_queryset_agent_execution.
        slow_agents = scope_queryset_agent_execution(
            request.user,
            AgentExecution.objects.filter(created_at__gte=cutoff, status='completed'),
        ).exclude(agent__name='PersonalAssistant').values('agent__name').annotate(
            avg_time=Avg('execution_time_ms'),
            count=Count('id')
        ).filter(avg_time__gt=60000, count__gte=3)

        for stat in slow_agents:
            agent_name = stat['agent__name'] or 'Unknown'
            alerts.append({
                'id': hashlib.md5(f"slow_{agent_name}".encode()).hexdigest()[:8],
                'type': 'slow_execution',
                'level': 'warning',
                'agent_name': agent_name,
                'message': f"{agent_name} avg execution time is {int(stat['avg_time']/1000)}s",
                'value': round(stat['avg_time'] / 1000, 1),
                'threshold': 60,  # Session 761: Updated to match new 60s threshold
                'timestamp': now.isoformat(),
            })

        return Response({
            'success': True,
            'data': {
                'alerts': alerts,
                'count': len(alerts),
            }
        })
    except Exception as e:
        logger.error(f"Error getting monitoring alerts: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def monitoring_agent_detail(request, agent_name):
    """
    Get detailed monitoring data for a specific agent.

    Session 761: Created for Agents Page Monitoring tab
    """
    try:
        from core.models_unified_system import AgentExecution, Agent
        from django.db.models import Count, Avg, Sum, Q, FloatField, DecimalField, Value
        from django.db.models.functions import Coalesce, TruncDate
        from django.utils import timezone
        from datetime import timedelta
        from decimal import Decimal

        period = request.GET.get('period', '7d')
        period_map = {
            '1h': timedelta(hours=1),
            '24h': timedelta(hours=24),
            '7d': timedelta(days=7),
            '30d': timedelta(days=30),
        }
        delta = period_map.get(period, timedelta(days=7))
        cutoff = timezone.now() - delta

        # Find agent
        agent = Agent.objects.filter(name__iexact=agent_name).first()
        if not agent:
            return Response({
                'success': False,
                'error': f'Agent {agent_name} not found'
            }, status=404)

        # I-0302 Phase 3 Sub-phase B2a: scoped to user via scope_queryset_agent_execution.
        executions = scope_queryset_agent_execution(
            request.user,
            AgentExecution.objects.filter(agent=agent, created_at__gte=cutoff),
        )

        total = executions.count()
        completed = executions.filter(status='completed').count()
        failed = executions.filter(status='failed').count()

        agg = executions.aggregate(
            total_tokens=Coalesce(Sum('tokens_used'), Value(0)),
            total_cost=Coalesce(Sum('cost'), Value(Decimal('0.00')), output_field=DecimalField()),
            avg_execution_time=Coalesce(Avg('execution_time_ms'), Value(0.0), output_field=FloatField()),
        )

        # Daily breakdown
        daily = executions.annotate(
            day=TruncDate('created_at')
        ).values('day').annotate(
            count=Count('id'),
            successful=Count('id', filter=Q(status='completed'))
        ).order_by('day')

        # Recent executions
        recent = executions.order_by('-created_at')[:20]

        return Response({
            'success': True,
            'data': {
                'agent': {
                    'id': str(agent.id),
                    'name': agent.name,
                    'display_name': agent.name,
                    'specialization': agent.specialization,
                },
                'period': period,
                'summary': {
                    'total_executions': total,
                    'completed': completed,
                    'failed': failed,
                    'success_rate': round(completed / total * 100, 1) if total > 0 else 0,
                    'total_tokens': agg['total_tokens'],
                    'total_cost': float(agg['total_cost'] or 0),
                    'avg_execution_time': round((agg['avg_execution_time'] or 0) / 1000, 2),
                },
                'timeline': [
                    {
                        'date': d['day'].isoformat() if d['day'] else None,
                        'executions': d['count'],
                        'successful': d['successful'],
                    }
                    for d in daily
                ],
                'recent_executions': [
                    {
                        'id': str(ex.id),
                        'status': ex.status,
                        'task': ex.task[:100] if ex.task else None,
                        'execution_time_ms': ex.execution_time_ms,
                        'tokens_used': ex.tokens_used,
                        'created_at': ex.created_at.isoformat(),
                    }
                    for ex in recent
                ]
            }
        })
    except Exception as e:
        logger.error(f"Error getting agent monitoring detail: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# ── Session 1098 PR #3: cooperative cancellation ────────────────────── #


@api_view(['POST'])
@permission_classes([AllowAny])  # Auth TBD — follow same pattern as peers
def cancel_agent_execution(request, execution_id: str):
    """Signal cooperative cancellation for an in-flight AgentExecution.

    Writes to the CancelTokenRegistry so every code path consulting the
    registry by execution_id (LLM wrapper pre-call check, BaseAgent
    checkpoints, router pre-dispatch) observes the signal at its next
    safe checkpoint.

    Idempotent — repeated calls return 200 with the existing record.
    Missing / invalid execution_id returns 404.

    Request body (optional)::

        {
            "reason": "user cancelled via Command Center",
            "requested_by": "donkeyking"
        }

    Response::

        {
            "ok": true,
            "execution_id": "...",
            "cancel_state": {
                "cancelled": "1",
                "reason": "...",
                "requested_at": "...",
                "observed_at": "..." | null,
                "observed_location": "..." | null
            }
        }
    """
    from core.services.cancel_registry import (
        request_execution_cancel,
        get_cancel_state,
    )

    reason = (request.data.get('reason') or '').strip()
    requested_by = (request.data.get('requested_by') or '').strip()
    if not requested_by and getattr(request.user, 'is_authenticated', False):
        requested_by = request.user.username

    # Confirm the execution actually exists. Cancel for an unknown
    # execution_id is a caller bug, not a silent no-op.
    try:
        from core.models_unified_system import AgentExecution
        # I-0302 Phase 3 Sub-phase B2a: EXISTS via scope_queryset_agent_execution
        # per Rigby SIGN — captures superuser carve-out (a plain
        # `.filter(user=request.user)` would incorrectly exclude null-user
        # rows for superusers).
        exists = scope_queryset_agent_execution(
            request.user, AgentExecution.objects.all()
        ).filter(id=execution_id).exists()
    except Exception as exc:
        logger.exception(
            "cancel_agent_execution: AgentExecution lookup failed: %s", exc
        )
        return Response({
            'ok': False,
            'error': 'execution lookup failed',
        }, status=500)

    if not exists:
        return Response({
            'ok': False,
            'error': 'execution_id not found',
            'execution_id': execution_id,
        }, status=404)

    ok = request_execution_cancel(
        execution_id,
        reason=reason or 'cancel requested via API',
        requested_by=requested_by,
    )
    if not ok:
        return Response({
            'ok': False,
            'error': 'invalid execution_id format',
        }, status=400)

    state = get_cancel_state(execution_id)
    logger.info(
        "[cancel-api] execution_id=%s reason=%r by=%r state=%s",
        execution_id, reason, requested_by, state,
    )
    return Response({
        'ok': True,
        'execution_id': execution_id,
        'cancel_state': state,
    }, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_agent_execution_cancel_state(request, execution_id: str):
    """Return the CancelTokenRegistry entry for this execution, or null.

    Used by dashboards / the Command Center to display "this run was
    cancelled at step X" without hitting the AgentExecution model.
    """
    from core.services.cancel_registry import get_cancel_state
    state = get_cancel_state(execution_id)
    return Response({
        'ok': True,
        'execution_id': execution_id,
        'cancel_state': state,
    }, status=200)