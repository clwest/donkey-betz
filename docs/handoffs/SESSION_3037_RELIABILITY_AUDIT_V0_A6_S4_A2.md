# Session 3037 — Reliability Audit v0 self-execution + A6 + S4 + A2 shipped

**Closed:** 2026-07-29
**HEAD at close:** filled at cascade merge (post-`ced5b7ea0`)
**Session shape:** Long-form arc — first execution of the A1 Reliability Audit wedge (~85 sessions after ratification) against Donkey Betz itself; audit surfaced 15 findings + 10-item remediation backlog; 3 of those items shipped this session (A6 + S4 + A2) plus 2 in-audit quick wins (A1 orphan recovery + S5 S3036 escalation reopen).

---

## What shipped

### The audit (5 workspace deliverables)

| Step | Deliverable | Type |
|---|---|---|
| 1 Scope Card | `aec0e6da-b2b4-4d28-8cca-b69da920b1f4` | initiative_phase_doc |
| 2 Telemetry Pull & Failure Signature Sweep | `361e8209-c24c-4401-8a3d-f5387f972dea` | audit_report |
| 3 Tool Reliability Matrix | `ce9ca37b-c544-4672-be9f-5b29e14aa59d` | audit_report |
| 4 Governance Posture | `1ac5f0dc-aa09-44da-8353-dea3e3cbdc2e` | audit_report |
| 5 Scenario Drills | *(skipped — Snapshot tier scope; findings characterized in Steps 2-4)* | — |
| 6 Remediation Backlog (10 items) | `c3cad098-6d29-447f-b949-456913f7d343` | audit_report |

All in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`, diagnostic flags cleared per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`.

### Two shipped PRs

**PR #3767 (`690ba8c6a`) — `fix(s3037-a6): AGENT_MAP fallback fail-loud in workflow orchestrator`.** 2 files, +205/-6. NEW test class `AgentMapFallbackFailLoudTests` (6 tests). Mirrors the S1234 D1 lane_4 pattern for the `AGENT_MAP` fallback path — surfaces actual Python exception + agent_name + duration_ms on falsy `router.route` success instead of the generic "Unknown error" fallback. Discharges the audit's Step 3 finding that the deterministic `error_signature: 1cfc0fcf97dd26ce` on 7 of 12 morning_brief failures was hiding a real bug.

**PR #3768 (`ced5b7ea0`) — `feat(s3037-s4): cleanup_stale_ops_runs Celery beat task`.** 4 files, +309/-0. NEW test file `test_cleanup_stale_ops_runs.py` (8 tests). Mirrors `_impl_cleanup_stale_agent_executions` pattern for `OpsRun` model. Beat-scheduled every 10 min on the `broadcast` queue with 60-min threshold. Discharges the "no lost dispatches" reliability rule violation surfaced by the audit (2 rows found stuck 383h + 434h at audit time).

### Three in-session ORM fixes (audit-driven)

- **A1 quick-win** — 2 orphaned OpsRun rows recovered manually via ORM: `132673de-…` (morning_brief 2026-07-13, 383h stuck) and `9ad50ab1-…` (rur_safety_contract_failures, 434h stuck) both flipped `running → failed` with `OpsRunEvent(event_type='cleanup', label='manual_recovery_s3037_audit')` audit trail. S4 now prevents recurrence.
- **S5 quick-win** — S3036 Chief of Staff Escalation deliverable `de861fe2-17ec-4a4a-a1e3-5a4371335812` reopened (`completed → ready`). Addendum appended contradicting the "self-caused WiFi drop" S3036 resolution with evidence: identical `error_signature: 1cfc0fcf97dd26ce` across 6 non-consecutive dates rules out network variability; deterministic 13:00 UTC firing (Celery-beat schedule window) rules out random WiFi timing. `OpsRunEvent(event_type='info', label='escalation_reopened')` recorded on the underlying OpsRun. PR #3767 unblocks re-resolution — the next morning_brief failure will now surface the actual Python exception.
- **A2 quick-win** — `AutonomyConfiguration` row created for Chris (id `6d4aef2d-365c-44e9-885f-660b0dfbdd1d`). Fills the Step 4 governance gap "AutonomyConfiguration model exists, zero rows." Defaults reflect single-tenant pre-prod context: autonomy_level=`high`, max_daily_actions=200, max_daily_value=`$75`, require_approval_above=`$25`, risk_tolerance=`moderate`, notify_on_action=False (no PA-post spam for single-tenant), 24/7 quiet-hours.

### Rigby Tool Gap Ledger — 3rd trigger entry

`5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` in Donkey Betz workspace received an S3037 append (Rigby persistence-gap: dispatches run tool_runs successfully but do not persist expected `deliverable_tool.create` output). Third trigger of the pattern (S2951 v0 orchestration diagnostic-flag, S2988 `briefing_action_item` exemption workaround, S3037 audit-time persistence miss). Discharge path = Step 6 S8 remediation item (~30-45 min).

---

## The through-line Chris re-remembered mid-session

Session opened with tour of the Findings surface + review of the RaaS/COS GTM gap audit (S2887). During review Chris identified that we'd been on the wrong thread — the pre-Findings arc was actually **"Rigby uses her own tools + agents to build a business for herself"** (S2951 open). That original arc:

1. S2951 — Rigby ran multi-agent orchestration on her own market fit → hit real failures (MarketIntelligenceCoordinator misrouting, ThinkingAgent SynchronousOnlyOperation, deliverable diagnostic flag). Chris ratified the **A1 wedge = Reliability Audit at $500 / $1,500 / $2,500**.
2. S2967 — Chris then pivoted from "fix each little failure" to "use the docs to predict failures" → shipped the Audit Findings surface (S2989 → S3000, 12-of-12 v2 items).
3. **Between S3000 and S3037 (~85 sessions), the original wedge — actually executing a Reliability Audit for a paying customer — was never touched.** Billing plumbing landed (A1 W1/W2 S2846-S2858). No first customer, no first execution.

S3037 fixed that: **first end-to-end execution of the wedge, on ourselves (dogfood).** Reproducible template + 3 concrete shippings + real reliability findings + a Rigby Tool Gap Ledger entry that IS the wedge-blocking constraint we discovered.

---

## Wedge lessons (meta — S3037 self-audit taught us about the wedge itself)

1. **Snapshot converges fast enough to be underpriced at $500.** 1-hour audit + 5 deliverables + 15 findings + immediate-action fixes = way more than $500 of value.
2. **Rigby-executes / Claude-verifies split does not yet work for paid customers.** Rigby's persistence-gap (3rd trigger) means Rigby can find failures but Claude has to compile the report. For paid delivery: either fix S8 first, or explicitly bake "hybrid execution" into the audit contract.
3. **Mis-attribution catches are the highest-value finding class.** S3036 escalation was closed "resolved — WiFi." Audit found deterministic-signature evidence contradicting that. Outside eyes catching a team's own mis-attributions is what customers PAY for.
4. **Snapshot scope (2 workflows, 5 tools, 8-10 pages, 10 items) was correctly sized.** Skipped Step 5 drills mid-audit at Chris's ratification with no loss; the drills are Standard/Deep-Dive value.

---

## Remediation backlog remaining (from Step 6 deliverable `c3cad098-…`)

Shipped this session: A1, A2, S4, A6, S5. **Remaining 5 items:**

- **A3** (45-60 min, QUICK WIN) — Backfill `LLMCallLog.error_type` from `error_message` via regex classifier + save() hook. Closes silent-monitoring gap.
- **S7** (~1 session, CRITICAL) — Root-cause `ThinkingAgent` 67% async failure. Instrument each ORM call site in `.think()`; consider `sync_to_async` at ORM boundary.
- **S8** (30-45 min, **WEDGE-BLOCKING**) — Instrument `deliverable_tool.create` — log intent + result envelope. Test minimum-scope dispatch to isolate root cause of Rigby-persistence gap (3rd trigger this session). **Cheapest strategic win remaining.**
- **S9** (~1 session, HIGH) — Wire downgrade/fallback logic to populate `was_downgraded` / `was_fallback` / `was_auto_selected` on LLMCallLog. S2853 shipping claim not empirically visible in 30d/39,971-call sample.
- **D10** (multi-session, DEFERRABLE) — Historical `LLMCallLog.workspace` backfill for 34,049 NULL rows (85.2% of 30d). Reporting quality, not runtime correctness.

Also carried:
- **A6 Phase 2** — root-cause the underlying `lane_1_platform_readiness` bug now that Phase 1 surfaces the real exception. Wait for next morning_brief failure to fire with new error surface, then investigate.

---

## Rigby SIGN this session

None — this session ran on **direct Claude-execute-and-verify** shape per `feedback_claude_directs_rigby_then_verifies` fallback for ad-hoc bug fixes with Chris-ratified direction and unambiguous design. Precedent from S2988: "SIGN is for spec-originated implementation; ad-hoc bug fixes and Chris-directed feature extensions where design is unambiguous route straight through Claude direct→execute→verify."

Rigby was dispatched twice at Step 2 telemetry pull. Both dispatches ran real tool_runs (surfaced the `Connection error.` signature that seeded Step 2 findings) but neither resulted in a persisted deliverable — 3rd trigger of Rigby persistence-gap logged to Tool Gap Ledger.

---

## Playbook rule exercise

- **PLAYBOOK-7.7.1** (spec→ship contract) — 2 Flow B spec→ship cycles (PR #3767 A6, PR #3768 S4). Spec = audit remediation-backlog items with acceptance criteria; ship = single-PR each.
- **PLAYBOOK-7.4.4** (recycle after merge) — `make recycle-all` executed after each of #3767, #3768; events recorded in `logs/recycle_events.jsonl` (sha=690ba8c6af90, sha=ced5b7ea01b6).
- **PLAYBOOK-7.7.3** (Chris-facing decision framing) — every mid-flight decision routed with "do we lose anything?" + "is it more work later?" tables + a recommendation lean. Applied to tier selection (Snapshot), workflow picks (A+B), execution mode (Rigby-led), Step 5 skip, wedge remediation ordering, close-readiness path.
- **Cycle 1A verify-before-build** — 22nd consecutive session. Both code PRs led with existing-implementation analysis (S1234 D1 lane_4 pattern for A6, `_impl_cleanup_stale_agent_executions` pattern for S4) — no parallel surfaces created.

---

## Files touched

- `core/services/workflow_orchestration_agent.py` (A6 fix)
- `core/tests/test_morning_brief_workflow_template.py` (A6 tests)
- `core/tasks_ops.py` (S4 impl)
- `core/tasks.py` (S4 wrapper)
- `core/celery.py` (S4 beat schedule)
- `core/tests/test_cleanup_stale_ops_runs.py` (S4 tests, NEW)
- 5 workspace deliverables (via ORM — audit output)
- 2 in-session workspace deliverable updates (S3036 escalation reopen, Tool Gap Ledger append)
- `docs/handoffs/SESSION_3037_RELIABILITY_AUDIT_V0_A6_S4_A2.md` (this file)
- `00-START-NEXT-SESSION.md` (refreshed for S3038)
- `tools/pa_local.sh` (wrapper pin bump at close)

---

## Wrapper pin

Active pin at S3037 open: `pa-7a5fff1efe2944bb` (minted at S3036 close).
Retired at S3037 close via `session_lifecycle close`; next-session pin minted + wrapper rewritten.
