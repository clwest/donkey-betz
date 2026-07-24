# SESSION 2945 — Ledger #38 Batch 4 (`run_cleanup` dry_run alignment — closes content_tool 100%)

**Closed:** 2026-07-24
**Body commit:** `62ca81bea` (u-d-b PR #3529, merged `main`)
**Docs cascade:** filled at close

---

## What shipped

**PR #3529** — S2945 Ledger #38 batch 4: `content_tool.run_cleanup` dry_run alignment via shared `_gather_cleanup_preview` helper. Closes content_tool's last unaligned mutation — all 4 content_tool mutations (`bulk_archive_published`, `bulk_archive`, `generate_newsletter`, `run_cleanup`) now carry the S2942 envelope contract. **content_tool per-action mutation alignment: 3 → 4 (100%).**

Chris directed Option G from the S2944-close deferred queue at S2945 open. Claude+Rigby T1 SIGN converged on Option B (rich preview via shared helper) over Option A (minimal stub); Rigby DISAGREE with Option A as final. Chris ratified Option B on plain-English framing.

Same-PR fold (PLAYBOOK-6.10.8): 2nd trigger of S2944 record-only statuses-autofill quirk mitigated at helper layer. Rigby's first live-verify returned `invalid_params` because GPT-5.2 autofilled `statuses:[]` — fix `if not statuses: statuses = ['ready','draft']` in `_gather_cleanup_preview` hardens BOTH the dry_run handler path AND the real Celery task path (single source of truth).

## Files shipped

- **MODIFIED** `core/services/td_handlers_content.py` — `run_cleanup` dry_run branch (line 4670+) emits S2942 envelope: `dry_run=true` (default), `would_action='dispatch_celery'`, `would_task='cleanup_stale_content'`, `no_writes=true`, plus preview (`would_archive_count`, `total_found`, `safe_statuses`, `cap`, `top_by_type[:5]`, `top_by_category[:5]`).
- **MODIFIED** `core/tasks_misc.py` — NEW `_gather_cleanup_preview()` helper (line 34-102) as single source of truth for the archive queryset. `_impl_cleanup_stale_content` refactored to call the helper (line 104-159) — no drift risk between preview and real archive filter.
- **MODIFIED** `core/services/pa_tool_schemas.py:4190` — `dry_run` description enumerates `run_cleanup` in the aligned actions list.
- **NEW** `core/tests/test_s2945_dry_run_batch_4.py` — 14 regression tests (10 handler + 4 helper).
- **MODIFIED** `docs/research/tools/validation/content_tool_validation.md` — header S2944 → S2945; §Covered actions + §5a mutation containment + §6.4 updated for `run_cleanup`; §6.6 added with real Rigby dispatch evidence (§6.6.a envelope proof, §6.6.b same-PR autofill fold, §6.6.c regression coverage, §6.6.d single-source-of-truth guarantee).

## Twin mirrors (per `feedback_twin_deliverable_at_every_ratification`)

- **Content mirror:** `fe4b9b00-8e3f-44ee-8801-44e979acec9c` (Architecture & Research workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`, category `initiative_phase_doc`; diagnostic flag cleared via ORM per known `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`).
- **Ratification envelope:** `b7ed980d-1561-4821-bfce-51f24e5917a7` (same workspace, `deliverable_type='ratification_record'`, category `governance`; no diagnostic flagged — S2942 pre-set workaround baked in).

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

- Recycled mid-session twice (once post-handler-edit before live-verify, once after autofill fix).
- Recycled after PR #3529 merge (workers matched HEAD `62ca81bea`).
- Live-verified `run_cleanup` dry_run in conversation `pa-2306c73855774b75`:
  - **Pre-fix verify (task `126fc9d6`):** returned `invalid_params` — surfaced the autofill quirk.
  - **Post-fix verify (task `30af3209`, 15ms):** 4/4 S2942 sentinels + 4/4 preview fields + `safe_statuses` coerced to `['ready','draft']` default.
  - **Post-merge verify (11ms):** identical clean shape, workers matched HEAD.
- Gap-map `--check` exits 0. Scoreboard witness unchanged (`per_execution_mode.live=3`, `per_mutation_safety.dry_run_supported=3`) — expected, scoreboard is per-doc and content_tool was already promoted at S2943; S2945 grows PER-ACTION alignment inside content_tool.

## Governance

- **D6 moratorium** unchanged.
- **PLAYBOOK-6.10.7 zoom-out ask** raised in T1 SIGN routing; Rigby addressed with substantive tool_runs (searched precedent shapes + read handler+tasks+tasks_misc); rejected Option A as final on future-drift + retrofit-cost grounds.
- **PLAYBOOK-6.10.8 same-PR fold** exercised: statuses-autofill 2nd-trigger fix bundled into ship PR before merge.
- **Zoom-out ledger candidates recorded record-only:** none new (autofill 2nd-trigger was mitigated in-PR, not deferred).

## Rigby Tool Gap Ledger

- **No new formal entries.** The autofill fix was a helper-layer defect (2nd trigger of S2944 record-only), not a tool-surface limitation.

## Ledger #38 arc status

| Batch | Session | Actions aligned | PR |
|---|---|---|---|
| MVP | S2942 | blog_tool.generate/approve/reject, feedback_tool.submit/update | (see S2942 handoff) |
| Batch 2 | S2943 | content_tool.bulk_archive_published | #3524 |
| Batch 3 | S2944 | content_tool.bulk_archive + generate_newsletter | #3527 |
| **Batch 4** | **S2945** | **content_tool.run_cleanup — closes content_tool 100%** | **#3529** |

**content_tool status:** All 4 mutations (bulk_archive_published + bulk_archive + generate_newsletter + run_cleanup) native-aligned to S2942 envelope. Delegated mutation actions inherit dry_run coverage from sibling tools (blog_tool, feedback_tool, deliverable_tool). **content_tool per-action mutation alignment: 100%.**

## Metrics

- **Scoreboard baseline (unchanged):** `per_execution_mode: {unknown: 158, live: 3}` + `per_mutation_safety: {unknown: 158, dry_run_supported: 3}`. Content_tool doc metric already promoted at S2943.
- **Gap-map headline (unchanged):** `100 validated_full / 0 untested`.
- **Test suite growth:** +14 tests (10 handler + 4 helper). Combined S2942+S2943+S2944+S2945 dry_run suite: 42 tests, ~1.1s, all pass.
- **Diff:** 5 files, +502/−37 lines.
