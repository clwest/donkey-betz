# `ml_analysis` — Validation Report (S2907)

**Tool:** `ml_analysis`
**Schema:** `core/services/pa_tool_schemas.py:215`
**Handler:** `core/services/td_handlers_agents.py:1711` (`_handle_ml_analysis`)
**Register site:** `core/services/tool_dispatcher.py:398`
**Session:** S2907 (Path B systematic sweep — Slice 2 batch 3 of `td_handlers_agents`, second accelerated batch post-substrate arc close, first small-actionful all-READ_ONLY stress test per S2906 T0 SIGN Fold A commitment)
**HEAD at validation:** `b02f08016`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (every action in the schema `action` enum exercised via T1a harness).
**Rigby SIGN:** S2907 T1 SIGN (pending) — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Read-only surface into MLEngine analytical methods. Answers "is the ML engine healthy, what confidence does this decision pattern carry, are there cross-domain opportunities the ML surface can detect from this market snapshot?" Use when the user asks about ML system health, prediction accuracy, decision-confidence analysis, or wants cross-domain opportunity detection scored by the ML engine.

Distinct from `stock_intelligence_tool` (predictions on stocks, not generic ML) and from `sports_betting_tool` (sports-domain predictions). `ml_analysis` is the read-only inspection surface for MLEngine's analytical primitives — no persisted predictions, no training triggers, no model updates.

## Covered actions

- `status` — **in scope this ship** — verified live via T1a harness. Returns `{action, engine, health}`; `health` is `MLEngine.get_system_health()` snapshot (system availability + core model status). No persistence.
- `decision_pattern` — **in scope this ship** — verified via T1a harness error path (handler is fail-loud on required `data` payload). Handler contract: `MLEngine.analyze_user_decision_pattern(decision_data)` → returns confidence score. Not exercised with real decision data in this sweep — see §5.
- `detect_opportunity` — **in scope this ship** — verified via T1a harness error path (handler is fail-loud on required `data` payload). Handler contract: `MLEngine.detect_cross_domain_opportunity(market_data)` → returns list of opportunity objects (`__dict__`-serialized). Not exercised with real market data in this sweep — see §5.

## 3. Schema notes

- **Required:** `action` (enum: `status, decision_pattern, detect_opportunity`).
- **Optional (schema-declared, handler-ignored):** `model_type` (string). Handler does NOT read this param on any branch. Schema-declared-but-handler-ignored — see §5 drift finding.
- **Undeclared (handler-required, schema-missing):** `data` (dict). Handler at line 1741 + 1753 reads `payload.get('data', {})` for `decision_pattern` + `detect_opportunity`; raises `ValueError("data is required for decision_pattern analysis")` (or the detect_opportunity equivalent) on empty. Schema does NOT declare a `data` property. Silent-parameter-invisibility class — same family as S2906 `get_body_vitals` (undeclared `systems`+`include_details`) and `web_search` (undeclared `limit`+`num_results`).
- **Session 933 note (preserved in handler docstring):** MLEngine has no generic `analyze` method — only these 3 action-mapped read methods.

## 4. Golden-path examples

**"Is the ML engine healthy?"**

```
ml_analysis  action=status
```

**Decision-pattern confidence** (requires undeclared `data`; not schema-dispatchable today):

```
ml_analysis  action=decision_pattern  data={"decision_context": "...", "prior_outcomes": [...]}
```

**Cross-domain opportunity detection** (requires undeclared `data`; not schema-dispatchable today):

```
ml_analysis  action=detect_opportunity  data={"market_snapshot": {...}, "domains": [...]}
```

## 5. Failure / empty-state / pagination notes

- **`decision_pattern` without `data` raises ValueError** — surfaced as `TOOL_EXCEPTION` error envelope (verified via T1a harness). Handler is fail-loud on required-but-schema-missing arg. This is the same class of pattern as gates_tool `detail`-without-`id`.
- **`detect_opportunity` without `data` raises ValueError** — same failure mode as above.
- **Silent schema/handler drift (S2906 Fold B trend candidate — data point #2):** schema declares `model_type` (handler ignores) + handler reads `data` (schema doesn't declare). Two-direction drift for a 3-action tool. Rigby cannot dispatch `decision_pattern` or `detect_opportunity` via function calling today because `data` isn't in the schema — the LLM has no signal to include it. `status` action works cleanly (no required payload beyond `action`).
- **Empty-state on `status`** — `MLEngine.get_system_health()` returns a dict even when no models are loaded; no empty-state edge to surface here.
- **Empty-state on `detect_opportunity`** — handler returns `{count: 0, opportunities: []}` when `MLEngine.detect_cross_domain_opportunity` returns `None` or an empty list.
- **`detect_opportunity` serialization** — handler uses `o.__dict__` on each returned opportunity. If MLEngine ever returns objects with private state or non-serializable attributes, this will surface as a dispatcher-level serialization failure. Not exercised this ship.
- **Unknown action** — handler returns `{action, error, available_actions}` instead of raising. Consistent with schema enum but bypasses the standard `TOOL_EXCEPTION` envelope. Non-blocking discrepancy from `pilots_tool`/`gates_tool` fail-loud convention.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

- **Mutating actions:** none. All 3 actions delegate to MLEngine read methods (`get_system_health`, `analyze_user_decision_pattern`, `detect_cross_domain_opportunity`) that return analysis results without persisting.
- **Containment protocol:** N/A — no state modification possible.
- **Safety metadata:** `ml_analysis` seeded in `TOOL_DEFAULTS` at S2907 with `default_safety_class='READ_ONLY'`.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness ml_analysis` at HEAD `b02f08016` (2026-07-23):

- **`status` (965ms):** `response_shape_keys=['action', 'engine', 'health']` — `success`. Higher latency (~1s) is `MLEngine()` __init__ cost even with `SKIP_NLP_MODELS=1` skipping the DistilBERT load; without the skip, the harness stalls ~5min on the transformers pipeline model download/load.
- **`decision_pattern` (3ms):** `error_captured` — `error_code=TOOL_EXCEPTION`, `msg="data is required for decision_pattern analysis"`. Expected: handler is fail-loud on required `data` arg; harness dispatched with only `{action: 'decision_pattern'}` per minimal-safe-args v1 profile (no `data` because schema doesn't declare it — same silent-parameter-invisibility class flagged in §5).
- **`detect_opportunity` (2ms):** `error_captured` — `error_code=TOOL_EXCEPTION`, `msg="data (market_data) is required for detect_opportunity"`. Same failure mode as decision_pattern.

Artifact: `docs/audits/pa_tools/harness_output/ml_analysis.json`.

**Batch-authoring note (S2907 substrate observation):** the ~5-min stall on the default (NLP-loading) run is a substrate-arc-scope authoring-tax finding — the T1a harness reboots MLEngine per tool invocation which triggers DistilBERT load. Not a defect of `ml_analysis` itself; setting `SKIP_NLP_MODELS=1` in the harness invocation reduces the cost to a single ~1s MLEngine boot. Deferred as a harness-substrate ledger candidate — see §Related.

### 6.2 Runtime-not-executed — this ship

- **`decision_pattern` with real decision data** — not exercised. Would confirm the `{confidence, data}` positive path + surface any MLEngine-side edge cases (empty prior_outcomes, malformed decision_context).
- **`detect_opportunity` with real market data** — not exercised. Would confirm the `opportunities[]` shape + the `__dict__` serialization path.
- **`model_type` param** — not exercised. Schema-declared, handler-ignored; verification would confirm the ignore is silent (no warning, no fallback path).

## 6a. Next batch shape (per Rigby S2907 T0 SIGN zoom-out E)

Per Rigby T0 SIGN zoom-out E (2026-07-23), the S2907 batch composition sustains a **uniform READ_ONLY multi-action** shape (batch 2 was uniform actionless; batch 3 is uniform small-actionful). Repeated uniform-only batches risk three couplings: (1) T1b template v1 gets implicitly optimized for the easy shape; (2) drift-find rate becomes selection-biased curation rather than ecosystem truth; (3) the hard governance muscle for mixed-safety and gated-write tools stays unexercised.

**S2908 commitment (Chris ratified 2026-07-23):** batch 4 MUST break the uniform pattern. Two acceptable shapes:

- **Mixed-tool scoped to READ_ONLY subset:** pick a tool with both READ_ONLY and WRITE actions, cover only the READ_ONLY actions in this doc, document the scoping explicitly in `## Covered actions`. Tests Template v1's mixed-pattern representation without taking write risk.
- **Gated-write dry_run-only:** pick a tool with a dry_run path (e.g., autopilot_tool, security_containment_plan), cover only the dry_run branch. Tests schema/handler gating and metadata correctness without mutations.

Do NOT open S2908 with another uniform-READ_ONLY multi-action batch.

---

## Related

- **Ledger candidates surfaced this ship:**
  - Schema-declared-but-handler-ignored `model_type` param (`pa_tool_schemas.py:229`). Two remediation options — (a) drop from schema if MLEngine won't route on it, (b) wire handler to actually pass `model_type` to MLEngine methods. Deferred.
  - Handler-required-but-schema-missing `data` param for `decision_pattern` + `detect_opportunity`. Same silent-parameter-invisibility class as S2906 `get_body_vitals` / `web_search`. Remediation: extend schema `properties` with a `data: {type: object}` declaration + move to `required: [action, data]` conditional (or accept the fail-loud handler contract as declared behavior). Deferred pending Rigby SIGN direction.
  - **Harness-substrate ledger candidate — MLEngine per-invocation NLP-model load stalls harness by ~5min.** Not a defect of `ml_analysis`; the T1a harness reboots MLEngine per tool invocation which triggers DistilBERT via `transformers.pipeline("sentiment-analysis", ...)`. `SKIP_NLP_MODELS=1` env var (already respected by MLEngine) reduces boot to ~1s. Remediation: either (a) T1a harness sets `SKIP_NLP_MODELS=1` by default when dispatching `ml_analysis`, or (b) MLEngine lazy-loads sentiment_analyzer on first sentiment-scoring call. Deferred to substrate-arc scope.
  - Contributes to S2906 Fold B systemic drift trend candidate — data point #2 this batch (voice_clone_tool marketplace `limit` silent clamp is data point #3). If sustained across batches 4-5, promote to Playbook amendment or dedicated cleanup arc.
- **Adjacent tools:** `stock_intelligence_tool` (validated — stocks-domain predictions), `sports_betting_tool` (validated — sports-domain predictions), `reasoning_engine_tool` (untested, actionless — distinct primitive).
- **Substrate context:** T1b `Template version: v1` sweep variant. Small-actionful stress test of `## Covered actions` handler-trace-evidence claim under non-trivial action enumeration.
- **Batch peers:** `voice_clone_tool`, `orm_inspect_tool` (Slice 2 batch 3).
