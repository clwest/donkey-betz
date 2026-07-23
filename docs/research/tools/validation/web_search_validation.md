# `web_search` — Validation Report (S2906)

**Tool:** `web_search`
**Schema:** `core/services/pa_tool_schemas.py:310`
**Handler:** `core/services/td_handlers_agents.py:384` (`_handle_web_search`)
**Register site:** `core/services/tool_dispatcher.py:323`
**Session:** S2906 (Path B systematic sweep — Slice 2 batch 2 of `td_handlers_agents`, first actionless-shape batch post-substrate)
**HEAD at validation:** `e59320017`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (actionless — no schema `action` enum to iterate).
**Rigby SIGN:** S2906 T0 SIGN AGREE-with-edits + S2906 T1 SIGN AGREE (9 verification tool_runs, all A/B/C/D/E sections; zoom-out: "systemic drift trend candidate, not yet substrate-arc trigger") — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Serper-backed web search over the public internet. Answers "what's happening right now about X?" — news, current events, recent releases, sports scores, market movements. Use when the user's question requires information newer than model training cutoff, or when platform-internal data (spiders, agents, DB) can't answer.

Distinct from `web_fetch_tool` (raw HTTP GET/POST — the "what does this specific URL return?" surface) and from `intelligence_tool` with `action=search, source=web` (gateway migration path that back-routes through this handler per `_handle_web_search` docstring). `web_search` is the direct convenience surface for the most common case.

## Covered actions

**This tool is actionless by schema design** — `schema_action_count=0` per T1a harness artifact (`docs/audits/pa_tools/harness_output/web_search.json`), no `action` enum declared in the schema at `pa_tool_schemas.py:315-321`. The dispatch surface is a single implicit "search" call parameterized by `query`.

Therefore `## Covered actions` is intentionally empty. S2906 batch 2 validates **(a)** actionless doc shape under T1b template v1, **(b)** `TOOL_DEFAULTS` READ_ONLY applicability when there is no action enum to iterate, and **(c)** schema-vs-handler drift detection — not action enumeration.

## 3. Schema notes

- **Required:** `query` (string).
- **Optional (declared):** none.
- **Optional (handler-only, undeclared):** `limit` (int) and `num_results` (int, legacy alias). Handler reads both at `td_handlers_agents.py:403` — see §5 drift finding.
- **Handler-side clamp:** `max_results = min(int(raw_max), 10)` — hard ceiling of 10 to bound Serper cost/latency. Default 5 when neither `limit` nor `num_results` supplied.
- **Not declared but hard-coded:** `search_type='text'` at line 409. Handler does not expose `search_type` to callers.

## 4. Golden-path examples

**"What's happening in AI right now?"**

```
web_search  query="latest AI news October 2026"
```

**"Search with explicit result count (via gateway convention):**

```
web_search  query="Palantir earnings"  limit=8
```

**Legacy convention (still supported, undeclared in schema):**

```
web_search  query="Palantir earnings"  num_results=8
```

## 5. Failure / empty-state / pagination notes

- **No pagination** — handler returns a single Serper page bounded by `max_results` (default 5, cap 10). No `has_more/offset` cursor. Not a S2868 Ledger #1 pagination surface.
- **Search failure** — Serper API errors return `{query, results: [], error: '<message>'}`. Handler is fail-open (no exception thrown); the `error` key signals failure to the LLM prompt loop.
- **Success shape** — `{query, results: [...], total_results: <int>, search_methods_used: [...]}`. `total_results` reflects handler-side result count post-clamp, not Serper's total-available claim.
- **No latency measurement in this ship** — T1a harness produced no artifact rows (actionless).

**Drift finding — schema/handler undeclared params:**

- Schema at `pa_tool_schemas.py:315-321` declares only `query` in `properties`. Handler at line 403 reads `limit` and `num_results` from payload — both undeclared. Handler-side clamp to max 10 exists but is invisible from schema.
- **Class:** silent-parameter-expansion. Same class as `get_body_vitals` (this batch) — handler-reads-undeclared-optional-params. Rigby Tool Gap Ledger candidate — see §Related.
- **This ship:** documented as finding; no schema edit (avoid unbounded contract expansion mid-batch). Fix candidate: declare `limit` (with `maximum: 10`) in schema properties; keep `num_results` as legacy alias with a `description` deprecation note.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

- **Mutating actions:** none. Read-only search surface — Serper HTTP call, no local writes.
- **Safety metadata:** `web_search` seeded in `TOOL_DEFAULTS` at S2906 with `default_safety_class='READ_ONLY'`. Applicability=always (no external prerequisite beyond Serper reachability).

## 6. Evidence

### 6.1 T1a harness artifact — this ship

`docs/audits/pa_tools/harness_output/web_search.json` at HEAD `fc5bca145` (harness run 2026-07-23):

```json
{
  "actions": [],
  "harness_version": "v1",
  "schema_action_count": 0,
  "tool_name": "web_search"
}
```

Expected shape for actionless tools — zero rows. `## Covered actions` authoring in this doc depends on schema + handler-trace evidence, not harness rows.

### 6.2 Handler-trace evidence — this ship

Handler at `td_handlers_agents.py:384-424`:

- Line 402: `query = payload.get('query', '')` — required-per-schema, but handler tolerates empty (would result in Serper miss).
- Line 403: `raw_max = payload.get('limit') or payload.get('num_results') or 5` — undeclared-param acceptance.
- Line 405: `max_results = min(int(raw_max), 10)` — silent hard clamp.
- Line 408: `WebSearchTool()` instantiated; `execute(query=query, max_results=max_results, search_type='text')`.
- Lines 411-424: success branch returns `{query, results, total_results, search_methods_used}`; failure branch returns `{query, results: [], error}`.

### 6.3 Runtime-not-executed — this ship

Actionless — no live dispatch was required for S2906 sweep-batch validation. Serper reachability + result-shape have historical E2E via routine use through prior sessions (search visible in Rigby task_runs across S28xx onward).

---

## 6a. Next stress test (S2907 pointer)

Per Rigby S2906 T0 SIGN zoom-out AGREE-with-edits: S2907 sweep batch commits to including a **small-actionful, all-read-only** tool (2-3 actions) to stress-test the handler-trace-evidence-required-for-`## Covered actions`-authoring claim under non-trivial action enumeration. Actionless-shape validation (this batch) proves the trivial case; small-actionful proves the harder case. Combined, S2906+S2907 establish the doc-authoring discipline across both schema classes.

---

## Related

- **Ledger candidates surfaced this ship:**
  - **`web_search` schema undeclared `limit` / `num_results` params** — Rigby Tool Gap Ledger candidate. Same class as `get_body_vitals` (this batch: handler-reads-undeclared-optional-params). Deferred to batch-close observation slate; do not schema-fix this batch to keep the sweep pace clean.
- **Adjacent tools:**
  - `web_fetch_tool` — raw HTTP GET/POST (Rigby Tool Gap Ledger #15). Different surface: verify what a specific URL returns rather than "search the web."
  - `intelligence_tool.action=search, source=web` — gateway migration path; back-routes through `_handle_web_search` per handler docstring. Same clamp + undeclared-param behavior via that route.
- **Substrate context:** part of S2906 4-actionless batch validating the actionless doc shape post-S2905 mixed-safety pattern batch. Batch peers: `get_body_vitals`, `check_resource_budget`, `get_system_alerts`.
- **Prior work:** Serper integration + WebSearchTool predate the systematic sweep; no prior validation doc. First entry into the validated corpus this session.
