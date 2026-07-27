---
title: "SESSION 2999 — F-A2-equivalent for downstream consumers (v2 item #7)"
session: 2999
date: 2026-07-27
type: engineering_close
merge_shas:
  - "d48ddc493"   # PR #3668 — AC consumer verifier
prs:
  - 3668
related_arcs:
  - "findings-surface v2 (S2991 → S2992 → S2993 → S2994 → S2995 → S2996 → S2997 → S2998 → S2999)"
consumes:
  - "S2995 `_check_staleness_at_head` + `_build_repo_file_index` helpers (via lazy import)"
  - "S2997 staleness-AC injection (skipped by verifier via prepended_count)"
  - "S2998 force=true escape hatch (used in A2 SIGN real dispatch)"
---

# S2999 — F-A2-equivalent for downstream consumers (v2 item #7)

**Status:** CLOSED. One feature PR merged. Recycle-all clean at `sha=d48ddc493729`.

## What shipped

**PR #3668 (`d48ddc493`) — v2 item #7: F-A2-equivalent for downstream consumers.**

Post-LLM-validation walks every `acceptance_criterion`, extracts `file:line` refs, and checks each against HEAD via the S2995 `_check_staleness_at_head` helper. Failed refs → `unverified_consumer_refs:N` warning on `spec.warnings` (fires existing `## Warnings` section) + full list in extras metadata as `unverified_consumer_refs: [...]`.

Complements S2997: S2997 handles the SOURCE side (loud injection of verification ACs for source-side stale refs); S2999 handles the DOWNSTREAM side (quiet warning for LLM-produced phantom refs). Deliberately quiet per Rigby T1 SIGN Ask #2 — S2997 already owns the loud pattern; item #7 is the "quiet downgrade/flag" analogue of S2989's F-A2.

- **`_verify_ac_consumers(acs)`** — new helper. Lazy-imports S2995 helpers to avoid pulling management-command module into hot import path. Fail-open if imports unavailable (returns empty list). File:line-only per Rigby T1 SIGN Ask #1 (identifier grepping is deferred scope + higher FP risk).
- **Skips prepended staleness ACs** — S2997 injects verification ACs at the top citing the SAME suspect refs we're already warning about (`staleness_failed_refs_injected`). Those would double-count as unverified consumers if we didn't skip them via `prepended_count`.
- **Extras metadata** carries `unverified_consumer_refs: [...]` — always present (list), even when empty, so downstream consumers can rely on the key.
- **No caching** per Rigby T1 SIGN Ask #3(b) — build once per request, no memoization; `@lru_cache(maxsize=1)` keyed on repo-root+HEAD-sha is the next step IF perf becomes a concern.

## SIGN discipline (PLAYBOOK-7.7.2)

- **T1 SIGN** — Rigby AGREE all asks with real `repo_tool` grep on the S2995 helper confirming reuse works. Verdicts: file:line-only scope (Ask #1); warning-only surface (Ask #2); separate pass from F-A2 (Ask #3(a)) since semantics differ ("invented path?" vs "path still works?"); no caching for MVP (Ask #3(b)); ledger candidate on scope limits (Ask #3(c)).

- **A2 SIGN** — Two real dispatches via S2998's `force=true` escape hatch:
  - Finding `00a142f2-...` (fresh, decision_evidence): HTTP 201, `extras.unverified_consumer_refs=[]` — LLM produced clean ACs, verifier ran + found nothing
  - Finding `e386eb18-...` (stale, executable, `executor/models.py:271` suspect): HTTP 201, `extras.unverified_consumer_refs=[]`, `extras.staleness_failed_refs_injected=True` — S2997 injected staleness AC skipped by verifier via `prepended_count`; LLM's other ACs also clean

  Rigby independently verified via `orm_inspect_tool filter(metadata__has_key='unverified_consumer_refs')` — both deliverables persisted with the new extras key. Factory dedupe (S2998 Fold A) updated metadata via title-dedupe path, so extras values are authoritative.

## v2 sequence status (post-S2999)

- [x] #1 close_mode taxonomy — S2991
- [x] #2 finding_type classifier + backfill — S2992
- [x] #3 spec-generator prompt branching on finding_type — S2993
- [x] #4 staleness detector at ingest + backfill — S2995
- [x] #4 UI surface (badge + filter + failed-refs) — S2996
- [x] #5 orm_inspect_tool allowlist (ORM half) — S2991
- [x] #6 Rigby-SIGN nudge in UI for decision_evidence — S2994
- [x] #6 hotfix — post-dispatch View-deliverable link — S2995
- [x] #7 F-A2-equivalent for downstream consumers — **S2999 (this handoff)**
- [x] #8 wire-through smoke-check AC for half-wired findings — S2997
- [x] Fold D from S2997 — send-to-rigby re-dispatch guard — S2998
- [ ] #5 `web_fetch_tool` session cookies (deferred half) — 4th trigger surfaced S2998, 5th trigger surfaced S2999 (had to force-dispatch via APIClient again)

**The findings-surface v2 arc is 11-of-12 items complete.** Only #5-cookies remains — bigger design change with security review needed.

## Zoom-out folds (PLAYBOOK-6.10.8)

**Fold A (A2 SIGN zoom-out (a)) — `informational`.** Verifier ran clean on both dispatches — zero false positives, but zero true positives too (LLM currently produces well-grounded ACs). Good signal for MVP not proof of exhaustive coverage. If quality issues surface later, next step is expanding scope to identifier-only refs (bigger FP risk).

**Fold B (A2 SIGN zoom-out (b)) — `active watch` on S2995 Fold E ledger candidate.** Metadata now carries 4 detector keys (`spec_prompt_shape`, `finding_type_used`, `staleness_failed_refs_injected`, `unverified_consumer_refs`). Governance trigger per Rigby A2: **5+ keys OR 2+ independent consumers reading metadata in production paths**. Currently 4 keys, 0 independent consumers (test-only reads). Watch for 5th key or first non-test consumer.

**Fold C (A2 SIGN zoom-out (c)) — Rigby Tool Gap Ledger.** Crisp expectation-setting: "downstream verification is file:line-only; identifier-only refs remain unverified; empty `unverified_consumer_refs` list does NOT imply 'no phantom refs' — only 'no phantom **file:line** refs'." Log to prevent misreads.

**Fold D (5th trigger of v2 item #5 cookies) — priority climbing.** A2 SIGN needed to use APIClient AGAIN because `web_fetch_tool` can't authenticate. 5 concrete triggers now (S2996, S2997, S2998 twice — pre+post-shipping, S2999).

## HEAD / recycle state

- `d48ddc493` — feat PR #3668
- Recycle-all clean at `sha=d48ddc493729` post-merge (backend-only, frontend rebuild skipped correctly).

## Files touched

- `core/services/briefing_spec_generator.py` — `_verify_ac_consumers` helper (lazy imports S2995 helpers), integration into `generate_spec_body` post-validation, `unverified_consumer_refs` in extras
- `core/tests/test_s2999_ac_consumer_verifier.py` — 14 tests

## Playbook rule exercise

- **PLAYBOOK-7.7.1** (Spec→Ship contract) — Flow B (Option A directive from S2998 close). No phase skipped.
- **PLAYBOOK-7.7.2** (SIGN evidence discipline) — T1 SIGN used real `repo_tool` grep. A2 SIGN used real APIClient dispatches producing verifiable extras metadata + Rigby independently ran `orm_inspect_tool filter(metadata__has_key)` on both deliverables.
- **PLAYBOOK-7.7.3** (Chris-facing decision framing) — No new decision required.
- **PLAYBOOK-6.10.8** (fold classification) — 4 folds (A `informational`; B `active watch` on existing ledger candidate; C ledger candidate; D `informational` = 5th trigger on existing carry-forward).
- **PLAYBOOK-7.4.4** (recycle after merge) + S2978 refinement — Backend-only; frontend rebuild skipped correctly.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — A2 SIGN used real APIClient dispatch + ORM verify BEFORE Rigby signed off. Both dispatches produced empty `unverified_consumer_refs` legitimately (LLM clean); would have flagged if LLM cited phantoms.
- **`feedback_zoom_out_ask_per_rigby_sign`** — A2 zoom-out surfaced Fold B (active-watch upgrade of an existing ledger candidate) and Fold D (5th trigger of #5-cookies). Zoom-out is now the primary vehicle for carry-forward-priority-climbing signal.
