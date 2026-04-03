"""
Agent Training API Views
========================

Session 217B: REST API endpoints for agent training and configuration.

Provides endpoints for:
- Agent configuration management
- Capability management
- Agent templates
- Training history and stats
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.services.agent_training import get_agent_training_service

logger = logging.getLogger(__name__)


# =============================================================================
# AGENT CONFIGURATION
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_agents(request):
    """
    GET /api/training/agents/

    Get all agent configurations.
    """
    service = get_agent_training_service(request.user)
    agents = service.get_all_agents()

    return Response({
        'agents': agents,
        'total': len(agents)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agent(request, agent_name):
    """
    GET /api/training/agents/{agent_name}/

    Get configuration for a specific agent.
    """
    service = get_agent_training_service(request.user)
    config = service.get_agent_config(agent_name)

    if not config:
        return Response(
            {'error': f'Agent not found: {agent_name}'},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(config)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_agent(request, agent_name):
    """
    PUT/PATCH /api/training/agents/{agent_name}/

    Update agent configuration.

    Body:
        display_name: Optional display name
        description: Optional description
        capabilities: Optional list of capability IDs
        is_active: Optional active status
    """
    data = request.data
    service = get_agent_training_service(request.user)

    result = service.update_agent_config(
        agent_name=agent_name,
        display_name=data.get('display_name'),
        description=data.get('description'),
        capabilities=data.get('capabilities'),
        is_active=data.get('is_active')
    )

    if result.get('success'):
        return Response(result)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


# =============================================================================
# CAPABILITIES
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_capabilities(request):
    """
    GET /api/training/capabilities/

    Get all available capabilities.
    """
    service = get_agent_training_service(request.user)
    capabilities = service.get_available_capabilities()

    return Response({
        'capabilities': capabilities,
        'total': len(capabilities)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_capability(request, agent_name):
    """
    POST /api/training/agents/{agent_name}/capabilities/

    Add a capability to an agent.

    Body:
        capability_id: ID of the capability to add
    """
    capability_id = request.data.get('capability_id')

    if not capability_id:
        return Response(
            {'error': 'capability_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    service = get_agent_training_service(request.user)
    result = service.add_capability(agent_name, capability_id)

    if result.get('success'):
        return Response(result)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_capability(request, agent_name, capability_id):
    """
    DELETE /api/training/agents/{agent_name}/capabilities/{capability_id}/

    Remove a capability from an agent.
    """
    service = get_agent_training_service(request.user)
    result = service.remove_capability(agent_name, capability_id)

    if result.get('success'):
        return Response(result)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


# =============================================================================
# TEMPLATES
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_templates(request):
    """
    GET /api/training/templates/

    Get available agent templates.
    """
    service = get_agent_training_service(request.user)
    templates = service.get_agent_templates()

    return Response({
        'templates': templates,
        'total': len(templates)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_from_template(request):
    """
    POST /api/training/agents/from-template/

    Create a new agent from a template.

    Body:
        template_id: ID of the template to use
        custom_name: Optional custom name for the agent
    """
    template_id = request.data.get('template_id')

    if not template_id:
        return Response(
            {'error': 'template_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    service = get_agent_training_service(request.user)
    result = service.create_agent_from_template(
        template_id=template_id,
        custom_name=request.data.get('custom_name')
    )

    if result.get('success'):
        return Response(result, status=status.HTTP_201_CREATED)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


# =============================================================================
# TRAINING HISTORY & STATS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def training_history(request):
    """
    GET /api/training/history/

    Get training history for agents.

    Query params:
        agent_name: Optional filter by agent
    """
    agent_name = request.GET.get('agent_name')

    service = get_agent_training_service(request.user)
    history = service.get_training_history(agent_name)

    return Response({
        'history': history,
        'total': len(history)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def training_stats(request):
    """
    GET /api/training/stats/

    Get overall training statistics.
    """
    service = get_agent_training_service(request.user)
    stats = service.get_training_stats()

    return Response(stats)


# =============================================================================
# DASHBOARD
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def training_dashboard(request):
    """
    GET /api/training/dashboard/

    Get all data for training dashboard.
    """
    service = get_agent_training_service(request.user)

    return Response({
        'agents': service.get_all_agents(),
        'capabilities': service.get_available_capabilities(),
        'templates': service.get_agent_templates(),
        'stats': service.get_training_stats(),
        'recent_history': service.get_training_history()[:10]
    })


# =============================================================================
# SESSION 383: AGENT CHAT & INVOKE
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agent_chat(request):
    """
    POST /api/training/agents/chat/

    Chat with an agent directly.

    Body:
        agent_name: Name of the agent to chat with
        message: User's message
        conversation_history: Optional list of previous messages
    """
    import time
    from openai import OpenAI
    import os

    agent_name = request.data.get('agent_name')
    message = request.data.get('message')
    conversation_history = request.data.get('conversation_history', [])

    if not agent_name or not message:
        return Response(
            {'success': False, 'error': 'agent_name and message are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get agent info
    from core.models_unified_system import AgentPerformanceMetric
    try:
        agent_metric = AgentPerformanceMetric.objects.get(agent_name=agent_name)
    except AgentPerformanceMetric.DoesNotExist:
        return Response(
            {'success': False, 'error': f'Agent not found: {agent_name}'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Build system prompt based on agent capabilities
    capabilities = agent_metric.capabilities or []
    display_name = agent_metric.agent_name.replace('_', ' ').title()

    system_prompt = f"""You are {display_name}, a specialized AI agent.

Your capabilities include: {', '.join(capabilities) if capabilities else 'general assistance'}

You should:
- Be helpful, creative, and engaging
- Stay in character as this specialized agent
- Provide detailed and actionable responses
- If asked to create something, describe what you would create in detail
- Reference your specific capabilities when relevant

Current conversation context: You are chatting directly with a user through the Agent Training interface."""

    # Build messages for OpenAI
    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history
    for msg in conversation_history[-10:]:  # Last 10 messages for context
        role = "user" if msg.get('role') == 'user' else "assistant"
        messages.append({"role": role, "content": msg.get('content', '')})

    # Add current message
    messages.append({"role": "user", "content": message})

    try:
        start_time = time.time()
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=messages,
            max_completion_tokens=2000
        )

        agent_response = response.choices[0].message.content
        execution_time = round(time.time() - start_time, 2)

        # Update agent metrics
        agent_metric.total_executions += 1
        agent_metric.successful_executions += 1
        agent_metric.update_quality_score()

        return Response({
            'success': True,
            'response': agent_response,
            'agent_name': agent_name,
            'execution_time': execution_time
        })

    except Exception as e:
        logger.error(f"Agent chat error: {e}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agent_invoke(request):
    """
    POST /api/training/agents/invoke/

    Invoke an agent with a specific task.

    Body:
        agent_name: Name of the agent to invoke
        task: Task description for the agent
    """
    import time
    from openai import OpenAI
    import os

    agent_name = request.data.get('agent_name')
    task = request.data.get('task')

    if not agent_name or not task:
        return Response(
            {'success': False, 'error': 'agent_name and task are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get agent info
    from core.models_unified_system import AgentPerformanceMetric
    try:
        agent_metric = AgentPerformanceMetric.objects.get(agent_name=agent_name)
    except AgentPerformanceMetric.DoesNotExist:
        return Response(
            {'success': False, 'error': f'Agent not found: {agent_name}'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Build task execution prompt
    capabilities = agent_metric.capabilities or []
    display_name = agent_metric.agent_name.replace('_', ' ').title()

    system_prompt = f"""You are {display_name}, a specialized AI agent executing a task.

Your capabilities include: {', '.join(capabilities) if capabilities else 'general task execution'}

Execute the following task with precision and detail:
- Provide a clear, actionable result
- If the task involves creation, describe what you created in detail
- Include any relevant insights or recommendations
- Format your response clearly with sections if needed"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Task: {task}"}
    ]

    try:
        start_time = time.time()
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=messages,
            max_completion_tokens=3000
        )

        result = response.choices[0].message.content
        execution_time = round(time.time() - start_time, 2)

        # Update agent metrics
        agent_metric.total_executions += 1
        agent_metric.successful_executions += 1
        agent_metric.update_quality_score()

        return Response({
            'success': True,
            'result': result,
            'agent_name': agent_name,
            'execution_time': execution_time
        })

    except Exception as e:
        logger.error(f"Agent invoke error: {e}")

        # Track failed execution
        agent_metric.total_executions += 1
        agent_metric.save()

        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
