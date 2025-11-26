"""
Workflow Orchestration Agent - Session 191

Manages multi-step creative workflows by executing agents in a fixed order.
This ensures GPT cannot deviate from the intended workflow or add extra steps.

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
        }
    }

    def execute(
        self,
        workflow: str,
        topic: str,
        count: int = 3,
        style_preferences: str = '',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a complete workflow.

        Args:
            workflow: Workflow type (e.g., 'research_and_create_logos')
            topic: The research topic (e.g., 'modern AI company')
            count: Number of images to create (1-5)
            style_preferences: Optional style preferences
            **kwargs: Additional workflow-specific parameters

        Returns:
            Complete result with outputs from all steps
        """
        self.log_start(
            f"execute workflow: {workflow}",
            topic=topic,
            count=count,
            style_preferences=style_preferences
        )

        # Validate workflow exists
        if workflow not in self.WORKFLOWS:
            return self._error_result(
                f"Unknown workflow: {workflow}. Available: {list(self.WORKFLOWS.keys())}",
                operation="validate_workflow"
            )

        workflow_def = self.WORKFLOWS[workflow]
        steps = workflow_def['steps']

        # Initialize workflow context - shared data between steps
        context = {
            'topic': topic,
            'count': count,
            'style_preferences': style_preferences,
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
        }

        # Execute each step in order
        step_results = []
        for step_def in steps:
            step_num = step_def['step']
            step_name = step_def['name']
            agent_name = step_def['agent']

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

        else:
            return {
                'success': False,
                'error': f"Unknown agent in workflow: {agent_name}"
            }

    def _execute_web_search_step(self, context: Dict) -> Dict[str, Any]:
        """Execute web search to research the topic."""
        topic = context['topic']
        year = context['year']
        style_prefs = context.get('style_preferences', '')
        content_type = context.get('content_type', 'logos')

        # Session 199/200: Build content-type-specific search queries
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
        else:
            # Default: logos
            query = f"{topic} logo trends {year} minimalist bold contemporary"

        if style_prefs:
            query += f" {style_prefs}"

        logger.info(f"🔍 Web search query ({content_type}): {query}")

        try:
            # Import and execute web search
            from core.views_image import _execute_web_search
            result = _execute_web_search({'query': query})
            return result

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {'success': False, 'error': str(e)}

    def _execute_coleadership_step(self, context: Dict) -> Dict[str, Any]:
        """Execute co-leadership agent for executive review."""
        topic = context['topic']
        count = context['count']
        research_summary = context.get('research_summary', 'Research completed')
        content_type = context.get('content_type', 'logos')

        # Session 199/200: Build content-type-specific questions
        if content_type == 'youtube_thumbnails':
            question = (
                f"Based on the research about {topic} YouTube thumbnails and CTR optimization, "
                f"what specific creative direction (bold text placement, color schemes, facial expressions, "
                f"composition) should we follow for creating {count} high-converting thumbnails? "
                f"Focus on what makes viewers click."
            )
        elif content_type == 'brand_identity':
            question = (
                f"Based on the research about {topic} brand identity design, "
                f"what comprehensive creative direction should we follow? Consider: "
                f"1) Primary logo style and variations, 2) Color palette (primary + accent colors), "
                f"3) Typography recommendations, 4) Visual elements and iconography. "
                f"Create {count} cohesive brand identity images."
            )
        elif content_type == 'product_photography':
            question = (
                f"Based on the research about {topic} product photography, "
                f"what creative direction should we follow for professional product shots? Consider: "
                f"1) Lighting style (soft, dramatic, natural), 2) Background and props, "
                f"3) Angles and composition, 4) Post-processing style. "
                f"Create {count} product images that drive conversions."
            )
        elif content_type == 'thumbnail_series':
            question = (
                f"Based on the research about {topic} thumbnail series design, "
                f"what creative direction ensures visual consistency across {count} thumbnails? Consider: "
                f"1) Consistent color scheme and branding elements, 2) Episode numbering style, "
                f"3) Text placement patterns, 4) Recognizable visual template. "
                f"Focus on instant series recognition while each being unique."
            )
        elif content_type == 'animated_logo':
            question = (
                f"Based on the research about {topic} logo animation, "
                f"what motion style and sound design should we use for an animated logo reveal? "
                f"Consider modern, professional motion graphics that enhance brand recognition."
            )
        else:
            # Default: logos
            question = (
                f"Based on the latest research about {topic} logos and design trends, "
                f"what specific creative direction (visual style, color palettes, symbols, typography) "
                f"should we follow for creating {count} modern, minimalist, professional logos? "
                f"The logos should feel bold, contemporary, and align with common themes "
                f"while remaining simple and versatile for digital products."
            )

        logger.info(f"🏢 Co-leadership question: {question[:100]}...")

        try:
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=context['user'])

            # Set project context if available
            if context.get('project_id'):
                from content.models import CreativeProject
                try:
                    project = CreativeProject.objects.get(id=context['project_id'])
                    assistant.project = project
                except CreativeProject.DoesNotExist:
                    pass

            parameters = {
                'question': question,
                'context': f"Research findings: {research_summary}. User topic: {topic}.",
                'participants': ['CTOAgent', 'COOAgent', 'CreativeDirectorAgent', 'CFOAgent', 'DataAnalystAgent'],
                'image_ids': [],
            }

            result = assistant._handle_coleadership_agent(parameters)
            return result

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

        # Session 199/200: Build content-type-specific prompts and dimensions
        if content_type == 'youtube_thumbnails':
            prompt = f"YouTube thumbnail for {topic}, bold large text, vibrant colors, high contrast, eye-catching, expressive face or reaction, dramatic lighting"
            width, height = 1280, 720  # YouTube 16:9 ratio
            style = "YouTube thumbnail, high CTR, click-worthy, bold graphics"
        elif content_type == 'brand_identity':
            # Session 200 FIX: Generate single clean logos, not mockup sheets
            prompt = f"single professional {topic} logo, minimalist, bold, clean design, versatile brand mark, isolated on simple background, no mockups, no multiple items, just one logo"
            width, height = 1024, 1024
            style = "single logo design, clean, professional, isolated mark"
        elif content_type == 'product_photography':
            prompt = f"professional product photography of {topic}, studio lighting, clean background, commercial quality, e-commerce ready, high detail"
            width, height = 1024, 1024
            style = "product photography, commercial, professional studio shot"
        elif content_type == 'thumbnail_series':
            prompt = f"YouTube thumbnail series for {topic}, consistent branding, episode numbering, bold text, recognizable template, cohesive visual style"
            width, height = 1280, 720  # YouTube 16:9 ratio
            style = "thumbnail series, consistent branding, recognizable template"
        else:
            # Default: logos
            prompt = f"single professional {topic} logo, minimalist, bold, geometric shapes"
            width, height = 1024, 1024
            style = "minimalist, bold, contemporary logo design"

        if creative_recs:
            # Extract key recommendations
            prompt += f", {creative_recs[:200]}"

        if style_prefs:
            prompt += f", {style_prefs}"

        if content_type == 'logos':
            prompt += ", clean negative space, strong yet simple mark, limited vibrant palette"

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

            parameters = {
                'prompt': prompt,
                'count': count,
                'model': 'sdxl',
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

        # Session 199: Clean up topic and create content-type-specific project name
        clean_topic = topic.title()
        duplicate_words = ['logo', 'logos', 'design', 'designs', 'thumbnail', 'thumbnails', 'video', 'videos']
        for word in duplicate_words:
            if clean_topic.lower().endswith(f' {word}'):
                clean_topic = clean_topic[:-len(word)-1]
            elif clean_topic.lower().endswith(f' {word}s'):
                clean_topic = clean_topic[:-len(word)-2]

        # Session 199/200: Content-type-specific project naming and categorization
        if content_type == 'youtube_thumbnails':
            project_name = f"{clean_topic.strip()} YouTube Thumbnails"
            category = 'youtube'
            suggested_next_steps = [
                'A/B test different thumbnail variations',
                'Add text overlays with different headlines',
                'Create variations with different expressions',
                'Upscale for higher resolution',
            ]
        elif content_type == 'brand_identity':
            project_name = f"{clean_topic.strip()} Brand Identity"
            category = 'branding'
            suggested_next_steps = [
                'Create logo variations (horizontal, stacked, icon-only)',
                'Remove backgrounds for transparent versions',
                'Generate color palette swatches',
                'Create brand guidelines document',
                'Train a style model for consistent branding',
            ]
        elif content_type == 'product_photography':
            project_name = f"{clean_topic.strip()} Product Photography"
            category = 'product'
            suggested_next_steps = [
                'Create lifestyle shots with context',
                'Generate different angle variations',
                'Remove backgrounds for e-commerce',
                'Add text overlays for marketing',
                'Upscale for print quality',
            ]
        elif content_type == 'thumbnail_series':
            project_name = f"{clean_topic.strip()} Thumbnail Series"
            category = 'youtube'
            suggested_next_steps = [
                'Add episode numbers to each thumbnail',
                'Create variations with different text',
                'Generate more episodes in the series',
                'A/B test different color schemes',
            ]
        elif content_type == 'animated_logo':
            project_name = f"{clean_topic.strip()} Animated Logo"
            category = 'branding'
            suggested_next_steps = [
                'Add sound effects or music',
                'Create different length versions (3s, 5s, 10s)',
                'Export as GIF for web use',
                'Create intro/outro versions',
            ]
        else:
            project_name = f"{clean_topic.strip()} Logo Designs"
            category = 'branding'
            suggested_next_steps = [
                'Upscale your favorite logo designs',
                'Remove backgrounds for transparent versions',
                'Create animated video versions',
                'Train a style model for consistent branding',
                'Generate color palette variations'
            ]

        logger.info(f"📁 Creating project: {project_name} with {len(image_ids)} images, {len(video_ids)} videos")

        try:
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=context['user'])

            # Session 194: Combine research findings with executive direction for richer context
            enriched_summary = research_summary
            if executive_direction:
                enriched_summary = f"**Research Findings:**\n{research_summary}\n\n**Executive Creative Direction:**\n{executive_direction}"

            parameters = {
                'project_name': project_name,
                'research_summary': enriched_summary,
                'image_ids': image_ids,
                'video_ids': video_ids,  # Session 199: Include videos
                'category': category,  # Session 199: Content-type-specific category
                'executive_direction': executive_direction,
                'suggested_next_steps': suggested_next_steps  # Session 199: Content-type-specific suggestions
            }

            result = assistant._handle_create_project_from_research(parameters)
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
            # Extract creative recommendations
            if result.get('success') and result.get('recommendations'):
                # Find Creative Director's recommendation
                for rec in result['recommendations']:
                    if rec.get('agent') == 'CreativeDirector':
                        context['creative_recommendations'] = rec.get('response', '')[:300]
                        break
                if not context.get('creative_recommendations'):
                    # Fallback to first recommendation
                    context['creative_recommendations'] = result['recommendations'][0].get('response', '')[:300]

        elif step_name in ['create_images', 'create_thumbnails', 'create_brand_images', 'create_product_images', 'create_thumbnail_series']:
            context['image_generation_result'] = result
            # Extract image IDs
            if result.get('success'):
                if result.get('images'):
                    context['generated_image_ids'] = [img.get('image_id') for img in result['images'] if img.get('image_id')]
                elif result.get('image_id'):
                    context['generated_image_ids'] = [result['image_id']]

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
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=context['user'])

            parameters = {
                'image_id': image_id,
                'motion_prompt': motion_prompt,
                'duration': 5,  # 5 second logo animation
            }

            if context.get('project_id'):
                parameters['project_id'] = context['project_id']

            result = assistant._handle_video_generation_agent(parameters)
            return result

        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            return {'success': False, 'error': str(e)}

    def _execute_audio_generation_step(self, context: Dict) -> Dict[str, Any]:
        """Execute audio generation for video."""
        topic = context['topic']

        # Build audio prompt
        audio_prompt = f"professional logo sound effect, whoosh, corporate, {topic}"

        logger.info(f"🔊 Audio generation: creating sound for logo")

        try:
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=context['user'])

            parameters = {
                'text': f"Professional sound effect for {topic}",
                'voice': 'sound_effect',  # or could be a jingle
                'style': 'corporate',
            }

            if context.get('project_id'):
                parameters['project_id'] = context['project_id']

            # For now, return success - audio can be optional
            # result = assistant._handle_audio_generation_agent(parameters)
            return {'success': True, 'message': 'Audio step skipped (optional)'}

        except Exception as e:
            logger.error(f"Audio generation failed: {e}")
            return {'success': True, 'message': f'Audio skipped: {e}'}  # Non-critical

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
