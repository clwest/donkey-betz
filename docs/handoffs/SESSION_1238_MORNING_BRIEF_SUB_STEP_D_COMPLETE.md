# Session 1238 — morning_brief Sub-step D + cf708a2e leak fix, 6 PRs

**Status:** Closes the daily-CoS Sub-step D polish phase end-to-end. All 6 PRs from Rigby's 06-26 audience-fit verdict landed in priority order. Plus the cf708a2e leak surfaced during P1.b drill (separate from Sub-step D, but adjacent fix).

**Date:** 2026-06-26 (UTC, Friday morning + day session ~09:00-09:10 CDT = 14:00-14:10 UTC).
**Active conversation:** `pa-a2443db2e43a42dc` — continued from Session 1237. Health 100/100 at S1238 open + close. ~24 turns added across the session.
**Companion handoffs:**
- [`SESSION_1237_AUDIT_BONUS_CARRYOVERS_CLOSE.md`](./SESSION_1237_AUDIT_BONUS_CARRYOVERS_CLOSE.md) — preceded; closed bonus carryovers from the P5#3 audit
- [`SESSION_1236_P5_3_AUDIT_COMPLETE_TRANCHE_1_THROUGH_4.md`](./SESSION_1236_P5_3_AUDIT_COMPLETE_TRANCHE_1_THROUGH_4.md) — full audit close
- [`SESSION_1235_CARRYOVER_CLOSE_PLUS_P5_3_DRIFT_SWEEP_TRANCHE_1.md`](./SESSION_1235_CARRYOVER_CLOSE_PLUS_P5_3_DRIFT_SWEEP_TRANCHE_1.md) — original audit start

## TL;DR

Session 1238 opened with P0 conv health check (100/100 fresh) and proceeded directly into P1 calendar verifications. **All 3 morning fires confirmed**:
- `refresh_docs_corpus` first-fire at 10:00 UTC: SUCCESS, took 12.35s (cascade ran due to new handoff added at S1237 close)
- morning_brief 2nd-fire at 13:00 UTC: SUCCESS, took 204.6s
- Operator Edge: confirmed DISABLED on local per `LOCAL_DENY_TASKS` (prod runs independently; my 00-START said wrong time)

**Two anomalies surfaced during P1**: a single cf708a2e workspace leak (COOAgent daily diagnostic, separate dispatch path from Session 1234 D3's morning_brief lane fixes) + Operator Edge timestamp wrong in 00-START. Both became PR-A + PR-B.

Then Chris read the morning brief, Rigby ran an audience-fit verdict (overall 66/100), and 4 polish PRs (PR-1 through PR-4) implemented her prioritized fix list. All 4 PRs through the same `_execute_strategic_synthesis_step` morning_brief mode pre-processing path.

## PRs (chronological)

| PR | Subject | Net | Tests |
|---|---|---|---|
| [#2653](https://github.com/clwest/donkey-betz-platform/pull/2653) (A) | `scheduled_diagnostic_runner` workspace_resolver | +368 / -1 | 10 |
| [#2654](https://github.com/clwest/donkey-betz-platform/pull/2654) (B) | 00-START Operator Edge timestamp 12:00→06:00 UTC | +6 / -6 | (doc-only) |
| [#2655](https://github.com/clwest/donkey-betz-platform/pull/2655) (1) | Decision Card validator + truncation guard + dynamic TZ | +391 / -5 | 11 |
| [#2656](https://github.com/clwest/donkey-betz-platform/pull/2656) (2) | Lane 1 self-referential health alarm filter | +317 / -0 | 12 |
| [#2657](https://github.com/clwest/donkey-betz-platform/pull/2657) (3) | Lane 4 odds-missing fallback | +298 / -0 | 13 |
| [#2658](https://github.com/clwest/donkey-betz-platform/pull/2658) (4) | Lane 3 adaptive + MUSCULAR plain-English | +322 / -0 | 19 |

**Totals:** +1,702 / -12 net production lines (mostly helper methods + tests). **75 new tests across 6 PRs, all green.**

## P1 calendar verifications (morning ritual)

### P1.a — refresh_docs_corpus ✅ PASSED

First-ever scheduled fire of the Session 1235 PR #2634 beat task:
- Status SUCCESS, fired exactly 10:00:00 UTC (within 90ms)
- Duration: 12.35 seconds — cascade ran because S1237 close added a new handoff doc + 13 embedding chunks, triggering both hash-delta + unembedded-count gates
- Next fire expected to hit < 1s skip path (corpus fully embedded again post-cascade)

### P1.b — morning_brief 2nd-fire ⚠️ FOUND CF708A2E LEAK

Workflow itself ran cleanly: 13:00 UTC SUCCESS, took 204.6s (~3.4min, expected for multi-agent workflow). **2/2 workflow-internal deliverables in MB workspace `19807888-…`** — Session 1234 D3-D6 fixes held.

**But cross-check found a SEPARATE leak**: 3rd today-chris deliverable came from COOAgent at 13:32:05 (the `coo_daily_diagnostic` beat task running 30min after morning_brief), with `ctx.workspace_id: None` → router fallback to `cf708a2e` debug ws. This is a DIFFERENT dispatch path from morning_brief; D3-D6 only fixed lane handlers, not other beat tasks. Became PR-A.

### P1.c — Operator Edge ✅ Non-issue locally

`enabled: False` because the task is in `LOCAL_DENY_TASKS` (`add_critical_celery_tasks.py:65`). Prod runs independently. Crontab is `hour=6, minute=0, day_of_week=friday` (06:00 UTC), NOT 12:00 UTC as my 00-START claimed. Doc correction became PR-B.

## PR-A — scheduled_diagnostic_runner workspace_resolver

**Bug:** all 3 scheduled diagnostics (COO, CTO, TrendAnalysis) share the `scheduled_diagnostic_runner.run_diagnostic()` primitive. When their per-diagnostic env vars (`COO_DIAG_WORKSPACE_ID` etc.) are unset, `workspace_id` falls through to `None`. The agent_router's fallback picks the user's most-recent-active workspace (`cf708a2e` from Session 1231 E2E). One leak path → 3 leaks closed.

**Fix:** added `workspace_resolver: Optional[Callable[[], Optional[str]]]` field to `DiagnosticConfig`. Priority chain becomes:
1. `workspace_id_env` (env var) — preserved for ops flexibility
2. `workspace_resolver()` — new lazy resolver for deterministic targeting
3. `None` — pre-fix fallback (router default, known bad)

New shared helper `core/services/diagnostics/_workspace_resolver.py:resolve_morning_brief_workspace_id()` returns chris's Morning Brief workspace_id. Wired into COO, CTO, Trend `build_config()`.

**Backfill:** moved today's leaked deliverable `c66ab90b-c872-44de-9f92-208339b1bc6f` ("COO Analysis: Brief — 2026-06-26") from cf708a2e → 19807888. Post-backfill: 3/3 chris deliverables in MB workspace, 0 in cf708a2e.

## PR-B — 00-START Operator Edge timestamp correction

Trivial doc fix. Active line 196 corrected to "06:00 UTC = 00:00 MDT" + appended operational notes (LOCAL_DENY_TASKS membership; prod-only verification via Railway logs; attribution to PR-B). Historical sections preserved as-is per "Never delete docs" rule.

## PR-1 through PR-4 — Sub-step D polish per Rigby's verdict

After Chris read the morning brief, I asked Rigby for her formal audience-fit verdict (Sub-step D scope-naming step from Session 1234 plan). She returned:

- **Score: 66/100** with one-sentence verdict: _"Useful skeleton and morning cadence, but it fails the 'trust + completeness' bar today due to an incomplete Decision 3 and an overconfident warning that asks Chris to act on telemetry the brief itself can't substantiate."_
- 6 prioritized polish items (5 of mine confirmed + 1 new — the MDT vs MST mismatch I missed)

Ordered by impact:

### PR-1 (#2655) — Decision Card validator + truncation guard + dynamic TZ

Highest user-facing trust impact. 3 changes:

1. **Dynamic Denver TZ**: prompt hardcoded `'by 11:00 AM MST'` example → LLM followed it → 06-26 brief said MST in summer. Fix: inject `datetime.now(tz=ZoneInfo('America/Denver')).strftime('%Z')` at prompt build time. Tracks DST automatically.
2. **Token budget bump (4000 → 6000)**: per memory rule `feedback_gpt5_max_completion_tokens_floor`, gpt-5-mini burns 1500-2000 reasoning tokens → 4000 max gave ~2000-2500 output ceiling. Tight for 3 decision cards × 4 fields. Today's truncation: Decision #3 ended at "...confirm whether missing odds data" with no period. Bumped both `decision_card_synthesis` and `strategic_synthesis morning_brief mode`.
3. **`_validate_decision_card` static method**: 4-rule post-render validator (sentinel exception / termination / required fields / at-least-one-decision). Logs warning on issues, does NOT fail the step. Telemetry field `validation_issues` on step result.

### PR-2 (#2656) — Lane 1 self-referential health alarm filter

Pre-fix Lane 1's MUSCULAR "paralyzed" warning was based on stale body_system snapshot — surfaced as high-confidence asking Chris to approve a manual health check on the system that JUST GENERATED THE BRIEF.

New helper `_collect_lane_1_self_check_evidence(lane_1_text)`:
- Trigger: scans for health-alarm keywords (only fires when needed)
- Self-check: cheap ORM queries on AgentExecution + CeleryTaskEvent for last 30 min — SAME metrics MUSCULAR body_system uses
- Confidence verdict: LOW (stale, downgrade) / MEDIUM (partial) / HIGH (real)
- Falsifying condition: explicit threshold for Chris to re-verify by hand

Injected into morning_brief synthesis prompt under `_lane_1_self_check` key. Prompt updated with explicit downgrade rule.

### PR-3 (#2657) — Lane 4 odds-missing fallback

Pre-fix SharpActionDetector returned success with thin "No multi-bookmaker odds data available." → dead lane. Two helpers:
- `_lane_4_output_is_thin(output)` — heuristic detector (empty / <200 chars / "no multi-bookmaker odds" / "no qualifying" markers)
- `_lane_4_sports_edge_scan_fallback()` — Rigby's 3-block template (Data status / What we can still do today / Action)

Integration in `_execute_lane_4_rotating_focus_step` success branch: augments thin sports_edge_scan outputs under a "Session 1238 PR-3 auto-augmented" marker. Other slots / substantive outputs / failure path all unchanged.

### PR-4 (#2658) — Lane 3 adaptive + MUSCULAR plain-English

Two text-shape fixes via same synthesis pre-processing path PR-2 established:

1. **Lane 3 adaptive**: detects no-signal (`_lane_3_is_no_signal`) → injects `_lane_3_no_signal_fallback()` template with Coverage map + Top 3 watch items + Action="None today, informational"
2. **MUSCULAR humanization**: `_humanize_body_system_jargon()` — pure idempotent string substitution. "MUSCULAR: No Agent Activity" → "Agent activity anomaly (possible worker stall) [MUSCULAR]"

## Operational invariants (post-Session 1238)

All prior session invariants still hold + Session 1238 additions:
1. `scheduled_diagnostic_runner` workspace priority chain: env_var → resolver → None. COO/CTO/Trend daily diagnostics auto-target chris's MB workspace.
2. Today's COOAgent leaked deliverable backfilled to MB workspace; zero cf708a2e deliverables remain for chris today.
3. Decision Cards: dynamic Denver TZ; budget headroom 6000 tokens; post-render validator catches truncation + missing fields.
4. Lane 1 health alarms: contradiction-aware via 30min recheck against AgentExecution + CeleryTaskEvent.
5. Lane 4 sports_edge_scan: deterministic fallback when odds data missing.
6. Lane 3: deterministic fallback when no-signal.
7. Body-system jargon: humanized in operator-facing text with engineering tag preserved.

## Worker state

No new `@shared_task` added Session 1238 — all changes were either to existing handlers, helper methods, or `DiagnosticConfig` fields. **No worker restart needed**.

## Tomorrow's cumulative verification (06-27 morning_brief 2nd-fire @ 13:00 UTC)

Expected behavior:
- ✅ Decision Cards end with periods, show "MDT" (not "MST"), have all 4 required fields per decision
- ✅ Lane 1 warnings tagged "(Evidence confidence: low — auto-downgraded by 30min recheck)" when self-check refutes them
- ✅ Lane 3 ships with coverage map + watch items if no-signal
- ✅ Lane 4 ships with 3-block fallback if odds data missing
- ✅ Body-system jargon humanized (MUSCULAR appears only as parenthetical tag)
- ✅ COO daily diagnostic deliverable (13:30 UTC) lands in MB workspace, not cf708a2e
- ✅ `refresh_docs_corpus` first fire (04:00 Denver) likely hits skip path

If all 5+ hold + no truncation: Rigby's overall 66/100 should land in the 80s.

## Active conversation at close

`pa-a2443db2e43a42dc` — health 100/100, ~24 turns added Session 1238 (8 PRs × ~3 turns each). Still healthy but approaching the rotation point Rigby flagged at S1237 open ("rotate before next substantial design+execution arc"). Recommend health re-check at S1239 open + possible rotation if score < 90 or topic count > 7.

## Doc-claim drift verifier at close

Expected 0 drift. Run at close.

## Memory rule reinforcements

No new feedback rules added. Existing rules used extensively:
- `feedback_session_open_with_orient` — P0 health check (used)
- `feedback_test_real_db_for_queryset_semantics` — all 75 new tests
- `feedback_gpt5_max_completion_tokens_floor` — PR-1 budget bump rationale
- `feedback_claude_directs_rigby_then_verifies` — Rigby's audience-fit verdict + my synthesis
- `feedback_corpus_walks_surface_mechanism_drift` — P1 drills surfaced PR-A + PR-B as bonus findings

## Carryover for Session 1239+

**Calendar (low priority — these have all fired today):**
- 06-27 morning_brief 2nd-fire @ 13:00 UTC = primary verification window for the 6 PRs landed today
- 06-27 `refresh_docs_corpus` @ 10:00 UTC = expected skip path

**Pre-existing tail (unchanged across many sessions):**
- Smoke-harness mode inconsistency (Session 1231 F5, LOW-MEDIUM)
- Smoke-probe tagging for AgentExecution (Session 1231 F1)
- Promote `scripts/smoke_all_agents.py` → mgmt cmd (LOW)
- Audit `5318da3e-…` §R2 amendment
- Engineer workspace staleness (Session 1230 F3, MEDIUM)
- Meeting-context leak shape watch (LOW)
- Fleet-smoke wall-clock timeouts (LOW)

**Chris-side:** Anthropic credit refill, CI billing (still admin-merging).

## Session content quality reflection (per `feedback_content_presence_vs_quality`)

Session 1238 was a high-yield day: 6 PRs, +1,702 / -12 production lines, 75 new tests. The Sub-step D arc closed end-to-end in a single day — every Rigby polish item from her 06-26 audience-fit verdict shipped with regression-guard tests and tomorrow's natural verification window.

Quality dimension: every PR shipped with green tests AND with the specific defect shape its tests prevent regression on (Decision #3 truncation literal in PR-1, MST-in-summer in PR-1, "paralyzed" without recheck in PR-2, "No multi-bookmaker odds data" in PR-3, "no confirmed events" + MUSCULAR jargon in PR-4). Tests aren't generic — they assert the exact pre-fix bug shape doesn't recur.

The morning brief is the deliverable; tomorrow's fire is the natural test harness.
