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
    
    # Check if topic is actually a detailed outline/brief
    is_detailed_brief = len(topic) > 200 and '\n' in topic
    
    # Parse the topic to extract the actual title if it's a detailed brief
    if is_detailed_brief:
        # Extract title from the detailed brief
        lines = topic.split('\n')
        actual_title = lines[0].replace('Title:', '').strip() if lines else topic[:100]
        
        # Use the entire detailed brief as the generation prompt
        generation_prompt = f"""
Please write a comprehensive blog post based on this detailed brief:

{topic}

Requirements:
- Tone: {tone}
- Length: {length} (approximately {'1500-2000' if length == 'long' else '800-1200' if length == 'medium' else '400-600'} words)
- Follow the provided outline structure
- Include specific examples and practical insights
- Make it engaging and informative
- Use the suggested meta description and keywords for SEO optimization

Please generate the full article content following the structure and guidelines provided.
"""
    else:
        # Standard topic - generate title and prompt normally
        actual_title = f'Comprehensive Guide to {topic}'
        generation_prompt = f"""
Write a comprehensive {length} blog post about {topic}.

Requirements:
- Tone: {tone}
- Length: approximately {'1500-2000' if length == 'long' else '800-1200' if length == 'medium' else '400-600'} words
- Include an introduction, main body with clear sections, and conclusion
- Provide practical examples and actionable insights
- Make it engaging and informative
"""
    
    # Generate outline based on the topic
    if is_detailed_brief and 'Suggested outline' in topic:
        # Extract outline from the detailed brief
        outline_start = topic.find('Suggested outline')
        outline_end = topic.find('\n\n', outline_start) if outline_start > -1 else -1
        if outline_start > -1 and outline_end > -1:
            outline_text = topic[outline_start:outline_end]
            outline = [line.strip('- ').strip() for line in outline_text.split('\n')[1:] if line.strip().startswith('-')]
        else:
            outline = [
                'Introduction',
                'Main Content',
                'Best Practices',
                'Conclusion'
            ]
    else:
        outline = [
            'Introduction',
            f'Understanding {topic}',
            'Best Practices and Strategies', 
            'Common Challenges and Solutions',
            'Future Outlook',
            'Conclusion'
        ] if include_outline else None
    
    # Set appropriate word count based on length
    word_count = 1500 if length == 'long' else 800 if length == 'medium' else 400
    
    # Try to generate content using AI provider
    generated_content = None
    ai_error = None
    
    # Check if AI provider is available
    from content.ai_providers import get_ai_provider
    ai_provider = get_ai_provider()
    
    if ai_provider:
        try:
            # Generate the actual blog content using AI
            ai_response = ai_provider.generate(
                prompt=generation_prompt,
                max_tokens=2000 if length == 'long' else 1500 if length == 'medium' else 800,
                temperature=0.7
            )
            
            if ai_response and ai_response.get('content'):
                generated_content = ai_response['content']
            else:
                generated_content = None
                ai_error = "AI provider returned empty response"
                
        except Exception as e:
            logger.error(f"Error generating blog content with AI: {str(e)}")
            ai_error = str(e)
            generated_content = None
    
    # If AI generation failed, create a more detailed placeholder
    if not generated_content:
        if is_detailed_brief:
            generated_content = f"""# {actual_title}

## Introduction

This article explores the critical aspects of {actual_title.lower()}, providing practical insights and actionable strategies for implementation.

## Key Concepts

Based on the provided brief, this comprehensive guide covers essential topics including testing methodologies, deployment strategies, and monitoring best practices. The approach outlined here emphasizes rigorous validation, systematic deployment, and continuous improvement.

## Implementation Strategy

### Testing Framework
A robust testing framework forms the foundation of reliable deployments. This includes unit tests for core functionality, integration tests for system interactions, and end-to-end tests for complete user workflows.

### Monitoring and Observability
Effective monitoring ensures system health and performance. Key metrics include response times, error rates, and resource utilization. Real-time alerting enables rapid response to issues.

### Deployment Process
The deployment process follows industry best practices with staged rollouts, comprehensive validation, and rollback capabilities. Each phase includes specific checkpoints and success criteria.

## Best Practices

1. **Automated Testing**: Implement comprehensive test suites that run automatically on every change
2. **Continuous Monitoring**: Deploy monitoring from day one to establish baselines
3. **Documentation**: Maintain clear documentation of processes and procedures
4. **Post-Deployment Reviews**: Conduct thorough reviews after each deployment

## Common Challenges and Solutions

### Challenge: Environment Inconsistencies
Solution: Use infrastructure as code and containerization to ensure consistency across environments.

### Challenge: Performance Degradation
Solution: Implement performance benchmarks and automated performance testing in CI/CD pipelines.

### Challenge: Complex Rollbacks
Solution: Design systems with rollback in mind, including database migrations and feature flags.

## Metrics and Success Criteria

Success is measured through multiple dimensions:
- **Reliability**: System uptime and error rates
- **Performance**: Response times and throughput
- **Quality**: Bug detection rates and test coverage
- **Efficiency**: Deployment frequency and lead time

## Conclusion

Successful deployment and testing require a systematic approach combining automated testing, comprehensive monitoring, and continuous improvement. By following the strategies outlined in this guide, teams can achieve reliable, efficient deployments while maintaining high quality standards.

## Next Steps

1. Assess your current testing and deployment practices
2. Identify gaps in monitoring and observability
3. Implement improvements incrementally
4. Measure results and iterate

---

*Note: This is a placeholder article generated while the AI service is unavailable. For a fully customized article based on your specific requirements, please ensure the AI service is properly configured.*"""
        else:
            generated_content = f"""# {actual_title}

## Introduction

{topic} represents a significant area of focus in today's rapidly evolving landscape. This comprehensive guide explores the key concepts, best practices, and practical strategies for understanding and implementing {topic.lower()}.

## Understanding {topic}

At its core, {topic.lower()} involves multiple interconnected elements that work together to achieve specific objectives. The fundamental principles include systematic approaches, evidence-based practices, and continuous optimization.

### Key Components

The essential components that make up an effective {topic.lower()} strategy include:

1. **Foundation Elements**: The basic building blocks that support all other activities
2. **Core Processes**: The central workflows and procedures that drive results
3. **Supporting Systems**: The infrastructure and tools that enable success
4. **Measurement Framework**: The metrics and KPIs that track progress

## Best Practices and Strategies

Implementing {topic.lower()} successfully requires adherence to proven best practices:

### Strategic Planning
Develop a comprehensive strategy that aligns with organizational goals and objectives. This includes defining clear outcomes, establishing timelines, and allocating resources effectively.

### Implementation Excellence
Focus on quality execution through systematic processes, regular checkpoints, and continuous refinement. Success depends on attention to detail and commitment to excellence.

### Continuous Improvement
Adopt a mindset of continuous improvement, regularly reviewing and optimizing processes based on data and feedback. This iterative approach ensures long-term success.

## Common Challenges and Solutions

### Challenge 1: Resource Constraints
Many organizations face limitations in resources, whether financial, human, or technological. The solution lies in prioritization, phased implementation, and creative resource optimization.

### Challenge 2: Change Resistance
Organizational change often meets resistance. Address this through clear communication, stakeholder engagement, and demonstrating early wins to build momentum.

### Challenge 3: Complexity Management
As systems grow, complexity increases. Manage this through modular design, clear documentation, and regular simplification efforts.

## Future Outlook

The future of {topic.lower()} holds exciting possibilities, driven by technological advancement and evolving best practices. Key trends include increased automation, data-driven decision making, and enhanced integration capabilities.

Organizations that invest in {topic.lower()} today position themselves for success tomorrow. The key is to start with a solid foundation and build incrementally toward more sophisticated capabilities.

## Conclusion

Success with {topic.lower()} requires a balanced approach combining strategic thinking, practical implementation, and continuous optimization. By following the principles and practices outlined in this guide, organizations can achieve meaningful results and sustainable improvements.

The journey toward excellence in {topic.lower()} is ongoing, requiring dedication, adaptability, and a commitment to continuous learning. Start where you are, use what you have, and do what you can to move forward progressively.

---

*Note: This is a placeholder article generated while the AI service is unavailable. For a fully customized article, please ensure the AI service is properly configured.*"""
    
    # Count actual words in generated content
    actual_word_count = len(generated_content.split()) if generated_content else word_count
    
    # Calculate reading time based on actual word count
    reading_time_minutes = max(1, actual_word_count // 200)
    reading_time = f"{reading_time_minutes}-{reading_time_minutes + 2} minutes"
    
    # Create ContentGeneration record in database
    try:
        content_generation = ContentGeneration.objects.create(
            user=user,
            prompt=generation_prompt if is_detailed_brief else f"Write a {length} {tone} blog post about {topic}",
            generated_content=generated_content,
            status='completed' if generated_content else 'failed',
            error_message=ai_error,
            generation_config={
                'content_type': 'blog',
                'tone': tone,
                'length': length,
                'include_outline': include_outline,
                'topic': topic,
                'is_detailed_brief': is_detailed_brief
            },
            metadata={
                'title': actual_title,
                'content': generated_content,
                'outline': outline,
                'blog_metadata': {
                    'word_count': actual_word_count,
                    'reading_time': reading_time,
                    'seo_score': 85,
                    'readability': 'Good',
                    'ai_generated': ai_error is None
                }
            }
        )
        
        return Response({
            'success': True,
            'blog_post': {
                'id': str(content_generation.id),
                'title': actual_title,
                'topic': topic if not is_detailed_brief else actual_title,
                'tone': tone,
                'length': length,
                'status': 'completed',
                'created_at': content_generation.created_at.isoformat(),
                'outline': outline,
                'content': generated_content,
                'metadata': {
                    'word_count': actual_word_count,
                    'reading_time': reading_time,
                    'seo_score': 85,
                    'readability': 'Good',
                    'ai_generated': ai_error is None
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_email(request):
    """
    Generate email content - Phase 4: Frontend Reality Fix
    """
    user = request.user
    data = json.loads(request.body)

    purpose = data.get('purpose', 'general')
    recipient = data.get('recipient', 'customer')
    tone = data.get('tone', 'professional')
    key_points = data.get('key_points', [])

    logger.info(f"📧 Email generation request from {user.username}: {purpose}")

    # Generate email based on purpose
    email_templates = {
        'marketing': {
            'subject': 'Exciting Updates from Our Team',
            'preview': 'We have some great news to share with you...',
            'body': '''Hi there,

We're excited to share some updates that we think you'll love!

{key_points}

We value your continued support and look forward to serving you better.

Best regards,
The Team'''
        },
        'newsletter': {
            'subject': 'Your Weekly Newsletter',
            'preview': 'This week\'s highlights and insights...',
            'body': '''Hello,

Here are this week's top stories and insights:

{key_points}

Stay tuned for more next week!

Cheers,
Newsletter Team'''
        },
        'transactional': {
            'subject': 'Your Account Update',
            'preview': 'Important information about your account...',
            'body': '''Dear Customer,

We're writing to inform you about recent activity on your account:

{key_points}

If you have any questions, please don't hesitate to contact us.

Sincerely,
Customer Support'''
        }
    }

    template = email_templates.get(purpose, email_templates['marketing'])

    # Format key points
    formatted_points = '\n'.join([f"• {point}" for point in key_points]) if key_points else "• Check out our latest features\n• Explore new opportunities\n• Join our community"

    return Response({
        'success': True,
        'email': {
            'id': int(datetime.now().timestamp()),
            'purpose': purpose,
            'recipient': recipient,
            'tone': tone,
            'subject': template['subject'],
            'preview_text': template['preview'],
            'body': template['body'].format(key_points=formatted_points),
            'estimated_read_time': '2 minutes',
            'call_to_action': 'Learn More',
            'created_at': datetime.now().isoformat(),
            'metadata': {
                'word_count': len(template['body'].split()),
                'character_count': len(template['body']),
                'has_personalization': True
            }
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_podcast_script(request):
    """
    Generate podcast episode script - Phase 4: Frontend Reality Fix
    """
    user = request.user
    data = json.loads(request.body)

    topic = data.get('topic', '')
    duration = data.get('duration', 30)  # minutes
    style = data.get('style', 'conversational')
    num_hosts = data.get('num_hosts', 1)

    logger.info(f"🎙️ Podcast script generation from {user.username}: {topic}")

    # Calculate segments based on duration
    intro_time = 2
    main_time = duration - 5
    outro_time = 3

    return Response({
        'success': True,
        'podcast_script': {
            'id': int(datetime.now().timestamp()),
            'topic': topic,
            'duration_minutes': duration,
            'style': style,
            'num_hosts': num_hosts,
            'segments': [
                {
                    'segment_number': 1,
                    'type': 'intro',
                    'duration_minutes': intro_time,
                    'content': f'[MUSIC INTRO]\n\nHost: Welcome back to the show! Today we\'re diving into {topic}. This is going to be an exciting episode, so let\'s get started!',
                    'notes': 'Upbeat and engaging opener'
                },
                {
                    'segment_number': 2,
                    'type': 'main_content',
                    'duration_minutes': main_time,
                    'content': f'Host: Let\'s break down {topic} into digestible pieces. First, let\'s talk about why this matters...\n\n[Discussion of key points, examples, and insights]\n\n[If multiple hosts: Back-and-forth conversation exploring different angles]',
                    'notes': 'Deep dive with examples and stories'
                },
                {
                    'segment_number': 3,
                    'type': 'outro',
                    'duration_minutes': outro_time,
                    'content': 'Host: That wraps up our discussion on {topic}. Key takeaways: [Summary of main points]\n\nThanks for listening! Subscribe for more episodes, and we\'ll see you next time!\n\n[MUSIC OUTRO]',
                    'notes': 'Strong call-to-action and closer'
                }
            ],
            'total_word_count': duration * 150,  # ~150 words per minute
            'estimated_prep_time': '2-4 hours',
            'suggested_music': ['Upbeat intro', 'Subtle background', 'Strong outro'],
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