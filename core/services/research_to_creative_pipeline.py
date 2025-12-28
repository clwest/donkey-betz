"""
Research to Creative Pipeline Connector
========================================

Session 353: Connect Research Pipeline to Creative Pipeline

This service bridges the gap between:
- Research Pipeline Output (Brand Strategy, Competitor Analysis, Customer Research)
- Creative Pipeline (78 image styles, video, audio, 3D generation)

Instead of settling for just "logo and image", this intelligently selects
from 78 available styles based on brand personality, industry, and target audience
to generate a comprehensive Brand Asset Pack.

Available Style Categories (78 total):
- Photography (10): photorealistic, portrait, landscape, macro, street, fashion, etc.
- Digital Art (8): digital_art, concept_art, matte_painting, vector, low_poly, etc.
- Traditional Art (8): oil_painting, watercolor, acrylic, gouache, ink, charcoal, etc.
- Animation (18): anime, manga, pixar, disney, dreamworks, ghibli, rick_and_morty, etc.
- Artistic Movements (11): impressionist, surreal, cubist, art_deco, pop_art, etc.
- Genre (8): fantasy, scifi, cyberpunk, steampunk, gothic, horror, retro, vaporwave
- 3D & Rendering (3): 3d_render, clay_render, wireframe
- Special Effects (3): neon, holographic, glitch
- Cultural (5): japanese, chinese, indian, african, aztec
- Other (4): pixel_art, graffiti, collage, mosaic, stained_glass, origami, psychedelic

Usage:
    from core.services.research_to_creative_pipeline import ResearchToCreativePipeline

    connector = ResearchToCreativePipeline(user=request.user)
    result = connector.generate_brand_asset_pack(
        project_id="uuid",
        asset_types=["logo", "social_media", "marketing", "mood_board"]
    )
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ==================== Style Intelligence ====================

# Map brand personalities to recommended styles
BRAND_PERSONALITY_TO_STYLES = {
    # Modern/Tech brands
    'innovative': ['digital_art', 'minimalist', 'neon', 'cyberpunk', '3d_render', 'holographic'],
    'tech': ['digital_art', 'minimalist', '3d_render', 'cyberpunk', 'isometric', 'vector'],
    'modern': ['minimalist', 'vector', 'digital_art', '3d_render', 'photographic'],
    'futuristic': ['cyberpunk', 'neon', 'holographic', 'scifi', '3d_render', 'glitch'],

    # Creative/Artistic brands
    'creative': ['watercolor', 'impressionist', 'abstract', 'collage', 'graffiti', 'psychedelic'],
    'artistic': ['oil_painting', 'watercolor', 'impressionist', 'abstract', 'art_nouveau'],
    'playful': ['cartoon', 'pixar', 'disney', 'adventure_time', 'chibi', 'pop_art'],
    'whimsical': ['ghibli', 'watercolor', 'fantasy', 'disney', 'dreamworks'],

    # Professional/Corporate brands
    'professional': ['photographic', 'minimalist', 'vector', 'portrait', 'architectural'],
    'corporate': ['photographic', 'minimalist', 'architectural', 'vector', 'digital_art'],
    'luxury': ['art_deco', 'photographic', 'baroque', 'renaissance', 'fashion'],
    'premium': ['fashion', 'art_deco', 'photographic', 'minimalist', 'baroque'],

    # Bold/Edgy brands
    'bold': ['pop_art', 'graffiti', 'neon', 'cyberpunk', 'comic', 'expressionist'],
    'edgy': ['gothic', 'horror', 'graffiti', 'glitch', 'cyberpunk', 'steampunk'],
    'rebellious': ['graffiti', 'punk', 'glitch', 'horror', 'cyberpunk'],

    # Warm/Friendly brands
    'friendly': ['cartoon', 'watercolor', 'pixar', 'pastel', 'disney', 'adventure_time'],
    'warm': ['watercolor', 'pastel', 'impressionist', 'vintage', 'gouache'],
    'approachable': ['cartoon', 'vector', 'pixar', 'minimalist', 'pastel'],

    # Nature/Organic brands
    'natural': ['watercolor', 'landscape', 'botanical', 'japanese', 'impressionist'],
    'organic': ['watercolor', 'botanical', 'impressionist', 'gouache', 'vintage'],
    'earthy': ['landscape', 'vintage', 'japanese', 'african', 'indian'],

    # Retro/Nostalgic brands
    'retro': ['retro', 'vintage', 'pixel_art', 'vaporwave', 'pop_art', 'art_deco'],
    'nostalgic': ['vintage', 'retro', 'black_white', 'pixel_art', 'simpsons'],
    'classic': ['renaissance', 'baroque', 'oil_painting', 'art_deco', 'vintage'],
}

# Map industries to recommended styles
INDUSTRY_TO_STYLES = {
    # Technology
    'ai': ['digital_art', 'cyberpunk', 'neon', '3d_render', 'holographic', 'minimalist'],
    'saas': ['minimalist', 'vector', 'digital_art', 'isometric', '3d_render'],
    'fintech': ['minimalist', 'digital_art', 'vector', '3d_render', 'cyberpunk'],
    'software': ['digital_art', 'minimalist', 'vector', 'isometric', '3d_render'],
    'technology': ['digital_art', 'cyberpunk', 'minimalist', '3d_render', 'neon'],
    'web3': ['cyberpunk', 'glitch', 'neon', 'vaporwave', 'holographic'],
    'crypto': ['cyberpunk', 'glitch', 'neon', 'digital_art', 'holographic'],

    # Creative
    'design': ['digital_art', 'minimalist', 'abstract', 'vector', 'art_nouveau'],
    'art': ['watercolor', 'oil_painting', 'impressionist', 'abstract', 'collage'],
    'photography': ['photographic', 'portrait', 'landscape', 'street', 'fashion'],
    'music': ['abstract', 'graffiti', 'neon', 'psychedelic', 'vaporwave'],
    'gaming': ['pixel_art', 'anime', 'fantasy', 'cyberpunk', 'digital_art'],
    'animation': ['anime', 'pixar', 'cartoon', 'disney', 'dreamworks'],

    # Media
    'podcasting': ['digital_art', 'minimalist', 'cartoon', 'vector', 'retro'],
    'video': ['cinematic', 'digital_art', 'neon', 'cyberpunk', 'photographic'],
    'publishing': ['minimalist', 'vintage', 'vector', 'typography', 'art_deco'],
    'news': ['photographic', 'minimalist', 'vector', 'digital_art'],

    # Health & Wellness
    'health': ['watercolor', 'minimalist', 'pastel', 'vector', 'photographic'],
    'wellness': ['watercolor', 'impressionist', 'japanese', 'minimalist', 'pastel'],
    'fitness': ['photographic', 'digital_art', 'bold', 'vector', 'minimalist'],
    'meditation': ['watercolor', 'japanese', 'minimalist', 'abstract', 'impressionist'],

    # Food & Beverage
    'food': ['photographic', 'watercolor', 'vintage', 'illustration', 'macro'],
    'restaurant': ['photographic', 'vintage', 'art_deco', 'minimalist', 'macro'],
    'coffee': ['vintage', 'watercolor', 'minimalist', 'indie', 'hipster'],
    'bakery': ['watercolor', 'vintage', 'pastel', 'gouache', 'illustration'],

    # Fashion & Beauty
    'fashion': ['fashion', 'photographic', 'art_deco', 'minimalist', 'editorial'],
    'beauty': ['fashion', 'watercolor', 'art_nouveau', 'minimalist', 'pastel'],
    'luxury_goods': ['art_deco', 'fashion', 'baroque', 'minimalist', 'photographic'],

    # Professional Services
    'finance': ['minimalist', 'vector', 'corporate', 'digital_art', 'architectural'],
    'legal': ['minimalist', 'vintage', 'vector', 'corporate', 'classic'],
    'consulting': ['minimalist', 'vector', 'digital_art', 'corporate', 'photographic'],
    'education': ['watercolor', 'vector', 'cartoon', 'minimalist', 'digital_art'],

    # E-commerce
    'ecommerce': ['photographic', 'minimalist', 'vector', 'digital_art', '3d_render'],
    'retail': ['photographic', 'minimalist', 'pop_art', 'vector', 'vintage'],
    'marketplace': ['vector', 'minimalist', 'digital_art', 'isometric', '3d_render'],

    # Others
    'nonprofit': ['watercolor', 'minimalist', 'vector', 'photographic', 'illustration'],
    'environmental': ['watercolor', 'landscape', 'japanese', 'impressionist', 'botanical'],
    'travel': ['landscape', 'photographic', 'watercolor', 'vintage', 'street'],
    'real_estate': ['architectural', 'photographic', 'minimalist', '3d_render', 'vector'],
}

# Map target demographics to styles
AUDIENCE_TO_STYLES = {
    'gen_z': ['vaporwave', 'glitch', 'anime', 'pixel_art', 'neon', 'rick_and_morty'],
    'millennials': ['minimalist', 'retro', 'digital_art', 'graffiti', 'pop_art'],
    'gen_x': ['photographic', 'vintage', 'digital_art', 'minimalist', 'retro'],
    'boomers': ['photographic', 'vintage', 'classic', 'traditional', 'oil_painting'],

    'young_professionals': ['minimalist', 'digital_art', 'vector', 'modern', 'photographic'],
    'entrepreneurs': ['minimalist', 'bold', 'digital_art', 'neon', 'cyberpunk'],
    'creatives': ['watercolor', 'abstract', 'artistic', 'graffiti', 'psychedelic'],
    'executives': ['minimalist', 'photographic', 'corporate', 'architectural', 'classic'],

    'families': ['cartoon', 'pixar', 'watercolor', 'disney', 'friendly'],
    'children': ['cartoon', 'disney', 'pixar', 'adventure_time', 'chibi'],
    'teens': ['anime', 'pixel_art', 'graffiti', 'neon', 'vaporwave'],

    'artists': ['impressionist', 'abstract', 'watercolor', 'oil_painting', 'collage'],
    'gamers': ['pixel_art', 'anime', 'cyberpunk', 'fantasy', 'digital_art'],
    'developers': ['cyberpunk', 'digital_art', 'minimalist', 'neon', 'glitch'],
}

# All 78 available styles
ALL_STYLES = [
    # Photography (10)
    'photorealistic', 'photographic', 'portrait', 'landscape', 'macro',
    'street', 'fashion', 'architectural', 'black_white', 'vintage',

    # Digital Art (8)
    'digital_art', 'concept_art', 'matte_painting', 'vector',
    'low_poly', 'voxel', 'isometric', 'digital-art',

    # Traditional Art (8)
    'oil_painting', 'watercolor', 'acrylic', 'gouache',
    'ink', 'charcoal', 'pencil', 'pastel',

    # Animation & Comics (18)
    'anime', 'manga', 'pixar', 'disney', 'dreamworks', 'south_park',
    'simpsons', 'family_guy', 'ghibli', 'studio_ghibli', 'comic', 'cartoon',
    'chibi', 'looney_tunes', 'rick_and_morty', 'archer', 'adventure_time',
    'gravity_falls', 'bojack',

    # Artistic Movements (11)
    'impressionist', 'expressionist', 'surreal', 'abstract', 'cubist',
    'art_nouveau', 'art_deco', 'pop_art', 'minimalist', 'baroque', 'renaissance',

    # Genre (8)
    'fantasy', 'scifi', 'cyberpunk', 'steampunk', 'gothic', 'horror', 'retro', 'vaporwave',

    # 3D & Rendering (3)
    '3d_render', 'clay_render', 'wireframe',

    # Special Effects (3)
    'neon', 'holographic', 'glitch',

    # Cultural (5)
    'japanese', 'chinese', 'indian', 'african', 'aztec',

    # Other (7)
    'pixel_art', 'graffiti', 'collage', 'mosaic', 'stained_glass', 'origami', 'psychedelic',
]


@dataclass
class StyleRecommendation:
    """A recommended style with rationale."""
    style: str
    rationale: str
    confidence: float  # 0-1
    asset_type: str  # logo, social_media, marketing, etc.


@dataclass
class BrandAssetPack:
    """Complete brand asset pack from Creative Pipeline."""
    success: bool
    project_id: str
    styles_used: List[str] = field(default_factory=list)

    # Generated assets by category
    logos: List[Dict[str, Any]] = field(default_factory=list)
    social_media: List[Dict[str, Any]] = field(default_factory=list)
    marketing_materials: List[Dict[str, Any]] = field(default_factory=list)
    mood_board: List[Dict[str, Any]] = field(default_factory=list)
    brand_patterns: List[Dict[str, Any]] = field(default_factory=list)

    # Style guide data
    recommended_styles: List[StyleRecommendation] = field(default_factory=list)
    color_palette: List[str] = field(default_factory=list)
    style_rationale: str = ""

    # Metadata
    total_assets: int = 0
    execution_time_ms: int = 0
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'project_id': self.project_id,
            'styles_used': self.styles_used,
            'logos': self.logos,
            'social_media': self.social_media,
            'marketing_materials': self.marketing_materials,
            'mood_board': self.mood_board,
            'brand_patterns': self.brand_patterns,
            'recommended_styles': [
                {
                    'style': s.style,
                    'rationale': s.rationale,
                    'confidence': s.confidence,
                    'asset_type': s.asset_type
                }
                for s in self.recommended_styles
            ],
            'color_palette': self.color_palette,
            'style_rationale': self.style_rationale,
            'total_assets': self.total_assets,
            'execution_time_ms': self.execution_time_ms,
            'error': self.error
        }


class ResearchToCreativePipeline:
    """
    Connector between Research Pipeline and Creative Pipeline.

    Takes brand strategy research and generates a comprehensive
    Brand Asset Pack using intelligent style selection from 78 styles.
    """

    def __init__(self, user=None):
        self.user = user
        self._creative_orchestrator = None
        self._image_service = None

    @property
    def creative_orchestrator(self):
        """Lazy-load Creative Orchestrator."""
        if self._creative_orchestrator is None:
            from core.services.creative_orchestrator import CreativeOrchestrator
            self._creative_orchestrator = CreativeOrchestrator(user=self.user)
        return self._creative_orchestrator

    @property
    def image_service(self):
        """Lazy-load Image Generation Service."""
        if self._image_service is None:
            from content.image_generation import ImageGenerationService
            self._image_service = ImageGenerationService()
        return self._image_service

    def analyze_brand_strategy(self, project_id: str) -> Dict[str, Any]:
        """
        Analyze brand strategy from project research to extract style signals.

        Returns personality traits, industry, target audience, and recommended styles.
        """
        from core.models_partnership import PartnershipProject
        from core.models_unified_system import BusinessResearchResult

        try:
            project = PartnershipProject.objects.get(id=project_id)
        except PartnershipProject.DoesNotExist:
            return {'error': 'Project not found'}

        analysis = {
            'project_name': project.project_name,
            'personality_traits': [],
            'industry': '',
            'target_audiences': [],
            'recommended_styles': [],
            'style_rationale': ''
        }

        # Get brand strategy research
        brand_research = BusinessResearchResult.objects.filter(
            project=project,
            research_type='brand_strategy'
        ).order_by('-created_at').first()

        competitor_research = BusinessResearchResult.objects.filter(
            project=project,
            research_type='competitor'
        ).order_by('-created_at').first()

        customer_research = BusinessResearchResult.objects.filter(
            project=project,
            research_type='customer'
        ).order_by('-created_at').first()

        # Extract signals from research
        all_text = ""
        if brand_research:
            all_text += (brand_research.analysis or '') + " "
        if competitor_research:
            all_text += (competitor_research.analysis or '') + " "
        if customer_research:
            all_text += (customer_research.analysis or '') + " "

        all_text_lower = all_text.lower()

        # Detect personality traits
        for trait in BRAND_PERSONALITY_TO_STYLES.keys():
            if trait in all_text_lower:
                analysis['personality_traits'].append(trait)

        # Detect industry
        for industry in INDUSTRY_TO_STYLES.keys():
            if industry in all_text_lower:
                analysis['industry'] = industry
                break

        # Detect target audience
        audience_signals = {
            'gen_z': ['gen z', 'generation z', 'young audience', 'teens', 'tiktok'],
            'millennials': ['millennial', 'young professional', '25-40'],
            'gen_x': ['gen x', 'generation x', '40-55'],
            'entrepreneurs': ['entrepreneur', 'startup', 'founder', 'business owner'],
            'creatives': ['creative', 'artist', 'designer', 'creator'],
            'developers': ['developer', 'programmer', 'engineer', 'tech professional'],
            'families': ['family', 'parents', 'household'],
            'gamers': ['gamer', 'gaming', 'esports'],
        }

        for audience, signals in audience_signals.items():
            if any(signal in all_text_lower for signal in signals):
                analysis['target_audiences'].append(audience)

        # Generate style recommendations based on signals
        analysis['recommended_styles'] = self._recommend_styles(
            personality_traits=analysis['personality_traits'],
            industry=analysis['industry'],
            target_audiences=analysis['target_audiences']
        )

        # Generate rationale
        analysis['style_rationale'] = self._generate_style_rationale(analysis)

        logger.info(f"Brand analysis for {project.project_name}: {len(analysis['recommended_styles'])} styles recommended")

        return analysis

    def _recommend_styles(
        self,
        personality_traits: List[str],
        industry: str,
        target_audiences: List[str]
    ) -> List[StyleRecommendation]:
        """
        Intelligently recommend styles based on brand signals.

        Uses a weighted scoring system to select the best styles.
        """
        style_scores = {}
        style_sources = {}  # Track why each style was recommended

        # Score styles from personality traits (weight: 1.0)
        for trait in personality_traits:
            for style in BRAND_PERSONALITY_TO_STYLES.get(trait, []):
                style_scores[style] = style_scores.get(style, 0) + 1.0
                if style not in style_sources:
                    style_sources[style] = []
                style_sources[style].append(f"personality:{trait}")

        # Score styles from industry (weight: 1.5 - industry is very important)
        if industry:
            for style in INDUSTRY_TO_STYLES.get(industry, []):
                style_scores[style] = style_scores.get(style, 0) + 1.5
                if style not in style_sources:
                    style_sources[style] = []
                style_sources[style].append(f"industry:{industry}")

        # Score styles from target audience (weight: 0.8)
        for audience in target_audiences:
            for style in AUDIENCE_TO_STYLES.get(audience, []):
                style_scores[style] = style_scores.get(style, 0) + 0.8
                if style not in style_sources:
                    style_sources[style] = []
                style_sources[style].append(f"audience:{audience}")

        # Sort by score and take top styles
        sorted_styles = sorted(style_scores.items(), key=lambda x: x[1], reverse=True)

        recommendations = []

        # Primary styles (top 3) for logos
        for style, score in sorted_styles[:3]:
            sources = style_sources.get(style, [])
            recommendations.append(StyleRecommendation(
                style=style,
                rationale=f"Recommended based on: {', '.join(sources)}",
                confidence=min(score / 5.0, 1.0),
                asset_type='logo'
            ))

        # Secondary styles (4-6) for social media
        for style, score in sorted_styles[3:6]:
            sources = style_sources.get(style, [])
            recommendations.append(StyleRecommendation(
                style=style,
                rationale=f"Good for social media based on: {', '.join(sources)}",
                confidence=min(score / 5.0, 0.9),
                asset_type='social_media'
            ))

        # Tertiary styles (7-10) for marketing/mood board
        for style, score in sorted_styles[6:10]:
            sources = style_sources.get(style, [])
            recommendations.append(StyleRecommendation(
                style=style,
                rationale=f"Suitable for marketing materials based on: {', '.join(sources)}",
                confidence=min(score / 5.0, 0.8),
                asset_type='marketing'
            ))

        # If we don't have enough styles, add some defaults
        if len(recommendations) < 5:
            default_styles = ['minimalist', 'digital_art', 'vector', 'photographic', 'modern']
            for style in default_styles:
                if not any(r.style == style for r in recommendations):
                    recommendations.append(StyleRecommendation(
                        style=style,
                        rationale="Default professional style",
                        confidence=0.7,
                        asset_type='logo'
                    ))
                    if len(recommendations) >= 10:
                        break

        return recommendations

    def _generate_style_rationale(self, analysis: Dict[str, Any]) -> str:
        """Generate human-readable rationale for style selection."""
        parts = []

        if analysis['personality_traits']:
            parts.append(f"Brand personality traits detected: {', '.join(analysis['personality_traits'][:3])}")

        if analysis['industry']:
            parts.append(f"Industry: {analysis['industry']}")

        if analysis['target_audiences']:
            parts.append(f"Target audience: {', '.join(analysis['target_audiences'][:2])}")

        if analysis['recommended_styles']:
            top_styles = [r.style for r in analysis['recommended_styles'][:5]]
            parts.append(f"Recommended visual styles: {', '.join(top_styles)}")

        return ". ".join(parts) + "." if parts else "Using default professional styles."

    def generate_brand_asset_pack(
        self,
        project_id: str,
        asset_types: List[str] = None,
        custom_styles: List[str] = None,
        num_variations: int = 3
    ) -> BrandAssetPack:
        """
        Generate a comprehensive brand asset pack.

        Args:
            project_id: Project with completed research
            asset_types: Types of assets to generate ["logo", "social_media", "marketing", "mood_board"]
            custom_styles: Override automatic style selection
            num_variations: Number of variations per asset type

        Returns:
            BrandAssetPack with all generated assets
        """
        import time
        start_time = time.time()

        asset_types = asset_types or ["logo", "social_media", "marketing"]

        result = BrandAssetPack(
            success=False,
            project_id=project_id
        )

        try:
            # Step 1: Analyze brand strategy to get style recommendations
            analysis = self.analyze_brand_strategy(project_id)

            if analysis.get('error'):
                result.error = analysis['error']
                return result

            # Use custom styles or recommended styles
            if custom_styles:
                styles = custom_styles
                result.recommended_styles = [
                    StyleRecommendation(style=s, rationale="User selected", confidence=1.0, asset_type="custom")
                    for s in custom_styles
                ]
            else:
                result.recommended_styles = analysis.get('recommended_styles', [])
                styles = [r.style for r in result.recommended_styles]

            result.styles_used = styles
            result.style_rationale = analysis.get('style_rationale', '')

            # Get project for creative brief
            from core.models_partnership import PartnershipProject
            project = PartnershipProject.objects.get(id=project_id)
            project_name = project.project_name

            # Step 2: Generate assets for each type

            # LOGOS - Use top 3 styles
            if "logo" in asset_types:
                logo_styles = [r.style for r in result.recommended_styles if r.asset_type == 'logo'][:3]
                if not logo_styles:
                    logo_styles = styles[:3]

                for style in logo_styles[:num_variations]:
                    logo = self._generate_asset(
                        project_name=project_name,
                        asset_type="logo",
                        style=style,
                        size="1024x1024"
                    )
                    if logo:
                        result.logos.append({
                            'style': style,
                            'images': logo,
                            'type': 'logo'
                        })

            # SOCIAL MEDIA - Use variety of styles
            if "social_media" in asset_types:
                social_styles = [r.style for r in result.recommended_styles if r.asset_type == 'social_media']
                if not social_styles:
                    social_styles = styles[3:6] if len(styles) > 3 else styles

                for style in social_styles[:num_variations]:
                    # Generate different social media formats
                    for size, name in [("1080x1080", "instagram_square"), ("1200x630", "facebook_og")]:
                        asset = self._generate_asset(
                            project_name=project_name,
                            asset_type=f"social_media_{name}",
                            style=style,
                            size=size
                        )
                        if asset:
                            result.social_media.append({
                                'style': style,
                                'format': name,
                                'images': asset,
                                'type': 'social_media'
                            })

            # MARKETING MATERIALS - Banner, hero image
            if "marketing" in asset_types:
                marketing_styles = styles[:2]  # Use top styles for marketing

                for style in marketing_styles:
                    # Wide banner
                    banner = self._generate_asset(
                        project_name=project_name,
                        asset_type="marketing_banner",
                        style=style,
                        size="1920x600"
                    )
                    if banner:
                        result.marketing_materials.append({
                            'style': style,
                            'format': 'banner',
                            'images': banner,
                            'type': 'marketing'
                        })

            # MOOD BOARD - Diverse styles to show brand direction
            if "mood_board" in asset_types:
                mood_styles = styles[:5]  # Use 5 different styles

                for style in mood_styles:
                    mood = self._generate_asset(
                        project_name=project_name,
                        asset_type="mood_board_element",
                        style=style,
                        size="512x512"
                    )
                    if mood:
                        result.mood_board.append({
                            'style': style,
                            'images': mood,
                            'type': 'mood_board'
                        })

            # Calculate totals
            result.total_assets = (
                len(result.logos) +
                len(result.social_media) +
                len(result.marketing_materials) +
                len(result.mood_board) +
                len(result.brand_patterns)
            )

            result.success = result.total_assets > 0

        except Exception as e:
            logger.error(f"Brand asset pack generation failed: {e}", exc_info=True)
            result.error = str(e)

        result.execution_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"Brand asset pack generated: {result.total_assets} assets, "
            f"{len(result.styles_used)} styles, {result.execution_time_ms}ms"
        )

        return result

    def _generate_asset(
        self,
        project_name: str,
        asset_type: str,
        style: str,
        size: str = "1024x1024"
    ) -> Optional[List[Dict[str, Any]]]:
        """Generate a single asset with the given style."""

        # Build prompt based on asset type
        prompts = {
            'logo': f"Professional minimalist logo icon for '{project_name}', clean design, memorable, suitable for web and print, no text",
            'social_media_instagram_square': f"Eye-catching social media graphic for '{project_name}', vibrant, engaging, Instagram-worthy",
            'social_media_facebook_og': f"Professional social media banner for '{project_name}', clean design, brand-focused",
            'marketing_banner': f"Professional marketing banner for '{project_name}', modern, clean, suitable for website header",
            'mood_board_element': f"Abstract brand visual element for '{project_name}', artistic, evocative, brand essence",
            'brand_pattern': f"Seamless brand pattern for '{project_name}', subtle, repeatable, brand colors"
        }

        prompt = prompts.get(asset_type, f"Brand visual for '{project_name}'")

        try:
            result = self.image_service.generate_image(
                prompt=prompt,
                style=style,
                size=size,
                quality='balanced',
                num_images=1
            )

            if result.success and result.images:
                return [
                    {
                        'url': url,
                        'prompt': prompt,
                        'style': style,
                        'size': size,
                        'provider': result.provider_used,
                        'model': result.model_used
                    }
                    for url in result.images
                ]
            else:
                logger.warning(f"Asset generation failed for {asset_type}/{style}: {result.error_message}")
                return None

        except Exception as e:
            logger.error(f"Asset generation error: {e}")
            return None

    def get_available_styles(self) -> Dict[str, List[str]]:
        """Return all available styles grouped by category."""
        return {
            'photography': ['photorealistic', 'photographic', 'portrait', 'landscape', 'macro',
                           'street', 'fashion', 'architectural', 'black_white', 'vintage'],
            'digital_art': ['digital_art', 'concept_art', 'matte_painting', 'vector',
                           'low_poly', 'voxel', 'isometric'],
            'traditional_art': ['oil_painting', 'watercolor', 'acrylic', 'gouache',
                               'ink', 'charcoal', 'pencil', 'pastel'],
            'animation': ['anime', 'manga', 'pixar', 'disney', 'dreamworks', 'south_park',
                         'simpsons', 'family_guy', 'ghibli', 'comic', 'cartoon', 'chibi',
                         'looney_tunes', 'rick_and_morty', 'archer', 'adventure_time',
                         'gravity_falls', 'bojack'],
            'artistic_movements': ['impressionist', 'expressionist', 'surreal', 'abstract', 'cubist',
                                  'art_nouveau', 'art_deco', 'pop_art', 'minimalist', 'baroque', 'renaissance'],
            'genre': ['fantasy', 'scifi', 'cyberpunk', 'steampunk', 'gothic', 'horror', 'retro', 'vaporwave'],
            '3d_rendering': ['3d_render', 'clay_render', 'wireframe'],
            'special_effects': ['neon', 'holographic', 'glitch'],
            'cultural': ['japanese', 'chinese', 'indian', 'african', 'aztec'],
            'other': ['pixel_art', 'graffiti', 'collage', 'mosaic', 'stained_glass', 'origami', 'psychedelic']
        }


# ==================== Convenience Function ====================

def get_research_to_creative_pipeline(user=None) -> ResearchToCreativePipeline:
    """Get a ResearchToCreativePipeline instance."""
    return ResearchToCreativePipeline(user=user)
