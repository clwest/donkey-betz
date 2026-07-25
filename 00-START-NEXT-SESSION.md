# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2963 CLOSED. Golden Evals **arc CLOSED** with canon_v2 ratification: 5 fold candidates + 1 EvalRunContext guardrail. Shipped `docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md` (PR #3567, HEAD `54bf92c27`, 190 lines, spec-only). 6 canon_v2 items bind the S2964 validator harness shape BEFORE harness code lands: (1) `orm_inspect_tool._MODEL_POLICIES` allowlist +ChatConversation +ToolCallRecord (14→16; LLMCallLog already present at `td_handlers_agents.py:749-752`) — code at S2964 first commit; (2) source-stratification as canon dimension (same `user_id` ≠ same eval class); (3) opt-in `latency_ms` evidence class (not universal `response_time_ms` promotion); (4) receipt-contamination filter as canon-wide predicate `NOT (parent_object_type='deliverable_factory' AND input_data.source='deliverable_factory.synthesized_pa_receipt')`; (5) fault-injection selector convention `module.Class.method` + `module.function`, handler-registry keys FORBIDDEN without adapter layer; (6) `EvalRunContext { substrate_type, primary_row_id, evidence_ledger_refs[], finalized_at, latency_ms? }` shape as canonical evidence abstraction. Rigby SIGN: T1 tool-grounded (10 tool_runs, 2 AGREE + 3 REVISE all folded), T2 5 PASS + 1 FAIL on Item 4 predicate, T2b PASS after De Morgan slip verified + doc rewritten to lead with `NOT (A AND B)` intent form. Chris D-verdict via TERMINAL 2026-07-25 — **7 consecutive terminal ratifications** S2957→S2963. **S2964 first-action = validator harness core (`run_golden_evals` mgmt cmd + `GoldenEvalRun` table + per-substrate adapter + JSON Schema executors + Pydantic acceptance-criteria runners); dogfood against slice 8 FIRST to force Item 1 allowlist code + validate two-substrate adapter cleanly.**

**Golden Evals Tier-1 arc — 8 canon_version=1 YAMLs shipped + canon_v2 ratified at S2963 arc-close (ARC CLOSED):**

| Slice | Session | Agent | Substrate | 30d | All-time | Domain predicates | Routing branches | HEAD |
|-------|---------|-------|-----------|-----|----------|-------------------|------------------|------|
| 1 | S2955 | SystemIntelligenceAgent | AgentExecution | 37 | 105 | 2-3 | 1 | d2acf9c92 |
| 2 | S2956 | ResearchAgent | AgentExecution | 37 | 90 | 2-3 | 1 | c8815cd38 |
| 3 | S2957 | DevOpsAgent | AgentExecution | 13 | 40+ | 2-3 | 2 (dual-path) | 98ba0e06b |
| 4 | S2958 | WorkflowOrchestrationAgent | AgentExecution | 9 | 30+ | 2-3 | 2 (programmatic) | e2b7e92c2 |
| 5 | S2959 | LegalDocDrafterAgent | AgentExecution | 5 | 10+ | 7 | 2 (routing) | 8fa60421f |
| 6 | S2960 | ContentWriterAgent | AgentExecution | 7 | 23 | 5 | 5 (routing) | 10b6b3ab1 |
| 7 | S2961 | CompetitorAnalysisAgent | AgentExecution | 2 | 11 | 5 | 5 (routing) | 75f8da29a |
| 8 | S2962 | Rigby (UnifiedPAEntrypoint) | ChatConversation | 508 | 1,018 | 6 | 1 | 6bf8d9a81 |
| ARC-CLOSE | S2963 | canon_v2 ratification (5 folds + EvalRunContext) | — | — | — | — | — | **54bf92c27** |

**Canon_v1 substrate (unchanged; still in force at canon_v2):**
1. `schema_version: 1` + `canon_version` at file top.
2. `canonical_field_mapping` block declaring `mapping_source: native|derived` per canon field with named derivation rules.
3. `fault_injection` uses effect-based contract (`component` + `fault.{type, params}`) with `python.{...}` as backend-adapter appendix. Service-level selectors (`core.agents.*` / `core.services.*`) preferred.
4. `one_of` acceptance-criteria capped at ≤2 branches with mandatory `why` string per branch.
5. Canon substrate is PORTABLE across persistence substrates. Two shipped substrates: AgentExecution (7 slices) + ChatConversation (1 slice).

**S2958 canon_v1 informative additions:**
6. Per-execution-shape evidence-tier requirements.
7. INTEGRATION EVIDENCE tier distinction — out-of-band DB inspection not in Tier-1 validator scope.
8. TRANSITIONAL marking pattern for fold-requires-code-follow-up slices.
9. Timeout-string brittleness avoidance — assert stable discriminator fields + broad substring patterns.

**S2959 canon_v1 informative additions:**
10. Domain-sensitivity acceptance predicates. Counts observed: Legal 7 / Content 5 / Competitor 5 / Rigby 6 / DevOps/Workflow/Research/SIA 2-3.
11. Routing-branch framing (not "new shape") — variant execution paths are routing branches inside the same agent contract.
12. Coverage-limits actionable conclusion — resolve caveat pile to one actionable line per slice.

**S2962 canon_v1 informative additions (superseded/formalized at S2963 canon_v2 where noted):**
13. Substrate portability: canonical_field_mapping abstracts over persistence substrate. (Formalized as canon_v2 Item 6 EvalRunContext.)
14. Source-stratification for multi-source substrates. (Formalized as canon_v2 Item 2.)
15. Receipt-contamination filter for AgentExecution queries. (Formalized as canon_v2 Item 4 with `NOT (A AND B)` intent form.)

**S2963 canon_v2 ratifications (governance-binding for S2964+):**
16. **Item 1 — `orm_inspect_tool._MODEL_POLICIES` extension**: add `ChatConversation` + `ToolCallRecord` (14→16 models; `LLMCallLog` already present at `td_handlers_agents.py:749-752`). Ships as code at S2964 harness first commit.
17. **Item 2 — Source-stratification as canon dimension**: multi-source substrates (any substrate with a `source` discriminator like `ChatConversation.source IN ('web', 'pa', 'claude-code', …)`) MUST filter to buyer-facing surface. **Same user_id ≠ same eval class.** Doc-only.
18. **Item 3 — Opt-in `latency_ms` evidence class**: do NOT universally promote `response_time_ms` to first-class evidence. Opt-in `latency_ms` class with "may be present" semantics for validators that are latency-sensitive. Doc-only; no retroactive slice updates.
19. **Item 4 — Receipt-contamination filter as canon-wide predicate**: Any Tier-1 query on `AgentExecution` MUST exclude synthetic deliverable-factory receipts via `NOT (parent_object_type='deliverable_factory' AND input_data.source='deliverable_factory.synthesized_pa_receipt')`. OR form + Django `.exclude(**kwargs)` form are logically identical alternatives. Doc-only; harness utility at S2964.
20. **Item 5 — Fault-injection selector convention**: canonical `fault_injection.selector` values MUST be `module.Class.method` (service methods, precedent `system_intelligence_agent.yaml:211`) or `module.function` (module-level). Handler-registry keys FORBIDDEN without an adapter layer. Doc-only; harness parser at S2964.
21. **Item 6 — `EvalRunContext` shape**: canonical evidence abstraction `{ substrate_type: str, primary_row_id: str, evidence_ledger_refs: list, finalized_at: datetime|None, latency_ms: int|None }`. Validators consume `EvalRunContext`, not raw substrate rows; per-substrate adapters normalize. Doc-only shape ratification; concrete Python API at S2964.

Reference implementations (8 Tier-1 YAMLs; all canon_version=1; canon_v2 items above apply to S2964 harness code + future slice authoring):
- `evals/tier1/system_intelligence_agent.yaml` — canon_version=1 original (463 lines, autonomous single-prompt, AgentExecution).
- `evals/tier1/research_agent.yaml` — human-diverse open-world (523 lines, 26-prompt, LLM synthesis).
- `evals/tier1/devops_agent.yaml` — dual-path advisory-vs-config-gen (612 lines, thin-traffic honesty pattern + service-level selector fold).
- `evals/tier1/workflow_orchestration_agent.yaml` — no-LLM-tool-calls programmatic-dispatch (801 lines, per-workflow-shape evidence cascade + transitional-fold pattern).
- `evals/tier1/legal_doc_drafter_agent.yaml` — 10-tool GPT-selection + routing-branch (794 lines, domain-sensitivity predicates + coverage-limits actionable conclusion).
- `evals/tier1/content_writer_agent.yaml` — 5-routing-branch single-LLM-call `tools=[]` (950 lines, proportional domain-sensitivity predicates).
- `evals/tier1/competitor_analysis_agent.yaml` — 5-routing-branch multi-tool GPT-dispatch (1232 lines, thinnest-traffic honesty pattern + verbatim-single-real-prompt anchor).
- `evals/tier1/rigby_agent.yaml` — eighth Tier-1 / FIRST non-AgentExecution substrate (1,628 lines, ChatConversation-row substrate with source filter, 6 predicates including `no_fabricated_conversation_history`).

**Refreshed 2026-07-25 (S2963 close).** Gap-map headline unchanged: `100 validated_full / 2 untested` — untested-by-design (`agent_capability_drift_tool` + `agent_job_status`). This session shipped a spec doc only, no PA tool / code changes.

**PRs shipped this session (S2963):**
- u-d-b PR **#3567** — S2963 Golden Evals arc-close canon_v2 ratification doc (+190 lines, spec-only, arc closed).
- u-d-b PR **#TBD** — S2963 close cascade (handoff + this 00-START refresh + wrapper pin bump).

**Twin mirrors shipped this session (S2963):**
- S2963 arc-close content mirror: `e333f8f8-26fc-4d46-a6f0-4aa8c1516fb5` (Donkey Betz workspace, `initiative_phase_doc`, `category='governance'`, **Ledger #16 RE-HIT 16th cumulative** — Rigby cleared proactively via `deliverable_tool.clear_diagnostic` in same tool cycle).
- S2963 arc-close ratification envelope: `fc46527e-7ea3-4069-afea-33f273694cc6` (Donkey Betz workspace, `ratification_record`, `category='governance'`, diagnostic-clean on create).

Full S2955-S2962 mirror IDs preserved in prior handoffs.

**Files shipped this session (S2963):**
- **NEW** `docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md` — canon_v2 ratification (190 lines).

**Post-merge:** PR #3567 was doc-only (no code, no worker impact) → no `make celery-recycle` required (PLAYBOOK-7.4.4).

**Governance:** Rigby SIGN discipline held throughout — 3 substantive turns (T1 per-candidate + T2 doc-verify + T2b reconciliation). T1: 10 tool_runs, 2 AGREE + 3 REVISE (all revisions folded). T2: 5 PASS + 1 FAIL on Item 4. T2b PASS after Claude verified FAIL was a De Morgan slip + rewrote Item 4 to lead with `NOT (A AND B)` for readability. Chris D-verdict via terminal after joint agreement: `yes` bundle (all 6 items).

**Rigby Tool Gap Ledger:**
- **Ledger #16 RE-HIT — 16th cumulative** — content mirror still fires `missing_initiative_id` on create (governance-scoped, no initiative_id by design); Rigby auto-cleared via `deliverable_tool.clear_diagnostic` in same tool cycle. Ratification envelope diagnostic-clean on create. Proactive-clear pattern held for 2nd consecutive session (S2962 was first). Underlying substrate bug still unfixed; Rigby's auto-clear compensates.
- **NO CHANGE — Ledger #17 count remains 4** — Chris used terminal ratification path directly. Consistent with S2957-S2962 pattern (**7 consecutive terminal ratifications S2957→S2963**). Design task `f3f140f9-87bf-488b-8757-eab5d8058f45` remains valid for the Chat-UI-only path.
- **Ledger #19 RATIFIED (as canon_v2 Item 1)** — flip **CANDIDATE → RATIFIED** at S2963 arc-close. Code fix opens with S2964 harness first commit: add `ChatConversation` + `ToolCallRecord` to `_MODEL_POLICIES` in `core/services/td_handlers_agents.py:733-831` (~30 lines).
- **Rigby T1/T2/T2b discipline HELD** — 10+5+1 tool_runs, zero rubber-stamp. T2 De Morgan slip caught by Claude verification; reconciliation smooth.

Full session context: `docs/handoffs/SESSION_2963_GOLDEN_EVALS_ARC_CLOSE_CANON_V2.md`.

---

## S2964 open sequence

**S2964 first-action = validator harness core.** Arc-close canon_v2 ratified S2963; harness code opens now. All 6 canon_v2 items are in force from harness first commit forward.

**Harness scope (S2964):**

1. **`run_golden_evals` mgmt cmd** — discovers `evals/tier1/*.yaml`, iterates prompts, dispatches via substrate-specific adapter (AgentExecution write path OR ChatConversation write path), collects results, writes `GoldenEvalRun` rows.
2. **`GoldenEvalRun` table** — per-run tracking (yaml_path, prompt_id, substrate_type, primary_row_id, pass/fail, evidence_pointer results, latency_ms, run_id).
3. **Per-substrate adapter abstraction (canon_v2 Item 6 concrete)** — `EvalRunContext` dataclass + two adapters: `AgentExecutionAdapter`, `ChatConversationAdapter`. Adapters normalize substrate-native rows → `EvalRunContext`.
4. **JSON Schema executors** — validate `expected_output_shape` against agent response.
5. **Pydantic acceptance-criteria runners** — evaluate `acceptance_criteria` predicates (required_fields_present, no_unsupported_claims, no_fabricated_conversation_history, etc.).
6. **Fault-injection selector parser (canon_v2 Item 5)** — deterministic resolver for `module.Class.method` + `module.function` shapes. Errors loudly on handler-registry-key selectors (per canon_v2 Item 5 forbid).
7. **Allowlist code fix (canon_v2 Item 1)** — first commit of harness adds `ChatConversation` + `ToolCallRecord` to `_MODEL_POLICIES` at `core/services/td_handlers_agents.py:733-831` (14→16 models). Dogfood Rigby's substrate inspection immediately.
8. **Receipt-contamination filter utility (canon_v2 Item 4)** — shared query helper for AgentExecution sampling; applies `NOT (A AND B)` predicate as canonical intent.
9. **Source-stratification lint (canon_v2 Item 2)** — harness may lint that multi-source substrate slices declare a source filter in `canonical_field_mapping`.

**Recommended dogfood order:**
- **FIRST dogfood target = slice 8 (Rigby, ChatConversation substrate)** — forces canon_v2 Item 1 allowlist fix immediately + validates the two-substrate adapter cleanly + exercises the ChatConversation "finalized_at" semantics (per canon_v2 Item 6).
- **THEN** iterate through 7 AgentExecution slices in slice order (SIA → Research → DevOps → Workflow → Legal → Content → Competitor).

### Universal open sequence (unchanged)

1. **Live-verify S2953 drift scanner:** `bash tools/pa_local.sh "run agent_capability_drift_tool action=summary"` — expect shape (83/92/59/1 → 77+2 or drifted numbers with same shape). CLI mirror: `python manage.py scan_agent_capability_drift --json | jq .totals`.
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline `100 validated_full / 2 untested`.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2964 pin (retired at S2963 close cascade).
4. **Read canon_v2 doc BEFORE writing harness code:** `docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md` (190 lines). All 6 canon_v2 items bind harness shape.
5. **Read slice 8 substrate reference:** `evals/tier1/rigby_agent.yaml` (only non-AgentExecution slice; forces the two-substrate adapter shape).
6. **Open S2964 harness scope** — see 9-item scope above; dogfood slice 8 first.

### S2964 scope note: harness core vs nightly beat

Harness core (mgmt cmd + `GoldenEvalRun` + adapters + executors + fault-injection parser + allowlist code fix + receipt filter utility) IS S2964 scope. **Out of scope for S2964:** nightly beat task + pass-rate drift dashboard — that's S2965+.

**Also out of scope for S2964:** the WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR (F1 from S2958). Separate follow-up that can happen any time; unblocks `workflow_orchestration_agent.yaml` v1.1 tightening.

**Estimated 2-4 sessions** for S2964 harness core + slice-8 dogfood.

### Golden Evals arc structure (updated at S2963 close)

**Arc CLOSED.** Post-close roadmap:

- ✅ **S2954 — arc open** (Tier-1 list + Day-1 fault-injection scope) — CLOSED.
- ✅ **S2955–S2962 — Tier-1 spec-authoring (8/8 slices shipped)** — CLOSED.
- ✅ **S2963 — arc close (canon_v2 ratification)** — CLOSED.
- ⏭ **S2964 — validator harness core** — NEXT (2-4 sessions estimated).
- **S2965+** — Nightly beat task + pass-rate drift dashboard.
- **Follow-up** — WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR (F1 from S2958); then `workflow_orchestration_agent.yaml` v1.1 revision.
- **Post-harness parallel tracks** — Rigby-as-Claude-Code eval slice (per canon_v2 Item 2); PA-turn AgentExecution eval slice (requires `PA_AGENT_EXECUTION_WRITE_ENABLED` flip + 2-4 weeks traffic).
- **After harness + drift dashboard land** — A1 Reliability Audit Phase 1 first-slice (Chris's 4 gating questions from scoping deliverable `7870eca9` still block Phase 1 code).

### Capability Manifest — build spec (parallel-track from A1 Phase 1 start)

_(unchanged — see prior S2953 close snapshots; not part of Golden Evals arc)_

### A1 Phase 1 still ahead (after harness + drift dashboard land)

Chris's 4 open questions from scoping deliverable `7870eca9` still gate Phase 1 code:

1. **Minimum evidence standard** we promise? (run IDs + failure signature samples vs metrics only)
2. **Default turnaround SLA** we can consistently hit without heroics?
3. Sell as **agent-system audit** (end-to-end) or **toolchain reliability audit** (tools/contracts) first?
4. **Legal posture** for handling customer logs (retention window, deletion guarantee, allowed data types)?

### Deferred queue (updated at S2963 close)

**S2963 additions (canon_v2 discharges + new items):**
- **Fold P2 — orm_inspect_tool allowlist** — DISCHARGED as canon_v2 Item 1 (code at S2964 first commit).
- **Fold S1 — source-stratification** — DISCHARGED as canon_v2 Item 2 (doc-only).
- **Fold U1 — latency evidence** — DISCHARGED as canon_v2 Item 3 (opt-in `latency_ms` class, doc-only).
- **Fold P1 — receipt-contamination filter** — DISCHARGED as canon_v2 Item 4 (doc-only; harness utility at S2964).
- **Fold V1 — selector convention** — DISCHARGED as canon_v2 Item 5 (doc-only; harness parser at S2964).
- **Fold U2 — dual-substrate abstraction** — DISCHARGED as canon_v2 Item 6 (`EvalRunContext` shape; concrete API at S2964).
- **NEW — Complex-boolean-in-canon-doc misread pattern (from Rigby T2 De Morgan slip)** — one trigger observed. Watch for second occurrence at S2964+ before codifying as canon guidance ("canon docs should always lead with intent form for complex booleans").
- **Content-append-vs-final content discrepancy** (Ledger candidate carried from S2962 T2) — Rigby's `deliverable_tool.append` reported 16,639 chars but final was 642 bytes. Potential silent overwrite. Investigate at S2964 if it re-surfaces on this session's twin mirrors.

**Carry forward from S2961/S2960/S2959/S2958:**
- **Fold α — Routing-branch encoding vs traffic reality** — 2 consecutive avoidance triggers (S2961 + S2962). No third trigger yet. Watch S2964+ authoring; if 3rd trigger surfaces, codify as canon guidance.
- **Fold β — Domain-sensitivity predicate epistemic-labeling rescope** — carried; not codified this arc-close (small-signal, no urgency).
- **Fold D — Line-number anchoring brittleness** — Rigby zoom-out concern #3 at S2963; `EvalRunContext` (canon_v2 Item 6) helps validators avoid it. Slice YAML author-side discipline still applies. Not codified separately; watch for a second trigger.
- **Fold 3 — Evidence-tier ladder mechanization** — carried from S2959; not codified this arc-close.
- **Inline fold-disposition header pattern (S2961)** — S2962 chose NOT to use; S2963 didn't use either. Not codified (2 non-use signals suggest it's not converging).
- **WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR** (F1 from S2958) — unblocker for `workflow_orchestration_agent.yaml` v1.1 tightening. Not urgent; any session.
- **Fold A — Tier-1 must-have-tool_runs global rule vs orchestration agents** (S2958) — not codified; watch.
- **Fold C — ambiguous_input vs bad_input remediation posture separation** (S2958) — not codified; watch.

**Carry forward from S2957/S2956:**
- **Fold #1 (S2957 T2) — `health_status` dual-path enum add** — not codified this arc-close.
- **Failure-mode lens documentation** — document convention in S2964 validator design.
- **Fold #5 (S2956 T2) — `health_status` derivation over-degrade** — not codified this arc-close.
- **Fold #6b (S2956 T2) — Tier-1 canon uniformity review** — happens iteratively as harness dogfoods per slice.
- **`orm_inspect_tool` distinct-count guardrail** — group-by on text fields rejected as "expensive/unbounded". Deferred.

**S2955 additions (carry forward):**
- **Bound-annotation discipline for volume claims in YAML headers** — CI-check candidate; deferred.

**S2954 additions (carry forward):**
- **00-START validated-full gap-map lint sync** — CI-check candidate; deferred.

**S2953 additions (carry forward):**
- Drift scanner invariant 4 (rerouted-must-be-labeled) — requires `AgentRerouteEntry`-style queryable model.
- Curate `capabilities_exceptions.yaml` — 77 active findings at HEAD.
- Fix run_agent dispatch-response agent-name echo (from S2952) — echo mapping-canonical CamelCase.

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

## What's forbidden at S2963 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2963 new forbidden entries:** none.

Canon_v2 adds one new forbid: **fault-injection selectors MUST NOT use handler-registry keys as canonical** without an adapter layer (canon_v2 Item 5). Enforced at S2964 harness parser.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2963 additions to the deferred queue:**
- Complex-boolean-in-canon-doc misread pattern (Rigby T2 De Morgan slip; one trigger, watch for second).
- Rigby-as-Claude-Code eval track (post-S2964, per canon_v2 Item 2).
- PA-turn AgentExecution eval track (post-S2964, requires `PA_AGENT_EXECUTION_WRITE_ENABLED` flip + 2-4 week traffic accumulation).
- Content-append-vs-final content discrepancy investigation (Ledger candidate, carried from S2962).

**Carry forward from S2961:**
- Routing-branch encoding vs traffic reality — 2 consecutive avoidance triggers; watch for 3rd.
- Domain-sensitivity predicate count normalization + epistemic labeling rescope — not codified.
- Line-number anchoring brittleness — `EvalRunContext` mitigates; not separately codified.
- Web_search fallback dedicated test — S2964 harness scope (deterministic mocking).
- Inline fold-disposition header pattern — 2 non-use signals; not codified.

**Carry forward from S2959/S2960/S2958/S2957/S2956/S2955/S2954/S2953/S2952/S2951:**
_(unchanged — see S2962 close snapshot)_

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

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) + pre-A1 capability triage (S2952) + capability substrate (S2953 Drift Scanner) + Golden Evals arc (S2954-S2963) are adjacent-domain net-new engineering + arc substrate, not sweep work.

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

## For fuller context (S2846 → S2963)

See:
- **S2963 handoff (current):** `docs/handoffs/SESSION_2963_GOLDEN_EVALS_ARC_CLOSE_CANON_V2.md`
- **S2963 shipped doc:** `docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md` (190 lines, canon_v2 ratification)
- **S2962 handoff:** `docs/handoffs/SESSION_2962_GOLDEN_EVALS_SLICE_8_RIGBY_YAML.md`
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
