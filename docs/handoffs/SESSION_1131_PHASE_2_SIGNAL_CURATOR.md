---
title: "Session 1131 Phase 2 — SignalCuratorAgent + curated_published"
date: 2026-05-22
status: active
session: 1131
phase: 2
previous_handoff: SESSION_1131_SIGNAL_STUDIO_PHASE_1.md
---

# Session 1131 Phase 2 — From firehose to curated experience

> **Read this if** you want to know how the daily curated Top-10
> snapshot is computed, why size got dropped from the scoring
> formula, what the `(pattern_type, topic_key)` dedup actually does
> in practice, or why one early smoke run produced groups like
> `demand_spike::suggestion`.

## TL;DR

Phase 1 turned signal-studio's 5 hardcoded seeds into 131 real
clusters (5 seed + 126 upstream) flowing live via SSE. Phase 2
layers a curated experience on top: a **daily Top-10 snapshot**
produced by `SignalCuratorAgent`, scored by Rigby's locked formula,
deduped by `(pattern_type, topic_key)`, capped at 3 per pattern_type,
and persisted with full provenance.

| What | Where |
|---|---|
| **u-d-b emit side** | PR [#2140](https://github.com/clwest/donkey-betz-platform/pull/2140) (stacked on Phase 1 PR #2138) |
| **signal-studio consume + UI side** | PR [#13](https://github.com/clwest/signal-studio/pull/13) (stacked on Phase 1 PR #12) |

End-to-end live: `curate_and_emit()` on u-d-b → `signal.curated_published`
FleetEvent → SSE → signal-studio consumer applies snapshot →
`GET /api/signals/curated` → React Curated tab. Visual: open
`localhost:5173`, click "Curated Top 10", see rank badges 1-10 on
amber-bordered cards.

## Rigby's four locks (conversation pa-d19c1674b936)

These came from a single histogram-driven round before any code
landed. Once locked, the implementation was straight-line.

### Lock 1 — Dedup = hard-cap grouping, not penalty term

Group key = `f"{pattern_type}::{topic_key}"`. Pick single best per
group; rank winners globally. Per-pattern_type cap of
`max(2, ceil(N/4))` = 3 for N=10 prevents one type from dominating.

**Why grouping over penalty**: penalty terms are fiddly and shift
with the distribution; grouping is deterministic and explainable in
the snapshot audit trail.

### Lock 2 — Score = `0.9 * strength + 0.1 * recency_decay`

Size dropped from the formula. The Phase 1 close histogram showed
`strength` and `cluster_size` correlate strongly (r≈0.7 in the
binned table) — keeping both was double-counting.
`recency_decay = exp(-age_hours / 72)`. Low recency weight because
in dev all 126 candidates are <72h old; bumping to 0.2 once we see
steady-state spread.

### Lock 3 — Top 10 per snapshot

Top 5 would be too sensitive to duplicates and look "stuck" if one
topic dominates. Top 10 with the per-pattern_type cap of 3 gives
enough room for diversity while staying clearly curated.

### Lock 4 — `CuratedSignalSnapshot` is source of truth

Typed parent + child table. Snapshot row carries `scoring_formula_version`
(e.g. `v1_strength_0.9_recency_0.1_tau72`), `dedup_strategy`,
`pattern_type_cap` (JSON), `pool_size`, `top_n`, `excluded_duplicates`
(JSON audit list). Child `CuratedSignalEntry` rows snapshot the
cluster's strength/size/age at pick time so the audit explains "why
was this picked" even after the cluster row drifts.

signal-studio side gets only convenience columns (`curated_rank`,
`curated_score`, `curated_snapshot_id`) on `SignalCluster` — latest
snapshot wins on the rendering side; full history lives in u-d-b.

## The topic_key gotcha (caught mid-implementation)

First smoke run produced top-10 groups like:
- `demand_spike::suggestion` (4 React clusters all collapsed here)
- `trend_emergence::suggestion`
- `sentiment_shift::suggestion`
- `opportunity_window::missing`

Useless for dedup. The upstream `keywords` JSON field mixes
PATTERN_TYPE_KEYWORDS indicator words ("want", "looking for",
"suggestion", "missing") with actual TOPIC words ("react",
"security", "ai"). Naively picking `keywords[0]` lands on indicator
words ~half the time.

**Fix** (in `signal_curator_service.topic_key_for_cluster`):

1. Prefer `cluster.name` first — `_generate_topic_name` in
   `signal_aggregation_service` leads with the topic ("React demand
   spike", "Security emerging trend").
2. Filter PATTERN_TYPE_KEYWORDS indicator words from BOTH paths
   (name and keywords). Stop-word set includes normalized
   multi-word forms (e.g. `"looking_for"`, `"how_to"`,
   `"better_than"`).
3. UUID-prefix fallback for clusters whose name is entirely stop
   words ("New emerging trend" → `unknown_<8chars>`).

Post-fix top-10 has meaningful group keys: `demand_spike::react`,
`trend_emergence::security`, `sentiment_shift::marketing`,
`trend_emergence::artificial`, `opportunity_window::security`,
`skill_demand::startup`, `demand_spike::analytics`,
`skill_demand::privacy`. 2/10 still fall back to UUID prefix because
their names are pure pattern labels — acceptable signal of upstream
naming quality.

## What ships

### u-d-b (PR #2140)

| File | Change |
|---|---|
| `core/migrations/0348_curated_signal_snapshot.py` | new — `CuratedSignalSnapshot` + `CuratedSignalEntry` tables, `unique(snapshot, rank)`, `(cluster, -snapshot)` index |
| `core/models_signal_intelligence.py` | + `CuratedSignalSnapshot` + `CuratedSignalEntry` models |
| `core/services/signal_curator_service.py` | new — pure-deterministic curator: `normalize_topic_key`, `topic_key_for_cluster`, `group_key_for_cluster`, `compute_score`, `_pick_group_winners`, `_apply_pattern_type_cap`, `curate_top_n`, `build_curated_envelope`, `emit_curated_published`, `curate_and_emit` |
| `core/tasks_spiders.py` | + `_impl_curate_signal_clusters` Celery impl |
| `core/tasks.py` | + `@shared_task curate_signal_clusters` wrapper |
| `core/celery.py` | + beat entry `'curate-signal-clusters'` daily at 13:00 UTC (6 AM MST), 4h expires, `long_running` queue |
| `tests/services/test_signal_curator_phase2.py` | new — 36 pure-function tests |

### signal-studio (PR #13)

| File | Change |
|---|---|
| `backend/app/models.py` | + `curated_rank` (Integer, indexed, nullable) + `curated_score` (Float, nullable) + `curated_snapshot_id` (String, nullable) on `SignalCluster` |
| `backend/app/signal_ingest.py` | `_ensure_schema()` adds the 3 columns + index idempotently. New `_apply_curated_snapshot()` implements latest-wins. `HANDLERS` routes `signal.curated_published` → `_apply_curated_snapshot` via the existing `_handle_signal_event` dispatcher (one tuple, no new long-running task — proves the Phase 1 router design) |
| `backend/app/main.py` | + `GET /api/signals/curated` endpoint |
| `frontend/src/App.tsx` | + view state extended to `'signals' | 'curated' | 'brain'`. Top-level toggle "All Signals" / "Curated Top 10". New `CuratedSignalCard` with rank badge + curated_score chip. Empty state for "no snapshot yet" |

## Smoke results (live local stack)

**Pool, dedup, cap**

```
pool=126 (matches Phase 1's quality-bar count exactly)
excluded=113 (dedup + cap)
kept=10

Pattern_type distribution in top 10:
  trend_emergence: 3   ← cap of 3 holding
  demand_spike:    2
  opportunity_window: 2
  skill_demand:    2
  sentiment_shift: 1
```

**Score spread**

| Position | Pre-dedup (close histogram) | Post-dedup (Phase 2) |
|---|---|---|
| #1 | 0.920 | 0.921 |
| #10 | 0.889 | 0.804 |
| spread | 0.031 | 0.117 |

Dedup actually opens up the score spread — each rank holds meaningful
position rather than 4 near-identical entries clustering at the top.

**End-to-end latency**: `curate_and_emit()` → FleetEvent row →
Redis pub/sub → signal-studio SSE consumer → `_apply_curated_snapshot`
→ DB row updates. Measured at ~3s under no load. Latest-snapshot-wins
verified by running `curate_and_emit()` twice; second snapshot's
UUID propagated to `/api/signals/curated.snapshot_id` end-to-end.

**Tests**: 36 new Phase 2 tests + 23 Phase 1 tests + 37 existing
fleet tests = **96 green**, no regressions.

## Memory deltas

No new memory entries this phase. The fleet HMAC sign-key gotcha
already in memory from Phase 1 close was sufficient; no new
recurring traps surfaced.

## Open carryovers (deferred again)

The following were noted in Phase 1's close and remain deferred —
not blocked by Phase 2.

- **Service-token auth for `app_slug`** (deferred 1130 → 1131 → 1131-Phase2).
  PA-token brain-bridge path still trusts whatever `app_slug` the
  caller claims. Known gap; promote when the fleet leaves the
  laptop. Rigby's "auth-gate before UI for security-boundary
  features" rule applies — this is the only remaining "real
  incident risk" carryover.
- **Evidence URL field** — Phase 1 envelope ships `url=""` because
  `SignalCluster.sample_signals` has no URL column. Phase 2 didn't
  fix this; deferred. Cleanest path: extend `sample_signals` shape
  upstream once we have an enrichment agent that can populate it.
- **Semantic `category`** — Both phases use `pattern_type` as the
  category (honest placeholder). A future enrichment agent could
  map clusters to real semantic categories ("tech", "crypto",
  "career", etc.) for cleaner UI filtering. Deferred.
- **`docs/SERVICES.md` drift** — header text says 320 service files;
  reality after Phase 2 is 335 (added `signal_curator_service.py`).
  Pre-existing pattern; cleanup pass when there's bandwidth.
- **Action-card pre-generation for curated only** — Rigby noted
  this in the Phase 1 close as Phase 2 optional. Didn't ship in
  this phase; bounded LLM cost worth picking up next if Chris wants
  the Curated tab to have instant action-cards.

## Recommended Rigby coordination for next session

I see three credible candidates for the next session's focus.
Brief Rigby with this list and let her pick:

### A) Action-card pre-generation for curated only
- One-time LLM call per curated item per day = bounded cost
- Curated tab becomes "click to expand pre-built action plan" vs
  the existing lazy `/api/signals/{id}/generate-action` path
- Low risk, ships in a session, makes the Curated tab feel "done"

### B) Service-token auth for `app_slug` (Rigby's long-deferred lock)
- The only remaining "real incident risk" carryover
- Less impressive visually but matches Rigby's "auth-gate before
  UI for security-boundary features" rule
- Probably 1-2 sessions of careful work — token rotation, audit
  log, identity-claim verification at the brain-bridge layer

### C) Real-time SSE refresh in the Curated tab
- When `signal.curated_published` lands while the user is on the
  Curated tab, the page should refresh automatically (or show a
  toast: "new curated set available, refresh?")
- Pure frontend work + a small WS / SSE proxy at the signal-studio
  backend; ~half a session
- Polishes the Phase 2 experience

My read: **A then C** as a single session if both are tight; **B**
if Chris wants security work before more features. None of these
are urgent.

---

*Phase 2 closed 2026-05-22 evening.*
