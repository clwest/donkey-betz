"""Fleet app → u-d-b agent routing.

Pure-function resolution between a fleet app's `routing` request block and
the agent that should actually handle the message. No Django ORM, no I/O
beyond loading config/fleet_agent_routing.json. Designed in Session 1126
with Rigby; see PR description for the full contract.

Public surface:
    from core.services.fleet_routing import resolve
    decision = resolve(app_slug, routing_block)
    # decision: RoutingDecision(...)

The hint-vs-force semantics:
- `mode="hint"` — honor requested agent only if allowlisted, else fall back
  to the app's default. Never errors solely due to routing.
- `mode="force"` — only honored if `force_allowed[app_slug] == true` AND
  the requested agent resolves and is allowlisted. Otherwise downgrades to
  default + sets `was_overridden=true` + an explanatory `override_reason`.
  This is a conservative default; callers that want hard 403 on force
  failure can check `was_overridden` + `override_reason` themselves.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

from django.conf import settings


CONFIG_REL = Path("config") / "fleet_agent_routing.json"


@dataclass(frozen=True)
class RoutingDecision:
    """The structured output of resolve(). Maps 1:1 onto the response
    `routing` block u-d-b sends back to the caller."""
    app_slug: Optional[str]
    requested: dict = field(default_factory=dict)
    default_agent: Optional[str] = None
    resolved_agent: Optional[str] = None
    routed_to: Optional[str] = None      # set later by the dispatcher
    allowlist_hit: bool = False
    force_permitted: bool = False
    was_overridden: bool = False
    override_reason: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "app_slug": self.app_slug,
            "requested": dict(self.requested),
            "default_agent": self.default_agent,
            "resolved_agent": self.resolved_agent,
            "routed_to": self.routed_to,
            "allowlist_hit": self.allowlist_hit,
            "force_permitted": self.force_permitted,
            "was_overridden": self.was_overridden,
            "override_reason": self.override_reason,
        }


@lru_cache(maxsize=1)
def _load_config() -> dict:
    """Cached load of the routing JSON. Cache survives the process lifetime;
    deploy → restart picks up changes. For tests, call `_load_config.cache_clear()`."""
    path = Path(settings.BASE_DIR) / CONFIG_REL
    if not path.is_file():
        return {"defaults": {}, "roles": {}, "allowlists": {}, "force_allowed": {}}
    return json.loads(path.read_text())


def _normalize_routing(routing: Optional[dict]) -> dict:
    """Coerce a possibly-missing or partial routing block into a normal dict."""
    routing = dict(routing or {})
    return {
        "mode": routing.get("mode", "hint"),
        "agent": routing.get("agent"),
        "role": routing.get("role"),
        "app_slug": routing.get("app_slug"),
    }


def resolve(app_slug: Optional[str], routing: Optional[dict]) -> RoutingDecision:
    """Apply the fleet routing policy to a request.

    Args:
        app_slug: caller's app identity (e.g. "contract-concierge"). When
            None, no defaults or allowlists apply — the function still
            returns a RoutingDecision but it'll have `app_slug=None` and
            no resolution. This is the right shape for non-fleet callers.
        routing: the caller's routing block, may be None. Recognized keys:
            mode (hint|force), agent (AGENT_MAP key), role (role name).

    Returns a RoutingDecision. Never raises; misconfiguration surfaces as
    `was_overridden=True` + an `override_reason` string.
    """
    cfg = _load_config()
    r = _normalize_routing(routing)
    requested = {"mode": r["mode"], "agent": r["agent"], "role": r["role"]}

    # Non-fleet caller: nothing to resolve.
    if not app_slug:
        return RoutingDecision(app_slug=None, requested=requested)

    defaults = cfg.get("defaults", {})
    roles = cfg.get("roles", {})
    allowlists = cfg.get("allowlists", {})
    force_allowed = cfg.get("force_allowed", {})

    default_agent = defaults.get(app_slug)
    app_allow = set(allowlists.get(app_slug, []))
    force_ok = bool(force_allowed.get(app_slug, False))

    # Resolve the requested agent: explicit > role mapping > none.
    requested_agent: Optional[str] = None
    if r["agent"]:
        requested_agent = r["agent"]
    elif r["role"]:
        requested_agent = roles.get(r["role"])
        if requested_agent is None and r["role"]:
            # Role doesn't exist in the map.
            return RoutingDecision(
                app_slug=app_slug, requested=requested,
                default_agent=default_agent,
                resolved_agent=default_agent,
                allowlist_hit=False, force_permitted=False,
                was_overridden=True, override_reason="unknown_role",
            )

    # No specific request → fall back to app's default.
    if requested_agent is None:
        return RoutingDecision(
            app_slug=app_slug, requested=requested,
            default_agent=default_agent,
            resolved_agent=default_agent,
            allowlist_hit=False, force_permitted=force_ok,
            was_overridden=False,
            override_reason="no_default_for_app" if default_agent is None else None,
        )

    # Specific agent requested. Apply allowlist + force gates.
    allowed = requested_agent in app_allow
    mode = r["mode"]

    if mode == "force":
        if force_ok and allowed:
            return RoutingDecision(
                app_slug=app_slug, requested=requested,
                default_agent=default_agent,
                resolved_agent=requested_agent,
                allowlist_hit=True, force_permitted=True,
                was_overridden=False,
            )
        # Force not permitted or agent not allowlisted → downgrade to default.
        return RoutingDecision(
            app_slug=app_slug, requested=requested,
            default_agent=default_agent,
            resolved_agent=default_agent,
            allowlist_hit=allowed, force_permitted=force_ok,
            was_overridden=True,
            override_reason=(
                "force_not_permitted_for_app" if not force_ok
                else "not_allowlisted"
            ),
        )

    # Hint mode (default): honor if allowlisted, else fall back.
    if allowed:
        return RoutingDecision(
            app_slug=app_slug, requested=requested,
            default_agent=default_agent,
            resolved_agent=requested_agent,
            allowlist_hit=True, force_permitted=force_ok,
            was_overridden=False,
        )
    return RoutingDecision(
        app_slug=app_slug, requested=requested,
        default_agent=default_agent,
        resolved_agent=default_agent,
        allowlist_hit=False, force_permitted=force_ok,
        was_overridden=True,
        override_reason="not_allowlisted",
    )
