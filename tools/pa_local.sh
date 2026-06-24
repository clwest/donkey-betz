#!/bin/bash
# Local PA chat shortcut.
#
# Session 1098 fix: token + conversation_id belong to donkeyking (the
# account Chris is logged into via the ChatUI). Previously this wrapper
# pointed at admin's token + conversation_id, which silently routed all
# Claude Code → Rigby chatter to an account Chris couldn't see in the
# UI. Memory rule: pa_chat.py defaults to PROD; this wrapper forces
# LOCAL + the right user.
#
# Session 1165 update: the local DB no longer has a `donkeyking` user
# (only `chris`, `system`, `system_autonomous`). The wrapper now points
# at chris's token + conversation; both pinned conversations
# (pa-f93d77e34f5d and pa-7684c8f93185) are owned by chris. Rigby's
# Session 1165 verdict on the drift: "Unexpected — flag it. Token +
# conversation ownership should match `chris` if that's the operator
# account." Memory rule: feedback_pa_local_verify_ownership.md.
#
# To change the default conversation (e.g., start a new thread), edit
# the --conversation flag below. Current value: Session 1231 — Fresh
# thread (carry-forward from pa-4086552cdc9840e9). Pin:
# pa-21dfa3a3dc4545b7. Rotated at Session 1230 close after
# health_check returned score=45 / suggest_fresh at 38 turns / 19k
# tokens / 2.5h. Carry-forward seed for the new conv: Session 1230
# closed (4 PRs merged: #2580 COOAgent semantic title, #2581 CTO/
# Trend sibling wiring, #2582 engineer request_mode + clarification-
# stall contract, #2583 handoff) + agent system audit deliverable
# 5318da3e-5ac1-43af-9160-d7505ff7c428 live in DBZ workspace (33,786
# chars). Chris answered R1: SportsOddsAnalyst cascade is upstream
# odds-API credit-exhaustion, not platform bug — revised R1 action
# is circuit-break env var pattern. Workers bounced twice during
# Session 1230 for P1+P4 wiring.
# Carryover priorities for Session 1231: Outreach beat first-fire
# verification 2026-06-25 13:30 UTC, Operator Edge Friday-1 dry-run
# check 2026-06-26 12:00 UTC, COOAgent scheduled 'files_generated'
# KeyError investigation (HIGH — daily diagnostic silently failing),
# deliverable_tool.append updated_at gap fix, engineer workspace
# staleness, audit R2 (CodeReview + Workflow error_message distros),
# audit R3 (wire 12 silently-failing-invisible agents to
# _save_to_deliverable). Chris-side: Anthropic credit refill, odds
# API credit refill, CI billing.
# Prior pins retired: pa-4086552cdc9840e9 (Sessions 1229-1230 — Rigby
# tool-surface verification arc + Session 1230 diagnostic-leak close +
# engineer request_mode + agent system audit; 38 turns / 19k tokens /
# score 45 / suggest_fresh at rotation), pa-08bdd7c9b348415a (Sessions 1226-1229 — agent_name
# canonicalization + verifier-loop audit + Session 1227 §4.6 deliverable_tool
# surface additions stack + Session 1228 LLM-autofill class sweep + Session
# 1229 P4 close + workers-bounce; 33 turns / 16.5k tokens / score 35 /
# strongly_recommend_fresh at rotation), pa-17e0fa71fd25470a (Sessions 1223-1225 — 2-session
# continuous thread covering audit sweep + watchdog burn-in + full outreach
# arc + hygiene initiative + token budget sweep; ended mid-Session 1225 at
# 39 turns / 19.5k tokens / score 45 / suggest_fresh), pa-58737666f25741dc
# (Sessions 1217-1222 — 6-session
# continuous thread, ended at 44 msgs / 22k tokens / strongly_recommend_fresh;
# Session 1217 self-directed audit experiment seeded the 15-finding
# deliverable, Sessions 1218-1222 closed 11/15 + both CI lints flipped
# to enforce mode), pa-e37fe30dc7b941a6 (Sessions 1214-1216 — OpenAI
# caller alignment spec 2b9aa447-…, full 5-phase arc shipped across 3
# single-day sessions, 15 PRs merged, catalog deliverable bb775acb-…
# maintained at 17,068 chars; closed clean with all 6 Rigby AC signals
# confirmed), pa-61c7b47d201d4591 (Sessions 1209-1213), pa-2d74e36cc3a04787
# (Session 1208), pa-33088358df304016 (Session 1207),
# pa-b2a99ff5b0ee47a6 (superseded mid-Session 1207), pa-234a75abfe374695
# (Session 1206), pa-76aa5b61d0764d11 (Session 1205), pa-1871b37227054254
# (Session 1204), pa-d2d0f4c2b6284899 (Session 1203), pa-123b7d48f01043eb
# (Session 1202 §A.2), pa-1ccc494ea00b4e77 (Sessions 1200-1202 §A.1),
# pa-ea12236c83eb4826 (Sessions 1196-1199), pa-92bacb0fbcab44fb (Session 1195),
# pa-e11847db632a4ee8 (Session 1194), pa-a60842917d36 (Session 1184),
# pa-8f8ef45338ce4a24 (Sessions 1182-83).
#
# NOTE on retirement: session_tool has no `retire` action (Rigby surfaced
# at Session 1213 close). "Retirement" = stop using the old thread +
# repin here. The fact that no explicit retire mechanism exists is exactly
# what Session 1212 stale-thread dispatcher audit deliverable 777d9cd8-…
# is about (~$3.60/day wasted on retired-thread dispatches). P2 carryover.
#
# IF YOU MANUALLY RESTART A CELERY WORKER (not via `make celery`):
# pass PA_USE_FUNCTION_CALLING=true in the env. Without it, the PA
# worker drops to keyword routing and source=claude-code messages
# short-circuit to the claude_code_coordination intent which has NO
# tool path — Rigby returns text-only "I don't have tool access"
# responses despite tools being wired. See
# feedback_pa_worker_function_calling_env.md memory.
export PA_API_URL=http://localhost:8000
export PA_API_TOKEN=4b458900136c83dd49b869b80e08b1e5d2967a4c
python tools/pa_chat.py "$@" --tools --conversation pa-21dfa3a3dc4545b7
