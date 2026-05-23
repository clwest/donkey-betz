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

## NEW IN SESSION 1130 — MOVE 3 ROUND 2 RECONNECT RESILIENCE

Full handoff: [`docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md`](docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md).

**Headline:** the fleet event stream no longer silently loses events on
reconnect. FleetEvent rows now carry a monotonic `seq` (Postgres
sequence), `GET /api/fleet/events/?since=<seq>` is the canonical
recovery path, the SSE `id:` field carries `seq` not UUID, and
`brain_events.py` across all 7 fleet repos drains replay before each
subscribe. TTL retention (`FLEET_EVENT_RETENTION_DAYS`, default 30)
landed alongside.

### Open PRs (8 — need merge to lock Session 1130 in)

| Repo | PR | What |
|---|---|---|
| u-d-b | [#2135](https://github.com/clwest/donkey-betz-platform/pull/2135) | seq + replay endpoint + SSE update + TTL + 18 unit tests |
| contract-concierge | [#16](https://github.com/clwest/contract-concierge/pull/16) | Canonical R2 brain_events.py — drain-then-subscribe + last_seq tracking |
| mentorforge | [#18](https://github.com/clwest/mentorforge/pull/18) | byte-identical back-prop |
| pitchdeckforge | [#17](https://github.com/clwest/pitchdeckforge/pull/17) | byte-identical back-prop |
| sellerpilot | [#11](https://github.com/clwest/sellerpilot/pull/11) | byte-identical back-prop |
| dealflowtracker | [#15](https://github.com/clwest/dealflowtracker/pull/15) | byte-identical back-prop |
| compliancesentinel | [#11](https://github.com/clwest/compliancesentinel/pull/11) | byte-identical back-prop |
| signal-studio | [#11](https://github.com/clwest/signal-studio/pull/11) | byte-identical back-prop |

All on the same `feature/fleet-events-move3-r2` branch name across
repos. Browser smoke (Test 1 + Test 2) confirmed by Chris before
commit.

### Why brain_events.py stays byte-identical across 7 repos

Same as Session 1129: ship per-app first, identical bodies, `DO NOT
EDIT EXCEPT THESE CONSTANTS` header preserved so Phase 2C can extract
into a shared package without diffing away accidental drift. Only
`DEFAULT_APP_SLUG` and the docstring's first line legitimately differ.

If you find yourself editing `brain_events.py` in any one repo, **edit
contract-concierge first, then back-prop**. Same rule applies to
`brain_client.py`.

### Docker rebuild reminder (Session 1130 hit it)

The 7 fleet apps run from `docker-compose.yml` (no volume mounts),
not `docker-compose.dev.yml`. Code changes need:

```bash
cd ~/development/<repo> && docker compose up -d --build --force-recreate <service>
```

`--build` alone often doesn't recreate the container. Verify with
`docker exec <container> wc -l /app/app/<file>.py` against the host
file.

---

## SESSION 1131 — CURRENT ENTRY POINT

> **Rigby's priority order coming out of 1130** (her standing rule:
> "auth-gate before UI for security-boundary features"):
>
> **B → D → E → F**
>
> B ranks first now that the 1130-priority A (replay) shipped. The
> signed fleet → u-d-b path is auth'd; the PA-token brain-bridge path
> still trusts whatever `app_slug` the caller claims. That gap is the
> next real security-boundary cleanup.

### FIRST THING — Merge the 8 open Session 1130 PRs + rebuild fleet

Before starting 1131 work, lock 1130 in:

1. Review + merge u-d-b [#2135](https://github.com/clwest/donkey-betz-platform/pull/2135) first (migration lives here; the 7 brain_events repos depend on the u-d-b replay endpoint being live).
2. Merge contract-concierge [#16](https://github.com/clwest/contract-concierge/pull/16) + the 6 back-prop PRs.
3. `cd ~/development/infra && make up` to pull rebuilt images for the 6 fleet apps that are still on R1 brain_events.py.
4. Verify locally: `docker exec <each-of-7> wc -l /app/app/brain_events.py` — they should all show **~312 lines** (the R2 size). R1 was ~162.
5. Re-run the smoke from the SESSION_1130 handoff (Test 1 + Test 2) just to be sure no merge regressions slipped in.

### Headline options for Session 1131 (Rigby-ordered)

#### B. Service-token auth for `app_slug` (now top priority)

**Why first.** Routing control is a security boundary, not a hint.
Today, signed fleet → u-d-b requests are auth'd; PA-token brain-bridge
requests can still claim any `app_slug`. The two paths have different
trust models and the PA-token path is the gap.

What ships:
- `allowed_app_slugs` JSONField on the PA token model (or a join
  table).
- On `/api/pa/chat/`, verify `routing.app_slug` is in the token's
  allowlist; if not, strip the routing block and log
  `override_reason="untrusted_app_slug"`.
- Back-fill migration: existing PA tokens get `["*"]` with a warning
  logged on each use until they're rotated to scoped tokens.

Existing `FleetAuthAuditLog` rows will capture the security boundary
crossings automatically.

**Brief Rigby before coding.** She'll want a clean migration path
that doesn't break existing brain-bridge callers. The default
`["*"]` for legacy tokens is the obvious starting move but she
might want a tighter posture.

Estimate: ~½ session. Touches PA token model + brain-bridge view +
routing override logic.

#### D. Wire SSE into mentorforge

Lesson generation has the same "long-running task you want to watch
live" shape as draft generation. Mirrors CC's pattern exactly:
- u-d-b emits `lesson.created` / `lesson.published` events.
- mentorforge backend: per-user `/api/lessons/events` endpoint.
- mentorforge frontend: activity strip on the relevant page.

Mostly reuse from CC. Estimate: ~½ session. Lands cleanly after B.

#### E. FC-path hint bias (Phase 2D, carryover from 1128)

u-d-b's `_run_agentic_loop` ignores `_routing_hint` when
`PA_USE_FUNCTION_CALLING=True` (prod default). Inject a system
message biasing the LLM toward the hinted agent's tool. Touches
prompt assembly — brief Rigby with the exact injection point first.

Estimate: ~⅓ session. Independent of B + D.

#### F. fleet_health → signal-studio spider feed

Deferred since Session 1126. Still independent of everything above.

**Rigby's recommendation for 1131: B alone is enough. D + E + F
remain queueable.**

### Carryovers (open / parked, not blocking)

- **ai-content-studio#2** — Docker foundation PR. Back burner.
- **24-7-ai-global** — Next.js, not yet Dockerized.
- **Per-user filter at u-d-b** — optional `?user_id=…` on the replay
  endpoint to push filtering server-side. Not done in 1130; current
  fan-out + filter in each consumer is cheaper than another index at
  current traffic.
- **DB-dependent tests** for replay ordering + TTL deletion — would
  need test DB with pgvector. Live smoke is the canonical
  verification path until that's solved.
- **context-kit doctor floor:** `10 OK / 2 warnings` (both upstream).
- **`character-os`** — Another Claude Code instance may be active there. Read-only is fine; don't push PRs there or edit their anchor docs.

### Operational notes carried forward from 1129/1130

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
- **`/api/fleet/events/*` paths are in `OPTIONAL_AUTH_PATHS`.** Signed-but-
  tokenless is the canonical fleet auth shape; the SSE and replay
  views do their own signature verification.
- **Test DB needs pgvector.** The rotation tests use it; the local
  Postgres container has it but a bare `createdb` doesn't. Manual
  smoke against the running stack remains the most reliable
  validation for fleet-auth + fleet-event changes.
- **Django 5 `db_default` is the right tool for DB-managed defaults
  on non-PK columns.** `null=True` alone makes Django pass NULL in
  INSERT and overrides the Postgres DEFAULT. Saved as a feedback
  memory.

### Recommended Rigby coordination for Session 1131

For option B (service-token auth): brief her on the migration shape
before coding. Specifically: (1) is the allowlist on the PA token
model or a separate join table; (2) what's the default for legacy
tokens — `["*"]` with a deprecation warning, or fail-closed; (3)
how should `/api/pa/chat/` log violations — strip + log, or
401-deny?

---

## SESSION 1130 — PRIOR ENTRY POINT (Move 3 R2)

Full handoff: [`docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md`](docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md).

---

## SESSION 1129 — TWO SESSIONS BACK (fleet auth + artifacts + SSE)

Full handoff: [`docs/handoffs/SESSION_1129_FLEET_BRAIN_AUTH_ARTIFACTS_EVENTS.md`](docs/handoffs/SESSION_1129_FLEET_BRAIN_AUTH_ARTIFACTS_EVENTS.md).

---

*Last overwrite: Session 1130 close, 2026-05-22.*
