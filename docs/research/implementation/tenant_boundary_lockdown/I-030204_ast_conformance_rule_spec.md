---
title: "I-0302 Phase 4 Sub-phase 3 — AST Conformance Rule Spec (Http404-swallow)"
status: active
authority: chris-d-verdict-ratified-2026-07-10-S2749 (Rigby SIGN fallback — provenance in §6)
session_added: 2749
last_updated: 2026-07-10
arc_id: I-0302
arc_phase: Phase 4 Sub-phase 3 (Harness completion + §14 codification)
parent_scoping_doc: docs/research/implementation/tenant_boundary_lockdown/I-0302_scoping.md
phase_1_ledger: docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md
phase_4_architecture: docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md
phase_4_s2748_handoff: docs/handoffs/SESSION_2748_I0302_PHASE_4_SUB_PHASE_0_1_2_COMPLETE.md
head_at_draft: 15fbd436
rigby_design_sign_state: unavailable — LLM-boundary jam across 2 pins on this content (see §6); Rigby to light-SIGN shipped harness post-merge
chris_d_verdicts_resolved:
  - §3 rule spec (6 folds) — ratified S2749 open
  - §4 report-only phase acceptance criteria — ratified S2749 open
  - §5 enforcement-mode flip criteria — ratified S2749 open
  - Batch-fix PR structure — one bundled PR for all 9 discovered sites (see §4 report validation)
constraint: implementation lands in report-only mode first; enforcement flip requires zero-known-violations post batch-fix PR
---

# I-0302 Phase 4 Sub-phase 3 — AST Conformance Rule Spec

Concrete design contract for the Http404-swallow anti-pattern check in `tests/security/test_i0302_p4_ast_conformance.py`.

## §1 Context recap

**§14 threshold met decisively at S2748 close** — 5 sites of the anti-pattern in `core/views_deliverables.py` documented in I-030201 §5.1.b (delete_deliverable, link_deliverable_workspace, record_deliverable_event, unsave_deliverable, templateize_deliverable). Site 5b (get_deliverable) was itself an anonymous-content-leak security bug surfaced by Rigby Q2 Edit 2 during Sub-phase 2 SIGN cycle. A 6th candidate (`export_deliverable:441`) is visible during Sub-phase 3 prep and validates the codification urgency before the report-only sweep even runs.

**Design SIGN status (from S2748 close):**
- F1 Mechanism = **C** — extend Phase 4 harness AST scan module (Rigby confidence 0.80, Claude lean matched)
- F2 Scope = **B** — all Django view files (Rigby 0.74, Claude matched)
- F3 Retroactive sweep = **A** — report-only → batch fix → enforcing (Rigby 0.76, Claude matched)

No Chris ratification was needed on F1/F2/F3 themselves. This doc adds the concrete rule definition that Rigby OFFERED to propose at S2748 close but couldn't deliver at S2749 open due to an LLM-boundary jam on this content (see §6). Claude drafts per path 2 of the memory-rule recovery protocol; Chris D-verdict on §3, §4, §5 before implementation code lands.

## §2 Anti-pattern definition

**Class:** broad `except Exception` handler covering a `try` block that calls `get_object_or_404`, without a preceding `except Http404: raise` handler in the same try's handler list. The `Http404` raised by `get_object_or_404` is caught by `except Exception` before Django's middleware can convert it to a 404 response — the caller receives 500 (with the exception string) instead of 404.

**Fix shape shipped 5x in §5.1.b:**

```python
try:
    ...
    obj = get_object_or_404(Model, id=some_id)
    ...
except Http404:  # <-- required guard, must precede the broad handler
    raise
except Exception as e:
    logger.error(...)
    return JsonResponse({..., 'error': str(e)}, status=500)
```

The guard is exactly `except Http404: raise` and must appear earlier in the handler list than any except that would catch `Http404` (e.g., `except Exception`, `except BaseException`, `except (Http404, OtherError)` — the last of which is a legit catch and NOT a violation).

**Non-violation shapes (must NOT be flagged):**
- `try` block calls `get_object_or_404` and the only except handler is `except Http404: raise` or a bare `raise`.
- `try` block calls `get_object_or_404` but is nested inside an outer try whose outer except is a broad `Exception` handler that DOES have a preceding `except Http404: raise` guard. (The inner try's own handler list is what matters for the inner call.)
- `try` block does NOT call `get_object_or_404` anywhere in its body.
- `get_object_or_404` call is NOT inside any try block (Django's middleware handles the raise directly — no swallow risk).
- `try` block has `except Http404` but no `raise` inside the body (e.g., handler returns a custom 404 JsonResponse). This is intentional handling, not a swallow. Report but do NOT flag as violation.

## §3 Six-fold spec

### §3.1 Violation predicate (structural AST shape)

**Node inspection unit:** `ast.Try` node.

**Violation predicate:**

Given an `ast.Try` node `T`:

1. `T.body` (list of statements) contains at least one `ast.Call` node — anywhere in the subtree of `T.body`, recursively — whose `func` resolves to `get_object_or_404` (see §3.3 for resolution). Call this set `calls_g404 = True/False`.

2. `T.handlers` (list of `ast.ExceptHandler`) contains at least one handler `H` whose `H.type` matches "catches Http404" per this predicate:
   - `H.type is None` (bare `except:`) → matches (catches everything including Http404).
   - `H.type` is `ast.Name(id="Exception")` → matches.
   - `H.type` is `ast.Name(id="BaseException")` → matches.
   - `H.type` is `ast.Attribute` with `attr == "Exception"` (e.g., `builtins.Exception`) → matches.
   - `H.type` is `ast.Tuple` and any element resolves to Exception/BaseException/bare → matches.
   - `H.type` is `ast.Name(id="Http404")` or `ast.Attribute` with `attr == "Http404"` → does NOT match (this is a specific handler).
   - `H.type` is `ast.Tuple` containing `Http404` alongside other types → does NOT match (mixed handler is a legit catch).
   - Any other named exception class → does NOT match.
   
   Call this set `catches_http404 = True/False` (via the broad-handler predicate).

3. `T.handlers` contains a specific `Http404` guard earlier than the broad handler:
   - Iterate handlers in order. If a handler `H_g` with `H_g.type` matching `Http404` (Name or Attribute) appears BEFORE any handler matching `catches_http404` predicate above, the guard is present.
   - Additionally, `H_g.body` must contain either a bare `ast.Raise(exc=None)` OR `ast.Raise(exc=ast.Name(id="Http404"))` OR `ast.Raise(exc=<any Http404-typed re-raise>)`. If `H_g.body` does something else (returns a JsonResponse, logs, etc.) — that's intentional handling; DO NOT count as guard for violation purposes, BUT emit as an INFO row in the report (context signal — see §3.5).
   
   Call this `has_guard = True/False`.

**Violation formula:** `violation = calls_g404 AND catches_http404 AND NOT has_guard`.

**Recursion:** for nested `ast.Try` nodes, inspect each try independently. A nested try's violation is scoped to that try's own handlers — an outer try's handlers do NOT rescue an inner try's violation.

**Structural signals recorded per violation (for report phase — see §3.5):**
- Absolute file path
- Line number of the `ast.Try` node
- Line number of the offending `get_object_or_404` call
- Line number of the broad-handler `ast.ExceptHandler` node
- Fully-qualified enclosing function name (via ancestor walk to nearest `ast.FunctionDef` / `ast.AsyncFunctionDef`; concatenate class names if inside `ast.ClassDef`)
- Source snippet: 3 lines centered on the try node
- Suggested fix hint: `insert 'except Http404: raise' before line <broad-handler-line>`

### §3.2 False-positive avoidance

Ruled out by design:
- **Nested try, inner OK, outer broad** — the outer try does not call `get_object_or_404` in its own body, so the outer try's violation predicate is False; the inner try owns its own handlers. Handled by scoping the `calls_g404` check to the exact `ast.Try.body` subtree (not the enclosing function's whole body).
- **Legit mixed catches** — `except (Http404, ValueError):` catches Http404 explicitly. Handled by the Tuple-with-Http404-element case in §3.1.
- **Intentional custom 404 return** — `except Http404: return JsonResponse({...}, status=404)`. Handled by the `has_guard` refinement in §3.1 — this counts as guard-not-present-for-violation-purposes BUT emits an INFO row so reviewers see it in the report.
- **`get_object_or_404` called via unusual alias** — see §3.3 for detection strategy.

Not ruled out but explicitly ACCEPTED as a false-positive tolerance:
- If `get_object_or_404` is monkeypatched at runtime to not raise Http404 (theoretical — no evidence in the codebase), the rule flags. Acceptable — the pattern of catching Http404 broadly is still worth flagging.
- If a helper function called from within the try raises Http404 internally (e.g., `_fetch_or_404(id)` that calls `get_object_or_404` transitively), the rule does NOT flag the outer try. This is by design — the AST is a local structural check, not a control-flow analysis. Documented as a known scope-limit; endpoint sentinels layer (I-030203 §1.2) covers behavior-level.

### §3.3 `get_object_or_404` detection

Attribute-access, aliased-import, and shortcut re-import all matter. Detection strategy:

**Recognized call forms:**
1. `get_object_or_404(...)` — direct call, likely imported via `from django.shortcuts import get_object_or_404`.
2. `shortcuts.get_object_or_404(...)` — via `from django import shortcuts`.
3. `django.shortcuts.get_object_or_404(...)` — via `import django.shortcuts`.
4. `<alias>(...)` where `<alias>` was imported as `from django.shortcuts import get_object_or_404 as <alias>`.
5. Local rebinding — `g404 = get_object_or_404` then `g404(...)`.

**Implementation strategy:**

Pre-pass over the module's top-level `ast.Import` / `ast.ImportFrom` nodes to build a set of local names that alias `get_object_or_404`:

```python
def _collect_g404_aliases(tree: ast.Module) -> set[str]:
    aliases = {"get_object_or_404"}  # default name
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "django.shortcuts":
            for name in node.names:
                if name.name == "get_object_or_404":
                    aliases.add(name.asname or name.name)
        elif isinstance(node, ast.ImportFrom) and node.module == "django":
            for name in node.names:
                if name.name == "shortcuts":
                    # user calls as shortcuts.get_object_or_404 — handled by attr check
                    pass
    return aliases
```

Also collect `ast.Assign` at module level where the RHS is one of the collected aliases (case 5). Scope: module-level only — function-local rebinding is uncommon and adds complexity; documented as a known scope-limit.

**Call-site match:**
- `ast.Call(func=ast.Name(id=alias))` where `alias in aliases` — matches cases 1, 4, 5.
- `ast.Call(func=ast.Attribute(attr="get_object_or_404"))` — matches cases 2, 3 (attribute chain end matters, chain root can be `shortcuts` or `django.shortcuts` — both flagged; false-positive risk is a caller writing `self.get_object_or_404` for some unrelated reason, which is virtually zero in view code).

### §3.4 Path allowlist heuristic

**Included paths (glob patterns applied to repo root):**
- `core/views*.py` — 209 files per PLATFORM_INVENTORY runtime snapshot
- `core/views/**/*.py` — subdirectory views if any exist
- `apps/*/views*.py` — currently 0 files but forward-compat for the `apps/` split if it ever happens
- `apps/*/views/**/*.py`

**Excluded paths (glob patterns; excluded even if matched above):**
- `**/tests/**` — test files use `get_object_or_404` for fixtures and don't need the guard
- `**/migrations/**` — migrations don't have view semantics
- `**/management/commands/**` — management commands run outside the request/response cycle
- `**/__pycache__/**`
- Any file under `.venv/`, `venv/`, `env/`, `site-packages/`

**Discovery:** at test collection time, walk the repo root once, apply include/exclude globs, cache the result at module level. Any file added under an included path automatically enters the harness — no per-file registration needed.

### §3.5 Report format (report-only phase)

**Emit target:** `test_reports/i0302_p4_ast_conformance.json` (git-ignored; committed only for design-doc example runs during Sub-phase 3).

**Schema (one JSON per run):**

```json
{
  "generated_at": "2026-07-10T21:00:00Z",
  "head_sha": "15fbd436",
  "rule_id": "i0302-p4-http404-swallow",
  "mode": "report-only",
  "scan_scope": {
    "included_globs": ["core/views*.py", "core/views/**/*.py", "apps/*/views*.py", "apps/*/views/**/*.py"],
    "excluded_globs": ["**/tests/**", "**/migrations/**", "**/management/commands/**"],
    "files_scanned": 209
  },
  "violations": [
    {
      "file": "core/views_deliverables.py",
      "try_line": 440,
      "call_line": 441,
      "broad_handler_line": 555,
      "enclosing": "export_deliverable",
      "snippet": [
        "    try:",
        "        deliverable = get_object_or_404(Deliverable, id=deliverable_id)",
        "        ..."
      ],
      "fix_hint": "insert 'except Http404: raise' before line 555"
    }
  ],
  "info_rows": [
    {
      "file": "...",
      "reason": "Http404 handler present but body does not raise (returns custom 404 response) — informational only",
      "try_line": 0,
      "handler_line": 0
    }
  ],
  "summary": {
    "violations_total": 1,
    "info_rows_total": 0,
    "files_with_violations": 1
  }
}
```

**Console output (pytest capture):** for each violation, one line: `[HTTP404-SWALLOW] <file>:<try_line> in <enclosing> — insert 'except Http404: raise' before line <broad_handler_line>`.

**Report-only test outcome:** test PASSES with warnings recorded via `warnings.warn(...)`. Zero violations → clean run; N violations → pytest reports the total in the tail summary but exit code stays 0.

### §3.6 Enforcing-mode failure signal

**After the flip** (per §5 acceptance criteria):

- Test is a **pytest test function** (not a `conftest.py`-level collection hook) that runs at test time.
- On any violation, the test FAILS with `pytest.fail(...)` and the assertion message includes:
  1. Total violation count
  2. File-level summary (max 20 lines) 
  3. Path to the JSON report on disk (always written even in enforcing mode)
  4. The suggested fix hint for the first 5 violations

Not a collection hook because collection-time failures make debugging painful (can't easily reproduce with `-k` filter, can't see the report path). A regular test failure is more actionable and matches the existing `@ops_aggregate_allowed` pattern which is also a test (not a collection hook) despite what the module docstring hints at — verified against `tests/security/test_i0302_p4_ops_aggregate_decorator.py`.

## §4 Report-only phase — acceptance criteria

Sub-phase 3 lands the harness in report-only mode. Acceptance criteria for the report-only PR:

1. `tests/security/test_i0302_p4_ast_conformance.py` exists and passes with exit code 0 for any violation count.
2. JSON report is emitted at `test_reports/i0302_p4_ast_conformance.json` on every run.
3. The 5 known §5.1.b sites appear in the JSON report as info_rows (not violations), because they now have the `except Http404: raise` guard. If they appear as violations, the rule has a false-positive bug — fix before merge.
4. `export_deliverable:441` (or its equivalent HEAD-updated location) DOES appear as a violation if the shape is still there at merge time. This is the design-validation signal — the rule works.
5. Console output during pytest -v is human-readable and matches §3.5 spec.
6. Rigby light-SIGN post-merge on behavioral verification: run the harness against HEAD, confirm the JSON report shape + violation set match the S2748 handoff §5.1.b table.

## §5 Enforcement-mode flip — acceptance criteria

The flip to enforcing mode requires a preceding batch-fix PR that reaches zero-known-violations. Sequence:

1. **Report-only PR merges** — the JSON report shows N violations (target: N ≥ 1 with `export_deliverable` at minimum, validating the rule).
2. **Batch-fix PR** — one PR per violation OR one bundled PR (Chris D-verdict at batch-fix PR open). Each fix is the 2-line `except Http404: raise` insertion before the broad handler, matching §5.1.b prior fixes.
3. **Re-run report** — confirm violations_total == 0 after batch-fix merges.
4. **Enforcement flip PR** — one-line change: swap the pytest test body from `warnings.warn(...)` to `pytest.fail(...)`. Re-run: test still passes (violations_total == 0).
5. **CI wiring** — `.github/workflows/security-conformance.yml` already runs `tests/security/test_i0302_p4_*.py` per PR path filters. Verify the new module is picked up.

**Rollback safety:** if enforcement flip introduces surprise failures (e.g., a legit false-positive discovered post-flip), the rollback is a one-line revert. The report-only PR remains as history.

## §6 Fallback provenance (why Claude drafted per path 2)

Path 1 executed at S2749 open per Chris D-verdict:

- Retired jammed pin `pa-59d27abadeed4411` (16 rows updated).
- Minted fresh pin `pa-e71c011bfa3d4124` (label `ios-arc-open-I0302-P4-S2749`). Ping healthy.
- Sent fold-1-only AST-rule ask to fresh pin (structural, minimal). Result: LLM boundary jam (`I ran into an issue processing that request`).
- Reworded the ask to drop security jargon (no "AST rule", no "violation" — "static analysis check for a code shape"). Same LLM boundary jam.

Fresh-pin jam count = 2, matching the memory-rule threshold in `feedback_rigby_sign_worker_instability_recovery.md` for fallback to parent-Claude verifier-loop. Chris D-verdict at S2749 open: **path 2** (Claude drafts + Chris D-verdict + Rigby post-merge verifier-loop).

This spec doc is the drafting artifact. Rigby's contribution to Sub-phase 3 shifts from "propose the rule" (upstream design) to "verify the shipped implementation matches the spec" (downstream behavioral verification — her strong lane; the LLM boundary jam does not affect verifier-loop asks because they operate on observable code+output rather than compositional design).

**Design-review posture for Chris:**
- If the 6-fold spec looks correct: D-verdict "ratify + ship report-only PR" — proceed to §4 acceptance criteria.
- If any fold reads wrong: D-verdict "revise fold N" and Claude re-drafts that fold only.
- If the whole approach looks wrong: D-verdict "pause + wait for Rigby boundary to clear" — the harness ships without §14 codification for now; unblocks the other Sub-phase 3 substrates (intentional-immutability contract, endpoint sentinels, coverage-gap report).

## §7 Provenance chain

- **Design SIGN** (§14 codification F1/F2/F3): Rigby SIGN-PASS 2026-07-10 S2748 close, pin `pa-59d27abadeed4411` (now retired). All leans matched Claude's; no Chris ratification needed on F1/F2/F3.
- **Rule proposal** (this doc §3): Claude drafts per path 2 fallback. **Chris D-verdict "ratify all, ship report-only PR, one bundled batch-fix PR" — 2026-07-10 S2749 open.**
- **Implementation** (`tests/security/test_i0302_p4_ast_conformance.py`): Claude ships first-pass. Rigby light-SIGN post-merge on behavioral verification.
- **Batch-fix + enforcement flip**: Chris D-verdict "one bundled batch-fix PR" ratified 2026-07-10 S2749 open. Enforcement flip PR sequenced after clean re-run.

## §8 First run — design validation results

Report-only harness executed at `HEAD 15fbd436` (S2749 open, 2026-07-10). Full JSON at `test_reports/i0302_p4_ast_conformance.json` (git-ignored — regenerate locally via `pytest tests/security/test_i0302_p4_ast_conformance.py -v`).

**Summary:**
- 212 view files scanned across the §3.4 allowlist
- 9 violations found across 3 files
- 0 info rows

**Batch-fix scope (bundled PR per Chris D-verdict):**

| File | Enclosing | Try line | Broad handler line |
|---|---|---|---|
| `core/views_deliverables.py` | `save_deliverable` | 235 | 259 |
| `core/views_deliverables.py` | `export_deliverable` | 440 | 556 |
| `core/views_agent_tracking.py` | `project_agents` | 64 | 85 |
| `core/views_agent_tracking.py` | `agent_timeline` | 130 | 152 |
| `core/views_agent_tracking.py` | `rate_contribution` | 179 | 219 |
| `core/views_agent_tracking.py` | `mark_contribution_selected` | 246 | 279 |
| `core/views_projects_api.py` | `toggle_project_learning` | 2213 | 2252 |
| `core/views_projects_api.py` | `get_project_learning_status` | 2294 | 2319 |
| `core/views_projects_api.py` | `trigger_project_learning` | 2346 | 2368 |

**Design-intent validation:**
- Predicted 6th `export_deliverable` site → flagged ✅
- 5 fixed §5.1.b sites (get/delete/link/record/unsave/templateize `_deliverable`) → correctly NOT flagged ✅ (`test_no_false_positive_on_fixed_deliverable_sites` passes)
- `test_report_file_written_and_shape_ok` → passes ✅

**Newly discovered — extend §5.1.b or scope to §14 batch:** `save_deliverable:235` (7th distinct site in `views_deliverables.py`, missed by prior §5.1.b sweep). Per Chris D-verdict "one bundled batch-fix PR," all 9 sites ship together — no distinction between §5.1.b extension and §14 general batch.
