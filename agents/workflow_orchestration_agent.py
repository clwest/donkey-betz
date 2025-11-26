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
        }
        # Future workflows can be added here
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
            # Results from each step
            'research_results': None,
            'research_summary': '',
            'executive_direction': None,
            'creative_recommendations': '',
            'generated_image_ids': [],
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

        # Build search query
        query = f"{topic} logo trends {year} minimalist bold contemporary"
        if style_prefs:
            query += f" {style_prefs}"

        logger.info(f"🔍 Web search query: {query}")

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

        # Build question for executive team
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
        """Execute image generation agent to create logos."""
        topic = context['topic']
        count = context['count']
        style_prefs = context.get('style_preferences', '')
        creative_recs = context.get('creative_recommendations', '')

        # Build prompt incorporating executive direction
        prompt = f"single professional {topic} logo, minimalist, bold, geometric shapes"

        if creative_recs:
            # Extract key recommendations
            prompt += f", {creative_recs[:200]}"

        if style_prefs:
            prompt += f", {style_prefs}"

        prompt += ", clean negative space, strong yet simple mark, limited vibrant palette"

        logger.info(f"🎨 Image generation prompt: {prompt[:100]}...")
        logger.info(f"🎨 Generating {count} logos")

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
                'style': 'minimalist, bold, contemporary logo design',
                'width': 1024,
                'height': 1024,
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
        research_summary = context.get('research_summary', 'Research and logos created')
        executive_direction = context.get('creative_recommendations', '')
        image_ids = context.get('generated_image_ids', [])

        if not image_ids:
            logger.warning("⚠️ No image IDs to add to project")

        # Session 194: Clean up project name - remove duplicate words like 'logo'
        # Remove common words that might be duplicated when we add "Logo Designs"
        clean_topic = topic.title()
        duplicate_words = ['logo', 'logos', 'design', 'designs']
        for word in duplicate_words:
            # Remove the word if it's at the end (case insensitive)
            if clean_topic.lower().endswith(f' {word}'):
                clean_topic = clean_topic[:-len(word)-1]
            elif clean_topic.lower().endswith(f' {word}s'):
                clean_topic = clean_topic[:-len(word)-2]

        project_name = f"{clean_topic.strip()} Logo Designs"

        logger.info(f"📁 Creating project: {project_name} with {len(image_ids)} images")

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
                'category': 'branding',
                'executive_direction': executive_direction,  # Session 194: Pass for metadata
                'suggested_next_steps': [
                    'Upscale your favorite logo designs',
                    'Remove backgrounds for transparent versions',
                    'Create animated video versions',
                    'Train a style model for consistent branding',
                    'Generate color palette variations'
                ]
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

        elif step_name == 'create_images':
            context['image_generation_result'] = result
            # Extract image IDs
            if result.get('success'):
                if result.get('images'):
                    context['generated_image_ids'] = [img.get('image_id') for img in result['images'] if img.get('image_id')]
                elif result.get('image_id'):
                    context['generated_image_ids'] = [result['image_id']]

        elif step_name == 'create_project':
            context['project_created'] = result

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

        return "Completed"

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
