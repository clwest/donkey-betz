"""
Conversation Lane Router — Session 1100
========================================

Routes PA conversations into 4 lanes with distinct behavior policies:

  DBZ       — Product/ops: full tool access, full memory
  PLATFORM  — Infrastructure: full tool access, full memory
  BIZ       — Launch/revenue: full tool access, full memory
  LOW_RET   — Low-retention: no tools, no memory unless explicitly requested

Lane detection:
  1. Explicit prefix tag in message: [DBZ], [PLATFORM], [BIZ], [LOW-RET]
  2. Persisted lane in conversation metadata (sticky per conversation)
  3. Default: DBZ (full access)

Low-Retention Mode:
  - Tool calls blocked unless user says "use tools", "search for", "create task", etc.
  - Memory writes blocked unless user says "remember this", "save this", etc.
  - Conversation still stored in ChatConversation (for history) but with
    metadata['lane'] = 'low_ret' so downstream systems can skip indexing.
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# ── Lane definitions ──────────────────────────────────────────────────────

LANES = {
    'dbz': 'DBZ',
    'platform': 'PLATFORM',
    'biz': 'BIZ',
    'low_ret': 'LOW_RET',
}

DEFAULT_LANE = 'dbz'

# ── Lane detection from message prefix ────────────────────────────────────

_TAG_PATTERN = re.compile(
    r'^\s*\[(DBZ|PLATFORM|BIZ|LOW[- ]?RET(?:ENTION)?)\]\s*',
    re.IGNORECASE,
)

# Map tag text → lane key
_TAG_TO_LANE = {
    'dbz': 'dbz',
    'platform': 'platform',
    'biz': 'biz',
    'low-ret': 'low_ret',
    'low ret': 'low_ret',
    'low-retention': 'low_ret',
    'low retention': 'low_ret',
    'lowret': 'low_ret',
    'lowretention': 'low_ret',
}

# ── Low-retention override phrases ────────────────────────────────────────
# These phrases in a low_ret conversation allow tool/memory access.

_TOOL_OVERRIDE_PHRASES = [
    'use tools', 'search for', 'look up', 'find me', 'create task',
    'run agent', 'check status', 'query', 'fetch', 'pull up',
    'show me data', 'get the', 'what are the stats',
]

_MEMORY_OVERRIDE_PHRASES = [
    'remember this', 'save this', 'store this', 'keep this',
    'note this', 'don\'t forget', 'make a note',
]


@dataclass
class LanePolicy:
    """Policy for a conversation lane."""
    lane: str
    display_name: str
    tools_allowed: bool = True
    memory_allowed: bool = True
    tool_override: bool = False   # True if user explicitly requested tools in low_ret
    memory_override: bool = False  # True if user explicitly requested memory in low_ret


def detect_lane_from_message(message: str) -> tuple[Optional[str], str]:
    """
    Detect lane from message prefix tag.

    Returns:
        (lane_key, cleaned_message) — lane_key is None if no tag found.
        cleaned_message has the tag stripped.
    """
    match = _TAG_PATTERN.match(message)
    if not match:
        return None, message

    tag_text = match.group(1).lower().replace(' ', ' ')
    lane = _TAG_TO_LANE.get(tag_text)
    if not lane:
        # Try normalized
        normalized = tag_text.replace('-', '').replace(' ', '')
        lane = _TAG_TO_LANE.get(normalized)

    cleaned = message[match.end():]
    return lane, cleaned


def get_conversation_lane(conversation_id: str) -> Optional[str]:
    """Load persisted lane from the most recent ChatConversation metadata."""
    if not conversation_id:
        return None
    try:
        from core.models import ChatConversation
        row = (
            ChatConversation.objects
            .filter(conversation_id=conversation_id)
            .order_by('-created_at')
            .values_list('metadata', flat=True)
            .first()
        )
        if row and isinstance(row, dict):
            return row.get('lane')
    except Exception as _e:
        logger.warning(
            "conv_router.get_conversation_lane: swallowed (%s: %s) — degraded",
            type(_e).__name__, _e,
        )
    return None


def resolve_lane(message: str, conversation_id: str = '') -> tuple[str, str, str]:
    """
    Resolve the active lane for this message.

    Returns:
        (lane_key, cleaned_message, lane_source)
        lane_source: 'tag', 'persisted', or 'default'
    """
    # 1. Check for explicit tag
    tag_lane, cleaned = detect_lane_from_message(message)
    if tag_lane:
        logger.info(f"[LaneRouter] Lane '{tag_lane}' from message tag")
        return tag_lane, cleaned, 'tag'

    # 2. Check persisted lane
    persisted = get_conversation_lane(conversation_id)
    if persisted and persisted in LANES:
        return persisted, message, 'persisted'

    # 3. Default
    return DEFAULT_LANE, message, 'default'


def get_lane_policy(lane: str, message: str) -> LanePolicy:
    """Build the policy for a given lane + message combination."""
    display = LANES.get(lane, 'DBZ')

    if lane != 'low_ret':
        return LanePolicy(lane=lane, display_name=display)

    # Low-retention: check for override phrases
    msg_lower = message.lower()
    tool_override = any(phrase in msg_lower for phrase in _TOOL_OVERRIDE_PHRASES)
    memory_override = any(phrase in msg_lower for phrase in _MEMORY_OVERRIDE_PHRASES)

    return LanePolicy(
        lane=lane,
        display_name=display,
        tools_allowed=tool_override,
        memory_allowed=memory_override,
        tool_override=tool_override,
        memory_override=memory_override,
    )


def get_lane_system_prompt(policy: LanePolicy) -> str:
    """Return system prompt addendum for the active lane."""
    if policy.lane == 'low_ret':
        parts = [
            "",
            "CONVERSATION LANE: LOW-RETENTION MODE",
            "- This is a casual, low-retention conversation.",
            "- Do NOT call any tools unless the user explicitly asks (e.g. 'search for', 'use tools', 'look up').",
            "- Do NOT save memories or create tasks unless the user explicitly asks (e.g. 'remember this', 'save this').",
            "- Keep responses conversational and lightweight.",
            "- If the user needs platform data, suggest they switch lanes: 'Switch to [DBZ] for full access.'",
        ]
        if policy.tool_override:
            parts.append("- USER OVERRIDE: Tools are allowed for this message (user explicitly requested).")
        if policy.memory_override:
            parts.append("- USER OVERRIDE: Memory writes are allowed for this message (user explicitly requested).")
        return "\n".join(parts)

    lane_descriptions = {
        'dbz': "CONVERSATION LANE: DBZ (Product & Ops)\n- Full tool and memory access. Focus on product development, agent operations, and system health.",
        'platform': "CONVERSATION LANE: PLATFORM (Infrastructure)\n- Full tool and memory access. Focus on infrastructure, deployments, and technical architecture.",
        'biz': "CONVERSATION LANE: BIZ (Business & Revenue)\n- Full tool and memory access. Focus on launch strategy, revenue, growth, and business operations.",
    }
    return "\n\n" + lane_descriptions.get(policy.lane, '')
