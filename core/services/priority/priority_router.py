"""
Session 1086 PR 2: PriorityRouter — pure matching logic for priority-aware routing.

Initiative ``2dcb79d7-6f2b-4e67-a366-a54e96d7870f``. This module is the
middle layer of the 3-PR priority-aware routing MVP:

- **PR 1 (#1911, merged):** :class:`core.models_unified_system.ActivePriority`
  model + ``active_priority_tool`` PA tool + seed priority.
- **PR 2 (this PR):** :class:`PriorityRouter` matching logic + cache +
  :class:`PriorityDecision` dataclass. Pure logic, no integration with
  ``agent_router.route()``, fully testable in isolation.
- **PR 3:** wire :meth:`PriorityRouter.check` into ``agent_router.route()``,
  add the semaphore throttling (matched=8, mismatched=1-2), plumb
  ``trigger_source`` from all dispatch paths, add telemetry fields.

## Locked design contract (from the Rigby design review)

**Match precedence** — stop at the first rule that applies:

0. If ``trigger_source == 'user_chat'`` → MATCH via ``user_chat_exempt``
   (user-triggered work is never throttled, per Rigby's Q5).
1. If ``agent_name`` in any priority's ``agent_whitelist`` → MATCH via
   ``whitelist`` — global short-circuit.
2. If ``agent_name`` in any priority's ``agent_blacklist`` → MISMATCH
   via ``blacklist`` — global short-circuit. Whitelist beats blacklist
   if both hit (whitelist is rule 1).
3. If any priority's ``tags`` list overlaps with the derived agent tag
   set → MATCH via ``tags``. This is the primary automatic matcher.
4. If ``priority.enable_keyword_match`` is True AND any priority tag
   appears as a substring inside the lowercased ``agent_name + task``
   string → MATCH via ``keyword``. Opt-in per Rigby's Q1 because
   substring matching creates false positives by default.
5. No active priorities at all → MATCH via ``fail_open``.
6. Priorities exist but nothing matched → MISMATCH with
   ``matched_via=None``.

## IMPORTANT: whitelist and blacklist are GLOBAL, not per-priority

Whitelist and blacklist hits short-circuit across the *entire active
priority set*, not just the priority that owns the list. Concrete
consequences to remember:

- If **any** active priority whitelists ``ImageAgent``, ``ImageAgent``
  is MATCHED regardless of what every other priority says.
- If **any** active priority blacklists ``ImageAgent`` AND no priority
  whitelists it, ``ImageAgent`` is MISMATCHED globally — even if
  another priority's ``tags`` list would otherwise overlap and match.
- If a single agent appears in priority A's whitelist and priority
  B's blacklist, the **whitelist wins** because rule 1 fires before
  rule 2.

This is **not** "this priority doesn't match, skip to the next one."
Do not change the interpretation in PR 3 or any follow-up without
bumping the contract and updating smoke test #3 (which locks the
whitelist-beats-blacklist behavior). The alternative (per-priority
blacklist) is more nuanced but forces us to decide how to pick
``priority_name`` when multiple priorities match, and Rigby's
Session 1086 design review deliberately picked the simpler global
semantics for MVP.

**Fail-open everywhere.** Empty priority set, all expired, DB error,
matching helper exception — any of these return MATCH rather than
blocking production traffic. Observability comes from rate-limited
``logger.exception`` calls, not from refusing to dispatch.

**Derived agent tags** are built from three sources combined into a
single set:

- The ``agent_name`` itself, lowercased (so ``ImageAgent`` always
  matches a priority tagged ``imageagent``).
- The agent's ``category`` field from
  :class:`core.models_unified_system.Agent` (if the agent has a row
  and a category set), lowercased.
- The entries in :data:`core.services.priority.agent_tags.AGENT_TAG_OVERRIDES`.

**60s in-process cache.** Module-level dict keyed on cache expiry
timestamp. Reading ``ActivePriority.get_active_priorities()`` is cheap
but we still cache because the check runs on every dispatch. Cache is
invalidated naturally after 60s (matches Rigby's suggestion in the
design review) and can be force-flushed via
:meth:`PriorityRouter.invalidate_cache` for tests and PA tool use.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ── PriorityDecision dataclass ──────────────────────────────────────────

# The allowed values for ``matched_via``. Using plain strings rather than
# an Enum so the dataclass serializes cleanly to JSON for PA tool output
# and telemetry fields without an extra ``.value`` dance.
MATCHED_VIA_USER_CHAT = "user_chat_exempt"
MATCHED_VIA_WHITELIST = "whitelist"
MATCHED_VIA_BLACKLIST = "blacklist"
MATCHED_VIA_TAGS = "tags"
MATCHED_VIA_KEYWORD = "keyword"
MATCHED_VIA_FAIL_OPEN = "fail_open"


@dataclass
class PriorityDecision:
    """
    The outcome of a :meth:`PriorityRouter.check` call.

    ``matched`` answers the core question: should this dispatch run in
    the high-concurrency matched lane (True) or the throttled mismatched
    lane (False)? ``throttle_class`` is a redundant string form of the
    same signal, kept because PR 3's telemetry layer will log it as-is
    without having to branch on the bool.

    ``recommended_queue`` is unused in PR 3's MVP (which ships Option A:
    semaphore-based throttling within the same queue), but exists so
    Option B (dedicated low_priority Celery queue) can be switched on
    later without changing the decision contract.

    ``priority_name`` is populated when a specific priority drove the
    decision (whitelist/blacklist/tags/keyword); it's ``None`` for
    ``fail_open``, ``user_chat_exempt``, and the no-match MISMATCH case.

    ``matched_via`` describes which rule fired. Useful for debugging
    (“why did ImageAgent match today?”) and for the future governance
    UI; it's also surfaced verbatim via the PA tool's ``test_match``
    action.
    """

    matched: bool
    priority_name: Optional[str]
    throttle_class: str  # 'matched' or 'mismatched'
    recommended_queue: str  # 'default' or 'low_priority'
    matched_via: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "matched": self.matched,
            "priority_name": self.priority_name,
            "throttle_class": self.throttle_class,
            "recommended_queue": self.recommended_queue,
            "matched_via": self.matched_via,
        }


# ── Module-level cache state ────────────────────────────────────────────

_CACHE_TTL_S = 60.0
_cache_lock = threading.Lock()
_cache_expires_at: float = 0.0
_cache_priorities: List[Dict[str, Any]] = []
_cache_last_fail_log_ts: float = 0.0


def _log_fail_open_rate_limited() -> None:
    """
    Emit a single ``logger.exception`` at most once per 60 seconds so we
    can SEE silent DB failures without flooding logs when the whole
    ActivePriority table is unreachable. Defensive-wrapped so logging
    itself can never break the fail-open contract.
    """
    global _cache_last_fail_log_ts
    try:
        now = time.monotonic()
        if now - _cache_last_fail_log_ts > 60.0:
            _cache_last_fail_log_ts = now
            logger.exception(
                "PriorityRouter fail-open: priority fetch raised, routing "
                "without priorities until next successful read"
            )
    except Exception:
        pass  # logging must never break fail-open


# ── PriorityRouter class ────────────────────────────────────────────────

# Queue / throttle class constants — kept here rather than in a separate
# constants module because they're part of the PriorityDecision contract
# and PR 3 imports them directly.
THROTTLE_CLASS_MATCHED = "matched"
THROTTLE_CLASS_MISMATCHED = "mismatched"
QUEUE_DEFAULT = "default"
QUEUE_LOW_PRIORITY = "low_priority"

# trigger_source values. MATCH anything coming from the user — never
# throttle chat-driven work. Any other value (or None) goes through the
# full matching pipeline.
TRIGGER_SOURCE_USER_CHAT = "user_chat"


class PriorityRouter:
    """
    Stateless matcher. Instance methods exist for testability (so tests
    can inject a fake priorities list), but the module-level cache is
    shared across instances, which is the desired behavior in production.
    """

    def check(
        self,
        agent_name: str,
        task: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        trigger_source: Optional[str] = None,
    ) -> PriorityDecision:
        """
        Return a :class:`PriorityDecision` describing whether this
        dispatch should run in the matched or mismatched lane.

        Never raises — all exceptions are caught and converted to a
        fail-open MATCH decision. This is the load-bearing guarantee
        that lets PR 3 wire the check into ``agent_router.route()``
        without worrying about cascading failures.
        """
        try:
            # Rule 0: user-triggered work is never throttled.
            if trigger_source == TRIGGER_SOURCE_USER_CHAT:
                return PriorityDecision(
                    matched=True,
                    priority_name=None,
                    throttle_class=THROTTLE_CLASS_MATCHED,
                    recommended_queue=QUEUE_DEFAULT,
                    matched_via=MATCHED_VIA_USER_CHAT,
                )

            priorities = self._get_cached_priorities()

            # Rule 5: no priorities at all → fail-open MATCH.
            if not priorities:
                return self._fail_open_decision()

            # Rule 1: whitelist short-circuit MATCH (global — any priority).
            for p in priorities:
                if agent_name in p.get("agent_whitelist", []):
                    return PriorityDecision(
                        matched=True,
                        priority_name=p.get("name"),
                        throttle_class=THROTTLE_CLASS_MATCHED,
                        recommended_queue=QUEUE_DEFAULT,
                        matched_via=MATCHED_VIA_WHITELIST,
                    )

            # Rule 2: blacklist short-circuit MISMATCH (global — any priority).
            for p in priorities:
                if agent_name in p.get("agent_blacklist", []):
                    return PriorityDecision(
                        matched=False,
                        priority_name=p.get("name"),
                        throttle_class=THROTTLE_CLASS_MISMATCHED,
                        recommended_queue=QUEUE_LOW_PRIORITY,
                        matched_via=MATCHED_VIA_BLACKLIST,
                    )

            # Rule 3: tag overlap MATCH.
            agent_tag_set = self._derive_agent_tags(agent_name)
            for p in priorities:
                priority_tags = {t.lower() for t in p.get("tags", []) if isinstance(t, str)}
                if priority_tags & agent_tag_set:
                    return PriorityDecision(
                        matched=True,
                        priority_name=p.get("name"),
                        throttle_class=THROTTLE_CLASS_MATCHED,
                        recommended_queue=QUEUE_DEFAULT,
                        matched_via=MATCHED_VIA_TAGS,
                    )

            # Rule 4: opt-in keyword MATCH. Only applies to priorities
            # that explicitly set ``enable_keyword_match=True``.
            haystack = (agent_name + " " + (task or "")).lower()
            for p in priorities:
                if not p.get("enable_keyword_match"):
                    continue
                for tag in p.get("tags", []):
                    if not isinstance(tag, str) or not tag:
                        continue
                    if tag.lower() in haystack:
                        return PriorityDecision(
                            matched=True,
                            priority_name=p.get("name"),
                            throttle_class=THROTTLE_CLASS_MATCHED,
                            recommended_queue=QUEUE_DEFAULT,
                            matched_via=MATCHED_VIA_KEYWORD,
                        )

            # Rule 6: priorities exist but nothing matched → MISMATCH.
            return PriorityDecision(
                matched=False,
                priority_name=None,
                throttle_class=THROTTLE_CLASS_MISMATCHED,
                recommended_queue=QUEUE_LOW_PRIORITY,
                matched_via=None,
            )
        except Exception:
            # Any unexpected exception in the match pipeline → fail open.
            # Don't let a bug in here take down the dispatch path.
            _log_fail_open_rate_limited()
            return self._fail_open_decision()

    # ── Internal helpers ────────────────────────────────────────────────

    def _fail_open_decision(self) -> PriorityDecision:
        return PriorityDecision(
            matched=True,
            priority_name=None,
            throttle_class=THROTTLE_CLASS_MATCHED,
            recommended_queue=QUEUE_DEFAULT,
            matched_via=MATCHED_VIA_FAIL_OPEN,
        )

    def _get_cached_priorities(self) -> List[Dict[str, Any]]:
        """
        Return the cached list of active priorities, refreshing from the
        DB if the cache has expired. Lock-protected for thread safety
        under Daphne / Celery worker pools. Fail-open (returns []) on any
        DB exception — the calling ``check()`` treats [] as "no priorities".
        """
        global _cache_expires_at, _cache_priorities

        now = time.monotonic()
        if now < _cache_expires_at:
            return _cache_priorities

        # Cache miss — refresh under lock so we only hit the DB once
        # even if multiple threads race into check() simultaneously.
        with _cache_lock:
            # Re-check after acquiring the lock in case another thread
            # refreshed while we were waiting.
            now = time.monotonic()
            if now < _cache_expires_at:
                return _cache_priorities

            try:
                # Lazy inline import to match the models_unified_system
                # pattern and avoid import-time Django apps issues.
                from core.models_unified_system import ActivePriority
                fresh = ActivePriority.get_active_priorities()
            except Exception:
                _log_fail_open_rate_limited()
                fresh = []

            _cache_priorities = fresh
            _cache_expires_at = now + _CACHE_TTL_S
            return _cache_priorities

    def _derive_agent_tags(self, agent_name: str) -> set:
        """
        Build the tag set for a given agent. Sources combined in order:

        1. The lowercased ``agent_name`` itself
        2. :data:`AGENT_TAG_OVERRIDES` entries
        3. ``Agent.category`` from the DB (if the agent row exists)

        Returns an already-lowercased ``set[str]`` so the caller can do
        cheap set intersection against priority tag sets.
        """
        tags: set = {agent_name.lower()}

        try:
            from core.services.priority.agent_tags import AGENT_TAG_OVERRIDES
            overrides = AGENT_TAG_OVERRIDES.get(agent_name, [])
            tags.update(t.lower() for t in overrides if isinstance(t, str))
        except Exception:
            pass  # missing override dict must not break matching

        try:
            from core.models_unified_system import Agent
            row = Agent.objects.filter(name=agent_name).first()
            if row is not None and getattr(row, "category", None) is not None:
                cat = row.category
                for attr in ("slug", "name"):
                    val = getattr(cat, attr, None)
                    if isinstance(val, str) and val:
                        tags.add(val.lower())
                        break
                else:
                    tags.add(str(cat).lower())
        except Exception:
            pass  # no DB / no Agent row / no category → skip category tag

        return tags

    @classmethod
    def invalidate_cache(cls) -> None:
        """
        Force the next :meth:`check` call to refetch from the DB. Used
        by :func:`active_priority_tool.test_match` after a ``set`` /
        ``update`` so preview decisions reflect current state, and by
        tests that want a clean slate between assertions.
        """
        global _cache_expires_at, _cache_priorities
        with _cache_lock:
            _cache_expires_at = 0.0
            _cache_priorities = []
