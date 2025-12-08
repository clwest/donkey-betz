"""
Agent-to-Content-Studio Bridge
Enables agents to access and use the Content Creation Studio for generating content
"""

import json
import logging
from typing import Dict, Any, List, Optional
from django.contrib.auth import get_user_model
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

# Import content studio views
from core.views_content import (
    create_content,
    generate_blog_post,
    generate_social_media_post,
    generate_video_script,
    list_content
)

# Import agent models
from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution
from content.models import ContentGeneration, ContentStatus

logger = logging.getLogger(__name__)
User = get_user_model()


class ContentStudioBridge:
    """
    Bridge that allows agents to interact with the Content Creation Studio
    """

    def __init__(self, agent: UnifiedAgentTemplate = None, user: User = None):
        """
        Initialize the bridge with an agent and user context
        """
        self.agent = agent
        self.user = user or self._get_default_user()
        self.factory = APIRequestFactory()
        self.execution_record = None

    def _get_default_user(self):
        """Get or create a default system user for agent operations"""
        user, created = User.objects.get_or_create(
            username='content_agent_system',
            defaults={
                'email': 'content.agent@system.ai',
                'is_staff': False,
                'is_active': True
            }
        )
        if created:
            logger.info("Created system user for content agent operations")
        return user

    def _create_request(self, method: str, data: Dict = None) -> Request:
        """Create a mock request for the content studio views"""
        if method == 'POST':
            request = self.factory.post(
                '/api/content/',
                json.dumps(data),
                content_type='application/json'
            )
        else:
            request = self.factory.get('/api/content/')

        # Add user to request
        request.user = self.user
        return request

    def _log_execution(self, action: str, input_data: Dict, result: Dict):
        """Log the agent execution for tracking"""
        if self.agent:
            try:
                self.execution_record = AgentExecution.objects.create(
                    template=self.agent,
                    input_data={
                        'action': action,
                        'parameters': input_data
                    },
                    output_data=result,
                    status='completed' if result.get('success') else 'failed',
                    execution_metadata={
                        'bridge': 'content_studio',
                        'content_type': input_data.get('content_type', 'unknown')
                    }
                )
                logger.info(f"Logged execution {self.execution_record.id} for {self.agent.name}")
            except Exception as e:
                logger.error(f"Failed to log execution: {e}")

    def create_blog_post(
        self,
        topic: str,
        tone: str = 'professional',
        length: str = 'medium',
        include_outline: bool = True
    ) -> Dict[str, Any]:
        """
        Create a blog post using the Content Studio

        Args:
            topic: The topic or detailed brief for the blog post
            tone: The tone of the content (professional, casual, engaging, etc.)
            length: The length (short, medium, long)
            include_outline: Whether to include an outline

        Returns:
            Dictionary with the generated blog post
        """
        data = {
            'topic': topic,
            'tone': tone,
            'length': length,
            'include_outline': include_outline
        }

        request = self._create_request('POST', data)

        try:
            response = generate_blog_post(request)
            result = response.data

            # Log the execution
            self._log_execution('generate_blog_post', data, result)

            if result.get('success'):
                logger.info(f"Successfully generated blog post: {result['blog_post']['title']}")
            else:
                logger.error(f"Failed to generate blog post: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error creating blog post: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_social_media_post(
        self,
        platform: str,
        topic: str,
        tone: str = 'engaging',
        include_hashtags: bool = True
    ) -> Dict[str, Any]:
        """
        Create social media content

        Args:
            platform: The social platform (twitter, linkedin, facebook, instagram)
            topic: The topic for the post
            tone: The tone of the content
            include_hashtags: Whether to include hashtags

        Returns:
            Dictionary with the generated social post
        """
        data = {
            'platform': platform,
            'topic': topic,
            'tone': tone,
            'include_hashtags': include_hashtags
        }

        request = self._create_request('POST', data)

        try:
            response = generate_social_media_post(request)
            result = response.data

            # Log the execution
            self._log_execution('generate_social_post', data, result)

            if result.get('success'):
                logger.info(f"Successfully generated {platform} post")
            else:
                logger.error(f"Failed to generate social post: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error creating social media post: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_video_script(
        self,
        topic: str,
        duration: int = 60,
        style: str = 'educational',
        include_narration: bool = True
    ) -> Dict[str, Any]:
        """
        Create a video script

        Args:
            topic: The topic for the video
            duration: Duration in seconds
            style: The style of the video (educational, promotional, etc.)
            include_narration: Whether to include narration

        Returns:
            Dictionary with the generated video script
        """
        data = {
            'topic': topic,
            'duration': duration,
            'style': style,
            'include_narration': include_narration
        }

        request = self._create_request('POST', data)

        try:
            response = generate_video_script(request)
            result = response.data

            # Log the execution
            self._log_execution('generate_video_script', data, result)

            if result.get('success'):
                logger.info(f"Successfully generated video script for: {topic}")
            else:
                logger.error(f"Failed to generate video script: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error creating video script: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_image(
        self,
        prompt: str,
        style: str = 'realistic',
        size: str = '1024x1024',
        negative_prompt: str = '',
        batch_size: int = 1
    ) -> Dict[str, Any]:
        """
        Create images using the Content Studio

        Args:
            prompt: The image generation prompt
            style: The style of the image
            size: The size of the image
            negative_prompt: What to avoid in the image
            batch_size: Number of images to generate

        Returns:
            Dictionary with the generated images
        """
        data = {
            'content_type': 'image',
            'prompt': prompt,
            'style': style,
            'size': size,
            'negative_prompt': negative_prompt,
            'batch_size': batch_size,
            'quality': 'standard'
        }

        request = self._create_request('POST', data)

        try:
            response = create_content(request)
            result = response.data

            # Log the execution
            self._log_execution('generate_image', data, result)

            if result.get('success'):
                images = result['content'].get('images', [])
                logger.info(f"Successfully generated {len(images)} images")
            else:
                logger.error(f"Failed to generate images: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error creating images: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_content_library(self, content_type: str = 'all') -> Dict[str, Any]:
        """
        Get the user's content library

        Args:
            content_type: Filter by content type (all, image, text, etc.)

        Returns:
            Dictionary with content library items
        """
        request = self.factory.get(f'/api/content/list/?type={content_type}')
        request.user = self.user

        try:
            response = list_content(request)
            result = response.data

            if result.get('success'):
                logger.info(f"Retrieved {result['count']} content items")
            else:
                logger.error(f"Failed to get content library: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error getting content library: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_multi_format_campaign(
        self,
        campaign_topic: str,
        platforms: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create a complete multi-format content campaign

        Args:
            campaign_topic: The main topic for the campaign
            platforms: List of platforms to create content for

        Returns:
            Dictionary with all generated content
        """
        if platforms is None:
            platforms = ['blog', 'twitter', 'linkedin', 'video']

        campaign_results = {
            'success': True,
            'campaign_topic': campaign_topic,
            'content_pieces': {}
        }

        # Generate blog post
        if 'blog' in platforms:
            blog_result = self.create_blog_post(
                topic=campaign_topic,
                tone='professional',
                length='medium'
            )
            campaign_results['content_pieces']['blog'] = blog_result

        # Generate social media posts
        if 'twitter' in platforms:
            twitter_result = self.create_social_media_post(
                platform='twitter',
                topic=campaign_topic,
                tone='engaging'
            )
            campaign_results['content_pieces']['twitter'] = twitter_result

        if 'linkedin' in platforms:
            linkedin_result = self.create_social_media_post(
                platform='linkedin',
                topic=campaign_topic,
                tone='professional'
            )
            campaign_results['content_pieces']['linkedin'] = linkedin_result

        # Generate video script
        if 'video' in platforms:
            video_result = self.create_video_script(
                topic=campaign_topic,
                duration=90,
                style='educational'
            )
            campaign_results['content_pieces']['video'] = video_result

        # Generate promotional images
        if 'images' in platforms:
            image_result = self.create_image(
                prompt=f"Professional promotional image for {campaign_topic}",
                style='corporate',
                batch_size=4
            )
            campaign_results['content_pieces']['images'] = image_result

        # Log the complete campaign
        self._log_execution(
            'create_multi_format_campaign',
            {'campaign_topic': campaign_topic, 'platforms': platforms},
            campaign_results
        )

        return campaign_results


class AgentContentCreator:
    """
    High-level interface for agents to create content through the studio
    """

    @staticmethod
    def get_content_agent() -> Optional[UnifiedAgentTemplate]:
        """Get the primary content creation agent"""
        try:
            # Try to get the ai-content-studio agent first
            agent = UnifiedAgentTemplate.objects.filter(
                name='ai-content-studio'
            ).first()

            if not agent:
                # Fallback to any content agent
                agent = UnifiedAgentTemplate.objects.filter(
                    name__icontains='content'
                ).first()

            return agent

        except Exception as e:
            logger.error(f"Error getting content agent: {e}")
            return None

    @staticmethod
    def create_content_for_app(
        content_type: str,
        topic: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Main entry point for agents to create content for the app

        Args:
            content_type: Type of content (blog, social, video, image)
            topic: The topic for content creation
            **kwargs: Additional parameters for content creation

        Returns:
            Dictionary with the created content
        """
        # Get the content agent
        agent = AgentContentCreator.get_content_agent()

        if not agent:
            return {
                'success': False,
                'error': 'No content agent available'
            }

        # Create the bridge
        bridge = ContentStudioBridge(agent=agent)

        # Route to appropriate content creation method
        if content_type == 'blog':
            return bridge.create_blog_post(
                topic=topic,
                tone=kwargs.get('tone', 'professional'),
                length=kwargs.get('length', 'medium')
            )

        elif content_type == 'social':
            return bridge.create_social_media_post(
                platform=kwargs.get('platform', 'twitter'),
                topic=topic,
                tone=kwargs.get('tone', 'engaging')
            )

        elif content_type == 'video':
            return bridge.create_video_script(
                topic=topic,
                duration=kwargs.get('duration', 60),
                style=kwargs.get('style', 'educational')
            )

        elif content_type == 'image':
            return bridge.create_image(
                prompt=topic,
                style=kwargs.get('style', 'realistic'),
                size=kwargs.get('size', '1024x1024')
            )

        elif content_type == 'campaign':
            return bridge.create_multi_format_campaign(
                campaign_topic=topic,
                platforms=kwargs.get('platforms', ['blog', 'twitter', 'linkedin'])
            )

        else:
            return {
                'success': False,
                'error': f'Unknown content type: {content_type}'
            }


# Convenience functions for direct agent usage
def agent_create_blog(topic: str, **kwargs) -> Dict[str, Any]:
    """Quick function for agents to create blog posts"""
    return AgentContentCreator.create_content_for_app('blog', topic, **kwargs)


def agent_create_social(topic: str, platform: str = 'twitter', **kwargs) -> Dict[str, Any]:
    """Quick function for agents to create social media posts"""
    return AgentContentCreator.create_content_for_app(
        'social', topic, platform=platform, **kwargs
    )


def agent_create_image(prompt: str, **kwargs) -> Dict[str, Any]:
    """Quick function for agents to create images"""
    return AgentContentCreator.create_content_for_app('image', prompt, **kwargs)


def agent_create_campaign(topic: str, platforms: List[str] = None) -> Dict[str, Any]:
    """Quick function for agents to create multi-format campaigns"""
    return AgentContentCreator.create_content_for_app(
        'campaign', topic, platforms=platforms
    )