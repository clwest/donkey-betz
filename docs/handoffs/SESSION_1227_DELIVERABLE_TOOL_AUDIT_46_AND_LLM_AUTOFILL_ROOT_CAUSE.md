# Session 1227 — Audit §4.6 deliverable_tool surface additions + LLM-autofill class-of-bug root cause

**Status:** Four-PR session, all stacked, all green-lit by Rigby end-to-end. Closes Session 1226 audit `e2964e4a-…` §4.6 items 1-5 in one continuous arc. Also surfaced — and root-caused — a generalizable LLM-autofill bug class that invalidated the audit's F3 diagnosis; captured as memory rule for the followup sweep PR.

**Date:** 2026-06-24 (UTC).
**Active conversation:** `pa-08bdd7c9b348415a` — same pin from Session 1226 close (via #2558 rotation). Carried 1227 open → close with no rotation; turn-count comfortably under threshold.
**Prior session:** [`SESSION_1226_RIGBY_PLATFORM_ACCESS_UNBLOCKING.md`](./SESSION_1226_RIGBY_PLATFORM_ACCESS_UNBLOCKING.md).
**Next session entry point:** Session 1228 — see 00-START-NEXT-SESSION.md "FIRST THING Session 1228".

## TL;DR

Session opened pointed at audit §4.6 — Rigby's audit deliverable `e2964e4a-…` named 5 tool-surface additions to `deliverable_tool` that turn future audits from "ORM archaeology" into "one tool call." All five shipped this session as a 4-PR stack:

1. **#2562** (PR1) — `list show_all=true` flag + `applied_filters` echo + `stats full_by_agent=true` (items 1+2 grouped).
2. **#2563** (PR2) — first-class `duplicates` action with the full audit-spec tuple per group.
3. **#2564** (PR3) — surgical `set_status` action with whitelisted `completed↔ready` transitions + reason field + audit trail.
4. **#2565** (PR4) — dry-run `normalize` action for alias-map drift detection.

**The big surprise** was inside PR1's verification: the audit's F3 finding ("default filter hides `blocked` + most `archived`, 148/300 workspace rows invisible") turned out to be a **misdiagnosis**. The visible symptom was real (152/300 today, was 180/300 at audit time) but the cause wasn't "blocked + archived hidden." A live DIAG log inside `_handle_deliverables` showed GPT-5.2 silently autofills every declared optional boolean schema param with Python `False`. That tripped the old `if has_init is not None:` check at line 1648 and filtered out every deliverable WITH an initiative attached. The "missing rows" exactly matched the WITH-initiative count.

Mid-PR2 verification then **caught a second instance of the same class** — GPT-5.2 autofills integer params with `0`, which made `deliverable_tool.duplicates` return 0 rows on every call until Rigby (correctly) flagged the bug and asked for a re-run. PR2 was patched to use a falsy-or-default pattern.

The class-of-bug is now documented as `feedback_llm_autofills_boolean_params_with_false.md` (extended to cover ints). Followup sweep PR queued in carryover.

**Bonus**: extracted `_AGENT_NAME_ALIASES` from `deliverable_factory` into a new shared module `core/services/deliverable_aliases.py` (Rigby D1 design call on PR4). The previous lockstep-via-comments contract between `deliverable_factory` and migration 0365 was a refactor hazard.

**Bonus²**: added the "Claude directs, Rigby executes, Claude verifies" collaboration shape to CLAUDE.md (PR1 commit `b473f910`) — codifies the workflow pattern Chris had been operating in for several sessions but that wasn't in the project's doc surface.

## Session Manifest

### PRs opened (4 total, all stacked, all open at session close)

| # | Title | What |
|---|---|---|
| **#2562** | `feat(session-1227): deliverable_tool visibility — has_initiative autofill safety + show_all + applied_filters + full_by_agent` | PR1 — addresses audit §4.6 (1)+(2). Fixes `has_initiative` truthy-only check (Python `False` = autofill, ignored). String `'false'` is the explicit no-init sentinel. Adds `show_all` bypass. Adds `applied_filters` echo on list + search. Adds `full_by_agent=true` on stats with `by_agent_truncated` flag. 12 new tests (18 with the updated Session 1226 test file). Stacks `b473f910` (CLAUDE.md workflow rule) + `d977154d` (code). |
| **#2563** | `feat(session-1227): deliverable_tool first-class duplicates action (stacks on #2562)` | PR2 — addresses audit §4.6 (3). New `duplicates` action returning per-group `{count, first_created_at, last_created_at, last_7d_count, agent_name_distribution, status_distribution}`. `group_by` whitelist of `['title']` / `['title','agent_name']` / `['title','category']`. `min_count`/`limit`/`window_days`/`exclude_archived` all use falsy-or-default to neutralize LLM int autofill. 21 new tests. |
| **#2564** | `feat(session-1227): deliverable_tool set_status — surgical, audited completed↔ready flip (stacks on #2563)` | PR3 — addresses audit §4.6 (4). Tight scope per Chris's earlier design call: ONLY `completed↔ready`. `reason` required on completed→ready (the unblock direction), optional on ready→completed, max 500 chars. Reuses existing `deliverable_status_signals.py` post-save signal — extended additively to consume optional `instance._transition_context` (with `delattr` after consume to prevent leak to subsequent saves). Event payload now includes `metadata.ctx.{reason, actor_user_id, trace_id, source}` + `DeliverableEvent.user_id`. 12 new tests; 32 existing rework-signal tests still pass (additive change). |
| **#2565** | `feat(session-1227): deliverable_tool normalize — dry-run alias-map sweep (stacks on #2564)` | PR4 — addresses audit §4.6 (5, optional). Extracts `_AGENT_NAME_ALIASES` to a shared module `core/services/deliverable_aliases.py`. Belt-and-suspenders write safety: dry_run defaults to True; writes require BOTH `dry_run=false` AND `confirm=true`. Workspace-scoped by default; `show_all=true` for global. Field allowlist (`agent_name` only in v1). Structured log line per write — no per-row DeliverableEvent. 15 new tests. |

**Total**: 7 files changed (PR1) + 5 files (PR2) + 6 files (PR3) + 7 files (PR4) = **+1,622 / −82 lines** across 4 PRs, **66 new tests** that all pass together.

### Carryover items NOT touched this session (intentional)

- **Outreach daily beat first-fire watch** — scheduled 2026-06-24 13:30 UTC, already past by session open. Carried into 1228.
- **Anthropic credit refill + claude_code_tool revert from OpenAI workaround** — Chris-side; OpenAI fallback (#2556) still active.
- **Operator Edge Friday-1 dry-run** — 2026-06-26 (Friday). Calendar-driven, carried.
- **CI billing fix** — Chris-side, carried.
- **Watchdog #5 24-48h re-run** — optional, carried.
- **Audit §4.4 P1 upstream `research_agent.py:1103` fix** — the prompt-leak title-truncation bug. PR2's duplicates output today shows these prompt-leak clusters are still the heaviest duplicates in DBZ (count=20 + count=9 ResearchAgent groups). Carried — but now queryable in one tool call.
- **Outreach tone tweak nice-to-haves** — Rigby's Session 1225 review items, carried.

### Memory rules + project-doc updates

| File | Why |
|---|---|
| `feedback_claude_directs_rigby_then_verifies.md` (new memory) | Codifies the workflow shape Chris named at PR1 open: Claude directs, Rigby executes via PA tools, Claude verifies independently via ORM/git/file Read. Supersedes the older "Claude codes, Rigby ops" split. |
| `feedback_llm_autofills_boolean_params_with_false.md` (new memory) | Class-of-bug rule: GPT-5.2 in function-calling mode autofills declared optional boolean params with `False` and integer params with `0`. Handler checks of the form `if x is not None:` then fire on the autofill, applying filters the caller never requested. Fix patterns include truthy-only checks and falsy-or-default. Diagnostic recipe included. |
| `CLAUDE.md` "Working with Rigby" section | Added the "Claude directs / Rigby executes / Claude verifies" three-step contract with work-type splits and override conditions. The rule was Chris's explicit ask early in the session. Committed in `b473f910` (part of PR #2562). |

## Arcs

### Arc 1 — Session-open mode shift (CLAUDE.md update + workflow rule)

Chris's framing at session open: "what we have been doing is you tell Rigby exactly what to do and then you verify that she's doing it." That pattern hadn't been captured in the docs. Saved as memory `feedback_claude_directs_rigby_then_verifies.md` and added a new section "Collaboration shape" to CLAUDE.md's "Working with Rigby" block. Committed as the first commit of PR1 (`b473f910`) so the doc + the first PR using that flow shipped together.

Concrete consequence for the rest of the session: every meaningful design judgment (D1-D6 on each PR) was routed through Rigby BEFORE coding. The diff landed on a decision she'd already signed off on. She also did the final end-to-end verification pass on each PR before commit + push.

### Arc 2 — PR1 + the F3 misdiagnosis root-cause

PR1 was originally framed as "add `show_all=true` + `applied_filters` echo to close audit F3." Mid-implementation I tried to reproduce the audit's 148/300 hidden-rows claim and couldn't — the handler code I was reading had no default status filter. Rigby's reproduction showed 180/300 vs ORM 300 — the gap was real but the 152 audit number was just from a different point in time.

Added a temporary `[deliverables] DIAG payload=...` log line, restarted the PA worker, asked Rigby to re-run. The actual payload GPT-5.2 was passing:

```python
{'has_initiative': False, 'orphans': False, 'status': '', 'agent': '',
 'category': '', 'type': '', 'workspace_id': '<DBZ>', 'limit': 1,
 'offset': 0, 'action': 'list'}
```

GPT-5.2 autofills every declared optional boolean with Python `False`. The handler's `if has_init is not None:` gate at line 1648 fired and applied `qs.filter(initiative_id__isnull=True)` — silently hiding all 120 deliverables with an initiative attached. Tool returned 180 (matches ORM count WITHOUT initiative); ORM truth was 300 (matches with-initiative + without-initiative).

The audit's F3 finding ("blocked + most archived hidden") was correct symptom, wrong cause. Fix shipped in PR1 with a truthy-only check matching the existing `orphans` pattern: Python `False` = autofill, ignored. String `'false'` = explicit sentinel for "deliverables without initiative." Reverted the diag log; saved the bug class as a memory rule.

### Arc 3 — PR2 catches the second instance (int autofill)

PR2's first end-to-end verification run came back with `count=0` and `total_groups_above_threshold=6` on a default `duplicates` call. Rigby flagged it clearly: "limit=0 in applied_filters echo — almost certainly LLM autofill." Confirmed via PA log: GPT-5.2 was passing `limit=0` and `window_days=0` even when the user (Rigby) didn't mention either.

Fix folded into PR2 in the same session: `limit = min(int(payload.get('limit') or 50), 200)` instead of `payload.get('limit', 50)`. Falsy-or-default pattern. Same fix applied to `window_days` and `min_count`. Three new tests in `IntAutofillSafetyTests` cover the pattern. Re-verified end-to-end: 6 duplicate groups returned, top two were the ResearchAgent prompt-leak clusters that PR #2557 (Session 1226) partially addressed but the upstream fix at `research_agent.py:1103` still hasn't shipped.

**Lesson**: the LLM autofill class affects BOTH bool and int param types. Schema description tightening alone won't fix it — the code-level falsy-or-default check is the durable fix. Followup sweep PR queued (see Carryover).

### Arc 4 — PR3 surgical set_status, reusing existing signal infrastructure

Before designing, surveyed the existing `core/signals/deliverable_status_signals.py` post-save signal (Session 1095). It already wrote `DeliverableEvent(event_type='status_transition', metadata={'from','to','direction'})` for every status change. Rather than writing a parallel event row, PR3 extended the signal additively to consume an optional `instance._transition_context` dict — handler stashes `{reason, actor_user_id, trace_id, source}` before save, signal namespaces under `metadata.ctx`, populates `DeliverableEvent.user_id`, then `delattr`s the attribute to prevent leak to subsequent saves on the same instance (Rigby D3 nuance).

Rigby tightened my D5 proposal (id-OR-title lookup) to id-first with title-only allowed when it resolves to exactly one row — title is unsafe in a duplicates-heavy workspace, which PR2 just made trivially queryable.

End-to-end verification flipped her own audit deliverable `e2964e4a-…` through the full cycle: completed → ready (with reason) → completed (no reason needed). Event payload confirmed; ephemeral context did not leak. Round-tripped back to starting state so the data is clean.

### Arc 5 — PR4 shared aliases module + belt-and-suspenders write safety

PR4 had two notable structural decisions:

1. **Source-of-truth restructure (Rigby D1)**: extracted `_AGENT_NAME_ALIASES` from `deliverable_factory.py` into `core/services/deliverable_aliases.py`. The factory now imports + re-exports. Migration 0365 stays as the historical-cleanup record. Future alias additions update only the shared module + a one-time cleanup migration (if rows hold the variant). The previous lockstep-via-comments contract between the factory and migration 0365 was a refactor hazard — anyone touching factory internals could drift the map.

2. **Belt-and-suspenders write safety (Rigby D4)**: `dry_run=True` is the default. Writes require BOTH `dry_run=false` AND `confirm=true`. Either alone keeps the call as preview. This is explicit protection against GPT-5.2 autofilling `dry_run=false` (which it would, per the Arc 2 finding) — without the `confirm=true` second factor, the LLM could silently flip preview to write.

End-to-end verification showed 0 rows would change in either workspace or global scope today, confirming migration 0365 + write-time enforcement #2560 are holding. The tool is in place for any future drift the next audit catches.

## Behavioral invariants post-Session-1227

For ops monitoring (Rigby's lane):

1. **`deliverable_tool action=list` returns full workspace results without LLM-autofill filtering.** Pre-PR1: returned ~180/300 due to silent `has_initiative=False` autofill. Post-PR1: returns the full 300. The `applied_filters` field in every list response shows exactly which filters fired — if a response is missing rows the caller expected, check `applied_filters` first.
2. **`deliverable_tool action=duplicates` returns up to 50 (default) duplicate groups per call.** Each group has the audit-spec tuple. `total_groups_above_threshold` shows how many groups exist above the (default 2) min_count even if pagination capped the response.
3. **`deliverable_tool action=set_status` is the audited path** for `completed↔ready` flips. Other transitions still work via `update` but are not whitelisted and not audited. Every set_status write produces a `DeliverableEvent(source='deliverable_tool.set_status')` with full `metadata.ctx`.
4. **`deliverable_tool action=normalize` is dry-run by default.** Writes require BOTH `dry_run=false` AND `confirm=true`. Per a fresh PA worker, the global sweep today reports 0 rows affected; any non-zero finding in the future is real drift.
5. **`_canonicalize_agent_name` and `_AGENT_NAME_ALIASES` re-export from `deliverable_factory` continue to work** — backwards-compatible alias to `core/services/deliverable_aliases`. New callers should import from `deliverable_aliases` directly.

## Rollback levers

| PR | Lever | When to use |
|---|---|---|
| **#2562** | Comment out the `_show_all` definition and `not _show_all and ...` clauses in `_apply_common_filters`. Revert the `has_initiative` block to the old `is not None` check. Tests in `test_deliverable_tool_session_1227.py::HasInitiativeAutofillSafetyTests` will fail — that's expected for the rollback. | Only if a real caller is depending on `has_initiative=False` (Python boolean) actually filtering. PA tool callers all hit the autofill bug instead, so this is unlikely. |
| **#2563** | Comment out the `elif action == 'duplicates':` block. ACTION_MAP entry can stay (it'll fall through to "Unknown action" cleanly with the elif removed). | If the per-group sub-queries (default 50 groups × 3 distributions = ~150 queries per call) introduce DB contention at scale. Has not been observed; default workspace fits easily. |
| **#2564** | Remove the `elif action == 'set_status':` block AND revert the signal change at `deliverable_status_signals.py:94-` (the `metadata['ctx']` namespacing + `delattr` consumption). The signal's old simpler `{from, to, direction}`-only metadata returns. Existing `status_transition` event rows survive unchanged. | If the signal extension somehow conflicts with another consumer — but the change is additive (reads optional context, no behavior change when absent), so no known caller is at risk. |
| **#2565** | Remove the `elif action == 'normalize':` block. The shared `deliverable_aliases.py` module + `deliverable_factory` re-exports stay — they're backwards-compatible. | If some unforeseen edge breaks the dry-run preview. No write path exists without explicit double-confirmation, so this is exceptionally unlikely. |

## 24h watch checklist

1. **PR1+ verification under real load** — Rigby will likely use `deliverable_tool action=list` and `action=duplicates` in routine PA chat over the next session. Spot-check her replies: `applied_filters` should always echo any filters the LLM/user passed; `total_rows_affected`/`total_groups_above_threshold` should match expected workspace counts.
2. **Outreach daily beat first fire** — past due at session open (2026-06-24 13:30 UTC). Verify per Session 1225+1226 watch checklist on first thing 1228.
3. **`set_status` ergonomics check** — Rigby should reach for set_status (rather than `update`) for any premature-completed flips she encounters. If she doesn't, schema description may need a discoverability tweak.
4. **Operator Edge Friday-1 dry-run** — 2026-06-26 (Friday). Same verification path as Session 1222 close.

## Open ops issues filed / continued this session

1. **LLM autofill class-of-bug followup sweep** — `feedback_llm_autofills_boolean_params_with_false.md` lists candidate audit targets: `content_tool` (`show_archived`?), `work_tool`, `initiative_tool` (`include_completed`?), `governance_tool` (`include_resolved`?). A focused sweep PR should grep for `payload.get('...') is not None` on optional bool/int params across all PA tool handlers. Effort: S-M; high leverage (similar silent-filter bugs likely exist elsewhere).
2. **Audit deliverable `e2964e4a-…` F3 amendment** — post-merge, add an addendum noting that the visible 152/300 symptom was real but the cause was misdiagnosed; actual cause is the LLM-autofill class bug closed by PR1. Effort: tiny; just update the deliverable's content via `deliverable_tool action=update`.
3. **Anthropic credit refill** — Chris-side, carried from 1226.
4. **CI billing fix** — Chris-side, carried from 1223 onward. All 4 Session 1227 PRs will need admin-merge until resolved.

## Stack state at session close

- **Branches:** 4 stacked feature branches all pushed to origin, none merged yet (CI billing carryover). Stack order: `feat/session-1227-deliverable-tool-visibility` (PR #2562) → `feat/session-1227-deliverable-tool-duplicates` (PR #2563) → `feat/session-1227-deliverable-tool-set-status` (PR #2564) → `feat/session-1227-deliverable-tool-normalize` (PR #2565). Each PR's base auto-retargets to `main` as the one before it merges.
- **Local environment:** PA worker restarted 4× during session (once per PR's verification pass). All workers healthy at session close.
- **OpenAI credits:** good.
- **Anthropic credits:** still exhausted — Chris-side fix carried from 1226.
- **CI billing:** still failing — Chris-side carryover from 1223 onward.
- **Active conversation:** `pa-08bdd7c9b348415a` — carried from Session 1226 close. Turn count well under threshold; no rotation needed for 1228.

## Open carryover into Session 1228

See 00-START-NEXT-SESSION.md FIRST THING Session 1228. Highlights:

- **LLM-autofill class-of-bug sweep PR** (lead item) — patch other PA tool handlers with the same `is not None` pattern on optional bool/int filter params. High-leverage; closes a recurrence class.
- **Outreach daily beat first-fire verification** — past due, verify on first thing 1228.
- **Operator Edge Friday-1 dry-run** — 2026-06-26 (Friday). Calendar-driven.
- **Anthropic credit refill + autonomous engineer revert** — Chris-side, carried from 1226.
- **Audit §4.4 P1 upstream fix** — `research_agent.py:1103` title-truncation bug. PR2's duplicates output today still shows the prompt-leak clusters as the heaviest groups. Worth a focused slice.
- **Audit deliverable `e2964e4a-…` F3 amendment** — post-merge edit to reflect actual cause.
- **CI billing fix** — Chris-side carryover.
- **Watchdog #5 24-48h re-run** — optional carryover from 1223.

## What didn't happen

- **No outreach work this session** — all calendar-driven items deferred to 1228.
- **No PR merges** — CI billing still blocking. All 4 PRs queued for admin-merge (Chris-side decision).
- **No upstream fix to `research_agent.py:1103`** — left as carryover; PR2's duplicates tool now makes the impact easy to measure across audits.
