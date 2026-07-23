# `get_body_vitals` — Validation Report (S2906)

**Tool:** `get_body_vitals`
**Schema:** `core/services/pa_tool_schemas.py:672`
**Handler:** `core/services/td_handlers_agents.py:4766` (`_handle_body_vitals`)
**Register site:** `core/services/tool_dispatcher.py:413`
**Session:** S2906 (Path B systematic sweep — Slice 2 batch 2 of `td_handlers_agents`, first actionless-shape batch post-substrate)
**HEAD at validation:** `e59320017`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (actionless — no schema `action` enum to iterate).
**Rigby SIGN:** S2906 T0 SIGN AGREE-with-edits (routed pre-authoring, `tool_runs` verified; drift finding deferred to §5 + Ledger per T0 agreement) + S2906 T1 SIGN pending — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Read-only surface over the 9 body-system vitals (HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN). Answers "how healthy is the organism right now?" — health scores, alerts, per-system detail. Use when the user asks about body systems, vitals, organism health, or when a broader "is the platform OK?" answer needs body-system substrate rather than infrastructure or agent metrics.

Distinct from `infra_health_tool` (Railway/DB/Redis probe surface — infrastructure layer) and from `check_resource_budget` (LUNGS-family specialized budget gate — this batch peer). `get_body_vitals` is the general per-system health-score inspection surface.

## Covered actions

**This tool is actionless by schema design** — `schema_action_count=0` per T1a harness artifact (`docs/audits/pa_tools/harness_output/get_body_vitals.json`), no `action` enum declared in the schema at `pa_tool_schemas.py:677-681`. The schema declares an empty `properties` object.

Therefore `## Covered actions` is intentionally empty. S2906 batch 2 validates **(a)** actionless doc shape under T1b template v1, **(b)** `TOOL_DEFAULTS` READ_ONLY applicability when there is no action enum to iterate, and **(c)** schema-vs-handler drift detection — this tool exhibits significant undeclared-param drift documented in §5 below.

## 3. Schema notes

- **Required:** none.
- **Optional (declared):** **none** — schema `properties` is an empty object at `pa_tool_schemas.py:680`.
- **Optional (handler-only, undeclared):** `systems` (list[str], default `['all']`) and `include_details` (bool, default `False`). Handler reads both at `td_handlers_agents.py:4776-4777` — see §5 drift finding.
- **Handler dispatch fork:** if `'all' in systems` → `vitals.get_all_vitals(include_details=...)`; otherwise iterate `systems` list and call `vitals.get_system_vitals(system_name, include_details=...)` per entry.
- **Valid `systems` values (from BodyCoordinator convention):** `HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN`, plus meta-value `all`.

## 4. Golden-path examples

**"How's the platform doing?" (default all-systems view):**

```
get_body_vitals
```

**"Just LUNGS with detail" (undeclared params — handler-accepted):**

```
get_body_vitals  systems=["LUNGS"]  include_details=true
```

**"Two specific systems, summary only":**

```
get_body_vitals  systems=["HEART","BRAIN"]
```

## 5. Failure / empty-state / pagination notes

- **No pagination** — single-shot vitals snapshot; each system entry carries a score + optional detail block.
- **Response shape (default `systems=['all']`):** `{systems_requested: ['all'], vitals: {<all-systems-envelope>}}` where the vitals payload is whatever `body_vitals.get_all_vitals()` returns — typically per-system health scores plus a top-level `alerts` array.
- **Response shape (specific systems):** `{systems_requested: [...list...], vitals: {<system_name>: <vitals_dict>, ...}}` — one key per system requested.
- **Invalid `system_name`** — `body_vitals.get_system_vitals` return depends on the LUNGS substrate implementation; typically returns an empty/absent envelope rather than raising.
- **Silent behavior:** handler tolerates absent/malformed `systems` because `payload.get('systems', ['all'])` defaults to `['all']`; if caller passes `systems=[]` (empty list), the `for` loop yields empty `result = {}` and no error surfaces.
- **No latency measurement in this ship** — T1a harness produced no artifact rows (actionless).

**Drift finding — schema/handler undeclared params (Rigby Tool Gap Ledger candidate):**

- Schema at `pa_tool_schemas.py:677-681` declares empty `properties: {}` — the schema literally exposes zero parameters to the LLM caller.
- Handler at line 4776 reads `systems` (list). Handler at line 4777 reads `include_details` (bool). Neither is discoverable from schema.
- **Real operator impact:** an LLM-authored tool_call following the schema will always call `get_body_vitals` with an empty payload. The `systems` and `include_details` params are dead — they'll never be sent because the caller can't see them.
- **Class:** silent-parameter-invisibility. Distinct from `web_search` (this batch) which declares `query` but hides `limit`/`num_results` — that's silent-param-expansion. `get_body_vitals` hides ALL its optional params. Both belong to the same Rigby Tool Gap Ledger candidate family — see §Related.
- **This ship:** documented as finding, defer to Ledger. NO schema edit this batch per Rigby S2906 T0 SIGN AGREE-with-edits ("could be intentionally permissive/undocumented internal knobs; auto-formalizing expands public contract surface"). Fix candidate for future batch: declare both properties with descriptions + note the LUNGS-substrate 9-system enum for `systems`.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

- **Mutating actions:** none. Read-only vitals inspection — `body_vitals.get_all_vitals` / `get_system_vitals` compute against current BodyCoordinator state, do not persist gate decisions.
- **Safety metadata:** `get_body_vitals` seeded in `TOOL_DEFAULTS` at S2906 with `default_safety_class='READ_ONLY'`. Applicability=always (LUNGS substrate always available; falls back to empty vitals dict on absence).

## 6. Evidence

### 6.1 T1a harness artifact — this ship

`docs/audits/pa_tools/harness_output/get_body_vitals.json` at HEAD `fc5bca145` (harness run 2026-07-23):

```json
{
  "actions": [],
  "harness_version": "v1",
  "schema_action_count": 0,
  "tool_name": "get_body_vitals"
}
```

Expected shape for actionless tools — zero rows. Note: the harness cannot pre-populate a "hidden params" test row from schema alone; the drift only surfaces via handler-trace reading, which is why §5 authoring is where the finding was uncovered.

### 6.2 Handler-trace evidence — this ship

Handler at `td_handlers_agents.py:4766-4794`:

- Line 4774: `from core.services.body_vitals import get_body_vitals_service` — LUNGS substrate service.
- Line 4776: `systems = payload.get('systems', ['all'])` — **undeclared**.
- Line 4777: `include_details = payload.get('include_details', False)` — **undeclared**.
- Lines 4781-4789: fork on `'all' in systems`; loop for per-system when not all.
- Lines 4791-4794: response wraps `systems_requested` + `vitals`.

### 6.3 Runtime-not-executed — this ship

Actionless — no live dispatch was required for S2906 sweep-batch validation. Cross-family reference: sibling tools `check_resource_budget` and `get_system_alerts` (both this batch) also delegate to the same LUNGS `body_vitals` service.

---

## 6a. Next stress test (S2907 pointer)

Per Rigby S2906 T0 SIGN zoom-out AGREE-with-edits: S2907 sweep batch commits to including a **small-actionful, all-read-only** tool (2-3 actions) to stress-test the handler-trace-evidence-required-for-`## Covered actions`-authoring claim under non-trivial action enumeration.

---

## Related

- **Ledger candidates surfaced this ship:**
  - **`get_body_vitals` schema declares empty properties; handler reads `systems` + `include_details`** — Rigby Tool Gap Ledger candidate. Silent-parameter-invisibility class. Related sibling: `web_search` silent-parameter-expansion (this batch). Both are the same "handler-reads-undeclared-optional-params" failure mode; the difference is degree (partial vs full hiding). Deferred to batch-close observation slate per T0 SIGN AGREE-with-edits.
- **Adjacent tools:**
  - `check_resource_budget` (this batch) — LUNGS-family specialized budget gate; reads the same substrate for a specific "am I OK to spend?" question.
  - `get_system_alerts` (this batch) — LUNGS-family alerts read; different slice of `get_all_vitals` return shape.
  - `infra_health_tool` (validated_full, S2894) — infrastructure-layer probes (DB, Redis, Railway); different substrate.
  - `status_snapshot_tool` (validated_full, S2894) — broader system overview; consumes vitals as one of several sections.
- **Substrate context:** part of S2906 4-actionless batch validating the actionless doc shape post-S2905 mixed-safety pattern batch. Batch peers: `check_resource_budget`, `get_system_alerts`, `web_search`.
- **Prior work:** BodyCoordinator + `body_vitals` service predate the systematic sweep; no prior validation doc. First entry into the validated corpus this session.
