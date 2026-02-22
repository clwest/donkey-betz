"""
Content Production Orchestrator
==============================

Session 812: Orchestrates complete content production with automatic asset creation.

When creating content (blogs, podcasts, videos), multiple agents need to work together:
- ContentWriterAgent creates the written content
- ImageAgent creates hero images, thumbnails, graphics
- SEOOptimizerAgent optimizes for search
- SocialMediaAgent creates promotional posts
- AudioAgent creates voiceovers (for videos/podcasts)
- VideoAgent creates promotional videos

This orchestrator:
1. Defines "production teams" for each content type
2. Coordinates sequential/parallel agent execution
3. Tracks asset completion
4. Returns a complete content package

Usage:
    from core.services.content_production_orchestrator import ContentProductionOrchestrator

    orchestrator = ContentProductionOrchestrator(user=request.user)

    # Create a complete blog post with all assets
    result = orchestrator.produce_content(
        content_type='blog_post',
        topic='AI trends for 2026',
        context={'tone': 'professional', 'target_audience': 'tech entrepreneurs'}
    )

    # result includes: blog content, hero image, thumbnails, SEO metadata, social posts
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from django.utils import timezone

logger = logging.getLogger(__name__)


class AssetStatus(Enum):
    """Status of an individual asset in production."""
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'
    SKIPPED = 'skipped'


class ContentType(Enum):
    """Supported content types."""
    BLOG_POST = 'blog_post'
    PODCAST = 'podcast'
    VIDEO = 'video'
    ARTICLE = 'article'
    SOCIAL_CAMPAIGN = 'social_campaign'
    NEWSLETTER = 'newsletter'


@dataclass
class AssetRequirement:
    """Definition of a required asset in a content production."""
    asset_type: str  # e.g., 'hero_image', 'thumbnail', 'seo_metadata'
    agent_name: str  # Agent responsible for creating this asset
    task_template: str  # Task description template
    depends_on: List[str] = field(default_factory=list)  # Asset types this depends on
    optional: bool = False  # If True, production continues even if this fails
    parallel_group: int = 0  # Assets with same group can run in parallel
    is_persona_agent: bool = False  # If True, this is a persona agent (advisory via LLM)
    advice_type: str = 'content_strategy'  # Type of advice for persona agents


@dataclass
class AssetResult:
    """Result of creating a single asset."""
    asset_type: str
    agent_name: str
    status: AssetStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: int = 0
    celery_task_id: Optional[str] = None


@dataclass
class ProductionResult:
    """Complete result of a content production."""
    production_id: str
    content_type: str
    topic: str
    status: str  # 'completed', 'partial', 'failed'
    assets: Dict[str, AssetResult] = field(default_factory=dict)
    total_execution_time_ms: int = 0
    errors: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'production_id': self.production_id,
            'content_type': self.content_type,
            'topic': self.topic,
            'status': self.status,
            'assets': {
                k: {
                    'asset_type': v.asset_type,
                    'agent_name': v.agent_name,
                    'status': v.status.value,
                    'data': v.data,
                    'error': v.error,
                    'execution_time_ms': v.execution_time_ms,
                }
                for k, v in self.assets.items()
            },
            'total_execution_time_ms': self.total_execution_time_ms,
            'errors': self.errors,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


# Production team definitions for each content type
PRODUCTION_TEAMS = {
    ContentType.BLOG_POST: {
        'name': 'Blog Production Team',
        'description': 'Creates complete blog posts with images, SEO, and persona advisory input',
        'assets': [
            # Phase 0: Strategy Advisory (Persona Agents)
            AssetRequirement(
                asset_type='strategy_advice',
                agent_name='Content Strategy Planner',
                task_template='Provide strategic advice for a blog post about: {topic}',
                depends_on=[],
                optional=True,
                parallel_group=0,
                is_persona_agent=True,
                advice_type='content_strategy'
            ),
            # Phase 1: Research (if needed)
            AssetRequirement(
                asset_type='research',
                agent_name='ResearchAgent',
                task_template='Research the topic: {topic}. Focus on recent trends, statistics, and expert opinions. {strategy_advice_summary}',
                depends_on=['strategy_advice'],
                optional=True,
                parallel_group=1
            ),
            # Phase 2: Content creation
            AssetRequirement(
                asset_type='blog_content',
                agent_name='ContentWriterAgent',
                task_template='Write a {tone} blog post about: {topic}. Target audience: {target_audience}. {strategy_advice_summary}',
                depends_on=['research'],
                optional=False,
                parallel_group=2
            ),
            # Phase 3: Visual assets (can run in parallel)
            AssetRequirement(
                asset_type='hero_image',
                agent_name='ImageAgent',
                task_template='Create a hero image for a blog post titled: "{blog_title}". The blog is about {topic}. Style: professional, modern, relevant to the content.',
                depends_on=['blog_content'],
                optional=False,
                parallel_group=3
            ),
            AssetRequirement(
                asset_type='thumbnail_image',
                agent_name='ImageAgent',
                task_template='Create a social media thumbnail (1200x630px) for a blog post titled: "{blog_title}". Make it eye-catching and shareable.',
                depends_on=['blog_content'],
                optional=True,
                parallel_group=3
            ),
            AssetRequirement(
                asset_type='inline_graphics',
                agent_name='ImageAgent',
                task_template='Create 2-3 inline graphics/diagrams for a blog post about: {topic}. These should illustrate key concepts mentioned in the post.',
                depends_on=['blog_content'],
                optional=True,
                parallel_group=3
            ),
            # Phase 4: Optimization
            AssetRequirement(
                asset_type='seo_metadata',
                agent_name='SEOOptimizerAgent',
                task_template='Optimize SEO for a blog post titled: "{blog_title}". Topic: {topic}. Generate meta description, keywords, schema markup.',
                depends_on=['blog_content'],
                optional=True,
                parallel_group=4
            ),
            # Phase 5: Marketing Advisory (Persona Agent)
            AssetRequirement(
                asset_type='marketing_advice',
                agent_name='Digital Marketing Strategist',
                task_template='Provide marketing advice for promoting blog: "{blog_title}"',
                depends_on=['blog_content'],
                optional=True,
                parallel_group=4,
                is_persona_agent=True,
                advice_type='marketing_angle'
            ),
            # Phase 6: Promotion (informed by marketing advice)
            AssetRequirement(
                asset_type='social_posts',
                agent_name='SocialMediaAgent',
                task_template='Create social media posts to promote a blog titled: "{blog_title}". Create versions for Twitter, LinkedIn, and Facebook. {marketing_advice_summary}',
                depends_on=['blog_content', 'thumbnail_image', 'marketing_advice'],
                optional=True,
                parallel_group=5
            ),
        ]
    },

    ContentType.PODCAST: {
        'name': 'Podcast Production Team',
        'description': 'Creates complete podcast episodes with audio and marketing assets',
        'assets': [
            AssetRequirement(
                asset_type='research',
                agent_name='ResearchAgent',
                task_template='Research for podcast episode about: {topic}. Find interesting angles, statistics, and expert quotes.',
                depends_on=[],
                optional=True,
                parallel_group=0
            ),
            AssetRequirement(
                asset_type='podcast_script',
                agent_name='ContentWriterAgent',
                task_template='Write a podcast script about: {topic}. Include intro hook, 3-5 segments with talking points, transitions, and outro.',
                depends_on=['research'],
                optional=False,
                parallel_group=1
            ),
            AssetRequirement(
                asset_type='podcast_audio',
                agent_name='AudioAgent',
                task_template='Generate voiceover for podcast episode using script. Use a {voice_style} voice appropriate for {target_audience}.',
                depends_on=['podcast_script'],
                optional=True,  # Session 1068: audio optional so production doesn't hard-fail
                parallel_group=2
            ),
            AssetRequirement(
                asset_type='episode_artwork',
                agent_name='ImageAgent',
                task_template='Create podcast episode artwork for: "{episode_title}". Square format (1400x1400), eye-catching, podcast-appropriate.',
                depends_on=['podcast_script'],
                optional=False,
                parallel_group=2
            ),
            AssetRequirement(
                asset_type='promo_video',
                agent_name='VideoAgent',
                task_template='Create a 30-60 second promotional video for podcast episode: "{episode_title}". Use audiogram style with waveform visualization.',
                depends_on=['podcast_audio', 'episode_artwork'],
                optional=True,
                parallel_group=3
            ),
            AssetRequirement(
                asset_type='show_notes',
                agent_name='ContentWriterAgent',
                task_template='Create show notes for podcast episode: "{episode_title}". Include timestamps, key points, resources mentioned, and links.',
                depends_on=['podcast_script'],
                optional=True,
                parallel_group=2
            ),
            AssetRequirement(
                asset_type='social_posts',
                agent_name='SocialMediaAgent',
                task_template='Create social media posts to promote podcast episode: "{episode_title}". Include audiogram suggestions and hashtags.',
                depends_on=['podcast_script', 'episode_artwork'],
                optional=True,
                parallel_group=4
            ),
        ]
    },

    ContentType.VIDEO: {
        'name': 'Video Production Team',
        'description': 'Creates complete video content with scripts, visuals, and marketing',
        'assets': [
            AssetRequirement(
                asset_type='research',
                agent_name='ResearchAgent',
                task_template='Research for video about: {topic}. Find visual examples, statistics, and compelling hooks.',
                depends_on=[],
                optional=True,
                parallel_group=0
            ),
            AssetRequirement(
                asset_type='video_script',
                agent_name='ContentWriterAgent',
                task_template='Write a video script about: {topic}. Include hook, scene descriptions, narration, and b-roll suggestions.',
                depends_on=['research'],
                optional=False,
                parallel_group=1
            ),
            AssetRequirement(
                asset_type='video_voiceover',
                agent_name='AudioAgent',
                task_template='Generate voiceover for video narration. Use a {voice_style} voice that engages {target_audience}.',
                depends_on=['video_script'],
                optional=True,  # Session 1068: audio optional so production doesn't hard-fail
                parallel_group=2
            ),
            AssetRequirement(
                asset_type='video_thumbnail',
                agent_name='ImageAgent',
                task_template='Create a YouTube thumbnail (1280x720) for video: "{video_title}". Make it click-worthy with bold text and compelling imagery.',
                depends_on=['video_script'],
                optional=False,
                parallel_group=2
            ),
            AssetRequirement(
                asset_type='video_graphics',
                agent_name='ImageAgent',
                task_template='Create motion graphics templates for video about: {topic}. Include lower thirds, transitions, and title cards.',
                depends_on=['video_script'],
                optional=True,
                parallel_group=2
            ),
            AssetRequirement(
                asset_type='seo_metadata',
                agent_name='SEOOptimizerAgent',
                task_template='Optimize YouTube SEO for video: "{video_title}". Generate description, tags, and timestamps.',
                depends_on=['video_script'],
                optional=True,
                parallel_group=3
            ),
            AssetRequirement(
                asset_type='social_posts',
                agent_name='SocialMediaAgent',
                task_template='Create social media posts to promote video: "{video_title}". Create teaser posts for multiple platforms.',
                depends_on=['video_script', 'video_thumbnail'],
                optional=True,
                parallel_group=4
            ),
        ]
    },

    ContentType.NEWSLETTER: {
        'name': 'Newsletter Production Team',
        'description': 'Creates complete newsletters with content and graphics',
        'assets': [
            AssetRequirement(
                asset_type='research',
                agent_name='ResearchAgent',
                task_template='Research latest news and insights about: {topic}. Focus on actionable, subscriber-valuable content.',
                depends_on=[],
                optional=True,
                parallel_group=0
            ),
            AssetRequirement(
                asset_type='newsletter_content',
                agent_name='ContentWriterAgent',
                task_template='Write an engaging newsletter about: {topic}. Include subject line, preview text, sections, and CTA.',
                depends_on=['research'],
                optional=False,
                parallel_group=1
            ),
            AssetRequirement(
                asset_type='header_image',
                agent_name='ImageAgent',
                task_template='Create a newsletter header image for topic: {topic}. Style: clean, professional, email-friendly (600px wide).',
                depends_on=['newsletter_content'],
                optional=True,
                parallel_group=2
            ),
            AssetRequirement(
                asset_type='section_graphics',
                agent_name='ImageAgent',
                task_template='Create 2-3 small graphics for newsletter sections about: {topic}. Keep them simple and email-safe.',
                depends_on=['newsletter_content'],
                optional=True,
                parallel_group=2
            ),
        ]
    },

    ContentType.SOCIAL_CAMPAIGN: {
        'name': 'Social Campaign Team',
        'description': 'Creates complete social media campaigns across platforms',
        'assets': [
            AssetRequirement(
                asset_type='campaign_strategy',
                agent_name='ContentStrategyAgent',
                task_template='Create a social media campaign strategy for: {topic}. Define goals, key messages, and posting schedule.',
                depends_on=[],
                optional=False,
                parallel_group=0
            ),
            AssetRequirement(
                asset_type='campaign_copy',
                agent_name='ContentWriterAgent',
                task_template='Write social media copy for campaign about: {topic}. Create posts for Twitter, LinkedIn, Instagram, and Facebook.',
                depends_on=['campaign_strategy'],
                optional=False,
                parallel_group=1
            ),
            AssetRequirement(
                asset_type='campaign_visuals',
                agent_name='ImageAgent',
                task_template='Create social media visuals for campaign: {topic}. Create platform-specific sizes: Twitter (1200x675), Instagram (1080x1080), LinkedIn (1200x627).',
                depends_on=['campaign_strategy'],
                optional=False,
                parallel_group=1
            ),
            AssetRequirement(
                asset_type='video_shorts',
                agent_name='VideoAgent',
                task_template='Create short video clips (15-30 seconds) for social campaign about: {topic}. Optimize for TikTok/Reels format.',
                depends_on=['campaign_strategy'],
                optional=True,
                parallel_group=2
            ),
        ]
    },
}


class ContentProductionOrchestrator:
    """
    Orchestrates complete content production across multiple agents.

    This orchestrator coordinates the creation of complete content packages,
    automatically triggering all necessary agents and tracking asset completion.
    """

    def __init__(self, user=None):
        """Initialize the orchestrator."""
        self.user = user
        self._router = None

    @property
    def router(self):
        """Lazy-load the agent router."""
        if self._router is None:
            from core.agent_router import AgentRouter
            self._router = AgentRouter(user=self.user)
        return self._router

    def produce_content(
        self,
        content_type: str,
        topic: str,
        context: Optional[Dict[str, Any]] = None,
        skip_assets: Optional[List[str]] = None,
        async_mode: bool = False
    ) -> ProductionResult:
        """
        Produce a complete content package.

        Args:
            content_type: Type of content (blog_post, podcast, video, etc.)
            topic: Main topic/subject for the content
            context: Additional context (tone, target_audience, research, etc.)
            skip_assets: List of asset types to skip
            async_mode: If True, queue production as Celery task

        Returns:
            ProductionResult with all created assets
        """
        context = context or {}
        skip_assets = skip_assets or []

        # Convert string to enum
        try:
            content_enum = ContentType(content_type)
        except ValueError:
            return ProductionResult(
                production_id=str(uuid.uuid4()),
                content_type=content_type,
                topic=topic,
                status='failed',
                errors=[f"Unknown content type: {content_type}. Available: {[c.value for c in ContentType]}"]
            )

        # Get production team
        team = PRODUCTION_TEAMS.get(content_enum)
        if not team:
            return ProductionResult(
                production_id=str(uuid.uuid4()),
                content_type=content_type,
                topic=topic,
                status='failed',
                errors=[f"No production team defined for: {content_type}"]
            )

        production_id = str(uuid.uuid4())
        logger.info(f"🎬 Starting content production {production_id}: {content_type} - {topic}")

        if async_mode:
            return self._produce_async(production_id, content_type, topic, context, skip_assets)

        return self._produce_sync(production_id, content_enum, topic, context, skip_assets, team)

    def _produce_sync(
        self,
        production_id: str,
        content_type: ContentType,
        topic: str,
        context: Dict[str, Any],
        skip_assets: List[str],
        team: Dict[str, Any]
    ) -> ProductionResult:
        """Execute production synchronously."""
        import time

        result = ProductionResult(
            production_id=production_id,
            content_type=content_type.value,
            topic=topic,
            status='in_progress',
            started_at=timezone.now()
        )

        start_time = time.time()

        # Build context with defaults
        production_context = {
            'topic': topic,
            'tone': context.get('tone', 'professional'),
            'target_audience': context.get('target_audience', 'general audience'),
            'voice_style': context.get('voice_style', 'professional'),
            **context
        }

        # Sort assets by parallel group for execution order
        assets = team['assets']
        completed_assets: Dict[str, AssetResult] = {}

        # Group assets by parallel_group
        groups: Dict[int, List[AssetRequirement]] = {}
        for asset in assets:
            if asset.asset_type in skip_assets:
                completed_assets[asset.asset_type] = AssetResult(
                    asset_type=asset.asset_type,
                    agent_name=asset.agent_name,
                    status=AssetStatus.SKIPPED
                )
                continue

            group = asset.parallel_group
            if group not in groups:
                groups[group] = []
            groups[group].append(asset)

        # Execute groups in order
        for group_num in sorted(groups.keys()):
            group_assets = groups[group_num]

            logger.info(f"📦 Production {production_id}: Executing group {group_num} ({len(group_assets)} assets)")

            # Check dependencies and execute eligible assets
            for asset in group_assets:
                # Check if dependencies are met
                deps_met = all(
                    dep in completed_assets and completed_assets[dep].status == AssetStatus.COMPLETED
                    for dep in asset.depends_on
                    if dep not in skip_assets
                )

                if not deps_met:
                    if asset.optional:
                        completed_assets[asset.asset_type] = AssetResult(
                            asset_type=asset.asset_type,
                            agent_name=asset.agent_name,
                            status=AssetStatus.SKIPPED,
                            error='Dependencies not met'
                        )
                        continue
                    else:
                        result.errors.append(f"Dependencies not met for required asset: {asset.asset_type}")
                        completed_assets[asset.asset_type] = AssetResult(
                            asset_type=asset.asset_type,
                            agent_name=asset.agent_name,
                            status=AssetStatus.FAILED,
                            error='Dependencies not met'
                        )
                        continue

                # Execute the asset creation
                asset_result = self._create_asset(
                    asset=asset,
                    production_context=production_context,
                    completed_assets=completed_assets
                )
                completed_assets[asset.asset_type] = asset_result

                # Update production context with results from this asset
                if asset_result.status == AssetStatus.COMPLETED and asset_result.data:
                    self._update_context_from_asset(production_context, asset_result)

        # Calculate final status
        required_failed = any(
            not assets[i].optional and completed_assets.get(assets[i].asset_type, AssetResult(
                asset_type='', agent_name='', status=AssetStatus.FAILED
            )).status == AssetStatus.FAILED
            for i in range(len(assets))
            if assets[i].asset_type not in skip_assets
        )

        all_completed = all(
            completed_assets.get(a.asset_type, AssetResult(
                asset_type='', agent_name='', status=AssetStatus.PENDING
            )).status in [AssetStatus.COMPLETED, AssetStatus.SKIPPED]
            for a in assets
            if a.asset_type not in skip_assets
        )

        if required_failed:
            result.status = 'failed'
        elif all_completed:
            result.status = 'completed'
        else:
            result.status = 'partial'

        result.assets = completed_assets
        result.completed_at = timezone.now()
        result.total_execution_time_ms = int((time.time() - start_time) * 1000)

        # Record production to database
        self._record_production(result)

        logger.info(
            f"🎬 Production {production_id} {result.status}: "
            f"{sum(1 for a in completed_assets.values() if a.status == AssetStatus.COMPLETED)}/{len(assets)} assets completed "
            f"({result.total_execution_time_ms}ms)"
        )

        return result

    def _create_asset(
        self,
        asset: AssetRequirement,
        production_context: Dict[str, Any],
        completed_assets: Dict[str, AssetResult]
    ) -> AssetResult:
        """Create a single asset using the designated agent or persona advisor."""
        import time

        agent_type = "persona" if asset.is_persona_agent else "core"
        logger.info(f"   🔧 Creating {asset.asset_type} via {asset.agent_name} ({agent_type})")

        start_time = time.time()

        try:
            # Build task from template
            task = self._build_task_from_template(
                template=asset.task_template,
                context=production_context,
                completed_assets=completed_assets
            )

            # Handle persona agents differently - use PersonaAdvisorService
            if asset.is_persona_agent:
                return self._create_persona_advisory_asset(
                    asset=asset,
                    task=task,
                    production_context=production_context,
                    start_time=start_time
                )

            # Get context for the core agent
            agent_context = self._build_agent_context(
                asset=asset,
                production_context=production_context,
                completed_assets=completed_assets
            )

            # Route to the core agent
            agent_result = self.router.route(
                agent_name=asset.agent_name,
                task=task,
                context=agent_context
            )

            execution_time = int((time.time() - start_time) * 1000)

            if agent_result.success:
                logger.info(f"   ✅ {asset.asset_type} completed ({execution_time}ms)")
                return AssetResult(
                    asset_type=asset.asset_type,
                    agent_name=asset.agent_name,
                    status=AssetStatus.COMPLETED,
                    data=agent_result.data,
                    execution_time_ms=execution_time
                )
            else:
                logger.warning(f"   ❌ {asset.asset_type} failed: {agent_result.error}")
                return AssetResult(
                    asset_type=asset.asset_type,
                    agent_name=asset.agent_name,
                    status=AssetStatus.FAILED,
                    error=agent_result.error,
                    execution_time_ms=execution_time
                )

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"   ❌ {asset.asset_type} error: {e}")
            return AssetResult(
                asset_type=asset.asset_type,
                agent_name=asset.agent_name,
                status=AssetStatus.FAILED,
                error=str(e),
                execution_time_ms=execution_time
            )

    def _create_persona_advisory_asset(
        self,
        asset: AssetRequirement,
        task: str,
        production_context: Dict[str, Any],
        start_time: float
    ) -> AssetResult:
        """
        Create an advisory asset from a persona agent.

        Uses PersonaAdvisorService to get LLM-generated advice enriched
        with spider data from the persona's domain.
        """
        import time

        try:
            from core.services.persona_advisor_service import get_persona_advisor_service

            advisor_service = get_persona_advisor_service()

            # Get advice from persona agent
            advice_result = advisor_service.get_advice(
                persona_name=asset.agent_name,
                topic=production_context.get('topic', ''),
                advice_type=asset.advice_type,
                context={
                    'content_type': production_context.get('content_type', 'content'),
                    'tone': production_context.get('tone', 'professional'),
                    'target_audience': production_context.get('target_audience', 'general'),
                }
            )

            execution_time = int((time.time() - start_time) * 1000)

            if advice_result.success:
                logger.info(
                    f"   ✅ {asset.asset_type} completed ({execution_time}ms) "
                    f"[{advice_result.spider_data_used} spider items used]"
                )
                return AssetResult(
                    asset_type=asset.asset_type,
                    agent_name=asset.agent_name,
                    status=AssetStatus.COMPLETED,
                    data={
                        'advice': advice_result.advice,
                        'structured_advice': advice_result.structured_advice,
                        'spider_data_used': advice_result.spider_data_used,
                        'advice_type': asset.advice_type,
                    },
                    execution_time_ms=execution_time
                )
            else:
                logger.warning(f"   ❌ {asset.asset_type} failed: {advice_result.error}")
                return AssetResult(
                    asset_type=asset.asset_type,
                    agent_name=asset.agent_name,
                    status=AssetStatus.FAILED,
                    error=advice_result.error,
                    execution_time_ms=execution_time
                )

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"   ❌ Persona advisory error for {asset.agent_name}: {e}")
            return AssetResult(
                asset_type=asset.asset_type,
                agent_name=asset.agent_name,
                status=AssetStatus.FAILED,
                error=str(e),
                execution_time_ms=execution_time
            )

    def _build_task_from_template(
        self,
        template: str,
        context: Dict[str, Any],
        completed_assets: Dict[str, AssetResult]
    ) -> str:
        """Build task string from template with context substitution."""
        # Start with production context
        substitutions = {**context}

        # Add titles from completed assets
        for asset_type, asset_result in completed_assets.items():
            if asset_result.status == AssetStatus.COMPLETED and asset_result.data:
                data = asset_result.data

                # Extract title from various content types
                if asset_type == 'blog_content':
                    content = data.get('content', {})
                    substitutions['blog_title'] = (
                        content.get('title') or
                        content.get('headline') or
                        context.get('topic', 'Untitled')
                    )
                elif asset_type == 'podcast_script':
                    content = data.get('content', {})
                    substitutions['episode_title'] = (
                        content.get('title') or
                        context.get('topic', 'Untitled Episode')
                    )
                elif asset_type == 'video_script':
                    content = data.get('content', {})
                    substitutions['video_title'] = (
                        content.get('title') or
                        context.get('topic', 'Untitled Video')
                    )
                elif asset_type == 'newsletter_content':
                    content = data.get('content', {})
                    substitutions['newsletter_title'] = (
                        content.get('subject_line') or
                        context.get('topic', 'Newsletter')
                    )

        # Perform substitution
        try:
            return template.format(**substitutions)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            # Return template with available substitutions
            for key, value in substitutions.items():
                template = template.replace('{' + key + '}', str(value))
            return template

    def _build_agent_context(
        self,
        asset: AssetRequirement,
        production_context: Dict[str, Any],
        completed_assets: Dict[str, AssetResult]
    ) -> Dict[str, Any]:
        """Build context dict for agent execution."""
        context = {
            'production_id': production_context.get('production_id'),
            'topic': production_context.get('topic'),
            'tone': production_context.get('tone'),
            'target_audience': production_context.get('target_audience'),
        }

        # Add content type specific context
        if asset.agent_name == 'ContentWriterAgent':
            if asset.asset_type == 'blog_content':
                context['content_type'] = 'blog_post'
            elif asset.asset_type == 'podcast_script':
                context['content_type'] = 'podcast_script'
            elif asset.asset_type == 'video_script':
                context['content_type'] = 'video_script'
            elif asset.asset_type == 'newsletter_content':
                context['content_type'] = 'newsletter'
            elif asset.asset_type == 'show_notes':
                context['content_type'] = 'article'

            # Add research if available
            if 'research' in completed_assets:
                research_result = completed_assets['research']
                if research_result.status == AssetStatus.COMPLETED and research_result.data:
                    context['research'] = research_result.data.get('research', '')

        elif asset.agent_name == 'ImageAgent':
            # Pass relevant content for image context
            for dep in asset.depends_on:
                if dep in completed_assets and completed_assets[dep].status == AssetStatus.COMPLETED:
                    dep_data = completed_assets[dep].data
                    if dep_data:
                        context['source_content'] = dep_data.get('content', {})

        elif asset.agent_name == 'AudioAgent':
            # Pass script for voiceover
            for dep in ['podcast_script', 'video_script']:
                if dep in completed_assets and completed_assets[dep].status == AssetStatus.COMPLETED:
                    script_data = completed_assets[dep].data
                    if script_data:
                        context['script'] = script_data.get('content', {}).get('full_text', '')
                        break

        return context

    def _update_context_from_asset(
        self,
        production_context: Dict[str, Any],
        asset_result: AssetResult
    ) -> None:
        """Update production context with data from completed asset."""
        if not asset_result.data:
            return

        data = asset_result.data
        content = data.get('content', {})

        # Handle advisory assets - extract summary for subsequent phases
        if asset_result.asset_type.endswith('_advice'):
            advice_text = data.get('advice', '')
            structured = data.get('structured_advice', {})

            # Create a summary for injection into subsequent tasks
            summary_key = f"{asset_result.asset_type}_summary"

            if structured:
                # Extract key points from structured advice
                key_points = []
                for section, content_text in structured.items():
                    if content_text and len(str(content_text)) > 10:
                        # Take first line or first 100 chars
                        first_line = str(content_text).split('\n')[0][:100]
                        key_points.append(f"- {section.replace('_', ' ').title()}: {first_line}")

                if key_points:
                    production_context[summary_key] = (
                        f"\n\n[Advisory from {asset_result.agent_name}]\n" +
                        "\n".join(key_points[:5])
                    )
                else:
                    production_context[summary_key] = ""
            elif advice_text:
                # Just use first 200 chars of advice
                truncated = advice_text[:200] + "..." if len(advice_text) > 200 else advice_text
                production_context[summary_key] = (
                    f"\n\n[Advisory from {asset_result.agent_name}]: {truncated}"
                )
            else:
                production_context[summary_key] = ""

            logger.debug(f"   📋 Added {summary_key} to production context")
            return

        # Extract and store titles from content assets
        if asset_result.asset_type == 'blog_content':
            production_context['blog_title'] = content.get('title', production_context.get('topic'))
        elif asset_result.asset_type == 'podcast_script':
            production_context['episode_title'] = content.get('title', production_context.get('topic'))
        elif asset_result.asset_type == 'video_script':
            production_context['video_title'] = content.get('title', production_context.get('topic'))

    def _record_production(self, result: ProductionResult) -> None:
        """Record production to database for tracking."""
        try:
            from core.models_unified_system import AgentExecution, Agent

            # Find or create a pseudo-agent for the orchestrator
            orchestrator_agent, _ = Agent.objects.get_or_create(
                name='ContentProductionOrchestrator',
                defaults={
                    'role': 'Orchestrates complete content production across multiple agents',
                    'category': 'orchestration',
                    'is_active': True,
                }
            )

            AgentExecution.objects.create(
                agent=orchestrator_agent,
                task=f"Produce {result.content_type}: {result.topic}",
                input_data={
                    'production_id': result.production_id,
                    'content_type': result.content_type,
                    'topic': result.topic,
                },
                output_data=result.to_dict(),
                status='success' if result.status == 'completed' else 'partial' if result.status == 'partial' else 'failure',
                execution_time_ms=result.total_execution_time_ms,
                created_by=self.user,
            )

        except Exception as e:
            logger.warning(f"Failed to record production: {e}")

    def _produce_async(
        self,
        production_id: str,
        content_type: str,
        topic: str,
        context: Dict[str, Any],
        skip_assets: List[str]
    ) -> ProductionResult:
        """Queue production as async Celery task."""
        try:
            from core.tasks import produce_content_package

            task = produce_content_package.delay(
                production_id=production_id,
                content_type=content_type,
                topic=topic,
                context=context,
                skip_assets=skip_assets,
                user_id=self.user.id if self.user else None
            )

            return ProductionResult(
                production_id=production_id,
                content_type=content_type,
                topic=topic,
                status='queued',
                errors=[],
                started_at=timezone.now()
            )

        except Exception as e:
            return ProductionResult(
                production_id=production_id,
                content_type=content_type,
                topic=topic,
                status='failed',
                errors=[f"Failed to queue production: {e}"]
            )

    @classmethod
    def get_available_teams(cls) -> Dict[str, Dict[str, Any]]:
        """Get list of available production teams and their assets."""
        return {
            content_type.value: {
                'name': team['name'],
                'description': team['description'],
                'assets': [
                    {
                        'asset_type': a.asset_type,
                        'agent_name': a.agent_name,
                        'optional': a.optional,
                        'depends_on': a.depends_on,
                    }
                    for a in team['assets']
                ]
            }
            for content_type, team in PRODUCTION_TEAMS.items()
        }


# Singleton instance
_orchestrator_instance = None


def get_content_production_orchestrator(user=None) -> ContentProductionOrchestrator:
    """Get or create the ContentProductionOrchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None or user is not None:
        _orchestrator_instance = ContentProductionOrchestrator(user=user)
    return _orchestrator_instance


def produce_content(
    content_type: str,
    topic: str,
    context: Optional[Dict[str, Any]] = None,
    skip_assets: Optional[List[str]] = None,
    user=None,
    async_mode: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to produce content.

    Args:
        content_type: Type of content (blog_post, podcast, video, etc.)
        topic: Main topic for the content
        context: Additional context
        skip_assets: Assets to skip
        user: User making the request
        async_mode: Queue as Celery task

    Returns:
        Dict with production results
    """
    orchestrator = get_content_production_orchestrator(user=user)
    result = orchestrator.produce_content(
        content_type=content_type,
        topic=topic,
        context=context,
        skip_assets=skip_assets,
        async_mode=async_mode
    )
    return result.to_dict()


__all__ = [
    'ContentProductionOrchestrator',
    'get_content_production_orchestrator',
    'produce_content',
    'ProductionResult',
    'AssetResult',
    'AssetStatus',
    'ContentType',
    'PRODUCTION_TEAMS',
]
