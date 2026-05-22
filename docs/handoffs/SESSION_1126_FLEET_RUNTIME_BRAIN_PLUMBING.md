---
title: "Session 1126 — Fleet runtime metadata + fleet_health + agent routing Phase 1"
date: 2026-05-22
status: active
session: 1126
previous_handoff: SESSION_1125_DOCKER_FLEET_AND_BRAIN_BRIDGE.md
---

# Session 1126 — Fleet runtime metadata + fleet_health + agent routing Phase 1

> **Read this if** you want to understand how each Docker fleet app's
> runtime metadata now flows to Rigby (PR #2123), how the new
> `fleet_health` PA tool gives 2-second answers to "what's broken?"
> (PR #2124), or where Phase 1 of agent-specific consult routing
> landed and what Phase 2 looks like (PR #2125).

## TL;DR

Three PRs merged, all co-designed with Rigby per the Session 1124
co-author pattern.

1. **#2123 — Docker runtime metadata.** Each of the 7 fleet repo
   profiles now carries a `docker` block (web URL, API URL, brain
   bridge endpoint, container names, fleet-net hostnames,
   healthchecks, bootstrap commands). The `register_external_repo`
   markdown serializer was patched to surface the block in the
   pinned Repo Profile deliverable — Rigby can answer "how do I
   reach mentorforge's brain right now?" from her tools.

2. **#2124 — `fleet_health` rollup.** New mgmt command (`python
   manage.py fleet_health_rollup`) + new PA tool (`fleet_health`).
   Single probe function (`probe_fleet`) shared between CLI and
   tool surfaces. Reads each app's `docker.base_urls.api_url +
   docker.healthchecks.api.path` and hits `/api/health`. ~2 second
   answer. Verified live: 7/7 healthy on `make up`; took mentorforge
   down → showed UNREACHABLE with exit code 1.

3. **#2125 — Agent routing Phase 1.** New
   `config/fleet_agent_routing.json` (defaults / roles / allowlists
   / force_allowed). New `core/services/fleet_routing.py:resolve()`
   pure function with hint/force semantics. PA chat view + Celery
   task patched to thread routing through context and emit a
   structured `routing` decision in the response. **Metadata
   pipeline only** — Phase 2 wires `resolved_agent` into PA's
   deliberation router. Three architectural options considered;
   Rigby picked extending the brain bridge (Option A) over direct
   AgentRouter (B) or PA tool wrapper (C).

Workspaces already existed for all 12 fleet repos from Session
1119 — what was missing was runtime metadata freshness. Reframed
Option A from "register" to "extend with Docker runtime block."

## Why this session is the wedge it is

Chris's Session 1126 directive: **"Use Rigby to start connecting
real-time data and Agents from u-d-b to the other apps."**

The brain bridge from Session 1125 was plumbing — every fleet app
could ask Rigby. But Rigby had no per-app context (stale workspace
profiles), no aggregate view (no fleet health tool), and no way to
route a question to the *right* agent in u-d-b's network. This
session shipped the foundations for all three.

## What shipped per PR

### #2123 — Docker runtime in repo profiles

Each `config/external_repos/<slug>.json` got a top-level `docker` block:

```json
{
  "docker": {
    "enabled": true,
    "primary_service": "web",
    "base_urls": {"web_url": "...", "api_url": "..."},
    "host_ports": {"web": 5174, "api": 8002},
    "container_names": {"web": "mentorforge_web", "api": "mentorforge_api", "postgres": "..."},
    "fleet_net_hostnames": {...},
    "healthchecks": {"web": {"path": "/", ...}, "api": {"path": "/api/health", ...}},
    "brain_bridge": {"url": "...", "auth_mode": "demo_user", "demo_user": {...}},
    "compose_files": [...],
    "env_files": [...],
    "depends_on_services": ["postgres"],
    "bootstrap_commands": {"direct": "...", "via_infra_make": "..."},
    "notes": [...]
  }
}
```

The `register_external_repo._render_repo_profile_markdown()` was
patched to emit a "## Docker runtime (live laptop fleet)" section in
the pinned Repo Profile deliverable. Without this patch, Rigby's
first attempt to pull mentorforge's profile reported the docker
block missing — a real serializer gap she caught mid-build.

Pattern lesson: **when adding new fields to a config JSON that gets
serialized to a deliverable, patch the renderer too.** Otherwise
consumers reading the deliverable see stale content even though the
JSON is updated.

### #2124 — fleet_health rollup

**Mgmt command** (`core/management/commands/fleet_health_rollup.py`):

```bash
python manage.py fleet_health_rollup            # human table
python manage.py fleet_health_rollup --json     # machine-readable
python manage.py fleet_health_rollup --repo mentorforge
python manage.py fleet_health_rollup --timeout 5
```

Exit codes: 0 healthy / 1 any failure / 2 nothing to probe.

**PA tool** (`fleet_health`): read-only. Same `probe_fleet()`
function the mgmt command uses — CLI and tool can't drift.
Parameters: `repo`, `timeout_seconds`, `include_healthy`.

Verified end-to-end via Rigby's tool invocation:

```json
{
  "generated_at": "2026-05-22T...",
  "overall_status": "healthy",
  "apps": [
    {"slug": "compliancesentinel", "ok": true, "status": "HEALTHY", "latency_ms": 3, "url": "..."},
    ... (7 rows)
  ],
  "probed_count": 7,
  "healthy_count": 7
}
```

**Tool-registration gotcha:** the PA's tool registry is loaded at
process start in BOTH daphne AND each celery worker. Restarted just
daphne after the tool addition — Rigby reported the tool unknown.
Restarted celery too — Rigby invoked cleanly. Always restart both.

### #2125 — Agent routing Phase 1

**The control plane** lives in u-d-b (centralized, not per-app —
Rigby's call):

- `config/fleet_agent_routing.json` — maps:
  - `defaults[app_slug]` → AGENT_MAP name (fallback)
  - `roles[role_name]` → AGENT_MAP name (role-based requests)
  - `allowlists[app_slug]` → set of permitted agents
  - `force_allowed[app_slug]` → bool (escape from hint→default
    downgrade)

- `core/services/fleet_routing.py:resolve(app_slug, routing_block)`
  → `RoutingDecision`. Pure function, lru_cache'd JSON load. Hint
  vs force semantics:
  - **hint**: honor if allowlisted, else fall back to default.
    Never errors.
  - **force**: only honored if `force_allowed[app_slug]==true` AND
    allowlisted. Otherwise downgrades to default with
    `was_overridden=true` and `override_reason` set. Conservative
    default — callers that want hard 403 can check the dict.

**PA chat flow**:

1. View (`core/views_personal_assistant.py:unified_pa_chat`) reads
   optional `routing` + `app_slug` from request payload, threads
   through context.
2. Celery task (`core/tasks_misc.py:_impl_process_pa_chat_task`)
   calls `fleet_routing.resolve()` when context carries
   routing/app_slug, attaches the decision to the response under
   `routing`.
3. Response now carries:
   ```json
   "routing": {
     "app_slug": "contract-concierge",
     "requested": {"mode": "hint", "agent": "legal_doc_drafter_agent", "role": null},
     "default_agent": "legal_doc_drafter_agent",
     "resolved_agent": "legal_doc_drafter_agent",
     "routed_to": "<whatever PA actually dispatched to>",
     "allowlist_hit": true,
     "force_permitted": true,
     "was_overridden": false,
     "override_reason": null
   }
   ```

**Verified live**:
- `contract-concierge` hint `legal_doc_drafter_agent` (allowlisted) →
  resolved cleanly, allowlist_hit=true
- `mentorforge` force `security_agent` (force NOT allowed) →
  downgraded to `customer_research_agent`, was_overridden=true,
  override_reason="force_not_permitted_for_app"

**Important: this is Phase 1 (metadata only).** The PA's
deliberation loop doesn't yet USE `resolved_agent` to pin its
routing — it still uses its own intent detection. Phase 2 plumbs
the hint into PA's router. Today's PR is the contract + the visible
metadata pipeline, so we can iterate on resolution logic with real
traffic before risking the dispatch.

## Co-design with Rigby (Session 1124 pattern, fifth+ run)

Per-PR shape:

1. Claude proposes scope + open questions
2. Rigby picks an option, proposes concrete contract (e.g. JSON
   shape, schema fields)
3. Claude implements
4. Rigby verifies via her tools (e.g. pulling a deliverable, calling
   the new PA tool)
5. Catches drift early (the markdown serializer gap in #2123 was a
   Rigby catch mid-build)

Net effect: she's the second pair of eyes that catches what Claude
misses when moving fast.

## New pattern: Phase-1-metadata-first

For multi-phase routing/dispatch work, ship the **observability**
(metadata, decision records, structured response fields) first.
THEN wire the action.

Why: lets you iterate on resolution logic with real traffic before
risking the actual dispatch. The routing block carries through PA
chat responses now — visible to every brain-bridge caller — but no
behavior changes yet. Phase 2 hooks `resolved_agent` into the
router with confidence that resolution itself is sound.

## Operational notes

- **PA tool registration needs BOTH daphne AND celery restart.**
  ```
  pkill -f "daphne -b 127.0.0.1 -p 8000"
  pkill -f "celery -A core"
  make start && make celery
  ```

- **Workspaces existed already (Session 1119).** Don't re-create.
  `ProjectWorkspace.objects.count()` was 15 at session start.

- **Renderer-stays-with-config rule.** When you add a JSON field
  that gets serialized to a deliverable, patch the renderer in the
  same PR.

- **Behavior layer validated a third time** — Rigby auto-redacted
  `demo@mentorforge.dev` / `demo123` in her JSON proposal even
  though they're publicly documented. The no-claims/sensitive-handling
  rule is live, sometimes a bit too cautious.

## Current laptop state at session close

```
u-d-b (BRAIN)
  unified-postgres        compose-managed, PGDATA fixed (PR #2121)
  unified-redis           container on fleet-net
  daphne :8000            native, healthy
  celery + 3 workers + beat  native, healthy + new fleet_health tool

Fleet (7 Docker apps, all on fleet-net + brain bridge + workspace runtime metadata)
  mentorforge        :8002 / :5174   + brain bridge + docker block ✓
  contract-concierge :8003 / :5175   + brain bridge + docker block ✓
  pitchdeckforge     :8004 / :5176   + brain bridge + docker block ✓
  sellerpilot        :8005 / :5177   + brain bridge + docker block ✓
  dealflowtracker    :8006 / :5178   + brain bridge + docker block ✓
  signal-studio      :8007 / :5173   + brain bridge + docker block ✓ (auth-less)
  compliancesentinel :8008 / :5180   + brain bridge + docker block ✓

Routing infra
  config/fleet_agent_routing.json   — control plane
  core/services/fleet_routing.py    — pure resolver
  PA chat req/resp                  — accepts/emits routing block
  PA deliberation                   — NOT YET wired (Phase 2)

PA tools
  fleet_health           — new, read-only rollup
  active_repo_tool       — existing
  ... 100+ others
```

## What's queued for Session 1127 (Phase 2)

Per Chris at session close: "next session we can start Phase 2."

1. **Plumb `resolved_agent` into PA's deliberation router.** Today
   the routing block rides through as metadata; Rigby's intent
   detection still picks the agent. Wire it so when a fleet caller
   sends `routing.agent=legal_doc_drafter_agent` (allowlisted, hint
   mode), the PA actually dispatches there.

2. **7 fleet brain_client.py PRs.** Each app's `brain_client.ask()`
   gets optional `agent` / `role` / `mode` / `app_slug` params,
   passes them through. Each app's `POST /api/brain/ask` exposes
   the params to the frontend.

3. **Smoke test path:** open contract-concierge's Brain UI, ask a
   legal question, verify the response routing block shows
   `resolved_agent=legal_doc_drafter_agent` AND the PA actually
   routed there. That's the Phase 2 success criterion.

---

PRs: [#2123](https://github.com/clwest/donkey-betz-platform/pull/2123),
[#2124](https://github.com/clwest/donkey-betz-platform/pull/2124),
[#2125](https://github.com/clwest/donkey-betz-platform/pull/2125).
All merged to main.
