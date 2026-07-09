# ORM Helper Defaults — Validation Report

**Tool:** ORM helper defaults — the class of tool handlers that wrap Django ORM queries with defaulted filter parameters, where the caller (Rigby's LLM) cannot see which filters were applied. This is the sibling class to Batch C tool 3's "retrieval limits + hidden filters" — one layer down, targeting the filter defaults at the handler-internal helper / queryset-composition boundary, not the retrieval-limit envelope surface.

**Files traced:**
- `core/services/td_autofill_safety.py` — canonical S1227 PR-A defenses (verified at Batch C tool 3 F-RL-5).
- `core/services/td_handlers_agents.py:1680-1770` — `deliverable_tool._apply_common_filters` (F-OH-3 gold standard).
- `core/services/td_handlers_agents.py:1863-1880` — `_id_lookup_qs` (user-scoped ORM helper).
- `core/services/td_handlers_content.py:339-341` — `content_tool.content_review.list` `status='ready'` default.
- `core/services/td_handlers_content.py:1588-1590` — `_handle_initiative.list` `status='ACTIVE'` default.
- `core/services/td_handlers_content.py:740-743` — `_handle_blog_query` — CORRECT pattern (empty default + guard).
- `core/services/td_handlers_agents.py:3284-3379` — voice-profile handlers with implicit `is_active=True`.
- `core/services/td_handlers_content.py:3467-3511` — LearningPattern handlers with implicit `is_active=True`.
- Various `td_handlers_*.py` sites with `is_active=True` implicit filters (see §4.4).

**Session validated:** S2730 (Batch C tool 4 of 5).
**HEAD at validation:** `72ea94a8` (post-Batch-C-tool-3 close on feature branch).
**Reviewer:** Claude (Opus 4.7, 1M context).
**Rigby cross-check:** deferred.
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch C tool 4 of 5). Trace + 2 code patches (F-OH-1 applied_filters + 'all' escape hatch + status_defaulted; F-OH-2 applied_filters + status_defaulted) + 18 regression tests complete; 220 total pass across all Batch A + B + C tools 1-4 validation-2728 files + test_td_autofill_safety.

---

## 1. Intended purpose

Every PA tool handler that composes an ORM queryset makes three implicit decisions:

1. **Base scope**: which model, which manager, which authorization filter.
2. **Applied filters**: which `.filter()` calls fire based on payload params.
3. **Response signal**: whether the response tells the caller which filters ran.

Batch C tool 3 verified that the payload-param `is not None` autofill trap (Session 1227 `has_initiative=False` class) is defended at 7 explicit sites via the `td_autofill_safety` module. **This tool sweeps the next layer**: handlers whose ORM composition **applies filters via defaulted-string parameters** (not autofilled booleans), and whether those filters surface in an `applied_filters` echo.

The MEMORY rule `feedback_llm_autofills_boolean_params_with_false` names the boolean/int autofill class explicitly. The **string-default** class is orthogonal — it's a design decision (the handler author chose a default that fires an active filter), not an autofill trap. But the *symptom* is the same: Rigby calls the tool with the schema-documented default action, gets back a bounded slice of rows, and has no way to know from the response envelope that a filter was applied.

**Gold standard**: `deliverable_tool.list` at `td_handlers_agents.py:1680-1770`:
- Optional filters are truthy-only or explicit-string-only.
- `show_all: true` bypasses the autofill-vulnerable subset.
- Every filter that fires records itself in a local `_applied` dict.
- Response envelope carries `applied_filters: dict(_applied)`.

**Failure mode we're patching**: handlers where the payload-string default fires an ORM filter with no `applied_filters` echo.

## 2. Rigby's belief (per MEMORY + prior tool context)

Load-bearing MEMORY:
- `feedback_llm_autofills_boolean_params_with_false` — Rigby knows to send `show_all=true` on `deliverable_tool.list` when she wants the broadest set. She does NOT know the equivalent pattern for `content_tool.content_review.list` (there isn't one — `status='ready'` is the silent default).
- `feedback_triage_decision_card_pattern` — Rigby uses `applied_filters` in the deliverable_tool workflow when composing her decision cards. She has no equivalent surface for content_tool.

Rigby's mental model at HEAD:
- **`deliverable_tool.list`**: fully-transparent — sees `applied_filters` in every response. VERIFIED-CORRECT.
- **`content_tool.content_review.list`**: **silently filters to `status='ready'`**. Rigby cannot detect `status='completed'` and `status='archived'` rows are excluded unless she explicitly passes `status='all'` (undocumented).
- **`_handle_initiative.list`**: **silently filters to `status='ACTIVE'`**. `status='all'` escape hatch exists but no `applied_filters` echo — Rigby cannot audit which filters fired.
- **Voice-profile / learning-pattern / agent-model list handlers**: **silently filter to `is_active=True`**. No override; no signal.

## 3. Constants / signatures (verbatim capture)

### 3.1 Gold-standard `_apply_common_filters` (deliverable_tool.list)

```python
def _apply_common_filters(qs):
    """Apply category/agent/type/saved/status/date filters."""
    dtype = payload.get('type')
    if dtype:
        qs = qs.filter(deliverable_type=dtype)
        _applied['type'] = dtype
    cat = payload.get('category')
    if cat:
        qs = qs.filter(category__iexact=cat)
        _applied['category'] = cat
    # ... every filter guarded by truthy check, every fire recorded in _applied
```

Response envelope includes:
```python
'applied_filters': dict(_applied),
'show_all': _show_all,
```

### 3.2 F-OH-1 defect: `content_tool.content_review.list`

```python
# td_handlers_content.py:339-341
status_filter = payload.get('status', 'ready')
status_filter = _STATUS_ALIASES.get(status_filter, status_filter)
qs = base_qs.filter(status=status_filter)
```

- Default `'ready'` fires filter regardless of caller intent.
- No `applied_filters` echo in the response.
- No `status='all'` escape hatch (aliased mapping doesn't include 'all').

### 3.3 F-OH-2 defect: `_handle_initiative.list`

```python
# td_handlers_content.py:1588-1590
status_filter = payload.get('status', 'ACTIVE')
if status_filter and status_filter != 'all':
    qs = qs.filter(status=status_filter.upper())
```

- Default `'ACTIVE'` fires filter.
- Has `status='all'` escape hatch — improvement over F-OH-1.
- No `applied_filters` echo.

### 3.4 Correct pattern: `_handle_blog_query`

```python
# td_handlers_content.py:740-743
status_filter = payload.get('status', '')
if status_filter:
    status_filter = _BLOG_STATUS_ALIASES.get(status_filter, status_filter)
    qs = base_qs.filter(status=status_filter)
```

- Default `''` does NOT fire filter.
- Response includes `'status': status_filter or 'pending_review or approved'` describing the effective scope.

## 4. Handler behavior (traced)

### 4.1 `deliverable_tool.list` (F-OH-3 gold standard)

- 12 filter checks in `_apply_common_filters`, all truthy-guarded.
- `has_initiative` uses truthy-only + explicit-string-'false' pattern (S1227 defense).
- `orphans` uses truthy-only.
- `show_all` bypasses the autofill-vulnerable subset.
- `applied_filters` echo in every response.
- **VERIFIED-CORRECT at HEAD.**

### 4.2 `content_tool.content_review.list` (F-OH-1 DEFECT)

- Line 339: silent `status='ready'` default.
- Line 343-346: `content_type` and `category` filters are correctly truthy-guarded.
- Line 349-360: date filters are correctly truthy-guarded.
- No `_applied` dict; no `applied_filters` echo.
- Rigby's mental model: "give me content ready for review" → gets 10 items → does not know that 300 completed items and 50 archived items exist.

### 4.3 `_handle_initiative.list` (F-OH-2 DEFECT — partial)

- Line 1588: silent `status='ACTIVE'` default.
- `status='all'` escape hatch exists (line 1589) — Rigby can broaden the query IF she knows the magic string.
- No `applied_filters` echo.
- Stage / purpose / program / owner filters are truthy-guarded and use `_IGNORED_PURPOSE`/`_IGNORED_PROGRAM` escape sets — those are correct.
- Missing: `_applied` dict + response echo.

### 4.4 Implicit `is_active=True` filter sweep

15+ sites apply `is_active=True` with no override or signal:

| Site | Model | Handler surface |
|---|---|---|
| `td_handlers_agents.py:3292` | VoiceProfile | voice list |
| `td_handlers_agents.py:3312` | VoiceProfile | voice detail |
| `td_handlers_agents.py:3378, 3379` | VoiceProfile | voice stats |
| `td_handlers_codejobs.py:110` | Repo | code jobs |
| `td_handlers_content.py:3435, 3467, 3481, 3499, 3501, 3511` | LearningPattern | patterns list/stats |
| `td_handlers_core.py:392, 1205, 1228, 1252` | Agent | agent lookup |
| `td_handlers_core.py:3800` | User | staff lookup |
| `td_handlers_gateway.py:1285, 1342, 1365, 1367, 1424` | Various | alerts/automations/platforms |

Each is semantically defensible — the caller almost always wants active rows. But **no signal** in the response envelope, and **no override**. Rigby cannot audit archived/deactivated data through these tools.

### 4.5 `_id_lookup_qs` and `_user_qs` (semantic ORM helpers)

- `_id_lookup_qs` at `td_handlers_agents.py:1863-1880`: user-scoped or admin-broadcast lookup. Semantically an authorization filter — should NOT surface in `applied_filters` (would leak `is_pa_or_staff`).
- `_user_qs` at `td_handlers_agents.py:3284-3288`: similar. Authorization scope, not user-visible filter.

**Not defects** — these are correct-by-construction.

## 5. Defaults inventory

| Default | Location | Value | Class |
|---|---|---|---|
| `status_filter` in content_review.list | `td_handlers_content.py:339` | `'ready'` | **F-OH-1 hidden default** |
| `status_filter` in _handle_initiative.list | `td_handlers_content.py:1588` | `'ACTIVE'` | **F-OH-2 hidden default (has escape hatch)** |
| `status_filter` in _handle_blog_query.list | `td_handlers_content.py:740` | `''` (no default filter) | correct |
| Implicit `is_active=True` | 15+ sites | applied unconditionally | **F-OH-5 sweep** |
| `has_initiative` | `td_handlers_agents.py:1746` | truthy-only + string-'false' | F-OH-3 gold standard |

## 6. Hidden filters inventory

See §4 — F-OH-1 (`status='ready'`), F-OH-2 (`status='ACTIVE'`), F-OH-5 sweep (~15 implicit `is_active=True` sites).

## 7. Limits inventory

Not applicable (covered by Batch C tool 3).

## 8. Silent-truncation test

Not applicable (covered by Batch C tool 2).

## 9. Silent-filter test

- **F-OH-1**: `status='ready'` fires silently at `td_handlers_content.py:341`. DEFECT.
- **F-OH-2**: `status='ACTIVE'` fires silently at `td_handlers_content.py:1590`. DEFECT (mitigated by `'all'` escape hatch).
- **F-OH-5**: `is_active=True` fires silently at 15+ sites. DEFECT (deferred sweep).
- **F-OH-3**: `_apply_common_filters` records every applied filter in `_applied` dict, echoes as `applied_filters` in response. VERIFIED-CORRECT.

## 10. Silent-fallback test

Not applicable at this layer.

## 11. Staleness test

Not applicable at this layer.

## 12. Freshness signal

Not applicable at this layer.

## 13. Provenance signal

Not applicable at this layer.

## 14. Authority / workspace assumptions

- `_id_lookup_qs`: user-scoped or admin-broadcast lookup. Correct-by-construction — should NOT surface in `applied_filters`.
- `_user_qs` (voice profile): user-scoped. Same reasoning.
- `is_pa_or_staff` bypass: correctly implemented at `_id_lookup_qs:1871-1879`.

## 15. Runtime dependencies

None at this layer.

## 16. Recoverable failure modes

None specific to this tool.

## 17. STOP-and-report failure modes

None. The whole point is Rigby-visible signal via `applied_filters`.

## 18. Operator-action failure modes

None.

## 19. Existing test coverage

- `core/tests/test_td_autofill_safety.py` — covers helper module.
- `core/tests/test_deliverable_tool_validation_2728.py` — covers `_apply_common_filters` behavior indirectly via F-D-* tests.
- **Zero coverage** for F-OH-1 / F-OH-2 / F-OH-5 silent-filter behavior.

## 20. Change list (code / docs / tests)

**Proposed patches (subject to Chris gate):**

- **F-OH-1 — Add `applied_filters` echo + change default to no-filter on `content_tool.content_review.list`.**
  Options:
  - **(a)** Add `applied_filters` echo only; keep `'ready'` default.
    - Rigby now sees the filter but has to override with a magic string (undocumented).
  - **(b)** Change default to `None`/`''` + add `applied_filters` echo.
    - Rigby-safe by construction. **Behavior change** — old callers that relied on the default now get all statuses.
  - **(c)** Add `applied_filters` echo + `status='all'` escape hatch (matches `_handle_initiative` pattern).
    - Minimum behavior change; preserves the "review defaults to ready" affordance.
  - Recommendation: **(c)** — matches an existing precedent and is minimum-disruption.

- **F-OH-2 — Add `applied_filters` echo to `_handle_initiative.list`.**
  Behavior unchanged; only observability. Rigby already knows `'all'` bypass.
  Recommendation: **patch — echo only, no default change.**

- **F-OH-3 — Verified `deliverable_tool.list` gold standard.**
  No patch. Reinforce MEMORY.

- **F-OH-4 — Verified S1227/S1228 autofill defenses at HEAD.**
  No patch. Already covered by Batch C tool 3 F-RL-5.

- **F-OH-5 — Defer sweep of ~15 implicit `is_active=True` sites.**
  Add to combined batch-close observation list. Retrofit will follow the same shape as F-OH-1/F-OH-2.

- **F-OH-6 — Regression tests.**
  New file `core/tests/test_orm_helper_defaults_validation_2728.py`:
  - F-OH-1: `content_tool.content_review.list` default surfaces in `applied_filters`.
  - F-OH-2: `_handle_initiative.list` default surfaces in `applied_filters`.
  - F-OH-3: source-level guard that `_apply_common_filters` still records into `_applied`.
  - F-OH-4: source-level guard that `td_autofill_safety` module exports still exist (re-verified from F-RL-5).

---

## Findings

### F-OH-1 — `content_tool.content_review.list` `status='ready'` silent default
- **Class:** DEFECT (D2 — silent filter, no signal).
- **Evidence:** `td_handlers_content.py:339-341`.
- **Severity:** MEDIUM.
- **Action:** patch — Chris gate on option (a)/(b)/(c). Recommendation: (c).

### F-OH-2 — `_handle_initiative.list` no `applied_filters` echo
- **Class:** DEFECT (D2 — signal missing).
- **Evidence:** `td_handlers_content.py:1583-1670`. Has `'all'` escape hatch but no echo.
- **Severity:** MEDIUM.
- **Action:** patch — add echo; behavior unchanged.

### F-OH-3 — `_apply_common_filters` gold standard verified
- **Class:** VERIFIED-CORRECT.
- **Evidence:** `td_handlers_agents.py:1680-1770`.
- **Severity:** N/A.
- **Action:** none.

### F-OH-4 — S1227/S1228 autofill defenses verified (reinforce Batch C tool 3 F-RL-5)
- **Class:** VERIFIED-CORRECT.
- **Evidence:** `td_autofill_safety.py` module in production use at 7 sites.
- **Severity:** N/A.
- **Action:** none.

### F-OH-5 — ~15 implicit `is_active=True` sites (sweep)
- **Class:** DEFECT (D2) — sweep.
- **Evidence:** 15+ sites across voice / agent / persona / learning-pattern / alert / automation handlers.
- **Severity:** LOW-MEDIUM.
- **Action:** **defer** to combined batch-close observation list.

### F-OH-6 — Zero coverage of silent-filter behavior
- **Class:** DEFECT (D9).
- **Evidence:** grep of `core/tests/*.py` for `applied_filters` — only deliverable_tool has coverage.
- **Severity:** MEDIUM.
- **Action:** patch — add unit tests.

---

## Verdict (Batch C tool 4 CLOSED)

- Tool status at close: **VERIFIED — DEFECT-PATCHED-VERIFIED.**
- Rigby-safe: **yes** for the 3 audited surfaces. `deliverable_tool.list` verified gold-standard (F-OH-3). `content_tool.content_review.list` (F-OH-1) and `_handle_initiative.list` (F-OH-2) now surface `applied_filters` + `status_defaulted` mirroring the gold standard. F-OH-5's ~15 implicit `is_active=True` sites deferred to combined batch-close per campaign scope.
- Regression tests added: `core/tests/test_orm_helper_defaults_validation_2728.py` — 18 tests (7 for F-OH-1, 4 for F-OH-2, 5 for F-OH-3 gold-standard source-level guards, 2 for F-OH-4 autofill-safety intact).
- Cross-tool regression: 220/220 substantive tests pass across all 14 validation-2728 files + `test_td_autofill_safety.py` (Batches A + B + C tools 1-4). Zero regressions.
- Docs updated: none required (schema descriptions inherit new fields without churn).
- Migration files: none.
- Follow-ups filed: F-OH-5 (implicit `is_active=True` sweep across ~15 sites) → combined batch-close observation list.

### Patches shipped

| Finding | Class | Commit |
|---|---|---|
| F-OH-1 | content_tool.content_review.list applied_filters + 'all' escape + status_defaulted | `497b6f28` |
| F-OH-2 | _handle_initiative.list applied_filters + status_defaulted | `540f71d6` |
| tests | 18 regression tests | `20d5485e` |

### MEMORY rules reinforcement (per campaign plan §12.4)

- `feedback_llm_autofills_boolean_params_with_false`: reinforced VERIFIED status at HEAD via F-OH-3/F-OH-4 (deliverable_tool gold-standard truthy-only + string-'false' + `td_autofill_safety` module still exports 3 canonical helpers). Third verification pass in this batch after Batch C tool 3 F-RL-5 and F-OH-4.
- `feedback_triage_decision_card_pattern`: reinforced with `applied_filters` echo spread to two additional list surfaces — Rigby's triage decision cards now have consistent audit surface across `deliverable_tool.list`, `content_tool.content_review.list`, and `_handle_initiative.list`.

### Design decision: `applied_filters` echo shape

The `applied_filters` dict records **only filters that actually fired**, matching the deliverable_tool gold standard. The legacy `filters_applied` dict (which included all declared filter values regardless of whether they fired) is preserved on both handlers for backward compat — any callers reading the old field see the same shape. New callers should prefer `applied_filters`. The `status_defaulted: bool` marker distinguishes explicit-caller-intent from implicit-default on the load-bearing `status` param at both handlers.
