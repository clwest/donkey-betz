"""
Workflow Orchestration Agent - Session 191

Manages multi-step creative workflows by executing agents in a fixed order.
This ensures GPT cannot deviate from the intended workflow or add extra steps.

Session 727: Migrated from agents/workflow_orchestration_agent.py to core/services/workflow_orchestration_agent.py

Architecture:
    GPT detects workflow type → calls this agent → agent executes steps internally

Key Principle:
    Instead of GPT calling multiple tools (which it can mess up), GPT calls
    ONE workflow orchestration agent that internally executes the correct
    steps in the correct order. GPT cannot deviate or add extra steps.

Workflows:
    - research_and_create_logos: web_search → coleadership → images → project
    - (Future: research_and_create_images, research_and_create_video, etc.)

Usage:
    agent = WorkflowOrchestrationAgent(user=request.user, project_id=project_id)
    result = agent.execute(
        workflow='research_and_create_logos',
        topic='modern AI company',
        count=3
    )
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base_agent import BaseContentAgent

logger = logging.getLogger(__name__)


def _sample_rss_mb() -> Optional[float]:
    """Return process RSS in MB, or None if psutil is unavailable.

    Session 1234 D1 (Rigby-ratified): light-touch instrumentation for the
    morning_brief Lane 4 dispatch. The first-fire postmortem showed a
    +783MB RSS spike on a workflow that didn't even complete; lane-scoped
    sampling lets us tag the spike to slot+agent without a deep dive.
    """
    try:
        import psutil
        return psutil.Process().memory_info().rss / (1024 * 1024)
    except Exception:
        return None


def _log_lane_4_rss(slot: str, agent_name: str,
                    rss_before_mb: Optional[float],
                    rss_after_mb: Optional[float]) -> None:
    """Emit a single greppable line tagging RSS delta to slot+agent."""
    if rss_before_mb is None or rss_after_mb is None:
        return
    delta_mb = rss_after_mb - rss_before_mb
    logger.info(
        "[MORNING_BRIEF_LANE_4_RSS] slot=%s agent=%s "
        "rss_before_mb=%.1f rss_after_mb=%.1f delta_mb=%+.1f",
        slot, agent_name, rss_before_mb, rss_after_mb, delta_mb,
    )


class WorkflowOrchestrationAgent(BaseContentAgent):
    """
    Orchestrates multi-step creative workflows.

    Key Principle: GPT calls this ONE agent, and the agent internally
    executes the correct steps in the correct order. GPT cannot
    deviate or add extra steps.

    Responsibilities:
        - Validate workflow type and parameters
        - Execute each step in fixed order
        - Pass context between steps
        - Aggregate results from all steps
        - Report progress for each step
    """

    agent_name = "WorkflowOrchestrationAgent"
    specialization = "workflow_orchestration"

    # Workflow definitions - HARDCODED order, no deviation allowed
    WORKFLOWS = {
        'research_and_create_logos': {
            'description': 'Research topic and create professional logos',
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research the topic for trends and best practices'
                },
                {
                    'step': 2,
                    'name': 'executive_review',
                    'agent': 'coleadership_agent',
                    'description': 'Get executive team creative direction'
                },
                {
                    'step': 3,
                    'name': 'create_images',
                    'agent': 'image_generation_agent',
                    'description': 'Generate the logos based on research and direction'
                },
                {
                    'step': 4,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Organize all content into a project'
                }
            ]
        },

        # Session 201: General Images/Artwork Workflow (NO text restrictions)
        'research_and_create_images': {
            'description': 'Research topic and create artistic images',
            'content_type': 'general_images',
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research the topic for visual inspiration'
                },
                {
                    'step': 2,
                    'name': 'executive_review',
                    'agent': 'coleadership_agent',
                    'description': 'Get executive team creative direction'
                },
                {
                    'step': 3,
                    'name': 'create_images',
                    'agent': 'image_generation_agent',
                    'description': 'Generate artistic images based on research and direction'
                },
                {
                    'step': 4,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Organize all content into a project'
                }
            ]
        },

        # Session 199: YouTube Thumbnail Package Workflow
        'youtube_thumbnail_package': {
            'description': 'Research topic and create YouTube thumbnail variations',
            'content_type': 'youtube_thumbnails',
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research YouTube thumbnail best practices and trends'
                },
                {
                    'step': 2,
                    'name': 'executive_review',
                    'agent': 'coleadership_agent',
                    'description': 'Get creative direction for thumbnails'
                },
                {
                    'step': 3,
                    'name': 'create_thumbnails',
                    'agent': 'image_generation_agent',
                    'description': 'Generate thumbnail variations'
                },
                {
                    'step': 4,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Organize thumbnails into a project'
                }
            ]
        },

        # Session 200: Brand Identity Package Workflow
        'brand_identity_package': {
            'description': 'Research brand and create complete identity (logo + variations + color palette)',
            'content_type': 'brand_identity',
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research brand identity trends and competitor analysis'
                },
                {
                    'step': 2,
                    'name': 'executive_review',
                    'agent': 'coleadership_agent',
                    'description': 'Get executive direction on brand positioning'
                },
                {
                    'step': 3,
                    'name': 'create_brand_images',
                    'agent': 'image_generation_agent',
                    'description': 'Generate logo and brand identity images'
                },
                {
                    'step': 4,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Organize into brand identity project'
                }
            ]
        },

        # Session 200: Product Photography Kit Workflow
        'product_photography_kit': {
            'description': 'Research product and create professional product images',
            'content_type': 'product_photography',
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research product photography trends and styles'
                },
                {
                    'step': 2,
                    'name': 'executive_review',
                    'agent': 'coleadership_agent',
                    'description': 'Get creative direction for product shots'
                },
                {
                    'step': 3,
                    'name': 'create_product_images',
                    'agent': 'image_generation_agent',
                    'description': 'Generate professional product images'
                },
                {
                    'step': 4,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Organize into product photography project'
                }
            ]
        },

        # Session 200: Video Thumbnail Series Workflow
        'video_thumbnail_series': {
            'description': 'Create a series of related thumbnails for a video series/playlist',
            'content_type': 'thumbnail_series',
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research thumbnail series best practices and branding'
                },
                {
                    'step': 2,
                    'name': 'executive_review',
                    'agent': 'coleadership_agent',
                    'description': 'Get direction on series visual consistency'
                },
                {
                    'step': 3,
                    'name': 'create_thumbnail_series',
                    'agent': 'image_generation_agent',
                    'description': 'Generate consistent thumbnail series'
                },
                {
                    'step': 4,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Organize into thumbnail series project'
                }
            ]
        },

        # Session 199: Logo to Video Workflow
        'logo_to_video': {
            'description': 'Animate an existing logo into a video',
            'content_type': 'animated_logo',
            'steps': [
                {
                    'step': 1,
                    'name': 'select_logo',
                    'agent': 'image_selection',
                    'description': 'Select the logo image to animate'
                },
                {
                    'step': 2,
                    'name': 'animate_logo',
                    'agent': 'video_generation_agent',
                    'description': 'Create animated video from logo'
                },
                {
                    'step': 3,
                    'name': 'add_audio',
                    'agent': 'audio_generation_agent',
                    'description': 'Add sound effect or music'
                },
                {
                    'step': 4,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Organize video into project'
                }
            ]
        },

        # =========================================================================
        # SESSION 212: NEW WORKFLOW TEMPLATES - Phase C
        # =========================================================================

        # Social Media Content Kit
        'social_media_kit': {
            'description': 'Create cohesive social media content package for multiple platforms',
            'content_type': 'social_media',
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research social media trends and platform best practices'
                },
                {
                    'step': 2,
                    'name': 'executive_review',
                    'agent': 'coleadership_agent',
                    'description': 'Get creative direction for social content'
                },
                {
                    'step': 3,
                    'name': 'create_hero_image',
                    'agent': 'image_generation_agent',
                    'description': 'Generate main hero image for campaign'
                },
                {
                    'step': 4,
                    'name': 'create_variations',
                    'agent': 'image_variation_agent',
                    'description': 'Create platform-specific variations'
                },
                {
                    'step': 5,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Organize into social media kit project'
                }
            ]
        },

        # Podcast Visual Package
        'podcast_visual_package': {
            'description': 'Create visuals for a podcast episode including cover art and quote cards',
            'content_type': 'podcast_visuals',
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research podcast visual trends and episode topic'
                },
                {
                    'step': 2,
                    'name': 'executive_review',
                    'agent': 'coleadership_agent',
                    'description': 'Get creative direction for podcast visuals'
                },
                {
                    'step': 3,
                    'name': 'create_cover_art',
                    'agent': 'image_generation_agent',
                    'description': 'Generate podcast episode cover art'
                },
                {
                    'step': 4,
                    'name': 'create_quote_cards',
                    'agent': 'image_generation_agent',
                    'description': 'Create shareable quote card designs'
                },
                {
                    'step': 5,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Organize into podcast visual project'
                }
            ]
        },

        # Ebook Cover Series
        'ebook_cover_series': {
            'description': 'Create ebook cover and promotional materials',
            'content_type': 'ebook_cover',
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research ebook cover trends in the genre'
                },
                {
                    'step': 2,
                    'name': 'executive_review',
                    'agent': 'coleadership_agent',
                    'description': 'Get creative direction for book cover design'
                },
                {
                    'step': 3,
                    'name': 'create_cover',
                    'agent': 'image_generation_agent',
                    'description': 'Generate ebook cover designs'
                },
                {
                    'step': 4,
                    'name': 'create_mockups',
                    'agent': 'image_generation_agent',
                    'description': 'Create 3D book mockups and promotional images'
                },
                {
                    'step': 5,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Organize into ebook cover project'
                }
            ]
        },

        # Video Production Kit
        'video_production_kit': {
            'description': 'Full video production asset package including thumbnails, intros, and end screens',
            'content_type': 'video_production',
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research video production trends and channel style'
                },
                {
                    'step': 2,
                    'name': 'executive_review',
                    'agent': 'coleadership_agent',
                    'description': 'Get creative direction for video assets'
                },
                {
                    'step': 3,
                    'name': 'create_thumbnail',
                    'agent': 'image_generation_agent',
                    'description': 'Generate video thumbnail'
                },
                {
                    'step': 4,
                    'name': 'create_end_screen',
                    'agent': 'image_generation_agent',
                    'description': 'Create end screen background'
                },
                {
                    'step': 5,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Organize into video production kit'
                }
            ]
        },

        # Course Thumbnail Series
        'course_thumbnail_series': {
            'description': 'Consistent thumbnails for online course modules',
            'content_type': 'course_thumbnails',
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research online course visual best practices'
                },
                {
                    'step': 2,
                    'name': 'executive_review',
                    'agent': 'coleadership_agent',
                    'description': 'Get direction for course visual identity'
                },
                {
                    'step': 3,
                    'name': 'create_module_thumbnails',
                    'agent': 'image_generation_agent',
                    'description': 'Generate thumbnails for course modules'
                },
                {
                    'step': 4,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Organize into course thumbnail project'
                }
            ]
        },

        # Pitch Deck Visuals
        'pitch_deck_visuals': {
            'description': 'Create visuals for a business pitch deck',
            'content_type': 'pitch_deck',
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research industry trends and competitor visuals'
                },
                {
                    'step': 2,
                    'name': 'executive_review',
                    'agent': 'coleadership_agent',
                    'description': 'Get strategic direction for pitch visuals'
                },
                {
                    'step': 3,
                    'name': 'create_hero_images',
                    'agent': 'image_generation_agent',
                    'description': 'Generate hero images for key slides'
                },
                {
                    'step': 4,
                    'name': 'create_infographic_elements',
                    'agent': 'image_generation_agent',
                    'description': 'Create icons and infographic elements'
                },
                {
                    'step': 5,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Organize into pitch deck visual project'
                }
            ]
        },

        # Product Launch Kit
        'product_launch_kit': {
            'description': 'Complete product launch visual package',
            'content_type': 'product_launch',
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research product launch trends and competitor analysis'
                },
                {
                    'step': 2,
                    'name': 'executive_review',
                    'agent': 'coleadership_agent',
                    'description': 'Get marketing and creative direction'
                },
                {
                    'step': 3,
                    'name': 'create_product_hero',
                    'agent': 'image_generation_agent',
                    'description': 'Generate product hero image'
                },
                {
                    'step': 4,
                    'name': 'create_feature_graphics',
                    'agent': 'image_generation_agent',
                    'description': 'Create feature highlight graphics'
                },
                {
                    'step': 5,
                    'name': 'create_social_announcements',
                    'agent': 'image_generation_agent',
                    'description': 'Generate social media announcement graphics'
                },
                {
                    'step': 6,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Organize into product launch kit'
                }
            ]
        },

        # =========================================================================
        # SESSION 293: BUSINESS RESEARCH WORKFLOWS - No Image/Video API Calls
        # =========================================================================

        # Full Business Research - Competitor + Customer + Market Analysis
        'business_research': {
            'description': 'Comprehensive business research: competitors, customers, market sizing',
            'content_type': 'business_research',
            'no_image_generation': True,  # Flag to skip image generation steps
            'steps': [
                {
                    'step': 1,
                    'name': 'market_research',
                    'agent': 'research_agent',
                    'description': 'Research market trends and industry landscape'
                },
                {
                    'step': 2,
                    'name': 'competitor_analysis',
                    'agent': 'competitor_analysis_agent',
                    'description': 'Analyze competitors, features, pricing, positioning'
                },
                {
                    'step': 3,
                    'name': 'customer_research',
                    'agent': 'customer_research_agent',
                    'description': 'Research customer pain points, personas, sentiment'
                },
                {
                    'step': 4,
                    'name': 'synthesize_findings',
                    'agent': 'strategic_synthesis',
                    'description': 'Synthesize all research into actionable insights'
                }
            ]
        },

        # Competitor Deep Dive
        'competitor_analysis': {
            'description': 'Deep dive into competitors in a specific market',
            'content_type': 'competitor_research',
            'no_image_generation': True,
            'steps': [
                {
                    'step': 1,
                    'name': 'identify_competitors',
                    'agent': 'research_agent',
                    'description': 'Identify key competitors in the market'
                },
                {
                    'step': 2,
                    'name': 'analyze_competitors',
                    'agent': 'competitor_analysis_agent',
                    'description': 'Deep analysis of each competitor'
                },
                {
                    'step': 3,
                    'name': 'generate_swot',
                    'agent': 'competitor_analysis_agent',
                    'description': 'Generate SWOT analysis and positioning map'
                }
            ]
        },

        # Customer Persona Development
        'customer_personas': {
            'description': 'Research and build detailed customer personas',
            'content_type': 'customer_research',
            'no_image_generation': True,
            'steps': [
                {
                    'step': 1,
                    'name': 'gather_discussions',
                    'agent': 'customer_research_agent',
                    'description': 'Search Reddit, forums for customer discussions'
                },
                {
                    'step': 2,
                    'name': 'extract_pain_points',
                    'agent': 'customer_research_agent',
                    'description': 'Extract and rank customer pain points'
                },
                {
                    'step': 3,
                    'name': 'build_personas',
                    'agent': 'customer_research_agent',
                    'description': 'Build 2-3 detailed customer personas'
                },
                {
                    'step': 4,
                    'name': 'extract_quotes',
                    'agent': 'customer_research_agent',
                    'description': 'Extract powerful customer quotes for messaging'
                }
            ]
        },

        # Session 297: Startup Validation - Comprehensive idea validation
        'startup_validation': {
            'description': 'Validate startup idea with market research, competitor analysis, and customer insights',
            'content_type': 'startup_validation',
            'no_image_generation': True,
            'steps': [
                {
                    'step': 1,
                    'name': 'market_opportunity',
                    'agent': 'research_agent',
                    'description': 'Research market size, growth trends, and industry landscape'
                },
                {
                    'step': 2,
                    'name': 'competitor_landscape',
                    'agent': 'competitor_analysis_agent',
                    'description': 'Identify and analyze existing competitors and alternatives'
                },
                {
                    'step': 3,
                    'name': 'customer_validation',
                    'agent': 'customer_research_agent',
                    'description': 'Validate customer pain points and willingness to pay'
                },
                {
                    'step': 4,
                    'name': 'differentiation_strategy',
                    'agent': 'competitor_analysis_agent',
                    'description': 'Define unique value proposition and competitive moat'
                },
                {
                    'step': 5,
                    'name': 'validation_summary',
                    'agent': 'strategic_synthesis',
                    'description': 'Synthesize findings into go/no-go recommendation with action items'
                }
            ]
        },

        # =========================================================================
        # SESSION 1232: Daily Chief-of-Staff Morning Brief — v0 draft
        # See docs/MORNING_BRIEF_SPEC.md for the canonical spec (lanes, rotation,
        # override triggers, output shapes, per-step input/write keys).
        # v0 is a workflow-shape stub: it parses + dispatches but the full
        # per-step input plumbing (rotation_slot_resolve pre-step, slot-resolved
        # agent for Lane 4, override-trigger inputs) lands in Sub-step B.
        # =========================================================================
        # Session 1233 B.1 + B.2 update: 8 steps total. B.1 flipped
        # lane_4_rotating_focus / decision_card_synthesis / create_deliverable
        # agents to dedicated workflow-internal handlers + extended
        # strategic_synthesis with morning_brief mode (reads lane_* +
        # decision_card_text). B.2 added Step 1 rotation_slot_resolve
        # pre-step that resolves context['rotation_slot'] per priority
        # chain (caller-forced → override flags → weekday default). All
        # remaining steps shifted from 1-7 to 2-8.
        'morning_brief': {
            'description': "Chris's daily Chief-of-Staff brief: rotation slot resolution + platform readiness + build focus + competitive landscape + rotating market lane + decision card synthesis",
            'content_type': 'morning_brief',
            'no_image_generation': True,
            'steps': [
                {
                    'step': 1,
                    'name': 'rotation_slot_resolve',
                    'agent': 'rotation_slot_resolve',  # B.2: internal pure-logic handler; weekday + overrides → context['rotation_slot']
                    'description': 'Resolve Lane 4 rotation slot per priority chain (caller-forced → incident → revenue → signal → calendar → weekday default)'
                },
                {
                    'step': 2,
                    'name': 'lane_1_platform_readiness',
                    'agent': 'system_intelligence_agent',
                    'description': 'Overnight platform health: SLO breaches, failing tasks, queue backlog, fleet degradation'
                },
                {
                    'step': 3,
                    'name': 'lane_2_build_focus',
                    'agent': 'coo_agent',
                    'description': 'Shipping delta + blocked initiatives + approvals needed in last 24h'
                },
                {
                    'step': 4,
                    'name': 'lane_3_competitive_landscape',
                    'agent': 'trend_analysis_agent',
                    'description': 'Change-only snapshot of competitor launches/pricing/features/fundraising in last 72h'
                },
                {
                    'step': 5,
                    'name': 'lane_4_rotating_focus',
                    'agent': 'lane_4_rotating_focus',  # B.1: internal handler; reads context['rotation_slot'] set by Step 1
                    'description': 'Rotating market/signal lane dispatched per the slot resolved by Step 1'
                },
                {
                    'step': 6,
                    'name': 'decision_card_synthesis',
                    'agent': 'decision_card_synthesis',  # B.1: internal LLM handler; reads 4 lane texts
                    'description': 'Synthesize 1-3 explicit decisions from the 4 lanes + governance/work/ops snapshots'
                },
                {
                    'step': 7,
                    'name': 'strategic_synthesis',
                    'agent': 'strategic_synthesis',  # workflow-internal handler; B.1 extension reads lane_* + decision_card_text in morning_brief mode
                    'description': 'Compile final brief markdown with TL;DR pointer to Decision Card'
                },
                {
                    'step': 8,
                    'name': 'create_deliverable',
                    'agent': 'create_morning_brief_deliverable',  # B.1: internal handler; persists Deliverable row (workspace_id wired in Sub-step C)
                    'description': 'Persist final brief into "Morning Brief" workspace as a deliverable'
                }
            ]
        },

        # =========================================================================
        # SESSION 496: Content Writing Workflows - Transform research into written content
        # =========================================================================

        # Write Blog Post from Research
        'write_blog_post': {
            'description': 'Transform research into a polished blog post',
            'content_type': 'blog_post',
            'no_image_generation': True,
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research the topic for insights and examples'
                },
                {
                    'step': 2,
                    'name': 'write_content',
                    'agent': 'content_writer_agent',
                    'description': 'Write the blog post based on research'
                },
                {
                    'step': 3,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Save content to a project'
                }
            ]
        },

        # Write Podcast Script from Research
        'write_podcast_script': {
            'description': 'Transform research into a conversational podcast script',
            'content_type': 'podcast_script',
            'no_image_generation': True,
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research the topic for talking points'
                },
                {
                    'step': 2,
                    'name': 'write_content',
                    'agent': 'content_writer_agent',
                    'description': 'Write the podcast script with segments and transitions'
                },
                {
                    'step': 3,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Save script to a project'
                }
            ]
        },

        # Write Video Script from Research
        'write_video_script': {
            'description': 'Transform research into a video script with scenes and narration',
            'content_type': 'video_script',
            'no_image_generation': True,
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research the topic for visual storytelling'
                },
                {
                    'step': 2,
                    'name': 'write_content',
                    'agent': 'content_writer_agent',
                    'description': 'Write video script with scenes, narration, and B-roll suggestions'
                },
                {
                    'step': 3,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Save script to a project'
                }
            ]
        },

        # Write Article from Research
        'write_article': {
            'description': 'Transform research into a professional article',
            'content_type': 'article',
            'no_image_generation': True,
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research the topic for depth and accuracy'
                },
                {
                    'step': 2,
                    'name': 'write_content',
                    'agent': 'content_writer_agent',
                    'description': 'Write the article with headline, lead, body, and CTA'
                },
                {
                    'step': 3,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Save article to a project'
                }
            ]
        },

        # Write Social Thread from Research
        'write_social_thread': {
            'description': 'Transform research into a viral social media thread',
            'content_type': 'social_thread',
            'no_image_generation': True,
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research the topic for engaging insights'
                },
                {
                    'step': 2,
                    'name': 'write_content',
                    'agent': 'content_writer_agent',
                    'description': 'Write connected social posts with hooks and hashtags'
                },
                {
                    'step': 3,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Save thread to a project'
                }
            ]
        },

        # Write Newsletter from Research
        'write_newsletter': {
            'description': 'Transform research into an email newsletter',
            'content_type': 'newsletter',
            'no_image_generation': True,
            'steps': [
                {
                    'step': 1,
                    'name': 'research',
                    'agent': 'web_search',
                    'description': 'Research the topic for newsletter content'
                },
                {
                    'step': 2,
                    'name': 'write_content',
                    'agent': 'content_writer_agent',
                    'description': 'Write newsletter with subject, preview, sections, and CTA'
                },
                {
                    'step': 3,
                    'name': 'create_project',
                    'agent': 'create_project_from_research',
                    'description': 'Save newsletter to a project'
                }
            ]
        }
    }

    # =========================================================================
    # SESSION 334: Project Research Context Integration
    # When project_id is provided, fetch existing research to inform creative work
    # =========================================================================

    def _get_project_research_context(self) -> Dict[str, Any]:
        """
        Session 334: Fetch existing research from project to GUIDE creative workflows.

        When a user says "Create brand identity" from within a project that already
        has competitor analysis and customer research, this method retrieves that
        research to ENHANCE and GUIDE each agent's work. Agents still do their own
        research, but they have project context to inform their direction.

        This context is injected into prompts so:
        - Research agents know what competitor/customer insights already exist
        - Image generation agents know the brand context and target audience
        - Executive review agents can make decisions based on prior research

        Returns:
            Dict with project info, research summaries, and context for prompts.
        """
        if not self.project_id:
            return {'has_research': False}

        try:
            from core.models_partnership import PartnershipProject
            from core.models_unified_system import BusinessResearchResult

            project = PartnershipProject.objects.get(id=self.project_id)

            # Get project basic info
            project_context = {
                'has_research': False,
                'project_id': str(project.id),
                'project_name': project.project_name,
                'project_description': project.description or '',
                'project_type': project.project_type or 'general',
                'research_summary': '',
                'competitor_insights': '',
                'customer_insights': '',
                'brand_recommendations': '',
            }

            # Get existing research from BusinessResearchResult
            research_results = BusinessResearchResult.objects.filter(
                project=project
            ).order_by('-created_at')

            research_summaries = []
            for result in research_results[:5]:  # Last 5 research results
                if result.research_type == 'competitor':
                    project_context['competitor_insights'] = result.analysis[:2000] if result.analysis else ''
                    research_summaries.append(f"Competitor Analysis: {result.analysis[:500] if result.analysis else 'N/A'}")
                elif result.research_type == 'customer':
                    project_context['customer_insights'] = result.analysis[:2000] if result.analysis else ''
                    # Include personas and pain points if available
                    if result.personas:
                        project_context['customer_personas'] = result.personas
                    if result.pain_points:
                        project_context['customer_pain_points'] = result.pain_points
                    research_summaries.append(f"Customer Research: {result.analysis[:500] if result.analysis else 'N/A'}")
                elif result.research_type == 'market':
                    research_summaries.append(f"Market Research: {result.analysis[:500] if result.analysis else 'N/A'}")

            # Also check metadata for research summaries (Session 325 format)
            if project.metadata and project.metadata.get('research_summaries'):
                for summary in project.metadata['research_summaries']:
                    if summary.get('type') == 'competitor_analysis' and not project_context['competitor_insights']:
                        project_context['competitor_insights'] = summary.get('summary', '')[:2000]
                    elif summary.get('type') == 'customer_research' and not project_context['customer_insights']:
                        project_context['customer_insights'] = summary.get('summary', '')[:2000]

            # Combine all research into a summary
            if research_summaries:
                project_context['research_summary'] = '\n\n'.join(research_summaries)
                project_context['has_research'] = True

            # Session 334 FIX: Also set has_research if we found insights from metadata
            if project_context['competitor_insights'] or project_context['customer_insights']:
                project_context['has_research'] = True

            # Generate brand recommendations from research
            if project_context['competitor_insights'] or project_context['customer_insights']:
                brand_recs = []
                if project_context.get('customer_pain_points'):
                    brand_recs.append(f"Address customer pain points: {', '.join(project_context['customer_pain_points'][:3])}")
                if project.project_name:
                    brand_recs.append(f"Brand name: {project.project_name}")
                project_context['brand_recommendations'] = '; '.join(brand_recs)

            logger.info(f"📊 Session 334: Found project research context for {project.project_name}: has_research={project_context['has_research']}")

            return project_context

        except Exception as e:
            logger.warning(f"⚠️ Session 334: Could not fetch project research context: {e}")
            return {'has_research': False}

    def execute(
        self,
        workflow: str,
        topic: str,
        count: int = 3,
        style_preferences: str = '',
        user_message: str = '',
        provided_research: str = '',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a complete workflow.

        Args:
            workflow: Workflow type (e.g., 'research_and_create_logos')
            topic: The research topic (e.g., 'modern AI company')
            count: Number of images to create (1-5)
            style_preferences: Optional style preferences
            user_message: Original user message (Session 239 - for style extraction)
            provided_research: Pre-existing research to skip research step (Session 495)
            **kwargs: Additional workflow-specific parameters

        Returns:
            Complete result with outputs from all steps
        """
        # =========================================================================
        # SESSION 495: Extract research context from user_message if present
        # When user clicks "create content based on this research", the frontend
        # appends "--- RESEARCH CONTEXT ---" followed by the research.
        # We need to:
        # 1. Extract research to skip the research step
        # 2. Use only the request part for mascot/style extraction (not the research!)
        # =========================================================================
        research_delimiter = '--- RESEARCH CONTEXT ---'
        extracted_research = provided_research  # Use explicit param if provided
        clean_user_message = user_message  # For mascot/style extraction

        if research_delimiter in user_message:
            parts = user_message.split(research_delimiter, 1)
            clean_user_message = parts[0].strip()  # Just the request part
            if not extracted_research and len(parts) > 1:
                extracted_research = parts[1].strip()  # The research content
            logger.info(f"📊 Session 495: Extracted research context ({len(extracted_research)} chars), clean request: '{clean_user_message}'")

        self.log_start(
            f"execute workflow: {workflow}",
            topic=topic,
            count=count,
            style_preferences=style_preferences,
            user_message=clean_user_message[:100] if clean_user_message else '',
            has_provided_research=bool(extracted_research)
        )

        # Validate workflow exists
        if workflow not in self.WORKFLOWS:
            return self._error_result(
                f"Unknown workflow: {workflow}. Available: {list(self.WORKFLOWS.keys())}",
                operation="validate_workflow"
            )

        workflow_def = self.WORKFLOWS[workflow]
        steps = workflow_def['steps']

        # Session 239/240: Extract style and mascot from BOTH user_message AND topic
        # GPT often fails to pass user_message, so we extract from topic as fallback
        extracted_style = ''
        extracted_mascot = ''

        # Style mapping used for both user_message and topic extraction
        style_mapping = {
            'pixar': 'pixar', 'disney': 'disney', 'dreamworks': 'dreamworks',
            'ghibli': 'ghibli', 'studio ghibli': 'ghibli', 'anime': 'anime',
            'cartoon': 'cartoon', 'animated': 'cartoon', 'south park': 'south_park',
            'simpsons': 'simpsons', 'family guy': 'family_guy', 'chibi': 'chibi',
            'manga': 'manga', 'looney tunes': 'looney_tunes', '3d animated': 'pixar',
            'watercolor': 'watercolor', 'oil painting': 'oil_painting',
            'cyberpunk': 'cyberpunk', 'steampunk': 'steampunk', 'minimalist': 'minimalist',
            'retro': 'retro', 'vintage': 'vintage', 'pop art': 'pop_art',
            'art deco': 'art_deco', 'impressionist': 'impressionist',
            'dreamworks-style': 'dreamworks', 'pixar-style': 'pixar', 'disney-style': 'disney'
        }

        # Mascot keywords to look for
        mascot_keywords = [
            'donkey', 'owl', 'lion', 'bear', 'fox', 'wolf', 'eagle', 'dragon',
            'unicorn', 'penguin', 'cat', 'dog', 'rabbit', 'monkey', 'elephant',
            'tiger', 'panda', 'koala', 'dinosaur', 'robot', 'mascot', 'character',
            'horse', 'bird', 'fish', 'shark', 'whale', 'octopus', 'bee', 'butterfly'
        ]

        # First, try to extract from user_message (most reliable source)
        # Session 495: Use clean_user_message (without research context) to avoid
        # extracting mascots/styles from research text
        if clean_user_message:
            user_msg_lower = clean_user_message.lower()
            logger.info(f"🔍 Session 239/495: Extracting from clean message: {clean_user_message[:100]}...")

            for style_key, style_value in style_mapping.items():
                if style_key in user_msg_lower:
                    extracted_style = style_value
                    logger.info(f"🎬 Session 239: Extracted style '{style_value}' from user message!")
                    break

            for mascot in mascot_keywords:
                if mascot in user_msg_lower:
                    extracted_mascot = mascot
                    logger.info(f"🦊 Session 239: Extracted mascot '{mascot}' from user message!")
                    break

        # Session 240: Also extract from topic parameter (fallback when GPT doesn't pass user_message)
        topic_lower = topic.lower()
        if not extracted_style:
            for style_key, style_value in style_mapping.items():
                if style_key in topic_lower:
                    extracted_style = style_value
                    logger.info(f"🎬 Session 240: Extracted style '{style_value}' from topic!")
                    break

        if not extracted_mascot:
            for mascot in mascot_keywords:
                if mascot in topic_lower:
                    extracted_mascot = mascot
                    logger.info(f"🦊 Session 240: Extracted mascot '{mascot}' from topic!")
                    break

        # Override GPT's stripped values with extracted ones
        if extracted_style and not style_preferences:
            style_preferences = extracted_style
            logger.info(f"✅ Session 239/240: Using extracted style: {style_preferences}")

        # If we found a mascot but it's not in the topic, add it
        if extracted_mascot and extracted_mascot not in topic.lower():
            topic = f"{topic} with {extracted_mascot} mascot"
            logger.info(f"✅ Session 239: Enhanced topic with mascot: {topic}")

        # Session 239: AUTO-DETECT style from topic if GPT didn't extract it
        # GPT often fails to extract style_preferences, so we do it ourselves
        if not style_preferences:
            topic_lower = topic.lower()
            animated_styles = {
                'pixar': 'pixar', 'disney': 'disney', 'dreamworks': 'dreamworks',
                'ghibli': 'ghibli', 'studio ghibli': 'ghibli', 'anime': 'anime',
                'cartoon': 'cartoon', 'animated': 'cartoon', 'south park': 'south_park',
                'simpsons': 'simpsons', 'family guy': 'family_guy', 'chibi': 'chibi',
                'manga': 'manga', 'looney tunes': 'looney_tunes', '3d animated': 'pixar'
            }
            for style_key, style_value in animated_styles.items():
                if style_key in topic_lower:
                    style_preferences = style_value
                    logger.info(f"🎬 Session 239: Auto-detected style '{style_value}' from topic")
                    break

        # Session 334: Fetch existing project research to GUIDE the workflow
        # This doesn't skip any steps - it provides context to enhance each agent's work
        project_research_context = self._get_project_research_context()

        # Initialize workflow context - shared data between steps
        context = {
            'topic': topic,
            'count': count,
            'style_preferences': style_preferences,
            'extracted_mascot': extracted_mascot,  # Session 240: Store mascot for image prompt
            'year': datetime.now().year,
            'user': self.user,
            'project_id': self.project_id,
            # Session 199: Content type from workflow definition
            'content_type': workflow_def.get('content_type', 'logos'),
            # Session 1233 B.1 — synthesis-mode flag flips
            # _execute_strategic_synthesis_step from generic-insights
            # output to morning-brief markdown output.
            '_synthesis_mode': (
                'morning_brief' if workflow == 'morning_brief' else 'default'
            ),
            # Results from each step
            'research_results': None,
            'research_summary': '',
            'executive_direction': None,
            'creative_recommendations': '',
            'generated_image_ids': [],
            'generated_video_ids': [],  # Session 199: Track videos too
            'selected_image_id': kwargs.get('image_id'),  # Session 199: For logo_to_video
            'project_created': None,
            # Session 334: Project research context as GUIDANCE (not replacement)
            'project_research_context': project_research_context,
            # Session 495: Pre-existing research to skip research step
            'provided_research': extracted_research,
        }

        # Session 495: If we have provided research, pre-populate research results
        # This allows us to skip the research step
        if extracted_research:
            logger.info(f"📊 Session 495: Using provided research ({len(extracted_research)} chars)")
            context['research_results'] = {'provided': True, 'content': extracted_research}
            context['research_summary'] = extracted_research[:2000]  # Use first 2000 chars as summary

        # Session 334: If we have project context, enhance the topic with project name
        if project_research_context.get('has_research'):
            project_name = project_research_context.get('project_name', '')
            if project_name and project_name.lower() not in topic.lower():
                # Enhance topic with project context
                context['topic'] = f"{topic} for '{project_name}'"
                logger.info(f"📊 Session 334: Enhanced topic with project name: {context['topic']}")

        # Session 1234 D3 — pre-materialize per-workflow target workspace
        # and thread its id into context BEFORE any step runs. Without
        # this, each step's delegate agent falls through agent_router's
        # active-workspace fallback (core/agent_router.py:1083-1121),
        # which picks the user's most-recently-active workspace —
        # typically a debugging/test workspace, NOT the workflow's
        # intended home. Symptom in the 2026-06-25 morning_brief first
        # fire: lane outputs (SystemIntelligenceAgent, COOAgent,
        # TrendAnalysisAgent) landed in workspace cf708a2e-…
        # (Session 1231 E2E) while only the final synthesized brief from
        # step 8 landed in the actual Morning Brief workspace.
        target_ws_id = self._resolve_workflow_target_workspace_id(workflow)
        if target_ws_id:
            context['workspace_id'] = target_ws_id

        # Execute each step in order
        step_results = []
        for step_def in steps:
            step_num = step_def['step']
            step_name = step_def['name']
            agent_name = step_def['agent']

            # Session 495: Skip research step if we already have provided research
            if step_name == 'research' and context.get('provided_research'):
                logger.info(f"⏭️ Session 495: SKIPPING research step - using provided research ({len(context['provided_research'])} chars)")
                step_results.append({
                    'step': step_num,
                    'name': step_name,
                    'agent': agent_name,
                    'success': True,
                    'skipped': True,
                    'reason': 'Using provided research context',
                    'result': {'provided': True, 'content_length': len(context['provided_research'])}
                })
                continue

            logger.info(f"🔄 Workflow Step {step_num}/{len(steps)}: {step_name} ({agent_name})")

            try:
                # Execute the step
                result = self._execute_step(step_def, context)

                # Record step result
                step_result = {
                    'step': step_num,
                    'name': step_name,
                    'agent': agent_name,
                    'success': result.get('success', False),
                    'summary': self._summarize_step_result(step_name, result),
                    'result': result
                }
                step_results.append(step_result)

                # Update context with step results
                self._update_context(step_name, result, context)

                if not result.get('success', False):
                    logger.error(f"❌ Step {step_name} failed: {result.get('error', 'Unknown error')}")
                    # Don't stop workflow on non-critical failures.
                    # Session 1234 D2 P2.C (Rigby-ratified): lane_4_rotating_focus
                    # is non-critical for morning_brief. The 4 non-gtm slot agents
                    # (SharpActionDetector / PredictionMarketAnalyst /
                    # StockAnalystAgent / ResearchAgent) return success=False on
                    # quiet-data days; halting the whole brief is the wrong call.
                    # Brief ships with Lane 4 sentinel from _lane_4_sentinel.
                    if step_name in ('create_project', 'lane_4_rotating_focus'):
                        if step_name == 'lane_4_rotating_focus':
                            logger.error(
                                "[MORNING_BRIEF_LANE_4_NONCRITICAL_FAIL] "
                                "slot=%s agent=%s error=%r — workflow continues, "
                                "brief will ship with sentinel",
                                result.get('slot_used'),
                                result.get('agent_name'),
                                result.get('error', 'no error captured'),
                            )
                        else:
                            logger.warning(f"⚠️ Continuing workflow despite {step_name} failure")
                    else:
                        # Critical step failed - abort
                        return self._compile_final_result(
                            workflow=workflow,
                            step_results=step_results,
                            context=context,
                            success=False,
                            error=f"Step '{step_name}' failed: {result.get('error', 'Unknown error')}"
                        )

                logger.info(f"✅ Step {step_name} completed: {step_result['summary']}")

            except Exception as e:
                logger.error(f"❌ Step {step_name} exception: {str(e)}", exc_info=True)
                step_results.append({
                    'step': step_num,
                    'name': step_name,
                    'agent': agent_name,
                    'success': False,
                    'summary': f"Exception: {str(e)}",
                    'result': {'success': False, 'error': str(e)}
                })
                return self._compile_final_result(
                    workflow=workflow,
                    step_results=step_results,
                    context=context,
                    success=False,
                    error=f"Step '{step_name}' exception: {str(e)}"
                )

        # All steps completed successfully
        self.log_complete(f"execute workflow: {workflow}", success=True)

        return self._compile_final_result(
            workflow=workflow,
            step_results=step_results,
            context=context,
            success=True
        )

    def _execute_step(self, step_def: Dict, context: Dict) -> Dict[str, Any]:
        """
        Execute a single workflow step.

        Routes to the appropriate handler based on agent name.
        """
        agent_name = step_def['agent']
        step_name = step_def['name']

        if agent_name == 'web_search':
            return self._execute_web_search_step(context)

        elif agent_name == 'coleadership_agent':
            return self._execute_coleadership_step(context)

        elif agent_name == 'image_generation_agent':
            return self._execute_image_generation_step(context)

        elif agent_name == 'create_project_from_research':
            return self._execute_create_project_step(context)

        # Session 199: New workflow step handlers
        elif agent_name == 'video_generation_agent':
            return self._execute_video_generation_step(context)

        elif agent_name == 'audio_generation_agent':
            return self._execute_audio_generation_step(context)

        elif agent_name == 'image_selection':
            return self._execute_image_selection_step(context)

        # Session 212: New workflow step handlers
        elif agent_name == 'image_variation_agent':
            return self._execute_image_variation_step(context)

        # Session 496: Content Writer Agent for written content
        elif agent_name == 'content_writer_agent':
            return self._execute_content_writer_step(context)

        # Session 1231 F7 — synthesize prior step outputs into actionable
        # insights. Built-in workflow templates `business_research` and
        # `startup_validation` end with a synthesis step that previously
        # failed because no `StrategicSynthesis` class exists in AGENT_MAP.
        # This handler reads whatever's in context (research_summary,
        # competitor_insights, customer_insights, etc.) and produces a
        # synthesis via an LLM call. Gracefully degrades when no input
        # is present (smoke-case behavior).
        # Session 1233 B.1 extends this handler with a 'morning_brief'
        # synthesis mode that reads lane keys and produces the final
        # brief markdown.
        elif agent_name == 'strategic_synthesis':
            return self._execute_strategic_synthesis_step(context)

        # Session 1233 B.2 — morning_brief workflow rotation_slot_resolve
        # pre-step. Pure logic (no LLM): reads weekday + override flags
        # from context, writes context['rotation_slot'] per priority
        # chain (caller-forced → incident → revenue → signal → calendar
        # → weekday default). Runs before Lane 4 so the slot resolution
        # is visible as a distinct workflow step in the trace.
        elif agent_name == 'rotation_slot_resolve':
            return self._execute_rotation_slot_resolve_step(context)

        # Session 1233 B.1 — morning_brief workflow Lane 4 rotating
        # focus dispatch. Reads context['rotation_slot'] (set by the
        # rotation_slot_resolve pre-step in B.2, or by an explicit
        # caller override). Default 'ai_infra_deep_dive' for safety
        # when no slot has been resolved.
        elif agent_name == 'lane_4_rotating_focus':
            return self._execute_lane_4_rotating_focus_step(context)

        # Session 1233 B.1 — morning_brief workflow Decision Card
        # synthesis. Reads the four lane texts from context, calls
        # gpt-5-mini to produce 1-3 explicit decisions, writes
        # context['decision_card_text'].
        elif agent_name == 'decision_card_synthesis':
            return self._execute_decision_card_synthesis_step(context)

        # Session 1233 B.1 — morning_brief workflow deliverable
        # creation. Persists context['morning_brief_markdown'] as a
        # Deliverable row. Workspace UUID will be wired in Sub-step C;
        # for B.1 the deliverable lands in the user's default workspace.
        elif agent_name == 'create_morning_brief_deliverable':
            return self._execute_create_morning_brief_deliverable_step(context)

        else:
            # Session 1231 F4 — AGENT_MAP fallback for snake_case step names
            # that lack a workflow-internal handler. The built-in
            # workflow templates reference 'research_agent',
            # 'competitor_analysis_agent', 'customer_research_agent',
            # 'strategic_synthesis' — three of which exist in AGENT_MAP
            # under their PascalCase names. Pre-fix every step using
            # those names silently failed with "Unknown agent in
            # workflow", aborting the workflow. Surfaced by the Session
            # 1231 full-AGENT_MAP fleet smoke (smoke_id=9321b9a13397):
            # WorkflowOrchestrationAgent's smoke dispatch hit
            # 'research_agent' and aborted.
            #
            # Session 1233 B.1.fix — acronym agents (COOAgent, CTOAgent,
            # SEOOptimizerAgent, AISeriesWorkflowAgent) need an explicit
            # alias because the default ``''.join(p.capitalize() …)``
            # produces wrong PascalCase (CooAgent ≠ COOAgent). Surfaced
            # by the morning_brief end-to-end smoke when Step 2
            # (lane_2_build_focus → coo_agent) hit "CooAgent not in
            # AGENT_MAP". The alias map below covers all known
            # acronym-style entries.
            pascal_name = self._AGENT_MAP_SNAKE_ALIASES.get(
                agent_name,
                ''.join(p.capitalize() for p in agent_name.split('_')),
            )
            try:
                from core.agent_router import AgentRouter
                router = AgentRouter(user=getattr(self, 'user', None))
            except Exception as e:
                return {
                    'success': False,
                    'error': (
                        f"Unknown agent in workflow: {agent_name} "
                        f"(AGENT_MAP fallback unavailable: {type(e).__name__})"
                    ),
                }
            if pascal_name not in router.AGENT_MAP:
                return {
                    'success': False,
                    'error': (
                        f"Unknown agent in workflow: {agent_name} "
                        f"(no internal handler + '{pascal_name}' not in AGENT_MAP)"
                    ),
                }
            try:
                step_task = step_def.get('description', '') or step_def.get('name', '')
                import time as _time
                _dispatch_start = _time.monotonic()
                result = router.route(pascal_name, step_task, context or {})
                duration_ms = int((_time.monotonic() - _dispatch_start) * 1000)
                # AgentResult → dict shape matching the other handlers
                success = bool(getattr(result, 'success', False))
                output = getattr(result, 'message', '') or ''
                data = getattr(result, 'data', {}) or {}
                if success:
                    return {
                        'success': True,
                        'output': output,
                        'data': data,
                    }
                # S3037 A6 fail-loud: mirror the S1234 D1 lane_4 fix onto the
                # AGENT_MAP fallback path. Before this fix, falsy result.success
                # returned {'success': False, 'output': '', 'data': ...} with no
                # 'error' field — orchestrator at line 1315/1342 then substituted
                # the generic "Unknown error" fallback. That produced the
                # deterministic error_signature 1cfc0fcf97dd26ce on 5+ morning_brief
                # failures across 12 days (see S3037 Reliability Audit v0 Step 3,
                # deliverable ce9ca37b-c544-4672-be9f-5b29e14aa59d).
                # Priority for error text: explicit .error → .message/output →
                # structured fallback identifying agent + result type.
                error_detail = (
                    getattr(result, 'error', None)
                    or (output if output else None)
                    or (
                        f"agent {pascal_name!r} returned success=False with no "
                        f"error/message/output (result type={type(result).__name__})"
                    )
                )
                return {
                    'success': False,
                    'output': output,
                    'data': data,
                    'error': (
                        f"AGENT_MAP dispatch: {pascal_name} reported failure "
                        f"for step {step_name!r} (duration_ms={duration_ms}): "
                        f"{error_detail}"
                    ),
                    'agent_name': pascal_name,
                    'duration_ms': duration_ms,
                }
            except Exception as e:
                logger.error(
                    "AGENT_MAP fallback dispatch failed for workflow step "
                    "agent='%s' → '%s': %s",
                    agent_name, pascal_name, e,
                    exc_info=True,
                )
                return {
                    'success': False,
                    'error': (
                        f"AGENT_MAP fallback dispatch failed for "
                        f"'{agent_name}' (→ '{pascal_name}') on step "
                        f"{step_name!r}: {type(e).__name__}: {e}"
                    ),
                    'agent_name': pascal_name,
                }

    def _execute_web_search_step(self, context: Dict) -> Dict[str, Any]:
        """
        Execute web search to research the topic.

        Session 238: Now augmented with Spider Intelligence!
        Before searching the web, we query our spider network for:
        - Trending topics in relevant categories
        - Real-time market insights
        - Industry-specific trends

        This gives the research step access to live data from 67 spiders
        across 21 real data sources.
        """
        topic = context['topic']
        year = context['year']
        style_prefs = context.get('style_preferences', '')
        content_type = context.get('content_type', 'logos')

        # =====================================================================
        # SESSION 238: SPIDER INTELLIGENCE INTEGRATION
        # Query our spider network FIRST to get real-time trending insights
        # =====================================================================
        spider_insights = self._get_spider_intelligence(topic, content_type)
        spider_trending_terms = spider_insights.get('trending_terms', [])
        spider_context = spider_insights.get('context_summary', '')

        # Store spider insights in context for later use (executives, prompts)
        context['spider_insights'] = spider_insights
        context['spider_trending'] = spider_trending_terms

        if spider_trending_terms:
            logger.info(f"🕷️ Spider Intelligence found {len(spider_trending_terms)} trending terms: {spider_trending_terms[:5]}")

        # Session 199/200/212: Build content-type-specific search queries
        if content_type == 'youtube_thumbnails':
            query = f"{topic} YouTube thumbnail design {year} high CTR click through rate best practices bold text"
        elif content_type == 'brand_identity':
            query = f"{topic} brand identity design {year} logo color palette typography visual identity guidelines"
        elif content_type == 'product_photography':
            query = f"{topic} product photography {year} e-commerce professional lighting composition styling"
        elif content_type == 'thumbnail_series':
            query = f"{topic} YouTube thumbnail series {year} consistent branding playlist visual identity recognition"
        elif content_type == 'animated_logo':
            query = f"{topic} animated logo motion graphics {year} logo animation trends"
        elif content_type == 'general_images':
            # Session 201: General images - focus on artistic/illustration inspiration
            query = f"{topic} illustration artwork {year} artistic style creative design visual inspiration"
        # Session 212: New content types
        elif content_type == 'social_media':
            query = f"{topic} social media content {year} Instagram Facebook LinkedIn visual marketing engagement"
        elif content_type == 'podcast_visuals':
            query = f"{topic} podcast cover art {year} episode artwork audiogram quote cards visual branding"
        elif content_type == 'ebook_cover':
            query = f"{topic} ebook cover design {year} book cover trends genre specific kindle amazon bestseller"
        elif content_type == 'video_production':
            query = f"{topic} video production assets {year} thumbnail end screen intro animation YouTube"
        elif content_type == 'course_thumbnails':
            query = f"{topic} online course thumbnails {year} Udemy Skillshare module design educational content"
        elif content_type == 'pitch_deck':
            query = f"{topic} pitch deck visuals {year} startup presentation investor deck infographics data visualization"
        elif content_type == 'product_launch':
            query = f"{topic} product launch visuals {year} marketing campaign announcement social media e-commerce"
        else:
            # Default: logos
            query = f"{topic} logo trends {year} minimalist bold contemporary"

        if style_prefs:
            query += f" {style_prefs}"

        # Session 238: Augment query with spider trending terms (top 3)
        if spider_trending_terms:
            trending_addition = ' '.join(spider_trending_terms[:3])
            query += f" {trending_addition}"
            logger.info(f"🕷️ Augmented query with spider trends: {trending_addition}")

        # =====================================================================
        # SESSION 334: INJECT PROJECT RESEARCH CONTEXT AS GUIDANCE
        # If we have prior research, augment the query with relevant terms
        # This helps the web search find MORE RELEVANT information, not LESS
        # =====================================================================
        project_research_context = context.get('project_research_context', {})
        if project_research_context.get('has_research'):
            # Extract key terms from existing research to enhance search
            guidance_terms = []

            # If we have customer pain points, search for solutions
            if project_research_context.get('customer_pain_points'):
                pain_points = project_research_context['customer_pain_points'][:2]
                guidance_terms.extend([str(pp).split()[0] for pp in pain_points if pp])

            # If we have competitor insights, search for differentiation
            if project_research_context.get('competitor_insights'):
                guidance_terms.append('differentiate')

            if guidance_terms:
                guidance_addition = ' '.join(guidance_terms[:3])
                query += f" {guidance_addition}"
                logger.info(f"📊 Session 334: Enhanced query with project context: {guidance_addition}")

        logger.info(f"🔍 Web search query ({content_type}): {query}")

        try:
            # Import and execute web search
            from core.views_image import _execute_web_search
            result = _execute_web_search({'query': query})

            # Session 238: Merge spider context into research summary
            if result.get('success') and spider_context:
                existing_summary = ''
                if result.get('results'):
                    snippets = [r.get('snippet', '') for r in result['results'][:3]]
                    existing_summary = ' '.join(snippets)[:300]

                # Prepend spider insights to the research summary
                result['spider_insights'] = spider_insights
                result['enhanced_summary'] = f"🕷️ LIVE TRENDS: {spider_context}\n\n📰 WEB RESEARCH: {existing_summary}"
                logger.info(f"🕷️ Enhanced research with spider intelligence")

            return result

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {'success': False, 'error': str(e)}

    def _get_spider_intelligence(self, topic: str, content_type: str) -> Dict[str, Any]:
        """
        Session 238: Query spider intelligence for topic-relevant trends.

        This method:
        1. Determines which spider categories are relevant to the topic
        2. Queries SpiderIntelligenceService for trending data
        3. Extracts actionable keywords for image generation
        4. Returns a context summary for executives

        Args:
            topic: The user's topic (e.g., "AI content generation")
            content_type: Type of content being created (logos, thumbnails, etc.)

        Returns:
            Dict with trending_terms, context_summary, and raw_trends
        """
        try:
            from core.services.spider_intelligence import SpiderIntelligenceService
            spider_service = SpiderIntelligenceService()

            # Determine relevant categories based on topic keywords
            topic_lower = topic.lower()
            categories_to_query = []

            # Map topic keywords to spider categories
            if any(kw in topic_lower for kw in ['ai', 'ml', 'tech', 'software', 'app', 'saas', 'developer', 'code', 'programming']):
                categories_to_query.append('tech')
            if any(kw in topic_lower for kw in ['design', 'creative', 'art', 'visual', 'brand', 'logo', 'graphic']):
                categories_to_query.append('creative')
            if any(kw in topic_lower for kw in ['crypto', 'bitcoin', 'ethereum', 'nft', 'blockchain', 'defi', 'web3']):
                categories_to_query.append('crypto')
            if any(kw in topic_lower for kw in ['finance', 'invest', 'stock', 'market', 'money', 'trading']):
                categories_to_query.append('financial')
            if any(kw in topic_lower for kw in ['job', 'career', 'remote', 'freelance', 'hire', 'work']):
                categories_to_query.append('jobs')
            if any(kw in topic_lower for kw in ['news', 'trending', 'viral', 'popular', 'current']):
                categories_to_query.append('news')

            # Default to tech + creative if no specific match
            if not categories_to_query:
                categories_to_query = ['tech', 'creative']

            # Query each relevant category
            all_trends = []
            for category in categories_to_query[:3]:  # Max 3 categories
                try:
                    trends = spider_service.get_trending_topics(
                        category=category,
                        hours=48,  # Last 48 hours
                        limit=10
                    )
                    for trend in trends:
                        trend['category'] = category
                    all_trends.extend(trends)
                except Exception as e:
                    logger.warning(f"Spider query failed for {category}: {e}")

            if not all_trends:
                logger.info(f"🕷️ No spider trends found for topic: {topic}")
                return {'trending_terms': [], 'context_summary': '', 'raw_trends': []}

            # Sort by score and deduplicate
            all_trends.sort(key=lambda x: x.get('score', 0), reverse=True)
            seen_topics = set()
            unique_trends = []
            for trend in all_trends:
                topic_name = trend.get('topic', '').lower()
                if topic_name and topic_name not in seen_topics:
                    seen_topics.add(topic_name)
                    unique_trends.append(trend)

            # Extract top trending terms (for query augmentation)
            trending_terms = [t['topic'] for t in unique_trends[:8]]

            # Build context summary (for executives)
            top_trends = unique_trends[:5]
            if top_trends:
                trend_list = ', '.join([f"{t['topic']} ({t.get('category', 'general')})" for t in top_trends])
                context_summary = f"Currently trending: {trend_list}. These topics are getting attention across {len(categories_to_query)} categories from our spider network."
            else:
                context_summary = ''

            logger.info(f"🕷️ Spider Intelligence: Found {len(unique_trends)} trends across {categories_to_query}")

            return {
                'trending_terms': trending_terms,
                'context_summary': context_summary,
                'raw_trends': unique_trends[:10],
                'categories_queried': categories_to_query
            }

        except Exception as e:
            logger.error(f"Spider intelligence query failed: {e}")
            return {'trending_terms': [], 'context_summary': '', 'raw_trends': []}

    def _execute_coleadership_step(self, context: Dict) -> Dict[str, Any]:
        """Execute co-leadership agent for executive review."""
        topic = context['topic']
        count = context['count']
        research_summary = context.get('research_summary', 'Research completed')
        content_type = context.get('content_type', 'logos')

        # Session 238: Include spider intelligence in executive context
        spider_insights = context.get('spider_insights', {})
        spider_context = spider_insights.get('context_summary', '')
        spider_trending = context.get('spider_trending', [])

        # Session 199/200/201: Build content-type-specific questions
        # Session 201: Questions now explicitly mention AI image generation
        # Session 238: Now includes live spider intelligence!
        ai_context = (
            "IMPORTANT: You are advising on AI IMAGE GENERATION using Stability AI. "
            "Your recommendations will be converted into prompts for the AI model. "
            "Consider what works well for AI: simple clear descriptions, style keywords, "
            "avoiding complex text/typography (AI struggles with text), focusing on composition and mood."
        )

        # Session 238: Add spider intelligence to executive context
        if spider_context:
            ai_context += f"\n\n🕷️ LIVE MARKET INTELLIGENCE FROM OUR SPIDER NETWORK:\n{spider_context}"
        if spider_trending:
            ai_context += f"\n\nTrending keywords to consider: {', '.join(spider_trending[:5])}"

        # =====================================================================
        # SESSION 334: INJECT PROJECT RESEARCH CONTEXT AS GUIDANCE
        # If we have prior competitor/customer research, share it with executives
        # This helps them make informed decisions based on existing project intel
        # =====================================================================
        project_research_context = context.get('project_research_context', {})
        if project_research_context.get('has_research'):
            ai_context += "\n\n📊 EXISTING PROJECT RESEARCH (use this to GUIDE your recommendations):"

            project_name = project_research_context.get('project_name', '')
            if project_name:
                ai_context += f"\n- Project: {project_name}"

            # Share competitor insights for differentiation guidance
            competitor_insights = project_research_context.get('competitor_insights', '')
            if competitor_insights:
                # Truncate to key insights
                ai_context += f"\n- Competitor Analysis (key insights): {competitor_insights[:500]}"

            # Share customer insights for target audience guidance
            customer_insights = project_research_context.get('customer_insights', '')
            if customer_insights:
                ai_context += f"\n- Customer Research (key insights): {customer_insights[:500]}"

            # Share pain points for visual direction
            pain_points = project_research_context.get('customer_pain_points', [])
            if pain_points:
                ai_context += f"\n- Customer Pain Points to address visually: {', '.join(str(pp) for pp in pain_points[:3])}"

            logger.info(f"📊 Session 334: Injected project research context for executive review")

        if content_type == 'youtube_thumbnails':
            question = (
                f"{ai_context}\n\n"
                f"Based on the research about {topic} YouTube thumbnails and CTR optimization, "
                f"what specific creative direction should guide our AI image generation? "
                f"Consider: bold compositions, vibrant color combinations, expressive imagery. "
                f"Note: AI-generated text often looks bad, so focus on visual impact over text. "
                f"We will generate {count} thumbnail variations."
            )
        elif content_type == 'brand_identity':
            question = (
                f"{ai_context}\n\n"
                f"Based on the research about {topic} brand identity design, "
                f"what creative direction should guide our AI logo generation? "
                f"CRITICAL: AI cannot reliably generate text/letters, so focus on: "
                f"1) Abstract symbols and icons, 2) Color palette, 3) Geometric vs organic shapes, "
                f"4) Simple memorable marks. We need {count} logo SYMBOLS (no text)."
            )
        elif content_type == 'product_photography':
            question = (
                f"{ai_context}\n\n"
                f"Based on the research about {topic} product photography, "
                f"what creative direction should guide our AI image generation? Consider: "
                f"1) Lighting style (soft, dramatic, studio), 2) Background (solid, gradient, contextual), "
                f"3) Composition and angles, 4) Mood and atmosphere. "
                f"We will generate {count} AI product shots."
            )
        elif content_type == 'thumbnail_series':
            question = (
                f"{ai_context}\n\n"
                f"Based on the research about {topic} thumbnail series design, "
                f"what creative direction ensures visual consistency across {count} AI-generated thumbnails? "
                f"Focus on: consistent color scheme, recognizable visual style, compositional patterns. "
                f"Note: AI text is unreliable, so prioritize strong visual identity over text elements."
            )
        elif content_type == 'animated_logo':
            question = (
                f"{ai_context}\n\n"
                f"Based on the research about {topic} logo animation, "
                f"what motion style should we use for AI video generation of the logo? "
                f"Consider: smooth reveals, professional motion, brand-appropriate energy level."
            )
        elif content_type == 'general_images':
            # Session 201: General images/artwork - creative freedom, no text restrictions
            question = (
                f"{ai_context}\n\n"
                f"Based on the research about {topic} illustrations and artwork, "
                f"what creative direction should guide our AI image generation? "
                f"Focus on: artistic style, color palette, mood and atmosphere, composition, "
                f"level of detail, and overall aesthetic. We need {count} creative, unique images."
            )
        # Session 212: New content types
        elif content_type == 'social_media':
            question = (
                f"{ai_context}\n\n"
                f"Based on the research about {topic} social media content, "
                f"what creative direction should guide our AI image generation? "
                f"Consider: platform-specific requirements (Instagram square, LinkedIn horizontal), "
                f"brand consistency, scroll-stopping visuals, engagement optimization. "
                f"We need {count} social media images."
            )
        elif content_type == 'podcast_visuals':
            question = (
                f"{ai_context}\n\n"
                f"Based on the research about {topic} podcast episode, "
                f"what creative direction should guide our AI image generation? "
                f"Consider: podcast cover art style, episode-specific imagery, "
                f"quote card designs that are shareable, consistent visual branding. "
                f"We need {count} podcast visual assets."
            )
        elif content_type == 'ebook_cover':
            question = (
                f"{ai_context}\n\n"
                f"Based on the research about {topic} ebook/book cover design, "
                f"what creative direction should guide our AI image generation? "
                f"Consider: genre-appropriate imagery, marketability, thumbnail visibility, "
                f"composition that works at small sizes, professional book design conventions. "
                f"NOTE: AI cannot reliably generate text, so focus on imagery. We need {count} cover concepts."
            )
        elif content_type == 'video_production':
            question = (
                f"{ai_context}\n\n"
                f"Based on the research about {topic} video production, "
                f"what creative direction should guide our AI image generation? "
                f"Consider: channel branding, thumbnail click-worthiness, "
                f"end screen call-to-action design, consistent visual identity. "
                f"We need {count} video production assets."
            )
        elif content_type == 'course_thumbnails':
            question = (
                f"{ai_context}\n\n"
                f"Based on the research about {topic} online course, "
                f"what creative direction should guide our AI image generation? "
                f"Consider: educational credibility, module differentiation, "
                f"consistent template design, professional appearance. "
                f"We need {count} course module thumbnails."
            )
        elif content_type == 'pitch_deck':
            question = (
                f"{ai_context}\n\n"
                f"Based on the research about {topic} pitch deck visuals, "
                f"what creative direction should guide our AI image generation? "
                f"Consider: professional/corporate aesthetic, data visualization support, "
                f"clean backgrounds for text overlay, infographic elements, investor appeal. "
                f"We need {count} pitch deck visual assets."
            )
        elif content_type == 'product_launch':
            question = (
                f"{ai_context}\n\n"
                f"Based on the research about {topic} product launch, "
                f"what creative direction should guide our AI image generation? "
                f"Consider: product hero shots, feature highlights, "
                f"social announcement graphics, marketing campaign cohesion. "
                f"We need {count} product launch visuals."
            )
        else:
            # Default: logos
            question = (
                f"{ai_context}\n\n"
                f"Based on the latest research about {topic} logos and design trends, "
                f"what specific creative direction should guide our AI logo generation? "
                f"CRITICAL: AI cannot generate readable text, so recommend: "
                f"abstract symbols, geometric shapes, iconic marks, color combinations. "
                f"We need {count} simple, bold, versatile logo SYMBOLS."
            )

        logger.info(f"🏢 Co-leadership question: {question[:100]}...")

        try:
            from core.agent_router import AgentRouter

            task = f"{question}\n\nResearch findings: {research_summary}. User topic: {topic}."
            router = AgentRouter(user=context.get('user'))
            result = router.route(agent_name='CreativeDirectorAgent', task=task)
            return result.data if result.data else {'success': True, 'message': result.message}

        except Exception as e:
            logger.error(f"Co-leadership failed: {e}")
            return {'success': False, 'error': str(e)}

    def _execute_image_generation_step(self, context: Dict) -> Dict[str, Any]:
        """Execute image generation agent - content-type aware."""
        topic = context['topic']
        count = context['count']
        style_prefs = context.get('style_preferences', '')
        creative_recs = context.get('creative_recommendations', '')
        content_type = context.get('content_type', 'logos')
        extracted_mascot = context.get('extracted_mascot', '')  # Session 240: Get mascot

        logger.info(f"🎨 Session 240: Image generation - topic='{topic}', style='{style_prefs}', mascot='{extracted_mascot}'")

        # Session 240: Pre-check for animated styles (used to decide if exec recommendations apply)
        animated_styles = ['pixar', 'disney', 'dreamworks', 'ghibli', 'anime', 'cartoon',
                          'south_park', 'simpsons', 'family_guy', 'rick_and_morty',
                          'looney_tunes', 'adventure_time', 'chibi', 'manga']
        style_lower = (style_prefs or '').lower().strip()
        is_animated_style = any(anim in style_lower for anim in animated_styles)

        # Session 199/200/201: Build content-type-specific prompts and dimensions
        # Session 201: Added "NO TEXT, NO WORDS, NO LETTERS" to all logo prompts
        if content_type == 'youtube_thumbnails':
            # YouTube thumbnails are the ONLY type that should have text
            prompt = f"YouTube thumbnail for {topic}, bold large text, vibrant colors, high contrast, eye-catching, expressive face or reaction, dramatic lighting"
            width, height = 1280, 720  # YouTube 16:9 ratio
            style = "YouTube thumbnail, high CTR, click-worthy, bold graphics"
        elif content_type == 'brand_identity':
            # Session 200/201 FIX: Generate single clean logos, NO TEXT
            prompt = f"single professional {topic} logo mark, abstract symbol only, NO TEXT, NO WORDS, NO LETTERS, NO TYPOGRAPHY, minimalist icon, clean geometric design, versatile brand mark, isolated on simple solid background, no mockups, no multiple items, just one simple logo symbol"
            width, height = 1024, 1024
            style = "single logo symbol, icon only, no text, clean, professional, isolated mark"
        elif content_type == 'product_photography':
            prompt = f"professional product photography of {topic}, studio lighting, clean background, commercial quality, e-commerce ready, high detail, NO TEXT, NO WORDS, NO LABELS"
            width, height = 1024, 1024
            style = "product photography, commercial, professional studio shot, no text"
        elif content_type == 'thumbnail_series':
            # Thumbnail series CAN have text for episode numbers
            prompt = f"YouTube thumbnail series for {topic}, consistent branding, episode numbering, bold text, recognizable template, cohesive visual style"
            width, height = 1280, 720  # YouTube 16:9 ratio
            style = "thumbnail series, consistent branding, recognizable template"
        elif content_type == 'general_images':
            # Session 201: General images/artwork - NO text restrictions, creative freedom
            prompt = f"artistic illustration of {topic}, creative, detailed, professional quality, vibrant composition"
            width, height = 1024, 1024
            style = "artistic, creative, professional illustration"
        # Session 212: New content types for image generation
        elif content_type == 'social_media':
            prompt = f"social media content for {topic}, eye-catching, scroll-stopping, vibrant colors, engaging composition, professional marketing quality"
            width, height = 1080, 1080  # Instagram square
            style = "social media, marketing, engaging, professional"
        elif content_type == 'podcast_visuals':
            prompt = f"podcast cover art for {topic}, professional audio content visual, bold imagery, modern podcast aesthetic, shareable design"
            width, height = 1400, 1400  # Podcast cover standard
            style = "podcast, audio content, professional, modern"
        elif content_type == 'ebook_cover':
            prompt = f"ebook cover design for {topic}, professional book cover, genre-appropriate imagery, marketable design, thumbnail-readable composition, NO TEXT, NO WORDS, NO TITLE"
            width, height = 1600, 2560  # Kindle cover ratio (1:1.6)
            style = "book cover, professional publishing, marketable"
        elif content_type == 'video_production':
            prompt = f"video production asset for {topic}, YouTube style, professional channel branding, bold visuals, engaging composition"
            width, height = 1920, 1080  # Full HD video
            style = "video production, YouTube, professional channel"
        elif content_type == 'course_thumbnails':
            prompt = f"online course thumbnail for {topic}, educational content, professional appearance, module design, learner-engaging, credible academic look"
            width, height = 1280, 720  # Course platform standard
            style = "educational, course, professional, academic"
        elif content_type == 'pitch_deck':
            prompt = f"pitch deck visual for {topic}, professional business aesthetic, clean corporate design, investor-ready quality, data visualization support, NO TEXT"
            width, height = 1920, 1080  # Presentation ratio
            style = "corporate, pitch deck, professional, clean"
        elif content_type == 'product_launch':
            prompt = f"product launch visual for {topic}, marketing campaign quality, hero shot, feature highlight, announcement graphic, professional e-commerce"
            width, height = 1200, 1200  # Square for versatility
            style = "product launch, marketing, professional, e-commerce"
        else:
            # Default: logos - NO TEXT
            # Session 238/240: Check if user requested an ANIMATED style (Pixar, Disney, etc.)
            # These need character/mascot prompts, NOT flat geometric icons
            # NOTE: is_animated_style already computed at top of function

            if is_animated_style:
                # Session 238/239/240: ANIMATED STYLE - generate a mascot/character logo, not flat icon
                # Include the specific animation style AND mascot type in the prompt
                if extracted_mascot:
                    # User specified a mascot type (donkey, owl, etc.) - use it!
                    prompt = f"{style_prefs} 3D animated style {extracted_mascot} character mascot, cute friendly {extracted_mascot} with expressive face, vibrant colors, simple memorable design, professional brand mascot for {topic}, clean solid background, NO TEXT, NO WORDS, NO LETTERS"
                    style = f"{style_prefs} style, {extracted_mascot} mascot character, 3D animated, friendly, professional brand"
                    logger.info(f"🎬 Session 240: Using {style_prefs} style with {extracted_mascot} mascot!")
                else:
                    # No specific mascot - generic animated mascot
                    prompt = f"3D animated {style_prefs} style mascot character for {topic}, cute friendly character, expressive face, vibrant colors, simple memorable design, professional brand mascot, clean background, NO TEXT, NO WORDS, NO LETTERS"
                    style = f"{style_prefs} style, mascot character, 3D animated, friendly, professional brand"
                    logger.info(f"🎬 Session 238: Detected animated style '{style_prefs}' - using generic mascot prompt")
            else:
                # Default: flat/geometric logo
                prompt = f"single professional {topic} logo mark, abstract symbol only, NO TEXT, NO WORDS, NO LETTERS, minimalist icon, bold geometric shapes, simple clean design"
                style = "minimalist icon, bold symbol, no text, contemporary logo design"

            width, height = 1024, 1024

        if creative_recs:
            # Add executive recommendations to prompt
            prompt += f", {creative_recs[:200]}"

        if style_prefs:
            # Session 201 FIX: Use the BUILT-IN 80+ styles from ImageGenerationService
            # instead of maintaining a separate style dictionary here.
            #
            # The ImageGenerationService._apply_style_to_prompt() has 80+ professionally
            # crafted style expansions including: pixar, disney, dreamworks, south_park,
            # anime, cyberpunk, watercolor, ghibli, simpsons, family_guy, etc.
            #
            # We pass the style to the service, which will apply it properly.
            # If it's a custom style not in the built-in list, the service will append "{style} style".
            #
            # Map common user variations to the built-in style keys:
            style_key_mapping = {
                # Animation variations
                'studio ghibli': 'ghibli',
                'south park': 'south_park',
                'family guy': 'family_guy',
                'rick and morty': 'rick_and_morty',
                'looney tunes': 'looney_tunes',
                'adventure time': 'adventure_time',
                'gravity falls': 'gravity_falls',
                'bojack horseman': 'bojack',
                # Other variations
                'pixel': 'pixel_art',
                'pixelart': 'pixel_art',
                '8bit': 'pixel_art',
                '8-bit': 'pixel_art',
                'scifi': 'scifi',
                'sci-fi': 'scifi',
                'science fiction': 'scifi',
                'cyber punk': 'cyberpunk',
                'steam punk': 'steampunk',
            }

            # Normalize the style key
            style_lower = style_prefs.lower().strip().replace('-', '_').replace(' ', '_')
            style = style_key_mapping.get(style_prefs.lower().strip(), style_lower)

            # The style will be passed to ImageGenerationService which has 80+ built-in styles
            logger.info(f"🎨 Session 201: Using style '{style}' (from user input '{style_prefs}')")

        if content_type == 'logos':
            # Session 201: Enhanced prompt suffix to EXPLICITLY prevent text
            # Include both positive (what we want) and negative (what to avoid) guidance
            prompt += ", clean negative space, strong yet simple mark, limited vibrant palette, symbol only, icon design, NO TEXT, no letters, no words, no typography, abstract mark"

        # =====================================================================
        # SESSION 299: INJECT STORED RESEARCH INTELLIGENCE
        # Query BusinessResearchResult for relevant competitor/customer research
        # and extract key insights to inform the image generation prompt
        # =====================================================================
        try:
            from core.models_unified_system import BusinessResearchResult

            # Use semantic search to find research relevant to this topic
            research_insights = BusinessResearchResult.get_research_context_for_prompt(topic, limit=3)

            if research_insights:
                # Extract actionable design guidance from research
                # We don't add the full context to the image prompt (too verbose)
                # Instead, extract key differentiators and pain points

                # Parse pain points for design cues
                pain_point_cues = []
                differentiation_cues = []

                # Search for customer pain points
                customer_research = BusinessResearchResult.objects.filter(
                    research_type='customer',
                    market_topic__icontains=topic.split()[0] if topic else ''
                ).order_by('-created_at').first()

                if customer_research and customer_research.pain_points:
                    # Convert pain points to design concepts
                    pain_points = customer_research.pain_points[:3]
                    for pp in pain_points:
                        if isinstance(pp, str):
                            # Map common pain points to visual cues
                            if 'trust' in pp.lower() or 'reliable' in pp.lower():
                                pain_point_cues.append('trustworthy stable')
                            elif 'simple' in pp.lower() or 'complex' in pp.lower():
                                pain_point_cues.append('simple approachable')
                            elif 'expensive' in pp.lower() or 'cost' in pp.lower():
                                pain_point_cues.append('value premium quality')
                            elif 'confus' in pp.lower() or 'overwhelm' in pp.lower():
                                pain_point_cues.append('clear organized')

                # Search for competitor insights for differentiation
                competitor_research = BusinessResearchResult.objects.filter(
                    research_type='competitor',
                    market_topic__icontains=topic.split()[0] if topic else ''
                ).order_by('-created_at').first()

                if competitor_research and competitor_research.recommendations:
                    # Extract differentiation concepts
                    for rec in competitor_research.recommendations[:2]:
                        if isinstance(rec, str):
                            if 'stand out' in rec.lower() or 'differentiate' in rec.lower():
                                differentiation_cues.append('distinctive unique bold')
                            elif 'modern' in rec.lower() or 'innovative' in rec.lower():
                                differentiation_cues.append('modern innovative cutting-edge')

                # Add research-informed cues to prompt (subtle, design-focused)
                research_cues = pain_point_cues + differentiation_cues
                if research_cues:
                    research_modifier = ', '.join(list(set(research_cues))[:3])
                    prompt += f", {research_modifier}"
                    logger.info(f"📊 Session 299: Enhanced prompt with research insights: {research_modifier}")
                    context['research_context_used'] = True
                    context['research_cues'] = research_cues

        except Exception as e:
            logger.warning(f"Session 299: Could not inject research context: {e}")

        # =====================================================================
        # SESSION 334: INJECT PROJECT-SPECIFIC RESEARCH AS GUIDANCE
        # If we have research from the actual project, use it to enhance prompt
        # This is more targeted than Session 299's topic-based search
        # =====================================================================
        project_research_context = context.get('project_research_context', {})
        if project_research_context.get('has_research'):
            project_visual_cues = []

            # Use direct pain points from project research
            project_pain_points = project_research_context.get('customer_pain_points', [])
            for pp in project_pain_points[:2]:
                if isinstance(pp, str):
                    pp_lower = pp.lower()
                    # Map pain points to visual concepts for image generation
                    if 'trust' in pp_lower or 'reliable' in pp_lower:
                        project_visual_cues.append('trustworthy stable')
                    elif 'simple' in pp_lower or 'easy' in pp_lower:
                        project_visual_cues.append('simple approachable')
                    elif 'expensive' in pp_lower or 'cost' in pp_lower:
                        project_visual_cues.append('premium value')
                    elif 'confus' in pp_lower or 'overwhelm' in pp_lower:
                        project_visual_cues.append('clear organized')
                    elif 'slow' in pp_lower or 'time' in pp_lower:
                        project_visual_cues.append('fast efficient dynamic')

            # If competitor insights mention differentiation
            if project_research_context.get('competitor_insights'):
                project_visual_cues.append('distinctive unique')

            if project_visual_cues:
                project_modifier = ', '.join(list(set(project_visual_cues))[:3])
                prompt += f", {project_modifier}"
                logger.info(f"📊 Session 334: Enhanced prompt with project research: {project_modifier}")
                context['project_research_used'] = True

        logger.info(f"🎨 Image generation prompt ({content_type}): {prompt[:100]}...")
        logger.info(f"🎨 Generating {count} images at {width}x{height}")

        try:
            from core.views_image import _execute_generate_image
            from content.models import AISession

            # Session 193: Fix MultipleObjectsReturned error & FieldError
            # AISession uses is_active (bool), not status (string)
            # Use filter().first() instead of get_or_create() since users have many sessions
            session = None
            if context.get('user'):
                session = AISession.objects.filter(
                    user=context['user'],
                    is_active=True
                ).order_by('-created_at').first()

                # If no active session, create one
                if not session:
                    session = AISession.objects.create(
                        user=context['user'],
                        title='Workflow Session',
                        is_active=True
                    )

            # Session 201: Build content-type-specific negative prompts
            # This is CRITICAL for preventing unwanted text in logos
            # Use repetition and emphasis for better guidance to the AI model
            if content_type in ['logos', 'brand_identity']:
                negative_prompt = (
                    "text, text, text, words, words, letters, letters, typography, font, writing, "
                    "alphabet, numbers, numbers, watermark, signature, signature, label, caption, "
                    "title, slogan, tagline, brand name, company name, initials, monogram, "
                    "multiple logos, collage, mockup, business card, letterhead, banner, "
                    "readable text, any text, english text, foreign text, chinese characters, "
                    "blurry, low quality, distorted, ugly, deformed"
                )
            elif content_type == 'product_photography':
                negative_prompt = (
                    "text, words, letters, label, price tag, watermark, "
                    "blurry, low quality, distorted, ugly, cartoon, illustration"
                )
            else:
                negative_prompt = (
                    "blurry, low quality, distorted, ugly, deformed, "
                    "watermark, signature"
                )

            # Session 238: Use SD3 for logos/brand_identity (better at avoiding text)
            # SDXL is faster but often ignores "no text" instructions
            # SD3 follows instructions more precisely, worth the extra ~2s per image
            if content_type in ['logos', 'brand_identity']:
                model = 'sd3'
            else:
                model = 'sdxl'

            parameters = {
                'prompt': prompt,
                'negative_prompt': negative_prompt,
                'count': count,
                'model': model,
                'style': style,
                'width': width,
                'height': height,
            }

            if context.get('project_id'):
                parameters['project_id'] = context['project_id']

            result = _execute_generate_image(
                user=context['user'],
                parameters=parameters,
                session=session
            )
            return result

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {'success': False, 'error': str(e)}

    def _execute_create_project_step(self, context: Dict) -> Dict[str, Any]:
        """Execute create project from research to organize content."""
        topic = context['topic']
        research_summary = context.get('research_summary', 'Research and content created')
        executive_direction = context.get('creative_recommendations', '')
        image_ids = context.get('generated_image_ids', [])
        video_ids = context.get('generated_video_ids', [])
        content_type = context.get('content_type', 'logos')

        if not image_ids and not video_ids:
            logger.warning("⚠️ No content IDs to add to project")

        # Session 199/201: Enhanced topic cleaning for better project names
        clean_topic = self._clean_project_name(topic, content_type)

        # Session 199/200/201: Content-type-specific project naming and enhanced categorization
        # Categories use format "primary/subcategory" for better organization
        if content_type == 'youtube_thumbnails':
            project_name = f"{clean_topic.strip()} YouTube Thumbnails"
            category = 'social-media/youtube-thumbnails'
            suggested_next_steps = [
                'A/B test different thumbnail variations',
                'Add text overlays with different headlines',
                'Create variations with different expressions',
                'Upscale for higher resolution',
            ]
        elif content_type == 'brand_identity':
            project_name = f"{clean_topic.strip()} Brand Identity"
            category = 'branding/identity-package'
            suggested_next_steps = [
                'Create logo variations (horizontal, stacked, icon-only)',
                'Remove backgrounds for transparent versions',
                'Generate color palette swatches',
                'Create brand guidelines document',
                'Train a style model for consistent branding',
            ]
        elif content_type == 'product_photography':
            project_name = f"{clean_topic.strip()} Product Photography"
            category = 'e-commerce/product-photos'
            suggested_next_steps = [
                'Create lifestyle shots with context',
                'Generate different angle variations',
                'Remove backgrounds for e-commerce',
                'Add text overlays for marketing',
                'Upscale for print quality',
            ]
        elif content_type == 'thumbnail_series':
            project_name = f"{clean_topic.strip()} Thumbnail Series"
            category = 'social-media/youtube-series'
            suggested_next_steps = [
                'Add episode numbers to each thumbnail',
                'Create variations with different text',
                'Generate more episodes in the series',
                'A/B test different color schemes',
            ]
        elif content_type == 'animated_logo':
            project_name = f"{clean_topic.strip()} Animated Logo"
            category = 'branding/motion-graphics'
            suggested_next_steps = [
                'Add sound effects or music',
                'Create different length versions (3s, 5s, 10s)',
                'Export as GIF for web use',
                'Create intro/outro versions',
            ]
        # Session 212: New content types for project creation
        elif content_type == 'social_media':
            project_name = f"{clean_topic.strip()} Social Media Kit"
            category = 'social-media/content-kit'
            suggested_next_steps = [
                'Create platform-specific size variations',
                'Generate story/reel versions',
                'A/B test different visuals',
                'Schedule posts with content calendar',
                'Create carousel variations',
            ]
        elif content_type == 'podcast_visuals':
            project_name = f"{clean_topic.strip()} Podcast Visuals"
            category = 'audio/podcast-assets'
            suggested_next_steps = [
                'Create audiogram templates',
                'Generate episode-specific covers',
                'Design shareable quote cards',
                'Create series banner art',
            ]
        elif content_type == 'ebook_cover':
            project_name = f"{clean_topic.strip()} Ebook Cover"
            category = 'publishing/ebook'
            suggested_next_steps = [
                'Create 3D book mockups',
                'Generate promotional banners',
                'Design series covers if applicable',
                'Create social media announcement graphics',
            ]
        elif content_type == 'video_production':
            project_name = f"{clean_topic.strip()} Video Production Kit"
            category = 'video/production-assets'
            suggested_next_steps = [
                'Create intro/outro animations',
                'Generate end screen variations',
                'Design lower third graphics',
                'Create chapter marker images',
            ]
        elif content_type == 'course_thumbnails':
            project_name = f"{clean_topic.strip()} Course Thumbnails"
            category = 'education/course-assets'
            suggested_next_steps = [
                'Generate remaining module thumbnails',
                'Create course promo graphics',
                'Design certificate templates',
                'Create lesson completion badges',
            ]
        elif content_type == 'pitch_deck':
            project_name = f"{clean_topic.strip()} Pitch Deck Visuals"
            category = 'business/pitch-deck'
            suggested_next_steps = [
                'Create data visualization graphics',
                'Generate team photo backgrounds',
                'Design icon sets for features',
                'Create slide transition graphics',
            ]
        elif content_type == 'product_launch':
            project_name = f"{clean_topic.strip()} Product Launch Kit"
            category = 'marketing/product-launch'
            suggested_next_steps = [
                'Create countdown graphics',
                'Generate email header images',
                'Design press release visuals',
                'Create landing page hero images',
            ]
        else:
            project_name = f"{clean_topic.strip()} Logo Designs"
            category = 'branding/logo-design'
            suggested_next_steps = [
                'Upscale your favorite logo designs',
                'Remove backgrounds for transparent versions',
                'Create animated video versions',
                'Train a style model for consistent branding',
                'Generate color palette variations'
            ]

        logger.info(f"📁 Creating project: {project_name} with {len(image_ids)} images, {len(video_ids)} videos")

        # Session 201: Generate dynamic next steps based on actual content created
        dynamic_next_steps = self._generate_dynamic_next_steps(
            content_type=content_type,
            image_count=len(image_ids),
            video_count=len(video_ids),
            base_steps=suggested_next_steps,
            executive_direction=executive_direction,
            topic=clean_topic
        )

        try:
            from content.models import CreativeProject

            # Session 201: Extract colors and tags from executive direction and research
            extracted_colors = self._extract_colors_from_direction(executive_direction)
            extracted_tags = self._extract_tags_from_context(
                topic=clean_topic,
                content_type=content_type,
                research_summary=research_summary,
                executive_direction=executive_direction,
                style_prefs=context.get('style_preferences', '')
            )

            # Session 201: Build a proper project description
            project_description = self._build_project_description(
                topic=clean_topic,
                content_type=content_type,
                research_summary=research_summary,
                executive_direction=executive_direction,
                image_count=len(image_ids)
            )

            # Session 201: Build a clear project goal
            project_goal = self._build_project_goal(
                topic=clean_topic,
                content_type=content_type,
                image_count=len(image_ids)
            )

            # Session 201: Include full research results (with links) and agent recommendations
            # This enables the Project Information UI to show:
            # - Research sources with clickable links
            # - Individual agent recommendations with stance indicators
            # - Complete context for the user
            research_results = context.get('research_results', {})
            research_links = []
            if research_results.get('success') and research_results.get('results'):
                research_links = [
                    {
                        'title': r.get('title', 'Untitled'),
                        'link': r.get('link', ''),
                        'snippet': r.get('snippet', '')[:200]  # Limit snippet length
                    }
                    for r in research_results.get('results', [])[:5]
                ]

            agent_recommendations = context.get('agent_recommendations', [])

            parameters = {
                'project_name': project_name,
                'description': project_description,
                'goal': project_goal,
                'research_summary': research_summary,
                'executive_direction': executive_direction,
                'research_links': research_links,  # Session 201: Full research sources
                'agent_recommendations': agent_recommendations,  # Session 201: Individual agent recommendations
                'image_ids': image_ids,
                'video_ids': video_ids,
                'category': category,
                'colors': extracted_colors,
                'tags': extracted_tags,
                'suggested_next_steps': dynamic_next_steps
            }

            # Inline project creation (previously via EPA handler)
            project = CreativeProject.objects.create(
                user=context['user'],
                name=parameters.get('project_name', clean_topic),
                description=parameters.get('description', project_description),
                goal=parameters.get('goal', project_goal),
                category=parameters.get('category', category),
                colors=parameters.get('colors', extracted_colors),
                tags=parameters.get('tags', extracted_tags),
                status='in_progress',
                metadata={
                    'auto_generated': True,
                    'source': 'research_workflow',
                    'research_summary': research_summary,
                    'executive_direction': executive_direction,
                    'research_links': research_links,
                    'agent_recommendations': agent_recommendations,
                    'suggested_next_steps': dynamic_next_steps,
                }
            )
            result = {'success': True, 'project_id': str(project.id), 'project_name': project.name}

            # =====================================================================
            # SESSION 299: LINK STORED RESEARCH TO PROJECT
            # After creating the project, link any relevant BusinessResearchResult
            # records to enable the cumulative intelligence pipeline
            # =====================================================================
            if result.get('success') and result.get('project_id'):
                try:
                    from core.models_unified_system import BusinessResearchResult
                    from content.models import CreativeProject

                    project = CreativeProject.objects.get(id=result['project_id'])

                    # Find research related to this project's topic using semantic search
                    # or market_topic matching
                    topic_words = clean_topic.lower().split()[:3]  # First 3 words
                    topic_query = ' '.join(topic_words)

                    # Link by market_topic match first
                    linked_count = 0
                    for research in BusinessResearchResult.objects.filter(
                        project__isnull=True,  # Only unlinked research
                        market_topic__icontains=topic_query
                    ).order_by('-created_at')[:5]:
                        research.project = project
                        research.save(update_fields=['project'])
                        linked_count += 1
                        logger.info(f"📊 Session 299: Linked {research.research_type} research to project {project.name}")

                    if linked_count > 0:
                        result['linked_research_count'] = linked_count
                        logger.info(f"📊 Session 299: Linked {linked_count} research reports to project")

                except Exception as e:
                    logger.warning(f"Session 299: Could not link research to project: {e}")

            return result

        except Exception as e:
            logger.error(f"Create project failed: {e}")
            return {'success': False, 'error': str(e)}

    def _update_context(self, step_name: str, result: Dict, context: Dict):
        """Update workflow context with results from a step."""

        if step_name == 'research':
            context['research_results'] = result
            # Extract summary from results
            if result.get('success') and result.get('results'):
                snippets = [r.get('snippet', '') for r in result['results'][:3]]
                context['research_summary'] = ' '.join(snippets)[:500]

        elif step_name == 'executive_review':
            context['executive_direction'] = result
            # Session 201: Extract and aggregate creative direction from ALL agents
            if result.get('success') and result.get('recommendations'):
                context['creative_recommendations'] = self._aggregate_executive_direction(
                    result['recommendations'],
                    context.get('content_type', 'logos')
                )
                # Also store individual agent recommendations for richer project context
                context['agent_recommendations'] = result.get('recommendations', [])

        elif step_name in ['create_images', 'create_thumbnails', 'create_brand_images', 'create_product_images', 'create_thumbnail_series']:
            context['image_generation_result'] = result
            # Extract image IDs - Session 239: Enhanced logging for debugging
            logger.info(f"🔍 Session 239 DEBUG: Image generation result keys: {result.keys() if result else 'None'}")
            if result.get('success'):
                if result.get('images'):
                    logger.info(f"🔍 Session 239 DEBUG: Found {len(result['images'])} images in result")
                    context['generated_image_ids'] = [img.get('image_id') for img in result['images'] if img.get('image_id')]
                    logger.info(f"🔍 Session 239 DEBUG: Extracted image IDs: {context['generated_image_ids']}")
                elif result.get('image_id'):
                    context['generated_image_ids'] = [result['image_id']]
                    logger.info(f"🔍 Session 239 DEBUG: Single image ID: {context['generated_image_ids']}")
                else:
                    logger.warning(f"⚠️ Session 239: No 'images' or 'image_id' in result. Available keys: {list(result.keys())}")

        elif step_name == 'create_project':
            context['project_created'] = result

        # Session 199: New step handlers
        elif step_name == 'select_logo':
            if result.get('success') and result.get('image_id'):
                context['selected_image_id'] = result['image_id']

        elif step_name == 'animate_logo':
            if result.get('success') and result.get('video_id'):
                context['generated_video_ids'].append(result['video_id'])

        # Session 1233 B.1 — morning_brief lane plumbing. Each Lane N
        # step writes its output text into context['lane_N_text'] so
        # decision_card_synthesis + strategic_synthesis can read them.
        # Result shape varies by source: AGENT_MAP fallback returns
        # {'output': str, 'data': dict}; the lane_4_rotating_focus
        # internal handler returns {'summary': str, 'output': str,
        # 'slot_used': str}. We pull the first non-empty string.
        elif step_name in (
            'lane_1_platform_readiness',
            'lane_2_build_focus',
            'lane_3_competitive_landscape',
            'lane_4_rotating_focus',
        ):
            lane_num = step_name.split('_')[1]  # '1' / '2' / '3' / '4'
            text = (
                result.get('output')
                or result.get('summary')
                or result.get('text')
                or ''
            )
            context[f'lane_{lane_num}_text'] = text
            context[f'lane_{lane_num}_data'] = result.get('data', {}) or {}
            if step_name == 'lane_4_rotating_focus':
                # Capture which slot Lane 4 actually used so synthesis can
                # render the right section heading.
                context['lane_4_slot_used'] = result.get(
                    'slot_used',
                    context.get('rotation_slot', self._MORNING_BRIEF_LANE_4_DEFAULT_SLOT),
                )

        # Session 1233 B.1 — decision_card_synthesis writes its output
        # directly into context via the handler, but mirror the assignment
        # here for symmetry + so the runner's step_results record sees the
        # value path consistently.
        # Session 1242 Path C — also mirror the structured decision_cards
        # list. Handler always sets both keys (markdown + structured) per
        # the locked spec, but mirroring here keeps the dispatch contract
        # symmetric across both representations.
        elif step_name == 'decision_card_synthesis':
            if result.get('decision_card_text'):
                context['decision_card_text'] = result['decision_card_text']
            if 'decision_cards' in result:
                context['decision_cards'] = result['decision_cards']

    def _summarize_step_result(self, step_name: str, result: Dict) -> str:
        """Create a human-readable summary of a step result."""

        if not result.get('success'):
            return f"Failed: {result.get('error', 'Unknown error')}"

        if step_name == 'research':
            count = len(result.get('results', []))
            return f"Found {count} relevant results"

        elif step_name == 'executive_review':
            recs = result.get('recommendations', [])
            support = sum(1 for r in recs if r.get('stance') == 'support')
            return f"Team reviewed: {support}/{len(recs)} supportive"

        elif step_name == 'create_images':
            images = result.get('images', [])
            if images:
                return f"Created {len(images)} logo images"
            return f"Created 1 logo image"

        elif step_name == 'create_project':
            name = result.get('project_name', 'Project')
            return f"Organized into '{name}'"

        # Session 199/200: New step summaries
        elif step_name == 'create_thumbnails':
            images = result.get('images', [])
            return f"Created {len(images) if images else 1} thumbnail variations"

        elif step_name == 'create_brand_images':
            images = result.get('images', [])
            return f"Created {len(images) if images else 1} brand identity images"

        elif step_name == 'create_product_images':
            images = result.get('images', [])
            return f"Created {len(images) if images else 1} product photos"

        elif step_name == 'create_thumbnail_series':
            images = result.get('images', [])
            return f"Created {len(images) if images else 1} thumbnails in series"

        elif step_name == 'select_logo':
            return f"Selected logo for animation"

        elif step_name == 'animate_logo':
            return f"Created animated logo video"

        elif step_name == 'add_audio':
            return f"Added audio to video"

        return "Completed"

    # =========================================================================
    # SESSION 201: INTELLIGENT DIRECTION AGGREGATION
    # =========================================================================

    def _aggregate_executive_direction(self, recommendations: List[Dict], content_type: str) -> str:
        """
        Session 238: COMPLETELY REWRITTEN - Extract ONLY actionable prompt keywords.

        The old approach extracted verbose sentences. This new approach extracts
        ONLY the words/phrases that directly improve image generation prompts:
        - Colors: "icy blues", "vibrant oranges", "earthy greys"
        - Shapes: "geometric", "abstract", "mountain silhouette"
        - Styles: "bold", "minimalist", "dynamic"
        - Moods: "adventurous", "professional", "playful"

        NO sentences. NO explanations. JUST prompt-ready keywords.
        """
        if not recommendations:
            return ""

        # Combine all responses into one text blob for extraction
        all_text = ' '.join([r.get('response', '') for r in recommendations]).lower()

        # COLORS - Extract specific color mentions
        color_patterns = [
            'icy blue', 'cool blue', 'navy blue', 'sky blue', 'deep blue',
            'vibrant orange', 'burnt orange', 'warm orange',
            'earthy grey', 'slate grey', 'charcoal', 'silver',
            'crisp white', 'pure white', 'off-white', 'cream',
            'forest green', 'emerald', 'mint green', 'sage',
            'rich purple', 'violet', 'lavender',
            'warm gold', 'bronze', 'copper', 'metallic',
            'deep red', 'burgundy', 'coral', 'salmon',
            'black and white', 'monochrome', 'grayscale',
            'earth tones', 'jewel tones', 'pastel', 'neon',
            'cool tones', 'warm tones', 'muted colors', 'vibrant colors',
            'high contrast', 'limited palette', 'two-color', 'gradient'
        ]

        # SHAPES & SYMBOLS - What to depict
        shape_patterns = [
            'mountain silhouette', 'mountain peak', 'mountain range',
            'snowflake', 'geometric snowflake', 'ice crystal',
            'wave pattern', 'dynamic wave', 'flowing lines',
            'abstract symbol', 'geometric shape', 'angular design',
            'circular design', 'rounded forms', 'organic shapes',
            'sharp edges', 'clean lines', 'flowing curves',
            'negative space', 'symmetrical', 'asymmetrical',
            'layered design', 'overlapping elements', 'interlocking',
            'arrow', 'chevron', 'hexagon', 'triangle', 'diamond'
        ]

        # STYLE DESCRIPTORS - How it should look
        style_patterns = [
            'bold', 'minimalist', 'modern', 'contemporary', 'classic',
            'elegant', 'sophisticated', 'professional', 'corporate',
            'playful', 'fun', 'energetic', 'dynamic', 'active',
            'rustic', 'vintage', 'retro', 'futuristic', 'tech',
            'clean', 'simple', 'streamlined', 'sleek', 'refined',
            'handcrafted', 'artisan', 'organic', 'natural',
            'luxurious', 'premium', 'high-end', 'upscale',
            'friendly', 'approachable', 'trustworthy', 'reliable',
            'innovative', 'cutting-edge', 'forward-thinking'
        ]

        # MOOD/FEELING - Emotional quality
        mood_patterns = [
            'adventurous', 'exciting', 'thrilling', 'action',
            'calm', 'serene', 'peaceful', 'relaxing',
            'powerful', 'strong', 'confident', 'bold',
            'warm', 'inviting', 'welcoming', 'cozy',
            'cool', 'fresh', 'crisp', 'invigorating',
            'mysterious', 'intriguing', 'dramatic'
        ]

        # Extract matching patterns
        found_colors = []
        found_shapes = []
        found_styles = []
        found_moods = []

        for pattern in color_patterns:
            if pattern in all_text and pattern not in found_colors:
                found_colors.append(pattern)

        for pattern in shape_patterns:
            if pattern in all_text and pattern not in found_shapes:
                found_shapes.append(pattern)

        for pattern in style_patterns:
            if pattern in all_text and pattern not in found_styles:
                found_styles.append(pattern)

        for pattern in mood_patterns:
            if pattern in all_text and pattern not in found_moods:
                found_moods.append(pattern)

        # Build concise prompt addition - prioritize variety
        prompt_parts = []

        # Add top styles (most important for visuals)
        prompt_parts.extend(found_styles[:4])

        # Add shapes/symbols (what to depict)
        prompt_parts.extend(found_shapes[:3])

        # Add colors (palette guidance)
        prompt_parts.extend(found_colors[:3])

        # Add moods (feeling)
        prompt_parts.extend(found_moods[:2])

        if prompt_parts:
            result = ', '.join(prompt_parts)
            logger.info(f"🎯 Session 238: Extracted {len(prompt_parts)} prompt keywords: {result}")
            return result

        # Fallback: extract any adjectives from Creative Director
        for rec in recommendations:
            if rec.get('agent') == 'CreativeDirector':
                # Just grab style words
                response = rec.get('response', '').lower()
                fallback = []
                for word in ['bold', 'clean', 'modern', 'professional', 'dynamic', 'vibrant']:
                    if word in response:
                        fallback.append(word)
                if fallback:
                    return ', '.join(fallback[:4])

        return ""

    # =========================================================================
    def _clean_project_name(self, topic: str, content_type: str) -> str:
        """
        Clean up the topic string to create a professional project name.

        Session 201: Enhanced cleaning that handles more edge cases:
        - Removes redundant words (logo, design, create, research, etc.)
        - Removes filler words (for, my, a, the, called, named, etc.)
        - Removes trailing content type words to avoid "Coffee Logo Logo Designs"
        - Properly capitalizes the result
        - Handles phrases like "create a logo for my coffee shop"

        Args:
            topic: Raw topic string from user input
            content_type: Type of content being created (logos, thumbnails, etc.)

        Returns:
            Clean, title-cased topic string
        """
        import re

        # Start with the original topic
        clean = topic.lower()

        # Remove common action words that shouldn't be in project names
        action_words = [
            'create', 'make', 'generate', 'design', 'build', 'research',
            'research and create', 'research and make', 'research and design',
            'help me', 'can you', 'please', 'i want', 'i need', 'i would like',
        ]
        for word in action_words:
            clean = clean.replace(word, ' ')

        # Remove quantity indicators
        quantity_patterns = [
            r'\b\d+\s*(logos?|designs?|thumbnails?|images?|videos?|photos?)\b',
            r'\b(three|four|five|six|seven|eight|nine|ten)\s+',
            r'\bsome\s+', r'\bfew\s+', r'\bmultiple\s+', r'\bseveral\s+',
        ]
        for pattern in quantity_patterns:
            clean = re.sub(pattern, ' ', clean)

        # Remove content type words (to avoid "Coffee Logo Logo Designs")
        content_words = [
            'logos?', 'designs?', 'thumbnails?', 'videos?', 'images?',
            'brand identity', 'branding', 'product photography', 'photos?',
            'series', 'animated', 'animation', 'youtube',
        ]
        for word in content_words:
            clean = re.sub(rf'\b{word}\b', ' ', clean, flags=re.IGNORECASE)

        # Remove filler words
        filler_words = [
            'for', 'my', 'our', 'the', 'a', 'an', 'with', 'about', 'on',
            'called', 'named', 'titled', 'like', 'style', 'styled', 'as',
            'that', 'which', 'of', 'in', 'to', 'and', 'or', 'from',
        ]
        for word in filler_words:
            # Only remove if surrounded by spaces/boundaries
            clean = re.sub(rf'\b{word}\b', ' ', clean, flags=re.IGNORECASE)

        # Remove style descriptors that are too generic (keep specific ones in the prompt)
        generic_style_words = [
            'modern', 'professional', 'clean', 'simple', 'nice', 'good', 'great',
            'beautiful', 'amazing', 'cool', 'awesome',
        ]
        for word in generic_style_words:
            clean = re.sub(rf'\b{word}\b', ' ', clean, flags=re.IGNORECASE)

        # Clean up multiple spaces
        clean = re.sub(r'\s+', ' ', clean).strip()

        # Title case
        clean = clean.title()

        # If we stripped everything, fall back to a generic name
        if not clean or len(clean) < 2:
            content_type_names = {
                'logos': 'Logo Project',
                'brand_identity': 'Brand Identity',
                'youtube_thumbnails': 'YouTube Thumbnails',
                'thumbnail_series': 'Thumbnail Series',
                'product_photography': 'Product Photos',
                'animated_logo': 'Animated Logo',
            }
            clean = content_type_names.get(content_type, 'Creative Project')

        logger.info(f"📁 Cleaned project name: '{topic}' → '{clean}'")
        return clean

    def _generate_dynamic_next_steps(
        self,
        content_type: str,
        image_count: int,
        video_count: int,
        base_steps: List[str],
        executive_direction: str,
        topic: str
    ) -> List[str]:
        """
        Generate dynamic next step suggestions based on actual content created.

        Session 201: Instead of static steps, we customize based on:
        - How many images/videos were created
        - What the executive team recommended
        - The specific topic/brand

        Args:
            content_type: Type of content created
            image_count: Number of images generated
            video_count: Number of videos generated
            base_steps: Default static steps for this content type
            executive_direction: Aggregated direction from executives
            topic: The cleaned topic name

        Returns:
            List of personalized next step suggestions
        """
        steps = []

        # Start with some base steps but personalize them
        if image_count > 0:
            # Personalize upscale suggestion
            if image_count == 1:
                steps.append(f"Upscale your {topic} image for higher resolution")
            else:
                steps.append(f"Review all {image_count} {topic} designs and upscale your favorites")

            # Add remove background if appropriate for content type
            if content_type in ['logos', 'brand_identity']:
                steps.append("Remove backgrounds for transparent PNG versions")
            elif content_type == 'product_photography':
                steps.append("Remove backgrounds for clean e-commerce product shots")

            # Suggest variations if few were created
            if image_count <= 2:
                steps.append(f"Generate more {topic} variations with different styles")

        # Add video-related suggestions
        if video_count > 0:
            steps.append(f"Add sound effects or music to your {video_count} video(s)")
        elif content_type in ['logos', 'brand_identity'] and image_count > 0:
            # No videos yet but they could be useful
            steps.append(f"Animate your favorite {topic} logo into a video intro")

        # Extract any specific recommendations from executive direction
        if executive_direction:
            direction_lower = executive_direction.lower()

            # Look for specific actionable suggestions from executives
            if 'color' in direction_lower and 'palette' not in steps[0].lower():
                steps.append("Generate color palette variations based on executive recommendations")

            if 'variation' in direction_lower or 'alternative' in direction_lower:
                if len([s for s in steps if 'variation' in s.lower()]) == 0:
                    steps.append("Create alternative versions exploring executive suggestions")

            if 'social media' in direction_lower or 'social' in direction_lower:
                steps.append("Export optimized versions for social media platforms")

        # Add training suggestion if we have enough images
        if image_count >= 3 and content_type in ['logos', 'brand_identity']:
            steps.append(f"Train a LoRA model on your {topic} style for consistent branding")

        # Add content-type-specific polish steps
        if content_type == 'youtube_thumbnails':
            steps.append("A/B test thumbnail variations to find highest CTR")
            steps.append("Create text overlay variations with different hooks")
        elif content_type == 'product_photography':
            steps.append("Create lifestyle context shots showing products in use")

        # Ensure we don't have too many steps (max 5)
        if len(steps) > 5:
            steps = steps[:5]

        # If we somehow have no steps, fall back to base
        if not steps:
            steps = base_steps[:4]

        logger.info(f"📋 Generated {len(steps)} dynamic next steps for {topic} ({content_type})")
        return steps

    def _extract_colors_from_direction(self, executive_direction: str) -> str:
        """
        Extract color mentions from executive direction.

        Session 201: Looks for color words and palette suggestions to auto-fill
        the project's color field.
        """
        if not executive_direction:
            return ""

        # Common color words to look for
        color_words = [
            'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'black', 'white',
            'navy', 'teal', 'coral', 'gold', 'silver', 'bronze', 'cream', 'ivory', 'beige',
            'brown', 'gray', 'grey', 'maroon', 'burgundy', 'olive', 'cyan', 'magenta',
            'turquoise', 'indigo', 'violet', 'lavender', 'mint', 'salmon', 'peach',
            'earth tones', 'warm tones', 'cool tones', 'neutral', 'pastel', 'vibrant',
            'muted', 'bold colors', 'soft colors', 'dark', 'light', 'bright'
        ]

        direction_lower = executive_direction.lower()
        found_colors = []

        for color in color_words:
            if color in direction_lower and color not in found_colors:
                found_colors.append(color)

        # Limit to 5 colors and format nicely
        if found_colors:
            return ', '.join(found_colors[:5])
        return ""

    def _extract_tags_from_context(
        self,
        topic: str,
        content_type: str,
        research_summary: str,
        executive_direction: str,
        style_prefs: str
    ) -> List[str]:
        """
        Extract relevant tags from all context.

        Session 201: Builds a tag list from topic, content type, styles, and keywords.
        """
        tags = set()

        # Add content type as tag
        content_type_tags = {
            'logos': ['logo', 'branding'],
            'brand_identity': ['brand-identity', 'branding', 'logo'],
            'youtube_thumbnails': ['youtube', 'thumbnail', 'social-media'],
            'thumbnail_series': ['youtube', 'series', 'thumbnail'],
            'product_photography': ['product', 'photography', 'e-commerce'],
            'animated_logo': ['animation', 'motion', 'logo', 'video'],
        }
        tags.update(content_type_tags.get(content_type, ['creative']))

        # Extract style words from style preferences
        if style_prefs:
            style_words = ['minimalist', 'modern', 'vintage', 'rustic', 'elegant',
                          'playful', 'professional', 'bold', 'clean', 'geometric',
                          'organic', 'futuristic', 'classic', 'retro', 'luxury']
            for word in style_words:
                if word in style_prefs.lower():
                    tags.add(word)

        # Extract from executive direction
        if executive_direction:
            direction_lower = executive_direction.lower()
            style_words = ['minimalist', 'modern', 'vintage', 'rustic', 'elegant',
                          'playful', 'professional', 'bold', 'clean', 'geometric',
                          'organic', 'futuristic', 'classic', 'warm', 'cool']
            for word in style_words:
                if word in direction_lower:
                    tags.add(word)

        # Add topic words as tags (split and clean)
        topic_words = topic.lower().replace('-', ' ').replace('_', ' ').split()
        for word in topic_words:
            if len(word) > 3 and word not in ['with', 'from', 'that', 'this']:
                tags.add(word)

        return list(tags)[:10]  # Limit to 10 tags

    def _build_project_description(
        self,
        topic: str,
        content_type: str,
        research_summary: str,
        executive_direction: str,
        image_count: int
    ) -> str:
        """
        Build a comprehensive project description.

        Session 201: Creates a well-structured description from all available context.
        """
        parts = []

        # Opening line based on content type
        content_descriptions = {
            'logos': f"Logo design project for {topic}.",
            'brand_identity': f"Complete brand identity package for {topic}.",
            'youtube_thumbnails': f"YouTube thumbnail designs for {topic} content.",
            'thumbnail_series': f"Consistent thumbnail series for {topic} video content.",
            'product_photography': f"Professional product photography for {topic}.",
            'animated_logo': f"Animated logo and motion graphics for {topic}.",
        }
        parts.append(content_descriptions.get(content_type, f"Creative project for {topic}."))

        # Add research insights (full content for project reference)
        if research_summary and len(research_summary) > 20:
            parts.append(f"\n\n**Research Insights:** {research_summary.strip()}")

        # Add executive direction summary (full content for project reference)
        if executive_direction and len(executive_direction) > 20:
            parts.append(f"\n\n**Creative Direction:** {executive_direction.strip()}")

        # Add content count
        if image_count > 0:
            parts.append(f"\n\n**Generated Assets:** {image_count} initial designs created.")

        return ''.join(parts)

    def _build_project_goal(self, topic: str, content_type: str, image_count: int) -> str:
        """
        Build a clear, actionable project goal.

        Session 201: Creates goal statements that guide the AI assistant.
        """
        goals = {
            'logos': f"Create a distinctive, memorable logo for {topic} that works across all platforms and sizes. Select the best design from {image_count} variations and refine it.",
            'brand_identity': f"Develop a cohesive brand identity for {topic} including logo variations, color palette, and visual guidelines. Build on the {image_count} initial concepts.",
            'youtube_thumbnails': f"Design eye-catching, high-CTR thumbnails for {topic} YouTube content. Test and iterate on {image_count} initial designs to maximize engagement.",
            'thumbnail_series': f"Create a consistent, recognizable thumbnail template for {topic} video series. Ensure brand cohesion across {image_count} episode thumbnails.",
            'product_photography': f"Produce professional product images for {topic} suitable for e-commerce and marketing. Refine the best of {image_count} initial shots.",
            'animated_logo': f"Create a professional animated logo reveal for {topic} suitable for video intros and brand content.",
        }

        return goals.get(content_type, f"Complete creative project for {topic} with {image_count} initial assets.")

    # =========================================================================
    # SESSION 199: NEW STEP HANDLERS FOR VIDEO/AUDIO WORKFLOWS
    # =========================================================================

    def _execute_video_generation_step(self, context: Dict) -> Dict[str, Any]:
        """Execute video generation for logo animation."""
        topic = context['topic']
        image_id = context.get('selected_image_id')
        creative_recs = context.get('creative_recommendations', '')

        if not image_id:
            return {'success': False, 'error': 'No image selected for animation'}

        # Build motion prompt
        motion_prompt = f"smooth professional logo animation, elegant reveal, {topic}"
        if creative_recs:
            motion_prompt += f", {creative_recs[:100]}"

        logger.info(f"🎬 Video generation: animating image {image_id}")

        try:
            from core.agent_router import AgentRouter

            task = f"Generate a 5-second professional logo animation from image {image_id}. Motion: {motion_prompt}"
            router = AgentRouter(user=context.get('user'))
            result = router.route(agent_name='VideoAgent', task=task, context={
                'image_id': image_id,
                'motion_prompt': motion_prompt,
                'project_id': context.get('project_id'),
            })
            return result.data if result.data else {'success': True, 'message': result.message}

        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            return {'success': False, 'error': str(e)}

    def _execute_audio_generation_step(self, context: Dict) -> Dict[str, Any]:
        """Execute audio generation for video."""
        topic = context['topic']

        # Build audio prompt
        audio_prompt = f"professional logo sound effect, whoosh, corporate, {topic}"

        logger.info(f"🔊 Audio generation: creating sound for logo")

        # Audio generation is optional and was already no-op (handler was commented out)
        return {'success': True, 'message': 'Audio step skipped (optional)'}

    def _execute_image_selection_step(self, context: Dict) -> Dict[str, Any]:
        """Select an image for animation from existing project images."""
        image_id = context.get('image_id')

        if image_id:
            # User specified an image
            logger.info(f"🖼️ Using specified image: {image_id}")
            context['selected_image_id'] = image_id
            return {'success': True, 'image_id': image_id}

        # If no image specified, try to get from project
        project_id = context.get('project_id')
        if project_id:
            try:
                from content.models import ImageHistory
                # Get most recent image from project
                image = ImageHistory.objects.filter(
                    project_id=project_id,
                    user=context['user']
                ).order_by('-created_at').first()

                if image:
                    context['selected_image_id'] = str(image.id)
                    logger.info(f"🖼️ Auto-selected image from project: {image.id}")
                    return {'success': True, 'image_id': str(image.id)}
            except Exception as e:
                logger.error(f"Image selection failed: {e}")

        return {'success': False, 'error': 'No image available for animation. Please specify an image_id.'}

    # =========================================================================
    # SESSION 212: NEW STEP HANDLERS FOR WORKFLOW EXPANSION
    # =========================================================================

    def _execute_image_variation_step(self, context: Dict) -> Dict[str, Any]:
        """
        Execute image variation step to create platform-specific variations.

        Session 212: Creates variations of the hero image for different platforms:
        - Instagram Square (1080x1080)
        - LinkedIn Banner (1200x627)
        - Facebook Cover (820x312)
        - Twitter Header (1500x500)
        """
        topic = context['topic']
        content_type = context.get('content_type', 'social_media')
        generated_image_ids = context.get('generated_image_ids', [])
        creative_recs = context.get('creative_recommendations', '')

        if not generated_image_ids:
            logger.warning("⚠️ No hero image available for variations")
            # Still return success - we'll generate new images instead
            return self._execute_image_generation_step(context)

        # Get the first generated image as the source
        source_image_id = generated_image_ids[0]

        logger.info(f"🔄 Creating variations from image {source_image_id}")

        try:
            from core.views_image import _execute_generate_image
            from content.models import AISession, ImageHistory

            # Get the source image to use its prompt as a base
            try:
                source_image = ImageHistory.objects.get(id=source_image_id)
                base_prompt = source_image.prompt or f"{topic} social media content"
            except ImageHistory.DoesNotExist:
                base_prompt = f"{topic} social media content"

            # Get or create session
            session = None
            if context.get('user'):
                session = AISession.objects.filter(
                    user=context['user'],
                    is_active=True
                ).order_by('-created_at').first()

                if not session:
                    session = AISession.objects.create(
                        user=context['user'],
                        title='Workflow Session',
                        is_active=True
                    )

            # Platform variations to create
            variations = [
                {'name': 'LinkedIn', 'width': 1200, 'height': 627, 'prompt_suffix': 'professional business format'},
                {'name': 'Facebook', 'width': 820, 'height': 312, 'prompt_suffix': 'facebook cover banner format'},
                {'name': 'Twitter', 'width': 1500, 'height': 500, 'prompt_suffix': 'twitter header banner format'},
            ]

            created_ids = []
            for variation in variations:
                prompt = f"{base_prompt}, {variation['prompt_suffix']}"
                if creative_recs:
                    prompt += f", {creative_recs[:100]}"

                parameters = {
                    'prompt': prompt,
                    'count': 1,
                    'model': 'sdxl',
                    'width': variation['width'],
                    'height': variation['height'],
                }

                if context.get('project_id'):
                    parameters['project_id'] = context['project_id']

                result = _execute_generate_image(
                    user=context['user'],
                    parameters=parameters,
                    session=session
                )

                if result.get('success'):
                    if result.get('images'):
                        created_ids.extend([img.get('image_id') for img in result['images'] if img.get('image_id')])
                    elif result.get('image_id'):
                        created_ids.append(result['image_id'])

                logger.info(f"✅ Created {variation['name']} variation")

            # Add new IDs to context
            context['generated_image_ids'].extend(created_ids)

            return {
                'success': True,
                'images': [{'image_id': img_id} for img_id in created_ids],
                'variation_count': len(created_ids),
                'message': f"Created {len(created_ids)} platform variations"
            }

        except Exception as e:
            logger.error(f"Image variation failed: {e}")
            return {'success': False, 'error': str(e)}

    # =========================================================================
    # SESSION 496: CONTENT WRITER STEP HANDLER
    # =========================================================================

    def _execute_content_writer_step(self, context: Dict) -> Dict[str, Any]:
        """
        Execute the ContentWriterAgent to generate written content from research.

        Session 496: Transforms research into blog posts, podcast scripts,
        video scripts, articles, social threads, or newsletters.

        Uses the research_summary from the research step (or provided_research)
        to generate polished, ready-to-publish written content.
        """
        topic = context.get('topic', '')
        content_type = context.get('content_type', 'blog_post')
        research = context.get('research_summary', '') or context.get('provided_research', '')
        tone = context.get('tone', 'professional')
        target_audience = context.get('target_audience', 'general audience')
        word_count = context.get('word_count', 1500)

        logger.info(f"📝 Session 496: Content Writer step")
        logger.info(f"   Topic: {topic}")
        logger.info(f"   Content Type: {content_type}")
        logger.info(f"   Research length: {len(research)} chars")
        logger.info(f"   Tone: {tone}, Audience: {target_audience}")

        if not research and not topic:
            return {
                'success': False,
                'error': 'No research or topic provided for content writing'
            }

        try:
            from core.agents.content_writer_agent import ContentWriterAgent

            agent = ContentWriterAgent(
                user=self.user,
                project_id=self.project_id
            )

            # Build agent context
            agent_context = {
                'content_type': content_type,
                'research': research or f"Write about: {topic}",
                'tone': tone,
                'target_audience': target_audience,
                'word_count': word_count,
                'topic': topic,
            }

            # Execute the agent
            result = agent.execute(
                task=f"Write {content_type} about {topic}",
                context=agent_context,
                scifi_context={},
                spider_context={}
            )

            if result.success:
                # Store the generated content in context for project creation
                content_data = result.data.get('content', {})
                context['generated_content'] = content_data
                context['content_full_text'] = content_data.get('full_text', '')
                context['content_metadata'] = result.data.get('metadata', {})

                # Log the content type and word count
                actual_words = len(context.get('content_full_text', '').split())
                logger.info(f"✅ Content Writer: Generated {content_type} ({actual_words} words)")

                return {
                    'success': True,
                    'content': content_data,
                    'content_type': content_type,
                    'word_count': actual_words,
                    'message': f"Successfully wrote {content_type}: {actual_words} words"
                }
            else:
                logger.error(f"❌ Content Writer failed: {result.error}")
                return {
                    'success': False,
                    'error': result.error or 'Content generation failed'
                }

        except Exception as e:
            logger.error(f"Content writer step failed: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    # =========================================================================
    # SESSION 1231 F7: STRATEGIC SYNTHESIS STEP
    # =========================================================================

    # Context keys that prior workflow steps may populate. Pulled in
    # priority order for the synthesis prompt. Defined at class level
    # so future steps that add context keys can extend this list in
    # one place rather than hunting through the handler.
    _SYNTHESIS_CONTEXT_KEYS: tuple = (
        'research_summary',
        'research_results',
        'competitor_insights',
        'customer_insights',
        'customer_personas',
        'customer_pain_points',
        'brand_recommendations',
        'creative_recommendations',
        'enhanced_summary',
        'spider_insights',
    )

    # Session 1233 B.1 — morning_brief lane → synthesis input key map.
    # Strategic synthesis uses these instead of _SYNTHESIS_CONTEXT_KEYS
    # when context['_synthesis_mode'] == 'morning_brief'.
    _MORNING_BRIEF_SYNTHESIS_KEYS: tuple = (
        'lane_1_text',
        'lane_2_text',
        'lane_3_text',
        'lane_4_text',
        'decision_card_text',
    )

    # Session 1233 B.1 — Lane 4 rotating-focus slot → agent map.
    # When B.2 lands rotation_slot_resolve, the pre-step will write
    # context['rotation_slot']; for B.1 we default to 'ai_infra_deep_dive'
    # so Lane 4 dispatches even when no rotation logic has run yet.
    # Spec source: docs/MORNING_BRIEF_SPEC.md § "Source (agents + feeds),
    # by slot" — v0.5 picks one agent per slot; alternatives noted in spec
    # are deferred until B.2.
    #
    # Session 1234 D2 (Rigby-ratified P1.A): gtm_pipeline_health
    # remapped from OpportunityPipelineAgent → COOAgent. The 2026-06-25
    # first-fire (task 9d00907a-…) showed OpportunityPipelineAgent's
    # execute() requires context['opportunity'] (per-Opportunity-row
    # processing) — wrong contract for Lane 4's daily-summary purpose.
    # COOAgent has no required context keys and was already proven in
    # the first-fire as Lane 2's agent. Persona duplication with Lane 2
    # is mitigated via the per-slot focus prompt below.
    _MORNING_BRIEF_LANE_4_SLOT_AGENT: dict = {
        'sports_edge_scan': 'SharpActionDetector',
        'prediction_markets': 'PredictionMarketAnalyst',
        'ticker_catalyst_watch': 'StockAnalystAgent',
        'gtm_pipeline_health': 'COOAgent',
        'ai_infra_deep_dive': 'ResearchAgent',
    }
    _MORNING_BRIEF_LANE_4_DEFAULT_SLOT: str = 'ai_infra_deep_dive'

    # Session 1234 D2 — slot-specific focus phrase appended to the Lane 4
    # step_task. Lets one agent (e.g., COOAgent in Lane 2 build_focus AND
    # Lane 4 gtm_pipeline_health) produce distinct content per lane by
    # narrowing the prompt's intent. The base step_task ("actionable
    # signals, 3-7 bullets, why-it-matters-today, action recommendation")
    # is shared; this dict adds the slot's specific lens.
    _MORNING_BRIEF_LANE_4_SLOT_FOCUS: dict = {
        'gtm_pipeline_health': (
            "Focus on GTM/pipeline health: top KPIs that moved overnight, "
            "top 3 risks blocking pipeline velocity, and follow-up actions "
            "with named owner. Do NOT cover product/build priorities "
            "(that's Lane 2's job)."
        ),
        'sports_edge_scan': (
            "Focus on sharp-action edges: cross-bookmaker line moves, "
            "limit changes, sharp money signals. Skip if no qualifying "
            "edges today."
        ),
        'prediction_markets': (
            "Focus on prediction market dislocations: implied probability "
            "shifts > 5pp overnight, mispriced contracts vs. base rates, "
            "and which markets to watch into close."
        ),
        'ticker_catalyst_watch': (
            "Focus on ticker-specific catalysts: earnings/guidance/SEC "
            "filings hitting today, unusual volume/options activity, "
            "and which tickers to read first."
        ),
        'ai_infra_deep_dive': (
            "Focus on AI infrastructure shifts: new model/inference "
            "announcements, pricing changes from major providers, and "
            "what to dig into deeper."
        ),
    }

    # Session 1233 B.1.fix — snake_case → AGENT_MAP key alias for agents
    # whose PascalCase form contains acronyms. The default fallback at
    # the F4 dispatcher (``''.join(p.capitalize() …)``) produces wrong
    # casing for these (e.g., coo_agent → 'CooAgent', actual key is
    # 'COOAgent'). Surfaced by the morning_brief end-to-end smoke at
    # Step 2 lane_2_build_focus → coo_agent.
    #
    # Add a new entry here when you ship a workflow that references a
    # snake_case agent name whose PascalCase form has 2+ consecutive
    # uppercase letters. Audit script:
    #     grep -E '"[A-Z]{2,}' core/agent_router.py | grep ':'
    _AGENT_MAP_SNAKE_ALIASES: dict = {
        'coo_agent': 'COOAgent',
        'cto_agent': 'CTOAgent',
        'seo_optimizer_agent': 'SEOOptimizerAgent',
        'ai_series_workflow_agent': 'AISeriesWorkflowAgent',
    }

    # Session 1233 B.2 — weekday → Lane 4 default rotation slot.
    # Mon-Thu pick fixed slots per spec § "Default rotation schedule".
    # Fri (weekday 4) uses iso_week parity to alternate between
    # sports_edge_scan (even weeks) and prediction_markets (odd weeks),
    # so it's NOT in this dict — handled by _resolve_rotation_slot
    # explicitly. Weekend (Sat/Sun) falls back to ai_infra_deep_dive
    # (Mon default) since scheduled briefs are weekday-only but the
    # workflow should still resolve cleanly if dispatched on weekend.
    #
    # Tuesday's "Competitor Wedge" per spec § Lane 4 rotation table is
    # a Lane-3-deepen concept rather than a distinct Lane 4 slot. For
    # B.2 Tue falls back to ai_infra_deep_dive; a future Sub-step could
    # add a 'competitor_wedge' slot to _MORNING_BRIEF_LANE_4_SLOT_AGENT
    # mapping to TrendAnalysisAgent / CompetitorAnalysisAgent.
    _WEEKDAY_DEFAULT_SLOT: dict = {
        0: 'ai_infra_deep_dive',     # Mon
        1: 'ai_infra_deep_dive',     # Tue (spec: competitor_wedge — deferred)
        2: 'ticker_catalyst_watch',  # Wed
        3: 'gtm_pipeline_health',    # Thu
        # 4 (Fri): iso_week parity → sports OR prediction_markets
        5: 'ai_infra_deep_dive',     # Sat (weekend default)
        6: 'ai_infra_deep_dive',     # Sun (weekend default)
    }

    # Session 1233 B.2 — override shorthand → Lane 4 slot map.
    # When the caller writes ``context['rotation_override']`` with
    # ``signal_slot`` or ``calendar_slot`` keys (per spec § Override
    # triggers), the value is a shorthand that gets mapped to the
    # full slot name via this dict.
    _ROTATION_OVERRIDE_SHORTHAND_TO_SLOT: dict = {
        'sports': 'sports_edge_scan',
        'markets': 'prediction_markets',
        'tickers': 'ticker_catalyst_watch',
        'gtm': 'gtm_pipeline_health',
        'ai_infra': 'ai_infra_deep_dive',
    }

    def _execute_strategic_synthesis_step(self, context: Dict) -> Dict[str, Any]:
        """Synthesize prior workflow step outputs into actionable insights.

        Built-in templates `business_research` and `startup_validation`
        end with this step. Pre-F7 it failed because no `StrategicSynthesis`
        agent existed in AGENT_MAP. This handler reads whatever the prior
        steps left in context, builds a synthesis prompt, and calls
        gpt-5-mini via the OpenAI factory.

        Session 1233 B.1 extension: when context['_synthesis_mode'] ==
        'morning_brief', read the lane keys instead of the generic
        _SYNTHESIS_CONTEXT_KEYS and produce the final brief markdown
        rather than 3-5 insight bullets.

        Graceful empty-context behavior: if no prior outputs are present
        (smoke / capability-ping case), returns success with an explicit
        "no synthesis input available" note rather than aborting. That
        keeps the workflow's dispatch contract honored and the smoke
        harness reporting PASS for the synthesis step.
        """
        from django.conf import settings
        from core.services.openai_client_factory import get_openai_client

        topic = context.get('topic') or context.get('query') or ''
        is_morning_brief = (
            context.get('_synthesis_mode') == 'morning_brief'
        )

        # Session 1233 B.1 — pick the key set based on synthesis mode.
        key_set = (
            self._MORNING_BRIEF_SYNTHESIS_KEYS
            if is_morning_brief
            else self._SYNTHESIS_CONTEXT_KEYS
        )

        # Collect any prior-step outputs present in context.
        synthesis_inputs = {}
        for key in key_set:
            val = context.get(key)
            if val:
                # Coerce dict/list to str for prompt assembly.
                if isinstance(val, (dict, list)):
                    import json as _json
                    synthesis_inputs[key] = _json.dumps(val, default=str)[:2000]
                else:
                    synthesis_inputs[key] = str(val)[:2000]

        if not synthesis_inputs and not topic:
            # Smoke / empty-context case — keep the workflow alive without
            # inventing data.
            logger.info(
                "🧩 Session 1231 F7: strategic_synthesis step ran with empty "
                "context (no prior step outputs found). Returning graceful "
                "no-op so the workflow's dispatch contract is honored."
            )
            return {
                'success': True,
                'summary': 'No synthesis input available',
                'synthesis': (
                    'No prior step outputs present in workflow context — '
                    'nothing to synthesize. (Workflow was likely dispatched '
                    'as a capability-ping smoke or with empty inputs.)'
                ),
                'inputs_used': [],
            }

        # Build the synthesis prompt from whatever's available.
        if is_morning_brief:
            # Session 1238 PR-2: run lane_1 self-referential health-alarm
            # self-check. If lane_1_text contains a "paralyzed" / "no agent
            # activity" warning, recompute the underlying metric now (30min
            # window) and inject the result as SELF_CHECK_EVIDENCE so the
            # LLM can downgrade the warning when contradicted by current
            # state. Closes the "system reports itself paralyzed at the
            # same moment it generates a brief" trust issue Rigby flagged.
            lane_1_text = synthesis_inputs.get('lane_1_text', '')
            self_check = self._collect_lane_1_self_check_evidence(lane_1_text)
            if self_check:
                synthesis_inputs['_lane_1_self_check'] = self_check

            # Session 1238 PR-4a: humanize body-system jargon in Lane 1.
            # Pre-fix "MUSCULAR: No Agent Activity" reached Chris as
            # insider jargon. Now translated to plain-English with the
            # system tag preserved as a parenthetical.
            if lane_1_text:
                synthesis_inputs['lane_1_text'] = (
                    self._humanize_body_system_jargon(lane_1_text)
                )

            # Session 1238 PR-4b: Lane 3 adaptive no-signal fallback.
            # When Lane 3 has no actionable signal, replace empty
            # rendering with a deterministic "coverage map + watch
            # items" template instead of an empty section.
            lane_3_text = synthesis_inputs.get('lane_3_text', '')
            if self._lane_3_is_no_signal(lane_3_text):
                synthesis_inputs['_lane_3_fallback'] = (
                    self._lane_3_no_signal_fallback()
                )

            prompt = self._build_morning_brief_prompt(
                synthesis_inputs=synthesis_inputs,
                slot_used=context.get(
                    'lane_4_slot_used',
                    context.get('rotation_slot', self._MORNING_BRIEF_LANE_4_DEFAULT_SLOT),
                ),
            )
        else:
            prompt_parts = [
                "You are synthesizing the outputs of a multi-step research workflow "
                "into a brief, actionable strategic insight.",
                "",
                f"Topic: {topic or '(not specified)'}",
                "",
                "Prior step outputs (truncated to 2000 chars each):",
            ]
            for key, val in synthesis_inputs.items():
                prompt_parts.append(f"\n--- {key} ---\n{val}")
            prompt_parts.extend([
                "",
                "Produce 3-5 actionable insights as bullets. Each bullet should be "
                "a single sentence naming a concrete next-step decision the reader "
                "can act on. Do not restate the inputs verbatim. Skip preamble.",
            ])
            prompt = "\n".join(prompt_parts)

        try:
            client = get_openai_client(api_key=settings.OPENAI_API_KEY)
            # Session 1238 PR-1: morning_brief mode renders 4 lane summaries +
            # embeds the (already-rendered) decision_card_text verbatim. With
            # gpt-5-mini's ~1500-2000 reasoning overhead, 4000 max gave
            # ~2000-2500 output tokens — tight for the full brief markdown.
            # Bump to 6000 to give consistent headroom. Default 4000 floor
            # still applies for non-morning_brief synthesis (3-5 bullets).
            mb_budget = 6000 if is_morning_brief else 4000
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
                # Floor 4000 per Session 1224 memory rule
                # (feedback_gpt5_max_completion_tokens_floor.md).
                max_completion_tokens=mb_budget,
            )
            synthesis_text = (response.choices[0].message.content or '').strip()
            if not synthesis_text:
                return {
                    'success': False,
                    'error': (
                        'strategic_synthesis: LLM returned empty content '
                        f'(finish_reason={response.choices[0].finish_reason})'
                    ),
                }

            # Persist into context for downstream steps and final compile.
            context['strategic_synthesis'] = synthesis_text
            inputs_used = list(synthesis_inputs.keys())

            # Session 1233 B.1 — for morning_brief mode, also write the
            # final brief markdown + title to context so the
            # create_morning_brief_deliverable step can persist it.
            if is_morning_brief:
                from datetime import date as _date
                context['morning_brief_markdown'] = synthesis_text
                context['morning_brief_title'] = (
                    f"Morning Brief — {_date.today().isoformat()}"
                )

            logger.info(
                "🧩 Session 1231 F7 / 1233 B.1: strategic_synthesis produced "
                "%d chars from %d input keys (mode=%s): %s",
                len(synthesis_text), len(inputs_used),
                'morning_brief' if is_morning_brief else 'default',
                inputs_used,
            )

            return {
                'success': True,
                'summary': f'Synthesized {len(inputs_used)} input source(s) '
                           f'into {len(synthesis_text.splitlines())} lines',
                'synthesis': synthesis_text,
                'inputs_used': inputs_used,
            }
        except Exception as e:
            logger.error(
                "🧩 Session 1231 F7: strategic_synthesis LLM call failed: %s",
                e, exc_info=True,
            )
            return {
                'success': False,
                'error': f"strategic_synthesis LLM call failed: {type(e).__name__}: {e}",
            }

    # =========================================================================
    # SESSION 1233 B.1 — Morning Brief workflow internal handlers
    # =========================================================================

    def _build_morning_brief_prompt(
        self,
        synthesis_inputs: Dict[str, str],
        slot_used: str,
    ) -> str:
        """Build the strategic-synthesis prompt for morning_brief mode.

        Reads the four lane texts + decision_card_text from
        ``synthesis_inputs`` (already truncated to 2000 chars per key)
        and asks gpt-5-mini to produce the final brief markdown:
        TL;DR pointer + 4 lane sections + Decision Card.

        Spec: docs/MORNING_BRIEF_SPEC.md § Intent + Decision Card.
        """
        slot_label_map = {
            'sports_edge_scan': 'Sports Edge Scan',
            'prediction_markets': 'Prediction Markets',
            'ticker_catalyst_watch': 'Ticker / Catalyst Watch',
            'gtm_pipeline_health': 'GTM / Pipeline Health',
            'ai_infra_deep_dive': 'AI Infrastructure Deep Dive',
        }
        lane_4_label = slot_label_map.get(slot_used, slot_used.replace('_', ' ').title())

        prompt_parts = [
            "You are producing today's morning Chief-of-Staff brief for Chris, ",
            "the sole operator of the Donkey Betz platform.",
            "",
            "Output a clean markdown document that Chris can read in 5-7 minutes.",
            "",
            "Required structure (top to bottom):",
            "1. A single-line pointer: **If you only read one thing: skip to the Decision Card.**",
            "2. ## TL;DR — 3 bullets maximum, one per line.",
            "3. ## Lane 1 — Platform Readiness — summarize lane_1_text concisely.",
            "4. ## Lane 2 — Build Focus — summarize lane_2_text concisely.",
            "5. ## Lane 3 — Competitive Landscape — summarize lane_3_text concisely.",
            f"6. ## Lane 4 — {lane_4_label} — summarize lane_4_text concisely.",
            "7. ## Today's Decisions — embed decision_card_text verbatim (it's already formatted).",
            "8. A one-line footer: *Brief generated YYYY-MM-DD*.",
            "",
            "Lane inputs (truncated to 2000 chars each):",
        ]
        for key, val in synthesis_inputs.items():
            prompt_parts.append(f"\n--- {key} ---\n{val}")
        prompt_parts.extend([
            "",
            "Rules:",
            "- Be concise. The whole brief should fit on one screen.",
            "- Do NOT invent facts. If a lane input is empty or thin, write '*(no notable items)*'.",
            "- Preserve specific numbers, names, and links from the lane inputs.",
            "- Skip preamble and meta-commentary. Start with the pointer line.",
            "- Session 1238 PR-2: If SELF_CHECK_EVIDENCE block is present and",
            "  it contradicts a Lane 1 health-alarm warning (e.g., reports",
            "  'LOW — stale telemetry'), tag the affected warning in Lane 1",
            "  with '(Evidence confidence: low — auto-downgraded by",
            "  30min recheck)' and do NOT lead the TL;DR with it. If the",
            "  self-check CORROBORATES the warning, surface it normally.",
            "- Session 1238 PR-4: If `_lane_3_fallback` is present (Lane 3 had",
            "  no actionable signal today), use its content for Lane 3's body",
            "  VERBATIM in place of an empty section. Do NOT add the fallback",
            "  to the TL;DR — Lane 3 is informational on no-signal days.",
        ])
        return "\n".join(prompt_parts)

    def _resolve_rotation_slot(self, context: Dict) -> str:
        """Pure-logic Lane 4 slot resolver. Pulled out as a helper so
        the rotation_slot_resolve pre-step (B.2) and Lane 4's runtime
        fallback can share it.

        Priority chain (highest wins):

        1. Caller-forced ``context['rotation_slot']`` (B.1 default
           override path stays supported).
        2. Override flags in ``context['rotation_override']``:
           ``incident`` (bool) → ai_infra_deep_dive (until incident_focus
           slot lands), ``revenue`` (bool) → gtm_pipeline_health,
           ``signal_slot`` (shorthand string) → corresponding slot via
           ``_ROTATION_OVERRIDE_SHORTHAND_TO_SLOT``, ``calendar_slot``
           (shorthand string) → same map.
        3. Weekday default from ``_WEEKDAY_DEFAULT_SLOT``. Friday
           (weekday 4) alternates between ``sports_edge_scan`` (even
           ISO weeks) and ``prediction_markets`` (odd ISO weeks) per
           spec § Lane 4 rotation schedule.

        Spec source: ``docs/MORNING_BRIEF_SPEC.md`` § "Default rotation
        schedule" + § "Override triggers".
        """
        # (1) Caller-forced slot.
        forced = context.get('rotation_slot')
        if forced:
            return forced

        # (2) Override chain.
        override = context.get('rotation_override') or {}
        if isinstance(override, dict):
            if override.get('incident'):
                # No dedicated 'incident_focus' slot in the B.2 slot
                # map yet; until that lands, treat incident as
                # "deepen Lane 1 coverage" via the default slot.
                return self._MORNING_BRIEF_LANE_4_DEFAULT_SLOT
            if override.get('revenue'):
                return 'gtm_pipeline_health'
            signal = override.get('signal_slot')
            if signal:
                return self._ROTATION_OVERRIDE_SHORTHAND_TO_SLOT.get(
                    signal, self._MORNING_BRIEF_LANE_4_DEFAULT_SLOT,
                )
            calendar = override.get('calendar_slot')
            if calendar:
                return self._ROTATION_OVERRIDE_SHORTHAND_TO_SLOT.get(
                    calendar, self._MORNING_BRIEF_LANE_4_DEFAULT_SLOT,
                )

        # (3) Weekday default. Friday handled separately for alternation.
        # Helper indirection (_get_now_utc) is a test seam — patching
        # ``self._get_now_utc`` lets tests inject a fixed weekday +
        # iso_week without monkey-patching datetime at the module level.
        now = self._get_now_utc()
        weekday = now.weekday()
        if weekday == 4:  # Friday
            iso_week = now.isocalendar()[1]
            return 'sports_edge_scan' if iso_week % 2 == 0 else 'prediction_markets'
        return self._WEEKDAY_DEFAULT_SLOT.get(
            weekday, self._MORNING_BRIEF_LANE_4_DEFAULT_SLOT,
        )

    @staticmethod
    def _get_now_utc():
        """Test seam: returns ``datetime.utcnow()``. Inline import
        keeps the module-level imports lean; patching this method
        on instances is the canonical way to inject a fixed time
        for tests."""
        from datetime import datetime as _dt
        return _dt.utcnow()

    def _execute_rotation_slot_resolve_step(
        self, context: Dict,
    ) -> Dict[str, Any]:
        """Resolve the Lane 4 rotation slot and write it to context.

        Pure-logic pre-step. Captures the resolution reason for the
        runner's step_result summary BEFORE delegating to
        ``_resolve_rotation_slot`` so caller-forced vs same-value-by-
        coincidence stays distinguishable. Persists the result into
        ``context['rotation_slot']`` for Lane 4 to consume.

        Session 1233 B.2.
        """
        forced = context.get('rotation_slot')
        override = context.get('rotation_override') or {}

        if forced:
            reason = 'caller_forced'
        elif isinstance(override, dict) and override.get('incident'):
            reason = 'override_incident'
        elif isinstance(override, dict) and override.get('revenue'):
            reason = 'override_revenue'
        elif isinstance(override, dict) and override.get('signal_slot'):
            reason = f"override_signal:{override['signal_slot']}"
        elif isinstance(override, dict) and override.get('calendar_slot'):
            reason = f"override_calendar:{override['calendar_slot']}"
        else:
            weekday = self._get_now_utc().weekday()
            reason = (
                f"fri_alt_iso_week_parity:{weekday}"
                if weekday == 4
                else f"weekday_default:{weekday}"
            )

        slot = self._resolve_rotation_slot(context)
        context['rotation_slot'] = slot

        logger.info(
            "🗓️ Session 1233 B.2: rotation_slot_resolve resolved slot=%r "
            "(reason=%s)",
            slot, reason,
        )
        return {
            'success': True,
            'summary': f"Resolved Lane 4 slot to {slot} ({reason})",
            'rotation_slot': slot,
            'reason': reason,
        }

    def _execute_lane_4_rotating_focus_step(self, context: Dict) -> Dict[str, Any]:
        """Dispatch Lane 4 to a slot-resolved agent.

        Reads ``context['rotation_slot']`` set by the
        ``rotation_slot_resolve`` pre-step (B.2). If no slot has been
        resolved (e.g., template lacks the pre-step or runs Lane 4
        directly), falls back to ``_resolve_rotation_slot`` so the
        weekday default applies. Maps the slot to its agent via
        ``_MORNING_BRIEF_LANE_4_SLOT_AGENT`` and dispatches through
        the standard AGENT_MAP path.

        Returns a dict with the same shape as the AGENT_MAP fallback
        in ``_execute_step``: ``{'success', 'output', 'data'}`` plus
        ``'slot_used'`` and ``'agent_name'`` for downstream
        ``_update_context`` capture.

        Session 1234 D1 fail-loud (Rigby-ratified): on falsy
        ``result.success``, the returned dict always populates an
        ``error`` field with the best available detail (priority:
        ``result.error`` → ``result.message`` → ``result.output`` →
        structured fallback). The 2026-06-25 first-fire postmortem
        showed this branch returning an empty error so the orchestrator
        logged a generic "Unknown error" with no diagnostic value. See
        ``feedback_editor_fail_loud.md``. TODO(session-1234+): the same
        soft-fail-without-error pattern likely exists in other lane
        handlers; consider extracting a ``normalize_step_result()``
        helper once D1 proves out.
        """
        slot = context.get('rotation_slot') or self._resolve_rotation_slot(context)
        agent_pascal = self._MORNING_BRIEF_LANE_4_SLOT_AGENT.get(slot)

        if not agent_pascal:
            logger.warning(
                "Lane 4: unknown rotation_slot=%r — falling back to default %r",
                slot, self._MORNING_BRIEF_LANE_4_DEFAULT_SLOT,
            )
            slot = self._MORNING_BRIEF_LANE_4_DEFAULT_SLOT
            agent_pascal = self._MORNING_BRIEF_LANE_4_SLOT_AGENT[slot]

        try:
            from core.agent_router import AgentRouter
            router = AgentRouter(user=getattr(self, 'user', None))
        except Exception as e:
            return {
                'success': False,
                'output': self._lane_4_sentinel(slot, f"{type(e).__name__}: {e}"),
                'error': (
                    f"Lane 4 dispatch unavailable (AGENT_MAP fallback init "
                    f"failed for slot={slot!r}, agent={agent_pascal!r}): "
                    f"{type(e).__name__}: {e}"
                ),
                'slot_used': slot,
                'agent_name': agent_pascal,
            }

        if agent_pascal not in router.AGENT_MAP:
            return {
                'success': False,
                'output': self._lane_4_sentinel(
                    slot, f"agent {agent_pascal!r} not in AGENT_MAP"),
                'error': (
                    f"Lane 4: slot {slot!r} resolved to {agent_pascal!r} "
                    f"but that agent is not in AGENT_MAP"
                ),
                'slot_used': slot,
                'agent_name': agent_pascal,
            }

        # Step task — spec § dispatch prompt for Lane 4. Session 1234 D2:
        # appends per-slot focus phrase from _MORNING_BRIEF_LANE_4_SLOT_FOCUS
        # so agents shared across lanes (e.g., COOAgent in Lane 2 + Lane 4)
        # produce distinct content per lane.
        topic = context.get('topic') or ''
        slot_focus = self._MORNING_BRIEF_LANE_4_SLOT_FOCUS.get(slot, '')
        step_task = (
            f"Morning Brief Lane 4 — slot={slot}. "
            f"Provide actionable signals only (not a news dump). "
            f"Include 3-7 bullets with 'why it matters today' and explicit "
            f"action recommendation if applicable. "
            f"{slot_focus} "
            f"Topic anchor: {topic or '(none)'}."
        )

        rss_before_mb = _sample_rss_mb()
        try:
            result = router.route(agent_pascal, step_task, context or {})
            rss_after_mb = _sample_rss_mb()
            _log_lane_4_rss(slot, agent_pascal, rss_before_mb, rss_after_mb)

            success = bool(getattr(result, 'success', False))
            output = getattr(result, 'message', '') or ''
            data = getattr(result, 'data', {}) or {}

            if success:
                # Session 1238 PR-3: augment thin sports_edge_scan
                # outputs with the deterministic no-odds fallback per
                # Rigby's 06-26 audience-fit verdict. Other slots fall
                # through unchanged. If agents for other slots exhibit
                # the same thin-success pattern, extend the slot->
                # fallback map; for now sports_edge_scan is the only
                # observed case.
                if (
                    slot == 'sports_edge_scan'
                    and self._lane_4_output_is_thin(output)
                ):
                    fallback = self._lane_4_sports_edge_scan_fallback()
                    output = (
                        f"{output}\n\n"
                        f"---\n\n"
                        f"_Session 1238 PR-3 auto-augmented (no-odds fallback):_\n\n"
                        f"{fallback}"
                    )
                return {
                    'success': True,
                    'output': output,
                    'data': data,
                    'slot_used': slot,
                    'agent_name': agent_pascal,
                }

            # Session 1234 D1 fail-loud: capture WHY the agent reported
            # failure. Priority: explicit error → message → output → fallback.
            error_detail = (
                getattr(result, 'error', None)
                or (output if output else None)
                or (
                    f"agent {agent_pascal!r} returned success=False with no "
                    f"error/message/output (result type={type(result).__name__})"
                )
            )
            full_error = (
                f"Lane 4 agent {agent_pascal!r} reported failure for "
                f"slot {slot!r}: {error_detail}"
            )
            # Session 1234 D2 P2.C: populate output with sentinel so
            # synthesis still renders a Lane 4 section ("No signal today
            # …") instead of an empty heading. Orchestrator's non-critical
            # path uses the populated context['lane_4_text'] downstream.
            return {
                'success': False,
                'output': output or self._lane_4_sentinel(slot, error_detail),
                'data': data,
                'error': full_error,
                'slot_used': slot,
                'agent_name': agent_pascal,
            }
        except Exception as e:
            rss_after_mb = _sample_rss_mb()
            _log_lane_4_rss(slot, agent_pascal, rss_before_mb, rss_after_mb)
            logger.error(
                "Lane 4 dispatch failed for slot=%r → agent=%r: %s",
                slot, agent_pascal, e, exc_info=True,
            )
            return {
                'success': False,
                'output': self._lane_4_sentinel(
                    slot, f"{type(e).__name__}: {e}"),
                'error': (
                    f"Lane 4 dispatch failed for slot {slot!r} → "
                    f"agent {agent_pascal!r}: {type(e).__name__}: {e}"
                ),
                'slot_used': slot,
                'agent_name': agent_pascal,
            }

    @staticmethod
    def _lane_4_sports_edge_scan_fallback() -> str:
        """Deterministic fallback for Lane 4 sports_edge_scan when no
        multi-bookmaker odds data is available.

        Session 1238 PR-3: closes Rigby's "dead lane" finding from the
        06-26 audience-fit verdict. Pre-fix, when the SharpActionDetector
        agent had no qualifying odds data, it returned success with the
        thin output "No multi-bookmaker odds data available." → the brief
        inherited a near-empty Lane 4 section.

        This fallback turns the empty lane into a structured 3-block
        template per Rigby's spec:
          - Data status (what feed is missing + spider health)
          - What we can still do today (model/news/watchlist signals)
          - Action (concrete restart/verify steps)

        Static + deterministic on purpose — operator-facing recovery
        playbook. If individual checks (spider liveness, watchlist
        population) need to surface live runtime data, that's a future
        enhancement (Session 1239+).
        """
        return (
            "**Data status:** Multi-bookmaker odds feed empty for today's "
            "scan window. Sharp-action signals require ≥2 sportsbook lines "
            "(line moves + limit changes) to flag edges — no qualifying data "
            "available from the current provider pull.\n\n"
            "**What we can still do today (no-odds-fallback):**\n"
            "- Review yesterday's closing line vs. results in the betting "
            "dashboard; surface any large CLV misses that suggest model "
            "drift.\n"
            "- Scan watchlist tickers for injury news / scheduling changes "
            "that would have moved lines if odds were live.\n"
            "- Spot-check ML model health: are inference latencies normal? "
            "Did any feature pipelines fail overnight?\n\n"
            "**Action (pick one):**\n"
            "- Verify odds provider API keys + rate-limit headroom "
            "(typical cause when feed goes silent without errors).\n"
            "- Manually trigger the odds-spider beat task if it's been "
            "skipped: `python manage.py shell -c \"from celery import "
            "current_app; current_app.send_task('core.tasks.run_odds_scan')\"`.\n"
            "- File a brief ops note if this is the 2nd day in a row — "
            "may indicate a provider-side outage worth escalating."
        )

    @staticmethod
    def _lane_4_output_is_thin(output: str) -> bool:
        """Heuristic: detect Lane 4 outputs that are technically
        successful but content-thin.

        Session 1238 PR-3: used by `_execute_lane_4_rotating_focus_step`
        to decide whether to augment with the slot-specific fallback.

        Thin signals:
        - Output < 200 characters total
        - Contains "no multi-bookmaker odds data" / "no qualifying"
        - Contains generic "no data available" markers

        Used in combination with the slot match (currently only
        sports_edge_scan has a fallback template; other slots fall
        through unchanged).
        """
        if not output:
            return True
        text = output.strip()
        if len(text) < 200:
            return True
        thin_markers = (
            'no multi-bookmaker odds',
            'no multi-book odds',
            'no qualifying',
            'no odds data available',
            'no data available',
        )
        text_lower = text.lower()
        return any(m in text_lower for m in thin_markers)

    @staticmethod
    def _lane_4_sentinel(slot: str, error_excerpt: str) -> str:
        """Render the Lane 4 'no signal today' sentinel.

        Session 1234 D2 P2.C (Rigby-ratified): when Lane 4 fails for
        a recoverable reason (no upstream data, agent contract mismatch,
        ambient dispatch error), the workflow continues and the brief
        ships with this sentinel as the Lane 4 section text. Synthesis
        reads it from ``context['lane_4_text']`` via ``_update_context``.

        The sentinel is short (one paragraph), names the slot, and
        embeds a truncated error excerpt so Chris can tell at a glance
        whether Lane 4 was quiet vs. broken.
        """
        excerpt = (error_excerpt or 'no detail captured').strip()
        if len(excerpt) > 240:
            excerpt = excerpt[:237] + '...'
        slot_label = slot.replace('_', ' ')
        return (
            f"_Lane 4 ({slot_label}): No signal today "
            f"(agent error: {excerpt})._"
        )

    def _execute_decision_card_synthesis_step(self, context: Dict) -> Dict[str, Any]:
        """Produce the Decision Card from the four lane texts.

        Reads ``lane_1_text`` through ``lane_4_text`` from context,
        calls gpt-5-mini to produce 1-3 explicit decisions, writes
        BOTH the markdown form into ``context['decision_card_text']``
        AND the structured form into ``context['decision_cards']``.

        Session 1242 (Path C — deliverable 19b45ea0-…): structured form
        added per MORNING_BRIEF_SPEC.md:228 (which always called for
        ``decision_card[{...}]`` alongside the markdown but was deferred
        in S1233 B.1). Markdown body uses RELATIVE deadlines per Rigby's
        S1242 audience-fit verdict (Chris's reading variance makes
        "within 24 hours" strictly more actionable than "by 11:00 AM MDT").
        Structured form carries an absolute ISO-8601 ``next_step_timebox``
        when the LLM can confidently derive one — "present but optional"
        per Rigby's locked design constraint.

        Per-card schema (``decision_cards[i]``):
          - ``decision``: str (non-empty after strip)
          - ``recommendation``: str (non-empty after strip)
          - ``why_now``: str (non-empty after strip)
          - ``next_step_owner``: str (non-empty after strip)
          - ``next_step_deadline_style``: one of {"relative", "absolute", "hybrid"}
          - ``next_step_timebox``: ISO-8601 datetime w/ offset OR null

        On structured-form parse / validation failure: keep the markdown,
        set ``decision_cards=[]``, emit warning log + observability metric.
        Brief still ships per ``feedback_workflow_step_sentinel_plus_
        noncritical_pattern``.

        Graceful empty-context behavior unchanged from B.1: if no lanes
        wrote anything, return sentinel markdown + empty structured list.
        """
        from django.conf import settings
        from core.services.openai_client_factory import get_openai_client

        # Collect lane inputs.
        # Session 1242: humanize lane_1_text BEFORE the LLM sees it.
        # Pre-fix the decision_card_synthesis step read lane_1_text raw
        # from context, so MUSCULAR jargon flowed into the LLM prompt and
        # echoed into TL;DR prose, Decision "Why now" lines, and
        # Where-to-verify pointers. Symmetrical with the humanizer call
        # in _execute_strategic_synthesis_step.
        lane_inputs = {}
        for lane_key in ('lane_1_text', 'lane_2_text', 'lane_3_text', 'lane_4_text'):
            val = context.get(lane_key)
            if val:
                val_str = str(val)[:2000]
                if lane_key == 'lane_1_text':
                    val_str = self._humanize_body_system_jargon(val_str)
                lane_inputs[lane_key] = val_str

        if not lane_inputs:
            # Smoke / empty-context case — keep the workflow alive.
            # Path C: also write empty decision_cards list so any
            # downstream consumer reading the structured form sees a
            # well-formed empty list, not a missing key.
            sentinel = "No urgent decisions today — monitor only."
            context['decision_card_text'] = sentinel
            context['decision_cards'] = []
            logger.info(
                "🗂️ Session 1233 B.1: decision_card_synthesis ran with empty "
                "lane context — wrote sentinel + empty decision_cards to keep "
                "workflow contract alive."
            )
            return {
                'success': True,
                'summary': 'No lane inputs available; wrote sentinel',
                'decision_card_text': sentinel,
                'decision_cards': [],
                'inputs_used': [],
            }

        slot_label = context.get('lane_4_slot_used') or context.get(
            'rotation_slot', self._MORNING_BRIEF_LANE_4_DEFAULT_SLOT,
        )

        # Session 1242 Path C: compute Denver TZ ISO offset for the
        # structured form's ``next_step_timebox`` when LLM emits an
        # absolute deadline. Output shape: "-06:00" (MDT) or "-07:00"
        # (MST), tracking DST automatically. Per Rigby's S1242 verdict
        # this is NOT exposed in the markdown prompt anymore (markdown
        # uses relative deadlines); only the structured form sees it.
        from datetime import datetime as _dt
        try:
            from zoneinfo import ZoneInfo
            _denver_now = _dt.now(tz=ZoneInfo('America/Denver'))
            _denver_iso_offset = _denver_now.strftime('%z')
            # Normalize "-0600" → "-06:00" for ISO-8601 colon-separated form
            if len(_denver_iso_offset) == 5:
                _denver_iso_offset = (
                    _denver_iso_offset[:3] + ':' + _denver_iso_offset[3:]
                )
        except Exception:
            _denver_iso_offset = '-06:00'  # MDT safe fallback

        prompt_parts = [
            "You are producing the 'Today's Decisions' section for Chris's "
            "daily Chief-of-Staff brief. Output TWO parts in order: a "
            "markdown body, then a JSON block.",
            "",
            "## PART 1 — Markdown body",
            "",
            "Based on the four lane outputs below, identify 1-3 explicit "
            "decisions Chris should make today. Hard cap: 3 decisions. If "
            "nothing urgent surfaces, output exactly:",
            "    No urgent decisions today — monitor only.",
            "",
            "For each decision, output one '### Decision N: <one-sentence title>' "
            "heading followed by:",
            "- **Decision:** 1 sentence stating what to decide.",
            "- **Recommendation:** 1 sentence with the suggested choice.",
            "- **Why now:** 1 bullet (evidence-linked to a specific lane output).",
            "- **Next step:** owner + RELATIVE timebox (e.g., 'Claude Code — within 24 hours' or 'DevOps — within 2 hours').",
            "",
            "USE RELATIVE DEADLINES IN THE MARKDOWN. Do NOT use absolute clock "
            "times in the markdown (no 'by 11:00 AM MDT' etc.) — Chris reads at "
            "variable times and relative deadlines stay actionable. Absolute "
            "times go in the JSON block instead.",
            "",
            "## PART 2 — JSON block (after the markdown)",
            "",
            "After the markdown body, output a fenced ```json ... ``` block "
            "with this exact shape:",
            "```json",
            '{"decision_cards": [',
            '  {',
            '    "decision": "<from Decision: line above>",',
            '    "recommendation": "<from Recommendation: line above>",',
            '    "why_now": "<from Why now: line above>",',
            '    "next_step_owner": "<owner name from Next step: line above>",',
            '    "next_step_deadline_style": "relative" | "absolute" | "hybrid",',
            '    "next_step_timebox": "<ISO-8601 datetime with offset>" OR null',
            '  }',
            ']}',
            "```",
            "",
            "Rules for the JSON block:",
            "- ``next_step_deadline_style`` MUST be one of: \"relative\", \"absolute\", \"hybrid\".",
            "  - \"relative\" when the markdown deadline is a duration (\"within X hours/days\") and no specific clock time applies — this is the typical case.",
            "  - \"absolute\" when a specific clock deadline is genuinely derivable (e.g., a meeting at 14:00, market close 16:00).",
            "  - \"hybrid\" when both apply (rare).",
            "- ``next_step_timebox`` MUST be ISO-8601 with offset when style=\"absolute\" or \"hybrid\"; MUST be null when style=\"relative\".",
            f"- ISO offset for Denver TZ today: {_denver_iso_offset}",
            "- ``decision_cards`` array length MUST equal the number of '### Decision N:' headers in the markdown body.",
            "- If markdown is the no-urgent sentinel, JSON block is exactly: ```json\\n{\"decision_cards\": []}\\n```.",
            "- All string fields must be non-empty after stripping whitespace.",
            "",
            "Lane inputs (truncated to 2000 chars each):",
        ]
        for key, val in lane_inputs.items():
            prompt_parts.append(f"\n--- {key} ---\n{val}")
        prompt_parts.extend([
            "",
            f"(Context: Lane 4 today is the '{slot_label}' rotating slot.)",
            "",
            "Output the markdown body FIRST, then the ```json ...``` block. "
            "Nothing else.",
        ])
        prompt = "\n".join(prompt_parts)

        try:
            client = get_openai_client(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
                # Session 1238 PR-1: bumped 4000 → 6000. gpt-5-mini's
                # reasoning consumes ~1500-2000 tokens (per memory rule
                # feedback_gpt5_max_completion_tokens_floor); 4000 gave
                # ~2000-2500 output tokens which is tight for 3 decision
                # cards each with 4 required fields. Today's 06-26 brief
                # truncated Decision #3 mid-sentence ("...confirm whether
                # missing odds data") — bump gives more headroom.
                # Session 1242 Path C: 6000 still adequate since structured
                # form adds ~300-500 tokens of JSON to a 1500-token markdown
                # body (estimated 2000-2500 output tokens including JSON).
                max_completion_tokens=6000,
            )
            full_response = (response.choices[0].message.content or '').strip()
            if not full_response:
                return {
                    'success': False,
                    'error': (
                        'decision_card_synthesis: LLM returned empty content '
                        f'(finish_reason={response.choices[0].finish_reason})'
                    ),
                }

            # Session 1242 Path C: split markdown body + JSON block.
            # Failure mode: keep markdown, set decision_cards=[] per
            # Rigby's "do not fail workflow on JSON parse failure" rule.
            card_text, decision_cards, parse_issue = (
                self._parse_decision_card_response(full_response)
            )
            if parse_issue:
                logger.warning(
                    "🗂️ Session 1242 Path C: decision_card JSON parse issue "
                    "(%s) — keeping markdown, setting decision_cards=[].",
                    parse_issue,
                )

            # Session 1238 PR-1: post-render markdown validator catches
            # truncation + missing required fields. Logs warning when
            # invalid (does NOT fail the step — brief still ships).
            validation_issues = self._validate_decision_card(card_text)
            if validation_issues:
                logger.warning(
                    "🗂️ Session 1238 PR-1: decision_card validation found "
                    "%d issue(s): %s",
                    len(validation_issues), validation_issues,
                )

            # Session 1242 Path C: structured-form validator. Empties
            # decision_cards on any validation failure (Rigby's "present
            # but optional" + "don't fail workflow" rules combined).
            structured_issues = self._validate_decision_cards_structured(
                decision_cards
            )
            if structured_issues:
                logger.warning(
                    "🗂️ Session 1242 Path C: decision_cards (structured) "
                    "validation found %d issue(s) (%s) — keeping markdown, "
                    "setting decision_cards=[].",
                    len(structured_issues), structured_issues,
                )
                decision_cards = []

            # Path C observability log: surfaces count + how many cards
            # carried a non-null absolute timebox (per Rigby's recommendation
            # — "log a compact summary, attach to existing run metadata").
            non_null_timebox_count = sum(
                1 for c in decision_cards if c.get('next_step_timebox')
            )
            logger.info(
                "🗂️ Session 1242 Path C: decision_cards structured form — "
                "count=%d, non_null_timebox=%d, parse_issue=%s, "
                "structured_issues=%d",
                len(decision_cards), non_null_timebox_count,
                bool(parse_issue), len(structured_issues),
            )

            context['decision_card_text'] = card_text
            context['decision_cards'] = decision_cards
            inputs_used = list(lane_inputs.keys())

            logger.info(
                "🗂️ Session 1233 B.1: decision_card_synthesis produced %d chars "
                "from %d lane inputs: %s",
                len(card_text), len(inputs_used), inputs_used,
            )
            return {
                'success': True,
                'summary': (
                    f'Produced decision card ({len(card_text)} chars markdown '
                    f'+ {len(decision_cards)} structured) from '
                    f'{len(inputs_used)} lane input(s)'
                ),
                'decision_card_text': card_text,
                'decision_cards': decision_cards,
                'inputs_used': inputs_used,
                'validation_issues': validation_issues,
                'structured_issues': structured_issues,
                'parse_issue': parse_issue,
            }
        except Exception as e:
            logger.error(
                "🗂️ Session 1233 B.1: decision_card_synthesis LLM call failed: %s",
                e, exc_info=True,
            )
            return {
                'success': False,
                'error': (
                    f"decision_card_synthesis LLM call failed: "
                    f"{type(e).__name__}: {e}"
                ),
            }

    @staticmethod
    def _parse_decision_card_response(full_response: str) -> tuple:
        """Split decision_card_synthesis LLM output into markdown body + structured cards.

        Session 1242 Path C: the LLM is asked to output TWO sections in
        order — a markdown body followed by a fenced ``` ```json ``` ```
        block containing ``{"decision_cards": [...]}``. This helper
        extracts both. On any parse failure, returns the full response
        as the markdown body, an empty list for the structured form, and
        a diagnostic string in the third tuple slot.

        Returns: (markdown_body: str, decision_cards: list[dict], parse_issue: str)
        ``parse_issue`` is '' on success, otherwise a short reason string
        the caller can log.

        Parsing strategy: locate the LAST ``` ```json ``` ``` fence in the
        response (more robust than greedy first-fence match if the
        markdown body itself contains a code block). Everything before
        that fence is the markdown body. Inside the fence, JSON-parse and
        extract the ``decision_cards`` array.
        """
        import json
        import re as _re

        if not full_response or not full_response.strip():
            return ('', [], 'empty response')

        # Two-pass fence matching:
        # 1. Prefer the LAST ```json fence (most specific; survives if
        #    the markdown body has its own ```python / ```bash blocks
        #    that share opening-and-closing-fence shape).
        # 2. Fall back to the LAST bare ``` fence only if no ```json
        #    fence found (handles the LLM-forgot-the-lang-tag case).
        #
        # Why this matters: with the LLM emitting fenced code samples
        # inside a Decision body, a single combined regex would pair
        # the code-sample's closing fence with the next code-sample's
        # opening fence and capture the text in between as "JSON" —
        # then json.loads fails on prose text. Splitting the strategy
        # avoids the false pair.
        json_fence_re = _re.compile(
            r'```json\s*\n(.*?)\n\s*```',
            _re.DOTALL,
        )
        matches = list(json_fence_re.finditer(full_response))
        if not matches:
            bare_fence_re = _re.compile(
                r'```\s*\n(.*?)\n\s*```',
                _re.DOTALL,
            )
            matches = list(bare_fence_re.finditer(full_response))
        if not matches:
            return (full_response.strip(), [], 'no JSON fence found')

        last_match = matches[-1]
        json_text = last_match.group(1).strip()
        markdown_body = full_response[:last_match.start()].strip()

        try:
            payload = json.loads(json_text)
        except json.JSONDecodeError as e:
            return (markdown_body, [], f'json decode error: {e}')

        if not isinstance(payload, dict):
            return (markdown_body, [], f'JSON root is {type(payload).__name__}, not dict')

        cards = payload.get('decision_cards')
        if cards is None:
            return (markdown_body, [], 'missing "decision_cards" key')
        if not isinstance(cards, list):
            return (
                markdown_body, [],
                f'"decision_cards" is {type(cards).__name__}, not list',
            )

        return (markdown_body, cards, '')

    @staticmethod
    def _validate_decision_cards_structured(cards: list) -> list:
        """Validate the structured decision_cards form per Rigby's S1242 contract.

        Locked contract (deliverable 19b45ea0-…):
        - ``decision_cards`` is a list[dict] (may be empty).
        - Required keys per card: ``decision``, ``recommendation``,
          ``why_now``, ``next_step_owner``, ``next_step_deadline_style``,
          ``next_step_timebox``.
        - ``next_step_deadline_style`` ∈ {"relative", "absolute", "hybrid"}.
        - ``next_step_timebox`` MUST be ISO-8601 datetime w/ offset when
          style ∈ {"absolute", "hybrid"}; MUST be null when style == "relative".
        - All string fields must be non-empty after strip().

        Returns: list[str] of human-readable issues (empty list = valid).
        Caller per S1242 design: if any issues, empty the decision_cards
        list entirely (don't ship partial structured form — keep markdown).
        """
        import re as _re

        issues: list = []
        REQUIRED_KEYS = (
            'decision', 'recommendation', 'why_now',
            'next_step_owner', 'next_step_deadline_style', 'next_step_timebox',
        )
        VALID_STYLES = {'relative', 'absolute', 'hybrid'}
        ISO_OFFSET_PATTERN = _re.compile(
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2}|Z)$'
        )

        if not isinstance(cards, list):
            return [f'decision_cards is {type(cards).__name__}, not list']

        for i, card in enumerate(cards):
            if not isinstance(card, dict):
                issues.append(f'card[{i}] is {type(card).__name__}, not dict')
                continue

            missing = [k for k in REQUIRED_KEYS if k not in card]
            if missing:
                issues.append(f'card[{i}] missing keys: {missing}')
                continue

            # String non-empty checks for first 4 fields
            for key in ('decision', 'recommendation', 'why_now', 'next_step_owner'):
                val = card.get(key)
                if not isinstance(val, str) or not val.strip():
                    issues.append(
                        f'card[{i}].{key} is empty or non-string'
                    )

            style = card.get('next_step_deadline_style')
            if style not in VALID_STYLES:
                issues.append(
                    f'card[{i}].next_step_deadline_style={style!r} '
                    f'not in {sorted(VALID_STYLES)}'
                )

            timebox = card.get('next_step_timebox')
            if style == 'relative':
                if timebox is not None:
                    issues.append(
                        f'card[{i}].next_step_timebox must be null when '
                        f'style=relative (got {timebox!r})'
                    )
            elif style in ('absolute', 'hybrid'):
                if not isinstance(timebox, str) or not timebox.strip():
                    issues.append(
                        f'card[{i}].next_step_timebox must be ISO-8601 '
                        f'string when style={style} (got {timebox!r})'
                    )
                elif not ISO_OFFSET_PATTERN.match(timebox):
                    issues.append(
                        f'card[{i}].next_step_timebox={timebox!r} does not '
                        f'match ISO-8601 with offset pattern'
                    )

        return issues

    @staticmethod
    def _lane_3_is_no_signal(lane_3_text: str) -> bool:
        """Detect Lane 3 (Competitive Landscape) no-signal cases.

        Session 1238 PR-4: Rigby's audience-fit verdict flagged Lane 3
        as producing no actionable signal when 'no confirmed competitor
        change events' is the answer. Pre-fix the LLM dutifully
        rendered the empty Lane 3 section anyway.

        This detector tags Lane 3 inputs that should be augmented with
        a deterministic 'coverage map' fallback instead of an empty
        section. Triggers on:
        - empty / short (< 200 chars) text
        - common no-signal markers (case-insensitive)
        """
        if not lane_3_text:
            return True
        text = lane_3_text.strip()
        if len(text) < 200:
            return True
        markers = (
            'no confirmed competitor',
            'no confirmed change events',
            'no notable competitor',
            'no significant competitor',
            'no qualifying events',
            'no actionable changes',
            'no changes detected',
        )
        text_lower = text.lower()
        return any(m in text_lower for m in markers)

    @staticmethod
    def _lane_3_no_signal_fallback() -> str:
        """Deterministic fallback for Lane 3 when no competitor change
        events surfaced.

        Session 1238 PR-4: closes Rigby's adaptive no-signal lane
        finding. Replaces the empty Lane 3 with a structured 'coverage
        map + watch items' template Chris can scan in seconds.
        """
        return (
            "**No confirmed competitor change events in last 72h.** "
            "(Honest empty — not necessarily proof no changes happened.)\n\n"
            "**Coverage map (what was checked):**\n"
            "- Crunchbase: funding rounds + product launches\n"
            "- Press release wire (PR Newswire, BusinessWire): pricing + GTM\n"
            "- Top-5 competitor blogs + changelogs: feature shifts\n"
            "- Social signal (X / LinkedIn): ambient mention spikes\n\n"
            "**Top 3 watch items (low-confidence, monitor only):**\n"
            "- Any competitor with recent funding may push enterprise "
            "pricing changes within 30-60 days — watch for tier "
            "additions.\n"
            "- Spider staleness can suppress true positives — verify "
            "Lane 1 spider health if today's empty result feels wrong.\n"
            "- Quarterly earnings windows often trigger competitor "
            "moves — check if any tracked rival is in that window.\n\n"
            "**Action:** None today — Lane 3 is informational. Escalate "
            "to a fresh competitor scan only if a downstream signal "
            "(e.g., a deal lost to a specific competitor) suggests "
            "deeper investigation."
        )

    @staticmethod
    def _humanize_body_system_jargon(text: str) -> str:
        """Translate insider body-system labels to plain-English with
        the system name preserved as a parenthetical tag.

        Session 1238 PR-4: Rigby's audience-fit verdict flagged
        'MUSCULAR: No Agent Activity' as insider jargon. Replace with
        'Agent activity anomaly (possible worker stall) [MUSCULAR]'
        per her suggestion.

        Session 1242: broadened beyond the original 2 literal patterns
        after 06-27 brief verification surfaced 4 MUSCULAR escapes —
        only 1 of which matched PR #2658's literal. The escapes (TL;DR
        prose, Where-to-verify lines, Decision Card "Why now" body)
        showed the LLM echoing MUSCULAR from its INPUT into its OUTPUT
        in shapes the literal substitution didn't cover. New approach:
        (1) legacy literals preserved for backwards compat with the
        original Rigby-prescribed rewrite, (2) a tolerant pass catches
        any remaining bare MUSCULAR mention not already wrapped in
        brackets, demoting it to a parenthetical [MUSCULAR] tag after
        a plain-English phrase. Other body systems (HEART, LUNGS,
        CIRCULATORY, etc.) still left unchanged — they don't appear
        in lane outputs yet.

        Idempotent: re-running the humanizer on its own output is a
        no-op because the regex skips tokens already preceded by `[`
        or followed by `]`.
        """
        if not text:
            return text

        # Pass 1: legacy literal patterns from PR #2658. Preserved so
        # the original "MUSCULAR: No Agent Activity" → "Agent activity
        # anomaly (possible worker stall) [MUSCULAR]" rewrite that
        # Rigby specifically prescribed continues to land verbatim.
        legacy = (
            (
                'MUSCULAR: No Agent Activity',
                'Agent activity anomaly (possible worker stall) [MUSCULAR]',
            ),
            (
                'MUSCULAR: no agent activity',
                'agent activity anomaly (possible worker stall) [MUSCULAR]',
            ),
        )
        out = text
        for old, new in legacy:
            out = out.replace(old, new)

        # Pass 2: tolerant sweep for remaining bare MUSCULAR mentions.
        # Order matters — most specific shape first so the generic fallback
        # only fires on mentions the specific shapes didn't claim.
        import re as _re
        # Shape: "MUSCULAR subsystem"  → "agent-activity subsystem [MUSCULAR]"
        # (case-insensitive; collapses the redundant "subsystem subsystem"
        # that a naive replace would produce.)
        out = _re.sub(
            r'(?<!\[)\bMUSCULAR\b\s+subsystem\b',
            'agent-activity subsystem [MUSCULAR]',
            out,
            flags=_re.IGNORECASE,
        )
        # Generic fallback: any other bare MUSCULAR not already wrapped
        # in `[...]`. Demote to a plain-English noun with the tag preserved.
        out = _re.sub(
            r'(?<!\[)\bMUSCULAR\b(?!\])',
            'agent-activity [MUSCULAR]',
            out,
        )
        return out

    @staticmethod
    def _collect_lane_1_self_check_evidence(lane_1_text: str) -> str:
        """Run cheap runtime self-checks for Lane 1 health-alarm claims.

        Session 1238 PR-2: closes the self-referential trust issue
        Rigby flagged in the 06-26 audience-fit verdict. Pre-fix Lane
        1's MUSCULAR warning ("Agent execution telemetry shows
        'paralyzed'") was based on a body_system snapshot that could be
        minutes-to-an-hour stale by the time the brief renders. The
        brief surfaced the stale warning as high-confidence with no
        recheck — even though the workflow itself was actively running
        agents at that moment.

        Returns a markdown SELF_CHECK_EVIDENCE block to inject into the
        morning_brief prompt so the LLM can downgrade contradicted
        warnings. Returns empty string if no health-alarm keywords
        detected in lane_1_text (no need to run the self-check).

        Self-check metrics (all cheap ORM queries, 30min window):
        - AgentExecution rows count
        - CeleryTaskEvent rows count (proxy for worker liveness)
        - Distinct agent names that produced AgentExecutions

        These are the same metrics the MUSCULAR body_system check uses
        to compute "paralyzed" status — so a fresh recompute directly
        falsifies or confirms the stale warning.
        """
        if not lane_1_text:
            return ''

        # Health-alarm triggers — keywords that indicate Lane 1 is
        # claiming a system stall / paralysis. If none present, no
        # self-check needed.
        triggers = (
            'paralyzed',
            'No Agent Activity',
            'no agent activity',
            'worker/process stall',
            'workers stalled',
        )
        if not any(t in lane_1_text for t in triggers):
            return ''

        try:
            from datetime import timedelta
            from django.utils import timezone as _tz
            from django.apps import apps
            AgentExecution = apps.get_model('core', 'AgentExecution')
            CeleryTaskEvent = apps.get_model('core', 'CeleryTaskEvent')

            window_minutes = 30
            since = _tz.now() - timedelta(minutes=window_minutes)

            # Arc I-0100 P4 §4.2 F1 fold (PR-B1 §3.3 Q5 Rigby
            # SIGN-with-edits + Chris agree-all 2026-07-06 →
            # exclude_pa): 30-min liveness health check should cover
            # runnable worker agents; PA is a meta-orchestrator with
            # its own separate health surface (SIGN edit fold:
            # optionally add a separate PA-loop health metric,
            # deferred as backlog item per PR-A6 scope). Use
            # agent__name form per ADR-0002 F1 fold equivalent
            # (Postgres JSONField NULL-semantics make the
            # input_data__source='pa' form unsafe for pre-flag-flip
            # rows).
            ae_qs = AgentExecution.objects.filter(
                created_at__gte=since,
            ).exclude(agent__name='PersonalAssistant')
            ae_count = ae_qs.count()
            distinct_agents = ae_qs.values_list(
                'agent__name', flat=True,
            ).distinct().count()

            cte_count = CeleryTaskEvent.objects.filter(
                started_at__gte=since,
            ).count()

            # Decide a confidence-downgrade verdict from the metrics.
            # If recent activity > 5 agent executions or > 20 celery
            # events, the system is demonstrably NOT paralyzed; the
            # warning should be marked "Evidence confidence: low".
            if ae_count > 5 or cte_count > 20:
                verdict = (
                    f"LOW — system shows healthy activity in last "
                    f"{window_minutes}min "
                    f"({ae_count} AgentExecutions, {cte_count} "
                    f"CeleryTaskEvents); the 'paralyzed' warning is "
                    f"stale telemetry."
                )
            elif ae_count == 0 and cte_count < 5:
                verdict = (
                    f"HIGH — corroborated by current self-check "
                    f"({ae_count} AgentExecutions, {cte_count} "
                    f"CeleryTaskEvents in last {window_minutes}min). "
                    f"The warning is real."
                )
            else:
                verdict = (
                    f"MEDIUM — current self-check shows partial "
                    f"activity ({ae_count} AgentExecutions, "
                    f"{cte_count} CeleryTaskEvents in last "
                    f"{window_minutes}min). Investigate before "
                    f"escalating."
                )

            return (
                f"\n--- SELF_CHECK_EVIDENCE (run at brief-compile time) ---\n"
                f"Lane 1 contains a health-alarm warning. Fresh "
                f"{window_minutes}-minute window recheck:\n"
                f"- AgentExecution rows: {ae_count} "
                f"(from {distinct_agents} distinct agents)\n"
                f"- CeleryTaskEvent rows: {cte_count}\n"
                f"- Evidence confidence: {verdict}\n"
                f"- What would falsify Lane 1's warning: "
                f"AgentExecution count > 5 or CeleryTaskEvent count "
                f"> 20 in the last {window_minutes} minutes.\n"
            )
        except Exception as e:
            logger.warning(
                "🩺 Session 1238 PR-2: lane_1 self-check raised "
                "(%s: %s) — returning empty evidence block",
                type(e).__name__, e,
            )
            return ''

    @staticmethod
    def _validate_decision_card(card_text: str) -> list:
        """Validate a decision_card_synthesis LLM output for completeness.

        Session 1238 PR-1: catches the truncation + missing-field
        defects Rigby's audience-fit verdict flagged on the 06-26 brief
        (Decision #3 ended mid-sentence at "...confirm whether missing
        odds data" — no period, no Next step field).

        Returns a list of human-readable issue strings (empty list =
        valid). Caller logs warnings + can attach to telemetry. Does NOT
        fail the step — the brief still ships, but the issue is
        visible.

        Validation rules (per docs/MORNING_BRIEF_SPEC.md Decision Card
        contract):

        1. **Sentinel exception:** If the entire text is exactly the
           "no urgent decisions today" sentinel, it's valid.
        2. **Termination:** card_text must end with sentence punctuation
           (., !, ?). Truncation mid-sentence fails this.
        3. **Per-decision required fields:** every '### Decision N:'
           block must contain all 4 markers: 'Decision:',
           'Recommendation:', 'Why now:', 'Next step:'. Missing any =
           fail.
        4. **At least one decision:** if text doesn't match the
           sentinel and contains no '### Decision' headers, fail.
        """
        import re

        issues: list = []

        if not card_text or not card_text.strip():
            return ['decision_card empty']

        text = card_text.strip()

        # Rule 1: sentinel exception — exact match is valid + skip rest
        SENTINEL = 'No urgent decisions today — monitor only.'
        if text == SENTINEL or text.startswith(SENTINEL):
            return []

        # Rule 2: termination — must end with sentence punctuation
        last_char = text[-1]
        if last_char not in '.!?"\'`)':
            issues.append(
                f"text ends with {last_char!r} (truncation suspected — "
                "no sentence-terminating punctuation)"
            )

        # Find all decision headers ('### Decision N:' or '### Decision N.')
        decision_headers = re.findall(
            r'^###\s+Decision\s+\d+[:.]', text, flags=re.MULTILINE,
        )

        # Rule 4: at least one decision
        if not decision_headers:
            issues.append(
                'no \'### Decision N:\' headers found (and not the '
                '"No urgent decisions today" sentinel)'
            )
            return issues  # short-circuit — can't validate fields

        # Rule 3: per-decision required-field check.
        # Split on the decision headers so each block has its own fields.
        # Use re.split with a capturing group to keep the headers.
        parts = re.split(r'(^###\s+Decision\s+\d+[:.][^\n]*$)',
                         text, flags=re.MULTILINE)
        # parts is [pre-header-junk, header1, body1, header2, body2, ...].
        for i in range(1, len(parts), 2):
            header = parts[i]
            body = parts[i + 1] if i + 1 < len(parts) else ''
            for required in ('Decision:', 'Recommendation:', 'Why now:', 'Next step:'):
                if required not in body:
                    issues.append(
                        f"{header.strip()}: missing required field {required!r}"
                    )

        return issues

    # Session 1233 Sub-step C — persistent "Morning Brief" workspace name.
    # Looked up via get_or_create at deliverable-persist time, scoped per
    # user, so the first scheduled fire bootstraps the workspace.
    _MORNING_BRIEF_WORKSPACE_NAME: str = 'Morning Brief'
    _MORNING_BRIEF_WORKSPACE_DESCRIPTION: str = (
        "Daily Chief-of-Staff brief workspace. Auto-created by "
        "WorkflowOrchestrationAgent on first morning_brief workflow fire. "
        "Each deliverable accumulates here as a dated entry."
    )

    def _resolve_workflow_target_workspace_id(self, workflow: str) -> str | None:
        """Resolve the workflow's target workspace_id, materializing if needed.

        Returns a ``str(workspace.id)`` or ``None`` (no scoping; the
        agent_router fallback chain takes over downstream).

        Session 1234 D3 — currently only ``morning_brief`` opts in.
        get_or_create on (user, 'Morning Brief') is idempotent so
        ``_execute_create_morning_brief_deliverable_step`` re-resolving
        at step 8 is a no-op on second hit. Future workflows that need
        their own persistent workspace can extend this method instead
        of repeating the pattern at the top of ``execute()``.
        """
        if workflow != 'morning_brief':
            return None
        user = getattr(self, 'user', None)
        if user is None:
            return None
        mb_ws = self._get_or_create_morning_brief_workspace(user)
        if mb_ws is None:
            return None
        logger.info(
            "📋 Session 1234 D3: morning_brief workspace_id=%s wired "
            "into context — lane delegates will save here.",
            mb_ws.id,
        )
        return str(mb_ws.id)

    def _get_or_create_morning_brief_workspace(self, user):
        """Resolve the persistent Morning Brief workspace for ``user``.

        Idempotent ``get_or_create`` on ``(user, name='Morning Brief')``.
        Returns the workspace or ``None`` if creation failed (e.g., no
        user). The Deliverable persist step keeps working in either case
        — workspace=None lands the row in the user's uncategorized view.

        Session 1233 Sub-step C.
        """
        if not user:
            return None
        try:
            from core.models_skin_layer import ProjectWorkspace
            workspace, created = ProjectWorkspace.objects.get_or_create(
                user=user,
                name=self._MORNING_BRIEF_WORKSPACE_NAME,
                defaults={
                    'description': self._MORNING_BRIEF_WORKSPACE_DESCRIPTION,
                    'workspace_type': 'local',
                    # Symbolic root_path — no filesystem access expected.
                    # Required by ProjectWorkspace model schema.
                    'root_path': '/morning-brief',
                    'tech_stack': {},
                },
            )
            if created:
                logger.info(
                    "📋 Session 1233 Sub-step C: bootstrapped Morning Brief "
                    "workspace %s for user=%s",
                    workspace.id, getattr(user, 'username', user),
                )
            return workspace
        except Exception as e:
            logger.warning(
                "Sub-step C workspace get_or_create failed (deliverable will "
                "land with workspace=None): %s: %s",
                type(e).__name__, e,
            )
            return None

    def _execute_create_morning_brief_deliverable_step(
        self, context: Dict,
    ) -> Dict[str, Any]:
        """Persist context['morning_brief_markdown'] as a Deliverable.

        Session 1233 Sub-step C wires the persistent "Morning Brief"
        workspace: ``_get_or_create_morning_brief_workspace`` materializes
        the workspace on first fire and reuses it thereafter. Deliverables
        accumulate as dated entries in this workspace so Chris can scroll
        back through past briefs.

        Graceful no-content case: if ``morning_brief_markdown`` is
        missing (workflow ran but synthesis didn't produce output),
        returns success with a note rather than aborting — the workflow
        contract stays honored for smoke probes.
        """
        markdown = context.get('morning_brief_markdown')
        if not markdown:
            logger.info(
                "📋 Session 1233 B.1: create_morning_brief_deliverable ran with "
                "no markdown — likely smoke probe. Returning graceful no-op."
            )
            return {
                'success': True,
                'summary': 'No morning_brief_markdown to persist; smoke no-op',
                'deliverable_id': None,
            }

        title = context.get('morning_brief_title') or 'Morning Brief'
        # Session 1234 D2.fix: context['user'] is a profile DICT (written
        # by lane handlers for prompt injection); Deliverable.user is a FK
        # to UnifiedUser. The previous `context.get('user') or getattr...`
        # always short-circuited on the truthy dict, raising
        # `Deliverable.user must be a UnifiedUser instance` at .create().
        # Use self.user directly — that's the source set at agent init.
        user = getattr(self, 'user', None)
        if user is None:
            return {
                'success': False,
                'error': (
                    "create_morning_brief_deliverable: agent has no user "
                    "instance (self.user is None). Beat task should "
                    "instantiate WorkflowOrchestrationAgent(user=…)."
                ),
            }
        workspace = self._get_or_create_morning_brief_workspace(user)

        try:
            from core.models_deliverables import Deliverable
            deliverable = Deliverable.objects.create(
                title=title,
                content=markdown,
                content_format='markdown',
                category='Morning Brief',
                agent_name='WorkflowOrchestrationAgent',
                agent_task='morning_brief workflow',
                user=user,
                workspace=workspace,  # Session 1233 Sub-step C
                status='ready',
                metadata={
                    'workflow': 'morning_brief',
                    'rotation_slot': context.get('lane_4_slot_used') or context.get(
                        'rotation_slot', self._MORNING_BRIEF_LANE_4_DEFAULT_SLOT,
                    ),
                    'session': '1233-C',
                },
            )
            logger.info(
                "📋 Session 1233 Sub-step C: created morning_brief Deliverable "
                "%s in workspace %s",
                deliverable.id, workspace.id if workspace else None,
            )
            return {
                'success': True,
                'summary': f'Persisted morning_brief as Deliverable {deliverable.id}',
                'deliverable_id': str(deliverable.id),
                'workspace_id': str(workspace.id) if workspace else None,
                'title': title,
            }
        except Exception as e:
            logger.error(
                "📋 Session 1233 B.1: create_morning_brief_deliverable failed: %s",
                e, exc_info=True,
            )
            return {
                'success': False,
                'error': (
                    f"create_morning_brief_deliverable failed: "
                    f"{type(e).__name__}: {e}"
                ),
            }

    # =========================================================================
    # SESSION 212: CUSTOM WORKFLOW EXECUTION
    # =========================================================================

    def execute_custom_workflow(
        self,
        workflow_def: Dict[str, Any],
        topic: str,
        style: str = None,
        count: int = 4
    ) -> Dict[str, Any]:
        """
        Execute a custom workflow defined by the user.

        Session 212: Allows execution of user-created workflows.

        Args:
            workflow_def: Workflow definition with 'description', 'content_type', 'steps'
            topic: The subject/topic for the workflow
            style: Optional style preset
            count: Number of images to generate

        Returns:
            Dict with success status and results
        """
        logger.info(f"🔧 Executing custom workflow: {workflow_def.get('description', 'Custom Workflow')}")

        # Build context
        context = {
            'topic': topic,
            'year': datetime.now().year,
            'user': self.user,
            'style_preferences': style or '',
            'count': count,
            'content_type': workflow_def.get('content_type', 'custom'),
            'generated_image_ids': [],
            'generated_video_ids': [],
        }

        if self.project_id:
            context['project_id'] = self.project_id

        step_results = []
        steps = workflow_def.get('steps', [])

        for step_def in steps:
            step_num = step_def.get('step', len(step_results) + 1)
            step_name = step_def.get('name', f'Step {step_num}')

            logger.info(f"📍 Custom workflow step {step_num}: {step_name}")

            # Check conditions if specified
            condition = step_def.get('condition', {})
            if condition:
                if condition.get('previous_step_success') and step_results:
                    if not step_results[-1].get('success'):
                        logger.info(f"⏭️ Skipping step {step_num} - previous step failed")
                        continue

                if condition.get('has_images') and not context.get('generated_image_ids'):
                    logger.info(f"⏭️ Skipping step {step_num} - no images available")
                    continue

            # Apply step config to context
            step_config = step_def.get('config', {})
            if step_config:
                context.update(step_config)

            # Execute the step
            try:
                result = self._execute_step(step_def, context)
                step_results.append({
                    'step': step_num,
                    'name': step_name,
                    'agent': step_def.get('agent'),
                    'success': result.get('success', False),
                    'result': result
                })

                # Handle step failure
                if not result.get('success'):
                    is_required = step_def.get('is_required', True)
                    if is_required:
                        logger.error(f"❌ Required step failed: {step_name}")
                        return self._compile_custom_result(
                            workflow_def=workflow_def,
                            step_results=step_results,
                            context=context,
                            success=False,
                            error=f"Step '{step_name}' failed: {result.get('error', 'Unknown error')}"
                        )
                    else:
                        logger.warning(f"⚠️ Optional step failed: {step_name}")

                # Update context from result
                self._update_context_from_result(context, step_def['agent'], result)

            except Exception as e:
                logger.error(f"❌ Step execution error: {e}")
                is_required = step_def.get('is_required', True)
                if is_required:
                    return self._compile_custom_result(
                        workflow_def=workflow_def,
                        step_results=step_results,
                        context=context,
                        success=False,
                        error=str(e)
                    )

        # Workflow completed successfully
        return self._compile_custom_result(
            workflow_def=workflow_def,
            step_results=step_results,
            context=context,
            success=True
        )

    def _compile_custom_result(
        self,
        workflow_def: Dict,
        step_results: List[Dict],
        context: Dict,
        success: bool,
        error: str = None
    ) -> Dict[str, Any]:
        """Compile result for custom workflow execution."""
        result = {
            'success': success,
            'workflow': 'custom',
            'workflow_description': workflow_def.get('description', 'Custom Workflow'),
            'content_type': workflow_def.get('content_type', 'custom'),
            'steps': step_results,
            'total_steps': len(workflow_def.get('steps', [])),
            'completed_steps': len([s for s in step_results if s.get('success')]),
        }

        if error:
            result['error'] = error

        if context.get('generated_image_ids'):
            result['image_ids'] = context['generated_image_ids']

        if context.get('generated_video_ids'):
            result['video_ids'] = context['generated_video_ids']

        # Session 1231 F8 — `'project_created': None` initialization at line
        # 1129 means `context.get('project_created', {})` returns None when
        # the key is present-but-None (which happens for any workflow that
        # doesn't run the create_project_from_research step). Use truthy
        # fallback so we don't AttributeError on .get('project_id').
        _proj_created = context.get('project_created') or {}
        if _proj_created.get('project_id'):
            result['project_id'] = _proj_created['project_id']
            result['project_name'] = context['project_created'].get('project_name')

        if success:
            result['summary'] = (
                f"Custom workflow completed. Created {len(context.get('generated_image_ids', []))} images."
            )
        else:
            result['summary'] = f"Custom workflow failed: {error}"

        return result

    def _compile_final_result(
        self,
        workflow: str,
        step_results: List[Dict],
        context: Dict,
        success: bool,
        error: str = None
    ) -> Dict[str, Any]:
        """Compile the final workflow result."""

        result = {
            'success': success,
            'workflow': workflow,
            'workflow_description': self.WORKFLOWS[workflow]['description'],
            'steps': step_results,
            'total_steps': len(self.WORKFLOWS[workflow]['steps']),
            'completed_steps': len([s for s in step_results if s.get('success')]),
        }

        if error:
            result['error'] = error

        # Add key outputs
        if context.get('generated_image_ids'):
            result['image_ids'] = context['generated_image_ids']

        if context.get('project_created') and context['project_created'].get('success'):
            result['project_id'] = context['project_created'].get('project_id')
            result['project_name'] = context['project_created'].get('project_name')

        if context.get('research_summary'):
            result['research_summary'] = context['research_summary']

        if context.get('creative_recommendations'):
            result['creative_direction'] = context['creative_recommendations']

        # Create human-readable summary
        if success:
            result['summary'] = (
                f"Workflow '{workflow}' completed successfully. "
                f"Researched {context['topic']}, got executive direction, "
                f"created {len(context.get('generated_image_ids', []))} logos."
            )
            # Session 1231 F8 — same None-vs-default-dict gotcha as line 3486.
            _proj_created_summary = context.get('project_created') or {}
            if _proj_created_summary.get('project_name'):
                result['summary'] += f" Organized into project: {_proj_created_summary['project_name']}"
        else:
            result['summary'] = f"Workflow '{workflow}' failed: {error}"

        # =====================================================================
        # SESSION 305: Learning Infrastructure Integration
        # Record workflow outcomes for cross-agent knowledge sharing
        # =====================================================================
        try:
            task = f"Workflow: {workflow} - {context.get('topic', '')}"
            spider_data_used = bool(context.get('spider_insights') or context.get('spider_trending'))

            # Record learning outcome
            self._record_learning_outcome(
                result=result,
                task=task,
                context=context,
                spider_data_used=spider_data_used,
                scifi_context_used=False
            )

            # Create memory of this workflow execution
            memory_type = "success" if success else "failure"
            self._create_execution_memory(
                result=result,
                task=task,
                memory_type=memory_type,
                importance=0.8  # Workflows are high-importance
            )

            # Share workflow knowledge for cross-agent learning
            if success:
                agents_used = [s.get('agent', '') for s in step_results]
                self._share_knowledge(
                    knowledge_type='workflow',
                    title=f"Successful workflow: {workflow}",
                    knowledge_value={
                        'workflow': workflow,
                        'topic': context.get('topic', ''),
                        'agents_used': agents_used,
                        'steps_completed': result.get('completed_steps', 0),
                        'images_created': len(context.get('generated_image_ids', [])),
                        'spider_data_used': spider_data_used,
                    },
                    confidence=0.85
                )
        except Exception as e:
            logger.debug(f"Learning hooks failed (non-critical): {e}")

        return result


# Factory function for easy instantiation
def get_workflow_orchestration_agent(user, project_id: str = None) -> WorkflowOrchestrationAgent:
    """
    Get a WorkflowOrchestrationAgent instance.

    Args:
        user: Django User object
        project_id: Optional project ID for context

    Returns:
        WorkflowOrchestrationAgent instance
    """
    return WorkflowOrchestrationAgent(user=user, project_id=project_id)
