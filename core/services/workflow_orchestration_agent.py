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
from typing import Dict, Any, List
from datetime import datetime

from agents.base_agent import BaseContentAgent

logger = logging.getLogger(__name__)


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
                    # Don't stop workflow on non-critical failures
                    if step_name in ['create_project']:
                        # Project creation failing is non-critical
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

        else:
            return {
                'success': False,
                'error': f"Unknown agent in workflow: {agent_name}"
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

        if context.get('project_created', {}).get('project_id'):
            result['project_id'] = context['project_created']['project_id']
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
            if context.get('project_created', {}).get('project_name'):
                result['summary'] += f" Organized into project: {context['project_created']['project_name']}"
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
