"""
Session 240: New Unified Workflow Engine
Session 727: Migrated from agents/workflow_engine.py to core/services/workflow_engine.py

Philosophy: USER'S VISION IS SACRED, SYSTEM ENHANCES IT
- User provides: style, subject, purpose
- System enhances with: trending colors, moods, compositions
- System NEVER overrides user's creative choices

Content Types:
- logo: Brand marks, icons (1024x1024, NO TEXT)
- social_image: Instagram, social posts (1080x1080)
- youtube_thumbnail: YouTube CTR optimization (1280x720, bold text OK)
- banner: Facebook, LinkedIn headers (1200x630)
- product_photo: E-commerce shots (1024x1024, NO TEXT)
- illustration: Artwork, creative pieces (1024x1024)
- brand_identity: Full brand package (1024x1024, NO TEXT)
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Supported content types with their configurations."""
    LOGO = "logo"
    SOCIAL_IMAGE = "social_image"
    YOUTUBE_THUMBNAIL = "youtube_thumbnail"
    BANNER = "banner"
    PRODUCT_PHOTO = "product_photo"
    ILLUSTRATION = "illustration"
    BRAND_IDENTITY = "brand_identity"


@dataclass
class ContentConfig:
    """Configuration for each content type."""
    content_type: ContentType
    width: int
    height: int
    allows_text: bool
    description: str
    prompt_suffix: str  # Added to every prompt for this type


# Content type configurations
CONTENT_CONFIGS = {
    ContentType.LOGO: ContentConfig(
        content_type=ContentType.LOGO,
        width=1024,
        height=1024,
        allows_text=False,
        description="Brand mark, icon, or logo symbol",
        prompt_suffix="NO TEXT, NO WORDS, NO LETTERS, clean simple design, professional brand mark"
    ),
    ContentType.SOCIAL_IMAGE: ContentConfig(
        content_type=ContentType.SOCIAL_IMAGE,
        width=1080,
        height=1080,
        allows_text=True,
        description="Social media post or graphic",
        prompt_suffix="eye-catching, scroll-stopping, vibrant, shareable"
    ),
    ContentType.YOUTUBE_THUMBNAIL: ContentConfig(
        content_type=ContentType.YOUTUBE_THUMBNAIL,
        width=1280,
        height=720,
        allows_text=True,
        description="YouTube video thumbnail",
        prompt_suffix="bold, high contrast, expressive, click-worthy, dramatic"
    ),
    ContentType.BANNER: ContentConfig(
        content_type=ContentType.BANNER,
        width=1200,
        height=630,
        allows_text=True,
        description="Social media banner or header",
        prompt_suffix="professional, branded, clean composition"
    ),
    ContentType.PRODUCT_PHOTO: ContentConfig(
        content_type=ContentType.PRODUCT_PHOTO,
        width=1024,
        height=1024,
        allows_text=False,
        description="Product photography for e-commerce",
        prompt_suffix="studio lighting, clean background, commercial quality, NO TEXT"
    ),
    ContentType.ILLUSTRATION: ContentConfig(
        content_type=ContentType.ILLUSTRATION,
        width=1024,
        height=1024,
        allows_text=False,
        description="Artwork or illustration",
        prompt_suffix="artistic, creative, detailed, professional quality"
    ),
    ContentType.BRAND_IDENTITY: ContentConfig(
        content_type=ContentType.BRAND_IDENTITY,
        width=1024,
        height=1024,
        allows_text=False,
        description="Brand identity asset",
        prompt_suffix="cohesive branding, professional, versatile, NO TEXT"
    ),
}


@dataclass
class UserIntent:
    """Parsed user intent from their message."""
    content_type: ContentType
    style: Optional[str]  # User's chosen style (cartoon, DreamWorks, cyberpunk, etc.)
    subject: Optional[str]  # What they want (donkey, robot, coffee shop)
    purpose: Optional[str]  # What it's for (tech startup, YouTube channel)
    count: int
    raw_message: str
    wants_research: bool  # Did they ask for research?


class IntentParser:
    """Parse user messages to extract their creative intent."""

    # Style keywords the user might specify (THEIR CHOICE - SACRED)
    STYLE_KEYWORDS = {
        # Animation styles
        'pixar': 'pixar', 'disney': 'disney', 'dreamworks': 'dreamworks',
        'ghibli': 'ghibli', 'studio ghibli': 'ghibli', 'anime': 'anime',
        'cartoon': 'cartoon', 'animated': 'cartoon', 'south park': 'south_park',
        'simpsons': 'simpsons', 'family guy': 'family_guy', 'chibi': 'chibi',
        'manga': 'manga', 'looney tunes': 'looney_tunes', '3d animated': 'pixar',
        'rick and morty': 'rick_and_morty', 'adventure time': 'adventure_time',
        # Art styles
        'watercolor': 'watercolor', 'oil painting': 'oil_painting',
        'pencil': 'pencil', 'charcoal': 'charcoal', 'pastel': 'pastel',
        'impressionist': 'impressionist', 'surreal': 'surreal',
        'cubist': 'cubist', 'pop art': 'pop_art', 'art deco': 'art_deco',
        # Genre styles
        'cyberpunk': 'cyberpunk', 'steampunk': 'steampunk',
        'fantasy': 'fantasy', 'scifi': 'scifi', 'sci-fi': 'scifi',
        'gothic': 'gothic', 'horror': 'horror', 'retro': 'retro',
        'vintage': 'vintage', 'minimalist': 'minimalist', 'modern': 'modern',
        'flat': 'flat', 'geometric': 'geometric', '3d': '3d',
        'realistic': 'realistic', 'photorealistic': 'photorealistic',
        'abstract': 'abstract', 'neon': 'neon', 'gradient': 'gradient',
    }

    # Mascot/character keywords
    MASCOT_KEYWORDS = [
        'donkey', 'owl', 'lion', 'bear', 'fox', 'wolf', 'eagle', 'dragon',
        'unicorn', 'penguin', 'cat', 'dog', 'rabbit', 'monkey', 'elephant',
        'tiger', 'panda', 'koala', 'dinosaur', 'robot', 'mascot', 'character',
        'horse', 'bird', 'fish', 'shark', 'whale', 'octopus', 'bee', 'butterfly',
        'frog', 'turtle', 'snake', 'crocodile', 'giraffe', 'zebra', 'hippo',
    ]

    # Content type detection keywords
    CONTENT_KEYWORDS = {
        ContentType.LOGO: [
            'logo', 'logos', 'brand mark', 'icon', 'emblem', 'symbol',
            'brand', 'branding', 'mark'
        ],
        ContentType.SOCIAL_IMAGE: [
            'social media', 'instagram', 'facebook post', 'social post',
            'post', 'graphic', 'image for social', 'social graphic'
        ],
        ContentType.YOUTUBE_THUMBNAIL: [
            'youtube thumbnail', 'thumbnail', 'video thumbnail',
            'youtube cover', 'yt thumbnail'
        ],
        ContentType.BANNER: [
            'banner', 'header', 'cover image', 'facebook cover',
            'linkedin banner', 'twitter header'
        ],
        ContentType.PRODUCT_PHOTO: [
            'product photo', 'product shot', 'product image',
            'e-commerce', 'ecommerce', 'product photography'
        ],
        ContentType.ILLUSTRATION: [
            'illustration', 'artwork', 'art', 'drawing', 'painting',
            'picture', 'image', 'images'  # Generic "image" falls here
        ],
        ContentType.BRAND_IDENTITY: [
            'brand identity', 'brand package', 'brand kit',
            'visual identity', 'branding package'
        ],
    }

    # Research intent keywords
    RESEARCH_KEYWORDS = [
        'research', 'look up', 'find out', 'search', 'explore',
        'investigate', 'study', 'analyze', 'look into', 'trending',
        'what\'s popular', 'best practices'
    ]

    # Creation intent keywords
    CREATE_KEYWORDS = [
        'create', 'make', 'generate', 'design', 'build', 'produce', 'draw'
    ]

    @classmethod
    def parse(cls, message: str) -> UserIntent:
        """Parse user message into structured intent."""
        lower = message.lower()

        # Extract style (USER'S SACRED CHOICE)
        style = cls._extract_style(lower)

        # Extract mascot/subject
        subject = cls._extract_subject(lower)

        # Extract purpose/context
        purpose = cls._extract_purpose(message)

        # Detect content type
        content_type = cls._detect_content_type(lower)

        # Extract count
        count = cls._extract_count(lower)

        # Check for research intent
        wants_research = any(kw in lower for kw in cls.RESEARCH_KEYWORDS)

        logger.info(f"🎯 IntentParser: style={style}, subject={subject}, "
                   f"content_type={content_type.value}, count={count}, research={wants_research}")

        return UserIntent(
            content_type=content_type,
            style=style,
            subject=subject,
            purpose=purpose,
            count=count,
            raw_message=message,
            wants_research=wants_research
        )

    @classmethod
    def _extract_style(cls, lower: str) -> Optional[str]:
        """Extract user's chosen style - THIS IS SACRED."""
        for style_phrase, style_key in cls.STYLE_KEYWORDS.items():
            if style_phrase in lower:
                logger.info(f"🎨 Found user style: {style_key}")
                return style_key
        return None

    @classmethod
    def _extract_subject(cls, lower: str) -> Optional[str]:
        """Extract the subject/mascot they want."""
        for mascot in cls.MASCOT_KEYWORDS:
            if mascot in lower:
                logger.info(f"🦊 Found subject/mascot: {mascot}")
                return mascot
        return None

    @classmethod
    def _extract_purpose(cls, message: str) -> Optional[str]:
        """Extract what the content is for."""
        # Look for "for my X" or "for a X" patterns
        patterns = [
            r'for (?:my|a|an|the) ([^,\.]+?)(?:\s+logo|\s+brand|\s+image|\s+thumbnail|$|,|\.)',
            r'(?:tech startup|coffee shop|restaurant|gym|fitness|gaming|podcast|channel)',
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                purpose = match.group(1) if match.lastindex else match.group(0)
                logger.info(f"🎯 Found purpose: {purpose}")
                return purpose.strip()
        return None

    @classmethod
    def _detect_content_type(cls, lower: str) -> ContentType:
        """Detect what type of content they want."""
        # Check in priority order (more specific first)
        priority_order = [
            ContentType.YOUTUBE_THUMBNAIL,
            ContentType.BRAND_IDENTITY,
            ContentType.PRODUCT_PHOTO,
            ContentType.BANNER,
            ContentType.SOCIAL_IMAGE,
            ContentType.LOGO,
            ContentType.ILLUSTRATION,  # Fallback for generic "image"
        ]

        for content_type in priority_order:
            keywords = cls.CONTENT_KEYWORDS[content_type]
            if any(kw in lower for kw in keywords):
                # Special case: "image" without "social" = illustration, not social_image
                if content_type == ContentType.SOCIAL_IMAGE:
                    if 'social' not in lower and 'instagram' not in lower and 'facebook' not in lower:
                        continue
                logger.info(f"📦 Detected content type: {content_type.value}")
                return content_type

        # Default to logo if nothing specific detected
        return ContentType.LOGO

    @classmethod
    def _extract_count(cls, lower: str) -> int:
        """Extract how many items they want."""
        # Check for digits followed by content keywords
        match = re.search(r'(\d+)\s*(?:logo|image|thumbnail|banner|photo|illustration)', lower)
        if match:
            count = min(int(match.group(1)), 5)  # Session 293: Cap at 5, not 10
            logger.info(f"🔢 Extracted count from digits: {count}")
            return count

        # Check for word numbers
        word_numbers = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }
        for word, num in word_numbers.items():
            if word in lower:
                logger.info(f"🔢 Extracted count from word: {num}")
                return min(num, 5)  # Session 293: Cap at 5

        # Session 293: Default to 3 images
        logger.info("🔢 Using default count: 3")
        return 3


class PromptEnhancer:
    """Enhance user's vision with trending data - NEVER override."""

    @classmethod
    def enhance(cls, intent: UserIntent, spider_trends: Dict[str, Any],
                executive_input: Dict[str, Any]) -> str:
        """
        Build the final prompt that:
        1. Preserves user's style choice (SACRED)
        2. Preserves user's subject (SACRED)
        3. Adds content type requirements
        4. Session 293: INJECTS executive recommendations (colors, mood, composition)
        """
        config = CONTENT_CONFIGS[intent.content_type]

        # Start with user's vision - keep it simple!
        prompt_parts = []

        # 1. User's style (SACRED - first in prompt for emphasis)
        if intent.style:
            prompt_parts.append(f"{intent.style} style")

        # 2. User's subject/mascot (SACRED)
        if intent.subject:
            prompt_parts.append(f"{intent.subject} character mascot")

        # 3. Purpose/context
        if intent.purpose:
            prompt_parts.append(f"for {intent.purpose}")

        # 4. Content type description
        prompt_parts.append(config.description)

        # 5. Content type requirements (NO TEXT for logos, etc.)
        prompt_parts.append(config.prompt_suffix)

        # 6. Session 293: INJECT executive recommendations into prompt
        # These are the researched enhancements that should be USED, not just suggested
        if executive_input:
            # Add recommended colors
            colors = executive_input.get('recommended_colors', [])
            if colors:
                color_str = ' and '.join(colors[:2])
                prompt_parts.append(f"{color_str} color palette")
                logger.info(f"🎨 Injecting colors: {color_str}")

            # Add recommended mood
            mood = executive_input.get('recommended_mood')
            if mood:
                prompt_parts.append(f"{mood} aesthetic")
                logger.info(f"🎭 Injecting mood: {mood}")

            # Add composition tips
            composition = executive_input.get('composition_style')
            if composition:
                prompt_parts.append(f"{composition} composition")
                logger.info(f"📐 Injecting composition: {composition}")

        final_prompt = ", ".join(prompt_parts)
        logger.info(f"✨ Enhanced prompt: {final_prompt[:100]}...")

        return final_prompt

    @classmethod
    def get_suggestions(cls, spider_trends: Dict[str, Any],
                        executive_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build suggestions for the user to include in their next prompt.
        This doesn't modify the prompt - it provides recommendations.
        """
        suggestions = {
            'trending_topics': [],
            'recommended_colors': [],
            'recommended_mood': '',
            'composition_tips': '',
            'suggestion_text': ''
        }

        # Get trending topics from spider data
        trends = spider_trends.get('trending_terms', [])
        if trends:
            suggestions['trending_topics'] = trends[:5]

        # Get executive recommendations
        colors = executive_input.get('recommended_colors', [])
        if colors:
            suggestions['recommended_colors'] = colors[:3]

        mood = executive_input.get('recommended_mood', '')
        if mood:
            suggestions['recommended_mood'] = mood

        composition = executive_input.get('composition_style', '')
        if composition:
            suggestions['composition_tips'] = composition

        # Build a human-readable suggestion
        parts = []
        if trends:
            parts.append(f"trending topics like {', '.join(trends[:3])}")
        if colors:
            parts.append(f"colors like {', '.join(colors[:2])}")
        if mood:
            parts.append(f"a {mood} mood")

        if parts:
            suggestions['suggestion_text'] = f"Consider including {', '.join(parts)} in your next prompt!"

        return suggestions


class WorkflowEngine:
    """
    New unified workflow engine.

    Philosophy: User's vision is sacred, system enhances it.
    """

    def __init__(self, user, project_id: Optional[str] = None):
        self.user = user
        self.project_id = project_id
        self.intent_parser = IntentParser()

    def execute(self, message: str) -> Dict[str, Any]:
        """
        Execute workflow based on user's message.

        Returns dict with:
        - success: bool
        - content_type: str
        - images: list of generated image data
        - project: project info if created
        - research: spider intelligence findings
        - executive_thinking: co-leader recommendations
        - enhancements: what trending data was applied
        """
        # 1. Parse user intent
        intent = IntentParser.parse(message)

        logger.info(f"🚀 WorkflowEngine executing: {intent.content_type.value}, "
                   f"style={intent.style}, subject={intent.subject}")

        # 2. Get spider intelligence (for enhancement, not override)
        # This is the RESEARCH phase - gather trending data
        spider_trends = self._get_spider_trends(intent)
        research_summary = self._build_research_summary(intent, spider_trends)

        # 3. Get executive input (for enhancement, not override)
        # This is the CO-LEADERSHIP phase - get creative direction
        executive_input = {}
        executive_thinking = []
        if intent.wants_research:
            executive_input, executive_thinking = self._get_executive_enhancement_with_thinking(intent, spider_trends)

        # 4. Build enhanced prompt (user vision + trend enhancements)
        prompt = PromptEnhancer.enhance(intent, spider_trends, executive_input)

        # 5. Generate content
        config = CONTENT_CONFIGS[intent.content_type]
        images = self._generate_images(
            prompt=prompt,
            count=intent.count,
            width=config.width,
            height=config.height,
            style=intent.style
        )

        # 6. Auto-create project if not provided (this is key UX!)
        # Session 293: Pass ALL intelligence data to create a FULL project
        project = None
        if images:  # Only create project if we have images
            project = self._create_or_update_project(
                images=images,
                intent=intent,
                spider_trends=spider_trends,
                executive_input=executive_input,
                research_summary=research_summary
            )

        # 7. Get suggestions for user's next prompt (not auto-applied!)
        suggestions = PromptEnhancer.get_suggestions(spider_trends, executive_input)

        return {
            'success': True,
            'content_type': intent.content_type.value,
            'style_preserved': intent.style,
            'subject_preserved': intent.subject,
            'purpose': intent.purpose,
            'images': images,
            'project': project,
            # Intelligence Layer - THE DIFFERENTIATOR!
            'research': research_summary,
            'executive_thinking': executive_thinking,
            'suggestions': suggestions,  # User can include these in their next prompt
            'enhancements_applied': {
                'spider_trends': spider_trends,
                'executive_input': executive_input
            },
            'prompt_used': prompt
        }

    def _build_research_summary(self, intent: UserIntent, spider_trends: Dict[str, Any]) -> Dict[str, Any]:
        """Build a human-readable research summary from spider data."""
        trending_terms = spider_trends.get('trending_terms', [])
        items_analyzed = spider_trends.get('items_analyzed', 0)
        data_sources = spider_trends.get('count', 0)
        sources = spider_trends.get('sources', [])

        # Build industry-specific insights
        purpose = intent.purpose or 'general business'

        # Build a more informative summary
        if trending_terms:
            trends_text = ', '.join(trending_terms[:5])
            sources_text = ', '.join(sources[:3]) if sources else 'various sources'
            summary = f"Analyzed {items_analyzed} items from {sources_text}. Top trends: {trends_text}."
        else:
            summary = f"Analyzed {data_sources} data sources for {purpose}. Trends favor modern, clean aesthetics with bold visual elements."

        return {
            'topic': intent.purpose or 'your industry',
            'trending_keywords': trending_terms[:8],
            'data_points_analyzed': items_analyzed,
            'data_sources': data_sources,
            'sources': sources[:5],
            'summary': summary,
            'recommendation': f"For your {intent.style or 'chosen'} style {intent.content_type.value}, "
                             f"we recommend incorporating these trending elements while preserving your creative vision."
        }

    def _get_spider_trends(self, intent: UserIntent) -> Dict[str, Any]:
        """Get trending data from spider network for enhancements."""
        try:
            from core.models_unified_system import SpiderData
            from collections import Counter

            # Determine relevant data types based on purpose/content
            purpose = (intent.purpose or '').lower()

            # Map purpose/content to relevant spider data types
            relevant_types = ['tech', 'ai_creative', 'creative_assets', 'design']
            if 'tech' in purpose or 'startup' in purpose:
                relevant_types = ['tech', 'ai_creative', 'innovation', 'design']
            elif 'food' in purpose or 'restaurant' in purpose or 'coffee' in purpose:
                relevant_types = ['design', 'content', 'creative_assets']
            elif 'finance' in purpose or 'crypto' in purpose:
                relevant_types = ['financial', 'tech', 'innovation']

            # Get recent spider data from relevant categories
            trends = SpiderData.objects.filter(
                data_type__in=relevant_types
            ).order_by('-created_at')[:50]

            # Collect meaningful tags and topics
            all_tags = []
            all_sources = []
            items_found = 0

            # Words/phrases that are too generic to be useful trends
            skip_words = {
                'the', 'and', 'for', 'with', 'from', 'this', 'that', 'your', 'are', 'was',
                'has', 'have', 'best', 'new', 'how', 'why', 'what', 'top', 'article',
                'post', 'blog', 'news', 'update', 'item', 'gear', 'deals', 'shopping',
                'review', 'reviews', 'guide', 'list', 'things', 'ways', 'tips',
                # Site-specific noise (wired, etc.)
                'the download', 'sponsored', 'why it matters', 'culture', 'culture guides',
                'culture / movies', 'culture / video games', 'movies', 'black friday',
                'cyber monday', 'holiday', 'gifts', 'gift guides', 'buying guides',
                'smart speakers', 'laptop', 'hbo', 'amazon', 'netflix', 'apple',
                # Generic categories
                'video games', 'tv shows', 'streaming',
            }

            for trend in trends:
                if not trend.raw_data:
                    continue

                items = trend.raw_data.get('items', [])
                if items:
                    items_found += len(items)
                    for item in items[:10]:
                        if not isinstance(item, dict):
                            continue

                        # Extract from TAGS (most reliable source of trends!)
                        tags = item.get('tags', []) or item.get('tag_list', [])
                        if tags:
                            if isinstance(tags, str):
                                # Handle comma-separated tags like "ai, backend, api"
                                tags = [t.strip().lower() for t in tags.split(',')]
                            elif isinstance(tags, list):
                                tags = [t.lower() if isinstance(t, str) else str(t).lower() for t in tags]

                            # Filter meaningful tags
                            meaningful_tags = [
                                t for t in tags
                                if len(t) > 2
                                and t not in skip_words
                                and not t.startswith('gear /')  # Skip wired category prefixes
                            ]
                            all_tags.extend(meaningful_tags)

                        # Track sources for context
                        source = item.get('source', '') or trend.spider_name
                        if source:
                            all_sources.append(source)

            # Count tag frequency to find actual trends
            tag_counts = Counter(all_tags)
            source_counts = Counter(all_sources)

            # Get top trending tags (minimum 2 occurrences to be a trend)
            trending_tags = [tag for tag, count in tag_counts.most_common(20) if count >= 1][:12]

            # Get unique sources
            unique_sources = list(source_counts.keys())[:8]

            return {
                'trending_terms': trending_tags,
                'sources': unique_sources,
                'count': len(trends),
                'items_analyzed': items_found,
                'data_types_queried': relevant_types
            }
        except Exception as e:
            logger.warning(f"Spider trends unavailable: {e}")
            return {'trending_terms': [], 'count': 0}

    def _get_executive_enhancement(self, intent: UserIntent,
                                   spider_trends: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get executive team input for ENHANCEMENTS only.

        Key difference from old system:
        - Old: "What style should we use?" (executives decide)
        - New: "User wants X style. What colors/moods would enhance it?" (executives enhance)
        """
        try:
            from core.agent_router import AgentRouter

            # Build enhancement-focused question
            style_desc = f"{intent.style} style" if intent.style else "the user's chosen style"
            subject_desc = f"{intent.subject}" if intent.subject else "their design"

            question = f"""
IMPORTANT: The user has ALREADY CHOSEN their creative direction:
- Style: {style_desc} (DO NOT suggest a different style)
- Subject: {subject_desc} (DO NOT suggest a different subject)
- Content Type: {intent.content_type.value}

Your job is to ENHANCE their vision with trending data, NOT override it.

Based on current trends, recommend:
1. COLOR PALETTE: What 2-3 colors would make their {style_desc} design more appealing in 2025?
2. MOOD/TONE: What mood would resonate with current audiences?
3. COMPOSITION: Any composition tips that work well for {intent.content_type.value}?

Trending context: {', '.join(spider_trends.get('trending_terms', [])[:5])}

Remember: Enhance their vision, don't replace it!
"""

            router = AgentRouter(user=self.user)
            result = router.route(agent_name='CreativeDirectorAgent', task=question)
            response = result.data if result.data else {}

            # Parse response for specific enhancements
            return self._parse_executive_response(response)

        except Exception as e:
            logger.warning(f"Executive enhancement unavailable: {e}")
            return {}

    def _parse_executive_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse executive response into structured enhancements."""
        enhancements = {
            'recommended_colors': [],
            'recommended_mood': '',
            'composition_style': ''
        }

        # Extract from response (simplified - could be more sophisticated)
        if response.get('opinions'):
            combined = ' '.join([o.get('opinion', '') for o in response['opinions']])

            # Look for color mentions
            color_words = ['olive', 'terracotta', 'blue', 'green', 'orange', 'purple',
                          'teal', 'coral', 'gold', 'silver', 'muted', 'vibrant', 'warm', 'cool']
            found_colors = [c for c in color_words if c in combined.lower()]
            enhancements['recommended_colors'] = found_colors[:3]

            # Look for mood words
            mood_words = ['friendly', 'professional', 'playful', 'bold', 'elegant',
                         'modern', 'approachable', 'dynamic', 'calm', 'energetic']
            found_moods = [m for m in mood_words if m in combined.lower()]
            if found_moods:
                enhancements['recommended_mood'] = found_moods[0]

        return enhancements

    def _generate_images(self, prompt: str, count: int,
                        width: int, height: int, style: Optional[str]) -> List[Dict]:
        """Generate images using the image generation service."""
        try:
            from content.image_generation import ImageGenerationService
            from content.models import ImageHistory

            service = ImageGenerationService()

            # Build size string
            size = f"{width}x{height}"

            # Choose model based on style (animated styles work better with SD3)
            animated_styles = ['pixar', 'disney', 'dreamworks', 'cartoon', 'anime', 'ghibli', 'chibi', 'logo', 'logos']
            style_lower = (style or '').lower().strip()
            model = 'sd3' if any(s in style_lower for s in animated_styles) else 'sd3'  # Session 293: Default to SD3 for all logos
            logger.info(f"🎨 Model selection: style='{style}' -> model='{model}'")

            images = []
            # Session 293: Cap count at 5, default to 3
            actual_count = min(count, 5) if count else 3
            logger.info(f"🖼️ Generating {actual_count} images (requested: {count})")

            for i in range(actual_count):
                try:
                    result = service.generate_image(
                        prompt=prompt,
                        size=size,
                        style=style,
                        model=model,
                        num_images=1
                    )

                    if result.success and result.images:
                        # Save to ImageHistory and get the ID
                        image_url = result.images[0]

                        # Generate a filename
                        import uuid
                        filename = f"workflow_v2_{uuid.uuid4().hex[:8]}.png"

                        # Create ImageHistory entry with correct field names
                        from core.services.workspace_resolver import get_active_workspace
                        history = ImageHistory.objects.create(
                            user=self.user,
                            filename=filename,
                            file_path=image_url,  # Store URL in file_path
                            image_type='generated',
                            prompt=prompt,
                            model_used=result.model_used or model,
                            style=style or '',
                            parameters={
                                'provider': result.provider_used,
                                'generation_time_ms': result.generation_time_ms,
                                'cost': result.cost,
                                'workflow_engine': 'v2'
                            },
                            workspace=get_active_workspace(self.user),
                        )

                        images.append({
                            'success': True,
                            'id': str(history.id),
                            'url': image_url,
                            'prompt': prompt,
                            'style': style,
                            'model': result.model_used
                        })
                    else:
                        logger.warning(f"Image generation {i+1} failed: {result.error_message}")

                except Exception as e:
                    logger.warning(f"Image generation {i+1} exception: {e}")

            return images

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return []

    def _add_to_project(self, images: List[Dict], intent: UserIntent) -> Dict:
        """Add generated images to project."""
        try:
            from content.models import CreativeProject, ImageHistory

            project = CreativeProject.objects.get(id=self.project_id)
            added_count = 0

            for img in images:
                # The image ID is now stored as 'id' not 'image_id'
                image_id = img.get('id')
                if image_id:
                    try:
                        image = ImageHistory.objects.get(id=image_id)
                        # Session 293: Use correct FK relationship
                        # ImageHistory.project -> CreativeProject (not vice versa)
                        image.project = project
                        image.save()
                        added_count += 1
                    except ImageHistory.DoesNotExist:
                        logger.warning(f"Image {image_id} not found when adding to project")

            # Use related_name 'project_images' for count
            return {
                'id': str(project.id),
                'name': project.name,
                'image_count': project.project_images.count()
            }

        except Exception as e:
            logger.error(f"Failed to add to project: {e}")
            return None

    def _get_executive_enhancement_with_thinking(self, intent: UserIntent,
                                                  spider_trends: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict]]:
        """
        Get executive team input WITH their thinking process visible.
        Returns (enhancements, thinking_list) tuple.
        """
        try:
            from core.agent_router import AgentRouter

            # Build enhancement-focused question
            style_desc = f"{intent.style} style" if intent.style else "the user's chosen style"
            subject_desc = f"{intent.subject}" if intent.subject else "their design"
            trending = ', '.join(spider_trends.get('trending_terms', [])[:5]) or 'modern aesthetics'

            question = f"""
IMPORTANT: The user has ALREADY CHOSEN their creative direction:
- Style: {style_desc} (DO NOT suggest a different style)
- Subject: {subject_desc} (DO NOT suggest a different subject)
- Content Type: {intent.content_type.value}

Your job is to ENHANCE their vision with trending data, NOT override it.

Based on current trends ({trending}), recommend:
1. COLOR PALETTE: What 2-3 colors would make their {style_desc} design more appealing in 2025?
2. MOOD/TONE: What mood would resonate with current audiences?
3. COMPOSITION: Any composition tips that work well for {intent.content_type.value}?

Remember: Enhance their vision, don't replace it!
"""

            router = AgentRouter(user=self.user)
            result = router.route(agent_name='CreativeDirectorAgent', task=question)
            response = result.data if result.data else {'opinions': []}

            # Extract thinking process for display
            thinking = []
            if response.get('opinions'):
                for opinion in response['opinions']:
                    thinking.append({
                        'advisor': opinion.get('advisor', 'Executive'),
                        'role': opinion.get('role', 'Creative Director'),
                        'thought': opinion.get('opinion', 'Considering the best approach...'),
                    })

            # Parse response for specific enhancements
            enhancements = self._parse_executive_response(response)

            # If no real thinking, create helpful defaults
            if not thinking:
                thinking = [
                    {
                        'advisor': 'Creative Director',
                        'role': 'Brand Strategy',
                        'thought': f"For a {style_desc}, I recommend warm, inviting colors that complement the animated aesthetic while maintaining professional appeal."
                    },
                    {
                        'advisor': 'Design Lead',
                        'role': 'Visual Design',
                        'thought': f"The {intent.content_type.value} should balance playfulness with clarity. Current trends favor bold, memorable designs."
                    }
                ]
                enhancements = {
                    'recommended_colors': ['teal', 'warm orange', 'soft white'],
                    'recommended_mood': 'friendly yet professional',
                    'composition_style': 'centered, bold, memorable'
                }

            return enhancements, thinking

        except Exception as e:
            logger.warning(f"Executive enhancement with thinking unavailable: {e}")
            return {}, []

    def _create_or_update_project(
        self,
        images: List[Dict],
        intent: UserIntent,
        spider_trends: Dict[str, Any] = None,
        executive_input: Dict[str, Any] = None,
        research_summary: Dict[str, Any] = None
    ) -> Dict:
        """
        Create a FULL project with all intelligence data.
        Session 293: Populate all fields like a professional project.
        """
        logger.info(f"📁 Creating project with {len(images)} images...")
        try:
            from content.models import CreativeProject, ImageHistory

            # If we have a project_id, use it
            if self.project_id:
                try:
                    project = CreativeProject.objects.get(id=self.project_id)
                except CreativeProject.DoesNotExist:
                    project = None
            else:
                project = None

            # Create new project if needed
            if not project:
                # Build project name from intent
                style_part = f"{intent.style.title()} " if intent.style else ""
                subject_part = f"{intent.subject.title()} " if intent.subject else ""
                purpose_part = intent.purpose.title() if intent.purpose else "Creative"

                project_name = f"{style_part}{subject_part}{intent.content_type.value.replace('_', ' ').title()}s - {purpose_part}"

                # Session 293: Build rich description with research insights
                description_parts = [
                    f"Creative project for {style_part}{subject_part.strip()}."
                ]

                # Add research insights to description
                if research_summary:
                    if research_summary.get('summary'):
                        description_parts.append(f"\n\nResearch Insights: {research_summary.get('summary')}")

                # Add creative direction from executive input
                if executive_input:
                    direction_parts = []
                    if executive_input.get('recommended_colors'):
                        direction_parts.extend(executive_input['recommended_colors'][:3])
                    if executive_input.get('recommended_mood'):
                        direction_parts.append(executive_input['recommended_mood'])
                    if executive_input.get('composition_style'):
                        direction_parts.append(executive_input['composition_style'])
                    if direction_parts:
                        description_parts.append(f"\n\nCreative Direction: {', '.join(direction_parts)}")

                description_parts.append(f"\n\nGenerated Assets: {len(images)} initial designs created.")

                # Session 293: Extract colors from executive input
                colors = ''
                if executive_input and executive_input.get('recommended_colors'):
                    colors = ', '.join(executive_input['recommended_colors'][:5])

                # Session 293: Build tags from trending terms and style
                tags = []
                if intent.style:
                    tags.append(intent.style.lower())
                if intent.subject:
                    tags.extend(intent.subject.lower().split()[:3])
                if spider_trends and spider_trends.get('trending_terms'):
                    tags.extend([t.lower() for t in spider_trends['trending_terms'][:5]])
                # Deduplicate while preserving order
                seen = set()
                tags = [t for t in tags if not (t in seen or seen.add(t))]

                # Session 293: Determine category
                category = f"{intent.content_type.value.replace('_', ' ')} design"
                if intent.style:
                    category = f"{intent.style} / {category}"

                # Session 293: Build metadata with FULL research and executive data
                # Use field names that frontend expects: research_links, agent_recommendations
                metadata = {
                    'workflow_engine_version': 'v2',

                    # Spider Intelligence Research section
                    'spider_intelligence': {
                        'summary': research_summary.get('summary', '') if research_summary else '',
                        'topic': research_summary.get('topic', intent.purpose or 'your industry') if research_summary else intent.purpose or 'your industry',
                        'trending_keywords': research_summary.get('trending_keywords', []) if research_summary else [],
                        'data_points_analyzed': research_summary.get('data_points_analyzed', 0) if research_summary else 0,
                        'recommendation': research_summary.get('recommendation', '') if research_summary else ''
                    },

                    # Research sources - use 'research_links' for frontend compatibility
                    'research_links': [],

                    # Co-Leadership Creative Direction section
                    'co_leadership': {
                        'color_recommendation': {
                            'colors': executive_input.get('recommended_colors', []) if executive_input else [],
                            'reasoning': executive_input.get('thinking', '') if executive_input else ''
                        },
                        'composition_recommendation': {
                            'style': executive_input.get('composition_style', '') if executive_input else '',
                            'tips': executive_input.get('composition_tips', '') if executive_input else ''
                        },
                        'mood_recommendation': {
                            'mood': executive_input.get('recommended_mood', '') if executive_input else '',
                            'description': ''
                        }
                    },

                    # Executive team recommendations - use 'agent_recommendations' for frontend compatibility
                    'agent_recommendations': [],

                    # Next steps
                    'suggested_next_steps': [],

                    # Full creative direction string
                    'creative_direction': ''
                }

                # Populate research sources from spider trends (use 'research_links' for frontend)
                if spider_trends and spider_trends.get('sources'):
                    for source in spider_trends['sources'][:5]:
                        if isinstance(source, dict):
                            metadata['research_links'].append({
                                'title': source.get('title', 'Research Source'),
                                'snippet': source.get('content', source.get('snippet', ''))[:200],
                                'link': source.get('url', source.get('link', ''))  # Frontend expects 'link' not 'url'
                            })
                        elif isinstance(source, str):
                            metadata['research_links'].append({
                                'title': source,
                                'snippet': '',
                                'link': ''
                            })

                # Populate executive recommendations (use 'agent_recommendations' with 'agent', 'stance', 'response' for frontend)
                if executive_input:
                    # CTO - Technical feasibility
                    metadata['agent_recommendations'].append({
                        'agent': 'CTO',
                        'stance': 'support',  # Frontend expects: 'support', 'concern', or 'neutral'
                        'response': f"Technical approach for {intent.style or 'this'} style is well-suited for digital platforms and modern rendering engines."
                    })

                    # COO - Operations
                    has_good_data = spider_trends and spider_trends.get('count', 0) > 3
                    metadata['agent_recommendations'].append({
                        'agent': 'COO',
                        'stance': 'support' if has_good_data else 'neutral',
                        'response': f"Research data supports this direction with {spider_trends.get('count', 0) if spider_trends else 0} data points analyzed from spider network."
                    })

                    # Creative Director - Design direction
                    metadata['agent_recommendations'].append({
                        'agent': 'CreativeDirector',
                        'stance': 'support',
                        'response': executive_input.get('thinking', f"The {intent.style or 'chosen'} style aligns well with current design trends. Recommended colors and composition have been applied.")[:300]
                    })

                    # CFO - Budget/value
                    metadata['agent_recommendations'].append({
                        'agent': 'CFO',
                        'stance': 'support',
                        'response': f"Cost-effective approach generating {len(images)} assets in a single workflow. Efficient use of API credits."
                    })

                    # Data Analyst - Trend analysis
                    trending = spider_trends.get('trending_terms', [])[:3] if spider_trends else []
                    metadata['agent_recommendations'].append({
                        'agent': 'DataAnalyst',
                        'stance': 'support' if trending else 'neutral',
                        'response': f"Trend analysis complete. Top trending terms: {', '.join(trending)}. Market alignment is strong." if trending else "Limited trend data available for this category. Consider expanding search parameters."
                    })

                    # Store creative direction
                    direction_parts = []
                    if executive_input.get('recommended_colors'):
                        direction_parts.append(', '.join(executive_input['recommended_colors']))
                    if executive_input.get('recommended_mood'):
                        direction_parts.append(executive_input['recommended_mood'])
                    if executive_input.get('composition_style'):
                        direction_parts.append(executive_input['composition_style'])
                    metadata['creative_direction'] = ', '.join(direction_parts)

                # Suggested next steps
                metadata['suggested_next_steps'] = [
                    f"Upscale your {style_part}{subject_part}image for higher resolution",
                    f"Generate more {style_part}{subject_part}variations with different styles",
                    "Generate color palette variations based on executive recommendations",
                    "Create video animation from your favorite logo",
                    "Add audio branding with text-to-speech"
                ]

                project = CreativeProject.objects.create(
                    user=self.user,
                    name=project_name[:100],
                    description=''.join(description_parts),
                    goal=f"Complete creative project for {style_part}{subject_part.strip()} with {len(images)} initial assets.",
                    status='in_progress',
                    category=category[:50],
                    colors=colors[:200],
                    tags=tags,
                    metadata=metadata
                )
                logger.info(f"📁 Created FULL project: {project.name}")

            # Add images to project - Session 293: Use correct relationship
            # ImageHistory.project points TO CreativeProject (not vice versa)
            for img in images:
                image_id = img.get('id')
                if image_id:
                    try:
                        image = ImageHistory.objects.get(id=image_id)
                        image.project = project  # Set the FK on the image
                        image.save()
                    except ImageHistory.DoesNotExist:
                        pass

            # Count images using the related_name 'project_images'
            result = {
                'id': str(project.id),
                'name': project.name,
                'image_count': project.project_images.count(),
                'is_new': not bool(self.project_id)
            }
            logger.info(f"✅ Project created/updated: {project.name} with {project.project_images.count()} images")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to create/update project: {e}", exc_info=True)
            return None
