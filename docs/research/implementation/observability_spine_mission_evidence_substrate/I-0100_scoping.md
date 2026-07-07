---
title: "Arc I-0100 — Observability Correlation Spine + Mission Evidence Substrate (Stages 1–2)"
status: closed-local
authority: implementation-scoping
arc_id: I-0100
arc_slug: observability_spine_mission_evidence_substrate
stage: 6
stage_state: closed
canonical_close_doc: I-010099_observability_spine_implementation_close.md
close_ratified_pr: 2976
stage_transition_history:
  - {stage: 1, state: exit-gate-cleared, at: 2026-07-06, event: "Rigby SIGN Cycle 1 SIGN-with-edits + Chris agree-all-F1-F8 ratification (Stage 1 arc-open bundle #2945 merged)"}
  - {stage: 1, state: p0-prep-in-flight, at: 2026-07-06, event: "P0 prep PR #2948 opened (IB-Q1-BOOT-01 discharge; ADR corpus establishment)"}
  - {stage: 1, state: p0-prep-merged, at: 2026-07-06, event: "PR #2948 merged; docs/adr/ + ADR-0001 on main; Stage 2 Entry gate v1.4 auto-open clause satisfied"}
  - {stage: 2, state: active, at: 2026-07-06, event: "Housekeeping PR #2950 — Stage 2 opening ceremony per IOS §4.3 Stage 2 Entry gate v1.4 Option (a) auto-open; frontmatter flipped 1 → 2 per §4.3.0 v1.4 discipline"}
  - {stage: 2, state: active, at: 2026-07-06, event: "ADR-B / ADR-0002 (pa-write-shape-and-correlation-contract) ratified 2026-07-06 via Chris agree-all-F1-F8; PR #2951 merged"}
  - {stage: 2, state: design-prep-in-flight, at: 2026-07-06, event: "ADR-A design-prep authoring opened per IOS v1.5 §4.3 Stage 2 mandatory design-prep rule + §4.3.0 v1.5 flip discipline; target: I-0100_design_prep_adr_a_mission_runner_staged_enable.md + ADR-0003"}
  - {stage: 2, state: active, at: 2026-07-06, event: "ADR-A / ADR-0003 (mission-runner-staged-enable-posture) ratified 2026-07-06 via Chris agree-all-F1-F8; PR #2953 merged; stage_state flipped design-prep-in-flight → active per §4.3.0 v1.5 discipline. Stage 2 ADR authoring complete except optional ADR-C (F4 fold third-place); Stage 3 pre-flight ready to open for P2/P3/P4 runtime discharge."}
session_opened: 2700
session_ratified: 2700
opened: 2026-07-06
ratified: 2026-07-06
ratifier: chris
first_arc_override: true
first_arc_override_reason: |
  Rigby recommended over Claude default (I-0100_ios_bootstrap); Chris
  ratified 2026-07-06 per RATIFICATION §2 Axis 2. Meta-argument:
  broken observability breaks IOS §2.2 verification-method Yes-required
  field for every downstream intake row — instrument first so verification
  of everything else works.
intake_seed_ids_flipped_in_arc: [IB-1799-T1-01, IB-1799-T1-02, IB-1799-T1-03]
intake_admitted_but_deferred_flip: [IB-1799-T0-01]
intake_conditional_admit: [IB-1799-T0-02]
discharges_debt: IDBT-0001 (1799 domain slice; discharge path 2 per resolution_path — arc-scoped incremental)
arc_pin: pa-c5b235f7b15f45be
arc_pin_label: ios-arc-open-I-0100
arc_pin_minted: 2026-07-06
paused_research_pin: pa-44a6eb70d8814e34 (T4 Group 1700 Observability — preserved as tools/pa_local.sh comment above --conversation line per §15.14)
retired_pin_prior: pa-39d3694312ab4326 (ios-part11-first-queue-ratification-v1; retired at seed PR merge 2026-07-06 per RATIFICATION §3 lifecycle)
sign_cycle_1: SIGN-with-edits (Rigby; single-batch × 4-Q per IOS §7.2; 8 folds applied; no BLOCKED; Cycle 2 not requested)
sign_cycle_1_pin: pa-c5b235f7b15f45be
adr_corpus_precondition: SATISFIED via Option (a) — IB-Q1-BOOT-01 shipped as P0 prep PR #2948 (merged 2026-07-06); `docs/adr/` + `ADR-0001-establish-adr-corpus.md` (status accepted) on main. NEEDS_ADR intake can now ship ADR-authoring PRs in Stage 2.
ratification_record: docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md §2 Axis 2
ios_status_at_open: active v1.2 (patch PR #2943 in flight — §4.3 template 9-section correction + §10 substitution + ADR corpus precondition + START-NEXT §15.14 citation fix)
ios_status_at_stage_2_open: active v1.4 (via #2947 v1.3 + #2949 v1.4 — cascade discipline codified + Stage 2 Entry gate + design-prep equivalence + ADR SIGN cadence + §15.15 00-START-NEXT-SESSION ownership all in force at Stage 2 opening)
companion_docs:
  - docs/research/domains/observability/1799_observability_canonical_summary.md
  - docs/research/implementation/BACKLOG.md
  - docs/research/implementation/IMPLEMENTATION_DEBT.md
  - docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md
  - docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md
  - docs/research/OPEN_ARCS.md
  - docs/topics/celery-workers.md
  - docs/topics/infrastructure.md
  - docs/topics/agent-system.md
  - docs/topics/employee-os.md
verifier_loop: |
  Stage 1 (2026-07-06): drafted by Claude Code in-conversation as Arc
  I-0100 Stage 1 planning deliverable following seed PR #2941 merge and
  session-open directive to execute "only Stage 1" per user framing.
  Draft consumed: RATIFICATION_2026-07-06 §2 Axis 2 (Chris pick of
  Arc I-0100 over Claude's I-0100_ios_bootstrap default); 1799 xx99 §1
  verdict + §5 D74 + §8.1 T0/Gate + §8.2 T1 items 1-4; BACKLOG.md T1
  Arc I-0100 seed rows; IMPLEMENTATION_DEBT.md IDBT-0001 resolution paths.
  Routed to Rigby SIGN Cycle 1 on fresh arc-scoped pin
  pa-c5b235f7b15f45be per IOS §7.2 single-batch × 4-Q cadence.
  Rigby returned SIGN-with-edits overall with 8 concrete folds across
  Q1a/Q1b/Q2a/Q2b/Q3a/Q3b/Q4a/Q4b sub-questions (Q2a SIGN-clean; 7
  SIGN-with-edits; no BLOCKED; Cycle 2 not requested). All 8 folds
  ratified by Chris via "agree all F1-F8" 2026-07-06. Folds applied
  in-doc: F1 admits IB-1799-T0-01 as architecture-only ADR-C track;
  F2 makes retention a required DECISION INPUT to ADR-C (not code output);
  F3 P2 unconditional ship confirmed clean; F4 ADR-B ratifies before
  ADR-A; F5 ADR-B specifies PA↔LLMCallEvent correlation contract;
  F6 anti-scope bullet 7 replaced with Stage 3 bounded fleet-adjacent
  audit in-scope; F7 verification-method as interface at Stage 1,
  concrete queries at Stage 3 pre-flight; F8 three risks + mitigations
  + rollback triggers added to §7.3. Anti-context-drift: this doc is
  authored by session slug `claude-arc-i0100-stage1-open`; if a future
  session remembers different fold semantics than what appears here,
  this doc is truth per IOS §15.7.
---

# Arc I-0100 — Observability Correlation Spine + Mission Evidence Substrate

**Stages 1–2 — status `active`; current `stage: 2, stage_state: active` (Stage 2 opened 2026-07-06 via P0 prep PR #2948 merge auto-open per IOS §4.3 Stage 2 Entry gate v1.4 Option (a) clause). Chris ratified Stage 1 exit 2026-07-06 via "agree all F1-F8" wholesale fold ratification.**

Template: Playbook §11.1 9-section parent-scoping template with IOS v1.2
§4.3 substitutions (§3 taxonomy → intake items; §5 child mission → PR
sequence; §7 anti-scope → anti-scope + reversibility + risks; §9 next
step → next step + ADR checkpoint; §10 added Stage checklist snapshot).

---

## 1. Why this arc

Five signals converge per `1799_observability_canonical_summary.md` §1
canonical verdict at HEAD `5867f134`:

1. **Cat D `ToolCallRecord.trace_id` is 100% NULL across 4144 rows at HEAD**
   (`core/models_tool_calls.py:19-131`; ORM-verified 2026-07-03 at S1704
   Q1-Q4). Column exists, `db_index=True`, composite-indexed with
   `created_at` — index space wasted. `deliverable_provenance.py:105`
   chain returns EMPTY for every deliverable at HEAD. Kills Option B
   of the D74 spine posture at runtime; poisons operator-surface trust.
2. **Cat C PA-path AgentExecution coverage is zero** (S1703 F4). PA
   agentic loop writes 0 `AgentExecution` rows unless the dispatched
   tool is a router-registered agent. Every PA turn un-instrumented.
3. **Cat E OpsRun / OpsRunEvent design-intent-latent** —
   `rigby_delegation_signals.py:79-84` (S1250 PR8) IS built to populate
   `execution_id` in OpsRunEvent detail JSON on `AgentExecution`
   post_save for delegated executions, but the handler is
   `settings.RIGBY_DELEGATION_ENABLED`-gated (default `False`). 0/224
   rows carry `execution_id` at HEAD.
4. **IOS §2.2 verification-method requirement (Yes-required)** cannot
   be satisfied for any downstream implementation arc's intake rows
   until at least one of the above is repaired. Rigby's meta-argument
   at RATIFICATION §2 Axis 2: *"Fixing observability makes every
   downstream arc's verification-method claims actually enforceable at
   Stage 5. Instrument first."*
5. **T4 Group 1700 Observability research arc is paused** per IOS
   §15.3 phase-transition supersession. No same-surface research
   conflict at arc open. Per §9.1, if T4 opens mid-Arc-I-0100, Arc
   I-0100 pauses at its current stage.

---

## 2. Existing inventory tells us

- **`PLATFORM_INVENTORY.md`** (regenerable snapshot at
  `e617af59` 2026-07-05): 9 body systems, 585 concrete models, 415
  user-defined Celery tasks (excludes `celery.*` internals), 92 enabled
  + 5 disabled PeriodicTask rows. Cat D writer paths cited at
  `core/models_tool_calls.py:19-131`.
- **`docs/topics/celery-workers.md`**: existing observability narrative
  for Cat A (CeleryTaskEvent 30-day retention baseline).
- **`docs/topics/agent-system.md`**: BaseAgent = 5,575 lines; AGENT_MAP
  = 83 agents (74 enabled); AgentExecution FK is documented for router
  path but NOT for PA path (Cat C S1703 F4 evidence).
- **`docs/topics/employee-os.md`**: 3 employees ratified (Documentation
  Manager, Platform Auditor, Chief of Staff). S1705 F3 flagged fourth
  (bug_triage_specialist added S1267) — Arc I-0100 close doc may
  inherit this counts-drift refresh via IB-1799-T1-03's flip cascade.
- **`docs/AUDIT_FINDINGS.md` §18**: Cat D writer paths already
  documented as `KNOWN_DEFERRED` for retention → NOT Celery deletes.
  IB-1799-T1-01 is a **write-side fix**, not a delete; §18 gate
  therefore does not apply here.
- **Cross-domain audit v5 §14.17 refresh (2026-07-06)**: observability
  rows current. Arc I-0100 close (Stage 6) MUST append §14.N delta per
  IOS D10 hard gate.

---

## 3. Intake items admitted to this arc (§4.3 substitution for §3)

### 3.1 Ratified seed rows (RATIFICATION §2 Axis 2, `IN_ARC` flipped this session)

| intake_id | title | source_ref | risk_class | design_state | affected_surfaces | expected_ship_size |
|-----------|-------|-----------|-----------|--------------|------------------|--------------------|
| `IB-1799-T1-01` | Fix `ToolCallRecord.trace_id` 100% NULL at write-side | 1799 §1 axis D + S1704 F1 | `NEEDS_RIGBY_SIGN_PLUS_CHRIS` | `SPEC_COMPLETE` | `core/services/tool_dispatcher.py:961` (dispatcher hardcodes `None` with comment "dispatcher trace_id ('td-N-hex') isn't a UUID"); `core/agents/base_agent.py:451-459` (S970 wrapper omits `trace_id`); `core/agents/base_agent.py:3302-3310` (S1085 inline recorder omits); PA path `pa-N-hex` → UUID conversion at `core/services/unified_pa_entrypoint.py` | M |
| `IB-1799-T1-02` | Wire PA-invoked agents → `AgentExecution` writes | 1799 §1 axis C + S1703 F1 + xx99 §8.2 T1 item 1 | `NEEDS_RIGBY_SIGN_PLUS_CHRIS` | `POSTURE_PENDING` (ADR-B decides shape: per-turn span vs per-message span vs dedicated `PAAgentExecution` model — MUST include PA↔LLMCallEvent correlation contract per F5 fold) | `core/agents/base_agent.py`, `core/services/tool_dispatcher.py`, `core/services/unified_pa_entrypoint.py`, PA tool-dispatch code path | L |
| `IB-1799-T1-03` | Unlock `OpsRun` + `OpsRunEvent` via `MISSION_RUNNER_ENABLED` (paired with `RIGBY_DELEGATION_ENABLED` posture) | 1799 §1 axis E + S1705 F1 + xx99 §8.2 T1 item 4 | `NEEDS_ADR` | `POSTURE_PENDING` (ADR-A ratifies flip posture + rollback trigger + staged-enable strategy per F8-iii) | `core/employees/mission_runner.py`, `core/models_ops_runs.py`, `core/services/rigby_delegation_signals.py:79-84`, feature-flag config in `settings.py` | S |

### 3.2 Admitted as architecture-only track (per F1 fold) — BACKLOG flip deferred to Stage 2 ADR-C opening

| intake_id | title | source_ref | admit posture (F1 fold) |
|-----------|-------|-----------|------------------------|
| `IB-1799-T0-01` | Ratify D74 six-axis observability correlation-spine posture (Option A execution_id / Option B trace_id / Option C shared view / Option D hybrid) | 1799 §5 D74 + §8.1 T0/Gate 2 | Admitted as **arc-local architecture-only track** producing ratified ADR-C posture + deprecation-plan notes. **NO new runtime writes or migrations in this arc beyond P2/P4 necessities.** Arc-boundary between fix (Arc I-0100) and deprecation (post-arc follow-on Arc I-0200-eq). BACKLOG row flips to `IN_ARC (I-0100)` at Stage 2 ADR-C opening, not at Stage 1 close, so that Chris ratifies the architecture-only scope explicitly at ADR-C entry per F1 fold semantics. |

### 3.3 Conditional admit (per F2 fold — required decision INPUT to ADR-C, not code output)

| intake_id | title | source_ref | admit posture (F2 fold) |
|-----------|-------|-----------|------------------------|
| `IB-1799-T0-02` | Ratify unified retention posture across 14 event models (12/14 currently UNBOUNDED) | 1799 §1 axis F + §8.1 T0/Gate 1 | ADR-C evaluates D74 posture with **explicit retention constraints** as required decision input (current TTLs, target TTLs, projected event-volume under `MISSION_RUNNER_ENABLED`). ADR-C **may conclude "retention follow-on required"** without shipping IB-1799-T0-02 as code in this arc. F2 fold semantics: your S1706 SIGN cycle 1 F2 fold required retention first-class in the spine ADR — that constraint is satisfied by making retention a decision-input regardless of the code-shipping decision. Volume-guardrail added at §7.2 to catch spike scenarios before retention ratifies. |

### 3.4 Deferred (NOT admitted to Arc I-0100)

- `IB-1799-T1-04` candidate (`_extract_usage` Gemini + Ollama shape completeness) — xx99 §8.3 T2 item 4 (S1702 R4). Orthogonal to correlation spine. Route to a later observability follow-on arc.
- Failure-cluster aggregator + observability→HAI escalation — per BACKLOG.md IDBT-0001 known un-enumerated list. Cross-arc (HAI arc).
- Cat E `evidence_for_mission` join repair (xx99 §8.2 T1 item 3) — follow-on arc after `IB-1799-T1-01` + `IB-1799-T1-02` merge. Depends on both.

### 3.5 IDBT-0001 1799-slice discharge scope

Per IMPLEMENTATION_DEBT.md IDBT-0001 resolution_path Option 2 (arc-scoped
incremental), Arc I-0100 discharges the 1799 slice by:
(a) enumerating candidate additional rows above (§3.2, §3.3);
(b) explicitly listing deferred candidates (§3.4);
(c) marking known-un-enumerated 1799 T1 tail items (per BACKLOG.md
IDBT-0001 known un-enumerated list) as CROSS-REFERENCED-NOT-ADMITTED
in Arc I-0100 — those items remain as PARTIAL_DISCHARGE tail rows in
BACKLOG.md pending either follow-on arc admit OR dedicated third
extraction pass.

---

## 4. Arc-vs-single-PR recommendation

**Arc recommended** (not single-PR). Rationale:

- Three intake items sized `L` / `M` / `S`. `IB-1799-T1-02` is `L`
  (~1000–1500 LOC) touching the PA hot-path — needs staging.
- Two of three items require ADR before Stage 4: `IB-1799-T1-02`
  (ADR-B: PA-write shape + PA↔LLMCallEvent correlation contract per F5
  fold) and `IB-1799-T1-03` (ADR-A: `MISSION_RUNNER_ENABLED` flip
  posture per F8-iii staged enable). Single-PR path cannot accommodate
  two ADR gates.
- IB-1799-T0-01 architecture-only ADR-C (per F1 fold) adds a third ADR
  track; can draft parallel to A+B but ratifies last (per F4 fold —
  ADR-B first, ADR-A second, ADR-C optional third).
- Retention posture (T0/Gate 1) constrains ADR-C per F2 fold — not
  code-shipping but decision-input.
- **Verification interface** per F7 fold: Stage 1 defines interface
  (per §7 below); Stage 3 pre-flight fills concrete queries once ADR-B
  selects storage shape. Single-PR path cannot accommodate this
  parameterization pattern.
- Regression risk: `IB-1799-T1-01` 3-writer coordination + `IB-1799-T1-02`
  hot-path row-volume + `IB-1799-T1-03` flag-gated dormancy exposure
  all benefit from independent Stage 5 verify cycles.

**Estimated arc runtime:** 4–6 sessions (Stage 2 = 2 sessions ADR
authoring with parallel drafts + sequenced ratification; Stage 3 = 1
session pre-flight with concrete query fill-in + bounded fleet-adjacent
audit per F6 fold; Stage 4 = 2–3 PRs across ~2 sessions with staged
enable per F8-iii; Stage 5 = 1 session verify; Stage 6 = 1 session
close + docs cascade + audit §14.N).

---

## 5. Planned PR sequence (§4.3 substitution for §5)

Sequenced by dependency + ADR gate. All PRs cite `intake_id` + 1799 §N
in body. All PRs pass §5.2 pre-merge gates. All rollouts feature-flagged
per §5.4 patterns.

| PR # | Discharges | Depends on | Size | Files touched (est.) | ADR gate | Rollout |
|------|-----------|------------|------|---------------------|---------|---------|
| **P0** | `IB-Q1-BOOT-01` — Author `ADR-0001-establish-adr-corpus.md` + create `docs/adr/`. **Prerequisite per IOS v1.2 §4.3 exit-gate ADR corpus precondition (patch PR #2943 in flight).** In-arc P0 prep PR per Option (a). Must ship BEFORE Stage 2 opens. | none (docs-only; recursive-bootstrap ADR) | XS (~100 LOC) | `docs/adr/ADR-0001-establish-adr-corpus.md` (new file, new dir) | none | Straight ship (docs) |
| **P1** | Prep — Stage 1 arc-open bundle (this PR): scoping doc + BACKLOG.md flips + OPEN_ARCS.md row + `tools/pa_local.sh` rotation. NOT an intake row; state-plumbing. | none | XS (~250 LOC docs + state) | `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md` (new), `docs/research/implementation/BACKLOG.md` (3-row flip), `docs/research/OPEN_ARCS.md` (In-progress row insert), `tools/pa_local.sh` (rotation) | none | Straight ship (docs+state) |
| **P2** | `IB-1799-T1-01` write-side trace_id fix. Ships **unconditional of D74 posture** per F3 SIGN-clean verdict — 100% NULL is broken invariant, not posture question. | none (SPEC_COMPLETE; ships regardless) | M (~400 LOC + regression tests) | `core/services/tool_dispatcher.py`, `core/agents/base_agent.py`, `core/services/unified_pa_entrypoint.py`, `core/tests/test_tool_call_record_trace_id.py` (new) | none | Feature flag `TOOL_CALL_TRACE_ID_ENFORCED` gates the new UUID-write branches at all 3 writer sites. **Per F8-i mitigation:** temporary dual-format acceptance during transition (accept both `td-N-hex` legacy + UUID new for a bounded window) to avoid breaking hidden `td-N-hex` readers not caught by Stage 3 bounded fleet-adjacent audit. |
| **P3** | `IB-1799-T1-03` `MISSION_RUNNER_ENABLED` + `RIGBY_DELEGATION_ENABLED` staged unlock | ADR-A ratified (per F4 fold, ADR-A ratifies AFTER ADR-B) | S (~200 LOC) | `settings.py`, `core/services/rigby_delegation_signals.py`, `core/tests/test_ops_run_event_execution_id.py` (new) | ADR-A | **Per F8-iii mitigation:** staged enable pattern — shadow mode (log without acting) → partial (10% cohort) → full. Alerting on first error signature triggers immediate disable. **Per F8-ii mitigation:** OpsRunEvent volume sampling/cap active during shadow + partial phases; DB pressure threshold gate before full enable. Metric: `OpsRunEvent.count()/day > <threshold>` → auto-disable. |
| **P4** | `IB-1799-T1-02` PA agentic loop → `AgentExecution` (or `PAAgentExecution` per ADR-B) per-turn / per-message write, including PA↔LLMCallEvent correlation contract (keys + join path per F5 fold) | ADR-B ratified (first per F4); P2 merged | L (~1200 LOC + regression tests + potential migration for new FK / new model) | `core/services/unified_pa_entrypoint.py`, `core/agents/base_agent.py`, `core/services/tool_dispatcher.py`, `core/models_unified_system.py` (potential FK addition) OR `core/models_pa_execution.py` (new model per ADR-B option 3), migration `NNNN_pa_agent_execution_backfill.py` | ADR-B | Feature flag `PA_AGENT_EXECUTION_WRITE_ENABLED` gates new PA write path. Migration backward-compatible (nullable field / additive-only). Rollback: toggle flag off; new writes halt; existing rows remain. |
| **P5** | Arc canonical close doc `I-010099_observability_spine_implementation_close.md`, `cross_domain_integration_audit.md §14.N` refresh (D10 hard gate), 4-step docs cascade + `build_docs_provenance` + `embed_documents --all-unembedded` (chunk count in PR body per MEMORY `feedback_cascade_pr_must_include_embed_step`), `OPEN_ARCS.md` row flip In-progress → Closed, BACKLOG.md rows flip `IN_ARC → SHIPPED` + `pr_refs` populated, IMPLEMENTATION_DEBT.md IDBT-0001 1799-slice discharge recorded | P2 + P3 + P4 merged + Stage 5 verify complete | M (docs only) | 5–10 docs | none | Straight ship (docs) |

**Not shipped in this arc (routed elsewhere):**

- **ADR-C (D74 spine posture)** authoring is in-arc per F1 fold, but
  ratification-plus-code path for downstream deprecation (e.g., drop
  `trace_id` column if Option A execution_id spine ratifies) is a
  post-arc follow-on candidate — see §6. F1 fold caps ADR-C to
  decision + consequences only; no in-arc migrations beyond P2/P4.
- **ADR-D retention posture** (`IB-1799-T0-02`) — per F2 fold, ADR-C
  bundles retention as decision input; conclusion may be "follow-on
  ADR-D required" without shipping IB-1799-T0-02 in this arc.
- **Cat E `evidence_for_mission` join repair** (xx99 §8.2 T1 item 3) —
  follow-on arc; blocks on `IB-1799-T1-01` + `IB-1799-T1-02` merge.

---

## 6. Parked candidate issues

- **Retention posture bundling shape** (paired-ADR question per your
  S1706 SIGN cycle 1 F2 fold): ADR-C decision-input-shape or follow-on
  ADR-D — decided at Stage 2 ADR-C opening.
- **Column-drop decision for `trace_id`** if ADR-C ratifies Option A
  (execution_id spine): moved from §6 Parked to **Post-arc follow-on
  candidate** per F1 fold (Rigby's explicit request). Route to Arc
  I-0200-eq post-close if Option A ratifies; otherwise column stays.
- **PA-coverage design shape** (per-turn span vs per-message span vs
  dedicated `PAAgentExecution` model) — held for ADR-B; F5 fold
  additionally requires PA↔LLMCallEvent correlation contract in ADR-B
  scope.
- **`AgentTaskExecution` posture** (0 rows since S1244 rename per S1703
  F1) — orthogonal cleanup; not admitted to Arc I-0100.
- **Doc-verifier drift as first-class telemetry signal** (xx99 §8.2 T1
  item 8) — non-blocking for this arc; routes to follow-on
  observability arc.
- **Cat B LLMCallEvent dedup posture** (LLMCallEvent + LLMCallLog +
  CostTracking third store per S1702 F1) — anti-scope for this arc
  (see §7.1). ADR-B includes correlation contract (per F5 fold) but
  NOT dedup implementation. Dedup routes to `IB-1799-T1-05` (from
  xx99 §8.2 T1 item 5) after ratification.

---

## 7. Anti-scope + reversibility guardrails + risks (§4.3 substitution for §7)

### 7.1 Anti-scope — this arc does NOT touch

1. **Cat A CeleryTaskEvent** — already 30-day retention, DEEP-WIRED
   per xx99 §1 Cat A cell.
2. **Cat B LLMCallEvent dedup posture** — LLMCallLog / CostTracking
   third store dedup routes to `IB-1799-T1-05` post-ratification.
   **Per F5 fold:** ADR-B MUST specify PA↔LLMCallEvent correlation
   contract (keys + join path) — WITHOUT implementing dedup. This
   captures the linkage decision in the same arc as the PA-write
   shape, keeping Cat C fix from leaving Cat B ambiguous.
3. **Cat F HeartBeat / SLO framework / doc-claim verifier /
   DeliverableEvent / 14-model event-shape catalog** — routes to
   Group 1900 Event Architecture arc.
4. **`AgentTaskExecution` model deprecation, S287 docstring cleanup**
   (T2 item 6) — orthogonal cleanup.
5. **Any PublishGate / Newsletter / SelfBlog change** — Group 1600
   Content territory.
6. **Any Auth silent-401 fix** — Group 2400 Auth territory.
7. **Broader fleet-federation observability sweep is parked** (xx99
   §6.9 UNKNOWN). **Per F6 fold in-scope:** Stage 3 pre-flight
   bounded audit of fleet-adjacent callers of
   `ToolCallRecord`/`trace_id` (gateway allowlist + dispatchers +
   any Fleet* consumers) to ensure no hidden `td-N-hex` readers
   break. Bounded audit = MEMORY `feedback_fleet_caller_verification_
   before_celery_deletes` 3-axis sweep. Broader federation-wide
   telemetry sweep remains parked as separate research.

### 7.2 Reversibility per PR

| PR | Rollout pattern | Rollback command / toggle |
|----|-----------------|--------------------------|
| P0 | Straight ship (docs) | Revert commit |
| P1 | Straight ship (docs+state) | Revert commit; retire fresh pin `pa-c5b235f7b15f45be`; restore prior `--conversation` value; unflip BACKLOG rows |
| P2 | Feature flag `TOOL_CALL_TRACE_ID_ENFORCED = False` gates new UUID-write branches at all 3 writer sites. Temporary dual-format acceptance during transition per F8-i mitigation | Toggle flag off (writes revert to `None`); no schema migration to undo |
| P3 | Existing feature flag flip: `MISSION_RUNNER_ENABLED = True` + `RIGBY_DELEGATION_ENABLED = True` (paired). **Staged pattern per F8-iii:** shadow → partial (10% cohort) → full | Restore settings to `False`; no schema change to undo. Auto-disable on: (a) OpsRunEvent growth threshold breach (`> X rows/day`; threshold set in Stage 3 pre-flight); (b) first error signature in `rigby_delegation_signals.py` handler (per F8-iii latent-bug detection) |
| P4 | Feature flag `PA_AGENT_EXECUTION_WRITE_ENABLED = False` gates new PA write path. Migration backward-compatible (nullable field / additive-only); rollback script committed alongside per §5.4 | Toggle flag off; new AgentExecution rows halt; existing rows remain (no delete). Migration rollback script restores schema |
| P5 | Docs-only close PR; standard revert | Revert commit — reopens arc |

### 7.3 Risk register (per F8 fold — 3 risks + mitigations + rollback triggers)

| Risk # | Risk | Severity | Mitigation | Rollback trigger |
|--------|------|----------|-----------|------------------|
| R1 | **Hidden `td-N-hex` string readers in fleet-key surfaces** — local grep may miss consumers in fleet repos (character-os, mentorforge, other-fleet apps). Per MEMORY `feedback_fleet_caller_verification_before_celery_deletes`. | HIGH | Stage 3 pre-flight bounded fleet-adjacent audit per F6 fold (repo grep + Rigby `ops_tool.celery_task_history` 30-day + ORM probe of `FleetServiceKey` / `FleetPAChatAuditRow` / `FleetArtifact` for `td-N-hex` regex). Temporary **dual-format acceptance** during transition — dispatcher accepts both legacy `td-N-hex` and new UUID for a bounded window. Bounded window closes at Stage 6 post-verify. | Revert `TOOL_CALL_TRACE_ID_ENFORCED` flag if any hidden reader breaks post-merge |
| R2 | **OpsRunEvent volume spike + retention shortage cascade** — `MISSION_RUNNER_ENABLED = True` triggers OpsRunEvent growth BEFORE IB-1799-T0-02 unified retention ADR ratifies. DB pressure risk. | HIGH | Per F8-ii + F2 volume-guardrail: sampling/cap active during shadow + partial phases. Metrics threshold gate before full enable: `OpsRunEvent.count()/day > <threshold>` (threshold set in Stage 3 pre-flight based on baseline measurement). Do NOT depend on retention ADR landing — mitigation active regardless. | Auto-disable `MISSION_RUNNER_ENABLED` on threshold breach. Sampling/cap remains as fallback until retention ADR ratifies |
| R3 | **`RIGBY_DELEGATION_ENABLED = True` unmasks latent bugs** in `rigby_delegation_signals.py:79-84` handler dormant behind `False` gate for months (since S1250 PR 8). Handler is untested at runtime. | HIGH | Per F8-iii: staged rollout — **shadow mode first** (log-without-act) + dry-run logging for first error-signature detection → partial (10% cohort) → full. Alerting on first exception signature triggers immediate disable. Regression test coverage before shadow-mode enable: exercise handler on synthetic AgentExecution post_save events in test suite. | Auto-disable `RIGBY_DELEGATION_ENABLED` on first exception signature. Fast rollback path — one config toggle. |

### 7.4 Cross-scope risks (in addition to F8-mandated three)

| Risk # | Risk | Severity | Mitigation | Rollback trigger |
|--------|------|----------|-----------|------------------|
| R4 | Cross-writer trace_id coordination breaks one path silently | HIGH | Regression test covers all 3 writer sites explicitly (`test_tool_call_record_trace_id.py`); `TOOL_CALL_TRACE_ID_ENFORCED` staged rollout | Flag off + revert per-writer if isolation permits |
| R5 | P4 PA-write increases AgentExecution row volume ~10–100× | HIGH | Bundle retention posture into ADR-B decision input OR accept 30-day default matching Cat C existing semantics; monitor row-count during Stage 5 | Toggle `PA_AGENT_EXECUTION_WRITE_ENABLED` off |
| R6 | Migration in P4 breaks in-flight requests | MEDIUM | Backward-compatible migration (nullable field); blue/green safety per §5.4 | Migration rollback script |
| R7 | T4 Group 1700 Observability research arc re-opens mid-Arc-I-0100 | MEDIUM | Per §4.4 + §9.1, Arc I-0100 pauses at current stage; Chris directive triggers | Not blocked by rollback; arc-state pause |
| R8 | Rigby SIGN worker instability on long Stage 2 ADR-C SIGN routing | LOW | Batch SIGN into 3-4 findings per prompt per MEMORY `feedback_rigby_sign_worker_instability_recovery`; fresh arc-scoped pin already minted (this arc's pin) reduces poisoning risk from ratification-pin history | Retire jammed pin; mint fresh; batch-shrink per recovery playbook |

---

## 8. Decisions recorded (Chris-ratified 2026-07-06 at Stage 1 exit)

- **First-arc identity:** `I-0100_observability_spine_mission_evidence_substrate` (Rigby recommended over Claude's `I-0100_ios_bootstrap`; Chris ratified per RATIFICATION §2 Axis 2).
- **First-arc override reason ratified:** Broken observability breaks IOS §2.2 verification-method Yes-required field for every downstream intake row.
- **Intake seed:** `IB-1799-T1-01`, `IB-1799-T1-02`, `IB-1799-T1-03` (RATIFICATION §2 Axis 2 minimum) — flipped `TRIAGED → IN_ARC (I-0100)` at this Stage 1 close.
- **F1 (Rigby SIGN cycle 1 fold, Chris ratified):** IB-1799-T0-01 admitted as **architecture-only ADR-C track**; BACKLOG flip deferred to Stage 2 ADR-C opening. Column-drop for `trace_id` (if D74 Option A ratifies) moved to Post-arc follow-on candidate.
- **F2 (Rigby SIGN cycle 1 fold, Chris ratified):** IB-1799-T0-02 conditional admit as **required decision INPUT to ADR-C**; may conclude "retention follow-on required" without shipping code in this arc. Volume-guardrail added at §7.3 R2.
- **F3 (Rigby SIGN cycle 1 verdict, Chris ratified):** P2 (trace_id write-side fix) ships **unconditional of D74 posture** — 100% NULL is broken invariant.
- **F4 (Rigby SIGN cycle 1 fold, Chris ratified):** ADR-A and ADR-B drafted in parallel; **Chris ratifies ADR-B first**, then ADR-A, then (optional) ADR-C. P3 gated on ADR-A ratification; P4 gated on ADR-B ratification.
- **F5 (Rigby SIGN cycle 1 fold, Chris ratified):** ADR-B MUST specify PA↔LLMCallEvent correlation contract (keys + join path) WITHOUT implementing dedup.
- **F6 (Rigby SIGN cycle 1 fold, Chris ratified):** Anti-scope bullet 7 replaced — broader fleet-federation sweep parked; Stage 3 pre-flight bounded fleet-adjacent audit of `ToolCallRecord`/`trace_id` callers is in-scope.
- **F7 (Rigby SIGN cycle 1 fold, Chris ratified):** Verification-method defined as an **interface** at Stage 1 (see §5 rollout column + §9 interface below); Stage 3 pre-flight fills concrete queries keyed to ADR-B selected model/table.
- **F8 (Rigby SIGN cycle 1 fold, Chris ratified):** Three risks (R1 hidden `td-N-hex` readers; R2 OpsRunEvent volume spike; R3 delegation handler dormancy) added to §7.3 with mitigations + rollback triggers.
- **ADR corpus precondition (per IOS v1.2 §4.3, patch PR #2943):** Option (a) bundle — `IB-Q1-BOOT-01` admitted as in-arc P0 prep PR (see §5 P0 row). MUST ship before Stage 2 opens ADR-A/B/C authoring.
- **No SIGN Cycle 2 requested** by Rigby — all fold edits structural/clarifying, no BLOCKED verdict.

---

## 9. Next step + ADR checkpoint (§4.3 substitution for §9)

### 9.1 Next step

Stage 2 opens with:
1. **P0 prep PR** — ship `IB-Q1-BOOT-01` (ADR-0001-establish-adr-corpus.md + `docs/adr/` creation) FIRST. Blocks any ADR authoring.
2. **ADR-B authoring** (per F4 fold, ADR-B ratifies first) — PA-write shape decision (per-turn span vs per-message span vs dedicated `PAAgentExecution` model), INCLUDING PA↔LLMCallEvent correlation contract (keys + join path) per F5 fold. Rigby SIGN routed on this arc pin `pa-c5b235f7b15f45be`.
3. **ADR-A authoring** (parallel drafting, ratifies after ADR-B per F4 fold) — `MISSION_RUNNER_ENABLED` + `RIGBY_DELEGATION_ENABLED` staged-enable posture per F8-iii + rollback triggers per §7.2/§7.3.
4. **ADR-C authoring** (parallel drafting, optional ratifies third per F4 fold) — D74 six-axis correlation-spine posture with **explicit retention constraints as required decision input** per F2 fold. May conclude "retention follow-on required" without shipping IB-1799-T0-02 code.

### 9.2 ADR checkpoint (per §4.3 substitution)

Three admitted intake rows carry `risk_class: NEEDS_ADR` or
`NEEDS_RIGBY_SIGN_PLUS_CHRIS`. **ADR corpus precondition** (per IOS
v1.2 §4.3, patch PR #2943) satisfied via Option (a) P0 prep PR bundling
`IB-Q1-BOOT-01`. Stage 2 opens only after P0 ships.

### 9.3 Verification-method interface (per F7 fold)

Rather than pre-committing three variant verification queries (one per
ADR-B outcome shape), Stage 1 defines an interface:

> **For a PA turn, retrieve executions + tool calls + ops evidence
> with correlation.**

Concrete implementation supplied at Stage 3 pre-flight after ADR-B
ratifies model/table shape:

- If ADR-B ratifies per-turn AgentExecution write: query
  `AgentExecution.objects.filter(input_data__source='pa', ...)` +
  `ToolCallRecord.objects.filter(execution_id__in=<>).values('trace_id',
  ...)` join.
- If ADR-B ratifies per-message span: analogous query with different
  granularity axis (message_id / turn_id).
- If ADR-B ratifies dedicated `PAAgentExecution` model: query the new
  model with same correlation semantics.

**Rigby-exercised surface** (interface-level) at Stage 5: PA chat call
→ `agent_tool.execute` OR `execution_history_tool.recent` OR
`deliverable_provenance_tool.trace` — all three exposed as the
interface's user-facing shape regardless of ADR-B storage decision.

---

## 10. Stage checklist snapshot (per IOS v1.2 §4.3 substitution — added by IOS, NOT in Playbook §11.1)

Grep-friendly enumeration of every exit-gate item for every planned
stage. One line each. A future Claude session can grep this section
to determine current stage without interpretation.

```
[STAGE 1 SCOPING] — status: exit-gate-cleared 2026-07-06
  [x] Scoping doc drafted per IOS v1.2 §4.3 template + substitutions
  [x] Playbook §11.1 sections present: §1 + §2 + §3 + §4 + §5 + §6 + §7 + §8 + §9 + Appendix
  [x] §4.3 substitution §3 applied (intake items)
  [x] §4.3 substitution §5 applied (PR sequence)
  [x] §4.3 substitution §7 applied (anti-scope + reversibility)
  [x] §4.3 substitution §9 applied (next step + ADR checkpoint)
  [x] §4.3 substitution §10 added (Stage checklist snapshot — this section)
  [x] Rigby SIGN Cycle 1 routed (single-batch × 4-Q per IOS §7.2)
  [x] Rigby SIGN Cycle 1 verdict: SIGN-with-edits overall; no BLOCKED
  [x] All 8 folds applied (F1-F8): F1 T0-01 architecture-only; F2 retention decision-input; F3 P2 unconditional (SIGN-clean); F4 ADR-B ratifies first; F5 PA↔LLMCallEvent correlation; F6 anti-scope bullet 7 replaced; F7 verification interface; F8 3 risks added
  [x] Chris "agree all F1-F8" ratified 2026-07-06
  [x] Scoping doc `status: draft → active` (frontmatter updated at ratification)
  [x] Fresh arc-scoped SIGN pin minted (`session_tool.create_fresh label='ios-arc-open-I-0100'` → `pa-c5b235f7b15f45be`)
  [x] Ratification pin `pa-39d3694312ab4326` retired (at seed PR merge 2026-07-06; verified via wrapper header)
  [x] `tools/pa_local.sh --conversation` rotated to `pa-c5b235f7b15f45be`
  [x] `OPEN_ARCS.md#In-progress` gains Arc I-0100 row (this bundle)
  [x] BACKLOG rows `IB-1799-T1-01/02/03` flipped `TRIAGED → IN_ARC (I-0100)` (this bundle)
  [x] IB-1799-T0-01 architecture-only admit documented in scoping §3.2 (BACKLOG flip deferred to Stage 2 ADR-C opening per F1 fold)
  [x] IB-1799-T0-02 conditional admit documented in scoping §3.3 (per F2 fold)
  [x] IDBT-0001 1799-slice discharge scope declared in scoping §3.5

[STAGE 2 DESIGN-PREP + ADR] — status: P0 prep in-flight (ADR authoring NOT opened per Chris directive)
  [x] IOS v1.2 §4.3 ADR corpus precondition satisfied at Stage 2 opening (Option (a) executed — bundle IB-Q1-BOOT-01 shipped as P0 prep PR #2948 merged 2026-07-06)
  [x] P0 prep PR: `IB-Q1-BOOT-01` shipped (`ADR-0001-establish-adr-corpus.md` + `docs/adr/` dir) — **PR #2948 merged 2026-07-06; cascade co-located per IOS v1.3 §12.5.a (33 chunks embedded for ADR-0001); IDBT-0002 recorded delegating RAG embed-invalidation gap to Group 2100 RAG**
  [x] IOS v1.4 fresh-session Stage 2 readiness refinement shipped (PR #2949 merged 2026-07-06) — codifies §4.3.0 stage_state enum + §4.3 Stage 2 Entry gate + design-prep equivalence + §7.2 ADR SIGN cadence + §15.15 00-START-NEXT ownership; unblocks Stage 2 mechanically for fresh Claude sessions
  [x] Stage 2 opening ceremony executed (this housekeeping PR): scoping frontmatter `stage: 1 → 2` + `stage_state: p0-prep-merged → active` per §4.3.0 v1.4 discipline; BACKLOG `IB-Q1-BOOT-01: IN_ARC → SHIPPED` with `pr_refs: #2948` per §2.2 v1.4 Discipline B inline syntax; 00-START-NEXT-SESSION.md refreshed per §15.15 (Stage-transition PR type)
  [x] IOS v1.5 design-prep first-class artifact refinement shipped (PR #2952 merged 2026-07-06) — replaces v1.4 §4.3 Stage 2 equivalence rule with mandatory standalone design-prep artifact for every NEEDS_ADR intake with design_state POSTURE_PENDING or NONE; §4.3.a canonical template + §14.2.a Chris refinement-authority prerogative formalization
  [x] ADR-B drafted + design-prep authored (`I-0100_design_prep_adr_b_pa_write_shape.md`) — PA-write shape + PA↔LLMCallEvent correlation contract per F5 fold; ships in PR #2951 alongside ADR-0002
  [x] ADR-A drafted + design-prep authored (`I-0100_design_prep_adr_a_mission_runner_staged_enable.md`) — RIGBY_DELEGATION_ENABLED staged-enable posture per F8-iii + rollback triggers (correcting scoping doc §5 P3 MISSION_RUNNER_ENABLED naming to sole runtime flag `RIGBY_DELEGATION_ENABLED` per ADR-0003 §2.1 F8 terminology binding); ships in PR #2953 alongside ADR-0003
  [ ] ADR-C drafted (D74 spine posture with retention as decision input per F2) — OPTIONAL per F4 fold; not authored (Chris directive pending)
  [x] Rigby SIGN cycle on ADR-B → Chris "agree all F1-F8" ratified 2026-07-06 (FIRST per F4 fold); PR #2951 merged. ADR-0002 accepted.
  [x] Rigby SIGN cycle on ADR-A → Chris "agree all F1-F8" ratified 2026-07-06 (SECOND per F4 fold); PR #2953 merged. ADR-0003 accepted.
  [ ] Rigby SIGN cycle on ADR-C (optional) → Chris "ratified" (THIRD per F4 fold) — DEFERRED unless Chris directs authoring

[STAGE 3 PRE-FLIGHT]
  [ ] Rollback plan committed per PR (§5.4) — matched to §7.2 table
  [ ] Regression tests named per PR (`test_tool_call_record_trace_id.py`, `test_ops_run_event_execution_id.py`, PA-write test file per ADR-B)
  [ ] Verification-method interface (§9.3) FILLED with concrete queries per ADR-B outcome (per F7 fold)
  [ ] Bounded fleet-adjacent audit run per F6 fold: repo grep + Rigby `ops_tool.celery_task_history` 30d + ORM probe of `FleetServiceKey`/`FleetPAChatAuditRow`/`FleetArtifact` for `td-N-hex` regex
  [ ] Volume threshold set for R2 mitigation (baseline OpsRunEvent measurement → threshold)
  [ ] D48 stability-probe gate: warmup-ping every Stage 6 arc-close checklist item
  [ ] Sub-agent verifier-loop scope declared (any Explore/Plan/general-purpose sub-agent claims spot-checked at parent level)
  [ ] Stage 3 Rigby SIGN routed (single-batch × 2-Q per §7.2 conditional — TRIGGERED because P4 may add migration AND fleet-key surface touched by P2)

[STAGE 4 BUILD]
  [ ] P0 prep PR (IB-Q1-BOOT-01) opened → merged → intake row `SHIPPED`
  [ ] P1 prep PR (this bundle) opened → merged (this PR)
  [ ] P2 (IB-1799-T1-01 trace_id fix) PR opened → §5.2 pre-merge gates → merged → Rigby exercises → intake `SHIPPED`
  [ ] P3 (IB-1799-T1-03 MISSION_RUNNER staged unlock) PR opened → staged rollout complete → intake `SHIPPED`
  [ ] P4 (IB-1799-T1-02 PA→AgentExecution) PR opened → §5.2 pre-merge gates → merged → intake `SHIPPED`

[STAGE 5 VERIFY]
  [ ] For each of P2/P3/P4: Rigby exercises via verification-method interface (§9.3) per ADR-B concrete query
  [ ] Claude verifies independently via ORM / git log / file Read per MEMORY `feedback_claude_directs_rigby_then_verifies`
  [ ] Local + prod parity check IF fleet-key surface (P2 confirmed fleet-adjacent per §7.1 bullet 7)
  [ ] R1/R2/R3 rollback triggers exercised in staging: hidden td-N-hex reader test; OpsRunEvent volume threshold breach test; RIGBY_DELEGATION handler synthetic error test
  [ ] Any regressions → route back to Stage 3 with fix plan

[STAGE 6 CLOSE]
  [ ] Canonical close doc `I-010099_observability_spine_implementation_close.md` authored (mirrors Playbook §11.3 xx99 template; §1-§9 close sections per IOS §4.3 Stage 6)
  [ ] `cross_domain_integration_audit.md §14.N` refresh entry appended (D10 hard gate)
  [ ] 4-step docs cascade run: `build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`
  [ ] `build_docs_provenance` run
  [ ] `embed_documents --all-unembedded` run; PR body cites chunk count as evidence per MEMORY `feedback_cascade_pr_must_include_embed_step`
  [ ] `OPEN_ARCS.md` row flipped In-progress → Closed
  [ ] BACKLOG.md rows IB-1799-T1-01/02/03 flipped `IN_ARC → SHIPPED` with populated `pr_refs`
  [ ] IB-1799-T0-01 BACKLOG row flipped `IN_ARC → SHIPPED` (or `RETRACTED` if ADR-C deferred; or `DEFERRED` per Chris directive)
  [ ] IMPLEMENTATION_DEBT.md IDBT-0001 1799-slice discharge recorded; any new debt (RETRACTED / TECH_DEBT_ACCRUED / CONTRACT_VIOLATION) recorded
  [ ] Arc-scoped SIGN pin `pa-c5b235f7b15f45be` retired via `session_tool.retire force=true` (§7.2 isolation-pin discipline)
  [ ] `tools/pa_local.sh --conversation` restored to paused-research pin `pa-44a6eb70d8814e34` per IOS §15.14 restoration rule (unless second implementation arc opens in same phase)
  [ ] Chris "commit it" for Stage 6 exit
```

---

## Appendix — Frontmatter provenance

- **Arc identity ratification:** RATIFICATION §2 Axis 2 —
  `docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md`.
- **IOS text:** `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md`
  v1.2 (patch PR #2943 in flight) §4.3 Stage 1 template + substitutions
  + exit gate + ADR corpus precondition; §7.2 Stage 1 SIGN discipline;
  §15.14 pin lifecycle.
- **xx99 source:** `docs/research/domains/observability/1799_observability_canonical_summary.md`
  §1 verdict (D74 six-axis + retention pattern inconsistency); §5.9 body
  systems drift; §5.10 employee count drift; §8.1 T0/Gate 1+2; §8.2 T1
  items 1+2+3+4.
- **Backlog seed:** `docs/research/implementation/BACKLOG.md` T1 Arc
  I-0100 seed rows (lines 162-164 pre-Stage-1; flipped `IN_ARC (I-0100)`
  in this PR).
- **Debt discharge:** `docs/research/implementation/IMPLEMENTATION_DEBT.md`
  IDBT-0001 resolution_path Option 2 (arc-scoped incremental discharge
  of 1799 slice).
- **Rigby SIGN Cycle 1 record (this doc's verifier_loop):** routed on
  fresh arc pin `pa-c5b235f7b15f45be` 2026-07-06; 4 Qs × 2 sub-Qs = 8
  sub-verdicts; 7 SIGN-with-edits + 1 SIGN-clean (Q2a P2 unconditional
  ship); no BLOCKED; Cycle 2 not requested. Chris ratified "agree all
  F1-F8" same day.
- **MEMORY rules bound to this arc:** `feedback_docs_cascade_at_every_close`,
  `feedback_cascade_pr_must_include_embed_step`,
  `feedback_rigby_sign_worker_instability_recovery`,
  `feedback_fleet_caller_verification_before_celery_deletes`,
  `feedback_procfile_makefile_queue_parity` (P4 potential),
  `feedback_verify_before_deleting_dead_code` (if any writer path is
  deemed dead), `feedback_claude_directs_rigby_then_verifies` (Stage 5
  verification loop), `feedback_llm_autofills_boolean_params_with_false`
  (test on real DB for QuerySet-heavy code per P2 test authoring),
  `feedback_test_real_db_for_queryset_semantics` (Stage 5 real-DB
  verification), `feedback_fail_loud_first_then_root_cause_then_telemetry`
  (any regression 3-PR arc).
