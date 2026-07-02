---
title: "Architecture Research Index — front page of Donkey Betz's engineering encyclopedia"
status: active
authority: navigation
session_added: 1268
last_verified: 2026-07-02 (v38 — **Group 1600 Cat D child audit LANDED at S1603.** §1.41 `domains/content/1603_content_deliverable_base_variants_audit.md` added (third child audit under Group 1600 per D66 P3 slot; F3 fold: Cat D moved from P4 → P3 because Cat C's gate semantics consume Cat D's canonical object-model decision D65a-analog; playbook §11.2 20-section template + 6-parallel-Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 22 pre-Explore + 6 post-Explore load-bearing binary claims). Third sibling of Group 1600 to propagate parent D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront at §4.8 + §5.6 + §6.5 + §8.5 per D68 F8/F10 folds. **D65a HEADLINE structural evidence:** grep-verified NO reverse FKs from any variant to Deliverable base — all 5 variants (SelfBlog + OutreachDraft + ClosePack + SportsBettingBrief + BlockchainAuditBrief) are **structural islands**; `publish_intent` enum only on Deliverable base :131-136. F6-reframed as 3-category neutral taxonomy (envelope-integrated / standalone-by-design / unfinished-orphan) NOT normative integration-blocker claim. Central factory adoption ~98% at Deliverable base level; 0% at variants. **F1 RESOLVED** shadow-`create_deliverable` in `real_job_execution_consumer.py:200` is name-collision demo (returns plain dict for demo WebSocket UI; never touches ORM; NOT factory bypass). **HIGH+CRITICAL debt confirmed at HEAD:** T.15.2 SportsBettingBrief WRITE-ONLY-FORGOTTEN (S1504 §14.3 pattern extension); T.15.3 BlockchainAuditBrief same pattern; T.15.4 OutreachDraft delivery MISSING F8-upgrade HIGH → CRITICAL (S1402 F.B1 CONFIRMED at HEAD); T.15.1 SelfBlog canonical bypass at runner:401 HIGH (16+ sites; factory invariants ALL skipped); T.15.6 Triple-gate composition contract MISSING F7+F11-reframed as boundary_violation (5-gate factory + PublishGate 4-threshold + SelfBlog own gate — no canonical precedence). **NEW T1 evidence recommendations:** T1 R.CONTENT.VARIANT-CATEGORIZATION-CLARIFICATION (F12 fold — bridge artifact for xx99 D65a consumption); T1 R.CONTENT.CANONICAL-CREATION-CONTRACT (F13 fold — factory + creation-funnels reconciliation); T1 R.CONTENT.OUTREACHDRAFT-DELIVERY upgraded T2 → T1 (F14 fold — revenue-critical). Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence 2026-07-02 (upgraded to High via F1 resolution) on fresh isolation pin `pa-8af9063864bf4a7f` (retired at S1603 close: `updated_count: 5, retired: true`). **F1-F18 folds landed pre-commit.** **D48 preemptive stability-probe gate 12th-arm outcome:** batches A/B/C substantive on fresh isolation pin + final-verdict single-question follow-up clean; **seven-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603 CONFIRMED** — extends 11-arc pattern to 12-arc + S1603. Codification-ready-STRENGTHENED for playbook v3 §15. ARCHITECTURE_INDEX v37 → v38. §8 timeline updated with S1603 close row.

**Prior v37 preamble (S1602 Cat B) preserved below:**

v37 — **Group 1600 Cat B child audit LANDED at S1602.** §1.40 `domains/content/1602_content_reviewers_decision_enforcement_audit.md` added (second child audit under Group 1600 per D66 P2 slot; 965 lines pre-fold; `status: active`, `category: child_audit`; playbook §11.2 20-section template + 6-parallel-Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 7 pre-Explore + 3 post-Explore load-bearing claims). Second sibling of Group 1600 to propagate parent D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront at §4.8 + §5.6 + §6.5 + §8.5 per D68 F8/F10 folds. **Load-bearing question resolutions (parent §3 Cat B):** Q1 dispatch shape — reviewers are PURE-FUNCTION MODULE-LEVEL (not class-based) via `content_review_panel_v2.py:88,107,124,208`; Q2 v1 vs v2 canonicalization — v2 canonical for deliberation pipeline (runner:225 imports v2); v1 `ContentReviewPanel` class at `content_review_panel.py:61` classified **PARTIALLY-ADOPTED-LIVE-SECONDARY** (grep-verified live consumer at `ContentWriterAgent:1376-1377` under `ENABLE_CONTENT_REVIEW=True` at :62; S1274 EventBus dormant-vs-partial lesson properly applied). **S1601 §15.1 UNK-2 fully resolved to CONFIRMED HIGH:** end-to-end citation integrity across Cat A + Cat B is LLM-prompt-only with zero code-side per-claim `[C-xxxxxxxxxx]` regex/typed-constraint at either gate. **NEW HIGH:** silent draft truncation at 8000 chars in v2 reviewers (`content_review_panel_v2.py:236` — extends S1601 F2 silent-partial-source pattern). **NEW HIGH latent-landmine:** `queue_agent_task` MISSING from `core/tasks.py` (grep-verified zero definitions); `DecisionEnforcerAgent.spawn_tasks_from_mandate` at `decision_enforcer_agent.py:456` imports missing task with broad `try/except Exception` guard at :455/:474-476 → exception-swallowed silent failure. Invalidates patent operational claim at `DISCLOSURE_F.md:140`. **NEW HIGH:** Cat B mandate + reviewer verdicts have ZERO PA-tool outbound channel (extends S1402 F.B1 ZERO outbound channel pattern to content Cat B — CONFIRMED). **Rigby SIGN cycle 1 SIGN-with-edits at High confidence** on fresh isolation pin `pa-1c5298d807d7a1d2` (retired at S1602 close via `session_tool.retire`; `updated_count: 4, retired: true`). **F1-F7 folds landed pre-commit:** F1 §5.5 ConversationOrchestrator critique reframed as Cat B decision-production substrate (not "just another review layer"); F2 §3.5 `_extract_decision` at runner :266-284 explicitly tagged Cat B-OWNED; F3 §1 tightened "all v2 deliberation deployment paths" scope (v1 direct-write via ContentWriterAgent goes through v1 ContentReviewPanel + does NOT touch v2 panel); F4 §4.2 + §13 MandateStatus lifecycle correction — `mark_killed` at :404-407 + `mark_completed` at :409-411 CODED but ZERO callers in deliberation flow (Rigby grep-verified); reframed as dormant state machine NOT missing machinery; F5 §1 finding #3 + §7.2 branch 8 + §15.3 spawn_tasks_from_mandate correction — DOES have broad try/except guard at :455/:474-476 → exception-swallowed silent failure, NOT unhandled crash; F6 §15.3 severity CRITICAL → HIGH latent-landmine + §19.6 T-slot rank #3/#4 reorder; F7 §15.10 `_detect_domain` 0.2 threshold MED → LOW (unvalidated tuning knob without misclassification evidence). **D48 preemptive stability-probe gate 11th-arm outcome:** Batches A/C + B/C substantive on fresh isolation pin; Batch C/C partial (worker-load deflection, not full jam per memory rule 2-substantive-turns threshold); final-verdict single-question turn returned clean in <10s. **Six-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602 CONFIRMED** — extends 10-arc pattern to 11-arc + S1602. Codification-ready-STRENGTHENED for playbook v3 §15. **§8 timeline row S1602 added.** Group 1600 arc In-progress with 2 child audits landed (S1601 Cat A + S1602 Cat B); four children + xx99 remain (S1603 Cat D → S1604 Cat C → S1605 Cat E → S1606 Cat F → S1699 xx99). v36 preamble follows: **Group 1600 Cat A child audit LANDED at S1601.** §1.39 `domains/content/1601_content_claims_pack_deliberation_pipeline_v2_audit.md` added (first child audit under Group 1600 Content / Deliverables / Publishing arc per D66 P1 slot; 1792 lines; `status: active`, `category: child_audit`; playbook §11.2 20-section template + 6-parallel-Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 6 load-bearing pre-Explore claims). Applies parent D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront pattern at §4.8 + §5.6 + §6.5 + §8.5 — **first sibling of Group 1600 to propagate the pattern upfront**. **Load-bearing question resolutions (parent §3 Cat A):** Q1 Citation integrity posture — Cat A enforces `claims_count == 0` gate only at `core/services/content_deliberation_runner.py:99-103`; NO per-claim `[C-xxxxxxxxxx]`-in-draft regex verifier code-side; Cat B FactCheckReviewer is LLM prompt-based (two-gate policy is LLM-verified, not code-enforced). Q2 v2 pipeline runtime posture — **strictly on-demand**; grep-verified ZERO beat entries fire `ContentDeliberationRunner.run_blog()`; triggers only via REST `POST /api/v1/research/self-blog/generate-v2/` + PA tool `blog_tool action=generate` (no topic) + Celery task `generate_self_blog_deliberation_task.delay()`. **Rigby SIGN cycle 1 SIGN-with-edits at Medium confidence** on fresh isolation pin `pa-9f075a024552b663` (F1-F6 folds landed pre-commit: F1 SelfBlog canonicalization-debt reframe not island posture proof; F2 silent-partial-source severity MEDIUM → HIGH; F3 RAG scope explicit cross-tenant/workspace framing; F4 RAG scope = riskiest overall Cat A finding elevation; F5 fix "ZERO writes to Cat B/C/D" Exec Summary contradiction (corrected: ZERO writes to Cat B/C; ONE write to Cat D via SelfBlog.objects.create as persistence handoff); F6 verification-report endpoint boundary caution pin). **D48 preemptive stability-probe gate 10th-arm outcome:** SIGN cycle 1 held clean in three turns; no worker instability observed; five-consecutive-fully-clean-arms sub-pattern **S1503+S1504+S1505+S1506+S1601** confirmed per D48 gate expectation at S1600 open. **§8 timeline row S1601 added.** Group 1600 arc now In-progress with 1 child audit landed (S1601 Cat A); five children + xx99 remain (S1602 Cat B → S1603 Cat D → S1604 Cat C → S1605 Cat E → S1606 Cat F → S1699 xx99). v35 preamble follows: **Group 1600 Content / Deliverables / Publishing arc OPENED at S1600.** §1.38 `domains/content/1600_content_domain_scoping.md` added (parent Phase 0 scoping per playbook §11.1 template; 1502 lines; `status: active`, `category: parent_scoping`; **THIRD application** of Chris's Phase 0 F.i/F.ii/F.iii methodology at §10/§11/§12 — applied UNCHANGED per D68 to preserve v3 promotion trigger integrity per S1400 D29 two-triggers rule + S1500 D58 second-application precedent + S1599 §12.4 discriminative-value criterion check 4-of-4 evidence types satisfied → playbook v3 §11.1 template promotion TRIGGERED at S1599 close; Group 1600 confirms whether pattern holds at third application via §12.4 F6-fold-tightened criterion). All 8 arc-open decisions Chris-locked in single "agree all + D-6=(a)" ratification round via governance decision `2c469638-643d-4477-a8ea-1766b552eebe` (`decision_create` + `decision_decide` action approve → status `acted`): **D63** domain slug=`content`; **D64** parent-with-children (P1-P6 children + P7 xx99 at S1699); **D65a** Deliverable canonicalization posture-decision framing (canonical container vs parallel-schema-siblings); **D65b** PublishGate canonicalization posture-decision framing (single canonical gate vs per-variant/channel); **D65c** Lifecycle transition ownership posture-decision framing (canonical orchestrator vs variant-owned rails); **D66** child mission sequence per F3 Rigby fold P3↔P4 swap — P1 Cat A ClaimsPack + Content Deliberation Pipeline v2 → P2 Cat B Content Reviewers + Decision Enforcement → **P3 Cat D Deliverable Base + Specialized Variants (moved from P4)** → **P4 Cat C PublishGate + Publish Rails (moved from P3)** → P5 Cat E Rigby-Facing Content PA Tooling + Approval UX → P6 Cat F Cross-Domain Integration Lens & Posture Decision Framing (LAST) → P7 S1699 xx99 canonical summary (**fourth application** of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second + S1599 third); **D67** §7 anti-scope 18 items (F5-fold expansion from 12 to 18 — added content indexing/discoverability + search/ranking + permissions/moderation + notification fanout + attribution/analytics expansion + template system/channel integrations beyond current rail); **D68** methodology UNCHANGED per D58 precedent + D62=(a) 6-sibling exemplar mini-schema propagation-upfront + F8/F10 folds adopted (one-sentence boundary rule per category + D66 dependency-clause embedding). **Rigby Light SIGN cycle 1 → cycle 2 SIGN-clean at High confidence** on fresh S1600 arc pin `pa-f52acf3f8d394faa` → **F1-F12 folds landed at commit-time** (F1 §3 Cat A ClaimsPack boundary rule; F2 §3 Cat C/D crisp boundary rules; F3 §5 P3↔P4 swap Cat D BEFORE Cat C; F4 §8 D65 split into D65a/D65b/D65c three orthogonal axes; F5 §7 anti-scope 12→18 items; F6 §12.4 discriminative-value tightening with required decision-discriminative proof + disconfirming evidence item; F7 §12.5 Deliverable Lifecycle Traceability Table 10→12 stages with normalization/canonicalization + eligibility/packaging-gate stages; F8 one-sentence boundary rule per category; F9 binary posture framing with mushy-hybrid disallowed; F10 D66 dependency-clause embedding; F11 §3 Cat E feedback-hazard note; F12 ClaimsPack centrality preserved via F1). Fresh S1600 arc pin `pa-f52acf3f8d394faa` minted via Rigby `session_tool.create_fresh` at S1600 open; `tools/pa_local.sh:128` updated from retired Group 1500 arc pin `pa-791b3db549a64e54` (retired at S1599 close per D53). **Load-bearing runtime evidence anchored via 2 parallel Explore sub-agent sweeps at S1600 open against `main` HEAD `82e8efe6`:** Content Pipeline surface confirmed 6+ services (ClaimsPackBuilder at `core/services/claims_pack_builder.py:51` + ContentWriterAgent at `core/agents/content_writer_agent.py:281` + 3-reviewer panel at `core/services/content_review_panel_v2.py:88,107,124` + DecisionEnforcerAgent at `core/agents/decision_enforcer_agent.py:60` + PublishGate at `core/services/publish_gate.py:27` with 4 hardcoded thresholds QUALITY_THRESHOLD 0.70/NOVELTY_THRESHOLD 0.60/STRUCTURE_THRESHOLD 0.55/MYTHOLOGY_THRESHOLD 0.15 + ContentDeliberationRunner at `core/services/content_deliberation_runner.py:21` + SportsContentContextBuilder at `core/services/sports_content_context.py:27`) + 6+ models (Deliverable base at `core/models_deliverables.py:84` + 5 parallel deliverable-shaped variants: SelfBlog at `core/models_unified_system.py:20611` + OutreachDraft at `core/models_outreach.py:18` + ClosePack at `core/models_close_pack.py:20` + SportsBettingBrief at `core/models_unified_system.py:18394` + BlockchainAuditBrief at `core/models_unified_system.py:18435`) + supporting models (DeliverableAppend at `core/models_deliverable_appends.py:35` + DeliverableExport at `core/models_deliverables.py:474` + DeliverableEvent at :561 + ContentPacket at :617) + 4 Rigby PA-tool surfaces (deliverable_tool schema at `core/services/pa_tool_schemas.py:3389-3460` + handler at `core/services/td_handlers_content.py:84` with 18 supported actions + content_tool at :235 + blog_tool at :162 + newsletter_tool schema at `pa_tool_schemas.py:3498-3550`) + 6+ Celery beat entries (`generate-operator-edge-newsletter` @ Fri 06:00 Denver `content` queue with dry_run=True default per S1228 P3 + `generate-outreach-drafts-daily` @ 07:30 Denver `content` queue + `cleanup-stale-content` @ 10:05 daily default queue + `cleanup-boardroom-junk` @ 04:30 daily + `cleanup-junk-initiatives` @ 04:05 daily + `initiative-activity-tick` every 30 min) + Discord broadcast surface at `core/services/discord_notifications.py:36-47` with 12 channel constants including CHANNEL_BOARDROOM 1448819855557136595 + CHANNEL_MARKET_ALERTS + CHANNEL_STOCK_ALERTS + CHANNEL_BLOCKCHAIN_ALERTS + CHANNEL_PODCAST_LIBRARY + Frontend surface (BlogViewerPage.tsx:45 + ContentPage.tsx + blogsApi at `frontend/src/lib/api.ts:3921-3962` + deliverablesApi at :4095-4109 + newsletter frontend). **Cross-arc handoffs owed to Group 1600:** S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN CRITICAL + S1504 §5.1 SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS HIGH + S1402 F.B1 Revenue OutreachDraft delivery ZERO outbound channel HIGH + S1403 F.C4 ContentEngagement docstring drift HIGH + S1502 §14.3 SignalCluster.pattern_type consumer-side gap (6-arc COMPLETED per S1599 §4.11) + S1499 D55 (ii) Revenue Employee + Income/Jobs Employee JobContract split precedent (Content Employee analog owed as Cat F evidence-plan input if surfaces). **Locked child mission sequence (D66 F3-fold-swap):** P1 S1601 Category A ClaimsPack + Content Deliberation Pipeline v2 → P2 S1602 Category B Content Reviewers + Decision Enforcement → P3 S1603 Category D Deliverable Base + Specialized Variants (F3 fold: moved from P4→P3 because Cat C's gate/rails semantics consume Cat D's canonical object-model decision D65a-analog) → P4 S1604 Category C PublishGate + Publish Rails (F3 fold: moved from P3→P4 because gate semantics D65b-analog + lifecycle transition ownership D65c-analog are grounded in Cat D's canonical object-model outcome) → P5 S1605 Category E Rigby-Facing Content PA Tooling + Approval UX → P6 S1606 Category F Cross-Domain Integration Lens & Posture Decision Framing (LAST — consumes P1-P5 evidence + produces xx99 §5 D65a/D65b/D65c-analog three-axis posture-decision evidence plan per parent §12.1 F.iii item 3) → P7 S1699 xx99 canonical summary (**fourth application** of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second + S1599 third). §8 timeline S1600 row added. OPEN_ARCS Group 1600 row moves Not-started → In-progress this commit. Playbook v3 §11.1 template promotion status: **TRIGGERED at S1599 close** per §12.4 discriminative-value criterion check (4 of 4 evidence types satisfied); Group 1600 is third application under D58/D68 methodology-unchanged pattern; xx99 §12.4 F6-fold-tightened criterion at S1699 close confirms whether third application produced discriminative value at arc-close bar OR whether pattern requires refinement. Prior — v34 (2026-07-02, S1599 close): **Group 1500 Sports/DBAO/Intelligence arc CLOSED at S1599 xx99 canonical summary.** §1.37 `domains/sports/1599_sports_canonical_summary.md` added (arc-close canonical summary per playbook §11.3 12-section template + §10 "What This Research Taught Us About How to Do Research" **third application** after S1399 first + S1499 second; 2241 lines; pending Rigby Full SIGN cycle 1 via fresh isolation pin — **D48 preemptive stability-probe gate 10th arm** anticipated; five-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1599 anticipated). **Sports arc-close pattern classes:** 13 pattern classes registered — 5 NEW at S1506 (P1 NAMING-CONVENTION-WITHOUT-MATERIALIZATION + P2 DECOUPLED-VERIFICATION-SYSTEMS + P3 DECLARED-FEATURE-FLAG-GATES-NOTHING + P4 DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT (3-child) + P5 SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION) + 5 NEW at other categories (P6 MOCK-DATA-CONSUMER S1505+S1506 + P7 DEAD-RENDER-PATH S1505 + P8 WRITE-ONLY-FORGOTTEN S1504+S1505 + P9 ZERO-FIRE-BEAT S1503+S1504 + P10 HOT-PATH-CHOKE-BYPASS S1504+S1506) + 3 INHERITED (P11 Sports↔Signal Engine 6-arc consumer-side gap COMPLETED + P12 Sports↔Memory PARTIAL bridge 5-arc + P13 Fixture/entity identity 2-arc). **§5 D59 posture-decision evidence brief** delivered with **explicit "Chris-gated selection" tag** — 7 integration criteria A1-A7 + 7 island criteria B1-B7 + 4 cross-cutting C1-C4 + failure-mode table D + cost asymmetry summary E + F2-fold scoring rubric F applied uniformly across P1-P6 evidence corpus → **all 22 criteria score FAIL at HEAD `5a8d3d75`** exposing load-bearing observation "BOTH postures require substantive investment; neither is a default." **§3.4 Four-axis compound-maturity shape** NEW arc-level maturity framing produced by Cat F. **§3.2 Sports Domain Lifecycle Traceability Table** per parent §12.5 F.iii deliverable — 8 lifecycle stages (odds ingestion + fixture/entity identity resolution + normalization + prediction + user wager + outcome verification + learning-loop feedback + signal aggregation gap); 1 of 8 MISSING (Stage 8 Signal Aggregation — 6-arc COMPLETED gap); 1 of 8 UNKNOWN+MISSING resolver (Stage 2 fixture/entity identity). **§10 meta-methodology third application** with **§12.4 discriminative-value criterion check** — **4 of 4 evidence types satisfied** (Scope confusion prevented via D60 Intelligence bound-out + Rework reduced via §11.4 F.ii boundary + Cleaner arc close via 6-of-6 SIGN-with-edits + Chris-lock efficiency via single agree-all round D56-D61); **playbook v3 §11.1 template promotion TRIGGERS**. **Playbook v3 candidate list (6):** D48 preemptive stability-probe gate 9-arc CODIFICATION-READY → v3 §15; D62=(a) 6-sibling exemplar pattern → v3 §5; F2-fold scoring rubric → v3 §11.3 §5; BEFORE-SIGN Rigby ORM probe → conditional v3 §14; S1504 verdict-text re-request recovery → v3 §15 preventive framing; S1505 Rigby Q8 grep-verified confidence-upgrade → v3 §15 SIGN-time verifier-loop tool. **§8 Follow-on queue T1-T10:** T1 Chris-gated ADRs (R.SPORTS.POSTURE + R.DBAO.CODENAME) + CRITICAL remediation sequences (R.C1←R.C2 verify-beat gate + R.D1←R.D2 digest-beat gate + R.D3 zero-test-coverage reliability multiplier + R.D4 SportsBettingBrief consumer-or-remove ← T1.a + R.D5 two-writer dedup); T2 12 tracks (SignalCluster bridge + verification reconciliation + Discord refactor + MOCK-DATA-CONSUMER cleanup + fixture identity + DEAD-RENDER-PATH cleanup + operational cadence + Bankroll reconciliation + auth-drift + test coverage + topic doc + BettingPage split); T3 6 tracks; T4 11 cleanup PRs; T5 6 optional. **§7 Anchor-update recommendations landing:** §3.10 Sports subdivision + DBAO subgroup addition/suppression conditional on T1.b + NEW `docs/topics/sports-betting.md` (C2 cross-cutting gate) + `PLATFORM_WHAT_IT_IS.md` Sports narrative refresh + `.github/CODEOWNERS` 6 sports runtime files (post-arc T3). **Arc pin `pa-791b3db549a64e54` retires at arc-close** per playbook §16 D53 arc-close discipline (matches S1499 pattern). **OPEN_ARCS Group 1500 In-progress → Closed at S1599 close.** Playbook §22 domain queue post-Group-1500-close: Group 1300 closed S1399 + Group 1400 closed S1499 + Group 1500 closed S1599 + next-arc default lean Group 1600 Content / Deliverables / Publishing. §8 timeline S1599 arc-close row added. Prior — v33 (2026-07-02, S1506 close): **Sixth and LAST Group 1500 child audit landed at S1506 — Category F Cross-Domain Integration Lens & Posture Decision Framing.** §1.36 `domains/sports/1506_sports_cross_domain_integration_lens_and_posture_decision_framing_audit.md` added (child audit per playbook §11.2 20-section template; 1345 lines pre-fold; `status: draft`, `category: child_audit`, `subdomain_category: F`; **LOAD-BEARING for D59 posture-decision evidence plan owed to xx99 canonical summary**; six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 6 load-bearing claims — all 6 verified CORRECT against source before draft integration; **sixth and final sibling** to apply D62 = (a) pre-brief mini-schema propagation upfront). **D62 = (a) propagate upfront 6-sibling exemplar pattern COMPLETED** — 4-item pre-brief mini-schema applied per surface (§4.4) extending D62 validation across S1501+S1502+S1503+S1504+S1505+S1506 6-arc pattern. Rigby Full SIGN cycle 1 SIGN-with-edits at High confidence via fresh isolation pin `pa-c2cdbd5c0b8c451b` (**D48 9th arm — four-consecutive-fully-clean arms S1503+S1504+S1505+S1506 sub-pattern** with zero worker-instability across 3 SIGN turns; retired at S1506 close via `session_tool.retire`). **F1-F2 folds landed at commit-time:** F1 §14.5 anchor-set tightening (`/odds` + `/futures` + `/slip` explicit bypass; `/arb` shared-agent exclusion made explicit at section body per Rigby Q5 Batch 1 edit); F2 §20.6 §F scoring rubric + threshold minima for xx99 consumption-readiness per Rigby Q15 Batch 3 edit (PASS/PARTIAL/FAIL rubric + minimum acceptable threshold per criterion A1-A7 + B1-B7 + C1-C4). **Cycle 2 SIGN-clean at High confidence anticipated post-fold-land** — pattern-consistent with S1501-S1505 cycle-1-predict-cycle-2 5-of-5 arc precedent. **D48 preemptive stability-probe gate 9th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506 9-arc pattern — further strengthens immediate codification recommendation from S1505 8-arc threshold with four-consecutive-fully-clean-arms sub-pattern. **Load-bearing findings owed to xx99 (S1599) posture-decision brief via §20.6 evidence plan (14):** (1) **CRITICAL architectural — DBAO is NAMING-CONVENTION-WITHOUT-MATERIALIZATION.** Six declared artifacts (schema/2 WS routes/env-vars/header) + zero runtime state + 2 unimplemented handler stubs. NEW pattern class for the arc. (2) **CRITICAL architectural — DECOUPLED-VERIFICATION-SYSTEMS at BettingOutcomeVerifier ↔ MLPrediction.** Two verification systems fully independent; zero cross-reference. NEW pattern class. (3) **HIGH architectural — Sports ↔ Signal Engine 6-arc consumer-side pattern completed** (extends 5-arc S1502-S1505 to 6-arc; PATTERN_TYPE_CHOICES + emitter + zero bridging code + zero sports-native aggregator). (4) **HIGH architectural — DECLARED-FEATURE-FLAG-GATES-NOTHING at `sports_intelligence`** (hardcoded True at 2 sites, consulted nowhere). NEW pattern class. (5) **HIGH architectural — Discord HOT-PATH-CHOKE bypass** at `/odds` + `/futures` + `/slip` extends S1504 REST-side pattern to Discord side. (6) **HIGH architectural — Sports ↔ Memory PARTIAL bridge** (2/4 market agent coverage; 0 AgentKnowledgeSource writes). (7) HIGH operational — `/ws/dbao-dashboard/` sibling route surfaced; S1505 §14.1 MOCK-DATA-CONSUMER footprint expands 1 route → 2 routes. (8) HIGH operational — DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT at `_impl_collect_sports_odds_intelligence`. NEW pattern class. (9) MED-HIGH — SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION at `RealtimeIntelligenceEngine` cross-domain loops (hardcoded demo). NEW pattern class. (10) MED-HIGH — LATENT-ZERO-FIRE at `RealtimeIntelligenceEngine` (no beat, no @shared_task, manual `start_skynet()` only) — deepens S1503 ZERO-FIRE-BEAT. (11) MED — `IntelligencePage` frontend does not consume sports despite flag claim. (12) MED architectural — DUAL-COORDINATOR-BYPASS at `_impl_collect_sports_odds_intelligence` (bypasses SportsBettingCoordinator AND RealtimeIntelligenceEngine). (13) MED — CODEOWNERS compound gap across 6 sports runtime files. (14) MED — `docs/topics/sports-betting.md` gap remains after 6 audits. **Cat F maturity verdict** per §13: **PARTIAL (mixed; multi-axis; four-axis compound shape)** — sixth distinguishing maturity shape in the arc (NAMING-CONVENTION-WITHOUT-MATERIALIZATION axis 1 + WORKING-when-started-LATENT-ZERO-FIRE-by-default + DECLARED-GATES-NOTHING + DOMAIN-NEUTRAL-REST-SPORTS-TANGENTIAL-UI axis 2 + FIRST-CLASS-WRITE-CONSUMER-BYPASSING-COORDINATOR axis 3 + ARMED-BUT-DECOUPLED axis 4). **§20.6 POSTURE-DECISION EVIDENCE PLAN** is the load-bearing D59 deliverable owed to xx99 — evidence-plan framing NOT posture selection; explicit Chris-gated selection tag; 7 integration criteria (A1-A7) + 7 island criteria (B1-B7) + 4 cross-cutting (C1-C4) + failure-mode table (D) + cost asymmetry summary (E) + F2-fold scoring rubric with thresholds (F). Group 1500 arc pin `pa-791b3db549a64e54` RETAINED per playbook §16 (carries P7 xx99); fresh SIGN pin `pa-c2cdbd5c0b8c451b` retired at S1506 close via `session_tool.retire`. §8 timeline S1506 row added. OPEN_ARCS Group 1500 current-child field advances "S1505 SIGN-with-edits cycle 1 (F1-F5 folds landed, cycle 2 anticipated, commit-gated) + S1506 queued next" → "S1506 SIGN-with-edits cycle 1 (F1-F2 folds landed, cycle 2 anticipated) + S1599 xx99 queued next"; row remains In-progress. Playbook §22 domain queue: Group 1300 closed S1399 + Group 1400 closed S1499 + Group 1500 In-progress (all 6 children S1501-S1506 landed, xx99 S1599 remaining). Prior — v32 (2026-07-02, S1505 close): **Fifth Group 1500 child audit landed at S1505 — Category E Sports Frontend Surface.** §1.35 `domains/sports/1505_sports_frontend_surface_audit.md` added (child audit per playbook §11.2 20-section template; 1009 lines after F1-F5 folds; `status: draft`, `category: child_audit`, `subdomain_category: E`; six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 5 load-bearing claims — all 5 verified CORRECT by Rigby Q8 grep pass). **D62 = (a) propagate upfront applied as fifth sibling** — 4-item pre-brief mini-schema applied per surface (§4.2) extending D62 validation across S1501+S1502+S1503+S1504+S1505 5-arc pattern. Rigby Full SIGN cycle 1 SIGN-with-edits at High confidence via fresh isolation pin `pa-546de7ebe8c8b885` (**D48 8th arm — three-consecutive-fully-clean arms S1503+S1504+S1505 pattern** with zero worker-instability across 4 SIGN turns; retired at S1505 close via `session_tool.retire` with `updated_count: 5`). **F1-F5 folds landed at commit-time:** F1 §14.3 auth-drift wording tightening ("no 401 surfacing / no per-call auth gate" frontend side + "permission-floor inconsistency" backend side — two-sided drift class explicit); F2 §15.5 elevated MED → HIGH structural debt "no API contract source-of-truth" as the parent cause behind §14.3 AUTH-DRIFT + §15.4 inline interfaces + §14.9 tab-count doc drift; F3 §14.3 "Verified-in-repo anchors" subsection explicitly enumerating 4 grep-verified anchor points from Rigby Q8; F4 §14.3 named `bettingApi.liveOpportunities()` and `bettingApi.intelligence()` as feeding Top Plays / Sharp Action / Arbitrage tab families; F5 §14.1 MOCK-DATA-CONSUMER intent-neutrality framing acknowledging "may be intentional demo/placeholder" without weakening CRITICAL classification — reframed as "operational-confusion / integration-signaling hazard." **Cycle 2 SIGN-clean at High confidence anticipated post-fold-land** — pattern-consistent with S1501+S1502+S1503+S1504 cycle-1-predict-cycle-2 accuracy. **D48 preemptive stability-probe gate 8th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505 8-arc pattern — further strengthens immediate codification recommendation from S1504 7-arc threshold with three-consecutive-clean-arms pattern (S1503+S1504+S1505). **Load-bearing findings owed to xx99 (S1599) posture-decision brief via Cat F evidence plan (11):** (1) **CRITICAL architectural — `/ws/dbao/` broadcasts random mock data, not sports-derived state.** `core/new_pages_consumer.py:310-331` populates payload via `random.randint()` + `random.uniform()` for every metric field. **NEW pattern class for the arc: MOCK-DATA-CONSUMER** (distinct from S1504 WRITE-ONLY-FORGOTTEN + S1503 ZERO-FIRE-BEAT + S1502 PROVENANCE-STAMP-ABSENT); no real data touched at any point. F5 intent-neutrality nuance: may be intentional demo but operational-confusion hazard stands. (2) **HIGH architectural — `markets` + `bankroll` DEAD-RENDER-PATH tabs.** `BettingTab` TypeScript union at `BettingPage.tsx:14` declares 11 tab identifiers; `tabs` array at lines 16-26 renders only 9 nav buttons; the remaining 2 have wired query hooks (lines 968 + 975) and wired render conditionals (lines 2080 + 2298) but no nav button to activate. **NEW pattern class: DEAD-RENDER-PATH** (fully coded feature branches with no user-facing entry point). Fifth distinguishing pattern shape after S1501–S1504. (3) **HIGH operational — 2 permission-floor inconsistencies** between frontend read-path expectations and backend IsAuthenticated decorators: `bettingApi.liveOpportunities()` → `live_betting_opportunities` at `views_odds_sports.py:580 @permission_classes([IsAuthenticated])` (urls.py:3085) + `bettingApi.intelligence()` → `get_betting_intelligence` at `views_odds_sports.py:2056 @permission_classes([IsAuthenticated])` (urls.py:3099); silent 401 on Top Plays / Sharp Action / Arbitrage tab families. F1 fold two-sided framing. F4 fold tab-consumer identification. (4) **HIGH architectural — S1504 §14.3 SportsBettingBrief write-only-and-forgotten CONFIRMED at frontend AND REST endpoint.** `get_betting_brief` at `views_odds_sports.py:3237-3265` calls coordinator on-the-fly; never queries persisted model. (5) **HIGH architectural — Zero WebSocket subscription from BettingPage despite defined sports WS routes.** `sports/routing.py:7-11` registers 3 consumers but BettingPage never connects; all 9 tabs polling only. (6) MED-HIGH POSTURE-DECISION-PENDING — Zero Cat E → Signal Engine emission (extends 4-arc pattern to 5-arc). (7) MED architectural — BettingPage sole frontend sports consumer (zero cross-domain leak — positive isolation signal for Cat F). (8) MED operational — BettingPage.tsx = 3,023 lines god-component (14 useQuery + 17 useState + 5 inline sub-components + 11 inline TS interfaces). (9) HIGH per S1504 §15.12 F4 precedent — Zero dedicated test coverage. (10) MED architectural — Zero client-side state persistence. (11) MED — No CODEOWNERS row for BettingPage.tsx. **Cat E maturity verdict** per §13: **PARTIAL (mixed — WORKING at read-side tabs; DEAD-RENDER-PATH at markets/bankroll; MOCK-DATA-CONSUMER at /ws/dbao/; AUTH-DRIFT at 2 endpoints; NO-REALTIME across all tabs)** — fifth distinguishing maturity shape in the arc. Group 1500 arc pin `pa-791b3db549a64e54` RETAINED per playbook §16 (carries P6 sequence + P7 xx99); fresh SIGN pin `pa-546de7ebe8c8b885` retired at S1505 close via `session_tool.retire` (updated_count=5). §8 timeline S1505 row added. OPEN_ARCS Group 1500 current-child field advances "S1504 SIGN-with-edits cycle 1 (F1-F11 folds landed, cycle 2 anticipated) + S1505 queued next" → "S1505 SIGN-with-edits cycle 1 (F1-F5 folds landed, cycle 2 anticipated) + S1506 queued next"; row remains In-progress. Playbook §22 domain queue: Group 1300 closed S1399 + Group 1400 closed S1499 + Group 1500 In-progress (S1501 + S1502 + S1503 + S1504 + S1505 landed, P6 + xx99 remaining). Prior — v31 (2026-07-02, S1504 close): **Fourth Group 1500 child audit landed at S1504 — Category D Sports Betting Content Pipeline.** §1.34 `domains/sports/1504_sports_betting_content_pipeline_audit.md` added (child audit per playbook §11.2 20-section template; 1078 lines after F1-F11 folds; `status: active`, `category: child_audit`, `subdomain_category: D`; six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 5 load-bearing claims — 4 sub-agent errors/conflicts caught pre-SIGN — plus parent-Claude Rigby ORM probe BEFORE draft integration; **second library application** of S1503-first-applied BEFORE-SIGN pattern). **D62 = (a) propagate upfront applied as fourth sibling** — 4-item pre-brief mini-schema applied per surface (§4.4 / §5.6 / §6.6 / §8.6 / §15.16) extending D62 validation across S1501+S1502+S1503+S1504 4-arc pattern. Rigby Full SIGN cycle 1 SIGN-with-edits at Medium-High confidence via fresh isolation pin `pa-af2bf7f2d1a0ef61` (**D48 7th arm — matches S1503 6th-arm cleanest arm pattern** with zero worker-instability across 4 SIGN turns) → F1-F11 folds landed at commit-time: F1 §1 Finding 6 + §7.2 `run_all_desks_intelligence` cross-domain writer bridge elevation; F2 §5.1 + §7.6 + §13.2 SportsContentContextBuilder HOT-PATH-CHOKE-POINT reframe (from TRANSITIVELY-COUPLED); F3 §4.2 LegacySpiderData shared-table Cat B/C bridge surface risk elevation; F4 §1 Finding 9 zero test coverage MED-HIGH → HIGH + §15.12 → CRITICAL + §19.1 #3; F5 §15.5 digest idempotency PRE-RESTORE-BEAT gate MED-HIGH → CRITICAL + §19.1 #2; F6 §14.2 + §15.3 docstring cadence drift HIGH → MED; F7 §1 exec-summary risk ordering strengthened; F8 §19.1 CRITICAL tier reordered to 5-item dependency ordering (1 digest beat + 2 idempotency + 3 test coverage + 4 consumer-or-remove + 5 dedup); F9 §13 + §1 maturity verdict tightened to distinguish WORKING (fire-verified) from PRESENT + SCHEDULED (runtime not verified beyond Celery SUCCESS counts) + §19.2 #8 runtime instrumentation task; F10 §1 exec-summary opening rewritten from "owed to xx99" placeholder to concrete handoff target; F11 §14.4 + §14.5 + §19.2 #6 + §19.4 #14-15 "no owning bridge implementation was located" clarifier. **Cycle 2 SIGN-clean at High confidence anticipated post-fold-land** matches S1501+S1502+S1503 cycle-1-predict-cycle-2 pattern. **D48 preemptive stability-probe gate 7th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502+S1503+S1504 7-arc pattern — further strengthens immediate codification recommendation from S1503 6-arc threshold. **Load-bearing findings owed to xx99 (S1599) posture-decision brief via Cat F evidence plan:** (1) CRITICAL operational — `daily_betting_digest` unscheduled + zero-fire + docstring-claim-lie (S1503 §14.1 pattern replicated). (2) CRITICAL architectural — `SportsBettingBrief` write-only-and-forgotten (2 writers + 0 readers + REST bypass; NEW pattern for the arc). (3) HIGH POSTURE-DECISION-PENDING — Zero Cat D → Cat B outcome-feedback loop per S1502 F3 / S1503 F9 precedent + F11 clarifier "no owning bridge implementation was located." (4) HIGH POSTURE-DECISION-PENDING — Zero Cat D → Signal Engine emission + F11 clarifier. (5) MED — `generate_daily_betting_brief` docstring cadence drift (F6 fold demote). (6) MED-HIGH — Two SportsBettingBrief writer paths without dedup (F1 fold cross-domain writer bridge elevation). (7) MED — Discord fast path BYPASSES `SportsContentContextBuilder` (F2 fold two-disconnected-content-generation-surfaces). (8) MED POSTURE-DECISION-PENDING — Zero Cat D → Memory Domain bridge + F11 clarifier. (9) HIGH → CRITICAL — Zero dedicated test coverage (F4 fold reliability multiplier). (10) MED — No PA tool for triggering brief / digest / regeneration. **Cat D maturity verdict** per §13 F9 fold: **PARTIAL (mixed — WORKING (beat + 30d fire evidence) at brief-generation; PRESENT + SCHEDULED (runtime not verified beyond Celery SUCCESS counts) at intelligence-hook + `/odds`; BROKEN/DORMANT at digest; WRITE-ONLY-FORGOTTEN at brief-persistence; HOT-PATH-CHOKE-POINT for content/PA — BYPASSED by Cat D Discord fast path)** — fourth distinguishing maturity shape in the arc. Group 1500 arc pin `pa-791b3db549a64e54` RETAINED per playbook §16 (carries P5-P6 sequence + P7 xx99); fresh SIGN pin `pa-af2bf7f2d1a0ef61` retired at S1504 close via Rigby `session_tool.retire`. §8 timeline S1504 row added. OPEN_ARCS Group 1500 current-child field advances "S1503 SIGN-with-edits cycle 1 (folds landed, cycle 2 anticipated) + S1504 queued next" → "S1504 SIGN-with-edits cycle 1 (F1-F11 folds landed, cycle 2 anticipated) + S1505 queued next"; row remains In-progress. Playbook §22 domain queue: Group 1300 closed S1399 + Group 1400 closed S1499 + Group 1500 In-progress (S1501 + S1502 + S1503 + S1504 landed, P5-P6 + xx99 remaining). Prior — v30 (2026-07-02, S1503 close): **Third Group 1500 child audit landed at S1503 — Category C Sports Wager Tracking & Outcome Verification.** §1.33 `domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md` added (child audit per playbook §11.2 20-section template; 1177 lines after F1-F14 folds; `status: active`, `category: child_audit`, `subdomain_category: C`; six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 7 load-bearing claims — 2 Sub-agent 6 errors caught pre-SIGN — plus parent-Claude Rigby ORM probe BEFORE draft integration; first library child audit to apply Rigby ORM probe as parent-Claude verifier-loop tool before SIGN routing). **D62 = (a) propagate upfront applied as third sibling** — 4-item pre-brief mini-schema applied per surface (§4.4 / §5.6 / §6.6 / §8.6 / §15.16) completing D62 validation across S1501+S1502+S1503 3-arc pattern. Rigby Full SIGN cycle 1 SIGN-with-edits at High confidence via fresh isolation pin `pa-8ce5f949bed5e093` (D48 6th arm — clean warm-up probe via `cockpit_tool.worker_health` + zero worker-instability across 4 substantive SIGN batches this session — cleanest arm of the 6-arc pattern) → F1-F14 folds landed at commit-time (F1 §5.4 additional Cat C read surfaces addendum `views_odds_sports.py` + `td_handlers_content.py` read path + `sports_content_context.py`; F2 §5.5 Bankroll adjacency touchpoints bounded subsection; F3 §1 executive summary compounding-risk observation Finding 1 + Finding 5 combo + orchestration+idempotency-as-readiness-gate reframe; F4 §14.1 + §20.5 independent Rigby SIGN cycle 1 batch 3 Q8 ORM probe block; F5 §14.5 + §15.10 severity MED-HIGH → MED downgrade "until divergence proven"; F6 §15.13 new debt item timezone correctness on `commence_time`; F7 §15.14 new debt item idempotency + replay safety as PRE-RESTORE-BEAT GATE HIGH-severity; F8 §15.15 new debt item Decimal quantization policy; F9 §14.2 + §14.3 "bridge owns learning writes" default posture statement; F10 §19.1 CRITICAL tier reorganization — beat-schedule remediation + concurrency-safety hardening moved from HIGH/MED to CRITICAL as PRE-RESTORE-BEAT GATE; F11 §19.2 #5 new research item operational cadence study Odds API rate limits + score availability lag; F12 fixture identity strategy already at §19.4 no move; F13 §19.3 #9 new research item operator tooling PA tool + management command; F14 §5.5 dual-Bankroll footnote clarifying `Bankroll` in `core/models_bankroll.py:19` PLUS `BankrollManagement` in `sports/models.py:1032`) → Cycle 2 SIGN-clean at High confidence anticipated post-fold-land (matches S1501 + S1502 cycle-1-predict-cycle-2 pattern). **D48 preemptive stability-probe gate 6th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502+S1503 6-arc pattern — further strengthens immediate codification recommendation from S1502 5-arc threshold; recommended for immediate codification alongside D45 titles-only recovery + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent + parent-Claude Rigby ORM probe BEFORE-SIGN pattern per S1499 §10 meta-methodology. **Load-bearing findings owed to xx99 posture-decision brief via Cat F evidence plan:** (1) CRITICAL operational — `verify_betting_outcomes` unscheduled AND zero-fire — grep of `core/celery.py` returns zero + grep of `docs/AUDIT_FINDINGS.md` §12 canonical deferred list returns zero + BOTH independent Rigby ORM probes returned 0/0 for both task variants; docstring at `core/tasks.py:6129` claims "Runs every 2 hours" — phantom behavior. (2) HIGH architectural POSTURE-DECISION-PENDING per S1502 F3 precedent — Zero Cat C → Cat B outcome-feedback loop; answers S1502 §1 Finding 6 explicitly; F9 fold "bridge owns learning writes" as default posture. (3) HIGH architectural POSTURE-DECISION-PENDING per S1502 F2 precedent — Zero Cat C → Signal Engine emission; extends S1274 §14 Finding #6 into Cat C consumer side. (4) MED-HIGH operational — Two task definitions for same feature (core.tasks + sports.tasks) with different behavior wrappers. (5) MED (F5 fold downgrade) — Discord `/bankroll` reads `Bankroll` model (not `BettingStats`) — dual aggregation surface. (6) MED-HIGH POSTURE-DECISION-PENDING per S1502 F4 precedent — Zero Cat C → Memory Domain (S1300) bridge beyond `AgentMemory` + `UserAgentLearning`. (7) MED architectural — `PlacedWagerLeg.event_id` string coupling to Odds API dict return shape (replicates S1502 §1 Finding 3 pattern on Cat C side). (8) MED POSTURE-DECISION-PENDING — Cat C is a leaf domain (zero inbound FKs); structural signature of "sports as island". (9) MED-HIGH operational — Zero test coverage for Cat C surface. (10) MED operational — No concurrency control on `_settle_wager()`. **Cat C maturity verdict** per §13: **PARTIAL (armed but zero-fire)** — third distinguishing shape after S1501 + S1502; features are code-complete + surface-complete but scheduling-broken. Group 1500 arc pin `pa-791b3db549a64e54` RETAINED per playbook §16 (carries P4-P6 sequence + P7 xx99); fresh SIGN pin `pa-8ce5f949bed5e093` retired at S1503 close via Rigby `session_tool.retire`. §8 timeline S1503 row added. OPEN_ARCS Group 1500 current-child field advances "S1502 SIGN-clean cycle 2 (commit-gated) + S1503 queued next" → "S1503 SIGN-with-edits cycle 1 (folds landed, cycle 2 anticipated) + S1504 queued next"; row remains In-progress. Playbook §22 domain queue: Group 1300 closed S1399 + Group 1400 closed S1499 + Group 1500 In-progress (S1501 + S1502 + S1503 landed, P4-P6 + xx99 remaining). Prior — v29 (2026-07-02, S1502 close): **Second Group 1500 child audit landed at S1502 — Category B Sports Prediction & Analytics Agents.** §1.32 `domains/sports/1502_sports_prediction_analytics_agents_audit.md` added (child audit per playbook §11.2 20-section template; 1981 lines after F1-F12 folds; `status: active`, `category: child_audit`, `subdomain_category: B`; six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 7 load-bearing claims — all 7 survived independent verification pre-SIGN; 0 sub-agent errors caught this pass, unlike S1501 which caught 3). **D62 = (a) propagate upfront applied as second sibling per Chris ratification S1501 open 2026-07-01** — 4-item pre-brief mini-schema applied per surface (§4.8 / §5.4 / §6.6 / §8.6 / §15.2). Rigby Full SIGN cycle 1 SIGN-with-edits at Medium confidence via fresh isolation pin `pa-64c019d7e6685d31` (D48 5th arm — clean stability probe via `cockpit_tool.worker_health` + zero worker-instability across 3 substantive SIGN batches this session) → F1-F12 folds landed at commit-time (F1 §7.1 explicit call-chain block `beat → task → coordinator → agents → aggregate → SportsBettingBrief.objects.create()` + §19 rank re-order PA registry promoted rank 5→4; F2 §1 Finding 5 SignalCluster reframed to POSTURE-DECISION-PENDING per S1274 §12.3 precedent + op-risk LOW / arch-risk HIGH; F3 §1 Finding 6 outcome-feedback-loop reframed to POSTURE-DECISION-PENDING "closed-loop learning deferred"; F4 §1 Finding 7 Memory Domain bridge reframed to POSTURE-DECISION-PENDING "context-agnostic by construction"; F5 §1 Finding 4 ArbitrageOpportunity dormant triple KEPT AS DRIFT per Rigby recommendation — "model + admin + serializer + viewset reads like we meant to persist"; F6 §15 debt matrix row #12 added: cross-book fixture-identity reconciliation MED-HIGH architectural / LOW operational; F7 §1 preamble added: operational-vs-architectural risk axis distinction + per-finding risk labels; F8 §1 Finding 9 continue-on-error reframed to INTENTIONAL-OR-DRIFT NEEDING CONTRACT STATEMENT per S1501 F6 "unimplemented expectation" precedent; F9 §1 Finding 1 + §13.2 Session-1205 DEAD-classification-residue language softened per Rigby cycle 1 concern; F10 §4.6 SportsBettingBrief model verified via grep — model at `core/models_unified_system.py:18394` + 2 write sites at `core/tasks.py:12187` + `core/tasks_content.py:3150`; F11 §20.2 REST endpoint router registration verified via grep of `core/urls.py:3083-3128` — 6 `path()` registrations + 6 view imports; F12 §5.1 direct-consume filter cite tightened with verbatim shape `filtered_events = [e for e in events if e.get('data_type') == 'sports_odds']` + note that TheOddsSpider assigns `data_type` key during `fetch_data()` normalization) → Rigby Full SIGN cycle 2 SIGN-clean at High confidence (cycle 1 prediction accurate). **D48 preemptive stability-probe gate 5th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502 5-arc pattern — clean stability probe + zero worker-instability observed across 4 substantive SIGN batches (cycle 1 batches 1-3 + cycle 2 verdict) this session; recommended for immediate codification alongside D45 titles-only recovery + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent per S1499 §10 meta-methodology. **Load-bearing findings owed to xx99 posture-decision brief via Cat F evidence plan:** (1) Coordinator `.run()` vs `.execute()` asymmetry — HIGH operational risk; 4 of 5 orchestrator agents bypass Layer 1 `AgentExecution` telemetry; only SportsOddsAnalyst uses `.run()` at `sports_betting_coordinator.py:122` with Session 1206 inline provenance comment; docstring at lines 22-33 describes symmetric 5-agent pipeline — mismatch creates "false green" monitoring. (2) PA tool registry gap — MED-HIGH operational risk; `sports_odds_analyst` + `arbitrage_detector` absent from `tool_dispatcher.py:302-305` (only 4 sports tools registered); both agents in AGENT_MAP but Rigby cannot surgically dispatch by name. (3) Direct-consume filter shape clarified — parent §3.B claim ambiguous; filter is post-fetch in-memory on dict return from `TheOddsSpider().fetch_data()`, NOT ORM query on SpiderData; couples to spider dict-return shape not persisted enum; cascades from S1501 §14.1. (4) ArbitrageDetector does NOT persist to sports.models.ArbitrageOpportunity despite full admin+serializer+viewset triple — KEPT AS DRIFT per Rigby cycle 1. (5) SignalCluster.pattern_type still lacks sports types — HIGH architectural risk; POSTURE-DECISION-PENDING per F2 fold. (6) Zero Cat B → Cat C outcome-to-agent learning loop — POSTURE-DECISION-PENDING per F3 fold. (7) Zero Memory Domain (S1300) bridge — POSTURE-DECISION-PENDING per F4 fold. (8) LineMovementAnalyzer + PredictionMarketAnalyst scope-boundary — called by coordinator + registered as PA tool but not in parent §3.B Cat B scope; owed to xx99 reconciliation. (9) Coordinator continue-on-error failure semantics — INTENTIONAL-OR-DRIFT NEEDING CONTRACT STATEMENT per F8 fold. **Cat B maturity verdict** per §13: **PARTIAL (armed but under-instrumented)** — beat fires 07:00 MT daily, coordinator invokes 5 agents, brief lands + SportsBettingBrief persists; but 4 of 5 agents lack Layer 1 telemetry + SignalCluster integration absent + no outcome-feedback loop + 2 of 4 audited agents missing from PA tool dispatcher + ArbitrageOpportunity model dormant. Group 1500 arc pin `pa-791b3db549a64e54` RETAINED per playbook §16 (carries P3-P6 sequence + P7 xx99); fresh SIGN pin `pa-64c019d7e6685d31` retired at S1502 close via Rigby `session_tool.retire`. §8 timeline S1502 row added. OPEN_ARCS Group 1500 current-child field advances "S1501 SIGN-clean cycle 2 (commit-gated) + S1502 queued next" → "S1502 SIGN-clean cycle 2 (commit-gated) + S1503 queued next"; row remains In-progress. Playbook §22 domain queue: Group 1300 closed S1399 + Group 1400 closed S1499 + Group 1500 In-progress (S1501 + S1502 landed, P3-P6 + xx99 remaining). Prior — v28 (2026-07-01, S1501 close): **First Group 1500 child audit landed at S1501 — Category A Sports Odds Ingestion & Normalization.** §1.31 `domains/sports/1501_sports_odds_ingestion_normalization_audit.md` added (child audit per playbook §11.2 20-section template; 1361 lines after F1-F7 folds; `status: active`, `category: child_audit`, `subdomain_category: A`; six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 5 load-bearing claims). D62 = (a) propagate upfront ratified by Chris at S1501 open — 4-item pre-brief mini-schema applied per surface for consistent evidence shape into P6/F posture-decision plan. Rigby Full SIGN cycle 1 SIGN-with-edits at Medium-High confidence via fresh isolation pin `pa-a39069230ab64450` (retired at S1501 close) → F1-F7 folds landed at commit-time (F1 §13 "WORKING (fragile contract) at ingestion, PARTIAL at normalization" qualifier; F2 §9 Q15 + §1 exec posture-decision-pending reframe cites S1274 §12.3 two-legitimate-postures precedent; F3 §17 dual-store SpiderData=semantic/log vs OddsSnapshot=UI-read-model clarification; F4 §15 debt severity adjustments — #1 HIGH confirmed / #2 → ARCHITECTURE-DECISION-PENDING / #6 LOW → MEDIUM; F5 §19 rank enum-resolution HIGH #2 + new HIGH #3 Downstream consumer inventory; F6 §14.3 unimplemented-expectation reframe; F7 §2.1 NEW Cat A contract statement — what Cat A guarantees today vs what it explicitly does NOT guarantee) → Rigby Full SIGN cycle 2 SIGN-clean at High confidence (cycle 1 prediction accurate). **D48 preemptive stability-probe gate 4th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501 4-arc pattern — clean stability probe + zero worker-instability observed across 4 substantive SIGN batches this session; recommended for immediate codification alongside D45 titles-only recovery + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent per S1499 §10 meta-methodology. **Load-bearing findings owed to xx99 posture-decision brief via Cat F evidence plan:** (1) Silent choices-enum violation on `SpiderData.data_type` + `source_platform` for sports/prediction-market rows — HIGH severity confirmed by Rigby SIGN cycle 1 Q5 + Q6 as riskiest operational finding; extends S1274 §14 Finding #6 beyond `SignalCluster.pattern_type` to `SpiderData` itself (Django CharField `choices=` validates only in Forms/Admin, not at `Model.save()`, so writes silently persist). (2) No unified normalization service — parent §6 P1-parked issue #1 grep-verified NEGATIVE; reclassified from HIGH to ARCHITECTURE-DECISION-PENDING per §2.1 Cat A contract confirms normalization is NOT part of Cat A's Cat B contract. (3) Dual-store `SpiderData` vs `OddsSnapshot`/`GameLineHistory` = posture-decision-pending intentional read-optimized-vs-semantic separation (not a defect). (4) `snapshot_odds_for_line_movement` dormant vs docstring (no beat entry). (5) Discord docstring drift on `#market-intelligence` vs code hardcode `CHANNEL_BOARDROOM`. **Cat A maturity verdict** per §13: **WORKING (fragile contract) at ingestion, PARTIAL at normalization.** Fixture-identity resolution across TheOdds `event_id` and Kalshi `ticker` upgraded to conditional MED-HIGH under any xx99 intent for cross-book aggregation per Rigby SIGN cycle 1 Q7. **New "Downstream consumer inventory" future-research item** added as HIGH #3 per Rigby Q7 fold — resolves whether dual-store is intentional posture or accidental divergence. Group 1500 arc pin `pa-791b3db549a64e54` RETAINED per playbook §16 (carries P2-P6 sequence + P7 xx99); fresh SIGN pin `pa-a39069230ab64450` retired at S1501 close via Rigby `session_tool.retire`. §8 timeline S1501 row added. OPEN_ARCS Group 1500 current-child field advances "S1500 arc-open + S1501 queued next" → "S1501 SIGN-clean cycle 2 (commit-gated) + S1502 queued next"; row remains In-progress. Playbook §22 domain queue: Group 1300 closed S1399 + Group 1400 closed S1499 + Group 1500 In-progress (S1501 landed, P2-P6 + xx99 remaining). Prior — v27 (2026-07-01, S1500 open): **Group 1500 Sports/DBAO/Intelligence arc OPENED at S1500.** §1.30 `domains/sports/1500_sports_domain_scoping.md` added (parent Phase 0 scoping per playbook §11.1 template; 1186 lines; `status: active`, `category: parent_scoping`; SECOND application of Chris's Phase 0 F.i/F.ii/F.iii methodology at §10/§11/§12 — applied UNCHANGED per D58 to preserve v3 promotion trigger integrity per S1400 D29 two-triggers rule). All 6 arc-open decisions Chris-locked in single "agree all + D-6=(a)" ratification round via governance decision `81d7467e-add6-420f-aee9-60b67d7867e8` (create + decide approve): D56 slug = `sports`; D57 parent-with-children (P1-P6 children + P7 xx99 at S1599); D58 methodology UNCHANGED; D59 load-bearing question = taxonomy + posture decision framing + evidence plan (Rigby refinement folded from pre-ratification pressure-test — NOT posture recommendation); D60 anti-scope + Intelligence bounded to sports-scope only; D61 DBAO = "Donkey Betz Analytics Ops" product-line codename option (a). Fresh S1500 arc pin minted `pa-791b3db549a64e54` via Rigby `session_tool.create_fresh`; `tools/pa_local.sh:128` updated from retired Group 1400 arc pin `pa-34d43795e1b24bd3` to fresh S1500 pin. **Load-bearing structural finding CONFIRMED at code level:** S1274 §14 Finding #6 — `sports_odds` NOT a valid `SignalCluster.pattern_type` (Signal Engine declares 10 canonical pattern types at `core/models_signal_intelligence.py:75-86`; `sports_odds` valid only on legacy `SpiderData.data_type`) — the runtime constraint Category F posture-decision evidence plan must confront per S1274 §12.3. **Runtime evidence anchored via 2 parallel Explore sub-agent sweeps at S1500 open against `main` HEAD `f7704586`:** Sports subsystem confirmed 5 models across 2 files (`core/models_betting.py:13,108,163` + `core/models_odds_history.py:15,82`) + 4 services + 5 spiders + 4 market agents in `core/agents/markets/` + 6 Celery tasks (2 beat schedule entries at `core/celery.py:784,788`) + 9-tab `BettingPage.tsx` at `/betting` route + 2 Discord commands + `/ws/dbao/` WebSocket + `dbao` PostgreSQL schema (per `docs/audit-2026/12-infrastructure.md:51`) + `sports_intelligence: True` feature flag at `intelligence/views.py:44`; zero body-system integration verified. **Locked child mission sequence (D57):** P1 S1501 Category A Odds Ingestion & Normalization → P2 S1502 Category B Prediction/Analytics Agents → P3 S1503 Category C Wager Tracking & Outcome Verification → P4 S1504 Category D Betting Content Pipeline → P5 S1505 Category E Frontend Sports Surface → P6 S1506 Category F Cross-Domain Integration Lens & Posture Decision Framing (LAST — consumes P1-P5 evidence) → P7 S1599 xx99 canonical summary (third application of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second). §8 timeline S1500 row added. Playbook v3 §11.1 template promotion criteria (Rigby caution 1 folded into §12.4): stricter than "ran twice" — xx99 §10.2 must demonstrate concrete discriminative-value evidence (scope confusion prevented + rework reduced + cleaner arc close + Chris-lock efficiency). Prior — v26 (2026-07-01, S1499 close): **Group 1400 Revenue arc CLOSED at S1499 xx99 canonical summary.** §1.29 `domains/revenue/1499_revenue_canonical_summary.md` added (arc-close canonical summary per playbook §11.3 12-section template + §10 "What This Research Taught Us About How to Do Research" second application after S1399 close 2026-07-01; 1915 lines; Rigby SIGN-with-edits cycle 1 substantive via fresh isolation pin `pa-877f1919efaa48e4` [retired post-fold] — 22 verdicts / 22 CONFIRM / 0 FLIP / 10 FLAG-EDIT framing refinements folded at commit-time; 0 must-fix; 0 severity flips; D48 stability-probe gate + warmup-ping + D45 titles-only recovery pattern successfully recovered from first-turn worker-instability; matches S1399 SIGN-clean cycle 1 pattern). **Revenue: high coverage, integration debt outstanding (T1)** — 4 of 9 lifecycle stages CRITICAL-INCOMPLETE (Stage 3 composition, Stage 4 delivery MISSING, Stage 5 ingestion MISSING, Stage 8 Revenue Received latent); 5 arc-wide 5-pillar convergence patterns confirmed (F2 orphan-write 8 sites unanimous; F1 provenance-filter narrow-scope 2 sites; state-machine incomplete 4 models 62% unreachable; learning-loop incomplete 3 sites; runtime-owner MISSING UNANIMOUS 6/6 — arc headline finding). D55 (ii) two sibling JobContracts (Revenue Employee for Cat A/B/C/D/E + Income/Jobs Employee for Cat F) ratified; D55 (ii) T3 Income/Jobs JobContract SPEC'D but not activated per T4 R.F3 = (b) dormant-planned Chris-lock (D-decision 2026-07-01). §8 timeline S1499 row added. **§7 Anchor-update recommendations** land in subsequent PR: 6 `platform_architecture_inventory.md` §3.32 corrections (F.D4/D5/D8 Cat D + F.E4/E6 Cat E + §4.9 outbound-channel broadening); NEW `docs/topics/revenue-pipeline.md` first-inventory landing; ARCHITECTURE_INDEX §5 gap entries consolidated (Group 1400 → closed); OPEN_ARCS Group 1400 In-progress → Closed. **Arc pin `pa-34d43795e1b24bd3` retired at arc-close** per playbook §16 arc-close discipline (D53 lock, `updated_count: 60`). Group 1400 arc closed via 8-doc arc: S1400 parent + 6 child audits (S1401-S1406) + S1499 canonical summary. **Second application of playbook §11.3 §10 meta-methodology template** — codifies 4 new patterns candidate for playbook v3 (D48 stability-probe gate + D45 recovery pattern + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent MET at 3-arc threshold, recommended for immediate codification). All 5 S1399-codified patterns REPLICATED in Group 1400. Prior — v25 (2026-07-01, S1406 Child F close): §1.28 S1406 Freelance/Gig — Income-Jobs lane audit; 10 F.F findings; provenance-stamp ORM probe first application; D48 stability-probe gate first application; 6-child Group 1400 arc complete + S1499 xx99 queued. See git history at commits `beda00e5` (S1401) → `7e80e54e` (S1406) for prior version details.
companion_anchors:
  - docs/PLATFORM_INVENTORY.md       # runtime anchor (counts source)
  - docs/PLATFORM_WHAT_IT_IS.md      # narrative anchor (glossary)
  - docs/EMPLOYEE_OS_PRIMITIVES.md   # canonical primitives + anti-duplication
  - docs/00-START-HERE/DOC_LIFECYCLE.md  # governs the corpus itself
  - docs/KNOWLEDGE_PIPELINE.md       # runtime flow map
  - docs/AUDIT_FINDINGS.md           # canonical Celery deferred list
  - docs/EVENT_SYSTEM_INVENTORY.md   # observability layers (§1.9 dep)
verifier_loop: |
  v5 update (2026-06-30, S1273 Part 2): re-inventoried docs/research/
  after S1273 landing. `ls docs/research/` now shows 8 .md files
  (7 research + this index). `platform_architecture_inventory.md`
  registered as §1.9 per §10.1 maintenance rules. Library scope
  broadens: §1.1-§1.8 remain the Employee-OS-focused arc; §1.9 is
  the whole-platform counterpart (Chris's explicit S1273-close
  direction). §1 preamble rewritten to acknowledge dual-scope
  library. §3 domain map extended for Revenue / Outreach /
  Engagement (Rigby caught this as a missed domain during S1273
  SIGN review; folded into §3.32 of §1.9 + registered here as new
  Revenue Pipeline domain row). §4 dep graph extended with whole-
  platform arc as sibling branch (does NOT depend on §1.1-§1.8 —
  parallel scope). §5: §5.4 Memory Architecture partially covered
  by §1.9 §3.13; new gaps §5.12 (Revenue Pipeline canonical
  architecture doc), §5.13 (Observability Deduplication Audit),
  §5.14 (Sports/DBAO ↔ AI Studio Integration Sketch) added per
  S1273 top-3 recommendations. §7 decision matrix +3 whole-
  platform rows. §8 timeline S1273 row. §9 lateral research list
  expanded to reference the 11-mission whole-platform roadmap in
  §1.9.
  Prior v4 update (S1273 Part 1): S1272 Authority Enforcement
  Design Space registered as §1.8 (Appendix C notes; frontmatter
  bumped to v4 mid-session).
  Prior v3 update (S1271 close): S1270 Symbol Mapping + S1271
  Actor Identity registered as §1.6 + §1.7 (Appendix B notes).
  Prior v2 note (S1269 close): added §1.4 governance research;
  §3/§4/§5/§7/§8/§9 updated per maintenance rules §10.1.
  Prior v1 note (S1268 close): inventoried docs/research/ at
  2026-06-30. Three docs present. Re-read each frontmatter before
  classifying. Self-verifier pass looked for missing docs,
  duplicate classifications, incorrect dependency ordering,
  inconsistent statuses, and discoverability gaps.
owner: claude (drafted S1268; v2 update S1269; v3 update S1271; v4 update S1273 Part 1; v5 update S1273 Part 2; v6 update S1274 Part 1 [concurrent §1.10 symbol_mapping_option_selection_design]; v7 update S1274 Part 2 [§1.11 DOMAIN_RESEARCH_PLAYBOOK v1]; v8 update S1275 [§1.12 symbol_mapping_event_schema_design]; v9 update S1300 [§1.13 domains/memory/1300_memory_domain_scoping — first parent-scoping doc; Group 1300 arc opened]; v10 update S1276 [§1.11 DOMAIN_RESEARCH_PLAYBOOK extended v1 → v2 in-place; process framework formalization]; v11 update S1277+S1278 [§1.14 RESEARCH_OPERATING_SYSTEM v2.1 canonical process framework + §1.15 claude_research_startup_introspection evidence base; three Rigby SIGN cycles; ratification READY WITH MINOR FOLLOW-UP]; v12 update S1279 [OS installation: CLAUDE.md pointer, OPEN_ARCS.md creation, START-HERE additions; OS status → active; OS CANONICAL]; v13 update S1301 [§1.16 domains/memory/1301_memory_rag_retrieval_lanes_audit — first child audit under Group 1300; Rigby SIGN-clean; owner-line drift fix on S1302 close]; v14 update S1302 [§1.17 domains/memory/1302_memory_persistence_architecture_audit — second child audit under Group 1300 covering Categories A+B+C combined; Rigby SIGN-clean after three fold cycles; F1 pa_content_feedback dead-code escalation + F2 orphan-write pattern narrowed across cycles from ~11 → 7 fields]; v15 update S1303 [§1.18 domains/memory/1303_memory_conversational_thread_memory_audit — third child audit under Group 1300, Category F Conversational / Thread Memory first-inventory landing; Rigby SIGN-clean after 12-edit fold + 1-cycle verification; F1 stale-thread waste reconciled via S1248 matched-pair fix; F3 verified soft-fail-at-import + latent-FieldError-at-query for content_writer_agent.py wrong-model+wrong-field; F4 discipline downgrade from "confirmed dead" to "CANDIDATE — not yet proven either way" per memory rule feedback_verify_before_deleting_dead_code; §19 R1 split into R1.a/b/c]; v16 update S1304 [§1.19 domains/memory/1304_memory_docs_rag_boundary_audit — fourth child audit under Group 1300, Categories E ↔ D Documentation Corpus ↔ RAG Boundary integration lens per parent §5 P4; Rigby SIGN-clean after 4-must-fix fold + verification pass; **partial invalidation of S1301 §19 D3 via S1304 verifier-loop** (source_type HAS owner-model-qualified consumer at content/embeddings.py:965-973; only ingested_via remains F1-CANDIDATE); D6 HIGH build_docs_provenance beat-unscheduled; §18 Documentation Manager JobContract at jobs.py:187-395 owns cascade steps 1-4; four boundary-maintenance responsibilities remain no-explicit-owner; §17 two provenance systems reframed complementary-not-duplicate via S1302 §17.3 methodology; §19 R5 turn-context → RAG enrichment inherited from S1303 §19 R3 routed to design-preparation phase]; v17 update S1305 [§1.20 domains/memory/1305_memory_runtime_correctness_audit — fifth (and final) child audit under Group 1300, Category H Runtime Memory Correctness NARROW scope per parent §5 P5 (Redis-loss + lru staleness only, not ops-in-general); Rigby SIGN-clean after 3-must-fix fold + verification pass on fresh pin pa-56a527a2c5528508 (retired at close); **first library audit to explicitly downgrade sub-agent severity via sibling-inherited context** — Agent 6 CRITICAL AgentLearningService durability claim → MEDIUM per Redis AOF at settings.py:944 matching S1302 T3 sibling classification; parent §3H 3 open questions closed (search_docs has no dedicated LRU, MemoryPromotionService no runtime cache, MemorySystem IS active via ai_core/agents/intelligent_job_matcher.py:57); 4 @lru_cache sites + 5 production cache.set(timeout=None) + 4-DB Redis topology + AgentLearningService within-process consistency gap + MemorySystem index→data divergence risk all with file:line cites; Group 1300 arc now closable via S1399 canonical summary next]; v18 update S1399 [§1.21 domains/memory/1399_memory_canonical_summary — **first formal xx99 canonical summary in the library** (S1268-S1275 arc predated the xx99 convention); consumes S1301-S1305 child outputs per playbook §11.3 bounded-work rule; Rigby SIGN-clean cycle 1 on fresh isolation pin pa-4fc3329d0db6484f at High confidence, 0 must-fix; four cross-cutting patterns named (F1 provenance-filter drift class; F2 row-level orphan-write pattern; F3 Redis-only durability + @lru_cache staleness; F4 F1/F4-CANDIDATE + severity-correction discipline as inheritance methodology); five contradictions resolved (§5.1-§5.5); anchor-update recommendations for platform_architecture_inventory.md §3.13 subdivision + §3.14 lane consolidation + new rows for Cat F + Cat H; 21-item ranked follow-on queue; 4 aggregated Group 1700 Observability delegations; Cat G delegated to Employee OS 1200s arc; Group 1300 arc closed per playbook §17 graduation criteria — Group 1400 Revenue next per playbook §22 queue]; v19 update S1399 §10 retrofit [meta-methodology section added to xx99 canonical summary template]; v22 update S1403 [§1.25 domains/revenue/1403_revenue_engagement_inbound_audit — third Group 1400 child audit, Category C Engagement Inbound; Rigby SIGN cycles 1+2 on fresh isolation pin pa-fba0c4c81fba4922 → SIGN-clean cycle 2 High confidence after cycle 1 fold (must-fix #1 CLOSED via parent-Claude Django ORM `.count()` on local — all 4 Category C tables 0 rows; must-fix #2 withdrawn as Rigby cycle-1 narrative artifact; 4 Q-answer folds Q1/Q4/Q5/Q6) + cycle 2 Q7/Q8/Q9 + 2 nice-to-have folds (Env Coverage Table + T.C8 three-checkbox split); load-bearing findings F.C1 zero-writer + F.C2 corrected axis map + F.C3 orphan-write CONFIRMED writer-site + F.C4/F.C5 docstring drifts + F.C6 run_ops_autopilot deferred-by-policy per AUDIT_FINDINGS.md #12; 11 verifier-loop checkpoints; sub-agent T.C4 dead-code overreach REFUTED via direct read + F2 CANDIDATE upgraded to CONFIRMED writer-site via direct read; four-way maturity split WORKING code / DEFERRED-BY-POLICY autonomous runtime / WORKING code + DORMANT local session-agg / MISSING ingestion; Rigby Q1 lean separate ADR outside G1400 for run_ops_autopilot enable-decision; Q4 lean two sequential ADRs F.B1→F.C1; isolation pin retires post-merge]; v20 update S1400+S1401 [§1.22 domains/revenue/1400_revenue_domain_scoping — Group 1400 Revenue arc opened with Phase 0 parent scoping doc + first application of Chris's F.i/F.ii/F.iii methodology; Rigby Light SIGN cycles 1+2 both SIGN-clean; 9 Chris-locked decisions across 3 "agree all" rounds — AND §1.23 domains/revenue/1401_revenue_opportunity_discovery_scoring_audit — first Group 1400 child audit shipped, Category A Opportunity Discovery + Scoring; 20-section playbook §11.2 template + §13 6-parallel-Explore sweep + parent-Claude verifier-loop pre-SIGN corrections on 5 sub-agent claims + Rigby SIGN cycles 1+2 on fresh isolation pin pa-16d8b24d30e7a7d8 → SIGN-clean cycle 2 High confidence after 4-fold cycle 1; NEW dual opportunity representation drift finding (5 consumer sites in consumers_base.py stream from intelligence_engine in-memory source, not persistent Django Opportunity); sports lane resolved as SEPARATE LANE with wording refinement; F1 provenance drift + F3 Redis-only durability CANDIDATE HIGH; NEW debt T5 Celery route duplicate; ownership gap CONFIRMED deferred to Child E per D28; S1273 §10.3 UNKNOWN #1 Opportunity model location RESOLVED at core/models_unified_system.py:1201])
---

# Architecture Research Index

> **What this is.** The front page of Donkey Betz's engineering
> encyclopedia. A Staff Engineer joining the project six months
> from now should read this document **first** — before opening
> any code, before reading CLAUDE.md, before touching a runtime
> file. It tells them what architectural research exists, why it
> exists, what order to read it in, and what decisions should
> never be made before reading specific documents.
>
> **What this is not.** A markdown link list. A taxonomy of every
> file under `docs/`. A historical archive. The wider `docs/`
> corpus has its own lifecycle (see
> `docs/00-START-HERE/DOC_LIFECYCLE.md`); this index governs the
> **research library specifically** — the docs that capture
> architectural reasoning *before* implementation.

---

## 0. Philosophy — why a research library exists

Before any system on this platform gets built or rebuilt, four
disciplines apply, in order:

1. **Research first.** Open-ended questions get a doc, not a
   sprint plan. The doc captures evidence with file:line cites
   and explicit unknowns; nothing is invented.
2. **Inventory before design.** Before you propose a primitive,
   you have to know what primitives already exist. The platform
   has **585 models**, **83 agents**, **113 PA tool schemas**,
   **91 enabled beat tasks** (see `docs/PLATFORM_INVENTORY.md`).
   Anything you "design" without that count in front of you is
   likely either re-inventing or violating
   `docs/EMPLOYEE_OS_PRIMITIVES.md` §2 (the anti-duplication
   matrix).
3. **Reuse before invention.** If an existing primitive does
   80% of the job, the right move is a wrapper, not a new model.
   Every "new model" instinct has cost an operator hour before;
   the names of those hours live in
   `EMPLOYEE_OS_PRIMITIVES.md` §2.
4. **Implementation last.** Once research + inventory + reuse
   are documented and reviewed, only then does code follow.
   PRs reference the research that justified them; the research
   exists to make the PR small.

These four disciplines map to the four document types you will
find in this library: **Audit**, **Inventory**, **Sketch**,
**Decision Record**. The first three precede code; the fourth
documents what the team decided once code is imminent.

**The verifier loop is the load-bearing rule.** Every research
doc in this library is grounded in direct file reads (Grep,
Read, ORM probes) — never recall, never assumption. When a
sub-agent produces evidence, the parent agent re-verifies a
sample by directly reading the cited file:line before
synthesizing. Rigby (the platform's PA / co-author) gets an
independent SIGN review on every doc before it's considered
publishable. Verdicts are **SIGN-clean**, **SIGN-with-edits**,
or **NEEDS-MORE**; edits are folded and the verifier_loop
frontmatter field is updated.

---

## 1. Current Architecture Research Library

The library has **two scopes as of S1273:**

- **The Employee OS arc (§1.1–§1.8):** an 8-doc chain that goes
  deep on a single subsystem. Each doc builds on the previous;
  read in order unless goal-driven (see §2 reading paths). This
  is the arc that began S1268 and closed STAGE 2 at S1272.
- **The whole-platform inventory (§1.9):** one doc, whole-
  platform scope. Independent of the Employee OS arc — read it
  when you need to know what domains exist across all of Donkey
  Betz, not when you're going deep on one subsystem. S1273 close
  registered it as "the whole-platform counterpart to the
  Employee OS research library" (Chris's direction).

**When to read which.** If your work touches a subsystem the
Employee OS arc has already researched (comms, governance,
authority, actor identity, mission orchestration), go to §1.1-
§1.8 for the deep dive. If your work touches a subsystem NOT in
that arc (frontend, spiders, RAG, betting, revenue, notifications,
etc.) — or if you're new to the platform and need the shape of
the whole thing — start with §1.9.

The two scopes will merge over time: as future missions bring
§1.9's LIGHT-coverage domains up to DEEP, they'll get their own
research docs registered as §1.10+, and §1.9 will remain the
navigation-and-classification layer.

### 1.1 `employee_os_communication_substrate_audit.md`

- **Title.** Employee OS Communication Substrate — Audit
- **Purpose.** Inventory every communication / collaboration
  primitive the platform already ships, classify each one for
  reuse, and identify the failure classes any future
  inter-employee protocol would inherit.
- **Status.** Draft → Active (SIGN-clean from Rigby S1268
  conversation `pa-01e90a1d36f54880`).
- **Research type.** Inventory + Architecture Audit + Failure
  Analysis (composite).
- **Primary questions answered.**
  - What communication substrates exist today?
  - Which are safe / wrappable / off-limits for reuse?
  - What's the receipt contract on Celery-dispatched tools?
  - What's the silent-failure history Employee OS would
    inherit?
- **Dependencies.** `PLATFORM_INVENTORY.md` (runtime
  anchor), `EMPLOYEE_OS_PRIMITIVES.md` (§2 anti-duplication
  matrix), `topics/employee-os.md`,
  `topics/agent-system.md`, `topics/personal-assistant.md`,
  `handoffs/SESSION_1267_*.md`.
- **Recommended next reads.** §1.2 (protocol sketch), then
  §1.3 (collaboration patterns).
- **Overall importance.** Foundational. Anything that touches
  inter-employee or inter-agent comms needs this read first.

### 1.2 `employee_os_communication_protocol_sketch.md`

- **Title.** Employee OS Comms Protocol Sketch — Platform
  Auditor → Chief of Staff
- **Purpose.** Take the substrate audit's `SAFE TO REUSE`
  primitives and scope the *first* concrete inter-employee
  write path. Reuse-only — explicit "do not enable
  `messaging_tool.send_message`" + explicit "no new model."
- **Status.** Draft → Active (SIGN-with-edits from Rigby
  S1268; two substantive edits folded — L3 helper-side dedupe
  + cadence expires_at default; two clarifications folded).
- **Research type.** Design Research / Protocol Sketch (not a
  decision record — no implementation greenlight).
- **Primary questions answered.**
  - What does an inter-employee notice look like as a bounded
    DM on existing `MessageThread` + `DirectMessage`
    primitives?
  - How does it thread without polluting the existing
    per-(employee, job) shift-report channels?
  - What's the dedupe contract (helper-side L1/L2/L3,
    caller-side defense-in-depth)?
  - What stays out of scope for v0 (HumanAttentionItem
    spawning, reply lane, fan-out, cross-fleet)?
- **Dependencies.** §1.1 (substrate audit must be read
  first); `EMPLOYEE_OS_PRIMITIVES.md`;
  `handoffs/SESSION_1267_EMPLOYEE_4_BUG_TRIAGE_SHIP.md`.
- **Recommended next reads.** §1.3 (the wider collaboration
  audit Rigby asked for as the next-mission frame).
- **Overall importance.** High for anyone scoping the first
  cross-employee write surface. Lower for anyone whose work
  doesn't touch inter-employee messaging.

### 1.3 `employee_os_collaboration_patterns.md`

- **Title.** Employee OS Collaboration Patterns — Platform-
  Wide Audit
- **Purpose.** Step back from "how do employees communicate"
  to "how do autonomous components *already* collaborate
  across the platform?" — so any future Employee OS work
  reuses existing collaboration mechanisms rather than
  reinventing them.
- **Status.** Draft → Active (SIGN-with-edits from Rigby
  S1268; one substantive correction folded — MissionRunner
  `verdict_issued` event is conditional on
  `auto_emit_verdict=True`, not guaranteed; one architectural
  blind-spot note added on canonical idempotency key across
  the two orthogonal orchestration paths).
- **Research type.** Architectural Discovery + Platform-Wide
  Inventory + Failure Analysis (composite).
- **Primary questions answered.**
  - Q1–Q8 from the mission spec, answered explicitly in the
    doc.
  - What are the eleven distinct collaboration substrates
    already in production?
  - Which 33 primitives are SAFE to reuse, which 10 need
    wrappers, which 4 should not be reused, and which 5 are
    UNKNOWN?
  - What 29 documented failure modes does any future
    collaboration design inherit (12 new beyond the substrate
    audit's baseline)?
  - What is the canonical foundation for future Employee OS
    collaboration? (MissionRunner + OpsRun + OpsRunEvent +
    AgentFollowupSubscription + `post_shift_report`-style
    helpers.)
- **Dependencies.** §1.1 + §1.2 (both prior research docs);
  `PLATFORM_INVENTORY.md`; `EMPLOYEE_OS_PRIMITIVES.md`;
  `topics/employee-os.md`, `topics/celery-workers.md`,
  `topics/agent-system.md`, `topics/initiative-pipeline.md`.
- **Recommended next reads.** Once this lands, the
  recommended **next research mission** is Governance +
  Authority Evolution (see §5 below). The next *design* work
  is the protocol sketch's v0 PR (assuming Chris greenlights
  it).
- **Overall importance.** Mandatory for anyone touching
  collaboration, orchestration, scheduling, mission
  coordination, or autonomy escalation.

### 1.4 `governance_authority_evolution.md`

- **Title.** Governance + Authority Evolution — Architectural
  Discovery
- **Purpose.** The canonical research anchor for every future
  authority or governance discussion. Inventories the governance
  + authority surface that exists today, identifies what's
  runtime-enforced vs. observational vs. documentation-only,
  surfaces the gaps, and recommends the next research mission
  (Symbol Mapping Architecture).
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1269;
  two must-fix edits folded — Exec Summary now uses canonical
  "four planes" framing instead of mixed "two + plus" framing,
  and gate count corrected 34→35; two clarifications folded —
  DO-NOT-REUSE-for-enforcement language on
  `JobContract.authority`, F4 budget-plane intent claim
  softened).
- **Research type.** Architectural Discovery + Platform-Wide
  Inventory + Failure Analysis (composite — same as §1.3 shape).
- **Primary questions answered.**
  - Q1–Q12 from the mission spec, answered explicitly in the
    doc's §12.1.
  - What are the four governance planes (autonomy / authority /
    budget / human governance) and why don't they compose today?
  - Where is authority enforced (35 runtime gates) vs. where is
    it only observed (warn-mode telemetry) vs. where does it
    disappear entirely (between MissionRunner and step.fn
    execution)?
  - What blocks the move from warn-mode to enforce-mode?
    (Symbol mapping — F2 + §11.)
  - What is the canonical foundation for governance reuse?
    (48 SAFE / 11 WRAPPER / 0 DO-NOT-REUSE / 0 DEPRECATED /
    3 UNKNOWN.)
- **Dependencies.** §1.1 + §1.2 + §1.3 (prior research docs);
  `PLATFORM_INVENTORY.md`; `EMPLOYEE_OS_PRIMITIVES.md` row 17
  (GovernanceState + KillSwitch); `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`
  (warn-mode design + enforce-mode prereqs).
- **Recommended next reads.** §1.5 (this index, for navigation
  context). The recommended **next research mission** per §11
  is Symbol Mapping Architecture (resolves §10 Q1 + Q12 of the
  collaboration audit + this doc's §9 Q1).
- **Overall importance.** Mandatory for anyone touching
  authority enforcement, governance modes, kill switches,
  budget controls, human approval lifecycles, or feature-flag
  gates.

### 1.5 Index doc (this file)

- **Title.** Architecture Research Index
- **Purpose.** Navigation. This doc.
- **Status.** Active (v3 — S1271 added §1.6 Symbol Mapping and
  §1.7 Actor Identity entries; §3-§9 updated per maintenance
  rules).
- **Research type.** Navigation / Decision Record (light).
- **Maintenance rule.** Every future research doc must update
  this index — see §10.

### 1.6 `symbol_mapping_architecture.md`

- **Title.** Symbol Mapping Architecture — Architectural Discovery
- **Purpose.** The canonical research anchor for the "WHAT
  action" question. What architectural bridge is missing between
  `JobContract.authority` policy strings and runtime symbols
  (tool names, step names, task names, function calls, model
  writes)? Enumerates the design space so authority enforcement
  can eventually be scoped.
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1270
  conversation `pa-cbcc410b32714f60`; two must-fix + three
  strongly-recommended optional edits folded — §8 narrowed
  `_AuthorityContractMalformedError` scope, §2.6 added
  parallel-vocabulary type/shape anchor, I-S4 wording softener,
  I-S3 dual-cite F1+F3, Option E "reversibility ≠ preference"
  disclaimer; §4.1 row 24 added for
  `AssistantProfile.get_allowed_tools`; §2.4 normalization caveat;
  §9 F11 with 7 architectural blind spots).
- **Research type.** Architectural Discovery + Platform-Wide
  Inventory + Failure Analysis (composite — same as §1.3 + §1.4
  shape).
- **Primary questions answered.**
  - Q1–Q8 from the mission spec, answered explicitly in the
    doc's §12.1.
  - What are the 57 unique authority strings (68 total entries),
    and where do they live?
  - What runtime action surfaces exist (12) and which carry
    action_class metadata today? (None.)
  - What identifier registries already exist on the platform
    (24) that could serve as reuse candidates?
  - What are the five mapping options (A/B/C/D/E) and their
    tradeoffs?
  - Where are the 20 candidate enforcement layers?
  - What historical failures (5 YES + 10 PARTIALLY + 8 NO of 23)
    would Symbol Mapping have prevented?
- **Dependencies.** §1.4 (the governance audit named this
  mission), §1.3, §1.1; `PLATFORM_INVENTORY.md`;
  `EMPLOYEE_OS_PRIMITIVES.md` §2 anti-duplication matrix;
  `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`.
- **Recommended next reads.** §1.7 (Actor Identity is the "WHO"
  companion). Then §9 roadmap STAGE 2 (Authority Enforcement
  Design Space) — the design mission that composes both.
- **Overall importance.** Mandatory for anyone scoping authority
  enforcement, adding a new employee's authority contract, or
  proposing action_class metadata on any runtime surface.

### 1.7 `actor_identity_attribution_architecture.md`

- **Title.** Actor Identity & Attribution Architecture —
  Architectural Discovery
- **Purpose.** The canonical research anchor for the "WHO
  performed it" question. Direct follow-on to §1.6 Symbol
  Mapping. When the platform records an action, how does it know
  who performed it? Both prereqs must land before authority
  enforcement can exist.
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1271
  conversation `pa-cbcc410b32714f60`; four must-fix + two
  strongly-recommended optional edits folded — §8.5 added
  introducing the executor_actor / sponsor_actor / principal_user
  3-role vocabulary as normative for the doc + §11 F11 summary
  finding; F1 language softened to "cannot answer reliably or
  queryably"; F9 softened to "the cleanest enforcement primitive";
  §3.5 added inventorying missing surfaces the platform does NOT
  ship; §9.4 Attribution-first counterargument paragraph; §5
  role-confusion framing note).
- **Research type.** Architectural Discovery + Platform-Wide
  Inventory + Failure Analysis (composite — same as §1.6 shape).
- **Primary questions answered.**
  - Q1–Q10 from the mission spec, answered explicitly in the
    doc's §14.1.
  - What actor identity concepts exist (19)?
  - Where is actor identity recorded (22 attribution surfaces —
    13 Explicit / 2 Inferred / 4 Ambiguous / 1 Unreliable /
    2 Missing)?
  - Where does identity change shape (14 shape changes, 3
    structural drop boundaries)?
  - What identity collisions have happened (15 historical
    incidents; 7 YES + 4 PARTIALLY + 4 NO — 73% effective
    case)?
  - What existing identity registries can be reused (25 — 14 SAFE
    + 7 WRAPPER + 0 DO-NOT-REUSE + 1 DEPRECATED + 3 UNKNOWN)?
  - What are the 17 candidate enforcement boundaries?
  - What does "actor" need to mean for Employee OS? (§8, six
    semantic questions posed.)
  - What is the relationship between actor identity and
    authority? (§9, the WHAT + WHO = enforcement primitive.)
  - What should the next research mission be? (§13.1 — Authority
    Enforcement Design Space.)
- **Dependencies.** §1.6 (Symbol Mapping is the WHAT companion),
  §1.4 (governance planes), §1.3, §1.1; `PLATFORM_INVENTORY.md`;
  `EMPLOYEE_OS_PRIMITIVES.md`; `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`.
- **Recommended next reads.** §9 roadmap STAGE 2 (Authority
  Enforcement Design Space) — the first design mission that
  consumes both §1.6 and §1.7.
- **Overall importance.** Mandatory for anyone touching actor
  identity on any audit surface, adding a `user` FK to OpsRun (a
  documented anti-pattern per §1.7 F11 without role clarity),
  proposing an actor primitive, or scoping the delegation/trust
  question. **F11 is especially load-bearing**: a single "actor"
  label is insufficient — enforcement-grade attribution requires
  at least executor_actor / sponsor_actor / principal_user as
  distinct roles.

### 1.8 `authority_enforcement_design_space.md`

- **Title.** Authority Enforcement Design Space — Architectural
  Discovery
- **Purpose.** The design-space research that must precede any
  enforce-mode PR. Symbol Mapping (S1270) answered WHAT action;
  Actor Attribution (S1271) answered WHO acted; this doc asks:
  given both prereqs are shipped as research, what are the
  possible ways the platform could eventually decide whether an
  actor was allowed to perform a mapped action? Enumerates the
  design space so a downstream design-with-Chris-gate mission
  can consume it. **Design-space only — no implementation,
  no decision.**
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1272
  conversation `pa-cbcc410b32714f60`; **Medium confidence**;
  8 must-fix edits folded — §3 gained 3 first-class boundaries
  (WebSocket, Fleet, Spider) closing a completeness gap Rigby
  flagged as "biggest architectural risk"; §9.0 neutrality
  guardrail; §9.1 + §9.2 annotation-burden failure modes;
  §9.6 policy-ossification risk; §8.4 rephrased separating
  prevent-modes from audit/warn modes; §10 Tier-0 hazards
  callout naming #1 + #8 + #15 as disproportionately-high
  blast radius; §6.1 role-propagation rule of thumb;
  §14 P0/P1 dependency-not-preference semantics + §14.2
  (i)/(ii) split.
- **Research type.** Design-Space Research + Platform-Wide
  Inventory + Composition Analysis + Failure Analysis
  (composite — first mission carrying design-space content per
  §9 STAGE 2 pacing note; still research-only, not design
  decision).
- **Primary questions answered.**
  - Q1–Q12 from the mission spec, answered explicitly in the
    doc's §15.1.
  - What are the 24 current enforcement-adjacent inputs
    (13 RUNTIME-VERIFIED / 7 OBSERVATION-ONLY / 3 ASPIRATIONAL
    / 1 UNKNOWN + 8 GAPS)?
  - What are the 20 candidate enforcement boundaries
    (17 original + 3 SIGN-added: WebSocket, Fleet, Spider)?
  - What are the 12 enforcement modes and their 204-cell
    (17×12) mode × boundary compatibility matrix?
  - What are the 4 interpretations per AuthorityLevel value
    (16 total; §5)?
  - How do executor_actor / sponsor_actor / principal_user
    compose across 11 canonical scenarios (§6)?
  - How does authority enforcement compose with the 4 governance
    planes (§7; 1 existing cross-plane touch + 8 new
    composition questions)?
  - Which historical incidents would each mode have prevented
    (33-incident matrix across 4 prior catalogs; §8)?
  - What are the 6 major design options (A-F; §9)?
  - What are the 15 anti-patterns to avoid (§10; Tier-0
    hazards flagged)?
  - What are the 15 prerequisites for enforce-mode and their
    dependency DAG (§11)?
- **Dependencies.** §1.6 (Symbol Mapping — WHAT input premise),
  §1.7 (Actor Attribution — WHO input premise), §1.4
  (governance planes), §1.1, §1.3;
  `PLATFORM_INVENTORY.md`; `EMPLOYEE_OS_PRIMITIVES.md`;
  `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`.
- **Recommended next reads.** §14.1 recommends Symbol Mapping
  Option Selection Design as P0 next research. The 6 design
  options in §9 will be consumed by that downstream mission +
  the Authority Enforcement Design Decision that follows it.
- **Overall importance.** Mandatory reading for anyone scoping
  authority enforcement, evaluating one of the 6 §9 design
  options, proposing an OpsRun schema change, or wiring a new
  enforcement boundary. **F1 is especially load-bearing:**
  AuthorityLevel has exactly one runtime consumer today
  (shape-counter at `mission_runner.py:864-867`) — the enum is
  policy metadata, not enforcement metadata; any design
  introduces the first decision-making consumer. **F8 fail-open
  precedent is the second load-bearing finding:** LLMEnforcer
  at `llm_enforcer.py:237-238` sets the platform's precedent
  for INLINE-gate error handling — any authority enforcement
  design must decide fail-open vs. fail-closed and cite
  rationale.
- **Boundary caveat.** The 3 SIGN-added boundaries
  (WebSocket / Fleet / Spider) are named but not yet
  cross-tabulated against the 12 modes in the 204-cell matrix.
  A future research pass or design mission should extend the
  matrix.

### 1.9 `platform_architecture_inventory.md`

- **Title.** Donkey Betz Platform Architecture Inventory — first
  whole-platform map
- **Purpose.** The whole-platform counterpart to the Employee-OS-
  focused §1.1-§1.8 arc. Inventories every major architectural
  domain of Donkey Betz — 32 domains — with maturity ratings,
  research coverage, existing docs, drift, and technical debt.
  Names the recommended next 11 research missions. **This is the
  doc a Staff Engineer new to the platform should read to
  understand the shape of the whole system.**
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1273
  conversation `pa-02cfd3206302352f`; Medium overall confidence;
  6 substantive edits folded — (1) added missed §3.32 Revenue /
  Outreach / Engagement Pipeline domain + §4.9 cross-domain flow;
  (2) downgraded §3.27 Auth / Permissions maturity STABLE →
  PARTIAL with trust-boundary enumeration; (3) upgraded §3.7 LLM
  Provider Registry maturity WORKING → STABLE (core registry
  stable, failover missing); (4) tightened §1 Executive Summary
  count phrasing to autoblock-consistent language; (5) added
  §3.31 Event Bus vs Observability separation-of-concerns
  paragraph; (6) expanded §9 roadmap 10 → 11 missions with
  Revenue Pipeline canonical architecture doc elevated to #2).
- **Research type.** Architectural Inventory + Platform-Wide
  Mapping + Maturity Classification (whole-platform composite;
  distinct shape from §1.1-§1.8 which are Employee-OS-focused
  audits / sketches / discovery / design-space).
- **Primary questions answered.**
  - What are the 32 major architectural domains of Donkey Betz?
  - Which domains are mature (CANONICAL/STABLE) vs risky
    (PARTIAL/EXPERIMENTAL)?
  - Which domains are under-researched (NONE/LIGHT coverage)?
  - What are the 9 cross-domain flows that traverse ≥ 2
    domains?
  - Which systems duplicate or overlap (8 categories: multiple
    orchestration paths / multiple messaging systems / multiple
    identity concepts / multiple memory stores / multiple
    governance surfaces / multiple content pipelines / multiple
    task/execution logs / multiple agent dispatch systems)?
  - What are the 11 recommended next research missions, ranked
    by architectural uncertainty × risk × reuse × decisions
    unblocked?
- **Dependencies.** `PLATFORM_INVENTORY.md` (authoritative
  counts anchor), `PLATFORM_WHAT_IT_IS.md` (narrative anchor),
  `EMPLOYEE_OS_PRIMITIVES.md` (canonical primitives),
  `KNOWLEDGE_PIPELINE.md`, `EVENT_SYSTEM_INVENTORY.md`,
  `AUDIT_FINDINGS.md` §12. Also depends on the entire Employee
  OS arc (§1.1-§1.8) for the subset of findings that overlap;
  cites governance-authority-evolution.md (§3.23),
  symbol_mapping_architecture.md (§9.1), and
  actor_identity_attribution_architecture.md (§5.3) where
  relevant.
- **Recommended next reads.** Depends on goal:
  - If interested in specific domain: jump to that §3.n
    inventory + cited docs.
  - If interested in cross-domain flows: read §4 (9 flows).
  - If interested in what's next: read §9 (11-mission roadmap
    — top-3 are Authority Enforcement Design Space (§5.2c
    here), Revenue Pipeline canonical architecture (§5.12
    here), Observability Deduplication Audit (§5.13 here)).
- **Overall importance.** **Foundational for whole-platform
  understanding.** The Employee OS arc (§1.1-§1.8) is deep on
  one subsystem; §1.9 is wide on all of them. A new hire should
  read §1.9 first to know the map, then dive into whichever arc
  their work touches. Existing team members should reference §1.9
  when scoping cross-domain work or evaluating "does this touch
  a mature domain or an experimental one?"
- **Verifier-loop note.** Six parallel Explore sub-agents
  produced independent domain sweeps; parent synthesized into
  the 32-domain map. Every domain row is grounded in file:line
  cites OR flagged UNKNOWN. Rigby SIGN-with-edits (fresh pin
  `pa-02cfd3206302352f`, NOT the shared S1270+ arc pin
  `pa-cbcc410b32714f60` — another Claude Code was on that pin;
  Chris flagged the context-crossing risk mid-session; isolation
  pin used to keep S1273 work separate).

### 1.10 `symbol_mapping_option_selection_design.md`

- **Title.** Symbol Mapping Option Selection Design — Research +
  Design Preparation (Chris-gated decision)
- **Purpose.** The design-preparation mission that follows §1.8
  Authority Enforcement Design Space. Where §1.6-§1.8
  enumerated options neutrally, §1.10 is the **first mission
  producing an evidence-based recommendation**: which of §1.6's
  5 Symbol Mapping options should Chris choose as v0? **The
  recommendation is a starting point for Chris, not a
  substitute for his decision.**
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1274
  conversation `pa-cbcc410b32714f60`; **Medium confidence**;
  Rigby recommendation: **Modify** — agree with Option E as v0
  subject to 4 must-fix tightenings; all folded).
  Four must-fix folded:
  (1) §8.8 whole-platform generalization claim tightened —
      "STRONG once producers exist; v0 coverage remains narrow
      (2/4/14 per §8.1); Fleet/WebSocket/Spider excluded until
      instrumented" (was overstated as absolute STRONG);
  (2) §10.3.1 catastrophic-action graduation guardrail added —
      4 telemetry triggers force Chris decision within 30 days
      (prevents "E-forever cope");
  (3) §12.1 non-NULL misclassification drift pattern added —
      sample-based truthing + cross-source consistency +
      golden-flow tests (higher-risk than producer omission
      per Rigby "wrong-but-non-NULL action_class" concern);
  (4) §11 employee_handle vs. executor_actor distinction
      clarified — employee_handle is Employee OS identity
      (NULL for non-mission actions); executor_actor is
      generalized runtime executor. Do NOT collapse.
- **Research type.** Design Preparation + Comparative Analysis
  + Evidence-Based Recommendation (composite; first mission in
  the S1268-founded library carrying an actual recommendation
  Chris can gate).
- **Primary questions answered.**
  - Q1-Q10 from mission spec, answered explicitly in the doc's
    §15 open questions + §16 next mission recommendation.
  - Which of §1.6's 5 Symbol Mapping options is safest v0?
  - Which is the recommended end-state?
  - What is the smallest reversible design that unlocks
    authority telemetry?
  - What must remain out-of-scope for v0?
- **Recommendation shape.**
  - **v0 (recommended):** **Option E — Evidence-only mapping.**
    Extend a minimum set of audit models (`ToolCallRecord`,
    `OpsRunEvent`, `LLMCallEvent`, `CeleryTaskEvent`,
    `AgentExecution`) with optional `action_class` field + all
    three actor role fields; instrument 3-5 highest-leverage
    producer sites incrementally; emit
    `authority_action_observed` events; **never blocks**.
  - **End-state (Chris-gated later; possibly 6-24 months
    out):** E foundation + Option B (tool schema
    `action_class` attribute) layered on top for pre-dispatch
    tool-mediated enforcement.
  - **Explicitly rejected:** Option C bundled standalone.
  - **Deferred:** Options A, B, D as tertiary layers pending
    telemetry evidence from Phase 5 E-only steady state.
  - **Maintenance note:** Option E as recommendation is for v0
    ONLY. It is **not implementation** and **not enforce-mode**.
    Chris gates every downstream step: (a) whether to ratify
    Option E as v0, (b) whether to graduate to E+B per §10.3.1
    guardrail triggers, (c) whether to add more layers.
- **Dependencies.** §1.4 (governance planes), §1.6 (5 mapping
  options — the input premise), §1.7 (3-role vocabulary — MUST
  be preserved), §1.8 (design space + 15-prereq DAG),
  `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md` (warn-mode
  precedent), `EMPLOYEE_OS_PRIMITIVES.md` §2 anti-duplication.
- **Recommended next reads.** §16 recommends Symbol Mapping
  Event Schema Design as the next mission (design the
  concrete event schema + producer instrumentation contract +
  retention policy + Bug Triage step 4 extension). Rigby SIGN
  at close of that mission.
- **Overall importance.** Foundational for anyone scoping the
  first authority-enforcement PR. Reading order: §1.6 (options
  enumerated) → §1.7 (actor vocabulary) → §1.8 (design space +
  prereqs) → §1.10 (recommendation) → downstream Symbol Mapping
  Event Schema Design mission (design → implementation gate).
  **F1 load-bearing:** the recommendation is E because it is
  the *most reversible* and *safest v0*, not because it is the
  *best end-state*. Do not read §1.10 as "E is the answer";
  read it as "E is the safest starting move." Chris re-decides
  at every phase per §10.3.1 guardrail.

### 1.11 `DOMAIN_RESEARCH_PLAYBOOK.md`

- **Title.** Domain Research Playbook — canonical framework
  for every Donkey Betz architectural research group
- **Current version.** **v2** (S1276, 2026-07-01). Extended in
  place from v1 (S1274). v2 restructures into 7 parts / 24
  sections and formalizes fifteen areas that emerged after v1
  shipped. Version history in playbook §20 changelog.
- **Purpose.** Process document that codifies the methodology
  developed across S1268-S1275 into a **reusable framework** so
  future Claude Code sessions can start a domain research group
  with a short request like *"Start research group 1300:
  Memory"* — no 4,000-word prompt required. v2 additionally
  makes arcs *closable*: Chris can now say *"Close research
  group 1300"* and the framework produces a canonical summary.
  Standardizes: numbering ranges (1300 Memory → 1900 Event
  Architecture) with xx99 canonical-summary reservation,
  parent-with-children arc lifecycle, phase discipline
  (research / design-preparation / design-decision / process /
  navigation / implementation), output paths
  (`docs/research/domains/<slug>/<session_id>_<slug>_<type>.md`),
  self-describing metadata standard, 28 canonical audit
  questions, 20-section child audit template + parent template
  + canonical summary template, 6 parallel Explore sub-agent
  sweeps, classification rules (Coverage / Maturity / Risk /
  Finding Type / Integration Strength), cross-reference
  policy, stage-scoped Rigby SIGN routing, commit rules,
  graduation criteria, cross-arc dependency mapping,
  generalization requirements, and evolution policy for the
  playbook itself.
- **Status.** Active (process documentation — no Rigby SIGN
  routed per §15's own rule for `authority: process`).
- **Research type.** Process Documentation / Meta (framework
  for other docs; does not produce research findings itself).
- **Primary questions answered.**
  - How does a future Claude Code session start a domain
    research group (single audit vs parent-with-children)?
  - What research group ranges are planned (1300s-1900s)?
  - What is the lifecycle of a research group (STAGE 0 parent
    → STAGE 1 children → STAGE 2 canonical summary → STAGE 3
    index update → STAGE 4 complete)?
  - How do research, design-preparation, and implementation
    differ, and how do docs signal which phase they belong to?
  - What belongs in a parent doc vs a child audit vs a
    canonical summary?
  - What is the canonical folder structure and file naming?
  - What metadata does every research doc need to be
    self-describing?
  - How do docs cross-reference each other without
    duplicating content?
  - What are the 28 canonical questions every child audit
    must answer?
  - What classifications must every domain audit use?
  - What is the Rigby SIGN review policy per stage?
  - When is it OK to commit vs when should draft stay
    uncommitted?
  - When is a research group *complete* (objective graduation
    criteria)?
  - How do cross-arc dependencies + delegations get recorded?
  - How does the playbook itself evolve without breaking
    older research groups?
- **Dependencies.** §1.9 (32-domain map — the audit target
  list), `docs/research/platform/cross_domain_integration_audit.md`
  (integration gap map — the S1274 sibling context each domain
  audit inherits), `docs/PLATFORM_INVENTORY.md` (runtime
  counts), `docs/research/domains/memory/1300_memory_domain_scoping.md`
  (S1300 parent-with-children exemplar — the doc that proved
  the v2 arc shape). Also inherits all lessons from §1.1-§1.8
  methodology history.
- **Recommended next reads.** For anyone starting a research
  session: read this playbook first (§1-§7 minimum), then the
  S1273 §3.N row for your target domain, then the S1274 §2.N +
  §3-§10 rows for cross-domain context, then existing topic
  docs for the domain. Only then execute STAGE 0 (parent) or
  STAGE 1 (single audit).
- **Overall importance.** **Foundational for every future
  research session.** Reading order for a fresh Claude Code:
  §1.11 (this playbook) → whatever domain the user picked.
  This should be the FIRST doc a fresh session reads after
  `CLAUDE.md`. The v2 additions make the framework
  self-describing — a fresh Claude Code that reads *only* the
  playbook + ARCHITECTURE_INDEX + PLATFORM_INVENTORY can
  execute a research arc end-to-end.
- **Initial domain queue** (from playbook §22): 1300 Memory
  (opened S1300 — parent locked), 1400 Revenue, 1500 Sports,
  1600 Content, 1700 Observability, 1800 HumanAttention, 1900
  Event Architecture. Queue order is a default, not a
  dependency — sessions can pick any.
- **Distinguishing property.** This is `authority: process`
  with `version: v2`, not `authority: research`. It sets rules
  for other docs rather than producing findings. Chris ratified
  v1 registration at S1274 close (*"register it now and
  commit"*) and v1 → v2 extension at S1276 open (*"Formalize
  the research process itself so future domain research
  becomes repeatable"*).
- **Backwards compatibility note.** Research groups closed
  under v1 (Employee OS arc §1.1-§1.8, whole-platform §1.9,
  cross-domain integration §1.10-§1.12) remain valid under
  v1. They do not retroactively conform to v2 additions. Per
  playbook §20, older research groups reference the playbook
  by version — v2 does not invalidate v1 outputs.

### 1.12 `symbol_mapping_event_schema_design.md`

- **Title.** Symbol Mapping v0 — Event Schema Design (`authority_action_observed`)
- **Purpose.** Closes §5.2d. Takes §1.10's Option E v0
  recommendation and pins the concrete event schema: canonical
  name, two-surface host (`OpsRunEvent` for mission scope +
  `ToolCallRecord.parameters` for non-mission tool calls,
  unified via a new `authority_action_observed_stream` DB
  view), 21 payload fields (7 required + 5 semi-required + 6
  optional + 3 reserved), 4 v0 emitters + 1 v0 first consumer,
  4-tier `mapping_confidence` enum with DECLARED explicitly
  non-authoritative, drift-detection stack across 6 patterns
  (NULL rate, wrong non-NULL via sampled truthing, zero-fire,
  cross-emitter disagreement, invariant + reserved-keys
  violations, schema drift), 3 golden flows, batch-mode v0
  dashboard, 15 out-of-scope items, and a change log capturing
  Rigby SIGN fold decisions.
- **Status.** Draft (Rigby SIGN-with-edits folded — 8
  must-fixes + bonus #9; awaiting Chris canonical sign-off).
- **Research type.** Design preparation (third design mission
  in the STAGE 2/3/4 Symbol Mapping arc, following §1.6
  Architectural Framing and §1.10 Option Selection).
- **Primary questions answered.**
  - What is the canonical event name? → `authority_action_observed`
  - Which existing audit surface(s) host it? → two-surface stream
    (`OpsRunEvent` + `ToolCallRecord.parameters`) + UNION view
  - What is the minimum viable schema, field by field?
  - Which 4 emitters go first, and what is the first consumer?
  - How is `action_class` populated per emitter × confidence tier?
  - How does `mapping_confidence` work — and why is DECLARED
    explicitly non-authoritative?
  - How are the 3 actor roles + graph position + identity marker
    kept separate?
  - How does the design prevent wrong-but-non-NULL
    false confidence? → sampled-truthing loop + weighted
    cross-emitter disagreement + invariant validator + golden
    flows
  - What are the first 3 golden flows?
  - What does the v0 dashboard / query API look like?
  - What is explicitly out of scope for v0? → 15-item list
- **Dependencies.** §1.10 (Option E as v0 ratified), §1.7
  (3-role actor vocabulary preserved), §1.6 (architectural
  framing), §1.8 (§11 15-prereq DAG — closes prereqs #3
  Evidence Event Schema and #4 Violation Event Schema at v0
  scope), `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`
  (`authority_contract_observed` warn-mode precedent —
  `authority_action_observed` is the action-level parallel),
  `EMPLOYEE_OS_PRIMITIVES.md` §2 (anti-duplication —
  justification for reusing existing audit models).
- **Recommended next reads.** After Chris canonical sign-off:
  the implementation prep sequence (rollout plan §15 outlines
  P0→P5 phases across ~10 weeks). Before then: cross-read
  against §1.10 §16 (out-of-scope list — that mission handed
  off 11 items that §1.12 §16 closes with 15 items).
- **Overall importance.** **First mission in the library that
  ships a concrete implementation-ready schema.** Prior
  Symbol Mapping missions produced framing (§1.6) and selection
  (§1.10); this one produces the field-level spec. Not yet
  implemented — Chris gates every subsequent PR. Rigby SIGN
  fold captures 8 must-fixes (ambient OpsRun → two-surface,
  drop required `event_id`, drop `notes`, downscope
  `producer_version`, rename `delegator_actor` → `caller_actor`,
  reframe "5 producers" → "4 emitters + 1 consumer", rename
  INFERRED → DECLARED, add sampled-truthing loop, DEFINITE ≠
  global truth) plus bonus #9 (reserved-keys policy + per-field
  caps).
- **Maintenance note.** This is the third design-preparation
  doc in the STAGE 2/3/4 Symbol Mapping arc. Do NOT treat as
  implementation greenlight — the rollout plan in §15 is a
  sequencing sketch, not a merged PR. If Chris ratifies the
  design at review, the next research artifact is either a
  Trust Propagation Model (§5.3) or the Employee Boundary
  Escalation Contract (§5.4) — both P1s at this point.

### 1.13 `domains/memory/1300_memory_domain_scoping.md`

- **Title.** S1300 Memory — Parent Architecture Scoping
  (Group 1300 mission plan)
- **Purpose.** First **parent-scoping** doc in the library —
  a shape not previously exercised. Chris opened S1300 with
  the playbook §11 short command "Start research group 1300:
  Memory" but pushed back on the standard a-f scope-pick
  framing: "Your clarification uncovered an architectural
  ambiguity rather than a simple scoping question. Treat this
  as a Phase 0 domain-definition exercise." The doc answers
  the single structural question — is "Memory" one domain or
  a parent capability composed of multiple architectural
  subdomains — enumerates 8 candidate subdomains (Categories
  A-H) grounded in existing inventory evidence, and asks
  Chris to gate parent-with-children vs single-audit before
  any audit work begins.
- **Status.** Active (parent — Chris decisions locked
  2026-07-01). Phase 0 complete. Session S1300 closed early
  per Chris directive; no P1 audit work in this session.
- **Research type.** Domain-definition / arc scoping
  (`authority: parent-doc`). Distinct from `authority:
  research` (audit findings) and `authority: process`
  (playbook rules).
- **Primary questions answered.**
  - Is "Memory" one domain? → No. §3 taxonomy enumerates 8
    candidate subdomains; S1273 already treats Memory as a
    3-row §3 cluster (§3.13/§3.14/§3.15) with §5.4 flagging
    "Multiple Memory / Knowledge Stores" independently.
  - Parent-with-children or single canonical audit? →
    Parent-with-children (Chris D1, 2026-07-01). Playbook §2
    rule 3 explicitly permits sub-grouping.
  - What is the Group 1300 arc shape? → S1300 parent →
    S1301 RAG Retrieval Lanes → S1302 Memory Persistence
    Architecture → S1303 Conversational/Thread Memory →
    S1304 Docs Corpus ↔ RAG Boundary → S1305 Runtime Memory
    Correctness → S1399 canonical summary (7 sessions total).
  - Which subdomain owns Employee OS mission memory? →
    Category G delegated to Employee OS 1200s follow-up arc
    (Chris D2). Group 1300 cross-links only; does not fold
    G in. Boundary respected: S1273 inventory homes it
    under §4 Employee OS, not §3.13.
  - Where does the RAG excluded_missing_provenance finding
    (surfaced at S1300 open — Rigby `search_docs` returned 8
    pre-filter → 7 excluded_missing_provenance + 1
    excluded_mismatch → 0 for OpsRun/MissionRunner/
    JobContract queries) go? → Parked as S1301 audit input
    under §6 (Chris D3). Not pursued in Phase 0.
  - Why the P2 rename? → "Memory Store Overlap Audit" →
    "Memory Persistence Architecture" (Chris D4). Wider
    frame captures durability + write/read paths + authority
    boundaries, not just overlap surfacing.
  - What closes the arc? → S1399 canonical summary planned
    (Chris D5): cross-cutting patterns across P1-P5,
    consolidated memory-subsystem shape, `PLATFORM_INVENTORY.md`
    §3 update recommendations, follow-on research queue.
- **Dependencies.** `DOMAIN_RESEARCH_PLAYBOOK.md` §11 short-
  command entry point (§1.11), `platform_architecture_inventory.md`
  §3.13/§3.14/§3.15/§5.4 (§1.9), `docs/narratives/KNOWLEDGE_
  RAG_MEMORY.md` (S1158 comprehensive narrative),
  `docs/KNOWLEDGE_PIPELINE.md` (flow map).
- **Recommended next reads.** After Chris canonical sign-off
  on §1.13 parent scoping (and greenlight on S1301 launch
  cadence — open D6 at S1300 close): begin `1301_memory_rag_
  retrieval_lanes_audit.md` under playbook §11 opening
  sequence, feeding the §6 provenance-filter finding as
  S1301 input.
- **Overall importance.** **First parent-scoping doc in the
  library** — a shape not previously exercised. Introduces
  the pattern where a research group opens with a taxonomy
  proposal that gates whether the group is one audit or an
  arc of child audits. Playbook §2 rule 3 already permitted
  sub-grouping; §1.13 is the first mission to actually
  exercise it. Also validates the DOMAIN_RESEARCH_PLAYBOOK.md
  short-command workflow — Chris's "Start research group
  1300: Memory" reached the playbook §11 opening sequence
  successfully.
- **Maintenance note.** This doc is the **parent** of Group
  1300. It is NOT itself an audit — it is the arc-plan that
  gates the child audits. If any child audit contradicts the
  parent's taxonomy boundaries, the child should update the
  parent (via a new v-number pass), not silently drift.
  Session S1300 ended EARLY at Chris close directive —
  Phase 0 scoping complete but no P1 audit work landed in
  this session. Open decisions at S1300 close: (D6) S1301
  launch cadence (default: pause for Chris review before
  greenlight); (D7) Rigby SIGN routing on parent doc
  (default: skip — playbook §9 attaches SIGN to audits, not
  scoping).

### 1.14 `RESEARCH_OPERATING_SYSTEM.md`

- **Title.** Research Operating System — the OS every Claude
  Code session executes in Donkey Betz
- **Current version.** **v2.1** (S1278, 2026-07-02). v1 →
  v1.1 (S1277 Rigby SIGN fold) → v2 (S1277 re-issue with 6
  new parts) → v2.1 (S1278 ratification + playbook cross-ref
  cleanup + §20 finalization).
- **Purpose.** The canonical process framework Claude Code
  executes across **every** class of work in the repo. Where
  the playbook (§1.11) governs research-class sessions
  specifically, this OS is the *superset* — it defines
  bootstrap sequence, request classification, per-class
  startup contracts, documentation authority hierarchy,
  research/completion contracts, research debt, ownership
  matrix, and Context-Kit boundary. Turns onboarding
  deterministic and prompt-independent. The success target:
  a brand-new Claude Code reads this document, executes
  bootstrap, classifies the user request, runs the matching
  startup contract, and begins contributing — **without Chris
  writing a 4,000-word prompt.**
- **Status.** **Active — CANONICAL** as of S1279 close
  (2026-07-02). v2.1 architecture complete; 3 P0 follow-up
  items landed at S1279 installation (CLAUDE.md pointer,
  `OPEN_ARCS.md`, START-HERE additions); OS status flipped
  `draft` → `active`. Every future Claude Code session
  executes this doc.
- **Research type.** Process Documentation / Meta / Canonical
  framework (analogous to §1.11 playbook but broader scope).
- **Primary questions answered.**
  - How does a fresh Claude think? (§3 Decision tree)
  - What does bootstrap look like? (§4 Level A + Level B)
  - How is a request routed? (§5 11 request classes + boundary
    rules)
  - What state surfaces exist? (§6 session + arc + runtime)
  - What is the documentation authority hierarchy? (§7 11 tiers
    with truth-authority vs read-priority split)
  - What startup contract per class? (§8.1-§8.11)
  - What thinking templates exist? (§9 registry)
  - What is discoverable today? (§10 audit)
  - Who owns which doc? (§11 ownership matrix + anti-patterns)
  - How does research reduce prompt burden? (§12 target rhythm)
  - What is a Research Contract? (§13 8 mandatory fields)
  - What is a Completion Contract? (§14 10-item close checklist)
  - What is Research Debt? (§15 concept + 7 categories +
    priority formula + escalation)
  - What is the one-year vision? (§16)
  - What is the Research Philosophy? (§1 stop condition +
    anti-patterns)
  - What is the Context-Kit boundary? (§2 ownership +
    drift-prevention model + do-not-duplicate list)
- **Dependencies.** `DOMAIN_RESEARCH_PLAYBOOK.md` v2 (§1.11 —
  the research-class specialization the OS calls), all §1.1-
  §1.13 research library entries (context for what the OS
  governs), `docs/PLATFORM_INVENTORY.md`, `docs/PLATFORM_WHAT_IT_IS.md`,
  `docs/00-START-HERE/DOC_LIFECYCLE.md` §2c, `docs/EMPLOYEE_OS_PRIMITIVES.md`,
  Context-Kit skill + `docs/docs-pattern/`.
- **Recommended next reads.** For anyone opening a new session
  in this repo: bootstrap Level A (§4.1) is the answer. For
  understanding *how* the OS integrates: §2 Context-Kit
  Integration + §7 Documentation Authority. For starting
  research work: §5 router → §8.1 RESEARCH contract → §1.11
  playbook.
- **Overall importance.** **Foundational — the highest-
  authority process doc in the library.** The playbook
  (§1.11) is one specialization of this OS. Reading order
  for a fresh Claude Code: (1) `CLAUDE.md` — session
  instructions; (2) OS §0-§5 — orientation + routing; (3)
  Level B contract per §5 classification. This doc supersedes
  no prior work; it consolidates and formalizes the process
  discipline that emerged across S1268-S1276.
- **Rigby SIGN history.** Three cycles across S1277-S1278:
  (1) v1 draft → v1.1 SIGN-with-edits (Medium confidence,
  fresh pin `pa-95ce3cbf0a2aa0cc`, 15 must-fixes folded on
  bootstrap/router/authority/contracts/templates); (2) v2
  extension → v2 SIGN-with-edits (Medium confidence, fresh
  pin `pa-117d3edf9d7b80f8`, 12 must-fixes folded on the six
  new parts); (3) v2.1 finalization → High-confidence
  SIGN-with-edits (fresh pin `pa-30278fb65295e74c`, zero
  factual errors, edits = docs-only follow-up items already
  flagged as P0 non-blocking).
- **Distinguishing property.** This is `authority: process`
  with `version: v2.1`. Governance-tier — every future
  Claude Code session executes it. Playbook (§1.11) is a
  specialization; OS is the entry point.

### 1.15 `claude_research_startup_introspection.md`

- **Title.** Claude Code Startup + Research Execution
  Introspection — S1276 meta-research
- **Purpose.** Evidence base for the OS (§1.14). Documents
  Claude Code's *actual* startup behavior (from S1276 open
  self-observation), grep audits of CLAUDE.md + START-HERE +
  playbook + INDEX showing what fresh Claude cannot discover
  today, and P0/P1/P2 recommendations that seeded the OS
  design.
- **Status.** Active (companion evidence to §1.14).
- **Research type.** Process Introspection / Startup Audit /
  Failure Mode Catalog.
- **Primary questions answered.**
  - What does Claude Code actually do at session open today?
  - What is mandated vs learned vs manual vs prompt-dependent?
  - What is discoverable from CLAUDE.md alone (short answer:
    not much)?
  - What are the recent failure modes (wrong pin, S1273/S1274
    numbering collision, handoff drift, domain ambiguity, RAG
    provenance filter, multi-Claude session risk)?
  - What P0/P1/P2 documentation changes would extinguish each
    failure mode?
- **Dependencies.** `CLAUDE.md`, `00-START-NEXT-SESSION.md`,
  `docs/00-START-HERE/`, `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`,
  `docs/research/ARCHITECTURE_INDEX.md`, MEMORY.md
  auto-loaded feedback rules, `.claude/skills/context-kit/SKILL.md`.
- **Recommended next reads.** Chris directive at S1276 close:
  read Parts 1 + 4 for accuracy verification. The full Part
  6 recommendations became the P0 items in OS §17.1 + §20.9.
- **Overall importance.** **Foundational for understanding
  the OS's design rationale.** Not read at every session
  bootstrap (OS §1.14 replaces it as the operational doc),
  but the evidence base for OS §8 discoverability audit + §20
  fresh-Claude confusion assessment. Chris directive:
  *"you don't need Rigby this should be for how you work with
  the repo"* — the doc introspects Claude's repo-interaction
  discipline, not architectural findings.
- **Distinguishing property.** `authority: process-audit` —
  Claude self-report, not architectural finding. Not routed
  to Rigby per S1276 close directive.

### 1.16 `domains/memory/1301_memory_rag_retrieval_lanes_audit.md`

- **Title.** S1301 Memory RAG Retrieval Lanes — Category D
  Architecture Audit
- **Purpose.** First child audit under Research Group 1300
  Memory (parent §1.13). Scopes exclusively to Category D
  (RAG / Document Retrieval) per parent §3D + §5D + §6.
  Traces the parent §6 provenance-filter finding
  (`search_docs` 8 pre-filter → 7 `excluded_missing_provenance`
  + 1 `excluded_mismatch` → 0 returned) to root cause and
  answers the 28 canonical playbook questions for Category D.
- **Status.** Draft → Active (Rigby SIGN-clean, cycle 1, fresh
  isolation pin `pa-a23736a833f646cf`, 2026-07-01). Chris
  commit-gate flips to active on merge per playbook §16.
- **Research type.** Child audit (playbook §11.2 20-section
  template). `authority: research`.
- **Primary questions answered.**
  - Which lane runs which PA tool? `search_docs` = LOCAL
    keyword (`core.rag.top_k` on `.rag/corpus.jsonl`);
    `kb_tool semantic_search` = PROD pgvector
    (`core.rag_integration.search_embeddings`). Verified at
    `core/services/td_handlers_ops.py:5502`.
  - What drives `excluded_missing_provenance`? External
    `docs/_provenance.json` index (git-history-derived by
    `build_docs_provenance`) with 464 UNKNOWN entries out of
    2156 total (~21.5%); `_filter_chunks_by_originating_session`
    treats "path not in index" as exclusion by design
    (`td_handlers_ops.py:78-127`).
  - Does the prod lane bypass the filter? Yes — the filter
    is local-lane-only. `kb_tool semantic_search` and the
    prod `search_embeddings` path never call
    `_filter_chunks_by_originating_session`.
  - Do the row-level `DocumentEmbedding.source_type` /
    `ingested_via` fields participate in retrieval? No — grep
    receipts: 0 hits in `core/rag_integration.py`,
    `core/rag.py`, `core/services/scoped_retrieval.py`. Two
    provenance systems coexist without a bridge.
  - Is there a two-lane runtime selector? No — never
    implemented. `search_docs` hardcoded to local lane;
    `kb_tool` hardcoded to prod lane.
  - Does PA turn enrichment auto-invoke RAG? No — grep of
    `unified_pa_entrypoint.py` finds zero RAG imports.
    Tool-call-only.
- **Dependencies.** `1300_memory_domain_scoping.md`
  (parent — Categories A–H taxonomy + §6 anchor finding);
  `platform_architecture_inventory.md` §3.13 / §3.14 / §3.15
  / §5.4 (S1273 cited for 13 of 28 canonical questions
  already answered — this audit cites rather than
  re-answers); `cross_domain_integration_audit.md` (S1274
  §2.5 STRONG classification for PA + Agent RAG paths).
- **Recommended next reads.** Once this lands, next Group
  1300 child is S1302 Memory Persistence Architecture
  (Categories A + B + C — this audit surfaces the row-level
  provenance semantics question as a persistence concern
  belonging in S1302). Cross-arc follow-on: Group 1700
  Observability owns filter-drop telemetry per §14.2.
- **Overall importance.** **The audit that made the two-lane
  split visible.** Prior to S1301, tool descriptions
  implied `search_docs` and `kb_tool` were parallel
  implementations; the audit shows they run entirely
  different lanes with entirely different corpus surfaces
  and entirely different provenance semantics.
  Subsystem maturity verdict WORKING (dropped from STABLE
  in the parent scope) captures the corpus-completeness gap
  that neither individual-lane verdict conveys.
- **Distinguishing property.** First child audit of the
  library — validates playbook §11.2 template + §13
  6-parallel-Explore sub-agent sweep. Rigby SIGN independently
  grep-verified 8 numbered load-bearing claims across
  mechanism, filter design, prod-lane bypass, denominator
  quantities, row-level vs external provenance systems,
  MISSING inbound consumers, PA enrichment path, and
  silent-failure surface. All 8 CONFIRMED after SIGN cycle 1
  fold. Verifier-loop history preserved append-only per
  playbook §6.

---

### 1.17 `domains/memory/1302_memory_persistence_architecture_audit.md`

- **Title.** S1302 Memory Persistence Architecture —
  Categories A + B + C Architecture Audit
- **Purpose.** Second child audit under Research Group 1300
  Memory (parent §1.13). Combined scope of Categories A +
  B + C (Semantic Knowledge / Personal-Adaptive / Agent
  Working Memory) per parent §5 P2 slot. Answers the
  persistence-architecture question renamed by Chris
  2026-07-01 from "Store Overlap Audit": *where does what
  memory live, with what durability, on what write/read
  paths, and where is write authority enforced?*
- **Status.** Draft → Active (Rigby SIGN-clean, cycle 3, same
  fresh isolation pin `pa-1b9f0f5264484c6b` across all three
  fold cycles, 2026-07-01). Chris commit-gate flips to active
  on merge per playbook §16.
- **Research type.** Child audit (playbook §11.2 20-section
  template). `authority: research`.
- **Primary questions answered.**
  - Where does what memory live? Cat A `AgentKnowledgeSource`
    (`core/models_unified_system.py:521`) is Postgres-durable
    per-agent; Cat B splits across durable
    `UserAgentLearning` (`:3912`) + durable pgvector
    `ConversationMemory` (`core/models/conversations/models.py:19`)
    + Redis-only per-user preferences (`AgentLearningService`
    at `core/services/agent_learning_service.py:122`); Cat C
    `AgentMemory` (`:10787`) is Postgres-durable per-agent,
    with Redis-cached embedding side.
  - What's the write authority model? Unrestricted at the
    model layer for all three categories. Per-user isolation
    for Cat B is schema-only (FK), not query-time enforced.
    Cat C `AgentMemory.create_memory` at :11004 has no user
    FK, no rate limiting, no gate — `MemoryPromotionService`
    auto-saves on every PA turn. T10 HIGH severity.
  - Does the row-level "orphan write path" pattern from
    S1301 §14.3 D3 recur? Yes, but narrower than v1 claimed
    (Rigby SIGN cycles 1 + 2 + 3 grep-tightened). Final
    classification: 5 strict-orphan fields
    (`AgentKnowledgeSource.feedback_positive` +
    `.feedback_negative`; `UserAgentLearning.context_metadata`
    + `.last_used`; `ConversationMemory.intent` Django model)
    + 2 narrow-consumer-safety-filter fields
    (`AgentMemory.poison_risk_score` +
    `.poison_risk_factors` — consumed for safety exclusion
    only at `core/services/memory_embedding_service.py:222,
    :261`). 7 total under F2 pattern, down from v1's ~11.
  - Is `spider_context['pa_content_feedback']` consumer
    UNKNOWN as parent §3 flagged? **No — it is CONFIRMED DEAD
    CODE.** Whole-tree grep across `core/` + `ai_core/`: 1
    producer at `core/agent_router.py:766`; 0 code
    consumers. F1 headline finding.
  - Is the 14-day freshness window a magic number? Yes —
    `core/conversation_orchestrator.py:749` verbatim
    `freshness_cutoff = tz.now() - timedelta(days=14)`;
    hardcoded, no env var / setting; Session 988 origin per
    :747-748 comment.
  - Is `AgentLearningService` Redis state recoverable on
    worker recycle? No — `save_memory` at
    `core/services/agent_learning_service.py:462-483` writes
    `redis_client.hset` at :476 with no DB backup; grep for
    `.expire()`/`.setex()` = 0 hits.
  - Does `spider_data_bridge` write Cat A (naming implies)
    or Cat B (code reveals)? **Cat B.** Bridge at
    `core/learning_bridges/spider_data_bridge.py:240` calls
    `UserAgentLearning.objects.get_or_create(...)`. F5
    docs_stale.
  - Does `MemoryPromotionService` write `AgentMemory` (Cat C
    per parent §3) or `UserMemoryContext` (user-scoped)?
    **UserMemoryContext.** `core/services/memory_promotion_service.py:303-318`
    calls `UserMemoryContext.objects.create(...)`. F6
    category-assignment drift.
- **Dependencies.** `1300_memory_domain_scoping.md` (parent —
  Categories A–H taxonomy + parent §3 known-drift bullets);
  `1301_memory_rag_retrieval_lanes_audit.md` (sibling Cat D
  audit — S1301 §14.3 D3 row-level orphan-write pattern
  inherited as first-order S1302 scope; §17.1 + §17.2 cited
  as authoritative resolutions, not re-answered);
  `platform_architecture_inventory.md` §3.13 + §5.4 (S1273
  overlap flag that motivated Group 1300);
  `cross_domain_integration_audit.md` (S1274 integration
  lens).
- **Recommended next reads.** Once this lands, next Group
  1300 child is S1303 Conversational / Thread Memory (Cat F)
  — will own the `ConversationSession` ↔ `ConversationMemory`
  boundary that S1302 documents as adjacent surface. S1304
  Docs Corpus ↔ RAG Boundary (E ↔ D) follows. Cross-arc
  follow-on: Group 1700 Observability owns dead-code /
  producer-only detection (F1 is highest-severity example);
  future design-preparation ADR (post-S1399) proposes the
  write-authority framework §18 surfaces but does not
  implement.
- **Overall importance.** **The audit that made the
  write-authority gap visible + escalated the pa_content_feedback
  loop from UNKNOWN to dead code.** The persistence-architecture
  rename by Chris 2026-07-01 made §18 (Ownership Gaps —
  authority framework) the audit's headline lens; every
  category has unrestricted model-layer writes, and Cat C
  auto-saves on every PA turn without rate limiting. Combined
  with F1's confirmed producer-only feedback loop and F2's
  narrower-but-real orphan-write pattern, the audit
  establishes that the Memory subsystem's biggest architectural
  risk is not overlap surfacing — it is the absence of a write
  authority framework.
- **Distinguishing property.** **Second child audit of the
  library; validates the fold discipline across THREE Rigby
  SIGN cycles on the same fresh isolation pin.** Cycle 1 folded
  F2 overstatement + verified F6 by parent-agent direct-read;
  cycle 2 folded AgentMemory field misclassification via
  Memory Palace consumer evidence + methodology tightening
  ("no explicit-qualified references found" replaces
  "0 consumers"); cycle 3 folded final poison_risk_*
  reclassification to narrow-consumer-safety-filter. Verifier-loop
  history preserved append-only per playbook §6. Total
  F2 orphan field count: ~11 (v1) → ~9 (cycle 1) → ~6 (cycle
  2) → 5 strict + 2 narrow-consumer (cycle 3 final). Pattern
  class stands; scope is significantly narrower than v1
  claimed. Overall confidence: High.

---

### 1.18 `domains/memory/1303_memory_conversational_thread_memory_audit.md`

- **Title.** S1303 Memory Conversational / Thread Memory —
  Category F Architecture Audit
- **Purpose.** Third child audit under Research Group 1300
  Memory (parent §1.13). Category F Conversational / Thread
  Memory exclusive scope per parent §5 P3 slot.
  **First-inventory landing** — Cat F had no
  `platform_architecture_inventory.md` §3.N row at audit open;
  this audit produces the terrain (§4 Major Models + §7
  Runtime Flows load-bearing sections). Answers: where does
  session pin identity live, how does turn history reinject
  across worker recycling, what is the retire lifecycle
  contract, and where does Cat F touch the 12 adjacent
  domains?
- **Status.** Draft → Active (Rigby SIGN-clean, cycles 1 + 2
  complete on fresh isolation pin `pa-23a38300dd84bae2`,
  2026-07-01). Chris commit-gate flips to active on merge per
  playbook §16.
- **Research type.** Child audit (playbook §11.2 20-section
  template). `authority: research`.
- **Primary questions answered.**
  - Where does session pin identity live? `ChatConversation`
    at `core/models/conversations/models.py:59-187` is the
    row-per-exchange table; `conversation_id` CharField (line
    76) stores the `pa-<uuid.hex[:16]>` pin (mint format at
    `td_handlers_core.py:3885`); `session_active` BooleanField
    (line 139-143) is the retire marker.
  - How does turn history reinject across Celery worker
    recycles? `_load_conversation_history_from_db()` at
    `unified_pa_entrypoint.py:7277-7343` loads the last 10
    ChatConversation rows scoped to `conversation_id`
    (7300-7302), chronologically ordered (7309), with 8000-
    char assistant-response truncation (7327, post-S1085
    bump), tool-call metadata (`tool_calls` / `tool_results`
    / `response_id`) reinjected at 7331-7336, fail-open on DB
    error at 7342.
  - Is `session_tool.retire` present + working? **YES.**
    Handler at `td_handlers_core.py:4011-4072`; requires
    `force=True` if retiring currently-bound thread (line
    4035-4050); returns `{retired: True, updated_count}` on
    success (line 4061); idempotent (`.filter(session_active=
    True).update(...)` returns 0 rows on double-retire).
    Memory rule `feedback_session_tool_retire_works.md`
    stands.
  - Was the S1212 stale-thread dispatcher waste (deliverable
    777d9cd8, ~$3.60/day) reconciled? **YES.** S1248 shipped
    matched-pair fix: retire handler flips `session_active=
    False`; dispatcher gate at `conversation_action_
    dispatcher.py:288-316` blocks. Enforcement is best-effort
    / fail-open under DB errors (line 317-323 `try/except`
    envelope) — availability > correctness by design.
  - Where is the Cat B / Cat F name-collision boundary
    (S1302 §17.3)? Django `ConversationMemory` at
    `models/conversations/models.py:19` = Cat B (S1302-
    owned); in-process `ConversationMemory` facade at
    `conversation_memory.py:59` = Cat F. Consumer imports
    split cleanly by pattern A (Cat B model) vs B (Cat F
    facade singleton). One WRONG import at
    `content_writer_agent.py:76` — see F3 below.
  - Are `ChatConversation.context_used` +
    `.agent_results` dead code? **CANDIDATE, NOT YET PROVEN
    EITHER WAY.** Rigby SIGN cycle 1 confirmed the raw-
    keyword grep catches unrelated variables (e.g.,
    `tasks_agents.py:1262` `agent_results = phase_data.get(
    'results', {})` is a local dict in different scope). Per
    memory rule `feedback_verify_before_deleting_dead_code.md`,
    dead-code verdict requires owner-model-qualified consumer
    inventory (§19 R1.a) + runtime/analytics/UI classification
    (R1.b) + canonical source-of-truth resolution vs the
    `metadata` dict (R1.c) BEFORE any deletion PR.
  - Does turn context enrich RAG queries? **Observed gap;
    owner confirmation required.** No verified wiring found
    from Cat F turn-history reinjection to Cat D retrieval
    query augmentation (0 RAG imports in
    `unified_pa_entrypoint.py`). Could be intentional
    separation (thread memory user-scoped; corpus source-
    scoped) or missing integration. §19 R3 delegates to S1304
    (Cat E ↔ D boundary).
  - What auto-cleanup exists for retired rows? **NONE.** No
    Celery task, no management command, no TTL config found
    for `ChatConversation` cleanup. Retired rows accumulate
    indefinitely. §14 F9 + §19 R4.
- **Dependencies.** `1300_memory_domain_scoping.md` (parent
  — Cat F systems named in §3F; parent §5 P3 rationale locks
  first-inventory discipline);
  `1301_memory_rag_retrieval_lanes_audit.md` (sibling Cat D
  — silent-failure class pattern adjacent to F7 EventBus
  gap; §19 downstream routing points at S1304 E↔D);
  `1302_memory_persistence_architecture_audit.md` (sibling
  Cat A+B+C — §17.3 name-collision resolution is
  load-bearing input; §14.3 F1 dead-code detection
  methodology applied as F4-CANDIDATE, not F4-CONFIRMED, per
  verifier discipline); `platform_architecture_inventory.md`
  (S1273 — Cat F has NO §3.N row today; audit produces the
  candidate row for S1399 canonical summary landing);
  `cross_domain_integration_audit.md` (S1274 integration
  lens; 12 Cat F domain pairs mapped).
- **Recommended next reads.** Once this lands, next Group
  1300 child is S1304 Documentation Corpus ↔ RAG Boundary
  (Categories E ↔ D) — inherits provenance-boundary
  questions from S1301 + S1302 and receives §19 R3 (turn-
  context → RAG enrichment design). S1305 Runtime Memory
  Correctness (Cat H narrow scope — Redis-loss + lru
  staleness) follows. S1399 canonical summary owns first-
  inventory row landing for Cat F (§19 R5).
- **Overall importance.** **The audit that documented the
  Cat F terrain for the first time + reconciled the stale-
  thread waste anchor + surfaced F4-CANDIDATE discipline as
  a repeatable methodology guard.** ConversationSession +
  turn-history reinject + retire lifecycle now have file:line
  cites and step-by-step runtime flows for the first time in
  the library. F3 wrong-model+wrong-field finding at
  `content_writer_agent.py:370` (Django `ConversationMemory`
  has no `memory_type` field) is a live drift class not
  previously named. F4-CANDIDATE discipline (verifier
  downgrade from Agent-6's "dead code" claim to "not yet
  proven either way") extends S1302's dead-code methodology
  by adding the owner-model qualification rule — future
  audits that apply this pattern must not accept keyword-
  grep evidence for dead-code claims.
- **Distinguishing property.** **First-inventory audit in
  the library** — no prior §3.N row existed for Cat F;
  §4 Major Models + §7 Runtime Flows are load-bearing (not
  just referential). Also: **only child audit to reach SIGN-
  clean in 2 cycles** (S1301 = 1 cycle, S1302 = 3 cycles) —
  verifier-loop spot-checks caught Agent-6's two overreaches
  (F3 "would fail at import time" → SOFT FAIL soft-guarded;
  F4 "confirmed dead code" → CANDIDATE) before shipping to
  Rigby, so cycle 1 only needed to fold the substantive
  edges (metadata contract, D1 widen, Cat F ↔ Cat D
  reframe, maturity bounding, R1 split into R1.a/b/c) rather
  than correct evidence overreach. Cycle 2 was a pure
  verification pass; Rigby confirmed E3/E4/E5 held via
  direct code reads and closed SIGN-clean. Verifier-loop
  history preserved append-only per playbook §6.

---

### 1.19 `domains/memory/1304_memory_docs_rag_boundary_audit.md`

- **Title.** S1304 Memory Documentation Corpus ↔ RAG Boundary
  — Categories E ↔ D Integration Audit
- **Purpose.** Fourth child audit under Research Group 1300
  Memory (parent §1.13). Categories E (Documentation / Research
  Knowledge System — S1273 §3.15) ↔ D (RAG / Document Loading —
  S1273 §3.14 + S1301 P1 audit) exclusive **boundary lens** per
  parent §5 P4 slot. Smaller scope than P1-P3 per parent
  rationale ("smaller scope; benefits from §3.14 audit landing
  first"). Answers: how does docs corpus become RAG-visible,
  where does ingestion hand off to retrieval, where do the two
  provenance systems (external `_provenance.json` vs row-level
  `DocumentEmbedding.source_type` + `ingested_via`) disagree,
  and what routes read which?
- **Status.** Draft → Active (Rigby SIGN-clean, cycles 1 + 2
  complete on fresh isolation pin `pa-2614a91a920642fa`,
  2026-07-01). Chris commit-gate flips to active on merge per
  playbook §16.
- **Research type.** Child audit (playbook §11.2 20-section
  template). `authority: research`.
- **Primary questions answered.**
  - Is S1301 §19 D3 "row-level provenance never read"
    hypothesis correct? **PARTIALLY INVALIDATED via S1304
    verifier-loop.** `DocumentEmbedding.source_type` HAS an
    owner-model-qualified consumer at
    `content/embeddings.py:965-973` (`semantic_search_sync`
    applies `.filter(source_type__in=['internal',
    'user_upload'])` at :971 and
    `.filter(source_type__in=['web', 'spider', 'api'])` at
    :973 as `source_filter` branch) + presentation at :1007
    (`getattr(embedding, 'source_type', 'unknown')`). Only
    `ingested_via` remains F1-CANDIDATE orphan — all 3
    write-sites use fixed string constants
    (`'sync_docs'` / `'backfill'` / `'unknown'`) with zero
    owner-model-qualified read consumers. F1-CANDIDATE
    verdict per S1303 §14 F4-CANDIDATE discipline (requires
    §19 R1 full-tree recheck before dead-code declaration).
  - Is `build_docs_provenance` beat-scheduled? **NO.** The
    sole `refresh-docs-corpus-daily` beat entry at
    `core/celery.py:495-499` runs `refresh_docs_corpus`
    daily at 04:00 Denver, which calls
    `build_docs_index` (`:5900`), `build_rag_corpus`
    (`:5901`), and `sync_docs_index_to_documents` (`:5902`)
    — but never `build_docs_provenance`. Provenance index
    rebuild is manual-only. Combined with the `lru_cache(1)`
    invalidation gap at `td_handlers_ops.py:78-93`, this is
    the canonical E→D write-side/read-side sync drift
    (§14 D2 + D6, both HIGH severity).
  - Who owns the E↔D boundary? **Cascade steps 1-4 owned by
    Documentation Manager `AIEmployee` handle at
    `core/employees/jobs.py:187-395` (registered `:1336` as
    `docs_manager`, employee_handle=`rigby`, `mission_run_
    kind="docs_cascade"`).** The four specific boundary-
    maintenance responsibilities (provenance rebuild
    cadence, cache invalidation strategy, filter counter
    observability, row-level `ingested_via` consumer
    strategy) have **no explicit named runtime owner** —
    Cat D + Cat E have implicit maintainers, but no
    `JobContract` binds boundary-maintenance
    responsibilities. Bounded language per playbook §12:
    "no explicit named runtime ownership" replaces the
    initial "UNOWNED" blanket verdict (fold #2 per Rigby
    SIGN cycle 1).
  - Is turn-context → RAG enrichment intentional separation
    or drift (S1303 §19 R3)? **NOT RESOLVABLE FROM STATIC
    EVIDENCE.** Three signals tilt intentional-separation
    (design discipline in 8 non-RAG enrichment services,
    tool-call-only pattern with two first-class PA tools,
    thread-memory vs source-memory scope discipline,
    no event-driven turn-signal wiring), three signals
    tilt drift (no design comment, no feature flag guarding
    absence, asymmetry with BaseAgent's
    `_get_relevant_knowledge_for_task`). Routed to §19 R5
    as design-decision hypothesis for
    design-preparation phase, NOT drift or wiring PR. R5.a
    (canonicalize separation) vs R5.b (implement enrichment)
    require product/architecture verdict on operational
    cost, migration risk, and future retrieval requirements.
  - Are the two provenance systems duplicates? **No —
    complementary, not redundant** (applied S1302 §17.3
    name-collision-as-methodology). External JSON encodes
    session origin (LOCAL keyword lane); row-level
    `source_type` encodes source-of-record enum (PROD
    pgvector lane); `ingested_via` was over-designed for a
    retrieval consumer that never materialized. Fold #4 per
    Rigby SIGN cycle 1: "complementary today does not imply
    optimal" guardrail added — unification vs explicit
    scoping is an open design decision routed to §19 R2.
- **Dependencies.** `1300_memory_domain_scoping.md` (parent
  — Cat E + Cat D systems named in §3E + §3D; parent §5 P4
  rationale locks boundary-lens discipline);
  `1301_memory_rag_retrieval_lanes_audit.md` (sibling Cat D
  — §14.2 21.5% coverage gap + §19 downstream routing
  including row-level orphan-write pattern that S1304
  partially invalidates);
  `1302_memory_persistence_architecture_audit.md` (sibling
  Cat A+B+C — §17.3 name-collision resolution methodology
  applied to the two-provenance-system reframe);
  `1303_memory_conversational_thread_memory_audit.md`
  (sibling Cat F — §9 Cat F ↔ Cat D OBSERVED GAP + §19 R3
  turn-context → RAG enrichment hypothesis + §14
  F4-CANDIDATE discipline enforced on
  `ingested_via` orphan claim);
  `platform_architecture_inventory.md` (S1273 §3.14 + §3.15
  + §5.4 overlap flag); `cross_domain_integration_audit.md`
  (S1274 §2.5 baseline for §9 comparison);
  `DOC_LIFECYCLE.md` (§2c inventory-wins-on-conflict rule
  as governance authority for the boundary);
  `docs/topics/local-askdocs.md` (S1108 CANONICAL boundary-
  disambiguating topic doc); `SESSION_1142` handoff
  (ingestion-moment snapshot 852 → 14,149 chunks).
- **Recommended next reads.** Once this lands, next Group
  1300 child is **S1305 Runtime Memory Correctness (Cat H
  narrow scope — Redis-loss + lru staleness)** per parent
  §5 P5 slot. Then S1399 canonical summary — owns first-
  inventory row landing for Cat F (§19 R5 inherited from
  S1303) + row-level orphan-write pattern classification
  (§19 R1 F1-CANDIDATE verification of `ingested_via`) +
  write-authority framework anchor recommendation
  (inherited from S1302 T10) + provenance-system
  reconciliation design proposal (§19 R2) + boundary-owner
  assignment (§19 R4). Follow-on delegations: R5 turn-
  context → RAG enrichment design → design-preparation
  phase post-S1399; R7 filter-drop telemetry → Group 1700
  Observability arc.
- **Overall importance.** **The audit that mapped the E↔D
  boundary integration for the first time + partially
  invalidated S1301 §19 D3 hypothesis via verifier-loop
  before it propagated to sibling audits + refined "boundary
  UNOWNED" to bounded ownership matrix + routed Cat F ↔ Cat
  D turn-context enrichment to design-decision phase.** The
  4-step ingestion cascade, provenance materialization,
  retrieval-side `lru_cache(1)` staleness gap, and
  boundary-maintenance ownership gaps now have file:line
  cites and mechanism-level explanations for the first time
  in the library. S1301 §19 D3 partial-invalidation
  demonstrates the verifier-loop pattern preventing sibling-
  audit hypothesis propagation before it hardens into
  library-wide false consensus.
- **Distinguishing property.** **First boundary-lens audit
  in the library** — scope is deliberately smaller than
  P1-P3 per parent §5 P4 rationale; audit is integration-
  focused, not re-audit of either category internals. Also:
  **only second child audit to reach SIGN-clean in 2 cycles**
  (S1301 = 1 cycle, S1302 = 3 cycles, S1303 = 2 cycles,
  S1304 = 2 cycles) — verifier-loop spot-checks caught the
  S1301 §19 D3 broad hypothesis invalidation before shipping
  to Rigby, so cycle 1 focused on substantive evidence
  additions (beat-schedule positive citation for D6,
  Documentation Manager ownership evidence for §18,
  F4-CANDIDATE hedge tightening for `ingested_via`,
  "complementary does not imply optimal" guardrail for
  §17). Cycle 2 was a pure verification pass; Rigby
  confirmed all 4 folds independently via direct code reads
  and closed SIGN-clean. Rigby-caught bonus at
  `content/embeddings.py:904` (async-path SearchResult
  presentation citation) flagged as nice-to-have, not
  SIGN-blocking. Verifier-loop history preserved
  append-only per playbook §6.

### 1.20 `domains/memory/1305_memory_runtime_correctness_audit.md`

- **Title.** S1305 Memory — Runtime Memory Correctness
  (Category H) Architecture Audit
- **Purpose.** **Fifth (and final child) audit under Research
  Group 1300 Memory (parent §1.13).** Category H Runtime Memory
  Correctness NARROW scope per parent §5 P5 slot — Redis-loss on
  worker recycle + `@lru_cache(1)` staleness drift class only.
  Explicitly OUT: system RAM, macOS SIGSEGV, Celery worker RSS,
  PID cache, ops-flavored infrastructure. Explicitly OUT: Cat A/
  B/C/D/E/F/G internals (owned by sibling audits — MAY be cited
  as adjacent evidence but NOT re-audited). Answers: where does
  the runtime model assume persistence that Redis / `@lru_cache`
  doesn't guarantee, and where does staleness silently ship
  wrong results?
- **Status.** Draft → Active (Rigby SIGN-clean, cycles 1 + 2
  complete on fresh isolation pin `pa-56a527a2c5528508` retired
  at close, 2026-07-01). Chris commit-gate flips to active on
  merge per playbook §16.
- **Research type.** Child audit (playbook §11.2 20-section
  template). `authority: research`.
- **Primary questions answered.**
  - How many `@lru_cache(maxsize=1)` sites in `core/services/`?
    **Exactly 4** grep-verified 2026-07-01: `_load_provenance_docs`
    at `td_handlers_ops.py:78` (S1304 D2 anchor);
    `_cached_primary_workspace_id` at `platform_config.py:89`;
    `_cached_primary_user_id` at `platform_config.py:133`;
    `_load_config` at `fleet_routing.py:64`. Only
    `platform_config` pair has an explicit invalidation contract
    (`clear_config_cache()` at :223); the other two rely on
    worker-restart discipline.
  - How many production `cache.set(..., timeout=None)` sites?
    **5** within scope after Rigby SIGN cycle 1 tightening
    (`core/` runtime excl. tests + subprocess-timeouts + archive
    + mock fallbacks): `core/tasks.py:5936`, `core/memory_system.py:54`,
    `:55`, `:176`, `core/services/discord_bot.py:9723,9728`.
    Full 11-file repo grep enumerated with 6 excluded-category
    justifications at §3 excluded-from-count table.
  - Is `AgentLearningService` durability actually CRITICAL as
    Agent 6 sweep claimed? **No — verifier-loop downgraded to
    MEDIUM.** Redis AOF at `settings.py:944 REDIS_APPENDONLY=True`
    + `REDIS_APPENDFSYNC='everysec'` at :945 preserves state
    across Redis restart; loss on Python-worker recycle is only
    the in-memory `_user_memories` buffer delta between last
    `save_memory()` and recycle, matching S1302 T3 sibling
    classification.
  - What is the within-process consistency gap in
    `AgentLearningService`? **CONFIRMED via direct file:line read
    + Rigby SIGN cycle 1 reinforcement.** `get_user_memory` at
    `agent_learning_service.py:415` short-circuits to
    `_user_memories[key]` BEFORE Redis on hit; `save_memory` at
    `:476` writes Redis via `hset` but never touches the dict.
    Grep across full file for `self._user_memories.clear` /
    `del self._user_memories` = 0 hits. Distinct from S1302 T3
    (cross-process recycle-loss). §14 D4 S1305-new.
  - Is `MemoryPromotionService` a Cat H surface? **NO** — Agent 2
    + verifier-loop confirmed pure DB I/O; no `@lru_cache`,
    `@cached_property`, or module-level memoization. Closes
    parent §3H open question.
  - Is `MemorySystem` at `core/memory_system.py` actively used?
    **YES** — Rigby SIGN cycle 1 grep found 9 files reference
    `MemorySystem(` or the `SharedMemorySystem` / `AIMemorySystem`
    cousins; direct instantiation confirmed at
    `ai_core/agents/intelligent_job_matcher.py:57`. §14 D5:
    unbounded `timeout=None` at `:54, :55, :176` creates index
    → data divergence risk under Redis LRU eviction
    (`REDIS_MAXMEMORY_POLICY='allkeys-lru'` at `settings.py:942`).
  - Is the Redis DB topology what documentation claims? **NO —
    4 DBs, not 3** as `docs/topics/infrastructure.md` says.
    Confirmed: DB 1 (Django cache `settings.py:448-453`), DB 2
    (Celery broker `:802`), DB 3 (Celery results `:803`), DB 5
    (`AgentLearningService` hardcoded at
    `agent_learning_service.py:145`). **Consequence:**
    `django.core.cache.cache.clear()` operates on backend at DB 1
    only; `AgentLearningService` uses raw `redis.Redis(**config)`
    at `:160` bypassing Django cache framework — DB 5 state is
    invisible to `cache.clear()`. §14 D8 + D9.
- **Dependencies.** `1300_memory_domain_scoping.md` (parent —
  §3H narrow scope defined + §5 P5 slot rationale + §7 anti-scope
  boundary); `1301_memory_rag_retrieval_lanes_audit.md` (sibling
  Cat D — §14 D1/D2 LRU staleness anchor);
  `1302_memory_persistence_architecture_audit.md` (sibling Cat A+B+C
  — §14 F4/F5 + §15 T3/T4 Redis-only durability anchor + AOF
  context); `1303_memory_conversational_thread_memory_audit.md`
  (sibling Cat F — §14 F4-CANDIDATE discipline applied to
  `platform_config` LRU F4-CANDIDATE claim);
  `1304_memory_docs_rag_boundary_audit.md` (sibling Cat E↔D —
  §14 D2/D6 canonical E→D synchronization gap + §15 T2 remediation
  option set inheritance + §18 ownership gap pattern extension);
  `platform_architecture_inventory.md` (S1273 §3.13 drift bullets
  reference Redis-only state + `lru_cache(1)` per-process).
- **Recommended next reads.** Group 1300 has now closed all 5
  child audits; **next is S1399 Canonical Summary** per parent
  §5 P6 slot. S1399 consumes S1301-S1305 outputs and produces:
  (a) consolidated memory-subsystem shape map across all 6 in-
  scope categories (A/B/C/D/E/F; G delegated), (b) cross-cutting
  patterns discovered across children (F1 provenance-filter drift
  class, F2 row-level orphan-write pattern, F3 Redis-only
  durability + `@lru_cache` staleness pattern, F4 F1-CANDIDATE
  discipline as methodology), (c) `PLATFORM_INVENTORY.md` §3
  update recommendations (§3.13 subdivision from S1302; §3.14 lane
  consolidation from S1301; new §3.N row for Cat F from S1303; new
  §3.N or §5 row for Cat H from S1305), (d) follow-on research
  queue (S1305 §19 R1 IntelligentJobMatcher production invocation;
  S1304 §19 R1 `ingested_via` full-tree recheck; S1303 §19 R1.a/b/c
  F4-CANDIDATE verification; S1302 T10 write-authority framework
  design), (e) cross-link to Employee OS 1200s Cat G Mission Memory
  arc. S1399 is bounded work (one session per playbook §11.3).
- **Overall importance.** **The audit that mapped the Cat H
  runtime-cache tier for the first time + established sibling-
  inherited severity discipline (Redis AOF context downgraded a
  CRITICAL claim to MEDIUM) + resolved 3 parent §3H open questions
  (search_docs cache location, MemoryPromotionService cache absence,
  MemorySystem active-use status).** 4 `@lru_cache` sites, 5
  production `cache.set(timeout=None)` sites, 4-DB Redis topology,
  Django cache framework vs raw redis client isolation, within-
  process consistency gap in AgentLearningService — all now have
  file:line cites and mechanism-level explanations. Second-in-a-
  row 2-cycle SIGN-clean pattern (matching S1303 + S1304
  discipline) reflects the audit landing with well-scoped
  verifier-loop pre-corrections + sibling-inheritance that let
  cycle 1 focus on substantive-scope edits rather than factual
  corrections.
- **Distinguishing property.** **Last child audit under Group
  1300; closes the 5-child arc** (S1301 Cat D + S1302 Cat A+B+C
  + S1303 Cat F + S1304 Cat E↔D + S1305 Cat H). Third child audit
  to reach SIGN-clean in 2 cycles (matching S1303 + S1304; S1301
  = 1, S1302 = 3). Also **first library audit to explicitly
  downgrade a sub-agent severity claim via sibling-inherited
  context** (Agent 6 "CRITICAL" → MEDIUM per Redis AOF at
  `settings.py:944`) — extends the verifier-loop pattern from
  hypothesis-correction (S1304 partial invalidation of S1301
  §19 D3) to severity-correction (§14 D3 downgrade). Rigby-caught
  bonus at MemorySystem active-use resolution shifted §19 R6
  from "verify MemorySystem is used" to "verify
  IntelligentJobMatcher is production-invoked" — same effort
  budget, higher-leverage question. Verifier-loop history
  preserved append-only per playbook §6.

---

### 1.21 `domains/memory/1399_memory_canonical_summary.md`

- **Title.** Group 1300 Memory / Knowledge / Embeddings —
  Canonical Summary
- **Purpose.** **Arc-closing `xx99` synthesis for Research Group
  1300** (Memory / Knowledge / Embeddings). Consumes the five
  child audit outputs (S1301 Cat D + S1302 Cat A+B+C + S1303 Cat
  F + S1304 Cat E↔D + S1305 Cat H) and produces the cross-
  cutting view that no single child could deliver: consolidated
  memory-subsystem shape map spanning Cat A/B/C/D/E/F (G
  delegated per parent §3G), recurring pattern classes named
  (F1-F4), resolved contradictions between siblings, anchor-
  update recommendations, ranked follow-on queue, and cross-
  links to delegated arcs.
- **Status.** Draft → Active (Rigby SIGN-clean cycle 1 on fresh
  isolation pin `pa-4fc3329d0db6484f`, High confidence, 0 must-
  fix, 1 optional nice-to-have re: docs↔code naming/category
  drift kept as §4.5 adjacent evidence). Chris commit-gate flips
  status → active on merge per playbook §16.
- **Research type.** Canonical summary (playbook §11.3 11-section
  template). `authority: research`, `category: canonical_summary`.
- **Primary questions answered.**
  - What are the cross-cutting patterns across all 5 child
    audits? **Four formal patterns named:** F1 provenance-
    filter drift class (S1301 §14.2 + S1304 §14 D2/D6 + S1305
    §14 D1); F2 row-level orphan-write pattern (S1301 §14.3 D3
    hypothesis + S1302 §14.3 F2 narrowed 11→7 fields + S1304
    §14 D3 partial invalidation); F3 Redis-only durability +
    `@lru_cache` staleness pattern (S1302 §14 F4 + §15 T3/T4 +
    S1304 §14 D2 + S1305 §14 D3/D4/D5/D8); F4 F1/F4-CANDIDATE
    discipline as inheritance methodology (S1303 §14 + S1304
    §14 D7 + S1305 §14 D6 + severity-correction extension at
    S1305 §14 D3). §4.5 adjacent-evidence addendum on docs↔code
    naming/category drift.
  - What contradictions between children required resolution?
    **Five resolved (§5):** (5.1) S1304 §14 D3 partial-invalidates
    S1301 §19 D3 broad `source_type` orphan hypothesis; (5.2)
    S1304 §17 "complementary" reframe of S1302 §17.3 "duplicate
    provenance systems"; (5.3) Agent 6 CRITICAL → MEDIUM
    severity downgrade via Redis AOF sibling context; (5.4)
    Agent 6 "13 cache.set(timeout=None)" → 5 production
    scope-tightened; (5.5) parent §3H bullet "search_docs LRU"
    → precision fix (cache is on `_load_provenance_docs`).
  - What anchor-update recommendations does the arc propose?
    **§7:** (a) `platform_architecture_inventory.md` §3.13
    subdivision into Cat A/B/C sub-rows (S1302); (b) §3.14 lane
    consolidation as explicit two-lane statement (S1301); (c)
    new §3.N row for Cat F Conversational/Thread Memory (S1303
    first-inventory landing); (d) new §3.N or §5.N row for Cat H
    Runtime Memory Correctness (S1305 first-inventory landing);
    (e) `docs/topics/infrastructure.md` Redis DB count 3 → 4
    (S1305 §14 D9); (f) `KNOWLEDGE_RAG_MEMORY.md` — resolve F1
    UNKNOWN + two-lane split explicit + LRU precision + pointer
    to this summary; (g) `ARCHITECTURE_INDEX.md` v17 → v18;
    (h) `docs/topics/docs-ingestion-cascade.md` NEW (S1304 §19
    R6). No direct edits to `PLATFORM_INVENTORY.md`
    (regenerable runtime anchor).
  - What's on the follow-on queue and how is it ranked? **21
    items ranked by uncertainty × risk × unblocked flows (§8.1).**
    Top 5: (1) S1304 §19 R1 `ingested_via` full-tree recheck
    (F1-CANDIDATE hardening); (2) S1303 §19 R1.a/b/c
    `ChatConversation.context_used` + `.agent_results`
    verification; (3) S1305 §19 R1 `platform_config` LRU
    F4-CANDIDATE mutation-path audit; (4) S1305 §19 R6
    `IntelligentJobMatcher` production invocation audit
    (routes T5 MemorySystem severity); (5) S1302 §15 T10
    write-authority framework design-preparation ADR (highest-
    severity debt in arc). Design-preparation items post-S1399:
    Cat H remediation per surface (S1305 §19 R2); Cat H ↔ Cat B
    integration lens (S1305 §19 R4 — fixes T3+T4+T7 together);
    provenance-system reconciliation (S1304 §19 R2); turn-context
    → RAG enrichment (S1304 §19 R5).
  - What delegated arcs receive handoffs? **§9:** Employee OS
    1200s arc (Cat G Mission Memory — parent §3G Chris-locked
    D2); Group 1700 Observability (4 aggregated items: Cat D
    filter-drop telemetry from S1301 R2, Cat E↔D filter-drop
    telemetry from S1304 R7, dead-code / producer-only detection
    from S1302, EventBus adoption for Cat F from S1303 R2,
    worker-recycle instrumentation for Cat H from S1305 R5);
    post-S1399 design-preparation phase (4 ADR/design-preparation
    docs); standalone bugfix follow-ups (S1303 R8 broken import,
    S1305 R8 doc-drift, S1304 R8 classifier bug).
- **Dependencies.**
  `1300_memory_domain_scoping.md` (parent — §5 P6 slot rationale
  + §3H open questions closed at S1305 close);
  `1301_memory_rag_retrieval_lanes_audit.md` (child P1);
  `1302_memory_persistence_architecture_audit.md` (child P2);
  `1303_memory_conversational_thread_memory_audit.md` (child P3);
  `1304_memory_docs_rag_boundary_audit.md` (child P4);
  `1305_memory_runtime_correctness_audit.md` (child P5). Also
  cross-links to `EMPLOYEE_OS_PRIMITIVES.md` (Cat G delegation
  target) and prospective Group 1700 Observability arc (multiple
  observability-flavored delegations).
- **Recommended next reads.** **Group 1300 is now closed** per
  playbook §17 graduation criteria. Next arc opens per
  `OPEN_ARCS.md` — default is **Group 1400 Revenue** (next in
  playbook §22 queue), pending Chris directive. Immediate P1
  follow-on missions (§8.2 of the summary) are eligible to open
  as single-child audits or new arcs; write-authority framework
  ADR (Rank 5) is design-preparation phase work post-arc-close.
- **Overall importance.** **The arc-closing xx99 that makes the
  entire Group 1300 arc navigable as a single memory-
  architecture picture.** Six sessions of research (S1300 parent
  + 5 children + this summary) collapse into: (a) a single Cat
  A-H matrix map any Staff Engineer can build a mental model
  from (§3); (b) four named cross-cutting pattern classes that
  now exist as vocabulary for future audits (F1-F4); (c) five
  resolved contradictions preventing sibling-audit hypothesis
  propagation into false library consensus; (d) 21 ranked
  follow-on items feeding future sessions; (e) 4 aggregated
  Group 1700 Observability delegations reducing that future
  arc's scoping cost. **First library `authority: research` +
  `category: canonical_summary` doc that follows playbook §11.3
  bounded-work discipline end-to-end.**
- **Distinguishing property.** **First formal xx99 canonical
  summary in the library** (the S1268-S1275 arc predated the
  xx99 convention per playbook §22 note). Consumes prior child
  outputs — no §13 6-parallel-Explore sweep, no new file:line
  evidence, no CANDIDATE → CONFIRMED resolutions. Every claim
  cites its source-audit §-anchor via `SNNNN §NN.N` notation.
  Rigby SIGN cycle 1 clean at High confidence — the audit
  contract's canonical-summary form works end-to-end. Chris's
  short command `start research group 1399` proved the reduced-
  prompt target rhythm from playbook §11 works for arc closure.
  Load-bearing methodology output: F4 F1/F4-CANDIDATE +
  severity-correction discipline codified as inheritance
  methodology — extends to playbook v3 candidate additions per
  §20 two-triggers rule (now used across S1303 + S1304 + S1305).
- **Post-close retrofit (2026-07-01 same day).** Chris directive
  after S1399 arc close: add §10 "What This Research Taught Us
  About How to Do Research" as a mandatory section in the playbook
  §11.3 canonical-summary template. S1399 retrofitted from 11
  sections to 12 sections as first application. Renumbering:
  former §10 Arc Change Log → §11; former §11 Appendix — Provenance
  → §12. Load-bearing methodology content previously at §10.4 moved
  into new §10.2 "What to codify into playbook v3" with two-triggers
  threshold status per pattern (3 patterns MET; 2 patterns Chris-
  ratified no-threshold). §11.4 preserved as backwards-compat
  pointer for external references to old §10.4 (OPEN_ARCS
  reconciliation notes; SESSION_1399 handoff `key_findings`).
  Playbook §11.3 template + rationale paragraph updated same-
  commit. Memory rules `feedback_xx99_meta_methodology_section.md`
  + `feedback_docs_cascade_at_every_close.md` saved. §12.6 arc
  close criteria checklist extended from 12 to 13 boxes (added
  "docs → RAG cascade executed post-merge"); all 13 ticked.
  Playbook §11.3 template becomes 12-section going forward — every
  future xx99 canonical summary includes §10 non-negotiably.

### 1.22 `domains/revenue/1400_revenue_domain_scoping.md`

- **Title.** Group 1400 Revenue / Outreach / Engagement — Parent Architecture Scoping (Phase 0)
- **Purpose.** **Arc-opening scoping deliverable for Research Group 1400** (Revenue / Outreach / Engagement — playbook §22 queue slot; S1273 §3.32 first-inventory row). Phase 0 domain-definition exercise per playbook §22 rule 3 (split large domains). First formal application of Chris's Phase 0 F.i/F.ii/F.iii methodology (Domain Definition / Existing Knowledge Inventory / Success Criteria) at §10/§11/§12 — proposed as playbook v3 §11.1 template addition at parent §9.5 (D29 Chris-lock; two-triggers threshold promotion at Group 1500 close).
- **Status.** Active (Chris-locked D21+D23-D29 across three "agree all" ratification rounds 2026-07-01; Rigby Light SIGN cycles 1 + 2 both SIGN-clean at Medium and Medium-High confidence respectively; 0 must-fix after fold on both cycles).
- **Research type.** Parent scoping (playbook §11.1 template + Chris's Phase 0 methodology overlay). `authority: parent-doc`, `category: parent_scoping`.
- **Primary questions answered.**
  - Should Group 1400 be a single audit or a parent-with-children structure? **Parent-with-children** (D23; 5-point rationale at §4).
  - What is the child mission sequence? **A → B → C → D → E → F → xx99** (D24 + D25 F.i); 6 children + canonical summary at S1499.
  - Is `Ops Autopilot` in scope? **Revenue-facing modules IN; cross-cutting primitives OUT** (D26).
  - How does SIGN routing work per stage? **Light on parent, Full on each child, Q10-Q13 canonical on xx99** (D27).
  - Who owns the Opportunity → Initiative wiring? **Child E owns** per Rigby Must-fix #2 escalated to D28.
  - Should Group 1400 pilot Chris's Phase 0 F.i/F.ii/F.iii methodology? **Yes-two-triggers** (D29); playbook v3 §11.1 promotes at Group 1500 close if second application unchanged.
- **Dependencies.**
  `platform_architecture_inventory.md` §3.32 + §4.9 (S1273 v2 Rigby-added Revenue row + cross-domain flow); `platform/cross_domain_integration_audit.md` §2.4 + §3.7 + §5.10 + §9.6 + §14 finding #36 (S1274 4 findings against domain 32); `domains/memory/1300_memory_domain_scoping.md` (parent-with-children exemplar); `domains/memory/1399_memory_canonical_summary.md` (first formal xx99 + F1-F4 methodology inheritance).
- **Recommended next reads.** Group 1400 child sequence — **S1401 (§1.23) Child A Opportunity Discovery + Scoring**, then S1402 Child B (Outreach), S1403 Child C (Engagement), S1404 Child D (Meeting + Close), S1405 Child E (Attribution + Analytics), S1406 Child F (Income/Jobs lane), S1499 xx99 canonical summary.
- **Overall importance.** **First application of Chris's Phase 0 3-step methodology in the library.** Codifies domain scoping discipline (5 F.i questions + 4 F.ii questions + 4 F.iii questions + 1 group-specific artifact requirement — Revenue Lifecycle Traceability Table). If Group 1500 applies the framework unchanged, playbook v3 §11.1 promotes at Group 1500 close per two-triggers threshold (S1399 §10 codified the threshold; S1400 is trigger #1).
- **Distinguishing property.** **First arc under Chris's Phase 0 methodology + first arc where the parent scoping doc explicitly proposes a playbook v3 addition.** 15 inherited findings enumerated at §11.4 (S1273 §3.32 + §4.9 + S1274 §2.4 + §3.7 + §5.10 + §9.6 + §14 finding #36 + S1399 F1-F4 methodology). 7 overlap points documented at §10.4 with existing arcs (Group 1300 closed; Employee OS 1200s; Groups 1500/1600/1700 not-started; Group 1300 Cat G delegated; post-1400 design-preparation). Rigby cycle 2 addition §12.5 requires Revenue Lifecycle Traceability Table at S1499 (8 stages minimum + 6 columns per stage + ≥3 verified writer/reader paths per stage + F1/F2/F3/F4 diagnostic-lens verdicts + row example template at §12.5 to prevent S1499 bikeshedding).

---

### 1.24 `domains/revenue/1402_revenue_outreach_composition_delivery_audit.md`

- **Title.** Group 1400 Revenue — Category B: Outreach Composition + Delivery Architecture Audit
- **Purpose.** **Second child audit under Research Group 1400 Revenue (parent §1.22).** Category B Outreach Composition + Delivery exclusive scope per parent §10.2 evidence-surface table + §12.1 Category B F.iii questions. Verifies the `OutreachDraft` model + `OpportunityDraftGenerator` composition path + `OutreachSequencer` scheduling + outbound-channel resolution + Outreach→Engagement seam. Grounded in verified runtime evidence at `main` HEAD `beda00e5`.
- **Status.** Draft → Active on Chris merge (Rigby SIGN-clean cycle 2 High confidence on fresh isolation pin `pa-4a0a28edcb7a45ec`; 2 must-fix + D.B7 dead-code fold cycle 1; 5 Q-answer folds cycle 2 with 3 nice-to-haves recorded for post-arc pickup). Pin retires post-PR-merge per playbook §15.
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: research`, `category: child_audit`.
- **Primary questions answered.** All 28 canonical questions + all 3 parent §12.1 Category B F.iii questions:
  - **Composition path — single-shot LLM vs Content Deliberation reviewer chain?** **SINGLE-SHOT LLM.** `OpportunityDraftGenerator.render_email` at `core/services/ops_autopilot/outreach_generation.py:340` calls `client.chat.completions.create(model='gpt-5-mini', messages=[system, user], max_completion_tokens=4000, response_format={'type':'json_object'})` via `get_openai_client()` factory. No Content Deliberation invocation, no reviewer chain. Resolves S1273 §10.3 UNKNOWN #1.
  - **Where does outreach actually get SENT?** **Nowhere.** Grep across mainline for `send_outreach|dispatch_outreach|deliver_outreach|outreach\.send|outreach_send` → 0 hits. Grep for `sendgrid|postmark|mailgun|smtplib|EMAIL_BACKEND` in mainline → 0 hits (only archive/, external-project-docs/, ai_core/). `core/settings.py` defines no provider credentials. Approved drafts accumulate at `status='approved'` until they expire 30 days later. **Resolves S1273 §10.3 UNKNOWN #2 + S1274 §2.4 line 293 MISSING → CONFIRMED and REFINED to "entire outbound channel missing, not just Inbox."**
  - **How does OutreachSequencer scheduling work?** `approve_draft(draft_id, edited_text)` transitions `draft → approved` (line 686) and schedules `next_touch_at = now + timedelta(days=TOUCH_DAYS[touch_number])`; `evaluate(now)` scans `approved AND next_touch_at <= now AND touch_number < MAX_TOUCHES` and creates follow-up rows. **BUT: `evaluate` is CONFIRMED DEAD CODE at runtime** — Rigby ops probe (celery_task_history 30d + PeriodicTask.filter(icontains='outreach')) + parent-Claude direct read (`td_handlers_ops.py:2699-2755` shows zero PA tool action wraps `.evaluate`; only `outreach_inbox`/`outreach_approve`/`outreach_reject`/`outreach_metrics_report` exposed) + repo-wide grep for `sequencer.evaluate`/`OutreachSequencer().evaluate` (0 hits) jointly confirm no invoker. Only Touch 1 fires at runtime via `generate-outreach-drafts-daily` beat.
- **Load-bearing findings (4).**
  - **F.B1 delivery path missing (CONFIRMED HIGH, runtime).** Grep-negative evidence complete at HEAD `beda00e5` across mainline. Category B is composition-only; delivery half is a missing subsystem. Approved drafts terminate at DB row.
  - **F.B3 engagement feedback loop missing (CONFIRMED HIGH, runtime).** No reply/click/open ingestion path. `EngagementEvent.outreach_draft` FK schema exists at `core/models_engagement.py:55-59` but zero writer sites for EngagementEvent. Category C S1403 inherits the seam build-out.
  - **F.B4 cadence declared but not realized at runtime (CONFIRMED via D.B7 probe).** OutreachSequencer declares 4-touch cadence; only Touch 1 fires. Touches 2–4 depend on `evaluate` which is dead code. Divergence between declared and implemented cadence.
  - **F.B2 follow-up composition writer-site is CONFIRMED F2 orphan-write + literal-stub pattern (code HIGH; runtime blast radius ZERO due to F.B4).** `revenue.py:812-829` writes `body_text = "Draft follow-up message needed."` and omits `opportunity=parent.opportunity` on create → every follow-up would be created with `opportunity=None`. CONFIRMED writer-site; CANDIDATE at repo-wide scope. Runtime blast radius zero because `evaluate` has no invoker.
- **Inherited findings status (from parent §11.4).** S1273 §10.3 UNKNOWN #1 RESOLVED (single-shot LLM); S1273 §10.3 UNKNOWN #2 + S1274 §2.4 line 293 RESOLVED to "entire outbound channel missing"; S1401 §14 D6 dual-representation drift RULED OUT for Category B (reads persistent `Opportunity.objects.filter(...)` only); S1401 F1 provenance-filter drift lens CANDIDATE extends to Category B reader surface; S1401 F2 orphan-write lens CONFIRMED at writer site, CANDIDATE repo-wide, blast radius ZERO at runtime; S1401 F3 Redis-only durability lens CLEAN for Category B; ownership gap CONFIRMED for Category B (no JobContract, no dedicated queue, shared `content` queue routing) — deferred to Child E per D28.
- **Dependencies.**
  `1400_revenue_domain_scoping.md` (parent — §10.2 evidence surface + §11.4 15 inherited findings + §12.1 Category B questions); `1401_revenue_opportunity_discovery_scoring_audit.md` (sibling — §9.1 integration map + §14 D6 dual-representation drift + §19 R1 umbrella); `platform_architecture_inventory.md` §3.32 + §4.9 [S1273]; `platform/cross_domain_integration_audit.md` §2.4 line 293 [S1274]; `domains/memory/1399_memory_canonical_summary.md` §4 F1/F2/F3/F4 [S1399 methodology inheritance].
- **Recommended next reads.** **S1403 Child C Engagement Inbound** next per parent §5 mission sequence. S1403 inherits Category B's F.B3 finding as its scope; the seam build-out (reply/click/open ingestion → EngagementEvent writes) is S1403's central deliverable. Also queued: §19 R.B1 delivery subsystem design ADR (umbrella); R.B2 follow-up composition subsystem; R.B3 F1 reader-side filter (Category-B-scoped per SIGN cycle 2 Q5); R.B4 evaluate cadence probe RESOLVED; R.B5 engagement ingestion path (S1403 owns); R.B6 offer-configuration debt; R.B7 send-gap fence test bundled with R.B1. D.B3 anchor-update at S1274 §2.4 line 293 recommended IMMEDIATELY per SIGN cycle 2 Q7 (truth correction, not synthesis).
- **Overall importance.** **Second Group 1400 child audit; first library audit to CONFIRM a missing-subsystem finding at HIGH runtime severity with complete negative-grep evidence.** Also first library audit where a Rigby ops probe + parent-Claude direct-read jointly CONFIRMED a dead-code finding (F.B4 / D.B7 / T.B5) mid-SIGN cycle 1 — extending S1401 verifier-loop from "hypothesis correction" to "runtime-liveness confirmation via ops telemetry." Load-bearing story: Category B is composition-only; the delivery half was never built AND the follow-up cadence half is dead code. This changes the arc's downstream integration seam question — Category C S1403 must build the entire ingestion path, not extend existing wiring.
- **Distinguishing property.** **First library audit where SIGN cycle 1 storage got truncated at Rigby's tool layer** — parent-Claude reconstructed the fold pass from (a) verbatim Must-fix #1 content (F.B2 CANDIDATE vs CONFIRMED classification drift), (b) inferred Must-fix #2 direction (F.B1 delivery-path severity: CONFIRMED HIGH not CANDIDATE HIGH, grep-negative evidence complete), (c) D.B7 dead-code confirmation via Rigby's ops probe + parent-Claude direct read. Cycle 2 SIGN-clean confirmed the inferred fold direction (Q3 downgraded D.B1 severity HIGH → MEDIUM as the only correction; Must-fix #2 inference verified correct). Sets pattern for future SIGN-storage-truncation recovery: reconstruct via combining verbatim excerpt + evidence-based inference + independent probe/read verification. Isolation pin `pa-4a0a28edcb7a45ec` retires post-PR-merge per playbook §15.

---

### 1.23 `domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md`

- **Title.** Group 1400 Revenue — Category A: Opportunity Discovery + Scoring Architecture Audit
- **Purpose.** **First child audit under Research Group 1400 Revenue (parent §1.22).** Category A Opportunity Discovery + Scoring exclusive scope per parent §10.2 evidence-surface table + §12.1 Category A F.iii questions. Verifies the mainline `Opportunity` model family (5 owned + 5 cited-only + FreelanceOpportunity/OpportunityTracking adjacent), 8 owned services + 2 agents + 1 WebSocket consumer + `OPPORTUNITY_SCORED` EventBus event + Category-A REST/PA-tool/Celery/management-command surface. Grounded in verified runtime evidence at `main` HEAD `ae30a1fe`.
- **Status.** Draft → Active (Rigby SIGN-clean cycle 2 High confidence on fresh isolation pin `pa-16d8b24d30e7a7d8`, 4 folds — 2 must-fix + 2 nice-to-have — applied cycle 1 and accepted cycle 2). Chris commit-gate flips status → active on merge per playbook §16. Pin retired at S1401 close per playbook §15.
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: research`, `category: child_audit`.
- **Primary questions answered.** All 28 canonical questions (§20.6 checklist) + all 6 parent §12.1 Category A F.iii questions (§20.7 checklist):
  - **What IS an Opportunity?** Mainline `Opportunity` at `core/models_unified_system.py:1201` with 27 core fields + 10-variant family (5 owned + 5 sibling-lifecycle/attribution + 1 engagement-feedback) enumerated at §4.
  - **Who produces Opportunities?** 4 confirmed writers of mainline `Opportunity.objects.create(...)`: `intelligence/spider_opportunity_connector.py:~620` (STRONG), `core/agents/analysis/opportunity_scoring_agent.py:~140` (WEAK NEW), `core/services/td_handlers_agents.py` (WEAK NEW), `core/services/income_action_service.py:~95` (WEAK NEW). 25 grep files matched; 21 false positives (Category F Income/Jobs surface + FreelanceOpportunity/OpportunityTracking/RealJobOpportunity/SpiderOpportunity dataclasses) deferred to S1406.
  - **How does scoring flow?** Flow α (spider → connector → `Opportunity.create` → `_publish_scoring_event` at `scoring_dispatcher.py:21` → `publish_opportunity_scored_event` at `event_bus.py:559` → `mi:opportunity_scored` stream). Flow β (`OpportunityPipelineOrchestrator` 5-stage agent routing via PA tool). Flow γ (sports lane isolated to `OpportunityTracking`). Flow δ (hourly `score_opportunities_from_spider_data` beat per WIREMAP.md:170). Flow ε (WebSocket `opportunity-scanner` READ-ONLY from `intelligence_engine.get_current_opportunities()`).
  - **What does OPPORTUNITY_SCORED carry + who consumes?** Payload verified: opportunity_id, spider_data_id, ml_score, rule_score, hybrid_score, confidence, priority, source. Handler registered at `event_handlers.py:48` (`self.register('opportunity_scored', handle_opportunity_scored_event)`); worker subscription verified at `event_handlers.py:536` (`create_validation_worker` streams). Corrected handler action per file:line comment: DETECTS + LOGS only (HITL service creates the validation request separately, not this handler).
  - **What is OpportunityScannerConsumer for?** READ-ONLY WebSocket listener streaming from `intelligence_engine.get_current_opportunities()` in-memory realtime source — NOT persistent `Opportunity` model. Room group `opportunity_scanner`. Hard-coded initial payload `domains_monitored: [SPORTS_BETTING, CRYPTO, TRADING, REAL_ESTATE]`.
  - **Does sports_opportunity_generator produce into mainline Opportunity or a separate lane?** **SEPARATE LANE** — `intelligence/sports_opportunity_generator.py:83` writes `OpportunityTracking.objects.create(...)` (intelligence app), not mainline `Opportunity`. S1274 §2.4 line 270 MISSING classification REMAINS ACCURATE for mainline; refinement is "separate lane" wording rather than "missing implementation."
- **Load-bearing findings.**
  - **Sports lane resolved (§12.1 Q6):** separate lane framing per M1 fold.
  - **NEW dual opportunity representation drift (§14 D6 + §19 R1 umbrella):** 5 consumer sites in `consumers_base.py` (lines 1696, 1730, 2541, 2557, 2597) stream from `intelligence_engine.get_current_opportunities()` in-memory source — Rigby SIGN cycle 1 grep expanded finding from 1 site to 5.
  - **F1 provenance drift CANDIDATE (HIGH):** writers tag `source` + `metadata['spider_source']` inconsistently across producers (spider connector complete; agents + PA-tool paths sparse); readers ignore provenance.
  - **F3 Redis-only durability CANDIDATE (HIGH):** `spider_opportunity_connector.py` uses async Redis with `cache_timeout=300`, no DB fallback.
  - **F2 orphan-write cluster CANDIDATE (HIGH):** 10-variant Opportunity family + Session Pre-38 partnership_* fields (10 fields with defaults, consumption sites unverified).
  - **OpportunityPipelineOrchestrator vs OpportunityExecutionPipeline COMPLEMENTARY, not overlapping** (parent-Claude verifier-loop resolved Agent 6's duplication flag via Agent 2 direct read — Orchestrator = transform Dict→Dict, ExecutionPipeline = materialize Opportunity→PartnershipProject).
  - **NEW debt T5:** `settings.py` `task_routes` defines `score_opportunities_from_spider_data` TWICE (line 1277 `long_running` + line 1484 `content`); later wins → effective queue `content`. Follow-on cleanup PR needed.
  - **Ownership gap CONFIRMED** (S1274 §14 #36 inherited HIGH); no JobContract wiring, no dedicated beat queue, no CODEOWNERS-style artifact. Deferred to Child E aggregate per D28.
  - **Maturity WORKING** (S1273 baseline preserved; no upgrade/downgrade). **Coverage LIGHT** (matches parent §11.3; upgrade candidate at S1499 xx99).
- **Dependencies.**
  `1400_revenue_domain_scoping.md` (parent — §10.2 evidence surface + §11.4 15 inherited findings + §12.1 Category A questions + §12.5 F.iii artifact requirement); `platform_architecture_inventory.md` §3.32 + §4.9 [S1273]; `platform/cross_domain_integration_audit.md` §2.4 + §3.7 + §5.10 + §6.2 + §9.6 + §14 finding #36 [S1274]; `domains/memory/1399_memory_canonical_summary.md` §4 F1/F2/F3/F4 [S1399 methodology inheritance].
- **Recommended next reads.** **S1402 Child B Outreach Composition + Delivery** next per parent §5 mission sequence. Also queued: §19 R1 umbrella "Dual-representation + provenance contract" post-arc design-preparation ADR; R2 scoring rate telemetry probe (Rigby-side ORM); R3 producer inventory completion → Category F S1406; R4 PeriodicTask row verify; R5 OpportunityAIAnalyzer liveness probe; R6 expires_at enforcement audit; R7 OPPORTUNITY_CREATED stream disposition; R8 T5 Celery route cleanup PR.
- **Overall importance.** **First Group 1400 child audit; validates the audit contract's parent-Claude verifier-loop discipline BEFORE Rigby.** 5 sub-agent claims corrected pre-SIGN (Agent 3 beat-schedule negative claim + orchestrator-overlap flag + publisher-line correction + dual-representation surfaced from consumer read + Celery duplicate surfaced from settings grep). Rigby SIGN cycle 1 SIGN-with-edits (4 folds — 2 must-fix + 2 nice-to-have) at High confidence; cycle 2 SIGN-clean High confidence. Sports lane verdict resolves parent §12.1 Q6 definitively (SEPARATE LANE — S1274 MISSING remains accurate for mainline). Dual opportunity representation NEW finding sets up R1 umbrella design-preparation ADR.
- **Distinguishing property.** **First library audit to surface a NEW dual-representation drift finding via a Rigby SIGN cycle 1 grep expansion** — Rigby's independent verification broadened the finding from 1 consumer site to 5, changing R1 from "single consumer's local bug" to "arc-wide contract question." Also first library audit where parent-Claude verifier-loop overrode a sub-agent's duplication flag via a competing sub-agent's direct code read (Agent 6 flagged Orchestrator ↔ ExecutionPipeline as duplication candidate; Agent 2's direct read showed complementary roles). Isolation pin `pa-16d8b24d30e7a7d8` retired at S1401 close per playbook §15.

---

### 1.25 `domains/revenue/1403_revenue_engagement_inbound_audit.md`

- **Title.** Group 1400 Revenue — Category C: Engagement Inbound Architecture Audit
- **Purpose.** **Third child audit under Research Group 1400 Revenue (parent §1.22).** Category C Engagement Inbound exclusive scope per parent §3 Cat C evidence surface + §12.1 Category C F.iii questions. Verifies the 4 engagement-shape models (`EngagementEvent` + `EngagementMetrics` + `OpportunityInteraction` + `ContentEngagement`) + `EngagementEngine` 7-method surface + `EngagementAutonomyEngine` 4-method surface + policy-engine wiring + WebSocket-consumer session-aggregation axis + F.B3 ingestion path design-preparation (inherited from S1402 as CENTRAL S1403 deliverable). Grounded in verified runtime evidence at `main` HEAD `d91d30f7`.
- **Status.** Draft → Active on Chris merge (Rigby SIGN-clean cycle 2 High confidence on fresh isolation pin `pa-fba0c4c81fba4922`; cycle 1 SIGN-with-edits Medium-High confidence → cycle 1 fold applied — must-fix #1 (runtime row-count verification) empirically CLOSED via parent-Claude Django ORM `.count()` on local env (all 4 Category C tables = 0 rows) + must-fix #2 (placeholder-stall artifact) WITHDRAWN as Rigby cycle-1 narrative artifact not audit defect + 4 Q-answer folds Q1/Q4/Q5/Q6; cycle 2 SIGN-clean High confidence + Q7/Q8/Q9 answers + 2 nice-to-have folds — Env Coverage Table + T.C8 three-checkbox split). Pin retires post-PR-merge per playbook §15.
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: research`, `category: child_audit`.
- **Primary questions answered.** All 28 canonical questions + all 3+1 parent §12.1 Category C F.iii questions (the +1 = inherited "how to design F.B3 ingestion given F.B1 delivery gap"):
  - **Which of the 4 engagement models is canonical?** `EngagementEvent` at `core/models_engagement.py:18` is parent-declared canonical inbound event stream — **but has ZERO writer sites at HEAD `d91d30f7`**. Grep `EngagementEvent.objects.create|EngagementEvent(` → only class definition. Both `outreach_draft` FK (:55-59) and `opportunity` FK (:62-66) are schema-only. **Empirical runtime CONFIRMATION** via parent-Claude Django ORM: `EngagementEvent.objects.count() = 0`. Extends S1402 F.B3 with the second-FK evidence.
  - **What is the event stream vs aggregate axis?** Parent §3 Cat C hypothesized three-axis map (event log = EngagementEvent; aggregation = EngagementMetrics + ContentEngagement; join = OpportunityInteraction) — **REFUTED by dual-sub-agent verification.** Actual axis is **three independent surfaces**: (i) EngagementEvent event-log axis architecturally-declared but runtime-empty; (ii) session-aggregation axis EngagementMetrics + OpportunityInteraction lives at `revenue_opportunities_consumer.py:849/527/694` WebSocket-consumer dual-write; (iii) ContentEngagement is orthogonal content-pipeline learning surface with no FK back to inbound. OpportunityInteraction is detail-child of EngagementMetrics via nullable `engagement_session` FK, not a join artifact.
  - **What does EngagementAutonomyEngine gate + default state?** Monitoring + reporting only; **NOT gating.** SLA thresholds hardcoded (`SLA_WARNING_HOURS=4`, `SLA_CRITICAL_HOURS=24`, `SLA_BREACH_HOURS=48`). No governance §3.23 crossover — kill-switch does NOT gate engagement autonomy. Default state: no autonomy mutations, no autonomous replies.
  - **How would F.B3 ingestion path be designed given F.B1 gap?** Central S1403 deliverable per §19 R.C1: webhook receiver `/api/webhooks/engagement/<provider>/` reusing Stripe pattern at `views_stripe.py:41-53`; 4 new EventStream additions (`ENGAGEMENT_REPLIED/OPENED/CLICKED/CLASSIFIED`); writer contract + idempotency via `get_or_create(outreach_draft=..., provider_message_id=...)`; feature-gate `settings.ENGAGEMENT_INGESTION_ENABLED`. BLOCKER pre-work: `OutreachDraft.provider_message_id` field MISSING (grep zero hits in `models_outreach.py`). Rigby cycle 1 Q4 lean **two sequential ADRs** — F.B1 delivery first (establishes channel + identifiers), F.C1 inbound ingestion stacked on top; "cleaner dependency ordering and less thrash."
- **Load-bearing findings (6).**
  - **F.C1 ingestion path missing (CONFIRMED HIGH — code + runtime local, prod unknown).** Zero EngagementEvent writer sites at HEAD `d91d30f7`. Grep + Django ORM `.count() = 0` both confirm. Extends S1402 F.B3 with `opportunity` FK second-writer-gap evidence. Prod PENDING (T.C8 tool gap).
  - **F.C2 corrected axis map (CONFIRMED, dual-agent verified).** Three independent surfaces — not the parent §3 hypothesis.
  - **F.C3 OpportunityInteraction F2 orphan-write CONFIRMED at writer-site `views_opportunities.py:56-65`.** REST `quick_apply()` omits `engagement_session` FK. Runtime blast radius LOCAL = ZERO (`OpportunityInteraction.objects.count() = 0`). Prod UNKNOWN. Sibling to S1402 F.B2 zero-blast-radius pattern via different mechanism.
  - **F.C4 ContentEngagement docstring drift (CONFIRMED HIGH docstring, MEDIUM runtime).** `models_pipeline_feedback.py:372-378` claims "closes the learning loop"; no FK bridge to EngagementEvent/Metrics/OpportunityInteraction exists. Rigby cycle 1 Q5 lean (i) narrow docstring NOW.
  - **F.C5 EngagementAutonomyEngine "reply context builder" drift (CONFIRMED LOW).** `engagement.py:774` lists 4 value-adds; no such method in 4-method class body. Rigby cycle 1 Q6 lean (iii) reframe as "planned surface."
  - **F.C6 `run_ops_autopilot` deferred-by-policy (CONFIRMED, load-bearing nuance to policy-engine claims).** `core/tasks.py:13090` defines beat wrapper with declared 10min cadence docstring; NOT registered as PeriodicTask (0 of 92 enabled rows); intentionally deferred per AUDIT_FINDINGS.md #12 gating (`core/celery.py:507-509` + `:633-634`). Ad-hoc PA-tool invocation path LIVE at `td_handlers_ops.py:1643,1674`. Category C's `evaluate()` sweeps fire only on operator initiation, never autonomous. Memory rule `feedback_audit_findings_12_canonical_celery_deferred_list.md` triggered pre-SIGN. Rigby cycle 2 Q1 lean **(iii) separate ADR outside G1400 arc** for enable-decision (cross-category impact spans all 6 categories).
- **Inherited findings status (parent §11.4 + S1402).** S1402 F.B3 CONFIRMED HIGH and EXTENDED (now includes `EngagementEvent.opportunity` FK second-writer-gap). S1402 F.B1 delivery-path-missing BLOCKER dependency for F.C1 ingestion design. S1402 F.B4 cadence-not-realized does NOT extend to Category C evaluate methods (both LIVE via policy registry, though F.C6 deferred-by-policy means autonomous cadence dormant). S1401 F1 provenance-filter drift CANDIDATE extends to Cat C readers. S1401 F2 orphan-write CONFIRMED at `views_opportunities.py:56-65` (F.C3). S1401 F3 Redis-only durability CANDIDATE holds (`revenue_opportunities_consumer.py:302-306` 5min TTL). Ownership gap S1274 §14 #36 CONFIRMED HIGH for Category C (0 JobContract + 0 AGENT_MAP + 0 task_routes hits for "engagement"). Coverage upgraded LIGHT → MODERATE. Maturity WORKING (code) / DEFERRED-BY-POLICY (autonomous runtime) / WORKING code + DORMANT local (session-agg) / MISSING (canonical ingestion) — four-way split extending S1402 WORKING/PARTIAL pattern.
- **Dependencies.**
  `1400_revenue_domain_scoping.md` (parent — §3 Cat C evidence surface + §11.4 15 inherited findings + §12.1 Category C questions); `1401_revenue_opportunity_discovery_scoring_audit.md` (sibling — §9.1 integration map); `1402_revenue_outreach_composition_delivery_audit.md` (sibling — §9 integration map + F.B3 CENTRAL inheritance + §14 D.B3 anchor-update precedent + §19 R.B5 engagement ingestion path); `platform_architecture_inventory.md` §3.32 + §4.9 [S1273]; `platform/cross_domain_integration_audit.md` §2.4 + §5.10 + §14 #36 [S1274]; `domains/memory/1399_memory_canonical_summary.md` §4 F1/F2/F3/F4 [S1399 methodology inheritance]; `docs/AUDIT_FINDINGS.md` §12 [F.C6 deferred-by-policy classification source].
- **Recommended next reads.** **S1404 Child D Meeting + Close** next per parent §5 mission sequence. Category D inherits Category C's session-aggregation axis + read-only-EngagementEngine surface + Rigby cycle 1 Q4 sequential-ADR pair-design recommendation (F.B1 → F.C1 order). Also queued: §19 R.C1 F.C1 ingestion path ADR (CENTRAL — pair-designed sequentially with F.B1); R.C2 F.C3 orphan-write fix at `views_opportunities.py:56-65`; R.C3 F.C4 ContentEngagement FK bridge (post-arc); R.C4 documentation anchor updates at `platform_architecture_inventory.md` §3.32 with per-model annotations (EngagementEvent schema-present-ingestion-missing-count=0; EngagementMetrics/OpportunityInteraction aggregation-axis-working-count=0-due-to-no-WS-activity; short note "engagement inbound relies on session/WebSocket surfaces not canonical event ingestion") per Rigby cycle 2 Q9 lean; R.C5 `OutreachDraft.provider_message_id` migration (blocks R.C1); R.C6 F.C5 "reply context builder" resolution (three-fork); R.C7 Governance §3.23 crossover ADR (bundle with Group 1700 Observability); R.C8 F1 provenance-drift repo-wide sweep (deferred until F.C1 ingestion writer contract lands). **T.C8 tool-surface gap** (ToolCallRecord query + bounded ORM count + prod DB reach) IMMEDIATE per Rigby cycle 2 Q8 — low-risk high-leverage arc-support tools.
- **Overall importance.** **Third Group 1400 child audit; first library audit to CONFIRM a canonical event log architecturally-intact-but-runtime-empty finding at both CODE and RUNTIME LOCAL tiers** via parent-Claude Django ORM `.count()` when Rigby's `db_health_tool` returned indeterminate `row_count=-1` estimate. Also first library audit where **PROD runtime tier is explicitly UNKNOWN due to Rigby tool-surface gap** (T.C8 `db_health_tool env=prod` "not configured: PA_DB_HEALTH_RPC_URL, PA_DB_HEALTH_RPC_CLIENT_TOKEN") — logged as explicit constraint on empirical falsification scope. Load-bearing story: Category C is code-complete on read-only monitoring + session-aggregation surfaces but runtime-dormant in the probed env; canonical ingestion has no writer path; the F.B1 → F.C1 pair-design sequential ADR is the arc-forward critical path.
- **Distinguishing property.** **First library audit where parent-Claude Django ORM `.count()` closed a Rigby cycle 1 must-fix that Rigby's own tool surface could not resolve** — extends the S1402 D.B7 joint-verifier-loop methodology to "when Rigby's tool returns indeterminate, parent-Claude runs direct-verification via alternate path (Django `.venv/bin/python manage.py shell` in this case)." Also first library audit where **Rigby withdraws a cycle-1 must-fix as her own narrative artifact after parent-Claude pushback** (cycle 2 Rigby: "Must-fix #2 is withdrawn: agreed it was my cycle-1 response artifact, not an audit-file defect"). Sets pattern for two verifier-loop conventions: (a) parent-Claude runs alternate direct-verification when Rigby's tool returns indeterminate; (b) parent-Claude pushback on must-fix classification is a legitimate cycle-2 fold move when the must-fix originates in Rigby's own response artifact rather than audit content. Isolation pin `pa-fba0c4c81fba4922` retires post-PR-merge per playbook §15.

### 1.26 `domains/revenue/1404_revenue_meeting_close_audit.md`

- **Title.** Group 1400 Revenue — Category D: Meeting + Close (Child audit under Group 1400 Revenue arc)
- **Purpose.** **Fourth child audit under Research Group 1400 Revenue (parent §1.22).** Category D Meeting + Close exclusive scope per parent §3 Cat D evidence surface + §12.1 Category D F.iii questions. Verifies the `Meeting` model (`core/models_meeting.py:18`) + `ClosePack` model (`core/models_close_pack.py:20`) + `MeetingEngine` service (`ops_autopilot/engagement.py:479-757`) + `CloseTheDealEngine` service (`ops_autopilot/revenue.py:851-1010`) + `ClosePackAutonomyEngine` monitoring service (`revenue.py:1504-1776`) + 2 policy-hook wirings (`_policy_meeting_engine` + `_policy_close_pack_autonomy`) + 12 PA tool actions (5 Meeting + 7 ClosePack) + HumanAttentionItem interlock verification (F.D4) + integrity audit design (§19 R.D8). Grounded in verified runtime evidence at `main` HEAD `12775448`.
- **Status.** Draft → Active on Chris merge (Rigby SIGN-clean cycle 2 High confidence on fresh isolation pin `pa-87ee24cd0d3947ce`; cycle 1 SIGN-with-edits Medium-High confidence + 4 must-fix + 4 nice-to-have fold cycle 1 — F.D10 promotion + F.D7/F.D8/F.D9 anchor corrections + Q1-Q9 answers all folded; cycle 2 NH-2 F.D6 "why it matters" expansion + NH-3 PROD-facing runtime-liveness stub applied; NH-1 + NH-4 deferred). Pin retires post-PR-merge per playbook §15.
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: research`, `category: child_audit`.
- **Primary questions answered.** All 28 canonical questions + all 4 parent §12.1 Category D F.iii questions + 1 inherited-from-S1403 (Meeting-trigger runtime liveness given F.C1 + F.C6):
  - **When does an EngagementEvent trigger a Meeting (auto vs manual)?** MANUAL only. Sole writer `MeetingEngine.create_meeting()` at `engagement.py:490-526` omits `engagement=` FK on `Meeting.objects.create()` at `:507`. Even if the model had rows, `engagement_id` would be NULL 100% of the time on this path. Auto-trigger requires F.B1 → F.C1 sequential-ADR pair from S1402+S1403 as blockers, plus a new Meeting writer that reads high-intent EngagementEvent rows.
  - **How is ClosePack assembled + triggered?** MANUAL PA-tool triggered. Sole writer `CloseTheDealEngine.generate_pack()` at `revenue.py:931-1010` creates rows via PA tool action `close_pack_generate` at `td_handlers_ops.py:2757-2776`. No auto-pipeline, no HumanAttentionItem approval-gate on creation. Post-creation state gating via `close_pack_approve` (draft → approved). **Resolves S1273 §10.3 UNKNOWN #3 → MANUAL.**
  - **Where does HumanAttention interlock (approval-required conversion)?** NOWHERE at Meeting/ClosePack level. Zero writers from any Category D path create `HumanAttentionItem`. Runtime probe: HAI.count = 3061 total, distribution shows 2854 spider_pipeline + 155 agent_output + only 2 ops_autopilot rows (from `_policy_revenue_pipeline` stale-opportunity monitoring, NOT approval-gating). Existing `_policy_revenue_pipeline` HAI writer at `core.py:2051-2066` fires for pipeline monitoring, not approval interlock. Extends S1402 (Cat B) + S1403 (Cat C) same finding → **Group 1400 arc-wide CONFIRMED SYSTEMIC GAP** for S1499 xx99. **Resolves S1274 §2.4 line 294 MISSING to CONFIRMED HIGH.**
  - **What does the integrity audit design look like (S1274 §5.10 orphan-record risk)?** Design skeleton at §19 R.D8. Scope: 5 models (OutreachDraft + EngagementEvent + Meeting + ClosePack + HumanAttentionItem). 10 orphan patterns across the 4 core models. Multi-layer detection (post-write signals + daily sweep + on-demand PA tool). Report-first repair policy (Chris-adjudicated via HAI escalation). Precedents: `core/signals/initiative_diagnostic_signals.py` (S1196 post_save + pre_save FK stash + `.filter(pk=...).update()` no-recursion pattern), `consolidate_workspaces.py` (bulk detection + reassignment), `fix_workspace_visibility.py` (multi-step remediation), `fix_orphan_initiative_tracking.py` (Session 906 retroactive tracking). **Design lands NOW; implementation POST F.B1/F.C1** — currently zero rows means no orphans to audit yet. Cycle-2 NH R.D8 CI guard smoke test added per Rigby cycle 1 Q6 lean.
  - **Inherited from S1403: How does Category D reason about Meeting-trigger runtime liveness given F.C1 + F.C6?** Category D is CODE-COMPLETE + RUNTIME-DORMANT at LOCAL. `Meeting.objects.count() = 0` empirically CONFIRMS the dormancy. Policy-hook `_policy_meeting_engine` LIVE in registry at `core.py:278` but fires only via deferred `run_ops_autopilot` beat per AUDIT_FINDINGS.md #12 gating. Autonomous cadence gated by same F.C6 policy decision. §19 R.D5 cross-links.
- **Load-bearing findings (10 — F.D10 added SIGN cycle 1 fold from T.D5 CANDIDATE promotion).**
  - **F.D1 Meeting-trigger runtime liveness at LOCAL = ZERO (CONFIRMED HIGH CODE + RUNTIME LOCAL).** Django ORM probe: Meeting=0, ClosePack=0, EngagementEvent=0. PROD unknown per T.C8(c).
  - **F.D2 Meeting.engagement FK never populated by sole writer.** `engagement.py:507`; F2 orphan-write class code-tier only (bounded by F.D1).
  - **F.D3 ClosePack trigger = MANUAL PA tool only.** Sole writer `revenue.py:931/:991`. Docstring at `models_close_pack.py:6-12` aspirational.
  - **F.D4 Revenue → HumanAttention CONFIRMED MISSING HIGH.** Arc-wide SYSTEMIC gap across Cat B + C + D.
  - **F.D5 Meeting docstring drift HIGH.** `models_meeting.py:22` "Created manually or from EngagementEvent" — engagement fork uninhabited.
  - **F.D6 Meeting 3 unreachable states MEDIUM.** `no_show`/`cancelled`/`followed_up` declared but no writer.
  - **F.D7 Parent §3.D anchor drift: ClosePackAutonomyEngine misnamed as writer.** Actual writer is CloseTheDealEngine. Immediate anchor-update (§20.10).
  - **F.D8 Parent §3.D category miscount: MeetingCoordinatorAgent NOT a Meeting writer.** Executive-agent facilitation surface; zero `Meeting.objects.create`. Immediate anchor-update (§20.10).
  - **F.D9 Structural correction: OpportunityAction + OpportunityTask are Cat A parallel axis, not Cat D lifecycle checkpoints.** Zero FK to Meeting/ClosePack. Reclassify to Cat A. Immediate anchor-update (§20.10).
  - **F.D10 ClosePack state machine PARTIAL (SIGN cycle 1 promotion, HIGH).** Writers for `draft` (default at `:991`), `approved` (`:1073`), `expired` (`:1173` bulk `.update()`). `sent`/`won`/`lost` CONFIRMED unreachable — all grep hits are `.filter()` READS. Paired arc-drift finding with F.D6 Meeting analog for xx99. Joint verifier-loop discipline extension: Rigby broader-grep + parent-Claude direct-read disambiguation of substring-ambiguous grep hits.
- **Inherited findings status (parent §11.4 + S1401/S1402/S1403).** S1274 §2.4 line 294 Revenue → HumanAttention MISSING CONFIRMED HIGH arc-wide (F.D4). S1274 §5.10 tight-coupling LOW-by-design CONFIRMED at Meeting-engagement + ClosePack-outreach_draft null-FK level; runtime blast radius bounded by F.D1. S1274 §14 finding #36 (Revenue Pipeline no runtime owner HIGH) CONFIRMED for Cat D (§18); deferred to S1405 Cat E per D28. S1273 §10.3 UNKNOWN #3 RESOLVED to MANUAL (F.D3). S1401 §9 Cat A → D read direction verified. S1402 §14 D.B7 dead-code methodology applied inversely at F.D8 (MeetingCoordinatorAgent has invokers via PA dispatch, not dead — memory rule `feedback_verify_before_deleting_dead_code.md`). S1403 F.C1 (empty EngagementEvent) + F.C6 (deferred `run_ops_autopilot`) inherited as upstream blockers for Meeting-trigger autonomous cadence. S1399 F1/F2/F3/F4 methodology lenses applied at §14 D.D6/D.D7 (F2 orphan-write class extends to Meeting + ClosePack writer sites). Coverage LIGHT → MODERATE.
- **Dependencies.**
  `1400_revenue_domain_scoping.md` (parent — §3 Cat D evidence surface + §11.4 15 inherited findings + §12.1 Category D questions); `1401_revenue_opportunity_discovery_scoring_audit.md` (sibling — §9.1 integration map); `1402_revenue_outreach_composition_delivery_audit.md` (sibling — §9 integration map + F.B1 delivery gap as upstream blocker); `1403_revenue_engagement_inbound_audit.md` (sibling — §9 integration map + F.C1 ingestion-missing + F.C6 run_ops_autopilot deferred); `platform_architecture_inventory.md` §3.32 + §4.9 [S1273]; `platform/cross_domain_integration_audit.md` §2.4 line 294 + §5.10 + §14 #36 [S1274]; `domains/memory/1399_memory_canonical_summary.md` §4 F1/F2/F3/F4 [S1399 methodology inheritance]; `docs/AUDIT_FINDINGS.md` §12 [F.D9 policy-hook deferred classification source].
- **Recommended next reads.** **S1405 Child E Revenue Attribution + Analytics** next per parent §5 mission sequence + parent §12.1 D28 arc-scoping decision. Category E inherits Category D's runtime-dormant seams (Meeting/ClosePack runtime empty at LOCAL) + arc-wide HAI missing (F.D4) + arc-wide ownership gap (§18) + F.D10 state-machine-partial pattern extension possibility for `OpportunityRevenue` / `OpportunityOutcome` state machines. Also queued: R.D1 Meeting + ClosePack writer normalization ADR (F2 class); R.D2 Meeting state machine completion ADR (F.D6 fix); **R.D3 Category D anchor-updates ADR IMMEDIATE per Rigby Q1+Q2 leans** (parent §3.D + platform_architecture_inventory.md §3.32); R.D5 policy-hook enablement ADR (inherited from S1403 R.C1 disposition — cross-arc); **R.D6 HumanAttention interlock ADR bundled with F.B1 → F.C1 stacked pair per Rigby cycle 1 Q5** (Meeting recap-send gate + ClosePack send gate + ClosePack won/lost adjudication); **R.D8 integrity audit design skeleton lands NOW + CI guard smoke test per Rigby cycle 1 Q6** (implementation POST F.B1/F.C1); R.D9 F1 provenance-filter drift repo-wide sweep (deferred until F.B1/F.C1 write-side lands). **T.C8 tool-surface gap** IMMEDIATE per Rigby cycle 1 Q8 lean (a) ToolCallRecord query + (b) bounded ORM count NOW pre-S1405; (c) prod DB RPC config to unlock F.D1 PROD confirmation.
- **Overall importance.** **Fourth Group 1400 child audit; first library audit to surface parent-doc drift as a load-bearing must-fix cluster** — three parent-doc corrections (F.D7 ClosePack writer + F.D8 MeetingCoordinatorAgent + F.D9 OpportunityAction/Task axis) all landing at immediate S1404 commit-time per Rigby cycle 1 Q1+Q2 leans. Also first library audit to CONFIRM a paired arc-level structural drift (F.D6 Meeting + F.D10 ClosePack; both models declare 6-state STATUS_CHOICES but implement only 3-4; symmetric unreachable-state pattern). Group 1400 arc convergence surfaces at S1404: Categories A/B/C/D all confirming (i) Revenue → HumanAttention MISSING (F.D4 arc-wide), (ii) ownership gaps (§18 arc-wide inheritance from S1274 §14 #36), (iii) runtime-liveness dormancy where autonomous cadence is deferred (F.D9 same class as S1403 F.C6). S1499 xx99 canonical summary trajectory (Rigby cycle 1 fold): single "activate the revenue lifecycle + enforce approval/attention gating" remediation plan.
- **Distinguishing property.** **First library audit where joint Rigby broader-grep + parent-Claude direct-read disambiguation resolved substring-ambiguous grep hits during SIGN cycle 1 fold** — Rigby's initial `status='sent'` grep returned mixed `.create()` writes + `.filter()` READS; parent-Claude direct-read at `revenue.py:1100-1180` disambiguated writers from reads. Extends S1403 "alternate-path direct-verification when Rigby tool returns indeterminate" pattern to "alternate-path direct-read disambiguation when Rigby grep returns substring-ambiguous hits" — new verifier-loop discipline extension for S1499 arc-methodology synthesis. Also first library audit to surface **3 parent-doc drift findings in a single audit** (F.D7 + F.D8 + F.D9) — extends S1401's 5-sub-agent-correction methodology to include upward-directed parent-doc drift catches, not just lateral sub-agent claims. Isolation pin `pa-87ee24cd0d3947ce` retires post-PR-merge per playbook §15.

### 1.27 `domains/revenue/1405_revenue_attribution_analytics_audit.md`

- **Title.** Group 1400 Revenue — Category E: Revenue Attribution + Analytics (Child audit under Group 1400 Revenue arc)
- **Purpose.** **Fifth child audit under Research Group 1400 Revenue (parent §1.22).** Category E Revenue Attribution + Analytics exclusive scope per parent §3 Cat E evidence surface + §12.1 Category E F.iii questions. Verifies `OpportunityRevenue` model (`core/models_unified_system.py:2613`) + `OpportunityOutcome` model (`:3394`) + `OpportunityContent` model (`:2805`) + `ImpactEvent` model (`core/models_impact_events.py:21-120`) + `ImpactCredit` model (`core/models_impact_credit.py`) + attribution algorithm at `MultiTouchAttributor._attribute_event` (`ops_autopilot/impact.py:1233-1290`) + `ImpactCollector` emission (`impact.py:238-505`) + `revenue_attribution_bridge.py:147+:181` signal-driven UserAgentLearning writes + 3 view files (`views_revenue.py` + `views_revenue_analytics.py` + `views_revenue_tracking.py`) + `calculate_daily_revenue_metrics` beat task (`intelligence/tasks.py:1462-1495`) + PA tool `revenue_tracker_tool` (`pa_tool_schemas.py:188-208`) + F.D4 refinement to code-exists/runtime-dormant. Grounded in verified runtime evidence at `main` HEAD `2355f5be`.
- **Status.** Draft → Active on Chris merge (Rigby SIGN-with-edits cycle 1 PARTIAL — Batch 1 F.E1-F.E3 substantive pressure-test delivered on fresh isolation pin `pa-4bdd5ad264674ce8` [jammed after batch] + retried on `pa-637331c5f9574a10` [worker instability blocked batches 2-3]; F.E3 framing refinement folded at commit-time per Rigby Batch 1 lean; F.E2 flagged MUST-FIX before canonical; Batches 2-3 deferred to follow-up SIGN addendum per D45 Chris ratification 2026-07-01 option (ii)). Both pins retire post-PR-merge per playbook §15.
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: research`, `category: child_audit`.
- **Primary questions answered.** All parent §12.1 Category E F.iii questions:
  - **What is the revenue attribution algorithm (`ops_autopilot/revenue.py`)?** **PARENT-DOC DRIFT (F.E6):** Algorithm is NOT in `revenue.py`. Actual location: `core/services/ops_autopilot/impact.py:1233-1290` (`MultiTouchAttributor._attribute_event`). 70% last-touch + 30% assist evenly split among upstream via `trace_id` + `deliverable→initiative/dream` + `agent_chain` (`_find_upstream:1292+`, MAX_HOPS cap). Writes `ImpactCredit` rows (`core/models_impact_credit.py`). `ops_autopilot/revenue.py` contains pipeline forecasting engines only. Anchor correction landed at S1405 commit-time.
  - **How does `ImpactEvent` emission work (write/read registry)?** `ImpactCollector` at `impact.py:238-505` harvests from Wager (`:375`), DeliverableEvent (`:431`), Revenue (`:488`) sources. Idempotent dedup by `(source_object_type, source_object_id)`. 6+ readers: `PortfolioAllocator.compute_desk_iqroi:582`, `MultiTouchAttributor.attribute_recent:1209`, `ROIEnforcer budget.py:644`, `ExperimentEngine experiment.py:641`, `get_attribution_report:1457`. Governance write via `_policy_attribution_debt (core.py:1673) → HAI`. **S1274 §2.4 STRONG classification VERIFIED end-to-end (F.E8).**
  - **How do 4 frontend routes + 3 view files serve distinct vs overlapping needs?** **PARENT-DOC DRIFT (F.E4):** The 4 named routes DO NOT EXIST in `frontend/src/App.tsx` (grep: 0 matches). Actual revenue surfaces: `/analytics` route (calls `/api/v1/analytics/charts/revenue/`) + `/intelligence` route (opportunity discovery). Anchor correction landed at commit-time. Among 3 view files: `views_revenue_analytics.py` architecturally distinct (7 endpoints); `views_revenue.py` + `views_revenue_tracking.py` provide DUPLICATE endpoint pairs (F.E5 CONFIRMED HIGH; consolidation ADR R.E-2 proposed).
  - **What is the runtime owner recommendation (S1274 §14 #36 HIGH)?** **F.E10 CONFIRMED HIGH:** Runtime owner ABSENT arc-wide. Zero JobContract in `core/employees/jobs.py`; zero AGENT_MAP entries in `core/agent_router.py`; zero task_routes; no dedicated queue. Only ownership signal: PA tool `revenue_tracker_tool` at `pa_tool_schemas.py:188-208`. **Recommendation: Revenue Employee JobContract under Employee OS** (R.E-1 ADR).
  - **Inherited from S1404: How does Cat E reason about Revenue Attribution runtime liveness given F.D1 + F.D3 + F.D4 + F.D10?** Attribution engine is CODE-COMPLETE end-to-end (F.E8 verifies STRONG); attribution is STARVED at source (Revenue tables empty locally per F.D1 pattern; ClosePack `sent`/`won`/`lost` unreachable per F.D10). F.E1 extends F.D10 to `OpportunityRevenue` + `OpportunityOutcome` (arc-wide 3-model over-modeling pattern). F.E7 refines F.D4: 6 HAI writers exist at `core.py:1561/:1673/:2051/:2117/:2237/:2361` but RUNTIME-DORMANT via F.C6 (`run_ops_autopilot` deferred per AUDIT_FINDINGS.md #12).
- **Load-bearing findings (10 F.E findings + 2 parent-doc anchor corrections).**
  - **F.E1 Over-modeled STATUS_CHOICES arc-wide (extends F.D10; CONFIRMED HIGH):** 3 revenue-domain models. OpportunityRevenue REVENUE_STATUS_CHOICES: 5 declared / 1 reachable (only `'received'`). OpportunityOutcome OUTCOME_CHOICES: 5 declared / 2 reachable (`won`+`lost`). Combined with ClosePack (S1404 F.D10): 16 declared / 6 reachable / 10 UNREACHABLE (62%).
  - **F.E2 Phantom field references (4 sites; CONFIRMED HIGH; MUST-FIX per Rigby Batch 1):** Readers/writers touch fields that DON'T EXIST in schema — deterministic runtime errors: (a) `ml_scoring_engine.py:1240-1242` `.filter(recorded_at__gte=cutoff)` — FieldError; (b) `event_handlers.py:290-292` `.filter(actual_outcome__isnull=False)` — FieldError; (c) `epa_handlers_tools.py:3583-3593` `.create(notes=...)` — TypeError; (d) `epa_handlers_tools.py:3727-3730` `revenue.metadata['linked_content_id']` — AttributeError. Blast radius LOW-TO-ZERO currently per F.D1 pattern; latent.
  - **F.E3 Dual-representation drift extends S1401 D6 to Revenue (CONFIRMED HIGH with Rigby cycle 1 framing refinement):** Two disconnected pipelines. Core has Revenue + OpportunityRevenue (`:2613`) + OpportunityOutcome (`:3394`); intelligence has parallel RevenueSource + RevenueRecord + ProposalTracker + RevenueDashboardMetrics at `intelligence/revenue_tracking_bridge.py:16-108`. `revenue_attribution_bridge.py:227` post_save fires on core Revenue only. **Rigby Batch 1 framing refinement:** dual-schema pattern MAY be intentional (core = finalized accounting truth; intelligence = external attribution ingestion); if intentional, gap reframes to "missing explicit contract + mapping + source-of-truth hierarchy" (R.E-3 ADR scope revised — see §19 audit).
  - **F.E4 Parent-doc anchor correction #1 (CONFIRMED):** Parent §3.E line 431 named 4 frontend routes — ZERO exist in `frontend/src/App.tsx`. Corrections landed at S1405 commit-time.
  - **F.E5 Duplicate view file endpoint pairs (CONFIRMED HIGH):** `views_revenue.py` + `views_revenue_tracking.py` provide duplicate POST create + GET summary/stats pairs with different models + URL namespaces. `views_revenue_tracking.py`: ZERO docstrings on 4 class-based views + calls MISSING `Revenue.get_user_total()` method.
  - **F.E6 Parent-doc anchor correction #2 (CONFIRMED):** Revenue attribution algorithm NOT at `ops_autopilot/revenue.py`; actual at `ops_autopilot/impact.py:1233-1290`. Correction landed at commit-time.
  - **F.E7 F.D4 refinement (CONFIRMED — code-exists-but-dormant, arc-wide):** S1404 F.D4 empirical HAI-missing at runtime refined at code layer: HAI writers exist at 6 sites in `core.py` (`:1561` impact_portfolio, `:1673` attribution_debt, `:2051` revenue_pipeline, `:2117` outbound_leads, `:2237` release_governor, `:2361` policy_arbitrator). Runtime-dormant via F.C6.
  - **F.E8 S1274 §2.4 STRONG classification verified end-to-end (CONFIRMED):** Revenue → Observability via ImpactEvent chain fully verified.
  - **F.E9 S1274 §4.3 revenue_attribution_bridge verified with 2-path mechanism (CONFIRMED):** `revenue_attribution_bridge.py:227` @receiver(post_save, sender=Revenue) → UserAgentLearning writes at `:147` (learning_domain='revenue_optimization') + `:181` (learning_domain='success_factors'). Docstring drift: "Feeds insights to UnifiedLearningPipeline" unfulfilled.
  - **F.E10 Runtime owner absent arc-wide (CONFIRMED HIGH; S1274 §14 #36 answer):** Zero JobContract / AGENT_MAP / task_routes / dedicated queue. Only PA tool `revenue_tracker_tool`. Cat E owns arc-wide synthesis per parent D28.
- **Verifier-loop discipline extension:** 12/12 parent-Claude direct-read checkpoints CONFIRM sub-agent claims (matches S1404 12-checkpoint count). New pattern: **broadened-grep with model-context disambiguation** — F.E1 `outcome='partial'` grep returned hits on `PilotExecution` (unrelated) at `tasks.py:6631` + `tasks_misc.py:162`; parent-Claude direct-read disambiguated as false positives, upholding OpportunityOutcome `partial` = UNREACHABLE.
- **Inherited findings status (parent §11.4 + S1401/S1402/S1403/S1404).** S1274 §2.4 line 292 STRONG (F.E8 VERIFIED). S1274 §2.4 line 294 REFINED via F.E7 (code-exists/runtime-dormant, arc-wide). S1274 §14 #36 CONFIRMED at Cat E code layer (F.E10). S1274 §4.3 CONFIRMED with 2-path mechanism (F.E9). S1274 §9.6 LOW readiness CONFIRMED (F.E3 + F.E5 + F.E10 all argue LOW). S1273 §10.3 UNKNOWN #3 (attribution algorithm) RESOLVED via F.E6. S1399 F1 methodology inherited; F.E2 is a MORE SEVERE variant (readers filter on fields that don't exist). S1401 §14 D6 dual-representation extended to Revenue via F.E3. S1404 F.D4 refined via F.E7. S1404 F.D10 extended arc-wide via F.E1 to 3-model pattern.
- **Dependencies.**
  `1400_revenue_domain_scoping.md` (parent — §3.E anchor-corrections landing here + §11.4 15 inherited findings + §12.1 Category E questions); `1401_revenue_opportunity_discovery_scoring_audit.md` (sibling — §9 integration map + D6 dual-representation methodology); `1402_revenue_outreach_composition_delivery_audit.md` (sibling — §9 integration map + F.B4 declared-not-realized lens); `1403_revenue_engagement_inbound_audit.md` (sibling — §9 integration map + F.C6 deferred-by-policy); `1404_revenue_meeting_close_audit.md` (sibling — §9 integration map + F.D4 arc-wide HAI missing + F.D10 state-machine PARTIAL + §20.10 anchor-corrections pattern); `platform_architecture_inventory.md` §3.32 + §4.9 [S1273]; `platform/cross_domain_integration_audit.md` §2.4 line 292 + §4.3 + §14 #36 [S1274]; `domains/memory/1399_memory_canonical_summary.md` §4 F1/F2/F3/F4 [S1399 methodology inheritance]; `docs/AUDIT_FINDINGS.md` §12 [F.E7 policy-hook deferred classification source].
- **Recommended next reads.** **S1406 Child F Freelance/Gig Opportunity subsystem (Income/Jobs lane per D25 F.i lock)** next per parent §5 mission sequence. Category F inherits Cat E's F.E10 arc-wide runtime-owner-absent finding + F.E1 STATUS_CHOICES pattern check for `FreelanceOpportunity` + 9-file `intelligence/` adjacency runtime-liveness probe. Also queued: **R.E-1 Revenue Employee JobContract ADR** (F.E10); **R.E-2 view-file consolidation ADR** (F.E5); **R.E-3 dual-representation reconciliation ADR** (F.E3, two-part: 3a framing decision, 3b remediation); **R.E-4 STATUS_CHOICES cleanup ADR arc-wide** (F.E1 3-model); **R.E-5 F.E2 phantom-field fix PR** (LOW-effort MUST-FIX); **R.E-6 F.C6 run_ops_autopilot enable-decision ADR** (from S1403; Cat E adds attribution-debt angle); **R.E-7 `intelligence/revenue_integration.py` completion or scope-reduction ADR** (T.E7).
- **Overall importance.** **Fifth Group 1400 child audit; first library audit to complete an arc-wide 3-model over-modeling pattern** (F.E1 extends F.D10 to OpportunityRevenue + OpportunityOutcome across ClosePack; 16 declared / 6 reachable / 10 UNREACHABLE combined). Also first library audit to surface **a new class of drift worse than S1399 F1** — F.E2 phantom-field references where readers filter on fields that don't exist in schema (deterministic runtime errors, latent only because tables are empty). Group 1400 arc convergence extended: S1404 §20.11 trajectory "activate lifecycle + enforce approval/attention gating" gains 5th pillar from S1405 — "consolidate revenue write path + assign runtime owner + fix phantom-field bugs." S1499 xx99 unified remediation plan candidates named across 5 tracks in §20.5 arc trajectory draft.
- **Distinguishing property.** **First library audit to ship with partial SIGN cycle 1** — Rigby SIGN worker instability across two fresh isolation pins blocked batches 2-3 (F.E4-F.E10) after substantive Batch 1 pressure-test on F.E1-F.E3. D45 Chris ratification option (ii) accepted Batch 1 verdict as SIGN-with-edits cycle 1; batches 2-3 deferred to follow-up SIGN addendum. Parent-Claude 12/12 verifier-loop discipline as compensating quality gate. Also **first library audit to fold Rigby framing refinement at commit-time on F.E3 dual-representation** (added "possible intentional dual-schema" alternative interpretation to F.E3 statement + revised R.E-3 ADR scope to include framing decision as step 3a before remediation step 3b). Both SIGN pins retire post-PR-merge per playbook §15. Memory rules triggered: `feedback_rigby_deliverable_content.md` (placeholder-stall observed on first pin) + `feedback_rigby_tool_verification.md` (verbose tool block confirmed full read despite narrative claim of partial retention).

### 1.28 `domains/revenue/1406_revenue_freelance_gig_income_jobs_audit.md`

- **Title.** Group 1400 Revenue — Category F: Freelance / Gig Opportunity subsystem / Income-Jobs lane (Child audit under Group 1400 Revenue arc)
- **Purpose.** **Sixth (and final) child audit under Research Group 1400 Revenue (parent §1.22).** Category F Freelance / Gig — Income-Jobs lane exclusive scope per parent §3 Cat F evidence surface + D25 F.i Chris-lock (Income/Jobs lane, not just FreelanceOpportunity model) + parent §12.1 Category F F.iii questions. Verifies `FreelanceOpportunity` model (`core/models_autonomous_situations.py:352-401`) + 9-file `intelligence/` adjacency (`ai_job_matcher.py`, `ai_job_application_pipeline.py`, `agent_income_tools.py`, `income_builder.py` shim, `income_builder_automation.py`, `income_builder_connector.py`, `income_spider_orchestrator.py`, `job_income_bridge.py`, `job_scanner_consumer.py`) + `ai_resume_generator.py` + adjacent `ai_core/intelligence/income_builder.py` canonical + `intelligence/spider_decision_bridge.py` (dominant Opportunity writer at 2630/2631 rows locally). Completes arc-wide F.E10 ownership synthesis (Cat F half per D28). Grounded in verified runtime evidence at `main` HEAD `752a27aa`.
- **Status.** Draft → Active on Chris merge (Rigby SIGN-with-edits cycle 1 substantive on fresh isolation pin `pa-8660ea7cfecd4bc6` batches 1-3 delivered; batch 4 S1405 F.E4-F.E10 deferred addendum BLOCKED by worker-instability recurrence; D50 Chris ratification (i) accepts SIGN-with-edits cycle 1 + D51 Chris ratification (i) defers batch 4 to S1499 xx99 synthesis via "agree all" 2026-07-01). Pin retires post-PR-merge per playbook §15.
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: research`, `category: child_audit`.
- **Primary questions answered.** All parent §12.1 Category F F.iii questions:
  - **Is the Income/Jobs lane actively driving income or dormant?** DORMANT LOCAL. `FreelanceOpportunity.objects.count() = 0`; income_spider_orchestrator beat-scheduled but 0 rows via provenance stamp locally; application submission simulated; deprecation shim on canonical writer path. Cat F ships code across 10 files but produces no observable local income signal.
  - **Who produces FreelanceOpportunity rows?** Currently no one. Declared writer at `core/tasks_ops.py:2239-2251` would raise `FieldError` on execution (F.F1 phantom fields: 5 non-existent fields unguarded). No other writer exists.
  - **What is income_builder_automation + income_spider_orchestrator + job_income_bridge doing at runtime?** income_builder_automation writes filesystem-only execution logs; income_spider_orchestrator beat-scheduled hourly but 0 rows via provenance stamp locally; job_income_bridge cache-only transform, zero production callers.
  - **Is ai_resume_generator production-invoked?** NO with high confidence. Called only by dormant paths (real_execution_engine + ai_job_application_pipeline both not invoked from production).
  - **Inherited from S1405 — How does Cat F reason about F.E10 arc-wide runtime-owner-absent finding?** F.F3 CONFIRMS F.E10 at Cat F code layer (zero JobContract/AGENT_MAP/PA tool/dedicated queue for the 10-file lane). Completes arc-wide synthesis: Revenue (Cat E half) + Income/Jobs (Cat F half) surface has NO organizational owner across 20+ writer sites, 30+ services, 6 entry-point paradigms. S1499 xx99 owns final remediation-plan track.
  - **Inherited from S1405 — Does Cat F exhibit F.E1 / F.E2 / F.E3 patterns?** YES to all three. F.F5 extends F.E1 (`OpportunityActionPlan` 11 declared / 3 reachable = 27% reachability, WORSE than S1405 arc-wide 37.5%). F.F1 extends F.E2 (5 phantom fields UNGUARDED, WORSE than S1405's 4 hasattr-guarded). F.F2 extends F.E3 (multi-writer convergence on `Opportunity` — 20 files call `.create()`, 1 dominant writer at 99.96%, no canonical write-authority contract).
- **Load-bearing findings (10 F.F).** F.F1 phantom-field writer (arc-wide F.E2 extension, worse-than-E variant); F.F2 multi-writer convergence on `Opportunity` (arc-wide F.E3 extension, multi-writer variant); F.F3 arc-wide runtime-owner-absent Cat F half (completes F.E10 synthesis); F.F4 three orthogonal dead-code patterns co-locate (deprecation shim + view null-check stub + Flask demo — split into 4a/4b/4c sub-findings per Rigby fold); F.F5 STATUS_CHOICES over-modeling extends F.E1 to intelligence-side; **F.F6 learning-loop-missing arc-wide MUST-FIX** (Rigby SIGN Batch 2 upgrade — north-star blocker; without outcomes cannot tune prompts, ranking, or ROI); F.F7 Redis pub-sub orphan channels (new pattern to Group 1400 arc); F.F8 frontend disconnection (extends F.E4 parent-doc frontend-routes drift methodology); **F.F9 LLM max_tokens floor risk UPGRADED to HIGH** (Rigby SIGN Batch 3 borderline resolved via parent-Claude direct-verify of `core/llm_enforcer.py:232` `downgrade_model = 'gpt-5-mini'` confirmed wired); F.F10 model placement drift (LOW informational; supporting evidence for F.F3).
- **Verifier-loop discipline extension.** 12 direct-read/direct-grep/direct-ORM checkpoints applied to sub-agent claims BEFORE Rigby SIGN. **10 CONFIRM + 2 DISAMBIGUATION.** New pattern: **provenance-stamp ORM probe as disambiguation tool** — Agent 4 claim "beat schedule fires hourly and writes 20 opportunities to Opportunity via income_spider_orchestrator.py:462" was REFINED not REFUTED via ORM row-count filter on `metadata__created_via='income_spider_orchestrator'` = 0. Local DB dominant writer is `intelligence/spider_decision_bridge.py` (2630 rows). Extends S1401-S1405 verifier-loop tools with ORM-provenance disambiguation.
- **Inherited findings status (parent §11.4 + S1401/S1402/S1403/S1404/S1405).** All 15 parent-inherited findings + 5 arc-wide S1401/2/3/4/5 patterns applied as diagnostic lenses; Cat F extends 5 of them (F.E1/F.E2/F.E3/F.E10 explicitly + F.D1 empty-tables + F.D4 HAI arc-wide) and confirms 0 new contradictions.
- **Dependencies.**
  `1400_revenue_domain_scoping.md` (parent — §3.F Cat F evidence surface + §11.4 15 inherited findings + §12.1 Category F questions + D25 F.i Chris-lock); `1401_revenue_opportunity_discovery_scoring_audit.md` (sibling — §14 D6 dual-representation methodology extended by F.F2); `1402_revenue_outreach_composition_delivery_audit.md` (sibling — §9 integration map + F.B4 declared-not-realized lens analog); `1403_revenue_engagement_inbound_audit.md` (sibling — §9 integration map + F.C6 deferred-by-policy pattern); `1404_revenue_meeting_close_audit.md` (sibling — §9 integration map + F.D1 runtime-empty-local + F.D10 state-machine PARTIAL); `1405_revenue_attribution_analytics_audit.md` (sibling — §14 F.E1 + F.E2 + F.E3 + F.E10 all extended); `platform_architecture_inventory.md` §3.32 + §4.9 [S1273]; `platform/cross_domain_integration_audit.md` §2.4 line 294 + §14 #36 [S1274]; `AUDIT_FINDINGS.md` #12 [F.C6 pattern reference].
- **Recommended next reads.** **S1499 xx99 Group 1400 canonical summary** next per parent §5 mission sequence P7 slot (final Group 1400 session). Cat F contributions to S1499 §8 follow-on queue: T6 Income/Jobs Employee JobContract ADR (paired with S1405 T2 Revenue Employee — single-merged vs two-sibling decision); T7 multi-writer convergence contract for `Opportunity`; T8 phantom-field remediation (LOW-effort MUST-FIX); T9 deprecation shim retirement + 45-file migration; T10 Redis pub-sub schema contract. Also owed at S1499: playbook §11.3 §10 meta-methodology section (second application after S1399 close); ORM-provenance disambiguation codification candidate for playbook v3 §14 if S1500 second-application preserves.
- **Overall importance.** **Sixth Group 1400 child audit; completes Group 1400 arc trajectory.** Categories A/B/C/D/E/F all shipped; S1499 xx99 owns final synthesis. **First library audit to complete arc-wide F.E10 ownership synthesis** — F.F3 confirms Cat F half; Cat E owned first half (S1405). **First library audit to extend F.E1/F.E2/F.E3 to a third domain lane** (Income/Jobs on top of Revenue's core + intelligence). **First library audit to apply S1405 D48 stability-probe gate** — fresh SIGN pin's first-turn generic-error triggered S1405 D45 recovery-pattern warmup-ping ("Ready" response); three batches delivered substantively before Batch 4 hit worker-instability recurrence. **Group 1400 arc close trajectory statement:** "Categories A-F now all shipped; consistent pattern: at every stage of lead → attribution lifecycle, Revenue domain has (i) more code than runtime signal, (ii) more declared entry points than production traffic, (iii) more STATUS_CHOICES states than reachable transitions, (iv) more model schemas than canonical write paths, (v) more scheduled Celery tasks than owned JobContracts. S1499 synthesizes 'activate the entire Revenue + Income/Jobs lifecycle + establish canonical ownership' remediation plan (T1-T10, 10 tracks: 5 from S1405 §19 + 5 from S1406 §19.8)."
- **Distinguishing property.** **First library audit to introduce provenance-stamp ORM probe as new verifier-loop disambiguation tool** — extends S1401-S1405 verifier-loop tool chain (file-line direct-reads, broader-grep, model-context disambiguation) with ORM-provenance disambiguation. Also **first library audit to fold Rigby SIGN into 3 substantive batches after single fresh-pin generic-error recovery** — D48 stability-probe gate application; Batches 1-3 substantive with 10 framing refinements + 2 severity upgrades (F.F6 MUST-FIX + F.F9 HIGH); Batch 4 deferred per D45+D48 fallback discipline. Also **first library audit to complete an arc-wide 5-pillar convergence synthesis at a child audit level** (rather than at xx99 summary) — Cat F's 10 F.F findings enumerate the 5 pillars extended from prior categories with no residual gaps to xx99 xx99 synthesis on those 5 pillars (S1499 owns unified remediation plan; not pattern-identification). Memory rules triggered: `feedback_verify_before_deleting_dead_code.md` (F.F4 anti-pattern guard applied to shim + null-check stub + Flask demo); `feedback_fleet_caller_verification_before_celery_deletes.md` (F.F4c fleet-app verification deferred to S1499 T9); `feedback_gpt5_max_completion_tokens_floor.md` (F.F9 direct-verify triggered severity upgrade); `feedback_procfile_makefile_queue_parity.md` (F.F3 queue verification); `feedback_rigby_sign_worker_instability_recovery.md` (Batch 4 worker instability triggered D45 recovery + D48 fallback (iii)); `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` (fresh-pin generic-error on turn 1 recovered via warmup ping). SIGN pin `pa-8660ea7cfecd4bc6` retires post-PR-merge per playbook §15.

### 1.29 `domains/revenue/1499_revenue_canonical_summary.md`

- **Title.** Group 1400 Revenue / Outreach / Engagement — Canonical Summary (arc-close per playbook §17 graduation)
- **Purpose.** **xx99 canonical summary closing Research Group 1400 (Revenue / Outreach / Engagement).** Consumes S1401-S1406 6-child audit outputs + parent §12.5 F.iii Revenue Lifecycle Traceability Table requirement. Produces cross-cutting synthesis: consolidated domain shape (§3 including 9-stage traceability table), 5 arc-wide cross-cutting patterns (§4), resolved contradictions including D54 fold of S1405 F.E4-F.E10 addendum (§5), anchor-update recommendations (§7), unified T1-T10 follow-on queue (§8), Employee OS + Group 1700 delegated arcs (§9), meta-methodology retrospective as second application of playbook §11.3 §10 template after S1399 close (§10). Grounded in child-audit source-anchor citations; no new §13 sweep per playbook §11.3 bounded-work rule.
- **Status.** `status: active` on Chris commit-gate 2026-07-01 (Rigby SIGN-with-edits cycle 1 substantive via fresh isolation pin `pa-877f1919efaa48e4` retired post-fold — 22 verdicts / 22 CONFIRM / 0 FLIP / 10 FLAG-EDIT framing refinements folded at commit-time; 0 must-fix; 0 severity flips; D48 stability-probe gate + warmup-ping + D45 titles-only recovery pattern successfully recovered from first-turn worker-instability; matches S1399 SIGN-clean cycle 1 pattern).
- **Research type.** Canonical summary (playbook §11.3 12-section template). `authority: research`, `category: canonical_summary`.
- **Primary questions answered.** All parent §12.1 arc-level questions:
  - **Which of the 15 inherited findings from S1274 changed under child-audit evidence?** §5.1 aggregation: all 15 hold as canonical baseline; zero inverted; 2 refined (#5 outbound channel broadening + #7 sports lane clarification).
  - **What are Revenue's F1/F2/F3/F4 diagnostic-lens hits cross-arc?** §4 identifies 5 arc-wide patterns: F2 orphan-write (8 sites unanimous); F1 provenance-filter drift (2 sites narrow-scope); state-machine incomplete (4 models 62% unreachable); learning-loop incomplete (3 sites 2-bucket split); runtime-owner MISSING (UNANIMOUS 6/6 — arc headline).
  - **What integration seams did children discover S1274 didn't name?** §5.2 parallel-schema umbrella (F.A1 + F.E3 + F.F2 with 2 subcases: domain modeling divergence + realtime representation divergence); 20-writer convergence on Opportunity (F.F2); ContentEngagement ↔ EngagementEvent orthogonal-axes (F.C4); Income lane orphaned (F.F6).
  - **Arc-wide runtime owner recommendation?** §3.4 + §8 T2/T3: D55 (ii) two sibling JobContracts (Revenue Employee for Cat A/B/C/D/E + Income/Jobs Employee for Cat F) — Chris-ratified 2026-07-01; T3 Income/Jobs SPEC'D but not activated per T4 R.F3 = (b) dormant-planned lock.
- **Load-bearing deliverables.** §3.2 Revenue Lifecycle Traceability Table (9 stages, minimum 8 per parent §12.5 F.iii; 4 CRITICAL-INCOMPLETE stages, 5 LIVE-BUT-DRIFTING, 0 CLEAN-END-TO-END); §4.1-§4.5 5 arc-wide patterns; §5.4-§5.7 D54 fold of S1405 F.E4/E5/E6/E10 addendum with residual-risk auditability note; §7 anchor-updates (6 §3.32 corrections + §4.9 outbound broadening + NEW `docs/topics/revenue-pipeline.md`); §8 T1-T10 unified queue with TIER structure (T1 parallel-schema/source-of-truth; T4 R.F3 dormancy Chris-locked (b); T5 delivery+ingestion sequential ADR pair; T6 HAI interlock ship-to-go-live prerequisite; T7 write+routing authority framework PROMOTED to TIER 2; T8 state-machine completion; T2/T3 Employee OS runtime-owner; T9 phantom-fix; T10 Celery routing); §10 meta-methodology 4 new candidate patterns for playbook v3 codification (D48 + D45 + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent MET at 3-arc threshold).
- **Verifier-loop discipline.** Parent-Claude 12-checkpoint verifier-loop pre-SIGN caught 4 corrections + folded (impact.py path prefix correction to `core/services/ops_autopilot/impact.py`; F2 count 7 → 8 sites; §4.5 finding-number attribution replaced with §18 ownership-gap refs; §11.1 PR numbers S1401=#2788 + S1402=#2789; §7.2 Employee OS count 4→6 with CLAUDE.md 3-vs-4 drift flagged for verify_doc_claims subsequent PR).
- **Inherited findings status (parent §11.4 15 findings from S1274).** §5.1 aggregation: 15/15 hold; 2 refined (broadened): #5 Revenue → Inbox scope broadens to "any outbound channel" per F.B1; #7 sports lane clarified as parallel (`OpportunityTracking`) — mainline untouched. Zero S1274 findings inverted, downgraded, or invalidated.
- **Dependencies.**
  `1400_revenue_domain_scoping.md` (parent — §5 P1→P7 sequence + §11.4 15 inherited findings + §12.1 category questions + §12.5 F.iii traceability table spec); `1401_revenue_opportunity_discovery_scoring_audit.md` (Child A); `1402_revenue_outreach_composition_delivery_audit.md` (Child B); `1403_revenue_engagement_inbound_audit.md` (Child C); `1404_revenue_meeting_close_audit.md` (Child D); `1405_revenue_attribution_analytics_audit.md` (Child E — F.E4-F.E10 D54 fold at §5.4-§5.7); `1406_revenue_freelance_gig_income_jobs_audit.md` (Child F); `platform_architecture_inventory.md` §3.32 + §4.9 [S1273]; `platform/cross_domain_integration_audit.md` §2.4 line 293-294 + §14 finding #36 [S1274]; `domains/memory/1399_memory_canonical_summary.md` [first application of playbook §11.3 §10 template; S1499 is second application].
- **Recommended next reads.** Post-arc design-preparation phase T1-T10 landing (Chris ratifies sequence + cadence at post-arc kick-off); Employee OS 1200s arc for T2 Revenue Employee + T3 Income/Jobs Employee (spec'd not activated per T4 R.F3 (b) dormant-planned lock); Group 1500+ Sports/DBAO/Intelligence (playbook §22 next-arc queue; second application of Chris's Phase 0 F.i/F.ii/F.iii methodology per S1400 D29 two-triggers gate). Also owed post-arc: `docs/topics/revenue-pipeline.md` first-inventory landing subsequent PR; verify_doc_claims verifier PR for CLAUDE.md 3-employee narrative anchor drift (actual: 4 per S1406 §5.4).
- **Overall importance.** **First formal Group 1400 arc-close in the library.** 8 docs total (parent + 6 child audits + this canonical summary); ~11,715 lines across arc corpus. **First library canonical summary to arc-close with 4 of 9 lifecycle stages CRITICAL-INCOMPLETE** — Revenue pipeline emits scored opportunities but nothing beyond spider → scoring → draft composition converts to Revenue at mainline layer (Stage 4 delivery MISSING, Stage 5 ingestion MISSING, Stage 8 Revenue Received latent). **First library arc-close to resolve arc-wide runtime-owner MISSING UNANIMOUS 6/6 with a peer-sibling JobContract shape** — D55 (ii) two sibling JobContracts (Revenue Employee + Income/Jobs Employee) precedent (contrast: S1304 §18 Documentation Manager AIEmployee single-employee shape). **Second application of playbook §11.3 §10 meta-methodology template** — all 5 S1399-codified patterns REPLICATED in Group 1400; 4 new S1499 candidate patterns pending third-arc validation (D48 stability-probe gate + D45 recovery pattern + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent MET at 3-arc threshold, recommended for immediate codification).
- **Distinguishing property.** **First library canonical summary to fold Rigby SIGN worker-instability recovery pattern at the xx99 level itself** — S1499 SIGN pin `pa-877f1919efaa48e4` first-turn triggered ~2400-word batch → worker instability → D45 recovery to titles-only 2-3-verdict batches → 22/22 CONFIRM delivered across Q10-Q13; matches S1406 D48 stability-probe gate precedent. Also **first library canonical summary to fold a prior child's SIGN-blocked addendum at §5 synthesis** — D54 fold of S1405 F.E4-F.E10 (worker-instability blocked Batches 2-3 at S1405 close → deferred through D45/D51 → landed at §5.4-§5.7 via parent-Claude 12/12 compensating quality gate + sibling cross-verification from S1404 F.D4/D5/D8 anchor-drift pattern + S1406 F.F3 arc-wide runtime-owner completion). Memory rules triggered: `feedback_xx99_meta_methodology_section.md` (§10 second application confirms non-negotiable status); `feedback_docs_cascade_at_every_close.md` (post-merge 4-step cascade + `build_docs_provenance` required); `feedback_rigby_sign_worker_instability_recovery.md` (S1499 SIGN pin worker-instability recovery via titles-only batches); `feedback_verify_before_deleting_dead_code.md` (T4 R.F3 (b) dormant-planned lock preserves F.F4a/b/c dormancy sub-patterns pending activation gate — not decommission). SIGN pin `pa-877f1919efaa48e4` retired post-fold. Arc pin `pa-34d43795e1b24bd3` retired at arc-close per playbook §16 (`updated_count: 60`). Index v26 updated per §10.1 (this row + §1.29 row + frontmatter v26 preamble + §8 timeline S1499 row).

### 1.30 `domains/sports/1500_sports_domain_scoping.md`

- **Title.** S1500 Sports/DBAO/Intelligence — Parent Architecture Scoping (Group 1500 mission plan)
- **Purpose.** **Arc-opening parent scoping doc for Research Group 1500 Sports / DBAO / Intelligence.** SECOND application of Chris's Phase 0 F.i/F.ii/F.iii methodology (Domain Definition / Existing Knowledge Inventory / Success Criteria) at §10/§11/§12 — applied UNCHANGED per D58 to preserve playbook v3 §11.1 template promotion trigger per S1400 D29 two-triggers rule. Answers two Phase 0 questions: (1) is Sports one domain or a parent capability composed of subdomains; (2) how does the arc route the S1274 §12.3 island-vs-integrated posture-decision evidence plan.
- **Status.** `status: active` on Chris commit-gate 2026-07-01 (Rigby pre-ratification pressure-test folded pre-draft — 4 refinements landed: D-4 wording → D59 refinement (posture decision framing + evidence plan, not recommendation); Rigby caution 1 (repeatability + discriminative value) → §12.4 explicit criterion; Rigby caution 2 (over-loading Phase 0) → D59 + §12.6 boundary; Rigby caution 3 (Intelligence scope-magnet) → D60 + §3 + §7 + §10.1 bounding). Fresh SIGN isolation pin owed post-anchor-updates per playbook §15 with D48 preemptive stability-probe gate per S1405+S1406+S1499 3-arc pattern.
- **Research type.** Parent doc (playbook §11.1 template with §10/§11/§12 Phase 0 methodology sections added per S1400 precedent). `authority: parent-doc + Phase 0 methodology second application`, `category: parent_scoping`.
- **Primary questions answered.**
  - **Is Sports one domain or parent-with-children?** §4 verdict: **parent-with-children (D57 Chris-locked 2026-07-01).** Surface size (5 models across 2 files + 4 services + 5 spiders + 4 market agents + 6 Celery tasks + 9-tab UI + discrete DB schema + WebSocket namespace) too big for single audit; multiple S1273 rows implied (§3.10 + §9 #4 mission); cross-domain lens is central (Category F posture-decision).
  - **Does DBAO exist as a first-class Django app?** §2.5 verified evidence: NO — DBAO is a materialized product-line codename (per D61 option (a) "Donkey Betz Analytics Ops") with 4 concrete artifacts (PostgreSQL `dbao` schema + `/ws/dbao/` WebSocket namespace + `VITE_DBAO_API_URL` env-var namespace + `X-DBAO-Client` HTTP header); NOT a mounted Django app; NOT an App.tsx route.
  - **Is `sports_odds` a valid `SignalCluster.pattern_type`?** §2.5 + §11.1: NO — Signal Engine declares 10 canonical `SignalCluster.pattern_type` values at `core/models_signal_intelligence.py:75-86`; `sports_odds` valid only on legacy `SpiderData.data_type`. Confirms S1274 §14 Finding #6 (HIGH) at code level.
  - **How does the arc route the posture decision?** §12.1 + D59: Phase 0 frames the posture question and specifies the evidence plan; children (P1-P6) gather evidence; xx99 (S1599) consolidates into Chris-gated decision brief; Chris picks posture in post-arc ADR. NOT posture recommendation at Phase 0.
- **Load-bearing deliverables.** §3 Six candidate subdomain categories A-F + explicit non-candidates (mobile-app deep audit; Odds API vendor selection; betting UX design; non-sports intelligence per D60; BILLING_MONETIZATION external companion; body-system integration; general SignalCluster/Memory refactoring); §4 parent-with-children verdict with evidence FOR and AGAINST rejected; §5 locked child mission sequence P1 S1501 Cat A → P2 S1502 Cat B → P3 S1503 Cat C → P4 S1504 Cat D → P5 S1505 Cat E → P6 S1506 Cat F (LAST — consumes P1-P5 evidence for posture-decision framing) → P7 S1599 xx99; §6 12 parked candidate issues (owed to specific children or xx99 or delegated to S1300 Memory / Group 1600 Content); §7 8-item anti-scope; §8 D56-D61 six ratified decisions; §10 F.i domain definition (Sports = platform's betting-analytics product-line materialized as DBAO PostgreSQL schema + `/ws/dbao/` WebSocket namespace) + boundary conditions + runtime shape confirmation via §10.2 "island posture already partially adopted at runtime layer"; §11 F.ii existing knowledge inventory (6 prior findings assigned to children + docs corpus state + runtime evidence anchors); §12 F.iii success criteria (10 arc-close deliverables owed to xx99 + 5 quality bars + §12.3 3 Rigby caution folds + §12.4 discriminative-value criterion for v3 promotion stricter than "ran twice" + §12.5 Sports Domain Lifecycle Traceability Table requirement matching S1400 §12.5 pattern).
- **Verifier-loop discipline.** Runtime evidence anchored via **two parallel Explore sub-agent sweeps at S1500 open against `main` HEAD `f7704586`** (sports subsystem inventory + DBAO/intelligence inventory). Every §2.5 file:line cite verified twice (Explore agent + spot-check). Fresh SIGN isolation pin cycle owed post-anchor-updates.
- **Inherited findings referenced.** S1273 §3.10 Sports Intelligence / Betting Pipeline (LIGHT); S1274 §14 Finding #6 (HIGH, `sports_odds` not SignalCluster.pattern_type); S1274 §12.3 P1 Product/Architecture Decision Point with 2-posture success criteria; S1273 §9 #4 Sports/DBAO ↔ AI Studio Integration Sketch as P1 mission #4. All 4 assigned to Category F evidence plan.
- **Dependencies.**
  `DOMAIN_RESEARCH_PLAYBOOK.md` (§11.1 template + Phase 0 second application); `RESEARCH_OPERATING_SYSTEM.md` (§8 arc-open contract); `OPEN_ARCS.md` (Group 1400 → Group 1500 handoff); `platform_architecture_inventory.md` §3.10 + `platform/cross_domain_integration_audit.md` §3.10/§12.3/§14 #6 [S1273 + S1274]; `domains/memory/1300_memory_domain_scoping.md` (parent-with-children exemplar); `domains/memory/1399_memory_canonical_summary.md` (first xx99 canonical summary); `domains/revenue/1400_revenue_domain_scoping.md` (first application of Phase 0 F.i/F.ii/F.iii — trigger 1 of two-triggers rule); `domains/revenue/1499_revenue_canonical_summary.md` (second xx99 + second application of §11.3 §10 meta-methodology template).
- **Recommended next reads.** **S1501 Child A Sports Odds Ingestion & Normalization** next per parent §5 mission sequence P1 slot. Load-bearing S1500 outputs to inherit at child sweeps: §2.5 verified evidence tables (runtime baseline); §3 category boundaries (avoid cross-category scope drag); §6 parked candidate issues per category; §11.1 6 prior findings pre-assigned. If Chris opens Group 1600 (Content) parallel, S1500 §6 flags a Cat D delimiter question delegated to that arc.
- **Overall importance.** **First library arc-open to explicitly test playbook v3 §11.1 promotion trigger per S1400 D29 two-triggers rule.** Group 1500 close (S1599 xx99) determines whether Chris's Phase 0 F.i/F.ii/F.iii methodology promotes to playbook v3 §11.1 template addition. Rigby caution 1 folded into §12.4: promotion criterion is stricter than "ran twice" — xx99 §10.2 must demonstrate concrete discriminative-value evidence (scope confusion prevented + rework reduced + cleaner arc close + Chris-lock efficiency). **First library parent scoping doc to route a Product/Architecture Decision Point (S1274 §12.3) as a load-bearing lens question via evidence-plan framing (not recommendation).** D59 Rigby refinement folded: Phase 0 frames + specifies evidence; children gather; xx99 consolidates; Chris picks posture in post-arc ADR. **First library parent scoping doc to identify architecture isolation at the runtime layer as evidence for the posture question** — §10.2 confirms Sports has its own PostgreSQL schema (`dbao`) + WebSocket namespace (`/ws/dbao/`); island posture is not hypothetical but already partially adopted at runtime.
- **Distinguishing property.** **First library parent scoping doc drafted with Chris ratification via a single governance decision request** (`81d7467e-add6-420f-aee9-60b67d7867e8` — governance_tool `decision_create` + `decision_decide` approve) — matches Rigby's PA tool surface for structured ratification with formal `acted` status. **First library parent scoping doc to fold Rigby's pre-ratification pressure-test as 4 wording/scope refinements before Chris ratification** (D59 wording refinement; §12.4 criterion; §12.6 boundary; D60 scope-magnet bounding). **First library arc-open to reference a paused parallel Claude Code session as memory-rule evidence** — memory rule `feedback_no_parallel_research_arcs.md` referenced at Appendix; Chris cleanly aborted the parallel S1500 attempt before landing partial doc, so S1500 opened with sole focus. Memory rules triggered: `feedback_no_parallel_research_arcs.md` (parallel session aborted); `feedback_docs_cascade_at_every_close.md` (post-merge 4-step cascade + `build_docs_provenance` required); `feedback_rigby_sign_worker_instability_recovery.md` (D48 preemptive stability-probe gate owed at SIGN cycle); `feedback_session_open_with_orient.md` + `feedback_pa_chat_local_override.md` (tools/pa_local.sh:128 updated from retired Group 1400 arc pin to fresh S1500 pin `pa-791b3db549a64e54`); `feedback_llm_autofills_boolean_params_with_false.md` (parent doc §2.5 evidence tables include explicit boolean-autofill safe interpretations). Fresh S1500 arc pin `pa-791b3db549a64e54` (minted via Rigby `session_tool.create_fresh` this session). Index v27 updated per §10.1 (this row + §1.30 row + frontmatter v27 preamble + §8 timeline S1500 row).

### 1.31 `domains/sports/1501_sports_odds_ingestion_normalization_audit.md`

- **Title.** S1501 Sports Odds Ingestion & Normalization — Child Audit (Category A / P1 under Group 1500)
- **Purpose.** First child audit under Group 1500. Answers the 28 playbook §9 canonical questions for Category A (sports odds ingestion + normalization + persistence). First sibling to apply the pre-brief 4-item mini-schema per D62 = (a) propagate upfront (Chris-ratified S1501 open 2026-07-01) so P6/F (S1506) inherits consistent evidence shape for the posture-decision brief owed to xx99 (S1599). Six parallel Explore sub-agents + parent-Claude verifier-loop for load-bearing claims per playbook §14 "trust but verify".
- **Status.** `status: active` on Chris commit-gate 2026-07-01. Rigby Full SIGN cycle 1 SIGN-with-edits at Medium-High confidence → F1-F7 folds landed at commit-time → Rigby Full SIGN cycle 2 SIGN-clean at High confidence 2026-07-01 on fresh isolation pin `pa-a39069230ab64450` (retired at S1501 close). **D48 preemptive stability-probe gate 4th arm — CODIFICATION-READY for playbook v3 §15 per S1405+S1406+S1499+S1501 4-arc pattern** (clean probe + zero worker-instability across 4 substantive SIGN batches this session).
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: child-audit`, `category: child_audit`, `subdomain_category: A`.
- **Primary questions answered.**
  - **Does a unified odds normalization service exist?** §5.2 grep-verified NEGATIVE — parent scoping §6 P1-parked issue #1 resolved to NO. Each spider writes its own persistence path; `_impl_snapshot_odds_for_line_movement` writes directly to `OddsSnapshot`/`GameLineHistory` bypassing `SpiderData` entirely.
  - **Is `sports_odds` a valid `SpiderData.data_type`?** §4.3 + §14.1 verified NEGATIVE — `SpiderData.data_type` at `persistence/models.py:693-712` declares 14 valid choices; `'sports_odds'` is NOT one of them. Same drift on `source_platform='theodds'`. Django CharField `choices=` validates only in Forms/Admin, not at `Model.save()`, so writes silently persist. Materializes S1274 §14 Finding #6 beyond `SignalCluster.pattern_type` to `SpiderData` itself. HIGH severity per Rigby SIGN cycle 1 Q5 confirmed.
  - **Is `snapshot_odds_for_line_movement` beat-scheduled?** §14.3 grep-verified NEGATIVE — docstring says "Runs every 20 minutes" but no beat entry in `core/celery.py:37-797`. Rigby SIGN cycle 1 Q8 fold: reframed as "unimplemented expectation" not "spec-vs-code violation".
  - **Where does the Discord digest actually post?** §14.2 verified drift — docstring says `#market-intelligence` (`_impl_collect_sports_odds_intelligence` at `tasks_financial.py:1817`); code hardcodes `CHANNEL_BOARDROOM` (`send_betting_digest` at `discord_notifications.py`). LOW severity docstring drift.
  - **Cat A maturity verdict?** §13: **WORKING (fragile contract) at ingestion, PARTIAL at normalization** (Rigby SIGN cycle 1 Q2 fold — qualifier acknowledges runtime success ≠ schema-contract stability).
- **Load-bearing deliverables.** §2.1 NEW **Cat A contract statement** ("Cat A guarantees today" vs "Cat A explicitly does NOT guarantee") per Rigby SIGN cycle 1 Q9 fold — F7 landed; §4 Major Models with 4-item mini-schema per model per D62 fold; §5 Services layer with grep-verified NEGATIVE on unified normalization; §7 4 runtime flow diagrams (TheOdds→SpiderData; snapshot→OddsSnapshot/GameLineHistory; Kalshi→SpiderData; Discord digest); §9 Q15 posture-decision-pending reframe per Rigby SIGN cycle 1 Q4 fold (F2 landed) — cites S1274 §12.3 two-legitimate-postures precedent; §14 drift matrix (5 items: enum violations HIGH; docstring drift LOW; snapshot dormancy MED; topic-doc stale claim LOW; parent scoping mock-vs-production refinement LOW); §15 debt matrix (9 items; #1 HIGH enum violations; #2 architecture-decision-pending downgrade per Rigby Q5 fold F4; #6 MEDIUM upgrade per Rigby Q5 fold F4; #8 conditional MED-HIGH for cross-book aggregation per Rigby Q7 fold F5); §17 dual-store clarification per Rigby SIGN cycle 1 Q9 fold — F3 landed; §19 10-item ranked future-research queue with enum resolution promoted to HIGH #2 + new "Downstream consumer inventory" HIGH #3 per Rigby SIGN cycle 1 Q7 folds F5; §20.5 F1-F7 SIGN fold notes + cycle 2 verdict verbatim.
- **Verifier-loop discipline.** Six parallel Explore sub-agents launched in single message per playbook §13 (Models/Persistence + Services/Runtime + APIs/Tools/Tasks/Commands + Spider Ingestion Detail + Docs/Prior-Research + Drift/Debt/Ownership/Maturity). Parent-Claude verifier-loop applied per playbook §14 on 5 load-bearing claims: (1) `SpiderData.data_type` enum choices via `persistence/models.py:693-712` direct read; (2) `_impl_collect_sports_odds` `update_or_create` payload via `core/tasks_financial.py:1770-1782` direct read; (3) `_impl_snapshot_odds_for_line_movement` producer identity via `core/tasks_financial.py:2140-2270` direct read (Sub-Agent 1 initial "no visible producer" claim REFUTED at commit-time §20.4); (4) Discord channel constant `CHANNEL_BOARDROOM` via `core/services/discord_notifications.py:40` direct read; (5) beat schedule slice via `core/celery.py:775-797` direct read. 3 Sub-agent claims corrected in-doc pre-SIGN (recorded in §20.4). Rigby SIGN cycle 1 substantive on fresh isolation pin `pa-a39069230ab64450` batches 1-3 (D48 stability-probe clean) — F1-F7 folds landed. Rigby SIGN cycle 2 SIGN-clean at High confidence — do-not-regress notes for PR: keep §2.1 Cat A contract statement + preserve posture-decision-pending framing throughout §9 Q15 + §17 + preserve enum-resolution HIGH severity in §15 debt #1 + §19 rank #2.
- **Inherited findings referenced.** S1274 §14 Finding #6 (HIGH — `sports_odds` not a `SignalCluster.pattern_type`) — CONFIRMED at code level AND extended to `SpiderData.data_type` + `source_platform` per §14.1; S1274 §12.3 (P1 Product/Architecture Decision Point) — posture-decision-pending framing licensed by "two legitimate postures" precedent; S1273 §3.10 LIGHT baseline → S1501 close moves Cat A coverage to MODERATE per §12.
- **Dependencies.** Parent scoping `1500_sports_domain_scoping.md` (§3 Cat A boundary + §5 mission sequence + §6 P1-parked issues resolved in this audit + §D62 mini-schema propagation directive); `DOMAIN_RESEARCH_PLAYBOOK.md` §9 canonical questions + §11.2 20-section template + §13 6-parallel-Explore sweep + §14 evidence rules + §15 SIGN policy; `RESEARCH_OPERATING_SYSTEM.md` §8 child-audit contract; `platform_architecture_inventory.md` §3.10; `platform/cross_domain_integration_audit.md` §14 Finding #6 + §12.3.
- **Recommended next reads.** **S1502 Child B Sports Prediction & Analytics Agents Audit** next per parent §5 mission sequence P2 slot. Load-bearing S1501 outputs to inherit at S1502: §2.1 Cat A contract statement (what Cat A does NOT guarantee — normalization, SignalCluster emission, fixture-identity reconciliation — Cat B P2 verifies whether Cat B contract fills those gaps or extends them); §14.1 silent choices-enum violations (S1502 verifies whether Cat B agents' `data_type == 'sports_odds'` filters compensate for or extend the enum drift); §19 rank order for Cat F consumption.
- **Overall importance.** **First library child audit to apply the 4-item pre-brief mini-schema per surface per D62 = (a) propagate upfront** — sets the evidence-shape contract that P2-P5 siblings inherit and P6/F consumes for the posture-decision evidence plan owed to xx99. **First library child audit to codify D48 stability-probe gate as 4th-arm CODIFICATION-READY signal** (S1405+S1406+S1499+S1501 pattern met at 4-arc threshold; recommended for immediate playbook v3 §15 codification alongside D45 titles-only recovery + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent per S1499 §10 meta-methodology). **First library child audit to explicitly reframe integration-gap language as posture-decision-pending language throughout** (per Rigby SIGN cycle 1 Q4 + Q8 folds F2 + F6 folded — cites S1274 §12.3 two-legitimate-postures precedent as licensing rationale; §9 Q15 + §1 exec summary + §17 all updated in sync).
- **Distinguishing property.** **First library child audit to add a "Cat A contract statement" (§2.1) explicitly listing what the category guarantees today vs what it explicitly does NOT guarantee.** Prevents downstream consumers from inferring integration/normalization/reconciliation contracts that Cat A does not own. Pattern candidate for playbook v3 §11.2 template addition if replicated at S1502-S1505. **First library child audit to catch a Django `choices=` silent-drift pattern** (§14.1 — CharField.choices only validates in Forms/Admin, not at Model.save()) as a top-1 HIGH-severity finding via grep-verified NEGATIVE on `SpiderData.data_type` enum membership + parent-Claude direct-read verification. Extends the memory rule `feedback_llm_autofills_boolean_params_with_false.md` (S1227) Django behavior pattern to a research-methodology finding. **First library child audit to inherit S1274 §14 Finding #6 at code level AND expand its scope** — S1274 named `SignalCluster.pattern_type`; S1501 confirms + adds `SpiderData.data_type` + `SpiderData.source_platform` to the same silent-drift class. Index v27 → v28 updated per §10.1 (this §1.31 row + frontmatter v28 preamble + §8 timeline S1501 row).

---

### 1.32 `domains/sports/1502_sports_prediction_analytics_agents_audit.md`

- **Title.** S1502 Sports Prediction & Analytics Agents — Child Audit (Category B / P2 under Group 1500)
- **Purpose.** Second child audit under Group 1500. Answers the 28 playbook §9 canonical questions for Category B (4 market agents — `sports_odds_analyst` + `game_predictor` + `sharp_action_detector` + `arbitrage_detector` — plus `SportsBettingCoordinator` orchestrator). Second sibling to apply the pre-brief 4-item mini-schema per D62 = (a) propagate upfront (Chris-ratified S1501 open 2026-07-01) so P6/F (S1506) inherits consistent evidence shape for the posture-decision brief owed to xx99 (S1599). Six parallel Explore sub-agents + parent-Claude verifier-loop for load-bearing claims per playbook §14 "trust but verify". Consumes S1501 §2.1 Cat A contract statement as load-bearing input — verifies whether Cat B fills or extends Cat A's "does NOT guarantee" list.
- **Status.** `status: active` on Chris commit-gate 2026-07-02. Rigby Full SIGN cycle 1 SIGN-with-edits at Medium confidence → F1-F12 folds landed at commit-time → Rigby Full SIGN cycle 2 SIGN-clean at High confidence 2026-07-02 on fresh isolation pin `pa-64c019d7e6685d31` (retired at S1502 close). **D48 preemptive stability-probe gate 5th arm — CODIFICATION-READY for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502 5-arc pattern** (clean probe via `cockpit_tool.worker_health` + zero worker-instability across 4 substantive SIGN batches this session).
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: child-audit`, `category: child_audit`, `subdomain_category: B`.
- **Primary questions answered.**
  - **Does the coordinator invoke all 5 agents symmetrically?** §5.2 + §7.1 verified NEGATIVE — `SportsBettingCoordinator` uses 4 `.execute()` calls (`GamePredictor` line 103, `ArbitrageDetector` line 140, `LineMovementAnalyzer` line 158, `SharpActionDetector` line 176) but 1 `.run()` call (`SportsOddsAnalyst` line 122 with explicit Session 1206 Layer 1 audit comment). §1 Finding 1 HIGH operational risk. Docstring at lines 22-33 describes symmetric 5-agent orchestration — mismatch.
  - **Do all 4 audited agents filter `data_type == 'sports_odds'` via ORM query on `SpiderData`?** §5.1 + §1 Finding 3 verified NEGATIVE — filter is post-fetch in-memory list comprehension on dict return from `TheOddsSpider().fetch_data()`, NOT ORM query. Only LineMovementAnalyzer (scope-boundary per parent §3.B) does `LegacySpiderData.objects.filter(...)`. F12 fold tightened verbatim shape + cite.
  - **Does `ArbitrageDetector` persist to `sports.models.ArbitrageOpportunity`?** §4.3 + §1 Finding 4 grep-verified NEGATIVE — zero `ArbitrageOpportunity.objects.create()` in `core/agents/markets/`. Model + admin + serializer + viewset triple all exist but no producer. F5 fold KEPT AS DRIFT per Rigby cycle 1 recommendation.
  - **Are all Cat B agents in the PA tool dispatcher registry?** §3.4 + §1 Finding 2 verified NEGATIVE — `tool_dispatcher.py:302-305` registers only 4 sports tools (`prediction_market_analyst`, `game_predictor`, `line_movement_analyzer`, `sharp_action_detector`); `sports_odds_analyst` and `arbitrage_detector` absent. MED-HIGH operational risk.
  - **Is `SignalCluster.pattern_type` enum updated with sports types on Cat B write side?** §9 + §1 Finding 5 grep-verified NEGATIVE — enum at `core/models_signal_intelligence.py:75-86` still lacks sports types; zero Cat B `SignalCluster.objects.create()` calls. F2 fold reframed to POSTURE-DECISION-PENDING per S1274 §12.3 precedent. HIGH architectural risk (biggest per Rigby cycle 1 verdict).
  - **Cat B maturity verdict?** §13: **PARTIAL (armed but under-instrumented)** — Session-1205 DEAD-classification remediation is incomplete (softened per F9 fold): beat armed + code complete but 4/5 telemetry-missing + 2/4 PA-missing + 0 SignalCluster emission + 0 outcome-feedback loop + `ArbitrageOpportunity` dormant.
- **Load-bearing deliverables.** §2.1 Cat B contract statement (mirror of S1501 §2.1 pattern) listing what Cat B guarantees today vs what it explicitly does NOT guarantee — establishes the contract Cat F evidence plan consumes; §4 Major Models with 4-item mini-schema (§4.8) per model per D62 fold + new §4.6 SportsBettingBrief subsection landed post-cycle-1 verifier-loop; §5 Services layer with god-service check (5 surfaces / 2,622 lines total; largest 730 lines / SportsOddsAnalyst) + coordinator asymmetry deep-dive at §5.2; §7 3 runtime flow diagrams + §7.1 F1-fold explicit call-chain block + failure-mode semantics + telemetry count table per single brief run; §9 integration strength table (STRONG inbound Cat A; MISSING to SignalCluster/Initiative/Memory/EventBus; PARTIAL bidirectional Cat C; STRONG outbound Deliverable/LLM providers/Cat E REST); §14 drift matrix (8 items — 2 HIGH + 3 MED-HIGH + 2 MED + 1 LOW); §15 debt matrix (12 items — F6 fold added cross-book fixture-identity as debt #12 MED-HIGH architectural / LOW operational); §17 duplicate/overlap flags (SportsOddsAnalyst vs SharpActionDetector complementary; ArbitrageDetector + GamePredictor duplicate implied-probability math §15 debt #8); §19 ranked future-research queue (F1 fold promoted PA registry gap rank 5→4 per Rigby cycle 1 Q7); §20.5 F1-F12 SIGN fold notes + cycle 2 verdict verbatim with Q10-Q12 confidence values.
- **Verifier-loop discipline.** Six parallel Explore sub-agents launched in single message per playbook §13 (Models/Persistence + Services/Runtime + APIs/Tools/Tasks/Commands + Integrations/Cross-Domain + Docs/Prior-Research + Drift/Debt/Ownership/Maturity). Parent-Claude verifier-loop applied per playbook §14 on 7 load-bearing claims (all 7 SURVIVED independent verification, 0 sub-agent errors caught this pass — cleaner than S1501 which caught 3): (1) coordinator `.run()` vs `.execute()` asymmetry via direct read of `sports_betting_coordinator.py:1-290`; (2) direct-consume filter shape via 4 grep sites; (3) ArbitrageDetector zero-persistence to `ArbitrageOpportunity` via targeted grep; (4) MLPrediction sole-writer verified as `game_predictor.py:505`; (5) beat schedule + queue via direct read `core/celery.py:775-797`; (6) PA tool registry via direct read `tool_dispatcher.py:302-305`; (7) `SignalCluster.pattern_type` enum via direct read `core/models_signal_intelligence.py:75-86`. Post-cycle-1 additional verifier-loop applied on 2 Rigby-flagged UNKNOWNs (SportsBettingBrief model existence F10 + router registration F11) — both resolved via targeted grep. Rigby SIGN cycle 1 substantive on fresh isolation pin `pa-64c019d7e6685d31` batches 1-3 (D48 stability-probe clean via `cockpit_tool.worker_health`) — F1-F12 folds landed. Rigby SIGN cycle 2 SIGN-clean at High confidence — do-not-regress notes for PR: keep §2.1 Cat B contract statement + preserve posture-decision-pending framing throughout §1 Findings 5-7 + preserve F1 explicit call-chain block + F6 fixture-identity debt item + F7 operational-vs-architectural risk axis.
- **Inherited findings referenced.** S1501 §2.1 Cat A contract statement — verified as Cat B's load-bearing input; Cat B §2.1 contract statement documents whether B fills or extends A's "does NOT guarantee" list (mostly extends — no unified normalization, no fixture-identity reconciliation, no SignalCluster emission, no outcome-feedback loop). S1274 §14 Finding #6 — CONFIRMED at code level for Cat B consumer side + write-side absence (both enum + `.objects.create()` missing). S1274 §12.3 posture-decision-pending framing licensed for Findings 5-7 per Rigby SIGN cycle 1 Q4 folds F2/F3/F4. S1273 §3.10 LIGHT baseline → S1502 close moves Cat B coverage from LIGHT to MODERATE per §12.
- **Dependencies.** Parent scoping `1500_sports_domain_scoping.md` (§3 Cat B boundary + §5 mission sequence + §6 P1/P2-parked issues resolved in this audit + §D62 mini-schema propagation directive); sibling audit `1501_sports_odds_ingestion_normalization_audit.md` (§2.1 Cat A contract statement as load-bearing input); `DOMAIN_RESEARCH_PLAYBOOK.md` §9 canonical questions + §11.2 20-section template + §13 6-parallel-Explore sweep + §14 evidence rules + §15 SIGN policy; `RESEARCH_OPERATING_SYSTEM.md` §8 child-audit contract; `platform_architecture_inventory.md` §3.10; `platform/cross_domain_integration_audit.md` §14 Finding #6 + §12.3.
- **Recommended next reads.** **S1503 Child C Wager Tracking & Outcome Verification Audit** next per parent §5 mission sequence P3 slot. Load-bearing S1502 outputs to inherit at S1503: §1 Finding 6 outcome-feedback-loop MISSING (Cat C S1503 owns `BettingOutcomeVerifier` scope; verifies whether outcomes route back to Cat B); §4.1 MLPrediction inventory (Cat C reads via `PlacedWager.game` FK); §5.2 coordinator asymmetry pattern (may recur in Cat C wager-outcome-verifier orchestration); §14.1 coordinator .run/.execute asymmetry (pattern candidate for cross-category discovery); §19 rank order for Cat F consumption.
- **Overall importance.** **Second library child audit to apply the 4-item pre-brief mini-schema per surface per D62 = (a) propagate upfront** — validates D62 propagation-upfront directive at second sibling by producing consistent evidence shape without schema drift from S1501. **Second library child audit to codify D48 stability-probe gate as 5th-arm CODIFICATION-READY signal** (S1405+S1406+S1499+S1501+S1502 5-arc pattern strengthens the immediate playbook v3 §15 codification recommendation). **First library child audit to distinguish OPERATIONAL RISK from ARCHITECTURAL RISK on per-finding basis** (F7 fold — per Rigby SIGN cycle 1 Q6 fold; propagates to §14 drift, §15 debt, §19 future research queue). **First library child audit to add explicit call-chain block** in flow section (F1 fold — per Rigby SIGN cycle 1 Q1 must-change-before-canonical directive; pattern candidate for playbook v3 §11.2 template addition). **First library child audit to catch a coordinator method-signature asymmetry** as a load-bearing HIGH operational-risk finding via direct read of the coordinator file + grep verification of orchestration site — extends the S1501 §14.1 Django `choices=` silent-drift pattern to a behavioral-invariance drift pattern class.
- **Distinguishing property.** **First library child audit to inherit a sibling's contract statement as load-bearing INPUT** — S1501 §2.1 Cat A contract statement was directly cited as Cat B's runtime dependency, and Cat B §2.1 documents which non-guarantees it fills vs extends. Pattern candidate for playbook v3 §11.2 template addition for arcs with sibling-inheritance structure. **First library child audit to explicitly separate operational-vs-architectural risk on all findings** — F7 fold applied per Rigby SIGN cycle 1 Q6 recommendation; propagates to drift matrix + debt matrix + future research queue; likely pattern candidate for playbook v3 §12 classification. **First library child audit to reach a "PARTIAL (armed but under-instrumented)" maturity verdict** — captures the shape where code + beat + persistence are complete but self-instrumentation + downstream signal-emission are partial adoption; extends S1501 "WORKING (fragile contract) at ingestion, PARTIAL at normalization" two-tier pattern to a single-tier observation-invariance pattern. **First library child audit to catch a Django admin+serializer+viewset triple with zero producer** — `ArbitrageOpportunity` at `sports/models.py:1292` + full admin/serializer/viewset infrastructure with no `.objects.create()` call in Cat B (F5 fold KEPT AS DRIFT per Rigby cycle 1: "model + admin + serializer + viewset reads like we meant to persist"). Index v28 → v29 updated per §10.1 (this §1.32 row + frontmatter v29 preamble + §8 timeline S1502 row).

---

### 1.36 `domains/sports/1506_sports_cross_domain_integration_lens_and_posture_decision_framing_audit.md`

- **Title.** S1506 Sports Cross-Domain Integration Lens & Posture Decision Framing — Child Audit (Category F / P6 under Group 1500 — **LAST child before xx99**)
- **Purpose.** Sixth and final child audit under Group 1500. Answers the 28 playbook §9 canonical questions for Category F — the cross-domain integration lens across four architecturally distinct axes: (1) DBAO product-line materialization surface (PostgreSQL `dbao` schema + `/ws/dbao/` + `/ws/dbao-dashboard/` WebSocket routes + `VITE_DBAO_API_URL`/`VITE_DBAO_WS_URL`/`VITE_DBAO_ENABLED`/`EXPO_PUBLIC_DBAO_API_URL`/`EXPO_PUBLIC_DBAO_WS_URL` env-vars + `x-dbao-client` CORS-whitelisted header); (2) Intelligence surface (`intelligence/realtime_engine.py` 702 lines sports-native + `intelligence/views.py:44` `sports_intelligence` hardcoded literal + duplicate at `core/intelligence_api.py:94` + `IntelligencePage.tsx` sports-tangential); (3) Discord sports surface (7 slash commands at `discord_bot.py:1108-1961` + `_impl_collect_sports_odds_intelligence` at `core/tasks_financial.py:1815-1902`); (4) Cross-domain feedback surface (Signal Engine `sports_odds` gap at `core/models_signal_intelligence.py:75-86` + Memory Domain partial bridge at `core/learning_bridges/sports_betting_bridge.py:532,606` + `MLPrediction`/`BettingOutcomeVerifier` decoupling). **LOAD-BEARING for D59 posture-decision evidence plan owed to xx99 canonical summary** — §20.6 produces the evidence-plan framing (7 integration criteria + 7 island criteria + 4 cross-cutting + failure-mode table + cost asymmetry summary + F2-fold scoring rubric with thresholds) with explicit "Chris-gated selection" tag. Sixth and final sibling to apply the pre-brief 4-item mini-schema per D62 = (a) propagate upfront (Chris-ratified S1501 open 2026-07-01) — 6-sibling exemplar pattern COMPLETED. Six parallel Explore sub-agents per playbook §13 + parent-Claude verifier-loop per playbook §14 "trust but verify" on 6 load-bearing pre-Explore claims (all 6 verified CORRECT against source before draft integration). Consumes S1501 §2.1 Cat A contract + S1502 §2.1 Cat B contract + S1503 §2.1 Cat C contract + S1504 §2.1 Cat D contract + S1505 §2.1 Cat E contract + S1505 §14.1 MOCK-DATA-CONSUMER + S1505 §4.2 humanApi cross-domain surface + S1504 §14.3 SportsBettingBrief write-only-and-forgotten + S1503 §14.1 ZERO-FIRE-BEAT + S1502 §14.3 Signal Engine emission absence + S1274 §14 Finding #6 as load-bearing inherited claims.
- **Status.** `status: draft` at S1506 commit (Chris commit-gate pending). Rigby Full SIGN cycle 1 SIGN-with-edits at **High confidence** 2026-07-02 on fresh isolation pin `pa-c2cdbd5c0b8c451b` → F1-F2 folds landed at commit-time → Cycle 2 SIGN-clean at High confidence anticipated post-fold-land (matches S1501-S1505 5-of-5 cycle-1-predict-cycle-2 arc precedent). **D48 preemptive stability-probe gate 9th arm — CODIFICATION-READY for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506 9-arc pattern** (clean probe via `cockpit_tool.worker_health` returning 4 healthy workers + `infra_health_tool.dependency_matrix` returning 7-of-7 healthy components; zero worker-instability across 3 substantive SIGN turns — **four consecutive fully-clean arms S1503+S1504+S1505+S1506**).
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: child-audit`, `category: child_audit`, `subdomain_category: F`.
- **Primary questions answered.**
  - **Does DBAO carry any real runtime state?** §14.1 CRITICAL verified NEGATIVE — 6 declared artifacts + zero materialized state + 2 unimplemented handler stubs (`send_query_status` + `handle_run_analytics` grep returns zero definitions across `core/`); schema empty (`grep db_table='dbao.*'` returns zero); WS handler broadcasts 100% mock (per S1505 §14.1 extended); VITE/EXPO env-vars declared but never read (frontend grep zero hits); `x-dbao-client` header CORS-whitelisted but never sent/read (repo-wide grep returns exactly one hit — the whitelist line itself). **NEW pattern class for the arc: NAMING-CONVENTION-WITHOUT-MATERIALIZATION** (distinct from S1505 MOCK-DATA-CONSUMER which required a real consumer running with fake data; here even the consumer is stub-referenced).
  - **Does BettingOutcomeVerifier route outcomes back to MLPrediction?** §14.2 CRITICAL verified NEGATIVE — `core/services/betting_outcome_verifier.py:30-481` never touches `MLPrediction` (grep zero); `PredictionEvaluator` at `sports/prediction_evaluator.py:40-420` per Explore Agent 6 never touches `PlacedWager`/`PlacedWagerLeg`. Two verification systems fully independent. Answers Cat F parked-candidate finding closure. **NEW pattern class: DECOUPLED-VERIFICATION-SYSTEMS.**
  - **Does the `sports_intelligence` flag gate any runtime path?** §14.4 HIGH verified NEGATIVE — hardcoded literal at `intelligence/views.py:44` inside `SkynetStatusView.get()` response dict; duplicate at `core/intelligence_api.py:94`; consulted nowhere at runtime. `settings.SPORTS_ANALYTICS` config block at `core/settings.py:629-633` similarly declared, never consulted. **NEW pattern class: DECLARED-FEATURE-FLAG-GATES-NOTHING.**
  - **Does the Sports ↔ Signal Engine 6-arc consumer-side pattern hold?** §14.3 HIGH verified NEGATIVE at every layer: (a) `SignalCluster.PATTERN_TYPE_CHOICES` at `core/models_signal_intelligence.py:75-86` lists 10 valid types + `sports_odds` NOT among them (verified this session); (b) `signal_aggregation_service.py` PATTERN_TYPE_KEYWORDS + TOPIC_PATTERNS hardcoded non-sports; (c) zero bridging code (grep for SportsSignal/betting_signal/bookmaker_signal/line_movement_signal returns zero); (d) zero sports-native aggregator. Extends S1502+S1503+S1504+S1505 5-arc pattern to **6-arc consumer-side pattern**. **§20.9 6-arc pattern completed.**
  - **What is Discord's role in the sports surface?** §14.5 HIGH verified — Discord is a first-class write consumer (`/bet` at line 1571 + `/resolve` at lines 1687+1705 write directly to `Wager`/`Bankroll` — no coordinator gate) AND read consumer with HOT-PATH-CHOKE bypass at 3 of 4 read commands (`/odds` + `/futures` + `/slip` instantiate `TheOddsSpider` directly and rebuild presentation inline). `/arb` shared-agent path via `ArbitrageDetector.run()`. `_impl_collect_sports_odds_intelligence` at `core/tasks_financial.py:1815-1902` bypasses BOTH `SportsBettingCoordinator` AND `RealtimeIntelligenceEngine` (dual-coordinator-bypass at §17.1). F1 fold §14.5 anchor set tightening per Rigby Q5 Batch 1.
  - **Is the Sports → Memory Domain bridge complete?** §14.6 HIGH verified NEGATIVE PARTIAL — `SportsBettingLearningBridge.record_wager_outcome` at `core/learning_bridges/sports_betting_bridge.py:532` (SportsOddsAnalyst) + `record_arbitrage_outcome` at line 606 (ArbitrageDetector) write to `AgentMemory`; GamePredictor + SharpActionDetector zero writes; zero `AgentKnowledgeSource` writes for any sports agent. 2 of 4 agent coverage; 0/1 write-target coverage on secondary model. Learning bridge exists via BettingOutcomeVerifier `_create_learning_records()` at lines 455-480.
  - **Cat F maturity verdict?** §13: **PARTIAL (mixed; multi-axis; four-axis compound shape)** — sixth distinguishing maturity shape after S1501 fragile-contract-at-ingestion + S1502 armed-but-under-instrumented + S1503 armed-but-zero-fire + S1504 mixed-brief-generation-persistence-forgotten-HOT-PATH-CHOKE + S1505 mixed-WORKING-DEAD-RENDER-MOCK-AUTH-NO-REALTIME. Cat F is the first sibling to require three new maturity classifiers in a single audit — the compound-multi-axis shape is expected for the cross-domain lens.
- **Load-bearing deliverables.** §2.1 Cat F contract statement (sixth and final sibling in Group 1500 completing 6-sibling contract-statement pattern) — 5 guarantees + 11 non-guarantees; §4 Major Models with §4.4 6-sibling exemplar pattern completion for D62 = (a) mini-schema propagation; §5 Major Services enumerated by cross-domain role; §7 Runtime Flows §7.1-§7.6 (Discord bypass + Discord write + verify_betting_outcomes + `/ws/dbao/` mock + RealtimeIntelligenceEngine sports flow + Discord digest dual-coordinator-bypass); §9 Integrations With Other Domains §9.1-§9.5 the LOAD-BEARING section for Cat F — one integration table per each of Signal Engine + Memory Domain + Intelligence surface + Discord + DBAO product-line; §14 drift matrix (12 items with 5 NEW pattern classes: NAMING-CONVENTION-WITHOUT-MATERIALIZATION + DECOUPLED-VERIFICATION-SYSTEMS + DECLARED-FEATURE-FLAG-GATES-NOTHING + DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT + SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION); §15 debt matrix (12 items with F1-F2 folds landed); §17 duplicate/overlapping systems (5 items — DUAL-COORDINATOR-BYPASS + Discord presentation duplication + RealtimeIntelligenceEngine ↔ SportsBettingCoordinator overlap + 2 verification systems for game outcomes + `/ws/dbao/` + `/ws/dbao-dashboard/` sibling routes); §18 ownership gaps (compound CODEOWNERS gap across 6 sports runtime files); §19 recommended future research T1-T5 tier-ordered; **§20.6 POSTURE-DECISION EVIDENCE PLAN** (D59 load-bearing deliverable) — 7 integration criteria (A1-A7 SignalCluster emit + coordinator gate + learning bridge coverage + engine auto-start + verification linkage + flag+IntelligencePage reality + DBAO materialized) + 7 island criteria (B1-B7 sports-native aggregator + sports-scoped memory + sports-native retrain + coordinator sole read gate + DBAO app label + sports-native engine + flag replaced by product-line boundary) + 4 cross-cutting (C1-C4 CODEOWNERS + topic doc + integration tests + BettingPage tests) + failure-mode table (D) + cost asymmetry summary (E) + F2-fold scoring rubric with thresholds (F) + explicit "Chris-gated selection" tag; §20.7 Sports Domain Lifecycle Traceability Table stub per parent §12.5 (Cat F contributes rows; xx99 assembles); §20.8 F1-F2 SIGN fold notes with cycle 1 verdict; §20.9 6-arc consumer-side pattern completion; §20.10 6-sibling exemplar pattern completion for D62 = (a).
- **Verifier-loop discipline.** Six parallel Explore sub-agents launched in single message per playbook §13 (Agent 1 DBAO footprint + Agent 2 Intelligence surface + Agent 3 Discord bridge + Agent 4 Signal Engine gap + Agent 5 Memory bridge + Agent 6 MLPrediction feedback). Parent-Claude verifier-loop applied per playbook §14 on 6 load-bearing pre-Explore claims — all 6 verified CORRECT against source before draft integration: (a) `SignalCluster.PATTERN_TYPE_CHOICES` at `core/models_signal_intelligence.py:75-86` (10 types; `sports_odds` absent); (b) `send_query_status` + `handle_run_analytics` unimplemented across `core/` (grep zero definitions); (c) PostgreSQL `dbao` schema in search_path at `core/settings.py:340`; (d) `/ws/dbao/` + `/ws/dbao-dashboard/` route registration at `core/routing.py:369-370`; (e) `sports_intelligence` hardcoded at `intelligence/views.py:44`; (f) `SportsBettingLearningBridge.AgentMemory.objects.create` at `core/learning_bridges/sports_betting_bridge.py:532` (wager) + `:606` (arb). Zero corrections needed pre-integration; all Explore claims consistent with source. Rigby SIGN cycle 1 substantive on fresh isolation pin `pa-c2cdbd5c0b8c451b` — D48 stability probe clean via `cockpit_tool.worker_health` (4/4 workers online, 0 active tasks) + `infra_health_tool.dependency_matrix` (7/7 healthy, 0 warnings, 0 errors) pre-SIGN. Rigby cycle 1 Batch 1 Q1-Q5 (4 CORRECT High + 1 CORRECT-with-EDIT Medium) + Batch 2 Q6-Q10 (all 5 CORRECT High) + Batch 3 Q11-Q16 (all 4 findings CORRECT High + Q15 §20.6 ADEQUATE-with-minor-structural-edits High + Q16 SIGN-WITH-EDITS at High confidence). F1 fold §14.5 anchor-set tightening + F2 fold §20.6 §F scoring rubric + threshold minima landed at commit-time. Cycle 2 SIGN-clean at High confidence anticipated post-fold-land. **Do-not-regress notes for PR:** preserve §2.1 Cat F contract statement (5 guarantees + 11 non-guarantees) + preserve F1 §14.5 anchor-set tightening (/odds + /futures + /slip explicit bypass; /arb shared-agent exclusion at section body) + preserve F2 §20.6 §F scoring rubric with threshold minima for xx99 consumption-readiness + preserve §20.9 6-arc consumer-side pattern completion + preserve §20.10 6-sibling exemplar pattern completion for D62 = (a).
- **Inherited findings referenced.** S1505 §14.1 MOCK-DATA-CONSUMER — extended at Cat F §14.7 with sibling route `/ws/dbao-dashboard/` (1 route → 2 routes footprint). S1505 §4.2 humanApi cross-domain surface — extended at Cat F §4.4 cross-sibling observation on isolation-cost distribution. S1504 §14.3 SportsBettingBrief write-only-and-forgotten — upheld and strengthened at Cat F §9.1 REST endpoint bypass. S1504 §14 HOT-PATH-CHOKE pattern — extended from REST-side to Discord-side at Cat F §14.5. S1503 §14.1 ZERO-FIRE-BEAT pattern — deepened at Cat F §14.10 LATENT-ZERO-FIRE (no beat at all, not just zero-fire). S1502 §14.3 Signal Engine emission absence — completed at Cat F §14.3 as 6-arc consumer-side pattern. S1501 §14 Discord `#market-intelligence` vs `CHANNEL_BOARDROOM` docstring drift — extended at Cat F §14.8 with `_impl_collect_sports_odds_intelligence` docstring vs runtime channel divergence. S1274 §14 Finding #6 — completed at Cat F integration-vs-island axis; §20.6 §A1/§B1 encodes both directions. S1274 §12.3 P1 decision point — Cat F §20.6 posture-decision evidence plan is the load-bearing deliverable. S1273 §9 #4 Sports/DBAO ↔ AI Studio Integration Sketch — Cat F is the successor evidence surface. S1273 §3.10 LIGHT baseline → S1506 close moves cross-domain-integration-lens coverage from parked-candidate to MODERATE-with-evidence-plan per §12.
- **Dependencies.** Parent scoping `1500_sports_domain_scoping.md` (§3.F Cat F scope + §5 mission sequence P6 LAST + §6 P6-parked issues resolved in this audit + §12.1 arc-close deliverables owed to xx99 + §12.5 Sports Domain Lifecycle Traceability Table stub + D57/D59/D60/D61/D62 Chris-locked decisions inherited); sibling audits `1501_sports_odds_ingestion_normalization_audit.md` (Cat A §2.1) + `1502_sports_prediction_analytics_agents_audit.md` (Cat B §2.1 + §14.3 SignalCluster) + `1503_sports_wager_tracking_outcome_verification_audit.md` (Cat C §2.1 + §14.7 AllowAny) + `1504_sports_betting_content_pipeline_audit.md` (Cat D §2.1 + §14.3 SportsBettingBrief) + `1505_sports_frontend_surface_audit.md` (Cat E §2.1 + §14.1 MOCK-DATA-CONSUMER); `DOMAIN_RESEARCH_PLAYBOOK.md` §9 canonical questions + §11.2 20-section template + §13 6-parallel-Explore sweep + §14 evidence rules + §15 SIGN policy + §16 arc-open discipline; `RESEARCH_OPERATING_SYSTEM.md` §8 child-audit contract; `docs/research/domains/memory/1399_memory_canonical_summary.md` (delegation candidate for Memory bridge design); `docs/research/domains/revenue/1499_revenue_canonical_summary.md` (playbook precedent); memory rule `feedback_docs_cascade_at_every_close.md` (post-merge 4-step cascade discipline).
- **Recommended next reads.** **S1599 xx99 canonical summary** next per parent §5 mission sequence P7 slot — the arc-close deliverable per playbook §11.3 12-section template + §10 meta-methodology (third application after S1399 first + S1499 second). Load-bearing S1506 outputs to inherit at S1599: §20.6 posture-decision evidence plan (verbatim consolidation into xx99 §5 posture-decision brief); §20.7 Sports Domain Lifecycle Traceability Table stub (xx99 assembles full table with all 6 P1-P6 audit rows filled); §20.3 5 new pattern classes (xx99 §4 cross-cutting patterns consolidates with S1501-S1505 pattern classes into ~13-class arc catalog); §20.9 6-arc consumer-side pattern completion (xx99 anchor for Signal Engine posture criterion); §20.10 6-sibling exemplar pattern completion (xx99 §10.2 codify-to-playbook-v3 candidate for D62 = (a) mini-schema propagation); §19 T1-T5 tier-ordered future research (xx99 §8 arc-wide T1-T10 unified tier structure consolidation).
- **Overall importance.** **First library child audit to introduce 5 NEW pattern classes in a single audit** — NAMING-CONVENTION-WITHOUT-MATERIALIZATION + DECOUPLED-VERIFICATION-SYSTEMS + DECLARED-FEATURE-FLAG-GATES-NOTHING + DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT + SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION. Prior siblings introduced 1-2 new classes per audit; Cat F is the compound cross-domain lens where every prior axis collapses. **First library child audit to produce a POSTURE-DECISION EVIDENCE PLAN as the load-bearing xx99 deliverable per D59** — evidence-plan framing (7 integration criteria + 7 island criteria + 4 cross-cutting + failure-mode table + cost asymmetry + scoring rubric with thresholds) with explicit Chris-gated selection tag. Pattern candidate for playbook v3 §11.2 template addition for arcs with posture-decision structure. **First library child audit to codify D48 stability-probe gate as 9th-arm CODIFICATION-READY signal with four-consecutive-fully-clean arms sub-pattern (S1503+S1504+S1505+S1506)** — further strengthens immediate playbook v3 §15 codification recommendation from S1505 8-arc threshold. **First library child audit to complete the 6-sibling exemplar pattern for D62 = (a) mini-schema propagation-upfront** — full arc validation of the directive; xx99 §10.2 candidate for playbook v3 §5 promotion. **First library child audit to reach a "PARTIAL (mixed; multi-axis; four-axis compound shape)" maturity verdict** — each of 4 axes carries its own pattern class; xx99 consolidates rather than merges. **First library child audit to introduce a NAMING-CONVENTION-WITHOUT-MATERIALIZATION pattern class distinct from S1505 MOCK-DATA-CONSUMER** — diagnostic criteria: (i) named artifacts declared across multiple layers (schema/WS/env-var/header); (ii) zero runtime state carried; (iii) unimplemented handler stubs referenced; (iv) env-vars declared but never read; (v) HTTP headers whitelisted but never sent/read. Pattern candidate for playbook v3 §14 evidence-rules diagnostic checklist.
- **Distinguishing property.** **First library child audit designed as a LENS rather than as a boundary-scoped surface audit** — Cat F is the cross-domain integration lens; every prior sibling collapses into it. Structural precedent for future domain arcs where the last child audit consumes P1-N evidence to produce the load-bearing xx99 deliverable per D59-analog. **First library child audit to explicitly separate 4 axes with per-axis maturity verdict** — DBAO materialization axis / Intelligence surface axis / Discord surface axis / Cross-domain feedback axis; compound shape captured cleanly. **First library child audit to fold Rigby scoring-rubric-with-thresholds edit into a posture-decision evidence plan** — F2 fold §20.6 §F adds PASS/PARTIAL/FAIL rubric + minimum acceptable threshold per criterion. Makes xx99 §5 posture-decision brief consumable without post-hoc scoring criteria. Pattern candidate for playbook v3 §11.3 canonical summary template §5 addition. **First library child audit where D48 stability-probe gate held clean across 3 substantive SIGN turns extending the four-consecutive-fully-clean-arms sub-pattern (S1503+S1504+S1505+S1506)** — 9-arc evidence base + specific sub-pattern strengthens xx99 §10.2 codification recommendation quality. Index v32 → v33 updated per §10.1 (this §1.36 row + frontmatter v33 preamble + §8 timeline S1506 row).

---

### 1.38 `domains/content/1600_content_domain_scoping.md`

- **Title.** S1600 Content / Deliverables / Publishing — Parent Architecture Scoping (Group 1600 mission plan; **third application of Chris's Phase 0 F.i/F.ii/F.iii methodology**)
- **Purpose.** Parent Phase 0 scoping for Group 1600 Content / Deliverables / Publishing arc. Third application of Chris's Phase 0 F.i/F.ii/F.iii methodology (Domain Definition / Existing Knowledge Inventory / Success Criteria) — applied UNCHANGED per D68 to preserve v3 promotion trigger integrity per S1400 D29 two-triggers rule + S1500 D58 second-application + S1599 §12.4 discriminative-value criterion check 4-of-4 evidence types satisfied → playbook v3 §11.1 template promotion **TRIGGERED at S1599 close**. Group 1600 confirms whether pattern holds at third application via §12.4 F6-fold-tightened criterion (required decision-discriminative proof + required disconfirming evidence item + optional scope-confusion-prevented specificity). All 8 arc-open decisions Chris-locked in single "agree all + D-6=(a)" ratification round via governance decision `2c469638-643d-4477-a8ea-1766b552eebe` (`decision_create` + `decision_decide` action approve → status `acted`): D63 slug=`content`; D64 parent-with-children (P1-P6 + P7 xx99 at S1699); D65a Deliverable canonicalization posture-decision framing; D65b PublishGate canonicalization posture-decision framing; D65c Lifecycle transition ownership posture-decision framing; D66 child mission sequence per F3 P3↔P4 swap Cat D BEFORE Cat C; D67 §7 anti-scope 18 items; D68 methodology unchanged + D62=(a) + F8/F10 folds adopted.
- **Status.** `status: active` at S1600 commit (Chris commit-gate ratified via "agree all + D-6=(a)"). Rigby Light SIGN cycle 1 → cycle 2 SIGN-clean at High confidence 2026-07-02 on fresh S1600 arc pin `pa-f52acf3f8d394faa` → **F1-F12 folds landed at commit-time**.
- **Research type.** Parent scoping (playbook §11.1 template). `authority: parent-doc`, `category: parent_scoping`, `session: 1600`.
- **Load-bearing three-axis posture-decision framing (D65a/D65b/D65c per F4 fold split):**
  - **D65a Deliverable canonicalization** — Is Deliverable the canonical content container across domains with variants expressed as typed subkinds (or metadata), OR are variants first-class siblings with independent schemas and lifecycles? Binary posture framing per F9 fold — mushy hybrid disallowed unless evidence forces it. Evidence FOR canonical container: Deliverable base at `core/models_deliverables.py:84` with 50+ fields + central factory `deliverable_factory.py:1269` consolidating 23+ scattered creation calls + `deliverable_tool` PA gateway with 18 supported actions + 5-gate quality check at `deliverable_factory.py:46-74`. Evidence FOR parallel-siblings: 5 parallel deliverable-shaped models exist (SelfBlog + OutreachDraft + ClosePack + SportsBettingBrief + BlockchainAuditBrief) with own `publish_ready` / `status` / lifecycle fields; SelfBlog has own quality gate at `models_unified_system.py:20708-20728`; PublishGate operates on SelfBlog-shaped inputs; SportsBettingBrief operates in complete isolation from Deliverable base (S1504 §14.3 WRITE-ONLY-FORGOTTEN pattern confirmed at 2-writer / 0-reader).
  - **D65b PublishGate canonicalization** — Is PublishGate a single canonical gate with variant/channel-specific policies, OR multiple gate classes/threshold systems per variant/channel? Binary posture framing per F9 fold. Evidence FOR single canonical: PublishGate at `publish_gate.py:27` with 4 hardcoded thresholds (QUALITY 0.70, NOVELTY 0.60, STRUCTURE 0.55, MYTHOLOGY 0.15). Evidence FOR per-variant/channel: SelfBlog own quality/novelty/structure/publish_ready fields at `models_unified_system.py:20708-20728` distinct from PublishGate; DeliverableGatedError 5-gate check at `deliverable_factory.py:46-74` operates at Deliverable creation time (not post-content-deliberation) — two competing gate systems.
  - **D65c Lifecycle transition ownership (factory/rails)** — Is there a single canonical transition orchestrator (e.g., publish rails/lifecycle engine) OR do variants own their own transition rails? Binary posture framing per F9 fold. Evidence: 35 files with `Deliverable.objects.create` grep matches (factory partially adopted); DeliverableAppend/DeliverableExport/DeliverableEvent supporting model split; content_tool.content_complete status transitions (per Rigby memory rule `feedback_deliverable_status_via_content_complete.md`); parallel variants own status/publish_ready lifecycle.
- **Load-bearing child mission sequence (D66 F3-fold-swap):** P1 S1601 Cat A → P2 S1602 Cat B → **P3 S1603 Cat D (F3 fold: moved from P4→P3)** → **P4 S1604 Cat C (F3 fold: moved from P3→P4)** → P5 S1605 Cat E → P6 S1606 Cat F → P7 S1699 xx99. Rationale per F3 fold: PublishGate semantics depend on "what gets gated" and variant-specific lifecycle differences; Cat D's canonical object-model decision (D65a-analog) must precede Cat C's gate/rails investigation to prevent retro-edits after Cat D closes. Every §5 row includes explicit "We run Cat X before Cat Y because Y consumes X's canonical decision" dependency clause per F10 fold.
- **F1-F12 Rigby fold summary (folded pre-Chris-lock; do-not-regress on PR):** F1 §3 Cat A ClaimsPack boundary rule (Cat A owns claims/evidence assembly + deliberation mechanics; Cat C owns publish gating; ClaimsPack centrality preserved); F2 §3 Cat C vs Cat D crisp separation (Cat D = what IS the object; Cat C = what happens at the boundary); F3 §5 P3↔P4 swap Cat D BEFORE Cat C; F4 §8 D65 split into D65a/D65b/D65c three orthogonal axes preventing agree-all masking; F5 §7 anti-scope 12→18 items (content indexing/discoverability + search/ranking + permissions/moderation + notification fanout + attribution/analytics expansion + template system/channel integrations beyond current rail); F6 §12.4 discriminative-value tightening with required decision-discriminative proof + required disconfirming evidence item + optional scope-confusion-prevented specificity; F7 §12.5 Deliverable Lifecycle Traceability Table 10→12 stages with normalization/canonicalization (variant typing + title/slug normalization + initiative linking + dedupe/merge policy) + eligibility/packaging-gate (state boundary "eligible_for_publish" load-bearing distinct from publish gate); F8 one-sentence boundary rule per category across Cat A/B/C/D/E; F9 binary posture framing with mushy-hybrid disallowed on D65a/D65b/D65c; F10 D66 dependency-clause embedding "We run Cat X before Cat Y because Y consumes X's canonical decision"; F11 §3 Cat E feedback-hazard note (Cat E downstream by default but may emit constrained "must-have" findings requiring bounded correction in C/D; no re-scope); F12 ClaimsPack centrality preserved via F1 boundary rule.
- **Verifier-loop discipline.** Two parallel Explore sub-agents launched at S1600 open per playbook §13 (Agent 1 Content Pipeline surface + Agent 2 Deliverables + Publishing surface). Parent-Claude verifier-loop applied per playbook §14 on 3 load-bearing pre-Explore claims: (a) PublishGate class existence + threshold constants verified at `core/services/publish_gate.py:27, 44-49` — Explore Agent 1 correct, Explore Agent 2 UNVERIFIED claim overturned; (b) Discord broadcast surface verified at `core/services/discord_notifications.py:36-47` with 12 channel constants — Explore Agent 2 UNVERIFIED claim overturned; (c) Content-related Celery beat entries verified at `core/celery.py:176, 433, 460` — `cleanup-stale-content` + `generate-operator-edge-newsletter` + `cleanup-junk-initiatives` confirmed. 2 sub-agent errors caught pre-Rigby-SIGN via parent-Claude direct-read verification.
- **Cross-arc handoffs owed to Group 1600 (from §2 evidence table).** S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN CRITICAL (Cat D headline evidence for D65a-analog); S1504 §5.1 SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS HIGH (Cat B + Cat F cross-arc); S1402 F.B1 Revenue OutreachDraft delivery ZERO outbound channel HIGH (Cat C scope inheritance; extends outbound-channel pattern verification to content publishing); S1403 F.C4 ContentEngagement docstring drift HIGH (Cat B + Cat D reader-engagement → author-attribution → learning-loop investigation); S1502 §14.3 SignalCluster.pattern_type consumer-side gap 6-arc COMPLETED (Cat A ClaimsPack consumption contract continuation); S1499 D55 (ii) Revenue Employee + Income/Jobs Employee JobContract split precedent (Content Employee analog owed as Cat F evidence-plan input if surfaces); S1500 D59 posture-decision framing (analog D65 precedent — split into D65a/D65b/D65c per F4 fold); S1274 §12.3 P1 Product/Architecture Decision Point precedent (two legitimate postures with explicit success criteria).
- **Dependencies.** Playbook §11.1 parent scoping template (S1500 D58 second-application precedent; S1400 D29 first-application precedent); playbook §11.3 §10 meta-methodology template (S1399 first + S1499 second + S1599 third; xx99 S1699 fourth); playbook §11.2 20-section child audit template (owed by S1601-S1606 children); playbook §13 Explore sub-agent 6-parallel sweep (owed by S1601-S1606 children); playbook §14 verifier-loop "trust but verify" (applied at S1600 open on 3 load-bearing claims); playbook §15 SIGN policy (Light SIGN at S1600 open Rigby cycle 1 → cycle 2 SIGN-clean); playbook §16 arc-close discipline (owed at S1699 close); playbook §17 graduation criteria (owed at S1699 close); playbook §22 next-arc queue default (Group 1600 Content = default lean per S1599 close); memory rule `feedback_docs_cascade_at_every_close.md` (post-merge 4-step cascade discipline); memory rule `feedback_no_parallel_research_arcs.md` (sequential single-arc discipline — Group 1500 closed at S1599, Group 1600 opens at S1600 clean sequential); Chris ratified decisions D63-D68 via governance decision `2c469638-643d-4477-a8ea-1766b552eebe`.
- **Recommended next reads.** **S1601 Cat A ClaimsPack + Content Deliberation Pipeline (v2)** next per D66 P1 slot — child audit per playbook §11.2 20-section template + 6-parallel-Explore-sweep per §13 + parent-Claude verifier-loop per §14 on load-bearing pre-Explore claims + D62 = (a) 6-sibling exemplar mini-schema propagation-upfront pattern applied per D68 F8/F10 folds adopted. Session sequencing determined by Chris post-S1600 open: S1601 → S1602 → S1603 → S1604 → S1605 → S1606 → S1699 (7 sessions total; matches S1500 arc's 7-session shape + S1400 7-session shape).
- **Overall importance.** **Third parent scoping doc application of Chris's Phase 0 F.i/F.ii/F.iii methodology** after S1400 first + S1500 second — third-trigger confirmation for playbook v3 §11.1 template promotion **already TRIGGERED at S1599 close** per §12.4 discriminative-value criterion. **First library parent scoping doc to split load-bearing question into three orthogonal axes** (D65a/D65b/D65c) per Rigby F4 fold — precedent for future D59-analog arcs where load-bearing question carries multiple orthogonal design decisions. **First library parent scoping doc with F3 P3↔P4 swap based on canonical-decision-dependency reasoning** — Cat D moved before Cat C per Cat D's canonical object-model decision precedes Cat C's gate-semantic decision. **First library parent scoping doc to expand anti-scope from S1500's 12 items to 18 items** per Rigby F5 fold — Content-adjacent scope-magnets bounded out (content indexing/discoverability + search/ranking + permissions/moderation + notification fanout + attribution/analytics expansion + template system/channel integrations). **First library parent scoping doc to tighten §12.4 discriminative-value criterion at third application** per Rigby F6 fold — required decision-discriminative proof + required disconfirming evidence item prevent playbook v3 §11.1 promotion from passing on catalog-shape evidence alone. **First library parent scoping doc with F7 12-stage Lifecycle Traceability Table** including normalization/canonicalization + eligibility/packaging-gate stages distinct from publish gate. **First library parent scoping doc with F11 Cat E feedback-hazard note** — Cat E downstream by default but may emit constrained "must-have" findings requiring bounded correction in C/D (no re-scope) — Content-specific pattern-match to S1505 §14.1 F5 fold intent-neutrality precedent.
- **Distinguishing property.** **First library parent scoping doc where Chris's short-command directive triggered arc open immediately after prior arc close** — "Let's do Group 1600 next, I want to get all of the research done" typed at S1599 close, single-session gap between arc-close and next-arc-open (matches S1500 immediate-open-after-S1499 pattern). Sequential single-arc discipline per memory rule `feedback_no_parallel_research_arcs.md`. **First library parent scoping doc where Rigby Light SIGN cycle 1 produced 12 folds F1-F12** — largest single-cycle fold set in library history; matches Content-domain higher complexity (multi-axis posture-decision + 5 parallel deliverable-shaped models + 6+ service pipeline + 4 Rigby PA-tool surfaces + Discord broadcast chain + frontend). Index v34 → v35 updated per §10.1 (this §1.38 row + frontmatter v35 preamble + §8 timeline S1600 row).

---

### 1.39 `domains/content/1601_content_claims_pack_deliberation_pipeline_v2_audit.md`

- **Title.** S1601 Group 1600 Cat A — ClaimsPack + Content Deliberation Pipeline v2 (Child Audit) — **first child audit under Group 1600**.
- **Purpose.** Applies playbook §11.2 20-section child audit template to Cat A per parent D66 P1 slot: pre-publication truth machinery (ClaimsPackBuilder + content_claims + EvidencePackBuilder + ContentDeliberationRunner + ContentWriterAgent + DeliberationSession persistence). Resolves parent §3 Cat A load-bearing questions Q1 (citation integrity posture — Cat A enforces claims_count > 0 gate only, no per-claim regex verifier code-side; Cat B FactCheckReviewer is LLM prompt-based) + Q2 (v2 pipeline runtime posture — strictly on-demand; grep-verified zero beat entries; three triggers: REST + PA tool + Celery `.delay()`). Applies parent D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront at §4.8 + §5.6 + §6.5 + §8.5. Six parallel Explore sub-agents per playbook §13 + parent-Claude verifier-loop per §14 on 6 load-bearing pre-Explore claims.
- **Status.** `status: active` at S1601 commit. Rigby SIGN cycle 1 SIGN-with-edits at Medium confidence 2026-07-02 on fresh isolation pin `pa-9f075a024552b663`. F1-F6 folds landed pre-commit: F1 SelfBlog canonicalization-debt reframe (not island posture proof); F2 silent-partial-source severity MEDIUM → HIGH; F3 RAG scope explicit cross-tenant/workspace framing; F4 RAG scope = riskiest overall Cat A finding elevation; F5 fix "ZERO writes to Cat B/C/D" Exec Summary contradiction (corrected: ZERO writes to Cat B/C; ONE write to Cat D via SelfBlog.objects.create as persistence handoff); F6 verification-report endpoint boundary caution pin.
- **Research type.** Child audit (playbook §11.2 template). `authority: child-audit`, `category: child_audit`, `session: 1601`, `child_slot: P1`, `domain_slug: content`, `research_group: 1600`.
- **Boundary rule per parent F1 fold.** Cat A owns claims/evidence assembly + deliberation mechanics (pre-publication truth machinery). Does NOT own publish gating (Cat C), Deliverable base object model (Cat D), or 3-reviewer panel prompts / DecisionEnforcer internals (Cat B — handoff surface only via `run_reviews(draft, claims_pack, topic, domain)` + `ExecutionMandate.chosen_path`).
- **Load-bearing findings (8, Rigby-reordered per F2+F4 folds).** (1) **RIGHIEST OVERALL — HIGH cross-tenant/workspace data exposure risk** at `_from_user_documents` at `core/services/claims_pack_builder.py:245` (no user_id/workspace_id scoping; `content/models.py:879-887` filters only orphan exclusion); T1 R.CONTENT.RAG-SCOPE. (2) **HIGH** — per-claim citation-in-draft verification absent code-side; only non-empty ClaimsPack gate at `content_deliberation_runner.py:99-103`; T1 R.CONTENT.CITATION-INTEGRITY. (3) **HIGH** (Rigby F2 fold elevated MEDIUM → HIGH) — silent partial-source failure = truth/evidence integrity degradation without explicit degraded-status contract; `claims_pack_builder.py:70-85` swallows three source exceptions with `logger.warning`. (4) **MEDIUM** — direct ORM reads bypass service layer. (5) **MEDIUM** — SignalCluster `pattern_type` consumer-side gap CONFIRMED for Cat A (extends S1502 §14.3 6-arc COMPLETED). (6) **LOW** — `SpiderData` vs `LegacySpiderData` naming drift. (7) **LOW/POSTURE-PENDING** — rewrite pass hard-capped at 1 iter. (8) **LOW/POSTURE-PENDING** — `_build_operational_context` module boundary (Session 1001 telemetry injection helper location).
- **D65a HEADLINE evidence for xx99 (Rigby F1 fold reframed).** `SelfBlog.objects.create` at `core/services/content_deliberation_runner.py:401` bypasses `deliverable_factory` — **canonicalization debt Cat A flags as D65a evidence input, NOT proof of intentional island architecture**. Chris/xx99 selects posture at post-arc ADR; Cat A does not editorialize.
- **Cross-arc handoffs.** To S1602 Cat B: verify FactCheckReviewer per-claim citation enforcement mechanism (UNK-2); verify v1 vs v2 content_review_panel canonicalization (parent §6.1). To S1603 Cat D: consume `SelfBlog.objects.create` bypass as D65a HEADLINE evidence + SelfBlog vs Deliverable parallel-variant overlap (§17.3). To S1604 Cat C: consume Cat A citation-integrity guard placement question as D65b evidence. To S1605 Cat E: verify Document workspace FK schema (UNK-1) — resolves T1 R.CONTENT.RAG-SCOPE. To S1606 Cat F: consume §9 integration map + §14 drift + §15 debt + §17.1 ContentWriterAgent cross-domain overlap. To S1699 xx99: consume §19.6 T1-T5 follow-on queue + §14.1 naming reconciliation for §7 anchor-updates + §12.5 lifecycle stages 1-2 (evidence assembly + draft generation — Cat A rows of 12-stage F7-fold-expanded Deliverable Lifecycle Traceability Table).
- **Verifier-loop discipline.** Six parallel Explore sub-agents fired per playbook §13 (Agent 1 Models + Persistence; Agent 2 Services + Runtime Flows; Agent 3 APIs, Tools, Tasks, Commands; Agent 4 Integrations + Cross-Domain; Agent 5 Documentation + Prior Research; Agent 6 Drift + Debt + Ownership + Maturity). Parent-Claude verifier-loop applied per playbook §14 on 6 load-bearing pre-Explore claims (all verified pre-fire via direct file:line read: ClaimsPackBuilder class-def at :51; make_claim_id at :23 returns f'C-{sha256[:10]}'; ContentDeliberationRunner class-def at :21; ContentWriterAgent class-def at :207; zero beat entries via grep of `core/celery.py`; citation-integrity guard at :99-103). Rigby SIGN cycle 1 caught one Exec Summary contradiction (F5 fold — "ZERO writes to Cat B/C/D" vs Cat D persistence handoff) — corrected pre-commit; front-runs Rigby-grep-verification standard.
- **Dependencies.** Parent doc `1600_content_domain_scoping.md` (§1.38) — Cat A boundary F1 fold + Q1/Q2 load-bearing questions. Playbook §11.2 20-section child template + §13 six-parallel-Explore + §14 verifier-loop + §15 SIGN policy + §16 commit policy. S1501 (§1.31) — first-child structural precedent under Group 1500 + D62 4-item mini-schema exemplar. S1502 §14.3 6-arc SignalCluster pattern_type gap — pattern extended to Cat A. S1504 §5.1 + §14.3 sports cross-arc handoffs. Rigby memory rules: `feedback_verifier_loop_pattern.md` (verifier-loop pre-Explore claim verification); `feedback_rigby_sign_worker_instability_recovery.md` (SIGN batching 3-of-9 questions per turn to prevent turn-2 stall on 1640-line audit).
- **Recommended next reads.** S1602 Cat B Content Reviewers + Decision Enforcement child audit per D66 P2 slot; inherit S1601 §15.1 HIGH gap (FactCheckReviewer enforcement mechanism) + §17.2 v1-vs-v2 canonicalization boundary. Alternative near-term: **T1 R.CONTENT.RAG-SCOPE cross-arc verification** via Cat E S1605 or Memory arc for Document workspace FK (UNK-1) if Chris prioritizes closing the riskiest-overall finding pre-S1602.
- **Overall importance.** **First child audit under Group 1600 Content / Deliverables / Publishing arc.** Establishes evidence baseline for Cat B/C/D/E/F consumption + xx99 D65a/b/c three-axis posture-decision evidence plan. Applies D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront pattern per parent D68 F8/F10 folds — **first sibling of Group 1600 to propagate the pattern upfront** (S1600 parent scoping laid down the folds; S1601 is first application in a child audit). **D48 preemptive stability-probe gate 10th-arm outcome:** SIGN cycle 1 held clean at Medium confidence in three turns on fresh isolation pin `pa-9f075a024552b663`; no worker instability observed; sub-pattern extension anticipated to five-consecutive-fully-clean-arms **S1503+S1504+S1505+S1506+S1601** per D48 gate expectation at S1600 open.
- **Distinguishing property.** **First library child audit to resolve two parent load-bearing questions with binary posture verdicts in one session** — Q1 (per-claim citation absent code-side; two-gate policy is LLM-verified not code-enforced) + Q2 (strictly on-demand; grep-verified zero beat entries across five sweeps). Also **first Rigby SIGN cycle to catch an internal Exec Summary contradiction** (F5 fold: "ZERO writes to Cat B/C/D" vs Cat D persistence handoff at :401) — landed pre-commit as canonicalization-language precision improvement.

---

### 1.41 `domains/content/1603_content_deliverable_base_variants_audit.md`

- **Title.** S1603 Group 1600 Cat D — Deliverable Base + Specialized Variants (Child Audit) — **third child audit under Group 1600**.
- **Purpose.** Applies playbook §11.2 20-section child audit template to Cat D per parent D66 P3 slot (F3 fold: moved from P4 → P3 because Cat C's gate semantics consume Cat D's canonical object-model decision D65a-analog). Answers parent §3 D four evidence axes A1-A4: A1 Deliverable canonicalization scope; A2 PublishGate canonicalization scope; A3 central factory scope; A4 `publish_intent` enum coverage. Applies parent D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront at §4.8 (deliverable_type enum) + §5.6 (factory branches) + §6.5 (deliverable_tool actions) + §8.5 (lifecycle stages) per D68 F8/F10 folds — **third sibling of Group 1600 to propagate the pattern upfront** after S1601 first + S1602 second. Six parallel Explore sub-agents per playbook §13 + parent-Claude verifier-loop per §14 on 22 pre-Explore + 6 post-Explore load-bearing binary claims (grep-verified against HEAD `b8269101`).
- **Status.** `status: active` at S1603 commit. Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence 2026-07-02 (upgraded to High via F1 resolution) on fresh isolation pin `pa-8af9063864bf4a7f` (retired at S1603 close via `session_tool.retire`; `updated_count: 5, retired: true`). **F1-F18 folds landed pre-commit** (§20.5): F1 shadow-`create_deliverable` in `real_job_execution_consumer.py:99/200` RESOLVED as name-collision (returns plain dict for demo WebSocket UI; never touches ORM; NOT a factory bypass); F2 Cat D-adjacent services added (`deliverable_envelope.py`, `conversation_deliverable_extractor.py`, `platform_event_view.py`, `deliverables_consumer.py`); F3 5 factory-adopter mgmt commands added; F4 Deliverable base maturity explicit "current-scope definition"; F5 factory-adoption reconciliation; F6 D65a reframed to 3-category neutral taxonomy (envelope-integrated / standalone-by-design / unfinished-orphan); F7 triple-gate reframed as "separation-of-concerns lacking composition contract"; F8 OutreachDraft delivery HIGH → CRITICAL; F9 SelfBlog bypass nuanced; F10 T.15.5 description update; F11 T.15.6 type change to boundary_violation + "composition contract missing" reframe; F12 NEW T1 R.CONTENT.VARIANT-CATEGORIZATION-CLARIFICATION; F13 NEW T1 R.CONTENT.CANONICAL-CREATION-CONTRACT; F14 OutreachDraft delivery T2 → T1; F15 over-binary claims softened with grep-method disclosed; F16 Cat D/Cat C boundary tightened; F17 F1 resolved before commit (Option 1 per Rigby verdict); F18 maturity provisional rewound.
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: child-audit`, `category: child_audit`, `session: 1603`, `child_slot: P3`, `domain_slug: content`, `research_group: 1600`.
- **Boundary rule per parent F2 fold.** Cat D answers *"what IS the object?"* — Deliverable base + variants + schemas + lifecycle states + identity/dedupe/merge policy + variant typing + title/slug normalization + initiative linking/ownership attribution. Cat D does NOT own gates or publish rails (Cat C S1604 owns PublishGate at `publish_gate.py:27` + publish rails).
- **Load-bearing findings (D65a HEADLINE + top-tier T1 evidence).** **HEADLINE:** grep-verified NO reverse FKs from any variant to Deliverable base — all 5 variants (SelfBlog + OutreachDraft + ClosePack + SportsBettingBrief + BlockchainAuditBrief) are **structural islands** at the FK layer; only uni-directional Deliverable→SelfBlog + Deliverable→PodcastEpisode via Session 862 forward FKs at :192-207. `publish_intent` enum only on Deliverable base :131-136 (grep-negative on 5 variant model files). F6-reframed as **3-category neutral taxonomy** (envelope-integrated vs standalone-by-design vs unfinished-orphan) NOT normative integration-blocker claim. Central factory adoption **~98% at Deliverable base level** (`create_deliverable` at `deliverable_factory.py:752`; 2 legitimate production bypasses at `views_deliverables.py:305` clone + `workflow_orchestration_agent.py:5107` morning-brief; F1 RESOLVED that `real_job_execution_consumer.py:200` is name-collision demo, not bypass); **0% factory adoption on any variant**. **HIGH+CRITICAL debt:** T.15.2 SportsBettingBrief WRITE-ONLY-FORGOTTEN CONFIRMED at HEAD (2 writers `tasks_content.py:3150` + `tasks.py:12187`; no readers found via `rg` across core/; REST `get_betting_brief` at `views_odds_sports.py:3237` AllowAny bypasses persisted model) — S1504 §14.3 pattern class extension; T.15.3 BlockchainAuditBrief same pattern (1 writer `tasks.py:12240`; no readers found); T.15.4 OutreachDraft delivery MISSING F8-upgrade from HIGH → CRITICAL (S1402 F.B1 CONFIRMED at HEAD: no `send_outreach|dispatch_outreach|sendgrid|postmark|mailgun|smtplib` found via `rg` in mainline production); T.15.1 SelfBlog canonical bypass at `content_deliberation_runner.py:401` HIGH (16+ sites; factory invariants ALL skipped: content_hash dedup, publish_intent resolution, provenance receipt, orphan diagnostic); T.15.6 Triple-gate architecture F7+F11 reframed as boundary_violation + "composition contract missing" HIGH (5-gate factory at :358-411 + PublishGate 4-threshold at `publish_gate.py:44-49` + SelfBlog own quality gate at `models_unified_system.py:20708-20728` — no canonical precedence statement; escalated from parent §6.3 parked issue).
- **D65a/D65b/D65c evidence contributions.** D65a (Deliverable canonicalization): **structural island posture confirmed at reverse-FK layer + 3-category taxonomy for variants** (2 envelope-integrated / 2 standalone-by-design provisional / 2 unfinished-orphan CRITICAL). Publisher-side: 98% factory adoption at base + 0% at variants. F1 resolved shadow-method concern. D65b (PublishGate canonicalization): triple-gate composition contract MISSING — Cat C S1604 owns resolution; Cat D contributes evidence. D65c (Lifecycle transition ownership): Cat D owns stages 1-8 + 12 of the 12-stage lifecycle traceability table; Cat C owns 9-11. `publish_intent` structural blocker for integration posture (only on base).
- **Cross-arc handoffs.** To S1604 Cat C: T.15.6 triple-gate composition contract resolution + §8.4 lifecycle stages 9-11 owned by Cat C + UNK-2 Newsletter dry_run promotion path + UNK-4 gate canonicalization. To S1605 Cat E: §14.4 status='completed' full drift resolution + UNK-1 Session 1248 P2b workaround assessment + UNK-3 `deliverable_tool.update` silent-fallback bug + Cat E owns final PA-tool contract sweep. To S1606 Cat F: §4.2 five-variant structural-island confirmation as D65a HEADLINE + §9 integration edge table (5 MISSING reverse FKs) + §16.3 SelfBlog canonical bypass + §17.4 five-variant overlap analysis. To S1699 xx99: §19 T1 recommendations feed §5 Chris-gated decision brief (D65a/D65b/D65c three-axis posture selection) + §14.8 drift matrix + §15 debt matrix + UNK-1 through UNK-5 → §6 unresolved unknowns + §11 documentation gaps → §7 anchor-update recommendations (topic-doc landing + DATABASE_MODEL_REFERENCE refresh).
- **Verifier-loop discipline.** Six parallel Explore sub-agents fired per playbook §13. Parent-Claude verifier-loop applied per playbook §14 on 22 pre-Explore load-bearing claims (F0 pre-Explore drift correction: central factory at `:752` not `:1269`; :1269 is `Deliverable.objects.create(**kwargs)` call inside function body) + 6 post-Explore binary claims (F0b post-Explore correction: content_hash NOT dead-write — factory queries at :955-970 for 72h dedup; reverse-FK grep-negative CONFIRMED; publish_intent variant-negative CONFIRMED; td_handlers_agents.py:2052 status='completed' hardcode CONFIRMED with Session 1248 P2b workaround comment at :2091-2109; 4 god-services >3000 lines confirmed; S1504 §14.3 + S1402 F.B1 CONFIRMED at HEAD). Rigby SIGN cycle 1 surfaced 18 folds (F1-F18) via batched A/B/C + final-verdict single-question follow-up; F1 shadow-method concern RESOLVED via parent-Claude direct-read verification (name-collision, not bypass) — allowed confidence upgrade 0.75 → High per Rigby Batch C Q9 must-change Option 1 verdict.
- **Dependencies.** Parent doc `1600_content_domain_scoping.md` (§1.38) — Cat D boundary + §3 D A1-A4 evidence axes + §5 D66 P3 slot per F3 fold + parked issues §6.3 (5-gate vs 4-threshold) + §6.5 (SportsBettingBrief/OutreachDraft cross-arc disposition ownership). Sibling audits `1601_content_claims_pack_deliberation_pipeline_v2_audit.md` (§1.39) — §9.1 SelfBlog.objects.create bypass at runner:401 = D65a HEADLINE evidence input; `1602_content_reviewers_decision_enforcement_audit.md` (§1.40) — §16.1 Cat B write to SelfBlog.stats_snapshot['deliberation'] at runner:415 = D65a HEADLINE evidence input. Cross-arc: `1504_sports_betting_content_pipeline_audit.md` (S1504 §14.3 WRITE-ONLY-FORGOTTEN pattern precedent); `1402_revenue_outreach_composition_delivery_audit.md` (S1402 F.B1 delivery MISSING); `1403_revenue_engagement_inbound_audit.md` (S1403 F.C4 ContentEngagement docstring drift). Playbook §11.2 20-section child template + §13 six-parallel-Explore + §14 verifier-loop + §15 SIGN policy + §16 commit policy. Rigby memory rules: `feedback_verifier_loop_pattern.md`; `feedback_rigby_sign_worker_instability_recovery.md`; 5 Cat D-relevant memory rules (`feedback_publish_intent_enum.md`, `feedback_deliverable_create_defaults_to_completed.md`, `feedback_deliverable_status_via_content_complete.md`, `feedback_deliverable_tool_use_append_for_large_payloads.md`, `feedback_deliverable_workspace.md`).
- **Recommended next reads.** **S1604 Cat C PublishGate + Publish Rails** next per D66 P4 slot (moved from P3 → P4 per parent F3 fold because Cat C consumes Cat D's canonical decision D65a-analog). S1604 inherits S1603 T.15.6 triple-gate composition contract MISSING as CORE debt + §8.4 lifecycle stages 9-11 as CAT C-OWNED scope + UNK-2 Newsletter dry_run promotion path + UNK-4 gate canonicalization + §14.3 triple-gate boundary evidence. Alternative near-term: **T1 R.CONTENT.RAG-SCOPE cross-arc verification** via Cat E S1605 or Memory arc (S1601 riskiest overall finding preserved through S1602 §19.6 T-slot rank).
- **Overall importance.** **Third child audit under Group 1600 Content / Deliverables / Publishing arc.** Establishes Cat D evidence baseline for Cat C/E/F consumption + xx99 D65a/b/c three-axis posture-decision evidence plan. **Third sibling of Group 1600 to propagate D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront pattern** — extends 6-arc Group 1500 pattern to Group 1600 third-application validation. **D48 preemptive stability-probe gate 12th-arm CONFIRMED — seven-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603 CONFIRMED** — extends 11-arc pattern S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506+S1601+S1602 to 12-arc + S1603. Codification-ready-STRENGTHENED for playbook v3 §15 with 7-consecutive-fully-clean sub-pattern.
- **Distinguishing property.** **First library child audit to reframe an "island posture" claim from binary structural-fact framing to 3-category neutral taxonomy** via Rigby SIGN Batch B fold (envelope-integrated vs standalone-by-design vs unfinished-orphan) — prevents S1274 EventBus-style over-interpretation of structural absence as functional gap. **First library child audit to RESOLVE a shadow-factory concern via direct-read name-collision verification** (F1: `real_job_execution_consumer.py:200` shadow `create_deliverable` returns plain dict for demo WebSocket UI, never touches ORM). **First library child audit to reframe a triple-system debt item from "duplicate_model" to "boundary_violation + composition contract missing"** (F7+F11 fold on T.15.6). **First library child audit to reach Rigby SIGN cycle 1 SIGN-with-edits verdict with 18 folds landed pre-commit** — largest fold count in the library reflects the audit's scope + Rigby's substantive engagement across A/B/C batches.

---

### 1.40 `domains/content/1602_content_reviewers_decision_enforcement_audit.md`

- **Title.** S1602 Group 1600 Cat B — Content Reviewers + Decision Enforcement (Child Audit) — **second child audit under Group 1600**.
- **Purpose.** Applies playbook §11.2 20-section child audit template to Cat B per parent D66 P2 slot: pre-publish gating (3-reviewer panel `SkepticReviewer` + `FactCheckReviewer` + `DomainPersonaReviewer` conditional + `run_reviews` dispatch + `DecisionEnforcerAgent` + single rewrite pass + synthetic-FAIL handling). Resolves parent §3 Cat B load-bearing questions Q1 (reviewers are PURE-FUNCTION MODULE-LEVEL dispatch via `content_review_panel_v2.py:88,107,124,208`; NOT class-based) + Q2 (v2 canonical for deliberation pipeline; v1 `ContentReviewPanel` at `content_review_panel.py:61` = PARTIALLY-ADOPTED-LIVE-SECONDARY via ContentWriterAgent:1376-1377 under `ENABLE_CONTENT_REVIEW=True` at :62; S1274 EventBus lesson properly applied). Applies parent D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront at §4.8 + §5.6 + §6.5 + §8.5 (second sibling of Group 1600 to propagate the pattern upfront after S1601 first). Six parallel Explore sub-agents per playbook §13 + parent-Claude verifier-loop per §14 on 7 pre-Explore + 3 post-Explore load-bearing binary claims (grep-verified `queue_agent_task` MISSING + `gpt-5.2` valid internal ID + v1 partially-adopted).
- **Status.** `status: active` at S1602 commit. Rigby SIGN cycle 1 SIGN-with-edits at High confidence 2026-07-02 on fresh isolation pin `pa-1c5298d807d7a1d2` (retired at S1602 close via `session_tool.retire`; `updated_count: 4, retired: true`). F1-F7 folds landed pre-commit: F1 §5.5 ConversationOrchestrator critique reframed as Cat B decision-production substrate; F2 §3.5 `_extract_decision` at runner :266-284 explicitly Cat B-OWNED; F3 §1 "all v2 deliberation deployment paths" scope tightening (v1 direct-write does NOT touch v2 panel); F4 §4.2 + §13 MandateStatus lifecycle correction (mark_killed at :404-407 + mark_completed at :409-411 CODED but ZERO callers in deliberation flow — dormant state machine NOT missing machinery); F5 §1 finding #3 + §7.2 branch 8 + §15.3 spawn_tasks_from_mandate correction (broad try/except guard at :455/:474-476 → exception-swallowed silent failure NOT unhandled crash); F6 §15.3 CRITICAL → HIGH latent-landmine + §19.6 T-slot rank #3/#4 reorder; F7 §15.10 `_detect_domain` 0.2 threshold MED → LOW (unvalidated tuning knob without misclassification evidence).
- **Research type.** Child audit (playbook §11.2 template). `authority: child-audit`, `category: child_audit`, `session: 1602`, `child_slot: P2`, `domain_slug: content`, `research_group: 1600`.
- **Boundary rule per parent F1/F8 fold.** Cat B owns *pre-publish gating: whether the draft passes reviewer verdicts + decision-enforcement contract*. Does NOT own downstream quality thresholds (Cat C S1604 owns PublishGate thresholds at `publish_gate.py:44-49`) or Deliverable base object model (Cat D S1603).
- **Load-bearing findings (7 ranked for xx99 §5 evidence plan).** (1) **HIGH CONFIRMED** — End-to-end LLM-prompt-only citation contract across A+B; no code-side per-claim `[C-xxxxxxxxxx]` regex/typed-constraint verifier at either gate (extends + fully resolves S1601 §15.1 UNK-2). Cat A's `claims_count == 0` gate at runner:99-105 is binary; Cat B FactCheckReviewer prompt at v2:107-122 is LLM inference only. T1 R.CONTENT.CITATION-INTEGRITY. (2) **HIGH** — Silent draft truncation at 8000 chars in v2 reviewers (`content_review_panel_v2.py:236` `draft[:8000]`) — reviewers PASS/FAIL on partial evidence; 1500-word target drafts exceed threshold. Extends S1601 F2 silent-partial-source pattern. T1 R.CONTENT.CAT-B-TRUNCATION. (3) **HIGH latent-landmine (F6 severity fold from CRITICAL)** — `queue_agent_task` MISSING from `core/tasks.py` (grep-verified zero definitions); `spawn_tasks_from_mandate` at `decision_enforcer_agent.py:456` imports missing task with broad try/except guard at :455/:474-476 → exception-swallowed silent failure; zero production callers; invalidates patent operational claim at `DISCLOSURE_F.md:140` + trivially-triggerable landmine. T1 R.CONTENT.CAT-B-SPAWN-TASKS. (4) **HIGH** — Cat B mandate + reviewer verdicts have ZERO PA-tool outbound channel; only readback via REST `/api/blog/<uuid>/deliberation/` at `views_deliberation.py:320-386`. Extends S1402 F.B1 ZERO outbound channel pattern to content Cat B — CONFIRMED. T1 R.CONTENT.CAT-B-OUTBOUND. (5) **MED** — ConversationOrchestrator hardcodes critique agents (EditorAgent + ContentStrategyAgent at runner:252-253); contradicts v2 DomainPersonaReviewer conditional pattern. (6) **MED** — Single-iteration rewrite pass; no convergence loop; DecisionEnforcerAgent NOT re-invoked post-rewrite. (7) **MED** — DeliberationSession retention unbounded (migration 0232 + 0283 add classification but no cleanup task).
- **D65a/D65b/D65c evidence contributions.** D65a (SelfBlog canonicalization): Cat B writes `deliberation_meta` to `SelfBlog.stats_snapshot['deliberation']` at runner:415 bypassing `deliverable_factory` (extends S1601 §9.1 F1 fold canonicalization-debt reframe to Cat B). D65b (citation-integrity policy): CONFIRMED HIGH end-to-end LLM-prompt-only + silent-truncation pattern. D65c (lifecycle-transition ownership): MandateStatus `mark_killed`/`mark_completed` CODED but never called from deliberation flow (dormant state machine); DecisionEnforcerAgent + spawn_tasks_from_mandate ownership fragmentation.
- **Cross-arc handoffs.** To S1603 Cat D: consume `SelfBlog.stats_snapshot['deliberation']` write bypass as D65a evidence input (F1-analog canonicalization-debt reframe applies). To S1604 Cat C: Cat B `decision` → PublishGate hand-off contract; `blog.status='needs_enhancement'` recovery envelope depends on Cat C `auto_enhance_blogs` beat. To S1605 Cat E: Cat B ZERO PA-tool coverage on verdicts + mandate — resolution owed by Cat E surface. To S1606 Cat F: Cat B ZERO outbound learning-loop / memory / signal-engine / Discord feedback — cross-domain integration lens. To S1699 xx99: three axes evidence inputs per D65a/D65b/D65c framing.
- **Verifier-loop discipline.** Six parallel Explore sub-agents fired per playbook §13. Parent-Claude verifier-loop applied per playbook §14 on 7 pre-Explore load-bearing claims (all verified pre-fire: SKEPTIC_SYSTEM at v2:88 + FACTCHECK_SYSTEM at v2:107 + DOMAIN_SYSTEM_TEMPLATE at v2:124 + run_reviews at v2:208 + DecisionEnforcerAgent class-def at decision_enforcer_agent.py:60 + fallback logic at runner:266-284 + rewrite pass at runner:107-116) + 3 post-Explore binary claims (queue_agent_task MISSING confirmed via zero core/tasks.py hits; gpt-5.2 valid internal ID via 14-file grep — Explore SPECULATIVE flag RETRACTED; v1 ContentReviewPanel PARTIALLY-ADOPTED-LIVE-SECONDARY confirmed via ContentWriterAgent:1376-1377 + ENABLE_CONTENT_REVIEW=True at :62). Rigby SIGN cycle 1 surfaced 2 factual corrections via grep (F4 MandateStatus + F5 spawn_tasks_from_mandate) + 2 severity re-ranks (F6 CRITICAL → HIGH + F7 MED → LOW).
- **Dependencies.** Parent doc `1600_content_domain_scoping.md` (§1.38) — Cat B boundary + Q1/Q2 load-bearing questions. Sibling audit `1601_content_claims_pack_deliberation_pipeline_v2_audit.md` (§1.39) — §14/§15/§20.6 cross-arc handoffs to Cat B; UNK-2 fully resolved by S1602. Playbook §11.2 20-section child template + §13 six-parallel-Explore + §14 verifier-loop + §15 SIGN policy + §16 commit policy. Rigby memory rules: `feedback_verifier_loop_pattern.md`; `feedback_rigby_sign_worker_instability_recovery.md` (SIGN batching 3-of-9 questions per turn — extended to include Batch C/C partial-deflection recovery via single-question follow-up).
- **Recommended next reads.** **S1603 Cat D Deliverable Base + Specialized Variants** next per D66 P3 slot (F3 fold: Cat D moved from P4 → P3 because Cat C's gate semantics consume Cat D's canonical object-model decision D65a-analog). S1603 inherits S1601 §9.1 SelfBlog.objects.create bypass + S1602 §16.1 canonicalization-debt reframe as D65a HEADLINE evidence. Alternative near-term: **T1 R.CONTENT.RAG-SCOPE cross-arc verification** via Cat E S1605 or Memory arc (S1601 riskiest overall finding preserved as #1 in S1602 §19.6 T-slot rank).
- **Overall importance.** **Second child audit under Group 1600 Content / Deliverables / Publishing arc.** Establishes Cat B evidence baseline for Cat C/D/E/F consumption + xx99 D65a/b/c three-axis posture-decision evidence plan. **Second sibling of Group 1600 to propagate D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront pattern** — extends 6-arc Group 1500 pattern to Group 1600 second-application validation. **D48 preemptive stability-probe gate 11th-arm outcome:** Batches A/C + B/C substantive; Batch C/C partial deflection (not full jam); final-verdict single-question turn returned clean in <10s. **Six-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602 CONFIRMED** — extends 10-arc pattern S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506+S1601 to 11-arc + S1602. Codification-ready-STRENGTHENED for playbook v3 §15 per S1599 §10.2 6-candidate codify list.
- **Distinguishing property.** **First library child audit to encounter Rigby SIGN Batch C/C partial-deflection pattern with clean single-question follow-up recovery** — new recovery-pattern candidate for playbook v3 §15 alongside D45 titles-only recovery + S1504 verdict-text re-request recovery. **First library child audit to fully resolve a prior-sibling UNK gap in one session** — S1601 §15.1 UNK-2 fully resolved to CONFIRMED HIGH via S1602's Cat B code inspection. **First library child audit to grep-verify SPECULATIVE flag retraction** — Explore Agent 2's `gpt-5.2` SPECULATIVE flag retracted via 14-file grep confirming valid internal LLM routing target. **First library child audit to have Rigby grep-verify 2 factual corrections against the audit's own claims** (F4 MandateStatus lifecycle transitions exist + F5 spawn_tasks try/except guard exists) — reinforces the "trust but verify" rule bidirectionally: parent-Claude verifies pre-Explore + Rigby verifies post-draft.

---

### 1.37 `domains/sports/1599_sports_canonical_summary.md`

- **Title.** S1599 Group 1500 Sports/DBAO/Intelligence — Canonical Summary (xx99 arc-close per playbook §11.3 12-section template)
- **Purpose.** Seventh and final slot under Group 1500. Consumes P1-P6 child audit outputs (S1501 Cat A + S1502 Cat B + S1503 Cat C + S1504 Cat D + S1505 Cat E + S1506 Cat F) and produces the cross-cutting view no single child could deliver: sports-subsystem shape map + four-axis compound-maturity pattern catalog + §3.2 Sports Domain Lifecycle Traceability Table per parent §12.5 F.iii requirement + resolved contradictions between siblings + D59-load-bearing xx99 §5 posture-decision evidence brief (integration vs island; **explicit Chris-gated selection tag** per D59) + §7 anchor-update recommendations + ranked T1-T10 follow-on queue + §10 meta-methodology **third application** after S1399 first + S1499 second. Bounded synthesis of Group 1500 child audit outputs per playbook §11.3 rules; no new §13 6-parallel-Explore sweep; no new file:line evidence; no CANDIDATE → CONFIRMED resolutions.
- **Status.** `status: active` at S1599 commit (Chris commit-gate pending). Rigby Full SIGN cycle 1 pending on fresh isolation pin — **D48 preemptive stability-probe gate 10th arm** anticipated; five-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1599 anticipated if held clean.
- **Research type.** Canonical summary (playbook §11.3 12-section template). `authority: research`, `category: canonical_summary`, `child_slot: P7`.
- **Primary contributions.**
  - **§3.4 Four-axis compound-maturity shape** — NEW arc-level maturity framing produced by Cat F consumption + arc-wide synthesis. Sports domain maturity is not one category but four compound axes: (1) DBAO product-line materialization axis = NAMING-CONVENTION-WITHOUT-MATERIALIZATION; (2) Intelligence surface axis = flag layer DECLARED-GATES-NOTHING + engine layer LATENT-ZERO-FIRE + REST/frontend layer DOMAIN-NEUTRAL; (3) Discord sports surface axis = read commands HOT-PATH-CHOKE-BYPASS + write commands WORKING + digest DUAL-COORDINATOR-BYPASS; (4) Cross-domain feedback surface axis = DECOUPLED-VERIFICATION-SYSTEMS + PARTIAL-LEARNING-BRIDGE + zero SignalCluster emission.
  - **§3.2 Sports Domain Lifecycle Traceability Table** — parent §12.5 F.iii deliverable. 8 lifecycle stages: odds ingestion + fixture/entity identity resolution + normalization + prediction + user wager + outcome verification + learning-loop feedback + signal aggregation gap. 1 of 8 stages MISSING (Stage 8 Signal Aggregation — 6-arc consumer-side pattern COMPLETED gap); 1 of 8 UNKNOWN+MISSING resolver (Stage 2 fixture/entity identity per parent §12.5 Rigby SIGN cycle 1 Q8 fold); 5 of 8 LIVE-BUT-DRIFTING; 1 of 8 IMPLICIT (Stage 3 Normalization — no dedicated service). No stage is CLEAN-END-TO-END.
  - **§5 D59 posture-decision evidence brief** — LOAD-BEARING deliverable per D59. 7 integration criteria (A1-A7 SignalCluster emit + coordinator gate + learning bridge coverage + engine auto-start + verification linkage + flag+IntelligencePage reality + DBAO materialized) + 7 island criteria (B1-B7 sports-native aggregator + sports-scoped memory + sports-native retrain + coordinator sole read gate + DBAO app label + sports-native engine + flag replaced by product-line boundary) + 4 cross-cutting C1-C4 (CODEOWNERS + topic doc + integration tests + BettingPage tests) + failure-mode table D + cost asymmetry summary E (integration MED / island HIGH-MED; DBAO materialization drives cost asymmetry either direction) + **F2-fold scoring rubric F applied uniformly across P1-P6 evidence corpus**. **Aggregate current-state score at HEAD `5a8d3d75`: ALL 22 criteria score FAIL** — load-bearing observation "BOTH postures require substantive investment; neither is a default." **Explicit "Chris-gated selection" tag** — xx99 does NOT select; Chris ratifies post-arc via ADR per D59.
  - **§4 Thirteen cross-cutting pattern classes** — 5 NEW at S1506 (P1-P5) + 5 NEW at other categories (P6-P10) + 3 INHERITED (P11 6-arc COMPLETED + P12 5-arc + P13 2-arc). Meets ≥2-child threshold per playbook §11.3 §5 F1-F4 methodology precedent.
  - **§8 T1-T10 follow-on queue** — matching S1499 T1-T10 shape. T1 Chris-gated ADRs (R.SPORTS.POSTURE + R.DBAO.CODENAME) + CRITICAL remediation sequences (R.C1 ← R.C2 verify-beat gate + R.D1 ← R.D2 digest-beat gate + R.D3 zero-test-coverage reliability multiplier + R.D4 SportsBettingBrief consumer-or-remove ← T1.a + R.D5 two-writer dedup); T2 12 design-preparation tracks (SignalCluster bridge + verification reconciliation + Discord refactor + MOCK-DATA-CONSUMER cleanup + fixture identity + DEAD-RENDER-PATH cleanup + operational cadence + Bankroll reconciliation + auth-drift + test coverage + topic doc + BettingPage split); T3 6 Employee OS + delegated (CODEOWNERS + Learning bridge extend + RealtimeIntelligenceEngine bootstrap + Retention + Channel owner + Ownership consolidation); T4 11 cleanup PRs (DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT P4 3-child + mock config consolidation + SportsDataSpider disposition + doc-drift fixes + DBAO artifact cleanup coupled to T1.b + intelligence-flag literal cleanup coupled to T1.a); T5 6 optional. Includes visual blocking dependency graph.
  - **§10 meta-methodology third application** with **§12.4 discriminative-value criterion check** per parent §12.4 + Rigby SIGN cycle 1 Q7 fold. 4 of 4 evidence types satisfied (Scope confusion prevented via D60 Intelligence bound-out + Rework reduced via §11.4 F.ii boundary + Cleaner arc close via 6-of-6 SIGN-with-edits + Chris-lock efficiency via single "agree all + D-6=(a)" round D56-D61). Threshold met — includes both (Scope confusion prevented) AND (Cleaner arc close). **Playbook v3 §11.1 template promotion TRIGGERS.**
  - **§7 Anchor-update recommendations** — `PLATFORM_INVENTORY.md` §3.10 refresh (subdivide Sports category + DBAO subgroup conditional on T1.b) + `PLATFORM_WHAT_IT_IS.md` Sports narrative refresh (four-axis compound-maturity framing) + `docs/research/ARCHITECTURE_INDEX.md` v33 → v34 (§1.37 registration + §8 timeline S1599 row + §5 gap consolidation + §7 decision matrix update + §9 roadmap update + v34 preamble) + `docs/research/OPEN_ARCS.md` Group 1500 in-progress → closed + NEW `docs/topics/sports-betting.md` (C2 cross-cutting gate) + `.github/CODEOWNERS` 6 sports runtime files (post-arc T3).
- **Load-bearing deliverables.** §1 Executive Summary (500-800 words compliance) + §2 Per-child rollup of 28 canonical questions across 6 siblings + §3 Consolidated Domain Shape (§3.1 Category matrix + §3.2 Sports Domain Lifecycle Traceability Table + §3.3 Two-Axis Sports Architecture + §3.4 Four-Axis Compound-Maturity Shape + §3.5 Load-bearing consequence table) + §4 Thirteen cross-cutting pattern classes (P1-P13) + §5 D59 posture-decision evidence brief + §6 Unresolved Unknowns U1-U23 categorized by tier + §7 Anchor-Update Recommendations (§7.1-§7.4) + §8 Follow-On Research Queue T1-T5 with dependency graph + §9 Cross-Links to Delegated Arcs (post-arc ADRs + S1300 Memory + Group 1600 Content + Group 1700 Observability + T2 tracks) + §10 What This Research Taught Us About How to Do Research (10.1 what worked + 10.2 codify-to-playbook-v3 candidates with two-triggers rule check + 10.3 anti-patterns + 10.4 playbook suggestions + 10.5 xx99 template suggestions) + §11 Arc Change Log (per-child + xx99 SIGN verdicts + folds landed) + §12 Appendix — Provenance (12.1-12.8 including pattern-class enumeration + post-arc T-slot summary + playbook v3 promotion status).
- **Verifier-loop discipline.** Bounded synthesis per playbook §11.3 §5-§7 canonical-summary rules; every load-bearing claim cites source child audit via `SNNNN §NN.N` anchor. No new file:line evidence; no CANDIDATE → CONFIRMED resolutions. F2-fold scoring rubric (S1506 §20.6 §F) applied uniformly across P1-P6 evidence corpus per Cat F handoff contract. §12.4 discriminative-value criterion check applied per parent §12.4 + Rigby SIGN cycle 1 Q7 fold — 4 of 4 evidence types satisfied. Rigby SIGN cycle 1 pending on fresh isolation pin; D48 preemptive stability-probe gate 10th arm (five-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1599 anticipated). Cycle 2 SIGN-clean at High confidence anticipated per §11.3 canonical-summary bounded-work + evidence-consolidation-not-new-audit precedent.
- **Inherited findings referenced.** All 6 child audits' §14 drift + §15 debt + §17 duplicates + §18 ownership + §19 future research + §20 deliverables to xx99 consolidated. Particularly load-bearing: S1506 §20.6 posture-decision evidence plan (D59 verbatim consumption into §5); S1506 §20.7 lifecycle table stub (assembled full at §3.2); S1506 §20.9 6-arc consumer-side pattern completion (§4.11 P11 pattern); S1506 §20.10 6-sibling exemplar pattern completion (§10.2 codify-to-playbook-v3 candidate for D62 = (a)); S1502 §15 debt #12 fixture identity F6 fold (§4.13 P13 2-arc pattern); S1503 §14.1 CRITICAL zero-fire pattern (§4.9 P9 first application); S1503 §15.14 F7 fold pre-restore-beat idempotency gate (§8 T1.d + T1.f blocking gate); S1504 §14.3 WRITE-ONLY-FORGOTTEN (§4.8 P8 first application); S1504 §15.12 F4 fold zero-test-coverage as reliability multiplier (§8 T1.g CRITICAL tier); S1505 §14.1 MOCK-DATA-CONSUMER (§4.6 P6 first application); S1505 §14.2 DEAD-RENDER-PATH (§4.7 P7 first application); S1274 §14 Finding #6 SignalCluster pattern_type gap (§4.11 P11 COMPLETED across 6 arcs); S1274 §12.3 two-legitimate-postures precedent (§5 D59 evidence-plan framing).
- **Dependencies.** Parent scoping `1500_sports_domain_scoping.md` (§5 P1-P7 mission sequence Chris-locked D57; §12.1 arc-close deliverables owed to xx99; §12.4 discriminative-value criterion; §12.5 F.iii Sports Domain Lifecycle Traceability Table requirement including fixture/entity identity resolution row per Q8 fold; §12.6 F.iii NOT try to answer boundary); sibling audits S1501-S1506 (all 6 child audits owe §2.1 contract statements + §14 drift + §15 debt + §17 duplicates + §18 ownership + §19 future research + §20 deliverables to xx99); precedent canonical summaries `1399_memory_canonical_summary.md` (first §10 meta-methodology application) + `1499_revenue_canonical_summary.md` (second §10 application; T1-T10 tier structure precedent + §12.4 discriminative-value criterion check precedent); `DOMAIN_RESEARCH_PLAYBOOK.md` §10 canonical summary responsibilities + §11.3 12-section template + §14 verifier-loop rules + §15 canonical summary SIGN policy + §16 arc-close discipline + §17 graduation criteria; `RESEARCH_OPERATING_SYSTEM.md` §9 arc-close contract; memory rule `feedback_docs_cascade_at_every_close.md` (post-merge 4-step cascade discipline + `build_docs_provenance`).
- **Recommended next reads.** After xx99 commits + PR merges + docs cascade completes, **post-arc T-slots**: T1.a R.SPORTS.POSTURE ADR (Chris-gated); T1.b R.DBAO.CODENAME ADR (Chris-gated coupled to T1.a); T1.c-i CRITICAL remediation sequences (verify-beat + digest-beat + concurrency-safety + idempotency + zero-test-coverage + consumer-or-remove + dedup); T2 12 design-preparation tracks (posture-tied); T3 Employee OS + Memory + Observability delegations; T4 cleanup PRs; T5 optional. Playbook v3 §11.1 promotion session (post-arc): consumes xx99 §10.2 codify-to-playbook-v3 candidate list (6 candidates: D48 preemptive stability-probe gate 9-arc; D62 = (a) 6-sibling exemplar pattern; F2-fold scoring rubric; BEFORE-SIGN Rigby ORM probe conditional; S1504 verdict-text re-request recovery; S1505 Rigby Q8 grep-verified confidence-upgrade). NEW `docs/topics/sports-betting.md` first-inventory landing (post-arc T2.k / C2 cross-cutting gate).
- **Overall importance.** **Third application of playbook §11.3 §10 meta-methodology template** after S1399 first + S1499 second — non-negotiable per Chris directive S1399 close 2026-07-01. **Third xx99 canonical summary in the library** (S1399 Memory + S1499 Revenue + S1599 Sports); establishes 3-arc precedent for playbook §11.3 template shape. **First xx99 to carry a D59-analog posture-decision evidence brief as §5** — evidence-consolidation NOT posture selection; Chris ratifies post-arc via ADR. **First xx99 to apply F2-fold scoring rubric across P1-P6 evidence corpus** — S1506 SIGN cycle 1 Q15 Batch 3 fold added rubric at Cat F; xx99 applies uniformly. **First xx99 to consolidate a Four-Axis Compound-Maturity Shape** as arc-level maturity framing — Sports domain not one category but four axes each with distinct verdict. **First xx99 where all 22 posture criteria score FAIL at HEAD** — exposing load-bearing observation "BOTH postures require substantive investment; neither is a default." Chris post-arc ADR judges which set of PASS-transitions is preferable. **First xx99 to demonstrate 4-of-4 discriminative-value evidence types satisfied at §12.4 criterion check** — playbook v3 §11.1 template promotion TRIGGERS with concrete evidence. **First xx99 to codify D48 preemptive stability-probe gate at 9-arc CODIFICATION-READY threshold** with four-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506. **First xx99 to complete a 6-arc consumer-side pattern (P11 Sports ↔ Signal Engine SignalCluster emit gap)** — inherited from S1274 §14 Finding #6; extended across all 6 sibling arcs; completed at S1506; consolidated at xx99 §4.11.
- **Distinguishing property.** **First library canonical summary designed as a D59-analog posture-decision evidence brief carrier** — §5 is the load-bearing D59 deliverable per parent §12.1 F.iii item 3; explicit Chris-gated selection tag. Structural precedent for future domain arcs where posture-decision framing is the load-bearing deliverable. **First library canonical summary to apply F2-fold scoring rubric uniformly across P1-P6 evidence corpus** — makes §5 posture-decision brief consumable without post-hoc scoring criteria. **First library canonical summary to produce Four-Axis Compound-Maturity Shape** at §3.4 — arc-level maturity framing that generalizes to any domain where cross-domain lenses reveal multi-axis maturity. Suggested for playbook v3 §11.3 §3 optional shape per §10.4 suggestion 1. **First library canonical summary where 22 of 22 posture criteria score FAIL** — the aggregate current-state score exposition clarifies "no default posture exists" and is a load-bearing observation for the Chris post-arc ADR. **First library canonical summary to demonstrate 4-of-4 §12.4 discriminative-value evidence types** — includes both (Scope confusion prevented) AND (Cleaner arc close) satisfying Rigby SIGN cycle 1 Q7 fold requirement. **First library canonical summary to produce a T1-T5 follow-on queue with visual blocking dependency graph** — §8 diagram shows T1.a → T2/T3/T4 blocking relationships in a single view. Index v33 → v34 updated per §10.1 (this §1.37 row + frontmatter v34 preamble + §8 timeline S1599 arc-close row).

---

### 1.35 `domains/sports/1505_sports_frontend_surface_audit.md`

- **Title.** S1505 Sports Frontend Surface — Child Audit (Category E / P5 under Group 1500)
- **Purpose.** Fifth child audit under Group 1500. Answers the 28 playbook §9 canonical questions for Category E — the user-facing frontend sports surface: `/betting` route at `frontend/src/App.tsx:89` inside `ProtectedRoute` (App.tsx:47-59) + `BettingPage.tsx` 3,023-line single-page god-component + `BettingTab` union at BettingPage.tsx:14 declaring 11 tabs with 9 rendered via `tabs` array (lines 16-26) + 2 DEAD-RENDER-PATH tabs (markets/bankroll wired but no nav button) + `bettingApi` (20+ methods at api.ts:1229-1276) + `sportsHubApi` (single-method at api.ts:1279-1282) + `humanApi` (shared Cat F cross-cutting surface at api.ts:1607-1665) + ~26 REST endpoints consumed across Categories A/B/C/D + zero WebSocket subscriptions despite `sports/routing.py:7-11` registering 3 sports consumers. Fifth sibling to apply the pre-brief 4-item mini-schema per D62 = (a) propagate upfront (Chris-ratified S1501 open 2026-07-01) so P6/F (S1506) inherits consistent evidence shape for the posture-decision brief owed to xx99 (S1599). Six parallel Explore sub-agents + parent-Claude verifier-loop for load-bearing claims per playbook §14 "trust but verify." Consumes S1504 §14.3 SportsBettingBrief write-only-and-forgotten + S1503 §14.7 AllowAny uniformity + S1502 §14.3 SignalCluster emission absence as load-bearing inherited claims.
- **Status.** `status: draft` at S1505 commit (Chris commit-gate pending). Rigby Full SIGN cycle 1 SIGN-with-edits at **High confidence** 2026-07-02 on fresh isolation pin `pa-546de7ebe8c8b885` → F1-F5 folds landed at commit-time → Cycle 2 SIGN-clean at High confidence anticipated post-fold-land (matches S1501 + S1502 + S1503 + S1504 cycle-1-predict-cycle-2 pattern). **D48 preemptive stability-probe gate 8th arm — CODIFICATION-READY for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505 8-arc pattern** (clean probe via `cockpit_tool.worker_health` + `infra_health_tool.dependency_matrix` returning 4 healthy workers + 7-of-7 healthy components; zero worker-instability across 4 substantive SIGN turns — **three consecutive fully-clean arms S1503+S1504+S1505**).
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: child-audit`, `category: child_audit`, `subdomain_category: E`.
- **Primary questions answered.**
  - **Does BettingPage subscribe to any WebSocket for realtime updates?** §14.5 verified NEGATIVE — grep of `frontend/src/pages/BettingPage.tsx` for `new WebSocket` / `useWebSocket` / `wss:` / `/ws/` returns zero matches. All 9 tabs use react-query polling (30s Live Odds; 60s Today's Games + Line Movement + Stats + Pipeline Status). "Live Odds" tab is misnamed — it's polling not WS push. Sports WS routes at `sports/routing.py:7-11` exist but are unwired to any frontend consumer.
  - **What does `/ws/dbao/` actually broadcast?** §14.1 CRITICAL verified NEGATIVE — `core/new_pages_consumer.py:310-331` `send_dbao_metrics` handler generates every metric field via `random.randint()` + `random.uniform()`. **NEW pattern class for the arc: MOCK-DATA-CONSUMER** — distinct from S1504 §14.3 WRITE-ONLY-AND-FORGOTTEN (real data written, never read) + S1503 §14.1 ZERO-FIRE-BEAT (real task, real schedule, never fires) + S1502 §14.4 PROVENANCE-STAMP-ABSENT (real writes but no owner tag). Here: no real data is touched at any point; the consumer synthesizes numbers server-side, timestamps them (`timezone.now().isoformat()`), and pushes as WS messages clients cannot distinguish from real data. F5 intent-neutrality fold: may be intentional demo/placeholder but operational-confusion / integration-signaling hazard stands. CRITICAL architectural.
  - **Are `markets` + `bankroll` tabs reachable via UI?** §14.2 verified NEGATIVE — `BettingTab` union at line 14 declares 11 tab identifiers; `tabs` array at lines 16-26 renders only 9 nav buttons. Verifier-loop confirmed at read of BettingPage.tsx:968 + :975 + :2080 + :2298 — `markets` + `bankroll` ARE wired at the render layer with conditional query hooks and conditional JSX blocks but no nav button to activate. **NEW pattern class: DEAD-RENDER-PATH** — fully coded feature branches with no user-facing entry point. Fifth distinguishing pattern shape after S1501–S1504.
  - **Is client-side auth enforced before REST calls?** §14.3 verified NEGATIVE at frontend + backend both — ProtectedRoute (App.tsx:47-59) redirects unauthenticated users to `/login` before BettingPage renders, BUT axios interceptor (api.ts:27-40) is what actually injects the `Authorization` header on each call, AND api.ts:48-56 only triggers logout on 401 for auth endpoints (other 401s log warning). Two endpoints require IsAuthenticated backend-side (`live_betting_opportunities` at views_odds_sports.py:580 + `get_betting_intelligence` at views_odds_sports.py:2056; urls.py:3085 + :3099) while all other Cat E-adjacent read paths are AllowAny (Session 559/688 pattern). Silent 401 on Top Plays / Sharp Action / Arbitrage tab families. F1 fold two-sided framing. F4 fold tab-consumer identification.
  - **Does the `/v1/betting/brief/` REST endpoint read persisted `SportsBettingBrief`?** §14.4 verified NEGATIVE — `get_betting_brief` at `views_odds_sports.py:3237-3265` calls `SportsBettingCoordinator.generate_brief()` on-the-fly and returns coordinator result verbatim; persisted `SportsBettingBrief` model is never queried. **S1504 §14.3 write-only-and-forgotten verdict UPHELD** — 2 writers + 0 readers at both persistence and consumption layers.
  - **Cat E maturity verdict?** §13: **PARTIAL (mixed — WORKING at read-side tabs; DEAD-RENDER-PATH at markets/bankroll; MOCK-DATA-CONSUMER at /ws/dbao/; AUTH-DRIFT at 2 endpoints; NO-REALTIME across all tabs)** — fifth distinguishing maturity shape after S1501 fragile-contract-at-ingestion + S1502 armed-but-under-instrumented + S1503 armed-but-zero-fire + S1504 mixed-brief-generation-persistence-forgotten-HOT-PATH-CHOKE.
- **Load-bearing deliverables.** §2.1 Cat E contract statement (fifth sibling in Group 1500 following S1501 + S1502 + S1503 + S1504 pattern) listing 5 guarantees + 11 non-guarantees; §4 Major Models thin because Cat E has no persistence layer (sibling-inheritance rule); §4.2 4-item mini-schema per surface per D62 fold + cross-sibling observation "humanApi cross-domain sharing is load-bearing on design-posture axis (d) — first sibling where 3 shared-with-mainline surfaces (humanApi + ProtectedRoute + /ws/dbao/ consumer) require cross-domain refactor if island posture chosen"; §6.1 REST endpoint inventory table (~26 endpoints frontend consumes across 47 total betting/sports/odds view functions, 20 AllowAny per Explore Agent 2); §6.2 WebSocket endpoint inventory (5 routes defined, 0 subscribed from BettingPage); §6.4 polling cadence table for all 9 visible tabs + 2 DEAD-RENDER-PATH; §7.1 F1-analog explicit call-chain block for Top Plays tab (extends S1503 §7.1 + S1504 §7.1 pattern); §9.3 positive isolation signal for Cat F ("BettingPage is SOLE frontend sports consumer"); §14 drift matrix (9 items — 1 CRITICAL + 4 HIGH + 2 MED-HIGH + 2 MED-LOW); §15 debt matrix (6 items with F2 elevation to structural debt class); §19 rank-ordered future-research queue (§19.1 CRITICAL tier 5 items: DBAO product-line footprint + DEAD-RENDER-PATH root-cause + AUTH-DRIFT resolution + Signal Engine emission bridge + Sports WS routes ownership); §20.5 5 verifier-loop corrections + §20.8 SIGN cycle 1 verdict block with F1-F5 folds enumerated.
- **Verifier-loop discipline.** Six parallel Explore sub-agents launched in single message per playbook §13 (Models/Persistence + Services/Runtime + APIs/Tools/Tasks/Commands + Integrations/Cross-Domain + Docs/Prior-Research + Drift/Debt/Ownership/Maturity). Parent-Claude verifier-loop applied per playbook §14 on 5 load-bearing claims pre-SIGN: (a) `/ws/dbao/` mock-data payload VERIFIED at `core/new_pages_consumer.py:310-331`; (b) BettingPage.tsx line count VERIFIED at 3,023 via `wc -l`; (c) `markets` + `bankroll` DEAD-RENDER-PATH conditionals VERIFIED at `BettingPage.tsx:968` + `:975` + `:2080` + `:2298`; (d) `get_betting_brief` model bypass VERIFIED at `views_odds_sports.py:3237-3265`; (e) AUTH-DRIFT permission decorators VERIFIED at `views_odds_sports.py:580` + `:2056` + `urls.py:3085` + `:3099`. Also 3 verifier-loop corrections applied to Explore agent conflicts (Agent 1 vs Agent 6 orphan-tab framing → resolved as DEAD-RENDER-PATH new pattern class; Agent 3 payload analysis → clarified MOCK-DATA-CONSUMER applies to DBAO handler not whole file; Agent 2 endpoint count → 47 backend total vs ~26 frontend-consumed). Rigby SIGN cycle 1 substantive on fresh isolation pin `pa-546de7ebe8c8b885` — D48 stability probe clean via `cockpit_tool.worker_health` + `infra_health_tool.dependency_matrix` returning 4 workers + 7 healthy components. Rigby Q8 grep-verified all 5 load-bearing file:line claims INDEPENDENTLY (BettingPage.tsx 3023 lines + tabs count 11 declared / 9 rendered + `live_betting_opportunities` decorator at line 580 + `get_betting_intelligence` decorator at line 2056 + urls.py mappings at 3085 + 3099 + `SportsBettingBrief.objects` 2-writer-0-reader). Confidence upgraded Medium → High at cycle 1 batch 3 after grep verification. **Do-not-regress notes for PR:** preserve §2.1 Cat E contract statement (11-item non-guarantee list) + preserve F1 §14.3 two-sided drift framing (frontend "no 401 surfacing" side + backend "permission-floor inconsistency" side) + preserve F2 §15.5 structural debt promotion (API contract source-of-truth as parent cause behind auth-drift + inline interfaces + tab-count doc drift + read-path fragility) + preserve F3 §14.3 verified-in-repo anchors subsection + preserve F4 §14.3 tab-consumer identification (Top Plays / Sharp Action / Arbitrage tab families) + preserve F5 §14.1 MOCK-DATA-CONSUMER intent-neutrality framing.
- **Inherited findings referenced.** S1504 §14.3 SportsBettingBrief write-only-and-forgotten — CONFIRMED at frontend AND REST endpoint via §14.4 (S1504 verdict upheld and strengthened; not only is no consumer reading, but the REST endpoint that would obviously be the reader deliberately bypasses persistence). S1504 §14.5 Signal Engine emission absence — REPLICATED at Cat E consumer side via §14.6 (extends 4-arc pattern to 5-arc pattern). S1503 §14.7 AllowAny uniformity — EXTENDED at Cat E via §14.3 F1 fold (permission floor is not uniform even inside a single dashboard; 2 IsAuthenticated endpoints stand out as un-migrated from Session 559/688 pattern). S1502 §14.3 SignalCluster emission absence — REPLICATED at Cat E via §14.6 F11 clarifier "no owning bridge implementation was located." S1502 §14.4 Memory Domain bridge absence — REPLICATED at Cat E via §14.8. S1501 §14.2 fixture-identity debt — no direct extension at Cat E scope (frontend consumes downstream). S1273 §3.10 LIGHT baseline → S1505 close moves Cat E coverage from LIGHT to MODERATE per §12 (formal Group 1500 arc structure; parent §3.E scoping + this dedicated child audit).
- **Dependencies.** Parent scoping `1500_sports_domain_scoping.md` (§3.E Cat E boundary + §5 mission sequence P5 + §6 P5-parked realtime channel question resolved in §14.5 + D62 mini-schema propagation directive); sibling audits `1501_sports_odds_ingestion_normalization_audit.md` (Cat A §2.1 contract) + `1502_sports_prediction_analytics_agents_audit.md` (Cat B §2.1 contract + §14.3 SignalCluster) + `1503_sports_wager_tracking_outcome_verification_audit.md` (Cat C §2.1 contract + §14.7 AllowAny + §5.4 additional read surfaces) + `1504_sports_betting_content_pipeline_audit.md` (Cat D §2.1 contract + §14.3 SportsBettingBrief + §14.5 Signal Engine); `DOMAIN_RESEARCH_PLAYBOOK.md` §9 canonical questions + §11.2 20-section template + §13 6-parallel-Explore sweep + §14 evidence rules + §15 SIGN policy; `RESEARCH_OPERATING_SYSTEM.md` §8 child-audit contract; `platform_architecture_inventory.md` §3.10; `docs/topics/frontend.md:77-95` (drift-source for §11); `docs/PLATFORM_INVENTORY.md:30 + :2039-2041` (runtime anchor for tab counts); memory rule `feedback_docs_cascade_at_every_close.md`.
- **Recommended next reads.** **S1506 Child F Cross-Domain Integration Lens & Posture Decision Framing Audit** next per parent §5 mission sequence P6 slot (LAST child before xx99). Load-bearing S1505 outputs to inherit at S1506: §14.1 MOCK-DATA-CONSUMER at `/ws/dbao/` — Cat F evidence plan owes DBAO product-line footprint audit (does DBAO carry any real state anywhere in the platform, or is it entirely a naming convention with no runtime data?); §14.6 zero Cat E → Signal Engine emission extends 4-arc pattern to 5-arc pattern — Cat F owes arc-close synthesis to xx99; §14.8 zero Memory Domain bridge extends 4-arc pattern to 5-arc pattern — Cat F owes POSTURE-DECISION framing; §14.3 AUTH-DRIFT two-sided framing — Cat F design-preparation candidate for canonical resolution; §14.5 sports WS routes ownership (staged for future use / legacy with no owner / delete candidate) — Cat F design-preparation candidate; §9.3 positive isolation signal for Cat F (BettingPage is SOLE Cat E surface with zero cross-domain leak) — Cat F island-posture evidence weight; §4.2 humanApi cross-domain sharing on design-posture axis (d) — Cat F island-posture cost estimate raised above prior siblings.
- **Overall importance.** **First library child audit to identify a MOCK-DATA-CONSUMER pattern class at the WebSocket layer** — introduces a NEW pattern class distinct from S1504 WRITE-ONLY-FORGOTTEN + S1503 ZERO-FIRE-BEAT + S1502 PROVENANCE-STAMP-ABSENT. Diagnostic criteria: (i) production WS namespace route registered, (ii) consumer file materialized, (iii) payload synthesized server-side via random.randint/uniform, (iv) payload timestamped and structured to mimic real-data handlers in the same consumer, (v) clients cannot distinguish from real data without reading source. Pattern candidate for playbook v3 §14 evidence-rules diagnostic checklist. **First library child audit to identify a DEAD-RENDER-PATH pattern class** — fully coded feature branches with no user-facing entry point (`markets` + `bankroll` tabs at BettingPage.tsx). Diagnostic criteria: (i) type union declares identifier, (ii) query hook wired conditionally, (iii) JSX block wired conditionally, (iv) no nav bar entry, (v) unreachable via any shipped code path. Pattern candidate for playbook v3 §14 evidence-rules diagnostic checklist. **First library child audit to elevate "no API contract source-of-truth" to first-class structural debt** — Rigby Q5 fold F2 named this as the parent cause behind §14.3 AUTH-DRIFT + §15.4 inline interfaces + §14.9 tab-count doc drift + general read-path fragility. Pattern candidate for playbook v3 §12.1 debt classification addition. **First library child audit to reach "PARTIAL (mixed)" verdict with FIVE distinct component states across the frontend** — WORKING at read-side tabs + DEAD-RENDER-PATH at markets/bankroll + MOCK-DATA-CONSUMER at /ws/dbao/ + AUTH-DRIFT at 2 endpoints + NO-REALTIME across all tabs. Fifth distinguishing maturity shape in the arc. **First library child audit to codify D48 stability-probe gate as 8th-arm CODIFICATION-READY signal with three-consecutive-fully-clean arms sub-pattern (S1503+S1504+S1505)** — further strengthens immediate playbook v3 §15 codification recommendation from S1504 7-arc threshold. **First library child audit where Rigby Q8 grep-verified ALL 5 load-bearing file:line claims independently pre-final-verdict** — confidence upgrade Medium → High at batch 3 after grep verification pass. Verification-driven confidence-upgrade pattern candidate for playbook v3 §15 addition.
- **Distinguishing property.** **First library child audit to identify a shared-with-mainline API surface as load-bearing on design-posture axis (d) island-isolation-cost** — humanApi is used by BettingPage + CommandCenterPage + BoardroomTab + DecisionDetailModal (Explore Agent 4 verified); this raises the island-posture cost estimate above prior siblings and is a load-bearing observation for Category F posture-decision brief. Cross-sibling observation: S1501+S1502+S1503+S1504 all identified isolation surfaces as sports-only in the vast majority of cases; Cat E has 3 shared-with-mainline surfaces (humanApi + ProtectedRoute + /ws/dbao/ consumer) that would require cross-domain refactor if the island posture is chosen. **First library child audit to catch a "misnamed realtime tab" drift** — "Live Odds" tab (BettingPage.tsx:23) uses 30-second polling (BettingPage.tsx:961), not WebSocket push; naming implies realtime but implementation is polling. **First library child audit to answer parent §3.E parked realtime channel question with explicit code-level evidence** — parent §3.E flagged "no dedicated betting WebSocket channel found" as known drift; S1505 verified NEGATIVE not just at BettingPage layer but confirmed the specific `/ws/dbao/` alternative would broadcast mock data even if subscribed. **First library child audit where zero cross-domain frontend consumption is a POSITIVE isolation signal for Cat F** — BettingPage.tsx is SOLE Cat E surface; grep of `frontend/src/**` for `bettingApi` / `sportsHubApi` imports outside BettingPage returns zero page-level consumers. This positive-shape finding contrasts with the mostly-negative drift-shape findings in siblings S1501-S1504. Index v31 → v32 updated per §10.1 (this §1.35 row + frontmatter v32 preamble + §8 timeline S1505 row).

---

### 1.34 `domains/sports/1504_sports_betting_content_pipeline_audit.md`

- **Title.** S1504 Sports Betting Content Pipeline — Child Audit (Category D / P4 under Group 1500)
- **Purpose.** Fourth child audit under Group 1500. Answers the 28 playbook §9 canonical questions for Category D — the sports betting **content generation and output surfaces** transforming ingested odds (Cat A) + analytics-agent outputs (Cat B) + wager-tracking stats (Cat C) into user-facing content across Discord + REST + persisted `SportsBettingBrief` model. Five surfaces per parent §3.D: `SportsContentContextBuilder` at `core/services/sports_content_context.py:27` (411 lines); `generate_daily_betting_brief` Celery task at `core/tasks_content.py:3103` + beat `generate-daily-betting-brief` at `core/celery.py:782-786` (crontab hour=7 minute=0, `CELERY_TIMEZONE = America/Denver`); `daily_betting_digest` at `core/tasks_financial.py:1907` (task defined but NO BEAT ENTRY — Finding 1 CRITICAL); Discord `/odds` at `core/services/discord_bot.py:1108`; `_impl_collect_sports_odds_intelligence` at `core/tasks_financial.py:1815` + beat at `core/celery.py:787-791` (crontab every 30 min). Plus REST endpoint `get_betting_brief` at `core/views_odds_sports.py:3237` (`AllowAny`) + `SportsBettingBrief` model at `core/models_unified_system.py:18394` (migration `0242_session_1003_desk_intelligence_briefs.py:52` — Session 1003 addition 2026-02-14). Fourth sibling to apply the pre-brief 4-item mini-schema per D62 = (a) propagate upfront (Chris-ratified S1501 open 2026-07-01) so P6/F (S1506) inherits consistent evidence shape for the posture-decision brief owed to xx99 (S1599). Six parallel Explore sub-agents + parent-Claude verifier-loop for load-bearing claims per playbook §14 "trust but verify" + Rigby ORM probe for CRITICAL beat-schedule zero-fire claim (second application of S1503-first-applied BEFORE-SIGN pattern). Consumes S1502 §1 Finding 1 call-chain block + S1502 §2.1 Cat B contract + S1503 §5.4 additional Cat C read surfaces list (all 3 read touchpoints in Cat D scope) as load-bearing inherited claims.
- **Status.** `status: active` on Chris commit-gate 2026-07-02. Rigby Full SIGN cycle 1 SIGN-with-edits at Medium-High confidence 2026-07-02 on fresh isolation pin `pa-af2bf7f2d1a0ef61` → F1-F11 folds landed at commit-time → Cycle 2 SIGN-clean at High confidence anticipated post-fold-land (matches S1501 + S1502 + S1503 cycle-1-predict-cycle-2 pattern). **D48 preemptive stability-probe gate 7th arm — CODIFICATION-READY for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502+S1503+S1504 7-arc pattern** (clean probe via `cockpit_tool.worker_health` + zero worker-instability across 4 substantive SIGN turns — matches S1503 6th-arm cleanest arm pattern).
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: child-audit`, `category: child_audit`, `subdomain_category: D`.
- **Primary questions answered.**
  - **Does `daily_betting_digest` actually fire on any schedule?** §1 Finding 1 + §14.1 CRITICAL verified NEGATIVE via 3-axis probe: grep of `core/celery.py` for `daily_betting_digest` → zero beat entries; grep of `docs/AUDIT_FINDINGS.md` §12 canonical deferred list → zero matches (task NOT documented as intentionally deferred); parent-Claude Rigby ORM probe on `pa-791b3db549a64e54` returned `CeleryTaskEvent.filter(30d, task_name='core.tasks.daily_betting_digest').count() = 0`. Docstring at `core/tasks_financial.py:1912` "Scheduled to run at 8 AM MST daily" describes phantom behavior. **S1503 §14.1 pattern replicated in Cat D scope** — second library child audit to catch the pattern class. CRITICAL operational risk — entire digest feature silently broken since Session 558 origin.
  - **Does `SportsBettingBrief` persistence have any consumer?** §1 Finding 2 + §14.3 verified NEGATIVE — grep of `SportsBettingBrief.objects.filter | get | all` returns zero reader sites (verifier-loop confirmed pre-SIGN). REST endpoint `get_betting_brief` at `core/views_odds_sports.py:3237` (`AllowAny`) calls `SportsBettingCoordinator.generate_brief()` DIRECTLY — never reads persisted model. Two writer sites: `core/tasks_content.py:3150` (Cat D daily brief) + `core/tasks.py:12187` (Session 1000 `run_all_desks_intelligence` multi-desk pipeline — Sports desk of 4-desk cascade). **NEW pattern for the arc: write-only-and-forgotten** — persistence artifact + REST bypass + two writers + zero readers. CRITICAL architectural.
  - **Does `generate_daily_betting_brief` docstring cadence match runtime?** §14.2 F6 fold verified NEGATIVE (demoted from HIGH → MED per Rigby batch 2 Q5): docstring at `core/tasks_content.py:3110` claims "Runs twice daily (morning + evening)" but beat crontab at `core/celery.py:783-786` is `crontab(hour=7, minute=0)` = once daily. Rigby ORM 5 SUCCESS fires in 30d all at 13:00 UTC = 07:00 MT. Docstring stale; primary daily brief still ships. F6 demote rationale: "less risky than 'doesn't run / duplicates / no tests / no consumers.'"
  - **Does Cat D write to Signal Engine (`SignalCluster`)?** §1 Finding 4 + §14.5 verified NEGATIVE — grep of Cat D scope for `SignalCluster.objects.create()`: zero matches. Extends S1274 §14 Finding #6 (`sports_odds` gap) to Cat D consumer side. **POSTURE-DECISION-PENDING per S1502 F2 / S1503 §14.3 precedent** + F11 fold Rigby batch 3 Q8: "no owning bridge implementation was located" (reads as "not built / not wired" not "intentionally delegated with evidence").
  - **Does Cat D write to Cat B agent memory / calibration?** §1 Finding 3 + §14.4 verified NEGATIVE — no `AgentMemory` writes, no `SportsBettingLearningBridge` for Cat D → Cat B feedback (`SportsBettingLearningBridge` exists for Cat C but not Cat D per parent-Claude grep + S1503 §5.2 inheritance). **POSTURE-DECISION-PENDING per S1502 F3 / S1503 F9 precedent** — bridge owns learning writes; brief-generation surface does not. F11 fold: no owning bridge implementation was located.
  - **Does `SportsContentContextBuilder` invocation chain reach content-generation surfaces?** §5.1 F2 fold Rigby batch 1 verified POSITIVE (elevated from TRANSITIVELY-COUPLED to HOT-PATH-CHOKE-POINT for content/PA subsystem) — called via `get_sports_content_context()` at `core/services/domain_content_context.py:189-190` by `DomainContentContextBuilder._get_sports_context()`, itself instantiated by 3 first-class downstream consumers: `content_review_panel_v2.py:198` + `content_review_panel.py:82-85` + `unified_pa_entrypoint.py:476-480`. **HOT-PATH-CHOKE-POINT** for content/PA; **BYPASSED** by Cat D Discord fast path (`_impl_daily_betting_digest`, `_impl_collect_sports_odds_intelligence`, `/odds`) — two disconnected content-generation surfaces (Finding 7).
  - **Cat D maturity verdict?** §13 F9 fold Rigby batch 3 Q8: **PARTIAL (mixed maturity — WORKING (beat + 30d fire evidence confirmed) at brief-generation; PRESENT + SCHEDULED (runtime not verified beyond Celery SUCCESS counts) at intelligence-hook + `/odds`; BROKEN/DORMANT at digest; WRITE-ONLY-FORGOTTEN at brief-persistence; HOT-PATH-CHOKE-POINT for content/PA at `SportsContentContextBuilder` — but bypassed by Cat D Discord fast path)** — fourth distinguishing maturity shape in the arc. F9 fold rationale: Celery SUCCESS counts prove task fired but do NOT prove semantic correctness of Discord posts / user interactions; runtime confirmation is a follow-on operational instrumentation task (§19.2 #8).
- **Load-bearing deliverables.** §2.1 Cat D contract statement (fourth sibling in Group 1500 following S1501 §2.1 + S1502 §2.1 + S1503 §2.1 pattern) listing 5 guarantees + 10 non-guarantees; §4 Major Models with §4.1 SportsBettingBrief detailed writer inventory + §4.2 LegacySpiderData F3-fold-elevated shared-table Cat B/C bridge surface risk + §4.4 4-item mini-schema per model per D62 fold; §5 Major Services with §5.1 F2-fold-reframed HOT-PATH-CHOKE-POINT observation + §5.2 SportsBettingCoordinator boundary note + §5.3 DiscordNotificationService.send_betting_digest() shared-service method + §5.4 additional Cat C read-surfaces (S1503 §5.4 F1 inheritance) + §5.5 god-service check + §5.6 4-item mini-schema per service; §6.6 4-item mini-schema per external surface; §7 runtime flows with §7.1 F1-analog explicit call-chain block for `generate_daily_betting_brief` (extends S1502 §7.1 pattern) + §7.2 F1-fold-elevated `run_all_desks_intelligence` cross-domain writer bridge + §7.6 SportsContentContextBuilder blog/content slow path invocation flow; §8 data ownership with §8.4 grep-verified absences (SignalCluster / AgentMemory / UserAgentLearning / Deliverable / ClaimsPack / PublishGate / SelfBlog — 7 architecturally load-bearing "sports as island" data points) + §8.6 4-item mini-schema per data owned; §9 integration table with inbound Cat A/B/C + outbound Discord + zero-emission columns for Signal Engine / Memory Domain / Content Pipeline; §14 drift matrix (8 items — 2 CRITICAL + 2 HIGH POSTURE-DECISION-PENDING + 1 MED F6-fold-demoted + 1 MED F11-fold-clarified + 2 MED-LOW); §15 debt matrix (16 items with F4+F5 CRITICAL promotes + F6 MED demote + §15.16 D62 mini-schema); §19 rank-ordered future-research queue F8-fold-reordered (§19.1 CRITICAL tier 5 items: digest beat + idempotency + test coverage + consumer-or-remove + dedup); §20.4 4 verifier-loop corrections applied pre-SIGN + §20.5 Rigby ORM probe log with 3-task 30d fire evidence + §20.8 SIGN cycle 1 verdict block with F1-F11 folds enumerated.
- **Verifier-loop discipline.** Six parallel Explore sub-agents launched in single message per playbook §13 (Models/Persistence + Services/Runtime + APIs/Tools/Tasks/Commands + Integrations/Cross-Domain + Docs/Prior-Research + Drift/Debt/Ownership/Maturity). Parent-Claude verifier-loop applied per playbook §14 on 5 load-bearing claims pre-SIGN: (a) `SportsBettingBrief` model definition VERIFIED at `core/models_unified_system.py:18394` (Sub-agent 3 was wrong "no model definition"); (b) `SportsBettingBrief` writer sites VERIFIED = 2 (Sub-agent 1 was wrong "Cat D-exclusive"); (c) `SportsBettingBrief` reader sites VERIFIED = 0 (Finding 2 write-only-and-forgotten pattern CONFIRMED); (d) `SportsContentContextBuilder` invocation chain VERIFIED (Sub-agent 6 marked UNKNOWN; parent-Claude resolved via grep to 3 consumer surfaces); (e) `get_betting_brief` REST behavior VERIFIED (Sub-agents 3 + 4 disagreed; parent-Claude Read confirmed coordinator direct-call, model bypass). Additionally CRITICAL load-bearing claim verified via parent-Claude Rigby ORM probe BEFORE draft integration (`ops_tool.celery_task_history 30d` on 3 Cat D task variants via arc pin `pa-791b3db549a64e54`) — **second library application** of S1503-first-applied BEFORE-SIGN pattern. Rigby SIGN cycle 1 substantive on fresh isolation pin `pa-af2bf7f2d1a0ef61` (D48 stability-probe clean via warm-up ping + `cockpit_tool.worker_health` confirming 4 workers online) — F1-F11 folds landed. **First library child audit where Rigby SIGN cycle 1 batch 1 substantive response required re-request** for verdict text (initial response was tool-heavy without verdict summary); subsequent batches delivered normally — recovery via one-line "please give me the Q1/Q2/Q3 verdict text" ping. Recovery pattern candidate for playbook v3 §15 alongside D45 titles-only recovery. Cycle 2 SIGN-clean at High confidence anticipated post-fold-land. **Do-not-regress notes for PR:** preserve §2.1 Cat D contract statement + preserve F1 `run_all_desks_intelligence` cross-domain writer bridge framing (do NOT backslide to "same target table" flat language) + preserve F2 HOT-PATH-CHOKE-POINT reframe at §5.1 + §7.6 + §13.2 (do NOT backslide to TRANSITIVELY-COUPLED) + preserve F3 LegacySpiderData shared-table Cat B/C bridge surface risk at §4.2 + preserve F4 zero test coverage CRITICAL tier position at §19.1 #3 above SportsBettingBrief consumer-or-remove + preserve F5 digest idempotency as PRE-RESTORE-BEAT GATE ordering at §19.1 #2 (cannot land #1 without #2 first) + preserve F6 docstring cadence MED demotion at all 4 sites + preserve F8 §19.1 5-item CRITICAL tier dependency ordering + preserve F9 WORKING vs PRESENT-SCHEDULED distinction at §13 + §1 maturity verdict + preserve F11 "no owning bridge implementation was located" clarifier at §14.4 + §14.5 + §19.2 #6 + §19.4 #14-15 + preserve F10 concrete handoff-target language at §1 exec summary opening.
- **Inherited findings referenced.** S1503 §5.4 F1 fold "additional Cat C read surfaces" — all 3 flagged read touchpoints (`views_odds_sports.py` + `td_handlers_content.py` + `sports_content_context.py`) deep-audited at Cat D §5.4; the primary Cat D service `sports_content_context.py` is Finding 7 evidence; `td_handlers_content.py` is content-PA dispatch adjacent but not Cat D-owning per grep. S1503 §14.1 CRITICAL beat-schedule zero-fire pattern — REPLICATED at Cat D `daily_betting_digest` (Finding 1 / §14.1) via analogous 3-axis probe. S1503 F9 fold "bridge owns learning writes" default posture statement — INHERITED as Cat D §14.4 default posture for Cat D → Cat B outcome-feedback loop (F11 fold clarifier: no owning bridge located). S1503 §7.1 F1-fold explicit call-chain block pattern — REPLICATED at Cat D §7.1 for `generate_daily_betting_brief` call-chain (beat → task_shim → impl → coordinator → 5 agents → SportsBettingBrief + LegacySpiderData + MLPrediction safety-net). S1503 §15.14 F7 fold idempotency-as-PRE-RESTORE-BEAT-GATE — REPLICATED at Cat D §15.5 (F5 fold promoted to CRITICAL per Rigby batch 2 Q5 "spam/dup posts" rationale). S1502 §1 Finding 6 outcome-feedback loop MISSING — INHERITED as F11-clarified POSTURE-DECISION-PENDING per Rigby batch 2 Q4 "not built / not wired" rationale. S1502 §7.1 explicit call-chain block — EXTENDED at Cat D §7.1 through persistence + safety-net layers. S1501 §14 Discord `#market-intelligence` vs `CHANNEL_BOARDROOM` docstring drift — INHERITED as §14.6 MED / §15.13 debt item. S1274 §14 Finding #6 `sports_odds` not a `SignalCluster.pattern_type` — CONFIRMED at Cat D consumer side (§14.5) + F11 clarifier "no owning bridge implementation was located." S1273 §3.10 LIGHT baseline → S1504 close moves Cat D coverage from LIGHT to MODERATE per §12. Session 1005 SportsBettingBrief.objects.create() fix note at `core/tasks.py:12184` "Persist to DB so briefs survive cache TTL" — VERIFIED intentional Session 1003 design intent; Finding 2 CRITICAL classification stands (consumer never materialized).
- **Dependencies.** Parent scoping `1500_sports_domain_scoping.md` (§3.D Cat D boundary + §5 mission sequence P4 + §6.4 P4-parked MT-tz assumption + §6.5 P4/P5-parked topic-doc gap owed to xx99 + D62 mini-schema propagation directive); sibling audits `1501_sports_odds_ingestion_normalization_audit.md` (Cat A §2.1 contract statement + §14 docstring channel-name drift as inherited debt) + `1502_sports_prediction_analytics_agents_audit.md` (Cat B §2.1 contract + §7.1 call-chain block precedent + §1 Finding 3 method-signature asymmetry as inherited risk to Cat D brief output) + `1503_sports_wager_tracking_outcome_verification_audit.md` (Cat C §5.4 F1 additional read surfaces + §14.1 CRITICAL zero-fire pattern + §14.2 F9 bridge-owns-learning-writes precedent + §15.14 F7 idempotency-PRE-RESTORE-BEAT gate); `DOMAIN_RESEARCH_PLAYBOOK.md` §9 canonical questions + §11.2 20-section template + §13 6-parallel-Explore sweep + §14 evidence rules + §15 SIGN policy; `RESEARCH_OPERATING_SYSTEM.md` §8 child-audit contract; `platform_architecture_inventory.md` §3.10; `platform/cross_domain_integration_audit.md` §14 Finding #6 + §12.3; `docs/AUDIT_FINDINGS.md` §12 (grep-verified NOT to contain 3 Cat D task names); memory rule `feedback_docs_cascade_at_every_close.md` (post-merge 4-step cascade discipline).
- **Recommended next reads.** **S1505 Child E Frontend Sports Surface Audit** next per parent §5 mission sequence P5 slot. Load-bearing S1504 outputs to inherit at S1505: §2.1 Cat D contract statement (10-item non-guarantee list — S1505 verifies whether frontend consumers rely on any Cat D non-guaranteed behaviors); §5.1 F2-fold HOT-PATH-CHOKE-POINT observation (`SportsContentContextBuilder` for content/PA + BYPASSED by Discord fast path — S1505 checks whether frontend has yet a third content-generation path or reuses one of these); §5.4 3 additional read surfaces list from S1503 inheritance (S1505 audits `views_odds_sports.py` from consumer angle for the 5 REST endpoints Cat D exposes); §14.3 REST `AllowAny` uniform-pattern (S1505 verifies whether frontend enforces client-side auth or relies on server AllowAny — matches S1503 §14.7 pattern); §14.5 Signal Engine emission absence — S1505 checks whether BettingPage frontend reads `SignalCluster` or is coupled to Discord/DB directly; §19.2 #7 operational cadence study `run_all_desks_intelligence` beat state — deferred to S1505 or S1506 investigation.
- **Overall importance.** **Second library child audit to apply Rigby ORM probe as parent-Claude verifier-loop tool BEFORE SIGN routing** — replicates S1503-first-applied pattern at second-arc evidence base; extends S1401-S1406 verifier tool chain into S1500 arc as fully adopted. Pattern candidate for playbook v3 §14 evidence-rules addition. **First library child audit to catch a CRITICAL write-only-and-forgotten persistence pattern** — `SportsBettingBrief` model has 2 writers (Cat D daily beat + Session 1000 multi-desk) since Session 1003 (2026-02-14) but zero readers; REST endpoint bypasses persisted model. Extends S1503 §14.1 zero-fire pattern to a distinct architectural class: write path present + persistence artifact present + zero readers + REST bypass. **First library child audit to identify a HOT-PATH-CHOKE-POINT service that is BYPASSED by a sibling fast path in the same domain** — `SportsContentContextBuilder` for content/PA vs BYPASSED for Cat D Discord fast path; two disconnected content-generation surfaces (F2 fold reframe from TRANSITIVELY-COUPLED). **First library child audit to reach a "mixed maturity — WORKING at some + PRESENT + SCHEDULED at others + BROKEN at digest + WRITE-ONLY-FORGOTTEN at persistence + HOT-PATH-CHOKE-POINT-BYPASSED at context-builder" hybrid verdict** — fourth distinguishing maturity shape after S1501 + S1502 + S1503 three-shape taxonomy. **First library child audit to catch a docstring cadence lie that survives 30d Rigby ORM SUCCESS-fire evidence** — F9 fold pressure-test: Celery SUCCESS counts are NOT semantic-correctness evidence. **First library child audit to codify D48 stability-probe gate as 7th-arm CODIFICATION-READY signal** (S1405+S1406+S1499+S1501+S1502+S1503+S1504 7-arc pattern further strengthens the immediate playbook v3 §15 codification recommendation). **First library child audit where Rigby SIGN cycle 1 batch 1 required re-request** for verdict text (tool-heavy response with tool_runs section dominating pa_chat.py output); recovery pattern candidate for playbook v3 §15 alongside D45 titles-only recovery.
- **Distinguishing property.** **First library child audit to identify a shared-persistence table with two-writer contested ownership across research arcs** — `SportsBettingBrief` is written by Cat D shim (`_impl_generate_daily_betting_brief`) AND Session 1000 multi-desk pipeline (`run_all_desks_intelligence` — outside Cat D scope); Cat D owns daily brief lane, Session 1000 pipeline owns multi-desk brief lane, same target table. F1 fold elevates the framing from "same target table" to "cross-domain writer bridge." Pattern candidate for future audits: distinguish between writer-domain ownership and target-table ownership. **First library child audit to introduce the "PRESENT + SCHEDULED (runtime not verified beyond Celery SUCCESS counts)" maturity qualifier** — F9 fold explicitly separates task-fired evidence from Discord-post semantic correctness evidence; requires separate telemetry to promote to full WORKING. **First library child audit to flag the "write-only-and-forgotten" pattern class** with 4 diagnostic criteria: (i) persistence artifact present; (ii) writer path(s) present; (iii) zero reader sites via grep; (iv) canonical downstream surface (REST/API) bypasses persisted artifact and re-generates on request. Pattern candidate for playbook v3 §14 evidence-rules diagnostic checklist. **First library child audit to catch a "no owning bridge implementation was located" clarifier as SIGN-with-edits requirement** — F11 fold Rigby batch 3 Q8: POSTURE-DECISION-PENDING framing requires explicit "bridge not built" statement to distinguish from "intentionally delegated with evidence." Applied at §14.4 + §14.5 + §19.2 #6 + §19.4 #14 + §19.4 #15. Index v30 → v31 updated per §10.1 (this §1.34 row + frontmatter v31 preamble + §8 timeline S1504 row).

---

### 1.33 `domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md`

- **Title.** S1503 Sports Wager Tracking & Outcome Verification — Child Audit (Category C / P3 under Group 1500)
- **Purpose.** Third child audit under Group 1500. Answers the 28 playbook §9 canonical questions for Category C — the user-facing wager tracking + outcome verification surface (`PlacedWager` + `PlacedWagerLeg` + `BettingStats` in `core/models_betting.py`; `BettingOutcomeVerifier` service at `core/services/betting_outcome_verifier.py:21`; Celery tasks `verify_betting_outcomes` at `core/tasks.py:6122` + sibling `sports.verify_betting_outcomes` at `sports/tasks.py:414`; Discord `/bankroll` at `core/services/discord_bot.py:1404`; 11 REST endpoints at `core/urls.py:3090-3123`; PA tool `intelligence_tool` actions `sports_wagers` + `sports_record_wager`; learning bridge `SportsBettingLearningBridge` at `core/learning_bridges/sports_betting_bridge.py`). Third sibling to apply the pre-brief 4-item mini-schema per D62 = (a) propagate upfront (Chris-ratified S1501 open 2026-07-01) so P6/F (S1506) inherits consistent evidence shape for the posture-decision brief owed to xx99 (S1599). Six parallel Explore sub-agents + parent-Claude verifier-loop for load-bearing claims per playbook §14 "trust but verify" + Rigby ORM probe for CRITICAL beat-schedule zero-fire claim (extends S1401-S1406 verifier tool chain — first library child audit to apply Rigby ORM probe as parent-Claude verifier tool BEFORE SIGN routing). Consumes S1502 §1 Finding 6 (outcome-feedback loop MISSING) as load-bearing inherited claim.
- **Status.** `status: active` on Chris commit-gate 2026-07-02. Rigby Full SIGN cycle 1 SIGN-with-edits at High confidence 2026-07-02 on fresh isolation pin `pa-8ce5f949bed5e093` → F1-F14 folds landed at commit-time → Cycle 2 SIGN-clean at High confidence anticipated post-fold-land (matches S1501 + S1502 cycle-1-predict-cycle-2 pattern). **D48 preemptive stability-probe gate 6th arm — CODIFICATION-READY for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502+S1503 6-arc pattern** (clean probe via `cockpit_tool.worker_health` + zero worker-instability across 4 substantive SIGN batches this session).
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: child-audit`, `category: child_audit`, `subdomain_category: C`.
- **Primary questions answered.**
  - **Is `verify_betting_outcomes` actually scheduled and firing?** §1 Finding 1 + §14.1 CRITICAL verified NEGATIVE via 3-axis probe: grep of `core/celery.py` for `verify_betting_outcomes` → zero matches; grep of `docs/AUDIT_FINDINGS.md` §12 canonical deferred-by-policy list → zero matches (task is NOT documented as intentionally deferred); parent-Claude Rigby ORM probe on `pa-791b3db549a64e54` + independent Rigby SIGN cycle 1 batch 3 Q8 probe on `pa-8ce5f949bed5e093` BOTH returned `PeriodicTask.objects.count() = 0` AND `CeleryTaskEvent 30d count = 0` for both task variants. Two independent probes on two different pins. Docstring at `core/tasks.py:6129` "Runs every 2 hours via Celery Beat" describes phantom behavior. CRITICAL operational risk — entire feature silently broken.
  - **Does Cat C write outcomes back to Cat B `MLPrediction.was_correct`?** §1 Finding 2 + §14.2 verified NEGATIVE — grep of `betting_outcome_verifier.py` for `MLPrediction` / `was_correct`: zero matches (verifier-loop confirmed). `SportsBettingLearningBridge.record_wager_outcome()` reads `MLPrediction.was_correct` at `sports_betting_bridge.py:394` but does NOT write it; `MLPrediction.was_correct` is set by separate task `evaluate_ml_predictions` at `core/tasks.py:6192`. Answers S1502 §1 Finding 6 explicitly. **F9 fold — POSTURE-DECISION-PENDING default posture:** "bridge owns learning writes" (both §14.2 + §14.3 apply the same framing) per S1502 F3 precedent.
  - **Does Cat C emit `SignalCluster` rows from settlement / streaks / arb verification?** §1 Finding 3 + §14.3 verified NEGATIVE — grep of `betting_outcome_verifier.py` for `SignalCluster` / `SignalService`: zero matches. Extends S1274 §14 Finding #6 into Cat C consumer side. **POSTURE-DECISION-PENDING** per S1502 F2 precedent.
  - **Are there duplicate task definitions for the same feature?** §1 Finding 4 + §14.4 verified POSITIVE — `core.tasks.verify_betting_outcomes` at `core/tasks.py:6121` (with retry policy + BettingStats-recalc wrapper) AND `sports.verify_betting_outcomes` at `sports/tasks.py:414` (simpler variant, no retry, no BettingStats wrapper) both call the same `BettingOutcomeVerifier` service. Different names via `@shared_task(name=...)` — Celery treats as distinct. `docs/CELERY_AUDIT.md:469-470` confirms both registered, neither scheduled. MED-HIGH operational + MED architectural risk.
  - **Does Discord `/bankroll` read `BettingStats`?** §1 Finding 5 + §14.5 verified NEGATIVE — `discord_bot.py:1404-1527` reads `core.models_bankroll.Bankroll` and its `.wagers` FK relation, NOT `PlacedWager` or `BettingStats`. Dual aggregation surface. Two Bankroll-related classes exist per Rigby SIGN cycle 1 batch 3 grep: `Bankroll` at `core/models_bankroll.py:19` + `BankrollManagement` at `sports/models.py:1032` — F14 fold clarifies "bankroll is NOT core-only". MED severity (downgraded from MED-HIGH per Rigby SIGN cycle 1 batch 2 Q5 fold F5 — until empirical divergence proven).
  - **Cat C maturity verdict?** §13: **PARTIAL (armed but zero-fire)** — extends S1501 "WORKING (fragile contract) at ingestion, PARTIAL at normalization" + S1502 "PARTIAL (armed but under-instrumented)" three-tier maturity taxonomy adding "**armed but zero-fire**" as third distinguishing shape. Model layer + service layer + REST + PA + Discord surfaces all complete; CRITICAL scheduling drift + zero test coverage + missing concurrency-safety + posture-decision-pending integration hold at PARTIAL.
- **Load-bearing deliverables.** §2.1 Cat C contract statement (third sibling in Group 1500 following S1501 §2.1 + S1502 §2.1 pattern) listing what Cat C guarantees today vs what it explicitly does NOT guarantee — establishes contract Cat F evidence plan consumes; §4 Major Models with 4-item mini-schema (§4.4) per model per D62 fold + §5.4 additional Cat C read surfaces subsection landed post-cycle-1 Q1 fold + §5.5 Bankroll adjacency touchpoints (bounded) subsection + §5.6 4-item mini-schema per service; §7 runtime flows with §7.1 F1-analog explicit call-chain block (Rigby SIGN cycle 1 batch 1 Q1 must-change-before-canonical directive; extends S1502 F1 pattern to Cat C); §8 data ownership with §8.6 4-item mini-schema per data owned + §8.4 grep-verified absences (MLPrediction / SignalCluster / Initiative / Deliverable / MemoryLane / AgentKnowledgeSource — 6 architecturally load-bearing "sports as island" data points); §9 integration table (WORKING Cat A read; MISSING Cat B feedback per §1 Finding 2 POSTURE-DECISION-PENDING; PARTIAL Memory Domain via bridge; leaf-domain zero inbound FKs per §1 Finding 8); §14 drift matrix (8 items — 1 CRITICAL + 2 HIGH + 3 MED-HIGH + 1 MED + 1 LOW); §15 debt matrix (15 items including F6-F8 fold new items: timezone / idempotency+replay-safety / Decimal rounding); §17 duplicate systems flags (Bankroll vs BettingStats dual aggregation + two task variants); §19 ranked future-research queue (F10 fold reorganized §19.1 CRITICAL tier: beat-schedule remediation + concurrency-safety as PRE-RESTORE-BEAT GATE + Cat F evidence plan items); §20.4 F1-F14 SIGN fold notes + §20.5 two independent Rigby ORM probes both returning zero + §20.8 Rigby SIGN cycle 1 verdict block.
- **Verifier-loop discipline.** Six parallel Explore sub-agents launched in single message per playbook §13 (Models/Persistence + Services/Runtime + APIs/Tools/Tasks/Commands + Integrations/Cross-Domain + Docs/Prior-Research + Drift/Debt/Ownership/Maturity). Parent-Claude verifier-loop applied per playbook §14 on 7 load-bearing claims — 2 sub-agent errors caught pre-SIGN (Sub-agent 6 line count 340→480 corrected + Sub-agent 6 line reference 28→26 corrected); 5 sub-agent claims survived independent verification. Additionally CRITICAL load-bearing claim verified via **parent-Claude Rigby ORM probe BEFORE draft integration** (`scheduled_tasks_tool` + `ops_tool.celery_task_history` on `pa-791b3db549a64e54`) — first library child audit to apply Rigby ORM probe as parent-Claude verifier tool before SIGN routing (extends S1401-S1406 verifier tool chain: file-line direct-reads + broader-grep + model-context disambiguation + provenance-stamp ORM probe now + BEFORE-SIGN Rigby ORM probe). Rigby SIGN cycle 1 substantive on fresh isolation pin `pa-8ce5f949bed5e093` batches 1-3 (D48 stability-probe clean via warm-up ping + `cockpit_tool.worker_health` confirming 4 workers online, 0 active tasks) — F1-F14 folds landed. Rigby SIGN cycle 1 batch 3 Q8 **second independent ORM probe** verified — matches parent-Claude pre-SIGN probe → CRITICAL §14.1 finding evidence-doubled. Cycle 2 SIGN-clean at High confidence anticipated post-fold-land. **Do-not-regress notes for PR:** preserve §2.1 Cat C contract statement + preserve F9 "bridge owns learning writes" framing throughout §14.2 + §14.3 (do NOT backslide to "MISSING integration" defect language) + preserve F4 independent Rigby ORM probe block in §14.1 + §20.5 + preserve F7 idempotency-as-pre-restore-beat-gate framing in §15.14 + §19.1 (do NOT let CRITICAL #1 land without CRITICAL #2 landing first) + preserve F10 §19.1 CRITICAL tier ordering.
- **Inherited findings referenced.** S1502 §1 Finding 6 outcome-feedback loop MISSING — CONFIRMED at Cat C code level as F2 fold POSTURE-DECISION-PENDING. S1502 §1 Finding 2 PA tool registry gap pattern — REPLICATED at Cat C (§3.4 registry gap: no verifier / recalc / bankroll surgical operations exposed). S1502 §1 Finding 3 direct-consume dict-shape coupling pattern — REPLICATED at Cat C via `PlacedWagerLeg.event_id` string coupling to Odds API dict return shape (§1 Finding 7). S1274 §14 Finding #6 `sports_odds` not a `SignalCluster.pattern_type` — CONFIRMED at Cat C consumer side (§14.3). S1501 §2.1 Cat A contract statement — verified as Cat C's load-bearing input for score provenance shape; Cat C §2.1 documents which non-guarantees Cat C fills vs extends. S1501 §14.2 fixture-identity debt — inherited as §15.12 debt item. S1273 §3.10 LIGHT baseline → S1503 close moves Cat C coverage from LIGHT to MODERATE per §12.
- **Dependencies.** Parent scoping `1500_sports_domain_scoping.md` (§3.C Cat C boundary + §5 mission sequence + §6 P3-parked outcome-feedback question resolved in this audit + §D62 mini-schema propagation directive); sibling audits `1501_sports_odds_ingestion_normalization_audit.md` + `1502_sports_prediction_analytics_agents_audit.md` (both §2.1 contract statements as load-bearing inputs); `DOMAIN_RESEARCH_PLAYBOOK.md` §9 canonical questions + §11.2 20-section template + §13 6-parallel-Explore sweep + §14 evidence rules + §15 SIGN policy; `RESEARCH_OPERATING_SYSTEM.md` §8 child-audit contract; `platform_architecture_inventory.md` §3.10; `platform/cross_domain_integration_audit.md` §14 Finding #6 + §12.3; `docs/CELERY_AUDIT.md:469-470` (canonical Celery inventory confirmation of no beat schedule); `docs/AUDIT_FINDINGS.md` §12 (grep-verified NOT to contain task name).
- **Recommended next reads.** **S1504 Child D Betting Content Pipeline Audit** next per parent §5 mission sequence P4 slot. Load-bearing S1503 outputs to inherit at S1504: §5.4 additional Cat C read surfaces flagged 3 read touchpoints in Cat D scope (`views_odds_sports.py` + `td_handlers_content.py` read path + `sports_content_context.py`); §14.5 Discord `/bankroll` uses Bankroll model — Cat D `/odds` command adjacency worth surveying; §14.1 CRITICAL beat-schedule zero-fire pattern — Cat D `generate_daily_betting_brief` beat state should be verified via analogous 3-axis probe; §1 Finding 1 pattern (docstring cadence vs runtime reality) is a candidate for cross-category discovery.
- **Overall importance.** **First library child audit to apply Rigby ORM probe as parent-Claude verifier-loop tool BEFORE SIGN routing** — extends S1401-S1406 verifier tool chain (file-line direct-reads + broader-grep + model-context disambiguation + provenance-stamp ORM probe) with a BEFORE-SIGN ORM verification step; pattern candidate for playbook v3 §14 evidence-rules addition. **First library child audit to catch a Celery task at CRITICAL zero-fire status via ORM probe (0 PeriodicTask + 0 CeleryTaskEvent 30d + NOT on `AUDIT_FINDINGS.md` §12 deferred list)** — extends the memory rule `feedback_audit_findings_12_canonical_celery_deferred_list.md` (S1245+S1246) canonical-deferred-list pattern to a research-methodology finding class. **First library child audit to reach a "PARTIAL (armed but zero-fire)" maturity verdict** — captures the shape where code + models + service + REST + PA + Discord are complete but scheduling is broken; extends S1502 "PARTIAL (armed but under-instrumented)" to a distinct third maturity shape. **First library child audit to codify D48 stability-probe gate as 6th-arm CODIFICATION-READY signal** (S1405+S1406+S1499+S1501+S1502+S1503 6-arc pattern further strengthens the immediate playbook v3 §15 codification recommendation). **First library child audit to have TWO independent Rigby ORM probes on TWO different pins both returning zero for the same CRITICAL claim** — evidence-doubling technique candidate for playbook v3 §14 addition.
- **Distinguishing property.** **First library child audit to inherit two sibling contract statements as load-bearing INPUTS** — S1501 §2.1 Cat A contract + S1502 §2.1 Cat B contract both cited as Cat C's runtime dependencies; Cat C §2.1 documents which non-guarantees Cat C fills vs extends from both. Pattern candidate for playbook v3 §11.2 template addition for late-sibling arcs with multi-sibling inheritance structure. **First library child audit to flag a task-schedule-vs-docstring drift as CRITICAL operational risk** rather than MED-HIGH documentation drift — via combined evidence bundle (grep of `core/celery.py` returns zero + grep of `docs/AUDIT_FINDINGS.md` §12 returns zero + Rigby ORM probe returns 0/0 for both task variants). **First library child audit to introduce compounding-risk observation** (F3 fold — §1 executive summary explicitly notes Finding 1 + Finding 5 combo produces stale + inconsistent user-facing views with no "system is behind" signal). **First library child audit to add "pre-restore-beat gate" concept** — §15.14 idempotency + replay safety as HIGH-severity operational debt that MUST land BEFORE any beat-schedule remediation; §19.1 CRITICAL tier reorganization enforces the ordering. **First library child audit to reach 6-arc D48 pattern with entirely clean stability probe** — zero worker-instability across 4 substantive SIGN batches (warm-up ping + 3 SIGN batches). Index v29 → v30 updated per §10.1 (this §1.33 row + frontmatter v30 preamble + §8 timeline S1503 row).

---

## 2. Recommended Reading Paths

Engineers join with different goals. Each path lists docs in
order; bracketed numbers point back to §1.

### Path A — "I need to understand Employee OS"

1. `CLAUDE.md` (Quick Start + Working with Rigby section)
2. `docs/EMPLOYEE_OS_PRIMITIVES.md` (canonical primitives +
   anti-duplication matrix)
3. `docs/topics/employee-os.md` (subsystem narrative)
4. `docs/research/employee_os_communication_substrate_audit.md`
   [§1.1]
5. `docs/research/employee_os_collaboration_patterns.md`
   [§1.3]
6. Latest handoff: `docs/handoffs/SESSION_1267_*.md`

You will now know: the four current employees, the lifecycle
primitives that compose them, the comms surfaces they expose,
and the collaboration substrates available across the wider
platform.

### Path B — "I want to design new employees"

1. Path A above (in full).
2. `docs/EMPLOYEE_OS_PRIMITIVES.md` §5 ("Quick-Start for
   Adding a New Employee").
3. `docs/research/employee_os_collaboration_patterns.md` §8
   (reuse classification — esp. SAFE rows) and §9
   (anti-duplication mapping).
4. `core/employees/jobs.py:74-162` (frozen `AIEmployee` +
   `JobContract` dataclass shapes) — read code, not docs.
5. `core/employees/mission_runner.py:1-230` (module docstring
   + lifecycle).
6. `core/employees/comms_docs_manager.py:1-122` (canonical
   per-employee comms wrapper pattern).

**Hard rule before opening a PR for Employee #5:** read
`EMPLOYEE_OS_PRIMITIVES.md` §2 + §4 in full. The 23-row "do
NOT build" matrix and the 7 explicit warnings exist because
each one cost real time before.

### Path C — "I want to understand governance"

1. `docs/research/governance_authority_evolution.md` [§1.4]
   — the canonical anchor (4 planes; 35 gates; 12 incidents;
   all Q1-Q12 answered).
2. `docs/EMPLOYEE_OS_PRIMITIVES.md` row 17 (GovernanceState +
   KillSwitch).
3. `docs/research/employee_os_collaboration_patterns.md` §2
   rows 55-56 + §10 Q11 (collaboration audit's view of
   authority enforcement).
4. `core/models_governance.py:17-189` (GovernanceState +
   KillSwitch model definitions).
5. `core/employees/mission_runner.py:258-275` (authority
   warn-mode constants + S1264 design).
6. `docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`
   (authority contract observation design + Rigby SIGN edits).

**Big findings to internalize:** four governance planes don't
compose today (autonomy / authority / budget / human
governance). KillSwitch has full write path + TTL but **zero
dispatch consumers** — write surface works, enforcement
doesn't. `JobContract.authority` is observation-only;
enforcement blocked on Symbol Mapping prerequisite (P0 next
research per §5.2).

### Path D — "I want to build new communication"

1. `docs/research/employee_os_communication_substrate_audit.md`
   [§1.1] — esp. §8 reuse classifications and §7 known risks.
2. `docs/research/employee_os_communication_protocol_sketch.md`
   [§1.2] — concrete pattern to mirror.
3. `core/employees/comms.py:228-367`
   (`post_shift_report` — canonical bounded-comms helper).
4. `core/employees/comms_docs_manager.py:1-122` (thin
   wrapper pattern).
5. `core/models_messaging.py:21-141`
   (MessageThread / ThreadParticipant / DirectMessage shapes).

**Hard rule:** do NOT propose enabling
`messaging_tool.send_message` in any design. It is OFF by
design (per `EMPLOYEE_OS_PRIMITIVES.md` §4.7 and
substrate audit §8 DO-NOT-REUSE row). Free-form LLM outbound
is the wrong shape for structured comms; bounded helpers in
`core/employees/comms*.py` are the right shape.

### Path E — "I need to understand orchestration"

1. `docs/research/employee_os_collaboration_patterns.md` §3
   (12 collaboration flow diagrams) + §4 (delegation
   mechanism comparison table).
2. `docs/topics/celery-workers.md` (worker / queue topology).
3. `core/employees/mission_runner.py:1-1758` (one orchestrator).
4. `ai_core/agents/hybrid_executor.py:244,351` (the other
   orchestrator — Celery chain + group).
5. `core/agents/workflow_orchestration_agent.py:47,302`
   (ThreadPoolExecutor fan-out variant).

**Big finding to internalize:** there are **two orthogonal
durable orchestration paths** (Celery chain in
`hybrid_executor.py` vs. MissionRunner step loop in
`mission_runner.py`). They do NOT compose today. Choose one
based on durability needs; do not mix.

### Path F — "I want to understand autonomous execution"

1. `docs/topics/spider-network.md` + `docs/topics/initiative-pipeline.md`.
2. `docs/research/employee_os_collaboration_patterns.md` §3.6
   (Spider → Signal → Trigger → Work flow) and §3.7 (Spider →
   EventBus → Consumer Group flow).
3. `core/services/signal_aggregation_service.py:33-1161`
   (entity-token clustering; pattern detection).
4. `core/services/event_bus.py:21-728` (8 streams + DLQ).
5. `core/services/body_coordinator.py:110-300+` (9 body
   systems autonomic reflex layer).

**Gap to know:** autonomous→initiative auto-creation
(AutoTopic → Initiative) is UNCERTAIN per collaboration audit
§10 Q2 — no creation task traced. Treat as not-yet-wired.

### Path G — "I need to understand platform reliability"

1. `docs/research/employee_os_collaboration_patterns.md` §5
   (mission coordination — what survives process / Redis / DB
   restarts) and §7 (29 failure modes).
2. `docs/research/employee_os_communication_substrate_audit.md`
   §7 (12 incident classes).
3. `docs/AUDIT_FINDINGS.md` (canonical Celery deferred list,
   S1115 multi-batch audit).
4. `docs/topics/celery-workers.md` (queue + worker
   architecture).
5. `core/services/anthropic_client_factory.py:38-50` +
   `core/services/openai_client_factory.py:68-72`
   (centralized timeout contract — must use these factories).

**Hard rule:** any new LLM client call site MUST go through
the factory (per memory rules
`feedback_anthropic_client_factory` and
`feedback_openai_client_factory`). Bare `Anthropic()` /
`OpenAI()` defaults to 600s timeout, causing the zombie-thread
class documented in collaboration audit §7 row 17.

### Path H — "I need to understand the whole platform"

*Added S1273 v5.* This is the whole-platform onboarding path.
Use it when your work spans multiple domains or you're new to
the codebase.

1. `CLAUDE.md` (Quick Start + Working with Rigby + system stats).
2. `docs/PLATFORM_WHAT_IT_IS.md` (narrative anchor — glossary +
   subsystem summaries).
3. `docs/PLATFORM_INVENTORY.md` (runtime anchor — authoritative
   counts; regenerable via `generate_platform_inventory`).
4. `docs/research/platform_architecture_inventory.md` [§1.9] —
   the 32-domain map + 9 cross-domain flows + maturity matrix +
   11-mission roadmap.
5. Whichever specific §3.n inventory in §1.9 matches your work.
6. If that subsystem has an Employee OS-arc research doc
   (§1.1-§1.8), read it next.

**Big finding to internalize:** the platform combines four
historically-separate stacks (AI Studio + DBAO + Employee OS +
Revenue Pipeline) under one substrate. §1.9's §1 executive
summary + §5 duplicate/overlapping systems section will show you
where those stacks compose cleanly and where they don't.

---

## 3. Architecture Domains

The platform is partitioned into ~17 domains below (the S1268-
S1272 arc's view). For a **whole-platform 32-domain map**
(broader scope, added S1273 v5), see `docs/research/platform_
architecture_inventory.md` [§1.9] §2. The two are complementary:
this table is Employee-OS-adjacent depth; §1.9's table is
whole-platform breadth.

For each row, the table lists what research exists (in this
library), what is still missing, and current maturity.

| Domain | Existing research | Canonical anchors | Missing research | Maturity |
|---|---|---|---|---|
| **Employee OS — core** | §1.1, §1.2, §1.3 | EMPLOYEE_OS_PRIMITIVES.md; topics/employee-os.md | (none today; covered by §1.1 + §1.3) | **High** — 4 production employees, fully audited |
| **Mission System (MissionRunner)** | §1.3 (§2 row 19, §3.9, §6) | mission_runner.py (1758 lines); jobs.py:74-162 | Dedicated MissionRunner architecture doc (could lift from §1.3's flow + reuse rows) | **High** — production for 4 employees |
| **Governance** | §1.4 (full audit; 4 planes documented) + §1.3 (§2 rows 55-56) | models_governance.py | (well-covered; downstream is Cross-plane Composition — see §5.4) | **Medium-High** — primitives fully audited; freeze/safe_mode wired; KillSwitch enforcement missing |
| **Authority** | §1.4 (full audit; 68 entries / 30 prohibited / 35 gates) + §1.3 (§2 row 26 + §10 Q11) + §1.6 (Symbol Mapping — 57 unique action strings; 5 mapping options; 20 enforcement boundaries) + §1.7 (Actor Attribution — WHO composes with WHAT) + §1.8 (Authority Enforcement Design Space — 24 inputs / 20 boundaries / 12 modes / 6 options A-F / 33 incidents / 15 anti-patterns / 15 prereqs) | mission_runner.py:258-275 (S1264 warn-mode); jobs.py:41-52 (AuthorityLevel); llm_enforcer.py:200-262 (fail-open precedent) | **Symbol Mapping Option Selection Design** (recommended P0 next per §1.8 §14.1 — pick from §1.6's 5 options + Chris gate) | **Medium-High** — all three prereqs shipped as research (S1270 + S1271 + S1272); no design decision yet; enforcement remains observation-only |
| **Actor Identity / Attribution** | §1.7 (full audit; 19 identity concepts; 22 attribution surfaces; 15 historical failures; 25 identity registries; F11 executor/sponsor/principal role vocabulary) | `AIEmployee` (jobs.py:73-92); `UnifiedUser` (models/base/models.py:86); `_resolve_runs_as_user_id` (mission_runner.py:1585-1591); `canonicalize_agent_name` (deliverable_aliases.py:39-47) | (§1.7 F1: OpsRun has no user FK — largest attribution gap; downstream design gated by Symbol Mapping Option Selection per §1.8 §14.1) | **Medium** — mixed strong-FK / ambiguous-CharField attribution; role vocabulary proposed but not schema-enforced |
| **Authority Enforcement (design space)** | §1.8 (full design-space discovery; 6 options A-F; 12 modes; 15 anti-patterns; 15-prereq DAG) | S1264 warn-mode; LLMEnforcer fail-open pattern; MissionRunner `_emit_authority_contract_event` | Symbol Mapping Option Selection Design + downstream Authority Enforcement Design Decision (Chris-gated per §1.8 §14.3) | **Design-space only** — no runtime enforcement designed yet; **maintenance note:** enforce-mode requires §14.1 P0 selection first; do not treat §1.8 options as implementable without downstream Chris-gated design decision |
| **Communication (employee comms)** | §1.1 (full); §1.2 (specific path) | comms.py, comms_docs_manager.py, EMPLOYEE_OS_PRIMITIVES.md §4.7 | Inter-employee reply lane (§1.3 F4); cross-fleet messaging | **Medium** — outbound shift reports work; inter-employee design sketched but not built |
| **Messaging (raw substrate)** | §1.1 (§2 rows 35-37); §1.3 (§2 row 36) | models_messaging.py:21-141 | inbox UI semantics for `thread_kind='inter_employee_notice'` (frontend ticket, not research) | **High** — substrate is production |
| **Memory (employee / agent)** | (none in research library) | core/models_agent_memory.py | **Memory Architecture research doc** — esp. how do employees remember each other's past verdicts? | **Low / UNKNOWN** — no research yet |
| **Decision Making** | §1.3 (§2 rows 38-42 + §3.10) | models_human_interface.py; models_orchestration.py | Decision precedent + multi-stakeholder approvals (§1.3 §10 Q6) | **Medium** — HAI lifecycle is robust; collaborative decisions absent |
| **Human Interface** | §1.3 (§2 rows 38-42, 58-59) | HumanAttentionItem + HumanFeedbackRecord + HumanPreference; views_inbox.py | DM-arrived WebSocket event surfacing (frontend ticket) | **High** — HAI lifecycle service production |
| **Automation (workflow autopilot)** | §1.3 (§2 row 47 — `WorkspaceTrigger`) | models_skin_layer.py | `workspace_autopilot_tick` location UNKNOWN (§1.3 §10 Q1); needs trace | **Medium / UNKNOWN** |
| **Agents (BaseAgent + AGENT_MAP)** | §1.1 (§3); §1.3 (§2 rows 1-9) | core/agent_router.py; core/agents/base_agent.py; topics/agent-system.md | (well-covered) | **High** — 83 agents production |
| **Spiders** | §1.3 (§3.6 + §3.7) | ai_core/spiders/; topics/spider-network.md | (well-covered) | **High** — 80 spiders + 1.14M item hashes |
| **Signal Processing** | §1.3 (§2 rows 48-50) | signal_aggregation_service.py; content_scoring_service.py | AutoTopic → Initiative wiring (§1.3 §10 Q2) | **Medium** — clustering production; downstream uncertain |
| **Workflows (Initiative pipeline)** | §1.3 (§2 rows 43-44 + §3.8) | models_document_registry.py; topics/initiative-pipeline.md; DREAM_INITIATIVE_WORKFLOW.md | (Initiative is documented; cross-employee composition is not) | **High** (pipeline) / **Medium** (composition) |
| **Scheduling (beat)** | §1.3 (§3.11) + 5-agent scheduling sweep evidence | core/celery.py:37-797; topics/celery-workers.md; AUDIT_FINDINGS.md §12 | **Cross-employee scheduling research doc** | **Medium** — beat tasks documented; cross-employee handoffs absent |
| **Observability** | §1.3 (§6 evidence scoring) | OpsRunEvent + AgentExecution + ToolCallRecord + LLMCallEvent + CeleryTaskEvent | (well-covered) | **High** — five audit tables compose |
| **Telemetry (LLM costs)** | §1.3 (§2 rows 8, 63-64) | models_llm_telemetry.py | (well-covered) | **High** — cleanup watchdog + total-request bound |
| **Reliability** | §1.3 (§5 + §7) | anthropic_client_factory.py; openai_client_factory.py; cleanup beat tasks | (well-covered) | **High** — multi-layer defense |
| **Infrastructure** | (none in research library — runtime evidence only) | topics/infrastructure.md; topics/celery-workers.md; Procfile | Redis broker persistence config — UNKNOWN (§1.3 §10 Q5) | **Medium / UNKNOWN** |
| **Knowledge Pipeline** | (none in research library) | docs/KNOWLEDGE_PIPELINE.md | (covered by KNOWLEDGE_PIPELINE.md narrative) | **High** — production pipeline |
| **Revenue / Outreach / Engagement** *(new domain, added S1273 v5)* | §1.9 §3.32 (LIGHT coverage — models + services + agents enumerated; no canonical topic doc) | models_outreach.py:18 (OutreachDraft); models_engagement.py:18 (EngagementEvent); models_meeting.py:18 (Meeting); models_close_pack.py:20 (ClosePack); opportunity_pipeline_orchestrator.py; ops_autopilot/revenue.py + outreach_generation.py + engagement.py | **Revenue Pipeline canonical architecture doc** (models + services + agents + PA tools + outbound channel + attribution) — see §5.12 | **WORKING** (per §1.9 §3.32) — models + services + agents shipped; whether pipeline drives revenue in prod vs is scaffolding awaiting activation is UNKNOWN |

---

## 4. Architecture Dependency Graph

The library's documents build on each other in a specific
order. Reading them out of order is technically possible but
each downstream doc assumes its upstream context.

```
                ┌─────────────────────────────────────────┐
                │  PLATFORM_INVENTORY.md (runtime anchor) │
                │  PLATFORM_WHAT_IT_IS.md (narrative)     │
                └────────────────────┬────────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────────┐
                    │  EMPLOYEE_OS_PRIMITIVES.md          │
                    │  (canonical primitives + §2 anti-   │
                    │   duplication matrix)               │
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────┐
        │  research/employee_os_communication_substrate_  │
        │  audit.md                                       │
        │  (Inventory of comms primitives + reuse class)  │
        └───────────────────┬─────────────────────────────┘
                            │
            ┌───────────────┴────────────────┐
            ▼                                ▼
┌───────────────────────────┐    ┌────────────────────────────────┐
│  research/employee_os_    │    │  research/employee_os_         │
│  communication_protocol_  │    │  collaboration_patterns.md     │
│  sketch.md                │    │  (Platform-wide inventory of   │
│  (One concrete path:      │    │  collaboration; 64-row table;  │
│  Auditor → Chief of Staff)│    │  11 substrates; 29 failures)   │
└──────────┬────────────────┘    └────────────────┬───────────────┘
           │                                      │
           ▼                                      ▼
┌───────────────────────────┐    ┌────────────────────────────────┐
│  [Future: v0 PR for the   │    │  research/governance_authority_│
│  protocol — gated by      │    │  evolution.md  [§1.4]          │
│  Chris's greenlight]      │    │  (4 planes; 35 gates; 12 inc.; │
│                           │    │  Symbol Mapping = P0 next)     │
└───────────────────────────┘    └────────────────┬───────────────┘
                                                  │
                                                  ▼
                                ┌──────────────────────────────────┐
                                │  research/symbol_mapping_        │
                                │  architecture.md  [§1.6]         │
                                │  (57 unique action strings; 5    │
                                │  mapping options A-E; 20         │
                                │  enforcement boundaries; SIGN-   │
                                │  with-edits from Rigby S1270)    │
                                └────────────────┬─────────────────┘
                                                 │
                                                 ▼
                                ┌──────────────────────────────────┐
                                │  research/actor_identity_        │
                                │  attribution_architecture.md     │
                                │  [§1.7]                          │
                                │  (19 identity concepts; 22       │
                                │  attribution surfaces; 25        │
                                │  registries; F11 executor/       │
                                │  sponsor/principal role vocab;   │
                                │  Rigby pressure-test SIGN-with-  │
                                │  edits S1271)                    │
                                └────────────────┬─────────────────┘
                                                 │
                                                 ▼
                                ┌──────────────────────────────────┐
                                │  research/authority_enforcement_ │
                                │  design_space.md  [§1.8]         │
                                │  (24 inputs; 20 boundaries; 12   │
                                │  modes; 6 options A-F; 15 anti-  │
                                │  patterns; 15-prereq DAG; Rigby  │
                                │  pressure-test SIGN-with-edits   │
                                │  S1272 — 3 SIGN-added boundaries │
                                │  WebSocket/Fleet/Spider)         │
                                └────────────────┬─────────────────┘
                                                 │
                                                 ▼
                                ┌──────────────────────────────────┐
                                │  [Future research mission —      │
                                │  recommended P0 per §1.8 §14.1]  │
                                │  Symbol Mapping Option Selection │
                                │  Design (picks from §1.6's 5     │
                                │  options; Chris gate; converts   │
                                │  research to design decision)    │
                                └────────────────┬─────────────────┘
                                                 │
                                                 ▼
                                ┌──────────────────────────────────┐
                                │  [Further future research —      │
                                │  see §9 roadmap]                 │
                                │  Actor Role Propagation ·        │
                                │  Authority Enforcement Design    │
                                │  Decision · Trust Propagation ·  │
                                │  Memory · Mission Composition ·  │
                                │  Cross-Employee Scheduling · …   │
                                └──────────────────────────────────┘
```

**Sibling arc (added S1273 v5) — whole-platform inventory.**
`platform_architecture_inventory.md` [§1.9] is NOT downstream
of the Employee OS arc. It's a sibling arc off the same three
anchors:

```
                ┌─────────────────────────────────────────┐
                │  PLATFORM_INVENTORY.md (runtime anchor) │
                │  PLATFORM_WHAT_IT_IS.md (narrative)     │
                │  EMPLOYEE_OS_PRIMITIVES.md (primitives) │
                └────────────────────┬────────────────────┘
                                     │
                       ┌─────────────┴─────────────┐
                       ▼                           ▼
        ┌──────────────────────────┐  ┌───────────────────────────┐
        │  Employee OS Arc         │  │  Whole-Platform Inventory │
        │  §1.1 → §1.2/§1.3 →      │  │  §1.9 (S1273)             │
        │  §1.4 → §1.6 → §1.7 →    │  │  32 domains + 9 flows +   │
        │  §1.8 (S1268-S1272)      │  │  11-mission roadmap       │
        └──────────────────────────┘  └───────────────────────────┘
```

§1.9 cites downstream findings from §1.4 (governance planes),
§1.6 (symbol mapping), and §1.7 (actor identity) where the
Employee-OS-arc research is the source of truth for a subset of
its findings. It does NOT depend on the arc's ordering.

**Reading the graph.** The two prior anchors at the top
(`PLATFORM_INVENTORY` + `PLATFORM_WHAT_IT_IS`) and the
primitives doc (`EMPLOYEE_OS_PRIMITIVES`) are *not* in the
research library but are **load-bearing context** for
everything in it. Any research doc that doesn't honor those
three is broken at the root.

The protocol sketch (§1.2) and the collaboration patterns
audit (§1.3) are siblings, both downstream of the substrate
audit (§1.1). They were written in the same session
(S1268) — the sketch came first, the wider audit came
second once Rigby's review of the sketch surfaced the broader
"how does collaboration work everywhere" question.

**Convention.** Every new research doc declares its parents
via the `companion_docs` frontmatter field. The dependency
graph above is reconstructable from those declarations.

---

## 5. Research Gaps

The library is **young** — 3 docs, all S1268. There are real
gaps. Below are the ones that have surfaced explicitly during
S1268 research, with priority and rationale. Each is a
*research* gap — i.e., something that should get its own
research doc before it gets implemented.

### 5.1 Governance + Authority Evolution — CLOSED S1269

**Closed by:** `docs/research/governance_authority_evolution.md`
(§1.4). Audit shipped 2026-06-30; Rigby SIGN-with-edits folded.
4 governance planes documented; 35 runtime gates inventoried;
warn-mode mechanics fully traced; 12 failure modes documented;
canonical foundation identified.

**Successor gap:** Symbol Mapping Architecture (see §5.2 below
— renumbered from prior §5.2; was P1, now P0 per §1.4 §11
recommendation).

### 5.2 Symbol Mapping Architecture — CLOSED S1270

**Closed by:** `docs/research/symbol_mapping_architecture.md`
(§1.6). Research shipped 2026-06-30; Rigby SIGN-with-edits
folded. 57 unique action strings enumerated across 68 total
entries. 5 mapping options (A steps self-declare / B tool
attribute / C hybrid / D central registry / E evidence-only)
inventoried with tradeoffs. 20 candidate enforcement layers
enumerated. 23 identifier registries classified (7 SAFE + 11
WRAPPER + 3 UNKNOWN post-Rigby-folded). §9 F11 blind spots
capture 7 architectural categories the design mission must
confront.

**Successor gap:** Authority Enforcement Design Space (see
§5.2b below) — first mission that composes §1.6 (WHAT) + §1.7
(WHO) into an actual enforcement gate.

### 5.2a Actor Identity & Attribution Architecture — CLOSED S1271

**Closed by:** `docs/research/actor_identity_attribution_architecture.md`
(§1.7). Research shipped 2026-06-30; Rigby pressure-test
SIGN-with-edits folded. 19 identity concepts inventoried, 22
attribution surfaces classified (13 Explicit / 2 Inferred / 4
Ambiguous / 1 Unreliable / 2 Missing), 14 identity shape
changes traced, 15 historical incidents catalogued (73%
effective case), 25 identity registries classified (14 SAFE
+ 7 WRAPPER + 1 DEPRECATED + 3 UNKNOWN), 17 enforcement
boundaries. **F11 introduces the executor_actor /
sponsor_actor / principal_user 3-role vocabulary** as
normative for downstream missions — treating any single field
as "the actor" without declaring which role it represents
produces "confidently wrong audit trails" (Rigby SIGN).

**Not a gap that pre-existed §5.2 explicitly**, but implicit
prerequisite that surfaced during §1.6 verifier loops (Symbol
Mapping cannot bind action_class without knowing which actor
attempted the action). Landed as an immediate follow-on same
day rather than deferred.

**Successor gap:** Authority Enforcement Design Space (see
§5.2b below).

### 5.2b Authority Enforcement Design Space — CLOSED S1272

**Closed by:** `docs/research/authority_enforcement_design_space.md`
(§1.8). Research shipped 2026-06-30; Rigby pressure-test
SIGN-with-edits folded (Medium confidence). 24 current
enforcement inputs classified; 20 candidate enforcement
boundaries (17 original + 3 SIGN-added: WebSocket / Fleet /
Spider); 12 enforcement modes with existing production
precedents for 8; 6 major design options A-F enumerated
neutrally (MissionRunner-centered / ToolDispatcher-centered /
Audit-first / Human-approval / Multi-layer / Governance-plane
composition); 33-incident historical matrix; 15 anti-patterns
(3 flagged as Tier-0 hazards: blocking all model writes,
enforcement before symbol mapping, silent enforcement); 15
prerequisites forming DAG (critical path Symbol Mapping →
Evidence Schema → Violation Event → Fallback → Layer choice →
Test Coverage + Human Review → Rollback → Per-Employee Opt-In →
Metrics Window → Trust + FP Thresholds). Named Symbol Mapping
Option Selection Design as the recommended P0 next research
per §14.1.

**Maintenance note:** §1.8 is **design-space research only**.
The 6 options A-F are enumerated for future consumption; none
is designated for implementation. Do not treat §1.8 as an
implementation greenlight — the downstream Authority
Enforcement Design Decision mission (see §14.3 in that doc)
requires Chris gate.

**Successor gap:** Symbol Mapping Option Selection Design (see
§5.2c below) — the first mission where the design space
narrows to a specific selection.

### 5.2c Symbol Mapping Option Selection Design — CLOSED S1274

**Closed by:** `docs/research/symbol_mapping_option_selection_design.md`
(§1.10). Research + design-preparation shipped 2026-07-01;
Rigby SIGN-with-edits folded (Medium confidence; recommendation
= Modify with 4 must-fix tightenings). **Recommendation:
Option E — Evidence-only mapping — as v0.** Extend a minimum
set of audit models with optional `action_class` field + all 3
actor role fields; instrument 3-5 highest-leverage producer
sites incrementally; emit `authority_action_observed` events;
NEVER blocks. Explicitly rejected Option C bundled standalone;
deferred Options A/B/D as tertiary layers pending Phase 5 E-only
telemetry. Set Symbol Mapping Event Schema Design as
recommended P0 next research per §16 of that doc.

**Maintenance note:** Option E is the v0 recommendation. It is
**not implementation** and **not enforce-mode**. Chris gates
every downstream step. §10.3.1 of that doc defines 4 graduation
triggers that force Chris re-decision within 30 days of any of:
(a) Tier-0 hazard observed ≥1 time; (b) PROHIBITED-level
violation rate > 0 per employee per 14-day window; (c) NULL rate
> 30% after Phase 4; (d) ≥90 days elapsed since Phase 5. This
prevents "E-forever cope."

**Successor gap:** Symbol Mapping Event Schema Design (see
§5.2d below) — designs the concrete event schema + producer
instrumentation contract + retention policy for Option E's
`authority_action_observed` event.

### 5.2d Symbol Mapping Event Schema Design — CLOSED S1275

**Closed by:** `docs/research/symbol_mapping_event_schema_design.md`
(§1.12). Design-preparation doc shipped 2026-07-01; Rigby SIGN-
with-edits folded (8 must-fixes + bonus #9). **Recommendation:
two-surface event stream** — `OpsRunEvent.data['authority_action_observed']`
for mission-scoped emissions + `ToolCallRecord.parameters['authority_action_observed']`
for non-mission tool calls, unified via a new
`authority_action_observed_stream` DB view (`UNION ALL`).
4 v0 emitters + 1 v0 first consumer. 21 payload fields
across 4 tiers (required / semi-required / optional / reserved).
4-value `mapping_confidence` enum {DEFINITE (emitter-local
certainty, not global truth), DECLARED (coverage-only, never
authoritative), HEURISTIC (reserved, banned), UNKNOWN}. Drift
stack: NULL-rate monitor + zero-fire audit + weighted
cross-emitter disagreement (never marks producer wrong without
adjudication) + weekly sampled-truthing loop with
`authority_mapping_correction` events + invariant validator
(I1–I7) + schema-signature check. 3 golden flows (GF-1
Documentation Manager audit, GF-2 PA-invoked `deliverable_tool.list`,
GF-3 employee_tool run_now for Bug Triage). Rollout: 5-phase
sequencing over ~10 weeks P0→exit.

**Maintenance note.** Design-preparation only. Not implementation.
Not enforce-mode. Every producer wire-up requires a separate PR
Chris gates. Rigby SIGN fold produced 8 must-fixes: (1) two-surface
+ UNION view replaces earlier "ambient OpsRun" mechanism; (2) drop
required `event_id`; (3) drop `notes` free-text field + downscope
`producer_version` to canary-only; (4) rename `delegator_actor` →
`caller_actor` (graph position, not 4th role); (5) reframe "5
producers" → "4 emitters + 1 consumer"; (6) rename `INFERRED` →
`DECLARED` + non-authoritative label; (7) add sampled-truthing
loop for stable-wrong-non-NULL detection; (8) `DEFINITE` ≠
canonical truth (weighted disagreement, not "producer X is
wrong" verdict). Bonus #9: reserved-keys policy + per-field caps.

**Successor gap:** Trust Propagation Model (§5.3) or Employee
Boundary Escalation Contract (§5.4) — both P1 at S1275 close.
No P0 sits in front of them; Chris picks the next STAGE.

### 5.2e Symbol Mapping v0 Implementation (P1 — post Chris sign-off on §1.12)

- **Why it matters.** §1.12 pins the schema; §5.2e is the
  first implementation session (not research). Rollout §15 of
  §1.12 outlines 5 phases (P0 schema + invariant validator; P1
  Emitter #1 MissionRunner preflight; P2 Emitter #2 step
  lifecycle + Step.action_class; P3 Emitter #3 ToolDispatcher +
  tool-schema action_class; P4 Emitter #4 employee_tool run_now
  + Consumer C1 Bug Triage step 4). Estimated 10 weeks P0→exit
  observation window.
- **Priority.** P1 (post-research). Blocked until Chris ratifies
  §1.12 as canonical.
- **Dependencies.** §1.12 canonical sign-off; `EMPLOYEE_OS_PRIMITIVES.md`
  §2 anti-duplication mandate; new `JobContract.mission_trigger_action_class`
  field + new `Step.action_class` attribute + new
  `pa_tool_schemas.py` per-tool `action_class` field.
- **Expected outcome.** 5 sequential PRs mapping to §15
  phases. Each PR carries greppable log lines +
  `verify_authority_action_observed_claims` management command
  registrations. No PR ships without golden-flow tests.
- **Type.** Implementation (not research). §1.12 is the last
  research artifact in the Symbol Mapping arc.

### 5.3 Trust Propagation Model (P1)

- **Why it matters.** S1264 shipped `authority_contract_observed`
  in warn-mode only. Per `mission_runner.py:264-894`, the event
  emits shape evidence but **never blocks**. Every research doc
  in this library has hit "but warn-mode doesn't enforce" as a
  boundary. Cross-employee dispatch is the first surface where
  the boundary actually matters.
- **Priority.** P0 next research mission per §1.3's §11
  recommendation. Rigby SIGN-clean on that recommendation.
- **Dependencies.** §1.3 (esp. §10 Q11), `mission_runner.py:258-275`,
  `docs/handoffs/SESSION_1264_*.md`,
  `core/employees/jobs.py:489-505` (Platform Auditor
  authority dict shape).
- **Expected outcome.** A research doc that scopes the
  symbol-mapping work needed to take authority strings (like
  `"recommend_remediations"`) and bind them to runtime symbols
  (tool names, FK methods). Plus trust-propagation primitives
  (when Employee A trusts Employee B's verdict, what's the
  contract?). Plus boundary cases (what happens when an
  authority contract changes mid-run?).

### 5.4 Memory Architecture (P1)

- **Why it matters.** Employees do not "remember" each other's
  past verdicts in their reasoning today. Bug Triage *queries*
  OpsRun rows from other employees (read-only composition), but
  there is no synthesized memory layer — no "last week the
  Auditor flagged this same finding" awareness inside the
  reasoning context. Derived from §1.3 §1 Finding F4 (no
  in-platform A→A reply contract today) — memory naturally
  falls out as a sub-question under trust propagation once
  inter-employee read-of-other-employee semantics exist.
- **Priority.** P1. Probably falls out of the Governance + Authority
  research naturally — but if it doesn't, it deserves its own
  pass.
- **Dependencies.** Governance research (above);
  `core/models_agent_memory.py` (current per-agent memory shape).
- **Expected outcome.** A doc that maps the existing
  `AgentMemory` / `AgentLearning` / `LearningInsight` /
  `SharedKnowledge` primitives, identifies whether they're
  shared-readable across employees, and proposes (research-only)
  what a "cross-employee episodic memory" layer would reuse vs.
  invent.

### 5.5 Cross-Employee Scheduling (P1)

- **Why it matters.** Per §1.3 §1 Finding F4 and Q8, the
  minimum missing runtime surface for inter-employee delegation
  is **a durable "subscribe-to-(employee, verdict)" primitive**
  that routes verdicts to a target employee's *next mission's
  preflight*. Today's AgentFollowupSubscription handles
  conversation-scoped wakeups, not mission-to-mission handoffs.
- **Priority.** P1 — depends on Governance research closing
  first because authority semantics gate the dispatch.
- **Dependencies.** §1.2 (protocol sketch), §1.3 (§2 rows 27-29).
- **Expected outcome.** A research doc that scopes whether the
  primitive is (a) a new model, (b) an extension of
  `AgentFollowupSubscription`, or (c) a pure read-side query
  pattern. Not a design — just the scope of the smallest
  missing piece.

### 5.6 Mission Composition (P1)

- **Why it matters.** Per Rigby S1268 review architectural-blind-
  spot note (folded into §1.3 §10 Q12), the two durable
  orchestration paths (Celery chain vs. MissionRunner step
  loop) don't compose. When a future mission needs to chain
  Celery tasks across employees, the canonical idempotency key
  across substrates is an open question — calendar-date scope
  (MissionRunner) vs. task_id (Celery) vs. event_id (EventBus)
  vs. UUID (AgentExecution) don't reconcile.
- **Priority.** P1 — touches Reliability + Observability if
  done poorly.
- **Dependencies.** §1.3 (Q12), `topics/celery-workers.md`.
- **Expected outcome.** A doc that names the canonical
  idempotency key (or proves none exists and what would have to
  give).

### 5.7 Observability / Failure Recovery (P2 — already strong)

- **Why it matters.** Observability is well-covered by §1.3 §6
  (evidence-and-auditability scoring). Failure recovery is
  well-covered by §1.3 §7 (29 documented failure modes).
- **Priority.** P2. Most failure classes are already
  documented with mitigations. A dedicated doc would be a
  consolidation pass, not new research.
- **Dependencies.** §1.3 §6 + §7; `docs/AUDIT_FINDINGS.md`.
- **Expected outcome.** Optional consolidated "failure
  taxonomy" doc that pulls the §7 incidents into a single
  reference. Not blocking.

### 5.8 Security Model / Permission Model (P2 — needs scoping)

- **Why it matters.** Service-token auth is referenced
  (`core/auth_middleware.py:113` only documents
  `PA_DB_HEALTH_RPC_TOKEN`), but the full scope of
  dispatch surfaces requiring auth is UNKNOWN per substrate
  audit §9 Q3. Cross-fleet messaging requires this answered.
- **Priority.** P2 — only blocking if a future research
  mission wants to cross fleet boundaries.
- **Dependencies.** TBD; needs an initial scoping pass to
  even know what to audit.
- **Expected outcome.** First a *scoping* doc (one page) to
  identify which surfaces need auth; then full research if the
  surface is non-trivial.

### 5.9 Configuration Architecture (P3 — possibly out of scope)

- **Why it matters.** Feature flags
  (`RIGBY_EVENT_INTAKE_ENABLED`, `MESSAGING_TOOL_ALLOW_SEND`,
  `CTO_DIAGNOSTIC_ENABLED`, `COO_DIAGNOSTIC_ENABLED`) are
  scattered. There may be an implicit convention but no
  documented one.
- **Priority.** P3 — UNKNOWN whether this needs research or
  just a one-page note in
  `docs/00-START-HERE/DOC_LIFECYCLE.md`.
- **Dependencies.** TBD.
- **Expected outcome.** Either a one-page convention note OR
  a scoping doc.

### 5.10 Knowledge Graph (P? — not raised yet)

- **Why it matters.** Mentioned in the mission spec as a
  candidate. Not raised in any prior research. No production
  evidence found for a knowledge-graph layer today.
- **Priority.** P? — premature. Surface only if a future
  research mission has a specific use case for it.

### 5.11 Focus Mode Inventory (P? — flagged by Rigby S1269 review)

- **Why it matters.** Rigby's S1269 review on §1.4
  noted that **"focus mode"** is a governance-like throttle
  that may live outside the GovernanceState/KillSwitch plane.
  §1.4 didn't scope focus mode (wasn't part of the original
  evidence sweeps). A follow-up scoping pass should determine
  whether focus mode is a fifth governance plane, a sub-feature
  of one of the existing four, or a distinct concept entirely.
- **Priority.** P? — depends on whether Employee OS reasoning
  has any dependency on focus mode state. If not, deferred.
- **Dependencies.** §1.4 (governance audit's §10.8 flags it).
- **Expected outcome.** A scoping doc (one page) to identify
  the surfaces, NOT a full audit.

### 5.12 Revenue / Outreach / Engagement Pipeline Canonical Architecture (P0-parallel — added S1273 v5 per Rigby review)

- **Why it matters.** Rigby's S1273 review on §1.9 caught this
  as a missed whole-platform domain — it exists in tools/models/
  services but is not represented as an end-to-end platform
  subsystem with a canonical architecture doc. Missing this
  research means any revenue-adjacent feature has no baseline
  to work from.
- **Priority.** P0 (parallel with §5.2c Symbol Mapping Option
  Selection). Different scope than the Employee OS arc; runs
  independently.
- **Dependencies.** §1.9 §3.32 (domain inventory shell), §1.9
  §4.9 (cross-domain flow), models_outreach.py + models_
  engagement.py + models_meeting.py + models_close_pack.py,
  ops_autopilot/revenue.py + outreach_generation.py +
  engagement.py + impact.py, opportunity_pipeline_orchestrator.py.
- **Expected outcome.** A canonical architecture doc covering
  models + services + agents + PA tools + outbound channel
  integration + revenue-attribution logic. Verify runtime state
  vs aspirational docs (`MASTER_PLAN_CREATIVE_INTELLIGENCE_
  EMPIRE.md`, external `BILLING_MONETIZATION_SYSTEM.md`). Rigby
  SIGN review. Result: promotes §1.9 §3.32 coverage from LIGHT
  to DEEP + potentially spawns a §1.10 research doc.

### 5.13 Observability Deduplication Audit (P1 — added S1273 v5)

- **Why it matters.** Per §1.9 §5.7, the platform has 5 parallel
  execution telemetry layers (`CeleryTaskEvent`, `LLMCallEvent`,
  `AgentExecution`, `ToolCallRecord`, `OpsRunEvent`) plus 14+
  event-shaped audit models. Whether they're necessary and non-
  overlapping or duplicate is undocumented. Any future
  observability feature is guessing at the design boundary.
- **Priority.** P1. Touches every future observability feature.
- **Dependencies.** `docs/EVENT_SYSTEM_INVENTORY.md`, §1.9 §3.25,
  §1.9 §5.7.
- **Expected outcome.** Trace a single "agent executes a tool
  that calls the LLM" scenario through all 5 execution telemetry
  layers + adjacent audit tables. Recommend rationalization
  (which to keep, which to deprecate, which to merge). Rigby
  SIGN review.

### 5.14 Sports / DBAO ↔ AI Studio Integration Sketch (P1 — added S1273 v5)

- **Why it matters.** Per §1.9 §3.10 + §1.9 §4.8, the DBAO
  stack (sports/odds/betting agents + models) is
  operationally-separate from AI Studio (content/signals/
  initiatives/deliverables). `sports_odds` is not a valid
  `SignalCluster` data_type track; sports predictions do NOT
  auto-create Initiatives; betting outcomes NOT fed to
  deliberation. Resolves the platform's biggest structural
  question ("what IS Donkey Betz — one platform or two?").
- **Priority.** P1. Structural question; unblocks content-
  pipeline decisions for sports content and betting-related
  deliberation.
- **Dependencies.** §1.9 §3.10 (DBAO inventory), §1.9 §3.9
  (Signal Engine), §1.9 §3.11 (Content Pipeline), §1.9 §3.12
  (Initiative Pipeline), §1.9 §4.8 (Sports flow).
- **Expected outcome.** Research doc documenting whether and how
  MLPrediction / PlacedWager / SharpAction outcomes should feed
  Signal / Initiative / Deliverable surfaces. Alternative:
  documented intentional island. Rigby SIGN review.

---

## 6. Research Principles

The principles below are extracted from the three S1268 docs
and the verifier-loop pattern they all share. They are not
opinion — they are what *worked* on the first three docs,
verified by Rigby's SIGN reviews.

1. **Evidence before opinion.** Every claim in a research doc
   carries a file:line cite or is marked UNKNOWN. There is no
   third option. "I think the system does X" without a cite is
   forbidden.
2. **Inventory before implementation.** Before you can propose
   a primitive, you must list the existing primitives that
   already cover the same surface. Anti-duplication is load-
   bearing per `EMPLOYEE_OS_PRIMITIVES.md` §2 + §4.1.
3. **Reuse before invention.** "Wrapper" beats "new model"
   beats "new admin UI." If a wrapper fits, the new model
   doesn't ship.
4. **Architecture before code.** Research docs exist to make
   PRs small. If a PR is small because the research is solid,
   the team has won.
5. **Document uncertainty.** When evidence is thin, mark
   UNKNOWN. Don't guess; don't fill gaps with plausible
   inference. The UNKNOWN list in §10 of each doc is the
   honest seed for the next research mission.
6. **Never silently assume.** When two doc-claims disagree
   (substrate audit said 6 EventBus streams; runtime says 8),
   the runtime wins per `DOC_LIFECYCLE.md` §2c. Flag the drift
   in the new doc; do not silently inherit the wrong number.
7. **Use verifier loops.** The doc author re-reads
   sub-agent cites by direct Grep/Read before synthesizing.
   No exceptions.
8. **Rigby independent review before architectural
   decisions.** Every research doc gets routed to Rigby via
   `tools/pa_local.sh` on the S1268 pinned conversation. The
   verdict (SIGN-clean / SIGN-with-edits / NEEDS-MORE) is
   recorded in the `verifier_loop` frontmatter field. Edits
   are folded before the doc is considered Active.
9. **Frontmatter declares lineage.** Every research doc lists
   its `companion_docs` so the dependency graph in §4 is
   reconstructable. If you don't declare your parents, you're
   not ready to publish.
10. **Authority is the only "must change" boundary.**
    Research-only missions don't touch runtime. The single
    exception: if mid-doc you discover that a prior research
    claim is wrong, the doc surfaces it (drift call) but does
    not patch the prior doc — patching happens in a separate
    pass with its own review.

---

## 7. Decision Matrix — "If you're about to work on…"

A pre-PR sanity gate. Find the row that matches your work;
read the documents in column 2 first. Skipping the read is the
fastest way to land a PR that violates the anti-duplication
matrix or re-introduces a closed failure class.

| About to work on… | Read these first |
|---|---|
| **Employee communication (anything)** | §1.1 + §1.2 + `EMPLOYEE_OS_PRIMITIVES.md` §4.7 (messaging_tool send guard) |
| **A new AI Employee** | Path B in full + `EMPLOYEE_OS_PRIMITIVES.md` §5 quick-start |
| **MissionRunner internals** | §1.3 §2 rows 17-23 + `mission_runner.py:1-230` + S1267 handoff |
| **`MissionRunnerConfig.auto_emit_verdict` semantics** | §1.3 Executive Summary item 6 (corrected by Rigby S1268 SIGN-with-edits) + §1.3 §2 row 19 + §1.3 §7 row 29 (protocol invariant change) + `core/employees/mission_runner.py:1127-1145` |
| **Governance flags or modes** | §1.4 §2.1 (full autonomy plane inventory) + §1.4 §4.6 (5 autonomy gates incl. KillSwitch UNKNOWN) + Path C |
| **Authority enforcement (vs. observation)** | §1.6 (5 mapping options + 20 boundaries) + §1.7 (17 boundaries + 3-role vocabulary) + §1.4 §3 (full lifecycle trace) + §1.4 §4.7 (authority plane gates) + §5.2b (Authority Enforcement Design Space P0 next) + S1264 handoff |
| **Anything using `JobContract.authority`** | §1.6 §2 (57 unique strings enumerated) + §1.6 §5 (mapping options A-E) + §1.6 §9 F1-F10 + §1.7 F11 + §1.7 §8.5 (executor/sponsor/principal roles) — a policy string is not a runtime symbol; do NOT assume it enforces anything today |
| **Actor identity on any new model / audit surface** | §1.7 §3.1 (22 attribution surfaces classified) + §1.7 §8.5 (3-role vocabulary) + §1.7 F11 — declare which of executor_actor / sponsor_actor / principal_user the field represents |
| **Adding `user` FK to OpsRun (or any "actor" field)** | §1.7 F1 + §1.7 F11 + §1.7 §13.1 — DO NOT ship without role clarity first; §1.7 explicitly warns adding a "user" field to OpsRun without role clarity codifies the executor / principal conflation as schema |
| **Any code using `agent_name` CharField** (ToolCallRecord / AgentExecution.owner_agent / LLMCallEvent) | §1.7 F4 (three ambiguous fields, undefined delegator-vs-executor semantics) + §1.7 §3.3 (evidence) — DO NOT assume the string is either delegator or executor; trace the call chain |
| **Any code using `runs_as_username` or `_resolve_runs_as_user_id`** | §1.7 §2.4 + §1.7 F3 (silent-None on missing User) + §1.7 F11 (this is a principal_user selector, NOT the executor_actor) — treating it as "actor" is a documented anti-pattern |
| **Duplicate Agent row risk** (any new agent-creation site) | §1.7 F5 (recurring failure class per S1263 PR #2754 + migration 0374) + `deliverable_aliases.py:33-47` (`canonicalize_agent_name` + `AGENT_NAME_ALIASES`) — must canonicalize at write time |
| **PA tool actor / user context propagation** | §1.7 §7 (17 boundaries; F6 identifies 3 structural drop points) + §1.6 §6 (20 symbol boundaries) + `tool_dispatcher.py:687-720` (`AssistantProfile.get_allowed_tools` is the ONLY canonical-actor gate today per §1.7 F7) |
| **Any authority enforcement idea** | §1.8 §9 (6 options A-F evaluated neutrally) + §1.8 §10 (15 anti-patterns incl. Tier-0 hazards) + §1.8 §11 (15-prereq DAG) — DO NOT ship enforce-mode before §5.2c Symbol Mapping Option Selection lands + Chris gates |
| **`AuthorityLevel` enum usage anywhere new** | §1.8 F1 — enum has exactly 1 runtime consumer today (shape-counter at `mission_runner.py:864-867`); adding decision-making consumer is a design-decision-scoped change |
| **New enforcement gate (INLINE)** | §1.8 F8 (LLMEnforcer fail-open precedent at `llm_enforcer.py:237-238`) + §1.8 §11 prereq #5 (fallback behavior must be explicit) — cite fail-open vs. fail-closed rationale |
| **Adding action_class to any audit model** | §1.8 §11 prereq #3 (Evidence Event Schema) + §11 prereq #4 (Violation Event Schema) — schema shape must precede any model migration |
| **WebSocket / Fleet / Spider handler that touches employee-scoped work** | §1.8 §3 rows 18-20 (added per Rigby SIGN pressure-test) — these boundaries are named but not yet mode-tabulated; design mission scope |
| **Cross-plane governance interaction (authority × autonomy × budget × human)** | §1.8 §7.5 (8 new composition questions) + §1.4 F1 (planes don't compose today) — this is deferred future research per §1.8 §14.4 |
| **KillSwitch (arming, status, enforcement)** | §1.4 §2.1 row 2 + §1.4 §4.6 (UNKNOWN row) + §1.4 §8 F3 (write-only finding) — DO NOT assume KillSwitch blocks dispatch today |
| **Budget freeze / LLM cost gates** | §1.4 §2.3 + §1.4 §8 F4 (one-way sync + desync risk) + `core/llm_enforcer.py:200-260` |
| **Human attention lifecycle (auto-approve / escalate)** | §1.4 §2.4 + §1.4 §5 (full flow + 7-condition auto-approve gate + escalation ladder) |
| **Adding any new tool to PA** | §1.1 §4.4 (handler/schema delta gotcha) + memory rule `feedback_llm_autofills_boolean_params_with_false.md` |
| **`messaging_tool` (any change)** | `EMPLOYEE_OS_PRIMITIVES.md` §4.7 + §1.1 §8 DO-NOT-REUSE row + `td_handlers_core.py:3693-3711` |
| **Mission scheduling (any new beat)** | Path E + `topics/celery-workers.md` + `EMPLOYEE_OS_PRIMITIVES.md` §4.6 (app.conf.imports requirement) |
| **Observability or audit chain** | §1.3 §6 (evidence-and-auditability scoring) + §1.3 §2 rows 7-9 |
| **Reliability / timeout / retry policy** | Path G + §1.3 §7 (rows 10, 17, 18, 19 esp.) |
| **Escalation surfaces** | §1.3 §3.5 (HAI creators) + §1.3 §3.9 (MissionRunner escalation) + §1.2 §8.1 (Auditor has no HAI creation authority) |
| **Human attention (HAI lifecycle)** | §1.3 §2 rows 38-41 + §3.5 + `core/services/human_attention_lifecycle.py:36-728` |
| **Deliverable creation / status flips** | Memory rules `feedback_deliverable_tool_use_append_for_large_payloads`, `feedback_deliverable_status_via_content_complete`, `feedback_deliverable_create_defaults_to_completed` + §1.1 §7.8 |
| **Spider → downstream work chains** | Path F + §1.3 §3.6 + §3.7 |
| **Anything that says "new model"** | `EMPLOYEE_OS_PRIMITIVES.md` §2 (anti-duplication matrix) + §1.3 §9 (anti-duplication analysis). If a row matches, you are not adding a model. |
| **Onboarding / any cross-domain scoping work** *(added S1273 v5)* | §1.9 whole-platform inventory (32-domain map + 9 cross-domain flows) — start here for shape of the system. Then dive into whichever §3.n row matches your work + cited Employee-OS-arc docs. |
| **Anything touching Revenue / Outreach / Engagement / Meeting / ClosePack** *(added S1273 v5)* | §1.9 §3.32 + §1.9 §4.9 + §5.12 (canonical architecture doc gap) — DO NOT assume the pipeline flow described in aspirational docs (`MASTER_PLAN_CREATIVE_INTELLIGENCE_EMPIRE.md`, external `BILLING_MONETIZATION_SYSTEM.md`) matches runtime; verify. |
| **Anything sports/betting-adjacent that touches content or signals** *(added S1273 v5)* | §1.9 §3.10 (DBAO inventory) + §1.9 §4.8 (Sports flow) + §5.14 (Integration Sketch gap). The two sides do NOT currently compose (`sports_odds` is not a valid SignalCluster data_type); do NOT assume they do. |

---

## 8. Architecture Timeline

The library is young. Here is the actual chronology with
influence callouts.

| When | Doc | What it added | Influenced |
|---|---|---|---|
| **S1268 P0 #1** (2026-06-30) | `employee_os_communication_substrate_audit.md` (§1.1) | First inventory of comms primitives between AI employees. 36-row table. Reuse classifications. 12 incident-class failure history. Rigby SIGN-clean. | Made §1.2 possible — the protocol sketch reused the SAFE rows directly. Also stated EventBus had "6 named streams" at line 135 — runtime is **8** per `event_bus.py:21-30`. The drift was caught in §1.3 §12 and Rigby independently corroborated it. The substrate audit text itself has **not** been amended (research-only constraint per S1268); the drift is flagged in §1.3 §12 (cross-reference + documentation drift table) and propagated forward as the canonical value. |
| **S1268 P0 #2** (2026-06-30) | `employee_os_communication_protocol_sketch.md` (§1.2) | First concrete inter-employee write path scoped (Platform Auditor → Chief of Staff). Helper signature, metadata envelope, threading model, 3-layer dedupe, terminal-gate, expires_at freshness boundary. Rigby SIGN-with-edits — 2 substantive edits folded (L3 helper-side dedupe + cadence Option A default). | Surfaced the question "but how does collaboration work *everywhere else* on the platform?" — which became §1.3. |
| **S1268 P0 #3** (2026-06-30) | `employee_os_collaboration_patterns.md` (§1.3) | Platform-wide audit. 64-row primitive inventory. 11 distinct collaboration substrates. 12 flow diagrams. 29 documented failure modes (12 new). Q1-Q8 answered. Rigby SIGN-with-edits — 1 substantive correction folded (MissionRunner verdict event is conditional, not guaranteed) + 1 architectural blind-spot note added (canonical idempotency key across orchestration paths). | Set the recommendation for the next research mission (Governance + Authority Evolution). Surfaced gaps that become §5.1–§5.7. |
| **S1268 P0 #4** (2026-06-30) | `ARCHITECTURE_INDEX.md` (this doc) | The first navigation / index doc for the research library. Establishes the corpus's identity, dependency graph, and maintenance rules. | Will be cited by every future research doc's `companion_docs`. |
| **S1269** (2026-06-30) | `governance_authority_evolution.md` (§1.4) | First architectural-discovery audit of the governance + authority surface. 63-row primitive inventory across 4 planes. 35 runtime gates. 12 governance-specific failure modes (3 new beyond S1268 collaboration audit baseline). 48 SAFE / 11 WRAPPER / 0 DO-NOT-REUSE / 0 DEPRECATED / 3 UNKNOWN. Rigby SIGN-with-edits (plane-count framing consistency, gate-count typo, two clarifications folded). | Set Symbol Mapping Architecture as the recommended P0 next research mission. Index v2 updated per maintenance rules §10.1 (this row + §1.4 + §3 domain map + §4 dependency graph + §5 gap recategorization + §7 decision matrix expansion + §9 roadmap promotion). |
| **S1270** (2026-06-30) | `symbol_mapping_architecture.md` (§1.6) | First architectural-discovery of the WHAT question. 57 unique action_class strings (68 total entries) enumerated. 5 mapping options (A steps self-declare / B tool attribute / C hybrid / D central registry / E evidence-only) with tradeoffs. 20 candidate enforcement layers. 23 identifier registries classified. 23 historical incidents (5 YES + 10 PARTIALLY + 8 NO). F1-F11 findings incl. F11 (7 architectural blind spots via Rigby SIGN). Rigby SIGN-with-edits — 2 must-fix (§8 `_AuthorityContractMalformedError` scope narrowed; §2.6 parallel-vocabulary type/shape anchor added) + 3 optional (I-S4 wording, I-S3 dual-cite, Option E disclaimer) + 2 discoverability (AssistantProfile registry, §2.4 normalization caveat) folded. | Established the "WHAT" half of the enforcement primitive. Surfaced the WHO question that became §1.7 (Actor Attribution) as an immediate follow-on same session. |
| **S1271** (2026-06-30) | `actor_identity_attribution_architecture.md` (§1.7) | First architectural-discovery of the WHO question. 19 identity concepts. 22 attribution surfaces classified (13 Explicit / 2 Inferred / 4 Ambiguous / 1 Unreliable / 2 Missing including OpsRun). 14 identity shape changes + 3 structural drop boundaries (HTTP→Celery, MissionRunner config→OpsRun, MissionRunner→Step.fn). 15 historical incidents (7 YES + 4 PARTIALLY + 4 NO — 73% effective case). 25 identity registries (14 SAFE + 7 WRAPPER + 0 DO-NOT-REUSE + 1 DEPRECATED + 3 UNKNOWN). 17 enforcement boundaries. Rigby pressure-test SIGN-with-edits, Medium confidence — 4 must-fix folded incl. **§8.5 introducing the executor_actor / sponsor_actor / principal_user 3-role vocabulary as normative** (biggest architectural risk: conflating the three into a single "actor" label). F1 + F9 language softened per Rigby. §3.5 added inventorying attribution patterns the platform does NOT ship. §9.4 Attribution-first counterargument acknowledged. §5 role-confusion framing note. | Established the "WHO" half of the enforcement primitive. Together with §1.6, closes the composite prereq. Set Authority Enforcement Design Space as recommended P0 next research (design mission that composes both). Index v3 updated per §10.1 (this row + §1.7 row above + §1.6 row above + §3 domain map + §4 dependency graph + §5 gap closure + §7 decision matrix expansion + §9 roadmap advancement). |
| **S1273** (2026-07-01) | `platform_architecture_inventory.md` (§1.9) | First whole-platform architectural inventory — the counterpart to the Employee-OS-focused §1.1-§1.8 arc. Six parallel Explore sub-agent sweeps synthesized into 32 domains (Cognition & agents: 7 / Data ingestion: 4 / Content & workflow: 2 / Revenue & GTM: 1 / Knowledge & memory: 3 / Human interface: 6 / API: 1 / Governance & ops: 4 / Infrastructure: 4). 9 cross-domain flows. 8 duplicate/overlapping system categories. Architecture Maturity Matrix rating every domain across Coverage / Maturity / Operational Health / Drift Risk / Debt Risk. 11-mission recommended research roadmap. Rigby SIGN-with-edits, Medium confidence, via fresh isolation pin `pa-02cfd3206302352f` (kept separate from shared S1270+ arc pin `pa-cbcc410b32714f60` per Chris's context-crossing directive). 6 substantive edits folded: (1) added missed §3.32 Revenue / Outreach / Engagement Pipeline domain + §4.9 flow — Rigby caught this as biggest missing platform subsystem; (2) downgraded §3.27 Auth STABLE → PARTIAL with trust-boundary enumeration; (3) upgraded §3.7 LLM Provider Registry WORKING → STABLE (core; failover missing); (4) tightened §1 Exec Summary count language; (5) added §3.31 Event Bus vs Observability separation-of-concerns paragraph; (6) expanded §9 roadmap 10 → 11 missions with Revenue Pipeline canonical architecture doc elevated to #2. | Established the whole-platform counterpart to the Employee-OS-focused arc. Chris's direction at close: "the next cleanup should be updating ARCHITECTURE_INDEX.md so this becomes the whole-platform counterpart to the Employee OS research library." Index v5 updated per §10.1 (this row + §1.9 row + §1 preamble rewrite + Path H reading path + §3 Revenue Pipeline domain row + §4 sibling-arc dependency graph extension + §5.12/§5.13/§5.14 gap entries + §7 decision matrix +3 whole-platform rows + §9 roadmap lateral research expansion referencing the 11-mission whole-platform roadmap in §1.9). Also caught + corrected v4 frontmatter drift — prior pass added Appendix C but never bumped last_verified line. |
| **S1272** (2026-06-30) | `authority_enforcement_design_space.md` (§1.8) | First design-space research — the mission that consumes S1270 + S1271 as INPUT premises and enumerates enforcement design options without picking. 24 enforcement inputs (13 RUNTIME-VERIFIED / 7 OBSERVATION-ONLY / 3 ASPIRATIONAL / 1 UNKNOWN + 8 GAPS). 20 candidate enforcement boundaries (17 original + 3 Rigby SIGN-added: WebSocket, Fleet, Spider — closing the biggest boundary-completeness gap). 12 enforcement modes with 8 existing production precedents; 4 without analog. 204-cell boundary × mode compatibility matrix (17-row form; 3 SIGN-added boundaries not yet cross-tabulated). 4-per-level AuthorityLevel semantics (16 interpretations, none chosen). 11 canonical actor-role scenarios × 3 roles + audit path. 4-plane governance composition with 8 new questions + 1 existing cross-plane touch. 33-incident consolidated historical matrix. **6 major design options A-F enumerated neutrally** (MissionRunner-centered / ToolDispatcher-centered / Audit-first / Human-approval / Multi-layer / Governance-plane composition). 15 anti-patterns (3 Tier-0 hazards: blocking all model writes, enforcement before symbol mapping, silent enforcement). 15-prereq DAG. Rigby pressure-test SIGN-with-edits, Medium confidence — 8 must-fix folded: §3 gained 3 first-class boundaries (WebSocket, Fleet, Spider); §9.0 neutrality guardrail; §9.1 + §9.2 annotation-burden failure modes; §9.6 policy-ossification risk; §8.4 rephrased separating prevent-modes from audit/warn modes; §10 Tier-0 hazards callout; §6.1 role-propagation rule of thumb; §14 P0/P1 dependency-not-preference semantics + §14.2 (i)/(ii) split. F1 (AuthorityLevel has 1 runtime consumer, a shape-counter) and F8 (LLMEnforcer fail-open precedent) are load-bearing findings. | Established the design space for authority enforcement. **First mission carrying design-space content per §9 STAGE 2 pacing note.** Set Symbol Mapping Option Selection Design as recommended P0 next research (§14.1). Maintenance note: this doc is **design-space only** — the 6 options A-F are for future consumption, not implementation. Index v4 updated per §10.1 (this row + §1.8 row + §3 domain map + §4 dependency graph + §5 gap closure §5.2b + new §5.2c + §7 decision matrix expansion + §9 roadmap advancement STAGE 2 → STAGE 3). |
| **S1274** (2026-07-01) | `DOMAIN_RESEARCH_PLAYBOOK.md` (§1.11) | **First `authority: process` doc in the library.** Codifies the S1268-S1274 methodology into a reusable playbook so future Claude Code sessions can start domain audits with short commands ("Start research group 1300: Memory") instead of 4,000-word prompts. Establishes: research group numbering (1300s Memory → 1900s Event Architecture), output-path convention (`docs/research/domains/<slug>/<session_id>_<slug>_architecture_audit.md`), 27 standard audit questions, 20-section document template with frontmatter, 6-sub-agent parallel sweep pattern, classification rules verbatim from S1274 §11 (Coverage / Maturity / Risk / Finding Type), Rigby SIGN review shape including fresh-isolation-pin practice (S1273/S1274 lesson) and grep-verification pattern (S1274 EventBus lesson), commit rules (default: don't; when Chris says "commit it": specific index-update checklist). Not routed to Rigby — process doc, not research finding. Chris explicit direction at close of drafting: "register it now and commit." | Sets the standard for research groups 1300-1900. Should be the FIRST doc a fresh Claude Code reads after `CLAUDE.md` when starting a domain audit. Distinguishing property: `authority: process` (rules for other docs), not `authority: research` (findings). Index v7 updated per §10.1 (this row + §1.11 row + Appendix E pass notes). |
| **S1300** (2026-07-01) | `domains/memory/1300_memory_domain_scoping.md` (§1.13) | **First parent-scoping doc in the library.** Opens Research Group 1300 (Memory / Knowledge / Embeddings — playbook §12 queue slot 1). Chris opened via playbook §11 short command (`Start research group 1300: Memory`) but paused before standard a-f scope-pick with directive: "Your clarification uncovered an architectural ambiguity rather than a simple scoping question. Treat this as a Phase 0 domain-definition exercise." Doc enumerates 8 candidate memory subdomains (A: Semantic Knowledge / B: Personal-Adaptive / C: Agent Working / D: RAG Retrieval / E: Docs Corpus / F: Conversational-Thread [no §3 row yet] / G: Employee OS Mission Memory [delegated] / H: Runtime Cache-Correctness). Recommends parent-with-children shape citing S1273 3-row Memory cluster + §5.4 multi-store overlap flag + playbook §2 rule 3 sub-group permission. Chris D1-D5 locked 2026-07-01: (D1) parent-with-children; (D2) Category G delegated to Employee OS 1200s arc; (D3) RAG excluded_missing_provenance finding (surfaced Rigby search_docs at S1300 open — 8 pre-filter → 7 excluded_missing_provenance + 1 excluded_mismatch → 0 for OpsRun/MissionRunner/JobContract) parked as S1301 input; (D4) P2 renamed "Memory Store Overlap Audit" → "Memory Persistence Architecture" (durability + authority frame); (D5) S1399 canonical summary planned as arc closer. Group 1300 shape: S1300 parent → S1301 RAG Lanes → S1302 Persistence → S1303 Conversational → S1304 Docs↔RAG Boundary → S1305 Runtime Correctness → S1399 summary (7 sessions). Session ENDED EARLY per Chris close directive — Phase 0 scoping only; no P1 audit in this session. Open decisions at close: (D6) S1301 launch cadence — default pause; (D7) Rigby SIGN routing on parent — default skip per playbook §9. Rigby not routed for SIGN on parent doc (scoping ≠ audit). | **First parent-scoping doc** — introduces the "parent doc gates arc shape via Chris decisions" pattern. Validates the DOMAIN_RESEARCH_PLAYBOOK.md §11 short-command workflow (first exercise). Chris directives at close: (a) commit approval given for S1300 parent + INDEX bump; (b) PR "marked ended early for core research" — Phase 0 landing only, P1 (S1301) deferred; (c) pin `pa-aa54193f240f4846` preserved for S1301 continuity (no rotation). Index v9 updated per §10.1 (this row + §1.13 row). |
| **S1275** (2026-07-01) | `symbol_mapping_event_schema_design.md` (§1.12) | **First mission in the library shipping an implementation-ready schema spec.** Closes §5.2d. Takes §1.10's Option E v0 recommendation and pins the concrete event: canonical name (`authority_action_observed`), two-surface host (`OpsRunEvent` mission-scoped + `ToolCallRecord.parameters` non-mission tool calls, unified via new `authority_action_observed_stream` DB view), 21 payload fields (7 required + 5 semi-required + 6 optional + 3 reserved), 4 v0 emitters + 1 v0 first consumer (Bug Triage step 4 is consumer, not "producer #5"), 4-value `mapping_confidence` enum (DEFINITE = emitter-local certainty *not* global truth, DECLARED = coverage-only *never* authoritative, HEURISTIC reserved+banned, UNKNOWN honest NULL), drift stack across 6 patterns (NULL rate + zero-fire + weighted cross-emitter disagreement + weekly sampled-truthing loop + invariant validator I1–I7 + schema-signature check), 3 golden flows, batch-mode v0 dashboard, 15-item out-of-scope list, 5-phase ~10-week rollout sketch. Five parallel Explore sub-agents produced: (1) 7-model audit surface inventory identifying OpsRunEvent-lacks-user-FK as largest gap; (2) 5 producer candidates ranked (35-44% authority string coverage estimate); (3) actor-role availability matrix showing ToolDispatcher has all 3 roles + S1271 F4 delegator/executor ambiguity flag; (4) action_class population confidence ranking; (5) drift/quality prior-art scan finding STRONG reuse for zero-fire (S1245) + claim-verification (S1099), NO precedent for cross-source truthing (largest gap). Rigby pressure-test SIGN-with-edits — **8 must-fixes + bonus #9 folded**: (1) drop "ambient OpsRun" for two-surface + UNION view; (2) drop required `event_id`, add optional `idempotency_key`; (3) kill free-text `notes`, downscope `producer_version` to canary-only, replace with 128B-capped `debug_context`; (4) rename `delegator_actor` → `caller_actor` (graph position, not 4th role) + explicit semantics block; (5) reframe "5 v0 producers" → "4 emitters + 1 consumer"; (6) rename `INFERRED` → `DECLARED` with explicit non-authoritative label; (7) add sampled-truthing loop (weekly N=25 per emitter × tier; `authority_mapping_correction` events; correction_rate KPI) — catches stable-wrong-non-NULL that other stack layers miss; (8) `DEFINITE` ≠ canonical truth (weighted disagreement + `suspected_mislabel` never "producer X wrong" — prevents false-positive alert cannon); bonus (9) reserved-keys policy + per-field caps + hard 1024B total cap. Rigby SIGN-clean on: warn-mode-only v0 choice; two-surface honesty over ambient-run synthetic grouping. | **First implementation-ready schema in the library.** Set STAGE 5 to Trust Propagation Model (§5.3) or Employee Boundary Escalation Contract (§5.4) — both P1 with no P0 in front. Maintenance note: §1.12 is design-preparation ONLY. Not implementation. Not enforce-mode. Rollout §15 is sequencing sketch, not merged PR. Index v8 updated per §10.1 (this row + §1.12 row + §5.2d closure + new §5.2e implementation-slot + §9 roadmap STAGE 4 CLOSED / no new P0 STAGE). |
| **S1276** (2026-07-01) | `DOMAIN_RESEARCH_PLAYBOOK.md` §1.11 — **v1 → v2 extension** | **First playbook version bump.** Restructured v1 into 7 parts / 24 sections. Formalized fifteen areas that emerged after v1 shipped across the S1268-S1275 arc and the S1300 parent-scoping experiment: (§2) research group lifecycle — parent → children → canonical summary → index update → complete, five stages with rationale for each; (§3) phase discipline — the research / design-preparation / design-decision / process / navigation / implementation split with `authority:` frontmatter field distinguishing them, Symbol Mapping arc as canonical exemplar (§1.6 research → §1.10 design-prep → §1.12 design-prep → §5.2e implementation); (§4) xx99 canonical summary convention with intra-range structure (NN00 parent / NN01-NN98 children / NN99 summary); (§5) canonical folder structure with legacy-doc grandfathering rule; (§6) self-describing metadata standard — adds `research_group`, `child_slot`, `dependencies_on`, `delegates_to`, `delegated_from` frontmatter fields with a required-fields-by-doc-type matrix; (§7) cross-reference policy — never duplicate, always reference; (§8) parent doc responsibilities — codifies the S1300 exemplar into a template (§11.1); (§10) canonical summary responsibilities — pins the xx99 template (§11.3) and rationale for the slot; (§11) three doc templates — parent + child audit + canonical summary; (§15) stage-scoped Rigby routing — table maps stage to SIGN requirement, canonical summary and design-prep get extra pressure-test questions; (§17) graduation criteria — objective checklist for `single-audit` vs `parent-with-children` groups with `not-started` / `in-progress` / `awaiting-summary` / `closed` / `stalled` states; (§18) domain dependency mapping — formalizes `dependencies_on` / `delegates_to` / `delegated_from` semantics as informational-not-blocking; (§19) generalization requirements — 13-domain verification list + anti-domain-specific-language rules + pre-audit 5-minute mental check; (§20) architecture evolution policy — the playbook is a living artifact; additive-first evolution, backwards compat, reality-wins rule mirrors DOC_LIFECYCLE §2c, formal change proposal workflow, changelog now in §20. All v1 content preserved semantically. New short commands: `Continue research group NNNN: <slot>` and `Close research group NNNN`. Chris directive at S1276 open: *"formalize the research process itself so future domain research becomes repeatable instead of prompt-driven."* Not routed to Rigby — process document, not research finding (per §15's own rule for `authority: process`). | Playbook is now the load-bearing foundation for every future domain research group. v2 makes the framework self-describing: a fresh Claude Code that reads *only* the playbook + ARCHITECTURE_INDEX + PLATFORM_INVENTORY can execute a research arc end-to-end. First playbook version bump — sets the pattern for how the framework itself evolves. Older research groups closed under v1 stay valid under v1 per §20 backwards-compat rule. Index v10 updated per §10.1 (this row + §1.11 body extension). |
| **S1274** (2026-07-01) | `symbol_mapping_option_selection_design.md` (§1.10) | **First mission in the library carrying an evidence-based recommendation Chris can gate.** Narrows §1.6's 5 Symbol Mapping options to a v0 selection. Five parallel Explore sub-agents produced: (1) 24-system runtime symbol inventory with 2 verified drifts from S1270 (REMOVED_TOOL_ALIASES 12→13; GATEWAY_TOOLS 23→22); (2) 100-cell coverage × reuse matrix (A:1/7/12, B:2/6/12, C:5/7/8, D:11/7/1 flattest, E:2/4/14); (3) drift risk ranking (A/B/C VERY HIGH; D HIGH; E MEDIUM lowest); (4) actor compatibility (E only option carrying all 3 roles end-to-end IF audit models extended); (5) failure modes + rollout + minimum viable event shape. **Recommendation: Option E — Evidence-only mapping — as v0.** Extend a minimum set of audit models with optional `action_class` field + all 3 actor role fields; instrument 3-5 highest-leverage producer sites incrementally; emit `authority_action_observed` events; NEVER blocks. **End-state (Chris-gated later):** E foundation + Option B tool schema attribute for pre-dispatch enforcement. **Explicitly rejected:** Option C bundled standalone. Rigby pressure-test SIGN-with-edits, Medium confidence, recommendation = Modify — 4 must-fix folded: (1) §8.8 tone alignment on whole-platform generalization vs. 2/4/14 matrix (Fleet/WebSocket/Spider not covered at v0 until instrumented); (2) §10.3.1 catastrophic-action graduation guardrail (4 telemetry triggers forcing Chris decision within 30 days — prevents "E-forever cope"); (3) §12.1 non-NULL misclassification drift pattern (sample-based truthing + cross-source consistency + golden-flow tests — higher-risk than producer omission); (4) §11 employee_handle vs. executor_actor clarification (employee_handle is Employee OS identity, NULL for non-mission actions; executor_actor is generalized runtime executor). Rigby SIGN-clean on: risk posture + reversibility (strongest argument); actor role separation. | **First evidence-based recommendation in the library.** Set Symbol Mapping Event Schema Design as recommended P0 next research (§16). Maintenance note: Option E is v0 recommendation ONLY. Not implementation. Not enforce-mode. §10.3.1 guardrail forces Chris re-decision within 30 days of graduation triggers. Index v6 updated per §10.1 (this row + §1.10 row + §5.2c closure + new §5.2d + §7 decision matrix expansion + §9 roadmap STAGE 3 CLOSED / new STAGE 4 Event Schema Design). |

| **S1277+S1278** (2026-07-01/02) | `RESEARCH_OPERATING_SYSTEM.md` (§1.14) + `claude_research_startup_introspection.md` (§1.15) | **Canonical process framework for every Claude Code session — superset containing the playbook.** S1276 introspection audited actual startup behavior and named P0/P1/P2 documentation gaps. S1277 drafted OS v1 (10 request classes + Level A/B bootstrap + authority hierarchy + startup contracts + templates + navigation audit + repeatability target + one-year vision + P0/P1/P2 debt + migration plan). Rigby SIGN cycle 1 (fresh pin `pa-95ce3cbf0a2aa0cc`, Medium confidence) folded 15 must-fixes: Level A/B split; minimal-context capture; prescriptive/observational labeling; OPS/DEPLOY/INCIDENT class 11 + contract §8.11; class-boundary rules (Design-Prep vs ADR / Review vs Meta / Bug vs Ops); state-reconciliation ritual §6.6; Tier 1a/1b split; Tier 5/6 disambiguator; Tier 9/10 boundary; NAVIGATION QUERY output format; META-PROCESS drift-scan; Investigation Log + Ops Incident Report templates. S1277 re-issued expanded scope (16 parts + 14 deliverables); OS extended to v2 with six new parts: Research Philosophy (stop condition + 4 anti-patterns), Context-Kit Integration (§2 ownership matrix + §2.7.1 operational cadence + §2.9 do-not-duplicate list), Documentation Ownership (§11 matrix + 6 anti-patterns), Research Contract (§13 8 mandatory fields), Completion Contract (§14 10-item close checklist + handoff template), Research Debt (§15 concept + 7 categories + defensible formula + 90-day escalation). Renumbered existing parts 3-12 + 16-19 to match spec ordering; renumber cascade introduced 13 playbook §-ref bugs (cascade prefix-matching corrupted `playbook §N` external refs). Rigby SIGN cycle 2 (fresh pin `pa-117d3edf9d7b80f8`, Medium confidence) folded 12 must-fixes: §1.2 stop-condition enforcement rule; §1.5 additional anti-patterns; §2.3 drift-tooling + entrypoint pattern rows; §2.7.1 cadence; §2.9 DOC_LIFECYCLE + playbook templates entries; §11.1 owner tightening (CLAUDE.md single-owner = Chris; 00-START-NEXT-SESSION single-owner = Claude); §11.4 zombie/shared/verification anti-patterns; §13.1 field 5 Decision + Ratifier + Deadline format; §14.7 "Open risks / landmines" handoff section; §15.1.1 seven debt categories; §15.3 defensible priority formula `severity_weight × blocking_count × (1 + age/30)`; §15.6 debt vs follow-on clarification. S1278 ratification pass: 13 playbook cross-ref cascade artifact bugs corrected (playbook §5→§3 phase discipline, §4→§2 STAGE 0, §17.4→§11.4 templates section, §19→§13 sub-agents, §12→§9 canonical Qs, §8→§6 metadata, §9→§7 cross-ref policy, §17.1→§11.1 template). §20 finalization section added: fresh-Claude confusion audit (3 blocking items — all docs-only), missing-layer verdict (none), documentation ecosystem diagram (canonical Tier 0 Runtime → Tier 10 Archive stack + 5 side channels), knowledge lifecycle mapping (no new ledger — maps to existing surfaces), research lifecycle completeness (complete + Implementation Review as P2 gap), quick-start doc (no — §0 TL;DR suffices), graduation verdict (GRADUATED — diminishing returns reached), P0/P1/P2 debt sort consolidating three prior sessions, ratification recommendation READY-WITH-MINOR-FOLLOW-UP, migration checklist for S1279, Context-Kit boundary re-evaluation. Rigby SIGN cycle 3 (fresh pin `pa-30278fb65295e74c`, **High confidence**, zero factual errors): SIGN-with-edits where edits = the 3 P0 doc-pointer follow-up items I already flagged; NO architectural changes recommended. | **Highest-authority process doc in the library.** Playbook (§1.11) is one specialization of this OS. Reading order for a fresh Claude Code: CLAUDE.md → OS §0-§5 → §5 classification → Level B contract. §1.14 OS + §1.15 introspection register the process framework foundation. Ratification READY-WITH-MINOR-FOLLOW-UP: 3 docs-only P0 items (CLAUDE.md pointer, `OPEN_ARCS.md` creation, START-HERE additions) gate CANONICAL status. Once P0 lands (S1279 or equivalent), OS becomes CANONICAL and every future Claude session executes it. Index v11 updated per §10.1 (this row + §1.14 + §1.15 + §1.11 body cross-reference to §1.14). |

| **S1301** (2026-07-01) | `domains/memory/1301_memory_rag_retrieval_lanes_audit.md` (§1.16) | **First child audit under Group 1300 Memory (parent §1.13).** Category D RAG Retrieval Lanes exclusive scope. 20-section playbook §11.2 template. Playbook §13 6-parallel-Explore sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity). Parent-agent verifier-loop spot-checks folded direct file reads on the mechanism claims. Traces parent §6 provenance-filter finding (8 pre-filter → 7 excluded_missing_provenance + 1 excluded_mismatch → 0 returned) to root cause: HYP-1 (migration-incomplete) × HYP-4 (never-wired-into-ingestion). Load-bearing findings: (1) `search_docs` = LOCAL keyword lane (`core.rag.top_k` on `.rag/corpus.jsonl`); `kb_tool semantic_search` = PROD pgvector lane (`core.rag_integration.search_embeddings`) — verified at `td_handlers_ops.py:5502`; the two tools are NOT parallel implementations. (2) Provenance is EXTERNAL to chunks — computed at query time from `docs/_provenance.json` (git-history-derived by `build_docs_provenance`); index has 464 UNKNOWN / 2156 docs (21.5%) per `_meta.confidence_breakdown`; filter treats "path not in index" as `excluded_missing_provenance` by design per Rigby S1145 P2 spec (`td_handlers_ops.py:82-85` docstring). (3) Two provenance systems coexist without integration — row-level `DocumentEmbedding.source_type` + `ingested_via` (migration 0044, populated at ingestion) are NEVER READ by any retrieval path (grep-confirmed 0 hits in `rag_integration.py` / `rag.py` / `scoped_retrieval.py`). (4) Prod pgvector lane bypasses the provenance filter entirely — `_filter_chunks_by_originating_session` only called from `_handle_search_docs`. (5) Two-lane selector NEVER IMPLEMENTED — playbook §12 §3.13 research question resolved as negative. (6) PA turn enrichment does NOT auto-invoke RAG — tool-call-only (grep of `unified_pa_entrypoint.py` = 0 RAG imports). (7) Silent-failure surface confirmed system-wide-in-`core/` — filter counters live only in response payload, no log/metric/alert (grep of `excluded_missing_provenance|excluded_mismatch|pre_filter_count` = 2 files matched: handler + test). (8) Combined subsystem maturity WORKING (prod STABLE + local PARTIAL individually; combined verdict dropped from STABLE due to corpus-completeness gap that neither individual-lane verdict conveys). §19 downstream routing: S1302 owns row-level provenance semantics (persistence-architecture concern); S1304 owns E↔D ingestion→retrieval handoff; Group 1700 owns filter-drop telemetry. Rigby SIGN cycle 1 on fresh isolation pin `pa-a23736a833f646cf` (owner chris, ownership match confirmed) — verdict **SIGN-clean** after fold cycle. 4 must-fix folded (MF1 denominator citation, MF2 D3 grep evidence, MF3 MISSING scope hedging, MF4 silent-failure `core/`-tree scope note). 5 nice-to-have deferrable. Verifier_loop history preserved append-only per playbook §6. | **First Group 1300 child audit; first library exercise of playbook §11.2 20-section template + §13 6-parallel-Explore sweep + §15 fresh-isolation-pin Rigby SIGN discipline.** Confirms the audit contract works end-to-end from short-command open through SIGN-clean. Next Group 1300 child S1302 Memory Persistence Architecture (Categories A + B + C) inherits the row-level provenance semantics question surfaced here as first-order scope. Index v13 updated per §10.1 (this row + §1.16 row). |

| **S1302** (2026-07-01) | `domains/memory/1302_memory_persistence_architecture_audit.md` (§1.17) | **Second child audit under Group 1300 Memory. Combined-category scope: A (Semantic Knowledge) + B (Personal-Adaptive) + C (Agent Working) per parent §5 P2 slot renamed by Chris 2026-07-01 to "Memory Persistence Architecture" (durability + write/read paths + write authority frame, not just overlap surfacing).** Playbook §11.2 20-section template + §13 6-parallel-Explore sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity). Parent-agent verifier-loop spot-checks resolved Agent 1 vs Agent 2 conflict on `MemoryPromotionService` existence (Agent 2 correct: `core/services/memory_promotion_service.py:119, :197`); disambiguated `ConversationMemory` name collision (Django at `core/models/conversations/models.py:19` vs in-process at `core/conversation_memory.py:59`) and `AgentMemory` name collision (Django at `core/models_unified_system.py:10787` vs in-process at `core/services/agent_learning_service.py:111`). **Headline finding F1 — CONFIRMED DEAD CODE.** Parent §3 flagged `spider_context['pa_content_feedback']` consumer as UNKNOWN; whole-tree grep including `ai_core/` returned 1 producer at `core/agent_router.py:766` + 0 code consumers. 14 doc references describe an intended consumer that never became code. Escalates parent §3 UNKNOWN → confirmed dead code per playbook §14 evidence rules. Session 990 producer half wired; agent-side consumer half never implemented. Analogous to S1301 §14.3 D3 "two systems, no bridge" class. **F2 — orphan write path pattern INHERITED from S1301 §14.3 D3; narrowed across three Rigby SIGN cycles.** v1 claim: ~11 fields populated at write, never read. Rigby SIGN cycle 1 (fresh isolation pin `pa-1b9f0f5264484c6b`, owner chris, ownership match confirmed) verdict SIGN-with-edits — grep-verified active readers on 3 fields removed from orphan list: `AgentKnowledgeSource.source_spider_names` (read at `core/tasks.py:3098` + `core/tasks_agents.py:3202, 3240, 3241, 3272, 3471` + `core/views_spider_intelligence.py`); `AgentKnowledgeSource.first_discovered_at` (read at `core/tasks_content.py:1893` + `core/tasks_agents.py:3236, 3265, 3938, 3953, 3980, 3994, 4008, 4305, 4323, 4348` + `core/project_intelligence_consumer.py:155, :186`); `AgentKnowledgeSource.feedback_adjusted_confidence` (read via `effective_confidence` computed property at `core/models_unified_system.py:612-613, :625-626` + `Avg()` aggregation at `core/services/project_research_bridge.py:334`). Rigby SIGN cycle 2 verdict SIGN-with-edits — 4 more `AgentMemory` fields removed from orphan list: `.source_type` + `.source_id` + `.access_count` + `.last_accessed_at` all consumed by `core/views_memory_palace.py:60` (order by `-last_accessed_at`), `:86` (listing payload return), `:113-114` (access tracking write on detail view), and source_type/source_id join to AgentExecution in `get_memory_detail`; `record_access` at `core/models_unified_system.py:11000-11001` writes both fields. Methodology tightening: language changed from "0 consumers" to "no explicit-qualified references found on the model" per Rigby's epistemic hedge (unqualified `.field` references on variables bound to the model at runtime cannot be exhaustively excluded without AST-level tracing). Rigby SIGN cycle 3 verdict SIGN-clean — one non-blocking residual folded: `AgentMemory.poison_risk_score` + `.poison_risk_factors` reclassified from orphan → narrow-consumer-safety-filter (consumed at `core/services/memory_embedding_service.py:222` via `getattr` + `:261` via `queryset.exclude(poison_risk_score__gte=0.5)`). **Final F2 classification: 5 strict-orphan fields** (`AgentKnowledgeSource.feedback_positive/_negative`; `UserAgentLearning.context_metadata` + `.last_used`; `ConversationMemory.intent` Django model — Rigby cycle 3 grep re-verified all = 0 hits on the specific model) **+ 2 narrow-consumer-safety-filter fields** = 7 total, down from v1's ~11. **Other findings:** (a) F5 — `spider_data_bridge` (named for Cat A per narrative KNOWLEDGE_RAG_MEMORY.md) writes Cat B — parent-agent direct read of `core/learning_bridges/spider_data_bridge.py:240`: `UserAgentLearning.objects.get_or_create(...)`. docs_stale terminology drift. (b) F6 — `MemoryPromotionService` (categorized under Cat C by parent §3C) writes `UserMemoryContext` (user-scoped table) at `core/services/memory_promotion_service.py:303-318`, not `AgentMemory` directly. Category-assignment drift. (c) 14-day freshness window at `core/conversation_orchestrator.py:749` verbatim `freshness_cutoff = tz.now() - timedelta(days=14)` — Session 988 origin per :747-748 comment; hardcoded magic number; no env var/setting/config surface. (d) `AgentLearningService.save_memory` at `:462-483` writes via `redis_client.hset` at :476 with no DB backup; grep for `.expire()` = 0 hits; Redis-only durability confirmed. (e) `MemoryPromotionService` scoring criteria: regex-only deterministic (`_MILESTONE_PATTERNS` at :32-47 +3 max once, `_IDENTIFIER_PATTERNS` at :51-63 +2 per type cap +6 across 11 identifier types, `_WIRING_PATTERNS` at :67-73 +2 max once, `_SECRET_PATTERNS` at :77-86 -10 hard block); thresholds hardcoded at :234 (≥7 auto-save), :237 (5-6 pending log-only); not configurable. (f) T10 HIGH severity: no write authority gate on `AgentMemory.create_memory` at `core/models_unified_system.py:11004`; no user FK, no rate limiting; MemoryPromotionService auto-saves on every PA turn. Riskiest finding per Rigby vote. **Per-category maturity verdicts:** Cat A = PARTIAL (knowledge accumulation works but no versioning + opt-in embedding silent-missing failure mode + orphaned feedback_positive/_negative); Cat B = PARTIAL (Postgres side WORKING with active `learning_source` filter at `core/services/td_handlers_ops.py:5965, 5986, 6000`; Redis side PARTIAL with loss-on-worker-recycle); Cat C = EXPERIMENTAL (downgraded from WORKING due to F1 dead-code loop — auto-promotion pipeline runs but downstream feedback consumer is broken). **§19 downstream routing:** S1303 owns Conversational / Thread Memory Cat F (`ConversationSession` ↔ `ConversationMemory` boundary); S1304 owns Docs Corpus ↔ RAG Boundary (E ↔ D); S1399 canonical summary owns row-level orphan-write pattern classification + write-authority framework anchor recommendation + `MemoryPromotionService` Cat B vs Cat C reassignment resolution + `spider_data_bridge` naming reconciliation; Group 1700 Observability owns dead-code / producer-only detection surface (F1 highest-severity example). Design-preparation ADR for write authority framework anti-pattern: NOT this audit's job (playbook §14.5 forbids implementation-in-research). | **Second Group 1300 child audit; validates the audit contract's fold discipline across three SIGN cycles.** Rigby SIGN cycle 1 corrected F2 overstatement + verified F5 by parent-agent direct-read; cycle 2 corrected AgentMemory field misclassification via Memory Palace consumer evidence + methodology tightening ("no explicit-qualified references found" replaces "0 consumers"); cycle 3 folded final poison_risk_* reclassification to narrow-consumer-safety-filter. Overall Rigby confidence: **High.** Index v14 updated per §10.1 (this row + §1.17 row). |

| **S1304** (2026-07-01) | `domains/memory/1304_memory_docs_rag_boundary_audit.md` (§1.19) | **Fourth child audit under Group 1300 Memory. Categories E ↔ D Documentation Corpus ↔ RAG Boundary exclusive boundary lens per parent §5 P4 slot ("smaller scope; benefits from §3.14 audit landing first").** 20-section playbook §11.2 template + §13 6-parallel-Explore sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity). Parent-agent verifier-loop spot-checks caught a broad hypothesis overreach from S1301 §19 D3 BEFORE Rigby SIGN: S1301 §19 D3 broadly claimed both `DocumentEmbedding.source_type` + `ingested_via` are orphan-writes; direct file:line read at `content/embeddings.py:965-973` confirms `semantic_search_sync` applies `.filter(source_type__in=['internal', 'user_upload'])` at :971 and `.filter(source_type__in=['web', 'spider', 'api'])` at :973 as `source_filter` branch (owner-model-qualified consumer) + presentation read at :1007 (`getattr(embedding, 'source_type', 'unknown')`). Only `ingested_via` remains F1-CANDIDATE orphan — all 3 write-sites use fixed string constants (`'sync_docs'` at `sync_docs_index_to_documents.py:394` / `'backfill'` at `core/tasks_agents.py:4223/4290/4351` / `'unknown'` default at `content/embeddings.py:654/753`) with zero owner-model-qualified read consumers per grep + admin.py + serializers.py verification. F1-CANDIDATE status pending §19 R1 full-tree recheck per S1303 §14 F4-CANDIDATE discipline (dead-code claim requires owner-model-qualified consumer inventory, not keyword grep). **Load-bearing findings:** (1) Two RAG lanes confirmed with distinct provenance mechanisms — `search_docs` (LOCAL keyword) at `td_handlers_ops.py:5468` reads external `docs/_provenance.json` for `originating_session` filter via `_load_provenance_docs()` at `:78-93` (per-process `@lru_cache(maxsize=1)`); `kb_tool semantic_search` (PROD pgvector) reads row-level `source_type` via `semantic_search_sync` at `content/embeddings.py:965-973`. (2) `refresh_docs_corpus` beat task at `core/tasks.py:5803` scheduled daily at 04:00 Denver via sole `refresh-docs-corpus-daily` entry at `core/celery.py:495-499` runs `build_docs_index` (`:5900`) + `build_rag_corpus` (`:5901`) + `sync_docs_index_to_documents` (`:5902`) + fans out step 4 embed tasks — **does NOT include `build_docs_provenance`.** D6 HIGH: provenance rebuild is manual-only. (3) `lru_cache(1)` staleness at `td_handlers_ops.py:78-93` — no invalidation mechanism; workers serve stale filter results until process restart. Combined with D6, canonical E→D write-side/read-side sync drift. (4) 21.5% corpus-completeness gap (464 UNKNOWN / 2156 docs per `docs/_provenance.json._meta.confidence_breakdown`) — inherited from S1301 §14.2; root cause is docs predating the session-NNNN convention (introduced Session 1144) OR bulk commits lacking session attribution. Not a filter mechanism bug — provenance-index-completeness signal. (5) Cat F ↔ Cat D wiring: PA turn enrichment does NOT auto-invoke RAG (S1304 grep verifier confirmed 0 matches for `search_docs|kb_tool|semantic_search|search_embeddings` in `unified_pa_entrypoint.py`). Reframed as **§19 R5 design-decision** (NOT drift or wiring PR) — 3 signals tilt intentional-separation (design discipline in 8 non-RAG enrichment services, tool-call-only pattern with two first-class PA tools, thread-memory vs source-memory scope discipline, no event-driven turn-signal wiring), 3 signals tilt drift (no design comment, no feature flag guarding absence, asymmetry with `BaseAgent._get_relevant_knowledge_for_task`). Requires product/architecture verdict on operational cost, migration risk, future retrieval requirements. (6) Documentation Manager `AIEmployee` handle at `core/employees/jobs.py:187-395` (registered `:1336` as `docs_manager`, employee_handle=`rigby`, `mission_run_kind=docs_cascade`) explicitly owns cascade steps 1-4 per `daily_routine` (`:222-231`) + authority set (`:238-250`). **§18 refined:** four specific boundary-maintenance responsibilities (provenance rebuild cadence, cache invalidation strategy, filter counter observability, row-level `ingested_via` consumer strategy) have "no explicit named runtime owner" per bounded-language refinement (SIGN cycle 1 fold #2 softened "CRITICAL" → "HIGH"). (7) Two provenance systems reframed as **complementary, not duplicate** via S1302 §17.3 name-collision-as-methodology — external JSON encodes session origin (LOCAL keyword lane); row-level `source_type` encodes source-of-record enum (PROD pgvector lane); `ingested_via` was over-designed for a retrieval consumer that never materialized. Fold #4 adds "complementary today does not imply optimal" guardrail — unification vs explicit scoping is an open design decision routed to §19 R2. (8) `td_handlers_ops.py` = 6290 lines (GOD-SERVICE, exceeds playbook §13 3000-line threshold); `doc_claim_verification.py` = 3275 lines (GOD-SERVICE CANDIDATE, cohesive registry + lazy imports justify current size). **Per-component maturity verdicts:** ingestion cascade PARTIAL (operates daily on beat; step 4 async fan-out not gated by beat completion; hash-delta gating edge-case fragile); provenance filter WORKING (mechanism sound but 21.5% UNKNOWN input coverage + counters lack operator visibility + cache staleness gap); row-level provenance write path EXPERIMENTAL (`source_type` wired to `semantic_search_sync`; `ingested_via` F1-CANDIDATE pending §19 R1 full-tree recheck); E↔D boundary as a whole PARTIAL (functional but not mature; ownership undefined for boundary-maintenance responsibilities; provenance rebuild unscheduled; cache invalidation absent; observability response-only; cascade documentation unpublished). **§19 downstream routing:** R1 full-tree `ingested_via` F1-CANDIDATE verification per S1303 §14 discipline (HIGHEST priority follow-on); R2 provenance-system reconciliation design (unify or explicit scoping) → S1399 canonical summary + S1302 P2 arc handoff; R3 rebuild cadence + cache invalidation design (add to beat OR file-watcher OR Redis TTL) → Cat E docs-governance owner; R4 boundary ownership assignment (expand Documentation Manager authority OR create distinct boundary employee OR delegate observability to Group 1700) → S1399 canonical summary; R5 turn-context → RAG enrichment design decision (canonicalize separation vs implement enrichment) → design-preparation phase post-S1399; R6 publish `docs/topics/docs-ingestion-cascade.md` → Cat E docs-governance owner; R7 filter-drop telemetry (log emit + Prometheus counter + Grafana surface + threshold alert) → Group 1700 Observability arc; R8 S1301 follow-up classifier precedence bug (standalone bugfix, NOT blocking Group 1300 arc). Rigby SIGN cycle 1 on fresh isolation pin `pa-2614a91a920642fa` (owner chris, ownership match confirmed) — verdict SIGN-with-edits with 4 must-fix folds: (fold #1) D6 beat-schedule positive citation — added `core/celery.py:495-499` sole `refresh-docs-corpus-daily` entry with 4-line dict quote + `core/tasks.py:5900-5902` cascade call sites showing NO `build_docs_provenance` call, no bare "grep returned 0" as sole justification; (fold #2) §18 UNOWNED reframed with Documentation Manager JobContract positive evidence at `core/employees/jobs.py:187-395` + refined ownership matrix acknowledging cascade steps 1-4 ARE owned; four specific boundary-maintenance responsibilities remain "no explicit named runtime owner"; softened "CRITICAL" → "HIGH" per playbook §12 bounded-language rule; explicit bounded-language check paragraph; (fold #3) F4-CANDIDATE discipline reinforced on `ingested_via` — §9 D→E edge cell rewritten to hedge, §14 D7 explicit F4-CANDIDATE hedge added, no bare "never read" language remaining on `ingested_via`; (fold #4) §17 "complementary" reframe augmented with explicit "does not imply optimal" guardrail + unification-vs-scoping design-decision routing to §19 R2. Rigby-caught bonus: additional `source_type` consumer citation at `content/embeddings.py:904` (async-path SearchResult presentation) flagged as nice-to-have, not SIGN-blocking. Rigby SIGN cycle 2 verdict SIGN-clean — verification pass confirmed all 4 folds via direct code reads; no structural rewrite; ready for Chris commit-gate per playbook §16. **Load-bearing methodology inheritance:** F1-CANDIDATE discipline for `ingested_via` orphan claim inherits S1303 §14 F4-CANDIDATE methodology + S1302 §17.3 name-collision-as-boundary-methodology + S1301 §19 downstream routing invalidation pattern (partial invalidation via verifier-loop prevents sibling-audit hypothesis propagation before hardening into library-wide false consensus). | **Fourth Group 1300 child audit; first boundary-lens integration audit in the library.** Second child audit to reach SIGN-clean in 2 cycles (matching S1303 discipline; S1301 = 1, S1302 = 3). Sets the pattern for future boundary-focused audits: catch broad hypothesis overreach from sibling audits parent-side first (via direct file:line verification), so SIGN cycles focus on substantive additions instead of evidence corrections. Partial invalidation of S1301 §19 D3 demonstrates the verifier-loop pattern preventing sibling-audit hypothesis propagation. Index v16 updated per §10.1 (this row + §1.19 row). |

| **S1305** (2026-07-01) | `domains/memory/1305_memory_runtime_correctness_audit.md` (§1.20) | **Fifth (and final) child audit under Group 1300 Memory. Category H Runtime Memory Correctness NARROW scope per parent §5 P5 slot — Redis-loss on worker recycle + `@lru_cache(1)` staleness drift class only.** 20-section playbook §11.2 template + §13 6-parallel-Explore sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity). Parent-agent verifier-loop pre-SIGN corrections applied to 4 sub-agent claims BEFORE Rigby: (v-l-1) Agent 6 "CRITICAL" severity on `AgentLearningService` Redis-only durability DOWNGRADED to MEDIUM per Redis AOF context (`settings.py:944 REDIS_APPENDONLY=True` + `:945 REDIS_APPENDFSYNC='everysec'`) matching S1302 T3 sibling classification; (v-l-2) Agent 6 "13 `cache.set(timeout=None)` sites" corrected to 5 production `core/` runtime (excluded 7 test-only + 2 subprocess-timeout `_run_ffmpeg` non-cache-set calls); (v-l-3) Agent 6 "3 disjoint Redis DBs" corrected to 4 (missed Celery broker DB 2 + results DB 3 split); (v-l-4) Agent 1 vs Agent 2 conflict on `search_docs` cache location resolved (Agent 2 correct: `search_docs` itself has NO LRU; only `_load_provenance_docs` called from it has the LRU at `td_handlers_ops.py:78`). **Load-bearing findings:** (1) Exactly 4 `@lru_cache(maxsize=1)` sites in `core/services/` grep-verified 2026-07-01 — `_load_provenance_docs` at `td_handlers_ops.py:78` (S1304 D2 anchor); `_cached_primary_workspace_id` at `platform_config.py:89`; `_cached_primary_user_id` at `platform_config.py:133`; `_load_config` at `fleet_routing.py:64`. Only `platform_config` pair has explicit invalidation contract via `clear_config_cache()` at `:223`; other two rely on worker-restart discipline. §14 D7 S1305-new (LRU staleness class extension of S1304 D2). (2) 5 production `cache.set(..., timeout=None)` sites within scope after Rigby SIGN cycle 1 tightening — `core/tasks.py:5936` (docs corpus index hash), `core/memory_system.py:54, :55, :176` (index + embedding-index + embedding-data), `core/services/discord_bot.py:9723,9728` (Discord bot config, out of memory-scope). §3 excluded-from-count table enumerates 6 excluded categories (subprocess-timeouts, tests, mock fallbacks, archive) with reasons. §14 D10 S1305-new. (3) `AgentLearningService` within-process consistency gap **CONFIRMED via direct file:line read + Rigby SIGN cycle 1 reinforcement** — `get_user_memory` at `agent_learning_service.py:415` short-circuits to `_user_memories[key]` BEFORE Redis on hit; `save_memory` at `:476` writes Redis via `hset` but never touches the dict; grep for `self._user_memories.clear` / `del self._user_memories` = 0 hits on the save path. Distinct from S1302 T3 cross-process recycle-loss. §14 D4 S1305-new. (4) `MemorySystem` at `core/memory_system.py:54-55, :176` writes `timeout=None` creating index → data divergence risk under Redis LRU eviction (`REDIS_MAXMEMORY_POLICY='allkeys-lru'` at `settings.py:942`). Rigby SIGN cycle 1 grep confirmed `MemorySystem` IS active — instantiated at `ai_core/agents/intelligent_job_matcher.py:57 self.memory = MemorySystem()`. §14 D5 S1305-new. (5) 4-DB Redis topology (DB 1 Django cache at `settings.py:452 RedisCache + LOCATION=REDIS_URL`; DB 2 Celery broker at `:802`; DB 3 Celery results at `:803`; DB 5 `AgentLearningService` hardcoded at `agent_learning_service.py:145`). `django.core.cache.cache.clear()` operates on backend DB 1 only; `AgentLearningService` uses raw `redis.Redis(**self.redis_config)` at `:160` bypassing Django cache framework — DB 5 state invisible to `cache.clear()`. §14 D8 S1305-new. Also `docs/topics/infrastructure.md` says "3 DBs" — doc drift; actual is 4. §14 D9. (6) `search_docs` PA tool has NO dedicated LRU cache — only `_load_provenance_docs` called from it. Parent §3H bullet "search_docs `lru_cache(1)` per-process" is imprecise; cache is on the provenance loader, not `search_docs` itself. §15 T12. (7) `MemoryPromotionService` has NO runtime cache surface — Agent 2 verified pure DB I/O (0 hits for `@lru_cache`, `@cached_property`, module-level memoization). Closes parent §3H "MemoryPromotionService runtime cache UNKNOWN." (8) Cat H ↔ Cat F integration MISSING — grep for `@lru_cache` in `conversation_orchestrator.py` = 0 hits; 14-day freshness cutoff at `:749` is a Cat F correctness boundary, not a Cat H cache surface. **Per-surface maturity verdicts:** `EmbeddingService` STABLE (bounded 7-day TTL, deterministic contract); `platform_config` LRU pair WORKING (invalidation contract explicit via `clear_config_cache()`); `_load_provenance_docs` PARTIAL (works with worker-restart discipline; no automation); `AgentLearningService` PARTIAL (works when Redis healthy; degrades silently on cross-process race + within-process staleness); `MemorySystem` EXPERIMENTAL (unbounded index + no lifecycle; index → data divergence possible); `fleet_routing._load_config` PARTIAL (deploy-restart contract; test-only invalidation). Category H as a whole: **WORKING with drift.** **§19 downstream routing:** R1 `platform_config` LRU D6 F4-CANDIDATE verification per S1303 §14 discipline (owner-model-qualified consumer inventory for Django admin / raw ORM / mgmt-command mutation paths); R2 Cat H remediation design-preparation per surface per S1304 T2 option set (worker-restart trigger vs file-watcher vs Redis-queryable vs TTL) → post-S1399; R3 beat-schedule audit for cache-refresh cadence gaps beyond `build_docs_provenance` (extends S1304 D6 pattern); R4 Cat H ↔ Cat B integration lens (`AgentLearningService` Redis-only durability + TTL policy + DB writeback design decision — fixes T3 + T4 + T7 together); R5 worker-recycle instrumentation → **delegate to Group 1700 Observability**; R6 `IntelligentJobMatcher` production invocation audit (post-Rigby-cycle-1-reshape — routes T5 severity assessment); R7 full `@lru_cache` sweep across `core/`, `ai_core/`, `content/` (completes Cat H surface enumeration); R8 doc-drift fix on Redis DB count `docs/topics/infrastructure.md` 3 → 4. Rigby SIGN cycles 1 + 2 on fresh isolation pin `pa-56a527a2c5528508` (owner chris, ownership match confirmed) → verdict **SIGN-clean** after 3-must-fix fold (cycle 1) + verification pass (cycle 2). Cycle 1 folds: (F1) §3 `cache.set(timeout=None)` scope definition + excluded-from-count table added; (F2) §7.2 gap (a) reinforced with direct file:line evidence — `get_user_memory:415` short-circuit + `save_memory:476` Redis-only write + grep-for-invalidation = 0 hits; (F3) §14 D8 Redis DB isolation tightened with Django cache backend citation (`settings.py:452 BACKEND` + `LOCATION`) + raw redis client citation (`agent_learning_service.py:160`). Bonus fold: §19 R6 reshaped from "verify MemorySystem is used" (Rigby-answered: yes) to "verify IntelligentJobMatcher production invocation paths" — same effort, higher-leverage. Cycle 2 verification pass — Rigby SIGN-clean High confidence; one optional micro-tighten flagged (§3 excluded-row rendering) but NOT blocking. Pin retired at close per Chris commit-gate directive (`updated_count: 2, retired: true`). Verifier-loop history preserved append-only per playbook §6. | **Fifth (and final) Group 1300 child audit; closes the 5-child arc (S1301-S1305).** Third child audit to reach SIGN-clean in 2 cycles (matching S1303 + S1304; S1301 = 1, S1302 = 3). Also **first library audit to explicitly downgrade a sub-agent severity claim via sibling-inherited context** — Agent 6 "CRITICAL" AgentLearningService durability claim downgraded to MEDIUM by Redis AOF context (settings.py:944 REDIS_APPENDONLY=True) matching S1302 T3 sibling classification. Extends the verifier-loop pattern from hypothesis-correction (S1304 partial invalidation of S1301 §19 D3) to severity-correction (S1305 §14 D3 downgrade). Group 1300 arc now closable via S1399 canonical summary next session — S1305 provides Cat H input material for the cross-cutting synthesis. Index v17 updated per §10.1 (this row + §1.20 row). |

| **S1399** (2026-07-01) | `domains/memory/1399_memory_canonical_summary.md` (§1.21) | **Arc-closing xx99 canonical summary for Research Group 1300 Memory / Knowledge / Embeddings.** Consumes S1301-S1305 child audit outputs per playbook §11.3 11-section canonical-summary template + bounded-work rule (no §13 6-parallel-Explore sweep launched; no new file:line evidence produced; every claim cites source-audit §-anchor via SNNNN §NN.N notation; CANDIDATE claims preserved rather than resolved to CONFIRMED per S1303 §14 F4-CANDIDATE discipline). **Rigby SIGN cycle 1 on fresh isolation pin `pa-4fc3329d0db6484f`** (owner chris, ownership match confirmed) → verdict **SIGN-clean** at **High confidence, 0 must-fix**, 1 optional nice-to-have (docs↔code naming/category drift micro-pattern acknowledged in §4.5 addendum as adjacent evidence rather than promoted to formal F5 — preserves the 4-pattern set named at S1305 close per parent §5 P6 rationale; Rigby explicitly said "not required if you want to keep exactly four"). All 4 pressure-test questions PASS: Q10 child contradictions resolved; Q11 anchor-update recommendations complete; Q12 cross-cutting patterns not missed; Q13 follow-on queue rankings defensible. **Load-bearing content:** (§3) Consolidated Cat A-H domain shape matrix + Redis 4-DB topology table + two-provenance-systems complementary-not-duplicate table + two-RAG-lanes-no-runtime-selector diagram + 4 `@lru_cache(1)` sites enumeration + 8-row load-bearing consequence table. (§4) **Four cross-cutting patterns named:** F1 provenance-filter drift class (S1301 §14.2 21.5% coverage gap + S1304 §14 D2/D6 lru staleness + cadence unscheduled + S1305 §14 D1 LRU class extension); F2 row-level orphan-write pattern (S1301 §14.3 D3 hypothesis + S1302 §14.3 F2 narrowed 11→7 fields across 3 SIGN cycles + S1304 §14 D3 partial invalidation of D3); F3 Redis-only durability + `@lru_cache` staleness pattern (S1302 §14 F4/T3/T4 + S1304 §14 D2 + S1305 §14 D3/D4/D5/D8 + Cat H 4-DB isolation); F4 F1/F4-CANDIDATE + severity-correction discipline as inheritance methodology (S1303 §14 F4-CANDIDATE + S1304 §14 D7 + S1305 §14 D6 F4-CANDIDATE + S1305 §14 D3 severity-correction extension). (§5) **Five contradictions resolved:** (5.1) S1304 §14 D3 partial-invalidates S1301 §19 D3 broad `source_type` orphan hypothesis via direct file:line at `content/embeddings.py:965-973`; (5.2) S1304 §17 complementary reframe of S1302 §17.3 duplicate provenance systems framing (external JSON = session origin LOCAL lane; row-level source_type = source-of-record enum PROD lane); (5.3) Agent 6 CRITICAL AgentLearningService durability claim DOWNGRADED to MEDIUM via Redis AOF sibling context (`settings.py:944 REDIS_APPENDONLY=True`) matching S1302 T3 classification; (5.4) Agent 6 "13 cache.set(timeout=None)" tightened to 5 production in `core/` runtime scope with excluded-from-count enumeration; (5.5) parent §3H bullet "search_docs `lru_cache(1)`" precision fix — cache is on `_load_provenance_docs` called from `search_docs`, not `search_docs` itself. (§7) **Anchor-update recommendations:** (7.2.1) `platform_architecture_inventory.md` §3.13 subdivision into Cat A/B/C sub-rows per S1302 findings; (7.2.2) §3.14 lane consolidation as explicit two-lane statement per S1301 findings; (7.2.3) new §3.N row for Cat F Conversational/Thread Memory (first-inventory landing per S1303 §4 + §7); (7.2.4) new §3.N or §5.N row for Cat H Runtime Memory Correctness (first-inventory landing per S1305 §14 D1-D10); (7.3) ARCHITECTURE_INDEX v17 → v18 bump plan; (7.4.1) `docs/topics/infrastructure.md` Redis DB count 3 → 4 fix per S1305 §14 D9; (7.4.2) `KNOWLEDGE_RAG_MEMORY.md` 4 targeted edits (F1 pa_content_feedback dead-code note, two-lane split explicit reference, LRU precision fix on `_load_provenance_docs`, pointer to S1399); (7.4.4) NEW `docs/topics/docs-ingestion-cascade.md` publish per S1304 §19 R6. NO direct edits to `PLATFORM_INVENTORY.md` per CLAUDE.md context-kit rule (runtime anchor, regenerable via `generate_platform_inventory`). (§8) **21-item follow-on queue ranked by uncertainty × risk × unblocked flows.** Top 5: (1) S1304 §19 R1 `ingested_via` full-tree recheck (F1-CANDIDATE hardening — deprecation hazard); (2) S1303 §19 R1.a/b/c `ChatConversation.context_used` + `.agent_results` owner-model-qualified inventory + runtime-vs-analytics-vs-UI classification + canonical-source-of-truth resolution; (3) S1305 §19 R1 `platform_config` LRU F4-CANDIDATE mutation-path audit; (4) S1305 §19 R6 `IntelligentJobMatcher` production invocation audit (routes T5 MemorySystem severity assessment); (5) S1302 §15 T10 write-authority framework design-preparation ADR (highest-severity debt in entire arc — no auth gate on `AgentMemory.create_memory:11004`). Design-preparation phase items post-S1399: Cat H remediation per surface (S1305 §19 R2); Cat H ↔ Cat B integration lens (S1305 §19 R4 — fixes T3+T4+T7 together); provenance-system reconciliation unify-vs-scoping (S1304 §19 R2); turn-context → RAG enrichment intentional-vs-drift decision (S1304 §19 R5). (§9) **Delegated arcs cross-linked:** Employee OS 1200s arc owns Cat G Mission Memory (parent §3G Chris-locked D2 2026-07-01); Group 1700 Observability owns 4 aggregated items (Cat D filter-drop telemetry S1301 R2 + Cat E↔D filter-drop S1304 R7 + dead-code / producer-only detection S1302 + EventBus adoption for Cat F S1303 R2 + worker-recycle instrumentation for Cat H S1305 R5); post-S1399 design-preparation phase owns 4 ADR/design-preparation docs; standalone bugfix follow-ups filed (S1303 R8 broken import + field mismatch, S1305 R8 doc-drift, S1304 R8 classifier bug). (§10) **Change log:** Session-by-session ledger of Rigby SIGN cycle counts (S1301 = 1; S1303/S1304/S1305 = 2; S1302 = 3; S1399 = 1); arc pin continuity `pa-aa54193f240f4846` across S1300 → S1399 (retires on Chris merge); fresh SIGN isolation pins per session enumerated with retirement schedule. **Load-bearing methodology outputs of the arc:** (a) F1/F4-CANDIDATE discipline; (b) sibling-inheritance hypothesis-correction; (c) severity-correction via sibling context. All three now qualify for playbook v3 additions per §20 two-triggers rule (each used across S1303 + S1304 + S1305). | **First formal xx99 canonical summary in the library** (S1268-S1275 arc predated the xx99 convention per playbook §22 note). Consumes prior child outputs — no §13 6-parallel-Explore sweep, no new file:line evidence, no CANDIDATE → CONFIRMED resolutions. Every claim cites source-audit §-anchor. Chris's short command `start research group 1399` proved the reduced-prompt target rhythm from playbook §11 works for arc closure. **Group 1300 arc closed** per playbook §17 graduation criteria — all 5 child audits + canonical summary shipped, SIGN-clean, committed to `main` (S1399 pending Chris commit-gate). Arc pin retires on merge. Group 1400 Revenue next per playbook §22 queue, pending Chris directive. Index v18 updated per §10.1 (this row + §1.21 row). |

| **S1303** (2026-07-01) | `domains/memory/1303_memory_conversational_thread_memory_audit.md` (§1.18) | **Third child audit under Group 1300 Memory. Category F Conversational / Thread Memory exclusive scope. First-inventory landing — no `platform_architecture_inventory.md` §3.N row existed for Cat F at audit open.** 20-section playbook §11.2 template + §13 6-parallel-Explore sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity). Parent-agent verifier-loop spot-checks caught two Agent-6 overreaches BEFORE Rigby SIGN: F3 "would fail at import time" → verified content_writer_agent.py:74-80 try/except guard = SOFT FAIL at import; F4 "confirmed dead code, 0 reads" → CANDIDATE per memory rule feedback_verify_before_deleting_dead_code.md (keyword-grep insufficient without owner-model qualification). Consequence: audit shipped to Rigby with the two most-load-bearing evidence claims already downgraded, so SIGN cycles focused on substantive-edge additions instead of evidence corrections. **Load-bearing findings:** (1) `ChatConversation` at `core/models/conversations/models.py:59-187` is the Cat F row-per-exchange table; `conversation_id` CharField at line 76 stores the `pa-<uuid.hex[:16]>` pin (mint format at `td_handlers_core.py:3885`); `session_active` BooleanField at line 139-143 is the retire marker. (2) Turn-history reinject at `unified_pa_entrypoint.py:7277-7343` loads last 10 rows scoped to `conversation_id` (7300-7302) with 8000-char truncation (7327, post-S1085), tool-call metadata reinjected (7331-7336), fail-open on DB error (7342). (3) `session_tool.retire` at `td_handlers_core.py:4011-4072` confirmed present + working — memory rule `feedback_session_tool_retire_works.md` stands; requires `force=True` if retiring currently-bound thread (line 4035-4050); returns `{retired: True, updated_count}` (line 4061). (4) S1212 deliverable 777d9cd8 stale-thread waste (~$3.60/day) CONFIRMED RECONCILED via S1248 matched-pair fix — retire handler flips `session_active=False`; dispatcher gate at `conversation_action_dispatcher.py:288-316` blocks; enforcement is best-effort / fail-open under DB errors (317-323 try/except envelope) — availability > correctness by design (Rigby SIGN cycle 1 riskiest-finding call). (5) F3 wrong-model + wrong-field at `content_writer_agent.py:76` (imports ConversationMemory from wrong module) + `:370` (filters `memory_type__in=['success','insight','learning']` but Django `ConversationMemory` at `models/conversations/models.py:19-31` has NO `memory_type` field — that field lives on `UserMemoryContext` at `:253`); D1 debt widened to "wrong model + wrong field" — import fix alone shifts crash from import-time to query-time FieldError. (6) F4 candidate for `ChatConversation.context_used` + `.agent_results` — Rigby SIGN cycle 1 confirmed Agent-6's keyword grep catches unrelated variables (e.g., `tasks_agents.py:1262` `agent_results = phase_data.get('results', {})` = local dict in different scope); §19 R1 split into R1.a owner-model-qualified consumer inventory / R1.b runtime vs analytics vs UI classification / R1.c canonical source-of-truth (first-class fields vs `metadata` dict) resolution. (7) Cat F ↔ Cat D wiring reframed as **OBSERVED GAP + owner confirmation required** (no verified turn-context → RAG query enrichment; could be intentional separation — user-scoped vs source-scoped — or missing integration); delegated to S1304 E ↔ D boundary. (8) F7 no Cat F event stream on EventBus (0 `CONVERSATION_*` streams in `event_bus.py:21-31`) reframed as gap/partial, delegated to Group 1700 Observability. (9) F8 pin rotation policy lives ONLY in `tools/pa_local.sh` header comments (policy-in-tooling anti-pattern). (10) F9 no auto-cleanup for retired rows (no Celery task, no management command, no TTL). (11) F10 Discord unlinked-user linkage-completion signal MISSING. **Maturity verdict (post-SIGN cycle 1 bounded):** WORKING (bounded) — interactive web PA sessions with DB-backed turn reinjection are stable; PARTIAL — lifecycle hygiene, analytics completeness, and hard policy enforcement (fail-open under exceptions). Rigby SIGN cycles 1 + 2 on fresh isolation pin `pa-23a38300dd84bae2` (owner chris, ownership match confirmed) → verdict **SIGN-clean** after 12-edit fold (E1-E12) + 1-cycle verification pass. Cycle 1 folded: E1 maturity bounding, E2/E3 F3+D1 wrong-model+wrong-field widen, E4 F4 CANDIDATE rewrite, E5 R1.a/b/c split, E6 Cat F ↔ Cat D reframe, E7 Flow E fail-open nuance, E8 retire idempotency clause, E9+E10 metadata contract Exec Summary mention + new §20.9 subsection, E11 F7 gap-not-defect reframe, E12 new §20.10 draft→active gating checklist. Cycle 2 verification pass — Rigby re-read `content_writer_agent.py:330-450` + `models/conversations/models.py:1-31` and confirmed E3/E4/E5 held; no structural rewrite; SIGN-clean. **§19 downstream routing:** R1.a-c (F4 verification) as highest-priority follow-on; R2 Cat F ↔ EventBus adoption → Group 1700 Observability; R3 turn-context → RAG enrichment → S1304 (Cat E ↔ D boundary); R4 retention lifecycle for retired rows; R5 land first-inventory §3.N row via S1399 canonical summary; R6 formalize session identity mint contract (§17 duplicate mechanism — `create_fresh` `pa-<hex>` vs `get_or_create_session` `uuid4()`); R7 doc-in-tooling reconciliation (F8); R8 D1 broken import + field mismatch runtime fix. Verifier_loop history preserved append-only per playbook §6. New §20.9 "Reinjection Metadata Contract" documents 4 expected metadata keys with producer/consumer citations to prevent F4-style false dead-code claims by distinguishing model fields from metadata dict keys. New §20.10 explicit `status: draft` → `status: active` gating checklist. | **Third Group 1300 child audit; first-inventory landing in the library.** Only child audit to reach SIGN-clean in 2 cycles (S1301 = 1, S1302 = 3). Verifier-loop spot-checks caught Agent-6's two overreaches before Rigby ever saw them — sets the pattern for future audits: catch evidence overreach parent-side first so SIGN cycles focus on substantive additions, not corrections. F4 CANDIDATE discipline extends S1302's dead-code methodology by adding the owner-model qualification rule — future audits applying this pattern must not accept keyword-grep evidence for dead-code claims. Index v15 updated per §10.1 (this row + §1.18 row). |

| **S1400** (2026-07-01) | `domains/revenue/1400_revenue_domain_scoping.md` (§1.22) | **Arc-opening parent scoping doc for Research Group 1400 Revenue / Outreach / Engagement.** First application of Chris's Phase 0 F.i/F.ii/F.iii methodology (Domain Definition / Existing Knowledge Inventory / Success Criteria) at §10/§11/§12 — proposed as playbook v3 §11.1 template addition at parent §9.5. **9 Chris-locked decisions D21 + D23-D29 across three "agree all" ratification rounds 2026-07-01:** D21 (short-command launch); D23 (parent-with-children); D24 (child mission sequence A→B→C→D→E→F→xx99); D25 (F.i Category F Income/Jobs lane child audit as S1406, 9-file intelligence/ adjacency + FreelanceOpportunity + resume/matcher/pipeline surface); D26 (Ops Autopilot revenue-facing modules IN, cross-cutting primitives OUT); D27 (§15 stage table SIGN routing — Light on parent, Full on each child, Q10-Q13 canonical on xx99); D28 (Opportunity → Initiative wiring ownership assigned to Child E per Rigby Must-fix #2); D29 (Yes-two-triggers — Group 1400 pilots Phase 0 methodology; playbook v3 §11.1 promotes at Group 1500 close if second application unchanged per S1399 two-triggers threshold). **Rigby Light SIGN cycles 1 + 2 both SIGN-clean** — cycle 1 Medium confidence 0 must-fix after fold (Must-fix #1 downgraded to §Appendix fold-note; Must-fix #2 escalated to D28 lock); cycle 2 Medium-High confidence 0 must-fix (nice-to-haves #2 + #3 folded, #1 skipped as low-value). Rigby spot-verified 2 of 15 inherited-finding citations at file:line — S1274 §2.4 lines 290-294 + §14 finding #36 at line 1499 — both correct. Load-bearing methodology outputs: **F.i-F.iii 3-step framework** (5+4+4 questions + 1 group-specific artifact); **Revenue Lifecycle Traceability Table** as S1499 F.iii "done" artifact (Rigby cycle 2 addition — 8 stages minimum + 6 columns per stage + ≥3 verified writer/reader paths + F1/F2/F3/F4 diagnostic-lens verdicts + row example template at §12.5 to prevent S1499 bikeshedding). Frame outputs: 17 revenue-related Django models enumerated at §2.4 with file:line grep-verified citations (10 Opportunity variants + Outreach + 4 engagement + Meeting + ClosePack + FreelanceOpportunity across 8 files); 10+ services + 3 revenue-related agents + 9-file Income/Jobs adjacency (Chris-locked as Category F child audit); 15 inherited findings enumerated at §11.4 (S1273 §3.32 + §4.9 + S1274 §2.4 + §3.7 + §5.10 + §9.6 + §14 finding #36 + S1399 F1-F4 methodology); 7 overlap points documented at §10.4 with existing arcs. **Reframe-under-directive discipline** established: when Chris redirects a decision framing mid-conversation (D25 → Phase 0 methodology), route interpretation through Rigby to pressure-test, execute the reframe explicitly with default lean, surface the reframed decision in one card for Chris ratification. New arc pin `pa-34d43795e1b24bd3` minted; old Group 1300 arc pin `pa-aa54193f240f4846` retired via `session_tool.retire force=true` (`updated_count: 29, retired: true, previously_active: true, is_current_bound: false`). §8 timeline S1400 row added. | **First arc under Chris's Phase 0 methodology; first arc where the parent scoping doc explicitly proposes a playbook v3 addition.** Group 1400 Revenue is trigger #1 for the two-triggers threshold; playbook v3 §11.1 template addition promotes at Group 1500 close if second application unchanged. Sets the pattern for future arc opens: parent scoping doc must answer 13 explicit questions (5 F.i + 4 F.ii + 4 F.iii) + name a group-specific "done" artifact at F.iii before any child audit launches. Index v20 first-half updated per §10.1 (this row + §1.22 row). |

| **S1401** (2026-07-01) | `domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` (§1.23) | **First child audit under Group 1400 Revenue (parent §1.22).** Category A Opportunity Discovery + Scoring exclusive scope per parent §10.2 evidence-surface table. 20-section playbook §11.2 template + §13 6-parallel-Explore sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity). **Parent-Claude verifier-loop pre-SIGN corrections applied to 5 sub-agent claims BEFORE Rigby:** (v-l-1) Agent 3 "score_opportunities_from_spider_data NOT SCHEDULED" downgraded to UNKNOWN — WIREMAP.md:170 + SESSION_872_COMPLETE.md:147 + SESSION_223_OPPORTUNITY_ENGINE.md:124 all document hourly beat; PeriodicTask row existence unverifiable from source tree; (v-l-2) Agent 6 "OpportunityPipelineOrchestrator ↔ OpportunityExecutionPipeline duplication candidate" resolved as COMPLEMENTARY via Agent 2 direct read (Orchestrator = transform Dict→Dict 5-stage agent routing 1848 LOC; ExecutionPipeline = materialize Opportunity instance → PartnershipProject + CustomWorkflow 541 LOC; different signatures, different downstream side effects); (v-l-3) Agent 3 EventBus publisher line ":282, :480" clarified to primary invocation at `scoring_dispatcher.py:41` (line 41 is direct call; :282, :480 are S1274 §6.2 higher-level caller lines); (v-l-4) NEW LOAD-BEARING FINDING surfaced from direct read of `consumers_base.py:2540` — `OpportunityScannerConsumer` reads from `intelligence.realtime_engine.intelligence_engine.get_current_opportunities()` in-memory realtime source, NOT `Opportunity.objects.filter(...)` persistent model — dual opportunity representation drift. (v-l-5) NEW debt finding surfaced from direct grep of `core/settings.py` — `score_opportunities_from_spider_data` defined TWICE in `task_routes` at line 1277 (`long_running`) and line 1484 (`content`); later wins → effective queue `content` (drift-prone silent config bug). **Rigby SIGN cycles 1 + 2 on fresh isolation pin `pa-16d8b24d30e7a7d8`** (owner chris, ownership match confirmed) → verdict **SIGN-with-edits cycle 1** (High confidence, 2 must-fix + 2 nice-to-have) → **SIGN-clean cycle 2** (High confidence, all 4 folds accepted). Rigby cycle 1 independently verified all 4 primary spot-check citations via `repo_tool.search` + `repo_tool.read_file`: sports lane at `sports_opportunity_generator.py:83` CONFIRMED; `intelligence_engine.get_current_opportunities()` **broadened finding from 1 to 5 consumer sites** in `consumers_base.py` (lines 1696, 1730, 2541, 2557, 2597); Celery duplicate at `settings.py:1277` + `:1484` CONFIRMED; OPPORTUNITY_SCORED registry `event_bus.py:25` + `:581` + `event_handlers.py:536` CONFIRMED. Cycle 1 folds: (M1) sports lane wording — clarify "separate lane" vs S1274 MISSING so readers don't misread as "integration solved" (S1274 MISSING remains ACCURATE for mainline); (M2) §10.1 EventBus overreach — added handler registry citation `event_handlers.py:48` + payload composition `event_bus.py:581`; corrected handler action from "routes confidence 50-85% → HITL VALIDATION_REQUIRED event" to DETECTS + LOGS only per `event_handlers.py:186-188` inline comment ("HITL service will have already created the validation request"); downgraded `scoring_workers` + `analytics_workers` group claims from S1274 §6.2 to CANDIDATE (not re-verified this session); only `create_validation_worker` at `event_handlers.py:521+` region verified this session; (NH #3) §15 T5 operational consequence — added detail on why `content` vs `long_running` queue mismatch matters (different concurrency + memory profile + workload assumptions per settings.py:1268-1273 comments; 100-item ML scoring pass under content semantics may cause latency regression); (NH #4) §19 R1 + R4 collapsed into single umbrella R1 "Dual-representation + provenance contract" with prerequisite sub-task R1.0 = identify origin/lifecycle of `intelligence_engine.get_current_opportunities()`. Subsequent R-numbers shifted -1; added new R8 for T5 Celery route cleanup (Rigby "important-but-contained"). Cycle 2 Rigby verdict verbatim: "SIGN-clean (cycle 2 unnecessary; ship to Chris commit-gate). No remaining blockers based on your fold summary." Pin retired at S1401 close per playbook §15. **Load-bearing findings:** (1) sports lane resolved as SEPARATE LANE (writes `OpportunityTracking`, not mainline `Opportunity`); (2) NEW dual opportunity representation drift (5 consumer sites); (3) F1 provenance-filter drift CANDIDATE HIGH; (4) F3 Redis-only durability CANDIDATE HIGH; (5) F2 orphan-write cluster CANDIDATE HIGH on 10-variant + partnership_* fields; (6) Orchestrator vs ExecutionPipeline COMPLEMENTARY (not overlap); (7) NEW debt T5 Celery route duplicate; (8) ownership gap CONFIRMED (deferred to Child E per D28); (9) maturity WORKING (S1273 baseline preserved); (10) research coverage LIGHT (matches parent §11.3). Parent §12.1 Category A F.iii questions all 6 answered (§20.7 checklist). §19 follow-on queue 8 items ranked; R1 umbrella + R2 scoring rate telemetry + R3 producer inventory completion → Category F S1406 + R4-R7 immediate Rigby probes + R8 T5 cleanup. All 15 inherited findings from S1273 + S1274 + S1399 cited, not rediscovered (§20.8). All 28 canonical questions answered (§20.6). S1273 §10.3 UNKNOWN #1 Opportunity model location RESOLVED at `core/models_unified_system.py:1201`. Verifier-loop history preserved append-only per playbook §6. §8 timeline S1401 row added. | **First Group 1400 child audit; validates parent-Claude verifier-loop discipline BEFORE Rigby.** First library audit where a Rigby SIGN cycle 1 grep BROADENED a NEW drift finding (dual opportunity representation) from 1 consumer site to 5 — changing follow-on from "single-consumer local bug" to "arc-wide contract question." Also first library audit where parent-Claude verifier-loop overrode a sub-agent's duplication flag via a competing sub-agent's direct code read (Agent 2 vs Agent 6 on Orchestrator ↔ ExecutionPipeline). Sports lane verdict definitively resolves parent §12.1 Q6 (SEPARATE LANE — S1274 MISSING remains accurate for mainline; refinement is wording). Sets pattern for Group 1400 remaining children: parent-Claude verifier-loop catches sub-agent overreach parent-side first so Rigby SIGN cycles focus on substantive edges. Index v20 second-half updated per §10.1 (this row + §1.23 row). |

| **S1402** (2026-07-01) | `domains/revenue/1402_revenue_outreach_composition_delivery_audit.md` (§1.24) | **Second child audit under Group 1400 Revenue (parent §1.22).** Category B Outreach Composition + Delivery exclusive scope per parent §10.2 evidence-surface table. 20-section playbook §11.2 template + §13 6-parallel-Explore sweep on 6 Category B evidence surfaces (OutreachDraft model + OpportunityDraftGenerator composition path + OutreachSequencer scheduling + outbound-channel resolution + Outreach → Engagement seam + Category B docs + prior research + drift/debt/ownership/maturity classification). **Parent-Claude verifier-loop pre-SIGN corrections applied to 2 sub-agent claims BEFORE Rigby:** (v-l-1) Agent 6 named "OutreachSequencer.evaluate() handles touches 2-4 with hardcoded text"; parent-Claude direct read of `revenue.py:812-829` ELEVATED the finding: the hardcoded text is the literal string `"Draft follow-up message needed."` AND the `.objects.create(...)` call omits `opportunity=parent.opportunity` → live F2 orphan-write pattern for every follow-up row created. (v-l-2) Agent 4 named "no outbound channel wired"; parent-Claude direct read of `models_outreach.py:10` OutreachDraft docstring reframed as *docstring-vs-runtime lifecycle divergence*: the model docstring declares five states (`draft → approved → sent → replied/expired`) but the runtime state machine only implements three (`draft → {approved, rejected}` + `approved → expired`). Same evidence, sharper claim. **Rigby SIGN cycles 1 + 2 on fresh isolation pin `pa-4a0a28edcb7a45ec`** → verdict **SIGN-with-edits cycle 1** (High confidence, 2 must-fix + 3 nice-to-have; storage truncated at Rigby's tool layer mid-Must-fix-#2) → **SIGN-clean cycle 2** (High confidence, 5 Q-answer folds applied + 3 nice-to-haves recorded). **Rigby ops probe mid-Cycle 1 CONFIRMED D.B7 dead-code finding** — `celery_task_history` 30d filter=outreach = 7 events all `generate_outreach_drafts_daily`; `PeriodicTask.filter(icontains='outreach')` = single row `generate-outreach-drafts-daily`; parent-Claude direct read of `core/services/td_handlers_ops.py:2699-2755` = zero PA tool action wraps `.evaluate` (only get_inbox/approve_draft/reject_draft/get_metrics_report exposed); repo-wide grep for `sequencer.evaluate`/`OutreachSequencer().evaluate` = 0 hits. **F.B4 CONFIRMED: OutreachSequencer's declared 4-touch cadence has no runtime realization — only Touch 1 fires; Touches 2–4 are dead code.** **Load-bearing findings (4, ranked by runtime severity):** (F.B1) delivery path missing CONFIRMED HIGH — grep-negative at HEAD `beda00e5` across mainline for send patterns + provider SDKs + EMAIL_BACKEND; approved drafts accumulate at `status='approved'` until 30d expiry; **S1274 §2.4 line 293 CONFIRMED and REFINED to "entire outbound channel missing, not just Inbox"** (recommended anchor-update IMMEDIATELY at S1274 per Rigby cycle 2 Q7); (F.B3) engagement feedback loop missing CONFIRMED HIGH — `EngagementEvent.outreach_draft` FK schema at `core/models_engagement.py:55-59` present, zero writer sites; Category C S1403 inherits the entire seam build-out; (F.B4) cadence declared but not realized at runtime — CONFIRMED via D.B7 probe (evidence bundle above); (F.B2) follow-up composition writer-site CONFIRMED F2 orphan-write + literal-stub pattern at `revenue.py:812-829` (code HIGH, runtime blast radius ZERO due to F.B4 dead code); CANDIDATE at repo-wide scope. **Inherited-finding resolutions:** S1273 §10.3 UNKNOWN #1 RESOLVED as single-shot LLM only (`outreach_generation.py:340-370`; no Content Deliberation, no reviewer chain; uses `get_openai_client()` factory + `gpt-5-mini` + `max_completion_tokens=4000` + `response_format='json_object'`); S1273 §10.3 UNKNOWN #2 + S1274 §2.4 line 293 RESOLVED to "entire outbound channel missing"; S1401 §14 D6 dual-representation drift RULED OUT for Category B (reads persistent `Opportunity.objects.filter(...)` only); F1 provenance-filter drift lens CANDIDATE extends to Category B reader surface; F3 Redis-only durability lens CLEAN for Category B. Cycle 2 fold outcomes: (Q3) D.B1 docstring-vs-runtime severity downgraded HIGH → MEDIUM per Rigby ("elevates to HIGH only if UI/ops relies on 5-state for compliance"); (Q5) R.B3 F1 reader-side filter narrowed from Group-1400-wide to Category-B-scoped; (Q6) T.B8 dedicated outreach queue documented NOW pre-Employee-OS (not deferred); (Q7) D.B3 anchor-update IMMEDIATELY at S1274 (not deferred to S1499 xx99); (Q9) R.B7 send-gap fence test bundled with R.B1 (not immediate). Cycle 2 3 nice-to-haves recorded for post-arc pickup: (NH-1) add provenance fields to OutreachDraft; (NH-2) rename UI/API "outreach delivery" → "outreach drafts" + add "no outbound channel implemented" banner; (NH-3) daily approved-drafts-older-than-X-days integrity report. Ownership gap CONFIRMED for Category B (deferred to Child E per D28). §19 follow-on queue 7 items ranked; R.B1 umbrella "outreach delivery subsystem design ADR" (highest priority); R.B2 follow-up composition subsystem; R.B3 F1 reader-side filter Category-B-scoped; R.B4 evaluate cadence probe RESOLVED via SIGN cycle 1; R.B5 engagement ingestion path Category C S1403 owns; R.B6 offer-configuration debt; R.B7 send-gap fence test bundled with R.B1. All 28 canonical questions answered; parent §12.1 Category B F.iii questions all 3 answered. Verifier-loop history preserved append-only per playbook §6. §8 timeline S1402 row added. | **Second Group 1400 child audit; first library audit to CONFIRM a missing-subsystem finding at HIGH runtime severity with complete negative-grep evidence.** Also first library audit where a Rigby ops probe (`celery_task_history` + `PeriodicTask` ORM) + parent-Claude direct read jointly CONFIRMED a dead-code finding (F.B4 / D.B7 / T.B5) MID-SIGN-cycle-1 — extending S1401 verifier-loop methodology from "hypothesis correction" to "runtime-liveness confirmation via ops telemetry." Also first library audit where SIGN cycle 1 storage got truncated at Rigby's tool layer; parent-Claude reconstructed the fold pass from (a) verbatim Must-fix #1 content, (b) inferred Must-fix #2 direction (F.B1 CONFIRMED HIGH not CANDIDATE HIGH — grep-negative evidence complete), (c) D.B7 dead-code confirmation via ops probe + direct read. Cycle 2 SIGN-clean confirmed the inferred fold direction (Q3 D.B1 severity downgrade HIGH → MEDIUM was the only correction; Must-fix #2 inference verified). Sets pattern for future SIGN-storage-truncation recovery: reconstruct via combining verbatim excerpt + evidence-based inference + independent probe/read verification. Load-bearing story change: Category C S1403 inherits F.B3 as its central deliverable (not just a seam-verify) because there is no existing Engagement ingestion wiring to extend. Isolation pin `pa-4a0a28edcb7a45ec` retires post-PR-merge per playbook §15. Index v21 updated per §10.1 (this row + §1.24 row + frontmatter v21 preamble). |

| **S1403** (2026-07-01) | `domains/revenue/1403_revenue_engagement_inbound_audit.md` (§1.25) | **Third child audit under Group 1400 Revenue (parent §1.22).** Category C Engagement Inbound exclusive scope per parent §3 Cat C evidence surface + §12.1 Category C F.iii questions. 20-section playbook §11.2 template + §13 6-parallel-Explore sweep on 6 Category C evidence surfaces (4 engagement models canonicity + EngagementEngine read/write graph + EngagementAutonomyEngine gating + F.B3 ingestion path design + EngagementMetrics aggregation direction + Category C docs+prior research+drift/debt/ownership/maturity). **Parent-Claude verifier-loop pre-SIGN corrections applied to 2 sub-agent claims BEFORE Rigby:** (v-l-1) Agent 6 T.C4 dead-code CANDIDATE for EngagementAutonomyEngine REFUTED via direct read of `core.py:2390-2418` (`_policy_engagement_autonomy` has LIVE invoker at :2404); (v-l-2) Agent 5 F2 CANDIDATE at `views_opportunities.py:56-65` UPGRADED to CONFIRMED writer-site via direct read of REST `quick_apply()` writer inventory. **Rigby SIGN cycles 1 + 2 on fresh isolation pin `pa-fba0c4c81fba4922`** → verdict **SIGN-with-edits cycle 1** (Medium-High confidence, 2 must-fix — #1 runtime falsification for F.C1/F.C2, #2 placeholder-stall artifact) → **SIGN-clean cycle 2** (High confidence, 0 residual must-fix + Q7/Q8/Q9 + 2 nice-to-haves folded). **Cycle 1 fold applied via parent-Claude direct verification:** must-fix #1 CLOSED via Django ORM `.count()` on local env — all 4 Category C tables = 0 rows (`EngagementEvent.objects.count() = 0` empirically CONFIRMS F.C1 at RUNTIME in addition to CODE; `EngagementMetrics = 0` and `OpportunityInteraction = 0` nuance session-aggregation axis to "code WORKING + runtime-local DORMANT"; `ContentEngagement = 0` makes F.C4 docstring drift RUNTIME MOOT locally); must-fix #2 push-back accepted by Rigby cycle 2 as her own turn-1 narrative artifact not audit content. Rigby's `db_health_tool` returned `row_count=-1` (pg_class ANALYZE estimate — indeterminate) + `ops_tool.sql_query` did not return in her context + `db_health_tool env=prod` returned "not configured: PA_DB_HEALTH_RPC_URL, PA_DB_HEALTH_RPC_CLIENT_TOKEN" — logged as T.C8 three-checkbox tool-surface gap (a) ToolCallRecord query surface (b) bounded ORM row-count (c) prod DB reach. Cycle 1 Q1/Q4/Q5/Q6 folds applied; cycle 2 Q7/Q8/Q9 folds applied + 2 nice-to-haves (Env Coverage Table + T.C8 three-checkbox split). **Load-bearing findings (6, ranked by runtime severity):** (F.C1) ingestion path missing CONFIRMED HIGH at CODE + RUNTIME LOCAL tiers — Django ORM count zero + grep zero-writers at HEAD `d91d30f7`; both `outreach_draft` and `opportunity` FKs schema-only; extends S1402 F.B3 with second-FK evidence; PROD tier UNKNOWN due to T.C8(c); (F.C2) corrected axis map — dual-sub-agent verified (Agents 1 + 5 independently refuted parent §3 hypothesis with matching evidence); three independent surfaces not the hypothesized event-log-vs-aggregation-vs-join map; OpportunityInteraction is detail-child of EngagementMetrics via nullable FK not a join artifact; (F.C3) OpportunityInteraction F2 orphan-write CONFIRMED at writer-site `views_opportunities.py:56-65` REST `quick_apply()` omits `engagement_session` FK; runtime blast radius LOCAL bounded to ZERO (0 rows) — sibling to S1402 F.B2 zero-blast-radius pattern via different mechanism (empty parent write path vs dead code); (F.C4) ContentEngagement docstring "closes learning loop" drift CONFIRMED — no FK bridge to EngagementEvent/Metrics/OpportunityInteraction; Rigby Q5 lean narrow docstring NOW; (F.C5) EngagementAutonomyEngine "reply context builder" drift CONFIRMED — no such method in 4-method class body; Rigby Q6 lean reframe as "planned surface"; (F.C6) `run_ops_autopilot` deferred-by-policy CONFIRMED via Rigby ops probe + parent-Claude direct read jointly — task defined + docstring declares 10min cadence but NOT registered as PeriodicTask (0 of 92 enabled rows); intentionally deferred per AUDIT_FINDINGS.md #12 gating (`core/celery.py:507-509` + `:633-634` behavior-changing green-light list); ad-hoc PA-tool invocation LIVE at `td_handlers_ops.py:1643,1674`; consequence Category C `evaluate()` sweeps fire only on operator initiation; memory rule `feedback_audit_findings_12_canonical_celery_deferred_list.md` triggered pre-SIGN to correctly classify; Rigby cycle 2 Q1 lean **(iii) separate ADR outside G1400 arc** for enable-decision (cross-category impact spans all 6 Category A/B/C/D/E/F policy hooks). **Inherited findings status:** S1402 F.B3 CONFIRMED HIGH and EXTENDED (adds `opportunity` FK second-writer-gap); S1402 F.B1 delivery-path-missing BLOCKER dependency for F.C1 ingestion design + `OutreachDraft.provider_message_id` MISSING (grep zero hits — R.C5 micro-migration); S1402 F.B4 does NOT extend to Category C `evaluate` methods (both LIVE via policy registry); Rigby cycle 1 Q4 lean **(ii) two sequential ADRs — F.B1 first, F.C1 stacked** ("cleaner dependency ordering and less thrash"); S1401 F1/F2/F3 lenses applied — F1 CANDIDATE holds for readers, F2 CONFIRMED at F.C3, F3 CANDIDATE at 5min Redis TTL in consumer; ownership gap S1274 §14 #36 CONFIRMED HIGH for Category C (0 JobContract + 0 AGENT_MAP + 0 task_routes hits); coverage upgraded LIGHT → MODERATE. **Maturity verdict WORKING (code) / DEFERRED-BY-POLICY (autonomous runtime) / WORKING code + DORMANT local runtime (session-aggregation axis) / MISSING (canonical ingestion)** — four-way split extending S1402 §13 WORKING/PARTIAL pattern. §19 follow-on queue 8 items ranked: R.C1 F.C1 ingestion path ADR (CENTRAL — pair-designed sequentially with F.B1); R.C2 F.C3 orphan-write fix; R.C3 F.C4 FK bridge (post-arc); R.C4 documentation anchor updates at §3.32 with per-model annotations per Rigby cycle 2 Q9 lean; R.C5 `OutreachDraft.provider_message_id` migration (blocks R.C1); R.C6 F.C5 resolution; R.C7 Governance §3.23 crossover ADR (bundle Group 1700); R.C8 F1 provenance-drift repo-wide sweep (deferred until F.C1 writer contract lands). T.C8 tool-surface gap IMMEDIATE per Rigby cycle 2 Q8 (low-risk high-leverage arc-support tools). All 28 canonical questions answered; parent §12.1 Category C F.iii questions all 3+1 answered. Verifier-loop history preserved append-only per playbook §6. §8 timeline S1403 row added. | **Third Group 1400 child audit; first library audit to CONFIRM a canonical event log architecturally-intact-but-runtime-empty finding at both CODE and RUNTIME LOCAL tiers** via parent-Claude Django ORM `.count()` when Rigby's `db_health_tool` returned indeterminate `row_count=-1` estimate. Also first library audit where **PROD runtime tier is explicitly UNKNOWN due to Rigby tool-surface gap** — logged as explicit constraint on empirical falsification scope. Also first library audit where **Rigby withdraws a cycle-1 must-fix as her own narrative artifact after parent-Claude pushback** ("Must-fix #2 is withdrawn: agreed it was my cycle-1 response artifact, not an audit-file defect"). Sets two verifier-loop pattern extensions: (a) parent-Claude runs alternate direct-verification via Django `manage.py shell` when Rigby's tool returns indeterminate — extends S1402 D.B7 joint-methodology from "confirmation" to "alternate-path direct-verification"; (b) parent-Claude pushback on must-fix classification is legitimate cycle-2 fold move when the must-fix originates in Rigby's response artifact not audit content. Load-bearing story: Category C is code-complete on read-only monitoring + session-aggregation surfaces but runtime-dormant in probed env; canonical ingestion has no writer path; F.B1 → F.C1 pair-design sequential ADR is arc-forward critical path. Isolation pin `pa-fba0c4c81fba4922` retires post-PR-merge per playbook §15. Index v22 updated per §10.1 (this row + §1.25 row + frontmatter v22 preamble). |

| **S1404** (2026-07-01) | `domains/revenue/1404_revenue_meeting_close_audit.md` (§1.26) | **Fourth child audit under Group 1400 Revenue (parent §1.22).** Category D Meeting + Close exclusive scope per parent §3 Cat D evidence surface + §12.1 Category D F.iii questions. 20-section playbook §11.2 template + §13 6-parallel-Explore sweep on 6 Category D evidence surfaces (Meeting model + ClosePack model + OpportunityAction/OpportunityTask lifecycle checkpoints + HumanAttentionItem interlock + MeetingEngine + policy hook + integrity audit design). **Parent-Claude verifier-loop pre-SIGN corrections applied to 3 sub-agent claims + 1 parent-doc drift surfaced BEFORE Rigby:** (v-l-1) Agent 2 promoted `CloseTheDealEngine.generate_pack` at `revenue.py:931/:991` as actual ClosePack writer (parent §3.D had named `ClosePackAutonomyEngine` at `:1504` which is READ-only monitoring) — F.D7 parent-doc drift surfaced; (v-l-2) Agent 5 confirmed `MeetingCoordinatorAgent` at `core/agents/executive/meeting_coordinator_agent.py:66` is executive-agent facilitation (BaseAgent multi-agent CTO/COO/CreativeDirector synthesis) with zero `Meeting.objects.create` calls — F.D8 parent-doc category miscount; (v-l-3) Agent 3 parallel-axis hypothesis for OpportunityAction (`core/models_unified_system.py:2552`) + OpportunityTask (`:3000` OneToOneField to Opportunity at `:3028`) CONFIRMED via Agent 6 FK graph cross-check — F.D9 structural correction (parent §3.D grouped as "Cat D lifecycle checkpoints" but both models have zero FK to Meeting/ClosePack + are written from Cat A code paths `views_opportunity.py:417,486,836,1149` + `opportunity_scoring_agent.py:1013`). **Rigby SIGN cycles 1 + 2 on fresh isolation pin `pa-87ee24cd0d3947ce`** → verdict **SIGN-with-edits cycle 1** (Medium-High confidence, 4 must-fix + 4 nice-to-have) → **SIGN-clean cycle 2** (High confidence, all 4 must-fix folded + NH-2/NH-3 applied + NH-1/NH-4 deferred). **Cycle 1 fold — T.D5 CANDIDATE → F.D10 CONFIRMED HIGH promotion via joint Rigby broader-grep + parent-Claude direct-read disambiguation:** Rigby's initial `status='sent'` grep returned mixed hits at `revenue.py:1073,1116,1120,1170,1173,1356,1414,1489`; parent-Claude direct-read at `:1100-1180` disambiguated writers from `.filter()` READS. Actual ClosePack state writers: `draft` (default at `:991`), `approved` (`:1073` in `approve_pack`), `expired` (`:1173` bulk `.update(status='expired')` in `ClosePackAutonomyEngine.evaluate`). `sent`/`won`/`lost` CONFIRMED unreachable — all grep hits are `.filter()` READS or aggregate keys. Paired arc-drift finding with F.D6 Meeting analog (both models declare 6-state STATUS_CHOICES but implement only 3-4 states). **Django ORM runtime probe (parent-Claude via `.venv/bin/python manage.py shell` — extends S1403 alternate-path direct-verification):** `Meeting.objects.count() = 0` + `ClosePack.objects.count() = 0` + `EngagementEvent.objects.count() = 0` + `OutreachDraft.objects.count() = 40` + `HumanAttentionItem.objects.count() = 3061` (distribution: 2854 spider_pipeline + 155 agent_output + 2 ops_autopilot only — CONFIRMS F.D4 at runtime tier). PROD counts UNKNOWN per T.C8(c) inherited from S1403. **Load-bearing findings (10 — F.D10 added SIGN cycle 1 fold from T.D5 promotion):** (F.D1) Meeting-trigger runtime liveness LOCAL = ZERO CONFIRMED HIGH CODE + RUNTIME LOCAL; (F.D2) Meeting.engagement FK never populated by sole writer at `engagement.py:507` F2 orphan-write class code-tier; (F.D3) ClosePack trigger = MANUAL PA tool via `close_pack_generate` at `td_handlers_ops.py:2757-2776` — **resolves S1273 §10.3 UNKNOWN #3**; (F.D4) Revenue → HumanAttention CONFIRMED MISSING HIGH at Cat D, arc-wide SYSTEMIC gap extending B + C — **resolves S1274 §2.4 line 294 MISSING to CONFIRMED HIGH**; (F.D5) Meeting docstring drift HIGH at `models_meeting.py:22`; (F.D6) Meeting 3 unreachable states MEDIUM (no_show/cancelled/followed_up); (F.D7) Parent §3.D anchor drift ClosePackAutonomyEngine misnamed as writer — immediate anchor-update per Rigby Q2 lean; (F.D8) Parent §3.D miscount MeetingCoordinatorAgent NOT a Meeting writer — immediate anchor-update per Rigby Q2 lean; (F.D9) Structural correction OpportunityAction/OpportunityTask = Cat A parallel axis not Cat D lifecycle checkpoints — immediate anchor-update per Rigby Q1 lean; (F.D10) ClosePack state machine PARTIAL CONFIRMED HIGH — writers for approved + expired only; sent/won/lost unreachable; paired arc-drift with F.D6 for xx99. **Rigby cycle 1 Q1-Q9 answers all folded** at §20.7: Q1 IMMEDIATE F.D9 anchor-update; Q2 IMMEDIATE F.D7/F.D8 anchor-updates; Q3 F.D6 stay MEDIUM; Q4 T.D5 → F.D10 promotion (drop R.D2 companion); Q5 R.D6 HAI ADR bundled with F.B1→F.C1 stacked pair; Q6 YES R.D8 CI guard smoke test; Q7 YES Group 1400 PA-tool inventory at S1499 xx99; Q8 LAND T.C8(a)+(b) NOW pre-S1405; Q9 SINGLE S1499 EventStream proposal (bundles OUTREACH_+ ENGAGEMENT_+ MEETING_+ CLOSE_PACK_). **Cycle 2 folds applied:** NH-2 F.D6 "why it matters" 2-sentence expansion (over-modeled enum harmless while runtime empty; contaminates dashboards once ingestion lands); NH-3 PROD-facing runtime-liveness stub method (Rigby `db_health_tool env=prod action=tables prefix=core_` when T.C8(c) lands). NH-1 (F.D5 wording calibration) + NH-4 (EventStream "none found" table) DEFERRED. **§20.10 Anchor corrections to upstream parent subsection added** — 3 immediate parent-doc corrections landing at S1404 commit-time per Rigby cycle 1 Q1+Q2 leans. **§20.11 Arc trajectory statement embedded (Rigby verbatim):** "With Categories A/B/C/D now converging on (i) missing Revenue → HumanAttention approval/interlock, (ii) ownership gaps, and (iii) runtime-liveness breaks preventing Meeting/ClosePack from being populated, S1499 should synthesize a single 'activate the revenue lifecycle + enforce approval/attention gating' remediation plan, while immediate anchor/taxonomy corrections prevent further drift." **Inherited findings status:** S1274 §2.4 line 294 CONFIRMED HIGH arc-wide (F.D4); S1274 §5.10 tight-coupling LOW-by-design CONFIRMED at Meeting-engagement + ClosePack-outreach_draft null-FK level; S1274 §14 #36 (Revenue Pipeline no runtime owner HIGH) CONFIRMED for Cat D §18 deferred to Cat E per D28; S1273 §10.3 UNKNOWN #3 RESOLVED to MANUAL (F.D3); S1401 §9 Cat A → D read direction verified; S1402 §14 D.B7 dead-code methodology applied inversely at F.D8 (MeetingCoordinatorAgent has invokers via PA dispatch — memory rule `feedback_verify_before_deleting_dead_code.md`); S1403 F.C1 + F.C6 inherited as upstream blockers; S1399 F1/F2/F3/F4 methodology lenses applied. Coverage LIGHT → MODERATE. **§19 follow-on queue 9 items ranked:** R.D1 Meeting + ClosePack writer normalization ADR (F2 class); R.D2 Meeting state machine completion ADR (F.D6); R.D3 Category D anchor-updates ADR IMMEDIATE (§20.10); R.D4 optional Cat D topic doc post-arc; R.D5 policy-hook enablement ADR cross-arc; R.D6 HumanAttention interlock ADR bundled with F.B1→F.C1 pair (CENTRAL S1404 deliverable); R.D7 ClosePack offer-configuration ADR; R.D8 integrity audit design + CI guard smoke test (CENTRAL S1404 deliverable — 5-model FK chain + 10 orphan patterns + Session 1196 precedent); R.D9 F1 provenance-filter drift repo-wide sweep (deferred until F.B1/F.C1 write-side lands). All 28 canonical questions answered; parent §12.1 Category D F.iii Q's all 4 answered + inherited-from-S1403 Q answered. Verifier-loop history preserved append-only per playbook §6. §8 timeline S1404 row added. | **Fourth Group 1400 child audit; first library audit to surface parent-doc drift as a load-bearing must-fix cluster (3 corrections in one audit: F.D7 + F.D8 + F.D9)** — extends S1401's 5-sub-agent-correction methodology from lateral-only (agent-vs-agent) to include upward-directed (parent-doc drift catches). Also first library audit to CONFIRM a paired arc-level structural drift (F.D6 Meeting + F.D10 ClosePack — both models declare 6-state STATUS_CHOICES but implement only 3-4). Also first library audit where **joint Rigby broader-grep + parent-Claude direct-read disambiguation resolved substring-ambiguous grep hits during SIGN cycle 1 fold** — Rigby's initial `status='sent'` grep returned mixed writers + reads; parent-Claude direct-read at `revenue.py:1100-1180` disambiguated. Extends S1403 "alternate-path direct-verification when Rigby tool returns indeterminate" pattern to "alternate-path direct-read disambiguation when Rigby grep returns substring-ambiguous hits" — new verifier-loop discipline extension for S1499 arc-methodology synthesis. Group 1400 arc convergence surfaces at S1404: Categories A/B/C/D all confirming (i) Revenue → HumanAttention MISSING (F.D4 arc-wide), (ii) ownership gaps (§18 arc-wide from S1274 §14 #36), (iii) runtime-liveness dormancy where autonomous cadence is deferred (F.D9 same class as S1403 F.C6). S1499 xx99 canonical summary trajectory locked: single "activate the revenue lifecycle + enforce approval/attention gating" remediation plan. Isolation pin `pa-87ee24cd0d3947ce` retires post-PR-merge per playbook §15. Index v23 updated per §10.1 (this row + §1.26 row + frontmatter v23 preamble). |

| **S1405** (2026-07-01) | `domains/revenue/1405_revenue_attribution_analytics_audit.md` (§1.27) | **Fifth child audit under Group 1400 Revenue (parent §1.22).** Category E Revenue Attribution + Analytics exclusive scope per parent §3 Cat E evidence surface + §12.1 Category E F.iii questions. 20-section playbook §11.2 template + §13 6-parallel-Explore sweep on 6 Category E evidence surfaces (OpportunityRevenue model + OpportunityOutcome model + OpportunityContent model + ops_autopilot revenue.py + impact.py attribution engine + attribution bridges + 3 view files + 4 frontend routes + Celery beat calculate-daily-revenue-metrics). **Parent-Claude verifier-loop pre-SIGN 12/12 direct-read checkpoints CONFIRM sub-agent claims; 2 anchor corrections landing at S1405 commit-time** (F.E4 parent §3.E line 431 4-route list — routes DO NOT EXIST in `frontend/src/App.tsx` grep 0 matches; actual revenue surfaces via `/analytics` + `/intelligence` routes; F.E6 parent §3.E + §12.1 attribution algorithm location — actual algorithm at `core/services/ops_autopilot/impact.py:1233-1290` `MultiTouchAttributor._attribute_event` with 70% last-touch + 30% assist evenly split writes `ImpactCredit`; `ops_autopilot/revenue.py` contains pipeline forecasting engines only). **Verifier-loop discipline extension:** new pattern **broadened-grep with model-context disambiguation** — F.E1 `outcome='partial'` broadened grep returned hits at `core/tasks.py:6631` + `core/tasks_misc.py:162`; parent-Claude direct-read disambiguated both as `PilotExecution` model (unrelated to OpportunityOutcome); sub-agent F.E1 unreachable-state claim UPHELD. **Rigby SIGN cycle 1 PARTIAL — Batch 1 F.E1-F.E3 substantive pressure-test delivered; Batches 2-3 blocked by worker instability.** First SIGN pin `pa-4bdd5ad264674ce8` jammed after 2 substantive turns (placeholder-stall pattern observed on turn 2 despite verbose tool block showing full-doc read); retired at `updated_count: 10`. Second SIGN pin `pa-637331c5f9574a10` (batched-retry per D44 Chris ratification (iii)→(i)): Batch 1 substantive pressure-test on F.E1 (HIGH confidence tech-debt/integrity issue with 3 potential-nuance disambiguations still stands), F.E2 (STRONG "canonical latent crash class" — flagged MUST-FIX before canonical unless proven dead code), F.E3 (framing refinement: dual-schema MAY be intentional core=accounting-truth vs intelligence=external-ingestion; if intentional gap reframes to "missing explicit contract + source-of-truth hierarchy"). Batches 2-3 generic-erroring on subsequent retries (worker instability). **D45 Chris ratification option (ii):** accept Batch 1 substantive pressure-test as SIGN-with-edits cycle 1 verdict; batches 2-3 deferred to follow-up SIGN addendum; F.E3 framing refinement folded at commit-time (audit §14.3 + §19 R.E-3 ADR scope revised). **Load-bearing findings (10 F.E findings + 2 anchor corrections):** F.E1 3-model over-modeled STATUS_CHOICES arc-wide (16 declared / 6 reachable / 10 UNREACHABLE across ClosePack S1404 F.D10 + OpportunityRevenue new + OpportunityOutcome new); F.E2 4 phantom-field references worse than S1399 F1 (readers filter on fields that don't exist in schema — deterministic runtime errors, latent per F.D1 empty-tables pattern; MUST-FIX before canonical per Rigby Batch 1); F.E3 dual-representation drift extends S1401 D6 to Revenue with Rigby framing refinement (intentional-vs-drift decision at R.E-3 ADR); F.E4 parent-doc drift #1 (4 frontend routes don't exist — anchor correction); F.E5 duplicate view file endpoint pairs (`views_revenue.py` POST /api/revenue/create/ vs `views_revenue_tracking.py` POST /api/v1/revenue/track/; GET /api/revenue/summary/ vs GET /api/v1/revenue/stats/; `views_revenue_analytics.py` architecturally distinct); F.E6 parent-doc drift #2 (attribution algorithm at `impact.py:1233-1290` not `revenue.py` — anchor correction); F.E7 F.D4 refinement (HAI writers CODE-EXIST at 6 core.py sites `:1561` `:1673` `:2051` `:2117` `:2237` `:2361` but RUNTIME-DORMANT via F.C6 deferred `run_ops_autopilot`); F.E8 S1274 §2.4 STRONG classification verified end-to-end (ImpactEvent chain: ImpactCollector at `impact.py:238-505` → 6+ readers → attribution report → HAI via `_policy_attribution_debt:1673`); F.E9 S1274 §4.3 attribution bridge verified with 2-path signal mechanism (`revenue_attribution_bridge.py:227` @receiver(post_save, sender=Revenue) → UserAgentLearning writes at `:147` learning_domain='revenue_optimization' + `:181` learning_domain='success_factors'; docstring drift on "insights → UnifiedLearningPipeline" unfulfilled); F.E10 runtime owner ABSENT arc-wide (zero JobContract in `core/employees/jobs.py`; zero AGENT_MAP in `core/agent_router.py`; zero task_routes; no dedicated Celery queue; only PA tool `revenue_tracker_tool` at `pa_tool_schemas.py:188-208` — Cat E owns arc-wide synthesis per parent D28). **Cross-arc convergence at S1405 close (5-pillar arc trajectory extending S1404 §20.11):** (i) F.E7 refines F.D4 as code-exists/runtime-dormant; (ii) F.E10 confirms S1274 §14 #36 arc-wide; (iii) F.E3 3 disconnected pipelines (core + intelligence + calculate_daily_revenue_metrics); (iv) F.E1 extends F.D10 to 3-model over-modeling; (v) F.E2 latent phantom-field bugs. **S1499 xx99 unified remediation plan candidates (5 tracks):** T1 activate lifecycle F.B1 → F.C1 → F.D6 → F.E3 sequential ADR chain; T2 F.E10 Revenue Employee JobContract ADR; T3 F.E7/F.C6 `run_ops_autopilot` enable-decision ADR (cross-arc); T4 F.E5 view-file consolidation ADR; T5 F.E1 arc-wide STATUS_CHOICES cleanup ADR. **Inherited findings status:** S1274 §2.4 line 292 STRONG (F.E8 VERIFIED); S1274 §2.4 line 294 REFINED via F.E7; S1274 §14 #36 CONFIRMED at Cat E code layer (F.E10); S1274 §4.3 CONFIRMED with 2-path mechanism (F.E9); S1274 §9.6 LOW readiness CONFIRMED; S1273 §10.3 UNKNOWN #3 attribution algorithm RESOLVED via F.E6; S1399 F1 inherited (F.E2 more severe variant); S1401 §14 D6 dual-representation extended to Revenue via F.E3; S1404 F.D4 refined via F.E7; S1404 F.D10 extended arc-wide to 3-model via F.E1. **§19 follow-on queue 7 items ranked:** R.E-1 Revenue Employee JobContract ADR (F.E10 primary); R.E-2 view-file consolidation ADR (F.E5); R.E-3 dual-representation reconciliation ADR two-part (F.E3 framing + remediation); R.E-4 STATUS_CHOICES cleanup ADR arc-wide (F.E1 3-model); R.E-5 F.E2 phantom-field fix PR (LOW-effort MUST-FIX); R.E-6 F.C6 run_ops_autopilot enable-decision ADR cross-arc; R.E-7 revenue_integration.py completion or scope-reduction ADR. **§20.9 Rigby SIGN cycle log:** 2 pins used, both retire post-PR-merge per playbook §15. Batch 1 must-fix MF1 (F.E2 phantom fields — bundle 4-site cleanup PR post-arc; if dead code document + remove per memory rule `feedback_verify_before_deleting_dead_code.md`) + MF2 (F.E3 framing refinement — landed at commit-time) + MF3 (F.E1 3-model nuance probe pre R.E-4 landing). §8 timeline S1405 row added. | **Fifth Group 1400 child audit; first library audit to complete arc-wide 3-model over-modeling pattern** (F.E1 extends F.D10 to OpportunityRevenue + OpportunityOutcome across ClosePack; 16 declared / 6 reachable / 10 UNREACHABLE combined 62%). Also **first library audit to surface a new class of drift worse than S1399 F1** — F.E2 phantom-field references where readers filter on fields that don't exist in schema (deterministic runtime errors, latent only because tables empty per F.D1). Also **first library audit to ship with partial SIGN cycle 1** — Rigby SIGN worker instability across two fresh isolation pins blocked batches 2-3 (F.E4-F.E10) after substantive Batch 1 pressure-test on F.E1-F.E3; D45 Chris ratification option (ii) accepted Batch 1 as SIGN-with-edits verdict; batches 2-3 deferred to follow-up SIGN addendum; parent-Claude 12/12 verifier-loop as compensating quality gate. Also **first library audit to fold Rigby framing refinement at commit-time on dual-representation drift** — F.E3 gained "possible intentional dual-schema" alternative interpretation + R.E-3 ADR scope revised to two-part (framing + remediation). Memory rules triggered: `feedback_verify_before_deleting_dead_code.md` (F.E1 disambiguation); `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` (Rigby placeholder-stall observed on first SIGN pin — verbose tool block confirmed full read despite narrative claim of partial retention). SIGN pins `pa-4bdd5ad264674ce8` + `pa-637331c5f9574a10` both retire post-PR-merge per playbook §15. Index v24 updated per §10.1 (this row + §1.27 row + frontmatter v24 preamble). |

| **S1406** (2026-07-01) | `domains/revenue/1406_revenue_freelance_gig_income_jobs_audit.md` (§1.28) | **Sixth (final) child audit under Group 1400 Revenue (parent §1.22); completes 6-child arc.** Category F Freelance / Gig — Income-Jobs lane exclusive scope per D25 F.i Chris-lock (Income/Jobs lane, not just FreelanceOpportunity model) + parent §3 Cat F evidence surface + §12.1 Category F F.iii questions. 20-section playbook §11.2 template + §13 6-parallel-Explore sweep on 6 Category F evidence surfaces (FreelanceOpportunity model + ai_job_matcher/pipeline + income_builder trio + connector/orchestrator/bridge trio + job_scanner_consumer/ai_resume_generator + cross-arc F.E10 ownership synthesis Cat F half). **Parent-Claude verifier-loop 12/12 checkpoints: 10 CONFIRM + 2 DISAMBIGUATION.** New pattern: **provenance-stamp ORM probe as disambiguation tool** — Agent 4 sub-agent claim "hourly writes 20 rows via `income_spider_orchestrator.py:462`" was REFINED not REFUTED via direct ORM query `.filter(metadata__created_via='income_spider_orchestrator').count() = 0` on local DB (99.96% of 2631 Opportunity rows have provenance `spider_decision_bridge` instead — dominant writer at `intelligence/spider_decision_bridge.py`); beat entry exists at `core/celery.py:755-759` LIVE-scheduled but writes not landing at that provenance stamp locally. Extends S1401-S1405 verifier-loop tools (file-line direct-reads, broader-grep, model-context disambiguation) with ORM-provenance disambiguation. **Rigby SIGN cycle 1 substantive on fresh isolation pin `pa-8660ea7cfecd4bc6`; first application of S1405 D48 stability-probe gate.** Fresh pin first-turn generic-error triggered S1405 D45 recovery-pattern warmup-ping (ultra-short "confirm ready" probe); Rigby responded "Ready. I don't have direct visibility into that draft file path unless you paste excerpts... but I'm ready to receive the titles-only SIGN batch now." Three batches delivered substantively: **Batch 1 (F.F1-F.F3 HIGH severity)** all 3 findings SURVIVE at HIGH with 3 framing refinements folded (F.F1 hard-crash-vs-currently-unreachable + call-chain evidence pin; F.F2 evidence-gap classification of 20 writers deferred to S1499; F.F3 ownership-plane-vs-capacity-plane separation); **Batch 2 (F.F4-F.F6):** F.F4 split into 4a/4b/4c sub-findings with separate severities (shim MEDIUM / stub HIGH-if-user-facing / Flask demo LOW-MEDIUM); F.F5 full-writer sweep deferred to S1499 T.F8; **F.F6 UPGRADED to MUST-FIX** per Rigby "north-star blocker" verdict (without outcomes cannot tune prompts, ranking, or ROI); **Batch 3 (F.F7-F.F10):** F.F7 no-false-negative confirmed via alternate-abstraction spot-check (57 broadcast_/publish_event/redis.publish hits across 10 files, none reference the 7 Cat F channel names); F.F8 tightened to "no UI client" + non-UI clients not audited note; **F.F9 UPGRADED to HIGH** after parent-Claude direct-verify of `core/llm_enforcer.py:232` confirmed `downgrade_model = 'gpt-5-mini'` wired + line 446-450 downgrade log confirming enforcer DOES route to gpt-5-mini via budget-controller downgrade path — silent-empty risk activated not latent; F.F10 reframed as taxonomy/ownership smell not drift. **Batch 4 (S1405 F.E4-F.E10 deferred addendum per D48 fold) BLOCKED by worker-instability pattern recurring on turn 4** (same failure mode as S1405 pins). **D51 Chris ratification (i)** defers S1405 F.E4-F.E10 pressure-test to S1499 xx99 synthesis per D48 fallback (iii). **D50 Chris ratification (i)** accepts SIGN-with-edits cycle 1 with commit-time folds — no cycle 2 attempt given worker-instability pattern matches S1405 D45 discipline. **Load-bearing findings (10 F.F):** F.F1 phantom-field writer arc-wide F.E2 extension (5 phantom fields UNGUARDED at `core/tasks_ops.py:2239-2251` — WORSE than S1405 F.E2 hasattr-guarded; runtime `FieldError` guaranteed if invoked; task not beat-scheduled locally, PROD unknown per T.C8(c)); F.F2 multi-writer convergence on `Opportunity` F.E3 arc-wide extension (20 files call `.create()`; `intelligence/spider_decision_bridge.py` dominant at 2630/2631 rows locally = 99.96%; `income_spider_orchestrator.py:462` produces 0 rows via provenance stamp — no canonical write-authority contract enforcement); F.F3 arc-wide runtime-owner-absent COMPLETES F.E10 synthesis (zero JobContract in `core/employees/jobs.py`, zero AGENT_MAP entries, zero dedicated PA tool schema, one shared `long_running` queue not dedicated; Cat E owned first half S1405, Cat F owns second half S1406 per D28); F.F4 three orthogonal dead-code patterns co-locate in one lane (Session 727 deprecation shim `intelligence/income_builder.py` with 45+ importers + view null-check stub `AIJobApplicationView.post` lines 202-218 + Flask demo `income_builder_connector.py` never production-deployed; split into 4a/4b/4c sub-findings per Rigby fold); F.F5 STATUS_CHOICES over-modeling extends F.E1 to intelligence-side (`OpportunityActionPlan` 11 declared / 3 reachable = 27% reachability, WORSE than S1405 F.E1 arc-wide 37.5%; full-writer sweep deferred to S1499 T.F8); F.F6 learning-loop-missing arc-wide MUST-FIX Cat F leg (F.C4 extension: `ai_resume_generator` no feedback + `job_scanner_consumer.py:497` TODO 'Would track real responses' + `ai_job_application_pipeline` filesystem-only writes; expected loop spec: event generated/applied/responded/interviewed/hired → model/table → application_outcome_bridge hook already registered globally per apps.py:1848 but Cat F does not write into it); F.F7 Redis pub-sub orphan channels new pattern (7 channels subscribed in `ai_job_application_pipeline.py:58-66`; 0 publishers arc-wide via alternate-abstraction verification); F.F8 frontend disconnection F.E4 extension (`/ws/job-scanner/` wired in `intelligence/routing.py:12` extended into `core/routing.py:192` but grep-negative for `/ws/job-scanner/` in `frontend/src/**/*.{tsx,ts}`; `ai_resume_generator.py` public API unused by production views; CareerTab.tsx uses /api/ats/* possibly duplicate surface); F.F9 LLM max_tokens floor risk UPGRADED to HIGH (`ai_resume_generator.py:256` max_tokens=200 / line 518 max_tokens=500; both below gpt-5-mini 4000 floor per memory rule `feedback_gpt5_max_completion_tokens_floor.md`; `core/llm_enforcer.py:232` `downgrade_model = 'gpt-5-mini'` CONFIRMED wired + line 446-450 downgrade log active → silent empty content risk ACTIVE not latent); F.F10 model placement drift LOW informational (FreelanceOpportunity in `models_autonomous_situations.py` bulk Session 479 rollout not co-located with Revenue-domain models; reframed as taxonomy/ownership smell supporting F.F3). **Arc-wide 5-pillar convergence extending S1405 (Cat F completions):** (i) F.E10 (S1405) + F.F3 (S1406) = COMPLETE arc-wide ownership synthesis; (ii) F.E3 (S1405) + F.F2 (S1406) = dual-representation drift extends from Revenue schemas to Opportunity write path (multi-writer variant); (iii) F.E2 (S1405) + F.F1 (S1406) = phantom-field pattern extends arc-wide as latent-crash class; (iv) F.E1 (S1405) + F.F5 (S1406) = STATUS_CHOICES over-modeling extends to intelligence-side models; (v) F.D4/F.D8 (S1404) + F.F4 (S1406) = dead-code/dormancy-at-scale (three orthogonal patterns co-locate). **S1499 xx99 unified remediation plan candidates now include Cat F track additions (T6-T10 on top of S1405's T1-T5):** T6 Income/Jobs Employee JobContract ADR (paired with S1405 T2 Revenue Employee — single-merged vs two-sibling decision); T7 multi-writer convergence contract for `Opportunity`; T8 phantom-field remediation (LOW-effort MUST-FIX); T9 deprecation shim retirement + 45-file migration; T10 Redis pub-sub schema contract. Total S1499 track candidate count: 10 (T1-T10). **Inherited findings status:** all 15 parent §11.4 inherited findings + 5 arc-wide S1401/2/3/4/5 patterns applied as diagnostic lenses; Cat F extends 5 of them (F.E1/F.E2/F.E3/F.E10 explicitly + F.D1 empty-tables + F.D4 HAI arc-wide) with 0 new contradictions. **§19 follow-on queue 7 items:** R.F-1 Income/Jobs Employee JobContract ADR (F.F3, HIGH); R.F-2 `Opportunity` multi-writer write-authority framework (F.F2, HIGH); R.F-3 phantom-field writer decision (F.F1, HIGH); R.F-4 deprecation shim retirement (F.F4a, MEDIUM); R.F-5 Redis pub-sub schema contract (F.F7, MEDIUM); R.F-6 frontend integration decision (F.F8, MEDIUM); R.F-7 `AIResumeGenerator` LLM max_tokens fix (F.F9, LOW). §8 timeline S1406 row added. | **Sixth (final) Group 1400 child audit; completes Group 1400 arc trajectory.** Categories A/B/C/D/E/F all shipped; S1499 xx99 owns final synthesis + unified remediation plan (10 tracks T1-T10). **First library audit to complete arc-wide F.E10 ownership synthesis** — F.F3 confirms Cat F half; Cat E owned first half (S1405). **First library audit to extend F.E1/F.E2/F.E3 patterns to a third domain lane** (Income/Jobs on top of Revenue's core + intelligence). **First library audit to introduce provenance-stamp ORM probe as new verifier-loop disambiguation tool** — extends S1401-S1405 verifier-loop tool chain with ORM-provenance query as disambiguation mechanism. **First library audit to fold Rigby SIGN into 3 substantive batches after fresh-pin first-turn generic-error recovery** — D48 stability-probe gate application; Batches 1-3 substantive with 10 framing refinements + 2 severity upgrades (F.F6 MUST-FIX + F.F9 HIGH); Batch 4 deferred per D45+D48 fallback discipline. **First library audit to complete arc-wide 5-pillar convergence at child-audit level** (rather than deferring pattern-identification to xx99) — Cat F's 10 F.F findings enumerate the 5 pillars extended from prior categories with no residual pattern-identification work for xx99 (S1499 owns unified remediation plan T1-T10, not pattern-identification). Memory rules triggered: `feedback_verify_before_deleting_dead_code.md` (F.F4 anti-pattern guard for shim + null-check stub + Flask demo); `feedback_fleet_caller_verification_before_celery_deletes.md` (F.F4c fleet-app verification deferred to S1499 T9); `feedback_gpt5_max_completion_tokens_floor.md` (F.F9 direct-verify triggered severity upgrade); `feedback_procfile_makefile_queue_parity.md` (F.F3 queue verification); `feedback_rigby_sign_worker_instability_recovery.md` (Batch 4 worker instability triggered D45 recovery + D48 fallback (iii)); `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` (fresh-pin generic-error on turn 1 recovered via warmup ping). SIGN pin `pa-8660ea7cfecd4bc6` retires post-PR-merge per playbook §15. Index v25 updated per §10.1 (this row + §1.28 row + frontmatter v25 preamble). |
| **S1499** (2026-07-01) | `domains/revenue/1499_revenue_canonical_summary.md` (§1.29) | **Group 1400 Revenue arc-close canonical summary; second application of playbook §11.3 §10 meta-methodology template after S1399 close.** 12-section canonical summary per playbook §11.3 template consuming S1401-S1406 6-child audit outputs + parent §12.5 F.iii Revenue Lifecycle Traceability Table requirement (9 stages mapped; 4 CRITICAL-INCOMPLETE + 5 LIVE-BUT-DRIFTING + 0 CLEAN-END-TO-END). **5 arc-wide cross-cutting patterns identified** (§4): (i) F2 orphan-write class CONFIRMED at 8 finding sites across all 6 children unanimous (root: no write-authority framework); (ii) F1 provenance-filter drift CONFIRMED at 2 sites Cat A+B narrow-scope debt (below 3-child cross-cutting threshold; elevation gate documented); (iii) state-machine incomplete CONFIRMED at 4 models across D+E (16 declared, 6 reachable, 10 UNREACHABLE = 62%); (iv) learning-loop incomplete CONFIRMED at 3 sites C/E/F with 2-bucket structural split (missing instrumentation vs dual-schema); (v) **runtime-owner MISSING UNANIMOUS 6/6 — arc headline finding**. **D55 (ii) two sibling JobContracts** ratified by Chris 2026-07-01 (Revenue Employee for Cat A/B/C/D/E + Income/Jobs Employee for Cat F). **T4 R.F3 Income lane dormancy disposition Chris-locked (b) DORMANT-PLANNED** — T3 Income/Jobs Employee JobContract SPEC'D but not activated; activation gate: post-T1/T5/T6/T7 foundation landing + explicit Chris re-ratification (30-60 day horizon per Rigby lean). **Rigby SIGN-with-edits cycle 1 substantive via fresh isolation pin `pa-877f1919efaa48e4` (retired post-fold):** 22 verdicts across Q10-Q13; 22 CONFIRM (0 FLIP); 10 FLAG-EDIT framing refinements folded at commit-time (V2 T1 subcases + V4 residual-risk auditability + V6 channel-class naming + V8 v26 preamble + V10 3 doc-surface deferral notes + V11 write+routing authority + V13 state-machine reachability nuance + V14 learning-loop 2-bucket split + V18 T6 ship-to-go-live label + V20/V22 T7 promoted to TIER 2); 0 must-fix; 0 severity flips. **D48 stability-probe gate + D45 titles-only recovery pattern successfully recovered from first-turn worker-instability** — S1499 SIGN pin first substantive turn (~2400 words) triggered "issue processing" error; recovery via 2-3-verdict batches delivered 22/22 CONFIRM. Matches S1399 SIGN-clean cycle 1 pattern. **Parent-Claude 12-checkpoint verifier-loop pre-SIGN caught 4 corrections + folded** at draft-time (impact.py path prefix; F2 count 7→8 sites; §4.5 ownership-gap refs; PR numbers S1401=#2788 + S1402=#2789 + Employee OS count 4→6 with CLAUDE.md 3-vs-4 drift). **§7 anchor-update recommendations for subsequent PR:** 6 `platform_architecture_inventory.md` §3.32 corrections (F.D4 ClosePackAutonomyEngine reader-only + F.D5 OpportunityAction/Task move to Cat A + F.D8 remove MeetingCoordinatorAgent + F.E4 frontend routes + F.E6 attribution algorithm location + §4.9 outbound-channel broadening); NEW `docs/topics/revenue-pipeline.md` first-inventory landing. **§8 T1-T10 unified follow-on queue tier structure:** TIER 1 blocking (T4 R.F3 Chris-locked (b)); TIER 2 umbrella ADRs (T1 parallel-schema/source-of-truth with 2 subcases + T5 delivery+ingestion sequential ADR pair + T6 HAI interlock ship-to-go-live prerequisite + T7 write+routing authority PROMOTED + T8 state-machine completion); TIER 3 Employee OS (T2 Revenue Employee + T3 Income/Jobs Employee spec'd not activated); TIER 4 cleanup (T9 phantom-fix + T10 Celery routing); TIER 5 optional deferrables. **§10 meta-methodology second application (after S1399 first):** all 5 S1399-codified patterns REPLICATED in Group 1400 (F1/F4-CANDIDATE discipline + sibling-inheritance hypothesis-correction + severity-correction + docs cascade + meta-methodology §10). 4 new S1499 candidate patterns pending third-arc validation for playbook v3 codification (D48 stability-probe gate + D45 recovery pattern + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent MET at 3-arc threshold — recommended for immediate codification). **D54 fold of S1405 F.E4-F.E10 addendum** landed at §5.4-§5.7 with residual-risk auditability note (compensating quality gate: parent-Claude 12/12 verifier-loop + sibling cross-verification from S1404 F.D4/D5/D8 anchor-drift + S1406 F.F3 arc-wide runtime-owner completion). **Arc close per playbook §16:** arc pin `pa-34d43795e1b24bd3` retired at arc-close (`updated_count: 60`); Group 1400 OPEN_ARCS row moved In-progress → Closed; ARCHITECTURE_INDEX v25 → v26 bump (this row + §1.29 row + frontmatter v26 preamble); post-merge 4-step docs cascade + `build_docs_provenance` per `feedback_docs_cascade_at_every_close.md`. Memory rules triggered: `feedback_xx99_meta_methodology_section.md` (§10 second application); `feedback_docs_cascade_at_every_close.md` (post-merge cascade); `feedback_rigby_sign_worker_instability_recovery.md` (S1499 SIGN pin worker-instability recovery via titles-only batches); `feedback_verify_before_deleting_dead_code.md` (T4 R.F3 (b) preserves F.F4a/b/c dormancy sub-patterns pending activation). **32 D-decisions ratified across 7 sessions** (D24-D55; only D55 required explicit Chris pick; 31 landed via "agree all" default-lean confirmation). Group 1400 arc CLOSED. | **First formal Group 1400 arc-close.** 8-doc arc: S1400 parent + 6 child audits (S1401-S1406) + S1499 canonical summary. ~11,715 lines across arc corpus. **First library canonical summary to arc-close with 4 of 9 lifecycle stages CRITICAL-INCOMPLETE** — Revenue pipeline emits scored opportunities but nothing beyond spider → scoring → draft composition converts to Revenue at mainline layer (Stage 4 delivery MISSING, Stage 5 ingestion MISSING, Stage 8 Revenue Received latent). **First library arc-close to resolve arc-wide runtime-owner MISSING UNANIMOUS 6/6 with peer-sibling JobContract shape** — D55 (ii) two sibling JobContracts precedent (contrast: S1304 §18 Documentation Manager AIEmployee single-employee shape). **First library canonical summary to fold Rigby SIGN worker-instability recovery pattern at the xx99 level itself** — S1499 SIGN pin worker-instability triggered D45 recovery to titles-only 2-3-verdict batches; 22/22 CONFIRM delivered across Q10-Q13. **Second application of playbook §11.3 §10 meta-methodology template** — all 5 S1399-codified patterns REPLICATED in Group 1400; 4 new S1499 candidate patterns pending third-arc validation. **First library canonical summary to fold a prior child's SIGN-blocked addendum at §5 synthesis** — D54 fold of S1405 F.E4-F.E10 (worker-instability blocked Batches 2-3 at S1405 close → deferred through D45/D51 → landed at §5.4-§5.7 via parent-Claude 12/12 compensating quality gate + sibling cross-verification). SIGN pin `pa-877f1919efaa48e4` retired post-fold. Arc pin `pa-34d43795e1b24bd3` retired at arc-close. Index v26 updated per §10.1 (this row + §1.29 row + frontmatter v26 preamble). |

| **S1500** (2026-07-01) | `domains/sports/1500_sports_domain_scoping.md` (§1.30) | **Arc-opening parent scoping doc for Research Group 1500 Sports / DBAO / Intelligence.** SECOND application of Chris's Phase 0 F.i/F.ii/F.iii methodology (Domain Definition / Existing Knowledge Inventory / Success Criteria) at §10/§11/§12 — applied UNCHANGED per D58 to preserve v3 promotion trigger integrity per S1400 D29 two-triggers rule. **6 Chris-locked decisions D56-D61 in single "agree all + D-6=(a)" ratification round 2026-07-01** via governance decision `81d7467e-add6-420f-aee9-60b67d7867e8` (governance_tool `decision_create` + `decision_decide` approve, status `acted`): D56 (domain slug = `sports`); D57 (parent-with-children arc shape — P1 S1501 Cat A Odds Ingestion & Normalization → P2 S1502 Cat B Prediction/Analytics Agents → P3 S1503 Cat C Wager Tracking & Outcome Verification → P4 S1504 Cat D Betting Content Pipeline → P5 S1505 Cat E Frontend Sports Surface → P6 S1506 Cat F Cross-Domain Integration Lens & Posture Decision Framing LAST → P7 S1599 xx99 canonical summary); D58 (Phase 0 methodology UNCHANGED — preserves v3 promotion trigger); D59 (load-bearing question = taxonomy + **posture decision framing + evidence plan**, NOT posture recommendation — Rigby refinement folded from pre-ratification pressure-test); D60 (anti-scope + Intelligence bounded to sports-scope only — no stock/legislation/narrative scope-drag per Rigby scope-magnet warning); D61 (DBAO = "Donkey Betz Analytics Ops" product-line codename option (a) — materialized as PostgreSQL `dbao` schema + `/ws/dbao/` WebSocket namespace + `VITE_DBAO_API_URL` env-var namespace + `X-DBAO-Client` HTTP header; NOT a mounted Django app). **Rigby pre-ratification pressure-test folded (4 refinements before Chris ratification):** (1) D-4 wording refined to "posture decision framing + evidence plan" (D59 final); (2) Rigby caution 1 (repeatability + discriminative value for v3 promotion) folded into §12.4 explicit criterion — stricter than "it ran twice"; (3) Rigby caution 2 (over-loading Phase 0 with posture selection) folded into D59 + §12.6 boundary; (4) Rigby caution 3 (Intelligence scope-magnet) folded into D60 + §3 non-candidates + §7 anti-scope + §10.1 boundary. **Runtime evidence anchored via 2 parallel Explore sub-agent sweeps against `main` HEAD `f7704586`:** Sports subsystem = 5 models across 2 files (`core/models_betting.py` + `core/models_odds_history.py`) + 4 services + 5 spiders + 4 market agents in `core/agents/markets/` + 6 Celery tasks (2 beat schedule at `core/celery.py:784,788`) + 9-tab `BettingPage.tsx` at `/betting` route + 2 Discord commands (`/odds`, `/bankroll`) + `/ws/dbao/` WebSocket + `dbao` PostgreSQL schema + `sports_intelligence: True` feature flag at `intelligence/views.py:44`; **zero body-system integration verified** in heart.py/lungs.py/circulatory.py. **Load-bearing structural finding CONFIRMED at code level:** S1274 §14 Finding #6 — `sports_odds` NOT a valid `SignalCluster.pattern_type` (Signal Engine declares 10 canonical pattern types at `core/models_signal_intelligence.py:75-86`; `sports_odds` valid only on legacy `SpiderData.data_type`). This is the runtime constraint Category F posture-decision evidence plan must confront per S1274 §12.3. **Locked child mission sequence rationale:** foundation (A odds ingestion) → consumers (B agents + C wagers + D content + E frontend) → integration lens (F LAST — consumes P1-P5 evidence to build posture-decision evidence plan owed to xx99 per D59). **Playbook §22 domain queue advanced:** Group 1300 closed S1399 + Group 1400 closed S1499 + Group 1500 opened S1500; next queued: Group 1600 (Content). **Fresh S1500 arc pin minted `pa-791b3db549a64e54`** via Rigby `session_tool.create_fresh` after retired Group 1400 arc pin `pa-34d43795e1b24bd3`; `tools/pa_local.sh:128` updated to fresh pin. Chris commit-gate expected via "commit it" 2026-07-01; commit landing on branch `docs/session-1500-sports-arc-open`. **Rigby SIGN cycle owed post-anchor-updates** with D48 preemptive stability-probe gate per S1405+S1406+S1499 3-arc pattern. Memory rules triggered: `feedback_no_parallel_research_arcs.md` (parallel S1500 attempt cleanly aborted by Chris before draft landed); `feedback_docs_cascade_at_every_close.md` (post-merge 4-step cascade + `build_docs_provenance` required). ARCHITECTURE_INDEX v26 → v27 bump same-commit: this §8 timeline row + §1.30 registration + frontmatter v27 preamble. OPEN_ARCS Group 1500 row moved Not-started → In-progress; parent-doc citation added. | **First library arc-open to explicitly test playbook v3 §11.1 promotion trigger per S1400 D29 two-triggers rule.** Group 1500 xx99 close determines v3 template promotion; Rigby caution 1 folded into §12.4 stricter criterion. **First library parent scoping doc to route S1274 §12.3 Product/Architecture Decision Point as evidence-plan framing (D59 refinement) rather than recommendation.** Phase 0 frames + specifies evidence; children gather; xx99 consolidates; Chris picks posture in post-arc ADR. **First library parent scoping doc to identify architecture isolation at runtime layer** — §10.2 confirms Sports has its own PostgreSQL schema (`dbao`) + WebSocket namespace (`/ws/dbao/`); island posture already partially adopted at runtime, not hypothetical. **First library parent scoping doc Chris-ratified via a single governance decision request** (`decision_create` + `decision_decide` approve → status `acted`; not conversational ratification). **First library arc-open to reference a paused parallel Claude Code session as memory-rule evidence** (`feedback_no_parallel_research_arcs.md` at Appendix; parallel S1500 attempt cleanly aborted by Chris before partial doc landed; S1500 opened with sole focus). Index v27 updated per §10.1 (this row + §1.30 row + frontmatter v27 preamble). |
| **S1501** (2026-07-01) | `domains/sports/1501_sports_odds_ingestion_normalization_audit.md` (§1.31) | **First child audit under Group 1500 Sports/DBAO/Intelligence arc — Category A Odds Ingestion & Normalization.** Playbook §11.2 20-section template + 6-parallel-Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 5 load-bearing claims (2 Sub-Agent 1 errors + 1 Sub-Agent 3 categorization error caught pre-SIGN; recorded §20.4). **First library child audit to apply the 4-item pre-brief mini-schema per surface per D62 = (a) propagate upfront** — Chris ratified D62 at S1501 open ("agree all" default lean matched Rigby's cycle-1 fold rationale — prevents schema drift, bounded 4-item annotation per surface, keeps P6/F focused on posture-decision brief rather than re-extraction). **Load-bearing findings:** (1) Silent choices-enum violation on `SpiderData.data_type` + `source_platform` writes for sports/prediction-market rows — HIGH severity confirmed Rigby SIGN cycle 1 Q5; extends S1274 §14 Finding #6 beyond `SignalCluster.pattern_type` to `SpiderData` itself (Django CharField `choices=` validates only in Forms/Admin, not at `Model.save()`). (2) No unified normalization service — parent §6 P1-parked issue #1 grep-verified NEGATIVE. Reclassified from HIGH to ARCHITECTURE-DECISION-PENDING per Rigby SIGN cycle 1 Q5 fold — §2.1 Cat A contract statement confirms normalization is NOT part of Cat A's Cat B contract. (3) `snapshot_odds_for_line_movement` docstring claims 20-min beat but has no `core/celery.py` entry — dormant vs docstring; reframed as "unimplemented expectation" per Rigby SIGN cycle 1 Q8 fold. (4) Discord `send_betting_digest` docstring says `#market-intelligence` but code routes to `CHANNEL_BOARDROOM` — docstring drift LOW. (5) Dual-store `SpiderData` vs `OddsSnapshot`/`GameLineHistory` — Rigby SIGN cycle 1 Q4 fold reframed as posture-decision-pending intentional read-optimized-vs-semantic separation rather than missing reconciler defect. **Rigby Full SIGN cycle 1** SIGN-with-edits at Medium-High confidence via fresh isolation pin `pa-a39069230ab64450` — 4 batches (1 stability probe + 3 substantive), zero worker-instability observed across all 4 substantive turns. **F1-F7 folds landed at commit-time** per Rigby cycle-1 requirements — F1 §13 maturity qualifier "WORKING (fragile contract) at ingestion, PARTIAL at normalization"; F2 §9 Q15 + §1 exec posture-decision-pending reframe cites S1274 §12.3 two-legitimate-postures precedent; F3 §17 dual-store SpiderData=semantic/log vs OddsSnapshot=UI-read-model clarification; F4 §15 debt severity adjustments (#1 HIGH confirmed; #2 → ARCHITECTURE-DECISION-PENDING; #6 LOW → MEDIUM); F5 §19 rank enum-resolution HIGH #2 + new HIGH #3 Downstream consumer inventory; F6 §14.3 unimplemented-expectation reframe; F7 §2.1 NEW Cat A contract statement (what Cat A guarantees today vs what it explicitly does NOT guarantee). **Rigby Full SIGN cycle 2 SIGN-clean at High confidence** — cycle 1 prediction accurate. **Do-not-regress notes for PR:** keep §2.1 Cat A contract statement + preserve posture-decision-pending framing throughout §9 Q15 + §17 + preserve enum-resolution HIGH severity in §15 debt #1 + §19 rank #2. **D48 preemptive stability-probe gate 4th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501 4-arc pattern (recommended for immediate codification alongside D45 titles-only recovery + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent per S1499 §10 meta-methodology). Fresh SIGN isolation pin `pa-a39069230ab64450` retired at S1501 close via Rigby `session_tool.retire`. Group 1500 arc pin `pa-791b3db549a64e54` RETAINED per playbook §16 — carries P2-P6 sequence + P7 xx99. ARCHITECTURE_INDEX v27 → v28 bump same-commit: this §8 timeline row + §1.31 registration + frontmatter v28 preamble. OPEN_ARCS Group 1500 row current-child field advances "S1500 arc-open + S1501 queued next" → "S1501 SIGN-clean cycle 2 (commit-gated) + S1502 queued next"; row remains In-progress. | **First library child audit to add a "Cat A contract statement" (§2.1) explicitly listing what the category guarantees today vs what it explicitly does NOT guarantee** — pattern candidate for playbook v3 §11.2 template addition if replicated at S1502-S1505. **First library child audit to catch a Django `choices=` silent-drift pattern** as a top-1 HIGH-severity finding via grep-verified NEGATIVE + parent-Claude direct-read verification, extending memory rule `feedback_llm_autofills_boolean_params_with_false.md` Django behavior pattern to research methodology. **First library child audit to inherit S1274 §14 Finding #6 at code level AND expand its scope** — S1274 named `SignalCluster.pattern_type` only; S1501 confirms + adds `SpiderData.data_type` + `SpiderData.source_platform` to the same silent-drift class. **First library child audit to explicitly reframe integration-gap language as posture-decision-pending language throughout** (per Rigby SIGN cycle 1 Q4 + Q8 folds F2 + F6 folded — cites S1274 §12.3 two-legitimate-postures precedent as licensing rationale; §9 Q15 + §1 exec summary + §17 all updated in sync). **First library child audit to codify D48 stability-probe gate as 4th-arm CODIFICATION-READY signal** for playbook v3 §15. Index v28 updated per §10.1 (this row + §1.31 row + frontmatter v28 preamble). |

| **S1502** (2026-07-02) | `domains/sports/1502_sports_prediction_analytics_agents_audit.md` (§1.32) | **Second child audit under Group 1500 Sports/DBAO/Intelligence arc — Category B Sports Prediction & Analytics Agents.** Playbook §11.2 20-section template + 6-parallel-Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 7 load-bearing claims (0 sub-agent errors caught this pass — cleaner than S1501 which caught 3; SA reports were internally consistent). **Second library child audit to apply the 4-item pre-brief mini-schema per surface per D62 = (a) propagate upfront** — validates D62 propagation-upfront directive at second sibling by producing consistent evidence shape without schema drift from S1501. **Load-bearing findings:** (1) Coordinator `.run()` vs `.execute()` asymmetry — HIGH operational risk; 4 of 5 agents bypass Layer 1 `AgentExecution` telemetry; only `SportsOddsAnalyst` at `sports_betting_coordinator.py:122` uses `.run()` with Session 1206 inline provenance comment; docstring at lines 22-33 asserts symmetric 5-agent pipeline — "false green" monitoring risk. (2) PA tool registry gap — MED-HIGH; `sports_odds_analyst` + `arbitrage_detector` absent from `tool_dispatcher.py:302-305` (only 4 of 6 sports agents registered). (3) Direct-consume filter is post-fetch in-memory list comprehension on dict return from `TheOddsSpider().fetch_data()`, NOT ORM query — parent §3.B claim clarified. (4) `ArbitrageDetector` does NOT persist to `sports.models.ArbitrageOpportunity` despite full admin+serializer+viewset triple — F5 fold KEPT AS DRIFT per Rigby cycle 1. (5) `SignalCluster.pattern_type` still lacks sports types + Cat B write side absent — HIGH architectural risk (biggest per Rigby cycle 1 verdict); F2 fold reframed to POSTURE-DECISION-PENDING per S1274 §12.3 precedent. (6) Zero Cat B → Cat C outcome-to-agent learning loop — F3 fold reframed to POSTURE-DECISION-PENDING "closed-loop learning deferred". (7) Zero Memory Domain (S1300) bridge — F4 fold reframed to POSTURE-DECISION-PENDING "context-agnostic by construction". (8) `LineMovementAnalyzer` + `PredictionMarketAnalyst` scope-boundary — called by coordinator + registered as PA tool but not in parent §3.B Cat B scope; owed to xx99 reconciliation. (9) Coordinator continue-on-error failure semantics — F8 fold reframed to INTENTIONAL-OR-DRIFT NEEDING CONTRACT STATEMENT per S1501 F6 "unimplemented expectation" precedent. **Rigby Full SIGN cycle 1** SIGN-with-edits at Medium confidence via fresh isolation pin `pa-64c019d7e6685d31` — 4 batches (1 stability probe via `cockpit_tool.worker_health` + 3 substantive), zero worker-instability observed across all 4 turns. **F1-F12 folds landed at commit-time** — F1 §7.1 explicit call-chain block + §19 rank re-order PA registry rank 5→4; F2-F4 posture-decision-pending reframes for Findings 5-7; F5 kept F4 ArbitrageOpportunity as DRIFT per Rigby recommendation; F6 §15 fixture-identity added as debt #12; F7 §1 operational-vs-architectural risk axis + per-finding labels; F8 continue-on-error reframe; F9 Session-1205 language softened; F10 SportsBettingBrief model verified via grep + §4.6 subsection added + §20.3 UNKNOWN resolved; F11 REST endpoint router registration verified via grep of `core/urls.py:3083-3128`; F12 §5.1 direct-consume filter cite tightened with verbatim shape. **Rigby Full SIGN cycle 2 SIGN-clean at High confidence** — cycle 1 prediction accurate. **Do-not-regress notes for PR:** keep §2.1 Cat B contract statement + preserve posture-decision-pending framing throughout §1 Findings 5-7 + preserve F1 explicit call-chain block + F6 fixture-identity as explicit debt matrix item + F7 operational-vs-architectural risk axis. **D48 preemptive stability-probe gate 5th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502 5-arc pattern (strengthens the immediate codification recommendation from S1501 4-arc threshold). Fresh SIGN isolation pin `pa-64c019d7e6685d31` retired at S1502 close via Rigby `session_tool.retire`. Group 1500 arc pin `pa-791b3db549a64e54` RETAINED per playbook §16 — carries P3-P6 sequence + P7 xx99. ARCHITECTURE_INDEX v28 → v29 bump same-commit: this §8 timeline row + §1.32 registration + frontmatter v29 preamble. OPEN_ARCS Group 1500 row current-child field advances "S1501 SIGN-clean cycle 2 (commit-gated) + S1502 queued next" → "S1502 SIGN-clean cycle 2 (commit-gated) + S1503 queued next"; row remains In-progress. | **First library child audit to distinguish OPERATIONAL RISK from ARCHITECTURAL RISK on per-finding basis** (F7 fold — per Rigby SIGN cycle 1 Q6 fold; propagates to §14 drift + §15 debt + §19 future research queue). **First library child audit to add explicit call-chain block** in flow section (F1 fold — per Rigby SIGN cycle 1 Q1 must-change-before-canonical). **First library child audit to inherit a sibling's contract statement as load-bearing INPUT** — S1501 §2.1 Cat A contract statement was directly cited as Cat B's runtime dependency; Cat B §2.1 documents which non-guarantees it fills vs extends. **First library child audit to catch a coordinator method-signature asymmetry** as a load-bearing HIGH operational-risk finding via direct read + grep verification — extends S1501 §14.1 Django `choices=` silent-drift pattern to a behavioral-invariance drift class. **First library child audit to reach a "PARTIAL (armed but under-instrumented)" maturity verdict** — captures the shape where code + beat + persistence are complete but self-instrumentation + downstream signal-emission are partial adoption; extends S1501 "WORKING (fragile contract) at ingestion, PARTIAL at normalization" two-tier pattern to single-tier observation-invariance pattern. **First library child audit to catch a Django admin+serializer+viewset triple with zero producer** — `ArbitrageOpportunity` at `sports/models.py:1292`. **First library child audit to codify D48 stability-probe gate as 5th-arm CODIFICATION-READY signal** for playbook v3 §15. Index v29 updated per §10.1 (this row + §1.32 row + frontmatter v29 preamble). |

| **S1503** (2026-07-02) | `domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md` (§1.33) | **Third child audit under Group 1500 Sports/DBAO/Intelligence arc — Category C Sports Wager Tracking & Outcome Verification.** Playbook §11.2 20-section template + 6-parallel-Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 7 load-bearing claims (2 Sub-agent 6 errors caught pre-SIGN: line count 340→480 + line reference 28→26) + parent-Claude Rigby ORM probe BEFORE draft integration (first library child audit to apply this pattern). **Third library child audit to apply the 4-item pre-brief mini-schema per surface per D62 = (a) propagate upfront** — third sibling completes D62 propagation-upfront validation across S1501+S1502+S1503 3-arc pattern with consistent evidence shape and no schema drift. **Load-bearing findings (10):** (1) **CRITICAL operational — `verify_betting_outcomes` unscheduled AND zero-fire** — grep of `core/celery.py` for task name returns zero + grep of `docs/AUDIT_FINDINGS.md` §12 canonical deferred list returns zero + BOTH independent Rigby ORM probes (parent-Claude on `pa-791b3db549a64e54` pre-SIGN + Rigby SIGN cycle 1 batch 3 Q8 on `pa-8ce5f949bed5e093`) returned `PeriodicTask.count() = 0` AND `CeleryTaskEvent 30d count = 0` for both task variants (`core.tasks.verify_betting_outcomes` + `sports.verify_betting_outcomes`). Docstring at `core/tasks.py:6129` claims "Runs every 2 hours" — phantom behavior. Session 1244 PR #2687 fixed sports-queue parity but did NOT restore beat entry. Session 1165 added retry policy that never fires. Entire feature silently broken. (2) **HIGH architectural POSTURE-DECISION-PENDING** per S1502 F3 precedent — Zero Cat C → Cat B outcome-feedback loop; answers S1502 §1 Finding 6 explicitly; F9 fold "bridge owns learning writes" as default posture statement. (3) HIGH architectural POSTURE-DECISION-PENDING per S1502 F2 precedent — Zero Cat C → Signal Engine emission; extends S1274 §14 Finding #6 into Cat C consumer side. (4) MED-HIGH operational — Two task definitions for same feature (core.tasks + sports.tasks) with different behavior wrappers. (5) MED (F5 fold downgrade from MED-HIGH) — Discord `/bankroll` reads `Bankroll` model (not `BettingStats`) — dual aggregation surface; empirical divergence probe deferred to §19.2 #6. (6) MED-HIGH POSTURE-DECISION-PENDING per S1502 F4 precedent — Zero Cat C → Memory Domain (S1300) bridge beyond `AgentMemory` + `UserAgentLearning`. (7) MED architectural — `PlacedWagerLeg.event_id` string coupling to Odds API dict return shape (replicates S1502 §1 Finding 3 direct-consume dict-shape pattern on the Cat C side). (8) MED POSTURE-DECISION-PENDING — Cat C is a leaf domain (zero inbound FKs across codebase); structural signature of "sports as island". (9) MED-HIGH operational — Zero test coverage across `core/tests/` for Cat C surface. (10) MED operational — No concurrency control on `_settle_wager()` (no `select_for_update()` / no `@transaction.atomic()` wrapper). **Rigby Full SIGN cycle 1** SIGN-with-edits at High confidence via fresh isolation pin `pa-8ce5f949bed5e093` — 4 batches (1 warm-up probe via `cockpit_tool.worker_health` confirming 4 workers online + 3 substantive SIGN batches Q1-Q3 + Q4-Q6 + Q7-Q9), **zero worker-instability observed across all 4 turns** (D48 6th arm — cleanest arm of the pattern). **F1-F14 folds landed at commit-time** — F1 §5.4 additional Cat C read surfaces addendum; F2 §5.5 Bankroll adjacency touchpoints bounded subsection; F3 §1 executive summary compounding-risk observation (Finding 1 + Finding 5 combo) + orchestration+idempotency-as-readiness-gate reframe; F4 §14.1 + §20.5 independent Rigby SIGN cycle 1 batch 3 Q8 ORM probe block (do-not-regress); F5 §14.5 + §15.10 severity MED-HIGH → MED downgrade with "until divergence proven" rationale; F6 §15.13 new debt item timezone correctness on `commence_time`; F7 §15.14 new debt item idempotency + replay safety as PRE-RESTORE-BEAT GATE (HIGH-severity); F8 §15.15 new debt item Decimal quantization policy; F9 §14.2 + §14.3 "bridge owns learning writes" default posture statement; F10 §19.1 CRITICAL tier reorganization (beat-schedule remediation + concurrency-safety hardening as PRE-RESTORE-BEAT GATE moved from HIGH/MED to CRITICAL); F11 §19.2 #5 new research item operational cadence study (Odds API rate limits + score availability lag); F12 fixture identity strategy already at §19.4 (no move); F13 §19.3 #9 new research item operator tooling (PA tool + management command for dry-run / recalc / single-wager modes); F14 §5.5 dual-Bankroll footnote clarifying `Bankroll` in `core/models_bankroll.py:19` PLUS `BankrollManagement` in `sports/models.py:1032`. **Cycle 2 SIGN-clean at High confidence anticipated post-fold-land** matches S1501 + S1502 cycle-1-predict-cycle-2 pattern. **Do-not-regress notes for PR:** preserve §2.1 Cat C contract statement + preserve F9 "bridge owns learning writes" framing throughout §14.2 + §14.3 + preserve F4 independent Rigby ORM probe block in §14.1 + §20.5 + preserve F7 idempotency-as-pre-restore-beat-gate framing in §15.14 + §19.1 (do NOT let CRITICAL #1 land without CRITICAL #2 landing first) + preserve F10 §19.1 CRITICAL tier ordering. **D48 preemptive stability-probe gate 6th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502+S1503 6-arc pattern (further strengthens the immediate codification recommendation from S1502 5-arc threshold; cleanest arm — zero instability across 4 turns). Fresh SIGN isolation pin `pa-8ce5f949bed5e093` retires at S1503 close via Rigby `session_tool.retire`. Group 1500 arc pin `pa-791b3db549a64e54` RETAINED per playbook §16 — carries P4-P6 sequence + P7 xx99. ARCHITECTURE_INDEX v29 → v30 bump same-commit: this §8 timeline row + §1.33 registration + frontmatter v30 preamble. OPEN_ARCS Group 1500 row current-child field advances "S1502 SIGN-clean cycle 2 (commit-gated) + S1503 queued next" → "S1503 SIGN-with-edits cycle 1 (folds landed, cycle 2 anticipated) + S1504 queued next"; row remains In-progress. | **First library child audit to apply Rigby ORM probe as parent-Claude verifier-loop tool BEFORE SIGN routing** — extends S1401-S1406 verifier tool chain (file-line direct-reads + broader-grep + model-context disambiguation + provenance-stamp ORM probe) with a BEFORE-SIGN ORM verification step; pattern candidate for playbook v3 §14 evidence-rules addition. **First library child audit to catch a Celery task at CRITICAL zero-fire status via 3-axis probe** (grep of `core/celery.py` for zero-hit + grep of `docs/AUDIT_FINDINGS.md` §12 for zero-hit + 2 independent ORM probes returning 0/0). **First library child audit to reach "PARTIAL (armed but zero-fire)" maturity verdict** — third distinguishing shape after S1501 "WORKING (fragile contract) at ingestion, PARTIAL at normalization" + S1502 "PARTIAL (armed but under-instrumented)"; captures features that are code-complete + surface-complete but scheduling-broken. **First library child audit to introduce compounding-risk observation** (F3 fold — Finding 1 + Finding 5 combo produces stale + inconsistent user-facing views with no "system is behind" signal). **First library child audit to add "pre-restore-beat gate" concept** — §15.14 idempotency + replay safety as HIGH-severity operational debt that MUST land BEFORE beat-schedule remediation; §19.1 CRITICAL tier reorganization enforces ordering. **First library child audit with 6-arc D48 pattern entirely clean stability probe** — zero worker-instability across 4 substantive SIGN batches. **First library child audit to have TWO independent Rigby ORM probes on TWO different pins both returning zero for same CRITICAL claim** — evidence-doubling technique candidate for playbook v3 §14 addition. Index v30 updated per §10.1 (this row + §1.33 row + frontmatter v30 preamble). |

| **S1504** (2026-07-02) | `domains/sports/1504_sports_betting_content_pipeline_audit.md` (§1.34) | **Fourth child audit under Group 1500 Sports/DBAO/Intelligence arc — Category D Sports Betting Content Pipeline.** Playbook §11.2 20-section template + 6-parallel-Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 5 load-bearing claims (4 verifier-loop corrections landed pre-SIGN: SportsBettingBrief model definition VERIFIED at core/models_unified_system.py:18394 — Sub-agent 3 was wrong "no model definition"; SportsBettingBrief writer sites VERIFIED = 2 including Session 1000 multi-desk — Sub-agent 1 was wrong "Cat D-exclusive"; SportsContentContextBuilder invocation chain VERIFIED via 3 consumer surfaces — Sub-agent 6 marked UNKNOWN; get_betting_brief REST behavior VERIFIED as coordinator direct-call not model read — Sub-agents 3 + 4 disagreed) + parent-Claude Rigby ORM probe BEFORE draft integration (second library application of S1503-first-applied pattern). **Fourth library child audit to apply the 4-item pre-brief mini-schema per surface per D62 = (a) propagate upfront** — fourth sibling extends D62 propagation-upfront validation from S1501+S1502+S1503 3-arc pattern to 4-arc pattern; embedded at §4.4 + §5.6 + §6.6 + §8.6 + §15.16. **Load-bearing findings (10):** (1) **CRITICAL operational — `daily_betting_digest` unscheduled AND zero-fire** — 3-axis probe: grep of `core/celery.py` for `daily_betting_digest` → zero beat entries + grep of `docs/AUDIT_FINDINGS.md` §12 canonical deferred list → zero matches + Rigby ORM probe on `pa-791b3db549a64e54` returned `CeleryTaskEvent 30d count = 0`. Docstring at `core/tasks_financial.py:1912` "Scheduled to run at 8 AM MST daily" is phantom behavior. S1503 §14.1 pattern replicated in Cat D scope. (2) **CRITICAL architectural — `SportsBettingBrief` model write-only-and-forgotten** — 2 writers (`core/tasks_content.py:3150` Cat D daily + `core/tasks.py:12187` Session 1000 multi-desk), 0 readers (grep-verified pre-SIGN); REST endpoint `get_betting_brief` at `core/views_odds_sports.py:3237` bypasses persisted model + calls coordinator directly. NEW pattern for the arc. (3) **HIGH POSTURE-DECISION-PENDING** per S1502 F3 / S1503 F9 precedent — Zero Cat D → Cat B outcome-feedback loop; F11 fold clarifier "no owning bridge implementation was located." (4) **HIGH POSTURE-DECISION-PENDING** per S1502 F2 / S1503 §14.3 precedent — Zero Cat D → Signal Engine emission; F11 fold clarifier. (5) MED (F6 fold demote from HIGH) — `generate_daily_betting_brief` docstring "twice daily" vs runtime once-daily (Rigby ORM 5 SUCCESS fires at 07:00 MT daily); F6 rationale "less risky than 'doesn't run / duplicates / no tests / no consumers.'" (6) MED-HIGH operational + architectural (F1 fold elevation) — `run_all_desks_intelligence` cross-domain writer bridge to `SportsBettingBrief` without dedup; two writers on same table without unique constraint on `brief_date`. (7) MED architectural — Discord `/odds` + digest + intelligence-hook BYPASS `SportsContentContextBuilder`; two disconnected content-generation surfaces; F2 fold reframe from TRANSITIVELY-COUPLED to HOT-PATH-CHOKE-POINT for content/PA + BYPASSED for Discord fast path. (8) MED POSTURE-DECISION-PENDING per S1502 F4 precedent — Zero Cat D → Memory Domain (S1300) bridge. (9) HIGH operational (F4 fold promote from MED-HIGH; further promoted to CRITICAL tier in §19 per Rigby batch 2 Q5 + batch 3 Q7 F3 "reliability multiplier" framing) — Zero dedicated test coverage. (10) MED operational — No PA tool for triggering brief / digest / manual regeneration. **Rigby Full SIGN cycle 1** SIGN-with-edits at Medium-High confidence via fresh isolation pin `pa-af2bf7f2d1a0ef61` — 4 substantive SIGN turns (1 warmup + 3 SIGN batches Q1-Q3 + Q4-Q6 + Q7-Q9), zero worker-instability observed (**D48 7th arm — matches S1503 6th-arm cleanest arm pattern**). **F1-F11 folds landed at commit-time** — F1 §1 Finding 6 + §7.2 heading `run_all_desks_intelligence` cross-domain writer bridge elevation; F2 §5.1 + §7.6 + §13.2 SportsContentContextBuilder HOT-PATH-CHOKE-POINT reframe (from TRANSITIVELY-COUPLED); F3 §4.2 LegacySpiderData shared-table Cat B/C bridge surface risk elevation; F4 §1 Finding 9 zero test coverage promoted MED-HIGH → HIGH + §15.12 promoted → CRITICAL + §19.1 #3 added to CRITICAL tier; F5 §15.5 digest idempotency PRE-RESTORE-BEAT gate promoted MED-HIGH → CRITICAL + §19.1 #2 sequence-gate; F6 §1 Finding 5 + §14.2 + §15.3 docstring cadence drift demoted HIGH → MED across all three sites + §19.3 #9 reprioritized; F7 §1 executive-summary risk ordering strengthened; F8 §19.1 CRITICAL tier reordered to 5-item dependency ordering; F9 §13 + §1 maturity verdict + §13.2 table refined to distinguish WORKING (fire-verified) from PRESENT + SCHEDULED (runtime not verified) for `/odds` + intelligence-hook + §19.2 #8 new operational instrumentation task; F10 §1 executive-summary opening rewritten from "owed to xx99" placeholder to concrete handoff target (Cat F P6 S1506 + xx99 S1599); F11 §14.4 + §14.5 gained "no owning bridge implementation was located" clarifier + §19.2 #6 + §19.4 #14/15 additional callouts. **First library child audit where Rigby SIGN cycle 1 batch 1 required re-request** for verdict text — initial response was tool-heavy (10 repo_tool.search invocations) without verdict summary; recovery via one-line "please give me the Q1/Q2/Q3 verdict text" ping delivered. Recovery pattern candidate for playbook v3 §15 alongside D45 titles-only recovery. **Cycle 2 SIGN-clean at High confidence anticipated post-fold-land** matches S1501+S1502+S1503 cycle-1-predict-cycle-2 pattern. **Do-not-regress notes for PR:** preserve §2.1 Cat D contract statement (10-item non-guarantees) + preserve F1-F11 folds per §20.8 detailed enumeration (see §1.34 audit registration for full do-not-regress list). **D48 preemptive stability-probe gate 7th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502+S1503+S1504 7-arc pattern — further strengthens the immediate codification recommendation from S1503 6-arc threshold; zero worker-instability across 4 SIGN turns. Fresh SIGN isolation pin `pa-af2bf7f2d1a0ef61` retires at S1504 close via Rigby `session_tool.retire`. Group 1500 arc pin `pa-791b3db549a64e54` RETAINED per playbook §16 — carries P5-P6 sequence + P7 xx99. ARCHITECTURE_INDEX v30 → v31 bump same-commit: this §8 timeline row + §1.34 registration + frontmatter v31 preamble. OPEN_ARCS Group 1500 row current-child field advances "S1503 SIGN-with-edits cycle 1 (folds landed, cycle 2 anticipated) + S1504 queued next" → "S1504 SIGN-with-edits cycle 1 (F1-F11 folds landed, cycle 2 anticipated) + S1505 queued next"; row remains In-progress. | **First library child audit to catch a CRITICAL write-only-and-forgotten persistence pattern** — introduces a NEW pattern class (write path present + persistence artifact present + zero readers + REST bypass) distinct from S1503 §14.1 zero-fire pattern. Diagnostic criteria replicable to future audits (e.g., stocks + blockchain + narrative desk brief models produced by Session 1000). **Second library application** of Rigby ORM probe as parent-Claude verifier-loop tool BEFORE SIGN routing — strengthens the pattern's replicability evidence for playbook v3 §14 codification. **First library child audit to identify a HOT-PATH-CHOKE-POINT service that is BYPASSED by a sibling fast path in the same domain** — `SportsContentContextBuilder` for content/PA vs BYPASSED for Discord fast path; introduces the "two disconnected content-generation surfaces" pattern class. **First library child audit to reach a "mixed maturity" hybrid verdict with FIVE distinguishable component states** — WORKING (fire-verified) + PRESENT + SCHEDULED (runtime not verified) + BROKEN/DORMANT + WRITE-ONLY-FORGOTTEN + HOT-PATH-CHOKE-POINT-BYPASSED. **First library child audit to distinguish "task fired" from "task semantically correct"** — F9 fold Rigby batch 3 Q8 pressure-test: Celery SUCCESS counts prove task fired but not Discord post + user interaction correctness; runtime instrumentation follow-on task added (§19.2 #8). **First library child audit to catch a docstring cadence lie that survives 30d Rigby ORM SUCCESS-fire evidence** — F9 discipline generalizes to any beat-scheduled task claiming multi-fire cadence. **First library child audit to require "no owning bridge implementation was located" clarifier as SIGN-with-edits requirement** (F11 fold Rigby batch 3 Q8) — distinguishes "not built / not wired" from "intentionally delegated with evidence" in POSTURE-DECISION-PENDING findings. Pattern candidate for playbook v3 §11.2 template update. **First library child audit to identify a shared-persistence table with two-writer contested ownership across research arcs** — Cat D shim + Session 1000 pipeline share SportsBettingBrief; cross-domain writer bridge concept introduced (F1 fold). **First library child audit to codify D48 stability-probe gate as 7th-arm CODIFICATION-READY signal**. **First library child audit where Rigby SIGN cycle 1 batch 1 required verdict-text re-request** — recovery pattern candidate for playbook v3 §15 alongside D45. Index v31 updated per §10.1 (this row + §1.34 row + frontmatter v31 preamble). |

| **S1600** (2026-07-02) | `domains/content/1600_content_domain_scoping.md` (§1.38) | **Group 1600 Content / Deliverables / Publishing arc OPENED at S1600 parent Phase 0 scoping.** Playbook §11.1 template applied verbatim + Chris's Phase 0 F.i/F.ii/F.iii methodology **THIRD application** at §10/§11/§12 (unchanged per D68 to preserve v3 promotion trigger integrity per D29/D58 precedent chain; playbook v3 §11.1 template promotion **already TRIGGERED at S1599 close** per §12.4 discriminative-value criterion check 4-of-4 evidence types satisfied). Two parallel Explore sub-agents per §13 sweep (Agent 1 Content Pipeline surface + Agent 2 Deliverables + Publishing surface) + parent-Claude verifier-loop per §14 on 3 load-bearing pre-Explore claims (PublishGate class + Discord broadcast + Celery beat entries all verified; 2 sub-agent errors caught). **All 8 Chris decisions locked in single "agree all + D-6=(a)" ratification round via governance decision `2c469638-643d-4477-a8ea-1766b552eebe` (`decision_create` + `decision_decide` action approve → status `acted`):** D63 slug=`content`; D64 parent-with-children (P1-P6 + P7 xx99 at S1699); **D65a Deliverable canonicalization** posture-decision framing (canonical container vs parallel-schema-siblings); **D65b PublishGate canonicalization** posture-decision framing (single canonical gate vs per-variant/channel); **D65c Lifecycle transition ownership** posture-decision framing (canonical orchestrator vs variant-owned rails); D66 child mission sequence per F3 P3↔P4 swap (P1 Cat A → P2 Cat B → **P3 Cat D (moved from P4)** → **P4 Cat C (moved from P3)** → P5 Cat E → P6 Cat F → P7 xx99); D67 §7 anti-scope 18 items (F5 fold 12→18); D68 methodology UNCHANGED + D62=(a) 6-sibling mini-schema propagation-upfront + F8/F10 folds adopted. **Rigby Light SIGN cycle 1 → cycle 2 SIGN-clean at High confidence** on fresh S1600 arc pin `pa-f52acf3f8d394faa` (minted via `session_tool.create_fresh` at S1600 open; `tools/pa_local.sh:128` rotated from retired Group 1500 arc pin `pa-791b3db549a64e54`); **F1-F12 folds landed at commit-time** — F1 §3 Cat A ClaimsPack boundary rule; F2 §3 Cat C/D crisp boundary rules; F3 §5 P3↔P4 swap Cat D BEFORE Cat C with embedded dependency clauses; F4 §8 D65 split into D65a/D65b/D65c three orthogonal axes; F5 §7 anti-scope 12→18 items; F6 §12.4 discriminative-value tightening with required decision-discriminative proof + required disconfirming evidence item; F7 §12.5 Deliverable Lifecycle Traceability Table 10→12 stages with normalization/canonicalization + eligibility/packaging-gate; F8 one-sentence boundary rule per category; F9 binary posture framing with mushy-hybrid disallowed; F10 D66 dependency-clause embedding; F11 §3 Cat E feedback-hazard note; F12 ClaimsPack centrality preserved via F1. **Load-bearing runtime evidence anchored via 2 parallel Explore sub-agent sweeps at S1600 open against `main` HEAD `82e8efe6`:** Content Pipeline surface confirmed 6+ services + 6+ models (Deliverable base + 5 parallel deliverable-shaped variants: SelfBlog + OutreachDraft + ClosePack + SportsBettingBrief + BlockchainAuditBrief) + 4 Rigby PA-tool surfaces + 6+ Celery beat entries + Discord broadcast surface with 12 channel constants + Frontend BlogViewerPage + ContentPage + blogsApi + deliverablesApi. **Cross-arc handoffs owed to Group 1600:** S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN CRITICAL + S1504 §5.1 SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS HIGH + S1402 F.B1 Revenue OutreachDraft delivery ZERO outbound channel HIGH + S1403 F.C4 ContentEngagement docstring drift HIGH + S1502 §14.3 SignalCluster pattern_type consumer-side gap 6-arc COMPLETED per S1599 §4.11 + S1499 D55 (ii) Revenue Employee + Income/Jobs Employee JobContract split precedent. **Locked child mission sequence (D66 F3-fold-swap):** P1 S1601 Cat A ClaimsPack + Content Deliberation Pipeline v2 → P2 S1602 Cat B Content Reviewers + Decision Enforcement → P3 S1603 Cat D Deliverable Base + Specialized Variants → P4 S1604 Cat C PublishGate + Publish Rails → P5 S1605 Cat E Rigby-Facing Content PA Tooling + Approval UX → P6 S1606 Cat F Cross-Domain Integration Lens & Posture Decision Framing (LAST — consumes P1-P5 evidence + produces xx99 §5 D65a/D65b/D65c-analog three-axis posture-decision evidence plan per parent §12.1 F.iii item 3) → P7 S1699 xx99 canonical summary (**fourth application** of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second + S1599 third). Row moves Not-started → In-progress this commit. | Feeds S1601 Cat A ClaimsPack + Content Deliberation Pipeline v2 child audit next per D66 P1 slot; Cat A canonical decision "what claims + which sources ground the deliberation?"; Cat B/D/C/E/F children consume Cat A evidence baseline; xx99 §5 posture-decision brief consumes P1-P5 evidence + Cat F evidence plan verbatim per D65a/D65b/D65c-analog three-axis framing; xx99 §7 anti-scope 18 items (F5-fold expansion from 12) prevents scope-drag during audits; xx99 §10.2 discriminative-value criterion F6-fold-tightened check with required decision-discriminative proof + required disconfirming evidence item confirms whether third application produced discriminative value at arc-close bar; xx99 §12.5 Deliverable Lifecycle Traceability Table 12-stage F7-fold-expansion consumed as consolidated deliverable per D66 P7 slot. |

| **S1601** (2026-07-02) | `domains/content/1601_content_claims_pack_deliberation_pipeline_v2_audit.md` (§1.39) | **First child audit under Group 1600 Content / Deliverables / Publishing arc — Category A ClaimsPack + Content Deliberation Pipeline v2.** Playbook §11.2 20-section template + 6-parallel-Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 6 load-bearing pre-Explore claims (all verified pre-Explore fire); applies D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront per parent D68 F8/F10 folds at §4.8 + §5.6 + §6.5 + §8.5. **Load-bearing question resolutions (parent §3 Cat A):** Q1 Citation integrity posture — Cat A enforces `claims_count == 0` gate only at `core/services/content_deliberation_runner.py:99-103`; NO per-claim `[C-xxxxxxxxxx]`-in-draft regex verifier code-side; Cat B FactCheckReviewer is LLM prompt-based, not code-enforced. Q2 v2 pipeline runtime posture — **strictly on-demand**; grep-verified ZERO beat entries fire `ContentDeliberationRunner.run_blog()`; triggers only via REST `POST /api/v1/research/self-blog/generate-v2/` + PA tool `blog_tool action=generate` (no topic) + Celery task `generate_self_blog_deliberation_task.delay()` dispatch. **Load-bearing findings (8, per Rigby SIGN cycle 1 F2+F4 fold reordering):** (1) **RIGHIEST OVERALL — HIGH cross-tenant / cross-workspace data exposure risk** — `_from_user_documents` at `core/services/claims_pack_builder.py:245` calls `DocumentEmbedding.cosine_similarity_search(query_vector, limit=10, min_similarity=0.4)` with NO `user_id`/`workspace_id`; `content/models.py:879-887` filters only `document__file_path__isnull=False` (orphan exclusion). Pipeline could ground drafts in another workspace's/user's documents. Owed to xx99 D65a evidence plan; T1 R.CONTENT.RAG-SCOPE post-arc ADR. (2) **HIGH** — Per-claim citation-in-draft verification absent code-side; only non-empty ClaimsPack gate at :99-103; FactCheckReviewer prompt-based. Owed to xx99 D65b evidence plan; T1 R.CONTENT.CITATION-INTEGRITY. (3) **HIGH (Rigby F2 fold elevated MEDIUM → HIGH)** — Silent partial-source failure = truth/evidence integrity degradation without explicit degraded-status contract; `claims_pack_builder.py:70-85` swallows three source exceptions with `logger.warning`; Cat A can lose entire evidence lane silently and pass `claims_count == 0` gate. (4) **MEDIUM** — Direct ORM reads (`LegacySpiderData` at :117, `SignalCluster` at :192, `DeliberationSession` at `content_deliberation_runner.py:343`) bypass service layer. (5) **MEDIUM** — SignalCluster `pattern_type` consumer-side gap CONFIRMED for Cat A (`grep pattern_type` in `claims_pack_builder.py` → 0 matches); extends S1502 §14.3 6-arc COMPLETED pattern to Cat A. (6) **LOW** — `SpiderData` vs `LegacySpiderData` naming drift (parent §3 + topic doc vs runtime `LegacySpiderData` at `core/models_unified_system.py:3691`). (7) **LOW/POSTURE-PENDING** — Rewrite pass hard-capped at 1 iter at `content_deliberation_runner.py:107-116`; no config knob (owed to D65c lifecycle-transition-ownership evidence plan). (8) **LOW/POSTURE-PENDING** — `_build_operational_context` module boundary at `content_deliberation_runner.py:191`; Session 1001 telemetry injection helper in `core/tasks.py:5560` vs `core/services/`. **D65a HEADLINE evidence for xx99 (Rigby F1 fold reframed):** `SelfBlog.objects.create` at `content_deliberation_runner.py:401` bypasses `deliverable_factory` — **canonicalization debt Cat A flags as evidence input to Chris-gated posture-decision brief, NOT proof of intentional island architecture**. Rigby SIGN cycle 1 SIGN-with-edits at Medium confidence on fresh isolation pin `pa-9f075a024552b663`; F1-F6 folds landed pre-commit — F1 SelfBlog canonicalization-debt reframe; F2 silent-partial-source severity MEDIUM → HIGH; F3 RAG scope explicit cross-tenant/workspace framing; F4 RAG scope = riskiest overall Cat A finding elevation; F5 fix "ZERO writes to Cat B/C/D" Exec Summary contradiction (corrected to "ZERO writes to Cat B/C; ONE write to Cat D (SelfBlog) as persistence handoff"); F6 verification-report endpoint boundary caution pin at `core/views_deliberation.py:394-561`. **D48 preemptive stability-probe gate 10th-arm outcome:** SIGN cycle 1 held clean at Medium confidence in three turns on fresh isolation pin; no worker instability observed; sub-pattern extension anticipated to five-consecutive-fully-clean-arms **S1503+S1504+S1505+S1506+S1601** per D48 gate expectation at S1600 open. |

| **S1603** (2026-07-02) | `domains/content/1603_content_deliverable_base_variants_audit.md` (§1.41) | **Third child audit under Group 1600 Content / Deliverables / Publishing arc — Category D Deliverable Base + Specialized Variants.** Playbook §11.2 20-section template + 6-parallel-Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 22 pre-Explore + 6 post-Explore load-bearing binary claims (all grep-verified against `main` HEAD `b8269101`). Applies D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront per parent D68 F8/F10 folds at §4.8 + §5.6 + §6.5 + §8.5 (third sibling of Group 1600 to propagate the pattern upfront after S1601 first + S1602 second). **Answers parent §3 D four evidence axes A1-A4:** A1 Deliverable canonicalization scope; A2 PublishGate canonicalization scope; A3 central factory scope; A4 `publish_intent` enum coverage. **D65a HEADLINE structural evidence for xx99:** grep-verified NO reverse FKs from any variant to Deliverable base — all 5 variants (SelfBlog at `models_unified_system.py:20611` + OutreachDraft at `models_outreach.py:18` + ClosePack at `models_close_pack.py:20` + SportsBettingBrief at `models_unified_system.py:18394` + BlockchainAuditBrief at `models_unified_system.py:18435`) are **structural islands** at the FK layer; only uni-directional `Deliverable.self_blog` FK at :192-199 + `Deliverable.podcast_episode` FK at :200-207 (Session 862). `publish_intent` enum only on Deliverable base :131-136 (grep-negative on 5 variant model files — D65a structural blocker for integration posture). **F6 Rigby fold reframe** from binary "island posture = missing integration" to **3-category neutral taxonomy** (envelope-integrated: 2 objects / standalone-by-design provisional: 2 objects / unfinished-orphan CRITICAL: 2 objects). **Central factory adoption ~98% at Deliverable base level** (`create_deliverable` at `deliverable_factory.py:752` — F0 pre-Explore drift correction: parent §3 D cited :1269, actual `def create_deliverable(` at :752; :1269 is `Deliverable.objects.create(**kwargs)` inside function body atomic-transaction block); 2 legitimate production Deliverable bypasses (`views_deliverables.py:305` clone + `workflow_orchestration_agent.py:5107` morning-brief); **0% factory adoption at variant models**. **F1 RESOLVED via parent-Claude direct-read verification:** Rigby SIGN Batch A flagged `real_job_execution_consumer.py:99/200` `async def create_deliverable(self, job)` as potential shadow factory bypass; direct-read at :200-237 confirms method returns plain Python dict for demo WebSocket UI simulation, never touches Django ORM, never persists Deliverable row. **Name collision, not shadow factory bypass.** Factory adoption metric of 98%+ REMAINS ACCURATE. **F0b post-Explore correction:** Explore Agent 6 initially flagged `content_hash` as dead-write; direct-read at factory :955-970 confirms `Deliverable.objects.filter(content_hash=c_hash, created_at__gte=hash_window).order_by('-created_at').first()` is the factory's 72h dedup query — NOT dead-write. **Load-bearing debt matrix (12 items, 3 CRITICAL + 4 HIGH + 4 MED + 1 LOW):** T.15.2 SportsBettingBrief WRITE-ONLY-FORGOTTEN CRITICAL CONFIRMED at HEAD (2 writers `tasks_content.py:3150` + `tasks.py:12187`; no readers found via `rg` across core/; REST `get_betting_brief` at `views_odds_sports.py:3237` `AllowAny` bypasses persisted model — S1504 §14.3 pattern class extension); T.15.3 BlockchainAuditBrief same pattern (1 writer `tasks.py:12240`; no readers found); T.15.4 OutreachDraft delivery MISSING **F8-upgrade HIGH → CRITICAL** because business-critical for outbound revenue (S1402 F.B1 CONFIRMED at HEAD: no `send_outreach|dispatch_outreach|sendgrid|postmark|mailgun|smtplib` found via `rg` in mainline production); T.15.1 SelfBlog canonical bypass at `content_deliberation_runner.py:401` HIGH (16+ sites; factory invariants ALL skipped: content_hash dedup, publish_intent resolution, provenance receipt synthesis, orphan diagnostic); T.15.6 Triple-gate **composition contract MISSING F7+F11-reframed** as boundary_violation (5-gate factory at :358-411 + PublishGate 4-threshold at `publish_gate.py:44-49` + SelfBlog own quality gate at `models_unified_system.py:20708-20728` — no canonical precedence statement; escalated from parent §6.3 parked issue; Cat C S1604 owns resolution; Cat D contributes evidence). **Rigby SIGN cycle 1** SIGN-with-edits at Medium-High confidence (0.75 → High via F1 resolution per Rigby Batch C Q9 Option 1 verdict) via fresh isolation pin `pa-8af9063864bf4a7f` (retired at S1603 close via `session_tool.retire`; `updated_count: 5, retired: true`; `is_current_bound: false, previously_active: true`). **F1-F18 folds landed pre-commit:** F1 shadow-`create_deliverable` RESOLVED as name-collision; F2 Cat D-adjacent services added (`deliverable_envelope.py`, `conversation_deliverable_extractor.py`, `platform_event_view.py`, `deliverables_consumer.py`) at §5.4a; F3 5 factory-adopter mgmt commands added at §7.4 (`register_external_repo.py`, `import_patent_disclosures.py`, `refresh_repo_context.py`, `draft_repo_verifier_claims.py`, `survey_external_repo.py`); F4 Deliverable base maturity explicit "current-scope definition" with WORKING = "operationally used successfully in production with known structural debt"; F5 factory adoption reconciliation; F6 D65a reframed to 3-category neutral taxonomy; F7 triple-gate reframed as "separation-of-concerns lacking composition contract"; F8 T.15.4 OutreachDraft delivery HIGH → CRITICAL; F9 T.15.1 SelfBlog bypass severity nuanced; F10 T.15.5 description update; F11 T.15.6 type changed to boundary_violation + "composition contract missing"; F12 NEW T1 R.CONTENT.VARIANT-CATEGORIZATION-CLARIFICATION (bridge artifact for xx99 D65a consumption); F13 NEW T1 R.CONTENT.CANONICAL-CREATION-CONTRACT (factory + creation-funnels reconciliation); F14 R.CONTENT.OUTREACHDRAFT-DELIVERY upgraded T2 → T1 (revenue-critical); F15 over-binary claims softened with grep-method disclosed (`rg` across `core/`); F16 Cat D-vs-Cat C boundary tightened (Cat D contributes evidence, Cat C owns resolution); F17 F1 resolved before commit (Option 1 per Rigby verdict); F18 maturity provisional rewound (F1 resolved). **D48 preemptive stability-probe gate 12th-arm outcome:** Batches A/B/C substantive on fresh isolation pin; final-verdict single-question follow-up clean; no pin-poisoning symptoms. **Seven-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603 CONFIRMED** — extends 11-arc pattern to 12-arc + S1603. Codification-ready-STRENGTHENED for playbook v3 §15. ARCHITECTURE_INDEX v37 → v38 bump same-commit: this §8 timeline row + §1.41 registration + frontmatter v38 preamble. OPEN_ARCS Group 1600 row current-child field advances "S1602 SIGN-with-edits cycle 1 at High confidence (F1-F7 folds landed) + S1603 queued next" → "S1603 SIGN-with-edits cycle 1 at Medium-High → High confidence (F1-F18 folds landed) + S1604 queued next"; row remains In-progress. Group 1600 arc pin `pa-f52acf3f8d394faa` RETAINED per playbook §16 — carries P4-P6 sequence + P7 xx99. | Feeds S1604 Cat C PublishGate + Publish Rails child audit next per D66 P4 slot (moved from P3 → P4 per parent F3 fold). S1604 inherits T.15.6 triple-gate composition contract MISSING + §8.4 lifecycle stages 9-11 CAT C-OWNED + UNK-2 Newsletter dry_run promotion path + UNK-4 gate canonicalization + §14.3 triple-gate boundary evidence. Alternative near-term: T1 R.CONTENT.RAG-SCOPE cross-arc verification via Cat E S1605 or Memory arc — resolves S1601 riskiest overall finding pre-S1604 if Chris prioritizes closing riskiest overall first. **First library child audit to reframe an "island posture" claim from binary structural-fact to 3-category neutral taxonomy** via Rigby SIGN Batch B fold — prevents S1274 EventBus-style over-interpretation of structural absence as functional gap. **First library child audit to RESOLVE a shadow-factory concern via direct-read name-collision verification** (F1: `real_job_execution_consumer.py:200` shadow returns plain dict for demo WebSocket UI). **First library child audit to reach 18-fold SIGN-with-edits verdict** — largest fold count in the library reflecting audit scope + Rigby's substantive engagement across A/B/C batches + final-verdict follow-up. |
| **S1602** (2026-07-02) | `domains/content/1602_content_reviewers_decision_enforcement_audit.md` (§1.40) | **Second child audit under Group 1600 Content / Deliverables / Publishing arc — Category B Content Reviewers + Decision Enforcement.** Playbook §11.2 20-section template + 6-parallel-Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 7 pre-Explore + 3 post-Explore load-bearing binary claims. **Load-bearing question resolutions (parent §3 Cat B):** Q1 dispatch shape — reviewers are PURE-FUNCTION MODULE-LEVEL (not class-based) via `content_review_panel_v2.py:88,107,124,208`; Q2 v1 vs v2 canonicalization — v2 canonical for deliberation pipeline; v1 `ContentReviewPanel` at `content_review_panel.py:61` classified **PARTIALLY-ADOPTED-LIVE-SECONDARY** (grep-verified live consumer at `ContentWriterAgent:1376-1377` under `ENABLE_CONTENT_REVIEW=True` at :62; S1274 EventBus lesson properly applied). **S1601 §15.1 UNK-2 fully resolved to CONFIRMED HIGH** — end-to-end citation integrity across A+B is LLM-prompt-only with zero code-side per-claim `[C-xxxxxxxxxx]` regex verifier at either gate. **Load-bearing findings (7 ranked for xx99 §5 evidence plan):** (1) **HIGH CONFIRMED** — End-to-end LLM-prompt-only citation contract across A+B (extends + fully resolves S1601 UNK-2); T1 R.CONTENT.CITATION-INTEGRITY. (2) **HIGH** — Silent draft truncation at 8000 chars in v2 reviewers (`content_review_panel_v2.py:236`); extends S1601 F2 silent-partial-source pattern; T1 R.CONTENT.CAT-B-TRUNCATION. (3) **HIGH latent-landmine** (F6 severity fold from CRITICAL) — `queue_agent_task` MISSING from `core/tasks.py`; `spawn_tasks_from_mandate` at `decision_enforcer_agent.py:456` imports missing task with broad try/except at :455/:474-476 → exception-swallowed silent failure; zero production callers; invalidates patent claim at `DISCLOSURE_F.md:140`; T1 R.CONTENT.CAT-B-SPAWN-TASKS. (4) **HIGH** — Cat B mandate + reviewer verdicts ZERO PA-tool outbound channel; only readback via REST `/api/blog/<uuid>/deliberation/` at `views_deliberation.py:320-386`; extends S1402 F.B1 ZERO outbound channel pattern to content Cat B CONFIRMED; T1 R.CONTENT.CAT-B-OUTBOUND. (5) **MED** — ConversationOrchestrator hardcodes critique agents at runner:252-253. (6) **MED** — Single-iteration rewrite; no convergence loop; DecisionEnforcerAgent NOT re-invoked post-rewrite. (7) **MED** — DeliberationSession retention unbounded. **Rigby SIGN cycle 1** SIGN-with-edits at High confidence via fresh isolation pin `pa-1c5298d807d7a1d2` (retired at S1602 close via `session_tool.retire`; `updated_count: 4, retired: true`). **F1-F7 folds landed pre-commit:** F1 §5.5 ConversationOrchestrator critique reframed as Cat B decision-production substrate; F2 §3.5 `_extract_decision` at runner :266-284 explicitly Cat B-OWNED; F3 §1 "all v2 deliberation deployment paths" scope tightening (v1 direct-write does NOT touch v2 panel); F4 §4.2 + §13 MandateStatus lifecycle correction (mark_killed at :404-407 + mark_completed at :409-411 CODED but ZERO callers in deliberation flow — Rigby grep-verified — dormant state machine NOT missing machinery); F5 §1 finding #3 + §7.2 branch 8 + §15.3 spawn_tasks_from_mandate correction (broad try/except guard at :455/:474-476 → exception-swallowed silent failure NOT unhandled crash); F6 §15.3 severity CRITICAL → HIGH latent-landmine + §19.6 T-slot rank #3/#4 reorder; F7 §15.10 `_detect_domain` 0.2 threshold MED → LOW (unvalidated tuning knob without misclassification evidence). **D48 preemptive stability-probe gate 11th-arm outcome:** Batches A/C + B/C substantive on fresh isolation pin; Batch C/C partial deflection (worker-load pressure, not full jam per memory rule 2-substantive-turns threshold); final-verdict single-question follow-up returned clean in <10s: "SIGN-with-edits (7 folded) — High confidence." **Six-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602 CONFIRMED** — extends 10-arc pattern S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506+S1601 to 11-arc + S1602. Codification-ready-STRENGTHENED for playbook v3 §15 per S1599 §10.2 6-candidate codify list. **Do-not-regress phrasings for PR:** (i) preserve F5 "exception-swallowed silent failure via broad try/except at :455/:474-476; no user-visible symptom" phrasing at §1 finding #3 + §15.3; (ii) preserve F4 "dormant state machine (contract supports transitions but no caller in deliberation flow invokes them), not missing machinery" phrasing at §4.2 + §13. ARCHITECTURE_INDEX v36 → v37 bump same-commit: this §8 timeline row + §1.40 registration + frontmatter v37 preamble. OPEN_ARCS Group 1600 row current-child field advances "S1601 SIGN-with-edits cycle 1 at Medium confidence (F1-F6 folds landed) + S1602 queued next" → "S1602 SIGN-with-edits cycle 1 at High confidence (F1-F7 folds landed) + S1603 queued next"; row remains In-progress. Group 1600 arc pin `pa-f52acf3f8d394faa` RETAINED per playbook §16 — carries P3-P6 sequence + P7 xx99. | Feeds S1603 Cat D Deliverable Base + Specialized Variants child audit next per D66 P3 slot (F3 fold: moved from P4→P3). S1603 inherits S1601 §9.1 SelfBlog.objects.create bypass + S1602 §16.1 canonicalization-debt reframe as D65a HEADLINE evidence. Alternative near-term: T1 R.CONTENT.RAG-SCOPE cross-arc verification via Cat E S1605 or Memory arc — resolves S1601 riskiest-overall finding (Document workspace FK schema UNK-1) pre-S1603 if Chris prioritizes closing riskiest overall first. **First library child audit to encounter Rigby SIGN Batch C/C partial-deflection pattern with clean single-question follow-up recovery** — new recovery-pattern candidate for playbook v3 §15. **First library child audit to fully resolve a prior-sibling UNK gap in one session** — S1601 UNK-2 fully resolved to CONFIRMED HIGH. **First library child audit to grep-verify SPECULATIVE flag retraction** — Explore Agent 2's gpt-5.2 SPECULATIVE flag retracted via 14-file grep confirming valid internal LLM routing target. **First library child audit to have Rigby grep-verify 2 factual corrections against the audit's own claims** (F4 MandateStatus lifecycle transitions exist + F5 spawn_tasks try/except guard exists) — reinforces "trust but verify" rule bidirectionally: parent-Claude verifies pre-Explore + Rigby verifies post-draft. |

| **S1599** (2026-07-02) | `domains/sports/1599_sports_canonical_summary.md` (§1.37) | **Group 1500 Sports/DBAO/Intelligence arc CLOSED at xx99 canonical summary.** Playbook §11.3 12-section template + §10 "What This Research Taught Us About How to Do Research" **third application** after S1399 first + S1499 second. Consumes 6 child audit outputs S1501 Cat A + S1502 Cat B + S1503 Cat C + S1504 Cat D + S1505 Cat E + S1506 Cat F + parent scoping S1500. Bounded synthesis per playbook §11.3 rules — no new §13 6-parallel-Explore sweep; no new file:line evidence; CANDIDATE → CONFIRMED resolutions preserved. **§5 D59 posture-decision evidence brief delivered** with **explicit "Chris-gated selection" tag** — 7 integration criteria A1-A7 + 7 island criteria B1-B7 + 4 cross-cutting C1-C4 + failure-mode table D + cost asymmetry summary E + F2-fold scoring rubric F applied uniformly across P1-P6 evidence corpus → **all 22 criteria score FAIL at HEAD `5a8d3d75`** exposing load-bearing observation "BOTH postures require substantive investment; neither is a default." **§3.4 Four-axis compound-maturity shape** NEW arc-level maturity framing: (1) DBAO product-line materialization axis = NAMING-CONVENTION-WITHOUT-MATERIALIZATION; (2) Intelligence surface axis = flag DECLARED-GATES-NOTHING + engine LATENT-ZERO-FIRE + REST/frontend DOMAIN-NEUTRAL; (3) Discord sports surface axis = read HOT-PATH-CHOKE-BYPASS + write WORKING + digest DUAL-COORDINATOR-BYPASS; (4) Cross-domain feedback surface axis = DECOUPLED-VERIFICATION-SYSTEMS + PARTIAL-LEARNING-BRIDGE + zero SignalCluster emission. **§3.2 Sports Domain Lifecycle Traceability Table** per parent §12.5 F.iii deliverable — 8 lifecycle stages (odds ingestion + fixture/entity identity resolution per Rigby Q8 fold + normalization + prediction + user wager + outcome verification + learning-loop feedback + signal aggregation gap); 1 of 8 stages MISSING (Stage 8 Signal Aggregation — 6-arc COMPLETED gap); 1 of 8 UNKNOWN+MISSING resolver (Stage 2 fixture/entity identity); 5 of 8 LIVE-BUT-DRIFTING; 1 of 8 IMPLICIT. **13 pattern classes registered** — 5 NEW at S1506 (P1 NAMING-CONVENTION-WITHOUT-MATERIALIZATION + P2 DECOUPLED-VERIFICATION-SYSTEMS + P3 DECLARED-FEATURE-FLAG-GATES-NOTHING + P4 DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT (3-child) + P5 SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION) + 5 NEW at other categories (P6 MOCK-DATA-CONSUMER 2-child + P7 DEAD-RENDER-PATH + P8 WRITE-ONLY-FORGOTTEN 2-child + P9 ZERO-FIRE-BEAT 2-child + P10 HOT-PATH-CHOKE-BYPASS 2-child) + 3 INHERITED (P11 Sports↔Signal Engine 6-arc consumer-side gap COMPLETED + P12 Sports↔Memory PARTIAL bridge 5-arc + P13 Fixture/entity identity 2-arc). **§12.4 discriminative-value criterion check per parent §12.4 + Rigby SIGN cycle 1 Q7 fold: 4 of 4 evidence types satisfied** (Scope confusion prevented via D60 Intelligence bound-out + Rework reduced via §11.4 F.ii boundary + Cleaner arc close via 6-of-6 SIGN-with-edits at commit-time + Chris-lock efficiency via single "agree all + D-6=(a)" round D56-D61) — includes both (Scope confusion prevented) AND (Cleaner arc close). **Playbook v3 §11.1 template promotion TRIGGERS.** **Playbook v3 candidate list (6):** D48 preemptive stability-probe gate 9-arc CODIFICATION-READY → v3 §15; D62=(a) 6-sibling exemplar pattern → v3 §5; F2-fold scoring rubric → v3 §11.3 §5 for D59-analog xx99s; BEFORE-SIGN Rigby ORM probe → conditional v3 §14; S1504 SIGN cycle 1 batch 1 verdict-text re-request recovery → v3 §15 preventive framing rule; S1505 Rigby Q8 grep-verified confidence-upgrade → v3 §15 SIGN-time verifier-loop tool candidate. **§7 anchor-update recommendations:** `PLATFORM_INVENTORY.md` §3.10 subdivision + DBAO subgroup conditional on T1.b; `PLATFORM_WHAT_IT_IS.md` Sports narrative refresh; ARCHITECTURE_INDEX v33 → v34 (this row + §1.37 registration + §5 gap consolidation + §7 decision matrix update + §9 roadmap update + frontmatter v34 preamble); OPEN_ARCS Group 1500 in-progress → closed; NEW `docs/topics/sports-betting.md` (C2 cross-cutting gate); `.github/CODEOWNERS` 6 sports runtime files. **§8 T1-T10 follow-on queue:** T1 Chris-gated ADRs (R.SPORTS.POSTURE + R.DBAO.CODENAME) + CRITICAL remediation sequences (R.C1 verify-beat ← R.C2 concurrency-safety + R.D1 digest-beat ← R.D2 idempotency + R.D3 zero-test-coverage reliability multiplier + R.D4 SportsBettingBrief consumer-or-remove ← T1.a + R.D5 two-writer dedup); T2 12 design-preparation tracks; T3 6 Employee OS + delegated; T4 11 cleanup PRs; T5 6 optional. Rigby Full SIGN cycle 1 pending on fresh isolation pin — **D48 preemptive stability-probe gate 10th arm** anticipated; five-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1599 anticipated if held clean. Arc pin `pa-791b3db549a64e54` retires at arc-close per playbook §16 D53 arc-close discipline (matches S1499 pattern). | Feeds post-arc T-slot ADRs (T1 R.SPORTS.POSTURE + T1 R.DBAO.CODENAME Chris-gated ADRs); playbook v3 §11.1 promotion session (consumes §10.2 6-candidate codify list); NEW `docs/topics/sports-betting.md` first-inventory landing PR; T2 design-preparation phase (12 tracks blocked by T1.a and/or T1.b); T3 Employee OS + delegated arcs (S1300 Memory follow-on if integration posture chosen; Group 1600 Content if opened; Group 1700 Observability if opened); T4 cleanup PRs (11 tracks); T5 optional. Sets 3-arc precedent (S1399 Memory + S1499 Revenue + S1599 Sports) for playbook §11.3 12-section canonical summary template shape. |

| **S1506** (2026-07-02) | `domains/sports/1506_sports_cross_domain_integration_lens_and_posture_decision_framing_audit.md` (§1.36) | **Sixth and LAST child audit under Group 1500 Sports/DBAO/Intelligence arc — Category F Cross-Domain Integration Lens & Posture Decision Framing.** Playbook §11.2 20-section template + 6-parallel-Explore sub-agents per §13 (Agent 1 DBAO footprint + Agent 2 Intelligence surface + Agent 3 Discord bridge + Agent 4 Signal Engine gap + Agent 5 Memory bridge + Agent 6 MLPrediction feedback) + parent-Claude verifier-loop per §14 on 6 load-bearing pre-Explore claims (all 6 verified CORRECT against source before draft integration). **LOAD-BEARING for D59 posture-decision evidence plan owed to xx99 canonical summary** — §20.6 produces the evidence-plan framing (7 integration criteria A1-A7 + 7 island criteria B1-B7 + 4 cross-cutting C1-C4 + failure-mode table D + cost asymmetry summary E + F2-fold scoring rubric with thresholds F) with explicit Chris-gated selection tag. **Sixth and final sibling to apply D62 = (a) pre-brief mini-schema propagation upfront** — 6-sibling exemplar pattern COMPLETED. Rigby Full SIGN cycle 1 SIGN-with-edits at **High confidence** via fresh isolation pin `pa-c2cdbd5c0b8c451b` (**D48 9th arm — four-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506** with zero worker-instability across 3 substantive SIGN turns; retired at S1506 close via `session_tool.retire`). F1-F2 folds landed at commit-time: F1 §14.5 anchor-set tightening (`/odds` + `/futures` + `/slip` explicit bypass; `/arb` shared-agent exclusion at section body per Rigby Q5 Batch 1 edit); F2 §20.6 §F scoring rubric + threshold minima for xx99 consumption-readiness per Rigby Q15 Batch 3 edit. **Load-bearing findings (14):** (1) CRITICAL — DBAO NAMING-CONVENTION-WITHOUT-MATERIALIZATION (NEW pattern class); (2) CRITICAL — DECOUPLED-VERIFICATION-SYSTEMS at BettingOutcomeVerifier ↔ MLPrediction (NEW pattern class); (3) HIGH — Sports ↔ Signal Engine 6-arc consumer-side pattern completed; (4) HIGH — DECLARED-FEATURE-FLAG-GATES-NOTHING at `sports_intelligence` (NEW pattern class); (5) HIGH — Discord HOT-PATH-CHOKE bypass extends S1504 pattern; (6) HIGH — Sports ↔ Memory PARTIAL bridge; (7) HIGH — `/ws/dbao-dashboard/` sibling route surfaced; (8) HIGH — DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT (NEW pattern class); (9) MED-HIGH — SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION (NEW pattern class); (10) MED-HIGH — LATENT-ZERO-FIRE deepens S1503 ZERO-FIRE-BEAT; (11) MED — IntelligencePage sports-tangential; (12) MED — DUAL-COORDINATOR-BYPASS; (13) MED — CODEOWNERS compound gap; (14) MED — `docs/topics/sports-betting.md` gap. **Cat F maturity verdict per §13:** **PARTIAL (mixed; multi-axis; four-axis compound shape)** — sixth distinguishing maturity shape in the arc. | Feeds S1599 xx99 canonical summary (P7 next per parent §5 sequence — third application of playbook §11.3 §10 meta-methodology after S1399 + S1499); §20.6 evidence plan consolidated verbatim into xx99 §5 posture-decision brief; §20.9 6-arc consumer-side pattern completion + §20.10 6-sibling exemplar pattern completion candidate for playbook v3 §5 promotion; D48 9-arc CODIFICATION-READY signal alongside D45 titles-only recovery + BEFORE-SIGN Rigby ORM probe + S1504 verdict-text re-request preventive framing + S1505 Q8 grep-verified confidence-upgrade patterns for xx99 §10.2 codify-to-playbook-v3 recommendation; F1 anchor-set-tightening pattern candidate for playbook v3 §14 evidence-rules addition; F2 scoring-rubric-with-thresholds pattern candidate for playbook v3 §11.3 canonical summary template §5 addition. |
| **S1505** (2026-07-02) | `domains/sports/1505_sports_frontend_surface_audit.md` (§1.35) | **Fifth child audit under Group 1500 Sports/DBAO/Intelligence arc — Category E Sports Frontend Surface.** Playbook §11.2 20-section template + 6-parallel-Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 5 load-bearing claims (all 5 verified CORRECT by Rigby Q8 grep pass: BettingPage.tsx 3,023 lines + `BettingTab` union at line 14 declares 11 identifiers / `tabs` array lines 16-26 renders 9 nav / `markets` + `bankroll` DEAD-RENDER-PATH conditionals at lines 968/975/2080/2298 + `live_betting_opportunities` `@permission_classes([IsAuthenticated])` at `views_odds_sports.py:580` + `get_betting_intelligence` `@permission_classes([IsAuthenticated])` at `views_odds_sports.py:2056` + `urls.py:3085` + `:3099` mappings + `SportsBettingBrief.objects` 2-writer-0-reader confirmed at frontend AND REST endpoint layer). **Fifth library child audit to apply the 4-item pre-brief mini-schema per surface per D62 = (a) propagate upfront** — fifth sibling extends D62 propagation-upfront validation from S1501+S1502+S1503+S1504 4-arc pattern to 5-arc pattern; embedded at §4.2 with cross-sibling observation "humanApi cross-domain sharing is load-bearing on design-posture axis (d) — first sibling where 3 shared-with-mainline surfaces (humanApi + ProtectedRoute + /ws/dbao/ consumer) require cross-domain refactor if island posture chosen; raises island-posture cost estimate above prior siblings." **Load-bearing findings (11):** (1) **CRITICAL architectural — `/ws/dbao/` broadcasts random mock data, not sports-derived state.** `core/new_pages_consumer.py:310-331` `send_dbao_metrics` handler populates every metric field via `random.randint()` + `random.uniform()`. **NEW pattern class for the arc: MOCK-DATA-CONSUMER** — distinct from S1504 §14.3 WRITE-ONLY-AND-FORGOTTEN (real data written, never read) + S1503 §14.1 ZERO-FIRE-BEAT (real task, real schedule, never fires) + S1502 §14.4 PROVENANCE-STAMP-ABSENT (real writes but no owner tag). Here: no real data is touched at any point; the consumer synthesizes numbers server-side, timestamps them (`timezone.now().isoformat()`), and pushes as WS messages that clients cannot distinguish from real data without reading source. F5 intent-neutrality fold: may be intentional demo/placeholder for a non-sports dashboard surface but the audit's concern still stands because the payload lives in a production WS namespace at a route that Cat E dashboards or Cat F integration paths might reasonably subscribe to; operational-confusion / integration-signaling hazard, not pure architectural anti-pattern. Whether the handler is intentional or accidental, the false-sense-of-coverage cost is the same. (2) **HIGH architectural — `markets` + `bankroll` DEAD-RENDER-PATH tabs.** `BettingTab` TypeScript union at `BettingPage.tsx:14` declares 11 tab identifiers; the visible `tabs` array at lines 16-26 renders only 9 nav buttons; verifier-loop confirms the remaining 2 ARE wired at the render layer — conditional query hooks at lines 968 (`activeTab === 'bankroll'`) + 975 (`activeTab === 'markets'`) and conditional JSX blocks at lines 2080 (`activeTab === 'markets'`) + 2298 (`activeTab === 'bankroll'`) — but with no tab button, they are unreachable via UI navigation. **NEW pattern class: DEAD-RENDER-PATH** (fully coded feature branches with no user-facing entry point). Fifth distinguishing pattern shape after S1501 fragile-contract + S1502 armed-but-under-instrumented + S1503 armed-but-zero-fire + S1504 write-only-forgotten. (3) **HIGH operational — 2 permission-floor inconsistencies between frontend read-path expectations and backend IsAuthenticated decorators.** Frontend calls `bettingApi.liveOpportunities()` → `GET /api/v1/sports/live-opportunities/` (`urls.py:3085` → `live_betting_opportunities` at `views_odds_sports.py:581` with `@permission_classes([IsAuthenticated])` at line 580) + `bettingApi.intelligence()` → `GET /api/v1/sports/betting-intelligence/` (`urls.py:3099` → `get_betting_intelligence` at `views_odds_sports.py:2057` with `@permission_classes([IsAuthenticated])` at line 2056). Frontend has no client-side auth gate before these calls + `api.ts:48-56` only triggers logout on 401 for auth endpoints (other 401s log warning). Silent 401 on Top Plays / Sharp Action / Arbitrage tab families. F1 fold two-sided drift class: frontend "no 401 surfacing / no per-call auth gate" + backend "permission-floor inconsistency with Session 559/688 public-read-for-dashboard precedent." F4 fold tab-consumer identification. (4) **HIGH architectural — S1504 §14.3 SportsBettingBrief write-only-and-forgotten CONFIRMED at frontend AND REST endpoint.** `get_betting_brief` at `views_odds_sports.py:3237-3265` calls `SportsBettingCoordinator.generate_brief()` on-the-fly + returns coordinator result verbatim; persisted `SportsBettingBrief` model is never queried. S1504 verdict upheld and strengthened. (5) **HIGH architectural — Zero WebSocket subscription from BettingPage despite defined sports WS routes.** `sports/routing.py:7-11` registers `/ws/sports/`, `/ws/sports/odds/`, `/ws/sports/games/` consumers but BettingPage (3,023 lines) has zero `new WebSocket` / `useWebSocket` / `wss:` / `/ws/` references. Live Odds tab misnamed — 30-second polling at `BettingPage.tsx:961`, not WS push. Extends S1502+S1503+S1504 consumer-side realtime absence into Cat E: no arc-scope surface publishes or subscribes to sports realtime events despite infrastructure being registered. (6) MED-HIGH POSTURE-DECISION-PENDING per S1502 F2 / S1503 §14.3 / S1504 F11 precedent — Zero Cat E → Signal Engine emission path; extends 4-arc consumer-side pattern to 5-arc pattern. (7) MED architectural — BettingPage is SOLE frontend sports data consumer (zero cross-domain leak); positive isolation signal for Cat F island-vs-integrated posture evidence. (8) MED operational — BettingPage.tsx = 3,023 lines god-component with 14 useQuery hooks + 17+ useState declarations + 5 inline sub-components + 11 inline TypeScript interfaces. Frontend god-component threshold analog to backend 3,000-line service check per playbook §13 Agent 2. (9) HIGH per S1504 §15.12 F4-fold sibling precedent — Zero dedicated test coverage for BettingPage.tsx. Grep of `frontend/**/*.test.{ts,tsx}` + `frontend/**/*.spec.{ts,tsx}` returns zero matches. Matches Cat D §15.12 F4-fold zero-test pattern that S1504 promoted MED-HIGH → HIGH. (10) MED architectural — Zero client-side state persistence (all state React `useState`; no localStorage / sessionStorage / IndexedDB); tab position + filters + expanded rows lost on refresh. (11) MED — No CODEOWNERS row for `frontend/src/pages/BettingPage.tsx`; ownership UNKNOWN. **Rigby Full SIGN cycle 1** SIGN-with-edits at **High confidence** via fresh isolation pin `pa-546de7ebe8c8b885` — 4 substantive SIGN turns (1 warmup ping via `cockpit_tool.worker_health` + `infra_health_tool.dependency_matrix` returning 4 healthy workers + 7-of-7 healthy components + 3 SIGN batches Q1-Q3 architectural + Q4-Q6 architectural + Q7-Q9 grep-verified). **Zero worker-instability observed across all 4 turns (D48 8th arm — three consecutive fully-clean arms S1503+S1504+S1505 pattern).** Confidence upgrade Medium → High at cycle 1 batch 3 after Rigby Q8 grep-verified all 5 load-bearing file:line claims independently. **F1-F5 folds landed at commit-time** — F1 §14.3 auth-drift wording tightening from frontend "assumes AllowAny" to two-sided drift class (frontend "no 401 surfacing / no per-call auth gate" + backend "permission-floor inconsistency"); F2 §15.5 elevated MED → HIGH structural debt "No API contract source-of-truth (no shared response types, no schema-generated clients)" as the parent cause behind §14.3 AUTH-DRIFT + §15.4 inline interfaces + §14.9 tab-count doc drift + general read-path fragility; F3 §14.3 added "Verified-in-repo anchors" subsection explicitly enumerating 4 grep-verified anchor points from Rigby Q8 pass; F4 §14.3 named `bettingApi.liveOpportunities()` + `bettingApi.intelligence()` as feeding Top Plays / Sharp Action / Arbitrage tab families per §6.1 Cat B ownership mapping; F5 §14.1 MOCK-DATA-CONSUMER intent-neutrality nuance — added intent-neutral framing paragraph acknowledging `/ws/dbao/` handler may be intentionally staged as demo/placeholder without weakening CRITICAL classification, reframed as "operational-confusion / integration-signaling hazard." **Cycle 2 SIGN-clean at High confidence anticipated post-fold-land** matches S1501+S1502+S1503+S1504 cycle-1-predict-cycle-2 pattern. **Do-not-regress notes for PR:** preserve §2.1 Cat E contract statement (5 guarantees + 11 non-guarantees) + preserve F1-F5 folds per §20.8 detailed enumeration (see §1.35 audit registration for full do-not-regress list). **D48 preemptive stability-probe gate 8th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505 8-arc pattern — further strengthens immediate codification recommendation from S1504 7-arc threshold with three-consecutive-fully-clean arms sub-pattern (S1503+S1504+S1505). Fresh SIGN isolation pin `pa-546de7ebe8c8b885` retires at S1505 close via Rigby `session_tool.retire` (updated_count=5). Group 1500 arc pin `pa-791b3db549a64e54` RETAINED per playbook §16 — carries P6 sequence + P7 xx99. ARCHITECTURE_INDEX v31 → v32 bump same-commit: this §8 timeline row + §1.35 registration + frontmatter v32 preamble. OPEN_ARCS Group 1500 row current-child field advances "S1504 SIGN-with-edits cycle 1 (F1-F11 folds landed, cycle 2 anticipated) + S1505 queued next" → "S1505 SIGN-with-edits cycle 1 (F1-F5 folds landed, cycle 2 anticipated) + S1506 queued next"; row remains In-progress. | **First library child audit to identify a MOCK-DATA-CONSUMER pattern class at the WebSocket layer** — introduces a NEW pattern class distinct from S1504 WRITE-ONLY-FORGOTTEN + S1503 ZERO-FIRE-BEAT + S1502 PROVENANCE-STAMP-ABSENT. Diagnostic criteria replicable to future audits (e.g., other dashboard WS namespaces + placeholder-scale metrics surfaces + demo-mode fallback handlers). **First library child audit to identify a DEAD-RENDER-PATH pattern class** — fully coded feature branches with no user-facing entry point. Pattern candidate for playbook v3 §14 evidence-rules diagnostic checklist. **First library child audit to elevate "no API contract source-of-truth" to first-class structural debt** — Rigby Q5 F2 fold named this as the parent cause behind auth-drift + inline interfaces + tab-count doc drift. Pattern candidate for playbook v3 §12.1 debt classification addition. **First library child audit to reach "PARTIAL (mixed)" verdict with FIVE distinct component states across the frontend** — WORKING + DEAD-RENDER-PATH + MOCK-DATA-CONSUMER + AUTH-DRIFT + NO-REALTIME. Fifth distinguishing maturity shape in the arc. **First library child audit to codify D48 stability-probe gate as 8th-arm CODIFICATION-READY signal with three-consecutive-fully-clean arms sub-pattern (S1503+S1504+S1505)** — further strengthens immediate playbook v3 §15 codification recommendation. **First library child audit where Rigby Q8 grep-verified ALL 5 load-bearing file:line claims independently pre-final-verdict** — confidence upgrade Medium → High at batch 3 after grep verification pass. Verification-driven confidence-upgrade pattern candidate for playbook v3 §15 addition. **First library child audit to identify a shared-with-mainline API surface as load-bearing on design-posture axis (d) island-isolation-cost** — humanApi is used by 4 non-BettingPage frontend consumers; raises island-posture cost estimate above prior siblings. Cross-sibling observation load-bearing for Cat F posture-decision brief. **First library child audit where zero cross-domain frontend consumption is a POSITIVE isolation signal for Cat F** — BettingPage.tsx is SOLE Cat E surface; positive-shape finding contrasts with mostly-negative drift-shape findings in siblings S1501-S1504. Index v32 updated per §10.1 (this row + §1.35 row + frontmatter v32 preamble). |

| **S1279** (2026-07-02) | Research OS installation: `CLAUDE.md` pointer + `docs/research/OPEN_ARCS.md` created + `docs/00-START-HERE/README.md` & `INDEX.md` extended | **Installation of the Research OS as canonical workflow.** Three P0 items landed in one atomic commit: (1) CLAUDE.md gains a "Research Library" subsection + universal 8-step Startup checklist — pointer-only into `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` (no restatement); (2) `docs/research/OPEN_ARCS.md` created as machine-readable cross-arc manifest with in-progress / awaiting-summary / closed / stalled / not-started sections + reconciliation ritual + schema reference (source-of-truth for arc state per OS §6.6); (3) `docs/00-START-HERE/README.md` + `INDEX.md` extended with Research Library discovery rows and OS entry in mandatory reading order. `CURRENT_RESEARCH.md` evaluated and explicitly rejected — OPEN_ARCS with `state: in-progress` filter serves the same purpose; adding a third file would duplicate one of OPEN_ARCS + `00-START-NEXT-SESSION.md`. OS `status:` flipped `draft` → `active` — Research OS is now **CANONICAL**. Verifier_loop appended with installation record + validation checklist. No architectural changes; OS §1-§19 structurally unchanged; §20.15 installation record section added additively. Zero circular references; zero duplicated startup instructions; zero conflicting authority. Runtime untouched. | **Installation, not extension.** S1268-S1278 built the process framework; S1279 makes it the default workflow. From this point forward: (a) every fresh Claude Code session discovers the OS naturally via CLAUDE.md or START-HERE; (b) Group 1400 Revenue may open under the fully-installed OS as the first exercise of the "Start research group NNNN" reduced-prompt target rhythm (OS §12.3); (c) future OS improvements are operational refinement (P1/P2 items: ADR corpus, Investigation Log template, Ops Incident Report template, playbook v3, `RESEARCH_DEBT.md` manifest) — not architectural redesign. The Research OS architecture is closed. Index v12 updated per §10.1 (this row + §1.14 CANONICAL status flip). |

**Pattern observation (updated S1279).** The library has grown
in **four waves plus one canonicalization event.** **First wave** (S1268-S1272): 5 docs in 5
sessions — the Employee OS depth arc following the "each doc
names the next" discipline. **Second wave** (S1273-S1275): the
whole-platform sibling arc (§1.9 inventory) + cross-domain
integration audit + design-preparation arc (§1.10 option
selection → §1.12 event schema) — first `authority: design-
preparation` docs. **Third wave** (S1274 v1 + S1276 v2 playbook,
S1300 memory scoping): the process framework itself.
`authority: process` (playbook) and `authority: parent-doc`
(S1300) enter the corpus. **Fourth wave** (S1276 introspection +
S1277 OS + S1278 ratification): the process framework becomes
self-executing. `authority: process-audit` (introspection) and
canonical Research OS (§1.14) enter the corpus. A brand-new
Claude Code can now be productive by reading only CLAUDE.md +
MEMORY.md + `00-START-NEXT-SESSION.md` + OS §0-§5 — no custom
prompt from Chris required. The library's *next* growth events
are: (a) migration session S1279+ landing OS §17 P0 items
(CLAUDE.md pointer, `OPEN_ARCS.md`, START-HERE pointers) that
convert OS from READY-WITH-MINOR-FOLLOW-UP to CANONICAL; (b)
Group 1400 Revenue opening under the OS+playbook contracts as
first exercise of "Start research group NNNN" reduced-prompt
target; (c) Group 1300 Memory children (S1301 RAG lanes queued
next); (d) whole-platform arc's top-3 next missions per §1.9
§9 — Revenue Pipeline canonical architecture (§5.12),
Observability Deduplication Audit (§5.13), Sports/DBAO ↔ AI
Studio Integration Sketch (§5.14); (e) Employee OS arc STAGE 5
(Trust Propagation §5.3 or Employee Boundary Escalation §5.4
— Chris picks). All parallel-safe if pursued independently,
per §18 dependency semantics (informational, not blocking).

---

## 9. Future Research Roadmap

Not a design. Not a build plan. A recommended *research*
ordering to minimize architectural uncertainty.

The ordering rule: each research mission unlocks the next.
Skipping a dependency means the downstream doc has to invent
context it should have inherited.

```
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 0 — Governance + Authority Evolution  ✓ CLOSED S1269     │
│                                                                  │
│  Shipped: docs/research/governance_authority_evolution.md       │
│  4 governance planes; 35 runtime gates; 12 failure modes;       │
│  authority enforcement blocked on Symbol Mapping prereq         │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 1 — Symbol Mapping Architecture  ✓ CLOSED S1270          │
│                                                                  │
│  Shipped: docs/research/symbol_mapping_architecture.md          │
│  57 unique action_class strings; 5 mapping options (A-E);       │
│  20 enforcement boundaries; 23 identifier registries; F11       │
│  captures 7 architectural blind spots. Rigby SIGN-with-edits    │
│  (2 must-fix + 3 optional + 2 discoverability folded).          │
│                                                                  │
│  Answered: WHAT action happened?                                │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 1b — Actor Identity & Attribution  ✓ CLOSED S1271        │
│  (same-session follow-on to STAGE 1; surfaced during Symbol     │
│   Mapping verifier loops as the composite prereq)               │
│                                                                  │
│  Shipped: docs/research/actor_identity_attribution_             │
│           architecture.md                                       │
│  19 identity concepts; 22 attribution surfaces (F1: OpsRun has  │
│  no user FK); 15 historical failures; 25 registries; §8.5       │
│  executor/sponsor/principal 3-role vocabulary; F11 warning      │
│  against single-actor label conflation. Rigby pressure-test     │
│  SIGN-with-edits (4 must-fix + 2 optional folded).              │
│                                                                  │
│  Answered: WHO performed the action?                            │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 2 — Authority Enforcement Design Space  ✓ CLOSED S1272   │
│                                                                  │
│  Shipped: docs/research/authority_enforcement_design_space.md   │
│  24 inputs; 20 boundaries (17 + 3 SIGN-added WebSocket/Fleet/   │
│  Spider); 12 modes; 6 design options A-F enumerated neutrally;  │
│  15 anti-patterns (3 Tier-0 hazards); 15-prereq DAG.            │
│  Rigby pressure-test SIGN-with-edits, Medium confidence.        │
│                                                                  │
│  Type: DESIGN-SPACE research (first mission carrying design-    │
│  space content per §9 pacing). No option chosen. No design      │
│  decision. Chris gates any downstream selection.                │
│                                                                  │
│  Maintenance note: §1.8 is design-space only. The 6 options     │
│  are for future consumption; none is designated for             │
│  implementation. Do not treat as implementation greenlight.     │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 3 — Symbol Mapping Option Selection Design  ✓ CLOSED    │
│  S1274                                                          │
│                                                                  │
│  Shipped: docs/research/                                         │
│    symbol_mapping_option_selection_design.md (§1.10)            │
│  5 parallel sub-agents; 100-cell coverage matrix; drift         │
│  ranking; actor compatibility per option; failure modes.        │
│  **Recommendation: Option E (evidence-only) as v0** with 4      │
│  Rigby must-fix edits folded (generalization tone alignment;    │
│  catastrophic-action graduation guardrail; non-NULL             │
│  misclassification drift pattern; employee_handle vs.           │
│  executor_actor distinction). Rigby SIGN-with-edits, Medium     │
│  confidence, recommendation = Modify.                           │
│                                                                  │
│  Maintenance note: Option E is v0-only recommendation, NOT      │
│  implementation and NOT enforce-mode. Chris gates all           │
│  downstream steps. §10.3.1 guardrail forces re-decision.        │
├──────────────────────────────────────────────────────────────────┤
│  STAGE 4 — Symbol Mapping Event Schema Design  ✓ CLOSED S1275   │
│                                                                  │
│  Shipped: docs/research/                                         │
│    symbol_mapping_event_schema_design.md (§1.12)                │
│  Two-surface event stream (`OpsRunEvent` mission-scoped +       │
│  `ToolCallRecord.parameters` non-mission tool calls) unified    │
│  via new `authority_action_observed_stream` DB view. 21 payload │
│  fields. 4 v0 emitters + 1 v0 first consumer. Confidence enum   │
│  {DEFINITE, DECLARED (non-authoritative), HEURISTIC (banned),   │
│  UNKNOWN}. Drift stack: NULL rate + zero-fire (S1245 reuse) +   │
│  weighted cross-emitter disagreement + weekly sampled truthing  │
│  + invariants I1-I7 + schema-signature check. 3 golden flows.   │
│  Batch-mode dashboard. 5-phase ~10-week rollout sketch.         │
│  Rigby SIGN-with-edits (8 must-fixes + bonus #9 folded).        │
│                                                                  │
│  Maintenance note: §1.12 is design-preparation only. Not        │
│  implementation. Not enforce-mode. Rollout §15 is sequencing    │
│  sketch, not merged PR. Chris gates every subsequent PR.        │
├──────────────────────────────────────────────────────────────────┤
│  STAGE 5 — no P0 gates the arc.                                 │
│                                                                  │
│  Both §5.3 Trust Propagation Model and §5.4 Employee Boundary   │
│  Escalation Contract are P1 with no P0 in front. Chris picks    │
│  the next STAGE.                                                │
│                                                                  │
│  Parallel-safe with the whole-platform arc's top-3 next         │
│  missions per §1.9 §9 — Revenue Pipeline canonical              │
│  architecture (§5.12), Observability Deduplication Audit        │
│  (§5.13), Sports/DBAO ↔ AI Studio Integration Sketch (§5.14).   │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 3b — Actor Role Propagation Design  (P1)                 │
│                                                                  │
│  Two layers per §1.8 §14.2 clarification:                       │
│  (i) Role schema + propagation contract — parallel-safe with    │
│      STAGE 3 (does not depend on Symbol Mapping option)         │
│  (ii) Implementation across boundaries — depends on STAGE 3     │
│       shipped                                                    │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 3c — Authority Enforcement Design Decision  (P1)         │
│                                                                  │
│  Convert §1.8's 6 design-space options into an actual design    │
│  decision. Consume §1.8's 33-incident catalog, 15 anti-         │
│  patterns, 15 prereqs. Rigby SIGN + Chris gate.                 │
└──────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  STAGE 4a       │  │  STAGE 4b       │  │  STAGE 4c       │
│  Trust          │  │  Memory         │  │  Mission        │
│  Propagation    │  │  Architecture   │  │  Composition    │
│  (§5.3)         │  │  (§5.4)         │  │  (§5.6)         │
│                 │  │                 │  │                 │
│  Inter-employee │  │  Cross-employee │  │  Canonical      │
│  trust contract │  │  episodic       │  │  idempotency    │
│  (today only    │  │  memory shape   │  │  key across     │
│  per-employee   │  │                 │  │  orchestration  │
│  trust exists)  │  │                 │  │  paths          │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                ┌──────────────────────────────┐
                │  STAGE 5                     │
                │  Cross-Employee Scheduling   │
                │  (§5.5) — depends on Stage   │
                │  4a + 4b + 4c                │
                └──────────────┬───────────────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │  STAGE 6                     │
                │  Employee Delegation Design  │
                │  (DESIGN, not research —     │
                │  prerequisites must close    │
                │  first)                      │
                └──────────────┬───────────────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │  STAGE 7 — Implementation    │
                │  (PRs, with research as the  │
                │  justification artifact)     │
                └──────────────────────────────┘

Lateral research that does not block the main chain:

  • Cross-plane Composition (§1.7 F10 + governance F1) — how do
    autonomy / authority / budget / human governance compose
    when all four are active? Blocking STAGE 2 completeness.
  • Security / Permission scoping (§5.8) — if cross-fleet
    surfaces enter scope.
  • Configuration Architecture note (§5.9) — when feature-flag
    growth becomes a documentation problem.
  • Observability consolidation (§5.7) — optional; no blocking
    downstream.
  • Knowledge Graph scoping (§5.10) — only if a use case
    materializes.
  • Focus Mode inventory (§5.11) — if Employee OS reasoning
    surfaces a dependency on it (flagged by Rigby S1269).

  Whole-platform arc (added S1273 v5 — parallel-safe to the
  Employee OS depth arc above):

  • §5.12 Revenue / Outreach / Engagement Pipeline canonical
    architecture doc — P0 parallel. Missed domain caught by
    Rigby S1273 review; blocks any revenue-adjacent work.
  • §5.13 Observability Deduplication Audit — P1. Trace a
    single execution scenario through 5 telemetry layers.
  • §5.14 Sports/DBAO ↔ AI Studio Integration Sketch — P1.
    Structural question about whether platform is one or two.
  • Full 11-mission whole-platform roadmap: see §1.9 §9
    (Notification Unification, Event Bus Producer/Consumer
    Map, Rigby v0 Event Intake Activation Plan, Advisor
    Persistence Contract, Content ↔ Initiative Wiring Audit,
    LLM Provider Failover + Cost Tracking, Claude Code
    Tooling Design Doc, etc.).
```

**Pacing note.** Stages 0 through 1b were pure research —
inventory + classification + failure analysis. STAGE 2
(Authority Enforcement Design Space) is the first mission with
*design* content: the doc will contain a proposal Chris must
gate. Stages 3-4 return to pure research; Stage 5 is design;
Stage 6 is implementation. The discipline that holds this
together is the verifier loop + Rigby SIGN review on every
transition.

---

## 10. Maintenance Rules

This index must evolve in lockstep with the library. The
rules below apply whenever any change happens.

### 10.1 When a new research doc is added

Within the same PR (or same session if no PR yet):

1. **Add a row to §1.** With Title / Purpose / Status / Type /
   Primary questions / Dependencies / Recommended next reads /
   Importance.
2. **Add the doc to §4 dependency graph.** Show its parents
   (via `companion_docs`) and where it sits in the lineage.
3. **Update §2 reading paths.** If the new doc belongs in
   Path A-G (or a new path), add it.
4. **Update §3 domain map.** Move the relevant domain row's
   "Missing research" → "Existing research" (or update
   maturity).
5. **Update §5 gaps.** If the new doc closes one of the named
   gaps, mark it closed with a pointer. If it surfaces new
   gaps, add them.
6. **Update §7 decision matrix.** If there's a class of work
   that should now read the new doc first, add the row.
7. **Update §8 timeline.** Append a new row chronologically.
8. **Update §9 roadmap.** If the new doc was the next stage,
   move the arrow forward.
9. **Bump `last_verified` in this doc's frontmatter.**

### 10.2 When a research doc is superseded

1. Add a pointer header at the top of the superseded doc per
   `DOC_LIFECYCLE.md` V2 conventions.
2. In §1, change Status to `Deprecated` and add a "Superseded
   by: [link]" line.
3. In §4, move the superseded doc to a "historical" footnote
   below the main graph. Do not remove from the corpus —
   per memory rule `feedback_docs_never_delete`, preservation
   matters.
4. In §7 decision matrix, replace references to the
   superseded doc with the successor.

### 10.3 When a doc's status changes (Draft → Active, Active → Canonical)

1. Update the doc's own frontmatter `status` field.
2. Update §1 row Status column.
3. If the doc has been moved to Canonical, add it to the
   appropriate canonical-anchor list in adjacent docs
   (`PLATFORM_INVENTORY.md`, `EMPLOYEE_OS_PRIMITIVES.md`,
   or this index's frontmatter `companion_anchors` if
   applicable).

### 10.4 When drift between docs is discovered

1. Per `DOC_LIFECYCLE.md` §2c: **inventory wins** on counts.
2. Add a drift call to the *newer* doc's drift section (every
   research doc has one — substrate audit cross-reference
   lives in Appendix A, collaboration patterns drift section
   lives in its §12).
3. Do **not** silently edit the older doc. If the older doc
   needs correction, that's a separate review pass with its
   own SIGN verdict.

### 10.5 When this index itself drifts from the library

If `ls docs/research/` shows a doc that isn't in §1, that's
the index's drift. Open a small fix-up PR that just updates
§1, §4, §5, §7, §8. Do not bundle it with anything else.

### 10.6 Authority on this index

This index is **authority: navigation**, not
**authority: canonical** — it points to canonical docs
without being one. If the index disagrees with a canonical
anchor (EMPLOYEE_OS_PRIMITIVES, PLATFORM_INVENTORY,
DOC_LIFECYCLE), the anchor wins; the index gets edited.

---

## Appendix A — Verifier-loop pass notes

This index was drafted from direct inventory of
`docs/research/` at 2026-06-30 (`ls` showed 3 .md files),
plus frontmatter re-reads of each, plus cross-reference
against `docs/` canonical anchors via `Glob`.

**Self-verifier pass (one round) before finalization
identified and fixed:**

- **Missing doc check.** `ls docs/research/` returns exactly
  3 files; all 3 cataloged in §1. No subdirectories. No
  hidden docs. ✓
- **Duplicate classifications.** Originally tagged §1.1 as
  pure "Inventory"; on second pass added "+ Architecture
  Audit + Failure Analysis" because §7 of that doc is
  substantively failure analysis. Same fix on §1.3. ✓
- **Dependency ordering.** First draft showed §1.2 and §1.3
  as parallel children of §1.1 in §4 graph. Re-verified
  against the actual creation order (§1.2 was written
  *before* §1.3 within the same session) and timeline §8 —
  graph is correct; chronologically §1.3 was the audit that
  surfaced the "wider question" raised by Rigby's review of
  §1.2. ✓
- **Inconsistent statuses.** First draft listed all three as
  "Active." Re-read each frontmatter and found all three are
  literally `status: draft` per their YAML. Updated §1 rows
  to "Draft → Active (SIGN-... from Rigby)" to honor both the
  frontmatter literal and the review-state reality. ✓
- **Discoverability.** Originally Path G ("platform
  reliability") didn't mention the client factories. Added
  the hard-rule callout on `anthropic_client_factory.py` /
  `openai_client_factory.py` because the memory rules
  (`feedback_anthropic_client_factory`,
  `feedback_openai_client_factory`) and the zombie-thread
  failure class (§1.3 §7 row 17) all converge on that
  enforcement. ✓
- **§3 domain map** — Memory domain originally not listed;
  added on second pass because §5.2 calls it out as a real
  research gap. Same for Knowledge Pipeline (added per
  `KNOWLEDGE_PIPELINE.md` existing as a canonical anchor
  outside the research library). ✓
- **§7 decision matrix** — first draft was missing the row
  for `MissionRunnerConfig.auto_emit_verdict`. Added on second
  pass because the protocol-invariant-change row (§1.3 §7 row
  29) was Rigby's SIGN-with-edits correction and deserves a
  decision-matrix anchor of its own.

**Status after self-verifier pass.** Publishable as v1.
Rigby independent SIGN review on this index is **not**
required per S1268 mission spec scope (the spec asks for a
verifier loop, not a Rigby pass on the index itself). If a
future session wants Rigby's read on the index, that's a fine
small follow-up.

## Appendix B — v3 update pass notes (S1271)

Triggered by the same-session landing of both `symbol_mapping_architecture.md`
(§1.6) and `actor_identity_attribution_architecture.md` (§1.7).
Both docs completed the verifier loop + Rigby SIGN review before
this index update, so §10.1 was applied wholesale.

**Verification pass (one round) before finalization:**

- **Missing doc check.** `ls docs/research/` now shows 6 files
  (5 research + this index). Both new docs cataloged in §1.6
  and §1.7 respectively. No subdirectories. No hidden docs. ✓
- **Section renumbering.** §5.2 (was "Symbol Mapping — P0
  recommended next" pre-close) marked CLOSED with pointer to
  §1.6. §5.2a added for Actor Attribution close. §5.2b added
  for new P0 next research (Authority Enforcement Design
  Space). Prior §5.3-§5.11 numbering preserved so downstream
  references don't break; renumbering deferred to a future pass
  if it becomes needed. ✓
- **Roadmap stage advancement.** Prior STAGE 1 (Symbol Mapping)
  marked CLOSED. New STAGE 1b (Actor Attribution) inserted as
  same-session follow-on. New STAGE 2 (Authority Enforcement
  Design Space) is the "recommended next." Prior STAGE 2a/2b/2c
  (Trust Propagation / Memory / Mission Composition) renumbered
  to STAGE 3a/3b/3c. Downstream stages (Cross-Employee
  Scheduling → 4, Employee Delegation Design → 5,
  Implementation → 6) bumped by one. ✓
- **Dependency graph.** ASCII diagram in §4 extended with two
  new boxes for §1.6 and §1.7 in the correct downstream
  position, then the "Future research mission" box updated to
  point at Authority Enforcement Design Space (was previously
  pointing at Symbol Mapping, now landed). ✓
- **Domain map.** Governance row's "Missing research" cleared
  (Symbol Mapping was the pending item, now shipped);
  downstream noted as Cross-plane Composition. Authority row
  updated: existing research now includes §1.6 + §1.7; missing
  research is Authority Enforcement Design Space. New "Actor
  Identity / Attribution" domain row added citing §1.7 with
  F1's OpsRun gap as the flagship finding. ✓
- **Decision matrix.** 7 new rows added covering:
  `JobContract.authority` use; actor identity on any new model /
  audit surface; adding user field to OpsRun (explicit
  anti-pattern warning per §1.7 F1 + F11); code using
  `agent_name` CharField anywhere (F4 ambiguity); code using
  `runs_as_username` (F3 + F11); duplicate Agent row risk (F5);
  PA tool actor/user context propagation (§1.6 §6 + §1.7 §7).
  Prior "Authority enforcement (vs. observation)" row updated
  to cite §1.6 + §1.7 + §5.2b instead of the now-closed §1.4 §11
  recommendation. ✓
- **Timeline.** 2 rows appended (S1270 + S1271) with full
  content summaries + influence callouts. Pattern observation
  updated to reflect the 3-session growth cadence
  (S1269/S1270/S1271) after the S1268 burst. ✓
- **Discoverability.** Both new docs now surface via §1
  (rows), §3 (domain map, esp. new Actor Identity row), §4
  (dependency graph position), §5 (closed-gap + new-gap
  entries), §7 (7 new decision-matrix rows), §8 (timeline
  chronology), and §9 (roadmap stage boxes). Reading paths §2
  not extended in this pass; a Path H for "understanding actor
  identity end-to-end" was considered but deferred — Paths A-G
  already cover the reading order via §1.6 and §1.7's
  companion_docs frontmatter chains. Future session can add
  Path H if requested. ✓
- **Frontmatter last_verified.** Bumped from "v2" to "v3" with
  a summary line naming the two shipped docs + the roadmap
  advancement. verifier_loop field expanded with the v3
  changes and prior v1/v2 history preserved. owner field
  extended: "v3 update S1271." ✓

**Status after v3 pass.** Publishable as v3. Both new docs are
discoverable via all 8 index sections (§1-§9 plus this appendix
+ maintenance rules). Rigby independent SIGN review on the
index itself remains optional per §10 discipline; if requested,
a small follow-up pass suffices.

## Appendix C — v4 update pass notes (S1273 Part 1)

Triggered by S1272's landing (`authority_enforcement_design_space.md`)
during S1273's Part 1 documentation-maintenance work. This is
the first update that includes an explicit **maintenance note**
that a docs/research/ entry is design-space only — not
implementation greenlight — per S1273 mission-spec requirement.

**Verification pass (one round) before finalization:**

- **Missing doc check.** `ls docs/research/` now shows 7 files
  (6 research + this index). §1.8 added for `authority_enforcement_design_space.md`.
  No subdirectories. ✓
- **Design-space vs. implementation distinction.** §1.8 status,
  §3 domain map row ("Authority Enforcement (design space)"),
  §5.2b closure note, §7 decision matrix new row on enforcement
  ideas, §8 timeline row, and §9 roadmap STAGE 2 box all
  explicitly state that §1.8 is **design-space only**. This is
  the explicit "maintenance note that Authority Enforcement is
  still design-space only, not implementation" required by
  S1273 mission spec. ✓
- **Roadmap advancement.** Prior STAGE 2 (Authority Enforcement
  Design Space) marked CLOSED S1272. Two new stages added
  parallel-ordered: STAGE 3 (Symbol Mapping Option Selection
  Design — the recommended P0 next), STAGE 3b (Actor Role
  Propagation Design — P1 parallel-safe on Layer (i)), STAGE
  3c (Authority Enforcement Design Decision — P1). Prior
  STAGE 3a/3b/3c (Trust Propagation / Memory / Mission
  Composition) renumbered to STAGE 4a/4b/4c. Downstream stages
  bumped: Cross-Employee Scheduling → 5, Employee Delegation
  Design → 6, Implementation → 7. ✓
- **Dependency graph.** ASCII diagram in §4 extended with new
  §1.8 box (with SIGN-added-boundaries callout). "Future
  research mission" downstream box updated to point at Symbol
  Mapping Option Selection Design (was Authority Enforcement
  Design Space, now landed). ✓
- **Domain map.** Authority row expanded to include §1.8;
  "Missing research" changed from "Authority Enforcement Design
  Space" to "Symbol Mapping Option Selection Design"; maturity
  bumped from "Medium" to "Medium-High" (all three prereqs now
  shipped as research). New "Authority Enforcement (design
  space)" row added citing §1.8 with explicit design-space-only
  maintenance note. Actor Identity row updated to reflect the
  new gating mission. ✓
- **Decision matrix.** 6 new rows added covering: any authority
  enforcement idea (must consult §1.8 anti-patterns + prereqs),
  AuthorityLevel enum usage anywhere new (F1 warning about
  single runtime consumer), new INLINE enforcement gate (F8
  fail-open precedent), adding action_class to any audit model
  (prereq #3 + #4), WebSocket/Fleet/Spider handlers touching
  employee-scoped work (§3 rows 18-20), cross-plane governance
  interaction (§7.5 8 questions). ✓
- **Timeline.** 1 new row appended (S1272) with content
  summary + influence callout. ✓
- **Discoverability.** §1.8 now surfaces via §1 (§1.8 row), §3
  (domain map — Authority row + new Authority Enforcement row),
  §4 (dependency graph position), §5 (§5.2b closed + new §5.2c
  gap), §7 (6 new decision-matrix rows), §8 (timeline), §9
  (roadmap STAGE 2 CLOSED + STAGE 3/3b/3c). ✓
- **Frontmatter.** Bumped from "v3" to "v4" with change
  summary. verifier_loop field expansion deferred to v5 or
  next larger update to keep this pass focused. owner field
  will be extended: "v4 update S1273 Part 1" at commit time. ✓

**Status after v4 pass.** Publishable as v4. §1.8 discoverable
via all 8 index sections. Maintenance note explicit at 4 sites
(§1.8 status, §3 row, §5.2b, §9 STAGE 2 box). Rigby independent
SIGN review on the index itself remains optional per §10.

**Frontmatter-drift note (caught S1273 v5).** The v4 pass
updated Appendix C but forgot to update the frontmatter's
`last_verified` and `owner` fields to reflect v4. That drift
was carried forward until S1273 v5 caught + corrected both.
Small process lesson: bump frontmatter in the same edit as the
appendix note; do not defer.

## Appendix D — v5 update pass notes (S1273 Part 2)

Triggered by S1273's landing of `platform_architecture_
inventory.md` (§1.9) as the first whole-platform architectural
inventory. Chris's direction at S1273 close: "the next cleanup
should be updating ARCHITECTURE_INDEX.md so this becomes the
whole-platform counterpart to the Employee OS research
library." This is the first update that expands the library's
scope from Employee-OS-focused-only to Employee-OS-arc PLUS
whole-platform inventory as a sibling arc.

**Verification pass (one round) before finalization:**

- **Missing doc check.** `ls docs/research/` now shows 8 files
  (7 research + this index). §1.9 added for
  `platform_architecture_inventory.md`. No subdirectories. ✓
- **Scope split acknowledgment.** §1 preamble rewritten to
  distinguish (a) Employee OS arc §1.1-§1.8 (deep on one
  subsystem, S1268-S1272) from (b) whole-platform inventory
  §1.9 (wide on all subsystems, S1273). "When to read which"
  guidance added. ✓
- **Reading path.** New Path H "I need to understand the whole
  platform" added — CLAUDE.md → PLATFORM_WHAT_IT_IS →
  PLATFORM_INVENTORY → §1.9 → specific §3.n → optional
  Employee-OS-arc doc if subsystem covered. ✓
- **Domain map.** New Revenue / Outreach / Engagement row
  added citing §1.9 §3.32 + underlying models + services.
  Rigby caught this as a missed platform subsystem during
  S1273 SIGN review; folded into §1.9 §3.32 + registered here
  as new domain row per §10.1. Rest of §3 unchanged — the
  17-domain Employee-OS-adjacent view remains valid; §1.9's
  32-domain whole-platform view is complementary. ✓
- **Dependency graph.** Sibling-arc ASCII diagram added below
  the main graph, showing §1.9 as parallel to the Employee OS
  arc off the same three anchors (PLATFORM_INVENTORY +
  PLATFORM_WHAT_IT_IS + EMPLOYEE_OS_PRIMITIVES). §1.9 cites
  downstream findings from §1.4 + §1.6 + §1.7 where they overlap
  its own findings, but does NOT depend on the arc's ordering. ✓
- **Gap closures and additions.** §5.4 Memory Architecture
  noted as partially covered by §1.9 §3.13 (Memory / Knowledge
  / Embeddings — DEEP coverage; 5 memory tables enumerated,
  14-day freshness contract, PA-to-Agent feedback closure,
  auto-save ops facts). Three new gaps added — §5.12 Revenue
  Pipeline canonical architecture (P0 parallel; missed-domain
  finding from Rigby's S1273 review), §5.13 Observability
  Deduplication Audit (P1; addresses §1.9 §5.7 5-layer
  telemetry duplication), §5.14 Sports/DBAO ↔ AI Studio
  Integration Sketch (P1; addresses §1.9 §3.10 island-vs-
  integrated structural question). ✓
- **Decision matrix.** 3 new whole-platform rows added:
  onboarding / cross-domain scoping (start at §1.9); Revenue/
  Outreach/Engagement/Meeting/ClosePack work (§1.9 §3.32 +
  §4.9 + §5.12 gap); sports-betting content integration
  (§1.9 §3.10 + §4.8 + §5.14 gap). ✓
- **Timeline.** 1 new row appended (S1273, 2026-07-01) with
  content summary + Rigby SIGN-with-edits detail (Medium
  confidence, 6 substantive edits folded incl. missed Revenue
  Pipeline domain) + Chris's whole-platform-counterpart
  direction. Timeline note extended to reference the fresh
  isolation pin `pa-02cfd3206302352f` used for §1.9's Rigby
  review (kept separate from shared S1270+ arc pin
  `pa-cbcc410b32714f60` mid-session per context-crossing
  directive). ✓
- **Pattern observation.** Section 8 pattern-observation
  paragraph updated to reflect the two-wave library shape —
  first wave S1268-S1272 (Employee OS depth arc), second wave
  S1273 (whole-platform sibling arc). Next growth events now
  split: (a) Employee OS arc STAGE 3 Symbol Mapping Option
  Selection Design (Chris-gated); (b) whole-platform arc
  top-3 next missions (§5.12/§5.13/§5.14). Parallel-safe. ✓
- **Roadmap.** §9 lateral research list expanded to reference
  whole-platform arc with §5.12/§5.13/§5.14 as the top-3 next
  missions + pointer to §1.9 §9 for the full 11-mission
  roadmap. ✓
- **Frontmatter.** Bumped from "v4" to "v5" with change
  summary. verifier_loop field expanded with v5 changes and
  prior v1-v4 history preserved. owner field extended: "v5
  update S1273 Part 2." Also caught + corrected v4 frontmatter
  drift (v4 pass updated Appendix C but never bumped
  last_verified — see Appendix C's Frontmatter-drift note
  above). ✓
- **Discoverability.** §1.9 now surfaces via §1 (preamble +
  §1.9 row), §2 (new Path H), §3 (Revenue Pipeline row +
  cross-reference to §1.9's 32-domain map), §4 (sibling-arc
  dependency graph extension), §5 (§5.12/§5.13/§5.14 new gap
  entries + §5.4 partial-coverage note), §7 (3 new decision-
  matrix rows), §8 (timeline row + pattern-observation
  update), §9 (roadmap lateral research expansion). ✓

**Status after v5 pass.** Publishable as v5. §1.9 discoverable
via all 9 index sections. Dual-scope library shape is now
explicit throughout the doc (§1 preamble, §2 Path H, §4 sibling
arc, §8 pattern observation, §9 lateral research). Rigby
independent SIGN review on the index itself remains optional
per §10.6 — the index is `authority: navigation`, not
`authority: canonical`; anchors win when they disagree with the
index.


## Appendix E — v6 + v7 update pass notes (S1274)

Two concurrent S1274 registrations landed in the same day:

**v6 (concurrent CC session).** Registered §1.10
`symbol_mapping_option_selection_design.md` (STAGE 3 Symbol Mapping
Option Selection Design mission — Chris-gated recommendation of Option
E as v0). Frontmatter bumped v5 → v6; timeline row added; roadmap
advanced STAGE 3 CLOSED / new STAGE 4 Event Schema Design. No
appendix pass notes written by that pass — noted for record.

**v7 (this pass).** Registered §1.11 `DOMAIN_RESEARCH_PLAYBOOK.md`.

### Verification pass (v7) before finalization

- **Missing doc check.** `ls docs/research/` shows the playbook
  present as `DOMAIN_RESEARCH_PLAYBOOK.md`. Registered as §1.11. ✓
- **Concurrent-session coordination.** Detected that a parallel CC
  session bumped v5 → v6 for §1.10 while this session was drafting
  the playbook. Handled by: (a) reading the current v6 frontmatter
  before editing, (b) building on top of v6 with a v6 → v7 bump
  rather than a v5 → v6 clash, (c) adding a note in this appendix
  that v6 concurrent session did not add its own appendix. No
  content loss; both S1274 registrations coexist. ✓
- **Authority-type distinction.** §1.11 is `authority: process`, the
  first process doc in the library. Distinguished in the §1.11 row
  text so readers know it sets rules for other docs rather than
  producing findings. Considered adding a new §11 "Process Documents"
  section separately from §1; decided against — one process doc
  today does not justify a new section, and readers looking for
  "what to read first" benefit from playbook being adjacent to
  research docs. ✓
- **Discoverability.** §1.11 surfaces via §1 (row) + §8 (timeline).
  Reading paths §2 not extended in this pass — the playbook does
  not fit any existing goal-based path (it is for people STARTING
  a domain audit, not any of the current A-H personas). A future
  Path I "I want to start a domain audit" could be added if session
  volume in the 1300-1900 range grows; deferred for now since
  §1.11 row and §8 timeline give sufficient entry points. ✓
- **Domain map §3.** Not updated in this pass — playbook is process
  meta, not a domain finding. No new domain row applies. ✓
- **Gaps §5.** Not extended in this pass — playbook sets research
  GROUP structure (queue in §12 of the playbook itself); §5 tracks
  research gaps in specific domains, which is orthogonal. ✓
- **Decision matrix §7.** Not extended — playbook governs how future
  audits get written, not what class of work triggers reading a
  specific doc. Row could be added in future: "About to start a
  domain audit → read DOMAIN_RESEARCH_PLAYBOOK.md first." Deferred. ✓
- **Roadmap §9.** Not modified in this pass — playbook does not
  advance any specific research stage; it enables the next 7 groups
  in parallel-safe fashion (§12 of the playbook). ✓
- **Frontmatter.** Bumped v6 → v7. verifier_loop preserved v1-v6
  history; added v7 note about concurrent-session coordination.
  owner field extended: "v7 update S1274 Part 2 [§1.11
  DOMAIN_RESEARCH_PLAYBOOK]." ✓

**Status after v7 pass.** Publishable as v7. §1.11 discoverable via
§1 (row) and §8 (timeline). Concurrent v6 session note preserved.
Rigby SIGN review on the index itself remains optional per §10.6.
