"""
Marketplace Discovery Service - Help Creators Find Audiences
=============================================================

Session 295: Marketplace Discovery for AI Content

This service helps AI content creators find audiences by:
1. Analyzing content metadata against current trends
2. Suggesting optimal platforms for distribution
3. Generating hashtags for discoverability
4. Identifying trending opportunities matching creator's style

Uses spider network data to provide real-time market intelligence.

Usage:
    from core.services.marketplace_discovery_service import MarketplaceDiscoveryService

    service = MarketplaceDiscoveryService()

    # Analyze market fit
    fit = service.analyze_content_market_fit(provenance_id)

    # Get platform suggestions
    platforms = service.suggest_platforms(provenance_id)

    # Generate hashtags
    hashtags = service.generate_hashtags(provenance_id)

    # Find trending opportunities
    opportunities = service.find_trending_opportunities(style='cyberpunk', category='illustration')
"""

import logging
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# Platform configurations
PLATFORMS = {
    'instagram': {
        'name': 'Instagram',
        'type': 'social',
        'best_for': ['illustration', 'photography', 'art', 'lifestyle'],
        'hashtag_limit': 30,
        'image_formats': ['square', 'portrait'],
        'audience_size': 'massive',
        'monetization': ['sponsored posts', 'affiliate links'],
        'tips': [
            'Use Reels for higher reach',
            'Post during peak hours (12-3pm, 7-9pm)',
            'Engage with AI art communities'
        ]
    },
    'twitter': {
        'name': 'Twitter/X',
        'type': 'social',
        'best_for': ['illustration', 'memes', 'tech', 'news'],
        'hashtag_limit': 5,
        'image_formats': ['landscape', 'square'],
        'audience_size': 'large',
        'monetization': ['tips', 'subscriptions'],
        'tips': [
            'Thread your creation process',
            'Tag AI art hashtags (#AIart, #Midjourney)',
            'Engage with art directors and studios'
        ]
    },
    'deviantart': {
        'name': 'DeviantArt',
        'type': 'art_portfolio',
        'best_for': ['illustration', 'concept_art', 'fan_art', '3d'],
        'hashtag_limit': 50,
        'image_formats': ['any'],
        'audience_size': 'medium',
        'monetization': ['prints', 'commissions', 'core membership'],
        'tips': [
            'Join AI art groups',
            'Participate in challenges',
            'Enable prints for passive income'
        ]
    },
    'artstation': {
        'name': 'ArtStation',
        'type': 'art_portfolio',
        'best_for': ['concept_art', '3d', 'game_art', 'vfx'],
        'hashtag_limit': 25,
        'image_formats': ['any'],
        'audience_size': 'professional',
        'monetization': ['prints', 'tutorials', 'jobs'],
        'tips': [
            'Tag with game/movie studios',
            'Create project breakdowns',
            'Apply for the ArtStation Marketplace'
        ]
    },
    'behance': {
        'name': 'Behance',
        'type': 'creative_portfolio',
        'best_for': ['design', 'branding', 'ui_ux', 'photography'],
        'hashtag_limit': 50,
        'image_formats': ['any'],
        'audience_size': 'professional',
        'monetization': ['freelance jobs', 'exposure'],
        'tips': [
            'Create comprehensive project pages',
            'Connect with Adobe Creative Cloud',
            'Get featured for maximum exposure'
        ]
    },
    'dribbble': {
        'name': 'Dribbble',
        'type': 'design_portfolio',
        'best_for': ['ui_ux', 'illustration', 'branding', 'icons'],
        'hashtag_limit': 20,
        'image_formats': ['square', 'specific_ratio'],
        'audience_size': 'professional',
        'monetization': ['freelance', 'pro subscription'],
        'tips': [
            'Keep designs clean and focused',
            'Join teams for more visibility',
            'Pro account for job board access'
        ]
    },
    'pinterest': {
        'name': 'Pinterest',
        'type': 'discovery',
        'best_for': ['illustration', 'photography', 'design', 'lifestyle'],
        'hashtag_limit': 20,
        'image_formats': ['portrait', 'square'],
        'audience_size': 'massive',
        'monetization': ['affiliate pins', 'traffic to store'],
        'tips': [
            'Vertical images perform best',
            'Create boards for each style',
            'SEO-rich descriptions'
        ]
    },
    'etsy': {
        'name': 'Etsy',
        'type': 'marketplace',
        'best_for': ['prints', 'digital_downloads', 'merchandise'],
        'hashtag_limit': 13,
        'image_formats': ['any'],
        'audience_size': 'buyers',
        'monetization': ['direct sales'],
        'tips': [
            'Bundle similar styles',
            'Offer instant downloads',
            'Good mockups increase sales 300%'
        ]
    },
    'redbubble': {
        'name': 'Redbubble',
        'type': 'pod',
        'best_for': ['illustration', 'patterns', 'pop_culture'],
        'hashtag_limit': 50,
        'image_formats': ['high_res'],
        'audience_size': 'buyers',
        'monetization': ['print_on_demand royalties'],
        'tips': [
            'Tag extensively for discovery',
            'Upload 300+ DPI for best prints',
            'Trendjack responsibly'
        ]
    },
    'society6': {
        'name': 'Society6',
        'type': 'pod',
        'best_for': ['illustration', 'abstract', 'photography', 'patterns'],
        'hashtag_limit': 50,
        'image_formats': ['high_res'],
        'audience_size': 'buyers',
        'monetization': ['print_on_demand royalties'],
        'tips': [
            'Art prints pay highest royalty',
            'Create cohesive collections',
            'Apply for curated collections'
        ]
    }
}

# Style to category mapping
STYLE_CATEGORIES = {
    'cyberpunk': ['sci-fi', 'tech', 'gaming'],
    'fantasy': ['gaming', 'illustration', 'book_covers'],
    'anime': ['gaming', 'fan_art', 'illustration'],
    'photorealistic': ['photography', 'product', 'stock'],
    'watercolor': ['fine_art', 'illustration', 'stationery'],
    'minimalist': ['ui_ux', 'branding', 'icons'],
    'abstract': ['fine_art', 'prints', 'patterns'],
    'pop_art': ['merchandise', 'prints', 'social'],
    'vintage': ['branding', 'photography', 'merchandise'],
    '3d': ['gaming', 'vfx', 'product'],
    'pixel_art': ['gaming', 'retro', 'icons'],
    'concept_art': ['gaming', 'movies', 'books'],
}


@dataclass
class MarketFitResult:
    """Result from market fit analysis."""
    success: bool
    overall_score: int = 50
    trend_match: int = 50
    platform_matches: List[Dict] = field(default_factory=list)
    trending_topics: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'success': self.success,
            'overall_score': self.overall_score,
            'trend_match': self.trend_match,
            'platform_matches': self.platform_matches,
            'trending_topics': self.trending_topics,
            'recommendations': self.recommendations,
            'error': self.error,
        }


@dataclass
class PlatformSuggestion:
    """A platform suggestion for content distribution."""
    platform: str
    name: str
    match_score: int
    audience_reach: str
    monetization_options: List[str]
    tips: List[str]
    hashtag_limit: int

    def to_dict(self) -> Dict:
        return {
            'platform': self.platform,
            'name': self.name,
            'match_score': self.match_score,
            'audience_reach': self.audience_reach,
            'monetization_options': self.monetization_options,
            'tips': self.tips,
            'hashtag_limit': self.hashtag_limit,
        }


class MarketplaceDiscoveryService:
    """
    Service for helping creators find audiences for their AI content.

    Uses spider network data and content analysis to match
    content with trending topics and optimal platforms.
    """

    def __init__(self):
        self._spider_service = None

    @property
    def spider_service(self):
        """Lazy load SpiderIntelligenceService."""
        if self._spider_service is None:
            try:
                from core.services.spider_intelligence import SpiderIntelligenceService
                self._spider_service = SpiderIntelligenceService()
            except ImportError:
                logger.warning("SpiderIntelligenceService not available")
                self._spider_service = None
        return self._spider_service

    def analyze_content_market_fit(self, provenance_id: str) -> MarketFitResult:
        """
        Analyze how well content matches current market trends.

        Args:
            provenance_id: UUID of the provenance record

        Returns:
            MarketFitResult with analysis
        """
        try:
            from core.models_unified_system import ContentProvenance

            provenance = ContentProvenance.objects.get(id=provenance_id)

            # Extract content metadata
            params = provenance.generation_params or {}
            prompt = params.get('prompt', '')
            model = params.get('model', '')
            style = params.get('style', '')

            # Analyze prompt for keywords/themes
            keywords = self._extract_keywords(prompt)
            style_detected = self._detect_style(prompt, style)

            # Get trending topics from spiders
            trending = self._get_trending_topics()

            # Calculate trend match
            trend_match = self._calculate_trend_match(keywords, trending)

            # Get platform matches
            platform_matches = self._get_platform_matches(
                style_detected,
                provenance.content_type
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                style_detected,
                trend_match,
                platform_matches
            )

            # Calculate overall score
            overall_score = (trend_match + sum(p['match_score'] for p in platform_matches[:3])) // 4

            return MarketFitResult(
                success=True,
                overall_score=overall_score,
                trend_match=trend_match,
                platform_matches=platform_matches[:5],
                trending_topics=trending[:10],
                recommendations=recommendations
            )

        except ContentProvenance.DoesNotExist:
            return MarketFitResult(
                success=False,
                error=f"Provenance not found: {provenance_id}"
            )
        except Exception as e:
            logger.error(f"Error analyzing market fit: {e}")
            return MarketFitResult(success=False, error=str(e))

    def suggest_platforms(self, provenance_id: str) -> List[PlatformSuggestion]:
        """
        Suggest best platforms for distributing content.

        Args:
            provenance_id: UUID of the provenance record

        Returns:
            List of PlatformSuggestion objects
        """
        try:
            from core.models_unified_system import ContentProvenance

            provenance = ContentProvenance.objects.get(id=provenance_id)

            params = provenance.generation_params or {}
            prompt = params.get('prompt', '')
            style = params.get('style', '')

            style_detected = self._detect_style(prompt, style)
            content_type = provenance.content_type

            suggestions = []

            for platform_id, config in PLATFORMS.items():
                # Calculate match score
                match_score = self._calculate_platform_match(
                    style_detected,
                    content_type,
                    config
                )

                if match_score > 40:  # Only suggest platforms above threshold
                    suggestions.append(PlatformSuggestion(
                        platform=platform_id,
                        name=config['name'],
                        match_score=match_score,
                        audience_reach=config['audience_size'],
                        monetization_options=config.get('monetization', []),
                        tips=config.get('tips', []),
                        hashtag_limit=config.get('hashtag_limit', 30)
                    ))

            # Sort by match score
            suggestions.sort(key=lambda x: x.match_score, reverse=True)

            return suggestions[:5]

        except Exception as e:
            logger.error(f"Error suggesting platforms: {e}")
            return []

    def find_trending_opportunities(
        self,
        style: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find trending opportunities matching creator's style.

        Args:
            style: Optional style filter
            category: Optional category filter
            limit: Maximum opportunities to return

        Returns:
            List of opportunity dicts
        """
        try:
            opportunities = []

            # Get trending data from spiders
            trending = self._get_trending_topics()

            # Get relevant categories for style
            relevant_categories = []
            if style and style.lower() in STYLE_CATEGORIES:
                relevant_categories = STYLE_CATEGORIES[style.lower()]
            if category:
                relevant_categories.append(category)

            # Match trends to opportunities
            for topic in trending[:20]:
                opportunity = {
                    'topic': topic,
                    'relevance_score': 70,
                    'platforms': [],
                    'suggested_hashtags': [],
                    'timing': 'now',
                }

                # Check platform relevance
                for platform_id, config in PLATFORMS.items():
                    if any(cat in config['best_for'] for cat in relevant_categories):
                        opportunity['platforms'].append(config['name'])

                # Generate hashtags for topic
                opportunity['suggested_hashtags'] = self._topic_to_hashtags(topic)

                if opportunity['platforms']:
                    opportunities.append(opportunity)

            return opportunities[:limit]

        except Exception as e:
            logger.error(f"Error finding opportunities: {e}")
            return []

    def generate_hashtags(
        self,
        provenance_id: str,
        platform: str = 'instagram'
    ) -> List[str]:
        """
        Generate optimized hashtags for content discoverability.

        Args:
            provenance_id: UUID of the provenance record
            platform: Target platform

        Returns:
            List of hashtags (without # prefix)
        """
        try:
            from core.models_unified_system import ContentProvenance

            provenance = ContentProvenance.objects.get(id=provenance_id)

            params = provenance.generation_params or {}
            prompt = params.get('prompt', '')
            style = params.get('style', '')

            # Extract keywords
            keywords = self._extract_keywords(prompt)
            style_detected = self._detect_style(prompt, style)

            hashtags = set()

            # Add AI art standard hashtags
            ai_hashtags = [
                'aiart', 'aiartwork', 'aiartcommunity',
                'generativeart', 'aicreator', 'digitalart'
            ]
            hashtags.update(ai_hashtags[:4])

            # Add style-based hashtags
            style_hashtags = self._style_to_hashtags(style_detected)
            hashtags.update(style_hashtags[:5])

            # Add keyword-based hashtags
            for keyword in keywords[:5]:
                clean = re.sub(r'[^a-z0-9]', '', keyword.lower())
                if len(clean) >= 3:
                    hashtags.add(clean)
                    hashtags.add(f"{clean}art")

            # Add trending hashtags
            trending = self._get_trending_topics()[:3]
            for topic in trending:
                clean = re.sub(r'[^a-z0-9]', '', topic.lower())
                if len(clean) >= 3:
                    hashtags.add(clean)

            # Get platform hashtag limit
            limit = PLATFORMS.get(platform, {}).get('hashtag_limit', 30)

            # Return sorted hashtags up to limit
            return sorted(list(hashtags))[:limit]

        except Exception as e:
            logger.error(f"Error generating hashtags: {e}")
            return ['aiart', 'generativeart', 'digitalart']

    def _extract_keywords(self, prompt: str) -> List[str]:
        """Extract relevant keywords from prompt."""
        # Remove common words
        stop_words = {
            'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for',
            'with', 'by', 'and', 'or', 'is', 'are', 'be', 'this',
            'that', 'it', 'as', 'very', 'highly', 'extremely'
        }

        # Split and clean
        words = re.findall(r'\b[a-zA-Z]{3,}\b', prompt.lower())
        keywords = [w for w in words if w not in stop_words]

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for w in keywords:
            if w not in seen:
                seen.add(w)
                unique.append(w)

        return unique

    def _detect_style(self, prompt: str, style_preset: str) -> str:
        """Detect content style from prompt and preset."""
        prompt_lower = prompt.lower()

        # Check explicit style preset first
        if style_preset:
            return style_preset.lower()

        # Detect from prompt keywords
        style_keywords = {
            'cyberpunk': ['cyberpunk', 'neon', 'futuristic', 'dystopian', 'cyber'],
            'fantasy': ['fantasy', 'magical', 'dragon', 'wizard', 'medieval', 'enchanted'],
            'anime': ['anime', 'manga', 'kawaii', 'chibi', 'japanese'],
            'photorealistic': ['photorealistic', 'realistic', 'photograph', 'photo'],
            'watercolor': ['watercolor', 'watercolour', 'painted', 'painting'],
            'minimalist': ['minimalist', 'minimal', 'simple', 'clean'],
            'abstract': ['abstract', 'geometric', 'shapes'],
            'pop_art': ['pop art', 'retro', 'vintage', 'comic'],
            '3d': ['3d', 'render', 'blender', 'octane', 'unreal'],
            'pixel_art': ['pixel', 'pixelated', '8-bit', '16-bit', 'retro game'],
            'concept_art': ['concept art', 'concept', 'design sheet'],
        }

        for style, keywords in style_keywords.items():
            if any(kw in prompt_lower for kw in keywords):
                return style

        return 'digital_art'  # Default

    def _get_trending_topics(self) -> List[str]:
        """Get trending topics from spider network."""
        try:
            if self.spider_service:
                # Try to get recent spider data
                # Session 493: Fixed to extract topics from raw_data items
                from core.models_unified_system import LegacySpiderData
                recent = LegacySpiderData.objects.order_by('-created_at')[:50]

                topics = set()
                for data in recent:
                    # Extract from raw_data.items if available
                    if data.raw_data and isinstance(data.raw_data, dict):
                        items = data.raw_data.get('items', [])
                        for item in items[:5]:  # Top 5 items per record
                            if isinstance(item, dict):
                                title = item.get('title', item.get('name', ''))
                                if title:
                                    keywords = self._extract_keywords(title)
                                    topics.update(keywords[:2])

                return list(topics)[:20]
        except Exception as e:
            logger.warning(f"Could not get spider topics: {e}")

        # Fallback trending topics
        return [
            'ai', 'artificial_intelligence', 'digital_art',
            'generative', 'creative', 'illustration',
            'design', 'concept_art', 'fantasy', 'scifi'
        ]

    def _calculate_trend_match(
        self,
        keywords: List[str],
        trending: List[str]
    ) -> int:
        """Calculate how well content matches trends."""
        if not keywords or not trending:
            return 50

        matches = 0
        for keyword in keywords:
            if keyword.lower() in [t.lower() for t in trending]:
                matches += 1

        # Score from 0-100
        match_ratio = matches / max(len(keywords), 1)
        return min(100, int(50 + match_ratio * 50))

    def _get_platform_matches(
        self,
        style: str,
        content_type: str
    ) -> List[Dict]:
        """Get ranked platform matches."""
        matches = []

        for platform_id, config in PLATFORMS.items():
            score = self._calculate_platform_match(style, content_type, config)
            matches.append({
                'platform': platform_id,
                'name': config['name'],
                'match_score': score,
                'type': config['type'],
            })

        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches

    def _calculate_platform_match(
        self,
        style: str,
        content_type: str,
        config: Dict
    ) -> int:
        """Calculate match score for a platform."""
        score = 50  # Base score

        # Check if style matches platform's best_for
        style_categories = STYLE_CATEGORIES.get(style.lower(), [])
        best_for = config.get('best_for', [])

        matches = sum(1 for cat in style_categories if cat in best_for)
        if matches:
            score += matches * 15

        # Direct style match
        if style.lower() in best_for:
            score += 20

        # Content type bonus
        if content_type == 'image':
            if config['type'] in ['art_portfolio', 'creative_portfolio', 'social']:
                score += 10
        elif content_type == '3d_model':
            if '3d' in best_for or 'gaming' in best_for:
                score += 15

        return min(100, score)

    def _generate_recommendations(
        self,
        style: str,
        trend_match: int,
        platform_matches: List[Dict]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Trend-based recommendations
        if trend_match < 40:
            recommendations.append(
                "Your content style isn't trending right now, but you can stand out by being unique! "
                "Focus on building a consistent portfolio."
            )
        elif trend_match >= 70:
            recommendations.append(
                "Your style matches current trends! Act fast to capitalize on audience interest."
            )

        # Platform recommendations
        if platform_matches:
            top_platform = platform_matches[0]
            recommendations.append(
                f"Start with {top_platform['name']} - it's the best match for your style "
                f"({top_platform['match_score']}% match)."
            )

        # Style-specific recommendations
        style_tips = {
            'cyberpunk': "Cyberpunk is popular in gaming communities - try ArtStation and gaming subreddits.",
            'fantasy': "Fantasy art performs well on DeviantArt and book cover marketplaces.",
            'anime': "Anime-style works great on Twitter/X where art directors are active.",
            'photorealistic': "Consider stock image platforms for passive income with photorealistic work.",
            'minimalist': "Minimalist designs are in demand for UI/UX - try Dribbble and Behance.",
        }

        if style.lower() in style_tips:
            recommendations.append(style_tips[style.lower()])

        # Cross-posting recommendation
        recommendations.append(
            "Cross-post to multiple platforms but customize for each "
            "(e.g., different hashtags, descriptions)."
        )

        return recommendations[:5]

    def _style_to_hashtags(self, style: str) -> List[str]:
        """Convert style to relevant hashtags."""
        style_hashtags = {
            'cyberpunk': ['cyberpunk', 'cyberpunkart', 'neonart', 'futureart', 'scifiart'],
            'fantasy': ['fantasyart', 'fantasyillustration', 'magicart', 'darkfantasy'],
            'anime': ['animeart', 'animestyle', 'mangaart', 'animedrawing', 'animefanart'],
            'photorealistic': ['photorealistic', 'hyperrealism', 'realismart'],
            'watercolor': ['watercolorart', 'watercolorpainting', 'traditionalart'],
            'minimalist': ['minimalistart', 'minimalistdesign', 'cleandesign'],
            'abstract': ['abstractart', 'abstractpainting', 'geometricart'],
            'pop_art': ['popart', 'retroart', 'vintageart', 'comicart'],
            '3d': ['3dart', '3drender', 'blender3d', 'cgi'],
            'pixel_art': ['pixelart', 'pixelartist', 'retrogaming', '8bitart'],
            'concept_art': ['conceptart', 'characterdesign', 'environmentdesign'],
        }

        return style_hashtags.get(style.lower(), ['digitalart', 'artwork'])

    def _topic_to_hashtags(self, topic: str) -> List[str]:
        """Convert topic to hashtags."""
        clean = re.sub(r'[^a-z0-9]', '', topic.lower())
        if len(clean) >= 3:
            return [clean, f"{clean}art", f"{clean}design"]
        return []


# Convenience functions
def get_platform_suggestions(provenance_id: str) -> List[Dict]:
    """Quick function to get platform suggestions."""
    service = MarketplaceDiscoveryService()
    suggestions = service.suggest_platforms(provenance_id)
    return [s.to_dict() for s in suggestions]


def get_hashtags(provenance_id: str, platform: str = 'instagram') -> List[str]:
    """Quick function to get hashtags for content."""
    service = MarketplaceDiscoveryService()
    return service.generate_hashtags(provenance_id, platform)
