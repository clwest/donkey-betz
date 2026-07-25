# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2961 CLOSED. Golden Evals arc-slice 7 shipped: `evals/tier1/competitor_analysis_agent.yaml` (PR #3563, HEAD `75f8da29a`). 1232 lines, 13 prompts, all 5 fault-injection categories (5 happy + 2 each of tool_timeout / data_unavailable / ambiguous_input / bad_input). Seventh canon_version=1 file — substrate frozen at S2955 continues holding cleanly across seven different agent shapes: SIA (closed-world platform-health, autonomous single-prompt), ResearchAgent (open-world LLM synthesis, human-diverse 26-prompt), DevOpsAgent (config-generation dual-path advisory-vs-config-gen), WorkflowOrchestrationAgent (no-LLM-tool-calls programmatic dispatch through 18 hardcoded workflow templates), LegalDocDrafterAgent (10-tool GPT-selection Standard Mode + Denied-Motion Routing Branch), ContentWriterAgent (5-routing-branch single-LLM-call agent with `tools=[]`), and now CompetitorAnalysisAgent (5-routing-branch multi-tool GPT-dispatch agent with 5 tools + web_search inheritance, THINNEST-TRAFFIC agent in the arc). DB-grounded via direct ORM at authoring T0 (Rigby T1-T3 SIGN tool-verified with `orm_inspect_tool.filter` + `orm_inspect_tool.get` + `orm_inspect_tool.count_by` + `repo_tool.read_file` + `repo_tool.search`) — verified 2 30d execs (2 completed / 0 failed / 0 cancelled) = 11 all-time (11 completed / 0 failed / 0 cancelled, earliest 2026-06-23) + **ZERO non-empty error_message rows ever** (only Tier-1 agent shipped with zero failure history). This is THINNEST-TRAFFIC in the arc — 2 30d / 11 all-time vs SIA 37 / Research 37 / DevOps 13 / Workflow 9 / Content 7 / Legal 5. Only 1 of 11 all-time prompts is a real competitor-analysis ask (2026-06-25 Donkey Betz identify-competitors, exec `3bc1df00-2288-4a9c-baef-c5ede3f1d502`, preserved verbatim as `competitor_happy_01` STANDARD-path anchor). 4/5 routing branches encoded on code-spec, not observed traffic (2nd trigger of S2960 Fold A). All coverage limits honestly called out in YAML header. **Competitive-intelligence buyer-facing risk invariants proportional per S2959 canon addition 9** — 5 domain-sensitivity predicates matching Content's 5 (fewer than Legal's 7): `no_fabricated_competitor_names`, `no_fabricated_pricing_financial_or_headcount_metrics`, `no_fabricated_executive_quotes_or_attributions`, `distinguishes_evidence_from_inference`, `honors_data_freshness_or_admits_gap`. Chris D-verdict `yes` via TERMINAL 2026-07-25 — **5 consecutive terminal ratifications** S2957→S2961 (Ledger #17 count unchanged at 4). **S2962 first-action = author `evals/tier1/personal_assistant_agent.yaml` (or Rigby-named equivalent) + arc-close canon-uniformity review** — 8th and FINAL Tier-1 slice per arc plan, followed by canon_v2 candidate ratification.

**Arc-precedent substrate frozen at canon_version=1** (unchanged from S2955; must apply to slice 8):
1. `schema_version: 1` + `canon_version: 1` at file top.
2. `canonical_field_mapping` block declaring `mapping_source: native|derived` per canon field with named derivation rules — S2963 validators MUST consult, never invent mappings.
3. `fault_injection` uses effect-based contract (`component` + `fault.{type, params}`) with `python.{...}` as backend-adapter appendix — portable beyond Python-mock. **S2957 fold**: prefer service-level selectors (`core.agents.*` / `core.services.*`) over library-internal Python paths (`openai.resources.*`) for portability across SDK upgrades.
4. `one_of` acceptance-criteria capped at ≤2 branches with mandatory `why` string per branch.

**S2958 additions to canon (informative, non-breaking — apply where relevant to slice 8):**
5. **Per-execution-shape evidence-tier requirements** — for agents where different execution shapes produce different evidence sets, `canonical_field_mapping.evidence_pointers` MAY carve per-shape rules rather than a single hard requirement.
6. **INTEGRATION EVIDENCE tier distinction** — out-of-band DB row inspection is NOT in Tier-1 validator scope; belongs to a separate integration/side-effect verification suite. Keep Tier-1 validators pure on the AgentResult artifact.
7. **TRANSITIONAL marking pattern** — when a YAML documents a fold requiring code follow-up, use the "TRANSITIONAL — code-fix PR expected" phrasing so it doesn't calcify. Include an explicit v1.1 removal clause.
8. **Timeout-string brittleness avoidance** — do NOT couple timeout assertions to exact wording. Assert stable discriminator fields + broad substring patterns for message text.

**S2959 additions to canon (informative, non-breaking — apply where relevant to slice 8):**
9. **Domain-sensitivity acceptance predicates** — for agents whose failure surface carries elevated buyer-facing cost, encode domain-specific predicates alongside the general `no_unsupported_claims`. S2961 applied 5 competitive-intelligence predicates (proportional harm class — same as Content).
10. **Routing-branch framing (not "new shape")** — when an agent has an auto-detected alternate execution path, frame as "routing branch inside the same agent contract" — NOT as a "new shape". Same success + evidence + hallucination invariants apply across branches.
11. **Coverage-limits actionable conclusion** — the THIN/NARROW/ZERO-FAILURE/BUYER-RISK caveat pile should resolve to ONE actionable conclusion line.

Reference implementations (in order of canon fidelity):
- `evals/tier1/system_intelligence_agent.yaml` — canon_version=1 original (463 lines, autonomous single-prompt shape, closed-world).
- `evals/tier1/research_agent.yaml` — second reference (523 lines, 26-prompt human-diverse, open-world LLM synthesis).
- `evals/tier1/devops_agent.yaml` — third reference (612 lines, dual-path advisory-vs-config-gen shape, thin-traffic honesty pattern + service-level selector fold).
- `evals/tier1/workflow_orchestration_agent.yaml` — fourth reference (801 lines, no-LLM-tool-calls programmatic-dispatch shape, per-workflow-shape evidence cascade + transitional wrapper-bug pattern + integration-evidence tier distinction).
- `evals/tier1/legal_doc_drafter_agent.yaml` — fifth reference (794 lines, 10-tool GPT-selection + routing-branch shape, domain-sensitivity predicates + coverage-limits actionable conclusion).
- `evals/tier1/content_writer_agent.yaml` — sixth reference (950 lines, 5-routing-branch single-LLM-call `tools=[]`, proportional domain-sensitivity predicates + representative-not-verbatim failure-replay pattern + softened diagnostic-mode contract language).
- `evals/tier1/competitor_analysis_agent.yaml` — **NEW seventh reference** (1232 lines, 5-routing-branch multi-tool GPT-dispatch, THINNEST-TRAFFIC honesty pattern + verbatim-single-real-prompt anchor + spider-first principal-contract predicate + boundary-condition evidence-gate disclaimer + inline Rigby-fold-disposition header section).

**Refreshed 2026-07-25 (S2961 close).** Gap-map headline unchanged: `100 validated_full / 2 untested` — the 2 are `agent_capability_drift_tool` (S2953-shipped) + `agent_job_status` (S2952-shipped), both untested-by-design at ship time. This session shipped a spec file only, no PA tool changes.

**PRs shipped this session (S2961):**
- u-d-b PR **#3563** — S2961 Golden Evals Tier-1 slice 7: CompetitorAnalysisAgent YAML (1 file, +1232/-0, spec-only).
- u-d-b PR **#TBD** — S2961 close cascade (handoff + this 00-START refresh + wrapper pin bump).

**Twin mirrors shipped this session (S2961 slice):**
- S2961 slice 7 content mirror: `56664ff4-1da4-43a8-944b-d09c09a8a5a7` (Donkey Betz workspace, `initiative_phase_doc`, `category='governance'`, **Ledger #16 RE-HIT 14th cumulative** — flag `missing_initiative_id` set on create but not surfaced in Rigby's initial "no re-hit" report; `session_lifecycle close` caught via CommandError; cleared via `deliverable_tool.clear_diagnostic`).
- S2961 slice 7 ratification envelope: `6815da1e-a991-43d3-a285-33561500df31` (Donkey Betz workspace, `ratification_record`, `category='governance'`, diagnostic clean on create).

Full S2955 slice-1 + S2956 slice-2 + S2957 slice-3 + S2958 slice-4 + S2959 slice-5 + S2960 slice-6 mirror IDs preserved in prior handoffs.

**Files shipped this session (S2961 slice):**
- **NEW** `evals/tier1/competitor_analysis_agent.yaml` — seventh Tier-1 canonical prompt suite (1232 lines, 13 prompts).

**Post-merge:** PR #3563 was spec-only (YAML config, no code), no worker impact → no `make celery-recycle` required (PLAYBOOK-7.4.4 applies to code-shipping PRs).

**Governance:** Rigby SIGN cycle T1→T3 tool-grounded. T1 surfaced 6 zoom-out folds with tool-verified volume + line-ref grounding (orm_inspect_tool.filter for 11 all-time / 2 30d / 0 failure rows raw; orm_inspect_tool.get for verbatim task-string byte-match on exec 3bc1df00; repo_tool.read_file for line refs at 128/147/187/636/660/712/890). T2 AGREE on all 4 in-PR fold-fix outcomes (γ harness-fixture removal, δ spider_query principal-contract predicate, ε evidence-gate realism disclaimer, forward-carry header documentation); 1 new zoom-out on inline fold-doc pattern (style drift from prior 6 slices — normalize at S2962). T3 AGREE on remaining line refs (940/1009/1060/1119/1129/1150/1153/1557/1558/1560/1588) + substrate-reference existence check + count_by CLOSED as not-a-bug. Chris D-verdict via terminal: `yes`.

**Rigby Tool Gap Ledger:**
- **Ledger #16 RE-HIT — 14th cumulative** — the `deliverable_tool.create` diagnostic-flag bug fired on the `initiative_phase_doc` content mirror (as usual since S2955). Rigby's initial no-re-hit report was incomplete — the flag was set on the row but not visible in the `create` response detail block. `session_lifecycle close` caught the discrepancy via CommandError (`--content-mirror-id flagged diagnostic_status='diagnostic'`), forcing clear via `deliverable_tool.clear_diagnostic` before the close could complete. Second-order finding: Rigby's initial-report observability gap for this bug is distinct from the underlying create-bug — the recipe drift forward-carry (dual-route documentation) from S2956 should be prioritized higher at S2962 arc-close.
- **NO CHANGE — Ledger #17 count remains 4** — Chris used terminal ratification path directly (`yes` typed in terminal), bypassing Chat UI relay entirely. Consistent with S2957 + S2958 + S2959 + S2960 pattern (**5 consecutive terminal ratifications S2957→S2961**). Design task `f3f140f9-87bf-488b-8757-eab5d8058f45` remains valid for the Chat-UI-only path.
- **Ledger #18 candidate CLOSED as NOT-A-BUG** — T3 confirmed `orm_inspect_tool.count_by(field="status")` handles group-by cleanly. Prior S2959/S2960 "count_by group_by bug" was schema misuse (`group_by` vs `field` kwarg naming), not a code bug. Remove from Deferred Queue.
- **Rigby T1/T2/T3 discipline HELD** — 6 substantive zoom-out folds surfaced, 3 in-PR fixes accepted, 3 forward-carries logged, 1 NOT-A-BUG finding, tool_runs verbose on every SIGN turn. Positive signal per `feedback_verify_rigby_tool_runs_before_trusting_sign` (opposite of rubber-stamp).

Full session context: `docs/handoffs/SESSION_2961_GOLDEN_EVALS_SLICE_7_COMPETITOR_YAML.md`.

---

## S2962 open sequence

**S2962 first-action = author `evals/tier1/personal_assistant_agent.yaml` (or Rigby-named equivalent) + arc-close canon-uniformity review** — 8th and FINAL Tier-1 slice per arc plan. This slice closes the Tier-1 spec-authoring phase; S2963 opens validator implementation.

**Two-component slice-8 work:**

**(A) Slice 8 YAML** — `evals/tier1/personal_assistant_agent.yaml` (verify agent class name via `grep -r "class.*Personal.*Agent\|class.*Rigby" core/agents/` before authoring). PersonalAssistant is the buyer-facing surface Rigby herself uses; largest tool surface (117 schemas + 160 handlers per PLATFORM_INVENTORY); most cross-cutting agent in the arc. Traffic will be THICK (probably highest 30d execution count of any Tier-1 slice — Rigby fires dozens of times per session, and the S2957-S2961 5-session terminal-ratification streak proves the load).

**(B) Arc-close canon-uniformity review** — before ratifying slice 8, review all 8 shipped Tier-1 YAMLs against the accumulated fold-carry-forward queue (see Deferred queue below).

### Universal open sequence

1. **Live-verify S2953 drift scanner still healthy:**
   - `bash tools/pa_local.sh "run agent_capability_drift_tool action=summary"` — expect shape (83/92/59/1 → 77+2 or drifted numbers with same shape).
   - `python manage.py scan_agent_capability_drift --json | jq .totals` — same from CLI.
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline `100 validated_full / 2 untested`. The 2 untested (`agent_capability_drift_tool`, `agent_job_status`) are expected.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2962 pin (retired at S2961 close cascade).
4. **Read the seven arc-precedent substrate references BEFORE authoring** (any is sufficient; all seven demonstrate different agent shapes):
   - `evals/tier1/system_intelligence_agent.yaml` — canon_version=1 original (closed-world, autonomous).
   - `evals/tier1/research_agent.yaml` — human-diverse open-world (includes `error_message` semantic note).
   - `evals/tier1/devops_agent.yaml` — dual-path advisory-vs-config-gen (thin-traffic honesty pattern + service-level selector fold).
   - `evals/tier1/workflow_orchestration_agent.yaml` — no-LLM-tool-calls programmatic dispatch (per-workflow-shape cascade + transitional-fold pattern + integration-evidence tier distinction).
   - `evals/tier1/legal_doc_drafter_agent.yaml` — 10-tool GPT-selection + routing-branch shape + domain-sensitivity predicates + coverage-limits actionable conclusion.
   - `evals/tier1/content_writer_agent.yaml` — 5-routing-branch single-LLM-call (`tools=[]`) + proportional domain-sensitivity predicates + representative-not-verbatim failure-replay pattern + softened diagnostic-mode contract language.
   - `evals/tier1/competitor_analysis_agent.yaml` — 5-routing-branch multi-tool GPT-dispatch (5 tools + web_search inheritance) + THINNEST-TRAFFIC honesty pattern + verbatim-single-real-prompt anchor + spider-first principal-contract predicate + boundary-condition evidence-gate disclaimer + inline Rigby-fold-disposition header section (S2961 innovation; canon-uniformity question for arc-close).
5. **Open S2962 slice 8 + arc-close review** — see scope below.

### S2962 arc-slice scope: PersonalAssistant (Rigby) YAML + arc-close ratification

**Target file:** `evals/tier1/personal_assistant_agent.yaml` (verify agent class name first).
**Agent source:** discover via `grep -r "class.*Personal.*Agent\|class.*Rigby" core/agents/`.

**Substrate-freeze reference:** any of the 7 shipped canon_version=1 YAMLs. Mirror all 4 core substrate patterns (schema_version + canon_version, canonical_field_mapping, effect-based fault_injection with service-level selectors, one_of ≤2 branches with mandatory why). Apply S2958 additions (per-shape evidence carving, integration-evidence tier separation, TRANSITIONAL marking if any code-follow-up folds surface, timeout brittle-string avoidance) AND S2959 additions (domain-sensitivity predicates, routing-branch framing if agent has auto-detected alternate paths, coverage-limits actionable conclusion).

**Coverage target:** 5–20 prompts across all 5 fault-injection categories. Pull all 30d prompts via direct ORM on `AgentExecution` where `owner_agent="<agent-class-name>"`, `created_at__gte="2026-06-25T00:00:00Z"` and select the most representative 5-8 for happy-path coverage. Given PA is thick-traffic, expect richer happy_path sampling than any prior slice.

**Domain-sensitivity considerations for PersonalAssistant:** PA is the buyer surface — Rigby's outputs ARE the platform's voice to the user. Hallucination costs are HIGH but distributed differently than analytic agents: (a) fabricated tool-run receipts (claiming a tool ran when it didn't), (b) fabricated deliverable IDs (referencing UUIDs that don't exist), (c) fabricated workspace or user context (claiming knowledge of Chris's projects that isn't grounded), (d) tool_runs empty vs claimed (rubber-stamp signal from feedback_verify_rigby_tool_runs_before_trusting_sign). Consider 4-6 PA-specific predicates layered on the general `no_unsupported_claims`.

**Volume header hygiene (per S2957/S2958/S2959/S2960/S2961 refinements):**
- Use full-calendar-30d bound (`created_at >= 2026-06-25T00:00:00Z`), not `now - timedelta(days=30)`.
- Distinguish non-null vs non-empty `error_message` explicitly in failure counts.
- Honestly call out coverage limits (thin traffic / shape mismatch / small failure sample) — every Tier-1 YAML gets this treatment.
- Prefer service-level fault_injection selectors over library-internal paths.
- **Failure-replay honesty (per S2960 Rigby T2 CLAIM 5 DISAGREE)**: if using a specific historical failure row as inspiration, either replay it verbatim OR frame it as "REPRESENTATIVE OF REAL FAILURE PATTERN (not a verbatim replay)".

**Arc-close canon-uniformity review scope:** Before ratifying slice 8, walk the accumulated fold-carry-forward queue below. Ratify or reject each canon_v2 candidate; ratify or defer each canon-consistency question. This is a SEPARATE ratification decision from slice-8 shipping; can happen at slice-8 close cascade OR opened as an independent S2963-prep session.

**Out of scope for S2962:** validator code (JSON Schema executors, Pydantic model runners) and `run_golden_evals` mgmt cmd. Those come at S2963.

**Also out of scope for S2962:** the WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR (F1 from S2958). That's a separate follow-up that can happen any time before S2963 validators are written.

**Estimated 1-2 sessions** for slice 8 authoring + arc-close review. May split if arc-close review takes its own session.

### Golden Evals arc structure (updated at S2961 close)

**Tier-1 YAMLs — 7 of 8 shipped:**
- ✅ **S2955 slice 1 — SystemIntelligenceAgent** (PR #3551, HEAD `d2acf9c92`) — SHIPPED. canon_version=1 substrate frozen.
- ✅ **S2956 slice 2 — ResearchAgent** (PR #3553, HEAD `c8815cd38`) — SHIPPED. Substrate validated on open-world/LLM-synthesis shape.
- ✅ **S2957 slice 3 — DevOpsAgent** (PR #3555, HEAD `98ba0e06b`) — SHIPPED. Substrate validated on dual-path advisory-vs-config-gen shape; service-level selector fold codified.
- ✅ **S2958 slice 4 — WorkflowOrchestrationAgent** (PR #3557, HEAD `e2b7e92c2`) — SHIPPED. Substrate validated on no-LLM-tool-calls programmatic-dispatch shape; transitional wrapper-bug pattern + per-workflow-shape evidence cascade + integration-evidence tier distinction codified.
- ✅ **S2959 slice 5 — LegalDocDrafterAgent** (PR #3559, HEAD `8fa60421f`) — SHIPPED. Substrate validated on 10-tool GPT-selection + routing-branch shape; domain-sensitivity predicates + routing-branch framing + coverage-limits actionable conclusion codified.
- ✅ **S2960 slice 6 — ContentWriterAgent** (PR #3561, HEAD `10b6b3ab1`) — SHIPPED. Substrate validated on 5-routing-branch single-LLM-call (`tools=[]`) shape; proportional domain-sensitivity predicates + representative-not-verbatim failure-replay pattern + softened diagnostic-mode contract language codified.
- ✅ **S2961 slice 7 — CompetitorAnalysisAgent** (PR #3563, HEAD `75f8da29a`) — SHIPPED. Substrate validated on 5-routing-branch multi-tool GPT-dispatch shape; THINNEST-TRAFFIC honesty pattern + spider-first principal-contract predicate + boundary-condition evidence-gate disclaimer + inline fold-disposition header codified. First-miss on Ledger #16 diagnostic-flag bug.
- ⏭ **S2962 slice 8 — PersonalAssistant (Rigby)** + arc-close review — NEXT.

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

### Deferred queue (updated at S2961 close)

**S2961 additions:**
- **Fold α — Routing-branch encoding vs traffic reality (canon-wide, all 7 slices)** — 2nd trigger of S2960 Fold A. Rigby-flagged, Chris-ratified for S2962 arc-close as canon_v2 candidate. Question: should Tier-1 YAML routing-branch encoding be traffic-weighted? S2961's 4-of-5-zero-traffic branches is the sharpest example. Strengthened forward-carry from S2960.
- **Fold β — Domain-sensitivity predicate epistemic-labeling rescoping (canon-wide, all 7 slices)** — Rigby-flagged, forward-carry to S2962. Extension of S2960 Fold B. Question: rescope `no_fabricated_X` from blanket prohibition to "if X not sourced, label as hypothesis + request validation"? Combines with predicate count normalization discussion.
- **Fold ζ — Dedicated web_search fallback branch test** — Rigby-flagged, forward-carry to S2963. Requires deterministic harness/mocking; not YAML scope.
- **S2961 T2 zoom-out — Inline fold-disposition header pattern** — S2961 introduced `── Rigby T1 folds applied (S2961) ──` section not present in prior 6 slices. Rigby non-blockingly recommended S2962 arc-close normalization (either add across all 8 OR move dispositions to ratification envelope + keep YAML lean).
- **Ledger #16 miss investigation** — first miss in the arc's 7-slice streak (S2955-S2960 all re-hit). If S2962 close cascade re-hits, S2961 was anomalous; if it stays quiet, may be intermittent or root-cause-shifted. Not urgent.
- **Ledger #18 CLOSED as not-a-bug** — remove from Deferred Queue (was carried from S2959/S2960).

**Carry forward from S2960:**
- **Fold B — Domain-sensitivity predicate count normalization (canon-wide, all 7 slices)** — Rigby-flagged, forward-carry to S2962. Question: right count is 2-3 (Rigby's Tier-1-minimalism recommendation) or 5-7 (proportional to harm class per S2959 canon addition 9)? Legal 7, Content 5, Competitor 5, DevOps/Workflow/Research/SIA 2-3. Combines with S2961 Fold β above.
- **Fold D — Line-number anchoring brittleness (canon-wide, all 7 slices)** — Rigby-flagged, forward-carry to S2962. Question: replace exact line refs with function names + string literals as landmarks?
- **Fold E — `_CONTENT_TYPE_ALIASES` inside `execute()`** — record-only, no action. Code-quality observation.

**Carry forward from S2959:**
- **Fold 3 — Evidence-tier ladder mechanization (canon-wide, all 7 slices)** — Rigby-flagged, Chris-ratified for S2962 arc-close as canon_v2 candidate. Question: does S2963 validator implementation consume prose `derivation_spec` via text-parsing, or does canon need typed evidence-tier entries?

**Carry forward from S2958:**
- **WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR** (F1 from S2958 T2) — canonicalize legacy `_compile_final_result` at services/workflow_orchestration_agent.py:5341 and wrapper at agents/workflow_orchestration_agent.py:315 on ONE key. After fix, v1.1 revision of `evals/tier1/workflow_orchestration_agent.yaml` REMOVES the fallback mapping.
- **Fold A carry-forward (arc-substrate)** — Tier-1 must-have-tool_runs global rule vs orchestration agents.
- **Fold C next-slice-fold** — ambiguous_input vs bad_input remediation posture separation.

**Carry forward from S2957:**
- **Fold #1 (S2957 T2) — `health_status` dual-path enum add for advisory-vs-config-gen agents** — DevOpsAgent's advisory path currently collapses into `healthy`. Rigby suggests `healthy_no_tools_expected`. Track for `canon_version=2` arc-close at S2962.
- **Failure-mode lens documentation** — `devops_timeout_01` uses `SoftTimeLimitExceeded` (agent-side lens). Observable is external-cleanup-marked-failed (external lens). Both legitimate; document convention in S2963 validator design.

**Carry forward from S2956:**
- **Ledger #16 recipe drift (dual-route)** — recipe should document both routes: (a) direct Claude ORM (set diagnostic_* fields to None), (b) via Rigby PA (`deliverable_tool.clear_diagnostic` sticky-cleared sentinel). Update `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic.md`.
- **`orm_inspect_tool` distinct-count guardrail** — group-by on text fields rejected as "expensive/unbounded". Won't scale for agents with >200 30d executions.
- **Fold #5 (S2956 T2) — `health_status` derivation over-degrade for open-world agents** — UNKNOWN→degraded may over-penalize research/analysis agents. Track for `canon_version=2` at S2962.
- **Fold #6b (S2956 T2) — Tier-1 canon uniformity review** — comment-vs-usage mismatches across YAMLs.

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

## What's forbidden at S2961 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2961 new forbidden entries:** none.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2961 additions to the deferred queue:**
- Routing-branch encoding vs traffic reality — S2962 arc-close as canon_v2 candidate (2nd trigger).
- Epistemic-labeling predicate rescoping — S2962 arc-close (extension of S2960 Fold B).
- Web_search fallback dedicated test — S2963 harness scope.
- Inline fold-disposition header pattern — S2962 arc-close (normalize or lean).
- Ledger #16 Rigby-observability gap — Rigby's `deliverable_tool.create` reply does not surface `diagnostic_status='diagnostic'` when the flag fires, so operators believe "no re-hit" when a re-hit occurred. Distinct from the underlying create-bug; caught by `session_lifecycle close` twin-mirror gate. Prioritize S2956 forward-carry (dual-route recipe documentation) at S2962 arc-close.

**Carry forward from S2960:**
- Routing-branch encoding vs traffic reality (canon-wide) — S2962 arc-close (now with S2961 as 2nd trigger).
- Domain-sensitivity predicate count normalization (canon-wide) — S2962 arc-close.
- Line-number anchoring brittleness (canon-wide) — S2962 arc-close.

**Carry forward from S2959:**
- Evidence-tier ladder mechanization (canon-wide) — S2962 arc-close as canon_v2 candidate.
- ~~`orm_inspect_tool.count_by` group_by not propagating~~ — CLOSED as not-a-bug at S2961 T3.

**Carry forward from S2958:**
- WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR (can happen pre-S2963; unblocks v1.1 tightening).
- Fold A (arc-substrate tool_runs global rule) — S2962 arc-close discussion.

**Carry forward from S2957:**
- `health_status` dual-path enum add (canon_version=2 discussion at S2962).
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

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) + pre-A1 capability triage (S2952) + capability substrate (S2953 Drift Scanner) + Golden Evals arc-open + slice work (S2954-S2961) are adjacent-domain net-new engineering + arc substrate, not sweep work.

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

## For fuller context (S2846 → S2961)

See:
- **S2961 handoff (current):** `docs/handoffs/SESSION_2961_GOLDEN_EVALS_SLICE_7_COMPETITOR_YAML.md`
- **S2961 shipped code:** `evals/tier1/competitor_analysis_agent.yaml` (1232 lines, 13 prompts, seventh canon_version=1 reference)
- **S2960 handoff:** `docs/handoffs/SESSION_2960_GOLDEN_EVALS_SLICE_6_CONTENT_YAML.md`
- **S2960 shipped code:** `evals/tier1/content_writer_agent.yaml` (950 lines, 13 prompts, sixth canon_version=1 reference)
- **S2959 handoff:** `docs/handoffs/SESSION_2959_GOLDEN_EVALS_SLICE_5_LEGAL_YAML.md`
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
