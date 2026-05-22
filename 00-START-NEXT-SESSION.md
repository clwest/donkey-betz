# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. If you don't override `PA_API_URL`, every call goes to prod. The `.env` file's `PA_API_TOKEN` is also the **production** token.

### The correct LOCAL invocation
```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=<local-donkeyking-token>      \
.venv/bin/python tools/pa_chat.py "message" --conversation <id>
```

**Before your first `pa_chat.py` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation; use that if you don't want to remember the env vars.

## SOURCE OF TRUTH

1. **`docs/PLATFORM_INVENTORY.md`** — runtime facts (counts, schedules, agents, spiders). Regenerate with `python manage.py generate_platform_inventory`.
2. **`docs/PLATFORM_WHAT_IT_IS.md`** — narrative anchor.
3. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + display rules + constraints. **Validated 3x now** (Sessions 1124, 1125, 1126 — she's auto-redacting and invoking no-claims rule unprompted; sometimes over-cautious on public-domain demo creds).
4. **`docs/UDB_TRANSLATION_LAYER.md`** — audience contract + no-claims rule.
5. **Archive / handoff docs** — historical unless promoted by `docs/handoffs/CURRENT.md` or this file.

Live drift checks:
- `python manage.py verify_doc_claims --only-drift`
- `.venv/bin/context-kit doctor` — **expected floor: `10 OK / 2 warnings`** (both upstream).
- `python scripts/verify_repo_guardrails.py`

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`).

## ONE-COMMAND LAUNCH — the laptop fleet

```bash
cd ~/development/infra   # private repo: github.com/clwest/infra
make up                  # 7 Docker fleet apps on fleet-net
make all                 # up + u-d-b natively (daphne + celery)
make status              # what's running + URLs
```

## CANONICAL PA / WORKSPACE NOTES

- `POST /api/pa/chat/` is the canonical Rigby endpoint.
- `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compat shims only.
- Rigby resolves `global` vs `workspace` mode from request/profile/context.
- **PA tool registration needs BOTH daphne AND celery restart.** Each celery worker loads its own tool registry. `pkill -f "daphne -b 127.0.0.1 -p 8000"; pkill -f "celery -A core"; make start && make celery`.

## NEW IN SESSION 1126 — FLEET RUNTIME + ROUTING

Three PRs landed:

- **PR #2123** — Docker runtime metadata block in each fleet repo profile. Rigby sees web URL, API URL, brain bridge endpoint, fleet-net hostnames, healthchecks per app. `register_external_repo` markdown serializer was patched to surface the block in the pinned Repo Profile deliverable.

- **PR #2124** — `fleet_health` rollup. New mgmt command + new PA tool, shared `probe_fleet()` function. Rigby can answer "what's broken in the fleet right now?" in ~2 seconds.

- **PR #2125** — **Phase 1** of agent-specific consult routing. Control plane (`config/fleet_agent_routing.json`) + pure resolver (`core/services/fleet_routing.py:resolve()`) + PA chat accepts/emits structured `routing` block. **METADATA pipeline only — Phase 2 wires `resolved_agent` into PA's deliberation router.**

### Routing — where it lives

- **Config:** `config/fleet_agent_routing.json` — defaults / roles / allowlists / force_allowed per app.
- **Resolver:** `core/services/fleet_routing.py:resolve(app_slug, routing_block)` → `RoutingDecision`. Pure function, lru_cache'd. Hint vs force semantics: hint downgrades to default if not allowlisted; force only honored if `force_allowed[app_slug]==true` AND allowlisted, else downgrades with `was_overridden=true`.
- **Request shape** (new fields on `/api/pa/chat/` payload):
  ```json
  {
    "message": "...",
    "app_slug": "contract-concierge",
    "routing": {"mode": "hint", "agent": "legal_doc_drafter_agent", "role": null}
  }
  ```
- **Response shape** (new `routing` block):
  ```json
  {
    "routing": {
      "app_slug": "...", "requested": {...}, "default_agent": "...",
      "resolved_agent": "...", "routed_to": "...",
      "allowlist_hit": true, "force_permitted": true,
      "was_overridden": false, "override_reason": null
    }
  }
  ```

---

## SESSION 1127 — CURRENT ENTRY POINT

### What Session 1126 shipped (so you know where things stand)

Full handoff: [`docs/handoffs/SESSION_1126_FLEET_RUNTIME_BRAIN_PLUMBING.md`](docs/handoffs/SESSION_1126_FLEET_RUNTIME_BRAIN_PLUMBING.md).

TL;DR: 3 PRs (#2123 #2124 #2125). Workspaces existed from Session 1119; reframed Option A as runtime-metadata-extension. Docker block per repo profile. `fleet_health` rollup mgmt+tool. Phase 1 routing infra. Rigby co-designed each.

### FIRST THING — Chris's directive for Session 1127

> **"Phase 2 — plumb resolved_agent into PA's deliberation router, then update each fleet app's brain_client to send routing."**

Phase 1 made routing decisions observable. Phase 2 makes them *actionable*.

### Headline options for Session 1127

- **A. Phase 2 plumb (u-d-b side, ~½ session).**
  Patch `core/services/unified_pa_entrypoint.py` to look at `context.routing` and, when `resolved_agent` is set, bias the PA's intent detection / router toward that agent. Probably: if mode is `force` + `force_permitted` + `allowlist_hit`, dispatch directly via AgentRouter (bypass PA's intent detection). If mode is `hint`, pass `resolved_agent` as a system-prompt hint or routing preference into PA's normal loop.

  Success criterion: `contract-concierge force legal_doc_drafter_agent` → response `routed_to == "LegalDocDrafterAgent"` (or whatever the AGENT_MAP key resolves to), not whatever PA's intent picker chose.

- **B. Fleet brain_client updates (7 PRs, ~½ session).**
  Each app's `backend/app/brain_client.py:ask()` gains optional `agent` / `role` / `mode` params + `app_slug` sent via the `routing` block to u-d-b. Each app's `POST /api/brain/ask` exposes these to the frontend. Then the Brain page UI gains a role-select dropdown.

  These can land before or after A — each adds the optional fields without requiring the deliberation hook to be wired.

- **C. fleet_health → spider-driven signals into signal-studio (deferred from Session 1126).**
  Pipe u-d-b's spider signals into signal-studio's database, replace its demo data with live data. Most natural per-app integration. Independent of A/B.

**My recommendation: A → B in same session.** A is the smaller change but unlocks B's actual usefulness (apps sending routing blocks that don't dispatch are decorative). C is independent and can slot in either order.

### Carryovers (open / parked, not blocking)

- **ai-content-studio#2** — Docker foundation PR open. Runtime needs migration + dep reconciliation. Per Chris: "back burner."
- **24-7-ai-global** — Next.js, not yet Dockerized. Different template needed.
- **context-kit doctor floor: `10 OK / 2 warnings`** (both upstream).

### Architectural patterns now well-established

1. **Brain bridge** — `~150 backend + ~80 frontend lines/app`, shared brain_client.py
2. **Co-authored docs** (1124) — Claude scaffolds, Rigby fills via marker-block inline replies
3. **Defang security placeholders at source** — no user-equals-password defaults
4. **make up** is the answer to "bring everything up"
5. **NEW Phase-1-metadata-first** (1126) — ship observability before action. Lets you iterate on resolution logic with real traffic before risking dispatch.

### Operational notes

- **u-d-b restart is safe** (PR #2121 PGDATA fix). `docker compose down`+`up` on u-d-b's postgres preserves the cluster.
- **PA tool changes need BOTH daphne AND celery restart** — each celery worker has its own loaded tool registry.
- **`register_external_repo` markdown serializer must keep pace with the JSON shape.** If you add a new field to the config, patch `_render_repo_profile_markdown()` in the same PR.
- **Workspaces already exist for all 12 fleet repos.** Don't re-create; extend.
- **`config/fleet_agent_routing.json` is the single source of truth** for which apps can talk to which agents.

### Recommended Rigby coordination for Session 1127

She's been co-designing the routing infrastructure since the brief; she has strong opinions on hint/force semantics + the allowlist contract. Before coding the Phase 2 dispatch, brief her with **exactly which file/function will branch on `resolved_agent`** and how. Likely she'll want:

- A clean separation between "PA route by intent" and "PA route by hint" paths
- Audit logging when `routed_to != resolved_agent` (so we can see when PA's intent detection diverged from the resolution)
- A safety hatch: never let `mode=hint` override a security-sensitive default

---

## SESSION 1126 — PRIOR ENTRY POINT (fleet runtime + routing Phase 1)

Full handoff: [`docs/handoffs/SESSION_1126_FLEET_RUNTIME_BRAIN_PLUMBING.md`](docs/handoffs/SESSION_1126_FLEET_RUNTIME_BRAIN_PLUMBING.md).

---

## SESSION 1125 — TWO SESSIONS BACK (Docker fleet + brain bridge)

Full handoff: [`docs/handoffs/SESSION_1125_DOCKER_FLEET_AND_BRAIN_BRIDGE.md`](docs/handoffs/SESSION_1125_DOCKER_FLEET_AND_BRAIN_BRIDGE.md).

---

*Last overwrite: Session 1126 close, 2026-05-22.*
