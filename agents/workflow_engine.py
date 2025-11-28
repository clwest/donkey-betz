"""
Session 240: New Unified Workflow Engine

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
        # Check for digits
        match = re.search(r'(\d+)\s*(?:logo|image|thumbnail|banner|photo|illustration)', lower)
        if match:
            return min(int(match.group(1)), 10)  # Cap at 10

        # Check for word numbers
        word_numbers = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }
        for word, num in word_numbers.items():
            if word in lower:
                return num

        return 3  # Default


class PromptEnhancer:
    """Enhance user's vision with trending data - NEVER override."""

    @classmethod
    def enhance(cls, intent: UserIntent, spider_trends: Dict[str, Any],
                executive_input: Dict[str, Any]) -> str:
        """
        Build the final prompt that:
        1. Preserves user's style choice (SACRED)
        2. Preserves user's subject (SACRED)
        3. Adds trending colors, moods from spider data
        4. Adds executive recommendations for details
        """
        config = CONTENT_CONFIGS[intent.content_type]

        # Start with user's vision
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

        # 5. ENHANCE with trending data (colors, moods - NOT style override)
        enhancements = cls._extract_enhancements(spider_trends, executive_input)
        if enhancements:
            prompt_parts.append(enhancements)

        # 6. Content type requirements (NO TEXT for logos, etc.)
        prompt_parts.append(config.prompt_suffix)

        final_prompt = ", ".join(prompt_parts)
        logger.info(f"✨ Enhanced prompt: {final_prompt[:100]}...")

        return final_prompt

    @classmethod
    def _extract_enhancements(cls, spider_trends: Dict[str, Any],
                              executive_input: Dict[str, Any]) -> str:
        """Extract color/mood enhancements from data - NOT style overrides."""
        enhancements = []

        # Extract color recommendations
        colors = executive_input.get('recommended_colors', [])
        if colors:
            enhancements.append(f"color palette: {', '.join(colors[:3])}")

        # Extract mood/tone recommendations
        mood = executive_input.get('recommended_mood', '')
        if mood:
            enhancements.append(mood)

        # Extract composition tips
        composition = executive_input.get('composition_style', '')
        if composition:
            enhancements.append(composition)

        return ", ".join(enhancements) if enhancements else ""


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
        - enhancements: what trending data was applied
        """
        # 1. Parse user intent
        intent = IntentParser.parse(message)

        logger.info(f"🚀 WorkflowEngine executing: {intent.content_type.value}, "
                   f"style={intent.style}, subject={intent.subject}")

        # 2. Get spider intelligence (for enhancement, not override)
        spider_trends = self._get_spider_trends(intent)

        # 3. Get executive input (for enhancement, not override)
        executive_input = {}
        if intent.wants_research:
            executive_input = self._get_executive_enhancement(intent, spider_trends)

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

        # 6. Create project if needed
        project = None
        if self.project_id:
            project = self._add_to_project(images, intent)

        return {
            'success': True,
            'content_type': intent.content_type.value,
            'style_preserved': intent.style,
            'subject_preserved': intent.subject,
            'images': images,
            'project': project,
            'enhancements_applied': {
                'spider_trends': spider_trends,
                'executive_input': executive_input
            },
            'prompt_used': prompt
        }

    def _get_spider_trends(self, intent: UserIntent) -> Dict[str, Any]:
        """Get trending data from spider network for enhancements."""
        try:
            from core.models_unified_system import SpiderData

            # Get recent trends relevant to the purpose/industry
            # Use 'created_at' not 'collected_at'
            trends = SpiderData.objects.filter(
                data_type='trend'
            ).order_by('-created_at')[:20]

            trending_terms = []
            for trend in trends:
                # SpiderData uses 'raw_data' not 'content'
                if trend.raw_data:
                    trending_terms.extend(trend.raw_data.get('keywords', []))

            return {
                'trending_terms': list(set(trending_terms))[:10],
                'count': len(trends)
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
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant

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

            assistant = EnhancedPersonalAIAssistant(user=self.user)
            response = assistant.get_coleadership_opinion(question)

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
            animated_styles = ['pixar', 'disney', 'dreamworks', 'cartoon', 'anime', 'ghibli', 'chibi']
            model = 'sd3' if style in animated_styles else 'sdxl'

            images = []
            for i in range(count):
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
                            }
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

            for img in images:
                # The image ID is now stored as 'id' not 'image_id'
                image_id = img.get('id')
                if image_id:
                    try:
                        image = ImageHistory.objects.get(id=image_id)
                        project.images.add(image)
                    except ImageHistory.DoesNotExist:
                        logger.warning(f"Image {image_id} not found when adding to project")

            project.save()

            return {
                'id': str(project.id),
                'name': project.name,
                'image_count': project.images.count()
            }

        except Exception as e:
            logger.error(f"Failed to add to project: {e}")
            return None
