# Session 1210 — URC v0.1 Phase B: `receipt_only` mode for CodeReviewAgent

**Status:** PR #2476 merged. AC-1, AC-2, AC-3, AC-4 all verified live. First agent-level `receipt_only` integration shipped — sets pattern for ~10 other context-dependent agents on the URC follow-on list.
**Date:** 2026-06-23
**Active conversation:** `pa-61c7b47d201d4591` — continued from Session 1209 open. Pinned in `tools/pa_local.sh`.
**Prior session:** [`SESSION_1209_URC_V01_ENVELOPE_AND_ROUTER_PATH.md`](./SESSION_1209_URC_V01_ENVELOPE_AND_ROUTER_PATH.md).
**Next session entry point:** Session 1211 — see §"Open follow-ups". 24h watches firing this session: Session 1208 Outbound (already fired ~04:45 UTC), Session 1209 URC (fires ~13:10 UTC 2026-06-24), Session 1210 Phase B (arms ~14:48 UTC 2026-06-24).

## TL;DR

Shipped **URC v0.1 Phase B** — agent-level `receipt_only` capability ping for `CodeReviewAgent`. When a caller passes `context['mode'] == 'receipt_only'` (or the forward-compat `context['receipt_only'] is True` signal), the agent short-circuits before `time_travel_session` opens and emits a minimal v0 receipt: `data={skipped: True, status: 'skipped', mode: 'receipt_only', message: ...}`. The Q1 predicate at `core/services/urc_envelope.py:50` reads `data['skipped'] is True` and the URC writeback writes `run_status='skipped'` instead of `'error'`.

**One PR (#2476), 1 implementation commit, AC verified live with 2-dispatch validation smoke from Rigby:**

- **PR #2476** (Phase B receipt_only branch + 14 unit tests): `core/agents/code_review_agent.py` adds `_is_receipt_only_mode(context)` static helper + early-return branch at the top of `execute()`. `core/tests/test_code_review_agent_receipt_only.py` covers detector (×7), execute behavior (×5), and URC integration (×2).

**Drift surfaced + resolved without changing URC core:** The Session 1209 spec text in `00-START-NEXT-SESSION.md:127` implied `data={'status': 'skipped'}` alone would trigger `run_status='skipped'`. The Q1 predicate actually checks `data['skipped'] is True`. Phase B's receipt emits **both** keys (Option A reconciliation, Rigby sign-off) — `skipped` lights up the predicate; `status` satisfies the v0 receipt schema. AC-4 addendum on deliverable `6f09233c-…` (+2601 chars) tightens the narrative so future adopters don't repeat the mismatch.

## Session Manifest

### PR merged

| # | Title | Commits (squashed) | Files | Verified |
|---|---|---|---|---|
| **#2476** | feat(session-1210-urc): Phase B — receipt_only mode for CodeReviewAgent | `538b97b1` | `core/agents/code_review_agent.py` (+44), `core/tests/test_code_review_agent_receipt_only.py` (+217 new), `docs/INDEX.md` (auto-regen) | ✅ 14 unit tests green pre-PR; ✅ live ×2 post-merge — receipt_only run `d0281cc8-477b-4099-aa21-10ad5439abfc` → `run_status='skipped'` with `data.skipped=True`, no tool_calls, no warnings; control run `042a8c0e-3b08-4a42-aea4-d997bde72253` → `run_status='success'` with 303 lines of python reviewed (normal path untouched). Squash-merged as `4d0040af`. |

### Deliverables filed / touched

| ID | Action | Note |
|---|---|---|
| `6f09233c-c984-4303-87c4-e67b94390030` | **APPENDED (+2601 chars)** | Rigby filed AC-4 addendum to the URC v0.1 spec deliverable. Captures (a) Phase B definition (first agent-level integration), (b) classification rule (`data['skipped'] is True` is the load-bearing Q1 marker), (c) schema nuance (`status='skipped'` is receipt-schema-valid but not sufficient), (d) reference impl `core/agents/code_review_agent.py:286-316`, (e) AC-2/AC-3 evidence row IDs. |

Initiative `29154d73-…` (Platform Capability Audit) holds the spec + smoke evidence + Phase B addendum on the same `kind=investigation` thread.

## Behavioral invariants — what's now true post-merge

1. **`CodeReviewAgent` recognizes two `receipt_only` signals on its `context` arg.** `context.get('mode') == 'receipt_only'` is the primary spec signal; `context.get('receipt_only') is True` is the secondary forward-compat signal. Either fires the early-return branch. `is True` is intentional — truthy strings/ints do NOT trigger (covered by `test_receipt_only_truthy_but_not_true_does_not_trigger`).
2. **`receipt_only` short-circuits before any LLM/repo/telemetry side effects.** `_call_openai`, `_build_intelligent_prompt`, `_execute_tool_call`, `_save_to_deliverable`, `_record_learning_outcome` are all skipped; `time_travel_session` never opens. The early return executes in ≤4 seconds end-to-end (3616ms in the validation smoke, dominated by celery dispatch + writeback overhead, not the agent body).
3. **Receipt data shape is fixed.** `{skipped: True, status: 'skipped', mode: 'receipt_only', message: 'receipt_only mode — no code inspection performed'}`. The `AgentResult` carries `success=True`, `message='receipt_only mode — no code inspection performed'`, `tool_calls=[]`, `decisions_made=0`.
4. **URC writeback classifies as `run_status='skipped'`.** Both `tasks_agents.execute_agent_task` (PR #2473) and `agent_router._complete_execution` (PR #2474) writeback paths reach `compute_run_status` with this shape and the `_is_skipped` Q1 predicate fires before the timeout/error/contract_violation branches. No `RECEIPT_CONTRACT_VIOLATION` warning is emitted.
5. **Normal-mode behavior is byte-identical to pre-Phase-B.** The early-return branch is a pure insertion above the existing flow — no edits below the `if self._is_receipt_only_mode(context):` block. The control run smoke confirmed this: empty context dispatch produced a comprehensive code review (303 lines of python analyzed) and the writeback wrote `run_status='success'`.

## Rollback levers

- **Disable the branch in-place:** edit `core/agents/code_review_agent.py:295` to `if False and self._is_receipt_only_mode(context):` and restart workers. Rolls the agent back to pre-Phase-B behavior. Receipt-only callers will revert to `run_status='error'` ("No code inspection or review completed").
- **Per-call override:** callers can omit the `mode` key (or pass `mode='normal'`) on a specific dispatch to force the inspection path. No env flag needed.
- **Full revert:** `git revert 4d0040af` (the squash merge commit). Branch deleted; no dependent PRs.
- **PR-level revert without losing helper:** if only the early-return is problematic but `_is_receipt_only_mode` is fine, delete lines 295-316 (the `if` block in `execute()`) and keep the helper. The helper has no callers besides `execute()`, so this is safe.

## 24h watch checklist — arms ~14:48 UTC 2026-06-24

Run the following ~24h after merge (2026-06-24 ~14:48 UTC; PR merged 14:48 UTC 2026-06-23):

```bash
# 1) Confirm AgentExecution rows for CodeReviewAgent with receipt_only mode
#    classify as run_status='skipped' across the 24h window
tools/pa_local.sh "Run execution_history_tool action=by_agent agent_name=CodeReviewAgent limit=30. Tally:
  - rows where output_data.run_status='skipped' AND input_data.context.mode='receipt_only' — should be > 0
  - rows where output_data.run_status='skipped' AND no receipt_only signal in input_data.context — expected 0 (no false positives)
  - rows where output_data.run_status='error' AND input_data.context.mode='receipt_only' — expected 0 (Phase B should have closed this)"

# 2) Spot-check normal-mode behavior hasn't regressed
#    Pick 3 normal-mode rows from the same window and verify they have
#    non-empty output_data.data + output_data.tool_calls (proof the
#    inspection path executed)

# 3) No spurious contract_violation warnings on receipt_only rows
#    AC: output_data.warnings should be [] on receipt_only rows
#    (NOT contain a RECEIPT_CONTRACT_VIOLATION entry)
```

**Invariants:**
- **A1:** Every CodeReviewAgent receipt_only dispatch → `run_status='skipped'`. No more `run_status='error'` for capability pings.
- **A2:** Zero spurious `run_status='skipped'` rows from non-receipt_only callers (the helper is strict).
- **A3:** Normal-mode rows still produce `output_data.data.results` + `output_data.tool_calls` (inspection path executed).
- **A4:** `warnings` list stays `[]` on receipt_only rows (NOT a `RECEIPT_CONTRACT_VIOLATION` entry — that would mean the receipt schema check failed).

If A1 misses, the helper isn't catching the signal — grep `input_data.context` for the actual shape. If A2 fires, the helper is overmatching — likely a new caller is passing `receipt_only` truthy unintentionally. If A3 fails, the early-return is leaking into normal-mode (regression). If A4 fires, the receipt schema check at `_receipt_violation_reason` rejected the shape — likely a key drift in the receipt dict.

## Open follow-ups

| Item | Priority | Where it's defined |
|---|---|---|
| **Other context-dependent agents adopt the Phase B pattern** | **P1** | Session 1209 fleet smoke (deliverable `1a8cde69-…`) surfaced ~10 agents that fail under `receipt_only` mode. Phase B sets the pattern: `_is_receipt_only_mode` static helper + early-return before `time_travel_session`. Reference: `core/agents/code_review_agent.py:286-316`. Candidate agents include the other Session 1209 fleet-smoke "error" rows. |
| **Standardize "skipped" semantics across agents** | **P2 (Rigby Session 1210 add)** | Decide whether future receipt_only agents must emit BOTH `data.skipped=True` AND `data.status='skipped'` (the Phase B Option A pattern), or whether URC should expand its Q1 predicate to also accept `data.status == 'skipped'`. Current pattern is safe; defer until ≥3 agents have adopted to see whether the dual-key requirement is friction. |
| **Other writeback callsites adopt URC** | **P2 (Session 1209 carryover)** | ~10 sites: `core/agent_execution_wrapper.py:93`, `ai_core/agents/sync_executor.py:109`, `core/services/content_executor.py:255`, `core/services/executor_registry.py:394`, `core/services/agent_collaboration.py:339`, `core/team_workflow_engine.py:494,517`, `core/services/collective_intelligence.py:1425`, `core/tasks_media.py:192`, `core/tasks_agents.py:706,2278`. Use `core.services.urc_envelope.enrich_output_data()`. |
| **Expose `parent_execution_id` filter in `ops_tool execution_search`** | **P2 (Session 1209 carryover)** | Rigby's fleet-smoke aggregation hit a tool gap — can't query "all AgentExecutions spawned by parent X". Session 1098 PR #4 added the field; just need to surface in the tool. ~30min PR. |
| **Promote `attempts_used` to canonical top-level on router-path writeback** | **P1 (Session 1208 carryover)** | PR #2469 + PR #2471 lifted it for `execute_agent_task`. The router-path canonical-shape writeback at `agent_router.py:1611` doesn't lift it. Small mirror — same convention. |
| **Smoke context minimization convention** | **P3 (Session 1209 — Rigby Phase 3 idea)** | Define a minimal "smoke context" convention (`context.mode` only + tiny `context.smoke_id`) for future fleet smokes. Avoids inflating execution records with multi-KB spec bodies under `context.research`. |
| **Session 1209 URC 24h watch** | **P1 (time-gated, fires ~13:10 UTC 2026-06-24)** | Checklist in [`SESSION_1209`](./SESSION_1209_URC_V01_ENVELOPE_AND_ROUTER_PATH.md) §"24h watch checklist". Invariants: URC envelope coverage 100% on new rows; run_status distribution sane; **zero spurious contract_violations on non-receipt_only callers**; warnings list shape consistent. |
| **Session 1208 Outbound-pack 24h watch (already fired ~04:45 UTC)** | **P1 (time-gated, verify result)** | Checklist in [`SESSION_1208`](./SESSION_1208_CAMPAIGN_ORCHESTRATOR_OUTBOUND_PACK_HARDENING.md) §"24h watch checklist". Run verification on next session open. |
| **Session 1210 Phase B 24h watch** | **P1 (time-gated, arms ~14:48 UTC 2026-06-24)** | §"24h watch checklist" above. Invariants A1-A4. |
| Carryover from Session 1209 priority table (Layer 1/2/4 dashboard refresh, lint rule for `\.execute\(`, Wakeup Week scoreboard, etc.) | — | Unchanged; pull from `00-START-NEXT-SESSION.md:351-389` table. |

## Active conversation

`pa-61c7b47d201d4591` — Rigby's `session_tool create_fresh` at Session 1209 open. Carried URC v0.1 Q1-Q5 design lock through Phase A+C (Session 1209) and Phase B (Session 1210). Pinned in `tools/pa_local.sh`. Lean for Session 1211: spin a fresh thread if Session 1211 takes a different lane; continue on this one if the work extends URC adoption to other agents. Prior threads retired: `pa-2d74e36cc3a04787` (Session 1208 + URC design discussion + Fleet Smoke Report `c5ccf3b1-…` as design-anchor record), `pa-33088358df304016` (Session 1207 MIC + spec handoff), `pa-b2a99ff5b0ee47a6` (Rigby's auto-spawned Session 1207 — superseded mid-session), `pa-234a75abfe374695` (Session 1206 Layer 1 Telemetry), `pa-76aa5b61d0764d11` (Session 1205 evidence-card pipeline), `pa-1871b37227054254` (Session 1204 Phase B.2), `pa-d2d0f4c2b6284899` (Session 1203 Phase B.1), `pa-123b7d48f01043eb` (Session 1202 Phase A.2).

## Drift findings surfaced this session

| Finding | Status | Reconciliation |
|---|---|---|
| Spec text in `00-START-NEXT-SESSION.md:127` implies `data={'status': 'skipped'}` alone triggers `run_status='skipped'`, but Q1 predicate at `urc_envelope.py:50` requires `data['skipped'] is True` | ✅ **closed in-session** | Option A — agent emits both keys (`skipped: True` + `status: 'skipped'`); AC-4 addendum (+2601 chars on deliverable `6f09233c-…`) tightens the narrative for future adopters. URC core unchanged. Per `feedback_corpus_walks_surface_mechanism_drift.md` — surfaced to Rigby before quietly bridging. |

## Notes / gotchas

- **Worker restart was required post-merge** because `code_review_agent.py` is imported by `core.tasks_agents._impl_execute_agent_task`. Done at 09:47 MDT post-merge (all 4 workers + beat alive on fresh PIDs). Per `feedback_new_shared_task_needs_worker_restart.md`.
- **The early-return branch is intentionally placed BEFORE `time_travel_session.__enter__`** to keep the receipt path side-effect-free. The TimeTravelSession would otherwise open a debug session, write a decision tree row, and emit telemetry — overhead the minimal v0 receipt explicitly avoids.
- **Receipt-only is not a contract_violation under any predicate.** The schema check at `_receipt_violation_reason` validates `status ∈ {'ok', 'skipped', 'error'}` — `'skipped'` is allowed. The dual-key emit pattern lights up Q1 (skipped) before the schema check is even reached in `compute_run_status`'s precedence chain.
- **AC-3 result was slightly better than baseline:** the control run executed a comprehensive code review on python source (303 lines analyzed). Pre-Phase-B baseline was `run_status='error'` on the fleet-smoke rows because they had specific contrived contexts; the empty-context control here exercises the legitimate normal path.
