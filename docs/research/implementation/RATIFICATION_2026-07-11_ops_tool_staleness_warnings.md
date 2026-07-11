---
title: "ops_tool.staleness_warnings PA Tool Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2760
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat SIGN (design → implementation) + Chris joint-recommend D-verdict
scope: S2759 warning-loop completion — new query action parallel to S2758 tenant_boundary_violations
serves_arc: S2759 stale-Daphne warning system
sibling_tools:
  - ops_tool.tenant_boundary_violations (S2758 — parallel-shape precedent)
  - ops_tool.version (S2759 — live freshness check that this action's warnings historically corroborate)
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-11_stale_daphne_warning_system.md (S2759 — Beat task whose emissions this action queries)
  - docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md (S2758 — parallel-shape design precedent)
ratified_documents:
  - core/services/pa_tool_schemas.py (amended — ops_tool action enum + staleness_warnings description)
  - core/services/td_handlers_ops.py (amended — elif branch + _ops_staleness_warnings method + _STALENESS_WARNING_VERDICTS constant)
  - tests/security/test_ops_tool_staleness_warnings.py (new — 9 tests, 189s runtime)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2760 — Rigby design SIGN turn 1 (pre-code): PASS on F1-F7 clean with 2 optional refinements (F4 nested-array response-size guardrail — not needed; F6 optional tighter empty-state phrasing — original phrasing kept)
  - S2760 — Rigby implementation SIGN turn 1 (post-code): PASS on F1-F7 clean, no edits; L1 known limitation (no live-emission E2E — Beat cadence 30 min + workers currently FRESH so no warning to emit) accepted
  - S2760 — Live E2E verification: ops_tool.staleness_warnings dispatched via Rigby PA loop, 10ms server-side, empty-state note returned cross-referencing ops_tool.version
frozen: true
test_results:
  local_test_count: 9
  local_test_pass_rate: "9/9"
  local_test_runtime_seconds: 189
---

# `ops_tool.staleness_warnings` PA Tool Ratification Record

Frozen canonical record of Chris's ratification of the new `ops_tool.staleness_warnings` PA tool on 2026-07-11. Completes the S2759 stale-Daphne warning system loop end-to-end (Beat task emits → tool queries → operator inspects). Parallel-shape lift from S2758 `ops_tool.tenant_boundary_violations`. Append-only; do NOT edit after commit.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Scope:** net-new PA tool. Not an arc phase-close.
- **Motivation:** S2759 shipped `check_process_staleness` Beat task emitting `OpsRunEvent(label='staleness_warning')` every 30 min when verdict != FRESH. S2760 open protocol's third check (query accumulated warnings) had no dedicated tool surface — Rigby proactively flagged the gap. Chris selected this as S2760 P0 from the open menu.
- **Ratifier:** Chris (D-verdict against joint Claude+Rigby recommendation)

---

## §2. Ratified Deliverables

### §2.1 `core/services/pa_tool_schemas.py` — `ops_tool` action enum extension

**Action enum extension** — `staleness_warnings` added to `ops_tool` action enum (24th action, after `tenant_boundary_violations`).

**Action description** (positioned before the tenant_boundary_violations block for chronological adjacency):

> `staleness_warnings`: query OpsRunEvent for S2759 staleness_warning envelopes emitted by the check_process_staleness Beat task (30 min cadence). Returns total_count + by_verdict + by_head_commit_sha aggregates + sample_events (most-recent) with process detail preserved. Optional filters: verdict (STALE_DAPHNE / STALE_CELERY / STALE_BOTH), limit (default 20, max 100). Empty state includes a diagnostic note cross-referencing ops_tool.version. Use to inspect accumulated stale-process warnings — especially post-merge to verify make recycle-all was run, or to audit which HEAD commits historically triggered warnings.

### §2.2 `core/services/td_handlers_ops.py` — `_ops_staleness_warnings` handler

**Elif branch** added after `tenant_boundary_violations` (line 364), delegates to `self._ops_staleness_warnings(payload, trace_id)`.

**Method** (~110 lines) placed after `_ops_tenant_boundary_violations` for adjacency with the parallel-shape sibling.

**Class constant** — `_STALENESS_WARNING_VERDICTS = ('STALE_DAPHNE', 'STALE_CELERY', 'STALE_BOTH')`. FRESH + UNKNOWN excluded because the Beat task never emits warnings for those verdicts.

**Enforcement algorithm:**

1. Resolve window (`1h`/`6h`/`24h`/`7d`/`30d` → hours delta; default `24h`).
2. Validate `verdict` against `_STALENESS_WARNING_VERDICTS`. Invalid → error response with allowed list.
3. Clamp `limit` to `[1, 100]` (default 20).
4. Query `OpsRunEvent.objects.filter(label='staleness_warning', created_at__gte=cutoff).order_by('-created_at')`.
5. Bound aggregation-side scan by `MAX_AGG_SCAN=5000` rows (F7 precedent) + set `aggregation_scan_capped: True` + `aggregation_scan_limit: 5000` on overrun.
6. Apply payload verdict filter Python-side (exact match).
7. Aggregate:
   - `by_verdict`: `dict[str, int]` counts per verdict class
   - `by_head_commit_sha`: `dict[str, int]` counts per short 12-char SHA — **the operational money bucket** answering "which merge did we forget to `make recycle-all` after?"
8. Sample events (up to `limit`):
   - Full `OpsRunEvent.detail` preserved: `verdict`, `head_commit_sha_short` (12 chars), `head_commit_timestamp`, `daphne_pid`, `daphne_pid_age_seconds`, `daphne_started_before_head_commit`, `celery_workers_status` (full unmodified list), `fix`, `created_at`
9. Empty-state note (Rigby F6 verbatim):

> "No staleness_warning events in the last {window}. Either verdict has been FRESH, or the check_process_staleness Beat task isn't emitting — confirm via ops_tool.version."

**Response shape:**

```
{
  "action": "staleness_warnings",
  "window": "24h",
  "window_cutoff": "<iso>",
  "verdict_filter": "(all)" | "<filter>",
  "total_count": int,
  "by_verdict": dict,
  "by_head_commit_sha": dict,
  "sample_events": [
    {"verdict", "head_commit_sha_short", "head_commit_timestamp",
     "daphne_pid", "daphne_pid_age_seconds",
     "daphne_started_before_head_commit", "celery_workers_status",
     "fix", "created_at"},
    ...
  ],
  // Optional:
  "aggregation_scan_capped": true,
  "aggregation_scan_limit": 5000,
  "note": "<diagnostic string>"
}
```

### §2.3 Test suite — 9 tests, 189s runtime, 9/9 passing

`tests/security/test_ops_tool_staleness_warnings.py` (new file):

- `test_empty_state_returns_note_and_zero_counts` — F6 empty state + cross-reference to ops_tool.version
- `test_aggregates_by_verdict_and_head_commit_sha` — F3 both buckets populate; SHA truncated to 12ch in aggregate key
- `test_sample_events_preserve_full_process_detail` — F4 exposure of verdict, head_commit_sha_short, timestamp, daphne pid/age, daphne_started_before_head_commit, full celery_workers_status, fix, created_at
- `test_sample_events_ordered_most_recent_first` — descending time order
- `test_verdict_filter_matches_exact_enum` — F2 exact enum filter
- `test_invalid_verdict_returns_error` — F2 typo guard with allowed list
- `test_window_filter_excludes_old_events` — window cutoff
- `test_limit_defaults_to_20_and_caps_at_100` — default + upper clamp
- `test_limit_min_clamps_to_one` — defensive lower clamp

Test approach (Rigby F5): handler-level unit tests via `_OpsProxy` mixin binding + synthetic seeded `OpsRunEvent` rows shaped like the real Beat task emissions.

---

## §3. Rigby SIGN Cycle

Two SIGN turns.

### §3.1 Design SIGN turn 1 (pre-code)

F1–F7 all PASS with 2 optional refinements:

- **F4 refinement (optional):** if any nested arrays (`celery_workers_status`) could blow up response size, optionally truncate per sample. Default should be full fidelity. **Applied resolution:** kept full fidelity — typical event carries ~5 workers, small volume.
- **F6 refinement (optional):** tighter phrasing on empty-state note. **Applied resolution:** kept original phrasing verbatim; Rigby said either works.

Q leans confirmed: QA=both aggregates · QB=full worker list · QC=proposed phrasing works · QD=parallel to S2758 (~10 tests) · QE=staleness_warnings action name.

### §3.2 Implementation SIGN turn 1 (post-code)

F1–F7 all PASS clean, no edits requested. L1 (no live-emission E2E) accepted — unit tests cover the round-trip; live emission requires stale processes which the current FRESH state precludes.

Live E2E verification: Rigby dispatched `ops_tool.staleness_warnings` post `make recycle-all`, tool executed 10ms server-side, empty-state note returned cross-referencing `ops_tool.version`. Tool wiring proven.

Joint recommend-to-Chris (final): *"APPROVE + MERGE. Completes the S2759 warning loop end-to-end (Beat emits → tool queries → operator inspects). S2760 open protocol is now a single Rigby round-trip going forward."*

---

## §4. Chris D-Verdict

**Verdict:** **APPROVED** ("approved, ship it" — S2760, 2026-07-11)

Two ratification points: original pre-code shape "approved" + final ship "approved, ship it". Zero unresolved menus routed per S2753 agree-first rule.

**Effect:** S2759 warning loop closed end-to-end. S2760 open protocol becomes a single Rigby round-trip (freshness check via `ops_tool.version` + accumulated findings via `ops_tool.tenant_boundary_violations` + `ops_tool.staleness_warnings` in one turn).

---

## §5. Operational Follow-Up

- **First real query:** at S2761 open (or any future session close touching ASGI/Celery-served code), Rigby can call `ops_tool.staleness_warnings, window=24h` to inspect accumulated warnings from the check_process_staleness Beat task.
- **Retroactive check post-S2761:** the Beat task has been running since S2759 merge; by S2761 open (~30+ min from now), the first Beat fire will have happened — either FRESH (silent) or STALE (envelope emitted). The tool will show accumulated history.

---

## §6. Provenance Chain

- **Predecessor session:** S2759 (stale-Daphne warning system ratification — Beat task whose emissions this action queries)
- **Sibling parallel-shape tool:** S2758 `ops_tool.tenant_boundary_violations` (same query pattern; same MAX_AGG_SCAN discipline; same aggregation shape)
- **Sibling live-check surface:** `ops_tool.version` (S2759 staleness_verdict) — the empty-state note cross-references this
- **Beat task emission source:** `core/tasks_beat_health.py::check_process_staleness` (S2759)
- **Engineering Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` — §7.4.x (close-ceremony 1-PR bundle) + §7.6.1 (SIGN watchpoint attestation, applied twice this session)
