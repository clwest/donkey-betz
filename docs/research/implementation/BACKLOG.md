---
title: "Implementation Backlog — IOS Part 11 intake register"
status: active
authority: implementation-intake
session_added: 2700
generated: 2026-07-06
schema_version: IOS v1.1 §2.2 (5-prefix intake_id scheme)
current_ratification: docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md
current_ratification_scope: tier-band level (Chris ratified 6 tier bands + Arc I-0100 first-arc identity + T0 individual-gate posture 2026-07-06; per-row leaf detail carries chris_gate=RATIFIED at band level and MAY revert to PENDING on Stage 1 re-classification per IOS §11.3 reversibility)
partial_discharge_debt: IDBT-0001 HIGH (deep-late xx99 §8 leaf rows unenumerated at v0-partial snapshot — see docs/research/implementation/IMPLEMENTATION_DEBT.md)
---

# Implementation Backlog

This is the **living** intake register for IOS-governed implementation work. It is grep-friendly — rows can be filtered by `status`, `affected_domain`, `risk_class`, `blast_radius`, `chris_gate`, or `arc_ref` without a human synthesizing. See IOS `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` §2.2 for the full schema definition (v1.1).

## Ratification history

| Date | Snapshot | Scope | Record |
|------|----------|-------|--------|
| 2026-07-06 | v0-partial (first queue) | Tier bands + Arc I-0100 first-arc identity + T0 individual-gate posture | [RATIFICATION_2026-07-06_first_queue.md](RATIFICATION_2026-07-06_first_queue.md) |

## Arc-open history

| Date | Arc | Stage-at-open | Intake rows flipped `IN_ARC` | Scoping doc |
|------|-----|--------------|------------------------------|-------------|
| 2026-07-06 | **I-0100** — Observability Correlation Spine + Mission Evidence Substrate | Stage 1 exit-gate cleared (Rigby SIGN Cycle 1 SIGN-with-edits + 8 folds ratified via Chris "agree all F1-F8") | `IB-1799-T1-01`, `IB-1799-T1-02`, `IB-1799-T1-03` (3 T1 rows). Also admitted (BACKLOG flip deferred to Stage 2): `IB-1799-T0-01` architecture-only ADR-C track per F1 fold; `IB-1799-T0-02` conditional as required decision INPUT to ADR-C per F2 fold. Also bundled as in-arc P0 prep PR per IOS v1.2 §4.3 ADR corpus precondition Option (a): `IB-Q1-BOOT-01` (BACKLOG flip pending P0 open). | [observability_spine_mission_evidence_substrate/I-0100_scoping.md](observability_spine_mission_evidence_substrate/I-0100_scoping.md) |
| 2026-07-06 | **I-0100** — P0 prep PR opened (in-arc IB-Q1-BOOT-01 discharge) | Stage 1 → Stage 2 transition: ADR corpus precondition being satisfied | `IB-Q1-BOOT-01` flipped `TRIAGED → IN_ARC`; final flip to `SHIPPED` at P0 prep PR merge. New rows added: `IDBT-0002` (RAG-owned embedding invalidation gap; delegated to Group 2100 RAG). | (P0 prep PR opens; `docs/adr/` + `ADR-0001-establish-adr-corpus.md` in tree) |
| 2026-07-06 | **I-0100** — **Stage 2 opened** (auto-open per IOS §4.3 Stage 2 Entry gate v1.4 Option (a) clause) | Stage 1 → Stage 2: ADR corpus precondition SATISFIED; scoping frontmatter `stage: 1 → 2, stage_state: p0-prep-merged → active` | `IB-Q1-BOOT-01` flipped `IN_ARC → SHIPPED` with `pr_refs: #2948` and `adr_ref: ADR-0001` per IOS §2.2 v1.4 Discipline B inline syntax. Preceded by PR #2947 (v1.3 cascade discipline) + #2948 (P0 prep) + #2949 (v1.4 Stage 2 readiness B1-B6) all merged 2026-07-06. Next: ADR-B (`ADR-0002 pa-write-shape-and-correlation-contract`) authoring per F4 fold ratifies-first ordering. | (Stage 2 opened; scoping doc frontmatter reflects `stage: 2, stage_state: active`) |
| 2026-07-06 | **I-0100** — ADR-B ratified (Stage 2 first ADR) | Stage 2 remains active | ADR-0002 (`pa-write-shape-and-correlation-contract`) accepted 2026-07-06 via Chris agree-all-F1-F8. IB-1799-T1-02 `design_state: POSTURE_PENDING → RATIFIED_ADR` with inline `adr_ref: ADR-0002`. PR #2951 merged. Standalone design-prep authored per Chris directive (canonical reference example under IOS v1.5 §4.3.a template). | (Stage 2 ADR-B ratified; ADR-A queued per F4) |
| 2026-07-06 | **I-0100** — IOS v1.5 design-prep first-class artifact shipped (PR #2952) | Stage 2 remains active | v1.5 replaces v1.4 §4.3 Stage 2 optional equivalence rule with mandatory standalone design-prep artifact. Two-trigger evidence: ADR-B consequences-per-option gap + ADR-A options-not-enumerated gap. §14.2.a Chris refinement-authority prerogative formalized. | (v1.5 in force; §4.3.a canonical template active) |
| 2026-07-06 | **I-0100** — ADR-A ratified (Stage 2 second ADR; first under IOS v1.5) | Stage 2 `stage_state: design-prep-in-flight → active` per §4.3.0 v1.5 flip | ADR-0003 (`mission-runner-staged-enable-posture`) accepted 2026-07-06 via Chris agree-all-F1-F8. IB-1799-T1-03 `design_state: POSTURE_PENDING → RATIFIED_ADR` with inline `adr_ref: ADR-0003`. Row description corrected per ADR-0003 §3.6: sole runtime gate is `RIGBY_DELEGATION_ENABLED`; `MISSION_RUNNER_ENABLED` retained as docs-only legacy alias per §2.1 F8 terminology binding. PR #2953 merged. Standalone design-prep authored — first live application of IOS v1.5 §4.3.a canonical template. | (Stage 2 F4 ordering complete except optional ADR-C; Stage 3 pre-flight ready to open for P2/P3/P4 runtime discharge) |
| 2026-07-06 | **I-0100** — P2 runtime SHIPPED (`ToolCallRecord.trace_id` write-side fix) | First runtime discharge PR of Arc I-0100 | IB-1799-T1-01 `status: IN_ARC → SHIPPED` with inline `pr_refs: #2954`. Feature flag `TOOL_CALL_TRACE_ID_ENFORCED` default OFF. Stage 5 verification 20/20 pass; ORM baseline confirmed 4265 NULL preserved under flag OFF; post-flag-ON provenance chain returns non-empty. Flag flip is Chris operator decision only — no pre-flag-flip work required. | (Arc I-0100 first runtime shipment) |
| 2026-07-06 | **I-0100** — P4 code-merged, flag-flip-blocked (PA per-turn `AgentExecution` write) | Second runtime PR of Arc I-0100; runtime dormant | IB-1799-T1-02 `status: IN_ARC` unchanged pending flag flip. `pr_refs: #2955` merged 2026-07-06 with default flag OFF. Migration 0377 creates canonical `PersonalAssistant` Agent row per ADR-0002 Sub-option 1(i). Runtime write path DORMANT until three STOP CONDITIONS discharge: (1) ~150-site AgentExecution consumer sweep; (2) early-return path finalization decision; (3) LLMCallEvent.execution_id end-to-end join verification. Row flips `IN_ARC → SHIPPED` only when Chris ratifies stop-condition discharge + directs flag flip. | (Arc I-0100 second runtime shipment; discharge deferred pending stop conditions) |
| 2026-07-06 | **I-0100** — P3 code-merged, flag-flip-blocked (delegation lifecycle Phase 1 smoke + Phase 2 spec) | Third runtime PR of Arc I-0100; runtime dormant | IB-1799-T1-03 `status: IN_ARC` unchanged pending flag flip. `pr_refs: #2957` merged 2026-07-06 with default flag OFF. All 6 §3.3.a assumption-lock gates PASS at Stage 3 pre-flight. Ships Phase 1 smoke command + Phase 2 auto-disable threshold spec + regression tests (9/9 pass). Baseline captured: OpsRunEvent 9.97/day → Phase 2 auto-disable threshold 14.9/day. Runtime path DORMANT until four STOP CONDITIONS discharge: (1) `MONITORING_SURFACE_INTEGRATED=True` integration; (2) Phase 2 evidence bundle Chris review; (3) A1-A6 re-verification at flag-flip time; (4) ratified §3.1 F1 entry gate. **Matches P4 code-merged-flag-flip-blocked pattern (2 of 4 triggers for future IOS v1.6 consideration per Chris four-trigger philosophy — memory-recorded).** Row flips `IN_ARC → SHIPPED` only when Chris ratifies stop-condition discharge + directs flag flip. | (Arc I-0100 third runtime shipment; discharge deferred pending stop conditions) |

## Tier band totals (as of 2026-07-06 ratification)

| Tier | v0-partial row count | Chris gate | Notes |
|------|---------------------|------------|-------|
| T0 / Gate | 32 (all enumerated below) | RATIFIED at band | Each T0 item requires individual Chris gate at Stage 2 entry (no SAFE_AUTONOMOUS T0 per 2026-07-06 ratification) |
| T1 CRITICAL/HIGH | 68 (35 enumerated below; ~33 in PARTIAL_DISCHARGE tail per IDBT-0001) | RATIFIED at band | Sequenced per T0 gate + §3.3 dependency scoring |
| T2 MEDIUM | 91 (representative summary below; leaf expansion during arc scoping) | RATIFIED at band | Design-prep follow-ons; posture-tied |
| T3 LOW-MEDIUM | ~180 (representative summary below; SAFE_AUTONOMOUS subset ~65) | RATIFIED at band | Bounded ops patches; standard PR gate |
| DEFER (BLOCKED_ON_RESEARCH) | 18 (all enumerated below) | RATIFIED as blocked | Routed to Research OS |
| Cross-arc initiatives | 5 (CX-P1 + CX-P3 + CX-P4 + CX-P6 + CX-P7/P8 — enumerated in §Cross-arc initiatives below) | RATIFIED existence + shape TBD | CX-P4 sequencing + CX-P7 shape deferred per 2026-07-06 ratification Axis 4 |

## Cascade-housekeeping exclusions (per IOS v1.1 §2.4)

Anchor-updates discharged by the 4-step docs cascade at every arc close, not by implementation intake. NOT included as backlog rows:

- 13× PLATFORM_INVENTORY.md refresh (one per closed xx99 arc; discharged by `refresh_doc_inventory_blocks` + docs cascade)
- 13× ARCHITECTURE_INDEX.md v-bump (one per closed xx99 arc; discharged at arc close)
- Various docs/topics/*.md count refreshes (discharged by docs cascade)
- docs/INDEX.md regeneration (autogen; discharged by `build_docs_index`)

Substantive anchor-update work not covered by cascade (new topic doc creation for new subsystems, structural inventory refactor) DOES admit as intake and appears in the T1/T3 rows below.

---

## T0 / Gate — Chris-gated meta-ADRs + IOS bootstrap infrastructure (32 rows)

**Columns:** `intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces`

### IOS bootstrap infrastructure

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-Q1-BOOT-01` | IOS §D3 + Appendix C | queue_construction | Author `ADR-0001-establish-adr-corpus.md` (recursive bootstrap ADR that installs the ADR corpus) | platform | NEEDS_ADR | RATIFIED_ADR | SHIPPED | RATIFIED (band) | `docs/adr/` (created 2026-07-06), `docs/adr/ADR-0001-establish-adr-corpus.md` (shipped 2026-07-06). `arc_ref: I-0100`; `adr_ref: ADR-0001` (accepted, ratified via §D3 Chris ratification 2026-07-06); `pr_refs: #2948` (P0 prep PR merged 2026-07-06 auto-opening Arc I-0100 Stage 2 per IOS §4.3 Stage 2 v1.4 Entry gate Option (a) clause). Row flipped `IN_ARC → SHIPPED` at housekeeping stage-transition PR per IOS §4.5 + §4.3.0 v1.4 discipline + §2.2 v1.4 Discipline B inline syntax. |
| `IB-Q1-BOOT-02` | IOS §D4 + §D6 + Appendix C | queue_construction | Create `docs/research/implementation/BACKLOG.md` + `IMPLEMENTATION_DEBT.md` living registers | platform | NEEDS_CHRIS_PRE_RATIFICATION | SPEC_COMPLETE | IN_ARC | RATIFIED (band) | this file, `docs/research/implementation/IMPLEMENTATION_DEBT.md` — **partially self-discharging via this seed PR** |
| `IB-Q1-BOOT-03` | IOS §D11 Wave 1 | queue_construction | Install `build-docs-cascade.yml` GitHub Action (fires on merge of any PR body citing `arc-close: I-NNNN99`) | platform | NEEDS_CHRIS_PRE_RATIFICATION | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `.github/workflows/build-docs-cascade.yml` (new file). BLOCKING for third implementation arc opening per D11. |

### Sports posture ADRs

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-1599-T0-01` | 1599 §8.1.a | xx99_followon_T0 | Ratify R.SPORTS.POSTURE (integration vs island) | sports | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, sports pipeline scope |
| `IB-1599-T0-02` | 1599 §8.1.b | xx99_followon_T0 | Ratify R.DBAO.CODENAME (materialize vs demote vs archive) | sports | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, DBAO artifact set |

### Content posture ADRs (D65 4-axis bundle — each axis is a separate T0)

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-1699-T0-01` | 1699 §8.2 D65a | xx99_followon_T0 | Ratify D65a Content lifecycle scoping ADR | content | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, content pipeline scope |
| `IB-1699-T0-02` | 1699 §8.2 D65b | xx99_followon_T0 | Ratify D65b Content correction-paths ADR (retract/errata/unpublish) | content | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, PublishGate + all publish surfaces |
| `IB-1699-T0-03` | 1699 §8.2 D65c | xx99_followon_T0 | Ratify D65c PublishGate composition ADR (SelfBlog-only → Deliverable+variant+rail) | content | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, PublishGate |
| `IB-1699-T0-04` | 1699 §8.2 D65e | xx99_followon_T0 | Ratify D65e Newsletter live-send posture ADR | content | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, Newsletter subsystem |

### Observability posture ADRs

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-1799-T0-01` | 1799 §5 D74 | xx99_followon_T0 | Ratify D74 six-axis observability correlation-spine posture | observability | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, event model schema across 14 Cat A–F |
| `IB-1799-T0-02` | 1799 §1 axis F | xx99_followon_T0 | Ratify unified retention policy across 14 event models (12/14 currently UNBOUNDED) | observability | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, 14 event models retention config |

### HumanAttention posture ADR

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-1899-T0-01` | 1899 §14.9 D80 | xx99_followon_T0 | Ratify D80 four-option HAI learning-surface posture | human_attention | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, HAI learning-surface + ownership |

### Authority Enforcement posture ADR

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-1999-T0-01` | 1999 §17.1 | xx99_followon_T0 | Ratify Authority Enforcement per-plane posture (5 PERMEABLE-BROKEN + 2 STRUCTURAL-DROP + 1 CLEAN) | authority_enforcement | NEEDS_ADR | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `docs/adr/`, per-plane register |

### Event/Integration posture ADR

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-2099-T0-01` | 2099 §5.1 | xx99_followon_T0 | Ratify 10-plane event/integration substrate landscape posture | event_integration | NEEDS_ADR | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `docs/adr/`, event bus + substrate register |

### RAG posture ADR

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-2199-T0-01` | 2199 §1 | xx99_followon_T0 | Ratify RAG corpus substrate maturity gradient (spec-complete/execution-pending) | rag,memory | NEEDS_ADR | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `docs/adr/`, RAG substrate |

### Frontend posture ADR

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-2299-T0-01` | 2299 §5.1 | xx99_followon_T0 | Ratify 4-axis Frontend contract-surface posture (canonical "declared-but-unenforced" seam) | frontend | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, frontend contract seam |

### Auth posture ADRs

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-2499-T0-01` | 2499 §1 | xx99_followon_T0 | Ratify 3-quadrant Auth + Cat D γ ⊃ Cat C β nesting posture | auth,api,frontend | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, auth 4-Cat + typed-error-envelope |
| `IB-2499-T0-02` | 2499 §3 | xx99_followon_T0 | Ratify typed-error-envelope α/β/γ decision (cross-transport SoT) | auth,api,frontend | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, typed error contract |

### API posture ADRs

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-2599-T0-01` | 2599 §1 | xx99_followon_T0 | Ratify 4-layered backend API surface topology (Cat A DECLARATION + Cat B CONSUMER + Cat C WIRE + Cat D PERMISSION-FLOOR+REST↔WS) | api,auth,frontend | NEEDS_ADR | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `docs/adr/`, API topology map |
| `IB-2599-T0-02` | 2599 §3.1 | xx99_followon_T0 | Ratify per-endpoint permission-floor governance (838/1856 = 49% decoration density; fragmentation signal) | api,auth | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, permission-floor registry |

### PA posture ADRs

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-2699-T0-01` | 2699 §11 | xx99_followon_T0 | Ratify PA 5-way Chris-D-verdict axes (Cat A/B/C1/C2/D with F5-analog HARD-INVALID for Path C-pure) | pa,api,auth,frontend | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, PA 4-plane spec |
| `IB-2699-T0-02` | 2699 §9.1a | xx99_followon_T0 | Ratify REST↔WS reconciliation-layer ownership (3 options i/ii/iii) | pa,api,observability | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, REST↔WS reconciliation |

### CX-P1 Runtime-owner assignments

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-CXP1-T0-01` | audit §14.6 CX-P1 | cx_pattern_P1 | Assign runtime owner (JobContract) to Revenue domain | revenue,employee_os | NEEDS_CHRIS_PRE_RATIFICATION | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `core/employees/jobs.py`, `core/models_jobs.py`, JobContract |
| `IB-CXP1-T0-02` | audit §14.6 CX-P1 | cx_pattern_P1 | Assign runtime owner to Sports domain | sports,employee_os | NEEDS_CHRIS_PRE_RATIFICATION | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `core/employees/jobs.py`, sports coordinator |
| `IB-CXP1-T0-03` | audit §14.6 CX-P1 (v4 fold 2026-07-05) | cx_pattern_P1 | Assign runtime owner to HumanAttention domain | human_attention,employee_os | NEEDS_CHRIS_PRE_RATIFICATION | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `core/employees/jobs.py`, HAI service |

### CX-P8 Silent-degrade codification

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-CXP8-T0-01` | audit §14.6 CX-P8 (2499 §10.2 two-trigger threshold met: Cat C 92.9% + Cat D 89.5%) | cx_pattern_P8 | Codify auth failure-handling (401/403/refresh/logout) UX + telemetry as IOS §5.2 rule 7 scope-bounded promotion | auth,api,frontend | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | IOS §5.2 rule 7, auth-facing UX contract |

### Revenue-specific T0 (source-of-truth + write-authority)

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-1499-T0-01` | 1499 §8.3.T1 | xx99_followon_T0 | Ratify Revenue source-of-truth hierarchy ADR (CX-P6 parallel-schema across `Revenue`/`RevenueRecord`/`Opportunity`/intelligence-engine planes) | revenue | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, `core/models_revenue.py`, `core/intelligence/*` |
| `IB-1499-T0-02` | 1499 §8.3.T7 | xx99_followon_T0 | Ratify Revenue write-authority + routing-authority framework ADR (F2 orphan-write pattern; 20-writer convergence on Opportunity) | revenue,authority_enforcement | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, `core/services/revenue_attribution_bridge.py`, `core/models_revenue.py` |

---

## T1 CRITICAL/HIGH — Post-arc ADRs + runtime unblockers (68 total; 35 enumerated below; ~33 in PARTIAL_DISCHARGE tail per IDBT-0001)

### Arc I-0100 seed rows (Observability Spine — FIRST ARC per 2026-07-06 ratification)

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-1799-T1-01` | 1799 §1 axis D + S1704 F1 | xx99_followon_T1 | Fix `ToolCallRecord.trace_id` 100% NULL at write-side (blocks cross-cat consumer join) | observability | NEEDS_RIGBY_SIGN_PLUS_CHRIS | SPEC_COMPLETE | SHIPPED (I-0100) | RATIFIED (band) | `core/services/tool_dispatcher.py:960`, `core/models_tool_calls.py` `ToolCallRecord.record()` classmethod (used by `core/agents/base_agent.py:3408`), `core/services/unified_pa_entrypoint.py` (deprecated writer). `pr_refs: #2954` merged 2026-07-06. Feature flag `TOOL_CALL_TRACE_ID_ENFORCED` default OFF; Chris directive to flip. Runtime SHIPPED — no pre-flag-flip work required; flip is operator decision only. Stage 5 verification complete (14/14 tests + 6/6 provenance + 4/4 ORM shell checks; baseline 4265 NULL → post-flag-ON provenance chain returns non-empty). Scoping doc: §3.1 + §5 P2. Rollout per F8-i dual-format acceptance. |
| `IB-1799-T1-02` | 1799 §1 axis C + S1703 F1 | xx99_followon_T1 | Wire PA-invoked agents → `AgentExecution` writes (PA tool dispatch currently bypasses `dispatch_agent` code path); ADR-B specifies PA↔LLMCallEvent correlation contract per F5 fold | observability,pa,agents | NEEDS_ADR | RATIFIED_ADR | LOCAL_ACCEPTED (I-0100 closed 2026-07-07) — code-merged; all 3 stop conditions locally discharged; PRODUCTION_DEFERRED per PR #2973 acceptance | RATIFIED (band) | `core/services/unified_pa_entrypoint.py` (write helpers + create/finalize insertions), `core/migrations/0377_arc_i0100_p4_canonical_pa_agent.py` (canonical PA Agent row per Sub-option 1(i)), `core/settings.py` (flag definition), `core/tests/test_pa_agent_execution_write.py` (10 tests). `pr_refs: #2955` merged 2026-07-06 + **#2970** async-write fix (`sync_to_async` hop; 3 `AsyncContextRegressionTests`) merged 2026-07-07. `adr_ref: ADR-0002`. Feature flag `PA_AGENT_EXECUTION_WRITE_ENABLED` default OFF (unchanged). **Terminal disposition:** LOCAL_ACCEPTED / PRODUCTION_DEFERRED under LOCAL-only operating model (PR #2972). All 3 stop conditions locally discharged: (1) ~150-site `AgentExecution` consumer sweep — PR #2967; (2) early-return finalize (Option A) — PR #2968; (3) `LLMCallEvent.execution_id` end-to-end join — PR #2969 + verified in local canary post-#2970. Acceptance package: `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_p4_local_activation_acceptance.md` (PR #2973). Arc close: `I-010099_observability_spine_implementation_close.md` (PR #2976). Row does NOT flip to SHIPPED until a production deployment exists AND Chris directs prod flag flip; that opens a follow-on arc, not a reopen of I-0100. Scoping doc: §3.1 + §5 P4. |
| `IB-1799-T1-03` | 1799 §1 axis E + S1705 F1 | xx99_followon_T1 | Discharge R3 delegation-handler dormancy via staged unlock of `RIGBY_DELEGATION_ENABLED` (sole runtime gate per ADR-0003 §2.1 terminology binding; `MISSION_RUNNER_ENABLED` is docs-only legacy slug — NO CODE reference) — Phase 1 shadow-audit-synthetic (`manage.py delegation_lifecycle_smoke_test`) + Phase 2 direct full-enable per ADR-0003 §3.1 Option 5 hybrid | observability,employee_os | NEEDS_ADR | RATIFIED_ADR | LOCAL_ACCEPTED (I-0100 closed 2026-07-07) — code-merged; all 4 stop conditions locally discharged; PRODUCTION_DEFERRED per PR #2975 acceptance | RATIFIED (band) | `core/signals/rigby_delegation_signals.py` (handler; R3 dormancy target — kill-switch guard added PR #2974), `core/services/rigby_mission_delegation.py` (`delegate_work_item` — kill-switch guard added PR #2974), `core/settings.py:138-140` (RIGBY_DELEGATION_ENABLED flag), `core/management/commands/delegation_lifecycle_smoke_test.py`, `core/services/delegation_auto_disable.py` (`MONITORING_SURFACE_INTEGRATED=True` per PR #2974), `core/services/delegation_auto_disable_monitor.py` (new PR #2974: `check_thresholds` / `trip` / `is_tripped` / `clear_trip`), `core/management/commands/delegation_auto_disable_check.py` (new PR #2974), `core/tests/test_delegation_lifecycle_smoke_test.py`, `core/tests/test_delegation_auto_disable_monitor.py` (new PR #2974: 21 tests). `pr_refs: #2957` merged 2026-07-06 + **#2974** SC#1 discharge merged 2026-07-07. `adr_ref: ADR-0003`. Feature flag `RIGBY_DELEGATION_ENABLED` default OFF (unchanged). **Terminal disposition:** LOCAL_ACCEPTED / PRODUCTION_DEFERRED under LOCAL-only operating model (PR #2972). All 4 stop conditions locally discharged: (1) monitoring surface integration `MONITORING_SURFACE_INTEGRATED=True` — PR #2974 (cache-key kill sentinel via `django.core.cache`; delegation entry point + lifecycle signal short-circuit on `is_tripped()`); (2) Phase 2 evidence bundle — smoke test PASS (12/12 checks, verdict `verified`, zero unhandled exceptions, savepoint cleanup); (3) A1-A6 re-verification — A1/A2/A4/A5 VERIFIED, A3/A6 CHANGED SINCE RATIFICATION and accepted by Chris as non-blocking for LOCAL (A3 = additive kill-switch guard from PR #2974; A6 = 30-day +5.3% drift, last-24h above threshold, recalibration deferred until future flag-flip prep); (4) §3.1 F1 entry gate — ratified by Chris via merge of PR #2975. Acceptance package: `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_p3_local_activation_acceptance.md` (PR #2975). Arc close: `I-010099_observability_spine_implementation_close.md` (PR #2976). Row does NOT flip to SHIPPED until a production deployment exists AND Chris directs prod flag flip; that opens a follow-on arc, not a reopen of I-0100. Naming correction per ADR-0003 §3.6 applied — single-flag scope. |

### Memory T1 leaf rows

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-1399-T1-01` | 1399 §8.2.5 | xx99_followon_T1 | Design AgentMemory.create_memory write-authority framework (user FK + rate-limit + audit) | memory,authority_enforcement | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `core/services/agent_memory_service.py`, `core/models_memory.py` |
| `IB-1399-T1-02` | 1399 §8.2.1 | xx99_followon_T1 | Recheck `ingested_via` orphan claim (full-tree consumer verification per §2.4 F4-CANDIDATE discipline) | memory,rag | NEEDS_RIGBY_SIGN_PLUS_CHRIS | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `core/models_memory.py`, `core/services/document_ingestion_service.py` |

### Revenue T1 leaf rows

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-1499-T1-01` | 1499 §8.3.T5 + audit §14.3 F.B1 + CX-P3 | xx99_followon_T1 | Author outreach delivery + engagement ingestion ADR pair (CX-P3 ZERO outbound; SendGrid vs Postmark vs SES vs LinkedIn vs Rigby-DM) | revenue,inbox | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `core/models_outreach.py`, `docs/adr/` |
| `IB-1499-T1-02` | 1499 §8.3.T8 | xx99_followon_T1 | Author Revenue state-machine ADR (16 declared vs 6 reachable states across 4 models) | revenue | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, `core/models_revenue.py`, state machines |
| `IB-1499-T1-03` | 1499 §8.3.T6 | xx99_followon_T1 | Author HAI interlock ADR (Meeting/ClosePack approval routing) | revenue,human_attention,authority_enforcement | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `docs/adr/`, HAI + revenue approval gate |

### Sports T1 leaf rows

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-1599-T1-01` | 1599 §8.1.d | xx99_followon_T1 | Concurrency-safety harden `_settle_wager` pre-beat restoration (select_for_update + transaction.atomic) | sports | NEEDS_RIGBY_SIGN_PLUS_CHRIS | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `core/services/wager_settlement_service.py` |
| `IB-1599-T1-02` | 1599 §8.1.f | xx99_followon_T1 | Idempotency harden `daily_betting_digest` pre-restore | sports | NEEDS_RIGBY_SIGN_PLUS_CHRIS | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `core/tasks_sports.py` daily_betting_digest |
| `IB-1599-T1-03` | 1599 §8.1.c + §8.1.e | xx99_followon_T1 | Restore verify_betting_outcomes beat + daily_betting_digest beat (gated on T1-01/T1-02 idempotency + concurrency work) | sports | NEEDS_CHRIS_PRE_RATIFICATION | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `core/celery.py` beat schedule, django-celery-beat rows |
| `IB-1599-T1-04` | audit §14.4 P11 + 1599 §4 | xx99_followon_T1 | Extend `SignalCluster.data_type` enum with `sports_odds` OR build sports-native aggregator | sports,signal_engine | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `core/models_signals.py` SignalCluster.data_type |

### Content T1 leaf rows (post-D65 ratifications)

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-1699-T1-01` | 1699 §8.2 T1 (D65b post-ratify) | xx99_followon_T1 | Implement Content correction-paths infrastructure (retract/errata/unpublish across all publish surfaces) | content | NEEDS_ADR (blocked on `IB-1699-T0-02`) | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | PublishGate + Newsletter + SelfBlog + Deliverable + variant |
| `IB-1699-T1-02` | 1699 §8.2 T1 (post-D65e) | xx99_followon_T1 | Implement Newsletter live-send infrastructure (currently dry_run parked >4mo) | content | NEEDS_ADR (blocked on `IB-1699-T0-04`) | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | Newsletter subsystem + delivery provider |
| `IB-1699-T1-03` | 1699 §8.2 T1 (post-D65c) | xx99_followon_T1 | Extend PublishGate composition (SelfBlog-only → Deliverable+variant+rail) | content | NEEDS_ADR (blocked on `IB-1699-T0-03`) | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | PublishGate composition logic |

### Authority Enforcement T1 leaf rows

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-1999-T1-01` | 1999 §14.3 P4 F5 + CX-P10 | xx99_followon_T1 | Implement `enforce_authority_mode` field toggle (ABSENT at HEAD; blocks enforcement dispatch) | authority_enforcement | NEEDS_ADR (blocked on `IB-1999-T0-01`) | SPEC_COMPLETE | BLOCKED_ON_RESEARCH | RATIFIED (band) | `core/models_jobs.py`, `core/employees/mission_runner.py` |
| `IB-1999-T1-02` | 1999 §1 + P3 §7.4.1 | xx99_followon_T1 | Wire KillSwitch dispatch enforcement across 4 REQUIRED insertion boundaries (2 tool_dispatcher + 3 PA gateway + 6 mission_runner pre-dispatch + 18 fleet_dispatch) | authority_enforcement,governance,pa | NEEDS_ADR | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `core/services/tool_dispatcher.py`, `core/services/pa_gateway.py`, `core/employees/mission_runner.py`, fleet dispatch |
| `IB-1999-T1-03` | 1999 T1 R.CONTENT.PUBLISHGATE-AUTHORITY-COMPOSITION | xx99_followon_T1 | Establish authority constraint at PublishGate composition | authority_enforcement,content | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `core/pipelines/content_pipeline.py`, PublishGate |

### HAI T1 leaf rows

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-1899-T1-01` | 1899 §1 F7 CRITICAL | xx99_followon_T1 | Resolve FeedbackProcessor → AgentLearning update-gap (post_save does NOT invoke update_learned_stats) | human_attention,memory,agents | NEEDS_RIGBY_SIGN_PLUS_CHRIS | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `core/services/feedback_processor.py`, `core/services/learning_engine.py` |
| `IB-1899-T1-02` | 1899 §14 F3 HIGH IMMEDIATE | xx99_followon_T1 | Fix silent BoardroomLearningService + UnifiedLearningPipeline import collisions (2 duplicate-file class-name pairs) | human_attention,memory | NEEDS_RIGBY_SIGN_PLUS_CHRIS | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `core/models_learning.py`, `core/services/*learning*.py` duplicates |

### Event/Integration T1 leaf rows

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-2099-T1-01` | 2099 §1 T1 (F5 highest priority) | xx99_followon_T1 | Emit HAI dual-wiring event paths (critical for autonomic escalation) | event_integration,human_attention | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `core/services/event_bus.py`, HAI escalation contract |
| `IB-2099-T1-02` | 2099 §1 T1 | xx99_followon_T1 | Wire per-user-authority emission across event contract (three-event contract) | event_integration,authority_enforcement | NEEDS_ADR | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `core/services/event_bus.py`, authority event schema |

### RAG T1 leaf row

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-2199-T1-01` | 2199 §1 (spec-complete/execution-pending) | xx99_followon_T1 | Implement retrieval-authority framework governance (spec-complete; execution pending) | rag,memory,authority_enforcement | NEEDS_ADR | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `core/services/rag_service.py`, retrieval-authority framework |

### Frontend T1 leaf row

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-2299-T1-01` | 2299 §8.2 (T1 handoff to Group 2400) | xx99_followon_T1 | Wire silent-401 + logout cleanup contract with Auth (four-axis T1 handoff bundle) | frontend,auth | NEEDS_ADR (blocked on `IB-2499-T0-*`) | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | frontend auth interceptor + logout flow |

### Auth T1 leaf rows

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-2499-T1-01` | 2499 §16 F-D-SIDEBAR-1 HIGH | xx99_followon_T1 | Fix F-D-SIDEBAR-1 backend-token-revoke via PA logout (Sidebar.tsx:356 clears authStore but does NOT invoke authApi.logout(); backend token never revoked) | auth,pa,frontend | NEEDS_RIGBY_SIGN_PLUS_CHRIS | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `frontend/src/components/layout/Sidebar.tsx:356`, `frontend/src/api/authApi.ts` |
| `IB-2499-T1-02` | 2499 §14 F-D-PA-1 (escalated MED→HIGH) | xx99_followon_T1 | Fix F-D-PA-1 PA-chat 401 silent-swallow escalation (`/pa/chat/` not in whitelist; 401 mid-conversation = silent reject) | auth,pa | NEEDS_RIGBY_SIGN_PLUS_CHRIS | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `core/views_pa.py`, auth whitelist config |
| `IB-2499-T1-03` | 2499 Cat A F-C-VIP-1 | xx99_followon_T1 | Enforce `VIPInvite.account_expires_at` at runtime (declared but NEVER checked; fictional claim) | auth | NEEDS_CHRIS_PRE_RATIFICATION | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | `core/models_auth.py` VIPInvite, VIP auth check path |

### API T1 leaf rows

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-2599-T1-01` | 2599 §4.2 | xx99_followon_T1 | Implement 4-shape 401 heterogeneity end-to-end remediation (Cat A → Cat B SHAPE-BLIND → 803-scale consumer) | api,auth,frontend | NEEDS_ADR (blocked on `IB-2499-T0-02` + `IB-2599-T0-01`) | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | `core/auth_middleware.py`, typed-error-envelope contract |
| `IB-2599-T1-02` | 2599 §3 + 2699 §9.1 | xx99_followon_T1 | Wire REST↔WS T7 joint envelope conformance (0/40 baseline) | api,pa | NEEDS_ADR (blocked on `IB-2699-T0-02`) | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | `core/consumers/pa_consumers.py`, WS envelope contract |

### PA T1 leaf rows

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-2699-T1-01` | 2699 §9.1 (F-S2699-Q4-3 telemetry-scoped) | xx99_followon_T1 | Envelope-shape telemetry emit-signature (Cat D §10.4 AC-D8 canonical candidates: `pa.ws.envelope.conformance.grade` + `pa.ws.unauthorized_connect.count` + `pa.ws.emit.latency_histogram` + `pa.ws.agent_completed.reconciliation_delta`) | pa,observability | NEEDS_RIGBY_SIGN_PLUS_CHRIS | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `core/services/observability_service.py`, WS envelope telemetry |
| `IB-2699-T1-02` | 2699 CF-C4 + DEBT-C2-8 | xx99_followon_T1 | Wire `MobilePushToken.revoked_at` at PA logout (cascades to mobile) | pa,mobile,auth | NEEDS_RIGBY_SIGN_PLUS_CHRIS | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `core/agents/pa_subsystem.py`, `core/models_mobile.py` |
| `IB-2699-T1-03` | 2699 §4.5 F-D2 boundary gap | xx99_followon_T1 | Establish PA ↔ Fleet-Federation identity workspace conveyance (FleetSignatureAuth carries no workspace_id) | pa,fleet_federation,auth | NEEDS_RIGBY_SIGN_PLUS_CHRIS | POSTURE_PENDING | TRIAGED | RATIFIED (band) | `core/auth/fleet_auth.py`, PA workspace-context resolver |

### CX-P10 runtime-binding leaf rows

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-CXP10-T1-01` | audit §14.6 CX-P10 (1999 §1) | cx_pattern_P10 | Wire Authority Enforcement runtime binding (post-1999 spec-complete) — sequences after `IB-1999-T0-01` + `IB-1999-T1-01` | authority_enforcement | NEEDS_CHRIS_PRE_RATIFICATION | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | Authority enforcement plane |
| `IB-CXP10-T1-02` | audit §14.6 CX-P10 (2099 §1) | cx_pattern_P10 | Wire Event/Integration architecture runtime (post-2099 spec-complete) | event_integration | NEEDS_CHRIS_PRE_RATIFICATION | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | Event bus + substrate execution |
| `IB-CXP10-T1-03` | audit §14.6 CX-P10 (2199 §1) | cx_pattern_P10 | Wire RAG design-complete runtime scaffold | rag | NEEDS_CHRIS_PRE_RATIFICATION | SPEC_COMPLETE | TRIAGED | RATIFIED (band) | RAG substrate execution |

### T1 PARTIAL_DISCHARGE tail — ~33 additional T1 leaf rows unenumerated at v0-partial snapshot

Tracked as `IDBT-0001` PARTIAL_DISCHARGE HIGH. Discharge either by:
1. Third dedicated extraction pass on 1699/1799/1899/1999/2099/2199/2299/2499/2599/2699 §8 T1 leaf detail, appending discovered rows here with `chris_gate: RATIFIED` at band level. OR
2. Arc-scoped incremental discharge during each arc's Stage 1 scoping (Arc I-0100 Observability Spine Stage 1 re-extracts 1799 §8 in full before Stage 2 opens).

Known un-enumerated T1 clusters (indicative, not exhaustive): auth Cat A/B/C/D CX-P7 per-surface enforcement rollout; 4-shape SHAPE-BLIND consumer pipeline SoT selection; Frontend contract-SoT drf-spectacular platform-wide rollout; observability retention 12/14 unbounded per-model policy application; HAI enable `record_verification` learning-loop event emission; Body Coordinator → Governance autonomic emissions; Body HeartBeat → HAI degradation escalation; failure-cluster aggregator → HAI escalation.

---

## T2 MEDIUM — Design-prep follow-ons; posture-tied (91 total; representative summary)

Representative items ratified at band level. Full leaf expansion during first arc's Stage 1 or via dedicated re-extraction (IDBT-0001):

- **Employee OS JobContracts** (Revenue, Income/Jobs, HumanAttention post-`IB-CXP1-T0-*`)
- **Cat H memory remediation designs** (worker-restart vs file-watcher vs TTL)
- **RAG workspace-scoping** (Content §14.5 flagged CRITICAL)
- **Sports Learning Bridge extension** (2/4 → 4/4 market agents + AgentKnowledgeSource)
- **Sports entity identity reconciler** (TheOdds vs Kalshi vs Game namespace)
- **Content pipeline degradation contract** (3 silent try/except in ClaimsPackBuilder)
- **PA envelope conformance measurement per Consumer** (4 Consumers at HEAD)
- **Auth-layer CX-P7 enforcement per-surface rollout** (VIPInvite, DRF permission inheritance, FleetSignatureAuth)
- **Frontend CX-P7 enforcement per-surface rollout** (drf-spectacular, Zustand persist 3-of-7, error boundaries 0-of-40)
- **Observability retention per-model policy application** (12/14 UNBOUNDED)
- **Consolidated 6 event substrates governance execution** (post-`IB-2099-T0-01`)

**PARTIAL_DISCHARGE:** Full T2 leaf enumeration deferred to arc-scoped Stage 1 work. Tracked as part of IDBT-0001.

---

## T3 LOW-MEDIUM — Bounded ops patches (~180 total; SAFE_AUTONOMOUS subset ~65)

Representative SAFE_AUTONOMOUS items (ship without Chris ratification per IOS §3.1 SAFE_AUTONOMOUS carve-out):

- Revenue frontend routes correction (4 non-existent routes)
- Revenue 5 phantom-field sites fix (`recorded_at`, `actual_outcome`, `notes`, `metadata`)
- Revenue Celery routing dedupe (`score_opportunities_from_spider_data`)
- MeetingCoordinatorAgent removal from Cat D
- Sports mock data removal (`/ws/dbao/`, `/ws/dbao-dashboard/`)
- Sports `sports_intelligence` flag enforcement OR removal (DECLARED-GATES-NOTHING)
- Sports Discord command re-routing through SportsBettingCoordinator
- Sports Freelance/Gig runtime FieldError fix
- `AgentLearningService._user_memories` dict clear on save
- Redis DB 5 mapping in `docs/topics/infrastructure.md`
- EventBus DLQ cleanup task (`mi:dead_letter` accumulation)
- 10 new per-plane `docs/topics/*-event-integration.md` (post-`IB-2099-T0-01` — substantive new topic docs, NOT cascade-housekeeping)
- Signal→HAI pattern-strength threshold escalation (bounded consumer)
- Revenue → Initiative revenue-threshold auto-trigger (bounded)
- 7× EventBus signature call-site trace items (SPIDER_DATA, VALIDATION_REQUIRED, VALIDATION_DECIDED, OUTCOME_RECORDED, SYSTEM_ALERT, MODEL_TRAINED, OPPORTUNITY_SCORED verification)

**Larger T3 candidates** (may re-tier to T2):
- Discord bot slice-refactor (11,677-line monolith across 25 Cogs + 96 commands)

**PARTIAL_DISCHARGE:** Full T3 leaf enumeration + SAFE_AUTONOMOUS/NEEDS_CHRIS classification deferred to arc-scoped Stage 1 work. Tracked as part of IDBT-0001.

---

## DEFER — BLOCKED_ON_RESEARCH (18 rows enumerated)

| intake_id | source_ref | source_type | title | affected_domains | risk_class | design_state | status | chris_gate | affected_surfaces |
|---|---|---|---|---|---|---|---|---|---|
| `IB-1399-BOR-01` | 1399 §6.1 | xx99_blocked_on_research | F4-CANDIDATE fields pending owner-model qualification | memory | NEEDS_ADR | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-1399-BOR-02` | 1399 §6.2 | xx99_blocked_on_research | IntelligentJobMatcher MemorySystem severity assessment | memory | NEEDS_ADR | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-1399-BOR-03` | 1399 §6.3 | xx99_blocked_on_research | Cat F ↔ Cat D turn-context enrichment intent (separation vs drift) | memory,pa,rag | NEEDS_ADR | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-1499-BOR-01` | 1499 §6.1 | xx99_blocked_on_research | T4 R.F3 income lane dormancy disposition | revenue | NEEDS_ADR | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-1499-BOR-02` | 1499 §6.4 | xx99_blocked_on_research | F.E3 dual-schema disposition (bridge vs intentional design) | revenue | NEEDS_ADR | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-1499-BOR-03` | 1499 §6.6 | xx99_blocked_on_research | State-machine remediation fork (prune vs implement) | revenue | NEEDS_ADR | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-1499-BOR-04` | 1499 §6.7 | xx99_blocked_on_research | Delivery provider choice (SendGrid vs Postmark vs SES) — auto-resolves post-`IB-1499-T1-01` | revenue | NEEDS_ADR | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-1599-BOR-01` | audit §2.6 | xx99_blocked_on_research | Sports Mobile integration UNKNOWN | sports,mobile | NEEDS_ADR | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-2199-BOR-01` | audit §2.5 | xx99_blocked_on_research | RAG `search_docs` + `kb_tool` retrieval end-to-end verification | rag,pa | NEEDS_RIGBY_SIGN_PLUS_CHRIS | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-1399-BOR-04` | audit §2.5 | xx99_blocked_on_research | Memory 14-day freshness window in ConversationOrchestrator | memory,agents | NEEDS_RIGBY_SIGN_PLUS_CHRIS | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-2699-BOR-01` | 2699 §6 (open unknown) | xx99_blocked_on_research | PA `assistant_context` view def-site enumeration | pa | NEEDS_RIGBY_SIGN_PLUS_CHRIS | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-2699-BOR-02` | 2699 Cat C DEBT-C1-4 | xx99_blocked_on_research | PA-produced DocumentEmbedding retention lifecycle inheritance | pa,memory,content | NEEDS_ADR | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-2699-BOR-03` | 2699 Cat B (16-field dump) | xx99_blocked_on_research | `paStore.isDockOpen` + `paStore.isDockMinimized` UNKNOWN intent | pa,frontend | SAFE_AUTONOMOUS | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-CDA-BOR-01` | audit §2.2 S1268 Q2 + S1273 §3.12 | cross_domain_UNKNOWN | AutoTopic → Initiative auto-creation contract UNKNOWN | signal_engine,initiative | NEEDS_ADR | POSTURE_PENDING | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-CDA-BOR-02` | audit §2.8 event_bus.py:539 | cross_domain_UNKNOWN | EventBus SPIDER_DATA consumer call-sites comprehensive trace | event_integration,spider_framework | NEEDS_RIGBY_SIGN_PLUS_CHRIS | NONE | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-CDA-BOR-03` | audit §2.8 event_bus.py:596 | cross_domain_UNKNOWN | EventBus VALIDATION_REQUIRED consumer wiring completion | event_integration | NEEDS_RIGBY_SIGN_PLUS_CHRIS | NONE | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-CDA-BOR-04` | audit §2.8 event_bus.py:619 | cross_domain_UNKNOWN | EventBus VALIDATION_DECIDED consumer wiring completion | event_integration | NEEDS_RIGBY_SIGN_PLUS_CHRIS | NONE | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |
| `IB-CDA-BOR-05` | audit §2.8 event_bus.py:643 + :686 | cross_domain_UNKNOWN | EventBus OUTCOME_RECORDED + SYSTEM_ALERT + MODEL_TRAINED consumer surface | event_integration | NEEDS_RIGBY_SIGN_PLUS_CHRIS | NONE | BLOCKED_ON_RESEARCH | RATIFIED (band) | (research first) |

---

## Cross-arc initiatives (per IOS §12.3; 5 initiatives; individual shape/scope subject to §11.3 first-arc-override refinement)

| initiative_id | pattern | surfaces_leaf | recommended_shape | chris_gate |
|---|---|---|---|---|
| `I-CX003_zero_outbound_delivery` | CX-P3 (2-of-2 confirmed) | OutreachDraft + Newsletter + BlockchainAuditBrief posture | Single cross-arc arc consuming `IB-CXP3-*` + `IB-1499-T1-01` + `IB-1699-T0-04`. Blocking: `IB-1499-T0-01` Revenue SoT ADR. | RATIFIED existence |
| `I-CX004_posture_pending_bundle` | CX-P4 (7-of-11 arcs) | Sports + Content + Revenue + Observability + HAI + Authority + Event/Integration | NOT single cross-arc — 7 discrete Chris-gated posture ADRs. Sequencing DEFERRED per 2026-07-06 Axis 4. | RATIFIED existence; sequence DEFERRED |
| `I-CX006_parallel_schema_drift` | CX-P6 (3+ arcs) | Revenue core-vs-intel + Revenue Opportunity mainline-vs-intel + Sports intel-vs-mainline + Observability LLM-telemetry dedup | Single cross-arc umbrella arc; discharges 4 SoT decisions. Blocking: `IB-1499-T0-01`, `IB-1599-T0-01`, `IB-1799-T0-01`. | RATIFIED existence |
| `I-CX007_declared_but_unenforced_contracts` | CX-P7 (auth + frontend codified) | 7 leaf surfaces: VIPInvite runtime + FleetSignatureAuth permissive fallback + DRF permission inheritance + Sidebar backend-revoke + drf-spectacular + Zustand persist + error boundaries | Shape DEFERRED per 2026-07-06 Axis 4. Single-arc OR per-surface split — Chris decides. | RATIFIED existence; shape DEFERRED |
| `I-CX008_auth_silent_degrade_codification` | CX-P8 (2-trigger threshold met at auth) | Auth failure UX + telemetry codification per IOS §5.2 rule 7 | Scope-bounded IOS rule promotion; conditional general codification if 3rd non-auth trigger surfaces. Discharges `IB-CXP8-T0-01`. | RATIFIED existence |

---

## Schema reference (IOS v1.1 §2.2)

See `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` §2.2 for the full 24-field intake schema. Highlights:

- `intake_id` — 5-prefix scheme per v1.1: `IB-<arc>-<seq>` (single-arc origin), `IB-Q<queue>-<seq>` (queue-construction), `IB-CDA-<seq>` (audit §2), `IB-CDA14-<seq>` (audit §14), `IB-CXP<n>-<seq>` (CX-P pattern).
- `source_type` — see §2.2 enum; `xx99_anchor_update` | `xx99_recommendation` | `xx99_followon_T0/T1/T2/T3` | `xx99_blocked_on_research` | `cross_domain_WEAK/MISSING/OVERCOUPLED/UNKNOWN` | `cx_pattern_Pn` | `queue_construction` | `audit_refresh_delta` | `t4_cross_arc_delegate`.
- `work_type_tier` — T0/T1/T2/T3/T4/T5 per §3.1 (T4/T5 not seeded here).
- `design_state` — NONE / SPEC_COMPLETE (CX-P10) / POSTURE_PENDING (CX-P4) / RATIFIED_ADR.
- `risk_class` — SAFE_AUTONOMOUS / NEEDS_CHRIS_PRE_RATIFICATION / NEEDS_RIGBY_SIGN_PLUS_CHRIS / NEEDS_ADR.
- `status` — INTAKE / TRIAGED / QUEUED / IN_ARC / SHIPPED / RETRACTED / BLOCKED_ON_RESEARCH / DEFERRED.
- `chris_gate` — RATIFIED / PENDING / NOT_REQUIRED. This seed populates `RATIFIED (band)` — the tier-level ratification per 2026-07-06 record. Individual row `chris_gate` may revert to PENDING at Stage 1 re-classification per IOS §11.3 reversibility.

## Amendment discipline

- **Additions:** New intake enters as `status: INTAKE`, then advances to `TRIAGED` on classification. Chris ratifies via post-arc-close reflex, cross_domain audit refresh reflex, explicit directive, or CX-P codification per IOS §2.3.
- **Retractions:** Follow IOS §8.4. Retracted findings enter `IMPLEMENTATION_DEBT.md` with `debt_type: RETRACTED` + `retraction_reason`. Do NOT delete rows here — flip `status: RETRACTED`.
- **Shipped:** On PR merge, flip `status: SHIPPED` + populate `pr_refs` + `arc_ref`. Do NOT delete.
- **Grep queries:** `grep -E '\| T0 \|' BACKLOG.md`, `grep -E 'chris_gate.*PENDING' BACKLOG.md`, `grep -E 'affected_domains.*observability' BACKLOG.md`, etc.
