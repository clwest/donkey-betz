"""
Session 1077: Focus Mode — guardrails for autonomous agent activity.

Prevents drift by enforcing North Star paths (revenue, content, sports)
and blocking noisy autonomous patterns (competitor loops, open-ended ideation).

Two modes:
  - gentle (default): cap + warn + downrank. Non-North-Star runs still allowed but throttled.
  - strict: block autonomous tasks that don't declare a North Star path.

Config is DB-backed via ComponentStatus (no migration needed) or Redis cache.
PA can read/write config via ops_tool focus_mode action.
"""

import json
import logging
import re
from datetime import timedelta
from typing import Optional

from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

# ── Default config ────────────────────────────────────────────────────────

_DEFAULT_CONFIG = {
    'enabled': True,
    'mode': 'gentle',  # 'gentle' or 'strict'
    'objective_weights': {
        'revenue': 0.40,
        'content': 0.35,
        'sports': 0.25,
    },
    'blocked_topics_autonomous': [
        'competitor comparison',
        'compare donkey betz',
        'donkey betz competitor',
        'competitor analysis',
        'competitive landscape',
        'competitor feature',
        'alternative platform',
    ],
    'max_conversations_per_agent_per_hour': 2,
    'max_total_conversations_per_hour': 8,
    'require_north_star_for_autonomous': False,  # gentle = False, strict = True
}

_CACHE_KEY = 'focus_mode:config'
_CACHE_TTL = 300  # 5 min

# ── Blocked topic patterns (compiled once) ────────────────────────────────

_BLOCKED_PATTERNS = None


def _get_blocked_patterns(config: dict) -> list:
    """Compile blocked topic strings into regex patterns."""
    topics = config.get('blocked_topics_autonomous', [])
    return [re.compile(re.escape(t), re.IGNORECASE) for t in topics]


# ── Config read/write ─────────────────────────────────────────────────────

def get_config() -> dict:
    """Get Focus Mode config from cache or DB, with defaults."""
    cached = cache.get(_CACHE_KEY)
    if cached:
        try:
            return json.loads(cached) if isinstance(cached, str) else cached
        except (json.JSONDecodeError, TypeError):
            pass

    # Try DB (ComponentStatus as config store — no migration needed)
    try:
        from core.models_heart import ComponentStatus
        cs = ComponentStatus.objects.filter(component='focus_mode_config').first()
        if cs and cs.details:
            config = {**_DEFAULT_CONFIG, **cs.details}
            cache.set(_CACHE_KEY, json.dumps(config), _CACHE_TTL)
            return config
    except Exception:
        pass

    # Return defaults
    cache.set(_CACHE_KEY, json.dumps(_DEFAULT_CONFIG), _CACHE_TTL)
    return _DEFAULT_CONFIG.copy()


def set_config(updates: dict) -> dict:
    """Update Focus Mode config (merge with existing)."""
    config = get_config()
    config.update(updates)

    # Persist to DB
    try:
        from core.models_heart import ComponentStatus
        cs, _ = ComponentStatus.objects.update_or_create(
            component='focus_mode_config',
            defaults={
                'status': 'active' if config.get('enabled') else 'inactive',
                'details': config,
                'last_check': timezone.now(),
            },
        )
    except Exception as e:
        logger.warning(f"[FocusMode] Failed to persist config: {e}")

    cache.set(_CACHE_KEY, json.dumps(config), _CACHE_TTL)
    return config


# ── Gate checks ───────────────────────────────────────────────────────────

def is_topic_blocked(topic: str) -> bool:
    """Check if a conversation topic is blocked by Focus Mode."""
    config = get_config()
    if not config.get('enabled'):
        return False

    patterns = _get_blocked_patterns(config)
    for pat in patterns:
        if pat.search(topic or ''):
            logger.info(f"[FocusMode] BLOCKED topic: '{topic[:80]}' (matched: {pat.pattern})")
            return True
    return False


def check_agent_conversation_cap(agent_name: str) -> dict:
    """Check if an agent has exceeded its hourly conversation cap.

    Returns:
        {'allowed': True/False, 'reason': str, 'count': int, 'limit': int}
    """
    config = get_config()
    if not config.get('enabled'):
        return {'allowed': True, 'reason': 'focus_mode_disabled', 'count': 0, 'limit': 0}

    limit = config.get('max_conversations_per_agent_per_hour', 2)
    one_hour_ago = timezone.now() - timedelta(hours=1)

    try:
        from core.models_unified_system import AgentConversation, Agent
        agent = Agent.objects.filter(name=agent_name).first()
        if not agent:
            return {'allowed': True, 'reason': 'agent_not_found', 'count': 0, 'limit': limit}

        count = AgentConversation.objects.filter(
            initiator=agent,
            started_at__gte=one_hour_ago,
        ).count()

        if count >= limit:
            logger.info(
                f"[FocusMode] CAP reached: {agent_name} has {count}/{limit} "
                f"conversations in last hour"
            )
            return {'allowed': False, 'reason': 'hourly_cap_reached', 'count': count, 'limit': limit}

        return {'allowed': True, 'reason': 'within_limit', 'count': count, 'limit': limit}
    except Exception as e:
        logger.warning(f"[FocusMode] Cap check error: {e}")
        return {'allowed': True, 'reason': 'check_error', 'count': 0, 'limit': limit}


def check_total_conversation_cap() -> dict:
    """Check if total autonomous conversations per hour have hit the cap."""
    config = get_config()
    if not config.get('enabled'):
        return {'allowed': True, 'reason': 'focus_mode_disabled', 'count': 0, 'limit': 0}

    limit = config.get('max_total_conversations_per_hour', 8)
    one_hour_ago = timezone.now() - timedelta(hours=1)

    try:
        from core.models_unified_system import AgentConversation
        # Only count scheduled/autonomous conversations (not user-triggered)
        count = AgentConversation.objects.filter(
            started_at__gte=one_hour_ago,
            trigger_type__in=['scheduled', 'learning_transfer', 'synthesis',
                              'spider_data', 'opportunity', 'anomaly'],
        ).count()

        if count >= limit:
            logger.info(f"[FocusMode] TOTAL CAP reached: {count}/{limit} autonomous conversations in last hour")
            return {'allowed': False, 'reason': 'total_hourly_cap', 'count': count, 'limit': limit}

        return {'allowed': True, 'reason': 'within_limit', 'count': count, 'limit': limit}
    except Exception as e:
        logger.warning(f"[FocusMode] Total cap check error: {e}")
        return {'allowed': True, 'reason': 'check_error', 'count': 0, 'limit': limit}


def check_autonomous_task(agent_name: str, task: str, context: Optional[dict] = None) -> dict:
    """Gate check for autonomous agent task execution.

    Called from execute_agent_task for non-manual runs.

    Returns:
        {'allowed': True/False, 'reason': str}
    """
    config = get_config()
    if not config.get('enabled'):
        return {'allowed': True, 'reason': 'focus_mode_disabled'}

    # Check topic blocks on task description
    if is_topic_blocked(task):
        return {'allowed': False, 'reason': f'blocked_topic_in_task'}

    # In strict mode, check if task declares a North Star path
    if config.get('mode') == 'strict' and config.get('require_north_star_for_autonomous'):
        from core.services.noise_metrics import classify_north_star
        ns = classify_north_star(agent_name, {}, task)
        if ns == 'none':
            logger.info(
                f"[FocusMode] STRICT block: {agent_name} task has no North Star path: "
                f"'{task[:60]}'"
            )
            return {'allowed': False, 'reason': 'no_north_star_path'}

    return {'allowed': True, 'reason': 'passed'}


# ── Conversation gate (combined check) ────────────────────────────────────

def check_conversation_allowed(topic: str, initiator_name: str) -> dict:
    """Combined gate for autonomous conversation spawning.

    Checks: enabled → topic blocked → per-agent cap → total cap.

    Returns:
        {'allowed': True/False, 'reason': str, 'details': dict}
    """
    config = get_config()
    if not config.get('enabled'):
        return {'allowed': True, 'reason': 'focus_mode_disabled', 'details': {}}

    # 1) Topic block
    if is_topic_blocked(topic):
        return {
            'allowed': False,
            'reason': 'blocked_topic',
            'details': {'topic': topic[:100]},
        }

    # 2) Per-agent cap
    agent_cap = check_agent_conversation_cap(initiator_name)
    if not agent_cap['allowed']:
        return {
            'allowed': False,
            'reason': 'agent_hourly_cap',
            'details': agent_cap,
        }

    # 3) Total cap
    total_cap = check_total_conversation_cap()
    if not total_cap['allowed']:
        return {
            'allowed': False,
            'reason': 'total_hourly_cap',
            'details': total_cap,
        }

    return {'allowed': True, 'reason': 'passed', 'details': {}}


# ── Status summary (for PA / dashboard) ──────────────────────────────────

def get_status() -> dict:
    """Get Focus Mode status summary for display."""
    config = get_config()

    # Count blocks in last 24h from logs (approximate via cache counters)
    blocks_24h = cache.get('focus_mode:blocks_24h', 0)

    return {
        'enabled': config.get('enabled', False),
        'mode': config.get('mode', 'gentle'),
        'objective_weights': config.get('objective_weights', {}),
        'blocked_topics': config.get('blocked_topics_autonomous', []),
        'max_conversations_per_agent_per_hour': config.get('max_conversations_per_agent_per_hour', 2),
        'max_total_conversations_per_hour': config.get('max_total_conversations_per_hour', 8),
        'require_north_star': config.get('require_north_star_for_autonomous', False),
        'blocks_24h': blocks_24h,
    }


def record_block(reason: str):
    """Increment the 24h block counter."""
    key = 'focus_mode:blocks_24h'
    try:
        val = cache.get(key, 0)
        cache.set(key, val + 1, 86400)
    except Exception:
        pass
