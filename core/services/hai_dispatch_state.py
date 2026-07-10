"""
HAI Dispatch State — CDR-001 §7 Gap 3 + Gap 4 (§16 wrap-up bundle)
==================================================================

Shared helper codifying the cross-channel dispatch-state convention for
HumanAttentionItem fanout. Replaces the ad-hoc ``payload['discord_sent']``
Discord-specific flag with a generalized ``payload['channels_fired']``
list convention (Gap 3), and canonizes the four dispatch outcomes as an
enum contract (Gap 4).

Ratified rules governing this module:
- PLAYBOOK-2.2.2 (CDR discipline) — CDR-001 covers the scope
- PLAYBOOK-3.2.2 (acceptance-tests-first) — AT16-3 + AT16-4 pre-drafted

Substrate context:
- HAI fanout pattern: signal receiver on ``HumanAttentionItem.post_save``
  → ``transaction.on_commit`` → Celery task → adapter call.
- Three shipped channels at HEAD 5bcb9777: Discord (PR #3038), Web Push
  (PR #3040), Expo (PR #1458). Inbox (Gap 1) joins them via this module.
- Backward compat: existing producers set ``payload['discord_sent']=True``
  to suppress double-dispatch; legacy flag preserved as one-way read.

Governance:
- Acceptance tests at ``core/tests/test_hai_wrap_up_bundle.py::AT16_3``
  and ``AT16_4`` verify the module contract at runtime.
- CDR-001 §7 Gap 3 + §12.3 (Rigby SIGN O4 refinement) is the ratified scope.
"""
from __future__ import annotations

import enum
from typing import Any, Dict, List


class ChannelDispatchState(enum.Enum):
    """Canonical outcomes for a channel dispatch attempt.

    Six states cover the observable dispatch outcomes for the HAI fanout
    pattern. Values are lowercase snake_case strings for stable DB storage
    (see ``HAIDispatchLog.status`` field choices).
    """

    NOT_ATTEMPTED = 'not_attempted'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    SUPPRESSED_BY_PRODUCER = 'suppressed_by_producer'
    KILL_SWITCH = 'kill_switch'
    GATED_OUT = 'gated_out'


# Legacy per-channel producer flags predating the ``channels_fired`` list.
# Read for backward compatibility; new producers should call
# ``payload_mark_channel_fired`` instead. Do NOT write these keys from
# new code.
_LEGACY_CHANNEL_FLAGS: Dict[str, str] = {
    'discord': 'discord_sent',
}


def payload_mark_channel_fired(payload: Dict[str, Any], channel: str) -> None:
    """Mark ``channel`` as fired on ``payload``.

    Idempotent — marking twice does not duplicate the channel. Writes
    the canonical ``payload['channels_fired']`` list; does NOT write any
    legacy per-channel key.

    Mutates ``payload`` in place. Callers that need to persist the
    payload after marking must save the enclosing model (typically
    ``HumanAttentionItem``) themselves.
    """
    if not isinstance(payload, dict):  # pragma: no cover — defensive
        raise TypeError(
            f"payload must be a dict; got {type(payload).__name__}"
        )
    fired = payload.setdefault('channels_fired', [])
    if not isinstance(fired, list):  # pragma: no cover — defensive
        fired = []
        payload['channels_fired'] = fired
    if channel not in fired:
        fired.append(channel)


def payload_has_channel_fired(payload: Dict[str, Any], channel: str) -> bool:
    """Check whether ``channel`` was previously fired on ``payload``.

    Reads BOTH the canonical ``payload['channels_fired']`` list AND the
    legacy per-channel key (e.g., ``payload['discord_sent']``) for
    backward compatibility. Returns True if either signals the channel
    fired.
    """
    if not isinstance(payload, dict):
        return False
    fired = payload.get('channels_fired') or []
    if isinstance(fired, list) and channel in fired:
        return True
    legacy_key = _LEGACY_CHANNEL_FLAGS.get(channel)
    if legacy_key and payload.get(legacy_key) is True:
        return True
    return False


def payload_channels_fired(payload: Dict[str, Any]) -> List[str]:
    """Return the list of channel names fired on ``payload``.

    Returns a fresh list — mutations to the returned list do NOT affect
    the underlying payload. Only reads the canonical ``channels_fired``
    list; legacy per-channel keys are not enumerated (use
    ``payload_has_channel_fired(payload, channel)`` for per-channel
    backward-compat reads).
    """
    if not isinstance(payload, dict):
        return []
    fired = payload.get('channels_fired') or []
    if not isinstance(fired, list):  # pragma: no cover — defensive
        return []
    return list(fired)
