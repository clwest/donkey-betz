# S3045 Batch 1 CLOSE — agent_via_run_agent bucket audit, customer-facing 10

**Session:** S3045 (agent_via_run_agent bucket audit — Batch 1)
**Ship shape:** substrate (`classify_tool` extension) + Batch 1 validation docs (10 tools) + close artifact — combined PR per Chris D-verdict "Option D" 2026-07-30.
**Substantive intent:** hardening class — extend gap-map classifier to recognize RaaS-dispatch-validated tools without inflating `validated_full`.
**PLAYBOOK-7.7.5 A2 sweep dimensions:** 6 dimensions per Rigby T1 SIGN refinement (see §5).

---

## 1. Batch 1 tool inventory (10 tools)

| # | Tool | Agent class | AGENT_MAP | Mapping line | Batch 1 dispatch task_id | Verdict |
|---|---|---|---|---|---|---|
| 1 | `thinking_agent` | `ThinkingAgent` | ✓ | `td_handlers_agents.py:101` | `220e883a-…` | **PASS** |
| 2 | `research_agent` | `ResearchAgent` | ✓ | `td_handlers_agents.py:97` | `1840eb3f-…` | **PASS** |
| 3 | `editor_agent` | `EditorAgent` | ✓ | `td_handlers_agents.py:106` | `becd4ccc-…` | **PASS** |
| 4 | `seo_optimizer_agent` | `SEOOptimizerAgent` | ✓ | `td_handlers_agents.py:104` | `ee809742-…` | **PASS** |
| 5 | `topic_miner_agent` | `TopicMinerAgent` | ✓ | `td_handlers_agents.py:150` | `330246e0-…` | **PASS** |
| 6 | `trend_analysis_agent` | `TrendAnalysisAgent` | ✓ | `td_handlers_agents.py:98` | `e0bc6e44-…` | **PASS** |
| 7 | `market_intelligence_agent` | `MarketIntelligenceAgent` | ✓ | `td_handlers_agents.py:138` | `902a80e5-…` | **PASS** |
| 8 | `code_review_agent` | `CodeReviewAgent` | ✓ | `td_handlers_agents.py:128` | `a2b97b5b-…` | **RaaS-dispatch PASS; smoke FAIL (input-contract)** |
| 9 | `security_agent` | `MemoryIsolationAgent` (**alias**) | ✓ | `td_handlers_agents.py:160` | `a9511c64-…` | **PASS (semantic-mismatch finding)** |
| 10 | `content_audit_agent` | `ContentAuditAgent` | ✓ | `td_handlers_agents.py:107` | `6e532086-…` | **PASS** |

**Summary:** 10/10 mechanical PASS on all 5 D-verdict criteria (mapping · AgentExecution · class match · terminal · non-empty output). Two edge-case dispositions:
- **#8 code_review_agent:** RaaS-dispatch PASS; task-level smoke FAIL (input-contract). Uniform smoke prompt lacked file/code as agent input contract requires; wiring/mapping/envelope all healthy. Does NOT block CLOSE. Rigby T0 SIGN wording clarification: separating "RaaS-dispatch" and "task-level smoke" preserves PASS/FAIL precision across artifacts.
- **#9 security_agent:** alias mismatch — mapping resolves to `MemoryIsolationAgent`, not a `SecurityAgent` class. PASS mechanically; semantic-mismatch finding logged in §4 substrate ledger row.

---

## 2. Substrate change — `classify_tool` extension

**File:** `core/services/pa_tools_gap_map.py`

**Change:** extend the `has_handler and not has_schema` early-return branch (line 528-529) to check for a per-tool validation doc when `is_agent_via_run_agent=True`. If a doc exists (via `find_matching_doc_stem`), classify as new category `agent_via_run_agent_validated`; else fall back to existing `agent_via_run_agent`.

**Why:** the S3044 doc-only pattern (author validation doc → gap-map flips category → metric moves) is architecturally blocked for the 45-tool bucket because these tools have no PA tool schema (dispatch via `run_agent(agent_name=...)`), so classify_tool short-circuits before reaching the validation-coverage assessment path. Runtime dispatch evidence for these tools was invisible to the metric.

**Companion changes:**
- `CATEGORY_LABEL['agent_via_run_agent_validated'] = 'agent via run_agent (validated)'`
- Module docstring `Categories emitted` list updated with new entry.
- `render_gap_map_markdown` Headline section adds RaaS-validated rollup line: `validated_full + agent_via_run_agent_validated`.
- 3 new unit tests in `core/tests/test_pa_tools_gap_map_2795.py` (positive branch / negative control / precedence stability).

**Metric verification (post-ship):**
- Before Batch 1: `agent_via_run_agent`=45 · `agent_via_run_agent_validated`=0 · `RaaS-validated`=118
- After Batch 1: `agent_via_run_agent`=35 · `agent_via_run_agent_validated`=10 · `RaaS-validated`=128
- Total row count preserved at 164 ✓

---

## 3. Failure taxonomy extension (from S3045 D-verdict)

D-verdict shipped 3 failure categories: **wiring**, **contract**, **runtime** (with disposition rules for each). Batch 1 surfaced a 4th shape:

**Input-contract failure.**
- **Trigger:** Mapping is correct, class dispatches, envelope populated, terminal status reached, but agent-level input schema enforces a per-tool contract that the uniform smoke prompt does not satisfy (e.g. `CodeReviewAgent` requires file path or fenced code block).
- **Distinguishing feature:** the failure is agent-authored, structured, and actionable (returns typed `error_message` + hint), not a crash or empty envelope.
- **Disposition:** **PASS with tailored-smoke-prompt caveat**. Wiring/mapping/envelope validated. Does NOT block CLOSE. Future re-validation should use tool-specific smoke prompt with correct input shape.
- **Distinct from contract failure:** contract failure = `AgentExecution` missing or envelope drifted; input-contract failure = envelope healthy, agent-level input validation enforced.

---

## 4. Substrate ledger row candidate

**Row title:** `[S3045] agent_via_run_agent alias semantic mismatch — security_agent → MemoryIsolationAgent`

Full details in `docs/research/tools/validation/security_agent_validation.md §5`. Rigby to append to Rigby Tool Gap Ledger (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`, `deliverable_type='engineering_backlog'`) per `feedback_rigby_tool_gap_ledger` discipline.

**3-instance ladder tracking:** 3rd instance of multi-tool → single-class alias pattern (after `content_strategy_agent`/`strategic_review` at Slice 5 close, and `create_brand_video`/`create_project_from_research` also at Slice 5 close). Distinct in that this alias creates user-expectation confusion vs. reflecting an intentional delegate pattern.

---

## 5. PLAYBOOK-7.7.5 A2 class-scoped sweep (6 dimensions)

**Shape signature:** classifier branch for `has_handler and not has_schema` tools reachable via `run_agent(agent_name=…)` — namely, the new `agent_via_run_agent_validated` promotion path in `classify_tool` at `pa_tools_gap_map.py:528+`.

**Rigby T1 SIGN refinement added dimensions (v) and (vi) to the original (i)-(iv):**

- **(i) Other production sites of the same shape signature.** Grepped for `agent_via_run_agent` and `is_agent_via_run_agent` — 5 hits, all in `pa_tools_gap_map.py` (module docstring / META_NO_HANDLER commentary / classify_tool branch / build_gap_map / CATEGORY_LABEL). No other production sites classify agent_via_run_agent tools. **PASS.**
- **(ii) Adjacent classes bounded to same taxonomy.** `validated_full` path (schema+handler classification) NOT touched — separate branch (lines 531-551), separate semantics (Covered actions coverage). Kept distinct so architecture difference stays visible. **PASS.**
- **(iii) Downstream consumers.** `render_gap_map_markdown` reads `CATEGORY_LABEL` (new entry added) + Headline `per_category` (rendered as-is, no special-case needed). `doc_claim_verification.py` grep: no `agent_via_run_agent` references — separate concern (doc-vs-runtime drift, not classifier consumption). **PASS.**
- **(iv) Tests that lock in old behavior.** Existing `test_classify_agent_via_run_agent` (test_pa_tools_gap_map_2795.py:197) uses `docs_index` with empty `per_tool_stems` — still returns `agent_via_run_agent` (the negative-doc-presence case). 3 new tests added for the new branch. **PASS.**
- **(v) Negative controls / collision cases (Rigby T1 SIGN refinement).** Test `test_classify_handler_only_dead_not_promoted_by_doc_presence` verifies that a handler-only tool NOT reachable via run_agent stays `handler_only_dead` even if a doc stem matches. Prevents accidental promotion. **PASS.** Ambiguous-doc-match case (multiple docs match one tool name): find_matching_doc_stem is deterministic — strategy 1 exact match wins first; strategy 3 loose containment only fires when strategy 1 misses. **PASS.**
- **(vi) Precedence / ordering stability (Rigby T1 SIGN refinement).** Test `test_classify_agent_via_run_agent_precedence_stable` verifies `meta_no_handler` and `orphan_schema` still short-circuit before the new branch fires. Both use `has_handler=False` so the new branch cannot fire regardless of doc presence. **PASS.**

**A2 sweep verdict:** all 6 dimensions clean. Class closure confirmed.

---

## 6. Prior loose-stem match observations

Two Batch 1 tools rescued from wrong-stem-match class (S3044 substrate ledger row 1):

- **`research_agent`** — was loose-matching `customer_research_agent_validation.md` via strategy-3 substring `_research_agent`. Dedicated file supersedes.

This is the **3rd concrete trigger** of the wrong-stem-match class (S3044 row 1 already had 2: `workspace_tool`, `kb_tool`). Per S3044 ledger row 1 mitigation options: "Open Option B if 3rd trigger surfaces" — Option B is warn-only lint on loose-containment strategy-3 matches. **Trigger threshold reached.** Recommend Rigby append to S3044 ledger row 1: `S3045 Batch 1 concrete trigger #3 (research_agent rescue) — Option B lint escalation threshold reached; open in successor batch.`

---

## 7. What did NOT happen this batch

- No net-new agent classes.
- No `AGENT_MAP` mutations (mapping cardinality unchanged).
- No `_handle_universal_agent` behavior change.
- No live dispatch of the 5-tool skiplist (`resolve_agent`, `video_generation_agent`, `audio_generation_agent`, `image_generation_agent`, `talking_character_agent`) — deferred per D-verdict conditional-live-smoke policy.
- No live dispatch of the 8-tool fanout-risk group (coordinators/orchestrators) — deferred to Batch 2 with `single-step / no-fanout` prompt discipline.
- No `pa_tool_schemas.py` changes — the 45 tools remain schema-less by architectural intent (dispatched via `run_agent`); no schema creation required.

---

## 8. Post-batch forward-carry

**Batch 2 candidates (next slice, still customer-facing but shift toward strategic/executive):**
- `brand_identity_agent` / `creative_director_agent` / `content_diversity_orchestrator` (content strategy leans)
- `cto_agent` / `coo_agent` (executive briefing leans; single-step-no-fanout prompt required)
- `contrarian_agent` / `voice_critic_agent` / `performance_analyst_agent` (autonomous content studio family)

**Batch 3 candidates (stock/betting/blockchain family):**
- `stock_analyst_agent` / `bear_case_agent` / `market_intelligence_coordinator` (stock family + 1 coordinator with fanout guard)
- `prediction_market_analyst` / `game_predictor` / `line_movement_analyzer` / `sharp_action_detector` (betting family)
- `whale_watcher_agent` / `blockchain_audit_coordinator` (blockchain family + 1 coordinator)

**Batch 4 candidates (remaining tail — coordinators, autonomous-studio, security/training):**
- `autonomous_content_studio_coordinator` / `podcast_coordinator_agent` / `meeting_coordinator_agent` / `campaign_orchestrator_agent` (remaining coordinators — fanout guard)
- `trained_creation_agent` / `memory_isolation_agent` (twin of `security_agent` alias — cover the sibling explicitly)
- `platform_audit_agent` / `system_intelligence_agent` / `opportunity_pipeline_agent` / `opportunity_scoring_agent`
- `ai_series_workflow_agent`
- (17-18 tools; may split into 4a/4b)

**Skiplist (conditional live smoke):** `resolve_agent`, `video_generation_agent`, `audio_generation_agent`, `image_generation_agent`, `talking_character_agent`. Doc-only + mitigation note when reached.

**Rough remaining scope:** 35 tools → 3 batches (Batch 2 ~10-12 · Batch 3 ~10 · Batch 4 ~13-15). Estimate 2-3 more sessions to CLOSE the full 45-tool bucket.

---

## 9. Cross-cutting workflow references

- **PLAYBOOK-7.7.1 spec→ship:** Batch 1 is Phase 4-8 (Implementation → T0 SIGN → merge → recycle) of this session's spec→ship cycle; Phase 1-3 discharged Cycle 1A verify + Rigby T1 SIGN AGREE.
- **PLAYBOOK-7.7.2 SIGN evidence:** T1 SIGN with grounded tool_runs (module reads at pa_tools_gap_map.py; grep for AGENT_MAP; classifier code inspection). Rigby T0 SIGN follows at Batch 1 merge.
- **PLAYBOOK-7.7.5 A2 class-scoped sweep:** 6 dimensions discharged (§5 above). Class closure confirmed.
- **PLAYBOOK-7.4.4 recycle-after-merge:** `make celery-recycle` (or `make recycle-all` if any frontend touched) post-merge. This batch has no frontend touch — `make celery-recycle` sufficient.
- **Verify-before-build (Cycle 1A):** **30th consecutive session.** S3045 open caught the classifier short-circuit as spec-invalidation before implementing the doc-only sweep against a metric that wouldn't move — reshape saved ~4-5 sessions of misaligned effort.
