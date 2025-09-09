"""
Content generation and management endpoints migrated from ai-content-studio.
Provides comprehensive content creation, editing, and library management.
"""

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from datetime import datetime
import json
import uuid

User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_content(request):
    """
    Create new content - migrated from ai-content-studio
    """
    user = request.user
    data = json.loads(request.body)
    
    content_type = data.get('content_type', 'text')
    prompt = data.get('prompt', '')
    style = data.get('style', 'default')
    length = data.get('length', 'medium')
    
    # Simulate content generation
    content_id = int(datetime.now().timestamp())
    
    return Response({
        'success': True,
        'content': {
            'id': content_id,
            'type': content_type,
            'prompt': prompt,
            'style': style,
            'length': length,
            'status': 'generated',
            'created_at': datetime.now().isoformat(),
            'generated_content': f'Generated {content_type} content based on: {prompt}',
            'metadata': {
                'word_count': 250 if length == 'medium' else 150,
                'estimated_read_time': '1-2 minutes',
                'style_applied': style
            }
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_content(request):
    """
    List user's content library - migrated from ai-content-studio
    """
    user = request.user
    content_type = request.GET.get('type', 'all')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    # Mock content data
    mock_content = [
        {
            'id': i,
            'title': f'Content Item {i}',
            'type': 'article',
            'status': 'published',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'word_count': 450 + (i * 50),
            'is_starred': i % 3 == 0
        }
        for i in range(1, 51)
    ]
    
    # Apply pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_content = mock_content[start_idx:end_idx]
    
    return Response({
        'success': True,
        'count': len(mock_content),
        'next': f'/api/content/list/?page={page + 1}' if end_idx < len(mock_content) else None,
        'previous': f'/api/content/list/?page={page - 1}' if page > 1 else None,
        'results': paginated_content
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_blog_post(request):
    """
    Generate blog post - migrated from ai-content-studio blog system
    """
    user = request.user
    data = json.loads(request.body)
    
    topic = data.get('topic', '')
    tone = data.get('tone', 'professional')
    length = data.get('length', 'medium')
    include_outline = data.get('include_outline', True)
    
    blog_id = int(datetime.now().timestamp())
    
    return Response({
        'success': True,
        'blog_post': {
            'id': blog_id,
            'title': f'Comprehensive Guide to {topic}',
            'topic': topic,
            'tone': tone,
            'length': length,
            'status': 'draft',
            'created_at': datetime.now().isoformat(),
            'outline': [
                'Introduction',
                f'Understanding {topic}',
                'Best Practices and Strategies',
                'Common Challenges and Solutions',
                'Future Outlook',
                'Conclusion'
            ] if include_outline else None,
            'content': f'Generated comprehensive blog post about {topic} in {tone} tone...',
            'metadata': {
                'word_count': 1200 if length == 'long' else 800,
                'reading_time': '6-8 minutes',
                'seo_score': 85,
                'readability': 'Good'
            }
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_social_media_post(request):
    """
    Generate social media content - migrated from ai-content-studio social system
    """
    user = request.user
    data = json.loads(request.body)
    
    platform = data.get('platform', 'twitter')
    topic = data.get('topic', '')
    tone = data.get('tone', 'engaging')
    include_hashtags = data.get('include_hashtags', True)
    
    platform_limits = {
        'twitter': 280,
        'linkedin': 3000,
        'facebook': 2000,
        'instagram': 2200
    }
    
    char_limit = platform_limits.get(platform, 280)
    
    return Response({
        'success': True,
        'social_post': {
            'id': int(datetime.now().timestamp()),
            'platform': platform,
            'topic': topic,
            'tone': tone,
            'character_limit': char_limit,
            'content': f'Engaging {platform} post about {topic}... #trending #content',
            'hashtags': [
                '#trending', '#content', '#marketing', '#growth'
            ] if include_hashtags else [],
            'estimated_reach': 1500,
            'engagement_score': 78,
            'created_at': datetime.now().isoformat()
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_video_script(request):
    """
    Generate video script - migrated from ai-content-studio video system
    """
    user = request.user
    data = json.loads(request.body)
    
    topic = data.get('topic', '')
    duration = data.get('duration', 60)  # seconds
    style = data.get('style', 'educational')
    include_narration = data.get('include_narration', True)
    
    return Response({
        'success': True,
        'video_script': {
            'id': int(datetime.now().timestamp()),
            'topic': topic,
            'duration': duration,
            'style': style,
            'scenes': [
                {
                    'scene_number': 1,
                    'duration': 10,
                    'visual_description': 'Opening title with engaging animation',
                    'narration': f'Welcome to our guide on {topic}',
                    'notes': 'Use brand colors and logo'
                },
                {
                    'scene_number': 2,
                    'duration': 40,
                    'visual_description': 'Main content with supporting visuals',
                    'narration': f'Let\'s dive deep into {topic} and explore key concepts',
                    'notes': 'Include charts and infographics'
                },
                {
                    'scene_number': 3,
                    'duration': 10,
                    'visual_description': 'Call to action with contact information',
                    'narration': 'Subscribe for more content like this',
                    'notes': 'Include social media handles'
                }
            ],
            'total_word_count': 150,
            'estimated_production_time': '2-3 hours',
            'created_at': datetime.now().isoformat()
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def content_templates(request):
    """
    Get available content templates - migrated from ai-content-studio
    """
    template_type = request.GET.get('type', 'all')
    
    templates = {
        'blog': [
            {
                'id': 'how-to-guide',
                'name': 'How-To Guide',
                'description': 'Step-by-step instructional content',
                'sections': ['Introduction', 'Prerequisites', 'Steps', 'Conclusion'],
                'estimated_length': '800-1200 words'
            },
            {
                'id': 'listicle',
                'name': 'Listicle',
                'description': 'List-based article format',
                'sections': ['Introduction', 'List Items', 'Conclusion'],
                'estimated_length': '600-1000 words'
            }
        ],
        'social': [
            {
                'id': 'announcement',
                'name': 'Product Announcement',
                'description': 'Launch new products or features',
                'platforms': ['twitter', 'linkedin', 'facebook'],
                'elements': ['Hook', 'Features', 'CTA']
            },
            {
                'id': 'educational',
                'name': 'Educational Post',
                'description': 'Share knowledge and insights',
                'platforms': ['linkedin', 'twitter'],
                'elements': ['Problem', 'Solution', 'Value']
            }
        ],
        'video': [
            {
                'id': 'explainer',
                'name': 'Explainer Video',
                'description': 'Educational content that explains concepts',
                'duration_range': '60-180 seconds',
                'scenes': ['Hook', 'Problem', 'Solution', 'CTA']
            },
            {
                'id': 'testimonial',
                'name': 'Customer Testimonial',
                'description': 'Showcase customer success stories',
                'duration_range': '30-90 seconds',
                'scenes': ['Introduction', 'Story', 'Results', 'Recommendation']
            }
        ]
    }
    
    if template_type == 'all':
        return Response({'success': True, 'templates': templates})
    else:
        return Response({
            'success': True,
            'templates': {template_type: templates.get(template_type, [])}
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_file_to_memory(request):
    """
    Import file to memory system - migrated from ai-content-studio
    """
    user = request.user
    
    # In a real implementation, this would handle file uploads
    file_data = {
        'file_name': 'example_document.pdf',
        'file_type': 'pdf',
        'file_size': '2.5MB',
        'pages': 15
    }
    
    memory_id = int(datetime.now().timestamp())
    
    return Response({
        'success': True,
        'import_result': {
            'memory_id': memory_id,
            'file_info': file_data,
            'processing_status': 'completed',
            'extracted_content': {
                'text_chunks': 45,
                'key_concepts': ['AI', 'Machine Learning', 'Data Science'],
                'summary': 'Document contains technical information about AI implementations'
            },
            'search_enabled': True,
            'created_at': datetime.now().isoformat()
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supported_file_formats(request):
    """
    Get supported file formats for import - migrated from ai-content-studio
    """
    return Response({
        'success': True,
        'supported_formats': {
            'documents': ['.pdf', '.docx', '.txt', '.md'],
            'images': ['.jpg', '.png', '.gif', '.webp'],
            'videos': ['.mp4', '.avi', '.mov', '.webm'],
            'audio': ['.mp3', '.wav', '.m4a'],
            'data': ['.csv', '.json', '.xml'],
            'max_file_size': '50MB',
            'batch_upload_limit': 10
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gallery_videos(request):
    """
    Get video gallery content.
    """
    user = request.user
    limit = request.GET.get('limit', 50)
    
    # Mock video data - matching frontend expectations
    videos = [
        {
            'id': 1,
            'title': 'Business Strategy Presentation',
            'description': 'Comprehensive business strategy analysis and recommendations',
            'video_url': 'https://example.com/videos/business-strategy.mp4',
            'thumbnail_url': 'https://example.com/thumbnails/business-strategy.jpg',
            'duration': '15:30',
            'size': '45.2MB',
            'saved_at': datetime.now().isoformat(),
            'views': 234,
            'tags': ['business', 'strategy', 'analysis'],
            'source_type': 'generated',
            'original_prompt': 'Create a business strategy presentation video',
            'motion_prompt': 'Professional presentation with charts and graphs',
            'category': 'business'
        },
        {
            'id': 2,
            'title': 'Market Analysis Deep Dive',
            'description': 'In-depth market research and competitive analysis',
            'video_url': 'https://example.com/videos/market-analysis.mp4',
            'thumbnail_url': 'https://example.com/thumbnails/market-analysis.jpg',
            'duration': '22:45',
            'size': '78.1MB',
            'saved_at': datetime.now().isoformat(),
            'views': 189,
            'tags': ['market', 'research', 'competitive'],
            'source_type': 'generated',
            'original_prompt': 'Create a market analysis video with data visualization',
            'motion_prompt': 'Animated charts and market trends',
            'category': 'research'
        },
        {
            'id': 3,
            'title': 'Product Launch Campaign',
            'description': 'Complete product launch strategy and execution plan',
            'video_url': 'https://example.com/videos/product-launch.mp4',
            'thumbnail_url': 'https://example.com/thumbnails/product-launch.jpg',
            'duration': '18:20',
            'size': '52.7MB',
            'saved_at': datetime.now().isoformat(),
            'views': 312,
            'tags': ['product', 'launch', 'campaign'],
            'source_type': 'generated',
            'original_prompt': 'Create a product launch campaign video',
            'motion_prompt': 'Dynamic product showcase with transitions',
            'category': 'marketing'
        }
    ]
    
    return Response({
        'success': True,
        'videos': videos[:int(limit)],
        'total_count': len(videos),
        'page_size': int(limit)
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def content_library(request):
    """
    Get content library items by type.
    """
    user = request.user
    content_type = request.GET.get('type', 'all')
    
    # Mock library content
    library_items = []
    
    if content_type in ['podcast', 'all']:
        library_items.extend([
            {
                'id': str(uuid.uuid4()),
                'type': 'podcast',
                'title': 'AI Business Transformation Podcast',
                'description': 'Weekly insights on AI-driven business transformation',
                'url': 'https://example.com/podcasts/ai-business.mp3',
                'thumbnail': 'https://example.com/thumbnails/ai-business.jpg',
                'duration': '45:30',
                'episode_number': 23,
                'published_at': datetime.now().isoformat(),
                'downloads': 1456
            },
            {
                'id': str(uuid.uuid4()),
                'type': 'podcast',
                'title': 'Market Strategy Deep Dive',
                'description': 'Expert analysis of market trends and strategic opportunities',
                'url': 'https://example.com/podcasts/market-strategy.mp3',
                'thumbnail': 'https://example.com/thumbnails/market-strategy.jpg',
                'duration': '38:15',
                'episode_number': 24,
                'published_at': datetime.now().isoformat(),
                'downloads': 892
            }
        ])
    
    if content_type in ['document', 'all']:
        library_items.extend([
            {
                'id': str(uuid.uuid4()),
                'type': 'document',
                'title': 'Strategic Planning Guide 2024',
                'description': 'Comprehensive guide to strategic business planning',
                'url': 'https://example.com/docs/strategic-planning-2024.pdf',
                'thumbnail': 'https://example.com/thumbnails/strategic-planning.jpg',
                'pages': 45,
                'size': '2.3MB',
                'published_at': datetime.now().isoformat(),
                'downloads': 567
            }
        ])
    
    return Response({
        'success': True,
        'library_items': library_items,
        'total_count': len(library_items),
        'content_type': content_type
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def podcasts_list(request):
    """
    Get podcast episodes list.
    """
    user = request.user
    
    # Mock podcast data
    podcasts = [
        {
            'id': str(uuid.uuid4()),
            'title': 'AI Business Transformation',
            'description': 'Weekly insights on AI-driven business transformation and strategy',
            'host': 'Business Strategy Team',
            'url': 'https://example.com/podcasts/ai-business.mp3',
            'thumbnail': 'https://example.com/thumbnails/ai-business.jpg',
            'duration': '45:30',
            'episode_number': 23,
            'season': 2,
            'published_at': datetime.now().isoformat(),
            'downloads': 1456,
            'rating': 4.7,
            'transcript_available': True
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Market Strategy Deep Dive',
            'description': 'Expert analysis of market trends, competitive landscapes, and strategic opportunities',
            'host': 'Market Analysis Team',
            'url': 'https://example.com/podcasts/market-strategy.mp3',
            'thumbnail': 'https://example.com/thumbnails/market-strategy.jpg',
            'duration': '38:15',
            'episode_number': 24,
            'season': 2,
            'published_at': datetime.now().isoformat(),
            'downloads': 892,
            'rating': 4.5,
            'transcript_available': True
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Product Innovation Spotlight',
            'description': 'Featuring innovative products and breakthrough technologies shaping the future',
            'host': 'Innovation Team',
            'url': 'https://example.com/podcasts/product-innovation.mp3',
            'thumbnail': 'https://example.com/thumbnails/product-innovation.jpg',
            'duration': '52:10',
            'episode_number': 25,
            'season': 2,
            'published_at': datetime.now().isoformat(),
            'downloads': 1203,
            'rating': 4.8,
            'transcript_available': False
        }
    ]
    
    return Response({
        'success': True,
        'podcasts': podcasts,
        'total_count': len(podcasts)
    })