"""
Agent Dashboard API Endpoints
Provides agent data and status for the frontend dashboard
"""
import json
import redis
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from datetime import datetime
import logging
from agents.models import UnifiedAgentTemplate, AgentExecution
from ai_core.agents.concrete_executor import ConcreteAgentExecutor
from core.models import Agent, SpiderCategory, AgentSpiderConnection, AgentKnowledgeSource

logger = logging.getLogger(__name__)

# Redis connection for real-time data
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)


class AgentStatsAPI(View):
    """API for agent statistics and registry"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        """Get current agent statistics and list"""
        try:
            # Initialize executor to get runtime agent info
            executor = ConcreteAgentExecutor()
            runtime_agents = len(executor.agent_classes)

            # Group agents by specialization from runtime
            by_category = {}
            agent_list = []

            # Use the runtime agents from executor
            for agent_name, agent_class in executor.agent_classes.items():
                # Try to get database record if it exists
                try:
                    db_agent = UnifiedAgentTemplate.objects.get(name=agent_name)
                    category = db_agent.specialization or 'general'
                    display_name = db_agent.display_name
                    description = db_agent.description
                    usage_count = db_agent.usage_count
                    success_rate = db_agent.success_rate
                    is_verified = db_agent.is_verified
                    capabilities = db_agent.capabilities or []
                except UnifiedAgentTemplate.DoesNotExist:
                    # Use defaults for agents not in database
                    category = 'general'
                    display_name = agent_name.replace('_', ' ').title()
                    description = f"Agent: {agent_name}"
                    usage_count = 0
                    success_rate = 0.0
                    is_verified = False
                    capabilities = []

                if category not in by_category:
                    by_category[category] = []

                agent_info = {
                    'name': agent_name,
                    'display_name': display_name,
                    'specialization': category,
                    'capabilities': capabilities,
                    'description': description,
                    'usage_count': usage_count,
                    'success_rate': success_rate,
                    'is_verified': is_verified,
                    'status': 'active',
                    'runtime_class': agent_class.__name__
                }

                by_category[category].append(agent_info)
                agent_list.append(agent_info)

            # Get recent executions for activity tracking
            recent_executions = AgentExecution.objects.filter(
                status='completed'
            ).order_by('-completed_at')[:10]

            recent_activity = []
            for exec in recent_executions:
                # Calculate duration if both start and end times exist
                duration = None
                if exec.completed_at and exec.created_at:
                    duration = (exec.completed_at - exec.created_at).total_seconds()

                recent_activity.append({
                    'agent': exec.template.name if exec.template else 'unknown',
                    'task': exec.task_description,
                    'completed': exec.completed_at.isoformat() if exec.completed_at else None,
                    'duration': duration,
                    'success': exec.status == 'completed'
                })

            # Get DATABASE spider connections (Session 242)
            db_spider_connections = AgentSpiderConnection.objects.count()
            db_spider_categories = SpiderCategory.objects.count()
            db_knowledge_sources = AgentKnowledgeSource.objects.filter(is_active=True).count()

            # Get agent count from core.Agent model (the real 20 agents)
            core_agents = Agent.objects.filter(is_active=True)
            core_agent_count = core_agents.count()

            # Build enhanced agent list with spider data
            enhanced_agents = []
            for agent in core_agents:
                spider_cats = list(agent.spider_categories.values_list('name', flat=True))
                knowledge_count = agent.knowledge_sources.filter(is_active=True).count()

                enhanced_agents.append({
                    'id': str(agent.id),
                    'name': agent.name,
                    'type': agent.agent_type,
                    'description': agent.description,
                    'effectiveness_score': agent.effectiveness_score,
                    'total_executions': agent.total_executions,
                    'success_rate': agent.success_rate,
                    'spider_categories': spider_cats,
                    'spider_count': len(spider_cats),
                    'knowledge_count': knowledge_count,
                    'is_active': agent.is_active,
                })

            # Get spider category summary
            spider_category_summary = [
                {
                    'slug': cat.slug,
                    'name': cat.name,
                    'icon': cat.icon,
                    'agent_count': cat.agent_connections.count(),
                }
                for cat in SpiderCategory.objects.all()
            ]

            return JsonResponse({
                'success': True,
                # Core agents (the real 20)
                'total_agents': core_agent_count,
                'core_agents': enhanced_agents,
                # Runtime agents (for backward compatibility)
                'runtime_agents': runtime_agents,
                'categories': list(by_category.keys()),
                'agents': agent_list,
                'by_category': by_category,
                'recent_activity': recent_activity,
                # Spider connection data (Session 242)
                'spider_connections': db_spider_connections,
                'spider_categories': db_spider_categories,
                'spider_category_list': spider_category_summary,
                'knowledge_sources': db_knowledge_sources,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error getting agent stats: {e}")
            return JsonResponse({'error': str(e)}, status=500)


class AgentActivityAPI(View):
    """API for real-time agent activity"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        """Get real-time agent activity from Redis"""
        try:
            activity = []

            # Get agent activity keys from Redis
            activity_keys = redis_client.keys('agent_activity:*')

            for key in activity_keys[:20]:  # Last 20 activities
                data = redis_client.get(key)
                if data:
                    try:
                        activity_data = json.loads(data)
                        activity.append(activity_data)
                    except:
                        pass

            # Sort by timestamp
            activity.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            return JsonResponse({
                'success': True,
                'activities': activity,
                'active_count': len([a for a in activity if a.get('status') == 'active']),
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error getting agent activity: {e}")
            return JsonResponse({'error': str(e)}, status=500)


class AgentExecuteAPI(View):
    """API for executing agents"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        """Execute an agent with given parameters"""
        try:
            data = json.loads(request.body or b"{}")
            agent_name = data.get('agent')
            task = data.get('task', {})

            if not agent_name:
                return JsonResponse({'error': 'Agent name required'}, status=400)

            # Initialize executor
            executor = ConcreteAgentExecutor()

            # Execute agent
            result = asyncio.run(executor.execute_agent(
                agent_name=agent_name,
                task=task,
                user=request.user if request.user.is_authenticated else None
            ))

            # Store activity in Redis
            activity_key = f"agent_activity:{agent_name}_{datetime.now().timestamp()}"
            redis_client.setex(
                activity_key,
                3600,  # Expire after 1 hour
                json.dumps({
                    'agent': agent_name,
                    'task': task,
                    'result': result,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'completed' if result.get('success') else 'failed'
                })
            )

            return JsonResponse(result)

        except Exception as e:
            logger.error(f"Error executing agent: {e}")
            return JsonResponse({'error': str(e)}, status=500)


class AgentSpiderConnectionAPI(View):
    """API for agent-spider connections (Session 242 - Database backed)"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        """Get agent-spider connection status from database"""
        try:
            # Get all connections from database (Session 242)
            db_connections = AgentSpiderConnection.objects.select_related(
                'agent', 'spider_category'
            ).order_by('agent__name', 'priority')

            connections = []
            for conn in db_connections:
                connections.append({
                    'id': str(conn.id),
                    'agent': conn.agent.name,
                    'agent_type': conn.agent.agent_type,
                    'spider_category': conn.spider_category.name,
                    'spider_icon': conn.spider_category.icon,
                    'is_primary': conn.is_primary,
                    'priority': conn.priority,
                    'total_processed': conn.total_processed,
                    'successful_processed': conn.successful_processed,
                    'success_rate': conn.success_rate,
                    'avg_quality_score': conn.avg_quality_score,
                    'last_processed_at': conn.last_processed_at.isoformat() if conn.last_processed_at else None,
                    'status': 'active'
                })

            # Group by agent
            by_agent = {}
            for conn in connections:
                agent_name = conn['agent']
                if agent_name not in by_agent:
                    by_agent[agent_name] = []
                by_agent[agent_name].append(conn)

            # Get category summary
            categories = [
                {
                    'slug': cat.slug,
                    'name': cat.name,
                    'icon': cat.icon,
                    'description': cat.description,
                    'connected_agents': cat.agent_connections.count(),
                }
                for cat in SpiderCategory.objects.all()
            ]

            return JsonResponse({
                'success': True,
                'connections': connections,
                'by_agent': by_agent,
                'categories': categories,
                'total_connections': len(connections),
                'total_categories': len(categories),
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error getting agent-spider connections: {e}")
            return JsonResponse({'error': str(e)}, status=500)


# Import asyncio for async execution
import asyncio