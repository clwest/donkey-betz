# SESSION 2961 — Golden Evals Tier-1 slice 7: CompetitorAnalysisAgent YAML

**Date:** 2026-07-25
**Session:** S2961
**Arc:** Golden Evals (S2954+ open)
**Slice:** 7 of 8 Tier-1 YAMLs
**HEAD at slice merge:** `75f8da29a`
**HEAD at close (post-cascade):** filled at close cascade merge
**PR shipped:** [#3563](https://github.com/clwest/donkey-betz-platform/pull/3563)

---

## What shipped

`evals/tier1/competitor_analysis_agent.yaml` — 1232 lines, 13 prompts, seventh canon_version=1 file.

**Coverage:** 5 happy path + 2 each tool_timeout / data_unavailable / ambiguous_input / bad_input.

**Substrate reference:** `evals/tier1/content_writer_agent.yaml` @ `10b6b3ab1` (S2960 slice 6 canon).

**Agent under test:**
- Source: `core/agents/business/competitor_analysis_agent.py:128` (CompetitorAnalysisAgent class).
- File size: 1783 lines / 78 KB.
- Five execution routing branches in `execute()` at line 636 (all inside same agent contract, framed as routing branches per S2959 canon addition 10):
  - **(A) STANDARD tool-dispatch mode** — default path at line 884+ when task validates, viability_score >= 50, and tool loop produces `all_competitor_data`. Multi-tool GPT dispatch (spider_query / analyze_competitor / generate_swot / refresh_spider_data / get_prior_research / web_search-fallback). Returns AgentResult with FULL data payload.
  - **(B) VIABILITY_EARLY_EXIT branch** — Session 350 "Idiot Protector" pattern; triggered when `_check_business_viability` at line 712 returns viability_score < 50. Returns AgentResult with `data.type='viability_feedback'`, `data.early_exit=True`, constructive feedback. NO tool calls. success=True (helpful redirect).
  - **(C) EVIDENCE_GATE branch** — Session 1023 "Minimum Evidence Gate"; triggered at line 949 when `_synthesize_analysis` returns `status='insufficient_evidence'`. Two sub-branches at line 1560 (MIN_DATA_POINTS=3 gate) and line 1588 (MIN_DOMAIN_RELEVANCE=15% gate). Returns AgentResult with `data.type='insufficient_evidence'`, `gate_reason`, `recommended_actions`. success=True (gate firing IS the correct behavior on thin evidence).
  - **(D) CONVERSATION_FALLBACK branch** — triggered at line 1119 when GPT returns no tool calls AND `all_competitor_data` is empty. Returns AgentResult with `data.type='conversation'`, `message=gpt_response.content`. Typically fires on meta-questions.
  - **(E) EXCEPTION branch** — top-level try/except at line 1129. Returns AgentResult with `success=False`, `error=str(e)`. Also covers line 660 `_validate_task` early-return ("Invalid or empty task").

## Volume snapshot (DB-verified via direct ORM at authoring T0)

- **30d executions** (`created_at >= 2026-06-25T00:00:00Z`): **2** (THINNEST in arc)
- **All-time**: **11** (all completed, ZERO historical failure rows ever — the ONLY Tier-1 agent shipped with zero failure history)
- **Earliest**: 2026-06-23; **Latest**: 2026-07-24
- **Only 1 of 11** all-time prompts is a real competitive-analysis ask (the 2026-06-25 Donkey Betz identify-competitors prompt, exec `3bc1df00-2288-4a9c-baef-c5ede3f1d502`, execution_time_ms=35195); the other 10 are smoke tests / URC receipts / fleet smoke runs.
- **Zero non-empty error_message rows** — all fault_injection prompts are constructed from code paths (line 660 validate guard, line 712 viability early-exit, line 949 evidence gate, line 1129 exception handler, line 890 time-budget branch) rather than replaying historical failure rows. Most speculative fault-injection coverage in the arc.

## Arc traffic comparison

| Slice | Agent | 30d execs | All-time | Failure samples |
|---|---|---:|---:|---:|
| S2955 | SIA | 37 | 100+ | multiple watchdog + fabrication |
| S2956 | ResearchAgent | 37 | 90+ | multiple watchdog |
| S2957 | DevOpsAgent | 13 | 40+ | watchdog |
| S2958 | WorkflowOrchestrationAgent | 9 | 30+ | watchdog |
| S2959 | LegalDocDrafterAgent | 5 | 10+ | watchdog |
| S2960 | ContentWriterAgent | 7 | 23 | 2× watchdog + 1× worker restart |
| **S2961** | **CompetitorAnalysisAgent** | **2** | **11** | **ZERO** |

## Domain-sensitivity predicates (5, proportional harm class)

Per S2959 canon addition 9, competitor-analysis outputs drive real investment/pricing/positioning decisions with buyer-facing quality-risk (not categorical/irreversible like legal drafting). 5 predicates layered on top of the general `no_unsupported_claims`:

1. `no_fabricated_competitor_names`
2. `no_fabricated_pricing_financial_or_headcount_metrics`
3. `no_fabricated_executive_quotes_or_attributions`
4. `distinguishes_evidence_from_inference`
5. `honors_data_freshness_or_admits_gap`

Same count as ContentWriterAgent (5); fewer than LegalDocDrafterAgent (7).

## Rigby SIGN cycle T1→T3 tool-grounded

**T1** — 6 zoom-out folds surfaced from Rigby's stepping-back review of the initial YAML. Tool-grounded verification via:
- `orm_inspect_tool.filter` on AgentExecution (volume snapshot: 11 all-time / 2 30d / zero failure rows raw output returned)
- `orm_inspect_tool.get` (verbatim task string byte-match for exec `3bc1df00`)
- `repo_tool.read_file` (line refs at 128/147/187/636/660/712/890 verified)
- `repo_tool.search` (execute + TIME_BUDGET_SECONDS + _check_business_viability confirmed)

**T2** — AGREE on all 4 in-PR fold-fix outcomes verified via `repo_tool.read_file`:
- (a) Fold γ harness-fixture removal: `competitor_happy_02` renamed to `..._domain_extraction_fallback`, `competitor_ambig_02` renamed to `..._task_internal_market_contradiction`, both with `context: {}`, no `project_id` field, both notes reference "REWRITTEN FROM ORIGINAL (per Rigby T1 fold γ)"
- (b) Fold δ `spider_query_invoked_in_tool_calls` predicate added to `competitor_happy_01` acceptance criteria + notes rationale bullet
- (c) Fold ε BOUNDARY-CONDITION TEST disclaimer added to `competitor_happy_04` notes
- (d) Fold header section `── Rigby T1 folds applied (S2961) ──` with all 6 fold dispositions
- 1 new T2 zoom-out: inline fold-doc pattern is style drift from prior 6 slices; normalize at S2962 arc-close

**T3** — AGREE on all remaining line refs + substrate reference:
- (a) EVIDENCE_GATE branch at line 949 + return 953-974 (`success=True` with `data.type='insufficient_evidence'`)
- (b) `BusinessResearchResult.save_competitor_analysis` at line 1009-1015 + `_save_to_deliverable` at line 1060
- (c) CONVERSATION_FALLBACK at line 1119-1127 + exception handler at line 1129-1136 + spider_query handler at line 1150 + `SpiderSemanticSearch.semantic_search` invocation at line 1153
- (d) `MIN_DATA_POINTS = 3` at line 1557, `MIN_DOMAIN_RELEVANCE = 15` at line 1558, gate checks at line 1560 + line 1588
- (T3-2) `evals/tier1/content_writer_agent.yaml` exists at HEAD `75f8da29a` with `schema_version: 1` + `canon_version: 1` + `arc_slice: S2960`
- (T3-3) **NOT-A-BUG finding**: `orm_inspect_tool.count_by(field="status")` handles group-by cleanly (returned `[{"value": "completed", "count": 11}]`). Prior S2959/S2960 "count_by bug" was schema misuse (`group_by` vs `field` kwarg), not a code bug. Ledger #18 candidate CLOSED.
- Ship-readiness zoom-out: unblocked at HEAD `e631ab0fb` (pre-merge SHA)

## Folds — in-PR fixes (3)

**Fold γ (harness fixture avoidance):** `competitor_happy_02` and `competitor_ambig_02` were originally written with `project_id: "test-project-uuid-placeholder-*"` context fields requiring S2963 harness to instantiate mock `PartnershipProject` rows. Rigby flagged as fixture-brittle — eval failures could reflect harness/environment drift rather than agent regressions. REWRITTEN:
- `happy_02` now uses plain dict `context: {}` + task carries explicit domain signals ("KYC, compliance, fintech, payments, SMB") to exercise Session 490 domain-extraction FALLBACK path (line 685-702).
- `ambig_02` uses task-internal contradiction (fintech-payments framing pivots to healthcare-vertical specifics mid-sentence) instead of task-vs-project-context conflict.

**Fold δ (spider_query principal-contract predicate):** system_prompt line 152-160 explicitly mandates spider_query as PRIMARY data source ("MOST IMPORTANT - real data!" + "CRITICAL - You MUST use spider_query"). Original acceptance criteria for `competitor_happy_01` required `tool_calls_list_present_with_at_least_one_entry` (any tool call satisfies) but did not explicitly assert spider_query was invoked. ADDED: `spider_query_invoked_in_tool_calls` predicate to test the principal contract.

**Fold ε (evidence-gate realism disclaimer):** `competitor_happy_04` (niche-domain evidence-gate test — "stained-glass artisans in rural Portugal") flagged as potentially reference-trivial (synthetic prompt engineered to force gate). ADDED: BOUNDARY-CONDITION TEST disclaimer preventing downstream gate-threshold refactors (line 1557 MIN_DATA_POINTS + line 1558 MIN_DOMAIN_RELEVANCE) from calibrating against this prompt as "typical."

## Folds — forward-carry to S2962 arc-close (3)

**Fold α (routing-branch encoding vs traffic reality):** Rigby leans toward collapsing S2961 from 5 routing-branch happy_paths to 3 (STANDARD + STANDARD_with_domain + ONE non-STANDARD sampler). SECOND trigger for her S2960 Fold A — strengthens the canon_v2 candidate. NOT fixed in-PR because mid-arc collapse would break consistency with 6 prior slices (all encoded multiple routing branches at similar-or-worse traffic-to-branch ratios).

**Fold β (epistemic-labeling predicate rescoping):** Rigby recommends re-scoping domain-sensitivity predicates from blanket prohibitions (`no_fabricated_X`) toward epistemic-labeling ("if X not sourced, label as hypothesis + request validation"). Canon-wide refactor affecting all 7 shipped YAMLs; strengthens her S2960 Fold B (predicate count normalization) into a rename+rescope proposal.

**Fold ζ (dedicated web_search fallback test):** Rigby suggests a dedicated test exercising the web_search-fallback branch at line 929-939. Requires deterministic harness/mocking of GPT tool-selection behavior — belongs to S2963 validator + harness design, not S2961 YAML scope.

## Twin mirrors

- **Content mirror**: `56664ff4-1da4-43a8-944b-d09c09a8a5a7` (Donkey Betz workspace, `initiative_phase_doc`, `category='governance'`, **Ledger #16 RE-HIT — 14th cumulative**, diagnostic flag `missing_initiative_id` cleared via `deliverable_tool.clear_diagnostic` at close cascade; Rigby's initial "no re-hit" report was incomplete — the flag was set on the row but not surfaced in the initial `create` response detail block. `session_lifecycle close` caught it via CommandError and blocked the close until the flag was cleared, then completed cleanly)
- **Ratification envelope**: `6815da1e-a991-43d3-a285-33561500df31` (Donkey Betz workspace, `ratification_record`, `category='governance'`, diagnostic clean on create — no re-hit)

## Rigby Tool Gap Ledger

- **Ledger #16 (deliverable_tool.create diagnostic-flag bug)**: **RE-HIT — 14th cumulative**. Initial Rigby report at twin-mirror creation said "no re-hit detected" because the flag was set on the row but not surfaced in the tool's `create` response detail block. `session_lifecycle close` caught the discrepancy via CommandError ("--content-mirror-id flagged diagnostic_status='diagnostic' — cannot serve as twin mirror"). Cleared via `deliverable_tool.clear_diagnostic` (recipe route B per S2956 forward-carry — sticky-cleared with `diagnostic_status='cleared'`). Second-order insight: the Ledger #16 recipe drift (dual-route documentation) forward-carry from S2956 should be prioritized higher — Rigby's initial-report gap for this bug is a distinct observability failure separate from the underlying create-bug itself.
- **Ledger #17 (Chat UI response-relay gap)**: Count unchanged at 4 — Chris used terminal ratification path directly (`yes` typed in terminal), bypassing Chat UI relay entirely. Consistent with S2957 + S2958 + S2959 + S2960 pattern (**5 consecutive terminal ratifications S2957→S2961**).
- **Ledger #18 candidate (count_by group_by bug from S2959/S2960)**: **CLOSED as not-a-bug**. T3 confirmed `orm_inspect_tool.count_by(field="status")` handles group-by cleanly. Prior "bug" was schema misuse (`group_by` vs `field` kwarg naming). Remove from S2962 Deferred Queue.
- **Rigby T1/T2/T3 discipline HELD**: 6 substantive zoom-out folds surfaced across the SIGN cycle, 3 in-PR fixes accepted verbatim, 3 forward-carries logged with clear justifications, 1 NOT-A-BUG finding surfaced. Positive signal per `feedback_verify_rigby_tool_runs_before_trusting_sign` — opposite of rubber-stamp. Tool_runs verbose on every SIGN turn.

## Post-merge

Spec-only YAML addition (PR #3563 was config, no code). No worker impact → no `make celery-recycle` required per PLAYBOOK-7.4.4 (applies to code-shipping PRs).

## Chris D-verdict

`yes` via terminal 2026-07-25 (**5th consecutive terminal ratification** S2957→S2961).

---

## What next session (S2962) should open with

**S2962 arc-slice scope: PersonalAssistant (Rigby) YAML + arc-close review.**

S2962 is the FINAL Tier-1 slice + arc-close ratification. Two components:

**(A) Slice 8 YAML** — `evals/tier1/personal_assistant_agent.yaml` (or `rigby_agent.yaml` depending on naming — verify agent class name first). PersonalAssistant is the buyer-facing surface Rigby herself uses; largest tool surface (117 schemas + 160 handlers per PLATFORM_INVENTORY); most cross-cutting agent in the arc. Traffic will be THICK (probably highest 30d execution count of any Tier-1 slice — Rigby fires dozens of times per session).

**(B) Arc-close canon-uniformity review** — before ratifying slice 8, review all 8 shipped Tier-1 YAMLs against the accumulated fold-carry-forward queue:

**canon_v2 candidates (4):**
- Fold #5 from S2956 — `health_status` derivation over-degrade for open-world agents (UNKNOWN→degraded may over-penalize research/analysis)
- Fold #1 from S2957 — `health_status` dual-path enum for advisory-vs-config-gen agents (`healthy_no_tools_expected`)
- Fold 3 from S2959 — evidence-tier ladder mechanization (does S2963 validator consume prose `derivation_spec` via text-parsing, or does canon need typed evidence-tier entries?)
- Fold A from S2960 — routing-branch encoding vs traffic reality (2nd trigger from S2961 Fold α; strongest carry-forward)

**canon-consistency questions (4):**
- Fold B from S2960 — domain-sensitivity predicate count normalization (2/3/5/7 across shipped slices; also S2961 Fold β epistemic-labeling rescoping)
- Fold D from S2960 — line-number anchoring brittleness (exact line refs vs function-name + string-literal landmarks)
- Fold #6b from S2956 — Tier-1 canon uniformity review (comment-vs-usage mismatches)
- S2961 T2 zoom-out — inline fold-doc pattern (S2961 only; normalize or keep-lean)

**follow-up code PRs (2):**
- S2958 WorkflowOrchestrationAgent wrapper key-name mismatch (`_compile_final_result` emits `'steps'`, wrapper reads `'step_results'`) — can happen before S2963 validators
- Ledger #18 CLOSED (not-a-bug this session) — no code PR needed

**Deferred queue additions from S2961:**
- Ledger #16 miss investigation — if Ledger #16 stays quiet at S2962 slice-8 close cascade, likely intermittent; if it re-hits, first-miss anomaly rather than resolution
- S2961 T2 zoom-out (inline fold-doc pattern) — decide at S2962 whether to normalize across all 8 or move dispositions to ratification envelopes

**Estimated 1-2 sessions** for slice 8 authoring + arc-close review. May run parallel if arc-close review is deferred to a separate session (S2963 opens on validator implementation regardless).

---

## Files touched this session

- **NEW**: `evals/tier1/competitor_analysis_agent.yaml` (1232 lines, 13 prompts, seventh canon_version=1 reference)
- Handoff (this file)
- 00-START-NEXT-SESSION.md refresh (points at S2962 slice 8)
- Wrapper pin bump (`tools/pa_local.sh` — retires S2961 pin, mints S2962 pin)

## References

- **S2961 PR**: [#3563](https://github.com/clwest/donkey-betz-platform/pull/3563) merged at HEAD `75f8da29a`
- **Substrate reference**: `evals/tier1/content_writer_agent.yaml` (S2960 sixth reference, canon_version=1)
- **Reliability contract source**: `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md` §3
- **A1 Wedge scoping deliverable**: `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope**: `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger**: `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
- **Ledger #17 (Chat UI relay gap)**: `db316865-d08c-4cc1-9d8e-cfac249e8c89`
- **Chat UI relay design task**: `f3f140f9-87bf-488b-8757-eab5d8058f45`
- **Parent-workspace multi-Claude rulebook**: `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
