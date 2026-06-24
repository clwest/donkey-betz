# Session 1228 — LLM-Autofill Class Sweep + Outreach/Newsletter Beat Timezone Fixes

**Status:** Four-PR session, all admin-merged. Closes the Session 1227-carryover sweep (`feedback_llm_autofills_boolean_params_with_false`) end-to-end, AND surfaces + fixes a separate misinterpretation class — Celery crontabs resolving against `America/Denver` instead of UTC despite UTC-worded comments — that was silently breaking two scheduled tasks.

**Date:** 2026-06-24 (UTC).
**Active conversation:** `pa-08bdd7c9b348415a` — carried from Session 1226 → Session 1227 → Session 1228 with no rotation. Comfortably under turn threshold at close.
**Prior session:** [`SESSION_1227_DELIVERABLE_TOOL_AUDIT_46_AND_LLM_AUTOFILL_ROOT_CAUSE.md`](./SESSION_1227_DELIVERABLE_TOOL_AUDIT_46_AND_LLM_AUTOFILL_ROOT_CAUSE.md).
**Next session entry point:** Session 1229 — see 00-START-NEXT-SESSION.md "FIRST THING Session 1229".

## TL;DR

Session opened on Session 1227's Priority 1: the LLM-autofill class-of-bug sweep across PA tool handlers. Initial grep surfaced **~80 candidate sites** — far larger than the start-here's "5-15" estimate. Rigby triaged into a 2-PR stack: **PR-A** for semantic safety (write-mode flips + filter gate overwrites) and **PR-B** for silent-truncation safety (int autofill with 0 winning over non-zero defaults). Both PRs introduce a new shared helper module `core/services/td_autofill_safety.py` that captures the canonical defenses agreed in Session 1227 PR1/PR2/PR4. **49 new tests** (PR-A) + **14 new tests** (PR-B) + Session 1226 regression = **72/72 OK**. Live Rigby verification confirmed the gates hold.

Mid-session pivoted to P2 (outreach daily beat first-fire verification). The beat **never fired** today: ORM check showed `last_run_at=None` / `total_run_count=0`. Root cause: Session 1225 PR #2548's `crontab(hour=13, minute=30)` was written with a "13:30 UTC" comment but actually fires at 13:30 *Denver* (= 19:30 UTC during MDT). The PeriodicTask row landed with crontab `30 13` / timezone `America/Denver` — six hours later than intended. **The same misinterpretation bug existed in `generate-operator-edge-newsletter`** (also Session 1228 P3 calendar item). Both fixed.

All four PRs admin-merged the same UTC day on Chris's session authorization. CI billing still failing — same Chris-side carryover.

## Session Manifest

### PRs merged (4 total)

| # | Title | What |
|---|---|---|
| **#2567** | `feat(session-1228): LLM-autofill class-of-bug sweep PR-A — mutation gating + update-field safety` | New `core/services/td_autofill_safety.py` (3 helpers: `is_truthy`, `coerce_optional_bool`, `require_write_authorization`). Tier 1 belt-and-suspenders gates on 6 mutation sites (`deliverable_tool.cleanup`, `content_tool.bulk_archive`, `initiative_tool.cleanup_action_items` / `bulk_cleanup` / `bulk_auto_assign`, `autopilot_tool.security_containment_plan`). Tier 2 update-field safety on 4 sites (`list_routes auth_required`, newsletter `manual_fields`, `initiative.create` extra fields, `task_manager.update description`). Schema updates for new `confirm` props. 49 new tests. |
| **#2571** (was **#2568**) | `feat(session-1228): LLM-autofill sweep PR-B — Tier 3 silent-truncation safety` | Falsy-or-default pattern applied to ~33 `int(payload.get('X', N))` sites across 5 handler files. Highest-risk catches: `max_runtime_seconds` (autofilled 0 = silent zero-second timeout), `max_chars` (autofilled 0 = empty deliverable body), `priority_rank` (autofilled 0 = accidental top-rank), 21 `hours`/`days` lookback params in ops. Source-level sweep guard test catches future accidental reverts. 14 new tests. **PR #2568 was closed when PR-A's admin-merge deleted its base branch; rebased onto main and re-opened as #2571.** |
| **#2569** | `fix(session-1228): generate-outreach-drafts-daily crontab timezone misinterpretation` | `crontab(hour=13, minute=30)` → `crontab(hour=7, minute=30)`. Was firing at 13:30 Denver (= 19:30 UTC during MDT); now fires at 7:30 Denver (= 13:30 UTC during MDT, 14:30 UTC during MST). `sync_celery_beat --apply` confirmed the PeriodicTask row updated. |
| **#2570** | `fix(session-1228): generate-operator-edge-newsletter crontab timezone misinterpretation` | Same class fix on the Friday newsletter beat. `crontab(hour=13, minute=0, day_of_week='friday')` → `crontab(hour=6, minute=0, day_of_week='friday')`. Friday 06-26 dry-run check now happens at 12:00 UTC instead of 19:00 UTC (kwargs still `{'dry_run': True}` — no auto-publish during burn-in). |

### Carryover items NOT touched this session (intentional)

- Audit deliverable `e2964e4a-…` F3 amendment — gated on Session 1227 PR1 (#2562) merge; those PRs not yet on main.
- Audit §4.4 P1 upstream `research_agent.py:1103` semantic title fix (prompt-leak duplicates still accumulating).
- Watchdog #5 24-48h re-run (Session 1223 followup).
- CI billing fix (Chris-side).
- Outreach tone tweak nice-to-haves from Session 1225 Rigby tone review.
- Anthropic credit refill + `claude_code_tool` revert from OpenAI workaround (Chris-side; OpenAI fallback continues to function fine — confirmed during this session).

## The four arcs

### Arc 1 — Autofill sweep PR-A (#2567)

**Lead-item entry.** Session 1227's start-here named the LLM-autofill sweep as P1. The recurrence class:
- **Booleans**: GPT-5.2 autofills declared optional bools with Python `False`. Handler checks `if x is not None:` then fire on autofill → silent filter / silent write-mode flip.
- **Integers**: GPT-5.2 autofills declared optional ints with `0`. Handler patterns `payload.get('x', N)` return 0 (the autofill) over N → silent zero-window queries.

Initial grep across `td_handlers_*.py` surfaced **~80 candidate sites** — well beyond the start-here's estimate. Triaged with Rigby via the active conversation; her verdict was to split:

- **Tier 1 (this PR)**: write-mode flips via `dry_run=True` default + autofilled `False` → belt-and-suspenders `dry_run='false'` AND `confirm=true` gate (mirrors PR4 normalize precedent).
- **Tier 2 (this PR)**: filter gates + update-field overwrites. Boolean filter sites use `coerce_optional_bool` (truthy / string-sentinel-false / no-filter). Update-field sites switched from `is not None` to `field in payload` + per-field validation.
- **Tier 3 (PR-B)**: int silent-truncation safety on `int(payload.get('X', N))` sites.

PR-A also extracted the canonical defenses into a new shared module `core/services/td_autofill_safety.py` so the next handler author inherits the pattern. Three helpers:

```python
is_truthy(value)              # one-direction switch (show_all-style)
coerce_optional_bool(value)   # tri-state filter (True/False-string/None)
require_write_authorization(payload)  # belt-and-suspenders mutation gate
```

All three are TypeError-safe against unhashable JSON payload values (lists, dicts) via internal `_safe_in()`.

**Sites fixed (10 total in PR-A)**:

| Tier | Site | Risk |
|---|---|---|
| 1 | `deliverable_tool action=cleanup` | Bulk DELETE on duplicates/orphans/low_quality |
| 1 | `content_tool action=bulk_archive` | Bulk UPDATE status=archived |
| 1 | `initiative_tool action=cleanup_action_items` | Cancels InitiativeActionItem rows |
| 1 | `initiative_tool action=bulk_auto_assign` | Mutates Initiative.owner_agent. **Bonus fix:** prior schema-vs-handler `dry_run` default mismatch (schema said default true, handler defaulted false). |
| 1 | `initiative_tool action=bulk_cleanup` | Bulk archive of stalled Initiatives. Same prior mismatch fixed. |
| 1 | `autopilot_tool action=security_containment_plan` | Live security ops |
| 2 | `platform_config_tool list_routes auth_required` | Autofilled False silently filtered to public-only |
| 2 | `newsletter_tool metrics manual_fields` | Autofilled `opens=0` silently overwrote real opens count |
| 2 | `initiative_tool create` extra fields | Autofilled `''` / `0` overwrote sensible defaults |
| 2 | `task_manager_tool update description` | Autofilled `''` silently cleared real descriptions |

49 new tests. Live Rigby verification through PA worker:
- `deliverable_tool action=cleanup` with no payload → `dry_run=true`, message names "AND confirm". ✓
- Same call with `dry_run=False` alone (autofill case) → `dry_run` still `true`, NOT executed. ✓
- `list_routes` baseline=8 / autofilled `auth_required=False` count=8 / string `'false'` count=0. ✓

### Arc 2 — Autofill sweep PR-B (#2571, was #2568)

**Tier 3 silent-truncation.** Canonical fix expression: `int(payload.get('X') or N)`. Matches Session 1227 PR2 `duplicates` precedent. The bare `or` falls through to the default on autofilled 0 / missing key / None / empty string.

**Distribution (~33 sites across 5 files)**:

| File | Sites | Highlights |
|---|---|---|
| `td_handlers_ops.py` | 24 | All `hours`/`days` lookback params (21), `priority_rank` default 100, `duration_minutes` default 30 |
| `td_handlers_core.py` | 2 | `hours` lookback + conversation `search` days param. The latter previously used `is not None else 7` + a `max(1, …)` clamp that floored autofilled 0 to 1 — still silent-wrong vs intended 7-day window. |
| `td_handlers_content.py` | 6 | `cutoff_days`, `hours`, `cluster_limit`, all 3 `cap` sites (bulk_archive variants) |
| `td_handlers_agents.py` | 5 | `max_chars` for deliverable detail (default 50000), brainstorm `days_back`/`days` |
| `td_handlers_codejobs.py` | 2 | `max_runtime_seconds` (default 600s; autofilled 0 = silent zero-second timeout = instant kill) |

**Intentionally deferred** per Rigby's triage: pure pagination `limit` / `offset` (autofilled 0 produces empty page — observable rather than silent-wrong), `k` for RAG retrieval (already uses `or default`), `start_line` / `after_sequence` / `content_offset` / `content_limit` (default 0 is the legitimate "start" / "no cap" semantic).

14 new tests across 3 classes:
- `AutopilotDaysHoursAutofillTests` — patches downstream engine methods on `SecurityEngine` / `DataIntegrityEngine` / `ValueRealizationEngine`, dispatches the action with autofilled 0, asserts the engine call received the documented default.
- `FalsyOrDefaultPatternSourceTests` — scans the 5 edited files for the bad shape + the PR-B comment marker. Catches future accidental reverts.
- `FalsyOrDefaultExpressionTests` — direct micro-tests of the `int(payload.get('x') or N)` expression across autofill shapes.

Live Rigby verification via `autopilot_tool.value_events_report`:
- Baseline (no `days`) → 744 events (default 7-day window).
- `days=0` (LLM autofill) → 744 events. ✓ Defense holds.
- `days=30` (explicit) → 866 events. ✓ Explicit value flows through.

**Note on PR number**: Originally opened as #2568 stacked on PR-A's branch. When PR-A admin-merged, GitHub deleted the PR-A branch which auto-closed #2568. Rebased the PR-B branch onto main, force-pushed, and re-opened as **#2571**. Content identical.

### Arc 3 — Outreach beat timezone misinterpretation (#2569)

Mid-session pivot to P2 (outreach daily beat first-fire verification). Today's intended fire time per Session 1225 start-here was 2026-06-24 13:30 UTC. Rigby's ORM check:

```
PeriodicTask.objects.filter(name='generate-outreach-drafts-daily').first()
  crontab=30 13 * * * (m/h/dM/MY/d) America/Denver
  last_run_at=None  total_run_count=0
```

Beat log around 07:30 local (= 13:30 UTC, intended fire time) dispatched ~18 unrelated tasks — but `generate-outreach-drafts-daily` was NOT in the batch. The CrontabSchedule had timezone `America/Denver`, so `30 13` meant 13:30 Denver = 19:30 UTC, not 13:30 UTC.

**Root cause:** Session 1225 PR #2548's `crontab(hour=13, minute=30)` was written with a "Schedule pinned 13:30 UTC = 7:30 AM MDT / 6:30 AM MST" comment but Celery resolves `crontab(...)` against `CELERY_TIMEZONE` (= Django `TIME_ZONE` = `America/Denver`). The crontab landed in Denver TZ, six hours later than the author intended.

**Fix:** `crontab(hour=7, minute=30)`. Now resolves to 7:30 AM Denver = 13:30 UTC during MDT (14:30 UTC during MST — seasonal drift acknowledged in the extended comment). `sync_celery_beat --apply` updated the PeriodicTask row in the DB. `QueuePreservingScheduler` picks up the updated crontab on its next poll — no beat restart needed.

**First clean fire:** 2026-06-25 (tomorrow) 13:30 UTC. **Today is a wash** — the inbox already has 5 drafts (overnight at 02:44 UTC, source unclear — likely manual or pre-Session 1225 backfill), so `DAILY_GENERATE_CAP=5` is saturated for the UTC day regardless of when the beat fires.

### Arc 4 — Operator Edge newsletter timezone misinterpretation (#2570)

While inspecting the outreach beat fix, noticed the **same misinterpretation pattern** on the Friday newsletter:

```python
'schedule': crontab(hour=13, minute=0, day_of_week='friday'),  # Friday 6 AM MST = 13:00 UTC
```

Comment claims 13:00 UTC but actually fires at 13:00 Denver = 19:00 UTC during MDT. **Direct impact on Session 1228 P3** — the Friday 06-26 dry-run check was going to land six hours later than expected.

**Fix:** `crontab(hour=6, minute=0, day_of_week='friday')`. Now resolves to 6:00 AM Denver = 12:00 UTC during MDT (13:00 UTC during MST). `dry_run=True` kwarg unchanged — burn-in continues, just at the correct morning slot.

**Friday 06-26 verification window:** dry-run fires at **12:00 UTC = 6:00 AM Denver**, not 19:00 UTC.

## Operational invariants (post-merge)

What's true now that wasn't before:

1. **No PA tool handler can silently flip to write-mode on an LLM autofill of `dry_run=False`.** Belt-and-suspenders requires both `dry_run` falsy AND `confirm=true`. Six mutation surfaces gated (Arc 1).
2. **No PA tool handler with a `is not None`-style optional boolean filter applies the filter on Python bool `False`.** Use `coerce_optional_bool` from the new shared helper (Arc 1).
3. **No PA tool handler returns silent zero from autofilled int=0 over a non-zero default.** All ~33 known offenders use the `int(payload.get('X') or N)` shape (Arc 2). Source-level test catches future regressions.
4. **`generate-outreach-drafts-daily` and `generate-operator-edge-newsletter` PeriodicTask rows are correctly scheduled for the intended Denver-morning slot.** The 6-hour drift bug is closed. Tomorrow's 13:30 UTC outreach fire and Friday's 12:00 UTC newsletter fire are the first clean validations.

## Rollback levers

- **Autofill helpers**: revert specific handler edits by replacing the `from core.services.td_autofill_safety import …` line with the old `if x is not None:` shape. The shared module can stay even with handlers reverted; no cross-coupling.
- **Beat schedules**: `PeriodicTask.objects.filter(name='generate-outreach-drafts-daily').update(enabled=False)` instantly disables the task without code revert. Same for `generate-operator-edge-newsletter`.
- **Per-call override on PR-A gates**: pass `dry_run='false' confirm=true` to deliberately flip to write mode. The audit trail at the call site logs the actor.

## 24h watch checklist

- [ ] **2026-06-25 13:30 UTC**: confirm `CeleryTaskEvent.objects.filter(task_name='core.tasks.generate_outreach_drafts_daily').order_by('-started_at').first()` returns a SUCCESS row and `OutreachDraft.objects.filter(lead_source='opportunity_outreach_seed', created_at__date='2026-06-25').count()` is 1–5.
- [ ] **2026-06-26 12:00 UTC**: confirm `PeriodicTask.objects.filter(name='generate-operator-edge-newsletter').first().last_run_at` updates + dry-run deliverable produced in `ready` / `preview` state (no auto-publish).
- [ ] **Rigby `deliverable_tool action=cleanup` sanity probe (any time)**: plain call should return `dry_run=True` with message naming "AND confirm". Re-verify if anything looks off.
- [ ] **`feedback_llm_autofills_boolean_params_with_false` memory rule**: keep updated as the canonical reference. Extend if a new LLM autofill shape surfaces (string-typed enums, list shapes, etc.).

## Key file pointers

- `core/services/td_autofill_safety.py` — new canonical helpers.
- `core/tests/test_td_autofill_safety.py` — 20 unit tests on the helpers.
- `core/tests/test_autofill_sweep_session_1228.py` — 29 PR-A integration tests across 8 test classes.
- `core/tests/test_autofill_sweep_session_1228_pr_b.py` — 14 PR-B integration + source-level + expression tests.
- `core/celery.py:431-444` (outreach) + `:418-432` (newsletter) — both with extended comments explaining the misinterpretation.

## Followups for Session 1229

1. **Tomorrow 13:30 UTC outreach beat watch** (calendar gate).
2. **Friday 12:00 UTC newsletter dry-run watch** (calendar gate; this is the first of the 2-Friday burn-in).
3. **Audit deliverable `e2964e4a-…` F3 amendment** — still gated on Session 1227 PR1 (#2562) merge. Trivial via `deliverable_tool action=update`.
4. **Audit §4.4 P1 upstream `research_agent.py:1103` semantic title fix** — prompt-leak duplicates still accumulating (count=20+ on the heaviest cluster per Session 1227 PR2 verification).
5. **Watchdog #5 24-48h re-run** (Session 1223 followup, optional drift confirmation).
6. **Chris-discretion**: fleet sibling apps build-out, additional audit items, anything else.
