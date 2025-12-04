"""
Creative Orchestrator - Asset Generation from Research
=======================================================

Session 339: Wire Up Creation Agents to Autonomous Pipeline

This orchestrator takes completed research and generates assets:
    - Logos based on brand strategy
    - Thumbnails for social media
    - Banners for marketing
    - (Optional) Videos, audio

Flow:
    Research Complete (from ResearchOrchestrator)
        ↓
    CreativeOrchestrator.execute_asset_generation()
        ↓
    1. Extract creative brief from brand_strategy
        ↓
    2. ImageAgent → Logo generation
        ↓
    3. ImageAgent → Thumbnail generation
        ↓
    4. ImageAgent → Banner generation
        ↓
    5. SEOOptimizerAgent → Metadata optimization
        ↓
    Return: Generated assets linked to project

Usage:
    from core.services.creative_orchestrator import CreativeOrchestrator

    orchestrator = CreativeOrchestrator(user=request.user)
    result = orchestrator.execute_asset_generation(
        project_id="uuid",
        asset_types=["logo", "thumbnail", "banner"]
    )
"""

import logging
import time
import json
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
    logo: AssetResult = None
    thumbnail: AssetResult = None
    banner: AssetResult = None
    all_images: List[Dict[str, Any]] = field(default_factory=list)
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
        self._image_agent = None
        self._seo_agent = None

    # ==================== Lazy-Loaded Agents ====================

    @property
    def image_agent(self):
        """Lazy-load ImageAgent."""
        if self._image_agent is None:
            from core.agents import ImageAgent
            self._image_agent = ImageAgent(user=self.user)
        return self._image_agent

    @property
    def seo_agent(self):
        """Lazy-load SEOOptimizerAgent (if available)."""
        if self._seo_agent is None:
            try:
                from core.agents.strategy import SEOOptimizerAgent
                self._seo_agent = SEOOptimizerAgent(user=self.user)
            except ImportError:
                logger.warning("SEOOptimizerAgent not available")
                self._seo_agent = None
        return self._seo_agent

    # ==================== Main Entry Point ====================

    def execute_asset_generation(
        self,
        project_id: str,
        asset_types: List[str] = None,
        style_override: str = None
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
                style_override=style_override
            )

            logger.info(f"Creative brief extracted: {creative_brief.get('style', 'default')}")

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

            # Step 4: Generate SEO metadata for assets
            if result.all_images and self.seo_agent:
                seo_result = self._generate_seo_metadata(
                    creative_brief=creative_brief,
                    assets=result.all_images
                )
                result.seo_metadata = seo_result

            # Step 5: Update project with generated assets
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
        style_override: str = None
    ) -> Dict[str, Any]:
        """
        Extract creative brief from research for asset generation.

        Returns a structured brief with:
        - brand_name: Name to display
        - tagline: Short tagline
        - style: Visual style (modern, vintage, etc.)
        - colors: Brand colors
        - industry: Industry/vertical
        - tone: Brand tone (professional, playful, etc.)
        """
        brief = {
            'brand_name': project_name[:50] if project_name else 'Brand',
            'tagline': '',
            'style': style_override or 'modern',
            'colors': [],
            'industry': '',
            'tone': 'professional',
            'keywords': []
        }

        # Extract from brand_strategy analysis
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

    # ==================== Asset Generation ====================

    def _generate_logo(self, creative_brief: Dict[str, Any]) -> AssetResult:
        """Generate logo using ImageAgent."""
        start_time = time.time()

        try:
            # Build logo prompt from creative brief
            brand_name = creative_brief.get('brand_name', 'Brand')
            style = creative_brief.get('style', 'modern')
            industry = creative_brief.get('industry', '')
            tone = creative_brief.get('tone', 'professional')

            task = f"""Create a professional logo for "{brand_name}".

Style: {style}
Industry: {industry if industry else 'technology'}
Tone: {tone}

Requirements:
- Clean, memorable design
- Works at small and large sizes
- Suitable for web, app, and print
- No text in the logo (icon only)
"""

            # Call ImageAgent
            agent_result = self.image_agent.execute(
                task=task,
                context={
                    'count': 3,  # Generate 3 logo options
                    'style': 'digital_art',
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
                metadata={'prompt': task},
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

    def _generate_thumbnail(self, creative_brief: Dict[str, Any]) -> AssetResult:
        """Generate social media thumbnail using ImageAgent."""
        start_time = time.time()

        try:
            brand_name = creative_brief.get('brand_name', 'Brand')
            style = creative_brief.get('style', 'modern')
            industry = creative_brief.get('industry', 'technology')

            task = f"""Create an eye-catching social media thumbnail for "{brand_name}".

Style: {style}, vibrant, attention-grabbing
Industry: {industry}
Use: Social media, YouTube, blog posts

Requirements:
- Bold, clear imagery
- Vibrant colors that stand out
- Professional but engaging
- Works well at small preview sizes
"""

            agent_result = self.image_agent.execute(
                task=task,
                context={
                    'count': 2,
                    'style': 'cinematic',
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
                metadata={'prompt': task},
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
        """Generate marketing banner using ImageAgent."""
        start_time = time.time()

        try:
            brand_name = creative_brief.get('brand_name', 'Brand')
            style = creative_brief.get('style', 'modern')
            industry = creative_brief.get('industry', 'technology')
            tone = creative_brief.get('tone', 'professional')

            task = f"""Create a professional marketing banner for "{brand_name}".

Style: {style}, {tone}
Industry: {industry}
Use: Website header, landing page, marketing materials

Requirements:
- Wide format suitable for headers
- Clean, professional design
- Subtle branding elements
- Space for text overlay if needed
"""

            agent_result = self.image_agent.execute(
                task=task,
                context={
                    'count': 2,
                    'style': 'cinematic',
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
                metadata={'prompt': task},
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
            self.project.metadata['asset_count'] = len(result.all_images)
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

            # Add AI contribution
            self.project.add_ai_contribution(
                agent_name='CreativeOrchestrator',
                task='Generate brand assets from research',
                time_saved_hours=1.0,  # Estimate: 1 hour of design work
                output_summary=f"Generated {len(result.all_images)} assets: {', '.join(result.assets_generated)}"
            )

            self.project.save()
            logger.info(f"Updated project {self.project.id} with {len(result.all_images)} assets")

        except Exception as e:
            logger.warning(f"Failed to update project with assets: {e}")


# ==================== Convenience Function ====================

def get_creative_orchestrator(user=None) -> CreativeOrchestrator:
    """Get a CreativeOrchestrator instance."""
    return CreativeOrchestrator(user=user)
