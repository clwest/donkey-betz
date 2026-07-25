# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2962 CLOSED. Golden Evals **Tier-1 spec-authoring phase COMPLETE** (8/8 slices shipped): `evals/tier1/rigby_agent.yaml` (PR #3565, HEAD `6bf8d9a81`). 1,628 lines, 18 prompts, all 5 fault-injection categories (10 happy + 2 each of tool_timeout / data_unavailable / ambiguous_input / bad_input). **FIRST Tier-1 slice authored against a NON-AgentExecution row substrate** — proves canon_version=1 portability across TWO persistence substrates (AgentExecution × 7 prior slices + ChatConversation × this slice). Substrate: `core.ChatConversation` (4,486 all-time / 3,208 30d) filtered `source IN ('web', 'pa')` per Chris directive (buyer-facing Chris↔Rigby corpus 1,018 all-time / 508 30d — THICKEST-TRAFFIC AMONG BUYER-FACING SLICES, Claude-verified via direct ORM, Rigby-unverified per Fold P2). Source pointer: `core/services/unified_pa_entrypoint.py` (UnifiedPAEntrypoint service, NOT an AGENT_MAP class — PersonalAssistantAgent was removed April 2026). 10 happy_path VERBATIM REPLAYS from ChatConversation rows 1395/1534/1544/1545/1547/1589/2476/2478/4038/4042 span 8 intent categories (initiatives ×2 / knowledge_base / codebase / system_overview / workspace / system_health / verification / boardroom / recent_activity). ToolCallRecord as PRIMARY evidence-pointer source (per Rigby Q1 REVISE; metadata.tool_calls as convenience cache). 6 domain-sensitivity predicates (matches Content/Competitor 5 + `no_fabricated_conversation_history` substrate-specific to multi-turn PA behavior). 1 routing branch ("Rigby PA-turn dispatch"); intent as sampling dimension per Rigby Q2 AGREE Option B — 2nd consecutive slice avoiding routing-branch explosion. Chris D-verdict via TERMINAL 2026-07-25 — **6 consecutive terminal ratifications** S2957→S2962. Rigby SIGN T1 blocking FAIL (1 nonexistent selector caught + Fold U1 wording + R5 REVISE), T2 PASS with 4 fixes verified + BUNDLE arc-close recommendation. **S2963 first-action = Arc-close canon_v2 candidate review + validator implementation** (see 5 candidates below).

**Golden Evals Tier-1 arc — 8 canon_version=1 YAMLs SHIPPED (arc-close BUNDLED with S2962):**

| Slice | Session | Agent | Substrate | 30d | All-time | Domain predicates | Routing branches | HEAD |
|-------|---------|-------|-----------|-----|----------|-------------------|------------------|------|
| 1 | S2955 | SystemIntelligenceAgent | AgentExecution | 37 | 105 | 2-3 | 1 | d2acf9c92 |
| 2 | S2956 | ResearchAgent | AgentExecution | 37 | 90 | 2-3 | 1 | c8815cd38 |
| 3 | S2957 | DevOpsAgent | AgentExecution | 13 | 40+ | 2-3 | 2 (dual-path) | 98ba0e06b |
| 4 | S2958 | WorkflowOrchestrationAgent | AgentExecution | 9 | 30+ | 2-3 | 2 (programmatic) | e2b7e92c2 |
| 5 | S2959 | LegalDocDrafterAgent | AgentExecution | 5 | 10+ | 7 | 2 (routing) | 8fa60421f |
| 6 | S2960 | ContentWriterAgent | AgentExecution | 7 | 23 | 5 | 5 (routing) | 10b6b3ab1 |
| 7 | S2961 | CompetitorAnalysisAgent | AgentExecution | 2 | 11 | 5 | 5 (routing) | 75f8da29a |
| 8 | S2962 | **Rigby (UnifiedPAEntrypoint)** | **ChatConversation** | **508** | **1,018** | **6** | **1** | **6bf8d9a81** |

**Arc-precedent substrate frozen at canon_version=1** (unchanged from S2955; substrate PROVEN PORTABLE across TWO persistence substrates via S2962):
1. `schema_version: 1` + `canon_version: 1` at file top.
2. `canonical_field_mapping` block declaring `mapping_source: native|derived` per canon field with named derivation rules — S2963 validators MUST consult, never invent mappings.
3. `fault_injection` uses effect-based contract (`component` + `fault.{type, params}`) with `python.{...}` as backend-adapter appendix. Prefer service-level selectors (`core.agents.*` / `core.services.*`) over library-internal Python paths per S2957 fold.
4. `one_of` acceptance-criteria capped at ≤2 branches with mandatory `why` string per branch.
5. **NEW (S2962 canon extension)**: canon substrate is PORTABLE across persistence substrates — S2963 validators MUST consume canonical_field_mapping abstractedly (not assume AgentExecution row shape). Two shipped substrates: AgentExecution rows (7 slices) + ChatConversation rows (1 slice). Additional substrates may be added at future slices.

**S2958 additions to canon (informative, non-breaking):**
6. **Per-execution-shape evidence-tier requirements** — for agents where different execution shapes produce different evidence sets, `canonical_field_mapping.evidence_pointers` MAY carve per-shape rules.
7. **INTEGRATION EVIDENCE tier distinction** — out-of-band DB row inspection is NOT in Tier-1 validator scope; belongs to a separate integration/side-effect verification suite. Tier-1 validators are pure on the returned artifact + join-substrate (ToolCallRecord, etc).
8. **TRANSITIONAL marking pattern** — when a YAML documents a fold requiring code follow-up, use "TRANSITIONAL — code-fix PR expected" phrasing with v1.1 removal clause.
9. **Timeout-string brittleness avoidance** — assert stable discriminator fields + broad substring patterns, not exact wording.

**S2959 additions to canon (informative, non-breaking):**
10. **Domain-sensitivity acceptance predicates** — for agents whose failure surface carries elevated buyer-facing cost, encode domain-specific predicates alongside `no_unsupported_claims`. Counts observed: Legal 7 / Content 5 / Competitor 5 / Rigby 6 / DevOps/Workflow/Research/SIA 2-3.
11. **Routing-branch framing (not "new shape")** — variant execution paths are routing branches inside the same agent contract, NOT new shapes. Same success + evidence + hallucination invariants apply across branches.
12. **Coverage-limits actionable conclusion** — the coverage-caveat pile should resolve to ONE actionable conclusion line per slice.

**S2962 additions to canon (informative, non-breaking — apply where relevant to S2963 validators):**
13. **Substrate portability**: canonical_field_mapping abstracts over persistence substrate. Two shipped: AgentExecution + ChatConversation. Validators consume via mapping declaration, not row-shape assumption. See Fold U2 forward-carry.
14. **Source-stratification as canon dimension**: multi-source substrates (e.g., ChatConversation with claude-code / web / pa / etc) MUST filter to buyer-facing surface for Tier-1 slices. Same user_id ≠ same eval class. See Fold S1.
15. **Receipt-contamination filter for AgentExecution queries**: any future "real usage" query on AgentExecution MUST exclude synthetic `deliverable_factory.synthesized_pa_receipt` rows via `parent_object_type != 'deliverable_factory' OR input_data.source != 'deliverable_factory.synthesized_pa_receipt'`. See Fold P1.

Reference implementations (in order of canon fidelity):
- `evals/tier1/system_intelligence_agent.yaml` — canon_version=1 original (463 lines, autonomous single-prompt shape, closed-world, AgentExecution substrate).
- `evals/tier1/research_agent.yaml` — human-diverse open-world (523 lines, 26-prompt, LLM synthesis).
- `evals/tier1/devops_agent.yaml` — dual-path advisory-vs-config-gen (612 lines, thin-traffic honesty pattern + service-level selector fold).
- `evals/tier1/workflow_orchestration_agent.yaml` — no-LLM-tool-calls programmatic-dispatch (801 lines, per-workflow-shape evidence cascade + transitional-fold pattern).
- `evals/tier1/legal_doc_drafter_agent.yaml` — 10-tool GPT-selection + routing-branch shape (794 lines, domain-sensitivity predicates + coverage-limits actionable conclusion).
- `evals/tier1/content_writer_agent.yaml` — 5-routing-branch single-LLM-call `tools=[]` (950 lines, proportional domain-sensitivity predicates + representative-not-verbatim failure-replay pattern).
- `evals/tier1/competitor_analysis_agent.yaml` — 5-routing-branch multi-tool GPT-dispatch (1232 lines, THINNEST-TRAFFIC honesty pattern + verbatim-single-real-prompt anchor + boundary-condition evidence-gate disclaimer).
- `evals/tier1/rigby_agent.yaml` — **NEW eighth reference / FIRST NON-AgentExecution substrate** (1,628 lines, ChatConversation-row substrate with source filter, 6 predicates including substrate-specific `no_fabricated_conversation_history`, verbatim-replays across 8 intents, two-phase ChatConversation lifecycle documented).

**Refreshed 2026-07-25 (S2962 close).** Gap-map headline unchanged: `100 validated_full / 2 untested` — the 2 are `agent_capability_drift_tool` (S2953-shipped) + `agent_job_status` (S2952-shipped), both untested-by-design at ship time. This session shipped a spec file only, no PA tool changes.

**PRs shipped this session (S2962):**
- u-d-b PR **#3565** — S2962 Golden Evals Tier-1 slice 8: Rigby YAML (1 file, +1628/-0, spec-only, FINAL Tier-1 slice).
- u-d-b PR **#TBD** — S2962 close cascade (handoff + this 00-START refresh + wrapper pin bump).

**Twin mirrors shipped this session (S2962 slice):**
- S2962 slice 8 content mirror: `3975ba21-dfb6-42c1-ad54-f060a8aaa330` (Donkey Betz workspace, `initiative_phase_doc`, `category='governance'`, **Ledger #16 RE-HIT 15th cumulative** — Rigby cleared PROACTIVELY this session, no post-hoc `session_lifecycle close` catch required; improvement over S2961 first-miss).
- S2962 slice 8 ratification envelope: `944503e2-fcf8-4d35-906f-db38d8c37ab0` (Donkey Betz workspace, `ratification_record`, `category='governance'`, diagnostic clean on create).

Full S2955-S2961 mirror IDs preserved in prior handoffs.

**Files shipped this session (S2962 slice):**
- **NEW** `evals/tier1/rigby_agent.yaml` — eighth Tier-1 canonical prompt suite (1,628 lines, 18 prompts, FIRST non-AgentExecution substrate).

**Post-merge:** PR #3565 was spec-only (YAML config, no code), no worker impact → no `make celery-recycle` required (PLAYBOOK-7.4.4 applies to code-shipping PRs).

**Governance:** Rigby SIGN cycle held tool-grounded discipline throughout — 3 substantive turns (co-scoping + T1 blocking FAIL + T2 PASS). T1 caught 1 blocking selector error (`_handle_workspace_lookup` nonexistent). T2 verified all 4 fixes + surfaced 6 new zoom-out folds (P1/P2/S1/U1/U2/V1) — all forward-carried to arc-close for S2963 canon_v2 candidate ratification. Chris D-verdict via terminal: `yes` (both authoring + arc-close bundle).

**Rigby Tool Gap Ledger:**
- **Ledger #16 RE-HIT — 15th cumulative** — Rigby CLEARED PROACTIVELY this session (improvement over S2961 first-miss). Ledger candidate for arc-close: is the pattern normalizing (Rigby learning to auto-clear) or is the underlying create-bug still needing a substrate fix?
- **NO CHANGE — Ledger #17 count remains 4** — Chris used terminal ratification path directly (`yes` typed in terminal). Consistent with S2957-S2961 pattern (**6 consecutive terminal ratifications S2957→S2962**). Design task `f3f140f9-87bf-488b-8757-eab5d8058f45` remains valid for the Chat-UI-only path.
- **Ledger #19 CANDIDATE (proposed at S2962 arc-close) — ChatConversation/ToolCallRecord/LLMCallLog allowlist gap** (Fold P2): Rigby's `orm_inspect_tool` allowlist blocks all three tables needed for the ChatConversation-substrate slice. She could not tool-verify her own eval substrate. S2963 harness dogfooding requires this fix. Additive, non-breaking (14 → 17 models). Chris to ratify inclusion at S2963 arc-close review.
- **Rigby T1/T2 discipline HELD** — 6 substantive folds surfaced, 4 in-PR fixes accepted, 1 module-path error caught by Grep (not Rigby's tool_runs — noted for arc-close discussion), tool_runs verbose on every SIGN turn.

Full session context: `docs/handoffs/SESSION_2962_GOLDEN_EVALS_SLICE_8_RIGBY_YAML.md`.

---

## S2963 open sequence

**S2963 first-action = Arc-close canon_v2 candidate review + validator implementation kickoff.** Tier-1 spec-authoring phase COMPLETE at S2962; S2963 opens the validator implementation phase.

**Two-component S2963 work:**

**(A) Arc-close canon_v2 candidate review** (should happen FIRST, before validator code) — Chris ratifies which of 5 candidates become canon_v2 refinements vs remain forward-carry:

1. **CANDIDATE 1 (Fold P2 fix)**: Add ChatConversation + ToolCallRecord + LLMCallLog to `orm_inspect_tool` allowlist. UNBLOCKS S2963 dogfooding. Additive, non-breaking. Likely ratify.
2. **CANDIDATE 2 (Fold S1 codification)**: Codify source-stratification as canon dimension for multi-source substrates. Documentation-only + validator design implication. Likely ratify.
3. **CANDIDATE 3 (Fold U1 elevation)**: Elevate `response_time_ms` to first-class evidence field for latency-sensitive validators (currently diagnostic-only). Requires per-slice update. Chris judgment call.
4. **CANDIDATE 4 (Fold P1 canonicalization)**: Adopt "receipt-contamination filter" as canon-wide predicate for any AgentExecution-based query. Documentation-only + validator implementation note. Likely ratify.
5. **CANDIDATE 5 (Fold V1 resolution)**: Resolve fault-injection selector naming convention (module.function vs module.Class.method vs handler-registry key). Required for S2963 harness. Must ratify before harness code.

Also arc-close DISCUSSION queue (carried from prior slices, may resolve at S2963 arc-close):
- **Fold α**: routing-branch encoding vs traffic reality (S2962 was 2nd consecutive slice avoiding branch explosion — pattern converging)
- **Fold β**: domain-sensitivity predicate epistemic-labeling rescope (carried S2960/S2961)
- **Fold D**: line-number anchoring brittleness (carried S2960)
- **Fold 3**: evidence-tier ladder mechanization (carried S2959)
- **Inline fold-disposition header pattern** (S2961 innovation) — S2962 chose NOT to use; canon-uniformity question
- **Content-append-vs-final content discrepancy** (S2962 T2 twin-mirror ledger candidate) — Rigby's deliverable_tool.append reported 16,639 chars but final state was 642 bytes; possible silent overwrite

**(B) Validator implementation kickoff** (after arc-close canon_v2 ratification) — build S2963 core:

1. `run_golden_evals` mgmt cmd that discovers `evals/tier1/*.yaml`, iterates prompts, dispatches via the appropriate substrate-specific adapter (AgentExecution write path OR ChatConversation write path)
2. JSON Schema executors for `expected_output_shape` validation
3. Pydantic model runners for `acceptance_criteria` predicate evaluation
4. `GoldenEvalRun` table for per-run tracking (per-prompt pass/fail + evidence-pointer join results)
5. Two-substrate adapter abstraction (Fold U2 concrete implementation)
6. Recommend: **dogfood against slice 8 (Rigby, ChatConversation substrate) FIRST** — forces the Fold P2 allowlist fix immediately + validates the two-substrate adapter cleanly before the 7 AgentExecution slices tighten the loop

### Universal open sequence (unchanged from prior sessions)

1. **Live-verify S2953 drift scanner still healthy:**
   - `bash tools/pa_local.sh "run agent_capability_drift_tool action=summary"` — expect shape (83/92/59/1 → 77+2 or drifted numbers with same shape).
   - `python manage.py scan_agent_capability_drift --json | jq .totals` — same from CLI.
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline `100 validated_full / 2 untested`.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2963 pin (retired at S2962 close cascade).
4. **Read the 8 arc-precedent substrate references BEFORE writing validator code** — any is sufficient for canon substrate understanding; slice 8 (Rigby) is essential reading because it's the only non-AgentExecution substrate.
5. **Open S2963 canon_v2 review + validator work** — see scope (A) and (B) above.

### S2963 scope note: arc-close review vs validator code

Arc-close canon_v2 review is DOCUMENTATION-HEAVY (candidate evaluation + rationale + Chris ratification). Validator implementation is CODE-HEAVY. Recommend SPLIT: arc-close review as S2963 focus (1-2 turns), validator code opens at S2964. This avoids scope creep on session count and keeps ratification cleanly separable from implementation.

Alternative: BUNDLE if canon_v2 review resolves cleanly in early turns AND Chris green-lights parallel validator work.

**Out of scope for S2963:** the harness (`run_golden_evals` mgmt cmd + `GoldenEvalRun` table + nightly beat task) — that's S2964. Validator core code (JSON Schema executors + Pydantic model runners) IS S2963 scope.

**Also out of scope for S2963:** the WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR (F1 from S2958). That's a separate follow-up that can happen any time.

**Estimated 1-3 sessions** for S2963 arc-close review + validator core.

### Golden Evals arc structure (updated at S2962 close)

**Tier-1 YAMLs — 8 of 8 shipped (FINAL):**
- ✅ **S2955 slice 1 — SystemIntelligenceAgent** (PR #3551, HEAD `d2acf9c92`) — SHIPPED.
- ✅ **S2956 slice 2 — ResearchAgent** (PR #3553, HEAD `c8815cd38`) — SHIPPED.
- ✅ **S2957 slice 3 — DevOpsAgent** (PR #3555, HEAD `98ba0e06b`) — SHIPPED.
- ✅ **S2958 slice 4 — WorkflowOrchestrationAgent** (PR #3557, HEAD `e2b7e92c2`) — SHIPPED.
- ✅ **S2959 slice 5 — LegalDocDrafterAgent** (PR #3559, HEAD `8fa60421f`) — SHIPPED.
- ✅ **S2960 slice 6 — ContentWriterAgent** (PR #3561, HEAD `10b6b3ab1`) — SHIPPED.
- ✅ **S2961 slice 7 — CompetitorAnalysisAgent** (PR #3563, HEAD `75f8da29a`) — SHIPPED.
- ✅ **S2962 slice 8 — Rigby (UnifiedPAEntrypoint)** (PR #3565, HEAD `6bf8d9a81`) — SHIPPED. **FIRST non-AgentExecution substrate. Tier-1 spec-authoring phase COMPLETE.**
- ⏭ **S2963 — Arc-close canon_v2 review + validator implementation** — NEXT.

**After S2963 validators:**
- **S2964** — Harness (`run_golden_evals` mgmt cmd + `GoldenEvalRun` table + nightly beat task).
- **Follow-up code-fix PR** for the S2958 WorkflowOrchestrationAgent wrapper key-name mismatch — canonicalize legacy `_compile_final_result` and wrapper on one key; then v1.1 revision of `workflow_orchestration_agent.yaml` to tighten assertions.
- **Rigby-as-Claude-Code eval track** — separate eval slice for the 3,453 source='claude-code' rows (per S1 canon: same user_id ≠ same eval class). Different trust surface, different predicates.
- **PA-turn AgentExecution eval track** — flip `PA_AGENT_EXECUTION_WRITE_ENABLED` + accumulate real PA-turn AgentExecution rows for 2-4 weeks, then author dedicated slice against that substrate (complement to ChatConversation-based slice 8).
- **After arc close** — A1 Phase 1 first-slice opens (Chris's 4 gating questions still block; see below).

### Capability Manifest — build spec (parallel-track from A1 Phase 1 start)

_(unchanged — see prior S2953 close snapshots; not part of Golden Evals arc)_

### A1 Phase 1 still ahead (after Golden Evals arc closes)

Chris's 4 open questions from scoping deliverable `7870eca9` still gate Phase 1 code:

1. **Minimum evidence standard** we promise? (run IDs + failure signature samples vs metrics only)
2. **Default turnaround SLA** we can consistently hit without heroics?
3. Sell as **agent-system audit** (end-to-end) or **toolchain reliability audit** (tools/contracts) first?
4. **Legal posture** for handling customer logs (retention window, deletion guarantee, allowed data types)?

### Deferred queue (updated at S2962 close)

**S2962 additions (arc-close canon_v2 candidates + fold forward-carries):**
- **Fold P1 — AgentExecution receipt-contamination filter** — canon_v2 candidate #4. Applies canon-wide to any "real usage" query on AgentExecution.
- **Fold P2 — ChatConversation/ToolCallRecord/LLMCallLog allowlist gap** — canon_v2 candidate #1. Blocks S2963 harness dogfooding. Additive, non-breaking (14 → 17 models). Likely ratify at S2963 arc-close.
- **Fold S1 — Source-stratification canon dimension** — canon_v2 candidate #2. Applies canon-wide to multi-source substrates.
- **Fold U1 — assistant_response update-site precise location TBD** — carried to canon_v2 refinement. Also candidate for `response_time_ms` elevation to first-class evidence (canon_v2 candidate #3).
- **Fold U2 — Dual-substrate validator abstraction** — must be resolved in S2963 validator code (concrete implementation).
- **Fold V1 — Fault-injection selector naming convention** — canon_v2 candidate #5. Required BEFORE S2963 harness code.
- **Content-append-vs-final content discrepancy** — Rigby's deliverable_tool.append reported 16,639 chars but final was 642 bytes. Potential silent overwrite. Investigate at S2963.

**Carry forward from S2961:**
- **Fold α — Routing-branch encoding vs traffic reality (canon-wide, all 7 slices + S2962)** — S2962 was 2nd consecutive slice avoiding branch explosion. Pattern converging on "routing branches only when execution shape actually forks in code, not when input taxonomy is diverse." Strengthens canon_v2 candidate.
- **Fold β — Domain-sensitivity predicate epistemic-labeling rescoping (canon-wide)** — extension of S2960 Fold B. S2963 arc-close discussion.
- **Fold ζ — Dedicated web_search fallback branch test** — S2963 harness scope (requires deterministic mocking).
- **S2961 T2 zoom-out — Inline fold-disposition header pattern** — S2961 introduced this style; S2962 chose NOT to. Canon-uniformity question for S2963 arc-close.
- **Ledger #16 miss investigation** — S2961 first miss + S2962 proactive clear = pattern may be normalizing. Track at S2963.

**Carry forward from S2960:**
- **Fold B — Domain-sensitivity predicate count normalization (canon-wide)** — Legal 7 / Content 5 / Competitor 5 / Rigby 6 / others 2-3. S2963 arc-close discussion.
- **Fold D — Line-number anchoring brittleness (canon-wide)** — S2963 arc-close discussion.
- **Fold E — `_CONTENT_TYPE_ALIASES` inside `execute()`** — record-only, no action.

**Carry forward from S2959:**
- **Fold 3 — Evidence-tier ladder mechanization (canon-wide)** — canon_v2 candidate. S2963 arc-close ratification.

**Carry forward from S2958:**
- **WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR** (F1 from S2958 T2) — can happen pre-S2963 as unblocker for v1.1 tightening.
- **Fold A carry-forward (arc-substrate)** — Tier-1 must-have-tool_runs global rule vs orchestration agents.
- **Fold C next-slice-fold** — ambiguous_input vs bad_input remediation posture separation.

**Carry forward from S2957:**
- **Fold #1 (S2957 T2) — `health_status` dual-path enum add for advisory-vs-config-gen agents** — Track for `canon_version=2` arc-close review at S2963.
- **Failure-mode lens documentation** — document convention in S2963 validator design.

**Carry forward from S2956:**
- **Ledger #16 recipe drift (dual-route)** — S2962 improvement (proactive clear) suggests recipe may be normalizing. Update at S2963 based on which pattern persists.
- **`orm_inspect_tool` distinct-count guardrail** — group-by on text fields rejected as "expensive/unbounded".
- **Fold #5 (S2956 T2) — `health_status` derivation over-degrade for open-world agents** — canon_v2 candidate for S2963.
- **Fold #6b (S2956 T2) — Tier-1 canon uniformity review** — happens at S2963 arc-close.

**S2955 additions (carry forward):**
- **Bound-annotation discipline for volume claims in YAML headers** — canon_v2 candidate for CI check.

**S2954 additions (carry forward):**
- **00-START validated-full gap-map lint sync** — canon_v2 candidate for CI check.

**S2953 additions (carry forward):**
- Drift scanner invariant 4 (rerouted-must-be-labeled) — requires `AgentRerouteEntry`-style queryable model.
- Curate `capabilities_exceptions.yaml` — 77 active findings at HEAD.
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

## What's forbidden at S2962 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2962 new forbidden entries:** none.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2962 additions to the deferred queue:**
- 5 canon_v2 candidates (P2 allowlist / S1 source-stratification / U1 response_time_ms elevation / P1 receipt filter / V1 selector convention) — S2963 arc-close review scope.
- Rigby-as-Claude-Code eval track (post-S2964, per S1 canon).
- PA-turn AgentExecution eval track (post-S2964, requires `PA_AGENT_EXECUTION_WRITE_ENABLED` flip + 2-4 week traffic accumulation).
- assistant_response update-site precise location investigation (Fold U1 canon_v2 refinement).
- Content-append-vs-final content discrepancy investigation (Ledger candidate).

**Carry forward from S2961:**
- Routing-branch encoding vs traffic reality — S2963 arc-close (now 2 consecutive avoidance triggers).
- Domain-sensitivity predicate count normalization + epistemic labeling rescope — S2963 arc-close.
- Line-number anchoring brittleness — S2963 arc-close.
- Web_search fallback dedicated test — S2963 harness scope.
- Inline fold-disposition header pattern — S2963 arc-close.

**Carry forward from S2959/S2960/S2958/S2957/S2956/S2955/S2954/S2953/S2952/S2951:**
_(unchanged — see S2961 close snapshot)_

**Long-standing:**
- Docs restructuring arc (Chris-ratified S2800).
- Slice 5-hardening executable invariants.
- Tier 2 lint promotion.
- Advanced paste-UUID fallback for cluster picker.
- Server-side search + pagination on `/eligible/`.
- Z1/Z2/Z4 signal-dispatch UI polish.
- Rank + cap + paginate follow-ups.
- Per-pattern-type diversity floors.
- Ledger candidates backlog.
- W2 #1 / #2b / #2c pending Chris re-slate.
- LLMCallLog field splits.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) + pre-A1 capability triage (S2952) + capability substrate (S2953 Drift Scanner) + Golden Evals arc-open + slice work (S2954-S2962) are adjacent-domain net-new engineering + arc substrate, not sweep work.

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

## For fuller context (S2846 → S2962)

See:
- **S2962 handoff (current):** `docs/handoffs/SESSION_2962_GOLDEN_EVALS_SLICE_8_RIGBY_YAML.md`
- **S2962 shipped code:** `evals/tier1/rigby_agent.yaml` (1,628 lines, 18 prompts, eighth canon_version=1 reference / FIRST non-AgentExecution substrate)
- **S2961 handoff:** `docs/handoffs/SESSION_2961_GOLDEN_EVALS_SLICE_7_COMPETITOR_YAML.md`
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
- **S2952 handoff:** `docs/handoffs/SESSION_2952_PRE_A1_CAPABILITY_FIXES.md`
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope (unchanged, S2951):** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
- **Ledger #17 (S2957):** `db316865-d08c-4cc1-9d8e-cfac249e8c89` — Chat UI response-relay gap (unchanged this session)
- **Chat UI relay design task (S2957):** `f3f140f9-87bf-488b-8757-eab5d8058f45`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
