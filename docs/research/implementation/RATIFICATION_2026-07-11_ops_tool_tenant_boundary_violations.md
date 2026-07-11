---
title: "ops_tool.tenant_boundary_violations PA Tool Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2758
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat SIGN (design → implementation) + Chris joint-recommend D-verdict
program_id: RUR (surfaces I-0303 substrate; not part of arc)
serves_arc: I-0303 (Phase 3 REPORT-ONLY findings surface)
serves_arc_workspace: fcd7e683-3bfe-4d35-9704-0e54dd587ea1
serves_arc_workspace_name: "RUR-C1 Tenant Boundary Lockdown"
scope: net-new PA tool (Chris S2745 engineering-bias directive)
predecessor_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md
  - docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md
ratified_documents:
  - core/services/pa_tool_schemas.py (amended — ops_tool action enum + failure_kind param + task_name description)
  - core/services/td_handlers_ops.py (amended — elif branch + _ops_tenant_boundary_violations method + _TENANT_BOUNDARY_FAILURE_KINDS constant)
  - tests/security/test_ops_tool_tenant_boundary_violations.py (new — 10 tests, 189s runtime)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2758 — Rigby design SIGN turn 1 (pre-code): PASS on F1-F6 with one F2 clarification (task_name icontains matching sibling celery_task_history)
  - S2758 — Rigby implementation SIGN turn 1 (post-code): PASS on F1-F7 (F7 defensive aggregation-scan cap added post-design)
  - S2758 — E2E verification (post-recycle): live Rigby PA loop invocation succeeded with two real findings surfaced (S2757 Path C smoke test + Rigby's own dispatch of process_pa_chat_task hitting missing_acting_identity — surfaces a dispatch-site gap outside the 4 S2757-converted sites, candidate for second BATCH-FIX pass follow-up)
frozen: true
tool_semantics:
  name: ops_tool
  action: tenant_boundary_violations
  scope: internal_operator_diagnostic
  discriminator_exposure: full (row_id + acting_user_id + support_code + trace_id + failure_kind + model_label preserved per Phase 2 §2.1 operator-side)
  rationale: this is INTERNAL operator surface — Rigby is trusted, Chris is the operator; the whole point of Phase 2's uniform-user-facing-envelope + operator-envelope-carries-discriminator design is that INTERNAL surfaces get the discriminator; PUBLIC surfaces get the sanitized envelope
test_results:
  local_test_count: 10
  local_test_pass_rate: "10/10"
  local_test_runtime_seconds: 189
---

# `ops_tool.tenant_boundary_violations` PA Tool Ratification Record

Frozen canonical record of Chris's ratification of the new `ops_tool.tenant_boundary_violations` PA tool on 2026-07-11. The tool surfaces I-0303 Phase 3 REPORT-ONLY substrate findings from `OpsRunEvent` for internal operator diagnostic use via Rigby chat. Append-only; do NOT edit after commit.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Scope:** net-new PA tool (not an arc phase-close). Per Chris S2745 engineering-bias directive: "list net-new engineering candidates FIRST; gate 'connect what's built' audits + constitutional-ADR unblocking + meta-methodology behind them."
- **Ratifier:** Chris (D-verdict against joint Claude+Rigby recommendation)
- **Serves I-0303 arc** — but is not part of it. Provides operator visibility into `tenant_boundary_violation` events emitted by the Phase 3 REPORT-ONLY substrate.
- **S2758 open menu:** 6 candidates offered; Chris selected #2 (`session_tool.recent_tenant_violations` shorthand — refined to `ops_tool.tenant_boundary_violations` via Rigby SIGN F1 domain-fit analysis).

---

## §2. Ratified Deliverables

### §2.1 `core/services/pa_tool_schemas.py` — `ops_tool` action enum + failure_kind param

**Action enum extension** — `tenant_boundary_violations` added to `ops_tool` action enum (now 23 actions).

**Action description** (appended to ops_tool description block):

> `tenant_boundary_violations`: query OpsRunEvent for I-0303 tenant_boundary_violation envelopes (Phase 3 REPORT-ONLY substrate). Returns total_count + by_task_name + by_failure_kind + by_task_and_kind aggregates + sample_events (most-recent). Optional filters: task_name (substring match), failure_kind (one of missing_row_id/row_not_found/missing_acting_identity/acting_user_not_found/unregistered_model/predicate_rejected), limit (default 20, max 100). Empty state includes a diagnostic note. Use when asked about tenant boundary violations, cross-tenant reports, I-0303 findings, or which tasks are surfacing report-only warn violations.

**New parameter** — `failure_kind` with enum of the 6 Phase 2 failure kinds. Optional. Guards against typos (invalid values are rejected with an allowed-list error).

**Extended parameter** — `task_name` description now mentions `tenant_boundary_violations` alongside `celery_task_history`.

### §2.2 `core/services/td_handlers_ops.py` — `_ops_tenant_boundary_violations` handler

**Elif branch** added after `zombie_thread_rate` (line 349), delegates to `self._ops_tenant_boundary_violations(payload, trace_id)`.

**Method** (~130 lines) placed after `_ops_celery_task_history` for adjacency with the sibling diagnostic-read pattern.

**Enforcement algorithm:**

1. Resolve window (`1h`/`6h`/`24h`/`7d`/`30d` → hours delta from `timezone.now()`; default `24h`).
2. Validate `failure_kind` against `_TENANT_BOUNDARY_FAILURE_KINDS` (the 6 Phase 2 kinds). Invalid → error response with allowed list.
3. Clamp `limit` to `[1, 100]` (default 20).
4. Query `OpsRunEvent.objects.filter(label='tenant_boundary_violation', created_at__gte=cutoff).order_by('-created_at')`.
5. Bound the aggregation-side scan by `MAX_AGG_SCAN=5000` rows (Rigby F7 defensive guard against violation-flood scenarios). Overrun sets `aggregation_scan_capped: True` + `aggregation_scan_limit: 5000` flags on the response.
6. Apply payload filters in Python (JSONField-portable across backends):
   - `task_name`: `icontains` on `detail.task_context.task_name` (matches sibling `_ops_celery_task_history`)
   - `failure_kind`: exact match on `detail.task_context.failure_kind`
7. Aggregate:
   - `by_task_name`: `dict[str, int]` counts per task
   - `by_failure_kind`: `dict[str, int]` counts per kind
   - `by_task_and_kind`: `dict[str, int]` counts per composite `"task/kind"` key
8. Sample events (up to `limit`):
   - Preserved discriminator: `task_name`, `failure_kind`, `model_label`, `row_id`, `acting_user_id`, `support_code`, `trace_id`, `created_at`
9. Empty-state note (Rigby F6 verbatim phrasing):
   > "No tenant_boundary_violation events in the last {window}. Either traffic isn't hitting decorated tasks, or enforcement is passing cleanly."

**Response shape:**
```
{
  "action": "tenant_boundary_violations",
  "window": "24h",
  "window_cutoff": "<iso>",
  "task_name_filter": "(all)" | "<filter>",
  "failure_kind_filter": "(all)" | "<filter>",
  "total_count": int,
  "by_task_name": dict,
  "by_failure_kind": dict,
  "by_task_and_kind": dict,
  "sample_events": [
    {"task_name", "failure_kind", "model_label", "row_id",
     "acting_user_id", "support_code", "trace_id", "created_at"},
    ...
  ],
  // Optional:
  "aggregation_scan_capped": true,     // if scan hit MAX_AGG_SCAN
  "aggregation_scan_limit": 5000,      // paired with above
  "note": "<diagnostic string>"        // if total_count == 0
}
```

### §2.3 Test suite — 10 tests, 189s runtime, 10/10 passing

`tests/security/test_ops_tool_tenant_boundary_violations.py` (new file):

- `test_empty_state_returns_note_and_zero_counts` — F6 diagnostic note
- `test_aggregates_by_task_name_failure_kind_and_composite` — F3 aggregation shape
- `test_sample_events_preserve_discriminator_fields` — F4 existence-oracle scope for operator surface
- `test_sample_events_ordered_most_recent_first` — descending time order
- `test_task_name_filter_matches_substring` — F2 `icontains`
- `test_failure_kind_filter_matches_exact` — F2 enum filter
- `test_invalid_failure_kind_returns_error` — typo guard
- `test_window_filter_excludes_old_events` — window cutoff
- `test_limit_defaults_to_20_and_caps_at_100` — default + upper clamp
- `test_limit_min_clamps_to_one` — defensive lower clamp

**Test approach:** handler-level unit tests via `_OpsProxy` mixin binding (calls `_ops_tenant_boundary_violations` directly against synthetic seeded `OpsRunEvent` rows). E2E dispatch through PA loop deferred — same rationale as Phase 2/3 test suites (worker-side signal handlers hang eager Celery dispatch).

---

## §3. Rigby SIGN Cycle

Two SIGN turns across S2758 authoring.

### §3.1 Design SIGN turn 1 (pre-code)

Rigby SIGN-PASS on F1–F6:

| Axis | Verdict |
|---|---|
| F1 tool-home decision (ops_tool over session_tool) | PASS |
| F2 action naming + params (window/task_name/failure_kind/limit) | PASS with F2 clarification: `task_name` uses `icontains` matching sibling `_ops_celery_task_history` |
| F3 aggregation output shape (by_task_name + by_failure_kind + by_task_and_kind + sample_events) | PASS |
| F4 existence-oracle scope (discriminator preserved: internal operator diagnostic) | PASS |
| F5 test scope (handler-level unit with synthetic seed; E2E deferred) | PASS |
| F6 empty-state note phrasing | PASS with verbatim shipped phrasing |

Q leans confirmed: QA ops_tool · QB `tenant_boundary_violations` action name · QC full discriminator exposure · QD handler-level tests only · QE no caching · QF include diagnostic note.

### §3.2 Implementation SIGN turn 1 (post-code)

Rigby SIGN-PASS on F1–F7 (F7 defensive scan cap added during implementation):

| Axis | Verdict |
|---|---|
| F1 shipped in ops_tool domain | PASS |
| F2 icontains + exact-enum params | PASS |
| F3 aggregation shape as designed | PASS |
| F4 discriminator preserved | PASS |
| F5 10 handler-level unit tests, 10/10 pass | PASS |
| F6 empty-state note verbatim | PASS |
| F7 (new) `MAX_AGG_SCAN=5000` cap + `aggregation_scan_capped` flag | PASS — "Good defensive guardrail. Having an explicit aggregation_scan_capped flag is the right way to avoid silent undercounting." |

**Known limitations ACKed:**

- L2 — Python-side filtering scans up to `MAX_AGG_SCAN=5000` rows before filtering. Postgres JSONB native operators would be a future optimization for very-high-cardinality scenarios.

**L1 originally listed but resolved at ship time:** Chris directive at S2758 close: "we are working locally so if it passes locally its working — no production right now" (per `project_single_user_pre_prod_operating_context.md` memory rule). Local PA worker recycled via `make celery-recycle`; live E2E dispatch verified — see §5 below.

Joint recommend-to-Chris (final): *"APPROVE + MERGE, local PA worker recycled and E2E verified via live Rigby dispatch."*

---

## §4. Chris D-Verdict

**Verdict:** **APPROVED** ("Approved" — S2758, 2026-07-11)

Two ratification points across S2758: original pre-code shape "approve" + post-code final ship "Approved". Zero unresolved menus routed per S2753 agree-first rule.

**Effect:** `ops_tool.tenant_boundary_violations` shipped. Live availability pending PA worker restart on deploy. First non-boundary-lockdown net-new engineering item since S2754 (per S2745 bias directive).

---

## §5. E2E Verification + First Real Finding

**Local Celery workers recycled via `make celery-recycle` at S2758 close.** Live E2E dispatch verified through Rigby PA loop with `ops_tool.tenant_boundary_violations, window=24h`:

- Tool executed successfully (7ms server-side)
- Response shape matches design contract (`action` / `window` / `window_cutoff` / `task_name_filter` / `failure_kind_filter` / `total_count` / `by_task_name` / `by_failure_kind` / `by_task_and_kind` / `sample_events`)
- Two real findings surfaced in the 24h window:

| Task | failure_kind | row_id | acting_user_id | Notes |
|---|---|---|---|---|
| `core.tasks.summarize_conversation_task` | `row_not_found` | `smoke-test-nonexistent-conv-id` | `null` | S2757 Path C smoke test at 18:15:09 |
| `core.tasks.process_pa_chat_task` | `missing_acting_identity` | `pa-5fe224e5757f42c0` | `null` | REAL production dispatch at 18:57:38 — Rigby's PA loop processing this S2758 test-drive request |

**§5.1 Finding — real dispatch-site gap surfaced.** The second event's `row_id=pa-5fe224e5757f42c0` matches Claude Code's current session pin. Rigby's own PA loop dispatched `process_pa_chat_task` for this conversation and hit `missing_acting_identity` — meaning the acting-user header was NOT attached at that dispatch path. This is a legitimate finding that Rigby's PA loop uses a dispatch path OUTSIDE the 4 sites converted in S2757 BATCH-FIX (`views_personal_assistant.py:467`+`:612`, `views/agents.py:155`, `services/td_handlers_core.py:2111`).

**Candidate for second BATCH-FIX pass follow-up:** locate the Rigby-side PA dispatch path (likely `core/services/unified_pa_entrypoint.py` or `views_assistant_bypass.py`) and convert it to `apply_async_with_actor` per the same pattern as S2757 sites. Not blocking S2758 close; the tool doing its job by surfacing this is the ratifiable outcome.

**First real query for Chris:**
```
bash tools/pa_local.sh "Show me tenant_boundary_violations in the last 24h"
```
Rigby invokes `ops_tool.tenant_boundary_violations` action with `window='24h'`.

---

## §6. Provenance Chain

- **Predecessor ratifications:**
  - `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md` (substrate that emits the events this tool surfaces)
  - `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md` (dispatch conversion that attaches the acting-user header the tool reads)
- **Sibling ops_tool actions (adjacency reference):**
  - `_ops_failure_signatures` — top error signatures by frequency
  - `_ops_celery_task_history` — recent task runs (SUCCESS + FAILURE)
  - `_ops_execution_search` — recent AgentExecutions by name/status
- **Engineering Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` — §7.4.x (close-ceremony discipline; 1-PR bundle for net-new tooling), §7.6.1 (SIGN watchpoint-attestation, applied twice this session)
