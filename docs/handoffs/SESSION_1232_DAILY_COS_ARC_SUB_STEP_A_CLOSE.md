# Session 1232 — Daily-CoS Arc Sub-step A close + Sub-step B start (v0 workflow template)

**Status:** Two-PR session. **Sub-step A closed** end-to-end (spec drafted via Rigby consultation + Chris-ratified via "agree all" decision card + committed in PR #2596). **Sub-step B started** with v0 `WORKFLOWS['morning_brief']` template + 10 contract tests in PR #2597. Acceptance criteria from Session 1231's "FIRST THING Session 1232" all met. Followup F-tags for Sub-steps B-completion / C / D / E roll into Session 1233 priorities.

**Date:** 2026-06-24 (UTC).
**Active conversation:** `pa-21dfa3a3dc4545b7` (continues from Session 1231 → 1232; +18 turns this session; `session_tool health_check` score 75/100, recommendation `continue`; no rotation triggered).
**Prior session:** [`SESSION_1231_AGENT_ERROR_PATTERN_INVESTIGATION.md`](./SESSION_1231_AGENT_ERROR_PATTERN_INVESTIGATION.md).
**Next session entry point:** Session 1233 — see `00-START-NEXT-SESSION.md` "FIRST THING Session 1233".

## TL;DR

Session 1231 closed with the platform at 68/68 = 100% production-healthy across both the dispatch contract and workflow-completion contract. The next-session plan picked the **daily Chief-of-Staff brief** as the first concrete product wedge — the closest-to-shipping framing for "what IS Donkey Betz?" because every piece exists + just got verified end-to-end. Only thing missing is a *standing* daily flow.

Session 1232 executed Sub-step A of that arc cleanly. **(1)** Rigby consulted on the topic mix and pushed back on the original candidate list — the plan suggested daily sports/Kalshi/tickers but Rigby's read was "easy to become noise, better as on-demand or rotation"; she counter-proposed a 4-lane structure (Platform Readiness + Build Focus + Competitive change-only + Rotating market lane) with explicit override triggers and a Decision Card synthesis section. **(2)** Spec captured in `docs/MORNING_BRIEF_SPEC.md` (PR #2596) with full rotation schedule, override priority, output shapes, source agents/feeds, and the 7-step `WORKFLOWS['morning_brief']` skeleton. **(3)** Chris ratified via "agree all" on a 7-question decision card surfaced through Rigby. **(4)** Sub-step B started with the v0 workflow template entry + 10 contract tests locking the v0 shape against the spec (PR #2597). 10/10 new + 6/6 adjacent F4 tests green.

Acceptance criteria from Session 1231's "FIRST THING Session 1232" all met:

- [x] `docs/MORNING_BRIEF_SPEC.md` exists, lists 4 lanes + per-topic prompts + output shape, Chris-ratified
- [x] Rigby consulted on topic selection (verifier-loop pattern — her input drove the rotation+overrides structure that replaced the daily-noise candidates)
- [x] At least one `morning_brief` workflow template draft exists (v0 in PR #2597)
- [x] Followup F-tags for Sub-steps B-completion / C / D / E rolled into Session 1233 priorities (see "FIRST THING Session 1233")

The collaboration shape that worked best in this session: **Claude directs, Rigby executes, Claude verifies, Chris ratifies via decision card.** Rigby drafted the substantive spec content (lane structure, rotation, overrides, workflow skeleton); Claude captured it verbatim into the doc + wrote the v0 workflow template + tests + PR descriptions; Chris approved with one-tap "agree all." No solo-Claude pivots. No Rigby placeholder-stall (she shipped real content in one pass after one truncation continuation).

Both PRs **awaiting CI/admin merge** — same Chris-side CI billing carryover from Sessions 1223 → 1231.

## Session Manifest

### PRs opened (2 total, both awaiting CI/admin merge)

| # | Title | What |
|---|---|---|
| **#2596** | `docs(session-1232): MORNING_BRIEF_SPEC v1 active — daily-CoS Sub-step A close` | `docs/MORNING_BRIEF_SPEC.md` (270 lines, status `active`, ratified `2026-06-24` by Chris via "agree all"). Captures: 4 lanes (Platform Readiness + Build Focus + Competitive change-only + Rotating Market) + Decision Card synthesis at bottom + rotation schedule (Mon=AI-infra / Tue=Competitor-deepen / Wed=Tickers / Thu=GTM / Fri=Sports↔Kalshi alternating) + override priority (Incident → Revenue → Signal → Calendar) + per-lane output shape + source agents/feeds + 7-step `WORKFLOWS['morning_brief']` skeleton + scheduling (13:00 UTC / 07:00 MDT) + Open Questions block (now resolved) + Definition of Done. Doc index regenerated in same PR. |
| **#2597** | `feat(session-1232): WORKFLOWS['morning_brief'] v0 template (Sub-step B start)` | v0 workflow template added to `core/services/workflow_orchestration_agent.py:WORKFLOWS['morning_brief']` (7 steps: lane_1_platform_readiness → system_intelligence_agent / lane_2_build_focus → coo_agent / lane_3_competitive_landscape → trend_analysis_agent / lane_4_rotating_focus → research_agent (v0 default for Mon AI-infra slot) / decision_card_synthesis → coo_agent / strategic_synthesis → strategic_synthesis (PR #2592 handler) / create_deliverable → create_project_from_research). Also adds `'morning_brief'` to `AVAILABLE_WORKFLOWS` in the wrapper. New `core/tests/test_morning_brief_workflow_template.py` — 10 contract tests locking v0 shape against spec (registered in AVAILABLE_WORKFLOWS, present in WORKFLOWS dict, no_image_generation flag, 7 steps, step names match, agents match, sequential step numbers, strategic_synthesis handler reference, create_project_from_research handler reference, content_type tag). 10/10 new + 6/6 adjacent F4 tests (`test_workflow_orchestration_agent_map_fallback`) green. v0 shape stub — full per-step input plumbing (rotation_slot_resolve pre-step, slot-resolved Lane 4 dispatch, override-trigger inputs) lands in Sub-step B follow-on next session. |

### Rigby's contributions to this session

- **Topic mix push-back** — first response to opening message refused to just rubber-stamp the candidate list from the start-here plan. Pushed back on daily sports/Kalshi/tickers as noise; counter-proposed rotation + overrides; flagged missing "decisions/asks" + GTM pipeline + initiative checkpoint sections. This re-shape is the load-bearing content of the spec.
- **v1 spec draft** — produced complete 4-lane spec with dispatch prompts, output shapes, source agents+feeds, rotation schedule (Mon/Tue/Wed/Thu/Fri assignments + reason per slot), 4-level override priority order, Decision Card placement + hybrid feed (synthesis dispatch + governance/work/ops guardrail tool reads), workflow skeleton with pre-step + 7 main steps with input/write key annotations. Three message-turns to complete (truncation continuations).
- **Decision card** — formatted the 7 ratification questions as a tight card with `your lean` + `Claude's lean` + alt options per item + an "Agree all" one-tap path. Chris hit "agree all" → no edits.
- **Config + ownership verify** — `platform_config_tool overview` (service_context=local ✓) + `session_tool whoami` (conversation_owner_match=true, owner=chris ✓) on session open per memory rule.
- **Health check at close** — `session_tool action=health_check` returned score 75/100 / recommendation=continue / 18 turns / ~9k tokens / 3.7h. No rotation triggered.

## Deliverables (in-session)

None this session. Spec doc + workflow template both land via PRs, not deliverables. The spec doc is the canonical artifact going forward.

## Operational invariants (post-merge — once #2596 + #2597 land)

1. **Canonical spec exists.** `docs/MORNING_BRIEF_SPEC.md` is the single source of truth for the daily-CoS brief shape. Any change to lane structure / rotation / override priority / workflow steps lands in the same PR as the spec update.
2. **`morning_brief` is a registered workflow.** `'morning_brief' in AVAILABLE_WORKFLOWS` and `'morning_brief' in WorkflowOrchestrationAgent.WORKFLOWS`. The wrapper exposes it; the runner can dispatch its steps via existing AGENT_MAP fallback + internal handlers.
3. **v0 contract tests sentinel the workflow shape.** `core/tests/test_morning_brief_workflow_template.py` fails loudly on any drift (step rename, agent swap, count change, sequence change) — Sub-step B follow-on PRs must update both spec doc AND test expectations in the same PR.

No behavioral invariants ship this session (no scheduled fires, no PA tool changes, no agent code paths modified). v0 workflow template is parsed-and-dispatchable but the rotation slot resolution + Lane 4 slot-resolved dispatch + per-step input plumbing all land in Session 1233 Sub-step B follow-on.

## Active conversation status

- `pa-21dfa3a3dc4545b7` — continues from Session 1230 close (rotated from `pa-4086552cdc9840e9` at Session 1230 close at 38 turns / 19k tokens / 2.5h / suggest_fresh score 45).
- Session 1231 added ~10 turns; Session 1232 added 18 turns; cumulative on this thread ~28 turns / ~9k tokens / 3.7h.
- `session_tool health_check` at session close: score 75/100, recommendation **continue**, no rotation triggered.
- Continues into Session 1233 on this thread.

## Carryover into Session 1233

### Chris-side

- **CI billing fix** still outstanding. Both Session 1232 PRs (#2596 + #2597) will need admin-merge if CI is still failing. Carryover from Sessions 1223 → 1224 → 1225 → 1226 → 1227 → 1228 → 1229 → 1230 → 1231 → 1232.
- **Anthropic credit refill** at https://console.anthropic.com/billing. One-liner Makefile revert (`unset CLAUDE_CODE_ENGINE_PROVIDER`) when credits land. Then A/B the Session 1229 line-count task on claude-sonnet-4 vs the Session 1230 OpenAI-path fix; if Anthropic-path is clean, lift the retry contract up out of the OpenAI-only branch.

### Time-bound (DUE TOMORROW)

- **Outreach beat first-fire verification (2026-06-25 13:30 UTC)** — Session 1228 carryover, P3 in Sessions 1230-1231. See "FIRST THING Session 1233" Priority 1 for verification commands.
- **P2 behavioral verify (2026-06-25 13:30 UTC, same window)** — first scheduled COOAgent daily diagnostic after PR #2586 merge. Expect zero `'files_generated'` errors going forward. See "FIRST THING Session 1233" Priority 1.
- **Operator Edge newsletter Friday-1 dry-run check (2026-06-26 12:00 UTC)** — Session 1228 carryover. Verify `PeriodicTask.last_run_at` reflects 06-26 12:00 UTC + new deliverable created with `status='ready'` or `'preview'` (no auto-publish). After 06-26 + 07-03 both pass, flip kwargs to `{'dry_run': False}`.

### Daily-CoS arc continuation

Sub-step B follow-on, Sub-step C scheduling, Sub-step D polish, Sub-step E dogfood — all rolled into Session 1233+ priorities. See "FIRST THING Session 1233" Priority 2.

## Recommended Session 1233 plan

1. **Priority 1 — Clear calendar checks first** (outreach + P2 verify both at 06-25 13:30 UTC + Friday newsletter at 06-26 12:00 UTC). All time-bound. ORM-pull commands in "FIRST THING Session 1233."
2. **Priority 2 — Daily-CoS arc Sub-step B follow-on**: wire `rotation_slot_resolve` pre-step + slot-resolved Lane 4 dispatch + per-step input/write key plumbing. End state: workflow runs end-to-end on a chosen weekday slot and produces a deliverable with the 4 lanes + decision card. Spec PR #2596 + v0 workflow PR #2597 are the inputs.
3. **Priority 3 — Daily-CoS arc Sub-step C**: persistent "Morning Brief" workspace (UUID captured) + `PeriodicTask` row `generate-morning-brief-daily` at `crontab(hour=13, minute=0)` UTC + verify first fire on the morning after merge. Per spec § Scheduling, watch the DST/MST transition (13:00 UTC = 07:00 MDT during summer; 14:00 UTC = 07:00 MST during winter). Session 1228 PRs #2569/#2570 are the TZ trap reference.
4. **Priority 4-N** — original Session 1232 priorities that didn't get touched (smoke-harness mode inconsistency F5, smoke-probe tagging F1/REC-2, smoke harness mgmt-command promotion F6, audit §R2 amendment F3, engineer workspace staleness, meeting-context leak shape watch, fleet-smoke wall-clock timeouts). None time-bound.

If Sub-step B finishes early and Sub-step C is a single small PR, ship both in Session 1233 and Chris gets his first scheduled morning brief 2026-06-27 13:00 UTC.

## Session bookkeeping

- Two PRs opened, neither yet merged.
- `docs/INDEX.md` regenerated and committed in PR #2596 to include the new spec row.
- Active branch `feat/session-1232-morning-brief-workflow` not yet merged; main is at `e6aab9a3` (Session 1231 close).
- All Session 1232 commit subjects include `session-1232` per commit-message hygiene rule.
- `make celery` not restarted this session — no `@shared_task` or imported-module changes.
- `verify_doc_claims --only-drift` not run this session (no count claims edited in the spec — counts pulled from anchors as-of-now).
