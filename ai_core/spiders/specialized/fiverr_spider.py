"""
Fiverr Spider - Freelance Gig Intelligence
==========================================

Session 534: Simplified to work with spider network interface.
Returns curated freelance categories and trending service ideas.
Fiverr has no public API/RSS, so we provide category exploration links.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class FiverrSpider:
    """Fiverr spider - freelance gig categories and service trends"""

    name = "fiverr"

    # Fiverr main categories with subcategories
    CATEGORIES = [
        # Programming & Tech
        ('Web Development', 'programming-tech/website-development', 'Website design and development services.'),
        ('Mobile App Development', 'programming-tech/mobile-app-development', 'iOS and Android app development.'),
        ('AI & Machine Learning', 'programming-tech/ai-development', 'AI models, chatbots, and ML solutions.'),
        ('Game Development', 'programming-tech/game-development', 'Unity, Unreal, and game programming.'),
        ('Data Science', 'programming-tech/data-science', 'Data analysis and visualization.'),

        # Graphics & Design
        ('Logo Design', 'graphics-design/logo-design', 'Brand logos and identity design.'),
        ('Brand Style Guides', 'graphics-design/brand-style-guides', 'Complete brand identity packages.'),
        ('Illustration', 'graphics-design/illustration', 'Custom illustrations and artwork.'),
        ('UI/UX Design', 'graphics-design/ux-design', 'User interface and experience design.'),
        ('3D Modeling', 'graphics-design/3d-design', '3D models, renders, and product visualization.'),

        # Digital Marketing
        ('Social Media Marketing', 'online-marketing/social-marketing', 'Social media management and growth.'),
        ('SEO Services', 'online-marketing/seo-services', 'Search engine optimization.'),
        ('Content Marketing', 'online-marketing/content-marketing', 'Content strategy and creation.'),
        ('Video Marketing', 'online-marketing/video-marketing', 'Video ads and promotional content.'),

        # Writing & Translation
        ('Blog Writing', 'writing-translation/blog-writing', 'Blog posts and articles.'),
        ('Copywriting', 'writing-translation/copywriting', 'Sales copy and marketing content.'),
        ('Translation', 'writing-translation/translation', 'Document and content translation.'),
        ('Resume Writing', 'writing-translation/resume-writing', 'Professional resume services.'),

        # Video & Animation
        ('Video Editing', 'video-animation/video-editing', 'Professional video editing.'),
        ('Motion Graphics', 'video-animation/motion-graphics', 'Animated graphics and intros.'),
        ('Explainer Videos', 'video-animation/explainer-videos', 'Animated explainer content.'),

        # AI Services
        ('AI Chatbots', 'ai-services/ai-chatbots', 'Custom AI chatbot development.'),
        ('AI Art', 'ai-services/ai-art', 'AI-generated artwork and images.'),
        ('AI Voice', 'ai-services/ai-voice', 'AI voice generation and cloning.'),
        ('AI Content', 'ai-services/ai-content', 'AI-assisted content creation.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch freelance service categories from Fiverr.

        Args:
            max_results: Maximum number of categories to return

        Returns:
            List of freelance category dictionaries
        """
        items = []

        for title, slug, description in self.CATEGORIES:
            items.append({
                'title': title,
                'name': title,
                'url': f'https://www.fiverr.com/categories/{slug}',
                'link': f'https://www.fiverr.com/categories/{slug}',
                'summary': description,
                'description': description,
                'category': slug.split('/')[0] if '/' in slug else slug,
                'subcategory': slug.split('/')[-1] if '/' in slug else '',
                'source': 'Fiverr',
                'data_type': 'freelance_category',
                'platform': 'fiverr',
                'tags': ['freelance', 'gigs', 'services', slug.split('/')[0]],
                'timestamp': datetime.now().isoformat(),
            })

            if len(items) >= max_results:
                break

        logger.info(f"Fiverr spider collected {len(items)} categories")
        return items[:max_results]
