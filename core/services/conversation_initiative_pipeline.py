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
import re
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
            # Session 1040: Changed from ThinkingAgent to ContentWriterAgent
            # ThinkingAgent returns system diagnostics instead of reviewing content
            {'agent': 'ContentWriterAgent', 'task_template': 'Review and polish {topic} content for quality'},
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
            # Session 1040: Changed from ThinkingAgent to ContentWriterAgent
            # ThinkingAgent returns system diagnostics instead of reviewing content
            {'agent': 'ContentWriterAgent', 'task_template': 'Review {topic} analysis for accuracy'},
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
            # Session 1040: Changed from ThinkingAgent to ContentWriterAgent
            # ThinkingAgent returns system diagnostics instead of reviewing content
            {'agent': 'ContentWriterAgent', 'task_template': 'Review {topic} documentation for quality'},
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
            # Session 924: Changed from EditorAgent (requires blog_id/content) to ContentWriterAgent
            {'agent': 'ContentWriterAgent', 'task_template': 'Enhance {topic} with additional detail'},
        ]},
        3: {'name': 'Review', 'tasks': [
            # Session 1040: Changed from ThinkingAgent to ContentWriterAgent
            # ThinkingAgent returns system diagnostics instead of reviewing content
            {'agent': 'ContentWriterAgent', 'task_template': 'Review {topic} for quality and accuracy'},
        ]},
        4: {'name': 'Polish', 'tasks': [
            # Session 924: Changed from EditorAgent to ContentWriterAgent for polish tasks
            {'agent': 'ContentWriterAgent', 'task_template': 'Final polish of {topic}'},
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


_BRACKET_PREFIX_RE = re.compile(r'^(\[(?:Conversation|HiveMind|Learned|Synthesis)\]\s*)+')


def strip_bracket_prefixes(text: str) -> str:
    """Strip accumulated bracket prefixes like [Conversation] [Conversation]."""
    return _BRACKET_PREFIX_RE.sub('', text).strip()


def is_valid_topic(topic: str) -> bool:
    """
    Session 911: Validate that a topic is suitable for research tasks.

    Rejects topics that look like action items or task descriptions rather than
    actual topics that can be researched.

    Args:
        topic: The topic string to validate

    Returns:
        True if topic is valid for research, False otherwise
    """
    if not topic or len(topic) < 5:
        return False

    topic_lower = topic.lower()

    # Action verbs that indicate this is a task, not a topic
    action_verbs = [
        'validate', 'export', 'create', 'build', 'implement', 'deploy',
        'configure', 'setup', 'set up', 'install', 'update', 'fix',
        'run', 'execute', 'trigger', 'call', 'invoke', 'process',
        'generate', 'compute', 'calculate', 'extract', 'transform',
        'must call', 'should call', 'need to', 'must use',
    ]

    # Check if topic starts with an action verb (strong signal it's a task)
    for verb in action_verbs:
        if topic_lower.startswith(verb):
            logger.debug(f"[Session 911] Topic rejected - starts with action verb '{verb}': {topic[:50]}")
            return False

    # Check for task-like patterns
    task_patterns = [
        'with 5 customer',  # Template artifact
        'knowledge base',  # Internal system reference
        'confidence scores',  # Internal metric
        'persona profiles',  # Internal data structure
        '; export',  # Chained actions
        '; create',
        '; build',
        'you must',
        'important:',
    ]

    for pattern in task_patterns:
        if pattern in topic_lower:
            logger.debug(f"[Session 911] Topic rejected - contains task pattern '{pattern}': {topic[:50]}")
            return False

    # Topic looks valid
    return True


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

    # Session 994: Exploratory / low-signal topics that should NOT spawn initiatives
    EXPLORE_PATTERNS = [
        'explore', 'exploring', 'brainstorm', 'what if', 'just thinking',
        'trending', 'trends', 'catch me up', 'what\'s new', 'what\'s going on',
        'show me', 'tell me about', 'how does', 'explain', 'describe',
        'recommend', 'suggest', 'any ideas', 'overview', 'summary',
    ]

    # Session 1042: Content-review patterns that generate busywork initiatives
    # These come from PA conversations about existing blog content — the system
    # creates "revise this blog" initiatives which clog the pipeline.
    CONTENT_REVIEW_PATTERNS = [
        'revise ', 'review ', 'revisit ', 'reassess ',
        'hold publication', 'assemble ', 'enhance ',
        'investor guidance', 'investor briefs', 'investor insights',
        'key insights for', 'actionable insights',
        'navigating ', 'enhancing ',
    ]

    # Action verbs that indicate an initiative-worthy objective
    ACTION_VERBS = [
        'build', 'create', 'implement', 'deploy', 'launch', 'design',
        'develop', 'integrate', 'automate', 'optimize', 'fix', 'repair',
        'migrate', 'refactor', 'test', 'validate', 'ship', 'deliver',
        'establish', 'configure', 'set up', 'install', 'write', 'draft',
    ]

    def _quality_gate(
        self,
        topic: str,
        messages: List[Dict[str, Any]],
        decision_summary: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Session 994: Pre-creation quality gate to prevent initiative spam.
        Session 1042: Added content-review/revision rejection.

        Checks:
        1. Topic is not purely exploratory (trends, brainstorm, overview)
        1b. Topic is not a content-review/revision pattern
        2. Decision summary contains an actionable objective
        3. Conversation has sufficient substance

        Returns:
            {'pass': bool, 'reason': str}
        """
        topic_lower = (topic or '').lower()

        # 1. Reject exploratory topics (lowered threshold from 2 to 1)
        explore_matches = sum(1 for p in self.EXPLORE_PATTERNS if p in topic_lower)
        if explore_matches >= 1:
            return {'pass': False, 'reason': f'Exploratory topic (matched: {[p for p in self.EXPLORE_PATTERNS if p in topic_lower]})'}

        # 1b. Session 1042: Reject content-review/revision topics
        # PA conversations about blog quality/revision should not become initiatives
        review_matches = [p for p in self.CONTENT_REVIEW_PATTERNS if p in topic_lower]
        if review_matches:
            return {'pass': False, 'reason': f'Content review/revision topic (matched: {review_matches})'}

        # 2. Check decision summary for actionable content
        if decision_summary:
            summary_text = ''
            if isinstance(decision_summary, dict):
                summary_text = str(decision_summary.get('synthesis', '')) + ' ' + str(decision_summary.get('suggested_feature', ''))
            elif isinstance(decision_summary, str):
                summary_text = decision_summary
            summary_lower = summary_text.lower()

            # Must contain at least one action verb
            has_action = any(verb in summary_lower for verb in self.ACTION_VERBS)
            if not has_action and len(summary_text) > 50:
                return {'pass': False, 'reason': 'No actionable objective in decision summary'}

        # 3. Check conversation substance (total content length)
        total_content = sum(len(m.get('content', '')) for m in messages)
        if total_content < 1000:
            return {'pass': False, 'reason': f'Insufficient substance ({total_content} chars, need 1000+)'}

        # 4. Single-pattern explore check on topic alone
        if any(topic_lower.startswith(p) for p in ['exploring ', 'what is ', 'tell me ', 'show me ']):
            return {'pass': False, 'reason': f'Topic starts with exploratory pattern'}

        return {'pass': True, 'reason': 'Passed quality gate'}

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

        # Session 994: Quality gate — reject low-signal conversations before creating initiatives
        gate_result = self._quality_gate(topic, messages, decision_summary)
        if not gate_result['pass']:
            result.errors.append(f"Quality gate rejected: {gate_result['reason']}")
            logger.info(
                f"[pipeline] Quality gate REJECTED initiative for topic '{topic[:50]}': "
                f"{gate_result['reason']}"
            )
            return result

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
            from core.services.initiative_title_generator import generate_initiative_title

            # 1. Create Initiative with smart title generation (Session 905)
            # Use content and topic to generate a clean, concise title
            content_preview = extracted['content'][:2000] if extracted else ""
            initiative_name = generate_initiative_title(
                content=content_preview,
                topic_hint=topic,
                max_length=80,
                use_llm=True
            )

            # Session 954: Validate generated title is not junk
            from core.services.decision_extractor import _is_valid_initiative_name
            if not _is_valid_initiative_name(initiative_name):
                logger.warning(f"Session 954: Generated invalid initiative name: '{initiative_name[:50]}', using topic fallback")
                # Try topic as fallback
                if topic and _is_valid_initiative_name(topic[:80]):
                    initiative_name = topic[:80]
                else:
                    result.errors.append(f"Could not generate valid initiative name from content")
                    return result

            # Dedup check: reuse existing similar initiative instead of creating duplicate
            from core.services.initiative_circuit_breaker import find_similar_initiative, can_create_initiative
            existing = find_similar_initiative(initiative_name)
            if existing:
                logger.info(f"[pipeline] Found similar initiative '{existing.name}' — reusing instead of creating duplicate")
                initiative = existing
                result.initiative_id = str(initiative.id)
                result.initiative_name = initiative.name
            elif not can_create_initiative():
                # Session 1020: Circuit breaker check (was missing — bypassed the breaker)
                logger.warning(f"[Session 1020] Circuit breaker blocked conversation initiative: {initiative_name[:60]}")
                result.errors.append("Initiative creation blocked by circuit breaker")
                return result
            else:
                # Ensure unique name
                base_name = initiative_name
                counter = 1
                while Initiative.objects.filter(name=initiative_name).exists():
                    initiative_name = f"{base_name} ({counter})"
                    counter += 1

                # Session 908/909/910: Get workspace for initiative
                # Session 910: Use centralized platform_config for configurable workspace
                workspace = None
                try:
                    from core.services.platform_config import get_primary_workspace
                    workspace = get_primary_workspace()

                except Exception as ws_error:
                    logger.warning(f"Could not get workspace for initiative: {ws_error}")

                initiative = Initiative.objects.create(
                    name=initiative_name,
                    description=f"Auto-created from conversation about: {strip_bracket_prefixes(topic)}",
                    status='TRIAGE',  # Session 994: Auto-created → TRIAGE, not ACTIVE
                    current_stage=1,
                    created_by='ConversationInitiativePipeline',
                    parent_topic=strip_bracket_prefixes(topic)[:200] if topic else '',
                    target_workspace=workspace,  # Session 908: Link to workspace
                )

                # Session 1003: Auto-set founder intent so auto-progression works
                initiative.set_founder_intent(
                    execution_speed='balanced',
                    risk_tolerance='balanced',
                    set_by='system_auto'
                )

                # Session 996: Auto-assign owner
                from core.services.initiative_integration_service import InitiativeIntegrationService
                InitiativeIntegrationService()._auto_assign_owner(initiative)

                # Session 1016: Auto-link to signal cluster
                try:
                    from core.services.initiative_signal_linker import auto_link_initiative_signals
                    auto_link_initiative_signals(initiative)
                except Exception as e:
                    logger.debug(f"Signal auto-link skipped: {e}")

                result.initiative_id = str(initiative.id)
                result.initiative_name = initiative_name

                logger.info(f"Created Initiative: {initiative_name} (id={initiative.id})")

            # 2. Create Deliverable linked to Initiative
            deliverable_title = f"{content_type.title()}: {topic[:100]}" if topic else f"{content_type.title()} Output"
            base_slug = slugify(deliverable_title)[:200]
            slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"

            from core.services.deliverable_workspace_resolver import resolve_workspace
            ws, ws_saved = resolve_workspace(initiative=initiative)

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
                initiative=initiative,
                workspace=ws,
                is_saved=ws_saved,
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

            # Session 915: Create Stage 1 document from deliverable content
            stage_1_doc = None
            try:
                from core.models_unified_system import SelfBlog
                stage_1_doc = SelfBlog.objects.create(
                    title=f"{initiative.name} - Stage 1: Research Brief",
                    intro=extracted['content'][:500] if extracted.get('content') else '',
                    full_text=extracted.get('content', ''),
                    category='research_brief',
                    content_type='internal',
                    status='draft',
                    initiative=initiative,
                )
                logger.info(f"[Session 915] Created Stage 1 document: {stage_1_doc.id}")
            except Exception as doc_err:
                logger.warning(f"[Session 915] Could not create Stage 1 document: {doc_err}")

            for stage_num in range(1, 6):
                stage_info = stage_config.get(stage_num, {'name': f'Stage {stage_num}', 'tasks': []})

                # Stage 1 starts as DRAFT since we have content
                status = 'DRAFT' if stage_num == 1 else 'PENDING'

                stage = InitiativeStage.objects.create(
                    initiative=initiative,
                    stage=stage_num,
                    status=status,
                    # Session 915: Attach document to Stage 1
                    document=stage_1_doc if stage_num == 1 else None,
                    notes=f"Auto-created: {stage_info['name']}\nDeliverable: {deliverable.id}" if stage_num == 1 else f"Auto-created: {stage_info['name']}",
                )

                # Session 915: Link Stage 1 back to the document
                if stage_num == 1 and stage_1_doc:
                    stage_1_doc.initiative_stage = stage
                    stage_1_doc.save(update_fields=['initiative_stage'])

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

        # Session 911: Validate topic before dispatching tasks
        if not is_valid_topic(topic):
            logger.warning(
                f"[Session 911] Skipping task dispatch - invalid topic: {topic[:80]}... "
                f"(initiative={initiative.id}, stage={stage_num})"
            )
            return []

        task_ids = []

        for task_config in tasks:
            agent_name = task_config['agent']
            task_template = task_config['task_template']
            task_description = task_template.format(topic=strip_bracket_prefixes(topic))

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

            # Session 1020: Create stage document if missing (fixes Stage 2+ stall)
            # Stage 1 gets a document at initialization, but Stage 2+ never did.
            # Without a document, the hard invariant at line 719 prevents auto-approval.
            if not stage.document and task_output:
                try:
                    from core.models_unified_system import SelfBlog
                    # Determine content type for stage name lookup
                    content_type = 'document'
                    try:
                        deliv = Deliverable.objects.filter(initiative=initiative).first()
                        if deliv and deliv.metadata and deliv.metadata.get('content_type'):
                            content_type = deliv.metadata['content_type']
                    except Exception:
                        pass
                    stage_config = CONTENT_TYPE_STAGES.get(content_type, CONTENT_TYPE_STAGES['document'])
                    stage_info = stage_config.get(stage_num, {})
                    stage_label = stage_info.get('name', f'Stage {stage_num}')

                    stage_doc = SelfBlog.objects.create(
                        title=f"{initiative.name} - Stage {stage_num}: {stage_label}",
                        intro=task_output[:500],
                        full_text=task_output,
                        category='initiative_stage',
                        content_type='internal',
                        status='draft',
                        initiative=initiative,
                        initiative_stage=stage,
                    )
                    stage.document = stage_doc
                    logger.info(f"[Session 1020] Created Stage {stage_num} document: {stage_doc.id}")
                except Exception as doc_err:
                    logger.warning(f"[Session 1020] Could not create Stage {stage_num} document: {doc_err}")

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

        # Session 994: Record activity whenever stage work completes
        try:
            initiative.update_activity()
        except Exception:
            pass  # Don't let tracking block stage processing

        # Check if we should auto-advance (simplified: advance after first successful task)
        # In production, you'd want more sophisticated logic (all tasks complete, human approval, etc.)
        if result['stage_updated'] and stage_num < 5:
            # Session 916: Use approve() method which enforces document requirement
            # Only approve if stage has a document (hard invariant)
            # Session 943: Only advance if approval succeeds (hard invariant)
            approval_succeeded = False
            if stage.document:
                try:
                    stage.approve(
                        approved_by='conversation_pipeline',
                        notes='Auto-approved via conversation initiative pipeline',
                        checks_passed={
                            'has_document': True,
                            'stage_updated': True,
                        }
                    )
                    approval_succeeded = True
                except Exception as approve_err:
                    logger.warning(f"⚠️ Approval failed for Stage {stage_num}: {approve_err}")
            else:
                # Cannot approve without document - log warning
                logger.warning(
                    f"⚠️ Cannot auto-approve Stage {stage_num} for {initiative.name[:30]} - no document attached"
                )

            # Session 916: DON'T auto-backfill prior stages without documents
            # This was the root cause of data corruption! Instead, ensure prior stages
            # exist but leave them in DRAFT status for proper document generation.
            for prior_stage_num in range(1, stage_num):
                prior_stage, created = InitiativeStage.objects.get_or_create(
                    initiative=initiative,
                    stage=prior_stage_num,
                    defaults={
                        'status': 'DRAFT',  # Session 916: DRAFT not APPROVED - needs document
                        'notes': f'Created when Stage {stage_num} was processed',
                    }
                )
                if created:
                    # Session 916: Log creation in DRAFT status
                    from core.models_document_registry import StageTransitionLog
                    StageTransitionLog.log_transition(
                        stage=prior_stage,
                        from_status='CREATED',
                        to_status='DRAFT',
                        triggered_by='conversation_pipeline',
                        trigger_type='system',
                        notes=f'Created in DRAFT when Stage {stage_num} processed - needs document before approval'
                    )
                    logger.info(f"📋 Created Stage {prior_stage_num} in DRAFT (needs document)")

            # Session 943: HARD INVARIANT - only advance if approval succeeded
            # This prevents initiatives from skipping to Stage 5 without proper approvals
            if approval_succeeded:
                initiative.current_stage = stage_num + 1
                initiative.save()

                result['stage_advanced'] = True
                result['new_stage'] = stage_num + 1

                logger.info(f"⏭️ Advanced Initiative {initiative.name} to Stage {stage_num + 1}")

                # Dispatch next stage tasks
                _dispatch_next_stage_tasks(initiative, stage_num + 1)
            else:
                logger.info(
                    f"⏸️ Initiative {initiative.name[:30]} NOT advanced - Stage {stage_num} not approved"
                )

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
    except Exception as e:
        logger.warning(f"Deliverable lookup failed for initiative: {e}")

    # Get stage config
    stage_config = CONTENT_TYPE_STAGES.get(content_type, CONTENT_TYPE_STAGES['document'])
    stage_info = stage_config.get(stage_num, {'tasks': []})

    for task_config in stage_info.get('tasks', []):
        agent_name = task_config['agent']
        task_template = task_config['task_template']
        task_description = task_template.format(topic=strip_bracket_prefixes(topic))

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
