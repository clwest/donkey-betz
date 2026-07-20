# SESSION 2854 — pricing canonicalization Phase 1 (C+) shipped

**Date:** 2026-07-20
**Predecessor:** SESSION_2853_W2_3_2_DOWNGRADE_SAVINGS_SHIPPED.md
**Branch:** main
**PR shipped:** #3324 → merged as `73ed79281`
**Session pin:** `pa-8e19c6fc3afe4396` (retires at S2854 close)

---

## TL;DR

Collapses the 7-way LLM-token pricing divergence surfaced by S2853 into a
single source of truth at `core/services/pricing_catalog.py` and reroutes
every billing path (`LLMCallLog.cost` write site) through it. Fixes a real
Claude Haiku billing bug (was blended $0.25/1M on total tokens; now correctly
split $0.25 input / $1.25 output). Fixes the enforcer's downgrade path
(was hardcoded to gpt-5.2 rates even on gpt-5-mini downgrades).

Display-only cost estimators (`base_agent`, `views_agent_dashboard`,
`views_analytics`) are intentionally NOT migrated in this pass — they carry
"NOT BILLING — see pricing_catalog.py — do not use for budgets /
enforcement" annotations and their reconciliation is deferred to Phase 2 of
this arc.

---

## Scope decision — Chris B → joint Claude+Rigby C+

Chris's opening lean was full B: single-PR sweep of every pricing site +
LLMCallLog↔CostTracking reconciliation ("we need to make sure everything is
correct"). Rigby's pre-code design SIGN (task `c2cf8bb8`) pushed back with
a coordination-trap argument — canonicalizing pricing without simultaneously
defining what "cost" means per fact table can *increase* confusion. Joint
Claude+Rigby recommendation: split into Phase 1 (this PR) + Phase 2
(separate arc). Chris ratified: "Looks like C+ now then lol."

**Phase 2 stays queued** — migrate display estimators to canonical, reconcile
`LLMCallLog.cost` ↔ `CostTracking.estimated_cost_usd` cost provenance
semantics, fact-table dimension for source-of-truth.

---

## Files shipped in PR #3324 (+522 / -138 across 11 files)

| Path | Change |
|---|---|
| **NEW `core/services/pricing_catalog.py`** (226 lines) | Canonical Python module. Decimal-typed `MODEL_PRICES` with per-model dict (input / output / cached_input where applicable). `get_model_pricing()` + `calculate_cost(model_id, input_tokens, output_tokens, cached_input_tokens=0)` + `estimate_uncached_cost()` back-compat shim. Contract docstring names every downstream billing path. |
| **NEW `core/migrations/0392_s2854_align_llmmodel_prices_to_canonical.py`** (73 lines) | Data migration realigning `LLMModel` rows for gpt-5-mini (0.15/0.60 → 0.50/1.50) + gpt-5.2 (5.00/20.00 → 1.75/14.00). Idempotent `.update()`; backward `RunPython` restores pre-S2854 values. |
| **NEW `core/tests/test_pricing_catalog.py`** (142 lines, 15 test cases) | Rate assertions per model, `calculate_cost` math correctness across cached / uncached / unknown / Haiku split paths, ops_autopilot shim identity check. |
| **`core/services/ops_autopilot/pricing.py` (-78 / +22)** | Reduced to thin re-export shim of canonical. S2853's scoped table deleted. |
| **`core/llm_enforcer.py` (+21 / -14)** | 3 sites migrated: gpt-5.2 inline `_call_openai_v2` (now uses `str(effective_model)` + `cached_input_tokens`); `_calculate_cost` gpt-5-mini helper; `_call_claude` Haiku bug fix. |
| **`core/services/llm_provider_registry.py` (-50 / +14)** | All 5 provider `_calculate_cost` methods (OpenAI/Anthropic/DeepSeek/Together/Gemini) reduced to 3-line canonical delegations. No inline pricing tables remain. |
| **`core/models_llm_routing.py` (+8 / -4)** | `DEFAULT_MODELS` seed rates for gpt-5-mini + gpt-5.2 aligned to canonical (paired with migration 0392 for existing installs). |
| **`core/agents/base_agent.py` (+5 / -2)** | 2 display-only sites (`_call_openai:2593` inline accumulator + `_track_llm_analytics:2825` → CostTracking) annotated. NOT migrated per C+ scope. |
| **`core/views_agent_dashboard.py` (+5 / -2)** | Line 141 annotated. |
| **`core/views_analytics.py` (+3 / -1)** | Line 316 annotated. |
| **`tools/pa_local.sh`** (+1 / -1) | S2854 session pin rotation to `pa-8e19c6fc3afe4396`. |

---

## Correctness deltas visible in production after this ships

### Enforcer path (`llm_enforcer._log_call` → `LLMCallLog.cost` + `CostTracking.estimated_cost_usd`)

1. **Claude Haiku billing bug FIXED.** Pre-S2854: `cost = tokens * 0.00025 / 1000` — single blended rate applied to `(input + output)`. Post: correctly split via canonical, `$0.25/1M input + $1.25/1M output`. For a 500-output-token Haiku call: was $0.000125, now $0.000625 (5× on the output component). Every Claude Haiku call on the enforcer path was silently under-charged.

2. **Downgrade path FIXED.** Pre-S2854 the `_call_openai_v2` cost calc applied `$1.75/$14.00` gpt-5.2 rates regardless of `effective_model`. When S2850 policy-triggered downgrade routed the call to `gpt-5-mini`, `LLMCallLog.cost` was persisted at gpt-5.2 rates — silent OVER-charge on every downgraded call since S2848 W1.5. Post: `calculate_cost(str(effective_model), ...)` correctly prices the downgraded call at gpt-5-mini rates. Downgraded-gpt-5.2 → gpt-5-mini calls now bill ~3.3× less.

3. **gpt-5.2 uncached + cached math unchanged.** Canonical mirrors enforcer inline rates verbatim; existing `LLMCallLog.cost` cost figures for non-downgraded gpt-5.2 calls unchanged.

4. **S2853 downgrade_savings_note caveat SHRINKS.** The "OVER-estimate" caveat noted at S2853 partially resolves: enforcer no longer over-charges downgraded calls in `actual_cost_usd`. Full caveat removal still requires the `was_downgraded` flag on `LLMCallLog` (slate #2, deferred).

### Router path (`agent_llm_router._log_call` → `LLMCallLog.cost` via provider adapter's `response.cost`)

5. **OpenAI provider adapter aligned.** Pre-S2854 the `OpenAIProvider._calculate_cost` inline table had gpt-5-mini at $0.15/$0.60 (3.33× under enforcer) and gpt-5.2 at $5.00/$20.00 (2.86× over enforcer). Post: canonical aligns both. Any router-path gpt-5-mini call now bills more; any router-path gpt-5.2 call now bills less.

6. **Unknown-model fallback normalized.** Pre-S2854 provider adapters had per-provider fallbacks ((1.00, 3.00) OpenAI / (3.00, 15.00) Anthropic / (0.14, 0.28) DeepSeek / (0.80, 0.80) Together / (0.50, 1.50) Gemini). Canonical unifies to (1.00, 3.00). Unknown Anthropic/Together/Gemini models will now bill less than before; unknown DeepSeek models will bill more.

### Display-only paths (unchanged, annotated only)

- `base_agent._call_openai:2593` (in-memory `_accumulated_cost`) — untouched, unchanged rate.
- `base_agent._track_llm_analytics:2825` (writes CostTracking, NOT LLMCallLog) — untouched, unchanged rate.
- `views_agent_dashboard:141` (dashboard blend) — untouched.
- `views_analytics:316` (agent-execution card) — untouched.

All 4 sites now carry `NOT BILLING — see pricing_catalog.py — do not use for budgets / enforcement` comments (Rigby SIGN Q3 refinement, applied verbatim).

---

## Working loop at S2854

- **1 Rigby pre-code design SIGN** (task `c2cf8bb8`) — 4Q + zoom-out. Rigby verified audit via 8 `repo_tool` calls, DISAGREED with Chris's B lean, recommended C+ split. Coordination-trap argument was the strongest push-back seen this arc streak.
- **1 Rigby SIGN on diff** (task `e23ec606`) — 4Q + zoom-out. Rigby verified via 10 `repo_tool` calls: canonical module rates, cached-input fallback semantics, effective_model claim, all 5 provider delegations, migration correctness, grep for remaining old-pattern hardcoded prices. AGREE-TO-SHIP with one refinement (Q3 comment wording). Q4 zoom-out not answered — flagged as minor forward-carry.
- **Pre-merge E2E direct handler invocation** — `workspace_budget_tool.enforcement_report` with `include_downgrade_savings=true` verified identical S2853 numbers ($0.000399 / $0.00301175 / $0.00261275).
- **Post-merge PA E2E via Rigby** — same numbers preserved on merged SHA `73ed79281` workers; canonical module confirmed present via `repo_tool` read.
- Zero rubber-stamps; `tool_runs` verified non-empty on both SIGN dispatches per `feedback_verify_rigby_tool_runs_before_trusting_sign`.
- Chris ratified scope shift after joint Claude+Rigby recommendation per `feedback_claude_rigby_agree_first_chris_yes_no`.

---

## Test coverage

- **15/15 new pytest cases** in `core/tests/test_pricing_catalog.py` — rate assertions, cached-input semantics, Haiku split fix, unknown-model fallback, ops_autopilot shim identity.
- **38/38 pre-existing** cost-related tests (`test_cost_protection_p1.py` + `_p2.py` + `test_openai_cost_cached_tokens.py`) still green — canonical preserves enforcer billing lineage.

---

## Not shipped at S2854 close (deferred to S2855 or later)

- **Phase 2 of pricing canonicalization arc** — migrate display estimators (`base_agent` / `views_agent_dashboard` / `views_analytics`) to canonical, reconcile `LLMCallLog.cost` ↔ `CostTracking.estimated_cost_usd` provenance semantics, fact-table dimension for source-of-truth
- **Slate #2 (was_downgraded flag on LLMCallLog)** — migration required. Would let S2853's `downgrade_savings` distinguish enforcer-forced from natively-mini calls (final removal of OVER-estimate caveat). Deferred from S2854 due to context weight.
- **Slate #3 (autopilot_tool.history include_evidence)** — small (~1 hr). Deferred from S2854 due to context weight.
- All prior S2853-deferred items still queued (auto-vs-operator event split, PA-surface E2E for llm_enforcer hot-path, N+1 in list_caps, clear_freeze spend context)

---

## Forward-carry ledger (S2854 Rigby SIGN observations)

Chris's Q4-not-answered on the SIGN-on-diff dispatch is a first-turn miss on
the zoom-out pattern; Rigby answered Q1/Q2/Q3 substantively. Not blocking
merge, not systemic (S2853 SIGN-on-diff answered zoom-out fully). Watch for
second instance before promoting to Playbook amendment.

Rigby also noted (outside scope) additional pricing constants exist in
`core/management/commands/triage_spider_embeddings.py` (`* 0.02` embedding
estimate) — outside C+ scope but flag for Phase 2 corpus completeness.

---

## References

- **Predecessor:** [SESSION_2853_W2_3_2_DOWNGRADE_SAVINGS_SHIPPED.md](SESSION_2853_W2_3_2_DOWNGRADE_SAVINGS_SHIPPED.md)
- **Canonical module:** `core/services/pricing_catalog.py`
- **Canonical tests:** `core/tests/test_pricing_catalog.py`
- **Data migration:** `core/migrations/0392_s2854_align_llmmodel_prices_to_canonical.py`
- **A4↔A1 constraints (unchanged S2846 baseline):** `00-START-NEXT-SESSION.md` §A4 Constraints
- **Constitutional (unchanged):** `docs/ENGINEERING_PLAYBOOK.md` v0.8.0

For older session history, see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
