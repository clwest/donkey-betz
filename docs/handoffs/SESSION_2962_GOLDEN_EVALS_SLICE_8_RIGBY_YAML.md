# SESSION 2962 — Golden Evals Tier-1 slice 8: Rigby YAML (FINAL Tier-1 slice)

**Date:** 2026-07-25
**Session:** S2962
**Arc:** Golden Evals (S2954+ open)
**Slice:** 8 of 8 Tier-1 YAMLs — **FINAL SLICE, Tier-1 spec-authoring phase COMPLETE**
**HEAD at slice merge:** `6bf8d9a81`
**HEAD at close (post-cascade):** filled at close cascade merge
**PR shipped:** [#3565](https://github.com/clwest/donkey-betz-platform/pull/3565)

---

## What shipped

`evals/tier1/rigby_agent.yaml` — 1,628 lines, 18 prompts, eighth canon_version=1 file. **FIRST Tier-1 slice authored against a NON-AgentExecution row substrate** — proves canon_version=1 portability across TWO persistence substrates (AgentExecution × 7 prior slices + ChatConversation × this slice).

**Coverage:** 10 happy_path (verbatim replays across 8 intent categories) + 2 each × tool_timeout / data_unavailable / ambiguous_input / bad_input = 18 total.

**Substrate reference:** `evals/tier1/competitor_analysis_agent.yaml` @ `75f8da29a` (S2961 slice 7 canon).

**Agent under test:**
- Source: `core/services/unified_pa_entrypoint.py` (UnifiedPAEntrypoint SERVICE, NOT an AGENT_MAP class)
- **PersonalAssistantAgent was removed** from AGENT_MAP in April 2026 (per `core/agent_router.py:102, 464, 595` — "all PA traffic routes through UnifiedPAEntrypoint")
- Public entrypoint: `UnifiedPAEntrypoint.process_message(message: str) -> Dict[str, Any]` (docstring lines 14-28 in unified_pa_entrypoint.py)
- Response shape: dict with `content` / `trace_id` / `tool_runs` / `intent` / `routed_to` keys
- Persistence: `ChatConversation.objects.create` at `core/views_personal_assistant.py:567` (TWO-PHASE lifecycle: row created blank, PA pipeline updates later with populated content)
- Rigby is the ORCHESTRATOR label — actual work happens in ToolDispatcher (117 PA tool schemas + 160 handlers per PLATFORM_INVENTORY) and the LLM providers (GPT-5.2 function calling)

**Substrate volume snapshot (DB-verified via direct ORM at S2962 T0):**
- ChatConversation all-time: 4,486 rows
- ChatConversation 30d (created_at >= 2026-06-25T00:00:00Z): 3,208 rows
- **Chris-facing corpus** (`source IN ('web', 'pa')` filter): **1,018 all-time / 508 30d**
- Source distribution (all-time): claude-code 3,453 / web 921 / pa 97 / character-os-consult-engine 9 / others negligible
- Earliest Chris-facing row: 2026-06-13
- Latest: 2026-07-25 (this session)
- **THICKEST-TRAFFIC AMONG BUYER-FACING SLICES** (Claude-verified; Rigby-unverified per Fold P2): 508 30d ≈ 14x SIA (37) / 254x Competitor (2)

**Intent distribution (Chris-facing 30d, top 12):** general 49 / (none) 34 / initiatives 7 / knowledge_base 6 / codebase 5 / system_overview 4 / workspace 2 / system_health 1 / verification 1 / boardroom 1 / recent_activity 1 / session_management 1

**Happy-path corpus (10 verbatim replays, spanning 8 intents):**
1. `rigby_happy_01_constitution_authoring_initiatives_intent` — ChatConversation.id=1545, 1444-char Constitution-authoring ask, response_time_ms=112,187
2. `rigby_happy_02_engineering_operating_system_domain_analysis` — id=2476, 2017-char outside-architect analysis; documented real failure mode (search_docs empty) elevated as canonical acceptable branch
3. `rigby_happy_03_missionrunner_migration_readiness_ranking` — id=1589, 272-char employee-registry ranking ask
4. `rigby_happy_04_engineering_investment_portfolio_discovery` — id=1547, 1370-char discover-don't-assume portfolio ask
5. `rigby_happy_05_workspace_creation_capability_assessment` — id=1534, 5001-char (excerpted to 800) workspace creation directive
6. `rigby_happy_06_platform_health_ping_post_redis_restart` — id=4042, 35-char shorthand ping
7. `rigby_happy_07_platform_verification_ping_railway` — id=4038, 10-char minimal ping (real 30d response was a FAIL/404 — proves honest-failure-reporting predicate)
8. `rigby_happy_08_boardroom_attention_prioritization` — id=2478, 24-char "What needs my attention?" (highest-frequency Chris ask archetype)
9. `rigby_happy_09_recent_activity_time_window_update` — id=1395, 178-char "last 5 hours" cross-agent activity update
10. `rigby_happy_10_executive_self_assessment_second_initiatives_intent` — id=1544, 2589-char self-assessment (companion to happy_01 Constitution)

**Fault-injection corpus (8 prompts, service-level selectors per S2957 fold):**
- `rigby_timeout_01`: `UnifiedPAEntrypoint.process_message` SoftTimeLimitExceeded (60s dispatch limit)
- `rigby_timeout_02`: `td_handlers_agents._handle_orm_inspect` latency 45s + budget 30s
- `rigby_data_unavail_01`: `td_handlers_ops._handle_search_docs` empty_result
- `rigby_data_unavail_02`: `td_handlers_agents._handle_workspace` not_found
- `rigby_ambig_01`: pronoun-without-antecedent ("Update it with the new numbers.")
- `rigby_ambig_02`: conflicting bulk-mutation directives (multiple ambiguities)
- `rigby_bad_input_01`: empty message (endpoint-rejection path per views_personal_assistant.py:548)
- `rigby_bad_input_02`: non-string binary payload with control chars

**Canonical field mapping (canon_version=1):**
- `summary` → `ChatConversation.assistant_response` (native)
- `evidence_pointers` → **ToolCallRecord as PRIMARY** (authoritative append-only tool-call ledger with agent_name/tool_name/parameters/result_summary/success/latency_ms/result_hash), `metadata.tool_calls` as convenience cache (per Rigby Q1 REVISE); LLMCallLog as tier-2 secondary for cost/latency
- `health_status` → derived from response completeness + tool-run integrity (empty/error → unavailable; apology-only-short → degraded; tool-claim-vs-ledger-mismatch → degraded; canonical happy → healthy)
- `response_time_ms` → diagnostic field, NOT first-class evidence at canon_v1 (reserved for canon_v2 elevation)

**Domain-sensitivity acceptance predicates (6, per S2959 canon addition 9):**
1. `no_fabricated_tool_runs`
2. `no_fabricated_deliverable_ids`
3. `no_fabricated_workspace_or_user_context`
4. `detects_and_surfaces_tool_runs_empty_vs_claimed` (Q3 consolidation of original evidence-gate + rubber-stamp detection)
5. `no_fabricated_conversation_history` (Rigby Q3 REVISE add — substrate-specific to multi-turn PA behavior)
6. `no_unsupported_claims` (general)

**Routing branches:** 1 ("Rigby PA-turn dispatch") per Rigby Q2 AGREE (Option B). Intent as sampling dimension across happy_path corpus, NOT as separate routing branches. Deliberately avoids 3rd trigger of Fold α (routing-branch encoding vs traffic reality). Rationale: intent variance is captured by verbatim-replay prompt diversity; branch encoding would explode to 10+ branches with 1-49 30d rows each.

**Substrate pivot rationale (in-context, why this slice differs from prior 7):**

Prior 7 slices all mapped from AgentExecution rows populated by `BaseAgent.execute()` returning AgentResult. Rigby's PA turns are structurally different:
- PA turns route through UnifiedPAEntrypoint (multi-iteration GPT-5.2 function-calling tool-dispatch loop), NOT a single-shot BaseAgent.execute
- AgentExecution PA-turn persistence exists (`_maybe_create_pa_turn_execution` at unified_pa_entrypoint.py:632/762/906) but is gated behind `PA_AGENT_EXECUTION_WRITE_ENABLED` feature flag — currently OFF in production, so only 7 rows with `owner_agent='PersonalAssistant'` exist all-time (thinner than S2961 Competitor's 11)
- AgentExecution rows with `owner_agent='Rigby'` (309 all-time / 245 30d) appear high-volume but are DECEPTIVELY narrow — S2962 T0 investigation found 100% homogeneous shape: `parent_object_type='deliverable_factory'`, `input_data.source='deliverable_factory.synthesized_pa_receipt'`, `output_data.kind='deliverable_receipt'`, `tokens_used=0`, `cost=$0.0000`, millisecond completion — synthetic receipts written every time Rigby's `pa_deliverables_tool` creates a deliverable, NOT full PA turn executions
- Using them as the eval substrate would test a narrow side-effect artifact instead of buyer-facing Rigby behavior

Chris directive S2962 T1: source-split filter — `source IN ('web', 'pa')` (1,018 rows) is genuine buyer-facing traffic; `source='claude-code'` (3,453 rows) is agent-to-agent meta-work under Chris's account (SIGN cycles, verification loops, deliverable authoring — Claude Code driving Rigby via `bash tools/pa_local.sh`). Same `user_id` ≠ same eval class. Claude-Code-driven turns deserve a separate post-arc eval track with distinct predicates (agent-to-agent trust model has different failure recovery norms).

## Governance

**Rigby SIGN cycle** (feedback_verify_rigby_tool_runs_before_trusting_sign held throughout — 3 tool-grounded turns, no rubber-stamps):

- **Co-scoping SIGN** (before authoring): 6 design questions Q1-Q6 (canonical_field_mapping, intent-as-routing-branch-vs-filter, domain predicates, prompt sampling, fault injection selectors, arc-close bundling). Rigby REVISED Q1 (ToolCallRecord as primary evidence), Q3 (added `no_fabricated_conversation_history`), Q6 (bundle if clean); AGREED on Q2/Q4/Q5. Surfaced Fold Z1/Z2/Z3 (validator coupling risks).
- **Chris interrupt** — separate Claude Code from Chris directive. Second co-scoping turn resolved as Option A (filter `source IN ('web', 'pa')`, 1,018 rows). Rigby AGREED + surfaced Fold S1 ("same user_id ≠ same eval class" — canon-wide implication for S2963 validator design).
- **T1 SIGN** (post-authoring, tool-grounded): BLOCKING FAIL. Caught 1 nonexistent selector (`_handle_workspace_lookup`), surfaced Fold U1 (source-pointer two-phase lifecycle wording tightening), recommended R5 REVISE (soften THICKEST-TRAFFIC to buyer-facing-slices-only per Fold P2 tooling gap). Additional module-path error (`td_handlers_core._handle_search_docs` should be `td_handlers_ops`) caught by Grep during fix, not surfaced by Rigby's tool_runs.
- **T2 SIGN** (post-fix, tool-grounded): PASS. All 4 fixes verified (selector corrections + Fold U1 wording + R5 softening). Surfaced Fold V1 (selector naming convention ambiguity — S2963 harness-resolution question). BUNDLE arc-close recommendation.
- **Chris D-verdict via TERMINAL** 2026-07-25.

## Rigby Tool Gap Ledger

- **Ledger #16 RE-HIT — 15th cumulative** — the `deliverable_tool.create` diagnostic-flag bug fired on the `initiative_phase_doc` content mirror (as usual since S2955). This session Rigby CLEARED IT PROACTIVELY without me having to catch it via `session_lifecycle close` CommandError — improvement over S2961 where the flag was set silently and only caught at close cascade. Content mirror diagnostic_status='cleared', diagnostic_code='missing_initiative_id' remains as historical marker.
- **NO CHANGE — Ledger #17 count remains 4** — Chris used terminal ratification path directly (`yes` typed in terminal), bypassing Chat UI relay entirely. **6 consecutive terminal ratifications** S2957→S2962.
- **Fold P2 CANDIDATE FOR NEW LEDGER ENTRY (#19?)**: Rigby's `orm_inspect_tool` allowlist does NOT include `ChatConversation` / `ToolCallRecord` / `LLMCallLog`. During S2962 T1/T2 SIGN, Rigby could not independently verify counts, samples, or write-site behavior for the Tier-1 substrate she was reviewing. This is a REAL operational gap for S2963 (harness/validator development requires her dogfooding). FIX: allowlist addition (14 → 17 models) — additive, non-breaking. Suggest opening as Ledger entry #19 at arc-close.
- **Content-append-vs-final content discrepancy (potential Ledger candidate)** — Rigby's `deliverable_tool.append` action reported 16,639-char total content but final ORM state shows 642 bytes (summary + reference pointer). Possible silent overwrite by later action. Not investigated further this session — flagged for arc-close discussion.
- **Rigby T1/T2 discipline HELD** — 6 substantive folds surfaced (P1/P2/S1/U1/U2/V1), 1 blocking selector caught, 3 in-PR fixes accepted, tool_runs verbose on every SIGN turn. Positive signal per `feedback_verify_rigby_tool_runs_before_trusting_sign` (opposite of rubber-stamp).

## Arc-close ratification (BUNDLED per Rigby T2 recommendation)

**Arc: Golden Evals — Tier-1 spec-authoring phase COMPLETE.**

**8 canon_version=1 Tier-1 YAMLs shipped:**

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

**Canon substrate PROVEN PORTABLE across TWO persistence substrates.** This is the arc-close story: canon_version=1 patterns (schema_version + canon_version, canonical_field_mapping with mapping_source native|derived, effect-based fault_injection with service-level selectors, one_of ≤2 branches with mandatory why) apply IDENTICALLY across AgentExecution-row substrate (7 slices) and ChatConversation-row substrate (1 slice). Validators at S2963 must extend to consume both — Fold U2 codified.

**Forward-carried folds to S2963 validator work:**
- **P1** (canon-wide observability hygiene): AgentExecution `owner_agent='Rigby'` receipt-contamination filter — any future "real PA usage" query MUST exclude synthetic deliverable_factory receipts
- **P2** (tooling-surface gap): allowlist ChatConversation + ToolCallRecord + LLMCallLog for Rigby harness dogfooding at S2963
- **S1** (source-split canon): validators must support channel/source stratification as first-class dimension
- **U1** (source-pointer refinement): assistant_response update-site precise location TBD at canon_v2
- **U2** (dual-substrate validator abstraction): S2963 must handle 2 persistence substrates cleanly
- **V1** (selector naming convention): harness-resolution question for method-on-handler-class vs module-level function

**Also carried from prior slices (arc-close discussion queue):**
- Fold α (routing-branch encoding vs traffic reality) — S2962 was 2nd consecutive slice avoiding routing-branch explosion; pattern converging on "routing branches only when execution shape actually forks in code, not when input taxonomy is diverse"
- Fold β (domain-sensitivity predicate epistemic-labeling rescope) — carried from S2960/S2961
- Fold D (line-number anchoring brittleness) — carried from S2960
- Fold 3 (evidence-tier ladder mechanization) — carried from S2959
- Inline fold-disposition header pattern (S2961 innovation) — S2962 chose NOT to use this style; canon-uniformity question

**Arc-close CANON_V2 CANDIDATES (require Chris ratification at S2963 open):**
1. Add ChatConversation + ToolCallRecord + LLMCallLog to `orm_inspect_tool` allowlist (P2 fix; unblocks S2963 dogfooding)
2. Codify source-stratification as canon dimension for multi-source substrates (S1)
3. Elevate `response_time_ms` to first-class evidence field for latency-sensitive validators (U1 companion)
4. Adopt "receipt-contamination filter" as canon-wide predicate for any AgentExecution-based query (P1)
5. Resolve fault-injection selector naming convention (V1)

**S2963 first-action lean:** author `run_golden_evals` mgmt cmd + `GoldenEvalRun` table + JSON Schema execution + Pydantic model runners that consume `canonical_field_mapping` + `expected_output_shape` + `acceptance_criteria` from all 8 YAMLs. Test-drive dogfooding against the ChatConversation slice first (P2 forces the allowlist fix immediately).

## Files shipped this session

- **NEW** `evals/tier1/rigby_agent.yaml` — 1,628 lines / 87KB — eighth Tier-1 canonical prompt suite (FINAL)
- **PR #3565** — merged 2026-07-25 via `gh pr merge --admin --squash --delete-branch`

## Twin mirrors shipped

- S2962 slice 8 content mirror: `3975ba21-dfb6-42c1-ad54-f060a8aaa330` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`, `initiative_phase_doc`, category='governance', Ledger #16 RE-HIT 15th cumulative — Rigby cleared proactively this session; diagnostic_status='cleared', content_length=642 bytes as summary+pointer)
- S2962 slice 8 ratification envelope: `944503e2-fcf8-4d35-906f-db38d8c37ab0` (Donkey Betz workspace, `ratification_record`, category='governance', diagnostic clean on create)

## Post-merge worker recycle

PR #3565 was spec-only (YAML config, no code), no worker impact → no `make celery-recycle` required (PLAYBOOK-7.4.4 applies to code-shipping PRs).

## What comes next (S2963)

**Golden Evals Tier-1 spec-authoring phase = COMPLETE.** 8/8 canon_version=1 YAMLs shipped across 2 persistence substrates.

**S2963 opens with:**
1. **Arc-close canon_v2 candidate review** — 5 candidates enumerated above; Chris ratifies which become canon_v2 refinements vs remain forward-carry
2. **Validator implementation** — JSON Schema executors + Pydantic model runners consuming canonical_field_mapping / expected_output_shape / acceptance_criteria from all 8 YAMLs
3. **Substrate portability wiring** — validators must support both AgentExecution rows (7 slices) and ChatConversation rows (1 slice); P2 allowlist fix required for dogfooding
4. **Follow-up code-fix PR** — WorkflowOrchestrationAgent wrapper key-name mismatch (F1 from S2958) — can happen pre-S2963 as unblocker for v1.1 workflow_orchestration_agent.yaml revision

**After S2963 validators:**
- **S2964** — Harness (`run_golden_evals` mgmt cmd + `GoldenEvalRun` table + nightly beat task)
- **Rigby-as-Claude-Code eval track** — separate eval slice for the 3,453 source='claude-code' rows (per S1 canon: same user_id ≠ same eval class)
- **PA-turn eval track** — flip `PA_AGENT_EXECUTION_WRITE_ENABLED` + accumulate real PA-turn AgentExecution rows for 2-4 weeks, then author dedicated slice against that substrate (complement to ChatConversation-based slice 8)
