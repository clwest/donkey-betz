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
import logging

# Import content models for database persistence
from content.models import ContentGeneration, ContentStatus

# Import image generation service
try:
    from content.image_generation import image_generation_service
    HAS_IMAGE_GENERATION = True
except ImportError as e:
    HAS_IMAGE_GENERATION = False
    logging.warning(f"Image generation service not available: {e}")

User = get_user_model()
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_content(request):
    """
    Create new content - migrated from ai-content-studio
    """
    user = request.user
    
    # Handle both request.data (DRF) and request.body (raw JSON)
    if hasattr(request, 'data'):
        data = request.data
    else:
        data = json.loads(request.body)
    
    content_type = data.get('content_type', 'text')
    prompt = data.get('prompt', '')
    style = data.get('style', 'default')
    length = data.get('length', 'medium')
    size = data.get('size', '1024x1024')
    
    # Simulate content generation
    content_id = int(datetime.now().timestamp())
    
    # Create response based on content type
    response_data = {
        'success': True,
        'content': {
            'id': content_id,
            'type': content_type,
            'prompt': prompt,
            'style': style,
            'status': 'generated',
            'created_at': datetime.now().isoformat(),
        }
    }
    
    if content_type == 'image':
        # Create ContentGeneration record for database persistence
        generation_record = ContentGeneration.objects.create(
            user=user,
            prompt=prompt,
            generation_config={
                'content_type': content_type,
                'style': style,
                'size': size,
                'negative_prompt': data.get('negative_prompt', ''),
                'batch_size': data.get('batch_size', 1),
                'quality': data.get('quality', 'standard'),
                'cfg_scale': data.get('cfg_scale', 7.0),
                'steps': data.get('steps', 30),
            },
            status=ContentStatus.PROCESSING
        )
        
        # Use real AI image generation if available
        if HAS_IMAGE_GENERATION:
            try:
                # Extract additional parameters
                negative_prompt = data.get('negative_prompt', '')
                num_images = data.get('batch_size', 1)
                quality = data.get('quality', 'standard')
                cfg_scale = data.get('cfg_scale', 7.0)
                steps = data.get('steps', 30)
                
                # Generate images using AI service
                result = image_generation_service.generate_image(
                    prompt=prompt,
                    style=style,
                    size=size,
                    negative_prompt=negative_prompt,
                    num_images=min(num_images, 4),  # Limit to 4 for safety
                    quality=quality,
                    cfg_scale=cfg_scale,
                    steps=steps
                )
                
                if result.success and result.images:
                    # Save successful generation to database
                    generation_record.generated_content = json.dumps({
                        'images': result.images,
                        'provider': result.provider_used,
                        'model': result.model_used
                    })
                    generation_record.status = ContentStatus.PROCESSED
                    generation_record.generation_time_ms = result.generation_time_ms
                    generation_record.token_usage = {
                        'images_generated': len(result.images),
                        'provider': result.provider_used
                    }
                    generation_record.save()
                    
                    # Format images for frontend
                    images = []
                    for i, image_url in enumerate(result.images):
                        images.append({
                            'id': f"{generation_record.id}_{i}",
                            'url': image_url,
                            'image_url': image_url,
                            'result': image_url,
                            'result_url': image_url,
                            'type': 'image',
                            'title': f"{prompt[:50]}..." if len(prompt) > 50 else prompt,
                            'prompt': prompt,
                            'style': style,
                            'size': size,
                            'created_at': generation_record.created_at.isoformat(),
                            'generation_id': str(generation_record.id)
                        })
                    
                    response_data['content']['images'] = images
                    response_data['content']['result'] = images[0]['url'] if images else None
                    response_data['content']['results'] = images
                    response_data['content']['generation_id'] = str(generation_record.id)
                    response_data['content']['metadata'] = {
                        'style_applied': style,
                        'size': size,
                        'variations': len(images),
                        'provider': result.provider_used,
                        'model': result.model_used,
                        'generation_time_ms': result.generation_time_ms,
                        'database_id': str(generation_record.id)
                    }
                else:
                    # If AI generation fails, log error and use fallback
                    logger.error(f"AI image generation failed: {result.error_message}")
                    generation_record.status = ContentStatus.FAILED
                    generation_record.error_message = result.error_message
                    
                    # Fall back to placeholder images
                    base_url = 'https://picsum.photos'
                    width, height = size.split('x')
                    images = []
                    for i in range(min(num_images, 4)):
                        seed = int(str(generation_record.id)[-6:]) + i  # Use generation ID for seed
                        image_url = f"{base_url}/{width}/{height}?random={seed}"
                        images.append({
                            'id': f"{generation_record.id}_{i}",
                            'url': image_url,
                            'image_url': image_url,
                            'result': image_url,
                            'result_url': image_url,
                            'type': 'image',
                            'title': f"{prompt[:50]}..." if len(prompt) > 50 else prompt,
                            'prompt': prompt,
                            'style': style,
                            'size': size,
                            'created_at': generation_record.created_at.isoformat(),
                            'generation_id': str(generation_record.id)
                        })
                    
                    # Save fallback images to database
                    generation_record.generated_content = json.dumps({
                        'images': [img['url'] for img in images],
                        'provider': 'fallback',
                        'model': 'placeholder'
                    })
                    generation_record.save()
                    
                    response_data['content']['images'] = images
                    response_data['content']['result'] = images[0]['url'] if images else None
                    response_data['content']['results'] = images
                    response_data['content']['generation_id'] = str(generation_record.id)
                    response_data['content']['metadata'] = {
                        'style_applied': style,
                        'size': size,
                        'variations': len(images),
                        'note': 'Using placeholder images - AI generation unavailable',
                        'database_id': str(generation_record.id)
                    }
                    
            except Exception as e:
                logger.error(f"Error in AI image generation: {str(e)}")
                generation_record.status = ContentStatus.FAILED
                generation_record.error_message = str(e)
                
                # Fall back to placeholder images
                base_url = 'https://picsum.photos'
                width, height = size.split('x')
                images = []
                for i in range(4):
                    seed = int(str(generation_record.id)[-6:]) + i
                    image_url = f"{base_url}/{width}/{height}?random={seed}"
                    images.append({
                        'id': f"{generation_record.id}_{i}",
                        'url': image_url,
                        'image_url': image_url,
                        'result': image_url,
                        'result_url': image_url,
                        'type': 'image',
                        'title': f"{prompt[:50]}..." if len(prompt) > 50 else prompt,
                        'prompt': prompt,
                        'style': style,
                        'size': size,
                        'created_at': generation_record.created_at.isoformat(),
                        'generation_id': str(generation_record.id)
                    })
                
                # Save exception fallback to database
                generation_record.generated_content = json.dumps({
                    'images': [img['url'] for img in images],
                    'provider': 'exception_fallback',
                    'model': 'placeholder',
                    'error': str(e)
                })
                generation_record.save()
                
                response_data['content']['images'] = images
                response_data['content']['result'] = images[0]['url'] if images else None
                response_data['content']['results'] = images
                response_data['content']['generation_id'] = str(generation_record.id)
                response_data['content']['metadata'] = {
                    'style_applied': style,
                    'size': size,
                    'variations': len(images),
                    'error': str(e),
                    'database_id': str(generation_record.id)
                }
        else:
            # No AI service available, use placeholder images
            generation_record.status = ContentStatus.PROCESSED
            generation_record.error_message = "AI image generation service not configured"
            
            base_url = 'https://picsum.photos'
            width, height = size.split('x')
            images = []
            for i in range(4):
                seed = int(str(generation_record.id)[-6:]) + i
                image_url = f"{base_url}/{width}/{height}?random={seed}"
                images.append({
                    'id': f"{generation_record.id}_{i}",
                    'url': image_url,
                    'image_url': image_url,
                    'result': image_url,
                    'result_url': image_url,
                    'type': 'image',
                    'title': f"{prompt[:50]}..." if len(prompt) > 50 else prompt,
                    'prompt': prompt,
                    'style': style,
                    'size': size,
                    'created_at': generation_record.created_at.isoformat(),
                    'generation_id': str(generation_record.id)
                })
            
            # Save no-service fallback to database
            generation_record.generated_content = json.dumps({
                'images': [img['url'] for img in images],
                'provider': 'no_service',
                'model': 'placeholder'
            })
            generation_record.save()
            
            response_data['content']['images'] = images
            response_data['content']['result'] = images[0]['url'] if images else None
            response_data['content']['results'] = images
            response_data['content']['generation_id'] = str(generation_record.id)
            response_data['content']['metadata'] = {
                'style_applied': style,
                'size': size,
                'variations': len(images),
                'note': 'AI image generation service not configured',
                'database_id': str(generation_record.id)
            }
    else:
        # For text content
        response_data['content']['length'] = length
        response_data['content']['generated_content'] = f'Generated {content_type} content based on: {prompt}'
        response_data['content']['metadata'] = {
            'word_count': 250 if length == 'medium' else 150,
            'estimated_read_time': '1-2 minutes',
            'style_applied': style
        }
    
    return Response(response_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_content(request):
    """
    List user's content library - now returns real data from ContentGeneration model
    """
    user = request.user
    content_type = request.GET.get('type', 'all')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    # Query real ContentGeneration records
    content_query = ContentGeneration.objects.filter(user=user).order_by('-created_at')
    
    # Filter by content type if specified
    if content_type != 'all':
        if content_type == 'image':
            # Filter for image generations
            content_query = content_query.filter(
                generation_config__content_type='image'
            )
        elif content_type == 'text':
            # Filter for text generations
            content_query = content_query.exclude(
                generation_config__content_type='image'
            )
    
    # Get total count
    total_count = content_query.count()
    
    # Apply pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_content = content_query[start_idx:end_idx]
    
    # Format content for frontend
    results = []
    for content in paginated_content:
        # Parse generated content
        generated_data = {}
        if content.generated_content:
            try:
                generated_data = json.loads(content.generated_content)
            except json.JSONDecodeError:
                generated_data = {}
        
        # Determine content type from generation config
        gen_config = content.generation_config or {}
        item_type = gen_config.get('content_type', 'text')
        
        # Create base item
        item = {
            'id': str(content.id),
            'title': f"{content.prompt[:50]}..." if len(content.prompt) > 50 else content.prompt,
            'type': item_type,
            'status': content.status,
            'created_at': content.created_at.isoformat(),
            'updated_at': content.updated_at.isoformat(),
            'is_starred': False,  # TODO: Implement starring system
            'prompt': content.prompt,
            'generation_id': str(content.id)
        }
        
        # Add type-specific data
        if item_type == 'image':
            images = generated_data.get('images', [])
            item.update({
                'image_count': len(images),
                'image_urls': images,
                'result': images[0] if images else None,
                'style': gen_config.get('style', 'default'),
                'size': gen_config.get('size', '1024x1024'),
                'provider': generated_data.get('provider', 'unknown')
            })
        else:
            # For text content
            item.update({
                'word_count': len(content.generated_content.split()) if content.generated_content else 0,
                'generated_content': content.generated_content
            })
        
        results.append(item)
    
    return Response({
        'success': True,
        'count': total_count,
        'next': f'/api/content/list/?page={page + 1}&type={content_type}' if end_idx < total_count else None,
        'previous': f'/api/content/list/?page={page - 1}&type={content_type}' if page > 1 else None,
        'results': results
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
    
    # Generate blog content
    title = f'Comprehensive Guide to {topic}'
    outline = [
        'Introduction',
        f'Understanding {topic}',
        'Best Practices and Strategies',
        'Common Challenges and Solutions',
        'Future Outlook',
        'Conclusion'
    ] if include_outline else None
    
    content_text = f'Generated comprehensive blog post about {topic} in {tone} tone...'
    word_count = 1200 if length == 'long' else 800
    
    # Create ContentGeneration record in database
    try:
        content_generation = ContentGeneration.objects.create(
            user=user,
            prompt=f"Write a {length} {tone} blog post about {topic}",
            generated_content=content_text,
            status='completed',
            generation_config={
                'content_type': 'blog',
                'tone': tone,
                'length': length,
                'include_outline': include_outline,
                'topic': topic
            },
            metadata={
                'title': title,
                'content': content_text,
                'outline': outline,
                'blog_metadata': {
                    'word_count': word_count,
                    'reading_time': '6-8 minutes',
                    'seo_score': 85,
                    'readability': 'Good'
                }
            }
        )
        
        return Response({
            'success': True,
            'blog_post': {
                'id': str(content_generation.id),
                'title': title,
                'topic': topic,
                'tone': tone,
                'length': length,
                'status': 'completed',
                'created_at': content_generation.created_at.isoformat(),
                'outline': outline,
                'content': content_text,
                'metadata': {
                    'word_count': word_count,
                    'reading_time': '6-8 minutes',
                    'seo_score': 85,
                    'readability': 'Good'
                }
            }
        })
        
    except Exception as e:
        print(f"Error creating blog content: {e}")
        return Response({
            'success': False,
            'error': f'Failed to generate blog content: {str(e)}'
        }, status=500)

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
    
    # Generate the social media content
    content_text = f'Engaging {platform} post about {topic}... #trending #content'
    hashtags = ['#trending', '#content', '#marketing', '#growth'] if include_hashtags else []
    
    # Create ContentGeneration record in database
    try:
        content_generation = ContentGeneration.objects.create(
            user=user,
            prompt=f"Create a {tone} {platform} post about {topic}",
            generated_content=content_text,
            status='completed',
            generation_config={
                'content_type': 'social',
                'platform': platform,
                'tone': tone,
                'character_limit': char_limit,
                'include_hashtags': include_hashtags
            },
            metadata={
                'content': content_text,
                'hashtags': hashtags,
                'platform': platform,
                'estimated_reach': 1500,
                'engagement_score': 78,
                'character_count': len(content_text)
            }
        )
        
        return Response({
            'success': True,
            'social_post': {
                'id': str(content_generation.id),
                'platform': platform,
                'topic': topic,
                'tone': tone,
                'character_limit': char_limit,
                'content': content_text,
                'hashtags': hashtags,
                'estimated_reach': 1500,
                'engagement_score': 78,
                'created_at': content_generation.created_at.isoformat()
            }
        })
        
    except Exception as e:
        print(f"Error creating social content: {e}")
        return Response({
            'success': False,
            'error': f'Failed to generate social content: {str(e)}'
        }, status=500)

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
def gallery_list(request):
    """
    Get gallery images - endpoint that frontend expects
    """
    limit = int(request.GET.get('limit', 50))
    
    # Get images from ContentGeneration model
    images = []
    
    # Mock some sample images for now since we don't have actual images stored yet
    sample_images = [
        {
            'id': 1,
            'title': 'Sample Image 1',
            'image_url': '/media/images/sample1.jpg',
            'tags': ['sample', 'test'],
            'category': 'generated',
            'saved_at': '2024-01-01T00:00:00Z',
            'is_public': False,
            'style_used': 'realistic'
        }
    ]
    
    return JsonResponse({
        'success': True,
        'images': sample_images[:limit]
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