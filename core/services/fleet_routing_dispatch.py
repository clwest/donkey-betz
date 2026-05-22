"""Fleet routing → AgentRouter dispatch bridge (Phase 2A).

Phase 1 (Session 1126, PR #2125) made fleet routing decisions observable:
fleet apps could send `routing` blocks, the PA task resolved them via
`core.services.fleet_routing.resolve()`, and the decision was surfaced in
the response. But the decision was metadata only — PA's own intent
detection still chose the agent.

Phase 2 (Session 1127) actually *uses* the decision:

- `force` + `force_permitted` + `allowlist_hit` + resolvable AGENT_MAP key
  → bypass PA entirely, dispatch via `AgentRouter.route()`, wrap result
  in `PAResponse`.
- `hint` + `allowlist_hit` + resolvable → set `_routing_hint` on the
  PA context so `process_message()` can bias intent detection / FC.
- Anything else → no override; normal PA flow.

This module is the dispatch bridge. It owns:
- The snake_case → PascalCase AGENT_MAP-key mapping (explicit for the
  agents named in `config/fleet_agent_routing.json`, with a guarded
  naïve fallback for anything else).
- `should_force_dispatch()` — the gate that decides whether to bypass
  PA. Pure function, no I/O.
- `apply_force_dispatch()` — actually runs the agent via `AgentRouter`
  and wraps `AgentResult` into a `PAResponse`-shaped dict. Sync; called
  from inside the Celery task before it spins up the async PA loop.

Co-designed with Rigby (Session 1127). Safety hatch rules:
- Hint mode never overrides; only force does.
- Force requires all gates (`force_permitted`, `allowlist_hit`,
  `was_overridden=False`, resolvable to a real AGENT_MAP class).
- If `resolved_agent` is set but doesn't map to AGENT_MAP, the
  decision is treated as overridden (logged, normal PA flow runs).
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from core.services.fleet_routing import RoutingDecision

logger = logging.getLogger(__name__)


# Explicit snake_case → AGENT_MAP key map for the agents named in
# config/fleet_agent_routing.json. Covers acronyms (SEO) that a
# naive snake-to-pascal walk would mangle (would produce
# "SeoOptimizerAgent" instead of "SEOOptimizerAgent").
SNAKE_TO_AGENT_MAP_KEY: dict[str, str] = {
    "customer_research_agent": "CustomerResearchAgent",
    "content_writer_agent": "ContentWriterAgent",
    "legal_doc_drafter_agent": "LegalDocDrafterAgent",
    "marketing_strategy_agent": "MarketingStrategyAgent",
    "market_intelligence_agent": "MarketIntelligenceAgent",
    "trend_analysis_agent": "TrendAnalysisAgent",
    "brand_strategy_agent": "BrandStrategyAgent",
    "competitor_analysis_agent": "CompetitorAnalysisAgent",
    "seo_optimizer_agent": "SEOOptimizerAgent",
    "social_media_agent": "SocialMediaAgent",
    "editor_agent": "EditorAgent",
    # "security_agent" intentionally absent — no SecurityAgent class
    # exists in AGENT_MAP yet. fleet_agent_routing.json now defaults
    # compliancesentinel to null per Rigby's Phase 2A guidance; any
    # other caller that asks for security_agent will fall through to
    # the naïve resolver, fail AGENT_MAP membership, and bail safely
    # to normal PA flow with an INFO log.
}


def _naive_snake_to_pascal(snake: str) -> str:
    """Fallback when the snake_name isn't in the explicit map.

    Drops a trailing `_agent` suffix only if the snake form keeps the
    suffix-after-conversion convention. Used only as a probe before
    AGENT_MAP membership check.
    """
    parts = [p for p in snake.split("_") if p]
    return "".join(p.capitalize() for p in parts)


def resolve_to_agent_map_key(snake_name: Optional[str]) -> Optional[str]:
    """Map a routing-config snake_case agent identifier to an AGENT_MAP key.

    Returns the AGENT_MAP key if resolution succeeds, else None. Does
    *not* import AGENT_MAP here (avoids triggering agent_router import
    chain on every PA turn); membership check is the dispatcher's job.
    """
    if not snake_name:
        return None
    explicit = SNAKE_TO_AGENT_MAP_KEY.get(snake_name)
    if explicit:
        return explicit
    # Naïve fallback. The dispatcher verifies AGENT_MAP membership
    # before actually dispatching, so a wrong guess here can't cause
    # a misroute — it just causes a bail-out to normal PA flow.
    return _naive_snake_to_pascal(snake_name)


def should_force_dispatch(decision: Optional[RoutingDecision]) -> bool:
    """Gate for the force-dispatch shortcut in tasks_misc.

    Returns True only when ALL of the following hold:
    - decision exists
    - caller asked for `mode=force`
    - `force_permitted` (the app appears in `force_allowed` config)
    - `allowlist_hit` (the requested agent is in the app's allowlist)
    - `was_overridden` is False (resolution didn't downgrade)
    - `resolved_agent` is set

    AGENT_MAP membership is checked separately by `apply_force_dispatch`
    so we can keep this function pure.
    """
    if decision is None:
        return False
    if (decision.requested or {}).get("mode") != "force":
        return False
    if not decision.force_permitted:
        return False
    if not decision.allowlist_hit:
        return False
    if decision.was_overridden:
        return False
    if not decision.resolved_agent:
        return False
    return True


def apply_force_dispatch(
    user,
    message: str,
    decision: RoutingDecision,
    context: Optional[dict] = None,
    conversation_id: Optional[str] = None,
) -> Optional[dict]:
    """Force-dispatch via AgentRouter, return a PAResponse-shaped dict.

    Returns None when dispatch should NOT happen (resolved_agent isn't
    in AGENT_MAP, or routing fails). On a successful dispatch, returns
    a dict mirroring `PAResponse.to_dict()` so the caller can build a
    PAResponse without importing it here (no circular risk).

    The returned dict includes a `_phase2_dispatched` marker so the
    Celery task can flag the routing decision metadata.
    """
    from core.agent_router import AgentRouter, AgentNotFoundError

    agent_map_key = resolve_to_agent_map_key(decision.resolved_agent)
    if not agent_map_key:
        logger.info(
            "[fleet-routing] No AGENT_MAP mapping for resolved_agent=%r "
            "(app=%s, mode=force) — bail to normal PA flow",
            decision.resolved_agent, decision.app_slug,
        )
        return None

    router = AgentRouter(user=user)
    if not router.is_valid_agent(agent_map_key):
        logger.info(
            "[fleet-routing] '%s' not in AGENT_MAP (resolved from %r, "
            "app=%s) — bail to normal PA flow",
            agent_map_key, decision.resolved_agent, decision.app_slug,
        )
        return None

    full_context = dict(context or {})
    full_context.setdefault("conversation_id", conversation_id)
    full_context["_fleet_force_dispatch"] = True
    full_context["_fleet_app_slug"] = decision.app_slug

    start_ms = time.time()
    trace_id = f"pa-fleet-{int(start_ms * 1000)}"

    try:
        result = router.route(
            agent_name=agent_map_key,
            task=message,
            context=full_context,
            trigger_source="user_chat",
        )
    except AgentNotFoundError as e:
        logger.warning(
            "[fleet-routing] AgentRouter raised AgentNotFoundError for "
            "%s (app=%s): %s — bail to normal PA flow",
            agent_map_key, decision.app_slug, e,
        )
        return None
    except Exception as e:
        logger.exception(
            "[fleet-routing] AgentRouter.route() failed for %s (app=%s): %s "
            "— bail to normal PA flow",
            agent_map_key, decision.app_slug, e,
        )
        return None

    latency_ms = int((time.time() - start_ms) * 1000)
    content = getattr(result, "message", None) or getattr(result, "content", "") or ""
    ok = bool(getattr(result, "success", True))
    error = None if ok else getattr(result, "error", None)

    logger.info(
        "[fleet-routing] Force-dispatched %s for app=%s in %dms ok=%s",
        agent_map_key, decision.app_slug, latency_ms, ok,
    )

    return {
        "content": content,
        "trace_id": trace_id,
        "tool_runs": [
            {
                "tool": agent_map_key,
                "ok": ok,
                "latency_ms": latency_ms,
                "source": "fleet_force_dispatch",
            }
        ],
        "audio_url": None,
        "intent": "fleet_force_dispatch",
        "routed_to": agent_map_key,
        "profile_completeness": None,
        "latency_ms": latency_ms,
        "error": error,
        "tool_call_metadata": None,
        "tool_result_data": None,
        "response_id": None,
        "lane": None,
        # Internal marker — surfaces into the routing decision dict in
        # tasks_misc so callers can tell phase 2 actually fired.
        "_phase2_dispatched": True,
        "_phase2_agent_map_key": agent_map_key,
    }


def derive_hint_for_context(decision: Optional[RoutingDecision]) -> Optional[dict]:
    """Return a `_routing_hint` dict for non-force decisions.

    Used by `unified_pa_entrypoint.process_message()` to bias intent
    detection (keyword path) or LLM tool selection (FC path) without
    overriding either. Returns None when the decision shouldn't bias
    anything (no decision, was_overridden, no allowlist_hit, no
    resolvable AGENT_MAP key).

    Hint requires `allowlist_hit=True` and `was_overridden=False`. The
    hint never carries `mode=force` semantics — force is handled by
    `apply_force_dispatch` upstream; if we reach here in force mode,
    force-dispatch must have already bailed (no AGENT_MAP match), and
    falling back to a hint would be surprising. Bail in that case too.
    """
    if decision is None:
        return None
    if decision.was_overridden:
        return None
    if not decision.allowlist_hit:
        return None
    if (decision.requested or {}).get("mode") == "force":
        # Force already had its chance upstream; don't quietly demote
        # to a hint.
        return None
    if not decision.resolved_agent:
        return None
    agent_map_key = resolve_to_agent_map_key(decision.resolved_agent)
    if not agent_map_key:
        return None
    return {
        "agent_map_key": agent_map_key,
        "snake_name": decision.resolved_agent,
        "app_slug": decision.app_slug,
    }
