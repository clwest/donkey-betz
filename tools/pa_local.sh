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
# the --conversation flag below. Current value: Session 1900 arc pin
# (Rigby create_fresh at S1900 open — carrying only mission scope,
# no S1800 HumanAttention arc turn context per playbook §16 arc-open
# fresh-thread discipline).
# Pin: pa-2bd1613ce2bd4a9c. Title: "Session 1900 — Group 1900
# Authority Enforcement Design Space parent scoping". Carry-forward:
# mission scope only — Research Group 1900 "Authority Enforcement
# Design Space" per Chris D-override 2026-07-04 of playbook §22
# default queue lean (which had Group 1900 Event / Integration /
# Runtime Architecture next per Group 1800 xx99 §8.1 T0/Gate
# R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES handoff). Rationale: Chris
# line-select signal at platform_architecture_inventory.md:191 —
# §9 STAGE 2 top-1 next-research recommendation per S1273
# (composes S1270 Symbol Mapping + S1271 Actor Identity; four-plane
# governance surface — autonomy / authority / budget / human — with
# PARTIAL maturity + HIGH drift risk; KillSwitch full write path +
# zero enforcement readers per S1273 Rigby v2 review).
#
# **Retired at S1900 open: pa-ae5931ea706b4537** (Sessions 1800-1806 +
# S1899 — Group 1800 HumanAttention / Feedback / Learning research group;
# 8-doc arc: S1800 parent + 6 child audits S1801-S1806 + S1899 xx99
# canonical summary; playbook §11.1 template FIFTH application + §11.2
# 20-section template ELEVENTH application overall + §11.3 12-section
# canonical-summary template SIXTH application + §11.3 §10 meta-
# methodology template SIXTH application. Retired via session_tool.retire
# at S1899 close per playbook §16 arc-close discipline (mirrors S1799
# Group 1700 + S1699 Group 1600 + S1599 Group 1500 + S1499 Group 1400 +
# S1399 Group 1300 arc pin retire precedent); updated_count=23,
# retired=true. SIXTH formal xx99 canonical summary in the Research OS
# library. D48 31st arm turn 1 CLEAN; 26-consecutive-fully-clean-arms
# sub-pattern EXTENDED at S1899 close per MC-2 CODIFICATION-CONFIRMED
# milestone extension. Meta-methodology promotions: MC-1 + MC-2 + MC-3
# CODIFICATION-CONFIRMED; MC-4 + MC-5 CODIFICATION-READY.)
#
# **Retired at S1800 open: pa-e7fbacc996b34b44** (Sessions 1700-1706 +
# S1799 — Group 1700 Observability / Telemetry / SLOs research group;
# 8-doc arc: S1700 parent + 6 child audits S1701-S1706 + S1799 xx99
# canonical summary; playbook §11.1 template FOURTH application + §11.3
# 12-section template FIFTH application + §11.3 §10 meta-methodology
# template FIFTH application. Retired via session_tool.retire at S1799
# close per playbook §16 arc-close discipline (mirrors S1699 Group 1600 +
# S1599 Group 1500 + S1499 Group 1400 + S1399 Group 1300 arc pin retire
# precedent); updated_count: 31, retired: true, previously_active: true.
# **Wrapper hard-code below still points at this retired pin — next
# session MUST rotate at open before any further work per Rigby
# pin_rotation_notice.** Executive Summary verdict: Observability is
# STABLE-at-writers + PARTIAL-at-consumers + UNBOUNDED-at-retention +
# LATENT-at-cross-cat-correlation-spine; six D74 axis cells locked; two
# paired T0/Gate items (RETENTION-UNIFIED-ADR + D74-SPINE-POSTURE); §10
# meta-methodology fifth application with MC-1 + MC-2 both
# CODIFICATION-READY. D48 24th arm HOLDING CLEAN — 19-consecutive-
# fully-clean-arms sub-pattern S1503+…+S1706+S1799 CONFIRMED.)
#
# Retired at S1700 open: pa-f52acf3f8d394faa (Sessions 1600-1699 —
# Content / Deliverables / Publishing research group; 8-doc arc:
# S1600 parent + 6 child audits S1601-S1606 + S1699 xx99 canonical
# summary. Fourth application of playbook §11.3 §10 meta-methodology
# template. Retired at S1699 close via session_tool.retire force=true
# after currently-bound-thread refusal + explicit override per playbook
# §16 final-arc-close discipline; updated_count: 30, retired: true).
# Retired at S1400 open: pa-aa54193f240f4846 (Sessions 1300-1399 —
# Memory / Knowledge / Embeddings research group; 7-session arc:
# S1300 parent + S1301 Cat D + S1302 Cat A+B+C + S1303 Cat F +
# S1304 Cat E↔D + S1305 Cat H + S1399 canonical summary. First
# formal xx99 canonical summary in the library. Ended at 27 turns
# / 13.5k tokens / score 70 / continue at rotation; retiring at
# Group 1400 open per OPEN_ARCS §schema arc-close cleanup rule,
# not because of health signal).
# Retired at S1399 close: pa-4fc3329d0db6484f (Session 1399 SIGN
# isolation pin — canonical-summary Rigby SIGN cycle 1 High
# confidence, 0 must-fix; retired at close per session_tool.retire
# updated_count=2, retired=true).
# Retired at S1300 open: pa-cbcc410b32714f60 (Sessions 1270-1275 —
# symbol_mapping research chain: architecture / actor_identity /
# authority_enforcement / whole-platform inventory / cross-domain
# integration audit / DOMAIN_RESEARCH_PLAYBOOK / option_selection
# (Option E evidence-only) / event_schema_design. 6 research docs
# + 2 index updates over 6 sessions; not health-scored because
# research-only sessions don't stress the tool surface).
# Retired at S1269 close: pa-01e90a1d36f54880 (Sessions 1268-1269 —
# 4-doc S1268 research library arc + S1269 governance/authority
# audit; 5 substantive SIGN turns across the arc; not health-scored
# because research-only sessions don't stress the tool surface).
# Retired at S1267 close: pa-3a226cd451494350 (Sessions 1265-1267 —
# S1265 3-PR hygiene + S1266 Employee #4 readiness audit + S1267
# Bug Triage ship; 21 turns / 10.5k tokens / score 70 / continue
# at rotation — Chris asked for clean runway for V14, not score
# driven). Pre-retirement pin: pa-85960cfecf5e42d5 (Sessions 1258-
# 1264 — S1259-1264 single-day arc covering receipts-gap close +
# claude-code Agent row consolidation + authority warn-mode; 38
# turns / 19k tokens / score 35 / strongly_recommend_fresh at
# rotation).
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
# NOTE on retirement: `session_tool.retire` DOES exist and works cleanly
# (superseded S1213 note — verified S1301 close 2026-07-01 per memory
# rule feedback_session_tool_retire_works.md; Rigby retired SIGN pin
# pa-a23736a833f646cf with updated_count=5, retired=true). Use
# `session_tool.retire conversation_id=<pin>` at arc close per playbook
# §16 arc-close discipline. The Session 1212 stale-thread dispatcher
# audit deliverable 777d9cd8-… remains open as P2 carryover for the
# broader repin-hygiene work, but the retire mechanism itself is
# operational.
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
# **RETIRED at S1999 close 2026-07-04:** pa-2bd1613ce2bd4a9c (Group 1900
# Authority Enforcement Design Space arc pin; retired via session_tool.retire
# per playbook §16 arc-close discipline; updated_count=23, retired=true).
# SIXTH formal arc-pin retirement in Research OS after S1399/S1499/S1599/
# S1699/S1799/S1899. Group 1900 arc closed 6/6 sessions = 100% (S1900 +
# S1901 + S1902 + S1903 + S1904 + S1999). Pin left in wrapper below until
# next-arc open rotates it (or reset to null-arc default per Chris preference).
# Next-arc lean: Group 2000+ Event / Integration Architecture per playbook
# §22 default (inheriting R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES from Group
# 1800 T0/Gate + F.SYMBOL-MAPPING-STATUS-VERIFICATION + F.PER-USER-AUTHORITY-
# MECHANISM from Group 1900 P3 §19) OR Chris D-override selection.
python tools/pa_chat.py "$@" --tools --conversation pa-2bd1613ce2bd4a9c
