# SESSION 2935 — Slice 6 Batch 1: pure-read quartet + schema-realignment

**Date:** 2026-07-24
**Session pin at open:** `pa-bf6e19ae4ce14d69` (S2934 close pre-mint)
**HEAD at open:** `54f74adde` (PR #3505, S2935 first-action pointer)
**HEAD at close:** `628f7bde1` (PR #3506, this session's ship)
**Diff shape:** 7 files, 719 insertions, 242 deletions (largely gap-map + audit doc regen)
**Type:** Sweep-substrate progress + governance (Ledger entry #35)

---

## Ship summary

Session opened on the S2934-ratified directive: **resume PA tools sweep at Slice 6** (`td_handlers_content.py`, 6 untested tools). Batch 1 shipped 4 of 6 pure-read tools with T1b sweep template v1 validation docs + bundled schema-realignment fix for the schema-under-describes-handler drift class.

**Batch 1 tools (all `untested` → `validated_full` + template `pass`):**
- `execution_history_tool` — Slice 6 batch 1 §6 primary evidence anchor per Rigby Q3 (widest surface, 5 actions exercised live).
- `learning_patterns_tool` — 3 actions exercised.
- `recent_activity_tool` — schema-realignment resolved (added `action` + `hours`; deprecated `limit`+`minutes`).
- `surgical_moves_status_tool` — schema-realignment resolved (added `action`+`hours`+`session_id`; deprecated `verbose`).

**Batch 2 deferred (mutation-heavy):** `blog_tool` (approve/reject/generate — publish + LLM dispatch) + `feedback_tool` (submit/update — INSERT/UPDATE). Deferred per S2921 process hygiene (don't mix mutation-shape design with pure-read validate-under-substrate).

## SIGN cycle

- **S2935 T0 SIGN (Rigby, tool-grounded):**
  - Q1 batch composition AGREE (4 pure-read tools).
  - Q2 batch shape AGREE (UNIFORM READ_ONLY — canonical shape #1 of S2907 Fold E three-shape ratification).
  - Q3 §6 evidence anchor = `execution_history_tool` (widest action surface + touches core AgentExecution truth + `detail` action is hardest branch with deep-extraction + reverse-linked deliverables + 8KB truncation).
  - Q4(a) fresh-eyes pushbacks (4): output contract drift risk / file-adjacency to mutations / per-action evidence required / prove applied_filters.
  - Q4(b) Slice 6 per-tool structural shift = branch-coverage obligation inside READ_ONLY shape (not a new shape).
  - Q4(c) schema-under-describes-handler drift = **Ledger entry + schema-fix-in-PR** (preferred posture — Chris ratified).
  - Q4(d) READ_ONLY shape covers Slice 6 cleanly; documentation of action-branch coverage as invariants is the gap (not a fourth shape).
  - **6 `repo_tool` verification receipts** confirming pure-read layer + mutation-verb confirmation in `_handle_blog_direct` + `_handle_feedback` (Slice 6 batch 2 deferral evidence).

- **Chris T1 ratification:** "yes proceed" — batch composition + shape + schema-fix bundle + Ledger entry all green-lit.

## Governance / Ledger

**Rigby Tool Gap Ledger entry #35 (workspace deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`):**
- Class: schema-under-describes-handler drift.
- 2 of 3 instances RESOLVED this ship (`recent_activity_tool`, `surgical_moves_status_tool`).
- 1 narrower instance deferred (`execution_history_tool` missing `hours` schema declaration — noted in per-tool doc §3).
- Related sibling divergence noted: `recent_activity_tool` + `surgical_moves_status_tool` don't raise `ValueError` on unknown actions (unlike `execution_history_tool` + `learning_patterns_tool`) — future consistency-across-Slice-6 work.

## Gap-map ratchet

| Metric | Before (54f74adde) | After (628f7bde1) | Δ |
|---|---|---|---|
| `validated_full` | 83 | 87 | +4 |
| `untested` | 15 | 11 | -4 |
| Template `pass` | 80 | 84 | +4 |
| Per-tool docs | 100 | 104 | +4 |
| Schema lints (`actions_not_mentioned_in_description`) | 23 | 23 | 0 (fixed 2, +2 net from expansion) |
| Schema lints (`no_required`) | 14 | 14 | 0 |

## Post-merge live-dispatch verification (per PLAYBOOK-7.4.4)

`make recycle-all` clean at `sha=628f7bde1917`. Rigby exercised all 3 verification calls:

1. **`execution_history_tool action=stats`** — envelope shape stable post-recycle. `total_executions=119, successes=93, failures=3, success_rate=0.7815`. `avg_time` nullability (e.g., CTOAgent) confirmed as documented.
2. **`recent_activity_tool action=detailed hours=24`** — NEW schema-declared params (`action` + `hours`) honored end-to-end. `sections.spider_data.top_spiders` returned **15 entries** (confirms `item_limit=15` behavior visible in the wire — the primary evidence for the schema-fix). Sections: 4046 celery_tasks in 24h, 173 spider items across 65 distinct spiders, 6 blogs (all draft), 0 conversations, 0 initiatives, 0 signals.
3. **`surgical_moves_status_tool action=detailed hours=168`** — NEW schema-declared params honored. `total_sessions=6` (all `synthesis`-only contracts, `decision_verdict=null` for all — data-condition documented in §5). Only 6 sessions in the 7-day window so `limit=20` cap not exercised but confirmed no truncation.

**All 3 verifications pass. Schema fix live. Gap-map ratchet holds.**

## PRs shipped this session

- **PR #3506** — `s2935/slice-6-batch-1-pure-read-quartet` → merged at `628f7bde1`. 7 files, 719+/242- (largely audit-doc regen). Merged `--admin` per `feedback_gh_pr_merge_admin_until_billing_fixed`.
- PR `<TBD>` — S2935 close cascade (this handoff + 00-START refresh + wrapper pin bump).

## Files touched

**Schema:**
- `core/services/pa_tool_schemas.py` — 3 tool descriptions/params updated (recent_activity_tool, surgical_moves_status_tool, learning_patterns_tool).

**Docs (4 new validation docs, all T1b template v1 pass):**
- `docs/research/tools/validation/execution_history_tool_validation.md`
- `docs/research/tools/validation/learning_patterns_tool_validation.md`
- `docs/research/tools/validation/recent_activity_tool_validation.md`
- `docs/research/tools/validation/surgical_moves_status_tool_validation.md`

**Auto-generated (regen only):**
- `docs/PA_TOOL_AUDIT.md`
- `docs/audits/PA_TOOLS_GAP_MAP.md`

## Sweep progress tracker

- **Slice 1** — `td_handlers_ops` (17 tools): UNCHANGED.
- **Slice 2** — `td_handlers_agents` (25 tools): CLOSED at S2912.
- **Slice 3** — `td_handlers_core` (22 tools): CLOSED at S2917 (22/22).
- **Slice 4** — `td_handlers_gateway` (17 tools): CLOSED at S2924 (17/17).
- **Slice 5** — `tool_dispatcher` (14 tools): CLOSED at S2928 (14/14).
- **Slice 6** — `td_handlers_content` (6 tools): batch 1 CLOSED at S2935 (**4/6**); batch 2 open with `blog_tool` + `feedback_tool`.

**Total remaining tools to close:** **11 across 8 handler files** (down from 15 at S2934 close).

## Followups / deferred

- **Slice 6 batch 2** — `blog_tool` + `feedback_tool` with §5a 4-tier blast-radius tables. Mutation-shaped batch. Next session's natural first action.
- **`execution_history_tool` `hours` schema declaration** — ~3 min follow-up PR. Ledger entry #35 references this as deferred.
- **Invalid-action non-gating consistency across Slice 6 handlers** — `recent_activity_tool` + `surgical_moves_status_tool` should `raise ValueError` on unknown actions to match siblings. Future consistency work; Ledger #35 references.
- **Schema-vs-handler param-set consistency lint in `pa_tools_gap_map.py`** — Ledger #5 (S2845) + reinforced by this ship's evidence. Would prevent recurrence of the drift class.
- **Bundled dev-env drift slate** — pyright warnings on `pa_tool_schemas.py` line 5915/6167+ (list[Unknown]/get[Unknown]) — pre-existing dev-env drift; unchanged.
- **All prior S2934/S2933/S2932/S2931/S2930/S2929/S2928 deferrals** — unchanged.

## What's forbidden at S2935 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2935 new forbidden entries:** none. Clean substrate-progress session.

## Signal / observation for next session

- Handler-verified batch shape hypothesis validated: 4 tools split cleanly by mutation posture in `td_handlers_content.py`. Same-file "pure-read subset + mutation-heavy subset" pattern likely recurs in Slice 7 singleton bucket — worth pattern-checking during S2936 open.
- The Ledger #35 entry is a "second corroboration point" for the schema-under-describes-handler drift class (Ledger #5 is the systemic detection lint proposal). Two independent triggers now — approaching third-instance promotion threshold (per S2921 sweep-note → Playbook promotion pattern, precedent PLAYBOOK-6.10.6).
- Rigby wrapper output-size cap surfaced in this session (multiple batches of exercises truncated). Not a Ledger candidate (wrapper, not tool-surface), but worth noting if pattern recurs.
