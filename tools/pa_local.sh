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
# the --conversation flag below. Current value: Session 1234 mid-
# session fresh thread (Rigby started new conv at Chris's direction
# after the morning_brief first-fire investigation kicked off). Pin:
# pa-0f08fc48ec914917. Session 1234 close (FINAL — two arcs same
# UTC day) health_check returned score=100 / continue — NO rotation;
# carries forward into Session 1235. Session 1234 closed 17 PRs
# total across two arcs. Arc 1 (morning_brief fixes) #2606-#2615
# + #2617 = D1-D8 + cascade checklist. Arc 2 (docs-corpus retrieval)
# #2618-#2625 = D9-D16: type-aware Document enrichment +
# kb_tool action=semantic_search (Rigby's first real semantic
# retrieval action) + min_session=0 LLM-autofill guard + similarity
# threshold tuning + filter-before-slice fix that finally made it
# all work end-to-end. 36 leak-victims archived + 2,729 Documents
# enriched + ~28k DocumentEmbedding chunks (backfill still ramping).
# Workers restarted 16:14 local at session close.
# Session 1234 close (3rd handoff): 22 PRs total across 3 arcs
# (D1-D8 morning_brief fixes, D9-D16 docs-corpus retrieval,
# D17-D21 broad-except sweep). Backfill completed at close: all
# 2,732 Documents embedded (36,854 chunks, 100% coverage). 4-way
# cross-file invariant locks the (DatabaseError, ConnectionError,
# OSError) allowlist across scoped_retrieval, knowledge_first_router,
# knowledge_similarity, views_rag_embeddings; D21 search_personal_
# memories matches that shape via shape-parity test.
# Carryover priorities for Session 1235: morning_brief 2nd-fire
# verify (06-26 13:00 UTC = 07:00 MDT) — first scheduled fire with
# D3/D4/D5/D6 live; ALL lane intermediates should land in MB
# workspace 19807888-…, NOT cf708a2e-… (Session 1231 E2E). Operator
# Edge Friday-1 dry-run (06-26 12:00 UTC). Chris reads the brief;
# Rigby provides audience-fit verdict; Sub-step D polish scope
# derives from that. Optional follow-ups: BACKEND_INVENTORY services
# count drift (only active verifier hit), TextProcessor extracted_
# metadata clobber root-cause, refresh_docs_corpus beat task,
# additional broad-except audits (D22+) if a specific file emerges.
# Chris-side: Anthropic credit refill, CI billing.
# Prior pins retired: pa-91cf6bbce1d6406e (Session 1234 morning —
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
python tools/pa_chat.py "$@" --tools --conversation pa-0f08fc48ec914917
