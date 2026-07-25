# Session 2956 — Golden Evals Slice 2: ResearchAgent YAML

**Session:** 2956
**Date:** 2026-07-25
**HEAD at open:** `d9f030bb5`
**HEAD at close:** `c8815cd38` (after PR #3553 merge, before close-cascade PR)
**Arc:** Golden Evals (S2954 open, this is arc-slice 2 of an 8-YAML Tier-1 build-out)

---

## Headline

Shipped `evals/tier1/research_agent.yaml` (523 lines, 13 prompts, PR #3553) — second Tier-1 canonical prompt suite. First slice authored under the S2955-frozen `canon_version=1` substrate; validates that the substrate holds cleanly on an agent with a very different shape (open-world research + LLM synthesis + iterative search + evidence-cited output vs SIA's closed-world platform-health with tool-grounded item counts). Rigby T1→T3 SIGN cycle with 6-fold T2 zoom-out — all folds disposed appropriately (1 in-PR, 2 disagreed-with-evidence, 1 deferred future, 2 tracked to arc-close). Chris D-verdict `yes` on ship.

---

## What shipped

### PR #3553 — `feat(s2956): Golden Evals Tier-1 slice 2 — ResearchAgent YAML`

Single new file:

- **`evals/tier1/research_agent.yaml`** — 523 lines, 13 prompts, all 5 fault-injection categories (5 happy + 2 each of tool_timeout / data_unavailable / ambiguous_input / bad_input).

**Grounding (DB-verified via ORM 2026-07-25):**
- 37 30d executions (`owner_agent="ResearchAgent"`, `created_at >= 2026-06-25T00:00:00Z`): 36 completed + 1 failed. Much healthier than SIA's 60% failure rate at S2955.
- 121 all-time executions.
- 26 distinct 30d task strings — rich human-input diversity vs SIA's 1 autonomous prompt.
- Top-frequency prompt (12 of 37, 32.4%): `"Research market trends and industry landscape"` (autonomous / scheduled beat) — covered as `research_happy_02_market_trends_autonomous`.
- Additional real 30d prompts covered:
  - `"Research the latest AI trends"` → `research_happy_01_bare_general`
  - Initiative-scoped with BINDING DIRECTIVE preamble → `research_happy_03_initiative_scoped_binding_directive`
  - `"Pull current web/spider intel on Donkey Betz and likely competitors..."` → `research_happy_04_specific_target_competitive_intel`
- One observed all-time failure mode (Celery 60-min watchdog kill: `"Task timed out after 60 minutes (no heartbeat) - marked as failed by cleanup"`) gets dedicated test: `research_timeout_01_watchdog_kill`.

**Fault-injection grounded in ResearchAgent's dependency graph:**
- `core.tasks.execute_agent_task` (Celery watchdog).
- `core.services.search_strategy_service.generate_query_plan` (iterative-search first call).
- `core.services.search_strategy_service.evaluate_search_results` (round-evaluator).
- `core.services.spider_intelligence.SpiderIntelligenceService.query` (spider DB layer).

**No worker impact** — spec-only YAML. `PLAYBOOK-7.4.4` recycle-after-merge does not apply.

---

## Substrate adherence (canon_version=1, S2955-frozen)

1. **`schema_version: 1` + `canon_version: 1`** at file top.
2. **`canonical_field_mapping`** declares `native` vs `derived` per canon field with named derivation rules prefixed `research_v1_*`:
   - `summary` = native from `AgentResult.message` (accepts either GPT-5.2 synthesis text when >200 chars per `research_agent.py:1082` OR constructed contract-status summary per `research_agent.py:1069-1078`).
   - `evidence_pointers` = derived via `research_v1_evidence_claims_plus_tool_calls` (preferred: `data.evidence_claims` ClaimsPack citation cards; fallback: `tool_calls[*].tool + arguments`).
   - `health_status` = derived via `research_v1_success_and_contract_status` (4-way enum from success + contract.status: RESOLVED→healthy, BLOCKED/UNKNOWN→degraded, success=False→unavailable).
3. **`fault_injection` is effect-based**: `component` (`celery_worker | python_service | db | ...`) + `fault.{type, params}` (`latency | error | bad_payload | watchdog_kill`) with `python.{...}` as backend-adapter appendix.
4. **`one_of` acceptance-criteria capped at ≤2 branches** with mandatory `why` string per branch. Used in 4 prompts: `research_data_unavail_02_spider_db_raises`, `research_ambig_01_underspecified`, `research_ambig_02_delegation_intent`, `research_bad_02_control_characters`.

---

## Rigby SIGN cycle

- **T1 (tool-grounded verification)** — Rigby ran `orm_inspect_tool.count_by` + `filter` on `AgentExecution`. **Verdict: PASS**. All 4 volume claims match DB reality:
  - 30d exec (30d bound) = 37 ✓
  - 30d status = completed:36 + failed:1 ✓
  - all-time = 121 ✓
  - all-time non-empty error_message = 1 (matches expected timeout string) ✓
  - Distinct-count direct query rejected by `orm_inspect_tool` guardrail (expensive text field group-by); best estimate from 37-row full sample = 26 ✓
- **T2 (zoom-out)** — 6 folds surfaced across the 6 requested categories. All disposed:
  - **Fold #1** (one_of cap arc-precedent drift) → **DISAGREE / no drift**. YAML uses ≤2 branches; matches Chris's ratified canon per 00-START S2955 close. SIA's inline comment says ≤3 but its actual usage is ≤2 — doc/comment debt on SIA, not my drift. (Tracked at fold #6b.)
  - **Fold #2** (coverage gap for 12/37 highest-volume task) → **DISAGREE / already covered**. `research_happy_02_market_trends_autonomous` has input verbatim `"Research market trends and industry landscape"` with `context.invocation_source: scheduled_beat` tagging its autonomous origin.
  - **Fold #3** (deterministic web outcomes in AC — conditional ship-blocking) → **DISPOSED via AC scan**. Every AC verified as contract-shape check, not external-artifact requirement (`source_urls_present_in_synthesis` asserts URLs surface without requiring specific URLs; `summary_mentions_at_least_one_competitor_name` accepts any name; `synthesis_cites_evidence_card_ids` targets the internal [E<N>] pattern deterministic from `research_agent.py:869-883`).
  - **Fold #4 + #6a** (non-null vs non-empty `error_message` ambiguity) → **FOLDED same-PR**. Added verifier note at lines 20-25 of the YAML header explaining Django empty-string vs NULL semantic on `AgentExecution.error_message` and directing future S2963 validators to filter on `error_message__gt=''` or `.exclude(error_message='')`.
  - **Fold #5** (`health_status` derivation oversimplifies — UNKNOWN→degraded may over-degrade research runs where uncertainty is expected) → **DEFERRED FUTURE-TRIGGER**. Legit conceptual concern but SIA canon uses the same 4-tier enum — changing it would break `canon_version=1` arc precedent. Filed as arc-level `canon_version=2` discussion for post-arc-close review.
  - **Fold #6b** (Tier-1 canon uniformity — comment-vs-usage mismatches across the suite) → **TRACKED forward** to arc-close review at S2962 when all 8 Tier-1 YAMLs are shipped.
- **T3 (folds-disposed verdict)** — **PASS** on every fold disposition. No further requirements from Rigby to ship.

---

## Chris D-verdict

Ratified `yes` via Chat UI 2026-07-25 (manual relay — Ledger #17 3rd observation of Chat UI relay-gap):
- **Ship** `evals/tier1/research_agent.yaml` as u-d-b PR #3553.

Fresh + specific first-action for S2957 pre-committed: author `evals/tier1/devops_agent.yaml` (slice 3 of 8).

---

## Twin mirrors (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)

- **Content mirror (engineering truth):** `a6fa0fa4-23c9-4959-946c-d471c12d24a1` (`initiative_phase_doc`, `category='governance'`). Ledger #16 re-hit (9th cumulative) — `missing_initiative_id` fired on create; suppressed via `deliverable_tool.clear_diagnostic` (sticky-cleared sentinel).
- **Ratification envelope (governance truth):** `8f98a793-942d-40bb-8639-580295023bbf` (`ratification_record`, `category='governance'`). Diagnostic clean on create — no flags fired.

**Ledger #16 sub-observation (S2956):** Rigby noted that from her surface, `orm_inspect_tool` is read-only — she cannot literally null out diagnostic fields via ORM. The workaround she uses is `deliverable_tool.clear_diagnostic`, which sets a sticky `cleared` sentinel that suppresses re-marking on future updates. The ORM-clear recipe documented in `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic.md` assumes direct Claude ORM access; when routed via Rigby the equivalent is the tool's own clear action. Recipe drift note stands.

---

## Rigby Tool Gap Ledger

- **Ledger #16 (deliverable_tool.create diagnostic-flag on initiative_phase_doc)** — potential re-hit at Mirror 1 create (9th cumulative if triggered). Established ORM-clear recipe applied.
- **Ledger #17 candidate (Chat UI relay gap)** — **3rd observation this session** (S2954 candidate → S2955 2nd → S2956 3rd). Chris ratified via Chat UI; response did not relay back to Claude terminal; Chris relayed manually. Pattern now stable across 3 sessions — **promote from candidate to full Ledger row** at S2957 first opportunity + open design task for Rigby Chat UI response-relay wiring.

---

## Deferred queue additions (from S2956)

- **Fold #5** — `health_status` derivation oversimplifies for open-world research agents (UNKNOWN→degraded may over-degrade). Filed for `canon_version=2` arc-close discussion at S2962.
- **Fold #6b** — Tier-1 canon uniformity review across all 8 YAMLs (comment-vs-usage mismatches, formatting drift) — track for arc-close S2962.
- **`orm_inspect_tool` distinct-count on text fields** — the guardrail rejecting group-by on text fields forced a workaround (return full row sample + client-side dedupe). For agents with >200 30d executions this pattern will not scale. Ledger candidate for a `distinct_values_capped` action on `orm_inspect_tool`.

---

## Post-merge state

- **HEAD:** `c8815cd38`
- **Worker state:** unchanged. No `make celery-recycle` required (spec-only YAML).
- **Gap-map:** unchanged, `100 validated_full / 2 untested` (`agent_capability_drift_tool` + `agent_job_status`, both untested-by-design at ship time).
- **Drift scanner:** unchanged shape (77 active / 92 db / 83 map / 59 enum / 2 suppressed).

---

## For fuller context

- **Arc-open scoping doc:** `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md`
- **Arc-open handoff:** `docs/handoffs/SESSION_2954_GOLDEN_EVALS_ARC_OPEN.md`
- **S2955 slice-1 handoff:** `docs/handoffs/SESSION_2955_GOLDEN_EVALS_SLICE_1_SIA_YAML.md`
- **This session's shipped file:** `evals/tier1/research_agent.yaml`
- **Substrate reference (canon_version=1):** `evals/tier1/system_intelligence_agent.yaml` at HEAD `d2acf9c92`
- **A1 Wedge scoping deliverable (still open):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope:** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
