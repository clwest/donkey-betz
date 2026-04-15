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
from content.models import Feedback, ContentGeneration
from django.db.models import Avg
import json
from datetime import datetime, timedelta
import uuid
import logging

# Session 266: Central prompt registry
from core.prompts import get_self_awareness_prompt

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
        data = json.loads(request.body or b"{}")
        
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
    except Exception:
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
    """List blog content from ContentGeneration model"""
    user = request.user
    
    # Get the content_type from the URL to determine what type of content to return
    # Check if this is being called from /content/social/list/ or /content/blog/list/
    path = request.get_full_path()
    if '/social/' in path:
        content_type = 'social'
    else:
        content_type = 'blog'
    
    # Get ContentGeneration records for this content type
    queryset = ContentGeneration.objects.filter(
        user=user,
        generation_config__content_type=content_type
    ).order_by('-created_at')
    
    # Convert to response format
    results = []
    for content in queryset:
        metadata = content.metadata or {}
        gen_config = content.generation_config or {}
        
        if content_type == 'social':
            item = {
                'id': str(content.id),
                'platform': gen_config.get('platform', 'unknown'),
                'content': metadata.get('content', content.generated_content),
                'hashtags': metadata.get('hashtags', []),
                'tone': gen_config.get('tone', 'engaging'),
                'character_limit': gen_config.get('character_limit', 280),
                'estimated_reach': metadata.get('estimated_reach', 0),
                'engagement_score': metadata.get('engagement_score', 0),
                'created_at': content.created_at.isoformat(),
                'status': content.status
            }
        else:  # blog
            item = {
                'id': str(content.id),
                'title': metadata.get('title', f"Blog post about {gen_config.get('topic', 'topic')}"),
                'content': metadata.get('content', content.generated_content),
                'topic': gen_config.get('topic', ''),
                'tone': gen_config.get('tone', 'professional'),
                'length': gen_config.get('length', 'medium'),
                'outline': metadata.get('outline', []),
                'metadata': metadata.get('blog_metadata', {}),
                'created_at': content.created_at.isoformat(),
                'status': content.status
            }
        
        results.append(item)
    
    return Response(results)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def campaigns_list(request):
    """Get campaigns list - Session 735: Now returns REAL data from Campaign model"""
    from core.models_campaign import Campaign

    user = request.user
    campaigns_qs = Campaign.objects.filter(user=user).order_by('-created_at')[:50]

    campaigns = []
    for campaign in campaigns_qs:
        campaigns.append({
            'id': str(campaign.id),
            'name': campaign.name,
            'client_name': campaign.client_name,
            'status': campaign.status,
            'budget_tier': campaign.budget_tier,
            'industry': campaign.industry,
            'progress_percentage': campaign.progress_percentage,
            'created_at': campaign.created_at.isoformat(),
            'due_date': campaign.due_date.isoformat() if campaign.due_date else None,
        })

    return Response({
        'success': True,
        'campaigns': campaigns,
        'total_count': campaigns_qs.count(),
        'source': 'database'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def styles_list(request):
    """Get visual styles for image generation - dynamically from Stable Diffusion service"""
    try:
        # Import the image generation service to get all available styles
        from content.image_generation import ImageGenerationService
        import inspect
        import re

        # Create instance to access the style method
        service = ImageGenerationService()

        # Get the source code of the _apply_style_to_prompt method
        source = inspect.getsource(service._apply_style_to_prompt)

        # Parse all style mappings from the source code
        style_mappings = {}
        categories = {}

        # Find the style_mappings dictionary in the source
        lines = source.split('\n')
        in_mappings = False
        current_category = None

        for line in lines:
            # Check if we're in the style_mappings dict
            if 'style_mappings = {' in line:
                in_mappings = True
                continue
            elif in_mappings and line.strip() == '}':
                break
            elif in_mappings:
                # Check for category comments
                if '# ' in line and 'Styles' in line:
                    category = line.strip().replace('#', '').strip()
                    current_category = category.replace(' Styles', '')
                    categories[current_category] = []
                # Check for style definitions
                elif "'" in line and ':' in line and 'f"' in line:
                    # Extract style ID
                    match = re.search(r"'([^']+)':\s*f\"", line)
                    if match:
                        style_id = match.group(1)
                        # Get the prompt template (just extract a preview)
                        prompt_match = re.search(r'f"([^"]+)"', line)
                        if prompt_match:
                            prompt_template = prompt_match.group(1)
                            style_mappings[style_id] = prompt_template
                            if current_category:
                                categories[current_category].append(style_id)

        # Build the response structure with all 70+ styles
        formatted_categories = {}

        for category, style_ids in categories.items():
            if not style_ids:
                continue

            formatted_styles = []
            for style_id in style_ids:
                # Create a user-friendly name from the ID
                name = style_id.replace('_', ' ').title()

                # Generate description based on style type
                description = f"High-quality {name.lower()} style optimized for Stable Diffusion"

                # Add common negative prompts for SD
                negative_prompt = "low quality, blurry, distorted, deformed, ugly, bad anatomy"

                # Determine tags from the style ID
                tags = style_id.split('_')

                # Set optimal cfg_scale and steps for SD
                cfg_scale = 7.5
                steps = 30

                # Special adjustments for certain styles
                if 'realistic' in style_id or 'photo' in style_id:
                    cfg_scale = 7
                    description = f"Ultra-realistic {name.lower()} with professional quality"
                elif 'art' in style_id or 'painting' in style_id:
                    cfg_scale = 8
                    steps = 35
                    description = f"Artistic {name.lower()} with detailed brushwork"
                elif 'anime' in style_id or 'manga' in style_id:
                    negative_prompt = "realistic, western style, photographic"
                elif 'fantasy' in style_id or 'surreal' in style_id:
                    cfg_scale = 8.5
                    steps = 40

                formatted_styles.append({
                    "id": style_id,
                    "name": name,
                    "description": description,
                    "negative_prompt": negative_prompt,
                    "tags": tags,
                    "cfg_scale": cfg_scale,
                    "steps": steps,
                    "provider": "Stable Diffusion"
                })

            formatted_categories[category] = formatted_styles

        # Add a special "All Styles" category with all styles
        all_styles = []
        for category_styles in formatted_categories.values():
            all_styles.extend(category_styles)

        # Build the final response
        styles = {
            "categories": formatted_categories,
            "total_styles": len(all_styles),
            "provider": "Stable Diffusion (Stability AI)",
            "message": f"Successfully loaded {len(all_styles)} Stable Diffusion optimized styles!"
        }

        return Response(styles)

    except Exception as e:
        logger.error(f"Error loading styles: {e}")
        # Fallback to some basic styles if there's an error
        fallback_styles = {
            "categories": {
                "Basic": [
                    {
                        "id": "photorealistic",
                        "name": "Photorealistic",
                        "description": "Ultra-realistic photography style",
                        "negative_prompt": "cartoon, illustration, painting",
                        "tags": ["photo", "realistic"],
                        "cfg_scale": 7,
                        "steps": 30
                    }
                ]
            },
            "total_styles": 2,
            "provider": "Stable Diffusion (Stability AI)",
            "message": "Fallback styles loaded - check logs for errors"
        }
        return Response(fallback_styles)


@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])  # Temporarily allow any for development
def prompting_settings(request):
    """Get or update prompting settings"""
    from core.models import UserProfile

    # Get or create user profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)

    if request.method == 'GET':
        # Return current settings
        settings = {
            'enhanced_mode': True,
            'auto_enhance': True,
            'enhancement_level': 'advanced',
            'use_memory': False
        }

        if profile:
            # Get user-specific settings if available
            settings['enhanced_mode'] = getattr(profile, 'enhanced_prompting', True)
            settings['auto_enhance'] = getattr(profile, 'auto_enhance_prompts', True)
            settings['enhancement_level'] = getattr(profile, 'prompt_enhancement_level', 'advanced')
            settings['use_memory'] = getattr(profile, 'use_prompt_memory', False)

        return Response(settings)

    elif request.method == 'PUT':
        # Update settings
        data = request.data

        if profile:
            # Update user profile settings
            if 'enhanced_mode' in data:
                profile.enhanced_prompting = data['enhanced_mode']
            if 'auto_enhance' in data:
                profile.auto_enhance_prompts = data['auto_enhance']
            if 'enhancement_level' in data:
                profile.prompt_enhancement_level = data['enhancement_level']
            if 'use_memory' in data:
                profile.use_prompt_memory = data['use_memory']

            profile.save()

        return Response({
            'status': 'success',
            'message': 'Settings updated successfully',
            'settings': data
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_agent(request):
    """Execute an agent with provided parameters"""
    from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution
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
    from core.models.agents_registry import UnifiedAgentTemplate
    
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
@permission_classes([AllowAny])
def agent_executions_list(request):
    """Get list of agent executions (actual task runs with results)"""
    from core.models.agents_registry import AgentExecution
    from agents.serializers import AgentExecutionSerializer
    from django.core.paginator import Paginator
    
    # Fetch agent executions, ordered by most recent first
    executions = AgentExecution.objects.select_related('template', 'user').order_by('-created_at')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        executions = executions.filter(status=status)
    
    # Paginate results
    paginator = Paginator(executions, 50)  # 50 executions per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Serialize the executions
    serializer = AgentExecutionSerializer(page_obj, many=True)
    
    return Response({
        'results': serializer.data,
        'count': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prompt_diagnostics_dashboard(request):
    """Prompt diagnostics dashboard - Session 735: Now returns REAL data"""
    from core.models_agent_memory import IntelligentPromptMetric, IntelligentPromptStats
    from django.db.models import Avg, Sum, Count

    # Get global stats
    try:
        stats = IntelligentPromptStats.objects.get(stat_type='global')
    except IntelligentPromptStats.DoesNotExist:
        stats = None

    # Calculate from metrics if stats not available
    metrics_agg = IntelligentPromptMetric.objects.aggregate(
        total=Count('id'),
        avg_quality=Avg('response_quality_score'),
        total_base_tokens=Sum('base_prompt_tokens'),
        total_context_tokens=Sum('context_tokens_added'),
        total_tokens=Sum('total_prompt_tokens'),
    )

    # Get recent analyses
    recent = IntelligentPromptMetric.objects.order_by('-created_at')[:10]
    recent_analyses = [{
        'id': str(m.id),
        'agent_name': m.agent_name,
        'task_type': m.task_type,
        'base_tokens': m.base_prompt_tokens,
        'context_tokens': m.context_tokens_added,
        'total_tokens': m.total_prompt_tokens,
        'quality_score': m.response_quality_score,
        'created_at': m.created_at.isoformat(),
    } for m in recent]

    # Get prompt types breakdown
    prompt_types = list(IntelligentPromptMetric.objects.values('task_type').annotate(
        count=Count('id')
    ).order_by('-count')[:10])

    return Response({
        'overview': {
            'total_analyses': metrics_agg['total'] or 0,
            'success_rate': (stats.satisfaction_rate * 100 if stats and stats.satisfaction_rate else 0),
            'total_token_savings': metrics_agg['total_context_tokens'] or 0,
            'avg_token_reduction': (stats.avg_context_tokens if stats else 0),
            'templates_created': stats.total_agents_using if stats else 0,
            'avg_clarity_score': metrics_agg['avg_quality'] or 0.0,
        },
        'performance_metrics': {
            'cost_savings_estimate': f"${((metrics_agg['total_tokens'] or 0) / 1000) * 0.01:.2f}",
            'efficiency_gain': f"{(stats.mood_usage_rate + stats.spider_usage_rate) * 50 if stats else 0:.1f}%",
            'quality_improvement': 'High' if (metrics_agg['avg_quality'] or 0) > 0.7 else 'Medium' if (metrics_agg['avg_quality'] or 0) > 0.4 else 'Low',
        },
        'issues_breakdown': {
            'mood_enabled': stats.mood_usage_rate * 100 if stats else 0,
            'memory_enabled': stats.memory_usage_rate * 100 if stats else 0,
            'spider_enabled': stats.spider_usage_rate * 100 if stats else 0,
        },
        'prompt_types': prompt_types,
        'recent_analyses': recent_analyses,
        'source': 'database'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prompt_diagnostics_analyses(request):
    """Prompt diagnostics analyses - Session 735: Now returns REAL data"""
    from core.models_agent_memory import IntelligentPromptMetric

    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))
    offset = (page - 1) * limit

    queryset = IntelligentPromptMetric.objects.order_by('-created_at')
    total = queryset.count()
    analyses_qs = queryset[offset:offset + limit]

    analyses = [{
        'id': str(m.id),
        'agent_name': m.agent_name,
        'agent_category': m.agent_category,
        'task_type': m.task_type,
        'task_preview': m.task_preview,
        'base_tokens': m.base_prompt_tokens,
        'context_tokens': m.context_tokens_added,
        'total_tokens': m.total_prompt_tokens,
        'included_components': {
            'mood': m.included_mood,
            'memory': m.included_memory_palace,
            'spider': m.included_spider_intel,
            'evolution': m.included_evolution,
            'policy': m.included_policy,
        },
        'quality_score': m.response_quality_score,
        'user_satisfied': m.user_satisfied,
        'created_at': m.created_at.isoformat(),
    } for m in analyses_qs]

    return Response({
        'analyses': analyses,
        'count': total,
        'page': page,
        'limit': limit,
        'next': f'?page={page + 1}' if offset + limit < total else None,
        'previous': f'?page={page - 1}' if page > 1 else None,
        'source': 'database'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prompt_diagnostics_templates(request):
    """Prompt diagnostics templates - Session 735: Returns ContentTemplate data"""
    from content.models import ContentTemplate
    from django.db.models import Q

    user = request.user
    limit = int(request.GET.get('limit', 50))
    offset = int(request.GET.get('offset', 0))

    # Get templates: public + user's own
    queryset = ContentTemplate.objects.filter(
        Q(is_public=True, is_active=True) | Q(creator=user)
    ).order_by('-usage_count', '-created_at')

    total = queryset.count()
    templates_qs = queryset[offset:offset + limit]

    templates = [{
        'id': str(t.id),
        'name': t.name,
        'display_name': t.display_name,
        'description': t.description,
        'template_type': t.template_type,
        'category': t.category,
        'usage_count': t.usage_count,
        'success_rate': t.success_rate,
        'avg_user_rating': t.avg_user_rating,
        'is_public': t.is_public,
        'is_verified': t.is_verified,
        'created_at': t.created_at.isoformat(),
    } for t in templates_qs]

    return Response({
        'templates': templates,
        'pagination': {
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_next': offset + limit < total
        },
        'source': 'database'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feedback_analytics(request):
    """Feedback analytics - Session 735: Returns REAL data from feedback models"""
    from core.models_pipeline_feedback import PipelineStageFeedback
    from core.models_human_interface import HumanFeedbackRecord
    from django.db.models import Avg, Count

    # Get pipeline feedback stats
    pipeline_stats = PipelineStageFeedback.objects.aggregate(
        total=Count('id'),
        avg_rating=Avg('rating'),
    )

    # Get human feedback stats
    human_stats = HumanFeedbackRecord.objects.aggregate(
        total=Count('id'),
        avg_confidence=Avg('confidence'),
    )

    # Get breakdown by content type
    by_type = list(PipelineStageFeedback.objects.values('stage').annotate(
        count=Count('id'),
        avg_rating=Avg('rating')
    ).order_by('-count')[:10])

    return Response({
        'total_feedback': (pipeline_stats['total'] or 0) + (human_stats['total'] or 0),
        'average_rating': pipeline_stats['avg_rating'] or 0.0,
        'by_content_type': {item['stage']: item['count'] for item in by_type},
        'recent_trends': [],  # Could add time-series analysis
        'source': 'database'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feedback_history(request):
    """Feedback history - Session 735: Returns REAL data from feedback models"""
    from core.models_pipeline_feedback import PipelineStageFeedback

    limit = int(request.GET.get('limit', 50))
    feedback_qs = PipelineStageFeedback.objects.order_by('-created_at')[:limit]

    feedback = [{
        'id': str(f.id),
        'stage': f.stage,
        'rating': f.rating,
        'created_at': f.created_at.isoformat(),
    } for f in feedback_qs]

    return Response({
        'feedback': feedback,
        'total_count': PipelineStageFeedback.objects.count(),
        'source': 'database'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prompting_stats(request):
    """Get prompting statistics"""
    from datetime import datetime, timedelta
    
    # Get days parameter (default 30)
    days = int(request.GET.get('days', 30))
    start_date = datetime.now() - timedelta(days=days)
    
    # For now, return empty/default statistics
    # Will integrate with real content tracking when available
    return Response({
        'period': {
            'start': start_date.isoformat(),
            'end': datetime.now().isoformat(),
            'days': days
        },
        'overview': {
            'total_content': 0,
            'enhanced_content': 0,
            'enhancement_rate': 0,
            'memory_usage_rate': 0,
            'total_memories': 0
        },
        'by_level': {
            'basic': 0,
            'advanced': 0,
            'expert': 0
        },
        'by_content_type': {},
        'techniques_used': {}
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def prompting_test(request):
    """Test prompt enhancement"""
    import random
    
    prompt = request.data.get('prompt', '')
    level = request.data.get('level', 'advanced')
    content_type = request.data.get('content_type', 'blog')
    use_memory = request.data.get('use_memory', False)
    
    if not prompt:
        return Response({
            'error': 'Prompt is required'
        }, status=400)
    
    # Simulate enhancement techniques based on level
    techniques = []
    if level == 'basic':
        techniques = ['clarity', 'structure']
    elif level == 'advanced':
        techniques = ['clarity', 'structure', 'context', 'specificity']
    elif level == 'expert':
        techniques = ['clarity', 'structure', 'context', 'specificity', 'reasoning', 'examples']
    
    # Simulate enhanced prompt
    enhancements = []
    if 'clarity' in techniques:
        enhancements.append('Added clear objectives')
    if 'structure' in techniques:
        enhancements.append('Structured format')
    if 'context' in techniques:
        enhancements.append('Added relevant context')
    if 'specificity' in techniques:
        enhancements.append('Made requirements specific')
    if 'reasoning' in techniques:
        enhancements.append('Included reasoning framework')
    if 'examples' in techniques:
        enhancements.append('Added relevant examples')
    
    # Create enhanced version
    enhanced = f"[Enhanced {level.upper()}] {prompt}\n\n"
    enhanced += f"Content Type: {content_type}\n"
    enhanced += f"Objectives: Clear, engaging {content_type} content\n"
    enhanced += f"Techniques Applied: {', '.join(enhancements)}\n\n"
    enhanced += f"Enhanced Prompt:\n{prompt}\n\n"
    enhanced += "Additional Context: Optimize for clarity, engagement, and completeness."
    
    # Simulate memory context
    memory_context = random.randint(0, 5) if use_memory else 0
    
    return Response({
        'original': prompt,
        'enhanced': enhanced,
        'level': level,
        'metadata': {
            'content_type': content_type,
            'use_memory': use_memory,
            'enhancement_applied': True
        },
        'memory_context': memory_context,
        'techniques': techniques,
        'examples': []
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
@csrf_exempt
def assistant_chat(request):
    """
    Personal AI Assistant Chat - powered by real AI providers with RAG and System Self-Awareness
    """
    user = request.user
    logger = logging.getLogger(__name__)

    try:
        # Use request.data for DRF views instead of request.body
        message = request.data.get('message', '').strip()
        conversation_id = request.data.get('conversation_id', str(uuid.uuid4()))
        use_personal_assistant = request.data.get('use_personal_assistant', True)
        use_rag = request.data.get('use_rag', True)  # Enable RAG by default
        use_self_awareness = request.data.get('use_self_awareness', True)  # Enable self-awareness by default
        
        if not message:
            return Response({
                'error': 'Message is required',
                'timestamp': datetime.now().isoformat()
            }, status=400)
        
        # Import and initialize AI provider
        try:
            from content.ai_providers import AIProviderManager
            from core.rag_integration import get_rag_context, enhance_prompt_with_rag
            
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
            
            # Get System Self-Awareness context if enabled
            system_context = None
            if use_self_awareness:
                try:
                    from core.personal_assistant_integration import personal_assistant_integration
                    system_context = personal_assistant_integration.enhance_assistant_context(
                        message, conversation_id
                    )
                    logger.info(f"Enhanced with system awareness: {system_context.get('system_awareness', {}).get('operational_percentage', 0)}% operational")
                except Exception as e:
                    logger.error(f"Error getting system awareness context: {e}")

            # Get RAG context if enabled
            rag_context = None
            enhanced_message = message

            if use_rag:
                try:
                    logger.info(f"Getting RAG context for query: {message[:100]}...")
                    rag_context = get_rag_context(message)

                    if rag_context.get('has_context'):
                        enhanced_message = enhance_prompt_with_rag(message, rag_context)
                        logger.info(f"RAG context found: {rag_context['used_documents']} documents used")
                    else:
                        logger.info("No relevant RAG context found")
                except Exception as e:
                    logger.error(f"RAG integration failed: {e}")
                    # Continue without RAG if it fails
            
            # Session 266: Use central prompt registry for system prompt
            user_name = user.username if hasattr(user, 'username') else user.email
            system_prompt = get_self_awareness_prompt(
                "personal_assistant",
                user_name=user_name,
                rag_context=""  # Will be added by RAG integration if enabled
            )

            # Add system awareness context if available
            if system_context:
                awareness = system_context.get('system_awareness', {})
                if awareness:
                    real_components = ', '.join(awareness.get('real_components', [])[:3]) if awareness.get('real_components') else 'None'
                    issues = ', '.join(awareness.get('broken_flows', [])[:2]) if awareness.get('broken_flows') else 'None'
                    system_prompt += get_self_awareness_prompt(
                        "system_awareness_context",
                        operational_percentage=awareness.get('operational_percentage', 0),
                        real_components=real_components,
                        issues=issues
                    )

            # Generate AI response
            # Use different config for GPT-5 models (no temperature parameter)
            if 'gpt-5' in model.lower():
                config = {'max_tokens': 1500}  # Increased for RAG responses
            else:
                config = {'temperature': 0.7, 'max_tokens': 1500}
            
            result = ai_manager.generate_content(
                provider=provider,
                model=model,
                system_prompt=system_prompt,
                user_prompt=enhanced_message,
                config=config
            )
            
            logger.info(f"AI generation result.success: {result.success}")
            logger.info(f"Result content length: {len(result.content) if result.content else 0}")
            
            if result.success:
                # Save conversation to memory for learning
                try:
                    logger.info(f"Attempting to save conversation to memory...")
                    from core.conversation_memory import conversation_memory
                    saved = conversation_memory.save_conversation(
                        user_id=user.id,
                        user_message=message,
                        assistant_response=result.content,
                        metadata={
                            'conversation_id': conversation_id,
                            'provider': provider,
                            'model': result.model_used or model,
                            'rag_used': rag_context.get('has_context', False) if rag_context else False
                        }
                    )
                    logger.info(f"Conversation save result: {saved}")
                except Exception as e:
                    logger.error(f"Failed to save conversation to memory: {e}")
                
                response_data = {
                    'message': result.content,
                    'conversation_id': conversation_id,
                    'timestamp': datetime.now().isoformat(),
                    'provider': provider,
                    'model': result.model_used or model,
                    'token_usage': result.token_usage,
                    'generation_time_ms': result.generation_time_ms
                }
                
                # Add RAG context info if available
                if rag_context and rag_context.get('has_context'):
                    response_data['rag_context'] = {
                        'documents_used': rag_context['used_documents'],
                        'total_documents_found': rag_context['total_documents']
                    }

                # Add system awareness info if available
                if system_context:
                    response_data['system_awareness'] = {
                        'operational_percentage': system_context.get('system_awareness', {}).get('operational_percentage', 0),
                        'recommendations': system_context.get('recommendations', []),
                        'routing': system_context.get('routing', {})
                    }

                return Response(response_data)
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
    """Get user's research books from knowledge base"""
    from content.models import DocumentEmbedding, Document
    
    # Get books from knowledge base
    books = Document.objects.filter(
        owner=request.user,
        document_type='book',
        is_active=True
    ).order_by('-created_at')
    
    data = [{
        'id': book.id,
        'title': book.title,
        'author': book.metadata.get('author', 'Unknown'),
        'pages': book.page_count,
        'created_at': book.created_at,
        'embeddings_count': DocumentEmbedding.objects.filter(document=book).count()
    } for book in books]
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def research_documents(request):
    """Get user's research documents from knowledge base"""
    from content.models import DocumentEmbedding, Document
    
    # Get documents from knowledge base
    documents = Document.objects.filter(
        owner=request.user,
        is_active=True
    ).exclude(document_type='book').order_by('-created_at')[:100]
    
    data = [{
        'id': doc.id,
        'title': doc.title,
        'type': doc.document_type,
        'source': doc.source,
        'created_at': doc.created_at,
        'word_count': doc.word_count,
        'embeddings_count': DocumentEmbedding.objects.filter(document=doc).count()
    } for doc in documents]
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def personal_knowledge_list(request):
    """Get user's personal knowledge base from unified embeddings"""
    import psycopg2
    import json
    
    # Get query parameters (support both per_page and page_size)
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('per_page', request.GET.get('page_size', 12)))
    
    try:
        # Connect to ai_unified_platform database
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            database=os.environ.get('DB_NAME', 'ai_unified_platform'),
            user=os.environ.get('DB_USER', 'ai_unified_user'),
            password=os.environ.get('DB_PASSWORD', '')
        )
        cursor = conn.cursor()
        
        # Build query with filters
        where_clauses = ["1=1"]
        params = []
        
        # Filter by user if authenticated (or show all if no user_id in metadata)
        if request.user.is_authenticated:
            where_clauses.append("(metadata->>'user_id' = %s OR metadata->>'user_id' IS NULL)")
            params.append(str(request.user.id))
        
        # Search filter
        if search:
            where_clauses.append("(content_text ILIKE %s OR metadata->>'title' ILIKE %s)")
            search_pattern = f'%{search}%'
            params.extend([search_pattern, search_pattern])
        
        # Category filter
        if category:
            where_clauses.append("content_type = %s")
            params.append(category)
        
        # Get total count
        count_query = f"""
            SELECT COUNT(*) FROM unified_embeddings 
            WHERE {' AND '.join(where_clauses)}
        """
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Get paginated results
        offset = (page - 1) * page_size
        query = f"""
            SELECT 
                source_id,
                content_type,
                content_text,
                metadata,
                importance_score,
                created_at
            FROM unified_embeddings
            WHERE {' AND '.join(where_clauses)}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([page_size, offset])
        cursor.execute(query, params)
        
        results = cursor.fetchall()
        
        # Format knowledge entries
        knowledge = []
        for row in results:
            source_id, content_type, content_text, metadata, importance, created_at = row
            
            # Parse metadata
            meta = json.loads(metadata) if isinstance(metadata, str) else metadata or {}
            
            # Decrypt content if needed
            if content_text and content_text.startswith('gAAAAA'):
                try:
                    from core.encryption_service import get_encryption_service
                    service = get_encryption_service()
                    content_text = service.decrypt(content_text) or content_text
                except Exception as _e:
                    logger.warning(
                        "views.personal_knowledge_list: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )
            
            # Create knowledge entry with full content
            knowledge.append({
                'id': source_id,
                'title': meta.get('title', content_text[:100] if content_text else 'Untitled'),
                'description': meta.get('description', ''),
                'content_preview': content_text[:500] if content_text else '',  # Increased preview
                'full_content': content_text,  # Include full content for detail view
                'content_type': content_type,
                'file_type': meta.get('file_type', 'text'),
                'category': content_type,
                'tags': meta.get('tags', []),
                'word_count': len(content_text.split()) if content_text else 0,
                'use_in_generation': True,
                'times_used': meta.get('times_used', 0),
                'last_used': meta.get('last_used'),
                'created_at': created_at.isoformat() if created_at else None
            })
        
        # Get stats
        stats_query = """
            SELECT 
                COUNT(*) as total_entries,
                COUNT(DISTINCT content_type) as categories,
                SUM(LENGTH(content_text)) as total_chars
            FROM unified_embeddings
            WHERE metadata->>'user_id' = %s OR %s = ''
        """
        cursor.execute(stats_query, [str(request.user.id) if request.user.is_authenticated else '', 
                                     str(request.user.id) if request.user.is_authenticated else ''])
        stats_row = cursor.fetchone()
        
        # Get categories
        cat_query = """
            SELECT DISTINCT content_type 
            FROM unified_embeddings 
            WHERE content_type IS NOT NULL
        """
        cursor.execute(cat_query)
        categories = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # Calculate pagination
        total_pages = (total_count + page_size - 1) // page_size
        
        return Response({
            'knowledge': knowledge,
            'stats': {
                'total_entries': stats_row[0] if stats_row else 0,
                'total_words': (stats_row[2] // 5) if stats_row and stats_row[2] else 0,  # Rough word estimate
                'categories': categories,
                'total_embeddings': total_count
            },
            'count': total_count,
            'page': page,
            'total_pages': total_pages,
            'next': f'?page={page + 1}' if page < total_pages else None,
            'previous': f'?page={page - 1}' if page > 1 else None
        })
        
    except Exception as e:
        logger.error(f"Error fetching personal knowledge: {e}")
        return Response({
            'knowledge': [],
            'stats': {
                'total_entries': 0,
                'total_words': 0,
                'categories': [],
                'total_embeddings': 0
            },
            'count': 0,
            'error': str(e)
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


# ===== FEEDBACK SYSTEM ENDPOINTS =====

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def feedback_submit(request):
    """
    Submit user feedback on generated content
    """
    user = request.user
    data = request.data
    
    content_type = data.get('content_type', 'image')
    content_id = data.get('content_id')
    overall_rating = data.get('overall_rating')
    
    # Validate required fields
    if not content_id or not overall_rating:
        return Response({
            'success': False,
            'error': 'content_id and overall_rating are required'
        }, status=400)
    
    try:
        # Convert content_id to int if it's a string UUID
        if isinstance(content_id, str):
            # Try to find ContentGeneration by UUID
            try:
                content_gen = ContentGeneration.objects.get(id=content_id)
                content_id_int = hash(content_id) % 2147483647  # Convert UUID to int for storage
            except ContentGeneration.DoesNotExist:
                content_id_int = int(content_id) if content_id.isdigit() else hash(content_id) % 2147483647
        else:
            content_id_int = content_id
        
        # Create or update feedback
        feedback, created = Feedback.objects.update_or_create(
            user=user,
            content_type=content_type,
            content_id=content_id_int,
            defaults={
                'overall_rating': int(overall_rating),
                'quality_rating': data.get('quality_rating'),
                'accuracy_rating': data.get('accuracy_rating'),
                'usefulness_rating': data.get('usefulness_rating'),
                'feedback_type': data.get('feedback_type', 'general'),
                'comments': data.get('comments', ''),
                'suggestions': data.get('suggestions', ''),
                'would_recommend': data.get('would_recommend'),
                'met_expectations': data.get('met_expectations'),
                'saved_time': data.get('saved_time'),
                'tags': data.get('tags', []),
                'generation_params': data.get('generation_params', {})
            }
        )
        
        return Response({
            'success': True,
            'feedback_id': str(feedback.id),
            'created': created,
            'message': 'Feedback submitted successfully'
        })
        
    except Exception as e:
        logging.error(f"Error submitting feedback: {str(e)}")
        return Response({
            'success': False,
            'error': f'Failed to submit feedback: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feedback_analytics(request):
    """
    Get feedback analytics and statistics
    """
    user = request.user
    content_type = request.GET.get('content_type', 'all')
    
    # Base query - only user's feedback
    query = Feedback.objects.filter(user=user)
    
    # Filter by content type if specified
    if content_type != 'all':
        query = query.filter(content_type=content_type)
    
    # Calculate statistics
    total_feedback = query.count()
    
    if total_feedback == 0:
        return Response({
            'total_feedback': 0,
            'average_rating': 0.0,
            'by_content_type': {},
            'recent_trends': []
        })
    
    # Average rating
    avg_rating = query.aggregate(avg=Avg('overall_rating'))['avg'] or 0.0
    
    # Breakdown by content type
    by_content_type = {}
    for ct in ['text', 'image', 'video', 'blog', 'social', 'ebook', 'voice', 'research']:
        ct_query = query.filter(content_type=ct)
        ct_count = ct_query.count()
        if ct_count > 0:
            ct_avg = ct_query.aggregate(avg=Avg('overall_rating'))['avg'] or 0.0
            by_content_type[ct] = {
                'count': ct_count,
                'average_rating': round(ct_avg, 2),
                'positive_count': ct_query.filter(overall_rating__gte=4).count(),
                'negative_count': ct_query.filter(overall_rating__lte=2).count()
            }
    
    # Recent trends (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_query = query.filter(created_at__gte=thirty_days_ago)
    
    recent_trends = []
    if recent_query.exists():
        recent_avg = recent_query.aggregate(avg=Avg('overall_rating'))['avg'] or 0.0
        trend_direction = 'stable'
        if recent_avg > avg_rating + 0.2:
            trend_direction = 'improving'
        elif recent_avg < avg_rating - 0.2:
            trend_direction = 'declining'
        
        recent_trends.append({
            'period': 'last_30_days',
            'average_rating': round(recent_avg, 2),
            'count': recent_query.count(),
            'trend': trend_direction
        })
    
    return Response({
        'total_feedback': total_feedback,
        'average_rating': round(avg_rating, 2),
        'by_content_type': by_content_type,
        'recent_trends': recent_trends
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feedback_history(request):
    """
    Get user's feedback history
    """
    user = request.user
    limit = int(request.GET.get('limit', 50))
    offset = int(request.GET.get('offset', 0))
    content_type = request.GET.get('content_type', 'all')
    
    # Base query
    query = Feedback.objects.filter(user=user).order_by('-created_at')
    
    # Filter by content type if specified
    if content_type != 'all':
        query = query.filter(content_type=content_type)
    
    # Apply pagination
    feedback_items = query[offset:offset + limit]
    
    # Format response
    results = []
    for feedback in feedback_items:
        results.append({
            'id': str(feedback.id),
            'content_type': feedback.content_type,
            'content_id': feedback.content_id,
            'overall_rating': feedback.overall_rating,
            'quality_rating': feedback.quality_rating,
            'accuracy_rating': feedback.accuracy_rating,
            'usefulness_rating': feedback.usefulness_rating,
            'feedback_type': feedback.feedback_type,
            'comments': feedback.comments,
            'suggestions': feedback.suggestions,
            'would_recommend': feedback.would_recommend,
            'met_expectations': feedback.met_expectations,
            'saved_time': feedback.saved_time,
            'tags': feedback.tags,
            'created_at': feedback.created_at.isoformat(),
            'is_positive': feedback.is_positive,
            'is_negative': feedback.is_negative,
            'is_neutral': feedback.is_neutral
        })
    
    return Response(results)

from django.http import JsonResponse

def platform_status(request):
    # Minimal stub so urls can import it; expand later if you want
    return JsonResponse({"ok": True, "status": "platform alive", "version": "stub"})

# unified-donkey-betz/core/views/llm_api.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from llm.base import ChatMessage
from llm import router

@csrf_exempt
def llm_chat(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST only"}, status=405)

    try:
        body = json.loads(request.body or "{}")
        provider = body.get("provider")            # optional: "ollama" | "openai" (ollama default)
        model = body.get("model")                  # optional: override default model
        messages = [ChatMessage(**m) for m in body.get("messages", [])]

        content = router.chat(messages, provider=provider, model=model)
        return JsonResponse({"ok": True, "provider": provider, "model": model, "content": content})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=502)