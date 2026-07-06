---
title: "ADR-0003 — RIGBY_DELEGATION_ENABLED staged-enable posture (formerly known as MISSION_RUNNER_ENABLED per scoping doc §5 P3)"
adr_id: ADR-0003
slug: mission-runner-staged-enable-posture
status: accepted
authority: design-decision
proposed: 2026-07-06
ratified: 2026-07-06
ratifier: chris
supersedes: (none)
superseded_by: (none)
intake_id: IB-1799-T1-03
arc_ref: I-0100
design_prep: docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_a_mission_runner_staged_enable.md
source_refs:
  - docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md §5 P3 + §7.3 R2/R3 + §8 F4/F8 + §9.1 line 3
  - docs/research/domains/observability/1799_observability_canonical_summary.md §1 point 3 + §2.5 + §120 canonical Cat E row
  - docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_a_mission_runner_staged_enable.md (this ADR's canonical design source per IOS v1.5 §4.3 mandatory design-prep rule)
  - docs/adr/ADR-0001-establish-adr-corpus.md §3.3 + §3.4 (frontmatter + body-section templates followed here)
  - docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md §3.3 F5/F6/F7 folds (correlation contract propagations)
  - core/signals/rigby_delegation_signals.py (the flag-gated handler)
  - core/services/rigby_mission_delegation.py (delegate_work_item entry point)
  - core/settings.py:138-140 (RIGBY_DELEGATION_ENABLED flag definition)
reversibility: 4
  # See §6. Flag flip is trivially reversible; management-command
  # smoke test creates no persistent artifacts requiring cleanup;
  # scoping-doc-baseline-skip (F8-iii 10% partial) is defensible
  # per design-prep §5 pressure test but re-adoption of the skipped
  # phase requires only removing the F8-iii-defensible-skip rationale
  # and reverting to design-prep Option 2b full-3-phase.
sign_cycle_1: SIGN-with-edits (Rigby; single-batch × 4-Q per IOS §7.2 v1.4 on arc pin pa-c5b235f7b15f45be; Q1 SIGN-with-edits/Med-High + Q2 SIGN-with-edits/High + Q3 SIGN-with-edits/Med + Q4 SIGN-with-edits/Med-High; 8 folds F1-F8 applied inline; no BLOCKED; Cycle 2 NOT requested)
sign_cycle_1_pin: pa-c5b235f7b15f45be
companion_docs:
  - docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md
  - docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_a_mission_runner_staged_enable.md
  - docs/adr/ADR-0001-establish-adr-corpus.md
  - docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md
  - docs/research/domains/observability/1799_observability_canonical_summary.md
---

# ADR-0003 — RIGBY_DELEGATION_ENABLED staged-enable posture

## 1. Status

**Accepted** — Chris ratified 2026-07-06 via directive "Agree all F1-F8. Ratify ADR-0003 as accepted. The core architectural decision remains unchanged: Option 5 hybrid rollout. Phase 1 synthetic shadow validation. Phase 2 direct full enable. RIGBY_DELEGATION_ENABLED is the canonical runtime gate. MISSION_RUNNER_ENABLED remains documentation alias only for historical continuity." Rigby SIGN Cycle 1 completed same day (SIGN-with-edits + 8 folds F1-F8 applied inline + no BLOCKED + no Cycle 2). Matches S1399-forward wholesale-ratification pattern.

## 2. Context

Arc I-0100 F4 fold ratified 2026-07-06 requires ADR-B ratifies FIRST (satisfied via ADR-0002 accepted 2026-07-06) and ADR-A ratifies SECOND. This is ADR-A. It resolves the staged-enable posture for `RIGBY_DELEGATION_ENABLED` — the runtime feature flag at `core/settings.py:138-140` that jointly gates two surfaces (`delegate_work_item()` PA action + `rigby_delegation_signals.on_delegation_lifecycle` post_save handler) per design-prep §1.3.

### 2.1 Scoping-doc naming reconciliation (per design-prep §1.4)

Arc I-0100 scoping doc §5 P3 references "Existing feature flag flip: `MISSION_RUNNER_ENABLED = True` + `RIGBY_DELEGATION_ENABLED = True` (paired)." **`MISSION_RUNNER_ENABLED` does NOT exist as a runtime flag.** Verified via `grep -rn 'MISSION_RUNNER_ENABLED' core/ agents/` — zero runtime matches. The actual runtime gate is `RIGBY_DELEGATION_ENABLED` (single flag, two surfaces). This ADR's title preserves the scoping-doc slug for grep-continuity (`mission-runner-staged-enable-posture`) while the body scopes to the actual runtime flag. See design-prep §1.4 for full analysis and Chris's 2026-07-06 directive on treating this as arc-specific (not IOS-structural) — recorded as observation only, does not interrupt implementation.

> **Terminology binding (SIGN Cycle 1 F8 fold — CRITICAL for downstream code / test / dashboard authors):**
>
> - **Runtime flag:** `RIGBY_DELEGATION_ENABLED` (at `core/settings.py:138-140`). This is the SOLE gate this ADR ratifies. Any code, migration, test, dashboard, or ops query written to discharge this ADR MUST use `RIGBY_DELEGATION_ENABLED` — never `MISSION_RUNNER_ENABLED`.
> - **Legacy slug (docs-only alias):** `MISSION_RUNNER_ENABLED` is preserved in prose citations (this ADR's title + slug + scoping doc §5 P3 back-references) FOR GREP CONTINUITY ONLY. **No code path may reference `MISSION_RUNNER_ENABLED`.** If a future refactor eliminates the naming ambiguity fully, this ADR's slug/title are the last vestige — a follow-on housekeeping PR may retire them without invalidating the ratified §3 Decision.
> - **Post-ratification correction:** BACKLOG.md `IB-1799-T1-03` row description referencing `MISSION_RUNNER_ENABLED + paired RIGBY_DELEGATION_ENABLED` is corrected in the ratification-housekeeping commit per §3.6.

### 2.2 Design-preparation source

Per IOS v1.5 §4.3 Stage 2 mandatory design-prep rule: this ADR's canonical design source is the standalone design-preparation document at

**`docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_a_mission_runner_staged_enable.md`**

which enumerates 5 candidate rollout postures × 5 consequence fields, pressure-tests each, and recommends Option 5 (hybrid: shadow-audit-synthetic Phase 1 + direct full-enable Phase 2, defensibly skipping F8-iii 10% partial per low-delegation-routing-cadence rationale). This is the FIRST design-prep artifact authored under IOS v1.5 §4.3.a canonical template. Readers seeking the analytical work behind ratification should read the design-prep first.

## 3. Decision

### 3.1 Sub-decision A — Rollout posture

**Adopt Option 5 (hybrid: shadow-audit-synthetic Phase 1 + direct full-enable Phase 2).** Defensibly skip F8-iii 10% partial phase per §3.3 rationale.

**Phases:**

- **Phase 1 — Shadow-audit-synthetic (~2 sessions, ~150 LOC).** `RIGBY_DELEGATION_ENABLED` remains False in production. Author `manage.py delegation_lifecycle_smoke_test` command (see §3.2). Command spins up synthetic `RigbyWorkItem` + `AgentExecution` rows in a bounded test-mode transaction, exercises the handler at `rigby_delegation_signals.on_delegation_lifecycle` through all 5 lifecycle labels (`agent_assigned` → `agent_completed` → `verification_started` → `verification_completed` → `mission_closed`), verifies expected output shape + idempotency, cleans up. Rigby-runnable via PA tool call OR direct Celery invocation. Pass verdict from Phase 1 gates Phase 2 opening.
- **Phase 2 — Direct full-enable.** Chris explicit directive flips `RIGBY_DELEGATION_ENABLED=True` (settings env var). All delegable work items dispatch via `delegate_work_item()`; handler at `on_delegation_lifecycle` emits 5-label lifecycle for each. Auto-disable triggers active from moment of flip per §3.4.

**Phase 2 entry gate — evidence bundle Yes-required (SIGN Cycle 1 F1 fold).** Phase 2 opens ONLY after Phase 1 produces an explicit go/no-go evidence bundle demonstrating:

- **Zero unhandled exceptions** during the synthetic lifecycle exercise. Any exception (even caught + logged) surfaces to Chris before Phase 2 opens.
- **Successful create → event → evidence join.** All 5 lifecycle labels emitted in expected order; `LLMCallEvent.execution_id` join succeeds; verdict = `verified` for happy path + `failed_agent_error` / `failed_no_llm_calls` for engineered failure fixtures.
- **"Same settings surface" assertion.** Phase 1 execution logs enumerate every setting override applied (`override_settings` targets) and confirms NO runtime feature flag mutation beyond side-effect isolation. See §3.2 F4 fold.
- **Evidence bundle committed to the arc's Stage 3 pre-flight §7 evidence log.** Chris reviews before Phase 2 open directive.

**Silent-drift risks (SIGN Cycle 1 F2 fold).** Phase 1 MUST run against the same routing registry (`DELEGATION_ROUTING`) + handler registry (`rigby_delegation_signals` module imports) + DB constraints (real `AgentExecution` + `OpsRun` + `OpsRunEvent` schemas) as production. **Mocking the routing registry OR the handler dispatch surface is prohibited** — Phase 1 either runs against real production-shape surfaces or its pass verdict does not transfer to Phase 2 safety.

### 3.2 Sub-decision B — Phase 1 shadow-audit-synthetic implementation

**Adopt the management-command approach:** `manage.py delegation_lifecycle_smoke_test`.

Sketch:

```python
# core/management/commands/delegation_lifecycle_smoke_test.py (new file, Stage 3 pre-flight)

class Command(BaseCommand):
    help = 'Exercise rigby_delegation_signals.on_delegation_lifecycle on synthetic rows.'

    def handle(self, *args, **options):
        with transaction.atomic():
            sid = transaction.savepoint()
            try:
                # 1. Create synthetic MissionRun.
                mission_run = OpsRun.objects.create(
                    ops_run_kind='mission',
                    employee_handle='SmokeTestEmployee',
                    # ... other MissionRun fields
                )
                # 2. Create synthetic RigbyWorkItem.
                work_item = RigbyWorkItem.objects.create(
                    source_mission_run=mission_run,
                    decision='monitor',
                    title='Smoke test synthetic delegation',
                    # ... other fields
                )
                # 3. Create synthetic AgentExecution with parent_object_type='RigbyWorkItem'.
                execution = AgentExecution.objects.create(
                    parent_object_type='RigbyWorkItem',
                    parent_object_id=work_item.id,
                    agent=Agent.objects.get(name='TrendAnalysisAgent'),
                    # ... other fields
                    status='pending',
                )
                # 4. Verify agent_assigned emitted.
                assert OpsRunEvent.objects.filter(
                    run=mission_run, label='agent_assigned',
                    detail__execution_id=str(execution.id),
                ).exists()
                # 5. Transition execution to 'completed' + create a mock LLMCallEvent(SUCCESS).
                LLMCallEvent.objects.create(execution_id=execution.id, status='SUCCESS', ...)
                execution.status = 'completed'
                execution.save()
                # 6. Verify all 5 terminal lifecycle labels emitted with verdict=verified.
                for label in ('agent_completed', 'verification_started',
                              'verification_completed', 'mission_closed'):
                    assert OpsRunEvent.objects.filter(
                        run=mission_run, label=label,
                        detail__execution_id=str(execution.id),
                    ).exists()
                # 7. Verify idempotency: re-save should not duplicate.
                execution.save()  # no-op re-fire
                count = OpsRunEvent.objects.filter(
                    run=mission_run, detail__execution_id=str(execution.id),
                ).count()
                assert count == 5  # Or 6 including agent_assigned; adjust per handler pattern.
                # 8. Cleanup: rollback savepoint.
            finally:
                transaction.savepoint_rollback(sid)
        self.stdout.write('DELEGATION_LIFECYCLE_SMOKE_TEST_PASS')
```

**Notes:**

- Command MUST run with `settings.RIGBY_DELEGATION_ENABLED=True` via `override_settings` context manager OR via a Django-management-command-scoped monkeypatch (production flag remains False). Do NOT flip the production flag temporarily — see design-prep §7.1 rejected alternative.
- Command cleanup via transaction savepoint rollback ensures zero persistent artifacts.
- LOC estimate: ~150 (command file + supporting fixture helpers). Ships in P3 PR alongside the settings-flag-flip approval.

**Side-effect isolation hard requirements (SIGN Cycle 1 F3 fold).** Transactional savepoint rollback covers DB-scoped side effects but NOT out-of-band async / signal / external side effects. The command MUST additionally:

- **Run Celery in eager or disabled mode** (`CELERY_TASK_ALWAYS_EAGER=True` OR explicit patching of `execute_agent_task.apply_async` to a synchronous stub) so no async tasks fire.
- **Disable follow-up scheduling / outbound hooks during synthetic execution.** Explicitly set `auto_followup=False` on any AgentExecution creation (matches `delegate_work_item` line 146 default). Patch or disable any signal receivers that would post to PA chat, send email, hit external APIs, or create Deliverables outside the transactional envelope.
- **No PA chat post; no Slack; no webhook.** Command runs headless; any external-effect handler must be identified and neutered before Phase 1 execution begins.

Rationale: synthetic passing while a downstream Celery task escapes the transaction rollback → phantom AgentExecution rows persist → false-negative on Phase 2 safety.

**`override_settings` scope rule (SIGN Cycle 1 F4 fold — CRITICAL).** `override_settings` in Phase 1 is permitted ONLY to disable side effects (e.g., `override_settings(CELERY_TASK_ALWAYS_EAGER=True, PA_CHAT_ENABLED=False)`). **`override_settings` MUST NOT mutate `RIGBY_DELEGATION_ENABLED` OR any other feature flag whose behavior differs between test-mode and production.** The synthetic execution must observe the handler behavior AS IT WOULD BEHAVE IN PRODUCTION with the flag ON — not a test-only variant. If the handler's flag-check at line 147 short-circuits when `RIGBY_DELEGATION_ENABLED=False`, Phase 1's synthetic exercise requires a Django-management-command-scoped monkeypatch on the specific handler entry point OR a temporary `override_settings(RIGBY_DELEGATION_ENABLED=True)` — but if the latter is used, log a WARNING line + record in the Phase 1 evidence bundle that flag-override was applied. Chris ratifies Phase 2 aware of whether the flag was toggled in Phase 1 or not.

**Rejected alternative:** flag-flip-flop-single-window (design-prep §7.1 rejected). Race condition with production PA users during synthetic window.

### 3.3 Sub-decision C — Defensible skip of F8-iii 10% partial phase

**Skip F8-iii's 10% partial phase.** Rationale (per design-prep §5 + §7):

1. **Delegation routing table v0 is single-agent** — `DELEGATION_ROUTING = {'monitor': 'TrendAnalysisAgent'}` at `core/services/rigby_mission_delegation.py:47-49`. Only `monitor` decision routes; `notify` returns 'not_delegatable' and stays in Rigby's queue.
2. **Cadence estimate:** `monitor` work-item daily count is bounded (0–5/day per informal review of RigbyWorkItem creation cadence; needs Stage 3 pre-flight measurement to confirm). At 5/day, 10% partial ≈ 0.5 dispatches per day. Not a meaningful traffic differentiation.
3. **Phase 1 synthetic-audit exercises ALL 5 lifecycle labels deterministically** with full handler-code coverage. Stronger latent-bug detection than 10% real traffic.
4. **Reversibility:** if Stage 3 pre-flight discovers `DELEGATION_ROUTING` has expanded beyond `{monitor}` (e.g., because a routing-expansion PR ships between ADR ratification and P3 authoring), revert to design-prep Option 2b full-3-phase (Phase 1 synthetic → Phase 2 10% partial → Phase 3 full). Re-adoption requires only reverting §3.3 skip rationale and adopting the intermediate phase. §7.3 pre-flight follow-on flags this as a check.

**Stage 3 pre-flight assumption-lock gate (SIGN Cycle 1 F5 fold — Yes-required before P3 merge).** Before P3 PR merges, verify ALL of the following:

- **Routing cardinality:** `len(DELEGATION_ROUTING) == 1` and `DELEGATION_ROUTING == {'monitor': 'TrendAnalysisAgent'}` (exact match). If expanded, snap back to design-prep Option 2b full-3-phase — reinstate 10% partial phase between Phase 1 and Phase 2.
- **Estimated daily volume:** measured `RigbyWorkItem` daily creation cadence (from ORM `RigbyWorkItem.objects.filter(created_at__gte=<30d>).count() / 30`) is `< 10/day` OR pre-flight ratifies a higher threshold with Chris. If cadence has grown, re-run pressure test — Option 5 defensibility depends on low cadence.
- **Handler surface unchanged:** `rigby_delegation_signals.on_delegation_lifecycle` source has not been amended since ADR-A ratification date. If it has, re-run Phase 1 synthetic against the amended handler before Phase 2.

### 3.3.a Assumption lock (SIGN Cycle 1 F6 fold)

**Assumptions this ADR ratifies at 2026-07-06 and REQUIRES verifying at Stage 3 pre-flight:**

| Assumption | Verification method | Snap-back plan if violated |
|-----------|---------------------|--------------------------|
| `DELEGATION_ROUTING` cardinality == 1 (single-agent) | `python -c "from core.services.rigby_mission_delegation import DELEGATION_ROUTING; print(len(DELEGATION_ROUTING))"` returns `1` | Revert to design-prep Option 2b full-3-phase with 10% partial reinstated |
| Delegable-work-item daily cadence `< 10/day` | 30-day ORM count divided by 30 | Same as above |
| Handler code (`rigby_delegation_signals.on_delegation_lifecycle` + adjacent helpers) unchanged since 2026-07-06 | `git log --since=2026-07-06 -- core/signals/rigby_delegation_signals.py` returns no commits | Re-run Phase 1 synthetic against amended handler before Phase 2 |
| `RIGBY_DELEGATION_ENABLED` remains the sole runtime gate | `grep -rn "MISSION_RUNNER_ENABLED" core/ agents/` returns zero code matches (docs matches OK) | If a new flag has been added, re-scope this ADR OR extend Phase 1 synthetic to exercise the new flag path |
| MissionRunner class contract unchanged (nine invariants I1-I9 per S1705 F1) | Existing `test_mission_runner.MissionRunnerImportContractTests` passes | Halt Phase 1 opening; route to Chris |
| Existing 3-employee OpsRun/OpsRunEvent write path (Documentation Manager, Platform Auditor, Chief of Staff) unaffected by rollout | Baseline OpsRun daily count (~2/day = 36/20d per 1799 §2.5) does not decrease during Phase 2 monitoring | Auto-disable Phase 2; investigate |

The assumption-lock table IS a load-bearing part of this ADR — its violation invalidates the §3.3 defensible-skip rationale and requires re-ratification.

### 3.4 Sub-decision D — Auto-disable triggers per phase

| Trigger | Phase 1 (synthetic) | Phase 2 (production) |
|---------|---------------------|----------------------|
| First `LABEL_AGENT_COMPLETED` with `event_type='step_fail'` | N/A (synthetic outcomes deterministic) | Log ERROR + Rigby alert; do NOT auto-disable on single fail unless failure rate `> threshold`. Protects against a single flaky work-item causing full arc rollback. |
| OpsRunEvent daily growth `> threshold` | N/A | Threshold = `baseline_daily_OpsRunEvent_count × 1.5` (measured at Stage 3 pre-flight). Auto-disable RIGBY_DELEGATION_ENABLED on breach; page Chris. |
| Handler exception rate `> N/hour` | N/A | Trigger auto-disable + Rigby alert. |
| **Data-integrity regression (SIGN Cycle 1 F7 fold — Yes-required)** | N/A | Auto-disable if `OpsRunEvent.execution_id NULL-rate > Y%` over N minutes for `label` in {`agent_assigned`, `agent_completed`, `verification_completed`, `mission_closed`}. Threshold Y set at Stage 3 pre-flight (starting default Y=5% over 10 minutes; measurable via `OpsRunEvent.objects.filter(created_at__gte=<T-10m>, label__in=[...]).exclude(detail__has_key='execution_id').count() / total_count`). Similarly monitor `OpsRun` invariant violations from MissionRunner nine-invariants (S1705 F1). Detects handler drift or race conditions writing incomplete lifecycle rows. |
| **Repeated error signature across distinct requests (SIGN Cycle 1 F7 fold — Yes-required)** | N/A | Auto-disable if the SAME exception signature (matched via error type + first-line traceback normalization) appears across ≥ K distinct `trace_id` values in a rolling window — EVEN IF the per-hour rate is below the "Handler exception rate > N/hour" threshold. Distinct-trace repetition indicates a code path bug reproducing for different inputs, not a flaky one-off. K = 3 as starting default; tunable at Stage 3 pre-flight. |
| Chris manual disable directive | Applies at any phase | Same |

### 3.5 Correlation contract compliance (per ADR-0002 §3.3 propagations)

- **F5 correlation contract:** `rigby_delegation_signals._verify_execution` at line 102 already queries `LLMCallEvent.objects.filter(execution_id=execution.id, status='SUCCESS')` — the join is Yes-implemented. Post-ADR-B P4 (write-side runtime discharge), this join extends to PA-driven executions cleanly.
- **F6 parent_execution_id chain:** delegated executions dispatched from PA sessions require `parent_execution_id = <pa_execution_id>` per ADR-B §3.3 F6. `delegate_work_item()` at `rigby_mission_delegation.py:131` must propagate the calling PA execution context. **This ADR does NOT block on ADR-B P4** — Phase 1 (synthetic) and Phase 2 (production) both work regardless of parent_execution_id population. But full end-to-end PA→delegation provenance chain requires P4 to ship first. See §7.2 Stage 3 pre-flight follow-on.
- **F7 ToolCallRecord.conversation_id warning:** ADR-A verification queries in §6 use `execution_id` + `trace_id` + `parent_object_id` — NOT `ToolCallRecord.conversation_id`. F7 warning honored.

### 3.6 IB-1799-T1-03 BACKLOG naming correction (housekeeping)

Post-ratification housekeeping: BACKLOG.md `IB-1799-T1-03` row description references `MISSION_RUNNER_ENABLED + paired RIGBY_DELEGATION_ENABLED`. Chris/Rigby preference — recommend correcting to single-flag scope: "staged unlock of `RIGBY_DELEGATION_ENABLED` per F8-iii-adapted rollout." Not blocking on this ADR's ratification; can batch into P3 PR OR housekeeping stage-transition PR.

## 4. Consequences

### 4.1 Enabled

- **Rigby delegation lifecycle observability lights up.** All 5 lifecycle labels (`agent_assigned` → `mission_closed`) accumulate in `OpsRunEvent` for every delegated work item post-Phase-2. Rigby's `ops_tool.mission_run_timeline` returns the full 6-event chain.
- **R3 dormancy risk discharged.** Handler code at `rigby_delegation_signals.on_delegation_lifecycle` (shipped S1250 PR8 2026-05-31, unexercised in production since) gets validated on synthetic + real traffic.
- **Arc I-0100 P3 PR (IB-1799-T1-03) unblocks.** F4 fold ordering satisfied; ADR-A ratifies second; P3 sequenced next per §5 P3 in scoping doc.
- **PA→delegation provenance chain** (via ADR-B F6 parent_execution_id) can extend across delegated executions post-P4.
- **1799 xx99 §1 point 3 Cat E** design-intent-latent gap closes for delegation path.

### 4.2 Obligated

- **`manage.py delegation_lifecycle_smoke_test` command MUST be authored** in P3 PR per §3.2 sketch (~150 LOC).
- **Baseline OpsRunEvent volume measurement** at Stage 3 pre-flight to set §3.4 auto-disable threshold.
- **Confirm `DELEGATION_ROUTING` state at Stage 3 pre-flight.** If expanded beyond `{monitor: TrendAnalysisAgent}`, revert to design-prep Option 2b full-3-phase per §3.3 defensible-skip rationale.
- **P3 PR body cites this ADR** per IOS §5.2 rule 5 (`adr_ref: ADR-0003`).
- **Chris directive required for Phase 2 flag flip.** Not auto-triggered by Phase 1 pass; explicit ratification.
- **Auto-disable code paths** (§3.4 triggers) must be implemented in P3 PR OR pre-existing monitoring surfaces must accept the responsibility. Stage 3 pre-flight determines implementation surface.

### 4.3 Non-goals

- **This ADR does NOT introduce `MISSION_RUNNER_ENABLED` as a new flag.** Per §2.1 naming reconciliation.
- **This ADR does NOT modify MissionRunner class or Celery employee tasks.** Existing OpsRun writes from Documentation Manager / Platform Auditor / Chief of Staff unaffected.
- **This ADR does NOT resolve D74 six-axis correlation-spine posture.** ADR-C (`ADR-0004` reserved slug) handles.
- **This ADR does NOT decide unified retention posture.** `IB-1799-T0-02` conditional input to ADR-C per F2 fold.
- **This ADR does NOT change ADR-0002's correlation contract.** F5/F6/F7 folds are inherited constraints, not modifications.

## 5. Alternatives considered

Full alternatives enumeration inherited from design-prep §4 + §8:

### 5.1 Option 1 — Permanent-OFF (rejected)

`RIGBY_DELEGATION_ENABLED` stays False indefinitely. Rejected: unmitigated R3 dormancy risk; zero observability into whether handler code works.

### 5.2 Option 2a — Shadow-passive (rejected)

Enable flag but neuter `delegate_work_item()` dispatch. Rejected: requires new dispatch-neuter branch (code cost); only exercises `delegation_started` writer, not the 5-label lifecycle. Weaker latent-bug detection than synthetic-audit approach.

### 5.3 Option 2b — Full-3-phase (shadow-audit-synthetic → 10% partial → full) — retained as fallback

Design-prep §4 Option 2b. Available as fallback if Stage 3 pre-flight discovers `DELEGATION_ROUTING` expansion beyond `{monitor}` per §3.3 conditional reversal clause. Not the default choice because current low-cadence delegation routing makes the 10% partial phase indistinguishable from zero traffic.

### 5.4 Option 3 — Direct full-enable (rejected)

Skip all validation phases; flip flag → True. Rejected: skips R3 dormancy validation entirely.

### 5.5 Option 4 — Per-employee canary (rejected)

Enable per employee sequentially (Documentation Manager → Platform Auditor → Chief of Staff). Rejected: current per-employee handler code is uniform (same `rigby_delegation_signals.on_delegation_lifecycle` for all employees); canary provides no differential signal.

### 5.6 New `MISSION_RUNNER_ENABLED` flag (rejected)

Introduce a distinct `MISSION_RUNNER_ENABLED` flag as a companion to `RIGBY_DELEGATION_ENABLED`. Rejected: (a) MissionRunner is not gated today and gating it would break existing OpsRun writes from 3 employee missions; (b) the naming discrepancy is scoping-doc-specific, not a real feature-flag requirement; (c) adding an unused flag violates IOS §5.1 rule 7 (feature-flag consumer verification — zero-consumer flags are `DECLARED-FEATURE-FLAG-GATES-NOTHING` per Sports F.F3 pattern and disqualify the arc).

## 6. Reversibility

**Rating: 4 (reversible with light effort).**

### 6.1 What "reverse" means

Reversing ADR-0003 means either (a) turning off `RIGBY_DELEGATION_ENABLED` (halts new dispatches + lifecycle events; existing rows remain queryable), (b) removing the `manage.py delegation_lifecycle_smoke_test` command (single file deletion), OR (c) reverting the §3.3 defensible-skip decision (re-adopting the 10% partial phase).

### 6.2 Reversal effort

- **Flag flip (a):** trivial — 1-line settings change via env var OR Chris explicit directive.
- **Command removal (b):** trivial — delete `core/management/commands/delegation_lifecycle_smoke_test.py`. Command is stateless; no data to clean up.
- **Defensible-skip revert (c):** trivial — remove §3.3 skip rationale; re-adopt design-prep Option 2b full-3-phase.

### 6.3 What is NOT reversible

- **OpsRunEvent rows written during Phase 2** remain queryable. Truncation via marker filter (`OpsRunEvent.objects.filter(label__startswith='...').delete()`) is bounded scope; safe if flag is OFF (no new writes competing).
- **Handler-code validation gained in Phase 1** is preserved knowledge; reverting the flag does not un-validate the handler.

Rating 4 reflects the flag-flip primary reversal path. Combined reversal (a+b+c) is still bounded.

## 7. Provenance

### 7.1 Rigby SIGN record

**Cycle 1 completed 2026-07-06 on arc pin `pa-c5b235f7b15f45be` per IOS §7.2 v1.4.** Single-batch × 4-Q. Overall verdict: **SIGN-with-edits** (no BLOCKED; Cycle 2 NOT requested).

| Q | Sub-Q | Verdict | Confidence | Folds applied inline |
|---|-------|---------|-----------|----------------------|
| Q1 | Rollout posture (§3.1) — Option 5 hybrid safe for low delegation cadence? | SIGN-with-edits | Med-High | **F1** — §3.1 Phase 2 entry gate: evidence bundle Yes-required (0 unhandled exceptions + successful create→event→evidence join + same-settings-surface assertion + evidence-bundle committed to Stage 3 §7 log). **F2** — §3.1 silent-drift risks: Phase 1 must run against same routing + handler registry; mocking prohibited. |
| Q2 | Phase 1 synthetic implementation (§3.2) — manage.py smoke test + savepoint safe? | SIGN-with-edits | High | **F3** — §3.2 side-effect isolation hard requirements: Celery eager/disabled mode; disable follow-up scheduling / outbound hooks. **F4** — §3.2 `override_settings` scope rule: permitted only for side-effect disabling; must NOT mutate runtime feature flags (log WARNING + record in evidence bundle if applied to RIGBY_DELEGATION_ENABLED). |
| Q3 | Defensible-skip of F8-iii 10% partial (§3.3) — low-cadence rationale defensible? | SIGN-with-edits | Med | **F5** — §3.3 Stage 3 pre-flight assumption-lock gate Yes-required: routing cardinality == 1 + estimated cadence < 10/day + handler code unchanged since ratification. If violated, snap back to design-prep Option 2b full-3-phase. **F6** — §3.3.a assumption-lock table codifies 6 assumptions + verification method + snap-back plan. |
| Q4 | Auto-disable triggers (§3.4) + naming discrepancy handling (§2.1) | SIGN-with-edits | Med-High | **F7** — §3.4 add data-integrity regression trigger: OpsRunEvent.execution_id NULL-rate > Y% (default 5% over 10min); repeated error signature across ≥K distinct trace_ids (default K=3). **F8** — §2.1 add terminology binding box: RIGBY_DELEGATION_ENABLED is the SOLE runtime gate; MISSION_RUNNER_ENABLED is docs-only legacy slug; NO CODE may reference MISSION_RUNNER_ENABLED. |

Total: 8 folds F1-F8 applied inline. All folds are additive-clarifying (hard requirements, warnings, evidence-bundle discipline, assumption-lock table) — none reverse a §3 Decision commitment.

### 7.2 Chris ratification

**Ratified 2026-07-06.** Chris "agree all F1-F8" wholesale ratification via terminal directive: "Agree all F1-F8. Ratify ADR-0003 as accepted. The core architectural decision remains unchanged: Option 5 hybrid rollout. Phase 1 synthetic shadow validation. Phase 2 direct full enable. RIGBY_DELEGATION_ENABLED is the canonical runtime gate. MISSION_RUNNER_ENABLED remains documentation alias only for historical continuity." `status` frontmatter flipped `proposed → accepted`; `ratified: 2026-07-06`, `ratifier: chris` populated.

### 7.3 Related PRs

- `#2941` (MERGED) First-queue seed
- `#2945` (MERGED) Arc I-0100 Stage 1 arc-open bundle
- `#2947` (MERGED) IOS v1.3 cascade discipline
- `#2948` (MERGED) IB-Q1-BOOT-01 P0 prep — ADR corpus + ADR-0001
- `#2949` (MERGED) IOS v1.4 fresh-session Stage 2 readiness
- `#2950` (MERGED) Arc I-0100 Stage 2 opening ceremony
- `#2951` (MERGED) ADR-B / ADR-0002 ratified
- `#2952` (MERGED) IOS v1.5 design-prep first-class artifact
- **This PR** — ADR-A / ADR-0003 authoring + design-prep. Ratification-pending.
- **Future:** P3 PR (IB-1799-T1-03) — gated on this ADR's ratification. Ships `manage.py delegation_lifecycle_smoke_test` command + Phase 1 execution + Phase 2 flag flip + auto-disable trigger implementation.

### 7.4 Related intake rows

- **`IB-1799-T1-03` (BACKLOG.md T1) — the discharge target.** This ADR ratifies the design; P3 PR ships the code. Row flips `IN_ARC → SHIPPED` at P3 merge with `adr_ref: ADR-0003` and `pr_refs: #<P3>`. See §3.6 for BACKLOG naming-correction housekeeping recommendation.
- **`IB-1799-T1-02`** — ADR-B / ADR-0002 ratified 2026-07-06; P4 PR pending. F6 parent_execution_id chain requires P4 shipped for full PA→delegation provenance (§3.5).
- **`IB-1799-T1-01`** — SPEC_COMPLETE; ships unconditional per F3 fold; P2 PR pending.

### 7.5 Related debt rows

- **`IDBT-0001`** PARTIAL_DISCHARGE HIGH — 1799 slice discharge in Arc I-0100 scope. This ADR discharges the Cat E slice.
- **`IDBT-0002`** TECH_DEBT_ACCRUED MEDIUM — RAG-owned embed-invalidation gap; delegated to Group 2100 RAG. Not affected by this ADR.
- **Potential IDBT-0003 candidate (from ADR-0002 §7.5):** ToolCallRecord.conversation_id UUID vs AgentExecution.conversation_id CharField(64) type mismatch. Cross-ref preserved; this ADR does not use ToolCallRecord.conversation_id joins per F7 warning.

## 8. Follow-on ADRs blocked on this one

Per Arc I-0100 F4 fold ordering:

| ADR ID (reserved) | Slug | Content | Blocking shape |
|-------------------|------|---------|----------------|
| `ADR-0004` | `d74-six-axis-correlation-spine-posture` | ADR-C — D74 six-axis correlation-spine posture; consumes ADR-A (this ADR)'s rollout posture as INPUT for volume-projection under `RIGBY_DELEGATION_ENABLED=True` steady state. F1 fold: architecture-only ADR-C track; no in-arc migrations beyond P2/P4. Optional per F4 fold. |

---

**END ADR-0003-mission-runner-staged-enable-posture.md — proposed 2026-07-06.**
