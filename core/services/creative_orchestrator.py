"""
Creative Orchestrator - Asset Generation from Research
=======================================================

Session 339: Wire Up Creation Agents to Autonomous Pipeline
Session 340: Added VideoAgent, AudioAgent, ThreeDAgent, Editing Agents
Session 341: Added CreativeDirectorAgent and ContentAuditAgent

This orchestrator takes completed research and generates assets:
    - Logos, thumbnails, banners (ImageAgent)
    - Promo videos, logo animations (VideoAgent)
    - Voiceovers, jingles (AudioAgent)
    - 3D product mockups (ThreeDAgent)
    - Polish/upscale (ImageEditingAgent, VideoEditingAgent)
    - Creative direction (CreativeDirectorAgent) - NEW Session 341
    - Bias/ethics audit (ContentAuditAgent) - NEW Session 341
    - Trained character/LoRA generation (TrainedCreationAgent) - NEW Session 341

Flow:
    Research Complete (from ResearchOrchestrator)
        ↓
    CreativeOrchestrator.execute_asset_generation()
        ↓
    1. Extract creative brief from brand_strategy
        ↓
    2. CreativeDirectorAgent → Enhanced creative direction (Session 341)
        ↓
    3. ImageAgent → Logo, thumbnail, banner
        ↓
    4. VideoAgent → Promo video, logo animation
        ↓
    5. AudioAgent → Voiceover, jingle
        ↓
    6. ThreeDAgent → 3D mockups (if images available)
        ↓
    7. ImageEditingAgent → Upscale best images
        ↓
    8. SEOOptimizerAgent → Metadata optimization
        ↓
    9. ContentAuditAgent → Bias/ethics audit (Session 341)
        ↓
    Return: Generated assets linked to project

Usage:
    from core.services.creative_orchestrator import CreativeOrchestrator

    orchestrator = CreativeOrchestrator(user=request.user)
    result = orchestrator.execute_asset_generation(
        project_id="uuid",
        asset_types=["logo", "thumbnail", "banner", "video", "audio"]
    )
"""

import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AssetResult:
    """Result from a single asset generation."""
    asset_type: str
    agent_name: str
    success: bool
    images: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: int = 0


@dataclass
class FullAssetResult:
    """Complete result from asset orchestration."""
    success: bool
    project_id: Optional[str] = None
    assets_generated: List[str] = field(default_factory=list)
    # Image assets
    logo: AssetResult = None
    thumbnail: AssetResult = None
    banner: AssetResult = None
    # Video assets
    promo_video: AssetResult = None
    logo_animation: AssetResult = None
    # Audio assets
    voiceover: AssetResult = None
    jingle: AssetResult = None
    # 3D assets
    product_mockup: AssetResult = None
    # All generated content
    all_images: List[Dict[str, Any]] = field(default_factory=list)
    all_videos: List[Dict[str, Any]] = field(default_factory=list)
    all_audio: List[Dict[str, Any]] = field(default_factory=list)
    seo_metadata: Dict[str, Any] = field(default_factory=dict)
    total_execution_time_ms: int = 0
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            'success': self.success,
            'project_id': self.project_id,
            'assets_generated': self.assets_generated,
            'all_images': self.all_images,
            'all_videos': self.all_videos,
            'all_audio': self.all_audio,
            'seo_metadata': self.seo_metadata,
            'total_execution_time_ms': self.total_execution_time_ms,
            'error': self.error,
        }

        # Include individual asset results
        if self.logo:
            result['logo'] = {
                'success': self.logo.success,
                'images': self.logo.images,
                'error': self.logo.error
            }
        if self.thumbnail:
            result['thumbnail'] = {
                'success': self.thumbnail.success,
                'images': self.thumbnail.images,
                'error': self.thumbnail.error
            }
        if self.banner:
            result['banner'] = {
                'success': self.banner.success,
                'images': self.banner.images,
                'error': self.banner.error
            }
        if self.promo_video:
            result['promo_video'] = {
                'success': self.promo_video.success,
                'metadata': self.promo_video.metadata,
                'error': self.promo_video.error
            }
        if self.voiceover:
            result['voiceover'] = {
                'success': self.voiceover.success,
                'metadata': self.voiceover.metadata,
                'error': self.voiceover.error
            }

        return result


class CreativeOrchestrator:
    """
    Orchestrates asset generation from completed research.

    This bridges the gap between:
    - ResearchOrchestrator output (brand_strategy, business_plan)
    - Creation agents (ImageAgent, VideoAgent, etc.)

    Attributes:
        user: Django User object
        project: PartnershipProject with research
    """

    def __init__(self, user=None):
        """
        Initialize the orchestrator.

        Args:
            user: Django User object for tracking
        """
        self.user = user
        self.project = None
        # Creation agents
        self._image_agent = None
        self._video_agent = None
        self._audio_agent = None
        self._three_d_agent = None
        # Editing agents
        self._image_editing_agent = None
        self._video_editing_agent = None
        # Strategy agents
        self._seo_agent = None
        self._content_strategy_agent = None
        self._brand_identity_agent = None
        self._social_media_agent = None
        # Session 341: Executive and Security agents
        self._creative_director_agent = None
        self._content_audit_agent = None
        # Session 341: Training agents
        self._character_training_agent = None
        self._trained_creation_agent = None

    # ==================== Lazy-Loaded Agents ====================

    @property
    def image_agent(self):
        """Lazy-load ImageAgent."""
        if self._image_agent is None:
            from core.agents import ImageAgent
            self._image_agent = ImageAgent(user=self.user)
        return self._image_agent

    @property
    def video_agent(self):
        """Lazy-load VideoAgent."""
        if self._video_agent is None:
            try:
                from core.agents import VideoAgent
                self._video_agent = VideoAgent(user=self.user)
            except ImportError:
                logger.warning("VideoAgent not available")
        return self._video_agent

    @property
    def audio_agent(self):
        """Lazy-load AudioAgent."""
        if self._audio_agent is None:
            try:
                from core.agents import AudioAgent
                self._audio_agent = AudioAgent(user=self.user)
            except ImportError:
                logger.warning("AudioAgent not available")
        return self._audio_agent

    @property
    def three_d_agent(self):
        """Lazy-load ThreeDAgent."""
        if self._three_d_agent is None:
            try:
                from core.agents import ThreeDAgent
                self._three_d_agent = ThreeDAgent(user=self.user)
            except ImportError:
                logger.warning("ThreeDAgent not available")
        return self._three_d_agent

    @property
    def image_editing_agent(self):
        """Lazy-load ImageEditingAgent."""
        if self._image_editing_agent is None:
            try:
                from core.agents import ImageEditingAgent
                self._image_editing_agent = ImageEditingAgent(user=self.user)
            except ImportError:
                logger.warning("ImageEditingAgent not available")
        return self._image_editing_agent

    @property
    def video_editing_agent(self):
        """Lazy-load VideoEditingAgent."""
        if self._video_editing_agent is None:
            try:
                from core.agents import VideoEditingAgent
                self._video_editing_agent = VideoEditingAgent(user=self.user)
            except ImportError:
                logger.warning("VideoEditingAgent not available")
        return self._video_editing_agent

    @property
    def seo_agent(self):
        """Lazy-load SEOOptimizerAgent."""
        if self._seo_agent is None:
            try:
                from core.agents.strategy import SEOOptimizerAgent
                self._seo_agent = SEOOptimizerAgent(user=self.user)
            except ImportError:
                logger.warning("SEOOptimizerAgent not available")
        return self._seo_agent

    @property
    def content_strategy_agent(self):
        """Lazy-load ContentStrategyAgent."""
        if self._content_strategy_agent is None:
            try:
                from core.agents.strategy import ContentStrategyAgent
                self._content_strategy_agent = ContentStrategyAgent(user=self.user)
            except ImportError:
                logger.warning("ContentStrategyAgent not available")
        return self._content_strategy_agent

    @property
    def brand_identity_agent(self):
        """Lazy-load BrandIdentityAgent."""
        if self._brand_identity_agent is None:
            try:
                from core.agents.strategy import BrandIdentityAgent
                self._brand_identity_agent = BrandIdentityAgent(user=self.user)
            except ImportError:
                logger.warning("BrandIdentityAgent not available")
        return self._brand_identity_agent

    @property
    def social_media_agent(self):
        """Lazy-load SocialMediaAgent."""
        if self._social_media_agent is None:
            try:
                from core.agents.strategy import SocialMediaAgent
                self._social_media_agent = SocialMediaAgent(user=self.user)
            except ImportError:
                logger.warning("SocialMediaAgent not available")
        return self._social_media_agent

    @property
    def creative_director_agent(self):
        """Session 341: Lazy-load CreativeDirectorAgent for creative oversight."""
        if self._creative_director_agent is None:
            try:
                from core.agents.executive import CreativeDirectorAgent
                self._creative_director_agent = CreativeDirectorAgent(user=self.user)
            except ImportError:
                logger.warning("CreativeDirectorAgent not available")
        return self._creative_director_agent

    @property
    def content_audit_agent(self):
        """Session 341: Lazy-load ContentAuditAgent for bias/ethics checking."""
        if self._content_audit_agent is None:
            try:
                from core.agents.security import ContentAuditAgent
                self._content_audit_agent = ContentAuditAgent(user=self.user)
            except ImportError:
                logger.warning("ContentAuditAgent not available")
        return self._content_audit_agent

    @property
    def character_training_agent(self):
        """Session 341: Lazy-load CharacterTrainingAgent for LoRA/character training."""
        if self._character_training_agent is None:
            try:
                from core.agents.training import CharacterTrainingAgent
                self._character_training_agent = CharacterTrainingAgent(user=self.user)
            except ImportError:
                logger.warning("CharacterTrainingAgent not available")
        return self._character_training_agent

    @property
    def trained_creation_agent(self):
        """Session 341: Lazy-load TrainedCreationAgent for generating with trained characters."""
        if self._trained_creation_agent is None:
            try:
                from core.agents.training import TrainedCreationAgent
                self._trained_creation_agent = TrainedCreationAgent(user=self.user)
            except ImportError:
                logger.warning("TrainedCreationAgent not available")
        return self._trained_creation_agent

    # ==================== Main Entry Point ====================

    def execute_asset_generation(
        self,
        project_id: str,
        asset_types: List[str] = None,
        style_override: str = None,
        brand_choices: Dict[str, Any] = None
    ) -> FullAssetResult:
        """
        Generate assets for a project based on its research.

        This:
        1. Loads project and extracts brand_strategy
        2. Creates creative brief from research
        3. Generates requested assets using ImageAgent
        4. Optimizes with SEO metadata
        5. Links assets to project

        Args:
            project_id: UUID of the project with completed research
            asset_types: List of asset types ["logo", "thumbnail", "banner"]
            style_override: Optional style to override brand strategy
            brand_choices: Session 394 - User's brand choices from Human-in-the-Loop review:
                - style: Selected visual style (e.g., "minimalist", "vector")
                - palette: Selected color palette name (e.g., "tech_modern")
                - logoDirection: Selected logo type (e.g., "icon_wordmark")
                - customFeedback: Optional custom feedback text

        Returns:
            FullAssetResult with all generated assets
        """
        start_time = time.time()
        asset_types = asset_types or ["logo"]

        logger.info(f"Starting asset generation for project: {project_id}")

        result = FullAssetResult(
            success=False,
            project_id=project_id
        )

        try:
            # Step 1: Load project and validate
            self.project = self._load_project(project_id)
            if not self.project:
                result.error = "Project not found"
                return result

            metadata = self.project.metadata or {}
            if not metadata.get('research_completed'):
                result.error = "Research not yet complete. Run research first."
                return result

            # Step 2: Extract creative brief from brand strategy
            brand_strategy = metadata.get('brand_strategy', {})
            business_plan = metadata.get('business_plan', {})
            creative_brief = self._extract_creative_brief(
                brand_strategy=brand_strategy,
                business_plan=business_plan,
                project_name=self.project.project_name,
                style_override=style_override,
                brand_choices=brand_choices or {}
            )

            logger.info(f"Creative brief extracted: style={creative_brief.get('style', 'default')}, "
                       f"colors={creative_brief.get('colors', [])}, logo_type={creative_brief.get('logo_type', 'auto')}")

            # Step 2.5: Session 341 - Get creative direction enhancement (optional)
            if self.creative_director_agent:
                enhanced_brief = self._get_creative_direction(creative_brief)
                if enhanced_brief:
                    creative_brief.update(enhanced_brief)
                    logger.info("Creative direction enhanced")

            # Step 3: Generate each asset type
            if "logo" in asset_types:
                logo_result = self._generate_logo(creative_brief)
                result.logo = logo_result
                if logo_result.success:
                    result.assets_generated.append("logo")
                    result.all_images.extend(logo_result.images)
                    logger.info(f"Logo generated: {len(logo_result.images)} images")

            if "thumbnail" in asset_types:
                thumbnail_result = self._generate_thumbnail(creative_brief)
                result.thumbnail = thumbnail_result
                if thumbnail_result.success:
                    result.assets_generated.append("thumbnail")
                    result.all_images.extend(thumbnail_result.images)
                    logger.info(f"Thumbnail generated: {len(thumbnail_result.images)} images")

            if "banner" in asset_types:
                banner_result = self._generate_banner(creative_brief)
                result.banner = banner_result
                if banner_result.success:
                    result.assets_generated.append("banner")
                    result.all_images.extend(banner_result.images)
                    logger.info(f"Banner generated: {len(banner_result.images)} images")

            # Step 4: Generate video assets
            if "video" in asset_types or "promo_video" in asset_types:
                video_result = self._generate_promo_video(creative_brief)
                result.promo_video = video_result
                if video_result.success:
                    result.assets_generated.append("promo_video")
                    videos = video_result.metadata.get('videos', [])
                    result.all_videos.extend(videos)
                    logger.info(f"Promo video generated: {len(videos)} videos")

            # Animate logo if we generated one and video was requested
            if "logo_animation" in asset_types and result.logo and result.logo.success:
                if result.logo.images:
                    first_logo_url = result.logo.images[0].get('url')
                    if first_logo_url:
                        animation_result = self._generate_logo_animation(
                            creative_brief, first_logo_url
                        )
                        result.logo_animation = animation_result
                        if animation_result.success:
                            result.assets_generated.append("logo_animation")
                            videos = animation_result.metadata.get('videos', [])
                            result.all_videos.extend(videos)
                            logger.info("Logo animation generated")

            # Step 5: Generate audio assets
            if "audio" in asset_types or "voiceover" in asset_types:
                voiceover_result = self._generate_voiceover(creative_brief)
                result.voiceover = voiceover_result
                if voiceover_result.success:
                    result.assets_generated.append("voiceover")
                    audio = voiceover_result.metadata.get('audio', [])
                    result.all_audio.extend(audio)
                    logger.info("Voiceover generated")

            if "jingle" in asset_types:
                jingle_result = self._generate_jingle(creative_brief)
                result.jingle = jingle_result
                if jingle_result.success:
                    result.assets_generated.append("jingle")
                    audio = jingle_result.metadata.get('audio', [])
                    result.all_audio.extend(audio)
                    logger.info("Jingle generated")

            # Step 6: Generate 3D assets
            if "3d" in asset_types or "product_mockup" in asset_types:
                mockup_result = self._generate_product_mockup(creative_brief)
                result.product_mockup = mockup_result
                if mockup_result.success:
                    result.assets_generated.append("product_mockup")
                    logger.info("Product mockup generated")

            # Step 7: Upscale best images if editing requested
            if "upscale" in asset_types and result.all_images:
                upscaled = self._upscale_best_images(result.all_images, count=1)
                if upscaled:
                    result.all_images.extend(upscaled)
                    result.assets_generated.append("upscaled")
                    logger.info(f"Upscaled {len(upscaled)} images")

            # Step 7.5: Session 341 - Generate with trained character (if available)
            if "trained_character" in asset_types and self.trained_creation_agent:
                trained_result = self._generate_with_trained_character(creative_brief)
                if trained_result and trained_result.get('success'):
                    trained_images = trained_result.get('images', [])
                    result.all_images.extend(trained_images)
                    result.assets_generated.append("trained_character")
                    logger.info(f"Trained character images generated: {len(trained_images)}")

            # Step 8: Generate SEO metadata for assets
            if result.all_images and self.seo_agent:
                seo_result = self._generate_seo_metadata(
                    creative_brief=creative_brief,
                    assets=result.all_images
                )
                result.seo_metadata = seo_result

            # Step 9: Session 341 - Content audit for bias/ethics (optional)
            if self.content_audit_agent and result.all_images:
                audit_result = self._audit_generated_content(
                    creative_brief=creative_brief,
                    assets=result.all_images
                )
                if audit_result:
                    result.seo_metadata['content_audit'] = audit_result
                    logger.info("Content audit complete")

            # Step 10: Update project with generated assets
            if result.all_images:
                self._update_project_with_assets(result)

            # Mark success if we generated at least one asset
            result.success = len(result.assets_generated) > 0

        except Exception as e:
            logger.error(f"Asset orchestration failed: {e}", exc_info=True)
            result.error = str(e)

        result.total_execution_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"Asset generation complete: {len(result.assets_generated)} assets, "
            f"{result.total_execution_time_ms}ms"
        )

        return result

    # ==================== Creative Brief Extraction ====================

    def _extract_creative_brief(
        self,
        brand_strategy: Dict[str, Any],
        business_plan: Dict[str, Any],
        project_name: str,
        style_override: str = None,
        brand_choices: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Extract creative brief from research for asset generation.

        Session 394: Now incorporates user's brand choices from Human-in-the-Loop review.

        Returns a structured brief with:
        - brand_name: Name to display
        - tagline: Short tagline
        - style: Visual style (modern, vintage, etc.)
        - colors: Brand colors (hex values)
        - industry: Industry/vertical
        - tone: Brand tone (professional, playful, etc.)
        - logo_type: Type of logo to generate (icon_wordmark, lettermark, etc.)
        - custom_feedback: Any custom feedback from user
        """
        brand_choices = brand_choices or {}

        brief = {
            'brand_name': project_name[:50] if project_name else 'Brand',
            'tagline': '',
            'style': style_override or 'modern',
            'colors': [],
            'industry': '',
            'tone': 'professional',
            'keywords': [],
            'logo_type': 'auto',
            'custom_feedback': ''
        }

        # Session 394: Apply user's brand choices (highest priority)
        if brand_choices.get('style'):
            brief['style'] = brand_choices['style']
            logger.info(f"Using user-selected style: {brief['style']}")

        if brand_choices.get('palette'):
            # Get actual colors from the palette name
            palette_colors = self._get_palette_colors(brand_choices['palette'])
            if palette_colors:
                brief['colors'] = palette_colors
                brief['palette_name'] = brand_choices['palette']
                logger.info(f"Using user-selected palette: {brand_choices['palette']} -> {palette_colors}")

        if brand_choices.get('logoDirection'):
            brief['logo_type'] = brand_choices['logoDirection']
            logger.info(f"Using user-selected logo type: {brief['logo_type']}")

        if brand_choices.get('customFeedback'):
            brief['custom_feedback'] = brand_choices['customFeedback']
            logger.info(f"Custom feedback received: {brief['custom_feedback'][:100]}...")

        # Only extract from analysis if user didn't make choices
        if not brand_choices.get('style'):
            analysis = brand_strategy.get('analysis', '')
            if isinstance(analysis, str):
                # Parse key elements from the analysis text
                analysis_lower = analysis.lower()

                # Detect style from analysis
                if 'minimalist' in analysis_lower:
                    brief['style'] = 'minimalist'
                elif 'playful' in analysis_lower or 'fun' in analysis_lower:
                    brief['style'] = 'playful'
                elif 'premium' in analysis_lower or 'luxury' in analysis_lower:
                    brief['style'] = 'premium'
                elif 'tech' in analysis_lower or 'digital' in analysis_lower:
                    brief['style'] = 'modern-tech'
                elif 'creative' in analysis_lower or 'artistic' in analysis_lower:
                    brief['style'] = 'creative'

                # Detect tone
                if 'friendly' in analysis_lower or 'approachable' in analysis_lower:
                    brief['tone'] = 'friendly'
                elif 'bold' in analysis_lower or 'confident' in analysis_lower:
                    brief['tone'] = 'bold'
                elif 'innovative' in analysis_lower:
                    brief['tone'] = 'innovative'

        # Extract from raw_data if available
        raw_data = brand_strategy.get('raw_data', [])
        if raw_data and isinstance(raw_data, list):
            # Look for color recommendations
            for item in raw_data:
                if isinstance(item, dict):
                    title = item.get('title', '').lower()
                    if 'color' in title:
                        brief['keywords'].append(item.get('title', ''))

        # Extract industry from business plan
        plan_summary = business_plan.get('summary', '')
        if isinstance(plan_summary, str):
            # Simple industry detection
            summary_lower = plan_summary.lower()
            if 'podcast' in summary_lower:
                brief['industry'] = 'podcasting'
            elif 'saas' in summary_lower or 'software' in summary_lower:
                brief['industry'] = 'software'
            elif 'e-commerce' in summary_lower or 'shop' in summary_lower:
                brief['industry'] = 'e-commerce'
            elif 'ai' in summary_lower or 'artificial intelligence' in summary_lower:
                brief['industry'] = 'AI/tech'
            elif 'marketing' in summary_lower:
                brief['industry'] = 'marketing'
            elif 'health' in summary_lower or 'wellness' in summary_lower:
                brief['industry'] = 'health'

        return brief

    def _get_palette_colors(self, palette_name: str) -> List[str]:
        """
        Session 394: Get hex colors for a palette name from the style library.

        Args:
            palette_name: Name of the palette (e.g., "tech_modern", "professional")

        Returns:
            List of hex color codes, or empty list if palette not found
        """
        try:
            from core.services.style_library import COLOR_PALETTES
            palette = COLOR_PALETTES.get(palette_name, {})
            return palette.get('colors', [])
        except ImportError:
            logger.warning("Style library not available for palette lookup")
            return []
        except Exception as e:
            logger.warning(f"Failed to get palette colors for {palette_name}: {e}")
            return []

    # ==================== Session 341: Creative Direction & Audit ====================

    def _get_creative_direction(self, creative_brief: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Session 341: Get creative direction enhancement from CreativeDirectorAgent.

        Returns enhanced brief with additional creative guidance.
        """
        if not self.creative_director_agent:
            return None

        try:
            brand_name = creative_brief.get('brand_name', 'Brand')
            style = creative_brief.get('style', 'modern')
            industry = creative_brief.get('industry', 'technology')

            task = f"""Provide creative direction for brand assets for "{brand_name}".

Current brief:
- Style: {style}
- Industry: {industry}
- Tone: {creative_brief.get('tone', 'professional')}

Suggest:
1. Color palette recommendations (2-3 colors)
2. Visual motifs that work for this brand
3. Specific style elements to incorporate
4. What to avoid for this type of brand

Keep suggestions concise and actionable."""

            result = self.creative_director_agent.execute(
                task=task,
                context={'project_id': str(self.project.id) if self.project else None},
                scifi_context={},
                spider_context={}
            )

            if result.success and result.data:
                # Extract enhancements from response
                return {
                    'creative_direction': result.data.get('analysis', result.message),
                    'enhanced': True
                }

            return None

        except Exception as e:
            logger.warning(f"Creative direction enhancement failed: {e}")
            return None

    def _audit_generated_content(
        self,
        creative_brief: Dict[str, Any],
        assets: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Session 341: Audit generated content for bias and ethics.

        Uses ContentAuditAgent to check generated assets for potential issues.
        """
        if not self.content_audit_agent:
            return None

        try:
            brand_name = creative_brief.get('brand_name', 'Brand')

            # Collect asset prompts/descriptions for audit
            asset_descriptions = []
            for asset in assets[:5]:  # Limit to first 5 assets
                if isinstance(asset, dict):
                    prompt = asset.get('prompt', asset.get('description', ''))
                    if prompt:
                        asset_descriptions.append(prompt)

            if not asset_descriptions:
                return {'status': 'skipped', 'reason': 'No asset descriptions to audit'}

            task = f"""Audit these generated asset prompts for "{brand_name}" for potential bias or ethical concerns:

{chr(10).join(f'- {desc[:200]}' for desc in asset_descriptions)}

Check for:
1. Unintended stereotypes
2. Cultural sensitivity issues
3. Inclusivity considerations
4. Potential misrepresentation

If all looks good, confirm as "passed". If issues found, provide brief recommendations."""

            result = self.content_audit_agent.execute(
                task=task,
                context={'project_id': str(self.project.id) if self.project else None},
                scifi_context={},
                spider_context={}
            )

            if result.success:
                return {
                    'status': 'audited',
                    'audit_result': result.data.get('analysis', result.message),
                    'assets_audited': len(asset_descriptions)
                }

            return {'status': 'audit_failed', 'error': result.error}

        except Exception as e:
            logger.warning(f"Content audit failed: {e}")
            return {'status': 'error', 'error': str(e)}

    def _generate_with_trained_character(
        self,
        creative_brief: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Session 341: Generate images using trained character/LoRA.

        Uses TrainedCreationAgent to generate brand assets with
        a previously trained character or style.
        """
        if not self.trained_creation_agent:
            return None

        try:
            brand_name = creative_brief.get('brand_name', 'Brand')
            style = creative_brief.get('style', 'modern')
            industry = creative_brief.get('industry', 'technology')

            # Check if there's a trained character/model available
            task = f"""Generate brand assets for "{brand_name}" using any available trained characters or styles.

Brand context:
- Style: {style}
- Industry: {industry}
- Tone: {creative_brief.get('tone', 'professional')}

If a trained character/mascot is available, create:
1. Character in a professional pose
2. Character with brand elements
3. Character in action relevant to the industry

If no trained character exists, return a message suggesting training one."""

            result = self.trained_creation_agent.execute(
                task=task,
                context={'project_id': str(self.project.id) if self.project else None},
                scifi_context={},
                spider_context={}
            )

            if result.success:
                return {
                    'success': True,
                    'images': result.data.get('images', []),
                    'message': result.message
                }

            return {'success': False, 'error': result.error}

        except Exception as e:
            logger.warning(f"Trained character generation failed: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== Asset Generation ====================

    def _generate_logo(self, creative_brief: Dict[str, Any]) -> AssetResult:
        """
        Generate logo using ImageAgent.

        Session 394: Now uses user's brand choices for style, colors, and logo type.
        """
        start_time = time.time()

        try:
            # Build logo prompt from creative brief
            brand_name = creative_brief.get('brand_name', 'Brand')
            style = creative_brief.get('style', 'modern')
            industry = creative_brief.get('industry', '')
            tone = creative_brief.get('tone', 'professional')
            colors = creative_brief.get('colors', [])
            logo_type = creative_brief.get('logo_type', 'auto')
            custom_feedback = creative_brief.get('custom_feedback', '')

            # Session 394: Build logo type description
            logo_type_desc = self._get_logo_type_description(logo_type)

            # Session 394: Build color guidance
            color_guidance = ""
            if colors:
                color_guidance = f"\nColor palette: Use these colors: {', '.join(colors)}"

            # Session 394: Include custom feedback
            custom_section = ""
            if custom_feedback:
                custom_section = f"\n\nUser's specific requirements:\n{custom_feedback}"

            task = f"""Create a professional logo for "{brand_name}".

Style: {style}
Industry: {industry if industry else 'technology'}
Tone: {tone}
Logo Type: {logo_type_desc}{color_guidance}

Requirements:
- Clean, memorable design
- Works at small and large sizes
- Suitable for web, app, and print
- {logo_type_desc}{custom_section}
"""

            # Call ImageAgent
            agent_result = self.image_agent.execute(
                task=task,
                context={
                    'count': 3,  # Generate 3 logo options
                    'style': style,  # Use user's chosen style
                    'size': '1024x1024',
                    'project_id': str(self.project.id) if self.project else None
                },
                scifi_context={},
                spider_context={}
            )

            images = agent_result.data.get('images', []) if agent_result.success else []

            return AssetResult(
                asset_type='logo',
                agent_name='ImageAgent',
                success=agent_result.success,
                images=images,
                metadata={
                    'prompt': task,
                    'style': style,
                    'logo_type': logo_type,
                    'colors': colors
                },
                error=agent_result.error if not agent_result.success else None,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            logger.error(f"Logo generation failed: {e}")
            return AssetResult(
                asset_type='logo',
                agent_name='ImageAgent',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _get_logo_type_description(self, logo_type: str) -> str:
        """
        Session 394: Get descriptive text for logo type.

        Args:
            logo_type: Logo type key (e.g., "icon_wordmark", "lettermark")

        Returns:
            Description of what kind of logo to generate
        """
        logo_descriptions = {
            'icon_wordmark': 'Icon with brand name - a symbolic icon accompanied by the brand name',
            'lettermark': 'Letter-based logo - stylized initials or first letter of the brand',
            'abstract': 'Abstract symbol - geometric or abstract shape representing the brand',
            'mascot': 'Character mascot - a character or figure that represents the brand',
            'emblem': 'Badge/emblem style - text integrated into a badge or crest design',
            'wordmark': 'Text-only logo - stylized typography of the brand name',
            'pictorial': 'Pictorial mark - a recognizable image or icon',
            'auto': 'Icon-only logo - clean, memorable icon without text'
        }
        return logo_descriptions.get(logo_type, logo_descriptions['auto'])

    def _generate_thumbnail(self, creative_brief: Dict[str, Any]) -> AssetResult:
        """
        Generate social media thumbnail using ImageAgent.

        Session 394: Now uses user's brand choices for style and colors.
        """
        start_time = time.time()

        try:
            brand_name = creative_brief.get('brand_name', 'Brand')
            style = creative_brief.get('style', 'modern')
            industry = creative_brief.get('industry', 'technology')
            colors = creative_brief.get('colors', [])
            custom_feedback = creative_brief.get('custom_feedback', '')

            # Session 394: Build color guidance
            color_guidance = ""
            if colors:
                color_guidance = f"\nColor palette: Incorporate these brand colors: {', '.join(colors)}"

            # Session 394: Include custom feedback
            custom_section = ""
            if custom_feedback:
                custom_section = f"\n\nUser's specific requirements:\n{custom_feedback}"

            task = f"""Create an eye-catching social media thumbnail for "{brand_name}".

Style: {style}, vibrant, attention-grabbing
Industry: {industry}{color_guidance}
Use: Social media, YouTube, blog posts

Requirements:
- Bold, clear imagery
- Vibrant colors that stand out
- Professional but engaging
- Works well at small preview sizes{custom_section}
"""

            agent_result = self.image_agent.execute(
                task=task,
                context={
                    'count': 2,
                    'style': style,  # Use user's chosen style
                    'size': '1280x720',  # Standard thumbnail size
                    'project_id': str(self.project.id) if self.project else None
                },
                scifi_context={},
                spider_context={}
            )

            images = agent_result.data.get('images', []) if agent_result.success else []

            return AssetResult(
                asset_type='thumbnail',
                agent_name='ImageAgent',
                success=agent_result.success,
                images=images,
                metadata={'prompt': task, 'style': style, 'colors': colors},
                error=agent_result.error if not agent_result.success else None,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return AssetResult(
                asset_type='thumbnail',
                agent_name='ImageAgent',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _generate_banner(self, creative_brief: Dict[str, Any]) -> AssetResult:
        """
        Generate marketing banner using ImageAgent.

        Session 394: Now uses user's brand choices for style and colors.
        """
        start_time = time.time()

        try:
            brand_name = creative_brief.get('brand_name', 'Brand')
            style = creative_brief.get('style', 'modern')
            industry = creative_brief.get('industry', 'technology')
            tone = creative_brief.get('tone', 'professional')
            colors = creative_brief.get('colors', [])
            custom_feedback = creative_brief.get('custom_feedback', '')

            # Session 394: Build color guidance
            color_guidance = ""
            if colors:
                color_guidance = f"\nColor palette: Incorporate these brand colors: {', '.join(colors)}"

            # Session 394: Include custom feedback
            custom_section = ""
            if custom_feedback:
                custom_section = f"\n\nUser's specific requirements:\n{custom_feedback}"

            task = f"""Create a professional marketing banner for "{brand_name}".

Style: {style}, {tone}
Industry: {industry}{color_guidance}
Use: Website header, landing page, marketing materials

Requirements:
- Wide format suitable for headers
- Clean, professional design
- Subtle branding elements
- Space for text overlay if needed{custom_section}
"""

            agent_result = self.image_agent.execute(
                task=task,
                context={
                    'count': 2,
                    'style': style,  # Use user's chosen style
                    'size': '1280x720',  # Banner size
                    'project_id': str(self.project.id) if self.project else None
                },
                scifi_context={},
                spider_context={}
            )

            images = agent_result.data.get('images', []) if agent_result.success else []

            return AssetResult(
                asset_type='banner',
                agent_name='ImageAgent',
                success=agent_result.success,
                images=images,
                metadata={'prompt': task, 'style': style, 'colors': colors},
                error=agent_result.error if not agent_result.success else None,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            logger.error(f"Banner generation failed: {e}")
            return AssetResult(
                asset_type='banner',
                agent_name='ImageAgent',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    # ==================== Video Generation ====================

    def _generate_promo_video(self, creative_brief: Dict[str, Any]) -> AssetResult:
        """Generate promotional video using VideoAgent."""
        start_time = time.time()

        if not self.video_agent:
            return AssetResult(
                asset_type='promo_video',
                agent_name='VideoAgent',
                success=False,
                error='VideoAgent not available',
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        try:
            brand_name = creative_brief.get('brand_name', 'Brand')
            style = creative_brief.get('style', 'modern')
            industry = creative_brief.get('industry', 'technology')
            tone = creative_brief.get('tone', 'professional')

            task = f"""Create a short promotional video for "{brand_name}".

Style: {style}, cinematic, engaging
Industry: {industry}
Tone: {tone}
Duration: 5 seconds

Requirements:
- Dynamic, attention-grabbing motion
- Subtle brand elements
- Professional production quality
- Suitable for social media ads
"""

            agent_result = self.video_agent.execute(
                task=task,
                context={
                    'duration': 5,
                    'style': style,
                    'project_id': str(self.project.id) if self.project else None
                },
                scifi_context={},
                spider_context={}
            )

            videos = agent_result.data.get('videos', []) if agent_result.success else []

            return AssetResult(
                asset_type='promo_video',
                agent_name='VideoAgent',
                success=agent_result.success,
                images=[],  # Videos stored separately
                metadata={'prompt': task, 'videos': videos},
                error=agent_result.error if not agent_result.success else None,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            logger.error(f"Promo video generation failed: {e}")
            return AssetResult(
                asset_type='promo_video',
                agent_name='VideoAgent',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _generate_logo_animation(
        self,
        creative_brief: Dict[str, Any],
        logo_image_url: str
    ) -> AssetResult:
        """Animate the logo using VideoAgent."""
        start_time = time.time()

        if not self.video_agent:
            return AssetResult(
                asset_type='logo_animation',
                agent_name='VideoAgent',
                success=False,
                error='VideoAgent not available',
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        try:
            brand_name = creative_brief.get('brand_name', 'Brand')
            style = creative_brief.get('style', 'modern')

            task = f"""Animate this logo for "{brand_name}" with a professional reveal animation.

Style: {style}, elegant motion
Duration: 3 seconds

Requirements:
- Smooth, professional reveal
- Subtle motion (zoom, fade, particles)
- Loop-friendly ending
- Suitable for video intros
"""

            agent_result = self.video_agent.execute(
                task=task,
                context={
                    'image_url': logo_image_url,
                    'animation_type': 'image_to_video',
                    'duration': 3,
                    'project_id': str(self.project.id) if self.project else None
                },
                scifi_context={},
                spider_context={}
            )

            videos = agent_result.data.get('videos', []) if agent_result.success else []

            return AssetResult(
                asset_type='logo_animation',
                agent_name='VideoAgent',
                success=agent_result.success,
                images=[],
                metadata={'prompt': task, 'videos': videos, 'source_image': logo_image_url},
                error=agent_result.error if not agent_result.success else None,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            logger.error(f"Logo animation failed: {e}")
            return AssetResult(
                asset_type='logo_animation',
                agent_name='VideoAgent',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    # ==================== Audio Generation ====================

    def _generate_voiceover(self, creative_brief: Dict[str, Any]) -> AssetResult:
        """Generate voiceover using AudioAgent."""
        start_time = time.time()

        if not self.audio_agent:
            return AssetResult(
                asset_type='voiceover',
                agent_name='AudioAgent',
                success=False,
                error='AudioAgent not available',
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        try:
            brand_name = creative_brief.get('brand_name', 'Brand')
            tagline = creative_brief.get('tagline', '')
            industry = creative_brief.get('industry', 'technology')
            tone = creative_brief.get('tone', 'professional')

            # Create a short brand intro script
            script = tagline if tagline else f"Introducing {brand_name}. Innovation meets {industry}."

            task = f"""Generate a professional voiceover for this brand intro:

Script: "{script}"
Tone: {tone}, confident, warm
Brand: {brand_name}

Requirements:
- Clear, professional voice
- Natural pacing
- Suitable for video ads
"""

            agent_result = self.audio_agent.execute(
                task=task,
                context={
                    'script': script,
                    'voice_style': tone,
                    'project_id': str(self.project.id) if self.project else None
                },
                scifi_context={},
                spider_context={}
            )

            audio_files = agent_result.data.get('audio', []) if agent_result.success else []

            return AssetResult(
                asset_type='voiceover',
                agent_name='AudioAgent',
                success=agent_result.success,
                images=[],
                metadata={'prompt': task, 'script': script, 'audio': audio_files},
                error=agent_result.error if not agent_result.success else None,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            logger.error(f"Voiceover generation failed: {e}")
            return AssetResult(
                asset_type='voiceover',
                agent_name='AudioAgent',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _generate_jingle(self, creative_brief: Dict[str, Any]) -> AssetResult:
        """Generate brand jingle/sound effect using AudioAgent."""
        start_time = time.time()

        if not self.audio_agent:
            return AssetResult(
                asset_type='jingle',
                agent_name='AudioAgent',
                success=False,
                error='AudioAgent not available',
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        try:
            brand_name = creative_brief.get('brand_name', 'Brand')
            style = creative_brief.get('style', 'modern')
            tone = creative_brief.get('tone', 'professional')

            task = f"""Create a short audio logo/jingle for "{brand_name}".

Style: {style}, memorable, distinctive
Tone: {tone}
Duration: 3-5 seconds

Requirements:
- Catchy, memorable sound
- Professional production quality
- Suitable for video outros
- Brand-appropriate mood
"""

            agent_result = self.audio_agent.execute(
                task=task,
                context={
                    'type': 'sound_effect',
                    'duration': 5,
                    'project_id': str(self.project.id) if self.project else None
                },
                scifi_context={},
                spider_context={}
            )

            audio_files = agent_result.data.get('audio', []) if agent_result.success else []

            return AssetResult(
                asset_type='jingle',
                agent_name='AudioAgent',
                success=agent_result.success,
                images=[],
                metadata={'prompt': task, 'audio': audio_files},
                error=agent_result.error if not agent_result.success else None,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            logger.error(f"Jingle generation failed: {e}")
            return AssetResult(
                asset_type='jingle',
                agent_name='AudioAgent',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    # ==================== 3D Generation ====================

    def _generate_product_mockup(self, creative_brief: Dict[str, Any]) -> AssetResult:
        """Generate 3D product mockup using ThreeDAgent."""
        start_time = time.time()

        if not self.three_d_agent:
            return AssetResult(
                asset_type='product_mockup',
                agent_name='ThreeDAgent',
                success=False,
                error='ThreeDAgent not available',
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        try:
            brand_name = creative_brief.get('brand_name', 'Brand')
            style = creative_brief.get('style', 'modern')
            industry = creative_brief.get('industry', 'technology')

            task = f"""Create a 3D product mockup for "{brand_name}".

Style: {style}, realistic, professional
Industry: {industry}

Requirements:
- High-quality 3D render
- Professional lighting
- Suitable for marketing materials
- Clean, modern aesthetic
"""

            agent_result = self.three_d_agent.execute(
                task=task,
                context={
                    'render_quality': 'high',
                    'project_id': str(self.project.id) if self.project else None
                },
                scifi_context={},
                spider_context={}
            )

            models = agent_result.data.get('models', []) if agent_result.success else []

            return AssetResult(
                asset_type='product_mockup',
                agent_name='ThreeDAgent',
                success=agent_result.success,
                images=[],
                metadata={'prompt': task, 'models': models},
                error=agent_result.error if not agent_result.success else None,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            logger.error(f"Product mockup generation failed: {e}")
            return AssetResult(
                asset_type='product_mockup',
                agent_name='ThreeDAgent',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    # ==================== Image Editing ====================

    def _upscale_best_images(
        self,
        images: List[Dict[str, Any]],
        count: int = 1
    ) -> List[Dict[str, Any]]:
        """Upscale the best images using ImageEditingAgent."""
        if not self.image_editing_agent or not images:
            return []

        try:
            # Take first N images to upscale
            to_upscale = images[:count]
            upscaled = []

            for img in to_upscale:
                image_url = img.get('url')
                if not image_url:
                    continue

                task = f"Upscale this image to 2x resolution while maintaining quality."

                result = self.image_editing_agent.execute(
                    task=task,
                    context={
                        'image_url': image_url,
                        'operation': 'upscale',
                        'scale': 2
                    },
                    scifi_context={},
                    spider_context={}
                )

                if result.success:
                    upscaled_data = result.data.get('image', {})
                    upscaled.append({
                        'original_url': image_url,
                        'upscaled_url': upscaled_data.get('url'),
                        'id': upscaled_data.get('id')
                    })

            logger.info(f"Upscaled {len(upscaled)} images")
            return upscaled

        except Exception as e:
            logger.warning(f"Image upscaling failed: {e}")
            return []

    # ==================== SEO Metadata ====================

    def _generate_seo_metadata(
        self,
        creative_brief: Dict[str, Any],
        assets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate SEO metadata for assets using SEOOptimizerAgent."""
        if not self.seo_agent:
            # Return basic metadata if SEO agent not available
            return {
                'hashtags': self._generate_basic_hashtags(creative_brief),
                'alt_text': f"{creative_brief.get('brand_name', 'Brand')} visual assets",
                'keywords': creative_brief.get('keywords', [])
            }

        try:
            brand_name = creative_brief.get('brand_name', 'Brand')
            industry = creative_brief.get('industry', 'technology')

            task = f"""Generate SEO metadata for {len(assets)} brand assets for "{brand_name}" in the {industry} industry.

Include:
- Relevant hashtags (5-10)
- Alt text for accessibility
- Keywords for discoverability
"""

            result = self.seo_agent.execute(
                task=task,
                context={'brand': brand_name, 'industry': industry},
                scifi_context={},
                spider_context={}
            )

            if result.success:
                return result.data
            else:
                return {
                    'hashtags': self._generate_basic_hashtags(creative_brief),
                    'alt_text': f"{brand_name} brand assets"
                }

        except Exception as e:
            logger.warning(f"SEO metadata generation failed: {e}")
            return {
                'hashtags': self._generate_basic_hashtags(creative_brief),
                'error': str(e)
            }

    def _generate_basic_hashtags(self, creative_brief: Dict[str, Any]) -> List[str]:
        """Generate basic hashtags without SEO agent."""
        industry = creative_brief.get('industry', 'technology')
        tags = ['#branding', '#startup', '#entrepreneur']

        if 'podcast' in industry.lower():
            tags.extend(['#podcast', '#podcaster', '#podcastlife'])
        elif 'ai' in industry.lower() or 'tech' in industry.lower():
            tags.extend(['#AI', '#technology', '#innovation'])
        elif 'marketing' in industry.lower():
            tags.extend(['#marketing', '#digitalmarketing', '#growth'])

        return tags[:8]

    # ==================== Project Management ====================

    def _load_project(self, project_id: str):
        """Load PartnershipProject by ID."""
        from core.models_partnership import PartnershipProject

        try:
            project = PartnershipProject.objects.get(id=project_id)
            # Verify user access if user is set
            if self.user and project.user != self.user:
                logger.warning(f"User {self.user} does not own project {project_id}")
                return None
            return project
        except PartnershipProject.DoesNotExist:
            logger.warning(f"Project not found: {project_id}")
            return None

    def _update_project_with_assets(self, result: FullAssetResult):
        """Update project with generated assets."""
        if not self.project:
            return

        try:
            self.project.metadata = self.project.metadata or {}
            self.project.metadata['assets_generated'] = True
            self.project.metadata['asset_types'] = result.assets_generated

            # Count all assets
            total_assets = (
                len(result.all_images) +
                len(result.all_videos) +
                len(result.all_audio)
            )
            self.project.metadata['asset_count'] = total_assets
            self.project.metadata['seo_metadata'] = result.seo_metadata

            # Store image references
            image_refs = []
            for img in result.all_images:
                if isinstance(img, dict):
                    image_refs.append({
                        'id': img.get('id'),
                        'url': img.get('url'),
                        'type': img.get('type', 'image')
                    })
            self.project.metadata['asset_images'] = image_refs

            # Store video references
            video_refs = []
            for vid in result.all_videos:
                if isinstance(vid, dict):
                    video_refs.append({
                        'id': vid.get('id'),
                        'url': vid.get('url'),
                        'type': 'video'
                    })
            self.project.metadata['asset_videos'] = video_refs

            # Store audio references
            audio_refs = []
            for aud in result.all_audio:
                if isinstance(aud, dict):
                    audio_refs.append({
                        'id': aud.get('id'),
                        'url': aud.get('url'),
                        'type': 'audio'
                    })
            self.project.metadata['asset_audio'] = audio_refs

            # Calculate time saved based on asset types
            time_saved = 0.0
            if result.all_images:
                time_saved += 1.0  # 1 hour for image design
            if result.all_videos:
                time_saved += 2.0  # 2 hours for video production
            if result.all_audio:
                time_saved += 0.5  # 30 min for audio

            # Add AI contribution
            asset_summary = f"{len(result.all_images)} images"
            if result.all_videos:
                asset_summary += f", {len(result.all_videos)} videos"
            if result.all_audio:
                asset_summary += f", {len(result.all_audio)} audio"

            self.project.add_ai_contribution(
                agent_name='CreativeOrchestrator',
                task='Generate brand assets from research',
                time_saved_hours=time_saved,
                output_summary=f"Generated {asset_summary}: {', '.join(result.assets_generated)}"
            )

            self.project.save()
            logger.info(f"Updated project {self.project.id} with {total_assets} assets")

        except Exception as e:
            logger.warning(f"Failed to update project with assets: {e}")


# ==================== Convenience Function ====================

def get_creative_orchestrator(user=None) -> CreativeOrchestrator:
    """Get a CreativeOrchestrator instance."""
    return CreativeOrchestrator(user=user)
