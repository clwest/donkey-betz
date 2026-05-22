---
title: "Session 1127 — Fleet agent routing Phase 2A (force-dispatch + hint bias)"
date: 2026-05-22
status: active
session: 1127
previous_handoff: SESSION_1126_FLEET_RUNTIME_BRAIN_PLUMBING.md
---

# Session 1127 — Fleet routing Phase 2A

> **Read this if** you want to know how fleet apps now actually route to a
> specific u-d-b agent (not just emit metadata about it), why the force
> path lives in `tasks_misc.py` instead of inside `UnifiedPAEntrypoint`,
> what Rigby's three safety-hatch rules look like in code, or what
> Phase 2B still needs.

## TL;DR

One PR.

- **#XXXX — Phase 2A plumb.** Force-dispatch wired into the PA Celery
  task: when a fleet app sends `mode=force` and clears all five safety
  gates, the task bypasses `UnifiedPAEntrypoint.process_message()`
  entirely and routes straight to the requested agent via
  `AgentRouter.route()`. Hint-mode bias plumbed into `process_message`
  with a "hint never overrides positive intent" rule. New module
  `core/services/fleet_routing_dispatch.py` owns snake_case ↔
  AGENT_MAP-key resolution and the safety gates. Compliancesentinel
  default flipped to `null` per Rigby (no SecurityAgent class exists
  yet). 26 tests.

Co-designed with Rigby in conversation `pa-d19c1674b936` (briefing →
signoff → implementation).

## What landed

### New module — `core/services/fleet_routing_dispatch.py` (~270 lines)

The bridge between `fleet_routing.resolve()` and `AgentRouter.route()`.

| Surface | Purpose |
|---|---|
| `SNAKE_TO_AGENT_MAP_KEY: dict[str, str]` | Explicit snake_case → PascalCase map for the 11 agents named in `fleet_agent_routing.json`. Handles acronyms (SEO) that a naïve snake-to-pascal walk would mangle (`SeoOptimizerAgent` vs `SEOOptimizerAgent`). |
| `resolve_to_agent_map_key(snake) → str \| None` | Maps a routing-config snake_case agent id to an AGENT_MAP key. Falls back to a naïve walk for anything not in the explicit map; the dispatcher does the final AGENT_MAP membership check, so a wrong fallback can't misroute — it just bails. |
| `should_force_dispatch(decision) → bool` | Pure gate. True iff `mode=force` AND `force_permitted` AND `allowlist_hit` AND not `was_overridden` AND `resolved_agent` is set. AGENT_MAP membership is verified separately in `apply_force_dispatch`. |
| `apply_force_dispatch(user, message, decision, context, conversation_id) → dict \| None` | Runs `AgentRouter.route()` and returns a PAResponse-shaped dict marked `_phase2_dispatched=True`. Returns None on any miss (AGENT_MAP, router exception) so the caller falls back to normal PA flow. |
| `derive_hint_for_context(decision) → dict \| None` | Returns `{agent_map_key, snake_name, app_slug}` for non-force decisions that pass the allowlist gate. Refuses to silently demote force-mode to a hint (Rigby's rule). |

### `core/tasks_misc.py:_impl_process_pa_chat_task` — force-dispatch shortcut

Resolution now happens **before** `pa.process_message()`. If
`should_force_dispatch()` returns True, the task calls
`apply_force_dispatch()`, builds a `PAResponse` from the result, and
skips the PA loop entirely. Otherwise, the decision is carried into PA
context as `_fleet_routing_decision` so the entrypoint can derive a
hint.

The Phase 1 post-PA decision-emit block was replaced with a single
reuse of the already-resolved `routing_decision`. The response's
`routing` block now carries:

- `phase2_dispatched: bool` — surface signal: did force actually fire?
- A WARN log on the worker when `resolved_agent != routed_to` (PA
  intent diverged from fleet resolution) — observability for hints
  that didn't steer.

### `core/services/unified_pa_entrypoint.py:process_message` — hint bias

After `_build_context`, the entrypoint reads
`context['_fleet_routing_decision']` and (when present) derives a
`_routing_hint` via `derive_hint_for_context`. The hint goes onto
`full_context`.

The keyword routing path applies the hint **only when intent detection
produced no `routed_to`** — a positive intent match always wins.
That preserves Rigby's "hint never overrides" rule.

FC-path hint is deferred to Phase 2B (would require prompt assembly
surgery; pragmatic call to ship 2A first).

### Config — `config/fleet_agent_routing.json`

```diff
 "defaults": {
   …
-  "compliancesentinel": "security_agent",
+  "compliancesentinel": null,
   …
 },
 "allowlists": {
   …
-  "compliancesentinel": ["security_agent"],
+  "compliancesentinel": [],
   …
 }
```

`security_agent` was a config bug from PR #2125 — there is no
`SecurityAgent` class in AGENT_MAP. Per Rigby, the fix for Phase 2A is
to default `compliancesentinel` to null so it falls through to normal
PA routing; Phase 2B can decide whether to add a real SecurityAgent or
remap to an existing concrete agent.

### Tests (26 total)

- `tests/services/test_fleet_routing_dispatch.py` — 21 tests covering
  the resolver, the 5-gate force check, AGENT_MAP-miss bail-out, hint
  derivation rules.
- `tests/services/test_fleet_routing_config_phase2.py` — 5 tests
  asserting the compliancesentinel config change and that the other 6
  fleet apps still resolve cleanly.

## How a fleet app uses Phase 2A

POST to `/api/pa/chat/`:

```json
{
  "message": "Draft a 1-page NDA for a contractor",
  "app_slug": "contract-concierge",
  "routing": {
    "mode": "force",
    "agent": "legal_doc_drafter_agent"
  }
}
```

Response now includes:

```json
{
  "routed_to": "LegalDocDrafterAgent",
  "routing": {
    "app_slug": "contract-concierge",
    "requested": {"mode": "force", "agent": "legal_doc_drafter_agent", "role": null},
    "default_agent": "legal_doc_drafter_agent",
    "resolved_agent": "legal_doc_drafter_agent",
    "routed_to": "LegalDocDrafterAgent",
    "allowlist_hit": true,
    "force_permitted": true,
    "was_overridden": false,
    "phase2_dispatched": true
  }
}
```

Before Phase 2A, `routed_to` was whatever PA's intent detector picked
(often diverged from `resolved_agent`). Now `phase2_dispatched: true`
means force actually fired and `routed_to` matches the AGENT_MAP key.

## Rigby's three safety-hatch rules — where they live

1. **Hint never overrides; only force does.** Enforced in
   `unified_pa_entrypoint.py:626`: hint is only applied when
   `routed_to` from intent detection is empty.
2. **Force requires verified `app_slug`.** Today, `app_slug` is
   accepted verbatim from the request body. Service-token
   verification for fleet callers is queued for Phase 2C.
3. **Compliancesentinel `security_agent` config bug.** Fixed in
   `fleet_agent_routing.json` — defaults to null, allowlist empty.
   Phase 2B can revisit.

The fourth (soft) rule Rigby mentioned — "ignore hint when conflicts
with governance/agent_control" — is not yet implemented; the existing
governor check inside `AgentRouter.route()` already covers force-mode
dispatches but not hint-biased keyword routes. Tracking for Phase 2B.

## What did NOT land (deferred to Phase 2B)

- **FC-path hint bias.** Requires injecting a system message in
  `_run_agentic_loop`. Skipped to keep this PR scoped.
- **Service-token verification for `app_slug`.** Right now any caller
  with a valid PA token can claim any `app_slug`. Mitigated by the
  allowlist + force_allowed gates; production hardening is a separate
  PR.
- **`SecurityAgent` class** for compliancesentinel. Either add it or
  remap the default — Rigby's call.
- **Fleet `brain_client.py` updates** (option B from Session 1126
  handoff). Each app's `brain_client.ask()` needs optional
  `agent`/`role`/`mode` params + frontend role-select. Now that 2A is
  in, the apps can start sending routing blocks that actually
  dispatch.

## Operational notes

- **PA tool changes need BOTH daphne AND celery restart.** Same rule
  as Session 1126; the new dispatch module loads into Celery workers'
  process memory.
- **`config/fleet_agent_routing.json` cache.** `fleet_routing._load_config`
  is `lru_cache(maxsize=1)`. Edits require a restart (or a manual
  `_load_config.cache_clear()` in dev). Tests use an autouse fixture
  to clear between cases.
- **Audit signal.** WARN `[PA routing] divergence` lines in the worker
  log mean a hint was set but PA's intent detection picked something
  else. Useful for tuning the allowlist + role mappings.

## Carryovers (open / parked)

- **ai-content-studio#2** — Docker foundation PR open. Per Chris: back burner.
- **24-7-ai-global** — Not yet Dockerized.
- **context-kit doctor floor**: `10 OK / 2 warnings` (both upstream).
