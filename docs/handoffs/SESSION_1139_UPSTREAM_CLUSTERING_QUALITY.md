---
title: "Session 1139 — Upstream clustering quality (Option A: entity-token clusterer)"
date: 2026-05-24
status: active
session: 1139
previous_handoff: SESSION_1138_F1_PAID_INTEREST_IMPLEMENTATION.md
next_session_primary: Live rejection-rate measurement post-merge + (Y) reject-mode flip if audit telemetry clean + Rigby's `signal_studio_judge_stats` PA tool from her Q3 design note
team: chris + claude + rigby (design review)
---

# Session 1139 — Upstream clustering quality

> **Read this if** you want the Session 1139 upstream clusterer rewrite
> details: empirical diagnosis, what the entity-token clusterer does,
> Rigby's design decisions, what's verified locally, and how the live
> rejection-rate acceptance test gets run after this merges.

## TL;DR

**Replaced the verb-keyword fallback clusterer in u-d-b's
`signal_aggregation_service` with an entity-token clusterer**, gated
behind a new `cluster_method` field that lets legacy rows decay
naturally (no forced re-cluster). All 307 existing SignalCluster rows
backfilled to `cluster_method='legacy'` by migration 0351; new rows
created by aggregation are tagged `entity_token_v1`. The
`cluster_method` discriminator propagates downstream through the
`cluster_envelope` so signal-studio's mirror can measure per-method
rejection rate after the change lands.

**Empirical diagnosis driving the rewrite**:
- 307 SignalClusters in local DB; latest 25 are **100%** keyed by the
  pre-1139 `kw:<first PATTERN_TYPE_KEYWORD>` fallback path. Names like
  "Now opportunity window" (13 sources) lumped Trump phone + Hubble
  galaxy + UK Ebola vaccine + NFL playoffs together.
- signal-studio LLM judge: **112 rejected / 131 total = 85.5%
  rejection rate**. That's the SLO baseline.
- Same name-string repeated ≥2x in 4/15 latest sample = ~27% near-dup
  rate (Rigby's parallel empirical check using `intelligence_tool`).

**Test posture**: 24 new pure-function tests in
`test_signal_aggregation_entity_clusterer.py` (all passing). 1
existing `test_fleet_signals_phase1` test updated for the new envelope
key (also passing). 84/84 across signal-adjacent suites green.

**Local live verification BLOCKED** by Postgres `$libdir/vector` path
mismatch on SpiderData queries — same parking pattern as Session
1138's `test_fleet_signals_phase1.py` integration tests. Live SLO
measurement is Session 1140's first task once this merges to a stack
with working pgvector (production / Docker).

## What landed (u-d-b, branch `feat/session-1139-upstream-clustering-quality`)

| Path | Change |
|---|---|
| `core/models_signal_intelligence.py` | `SignalCluster.cluster_method` CharField (`legacy` / `entity_token_v1`), db_index'd, default `entity_token_v1`. |
| `core/migrations/0351_session_1139_cluster_method.py` | AddField + RunPython that backfills all 307 existing rows to `legacy`. Hand-trimmed: makemigrations auto-included unrelated NarrativeShift / AgentExecution / FleetPAChatAuditRow ops from prior partial work — stripped to keep Session 1139 PR minimal. |
| `core/services/signal_aggregation_service.py` | Entity-token clusterer constants (`CLUSTER_METHOD_V1`, `MIN_ENTITY_TOKEN_LENGTH`, `MIN_TOKEN_FREQUENCY_IN_WINDOW`, `MIN_SHARED_TOKENS`, `PER_PATTERN_MIN_CLUSTER_SIZE`, 72-token `NEWS_BOILERPLATE_TOKENS` denylist, regex). New `_extract_entity_tokens` helper. `_cluster_signals` rewritten as entity-token Union-Find. `_create_signal_clusters` tags new rows with `cluster_method=v1` and looks up existing rows by `(cluster_method, pattern_type, keywords__contains=key_tokens)`. `_generate_cluster_name` handles `"tok1|tok2"` v1 format with Title-cased tokens; legacy single-token path preserved for back-compat. |
| `core/services/fleet_signals.py` | `cluster_envelope` emits `cluster_method`, falling back to `legacy` if missing. So signal-studio's mirror records which clusterer produced each row. |
| `tests/services/test_signal_aggregation_entity_clusterer.py` | 24 new pure-function tests across 6 classes: entity extraction (basic, ALL-CAPS exclusion, denylist, hyphenated, camel-case, per-signal cap, empty), clusterer collapse (Tableau dup-merge, two-topic separation), rejection (heterogeneity, one-off entities, no-token signals), per-pattern min size (opportunity_window=4 vs default=3), name generation (v1 csv format + legacy back-compat), degenerate inputs, extract_signals wiring. |
| `tests/services/test_fleet_signals_phase1.py` | Existing `test_basic_envelope_shape` updated for new key; new `test_envelope_includes_cluster_method` exercises both `legacy` and `entity_token_v1` paths. |

## Empirical baseline (locked 2026-05-24 11:18 local time)

```text
SignalCluster (u-d-b):
  total: 307
  by pattern_type:
    trend_emergence: 97
    opportunity_window: 72
    demand_spike: 71
    skill_demand: 58
    sentiment_shift: 6
    knowledge_gap: 3
    (zero rows: content_gap, competitive_signal, market_movement, user_need)
  by status: archived=128, decayed=95, active=50, detecting=34
  by cluster_method (post-backfill): legacy=307

signal_clusters (signal-studio mirror):
  total: 131
  rejected:   112 (85.5%)  ← LLM judge rejection rate to BEAT
  summarized:  19 (14.5%)
```

Latest-25 sample cluster names confirmed 100% generic-verb-fallback:
`Now opportunity window` x3, `Before opportunity window` x3, `Rising
emerging trend` x4, `Need demand spike` x2, etc. Sample evidence
under "Now opportunity window" (13 sources) included Trump phone +
Hubble galaxy MACS J1141 + UK Ebola vaccine + NFL playoffs.

## Why entity-token + the design choices Rigby anchored

**Diagnosis** (`core/services/signal_aggregation_service.py:259-282`
pre-1139): `_cluster_signals` keyed clusters by either (a) regex topic
match against 10 broad patterns (`AI`, `crypto`, `startup`...) OR (b)
literal first PATTERN_TYPE_KEYWORD (`now`, `need`, `rising`, `role`).
Path (b) fired for ~100% of latest clusters because spider content is
news-shaped (specific entities), not topic-tag-shaped (broad topics).
Generic-verb clusters → heterogeneous evidence → 85.5% LLM rejection.

**Rigby's design ratifications** (Q1–Q5 from her review of the
empirical diagnosis):

| Q | Decision | Why |
|---|----------|-----|
| Q1 — what to do with 307 existing rows | Don't re-cluster. Add `cluster_method` discriminator; downstream filters new rows in via `cluster_method=v1`. Legacy rows decay naturally (95/307 already decayed). Bulk-archive legacy after 7–14 days, not now. | Cross-system mapping to "rejected equivalents" is more surface area than the clustering fix itself. Self-cleaning system. |
| Q2 — regex vs NER | Regex v1 — but add boilerplate denylist (Today / Breaking / FDA / NFL...) AND a `token must appear in ≥2 signals within the window` throttle so we don't trade verb-clusters for capitalized-garbage-clusters. | Optimizing for *stopping junk now* > extracting perfect entities. NER is a Session 1140+ option if telemetry says we need it. |
| Q3 — `signal_studio_judge_stats` PA tool | Yes. Becomes the SLO/acceptance test. | "Can't call the rewrite done without seeing the rejection rate drop materially." DEFERRED to Session 1140 to keep this session small; signal-studio's existing `/api/summarizer-status` + docker exec is good enough for the first measurement. |
| Q4 — retire dead pattern_types | Not this session. Keep the enum, deprecate the keyword tables as *naming* inputs. | Decide in 1-2 weeks based on telemetry. Don't bundle independent surgery. |
| Q5 — `cluster.name` consumers | `name` is display-only. Categorical consumers must use `pattern_type`. | Existing fleet_signals envelope already does this — no breakage. |

**Extra defensive note from Rigby**: define the clustering window
explicitly. The entity-token clusterer is bounded by
`SignalAggregationService(lookback_hours=N)` already — default 6h,
configurable. No code change needed; documenting here so it's not
implicit.

## How the entity-token clusterer works

1. **Tokenize per-signal**: extract capitalized noun-ish tokens via
   regex `\b([a-z]?[A-Z][a-zA-Z][a-zA-Z\-]+)\b`. Allows iPhone /
   OpenAI / Anti-Corruption. Excludes ALL-CAPS acronyms via length
   floor (FDA/FBI/DOJ = 3 chars < `MIN_ENTITY_TOKEN_LENGTH=4`).
   Drops `NEWS_BOILERPLATE_TOKENS` (72 entries: Today, Breaking,
   Inc, FDA, NFL, day names, month names, etc.). Capped at
   `MAX_ENTITY_TOKENS_PER_SIGNAL=8` per signal.

2. **Window-frequency throttle**: build global token frequency
   across the lookback window. Drop tokens with freq <
   `MIN_TOKEN_FREQUENCY_IN_WINDOW=2`. Prevents one-off proper nouns
   from forming clusters.

3. **Union-find on shared tokens**: O(n²) pairs (n ≤ 500 from
   upstream cap). Two signals merge when they share ≥
   `MIN_SHARED_TOKENS=2` frequent tokens.

4. **Per-pattern min size**: `opportunity_window=4` (was noisiest at
   72/307 rows pre-1139), default 3 elsewhere.

5. **Cluster key**: top-2 tokens by within-group frequency. Sorted
   `(-freq, alphabetical)` so the most-discriminative token leads
   the name. Format `"tableau|developer"` → name `"Tableau,
   Developer skill demand"`.

6. **Tag the row**: `cluster_method='entity_token_v1'`. Downstream
   consumers filter on this to opt new rows into any new quality bar.

## Live verification protocol (Session 1140 acceptance test)

This session's verification is purely synthetic (24 unit tests).
Local live verification was BLOCKED by Postgres `$libdir/vector` path
mismatch — same local-env issue parking
`test_fleet_signals_phase1.py` integration tests since Session 1131.
Production has working pgvector.

**After merge, Session 1140 step 1**:

```bash
# 1. Wait 24-48h for celery beat to produce v1 clusters in production
#    (signal_aggregation_service runs on the existing schedule).
# 2. Pull the post-merge breakdown:

# u-d-b side — what fraction of new clusters are v1?
.venv/bin/python manage.py shell -c "
from core.models_signal_intelligence import SignalCluster
from collections import Counter
recent = SignalCluster.objects.filter(detected_at__gte='<24h-ago>')
print(f'last 24h total: {recent.count()}')
print('by cluster_method:')
for cm, n in Counter(recent.values_list('cluster_method', flat=True)).most_common():
    print(f'  {cm}: {n}')
"

# signal-studio side — rejection rate for v1 vs legacy mirrors.
cd ~/development/signal-studio
docker compose exec -T signal_studio_postgres psql -U signalstudio -d signalstudio -c \\
  \"SELECT cluster_method, summary_quality, COUNT(*) FROM signal_clusters
    GROUP BY 1, 2 ORDER BY 1, 2;\"
```

**Acceptance bar (locked with Rigby):**
- v1 rejection rate **< 30%** → declare victory, ship Rigby's PA tool
  for ongoing SLO visibility, queue legacy bulk-archive for Session
  1141.
- v1 rejection rate **30–60%** → partial win, decide whether Option B
  (embedding-based clustering) is worth the spend.
- v1 rejection rate **≥ 60%** → close to baseline failure, escalate
  to Option B.

Note: signal-studio's mirror needs the `cluster_method` column added
to receive the envelope field. Today's signal-studio
`signal_ingest.py` should accept-and-ignore the new key (forward
compat). The mirror schema change is a separate small signal-studio
PR — included in the Session 1140 first-step work.

## Honest scope notes

- **Live RUN through real SpiderData**: not executed locally. Local
  Postgres can't load the pgvector extension via the standard
  `$libdir/vector` path so any query touching SpiderData fails at
  cursor exec time. Same blocker that's parked
  `test_fleet_signals_phase1.py` integration paths since Session
  1131. Synthetic unit tests cover all the algorithmic behavior.
- **Signal-studio mirror schema change** for `cluster_method` is not
  in this PR. Until that ships, the envelope key is silently dropped
  by signal-studio (forward compat). Session 1140 includes the
  matching signal-studio PR.
- **Rigby's `signal_studio_judge_stats` PA tool** is deferred to
  Session 1140 — small (~50 LOC across 2 repos) but waiting until we
  have first-day v1 data to wrap a tool around.
- **`SERVICES.md` drift**: still says 320 service files; reality is
  336. Not touched this session.

## Files touched (summary)

```
u-d-b (branch feat/session-1139-upstream-clustering-quality):
  core/models_signal_intelligence.py            #  +20 / -0   (cluster_method field)
  core/migrations/0351_session_1139_cluster_method.py   #  +66 / -0   (new file)
  core/services/signal_aggregation_service.py   # +298 / -36  (entity-token clusterer)
  core/services/fleet_signals.py                #   +6 / -0   (envelope cluster_method)
  tests/services/test_signal_aggregation_entity_clusterer.py   # +325 / -0  (new file, 24 tests)
  tests/services/test_fleet_signals_phase1.py   #  +27 / -5   (envelope shape + new test)
```

## Test posture

- **24/24 new clusterer tests passing** (`tests/services/test_signal_aggregation_entity_clusterer.py`)
- **84/84 signal-adjacent suites passing** (clusterer + fleet_signals_phase1 + signal_curator_phase2)
- **Migration 0351 applied locally**: all 307 existing rows backfilled to `cluster_method='legacy'`
- **Synthetic clustering verified**: Tableau-job dup-merge → 1 cluster; Trump+Hubble+NFL heterogeneity → 0 clusters; window-frequency throttle blocks single-token clusters
- **DB-dependent integration parked**: pgvector local env block — verification deferred to post-merge stack run

## Carryover into Session 1140

**FIRST THING** — Live rejection-rate measurement (protocol above).

**SECOND** — Ship Rigby's `signal_studio_judge_stats` PA tool
once we have 24-48h of v1 data to wrap visibility around.

**THIRD** — Signal-studio mirror schema for `cluster_method`
(small PR in signal-studio repo).

**Inherits from start-here** — everything from Session 1138's entry
remains: Chris ratification pass on Jessica's 22 decisions, tech queue
items (Contract Concierge / Signal Studio enrichment / Phase 0
cost-attribution schema / etc.), (Y) reject-mode flip post audit
telemetry window, (A) action-card pre-gen.
