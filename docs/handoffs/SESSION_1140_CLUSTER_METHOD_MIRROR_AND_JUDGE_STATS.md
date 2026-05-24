---
title: "Session 1140 — Mirror cluster_method + signal_studio_judge_stats PA tool"
date: 2026-05-24
status: merged
session: 1140
previous_handoff: SESSION_1139_UPSTREAM_CLUSTERING_QUALITY.md
next_session_primary: Live rejection-rate measurement (Session 1139 acceptance test) — gated on 24-48h post-merge beat aggregation + working pgvector
team: chris + claude + rigby (PR-review pass)
signal_studio_pr: 17
udb_pr: 2169
signal_studio_merge_commit: 19dfe102
udb_merge_commit: 4086019d
signal_studio_merged_at: 2026-05-24T21:02:50Z
udb_merged_at: 2026-05-24T21:03:46Z
---

# Session 1140 — Mirror `cluster_method` + `signal_studio_judge_stats` PA tool

> **Read this if** you want the Session 1140 closure of Session 1139's
> SECOND + THIRD work items: how the signal-studio mirror now stores
> `cluster_method`, what `/api/judge-stats` returns, and how Rigby's
> `signal_studio_judge_stats` PA tool surfaces the rejection-rate per
> clusterer without `docker exec`.

> **Merge status (2026-05-24):**
> - signal-studio PR [#17](https://github.com/clwest/signal-studio/pull/17) — squash-merged at `19dfe102` (2026-05-24T21:02:50Z). 3 checks green (verify-doc-claims, GitGuardian, Vercel Preview Comments). Vercel preview deploy FAILURE noted on merge — non-local, backend-only diff couldn't have caused it, proceeded per `feedback_local_only_default.md` (non-local CI doesn't block local-only merges).
> - u-d-b PR [#2169](https://github.com/clwest/donkey-betz-platform/pull/2169) — squash-merged at `4086019d` (2026-05-24T21:03:46Z). 3 checks all CLEAN (Direct LLM SDK, Repo Guardrails, GitGuardian).
> - Source branches: `feat/session-1140-cluster-method-mirror` (signal-studio, 2 commits before squash: `fb2285c` + `274d10a`); `feat/session-1140-signal-studio-judge-stats-tool` (u-d-b, 3 commits before squash: `c9b0e444` + `0eb3f1d9` + `1e120422`). Both branches deleted on merge.
> - **Deploy reminder:** PA tool registration needs both daphne AND celery restart for the registry to pick up — per canonical PA notes in `00-START-NEXT-SESSION.md`. Not done yet (next-session work).

> **Rigby design-review pass (PR #2169, conversation `pa-d19c1674b936`):** Six-question review (Q1–Q6) ran mid-session. Rigby's only merge-blocker — stale SLO numbers in the LLM-facing schema description — was fixed in `0eb3f1d9`. Acceptance bar + 85.5% baseline relocated from the schema into this handoff doc + start-here, where they belong. Nice-to-have (`status_code` on HTTP failures) also landed in the same commit. Sync httpx, days clamping, env var name (`SIGNAL_STUDIO_API_URL`), `{ok, error, days}` envelope shape, single-PR vertical slice — all confirmed correct, no change required.

## TL;DR

**Closed Session 1139's SECOND (mirror schema accepts `cluster_method`)
+ THIRD (Rigby's `signal_studio_judge_stats` PA tool) in two
coordinated PRs.** The signal-studio mirror now persists the
`cluster_method` discriminator that u-d-b's cluster envelope has been
shipping since Session 1139 — previously accept-and-ignored. The new
`/api/judge-stats` endpoint returns the LLM auto-summarizer judge's
accept/reject breakdown at three levels (total, by_cluster_method,
by_pattern_type), and the matching PA tool surfaces it conversationally
so Chris can ask Rigby "how is the entity-token clusterer doing?"
without docker-exec'ing into Postgres.

**What this unblocks:** the FIRST THING from Session 1139 — the
live rejection-rate measurement — becomes a single tool call (or
single curl) instead of a multi-line SQL hand-roll. Acceptance
bar stays Rigby-locked: `by_cluster_method.entity_token_v1.rejection_rate`
< 30% (victory) / 30-60% (partial) / ≥ 60% (escalate). Pre-1139
baseline was 112/131 = 85.5% rejection on legacy clusters.

**Test posture**: 11 new unit tests on the PA-tool handler (mocked
httpx, covers default-days, clamping, happy path, HTTP error, network
error, non-JSON 200, env override, trailing-slash normalization). Both
signal-studio smoke paths (mirror fresh-install + upgrade-install +
endpoint cross-tab math) verified locally against SQLite.

**Local live verification of the full pipeline still BLOCKED** by the
pgvector `$libdir/vector` path mismatch — same blocker that's parked
`test_fleet_signals_phase1.py` integration paths since Session 1131
and parked Session 1139's live SLO measurement.

## What landed

### signal-studio PR [#17](https://github.com/clwest/signal-studio/pull/17)

Two commits on `feat/session-1140-cluster-method-mirror`:

| Commit | Path | Change |
|---|---|---|
| `fb2285c` | `backend/app/models.py` | `cluster_method = Column(String(32), default="legacy", index=True)`. Width matches u-d-b's `CharField(max_length=32)`. |
| `fb2285c` | `backend/app/signal_ingest.py` | `_ensure_schema`: idempotent `ALTER TABLE … ADD COLUMN cluster_method VARCHAR(32) DEFAULT 'legacy'` + `CREATE INDEX IF NOT EXISTS`. Existing rows pre-1140 backfill to `'legacy'` on first boot (matches u-d-b migration 0351 pattern). |
| `fb2285c` | `backend/app/signal_ingest.py` | `upsert_cluster_from_envelope`: persists `envelope.get('cluster_method') or 'legacy'` on insert + update branches. |
| `274d10a` | `backend/app/main.py` | `GET /api/judge-stats?days=N` (1..90, default 7). Returns `{days, since, total, summarized, rejected, raw, rejection_rate, by_cluster_method, by_pattern_type}`. `pattern_type` resolved from `extra_data['pattern_type']` because it's never been a first-class mirror column. `rejection_rate` denominator excludes `summary_quality='raw'` (not-yet-judged) so a backlog spike can't mask quality. |

### u-d-b PR [#2169](https://github.com/clwest/donkey-betz-platform/pull/2169)

Two commits on `feat/session-1140-signal-studio-judge-stats-tool`:

| Commit | Path | Change |
|---|---|---|
| `c9b0e444` | `core/services/pa_tool_schemas.py` | New schema in `PA_TOOL_SCHEMAS`. Entries in `TOOL_ENRICHMENT_MAP` (`[]`, no enrichment) and `TOOL_TO_INTENT_MAP` (`'system_health'`, matches `paid_interest_status`). |
| `c9b0e444` | `core/services/td_handlers_core.py` | `_handle_signal_studio_judge_stats` — httpx GET to `${SIGNAL_STUDIO_API_URL:-http://localhost:8007}/api/judge-stats?days=N`. Days clamped to 1..90 (mirrors endpoint bounds). signal-studio is auth-less by design (per `config/external_repos/signal-studio.json`) so no fleet HMAC needed. All failure modes return `{ok: False, error: ...}` envelope, never raise. |
| `c9b0e444` | `core/services/tool_dispatcher.py` | Registry registration alongside `paid_interest_status`. |
| `c9b0e444` | `tests/services/test_signal_studio_judge_stats_tool.py` | 11 unit tests covering default days, clamping (both bounds + garbage input), happy path, HTTP 500, network error, non-JSON 200, env override, trailing-slash normalization. |
| `0eb3f1d9` | `core/services/pa_tool_schemas.py` | Rigby review (Q1): stripped acceptance bar + 85.5% baseline from the LLM-facing schema description. Replaced with evergreen wording ("counts of clusters accepted vs rejected, with rejection_rate broken down by cluster_method and pattern_type"). Stale numbers in the schema bias the LLM toward an out-of-date target. |
| `0eb3f1d9` | `core/services/td_handlers_core.py` | Rigby review (Q3 nice-to-have): added `status_code` to HTTP failure envelopes. Surfaced on non-200 (actual code) + 200-but-unparseable-JSON (200, so callers can distinguish "endpoint live but returning HTML" from "endpoint down"). Not surfaced on transport-layer failures — no response object exists. |
| `0eb3f1d9` | `tests/services/test_signal_studio_judge_stats_tool.py` | Updated 500-path test to assert `status_code == 500`. Updated non-JSON-200 test to assert `status_code == 200`. Updated network-error test to assert `status_code` is absent. Still 11/11 passing. |

**Inventory deltas:**
- PA tool schemas: 104 → **105**
- ToolDispatcher registered handlers: 169 → **170**

## Acceptance protocol (carried forward from Session 1139)

After both PRs merge + 24-48h of celery-beat aggregation against
production-like data, run one of:

### Option A — Rigby (preferred, post-deploy)

```text
"signal_studio_judge_stats with days=7"
```

Reads `by_cluster_method.entity_token_v1.rejection_rate` from the
response.

### Option B — curl (direct, no Rigby dependency)

```bash
curl -s "https://signal-studio.../api/judge-stats?days=7" | jq .by_cluster_method
```

### Option C — docker exec (fallback)

```bash
cd ~/development/signal-studio
docker compose exec -T signal_studio_postgres psql -U signalstudio -d signalstudio -c \
  "SELECT cluster_method, summary_quality, COUNT(*) FROM signal_clusters
   GROUP BY 1, 2 ORDER BY 1, 2;"
```

**Acceptance bar (Rigby-locked Session 1139, unchanged):**
- v1 rejection rate **< 30%** → declare victory; queue legacy
  bulk-archive for Session 1141.
- v1 rejection rate **30–60%** → partial win; decide whether Option B
  (embedding-based clustering) is worth the spend.
- v1 rejection rate **≥ 60%** → close to baseline failure; escalate.

## Honest scope notes

- **Live HTTP path not exercised this session.** Unit tests mock
  httpx. The end-to-end (Rigby → handler → signal-studio →
  Postgres → response) round-trip lands when both PRs are merged
  and Chris asks Rigby the question — failure modes from a
  real network path may differ from the mocked ones.
- **`pattern_type` lives in `extra_data['pattern_type']`** on the
  signal-studio side, never promoted to a first-class column. The
  endpoint reads it from the JSON blob; works fine for cardinalities
  we have today (<20 distinct pattern types) but would warrant
  promotion to a column if the row count or query frequency grows.
- **Pre-1140 mirror rows have `cluster_method='legacy'`** after the
  `_ensure_schema` ALTER fires on first boot — matches u-d-b's
  migration 0351 backfill semantics. The judge-stats endpoint will
  show these in the `legacy` bucket from day one even though they
  were ingested before u-d-b shipped the discriminator.
- **Stripe + httpx missing from `backend/.venv`** on the signal-studio
  side as discovered during smoke testing — `pip install` ran cleanly
  but not committed (deps already listed in `requirements.txt`). Not
  this PR's concern; flagging for future smoke-test sessions.
- **Daphne + celery restart required** on u-d-b after merge. Each
  celery worker loads its own tool registry — registration is not
  visible until both daphne and every celery worker process is
  restarted. Per the canonical PA notes in `00-START-NEXT-SESSION.md`.

## Test posture

- **11/11 PA-tool handler tests passing** in `tests/services/test_signal_studio_judge_stats_tool.py`
- **Django boot + ToolDispatcher.__init__** registers the handler cleanly (verified: `_tool_handlers["signal_studio_judge_stats"]` resolves to `_handle_signal_studio_judge_stats`).
- **Schema-level checks**: `PA_TOOL_SCHEMAS` count 104 → 105; `_tool_handlers` count 169 → 170.
- **signal-studio mirror smoke (SQLite)**: fresh-install + upgrade-install paths both green, `_ensure_schema` idempotent across calls.
- **signal-studio endpoint smoke (SQLite + FastAPI TestClient)**: synthetic grid of 12 in-window rows + 1 old-row exclusion, cross-tab math matches hand-calc (`entity_token_v1` 1/5 = 0.2, `legacy` 6/7 = 0.8571, `opportunity_window` 5/5 = 1.0).
- **Live HTTP / Postgres path**: not exercised. Verified at next live Rigby call.
- **CI status**: TBD (PR pending; update post-merge).

## Files touched (summary)

```
signal-studio (branch feat/session-1140-cluster-method-mirror, PR #17):
  backend/app/models.py                  # +8 / -0   (cluster_method column)
  backend/app/signal_ingest.py           # +27 / -0  (ensure_schema + upsert persistence)
  backend/app/main.py                    # +99 / -0  (/api/judge-stats endpoint)

u-d-b (branch feat/session-1140-signal-studio-judge-stats-tool, PR #2169):
  core/services/pa_tool_schemas.py       # +37 / -0   (schema + 2 map entries; evergreen description post-review)
  core/services/td_handlers_core.py      # +68 / -0   (_handle_signal_studio_judge_stats + status_code on failures)
  core/services/tool_dispatcher.py       # +9  / -0   (register call)
  tests/services/test_signal_studio_judge_stats_tool.py  # +183 / -0  (11 tests, new file; status_code assertions added post-review)
```

## Carryover into Session 1141

**FIRST THING — Live rejection-rate measurement (Session 1139 acceptance test).**
Still gated on:
1. Both Session 1140 PRs merged.
2. 24-48h of celery-beat aggregation against production-like data so
   the v1 clusterer has produced enough rows for a real measurement.
3. Working pgvector (production or fixed docker env) — local
   `$libdir/vector` block still in effect.

Once those land, the protocol is one of (A/B/C) above. Acceptance bar
is Rigby-locked at <30% (victory) / 30-60% (partial) / ≥60% (escalate).

**Open carryovers (unchanged from Session 1139 close, see `00-START-NEXT-SESSION.md` for full list):**

- (Y) Reject-mode flip in `unified_pa_chat` — gated on 3-day clean
  audit telemetry post-merge.
- (A) Action-card pre-generation for curated — visible-feature
  alternative, design fork locked (child rows, not payload blob).
- Legacy SignalCluster bulk-archive (post-victory follow-up).
- signal-studio mirror dep gap: `stripe` + `httpx` were missing from
  `backend/.venv` until ad-hoc `pip install` this session. Not
  committed. Future smoke-test sessions should re-pip from
  `requirements.txt` rather than assume venv is current.
- Chris's tech queue + Phase 5 audit queue items still open
  (unchanged from Session 1138 / 1139 close).

## Companion docs

- [SESSION_1138_F1_PAID_INTEREST_IMPLEMENTATION](SESSION_1138_F1_PAID_INTEREST_IMPLEMENTATION.md) — Decision 13 demand-gate (the architectural sibling tool: `paid_interest_status`).
- [SESSION_1139_UPSTREAM_CLUSTERING_QUALITY](SESSION_1139_UPSTREAM_CLUSTERING_QUALITY.md) — entity-token clusterer + `cluster_method` discriminator that this session's mirror + PA tool consume.
- `core/services/td_handlers_core.py:_handle_paid_interest_status` — direct sibling for tool pattern (delegate-to-helper vs httpx-to-fleet-app).
- `config/external_repos/signal-studio.json` — confirms signal-studio is auth-less, fleet-net hostname is `signal_studio_api:8007`.

---

*Draft scaffold written during Session 1140 — pre-merge. After both
PRs land, update header `merged_at` + commit SHAs, flip `status` to
`merged`, and overwrite `00-START-NEXT-SESSION.md` to point Session
1141 at the FIRST THING measurement protocol.*
