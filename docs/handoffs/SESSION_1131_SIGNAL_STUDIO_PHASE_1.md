---
title: "Session 1131 — signal-studio Phase 1: real cluster ingest + live SSE consumer"
date: 2026-05-22
status: active
session: 1131
previous_handoff: SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md
---

# Session 1131 — signal-studio drinks from the real fleet pipe

> **Read this if** you want to know why signal-studio's UI flipped
> from 5 hardcoded seeds to 131 real clusters in one session, how
> the `signal.cluster_promoted` event flows from u-d-b's
> `signal_aggregation_service` into signal-studio's Postgres in
> under 5 seconds, or what Phase 2 (path C, the SignalCuratorAgent
> layer) still has left to do.

## TL;DR

Session 1131 wired signal-studio to u-d-b's `SignalCluster` pipeline.
The contract used to be **"5 hardcoded demos forever"**; it's now
**"live clusters from the spider network, ranked by upstream quality
bar, replayable from any cursor."** Rigby's path B + lock C both
shipped end-to-end.

| Step | Side | What shipped | PR |
|---|---|---|---|
| **1 — Pull endpoint** | u-d-b | `GET /api/fleet/signals/clusters?since=<seq>&limit=<n>` — paginated cursor mirroring Move 3 R2, fleet HMAC sig + signal-studio-only allowlist, SQL filter `status=active AND strength>=0.6` | [u-d-b #2138](https://github.com/clwest/donkey-betz-platform/pull/2138) |
| **2 — Event emit** | u-d-b | `signal.cluster_promoted` fires on detecting→active transition in `signal_aggregation_service._create_signal_clusters` (both new + update paths). Payload byte-identical to the pull endpoint's envelope so consumers need one code path | (same PR) |
| **2a — Monotonic `seq`** | u-d-b | `core_signalcluster_seq` Postgres sequence, migration 0347 backfilled 307 existing rows in `detected_at` order (monotonic 1→307, zero violations) | (same PR) |
| **3 — Ingest + HANDLERS router** | signal-studio | `app/signal_ingest.py`: `HANDLERS = [(prefix, handler_fn), ...]`, `upsert_cluster_from_envelope()` by `external_cluster_id`, `backfill_from_pull_endpoint()` drains all eligible clusters on startup, `consume_fleet_events()` long-running asyncio task on top of `subscribe_fleet_events()` | [signal-studio #12](https://github.com/clwest/signal-studio/pull/12) |
| **3b — Schema migration** | signal-studio | `_ensure_schema()` adds `external_cluster_id` column + unique partial index across both Postgres and SQLite (idempotent ALTER TABLE; `init_db()`'s `create_all` doesn't migrate existing tables) | (same PR) |
| **4 — Seed NO-OP guard** | signal-studio | `seed_database()` short-circuits when any row with `external_cluster_id IS NOT NULL` exists; `force=True` overrides | (same PR) |
| **5 — Smoke** | both | Backfill: 126 upstream clusters upserted on first run (matches u-d-b's quality-bar count exactly). Live SSE: title update propagates u-d-b → signal-studio Postgres in ~3s; revert clears it the same way | — |

**2 PRs open** (u-d-b #2138 + signal-studio #12). Smoke verified
end-to-end against the live local stack — fleet up, u-d-b native,
all 7 fleet apps healthy on `fleet-net`. UI at `localhost:5173` now
shows real cluster titles like "React demand spike", "Marketing
sentiment shift", "AI emerging trend" where the 5 demos used to live.

## Rigby's three locks (conversation pa-d19c1674b936)

These are the design decisions Rigby made when I briefed her with
the cluster histogram before any code landed.

1. **Quality bar — strength-only, no OR.** Locked to
   `status=active AND cluster_size>=3 AND strength>=0.6`. The
   starter bar from the 1131 entry plan (`size>=3 AND (strength>=0.6
   OR sources>=2)`) was too permissive — `sources>=2` alone hits
   88.9% of the local 307-cluster sample, collapsing the OR and
   turning the emit into a firehose. Tightened version emits ~41%
   (126/307), which is the right shape for a "signal feed" not a
   stream of everything. Tighter ratchet (Option 2: `size>=5`) is
   one-line ready if the UI shows it's still noisy.
2. **No source_diversity guardrail yet.** Only 34/307 clusters are
   single-source today. Adding `sources>=2` as a guardrail would
   buy ~10% noise reduction at the cost of complicating the
   predicate. Defer until the UI shows single-source spam.
3. **Generic prefix router, not parallel listeners.** Extend the
   single `brain_events.py` consumer's call-site with a
   `HANDLERS = [(prefix, handler_fn), ...]` dispatch table rather
   than spinning up a parallel `signal_events.py` per repo. Adding
   `signal.curated_published` in Phase 2 means one tuple, not a
   second long-running task. Unknown prefixes silently drop to
   debug log (no warn spam).

## What broke / what surprised

### Fleet HMAC sign-key is `SHA256(raw_secret).hexdigest()`, not the raw secret

Burned ~5min on a `signature_mismatch` 401 before I realized both
sides of the wire use `SHA256(secret).hexdigest()` as the HMAC key.
The raw secret only ever lives in the fleet app's env;
`FleetServiceKey.secret_hash` stores the hex digest, and
`compute_signature()` is called with that string on the verify side.
Documented inline in `contract-concierge/backend/app/fleet_signer.py:141`
but not obvious from u-d-b's spec.

**Saved to memory** as `feedback_fleet_hmac_sign_with_secret_hash.md` so
future Step-3-style work doesn't trip the same wire.

### Dockerfile CMD runs `seed_database()` BEFORE uvicorn imports `main.py`

signal-studio's container starts with:

```
CMD python -c "from app.seed import seed_database; seed_database()" \
    && uvicorn app.main:app ...
```

That sequence meant my `_ensure_schema()` call from `main.py`'s
startup hook ran **after** seed.py had already queried the
not-yet-existing `external_cluster_id` column — `psycopg2.errors.
UndefinedColumn` on the first container start. Fix: import
`_ensure_schema` inside `seed_database()` and run it before the guard
query. Now both startup paths (seed-first, then uvicorn) call the
helper, which is idempotent.

### `init_db()` does not alter existing tables

`Base.metadata.create_all()` only creates **missing** tables; it does
NOT add new columns to existing tables. The Phase 1 schema change
(`external_cluster_id`) needed an explicit ALTER TABLE path. The
helper `signal_ingest._ensure_schema()` introspects via PRAGMA (SQLite)
or `information_schema.columns` (Postgres) and emits ALTER + a unique
partial index. Idempotent on both dialects.

## Smoke recipe (canonical, for future Phase work)

After this session the canonical end-to-end smoke is:

```bash
# 1. Fleet up, u-d-b native
cd ~/development/infra && make up
make all   # or `make start && make celery` from u-d-b

# 2. Confirm signal-studio has real clusters
curl -s "http://localhost:8007/api/signals" | jq '.total'
# expect: 131 (5 seed + 126 real)

# 3. Confirm external_cluster_id linkage
docker exec signal_studio_postgres psql -U signalstudio -d signalstudio -c \
  "SELECT COUNT(*) FILTER (WHERE external_cluster_id IS NOT NULL) AS real,
          COUNT(*) FILTER (WHERE external_cluster_id IS NULL) AS seed
   FROM signal_clusters;"
# expect: real=126, seed=5

# 4. Live SSE smoke — bump a title on u-d-b, re-emit, watch it land
cd ~/development/unified-donkey-betz
.venv/bin/python manage.py shell -c "
from core.models_signal_intelligence import SignalCluster
from core.services.signal_aggregation_service import SignalAggregationService
c = SignalCluster.objects.filter(status='active', strength__gte=0.6).first()
c.name = f'[SMOKE] {c.name}'
c.save(update_fields=['name'])
SignalAggregationService()._maybe_emit_cluster_promoted(c)
print(c.id)
"
# Then within ~3s:
docker exec signal_studio_postgres psql -U signalstudio -d signalstudio -c \
  "SELECT title FROM signal_clusters WHERE external_cluster_id = '<paste id>';"
# expect: '[SMOKE] ...' to appear; revert + re-emit to clear.
```

## Files touched

### u-d-b (PR #2138)

| File | Change |
|---|---|
| `core/migrations/0347_signalcluster_seq.py` | new — `core_signalcluster_seq` sequence + `seq BIGINT NOT NULL` column + backfill in `detected_at` order |
| `core/models_signal_intelligence.py` | + `seq` field on SignalCluster (Django 5 `db_default=RawSQL(nextval(...))`) |
| `core/services/fleet_signals.py` | new — translator (`cluster_envelope`, `iter_cluster_envelopes`), quality-bar constants |
| `core/views_fleet_signals.py` | new — `GET /api/fleet/signals/clusters` view; fleet sig verify → app_slug allowlist → SQL filter → translate |
| `core/services/signal_aggregation_service.py` | + `_maybe_emit_cluster_promoted()`; emit on detecting→active in both create + update paths |
| `core/urls.py` | + route registration |
| `core/auth_middleware.py` | + `/api/fleet/signals/` in `OPTIONAL_AUTH_PATHS` |
| `tests/services/test_fleet_signals_phase1.py` | new — 23 pure-function tests |

### signal-studio (PR #12)

| File | Change |
|---|---|
| `backend/app/signal_ingest.py` | new — `HANDLERS` router, upsert, backfill, consumer, `_ensure_schema` |
| `backend/app/models.py` | + `external_cluster_id` column on `SignalCluster` |
| `backend/app/main.py` | + `@app.on_event("startup")` spawning backfill + consumer (gated on `FLEET_SERVICE_SECRET`) |
| `backend/app/seed.py` | + NO-OP guard on `external_cluster_id IS NOT NULL > 0`; `force=True` override; pre-query `_ensure_schema` call |
| `docker-compose.yml` | + `FLEET_APP_SLUG`/`FLEET_KEY_ID`/`FLEET_SERVICE_SECRET` env block |
| `.env.example` | + same env stubs with provisioning instructions |

### Out-of-band

- Provisioned `signal-studio` `FleetServiceIdentity` (`fs_signalstudio_k1`)
  via `python manage.py provision_fleet_identity --app-slug signal-studio`.
  Raw secret in signal-studio's local `.env` (gitignored). u-d-b
  stores `SHA256(secret).hexdigest()` only.

## Memory deltas

- **New feedback memory**: `feedback_fleet_hmac_sign_with_secret_hash.md`
  — fleet HMAC sign-key contract; symptom is 401 `signature_mismatch`
  with no other clue.
- **No other rule changes**. Existing rules (Rigby-first comms,
  pa_chat local override, docs index, Django 5 `db_default`, Docker
  `--force-recreate`, etc.) all applied without exception.

## Open carryovers for Phase 2 (Session 1132)

### Phase 2 — SignalCuratorAgent layer (Rigby's path C)

> Phase 2 is the agent-curated ranking layer on top of what Phase 1
> shipped. The pull endpoint + emit + live consumer is the firehose;
> Phase 2 turns it into a curated experience.

- **New `SignalCuratorAgent`** (u-d-b side) — lightweight agent,
  governor-eligible, runs daily:
  - Pulls recent clusters via `/api/fleet/signals/clusters` (the
    Phase 1 endpoint already gives us a clean cursor)
  - Scores by composite of `signal_strength + cluster_size + recency`
  - Picks Top 5–10
  - Writes a curated artifact set + emits `signal.curated_published`
- **signal-studio Curated tab** — new UI tab alongside the existing
  list. Renders from a curated subset stored as a separate ORM type
  (or a `curated_score` column on `SignalCluster`).
- **Handler plug-in** — `signal_ingest.HANDLERS` adds one tuple:
  `("signal.curated_published", _handle_curated_event)`. The router
  pattern was designed for this exact extension.
- **Optional**: action-card pre-generation for curated only (bounded
  LLM cost; keeps lazy-on-click for everything else, which is what
  the existing `/api/signals/{id}/generate-action` already does).

### Lower-priority cleanup

- **Evidence URL field**. The Phase 1 envelope ships `url=""` because
  `SignalCluster.sample_signals` has no URL column. UI renders empty
  link state today. Two paths: (a) extend `sample_signals` upstream
  to include a `url` field, or (b) wait for the SignalCuratorAgent
  to do enrichment in Phase 2 — that's the cleaner path.
- **`pattern_type` as `category`** — Phase 1 honest placeholder.
  Phase 2 SignalCuratorAgent can categorize semantically.
- **Service-token auth for `app_slug`** (deferred from 1130 → 1131
  → still deferred). The PA-token brain-bridge path still trusts
  whatever `app_slug` the caller claims. Known gap, not exploited
  because the fleet is laptop-local. Promote when the fleet leaves
  the laptop.
- **`docs/SERVICES.md` drift** — header text says 320 service files,
  reality after this session is 334 (added `fleet_signals.py`).
  Pre-existing header-staleness pattern; cleanup pass when there's
  bandwidth.

## Recommended Rigby coordination for Session 1132

For SignalCuratorAgent scoring weights: brief her with a recency-
weighted strength histogram of the current 126 real clusters before
locking the composite formula. Starter weights are fine to propose
(`0.5*strength + 0.3*size_normalized + 0.2*recency_decay`) but she
should sign off based on actual distribution shape.

For the Curated tab UI: confirm whether curated clusters live as a
separate ORM type (cleaner long-term, requires a new table) or as a
boolean+score on the existing `SignalCluster` row (simpler, one
column add). Her call.
