# Session 2861 — `autopilot_tool.history selected_fields` Projection Shipped

**Date:** 2026-07-21
**HEAD at close:** `54e9d5779`
**PR:** [#3341](https://github.com/clwest/donkey-betz-platform/pull/3341)
**Prior session:** [SESSION_2860](SESSION_2860_DELIVERABLE_TOOL_DELETE_SHIPPED.md)
**Session pin retired at close:** `pa-d982a2e9f84a4381` (labeled `s2861-open`)

---

## TL;DR

Shipped the Chris-selected S2861 slate #1 (S2856 Q5c zoom-out fold, Rigby Tool Gap Ledger #6) as **one PR / one commit**. Adds a `selected_fields` payload param to `autopilot_tool.history` when `include_evidence=true`, so operators can project the returned `evidence` + `result` JSONFields down to specific top-level keys instead of dumping full JSON blobs.

**Fix shape:** additive read-surface change. No migration. Backward-compatible: absent/empty `selected_fields` preserves prior S2856 behavior exactly.

- **Schema** — new `selected_fields: array<string>` on `autopilot_tool`; dot-notation `evidence.<key>` / `result.<key>` only; max 20 paths; ignored unless `include_evidence=true`; response echoes server-accepted list post-validation.
- **Handler** — allowlist tuple `_ALLOWED_PROJECTION_PREFIXES = ('evidence', 'result')` for future extension (Rigby Q5b same-PR fold-mitigation); cap-then-validate; both prefixes projected when set; missing keys silently omitted; non-dict src defensively demoted to `{}`.
- **v1 = Option C** — top-level projection only; nested dicts/lists returned verbatim when top-level key selected (matches cycle-log rows at `ops_autopilot/core.py:353` where `evidence={k:v for k,v in results.items()}` produces deeply nested payloads).
- **13 new pytest cases** (`test_s2861_autopilot_selected_fields.py`); **49/49 pass** across S2856 + S2857 + S2861 in ~198s.
- **Rigby SIGN loop:** pre-code AGREE-WITH-MODS (Q1 F-BLOCKING resolved after write-site verification) → post-code AGREE-TO-SHIP on all 5 F-BLOCKING Qs.

Post-recycle Rigby E2E validated all 3 dispatch shapes end-to-end on the Donkey Betz workspace.

---

## Why this slate

At S2861 open Rigby recommended slate #1 from the 10-candidate list: `selected_fields` for `autopilot_tool.history include_evidence=true`. Rationale: known trigger (Ledger Entry #6, S2850 Django-shell detour to inspect evidence + result), A4 provenance-story leverage (governance/enforcement demos live or die on "show me who triggered / why / what changed"), low-risk operator-surface work, no migration.

Chris ratified. Zoom-out flag from Rigby's Q2: huggingface → SignalCluster drop (Ledger #3) is a strong slate-#2 or S2862 candidate — recorded, not shipped.

---

## What shipped

### 1. Schema addition (`core/services/pa_tool_schemas.py`)

- Extended the `history` action description at line 2957–2963 with a cross-reference: "Pair with `selected_fields=[\"evidence.<key>\", \"result.<key>\"]` to trim the returned JSON to only specific top-level keys."
- Extended the `include_evidence` param description at line 3164–3170 with the same cross-reference on its tail sentence.
- New `selected_fields` param definition at lines 3172–3189:

```python
"selected_fields": {
    "type": "array",
    "items": {"type": "string"},
    "description": (
        "For 'history' action: project the returned `evidence` and `result` "
        "JSON to only the specified top-level keys. Use dot-notation with "
        "`evidence.<key>` or `result.<key>` prefixes (e.g., "
        "[\"evidence.actor_user_id\", \"evidence.trigger\", \"result.reason\", "
        "\"result.cap\"]). Returns the top-level key's value verbatim — "
        "nested dicts/lists are returned whole (v1 does not deep-project). "
        "Missing keys silently omitted; invalid prefixes silently ignored. "
        "Max 20 paths (extras truncated). Ignored unless `include_evidence=true`. "
        "When set, BOTH `evidence` and `result` are projected to their "
        "respective selections (an empty selection for one prefix returns "
        "`{}` for that field). Response echoes the server-applied list "
        "(post-validation, post-cap)."
    ),
},
```

### 2. Handler projection (`core/services/td_handlers_ops.py:2108–2159`)

Cap-then-validate → allowlist-gated projection application:

```python
# S2861 slate #1: selected_fields projects evidence + result JSON
# down to specific top-level keys ...
_ALLOWED_PROJECTION_PREFIXES = ('evidence', 'result')
_MAX_SELECTED_FIELDS = 20
raw_selected = payload.get('selected_fields') or []
if not isinstance(raw_selected, list):
    raw_selected = []
raw_selected = [str(f) for f in raw_selected[:_MAX_SELECTED_FIELDS]]
selected_fields: list = []
projection: dict = {p: [] for p in _ALLOWED_PROJECTION_PREFIXES}
if include_evidence:
    for path in raw_selected:
        prefix, _, key = path.partition('.')
        if prefix in _ALLOWED_PROJECTION_PREFIXES and key:
            projection[prefix].append(key)
            selected_fields.append(path)
```

Projection application in the row-mutation loop:

```python
for a in actions:
    a['created_at'] = a['created_at'].isoformat()
    if include_evidence and selected_fields:
        for prefix in _ALLOWED_PROJECTION_PREFIXES:
            src = a.get(prefix)
            if not isinstance(src, dict):
                a[prefix] = {}
                continue
            a[prefix] = {
                k: src[k] for k in projection[prefix] if k in src
            }
```

Return dict gains a `'selected_fields': selected_fields` key echoing server-accepted paths.

Key hardening choices:

- **Allowlist tuple** at line 2118 — future extension (e.g., `verification_result` JSONField at `models_diagnostic_pipeline.py:569`) is a single-line change per Rigby Q5b fold-mitigation absorbed same-PR.
- **Cap-then-validate** — matches the existing `limit = min(int(payload.get('limit', 20)), 100)` cap-not-error posture at line 2106 for the same handler.
- **Echo post-validation** — `selected_fields` return key only contains paths that passed prefix + non-empty-key validation, absorbing Rigby Q5d1 fold-mitigation same-PR.
- **Non-dict defense** — `isinstance(src, dict)` guard demotes edge-case non-dict values to `{}` rather than crash.
- **Missing-key silent omission** — `if k in src` inside the dict comprehension keeps payload small + API stable across schema drift.

### 3. Tests (`core/tests/test_s2861_autopilot_selected_fields.py` — NEW, 13 cases)

- `test_projects_only_requested_evidence_keys` — evidence-only projection.
- `test_projects_only_requested_result_keys` — result-only projection.
- `test_projects_across_both_prefixes` — evidence + result mixed.
- `test_ignored_when_include_evidence_false` — gate check; evidence + result absent from row when `include_evidence=false`; response `selected_fields: []`.
- `test_missing_path_silently_omitted` — `evidence.does_not_exist` and `result.also_missing` don't crash; still echoed as accepted (validation-passed).
- `test_invalid_prefix_silently_ignored` — `foo.bar`, `verification_result.source`, bare `agent_name` all rejected from echo.
- `test_path_without_dot_silently_ignored` — bare `evidence` / `result` rejected.
- `test_empty_selected_fields_returns_full_json` — `selected_fields=[]` returns full evidence + result unchanged.
- `test_missing_selected_fields_returns_full_json` — absent key returns full evidence + result unchanged.
- `test_max_cap_enforced_at_20_paths` — 25 paths → first 20 accepted.
- `test_non_list_selected_fields_treated_as_no_op` — string payload coerced to no-op projection (Rigby autofill risk).
- `test_response_echoes_server_accepted_fields` — mixed valid+invalid+cap → echo contains only accepted post-validation.
- `test_nested_value_returned_whole` — Option C promise: `evidence.timeout_spike` returns full nested dict verbatim (simulates cycle-log rows at `core.py:353`).

**49/49 tests green** across S2856 + S2857 + S2861 in ~198s locally.

---

## Rigby SIGN loop

### Pre-code design SIGN

- **Turn 1:** 5 grounded `repo_tool` reads on substrate (schema + handler + model + include_evidence definition). Q1 flagged **F-BLOCKING** because Rigby ran out of tool budget before verifying write-site payload shapes (flat vs nested). Q2–Q4 non-blocking agree. Q5 (zoom-out) surfaced 4 sub-concerns: (a) shared helper extraction, (b) hardcoded prefix constrains future extension, (c) Playbook fold-trigger risk, (d) echo semantics + ordering coupling + debuggability.
- **Turn 2:** I verified write-site shapes myself (`budget.py:295–310`, `budget.py:475–508`, `core.py:337–356`) — found mixed flat/nested. Real payloads are NOT always 1-level flat: workspace-scope evidence includes `top_agents` + `top_models` lists of dicts; cycle-log rows include per-policy result dicts (deeply nested); flat scalar rows are majority for workspace_budget_freeze / cap_set / downgrade_set. Revised v1 → **Option C: top-level projection, nested returned whole**. Rigby AGREE-TO-BUILD on all 5 Qs with 2 same-PR fold-mitigations absorbed:
  - **Q5b same-PR:** allowlist tuple `_ALLOWED_PROJECTION_PREFIXES = ('evidence', 'result')` — future extension is single-line.
  - **Q5d1 same-PR:** echo `selected_fields` only what passed validation (not raw autofilled input).

### Post-code diff SIGN

4 grounded `repo_tool.read_file` verifications on the staged hunks:

- **Q1 (projection application, handler 2144–2153):** PASS non-blocking — empty projection→`{}`, non-dict src→`{}`, missing key silently skipped.
- **Q2 (validation loop, handler 2126–2131):** PASS non-blocking — no-dot / invalid prefix / empty key all rejected by `partition('.')` + `if prefix in _ALLOWED and key`.
- **Q3 (schema description accuracy, schema 3171–3187):** PASS non-blocking — all shipped semantics match.
- **Q4 (nested-value-whole test, test file 206–242):** PASS non-blocking — full nested dict equality asserted for both evidence and result.
- **Q5 (zoom-out):** three non-blocking future-trigger folds recorded (see below).

**AGREE-TO-SHIP on all 5 F-BLOCKING Qs.**

### Fold ledger persistence (per PLAYBOOK-6.10.9)

**Absorbed same-PR (evidence in shipped code):**
- **Fold A (Q5b extension-point):** `_ALLOWED_PROJECTION_PREFIXES = ('evidence', 'result')` at `td_handlers_ops.py:2118`. Adding `verification_result` is a one-line tuple extension. Verified via post-code SIGN Q1 confirmation.
- **Fold B (Q5d1 echo semantics):** `selected_fields.append(path)` only inside the `if prefix in _ALLOWED and key` branch at `td_handlers_ops.py:2130`. Echo contains post-validation paths only. Verified via post-code SIGN Q2 confirmation + `test_response_echoes_server_accepted_fields`.

**Future-trigger folds (NOT shipped; watch for second independent trigger):**
- **Fold C (Q5a helper extraction):** If a second tool needs JSONField projection, extract a shared utility like `project_jsonfields(row, selected_paths, allowed_prefixes, cap)`. First trigger observed at S2861. `same_pr_mitigatable=false` (would over-generalize before use pattern known).
- **Fold D (Q5b operator-surface discoverability):** `history` now has 3 opt-in payload knobs (`limit`, `include_evidence`, `selected_fields`). If operator surfaces render schema helptext poorly, advanced params ship "invisible." `same_pr_mitigatable=partially` — cross-references embedded in action + `include_evidence` descriptions do what this PR's scope allows. Full mitigation needs UI-surface work outside this slate.
- **Fold E (Q5c dedupe / normalize):** Duplicates in `selected_fields` are preserved; non-string entries are `str()`-coerced (e.g., `None` → `"None"`). Safe but potentially confusing in echo. First trigger observed at S2861; watch for operator confusion before adding normalization.
- **Fold F (Meta.ordering coupling):** `history` slice `[:limit]` relies on `AutopilotAction.Meta.ordering = ['-created_at']` at `models_diagnostic_pipeline.py:577–583`. Not caused by this PR; documented only. Fold future-trigger if a related handler needs explicit `order_by`.

---

## Post-merge E2E

Local `make recycle-all` post-merge at HEAD `54e9d5779` per PLAYBOOK-7.4.4. Rigby E2E dispatch confirmed 3 shapes on the Donkey Betz workspace:

- **Call 1** — `include_evidence=true, no selected_fields`: 3 rows with full `evidence` + `result` JSONs; `selected_fields: []` echoed.
- **Call 2** — `include_evidence=true, selected_fields=['evidence.actor_user_id', 'evidence.trigger', 'result.reason', 'result.cap']`: 3 rows projected to requested keys only; missing keys silently omitted (workspace_downgrade_cleared row got `result: {}` because it has `{cleared: true}` — no reason/cap); `selected_fields` echoed the 4 accepted paths.
- **Call 3** — `include_evidence=false, selected_fields=['evidence.trigger']`: gate holds — no `evidence` or `result` keys in rows at all; `selected_fields: []` echoed (ignored because `include_evidence=false`).

All 3 shapes match spec exactly.

---

## Not shipped at S2861 close (deferred to S2862 or later)

- Ledger #11 durable non-cascading audit table for deletes (still no compliance/forensic trigger).
- All prior deferred items from S2859/S2858/S2857/S2856/S2861 slate list.
- Fold C helper extraction (needs second trigger).
- Fold D operator-surface discoverability (UI work outside PA slate scope).

---

## Session pin lifecycle

Session pin `pa-d982a2e9f84a4381` (labeled `s2861-open`) retires at S2861 close. Fresh mint required at S2862 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.
