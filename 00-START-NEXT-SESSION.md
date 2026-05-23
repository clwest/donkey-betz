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

## SESSION 1131 LANDED — Phase 1 + Phase 2 both shipped

Phase 1 (signal-studio drinks from the real fleet pipe):
- Full handoff: [`docs/handoffs/SESSION_1131_SIGNAL_STUDIO_PHASE_1.md`](docs/handoffs/SESSION_1131_SIGNAL_STUDIO_PHASE_1.md)
- u-d-b PR [#2138](https://github.com/clwest/donkey-betz-platform/pull/2138) + signal-studio PR [#12](https://github.com/clwest/signal-studio/pull/12)
- 5 hardcoded seeds → **131 real clusters** (5 seed + 126 upstream). Live SSE updates in ~3s.

Phase 2 (curated experience on top of the firehose):
- Full handoff: [`docs/handoffs/SESSION_1131_PHASE_2_SIGNAL_CURATOR.md`](docs/handoffs/SESSION_1131_PHASE_2_SIGNAL_CURATOR.md)
- u-d-b PR [#2140](https://github.com/clwest/donkey-betz-platform/pull/2140) + signal-studio PR [#13](https://github.com/clwest/signal-studio/pull/13)
- Daily SignalCuratorAgent at 6 AM MST. Top 10 deduped by `(pattern_type, topic_key)`, capped at 3/type. `signal.curated_published` event drives the Curated tab in signal-studio.

**Visual diff for Chris**: open `localhost:5173`. Click "Curated Top 10" → see rank badges 1-10 on amber-bordered cards. Scores 0.804–0.921. Click any → existing SignalDetail UI (evidence cards, sources, action plan).

**Burned-in gotcha from Phase 1 (saved to memory):** Fleet HMAC clients sign with `SHA256(raw_secret).hexdigest()`, not the raw secret. Symptom is 401 `signature_mismatch`. Reference impl: `contract-concierge/backend/app/fleet_signer.py:141`.

---

## SESSION 1132 — CURRENT ENTRY POINT (C primary + B scaffold stretch)

> **Rigby's pick** (conversation pa-d19c1674b936, locked at Phase 2
> close): **C first**, then start **B** scaffolding if time remains.
> A is deferred — see "Deferred this session" below for her forward
> note on how A should land when greenlit.

### FIRST THING — Sanity check before any new work

1. `cd ~/development/infra && make up`
2. `make all` (or `make start && make celery` from u-d-b)
3. `curl -s http://localhost:8007/api/signals | jq '.total'` should be `131`-ish (5 seed + N real). If still 5, Phase 1's `FLEET_SERVICE_SECRET` isn't set in signal-studio's env: `docker exec signal_studio_api env | grep FLEET`.
4. `curl -s http://localhost:8007/api/signals/curated | jq '.total'` should be `10` if the curator has run; `0` with the "no curated snapshot yet" empty state otherwise. To force a fresh curated emit:
   ```bash
   cd ~/development/unified-donkey-betz
   .venv/bin/python manage.py shell -c "
   from core.services.signal_curator_service import curate_and_emit
   r = curate_and_emit(top_n=10)
   print(r.snapshot.id, r.snapshot.top_n)
   "
   ```
5. Visual check at `localhost:5173`: "All Signals" tab + "Curated Top 10" tab both render with real data.

If anything is off, fix it before starting new work.

### Primary: (C) Real-time SSE refresh in the Curated tab

**Estimate:** ~half a session.

**Why Rigby picked C first:** highest ROI per hour. No new backend
semantics, no LLM spend, makes Phase 2 feel "alive" immediately.
Aligns with Chris's cleanup/verify-truth mode + local-only default.

**Goal:** when `signal.curated_published` lands while a user is
viewing the Curated tab, the page either auto-refreshes the list
or shows a toast like *"new curated set available — refresh?"*

#### Suggested path (Rigby may adjust)

1. **signal-studio backend**: add a small browser-facing SSE
   endpoint (e.g. `GET /api/signals/events`) that subscribes to a
   per-app-slug Redis channel and emits curated-only events to the
   user-session. **Async only** — daphne + sync generator + Redis
   pub/sub = hang (memory rule). Use `async def event_generator` +
   `redis.asyncio`. The Phase 1 brain_events.py SSE primitive is
   the reference pattern.
2. **signal_ingest handler**: when `_apply_curated_snapshot()`
   finishes, also publish a tiny `curated:refreshed` event onto
   the browser-facing Redis channel (just `{snapshot_id, top_n}`
   — no need to fan out the full envelope; the UI can refetch).
3. **React Curated tab**: open an `EventSource` to the new
   endpoint when the tab is active; on `curated:refreshed`, either
   call `setCurated(refetch)` directly or render a small "🟢 New
   curated set — refresh" pill that re-fetches on click. UX call
   is yours/Rigby's; the toast variant is less jarring while the
   user is reading.
4. **Smoke**: trigger `curate_and_emit()` from u-d-b shell while
   the Curated tab is open in the browser; verify the badge/refresh
   fires within a few seconds.

#### Gotchas to expect

- **2-hop pattern still applies** (memory rule): u-d-b's
  `signal.curated_published` arrives at signal-studio backend via
  the existing brain_events SSE consumer. The NEW user-facing SSE
  channel is signal-studio backend → browser. The two-hop is
  preserved; you're adding the second hop.
- **EventSource is browser-only.** Server-to-server stays on the
  signed signal_ingest path.
- **No per-user filtering needed** at signal-studio backend for
  Phase 2: curated set is app-wide, not user-scoped. Phase 3+ can
  add user-personalized curation if it ever matters.

### Stretch: (B) Service-token auth for `app_slug` (scaffold only)

**Rigby's rule**: "do not ship partial auth unless it's end-to-end
enforceable." If there's session time after C lands, **start B's
scaffolding** — token plumbing, model fields, tests — but don't
flip any verification on until the next session can finish it.

**Status**: deferred 1130 → 1131 → 1131 Phase 2 → now scaffolding
candidate. Only remaining "real incident risk" carryover.

**What it fixes**: the PA-token brain-bridge path still trusts
whatever `app_slug` the caller claims. A compromised fleet app
could currently impersonate another. Not exploited because fleet
is laptop-local; promote when fleet leaves the laptop.

**Suggested scaffold work order** (1132 stretch, 1133 finish):

1. New `FleetServiceToken` model (or extend existing
   `FleetServiceIdentity` with a token field) — bearer-token
   shape, rotation-capable, scoped to `app_slug`.
2. Mint endpoint or management command (mirrors
   `provision_fleet_identity`).
3. Verification middleware/decorator — initially log-only (warn
   when claimed app_slug doesn't match token's identity, don't
   reject yet). Once we have a few days of clean logs, flip to
   enforce.
4. Update each fleet app's `.env` to consume + send the token.
5. **Do NOT ship partial enforcement** — the warn-only phase is
   safe to land, but the reject phase has to wait for end-to-end
   coverage across all 7 fleet repos.

If 1132 only gets C + scaffolding for B's models/tests landed,
that's a successful session per Rigby's framing.

### Deferred this session: (A) Action-card pre-gen for curated

Rigby's forward note for when A is greenlit:

> Pre-generate on the **u-d-b side** for curated-only (top 10) and
> include them in the `signal.curated_published` payload **or**
> store them in the snapshot child rows. That keeps "curated set
> is ready-to-act" as a single-source-of-truth artifact, and
> signal-studio becomes a renderer, not an LLM executor.

Cost shape: ~10 LLM calls/day per curator run. Bounded. Postponed
because Chris is in cleanup/verify-truth mode and A adds an
"is the generated content correct?" surface area. Promote when
Chris explicitly wants Phase 2's UX to feel "done."

### Lower-priority cleanup (defer further if 1132 has a clear focus)

- **Evidence URL field** — both phases ship `url=""` because `SignalCluster.sample_signals` has no URL column. Cleanest path: a future enrichment agent populates it.
- **Semantic `category`** — phases 1+2 use `pattern_type` as category. Real semantic categorization would unlock cleaner UI filtering.
- **`docs/SERVICES.md` drift** — header says 320 service files; reality after Phase 2 is 335. Cleanup pass when there's bandwidth.

### Operational notes carried forward from 1131

These are now locked in code and tests but worth remembering when touching adjacent areas:

- **Fleet HMAC sign-key = SHA256(secret), not raw secret.** Saved to memory. Any new fleet client must follow this contract.
- **`init_db()` does not migrate existing tables** (signal-studio side). Schema additions need `_ensure_schema()` calls in BOTH startup paths (`main.py` startup hook AND `seed.py` before its first query — Dockerfile runs seed before uvicorn). Phase 1's pattern is the reference.
- **brain_events.py is byte-identical across all 7 fleet repos.** signal_ingest.py is signal-studio-specific. Future event types plug into the HANDLERS prefix router (one tuple, no parallel listener) — the Phase 2 `signal.curated_published` handler proved this pattern.
- **EventSource is browser-only.** 2-hop pattern still applies: u-d-b emits → fleet backend server-to-server subscribes → fleet backend re-emits to browser.
- **Daphne + sync generator + Redis pub/sub = hang.** Use `async def event_generator` + `redis.asyncio` for any new SSE endpoint.
- **Docker rebuild gotcha.** `docker compose up -d --build` doesn't always recreate the container — use `--force-recreate`. Don't run parallel builds across 6+ repos.
- **`/api/fleet/*` paths are in `OPTIONAL_AUTH_PATHS`.** Signed-but-tokenless is the canonical fleet auth shape.
- **Django 5 `db_default` for DB-managed defaults** (Postgres sequences, `gen_random_uuid()`, `now()`). `null=True` alone makes Django pass NULL in INSERT and overrides the DB DEFAULT.
- **Phase 2 topic-key gotcha**: upstream keywords mix PATTERN_TYPE_KEYWORDS indicator words with topics. `topic_key_for_cluster` in `signal_curator_service.py` prefers `cluster.name` first then keywords, with a stop-word filter on BOTH. If you add new pattern types or change `_generate_topic_name`, update the stop-word set.

### Carryovers (open / parked, not blocking)

- **Service-token auth for `app_slug`** — see (B) above. Promote when fleet leaves laptop.
- **ai-content-studio#2** — Docker foundation PR. Back burner.
- **24-7-ai-global** — Next.js, not yet Dockerized.
- **Per-user filter at u-d-b's replay endpoint** — optional `?user_id=…` query param. Cheaper to fan-out + filter in each consumer at current traffic.
- **DB-dependent tests** for fleet emit predicate + cursor advancement + curator dedup at scale — requires test DB with pgvector. Live smoke is the canonical verification path until that's solved.
- **context-kit doctor floor:** `10 OK / 2 warnings` (both upstream).
- **`character-os`** — Another Claude Code instance may be active there. Read-only is fine; don't push PRs there or edit their anchor docs.

### Recommended Rigby coordination for Session 1132

Direction is already locked (C primary + B scaffold stretch). Only
re-engage Rigby if:

- **C surfaces an unexpected design question** (e.g. per-user
  filter becomes necessary, or the toast vs auto-refresh UX call
  needs a second opinion based on what you see in browser smoke).
- **B scaffolding hits a model design fork** (FleetServiceToken
  as new model vs token field on existing FleetServiceIdentity).
  She locked Phase 2's snapshot as a new typed table over a
  column-on-cluster; the analog for B is probably "new model" but
  confirm before you code.
- **Chris overrides** the C → B order and asks for something
  different at session start.

Otherwise: code C, smoke it in the browser, ship the PR, then
start B scaffolding only if there's session budget left. Do NOT
ship partial auth enforcement (her hard rule).

---

## SESSION 1131 PHASE 1 — PRIOR ENTRY POINT (closed)

Full handoff: [`docs/handoffs/SESSION_1131_SIGNAL_STUDIO_PHASE_1.md`](docs/handoffs/SESSION_1131_SIGNAL_STUDIO_PHASE_1.md).

---

## SESSION 1130 — TWO SESSIONS BACK (Move 3 R2 reconnect-resilience)

Full handoff: [`docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md`](docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md).

---

*Last overwrite: Session 1131 Phase 2 close → 1132 entry (C primary + B scaffold stretch, per Rigby pick), 2026-05-22 evening.*
