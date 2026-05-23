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

## SESSION 1131 LANDED — signal-studio drinks from the real fleet pipe

Full handoff: [`docs/handoffs/SESSION_1131_SIGNAL_STUDIO_PHASE_1.md`](docs/handoffs/SESSION_1131_SIGNAL_STUDIO_PHASE_1.md).

**Headline:** signal-studio went from 5 hardcoded seeds to **131 real
clusters** (5 seed + 126 upstream). Live SSE updates land in ~3s.
Quality bar locked by Rigby: `status=active AND cluster_size>=3 AND
strength>=0.6`. HANDLERS prefix router shipped per Rigby's lock C.
2 PRs open: u-d-b [#2138](https://github.com/clwest/donkey-betz-platform/pull/2138) +
signal-studio [#12](https://github.com/clwest/signal-studio/pull/12).

**Visual diff for Chris:** open `http://localhost:5173`. Real cluster
titles ("React demand spike", "Marketing sentiment shift", "AI
emerging trend") replace the 5 hardcoded seeds.

**Burned-in gotcha (saved to memory):** Fleet HMAC clients sign with
`SHA256(raw_secret).hexdigest()`, not the raw secret. Symptom is 401
`signature_mismatch`. Reference impl: `contract-concierge/backend/app/fleet_signer.py:141`.

---

## SESSION 1132 — CURRENT ENTRY POINT (signal-studio Phase 2: SignalCuratorAgent)

> **Carry-over from 1131:** Rigby's path C — the curated ranking
> layer on top of what Phase 1 shipped. The pull endpoint + emit +
> live consumer is the firehose; Phase 2 turns the 126-cluster feed
> into a curated experience.

### FIRST THING — Sanity check before coding

1. `cd ~/development/infra && make up`
2. `make all` (or `make start && make celery` from u-d-b)
3. `curl http://localhost:8007/api/signals | jq '.total'` should be `131`-ish (5 seed + N real). If it's still 5, Phase 1 isn't running — check `FLEET_SERVICE_SECRET` is set in signal-studio's container env (`docker exec signal_studio_api env | grep FLEET`).
4. Visual check: `localhost:5173` shows real cluster titles, not the 5 hardcoded seeds.

If anything is off, debug Phase 1 before starting Phase 2.

### Phase 2 — SignalCuratorAgent layer (Rigby's "C")

**Estimate:** ~1 day for the agent + handler + Curated tab.

#### Step 1 (u-d-b): SignalCuratorAgent

Where to wire it in:
- New agent class — likely `core/agents/signal_curator_agent.py`
- Register in `AGENT_MAP` (governor-eligible, rate-limited daily)
- Beat schedule entry: once daily, say 6 AM MST

What it does:
- Pulls all clusters with `status=active AND strength>=0.6` (the
  Phase 1 quality-bar set — same predicate as the pull endpoint)
- Scores each by composite: starter formula
  `0.5*strength + 0.3*size_normalized + 0.2*recency_decay` (Rigby
  should lock the weights based on actual distribution shape — brief
  her with a recency-weighted histogram before coding)
- Picks Top 5–10
- Persists curated artifact set (see Step 2 for storage shape)
- Emits `signal.curated_published` with the curated list as payload

#### Step 2 (u-d-b): curated persistence

Two options to brief with Rigby:

**(a)** Separate ORM type (`CuratedSignalSnapshot`?) — cleaner
long-term, requires new table + migration. Each daily run writes a
new snapshot row; historical curated lists are queryable.

**(b)** Boolean + score on `SignalCluster` — simpler, one column
add (`curated_score: float`, indexed). Curated set = `ORDER BY
curated_score DESC LIMIT 10`. No history — last run wins.

I lean (a) but (b) ships faster. Rigby's call.

#### Step 3 (u-d-b): emit `signal.curated_published`

Payload should mirror the cluster envelope shape from Phase 1 (so
the consumer's HANDLERS router can reuse `_handle_signal_event`'s
upsert path with minimal branching) BUT include a `curated_score`
field and ideally a snapshot id.

Same fleet-event mechanism as `signal.cluster_promoted` — call
`emit_event(event_type="signal.curated_published", app_slug="signal-studio", payload={...})`.

#### Step 4 (signal-studio): handler + Curated tab

- **Handler**: in `app/signal_ingest.py`, add a new tuple to the
  HANDLERS list. The router already routes anything `signal.*` to
  `_handle_signal_event` — split that into per-event-type branches
  (or add a new `_handle_signal_curated_event` and route by exact
  match before the prefix). Rigby's choice when she sees the
  envelope shape.
- **Storage**: a `curated_score` column on `SignalCluster` (cheapest)
  OR a new `CuratedSnapshot` ORM type if she chose (a) above.
- **UI**: new Curated tab in the React frontend alongside the
  existing signal list. Renders top 10 by `curated_score`.

#### Step 5: smoke

- Trigger SignalCuratorAgent manually via Django shell
- Confirm `signal.curated_published` lands in signal-studio (the
  HANDLERS router fires; new column / table populated)
- UI: Curated tab shows 5–10 ranked clusters

### Lower-priority cleanup (defer further if Phase 2 is the focus)

- **Evidence URL field** — Phase 1 ships `url=""` because
  `SignalCluster.sample_signals` has no URL column. Options: extend
  `sample_signals` upstream OR wait for SignalCuratorAgent to do
  enrichment (cleaner path). Phase 2 candidate if cleanly bounded.
- **Action-card pre-generation for curated only** — bounded LLM
  cost; keeps lazy-on-click for everything else, which is what
  `/api/signals/{id}/generate-action` already does. Optional.
- **`pattern_type` as `category` rename** — Phase 1 honest
  placeholder. Phase 2 SignalCuratorAgent can categorize
  semantically.

### Operational notes carried forward from 1131

- **Fleet HMAC sign-key = SHA256(secret), not raw secret.** Saved to
  memory. Any new fleet client (Step 1 SignalCuratorAgent doesn't
  need this — it runs IN u-d-b; only OUTSIDE callers sign) must
  follow this contract.
- **`init_db()` does not migrate existing tables.** Adding a column
  to a signal-studio model requires either an explicit
  `_ensure_schema()`-style helper OR an Alembic setup. Phase 1
  chose the former.
- **Dockerfile CMD runs `seed_database()` BEFORE uvicorn.** Any
  schema migration helper used in main.py's startup must ALSO be
  callable from seed.py before its query. Phase 1's pattern: import
  inside the function, call before any query that touches the new
  column.
- **brain_events.py is byte-identical across all 7 fleet repos.**
  signal_ingest.py is signal-studio-specific (no back-prop) but if
  another fleet app ever needs `signal.*` events later, the
  HANDLERS pattern in signal_ingest.py is the reference for how to
  consume them.
- **EventSource is browser-only.** The 2-hop pattern still applies:
  u-d-b emits → fleet backend subscribes server-to-server → fleet
  backend re-emits to browser. signal-studio currently has NO
  browser-facing SSE — adding one for the Curated tab (live updates
  to the curated list?) is a Phase 2 design question, not assumed.
- **Daphne + sync generator + Redis pub/sub = hang.** Use
  `async def event_generator` + `redis.asyncio` for any new SSE
  endpoint.
- **Docker rebuild gotcha.** `docker compose up -d --build` doesn't
  always recreate the container — use `--force-recreate`. Don't run
  parallel builds across 6+ repos.
- **`/api/fleet/*` paths are in `OPTIONAL_AUTH_PATHS`.** Signed-but-
  tokenless is the canonical fleet auth shape.
- **Django 5 `db_default` for DB-managed defaults** (Postgres
  sequences, `gen_random_uuid()`, `now()`). `null=True` alone makes
  Django pass NULL in INSERT and overrides the DB DEFAULT.

### Carryovers (open / parked, not blocking)

- **Service-token auth for `app_slug`** (deferred 1130 → 1131 → 1132).
  PA-token brain-bridge path still trusts whatever `app_slug` the
  caller claims. Known gap; not exploited because the fleet is
  laptop-local. Promote when the fleet leaves the laptop.
- **`docs/SERVICES.md` drift** — header says 320 service files,
  reality is 334 after Phase 1 (+ `fleet_signals.py`). Pre-existing
  pattern; cleanup pass when there's bandwidth.
- **ai-content-studio#2** — Docker foundation PR. Back burner.
- **24-7-ai-global** — Next.js, not yet Dockerized.
- **Per-user filter at u-d-b's replay endpoint** — optional
  `?user_id=…` query param. Cheaper to fan-out + filter in each
  consumer at current traffic.
- **DB-dependent tests** for `signal_aggregation_service` emit
  predicate + cursor advancement — requires test DB with pgvector.
  Live smoke is the canonical verification path until that's solved.
- **context-kit doctor floor:** `10 OK / 2 warnings` (both upstream).
- **`character-os`** — Another Claude Code instance may be active there. Read-only is fine; don't push PRs there or edit their anchor docs.

### Recommended Rigby coordination for Session 1132

For Step 1: brief her with a recency-weighted strength histogram of
the current ~126 real clusters before locking SignalCuratorAgent's
scoring weights. The starter formula
(`0.5*strength + 0.3*size_normalized + 0.2*recency_decay`) is a guess;
she'll want to base the weights on actual distribution shape, same way
she locked the Phase 1 quality bar.

For Step 2: lock the curated-persistence shape (separate ORM type vs
column-on-SignalCluster). Her past architectural calls (publish_intent
enum vs boolean, Session 1094) suggest she'll lean toward the typed
option, but ask explicitly.

For Step 3: confirm the curated payload envelope shape — does it
re-send the full cluster envelope plus `curated_score`, or just an
ID list pointing back to the cluster the consumer already has? The
latter is leaner but assumes the consumer is caught up; the former is
self-contained.

---

## SESSION 1131 — PRIOR ENTRY POINT (signal-studio Phase 1 — closed)

Full handoff: [`docs/handoffs/SESSION_1131_SIGNAL_STUDIO_PHASE_1.md`](docs/handoffs/SESSION_1131_SIGNAL_STUDIO_PHASE_1.md).

---

## SESSION 1130 — TWO SESSIONS BACK (Move 3 R2 reconnect-resilience)

Full handoff: [`docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md`](docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md).

---

*Last overwrite: Session 1131 close → 1132 entry, 2026-05-22 evening.*
