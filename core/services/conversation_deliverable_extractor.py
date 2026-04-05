"""
Conversation Deliverable Extractor
==================================

Session 884: Extracts actionable deliverables from agent conversations.

When agents have a productive conversation that produces structured output
(personas, plans, analyses, strategies), this service:

1. Detects deliverable-worthy content in the final synthesis
2. Creates a Deliverable record with the content
3. Generates concrete next steps (not vague "document insights")

This closes the loop between thinking (conversations) and doing (deliverables + tasks).

Usage:
    from core.services.conversation_deliverable_extractor import extract_conversation_deliverables

    result = extract_conversation_deliverables(
        conversation_id="uuid-here",
        messages=conversation_messages,
        decision_summary=decision_summary,
        participants=['AgentA', 'AgentB'],
        topic="Create customer personas"
    )
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

from django.utils import timezone
from django.utils.text import slugify

logger = logging.getLogger(__name__)


# Content patterns that indicate deliverable-worthy output
DELIVERABLE_PATTERNS = {
    'persona': {
        'keywords': ['persona', 'jobs-to-be-done', 'jtbd', 'pain points', 'decision criteria', 'buyer'],
        'type': 'strategy',
        'category': 'Marketing',
        'title_template': 'Customer Personas: {topic}',
    },
    'plan': {
        'keywords': ['next steps', 'timeline', 'phases', 'implementation plan', 'roadmap', 'action plan'],
        'type': 'plan',
        'category': 'Strategy',
        'title_template': 'Action Plan: {topic}',
    },
    'analysis': {
        'keywords': ['analysis', 'findings', 'insights', 'market', 'competitive', 'swot', 'assessment'],
        'type': 'analysis',
        'category': 'Research',
        'title_template': 'Analysis: {topic}',
    },
    'strategy': {
        'keywords': ['strategy', 'approach', 'tactics', 'go-to-market', 'gtm', 'positioning'],
        'type': 'strategy',
        'category': 'Strategy',
        'title_template': 'Strategy: {topic}',
    },
    'research': {
        'keywords': ['research', 'findings', 'data', 'sources', 'evidence', 'study'],
        'type': 'research',
        'category': 'Research',
        'title_template': 'Research Brief: {topic}',
    },
    'content_outline': {
        'keywords': ['content hooks', 'content calendar', 'blog', 'posts', 'article', 'social media'],
        'type': 'document',
        'category': 'Content',
        'title_template': 'Content Plan: {topic}',
    },
    'recommendations': {
        'keywords': ['recommendations', 'suggestions', 'should', 'recommend', 'advised'],
        'type': 'document',
        'category': 'Advisory',
        'title_template': 'Recommendations: {topic}',
    },
}


@dataclass
class ExtractedDeliverable:
    """A deliverable extracted from conversation content."""
    content_type: str
    title: str
    content: str
    category: str
    tags: List[str]
    confidence: float = 0.0
    source_message_idx: int = -1


@dataclass
class ExtractionResult:
    """Result of extracting deliverables from a conversation."""
    conversation_id: str
    deliverables_created: int = 0
    deliverable_ids: List[str] = field(default_factory=list)
    concrete_next_steps: List[Dict[str, str]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'conversation_id': self.conversation_id,
            'deliverables_created': self.deliverables_created,
            'deliverable_ids': self.deliverable_ids,
            'concrete_next_steps': self.concrete_next_steps,
            'errors': self.errors,
        }


class ConversationDeliverableExtractor:
    """
    Extracts deliverables from agent conversations.

    Analyzes conversation output to identify structured content worth
    persisting, then creates Deliverable records and generates
    concrete follow-up tasks.
    """

    def __init__(self):
        self.min_content_length = 500  # Minimum chars for a worthwhile deliverable
        self.min_confidence = 0.6  # Minimum pattern match confidence

    def detect_content_type(self, text: str) -> Tuple[Optional[str], float]:
        """
        Detect the type of deliverable based on content keywords.

        Args:
            text: The content to analyze

        Returns:
            Tuple of (content_type, confidence_score)
        """
        text_lower = text.lower()
        scores = {}

        for content_type, config in DELIVERABLE_PATTERNS.items():
            keywords = config['keywords']
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > 0:
                # Score based on keyword density
                score = min(1.0, matches / (len(keywords) * 0.5))
                scores[content_type] = score

        if not scores:
            return None, 0.0

        # Return highest scoring type
        best_type = max(scores.keys(), key=lambda k: scores[k])
        return best_type, scores[best_type]

    def extract_structured_content(
        self,
        messages: List[Dict[str, Any]],
        decision_summary: Optional[Dict[str, Any]]
    ) -> Optional[ExtractedDeliverable]:
        """
        Extract the best structured content from conversation messages.

        Looks for the synthesis message (usually the last substantive message)
        that contains the actual deliverable content.

        Args:
            messages: List of conversation messages
            decision_summary: The decision summary dict

        Returns:
            ExtractedDeliverable if found, None otherwise
        """
        # Look for synthesis content in messages (usually last few turns)
        best_content = None
        best_confidence = 0.0
        best_idx = -1

        # Check messages in reverse (most recent first)
        for idx in range(len(messages) - 1, -1, -1):
            msg = messages[idx]
            content = msg.get('content', '')

            # Skip short messages
            if len(content) < self.min_content_length:
                continue

            # Detect content type
            content_type, confidence = self.detect_content_type(content)

            if content_type and confidence > best_confidence:
                best_confidence = confidence
                best_content = content
                best_idx = idx
                best_type = content_type

        if not best_content or best_confidence < self.min_confidence:
            return None

        # Get config for this type
        config = DELIVERABLE_PATTERNS[best_type]

        # Extract tags from content
        tags = self._extract_tags(best_content, best_type)

        return ExtractedDeliverable(
            content_type=config['type'],
            title='',  # Will be set by caller with topic
            content=best_content,
            category=config['category'],
            tags=tags,
            confidence=best_confidence,
            source_message_idx=best_idx,
        )

    def _extract_tags(self, content: str, content_type: str) -> List[str]:
        """Extract relevant tags from content."""
        tags = [content_type]

        # Add common business tags if detected
        tag_keywords = {
            'b2b': ['b2b', 'enterprise', 'business'],
            'b2c': ['b2c', 'consumer', 'customer'],
            'saas': ['saas', 'subscription', 'mrr', 'arr'],
            'marketing': ['marketing', 'content', 'campaign'],
            'sales': ['sales', 'revenue', 'conversion'],
            'product': ['product', 'feature', 'roadmap'],
            'technical': ['api', 'integration', 'technical'],
        }

        content_lower = content.lower()
        for tag, keywords in tag_keywords.items():
            if any(kw in content_lower for kw in keywords):
                tags.append(tag)

        return tags[:10]  # Limit to 10 tags

    def generate_concrete_next_steps(
        self,
        extracted: ExtractedDeliverable,
        participants: List[str],
        topic: str
    ) -> List[Dict[str, str]]:
        """
        Generate concrete, actionable next steps based on the deliverable type.

        Instead of vague "document insights", generates specific tasks like:
        - "Run 5 customer interviews to validate personas"
        - "Create 3 content pieces using hooks from personas"
        - "Set up A/B test framework for pricing experiments"

        Args:
            extracted: The extracted deliverable
            participants: Agents that participated
            topic: The conversation topic

        Returns:
            List of concrete next steps with agent assignments
        """
        steps = []
        content_type = extracted.content_type

        # Define concrete actions per content type
        action_templates = {
            'strategy': [
                {'agent': 'ResearchAgent', 'task': f'Validate {topic} strategy with 5 customer interviews'},
                {'agent': 'ContentStrategyAgent', 'task': f'Create content calendar implementing {topic} strategy'},
                {'agent': 'MarketIntelligenceAgent', 'task': f'Audit 3 competitors for gaps in {topic} space'},
            ],
            'plan': [
                {'agent': 'ProjectManagerAgent', 'task': f'Break down {topic} plan into weekly milestones'},
                {'agent': 'ResearchAgent', 'task': f'Identify dependencies and blockers for {topic}'},
            ],
            'analysis': [
                {'agent': 'ResearchAgent', 'task': f'Expand {topic} analysis with primary data sources'},
                {'agent': 'ContentWriterAgent', 'task': f'Draft executive summary of {topic} findings'},
            ],
            'research': [
                {'agent': 'ResearchAgent', 'task': f'Validate {topic} findings with additional sources'},
                {'agent': 'ContentWriterAgent', 'task': f'Create shareable brief from {topic} research'},
            ],
            'document': [
                {'agent': 'ContentWriterAgent', 'task': f'Polish and format {topic} document for publishing'},
                {'agent': 'EditorAgent', 'task': f'Review {topic} document for quality and accuracy'},
            ],
        }

        # Get templates for this type (or default to document)
        templates = action_templates.get(content_type, action_templates['document'])

        for template in templates[:3]:  # Limit to 3 concrete steps
            steps.append({
                'agent': template['agent'],
                'task': template['task'],
                'priority': 'high' if len(steps) == 0 else 'medium',
                'source': 'conversation_deliverable_extractor',
            })

        return steps

    def extract_and_create(
        self,
        conversation_id: str,
        messages: List[Dict[str, Any]],
        decision_summary: Optional[Dict[str, Any]],
        participants: List[str],
        topic: str,
        user_id: Optional[int] = None
    ) -> ExtractionResult:
        """
        Extract deliverables from a conversation and create database records.

        Args:
            conversation_id: ID of the source conversation
            messages: List of conversation messages
            decision_summary: The decision summary dict
            participants: List of participating agent names
            topic: The conversation topic
            user_id: Optional user ID to associate with deliverables

        Returns:
            ExtractionResult with created deliverables and next steps
        """
        result = ExtractionResult(conversation_id=conversation_id)

        # Extract structured content
        extracted = self.extract_structured_content(messages, decision_summary)

        if not extracted:
            logger.info(f"No deliverable-worthy content found in conversation {conversation_id}")
            return result

        try:
            from core.models_deliverables import Deliverable, DeliverableType

            # Generate title
            config = DELIVERABLE_PATTERNS.get(
                extracted.content_type,
                {'title_template': 'Output: {topic}'}
            )
            title = config.get('title_template', 'Output: {topic}').format(
                topic=topic[:100] if topic else 'Untitled'
            )

            # Create unique slug
            base_slug = slugify(title)[:200]
            slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"

            # Resolve workspace for deliverable assignment
            from core.services.deliverable_workspace_resolver import resolve_workspace
            ws, ws_saved = resolve_workspace()

            # Create the Deliverable
            from core.services.deliverable_factory import create_deliverable
            deliverable = create_deliverable(
                title=title,
                content=extracted.content,
                agent_name=participants[0] if participants else 'ConversationOrchestrator',
                category=extracted.category,
                deliverable_type=extracted.content_type,
                tags=extracted.tags,
                content_format='markdown',
                quality_score=extracted.confidence,
                confidence_score=extracted.confidence,
                is_saved=ws_saved,
                metadata={
                    'source': 'conversation_deliverable_extractor',
                    'session': '884',
                    'participants': participants,
                    'topic': topic,
                    'extracted_at': timezone.now().isoformat(),
                    'source_message_idx': extracted.source_message_idx,
                },
                slug=slug,
                workspace=ws,
                parent_object_type='conversation',
                parent_object_id=uuid.UUID(conversation_id) if conversation_id else None,
            )

            result.deliverables_created = 1
            result.deliverable_ids.append(str(deliverable.id))

            logger.info(
                f"Created deliverable '{title}' (id={deliverable.id}) "
                f"from conversation {conversation_id}"
            )

            # Generate concrete next steps
            result.concrete_next_steps = self.generate_concrete_next_steps(
                extracted, participants, topic
            )

        except Exception as e:
            logger.error(f"Failed to create deliverable: {e}")
            result.errors.append(str(e))

        return result


# Singleton instance
_extractor_instance = None


def get_deliverable_extractor() -> ConversationDeliverableExtractor:
    """Get or create the singleton extractor."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = ConversationDeliverableExtractor()
    return _extractor_instance


def extract_conversation_deliverables(
    conversation_id: str,
    messages: List[Dict[str, Any]],
    decision_summary: Optional[Dict[str, Any]],
    participants: List[str],
    topic: str,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Convenience function to extract deliverables from a conversation.

    Args:
        conversation_id: ID of the source conversation
        messages: List of conversation messages
        decision_summary: The decision summary dict
        participants: Participating agents
        topic: Conversation topic
        user_id: Optional user ID

    Returns:
        Dict with extraction results
    """
    extractor = get_deliverable_extractor()
    result = extractor.extract_and_create(
        conversation_id=conversation_id,
        messages=messages,
        decision_summary=decision_summary,
        participants=participants,
        topic=topic,
        user_id=user_id
    )
    return result.to_dict()


__all__ = [
    'ConversationDeliverableExtractor',
    'get_deliverable_extractor',
    'extract_conversation_deliverables',
    'ExtractedDeliverable',
    'ExtractionResult',
]
