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

## SESSION 1130 LANDED — Move 3 R2 reconnect-resilience live everywhere

Full handoff: [`docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md`](docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md).

**Headline:** monotonic `seq` column on FleetEvent + canonical
replay endpoint + 30-day TTL + drain-before-subscribe pattern across
all 7 fleet apps. 9 PRs merged. All 7 containers now run
312-line brain_events.py (verify with
`docker exec <container> wc -l /app/app/brain_events.py`).

Browser smoke confirmed: tab-switch-then-replay works end-to-end.

---

## SESSION 1131 — CURRENT ENTRY POINT (signal-studio Phase 1)

> **Chris's pivot at the end of 1130:** signal-studio is currently
> showing 5 hardcoded seed signals. He wants it wired into u-d-b's
> spider + signal-aggregation pipeline so it shows real data with
> agent-curated ranking on top.
>
> Briefed Rigby; she locked **path B + C** (pull endpoint + events
> first, then a SignalCuratorAgent layer). Phase 1 below is the B
> half. Phase 2 (C) ships in Session 1132.

### FIRST THING — Quick stack sanity check before coding

1. `cd ~/development/infra && make up` — fleet up.
2. `make all` (or `make start && make celery` from u-d-b) — u-d-b native.
3. Open `http://localhost:5173` (signal-studio frontend) and confirm
   the 5 hardcoded seed signals still show. That's the "before"
   state for the visual diff Chris will care about at the end of 1131.
4. `curl http://localhost:8007/api/signals` should return the same
   5 signals (sanity check the API mirror of what the UI sees).

If anything is off, debug before starting Phase 1 work — every
step below assumes a green stack.

### Phase 1 — pull endpoint + event emit (Rigby's "B")

**Estimate:** ~1 day.

#### Step 1 (u-d-b): `GET /api/fleet/signals/clusters` endpoint

Add a signed endpoint that returns a normalized cluster summary
list, paginated by an exclusive cursor (mirror the Move 3 R2
contract):

```
GET /api/fleet/signals/clusters?since=<seq>&limit=50
Response: { clusters: [...], next_since: <int>, has_more: <bool>, app_slug: "<caller>" }
```

Per-cluster shape (drawn from `core/services/signal_aggregation_service.py`'s
SignalCluster model + what signal-studio's `SignalCluster` /
`EvidenceCard` rows need):

```json
{
  "external_cluster_id": "<uuid>",
  "title": "<short title>",
  "summary": "<2-3 sentences>",
  "pattern_type": "demand_spike | trend_emergence | ...",
  "category": "tech | crypto | business | career | ...",
  "signal_strength": 0.0-1.0,
  "confidence_score": 0.0-1.0,
  "cluster_size": <int>,
  "evidence": [
    {"source": "...", "url": "...", "headline": "..."},
    ...
  ],
  "tags": ["...", "..."],
  "created_at": "<iso8601>"
}
```

**Where to wire it in u-d-b:**
- New view file `core/views_fleet_signals.py` (mirrors
  `core/views_fleet_events.py` shape — fleet sig verify + audit row
  + JSON response).
- New helper service `core/services/fleet_signals.py` that
  translates `SignalCluster` ORM rows into the response shape above.
- Register the URL in `core/urls.py` alongside the fleet artifacts/
  events routes.

**App-scoping gotcha (Rigby's gotcha B):** restrict this endpoint
to `app_slug == "signal-studio"` *at first* — the cluster
firehose is not a thing other fleet apps should subscribe to by
default. Easiest path: add an explicit allowlist check after
signature verification. If/when other apps need clusters later we
can broaden via `FleetServiceIdentity.capabilities`.

#### Step 2 (u-d-b): `signal.cluster_promoted` event emit

When `signal_aggregation_service` creates a new cluster meeting the
quality bar (Rigby's gotcha A):

- `cluster_size >= MIN_CLUSTER_SIZE` (3, already a constant)
- `pattern_type in {allowed list — start permissive, tighten if noisy}`
- `signal_strength >= 0.6` *or* evidence from ≥2 unique source
  domains (Rigby's "evidence diversity" alternative)

Call `emit_event(event_type="signal.cluster_promoted",
app_slug="signal-studio", payload={...cluster summary...})`. Same
envelope shape as the pull endpoint's per-cluster object so
signal-studio's consumer doesn't need two code paths.

**Important:** emit AFTER the cluster row commits (matches the
existing artifact emit pattern in
`core/services/fleet_artifact_cleanup.py`).

#### Step 3 (signal-studio): brain_events handler + DB writes

In `~/development/signal-studio/backend/app/`:

- Extend brain_events.py consumer (or add a sibling handler) to
  recognize `signal.cluster_promoted` and `signal.curated_published`
  events.
- New `app/signal_ingest.py` that:
  - On app startup: pulls one page of `/api/fleet/signals/clusters`
    with `since=<max(external_cluster_id seq) or 0>` until exhausted
    — backfills SignalCluster + EvidenceCard rows.
  - On each `signal.cluster_promoted` event: upserts the cluster by
    `external_cluster_id` (NOT by local UUID — that's Rigby's
    "upsert by external_cluster_id" lock).
- Persist `external_cluster_id` as a column on `SignalCluster` (new
  field; lightweight Alembic migration or SQLAlchemy create_all
  refresh since it's SQLite + early development).

#### Step 4 (signal-studio): drop the seed-only path

`backend/app/seed.py` currently fills 5 hardcoded signals. After
backfill works, the seeder should be a NO-OP when real clusters
exist (`if SignalCluster.objects.count() == 0: seed_demo_signals()`
or similar guard). Don't delete it — useful for cold-start dev /
demo when u-d-b isn't running.

#### Step 5: smoke

- `cd ~/development/infra && make up && make all`
- Trigger a synthetic cluster on u-d-b (Django shell or test fixture
  → emit_event manually).
- Confirm the event lands in signal-studio's SQLite within ~5s and
  shows up in the UI (`localhost:5173/`).
- Optional: tab-switch → emit another cluster → tab back → confirm
  the missed cluster replays (Move 3 R2 already validated this, but
  it's a nice belt-and-suspenders for the new event type).

### Carryover for Session 1132 — Phase 2 (C)

Not in scope for 1131; sketched here so the next handoff doesn't
have to re-discover it:

- New `SignalCuratorAgent` (lightweight, agent-rotation eligible
  under the governor) that runs daily:
  - Pulls recent clusters via the new endpoint.
  - Scores into Top 5-10 by composite of `signal_strength` +
    `cluster_size` + recency.
  - Writes a curated artifact set + emits
    `signal.curated_published`.
- signal-studio UI: add a Curated tab alongside the existing list.
- Optional: action-card pre-generation for curated top only
  (bounded LLM cost; keeps lazy-on-click for everything else).

### Operational notes carried forward

- **brain_events.py is byte-identical across all 7 fleet repos.**
  Edit contract-concierge first, then back-prop. New event types
  (`signal.cluster_promoted`, etc.) probably need a generic event
  router in the subscriber — design that before coding to avoid
  another per-app divergence.
- **EventSource is browser-only.** The 2-hop pattern is u-d-b emits
  → fleet backend subscribes (signed server-to-server) → fleet
  backend re-emits to browser (user-session, token in query).
- **Daphne + sync generator + Redis pub/sub = hang.** Use
  `async def event_generator` + `redis.asyncio` for any new SSE
  endpoint.
- **Docker rebuild gotcha.** `docker compose up -d --build` doesn't
  always recreate the container — use `--force-recreate`. Don't run
  parallel builds across 6+ repos (Docker Desktop daemon hang risk,
  per Session 1125 memory; we got lucky on the Session 1130 close
  but it's a coin flip).
- **`/api/fleet/*` paths are in `OPTIONAL_AUTH_PATHS`.** Signed-but-
  tokenless is the canonical fleet auth shape.
- **Test DB needs pgvector.** Use pure-function unit tests + live
  smoke against running stack for fleet-anything changes.
- **Django 5 `db_default` for DB-managed defaults** (Postgres
  sequences, `gen_random_uuid()`, `now()`). `null=True` alone makes
  Django pass NULL in INSERT and overrides the DB DEFAULT.

### Carryovers (open / parked, not blocking)

- **ai-content-studio#2** — Docker foundation PR. Back burner.
- **24-7-ai-global** — Next.js, not yet Dockerized.
- **Per-user filter at u-d-b's replay endpoint** — optional
  `?user_id=…` query param to push filtering server-side. Not done
  in 1130; current fan-out + filter in each consumer is cheaper at
  this traffic.
- **DB-dependent tests** for replay ordering + TTL deletion —
  requires test DB with pgvector. Live smoke is the canonical
  verification path until that's solved.
- **`docs/SERVICES.md` drift** — header text says 320 service files,
  reality is 332 (fleet_event_cleanup.py landed). Pre-existing
  header-staleness pattern; cleanup pass when there's bandwidth.
- **context-kit doctor floor:** `10 OK / 2 warnings` (both upstream).
- **`character-os`** — Another Claude Code instance may be active there. Read-only is fine; don't push PRs there or edit their anchor docs.

### Service-token auth for `app_slug` (deferred from 1131 top priority)

This was Rigby's option B priority coming out of 1130 ("auth-gate
before UI for security-boundary features"). Chris pivoted to
signal-studio because it's higher-visibility. Service-token auth
moves to Session 1132 or 1133. The PA-token brain-bridge path still
trusts whatever `app_slug` the caller claims — known gap, not yet
exploited because the fleet is laptop-local.

### Recommended Rigby coordination for Session 1131

For the Step 2 quality bar: lock the exact threshold values before
coding. The starter values above (strength >= 0.6, OR ≥2 unique
domains) are placeholders — she'll want to base them on actual
distribution of current cluster scores, which a quick
`SignalCluster.objects.aggregate(...)` will give. Brief her with
the histogram before deciding.

For Step 3: confirm whether to extend the existing brain_events.py
subscriber or add a sibling `signal_events.py` module. The CC-side
draft listener filters by `event_type.startswith("artifact.")`;
adding `signal.*` to the same listener might be cleaner than two
parallel handlers. Her call.

---

## SESSION 1130 — PRIOR ENTRY POINT (Move 3 R2 — closed)

Full handoff: [`docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md`](docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md).

---

## SESSION 1129 — TWO SESSIONS BACK (fleet auth + artifacts + SSE)

Full handoff: [`docs/handoffs/SESSION_1129_FLEET_BRAIN_AUTH_ARTIFACTS_EVENTS.md`](docs/handoffs/SESSION_1129_FLEET_BRAIN_AUTH_ARTIFACTS_EVENTS.md).

---

*Last overwrite: Session 1130 close → 1131 entry, 2026-05-22 evening.*
