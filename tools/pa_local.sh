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
# the --conversation flag below. Current value: Session 1247 fresh
# thread (Rigby create_fresh at S1247 open per S1246 P2 close pin
# pa-2bb73c969fd24802 sitting at 60/suggest_fresh after 26 turns / 7
# topics / 34 unique agents / 2.8h duration). Pin:
# pa-3901b70e61934df7. Title: "Session 1247 — morning_brief P1
# verification + content/char-training retirement". Carry-forward
# seeded MANUALLY post-create_fresh (create_fresh action returned
# empty starter_prompt — filed as PA tool surface finding): S1246
# 2-part close (15 PRs day total, 31-tab workspace audit, 3 BROKEN
# tabs fixed, 1 SLO cleared), S1247 priority queue (P0 health check
# done; P1 TIME-BOUND 13:00 UTC Sunday 06-28 morning_brief CUMULATIVE
# verification via runbook deliverable 421eeaca-…; P2 content/
# char-training full retirement via reachability map deliverable
# c5ea2f61-…; P3 workspace leak watch cf708a2e-…; P4 S1115 #12
# re-audit ~2026-07-13; P5 audit-domain menu), outstanding finding
# list (start-here stale local-trap reference, session_tool
# health_check conversation_id param ignored, session_tool
# create_fresh carry_forward_summary not honored).
# Retired at S1247 open: pa-2bb73c969fd24802 (Session 1246 — both
# parts of the 15-PR day, ended at 26 turns / 13k tokens / score 60 /
# suggest_fresh; multi-topic but coherent — rotated to give S1247 a
# clean focused thread for the time-bound P1 morning_brief
# verification).
# Prior pins retired: pa-0f08fc48ec914917 (Sessions 1234-1235 →
# Session 1236 open; ~50 turns across the 3 sessions covering
# Session 1234 3-arc 22-PR close + Session 1235 9-PR + audit
# Tranche 1 8th PR; health at rotation: 75/continue with rotation
# trigger "before Tranche 2/3/4 implementation". Carries the full
# audit-discovery + Tranche 1 design context — superseded for
# execution work by the fresh thread).
# Retired at S1243 close: pa-634b8fef344d4af2 (Sessions 1241-1243 —
# 3-session continuous thread covering S1241 frontend rot audit +
# S1242 Path C / Cat 5 audit / 6 PRs + S1243 audit-method
# canonicalization / 4 PRs / full Cat 2 cross-app duplicate
# inventory; ended at 34 turns / 17k tokens / score 45 /
# suggest_fresh).
# Older retired pins (Sessions 1234 morning + earlier):
# pa-91cf6bbce1d6406e (Session 1234 morning —
# replaced mid-session when Rigby fresh-started pa-0f08fc48ec914917
# at Chris's direction during the deliverable_tool corpus sweep;
# ~6 turns ResearchAgent dup investigation + early D1/D2 morning
# work / score not pulled at retirement), pa-21dfa3a3dc4545b7 (Sessions 1231-1233 — agent
# error-pattern investigation arc + daily-CoS arc Sub-steps A close +
# B.1/B.2/C build-out; 26 turns / 13k tokens / score 60 / suggest_fresh
# at rotation), pa-4086552cdc9840e9 (Sessions 1229-1230 — Rigby
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
python tools/pa_chat.py "$@" --tools --conversation pa-3901b70e61934df7
