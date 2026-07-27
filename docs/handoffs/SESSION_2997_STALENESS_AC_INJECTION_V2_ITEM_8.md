---
title: "SESSION 2997 — Findings-surface v2 item #8: stale-ref AC injection at spec generation"
session: 2997
date: 2026-07-27
type: engineering_close
merge_shas:
  - "c315aa4fc"   # PR #3663 — v2 item #8: stale-ref AC injection
  - "28c8547b0"   # PR #3664 — Staleness note placement polish (A2 fold)
prs:
  - 3663
  - 3664
related_arcs:
  - "findings-surface v2 (S2991 → S2992 → S2993 → S2994 → S2995 → S2996 → S2997)"
consumes:
  - "S2995 staleness axis + metadata['staleness_failed_refs']"
  - "S2993 spec_prompt_shape branching"
---

# S2997 — Stale-ref AC injection at spec generation (v2 item #8)

**Status:** CLOSED. Two feature PRs merged (item #8 + A2-fold placement polish). Recycle-all clean at `sha=28c8547b086a`.

## What shipped

### PR #3663 (`c315aa4fc`) — v2 item #8: stale-ref AC injection

When a finding has `staleness=suspected` per S2995, `send-to-rigby` now produces a spec deliverable that surfaces the drift call-out so downstream executors see it. Belt-and-suspenders per Rigby T1 SIGN Ask #2: LLM prompt hint AND deterministic AC prepend.

- **`generate_spec_body`** accepts new `staleness_failed_refs: List[str]` kwarg. When non-empty:
  - `_build_spec_prompt` appends a `STALENESS NOTE` hint to the system prompt telling the LLM to include verification steps for each ref
  - `_inject_staleness_acs` prepends one verification AC per failed ref, deduped against LLM output (defensive against the LLM having taken the hint and produced the same line), capped at `MAX_ACCEPTANCE_CRITERIA` (8)
  - `_render_spec_markdown` adds a `## Staleness note` section listing the failed refs so the drift is visually distinct from the LLM-generated body
- **AC wording differs per prompt_shape** per Rigby T1 SIGN Ask #3(a):
  - engineering (executable/unknown): "Open `<ref>` at HEAD and confirm it supports the claim in the finding text; if not, update the spec with the correct file:line citation (or revise the claim)."
  - evidence (decision_evidence): "Open `<ref>` at HEAD and confirm it still supports the evidence assertion; if not, update the citation (or revise the decision record)."
- **Extras metadata** carries `staleness_failed_refs_injected: bool` for audit
- **send-to-rigby view** forwards `finding.metadata.staleness_failed_refs` ONLY when `finding.staleness == 'suspected'` — fresh findings don't get spurious injection

### PR #3664 (`28c8547b0`) — Staleness note placement polish (A2 SIGN fold)

Rigby A2 SIGN zoom-out (b) flagged that `## Staleness note` was rendering AFTER `## Acceptance criteria`, reading as an audit appendix rather than operational context. Moved the section to sit between `## Context` and `## Open question` so the reader knows "this finding's refs are suspect" BEFORE they scan what to do about it. Same-session polish PR following S2994→S2995 hotfix precedent for real critiques of shipped shape.

## SIGN discipline (PLAYBOOK-7.7.2)

- **T1 SIGN** — Rigby fetched the actual `e386eb18-...` stale finding (`executor/models.py:271`) via `orm_inspect_tool` and confirmed the injected-AC template reads well against real corpus text. Also tightened the wording. Verdicts: Ask #1 AGREE (template close, wording improved); Ask #2 AGREE both (belt-and-suspenders); Ask #3 (a) AGREE per-shape wording; (b) DISAGREE bundling UI toast (keep decoupled); (c) AGREE low risk metadata addition; (d) AGREE ledger candidate.

- **A2 SIGN (item #8)** — Real send-to-rigby dispatch of the `e386eb18` stale finding produced deliverable `1060ab68-3dd4-427b-9000-f62e9a615510` with:
  - `metadata.staleness_failed_refs_injected: true`
  - First AC IS the prepended verification line ("Open `executor/models.py:271` at HEAD and confirm it supports the claim...")
  - LLM ALSO wove additional verification ACs (belt-and-suspenders paid off)
  - Context section: "the citation points to executor/models.py:271, but that file reference failed re-verification at HEAD and must be checked"
  - Rendered `## Staleness note` section present

  Rigby independently verified via `deliverable_tool detail` + `orm_inspect_tool filter(metadata__has_key='staleness_failed_refs_injected')`. All 3 sub-checks of Ask #1 AGREE, Ask #2 AGREE (with caveat: `orm_inspect_tool` doesn't support `metadata__<key>` JSON-path lookups, only `metadata__has_key` — logged as Rigby Tool Gap).

## v2 sequence status (post-S2997)

- [x] #1 close_mode taxonomy — S2991
- [x] #2 finding_type classifier + backfill — S2992
- [x] #3 spec-generator prompt branching on finding_type — S2993
- [x] #4 staleness detector at ingest + backfill — S2995
- [x] #4 UI surface (badge + filter + failed-refs) — S2996
- [x] #5 orm_inspect_tool allowlist (ORM half) — S2991
- [x] #6 Rigby-SIGN nudge in UI for decision_evidence — S2994
- [x] #6 hotfix — post-dispatch View-deliverable link — S2995
- [x] #8 wire-through smoke-check AC for half-wired findings — **S2997 (this handoff)**
- [ ] #5 `web_fetch_tool` session cookies (deferred half) — 2nd trigger surfaced S2996
- [ ] #7 F-A2-equivalent for downstream consumers — carry-forward

**The findings-surface v2 arc is 8-of-8 UI+backend items complete except #5-cookies (bigger design change) and #7 (F-A2-equivalent).** The stale-finding pipeline now flows cleanly: audit → ingest classifier flags stale → FindingsTab surfaces orange Stale badge → Chris clicks Verify evidence / Send to Rigby → deliverable carries `## Staleness note` + prepended verification ACs → executor sees the drift call-out in the first AC they scan.

## Zoom-out folds (PLAYBOOK-6.10.8)

**Fold A (Rigby T1 Ask #1) — `informational`, mitigated same-PR.** AC wording tightened from generic "verify" to "Open `<ref>` at HEAD and confirm it supports the claim; if not, update the spec with the correct file:line citation (or revise the claim)." Per Rigby suggestion during T1 SIGN, not deferred.

**Fold B (Rigby A2 zoom-out (a)) — `future_trigger`.** Exact-string dedupe against LLM output is right for MVP. If we see repeated noise, dedupe by `(ref, verb)` deterministic key rather than fuzzy text similarity. Watch for 2nd trigger.

**Fold C (Rigby A2 zoom-out (b)) — `same_pr_mitigatable` → mitigated in PR #3664.** Staleness note placement moved from after-ACs to before-ACs so it informs AC scanning.

**Fold D (Rigby A2 zoom-out (c)) — `future_trigger`.** send-to-rigby endpoint currently allows re-dispatch when `deliverable_id` is already set (I had to manually clear it during A2 SIGN dispatch — sharp edge). Should refuse by default with a `force=true` / `allow_redraft=true` escape hatch. Not blocking; log for future PR.

**Fold E (Rigby A2 zoom-out (d)) — Rigby Tool Gap Ledger.** "Finding→spec pipeline needs staleness refs to survive into executor-facing ACs + rendered note; deterministic injection fixed." Clean example of "context drop" in a half-wired chain, now closed.

**Fold F (from A2 tool_run) — Rigby Tool Gap Ledger.** `orm_inspect_tool` doesn't support `metadata__<key>` JSON-path lookups — only `metadata__has_key`. Rigby hit this trying to filter by `metadata__staleness_failed_refs_injected=true`. Not blocking (workaround: `has_key` + client-side filter) but a real surface gap.

## HEAD / recycle state

- `28c8547b0` — polish PR #3664 (Staleness note placement)
- `c315aa4fc` — feat PR #3663 (item #8)
- Recycle-all clean at `sha=28c8547b086a` post-both-PRs (backend-only diffs, frontend rebuild skipped correctly via HEAD-range path-diff).

## Files touched

- `core/services/briefing_spec_generator.py` — `_staleness_ac_for` / `_staleness_prompt_hint` / `_inject_staleness_acs` helpers; `generate_spec_body` `staleness_failed_refs` kwarg; `_render_spec_markdown` Staleness note section (moved above ACs by polish PR)
- `core/views_doc_research_findings.py` — send-to-rigby view forwards `finding.metadata.staleness_failed_refs` when staleness=suspected
- `core/tests/test_s2997_staleness_ac_injection.py` — 17 tests

## Playbook rule exercise

- **PLAYBOOK-7.7.1** (Spec→Ship contract) — Flow B (Option B directive from S2996 close). Two PRs in one session: main + A2-fold polish, both followed the 7.7.1 shape.
- **PLAYBOOK-7.7.2** (SIGN evidence discipline) — Both SIGN cycles used real tool_runs. T1 used `orm_inspect_tool` on 1 real stale row. A2 used `deliverable_tool detail` + `orm_inspect_tool filter` on the actual dispatched deliverable. Real gpt-5-mini roundtrip in A2 dispatch produced verifiable content.
- **PLAYBOOK-7.7.3** (Chris-facing decision framing) — No new Chris decision required; Option B was Chris's directive at S2996 close.
- **PLAYBOOK-6.10.8** (fold classification) — 6 folds classified (A `informational` mitigated in main PR; B `future_trigger`; C `same_pr_mitigatable` → mitigated in polish PR; D `future_trigger`; E/F ledger candidates).
- **PLAYBOOK-7.4.4** (recycle after merge) + S2978 refinement — Both PRs are backend-only; recycle-all correctly skipped frontend rebuild via HEAD-range path-diff.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — Rigby A2 Ask #1 used `deliverable_tool detail` to independently verify substrate (metadata flags, section presence, AC ordering).
- **`feedback_zoom_out_ask_per_rigby_sign`** — A2 zoom-out surfaced Fold C (`same_pr_mitigatable`) that was mitigated same-session via polish PR. Canonical example of the zoom-out ask catching real critique that would otherwise ship as-is.
