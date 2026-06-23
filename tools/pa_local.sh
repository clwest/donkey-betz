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
# the --conversation flag below. Current value: Session 1207 (per
# Chris's direct pin: pa-33088358df304016). The earlier-spawned thread
# pa-b2a99ff5b0ee47a6 (Rigby's session_tool create_fresh from this
# session) was superseded by Chris's preferred thread mid-session;
# both carry Session 1207 / Hybrid A+B context. Use this one.
# Prior pins retired: pa-b2a99ff5b0ee47a6 (superseded mid-session),
# pa-234a75abfe374695 (Session 1206 — 5 PRs +
# docs; closed clean), pa-76aa5b61d0764d11 (Session 1205 Evidence-card
# pipeline; PR #2456 closed the cardifier asymmetry),
# pa-1871b37227054254 (Session 1204 Phase B.2),
# pa-d2d0f4c2b6284899 (Session 1203 Phase B.1), pa-123b7d48f01043eb
# (Session 1202 Phase A.2), pa-1ccc494ea00b4e77 (Sessions 1200-1202 §A.1),
# pa-ea12236c83eb4826 (Sessions 1196-1199), pa-92bacb0fbcab44fb (Session 1195),
# pa-e11847db632a4ee8 (Session 1194), pa-a60842917d36 (Session 1184),
# pa-8f8ef45338ce4a24 (Sessions 1182-83).
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
python tools/pa_chat.py "$@" --tools --conversation pa-33088358df304016
