"""
Deliverable Envelope Service - Session 819: Deliverables Marketplace

This service standardizes agent outputs into Deliverable objects,
transforming raw execution results into a consistent "envelope" format
suitable for display as product cards in the UI.

The envelope wraps:
- Agent result data into displayable content
- Execution metadata (timing, cost, tool calls)
- Quality metrics
- Classification (type, category, tags)

Session 846: Added citation gate integration to validate Research/Financial/Strategy
outputs have proper source citations before creating deliverables.
"""

import logging
import re
from typing import Optional, Dict, Any, List
from decimal import Decimal
from django.utils import timezone

from core.models_deliverables import (
    Deliverable,
    DeliverableType,
    ContentFormat,
)

logger = logging.getLogger(__name__)


class DeliverableEnvelopeService:
    """
    Standardizes agent outputs into Deliverable objects.

    Usage:
        service = DeliverableEnvelopeService()
        deliverable = service.wrap(
            agent_name='ContentWriterAgent',
            task='Write a blog post about AI trends',
            result=agent_result,
            user=request.user,
            operation=workspace_operation
        )
    """

    # Map agent names to deliverable types
    AGENT_TYPE_MAPPING: Dict[str, str] = {
        # Creation agents
        'ImageAgent': DeliverableType.IMAGE,
        'VideoAgent': DeliverableType.VIDEO,
        'AudioAgent': DeliverableType.AUDIO,
        'ThreeDAgent': DeliverableType.IMAGE,

        # Content agents
        'ContentWriterAgent': DeliverableType.DOCUMENT,
        'TechnicalDocumentAgent': DeliverableType.DOCUMENT,
        'LegalDocDrafterAgent': DeliverableType.DOCUMENT,

        # Research agents
        'ResearchAgent': DeliverableType.RESEARCH,
        'TrendAnalysisAgent': DeliverableType.ANALYSIS,
        'MarketIntelligenceAgent': DeliverableType.ANALYSIS,
        'CompetitorAnalysisAgent': DeliverableType.ANALYSIS,
        'CustomerResearchAgent': DeliverableType.RESEARCH,

        # Strategy agents
        'ContentStrategyAgent': DeliverableType.STRATEGY,
        'BrandIdentityAgent': DeliverableType.STRATEGY,
        'BrandStrategyAgent': DeliverableType.STRATEGY,
        'MarketingStrategyAgent': DeliverableType.STRATEGY,
        'SEOOptimizerAgent': DeliverableType.ANALYSIS,

        # Code agents
        'CodeGeneratorAgent': DeliverableType.CODE,
        'FullStackDeveloperAgent': DeliverableType.CODE,
        'CodeReviewAgent': DeliverableType.ANALYSIS,
        'DevOpsAgent': DeliverableType.CODE,
        'PromptEngineeringAgent': DeliverableType.TEMPLATE,

        # Analysis agents
        'OpportunityScoringAgent': DeliverableType.ANALYSIS,
        'StockAnalystAgent': DeliverableType.ANALYSIS,
        'PredictionMarketAnalyst': DeliverableType.ANALYSIS,
        'SportsOddsAnalyst': DeliverableType.ANALYSIS,
        'ArbitrageDetector': DeliverableType.ANALYSIS,

        # Planning agents
        'WorkflowAgent': DeliverableType.PLAN,
        'CampaignOrchestratorAgent': DeliverableType.PLAN,
        'ContentExecutorAgent': DeliverableType.PLAN,

        # Script/podcast agents
        'PodcastCoordinatorAgent': DeliverableType.SCRIPT,
        'DebateAdvocateAgent': DeliverableType.SCRIPT,
        'DebateSkepticAgent': DeliverableType.SCRIPT,
        'ModeratorAgent': DeliverableType.SCRIPT,

        # Default for unspecified agents
        'default': DeliverableType.DOCUMENT,
    }

    # Map agent names to categories
    AGENT_CATEGORY_MAPPING: Dict[str, str] = {
        'ContentWriterAgent': 'Content',
        'ImageAgent': 'Creative',
        'VideoAgent': 'Creative',
        'AudioAgent': 'Creative',
        'ResearchAgent': 'Research',
        'CodeGeneratorAgent': 'Development',
        'FullStackDeveloperAgent': 'Development',
        'CodeReviewAgent': 'Development',
        'DevOpsAgent': 'Development',
        'TrendAnalysisAgent': 'Analytics',
        'MarketIntelligenceAgent': 'Analytics',
        'StockAnalystAgent': 'Finance',
        'ContentStrategyAgent': 'Marketing',
        'BrandStrategyAgent': 'Marketing',
        'SEOOptimizerAgent': 'Marketing',
        'LegalDocDrafterAgent': 'Legal',
        'PodcastCoordinatorAgent': 'Podcast',
        'default': 'General',
    }

    # Map content to format based on patterns
    CONTENT_FORMAT_PATTERNS = [
        (r'^#+ ', ContentFormat.MARKDOWN),
        (r'^```', ContentFormat.MARKDOWN),
        (r'^\{', ContentFormat.JSON),
        (r'^<', ContentFormat.HTML),
        (r'^(def |class |import |from )', ContentFormat.PYTHON),
        (r'^(const |let |var |function |import |export )', ContentFormat.JAVASCRIPT),
        (r'^(interface |type |const |let |import )', ContentFormat.TYPESCRIPT),
    ]

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def wrap(
        self,
        agent_name: str,
        task: str,
        result: Dict[str, Any],
        user=None,
        operation=None,
        **kwargs
    ) -> Optional[Deliverable]:
        """
        Wrap an agent result into a Deliverable object.

        Args:
            agent_name: Name of the agent that produced the output
            task: The task/prompt given to the agent
            result: The agent result dictionary
            user: Optional user who owns this deliverable
            operation: Optional WorkspaceOperation that produced this
            **kwargs: Additional metadata including:
                - context: Dict with trace_id, project_id, parent info
                - parent_execution: AgentExecution to inherit trace from

        Returns:
            Deliverable object or None if wrapping failed
        """
        try:
            # Extract content from result
            content = self._extract_content(result)
            if not content:
                self.logger.warning(
                    f"No content to wrap from {agent_name} result"
                )
                return None

            # Session 846: Citation Gate - validate Research/Financial/Strategy outputs
            context = kwargs.get('context', {})
            parent_execution = kwargs.get('parent_execution')
            trace_id = context.get('trace_id')
            execution_id = parent_execution.id if parent_execution and hasattr(parent_execution, 'id') else None

            citation_valid = self._validate_citations(
                agent_name=agent_name,
                result=result,
                task=task,
                trace_id=trace_id,
                execution_id=execution_id,
            )

            # Determine deliverable type
            deliverable_type = self._determine_type(agent_name, result)

            # Determine category
            category = self._determine_category(agent_name, result)

            # Determine content format
            content_format = self._detect_content_format(content)

            # Generate title
            title = self._generate_title(agent_name, task, result)

            # Extract tags
            tags = self._extract_tags(task, content, result)

            # Calculate quality score
            quality_score = self._calculate_quality_score(result)

            # Extract execution metadata
            execution_time_ms = result.get('execution_time_ms', 0)
            llm_cost = Decimal(str(result.get('cost', 0)))
            tool_calls = result.get('tool_calls', [])

            # Session 843: Get trace context from kwargs or result (moved earlier for citation gate)

            # Resolve workspace: explicit kwarg > active workspace fallback
            active_workspace = None
            ws_id = kwargs.get('workspace_id')
            if ws_id:
                try:
                    from core.models_skin_layer import ProjectWorkspace
                    active_workspace = ProjectWorkspace.objects.filter(id=ws_id).first()
                except Exception:
                    pass
            if not active_workspace:
                try:
                    from core.models_skin_layer import ProjectWorkspace
                    active_workspace = ProjectWorkspace.objects.filter(is_active=True).first()
                except Exception:
                    pass

            # Create the deliverable
            deliverable = Deliverable.objects.create(
                title=title,
                deliverable_type=deliverable_type,
                category=category,
                tags=tags,
                source_operation=operation,
                agent_name=agent_name,
                agent_task=task,
                user=user,
                workspace=active_workspace,
                is_saved=bool(active_workspace),
                content=content,
                content_format=content_format,
                preview_content=self._generate_preview(content),
                quality_score=quality_score,
                confidence_score=result.get('confidence', 0.0),
                execution_time_ms=execution_time_ms,
                llm_cost=llm_cost,
                tool_calls=tool_calls,
                raw_output=result,
                metadata=kwargs.get('metadata', {}),
            )

            # Session 843: Attach trace context
            from core.services.trace_attachment_service import TraceAttachmentService
            TraceAttachmentService.attach_to_object(
                deliverable,
                context,
                parent_object=parent_execution,
                user=user,
                agent_name=agent_name,
            )
            deliverable.save()

            # Session 930: Auto-learning triggers
            self._trigger_learning_from_deliverable(deliverable, user)

            self.logger.info(
                f"Created deliverable: {deliverable.title} "
                f"(type={deliverable_type}, agent={agent_name}, trace_id={deliverable.trace_id})"
            )

            return deliverable

        except Exception as e:
            self.logger.error(
                f"Failed to wrap result from {agent_name}: {e}",
                exc_info=True
            )
            return None

    def wrap_from_operation(
        self,
        operation,
        user=None
    ) -> Optional[Deliverable]:
        """
        Create a Deliverable from a WorkspaceOperation.

        This is called after a workspace operation completes to create
        a user-facing deliverable from the operation's output data.
        """
        # Skip if operation has no output data or failed
        if not operation.success:
            return None

        # Try to extract content from operation
        content = None
        result = {}

        # Check file content for file operations
        if operation.file_content_after:
            content = operation.file_content_after
            result = {
                'content': content,
                'file_path': operation.file_path,
                'operation_type': operation.operation_type,
            }

        # Check command output for command operations
        elif operation.command_output:
            content = operation.command_output
            result = {
                'content': content,
                'command': operation.command,
                'operation_type': operation.operation_type,
            }

        if not content:
            return None

        return self.wrap(
            agent_name=operation.agent_name,
            task=operation.agent_task or f"{operation.operation_type}: {operation.file_path}",
            result=result,
            user=user or operation.user,
            operation=operation,
            metadata={
                'file_path': operation.file_path,
                'operation_type': operation.operation_type,
            }
        )

    def _extract_content(self, result: Dict[str, Any]) -> str:
        """Extract the main content from an agent result."""
        # Try common content keys
        content_keys = [
            'content', 'output', 'result', 'text', 'data',
            'document', 'code', 'analysis', 'report',
            'response', 'generated_content', 'blog_content',
        ]

        for key in content_keys:
            if key in result and isinstance(result[key], str):
                return result[key]

        # Try nested structures
        if 'data' in result and isinstance(result['data'], dict):
            for key in content_keys:
                if key in result['data']:
                    val = result['data'][key]
                    if isinstance(val, str):
                        return val

        # Handle tool_results format
        if 'tool_results' in result:
            tool_results = result['tool_results']
            if isinstance(tool_results, list) and tool_results:
                first = tool_results[0]
                if isinstance(first, dict) and 'result' in first:
                    return str(first['result'])

        # Last resort: stringify the whole result
        if result:
            # Remove metadata keys for cleaner output
            clean_result = {
                k: v for k, v in result.items()
                if k not in ['execution_time_ms', 'cost', 'confidence', 'tool_calls']
            }
            if clean_result:
                import json
                return json.dumps(clean_result, indent=2, default=str)

        return ''

    def _determine_type(
        self,
        agent_name: str,
        result: Dict[str, Any]
    ) -> str:
        """Determine the deliverable type based on agent and result."""
        # Check if result specifies a type
        if 'deliverable_type' in result:
            return result['deliverable_type']

        # Check if there are images/videos/audio in result
        if 'image_url' in result or 'images' in result:
            return DeliverableType.IMAGE
        if 'video_url' in result or 'video' in result:
            return DeliverableType.VIDEO
        if 'audio_url' in result or 'audio' in result:
            return DeliverableType.AUDIO

        # Use agent mapping
        return self.AGENT_TYPE_MAPPING.get(
            agent_name,
            self.AGENT_TYPE_MAPPING['default']
        )

    def _determine_category(
        self,
        agent_name: str,
        result: Dict[str, Any]
    ) -> str:
        """Determine the category based on agent and result."""
        if 'category' in result:
            return result['category']

        return self.AGENT_CATEGORY_MAPPING.get(
            agent_name,
            self.AGENT_CATEGORY_MAPPING['default']
        )

    def _detect_content_format(self, content: str) -> str:
        """Detect the format of the content."""
        if not content:
            return ContentFormat.TEXT

        first_line = content.split('\n')[0] if content else ''

        for pattern, format_type in self.CONTENT_FORMAT_PATTERNS:
            if re.match(pattern, first_line):
                return format_type

        # Check for common patterns in full content
        if '```' in content or content.count('#') > 3:
            return ContentFormat.MARKDOWN

        return ContentFormat.TEXT

    def _generate_title(
        self,
        agent_name: str,
        task: str,
        result: Dict[str, Any]
    ) -> str:
        """Generate a meaningful title for the deliverable."""
        # Check if result provides a title
        if 'title' in result:
            return result['title'][:255]

        # Clean up agent name for display
        agent_display = agent_name.replace('Agent', '').replace('_', ' ')

        # Extract key words from task
        task_preview = task[:80] if task else ''
        if len(task) > 80:
            task_preview = task[:77] + '...'

        # Generate title
        if task_preview:
            return f"{agent_display}: {task_preview}"
        else:
            return f"{agent_display} Output - {timezone.now().strftime('%Y-%m-%d %H:%M')}"

    def _generate_preview(self, content: str, max_length: int = 500) -> str:
        """Generate a preview of the content."""
        if not content:
            return ''

        preview = content[:max_length]
        if len(content) > max_length:
            # Try to break at a sentence or paragraph
            last_period = preview.rfind('.')
            last_newline = preview.rfind('\n')
            break_point = max(last_period, last_newline)
            if break_point > max_length // 2:
                preview = content[:break_point + 1]
            else:
                preview = content[:max_length] + '...'

        return preview

    def _extract_tags(
        self,
        task: str,
        content: str,
        result: Dict[str, Any]
    ) -> List[str]:
        """Extract relevant tags from the task and content."""
        tags = []

        # Use explicit tags from result
        if 'tags' in result:
            tags.extend(result['tags'])

        # Extract from task keywords
        task_lower = task.lower()
        keyword_tags = {
            'blog': ['blog', 'writing'],
            'report': ['report', 'analysis'],
            'code': ['code', 'development'],
            'image': ['image', 'visual'],
            'video': ['video', 'multimedia'],
            'audit': ['audit', 'review'],
            'strategy': ['strategy', 'planning'],
            'research': ['research'],
            'market': ['market', 'business'],
        }

        for keyword, tag_list in keyword_tags.items():
            if keyword in task_lower:
                tags.extend(tag_list)

        # Deduplicate and limit
        return list(set(tags))[:10]

    def _calculate_quality_score(self, result: Dict[str, Any]) -> float:
        """Calculate a quality score for the output."""
        score = 0.5  # Base score

        # Check for explicit quality metrics
        if 'quality_score' in result:
            return float(result['quality_score'])

        # Adjust based on result characteristics
        content = self._extract_content(result)

        # Content length (longer = more complete, up to a point)
        if content:
            word_count = len(content.split())
            if word_count > 100:
                score += 0.1
            if word_count > 500:
                score += 0.1
            if word_count > 1000:
                score += 0.1

        # Has confidence score
        if result.get('confidence', 0) > 0.7:
            score += 0.1

        # Completed successfully
        if result.get('success', True):
            score += 0.1

        return min(score, 1.0)

    def _validate_citations(
        self,
        agent_name: str,
        result: Dict[str, Any],
        task: str,
        trace_id=None,
        execution_id=None,
    ) -> bool:
        """
        Session 846: Validate citation requirements for critical agents.

        Uses CitationGateService to check Research/Financial/Strategy outputs
        have proper source citations. Currently runs in 'warn' mode - violations
        are logged but outputs are not blocked.

        Args:
            agent_name: Name of the agent
            result: The agent result dictionary
            task: The task/prompt
            trace_id: Optional trace ID for linking
            execution_id: Optional execution ID

        Returns:
            True if citations are valid or not required, False if violation logged
        """
        try:
            from core.services.citation_gate_service import get_citation_gate_service
            import uuid

            gate = get_citation_gate_service()

            # Check if this agent requires citations
            if not gate.requires_citations(agent_name):
                return True

            # Convert trace_id to UUID if needed
            trace_uuid = None
            if trace_id:
                if isinstance(trace_id, str):
                    try:
                        trace_uuid = uuid.UUID(trace_id)
                    except ValueError:
                        pass
                elif isinstance(trace_id, uuid.UUID):
                    trace_uuid = trace_id

            exec_uuid = None
            if execution_id:
                if isinstance(execution_id, str):
                    try:
                        exec_uuid = uuid.UUID(execution_id)
                    except ValueError:
                        pass
                elif isinstance(execution_id, uuid.UUID):
                    exec_uuid = execution_id

            # Enforce in 'warn' mode (log violations but don't block)
            is_valid = gate.enforce(
                agent_name=agent_name,
                result=result,
                task=task,
                trace_id=trace_uuid,
                execution_id=exec_uuid,
                mode='warn',
            )

            if not is_valid:
                self.logger.info(
                    f"Citation violation recorded for {agent_name} - output will proceed"
                )

            return is_valid

        except Exception as e:
            self.logger.warning(f"Citation gate check failed: {e}")
            return True  # Don't block on gate errors

    def _trigger_learning_from_deliverable(self, deliverable, user) -> None:
        """
        Session 930: Trigger automatic learning from deliverable creation.

        This calls the user learning services to:
        1. Infer and track skills demonstrated in the deliverable
        2. Auto-link the deliverable to relevant user goals

        Runs asynchronously to not block deliverable creation.
        """
        if not user:
            return

        try:
            # 1. Skill Evolution: Infer skills from deliverable content
            from core.services.skill_evolution_service import get_skill_evolution_service
            skill_service = get_skill_evolution_service()

            # Use quality_score as base quality for skill demonstrations
            base_quality = float(deliverable.quality_score) if deliverable.quality_score else 0.7

            demonstrations = skill_service.update_skills_from_deliverable(
                user=user,
                deliverable=deliverable,
                base_quality=base_quality,
            )

            if demonstrations:
                self.logger.debug(
                    f"Inferred {len(demonstrations)} skills from deliverable {deliverable.id}"
                )

        except Exception as e:
            self.logger.debug(f"Skill evolution trigger failed: {e}")

        try:
            # 2. Goal Tracking: Auto-link deliverable to matching goals
            from core.services.goal_tracking_service import get_goal_tracking_service
            goal_service = get_goal_tracking_service()

            progress = goal_service.auto_link_deliverable(deliverable)

            if progress:
                self.logger.debug(
                    f"Auto-linked deliverable {deliverable.id} to goal {progress.goal_id}"
                )

        except Exception as e:
            self.logger.debug(f"Goal tracking trigger failed: {e}")


# Singleton instance for easy access
_service_instance: Optional[DeliverableEnvelopeService] = None


def get_deliverable_envelope_service() -> DeliverableEnvelopeService:
    """Get or create the singleton DeliverableEnvelopeService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = DeliverableEnvelopeService()
    return _service_instance
