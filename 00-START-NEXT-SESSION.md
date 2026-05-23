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

## NEW IN SESSION 1129 — FLEET AUTH + ARTIFACTS + SSE EVENT STREAM

Five movements landed this session. Full handoff:
[`docs/handoffs/SESSION_1129_FLEET_BRAIN_AUTH_ARTIFACTS_EVENTS.md`](docs/handoffs/SESSION_1129_FLEET_BRAIN_AUTH_ARTIFACTS_EVENTS.md).

**Headline:** every fleet → u-d-b call is now HMAC-SHA256 signed (Move 1). Fleet apps can persist work-product as artifacts with TTL retention (Move 2 R1+R2). Contract Concierge has a real "AI Draft Library" flow live in the running stack. u-d-b emits lifecycle events; CC streams them to the browser via two SSE hops (Move 3 R1).

### Open PRs (need merge to lock Session 1129 in)

| Repo | PR | What |
|---|---|---|
| u-d-b | [#2133](https://github.com/clwest/donkey-betz-platform/pull/2133) | Move 3 R1 — SSE event stream MLC |
| contract-concierge | [#15](https://github.com/clwest/contract-concierge/pull/15) | Live SSE activity feed + per-user filter |
| mentorforge | [#17](https://github.com/clwest/mentorforge/pull/17) | brain_events subscriber back-prop |
| pitchdeckforge | [#16](https://github.com/clwest/pitchdeckforge/pull/16) | brain_events subscriber back-prop |
| sellerpilot | [#10](https://github.com/clwest/sellerpilot/pull/10) | brain_events subscriber back-prop |
| dealflowtracker | [#14](https://github.com/clwest/dealflowtracker/pull/14) | brain_events subscriber back-prop |
| compliancesentinel | [#10](https://github.com/clwest/compliancesentinel/pull/10) | brain_events subscriber back-prop |
| signal-studio | [#10](https://github.com/clwest/signal-studio/pull/10) | brain_events subscriber back-prop |

Move 1 + Move 2 PRs from earlier in the session (#2129, #2130, #2131, #2132, CC #12, CC #13, CC #14, and back-prop stacks) are already merged.

### Why brain_client.py AND brain_events.py are intentionally copy-pasted

Per Rigby's standing signoff: ship per-app first, identical bodies, "DO NOT EDIT EXCEPT THESE CONSTANTS" header so a future round (Phase 2C) can extract into a shared package without diffing away accidental drift. Only `DEFAULT_APP_SLUG` and the docstring's first line legitimately differ between copies.

If you find yourself editing either file in any one repo, **edit contract-concierge first, then back-prop**. Propagation helpers:
- `/tmp/propagate_brain_client.py`
- `/tmp/propagate_brain_events.py`

Both get cleared on reboot; recreate from the canonical source if needed.

---

## SESSION 1130 — CURRENT ENTRY POINT

> **Rigby's Session 1130 priority order (her standing rule: "auth-gate
> before UI for security-boundary features"):** Move 3 R2 (replay + per-
> user filter at u-d-b) → service-token auth for app_slug → FleetEvent
> retention → wire SSE into one other fleet app → FC-path hint bias.
>
> Replay ranks above auth because: today's MLC drops events on every
> reconnect, and reconnect happens any time the browser tab loses focus
> on iOS. Without replay, the activity strip silently lies about
> "everything that's happened" — that's a worse UX foot-gun than the
> auth gap (which has u-d-b's allowlist + force_allowed gates as
> mitigation).

### FIRST THING — Verify Session 1129 PRs merged + e2e smoke

Before starting 1130 work, confirm the 8 open PRs from 1129 are on
`main` in each repo, then run the live SSE end-to-end:

1. `cd ~/development/infra && make up` (or `make all` for u-d-b natively too)
2. Log into Contract Concierge as `chris@donkeybetz.com` at http://localhost:5175
3. Open the **Drafts** tab. The activity strip should show "Live —
   connected to Rigby brain stream" with an emerald dot within ~2s.
4. Click **New draft** → fill in (NDA / parties / Colorado / 2 years) →
   Generate. The new draft should appear in the activity strip as
   `created` within ~10-30s, and the library list should auto-refresh.

If any of those fail, debug before moving on — the Session 1130
priorities all assume Move 3 R1 is working.

### Headline options for Session 1130 (Rigby-ordered)

#### A. Move 3 Round 2 — replay + per-user filter at u-d-b

**Why first.** MLC works while connected; reconnection drops every
event that happened during the gap. iOS / mobile / tab-switch users
silently lose activity. Worse failure mode than the auth gap.

What ships:
- `GET /api/fleet/events/?since=<event_id>&limit=100` — replay from
  `FleetEvent` rows. Signed (fleet auth class). Auto-scoped to
  caller's `app_slug`.
- Optional `?user_id=...` query for u-d-b-side per-user filtering
  (cheaper than fan-out + filter in every consuming app — Rigby will
  want to weigh DB-side filter vs. consumer-side filter trade-off).
- `Last-Event-ID` header support on `/api/fleet/events/stream` so
  reconnecting clients pick up where they left off.
- Frontend (CC): when EventSource fires `onerror` then reconnects,
  send `?since=<last seen event_id>` to replay missed events.

Brief Rigby with the replay query shape before coding. She'll want
to lock event_id ordering semantics (timestamp tiebreak, gap-detection
rules) up front.

Estimate: ~⅓ session.

#### B. Service-token auth for `app_slug` (carryover from 1128 option A)

**Why second.** Routing control is a security boundary now, not a
hint. Today, signed fleet → u-d-b requests are auth'd; PA-token
brain-bridge requests can still claim any `app_slug`. The two paths
have different trust models.

Bind PA tokens to one-or-more allowed `app_slug` values. Add
`allowed_app_slugs` JSONField on the PA token model (or a join
table). On `/api/pa/chat/`, verify `routing.app_slug` is in the
token's allowlist; if not, strip the routing block and log
`override_reason="untrusted_app_slug"`.

Existing `FleetAuthAuditLog` rows will capture the security
boundary crossings automatically.

Estimate: ~½ session. Touches PA token model + brain-bridge view +
routing override logic.

#### C. FleetEvent retention (quick win)

Borrow Move 2 R2's pattern: add `expires_at` + cleanup beat task to
`FleetEvent`. Default TTL = 30 days (Rigby's call — confirm before
shipping). Reuse the cleanup primitive in
`core/services/fleet_artifact_cleanup.py` rather than duplicating.

Estimate: ~⅙ session. Can land alongside A.

#### D. Wire SSE into one other fleet app

mentorforge is the natural pick — lesson generation has the same
"long-running task you want to watch live" shape as draft generation.
Mirrors CC's pattern exactly:
- u-d-b emits `lesson.created` / `lesson.published` events.
- mentorforge backend: per-user `/api/lessons/events` endpoint.
- mentorforge frontend: activity strip on the relevant page.

Mostly reuse. Estimate: ~½ session.

#### E. FC-path hint bias (Phase 2D, carryover from 1128)

u-d-b's `_run_agentic_loop` ignores `_routing_hint` when
`PA_USE_FUNCTION_CALLING=True` (prod default). Inject a system
message biasing the LLM toward the hinted agent's tool. Touches
prompt assembly — brief Rigby with the exact injection point first.

Estimate: ~⅓ session. Independent of A-D.

#### F. fleet_health → signal-studio spider feed

Deferred since Session 1126. Still independent of everything above.

**Rigby's recommendation: A + C in same session, then B, then D in
Session 1131.**

### Carryovers (open / parked, not blocking)

- **ai-content-studio#2** — Docker foundation PR. Back burner.
- **24-7-ai-global** — Next.js, not yet Dockerized.
- **context-kit doctor floor:** `10 OK / 2 warnings` (both upstream).
- **`character-os`** — Another Claude Code instance may be active there. Read-only is fine; don't push PRs there or edit their anchor docs.

### Operational notes

- **`brain_events.py` is byte-identical across all 7 fleet repos.**
  Edit contract-concierge first, then back-prop. Same rule as
  `brain_client.py`.
- **EventSource is browser-only.** The 2-hop pattern is: u-d-b emits
  → fleet backend subscribes (signed, server-to-server) → fleet
  backend re-emits to browser (user-session, token in query). Don't
  point a browser directly at u-d-b's SSE; auth model doesn't fit.
- **Token-in-query for SSE auth.** EventSource can't set custom
  headers. JWT goes as `?token=...`. Same `SECRET_KEY` + `ALGORITHM`
  as `decode_token`. Same trust model — short-lived, same-origin.
- **Daphne + sync generator + Redis pub/sub = hang.** If you write a
  new SSE endpoint, use `async def event_generator` + `redis.asyncio`
  (see `core/services/fleet_events.asubscribe_events`). The sync
  variant blocks daphne's event loop and makes the server
  unresponsive after one disconnect.
- **Docker rebuild gotcha.** `docker compose up -d --build <service>`
  doesn't always re-create the container — use `--force-recreate`
  when you need the new code to actually run.
- **`/api/fleet/events/` is in `OPTIONAL_AUTH_PATHS`.** Signed-but-
  tokenless is the canonical fleet auth shape; the SSE view does its
  own signature verification.
- **Test DB needs pgvector.** The rotation tests use it; the local
  Postgres container has it but a bare `createdb` doesn't. Manual
  smoke against the running stack remains the most reliable
  validation for fleet-auth changes.

### Recommended Rigby coordination for Session 1130

For Move 3 R2 (option A): lock event_id ordering semantics before
coding. Specifically: (1) is timestamp + uuid the tiebreak, or
something more deterministic; (2) what's the gap-detection rule on
reconnect — strict (replay all events `> last_seen`) or fuzzy
(replay last N + dedupe client-side); (3) should the SSE endpoint
auto-replay on `Last-Event-ID` or require the client to explicitly
GET the replay endpoint first.

For service-token auth (option B): she'll want a clean migration
path. The PA token model has a lot of existing rows; back-filling
`allowed_app_slugs` needs a default that doesn't break existing
brain-bridge callers (probably `["*"]` for legacy tokens, with a
warning logged on each use until they're rotated to a scoped
token).

---

## SESSION 1129 — PRIOR ENTRY POINT (fleet auth + artifacts + SSE)

Full handoff: [`docs/handoffs/SESSION_1129_FLEET_BRAIN_AUTH_ARTIFACTS_EVENTS.md`](docs/handoffs/SESSION_1129_FLEET_BRAIN_AUTH_ARTIFACTS_EVENTS.md).

---

## SESSION 1128 — TWO SESSIONS BACK (fleet brain bridge sends routing)

Full handoff: [`docs/handoffs/SESSION_1128_FLEET_BRAIN_BRIDGE_ROUTING.md`](docs/handoffs/SESSION_1128_FLEET_BRAIN_BRIDGE_ROUTING.md).

---

*Last overwrite: Session 1129 close, 2026-05-22.*
