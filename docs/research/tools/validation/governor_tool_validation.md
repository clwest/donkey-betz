# `governor_tool` — Validation Report (S2893)

**Tool:** `governor_tool`
**Schema:** `core/services/pa_tool_schemas.py:3144`
**Handler:** `core/services/td_handlers_ops.py:2341` (`_handle_governor`)
**Register site:** `core/services/tool_dispatcher.py:535`
**Session:** S2893 (Path B systematic sweep — Slice 1 batch 2 of `td_handlers_ops`)
**HEAD at validation:** `387ac953e`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (every action in the schema `action` enum exercised live except `reset_breaker`, which was correctly not-exercised per canary rule; see §6.2).
**Rigby SIGN:** S2893 T1 SIGN AGREE-clean (6/6, 0 F-BLOCKING) with 4 zoom-out concerns — 2 mitigated same-PR, 2 forward-carry.

---

## 1. Purpose / when-to-use

Beat Task Governor readout + control. Answers "which agents will run right now, which are blocked, which are misaligned, what would happen if X ran?" Use when asked about autonomous dispatch permissions, mission alignment, tripped circuit breakers, or per-agent throttle state.

Distinct from `agent_control_tool` (per-agent manual block/unblock rows) — governor reflects mission-alignment + failure-rate circuit-breaker state, not operator overrides.

## Covered actions

- `status` — **in scope this ship** — verified live (see §6.1). Returns `governor_enabled`, `demo_mode`, active priorities, disabled missions, tripped circuit breakers, telemetry, config. **Consistency caveat:** observed a status-vs-coverage drift where first call returned `circuit_breakers_tripped=[]` while `.coverage` reported 3 blocked agents; re-check within the same session returned the full breaker list. See §6.1 finding + Ledger candidate #1.
- `coverage` — **in scope this ship** — verified live. Returns per-agent proceed/reason/detail across all 83 AGENT_MAP entries. Semantic note: `reason="aligned"` is emitted even when `detail="matched via fail_open: None"` — i.e. the outcome is fail-open, not mission-matched. See §6.1 + Ledger candidate #3.
- `test` — **in scope this ship** — verified live with `agent_name='ResearchAgent'`, `trigger_source='schedule'`. Same fail-open labeling concern applies to per-agent results.
- `reset_breaker` — **NOT exercised this ship — CANARY-EXCLUDED** — per S2893 pre-dispatch SIGN, we do not trip a breaker artificially to exercise reset. Would-reset-if-tripped verified as an available code path via schema + handler read only. See §6.2.

## 3. Schema notes

- **Required:** `action` (enum: `status, test, reset_breaker, coverage`).
- **Conditional required:** `agent_name` required at handler level for `test` + `reset_breaker`; schema declares `agent_name` as optional string. Not a defect in isolation — matches usage — but does mirror the S2892 Ledger candidate #1 pattern on `agent_memory_tool`. Marginal Ledger entry candidate; consider aligning the schema to declare `agent_name` conditionally required.
- **Optional:** `trigger_source` (default `'schedule'`), `task` (keyword-match hint for `test`).
- **Schema description lint:** clean — enumerates all four actions and their arg requirements.

## 4. Golden-path examples

**Governor pulse ("is dispatch open?"):**

```
governor_tool  action=status
```

**Full alignment sweep (all agents, one call):**

```
governor_tool  action=coverage
```

**Would-this-agent-run check:**

```
governor_tool  action=test  agent_name=ResearchAgent  trigger_source=schedule
```

**Clear a tripped breaker (mutating; verify tripped-state first):**

```
governor_tool  action=status
# if agent_name is in circuit_breakers_tripped:
governor_tool  action=reset_breaker  agent_name=<name>
governor_tool  action=status   # confirm cleared
```

## 5. Failure / empty-state / pagination notes

- **No pagination** — `.coverage` returns the full agent list in one call (83 rows at HEAD `387ac953e`); response is ~15KB.
- **`.status` intermittent staleness observed** — see §6.1 finding (a). Downstream callers should not assume `.status.circuit_breakers_tripped` and `.coverage[*].reason='circuit_breaker'` agree in a single request; re-query `.status` if consistency is required.
- **`reset_breaker` is silent** on non-tripped agent names — handler returns success even if the named agent was not tripped. Not confirmed as defect in this ship; noted as follow-up.
- **No latency outliers** — all read actions <250ms observed.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

- **Mutating actions:** `reset_breaker` only.
- **Containment protocol applied this ship:** `reset_breaker` was **not invoked** (canary-excluded); no state modification occurred. When invoked in production, callers should pair with a pre-check `.status` read and a post-check `.status` re-read to verify the breaker cleared. Reset is not automatically re-tripped on subsequent failures until the failure window rolls forward.

## 6. Evidence

### 6.1 Observed runs — this ship

Rigby's live dispatches at S2893 T1 (2026-07-22, HEAD `387ac953e`, pin `pa-7a595cac8cc04bf8`):

**`status` (50ms) — first call:**

```json
{"action": "status", "governor_enabled": true, "demo_mode": false,
 "active_priorities": 0, "priority_names": [], "disabled_missions": [],
 "circuit_breakers_tripped": [],
 "telemetry": {"date": "2026-07-22", "missions": []},
 "config": {"cb_window_size": 20, "cb_failure_threshold": 0.4,
            "cb_cooldown_seconds": 3600}}
```

**`status` (37ms) — re-check within same session:**

```json
{"action": "status", "governor_enabled": true, "demo_mode": false,
 "circuit_breakers_tripped": ["AudioAgent", "CodeReviewAgent", "WorkflowAgent"],
 "telemetry": {"date": "2026-07-22", "missions": []},
 "config": {"cb_window_size": 20, "cb_failure_threshold": 0.4,
            "cb_cooldown_seconds": 3600}}
```

**Finding (a) — status inconsistency:** The two `.status` calls returned different `circuit_breakers_tripped` arrays within the same session (no state-change actions between them). The second call agrees with `.coverage`. **Read:** eventual-consistency / cache / partial-refresh artifact in the status handler's breaker read. Ledger candidate #1 for S2893.

**`coverage` (231ms):**

```json
{"action": "coverage", "total": 83, "aligned": 80, "misaligned": 3,
 "coverage_pct": "96%",
 "agents": [
   {"agent": "AudioAgent", "proceed": false, "reason": "circuit_breaker",
    "detail": "circuit breaker tripped: 45% failure rate over last 20 executions (threshold: 40%)"},
   {"agent": "CodeReviewAgent", "proceed": false, "reason": "circuit_breaker",
    "detail": "circuit breaker tripped: 75% failure rate over last 20 executions (threshold: 40%)"},
   // ...80 more agents with reason="aligned", detail="matched via fail_open: None"
 ]}
```

**Finding (b) — "aligned" is a fail-open label, not a mission-match assertion:** All 80 non-blocked agents show `reason="aligned"` with `detail="matched via fail_open: None"`. There is no per-agent distinction between "aligned by explicit mission match" and "allowed by fail-open default." Ledger candidate #3 — surface the distinction so operators can see whether coverage is genuinely mission-governed vs merely permissive.

**`test` (7ms):**

```json
{"action": "test", "agent_name": "ResearchAgent", "trigger_source": "schedule",
 "proceed": true, "reason": "aligned",
 "detail": "matched via fail_open: None"}
```

Same fail-open semantics apply to single-agent `test` outcomes.

### 6.2 Runtime-not-executed — this ship

- **`reset_breaker`** — canary-excluded per SIGN. Would-reset-if-tripped verified via schema + handler read only. Live exercise deferred to next session where a breaker is naturally tripped (three currently visible in `.status` re-check but they are legitimate live-system state — resetting them without operator intent is out of scope for a validation sweep).
- **`test` under a tripped breaker** — not exercised. Would confirm `.test` returns `proceed=false, reason="circuit_breaker"` for one of the 3 currently tripped agents; deferred.
- **`test` under demo_mode=true** — not exercised (demo_mode was false throughout).

---

## Related

- **Ledger candidates surfaced this ship** (routed to Ledger at close):
  1. `.status` intermittent inconsistency with `.coverage` on `circuit_breakers_tripped` field.
  2. `.reset_breaker` handler tolerates non-tripped `agent_name` silently — confirm intended behavior.
  3. `reason="aligned"` conflates mission-match vs fail-open — surface distinction in output.
  4. Schema `agent_name` declared optional but conditionally required for `test`/`reset_breaker` (mirrors S2892 Ledger #1 pattern on `agent_memory_tool`).
- **S2893 handoff:** `docs/handoffs/SESSION_2893_PA_TOOLS_SWEEP_SLICE_1_BATCH_2.md`.
- **Related tools:** `agent_control_tool` (per-agent operator blocks — orthogonal to circuit-breaker state), `autopilot_tool` (broader ops policy engine — deferred to Slice 1.5).
