"""
Reference Resolver Service - Session 482

Resolves ambiguous references in conversations like:
- "it", "that", "this" → Last mentioned entity
- "the first one", "the second one" → Items from numbered lists
- "do it again" → Repeat last action
- "them", "those" → Plural entity references

Tracks entities across conversation turns to enable contextual follow-ups.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """An entity mentioned in conversation."""
    text: str
    entity_type: str  # 'topic', 'item', 'action', 'result', 'number', 'person'
    position: int  # Order in list if applicable
    source_message: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResolvedReference:
    """Result of resolving a reference."""
    original: str  # The original reference text
    resolved: str  # What it resolves to
    entity: Optional[Entity]  # The entity it refers to
    confidence: float  # 0.0 to 1.0
    resolution_type: str  # 'pronoun', 'ordinal', 'repeat', 'plural'


class ReferenceResolver:
    """
    Resolves ambiguous references in conversation context.

    Features:
    - Extracts entities from conversation history
    - Resolves pronouns (it, that, this)
    - Resolves ordinal references (first one, second one)
    - Tracks actions for "do it again" requests
    - Maintains context across conversation turns
    """

    # Ordinal patterns
    ORDINAL_PATTERNS = [
        (r'\b(the\s+)?first\s+(one|item|option|choice|result|thing)\b', 1),
        (r'\b(the\s+)?second\s+(one|item|option|choice|result|thing)\b', 2),
        (r'\b(the\s+)?third\s+(one|item|option|choice|result|thing)\b', 3),
        (r'\b(the\s+)?fourth\s+(one|item|option|choice|result|thing)\b', 4),
        (r'\b(the\s+)?fifth\s+(one|item|option|choice|result|thing)\b', 5),
        (r'\b(the\s+)?1st\s*(one|item|option|choice|result|thing)?\b', 1),
        (r'\b(the\s+)?2nd\s*(one|item|option|choice|result|thing)?\b', 2),
        (r'\b(the\s+)?3rd\s*(one|item|option|choice|result|thing)?\b', 3),
        (r'\b(the\s+)?4th\s*(one|item|option|choice|result|thing)?\b', 4),
        (r'\b(the\s+)?5th\s*(one|item|option|choice|result|thing)?\b', 5),
        (r'\bnumber\s+(\d+)\b', None),  # "number 2" - extract digit
        (r'\b#(\d+)\b', None),  # "#2" - extract digit
        (r'\boption\s+(\d+)\b', None),  # "option 2" - extract digit
    ]

    # Pronoun patterns that need resolution
    PRONOUN_PATTERNS = [
        r'\b(it)\b',
        r'\b(that)\b',
        r'\b(this)\b',
        r'\b(them)\b',
        r'\b(those)\b',
        r'\b(these)\b',
    ]

    # Action repeat patterns
    REPEAT_PATTERNS = [
        r'\bdo\s+(it|that)\s+again\b',
        r'\brepeat\s+(that|it|the\s+last\s+one)\b',
        r'\bagain\b',
        r'\bone\s+more\s+time\b',
        r'\bsame\s+thing\b',
        r'\banother\s+one\b',
    ]

    # Patterns for extracting numbered lists from assistant responses
    LIST_PATTERNS = [
        r'(?:^|\n)\s*(\d+)\.\s*\*?\*?([^\n]+)',  # "1. Item" or "1. **Item**"
        r'(?:^|\n)\s*[-•]\s*\*?\*?([^\n]+)',  # "- Item" or "• Item"
        r'\*\*(\d+)\.\s*([^*]+)\*\*',  # "**1. Item**"
    ]

    def __init__(self):
        self.entities: List[Entity] = []
        self.last_action: Optional[Dict[str, Any]] = None
        self.numbered_items: List[Entity] = []
        self.last_topic: Optional[Entity] = None

    def extract_entities_from_history(
        self,
        conversation_history: List[Dict[str, str]]
    ) -> List[Entity]:
        """
        Extract entities from conversation history.

        Args:
            conversation_history: List of {role, content} messages

        Returns:
            List of extracted entities
        """
        self.entities = []
        self.numbered_items = []

        for msg in conversation_history:
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            if role == 'assistant':
                # Extract numbered lists from assistant responses
                self._extract_numbered_items(content)
                # Extract topics/subjects from responses
                self._extract_topics(content, role)
            else:
                # Extract entities from user messages
                self._extract_topics(content, role)

        logger.debug(f"📝 Extracted {len(self.entities)} entities, "
                    f"{len(self.numbered_items)} numbered items")

        return self.entities

    def _extract_numbered_items(self, content: str) -> None:
        """Extract numbered list items from content."""
        # Pattern for numbered lists like "1. Item" or "1. **Item**"
        numbered_pattern = r'(?:^|\n)\s*(\d+)\.\s*\*?\*?([^\n*]+)'
        matches = re.findall(numbered_pattern, content, re.MULTILINE)

        for num, item_text in matches:
            position = int(num)
            # Clean up the item text
            clean_text = re.sub(r'\*+', '', item_text).strip()
            clean_text = clean_text.split(' - ')[0].strip()  # Take first part before dash
            clean_text = clean_text.split(':')[0].strip()  # Take first part before colon

            if clean_text and len(clean_text) > 2:
                entity = Entity(
                    text=clean_text,
                    entity_type='item',
                    position=position,
                    source_message=content[:100],
                    metadata={'full_text': item_text.strip()}
                )
                self.numbered_items.append(entity)
                self.entities.append(entity)

        # Also extract bullet points
        bullet_pattern = r'(?:^|\n)\s*[-•]\s*\*?\*?([^\n*]+)'
        bullet_matches = re.findall(bullet_pattern, content, re.MULTILINE)

        for i, item_text in enumerate(bullet_matches, 1):
            clean_text = re.sub(r'\*+', '', item_text).strip()
            clean_text = clean_text.split(' - ')[0].strip()

            if clean_text and len(clean_text) > 2:
                entity = Entity(
                    text=clean_text,
                    entity_type='item',
                    position=i,
                    source_message=content[:100],
                    metadata={'bullet': True}
                )
                # Only add if we don't already have numbered items
                if not self.numbered_items:
                    self.numbered_items.append(entity)
                    self.entities.append(entity)

    def _extract_topics(self, content: str, role: str) -> None:
        """Extract main topics/subjects from content."""
        # Extract capitalized phrases (likely proper nouns/topics)
        topic_pattern = r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b'
        topics = re.findall(topic_pattern, content)

        # Filter common words
        common_words = {'The', 'This', 'That', 'Here', 'There', 'What', 'How',
                       'When', 'Where', 'Why', 'Who', 'I', 'You', 'We', 'They',
                       'It', 'Is', 'Are', 'Was', 'Were', 'Be', 'Been', 'Being',
                       'Have', 'Has', 'Had', 'Do', 'Does', 'Did', 'Will', 'Would',
                       'Could', 'Should', 'May', 'Might', 'Must', 'Can'}

        for topic in topics:
            if topic not in common_words and len(topic) > 2:
                entity = Entity(
                    text=topic,
                    entity_type='topic',
                    position=0,
                    source_message=content[:100],
                    metadata={'role': role}
                )
                self.entities.append(entity)
                self.last_topic = entity

    def resolve_references(
        self,
        message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Tuple[str, List[ResolvedReference]]:
        """
        Resolve all references in a message.

        Args:
            message: The user's current message
            conversation_history: Previous messages for context

        Returns:
            Tuple of (resolved_message, list of resolutions made)
        """
        # Extract entities from history
        self.extract_entities_from_history(conversation_history)

        resolutions = []
        resolved_message = message

        # 1. Check for ordinal references ("the first one", "the second one")
        ordinal_resolution = self._resolve_ordinal(message)
        if ordinal_resolution:
            resolutions.append(ordinal_resolution)
            resolved_message = self._apply_resolution(
                resolved_message, ordinal_resolution
            )

        # 2. Check for repeat patterns ("do it again")
        repeat_resolution = self._resolve_repeat(message)
        if repeat_resolution:
            resolutions.append(repeat_resolution)

        # 3. Check for pronoun references ("it", "that")
        pronoun_resolutions = self._resolve_pronouns(message)
        resolutions.extend(pronoun_resolutions)

        if resolutions:
            logger.info(f"🔍 Resolved {len(resolutions)} references in message")
            for r in resolutions:
                logger.debug(f"   '{r.original}' → '{r.resolved}' ({r.resolution_type})")

        return resolved_message, resolutions

    def _resolve_ordinal(self, message: str) -> Optional[ResolvedReference]:
        """Resolve ordinal references like 'the first one'."""
        message_lower = message.lower()

        for pattern, position in self.ORDINAL_PATTERNS:
            match = re.search(pattern, message_lower)
            if match:
                # If position is None, extract from the match
                if position is None:
                    try:
                        position = int(match.group(1))
                    except (IndexError, ValueError):
                        continue

                # Find the item at this position
                matching_items = [e for e in self.numbered_items if e.position == position]
                if matching_items:
                    entity = matching_items[0]
                    return ResolvedReference(
                        original=match.group(0),
                        resolved=entity.text,
                        entity=entity,
                        confidence=0.9,
                        resolution_type='ordinal'
                    )

        return None

    def _resolve_repeat(self, message: str) -> Optional[ResolvedReference]:
        """Resolve repeat patterns like 'do it again'."""
        message_lower = message.lower()

        for pattern in self.REPEAT_PATTERNS:
            if re.search(pattern, message_lower):
                if self.last_action:
                    return ResolvedReference(
                        original=message,
                        resolved=f"Repeat: {self.last_action.get('description', 'last action')}",
                        entity=None,
                        confidence=0.8,
                        resolution_type='repeat'
                    )
                break

        return None

    def _resolve_pronouns(self, message: str) -> List[ResolvedReference]:
        """Resolve pronoun references like 'it', 'that'."""
        resolutions = []
        message_lower = message.lower()

        # Only resolve if there's context
        if not self.entities and not self.numbered_items:
            return resolutions

        # Get the most recent topic or item
        recent_entity = None
        if self.last_topic:
            recent_entity = self.last_topic
        elif self.numbered_items:
            recent_entity = self.numbered_items[0]
        elif self.entities:
            recent_entity = self.entities[-1]

        if recent_entity:
            for pattern in self.PRONOUN_PATTERNS:
                match = re.search(pattern, message_lower)
                if match:
                    pronoun = match.group(1)
                    # Only resolve if pronoun seems to refer to something specific
                    if self._is_referential_context(message, pronoun):
                        resolutions.append(ResolvedReference(
                            original=pronoun,
                            resolved=recent_entity.text,
                            entity=recent_entity,
                            confidence=0.7,
                            resolution_type='pronoun'
                        ))

        return resolutions

    def _is_referential_context(self, message: str, pronoun: str) -> bool:
        """Check if the pronoun is used in a referential context."""
        # Phrases that indicate the pronoun refers to something specific
        referential_phrases = [
            f'tell me more about {pronoun}',
            f'what about {pronoun}',
            f'explain {pronoun}',
            f'describe {pronoun}',
            f'research {pronoun}',
            f'show me {pronoun}',
            f'create {pronoun}',
            f'using {pronoun}',
            f'with {pronoun}',
            f'for {pronoun}',
        ]

        message_lower = message.lower()
        return any(phrase in message_lower for phrase in referential_phrases)

    def _apply_resolution(
        self,
        message: str,
        resolution: ResolvedReference
    ) -> str:
        """Apply a resolution to the message for clarity."""
        # For ordinal resolutions, add context
        if resolution.resolution_type == 'ordinal':
            # Append clarification
            return f"{message} [Referring to: {resolution.resolved}]"
        return message

    def record_action(self, action: Dict[str, Any]) -> None:
        """Record an action for potential repeat requests."""
        self.last_action = {
            **action,
            'timestamp': datetime.now()
        }
        logger.debug(f"📝 Recorded action: {action.get('description', 'unknown')}")

    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of current context for debugging."""
        return {
            'total_entities': len(self.entities),
            'numbered_items': len(self.numbered_items),
            'last_topic': self.last_topic.text if self.last_topic else None,
            'has_last_action': self.last_action is not None,
            'items': [
                {'position': e.position, 'text': e.text}
                for e in self.numbered_items[:5]
            ]
        }


# Singleton instance per user session
_resolvers: Dict[str, ReferenceResolver] = {}


def get_reference_resolver(session_id: str = 'default') -> ReferenceResolver:
    """Get or create a reference resolver for a session."""
    if session_id not in _resolvers:
        _resolvers[session_id] = ReferenceResolver()
    return _resolvers[session_id]


def clear_resolver(session_id: str = 'default') -> None:
    """Clear a session's resolver."""
    if session_id in _resolvers:
        del _resolvers[session_id]
