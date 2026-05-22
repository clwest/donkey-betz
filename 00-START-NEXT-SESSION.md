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

## NEW IN SESSION 1128 — FLEET ROUTING WIRE LIVE

Seven PRs. Fleet apps now actually send routing blocks to u-d-b. See `docs/handoffs/SESSION_1128_FLEET_BRAIN_BRIDGE_ROUTING.md` for the full handoff.

**Headline:** every fleet app's `/api/brain/ask` accepts optional `agent` / `role` / `mode` and forwards them as a `routing` block to u-d-b's `/api/pa/chat/`. Every call now also sends `context.app_slug` (canonical location) and an auto-generated `context.request_id` for trace joining. Responses surface u-d-b's routing decision (including `phase2_dispatched: true/false`).

| Repo | PR |
|---|---|
| contract-concierge (reference) | [#10](https://github.com/clwest/contract-concierge/pull/10) |
| mentorforge | [#13](https://github.com/clwest/mentorforge/pull/13) |
| pitchdeckforge | [#12](https://github.com/clwest/pitchdeckforge/pull/12) |
| sellerpilot | [#6](https://github.com/clwest/sellerpilot/pull/6) |
| dealflowtracker | [#10](https://github.com/clwest/dealflowtracker/pull/10) |
| compliancesentinel | [#6](https://github.com/clwest/compliancesentinel/pull/6) |
| signal-studio | [#6](https://github.com/clwest/signal-studio/pull/6) |

**Depends on u-d-b PR #2127 (Phase 2A) being merged first** — that's what gives the dispatch a response to send back.

### Wire shape additions (canonical)

Outbound (fleet app → u-d-b):
- `context.app_slug` (always)
- `context.request_id` (always, auto-generated)
- `routing` (only when caller passed mode/agent/role)

Inbound (u-d-b → fleet app, response):
- `routing.phase2_dispatched: bool` — was force actually used
- `routing.routed_to` — AGENT_MAP key that actually ran
- `routing.was_overridden` / `override_reason` — when resolution downgraded

### Why brain_client.py is intentionally copy-pasted across 7 repos

Per Rigby's signoff: ship per-app first, identical bodies, "DO NOT EDIT EXCEPT THESE CONSTANTS" header so Phase 2C can extract into a shared package without diffing away accidental drift. Only `DEFAULT_APP_SLUG` and the docstring's first line legitimately differ between copies.

If you find yourself editing `brain_client.py` in any one repo, **edit contract-concierge first, then back-prop**. The propagation helper script that did the original copy is at `/tmp/propagate_brain_client.py` (recreate if cleared).

---

## SESSION 1129 — CURRENT ENTRY POINT

> **Rigby's Session 1129 priority order (her review of Session 1128
> close):** verify #2127 merge → service-token auth → observability →
> compliancesentinel decision stub → THEN frontend. Routing control
> without auth is the only thing that can turn into a real incident,
> so it ranks above visible UI work.
>
> **Implement-from-this spec lives at
> [`docs/specs/FLEET_MOVE_1_AND_2_SPEC.md`](docs/specs/FLEET_MOVE_1_AND_2_SPEC.md).**
> Full Move 1 (service identity + signed requests) and Move 2 (artifact
> push/pull) contracts — models, headers, signature scheme, capability
> gates, failure codes, audit log shape, bootstrap + rotation flow,
> push/pull endpoints, edge cases for versioning/citations/attribution/
> retention. Drafted by Rigby in conversation `pa-d19c1674b936`. If you
> find yourself making a judgment call that isn't in the spec, brief
> her before coding.

### FIRST THING — Merge dependency + e2e verification checklist

Phase 2B PRs are inert without u-d-b PR #2127 (Phase 2A) on `main`.

1. **Confirm #2127 is merged** to u-d-b `main` in the prod/local target.
2. **Run true e2e from a force_allowed app.** Either contract-concierge
   or signal-studio is fine — both have `force_allowed=true` in
   `config/fleet_agent_routing.json`. Example:

   ```bash
   curl -X POST http://localhost:8003/api/brain/ask \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "draft a 1-page NDA",
       "mode": "force",
       "agent": "legal_doc_drafter_agent"
     }'
   ```

3. **Verify all routing fields land** in the response: `requested` /
   `resolved_agent` / `routed_to` / `was_overridden` / `override_reason`
   / `phase2_dispatched`.

### Headline options for Session 1129 (Rigby-ordered)

- **A. Service-token verification for `app_slug` — highest-risk gap.**
  Today any PA-token caller can claim any `app_slug`. Mitigated by the
  server-side allowlist + `force_allowed` gates, but routing control
  without auth is the one thing that can turn into a real incident.
  Bind PA tokens to one-or-more allowed `app_slug` values; reject at
  view layer. Add an explicit audit log line when routing is ignored
  due to auth failure: `override_reason="untrusted_app_slug"`.

  **This ranks above the frontend dropdown** — Rigby's call. Routing
  is a security boundary now, not a hint.

- **B. Observability — one metric + one log line.**
  Add a counter `fleet_routing.force_dispatch.count` tagged by
  `app_slug` + `agent`. WARN when `resolved_agent` exists but
  `routed_to` diverges (catches fallback or dispatch failure). This
  is the cheapest way to learn what the new dispatch path is
  actually doing in the wild.

  Estimate: ~⅙ session. Can land alongside A.

- **C. Compliancesentinel — decision STUB (don't pick yet).**
  Keep defaults `null` for now. Drop a short decision note into the
  handoff: "SecurityAgent: build vs map to existing compliance-capable
  agent vs leave unpinned." Lock the question so it doesn't get
  re-litigated mid-session.

- **D. Frontend role-select dropdown (Phase 2B.2).**
  Per-app Brain-page dropdown ("PA chooses" / "Legal drafter (force)"
  / "Trend analyst (hint)"). 7 PRs in worktree-pattern. Role list
  comes from u-d-b's `config/fleet_agent_routing.json` allowlists
  but Rigby will want to filter which roles are exposed to users
  (some are internal-only). Defer to AFTER service-token auth (A).

  Estimate: ~½ session.

- **E. FC-path hint bias (Phase 2D).**
  u-d-b's `_run_agentic_loop` (GPT-5.2 function calling) currently
  ignores `_routing_hint`. When `PA_USE_FUNCTION_CALLING=True` (prod
  default), hints have no effect. Inject a system message biasing
  the LLM toward the hinted agent's tool. Touches prompt assembly —
  brief Rigby with the exact injection point first.

  Estimate: ~⅓ session.

- **F. fleet_health → signal-studio spider feed** (deferred since
  Session 1126). Independent of A-E.

**Rigby's recommendation: A + B in same session, then C (just the
stub), then D in Session 1130.**

### Carryovers (open / parked, not blocking)

- **u-d-b PR #2127** — Phase 2A; needs merge before 2B PRs are useful.
- **ai-content-studio#2** — Docker foundation PR. Per Chris: back burner.
- **24-7-ai-global** — Next.js, not yet Dockerized.
- **context-kit doctor floor:** `10 OK / 2 warnings` (both upstream).

### Operational notes

- **`brain_client.py` is byte-identical across all 7 repos** (modulo
  `DEFAULT_APP_SLUG` and the docstring header). If you edit one, edit
  the reference in contract-concierge first, then back-prop.
- **Test files set `BRAIN_TOKEN` + `DATABASE_URL` envvars** before
  importing the app (SQLAlchemy engine constructs at module load).
  New tests must follow this pattern.
- **Routing block is opt-in.** Bare `/api/brain/ask` POSTs (no
  mode/agent/role) behave exactly like pre-2B — no surprise
  routing.
- **`request_id` is auto-generated** if the caller doesn't pass one;
  it's threaded into `context.request_id` and returned in the
  response for trace joining.

### Recommended Rigby coordination for Session 1129

For frontend dropdown (option A): she'll want to see the role list per
app. Quick mock the dropdown structure (default + 2-3 roles per app)
and ask her to validate before coding. The role list should come
from u-d-b's `config/fleet_agent_routing.json` allowlists — but she'll
have a view on which to *expose to users* (some are internal-only).

For FC-path hint bias (option B): brief her with the exact spot in
`_run_agentic_loop` that the system message gets injected. She'll
likely want a safety hatch like the keyword path got ("hint never
overrides positive intent" — the FC equivalent is "hint never
overrides the LLM picking a different tool autonomously").

---

## SESSION 1128 — PRIOR ENTRY POINT (fleet brain bridge sends routing)

Full handoff: [`docs/handoffs/SESSION_1128_FLEET_BRAIN_BRIDGE_ROUTING.md`](docs/handoffs/SESSION_1128_FLEET_BRAIN_BRIDGE_ROUTING.md).

---

## SESSION 1127 — TWO SESSIONS BACK (fleet routing Phase 2A)

Full handoff: [`docs/handoffs/SESSION_1127_FLEET_ROUTING_PHASE_2A.md`](docs/handoffs/SESSION_1127_FLEET_ROUTING_PHASE_2A.md).

---

*Last overwrite: Session 1128 close, 2026-05-22.*
