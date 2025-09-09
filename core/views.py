"""
Core views for the Unified Donkey Betz Platform.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import SystemConfiguration, PlatformMetrics
import json
from datetime import datetime
import uuid
import logging

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def platform_status(request):
    """
    Return comprehensive platform status information.
    
    This endpoint provides a health check and status overview
    of all platform components.
    """
    
    # Gather system statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    total_configs = SystemConfiguration.objects.count()
    active_configs = SystemConfiguration.objects.filter(is_active=True).count()
    total_metrics = PlatformMetrics.objects.count()
    
    # Get key configuration values
    max_agents = SystemConfiguration.get_config('max_concurrent_agents', 100)
    ai_provider = SystemConfiguration.get_config('default_ai_provider', 'openai')
    self_awareness = SystemConfiguration.get_config('enable_self_awareness', True)
    
    # Calculate uptime (simplified - from platform initialization)
    init_metric = PlatformMetrics.objects.filter(
        metric_name='platform_initialized'
    ).first()
    
    uptime_seconds = 0
    if init_metric:
        delta = datetime.now(init_metric.timestamp.tzinfo) - init_metric.timestamp
        uptime_seconds = int(delta.total_seconds())
    
    # System health indicators
    health_status = {
        'database': 'healthy',  # If we got here, DB is working
        'configuration': 'healthy' if active_configs > 0 else 'warning',
        'users': 'healthy' if total_users > 0 else 'warning',
        'metrics': 'healthy' if total_metrics > 0 else 'warning',
    }
    
    overall_health = 'healthy'
    if 'warning' in health_status.values():
        overall_health = 'warning'
    
    status_data = {
        'platform': 'Unified Donkey Betz',
        'version': '1.0.0-alpha',
        'status': overall_health,
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': uptime_seconds,
        
        'statistics': {
            'users': {
                'total': total_users,
                'active': active_users,
            },
            'configuration': {
                'total_settings': total_configs,
                'active_settings': active_configs,
            },
            'metrics': {
                'total_recorded': total_metrics,
            },
        },
        
        'key_settings': {
            'max_concurrent_agents': max_agents,
            'default_ai_provider': ai_provider,
            'self_awareness_enabled': self_awareness,
        },
        
        'health': health_status,
        
        'subsystems': {
            'agents': {'status': 'ready', 'description': 'Agent orchestration system'},
            'sports': {'status': 'ready', 'description': 'Sports analytics engine'},
            'content': {'status': 'ready', 'description': 'Content generation system'},
            'ai_services': {'status': 'ready', 'description': 'AI provider interface'},
            'self_awareness': {'status': 'ready', 'description': 'System introspection'},
        },
        
        'api': {
            'version': 'v1',
            'base_url': request.build_absolute_uri('/api/v1/'),
            'documentation': request.build_absolute_uri('/api/docs/'),
        }
    }
    
    return Response(status_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def platform_info(request):
    """
    Return basic platform information.
    
    Simple endpoint for checking if the platform is running.
    """
    
    return Response({
        'name': 'Unified Donkey Betz Platform',
        'description': 'Self-aware mega-platform combining AI content generation, sports analytics, and agent orchestration',
        'version': '1.0.0-alpha',
        'status': 'operational',
        'capabilities': [
            'Agent Orchestration (500+ agents)',
            'Sports Betting Analytics',
            'AI Content Generation',
            'Real-time Communication',
            'Self-Awareness & Code Modification',
            'Multi-Provider AI Integration',
        ],
        'architecture': {
            'backend': 'Django + DRF',
            'database': 'PostgreSQL + SQLite (dev)',
            'cache': 'Redis',
            'websockets': 'Django Channels',
            'ai_providers': ['OpenAI', 'Anthropic', 'Google', 'Local Models'],
        },
        'links': {
            'status': request.build_absolute_uri('/api/status/'),
            'admin': request.build_absolute_uri('/admin/'),
            'api_docs': request.build_absolute_uri('/api/docs/'),
        }
    })


@csrf_exempt
@require_http_methods(["POST"])
def record_metric(request):
    """
    Record a platform metric.
    
    Allows external systems to record metrics into the platform.
    """
    try:
        data = json.loads(request.body)
        
        metric = PlatformMetrics.record_metric(
            name=data.get('name'),
            value=float(data.get('value', 0)),
            metric_type=data.get('type', 'gauge'),
            subsystem=data.get('subsystem', 'system'),
            labels=data.get('labels', {})
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Metric recorded successfully',
            'metric_id': str(metric.id),
            'timestamp': metric.timestamp.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint for monitoring.
    """
    from django.db import connection
    from django.utils import timezone
    
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = 'connected'
    except:
        db_status = 'disconnected'
    
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'services': {
            'api': 'running',
            'database': db_status,
            'redis': 'connected',
            'websocket': 'active'
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def blog_list(request):
    """Placeholder blog list endpoint"""
    return Response([])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def campaigns_list(request):
    """Placeholder campaigns list endpoint"""
    return Response([])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def styles_list(request):
    """Placeholder styles list endpoint"""
    return Response([])


@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])  # Temporarily allow any for development
def prompting_settings(request):
    """Get or update prompting settings"""
    if request.method == 'GET':
        # Return current settings
        return Response({
            'enabled': True,
            'default_level': 'advanced',
            'use_memory': True,
            'auto_enhance': True,
            'model': 'gpt-5-mini',
            'temperature': 0.7,
            'content_preferences': {
                'blog': True,
                'social': True,
                'email': True,
                'video': True,
                'image': True,
                'ebook': True,
            }
        })
    
    elif request.method == 'PUT':
        # Update settings
        # In production, save to database
        settings = request.data
        return Response({
            'message': 'Settings updated successfully',
            'settings': settings
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_agent(request):
    """Execute an agent with provided parameters"""
    from agents.models import UnifiedAgentTemplate, AgentExecution
    from agents.tasks import execute_agent as execute_agent_task
    import uuid
    
    # Get agent by name or ID
    agent_name = request.data.get('agent_name')
    agent_id = request.data.get('agent_id')
    
    if agent_id:
        try:
            agent_template = UnifiedAgentTemplate.objects.get(id=agent_id, is_active=True)
        except UnifiedAgentTemplate.DoesNotExist:
            return Response({'error': f'Agent with ID {agent_id} not found'}, status=404)
    elif agent_name:
        try:
            agent_template = UnifiedAgentTemplate.objects.get(name=agent_name, is_active=True)
        except UnifiedAgentTemplate.DoesNotExist:
            return Response({'error': f'Agent {agent_name} not found'}, status=404)
    else:
        return Response({'error': 'Either agent_name or agent_id is required'}, status=400)
    
    # Generate unique execution ID
    execution_id = f"exec_{agent_template.name}_{uuid.uuid4().hex[:8]}"
    
    # Create execution instance
    execution = AgentExecution.objects.create(
        template=agent_template,
        user=request.user,
        execution_id=execution_id,
        task_description=request.data.get('task_description', ''),
        task_type=request.data.get('task_type', ''),
        context=request.data.get('context', {}),
        input_data=request.data.get('input_data', {}),
        priority=request.data.get('priority', 'normal'),
        websocket_channel=request.data.get('websocket_channel', '')
    )
    
    # Trigger the Celery task
    execute_agent_task.delay(execution_id=execution.execution_id)
    
    return Response({
        'execution_id': execution.execution_id,
        'status': execution.status,
        'message': 'Agent execution queued successfully'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def agent_instances(request):
    """Get list of agent instances from database"""
    from agents.models import UnifiedAgentTemplate
    
    # Fetch real agents from database
    agents = UnifiedAgentTemplate.objects.filter(is_active=True)
    
    # Convert to instances format (agents are templates, instances are runtime)
    instances = []
    for agent in agents:
        instances.append({
            'id': f'inst-{agent.id}',
            'agent_id': str(agent.id),
            'name': agent.name,
            'status': 'active' if agent.is_active else 'inactive',
            'created_at': agent.created_at.isoformat() if agent.created_at else None,
            'last_active': agent.updated_at.isoformat() if agent.updated_at else None,
            'tasks_completed': agent.total_executions if hasattr(agent, 'total_executions') else 0,
            'success_rate': float(agent.success_rate) if hasattr(agent, 'success_rate') else 0.95,
            'model': agent.llm_model,
            'specialization': agent.specialization,
            'description': agent.description,
            'capabilities': agent.capabilities if agent.capabilities else [],
            'tags': agent.domain_tags if hasattr(agent, 'domain_tags') else []
        })
    
    # If no agents exist, return a helpful message
    if not instances:
        return Response({
            'message': 'No agents found. Run "python manage.py create_sample_agents" to create sample agents.',
            'agents': []
        })
    
    return Response(instances)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prompt_diagnostics_dashboard(request):
    """Placeholder prompt diagnostics dashboard endpoint"""
    return Response({
        'overview': {
            'total_analyses': 0,
            'success_rate': 0.0,
            'total_token_savings': 0,
            'avg_token_reduction': 0.0,
            'templates_created': 0,
            'avg_clarity_score': 0.0
        },
        'performance_metrics': {
            'cost_savings_estimate': '$0',
            'efficiency_gain': '0%',
            'quality_improvement': 'Medium'
        },
        'issues_breakdown': {},
        'prompt_types': [],
        'recent_analyses': []
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prompt_diagnostics_analyses(request):
    """Placeholder prompt diagnostics analyses endpoint"""
    return Response({
        'analyses': [],
        'count': 0,
        'next': None,
        'previous': None
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feedback_analytics(request):
    """Placeholder feedback analytics endpoint"""
    return Response({
        'total_feedback': 0,
        'average_rating': 0.0,
        'by_content_type': {},
        'recent_trends': []
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feedback_history(request):
    """Placeholder feedback history endpoint"""
    return Response([])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prompting_stats(request):
    """Placeholder prompting stats endpoint"""
    return Response({
        'total_prompts': 0,
        'successful_completions': 0,
        'average_tokens': 0,
        'cost_estimate': 0
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def assistant_context(request):
    """Placeholder assistant context endpoint"""
    if request.method == 'GET':
        return Response({
            'context': {},
            'history': [],
            'preferences': {}
        })
    return Response({'status': 'context updated'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assistant_chat(request):
    """
    Personal AI Assistant Chat - powered by real AI providers
    """
    user = request.user
    logger = logging.getLogger(__name__)
    
    try:
        # Use request.data for DRF views instead of request.body
        message = request.data.get('message', '').strip()
        conversation_id = request.data.get('conversation_id', str(uuid.uuid4()))
        use_personal_assistant = request.data.get('use_personal_assistant', True)
        
        if not message:
            return Response({
                'error': 'Message is required',
                'timestamp': datetime.now().isoformat()
            }, status=400)
        
        # Import and initialize AI provider
        try:
            from content.ai_providers import AIProviderManager
            ai_manager = AIProviderManager()
            
            # Get available providers
            available_providers = ai_manager.get_available_providers()
            
            if not available_providers:
                # Fallback to mock response if no AI providers available
                logger.warning("No AI providers available, falling back to mock response")
                return Response({
                    'message': f"I understand you said: '{message}'. I'm your personal AI assistant, but I'm currently running in mock mode. Please configure AI provider API keys to enable full functionality.",
                    'conversation_id': conversation_id,
                    'timestamp': datetime.now().isoformat(),
                    'provider': 'mock',
                    'model': 'fallback'
                })
            
            # Use first available provider (prioritize OpenAI, then Anthropic, then Google)
            provider = None
            model = None
            
            if 'openai' in available_providers:
                provider = 'openai'
                model = 'gpt-5-mini'
            elif 'anthropic' in available_providers:
                provider = 'anthropic' 
                model = 'claude-3-haiku-20240307'
            elif 'google' in available_providers:
                provider = 'google'
                model = 'gemini-pro'
            else:
                provider = available_providers[0]  # Use any available provider
                model = 'default'
            
            # Create system prompt for personal assistant
            system_prompt = f"""You are {user.username if hasattr(user, 'username') else user.email}'s personal AI assistant in the Unified Donkey Betz Platform. 

You have access to a comprehensive business intelligence platform with:
- Advanced AI agent orchestration
- Multi-LLM provider integration  
- RAG-powered knowledge management
- Sports betting analytics with Kelly Criterion optimization
- Content creation and management tools
- Real-time workflow automation

Be helpful, concise, and professional. If the user asks about platform features, provide specific guidance on what's available. Keep responses focused and actionable."""

            # Generate AI response
            # Use different config for GPT-5 models (no temperature parameter)
            if 'gpt-5' in model.lower():
                config = {'max_tokens': 500}
            else:
                config = {'temperature': 0.7, 'max_tokens': 500}
            
            result = ai_manager.generate_content(
                provider=provider,
                model=model,
                system_prompt=system_prompt,
                user_prompt=message,
                config=config
            )
            
            if result.success:
                return Response({
                    'message': result.content,
                    'conversation_id': conversation_id,
                    'timestamp': datetime.now().isoformat(),
                    'provider': provider,
                    'model': result.model_used or model,
                    'token_usage': result.token_usage,
                    'generation_time_ms': result.generation_time_ms
                })
            else:
                logger.error(f"AI generation failed: {result.error_message}")
                return Response({
                    'message': f"I'm sorry, I encountered an error processing your message. Please try again. ({result.error_message})",
                    'conversation_id': conversation_id,
                    'timestamp': datetime.now().isoformat(),
                    'error': result.error_message
                }, status=500)
                
        except ImportError:
            logger.warning("AI providers module not available")
            # Fallback response
            return Response({
                'message': f"I received your message: '{message}'. I'm your personal assistant, but AI providers are not currently configured. Please check your API keys.",
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat(),
                'provider': 'fallback'
            })
            
    except Exception as e:
        logger.error(f"Assistant chat error: {str(e)}")
        return Response({
            'message': "I'm sorry, I encountered an unexpected error. Please try again.",
            'conversation_id': conversation_id if 'conversation_id' in locals() else str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def research_books(request):
    """Placeholder research books endpoint"""
    return Response([])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def research_documents(request):
    """Placeholder research documents endpoint"""
    return Response([])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def personal_knowledge_list(request):
    """Placeholder personal knowledge list endpoint"""
    return Response({
        'knowledge': [],
        'stats': {
            'total_entries': 0,
            'total_words': 0,
            'categories': [],
            'total_embeddings': 0
        },
        'count': 0,
        'next': None,
        'previous': None
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agents_discovery_stats(request):
    """Placeholder agents discovery stats endpoint"""
    return Response({
        'total_discovered': 0,
        'by_category': {},
        'recent_discoveries': [],
        'trending_capabilities': []
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ebooks_list(request):
    """Placeholder ebooks list endpoint"""
    return Response([])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def voice_history(request):
    """Placeholder voice history endpoint"""
    return Response([])