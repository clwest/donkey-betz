# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2959 CLOSED. Golden Evals arc-slice 5 shipped: `evals/tier1/legal_doc_drafter_agent.yaml` (PR #3559, HEAD `8fa60421f`). 794 lines, 13 prompts, all 5 fault-injection categories (5 happy + 2 each of tool_timeout / data_unavailable / ambiguous_input / bad_input). Fifth canon_version=1 file — substrate frozen at S2955 continues holding cleanly across five different agent shapes: SIA (closed-world platform-health, autonomous single-prompt), ResearchAgent (open-world LLM synthesis, human-diverse 26-prompt), DevOpsAgent (config-generation dual-path advisory-vs-config-gen), WorkflowOrchestrationAgent (no-LLM-tool-calls programmatic dispatch through 18 hardcoded workflow templates), and now LegalDocDrafterAgent (10-tool GPT-selection Standard Mode + Denied-Motion Routing Branch, 8,169-line largest agent file in the arc). DB-grounded via direct ORM at authoring T0 — verified 5 30d execs (all completed / 0 failed) = 12 all-time (all completed / 0 failed, earliest 2026-06-23) + error_message='' empty-string across all 12 rows. This is the thinnest arc traffic tied with WorkflowOrchestrationAgent (5 vs Workflow 9 vs SIA 37 / Research 37 / DevOps 13) AND narrowest (100% Colorado parenting-time modification variants across all 5 30d prompts) AND zero-failure sample (all fault-injection cases constructed) — all four coverage limits honestly called out in YAML header. **Legal-domain hallucination invariants extra-sharp per S2959 arc-slice scope note** — beyond general `no_unsupported_claims`, YAML encodes 7 legal-specific predicates: `no_statutory_citations`, `no_outcome_predictions`, `no_strategy_language`, `non_party_detected_when_present`, `jdf_form_reference_correct_or_title_only`, `mythology_enforcer_passed`, `declaration_contains_penalty_of_perjury_language`. Chris D-verdict `yes` via TERMINAL 2026-07-25 (`yes ship it and forward-carry fold 3`) — Ledger #17 count unchanged at 4 (Chris used terminal path, not Chat UI relay). **S2960 first-action = author `evals/tier1/content_writer_agent.yaml`** — 6th Tier-1 slice per arc plan.

**Arc-precedent substrate frozen at canon_version=1** (unchanged from S2955; must apply to all remaining Tier-1 YAMLs):
1. `schema_version: 1` + `canon_version: 1` at file top.
2. `canonical_field_mapping` block declaring `mapping_source: native|derived` per canon field with named derivation rules — S2963 validators MUST consult, never invent mappings.
3. `fault_injection` uses effect-based contract (`component` + `fault.{type, params}`) with `python.{...}` as backend-adapter appendix — portable beyond Python-mock. **S2957 fold**: prefer service-level selectors (`core.agents.*` / `core.services.*`) over library-internal Python paths (`openai.resources.*`) for portability across SDK upgrades.
4. `one_of` acceptance-criteria capped at ≤2 branches with mandatory `why` string per branch.

**S2958 additions to canon (informative, non-breaking — apply where relevant to remaining slices):**
5. **Per-execution-shape evidence-tier requirements** — for agents where different execution shapes produce different evidence sets, `canonical_field_mapping.evidence_pointers` MAY carve per-shape rules rather than a single hard requirement. S2959 applied to Standard Mode vs Denied-Motion Routing Branch.
6. **INTEGRATION EVIDENCE tier distinction** — out-of-band DB row inspection is NOT in Tier-1 validator scope; belongs to a separate integration/side-effect verification suite. Keep Tier-1 validators pure on the AgentResult artifact.
7. **TRANSITIONAL marking pattern** — when a YAML documents a fold requiring code follow-up, use the "TRANSITIONAL — code-fix PR expected" phrasing so it doesn't calcify. Include an explicit v1.1 removal clause.
8. **Timeout-string brittleness avoidance** — do NOT couple timeout assertions to exact wording. Assert stable discriminator fields (`data.timeout=True` on wrapper-side FuturesTimeoutError; structured status fields when available) + broad substring patterns for message text.

**S2959 additions to canon (informative, non-breaking — apply where relevant to remaining slices):**
9. **Domain-sensitivity acceptance predicates** — for agents whose failure surface carries elevated buyer-facing cost (legal drafting, medical, financial advice), encode domain-specific predicates alongside the general `no_unsupported_claims`. LegalDocDrafterAgent example: 7 legal-specific predicates layered on top of the general canon. Reserve for agents where hallucination cost is CATEGORICAL (not just quality-degrading).
10. **Routing-branch framing (not "new shape")** — when an agent has an auto-detected alternate execution path that bypasses the primary tool-dispatch flow (e.g., LegalDocDrafterAgent's DENIED MOTION MODE, forced-tool_choice paths, guardrail deflections), frame as "routing branch inside the same agent contract" — NOT as a "new shape". Keeps acceptance criteria unified and avoids inviting canon_version=2 creep before S2962. Same success + evidence + hallucination invariants apply across branches.
11. **Coverage-limits actionable conclusion** — the THIN/NARROW/ZERO-FAILURE/BUYER-RISK caveat pile should resolve to ONE actionable conclusion line (e.g., "treat as SCHEMA + HALLUCINATION-INVARIANT validation, not performance assurance"). Prevents caveat stacking from making the artifact read as self-invalidating.

Reference implementations (in order of canon fidelity):
- `evals/tier1/system_intelligence_agent.yaml` — canon_version=1 original (463 lines, autonomous single-prompt shape, closed-world).
- `evals/tier1/research_agent.yaml` — second reference (523 lines, 26-prompt human-diverse, open-world LLM synthesis, `error_message` empty-vs-null semantic verifier note).
- `evals/tier1/devops_agent.yaml` — third reference (612 lines, dual-path advisory-vs-config-gen shape, thin-traffic honesty pattern + service-level selector fold).
- `evals/tier1/workflow_orchestration_agent.yaml` — fourth reference (801 lines, no-LLM-tool-calls programmatic-dispatch shape, per-workflow-shape evidence cascade + transitional wrapper-bug pattern + integration-evidence tier distinction).
- `evals/tier1/legal_doc_drafter_agent.yaml` — fifth reference (794 lines, 10-tool GPT-selection Standard Mode + Denied-Motion Routing Branch, domain-sensitivity predicates + routing-branch framing + coverage-limits actionable conclusion).

**Refreshed 2026-07-25 (S2959 close).** Gap-map headline unchanged: `100 validated_full / 2 untested` — the 2 are `agent_capability_drift_tool` (S2953-shipped) + `agent_job_status` (S2952-shipped), both untested-by-design at ship time. This session shipped a spec file only, no PA tool changes.

**PRs shipped this session (S2959):**
- u-d-b PR **#3559** — S2959 Golden Evals Tier-1 slice 5: LegalDocDrafterAgent YAML (1 file, +794/-0, spec-only).
- u-d-b PR **#TBD** — S2959 close cascade (handoff + this 00-START refresh + wrapper pin bump).

**Twin mirrors shipped this session (S2959 slice):**
- S2959 slice 5 content mirror: `d615ffbd-da45-44b6-9882-ddfc471e2a3c` (Donkey Betz workspace, `initiative_phase_doc`, `category='governance'`, Ledger #16 re-hit **12th cumulative**, sticky-cleared via `deliverable_tool.clear_diagnostic`).
- S2959 slice 5 ratification envelope: `f3e5f746-c084-4457-8f49-a855ff5c67e0` (Donkey Betz workspace, `ratification_record`, `category='governance'`, diagnostic clean on create).

Full S2955 slice-1 + S2956 slice-2 + S2957 slice-3 + S2958 slice-4 mirror IDs preserved in prior handoffs.

**Files shipped this session (S2959 slice):**
- **NEW** `evals/tier1/legal_doc_drafter_agent.yaml` — fifth Tier-1 canonical prompt suite (794 lines, 13 prompts).

**Post-merge:** PR #3559 was spec-only (YAML config, no code), no worker impact → no `make celery-recycle` required (PLAYBOOK-7.4.4 applies to code-shipping PRs).

**Governance:** Rigby SIGN cycle T1→T3. T1 tool-grounded PASS on volume + line refs via real `orm_inspect_tool.filter` (12 all-time rows returned raw) + `repo_tool.read_file` at exact line refs (474, 1229, 1252, 1424-1426, 1464, 1481) + `repo_tool.search` for all 10 declared tools at their line positions — no rubber-stamp. DISAGREE on 3 CLAIMS with honest reasons: (a) tool count 9 → 10 declared / 11 total-schema (in-PR fixed); (b) YAML structure (Rigby didn't re-verify in thread — independently confirmed via Claude's `yaml.safe_load` structural check); (c) devops parity (same reason). T2 zoom-out surfaced 4 folds — 3 disposed in-PR (fold 1 tool count, fold 2 "NEW SHAPE" → "routing branch", fold 4 coverage-limits actionable conclusion); 1 fold FORWARD-CARRY: fold 3 evidence-tier ladder mechanization → S2962 arc-close (canon-wide question about S2963 validator consumption of prose derivation_specs vs typed evidence tiers). Chris D-verdict via terminal: `yes ship it and forward-carry fold 3`.

**Rigby Tool Gap Ledger:**
- **Expected RE-HIT at close cascade (Ledger #16, 12th time cumulative)** — `deliverable_tool.create` diagnostic-flag bug on `initiative_phase_doc` will fire when the S2959 content-mirror deliverable is created. Sticky-clear via `deliverable_tool.clear_diagnostic` per prior 11-session recipe.
- **NO CHANGE — Ledger #17 count remains 4** — Chris used terminal ratification path directly (`yes ship it and forward-carry fold 3` typed in terminal), bypassing Chat UI relay entirely. Consistent with S2957 + S2958 pattern (three consecutive terminal ratifications). Design task `f3f140f9-87bf-488b-8757-eab5d8058f45` remains valid for the Chat-UI-only path.
- **Rigby T1 discipline HELD** — explicit DISAGREE on CLAIMS 4/5 for "no thread tool_runs" reason is a POSITIVE signal per `feedback_verify_rigby_tool_runs_before_trusting_sign` (opposite of rubber-stamp).

Full session context: `docs/handoffs/SESSION_2959_GOLDEN_EVALS_SLICE_5_LEGAL_YAML.md`.

---

## S2960 open sequence

**S2960 first-action = author `evals/tier1/content_writer_agent.yaml`** — 6th Tier-1 slice. Locate agent source via `grep -r "class ContentWriterAgent" core/agents/` and open the file. Pull ContentWriterAgent 30d + all-time volume snapshot via direct ORM before authoring (mirror S2959 T0 shape — Rigby's `orm_inspect_tool.count_by` currently doesn't propagate the `group_by='status'` argument correctly, so use direct `python manage.py shell` for the volume snapshot and use Rigby for line-ref verification via `repo_tool.read_file` + `repo_tool.search`). If traffic is thin, call out honestly in header per S2957/S2958/S2959 precedent.

### Universal open sequence

1. **Live-verify S2953 drift scanner still healthy:**
   - `bash tools/pa_local.sh "run agent_capability_drift_tool action=summary"` — expect shape (83/92/59/1 → 77+2 or drifted numbers with same shape).
   - `python manage.py scan_agent_capability_drift --json | jq .totals` — same from CLI.
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline `100 validated_full / 2 untested`. The 2 untested (`agent_capability_drift_tool`, `agent_job_status`) are expected.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2960 pin (retired at S2959 close cascade).
4. **Read the five arc-precedent substrate references BEFORE authoring** (any is sufficient; all five demonstrate different agent shapes):
   - `evals/tier1/system_intelligence_agent.yaml` — canon_version=1 original (closed-world, autonomous).
   - `evals/tier1/research_agent.yaml` — human-diverse open-world (includes `error_message` semantic note).
   - `evals/tier1/devops_agent.yaml` — dual-path advisory-vs-config-gen (thin-traffic honesty pattern + service-level selector fold).
   - `evals/tier1/workflow_orchestration_agent.yaml` — no-LLM-tool-calls programmatic dispatch (per-workflow-shape cascade + transitional-fold pattern + integration-evidence tier distinction).
   - `evals/tier1/legal_doc_drafter_agent.yaml` — 10-tool GPT-selection + routing-branch shape + domain-sensitivity predicates + coverage-limits actionable conclusion.
5. **Open S2960 slice** — see scope below.

### S2960 arc-slice scope: ContentWriterAgent YAML

**Target file:** `evals/tier1/content_writer_agent.yaml`.
**Agent source:** discover via `grep -r "class ContentWriterAgent" core/agents/`.

**Substrate-freeze reference:** any of the 5 shipped canon_version=1 YAMLs. Mirror all 4 core substrate patterns (schema_version + canon_version, canonical_field_mapping, effect-based fault_injection with service-level selectors, one_of ≤2 branches with mandatory why). Apply S2958 additions (per-shape evidence carving, integration-evidence tier separation, TRANSITIONAL marking if any code-follow-up folds surface, timeout brittle-string avoidance) AND S2959 additions (domain-sensitivity predicates IF applicable to content quality domain, routing-branch framing if agent has auto-detected alternate paths, coverage-limits actionable conclusion).

**Coverage target:** 5–20 prompts across all 5 fault-injection categories. Pull all 30d prompts via direct ORM on `AgentExecution` where `owner_agent="ContentWriterAgent"`, `created_at__gte="2026-06-25T00:00:00Z"` and select the most representative 5 for happy-path coverage.

**Volume header hygiene (per S2957/S2958/S2959 refinements):**
- Use full-calendar-30d bound (`created_at >= 2026-06-25T00:00:00Z`), not `now - timedelta(days=30)`.
- Distinguish non-null vs non-empty `error_message` explicitly in failure counts.
- Honestly call out coverage limits (thin traffic / shape mismatch / small failure sample) — every Tier-1 YAML gets this treatment.
- Prefer service-level fault_injection selectors over library-internal paths.
- Content-writing domain sensitivity: brand-voice fidelity, source attribution, factual grounding, plagiarism avoidance. Consider whether ContentWriterAgent output flows into buyer-facing deliverables (newsletters, blog posts, marketing copy) — if so, hallucination-cost is buyer-critical and warrants domain-specific predicates per S2959 canon addition 9.

**Out of scope for S2960:** validator code (JSON Schema executors, Pydantic model runners) and `run_golden_evals` mgmt cmd. Those come after all 8 Tier-1 YAMLs are shipped.

**Also out of scope for S2960:** the WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR (F1 from S2958). That's a separate follow-up that can happen any time before S2963 validators are written.

**Estimated 1 session** for this slice.

### Golden Evals arc structure (updated at S2959 close)

**Tier-1 YAMLs — 5 of 8 shipped:**
- ✅ **S2955 slice 1 — SystemIntelligenceAgent** (PR #3551, HEAD `d2acf9c92`) — SHIPPED. canon_version=1 substrate frozen.
- ✅ **S2956 slice 2 — ResearchAgent** (PR #3553, HEAD `c8815cd38`) — SHIPPED. Substrate validated on open-world/LLM-synthesis shape.
- ✅ **S2957 slice 3 — DevOpsAgent** (PR #3555, HEAD `98ba0e06b`) — SHIPPED. Substrate validated on dual-path advisory-vs-config-gen shape; service-level selector fold codified.
- ✅ **S2958 slice 4 — WorkflowOrchestrationAgent** (PR #3557, HEAD `e2b7e92c2`) — SHIPPED. Substrate validated on no-LLM-tool-calls programmatic-dispatch shape; transitional wrapper-bug pattern + per-workflow-shape evidence cascade + integration-evidence tier distinction codified.
- ✅ **S2959 slice 5 — LegalDocDrafterAgent** (PR #3559, HEAD `8fa60421f`) — SHIPPED. Substrate validated on 10-tool GPT-selection + routing-branch shape; domain-sensitivity predicates + routing-branch framing + coverage-limits actionable conclusion codified.
- ⏭ **S2960 slice 6 — ContentWriterAgent** — NEXT.
- **S2961 slice 7 — CompetitorAnalysisAgent.**
- **S2962 slice 8 — PersonalAssistant (Rigby)** + arc-close review (canon uniformity across all 8 YAMLs; canon_version=2 open discussion for `health_status` open-world + dual-path enum concerns + arc-substrate tool_runs rule + **NEW S2959 fold 3: evidence-tier ladder mechanization**).

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

### Deferred queue (updated at S2959 close)

**S2959 additions:**
- **Fold 3 — Evidence-tier ladder mechanization (canon-wide, all 5 slices)** — Rigby-flagged, Chris-ratified for S2962 arc-close as third canon_v2 candidate alongside S2956 + S2957 `health_status` variants. Question: does S2963 validator implementation consume prose `derivation_spec` via text-parsing, or does canon need typed evidence-tier entries (selector + predicate + applicability)? Applies to all 5 shipped YAMLs; if canon needs upgrade, upgrade as batch not per-slice.
- **`orm_inspect_tool.count_by` group_by argument not propagating** — Rigby's tool call at S2959 T0 defaulted `group_key='id'` even though I asked for `group_by='status'`. Direct ORM verification bypassed cleanly (`python manage.py shell`), but this is a tool-surface bug worth ledger entry for the Rigby Tool Gap Ledger. Consider filing as Ledger #18 with reproducer.

**Carry forward from S2958:**
- **WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR** (F1 from S2958 T2) — canonicalize legacy `_compile_final_result` at services/workflow_orchestration_agent.py:5341 (emits `'steps'`) and wrapper at agents/workflow_orchestration_agent.py:315 (reads `'step_results'`) on ONE key. After fix, v1.1 revision of `evals/tier1/workflow_orchestration_agent.yaml` REMOVES the fallback mapping (per Rigby's F1 residual guidance). Can happen any time before S2963 validators are written.
- **Fold A carry-forward (arc-substrate)** — Tier-1 must-have-tool_runs global rule vs orchestration agents. Rigby: "Tier 1 requires tool-grounded verification when tool_runs exist; otherwise require deterministic artifact fields + provenance pointers." Track for S2962 arc-close discussion.
- **Fold C next-slice-fold** — ambiguous_input vs bad_input remediation posture separation. Ambiguous → clarifying question / request params; bad_input → reject with reason + example fix. Apply to remaining slices (S2960+) as authoring discipline.

**Carry forward from S2957:**
- **Fold #1 (S2957 T2) — `health_status` dual-path enum add for advisory-vs-config-gen agents** — DevOpsAgent's advisory path (no tool_calls, message-only) currently collapses into `healthy`. Rigby suggests `healthy_no_tools_expected`. Track for `canon_version=2` arc-close at S2962 alongside S2956 Fold #5 and S2959 Fold 3.
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

## What's forbidden at S2959 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2959 new forbidden entries:** none.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2959 additions to the deferred queue:**
- Evidence-tier ladder mechanization (canon-wide) — S2962 arc-close as canon_v2 candidate #3.
- `orm_inspect_tool.count_by` group_by not propagating — file as Ledger #18 with reproducer.

**Carry forward from S2958:**
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

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) + pre-A1 capability triage (S2952) + capability substrate (S2953 Drift Scanner) + Golden Evals arc-open + slice work (S2954-S2959) are adjacent-domain net-new engineering + arc substrate, not sweep work.

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

## For fuller context (S2846 → S2959)

See:
- **S2959 handoff (current):** `docs/handoffs/SESSION_2959_GOLDEN_EVALS_SLICE_5_LEGAL_YAML.md`
- **S2959 shipped code:** `evals/tier1/legal_doc_drafter_agent.yaml` (794 lines, 13 prompts, fifth canon_version=1 reference)
- **S2958 handoff:** `docs/handoffs/SESSION_2958_GOLDEN_EVALS_SLICE_4_WORKFLOW_YAML.md`
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
