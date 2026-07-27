---
title: "SESSION 2994 — Findings-surface v2 item #6: FindingsTab finding_type nudge for decision_evidence"
session: 2994
date: 2026-07-27
type: engineering_close
merge_shas:
  - "ddeb9e19f"
prs:
  - 3655
related_arcs:
  - "findings-surface v2 (S2991 → S2992 → S2993 → S2994)"
consumes:
  - "S2993 spec_prompt_shape metadata"
  - "S2992 finding_type axis"
---

# S2994 — FindingsTab surfaces finding_type + evidence-nudge

**Status:** CLOSED. One feature PR merged. Recycle-all clean at `sha=ddeb9e19f46c` (frontend rebuild included per `feedback_recycle_after_merge`).

## What shipped

**PR #3655 (`ddeb9e19f`) — v2 item #6: `FindingsTab` differentiates decision_evidence findings in the UI.**

`frontend/src/pages/workspace/tabs/FindingsTab.tsx`:

1. **`finding_type` in the Finding TS type.** New `FindingType = 'decision_evidence' | 'executable' | 'unknown'` union.

2. **`FindingTypeBadge` component.** Renders amber "Evidence" badge for decision_evidence, blue "Executable" badge for executable, hidden entirely for `unknown` (no signal added when the classifier couldn't determine). Rendered inline with StatusBadge/ConfidenceBadge on every row.

3. **`finding_type` filter dropdown.** Added next to the existing status / source / min-confidence dropdowns. Backend already supported `?finding_type=...` (S2992 shipped it).

4. **Decision-evidence action-side treatment** (only for `status='open'` + `finding_type='decision_evidence'`):
   - **Tiny inline helper** above the action buttons: "Decision record — verify boundary before re-audit." (10px, amber/80, right-aligned, single-line).
   - **Button relabel:** "Send to Rigby" → "Verify evidence" with amber styling.
   - **Tooltip:** "Create a re-audit spec to confirm this boundary still holds".

5. **Toast copy differentiation.** After dispatch, the ok-toast names the deliverable variant based on the finding_type sent: `"Evidence-capture deliverable created (…)"` vs `"Engineering spec deliverable created (…)"`. Same-PR mitigation of Rigby T1 SIGN zoom-out fold (c) — closes the mental-model loop between send action and downstream deliverable shape.

**No backend changes.** All axes (`finding_type` in serializer, `?finding_type=` filter, `spec_prompt_shape` in Deliverable.metadata) shipped in S2991/S2992/S2993.

## SIGN discipline (PLAYBOOK-7.7.2)

- **T1 SIGN** — Rigby fetched the S2993 A2 SIGN evidence deliverable (`e51207dc-…`) content via `deliverable_tool` and confirmed the proposed "Verify evidence" UI copy matches actual shipped output (goal="Record that F-VIP-1 and F-C-VIP-1 are the same issue lineage…", all AC read as verification steps like "Open doc, locate strings, confirm statements"). She AGREE'd (c) Both nudge shape (label swap + inline helper) with constraint "keep primary CTA footprint stable" — kept the button at the same position/size, only swapped label + color. DISAGREE'd (a) "filter is premature" — 139/900 is big enough to filter usefully. DISAGREE'd (b) "badge alone is enough" — badge alone doesn't fix the misframe problem. AGREE'd (c) "close the loop with toast copy" — that's the same-PR mitigation shipped.

- **A2 SIGN** — Post-merge, Rigby independently verified the substrate via `orm_inspect_tool`:
  - `count_by(finding_type)` → `{unknown: 623, decision_evidence: 139, executable: 138, total: 900}` (matches pre-merge dry-run exactly)
  - `filter(Deliverable, metadata__has_key='spec_prompt_shape', limit=3)` → 3 rows from S2993 A2 SIGN, verifying the toast-copy branch has real data to differentiate on (1× evidence_capture, 2× engineering).

## v2 sequence status (post-S2994)

- [x] #1 close_mode taxonomy — S2991
- [x] #2 finding_type classifier + backfill — S2992
- [x] #3 spec-generator prompt branching on finding_type — S2993
- [x] #5 orm_inspect_tool allowlist (ORM half) — S2991 (`web_fetch_tool` cookies deferred)
- [x] #6 Rigby-SIGN nudge in UI for `finding_type=decision_evidence` — **S2994 (this handoff)**
- [ ] #4 staleness detector at ingest — carry-forward (S2994's original Option B)
- [ ] #7 F-A2-equivalent for downstream consumers — carry-forward
- [ ] #8 wire-through smoke-check AC for half-wired findings — carry-forward

**#6 was the "quick UI win" complement to #3.** With prompt-branching + UI-nudge shipped, the human-loop is coherent: Chris sees the type distinction on every row, filters when he wants, and the send-to-Rigby action label matches what he'll get back. #4 (staleness detector) is the natural next opener — Chris ratified "A then B" at S2994 open.

## Zoom-out folds (PLAYBOOK-6.10.8)

**Fold A (Rigby A2 zoom-out (a)) — `informational`, already mitigated.** Amber-only visual convention risk for color-blind / theme drift. Mitigation already shipped: badges carry text ("Evidence" / "Executable"); button carries text ("Verify evidence" / "Send to Rigby"); inline helper is text. Color is redundant reinforcement, not the sole channel. No follow-up needed.

**Fold B (Rigby A2 zoom-out (b)) — `future_trigger`.** Inline helper renders on every open decision_evidence row (up to 139 with unfiltered view). Rigby judged right-sized given misframe cost but flagged: if noisy, next step is show-on-hover / show-once-per-session. Not blocking; watch for Chris "the helper is noisy" signal or 2nd independent trigger.

**Fold C (Rigby A2 zoom-out (c)) — `future_trigger`.** Deliverable-tab badge on WorkspacePageNew would close the long-term mental-model loop — after Chris navigates away from FindingsTab and returns to the deliverable list, he'd still see "Evidence-capture" vs "Engineering spec" distinction. Natural extension of #6. Not blocking; log as follow-on if the deliverables tab surfaces the workspace's briefing_action_items with a type facet.

**Fold D (Rigby A2 zoom-out (d)) — Rigby Tool Gap Ledger candidate.** Pattern: "backend semantics shipped → UI affordance missing → user intent mismatch risk." S2993 shipped the prompt branching; S2994 shipped the UI affordance one session later. The gap window (backend-ahead-of-UI) is a systemic risk shape that could recur on future finding_type-like axes. Logged.

## HEAD / recycle state

- `ddeb9e19f` — feat(s2994) PR #3655 (this session's feature PR)
- Recycle-all clean at `sha=ddeb9e19f46c` post-merge (frontend rebuild included; `feedback_recycle_after_merge` compliance).

## Files touched

- `frontend/src/pages/workspace/tabs/FindingsTab.tsx` — TS type, badge component, filter dropdown, decision_evidence action treatment, toast differentiation
- `core/templates/index.html` — Vite build manifest sync (auto-generated)

## Playbook rule exercise

- **PLAYBOOK-7.7.1** (Spec→Ship contract) — Flow B (00-START directive at S2993 close ratified Option A / item #6 as first S2994 opener). Framing → Rigby T1 SIGN → code → build check → PR → Rigby A2 SIGN → merge → recycle-all. No phase skipped.
- **PLAYBOOK-7.7.2** (SIGN evidence discipline) — T1 SIGN Ask #1 fetched the actual S2993 evidence deliverable content via `deliverable_tool` before I committed the UI copy. A2 SIGN independently verified substrate counts + deliverable metadata via `orm_inspect_tool`. Zero rubber-stamping across both cycles.
- **PLAYBOOK-7.7.3** (Chris-facing decision framing) — No new Chris decision this session; Option A directive already ratified at S2993 close.
- **PLAYBOOK-6.10.8** (fold classification) — 4 folds classified (A `informational` already mitigated; B `future_trigger`; C `future_trigger`; D ledger candidate).
- **PLAYBOOK-7.4.4** (recycle after merge) + S2978 refinement (`make recycle-all` for frontend diff) — Followed exactly. Frontend rebuild occurred (2303 modules transformed, 3.42s), Daphne restarted, dist synced.
- **`feedback_recycle_after_merge`** — Frontend diff explicitly triggered `make recycle-all` not `make celery-recycle`. UI is visible.
- **`feedback_zoom_out_ask_per_rigby_sign`** — Both SIGN cycles included zoom-out asks; A2 zoom-out surfaced Fold D (ledger candidate) and Fold C (deliverables-tab badge — natural next extension).
