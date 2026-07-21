# Session 2856 handoff — autopilot_tool.history include_evidence + enforcement_report auto/operator split shipped

**Date:** 2026-07-20 (evening)
**Branch:** `main` at `4b7d29927`
**Session pin:** `pa-cd83950450f3466c` (minted at S2856 open; retires at close)
**Shipped:** PR #3329 (`4b7d29927`) — S2856 slate #2 + #3 bundle

---

## Two PRs shipped in the S2856 window

This session opened after S2855 close with a stale `00-START-NEXT-SESSION.md` — slate #1 (`was_downgraded` flag on `LLMCallLog`) had already been shipped by a prior session on the same S2856 label as **PR #3328** (`725b71f2f`) but the START-NEXT doc still listed it as pending. Investigation caught this before wasted work.

- **PR #3328** `725b71f2f` (prior session, S2856 label) — `was_downgraded` + `pre_downgrade_model_id` fields on `LLMCallLog` + `enforce_real_ai` singleton stale-flag reset. Removed the OVER-estimate caveat that shipped with S2853. See its commit body for detail — this handoff does not duplicate that content.
- **PR #3329** `4b7d29927` (this session) — bundle of slate #2 (`autopilot_tool.history include_evidence`) + slate #3 (`enforcement_report` auto/operator event split) + bundled schema copy-edit to `include_downgrade_savings` description (was stale since PR #3328).

Chris ratified the bundle at S2856 open per `feedback_claude_rigby_agree_first_chris_yes_no`.

---

## What PR #3329 shipped

Two additive read-surface changes to `core/services/td_handlers_ops.py`. No migration. Backward-compatible defaults preserve prior response shape.

### Slate #2 — `autopilot_tool.history include_evidence` (opt-in)

- Adds `include_evidence=false` payload param.
- When `true`, each row includes the raw `evidence` and `result` JSON fields from `AutopilotAction`.
- Response top-level `include_evidence` echoes what the server applied.
- Operators can now inspect `trigger` / `actor_user_id` / `reason` without dropping to Django shell.

### Slate #3 — `enforcement_report` auto/operator event split

- Per-workspace rows gain `auto_events_count` + `operator_events_count`.
- Decision rule (Rigby pre-code SIGN Q1): `bool(evidence.actor_user_id)` → operator; absent → auto.
- Rule works uniformly across all 4 filtered action types including manual-clear rows that don't stamp `trigger` (freeze_cleared, manual downgrade_cleared).
- `enforcement_events_count` preserved as the sum for back-compat.
- Response `note` extended with the split-rule explainer so operators know how to interpret the counts.

### Bundled copy-edit — `include_downgrade_savings` schema description

PR #3328 landed the semantic fix (`was_downgraded=True` filter) but didn't refresh the schema doc. Wording still said "natively-mini calls are not yet distinguishable from enforcer-forced downgrades, so the estimate OVER-reports true policy savings." Rewritten to reflect the current filter behavior + the under-report note for windows straddling the S2856 deploy boundary. Same PR because the wording is directly tied to the shipped semantics.

---

## Rigby SIGN loop

### Pre-code design SIGN — AGREED-TO-BUILD

Full response Q1–Q5 answered; 9 tool_runs across `repo_tool` (independent line-number verification of write sites at `budget.py:684/756/827/882/953` and callers at `core.py:1467-1473` vs `td_handlers_ops.py:4074-4079`) + `workspace_budget_tool.get_default_cap / list_caps` E2E + `deliverable_tool` ledger create.

Rigby's Q5c zoom-out fold added a third risk beyond my two: `include_evidence` payload growth as a future API-stability concern → deferred to a future `selected_fields` param over retrofit truncation. Codified in the schema description for future-me.

### Post-code diff SIGN — AGREED-TO-SHIP

4 independent `repo_tool` diff verifications on the actual staged hunks (`td_handlers_ops.py:2085-2205 + 4345-4535 + 4535-4655`, `pa_tool_schemas.py:2915-3005`). Rigby verified line-by-line the shape matched what she'd agreed to build.

Optional Q3 belt-and-suspenders comment on the shared `empty_bucket` immutable-by-convention dict applied inline (Rigby's note about the future footgun on shared-default mutation).

Q5a: `note` field is the right home for surfacing the decision semantics to operators; a schema-side sentence is optional and deferred. Q5b: skip the payload-growth warning as premature.

---

## Tests

Locked in at `core/tests/test_s2856_autopilot_evidence_and_split.py` (+233 lines, 10 cases, 2 classes):

- **`AutopilotHistoryIncludeEvidenceTests`** (3): default omits evidence + result; `include_evidence=true` surfaces both; limit capped at 100.
- **`EnforcementReportAutoOperatorSplitTests`** (7): auto-only row; operator-only row; mixed with sum-invariant assertion; empty-window row shape defaults to 0/0/0; `actor_user_id=''` edge case (`bool('') is False` → auto bucket); out-of-window row ignored; response `note` mentions split rule.

Full regression: 43/43 pass locally (10 new + 8 pre-existing `test_s2856_was_downgraded` + 25 `test_pricing_catalog`) in 0.811s.

---

## Post-merge E2E (per `feedback_local_truth_no_production`)

Local `make celery-recycle` post-merge on `4b7d29927` per PLAYBOOK-7.4.4. Rigby E2E dispatch confirmed:

- `autopilot_tool.history include_evidence=true` returns rows with populated `evidence` + `result` JSON.
- `workspace_budget_tool.enforcement_report window=24h` returns rows with new `auto_events_count` + `operator_events_count` keys.
- Real data: Donkey Betz workspace shows `enforcement_events_count: 17`, `auto_events_count: 6`, `operator_events_count: 11`. **Sum invariant holds: 6 + 11 = 17.**
- Zero-events workspaces default to `0 / 0 / 0`.
- Response `note` carries the S2856 split-rule explainer.

---

## Forward carry

### Rigby's Q5c zoom-out fold — `include_evidence` payload-growth risk

Codified in the schema description at `pa_tool_schemas.py`. Trigger: if evidence JSONFields grow materially in the future, prefer a `selected_fields` param over retrofit truncation. One trigger observed; watch for second before promoting to Playbook rule.

### Pre-code Q5b — duplicated `enforcement_action_types` constant

`enforcement_action_types` at `td_handlers_ops.py:4362` duplicates the reasoning that lives in `ops_autopilot/budget.py`. Adding a fifth workspace action type would require updating both sites. Deferred as a small refactor. One trigger observed; not yet urgent.

### Pre-code Q5a — `actor_user_id` as first-class column vs JSONField

The `evidence.actor_user_id` contract is now a first-class **read** semantic (drives split in the report) even though it lives in a JSONField on the **write** side. Long-term this wants to be an explicit column on `AutopilotAction`. Deferred — needs migration.

---

## Not shipped at S2856 close (deferred to S2857 or later)

- Slate #4 `budget_tool.simulate_enforcement` PA-surface for enforcer hot-path E2E
- Slate #5 `clear_freeze`/`clear_downgrade` post-clear spend context
- Slate #6 N+1 in `list_caps include_defaults=False`
- Slate #7 Phase 2B pricing (`model_kind`, `EMBEDDING_COSTS`+`MODEL_PRICES` unification, `pricing_catalog_version`, LLMCallLog↔CostTracking provenance column)
- Slate #8 A4 warm-up under ratified constraints

All S2854/S2855-carried items still queued (see prior handoffs).

---

## Twin-pointer docs card (per `feedback_twin_pointer_docs_at_boundaries`)

Current-arc artifacts live in BOTH:

**Repo `/docs/`**
- Handoffs: `docs/handoffs/SESSION_2856_AUTOPILOT_HISTORY_EVIDENCE_AND_ENFORCEMENT_SPLIT_SHIPPED.md` (this file)
- Prior in the arc: `docs/handoffs/SESSION_2855_PRICING_CANON_PHASE_2A_SHIPPED.md`, `SESSION_2854_PRICING_CANON_PHASE_1_SHIPPED.md`, `SESSION_2853_W2_3_2_DOWNGRADE_SAVINGS_SHIPPED.md`, `SESSION_2852_LIST_CAPS_AUTH_TIGHTENED.md`
- Next-session start: `00-START-NEXT-SESSION.md`

**Workspace UI `/workspaces`**
- Content mirror + ratification envelope to be written by Rigby at close per `feedback_rigby_writes_workspace_deliverables`. Workspace: Donkey Betz (`b4503364-2573-4401-9e28-61a739e0ce50`) + Architecture & Research (`a9a16593-e0a4-44dc-8256-efc65d524b3c`).
- Rigby tool gap ledger entry: `0cde5eb5-718b-454e-82f1-e6c3423846d9` (created by Rigby at pre-code SIGN time).

---

## Session pin lifecycle

- Pin `pa-cd83950450f3466c` MINTED at S2856 open via `python manage.py session_lifecycle close --label s2856-open` (retired `pa-42d61f82953a4e48` from the prior stealth-S2856 session that shipped PR #3328).
- Pin `pa-cd83950450f3466c` RETIRES at S2856 close. Fresh mint required at S2857 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.
