---
session: 1706
status: closed (Group 1700 Cat F Adjacent/Separation Boundaries child audit LANDED — SIXTH and LAST child under Group 1700 per parent D72 P6 slot; audit doc landed `status: active` post-fold; Rigby SIGN cycle 1 SIGN-with-edits at Medium/Medium-High confidence on arc pin `pa-e7fbacc996b34b44` — fresh SIGN isolation pin `pa-a5ce5fdd56364dee` minted per playbook §15 but routed-around by `tools/pa_local.sh:128` wrapper hard-code (S1600/S1700/S1701/S1702/S1703/S1704/S1705 precedent: arc pin doubles as SIGN pin; fresh SIGN pin retired at S1706 close per §16 with `updated_count=1, retired=true, previously_active=true`); F1-F4 folds landed pre-commit; D48 preemptive stability-probe gate 23rd arm HOLDING CLEAN — 18-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702+S1703+S1704+S1705+S1706 CONFIRMED per single-batch-4-question criterion; ARCHITECTURE_INDEX v48 → v49 with §1.52 S1706 registration + §8 timeline S1706 row + line-6 v49 preamble; OPEN_ARCS Group 1700 In-progress row current-child updated S1705 → S1706 AND row prepared for imminent transition to Awaiting summary at S1799 xx99 close; arc pin retained through Group 1700 close at S1799 — the LAST session under Group 1700 arc; next session: S1799 xx99 canonical summary — LAST session under Group 1700)
date: 2026-07-03
arc: Research Group 1700 (Observability / Telemetry / SLOs) — Cat F Adjacent / Separation Boundaries child audit; SIXTH and LAST child session under Group 1700 per D72 P6 slot before S1799 xx99 canonical summary
category: research (playbook §11.2 child audit template + §13 six-parallel-Explore + §14 verifier-loop + §15 SIGN cycle 1)
head_commit_before: 7b8dd128 (main; post-S1705 close + PR #2846 audit + PR #2847 cascade artifacts)
head_commit_after: (this session's commit)
authors: Claude Code (Chris directed via short command "start research group 1706")
---

# Session 1706 — Group 1700 Cat F Adjacent / Separation Boundaries Child Audit

> **Sixth and LAST child audit under Group 1700 (Observability arc) before S1799 xx99 canonical summary.** Playbook §11.2 20-section template SIXTH application under Group 1700 arc (first was S1701 Cat A CeleryTaskEvent; second S1702 Cat B LLMCallEvent; third S1703 Cat C AgentExecution; fourth S1704 Cat D ToolCallRecord; fifth S1705 Cat E OpsRun+OpsRunEvent). 6-parallel-Explore sweep + parent-Claude verifier-loop applied both pre-Explore and post-Explore. Rigby SIGN cycle 1 delivered SIGN-with-edits at Medium/Medium-High confidence via single-batch 4-question pattern (D48 23rd arm HOLDING CLEAN — 18-consecutive-fully-clean-arms sub-pattern confirmed).

## What shipped

### 1. Audit doc

- **`docs/research/domains/observability/1706_observability_cat_f_adjacent_separation_boundaries_audit.md`** (NEW; ~950 lines post-fold)
- `status: active` after Rigby SIGN cycle 1 SIGN-with-edits
- `authority: child-audit`, `category: child_audit`, `session: 1706`, `child_slot: P6`, `domain_slug: observability`, `research_group: 1700`, `sub_slots: [F.a Body Systems / HeartBeat, F.b SLO framework audit, F.c Event-model catalog + WRITE-ONLY-FORGOTTEN audit, F.d Doc-claim verifier drift as meta-observability signal, F.e Observability↔Event-Architecture terminology boundary]`
- Applies playbook §11.2 20-section child audit template + §13 6-parallel-Explore + §14 verifier-loop discipline (both pre-Explore and post-Explore)

### 2. Rigby SIGN cycle 1 folds (F1-F4, all landed pre-commit)

- **F1 (Q1 SIGN-with-edits Medium)** — Candidate-surface disposition bullet list added to §1 executive: resolve_node telemetry OUT-of-scope (separate media/render ops), memory_pressure NOT event-model (does not alter boundary), fleet auth token audit = security/compliance desk, no additional `RIGBY_*_INTAKE_ENABLED` siblings found.
- **F2 (Q3 SIGN-with-edits Medium)** — F9 axis label renamed OBSERVABILITY-FRAMEWORK-UNBOUNDED-RETENTION → **RETENTION-PATTERN-INCONSISTENT (unbounded growth across key observability/event tables)** + "cross-cat pattern with Cat F as consolidation point" clarifying line added to §1.1 F9 row + §9.1 D74 matrix cell.
- **F3 (Q4 CONFIRM-with-edit Medium-High)** — R1 "xx99 output = posture/decision + evidence; purge-task implementation post-arc T-slot per §14.5" scope-discipline sentence added.
- **F4 (Q4 CONFIRM-with-edit Medium-High)** — R8/R9 marked "optional / non-blocking — not required shipping work during research".

### 3. §1.1 F1-F9 findings lock-in

- **F1 (HIGH)** Passive-leak retention pattern — HeartBeat + DeliverableEvent + OpsRunEvent lack date-based purge tasks despite comparable-cadence peer tables (LearningReadbackEvent 30-day at `core/celery.py:246`, FleetEvent 30-day at `core/services/fleet_event_cleanup.py:70`, CeleryTaskEvent weekly) that DO have beat-scheduled purge. Growth projection at 10-min cadence: 144/day × 365 = ~52.5K HeartBeat rows/year unbounded. Structural inheritance of S1705 F6 + S1704 F5 + S1702 F4 + S1701 F6 across Cat F surface.
- **F2 (MEDIUM)** 10 body-system getters in code (`core/services/body_vitals.py:340-790` includes `_get_nervous_vitals` at :744-790) vs PLATFORM_INVENTORY.md:24 + CLAUDE.md `Live Counts` autoblock both claim "9 body systems." Nervous is the missing 10th.
- **F3 (MEDIUM)** `check_learning_loop_slo` at `core/tasks.py:13170` — parent §5.F + start-here L89 + S1273 line 1969 all cite `core/tasks.py:12492`. +678 line drift.
- **F4 (POSITIVE differentiator)** 1/14 event-shaped models truly WRITE-ONLY-FORGOTTEN (ABTestEvent at `core/models_unified_system.py:8686`, writer at `core/views_ab_testing.py:481`, ZERO consumer sites). Post-Explore verifier-loop correction: CockpitIncidentEvent consumed at `core/views_diagnostics.py:3889` (`.filter(incident=inc).order_by('created_at')`); CockpitAutopilotEvent consumed at `core/views_diagnostics.py:3367` (`.select_related('policy')[:limit].values(...)`). Both corrected to WIRED-BOTH-SIDES from Agent 3's WRITE-ONLY-FORGOTTEN pre-Explore claim. Cat F event-model surface is healthier than S1273 lines 1912-1917 hypothesized: 12/14 WIRED-BOTH-SIDES + 1 PRODUCER-ONLY-BY-DESIGN (EngagementEvent) + 1 truly orphan (ABTestEvent).
- **F5 (MEDIUM)** SLO surface = 2 beat-scheduled true-SLOs (`check_learning_loop_slo` + `check_llm_cost_spike` at `core/tasks_misc.py:5048`) + 8 on-demand hardcoded SLOs in `_ops_slo_status` at `core/services/td_handlers_ops.py:365-648` (2-min cache, zero persistence) + 0 `SLOResult`/`SLABreach`/`ServiceLevelObjective` model. CTO/COO/Trend Analysis dailies are threshold-gated alert escalators, NOT SLOs.
- **F6 (POSITIVE)** Doc-claim verifier at `core/services/doc_claim_verification.py` (3275 lines, 128,672 bytes) has 75 `@register_claim` decorators (grep-verified via `grep -c`). Consumed daily by `core/jobs/docs_cascade.py:105 DRIFT_LABEL="step_5_drift_observed"` emitting OpsRunEvent detail with `drift_count` + `drift_items_count`. Embedded in PLATFORM_INVENTORY.md via `core/services/platform_inventory.py:605-639`. But: zero dedicated persistence table + zero CI/GitHub Actions gating + zero alert/notification integration. Classification: **DESIGN-INTENT-LATENT** (S1705 F1 analog).
- **F7 (POSITIVE)** HeartBeat + BodyVitalsService + 10 body systems structurally intact. Producer wired (`run_heartbeat` @ `core/celery.py:39-42` every 600s → `heart.pulse()` at `core/services/heart.py:121-201` → `record_heartbeat()` at :649-665). 4 consumer sites: REST at `core/views_heart.py:78, 705`, agent narrative at `core/agents/content_writer_agent.py:544`, task-detail debug at `core/services/td_handlers_ops.py:3845, 4917, 4943`. Redis pub/sub publish at `core/tasks_misc.py:3045` (no consumer for `heart:status` channel). Discord alert at `core/services/heart.py:667-698`. S1273 line 1965 export gap VERIFIED as integration-gap (REST endpoints exist; frontend `.tsx/.ts` files show ZERO imports of `/api/heart/*`). S1273 line 1964 "digestive+muscular sluggish/paralyzed on fresh DB" claim NOT verified via code — `core/services/digestive.py:103-114` + `core/services/muscular.py:115-170` default to healthy/strong on zero-execution baseline. Flagged SPECULATIVE.
- **F8 (MEDIUM)** Observability↔Event-Architecture terminology boundary recommendation for xx99 §5 posture-decision brief: **PERMEABLE with producer/consumer structural split.** Execution telemetry (Cat A-E) = Group 1700 core; 14+ event-shaped models = observability-adjacent PRODUCERS, Group 1900 owns CONSUMERS/routing. Terminology stability grid: 3 pairs STABLE (Alert/Notification/Incident + Producer/Emitter/Writer + Consumer/Aggregator/Sink) + 2 pairs DRIFTED (Event/Telemetry/Observation/Signal + Monitor/SLO/Health-check) + 1 pair UNSTABLE (Metric/Log/Trace due to `trace_id` dead on deprecated `AgentExecution` per S1703 F1 landmine).
- **F9 (D74 axis contribution)** **RETENTION-PATTERN-INCONSISTENT (unbounded growth across key observability/event tables)** — sixth axis cell distinct from Cat A DEEP-WIRED / Cat B DEEP-WIRED-BUT-DEDUP-UNRESOLVED / Cat C COVERAGE-GAP-ON-PA-PATH / Cat D ACTIVELY-BROKEN / Cat E LATENT-VIABLE-BUT-FLAG-GATED. Cross-cat pattern (A/B/D/E/F evidence) with Cat F serving as consolidation/ratification point rather than unique root cause (per Rigby SIGN Q3 F2 fold). Feeds xx99 §5 posture-decision brief.

### 4. §16 Boundary Violations (5 candidates all LEGITIMATE)

HeartBeat writers + BodyVitalsService + `check_learning_loop_slo` + doc-claim verifier via docs_cascade + CTO/COO diagnostics via mission scheduler. No unexpected writer sites detected via grep. Cat F is self-contained per parent §5.F sub-slotting design.

### 5. §16.1 Observability↔Event-Architecture recommendation

**PERMEABLE with producer/consumer structural split.** Not a naming problem — a producer/consumer structural division that preserves parent D2 delegation to Group 1900 while keeping producer-side telemetry within Cat A-F Observability scope.

### 6. §19 R1-R10 follow-ons

- R1 (HIGH, load-bearing for xx99) — F1 retention posture decision; xx99 = posture + evidence, purge-task implementation post-arc T-slot per §14.5.
- R2 (HIGH) — F9 D74 axis posture decision.
- R3 (MEDIUM) — F5 SLO framework scoping post-arc.
- R4 (MEDIUM) — F6 doc-claim verifier observability integration.
- R5 (MEDIUM) — F8 terminology recommendation ratification.
- R6 (MEDIUM) — F2 body-system inventory refresh via `refresh_doc_inventory_blocks` + `generate_platform_inventory`.
- R7 (LOW) — F4 ABTestEvent orphan disposition (Group 1900 territory).
- R8 (LOW, non-blocking) — F7 HeartBeat export UI wiring.
- R9 (LOW, non-blocking) — F7 SPECULATIVE cold-start behavior verification.
- R10 (LOW) — F3 parent scoping / start-here line-cite refresh.

### 7. Session close artifacts

```
docs/research/domains/observability/1706_observability_cat_f_adjacent_separation_boundaries_audit.md   [new; ~950 lines post-fold; SIXTH and LAST child under Group 1700]
docs/research/ARCHITECTURE_INDEX.md                                                                    [modified — v48 → v49 with §1.52 S1706 registration + §8 timeline S1706 row + line-6 v49 preamble]
docs/research/OPEN_ARCS.md                                                                             [modified — Group 1700 In-progress row current-child updated S1705 → S1706 AND row prepared for Awaiting summary transition at S1799]
docs/handoffs/SESSION_1706_OBSERVABILITY_CAT_F_ADJACENT_SEPARATION_BOUNDARIES.md                       [new — this handoff]
00-START-NEXT-SESSION.md                                                                               [modified — S1706 Cat F CLOSED; next-session priority = S1799 xx99 canonical summary + Group 1700 arc-close]
```

## Verifier-loop record

**Pre-Explore verified (playbook §14, front-runs Rigby grep):**
- `core/models_heart.py`, `core/services/{heart,body_vitals,doc_claim_verification}.py` all EXIST as concrete files.
- `check_learning_loop_slo` at `core/tasks.py:13170` (not 12492 as parent claims — F3 drift caught pre-Explore).
- All 14 event-shaped models confirmed as concrete Django model classes at claimed file:line anchors via `grep -E '^class (DeliverableEvent|...)\('`.
- `RIGBY_EVENT_INTAKE_ENABLED` default `False` confirmed at `core/signals/deliverable_status_signals.py:47`.

**Post-Explore verified (playbook §14, trust-but-verify sub-agent claims):**
- **10-vs-9 body systems drift** — `_get_nervous_vitals` at `body_vitals.py:744-790` present; PLATFORM_INVENTORY.md:24 + CLAUDE.md autoblock claim 9. F2 locked.
- **CockpitIncidentEvent consumer** — grep found `views_diagnostics.py:3889` filter+order_by consumer; Agent 3 verdict corrected. F4 locked.
- **CockpitAutopilotEvent consumer** — grep found `views_diagnostics.py:3367` select_related+values consumer; Agent 3 verdict corrected. F4 locked.
- **ABTestEvent WRITE-ONLY-FORGOTTEN** — grep across `core` returned only writer at `views_ab_testing.py:481` + model def + import; NO consumer. F4 locked as true 1/14 orphan.
- **75 `@register_claim` decorators** — `grep -c '@register_claim'` in `doc_claim_verification.py` returned 75. F6 locked.
- **`step_5_drift_observed` OpsRunEvent** — grep confirmed at `core/jobs/docs_cascade.py:105 DRIFT_LABEL = "step_5_drift_observed"` plus emission sites at :386, :612, :677. F6 locked.
- **HeartBeat purge absence** — grep of `core/celery.py` for "heartbeat" returned only writer beat entry at :39-42; no cleanup task. F1 locked.
- **FleetEvent 30-day purge** — confirmed at `core/services/fleet_event_cleanup.py:70` (`FLEET_EVENT_RETENTION_DAYS=30`). Peer-comparison evidence for F1.
- **LearningReadbackEvent cleanup beat-scheduled** — confirmed at `core/celery.py:246` (`'task': 'core.tasks.cleanup_learning_readback_events'`). Peer-comparison evidence for F1.

**Verifier-loop verdict:** Two Agent 3 claims materially corrected pre-Rigby (CockpitIncidentEvent + CockpitAutopilotEvent). One Agent 3 claim confirmed (ABTestEvent). All other load-bearing claims verified as posted.

## Rigby SIGN cycle 1 record

**Routing:** Arc pin `pa-e7fbacc996b34b44` (S1600/S1700/S1701/S1702/S1703/S1704/S1705 precedent: arc pin doubles as SIGN pin). Fresh SIGN isolation pin `pa-a5ce5fdd56364dee` minted per playbook §15 promoted rule — routed-around by `tools/pa_local.sh:128` wrapper hard-code — retired at S1706 close per §16 with `updated_count=1, retired=true, previously_active=true`.

**Verdicts (single-batch 4-question per S1701-S1705 precedent):**

| Q | Verdict | Confidence | Folds landed |
|---|---------|-----------|--------------|
| Q1 coverage completeness | SIGN-with-edits | Medium | F1 candidate-surface disposition bullet list added to §1 executive |
| Q2 drift severity | CONFIRM | Medium-High | No folds (F1 stays HIGH not CRITICAL; F2/F3 rankings confirmed) |
| Q3 D74 axis correctness | SIGN-with-edits | Medium | F2 F9 axis label renamed + cross-cat pattern with Cat F as consolidation point clarifying line |
| Q4 R1-R10 ranking + xx99 scope discipline | CONFIRM (with 2 small scope-discipline edits) | Medium-High | F3 R1 posture-vs-implementation + F4 R8/R9 non-blocking labels |

**D48 preemptive stability-probe gate 23rd arm HOLDING CLEAN** — single-batch 4-question pattern per S1701-S1705 precedent. **18-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702+S1703+S1704+S1705+S1706 CONFIRMED** at S1706 close. Codification-ready-STRENGTHENED-EVEN-FURTHER for playbook v3 §15 (18-consecutive from 17-consecutive at S1705 close).

## What's next

Group 1700 arc reaches **7/8 = 87.5% complete** at S1706 close. Next session: **S1799 xx99 canonical summary** — the LAST session under Group 1700 arc.

Per playbook §11.3 12-section canonical summary template + §11.3 §10 meta-methodology template FIFTH application (after S1399 first + S1499 second + S1599 third + S1699 fourth):

- **§5 six-axis (or fewer, per Cat F evidence) posture-decision evidence brief** for D74 structural-separability vs canonical-unification, consuming F9 axis matrix now complete with six cells (A DEEP-WIRED, B DEEP-WIRED-BUT-DEDUP-UNRESOLVED, C COVERAGE-GAP-ON-PA-PATH, D ACTIVELY-BROKEN, E LATENT-VIABLE-BUT-FLAG-GATED, F RETENTION-PATTERN-INCONSISTENT).
- **§7 anchor-update tranche** — CLAUDE.md `Live Counts` autoblock body-systems 9 → 10 (F2 drift); PLATFORM_INVENTORY.md line 24 body-systems 9 → 10 (F2); parent §5.F + start-here L89 check_learning_loop_slo line-cite 12492 → 13170 (F3); CLAUDE.md/PLATFORM_INVENTORY 3-vs-4 employees drift (S1705 F3 owed); parent §5.E scope clarification (S1705 D3); parent §5.F "six sub-slots" wording vs 5-actual (S1706 R10).
- **§8 T0/Gate + T1 unified follow-on queue** — R1 F1 retention posture ADR spanning all six Cats (Cat F R1 unified across A-F); R2 D74 axis posture; R.RIGBY_DELEGATION-flag (S1705 R2); R.evidence_for_mission-repair (S1705 R3); R.tool_call_id-schema (S1704 R4); R.PA-path-AgentExecution (S1703 R1); R.LLM-multi-model-dedup (S1702 R2).
- **§10 fifth-application meta-methodology** confirms F.i/F.ii/F.iii durable at five-consecutive-application (playbook v3 §11.3 §10 template promoted at S1399 close).
- **Rigby SIGN cycle 1 required** per playbook §15 stage-table `canonical_summary` row.
- **Group 1700 arc-close after S1799 xx99 close** — arc pin `pa-e7fbacc996b34b44` retire owed at S1799 close per playbook §16.

**Session flow at next-session open:**

1. `context-kit orient` (session-open protocol per memory rule).
2. Check if S1706 artifact set merged to `main` (audit doc + INDEX v49 + OPEN_ARCS + handoff + start-here).
3. If not yet merged: Chris merge + PR merge.
4. Run post-merge 4-step docs cascade + `build_docs_provenance` per memory rule `feedback_docs_cascade_at_every_close.md`.
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-e7fbacc996b34b44` (D48 24th arm start; anticipated CLEAN per S1503+…+S1706 sub-pattern).
6. Mint fresh SIGN isolation pin for S1799 via Rigby `session_tool.create_fresh` (title: "Session 1799 — Group 1700 Observability canonical summary — SIGN isolation").
7. Draft S1799 xx99 per playbook §11.3 12-section canonical summary + §10 meta-methodology template FIFTH application.
8. Consume all six children S1701-S1706 §1.1 F1-F9 findings + §19 R-slots + §17 duplicate/overlapping systems + §14 drift matrices + §16 boundary violations catalogs.
9. Rigby SIGN cycle 1 (may exceed single-batch 4-question given xx99 scale — see playbook §15 canonical_summary row for full-SIGN discipline).
10. Land Rigby folds pre-commit.
11. Retire SIGN isolation pin at S1799 close per §16.
12. **Retire arc pin `pa-e7fbacc996b34b44` at S1799 close** per playbook §16 arc-close discipline (mirrors S1699 Group 1600 arc pin `pa-f52acf3f8d394faa` retire precedent).
13. Update ARCHITECTURE_INDEX v49 → v50 with §1.53 S1799 registration + §8 timeline S1799 row + line-6 v50 preamble.
14. Update OPEN_ARCS Group 1700 row: MOVE from In-progress → Closed section.
15. Write S1799 handoff + overwrite `00-START-NEXT-SESSION.md` to point at Group 2000 (or next §22 queue lean) as next-session priority.

**Not next (unless Chris specifies):** any specific implementation work per playbook §14.5 no-implementation rule. Retention purge tasks + SLO framework design + terminology renames + verifier observability integration + HeartBeat export activation are all post-arc T-slot per parent §6.

## Post-arc queued items (Chris-gated, inherited from prior arcs + additions from S1706)

- **From S1706 §19:** R1 (HIGH) F1 retention posture (spans Cats A-F via consolidation); R2 (HIGH) F9 D74 axis posture; R3 (MED) F5 SLO framework scope; R4 (MED) F6 doc-verifier integration; R5 (MED) F8 terminology ratification; R6 (MED) F2 body-system inventory refresh; R7 (LOW) F4 ABTestEvent orphan; R8 (LOW non-blocking) F7 HeartBeat export UI; R9 (LOW non-blocking) F7 cold-start SPECULATIVE verification; R10 (LOW) F3 line-cite refresh.
- **From S1706 §14:** D1 (10-vs-9 body systems) + D2 (`check_learning_loop_slo` line drift) + D3 (F7 cold-start SPECULATIVE) — all owed to xx99 §7 anchor-update tranche.
- **From S1705 §19:** R1-R12 (Cat E-specific; consolidated with Cat F R1 for retention).
- **From S1704 §19:** R1-R12 (Cat D-specific; F1 CRITICAL trace_id repair still gating any Option B posture evaluation).
- **From S1703 §19:** R1-R10 (Cat C-specific; F4 PA path AgentExecution coverage still HIGH).
- **From S1702 §19:** R1-R10 (Cat B-specific; multi-model dedup posture unresolved).
- **From S1701 §19:** R1-R8 (Cat A-specific; task_id ↔ execution_id spine posture is xx99 scope).
- **From S1701-S1705 §14:** D1-D9 owed to xx99 anchor-update PR.
- **From S1701 §20.5:** `tools/pa_local.sh` wrapper enhancement to support per-child SIGN pin routing (nice-to-have; not blocking).
- **From Group 1600 (S1699):** T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E; T1 (20 items); T3 CROSS-DOMAIN-EMPLOYEE-ANALOG; cross-arc: Group 1500 T1.h SportsBettingBrief consumer-or-remove + Group 1400 R.B1 OutreachDraft delivery.
- **From Group 1500 (S1599):** T1 R.SPORTS.POSTURE + R.DBAO.CODENAME Chris-gated ADRs; T1 CRITICAL remediation sequences.
- **From Group 1400 (S1499):** T1-T10 unified follow-on queue tier structure (still pending).
- **From Group 1300 (S1399):** 21 follow-on items (still pending).
- **§8 timeline table drift** — missing rows for S1605 Cat E + S1606 Cat F + S1699 xx99 (all Group 1600); owed to follow-up docs PR.
- **5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.

## Reference — where to look

- **S1706 Cat F audit doc:** `docs/research/domains/observability/1706_observability_cat_f_adjacent_separation_boundaries_audit.md` — playbook §11.2 20-section template SIXTH application under Group 1700; §1.1 F1-F9 lock-in table; §4.1 HeartBeat 10-field schema; §4.2 14-model WRITE-ONLY-FORGOTTEN matrix; §5-§7 canonical entry points + services + runtime flows; §8 retention posture comparison table (F1 peer contrast); §9.1 D74 axis matrix with sixth cell; §14 D1-D3 drift catalog; §15 D1-D6 debt matrix; §16 5 LEGITIMATE + §16.1 PERMEABLE-boundary recommendation + terminology stability grid; §17 duplicate/overlap analysis with F4 verifier-loop corrections; §19 R1-R10 follow-on queue; §20.6 Rigby SIGN cycle 1 F1-F4 fold notes.
- **S1705 Cat E audit doc:** `docs/research/domains/observability/1705_observability_cat_e_ops_run_event_audit.md`.
- **S1704 Cat D audit doc:** `docs/research/domains/observability/1704_observability_cat_d_tool_call_record_audit.md`.
- **S1703 Cat C audit doc:** `docs/research/domains/observability/1703_observability_cat_c_agent_execution_audit.md`.
- **S1702 Cat B audit doc:** `docs/research/domains/observability/1702_observability_cat_b_llm_call_event_audit.md`.
- **S1701 Cat A audit doc:** `docs/research/domains/observability/1701_observability_cat_a_celery_task_event_audit.md`.
- **S1700 parent scoping doc:** `docs/research/domains/observability/1700_observability_domain_scoping.md`.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.1 parent template + §11.2 child template + §11.3 canonical summary template + §11.3 §10 meta-methodology template + §22 default queue lean).
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` (§8.1 RESEARCH contract + §12.3 "Start Group NNNN" target).
- **ARCHITECTURE_INDEX v49:** `docs/research/ARCHITECTURE_INDEX.md` — S1706 §1.52 + line-6 v49 preamble + §8 timeline S1706 row.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1700 In-progress row current-child S1706; row prepared for imminent transition to Awaiting summary at S1799 xx99 close.
- **Cross-domain refresh:** `docs/research/platform/cross_domain_integration_audit.md` §14 (line 1977+) — §14.8 reserved for Group 1700 xx99 close consumption at S1799.
