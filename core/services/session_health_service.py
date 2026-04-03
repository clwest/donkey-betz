"""
Session Health Service — Context-Aware Session Management
==========================================================

Detects when a conversation has become too long, drifted off-topic,
or switched contexts. Provides a freshness score and recommendations
so the UI can suggest starting a fresh session.

Users shouldn't have to think about context management — the system
handles it proactively.

Signals used:
- Turn count (more turns = more noise)
- Topic drift (semantic distance between early vs recent messages)
- Role/intent changes (engineering → legal → marketing)
- Task completions (pipeline finished, deliverable created)
- Token estimate (proxy for context window pressure)

Usage:
    from core.services.session_health_service import get_session_health
    health = get_session_health(conversation_id, user_id)
    # Returns: {score, recommendation, signals, auto_summary, starter_prompt}
"""

import logging
from datetime import timedelta
from typing import Dict, Any, Optional

from django.utils import timezone

logger = logging.getLogger(__name__)

# Thresholds (tunable)
TURN_THRESHOLD_SOFT = 20       # Suggest fresh session
TURN_THRESHOLD_HARD = 40       # Strongly recommend
TOKEN_ESTIMATE_PER_TURN = 500  # Rough estimate
TOKEN_THRESHOLD_SOFT = 15000
TOKEN_THRESHOLD_HARD = 30000
TOPIC_DRIFT_THRESHOLD = 0.4    # 0-1 scale, higher = more drift
HOURS_STALE_THRESHOLD = 4      # Session idle > 4h = suggest fresh


def get_session_health(conversation_id: str, user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Analyze a conversation's health and return freshness score + recommendations.

    Returns:
        {
            'score': 0-100 (100 = perfectly fresh, 0 = severely degraded),
            'recommendation': 'continue' | 'suggest_fresh' | 'strongly_recommend_fresh',
            'signals': {turn_count, estimated_tokens, topic_count, hours_since_start, ...},
            'reasons': ['High turn count (35 messages)', ...],
            'auto_summary': '3-sentence summary of conversation',
            'starter_prompt': 'Pre-filled prompt for new session',
        }
    """
    from core.models import ChatConversation

    # Fetch conversation messages
    messages = ChatConversation.objects.filter(
        conversation_id=conversation_id,
    ).order_by('created_at')

    if not messages.exists():
        return _fresh_session()

    msg_list = list(messages.values(
        'user_message', 'assistant_response', 'created_at',
        'agents_used', 'metadata',
    ))

    # Calculate signals
    signals = _calculate_signals(msg_list)

    # Calculate composite score (100 = fresh, 0 = degraded)
    score = _calculate_score(signals)

    # Determine recommendation
    if score >= 70:
        recommendation = 'continue'
    elif score >= 40:
        recommendation = 'suggest_fresh'
    else:
        recommendation = 'strongly_recommend_fresh'

    # Build reasons list
    reasons = _build_reasons(signals)

    # Generate auto-summary and starter prompt
    auto_summary = _generate_auto_summary(msg_list)
    starter_prompt = _generate_starter_prompt(msg_list, signals)

    return {
        'conversation_id': conversation_id,
        'score': score,
        'recommendation': recommendation,
        'signals': signals,
        'reasons': reasons,
        'auto_summary': auto_summary,
        'starter_prompt': starter_prompt,
    }


def _fresh_session():
    """Return a perfectly fresh session health."""
    return {
        'score': 100,
        'recommendation': 'continue',
        'signals': {},
        'reasons': [],
        'auto_summary': '',
        'starter_prompt': '',
    }


def _calculate_signals(messages: list) -> Dict[str, Any]:
    """Calculate all health signals from conversation messages."""
    turn_count = len(messages)
    estimated_tokens = turn_count * TOKEN_ESTIMATE_PER_TURN

    # Time signals
    first_msg = messages[0]['created_at']
    last_msg = messages[-1]['created_at']
    hours_since_start = (timezone.now() - first_msg).total_seconds() / 3600
    hours_since_last = (timezone.now() - last_msg).total_seconds() / 3600
    duration_hours = (last_msg - first_msg).total_seconds() / 3600

    # Topic detection — extract unique topics from messages
    topics = set()
    tool_names = set()
    for msg in messages:
        # Extract topics from user messages (simple keyword approach)
        user_msg = (msg.get('user_message') or '')[:200].lower()
        for keyword in ['workspace', 'pipeline', 'agent', 'newsletter', 'deploy',
                        'fix', 'bug', 'feature', 'test', 'review', 'deliverable',
                        'spider', 'research', 'content', 'legal', 'patent']:
            if keyword in user_msg:
                topics.add(keyword)

        # Track tools/agents used
        agents = msg.get('agents_used') or []
        if isinstance(agents, list):
            tool_names.update(agents)

        # Check metadata for structured info
        meta = msg.get('metadata') or {}
        if isinstance(meta, dict):
            if meta.get('structured_type'):
                topics.add(meta['structured_type'])

    # Task completion signals
    task_completions = sum(
        1 for msg in messages
        if msg.get('metadata') and isinstance(msg['metadata'], dict)
        and msg['metadata'].get('structured_type') in ('pipeline_complete', 'deliverable_created', 'task_done')
    )

    return {
        'turn_count': turn_count,
        'estimated_tokens': estimated_tokens,
        'hours_since_start': round(hours_since_start, 1),
        'hours_since_last_message': round(hours_since_last, 1),
        'duration_hours': round(duration_hours, 1),
        'topic_count': len(topics),
        'topics': sorted(topics),
        'unique_agents_used': len(tool_names),
        'task_completions': task_completions,
    }


def _calculate_score(signals: Dict[str, Any]) -> int:
    """Calculate composite freshness score (100 = fresh, 0 = degraded)."""
    score = 100

    # Turn count penalty
    turns = signals.get('turn_count', 0)
    if turns > TURN_THRESHOLD_HARD:
        score -= 40
    elif turns > TURN_THRESHOLD_SOFT:
        score -= 20
    elif turns > 10:
        score -= 5

    # Token pressure penalty
    tokens = signals.get('estimated_tokens', 0)
    if tokens > TOKEN_THRESHOLD_HARD:
        score -= 30
    elif tokens > TOKEN_THRESHOLD_SOFT:
        score -= 15

    # Topic sprawl penalty
    topics = signals.get('topic_count', 0)
    if topics > 6:
        score -= 20
    elif topics > 4:
        score -= 10

    # Stale conversation penalty
    hours_idle = signals.get('hours_since_last_message', 0)
    if hours_idle > HOURS_STALE_THRESHOLD:
        score -= 15

    # Long-running session penalty
    duration = signals.get('duration_hours', 0)
    if duration > 6:
        score -= 10

    return max(0, min(100, score))


def _build_reasons(signals: Dict[str, Any]) -> list:
    """Build human-readable list of reasons for the score."""
    reasons = []
    turns = signals.get('turn_count', 0)
    tokens = signals.get('estimated_tokens', 0)
    topics = signals.get('topic_count', 0)
    hours_idle = signals.get('hours_since_last_message', 0)

    if turns > TURN_THRESHOLD_HARD:
        reasons.append(f'Very long conversation ({turns} messages)')
    elif turns > TURN_THRESHOLD_SOFT:
        reasons.append(f'Long conversation ({turns} messages)')

    if tokens > TOKEN_THRESHOLD_HARD:
        reasons.append(f'High context pressure (~{tokens:,} tokens)')
    elif tokens > TOKEN_THRESHOLD_SOFT:
        reasons.append(f'Growing context ({tokens:,} estimated tokens)')

    if topics > 4:
        reasons.append(f'Multiple topics covered ({topics} detected: {", ".join(signals.get("topics", [])[:5])})')

    if hours_idle > HOURS_STALE_THRESHOLD:
        reasons.append(f'Session idle for {hours_idle:.0f} hours')

    return reasons


def _generate_auto_summary(messages: list) -> str:
    """Generate a brief summary of the conversation."""
    if not messages:
        return ''

    # Collect first and last few user messages for summary
    user_msgs = [m.get('user_message', '') for m in messages if m.get('user_message')]

    if not user_msgs:
        return ''

    first = user_msgs[0][:100] if user_msgs else ''
    recent = user_msgs[-1][:100] if len(user_msgs) > 1 else ''
    total = len(user_msgs)

    summary = f"Conversation with {total} exchanges. "
    if first:
        summary += f"Started with: \"{first}...\" "
    if recent and recent != first:
        summary += f"Most recently: \"{recent}...\""

    return summary.strip()


def _generate_starter_prompt(messages: list, signals: Dict[str, Any]) -> str:
    """Generate a starter prompt for a new session."""
    topics = signals.get('topics', [])

    # Get the most recent user message as context
    recent_msgs = [m.get('user_message', '') for m in messages[-3:] if m.get('user_message')]
    recent_context = '; '.join(msg[:80] for msg in recent_msgs)

    prompt_parts = ['Continuing from a previous session.']

    if topics:
        prompt_parts.append(f"Topics covered: {', '.join(topics[:5])}.")

    if recent_context:
        prompt_parts.append(f"Recent context: {recent_context}")

    prompt_parts.append("Pick up where we left off.")

    return ' '.join(prompt_parts)
