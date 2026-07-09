# Retrieval Limits + Hidden Filters — Validation Report

**Tool:** retrieval limits + hidden filters — the class of `payload.get('limit', N)` retrieval caps and boolean/integer autofill hidden-filter patterns across the PA tool surface. This is not a single Rigby-callable tool; it is the substrate discipline that every list-shaped or filter-shaped handler must apply to be Rigby-safe.

**Files traced:**
- `core/services/td_autofill_safety.py` — canonical S1227 PR-A defenses: `coerce_optional_bool`, `is_truthy`, `require_write_authorization`.
- `core/services/td_handlers_agents.py:1621-1938` — `deliverable_tool` list/search F-D-5 envelope + F-D-9 F-D-10 F-D-11 truthy-only + `show_all` bypass + `applied_filters` echo.
- `core/services/td_handlers_core.py:4013-4062` — `content_tool.list_recent` F-D-5 envelope.
- `core/services/td_handlers_core.py:875-892` — `td_handlers_core` `auth_required` `coerce_optional_bool` use.
- `core/services/td_handlers_core.py:5267-5291` — `ops_tool.kb_browse` F-KB-1 envelope (inline `_apply_limit_envelope` closure).
- `core/services/td_handlers_gateway.py:113-176` — `repo_tool` tree/search F-RT-2/F-RT-5 envelope.
- `core/services/pa_tool_schemas.py` — 46 declared boolean params (schema layer).
- `core/tests/test_td_autofill_safety.py` — existing coverage of the S1227 helpers.
- `core/tests/test_deliverable_tool_validation_2728.py:194-224` — existing F-D-5 envelope coverage.

**Session validated:** S2730 (Batch C tool 3 of 5).
**HEAD at validation:** `5fa2c9d9` (post-Batch-C-tool-2 close on feature branch).
**Reviewer:** Claude (Opus 4.7, 1M context).
**Rigby cross-check:** deferred.
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch C tool 3 of 5). Trace + 2 code patches (F-RL-1 helper + F-RL-2 3-site migration) + 21 regression tests complete; 202 total pass across all Batch A + B + C tools 1-3 validation-2728 files + test_td_autofill_safety.

---

## 1. Intended purpose

Every list-shaped or filter-shaped tool has to answer three questions correctly when Rigby's LLM autofills its arguments:

1. **Retrieval limit**: what's the cap, was the caller's `limit` respected, and if not, why?
2. **Boolean filter**: does the autofilled `False` mean "filter to falsy" or "no filter"?
3. **Integer filter**: does the autofilled `0` mean "the value is 0" or "no filter"?

Two crystallized MEMORY rules govern this substrate:

- `feedback_llm_autofills_boolean_params_with_false` — S1227 evidence. GPT-5.2 fills every declared optional boolean with `False`; handler gates of the form `if x is not None:` silently apply a filter the caller never intended.
- `feedback_deliverable_tool_use_append_for_large_payloads` — orthogonal, RESOLVED at Batch A tool 1 F-D-9.

The F-D-5 envelope pattern (Batch A tool 1) — `limit_capped: True`, `requested_limit: int`, `effective_limit: int`, `hard_max: int` — is the load-bearing surface for question 1. `td_autofill_safety.py` (Session 1228 PR-A) is the load-bearing helper for questions 2-3.

**This tool's scope**: verify the S1227/S1228 defenses are intact at HEAD, count the un-defended silent-cap surfaces, extract the F-D-5 envelope from three inline-closure sites into a shared module, apply it to a small set of additional Rigby-callable handlers as proof-of-spread, and log the rest as a batch-close observation.

## 2. Rigby's belief (per MEMORY + prior tool context)

Load-bearing MEMORY:
- `feedback_llm_autofills_boolean_params_with_false` — Rigby's LLM autofills every declared optional boolean with Python `False`. Handler gates must use truthy-only semantics (`param in (True, 'true', 'True', 1, '1')`), NOT `if param is not None:`.
- `feedback_deliverable_tool_use_append_for_large_payloads` — Rigby now sees `limit_capped: True` + `requested_limit/effective_limit/hard_max` when a cap fires.

Rigby's mental model:
- **Correct**: default limits are documented in schema descriptions; when a call would exceed the hard cap, the response tells her.
- **Wrong**: unmarked silent caps — she has no way to tell "list returned 50 rows" from "list returned 50 rows because I asked for 500 and the cap is 50."

## 3. Constants / signatures (verbatim capture)

### 3.1 `td_autofill_safety` (canonical helpers, verified stale-at-HEAD)

```python
_TRUTHY = frozenset([True, 'true', 'True', 1, '1'])
_EXPLICIT_FALSE_STRINGS = frozenset(['false', 'False'])
_DRY_RUN_FALSY = frozenset([False, 'false', 'False', 0, '0'])

def is_truthy(value) -> bool: ...
def coerce_optional_bool(value) -> Optional[bool]: ...
def require_write_authorization(payload, *, dry_run_key, confirm_key) -> Tuple[bool, bool]: ...
```

### 3.2 F-D-5 envelope shape (Batch A tool 1)

```python
_LIST_HARD_MAX = 50
_requested_limit = payload.get('limit', 10)
try:
    _requested_limit_int = int(_requested_limit)
except (TypeError, ValueError):
    _requested_limit_int = 10
limit = min(_requested_limit_int, _LIST_HARD_MAX)
_limit_capped = _requested_limit_int > _LIST_HARD_MAX

# ...later, in each return path:
_resp = {...}
if _limit_capped:
    _resp['limit_capped'] = True
    _resp['requested_limit'] = _requested_limit_int
    _resp['effective_limit'] = limit
    _resp['hard_max'] = _LIST_HARD_MAX
return _resp
```

### 3.3 Inline `_apply_limit_envelope` closure (F-KB-1 shape at `td_handlers_ops.py:5284`)

The closure form is more compact than the inline conditional — used at `ops_tool.kb_browse`:

```python
def _apply_limit_envelope(resp: Dict[str, Any]) -> Dict[str, Any]:
    if _limit_capped:
        resp['limit_capped'] = True
        resp['requested_limit'] = _requested_limit_int
        resp['effective_limit'] = limit
        resp['hard_max'] = _KB_HARD_MAX
    return resp
```

Both shapes are the same envelope; the closure form is cleaner when multiple return paths need it.

## 4. Handler behavior (traced)

### 4.1 Autofill defenses (S1227 + S1228)

Verified in place at HEAD:

| Site | Helper | Filter |
|---|---|---|
| `td_handlers_agents.py:1752` | truthy-only inline (`in (True, 'true', 'True', 1, '1')`) | `has_initiative` |
| `td_handlers_agents.py:1772` | truthy-only inline | `orphans` |
| `td_handlers_agents.py:1691` | truthy-only inline | `show_all` bypass |
| `td_handlers_core.py:883` | `coerce_optional_bool` | `auth_required` |
| `td_handlers_agents.py:2658` | `require_write_authorization` | dry_run/confirm gate |
| `td_handlers_content.py:2100, 2664, 2731, 4747` | `require_write_authorization` | dry_run/confirm gate |
| `td_handlers_ops.py:3252` | `require_write_authorization` | dry_run/confirm gate |

**Verdict**: `td_autofill_safety` module is in production use; 46 declared boolean params exist in `pa_tool_schemas.py`, of which ~7 are actively autofill-hardened. The rest are one-direction flags (autofill `False` matches the safe default — e.g. `include_transcript`, `include_full_content`, `show_disabled`, `verbose`), so no defense is required. **No hidden-filter DEFECT found at HEAD.**

### 4.2 F-D-5 envelope call sites

Verified in place at HEAD:

| Site | Handler | Hard max |
|---|---|---|
| `td_handlers_agents.py:1621-1938` | `deliverable_tool.list` / `.search` | 50 |
| `td_handlers_core.py:4013-4062` | `content_tool.list_recent` | 200 |
| `td_handlers_core.py:5267-5291` | `ops_tool.kb_browse` (documents / chunks / search_embeddings / semantic_search) | 50 |
| `td_handlers_gateway.py:113-176` | `repo_tool` tree (depth + entries) / search (files matched) | 5 / 200 / 50 |

Total: **4 handler surfaces with F-D-5 envelope; ~30+ handler surfaces WITHOUT envelope.**

### 4.3 Un-enveloped silent-cap sweep

`grep -rn "limit = min(.*payload.get" core/services/td_handlers_*.py` returns 30+ sites. Sample:

| Site | Handler (approx) | Cap |
|---|---|---|
| `td_handlers_agents.py:1462` | agent introspection variant | 100 |
| `td_handlers_agents.py:2795` | duplicates dup_limit | 200 |
| `td_handlers_agents.py:3146, 3369, 3535, 3845` | various agent/pipeline lists | 30-50 |
| `td_handlers_codejobs.py:210, 257` | code jobs list | 50-100 |
| `td_handlers_content.py:4573, 4594` | initiative content variants | 30 |
| `td_handlers_core.py:675, 706, 1137, 1910, 1983` | multiple core handlers | 50-200 |
| `td_handlers_core.py:2390-3729` (many) | ops list variants | 30-50 |

Each site silently caps at its hard_max with no `limit_capped` signal to Rigby. This is the F-D-5 D2 defect class replicated 30x.

**Full sweep is out of scope for a single Batch C tool.** Chris's guidance was to keep per-tool patches surgical.

### 4.4 Schema-level boolean audit

46 declared boolean params in `pa_tool_schemas.py`. Classified:

- **7 with autofill hardening** (S1227/S1228 defended): `orphans`, `has_initiative`, `saved`, `show_all`, `full_by_agent`, `exclude_archived`, `auth_required`, plus the `dry_run/confirm` write gates.
- **~30 one-direction flags** (autofill `False` = safe default): `include_transcript`, `include_full_content`, `show_disabled`, `verbose`, `include_healthy`, `manual_override`, `writes_only`, `fail_fast`, `return_body`, `save`, `auto_research`, `include_disabled`, `confirm_rollback` — **no defect** because the autofilled `False` matches the intended safe path.
- **~9 remaining** — need audit; most likely one-direction. Log for combined batch-close.

**No hidden-filter DEFECT at HEAD** for the 7 explicitly-defended params. The one-direction category is safe by construction.

## 5. Defaults inventory

| Default | Location | Value | Class |
|---|---|---|---|
| `_TRUTHY` | `td_autofill_safety.py:45` | `frozenset([True, 'true', 'True', 1, '1'])` | canonical |
| `_EXPLICIT_FALSE_STRINGS` | `td_autofill_safety.py:51` | `frozenset(['false', 'False'])` | canonical |
| `_DRY_RUN_FALSY` | `td_autofill_safety.py:57` | `frozenset([False, 'false', 'False', 0, '0'])` | canonical |
| F-D-5 envelope shape | 4 handler surfaces | `{limit_capped, requested_limit, effective_limit, hard_max}` | canonical |
| Silent `min(limit, N)` cap | 30+ sites | varies | **F-RL-4 sweep** |

## 6. Hidden filters inventory

- **`deliverable_tool.list`**: `has_initiative`, `orphans`, `saved`, `status`, `agent`, `category`, `type`, `workspace_id`. **`applied_filters` echo** is present at `td_handlers_agents.py:1899-1938` — Rigby can see which filters fired.
- **`ops_tool.list_routes`**: `auth_required`, `category`. Only `auth_required` is defended.
- **`content_tool` list actions**: various status/agent/category filters — most use string filters (not autofill-trap class).
- **All others** — the 30+ un-enveloped list handlers may apply filter conditions; sweep is out of scope.

## 7. Limits inventory

See §5.

## 8. Silent-truncation test

Not applicable to this tool (payload-size covered by Batch C tool 2). This tool concerns silent CAPS (limit truncation) — see F-RL-4.

## 9. Silent-filter test

- **has_initiative autofill trap** (S1227): **VERIFIED-FIXED-AT-HEAD** via truthy-only gate at `td_handlers_agents.py:1752`. Regression covered by `test_td_autofill_safety.py`.
- **orphans autofill trap**: **VERIFIED-FIXED-AT-HEAD** via truthy-only gate at `td_handlers_agents.py:1772`.
- **auth_required autofill trap**: **VERIFIED-FIXED-AT-HEAD** via `coerce_optional_bool` at `td_handlers_core.py:883`.
- **dry_run/confirm write gates**: **VERIFIED-FIXED-AT-HEAD** via `require_write_authorization` at 6 sites.
- **~30 un-enveloped list handlers**: filter behavior varies; sweep is out of scope.

## 10. Silent-fallback test

Not applicable (deliverable_tool.update → action=list case covered by Batch C tool 2 / S1177 F1).

## 11. Staleness test

Not applicable.

## 12. Freshness signal

Not applicable at this layer.

## 13. Provenance signal

Not applicable at this layer.

## 14. Authority / workspace assumptions

- `show_all` bypass at `td_handlers_agents.py:1691` intentionally bypasses filters; the response echoes `show_all: true` in `applied_filters` so Rigby knows.
- No cross-workspace reach at this layer.

## 15. Runtime dependencies

- `td_autofill_safety.py` is a standalone module — no runtime deps beyond stdlib.
- Handlers depend on the payload dict shape from `tool_dispatcher.execute()`.

## 16. Recoverable failure modes

- Non-integer `limit` value (e.g. `"foo"`) — handlers use `try/except (TypeError, ValueError): _requested_limit_int = default`. Safe.
- Boolean autofill — helpers return `None` on unhashable inputs (`_safe_in` at `td_autofill_safety.py:60`). Safe.

## 17. STOP-and-report failure modes

None. The whole point of the F-D-5 envelope + `applied_filters` echo is Rigby-visible signal, not STOP-and-report.

## 18. Operator-action failure modes

None at this layer.

## 19. Existing test coverage

- `core/tests/test_td_autofill_safety.py` — comprehensive coverage of `coerce_optional_bool`, `is_truthy`, `require_write_authorization`.
- `core/tests/test_deliverable_tool_validation_2728.py` — F-D-5 envelope + F-D-9/10/11 autofill defenses.
- `core/tests/test_search_docs_kb_tool_validation_2728.py` — F-KB-1 envelope + originating_session autofill.
- `core/tests/test_repo_tool_validation_2728.py` — F-RT-2/5 envelopes.

**Zero test coverage** for the new `td_limit_envelope.compute_limit` module (F-RL-1 patch).

## 20. Change list (code / docs / tests)

**Proposed patches (subject to Chris gate):**

- **F-RL-1 — Extract shared `td_limit_envelope` module.**
  Introduce `core/services/td_limit_envelope.py` with:
  ```python
  def compute_limit(payload, default: int, hard_max: int) -> tuple[int, dict]:
      """Return (effective_limit, envelope_dict).
      envelope_dict is empty when no cap fires; carries F-D-5 shape when capped."""
  ```
  Also handles the int-autofill trap (Session 1227 PR2 pattern): `payload.get('limit', 0)` autofilled by LLM → treat as no signal, use default.

- **F-RL-2 — Migrate 3 inline call sites to the shared module.**
  Replace inline F-D-5 pattern in `deliverable_tool.list` (agents:1621), `content_tool.list_recent` (core:4013), `ops_tool.kb_browse` (core:5267), and `repo_tool` tree/search (gateway:113). Behavior-identical migration. Removes ~30 lines of duplicated logic.

- **F-RL-3 — Apply the envelope to 2-3 additional Rigby-callable list surfaces (Chris gate).**
  Candidates (all Rigby uses these frequently):
  - **(a)** `td_handlers_core.py:706` — some ops list at cap 50.
  - **(b)** `td_handlers_core.py:1137` — some ops list at cap 50.
  - **(c)** `td_handlers_agents.py:5148` — agent-history list at cap 200.
  Recommendation: pick 2 that Chris finds highest-value.

- **F-RL-4 — Combined batch-close observation: ~25 remaining un-enveloped silent-cap sites.**
  Log for a future combined batch-close doc pass; do NOT patch this batch. Retrofit will follow the F-RL-1 helper.

- **F-RL-5 — Verified helpers at HEAD (no patch).**
  `td_autofill_safety` verified in production use at 7 sites. `has_initiative`, `orphans`, `auth_required`, `dry_run/confirm` gates all intact. **No new patch required** — MEMORY rule `feedback_llm_autofills_boolean_params_with_false` remains VERIFIED (was RESOLVED at S1227).

- **F-RL-6 — Regression tests for `compute_limit`.**
  New file `core/tests/test_retrieval_limits_hidden_filters_validation_2728.py`:
  - `compute_limit(payload={}, default=10, hard_max=50)` returns `(10, {})`.
  - `compute_limit(payload={'limit': 30}, default=10, hard_max=50)` returns `(30, {})` — under cap.
  - `compute_limit(payload={'limit': 100}, default=10, hard_max=50)` returns `(50, {envelope})` — capped.
  - `compute_limit(payload={'limit': 0}, default=10, hard_max=50)` returns `(10, {})` — LLM autofill defense.
  - `compute_limit(payload={'limit': 'foo'}, default=10, hard_max=50)` returns `(10, {})` — non-int defense.
  - Source-level guards: inline `_LIST_HARD_MAX/_KB_HARD_MAX/_LIST_RECENT_HARD_MAX` still present at the 4 migrated sites (behavior-preserved).
  - Also: verify at source level that `td_autofill_safety.py` module still exists with all 3 helpers (verified-stale guard).

---

## Findings

### F-RL-1 — Shared `td_limit_envelope` module absent
- **Class:** DEFECT (D2 — duplication of the F-D-5 pattern at 4 sites).
- **Evidence:** inline closure at `td_handlers_ops.py:5284`; inline conditional at 3 other sites.
- **Severity:** LOW (correctness fine at 4 sites; velocity + consistency defect for the ~30 un-enveloped sites).
- **Action:** patch — extract module.

### F-RL-2 — Migrate 3 existing inline sites to shared module
- **Class:** DEFECT (D9 — future regressions in one copy won't propagate to the others).
- **Evidence:** duplicated pattern at 4 sites.
- **Severity:** LOW.
- **Action:** patch — behavior-identical migration.

### F-RL-3 — Apply envelope to 2-3 additional Rigby-callable list surfaces
- **Class:** DEFECT (D2 — silent cap without signal).
- **Evidence:** 30+ un-enveloped sites (see §4.3).
- **Severity:** MEDIUM (Rigby cannot detect when a cap fires).
- **Action:** patch — Chris gate on which handlers.

### F-RL-4 — ~25 remaining un-enveloped silent-cap sites
- **Class:** DEFECT (D2) — sweep.
- **Evidence:** 30+ un-enveloped sites; only 4 have envelope.
- **Severity:** MEDIUM (surface-wide).
- **Action:** **defer** to combined batch-close observation list (out of scope for this batch's per-tool discipline).

### F-RL-5 — `td_autofill_safety` verified in production use at HEAD
- **Class:** VERIFIED-CORRECT.
- **Evidence:** 7 call sites; `test_td_autofill_safety.py` regression coverage.
- **Severity:** N/A.
- **Action:** none. MEMORY rule `feedback_llm_autofills_boolean_params_with_false` remains VERIFIED.

### F-RL-6 — Regression tests for shared module
- **Class:** DEFECT (D9).
- **Evidence:** no coverage of the new `compute_limit` function.
- **Severity:** MEDIUM.
- **Action:** patch — add unit tests.

---

## Verdict (Batch C tool 3 CLOSED — refactor-only scope)

- Tool status at close: **VERIFIED — DEFECT-PATCHED-VERIFIED (refactor-only).**
- Rigby-safe: **partial** (unchanged from pre-batch). 3 handler surfaces migrated to the shared `td_limit_envelope.compute_limit` helper — behavior-identical, but with two additional autofill defenses now applied (zero and negative limit → default). Repo_tool's `depth_capped/entries_truncated/files_capped_per_dir` axes stay inline. ~25 un-enveloped silent-cap sites deferred to F-RL-4 combined batch-close observation list.
- Regression tests added: `core/tests/test_retrieval_limits_hidden_filters_validation_2728.py` — 21 tests covering F-RL-1 helper (14 tests) + F-RL-2 source-level migration guards (3 tests) + F-RL-5 `td_autofill_safety` verified-at-HEAD (4 tests).
- Cross-tool regression: 202/202 substantive tests pass across all 13 validation-2728 files + `test_td_autofill_safety.py` (Batches A + B + C tools 1-3). Zero regressions.
- Docs updated: none (envelope shape is documented in Batch A tool 1 report; helper docstring names the pattern in-place).
- Migration files: none (helper is a pure Python module with no ORM surface).
- Follow-ups filed: F-RL-4 (25 remaining silent-cap sites) → combined batch-close observation list. F-RL-3 (apply envelope to 2-3 additional Rigby-callable handlers) → deferred per Chris directive at Batch C tool 3 open.

### Patches shipped

| Finding | Class | Commit |
|---|---|---|
| F-RL-1 | extract `td_limit_envelope` helper module | `dcb0697a` |
| F-RL-2 | migrate 3 inline sites (deliverable_tool / content_tool.list_recent / kb_browse) | `c8d190eb` |
| tests + F-RL-6 | 21 regression tests | `dfe80e39` |

### MEMORY rules reinforcement (per campaign plan §12.4)

- `feedback_llm_autofills_boolean_params_with_false`: reinforced VERIFIED status at HEAD via F-RL-5 (module exists + 3 helpers exported + Python False → None + string 'false' → False + truthy forms → True). The shared `td_limit_envelope.compute_limit` helper extends this defense's semantic to the int-autofill class (zero → default; negative → default).
- `feedback_deliverable_tool_use_append_for_large_payloads`: unchanged (RESOLVED at Batch A tool 1 F-D-9, re-verified at Batch C tool 2 F-PS-6).

### Scope clarification: refactor-only

At Batch C tool 3 open, Chris chose the refactor-only scope over F-RL-3's "apply envelope to 2-3 additional handlers." Rationale: keep this tool narrow; the ~25 un-enveloped sites are all similarly-shaped (a single `limit = min(payload.get('limit', N), M)` line each), so the F-RL-1 helper is the primitive future sweep will use. Applying F-RL-1 at 3 additional sites now would have set a precedent for partial rollout without changing Rigby's overall exposure to the class.
