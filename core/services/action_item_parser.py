"""
Action Item Parser Service - Session 902

Extracts trackable action items from conversation conclusions.

Parses text like:
    === DecisionSummary ===
    Next Steps:
    - ResearchAgent: Define canonical persona schema (Week 0-1)
    - ContentWriterAgent: Draft methodology guide (Week 1-3)

Into structured InitiativeActionItem records.
"""

import re
import logging
from datetime import timedelta
from typing import List, Dict, Optional, Tuple
from django.utils import timezone

logger = logging.getLogger(__name__)


class ActionItemParser:
    """
    Parses conversation conclusions to extract actionable items.

    Supports multiple formats:
    - "AgentName: Task description (Timeline)"
    - "- Task description [assigned to AgentName]"
    - "1. Task description"
    - Bullet points with agent mentions
    """

    # Patterns for extracting action items
    AGENT_TASK_PATTERN = re.compile(
        r'^[\-\*•]\s*(?:(\w+Agent):\s*)?(.+?)(?:\s*\(([^)]+)\))?$',
        re.MULTILINE
    )

    NUMBERED_TASK_PATTERN = re.compile(
        r'^\d+\.\s*(?:(\w+Agent):\s*)?(.+?)(?:\s*\(([^)]+)\))?$',
        re.MULTILINE
    )

    # Timeline patterns
    WEEK_PATTERN = re.compile(r'[Ww]eek\s*(\d+)(?:\s*-\s*(\d+))?')
    DAY_PATTERN = re.compile(r'(\d+)\s*days?')
    IMMEDIATE_PATTERN = re.compile(r'immediate|asap|now|urgent', re.IGNORECASE)

    # Section markers
    SECTION_MARKERS = [
        'next steps',
        'action items',
        'follow-up',
        'to do',
        'tasks',
        'deliverables',
        'recommendations',
        'proposed actions',
    ]

    def __init__(self):
        self.base_date = timezone.now().date()

    def parse_conclusion(self, conclusion_text: str) -> List[Dict]:
        """
        Parse a conversation conclusion and extract action items.

        Args:
            conclusion_text: The full conclusion text from a conversation

        Returns:
            List of dicts with action item data
        """
        if not conclusion_text:
            return []

        action_items = []

        # Find the relevant section(s) containing action items
        sections = self._find_action_sections(conclusion_text)

        for section_text in sections:
            items = self._extract_items_from_section(section_text)
            action_items.extend(items)

        # Deduplicate by title
        seen_titles = set()
        unique_items = []
        for item in action_items:
            title_key = item['title'].lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_items.append(item)

        # Assign order
        for i, item in enumerate(unique_items):
            item['order'] = i

        return unique_items

    def _find_action_sections(self, text: str) -> List[str]:
        """Find sections that contain action items."""
        sections = []
        text_lower = text.lower()

        # Look for section headers
        for marker in self.SECTION_MARKERS:
            # Find the marker
            marker_pos = text_lower.find(marker)
            if marker_pos == -1:
                continue

            # Find the start of the section (after the header line)
            section_start = text.find('\n', marker_pos)
            if section_start == -1:
                section_start = marker_pos + len(marker)
            else:
                section_start += 1

            # Find the end of the section (next header or end of text)
            section_end = len(text)

            # Look for next section header
            for next_marker in ['===', '---', '##', '\n\n\n']:
                next_pos = text.find(next_marker, section_start + 10)
                if next_pos != -1 and next_pos < section_end:
                    section_end = next_pos

            section_text = text[section_start:section_end].strip()
            if section_text:
                sections.append(section_text)

        # If no sections found, try to extract from the whole text
        if not sections:
            # Look for bullet points or numbered lists
            if re.search(r'^[\-\*•]\s+', text, re.MULTILINE) or re.search(r'^\d+\.\s+', text, re.MULTILINE):
                sections.append(text)

        return sections

    def _extract_items_from_section(self, section_text: str) -> List[Dict]:
        """Extract action items from a section of text."""
        items = []

        # Try bullet points first
        for match in self.AGENT_TASK_PATTERN.finditer(section_text):
            agent = match.group(1) or ''
            task = match.group(2).strip()
            timeline = match.group(3) or ''

            if task and len(task) > 5 and not self._is_junk_title(task):
                items.append(self._create_item_dict(task, agent, timeline, match.group(0)))

        # Try numbered lists
        for match in self.NUMBERED_TASK_PATTERN.finditer(section_text):
            agent = match.group(1) or ''
            task = match.group(2).strip()
            timeline = match.group(3) or ''

            if task and len(task) > 5 and not self._is_junk_title(task):
                items.append(self._create_item_dict(task, agent, timeline, match.group(0)))

        # Also look for inline agent mentions
        lines = section_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip if already captured by patterns above
            if any(line in item.get('source_text', '') for item in items):
                continue

            # Look for "AgentName should/will/needs to" patterns
            agent_action_match = re.search(
                r'(\w+Agent)\s+(?:should|will|needs to|must|can)\s+(.+)',
                line,
                re.IGNORECASE
            )
            if agent_action_match:
                agent = agent_action_match.group(1)
                task = agent_action_match.group(2).strip()
                if task and len(task) > 5 and not self._is_junk_title(task):
                    items.append(self._create_item_dict(task, agent, '', line))

        return items

    # Session 1076: Junk patterns that produce noise action items
    _JUNK_TITLE_RE = re.compile(
        r'^(?:'
        r'.{0,15}:\s*$'       # Short titles ending with colon ("Nightly:", "Fields:")
        r'|[A-Z][a-z\- ]{0,12}:$'  # Single-word labels ending with colon
        r')',
        re.MULTILINE,
    )

    @staticmethod
    def _is_junk_title(title: str) -> bool:
        """Return True if title is a section heading / label, not a real action item."""
        t = title.strip()
        if not t:
            return True
        # Ends with colon (heading/label, not actionable)
        if t.endswith(':'):
            return True
        # Extremely short (< 10 chars after stripping bullets)
        stripped = re.sub(r'^[\-\*•\d.)\s]+', '', t)
        if len(stripped) < 10:
            return True
        # Session 1102: Catch markdown heading patterns that leaked from stage docs
        # e.g. "*Ongoing Evaluation**: Establish a timeline..."
        if re.match(r'^\*+[A-Z].*\*\*:', t):
            return True
        # Bare markdown bold headings e.g. "Scale Plan**", "Recommendations**"
        if t.endswith('**') and len(re.sub(r'\*+', '', t).strip()) < 30:
            return True
        # Generic template headings (not actionable engineering work)
        _TEMPLATE_PHRASES = [
            'ongoing evaluation', 'training and support', 'broader rollout',
            'monitoring and alerts', 'slo targets', 'infrastructure improvements',
            'documentation updates', 'stakeholder communication',
            'risk mitigation', 'change management',
        ]
        t_lower = t.lower()
        if any(t_lower.startswith(f'*{phrase}') or t_lower.startswith(phrase)
               for phrase in _TEMPLATE_PHRASES):
            return True
        return False

    def _create_item_dict(self, title: str, agent: str, timeline: str, source_text: str) -> Dict:
        """Create a standardized action item dictionary."""
        # Clean up title
        title = title.strip()
        title = re.sub(r'^[\-\*•]\s*', '', title)
        title = title.rstrip('.')

        # Extract agent from title if not provided
        if not agent:
            agent_in_title = re.match(r'^(\w+Agent):\s*(.+)', title)
            if agent_in_title:
                agent = agent_in_title.group(1)
                title = agent_in_title.group(2)

        # Parse timeline to due date
        due_date = self._parse_timeline_to_date(timeline) if timeline else None

        # Infer priority from keywords
        priority = self._infer_priority(title, timeline)

        return {
            'title': title[:300],  # Truncate to max length
            'assigned_agent': agent,
            'timeline_text': timeline[:50] if timeline else '',
            'due_date': due_date,
            'priority': priority,
            'source_text': source_text[:500] if source_text else '',
        }

    def _parse_timeline_to_date(self, timeline: str) -> Optional['date']:
        """Convert timeline text to a due date."""
        if not timeline:
            return None

        # Check for week ranges
        week_match = self.WEEK_PATTERN.search(timeline)
        if week_match:
            end_week = int(week_match.group(2) or week_match.group(1))
            return self.base_date + timedelta(weeks=end_week)

        # Check for day counts
        day_match = self.DAY_PATTERN.search(timeline)
        if day_match:
            days = int(day_match.group(1))
            return self.base_date + timedelta(days=days)

        # Check for immediate/urgent
        if self.IMMEDIATE_PATTERN.search(timeline):
            return self.base_date + timedelta(days=1)

        return None

    def _infer_priority(self, title: str, timeline: str) -> str:
        """Infer priority from title and timeline keywords."""
        text = f"{title} {timeline}".lower()

        if any(word in text for word in ['critical', 'urgent', 'asap', 'immediate', 'blocker']):
            return 'critical'
        elif any(word in text for word in ['important', 'high priority', 'week 0', 'week 1']):
            return 'high'
        elif any(word in text for word in ['low priority', 'nice to have', 'optional', 'future']):
            return 'low'
        else:
            return 'medium'


def extract_action_items_from_conversation(session_id: str) -> List:
    """
    Extract action items from a HiveMindSession and create InitiativeActionItem records.

    Args:
        session_id: UUID of the HiveMindSession

    Returns:
        List of created InitiativeActionItem instances
    """
    from core.models_unified_system import HiveMindSession
    from core.models_document_registry import Initiative, InitiativeActionItem

    try:
        session = HiveMindSession.objects.get(id=session_id)
    except HiveMindSession.DoesNotExist:
        logger.error(f"Session {session_id} not found")
        return []

    # Get the conclusion text (HiveMindSession uses synthesis_summary)
    conclusion = session.synthesis_summary or session.synthesis or ''
    if not conclusion:
        logger.info(f"Session {session_id} has no synthesis")
        return []

    # Find linked initiative
    initiative = None

    # Try to find via decision -> initiative link
    decisions = session.decisions.all()
    for decision in decisions:
        if hasattr(decision, 'initiative') and decision.initiative:
            initiative = decision.initiative
            break

    # If no initiative found, try to find by topic matching
    if not initiative:
        topic = session.conversation_topic or ''
        if topic:
            initiative = Initiative.objects.filter(name__icontains=topic[:50]).first()

    if not initiative:
        logger.info(f"No initiative found for session {session_id}")
        return []

    # Parse the conclusion
    parser = ActionItemParser()
    items_data = parser.parse_conclusion(conclusion)

    if not items_data:
        logger.info(f"No action items found in session {session_id}")
        return []

    # Create action item records
    created_items = []
    for item_data in items_data:
        # Check if similar item already exists
        existing = InitiativeActionItem.objects.filter(
            initiative=initiative,
            title__iexact=item_data['title'][:300]
        ).exists()

        if existing:
            continue

        action_item = InitiativeActionItem.objects.create(
            initiative=initiative,
            source_conversation=session,
            title=item_data['title'],
            assigned_agent=item_data.get('assigned_agent', ''),
            timeline_text=item_data.get('timeline_text', ''),
            due_date=item_data.get('due_date'),
            priority=item_data.get('priority', 'medium'),
            source_text=item_data.get('source_text', ''),
            order=item_data.get('order', 0),
            created_by='action_item_parser',
        )
        created_items.append(action_item)
        logger.info(f"Created action item: {action_item.title}")

    return created_items


def extract_action_items_from_stage(stage_id: str) -> List:
    """
    Session 1058: Extract action items from an InitiativeStage document
    and create InitiativeActionItem records.

    Called after stage document generation to populate trackable work items
    that must be completed before the stage can auto-approve.

    Args:
        stage_id: UUID of the InitiativeStage

    Returns:
        List of created InitiativeActionItem instances
    """
    from core.models_document_registry import InitiativeStage, InitiativeActionItem

    try:
        stage = InitiativeStage.objects.select_related(
            'initiative', 'document'
        ).get(id=stage_id)
    except InitiativeStage.DoesNotExist:
        logger.error(f"[Session 1058] Stage {stage_id} not found")
        return []

    if not stage.document:
        logger.info(f"[Session 1058] Stage {stage_id} has no document")
        return []

    full_text = stage.document.full_text or ''
    if not full_text:
        logger.info(f"[Session 1058] Stage {stage_id} document has no text")
        return []

    # Parse the document for action items
    parser = ActionItemParser()
    items_data = parser.parse_conclusion(full_text)

    if not items_data:
        logger.info(f"[Session 1058] No action items found in stage {stage_id}")
        return []

    initiative = stage.initiative

    # Create action item records (dedup by title within this initiative)
    created_items = []
    for item_data in items_data:
        existing = InitiativeActionItem.objects.filter(
            initiative=initiative,
            title__iexact=item_data['title'][:300]
        ).exists()

        if existing:
            continue

        action_item = InitiativeActionItem.objects.create(
            initiative=initiative,
            source_stage=stage,
            title=item_data['title'],
            assigned_agent=item_data.get('assigned_agent', ''),
            timeline_text=item_data.get('timeline_text', ''),
            due_date=item_data.get('due_date'),
            priority=item_data.get('priority', 'medium'),
            source_text=item_data.get('source_text', ''),
            order=item_data.get('order', 0),
            created_by='stage_pipeline',
        )
        created_items.append(action_item)
        logger.info(f"[Session 1058] Created action item: {action_item.title}")

    return created_items


def bulk_extract_action_items(limit: int = 100) -> Dict:
    """
    Extract action items from recent conversations that don't have any yet.

    Returns:
        Dict with extraction stats
    """
    from core.models_unified_system import HiveMindSession
    from core.models_document_registry import InitiativeActionItem

    # Find sessions with conclusions that haven't been processed
    processed_session_ids = InitiativeActionItem.objects.values_list(
        'source_conversation_id', flat=True
    ).distinct()

    sessions = HiveMindSession.objects.filter(
        synthesis_summary__isnull=False
    ).exclude(
        synthesis_summary=''
    ).exclude(
        id__in=processed_session_ids
    ).order_by('-created_at')[:limit]

    stats = {
        'sessions_processed': 0,
        'items_created': 0,
        'sessions_with_items': 0,
    }

    for session in sessions:
        items = extract_action_items_from_conversation(str(session.id))
        stats['sessions_processed'] += 1
        if items:
            stats['items_created'] += len(items)
            stats['sessions_with_items'] += 1

    logger.info(f"Bulk extraction complete: {stats}")
    return stats
