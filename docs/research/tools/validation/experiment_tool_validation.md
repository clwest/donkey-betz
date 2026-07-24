# `experiment_tool` — Validation Report (S2918)

**Tool:** `experiment_tool`
**Schema:** `core/services/pa_tool_schemas.py:4812`
**Handler:** `core/services/td_handlers_gateway.py:1879` (`_handle_experiment`)
**Register site:** `core/services/tool_dispatcher.py:583`
**Session:** S2918 (Slice 4 batch 1 — gateway small-tier mixed pilot: analytics + audit + campaign + experiment)
**HEAD at validation:** `e1a09d8d0` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2918 T0 SIGN AGREE-with-edits — mixed-pilot batch composition ratified with 20+ `repo_tool` receipts; Rigby's initial "probable mutation surface" verdict was walked back after verb-scan showed no `.save()`/`.create(`/`.update(`/`.delete(` in handler body. All 3 actions are pure ORM SELECT.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`experiment_tool` reads A/B test rows from `ABTest` and their variants from `ABTestVariant`. Use it when the operator asks "what A/B tests are running?" / "what were the results of test X?" / "how many experiments hit statistical significance?". It's a **read-only** surface — creating or mutating experiments happens elsewhere (out of scope this tool).

Distinct from `analytics_tool` (behavioral events, not experiment configuration) and from `campaign_tool` (campaign entities, not test variants).

## Covered actions

- `tests` — **in scope this ship** — lists `ABTest` rows ordered by `-created_at`. Supports `status` filter. **User-scoped when `user_id` is set** — filters `ABTest.objects.filter(user_id=user_id)`. Truncates to `limit` (default 20, hard cap 50).
- `results` — **in scope this ship** — requires `test_id`. Returns the test row + all `ABTestVariant` rows ordered by `created_at`. Not user-scoped in this action (fetches by `test_id` globally).
- `stats` — **in scope this ship** — default action; aggregate over all A/B tests (user-scoped if `user_id` set). Returns `total_tests` + `by_status` dict + `by_type` dict.

Default action = `stats` (per `payload.get('action', 'stats')` at handler line 1881). **Note:** default differs from `analytics_tool` / `audit_tool` / `campaign_tool` in this batch (which default to a `list`/`summary` shape). Operator calling `experiment_tool` with no action gets aggregate stats, not a list of tests.

## 3. Schema notes

- **Required:** `action` (enum: `tests` / `results` / `stats`).
- **Optional:** `test_id` (UUID string — required for `results`; ignored otherwise), `status` (string — filters `tests` action only, not `stats`), `limit` (int; default 20, hard cap 50 via `min(int(payload.get('limit', 20)), 50)` at handler line 1882).
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4810-4835`.
- **Authority note:** `tests` and `stats` respect `user_id` (multi-tenant filter applied); `results` does NOT — it fetches by `test_id` globally. Same shape as `campaign_tool.detail`; same post-D6 review candidate under single-user pre-prod context.
- **Decimal handling:** `statistical_significance` and `traffic_percentage` are cast to `float(...)` if truthy, else `None`. Prevents `Decimal` from leaking into JSON.

## 4. Golden-path examples

**Example 1 — aggregate stats (default action):**
```json
{"action": "stats"}
```
Expected envelope: `{"action": "stats", "total_tests": <int>, "by_status": {<status>: <count>, ...}, "by_type": {<test_type>: <count>, ...}}`.

**Example 2 — list running tests:**
```json
{"action": "tests", "status": "running", "limit": 10}
```
Expected envelope: `{"action": "tests", "count": <int ≤ 50>, "tests": [{id, name, test_type, status, primary_metric, start_date, statistical_significance}, ...]}`.

**Example 3 — full test results with variants:**
```json
{"action": "results", "test_id": "<UUID>"}
```
Expected envelope: `{"action": "results", "test": {id, name, test_type, status, hypothesis, primary_metric, conclusion, statistical_significance}, "variants": [{id, name, is_control, traffic_percentage, config}, ...]}`.

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": "Unknown experiment_tool action: <action>"}` at handler line 1952. In-envelope.
- **Handler exception:** any exception is caught at line 1954, logged via `logger.error(..., exc_info=True)`, returns `{"error": <str>}`. No `error_code` — legacy-error envelope (8th instance corroborating post-S2917).
- **`results` missing `test_id`:** returns `{"error": "Provide test_id for results"}` at line 1913. In-envelope.
- **`results` with non-existent `test_id`:** returns `{"error": "ABTest <id> not found"}` at line 1916. In-envelope.
- **Empty result set:** `tests` returns `count: 0` + empty list; `stats` returns `total_tests: 0` + empty dicts. No error.
- **Decimal fields when null:** `statistical_significance` / `traffic_percentage` return `None` (not `0.0`) when unset. Downstream consumers must handle both.
- **`limit` hard cap:** 50. No pagination cursor.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `ABTest.objects.order_by(...)` + `.filter(...)` | `read` | `td_handlers_gateway.py:1889-1895,1914,1940-1942` | ORM SELECT; documented |
| `ABTestVariant.objects.filter(...)` | `read` | `td_handlers_gateway.py:1917` | ORM SELECT; documented |

**Appendix N (Network-Preflight) — N/A.** No network first-hop.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` first-hop.

Both Appendices declared N/A per S2918 T0 SIGN Q2 DISAGREE verdict.

**Note on read-only classification:** Direct read of lines 1879-1956 confirms pure ORM SELECT. No mutation vectors, no §5a deferral needed.

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification appended to the S2918 handoff. Expected shapes documented in §4.

## Related

- **Adjacent tools:** `analytics_tool` / `audit_tool` / `campaign_tool` (same slice batch); `distribution_tool` (rollout mechanics — different concern from A/B configuration).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1); models at `core/models_unified_system.py` (`ABTest`, `ABTestVariant`).
- **Prior ratifications:** S2892 Path B open, S2917 Slice 3 CLOSE (22/22).
- **Ledger rows relevant to this ship:**
  - Legacy-error envelope 8th corroborating instance (post-S2917 corroboration count reaches 8 across the S2918 batch 1 quartet).
  - Multi-tenant leak candidate — `results` action bypasses `user_id` filter. Post-D6 evaluation only.
  - Envelope-key asymmetry across actions (`tests` list vs `test` singular vs `total_tests` scalar) — pluralization variant, not defect. Similar shape to `audit_tool`; if 3rd instance surfaces at Slice 4, worth a "consistent-envelope-key" harness-lint candidate.
