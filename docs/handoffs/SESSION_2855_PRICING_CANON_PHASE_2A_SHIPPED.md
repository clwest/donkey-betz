---
title: "Session 2855 — Pricing Canonicalization Phase 2A shipped"
session: 2855
date: 2026-07-20
predecessor: SESSION_2854_PRICING_CANON_PHASE_1_SHIPPED.md
status: closed
tags: [session-close, pricing-canonicalization, phase-2a, analytics-plane, display-fallback, embedding-cost]
---

# Session 2855 close — S2855 A1 Pricing Canonicalization Phase 2A shipped

## Ship line

**One code PR merged:** PR #3326 `464985198` — Phase 2A of the pricing canonicalization arc extends S2854's canonical `core/services/pricing_catalog.py` to every remaining display-only estimator site the platform had, plus fixes one real analytics-plane bug and one real display-only bug that were rate-mis-priced pre-Phase-2A.

## Two real correctness fixes (visible in production)

### Fix 1 — `base_agent._track_llm_analytics` model mis-attribution

**Pre-Phase-2A:** every call from `BaseAgent._call_openai` → `_track_llm_analytics` wrote a `CostTracking` row with `service='gpt-5-mini'` hardcoded, irrespective of the actual model. `BaseAgent._call_openai` chooses `gpt-5.2` when the agent has tools and `gpt-5-mini` when it does not (`base_agent.py:2550`) — so every tool-using agent's analytics rollup was silently mis-attributed to `gpt-5-mini` in CostTracking. The rate formula was `(input * 0.003/1000) + (output * 0.012/1000)` = $3/$12 per 1M input/output tokens — matched neither `gpt-5.2` canonical ($1.75/$14) nor `gpt-5-mini` canonical ($0.50/$1.50).

**Post-Phase-2A:** `_call_openai` sets `self._last_llm_model = model` right after computing the model (instance attribute — avoids `_track_llm_analytics` signature change that would break subclass overrides). `_track_llm_analytics` reads a graceful fallback chain: `self._last_llm_model → response.model → 'gpt-5-mini'`. Both the `service` field written to `AdvancedAnalyticsService.track_cost` and the `estimated_cost` value now reflect the actual model + canonical rates.

**Regression witness** (in test suite): `TrackLLMAnalyticsModelAttributionTests.test_pre_phase_2a_wrong_rates_would_have_differed` — asserts the pre-fix formula priced (100/50 tokens) at $0.000900, which matches neither the canonical `gpt-5.2` value ($0.000875) nor the canonical `gpt-5-mini` value ($0.000125).

### Fix 2 — `base_agent._call_openai` accumulated cost display

Same rate formula as Fix 1, used to accumulate `self._accumulated_cost` and return as the `cost` field in the response dict. Pre-Phase-2A this was display-only and did not write any billing row (per S2854 annotation) — but the number surfaced in agent execution summaries. Post-Phase-2A it uses `float(calculate_cost(model, input_tokens, output_tokens, 0))` with the actual model.

## Two display-fallback estimators migrated

### `views_agent_dashboard.py::agent_costs_data` (endpoint `/api/agent-dashboard/costs/`)

**Pre-Phase-2A:** blended rate `cost_per_million_tokens = 0.375` (unclear provenance) used to fabricate `learning_cost` + `collaboration_cost` when `AgentExecution.cost` aggregate was null/zero. Real per-call cost still won when present.

**Post-Phase-2A:** uses `float(calculate_cost('gpt-5-mini', tokens, 0, 0))` as the documented default; adds `estimated: true` boolean to the JSON response so the frontend can label the number. Real `AgentExecution.cost` aggregate still supersedes the fallback (sets `estimated: false`).

### `views_analytics.py::cost_breakdown` (endpoint `/api/v1/analytics/cost-breakdown/`)

**Pre-Phase-2A:** blended rate `(agent_cost['total_tokens'] / 1000) * 0.01` = $10 per 1M (unclear provenance).

**Post-Phase-2A:** same shape — `float(calculate_cost('gpt-5-mini', tokens, 0, 0))` + `estimated: true` + `estimator_model` fields in the `agent_execution` service dict.

**Frontend backward-compat verified:** neither endpoint has any current frontend consumer (grep across `frontend/` finds zero matches for `agent-dashboard/costs`, `cost-breakdown`, `totalCost`, `learningCost`, `collaborationCost`, `costBreakdown` in that context — the one match at `ListenButton.tsx` is for TTS audio, unrelated). Adding new JSON fields is 100% safe.

## Embedding cost — single-source-of-truth preserved (Rigby zoom-out fold)

Rigby's pre-code SIGN zoom-out fold pushed back on my initial lean to add `text-embedding-3-small` to `pricing_catalog.MODEL_PRICES`. Rationale: `EMBEDDING_COSTS` already exists in `core/services/embedding_service.py:37-41` and is the sole source of truth for embedding rates today. Duplicating rates into `pricing_catalog` would create dual sources of truth requiring parallel maintenance forever.

**Post-Phase-2A:** `triage_spider_embeddings.py:135` imports `EMBEDDING_COSTS` + `DEFAULT_MODEL` from `embedding_service` directly. Chat pricing (`pricing_catalog`) and embedding pricing (`embedding_service.EMBEDDING_COSTS`) remain structurally separate. Enforced by `PricingCatalogSeparationTests.test_embedding_models_not_in_chat_pricing_catalog` (Phase 2A guard).

## Docstring reconciliation

- **`LLMCallLog`** (`core/models_llm_routing.py`) — annotated as the **canonical billing plane**; cites 3 verified write sites: `llm_enforcer.py:840`, `agent_llm_router.py:481`, `embedding_service.py:364`
- **`CostTracking`** (`core/models_unified_system.py`) — annotated as the **analytics plane**; cites `base_agent._track_llm_analytics` + non-LLM ops via `AdvancedAnalyticsService.track_cost`
- **Non-overlap invariant** asserted: `base_agent` direct-client path writes CostTracking only, router/enforcer/embedding paths write LLMCallLog only. If a future refactor unifies them, add a provenance dimension to avoid silent double-counting.
- **`pricing_catalog`** module docstring maps both planes + notes embedding rates live in `embedding_service.EMBEDDING_COSTS`

## Working loop validated at S2855

**1 Rigby pre-code design SIGN cycle (3 turns):**
- Task `228223e9…` — initial 4Q + zoom-out; Rigby's prose hedged "no repo_tool access" while her `tool_runs` block showed 8 real `repo_tool` calls. Called out per `feedback_verify_rigby_tool_runs_before_trusting_sign`.
- Task `469e5632…` — follow-up naming the tool_runs mismatch + requesting completion using evidence already gathered. Rigby acknowledged and delivered substantive Q1-Q2 verdicts with line citations.
- Task `c13ef9ca…` — remaining Q3/Q4/zoom-out. Rigby zoom-out fold **reshaped the embedding factoring** (dual-source-of-truth pushback → route through existing `EMBEDDING_COSTS` instead of duplicating). Chris ratified the joint recommendation via terminal yes.

**1 Rigby post-code diff SIGN cycle (1 turn):**
- Task `dae73390…` — 4Q + zoom-out; 8 `repo_tool` verifications; AGREE-TO-SHIP conditional on Q4 frontend grep. Claude closed Q4 independently (no frontend consumers of either endpoint — new JSON fields fully backward-compatible).

**Non-rubber-stamp signals:**
- 23 total `repo_tool` verifications across pre-code + post-code SIGN cycles
- Rigby's zoom-out DISAGREE on embedding factoring caught a real design mistake (dual-source-of-truth) before code was written
- Chris ratified scope via joint Claude+Rigby recommendation per `feedback_claude_rigby_agree_first_chris_yes_no`

## Tests

- **`test_pricing_catalog.py`** — 25/25 pass (17 pre-existing from Phase 1 + 8 new from Phase 2A across 4 new test classes: `PricingCatalogSeparationTests`, `TrackLLMAnalyticsModelAttributionTests`, `DisplayFallbackEstimatorTests`, `TriageSpiderEmbeddingsCostSourceTests`)
- **Broader cost surface** — 88/88 pass across `test_pricing_catalog`, `test_cost_protection_p1`, `test_cost_protection_p2`, `test_cost_thresholds_command`, `test_openai_cost_cached_tokens`

## Post-merge E2E via Rigby

Task `d5c1cc3b…` — verified post-recycle on SHA `464985198`:
1. ✅ `calculate_cost('gpt-5.2', 100, 50)` = `Decimal('0.000875')` (canonical `gpt-5.2` rate stable through Phase 2A)
2. ✅ `calculate_cost('gpt-5-mini', 35, 254)` = `Decimal('0.0003985')` (S2853 downgrade_savings pinning value preserved)
3. ✅ `EMBEDDING_COSTS['text-embedding-3-small'] == Decimal('0.02')` (embedding table untouched, source-of-truth intact)

## Files changed

| File | Lines | What |
|------|-------|------|
| `core/agents/base_agent.py` | +21/-6 | `self._last_llm_model` instance attr; both estimators use `calculate_cost` |
| `core/management/commands/triage_spider_embeddings.py` | +7/-1 | Import `EMBEDDING_COSTS` instead of inline `* 0.02` |
| `core/models_llm_routing.py` | +25/-6 | `LLMCallLog` docstring — billing plane reconciliation |
| `core/models_unified_system.py` | +19/-1 | `CostTracking` docstring — analytics plane reconciliation |
| `core/services/pricing_catalog.py` | +18/-4 | Module docstring — both planes + embedding-lives-elsewhere note |
| `core/tests/test_pricing_catalog.py` | +201/-0 | 8 new tests across 4 classes |
| `core/views_agent_dashboard.py` | +14/-12 | Fallback uses canonical + `estimated: true` flag |
| `core/views_analytics.py` | +14/-6 | Same shape + `estimator_model` field |
| **Total** | **+319/-36** | 8 files |

## Not shipped at S2855 (deferred to S2856 or later)

Phase 2B candidates surfaced during Phase 2A but explicitly deferred:
- **`model_kind: 'chat' \| 'embedding'`** dimension on pricing catalog entries (structural pass — would enable enforcement that embeddings have `output_tokens=0`)
- **Unifying `EMBEDDING_COSTS` + `MODEL_PRICES`** into single table (would resolve the intentional separation Phase 2A preserved; only justified if a real reconciliation need surfaces)
- **`pricing_catalog_version` field** on `LLMCallLog` (schema-level provenance dimension)
- **LLMCallLog↔CostTracking schema-level provenance column** (only justified if the two planes accidentally overlap in a future refactor)

Other slate items still queued from S2855 open:
- Slate #2: `was_downgraded` flag on `LLMCallLog` (migration required)
- Slate #3: `autopilot_tool.history include_evidence` param
- Auto-vs-operator event split for `enforcement_report` (blocked on evidence audit)
- PA-surface E2E for enforcer hot-path
- N+1 in `list_caps` `include_defaults=False` path
- `clear_freeze` post-clear spend context

## Constitutional posture

- **D6 moratorium still in force** — no strategic-discovery arcs opened this session
- **Playbook v0.8.0** governance chain intact
- **PLAYBOOK-7.4.4** honored: `make recycle-all` ran post-merge before docs cascade + handoff
- **Twin canonical representations** per `feedback_twin_deliverable_at_every_ratification`: this handoff + workspace mirror (Rigby to write at next session boundary per `feedback_rigby_writes_workspace_deliverables`)

## Session pin

`pa-dcbe01aef77b48d3` retires at S2855 close. Fresh mint required at S2856 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.
