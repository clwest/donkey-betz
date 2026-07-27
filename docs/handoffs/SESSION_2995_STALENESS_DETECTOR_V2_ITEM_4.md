---
title: "SESSION 2995 — Findings-surface v2 item #4: staleness detector at ingest + backfill"
session: 2995
date: 2026-07-27
type: engineering_close
merge_shas:
  - "2b9ba90cc"   # PR #3657 — S2994 hotfix: post-dispatch View-deliverable link
  - "c4c814f27"   # PR #3658 — PR (a): schema + helper + serializer + tests
  - "85d37d0fc"   # PR #3659 — PR (b): backfill on 900-row corpus
prs:
  - 3657
  - 3658
  - 3659
related_arcs:
  - "findings-surface v2 (S2991 → S2992 → S2993 → S2994 → S2995)"
consumes:
  - "S2992 finding_type axis + regex classifier"
  - "S2994 FindingsTab UI (compatible without changes; staleness ready to surface)"
---

# S2995 — Staleness detector at ingest (+ S2994 post-dispatch UX hotfix)

**Status:** CLOSED. Three feature PRs merged (one S2994 hotfix + PR (a) + PR (b)). Recycle-all clean at `sha=85d37d0fc106`.

## Session shape

Session opened with a Chris-signaled S2994 hotfix (Verify-evidence button re-dispatch footgun), then pivoted to the planned v2 item #4 (staleness detector) — two PRs on the S2992 pattern (schema-only + backfill).

## What shipped

### PR #3657 (`2b9ba90cc`) — S2994 hotfix: post-dispatch View-deliverable link

Chris used the "Verify evidence" button on a real decision_evidence finding and hit a footgun: after dispatch, the button stayed clickable and would re-dispatch (burning tokens on the same finding). Fix by making the CTA shape-aware — once `finding.deliverable_id` is set, the button transforms into a "View deliverable" link with `ExternalLink` icon + type-aware tooltip. The link deep-links via a new `?deliverable=<id>` query param that `DeliverablesTab` now consumes to auto-`setSelectedId` on landing (mirrors the already-shipped `?filter=` pattern per Rigby T1 SIGN — not scope creep).

Files touched: `frontend/src/pages/workspace/tabs/FindingsTab.tsx`, `frontend/src/pages/workspace/tabs/DeliverablesTab.tsx`, `core/templates/index.html` (Vite manifest sync).

### PR #3658 (`c4c814f27`) — v2 item #4 PR (a): schema + helper + serializer + tests

**Fourth orthogonal axis on `DocResearchFinding`** — `staleness = fresh | suspected`. Orthogonal to status/close_mode/finding_type: a decision_evidence finding can still be `suspected` if its cited file:line drifted.

- **Migration 0402 (schema-only, surgical)** — `staleness` CharField, `choices=[fresh, suspected]`, `default='fresh'`, `db_index=True`. Constants on `DocResearchFinding.STALENESS_FRESH` / `.STALENESS_SUSPECTED`. Django's autodetector swept up 40+ unrelated model drift ops (Narrative*, HAI dispatch help_text, index renames) into the initial pass; **stripped to just the field add** per S2992 surgical-migration precedent.

- **`_check_staleness_at_head(text, base_dir, file_index) -> (str, [failed_refs])`** — reuses `EXECUTABLE_FILE_LINE_RE` (from the S2992 classifier) to extract `path:line` refs. Any ref that fails path-existence OR line-count check flips to `suspected`; failed refs land in `metadata['staleness_failed_refs']` so v2 item #8 can consume without a second schema field.

- **Bare-filename normalization via git ls-files** — Rigby T1 SIGN Fold A on the 20-row corpus sample revealed that bare refs like `td_handlers_ops.py:5585` (no directory prefix) are common in real findings. Addressed via a `basename → {paths}` index built once per command invocation from `git ls-files`. Collision tie-break: shortest path wins (canonical over deep-buried). When git isn't available (tests), index is empty and bare refs correctly go `suspected`.

- **Ingest command wired** — every new/updated finding gets checked automatically during upsert.

- **New `--recheck-staleness [--apply]` command mode** — mirrors the S2992 `--reclassify-existing` shape. Dry-run by default (prints distribution + change delta); `--apply` required to persist per PR #3648 zoom-out fold + `feedback_local_truth_no_production`.

- **Serializer + list-endpoint filter surface `staleness`** (`?staleness=fresh|suspected`).

- **25 tests** covering: no-refs → fresh; path missing → suspected; line out of range → suspected; multi-ref where any fail → suspected; multi-ref all pass → fresh; backticked refs still detected; bare-ref resolves via index; bare-ref unresolvable → suspected; empty file_index (git unavailable) → bare refs suspected; `_resolve_ref_path` collision tie-break prefers shortest; `_build_repo_file_index` degrades to empty dict when git missing; `--recheck-staleness` dry-run doesn't persist; `--apply` persists + writes `staleness_failed_refs`; serializer includes staleness; filter by `staleness=suspected` / `staleness=fresh` / invalid values silently ignored.

### PR #3659 (`85d37d0fc`) — v2 item #4 PR (b): backfill on 900-row corpus

Data migration 0403 iterates every existing row via `apps.get_model(...).iterator(chunk_size=500)`, re-runs `_check_staleness_at_head`, only flips rows whose recheck output differs. Reverse resets non-fresh rows to fresh + drops the `staleness_failed_refs` metadata key (pragmatic — pre-migration state was uniformly fresh).

**Post-migration distribution matches pre-merge dry-run exactly:**
- `fresh`: **896** (99.6%)
- `suspected`: **4** (0.4%)
- total: **900**

**All 4 suspected findings are real drift signals**, not false positives:
| id (prefix) | failing ref | reason |
|---|---|---|
| `e386eb18` | `executor/models.py:271` | no `executor/` top-level dir |
| `956f8571` | `base_agent.py:4723` | bare ref, line 4723 out of range |
| `7d5f6797` | `assistant/base.py:172` | no `assistant/` dir |
| `56851590` | `models/conversations/models.py:19` | no `models/` top-level dir |

**Zero false positives** from the git-ls-files basename normalization — Rigby T1 SIGN Fold A paid off exactly as predicted. Bare refs like `td_handlers_ops.py:5585` correctly resolve to `core/services/td_handlers_ops.py` via the ls-files index.

## SIGN discipline (PLAYBOOK-7.7.2)

- **T1 SIGN (item #4 framing)** — Rigby returned real `orm_inspect_tool` results on Ask #1: sampled 20 real `finding_type='executable'` rows from the 138-row subset. Confirmed the regex catches expected shapes AND revealed the bare-filename over-fire risk (~4-5 of 20 sampled rows had bare refs). Same-PR mitigation: git-ls-files basename index. Ask #2 (semantic range around VERIFIED-at-HEAD findings): AGREE don't special-case — that's what `--recheck-staleness` is for. Ask #3 zoom-out: AGREE keep 2-value enum, AGREE local filesystem sufficient under `feedback_local_truth_no_production`, AGREE store failed refs in `metadata['staleness_failed_refs']` (MVP shape; dedicated JSONField only if it grows).

- **T1 SIGN (S2994 hotfix framing)** — Rigby returned real `repo_tool` search on `WorkspacePageNew.tsx`; confirmed URL shape works cleanly (WorkspacePageNew only reads `tab` + `sub`; extra params pass through to DeliverablesTab's own `useSearchParams`). Verdicts: keep single "View deliverable" label; keep expanded-row belt-and-suspenders link updated with `&deliverable=`; `?deliverable=` support in DeliverablesTab is not scope creep (mirrors `?filter=`).

- **A2 SIGN (item #4)** — Post-both-merge, Rigby independently verified via `orm_inspect_tool count_by(staleness)` → `{fresh: 896, suspected: 4}` (matches dry-run exactly) AND `filter(staleness='suspected', limit=5)` → all 4 suspected rows carry `metadata.staleness_failed_refs` populated with the failing ref. Zero rubber-stamping.

## v2 sequence status (post-S2995)

- [x] #1 close_mode taxonomy — S2991
- [x] #2 finding_type classifier + backfill — S2992
- [x] #3 spec-generator prompt branching on finding_type — S2993
- [x] #4 staleness detector at ingest + backfill — **S2995 (this handoff)**
- [x] #5 orm_inspect_tool allowlist (ORM half) — S2991 (`web_fetch_tool` cookies deferred)
- [x] #6 Rigby-SIGN nudge in UI for `finding_type=decision_evidence` — S2994
- [x] #6 hotfix — post-dispatch View-deliverable link — **S2995 (this handoff)**
- [ ] #7 F-A2-equivalent for downstream consumers — carry-forward
- [ ] #8 wire-through smoke-check AC for half-wired findings — carry-forward

**#4 was the last big-ticket backend item on the v2 list.** Remaining v2 items (#7, #8) are ~30-60 min each and depend on downstream consumer patterns that haven't crystallized yet. Natural next candidates are the surface work: FindingsTab staleness badge/filter (matches the S2994 finding_type UI pattern), or Chris pivots to a fresh arc.

## Zoom-out folds (PLAYBOOK-6.10.8)

**Fold A (item #4 T1 SIGN Ask #1) — `informational`, mitigated same-PR.** Bare-filename refs common in corpus (~4-5 of 20 sampled). Would over-fire under strict path-check. Mitigation: git-ls-files basename index built once per command invocation, with shortest-path collision tie-break. Backfill result validates: 0 false positives.

**Fold B (item #4 A2 SIGN zoom-out (a)) — `informational`.** 0.4% signal rate right-sized. Tuning candidate for later if we want more recall (expand beyond `path:line` to `package.module:line` or unadorned repo-relative paths) but only if a downstream consumer surfaces demand.

**Fold C (item #4 A2 SIGN zoom-out (b)) — `future_trigger`.** `metadata` JSON blob now carries 3+ domain-specific keys (`spec_prompt_shape`, `finding_type_used`, `staleness_failed_refs`). Rigby flags moderate long-term schema-drift risk. Promote to dedicated `staleness_detail` JSONField once it grows past "one list of refs" (e.g. failure_kinds, checked_refs, timestamps, head_sha). Not blocking; watch for 2nd trigger.

**Fold D (item #4 A2 SIGN zoom-out (c)) — `future_trigger`.** Periodic (weekly) recheck via Celery beat only worth it if UI surfaces stale findings. Current cadence: ingest + `--recheck-staleness --apply` on demand. Revisit when a UI surface for stale findings exists.

**Fold E (item #4 A2 SIGN zoom-out (d)) — Rigby Tool Gap Ledger.** Metadata accretion governance. Reserve a namespace key convention (e.g. `metadata.detectors.*` or `metadata.sign.*`) + document allowed keys + expected shapes so future additions don't silently diverge. Logged.

**Fold F (S2994 hotfix zoom-out) — `future_trigger`.** WorkspacePageNew's `setSearchParams({tab, sub}, {replace: true})` drops non-tab/sub params like `?deliverable=`. Fine for initial-landing use-case (deep-link works on first paint) but breaks if user then clicks a different tab. Fix would merge instead of replace, or explicitly whitelist pass-through params.

## HEAD / recycle state

- `85d37d0fc` — feat(s2995) PR #3659 (backfill)
- `c4c814f27` — feat(s2995) PR #3658 (schema + helper)
- `2b9ba90cc` — fix(s2995) PR #3657 (S2994 hotfix)
- Recycle-all clean at `sha=85d37d0fc106` post-PR-#3659 (backend-only diff, frontend rebuild skipped correctly).

## Files touched

- `core/models_audit_findings.py` — `staleness` CharField + constants
- `core/migrations/0402_s2995_doc_research_finding_staleness.py` — schema-only, surgical
- `core/migrations/0403_s2995_staleness_backfill.py` — data migration re-runs check
- `core/management/commands/index_doc_research_findings.py` — helpers (`_build_repo_file_index`, `_resolve_ref_path`, `_check_staleness_at_head`), ingest wiring, `--recheck-staleness [--apply]` mode
- `core/views_doc_research_findings.py` — `staleness` in serializer + `?staleness=` filter
- `core/tests/test_s2995_staleness_detector.py` — 25 tests
- `frontend/src/pages/workspace/tabs/FindingsTab.tsx` — button-shape gate + type-aware "View deliverable" link (hotfix)
- `frontend/src/pages/workspace/tabs/DeliverablesTab.tsx` — `?deliverable=<id>` deep-link support (hotfix)

## Playbook rule exercise

- **PLAYBOOK-7.7.1** (Spec→Ship contract) — Flow B (spec-originated from S2991's v2 list; Chris "A then B" directive at S2994 open). No phase skipped: framing → T1 SIGN → code → tests → PR → A2 SIGN → merge → recycle for the main sequence. S2994 hotfix followed same shape mid-session (Chris signal → T1 SIGN → code → PR → merge → recycle).
- **PLAYBOOK-7.7.2** (SIGN evidence discipline) — Both T1 SIGN cycles returned real tool_runs (`orm_inspect_tool` 20-row corpus sample + `repo_tool` search). A2 SIGN independently verified via `count_by(staleness)` + `filter(staleness='suspected')`. Zero rubber-stamping.
- **PLAYBOOK-7.7.3** (Chris-facing decision framing) — No new Chris ratification required this session; item #4 already ratified as "Option B" at S2994 open. S2994 hotfix routed with plain-english "does it lose anything? / is it more work later?" framing.
- **PLAYBOOK-6.10.8** (fold classification) — 6 folds classified (A `informational` mitigated same-PR; B `informational`; C `future_trigger`; D `future_trigger`; E ledger candidate; F `future_trigger`).
- **PLAYBOOK-7.4.4** (recycle after merge) + S2978 refinement — Followed exactly for both frontend (S2994 hotfix) and backend PRs. S2994 hotfix used `make recycle-all` per `feedback_recycle_after_merge` (frontend rebuild). Item #4 PRs are backend-only; recycle-all correctly skipped frontend rebuild via HEAD-range path-diff.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — Backfill dry-run was verified via direct ORM before committing the data migration; the 4 suspected rows spot-checked against real file paths to confirm they're real drift signals (not false positives) before Rigby A2 SIGN.
- **`feedback_local_truth_no_production`** — Path checks use local filesystem; `--apply` on `--recheck-staleness` IS the deploy step. No "live E2E deferred to production Railway deploy" framing.
