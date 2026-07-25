# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2958 CLOSED. Golden Evals arc-slice 4 shipped: `evals/tier1/workflow_orchestration_agent.yaml` (PR #3557, HEAD `e2b7e92c2`). 801 lines, 13 prompts, all 5 fault-injection categories (5 happy + 2 each of tool_timeout / data_unavailable / ambiguous_input / bad_input). Fourth canon_version=1 file — substrate frozen at S2955 continues holding cleanly across four different agent shapes: SIA (closed-world platform-health, autonomous single-prompt), ResearchAgent (open-world LLM synthesis, human-diverse 26-prompt), DevOpsAgent (config-generation dual-path advisory-vs-config-gen), and now WorkflowOrchestrationAgent (no-LLM-tool-calls programmatic dispatch through 18 hardcoded workflow templates). DB-grounded via Rigby ORM T1 SIGN — verified 9 30d execs (7 completed / 2 failed) = 9 all-time (no history before 2026-06-25) + CLAIM 5 (0 failed rows with empty error_message; 7 completed rows all have empty-string not null). Both all-time failures = same Celery watchdog kill on morning_brief smoke tests (2026-06-25) — modeled as `workflow_timeout_01_watchdog_kill`. This is the thinnest arc traffic yet (9 vs SIA 37 / Research 37 / DevOps 13) AND 100% smoke traffic (zero real customer use of the 18 creative-workflow templates) AND a new agent shape (`tools = []`, programmatic dispatch, no LLM function calls) — all four coverage limits honestly called out in YAML header. Live wrapper bug discovered at authoring: legacy `_compile_final_result` at services/…:5341 emits `steps` key; wrapper at agents/…:315 reads `step_results` — data.step_results always empty on happy paths. Documented as TRANSITIONAL with fallback contract in `canonical_field_mapping.evidence_pointers` (per Rigby S2958 T2 disposition); code-fix PR expected in follow-up slice. Chris D-verdict `yes` via TERMINAL 2026-07-25 (`yes ship it`) — Ledger #17 count unchanged at 4 (Chris used terminal path, not Chat UI relay). **S2959 first-action = author `evals/tier1/legal_doc_drafter_agent.yaml`** — 5th Tier-1 slice per arc plan.

**Arc-precedent substrate frozen at canon_version=1** (unchanged from S2955; must apply to all remaining Tier-1 YAMLs):
1. `schema_version: 1` + `canon_version: 1` at file top.
2. `canonical_field_mapping` block declaring `mapping_source: native|derived` per canon field with named derivation rules — S2963 validators MUST consult, never invent mappings.
3. `fault_injection` uses effect-based contract (`component` + `fault.{type, params}`) with `python.{...}` as backend-adapter appendix — portable beyond Python-mock. **S2957 fold**: prefer service-level selectors (`core.agents.*` / `core.services.*`) over library-internal Python paths (`openai.resources.*`) for portability across SDK upgrades.
4. `one_of` acceptance-criteria capped at ≤2 branches with mandatory `why` string per branch.

**S2958 additions to canon (informative, non-breaking — apply where relevant to remaining slices):**
5. **Per-workflow-shape evidence-tier requirements** — for agents where different execution shapes produce different evidence sets, `canonical_field_mapping.evidence_pointers` MAY carve per-shape rules rather than a single hard requirement.
6. **INTEGRATION EVIDENCE tier distinction** — out-of-band DB row inspection is NOT in Tier-1 validator scope; belongs to a separate integration/side-effect verification suite. Keep Tier-1 validators pure on the AgentResult artifact.
7. **TRANSITIONAL marking pattern** — when a YAML documents a fold requiring code follow-up, use the "TRANSITIONAL — code-fix PR expected" phrasing so it doesn't calcify. Include an explicit v1.1 removal clause.
8. **Timeout-string brittleness avoidance** — do NOT couple timeout assertions to exact wording. Assert stable discriminator fields (`data.timeout=True` on wrapper-side FuturesTimeoutError; structured status fields when available) + broad substring patterns for message text.

Reference implementations (in order of canon fidelity):
- `evals/tier1/system_intelligence_agent.yaml` — canon_version=1 original (463 lines, autonomous single-prompt shape, closed-world).
- `evals/tier1/research_agent.yaml` — second reference (523 lines, 26-prompt human-diverse, open-world LLM synthesis, `error_message` empty-vs-null semantic verifier note).
- `evals/tier1/devops_agent.yaml` — third reference (612 lines, dual-path advisory-vs-config-gen shape, thin-traffic honesty pattern + service-level selector fold).
- `evals/tier1/workflow_orchestration_agent.yaml` — fourth reference (801 lines, no-LLM-tool-calls programmatic-dispatch shape, per-workflow-shape evidence cascade + transitional wrapper-bug pattern + integration-evidence tier distinction).

**Refreshed 2026-07-25 (S2958 close).** Gap-map headline unchanged: `100 validated_full / 2 untested` — the 2 are `agent_capability_drift_tool` (S2953-shipped) + `agent_job_status` (S2952-shipped), both untested-by-design at ship time. This session shipped a spec file only, no PA tool changes.

**PRs shipped this session (S2958):**
- u-d-b PR **#3557** — S2958 Golden Evals Tier-1 slice 4: WorkflowOrchestrationAgent YAML (1 file, +801/-0, spec-only).
- u-d-b PR **#TBD** — S2958 close cascade (handoff + this 00-START refresh + wrapper pin bump).

**Twin mirrors shipped this session (S2958 slice):**
- S2958 slice 4 content mirror: `d05172f0-2660-41d7-9354-d56bf2a8dbac` (Donkey Betz workspace, `initiative_phase_doc`, `category='governance'`, Ledger #16 re-hit **11th cumulative**, sticky-cleared via `deliverable_tool.clear_diagnostic`).
- S2958 slice 4 ratification envelope: `e519e7a9-934b-40a1-b074-e114ce576733` (Donkey Betz workspace, `ratification_record`, `category='governance'`, diagnostic clean on create).

Full S2955 slice-1 + S2956 slice-2 + S2957 slice-3 mirror IDs preserved in prior handoffs.

**Files shipped this session (S2958 slice):**
- **NEW** `evals/tier1/workflow_orchestration_agent.yaml` — fourth Tier-1 canonical prompt suite (801 lines, 13 prompts).

**Post-merge:** PR #3557 was spec-only (YAML config, no code), no worker impact → no `make celery-recycle` required (PLAYBOOK-7.4.4 applies to code-shipping PRs).

**Governance:** Rigby SIGN cycle T1→T3. T1 tool-grounded PASS (`orm_inspect_tool.count_by` + `filter` on `AgentExecution`, 5 real tool_runs not rubber-stamp) — all 5 volume/integrity claims match DB reality. T2 zoom-out surfaced 6 folds — 4 disposed appropriately in-PR (F1 wrapper key-mismatch → TRANSITIONAL marking + explicit v1.1 removal clause; F3 6-tier cascade → tier-6 reclassified as INTEGRATION EVIDENCE non-blocking for Tier-1; Fold B timeout brittle-string → pattern relaxed + `data.timeout=True` codified as stable discriminator; Residual #2 → Deliverable-only workflow evidence exception added). 2 folds deferred: F2 (NEW AGENT SHAPE framing) → coverage-note only, stay canon_v1; Fold A (arc-substrate tool_runs global rule) → S2962 arc-close. 1 fold next-slice: Fold C (ambig vs bad_input remediation separation).

**Rigby Tool Gap Ledger:**
- **RE-HIT (Ledger #16, 11th time cumulative)** — `deliverable_tool.create` diagnostic-flag bug on `initiative_phase_doc`. S2958 content mirror flagged `missing_initiative_id`; sticky-cleared via `deliverable_tool.clear_diagnostic`. Consistent behavior across 11 sessions.
- **NO CHANGE — Ledger #17 count remains 4** — Chris used terminal ratification path directly (`yes ship it` typed in terminal), bypassing Chat UI relay entirely. Interesting datapoint: terminal ratification IS a viable low-friction path when Chris is present at the terminal; Chat UI relay gap only bites when Chris returns to Chat UI after Claude has moved on. Design task `f3f140f9-87bf-488b-8757-eab5d8058f45` remains valid for the Chat-UI-only path.
- **Rigby residual observations (informative-only, not blocking)** — Non-blocker residuals from T3 pass: (1) once wrapper fix lands, v1.1 must REMOVE the fallback mapping (already documented in header + mapping block); (2) once wrapper fix restores tier 1, Deliverable-only workflow exception collapses; (3) other slices should adopt the timeout brittle-string discipline (already codified as canon addition 8).

Full session context: `docs/handoffs/SESSION_2958_GOLDEN_EVALS_SLICE_4_WORKFLOW_YAML.md`.

---

## S2959 open sequence

**S2959 first-action = author `evals/tier1/legal_doc_drafter_agent.yaml`** — 5th Tier-1 slice. Agent lives at `core/agents/legal/legal_doc_drafter_agent.py:474`. Pull LegalDocDrafterAgent 30d + all-time volume snapshot via Rigby ORM before authoring (mirror S2958 T0 shape). If traffic is thin, call out honestly in header per S2957/S2958 precedent.

### Universal open sequence

1. **Live-verify S2953 drift scanner still healthy:**
   - `bash tools/pa_local.sh "run agent_capability_drift_tool action=summary"` — expect shape (83/92/59/1 → 77+2 or drifted numbers with same shape).
   - `python manage.py scan_agent_capability_drift --json | jq .totals` — same from CLI.
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline `100 validated_full / 2 untested`. The 2 untested (`agent_capability_drift_tool`, `agent_job_status`) are expected.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2959 pin (retired at S2958 close cascade).
4. **Read the four arc-precedent substrate references BEFORE authoring** (any is sufficient; all four demonstrate different agent shapes):
   - `evals/tier1/system_intelligence_agent.yaml` — canon_version=1 original (closed-world, autonomous).
   - `evals/tier1/research_agent.yaml` — human-diverse open-world (includes `error_message` semantic note).
   - `evals/tier1/devops_agent.yaml` — dual-path advisory-vs-config-gen (thin-traffic honesty pattern + service-level selector fold).
   - `evals/tier1/workflow_orchestration_agent.yaml` — no-LLM-tool-calls programmatic dispatch (per-workflow-shape cascade + transitional-fold pattern + integration-evidence tier distinction).
5. **Open S2959 slice** — see scope below.

### S2959 arc-slice scope: LegalDocDrafterAgent YAML

**Target file:** `evals/tier1/legal_doc_drafter_agent.yaml`.
**Agent source:** `core/agents/legal/legal_doc_drafter_agent.py:474`.

**Substrate-freeze reference:** any of the 4 shipped canon_version=1 YAMLs. Mirror all 4 core substrate patterns (schema_version + canon_version, canonical_field_mapping, effect-based fault_injection with service-level selectors, one_of ≤2 branches with mandatory why). Apply S2958 additions where relevant (per-shape evidence carving, integration-evidence tier separation, TRANSITIONAL marking if any code-follow-up folds surface, timeout brittle-string avoidance).

**Coverage target:** 5–20 prompts across all 5 fault-injection categories. Pull all 30d prompts via `orm_inspect_tool.filter` on `AgentExecution` where `owner_agent="LegalDocDrafterAgent"`, `created_at__gte="2026-06-25T00:00:00Z"` and select the most representative 5 for happy-path coverage.

**Volume header hygiene (per S2957/S2958 refinements):**
- Use full-calendar-30d bound (`created_at >= 2026-06-25T00:00:00Z`), not `now - timedelta(days=30)`.
- Distinguish non-null vs non-empty `error_message` explicitly in failure counts.
- Honestly call out coverage limits (thin traffic / shape mismatch / small failure sample) — every Tier-1 YAML gets this treatment.
- Prefer service-level fault_injection selectors over library-internal paths.
- Legal domain has particular sensitivity — hallucination invariants must be extra sharp given the buyer-facing risk of drafting incorrect legal language.

**Out of scope for S2959:** validator code (JSON Schema executors, Pydantic model runners) and `run_golden_evals` mgmt cmd. Those come after all 8 Tier-1 YAMLs are shipped.

**Also out of scope for S2959:** the WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR (F1 from S2958). That's a separate follow-up that can happen any time before S2963 validators are written (which is when v1.1 tightening of the S2958 YAML would occur).

**Estimated 1 session** for this slice.

### Golden Evals arc structure (updated at S2958 close)

**Tier-1 YAMLs — 4 of 8 shipped:**
- ✅ **S2955 slice 1 — SystemIntelligenceAgent** (PR #3551, HEAD `d2acf9c92`) — SHIPPED. canon_version=1 substrate frozen.
- ✅ **S2956 slice 2 — ResearchAgent** (PR #3553, HEAD `c8815cd38`) — SHIPPED. Substrate validated on open-world/LLM-synthesis shape.
- ✅ **S2957 slice 3 — DevOpsAgent** (PR #3555, HEAD `98ba0e06b`) — SHIPPED. Substrate validated on dual-path advisory-vs-config-gen shape; service-level selector fold codified.
- ✅ **S2958 slice 4 — WorkflowOrchestrationAgent** (PR #3557, HEAD `e2b7e92c2`) — SHIPPED. Substrate validated on no-LLM-tool-calls programmatic-dispatch shape; transitional wrapper-bug pattern + per-workflow-shape evidence cascade + integration-evidence tier distinction codified.
- ⏭ **S2959 slice 5 — LegalDocDrafterAgent** — NEXT.
- **S2960 slice 6 — ContentWriterAgent.**
- **S2961 slice 7 — CompetitorAnalysisAgent.**
- **S2962 slice 8 — PersonalAssistant (Rigby)** + arc-close review (canon uniformity across all 8 YAMLs; canon_version=2 open discussion for `health_status` open-world + dual-path enum concerns + arc-substrate tool_runs rule).

**After all 8 Tier-1 YAMLs shipped:**
- **S2963** — Validators (JSON Schema execution + Pydantic model runners consuming `canonical_field_mapping` + `expected_output_shape` + `acceptance_criteria`).
- **S2964** — Harness (`run_golden_evals` mgmt cmd + `GoldenEvalRun` table + nightly beat task).
- **Follow-up code-fix PR** for the S2958 WorkflowOrchestrationAgent wrapper key-name mismatch — canonicalize legacy `_compile_final_result` and wrapper on one key; then v1.1 revision of `workflow_orchestration_agent.yaml` to tighten assertions.
- **After arc close** — A1 Phase 1 first-slice opens (Chris's 4 gating questions still block; see below).

_Note: session numbers above are ESTIMATED linear progression assuming 1 slice per session. Actual session numbers may drift if a slice takes >1 session or if a non-arc session interleaves._

### Capability Manifest — build spec (parallel-track from A1 Phase 1 start)

_(unchanged — see prior S2953 close snapshots; not part of Golden Evals arc)_

### A1 Phase 1 still ahead (after Golden Evals arc closes)

Chris's 4 open questions from scoping deliverable `7870eca9` still gate Phase 1 code:

1. **Minimum evidence standard** we promise? (run IDs + failure signature samples vs metrics only)
2. **Default turnaround SLA** we can consistently hit without heroics?
3. Sell as **agent-system audit** (end-to-end) or **toolchain reliability audit** (tools/contracts) first?
4. **Legal posture** for handling customer logs (retention window, deletion guarantee, allowed data types)?

### Deferred queue (updated at S2958 close)

**S2958 additions:**
- **WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR** (F1 from S2958 T2) — canonicalize legacy `_compile_final_result` at services/workflow_orchestration_agent.py:5341 (emits `'steps'`) and wrapper at agents/workflow_orchestration_agent.py:315 (reads `'step_results'`) on ONE key. After fix, v1.1 revision of `evals/tier1/workflow_orchestration_agent.yaml` REMOVES the fallback mapping (per Rigby's F1 residual guidance). Can happen any time before S2963 validators are written.
- **Fold A carry-forward (arc-substrate)** — Tier-1 must-have-tool_runs global rule vs orchestration agents. Rigby: "Tier 1 requires tool-grounded verification when tool_runs exist; otherwise require deterministic artifact fields + provenance pointers." Track for S2962 arc-close discussion.
- **Fold C next-slice-fold** — ambiguous_input vs bad_input remediation posture separation. Ambiguous → clarifying question / request params; bad_input → reject with reason + example fix. Apply to remaining slices (S2959+) as authoring discipline.

**Carry forward from S2957:**
- **Fold #1 (S2957 T2) — `health_status` dual-path enum add for advisory-vs-config-gen agents** — DevOpsAgent's advisory path (no tool_calls, message-only) currently collapses into `healthy`. Rigby suggests `healthy_no_tools_expected`. Track for `canon_version=2` arc-close at S2962 alongside S2956 Fold #5.
- **Failure-mode lens documentation** — `devops_timeout_01` uses `SoftTimeLimitExceeded` (agent-side lens). Observable is external-cleanup-marked-failed (external lens). Both legitimate; document convention in S2963 validator design so validators handle both.

**Carry forward from S2956:**
- **Ledger #16 recipe drift (dual-route)** — recipe should document both routes: (a) direct Claude ORM (set diagnostic_* fields to None), (b) via Rigby PA (`deliverable_tool.clear_diagnostic` sticky-cleared sentinel). Update `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic.md`.
- **`orm_inspect_tool` distinct-count guardrail** — group-by on text fields rejected as "expensive/unbounded". Won't scale for agents with >200 30d executions. Consider `distinct_values_capped` action or `hash_distinct` shortcut.
- **Fold #5 (S2956 T2) — `health_status` derivation over-degrade for open-world agents** — UNKNOWN→degraded may over-penalize research/analysis agents. Track for `canon_version=2` at S2962.
- **Fold #6b (S2956 T2) — Tier-1 canon uniformity review** — comment-vs-usage mismatches across YAMLs. Track for arc-close review at S2962.

**S2955 additions (carry forward):**
- **Bound-annotation discipline for volume claims in YAML headers** — consider making calendar-30d the canonical bound across all Tier-1 YAML volume snapshots + drift-scanner + audit tools.

**S2954 additions (carry forward):**
- **00-START validated-full gap-map lint sync** — consider CI check that the 00-START headline pulls from `build_pa_tool_audit` live rather than manual editing.

**S2953 additions (carry forward):**
- Drift scanner invariant 4 (rerouted-must-be-labeled) — requires `AgentRerouteEntry`-style queryable model.
- Curate `capabilities_exceptions.yaml` — 77 active findings at HEAD. Walk each; tier-classify or fix.
- Fix run_agent dispatch-response agent-name echo (from S2952) — echo mapping-canonical CamelCase, not input string.

**S2952 carry-forward:**
- Schema/handler drift scanner (PA tool contract — separate from S2953's agent drift scanner).
- `agent_job_status` design gap harder fix (reserve `AgentExecution` row synchronously at dispatch).

**Signal-dispatch queue (from S2951, carry forward):**
- **(A11)** 6th signal-dispatch rule (`sentiment_shift` or `market_movement`) — no volume evidence yet.
- **(NEW-6)** Fair-share round-robin scanning in `scan_and_dispatch()`.
- **(NEW-7)** Persist `per_rule_diagnostics` per `scan_run_id`.
- **(NEW-8)** Per-pattern effectiveness attribution for reused agents.

**Long-standing (carry forward from S2951):**
- **(D)** Docs restructuring arc — Chris-ratified S2800, still queued.
- **(B)** Slice 5-hardening — 3-4 executable invariants deferred at S2928.
- **(E)** Tier 2 lint promotion — envelope-JSON top-level-key parse.
- **(H)** generate_newsletter dry_run default flip.
- **(I)** bulk_archive statuses autofill robustness — 2nd trigger at S2945.
- **Envelope enhancement** (record-only S2942) — `verify_hint` + `would_write_count` for dry_run.
- **Close-ceremony ledger-flip checklist** (meta-fix, record-only S2942).
- **Deliverable v1 template retrofit** (record-only S2943).

---

## What's forbidden at S2958 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2958 new forbidden entries:** none.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2958 additions to the deferred queue:**
- WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR (can happen pre-S2963; unblocks v1.1 tightening of `workflow_orchestration_agent.yaml`).
- Fold A (arc-substrate tool_runs global rule) — S2962 arc-close discussion.

**Carry forward from S2957:**
- `health_status` dual-path enum add (canon_version=2 discussion at S2962, alongside S2956 Fold #5).
- Failure-mode lens documentation (S2963 validator design note).

**Carry forward from S2956:**
- Ledger #16 recipe drift (dual-route documentation).
- `orm_inspect_tool` distinct-count guardrail.
- `health_status` derivation refactor for open-world agents (canon_version=2 at S2962).
- Tier-1 canon uniformity review (arc-close S2962).

**S2954 additions (carry forward):**
- 00-START validated-full gap-map lint sync.

**S2953 additions (carry forward):**
- Drift scanner invariant 4 (rerouted-must-be-labeled).
- `capabilities_exceptions.yaml` curation.

**S2952 additions (carry forward):**
- Schema/handler drift scanner (PA tool contract).
- `agent_job_status` design gap harder fix.
- Dispatch-response agent-name echo cleanup.

**S2951 additions (carry forward):**
- `MarketIntelligenceCoordinator` rename — cosmetic only.
- `brainstorm_tool.create` real panel implementation.
- CompetitorAnalysisAgent spider sources (LangSmith/Langfuse/Helicone/Arize).

**Long-standing (carry forward from S2951):**
- Fair-share round-robin scanning.
- Persist per_rule_diagnostics in audit table.
- Advanced paste-UUID fallback for cluster picker.
- Server-side search + pagination on `/eligible/`.
- Z1/Z2/Z4 signal-dispatch UI polish (Rigby S2947 zoom-outs).
- Rank + cap + paginate follow-ups (Rigby S2946).
- Per-pattern-type diversity floors.
- Ledger candidates (S2945/2944/2943/2942 backlog).
- Docs restructuring arc (Chris-ratified S2800).
- W2 #1 / #2b / #2c pending Chris re-slate.
- LLMCallLog field splits.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) + pre-A1 capability triage (S2952) + capability substrate (S2953 Drift Scanner) + Golden Evals arc-open + slice work (S2954-S2958) are adjacent-domain net-new engineering + arc substrate, not sweep work.

**Total remaining sweep tools: 0.**

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force)

1. **Spend lane:** A4 warm-up uses separate budget lane/cap; must NOT consume A1 shipping spend.
2. **Evidence tag:** All A4 artifacts labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up constrained to fixed timebox + fixed send count (3-5 total intros).
6. **No bespoke follow-ups.**

---

## For fuller context (S2846 → S2958)

See:
- **S2958 handoff (current):** `docs/handoffs/SESSION_2958_GOLDEN_EVALS_SLICE_4_WORKFLOW_YAML.md`
- **S2958 shipped code:** `evals/tier1/workflow_orchestration_agent.yaml` (801 lines, 13 prompts, fourth canon_version=1 reference)
- **S2957 handoff:** `docs/handoffs/SESSION_2957_GOLDEN_EVALS_SLICE_3_DEVOPS_YAML.md`
- **S2957 shipped code:** `evals/tier1/devops_agent.yaml` (612 lines, 13 prompts, third canon_version=1 reference)
- **S2956 handoff:** `docs/handoffs/SESSION_2956_GOLDEN_EVALS_SLICE_2_RESEARCH_YAML.md`
- **S2956 shipped code:** `evals/tier1/research_agent.yaml` (523 lines, 13 prompts, second canon_version=1 reference)
- **S2955 handoff:** `docs/handoffs/SESSION_2955_GOLDEN_EVALS_SLICE_1_SIA_YAML.md`
- **S2955 shipped code:** `evals/tier1/system_intelligence_agent.yaml` (canon_version=1 original reference, 463 lines, 13 prompts)
- **S2954 arc-open handoff:** `docs/handoffs/SESSION_2954_GOLDEN_EVALS_ARC_OPEN.md`
- **S2954 arc-open scoping doc:** `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md` (95 lines)
- **S2953 handoff:** `docs/handoffs/SESSION_2953_DRIFT_SCANNER.md`
- **S2953 shipped code:**
  - `core/services/agent_capability_drift.py` — scanner service
  - `capabilities_exceptions.yaml` — allowlist
  - `core/management/commands/scan_agent_capability_drift.py` — CLI
  - `core/services/pa_tool_schemas.py` — `agent_capability_drift_tool` schema
  - `core/services/td_handlers_agents.py:6713-6764` — `_handle_agent_capability_drift`
  - `core/services/tool_dispatcher.py:406-408` — handler registration
  - `core/tests/test_agent_capability_drift.py` — 9 tests
- **S2952 handoff:** `docs/handoffs/SESSION_2952_PRE_A1_CAPABILITY_FIXES.md`
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope (unchanged, S2951):** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
- **Ledger #17 (S2957):** `db316865-d08c-4cc1-9d8e-cfac249e8c89` — Chat UI response-relay gap (unchanged this session)
- **Chat UI relay design task (S2957):** `f3f140f9-87bf-488b-8757-eab5d8058f45`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
