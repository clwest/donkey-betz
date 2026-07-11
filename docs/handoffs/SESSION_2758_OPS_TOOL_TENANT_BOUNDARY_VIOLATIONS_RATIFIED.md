# Session 2758 — `ops_tool.tenant_boundary_violations` PA Tool Ratified

**Date:** 2026-07-11
**Predecessor:** S2757 (I-0303 Phase 3 BATCH-FIX first pass ratified; pin `pa-bb7f7567c6e34951` retired)
**Successor:** S2759 (multiple candidates — Rigby-side dispatch-path conversion (real S2758 finding), D2 canonical decision routing, D4 HIGH-RISK task file wiring extension, or net-new engineering)
**Session pin:** `pa-5fe224e5757f42c0` (label `s2758-recent-tenant-violations-tool`; **retired at S2758 close** per protocol)
**HEAD at open:** `168b663ad` (post-S2757 BATCH-FIX merge)
**HEAD at close:** (filled at merge)

---

## §1 Delivery Ledger

Single 1-PR close-ceremony bundle per PLAYBOOK-7.4.1. First non-boundary-lockdown net-new engineering item since S2754 (per Chris S2745 engineering-bias directive).

| # | PR | Merge SHA | Content |
|---|---|---|---|
| 1 | (this PR) | pending | `ops_tool.tenant_boundary_violations` schema + handler + 10 tests + ratification envelope + handoff + docs cascade + pin retire commentary |

---

## §2 Ratified Deliverables

### §2.1 Schema (`core/services/pa_tool_schemas.py`)

- `tenant_boundary_violations` added to `ops_tool` action enum (23rd action)
- Action description added (positioned after `zombie_thread_rate`)
- New parameter `failure_kind` with 6-kind Phase 2 enum
- Extended `task_name` description to mention new tool

### §2.2 Handler (`core/services/td_handlers_ops.py`)

- New `elif action == 'tenant_boundary_violations'` branch (after `zombie_thread_rate`)
- New `_ops_tenant_boundary_violations(payload, trace_id)` method (~130 lines) placed adjacent to `_ops_celery_task_history`
- Query: `OpsRunEvent.filter(label='tenant_boundary_violation', created_at__gte=cutoff)`
- Defensive `MAX_AGG_SCAN=5000` cap with `aggregation_scan_capped` flag (Rigby F7)
- Aggregates: `by_task_name` / `by_failure_kind` / `by_task_and_kind` composite
- Sample events preserve discriminator: `task_name` / `failure_kind` / `model_label` / `row_id` / `acting_user_id` / `support_code` / `trace_id` / `created_at`
- Empty-state diagnostic note (Rigby F6 verbatim)
- Invalid `failure_kind` returns error with allowed list
- `task_name` uses `icontains` (matches sibling `_ops_celery_task_history`)

### §2.3 Test suite — 10 tests, 10/10 passing (189s runtime)

`tests/security/test_ops_tool_tenant_boundary_violations.py` (new). Handler-level unit tests via `_OpsProxy` mixin binding + synthetic `OpsRunEvent` seed rows. Covers empty state, aggregation shape, discriminator preservation, ordering, filters (task_name icontains + failure_kind exact), invalid failure_kind guard, window cutoff, limit default/cap/min-clamp.

### §2.4 E2E verification (post-recycle)

Ran `make celery-recycle` at S2758 close per Chris directive ("we are working locally so if it passes locally its working"). Live E2E dispatch through Rigby PA loop:

- Tool executed successfully (7ms server-side)
- Response shape matches design contract
- **Two real findings surfaced:**
  1. `summarize_conversation_task` / `row_not_found` / `smoke-test-nonexistent-conv-id` — S2757 Path C smoke test at 18:15:09
  2. `process_pa_chat_task` / `missing_acting_identity` / `pa-5fe224e5757f42c0` — REAL production dispatch at 18:57:38 (Rigby's own PA loop processing my test-drive request)

**Finding #2 is a legitimate discovery:** the `row_id` matches the S2758 session pin, meaning Rigby's PA loop dispatched `process_pa_chat_task` without attaching the acting-user header. The dispatch path is outside the 4 S2757-converted sites — likely `core/services/unified_pa_entrypoint.py` or `views_assistant_bypass.py`. **This is exactly what the tool is supposed to surface** — candidate for second BATCH-FIX pass follow-up.

### §2.5 Ratification envelope

`docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md` — frozen record with two Rigby SIGN turn logs + Chris D-verdict + E2E verification detail + real-finding discovery documentation.

---

## §3 Rigby SIGN Cycle — two turns, all PASS

### §3.1 Design SIGN turn 1 (pre-code)

F1–F6 all PASS with one F2 clarification (`task_name` uses `icontains` matching sibling `_ops_celery_task_history`). Q leans confirmed on 6 axes (QA/QB/QC/QD/QE/QF).

### §3.2 Implementation SIGN turn 1 (post-code)

F1–F7 all PASS (F7 = defensive `MAX_AGG_SCAN=5000` cap added during implementation). L2 (Python-side filtering scans up to cap) ACKed.

**L1 originally listed but resolved at ship time:** Chris directive at S2758 close overrode: "we are working locally so if it passes locally its working — no production right now". Local worker recycled + E2E verified.

---

## §4 Chris D-Verdict — two ratification points

1. **Original pre-code shape** — "approve" (open implementation authorized)
2. **Final ship** — "Approved" (close-ceremony bundle authorized)

Zero unresolved menus routed per S2753 agree-first rule.

**Chris directive at close (memory rule update):** "we are working locally so if it passes locally its working — no production right now". Reinforces `project_single_user_pre_prod_operating_context.md`: default single-tenant local-truth assumptions; production-observation-window framing was wrong for S2758 close.

---

## §5 Workflow Rules Exercised

### §5.1 Claude+Rigby agree-first (S2753 directive)

Two Rigby SIGN turns + two Chris D-verdict points. Zero unresolved menus presented to Chris.

### §5.2 Bias engineering / net-new builds (S2745 close directive)

S2758 shipped a NET-NEW PA tool — first non-boundary-lockdown net-new engineering item since S2754. Chris selected #2 from a 6-candidate menu proposed at S2758 open.

### §5.3 Verify-before-build (Cycle 1A rule)

Before drafting, investigated existing `session_tool` vs `ops_tool` pattern. Discovered `ops_tool` was the semantically correct home (already houses `failure_signatures` + `celery_task_history` + `execution_search` — same diagnostic-read shape). Chris's shorthand `session_tool.recent_tenant_violations` was refined to `ops_tool.tenant_boundary_violations` via Rigby F1 SIGN.

### §5.4 Twin-canonical-representations (S2754a rule)

S2758 ratification lands TWO deliverables in RUR-C1 workspace (tool serves I-0303 substrate):

- Governance-truth: `RATIFICATION_20260711_ops_tool_tenant_boundary_violations`
- Engineering-truth: `ops_tool.tenant_boundary_violations PA Tool (mirror)`

Created via ORM-direct.

### §5.5 Docs cascade at every close (S1399 rule)

Full 4-step cascade at close: `build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `embed_documents --all-unembedded` + `build_docs_provenance`. Chunk count evidence in PR body.

### §5.6 PLAYBOOK-7.4.1 close-ceremony 1-PR bundle

All artifacts land in ONE PR — schema + handler + tests + envelope + handoff + docs cascade + pin retire.

### §5.7 PLAYBOOK-7.6.1 SIGN watchpoint-attestation

Two SIGN turns (pre-code + post-code). Both PASS.

### §5.8 Local-truth rule (Chris S2758 directive)

New memory rule established: local pass = shipped. No production observation windows. Applies to all future close-ceremonies until prod comes online. Envelope §3 + §5 corrected to remove production-Railway-deploy framing.

### §5.9 `gh pr merge --admin` (feedback rule)

Merged with `--admin` posture — GitHub Actions billing still blocked. Rationale in PR body.

---

## §6 Session Timing + Cost

- Session open: 2026-07-11 (continued conversation post-S2757 close)
- First Rigby dispatch: after fresh pin mint (`pa-5fe224e5757f42c0`)
- Rigby SIGN turns: 2 (pre-code + post-code) — all PASS
- Chris D-verdicts: 2 (original shape / final ship)
- Test suite: 1 run during authoring (189s combined 10/10)
- E2E verification: `make celery-recycle` + live Rigby dispatch (7ms server-side, 2 real findings surfaced)
- Total local runtime: ~1.5 hours (very efficient — single-turn SIGN convergence + net-new-tool scope)

---

## §7 S2759 Priorities (Informative)

Chris selects at S2759 open:

1. **Rigby-side dispatch-path conversion** — the S2758 tool immediately surfaced a real finding (Rigby's own PA loop dispatches `process_pa_chat_task` without the acting-user header, missing the S2757 BATCH-FIX conversion). Route to Rigby: find the exact dispatch site (likely `core/services/unified_pa_entrypoint.py` or `views_assistant_bypass.py`) + convert to `apply_async_with_actor`. Small PR; fast turnaround.
2. **D2 canonical AgentExecution vs AgentTaskExecution decision** — three approaches, needs Chris directive
3. **D4 HIGH-RISK task file wiring extension** — REPORT-ONLY-shape PR for tasks_initiatives/content/media/misc
4. **Net-new engineering item** — new spider / UI page / capability
5. Housekeeping: P0.5 freeze-mode routing + P0.75 CI billing

---

## §8 Provenance Chain

- **Predecessor session:** `docs/handoffs/SESSION_2757_I0303_PHASE3_BATCH_FIX_RATIFIED.md`
- **Serves I-0303 substrate:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md` (emits `tenant_boundary_violation` OpsRunEvents this tool surfaces)
- **Serves I-0303 dispatch conversion:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md` (attaches acting-user header this tool reads)
- **Sibling ops_tool actions (adjacency reference):** `_ops_failure_signatures` + `_ops_celery_task_history` + `_ops_execution_search`
- **Engineering Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` — §7.4.x (close-ceremony discipline) + §7.6.1 (SIGN watchpoint, applied twice this session)
- **Ratification envelope (this session):** `docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md`
