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
from django.db.models import Avg, Count, Q
import json
from datetime import datetime, timedelta
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
    """Placeholder campaigns list endpoint"""
    return Response([])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def styles_list(request):
    """Get visual styles for image generation"""
    styles = {
        "categories": {
            "Professional": [
                {
                    "id": "corporate_minimal",
                    "name": "Corporate Minimal",
                    "description": "Clean, professional minimal design for business presentations",
                    "prompt": "corporate minimal design, clean layout, professional, business style, white background, modern typography",
                    "negative_prompt": "cluttered, messy, unprofessional, comic, cartoon",
                    "tags": ["professional", "minimal", "business"],
                    "use_cases": ["presentations", "corporate materials"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "tech_startup",
                    "name": "Tech Startup",
                    "description": "Modern tech startup aesthetic with bold colors and clean lines",
                    "prompt": "tech startup style, modern interface, bold colors, clean design, gradient backgrounds, tech aesthetic",
                    "negative_prompt": "old fashioned, traditional, boring, dull colors",
                    "tags": ["tech", "startup", "modern"],
                    "use_cases": ["tech presentations", "startup materials"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "professional_presentation",
                    "name": "Professional Presentation",
                    "description": "Polished presentation style with clear hierarchy and professional color scheme",
                    "prompt": "professional presentation style, clear hierarchy, elegant design, business colors, polished layout",
                    "negative_prompt": "amateur, messy, unprofessional, childish",
                    "tags": ["professional", "presentation", "business"],
                    "use_cases": ["business presentations", "reports"],
                    "cfg_scale": 8,
                    "steps": 30
                }
            ],
            "Creative": [
                {
                    "id": "digital_art_masterpiece",
                    "name": "Digital Art",
                    "description": "High-quality digital artwork with artistic flair and creative composition",
                    "prompt": "digital art masterpiece, trending on artstation, highly detailed, creative composition, vibrant colors, artistic",
                    "negative_prompt": "low quality, blurry, amateur, simple",
                    "tags": ["digital art", "creative", "artistic"],
                    "use_cases": ["artwork", "creative projects"],
                    "cfg_scale": 8,
                    "steps": 35
                },
                {
                    "id": "van_gogh_style",
                    "name": "Van Gogh",
                    "description": "Vincent van Gogh inspired post-impressionist painting style",
                    "prompt": "Van Gogh style, post-impressionist painting, swirling brushstrokes, vibrant colors, expressive style",
                    "negative_prompt": "photorealistic, smooth, digital, modern, flat colors",
                    "tags": ["van gogh", "impressionist", "classic art"],
                    "use_cases": ["artistic portraits", "landscape art"],
                    "cfg_scale": 8,
                    "steps": 35
                },
                {
                    "id": "pop_art",
                    "name": "Pop Art",
                    "description": "Bold pop art style with bright colors and graphic elements",
                    "prompt": "pop art style, bold colors, graphic design, Andy Warhol style, bright contrasts, screen print effect",
                    "negative_prompt": "subtle, muted colors, realistic, traditional, classical",
                    "tags": ["pop art", "bold", "graphic"],
                    "use_cases": ["modern art", "graphic design"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "watercolor_dream",
                    "name": "Watercolor",
                    "description": "Soft, flowing watercolor painting style with dreamy quality",
                    "prompt": "watercolor painting, soft flowing colors, dreamy atmosphere, artistic brushstrokes, paper texture",
                    "negative_prompt": "digital, sharp edges, photo realistic, harsh colors",
                    "tags": ["watercolor", "painting", "dreamy"],
                    "use_cases": ["artistic illustrations", "soft designs"],
                    "cfg_scale": 6,
                    "steps": 25
                },
                {
                    "id": "sketch_notebook",
                    "name": "Sketch",
                    "description": "Hand-drawn pencil sketch style like from an artist's notebook",
                    "prompt": "pencil sketch, hand drawn, notebook style, artistic sketching, graphite drawing, paper texture",
                    "negative_prompt": "colored, digital, polished, clean",
                    "tags": ["sketch", "pencil", "notebook"],
                    "use_cases": ["concept art", "rough designs"],
                    "cfg_scale": 6,
                    "steps": 20
                },
                {
                    "id": "oil_painting_classical",
                    "name": "Oil Painting",
                    "description": "Traditional oil painting style with rich textures and classical techniques",
                    "prompt": "oil painting, classical art style, rich textures, masterpiece, museum quality, traditional techniques",
                    "negative_prompt": "digital, modern, cartoon, flat",
                    "tags": ["oil painting", "classical", "traditional"],
                    "use_cases": ["fine art", "portraits"],
                    "cfg_scale": 8,
                    "steps": 35
                },
                {
                    "id": "abstract_modern",
                    "name": "Abstract",
                    "description": "Contemporary abstract art with bold shapes and modern composition",
                    "prompt": "abstract modern art, bold geometric shapes, contemporary style, vibrant colors, artistic composition",
                    "negative_prompt": "realistic, traditional, representational, boring",
                    "tags": ["abstract", "modern", "contemporary"],
                    "use_cases": ["modern art", "abstract designs"],
                    "cfg_scale": 7,
                    "steps": 30
                }
            ],
            "Digital": [
                {
                    "id": "cyberpunk_neon",
                    "name": "Cyberpunk Neon",
                    "description": "Futuristic cyberpunk aesthetic with neon lights and dark atmosphere",
                    "prompt": "cyberpunk style, neon lights, futuristic cityscape, dark atmosphere, glowing effects, high tech",
                    "negative_prompt": "natural, rustic, medieval, bright daylight",
                    "tags": ["cyberpunk", "neon", "futuristic"],
                    "use_cases": ["sci-fi designs", "tech aesthetics"],
                    "cfg_scale": 8,
                    "steps": 35
                },
                {
                    "id": "synthwave_retro",
                    "name": "Synthwave Retro",
                    "description": "80s inspired synthwave aesthetic with retro futuristic vibes",
                    "prompt": "synthwave style, 80s retro futuristic, neon grids, sunset colors, retro aesthetic, outrun style",
                    "negative_prompt": "modern, realistic, natural, dull colors",
                    "tags": ["synthwave", "retro", "80s"],
                    "use_cases": ["retro designs", "music covers"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "glassmorphism_ui",
                    "name": "Glassmorphism UI",
                    "description": "Modern glassmorphism design with transparent elements and blur effects",
                    "prompt": "glassmorphism design, transparent glass effect, blur background, modern UI, clean interface, frosted glass",
                    "negative_prompt": "opaque, solid colors, old fashioned, cluttered",
                    "tags": ["glassmorphism", "UI", "modern"],
                    "use_cases": ["UI design", "modern interfaces"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "isometric_3d",
                    "name": "Isometric 3D",
                    "description": "Clean isometric 3D illustration style perfect for infographics",
                    "prompt": "isometric 3D illustration, clean geometric style, bright colors, vector-like, infographic style",
                    "negative_prompt": "realistic perspective, messy, photorealistic, dark",
                    "tags": ["isometric", "3D", "illustration"],
                    "use_cases": ["infographics", "technical illustrations"],
                    "cfg_scale": 7,
                    "steps": 30
                }
            ],
            "Photography": [
                {
                    "id": "photorealistic",
                    "name": "Photorealistic",
                    "description": "Ultra-realistic photography style with professional quality",
                    "prompt": "photorealistic, high quality photography, professional lighting, sharp focus, detailed",
                    "negative_prompt": "cartoon, illustration, painting, anime, artificial",
                    "tags": ["photorealistic", "photography", "professional"],
                    "use_cases": ["product photography", "portraits"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "vintage_photo",
                    "name": "Vintage Photo",
                    "description": "Vintage film photography with retro color grading",
                    "prompt": "vintage photography, film grain, retro color grading, old camera, nostalgic mood",
                    "negative_prompt": "digital, modern, clean, sharp, high definition",
                    "tags": ["vintage", "film", "retro"],
                    "use_cases": ["retro photography", "nostalgic images"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "cinematic_portrait",
                    "name": "Cinematic Portrait",
                    "description": "Dramatic cinematic portrait photography with professional lighting",
                    "prompt": "cinematic portrait, dramatic lighting, film photography, professional studio lighting, shallow depth of field",
                    "negative_prompt": "amateur, flat lighting, cartoon, illustration",
                    "tags": ["cinematic", "portrait", "photography"],
                    "use_cases": ["professional portraits", "headshots"],
                    "cfg_scale": 8,
                    "steps": 35
                },
                {
                    "id": "studio_portrait",
                    "name": "Studio Portrait",
                    "description": "Clean studio portrait photography with professional lighting setup",
                    "prompt": "studio portrait photography, professional lighting, clean background, high quality, sharp focus",
                    "negative_prompt": "outdoor, natural lighting, casual, amateur",
                    "tags": ["studio", "portrait", "professional"],
                    "use_cases": ["business headshots", "professional portraits"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "food_photography",
                    "name": "Food Photography",
                    "description": "Appetizing food photography with perfect lighting and composition",
                    "prompt": "food photography, appetizing presentation, professional lighting, mouth-watering, high quality",
                    "negative_prompt": "unappetizing, dark, blurry, amateur",
                    "tags": ["food", "photography", "culinary"],
                    "use_cases": ["restaurant menus", "food blogs"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "product_showcase",
                    "name": "Product Showcase",
                    "description": "Professional product photography for e-commerce and marketing",
                    "prompt": "product photography, clean background, professional lighting, commercial quality, detailed",
                    "negative_prompt": "cluttered background, poor lighting, amateur, blurry",
                    "tags": ["product", "photography", "commercial"],
                    "use_cases": ["e-commerce", "product catalogs"],
                    "cfg_scale": 7,
                    "steps": 30
                }
            ],
            "3D": [
                {
                    "id": "3d_render_octane",
                    "name": "3D Render Octane",
                    "description": "High-quality 3D rendering with Octane Render quality",
                    "prompt": "3D render, octane render, unreal engine, photorealistic 3D, high quality rendering, professional 3D",
                    "negative_prompt": "2D, flat, low quality, amateur 3D",
                    "tags": ["3D", "render", "octane"],
                    "use_cases": ["product visualization", "architectural renders"],
                    "cfg_scale": 8,
                    "steps": 35
                },
                {
                    "id": "architectural_render",
                    "name": "Architectural Render",
                    "description": "Professional architectural visualization and building renders",
                    "prompt": "architectural render, building visualization, professional architecture, clean design, modern architecture",
                    "negative_prompt": "cartoon, unrealistic, poor proportions, amateur",
                    "tags": ["architectural", "building", "visualization"],
                    "use_cases": ["architecture", "real estate"],
                    "cfg_scale": 8,
                    "steps": 35
                }
            ],
            "Gaming": [
                {
                    "id": "pixel_art",
                    "name": "Pixel Art",
                    "description": "Retro pixel art style reminiscent of classic video games",
                    "prompt": "pixel art, 8-bit style, retro gaming, pixelated, video game art, classic arcade style",
                    "negative_prompt": "smooth, realistic, high resolution, modern",
                    "tags": ["pixel art", "retro", "gaming"],
                    "use_cases": ["game assets", "retro designs"],
                    "cfg_scale": 6,
                    "steps": 25
                },
                {
                    "id": "game_concept",
                    "name": "Game Concept",
                    "description": "Video game concept art style with dynamic composition",
                    "prompt": "game concept art, video game style, dynamic composition, gaming aesthetic, digital illustration",
                    "negative_prompt": "realistic photo, static, boring composition",
                    "tags": ["game art", "concept", "digital"],
                    "use_cases": ["game development", "concept art"],
                    "cfg_scale": 8,
                    "steps": 35
                },
                {
                    "id": "minecraft",
                    "name": "Minecraft",
                    "description": "Minecraft blocky voxel art style",
                    "prompt": "Minecraft style, blocky, voxel art, cubic blocks, pixelated textures, game blocks",
                    "negative_prompt": "smooth, realistic, curved, organic shapes, high resolution",
                    "tags": ["minecraft", "voxel", "blocky"],
                    "use_cases": ["minecraft art", "voxel designs"],
                    "cfg_scale": 6,
                    "steps": 25
                }
            ],
            "Anime": [
                {
                    "id": "anime_character",
                    "name": "Anime Character",
                    "description": "Japanese anime character art style with cel shading",
                    "prompt": "anime character, manga style, cel shaded, Japanese animation style, detailed anime art",
                    "negative_prompt": "realistic, western cartoon, 3D, photorealistic",
                    "tags": ["anime", "character", "manga"],
                    "use_cases": ["character design", "anime illustrations"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "anime_background",
                    "name": "Anime Background",
                    "description": "Beautiful anime-style background scenery and environments",
                    "prompt": "anime background, beautiful scenery, Japanese animation style, detailed environment, anime landscape",
                    "negative_prompt": "realistic photo, western style, dark, gloomy",
                    "tags": ["anime", "background", "scenery"],
                    "use_cases": ["anime backgrounds", "environment art"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "manga_style",
                    "name": "Manga Style",
                    "description": "Black and white manga comic book art style",
                    "prompt": "manga style, black and white, comic book art, Japanese manga, detailed line art",
                    "negative_prompt": "colored, western comic, simple lines, amateur",
                    "tags": ["manga", "comic", "black and white"],
                    "use_cases": ["manga creation", "comic art"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "studio_ghibli",
                    "name": "Studio Ghibli",
                    "description": "Studio Ghibli inspired art style with soft, magical atmosphere",
                    "prompt": "Studio Ghibli style, magical atmosphere, soft colors, beautiful scenery, Miyazaki style",
                    "negative_prompt": "dark, harsh, realistic photo, western animation",
                    "tags": ["Studio Ghibli", "magical", "anime"],
                    "use_cases": ["fantasy art", "magical illustrations"],
                    "cfg_scale": 8,
                    "steps": 35
                }
            ],
            "Retro": [
                {
                    "id": "retro_vintage",
                    "name": "Retro Vintage",
                    "description": "Nostalgic vintage design with retro color palettes",
                    "prompt": "retro vintage style, nostalgic design, vintage colors, classic aesthetic, old school design",
                    "negative_prompt": "modern, contemporary, bright neon, futuristic",
                    "tags": ["retro", "vintage", "nostalgic"],
                    "use_cases": ["vintage designs", "retro branding"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "film_noir",
                    "name": "Film Noir",
                    "description": "Classic film noir aesthetic with dramatic shadows and lighting",
                    "prompt": "film noir style, dramatic shadows, black and white, classic cinema, moody lighting",
                    "negative_prompt": "colorful, bright, modern, cheerful",
                    "tags": ["film noir", "dramatic", "classic"],
                    "use_cases": ["dramatic art", "classic designs"],
                    "cfg_scale": 8,
                    "steps": 35
                }
            ],
            "Fantasy": [
                {
                    "id": "fantasy_world",
                    "name": "Fantasy World",
                    "description": "Magical fantasy world with epic landscapes and mystical elements",
                    "prompt": "fantasy world, magical landscape, epic scenery, mystical atmosphere, fantasy art",
                    "negative_prompt": "realistic, modern, scientific, mundane",
                    "tags": ["fantasy", "magical", "epic"],
                    "use_cases": ["fantasy art", "game environments"],
                    "cfg_scale": 8,
                    "steps": 35
                },
                {
                    "id": "dark_gothic",
                    "name": "Dark Gothic",
                    "description": "Dark gothic aesthetic with mysterious and dramatic atmosphere",
                    "prompt": "dark gothic style, mysterious atmosphere, dramatic shadows, gothic architecture, dark fantasy",
                    "negative_prompt": "bright, cheerful, modern, colorful",
                    "tags": ["gothic", "dark", "mysterious"],
                    "use_cases": ["gothic art", "dark fantasy"],
                    "cfg_scale": 8,
                    "steps": 35
                },
                {
                    "id": "steampunk",
                    "name": "Steampunk",
                    "description": "Victorian-era inspired steampunk with mechanical elements",
                    "prompt": "steampunk style, Victorian era, mechanical elements, brass and copper, steam-powered technology",
                    "negative_prompt": "modern technology, digital, clean, minimalist",
                    "tags": ["steampunk", "mechanical", "Victorian"],
                    "use_cases": ["steampunk art", "mechanical designs"],
                    "cfg_scale": 8,
                    "steps": 35
                }
            ],
            "Animation": [
                {
                    "id": "pixar_style",
                    "name": "Pixar",
                    "description": "Pixar-style 3D animated movie characters and scenes",
                    "prompt": "Pixar style, 3D animated movie, cartoon character, Disney Pixar animation, colorful, family-friendly",
                    "negative_prompt": "realistic, dark, scary, adult content, 2D animation",
                    "tags": ["pixar", "3D animation", "disney"],
                    "use_cases": ["character design", "family content"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "south_park",
                    "name": "South Park",
                    "description": "South Park cartoon style with simple cut-out animation look",
                    "prompt": "South Park style, simple cartoon, cut-out animation, flat colors, comedy cartoon style",
                    "negative_prompt": "realistic, 3D, detailed, complex shading, photorealistic",
                    "tags": ["south park", "cartoon", "comedy"],
                    "use_cases": ["comedy animation", "simple cartoons"],
                    "cfg_scale": 6,
                    "steps": 25
                },
                {
                    "id": "disney_classic",
                    "name": "Disney Classic",
                    "description": "Classic Disney 2D animation style from golden age films",
                    "prompt": "Disney classic animation, 2D cartoon, traditional animation, Disney golden age style, hand-drawn",
                    "negative_prompt": "3D, modern, realistic, computer generated, dark",
                    "tags": ["disney", "classic", "2D animation"],
                    "use_cases": ["classic animation", "fairytale art"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "rick_and_morty",
                    "name": "Rick and Morty",
                    "description": "Rick and Morty adult animated series style",
                    "prompt": "Rick and Morty style, adult swim animation, sci-fi cartoon, colorful, comedy animation style",
                    "negative_prompt": "realistic, serious, photorealistic, live action, 3D",
                    "tags": ["rick and morty", "adult animation", "sci-fi cartoon"],
                    "use_cases": ["adult animation", "sci-fi comedy"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "comic_book",
                    "name": "Comic Book",
                    "description": "Classic comic book art style with bold lines and vibrant colors",
                    "prompt": "comic book art, bold lines, vibrant colors, superhero style, pop art influence",
                    "negative_prompt": "realistic, muted colors, photographic, subtle",
                    "tags": ["comic", "bold", "colorful"],
                    "use_cases": ["comic art", "graphic novels"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "double_exposure",
                    "name": "Double Exposure",
                    "description": "Artistic double exposure effect blending multiple images",
                    "prompt": "double exposure effect, artistic blend, multiple exposures, creative composition, surreal",
                    "negative_prompt": "single image, simple, straightforward, literal",
                    "tags": ["double exposure", "artistic", "creative"],
                    "use_cases": ["artistic photography", "creative designs"],
                    "cfg_scale": 8,
                    "steps": 35
                }
            ],
            "Art": [
                {
                    "id": "minimalist",
                    "name": "Minimalist",
                    "description": "Clean minimalist design with simple forms and limited color palette",
                    "prompt": "minimalist design, clean simple forms, limited color palette, negative space, elegant simplicity",
                    "negative_prompt": "cluttered, complex, busy, ornate, excessive detail",
                    "tags": ["minimalist", "clean", "simple"],
                    "use_cases": ["modern design", "clean aesthetics"],
                    "cfg_scale": 6,
                    "steps": 25
                },
                {
                    "id": "surreal",
                    "name": "Surreal",
                    "description": "Surreal artistic style with dreamlike and impossible elements",
                    "prompt": "surreal art, dreamlike quality, impossible geometry, artistic surrealism, creative composition",
                    "negative_prompt": "realistic, logical, mundane, ordinary, conventional",
                    "tags": ["surreal", "dreamlike", "artistic"],
                    "use_cases": ["surreal art", "creative illustrations"],
                    "cfg_scale": 8,
                    "steps": 35
                },
                {
                    "id": "renaissance",
                    "name": "Renaissance",
                    "description": "Renaissance classical art style with detailed realism",
                    "prompt": "Renaissance art, classical painting, detailed realism, masterpiece, museum quality, traditional techniques",
                    "negative_prompt": "modern, abstract, digital, cartoon, simple",
                    "tags": ["renaissance", "classical", "realistic"],
                    "use_cases": ["classical art", "historical portraits"],
                    "cfg_scale": 8,
                    "steps": 35
                }
            ],
            "Urban": [
                {
                    "id": "graffiti_street",
                    "name": "Graffiti Street Art",
                    "description": "Urban street art and graffiti style with bold colors and urban aesthetic",
                    "prompt": "graffiti street art, urban style, bold colors, spray paint effect, street culture",
                    "negative_prompt": "formal, corporate, clean, traditional, conservative",
                    "tags": ["graffiti", "street art", "urban"],
                    "use_cases": ["urban design", "street art"],
                    "cfg_scale": 7,
                    "steps": 30
                }
            ],
            "Sci-Fi": [
                {
                    "id": "sci_fi_concept",
                    "name": "Sci-Fi Concept",
                    "description": "Futuristic science fiction concept art with advanced technology",
                    "prompt": "sci-fi concept art, futuristic technology, space age design, advanced civilization, concept design",
                    "negative_prompt": "primitive, medieval, low-tech, rustic, natural",
                    "tags": ["sci-fi", "futuristic", "technology"],
                    "use_cases": ["sci-fi art", "concept design"],
                    "cfg_scale": 8,
                    "steps": 35
                },
                {
                    "id": "space_exploration",
                    "name": "Space Exploration",
                    "description": "Space exploration themes with cosmic landscapes and spacecraft",
                    "prompt": "space exploration, cosmic landscape, spacecraft, stars and galaxies, space travel",
                    "negative_prompt": "earthbound, terrestrial, familiar, mundane",
                    "tags": ["space", "exploration", "cosmic"],
                    "use_cases": ["space art", "cosmic designs"],
                    "cfg_scale": 8,
                    "steps": 35
                }
            ],
            "Nature": [
                {
                    "id": "nature_landscape",
                    "name": "Nature Landscape",
                    "description": "Beautiful natural landscapes with organic forms and natural lighting",
                    "prompt": "nature landscape, beautiful scenery, natural lighting, organic forms, peaceful environment",
                    "negative_prompt": "urban, artificial, mechanical, industrial, harsh",
                    "tags": ["nature", "landscape", "organic"],
                    "use_cases": ["landscape art", "nature photography"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "underwater",
                    "name": "Underwater",
                    "description": "Underwater scenes with marine life and aquatic environments",
                    "prompt": "underwater scene, marine life, aquatic environment, ocean depths, underwater photography",
                    "negative_prompt": "surface, dry, terrestrial, above water",
                    "tags": ["underwater", "marine", "aquatic"],
                    "use_cases": ["underwater photography", "marine art"],
                    "cfg_scale": 7,
                    "steps": 30
                }
            ],
            "Fashion": [
                {
                    "id": "fashion_editorial",
                    "name": "Fashion Editorial",
                    "description": "High-fashion editorial photography with dramatic styling",
                    "prompt": "fashion editorial photography, high fashion, dramatic styling, professional modeling, fashion magazine",
                    "negative_prompt": "casual wear, everyday clothing, amateur, simple",
                    "tags": ["fashion", "editorial", "high fashion"],
                    "use_cases": ["fashion photography", "editorial shoots"],
                    "cfg_scale": 8,
                    "steps": 35
                }
            ],
            "Horror": [
                {
                    "id": "horror_atmospheric",
                    "name": "Horror Atmospheric",
                    "description": "Atmospheric horror with dark, eerie, and unsettling elements",
                    "prompt": "horror atmosphere, dark and eerie, unsettling mood, gothic horror, creepy ambiance",
                    "negative_prompt": "bright, cheerful, comforting, safe, pleasant",
                    "tags": ["horror", "dark", "atmospheric"],
                    "use_cases": ["horror art", "dark atmospheres"],
                    "cfg_scale": 8,
                    "steps": 35
                }
            ],
            "Achievement": [
                {
                    "id": "achievement_badge",
                    "name": "Achievement Badge",
                    "description": "Gaming-style achievement badge with metallic effects and emblematic design",
                    "prompt": "achievement badge, gaming trophy, metallic effects, emblematic design, award symbol",
                    "negative_prompt": "plain, simple, non-metallic, dull, boring",
                    "tags": ["achievement", "badge", "award"],
                    "use_cases": ["gaming achievements", "award designs"],
                    "cfg_scale": 7,
                    "steps": 30
                },
                {
                    "id": "trophy_gold",
                    "name": "Golden Trophy",
                    "description": "Prestigious golden trophy design with elegant form and luxurious finish",
                    "prompt": "golden trophy, prestigious award, elegant design, luxurious finish, championship trophy",
                    "negative_prompt": "cheap, plastic, dull, simple, unimpressive",
                    "tags": ["trophy", "gold", "prestigious"],
                    "use_cases": ["awards", "competitions"],
                    "cfg_scale": 8,
                    "steps": 35
                }
            ]
        }
    }
    
    return Response(styles)


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
        # Return default settings (will store in profile later)
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
        settings = request.data
        
        # TODO: Save settings to user profile when metadata field is available
        
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
@permission_classes([AllowAny])
def agent_executions_list(request):
    """Get list of agent executions (actual task runs with results)"""
    from agents.models import AgentExecution
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
def prompt_diagnostics_templates(request):
    """Placeholder prompt diagnostics templates endpoint"""
    return Response({
        'templates': [],
        'pagination': {
            'total': 0,
            'limit': 50,
            'offset': 0,
            'has_next': False
        }
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
    Personal AI Assistant Chat - powered by real AI providers with RAG
    """
    user = request.user
    logger = logging.getLogger(__name__)
    
    try:
        # Use request.data for DRF views instead of request.body
        message = request.data.get('message', '').strip()
        conversation_id = request.data.get('conversation_id', str(uuid.uuid4()))
        use_personal_assistant = request.data.get('use_personal_assistant', True)
        use_rag = request.data.get('use_rag', True)  # Enable RAG by default
        
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
            
            # Create system prompt for personal assistant
            system_prompt = f"""You are {user.username if hasattr(user, 'username') else user.email}'s personal AI assistant.

CRITICAL RESPONSE GUIDELINES:
1. Be EXTREMELY CONCISE - default to 1-3 sentences unless specifically asked for details
2. Answer the question directly without preamble or excessive explanation
3. Only provide detailed breakdowns when explicitly requested
4. Don't list all available features/options unless asked
5. Avoid bullet points and numbered lists unless essential
6. Match the brevity of the user's question with your response

For simple questions like "What's going on?" - give a ONE sentence overview.
For complex requests - provide the essential answer first, then ask if they need more detail.

You are a general-purpose AI assistant who can help with any topic - coding, research, analysis, creative tasks, problem-solving, conversations, and more. You have access to a comprehensive knowledge base and can orchestrate specialized AI agents when needed for complex tasks.

Remember: BREVITY IS KEY. Most responses should be 1-3 sentences maximum."""

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
    from django.core.paginator import Paginator
    
    # Get query parameters (support both per_page and page_size)
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('per_page', request.GET.get('page_size', 12)))
    
    try:
        # Connect to ai_unified_platform database
        conn = psycopg2.connect(
            host='localhost',
            database='ai_unified_platform',
            user='ai_unified_user',
            password='ai_unified_pass_2025'
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
                except:
                    pass
            
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