# `orm_inspect_tool` — Validation Report (S2907)

**Tool:** `orm_inspect_tool`
**Schema:** `core/services/pa_tool_schemas.py:400`
**Handler:** `core/services/td_handlers_agents.py:592` (`_handle_orm_inspect`)
**Register site:** `core/services/tool_dispatcher.py:327`
**Session:** S2907 (Path B systematic sweep — Slice 2 batch 3 of `td_handlers_agents`, second accelerated batch post-substrate arc close, first small-actionful all-READ_ONLY stress test per S2906 T0 SIGN Fold A commitment)
**HEAD at validation:** `b02f08016`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (every action in the schema `action` enum exercised via T1a harness).
**Rigby SIGN:** S2907 T1 SIGN (pending) — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Bounded, allowlisted Django ORM row inspection surface. Answers "does this row exist under this filter?", "what fields does this model have?", "how many rows match X, grouped by Y?" Purpose-built at S2866 (Rigby Tool Gap Ledger #3) to close the S2845-class false-negative gap where PA tool surfaces report "no data" but rows exist under a different filter path (140 AI-community SignalCluster rows found via ORM `source_breakdown__has_key='huggingface'` after enum-restricted tool surface returned 0).

**Rigby's read-only fallback for ecosystem verification.** Use when a tool surface returns thin/empty results and you need to confirm at the raw layer whether data is genuinely absent vs surfaced-out via enum/filter/enrichment restrictions. Complements `web_fetch_tool` (external HTTP verify) — this is internal DB verify. Sensitive field-name redaction + JSONField sensitivity policy protect against credential leakage even when the operator asks for a broad projection.

Expected lower drift likelihood on this doc than adjacent batch peers due to recent SIGN + explicit contract at S2866 (Q3+Q6 F-BLOCKING) and S2867 count_by extension (Q1+Q2+Q3+Q6 F-AGREE), but audited with the same rigor as `ml_analysis` and `voice_clone_tool` this batch (per Rigby T0 SIGN §C edit).

## Covered actions

- `list_models` — **in scope this ship** — verified live via T1a harness. Returns `{ok, action, count, models[]}` — enumerates the `_MODEL_POLICIES` allowlist (currently 20+ models across core + spider apps). Each model row carries `name, app_label, sensitive, expensive_text_fields, field_count`.
- `describe_model` — **in scope this ship** — verified via T1a harness error path (requires `model`). Returns `{ok, action, model, sensitive_model, expensive_text_fields, field_count, fields[]}` when `model` is an allowlisted string. Each field carries `name, type, is_json, is_text, sensitive_by_name, is_fk`. Sensitive-by-name flagged per the two-layer S2866 Case 3 rule (composite substrings + word-split match). Not exercised with a real model name in the minimal-safe-args harness profile.
- `get` — **in scope this ship** — verified via T1a harness error path (requires `model` + `pk`). Returns `{ok, action, model, include_json_fields, row}` on hit; `{ok: false, error}` on missing pk. Uses `objects.get(pk=pk_value)`. Sensitive JSONField values excluded by default when the model is flagged `sensitive` (LLMCallLog, AutopilotAction, OpsRun); can be opted in via `include_json_fields=true` at caller risk.
- `filter` — **in scope this ship** — verified via T1a harness error path (requires `model` + `filter_kwargs`). Returns `{ok, action, model, count, rows[]}` with `count` = returned rows (bounded by `limit`, default 20, max 200). Lookup allowlist restricted to `{exact, iexact, isnull, gt, gte, lt, lte, contains, icontains, startswith, istartswith, in, has_key, has_keys}`. `in` list capped at 100. FK traversal blocked beyond single `__` chain. Expensive-text fields reject `contains`/`icontains` per model policy.
- `count_by` — **in scope this ship** — verified via T1a harness error path (requires `model` + `group_by`). Returns `{ok, action, model, group_key, total_matching, group_count, returned, truncated, groups[]}`. Aggregate group-by counts sorted descending by count. Default `limit=50`, max 500. DateTimeField auto-buckets to day via TruncDate. FK fields group on `<field>_id` (matches `_serialize_row` convention). S2867 extension.

## 3. Schema notes

- **Required:** `action` (enum: `list_models, describe_model, get, filter, count_by`).
- **Conditional required (handler-enforced):**
  - `model` for `describe_model, get, filter, count_by` — all four fail-loud when missing.
  - `pk` for `get` — fail-loud when empty.
  - `filter_kwargs` (dict) for `filter` — empty dict allowed (returns unfiltered top-N); non-dict rejected.
  - `group_by` for `count_by` — fail-loud when missing.
- **Optional:** `fields` (list of strings — explicit projection), `include_json_fields` (bool — override sensitivity default), `order_by` (string, `-` prefix for desc, allowlisted to common temporal fields), `limit` (int, default varies by action, max 200 for filter / 500 for count_by).
- **Model allowlist enforced:** models not in `_MODEL_POLICIES` return `{ok: false, error, allowlist}` with the sorted allowlist for discoverability.
- **Lookup allowlist enforced:** filter_kwargs with lookups outside the safe set return `{ok: false, error}` naming the disallowed lookup.
- **Bounded by design (S2866 pre-code SIGN Q3+Q6):** no FK traversal beyond `__` chain, `in` cap at 100, no `.save`/`.update`/`.delete` surface, no order_by beyond allowlisted temporal fields. Docstring at line 592-654 documents the contract explicitly.

## 4. Golden-path examples

**"What models can I inspect?"**

```
orm_inspect_tool  action=list_models
```

**"What fields does SignalCluster have, and which are sensitive?"**

```
orm_inspect_tool  action=describe_model  model=SignalCluster
```

**"Fetch one Deliverable by UUID:"**

```
orm_inspect_tool  action=get  model=Deliverable  pk=<UUID>
```

**"Do SignalCluster rows with huggingface in source_breakdown exist?"** (the canonical S2845 use case)

```
orm_inspect_tool  action=filter  model=SignalCluster
                  filter_kwargs={"source_breakdown__has_key": "huggingface", "signal_count__gte": 3}
                  limit=50
```

**"How many Deliverable rows per status?"**

```
orm_inspect_tool  action=count_by  model=Deliverable  group_by=status  limit=50
```

## 5. Failure / empty-state / pagination notes

- **All error paths return `{ok: false, error, ...}` uniformly** — no `TOOL_EXCEPTION` for validation failures. Handler catches its own errors and shapes the response so the caller can retry with corrected args. This is a departure from the `ValueError`-raise-into-`TOOL_EXCEPTION` pattern used by `pilots_tool`/`gates_tool`/`voice_clone_tool`/`ml_analysis`. Intentional — the tool is specifically designed as a fallback for other tools, so surfaces its own validation failures inline rather than escalating.
- **Missing required arg** — inline `{ok: false, error: "<field> is required for <action>"}` per action. See handler lines 954, 1005, 1019.
- **Model not in allowlist** — returns `{ok: false, error, allowlist}` so operator can retry with an allowed model.
- **Model in allowlist but not resolvable via `apps.get_model`** — returns `{ok: false, error}` naming the failure. Would indicate policy/apps drift, not operator error.
- **Filter lookup not in allowlist** — returns `{ok: false, error}` naming the disallowed lookup.
- **FK traversal beyond `__` chain** — rejected by `_validate_filter_kwargs`.
- **`in` list > 100** — rejected.
- **`expensive_text_fields` with `contains`/`icontains`** — rejected per model policy.
- **`get` with pk that doesn't match a row** — `{ok: false, error: "no <model> row with pk=<value>"}`. `ObjectDoesNotExist` caught inline.
- **`filter` empty result** — `{ok: true, count: 0, rows: []}`. Same shape as populated result.
- **`count_by` truncation signal** — response includes `truncated: bool` + `total_matching` + `group_count` + `returned` so operator can see when the group cap fired.
- **JSONField sensitivity default** — for `sensitive=True` models (LLMCallLog, AutopilotAction, OpsRun), JSONField values excluded from `get`/`filter` projections unless `include_json_fields=true` is explicit.
- **Sensitive field-name redaction (S2866 Case 3 fold)** — two-layer match: composite substrings (`api_key`, `access_key`, `refresh_token`, etc.) match anywhere; word-split matches against `_SENSITIVE_WORDS` set. `total_tokens`/`prompt_tokens` NOT matched (numeric counters); `access_token` IS matched. Recursive redaction inside JSONField values via `_JSON_REDACT_KEYS`.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

- **Mutating actions:** none. Handler docstring explicit: "No .save / .update / .delete surface — construction only." Every branch returns a serialized snapshot; no `objects.create`, `.save`, `.update`, `.delete`, `.get_or_create` calls in the handler.
- **Containment protocol:** N/A — no state modification possible via this tool's dispatch surface.
- **Sensitivity note (per Rigby T0 SIGN §D):** `orm_inspect_tool` is "sensitive read" in the *data exposure* sense (can project sensitive JSONField values when the caller opts in, exposes model shape + row content). That's handled by the S2866 allowlist + sensitive-by-name redaction + JSONField sensitivity policy — NOT by READ_ONLY vs WRITE metadata. Safety class remains READ_ONLY; data-exposure discipline is enforced separately by the policy tables inside the handler.
- **Safety metadata:** `orm_inspect_tool` seeded in `TOOL_DEFAULTS` at S2907 with `default_safety_class='READ_ONLY'`.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness orm_inspect_tool` at HEAD `b02f08016` (2026-07-23):

- **`list_models` (4ms):** `response_shape_keys=['action', 'count', 'models', 'ok']` — `success`. Returns full allowlist enumeration.
- **`describe_model` (3ms):** `response_shape_keys=['error', 'error_code', 'ok']` — inline error envelope (`ok: false`, "model is required for describe_model/get/filter"). Harness classifies as `success` because `status_code=200`; **harness classification drift — see §5 note below.**
- **`get` (4ms):** `response_shape_keys=['error', 'error_code', 'ok']` — inline error envelope. Same classification-drift pattern.
- **`filter` (3ms):** `response_shape_keys=['error', 'error_code', 'ok']` — inline error envelope. Same pattern.
- **`count_by` (2ms):** `response_shape_keys=['error', 'error_code', 'ok']` — inline error envelope. Same pattern.

Artifact: `docs/audits/pa_tools/harness_output/orm_inspect_tool.json`.

**Harness classification drift observed (NEW substrate finding — S2907 first batch to surface this):** the T1a auto-harness's `expected_outcome` classification uses a status_code-only heuristic that misclassifies inline `{ok: false, error, error_code}` envelopes as `success`. `orm_inspect_tool` returns such envelopes at `status_code=200` for validation failures (instead of raising `ValueError` → `TOOL_EXCEPTION` → 500 which is what the other batch peers do). Result: 4/5 actions this ship show `expected_outcome=success` when they were actually validation errors that the operator would need to see. The `response_shape_keys=[error, error_code, ok]` DO signal the actual state — the harness just doesn't consult them for outcome classification. This is an intentional handler design choice (documented in the S2866 docstring at line 592-654), not a defect. See §Related for substrate ledger candidate.

### 6.2 Runtime-not-executed — this ship

- **`describe_model` with a real model name** — not exercised. Would confirm the fields-array shape + sensitive-by-name flag propagation.
- **`get` with a real (model, pk) pair** — not exercised. Would confirm `_serialize_row` + sensitivity redaction behavior end-to-end.
- **`filter` with a real filter_kwargs against a populated model** — not exercised. Would confirm the S2845 use case E2E (the exact scenario the tool was built for).
- **`count_by` with DateTimeField auto-bucket** — not exercised. Would confirm the TruncDate branch fires as designed.
- **`filter` with disallowed lookup** — not exercised in the harness (harness only dispatches minimal-safe-args); would confirm the reject path returns the allowlist inline.
- **Sensitive-model JSONField projection with `include_json_fields=true`** — not exercised. Would confirm the opt-in path bypasses default exclusion.

## 6a. Next batch shape (per Rigby S2907 T0 SIGN zoom-out E)

Per Rigby T0 SIGN zoom-out E (2026-07-23), the S2907 batch composition sustains a **uniform READ_ONLY multi-action** shape (batch 2 was uniform actionless; batch 3 is uniform small-actionful). Repeated uniform-only batches risk three couplings: (1) T1b template v1 gets implicitly optimized for the easy shape; (2) drift-find rate becomes selection-biased curation rather than ecosystem truth; (3) the hard governance muscle for mixed-safety and gated-write tools stays unexercised.

**S2908 commitment (Chris ratified 2026-07-23):** batch 4 MUST break the uniform pattern. Two acceptable shapes:

- **Mixed-tool scoped to READ_ONLY subset:** pick a tool with both READ_ONLY and WRITE actions, cover only the READ_ONLY actions in this doc, document the scoping explicitly in `## Covered actions`. Tests Template v1's mixed-pattern representation without taking write risk.
- **Gated-write dry_run-only:** pick a tool with a dry_run path (e.g., autopilot_tool, security_containment_plan), cover only the dry_run branch. Tests schema/handler gating and metadata correctness without mutations.

Do NOT open S2908 with another uniform-READ_ONLY multi-action batch.

---

## Related

- **Ledger candidates surfaced this ship:**
  - **T1a harness classification drift — status_code-only outcome detection misses `ok: false` inline error envelopes.** `orm_inspect_tool` returns `{ok: false, error, error_code}` at HTTP 200 for validation failures (intentional S2866 design — this tool is a fallback surface, so surfaces its own errors inline rather than escalating). The harness's `expected_outcome=success` classification is misleading for such responses; only the `response_shape_keys=[error, error_code, ok]` signal betrays the actual state. Remediation options: (a) T1a harness inspects response body for `ok: false` and re-classifies to `error_captured`; (b) T1a harness adds a per-tool "response-envelope-shape" hint in metadata; (c) `orm_inspect_tool` converts to `TOOL_EXCEPTION` (would break the "self-contained fallback surface" design intent from S2866 — NOT recommended). Deferred to substrate-arc scope.
  - Handler response envelope shape (`{ok, ...}` vs `{action, ...}`) differs from the rest of the sweep batch. Intentional per S2866 docstring at line 592-654 — flagged here for Rigby T1 SIGN awareness (not a defect; design contract).
- **Adjacent tools:** `web_fetch_tool` (untested — external HTTP verify sibling), `db_health_tool` (untested — DB health / connection-state, distinct from ORM row inspection), `orm_aggregate_tool` (not shipped — S2867 zoom-out Q6 carve-out candidate if count_by v2 items land).
- **Substrate context:** T1b `Template version: v1` sweep variant. Small-actionful stress test of `## Covered actions` handler-trace-evidence claim under 5-action enumeration; also serves as the batch's expected-lower-drift benchmark per Rigby T0 SIGN §C edit (recent SIGN discipline + explicit contract, audited with same rigor).
- **Substrate build history:** S2866 (Rigby Tool Gap Ledger #3, `b5a22ea7`) — inaugural build with pre-code SIGN Q3+Q6 F-BLOCKING drove the policy-dict + allowlist design. S2867 — `count_by` extension via pre-code SIGN Q1+Q2+Q3+Q6 F-AGREE + post-code SIGN Q2+Q5 folds. S2866 Case 3 fold — sensitive-field-name two-layer match after `total_tokens` false-positive.
- **Batch peers:** `ml_analysis`, `voice_clone_tool` (Slice 2 batch 3).
