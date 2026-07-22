# `heartbeat_history_tool` — Validation Report (S2892)

**Tool:** `heartbeat_history_tool`
**Schema:** `core/services/pa_tool_schemas.py:5261`
**Handler:** `core/services/td_handlers_ops.py:7214` (`_handle_heartbeat_history`)
**Register site:** `core/services/tool_dispatcher.py:611`
**Session:** S2892 (Path B systematic sweep — Slice 1 batch 1 of `td_handlers_ops`)
**HEAD at validation:** `81502903d`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (every action in the schema `action` enum exercised live).
**Rigby SIGN:** S2892 T1 SIGN AGREE-WITH-EDITS.

---

## 1. Purpose / when-to-use

Read-only view over the `HeartBeat` model. Two shapes: (a) `recent` — most recent N heartbeat rows with per-row health snapshot, (b) `trends` — aggregated stats over an hours window. Use when asked about system health trends over time, uptime, or historical status.

Distinct from `status_snapshot_tool` (which reads current health as one of 12 sections) and `get_body_vitals` (which reads live per-body-system state) — `heartbeat_history_tool` is scoped to historical HeartBeat rows.

## Covered actions

- `recent` — **in scope this ship** — verified live (see §6.1). Returns last N heartbeats (default 20) with health_score, overall_status, is_alive, per-heartbeat component counts, check_duration_ms, recorded_at.
- `trends` — **in scope this ship** — verified live. Returns aggregate over hours window (default 24): total_heartbeats, avg/min/max health_score, avg_check_duration_ms, status_distribution.

## 3. Schema notes

- **Required:** `action` (enum: `recent, trends`).
- **`limit`** — integer, applies only to `recent`. Default 20. No documented upper cap in schema (handler behavior with excessively large limits unverified).
- **`hours`** — integer, applies only to `trends`. Default 24.
- **Schema description lint:** clean — describes both actions distinctly.

## 4. Golden-path examples

**Last 20 heartbeats:**

```
heartbeat_history_tool  action=recent
```

**7-day trends:**

```
heartbeat_history_tool  action=trends  hours=168
```

**Deep recent view (up to N):**

```
heartbeat_history_tool  action=recent  limit=100
```

## 5. Failure / empty-state / pagination notes

- **Empty state:** if `HeartBeat` table has no rows in-window, `recent` returns `count: 0, heartbeats: []`; `trends` returns `total_heartbeats: 0` with null aggregates (behavior not exercised live).
- **No offset pagination** — `recent` supports `limit` only. To page further back, would need explicit date range params (not in schema).
- **Semantic anomaly worth noting** — see §6.1: at S2892 T1, all 137 heartbeats over 24h returned `health_score: 87.5` (min=max=avg). Either the scoring collapsed to a fixed value or one component perpetually returns `degraded` (7 healthy / 1 degraded per heartbeat) driving the constant. Not a tool defect, but a downstream signal worth investigation. **Ledger candidate.**

## 6. Evidence

### 6.1 Observed runs — this ship

Rigby's live dispatches at S2892 T1 (2026-07-22, HEAD `81502903d`, pin `pa-373cf02ba2344b13`):

**`recent` (9ms):** returned 20 heartbeat rows. First 4 rows all identical shape:

```json
{"health_score": 87.5, "overall_status": "healthy", "is_alive": true,
 "components_checked": 8, "components_healthy": 7, "components_degraded": 1,
 "check_duration_ms": 3124, "recorded_at": "2026-07-22T22:09:21.746238+00:00"}
```

10-min spacing between rows confirms the beat-scheduled cadence.

**`trends` (7ms, hours=24):**

```json
{"action": "trends", "hours": 24, "total_heartbeats": 137,
 "avg_health_score": 87.5, "min_health_score": 87.5, "max_health_score": 87.5,
 "avg_check_duration_ms": 3163.1, "status_distribution": {"healthy": 137}}
```

**Score-flat observation:** min = max = avg = 87.5 across 137 heartbeats. Every heartbeat records components_checked=8, components_healthy=7, components_degraded=1 — one component is perpetually degraded. Score = 87.5 = 7/8. Suggests one body system reliably degrades and is scored deterministically. Not tool malfunction; downstream signal for follow-up.

### 6.2 Runtime-not-executed — this ship

- **Empty-state behavior** for both actions.
- **`limit > 20`** on `recent` — not exercised (no documented cap).
- **`hours` at extreme values** (e.g. 1, 720) — not exercised.
- **Trends with non-uniform score distribution** — cannot exercise until scores diverge.

---

## Related

- **S2795 gap map:** `docs/audits/PA_TOOLS_GAP_MAP_S2795.md`.
- **S2892 handoff:** `docs/handoffs/SESSION_2892_PA_TOOLS_SWEEP_SLICE_1_BATCH_1.md`.
- **Ledger candidate from this ship:** health_score collapsed to 87.5 across 137 heartbeats/24h. One component degrades deterministically; investigate which and why the score never fluctuates.
- **Related tools:** `status_snapshot_tool.health` section (current view of same HeartBeat table), `get_body_vitals` (live per-body-system read).
