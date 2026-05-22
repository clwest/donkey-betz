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
2. **`docs/PLATFORM_WHAT_IT_IS.md`** — narrative anchor (what each subsystem is + why).
3. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + source-of-truth display rules + constraint preservation. (Validated again Session 1125 — she invoked the no-claims rule unprompted.)
4. **`docs/UDB_TRANSLATION_LAYER.md`** — audience translation contract + no-claims verification rule.
5. **Archive / handoff docs** — historical unless promoted by `docs/handoffs/CURRENT.md` or this file.

Live drift checks:
- `python manage.py verify_doc_claims --only-drift`
- `.venv/bin/context-kit doctor` (expected floor: `10 OK / 2 warnings`, both upstream heuristic mismatches)
- `python scripts/verify_repo_guardrails.py`

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`) per recent commit history.

## ONE-COMMAND LAUNCH — the laptop fleet

```bash
cd ~/development/infra   # this is now its own private repo: github.com/clwest/infra
make up                  # 7 Docker fleet apps on fleet-net
make all                 # up + u-d-b natively (daphne + celery)
make status              # what's running + URLs
make down                # stop the 7 Docker apps (preserves data + u-d-b)
```

The 7 fleet apps live in their own repos with root-level `docker-compose.yml`. character-os data containers stay on fleet-net via that repo's compose. ai-content-studio is parked. 24-7-ai-global is not yet Dockerized.

## CANONICAL PA / WORKSPACE NOTES

- `POST /api/pa/chat/` is the canonical Rigby endpoint.
- `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compatibility-only shims.
- Rigby resolves `global` vs `workspace` mode from request/profile/context. Do not infer.
- Workspace Files tab supports preview, edit/save, file history.

## NEW IN SESSION 1125 — THE FLEET BRAIN BRIDGE

Every fleet app now has a `POST /api/brain/ask` endpoint and a "Brain" page in its UI that proxies freeform questions through to u-d-b's PA (Rigby).

**Where the bridge lives in each app:**

- `backend/app/brain_client.py` — identical across all 7 apps. POSTs to u-d-b `/api/pa/chat/`, polls for completion, returns `{ok, answer, intent, tool_runs, trace_id, latency_ms}`. Host header override (default `localhost`) lets Django's `ALLOWED_HOSTS` accept requests routed via `host.docker.internal`.
- `POST /api/brain/ask` — auth-gated (or open for signal-studio).
- Env vars: `BRAIN_URL`, `BRAIN_TOKEN`, `BRAIN_CONVERSATION`, plus `extra_hosts: ["host.docker.internal:host-gateway"]` in compose.
- Frontend Brain page — fit per app's `App.tsx` structure.

**Verified end-to-end live across all 7 apps, 4.7-9s round-trip.**

This is the *plumbing*. Session 1126 is about flowing real signals + agent outputs through it.

---

## SESSION 1126 — CURRENT ENTRY POINT

### What Session 1125 shipped (so you know where things stand)

Full handoff: [`docs/handoffs/SESSION_1125_DOCKER_FLEET_AND_BRAIN_BRIDGE.md`](docs/handoffs/SESSION_1125_DOCKER_FLEET_AND_BRAIN_BRIDGE.md).
TL;DR: **~25 PRs across 9 repos**. Dockerized all 7 FastAPI+React fleet apps. Brain bridge live across all 7 — each can ask Rigby and get a deliberated answer. New `infra/` private repo with `make up` launcher. u-d-b PGDATA fix (#2121) made postgres restart-safe. ai-content-studio Docker foundation PR (#2) open but parked.

### FIRST THING — Chris's directive for Session 1126

> **"Use Rigby to start connecting real-time data and Agents from u-d-b to the other apps."**

The brain bridge is plumbing. Now flow real content through it.

### Headline options for Session 1126 (ordered by leverage)

- **A. Each fleet app registered as a `ProjectWorkspace` in u-d-b** (~½ session).
  Use the existing `register_external_repo` command (or a new "running app" variant) to create a workspace row for each fleet app in u-d-b. Then Rigby has shared state across the fleet — she can see each app's surface and post deliverables/initiatives scoped to that app. **This is the foundation for everything below.**

- **B. Spider-driven signals into signal-studio** (~1 session).
  u-d-b has 80 spiders producing signals; signal-studio's domain *is* signal display. Replace its demo data with live u-d-b signal feeds — either piped on push, or signal-studio queries u-d-b on a timer. Most natural per-app integration in the fleet.

- **C. Agent-specific consult routing through the brain bridge** (~1 session).
  Today the brain bridge always reaches Rigby. Extend to specific agents:
  - mentorforge → CTOAgent / mentor-expertise agents
  - pitchdeckforge → content writers + investor pitch advisors
  - contract-concierge → legal-style agents
  - dealflowtracker → VC-pattern agents (Warren Buffett, Ray Dalio advisors)
  - sellerpilot → marketing/sales agents
  - compliancesentinel → compliance/regulatory agents
  - signal-studio → trend analysis agents

  Same bridge, optional `agent` param routes to a specific persona instead of generic Rigby.

- **D. Workspace-scoped Initiatives on app actions** (~1 session).
  When a fleet app does something meaningful (deck created, contract sent, deal moved, alert assigned), POST a deliverable / create-or-update Initiative in u-d-b's workspace for that app. Rigby surfaces cross-app state across the fleet ("3 contracts pending, 2 decks in review, 1 deal in diligence").

- **E. Service tokens** (~½ session, security hygiene).
  Currently every fleet app uses donkeyking's personal PA token via `BRAIN_TOKEN`. Generate per-app service tokens with workspace-scoped permissions on the u-d-b side. Lower-leverage but tidy.

**My recommendation: A → B (or A → D) for the leverage path. A unlocks everything else.**

### Carryovers (open / parked, not blocking)

- **ai-content-studio#2** — Docker foundation PR open. Runtime needs migration + dep reconciliation. Per Chris: "back burner."
- **24-7-ai-global** — Next.js, not yet Dockerized. Will need its own template when promoted.
- **context-kit doctor floor: `10 OK / 2 warnings`.** Both warnings are upstream heuristic mismatches; persistent.

### Architectural patterns now well-established

1. **Brain bridge.** Backend client identical across apps; frontend page fitted per `App.tsx` shape. Total ~150 backend lines + ~80 frontend lines per app.
2. **Co-authored docs (Session 1124).** Claude scaffolds structure/rules, Rigby fills voice/audience via marker-block inline replies, Claude diffs back.
3. **Defang security placeholders at source.** No more user-equals-password defaults; use `change-me-in-production` or similar.
4. **`make up` is the answer to "how do I bring everything up."** Don't write per-repo start scripts; let `infra/Makefile` orchestrate.

### Operational notes

- **u-d-b restart is now safe** (PR #2121). `docker compose down` then `up` on u-d-b's compose will preserve the postgres cluster. The brain bridge still works through the daphne native daemon over `host.docker.internal:8000`.
- **Don't dual-attach data containers to multiple networks.** If a container's host-port forwarding starts hanging, check `docker network inspect` — multi-network attachment confuses port forwarding. (Hit this with unified-postgres mid-session.)
- **Don't run parallel `docker compose build` against the same daemon.** Buildkit can lock up.
- **GitGuardian's Generic Password detector is sensitive.** Watch for `<USERNAME>=<USERNAME>` patterns in `.env.example` and compose defaults.

### Recommended Rigby coordination for Session 1126

Per the `feedback_rigby_collaboration.md` rule + the new co-author pattern: when picking up A or B, **brief Rigby first** with the plan (workspace registration scope, naming convention, what telemetry she should expose), and let her redirect before coding. The fleet brain bridge is now her surface — she'll have opinions about what should flow back.

---

## SESSION 1125 — PRIOR ENTRY POINT (Docker fleet + brain bridge)

Full handoff: [`docs/handoffs/SESSION_1125_DOCKER_FLEET_AND_BRAIN_BRIDGE.md`](docs/handoffs/SESSION_1125_DOCKER_FLEET_AND_BRAIN_BRIDGE.md).

---

## SESSION 1124 — TWO SESSIONS BACK (doctor warnings + behavior/translation layers)

Full handoff: [`docs/handoffs/SESSION_1124_DOCTOR_WARNINGS_CLEARANCE.md`](docs/handoffs/SESSION_1124_DOCTOR_WARNINGS_CLEARANCE.md).

---

*Last overwrite: Session 1125 close, 2026-05-22.*
