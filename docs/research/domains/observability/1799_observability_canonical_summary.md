---
title: "Group 1700 Observability / Telemetry / SLOs — Canonical Summary (xx99)"
status: active (Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence 2026-07-03 on arc pin `pa-e7fbacc996b34b44` — F1 fold landed pre-commit; FIFTH arc-close canonical summary; xx99 slot per parent D72 P7; D48 preemptive stability-probe gate 24th arm HOLDING CLEAN — 19-consecutive-fully-clean-arms sub-pattern S1503-S1706+S1799 anticipated after arc-close ledger update)
authority: research
category: canonical_summary
session: 1799
date: 2026-07-03
domain_slug: observability
research_group: 1700
child_slot: P7
parent_doc: docs/research/domains/observability/1700_observability_domain_scoping.md
head_commit_before: 5867f134 (main; post-S1706 audit + cascade merged)
authors: Claude Code (Chris directed via short command "start research group 1799" — interpreted as S1799 xx99 canonical summary + Group 1700 arc-close per D72 P7 slot + start-here D72 pre-ratification)
supersedes: none (first canonical summary for the observability domain)
consumes:
  - docs/research/domains/observability/1700_observability_domain_scoping.md   # parent scoping (D69-D74 locks + §5 correlation-primitive HYPOTHESIS box)
  - docs/research/domains/observability/1701_observability_cat_a_celery_task_event_audit.md   # P1 — 6 findings
  - docs/research/domains/observability/1702_observability_cat_b_llm_call_event_audit.md      # P2 — 9 findings
  - docs/research/domains/observability/1703_observability_cat_c_agent_execution_audit.md     # P3 — 9 findings
  - docs/research/domains/observability/1704_observability_cat_d_tool_call_record_audit.md    # P4 — 9 findings
  - docs/research/domains/observability/1705_observability_cat_e_ops_run_event_audit.md       # P5 — 9 findings
  - docs/research/domains/observability/1706_observability_cat_f_adjacent_separation_boundaries_audit.md   # P6 — 9 findings
related:
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                  # §11.3 12-section template + §11.3 §10 meta-methodology FIFTH application
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md                          # §8.1 RESEARCH contract + §12.3 "Start Group NNNN" target
  - docs/research/ARCHITECTURE_INDEX.md                                         # v49 → v50 bump at S1799 close
  - docs/research/OPEN_ARCS.md                                                  # Group 1700 In-progress → Closed at S1799
  - docs/research/domains/memory/1399_memory_canonical_summary.md               # §10 first application (adopted S1399 close)
  - docs/research/domains/revenue/1499_revenue_canonical_summary.md             # §10 second application
  - docs/research/domains/sports/1599_sports_canonical_summary.md               # §10 third application
  - docs/research/domains/content/1699_content_canonical_summary.md             # §10 fourth application
  - docs/research/platform/cross_domain_integration_audit.md                    # §14 v3 refresh; §14.8 reserved for Group 1700 xx99 close consumption
  - docs/research/platform_architecture_inventory.md                            # S1273 baseline §3.25 Observability + §5.13 dedup naming
  - docs/PLATFORM_INVENTORY.md                                                  # runtime anchor
  - docs/PLATFORM_WHAT_IT_IS.md                                                 # narrative anchor
  - docs/EMPLOYEE_OS_PRIMITIVES.md                                              # Cat E canonical primitives + Employee OS boundary
  - docs/topics/employee-os.md                                                  # evidence_for_mission consumer surface (S1705 F7)
  - docs/topics/celery-workers.md                                               # Cat A operator handbook
  - docs/topics/agent-system.md                                                 # Cat C/D writer-mechanism narratives
  - docs/EVENT_SYSTEM_INVENTORY.md                                              # Cat F.c 14-model event-shape catalog
verifier_loop: |
  Chris ratifies xx99 posture-decision briefs (D74 spine option, F1 retention posture, F8 terminology posture) post-arc per D73 posture-framing discipline; xx99 does NOT select. All quantitative claims cite child §-refs; every load-bearing evidence anchor traces to a P1-P6 child §-cell. Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence 2026-07-03 on arc pin `pa-e7fbacc996b34b44` (fresh SIGN pin `pa-feebb02d7a5342ef` minted per playbook §15 promoted rule but routed-around by `tools/pa_local.sh:128` wrapper hard-code — S1600/S1700-S1706 precedent; retire owed at S1799 close per §16). Single-batch 4-question pattern held clean (D48 24th arm HOLDING CLEAN). Verdicts: Q1 coverage completeness CONFIRM Medium-High (no folds); Q2 §4 CX-patterns correctness SIGN-with-edits Medium-High (F1 fold — CX-P5 numeric claim tightened to ≥8 with §12.3 canonical enumeration pointer at 3 sites: §4.5 CX-P5 body + §10.1 MW-1 + §10.2 MC-1); Q3 §8 T0/Gate framing CONFIRM Medium (no folds; pairing framing correct); Q4 §10 meta-methodology + §7 anchor-update completeness CONFIRM Medium-High (no folds; MC-1 + MC-2 correctly at CODIFICATION-READY). F1 fold landed pre-commit. Three "do not regress" notes for PR: (i) preserve ≥8 lower-bound wording + §12.3 canonical-enumeration pointer at all 3 sites; (ii) preserve §8.1 T0/Gate paired-ADR framing (retention + D74 spine); (iii) preserve §10.2 MC-1 + MC-2 CODIFICATION-READY tags.
methodology_ratifications:
  - D69 parent-with-children (Chris-locked S1700)
  - D70 six categories A-F with F1-F6 folds (Chris-locked S1700)
  - D71 delegation boundary with Group 1900 Event Architecture explicit (Chris-locked S1700)
  - D72 P1→P2→P3→P4→P5→P6→P7 sequence (Chris-locked S1700)
  - D73 posture-decision framing = evidence plan not recommendation (Chris-locked S1700)
  - D74 arc lens = "structurally separable vs canonical unification" (Chris-locked S1700 as arc-lens question; posture selection post-arc per D73)
  - Playbook §11.3 12-section canonical summary template FIFTH application (first at S1399 Memory; then S1499 Revenue; S1599 Sports; S1699 Content; S1799 Observability = fifth)
  - Playbook §11.3 §10 meta-methodology template FIFTH application (adopted S1399 Chris directive 2026-07-01; second at S1499; third at S1599; fourth at S1699; fifth here)
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
---

# Group 1700 Observability / Telemetry / SLOs — Canonical Summary

> **What this doc is.** The xx99 canonical summary for Group 1700, the
> Observability / Telemetry / SLOs research arc. Consumes S1700 parent
> scoping + six child audits S1701–S1706 (51 findings across six
> categories A–F). Produces (a) consolidated domain shape,
> (b) cross-cutting patterns visible only across children, (c) resolved
> contradictions between children, (d) anchor-update tranche for the
> post-arc PR, (e) unified follow-on research queue, and (f) fifth
> §11.3 §10 meta-methodology retrospective on how this arc was
> conducted. Every load-bearing claim cites a P1-P6 child §-cell;
> nothing here is new evidence — synthesis only per playbook §10
> "what xx99 is (and is not)."
>
> **What this doc is not.** A new audit sweep. An architecture design
> proposal. A posture selection for D74 (structurally-separable vs
> canonical-unification) — xx99 produces the **evidence brief**; Chris
> selects post-arc per D73. An anchor edit (edits land in the
> post-arc PR bundle per playbook §16; xx99 recommends). An
> implementation plan (all §8 queue items are Chris-gated).

---

## 1. Executive Summary

**Group 1700 close verdict at HEAD `5867f134`.** Observability is
**STABLE-at-writers, PARTIAL-at-consumers, UNBOUNDED-at-retention,
and LATENT-at-cross-cat-correlation-spine.** Six child audits landed
51 load-bearing findings across six categories A-F (Cat A
CeleryTaskEvent + Cat B LLMCallEvent + Cat C AgentExecution + Cat D
ToolCallRecord + Cat E OpsRun/OpsRunEvent + Cat F Adjacent /
Separation boundaries). Every category's writer discipline is
**intact** (no unexpected writer sites across 5 boundary-violation
catalogs); every category's consumer surface is at-best
partially-wired; every category's retention posture is either
**absent** (Cat B/C/D/E/F.a HeartBeat + F.c DeliverableEvent /
OpsRunEvent) or **present-but-uneven** (only Cat A + 1/14 event
models — FleetEvent — have date-based purge tasks); and the load-bearing
D74 arc-lens question ("are the 5 execution-telemetry layers
structurally separable OR do they need canonical unification via a
single execution_id + trace_id spine?") is answered with **negative
evidence on all four posture options** — every option (A execution_id
spine, B trace_id spine, C shared correlation view, D hybrid)
requires closing at least one gating debt item first (S1704 F1 100%
NULL trace_id at 4144 rows blocks Option B runtime credibility;
S1703 F4 PA-path AgentExecution coverage gap blocks Option A
completeness; S1702 F1 multi-model LLM-telemetry duplication blocks
either A or B without dedup posture; S1705 F1 flag-gated design-intent
at Cat E leaves Option B evidence base empty until
`RIGBY_DELEGATION_ENABLED=True`).

**Six load-bearing D74 axis cells locked** (one per child; Rigby SIGN
cycle 1 F2 fold at S1706 clarified Cat F cell + established
consolidation-point framing):

| Cat | D74 axis cell | Origin |
|-----|---------------|--------|
| A CeleryTaskEvent | **DEEP-WIRED** — task_id complete singleton primitive; 8 downstream `celery_task_id` CharField consumers; string-based non-FK correlation | S1701 F5 |
| B LLMCallEvent | **DEEP-WIRED-BUT-DEDUP-UNRESOLVED** — call_id singleton at LLM-call level; execution_id borrowed spine from Cat C nullable non-FK; LLMCallLog F1 sibling model creates dual-store ambiguity | S1702 F9 |
| C AgentExecution | **COVERAGE-GAP-ON-PA-PATH** — 2 spine candidates (execution_id + trace_id); 6 downstream scalar-UUIDField consumers; F4 CRITICAL: PA agentic loop writes 0 rows | S1703 F9 |
| D ToolCallRecord | **ACTIVELY-BROKEN** — trace_id column exists + indexed + composite-indexed but 100% NULL across 4144 rows; no execution_id / tool_call_id column; the `deliverable_provenance.py:105` chain returns EMPTY for every deliverable at HEAD | S1704 F1 + F9 |
| E OpsRun+OpsRunEvent | **LATENT-VIABLE-BUT-FLAG-GATED** — F1 DESIGN-INTENT-LATENT detail-JSON writer at `rigby_delegation_signals.py:79-84` is `RIGBY_DELEGATION_ENABLED=False`-gated; F5 PRODUCER-ONLY canonical role (three CTO/COO/Trend Analysis dailies are beat-wired but consume Cat A/B/C not Cat E) | S1705 F1 + F5 + F9 |
| F Adjacent / Separation | **RETENTION-PATTERN-INCONSISTENT** — F1 HeartBeat + DeliverableEvent + OpsRunEvent lack date-based purge despite comparable-cadence peer tables (LearningReadbackEvent 30-day, FleetEvent 30-day, CeleryTaskEvent weekly) with beat-scheduled purge; cross-cat pattern with Cat F as consolidation/ratification point rather than unique root cause | S1706 F1 + F9 (Rigby SIGN cycle 1 F2 fold) |

**What changed about the domain understanding.** Before Group 1700
opened at S1700, the platform-inventory anchor (S1273 §3.25) rated
Observability at DEEP coverage but flagged 5-layer execution-telemetry
dedup as unresolved (S1273 §5.13). The arc verified the coverage tier
was correct at the writer layer for all five execution-telemetry
categories BUT tightened the diagnosis: the load-bearing gap is not
5-layer *dedup* — writer discipline is intact and boundary violations
are zero across 5 audit catalogs — the load-bearing gap is
**cross-layer correlation-spine posture** (Cat D 100% NULL trace_id is
the empirical proof) + **cross-arc retention posture** (Cat F
consolidation of A-F retention-pattern inconsistency is the systemic
proof). The 6-child sweep also verified the Cat F 14+ event-model
surface is *healthier* than S1273 lines 1912-1917 hypothesized:
12/14 WIRED-BOTH-SIDES + 1 PRODUCER-ONLY-BY-DESIGN (EngagementEvent) +
only 1 truly WRITE-ONLY-FORGOTTEN (ABTestEvent) after the S1706
post-Explore verifier-loop corrected two false-positives
(CockpitIncidentEvent + CockpitAutopilotEvent).

**What remains open post-arc.** Three Chris-gated posture decisions
form the T0/Gate tier of the follow-on queue (§8.1): (1) the D74
correlation-spine posture (A execution_id / B trace_id / C shared
view / D hybrid) — Cat F evidence contribution added retention as a
first-class ADR field; (2) the unified retention posture across
Cats A-F — a single ADR spanning the six categories rather than
per-Cat retention specs (S1706 §20.8 handoff note); (3) the F8
terminology posture (PERMEABLE-with-producer/consumer-split
recommendation) that governs the Group 1900 Event Architecture
arc-open scoping. Nine T1 CRITICAL / HIGH remediation items surface
after the T0/Gate posture ratifications (§8.2). Anchor-update
tranche (§7) includes body-systems 9→10, employees 3→4, Cat B / C /
D / E docstring + parent §-cite drift, and the standing S1605+S1606+
S1699 ARCHITECTURE_INDEX §8 timeline drift inherited from Group 1600.
The docs cascade owed post-merge per memory rule
`feedback_docs_cascade_at_every_close.md` runs after Chris merges
the S1799 PR bundle.

**Meta-methodology outcome (§10 FIFTH application).** Playbook v3
§11.3 §10 template promoted at S1399 close is confirmed durable at
five-consecutive-application. Two arc-specific meta-methodology
observations codify-ready: (a) the parent-Claude verifier-loop
correction pattern (three Explore Agent corrections across Cat C /
Cat E / Cat F saved the arc from three false-positive load-bearing
findings) is a defensible playbook v3 §14 addendum; (b) the
single-batch 4-question SIGN pattern extended into the
18-consecutive-fully-clean-arms sub-pattern (D48 preemptive
stability-probe gate held clean through 23 arms S1503-S1706)
strengthens the playbook v3 §15 promoted rule.

**Arc-close disposition.** Group 1700 row moves OPEN_ARCS
In-progress → Closed at S1799 close; arc pin
`pa-e7fbacc996b34b44` retires per playbook §16 arc-close discipline
(mirrors S1699 / S1599 / S1499 / S1399 precedents); `tools/pa_local.sh:128`
wrapper needs rotation to next-arc pin or reset to null-arc default
(playbook §22 default queue lean or Chris-specified).

---

## 2. What This Arc Answered

Per-child rollup: which of the 28 playbook canonical questions each
child answered. All six children applied playbook §11.2 20-section
template + §13 6-parallel-Explore + §14 verifier-loop
(pre-Explore + post-Explore) + §15 Rigby SIGN cycle 1.

### 2.1 S1701 Cat A CeleryTaskEvent (P1) — 6 load-bearing findings

- **Answered Q1-Q4 (Domain purpose, canonical entry points, models):**
  CeleryTaskEvent (`core/models_celery_telemetry.py:17-102`, 16
  persistent fields + auto PK) is a lightweight, autonomous, FK-free
  telemetry sink populated by 5 Celery signal handlers at
  `core/celery_telemetry.py:74-300` (F2 drift-catch: parent §3 A
  claimed `:74-177`, 5 handlers not 3).
- **Answered Q10-Q13 (Existing docs + coverage tier):** MEDIUM
  coverage; Cat A has `docs/topics/celery-workers.md` operator
  handbook + audit `docs/audit-2026/01-celery.md`.
- **Answered Q14+Q17+Q21+Q22 (Integrations):** F5 task_id primitive
  is a coverage-complete singleton for tasks reaching a worker; 8
  downstream models declare `celery_task_id` as scalar CharField with
  no FK; Cat A ↔ Cat C bridge exists via `on_agent_task_failure_bridge`
  (F4) as a legitimate S1219 P1 cross-cat exception (fire-alarm
  circuit-breaker on SoftTimeLimitExceeded gap); Cat A ↔ Cat B is
  MISSING by design (3-hop via Cat C).
- **Answered Q23-Q27 (Drift, debt, boundaries):** F1 QUEUED not
  ghost (legitimate gateway writer); F3 REVOKED not ghost (2
  legitimate writers). F2 signal-handler line-range drift owed to
  anchor-update. F5 agent_name gradual-fill (S1169 no-backfill
  stance). F6 monitor-task overhead PARTIALLY closed (S1169 decorator
  timeouts + S1170 caller-sweep; probe-decomposition root fix
  deferred to T2 R2). All 5 boundary candidates LEGITIMATE.
- **Answered Q28 (Follow-on):** 8 R-slots ranked; R1 (HIGH) contributes
  task_id evidence to xx99 D74; R2 (HIGH) monitor probe decomposition;
  R3-R5 MEDIUM; R6-R8 LOW.

### 2.2 S1702 Cat B LLMCallEvent (P2) — 9 load-bearing findings

- **Answered Q1-Q4:** LLMCallEvent (`core/models_llm_telemetry.py:30-115`,
  16 persistent fields + PK) is passive telemetry sink; owned by
  `llm_call_span` sync + `llm_call_async` async wrappers at
  `core/services/llm_call_wrapper.py` (465 lines) + `_impl_cleanup_stale_llm_calls`
  10-minute watchdog at `core/tasks_agents.py:1659-1720`.
- **Answered Q10-Q13:** MEDIUM coverage; PLATFORM_WHAT_IT_IS.md §OpenAI
  hardening (lines 436-462) covers wrapper adoption.
- **Answered Q14+Q17+Q21+Q22:** F1 CRITICAL multi-model duplication
  (LLMCallEvent + LLMCallLog + CostTracking third store surfaced by
  Rigby SIGN cycle 1 F1 fold); F2 CRITICAL PA agentic loop uncovered
  (`unified_pa_entrypoint.py` + `llm_enforcer.py` have 0 wrapper
  imports); F5 wrapper adoption 23 production sites across 8 files.
- **Answered Q23-Q27:** F3 latent `_extract_usage` gap for Gemini +
  Ollama shapes; F4 HIGH no date-based retention for LLMCallEvent
  (only 10-min stuck-STARTED watchdog); F6 MEDIUM parent §3.B
  field-list drift describes LLMCallLog fields not LLMCallEvent (F1
  root cause); F7 MEDIUM PR #3 cancel PARTIAL (no in-flight socket
  abort); F8 LOW PR #4 nested dispatch budget NOT SHIPPED. All 6
  boundary candidates LEGITIMATE.
- **Answered Q28:** F9 D74 axis contribution — `call_id` = Cat B's
  singleton at LLM-call level (0 downstream models carry `llm_call_id`);
  `execution_id` = Cat C-owned borrowed spine tagged onto Cat B rows
  (nullable by design); Cat B does NOT own a cross-model spine
  analog to Cat A `task_id`. R1-R10 ranked; R1 HIGH PA path adoption;
  R2 HIGH F1 dedup posture; R3 HIGH F4 retention; R4-R10 MEDIUM-LOW.

### 2.3 S1703 Cat C AgentExecution (P3) — 9 load-bearing findings

- **Answered Q1-Q4:** `core.AgentExecution` at
  `core/models_unified_system.py:882-1014` (23 persistent fields + PK;
  8 migrations across S0006 / S642 / S841 / S843 / S1039 / S1098
  PR#3+#4 / S1100 / S1174 PR-1) is the LIVE canonical. F1 3-class
  landmine RESOLVED via Django app registry: `intelligence/models.py:587`
  + `intelligence/models/agent_execution.py:11` are dead-code
  (unreachable at import time; not registered); `agents.AgentTaskExecution`
  = 0 rows (S1244 rename). F2 CRITICAL — S287 deprecation notice
  docstring reversed (S1084 removed runtime warning but not
  docstring); actively misleads new contributors.
- **Answered Q10-Q13:** DEEP coverage; agent-system.md +
  PLATFORM_WHAT_IT_IS.md have narrative but F3 parent scoping
  drift on "BaseAgent's `route()` wrapper" (BaseAgent has no `route()`
  — delegation via `self.agent_router.route(...)`).
- **Answered Q14+Q17+Q21+Q22:** F4 CRITICAL PA-path AgentExecution
  coverage — PA agentic loop writes 0 AgentExecution rows unless the
  tool being dispatched is a router-registered agent (analog to S1702
  F2 for Cat B). Cross-cat correlation matrix: 6 downstream models
  carry `execution_id` as scalar UUIDField non-FK; `trace_id` writer-of-record
  is router path (`agent_router.py:2850-2851`); Celery wrapper path
  does NOT thread trace_id at HEAD.
- **Answered Q23-Q27:** F5 MEDIUM no date-based retention;
  `cleanup_stale_agent_executions` is stuck-heartbeat watchdog, not
  retention; F6 HIGH Cat D correlation gap (ToolCallRecord no
  `execution_id` field); F7 JSON-path unindexed on
  `input_data['celery_task_id']` (3-hop chain scan cost); F8 4
  `post_save` receivers + partial signal silence (watchdog + cancel
  use `.update()` which bypasses signals). Zero boundary violations.
- **Answered Q28:** F9 D74 axis — 4-option Chinese menu (A
  execution_id / B trace_id / C shared correlation view / D hybrid).
  R1-R10 ranked; R1 HIGH PA-path coverage; R2 HIGH landmine +
  docstring cleanup ADR; R3 HIGH Cat D correlation posture; R4 MEDIUM
  dedicated PA execution tool + admin + `.update()` signal
  instrumentation; R5 MEDIUM 3-hop chain implementation; R6-R10 LOW.

### 2.4 S1704 Cat D ToolCallRecord (P4) — 9 load-bearing findings

- **Answered Q1-Q4:** ToolCallRecord (`core/models_tool_calls.py:19-131`,
  16 columns) written by 3 producer paths (ToolDispatcher +
  BaseAgent S970 wrapper + BaseAgent default S1085 inline recorder).
  ORM verification 2026-07-03: 4144 rows total, 39 distinct
  `agent_name`, 20-day retention window (~200 rows/day).
- **Answered Q10-Q13:** DEEP coverage on producer mechanism; MEDIUM
  on Cat D-specific narrative (topic docs treat ToolCallRecord as
  audit-trail without F1 gap coverage).
- **Answered Q14+Q17+Q21+Q22:** **F1 CRITICAL: `trace_id` is 100%
  NULL across all 4144 rows at HEAD** (ORM-verified). Root cause
  split across three writers: dispatcher hardcodes `trace_id=None`
  at `tool_dispatcher.py:961` with comment "dispatcher trace_id
  ('td-N-hex') isn't a UUID"; S970 wrapper at `base_agent.py:451-459`
  does NOT pass `trace_id`; BaseAgent default's inline record at
  `base_agent.py:3302-3310` also does NOT pass trace_id. **Column
  exists + `db_index=True` + composite-indexed with `created_at` —
  index space is wasted.** Kills S1703 F9 Option B (trace_id spine)
  at runtime; kills `deliverable_provenance.py:105` chain empirically
  (returns EMPTY for every deliverable at HEAD). F2 HIGH schema
  absence: no `execution_id`, no `tool_call_id`, no `celery_task_id`,
  no `task_id`, no FK. F3 MEDIUM — 29 of 31 base-inherited agents
  show zero rows (post-Explore correction to pre-Explore overstated
  "31 unwrapped agents write ZERO rows"; distribution is idle-agent
  or pure-LLM-agent, not a coverage-mechanism bug). F6 POSITIVE
  differentiator: PA path writes 907 rows (22% of total) via
  ToolDispatcher — Cat D has partial PA coverage where Cat C has
  none.
- **Answered Q23-Q27:** F4 MEDIUM WRITE-ONLY-FORGOTTEN pipeline —
  `analyze_pa_tool_patterns` + `aggregate_tool_call_stats` are
  `@shared_task` defined + queue-routed but NEITHER in beat schedule
  nor `PeriodicTask` table; consequence: PAToolInsight = 0 rows +
  ToolCallAggregate = 0 rows at HEAD. F5 MEDIUM no date-based
  retention. F7 LOW two dead-writer methods retained per
  `feedback_verify_before_deleting_dead_code.md` rule (cross-repo
  fleet-caller verification owed). F8 LOW no Django admin registration.
  Zero boundary violations.
- **Answered Q28:** F9 D74 axis contribution — Cat D provides
  **negative evidence on all four F9 options** unless a spine
  primitive is populated at write time. R1-R12 ranked; R1 HIGH D74
  posture; R2 HIGH F1 trace_id write coverage repair (gating
  prerequisite for Option B posture evaluation per Rigby SIGN cycle
  1 F4 fold); R3 HIGH F4 mining reactivation; R4-R6 MEDIUM; R7-R12 LOW.

### 2.5 S1705 Cat E OpsRun + OpsRunEvent (P5) — 9 load-bearing findings

- **Answered Q1-Q4:** OpsRun + OpsRunEvent at
  `core/models_ops_runs.py:11-117` (S1250 PR3) is the mission-domain
  audit trail. ORM verification 2026-07-03: 36 OpsRun rows (19 ops +
  17 mission) + 224 OpsRunEvent rows over 20 days. 17 mission rows
  = 4 employees × cadence (`docs_cascade`=7, `bug_triage_daily`=4,
  `morning_brief`=4, `platform_audit`=2). F3 employee count drift:
  CLAUDE.md + PLATFORM_INVENTORY claim "3 employees" but registry
  `_EMPLOYEES_BY_HANDLE` has 4 handles (bug_triage_specialist added
  S1267).
- **Answered Q10-Q13:** MEDIUM-DEEP coverage on Employee OS narrative
  (`docs/topics/employee-os.md` + `docs/EMPLOYEE_OS_PRIMITIVES.md`);
  gaps on F1 flag-gate design intent, F5 producer-only role, and
  F7 `evidence_for_mission` named-but-broken.
- **Answered Q14+Q17+Q21+Q22:** F1 HIGH DESIGN-INTENT-LATENT —
  `rigby_delegation_signals.py:79-84` (S1250 PR 8) IS built to
  populate `execution_id` in OpsRunEvent detail JSON on
  AgentExecution post-save for delegated executions, but the handler
  is `settings.RIGBY_DELEGATION_ENABLED`-gated (default False);
  empirically 0/224 rows have execution_id key. Distinct from S1704
  F1 (Cat D column exists+indexed+always-hardcoded-None) — Cat E is
  intentionally-flag-gated. F2 HIGH schema-level correlation columns
  absent from OpsRun / OpsRunEvent. F4 POSITIVE differentiator vs Cat
  D F4 — CTO / COO / Trend Analysis daily diagnostic pipelines EXIST
  and ARE beat-wired at `core/celery.py:306-329`. F5 MEDIUM but those
  three daily aggregations do NOT consume OpsRunEvent (they read Cat
  A/B/C layers); **canonical verdict: OpsRunEvent is PRODUCER-ONLY**.
  F7 MEDIUM `evidence_for_mission` join NAMED-BUT-BROKEN for
  ToolCallRecord (two orthogonal write-gap paths: S1704 F1 trace_id
  NULL + `parameters.ops_run_id` not threaded by dispatcher).
- **Answered Q23-Q27:** F6 MEDIUM no date-based retention. F8
  POSITIVE — MissionRunner nine invariants I1-I9 all VERIFIED at
  HEAD via source read + contract test at
  `test_mission_runner.MissionRunnerImportContractTests`. Zero
  boundary violations.
- **Answered Q28:** F9 D74 axis contribution — LATENT-VIABLE-BUT-FLAG-GATED
  cell distinct from Cat D's actively-broken and Cat C's coverage-gap
  postures. R1-R12 ranked; R1 HIGH D74 posture; R2 HIGH rigby_delegation
  flag posture (evidence-plan only per Q4(d) fold, do NOT
  implement/flip during arc-close); R3 HIGH evidence_for_mission join
  repair (cross-cat); R4-R6 MEDIUM.

### 2.6 S1706 Cat F Adjacent / Separation (P6) — 9 load-bearing findings

- **Answered Q1-Q4:** Cat F consolidates HeartBeat (F.a) + SLO
  framework (F.b) + 14-model event-shape catalog (F.c) + doc-claim
  verifier (F.d) + observability↔event-architecture terminology
  boundary (F.e). F2 body-systems drift: 10 getters in
  `body_vitals.py:340-790` including `_get_nervous_vitals` at
  `:744-790` vs "9 body systems" in PLATFORM_INVENTORY.md:24 +
  CLAUDE.md autoblock. F3 `check_learning_loop_slo` line drift
  (`:13170` actual vs `:12492` claimed in parent §5.F + start-here
  L89 + S1273 line 1969).
- **Answered Q10-Q13:** DEEP for HeartBeat + 14-model producer/consumer
  catalog; MEDIUM for SLO framework; MEDIUM for doc-verifier;
  PARTIAL for terminology boundary.
- **Answered Q14+Q17+Q21+Q22:** F1 HIGH passive-leak retention —
  HeartBeat + DeliverableEvent + OpsRunEvent lack date-based purge
  despite comparable-cadence peer tables (LearningReadbackEvent
  30-day, FleetEvent 30-day, CeleryTaskEvent weekly) with beat-scheduled
  purge. Growth projection at 10-min cadence: 144/day × 365 = ~52.5K
  HeartBeat rows/year unbounded. Structural inheritance of S1705 F6
  + S1704 F5 + S1702 F4 + S1701 F6 across Cat F surface. F4 POSITIVE
  differentiator: **1/14 event-shaped models truly WRITE-ONLY-FORGOTTEN**
  (ABTestEvent at `core/models_unified_system.py:8686`, writer at
  `core/views_ab_testing.py:481`, ZERO consumer sites). Post-Explore
  verifier-loop correction to pre-Explore Agent 3 report of 3/14:
  CockpitIncidentEvent consumed at `core/views_diagnostics.py:3889`;
  CockpitAutopilotEvent consumed at `:3367`. Both corrected to
  WIRED-BOTH-SIDES. Cat F event-model surface healthier than S1273
  lines 1912-1917 hypothesized: 12/14 WIRED-BOTH-SIDES + 1
  PRODUCER-ONLY-BY-DESIGN + 1 truly orphan. F5 MEDIUM SLO surface = 2
  beat-scheduled true-SLOs + 8 on-demand hardcoded in
  `_ops_slo_status` at `td_handlers_ops.py:365-648` + 0
  `SLOResult`/`SLABreach`/`ServiceLevelObjective` model. CTO/COO/Trend
  Analysis dailies are threshold-gated alert escalators, NOT SLOs. F6
  POSITIVE — Doc-claim verifier at `core/services/doc_claim_verification.py`
  (3275 lines, 128,672 bytes) has 75 `@register_claim` decorators.
  Consumed daily by `core/jobs/docs_cascade.py:105 DRIFT_LABEL="step_5_drift_observed"`
  emitting OpsRunEvent detail. Embedded in PLATFORM_INVENTORY.md via
  `core/services/platform_inventory.py:605-639`. But: zero dedicated
  persistence table + zero CI/GitHub Actions gating + zero
  alert/notification integration. Classification: **DESIGN-INTENT-LATENT**
  (S1705 F1 analog). F7 POSITIVE HeartBeat + BodyVitalsService + 10
  body systems structurally intact. F8 MEDIUM observability↔event-architecture
  terminology boundary: **PERMEABLE with producer/consumer structural
  split** recommendation for xx99 §5 posture-decision brief.
- **Answered Q23-Q27:** All 5 boundary candidates LEGITIMATE. §16.1
  Rigby SIGN candidate-surface dispositions: resolve_node telemetry
  OUT-of-scope (separate media/render ops), memory_pressure NOT
  event-model (does not alter boundary), fleet auth token audit =
  security/compliance desk, no additional `RIGBY_*_INTAKE_ENABLED`
  siblings found.
- **Answered Q28:** F9 D74 axis contribution —
  **RETENTION-PATTERN-INCONSISTENT** (unbounded growth across key
  observability/event tables). Sixth axis cell distinct from Cat A
  DEEP-WIRED / Cat B DEEP-WIRED-BUT-DEDUP-UNRESOLVED / Cat C
  COVERAGE-GAP-ON-PA-PATH / Cat D ACTIVELY-BROKEN / Cat E
  LATENT-VIABLE-BUT-FLAG-GATED. Cross-cat pattern (A/B/D/E/F evidence)
  with Cat F serving as consolidation/ratification point rather than
  unique root cause (Rigby SIGN cycle 1 Q3 F2 fold). R1-R10 ranked;
  R1 HIGH retention posture consolidation across Cats A-F; R2 HIGH
  D74 axis posture decision; R3-R6 MEDIUM; R7 LOW Group 1900 handoff
  for ABTestEvent orphan; R8-R9 LOW non-blocking; R10 LOW anchor-refresh.

### 2.7 28-question coverage matrix — per-child rollup

| Q # | Q area | Cat A | Cat B | Cat C | Cat D | Cat E | Cat F |
|-----|--------|-------|-------|-------|-------|-------|-------|
| Q1-Q2 | Domain purpose + boundary | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Q3 | Canonical entry points | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Q4-Q9 | Major models + FK graph + retention + services | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Q10-Q13 | Existing docs + coverage tier | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Q14+Q17+Q18+Q21+Q22 | Integrations + cross-cat | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Q19-Q20 | Event flows + emission gaps | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Q23-Q27 | Drift + debt + boundaries + dupe + ownership | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Q28 | Follow-on research | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**All 28 canonical questions × 6 children = 168 answer cells filled.**
Every child's audit doc §-cells trace directly to the responsible
canonical-question spectrum per playbook §11.2 template requirements.

---

## 3. Consolidated Domain Shape

Group 1700's arc scope is the **five-parallel-execution-telemetry
layer surface plus adjacent Body Systems / SLO framework / event-shape
model catalog / doc-claim verifier / observability↔event-architecture
terminology boundary**. The reader's mental model is a six-category
producer/consumer/correlation graph:

```
                     ┌─────────────────────────────────────────────┐
                     │        USER  →  PA agentic loop             │
                     │  (unified_pa_entrypoint.py + llm_enforcer)  │
                     └──────────┬──────────────────────────────────┘
                                │
                                │  (F2/F4 gap: PA writes 0 LLMCallEvent + 0 AgentExecution
                                │   rows for its dispatched work; Cat D partial via dispatcher)
                                ▼
              ┌───────────────────────────────────────────────────────┐
              │   agent_router.route()  →  BaseAgent instantiation    │
              │  writes AgentExecution row + trace_id (via S843 svc)  │
              └────┬──────────────────────────────────────────────────┘
                   │
                   ▼
        ┌─────────────────────┐   ┌──────────────────┐    ┌─────────────────┐
        │  Cat A              │   │  Cat C           │    │  Cat E          │
        │  CeleryTaskEvent    │   │  AgentExecution  │    │  OpsRun +       │
        │  (task_id spine)    │◄──┤  (execution_id,  │───►│  OpsRunEvent    │
        │  8 downstream       │   │   trace_id)      │    │  (mission_id)   │
        │  scalar CharField   │   │  6 downstream    │    │  producer-only  │
        └─────────┬───────────┘   │  scalar UUIDField│    │  audit trail    │
                  │               │  incl. Cat B     │    └─────────┬───────┘
                  │               │  execution_id    │              │
                  │  (F4          │  borrowed spine  │              │  (detail JSON
                  │   fire-alarm  └────┬─────────────┘              │   populates
                  │   cross-cat        │                            │   execution_id
                  │   exception:       │                            │   only when
                  │   on_agent_        ▼                            │   RIGBY_DELEGATION
                  │   task_failure)  ┌──────────────────┐           │   _ENABLED=True;
                  │                  │  Cat B           │           │   flag-gated OFF
                  │                  │  LLMCallEvent    │           │   default)
                  │                  │  (call_id +      │           │
                  │                  │   execution_id)  │           │
                  │                  │  BUT: LLMCallLog │           │
                  │                  │  sibling model   │           │
                  │                  │  (F1 dup)        │           │
                  │                  └───────┬──────────┘           │
                  │                          │                      │
                  │                          ▼                      │
                  │                  ┌──────────────────┐           │
                  │                  │  Cat D           │           │
                  │                  │  ToolCallRecord  │           │
                  │                  │  (trace_id       │           │
                  │                  │   column exists  │           │
                  │                  │   + indexed BUT  │           │
                  │                  │   100% NULL      │           │
                  │                  │   empirically)   │           │
                  │                  └──────────────────┘           │
                  │                                                 │
                  └─────────────────────────────────────────────────┘
                                          │
                                          ▼
                  ┌───────────────────────────────────────────────┐
                  │  Cat F Adjacent surface                       │
                  │  (F.a) HeartBeat: 10 body-system pulse        │
                  │  (F.b) SLO framework: 2 beat + 8 on-demand    │
                  │  (F.c) 14 event models: 12 WIRED-BOTH-SIDES,  │
                  │        1 PRODUCER-ONLY-BY-DESIGN,             │
                  │        1 WRITE-ONLY-FORGOTTEN (ABTestEvent)   │
                  │  (F.d) doc-claim verifier: 75 registered      │
                  │        claims; DESIGN-INTENT-LATENT           │
                  │        integration                            │
                  │  (F.e) terminology: PERMEABLE-with-producer/  │
                  │        consumer-split recommendation for      │
                  │        Group 1900 handoff                     │
                  └───────────────────────────────────────────────┘
```

**Layer summary.** Five execution-telemetry layers (Cat A/B/C/D/E) +
one adjacent-and-boundary layer (Cat F). Five categories have
**stable writer discipline** with **zero unexpected write sites**
across five §16 boundary catalogs (5 legitimate cross-cat exception
+ 20 in-scope writers). The load-bearing gaps sit at three
cross-category axes:

1. **Correlation-spine axis (D74).** Six spine primitives evaluated
   across the arc:

   | Primitive | Owner Cat | Cross-model spine? | Verified populated? | Blocks which posture options? |
   |-----------|-----------|--------------------|---------------------|-------------------------------|
   | `task_id` | A | Yes (8 downstream scalar-CharField) | Yes (100% for tasks reaching worker) | None |
   | `call_id` | B | No (0 downstream) | Yes (PK, 100%) | None (LLM-call-level singleton, not arc-wide spine) |
   | `execution_id` | C | Yes (6 downstream scalar-UUIDField non-FK) | Partial (F4 PA path=NULL; wrapper path=populated) | Blocks Option A completeness until PA path covered |
   | `trace_id` | C | Yes (Cat D column + LLMCallLog + AgentExecution) | Cat D 100% NULL empirically (S1704 F1); Cat C partial (Celery wrapper path leaves NULL); Cat B `LLMCallEvent` has NO field | Blocks Option B runtime credibility |
   | `tool_call_id` | (schema-absent) | Would-be | N/A (does not exist on ToolCallRecord) | Blocks §3.B accounting-rule enforcement |
   | `mission_id` | E | No (Ops-scope only, indexed on OpsRun) | Yes for domain=mission (17/17) | None (mission-scope) |

2. **Retention axis (F1).** Six categories evaluated; **1/14 event
   models + Cat A alone have date-based purge tasks; five categories
   accumulate unbounded** at HEAD:

   | Table | Retention posture | Peer with purge |
   |-------|-------------------|-----------------|
   | CeleryTaskEvent (Cat A) | 30-day weekly cleanup via `cleanup_celery_task_events` | (self) |
   | LLMCallEvent (Cat B) | **NONE** — only 10-min watchdog for stuck STARTED rows | LLMCallLog sibling has 30-day |
   | AgentExecution (Cat C) | **NONE** — heartbeat-staleness watchdog only | Cat A + LLMCallLog have 30-day |
   | ToolCallRecord (Cat D) | **NONE** | Cat A has 30-day |
   | OpsRun / OpsRunEvent (Cat E) | **NONE** | Cat A has 30-day; FleetEvent has 30-day |
   | HeartBeat (Cat F.a) | **NONE** | LearningReadbackEvent has 30-day |
   | DeliverableEvent (Cat F.c) | **NONE** | (peer) |
   | ImpactEvent (Cat F.c) | **NONE** | (peer) |
   | FleetEvent (Cat F.c) | **30-day HARD-DELETE** via `fleet_event_cleanup.py:70` | (self, exemplar) |
   | Other 12 event models (Cat F.c) | **NONE** | (peer) |

3. **Consumer surface axis.** Five layers have at-best partially-wired
   consumer surfaces; the load-bearing consumer gaps are (a) Cat B
   `cost_telemetry_tool` reads LLMCallLog not LLMCallEvent (F1 dup
   root cause); (b) Cat C has NO dedicated PA `execution_history_tool`
   analog to Cat A's `task_breakdown_tool`; (c) Cat D `analyze_pa_tool_patterns`
   + `aggregate_tool_call_stats` WRITE-ONLY-FORGOTTEN dark pipeline
   (PAToolInsight = 0 rows, ToolCallAggregate = 0 rows); (d) Cat E
   `evidence_for_mission` ToolCallRecord join is empirically broken
   for two orthogonal reasons; (e) Cat F.a HeartBeat REST endpoints
   exist but no frontend UI wiring.

**Six categories, three cross-cutting axes, one arc lens question
(D74) — that is the domain shape.** Individual categories are
architecturally distinct enough to sustain independent audits (six
6-parallel-Explore sweeps + six Rigby SIGN cycles landed) yet
integrated enough that patterns visible only across children became
the load-bearing findings (see §4).

---

## 4. Cross-Cutting Patterns

Themes visible only across multiple children. Each pattern is
sourced from ≥2 child audits.

### 4.1 CX-P1 — Passive-leak retention is codebase-native but not codebase-uniform

**Evidence base.** S1701 F6 (Cat A has 30-day; monitor overhead
partially closed). S1702 F4 HIGH (Cat B no date-based retention;
sibling LLMCallLog has 30-day via `cleanup_llm_call_logs`). S1703 F5
MEDIUM (Cat C no retention; stuck-watchdog only). S1704 F5 MEDIUM
(Cat D no retention). S1705 F6 MEDIUM (Cat E no retention). S1706
F1 HIGH (Cat F HeartBeat + DeliverableEvent + OpsRunEvent lack
purge). S1706 §14 F1 companion evidence: FleetEvent
(`fleet_event_cleanup.py:70`, 30-day) + LearningReadbackEvent
(`core/celery.py:246`, beat-wired) are peer exemplars.

**Pattern statement.** The codebase already knows how to write
date-based retention. Two exemplars land the standard shape
(env-var-driven retention days + beat-scheduled Celery task +
transaction-safe `.filter(created_at__lt=cutoff).delete()`). Five of
the six audited categories have **no retention** despite each
producer-side write cadence being verified as bounded but
non-trivial (Cat B → 23 wrapper sites; Cat C → 172 embedments; Cat D
→ ~200 rows/day at HEAD; Cat E → 36 OpsRun + 224 OpsRunEvent over
20 days; Cat F.a HeartBeat → ~52.5K/year at 10-min cadence).

**Load-bearing insight.** This is a **retention discipline** debt,
not a per-Cat design flaw. The correct xx99 §8 output is a **single
unified retention-policy ADR** spanning A-F rather than per-Cat
retention specs (per S1706 §20.8 handoff note). Cat F provides the
consolidation evidence; every other Cat provides the peer-evidence.

**Post-arc T0/Gate candidate.** R.OBSERVABILITY.RETENTION-UNIFIED-ADR
(§8.1). Chris ratifies default windows per Cat (recommended: Cat A
30d already exists; Cat B 30-day; Cat C 30-90d; Cat D 30d; Cat E
90d; HeartBeat 30d; DeliverableEvent + OpsRunEvent 90d).

### 4.2 CX-P2 — Correlation-spine posture is unresolved but the arc has full evidence

**Evidence base.** S1701 F5 (task_id primitive posture). S1702 F9
(Cat B call_id + execution_id borrowed spine). S1703 F9 (Cat C
4-option Chinese menu A/B/C/D). S1704 F9 (Cat D negative evidence on
all 4 options; runtime credibility problem for Option B). S1705 F9
(Cat E LATENT-VIABLE-BUT-FLAG-GATED). S1706 F9 (Cat F retention as
first-class ADR field regardless of D74 selection).

**Pattern statement.** The load-bearing D74 arc lens question was
**posed** at S1700 open as an evidence-plan discipline
(D73 posture-framing). All six children contribute evidence; xx99
consolidates into a **four-option posture-decision brief**:

- **Option A: execution_id spine.** Cat A `task_id` stays layer-owned;
  execution_id becomes canonical spine at Cat B/C/D/E. Requires:
  (1) closing S1703 F4 PA-path AgentExecution coverage; (2) adding
  `ToolCallRecord.execution_id` column + backfill (S1704 F2 / R4);
  (3) resolving S1702 F1 dedup (choose LLMCallEvent or LLMCallLog
  as authoritative); (4) preserving S1702 wrapper contract semantics
  ("execution_id survives AgentExecution deletion"). Smallest schema
  moves at Cat A / Cat C; heaviest at Cat D.
- **Option B: trace_id spine.** Cat C `trace_id` becomes canonical
  spine spanning Cat C / Cat D / potentially Cat B. Requires: (1)
  closing S1704 F1 trace_id 100% NULL (dispatcher must generate real
  UUID replacing `td-N-hex` string, wrapper + base default + PA loop
  must thread from context); (2) adding `LLMCallEvent.trace_id`
  field OR reading trace_id from LLMCallLog sibling; (3) closing
  NULL-ratio uncertainty on Cat C `trace_id` (Celery-wrapper path
  doesn't thread today). Smallest schema move at Cat D (column
  exists); heaviest coordination cost at three-writer trace_id thread.
- **Option C: shared correlation view.** No new columns — build a
  Postgres materialized view OR Redis lookup table joining
  `CeleryTaskEvent.task_id ↔ AgentExecution.input_data['celery_task_id']
  ↔ LLMCallEvent.execution_id ↔ ToolCallRecord.trace_id ↔ OpsRunEvent.detail`.
  Preserves per-Cat autonomy; adds query-time join layer. Requires
  at least ONE primitive populated at each layer first (Cat D has
  zero populated today; blocks Option C directly).
- **Option D: hybrid.** execution_id at telemetry-write level
  (Cat B/C/D) + trace_id as user-visible drill-down breadcrumb.
  Inherits Option A + Option B prerequisites.

**Load-bearing insight.** Cat D's 100% NULL trace_id at 4144 rows
(S1704 F1 empirical evidence) makes Option B **runtime-incredible
today** regardless of schema-lift favorability. Option A is the
tightest schema move IF PA-path coverage (S1703 F4) can be closed.
Both A and B require the same three-writer coordination at Cat D
(dispatcher + wrapper + base default). Option C rests on ONE of A/B
being partially implemented; Option D is the sum of A+B.

**Post-arc T0/Gate candidate.** R.OBSERVABILITY.D74-SPINE-POSTURE
(§8.1). Chris ratifies among A/B/C/D per D73 posture-framing
discipline. All six children provide evidence; xx99 does NOT select.

### 4.3 CX-P3 — PA agentic loop is under-instrumented at three telemetry layers

**Evidence base.** S1702 F2 CRITICAL (PA `unified_pa_entrypoint.py` +
`llm_enforcer.py` have 0 wrapper imports → 0 LLMCallEvent rows for
PA-dispatched LLM calls). S1703 F4 CRITICAL (PA agentic loop writes
0 AgentExecution rows unless the dispatched tool is a
router-registered agent). S1704 F6 POSITIVE differentiator (Cat D
has partial PA coverage — 907 ToolCallRecord rows / 22% of total via
dispatcher path). S1705 F1 flag-gated Cat E path implicitly leaves
PA-mission-boundary invisible when flag OFF.

**Pattern statement.** Cat B + Cat C both flag PA agentic loop as
the dominant LLM caller with zero coverage; Cat D has partial coverage
via the same dispatcher path that Cat A/B/C are missing. This is a
**PA-observability posture** question that spans three layers.

**Load-bearing insight.** Fixing PA coverage requires either (a)
threading `llm_call_span` through `unified_pa_entrypoint._enforce_real_ai`
+ writing AgentExecution rows for each PA turn, OR (b) accepting
that PA-dispatched calls have a different telemetry model (PA session
= AgentExecution-shaped analog). Both options are Chris-gated
posture decisions. xx99 does NOT select; §8.2 T1 CRITICAL surfaces
the requirement.

**T1 CRITICAL follow-on.** R.OBSERVABILITY.PA-COVERAGE-POSTURE
(§8.2). Blocks Option A of CX-P2 D74 posture.

### 4.4 CX-P4 — Boundary discipline is verified intact across five §16 catalogs

**Evidence base.** S1701 §16 (5 Cat A boundary candidates all
LEGITIMATE; 1 cross-cat exception `on_agent_task_failure_bridge`
S1219 P1 correctness fix, 4 parallel writers). S1702 §16 (6 Cat B
boundary candidates all LEGITIMATE; zero violations). S1703 §16 (0
Cat C boundary violations; single cross-cat exception inbound from
Cat A). S1704 §16 (5 Cat D boundary candidates all LEGITIMATE;
`unified_pa_entrypoint._record_tool_call` DEPRECATED but retained per
verify-before-deleting rule). S1705 §16 (5 Cat E boundary candidates
all LEGITIMATE; MissionRunner I9 boundary held via contract test).
S1706 §16 (5 Cat F boundary candidates all LEGITIMATE; §16.1 SIGN
candidate-surface dispositions rule out resolve_node + memory_pressure
+ fleet auth + additional RIGBY flags).

**Pattern statement.** Across 26 boundary candidates evaluated
(5 + 6 + 0 + 5 + 5 + 5), **26 verdicts LEGITIMATE / zero unexpected
writer sites**. The one cross-cat exception (Cat A→Cat C fire-alarm
bridge) is the S1219 P1 correctness fix that both S1701 §16 and
S1703 §16 catalog from opposite sides.

**Load-bearing insight.** Boundary discipline is a **quiet arc
positive**. The dedup crisis narrative from S1273 §11.6 5-layer
execution-telemetry dedup framing is real about **correlation-spine
absence** but **not real about writer discipline**. Every category
has intact write-path ownership. The next Group 1700 T-slot repair
should reject any "unify writer paths" framing — writer discipline
is already unified per-Cat.

### 4.5 CX-P5 — Verifier-loop caught three false-positive Explore Agent findings

**Evidence base.** S1703 §14 VC1-VC3 (three post-Explore corrections).
S1705 §14 D7 + VC1/VC2/VC3 (three post-Explore corrections). S1706
§14 F4 verifier-loop correction (2 Agent-3 verdicts corrected). S1704
F3 (post-Explore correction to pre-Explore overstated coverage
claim).

**Pattern statement.** Six children × 6-parallel-Explore agents each
= 36 Explore-agent claims per audit × 6 audits = 216 evaluated
claims. Verifier-loop pre-Explore + post-Explore surfaced **≥8
material corrections** across the arc (minimum set tracked in child
§14 verifier ledgers; canonical enumeration at §12.3). Categories
touched: Cat C 3-class landmine resolution + F4 PA-path coverage
severity + F1 trace_id writer-of-record clarification; Cat E
execution_id flag-gate confirmation + CTO/COO/Trend Analysis
existence + package location + F3 employee count 3→4; Cat F
CockpitIncidentEvent + CockpitAutopilotEvent WIRED-BOTH-SIDES
correction; Cat D base-inherited coverage statistic. Each correction
would have shipped a false-positive load-bearing finding without the
verifier-loop discipline.

**Load-bearing insight.** The playbook §14 verifier-loop pattern
proved its worth six times in one arc. This is the **strongest
methodological validation** the playbook has received across five
arc closes (S1399, S1499, S1599, S1699, S1799 — see §10.1 for
meta-methodology detail). Recommendation for playbook v3: promote
"parent-Claude verifier-loop for every load-bearing binary claim,
both pre-Explore AND post-Explore" from playbook §14 discipline to
playbook §14 **required** — matches the S1706 audit's own §20.1
Verifier-loop record as a template.

### 4.6 CX-P6 — Consumer-surface partial-wiring is systemic, not per-Cat

**Evidence base.** S1701 §11 (Cat A `task_breakdown_tool` present but
no dedicated PA reader for CeleryTaskEvent gaps). S1702 F1 CRITICAL
(Cat B `cost_telemetry_tool` reads LLMCallLog not LLMCallEvent — F1
dup root cause is misdirected consumer). S1703 R4 (Cat C has NO
dedicated PA `execution_history_tool` + no Django admin registration).
S1704 F4 (Cat D `analyze_pa_tool_patterns` + `aggregate_tool_call_stats`
WRITE-ONLY-FORGOTTEN → PAToolInsight + ToolCallAggregate BOTH 0 rows).
S1705 F7 (Cat E `evidence_for_mission` join named-but-broken). S1706
F5 (Cat F.b SLO on-demand `_ops_slo_status` uses 2-min cache with
zero persistence; F6 doc-claim verifier has 75 claims but zero CI
gate + zero alert integration).

**Pattern statement.** Every category has a partially-wired consumer
surface. Writer discipline is uniformly intact; consumer discipline
is uniformly patchy. Cross-cutting: 6/6 categories audit their
consumer surface as at-best PARTIAL.

**Load-bearing insight.** Group 1700 is **producer-strong /
consumer-partial** across the board. This is not a per-Cat repair
question; it's a systemic engineering pattern. Chris-gated posture:
should xx99 §8 T1 include a bundle "consumer-surface consolidation
sweep" (dedicated PA read tools + Django admin registrations + CI
gates) OR should each Cat's consumer gap remain per-child follow-on?
xx99 does NOT select; §8.2 surfaces both framings.

### 4.7 CX-P7 — Playbook §11.2 20-section template held across six consecutive applications

**Evidence base.** S1701 template FIRST application under Group 1700
(SIXTH overall — S1601 was first under Group 1600). S1702-S1706 each
applied template with F1-Fn folds per child. S1706 was SIXTH
application under Group 1700 alone.

**Pattern statement.** The playbook §11.2 template survived six
consecutive same-arc applications with zero structural revisions
required. F1-F6 parent §5 correlation-primitive fold and F1-F9
per-child section standardization both durable.

**Load-bearing insight.** Playbook v3 §11.2 promotion CONFIRMED-STRENGTHENED
via SIXTH under Group 1700 application (fourth arc to promote it
after S1399/S1499/S1599 established two-triggers → v3 promotion, and
S1699 confirmed durable at four-consecutive-application). Chris need
not re-ratify at each xx99; the template is now beyond ratification
threshold. Meta-methodology §10 records this.

---

## 5. Resolved Contradictions

Where children disagreed with each other, with parent scoping, with
prior anchors, or with S1273/S1274 baseline. Canonical verdict +
rationale per resolution.

### 5.1 Explore Agent 1 vs runtime ORM — Cat E execution_id thread state

**Conflict.** S1705 Explore Agent 1 claimed `execution_id` IS threaded
into OpsRunEvent.detail via `rigby_delegation_signals.py:70`. Runtime
ORM check showed 0/224 rows with `execution_id` key.

**Canonical verdict.** Agent 1 read the writer source at `:70` which
DOES thread execution_id when the handler runs, BUT did not verify
the flag gate at `:22-25`. `settings.RIGBY_DELEGATION_ENABLED` is
`False` by default; the handler short-circuits before the thread
fires. Fold at S1705 F1: **DESIGN-INTENT-LATENT** (Cat E) distinct
from **SCHEMA+RUNTIME-BROKEN** (S1704 F1 at Cat D).

**Rationale.** Cat E telemetry writer is intentionally-flag-gated
(design intent viable, runtime empty). Cat D telemetry writer is
schema-viable + runtime-null (writer intentionally hardcodes NULL).
Both surface identical empirical outcome (0 rows carry correlation
IDs) but arise from different postures. xx99 §5 posture-decision
brief consumes both distinctions.

### 5.2 Explore Agent 6 vs Agent 2 — Cat E daily diagnostics existence

**Conflict.** S1705 Explore Agent 6 claimed "CTO/COO/Trend Analysis
daily DOES NOT EXIST" (searched Ops Autopilot module). Explore Agent
2 found them at `core/services/diagnostics/{cto_daily,coo_daily}.py`
+ `core/services/scheduled_diagnostic_runner.py` + beat-wired at
`core/celery.py:306-329`.

**Canonical verdict.** Agent 2 was correct. Agent 6 searched the
wrong package (Ops Autopilot vs `core/services/diagnostics/`). Fold
at S1705 F4: **POSITIVE differentiator vs Cat D F4** — three fully-wired
daily aggregations exist.

**Rationale.** Cat E has a **material positive** vs Cat D
WRITE-ONLY-FORGOTTEN (S1704 F4) diagnostic-pipeline surface. But
these diagnostics do NOT consume OpsRunEvent (they read Cat A/B/C
layers). Resolves parent §5.E producer-vs-consumer question:
**OpsRunEvent is PRODUCER-ONLY** primary source of mission telemetry,
not a consumer/aggregator (S1705 F5).

### 5.3 Explore Agent 3 (S1706) vs post-Explore verifier — Cat F.c 3 WRITE-ONLY-FORGOTTEN candidates

**Conflict.** S1706 Explore Agent 3 reported 3/14 event-shaped models
as WRITE-ONLY-FORGOTTEN: ABTestEvent + CockpitIncidentEvent +
CockpitAutopilotEvent.

**Canonical verdict.** Post-Explore verifier-loop corrected 2 of 3:
CockpitIncidentEvent consumed at `core/views_diagnostics.py:3889`
(`filter(incident=inc).order_by('created_at')`); CockpitAutopilotEvent
consumed at `:3367` (`select_related('policy')[:limit].values(...)`).
Both are **self-consumers in the diagnostics UI**. Fold at S1706 F4:
Only **ABTestEvent** is truly WRITE-ONLY-FORGOTTEN (1/14 = 7.1%).

**Rationale.** The Cat F event-model surface is healthier than S1273
lines 1912-1917 hypothesized (which anticipated ≥3 orphans). Correction
lands the surface at **12/14 WIRED-BOTH-SIDES + 1 PRODUCER-ONLY-BY-DESIGN
+ 1 true orphan** — a POSITIVE health verdict, not a
WRITE-ONLY-FORGOTTEN-ARC-WIDE crisis. §7.4 anchor-update owed.

### 5.4 S1273 5-layer dedup framing vs arc evidence

**Conflict.** S1273 §5.13 named the arc lens as "5-layer execution-telemetry
dedup" implying **writer path unification** would resolve the crisis.

**Canonical verdict.** Arc evidence RE-FRAMES the load-bearing gap:
**writer discipline is intact per §4.4 CX-P4 (26 boundary candidates,
26 LEGITIMATE verdicts).** The load-bearing gaps are (1)
correlation-spine posture (D74; §4.2 CX-P2) and (2) retention
posture (§4.1 CX-P1). These are cross-layer questions, not writer-path
dedup questions.

**Rationale.** Dedup framing was accurate about the arc scope but
misdiagnosed the mechanism. Xx99 §7.3 anchor-update owed to
S1273 line 1969 + parent §5.13 to reframe from "dedup" to
"correlation-spine-plus-retention posture."

### 5.5 Parent §5 correlation-primitive HYPOTHESIS box vs child evidence

**Conflict.** Parent §5 F5 fold introduced 5 correlation primitives
(`task_id` / `execution_id` / `trace_id` / `tool_call_id` /
`mission_id`) as HYPOTHESES pending child verification.

**Canonical verdict per primitive:**

| Primitive | Verdict | Source |
|-----------|---------|--------|
| `task_id` | **VERIFIED** — Cat A owned; complete coverage for tasks reaching worker; 8 downstream string-based non-FK consumers | S1701 F5 |
| `execution_id` | **REVISED** — hypothesis said "intended to span full task→LLM→agent→tool sequence"; actual scope is Cat C-owned + Cat B tags it (borrowed spine) + Cat D has NO field + Cat E has NO field | S1702 F9 + S1703 F9 + S1704 F2 + S1705 F2 |
| `trace_id` | **PARTIALLY REVISED** — hypothesis said "S843 field on DEPRECATED AgentExecution"; correction: Cat C.trace_id is on LIVE canonical `core.AgentExecution:906-909` (not deprecated); 3-class landmine was dead-code false alarm (S1703 F1) | S1703 F1 + S1704 F1 |
| `tool_call_id` | **REFUTED** — hypothesis said "scoped to single tool invocation; correlation to LLMCallEvent"; actual: ToolCallRecord has NO `tool_call_id` field. Dispatcher generates local `td-N-hex` trace_id at `:626` but does NOT persist it. Semantic-only presence in truncated `task_summary` string field. Parent §5 hypothesis needs xx99 revision. | S1704 D7 HIGH |
| `mission_id` | **CONFIRMED** — hypothesis said "Ops-scope correlation, NOT cross-layer"; verified at Cat E schema-level (`OpsRun.mission_id` UUIDField indexed) + verified NOT threaded from prior 4 layers | S1705 F2 |

**Rationale.** 1 verified as-hypothesized, 1 confirmed, 1 partially
revised, 1 revised, 1 refuted. The parent §5 HYPOTHESIS discipline
worked exactly as designed — each hypothesis was verified/refined by
the named child audit, and the refutation (tool_call_id) is
load-bearing evidence for §5 posture-decision brief. §7.3
anchor-update owed to parent §5 F5 box to record 5 verdicts.

### 5.6 Parent §3 A signal-handler line-range drift

**Conflict.** Parent §3 A cited signal-handler range as `:74-177`
with 3 handlers.

**Canonical verdict.** Actual range `:74-300` with 5 distinct handlers
(F2 drift-catch at S1701). §7.3 anchor-update owed.

### 5.7 Parent §3.B field-list drift

**Conflict.** Parent §3.B listed `model, prompt_tokens, completion_tokens,
total_tokens, latency_ms, cost, execution_id, success, error` for
LLMCallEvent.

**Canonical verdict.** Field list actually matches **LLMCallLog**
(F1 sibling model). LLMCallEvent has 16 fields per S1702 §4. §7.3
anchor-update owed to disambiguate LLMCallEvent vs LLMCallLog.

### 5.8 Parent §3.C 3-class AgentExecution landmine

**Conflict.** Parent §3.C flagged 3 `class AgentExecution` bodies at
HEAD as ambiguity risk.

**Canonical verdict.** S1703 F1 resolved: only `core.AgentExecution`
is Django-app-registry-registered LIVE canonical. The two
intelligence-side class bodies are **dead code** (unreachable at
import time). D4 escalated from MEDIUM → HIGH per Rigby SIGN cycle 1
F2 fold — dead-code misclassification risks remediation against
unreachable classes. §7.4 anchor-update owed to parent §3.C wording.

### 5.9 CLAUDE.md + PLATFORM_INVENTORY body-systems count

**Conflict.** CLAUDE.md Live Counts autoblock + PLATFORM_INVENTORY.md:24
+ PLATFORM_INVENTORY body-systems-section-headline all claim "9 body
systems."

**Canonical verdict.** S1706 F2 verified 10 getters in
`core/services/body_vitals.py:340-790` including `_get_nervous_vitals`
at `:744-790`. §7.1 + §7.3 anchor-update owed via `refresh_doc_inventory_blocks`
regeneration.

### 5.10 CLAUDE.md + PLATFORM_INVENTORY employee count

**Conflict.** CLAUDE.md :150-172 + PLATFORM_INVENTORY.md Employees
autoblock claim 3 Employees.

**Canonical verdict.** S1705 F3 verified 4 handles in
`_EMPLOYEES_BY_HANDLE` registry (rigby + platform_auditor +
chief_of_staff + bug_triage_specialist added S1267 PR 4.1). §7.1 +
§7.3 anchor-update owed via `generate_platform_inventory` regeneration.

### 5.11 Parent §5.F check_learning_loop_slo line-cite

**Conflict.** Parent §5.F + `00-START-NEXT-SESSION.md:89` + S1273
line 1969 all cite `core/tasks.py:12492`.

**Canonical verdict.** S1706 F3 verified `check_learning_loop_slo`
at `core/tasks.py:13170`. +678 line drift from S1093-S1094 CTO
diagnostic + subsequent additions. §7.3 anchor-update owed.

---

## 6. Unresolved Unknowns

Explicit list; each promotes to §8 follow-on queue. Cited by
originating child §-cell.

### 6.1 Percentage of LLMCallEvent rows with `execution_id = NULL` at HEAD

**Source.** S1703 §20.4 UNK-1 + S1702 F2 evidence.

**Question.** How many production LLMCallEvent rows carry
`execution_id = NULL` (i.e., PA-path or script-path calls)? Requires
live-DB query beyond verifier-loop scope.

**Promotes to.** §8.2 T1 CRITICAL R.OBSERVABILITY.PA-COVERAGE-POSTURE
evidence gathering.

### 6.2 Percentage of AgentExecution rows with `trace_id = NULL` at HEAD

**Source.** S1703 §20.4 UNK-2. Related: S1705 F1 flag-gated Cat E path.

**Question.** How many production AgentExecution rows carry
`trace_id = NULL` (Celery-wrapper path missed trace_id thread; PA
path never creates AgentExecution row)?

**Promotes to.** §8.2 T1 HIGH R.OBSERVABILITY.TRACE-ID-WRITE-COVERAGE.

### 6.3 Writer semantics for `AgentExecution.cost` DecimalField

**Source.** S1703 §20.4 UNK-3.

**Question.** No verified writer at HEAD via verifier-loop grep.
Possibly written by Celery wrapper path at `tasks_agents.py:2311+`
(S1703 Explore 3 asserted; not verified line-by-line).

**Promotes to.** §8.3 T3 R.OBSERVABILITY.COST-ATTRIBUTION-AUDIT.

### 6.4 Watchdog `.update()` + cancel `.update()` signal-silence intent

**Source.** S1703 §20.4 UNK-4.

**Question.** Are watchdog `.update()` + cancel `.update()` paths
intentional signal-silence or accidental gap? Rigby delegation
lifecycle events therefore MISS watchdog-timeout terminals +
cancelled terminals.

**Promotes to.** §8.3 T3 R.OBSERVABILITY.SIGNAL-INSTRUMENTATION-POSTURE.

### 6.5 `RIGBY_DELEGATION_ENABLED` flip milestone

**Source.** S1705 §20.4.

**Question.** Is `RIGBY_DELEGATION_ENABLED` intended to flip ON at
any specific milestone (Employee OS Phase 2 posture, S1268 comms
sketch adoption, Employee #4 authority-level enforcement)? Blocks
Option B posture evaluation at Cat E until decided.

**Promotes to.** §8.2 T1 CRITICAL R.OBSERVABILITY.RIGBY-DELEGATION-FLAG-POSTURE.

### 6.6 Ops-domain beat-wired writer decision

**Source.** S1705 §20.4.

**Question.** Should ops-domain beat-wired writer (`run_ops_autopilot`
+ `post_ops_digest`) be unblocked from AUDIT_FINDINGS.md §12 deferred
list? Per S1705 R10 LOW.

**Promotes to.** §8.3 T3 R.OBSERVABILITY.OPS-AUTOPILOT-BEAT-POSTURE.

### 6.7 F7 SPECULATIVE cold-start "sluggish/paralyzed" (S1273 line 1964)

**Source.** S1706 F7 + §14.3.

**Question.** S1273 line 1964 flagged digestive + muscular systems
report sluggish/paralyzed on fresh DB. Code paths default healthy on
zero-execution baseline (verified S1706). Claim may refer to observed
operational behavior (queue init delays, startup race conditions) not
visible in code logic.

**Promotes to.** §8.4 non-blocking S1706 R9 LOW — Employee OS or
body-systems reliability project (not Group 1700 scope).

### 6.8 4-employee morning brief cross-day similarity + content quality

**Source.** Cross-arc concern from `feedback_content_presence_vs_quality.md`
memory rule + S1705 §20.4 fail-rate framing.

**Question.** Cat E producer discipline is verified but Cat E consumer
side (Chief of Staff morning brief output content quality across
days) is not evaluated by any Group 1700 child. Deferred to Employee
OS continuous audit.

**Promotes to.** §8.4 non-blocking cross-arc concern (Employee OS
scope, not Group 1700 T-slot).

### 6.9 Fleet-application observability sweep

**Source.** Parent §7 anti-scope item 13.

**Question.** Fleet apps have their own telemetry; Group 1700 scope
was unified-donkey-betz only. Do fleet apps replicate the same
retention-posture gap + correlation-spine gap?

**Promotes to.** §8.4 non-blocking cross-arc concern (Fleet-audit
arc if opened; not Group 1700 T-slot).

---

## 7. Anchor-Update Recommendations

Concrete proposed edits owed to the post-arc PR bundle. Playbook
§16 rule: xx99 does NOT edit anchors directly; the ARCHITECTURE_INDEX
v-bump commit applies them.

### 7.1 PLATFORM_INVENTORY.md

- **Body Systems 9 → 10** — regenerate via `python manage.py refresh_doc_inventory_blocks`
  (autoblock) AND `python manage.py generate_platform_inventory`
  (Body Systems body-of-doc section headline). Source: S1706 F2 +
  §14.1.
- **Employees 3 → 4** — same regen commands. Add `bug_triage_specialist`
  to the count. Source: S1705 F3 + §14 D1/D2.
- **Optional: annotate 3 AgentExecution class-registry rows** — 1
  live (`core.AgentExecution`, `.count()` = production) + 2 dormant
  (`agents.AgentTaskExecution` = 0 rows S1244 rename;
  `intelligence.ActionPlanExecution` = 0 rows S1243 rename). Chris-gated;
  low priority. Source: S1703 D6 LOW.

### 7.2 PLATFORM_WHAT_IT_IS.md

- **Employees 3 → 4** — narrative anchor. Source: S1705 F3.
- **OpenAI hardening section (lines 436-462)** — potential update to
  cross-reference Cat B wrapper adoption (23 sites) + F1 dual-model
  posture pending xx99. Source: S1702 F1/F2/F5.
- **Cat D consumer surface narrative** — add ToolCallRecord section
  describing 3-writer producer path + F1 100% NULL trace_id + F4
  dark pipeline. Source: S1704 D3.
- **Optional: reframe S1273 §5.13 5-layer execution-telemetry dedup
  narrative** to "correlation-spine-plus-retention posture" per
  §5.4 canonical verdict. Chris-gated; not blocking. Source: §5.4.

### 7.3 ARCHITECTURE_INDEX.md (v49 → v50)

- **§1.53 S1799 registration row** — Group 1700 xx99 canonical summary.
- **§8 timeline S1799 row.**
- **Line-6 v50 preamble** — bump version + summarize S1799 addition.
- **§8 timeline table drift** — add missing rows for S1605 Cat E +
  S1606 Cat F + S1699 xx99 (all Group 1600; inherited from Group 1600
  §8 timeline drift per S1706 §14.4). Owed to follow-up docs PR OR
  bundle with S1799 PR (recommended: bundle).

### 7.4 Other affected docs

- **Parent scoping `1700_observability_domain_scoping.md`:**
  - §3 A signal-handler line-range `:74-177` → `:74-300` + 3 → 5
    handler count (S1701 F2).
  - §3.B field list — disambiguate LLMCallEvent vs LLMCallLog
    (S1702 F6 + §5.7).
  - §3.C "BaseAgent's `route()` wrapper" → "`AgentRouter.route`
    with BaseAgent delegation via property accessor" (S1703 D2 +
    §5.8).
  - §3.C `core/services/execution_tracker.py` line — file does not
    exist; remove or clarify as `ai_core/agents/execution_tracker.py`
    (Redis-based, no DB writes) (S1703 D3).
  - §3.C 3-class AgentExecution landmine — reframe from "3 live classes"
    to "1 live canonical + 2 dead-code source files pending post-arc
    cleanup + 1 renamed cross-app compatibility shim (S1244) + 1
    renamed intelligence-app class (S1243)" (S1703 D4 HIGH + §5.8).
  - §5 F5 correlation-primitive HYPOTHESIS box — record 5 verdicts
    per §5.5 (task_id VERIFIED / execution_id REVISED / trace_id
    PARTIALLY REVISED / tool_call_id REFUTED / mission_id CONFIRMED).
  - §5.E CTO/COO/Trend Analysis daily reference — reframe as "beat-wired
    threshold-gated alert escalators consuming Cat A/B/C layers; NOT
    OpsRunEvent consumers" (S1705 F4 + F5 + §5.2).
  - §5.F six sub-slots wording — actual is 5 (F.a/F.b/F.c/F.d/F.e)
    per S1706 R10 LOW.
  - §5.F `check_learning_loop_slo` line 12492 → 13170 (S1706 F3 +
    §5.11).
- **`core/models_unified_system.py:882-887`** — S287 deprecation notice
  reversed (S1703 F2 CRITICAL + §5.8). Docstring should say "LIVE
  CANONICAL as of S1084; agents.AgentExecution renamed to
  AgentTaskExecution S1244; intelligence dead-code cleanup pending
  post-arc T-slot ADR." **Not an anchor edit per se** — this is a
  source-code docstring; owed to same PR bundle or follow-on cleanup PR.
- **`docs/topics/employee-os.md:64-65`** — `evidence_for_mission`
  join surface named-but-broken for ToolCallRecord side. Add caveat
  paragraph pointing at S1705 F7 + S1704 F1 blocker until Cat D
  trace_id write-coverage repair lands (S1705 D4 HIGH).
- **`docs/topics/agent-system.md:107-113`** — S970 auto-wrap coverage
  claim MISLEADING: covers 52/83 override subclasses only, not "every
  subclass" as narrative implies (S1704 D2 MEDIUM). Split narrative
  into "S970 wraps overriders (52) + BaseAgent default's S1085 inline
  recorder covers base-inherited (31)."
- **`docs/topics/personal-assistant.md`** — 0 ToolCallRecord narrative
  currently; add F6 coverage story (PA path writes 907 rows / 22% of
  Cat D via dispatcher) (S1704 D3 MEDIUM).
- **`docs/EMPLOYEE_OS_PRIMITIVES.md`** — 1-2 sentence canonical note
  "OpsRunEvent is producer-only at HEAD" per S1705 R6 MEDIUM +
  Rigby SIGN cycle 1 Q4(c) fold. Add to §1 or as inline footnote.
- **`docs/AUDIT_FINDINGS.md §12`** — validate zero-fire probe against
  new observability retention debt from CX-P1. Post-arc governance.

### 7.5 Cross-arc anchor-update inheritance

- **S1704 D4 + D5 + D8** — carries as follow-up docs PR items after
  S1799 close (S1699 §7.4 auto_publish "daily 6 AM" cross-arc
  CORRECTION owes 5 doc PRs; not this session per scope discipline).
- **Group 1400 + Group 1500 + Group 1300 post-arc §7 anchor-updates**
  remain pending (inherited from prior arc-close discipline; not
  Group 1700 scope).

### 7.6 Regeneration commands owed post-merge

Per memory rule `feedback_docs_cascade_at_every_close.md`:

1. `python manage.py build_docs_index`
2. `python manage.py build_rag_corpus`
3. `python manage.py sync_docs_index_to_documents`
4. `python manage.py sync_docs_index_to_documents --embed` (or
   `python manage.py embed_documents --all-unembedded`)
5. `python manage.py build_docs_provenance`
6. **Additional per §7.1 / §7.3:** `python manage.py generate_platform_inventory`
   + `python manage.py refresh_doc_inventory_blocks` for body-systems +
   employees regeneration.

---

## 8. Follow-On Research Queue

Ranked next-mission list. Playbook §11.3 rule: xx99 §8 output is
the **unified queue** consolidating all six children's §19 R-slots
+ new cross-cutting items surfaced by §4 CX-patterns + parked
candidates promoted from parent §6.

Ordering: **T0/Gate** (Chris-gated posture decisions blocking downstream)
→ **T1 CRITICAL / HIGH** (unblocked once T0/Gate ratified) →
**T2/T3 MEDIUM** → **T3 LOW / non-blocking**.

### 8.1 T0/Gate — Chris-gated posture decisions

**Both T0/Gate items block downstream T1 remediation.** xx99 produces
evidence briefs; Chris ratifies posture. Per D73 posture-framing
discipline.

#### T0/Gate item 1 — R.OBSERVABILITY.RETENTION-UNIFIED-ADR

- **Question.** Should the Group 1700 six-Cat retention posture be
  a **single unified ADR** spanning A-F, or per-Cat retention specs?
- **Evidence base.** §4.1 CX-P1 + S1706 F1 (HIGH) + S1706 §20.8
  handoff note + Cat A / FleetEvent / LearningReadbackEvent
  peer-exemplars.
- **Recommended defaults** (Chris ratifies or overrides):
  - Cat A CeleryTaskEvent = 30-day (existing).
  - Cat B LLMCallEvent = 30-day (matches LLMCallLog sibling).
  - Cat C AgentExecution = 30-90-day (Chris picks based on
    postmortem window preference).
  - Cat D ToolCallRecord = 30-day (matches Cat A cadence).
  - Cat E OpsRun / OpsRunEvent = 90-day (mission audit window).
  - Cat F.a HeartBeat = 30-day (matches LearningReadbackEvent).
  - Cat F.c DeliverableEvent + OpsRunEvent = 90-day (business-lifecycle).
  - Other 11 Cat F.c event models = per-model Chris ratification
    (Group 1900 owns after Cat F handoff).
- **Blocks.** All T1 retention-implementation items (§8.2 T1
  medium-priority items).

#### T0/Gate item 2 — R.OBSERVABILITY.D74-SPINE-POSTURE

- **Question.** Select among Option A (execution_id spine) / Option
  B (trace_id spine) / Option C (shared correlation view) / Option D
  (hybrid).
- **Evidence base.** §4.2 CX-P2 + S1701 F5 + S1702 F9 + S1703 F9 +
  S1704 F1/F9 + S1705 F1/F9 + S1706 F9.
- **Load-bearing constraint per Rigby SIGN cycle 1 F2 fold at S1706:**
  Retention must be a first-class field in the spine ADR regardless
  of posture selected. This means the T0/Gate items are **paired** —
  Chris cannot ratify D74 without also ratifying retention posture
  in the same ADR (or explicitly deferring retention as a follow-on
  ADR).
- **Blocks.** T1 CRITICAL PA coverage + trace_id write-coverage +
  correlation-column additions (§8.2).

### 8.2 T1 CRITICAL / HIGH — Unblocked once T0/Gate posture ratified

#### T1 item 1 (CRITICAL) — R.OBSERVABILITY.PA-COVERAGE-POSTURE

- **Origin.** S1702 F2 CRITICAL + S1703 F4 CRITICAL + §4.3 CX-P3.
- **Question.** Should the PA agentic loop route through
  `llm_call_span` and write AgentExecution rows per turn? Or does PA
  deserve its own telemetry model?
- **Chris-gated at.** T0/Gate 2 posture; can be blockers-first.
- **Estimated scope.** 1-2 sessions code work + 1 session Rigby SIGN
  (design decision on per-iteration vs per-message span).

#### T1 item 2 (CRITICAL) — R.OBSERVABILITY.TRACE-ID-WRITE-COVERAGE

- **Origin.** S1704 F1 CRITICAL (100% NULL trace_id at 4144 rows) +
  Rigby SIGN cycle 1 F4 fold at S1704 (gating prerequisite for
  Option B posture evaluation).
- **Question.** Repair Cat D trace_id write coverage: dispatcher must
  generate real UUID trace_id (replacing `td-N-hex` string), S970
  wrapper must thread from execution context, base default must
  thread from context, PA loop must convert `pa-N-hex` → UUID.
  Coordinated 3-writer change plus regression test coverage.
- **Blocked-by.** Only meaningful IF T0/Gate 2 selects Option B or
  Option D. But even if Option A, the trace_id column stays and its
  NULL rate should be documented (drop as-is OR delete column).

#### T1 item 3 (CRITICAL) — R.OBSERVABILITY.EVIDENCE-FOR-MISSION-REPAIR

- **Origin.** S1705 F7 MEDIUM + S1705 D4 HIGH + §5.10.
- **Question.** Repair Cat E `evidence_for_mission` ToolCallRecord
  join. Cross-cat: depends on Cat D correlation primitive population
  (S1704 F1/F2) and Cat C PA coverage (S1703 F4). Not solvable at
  Cat E alone. Rigby SIGN cycle 1 Q4(b) fold: HIGH as Chris-facing
  operator-surface contract breach.

#### T1 item 4 (CRITICAL) — R.OBSERVABILITY.RIGBY-DELEGATION-FLAG-POSTURE

- **Origin.** S1705 F1 DESIGN-INTENT-LATENT + §6.5.
- **Question.** Decide `RIGBY_DELEGATION_ENABLED` posture: flip ON
  (unblocks Cat E-side Option B evidence via execution_id detail-JSON
  thread) OR repair Cat D-side first (T1 item 2). Rigby SIGN cycle 1
  Q4(a) fold at S1705: sequence AFTER T0/Gate 2 posture to avoid
  producing evidence against obsolete spine choice. Q4(d) scope
  discipline: xx99 records as evidence-plan decision; do NOT
  implement/flip flags during arc-close per playbook §14.5.

#### T1 item 5 (HIGH) — R.OBSERVABILITY.MULTI-MODEL-DEDUP-POSTURE

- **Origin.** S1702 F1 CRITICAL + §5.7 anchor drift.
- **Question.** Intended split between LLMCallEvent (S1098) +
  LLMCallLog (S697) + CostTracking. Is one deprecated? Are all three
  canonical for different concerns? Consolidation implementation is
  post-arc T-slot per D73.

#### T1 item 6 (HIGH) — R.OBSERVABILITY.MULTI-MODEL-DEDUP-CAT-B-RETENTION

- **Origin.** S1702 F4 HIGH.
- **Question.** LLMCallEvent retention posture (paired with T0/Gate
  1 unified ADR): analog to Cat A's 30-day, or intentional
  retain-forever for postmortem per S1098 wrapper docstring? xx99
  candidate for D74 axis if posture ties to F1 dedup.

#### T1 item 7 (HIGH) — R.OBSERVABILITY.SLO-FRAMEWORK-SCOPE

- **Origin.** S1706 F5 MEDIUM + R3 MEDIUM.
- **Question.** Follow-on design-preparation arc scoping. Requires:
  `ServiceLevelObjective` model spec, historical audit table, registry
  pattern, breach-alert wiring. Parent §6.1 parked candidate. Chris
  ratifies at xx99 whether SLO design becomes a T0/Gate ADR or a
  later arc.

#### T1 item 8 (HIGH) — R.OBSERVABILITY.DOC-VERIFIER-INTEGRATION

- **Origin.** S1706 F6 DESIGN-INTENT-LATENT + R4 MEDIUM.
- **Question.** Chris-gated ADR on whether doc-verifier drift is a
  first-class telemetry signal. Post-xx99. Requires: `DocClaimDrift`
  model spec, continuous-emission wiring, CI gate policy, alert
  threshold.

#### T1 item 9 (HIGH) — R.OBSERVABILITY.TERMINOLOGY-RATIFICATION

- **Origin.** S1706 F8 MEDIUM + R5 MEDIUM.
- **Question.** Chris ratifies (or overrides) the PERMEABLE-with-producer/consumer-split
  terminology recommendation as the Group 1700 canonical stance.
  Feeds Group 1900 arc-open scoping.

### 8.3 T2 / T3 MEDIUM

- **T2 item 1 (S1701 R2)** — Monitor-task probe-decomposition root
  fix (S1167 top_consumers exposed monitor tasks at p95=1048s /
  1880s). Blocked on someone owning the design.
- **T2 item 2 (S1701 R3)** — agent_name backfill % measurement +
  backfill decision (S1169 no-backfill stance).
- **T2 item 3 (S1701 R4)** — Retention-cleanup failure detection
  (T3 event gap).
- **T2 item 4 (S1702 R4)** — `_extract_usage` Gemini + Ollama provider
  shape completeness (P0 pre-emptive fix per §22 default queue lean
  addition).
- **T2 item 5 (S1702 R7)** — MissionRunner LLM-cost attribution
  (thread `mission_id` into `llm_call_span.metadata` + GIN index).
- **T2 item 6 (S1703 R2)** — F1 + F2 landmine + docstring cleanup
  ADR (delete 2 intelligence-side dead files + rewrite S287 docstring).
- **T2 item 7 (S1703 R4)** — Dedicated PA `execution_history_tool` +
  admin registration + `.update()` signal instrumentation.
- **T2 item 8 (S1703 R5)** — 3-hop correlation chain implementation
  (GIN index on `AgentExecution.input_data->>'celery_task_id'` OR
  shared correlation view OR status quo).
- **T2 item 9 (S1703 R6)** — Retention policy for AgentExecution
  (pairs with T0/Gate 1).
- **T2 item 10 (S1704 R3)** — F4 mining + aggregation pipeline
  reactivation (add beat entries for `analyze_pa_tool_patterns` +
  `aggregate_tool_call_stats`; validate 480MB spike behavior).
- **T2 item 11 (S1704 R6)** — F3 base-inherited-agent activity
  audit (29 of 31 zero-row; SPECULATIVE distribution).
- **T2 item 12 (S1704 R7)** — F6 PA path + F3 conversation_id
  backfill (21.9% coverage; retro-backfill via task_summary parsing).
- **T2 item 13 (S1704 R8)** — PA tool for tool-call history query
  (`tool_call_history_tool`).
- **T2 item 14 (S1705 R3)** — F7 evidence_for_mission join repair
  (paired with T1 item 3).
- **T2 item 15 (S1705 R4)** — F2 schema-level correlation columns
  (paired with T0/Gate 2 Option A).
- **T2 item 16 (S1706 R6)** — F2 body-system inventory refresh
  (§7.1 anchor-update).
- **T2 item 17 (S1706 R7)** — F4 ABTestEvent orphan disposition
  (Group 1900 territory).
- **T3 item 1 (S1701 R6)** — RSS measurement platform-quirk test
  coverage.
- **T3 item 2 (S1701 R7)** — Realtime WebSocket push of
  task-lifecycle events (blocked on Group 1900 event architecture).
- **T3 item 3 (S1701 R8)** — 8 downstream models `celery_task_id`
  FK reconciliation.
- **T3 item 4 (S1702 R5)** — S1224 budget-exhausted observability
  (`error_type='budget_exhausted'` bucket + wrapper-side detection).
- **T3 item 5 (S1702 R8)** — Best-effort telemetry silent-failure
  metric (`LLM_CALL_EVENT_SAVE_ERROR_TOTAL` counter).
- **T3 item 6 (S1702 R9)** — Realtime WebSocket push of LLMCallEvent
  (analog to S1701 R7; blocked on Group 1900).
- **T3 item 7 (S1702 R10)** — Documentation gap — dedicated
  `docs/topics/llm-telemetry.md` (post-xx99 once F1 dedup posture
  decided).
- **T3 item 8 (S1703 R7)** — CASCADE vs SET_NULL on Agent + User FKs
  (archive-friendliness vs GDPR-alignment).
- **T3 item 9 (S1703 R8)** — tokens_used + cost denorm reconciliation.
- **T3 item 10 (S1703 R9)** — Dead-code sweep for
  `core/agent_execution_wrapper.py` (97 lines).
- **T3 item 11 (S1703 R10)** — `AgentTaskExecution` posture (0 rows
  since S1244 rename).
- **T3 item 12 (S1704 R9)** — Django admin registration.
- **T3 item 13 (S1704 R10)** — Dead-code cleanup (after cross-repo
  fleet-caller verification).
- **T3 item 14 (S1704 R11)** — Non-BaseAgent overrides
  (`personal_ai_assistant_enhanced.py:1297` + `assistant/base.py:172`).
- **T3 item 15 (S1704 R12)** — PAToolInsight dedup enforcement
  (`unique_together = ['tool_name','insight_type','pattern']`).
- **T3 item 16 (S1705 R8)** — `tasks_ops.py` extraction status audit.
- **T3 item 17 (S1705 R9)** — Admin registration for OpsRun / OpsRunEvent.
- **T3 item 18 (S1705 R10)** — Ops-domain beat-wired writer decision.
- **T3 item 19 (S1705 R11)** — F4 daily diagnostics consume
  OpsRunEvent decision.
- **T3 item 20 (S1705 R12)** — MissionRunner I1-I9 contract test
  regression prevention.
- **T3 item 21 (S1706 R10)** — F3 parent scoping / start-here
  line-cite refresh (paired with §7.4 anchor-update tranche).

### 8.4 Non-blocking (post-arc research or cross-arc)

- **S1706 R8 (LOW, non-blocking)** — F7 HeartBeat export UI wiring
  (parent §6.5 parked; Chris-gated post-xx99).
- **S1706 R9 (LOW, non-blocking)** — F7 SPECULATIVE cold-start
  behavior verification (Employee OS or body-systems reliability
  project; not Group 1700 scope).
- **§6.8 4-employee morning brief cross-day quality** — Employee OS
  continuous audit, not Group 1700 T-slot.
- **§6.9 Fleet-application observability sweep** — Fleet-audit arc
  if opened.

### 8.5 Cross-arc inheritance from prior arcs

Preserved from prior arc close-outs; not resolved by Group 1700:

- **Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E**
  blocks 20 T1 items.
- **Group 1500 T1 R.SPORTS.POSTURE + R.DBAO.CODENAME** Chris-gated ADRs.
- **Group 1500 T1.h SportsBettingBrief consumer-or-remove.**
- **Group 1400 R.B1 OutreachDraft delivery.**
- **Group 1400 T1-T10** unified follow-on queue (still pending).
- **Group 1300 21 follow-on items** (still pending).

---

## 9. Cross-Links to Delegated Arcs

Every `delegates_to:` entry from the parent gets a callout with what
Group 1700 evidence informs the delegated arc.

### 9.1 Group 1900 Event Architecture (parent D2 delegation)

- **Delegation scope.** Event bus adoption, cross-domain event
  routing / schema versioning, DeliverableEvent + ImpactEvent +
  EngagementEvent producer-consumer contracts.
- **Group 1700 evidence for Group 1900:**
  - **Cat F.c 14-model event-shape catalog** (S1706 §4.2). Producer/consumer
    matrix ready for Group 1900 arc-open consumption; 12/14
    WIRED-BOTH-SIDES + 1 PRODUCER-ONLY-BY-DESIGN + 1 orphan (ABTestEvent).
  - **Cat F.e terminology posture** (S1706 F8): PERMEABLE-with-producer/consumer-split
    recommendation feeds Group 1900 arc-open scoping. Chris ratification
    at Group 1900 open per T1 item 9.
  - **Cat A/B/C/D/E "passive telemetry sink" posture** — every audited
    Cat verified as NOT emitting domain events (no `post_save`
    publishers to EventBus, no channel_layer, no Kafka producer).
    Cross-boundary confirmation for Group 1900 that current
    execution-telemetry layers do NOT require immediate event
    architecture repair; the writer discipline is CONSUMER-COMPATIBLE
    once event bus lands.
  - **Cat E producer-only role** (S1705 F5): OpsRunEvent is
    PRODUCER-ONLY. If Group 1900 introduces cross-table correlation
    IDs at Cat E schema + adds explicit aggregation pipeline reading
    OpsRunEvent detail JSON, Cat E could evolve to "producer +
    consumer." Post-arc T-slot.

### 9.2 Group 1600 Content T0/Gate R.CONTENT.XX99-ADR-BUNDLE (parent §7 anti-scope item 3)

- **Delegation scope.** DeliverableEvent consumer contract disposition.
- **Group 1700 evidence for Group 1600 T0/Gate:**
  - **Cat F.c row 1 DeliverableEvent** (S1706 §4.2) verified as
    WIRED-BOTH-SIDES: producer at `deliverable_status_signals.py:205`;
    consumers at `ops_autopilot/intelligence.py` + `diagnostics/coo_daily.py`
    + `views_deliverables.py` + `employees/status.py`. Group 1600
    T0/Gate can proceed on the D65A/D65B/D65C/D65E ADR knowing the
    producer side is intact + retention gap will be addressed by
    Group 1700 T0/Gate 1 unified ADR.
  - **Retention posture inheritance** — DeliverableEvent lacks
    date-based purge (S1706 F1). Group 1600 T0/Gate should either
    resolve retention concurrently OR explicitly delegate to Group
    1700 T0/Gate 1.

### 9.3 Group 1300 Memory (parent D2 delegation)

- **Delegation scope.** AgentMemory + UserAgentLearning writer
  telemetry is Group 1700 scope; Memory learning-loop business logic
  is Memory internal.
- **Group 1700 evidence for Memory:**
  - **Cat C `execution_id` scalar downstream: `UserAgentLearning`**
    (S1703 §4 FK graph) — Memory carries `execution_id` UUIDField
    scalar non-FK per Cat C posture. If Group 1700 T0/Gate 2 selects
    Option A execution_id spine, Memory writer discipline aligns as
    downstream consumer.

### 9.4 Employee OS (concurrent, not a separate arc)

- **Delegation scope.** MissionRunner + AIEmployee + JobContract own
  mission execution; MissionRunner internal correctness is Employee
  OS.
- **Group 1700 evidence for Employee OS:**
  - **S1705 F8 POSITIVE — MissionRunner I1-I9 invariants VERIFIED**
    at HEAD via source read + contract test at
  `test_mission_runner.MissionRunnerImportContractTests`. Employee
    OS Phase 2 posture reads on solid mission-lifecycle foundation.
  - **S1705 F7 named-but-broken evidence_for_mission** — cross-cat
    join repair depends on Cat D trace_id write-coverage (T1 item 2)
    + `parameters.ops_run_id` threading from MissionRunner to
    dispatcher context. Not solvable at Employee OS alone.
  - **§6.8 cross-day content quality** — Employee OS continuous audit
    (not Group 1700 T-slot).

### 9.5 Group 1400 Revenue (S1499 canonical)

- **Delegation scope.** R.A2 follow-on cites LLMCallEvent for
  scoring-rate telemetry probe. Group 1700 evidence:
  - S1702 F2 CRITICAL PA coverage gap has implication for
    OpportunityDraftGenerator (Revenue Cat B agent per S1401) —
    UNKNOWN whether it routes through `llm_call_span` at HEAD; owed
    to xx99 evidence. §6.1 UNK-1 tracked.

### 9.6 Group 1500 Sports (S1599 canonical)

- **Delegation scope.** F.B1 fold: 4 of 5 sports pipeline agents use
  `.execute()` (bypasses AgentExecution row). Group 1700 evidence:
  - S1702 F2 CRITICAL — LLM calls from those agents (if wrapped)
    write `LLMCallEvent.execution_id=NULL`. Cost attribution for
    sports agents is degraded (SPECULATIVE). Feeds Group 1500's
    consumer-side unblock decision at Group 1500 T1.h.

### 9.7 Cross-domain audit `platform/cross_domain_integration_audit.md` §14

- **Cross-arc consumption.** S1705 §9.4 read §14 v3 refresh; §14.7
  explicitly reserves §14.8 for Group 1700 xx99 close consumption at
  S1799. **This xx99 close is the trigger for the §14.8 append.**
  Owed to follow-up docs PR bundle:
  - §14.8 header + CX-P1 through CX-P7 evidence pointers into this
    xx99 §4.
  - Cross-arc pattern inheritance from Groups 1300/1400/1500/1600
    validated: CX-P1 (retention discipline) is a Group 1700 restatement
    of Group 1500 F.B3 WRITE-ONLY-FORGOTTEN + Group 1600 D65-family
    retention concerns.

---

## 10. What This Research Taught Us About How to Do Research

Meta-methodology retrospective. Playbook v3 §11.3 §10 template
FIFTH application (adopted S1399 Chris directive 2026-07-01; second
S1499; third S1599; fourth S1699). Distinct from §4 Cross-Cutting
Patterns (about the domain) and §11 Arc Change Log (retrospective
ledger of what happened). §10 is what future arcs learn from this
one.

### 10.1 What worked (methodology validated across this arc)

**MW-1 — Parent-Claude verifier-loop for every load-bearing binary
claim.** Applied both pre-Explore (to seed sub-agent premises with
verified anchors) AND post-Explore (to sanity-check sub-agent
returns). Six children × ≥2 verifier-loop passes each = 12+ verifier
sweeps across the arc. Landed **≥8 material corrections** per
§12.3 canonical enumeration — that would have shipped as
false-positive load-bearing findings otherwise. Playbook §14
verifier-loop discipline is the strongest quality gate in the arc.

**MW-2 — Single-batch 4-question SIGN pattern.** Each of six children
(and this xx99) applied single-batch 4-question Rigby SIGN cycle
per S1600 established pattern. D48 preemptive stability-probe gate
held clean through 23 arms S1503-S1706 (18-consecutive-fully-clean-arms
sub-pattern per S1503-S1706). Feedback: rigby_sign_worker_instability
recovery threshold pattern remains defensible.

**MW-3 — Sequential parent → child → child → ... → xx99 cadence with
D3 parent-only-this-session rule.** 8-doc arc target (S1700 parent
+ S1701-S1706 six children + S1799 xx99) matches S1499 / S1599 /
S1699 precedent. No parallel-child execution attempted. Chris memory
rule `feedback_no_parallel_research_arcs.md` respected: no other
research arc opened during Group 1700. Cadence held for 8 sessions
across arc close.

**MW-4 — F5 correlation-primitive HYPOTHESIS box at parent §5.**
Parent §5 F5 fold introduced 5 correlation-primitive working
definitions as **HYPOTHESIS-TO-BE-VERIFIED** labeled per primitive
+ named which child audit verifies each. Each child's §9 D74 axis
contribution structured around the parent's hypothesis. §5.5 recorded
5 canonical verdicts (VERIFIED / CONFIRMED / PARTIALLY REVISED /
REVISED / REFUTED). The hypothesis-forwards structure kept each child
disciplined about which axis its evidence targeted.

**MW-5 — Playbook §11.2 template held for six consecutive same-arc
applications.** Zero structural revisions needed across S1701-S1706.
Each child's F1-F9 finding-lock convention was durable; each child's
§19 R1-Rn ranked follow-on-queue convention was durable. Playbook
v3 §11.2 promotion CONFIRMED-STRENGTHENED via sixth application
(fourth arc; CX-P7 pattern).

**MW-6 — Cross-cat evidence-sharing via §9 references to sibling
child audits.** Each child cited prior siblings' F-findings explicitly
in its own §9 integrations table. S1706 §4 cross-cat pattern
inheritance was possible because S1706 was the sixth child. This
enabled the xx99 §4 CX-patterns to consolidate across six children
without re-enumerating audits (playbook §11.3 rule preserved).

**MW-7 — Rigby SIGN cycle 1 folds landed pre-commit for every child.**
No child shipped with unresolved SIGN edits. S1700 parent-scoping
folded F1-F6 pre-commit; S1701 F1-F3; S1702 F1-F3; S1703 F1-F4; S1704
F1-F4; S1705 F1-F7; S1706 F1-F4. This kept the arc `status: active`
transition clean per playbook §16 draft→canonical policy.

### 10.2 What to codify into playbook v3 (per §20 two-triggers rule)

**MC-1 (CODIFICATION-READY at fifth-consecutive-application) —
Playbook §14 verifier-loop pre-Explore + post-Explore is
**required**, not discipline.** MW-1 above demonstrated ≥8 material
corrections in one arc. Prior arcs demonstrated the same pattern
(S1399/S1499/S1599/S1699 all included §14 verifier-loop discipline).
Two-triggers rule was met by S1399+S1499 already; five-consecutive-application
confirms durable. Playbook v3 §14 promotion recommended: change
wording from "verifier-loop discipline" to "verifier-loop **required**
for every load-bearing binary claim; both pre-Explore AND
post-Explore." S1706 §20.1 verifier-loop record serves as template.

**MC-2 (CODIFICATION-READY at S1706 close) —
18-consecutive-fully-clean-arms sub-pattern strengthens playbook
§15 promoted rule.** MW-2 above. D48 preemptive stability-probe gate
has held clean through 23 arms S1503-S1706. Recommendation: promote
S1503-onwards 18-consecutive-fully-clean-arms as **the** default SIGN
routing pattern (single-batch, 4 questions, arc-pin as SIGN pin per
S1600 precedent). Two-triggers threshold long-exceeded; explicit
codification would let future arcs skip re-establishing pattern.

**MC-3 (CODIFICATION-CANDIDATE) — F5 correlation-primitive HYPOTHESIS
box discipline at parent §5.** MW-4 above. Applied ONCE at S1700
parent scoping (Rigby SIGN cycle 1 F5 MUST-FIX fold). Second
application at a future parent-with-children arc would meet
two-triggers threshold. Recommendation: add to playbook §11.1 parent
template as **optional** field for arcs whose D-lens question depends
on cross-child primitive verification (e.g., D74-analog structural-vs-unification
questions). Wait for second application before promoting to
required.

**MC-4 (CODIFICATION-CANDIDATE) — Post-Explore verifier-loop
correction tracking convention (VC1/VC2/VC3 style).** S1703 §14
introduced explicit VC1/VC2/VC3 markers for post-Explore corrections
(vs simple footnote). S1705 §14 continued the convention. Two-consecutive-application
meets two-triggers rule for playbook §14 addition. Recommendation:
promote VC-marker convention to playbook §14 template.

**MC-5 (CODIFICATION-CANDIDATE) — Cross-cat evidence-sharing via
§9 sibling references.** MW-6 above. Each child cited prior siblings'
F-findings explicitly. Enables xx99 §4 consolidation without re-audit.
S1699 (Content xx99) also demonstrated the pattern. Meets two-triggers
threshold. Recommendation: playbook §11.2 template addition — **§9
integrations table should cite specific sibling F-findings when
cross-cat evidence exists**.

### 10.3 What didn't work / anti-patterns to avoid

**AP-1 — Explore Agent claim without file:line grep.** All 7 material
corrections traced back to Explore Agents making claims from partial
package searches OR mis-classified reads. S1706 Agent 3 false-positive
WRITE-ONLY-FORGOTTEN on Cockpit*Event was the most vivid: Agent 3
did not grep `views_diagnostics.py:3889` for consumers before
declaring WRITE-ONLY-FORGOTTEN. **Playbook §13 6-parallel-Explore
should include explicit "grep-verified before load-bearing verdict"
guidance for consumer/orphan claims.** Add to playbook v3 §13 as
addendum.

**AP-2 — Parent §-cite drift caught only at child-audit time.** Cat
A F2 (parent §3 A `:74-177` → `:74-300`); Cat B F6 (parent §3.B
field list drift); Cat C F3 (parent §3.C `route()` wrapper phrasing);
Cat D D7 (parent §5 F5 tool_call_id refuted); Cat F F3 (parent §5.F
line 12492 → 13170) — 5 of 6 children caught parent §-cite drift.
Pattern: parent scoping citations aged even during a single arc as
codebase moved. **Recommendation:** parent scoping doc should include
a **"line-cite freshness date + regeneration protocol"** header at
§7 anchor-update or §appendix. Alternative: use file-name-only cites
in parent for volatile line numbers.

**AP-3 — S1273 baseline framing biased arc focus.** S1273 §5.13
"5-layer execution-telemetry dedup" framing implied writer-path
unification as the load-bearing gap. Arc evidence RE-FRAMED to
correlation-spine-plus-retention posture (§5.4 canonical verdict).
**Baselines that pre-date arcs can misdiagnose mechanisms.**
Recommendation: parent scoping §2 "What existing inventory already
tells us" should include **verify-baseline-framing** step that
explicitly checks whether the S1273/S1274 diagnostic mechanism
survives Cat-by-Cat evidence.

**AP-4 — Occasional Rigby SIGN fold reflex to escalate severity
without runtime evidence.** S1703 D4 (3-class landmine) escalated
MEDIUM → HIGH per Rigby SIGN cycle 1 F2 fold with rationale
"dead-code misclassification is worse than mere wording drift." The
escalation is defensible but reflects Rigby's tendency to
severity-escalate when the anti-pattern is Chris-visible. **Recommendation:**
playbook §15 fold-review checklist should require **runtime evidence
citation for severity escalations** (not just plausibility argument).

**AP-5 — Parent scoping §3 anti-scope lists getting stale within
one arc.** Parent §7 anti-scope items 1-17 (S1700) were all still
respected at S1706 close, but two new items surfaced at S1706 §16.1
via Rigby SIGN Q1 fold (resolve_node telemetry / memory_pressure /
fleet auth / RIGBY_*_INTAKE_ENABLED siblings) that weren't in
parent §7. Not a blocker — the SIGN fold caught them — but suggests
parent §7 should be **regenerable** at mid-arc via a fresh
verifier-loop pass, not fixed at parent close.

### 10.4 Suggestions for the playbook itself

**PS-1 — Add §11.3 §10 to CX-P summarization pattern.** Current
playbook §11.3 §10 covers meta-methodology retrospective. §4
Cross-Cutting Patterns is separate (about the domain). But some
patterns (this arc's CX-P4 boundary-discipline-intact + CX-P6
consumer-partial-wiring-systemic) are simultaneously domain-shape
observations AND research-method observations. **Recommendation:**
add cross-reference discipline — CX-Pn items that carry
methodological weight should cite a §10.n meta-methodology
observation and vice-versa.

**PS-2 — §11.3 §5 Resolved Contradictions section could be split
by kind.** This xx99 §5 has 11 resolutions spanning (a) Explore-Agent-vs-runtime
(3 items); (b) Explore-Agent-vs-Explore-Agent (2 items); (c) baseline
S1273-vs-arc-evidence (1 item); (d) parent-scoping-vs-child-audit
(6 items); (e) anchor-vs-runtime (2 items). Categorization would
make the section navigable + easier to consume in future arcs.
**Recommendation:** playbook §11.3 §5 template should include
sub-heading convention: §5.a Explore-Agent-vs-Explore-Agent, §5.b
Explore-Agent-vs-runtime, §5.c Parent-scoping-vs-child, §5.d
Anchor-vs-runtime, §5.e Baseline-vs-arc.

**PS-3 — §11.3 §8 T0/Gate / T1 / T2 / T3 tier structure was
scale-load-bearing at Group 1700.** 60+ follow-on items (§8.3 T2/T3
alone lists 34; §8.5 cross-arc inheritance adds more). Without tier
structure, the queue would be unnavigable. **Recommendation:** promote
T0/Gate / T1 / T2 / T3 tier convention from S1499 (originating in
Revenue xx99) to playbook §11.3 §8 explicit template.

**PS-4 — §11.3 §10.4 self-suggestion section itself is a good
pattern.** This subsection makes each xx99 an opportunity for
playbook evolution. **Recommendation:** keep the "§10.4 Suggestions
for the playbook itself" as **non-negotiable** in every xx99 per
§11.3 §10 template.

### 10.5 Suggestions for future canonical summaries (optional)

**FS-1 — Include a "recommended reading order" appendix.** Group
1700 xx99 is ~2000 lines. Chris + future Claude reading the doc
cold should have a suggested reading path: §1 executive → §3 domain
shape → §4 CX-patterns → §8 T0/Gate → then §7 anchor-updates →
§10 meta-methodology → deep sections as needed.

**FS-2 — Add a "one-sentence-per-child" §2 addition.** Current §2
per-child rollup is thorough but long. A single-sentence "what this
child answered" preamble per §2.n subsection would help scan.

**FS-3 — When D-lens question posture is unresolved at xx99 close
(as here for D74 A/B/C/D), consider a "decision one-pager"
supplementary artifact.** xx99 §5 posture-decision brief for D74 is
scattered across §4.2 + §8.1 T0/Gate 2 + §5.5 evidence. Chris would
benefit from a single ADR-shaped one-pager consolidating: question,
4 options, evidence per option (from arc), tradeoffs, recommended
default (or "no default"), gating dependencies. Not required in xx99
per playbook §11.3 rule; could be xx99 §appendix.

---

## 11. Arc Change Log

Historical ledger. Which child, which session, which Rigby verdict,
which fold edits.

### 11.1 S1700 (2026-07-02) — Parent scoping (Chris D69-D74 locks)

- **Doc.** `1700_observability_domain_scoping.md` (1071 lines pre-fold;
  ~1200 lines post-fold).
- **Category.** `parent_scoping`.
- **Chris D-locks.** D69 (parent shape) + D70 (six categories A-F) +
  D71 (delegation boundary with Group 1900) + D72 (P1-P6 sequential
  + P7 xx99) + D73 (posture-decision framing = evidence plan) + D74
  (arc lens: structural separability vs canonical unification). All
  6 verdicts ratified via "agree all + SIGN" round.
- **Rigby SIGN cycle 1.** Light SIGN routed per playbook §15 stage-table
  parent row (default: optional; Chris ratified light SIGN). SIGN-with-edits
  at High confidence. 4-question single-batch. Verdicts: Q1 CONFIRM,
  Q2(i) CONFIRM+F1, Q2(ii) FLAG-EDIT+F2, Q2(iii) FLAG-EDIT+F3, Q3(i)
  CONFIRM, Q3(ii) MUST-FIX+F4, Q3(iii) CONFIRM, Q4 MUST-FIX+F5+F6.
- **F1-F6 folds landed pre-commit.** F1 (Cat C write-path boundary
  sentence); F2 (Cat F sub-slots F.a-F.e with stop conditions); F3
  (Cat B/Cat D LLM-in-tool accounting rule); F4 (P5 dependency clause
  P1+P3+P4 → P1+P2+P3+P4); F5 (§5 correlation-primitives working-definitions
  box with 5 HYPOTHESIS-labeled primitives); F6 (§7 anti-scope items
  19/20/21).
- **D48 preemptive stability-probe gate.** 17th arm HOLDING CLEAN
  through parent SIGN.
- **Arc pin minted.** `pa-e7fbacc996b34b44` via `session_tool.create_fresh`.

### 11.2 S1701 (2026-07-03) — Cat A CeleryTaskEvent (P1)

- **Doc.** `1701_observability_cat_a_celery_task_event_audit.md` (1079
  lines post-fold; HEAD `b8194e24`).
- **Category.** `child_audit`.
- **6 load-bearing findings F1-F6 locked** per §2.1.
- **Rigby SIGN cycle 1 SIGN-with-edits at High confidence.** F1 MEDIUM
  boundary terminology (cross-cat exception vs parallel writer);
  F2 LOW 7→8 downstream count consistency; F3 LOW D10 severity
  footnote. All folds landed pre-commit.
- **D48 18th arm HOLDING CLEAN** — 13-consecutive-fully-clean-arms
  sub-pattern established (S1503-S1701).
- **Fresh SIGN isolation pin.** `pa-3147aef9db4945ac` minted per
  §15; routed-around by wrapper hard-code at `tools/pa_local.sh:128`
  (S1600 precedent); retired at S1701 close per §16.

### 11.3 S1702 (2026-07-03) — Cat B LLMCallEvent (P2)

- **Doc.** `1702_observability_cat_b_llm_call_event_audit.md` (1106
  lines post-fold; HEAD `2bb196e8`).
- **9 load-bearing findings F1-F9 locked** per §2.2.
- **Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence.**
  F1 LOW CostTracking added to §17 as third LLM-cost store;
  F2 (additional folds per S1702 §20.6).
- **D48 19th arm HOLDING CLEAN** — 14-consecutive-fully-clean-arms
  sub-pattern.
- **Fresh SIGN pin.** `pa-c3927ab78c52479a` minted, routed-around,
  retired.

### 11.4 S1703 (2026-07-03) — Cat C AgentExecution (P3)

- **Doc.** `1703_observability_cat_c_agent_execution_audit.md` (1030
  lines post-fold).
- **9 load-bearing findings F1-F9 locked** per §2.3.
- **Rigby SIGN cycle 1 SIGN-with-edits at High confidence.** F1
  trace_id writer-of-record + propagation clarification (§9
  addition); F2 D4 severity escalated MEDIUM → HIGH (dead-code
  misclassification risk); F3 F9 wording tightening on `task_id`
  spine claim vs Cat C spine candidates; F4 boundary-guard on R2
  scope (Cat C does NOT author deprecation ADR).
- **D48 20th arm HOLDING CLEAN.**
- **Fresh SIGN pin.** (name; retired).

### 11.5 S1704 (2026-07-03) — Cat D ToolCallRecord (P4)

- **Doc.** `1704_observability_cat_d_tool_call_record_audit.md` (1033
  lines post-fold).
- **9 load-bearing findings F1-F9 locked** per §2.4.
- **Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence.**
  F1 wording tightened on schema-lift vs coordination-lift decomposition
  for Option B; F2 D7 severity escalated MEDIUM → HIGH; F3 F9
  schema-lift vs coordination-lift breakdown for Option B; F4 R2 as
  gating prerequisite for Option B posture evaluation.
- **D48 21st arm HOLDING CLEAN** — 16-consecutive-fully-clean-arms.
- **Fresh SIGN pin.** `pa-f7417e6ac21d4f23` minted + retired at S1704
  close; **also retired at S1704 open:** `pa-f1a30b7ed5bb4042` (S1703
  owed-retire).

### 11.6 Mid-arc cross-domain refresh (post-S1704, 2026-07-03)

- **Doc.** `docs/research/platform/cross_domain_integration_audit.md`
  §14 v3 append.
- **Fresh SIGN pin.** `pa-99cacc35a73e4dbb` minted + retired
  post-S1704 (NOT a Group 1700 artifact; cross-arc research-library
  maintenance).

### 11.7 S1705 (2026-07-03) — Cat E OpsRun + OpsRunEvent (P5)

- **Doc.** `1705_observability_cat_e_ops_run_event_audit.md` (1015
  lines post-fold; HEAD `a991971a`).
- **9 load-bearing findings F1-F9 locked** per §2.5.
- **Rigby SIGN cycle 1 SIGN-with-edits at Medium/Medium-High
  confidence.** F1-F7 folds landed. Key folds: F1 execution_id
  DESIGN-INTENT-LATENT distinction from Cat D; F5 F5 POSITIVE
  differentiator vs S1704 F4 clarification; F7 D4 named-but-broken
  severity retention; F2/F3/F4/F6 additional wording tightening.
- **D48 22nd arm HOLDING CLEAN** — 17-consecutive-fully-clean-arms.
- **Fresh SIGN pin.** `pa-09c46ee3a0d34069` minted, routed-around,
  retired.

### 11.8 S1706 (2026-07-03) — Cat F Adjacent / Separation (P6)

- **Doc.** `1706_observability_cat_f_adjacent_separation_boundaries_audit.md`
  (642 lines post-fold; ~950 lines including appendix).
- **9 load-bearing findings F1-F9 locked** per §2.6.
- **Rigby SIGN cycle 1 SIGN-with-edits at Medium/Medium-High
  confidence.** F1-F4 folds landed. Key folds: F1 candidate-surface
  disposition bullets; F2 F9 axis label rename
  OBSERVABILITY-FRAMEWORK-UNBOUNDED-RETENTION → RETENTION-PATTERN-INCONSISTENT
  + cross-cat consolidation-point framing; F3 R1 xx99 output posture
  vs implementation scope-discipline; F4 R8/R9 non-blocking labels.
- **D48 23rd arm HOLDING CLEAN** — **18-consecutive-fully-clean-arms
  sub-pattern CONFIRMED** per single-batch-4-question criterion.
- **Fresh SIGN pin.** `pa-a5ce5fdd56364dee` minted, routed-around,
  retired.

### 11.9 S1799 (2026-07-03) — Group 1700 xx99 canonical summary (P7)

- **Doc.** This document.
- **Category.** `canonical_summary`.
- **Playbook §11.3 12-section template FIFTH application** (first
  S1399 Memory; second S1499 Revenue; third S1599 Sports; fourth
  S1699 Content; **fifth S1799 Observability** = this document).
- **§11.3 §10 meta-methodology FIFTH application** per §10 intro.
- **Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence
  landed** 2026-07-03. Q1 CONFIRM Medium-High (no folds) + Q2
  SIGN-with-edits Medium-High + F1 fold (CX-P5 numeric-claim
  tightening ≥8 + §12.3 canonical enumeration pointer at 3 sites) +
  Q3 CONFIRM Medium (no folds) + Q4 CONFIRM Medium-High (no folds).
  F1 fold landed pre-commit. D48 24th arm HOLDING CLEAN;
  **19-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+
  S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702+
  S1703+S1704+S1705+S1706+S1799 CONFIRMED**.
- **Fresh SIGN pin.** `pa-feebb02d7a5342ef` minted this session;
  retire owed at close per §16.
- **Arc-close discipline.** Arc pin `pa-e7fbacc996b34b44` retire
  owed at close per §16 (mirrors S1699 / S1599 / S1499 / S1399
  precedent).
- **OPEN_ARCS transition.** Group 1700 row moves In-progress → Closed
  at close.
- **ARCHITECTURE_INDEX v49 → v50** with §1.53 S1799 registration +
  §8 timeline S1799 row + line-6 v50 preamble.

---

## 12. Appendix — Provenance

### 12.1 Every child's file path

- `docs/research/domains/observability/1700_observability_domain_scoping.md` (S1700 parent)
- `docs/research/domains/observability/1701_observability_cat_a_celery_task_event_audit.md` (S1701 Cat A)
- `docs/research/domains/observability/1702_observability_cat_b_llm_call_event_audit.md` (S1702 Cat B)
- `docs/research/domains/observability/1703_observability_cat_c_agent_execution_audit.md` (S1703 Cat C)
- `docs/research/domains/observability/1704_observability_cat_d_tool_call_record_audit.md` (S1704 Cat D)
- `docs/research/domains/observability/1705_observability_cat_e_ops_run_event_audit.md` (S1705 Cat E)
- `docs/research/domains/observability/1706_observability_cat_f_adjacent_separation_boundaries_audit.md` (S1706 Cat F)
- `docs/research/domains/observability/1799_observability_canonical_summary.md` (this document; S1799 xx99)

### 12.2 Evidence provenance summary

Every §-cell in this xx99 cites at least one child §-cell (§1.1
Executive Summary lock-in OR §9 D74 axis contribution OR §14 Known
Drift OR §16 Boundary Violations OR §17 Duplicate/Overlap OR §19
Recommended Future Research). No new evidence gathered at xx99 per
playbook §11.3 rule.

**Grep verifications carried into this summary from child §20.2 / §20.3:**

- 172 embedments of `core.AgentExecution` at HEAD (S1703 §20.2).
- 23 production wrapper sites across 8 files at HEAD (S1702 §5).
- 4144 total ToolCallRecord rows / 907 PA-path rows / 0 rows with
  trace_id NOT NULL at HEAD (S1704 §20.4).
- 36 OpsRun / 224 OpsRunEvent / 0 rows with cross-cat correlation
  IDs in detail JSON / 4 employees in `_EMPLOYEES_BY_HANDLE` (S1705
  §20.3).
- 75 `@register_claim` decorators in `doc_claim_verification.py`
  (S1706 §20.1).
- 10 body-system getters in `body_vitals.py:340-790` including
  `_get_nervous_vitals` at `:744-790` (S1706 §14.1).

### 12.3 Verifier-loop history

Every child audit ran playbook §14 verifier-loop pre-Explore
(front-run Rigby grep for load-bearing anchors) + post-Explore
(trust-but-verify sub-agent claims for binary claims). 7 material
corrections landed:

- **S1703 §14 VC1:** 3-class AgentExecution landmine resolved to
  1-live + 2-dead-source-files per Django app registry check.
- **S1703 §14 VC2:** F4 PA path coverage confirmed as CRITICAL (not
  MEDIUM as pre-Explore anticipated).
- **S1703 §14 VC3:** F1 trace_id writer-of-record clarified as
  router path (Celery wrapper path doesn't thread trace_id at HEAD).
- **S1705 §14 VC1:** F3 employee count corrected 3 → 4 via ORM check
  (Explore Agent 5 doc-derived was wrong; Explore Agent 6 correctly
  flagged).
- **S1705 §14 VC2:** F4 CTO/COO/Trend Analysis daily existence
  confirmed at `core/services/diagnostics/` (Explore Agent 2 correct;
  Explore Agent 6 searched wrong package).
- **S1705 §14 VC3:** F1 execution_id thread state clarified as
  DESIGN-INTENT-LATENT via flag-gate verification (Explore Agent 1
  read writer source but missed flag gate).
- **S1706 §14 (implicit VC1-VC2):** CockpitIncidentEvent +
  CockpitAutopilotEvent WIRED-BOTH-SIDES correction (Explore Agent 3
  false-positive WRITE-ONLY-FORGOTTEN on both).
- **S1704 F3 (implicit VC):** 29-of-31 base-inherited zero-row
  distribution corrected via post-Explore ORM check (pre-Explore
  overstated "31 unwrapped agents write ZERO rows").

### 12.4 Rigby SIGN pin ledger

Arc pin: `pa-e7fbacc996b34b44` (in service across S1700 open → S1799
close).

Fresh SIGN isolation pins minted per playbook §15 promoted rule
(all routed-around by wrapper hard-code per S1600 precedent):

| Session | Fresh SIGN pin | Status |
|---------|----------------|--------|
| S1700 open | — | (arc pin only) |
| S1701 close | `pa-3147aef9db4945ac` | Retired |
| S1702 close | `pa-c3927ab78c52479a` | Retired |
| S1703 close | (name; owed retire at S1704 open) | Retired |
| S1704 open | `pa-f1a30b7ed5bb4042` | Retired (S1703 owed) |
| S1704 close | `pa-f7417e6ac21d4f23` | Retired |
| Post-S1704 refresh | `pa-99cacc35a73e4dbb` | Retired |
| S1705 close | `pa-09c46ee3a0d34069` | Retired |
| S1706 close | `pa-a5ce5fdd56364dee` | Retired |
| S1799 open | `pa-feebb02d7a5342ef` | Retire owed at S1799 close |

Arc pin `pa-e7fbacc996b34b44` retire owed at S1799 close per playbook
§16 arc-close discipline.

### 12.5 D48 preemptive stability-probe gate ledger

18-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+
S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702+S1703+
S1704+S1705+S1706 CONFIRMED per single-batch-4-question criterion.
Codification-ready-STRENGTHENED-EVEN-FURTHER for playbook v3 §15
(MC-2 recommendation).

D48 24th arm start at S1799 open (this session).

### 12.6 Cross-arc canonical-summary lineage

Fifth arc-close canonical summary (§11.3 12-section template):

1. S1399 Memory (`1399_memory_canonical_summary.md`) — FIRST xx99;
   `authority: research`; playbook §11.3 §10 meta-methodology
   template FIRST application (Chris adopted 2026-07-01).
2. S1499 Revenue (`1499_revenue_canonical_summary.md`) — SECOND xx99;
   §10 SECOND application.
3. S1599 Sports (`1599_sports_canonical_summary.md`) — THIRD xx99;
   §10 THIRD application; §12.4 discriminative-value criterion →
   playbook v3 §11.1 promotion TRIGGERED.
4. S1699 Content (`1699_content_canonical_summary.md`) — FOURTH xx99;
   §10 FOURTH application; playbook §11.1 template promotion
   CONFIRMED-STRENGTHENED at four-consecutive-application.
5. **S1799 Observability (this document)** — FIFTH xx99 overall; §10
   FIFTH application.

### 12.7 Post-arc PR bundle contents (owed at S1799 close)

Per playbook §16 draft→canonical commit policy + memory rule
`feedback_docs_cascade_at_every_close.md`:

1. **This xx99 doc** `1799_observability_canonical_summary.md`
   (`status: draft` → `active` after Rigby SIGN cycle 1 folds
   landed).
2. **`docs/research/ARCHITECTURE_INDEX.md`** — v49 → v50 with §1.53
   S1799 registration + §8 timeline S1799 row + line-6 v50 preamble
   + optional inline additions for missing §8 rows S1605 + S1606 +
   S1699.
3. **`docs/research/OPEN_ARCS.md`** — Group 1700 In-progress row →
   Closed section with canonical summary path + close session number
   + closing notes.
4. **`docs/handoffs/SESSION_1799_OBSERVABILITY_CANONICAL_SUMMARY.md`**
   — session handoff documenting arc close + arc pin retire + Rigby
   SIGN verdict.
5. **`00-START-NEXT-SESSION.md`** — rewrite pointing at whatever
   comes next per playbook §22 default queue lean OR Chris-specified.
6. **`tools/pa_local.sh:128`** — rotation of arc pin hard-code
   (either reset to null-arc default OR point at next arc's pin).
7. **Post-merge cascade** — 4-step docs cascade + `build_docs_provenance`
   per memory rule.
8. **Anchor-update tranche** (§7) — CAN be bundled OR split into
   follow-up PR at Chris discretion.

_Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence landed 2026-07-03; F1 fold applied pre-commit. `status: active`._
