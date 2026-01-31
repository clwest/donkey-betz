"""
Conversation to Initiative Pipeline
====================================

Session 884: Connects conversations to trackable Initiatives with stage progression.

When a conversation produces valuable content, this pipeline:
1. Creates an Initiative to track the work
2. Creates the Deliverable and links it to Stage 1
3. Dispatches tasks linked to specific stages
4. Handles task completion → stage advancement
5. Feeds outputs back to enrich the original deliverable

This closes the loop between THINKING (conversations) and DOING (tracked work).

Flow:
    Conversation
        ↓
    Initiative created (5 stages)
        ↓
    Deliverable → linked to Initiative
        ↓
    Tasks dispatched → linked to stages
        ↓
    Task completes → stage updated
        ↓
    Stage complete → advance to next
        ↓
    All stages done → Initiative complete

Usage:
    from core.services.conversation_initiative_pipeline import process_conversation_to_initiative

    result = process_conversation_to_initiative(
        conversation_id="uuid",
        messages=messages,
        decision_summary=summary,
        participants=['AgentA', 'AgentB'],
        topic="Customer Personas"
    )
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from django.utils import timezone
from django.utils.text import slugify
from django.db import transaction

logger = logging.getLogger(__name__)


# Stage definitions for different content types
CONTENT_TYPE_STAGES = {
    'strategy': {
        1: {'name': 'Research & Validation', 'tasks': [
            {'agent': 'ResearchAgent', 'task_template': 'Validate {topic} with 5 customer interviews or data sources'},
            {'agent': 'MarketIntelligenceAgent', 'task_template': 'Audit 3 competitors for gaps in {topic} space'},
        ]},
        2: {'name': 'Strategy Refinement', 'tasks': [
            {'agent': 'ContentStrategyAgent', 'task_template': 'Refine {topic} based on validation findings'},
        ]},
        3: {'name': 'Content Creation', 'tasks': [
            {'agent': 'ContentWriterAgent', 'task_template': 'Create content implementing {topic}'},
        ]},
        4: {'name': 'Review & Polish', 'tasks': [
            {'agent': 'EditorAgent', 'task_template': 'Review and polish {topic} content for quality'},
        ]},
        5: {'name': 'Publication', 'tasks': [
            {'agent': 'ContentDistributionAgent', 'task_template': 'Prepare {topic} for distribution'},
        ]},
    },
    'plan': {
        1: {'name': 'Requirements Gathering', 'tasks': [
            {'agent': 'ResearchAgent', 'task_template': 'Identify dependencies and blockers for {topic}'},
        ]},
        2: {'name': 'Planning', 'tasks': [
            {'agent': 'ProjectManagerAgent', 'task_template': 'Break down {topic} into weekly milestones'},
        ]},
        3: {'name': 'Execution Setup', 'tasks': [
            {'agent': 'FullStackDeveloperAgent', 'task_template': 'Set up technical foundation for {topic}'},
        ]},
        4: {'name': 'Implementation', 'tasks': [
            {'agent': 'FullStackDeveloperAgent', 'task_template': 'Implement core features for {topic}'},
        ]},
        5: {'name': 'Review & Launch', 'tasks': [
            {'agent': 'CodeReviewAgent', 'task_template': 'Final review of {topic} implementation'},
        ]},
    },
    'analysis': {
        1: {'name': 'Data Collection', 'tasks': [
            {'agent': 'ResearchAgent', 'task_template': 'Expand {topic} with additional data sources'},
        ]},
        2: {'name': 'Analysis', 'tasks': [
            {'agent': 'TrendAnalysisAgent', 'task_template': 'Perform deep analysis on {topic} data'},
        ]},
        3: {'name': 'Synthesis', 'tasks': [
            {'agent': 'ContentWriterAgent', 'task_template': 'Synthesize {topic} findings into executive summary'},
        ]},
        4: {'name': 'Review', 'tasks': [
            {'agent': 'EditorAgent', 'task_template': 'Review {topic} analysis for accuracy'},
        ]},
        5: {'name': 'Distribution', 'tasks': [
            {'agent': 'ContentDistributionAgent', 'task_template': 'Share {topic} analysis with stakeholders'},
        ]},
    },
    'research': {
        1: {'name': 'Initial Research', 'tasks': [
            {'agent': 'ResearchAgent', 'task_template': 'Validate {topic} findings with additional sources'},
        ]},
        2: {'name': 'Deep Dive', 'tasks': [
            {'agent': 'ResearchAgent', 'task_template': 'Conduct deep dive on key aspects of {topic}'},
        ]},
        3: {'name': 'Documentation', 'tasks': [
            {'agent': 'ContentWriterAgent', 'task_template': 'Create shareable brief from {topic} research'},
        ]},
        4: {'name': 'Review', 'tasks': [
            {'agent': 'EditorAgent', 'task_template': 'Review {topic} documentation for quality'},
        ]},
        5: {'name': 'Publication', 'tasks': [
            {'agent': 'ContentDistributionAgent', 'task_template': 'Publish {topic} research findings'},
        ]},
    },
    'document': {
        1: {'name': 'Draft', 'tasks': [
            {'agent': 'ContentWriterAgent', 'task_template': 'Complete initial draft of {topic}'},
        ]},
        2: {'name': 'Enhancement', 'tasks': [
            {'agent': 'EditorAgent', 'task_template': 'Enhance {topic} with additional detail'},
        ]},
        3: {'name': 'Review', 'tasks': [
            {'agent': 'EditorAgent', 'task_template': 'Review {topic} for quality and accuracy'},
        ]},
        4: {'name': 'Polish', 'tasks': [
            {'agent': 'EditorAgent', 'task_template': 'Final polish of {topic}'},
        ]},
        5: {'name': 'Publication', 'tasks': [
            {'agent': 'ContentDistributionAgent', 'task_template': 'Prepare {topic} for publication'},
        ]},
    },
}


@dataclass
class PipelineResult:
    """Result of processing a conversation through the initiative pipeline."""
    conversation_id: str
    initiative_id: Optional[str] = None
    initiative_name: Optional[str] = None
    deliverable_id: Optional[str] = None
    stages_created: int = 0
    tasks_dispatched: int = 0
    task_ids: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'conversation_id': self.conversation_id,
            'initiative_id': self.initiative_id,
            'initiative_name': self.initiative_name,
            'deliverable_id': self.deliverable_id,
            'stages_created': self.stages_created,
            'tasks_dispatched': self.tasks_dispatched,
            'task_ids': self.task_ids,
            'errors': self.errors,
        }


class ConversationInitiativePipeline:
    """
    Transforms conversations into trackable Initiatives with connected outputs.
    """

    def __init__(self):
        self.min_content_length = 500

    def detect_content_type(self, text: str) -> Optional[str]:
        """Detect the type of content for stage template selection."""
        from core.services.conversation_deliverable_extractor import DELIVERABLE_PATTERNS

        text_lower = text.lower()
        scores = {}

        for content_type, config in DELIVERABLE_PATTERNS.items():
            keywords = config['keywords']
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > 0:
                score = min(1.0, matches / (len(keywords) * 0.5))
                scores[content_type] = score

        if not scores:
            return None

        return max(scores.keys(), key=lambda k: scores[k])

    def extract_best_content(self, messages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Extract the best content from conversation messages."""
        best_content = None
        best_length = 0

        for idx in range(len(messages) - 1, -1, -1):
            msg = messages[idx]
            content = msg.get('content', '')

            if len(content) > best_length and len(content) >= self.min_content_length:
                best_length = len(content)
                best_content = {
                    'content': content,
                    'agent': msg.get('role', 'unknown'),
                    'idx': idx,
                }

        return best_content

    @transaction.atomic
    def process(
        self,
        conversation_id: str,
        messages: List[Dict[str, Any]],
        decision_summary: Optional[Dict[str, Any]],
        participants: List[str],
        topic: str,
        user_id: Optional[int] = None,
        bypass_circuit_breaker: bool = False
    ) -> PipelineResult:
        """
        Process a conversation into a full Initiative pipeline.

        Args:
            conversation_id: ID of the source conversation
            messages: Conversation messages
            decision_summary: Decision summary from conversation
            participants: Participating agents
            topic: Conversation topic
            user_id: Optional user ID
            bypass_circuit_breaker: Skip backlog check (for manual/admin use)

        Returns:
            PipelineResult with Initiative, Deliverable, and task info
        """
        result = PipelineResult(conversation_id=conversation_id)

        # Session 884: Circuit breaker check - pause creation when backlog is too high
        from core.services.initiative_circuit_breaker import can_create_initiative, get_backlog_status
        if not can_create_initiative(bypass_check=bypass_circuit_breaker):
            status = get_backlog_status()
            result.errors.append(
                f"Initiative creation paused: {status['pending_count']} pending "
                f"(threshold: {status['threshold']}). Set INITIATIVE_CREATION_PAUSED=false to resume."
            )
            logger.warning(f"[pipeline] Circuit breaker blocked initiative creation for: {topic[:50]}")
            return result

        # Extract best content
        extracted = self.extract_best_content(messages)
        if not extracted:
            result.errors.append("No substantial content found in conversation")
            return result

        # Detect content type
        content_type = self.detect_content_type(extracted['content'])
        if not content_type:
            content_type = 'document'  # Default

        try:
            # Import models
            from core.models_document_registry import Initiative, InitiativeStage
            from core.models_deliverables import Deliverable

            # 1. Create Initiative
            initiative_name = f"{topic[:100]}" if topic else f"Initiative-{conversation_id[:8]}"

            # Ensure unique name
            base_name = initiative_name
            counter = 1
            while Initiative.objects.filter(name=initiative_name).exists():
                initiative_name = f"{base_name} ({counter})"
                counter += 1

            initiative = Initiative.objects.create(
                name=initiative_name,
                description=f"Auto-created from conversation about: {topic}",
                status='ACTIVE',
                current_stage=1,
                created_by='ConversationInitiativePipeline',
                parent_topic=topic[:200] if topic else '',
            )

            result.initiative_id = str(initiative.id)
            result.initiative_name = initiative_name

            logger.info(f"📋 Created Initiative: {initiative_name} (id={initiative.id})")

            # 2. Create Deliverable linked to Initiative
            deliverable_title = f"{content_type.title()}: {topic[:100]}" if topic else f"{content_type.title()} Output"
            base_slug = slugify(deliverable_title)[:200]
            slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"

            deliverable = Deliverable.objects.create(
                title=deliverable_title,
                slug=slug,
                deliverable_type=content_type,
                category=content_type.title(),
                tags=[content_type, 'conversation-generated', 'auto-pipeline'],
                content=extracted['content'],
                content_format='markdown',
                agent_name=participants[0] if participants else 'ConversationOrchestrator',
                quality_score=0.7,
                confidence_score=0.7,
                initiative=initiative,  # Link to Initiative!
                parent_object_type='conversation',
                parent_object_id=uuid.UUID(conversation_id) if conversation_id else None,
                metadata={
                    'source': 'conversation_initiative_pipeline',
                    'session': '884',
                    'participants': participants,
                    'topic': topic,
                    'content_type': content_type,
                    'pipeline_stage': 1,
                }
            )

            result.deliverable_id = str(deliverable.id)
            logger.info(f"📦 Created Deliverable: {deliverable_title} (id={deliverable.id})")

            # 3. Create InitiativeStages
            stage_config = CONTENT_TYPE_STAGES.get(content_type, CONTENT_TYPE_STAGES['document'])

            for stage_num in range(1, 6):
                stage_info = stage_config.get(stage_num, {'name': f'Stage {stage_num}', 'tasks': []})

                # Stage 1 starts as DRAFT since we have content
                status = 'DRAFT' if stage_num == 1 else 'PENDING'

                stage = InitiativeStage.objects.create(
                    initiative=initiative,
                    stage=stage_num,
                    status=status,
                    # Note: document is FK to SelfBlog, we store deliverable link in notes
                    notes=f"Auto-created: {stage_info['name']}\nDeliverable: {deliverable.id}" if stage_num == 1 else f"Auto-created: {stage_info['name']}",
                )

                result.stages_created += 1

            logger.info(f"📊 Created {result.stages_created} stages for Initiative")

            # 4. Dispatch Stage 1 tasks
            stage_1_config = stage_config.get(1, {'tasks': []})
            task_ids = self._dispatch_stage_tasks(
                initiative=initiative,
                stage_num=1,
                tasks=stage_1_config.get('tasks', []),
                topic=topic,
                conversation_id=conversation_id,
                deliverable_id=str(deliverable.id),
            )

            result.tasks_dispatched = len(task_ids)
            result.task_ids = task_ids

            logger.info(
                f"🚀 Pipeline complete: Initiative={initiative_name}, "
                f"Deliverable={deliverable.id}, Tasks={len(task_ids)}"
            )

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            result.errors.append(str(e))

        return result

    def _dispatch_stage_tasks(
        self,
        initiative,
        stage_num: int,
        tasks: List[Dict[str, str]],
        topic: str,
        conversation_id: str,
        deliverable_id: str,
    ) -> List[str]:
        """Dispatch tasks for a specific stage."""
        from core.tasks import execute_initiative_stage_task

        task_ids = []

        for task_config in tasks:
            agent_name = task_config['agent']
            task_template = task_config['task_template']
            task_description = task_template.format(topic=topic)

            try:
                # Queue the task with initiative context
                async_result = execute_initiative_stage_task.delay(
                    initiative_id=str(initiative.id),
                    stage_num=stage_num,
                    agent_name=agent_name,
                    task=task_description,
                    context={
                        'source': 'conversation_initiative_pipeline',
                        'conversation_id': conversation_id,
                        'deliverable_id': deliverable_id,
                        'topic': topic,
                    }
                )

                task_ids.append(async_result.id)
                logger.info(f"📤 Dispatched: {agent_name} for Stage {stage_num} (task_id={async_result.id})")

            except Exception as e:
                logger.error(f"Failed to dispatch task to {agent_name}: {e}")

        return task_ids


def handle_stage_task_completion(
    initiative_id: str,
    stage_num: int,
    agent_name: str,
    task_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Handle completion of a stage task.

    Called when an agent finishes a task linked to an InitiativeStage.
    Updates the stage, checks for completion, and advances if ready.

    Args:
        initiative_id: ID of the Initiative
        stage_num: Stage number (1-5)
        agent_name: Agent that completed the task
        task_result: Result from the agent execution

    Returns:
        Dict with stage update info
    """
    from core.models_document_registry import Initiative, InitiativeStage
    from core.models_deliverables import Deliverable

    result = {
        'initiative_id': initiative_id,
        'stage_num': stage_num,
        'agent_name': agent_name,
        'stage_updated': False,
        'stage_advanced': False,
        'new_stage': None,
        'deliverable_enriched': False,
    }

    try:
        initiative = Initiative.objects.get(id=initiative_id)
        stage = InitiativeStage.objects.get(initiative=initiative, stage=stage_num)

        # Update stage notes with task result
        task_output = task_result.get('content', '')[:2000] if task_result.get('success') else ''
        stage.notes = f"{stage.notes}\n\n--- {agent_name} Output ---\n{task_output}"

        # If task succeeded, mark stage as IN_REVIEW
        if task_result.get('success'):
            if stage.status in ['PENDING', 'DRAFT']:
                stage.status = 'IN_REVIEW'
                result['stage_updated'] = True

            # Enrich the Initiative's Deliverable with task output
            if task_output:
                try:
                    # Find Deliverable linked to this Initiative
                    deliverable = Deliverable.objects.filter(initiative=initiative).first()
                    if deliverable:
                        enrichment = f"\n\n---\n## {agent_name} Findings (Stage {stage_num})\n{task_output}"
                        deliverable.content = deliverable.content + enrichment
                        deliverable.save()
                        result['deliverable_enriched'] = True
                        logger.info(f"📝 Enriched Deliverable {deliverable.id} with {agent_name} output")
                except Exception as e:
                    logger.warning(f"Could not enrich deliverable: {e}")

        stage.save()

        # Check if we should auto-advance (simplified: advance after first successful task)
        # In production, you'd want more sophisticated logic (all tasks complete, human approval, etc.)
        if result['stage_updated'] and stage_num < 5:
            # Auto-approve current stage
            stage.status = 'APPROVED'
            stage.approved_at = timezone.now()
            stage.save()

            # Session 884: Ensure all PRIOR stages are also APPROVED (backfill fix)
            # This fixes the issue where initiatives jump ahead without completing earlier stages
            for prior_stage_num in range(1, stage_num):
                prior_stage, created = InitiativeStage.objects.get_or_create(
                    initiative=initiative,
                    stage=prior_stage_num,
                    defaults={
                        'status': 'APPROVED',
                        'approved_at': timezone.now(),
                        'notes': f'Auto-backfilled when Stage {stage_num} completed',
                    }
                )
                if not created and prior_stage.status != 'APPROVED':
                    prior_stage.status = 'APPROVED'
                    prior_stage.approved_at = timezone.now()
                    prior_stage.notes = f"{prior_stage.notes}\n\n[Backfilled: approved when Stage {stage_num} completed]"
                    prior_stage.save()
                    logger.info(f"📋 Backfilled Stage {prior_stage_num} as APPROVED")

            # Advance initiative to next stage
            initiative.current_stage = stage_num + 1
            initiative.save()

            result['stage_advanced'] = True
            result['new_stage'] = stage_num + 1

            logger.info(f"⏭️ Advanced Initiative {initiative.name} to Stage {stage_num + 1}")

            # Dispatch next stage tasks
            _dispatch_next_stage_tasks(initiative, stage_num + 1)

    except Exception as e:
        logger.error(f"Error handling stage task completion: {e}")
        result['error'] = str(e)

    return result


def _dispatch_next_stage_tasks(initiative, stage_num: int):
    """Dispatch tasks for the next stage."""
    from core.tasks import execute_initiative_stage_task

    # Get topic from initiative
    topic = initiative.parent_topic or initiative.name

    # Determine content type from deliverable
    content_type = 'document'
    try:
        from core.models_deliverables import Deliverable
        deliverable = Deliverable.objects.filter(initiative=initiative).first()
        if deliverable:
            content_type = deliverable.deliverable_type
    except Exception:
        pass

    # Get stage config
    stage_config = CONTENT_TYPE_STAGES.get(content_type, CONTENT_TYPE_STAGES['document'])
    stage_info = stage_config.get(stage_num, {'tasks': []})

    for task_config in stage_info.get('tasks', []):
        agent_name = task_config['agent']
        task_template = task_config['task_template']
        task_description = task_template.format(topic=topic)

        try:
            execute_initiative_stage_task.delay(
                initiative_id=str(initiative.id),
                stage_num=stage_num,
                agent_name=agent_name,
                task=task_description,
                context={
                    'source': 'auto_stage_advancement',
                    'topic': topic,
                }
            )
            logger.info(f"📤 Dispatched Stage {stage_num} task: {agent_name}")
        except Exception as e:
            logger.error(f"Failed to dispatch Stage {stage_num} task: {e}")


# Convenience function
def process_conversation_to_initiative(
    conversation_id: str,
    messages: List[Dict[str, Any]],
    decision_summary: Optional[Dict[str, Any]],
    participants: List[str],
    topic: str,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Process a conversation into a full Initiative pipeline.

    This is the main entry point. Call this at the end of a conversation
    to create an Initiative with linked Deliverable and dispatched tasks.
    """
    pipeline = ConversationInitiativePipeline()
    result = pipeline.process(
        conversation_id=conversation_id,
        messages=messages,
        decision_summary=decision_summary,
        participants=participants,
        topic=topic,
        user_id=user_id,
    )
    return result.to_dict()


__all__ = [
    'ConversationInitiativePipeline',
    'process_conversation_to_initiative',
    'handle_stage_task_completion',
    'PipelineResult',
    'CONTENT_TYPE_STAGES',
]
