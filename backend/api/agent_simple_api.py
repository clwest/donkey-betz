"""
Simple Agent API for Frontend
Provides basic agent data without complex model dependencies
"""
import json
import asyncio
import uuid
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from backend.agents.concrete_executor import ConcreteAgentExecutor
import logging
import redis

logger = logging.getLogger(__name__)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


@csrf_exempt
@require_http_methods(["GET"])
def agent_list(request):
    """Simple endpoint to get list of agents"""
    try:
        # Initialize executor to get runtime agents
        executor = ConcreteAgentExecutor()

        agents_data = []
        for agent_name, agent_class in executor.agent_classes.items():
            agents_data.append({
                'name': agent_name,
                'display_name': agent_name.replace('_', ' ').title(),
                'class_name': agent_class.__name__,
                'module': agent_class.__module__ if hasattr(agent_class, '__module__') else 'unknown',
                'status': 'active'
            })

        # Sort by name
        agents_data.sort(key=lambda x: x['name'])

        # Group by first letter for easy navigation
        grouped = {}
        for agent in agents_data:
            if agent['name']:  # Check if name is not empty
                first_letter = agent['name'][0].upper()
                if first_letter not in grouped:
                    grouped[first_letter] = []
                grouped[first_letter].append(agent)

        return JsonResponse({
            'success': True,
            'total': len(agents_data),
            'agents': agents_data,
            'grouped': grouped
        })

    except Exception as e:
        logger.error(f"Error in agent_list: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'agents': [],
            'total': 0
        })


@csrf_exempt
@require_http_methods(["GET"])
def agent_categories(request):
    """Get agent categories based on name patterns"""
    try:
        executor = ConcreteAgentExecutor()

        categories = {
            'content': [],
            'trading': [],
            'sports': [],
            'income': [],
            'research': [],
            'analysis': [],
            'automation': [],
            'general': []
        }

        for agent_name in executor.agent_classes.keys():
            name_lower = agent_name.lower()

            if 'content' in name_lower or 'writer' in name_lower or 'creator' in name_lower:
                categories['content'].append(agent_name)
            elif 'trading' in name_lower or 'crypto' in name_lower or 'forex' in name_lower or 'stock' in name_lower:
                categories['trading'].append(agent_name)
            elif 'sports' in name_lower or 'betting' in name_lower or 'odds' in name_lower:
                categories['sports'].append(agent_name)
            elif 'income' in name_lower or 'money' in name_lower or 'revenue' in name_lower:
                categories['income'].append(agent_name)
            elif 'research' in name_lower or 'search' in name_lower:
                categories['research'].append(agent_name)
            elif 'analysis' in name_lower or 'analyzer' in name_lower:
                categories['analysis'].append(agent_name)
            elif 'automation' in name_lower or 'bot' in name_lower:
                categories['automation'].append(agent_name)
            else:
                categories['general'].append(agent_name)

        # Count agents per category
        category_stats = {
            cat: {
                'count': len(agents),
                'agents': agents[:10]  # Limit to first 10 for display
            }
            for cat, agents in categories.items()
        }

        return JsonResponse({
            'success': True,
            'total_agents': len(executor.agent_classes),
            'categories': category_stats
        })

    except Exception as e:
        logger.error(f"Error in agent_categories: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'categories': {}
        })


@csrf_exempt
@require_http_methods(["POST"])
def execute_agent(request, agent_name):
    """Execute a specific agent with given task"""
    try:
        # Parse request body
        if request.body:
            try:
                data = json.loads(request.body)
                task = data.get('task', 'analyze')
            except json.JSONDecodeError:
                task = 'analyze'
        else:
            task = 'analyze'

        # Create execution ID
        execution_id = str(uuid.uuid4())[:8]

        # Store execution request in Redis
        execution_key = f"agent_execution:{agent_name}:{execution_id}"
        redis_client.set(execution_key, json.dumps({
            'agent': agent_name,
            'task': task,
            'status': 'queued',
            'created_at': str(datetime.now())
        }), ex=300)  # Expire after 5 minutes

        # For now, return mock success - will be connected to real execution later
        logger.info(f"Agent execution requested: {agent_name} - Task: {task}")

        return JsonResponse({
            'success': True,
            'execution_id': execution_id,
            'agent': agent_name,
            'task': task,
            'status': 'queued',
            'message': f'Agent {agent_name} queued for execution'
        })

    except Exception as e:
        logger.error(f"Error executing agent {agent_name}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })