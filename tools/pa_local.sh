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
# the --conversation flag below. Current value: Arc I-0200 arc-scoped
# SIGN pin (session_tool.create_fresh at Arc I-0200 Stage 1 open
# 2026-07-07 per IOS §4.3 Stage 1 arc-open protocol + §15.14 arc-scoped
# pin lifecycle).
# Pin: pa-1b76ee75adbf4031. Title: "ios-arc-open-I-0200". Carry-forward:
# Arc I-0200 contingency-gated seed — default IB-2199-T0-01 (RAG corpus
# substrate maturity gradient) IF Stage 1 confirms severability from
# IB-2199-BOR-01, ELSE auto-switch to IB-1999-T0-01 (Authority per-plane
# posture). Rigby SIGN F1-F8 folds ratified via Chris "Agree All"
# 2026-07-07. Ratification record: `docs/research/implementation/
# RATIFICATION_2026-07-07_second_arc_I-0200.md`. Prior legacy pins:
# pa-44a6eb70d8814e34 (T4 Group 1700 Observability, paused-research per
# §15.14 phase-transition supersession — preserved as comment above
# --conversation line for restoration at Arc I-0200 close);
# pa-6a4e2eff5594486b (Arc I-0200 selection SIGN review; retired
# 2026-07-07 post-Chris-Agree-All).
# Load-bearing inputs at S1700 open: PA-slice envelope-shape telemetry
# emit-signature (Cat D AC-D8 canonical candidates: pa.ws.envelope.
# conformance.grade + pa.ws.unauthorized_connect.count +
# pa.ws.emit.latency_histogram + pa.ws.agent_completed.
# reconciliation_delta) + per-Consumer conformance metrics for 4
# PA-related Consumers at HEAD + doc_claim_verification 4-child
# convergent PA-slice claim registration hooks (AU-DCV-1) + audit-log
# hook signature + emit-point observability plane for Cat C1 Path
# C+compensating (DEBT-C1-4 "SINGLE MOST IMPORTANT" per Rigby SIGN
# Batch 2 Q3(e) at S2603 close) + optional cross-arc reconciliation-
# layer ownership decision (§9.1a options i/ii/iii). Prior legacy pin:
# pa-c17a8d7e0660413b (Group 2600 PA arc).
#
# **Retired at S2699 xx99 close: pa-c17a8d7e0660413b** (Sessions
# 2600-2604 + S2699 — Group 2600 PA (Cross-Arc Handoff Bundle
# Consuming CF-2600-PA + CF-D6 + F-B-HIGH-3 + Workspace-Context Authz
# + REST↔WS T7 Joint Dual-Owner PA Side) research group; 6-doc arc:
# S2600 parent scoping + S2601 P1 Cat A PA Endpoint Contract SoT
# Design-Prep + S2602 P2 Cat B PA-Client Contract Surface Design-Prep
# + S2603 P3 Cat C PA Workspace-Context Authz + Session-Lifecycle
# Design-Prep (2 parallel sub-tracks C1+C2) + S2604 P4 Cat D PA
# REST↔WS T7 Joint Contract SoT (dual-owner PA side) Design-Prep +
# S2699 xx99 canonical summary; playbook §11.1 SEVENTH-consecutive
# parent-with-4-children application + §11.2 20-section child-audit
# template TWENTY-FIRST → TWENTY-FOURTH consecutive at Cat A/B/C/D +
# §11.3 12-section canonical-summary template THIRTEENTH-consecutive
# candidate + §11.3 §10 5-subsection meta-methodology template
# THIRTEENTH-consecutive candidate (adopted S1399 close 2026-07-01;
# unbroken S1399→S2699 chain). Retired via session_tool.retire at
# S2699 close per playbook §16 arc-close discipline; ELEVENTH formal
# arc-pin retirement in Research OS after S1399/S1499/S1599/S1699/
# S1799/S1899/S1999/S2099/S2199/S2299/S2499/S2599 twelve prior
# (Group 2400 Auth S2499 close + Group 2500 API S2599 close bracket
# Group 2600 PA). THIRTEENTH formal xx99 canonical summary in the
# Research OS library. Runtime target 6 sessions ACHIEVED — 6/6 = 100%;
# runtime cap 8 never invoked. Canonical arc-close verdict: "PA
# subsystem MECHANISM is OPERATIONAL across all four contract planes
# (REST endpoint dispatch, client consumption, workspace-context
# resolution, and WS envelope broadcast); PA subsystem DECLARATION/SoT
# is consistently partial/implicit across all four planes; arc-close
# diagnosis is design-plane governance + compensating-controls policy,
# NOT systemic runtime failure. Structural signature: this arc's
# closure criterion treated compensating-controls as required whenever
# SoT claims were not enforceable at runtime (Cat C1 F5+F-C7 + Cat D
# F-D1 F5-analog HARD-INVALID / NON-SELECTABLE for Path C-pure)."
# Chris "agree all" 2026-07-06 wholesale ratifications: shape-card
# SIGN-preview 14+ folds + SIGN cycle 1 13 folds + 3 sub-tighteners
# per S2699 close. Retired via session_tool.retire per playbook §16.
# Consumes 4 CF-* originated S2501-S2504: CF-2600-PA (S2501 Cat A) +
# CF-D6 (S2504 Cat D REST↔WS T7 joint). Selected over 1700
# Observability / 2300 Mobile (parallel) / 1600 Content per T-slot
# queue T3 assignment at S2599 xx99 close. Health check at open:
# platform_config_tool overview = service_context: local ✓ +
# session_tool create_fresh = pa-c17a8d7e0660413b ✓ (S2600 arc-open
# turn 1, 2026-07-06). THIRTEENTH formal arc pin under Research OS
# after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200/
# 2400/2500 prior twelve. TWELFTH-consecutive parent-with-children
# arc under Research OS.
#
# ---- HISTORICAL LEDGER (chronological, newest first) ----
#
# **S2500 arc opened 2026-07-05 (pa-a03b111768464b3f):**
# Selected over 2300 Mobile / 2600 PA
# per highest cross-arc-handoff-frequency signal (4/4 Group 2200
# children referenced API contract discipline — S2203 F1 SoT-ABSENT +
# F3 silent-401 SYSTEMIC + F4 mega-module api.ts 4194-LOC + F5 18
# DEAD-CANDIDATE modules; ALL 4 Cat A/B/C/D children of Group 2400
# emitted CF-*1 flags to Group 2500 — refresh endpoint + logout
# envelope + Clear-Site-Data + typed-error-envelope + per-endpoint
# permission registry design-prep + drf-spectacular retrofit).
# Scopes (per S2500 parent scoping to be ratified this session):
# backend API contract SoT (drf-spectacular platform-wide retrofit;
# sports/views.py 16 @extend_schema decorators + core/*.py 0
# decorators baseline per S2203 F1) + money-path API surface
# (placeBetMutation + revenueApi + incomeBuilderApi + distributionApi)
# + governance-path (decisionsApi + dreamsApi + advisorsApi +
# platformApi) + PA-path (assistantApi + /pa/chat/*) + refresh
# endpoint contract (F-C-REFRESH-1 downstream) + logout envelope +
# Clear-Site-Data emission (F-C-CSD-1) + typed-error-envelope Cat D
# α/β/γ input + per-endpoint permission registry Cat B c input +
# api.ts extraction (S2203 R4; 4194-LOC + 93 exports + 407-session
# churn) + REST↔WS message contract joint 2500+2600 (S2203 T7 +
# S2202 T6). ELEVENTH-consecutive parent-with-children arc under
# Research OS. TWELFTH formal arc pin under Research OS after
# Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200/2400
# prior eleven. Health check at open: platform_config_tool overview
# = service_context: local ✓ + session_tool create_fresh =
# pa-a03b111768464b3f ✓ (S2500 arc-open turn 1, 2026-07-05).
#
# **S2500 arc CLOSED at S2599 xx99 close 2026-07-06.** Pin
# pa-a03b111768464b3f RETIRED via session_tool.retire force=true
# (updated_count=1, retired=true, previously_active=true). TWELFTH
# formal arc-pin retirement in Research OS after S1399/S1499/S1599/
# S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2499 eleven prior. TWELFTH
# formal xx99 canonical summary in the Research OS library. Runtime
# target 6 sessions ACHIEVED — 6/6 = 100%; runtime cap 8 never invoked.
# SIXTH-consecutive parent-with-4-children arc (Groups 1900 + 2000+ +
# 2100 + 2200 + 2400 + 2500) — MC-4 CODIFICATION-CONFIRMED-with-scope-
# guardrails extended. Canonical seam statement: "MECHANISM working at
# file-precision + DECLARATION SoT absent or non-uniform across all
# four contract axes (backend schema + consumer typing + error envelope
# + permission-floor + WS message contract); majority IMPLICIT-
# INHERITANCE with ISLAND-DECLARATION pockets and ZERO cross-transport
# SoT; gap is design-plane governance, not runtime failure." Chris
# "commit it" 2026-07-06 ratified xx99 SIGN-with-edits wholesale (5
# folds — 1 Q1 STRENGTHEN §3.1+§5.2 route-indexed vs coverage-rate
# clarifier + 1 Q2 AGREE-optional §7.1 AU-1 D1-D6 naming + 1 Q3
# STRENGTHEN §4.2 4-shape→SHAPE-BLIND→803 pipeline sentence + 1 Q4
# STRENGTHEN §8.1 blocking-vs-non-blocking dependency clarifier + 1
# understated-maturity STRENGTHEN §3.1 WS auth-middleware uniformity
# row). Rigby SIGN cycle 1 SIGN-with-edits at HIGH confidence via
# dedicated fresh SIGN isolation pin pa-59d9583dc4da4d5e (TWENTY-SECOND
# consecutive dedicated fresh SIGN pin retirement in Research OS after
# S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/
# S2401/S2402/S2403/S2404/S2499/S2500/S2501/S2502/S2503/S2504 twenty-
# one prior). **Wrapper hard-code at line 312 still points at this
# retired pin — next arc-open session (Group 2600 PA) MUST rotate at
# open before any further work per S2500 parent scoping deferral +
# Rigby pin_rotation_notice precedent (mirrors S1700 → S1800 open
# pattern documented at retired-S1800 stanza above).** T-slot queue
# advances: T3 Group 2600 PA (NEXT) → T4 Group 1700 Observability →
# T5 Group 2300 Mobile (parallel) → T6 Group 1600 Content per §8.2
# xx99 canonical summary. Meta-methodology: §11.3 §10 5-subsection
# meta-methodology template TWELFTH-consecutive application preserved.
#
# **Retired at S2500 open: pa-6279ead1714c4630** (Sessions 2400-2404
# + S2499 — Group 2400 Auth Session Lifecycle + Permission Floor +
# Silent-401 Resolution research group; 6-doc arc: S2400 parent +
# S2401 P1 Cat A Authentication Surface + S2402 P2 Cat B Authorization
# / Permission-Floor Uniformity + S2403 P3 Cat C Session Lifecycle +
# S2404 P4 Cat D Frontend Integration / Silent-401 SYSTEMIC Resolution
# + S2499 xx99 canonical summary; playbook §11.1 template ELEVENTH
# application + §11.2 20-section template FOURTEENTH application
# overall + §11.3 12-section canonical-summary template ELEVENTH
# application + §11.3 §10 meta-methodology template ELEVENTH
# application. Retired via session_tool.retire force=true at S2499
# close per playbook §16 arc-close discipline; updated_count=25,
# retired=true, previously_active=true. ELEVENTH formal arc-pin
# retirement in Research OS. ELEVENTH xx99 canonical summary in the
# Research OS library. Runtime target 6 sessions ACHIEVED — 6/6 =
# 100%. Canonical verdict: "ACCRETION with declared-but-unenforced
# contracts" — Chris "commit it" 2026-07-05 ratified xx99 SIGN-with-
# edits (4 folds Q1 minor tightening + Q2 MC-4 methodological-not-
# platform-state + Q2 §10.4 MC-14 threshold rule + Q3 §10.2
# conditional promotion rule). Rigby SIGN cycle 1 SIGN-with-edits at
# HIGH confidence (~0.88 — HIGHEST in Group 2400 arc; monotonically-
# increasing confidence across arc). 19 findings STILL-LIVE at HEAD
# for T2 Group 2500 API arc + T3 Group 2600 PA + T4 Group 1700
# Observability distribution. Meta-methodology: §10.2 MC-14 threshold-
# rule + §10.2 §10 conditional-promotion-rule + Cat A CF-3 roll-up +
# Cat B/C/D CF-B/C/D1 seven-flag umbrella all CODIFICATION-READY.)
#
# **Retired at S2000 open: pa-2bd1613ce2bd4a9c** (Sessions 1900-1904 +
# S1999 — Group 1900 Authority Enforcement Design Space research group;
# 6-doc arc: S1900 parent + S1901 P1 Cat A Actor Role Propagation Design
# + S1902 P2 Cat B Authority Enforcement Design Decision + S1903 P3 Cat C
# Cross-Plane Composition Design + S1904 P4 Cat F Adjacent / Separation
# Boundaries CONSOLIDATION + S1999 xx99 canonical summary; playbook §11.1
# template SIXTH application + §11.3 12-section canonical-summary template
# SEVENTH application + §11.3 §10 meta-methodology template SEVENTH
# application. Retired via session_tool.retire at S1999 close per playbook
# §16 arc-close discipline; updated_count=23, retired=true. SEVENTH formal
# xx99 canonical summary in the Research OS library. Runtime target 6
# sessions ACHIEVED — 6/6 = 100%; runtime cap 8 never invoked. D48 37th arm
# turn 1 CLEAN → 32-consecutive-fully-clean-arms sub-pattern EXTENDED at
# S1999 SIGN cycle 1 per single-batch-4-question criterion (MC-2
# CODIFICATION-CONFIRMED milestone extended 31 → 32 consecutive). Meta-
# methodology promotions: MC-4 CODIFICATION-CONFIRMED with scope guardrails
# + MC-5 CODIFICATION-CONFIRMED + MC-6 CODIFICATION-READY.)
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
export PA_API_TOKEN=[REDACTED - HISTORICAL SECRET]
# **ACTIVE at S2400 open 2026-07-05:** pa-6279ead1714c4630 (Group 2400
# Auth arc pin — minted at S2400 open via session_tool.create_fresh
# per playbook §16 arc-open fresh-thread discipline). ELEVENTH formal
# arc under the Research OS after Groups 1300/1400/1500/1600/1700/1800/
# 1900/2000+/2100/2200. Chris D-override at S2299 close 2026-07-05
# ("agree all + (6) = 2400 Auth") ratified Auth over any playbook §22
# default queue lean, per highest cross-arc-handoff-frequency signal
# (4/4 Group 2200 children reference silent-401 + logout cleanup +
# session lifecycle + permission-floor uniformity — S2201 §14.3 +
# §15.5 + S2202 no-drift-but-perms-floor-owned-here + S2203 §14 F3 +
# F3.5 + S2204 §19.1 R1). Load-bearing inputs: S2299 §8.2 T1 Group
# 2400 Auth cross-arc handoff bundle + §3.27 Auth / Permissions /
# Security prior-coverage row (LIGHT research coverage + PARTIAL
# maturity per Rigby S1273 review; VIP demo prompt-only + Fleet
# permissive fallback + no threat-model/trust-boundary doc). Scopes
# (per S2400 parent scoping to be ratified this session): authentication
# surface + authorization + trust boundaries + session lifecycle +
# frontend integration. TENTH-consecutive parent-with-children arc —
# MC-4 dial-back-resolution 5th confirming arc candidate (Group 2400
# Auth 4-child structure would trigger resolution of S2199 Q3
# STRENGTHEN dial-back per §5.3 Group 2200 canonical summary). Health
# check at open: platform_config_tool overview = service_context: local
# ✓ + session_tool create_fresh = pa-6279ead1714c4630 ✓ (S2400
# arc-open turn 1).
# **Retired at S2400 open: pa-f7fd5016600f4513** (Sessions 2200-2204 +
# S2299 — Group 2200 Frontend (Contract-Surface Arc) research group;
# 6-doc arc: S2200 parent + S2201 P1 Child A Routes+Pages+Layouts+
# Component Patterns + S2202 P2 Child B WebSocket Consumer Surface +
# ui.render_hint Envelope + S2203 P3 Child C Frontend↔Backend API
# Contract + Boundary Discipline + S2204 P4 Child D Session-scoped
# State Management + Persistence Discipline + S2299 xx99 canonical
# summary; playbook §11.1 template NINTH application + §11.3 12-section
# canonical-summary template TENTH application + §11.3 §10 meta-
# methodology template TENTH application after S1399/S1499/S1599/S1699/
# S1799/S1899/S1999/S2099/S2199 prior nine. Retired via session_tool.retire
# at S2299 close per playbook §16 arc-close discipline; TENTH formal
# arc-pin retirement in Research OS after S1399/S1499/S1599/S1699/S1799/
# S1899/S1999/S2099/S2199. TENTH formal xx99 canonical summary in the
# Research OS library. Runtime target 6 sessions ACHIEVED — 6/6 = 100%;
# runtime cap 8 never invoked. Canonical seam statement: "accreted UI
# mesh with declared-but-unenforced contracts — structurally healthy at
# the routing / auth-wrapper / layout / Zustand-persist boundary but
# structurally under-specified at the page-component / consumer-contract
# / API-typing / state-discipline boundary — three of four contract-
# surface axes SYSTEMIC with surface variance + one axis SURFACE-LOCAL
# + DOMAIN-SPECIFIC HYBRID confined to /betting; fix path = wiring the
# design-latent contract infrastructure through cross-arc coordination
# with Group 2400 Auth + Group 2500 API + Group 2600 PA + Group 1700
# Observability, not framework migration." Chris "agree all + (6) =
# 2400 Auth" 2026-07-05 ratified all 6 close-card items wholesale —
# including next-arc D-override = Group 2400 Auth per highest cross-
# arc-handoff-frequency signal.)
# Retired at S2199 close: pa-18b095bb7c4740be (Group 2100 RAG /
# Document Loading — Knowledge Loop arc pin; NINTH formal arc;
# NINTH formal arc-pin retirement in Research OS after S1399/S1499/
# S1599/S1699/S1799/S1899/S1999/S2099; retired via session_tool.retire
# per playbook §16 arc-close discipline. 6-doc arc: S2100 parent +
# S2101 P1 Corpus State + S2102 P2 Ingestion Pipeline + S2103 P3
# Retrieval Authority Framework + Governance Design + S2104 P4
# Behavior Substrate Structured Observation + Integration + S2199
# xx99 canonical summary. NINTH xx99 canonical summary in the Research
# OS library. Runtime target 6 sessions ACHIEVED — 6/6 = 100%.)
# Retired at S2099 close: pa-dd7e973617da464d (Group 2000+ Event /
# Integration Architecture arc pin — SEVENTH formal arc; EIGHTH formal
# arc-pin retirement in Research OS after S1399/S1499/S1599/S1699/S1799/
# S1899/S1999; retired=true, updated_count=35, previously_active=true
# via session_tool.retire per playbook §16 arc-close discipline).
# ---
# Retired at IOS Part 11 first-queue-ratification close 2026-07-06:
# pa-39d3694312ab4326 (ios-part11-first-queue-ratification-v1)
# — TWENTY-FIRST consecutive dedicated fresh SIGN pin retirement
# under Research OS/IOS combined discipline; FIRST post-active-IOS
# pin retirement per IOS v1.1 §15.14 (Part 11 Step 6 Rigby routing
# lifecycle). Retired via session_tool.retire force=true; updated
# 2 rows. Post-retirement: --conversation rotated back to
# paused-research T4 Group 1700 Observability pin per §15.14
# restoration rule (Arc I-0100 Stage 1 not yet open; opens next
# session per 00-START-NEXT-SESSION.md sequence). On Arc I-0100
# Stage 1 open next session, mint fresh arc-scoped pin via
# session_tool.create_fresh label='ios-arc-open-I-0100' and rotate
# --conversation to that pin. If Chris re-enters research phase via
# Research OS command instead, the T4 pin remains active as-is.
# ---
# Retired at Arc I-0100 Stage 6 close 2026-07-07:
# pa-c5b235f7b15f45be (ios-arc-open-I-0100 — Arc I-0100 Observability
# correlation spine + mission evidence substrate; Stage 1 opened
# 2026-07-06 S2700; Stage 6 closed 2026-07-07 via close doc
# `I-010099_observability_spine_implementation_close.md` in PR #2976).
# FIRST fresh arc-scoped implementation-pin retirement in Research OS
# + IOS combined discipline; retired via `session_tool.retire
# conversation_id=pa-c5b235f7b15f45be` routed through the restored
# paused-research T4 pin `pa-44a6eb70d8814e34` per §15.14 restoration
# rule + FIRST post-active-IOS arc-pin retirement per IOS §7.2
# isolation-pin discipline. Terminal intake dispositions on retirement:
# P2 IB-1799-T1-01 SHIPPED (#2954); P3 IB-1799-T1-03 LOCAL_ACCEPTED /
# PRODUCTION_DEFERRED (#2957 + #2974 + #2975); P4 IB-1799-T1-02
# LOCAL_ACCEPTED / PRODUCTION_DEFERRED (#2955 + #2970 + #2973). Both
# runtime flags remain `false` by default. Operating model: LOCAL-only
# per PR #2972 guardrail.
# ---
# Retired at Arc I-0200 selection SIGN close 2026-07-07:
# pa-6a4e2eff5594486b (ios-arc-open-I-0200-sign-review) — Arc I-0200
# second-arc selection SIGN review pin; minted 2026-07-07 at Chris
# directive to route Claude's IOS Part 11 ranking through Rigby SIGN
# before Chris ratification; Rigby returned SIGN-with-edits MED
# confidence with 8 folds F1-F8 (2199-provisional-pending-severability
# + re-score-without-contested-boosts + BOR-classification-at-Stage-1
# + auto-switch-to-1999-on-BOR-fail + remove-+2-bump + deterministic-
# fallback-1999 + re-rank-if-severable-but-bumped + 1999-T1-01-blocker-
# type-classification); Chris "Agree All" recorded 2026-07-07 —
# ratifies contingency structure (default seed IB-2199-T0-01 if
# severable from IB-2199-BOR-01; auto-switch to IB-1999-T0-01 if not
# severable); retired via `session_tool.retire force=true` post-
# ratification, updated_count=4, retired=true, previously_active=true.
# SECOND consecutive dedicated fresh SIGN pin retirement under IOS
# active discipline after `pa-39d3694312ab4326` (first-queue-
# ratification). Ratification record: `docs/research/implementation/
# RATIFICATION_2026-07-07_second_arc_I-0200.md`.
# ---
# PRESERVED AS COMMENT / paused-research during Arc I-0200 phase
# (per IOS v1.1 §15.14 phase-transition supersession rule; pin
# unchanged since 2026-07-06 arc-lifecycle preservation; restored to
# ACTIVE 2026-07-07 at Arc I-0200 Stage 6 close per §15.14 restoration
# rule mirroring Arc I-0100 PR #2978 pattern):
# pa-44a6eb70d8814e34 (T4 Group 1700 Observability research arc pin;
# implementation-phase supersession terminated 2026-07-07). Research-
# phase re-entry available via Chris explicit `Start / Continue /
# Close research group NNNN` directive.
# ---
# Retired at Arc I-0200 Stage 6 close 2026-07-07:
# pa-1b76ee75adbf4031 (ios-arc-open-I-0200 — Arc I-0200 RAG corpus
# substrate maturity gradient; Stage 1 opened 2026-07-07 S2701;
# Stage 6 closed 2026-07-07 via close doc
# `I-020099_rag_corpus_substrate_maturity_implementation_close.md`
# in this Stage 6 close PR). SECOND fresh arc-scoped implementation-
# pin retirement in Research OS + IOS combined discipline (after
# `pa-c5b235f7b15f45be` from Arc I-0100 close PR #2977); retired via
# `session_tool.retire conversation_id='pa-1b76ee75adbf4031'
# force=true` routed through the restored paused-research T4 pin
# `pa-44a6eb70d8814e34` per §15.14 restoration rule. Terminal intake
# disposition on retirement: IB-2199-T0-01 SHIPPED (I-0200) with
# adr_ref: ADR-0004 + pr_refs: #2984. Operating model: LOCAL-only
# per PR #2972 guardrail (unchanged from Arc I-0100).
# ---
# ACTIVE (restored 2026-07-07 to paused-research T4 Group 1700
# Observability pin per IOS v1.1 §15.14 restoration rule at Arc I-0200
# Stage 6 close; unchanged pin identity — the pin was never retired,
# only paused per §15.3 phase-transition supersession while Arc I-0200
# was active):
# pa-44a6eb70d8814e34 (T4 Group 1700 Observability research arc pin
# — arc-open pending until Chris explicitly re-enters research via
# Research OS command `Start / Continue / Close research group NNNN`).
# On any future implementation-phase arc open, mint a fresh
# arc-scoped pin via `session_tool.create_fresh label='ios-arc-open-
# I-NNNN'` and rotate --conversation to that pin; the T4 pin is
# preserved as-is for research-phase re-entry.
# Session 2735 conversation-lifecycle checkpoint (2026-07-09):
# Retired the long-lived T4 Group 1700 Observability pin
# `pa-44a6eb70d8814e34` after it accumulated 100+ messages and 70+
# tool calls across multiple campaigns (Platform Closure, HAI
# Delivery Fanout, Cost Protection, Beat Schedule Health). Chris
# formalized the new conversation-lifecycle rule: "conversations are
# compute, not memory. Permanent memory lives in repository /
# Workspace / Deliverables / docs / RAG / Playbook / retrospectives."
#
# Retirement triggers going forward:
# - campaign completed
# - PR merged + cascade complete
# - SIGN complete
# - deliverable finalized
# - conversation exceeds ~50 messages
# - conversation exceeds ~40 tool calls
# - Claude or Rigby detects context drift risk
#
# 20 stale campaign/SIGN/verify pins retired in the same operation
# via session_tool.retire (see the process-checkpoint report in the
# corresponding closeout deliverable for the full list).
#
# New default: pa-fe6e8eca232c4903 (label
# 'engineering-session-post-process-checkpoint'). This becomes the
# next-campaign starting pin until it too hits a retirement trigger,
# at which point mint a fresh one via session_tool.create_fresh and
# update this line.
#
# S2748 open (2026-07-10): retired S2747 pin `pa-cd35bde16f974843`
# via session_tool.retire (updated_count=1, previously_active=true).
# Minted fresh `pa-59d27abadeed4411` label 'ios-arc-open-I0302-P4'
# for the I-0302 Phase 4 (regression harness for RUR-C1 parent
# invariant) arc. Prior pin `pa-43818ab8ba144a2f` preserved above
# as comment (rotated from at S2748 open).

# ── S2776 N21: wrapper token/pin ownership check ──
# First invocation per pin verifies PA_API_TOKEN + wrapper pin resolve
# to the same user. Cache at ~/.claude-pa-verified/<pin>.json marks the
# pin as verified so subsequent invocations skip the check.
# Escape hatch: PA_LOCAL_ALLOW_MISMATCH=1 → warn but continue (for
# emergency close-ceremony continuity when a mismatch is expected).
# Exit codes: 0 verified · 2 mismatch · 3 token invalid · 4 orphan pin.
_pa_cache_dir="${HOME}/.claude-pa-verified"
_pa_pin=$(grep -oE 'conversation pa-[a-f0-9]{16}' "$0" 2>/dev/null | head -1 | awk '{print $2}')
if [ -n "$_pa_pin" ]; then
  mkdir -p "$_pa_cache_dir"
  if [ ! -f "$_pa_cache_dir/${_pa_pin}.json" ]; then
    if ! python manage.py verify_pa_wrapper_ownership --pin "$_pa_pin"; then
      _pa_ec=$?
      if [ "${PA_LOCAL_ALLOW_MISMATCH:-0}" = "1" ]; then
        echo "[pa_local] ⚠ ownership verify failed (exit $_pa_ec) — PA_LOCAL_ALLOW_MISMATCH=1 override in effect, continuing" >&2
      else
        exit $_pa_ec
      fi
    fi
  fi
fi

python tools/pa_chat.py "$@" --tools --conversation pa-7a5fff1efe2944bb
