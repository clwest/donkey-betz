# Session 2859 — `deliverable_tool.create` Substrate Fix (Ledger #8 + #9) Shipped

**Date:** 2026-07-20
**HEAD at close:** `f0757eabd`
**PR:** [#3337](https://github.com/clwest/donkey-betz-platform/pull/3337)
**Prior session:** [SESSION_2858](SESSION_2858_CLEAR_STATUS_CONTEXT_AND_LIST_CAPS_N1_SHIPPED.md)
**Session pin retired at close:** `pa-c82f75411b3d45f0`

---

## TL;DR

Shipped the Chris-selected S2859 slate #1 (Rigby Tool Gap Ledger entries #8 + #9) as **one bundled PR with two commits** (Rigby SIGN Q3 concurred on bundle; Q4 mod folded via split-commit for blame localization):

- **Commit `14ac6e23c`** — fixture-drift fix in `core/tests/test_deliverable_initiative_diagnostics.py` (owner_id NOT NULL + S1199 PR-D provenance contract). No production code changes; unblocks the A/B/C regression classes locally.
- **Commit `b8b1cd518`** — S2859 behavior change: opt-in `preserve_title=True` on `create_deliverable()` (Ledger #8) + `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT = frozenset({'ratification_record'})` for the diagnostic gate (Ledger #9) + 12 new pytest cases.

**23/23 tests green** (12 new + 11 pre-existing that were blocked by fixture drift, now unblocked). Post-recycle Rigby E2E confirmed both fixes wired end-to-end on the Donkey Betz workspace: title lands verbatim (no `Rigby:` prefix, no 120-char cap), no `missing_initiative_id` diagnostic on the ratification_record row.

---

## Why this slate

Both entries came from the Rigby Tool Gap Ledger deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` in workspace `b4503364-2573-4401-9e28-61a739e0ce50`. Chris pre-selected them at S2858 close as "S2859 slate #1" because they trigger on EVERY ratification close-cascade and force a manual Django-shell ORM cleanup:

```python
# Historical post-create cleanup that S2859 makes obsolete:
Deliverable.objects.filter(id=<uuid>).update(
    title='RATIFICATION_20260714_PLAYBOOK_v0_8_0',  # strip 'Rigby:' prefix
    deliverable_type='ratification_record',
    category='governance',
    diagnostic_status=None,          # clear diagnostic mark
    diagnostic_code=None,
    diagnostic_payload=None,
    diagnostic_marked_at=None,
    diagnostic_expires_at=None,
)
```

Per `feedback_rigby_tool_gap_ledger`: Rigby's `deliverable_tool` IS the A1 SaaS product surface + A4 consulting demo substrate — every gap Rigby hits, a customer hits.

---

## What shipped

### Ledger #8 — auto-`Rigby:` (or `PersonalAssistant:`) title prefix

**Root cause:** `_clean_deliverable_title` (`core/services/deliverable_factory.py:468-575`) unconditionally re-attaches `f"{display_prefix}: {clean}"` at line 574 when the title doesn't already start with the prefix, AND caps at 120 chars. For PA/Rigby callers who supply explicit user-authored identifier-like titles (e.g. `RATIFICATION_20260720_PLAYBOOK_v0_9_0`), every ratification record landed with a spurious prefix + truncated identifier.

**Fix:** opt-in `preserve_title: bool = False` kwarg on `create_deliverable()`. When True:
1. Skip `_clean_deliverable_title` entirely at line 1088 gate.
2. Bypass the 120-char cap that the cleaner enforces.
3. Still apply `kwargs['title'] = title[:255]` to match the actual `Deliverable.title.max_length` (Rigby Q5.1 post-code fold — pre-existing latent bug: outer truncation was `[:500]` diverging from the model column).

Wired narrowly from the PA tool-surface create path (`td_handlers_agents._handle_deliverables` action=create line 2216). The `preserve_title` docstring explicitly narrows the scope:

```python
# S2859 Ledger #8: skip `_clean_deliverable_title` entirely when the
# caller supplied an explicit user-authored/identifier-like title
# (e.g. `RATIFICATION_...`). Wire narrowly from the PA tool surface
# only — do NOT spread to agent callers; the cleaner exists to fix
# raw-prompt-as-title leakage from those flows.
preserve_title: bool = False,
```

### Ledger #9 — `missing_initiative_id` diagnostic on ratification types

**Root cause:** `create_deliverable` unconditionally runs `_evaluate_initiative_alignment` (deliverable_factory.py:1221), which returns `('missing_initiative_id', None)` for any create without an `initiative_id`. Governance/ratification artifacts legitimately have no initiative parent — they document decisions across initiatives rather than progress within one — but every one landed marked diagnostic, hiding it from the workspace UI.

**Fix:** module-level `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT = frozenset({'ratification_record'})` (deliverable_factory.py:1398). Extended `_evaluate_initiative_alignment(initiative_id, workspace_id, deliverable_type=None)` (line 1401-1425) to skip the missing-initiative diagnostic when the type is exempt:

```python
if not initiative_id:
    if deliverable_type in _TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT:
        return None
    return ('missing_initiative_id', None)
```

**Rigby Q2 mod:** exemption narrowly scoped — bypasses ONLY the `not initiative_id` branch. If the caller supplies a stale/hallucinated `initiative_id` (line 1406 `initiative is None`) or a real `workspace_mismatch` is detected (line 1416), the diagnostic still fires. Those are real data-integrity signals regardless of type.

**Same gate applied at update-path re-eval** (`td_handlers_agents._handle_deliverables` line 2462) — `deliverable_type=obj.deliverable_type` passed to `_evaluate_initiative_alignment` — so a later update to a `ratification_record` row doesn't re-mark it via the S1195 auto-re-eval.

---

## Files touched

| File | Δ | Change |
|---|---|---|
| `core/services/deliverable_factory.py` | +42, -5 | new `preserve_title` kwarg + gate; `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT` constant + extended `_evaluate_initiative_alignment` signature; `kwargs['title']=title[:255]` alignment (Q5.1 fold) |
| `core/services/td_handlers_agents.py` | +6 | pass `preserve_title=True` at create; pass `deliverable_type=obj.deliverable_type` at update re-eval |
| `core/tests/test_deliverable_initiative_diagnostics.py` | +246 | 12 new tests (PreserveTitleTests d1-d5 + d2b; RatificationTypeExemptTests e1-e6) + fixture drift fix (owner=cls.user + agent_name='PersonalAssistant' in three `_create` helpers) |

**Net:** 289 insertions, 5 deletions across 3 production/test files.

---

## Test coverage

23/23 pass in `test_deliverable_initiative_diagnostics.py` after fixture drift resolution:

| Class | Tests | Purpose |
|---|---|---|
| `FactoryDiagnosticTests` | 4 (a1..a4) | Pre-existing S1195 factory create-path diagnostic behavior; unblocked by fixture fix |
| `UpdateDiagnosticTests` | 4 (b4..b7) | Pre-existing S1195 update-path re-eval; unblocked by fixture fix |
| `SweepDiagnosticTests` | 3 (c8..c10) | Pre-existing S1195 TTL sweep; unblocked by fixture fix |
| `PreserveTitleTests` | 6 (d1..d5 + d2b) | **NEW** — Ledger #8: verbatim title, 120-char bypass, 255-char DB column truncation (Q5.1 fold), existing-prefix preservation, regression on cleaner + idempotency guard |
| `RatificationTypeExemptTests` | 6 (e1..e6) | **NEW** — Ledger #9: exemption fires, aligned path, workspace_mismatch integrity preserved (Q2 mod), update-path exempt, non-exempt regressions on create + update |

---

## Rigby SIGN loop

Two SIGN cycles, both grounded (no rubber-stamp per `feedback_verify_rigby_tool_runs_before_trusting_sign`).

### Pre-code SIGN
- 5 grounded `repo_tool.read_file` calls
- Ledger #8 + #9 entries confirmed match my summary
- Q1 AGREE-with-mods: `preserve_title` opt-in shape right; skip `_clean_deliverable_title` entirely + skip 120-char cap
- Q2 AGREE-with-mods: type-exempt frozenset right; push type-aware decision into ONE place (extended `_evaluate_initiative_alignment` signature); exemption scoped ONLY to `missing_initiative_id` (not `workspace_mismatch`)
- Q3 AGREE: bundle ONE PR
- Q4 AGREE-with-tweaks: add test that `preserve_title=True` bypasses 120-char cap + regression test on idempotency guard
- Q5 zoom-out surfaced 3 concerns:
  - **Q5.1 escape-hatch accretion** → mitigated same-PR via narrow docstring + PA-tool-surface-only wiring
  - **Q5.2 type-as-policy-bypass** → mitigated same-PR via narrow exemption scope + Q2 mod
  - **Q5.3 "diagnostic == effectively hidden"** = deeper substrate issue driving these exemption requests; recorded as **future_trigger** (Ledger candidate — new entry queued at close)

### Post-code SIGN
- 7 grounded `repo_tool.read_file` calls covering all 7 diff sites
- Q1 AGREE-TO-SHIP: docstring encodes escape-hatch containment
- Q2 AGREE-TO-SHIP: exemption correctly scoped
- Q3 AGREE-TO-SHIP: `test_e3` asserts workspace_mismatch integrity preserved
- Q4 AGREE-WITH-MODS: split-commit within same PR for fixture drift vs behavior change → folded (two commits landed)
- Q5 surfaced 2 concerns:
  - **Q5.1 title max_length mismatch (500 vs 255)** — pre-existing latent bug my PR exposed. Folded same-PR (`kwargs['title'] = title[:255]` + `test_d2b_preserve_true_over_255_truncates_to_column_max`).
  - **Q5.2 governance obligation on future `_TYPES_EXEMPT` additions** — docstring already encodes "grow via second/third trigger per Playbook §14.2." No code change needed.

Working loop pattern: `feedback_zoom_out_ask_per_rigby_sign` continues to catch substantive concerns (7 across both SIGN cycles — 6 folded same-PR, 1 recorded as future_trigger).

---

## Post-merge E2E verify

Post-recycle Rigby dispatch created a ratification_record smoke row on the Donkey Betz workspace with title `RATIFICATION_20260720_S2859_LEDGER_8_AND_9_E2E_VERIFY`:

| Fix | Assertion | Result |
|---|---|---|
| #8 | title returned verbatim (no prefix, no 120-char cap) | ✅ `RATIFICATION_20260720_S2859_LEDGER_8_AND_9_E2E_VERIFY` |
| #9 | no `diagnostic_status='diagnostic'` on the row | ✅ diagnostic fields not surfaced (null) |

Smoke row `0b267cec-3402-480b-9306-d422cb24f8c1` archived post-verify via `content_tool.content_reject` (no `deliverable_tool.delete` action exists — see new Ledger entry below).

---

## New Ledger candidates surfaced at S2859

Two future-trigger candidates for the Rigby Tool Gap Ledger:

1. **Q5.3 fold (S2859 post-code SIGN)** — "diagnostic == effectively hidden in workspace UI" as the deeper substrate driver behind repeated exemption pressure. Requires UI/product decision (filterable diagnostic view? severity levels?). Watch for a 3rd/4th independent trigger before proposing a same-PR fix.

2. **`deliverable_tool.delete` action missing** — surfaced during S2859 post-merge E2E. Rigby had to fall back to `content_tool.content_reject` (which sets `status='archived'` — soft delete). For genuine smoke/scratch row cleanup, a real hard-delete action would be cleaner. Small (~1-2 hours), self-contained. Candidate for S2860 or later slate.

---

## What's forbidden at S2860 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

---

## Substrate story after S2859 close

Every workspace including A4 has:
- $5/day default cap; operator-configurable via `set_cap` (immediate enforcement per S2850 #3.0a) or `set_default_cap` + `backfill_defaults`
- Freeze @ 100% / downgrade @ 70% auto-enforcement with hysteresis
- Full audit trail — cycle vs operator vs simulated attribution
- Simulated enforcement (S2857) — operators verify enforcement path without touching real spend
- Post-clear `status_context` inline on clear_* responses (S2858 PR#1) — no follow-up `get_status` needed
- `list_caps include_defaults=false` scales O(1) on workspace count (S2858 PR#2)
- **NEW at S2859:** ratification records land with verbatim titles + no spurious diagnostic mark — governance close-cascade no longer requires manual ORM cleanup

Fleet auditability, downgrade savings estimates, pricing catalog canonicalization, evidence surfacing on autopilot history all still in force from prior arcs.
