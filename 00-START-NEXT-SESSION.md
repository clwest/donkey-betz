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
3. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + display rules + constraints.
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

## NEW IN SESSION 1127 — FLEET ROUTING PHASE 2A LIVE

One PR. Phase 2A force-dispatch + hint bias plumbed end-to-end. See `docs/handoffs/SESSION_1127_FLEET_ROUTING_PHASE_2A.md` for the full handoff.

**Headline:** when a fleet app sends `mode=force` with a permitted + allowlisted + AGENT_MAP-resolvable agent, the PA Celery task now bypasses `UnifiedPAEntrypoint.process_message()` entirely and dispatches via `AgentRouter`. Response carries `routing.phase2_dispatched: true` so the caller can tell force actually fired. Hint mode biases the keyword path when intent detection returned no `routed_to`, never overrides positive matches.

### Where the new pieces live

| File | Role |
|---|---|
| `core/services/fleet_routing_dispatch.py` | Snake_case ↔ AGENT_MAP-key resolver, force-dispatch gate, hint deriver. |
| `core/tasks_misc.py:_impl_process_pa_chat_task` | Pre-PA force-dispatch shortcut + routing block emission. |
| `core/services/unified_pa_entrypoint.py:process_message` | Hint-mode bias for the keyword path. |
| `config/fleet_agent_routing.json` | `compliancesentinel` default flipped to null (no SecurityAgent class). |
| `tests/services/test_fleet_routing_{dispatch,config_phase2}.py` | 26 tests covering all 5 force gates, hint rules, config patch. |

### Audit signals to know about

- `routing.phase2_dispatched: true/false` in `/api/pa/chat/` response — was force actually used.
- Worker log: `[PA routing] divergence — app=X resolved_agent=Y routed_to=Z` — hint set but intent detection picked something different. Useful for tuning the allowlist.

---

## SESSION 1128 — CURRENT ENTRY POINT

### FIRST THING — Chris's directive for Session 1128

> **"Phase 2B — fleet `brain_client.py` updates (7 PRs), then either FC-path hint bias OR the SecurityAgent / compliancesentinel decision."**

Phase 2A made force/hint *actionable* in u-d-b. Phase 2B makes the fleet apps actually *send* the routing blocks. Without 2B, the new dispatch path stays inert (apps currently don't send `app_slug` or `routing`).

### Headline options for Session 1128

- **A. Fleet `brain_client.py` updates (~½ session, 7 PRs in worktree-pattern).**
  Each app's `backend/app/brain_client.py:ask()` gains optional
  `agent` / `role` / `mode` params + ships `app_slug` automatically. Each
  app's `POST /api/brain/ask` exposes those params to the frontend.
  Each frontend Brain page gains a role-select dropdown.

  Success criterion: open contract-concierge's Brain page → pick "Legal
  drafter (force)" → response carries `routing.phase2_dispatched: true`
  and `routed_to: "LegalDocDrafterAgent"`.

- **B. FC-path hint bias (~⅓ session).**
  Inject a system message into `_run_agentic_loop` when `_routing_hint`
  is set, biasing GPT-5.2 toward calling the hinted agent's tool. Adds
  hint coverage to the FC path; today only the keyword path uses hints.

- **C. SecurityAgent decision for compliancesentinel.**
  Either add a real `SecurityAgent` class (audit + compliance reasoning,
  feed from MemoryIsolationAgent + audit findings) or remap
  `compliancesentinel` default to an existing concrete agent. Rigby's
  call — flag her before picking.

- **D. fleet_health → spider-driven signals into signal-studio**
  (still deferred from Session 1126). Independent of A/B/C.

**Recommendation: A first (unlocks 2A's actual usefulness). Then
either B or C as time permits.**

### Carryovers (open / parked, not blocking)

- **ai-content-studio#2** — Docker foundation PR. Per Chris: back burner.
- **24-7-ai-global** — Next.js, not yet Dockerized.
- **context-kit doctor floor: `10 OK / 2 warnings`** (both upstream).
- **Service-token verification for `app_slug`** (Phase 2C) — today any
  PA-token caller can claim any `app_slug`. Mitigated by allowlist +
  force_allowed gates; production hardening is a separate PR.

### Operational notes

- **`config/fleet_agent_routing.json` is cached.** `fleet_routing._load_config`
  is `lru_cache(maxsize=1)`. Edits require a restart (or
  `_load_config.cache_clear()` in tests/dev).
- **`SNAKE_TO_AGENT_MAP_KEY` is the source of truth** for snake_case ↔
  AGENT_MAP-key resolution (handles acronyms). If you add a new agent
  to `allowlists` in the JSON config, also add a row to that dict in
  `core/services/fleet_routing_dispatch.py`.

### Recommended Rigby coordination for Session 1128

She co-designed Phase 2A and reviewed the safety hatches. For 2B
(`brain_client.py` updates across 7 repos), her likely concerns:

- Whether to ship one canonical `brain_client.py` shared across apps
  (single source of truth) vs per-app copies (current model).
- Frontend role-select UX — what set of roles to expose; what default
  per app.
- Defaults vs "stay in PA intent" toggle — should the role select
  default to "PA chooses" or to the app's default agent?

---

## SESSION 1127 — PRIOR ENTRY POINT (fleet routing Phase 2A)

Full handoff: [`docs/handoffs/SESSION_1127_FLEET_ROUTING_PHASE_2A.md`](docs/handoffs/SESSION_1127_FLEET_ROUTING_PHASE_2A.md).

---

## SESSION 1126 — TWO SESSIONS BACK (fleet runtime + routing Phase 1)

Full handoff: [`docs/handoffs/SESSION_1126_FLEET_RUNTIME_BRAIN_PLUMBING.md`](docs/handoffs/SESSION_1126_FLEET_RUNTIME_BRAIN_PLUMBING.md).

---

*Last overwrite: Session 1127 close, 2026-05-22.*
