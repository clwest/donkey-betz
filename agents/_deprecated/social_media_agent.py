"""
Social Media Content Creator Agent
===================================

Session 241: Created as part of agent cleanup - building real, valuable agents.

This agent specializes in platform-specific content generation:
- Knows optimal dimensions for each platform
- Suggests posting times based on engagement data
- Batch generates content for multiple platforms
- Applies platform-specific best practices

Example:
    agent = SocialMediaAgent(user=request.user)

    # Generate content for specific platform
    result = agent.create_for_platform('instagram', prompt='Product launch announcement')

    # Batch generate for all platforms
    result = agent.create_multi_platform(prompt='New feature release')

    # Get posting schedule recommendation
    result = agent.get_best_posting_times()
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class SocialMediaAgent:
    """
    Creates platform-optimized social media content.

    Handles dimensions, styles, and best practices for each platform.
    """

    # Platform specifications
    PLATFORM_SPECS = {
        'instagram_post': {
            'name': 'Instagram Post',
            'size': '1080x1080',
            'aspect_ratio': '1:1',
            'max_hashtags': 30,
            'optimal_hashtags': 11,
            'caption_limit': 2200,
            'best_times': ['9:00', '11:00', '14:00', '17:00'],
            'style_tips': ['High contrast', 'Vibrant colors', 'Clean composition'],
            'content_types': ['carousel', 'single image', 'quote graphic']
        },
        'instagram_story': {
            'name': 'Instagram Story',
            'size': '1080x1920',
            'aspect_ratio': '9:16',
            'duration': '15 seconds max per story',
            'style_tips': ['Vertical orientation', 'Bold text', 'Interactive elements'],
            'content_types': ['behind the scenes', 'polls', 'announcements']
        },
        'instagram_reel': {
            'name': 'Instagram Reel',
            'size': '1080x1920',
            'aspect_ratio': '9:16',
            'duration': '90 seconds max',
            'style_tips': ['Hook in first 3 seconds', 'Trending audio', 'Fast-paced'],
            'content_types': ['tutorials', 'transformations', 'trends']
        },
        'facebook_post': {
            'name': 'Facebook Post',
            'size': '1200x630',
            'aspect_ratio': '1.91:1',
            'caption_limit': 63206,
            'best_times': ['9:00', '13:00', '16:00'],
            'style_tips': ['Less saturated than Instagram', 'Informative', 'Shareable'],
            'content_types': ['link posts', 'photo albums', 'events']
        },
        'twitter_post': {
            'name': 'Twitter/X Post',
            'size': '1600x900',
            'aspect_ratio': '16:9',
            'caption_limit': 280,
            'max_hashtags': 2,
            'best_times': ['8:00', '12:00', '17:00'],
            'style_tips': ['High contrast text', 'Bold statements', 'Meme-friendly'],
            'content_types': ['threads', 'quotes', 'infographics']
        },
        'linkedin_post': {
            'name': 'LinkedIn Post',
            'size': '1200x627',
            'aspect_ratio': '1.91:1',
            'caption_limit': 3000,
            'max_hashtags': 5,
            'best_times': ['7:00', '10:00', '12:00'],
            'style_tips': ['Professional', 'Data-driven', 'Thought leadership'],
            'content_types': ['carousels', 'documents', 'polls']
        },
        'tiktok_post': {
            'name': 'TikTok Video',
            'size': '1080x1920',
            'aspect_ratio': '9:16',
            'duration': '3 minutes max',
            'max_hashtags': 5,
            'best_times': ['7:00', '12:00', '19:00', '22:00'],
            'style_tips': ['Trendy', 'Authentic', 'Fast hooks'],
            'content_types': ['tutorials', 'duets', 'trends', 'behind the scenes']
        },
        'youtube_thumbnail': {
            'name': 'YouTube Thumbnail',
            'size': '1280x720',
            'aspect_ratio': '16:9',
            'best_times': ['14:00', '16:00'],  # Best upload times
            'style_tips': ['Faces with expressions', 'Bold text (3-5 words)', 'High contrast', 'Curiosity gap'],
            'content_types': ['reaction faces', 'text overlays', 'before/after']
        },
        'pinterest_pin': {
            'name': 'Pinterest Pin',
            'size': '1000x1500',
            'aspect_ratio': '2:3',
            'best_times': ['20:00', '21:00'],
            'style_tips': ['Tall format', 'Text overlay', 'Lifestyle imagery'],
            'content_types': ['infographics', 'step-by-step', 'inspiration boards']
        }
    }

    # Content templates by category
    CONTENT_TEMPLATES = {
        'product_launch': {
            'hook': 'Introducing...',
            'elements': ['product image', 'key feature', 'CTA'],
            'platforms': ['instagram_post', 'facebook_post', 'twitter_post']
        },
        'behind_the_scenes': {
            'hook': 'Ever wondered...',
            'elements': ['candid shots', 'process reveal', 'team'],
            'platforms': ['instagram_story', 'tiktok_post']
        },
        'educational': {
            'hook': 'Did you know...',
            'elements': ['facts', 'statistics', 'tips'],
            'platforms': ['linkedin_post', 'twitter_post', 'youtube_thumbnail']
        },
        'testimonial': {
            'hook': 'See what our customers say...',
            'elements': ['quote', 'customer photo', 'results'],
            'platforms': ['instagram_post', 'facebook_post', 'linkedin_post']
        },
        'announcement': {
            'hook': 'Big news!',
            'elements': ['headline', 'key info', 'link'],
            'platforms': ['twitter_post', 'linkedin_post', 'facebook_post']
        }
    }

    def __init__(self, user: Optional[User] = None, project_id: Optional[str] = None):
        """
        Initialize Social Media Agent.

        Args:
            user: User context
            project_id: Optional project context
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = 'SocialMediaAgent'
        self._image_agent = None

        logger.info(f"📱 SocialMediaAgent initialized for user: {user.username if user else 'system'}")

    @property
    def image_agent(self):
        """Lazy load ImageAgent for content generation."""
        if self._image_agent is None:
            from agents.image_agent import ImageAgent
            self._image_agent = ImageAgent(user=self.user, project_id=self.project_id)
        return self._image_agent

    def create_for_platform(
        self,
        platform: str,
        prompt: str,
        style: Optional[str] = None,
        generate_image: bool = True
    ) -> Dict[str, Any]:
        """
        Create content optimized for a specific platform.

        Args:
            platform: Target platform (instagram_post, twitter_post, etc.)
            prompt: Content description
            style: Optional style preset
            generate_image: Whether to actually generate the image

        Returns:
            Platform-optimized content with image (if generated)
        """
        logger.info(f"📱 Creating content for {platform}: {prompt[:50]}...")

        if platform not in self.PLATFORM_SPECS:
            return {
                'success': False,
                'error': f"Unknown platform: {platform}. Available: {list(self.PLATFORM_SPECS.keys())}"
            }

        try:
            specs = self.PLATFORM_SPECS[platform]

            # Build platform-optimized prompt
            enhanced_prompt = self._enhance_prompt_for_platform(prompt, platform, specs)

            result = {
                'success': True,
                'platform': platform,
                'platform_name': specs['name'],
                'specs': {
                    'size': specs['size'],
                    'aspect_ratio': specs['aspect_ratio']
                },
                'enhanced_prompt': enhanced_prompt,
                'style_tips': specs.get('style_tips', []),
                'best_posting_times': specs.get('best_times', [])
            }

            # Generate image if requested
            if generate_image:
                image_result = self.image_agent.generate(
                    prompt=enhanced_prompt,
                    style=style,
                    size=specs['size']
                )

                if image_result.get('success'):
                    result['image'] = {
                        'image_id': image_result.get('image_id'),
                        'image_url': image_result.get('image_url')
                    }
                    result['message'] = f"Created {specs['name']} content successfully"
                else:
                    result['image_error'] = image_result.get('error')
                    result['message'] = "Content specs ready, but image generation failed"
            else:
                result['message'] = f"Content specs ready for {specs['name']}"

            return result

        except Exception as e:
            logger.error(f"❌ SocialMediaAgent.create_for_platform failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def create_multi_platform(
        self,
        prompt: str,
        platforms: Optional[List[str]] = None,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create content for multiple platforms at once.

        Args:
            prompt: Content description
            platforms: List of platforms (defaults to main ones)
            style: Optional style preset

        Returns:
            Content for each platform
        """
        logger.info(f"📱 Creating multi-platform content: {prompt[:50]}...")

        if platforms is None:
            # Default to most common platforms
            platforms = ['instagram_post', 'facebook_post', 'twitter_post', 'linkedin_post']

        try:
            results = []
            successful = 0

            for platform in platforms:
                result = self.create_for_platform(
                    platform=platform,
                    prompt=prompt,
                    style=style,
                    generate_image=True
                )

                results.append({
                    'platform': platform,
                    'success': result.get('success', False),
                    'image': result.get('image'),
                    'specs': result.get('specs'),
                    'error': result.get('error')
                })

                if result.get('success'):
                    successful += 1

            return {
                'success': successful > 0,
                'total_platforms': len(platforms),
                'successful': successful,
                'results': results,
                'message': f"Created content for {successful}/{len(platforms)} platforms"
            }

        except Exception as e:
            logger.error(f"❌ SocialMediaAgent.create_multi_platform failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def get_platform_specs(self, platform: Optional[str] = None) -> Dict[str, Any]:
        """
        Get specifications for a platform or all platforms.

        Args:
            platform: Optional specific platform

        Returns:
            Platform specifications
        """
        if platform:
            if platform not in self.PLATFORM_SPECS:
                return {
                    'success': False,
                    'error': f"Unknown platform: {platform}"
                }
            return {
                'success': True,
                'platform': platform,
                'specs': self.PLATFORM_SPECS[platform]
            }

        return {
            'success': True,
            'platforms': self.PLATFORM_SPECS
        }

    def get_best_posting_times(self, platform: Optional[str] = None) -> Dict[str, Any]:
        """
        Get optimal posting times.

        Args:
            platform: Optional specific platform

        Returns:
            Best posting times with explanations
        """
        logger.info(f"📱 Getting best posting times for: {platform or 'all platforms'}")

        try:
            if platform:
                if platform not in self.PLATFORM_SPECS:
                    return {
                        'success': False,
                        'error': f"Unknown platform: {platform}"
                    }

                specs = self.PLATFORM_SPECS[platform]
                return {
                    'success': True,
                    'platform': platform,
                    'best_times': specs.get('best_times', []),
                    'timezone_note': 'Times are in your local timezone',
                    'tips': [
                        'Post consistently at the same times',
                        'Test different times and track engagement',
                        'Weekdays generally perform better than weekends'
                    ]
                }

            # All platforms
            all_times = {}
            for plat, specs in self.PLATFORM_SPECS.items():
                all_times[plat] = {
                    'name': specs['name'],
                    'best_times': specs.get('best_times', [])
                }

            return {
                'success': True,
                'posting_schedule': all_times,
                'general_tips': [
                    'Best days: Tuesday, Wednesday, Thursday',
                    'Avoid posting late night (11pm-5am)',
                    'Consistency matters more than perfect timing'
                ]
            }

        except Exception as e:
            logger.error(f"❌ SocialMediaAgent.get_best_posting_times failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def suggest_content_type(self, goal: str) -> Dict[str, Any]:
        """
        Suggest content type based on marketing goal.

        Args:
            goal: Marketing goal (awareness, engagement, conversion, etc.)

        Returns:
            Content type suggestions
        """
        logger.info(f"📱 Suggesting content for goal: {goal}")

        goal_suggestions = {
            'awareness': {
                'content_types': ['infographics', 'viral content', 'trends'],
                'platforms': ['instagram_post', 'tiktok_post', 'twitter_post'],
                'tips': ['Focus on shareability', 'Use trending topics', 'Bold visuals']
            },
            'engagement': {
                'content_types': ['polls', 'questions', 'behind the scenes', 'user generated content'],
                'platforms': ['instagram_story', 'twitter_post', 'facebook_post'],
                'tips': ['Ask questions', 'Respond to comments', 'Create conversations']
            },
            'conversion': {
                'content_types': ['testimonials', 'product showcases', 'limited offers'],
                'platforms': ['instagram_post', 'facebook_post', 'pinterest_pin'],
                'tips': ['Clear CTAs', 'Social proof', 'Urgency elements']
            },
            'education': {
                'content_types': ['tutorials', 'how-tos', 'tips and tricks', 'explainers'],
                'platforms': ['youtube_thumbnail', 'linkedin_post', 'pinterest_pin'],
                'tips': ['Step-by-step format', 'Value-first approach', 'Save-worthy content']
            },
            'community': {
                'content_types': ['user spotlights', 'team introductions', 'milestones'],
                'platforms': ['instagram_story', 'linkedin_post', 'facebook_post'],
                'tips': ['Humanize your brand', 'Celebrate customers', 'Show authenticity']
            }
        }

        goal_lower = goal.lower()
        suggestion = None

        for key, value in goal_suggestions.items():
            if key in goal_lower:
                suggestion = value
                break

        if not suggestion:
            suggestion = goal_suggestions['engagement']  # Default

        return {
            'success': True,
            'goal': goal,
            'suggestions': suggestion,
            'recommended_frequency': 'Post 1-2 times per day on main platforms'
        }

    def create_content_calendar(self, days: int = 7, focus: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a content calendar for multiple platforms.

        Args:
            days: Number of days to plan
            focus: Optional focus area

        Returns:
            Content calendar with daily recommendations
        """
        logger.info(f"📱 Creating {days}-day content calendar")

        try:
            calendar = []

            # Mix of platforms across the week
            platform_rotation = [
                ['instagram_post', 'twitter_post'],
                ['linkedin_post', 'facebook_post'],
                ['instagram_story', 'tiktok_post'],
                ['twitter_post', 'youtube_thumbnail'],
                ['instagram_post', 'linkedin_post'],
                ['facebook_post', 'pinterest_pin'],
                ['instagram_story', 'twitter_post']
            ]

            content_ideas = [
                'Product/service highlight',
                'Educational tip',
                'Behind the scenes',
                'Customer testimonial',
                'Industry news reaction',
                'Team spotlight',
                'Inspirational quote'
            ]

            for i in range(days):
                date = timezone.now() + timedelta(days=i)
                day_of_week = date.weekday()

                platforms = platform_rotation[day_of_week % len(platform_rotation)]
                content_idea = content_ideas[i % len(content_ideas)]

                posts = []
                for platform in platforms:
                    specs = self.PLATFORM_SPECS.get(platform, {})
                    posts.append({
                        'platform': platform,
                        'platform_name': specs.get('name', platform),
                        'size': specs.get('size'),
                        'content_idea': content_idea,
                        'best_time': specs.get('best_times', ['10:00'])[0]
                    })

                calendar.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'day_name': date.strftime('%A'),
                    'posts': posts
                })

            return {
                'success': True,
                'calendar': calendar,
                'days_planned': days,
                'total_posts': sum(len(day['posts']) for day in calendar),
                'tips': [
                    'Batch create content on one day',
                    'Use scheduling tools',
                    'Leave room for timely content'
                ]
            }

        except Exception as e:
            logger.error(f"❌ SocialMediaAgent.create_content_calendar failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    # Private helper methods

    def _enhance_prompt_for_platform(self, prompt: str, platform: str, specs: Dict[str, Any]) -> str:
        """Enhance prompt with platform-specific requirements."""
        enhancements = []

        # Add dimension context
        if specs.get('aspect_ratio'):
            enhancements.append(f"{specs['aspect_ratio']} aspect ratio")

        # Add style tips
        if specs.get('style_tips'):
            enhancements.append(specs['style_tips'][0])

        # Platform-specific enhancements
        platform_additions = {
            'instagram_post': 'vibrant, eye-catching, Instagram-worthy',
            'instagram_story': 'vertical format, bold text, engaging',
            'twitter_post': 'bold, shareable, attention-grabbing',
            'linkedin_post': 'professional, clean, business-appropriate',
            'youtube_thumbnail': 'high contrast, bold text overlay, curiosity-inducing',
            'tiktok_post': 'trendy, dynamic, youthful energy',
            'pinterest_pin': 'inspirational, lifestyle, save-worthy',
            'facebook_post': 'engaging, informative, shareable'
        }

        if platform in platform_additions:
            enhancements.append(platform_additions[platform])

        if enhancements:
            return f"{prompt}, {', '.join(enhancements)}"

        return prompt


# Convenience function
def get_social_media_agent(user=None, project_id=None) -> SocialMediaAgent:
    """Get SocialMediaAgent instance."""
    return SocialMediaAgent(user=user, project_id=project_id)


__all__ = [
    'SocialMediaAgent',
    'get_social_media_agent'
]
