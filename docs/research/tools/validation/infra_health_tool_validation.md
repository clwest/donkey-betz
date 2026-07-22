# `infra_health_tool` — Validation Report (S2892)

**Tool:** `infra_health_tool`
**Schema:** `core/services/pa_tool_schemas.py:5288`
**Handler:** `core/services/td_handlers_ops.py:7293` (`_handle_infra_health`)
**Register site:** `core/services/tool_dispatcher.py:612`
**Session:** S2892 (Path B systematic sweep — Slice 1 batch 1 of `td_handlers_ops`)
**HEAD at validation:** `81502903d`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (every action in the schema `action` enum exercised live).
**Rigby SIGN:** S2892 T1 SIGN AGREE-WITH-EDITS.

---

## 1. Purpose / when-to-use

Deep infrastructure health checks. Four orthogonal probes: Redis health, PostgreSQL performance, dependency matrix (web/db/redis/celery/pgvector/spiders/storage), and process/system runtime metrics. Use when asked about Redis health, DB performance, dependency status, memory usage, or any infra-level diagnosis.

Distinct from `heartbeat_history_tool` (historical HeartBeat table read) and `status_snapshot_tool` (broad 12-section snapshot) — `infra_health_tool` runs each probe LIVE at dispatch time.

## Covered actions

- `redis_health` — **in scope this ship** — verified live (see §6.1). Live Redis PING + INFO probe. Returns ping_ms, connected_clients, memory usage, keyspace hit/miss + hit_rate_pct, evicted_keys.
- `db_perf` — **in scope this ship** — verified live. Live pg_stat_activity + pg_stat_database read. Returns connections (total/active/idle/idle_in_transaction/longest_query_secs), cache_hit_ratio_pct, transactions, tuples, deadlocks.
- `dependency_matrix` — **in scope this ship** — verified live. Runs a per-component check across 7 subsystems (web, postgres, redis, celery, pgvector, spiders, storage). Returns per-component status + overall verdict.
- `runtime_metrics` — **in scope this ship** — verified live. Process (RSS/VMS/CPU/threads/uptime) + system (RAM/disk/CPU count) + Railway env fields.

## 3. Schema notes

- **Required:** `action` (enum: `redis_health, db_perf, dependency_matrix, runtime_metrics`).
- **No other params** — each action is deterministic with no tunables.
- **Schema description lint:** clean — description enumerates all four probes with what each returns.

## 4. Golden-path examples

**Redis pulse check:**

```
infra_health_tool  action=redis_health
```

**End-to-end dependency verdict (call this when asked "is anything down?"):**

```
infra_health_tool  action=dependency_matrix
```

**DB perf snapshot:**

```
infra_health_tool  action=db_perf
```

**Process/system resource read:**

```
infra_health_tool  action=runtime_metrics
```

## 5. Failure / empty-state / pagination notes

- **No pagination** — each action returns fixed-shape response.
- **`dependency_matrix` is the slowest** — 5176ms observed live (fans out to 7 subsystem checks). All others sub-200ms.
- **`redis_health` masks `maxmemory=0B` / `maxmemory_policy=noeviction`** as raw values — a live probe reports what it sees; no interpretation of whether that config is safe for production. Not a defect.
- **`db_perf` returns `longest_query_secs` from `pg_stat_activity`** but does not surface the query text. Long-running queries visible as durations only — see §6.1 finding.
- **`runtime_metrics.vms_mb`** is often huge (100s of GB) due to Python mmap of large files; this is a normal reading, not a memory leak signal.

## 6. Evidence

### 6.1 Observed runs — this ship

Rigby's live dispatches at S2892 T1 (2026-07-22, HEAD `81502903d`, pin `pa-373cf02ba2344b13`):

**`redis_health` (7ms):**

```json
{"ping_ms": 0.37, "connected": true, "used_memory_human": "65.26M",
 "used_memory_peak_human": "66.48M", "maxmemory_human": "0B",
 "maxmemory_policy": "noeviction", "connected_clients": 96,
 "blocked_clients": 5, "evicted_keys": 0, "keyspace_hits": 18031,
 "keyspace_misses": 12264, "hit_rate_pct": 59.52,
 "total_commands_processed": 270845, "uptime_seconds": 0}
```

**Observation worth logging:** `hit_rate_pct: 59.52` is below the 80%+ typical target. May be normal for local dev with cold cache; worth confirming against production baseline. `blocked_clients: 5` also notable — Redis has 5 clients waiting on a blocked operation (e.g., BLPOP). Not tool defect but a signal.

**`db_perf` (15ms):**

```json
{"connections": {"total_connections": 60, "active": 1, "idle": 59,
                 "idle_in_transaction": 0, "longest_query_secs": 2302},
 "cache_hit_ratio_pct": 62.51,
 "transactions": {"committed": 2684902, "rolled_back": 3119},
 "tuples": {"returned": 3855908991, "fetched": 182894191, "inserted": 208730,
            "updated": 198043, "deleted": 116366},
 "deadlocks": 0, "conflicts": 0}
```

**Observation worth logging:** `longest_query_secs: 2302` (~38 min). Suggests a stuck cursor or long-running background job. Handler surface reports this correctly; investigation needed at pg_stat_activity level to identify the query. `cache_hit_ratio_pct: 62.51` is also below target 90%+.

**`dependency_matrix` (5176ms):**

```json
{"overall": "healthy",
 "components": {
   "web": {"status": "ok", "detail": "responding (this request succeeded)"},
   "postgres": {"status": "ok"},
   "redis": {"status": "ok"},
   "celery": {"status": "ok", "workers": 4},
   "pgvector": {"status": "ok", "version": "0.8.0"},
   "spiders": {"status": "ok", "items_last_2h": 11},
   "storage": {"status": "ok", "backend": "DefaultStorage"}},
 "total": 7, "healthy": 7, "warnings": 0, "errors": 0}
```

7/7 healthy. Latency 5176ms confirms this is the fan-out probe; use sparingly.

**`runtime_metrics` (108ms):**

```json
{"process": {"pid": 62488, "rss_mb": 234.5, "vms_mb": 425639.2,
             "cpu_percent": 0.1, "threads": 5, "uptime_seconds": 2311},
 "system": {"total_ram_mb": 18432.0, "available_ram_mb": 4348.1,
            "ram_percent": 76.4, "disk_total_gb": 460.4, "disk_used_gb": 11.7,
            "disk_percent": 11.9, "cpu_count": 12, "platform": "macOS-26.5.2-arm64-arm-64bit"},
 "railway": {"environment": "", "service": "", "deployment_id": "", "replica_id": ""}}
```

Local dev (Railway fields empty). RSS 234.5MB reasonable for the daphne worker.

### 6.2 Runtime-not-executed — this ship

- **`dependency_matrix` degraded-path** — cannot exercise until a real dependency fails.
- **`redis_health` under real memory pressure** (`evicted_keys > 0`) — cannot exercise on local dev with noeviction + 0B maxmemory.
- **`db_perf` deadlocks/conflicts non-zero** — cannot exercise without inducing a race.

---

## Related

- **S2795 gap map:** `docs/audits/PA_TOOLS_GAP_MAP_S2795.md`.
- **S2892 handoff:** `docs/handoffs/SESSION_2892_PA_TOOLS_SWEEP_SLICE_1_BATCH_1.md`.
- **Semantic-signal candidates from this ship (NOT tool defects — worth investigating separately):**
  1. Redis `hit_rate_pct: 59.52` (below 80%+ target) — may indicate cache-key churn or cold cache; compare to production baseline.
  2. Postgres `longest_query_secs: 2302` (~38 min stuck query). Identify + resolve at `pg_stat_activity` level.
  3. Postgres `cache_hit_ratio_pct: 62.51` (below 90%+ target).
  4. Redis `blocked_clients: 5` — 5 clients on blocked ops (BLPOP/BRPOP typically). Confirm if expected pattern.
- **Related tools:** `status_snapshot_tool` (broad snapshot with less depth), `heartbeat_history_tool` (historical view of aggregated health).
