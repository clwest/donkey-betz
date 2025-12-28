"""
Unified Personal Assistant API Views
===================================

The One True Assistant™ endpoint that combines:
- Neural intelligence with agent orchestration
- Personal learning and memory
- Agent performance tracking
- Reality-aware responses
"""

import logging
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from core.unified_personal_assistant import UnifiedPersonalAssistant
from core.models_agent_memory import AgentExecutionMemory, AgentRecommendation

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unified_assistant_chat(request):
    """
    The One True Assistant™ Chat Endpoint

    Combines all assistant capabilities:
    - Full agent integration with memory
    - Personal learning and preferences
    - Reality-aware responses
    - Performance tracking
    """
    user = request.user

    try:
        # Get request data
        message = request.data.get('message', '').strip()
        conversation_history = request.data.get('conversation_history', [])
        context = request.data.get('context', {})

        if not message:
            return Response({'error': 'Message is required'}, status=400)

        logger.info(f"🤖 Unified Assistant processing message for {user.username}: {message[:50]}...")

        # Initialize the unified assistant
        assistant = UnifiedPersonalAssistant(user)

        # Add conversation history to context
        enhanced_context = {
            **context,
            'conversation_history': conversation_history,
            'user_id': str(user.id),
            'username': user.username,
            'timestamp': datetime.now().isoformat()
        }

        # Process the message
        response_data = assistant.process_message(message, enhanced_context)

        # Add unified assistant metadata
        response_data.update({
            'unified_assistant': True,
            'capabilities': [
                'agent_orchestration',
                'performance_memory',
                'personal_learning',
                'reality_awareness'
            ],
            'user_context': {
                'total_agent_uses': AgentExecutionMemory.objects.filter(user=user).count(),
                'favorite_agents': assistant._get_favorite_agents()[:3]
            }
        })

        logger.info(f"✅ Unified Assistant response generated for {user.username}")

        return Response({
            'success': True,
            'data': response_data
        })

    except Exception as e:
        logger.error(f"Error in unified assistant: {e}")
        return Response({
            'error': 'Failed to process message',
            'detail': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unified_assistant_context(request):
    """
    Get comprehensive context including agent memories and preferences.
    """
    user = request.user

    try:
        assistant = UnifiedPersonalAssistant(user)
        context = assistant.get_personalized_context()

        # Add agent recommendation summary
        recent_recs = AgentRecommendation.objects.filter(
            user=user
        ).order_by('-confidence_score')[:5]

        agent_insights = []
        for rec in recent_recs:
            agent_insights.append({
                'task_type': rec.task_type,
                'recommended_agent': rec.recommended_agent,
                'success_rate': f"{rec.avg_success_rate:.1%}",
                'best_outcome': rec.best_outcome_description[:100] + "..." if len(rec.best_outcome_description) > 100 else rec.best_outcome_description
            })

        return Response({
            'success': True,
            'context': {
                **context,
                'agent_insights': agent_insights,
                'assistant_type': 'unified',
                'capabilities': [
                    'Full agent orchestration with memory',
                    'Performance-based recommendations',
                    'Personal learning and adaptation',
                    'Reality-aware responses'
                ]
            }
        })

    except Exception as e:
        logger.error(f"Error getting unified context: {e}")
        return Response({
            'error': 'Failed to get context',
            'detail': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_agent_with_memory(request):
    """
    Execute a specific agent and record performance for future recommendations.
    """
    user = request.user

    try:
        agent_name = request.data.get('agent_name', '').strip()
        task = request.data.get('task', '').strip()
        context = request.data.get('context', {})

        if not agent_name or not task:
            return Response({
                'error': 'Both agent_name and task are required'
            }, status=400)

        logger.info(f"🤖 Executing {agent_name} for {user.username}: {task[:50]}...")

        assistant = UnifiedPersonalAssistant(user)
        result = assistant.execute_agent_with_memory(agent_name, task, context)

        return Response({
            'success': True,
            'data': result
        })

    except Exception as e:
        logger.error(f"Error executing agent with memory: {e}")
        return Response({
            'error': 'Failed to execute agent',
            'detail': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agent_recommendations(request):
    """
    Get personalized agent recommendations based on past performance.
    """
    user = request.user
    task_query = request.GET.get('task', '')

    try:
        assistant = UnifiedPersonalAssistant(user)
        recommendations = assistant.get_agent_recommendations(task_query)

        return Response({
            'success': True,
            'recommendations': recommendations,
            'query': task_query
        })

    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return Response({
            'error': 'Failed to get recommendations',
            'detail': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_agent_execution(request):
    """
    Allow users to rate agent executions for better learning.
    """
    user = request.user

    try:
        execution_id = request.data.get('execution_id')
        rating = request.data.get('rating')  # 1-5 stars
        feedback = request.data.get('feedback', '')

        if not execution_id or not rating:
            return Response({
                'error': 'execution_id and rating are required'
            }, status=400)

        # Update the execution memory
        memory = AgentExecutionMemory.objects.get(
            id=execution_id,
            user=user
        )
        memory.user_rating = rating
        memory.user_feedback = feedback

        # Adjust success score based on rating
        if rating >= 4:
            memory.success_score = min(memory.success_score + 0.1, 1.0)
        elif rating <= 2:
            memory.success_score = max(memory.success_score - 0.2, 0.0)

        memory.save()

        # Recalculate recommendations
        assistant = UnifiedPersonalAssistant(user)
        assistant._update_agent_recommendations(
            memory.agent_name,
            memory.task_type,
            memory.success_score
        )

        return Response({
            'success': True,
            'message': 'Rating recorded and recommendations updated'
        })

    except AgentExecutionMemory.DoesNotExist:
        return Response({
            'error': 'Execution not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error rating execution: {e}")
        return Response({
            'error': 'Failed to record rating',
            'detail': str(e)
        }, status=500)


# Development endpoint for testing without auth
@csrf_exempt
@never_cache
@api_view(['POST'])
@permission_classes([AllowAny])
def unified_assistant_chat_dev(request):
    """
    Development version of unified assistant for testing without authentication.
    Falls back to assistant_user if no authentication.
    """
    try:
        # Get user - authenticated or default
        if request.user and request.user.is_authenticated:
            user = request.user
            logger.info(f"Using authenticated user: {user.username}")
        else:
            try:
                user = User.objects.get(username='chris')  # Use chris by default
            except User.DoesNotExist:
                user = User.objects.get(username='assistant_user')
            logger.info(f"Using default user: {user.username}")

        message = request.data.get('message', '').strip()
        conversation_history = request.data.get('conversation_history', [])
        context = request.data.get('context', {})

        if not message:
            return Response({'error': 'Message is required'}, status=400)

        # Initialize unified assistant
        assistant = UnifiedPersonalAssistant(user)

        enhanced_context = {
            **context,
            'conversation_history': conversation_history,
            'user_id': str(user.id),
            'username': user.username,
            'timestamp': datetime.now().isoformat(),
            'dev_mode': True
        }

        # Process message
        response_data = assistant.process_message(message, enhanced_context)

        # Add dev metadata
        response_data.update({
            'unified_assistant': True,
            'dev_mode': True,
            'debug_info': {
                'user': user.username,
                'authenticated': bool(request.user.is_authenticated if hasattr(request, 'user') else False),
                'agent_memories': AgentExecutionMemory.objects.filter(user=user).count()
            }
        })

        return JsonResponse({
            'success': True,
            'data': response_data
        })

    except Exception as e:
        logger.error(f"Error in unified assistant dev: {e}")
        return JsonResponse({
            'error': 'Failed to process message',
            'detail': str(e)
        }, status=500)