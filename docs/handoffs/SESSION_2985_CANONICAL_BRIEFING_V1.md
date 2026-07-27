# SESSION 2985 — Canonical Briefing v1 (LLM briefing + citations on canonical summary docs)

**Date:** 2026-07-26 evening (US/Denver)
**Merge:** `b281a0f03` — PR #3629
**Spec deliverable:** `6f6c4122-a98f-48c2-a8b3-ab687b44cbf6` (Donkey Betz workspace `b4503364-…`)
**Session shape:** PLAYBOOK-7.7.1 spec→ship, all 9 phases walked
**Rigby cycles:** 3 SIGN passes (T1 pass 1 REVISE / T1 pass 2 PROCEED / A2 PROCEED-TO-MERGE with 1 same-PR fold)

---

## Three-part summary

**What was done (plain English):**
Any canonical summary doc under `docs/research/domains/**/*canonical_summary*.md` now defaults to an LLM-generated **Briefing** view — five section cards (TL;DR / Decisions / State / Risks / Next Actions) with bullet-level citations that expand to show the source chunk. The old "wall of markdown" is still one tab click away. PR #3629, sha `b281a0f03`.

**How it improves the platform (before / after):**
- **Before:** Clicking a canonical summary from Home → Research Arcs opened a scrolled wall of markdown; readers had to scan the whole file to find decisions, risks, or next actions.
- **After:** Same click opens a 5-card briefing with citations; readers see the shape in seconds and can drill into the raw markdown when they want. Any bullet whose citations don't map to a retrieved chunk collapses to "Insufficient support in canonical docs" — the LLM cannot ship an unbacked claim.

**Next-session first action:**
Open the browser visual check at `http://127.0.0.1:8000/workspace` → Home tab → click any hanging arc entrypoint that resolves to a canonical summary → confirm the Briefing tab defaults, bullets render with Evidence expandables, Refresh works. If the check surfaces any UX gap, open a small follow-up. If the check is clean, open the next arc.

---

## Session timeline

| # | Event | Artifact |
|---|-------|----------|
| 1 | Session open — S2985 first-action was "wait for Chris" | HEAD `9235cb7de` after S2984 arc |
| 2 | Chris interrupt — Rigby had dispatched a runaway `claude_code_tool` job for the same spec | Task ID `59ad471e-…` |
| 3 | Killed runaway PID `55024` (parent) + `55278` (child); credit-burn stopped | `ps aux \| grep claude` verified clean |
| 4 | Chris handed spec: deliverable `6f6c4122-…` "Canonical Summary Briefing UI" | Body loaded via ORM (`content` field) |
| 5 | Phase 0/1 pre-code sampling (Claude-local) — 4 reference surfaces mapped | search_embeddings@798, doc_content_view@1235, DocumentViewer.tsx, HomeTab.tsx |
| 6 | Phase 5 Chris-facing framing — one decision surfaced ("v1 only vs v1+v2 bundle") | Chris ratified "Ship v1 only" |
| 7 | Phase 3 T1 SIGN pass 1 — Rigby returned REVISE with 4 gap items + 4 zoom-out folds | 11 tool_runs cited |
| 8 | Phase 3 T1 SIGN pass 2 — gap completion; Rigby returned PROCEED with 4 refinements | 4 additional citations |
| 9 | Refinements folded: `/api/repo/` namespace / single-LLM structured JSON / redis_lock reuse / file_path unindex as v2 future_trigger | All Z1/Z2/Z3 invariants baked in |
| 10 | Phase 6 implement — 6 files, +1219/−3 lines, 14 tests green | Commit `ad266c0a0` |
| 11 | Phase 7 A2 SIGN — Rigby returned PROCEED-TO-MERGE with 3 folds (ZO1 same_pr_mitigatable / ZO2 + ZO3 future_trigger) | 7 tool_runs cited |
| 12 | ZO1 fold shipped — `_parse_and_validate` returns `(sections, llm_valid_json)`; malformed-JSON test pinned | Commit `a79d28de1` |
| 13 | Phase 8 merge — PR #3629 → `b281a0f03` via `gh pr merge --admin --squash --delete-branch` | Squash-merge |
| 14 | PLAYBOOK-7.4.4 recycle — `make recycle-all` clean at `sha=b281a0f03762` | recycle_events.jsonl written |

---

## Files touched (merged PR)

**Backend (new):**
- `core/services/canonical_briefing.py` — orchestrator + scope-filtered retrieval + LLM call + cache + lock (~470 lines)
- `core/views_repo_canonical_briefing.py` — `POST /api/repo/canonical-briefing/` (~140 lines)
- `core/tests/test_canonical_briefing.py` — 15 tests

**Backend (edited):**
- `core/urls.py` — route wired next to `/api/repo/research/arcs/`

**Frontend (new):**
- `frontend/src/components/platform/CanonicalBriefing.tsx` — section cards, expandable Evidence, Refresh, fallback-to-Raw

**Frontend (edited):**
- `frontend/src/components/platform/DocumentViewer.tsx` — `viewerMode` state, tab strip gated by `BRIEFING_ELIGIBLE_PATTERN`, +64 lines

Frontend chunk grew `DocumentViewer-*.js` from ~4 KB → 10.83 KB.

---

## Rigby cycle discipline (PLAYBOOK-7.7.2)

**T1 pass 1** — 8 file:line citations, 4 gaps flagged honestly (C4 index / D1 structured-output helper / D2 URL namespace / D3 cache-lock helper), 4 zoom-out folds surfaced. Verdict REVISE.

**T1 pass 2** — 6 more citations, all 4 gaps closed with concrete recommendations. Verdict PROCEED once refinements folded.

**A2** — 7 citations verifying implementation matches T1-agreed shape. 3 zoom-out concerns: ZO1 (silent JSON-parse degradation, same_pr_mitigatable), ZO2 (60s lock TTL, future_trigger), ZO3 (file_path unindexed, future_trigger — already documented in service docstring). Verdict PROCEED-TO-MERGE.

Every cycle passed the tool_runs non-empty gate (`feedback_verify_rigby_tool_runs_before_trusting_sign`). No rubber-stamping.

---

## Fold classifications (PLAYBOOK-6.10.8)

| Fold | Origin | Classification | Disposition |
|------|--------|---------------|-------------|
| Z1 no-hallucination invariant | T1 pass 1 | same_pr_mitigatable | Shipped: `INSUFFICIENT_SUPPORT_MSG` at service layer + `test_bullet_without_valid_citation_collapses_to_insufficient_support` |
| Z2 UI isolation | T1 pass 1 | same_pr_mitigatable | Shipped: `BRIEFING_ELIGIBLE_PATTERN` regex + `viewerMode` state + fallback-to-Raw button |
| Z3 v2-ready scope.root | T1 pass 1 | same_pr_mitigatable | Shipped: endpoint accepts + echoes `scope.root` even though v1 only serves arc-folder |
| Z4 T1 tool-gap re-issue | T1 pass 1 | blocking | Resolved by T1 pass 2 |
| C4 file_path unindexed | T1 pass 2 | future_trigger | Documented in service docstring; v2 migration owed when scope broadens |
| D1 no json_schema helper | T1 pass 2 | same_pr_mitigatable | Shipped: reuse `response_format={"type":"json_object"}` pattern from `thinking_agent.py:670` |
| D2 URL namespace | T1 pass 2 | same_pr_mitigatable | Shipped: `/api/repo/canonical-briefing/` (matches `/api/repo/research/arcs/`) |
| D3 cache-lock helper | T1 pass 2 | same_pr_mitigatable | Shipped: `acquire_singleton_lock` / `release_singleton_lock` from `core/services/redis_lock.py` |
| ZO1 malformed-JSON silent degradation | A2 | same_pr_mitigatable | Shipped as second commit (`a79d28de1`): `_parse_and_validate` returns `(sections, llm_valid_json)`; payload flag |
| ZO2 60s lock TTL | A2 | future_trigger | Bump if LLM P99 latency approaches 60s; not likely at current scope |
| ZO3 file_path unindexed | A2 (duplicate of C4) | future_trigger | Same disposition as C4 |

**Count:** 8 same_pr_mitigatable (all shipped) + 2 future_trigger (documented + logged for v2) + 1 blocking (resolved) = 11 folds.

---

## Constitutional discipline (PLAYBOOK-7.7.1)

All 9 phases walked in order — no phase-skip, no abort-early:

| Phase | Artifact |
|-------|----------|
| 0 Verify existing implementation | Pre-code sample of 5 reference surfaces (Claude-local reads) |
| 1 Pre-code sampling | search_embeddings signature confirmed, DocumentViewer + HomeTab lazy-load pattern confirmed |
| 2 Implementation analysis | Reuse-first plan; no parallel viewer, no new LLM helper |
| 3 T1 SIGN | 2 Rigby passes; PROCEED after 4 refinements folded |
| 4 Chris D-verdict on T1 | Route was: Claude+Rigby agree first, present Chris ≤1 decision → Chris ratified "Ship v1 only" |
| 5 Chris-facing framing (7.7.3) | Plain english "do we lose anything? / is it more work later?" — both answered "no" |
| 6 Implement | 6 files, 15 tests, 3 zoom-out invariants baked in |
| 7 A2 SIGN | Rigby PROCEED-TO-MERGE with 1 same-PR fold (ZO1) |
| 8 Ship | `gh pr merge --admin --squash --delete-branch` |
| 9 Close ceremony | (this handoff + wrapper pin + 00-START refresh + docs cascade PR) |

Also honored:
- **feedback_engineering_bias_over_audit** — this session was net-new engineering; no audit substrate iteration.
- **feedback_local_truth_no_production** — `make recycle-all` is the deploy step; no production observation window.
- **feedback_recycle_after_merge** — `make recycle-all` (not `celery-recycle`) ran because frontend was touched.
- **feedback_verify_rigby_tool_runs_before_trusting_sign** — every SIGN verdict pinned to tool citations.
- **feedback_zoom_out_ask_per_rigby_sign** — T1 and A2 both included explicit zoom-out asks; 7 substantive folds surfaced.
- **feedback_claude_rigby_agree_first_chris_yes_no** — Chris saw one decision ("ship v1 vs bundle v1+v2"), one yes/no.
- **feedback_plain_english_decision_framing_for_chris** — no jargon in the decision surface (no "Fold C 3rd trigger" phrases).
- **feedback_commit_wrapper_pin_bump_at_close** — wrapper pin bump will be included in this close cascade PR.

---

## Chris still owes

**Browser visual check** at `http://127.0.0.1:8000/workspace` → Home tab:
1. Click any hanging arc entrypoint that lands on a canonical summary file (e.g., `docs_content_audit` arc → `2899_docs_content_canonical_summary.md`)
2. Confirm the Briefing tab is the default (Sparkles icon)
3. Confirm bullets render with an "Evidence (N)" toggle
4. Click Evidence — should expand to show the citation path + snippet
5. Click "Raw" tab — should show the underlying markdown
6. Click "Refresh" on the Briefing tab — should force cache bypass (server hit visible in logs)
7. Open a non-canonical doc (e.g., `docs/canon/*.md` from Knowledge tab) → confirm NO Briefing tab appears (Z2 isolation)

---

## Open follow-ups for S2986+

- **v2 (`/docs`-wide scope toggle)** — deferred per Chris D-verdict. Pure additive: one dropdown in `CanonicalBriefing.tsx` + one default exclude-globs list. ~1-2 hr.
- **`Document.file_path` index** — add `models.Index(fields=['file_path'])` migration when v2 broadens scope. `startswith()` on unindexed CharField at `/docs`-wide scope could scan the whole embedding table.
- **ZO2 lock TTL bump** — if LLM P99 latency approaches 60s under load, bump `LOCK_TTL_SECONDS`.
- **Chris browser visual check** on this session's PR3 (this session's ship) + carryovers from S2984 (arcs section + PR2 Home tab layout).
- **Systemic auth-XHR JSON envelope middleware** — S2984 fold still open; not blocking here.
- **Phase B Theme Signals** (Why-now LLM summarizer / who-benefits-who-loses / sub-tab localStorage) — S2978/S2980 carryovers.
- **Rigby memory-store cap investigation** — S2979 carryover.
- **Rigby Tool Gap Ledger #13** — S2982 carryover (`AgentExecution.celery_task_id` uniqueness).
- **Rigby claude_code_tool safeguards** — new future_trigger from this session. The runaway that opened S2985 was Rigby's `claude_code_tool` firing against a spec that explicitly said "Do not use claude_code_tool." Consider: (a) tool-surface pre-check that scans the spec body for that literal string, (b) opt-in flag on the deliverable, (c) rate-limit or budget cap on `claude_code_tool` invocations per session. Not urgent — a one-shot incident — but worth a Ledger entry.

---

## HEAD at close

`b281a0f03` before docs cascade; will be `<cascade sha>` after cascade merges.
