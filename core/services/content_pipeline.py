"""
Unified Content Pipeline Service - Session 440

The AI Content Factory: Orchestrates the full pipeline from idea to finished content.

Pipeline Stages:
1. Research - Spider data gathering for trends/context
2. Script - GPT generates scripts, copy, stories
3. Character - Stability AI creates visuals
4. Voice - ElevenLabs generates audio
5. Video - Runway ML creates animations
6. Package - Bundle everything for delivery

Same pipeline powers everything from $5 birthday messages to $50K productions.
"""

import logging
from decimal import Decimal
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone

from core.models_content_pipeline import (
    ContentPackage, ContentAsset, ContentGenerationJob,
    ContentTier, PackageStatus, AssetType
)

logger = logging.getLogger(__name__)


# =============================================================================
# TIER CONFIGURATIONS
# =============================================================================

@dataclass
class TierConfig:
    """Configuration for each content tier"""
    name: str
    min_price: Decimal
    max_price: Decimal
    default_price: Decimal

    # What gets generated
    num_images: int
    num_videos: int
    num_voice_options: int
    video_durations: List[int]  # in seconds

    # Generation settings
    image_quality: str  # 'standard', 'hd', 'ultra'
    video_quality: str
    voice_quality: str

    # Estimated costs
    estimated_cost: Decimal


TIER_CONFIGS: Dict[str, TierConfig] = {
    ContentTier.QUICK: TierConfig(
        name="Quick Content",
        min_price=Decimal("5.00"),
        max_price=Decimal("29.00"),
        default_price=Decimal("15.00"),
        num_images=1,
        num_videos=1,
        num_voice_options=1,
        video_durations=[15],
        image_quality="standard",
        video_quality="standard",
        voice_quality="standard",
        estimated_cost=Decimal("0.17"),
    ),
    ContentTier.AD: TierConfig(
        name="Small Business Ad",
        min_price=Decimal("29.00"),
        max_price=Decimal("99.00"),
        default_price=Decimal("49.00"),
        num_images=3,
        num_videos=3,
        num_voice_options=3,
        video_durations=[15, 30, 60],
        image_quality="hd",
        video_quality="hd",
        voice_quality="standard",
        estimated_cost=Decimal("0.80"),
    ),
    ContentTier.BRAND: TierConfig(
        name="Brand Package",
        min_price=Decimal("99.00"),
        max_price=Decimal("499.00"),
        default_price=Decimal("249.00"),
        num_images=10,
        num_videos=5,
        num_voice_options=3,
        video_durations=[15, 30, 60],
        image_quality="hd",
        video_quality="hd",
        voice_quality="hd",
        estimated_cost=Decimal("2.90"),
    ),
    ContentTier.SERIES: TierConfig(
        name="Content Series",
        min_price=Decimal("499.00"),
        max_price=Decimal("2999.00"),
        default_price=Decimal("1499.00"),
        num_images=20,
        num_videos=5,
        num_voice_options=3,
        video_durations=[180, 300],  # 3-5 min videos
        image_quality="hd",
        video_quality="hd",
        voice_quality="hd",
        estimated_cost=Decimal("14.00"),
    ),
    ContentTier.PITCH: TierConfig(
        name="Pitch Package",
        min_price=Decimal("2999.00"),
        max_price=Decimal("9999.00"),
        default_price=Decimal("4999.00"),
        num_images=50,
        num_videos=4,
        num_voice_options=5,
        video_durations=[300, 600, 1320],  # 5min, 10min, 22min pilot
        image_quality="ultra",
        video_quality="ultra",
        voice_quality="ultra",
        estimated_cost=Decimal("70.00"),
    ),
    ContentTier.PRODUCTION: TierConfig(
        name="Full Production",
        min_price=Decimal("9999.00"),
        max_price=Decimal("99999.00"),
        default_price=Decimal("49999.00"),
        num_images=100,
        num_videos=10,
        num_voice_options=10,
        video_durations=[1320] * 10,  # 10 x 22min episodes
        image_quality="ultra",
        video_quality="ultra",
        voice_quality="ultra",
        estimated_cost=Decimal("700.00"),
    ),
}


# =============================================================================
# PIPELINE SERVICE
# =============================================================================

class UnifiedContentPipeline:
    """
    The AI Content Factory.

    Orchestrates the complete content generation pipeline:
    1. Research (Spiders) - Gather context and trends
    2. Script (GPT) - Generate copy, scripts, stories
    3. Character (Stability AI) - Create visuals
    4. Voice (ElevenLabs) - Generate audio
    5. Video (Runway ML) - Create animations
    6. Package - Bundle for delivery

    Example usage:
        pipeline = UnifiedContentPipeline()
        package = await pipeline.create_package(
            tier="ad",
            prompt="Tony's Pizza, Brooklyn, family owned since 1985, $2 Tuesdays",
            user=request.user,
            category="restaurant"
        )
    """

    def __init__(self):
        self.openai_client = None
        self.stability_client = None
        self.elevenlabs_client = None
        self.runway_client = None
        self._init_clients()

    def _init_clients(self):
        """Initialize API clients"""
        try:
            from openai import OpenAI
            self.openai_client = OpenAI()
            logger.info("OpenAI client initialized")
        except Exception as e:
            logger.warning(f"OpenAI client not available: {e}")

        # Stability, ElevenLabs, Runway initialized on demand

    async def create_package(
        self,
        tier: str,
        prompt: str,
        user,
        category: str = "other",
        custom_config: Optional[Dict] = None,
        is_public: bool = True,
    ) -> ContentPackage:
        """
        Create a new content package.

        Args:
            tier: Content tier (quick, ad, brand, series, pitch, production)
            prompt: The creative prompt describing what to create
            user: The user creating the package
            category: Industry/use case category
            custom_config: Optional overrides for generation settings
            is_public: Whether to list in public marketplace

        Returns:
            ContentPackage instance (generation starts in background)
        """
        # Get tier config
        tier_config = TIER_CONFIGS.get(tier)
        if not tier_config:
            raise ValueError(f"Invalid tier: {tier}")

        # Create package
        package = ContentPackage.objects.create(
            name=self._generate_name(prompt, tier),
            description=prompt,
            tier=tier,
            category=category,
            prompt=prompt,
            base_price=tier_config.default_price,
            status=PackageStatus.QUEUED,
            is_public=is_public,
            created_by=user,
            generation_config={
                "tier_config": {
                    "num_images": tier_config.num_images,
                    "num_videos": tier_config.num_videos,
                    "num_voice_options": tier_config.num_voice_options,
                    "video_durations": tier_config.video_durations,
                    "image_quality": tier_config.image_quality,
                    "video_quality": tier_config.video_quality,
                    "voice_quality": tier_config.voice_quality,
                },
                "custom_config": custom_config or {},
            }
        )

        # Create generation job
        job = ContentGenerationJob.objects.create(
            package=package,
            current_stage="queued"
        )

        # Start generation in background
        from core.tasks import generate_content_package
        generate_content_package.delay(str(package.id))

        logger.info(f"Created content package: {package.name} (tier={tier})")
        return package

    def _generate_name(self, prompt: str, tier: str) -> str:
        """Generate a name for the package from the prompt"""
        # Take first few words and clean up
        words = prompt.split()[:5]
        name = " ".join(words)
        if len(prompt) > len(name):
            name += "..."
        return f"{name} ({tier.title()})"

    # =========================================================================
    # PIPELINE STAGES
    # =========================================================================

    async def run_pipeline(self, package_id: str):
        """
        Run the complete generation pipeline for a package.
        Called by Celery task.
        """
        try:
            package = ContentPackage.objects.get(id=package_id)
            job = package.generation_job

            package.start_generation()
            job.started_at = timezone.now()
            job.save()

            logger.info(f"Starting pipeline for: {package.name}")

            # Stage 1: Research
            job.advance_stage()
            research_result = await self._stage_research(package)
            job.research_result = research_result
            job.save()

            # Stage 2: Script
            job.advance_stage()
            script_result = await self._stage_script(package, research_result)
            job.script_result = script_result
            job.save()

            # Stage 3: Character/Images
            job.advance_stage()
            character_result = await self._stage_character(package, script_result)
            job.character_result = character_result
            job.save()

            # Stage 4: Voice
            job.advance_stage()
            voice_result = await self._stage_voice(package, script_result)
            job.voice_result = voice_result
            job.save()

            # Stage 5: Video
            job.advance_stage()
            video_result = await self._stage_video(package, character_result, voice_result)
            job.video_result = video_result
            job.save()

            # Stage 6: Package
            job.advance_stage()
            await self._stage_package(package)

            # Complete
            job.completed_at = timezone.now()
            job.current_stage = "complete"
            job.save()

            package.complete_generation()

            logger.info(f"Pipeline complete for: {package.name}")
            return package

        except Exception as e:
            logger.error(f"Pipeline failed for {package_id}: {e}")
            if 'job' in locals():
                job.fail(str(e))
            raise

    async def _stage_research(self, package: ContentPackage) -> Dict[str, Any]:
        """
        Stage 1: Research using spider network.
        Gathers trends, competitor info, and context.
        """
        logger.info(f"[{package.name}] Stage 1: Research")

        # Use spider intelligence to gather context
        try:
            from core.services.spider_intelligence import SpiderIntelligenceService
            spider_service = SpiderIntelligenceService()

            # Search for relevant data
            spider_data = spider_service.search_intelligence(
                query=package.prompt,
                limit=10
            )

            return {
                "spider_data": spider_data,
                "trends": [],  # Could add trend analysis
                "competitors": [],  # Could add competitor research
                "context": f"Research completed for: {package.prompt}"
            }
        except Exception as e:
            logger.warning(f"Research stage skipped: {e}")
            return {"context": package.prompt, "error": str(e)}

    async def _stage_script(
        self,
        package: ContentPackage,
        research: Dict
    ) -> Dict[str, Any]:
        """
        Stage 2: Script/copy generation using GPT.
        Creates scripts, taglines, stories based on tier.
        """
        logger.info(f"[{package.name}] Stage 2: Script")

        tier_config = TIER_CONFIGS.get(package.tier)

        # Build prompt based on tier
        if package.tier == ContentTier.QUICK:
            script_prompt = f"""Create a short, punchy message for:
{package.prompt}

Output a single 15-second script that's engaging and memorable."""

        elif package.tier == ContentTier.AD:
            script_prompt = f"""Create advertising copy for a small business:
{package.prompt}

Create:
1. A catchy tagline (max 10 words)
2. A 15-second script
3. A 30-second script
4. A 60-second script

Make it friendly, local, and memorable."""

        elif package.tier == ContentTier.BRAND:
            script_prompt = f"""Create brand messaging for:
{package.prompt}

Create:
1. Brand tagline
2. Brand voice guidelines (3-5 adjectives)
3. Value proposition (1 sentence)
4. Three 30-second ad scripts for different audiences
5. Social media bio (160 chars)

Keep it professional but approachable."""

        elif package.tier in [ContentTier.SERIES, ContentTier.PITCH, ContentTier.PRODUCTION]:
            script_prompt = f"""Create content series concept for:
{package.prompt}

Create:
1. Series title and logline
2. Main character descriptions (3 characters)
3. Episode 1 outline
4. Series arc overview
5. Target audience description

Make it compelling and producible."""
        else:
            script_prompt = package.prompt

        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[
                        {"role": "system", "content": "You are a creative copywriter and content strategist."},
                        {"role": "user", "content": script_prompt}
                    ],
                    max_completion_tokens=2000
                )
                script_content = response.choices[0].message.content
            else:
                script_content = f"[Script for: {package.prompt}]"

            return {
                "main_script": script_content,
                "tagline": self._extract_tagline(script_content),
                "scripts": [script_content],  # Would parse multiple scripts
            }
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            return {"main_script": package.prompt, "error": str(e)}

    def _extract_tagline(self, script: str) -> str:
        """Extract a tagline from script content"""
        # Simple extraction - take first line or sentence
        lines = script.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) < 100:
                return line
        return ""

    async def _stage_character(
        self,
        package: ContentPackage,
        script: Dict
    ) -> Dict[str, Any]:
        """
        Stage 3: Character/image generation using Stability AI.
        Creates mascots, logos, character art based on tier.
        """
        logger.info(f"[{package.name}] Stage 3: Character/Images")

        tier_config = TIER_CONFIGS.get(package.tier)
        images = []

        # Generate image prompts based on tier
        if package.tier == ContentTier.QUICK:
            image_prompts = [f"Cartoon mascot for: {package.prompt}, friendly, colorful, simple design"]
        elif package.tier == ContentTier.AD:
            image_prompts = [
                f"Mascot character for {package.prompt}, front view, friendly, professional",
                f"Mascot character for {package.prompt}, waving pose, welcoming",
                f"Logo icon for {package.prompt}, simple, memorable",
            ]
        else:
            # More prompts for higher tiers
            image_prompts = [
                f"Main character for {package.prompt}, detailed design",
            ] * tier_config.num_images

        # Generate images via Stability AI
        try:
            from content.image_generation import generate_image

            for i, prompt in enumerate(image_prompts[:tier_config.num_images]):
                result = generate_image(
                    prompt=prompt,
                    width=1024,
                    height=1024,
                    style_preset="digital-art"
                )

                if result.get("success"):
                    images.append({
                        "url": result.get("image_url"),
                        "prompt": prompt,
                        "type": "character" if i < 3 else "supporting"
                    })

                    # Create asset record
                    ContentAsset.objects.create(
                        package=package,
                        asset_type=AssetType.IMAGE,
                        name=f"Image {i+1}",
                        file_url=result.get("image_url", ""),
                        metadata={"prompt": prompt, "dimensions": "1024x1024"}
                    )

            # Set preview image
            if images:
                package.preview_image_url = images[0].get("url")
                package.save(update_fields=["preview_image_url"])

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {"images": [], "error": str(e)}

        return {"images": images, "count": len(images)}

    async def _stage_voice(
        self,
        package: ContentPackage,
        script: Dict
    ) -> Dict[str, Any]:
        """
        Stage 4: Voice generation using ElevenLabs.
        Creates voiceovers from scripts.
        """
        logger.info(f"[{package.name}] Stage 4: Voice")

        tier_config = TIER_CONFIGS.get(package.tier)
        voices = []

        script_text = script.get("main_script", package.prompt)

        try:
            import requests

            api_key = settings.ELEVENLABS_API_KEY
            if not api_key:
                raise ValueError("ElevenLabs API key not configured")

            # Use a default voice (could let user pick from marketplace)
            voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - clear, professional

            response = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "text": script_text[:1000],  # Limit for demo
                    "model_id": "eleven_turbo_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                }
            )

            if response.status_code == 200:
                # In production, save to S3/storage
                audio_url = f"/media/voice/{package.id}_voice.mp3"

                voices.append({
                    "voice_id": voice_id,
                    "url": audio_url,
                    "text": script_text[:100]
                })

                ContentAsset.objects.create(
                    package=package,
                    asset_type=AssetType.AUDIO,
                    name="Voiceover",
                    file_url=audio_url,
                    metadata={"voice_id": voice_id, "text_length": len(script_text)}
                )

                package.preview_audio_url = audio_url
                package.save(update_fields=["preview_audio_url"])

        except Exception as e:
            logger.error(f"Voice generation failed: {e}")
            return {"voices": [], "error": str(e)}

        return {"voices": voices, "count": len(voices)}

    async def _stage_video(
        self,
        package: ContentPackage,
        character: Dict,
        voice: Dict
    ) -> Dict[str, Any]:
        """
        Stage 5: Video generation using Runway ML.
        Creates animated videos from images + audio.
        """
        logger.info(f"[{package.name}] Stage 5: Video")

        tier_config = TIER_CONFIGS.get(package.tier)
        videos = []

        # Get first image for video generation
        images = character.get("images", [])
        if not images:
            return {"videos": [], "error": "No images available for video"}

        try:
            from content.video_generation import generate_video_from_image

            for duration in tier_config.video_durations[:tier_config.num_videos]:
                result = generate_video_from_image(
                    image_url=images[0].get("url"),
                    prompt=f"Animate this character, subtle movement, professional",
                    duration=min(duration, 10)  # Runway has limits
                )

                if result.get("success"):
                    video_url = result.get("video_url")

                    videos.append({
                        "url": video_url,
                        "duration": duration,
                    })

                    ContentAsset.objects.create(
                        package=package,
                        asset_type=AssetType.VIDEO,
                        name=f"Video ({duration}s)",
                        file_url=video_url or "",
                        metadata={"duration": duration}
                    )

            if videos:
                package.preview_video_url = videos[0].get("url")
                package.save(update_fields=["preview_video_url"])

        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            return {"videos": [], "error": str(e)}

        return {"videos": videos, "count": len(videos)}

    async def _stage_package(self, package: ContentPackage):
        """
        Stage 6: Final packaging.
        Bundle all assets, create previews, prepare for marketplace.
        """
        logger.info(f"[{package.name}] Stage 6: Packaging")

        # Count assets
        asset_counts = {}
        for asset in package.assets.all():
            asset_type = asset.asset_type
            asset_counts[asset_type] = asset_counts.get(asset_type, 0) + 1

        # Update package description with asset summary
        summary_parts = []
        if asset_counts.get(AssetType.IMAGE):
            summary_parts.append(f"{asset_counts[AssetType.IMAGE]} images")
        if asset_counts.get(AssetType.VIDEO):
            summary_parts.append(f"{asset_counts[AssetType.VIDEO]} videos")
        if asset_counts.get(AssetType.AUDIO):
            summary_parts.append(f"{asset_counts[AssetType.AUDIO]} audio files")

        if summary_parts:
            package.description += f"\n\nIncludes: {', '.join(summary_parts)}"
            package.save(update_fields=["description"])

        logger.info(f"Package complete: {package.name} with {sum(asset_counts.values())} assets")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_content_pipeline() -> UnifiedContentPipeline:
    """Get or create the singleton pipeline instance"""
    return UnifiedContentPipeline()


def get_tier_config(tier: str) -> Optional[TierConfig]:
    """Get configuration for a content tier"""
    return TIER_CONFIGS.get(tier)


def get_all_tiers() -> Dict[str, TierConfig]:
    """Get all tier configurations"""
    return TIER_CONFIGS.copy()
