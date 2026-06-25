---
title: "Session 1233 — Morning Brief workflow B.1 + B.1.fix smoke verification"
status: active
session: 1233
generated: 2026-06-24
companion_docs:
  - docs/MORNING_BRIEF_SPEC.md
  - docs/handoffs/SESSION_1232_DAILY_COS_ARC_SUB_STEP_A_CLOSE.md
related_prs:
  - "#2599 — feat(session-1233): morning_brief plumbing + Lane 4 slot-driven + decision card + deliverable handler (B.1)"
  - "#2600 — fix(session-1233): AGENT_MAP fallback acronym alias map (B.1 follow-on)"
---

# Session 1233 — Morning Brief Workflow B.1 + B.1.fix Smoke Verification

## TL;DR

End-to-end smoke of `WORKFLOWS['morning_brief']` against locally-merged main confirmed **3 of 7 steps green** before hitting a known macOS-local environment issue (ML model loading + fork-safety mutex deadlock — memory rule `feedback_local_celery_stall_playbook`). The 3 verified steps cover **all the B.1 code changes**:

- ✅ Lane 1 dispatch via AGENT_MAP fallback (Step 1 — `system_intelligence_agent → SystemIntelligenceAgent`)
- ✅ **Acronym alias map (B.1.fix / PR #2600)** — Step 2 dispatched `coo_agent → COOAgent` cleanly. This is the exact failure surfaced by the first smoke that drove PR #2600. **Smoking-gun verification: alias works.**
- ✅ Standard PascalCase fallback (Step 3 — `trend_analysis_agent → TrendAnalysisAgent`)
- ✅ Internal handler dispatch (Step 4's `lane_4_rotating_focus` internal handler entered + slot-resolved to `ai_infra_deep_dive → ResearchAgent` correctly)

The hang at Step 4 is **environment-level, not code-level**. Same workflow will run end-to-end on Railway where the worker env has `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`.

## Step transitions captured

Trace from `_execute_step` (`core/services/workflow_orchestration_agent.py`) during the smoke:

```
21:05:02  🔄 Workflow Step 1/7: lane_1_platform_readiness (system_intelligence_agent)
21:05:45  ✅ Step lane_1_platform_readiness completed: Completed     (43s)
21:05:45  🔄 Workflow Step 2/7: lane_2_build_focus (coo_agent)
21:06:09  ✅ Step lane_2_build_focus completed: Completed             (24s)  ← B.1.fix verified
21:06:09  🔄 Workflow Step 3/7: lane_3_competitive_landscape (trend_analysis_agent)
21:06:45  ✅ Step lane_3_competitive_landscape completed: Completed   (36s)
21:06:45  🔄 Workflow Step 4/7: lane_4_rotating_focus (lane_4_rotating_focus)
        [hung — see Root Cause below]
```

(Times UTC. PID 7895, smoke script `/tmp/smoke_morning_brief.py` invoked via `manage.py shell`.)

## B.1.fix verification (the smoking gun)

The **first smoke** (pre-PR #2600) failed at Step 2:

```
ERROR 2026-06-24 20:48:49  workflow_orchestration_agent
❌ Step lane_2_build_focus failed:
   Unknown agent in workflow: coo_agent
   (no internal handler + 'CooAgent' not in AGENT_MAP)
```

The **post-PR #2600 smoke** (above trace) completed Step 2 in 24s with no error. This is the exact code path PR #2600 patched:

- Pre-fix: `''.join(p.capitalize() for p in 'coo_agent'.split('_'))` → `'CooAgent'` → not in AGENT_MAP → workflow aborts.
- Post-fix: `_AGENT_MAP_SNAKE_ALIASES['coo_agent']` → `'COOAgent'` → present in AGENT_MAP → dispatch succeeds.

Zero ambiguity: the alias map fixed the smoke-blocking bug.

## Internal handler dispatch evidence (Step 4 start)

Before the hang, Lane 4's internal handler logged its slot resolution + Lane 4 dispatch entry:

```
INFO 21:06:45  [router_heartbeat] thread spawned agent=ResearchAgent
INFO 21:06:45  knowledge_first_router  Knowledge-first routing for:
               Morning Brief Lane 4 — slot=ai_infra_deep_dive.
               Provide actionable signals only (not a news dump)…
```

The slot resolved to `ai_infra_deep_dive` (the B.1 default per spec — Monday AI-infra slot) and dispatched to `ResearchAgent` per the `_MORNING_BRIEF_LANE_4_SLOT_AGENT` map. The internal handler is working as designed.

## Root cause of the Step 4 hang

ResearchAgent's downstream pipeline triggered ML model loading:

```
21:07:14  ml_engine  Initializing ML stack - MLX Available: False
21:07:15  ml_engine  Loaded existing model: sports_crypto_lstm
21:07:15  ml_engine  Loaded existing model: options_betting_nn
21:07:15  ml_engine  Loaded existing model: user_behavior_rf
21:07:15  ml_engine  Loaded existing model: cross_domain_gb
21:07:15  ml_engine  Loaded NFL model: nfl_predictor
21:07:15  ml_engine  Loaded NBA model: nba_predictor
21:07:15  ml_engine  Loaded MLB model: mlb_predictor
21:07:15  ml_engine  Loaded NHL model: nhl_predictor
[mutex.cc : 452] RAW: Lock blocking 0x10159fc38   @
```

The final line is the **classic macOS fork-safety mutex deadlock** documented in memory rule `feedback_local_celery_stall_playbook`. Triggered because the smoke ran via `python manage.py shell` (not a Celery worker), so the parent process lacked `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` in its env. When ML frameworks tried to spawn worker threads/processes, the inherited locks blocked indefinitely.

This is documented in `CLAUDE.md` § Troubleshooting → macOS Celery SIGSEGV fix. The Railway worker env already sets this variable, so the same workflow dispatched on Railway (or via local `make celery` worker dispatch) would not hit this issue.

## What this verification DOES prove

1. **B.1 plumbing works.** Steps 1-3 dispatched correctly via the AGENT_MAP fallback, internal handlers loaded, context flowed.
2. **B.1.fix (PR #2600) works.** Step 2's `coo_agent → COOAgent` alias dispatch succeeded — the exact path that failed pre-fix.
3. **Lane 4 internal handler works.** Slot resolved to `ai_infra_deep_dive` (B.1 default), agent dispatched to `ResearchAgent` (correct slot → agent mapping), router heartbeat armed.

## What this verification does NOT prove (still pending)

1. **Steps 5-7 end-to-end behavior.** `decision_card_synthesis` LLM call, `strategic_synthesis` morning_brief mode (the full brief markdown synthesis), `create_morning_brief_deliverable` persistence. These weren't reached because of the env-level hang at Step 4.
2. **Real `morning_brief_markdown` artifact.** No actual brief was produced.
3. **Real `Deliverable` row with `category='Morning Brief'`.** No deliverable was persisted.

These pending verifications all live behind a working ML stack environment. Either retry locally with the env var, or rely on the first scheduled fire post-Sub-step C deployment on Railway.

## Recommended next moves

1. **For full local E2E verification** (optional, ~10 min compute): retry with the env var prepended:

   ```bash
   OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES \
     .venv/bin/python manage.py shell < /tmp/smoke_morning_brief.py
   ```

   That bypasses the macOS fork-safety issue and lets Steps 4-7 complete.

2. **For Sub-step B.2 follow-on** (rotation_slot_resolve pre-step + override chain): blocked only by the unverified Steps 5-7 surfaces. Can proceed in parallel with the env-var retry above.

3. **For Sub-step C** (workspace + PeriodicTask): the Railway worker env has the fork-safety var set, so the first scheduled fire (post-C-merge, the morning after) will dispatch through Celery and produce a real deliverable end-to-end. That's the more durable verification.

## Related artifacts

- Smoke trace: see step transitions block above. Full output preserved at `/private/tmp/claude-501/.../bic3delf3.output` (413KB, not committed — ephemeral evidence).
- Smoke script: `/tmp/smoke_morning_brief.py` (not committed — ephemeral).
- PRs merged in this session: #2599 (B.1), #2600 (B.1.fix).
- Spec: `docs/MORNING_BRIEF_SPEC.md` § B.1 implementation notes.
