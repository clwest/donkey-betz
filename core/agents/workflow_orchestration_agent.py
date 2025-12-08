"""
Workflow Orchestration Agent - Clean Architecture Wrapper
=========================================================

Session 393: Refactored to use BaseAgent while preserving all legacy functionality.

This module provides a clean architecture adapter for the legacy WorkflowOrchestrationAgent.
It wraps the existing 3,120-line orchestrator to work with the BaseAgent pattern
while preserving all its predefined workflow templates and features.

Key Features Preserved:
    - 16+ predefined workflow templates (research_and_create_logos, youtube_thumbnail_package, etc.)
    - Spider intelligence integration
    - Project research context injection
    - Executive review (co-leadership) steps
    - Style and mascot extraction
    - Content-type-specific prompts and dimensions

Why a Wrapper?
    The legacy WorkflowOrchestrationAgent has extensive, battle-tested logic for:
    - Extracting styles from user messages (Pixar, Disney, etc.)
    - Building content-type-specific image prompts
    - Integrating spider trending data into research
    - Injecting project research context

    Rewriting this would be risky. Instead, we wrap it to gain BaseAgent benefits:
    - TimeTravelMixin for decision tracking
    - Learning infrastructure hooks
    - Consistent AgentResult interface
    - Clean architecture compatibility

Usage:
    from core.agents.workflow_orchestration_agent import WorkflowOrchestrationAgent

    agent = WorkflowOrchestrationAgent(user=request.user)
    result = agent.execute(
        task="Create logos for my AI startup",
        context={'workflow': 'research_and_create_logos', 'count': 3},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
from typing import Dict, Any, List, Optional

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


# List of available workflows for reference
AVAILABLE_WORKFLOWS = [
    'research_and_create_logos',
    'research_and_create_images',
    'youtube_thumbnail_package',
    'brand_identity_package',
    'product_photography_kit',
    'video_thumbnail_series',
    'logo_to_video',
    'social_media_kit',
    'podcast_visual_package',
    'ebook_cover_series',
    'video_production_kit',
    'course_thumbnail_series',
    'pitch_deck_visuals',
    'product_launch_kit',
    'business_research',
    'competitor_analysis',
    'customer_research',
]


class WorkflowOrchestrationAgent(BaseAgent):
    """
    Clean architecture wrapper for the legacy WorkflowOrchestrationAgent.

    This agent orchestrates multi-step creative workflows using predefined
    templates. It wraps the legacy implementation to work with BaseAgent.

    Workflows:
        - research_and_create_logos: Research + executive review + image generation + project
        - youtube_thumbnail_package: Research + thumbnails (1280x720)
        - brand_identity_package: Complete brand identity with logos
        - product_photography_kit: Professional product images
        - video_thumbnail_series: Consistent thumbnail series
        - logo_to_video: Animate logo into video
        - social_media_kit: Multi-platform social content
        - podcast_visual_package: Podcast cover art and quote cards
        - ebook_cover_series: Book cover designs
        - video_production_kit: Thumbnails, intros, end screens
        - course_thumbnail_series: Online course thumbnails
        - pitch_deck_visuals: Pitch deck graphics
        - product_launch_kit: Product launch visuals
        - business_research: Competitor + customer research
        - competitor_analysis: Deep competitor dive
        - customer_research: Customer personas and pain points
    """

    name = "WorkflowOrchestrationAgent"

    system_prompt = """You are WorkflowOrchestrationAgent, a specialist in executing predefined creative workflow packages.

Your job is to run multi-step creative workflows that have been pre-defined for specific outcomes.
Each workflow has fixed steps in a specific order - you execute them reliably.

Available Workflows:
1. research_and_create_logos - Research topic, get executive direction, generate logos, create project
2. youtube_thumbnail_package - Research + high-CTR YouTube thumbnails (1280x720)
3. brand_identity_package - Complete brand identity with logo symbols
4. product_photography_kit - Professional product images
5. video_thumbnail_series - Consistent series of thumbnails
6. logo_to_video - Animate existing logo
7. social_media_kit - Multi-platform social content
8. podcast_visual_package - Podcast covers and quote cards
9. ebook_cover_series - Book cover designs
10. video_production_kit - Video thumbnails, intros, end screens
11. course_thumbnail_series - Online course module thumbnails
12. pitch_deck_visuals - Pitch deck graphics
13. product_launch_kit - Product launch visuals
14. business_research - Comprehensive business intelligence
15. competitor_analysis - Deep competitor research
16. customer_research - Customer personas and pain points

Each workflow automatically:
- Queries spider intelligence for trending data
- Gets executive team creative direction
- Uses content-type-specific prompts and dimensions
- Injects project research context when available
- Tracks agent contributions

You execute complete workflow packages, not individual steps."""

    tools = []  # No GPT tools - workflows are executed programmatically

    def __init__(self, user=None, project_id: str = None):
        """
        Initialize the orchestration agent.

        Args:
            user: Django User object
            project_id: Optional project UUID for context
        """
        super().__init__(user)
        self.project_id = project_id
        self._legacy_agent = None

    @property
    def legacy_agent(self):
        """Lazy-load the legacy WorkflowOrchestrationAgent."""
        if self._legacy_agent is None:
            from agents.workflow_orchestration_agent import WorkflowOrchestrationAgent as LegacyAgent
            self._legacy_agent = LegacyAgent(
                user=self.user,
                project_id=self.project_id
            )
        return self._legacy_agent

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute a workflow using the legacy orchestrator.

        Args:
            task: Description of what to create (used to extract style/topic)
            context: Must contain 'workflow' key with workflow name.
                     Can also contain: count, style_preferences, topic, etc.
            scifi_context: Sci-fi features context (mood, memory, evolution)
            spider_context: Spider intelligence context (trends, market data)

        Returns:
            AgentResult with workflow execution results
        """
        start_time = time.time()

        with self.time_travel_session("workflow_orchestration", task, input_data=context):
            try:
                # Extract workflow name from context or infer from task
                workflow = context.get('workflow')

                if not workflow:
                    # Try to infer workflow from task
                    workflow = self._infer_workflow(task)

                if not workflow:
                    return AgentResult(
                        success=False,
                        error=f"No workflow specified. Available: {AVAILABLE_WORKFLOWS}",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="workflow_selection",
                    action=f"Executing workflow: {workflow}",
                    reasoning=f"Task: {task[:100]}",
                    alternatives=AVAILABLE_WORKFLOWS[:5],
                    confidence=0.95
                )

                # Extract parameters from context
                topic = context.get('topic', task)
                count = context.get('count', 3)
                style_preferences = context.get('style_preferences', '')
                user_message = context.get('user_message', task)

                # Execute via legacy agent
                legacy_result = self.legacy_agent.execute(
                    workflow=workflow,
                    topic=topic,
                    count=count,
                    style_preferences=style_preferences,
                    user_message=user_message,
                    **{k: v for k, v in context.items()
                       if k not in ['workflow', 'topic', 'count', 'style_preferences', 'user_message']}
                )

                execution_time = int((time.time() - start_time) * 1000)

                # Convert legacy result to AgentResult
                if legacy_result.get('success'):
                    result = AgentResult(
                        success=True,
                        message=legacy_result.get('message', f"Workflow '{workflow}' completed"),
                        data={
                            'workflow': workflow,
                            'step_results': legacy_result.get('step_results', []),
                            'image_ids': legacy_result.get('image_ids', []),
                            'video_ids': legacy_result.get('video_ids', []),
                            'project_created': legacy_result.get('project_created'),
                            'summary': legacy_result.get('summary', ''),
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=[]
                    )

                    self.mark_decision_outcome(
                        success=True,
                        result_summary=f"Workflow {workflow} completed successfully"
                    )

                    # Learning hooks
                    self._record_learning_outcome(
                        result, task, context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(result, task, "success", 0.8)
                    self._share_knowledge(
                        knowledge_type='technique',
                        title=f"Workflow completed: {workflow}",
                        knowledge_value={
                            'workflow': workflow,
                            'topic': topic,
                            'count': count,
                            'execution_time_ms': execution_time
                        },
                        confidence=0.85
                    )

                    return result

                else:
                    result = AgentResult(
                        success=False,
                        error=legacy_result.get('error', 'Workflow execution failed'),
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        data={
                            'workflow': workflow,
                            'step_results': legacy_result.get('step_results', []),
                        }
                    )

                    self.mark_decision_outcome(
                        success=False,
                        result_summary=f"Workflow {workflow} failed"
                    )

                    self._record_learning_outcome(result, task, context)
                    self._create_execution_memory(result, task, "failure", 0.7)

                    return result

            except Exception as e:
                logger.error(f"WorkflowOrchestrationAgent error: {e}", exc_info=True)
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _infer_workflow(self, task: str) -> Optional[str]:
        """
        Infer workflow type from task description.

        Args:
            task: User's task description

        Returns:
            Inferred workflow name or None
        """
        task_lower = task.lower()

        # Logo workflows
        if 'logo' in task_lower:
            if 'video' in task_lower or 'animate' in task_lower:
                return 'logo_to_video'
            elif 'brand' in task_lower or 'identity' in task_lower:
                return 'brand_identity_package'
            else:
                return 'research_and_create_logos'

        # Thumbnail workflows
        if 'thumbnail' in task_lower:
            if 'series' in task_lower or 'playlist' in task_lower:
                return 'video_thumbnail_series'
            elif 'course' in task_lower or 'module' in task_lower:
                return 'course_thumbnail_series'
            else:
                return 'youtube_thumbnail_package'

        # Product workflows
        if 'product' in task_lower:
            if 'launch' in task_lower:
                return 'product_launch_kit'
            else:
                return 'product_photography_kit'

        # Research workflows
        if 'competitor' in task_lower or 'competition' in task_lower:
            return 'competitor_analysis'
        if 'customer' in task_lower or 'persona' in task_lower:
            return 'customer_research'
        if 'research' in task_lower and 'business' in task_lower:
            return 'business_research'

        # Other content types
        if 'social media' in task_lower or 'social' in task_lower:
            return 'social_media_kit'
        if 'podcast' in task_lower:
            return 'podcast_visual_package'
        if 'ebook' in task_lower or 'book cover' in task_lower:
            return 'ebook_cover_series'
        if 'pitch' in task_lower or 'deck' in task_lower:
            return 'pitch_deck_visuals'
        if 'video' in task_lower and ('production' in task_lower or 'channel' in task_lower):
            return 'video_production_kit'

        # Default to general images if creative intent detected
        if any(word in task_lower for word in ['create', 'generate', 'make', 'design']):
            return 'research_and_create_images'

        return None

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        This agent doesn't use GPT tools - workflows are predefined.

        Returns:
            Error dict since tools shouldn't be called
        """
        return {
            'success': False,
            'error': f"WorkflowOrchestrationAgent uses predefined workflows, not tools. "
                    f"Pass 'workflow' in context instead."
        }

    @classmethod
    def get_available_workflows(cls) -> List[str]:
        """Return list of available workflow names."""
        return AVAILABLE_WORKFLOWS.copy()

    @classmethod
    def get_workflow_info(cls, workflow_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific workflow.

        Args:
            workflow_name: Name of the workflow

        Returns:
            Dict with workflow info or None if not found
        """
        from agents.workflow_orchestration_agent import WorkflowOrchestrationAgent as LegacyAgent

        if workflow_name not in LegacyAgent.WORKFLOWS:
            return None

        workflow_def = LegacyAgent.WORKFLOWS[workflow_name]
        return {
            'name': workflow_name,
            'description': workflow_def.get('description', ''),
            'content_type': workflow_def.get('content_type', 'general'),
            'steps': [
                {
                    'step': s['step'],
                    'name': s['name'],
                    'agent': s['agent'],
                    'description': s['description']
                }
                for s in workflow_def.get('steps', [])
            ],
            'no_image_generation': workflow_def.get('no_image_generation', False)
        }


# Factory function for backwards compatibility
def get_workflow_orchestration_agent(user=None, project_id: str = None) -> WorkflowOrchestrationAgent:
    """
    Factory function to create a WorkflowOrchestrationAgent.

    Args:
        user: Django User object
        project_id: Optional project UUID

    Returns:
        WorkflowOrchestrationAgent instance
    """
    return WorkflowOrchestrationAgent(user=user, project_id=project_id)
