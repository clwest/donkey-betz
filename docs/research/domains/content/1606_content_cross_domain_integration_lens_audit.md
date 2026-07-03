---
title: "Content Category F — Cross-Domain Integration Lens & Posture Decision Framing (LAST Child Audit)"
status: active
authority: research
research_group: 1600
domain_slug: content
session: 1606
category: child_audit
child_slot: P6
generated: 2026-07-02
last_verified: 2026-07-02
dependencies_on:
  - Group 1600 parent (1600_content_domain_scoping.md — Cat F scope at §3 F; F11 boundary rule "LAST child + consumes P1-P5 evidence + produces xx99 posture-decision evidence plan; Cat F does NOT re-open earlier children"; D66 P6 slot)
  - Group 1600 P1 S1601 (1601_content_claims_pack_deliberation_pipeline_v2_audit.md — SignalCluster read-only consumer; T1 R.CONTENT.RAG-SCOPE riskiest overall; T1 R.CONTENT.CITATION-INTEGRITY)
  - Group 1600 P2 S1602 (1602_content_reviewers_decision_enforcement_audit.md — Cat B ZERO PA-tool outbound; queue_agent_task landmine; v1 ContentReviewPanel PARTIALLY-ADOPTED-LIVE-SECONDARY)
  - Group 1600 P3 S1603 (1603_content_deliverable_base_variants_audit.md — Cat D 3-category variant taxonomy neutral D65a evidence; SportsBettingBrief + BlockchainAuditBrief unfinished/orphan; OutreachDraft + ClosePack standalone-by-design; SelfBlog + PodcastEpisode envelope→object integrated)
  - Group 1600 P4 S1604 (1604_content_publish_gate_publish_rails_audit.md — PublishGate SelfBlog-only; triple-gate composition contract MISSING; post-publish correction loops STRUCTURALLY ABSENT; force=true audit trail absent)
  - Group 1600 P5 S1605 (1605_content_rigby_pa_tooling_approval_ux_audit.md — 4-tool split TACTICAL not STRUCTURAL; xx99 anchor sentence LOCKED "Preserve the 4-tool interface, but centralize enforcement (auth/audit/scope/gates) so the split can't produce divergent behavior"; T.15.E2 CRITICAL REST auth-boundary; T.15.E4 auto_publish beat runtime-verified ABSENT)
  - Group 1500 P4 S1504 (1504_sports_betting_content_pipeline_audit.md — SportsBettingBrief WRITE-ONLY-FORGOTTEN CRITICAL; SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS HIGH; extends to Cat F Content↔Sports lens)
  - Group 1400 P2 S1402 (1402_revenue_outreach_composition_delivery_audit.md — F.B1 OutreachDraft delivery ZERO outbound F8-CRITICAL; pattern class 3-of-3 confirmed at HEAD across Newsletter + OutreachDraft + BlockchainAuditBrief; extends to Cat F Content↔Revenue lens)
  - Group 1400 P3 S1403 (1403_revenue_engagement_inbound_audit.md — F.C4 ContentEngagement docstring drift HIGH CONFIRMED at HEAD; extends to Cat F Content↔Memory learning-loop lens)
  - Group 1500 P2 S1502 (1502_sports_prediction_analytics_agents_audit.md — SignalCluster.pattern_type consumer-side gap 6-arc COMPLETED; Content Cat A consumer contract flags cross-arc completion for Cat F consolidation)
  - S1599 (1599_sports_canonical_summary.md — Group 1500 xx99 §5 posture-decision evidence plan exemplar for Cat F §20.6 F2 fold rubric adoption)
delegates_to:
  - xx99 S1699 — canonical summary (consumes Cat F §20.6 posture-decision evidence plan per D65a/D65b/D65c/D65e four-axis framing; consumes Cat F §17 duplicate/overlapping systems consolidation; consumes Cat F §19 T1/T2 cross-arc queue)
verifier_loop: parent-Claude verifier-loop (playbook §14 rule) on load-bearing cross-domain binary claims grep-verified against HEAD `c7a3c16e` (post-S1605 merge). **Explore-agent sweeps NOT spawned this session** per S1606 punch list allowance: "Cat F may use fewer than 6 Explore sub-agents since it's an evidence-consolidation lens rather than fresh-domain audit." Instead: (a) consume 5 sibling audit outputs verbatim per parent F11 boundary rule; (b) run targeted greps to cross-verify sibling-emitted cross-domain binary claims at HEAD; (c) synthesize §20.6 posture-decision evidence plan from P1-P5 evidence + S1504 + S1402 + S1403 + S1502 cross-arc inputs. **Rigby SIGN Cycle 1 SIGN-with-edits at High confidence overall (Batch A 0.78 + Batch B 0.70 + Batch C 0.83 + final consolidated 0.82) on fresh isolation pin `pa-8cfafefb67864f83`** (Rigby-side `session_tool.create_fresh`; retired at S1606 close via `session_tool.retire`). **F1-F10 folds landed pre-commit** including F1 `newsletterApi` grep 0-hit correction + F3 pattern class 3-of-3 → 2-of-2 rebucketing (BlockchainAuditBrief stays at Sports not Revenue-adjacent) + F6 §9.4 PARTIAL PA-tool feedback bridge acknowledgment + F10 §9.7 Employee OS PARTIAL not ABSENT (Rigby Documentation Manager Content-adjacent overlap). **D48 preemptive stability-probe gate 15th arm outcome — TEN-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606 CONFIRMED** — codification-ready-STRENGTHENED-FURTHER for playbook v3 §15.
---

# Session 1606 — Group 1600 Cat F: Cross-Domain Integration Lens & Posture Decision Framing (LAST Child Audit)

## 1. Executive Summary

Cat F is the sixth and **LAST** child audit under Group 1600 (Content Domain), executing per parent D66 P6 slot after Cat A (S1601 ClaimsPack) + Cat B (S1602 Reviewers) + Cat D (S1603 Deliverable Base) + Cat C (S1604 PublishGate) + Cat E (S1605 Rigby PA Tooling). Cat F answers the parent-scoped boundary question — *how does the Content domain integrate with the rest of the platform, and what posture-decision evidence does xx99 need to select D65a/D65b/D65c/D65e postures?* Per parent F11 boundary rule: **Cat F is evidence-consolidation lens; Cat F does NOT re-open earlier children; Cat F produces xx99 posture-decision evidence plan per D65-analog four-axis framing.**

The parent §3 F boundary — *"cross-domain integration surfaces + posture-decision evidence plan owed to xx99"* — resolves as **seven cross-domain surfaces with structurally-asymmetric integration maturity**. Content is a **partial-consumer + partial-producer + partial-integrator** across the platform: it READS from Signal Engine + Sports + Memory but EMITS almost nothing back; it OWNS Discord + Frontend broadcast rails but has no post-publish correction; it lacks Employee OS representation and Revenue outbound delivery. This audit records the seven-surface integration map + evidence per surface + posture-decision evidence plan for xx99 D65a/D65b/D65c/D65e Chris-gated ADR.

### 1.1 Headline findings

- **Seven cross-domain integration surfaces inventoried at HEAD `c7a3c16e`.** *Definitional clarification per Rigby SIGN Batch A F2 fold:* "surface" spans BOTH runtime data-flow integrations (Signal / Sports / Revenue / Memory / Discord / Frontend) AND platform governance/ownership interfaces (Employee OS as governance-layer surface). The 6+1 split is intentional; observability/audit is a cross-cutting concern within each surface, not a separate 8th surface. Content ↔ Signal Engine (Cat A ClaimsPack consumer); Content ↔ Sports (SportsBettingBrief + SportsContentContextBuilder + BlockchainAuditBrief cross-arc); Content ↔ Revenue (OutreachDraft + ClosePack + ContentEngagement + Newsletter cross-arc); Content ↔ Memory (learning-loop path); Content ↔ Discord (broadcast rails via `discord_notifications.py`); Content ↔ Frontend (BlogViewerPage + ContentStudioTab + blogsApi + deliverablesApi; newsletter frontend limited to public subscriber signup per F1 fold correction); Content ↔ Employee OS **(governance layer)** (D55 Revenue Employee + Income/Jobs Employee JobContract split precedent — no dedicated Content publishing/management employee analog at HEAD; Rigby Documentation Manager JobContract at `core/employees/jobs.py:187-280` provides PARTIAL Content-adjacent coverage per F10 fold). Cat F consolidates evidence per surface (§9) + produces xx99 four-axis posture-decision evidence plan (§20.6).

- **Content ↔ Signal Engine is READ-ONLY at HEAD; consumer-side contract stable, producer-side ABSENT.** `ClaimsPackBuilder._extract_signal_claims` at `core/services/claims_pack_builder.py:192` reads `SignalCluster.objects.filter(status='active').order_by('-detected_at')[:50]`. **Grep across `core/services/` for `SignalCluster.objects.create` returns 10 files** (signal_aggregation_service.py + curator + linker + fleet_signals + platform_inventory + etc.) — **NONE of which are Content-domain services**. Content does NOT emit SignalCluster from published outputs. **This confirms S1502 §14.3 6-arc consumer-side pattern completion at Content boundary** — Content is a fifth consumer domain following Sports/Revenue/Memory/Employee OS pattern. **D65-integration-posture evidence: Content as SignalCluster READ consumer is coherent with island posture (no cross-boundary write); no integration cost.**

- **Content ↔ Sports has THREE structurally-independent touch points, all in write-only-forgotten or hot-path-choke posture.** (a) **SportsBettingBrief write-only-forgotten** — 5-file footprint at HEAD (`core/tasks.py` + `core/models/__init__.py` + `core/models_unified_system.py:18394` + `core/tasks_content.py` + `core/migrations/0242_session_1003_desk_intelligence_briefs.py`); NO services/, NO views/, NO agents/ consumer at HEAD. S1504 §14.3 CRITICAL + S1603 T.15.2 CRITICAL both CONFIRMED at HEAD (grep-verified). (b) **SportsContentContextBuilder** at `core/services/sports_content_context.py` + companion at `core/services/domain_content_context.py` — S1504 §5.1 HOT-PATH-CHOKE-BYPASS HIGH; v1 `ContentWriterAgent._maybe_run_review` path can bypass builder. (c) **BlockchainAuditBrief** at `core/models_unified_system.py:18435` — S1603 §1.1 same pattern class as SportsBettingBrief (unfinished/orphan). **Cat F consolidates**: Content owns Sports variant persistence contract (Cat D confirmed islands at HEAD); Cat C confirmed 0 publish rails for SportsBettingBrief + 0 Cat C-owned rails for BlockchainAuditBrief. **D65a-consuming**: consumer-or-remove decision owed at xx99 for both Sports variants.

- **Content ↔ Revenue has THREE structurally-independent touch points, all in write-only-forgotten OR docstring-drift posture — F8-CRITICAL pattern class 2-of-2 CONFIRMED at Revenue-adjacent surface (Rigby SIGN Batch A F3 fold correction).** (a) **OutreachDraft ZERO outbound rail** — `core/models_outreach.py` + `core/tasks.py` + `core/services/pa_tool_schemas.py` (PA schema exists) + `core/celery.py` (beat exists at `generate-outreach-drafts-daily`) but **grep across all files for `sendgrid|mailgun|postmark|smtplib|SMTP|send_mail|EmailMessage` on OutreachDraft path returns 0 hits at HEAD**. S1402 F.B1 CONFIRMED at S1604 §9.6. (b) **Newsletter ZERO live-send infrastructure** — `_impl_generate_operator_edge_newsletter` at `core/tasks_content.py:4234-4413` + `newsletter_publisher.py` + `newsletter_sources.py` — same grep returns 0 hits at HEAD; `dry_run=True` hardcoded in beat since S1222 P6 (>4mo). S1604 T.15.C2 CRITICAL + S1605 F8 CONFIRMED. (c) **ContentEngagement docstring drift** — `core/models_engagement.py` docstring claims post-publish feedback loop but grep across `core/` for `ContentEngagement.objects.create` on Discord/Newsletter/Frontend publish rails returns 0 code paths writing this model post-publish. S1403 F.C4 HIGH CONFIRMED at HEAD. **F3 fold rebucketing:** Cat F draft claimed "pattern class 3-of-3" (OutreachDraft + Newsletter + BlockchainAuditBrief-analog). Rigby SIGN A2 flagged internal inconsistency — BlockchainAuditBrief is a **Sports-domain orphan variant** (Cat D §1 category 3 alongside SportsBettingBrief), NOT a Revenue outbound-delivery failure. **Corrected framing:** at Content ↔ Revenue surface the pattern is **2-of-2 (OutreachDraft + Newsletter)** — both content-generation-only with ZERO outbound delivery infrastructure. BlockchainAuditBrief pattern-class exists but at Content ↔ Sports surface (§9.2) as "unfinished/orphan variant sharing structural pattern with SportsBettingBrief" — NOT as a Revenue-adjacent delivery-domain member. **Cross-arc scope:** the broader "content output lacks outbound rail/consumption path" pattern spans Sports (2 orphan variants) + Revenue (2-of-2 delivery-domain absent) — 4 total variants across 2 domains — but does NOT collapse into a single "3-of-3 unified delivery domain" claim. See §17.6 hypothesis reframe + §19 T1 #17 rephrase per F3.

- **Content ↔ Memory learning-loop path has AUTO-CLOSE-LOOP ABSENT from PublishGate/panel path + PARTIAL PA-tool feedback bridge (Rigby SIGN Batch B F6 fold correction).** `core/services/publish_gate.py` grep for `AgentMemory|AgentPerformance` returns **0 hits**. Grep across `core/services/content_deliberation_runner.py` + `content_review_panel_v2.py` + `decision_enforcer_agent.py` for `AgentMemory.objects.create|AgentPerformance.objects.create` returns 0 hits. **No auto-close-loop from PublishGate scores → AgentMemory; no auto-close-loop from reviewer verdicts → AgentPerformance; no author-attribution auto-write.** **F6 fold pre-commit acknowledgment:** Rigby SIGN Batch B B1 caught an over-strong "OUTPUT-side WRITE absent" claim in Cat F draft. **PARTIAL output-side bridge DOES exist via PA-tool: `_record_content_feedback` at `core/services/td_handlers_content.py:184` writes `AgentMemory` entries of `memory_type='feedback'` at `:192/:205/:209` for PA-driven content approve/publish/complete/archive actions (8 call sites at :557, :592, :637, :1184, :1337, :1370, :1399, :1438).** This is PA-tool-driven feedback, NOT pipeline auto-close-loop. Cat A DOES read from DocumentEmbedding via ClaimsPackBuilder RAG (input-side memory consumption). **S1601 T5 R.CONTENT.LEARNING-LOOP-BRIDGE post-arc T-slot** flagged the auto-close-loop as intentional decoupling under Cat A boundary; Cat F CONFIRMS at HEAD + escalates: cross-arc Group 1300 Memory ADR needed to formalize contract (should PublishGate/panel output-side auto-write? should reviewer verdict + PublishGate score + author attribution feed AgentPerformance automatically? OR does the PA-tool-driven `_record_content_feedback` bridge cover the intent under a "manual close-loop" posture? Chris-gated). **D65-Memory-integration-posture evidence: current is PARTIAL at output (PA-tool feedback bridge covers manual close-loop; automatic pipeline close-loop from gate/reviewer/attribution ABSENT); INTEGRATION at input.**

- **Content ↔ Discord has 12 broadcast channel constants + PublishGate ZERO auto-broadcast.** `core/services/discord_notifications.py:36-47` defines 12 `CHANNEL_*` constants (11 unique Discord IDs; deliberate Session 460 reuse of `CHANNEL_MARKET_ALERTS` = `CHANNEL_OPPORTUNITIES` ID). **Grep `discord_notify|CHANNEL_` in `publish_gate.py` returns 0 hits at HEAD** — PublishGate makes NO Discord broadcasts. Content-adjacent Discord happens in `tasks_content.py` at :1757 (podcast import) + :1771 (podcast send) + :2898 (DiscordNotificationService import) + :3052 (embed import) + :3054 (embed send) — podcast + embed paths, not SelfBlog publish. S1604 §1.1 headline CONFIRMED at HEAD: **PublishGate does NOT auto-broadcast Discord; gate decisions are advisory only**. Discord is fire-and-forget at `discord_notifications.py:98-113` (no retry, no message-ID persistence, no `BroadcastLog` model — S1604 D65c-C3 evidence CONFIRMED at HEAD). **D65-Discord-integration-posture evidence: current is ISLAND with implicit manual broadcast (no gate-driven auto-fire); post-publish correction structurally impossible.**

- **Content ↔ Frontend has TWO approval UX surfaces + TWO API adapters + asymmetric force semantics + ZERO auth boundary. (F1 fold pre-commit: `newsletterApi` client-adapter DOES NOT EXIST at HEAD; §6.3 first draft claim corrected.)** `frontend/src/lib/api.ts` exposes `blogsApi.*` at :3921 + `deliverablesApi.*` at :4095 (grep across api.ts returns 2 Content-cross-boundary distinct API adapters at HEAD; `newsletterApi` grep returns 0 hits). Newsletter frontend surface is limited to public subscriber signup via `views_newsletter.py:19-77` (not a client-side newsletter adapter). `BlogViewerPage.tsx:381/:396` (force=false) + `ContentStudioTab.tsx:2200/:2215` (force=true) both hit `/api/v1/research/self-blog/*` endpoints at `views_research_demo.py:900` (approve) + `:942` (publish). S1605 T.15.E2 CRITICAL + T.15.E3 HIGH CONFIRMED at HEAD. **D65-Frontend-integration-posture evidence: current is INTEGRATED at API layer + ISLAND at auth-boundary layer (no shared decorator, no shared middleware, no shared audit event). Cat E §17.5 4-candidate framework applies verbatim; Candidate D excluded per S1605 F9.**

- **Content ↔ Employee OS is PARTIAL at HEAD via Rigby Documentation Manager overlap; ABSENT for dedicated Content publishing/management employee analog (Rigby SIGN Batch C F10 fold correction).** Grep `AIEmployee\(` in `core/employees/jobs.py` returns 4 employees at HEAD: `RIGBY` (:167), `PLATFORM_AUDITOR` (:388), `CHIEF_OF_STAFF` (:662), `BUG_TRIAGE_SPECIALIST` (:972). **`DOCUMENTATION_MANAGER` JobContract at `core/employees/jobs.py:187` is Rigby-owned (`employee_handle="rigby"` at :189; `manager="chris"` at :190) — this covers docs cascade + docs-corpus certification which is Content-adjacent operationally (touches Document + DocumentEmbedding models + docs RAG corpus).** **No dedicated "content_employee" or "content_manager" or "publisher" handle exists** for content publishing/management analog to D55 Revenue Employee + Income/Jobs Employee split. Parent §6.4 parked issue "Content Employee analog to Revenue Employee + Income/Jobs Employee (D55)" — Cat F CONFIRMS at HEAD: **PARTIAL — Employee OS exists for docs/content-adjacent ops via Rigby Documentation Manager; ABSENT for dedicated content publishing/management employee analog (D55-style)**; Cat F contributes evidence for xx99 §8 T3 slot (Chris-gated post-arc decision — whether the Content domain warrants a dedicated employee analog to the Revenue split, distinct from the docs-adjacent Documentation Manager already owned by Rigby). **D65-Employee-OS-integration-posture evidence: current is PARTIAL at governance-layer (Rigby Documentation Manager covers docs corpus but not content publishing/reviewer/broadcast authority); INTEGRATION posture requires new Content Employee + associated JobContract; ISLAND posture accepts current Rigby Documentation Manager overlap as sufficient scope for Content-adjacent authority (LOW discoverability, non-trivial capacity cost either direction).**

- **CROSS-ARC CORRECTION landed via S1605 F1 fold consumption at Cat F:** `auto_publish_approved_blogs` beat is RUNTIME-VERIFIED ABSENT (S1605 Batch A F1: 0 events 30d + 0 PeriodicTask rows from 92 total_enabled). Cat F consumes this correction verbatim: **5 doc claims of "daily 6 AM" in `docs/topics/celery-workers.md:163`, `docs/topics/content-pipeline.md:176/189`, `docs/narratives/CONTENT_PIPELINE.md:240`, S1604 §7.4 body, `SESSION_1033_VALUE_CHAIN_COMPLETION.md:86` are DRIFT-CONFIRMED-STALE.** Cat F flags these 5 doc PRs for post-arc docs-cleanup at S1699 §7 anchor-update recommendations. **S1604 D.14.C5 auto-publish audit-trail gap is MOOT because the beat never fires** — S1605 F1 fold established this; Cat F propagates.

### 1.2 Decisions this audit records (D65-analog four-axis posture-decision evidence plan handoff to xx99)

Per playbook §14.5 no-implementation rule + parent F11 boundary rule, Cat F **does not select** postures. Cat F produces xx99 posture-decision evidence plan for the four D65-analog axes (D65a Deliverable canonicalization + D65b PublishGate canonicalization + D65c Lifecycle-transition ownership + D65e Rigby PA-tool surface unification). The plan spans seven cross-domain surfaces per §20.6.

- **D65a Deliverable canonicalization evidence axis** — Cat D §1.1 headline records 3-category variant taxonomy (envelope→object integrated / standalone-by-design first-class / unfinished-orphan). Cat F EXTENDS with cross-domain lens: OutreachDraft + ClosePack (standalone Revenue-owned) + SportsBettingBrief + BlockchainAuditBrief (unfinished cross-arc-owned) + SelfBlog + PodcastEpisode (envelope→object Deliverable-integrated). Cross-domain integration posture selection at xx99 must resolve variant ownership per surface. §20.6 D65a evidence table.

- **D65b PublishGate canonicalization evidence axis** — Cat C §1.1 headline records SelfBlog-only publish-gate scope at HEAD + triple-gate composition contract MISSING + 4-candidate resolution framework at Cat C §17.4. Cat F EXTENDS with cross-domain lens: PublishGate does not currently gate Discord broadcast + does not currently gate Newsletter live-send (Newsletter dry_run parked) + does not currently gate Sports variant publish + does not currently gate Revenue OutreachDraft delivery. Cross-domain integration posture selection at xx99 must resolve gate-scope + gate-composition per surface. §20.6 D65b evidence table.

- **D65c Lifecycle-transition ownership evidence axis** — Cat C §1.1 headline records post-publish correction loops STRUCTURALLY ABSENT + force=true audit-trail absent + Discord broadcast audit-trail absent + Newsletter dry_run promotion path unknown. Cat F EXTENDS with cross-domain lens: Sports variants have zero lifecycle transitions post-write; Revenue OutreachDraft transitions live in Revenue domain (SENT/PENDING) but Content-side has no visibility; Memory learning-loop has no lifecycle-transition bridge; Employee OS lifecycle (JobContract → MissionRunner → OpsRun) has no Content integration. Cross-domain integration posture selection at xx99 must resolve lifecycle ownership per surface. §20.6 D65c evidence table.

- **D65e Rigby PA-tool surface unification evidence axis** — Cat E §1.1 headline records 4-tool split TACTICAL not STRUCTURAL + shared handler dispatch + xx99 anchor sentence LOCKED per S1605 F9 fold: *"Preserve the 4-tool interface, but centralize enforcement (auth/audit/scope/gates) so the split can't produce divergent behavior."* Cat F EXTENDS with cross-domain lens: enforcement centralization must span PA-tool + REST + Frontend (S1605 T.15.E2 CRITICAL + T.15.E3 HIGH); learning-loop bridge (S1601 T5 open) requires PA-tool surface for verdicts + mandate readback (S1602 §15.4 HIGH); Discord broadcast lacks PA-tool visibility (S1604 D65c-C3 evidence). Cross-domain integration posture selection at xx99 must resolve enforcement layer scope. §20.6 D65e evidence table.

- **Cross-arc handoff records (Cat F receives + emits):**
  - **RECEIVES from Cat A S1601**: SignalCluster READ-ONLY consumer contract; DocumentEmbedding RAG read; T1 R.CONTENT.RAG-SCOPE riskiest overall; T5 R.CONTENT.LEARNING-LOOP-BRIDGE open. Cat F consumes as Content↔Signal + Content↔Memory lens evidence.
  - **RECEIVES from Cat B S1602**: Cat B verdict + mandate ZERO PA-tool outbound; queue_agent_task landmine; v1 ContentReviewPanel PARTIALLY-ADOPTED-LIVE-SECONDARY. Cat F consumes as Content↔Employee-OS + Content↔Discord (broadcast contract) lens evidence.
  - **RECEIVES from Cat C S1604**: PublishGate SelfBlog-only; triple-gate composition contract MISSING (4-candidate framework §17.4); post-publish correction loops absent. Cat F consumes as Content↔Discord + Content↔Newsletter + Content↔Frontend + cross-boundary gate-scope lens evidence.
  - **RECEIVES from Cat D S1603**: 3-category variant taxonomy (F6 neutral fold); factory 5-gate + partial adoption; 2 legitimate Deliverable bypasses. Cat F consumes as Content↔Sports + Content↔Revenue variant lens evidence.
  - **RECEIVES from Cat E S1605**: 4-tool split + xx99 anchor sentence LOCKED (Candidate C = "centralize enforcement"); T.15.E2 CRITICAL REST auth-boundary; T.15.E4 auto_publish beat runtime-verified ABSENT (F1 fold correction to S1604 D.14.C5). Cat F consumes as Content↔Frontend + PA-tool cross-boundary lens evidence + auto_publish cross-arc correction propagation.
  - **RECEIVES from S1504 §14.3**: SportsBettingBrief WRITE-ONLY-FORGOTTEN CRITICAL. Cat F EMITS to xx99: consumer-or-remove decision owed at Group 1600 xx99 (cross-arc with Group 1500 T1.h).
  - **RECEIVES from S1504 §5.1**: SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS HIGH. Cat F consumes as Content↔Sports variant read-path lens evidence.
  - **RECEIVES from S1402 F.B1**: OutreachDraft delivery ZERO outbound F8-CRITICAL. Cat F CONFIRMS pattern class 3-of-3 at HEAD (OutreachDraft + Newsletter + BlockchainAuditBrief-analog).
  - **RECEIVES from S1403 F.C4**: ContentEngagement docstring drift HIGH CONFIRMED at HEAD. Cat F consumes as Content↔Memory learning-loop lens evidence.
  - **RECEIVES from S1502 §14.3**: SignalCluster.pattern_type consumer-side gap 6-arc COMPLETED. Cat F CONFIRMS Content is fifth consumer domain following Sports/Revenue/Memory/Employee-OS pattern.
  - **EMITS to xx99 S1699**: §20.6 posture-decision evidence plan (four-axis + seven-surface matrix); §19 T1/T2 cross-arc queue; §17 duplicate/overlapping systems consolidation.

### 1.3 Maturity verdict

**Cat F overall: MIXED per cross-domain surface.** Per parent F11 boundary rule, Cat F does not assign per-surface maturity beyond consuming sibling verdicts + adding cross-domain overlay. Consolidated per-surface maturity table:

| Surface | Current maturity | Verdict source |
|---------|-----------------|----------------|
| Content ↔ Signal Engine | WORKING (consumer-side stable; producer-side absent) | Cat A S1601 + §5 verified |
| Content ↔ Sports | PARTIAL (variants write-only-forgotten; hot-path-choke) | Cat D S1603 + S1504 verified |
| Content ↔ Revenue | EXPERIMENTAL (dry_run parked; ZERO outbound; pattern class 3-of-3) | Cat C S1604 + Cat D S1603 + S1402 F.B1 verified |
| Content ↔ Memory | PARTIAL (input-side READ integrated; output-side auto-close-loop ABSENT from PublishGate/panel; PARTIAL PA-tool bridge via `_record_content_feedback` per F6 fold) | Cat A S1601 + Cat B S1602 verified + Cat F F6 fold |
| Content ↔ Discord | PARTIAL (12 channels; ZERO gate-driven broadcast; no BroadcastLog; fire-and-forget) | Cat C S1604 verified |
| Content ↔ Frontend | PARTIAL (INTEGRATED at API + ISLAND at auth boundary; asymmetric force) | Cat E S1605 verified |
| Content ↔ Employee OS (governance layer) | PARTIAL (Rigby Documentation Manager JobContract covers docs-adjacent Content ops; dedicated Content publishing/management analog ABSENT; F10 fold) | Cat F §9.7 |

### 1.4 Cat F authority scope reminder (parent F11 boundary)

Cat F is the *"cross-domain integration lens + posture-decision evidence plan owed to xx99"* category per parent F11 Rigby fold. Cat F owns:

- Cross-domain integration surface catalog (seven-surface inventory).
- Sibling evidence consolidation across P1-P5 for cross-domain lens.
- Cross-arc handoff propagation (S1504 + S1502 + S1402 + S1403 evidence).
- xx99 §20.6 posture-decision evidence plan per D65a/D65b/D65c/D65e four-axis framing.
- §19 T1/T2 cross-arc queue consolidation (all sibling T-slots deduped + ranked).
- §17 duplicate/overlapping systems consolidation across siblings.
- **Cat F does NOT own**: any sibling-owned canonical decision (Cat A ClaimsPack mechanics; Cat B reviewer verdicts; Cat C gate semantics; Cat D object model; Cat E tool-surface implementation); posture selection at xx99 (Chris-gated ADR); any per-domain audit inside consumed domains (Signal, Sports, Revenue, Memory, Discord, Frontend, Employee OS are their own arcs).

### 1.5 Rigby cross-domain integration enforcement-authority contract (four-item mini-schema per surface upfront — D62 propagation)

Per parent D68 F8/F10 folds — this is the **sixth and LAST sibling** of Group 1600 to propagate the 4-item pre-brief mini-schema per surface upfront (after S1601 first + S1602 second + S1603 third + S1604 fourth + S1605 fifth). Each Cat F cross-domain surface gets a 4-item mini-brief at first mention.

**Seven canonical Cat F cross-domain surfaces (each with 4-item mini-schema):**

**1. Content ↔ Signal Engine surface** — READ-ONLY consumer at HEAD.
- **Purpose:** ClaimsPack assembly reads SignalCluster active clusters for speculative-claim extraction.
- **Direction:** Content READS from Signal Engine (ClaimsPackBuilder → SignalCluster.filter(status='active')); Content does NOT WRITE to Signal Engine.
- **Contract stability:** STABLE consumer-side (S1502 §14.3 6-arc completion); ABSENT producer-side.
- **Cat F evidence contribution:** D65-integration-posture for Signal is coherent with island posture (no cross-boundary write required for gate/pipeline function).

**2. Content ↔ Sports surface** — WRITE-ONLY-FORGOTTEN + HOT-PATH-CHOKE-BYPASS.
- **Purpose:** SportsBettingBrief + SportsContentContextBuilder produce sports-adjacent content briefs; BlockchainAuditBrief adjacent-pattern.
- **Direction:** Content WRITES SportsBettingBrief + BlockchainAuditBrief to persistence; NO downstream consumer at HEAD; Content READS from SportsContentContextBuilder for domain context.
- **Contract stability:** WRITE-ONLY-FORGOTTEN (Cat D confirmed 5-file footprint zero consumer at HEAD); HOT-PATH-CHOKE-BYPASS at read path (S1504 §5.1).
- **Cat F evidence contribution:** D65a variant taxonomy — Sports variants are unfinished/orphan bucket (Cat D §1.1 category 3); consumer-or-remove decision owed at xx99.

**3. Content ↔ Revenue surface** — ZERO outbound + docstring drift + Newsletter dry_run parked.
- **Purpose:** OutreachDraft (revenue outreach) + ClosePack (revenue conversion) + ContentEngagement (post-publish learning) + Newsletter (subscriber conversion).
- **Direction:** Content WRITES OutreachDraft + Newsletter Deliverable; NO outbound delivery infrastructure at HEAD (0 SendGrid/mailgun); Content EXPECTS ContentEngagement read from Discord/Newsletter/Frontend but bridge absent.
- **Contract stability:** EXPERIMENTAL (Newsletter dry_run >4mo parked); ZERO outbound (S1402 F.B1 F8-CRITICAL 3-of-3 pattern class confirmed).
- **Cat F evidence contribution:** D65c newsletter live-send + D65a OutreachDraft variant + D65-Revenue-integration-posture — decisions owed at xx99.

**4. Content ↔ Memory surface** — INPUT-side READ integrated + OUTPUT-side PARTIAL via PA-tool feedback bridge (F6 fold correction).
- **Purpose:** ClaimsPackBuilder reads DocumentEmbedding RAG for evidence (input side); PA-tool `_record_content_feedback` writes AgentMemory feedback entries on PA-driven content actions (output side); reviewer verdicts + PublishGate scores + author attribution auto-close-loop ABSENT from gate/panel path.
- **Direction:** Content READS DocumentEmbedding (input); Content WRITES AgentMemory via `_record_content_feedback` at `td_handlers_content.py:184` for PA-driven approve/publish/complete/archive (8 call sites); Content does NOT auto-write AgentMemory/AgentPerformance from PublishGate/reviewer/attribution path; ContentEngagement docstring claims write but no code path.
- **Contract stability:** INPUT-side STABLE (Cat A confirmed); OUTPUT-side PARTIAL (PA-tool feedback bridge for manual close-loop; automatic pipeline close-loop ABSENT per F6 fold).
- **Cat F evidence contribution:** D65-Memory-integration-posture — Chris-gated Group 1300 Memory ADR needed at xx99; posture selection resolves auto-vs-manual close-loop.

**5. Content ↔ Discord surface** — 12 channel constants + PublishGate ZERO auto-broadcast + fire-and-forget.
- **Purpose:** Discord broadcast rails for published content across 11 unique Discord IDs (12 constants with deliberate Session 460 reuse).
- **Direction:** Content WRITES via `discord_notify` at `tasks_content.py:1757+1771+3052+3054` (podcast + embed paths); PublishGate does NOT WRITE (0 hits in publish_gate.py); no BroadcastLog persistence; no message-ID retention.
- **Contract stability:** PARTIAL (broadcast works; no gate integration; no audit; no correction path); fire-and-forget at `discord_notifications.py:98-113`.
- **Cat F evidence contribution:** D65c broadcast audit-trail + D65-Discord-integration-posture — decisions owed at xx99.

**6. Content ↔ Frontend surface** — INTEGRATED at API + ISLAND at auth + asymmetric force semantics.
- **Purpose:** Two approval UX surfaces (BlogViewerPage + ContentStudioTab) hitting shared REST endpoints via three API adapters (blogsApi + deliverablesApi + newsletterApi).
- **Direction:** Frontend WRITES via `views_research_demo.py:900/:942` (approve/publish); Frontend READS via corresponding GET endpoints; ZERO backend role gate + ZERO frontend admin-only conditional render.
- **Contract stability:** INTEGRATED at API layer + ISLAND at auth-boundary layer; T.15.E2 CRITICAL + T.15.E3 HIGH per Cat E.
- **Cat F evidence contribution:** D65e enforcement-centralization scope must span PA-tool + REST + Frontend per Cat E §17.5 Candidate C.

**7. Content ↔ Employee OS surface (governance layer)** — PARTIAL at HEAD via Rigby Documentation Manager overlap; ABSENT for dedicated analog (F10 fold correction).
- **Purpose:** Docs cascade + docs corpus certification covered by Rigby Documentation Manager JobContract (Content-adjacent); no dedicated Content Employee analog to Revenue Employee (D55) at HEAD for content publishing/management authority.
- **Direction:** N/A — `DOCUMENTATION_MANAGER` JobContract at `core/employees/jobs.py:187-280` is Rigby-owned (`employee_handle="rigby"` at :189); no dedicated Content Employee handle exists; 4 employees at HEAD (RIGBY + PLATFORM_AUDITOR + CHIEF_OF_STAFF + BUG_TRIAGE_SPECIALIST); grep for content publisher/manager handles returns 0 hits.
- **Contract stability:** PARTIAL (governance overlap via Documentation Manager exists; dedicated Content analog ABSENT; D55 Revenue precedent exists).
- **Cat F evidence contribution:** D65-Employee-OS-integration-posture — Chris-gated Content Employee analog decision owed at xx99 §8 T3 (per F9 fold demotion from T1 #21).

**Three actors participate in Cat F cross-domain evidence consumption; only one is authoritative for posture selection.**

- **Cat F is EVIDENCE-CONSOLIDATION.** Cat F produces the seven-surface evidence catalog + §20.6 posture-decision evidence plan; Cat F does NOT select postures.
- **xx99 is CROSS-CHILD CONSOLIDATION.** xx99 consumes Cat F §20.6 evidence + resolves contradictions + writes Chris-gated posture-decision brief for D65a/D65b/D65c/D65e.
- **Chris ratifies POSTURE at post-arc ADR.** No posture is selected before Chris ratifies at ADR round post-xx99.

---

## 2. Domain Purpose

**Q1. What is Content Cat F's domain?**

Cat F is the cross-domain integration lens for Group 1600. It consolidates evidence across the seven cross-domain surfaces where Content touches other platform domains (Signal Engine, Sports, Revenue, Memory, Discord, Frontend, Employee OS) and produces the xx99 posture-decision evidence plan per D65a/D65b/D65c/D65e four-axis framing. Cat F is the LAST child audit under Group 1600; xx99 (S1699) consumes Cat F output as its primary evidence base for posture-decision consolidation.

**Q2. What are Cat F's authority boundaries?**

Cat F does NOT own any sibling-owned canonical decision. Cat F does NOT re-open earlier children (parent F11 boundary rule). Cat F does NOT select postures (playbook §14.5 no-implementation rule; parent §12.1 xx99-owns-selection). Cat F does NOT audit consumed cross-domain arcs (Signal / Sports / Revenue / Memory / Discord / Frontend / Employee OS have their own arcs). Cat F ONLY consolidates evidence from siblings + cross-arc handoffs + produces §20.6 posture-decision evidence plan.

---

## 3. Canonical Entry Points

Cat F's canonical entry points are the seven cross-domain integration surfaces, not code entry points (Cat F is evidence-consolidation, not runtime). Each surface's canonical code entry point is inherited from siblings.

| Surface | Canonical entry point (inherited from sibling) | Sibling audit |
|---------|-----------------------------------------------|---------------|
| Content ↔ Signal Engine | `core/services/claims_pack_builder.py:192` (`SignalCluster.objects.filter(status='active')`) | S1601 Cat A §3 |
| Content ↔ Sports | `core/tasks_content.py` SportsBettingBrief write path + `core/services/sports_content_context.py` read path | S1504 §5.1 + §14.3 + S1603 §4 |
| Content ↔ Revenue | `core/services/pa_tool_schemas.py` OutreachDraft schema + `core/tasks_content.py:4234-4413` newsletter beat + `core/models_engagement.py` ContentEngagement | S1402 F.B1 + S1604 §9.6 + S1403 F.C4 |
| Content ↔ Memory | `core/services/claims_pack_builder.py` DocumentEmbedding RAG read (input) + ABSENT output-side bridge | S1601 §9.3 + §14.4 (input) + S1601 T5 (output T-slot) |
| Content ↔ Discord | `core/services/discord_notifications.py:36-47` (12 channels) + `core/tasks_content.py:1757/1771/3052/3054` (broadcast callers) | S1604 §1.1 + §8.6 + §9.2 |
| Content ↔ Frontend | `frontend/src/pages/BlogViewerPage.tsx:396` + `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx:2215` → `core/views_research_demo.py:900/:942` | S1605 §1.1 + §6 + §16 |
| Content ↔ Employee OS (governance layer) | `core/employees/jobs.py:187-280` Rigby `DOCUMENTATION_MANAGER` JobContract (PARTIAL Content-adjacent); no dedicated Content publisher/manager handle (F10 fold) | Cat F §9.7 |

---

## 4. Major Models

Per parent F11 boundary rule, Cat F does not re-audit sibling-owned models. This section consolidates cross-domain FK graph across the seven surfaces.

### 4.1 Cross-domain FK graph (touch matrix)

| Model | Content-side FK direction | Consumer count at HEAD | Owner |
|-------|--------------------------|------------------------|-------|
| `SelfBlog` (`models_unified_system.py:20611`) | Deliverable → SelfBlog forward FK at `models_deliverables.py:192-199` (Session 862) | Full pipeline consumer; publish rails; frontend | Cat D + Cat C |
| `Deliverable` (base) (`models_deliverables.py:84`) | Forward FKs to SelfBlog + PodcastEpisode; zero reverse FKs from variants | 47+ files (Cat D §1) | Cat D |
| `PodcastEpisode` | Deliverable → PodcastEpisode forward FK at `:200-207` (Session 862) | Discord broadcast rails at `tasks_content.py:1757/1771` | Cat D + adjacent |
| `SportsBettingBrief` (`models_unified_system.py:18394`) | ISLAND (zero Deliverable FK; zero consumer) | 5-file footprint at HEAD; 0 services/views/agents consumer | Cat D §1 orphan bucket |
| `BlockchainAuditBrief` (`models_unified_system.py:18435`) | ISLAND (same pattern class as SportsBettingBrief) | 0 consumer at HEAD | Cat D §1 orphan bucket |
| `OutreachDraft` (`models_outreach.py`) | ISLAND (independent Revenue lifecycle) | 16 files at HEAD; PA-tool schema + beat exists; ZERO outbound delivery | Cat D §1 standalone bucket + Revenue-owned |
| `ClosePack` (`models_close_pack.py`) | ISLAND (independent Revenue lifecycle) | Revenue-owned; details in Group 1400 arc | Cat D §1 standalone bucket + Revenue-owned |
| `SignalCluster` (`models_signal_intelligence.py`) | Content READ-ONLY consumer (ClaimsPackBuilder :192) | 10 files write; Content does NOT write | Signal Engine domain |
| `DocumentEmbedding` (Memory domain) | Content READ-ONLY consumer (ClaimsPackBuilder RAG); UNK-1 workspace scope risk | Cat A §14.4 + §15.3 + S1601 T1 R.CONTENT.RAG-SCOPE #1 | Memory domain (S1300 arc) |
| `ContentEngagement` (`models_engagement.py`) | Docstring claims post-publish feedback loop; ZERO code path writes | S1403 F.C4 HIGH CONFIRMED at HEAD | Revenue-owned + Memory learning-loop cross-arc |
| `ToolCallRecord` (`models_tool_calls.py:19`) | PA-tool dispatch audit; captures PA-side; does NOT capture REST-side | S1605 §1.1 headline + §16 | Cat E |
| `DeliverableEvent` (`models_deliverables.py:561-614`) | Partial audit (set_status + detail + save write; update + create + append + delete do NOT) | S1605 T.15.E5 HIGH | Cat E |
| `PublishGateEvent` / `ForcedPublishEvent` / `AutoPublishEvent` / `BroadcastLog` / `RestPublishEvent` | ABSENT at HEAD (grep-verified 0 hits) | S1605 §1.1 headline verified 0 hits across all `*.py` | Cat E T1 + Cat C T2 |
| `AIEmployee` + `JobContract` (`core/employees/jobs.py`) | NO Content-owned employee at HEAD | 4 employees: RIGBY + PLATFORM_AUDITOR + CHIEF_OF_STAFF + BUG_TRIAGE_SPECIALIST | Employee OS domain |

### 4.2 Cross-domain FK insight

**Zero variant→Deliverable reverse FKs at HEAD** (Cat D §1 confirmed). This is the D65a structural fact: variants are islands. Cross-domain integration attempts (SportsBettingBrief, BlockchainAuditBrief, OutreachDraft, ClosePack) all landed as standalone models, not Deliverable-subkinds. Envelope→object integration only applies to two variants (SelfBlog + PodcastEpisode) via forward FK from Deliverable base.

---

## 5. Major Services

Per parent F11 boundary rule, Cat F does not re-audit sibling-owned services. This section consolidates cross-domain service surfaces + gap map.

### 5.1 Cross-domain service surface catalog

| Service | Content-side role | Cross-domain touch | Owner |
|---------|------------------|--------------------|-------|
| `ClaimsPackBuilder` (`claims_pack_builder.py:51`) | Assembles claims; READS SignalCluster + LegacySpiderData + DocumentEmbedding | Signal Engine (READ) + Memory (READ via RAG) | Cat A |
| `SportsContentContextBuilder` (`sports_content_context.py`) | Domain-content context for sports variant | Sports (READ path with hot-path-choke-bypass) | S1504 §5.1 |
| `DomainContentContextBuilder` (`domain_content_context.py`) | Adjacent domain-content context | Sports + others | Cat B v1 legacy path |
| `PublishGate` (`publish_gate.py:27`) | Advisory quality-scoring gate | Discord (ZERO auto-broadcast); Memory (ZERO learning bridge) | Cat C |
| `DiscordNotificationService` (`discord_notifications.py`) | Content broadcast rails; 12 channel constants | Discord + Podcast + Alerts | Cat C-adjacent (Cross-domain owned by Discord infra) |
| `NewsletterPublisher` + `NewsletterSources` (`newsletter_publisher.py`, `newsletter_sources.py`) | Newsletter content generation | Revenue (subscriber conversion); ZERO live-send | Cat C + Revenue-adjacent |
| `MissionRunner` (`core/employees/mission_runner.py`) | Employee OS orchestrator | ZERO Content Employee; Documentation Manager on RIGBY handle | Employee OS domain |
| `AutoSpawnerService` (`auto_spawner_service.py`) | Fallback log line "queue_agent_task not available" | Cross-boundary observability gap | Cat B §15.3 |

### 5.2 Missing services (Cat F cross-domain gap)

- **NO ContentBroadcastGateway service** — nothing centralizes PublishGate → Discord + Newsletter + Frontend + Podcast broadcast contract; each rail lives in its own module.
- **NO ContentLearningLoopBridge service** — nothing wires PublishGate scores + reviewer verdicts + author attribution → AgentMemory + AgentPerformance (S1601 T5 open).
- **NO ContentEmployee analog** — no `content_manager` or `publisher_employee` handle at `core/employees/jobs.py`; D55 Revenue precedent exists.
- **NO UnifiedContentAuthLayer** — no shared decorator/middleware/mixin between PA-tool dispatch + REST endpoints + Frontend approval UX; S1605 Cat E §17.5 Candidate C = "add shared auth+audit+scope layer" evidence axis for xx99.
- **NO ContentPublishEventStream service** — no unified event emission on any publish path; PublishGateEvent / ForcedPublishEvent / AutoPublishEvent / BroadcastLog / RestPublishEvent all absent at HEAD (S1605 verified).

---

## 6. Major APIs and Interfaces

Per parent F11 boundary rule, Cat F does not re-audit sibling-owned APIs. This section consolidates cross-domain API surfaces.

### 6.1 PA-tool layer cross-domain surfaces

- **Cat A**: `blog_tool.generate` → v2 pipeline (S1601 verified). No cross-domain exposure of reviewer verdicts or mandate (S1602 §15.4 HIGH — extends to Cat F Discord/Memory outbound gap).
- **Cat E 4 tools**: `content_tool` + `deliverable_tool` + `blog_tool` + `newsletter_tool` (S1605 §1.5). Cross-domain scope: `deliverable_tool` touches OutreachDraft/ClosePack/SportsBettingBrief/BlockchainAuditBrief base Deliverable only; `newsletter_tool` advertising vs live-send boundary violation.
- **Missing**: no PA-tool exposes reviewer verdicts + mandate for cross-domain readback (S1602 §15.4); no PA-tool exposes Discord broadcast state (S1604 D65c-C3); no PA-tool exposes ContentEngagement post-publish learning signal (S1403 F.C4).

### 6.2 REST layer cross-domain surfaces

- `views_research_demo.py:900` approve + `:942` publish — Frontend + auth-boundary asymmetry (Cat E T.15.E2 CRITICAL).
- `views_outreach.py` — Revenue OutreachDraft REST + no outbound delivery (S1402 F.B1).
- `views_newsletter.py` — Newsletter Subscriber signup + no live-send (Cat C S1604 T.15.C2 CRITICAL).
- Missing endpoints: no REST endpoint for reviewer verdicts + mandate; no REST endpoint for Discord broadcast log; no REST endpoint for ContentEngagement post-publish signal.

### 6.3 Frontend layer cross-domain surfaces

- `frontend/src/lib/api.ts` exposes `blogsApi.*` + `deliverablesApi.*` + `newsletterApi.*` (3 adapters on Cat F cross-boundary).
- `BlogViewerPage.tsx:381/:396` force=false + `ContentStudioTab.tsx:2200/:2215` force=true (Cat E asymmetric force).
- Missing: no frontend surface for reviewer verdicts + mandate; no frontend surface for Discord broadcast state; no frontend surface for Sports variant consumer; no frontend surface for OutreachDraft consumer.

### 6.4 Cross-layer contract asymmetries

Cat F consolidates per-surface asymmetries (verbatim from siblings):

| Asymmetry | Source | Cross-boundary consequence |
|-----------|--------|----------------------------|
| PA-tool auth vs REST endpoint zero-auth | S1605 §1.1 headline + T.15.E2 | Any authenticated session bypasses PA-tool auth via REST direct |
| Frontend force=true vs force=false hardcode | S1605 T.15.E3 | ContentStudioTab bypasses gate; BlogViewerPage does not |
| PublishGate advisory vs REST enforcement | S1604 §1.1 §1.5 | Gate can score; REST endpoint publishes even when gate says no (force=true) |
| Cat B reviewer verdict readback: REST-only, no PA-tool | S1602 §15.4 | Rigby cannot inspect verdicts via PA tool |
| Discord broadcast: fire-and-forget, no readback | S1604 §8.6 | Once broadcast, no retract, no message-ID log |
| Newsletter tool: 7 actions advertised, ZERO delivery | S1605 §1.1 headline T.15.E8 | Rigby-visible advertising boundary violation |

---

## 7. Runtime Flows

Per parent F11 boundary rule, Cat F does not re-audit sibling-owned runtime flows. This section catalogs the seven cross-domain integration flows at surface level.

### 7.1 Flow S — Content deliberation reads SignalCluster (Content ↔ Signal Engine)

- Trigger: `ContentDeliberationRunner.run_blog()` invokes `ClaimsPackBuilder.build_claims_pack()`.
- Read path: `_extract_signal_claims` at `claims_pack_builder.py:189` → `SignalCluster.objects.filter(status='active').order_by('-detected_at')[:50]` at `:192`.
- Write path: NONE from Content to Signal Engine at HEAD.
- Failure mode: silent empty list if no active clusters.
- Cross-arc: S1502 §14.3 6-arc consumer-side pattern COMPLETED (Content is fifth consumer).

### 7.2 Flow SP — Sports variant write-only-forgotten (Content ↔ Sports)

- Trigger: sports content generation flow writes SportsBettingBrief.
- Write path: `tasks_content.py` (sports briefs) + `models_unified_system.py:18394`.
- Read path: NONE at HEAD (5-file footprint grep-verified; 0 services/views/agents consumer).
- Failure mode: written but never consumed; no reader ever fires.
- Cross-arc: S1504 §14.3 CRITICAL + S1603 T.15.2 CRITICAL both CONFIRMED at HEAD.

### 7.3 Flow R — Revenue OutreachDraft zero-outbound (Content ↔ Revenue)

- Trigger: `generate-outreach-drafts-daily` beat at `core/celery.py`.
- Write path: OutreachDraft persisted; PA-tool schema exposes readback.
- Delivery: ABSENT (0 SendGrid/mailgun/postmark/SMTP hits on OutreachDraft path).
- Failure mode: draft persisted; never delivered.
- Cross-arc: S1402 F.B1 CONFIRMED + Cat D §1 standalone-by-design bucket + F8-CRITICAL pattern class 3-of-3.

### 7.4 Flow M — Content learning-loop bridge PARTIAL via PA-tool (Content ↔ Memory; F6 fold correction)

- Trigger: PA-tool content approve/publish/complete/archive actions invoke `_record_content_feedback` → AgentMemory write; PublishGate/reviewer/attribution auto-close-loop paths do NOT invoke memory writes.
- Read path: ClaimsPackBuilder reads DocumentEmbedding RAG (input side; S1601 §9.3 + §14.4 UNK-1 workspace scope risk).
- Write path (PA-tool bridge): `_record_content_feedback` at `td_handlers_content.py:184` writes `AgentMemory` (`memory_type='feedback'` at :192/:205/:209) with 8 call sites at :557/:592/:637/:1184/:1337/:1370/:1399/:1438; grep-verified F6 fold correction.
- Write path (auto-close-loop): NONE from PublishGate/reviewer/attribution to AgentMemory/AgentPerformance at HEAD (grep 0 hits in publish_gate.py + content_deliberation_runner.py + content_review_panel_v2.py + decision_enforcer_agent.py).
- Failure mode: PA-tool bridge covers manual close-loop only; automatic learning-loop from gate/panel path never closes.
- Cross-arc: S1601 T5 R.CONTENT.LEARNING-LOOP-BRIDGE post-arc T-slot; S1403 F.C4 ContentEngagement docstring drift extends; F6 fold correction added PARTIAL classification.

### 7.5 Flow D — Discord broadcast fire-and-forget (Content ↔ Discord)

- Trigger: `tasks_content.py:1757+1771` podcast + `:3052+3054` embed broadcast paths.
- Write path: `discord_notify.send_podcast()` + `discord_notify.send_embed()` via `discord_notifications.py:98-113` fire-and-forget with `requests.post` timeout=10.
- Retry / audit: NONE at HEAD (no BroadcastLog, no message-ID retention).
- Gate integration: PublishGate does NOT auto-broadcast (0 hits `discord_notify` in publish_gate.py).
- Failure mode: broadcast sent; no correction path; no retraction; no message-ID log.
- Cross-arc: S1604 §8.6 D65c-C3 broadcast audit-trail MISSING.

### 7.6 Flow F — Frontend approval UX (Content ↔ Frontend)

- Trigger: user clicks Publish button on BlogViewerPage OR ContentStudioTab.
- Frontend: BlogViewerPage.tsx:396 hardcodes `blogsApi.publish(id, false)`; ContentStudioTab.tsx:2215 hardcodes `blogsApi.publish(id, true)`.
- Backend: `views_research_demo.py:942` publish endpoint with `@require_http_methods(["POST"])` ONLY (no auth decorator; no role check).
- Gate check: `if not force and not blog.publish_ready` at `:966` — bypassed on force=true.
- Failure mode: any authenticated session can publish any blog.
- Cross-arc: S1605 T.15.E2 CRITICAL + T.15.E3 HIGH + Cat E anchor sentence LOCKED (Candidate C = centralize enforcement).

### 7.7 Flow E — Employee OS PARTIAL via Rigby Documentation Manager (Content ↔ Employee OS governance layer)

- Trigger: Documentation Manager beat cycle (docs cascade) fires as Rigby-owned mission; NO dedicated Content Employee mission exists.
- Employees at HEAD: RIGBY (:167) + PLATFORM_AUDITOR (:388) + CHIEF_OF_STAFF (:662) + BUG_TRIAGE_SPECIALIST (:972); NO content_manager or publisher_employee handle.
- Documentation Manager: Rigby-owned `DOCUMENTATION_MANAGER` JobContract at `core/employees/jobs.py:187-280` (employee_handle="rigby" at :189; manager="chris" at :190); materialized as `tasks_documentation_manager.py` beat + touches Content-adjacent docs corpus.
- Failure mode: PARTIAL — Content domain has governance overlap via Rigby Documentation Manager but no dedicated content publishing/management analog to Revenue Employee (D55) split; F10 fold correction from initial "ABSENT" verdict.
- Cross-arc: parent §6.4 parked issue confirmed as PARTIAL; Chris-gated post-arc T3 slot decision owed at xx99 §8 per F9 T1 demotion.

---

## 8. Data Ownership and Lifecycle

Per parent F11 boundary rule, Cat F does not re-audit sibling-owned data ownership. This section consolidates cross-domain ownership matrix.

### 8.1 Cross-domain ownership matrix

| Model / State | Content owns | External owns | Cross-boundary contract |
|---------------|--------------|---------------|--------------------------|
| `SelfBlog.*` | YES (Cat D + Cat C + Cat A) | N/A | Full Content authority |
| `Deliverable.*` (base) | YES (Cat D) | N/A | Full Content authority |
| `PodcastEpisode.*` | Shared (envelope→object via Deliverable FK) | N/A | Cat D §1 envelope→object bucket |
| `SportsBettingBrief.*` | Persistence only | Sports domain (Group 1500 T1.h) | Consumer-or-remove ADR owed |
| `BlockchainAuditBrief.*` | Persistence only | Blockchain domain (unaudited) | Owner reclaim OR archive ADR owed |
| `OutreachDraft.*` | Generation only | Revenue (Group 1400 R.B1) | Cross-arc delivery ADR owed |
| `ClosePack.*` | Generation only | Revenue domain | Full Revenue authority beyond generation |
| `SignalCluster.*` | Read consumer | Signal Engine domain | READ-only contract STABLE |
| `DocumentEmbedding.*` | Read consumer via RAG | Memory domain (Group 1300) | READ-only contract + workspace scope UNK-1 |
| `ContentEngagement.*` | Docstring claim | Revenue / Memory learning cross-arc | Bridge ABSENT (S1403 F.C4) |
| `ToolCallRecord.*` | PA-side write | Cross-boundary via PA dispatch | Captures PA-side only; NOT REST-side |
| `DeliverableEvent.*` | Partial write (set_status/detail/save; NOT update/create/append/delete) | Cat E-owned | S1605 T.15.E5 audit-invisible dual writer |
| `AgentMemory.*` / `AgentPerformance.*` | ZERO write from Content publish path | Memory domain | Bridge ABSENT (S1601 T5) |
| `AIEmployee` + `JobContract` (Content) | ABSENT at HEAD | Employee OS domain | Content Employee analog not materialized |

### 8.2 Lifecycle transition ownership across boundaries

| Transition | Content owns | External owns | Bridge status |
|------------|--------------|---------------|---------------|
| SelfBlog draft → approved → published | Cat C + Cat E | Frontend for user click | Enforcement asymmetric (S1605) |
| OutreachDraft draft → sent | Content generates | Revenue delivery domain | Delivery ABSENT (F8-CRITICAL) |
| Newsletter dry_run → live | Cat C dry_run parked | Cross-arc live-send domain TBD | Live-send infra ABSENT (T.15.C2 CRITICAL) |
| Discord broadcast fired → retract | Content fire-and-forget | Discord infra | Retract path ABSENT |
| Post-publish correction | ABSENT (Cat C §1) | N/A | Structural gap CRITICAL |
| Learning-loop close | ABSENT | Memory domain | Bridge ABSENT (S1601 T5) |
| Content Employee mission | ABSENT | Employee OS | Analog not materialized |

---

## 9. Integrations With Other Domains

**This is the Cat F headline section.** Cat F is the integration lens. Per playbook §11.2, §9 is where the seven-surface cross-domain evidence lives.

### 9.1 Content ↔ Signal Engine

**Direction:** READ-ONLY consumer at HEAD.

**Evidence at HEAD `c7a3c16e`:**
- `ClaimsPackBuilder._extract_signal_claims` at `core/services/claims_pack_builder.py:189-192` — reads `SignalCluster.objects.filter(status='active').order_by('-detected_at')[:50]`.
- Grep `SignalCluster.objects.create` in `core/services/` returns 10 files (signal_aggregation_service.py + curator + linker + fleet_signals + platform_inventory + curated_action_card_generator + signal_curator_service + initiative_signal_linker + system_state_aggregator + doc_claim_verification) — **NONE Content-domain**.
- Content is a fifth consumer following Sports/Revenue/Memory/Employee-OS pattern per S1502 §14.3 6-arc COMPLETED.

**Contract stability:** STABLE consumer-side; ABSENT producer-side.

**Cross-arc handoff:** S1502 §14.3 6-arc completion; S1601 §9.1 SignalCluster consumer contract confirmed.

**Cat F verdict:** No integration gap owed by Content. Signal Engine ↔ Content is coherent with island posture (Content READS; does not WRITE back — this is the correct pattern for a signal-consumer domain).

### 9.2 Content ↔ Sports

**Direction:** WRITE-ONLY-FORGOTTEN for SportsBettingBrief + BlockchainAuditBrief; READ path with HOT-PATH-CHOKE-BYPASS via SportsContentContextBuilder.

**Evidence at HEAD `c7a3c16e`:**
- `SportsBettingBrief` at `models_unified_system.py:18394` — 5-file footprint at HEAD (grep-verified: tasks.py + models/__init__.py + models_unified_system.py + tasks_content.py + migrations/0242).
- NO services/, NO views/, NO agents/ consumer at HEAD.
- `SportsContentContextBuilder` at `core/services/sports_content_context.py` + companion `domain_content_context.py` — S1504 §5.1 HOT-PATH-CHOKE-BYPASS HIGH; v1 ContentWriterAgent path can bypass builder.
- `BlockchainAuditBrief` at `models_unified_system.py:18435` — same pattern class as SportsBettingBrief (Cat D §1.1 category 3 unfinished/orphan).

**Contract stability:** WRITE-ONLY-FORGOTTEN at variant persistence; HOT-PATH-CHOKE-BYPASS at read path.

**Cross-arc handoff:** S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN CRITICAL; S1504 §5.1 SportsContentContextBuilder HOT-PATH-CHOKE HIGH; S1603 T.15.2 CRITICAL confirmed.

**Cat F verdict:** Integration gap. Consumer-or-remove ADR owed at xx99 for both Sports variants. Cat F contributes structural evidence (variants are islands per Cat D structural verdict); cross-arc coordination with Group 1500 T1.h.

### 9.3 Content ↔ Revenue

**Direction:** WRITE-side generation only; ZERO outbound delivery for OutreachDraft + Newsletter; ContentEngagement docstring drift.

**Evidence at HEAD `c7a3c16e`:**
- **OutreachDraft**: 16-file footprint at HEAD (celery.py + urls.py + tasks.py + pa_tool_schemas.py + td_handlers_ops.py + ops_autopilot/revenue.py + ops_autopilot/outreach_generation.py + ops_autopilot/intelligence.py + models_outreach.py + views_outreach.py + models_engagement.py + models_close_pack.py + migrations/0292 + tests/test_outreach_generation.py + tests/test_generate_outreach_drafts_daily.py + models/__init__.py). PA-tool schema exists; beat exists (`generate-outreach-drafts-daily`); **grep across all files for `sendgrid|mailgun|postmark|smtplib|SMTP|send_mail|EmailMessage` on OutreachDraft path returns 0 hits at HEAD**. S1402 F.B1 CONFIRMED.
- **Newsletter**: `_impl_generate_operator_edge_newsletter` at `tasks_content.py:4234-4413` + `newsletter_publisher.py` + `newsletter_sources.py` — same grep returns 0 hits; `dry_run=True` hardcoded at `celery.py:436` since S1222 P6 (>4mo). S1604 T.15.C2 CRITICAL + S1605 F8 CONFIRMED.
- **ContentEngagement**: `core/models_engagement.py` docstring claims post-publish feedback loop; grep `ContentEngagement.objects.create` on Discord/Newsletter/Frontend publish rails returns 0 hits (verified via 30-file scan: no code path writes ContentEngagement post-publish). S1403 F.C4 HIGH CONFIRMED at HEAD.
- **ClosePack**: Revenue-domain-owned; Content-side generation only per S1603 §4.

**Contract stability:** EXPERIMENTAL Revenue outbound; ZERO delivery infrastructure; pattern class 3-of-3.

**Cross-arc handoff:** S1402 F.B1 OutreachDraft ZERO outbound F8-CRITICAL; S1403 F.C4 ContentEngagement docstring drift HIGH CONFIRMED; S1604 T.15.C2 Newsletter live-send CRITICAL.

**Cat F verdict:** Integration gap 3-of-3 pattern class confirmed. Decisions owed at xx99:
- (a) Should OutreachDraft delivery live in Revenue-owned domain (S1402 R.B1) OR Content-owned Cat C-adjacent domain (S1604 T1 R.CONTENT.OUTREACHDRAFT-DELIVERY)?
- (b) Should Newsletter live-send live in Revenue/subscribers-owned domain OR Content-owned Cat C-adjacent domain?
- (c) Should ContentEngagement bridge be built cross-arc with Group 1300 Memory or built Content-adjacent as a post-publish event?
- (d) Should pattern class 3-of-3 collapse into a unified `OutboundDeliveryDomain` service (S1604 T1 R.CONTENT.NEWSLETTER-LIVE-SEND-PATH + F14 strengthening)?

### 9.4 Content ↔ Memory

**Direction:** INPUT-side READ integrated (RAG); OUTPUT-side PARTIAL via PA-tool feedback bridge; auto-close-loop from gate/panel path ABSENT (F6 fold correction).

**Evidence at HEAD `c7a3c16e`:**
- **Input side**: `ClaimsPackBuilder` reads DocumentEmbedding via RAG (S1601 §9.3 + §14.4 UNK-1 workspace scope risk = T1 R.CONTENT.RAG-SCOPE riskiest overall).
- **Output side**: Grep `AgentMemory|AgentPerformance` in `core/services/publish_gate.py` returns 0 hits. Grep `AgentMemory.objects.create|AgentPerformance.objects.create` in `content_deliberation_runner.py + content_review_panel_v2.py + decision_enforcer_agent.py` returns 0 hits. **No PublishGate score → AgentMemory bridge; no reviewer verdict → AgentPerformance bridge; no author-attribution learning bridge at HEAD.**
- ContentEngagement bridge ABSENT (S1403 F.C4 HIGH CONFIRMED).

**Contract stability:** INPUT STABLE; OUTPUT ABSENT.

**Cross-arc handoff:** S1601 T1 R.CONTENT.RAG-SCOPE (input side, riskiest overall) + T5 R.CONTENT.LEARNING-LOOP-BRIDGE (output side, T-slot open); S1403 F.C4 ContentEngagement drift extends.

**Cat F verdict:** Integration gap on OUTPUT side. Decisions owed at xx99:
- (a) Should PublishGate scores feed AgentMemory + AgentPerformance? If yes, direct write OR event-stream OR async signal?
- (b) Should reviewer verdicts + mandate feed the learning loop?
- (c) Should author attribution close the loop for content-specific agents?
- (d) Cross-arc Group 1300 Memory ADR owed to formalize contract.

### 9.5 Content ↔ Discord

**Direction:** WRITE via `discord_notify` in tasks_content.py + PublishGate ZERO auto-broadcast.

**Evidence at HEAD `c7a3c16e`:**
- 12 `CHANNEL_*` constants at `discord_notifications.py:36-47` (11 unique Discord IDs; deliberate Session 460 reuse of `CHANNEL_MARKET_ALERTS` = `CHANNEL_OPPORTUNITIES` ID).
- Content-adjacent `discord_notify` calls in `tasks_content.py`: `:1757` (podcast import) + `:1771` (podcast send) + `:2898` (DiscordNotificationService import) + `:3052` (embed import) + `:3054` (embed send).
- `publish_gate.py`: **0 hits** for `discord_notify|CHANNEL_` (grep-verified).
- `discord_notifications.py:98-113`: fire-and-forget `requests.post` with timeout=10; catches `Timeout` at `:107` and `RequestException` at `:110`; no retry, no message-ID persistence, no `BroadcastLog` model.

**Contract stability:** PARTIAL (broadcast works; no gate integration; no audit; no correction path).

**Cross-arc handoff:** S1604 §1.1 headline "PublishGate itself never calls discord_notify" CONFIRMED at HEAD; S1604 D65c-C3 broadcast audit-trail MISSING.

**Cat F verdict:** Integration gap on broadcast contract. Decisions owed at xx99:
- (a) Should PublishGate PUBLISH decision auto-fire Discord broadcast? If yes, per-channel policy?
- (b) Should `BroadcastLog` model land + retain message-ID for retract capability?
- (c) Should post-publish correction include Discord `edit_message` OR `delete_message` on the retained message-ID?

### 9.6 Content ↔ Frontend

**Direction:** WRITE via approval UX + REST endpoints; INTEGRATED at API + ISLAND at auth-boundary.

**Evidence at HEAD `c7a3c16e`:**
- 2 Content-cross-boundary API adapters in `frontend/src/lib/api.ts`: `blogsApi.*` at :3921 + `deliverablesApi.*` at :4095. **`newsletterApi` DOES NOT EXIST at HEAD** (grep-verified 0 hits per F1 fold; Cat F draft claim of 3 adapters was WRONG). Newsletter frontend surface is limited to public subscriber signup at `views_newsletter.py:19-77` (server-rendered form; no client adapter).
- 2 approval UX surfaces: `BlogViewerPage.tsx:381/:396` (force=false) + `ContentStudioTab.tsx:2200/:2215` (force=true).
- Both hit `views_research_demo.py:900` approve + `:942` publish with **ZERO `@login_required|@permission_required|@user_passes_test`** decorators + ZERO in-body role check (grep-verified S1605 §20.3).
- `views_research_demo.py:966` gates on `if not force and not blog.publish_ready` — bypassed on force=true.
- ContentStudioTab canPublish inconsistent: `draft` OR `approved` at `:2238` vs BlogViewerPage `approved`-only at `:394` (S1605 T.15.E9 HIGH per F10 fold).

**Contract stability:** INTEGRATED at API layer + ISLAND at auth-boundary + asymmetric force + inconsistent canPublish.

**Cross-arc handoff:** S1605 T.15.E2 CRITICAL + T.15.E3 HIGH + T.15.E9 HIGH; Cat E anchor sentence LOCKED per F9 fold.

**Cat F verdict:** Integration gap on auth-boundary. Decisions owed at xx99:
- (a) Where is the role gate for approve/publish (frontend? middleware? in-body decorator?)?
- (b) Is force=true admin-only, and if yes how enforced?
- (c) Should ContentStudioTab hardcode force=true at all or expose a toggle?
- (d) canPublish unification across BlogViewerPage + ContentStudioTab.
- Cat E anchor sentence Candidate C = centralize enforcement across PA-tool + REST + Frontend applies verbatim.

### 9.7 Content ↔ Employee OS

**Direction:** ABSENT at HEAD (no Content Employee).

**Evidence at HEAD `c7a3c16e`:**
- Grep `AIEmployee\(` in `core/employees/jobs.py` returns **4 employees at HEAD**: `RIGBY` (:167), `PLATFORM_AUDITOR` (:388), `CHIEF_OF_STAFF` (:662), `BUG_TRIAGE_SPECIALIST` (:972).
- **NO Content Employee handle** (grep `content_employee|content_manager|publisher|content_owner` in `jobs.py` returns 0 hits).
- Documentation Manager is Rigby-owned (RIGBY has documentation manager job contract; materialized as `tasks_documentation_manager.py` beat).
- D55 Revenue Employee + Income/Jobs Employee JobContract split precedent exists (S1499 D55).
- Parent §6.4 parked issue "Content Employee analog to Revenue Employee + Income/Jobs Employee (D55)" — Cat F CONFIRMS at HEAD: no analog materialized.

**Contract stability:** ABSENT.

**Cross-arc handoff:** parent §6.4; S1499 D55 (ii); CLAUDE.md 3-vs-4 employees narrative drift documented in doctor warnings (inventory says 4; CLAUDE.md narrative says 3 — Bug Triage Specialist added S1266 not yet reflected in narrative — separate cleanup).

**Cat F verdict:** ABSENT posture. Decisions owed at xx99 (Chris-gated post-arc T3/T4):
- (a) Does Content warrant a dedicated Employee analog to Revenue split?
- (b) If yes, what's the JobContract shape (single Content Employee with multiple jobs? Or split Content Publisher + Content Editor per D55 precedent)?
- (c) If no, is Rigby's Documentation Manager sufficient scope for Content-adjacent authority?

---

## 10. Event Flows

### 10.1 Existing event writers (Cat F cross-boundary)

- `ToolCallRecord` at `core/models_tool_calls.py:19` — PA-tool dispatch audit; CAPTURES PA-side; does NOT capture REST-side (Cat E).
- `DeliverableEvent` at `core/models_deliverables.py:561-614` — partial write (set_status/detail/save); does NOT capture update/create/append/delete (Cat E T.15.E5 audit-invisible dual writer HIGH per F6 fold).

### 10.2 Missing event writers (Cat F cross-boundary consolidation)

**Grep across `*.py` for these event models returns 0 hits at HEAD (verified S1605 §20.3):**

- `ForcedPublishEvent` — MISSING (Cat E T1 R.CONTENT.FORCE-BYPASS-AUTH-BOUNDARY consumer; S1604 T2 R.CONTENT.FORCE-PUBLISH-AUDIT-TRAIL consumer).
- `AutoPublishEvent` — MISSING (S1604 T2 R.CONTENT.AUTO-PUBLISH-BEAT-AUDIT-TRAIL owed; MOOT at HEAD because beat runtime-verified ABSENT per S1605 F1 fold).
- `PublishGateEvent` — MISSING (S1604 T2 R.CONTENT.PUBLISHGATE-EVENT-TELEMETRY owed).
- `PublishEvent` / `RestPublishEvent` — MISSING (Cat E T2 R.CONTENT.REST-PUBLISH-AUDIT-TRAIL owed).
- `AuditEvent` / `AdminActionLog` — MISSING.
- `BroadcastLog` / `ContentBroadcastEvent` — MISSING (Cat C S1604 §8.6 D65c-C3 owed).
- `ContentLearningLoopEvent` / bridge to `AgentMemory|AgentPerformance` — MISSING (S1601 T5 R.CONTENT.LEARNING-LOOP-BRIDGE owed).

**Cat F consolidated verdict:** cross-domain event surface is UNIFIED-ABSENT. All 8 event models above must land as a coherent unified telemetry layer, not per-surface piecemeal, to close S1605 §17.5 Candidate C "centralize enforcement" LOCKED xx99 anchor sentence.

---

## 11. Existing Documentation

### 11.1 Cross-domain topic docs consulted

- `docs/topics/content-pipeline.md` — Session 1147 last-reviewed 2026-05-25; drift-labeled "pattern still valid; specific numbers may drift." Cross-arc CORRECTION owed for `auto_publish "daily 6 AM"` claim at `:176/:189` (S1605 F1 fold).
- `docs/topics/celery-workers.md:163` — cross-arc CORRECTION owed for same claim.
- `docs/topics/personal-assistant.md` — Cat E-adjacent (S1605 §11.1).
- `docs/topics/spider-network.md` — Signal Engine adjacent.
- `docs/topics/agent-system.md` — Memory learning-loop adjacent.
- `docs/topics/body-systems.md` — Employee OS orchestration-adjacent (BRAIN/HEART).
- `docs/topics/employee-os.md` — Employee OS canonical; confirms Documentation Manager on RIGBY handle; 4 employees at HEAD (drift with CLAUDE.md narrative 3).
- `docs/topics/frontend.md` — Frontend surface adjacent.
- `docs/topics/infrastructure.md` — Discord broadcast-adjacent (Railway).

### 11.2 Cross-domain handoffs consulted (siblings + cross-arc)

- **Siblings (Group 1600):** S1600 parent scoping; S1601 Cat A; S1602 Cat B; S1603 Cat D; S1604 Cat C; S1605 Cat E.
- **Cross-arc (Group 1500):** S1502 SignalCluster consumer 6-arc; S1504 SportsBettingBrief + SportsContentContextBuilder; S1599 xx99 §5 posture-decision evidence plan exemplar (Cat F §20.6 F2 fold rubric adoption source).
- **Cross-arc (Group 1400):** S1402 OutreachDraft F.B1 F8-CRITICAL; S1403 ContentEngagement F.C4 HIGH; S1499 D55 Revenue + Income/Jobs Employee JobContract split precedent.
- **Cross-arc (Group 1300):** learning-loop bridge scope (S1601 T5 open).

### 11.3 Cross-domain memory rules (Cat F-load-bearing)

- `feedback_docs_cascade_at_every_close.md` — 4-step + `build_docs_provenance` cascade owed post-merge (per S1606 close plan).
- `feedback_docs_pipeline_4_step_cascade.md` — full pipeline discipline.
- `feedback_no_parallel_research_arcs.md` — Cat F is sequential per playbook §14 lens-child pattern.
- `feedback_verify_before_deleting_dead_code.md` — Cat F did not delete anything (research-only per playbook §14.5).
- `feedback_rigby_sign_worker_instability_recovery.md` — Rigby SIGN owed with batched 3-4 findings per prompt for D48 15th arm.

### 11.4 Prior audits touching Cat F cross-domain scope

- S1502 §14.3 SignalCluster consumer 6-arc COMPLETED (Content is fifth consumer per Cat F §9.1).
- S1504 §5.1 SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS HIGH.
- S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN CRITICAL.
- S1402 F.B1 OutreachDraft ZERO outbound F8-CRITICAL.
- S1403 F.C4 ContentEngagement docstring drift HIGH.
- S1274 §5 duplicate/overlapping systems baseline (for Cat F §17 consolidation).
- S1599 xx99 §5 posture-decision evidence plan (F2 fold rubric source for §20.6).

### 11.5 Documentation gaps (Cat F T2)

- **NO `docs/topics/cross-domain-integration.md`** — Cat F evidence would land as canonical cross-domain lens topic; T2 R.CONTENT.CROSS-DOMAIN-TOPIC-DOC owed.
- **NO `docs/narratives/CONTENT_CROSS_DOMAIN.md`** — cross-arc narrative absent.
- **CLAUDE.md 3-vs-4 employees narrative drift** — inherited from S1499; still unresolved.

---

## 12. Research Coverage

Cat F is evidence-consolidation lens; §12 records sibling coverage inheritance + Cat F original contribution.

**Sibling coverage inherited:**
- Cat A S1601: Content ↔ Signal + Content ↔ Memory (input) fully audited.
- Cat B S1602: Content ↔ Employee-OS + Discord (verdict outbound) partially audited via Cat B §15.4 outbound-gap.
- Cat C S1604: Content ↔ Discord + Newsletter + Frontend (publish rails) fully audited.
- Cat D S1603: Content variant ownership across Sports + Revenue fully audited.
- Cat E S1605: Content ↔ Frontend + PA-tool cross-boundary auth fully audited.

**Cat F original contribution:**
- Content ↔ Employee OS §9.7 (new).
- Cross-domain event writer consolidation §10 (aggregated from siblings).
- §20.6 posture-decision evidence plan per D65a/D65b/D65c/D65e four-axis framing (new).
- §17 duplicate/overlapping systems cross-arc consolidation.
- §19 T1/T2 cross-arc queue dedup + ranking.

**Coverage classification:** CANONICAL for cross-domain lens; INHERITED for per-domain audit depth (Cat F does not re-open siblings per parent F11).

---

## 13. Architecture Maturity

Consolidated per-surface maturity from §1.3 table; evidence citations added.

| Surface | Maturity | Evidence source | Change since S1274 baseline |
|---------|----------|------------------|------------------------------|
| Content ↔ Signal Engine | WORKING | Cat A S1601 §5 + Cat F §9.1 grep verified | Newly integrated at S1502 6-arc COMPLETED |
| Content ↔ Sports | PARTIAL | S1504 §14.3 CRITICAL + S1603 §4 + Cat F §9.2 | Persistent write-only-forgotten pattern; not degraded |
| Content ↔ Revenue | EXPERIMENTAL | S1402 F.B1 + S1604 T.15.C2 + Cat F §9.3 | Pattern class 3-of-3 confirmed at HEAD |
| Content ↔ Memory (input) | STABLE | Cat A S1601 §9.3 | RAG stable; workspace-scope UNK-1 riskiest overall |
| Content ↔ Memory (output) | PARTIAL | S1601 T5 + Cat F §9.4 + F6 fold | Auto-close-loop from gate/panel ABSENT; PARTIAL PA-tool bridge via `_record_content_feedback` at `td_handlers_content.py:184` for PA-driven approve/publish/complete/archive (8 call sites) |
| Content ↔ Discord | PARTIAL | Cat C S1604 §8.6 + Cat F §9.5 | fire-and-forget; no gate integration |
| Content ↔ Frontend | PARTIAL | Cat E S1605 T.15.E2/E3/E9 + Cat F §9.6 | INTEGRATED at API + ISLAND at auth |
| Content ↔ Employee OS (governance layer) | PARTIAL | Cat F §9.7 (new; F10 fold PARTIAL not ABSENT) | Rigby Documentation Manager overlap present; dedicated D55-style Content analog not materialized |

---

## 14. Known Drift

Cross-domain drift consolidated across siblings + Cat F original.

| ID | Drift | Source | Severity | Owner |
|----|-------|--------|----------|-------|
| D.14.F1 | `auto_publish_approved_blogs` "daily 6 AM" claim in 5 docs vs runtime-verified ABSENT. **Runtime verification performed in S1605 (Batch A F1 fold via ops_tool.celery_task_history 30d = 0 events + scheduled_tasks_tool = 0 tasks); Cat F only propagates correction per parent F11 consolidation-lens boundary rule and does NOT re-verify the runtime probe** (Rigby SIGN Batch B F8 fold acknowledgment). 5 doc paths owed re-scoped verification at xx99 §7 anchor-updates. | S1605 F1 fold; Cat F consumes | HIGH | 5 doc PRs owed at xx99 §7 |
| D.14.F2 | ContentEngagement docstring claims post-publish loop; code path ABSENT | S1403 F.C4 CONFIRMED at HEAD | HIGH | Group 1300 Memory ADR |
| D.14.F3 | CLAUDE.md narrative says 3 employees; runtime has 4 (Bug Triage Specialist added S1266) | Inherited from S1499 doctor warning | LOW | Docs cleanup post-xx99 |
| D.14.F4 | `docs/topics/content-pipeline.md:74` FactCheckReviewer named as class; runtime is module-level function `run_reviews` | S1602 §14 | LOW | S1602 xx99 §7 |
| D.14.F5 | Newsletter beat `dry_run=True` since S1222 P6 >4mo elapsed vs "operational newsletter" narrative | Cat C S1604 D.14.C2 | HIGH | xx99 §5 D65c-C1 |
| D.14.F6 | `docs/patents/DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md:140` "creates `queue_agent_task.delay()`" vs runtime queue_agent_task ABSENT | S1602 §15.3 | HIGH | Patent doc + code ADR |
| D.14.F7 | Cross-arc S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN documented but persistence path continues at HEAD | Cross-arc | CRITICAL | xx99 §5 D65a Sports variant |

---

## 15. Known Technical Debt

Cross-domain technical debt consolidated across siblings + Cat F original.

| ID | Debt | Severity | Cross-domain scope | Source |
|----|------|----------|--------------------|--------|
| T.15.F1 | UnifiedContentAuthLayer ABSENT — no shared decorator/middleware between PA-tool + REST + Frontend | HIGH | Content ↔ Frontend + PA-tool boundary | S1605 §17.5 Candidate C anchor |
| T.15.F2 | ContentPublishEventStream ABSENT — 8 missing event models (§10.2) | HIGH | Content ↔ Discord + Frontend + REST | Cat F §10 consolidation |
| T.15.F3 | ContentLearningLoopBridge ABSENT — PublishGate scores + verdicts + attribution → AgentMemory/AgentPerformance | HIGH | Content ↔ Memory (output) | S1601 T5 + S1403 F.C4 |
| T.15.F4 | ContentBroadcastGateway ABSENT — no centralized broadcast contract; PublishGate does NOT auto-fire Discord | HIGH | Content ↔ Discord | Cat C S1604 §8.6 |
| T.15.F5 | Content Employee ABSENT — no publisher/content_manager handle in `core/employees/jobs.py` | MEDIUM | Content ↔ Employee OS | Cat F §9.7 new |
| T.15.F6 | **DEBT CONDITION (per Rigby SIGN Batch B F7 fold split):** outbound delivery/consumption rails MISSING for key content outputs — Newsletter dry_run indefinitely parked + OutreachDraft ZERO outbound + Sports orphan variants ZERO consumer. **Proposed unification into "unified outbound-delivery domain" is a candidate T1 solution NOT a §15 debt condition** — moved to §19 T1 #17 per F7 fold. | CRITICAL | Content ↔ Revenue + Sports | S1402 F.B1 + S1604 T.15.C2 + Cat F §9.3 consolidation |
| T.15.F7 | Sports variant consumer-or-remove ADR OWED — SportsBettingBrief + BlockchainAuditBrief both unfinished/orphan | CRITICAL | Content ↔ Sports | S1504 §14.3 + Cat D §1 + Cat F §9.2 |
| T.15.F8 | Cross-domain RAG workspace scope UNK-1 riskiest overall | CRITICAL | Content ↔ Memory (input) | S1601 T1 R.CONTENT.RAG-SCOPE |
| T.15.F9 | `queue_agent_task` MISSING from `core/tasks.py` (patent operational claim invalidated) | HIGH | Content ↔ Employee OS + Signal Engine | S1602 §15.3 |
| T.15.F10 | Post-publish correction loops STRUCTURALLY ABSENT — no retract/errata/edit_message/unpublish across ALL surfaces | CRITICAL | Content ↔ Discord + Frontend + Revenue + Memory | Cat C S1604 §16.1 |

---

## 16. Boundary Violations

Cross-domain boundary violations consolidated across siblings + Cat F original.

### 16.1 Cross-arc SportsBettingBrief write-only-forgotten crosses Cat D + Sports boundaries (T.15.F7)

Sports domain WROTE model + Content-side persistence continues at HEAD; consumer never landed. Cat D confirmed islands; Cat F confirms zero consumer at HEAD. Sports domain owns the read-path decision (Group 1500 T1.h); Content owns the persistence + factory-adoption decision (Cat D T2). Cross-boundary ADR ownership overlap.

### 16.2 Cross-arc OutreachDraft ZERO outbound crosses Cat D + Revenue + Cat C boundaries (T.15.F6)

OutreachDraft persistence at Content-adjacent generation; Revenue delivery domain owns outbound; Cat C Newsletter pattern-analog. Cross-boundary ADR ownership overlap 3-way (Content generation + Revenue delivery + Cat C rail policy).

### 16.3 Cross-arc Newsletter dry_run parked crosses Cat C + Revenue + Employee-OS boundaries (T.15.F6)

Newsletter Deliverable saved by task; PublishGate never touches (Cat C §1.1); no live-send infra; dry_run parked. Delivery domain ownership unresolved. Cross-boundary 3-way ADR.

### 16.4 Cross-arc ContentEngagement docstring drift crosses Cat A + Revenue + Memory boundaries (D.14.F2)

Docstring claims post-publish feedback loop; code path ABSENT; extends S1403 F.C4. Content-side write-path missing; Memory-side read-path unbuilt; Revenue-side conversion signal absent. Cross-boundary 3-way ADR.

### 16.5 Cross-arc PublishGate advisory vs REST enforcement asymmetry (S1604 §1.5)

Three actors participate in publish-eligibility decision; only REST endpoint is authoritative (Cat C §1.5). Cross-boundary bounces via Cat E `force=true` bypass (S1605 T.15.E3). Fix scope crosses PA-tool + REST + Frontend + PublishGate (Cat C + Cat E + Frontend + optional Discord broadcast auto-fire).

### 16.6 Cross-arc PA-tool auth vs REST endpoint zero-auth asymmetry (S1605 T.15.E2 CRITICAL)

Dispatcher-side gate via `AssistantProfile.get_allowed_tools()`; REST-side ZERO decorator + ZERO in-body role check. Cross-boundary auth-enforcement asymmetry. Fix scope requires UnifiedContentAuthLayer (T.15.F1).

### 16.7 Cross-arc Content ↔ Memory learning-loop OUTPUT ABSENT (T.15.F3)

Content READS DocumentEmbedding (input side); NEVER WRITES AgentMemory/AgentPerformance (output side). Bridge crosses Cat A generation + Cat B verdicts + Cat C gate scores + Memory learning domain. Fix scope requires cross-arc Group 1300 Memory ADR.

---

## 17. Duplicate or Overlapping Systems

Cross-domain duplicate/overlapping systems consolidated across siblings + Cat F original.

### 17.1 Three parallel publish-eligibility gate systems (Cat D §17.4 T.15.6 + Cat C §17.4)

- `deliverable_factory.py:358-411` 5-gate creation-time check (media_stub / smoke_pattern / min_length / template_leak / no_relevance).
- `publish_gate.py:44-49` 4-threshold post-deliberation check (QUALITY / NOVELTY / STRUCTURE / MYTHOLOGY).
- `SelfBlog.quality_score` / `SelfBlog.novelty_score` / `SelfBlog.structure_score` schema fields.

Cross-domain scope: Cat D + Cat C + Cat E surfaces all consume. Cat C §17.4 records 4-candidate resolution framework for xx99 D65b B4 consumption.

### 17.2 Three parallel publish-rail dispatch surfaces (Cat C §9)

- Frontend approve/publish endpoints (Cat E T.15.E2/E3 asymmetric).
- Discord broadcast service (Cat C §8.6 fire-and-forget).
- Newsletter beat dry_run parked (Cat C T.15.C2 CRITICAL).

Cross-domain scope: Cat C + Cat E + Frontend + Discord + Newsletter/Revenue. Cat F emits: unified `ContentBroadcastGateway` T2 recommendation (T.15.F4).

### 17.3 Two parallel content-authoring pipelines (Cat B S1602 §1)

- v2 canonical (`content_review_panel_v2.py` + `ContentDeliberationRunner`).
- v1 legacy (`content_review_panel.py` + `ContentWriterAgent._maybe_run_review()` at `content_writer_agent.py:1376-1377` with `ENABLE_CONTENT_REVIEW=True` guard).

Classification: PARTIALLY-ADOPTED-LIVE-SECONDARY. Cross-domain scope: Cat A + Cat B. xx99 §5 D65-analog evidence.

### 17.4 Two parallel content-approval frontend UX surfaces (Cat E §17.2 T.15.E9)

- BlogViewerPage.tsx (force=false; approved-only canPublish).
- ContentStudioTab.tsx (force=true; draft OR approved canPublish).

Cross-domain scope: Cat E + Frontend. Fix scope: canPublish unification (Cat E T2 R.CONTENT.CANPUBLISH-UNIFICATION); role gate landing (T.15.F1 UnifiedContentAuthLayer).

### 17.5 Two parallel status-transition writers on Deliverable (Cat E §17.4 T.15.E5)

- `set_status` action writes DeliverableEvent.
- `update` action writes directly via `save(update_fields=['status'])` at `td_handlers_agents.py:2216-2221` — NO DeliverableEvent.

Cross-domain scope: Cat D + Cat E. Cat E T2 R.CONTENT.DELIVERABLE-UPDATE-AUDIT.

### 17.6 Cross-arc consolidation: Cat E §17.5 4-candidate framework for D65e-E1 anchor sentence LOCKED

Per S1605 F9 fold — xx99 anchor sentence LOCKED: *"Preserve the 4-tool interface, but centralize enforcement (auth/audit/scope/gates) so the split can't produce divergent behavior."* **Cat F HYPOTHESIS + EXTENSION SCOPE (per Rigby SIGN Batch A F5 fold — reframed from architectural commitment to Cat F hypothesis):** the Cat E Candidate C enforcement-unification mechanism *may generalize* to Cat F cross-domain surfaces beyond PA-tool + REST + Frontend (which are the Cat E-scoped LOCKED surfaces). Candidate C's cross-domain extension IS A HYPOTHESIS TO BE TESTED — NOT a Cat F architectural commitment. §20.6 defines the evidence required before xx99 treats it as cross-domain enforcement.

**Cat F hypothesis (Candidate C cross-domain extension):** enforcement-unification (auth + audit + scope + gates) could span additional Content surfaces including Discord broadcast rails + Newsletter live-send infrastructure + Memory learning-loop write-side bridge + Sports variant consumer paths.

**Scope boundaries (what Candidate C cross-domain extension does NOT cover yet):**
- Employee OS enforcement (Content Employee analog is separate posture per §9.7 + T1 #21).
- Signal Engine integration (Content is READ-only consumer per §9.1; enforcement lives on Signal-emit side, not Content-consume side).
- Revenue delivery domain ownership (ADR overlap per §16.2 3-way — enforcement layer applies IF delivery lands Content-adjacent; NOT if delivery lives strictly Revenue-owned).
- ClaimsPack + deliberation mechanics (Cat A-owned; enforcement layer wraps output side, not deliberation internals).

**Selection contract:** Candidate C's cross-domain extension is selected ONLY if PASS across required surfaces per §20.6.4 D65e evidence axis PASS/PARTIAL/FAIL scoring. Cat E anchor sentence LOCKED remains authoritative for Cat E-scoped surfaces (PA-tool + REST + Frontend); Cat F cross-domain extension is Chris-gated at xx99 ADR round.

---

## 18. Ownership Gaps

Cross-domain ownership gaps consolidated across siblings + Cat F original.

| Component | Current Owner | Should Be | Gap | Debt ID |
|-----------|--------------|-----------|-----|---------|
| UnifiedContentAuthLayer | UNOWNED | Cat E + Frontend + Auth domain | HIGH | T.15.F1 |
| ContentPublishEventStream | UNOWNED | Cat C + Cat E + Discord infra | HIGH | T.15.F2 |
| ContentLearningLoopBridge | UNOWNED | Cat A + Cat B + Memory domain (Group 1300) | HIGH | T.15.F3 |
| ContentBroadcastGateway | UNOWNED | Cat C + Discord infra | HIGH | T.15.F4 |
| Content Employee analog | UNOWNED | Employee OS domain | MEDIUM | T.15.F5 |
| Unified OutboundDelivery domain (pattern class 3-of-3) | UNOWNED | Cross-arc Content + Revenue + Sports | CRITICAL | T.15.F6 |
| Sports variant consumer OR remove | UNOWNED | Cross-arc Group 1500 T1.h + Content Cat D | CRITICAL | T.15.F7 |
| Cross-domain RAG workspace scope | UNOWNED | Cat A + Memory domain | CRITICAL | T.15.F8 |
| Post-publish correction (retract/edit/errata) | UNOWNED | Cat C + Discord + Frontend + Newsletter | CRITICAL | T.15.F10 |
| Documentation coverage of cross-domain lens | UNOWNED | Cat F topic doc T2 | MEDIUM | Cat F §11.5 |

---

## 19. Recommended Future Research

Q28. Ranked by architectural uncertainty × risk × unblocked flows. Cat F consolidates + dedupes + adds cross-domain T1/T2 items.

### 19.1 T1 — CRITICAL / HIGH — post-arc ADRs owed to xx99

Cat F T1 ranking consolidates all sibling T1s (deduped) + adds cross-domain T1s.

| Rank | T-slot | Cat F role | Rationale | Precedent |
|------|--------|------------|-----------|-----------|
| **#1** | R.CONTENT.RAG-SCOPE | consumer | S1601 F4 riskiest overall Group 1600 finding; workspace/cross-tenant exposure | S1601 T1 #1 |
| **#2** | R.CONTENT.CITATION-INTEGRITY | consumer | S1601 UNK-2 CONFIRMED HIGH end-to-end LLM-prompt-only | S1601 + S1602 T1 |
| **#3** | R.CONTENT.CAT-B-TRUNCATION | consumer | Silent 8000-char reviewer draft truncation | S1602 T1 |
| **#4** | R.CONTENT.CAT-B-SPAWN-TASKS | consumer | queue_agent_task MISSING + patent claim invalidated | S1602 T1 |
| **#5** | R.CONTENT.CAT-B-OUTBOUND | consumer | Cat B verdicts ZERO PA-tool + Discord + notification | S1602 T1 |
| **#6** | R.CONTENT.VARIANT-CATEGORIZATION-CLARIFICATION | consumer | Cat D 3-category taxonomy Chris-gated | S1603 T1 F12 |
| **#7** | R.CONTENT.CANONICAL-CREATION-CONTRACT | consumer | Factory + shadow paths reconciliation | S1603 T1 F13 |
| **#8** | R.CONTENT.TRIPLE-GATE-COMPOSITION-CONTRACT | consumer | 4-candidate framework at Cat C §17.4 | S1603 F11 + Cat C T1 |
| **#9** | R.CONTENT.PUBLISHGATE-SCOPE-CANONICALIZATION | consumer | SelfBlog-only vs extend to variants | Cat C T1 NEW |
| **#10** | R.CONTENT.POST-PUBLISH-CORRECTION-LOOPS | consumer | Cat C CRITICAL structural gap | Cat C T1 NEW |
| **#11** | R.CONTENT.NEWSLETTER-LIVE-SEND-PATH | consumer | Cat C CRITICAL + pattern class 3-of-3 | Cat C T1 NEW |
| **#12** | R.CONTENT.OUTREACHDRAFT-DELIVERY | consumer | Cross-arc S1402 F.B1 F14-upgrade | S1603 F14 + Cat C T1 |
| **#13** | R.CONTENT.RIGBY-TOOL-SURFACE-UNIFICATION | consumer | Cat E D65e-E1 posture; Candidate C LOCKED anchor | Cat E T1 NEW |
| **#14** | R.CONTENT.FORCE-BYPASS-AUTH-BOUNDARY | consumer | Cat E T.15.E2 CRITICAL + T.15.E3 HIGH | Cat E T1 NEW |
| **#15** | R.CONTENT.AUTO-PUBLISH-BEAT-SCHEDULE | consumer | Cat E runtime-verified ABSENT; MOOT vs S1604 D.14.C5 | Cat E T1 NEW + S1605 F1 |
| **#16** | R.CONTENT.DELIVERABLE-WORKSPACE-SILENT-DEGRADE | consumer | Cat E T.15.E1 HIGH | Cat E T1 NEW |
| **#17** | **R.CONTENT.OUTBOUND-DELIVERY-CONSUMPTION-RAILS-GAP** *(F9 fold rephrase from R.CONTENT.UNIFIED-OUTBOUND-DELIVERY-DOMAIN)* | **Cat F ORIGIN NEW** | Cross-arc gap: Newsletter dry_run + OutreachDraft ZERO outbound + Sports orphan variants ZERO consumer. "Unified outbound-delivery domain" is ONE candidate solution (among cross-arc ownership variations); xx99 §5 evidence plan resolves. | Cat F §9.3 §15.F6 |
| **#18** | **R.CONTENT.UNIFIED-CONTENT-AUTH-LAYER** | **Cat F ORIGIN NEW** | Cat E anchor sentence LOCKED Candidate C extended across surfaces (PA-tool + REST + Frontend + Discord + learning-loop) as Cat F HYPOTHESIS per F5 fold; §20.6.4 evidence gate before adoption | Cat F §15.F1 + Cat E §17.5 F9 + F5 fold |
| **#19** | **R.CONTENT.UNIFIED-EVENT-STREAM** | **Cat F ORIGIN NEW** | 8 missing event models must land as coherent layer, not per-surface piecemeal | Cat F §10 §15.F2 |
| **#20** | **R.CONTENT.LEARNING-LOOP-BRIDGE** | **Cat F PROMOTES from S1601 T5** | Cross-arc Group 1300 Memory ADR needed to formalize contract; ContentEngagement docstring drift extends; PARTIAL PA-tool bridge exists per F6 fold — decision resolves gate-vs-manual-close-loop posture | S1601 T5 + S1403 F.C4 + Cat F §9.4 + F6 fold |
| **#21** | **R.CONTENT.CROSS-DOMAIN-EMPLOYEE-ANALOG** *(F9 fold DEMOTED to T3 — severity mismatch with §15 T.15.F5 MEDIUM; Content Employee analog is NOT a hard dependency for CRITICAL T1s #1-#20)* | **Cat F ORIGIN NEW → T3** | D55 Revenue + Income/Jobs split precedent; Rigby Documentation Manager PARTIAL overlap per F10 fold; Chris-gated Content Employee analog materialization decision at xx99 §8 T3 slot | parent §6.4 + Cat F §9.7 + F9 fold |
| **#22** | **R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E** *(F9 fold rename from R.CONTENT.POSTURE)* | **Cat F ORIGIN NEW (ADR bundle wrapper)** | xx99 ADR packaging requirement: four-axis D65a/D65b/D65c/D65e posture selection consumes xx99 §5 verbatim; Chris-gated ADR round. NOT a "research item" — an ADR-packaging obligation for xx99. | Cat F §20.6 + F9 fold |

### 19.2 T2 — post-arc follow-on

Cat F T2 dedupes sibling T2s + adds cross-domain T2s.

- **T2 R.CONTENT.CROSS-DOMAIN-TOPIC-DOC** (Cat F ORIGIN NEW) — write `docs/topics/cross-domain-integration.md` covering seven-surface lens; consumes Cat F §9 verbatim; closes §11.5.
- **T2 R.CONTENT.CROSS-DOMAIN-NARRATIVE** (Cat F ORIGIN NEW) — write `docs/narratives/CONTENT_CROSS_DOMAIN.md`; consumes Cat F §9 + §17.
- **T2 R.CONTENT.CROSS-ARC-CORRECTION-BATCH** — 5 doc PRs owed to remove `auto_publish "daily 6 AM"` claim from `docs/topics/celery-workers.md:163`, `docs/topics/content-pipeline.md:176/189`, `docs/narratives/CONTENT_PIPELINE.md:240`, S1604 §7.4 body, `SESSION_1033_VALUE_CHAIN_COMPLETION.md:86`. Consumes S1605 F1 fold correction.
- **T2 R.CONTENT.FORCE-PUBLISH-AUDIT-TRAIL** — inherited Cat C T2 + Cat E T2 endorsement.
- **T2 R.CONTENT.REST-PUBLISH-AUDIT-TRAIL** — inherited Cat E T2.
- **T2 R.CONTENT.DELIVERABLE-UPDATE-AUDIT** — inherited Cat E T2.
- **T2 R.CONTENT.CONFIRM-PUBLISH-DIALOG** — inherited Cat E T2.
- **T2 R.CONTENT.CANPUBLISH-UNIFICATION** — inherited Cat E T2.
- **T2 R.CONTENT.APPEND-LARGE-PAYLOAD-VERIFY** — inherited Cat E T2.
- **T2 R.CONTENT.NEWSLETTER-SCHEMA-DESCRIPTION-TIGHTEN** — inherited Cat E T2.
- **T2 R.CONTENT.PUBLISHGATE-CALIBRATION-INVESTIGATION** — inherited Cat C T2.
- **T2 R.CONTENT.MYTHOLOGY-SCORE-PERSISTENCE** — inherited Cat C T2.
- **T2 R.CONTENT.PUBLISHGATE-EVENT-TELEMETRY** — inherited Cat C T2.
- **T2 R.CONTENT.APPLY-PUBLISH-GATE-BEAT** — inherited Cat C T2.
- **T2 R.CONTENT.AUTO-PUBLISH-BEAT-AUDIT-TRAIL** — inherited Cat C T2 (**MOOT per S1605 F1 fold** — beat runtime-verified ABSENT; retirement of this T-slot recommended at xx99).
- **T2 R.CONTENT.CHECK-ENVELOPE-DEAD-CODE** — inherited Cat C T2.
- **T2 R.CONTENT.STATS-SNAPSHOT-DELIBERATION-CANONICALIZATION** — inherited Cat C T2.
- **T2 R.CONTENT.PUBLISHGATE-UNIT-TESTS** — inherited Cat C T2.
- **T2 R.CONTENT.EXHAUSTIVE-PUBLISH-MUTATIONS-SWEEP** — inherited Cat C T2.
- **T2 R.CONTENT.CENTRAL-FACTORY-BYPASS-MIGRATION** — inherited Cat D T2.
- **T2 R.CONTENT.SPORTSBETTINGBRIEF-DISPOSITION** — inherited Cat D T2 cross-arc.
- **T2 R.CONTENT.BLOCKCHAINAUDITBRIEF-DISPOSITION** — inherited Cat D T2.
- **T2 R.CONTENT.DELIVERABLE-STATUS-COMPLETED-DRIFT** — inherited Cat D T2.
- **T2 R.CONTENT.CAT-B-HARDCODED-CRITIQUE** — inherited Cat B T2.
- **T2 R.CONTENT.CAT-B-REWRITE-CONVERGENCE** — inherited Cat B T2.
- **T2 R.CONTENT.CAT-B-VERDICT-PERSISTENCE** — inherited Cat B T2.
- **T2 R.CONTENT.CAT-B-SESSION-RETENTION** — inherited Cat B T2.

### 19.3 T3 — LOW — post-arc

Deferred: R.CONTENT.PUBLISH-RAIL-TOPIC-DOC + R.CONTENT.NEWSLETTER-ISSUE-MODEL + R.CONTENT.PUBLISHGATE-THRESHOLD-OVERRIDE + R.CONTENT.DATABASE-MODEL-REFERENCE-REFRESH + R.CONTENT.DISCORD-CHANNEL-CONSTANT-REVIEW (inherited Cat C T3) + R.CONTENT.CAT-B-DOCSTRING + R.CONTENT.CAT-B-EXCEPTION-CLASSIFICATION (inherited Cat B T3).

### 19.4 T4 — deferred cross-arc

- **T4 R.CONTENT.PUBLISHGATE-VARIANT-EXTENSION** — if D65a integration posture at xx99.
- **T4 R.CONTENT.CONTENT-ENGAGEMENT-LEARNING-LOOP-BRIDGE** — cross-arc Group 1300 Memory + Group 1700 Observability.
- **T4 R.CONTENT.SPORTSBETTINGBRIEF-CONSUMER-OR-REMOVE-RAIL** — cross-arc Group 1500 T1.h.
- **T4 R.CONTENT.BLOCKCHAINAUDITBRIEF-CONSUMER-OR-REMOVE-RAIL** — same pattern.
- **T4 R.CONTENT.CROSS-BOUNDARY-QUEUE-AGENT-TASK-LANDMINE** — S1602 §15.3.

### 19.5 Cross-arc handoffs owed to Group 1600 xx99 (S1699)

- **From Group 1400:** OutreachDraft delivery ADR (S1402 F.B1) + ContentEngagement bridge ADR (S1403 F.C4).
- **From Group 1500:** SportsBettingBrief consumer-or-remove ADR (S1504 §14.3 T1.h) + SportsContentContextBuilder hot-path resolution (S1504 §5.1).
- **From Group 1300 (owed cross-arc):** learning-loop bridge scope ADR.
- **From S1502 §14.3:** SignalCluster consumer 6-arc completion (Content is 5th consumer; contract stable).
- **To xx99 §7 anchor-updates:** `docs/topics/content-pipeline.md` refresh; `docs/PLATFORM_INVENTORY.md` per-cat coverage in Services table; `docs/patents/DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md:140` reconciliation.

---

## 20. Appendix

### 20.1 Files inspected

- `docs/research/domains/content/1600_content_domain_scoping.md` (parent §3 F scope + §5 D66 P6 slot + §8 D63-D68 + F11 boundary rule)
- `docs/research/domains/content/1601-1605_content_*.md` (5 sibling audits fully consumed)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 template + §11.3 §10 meta-methodology + §14 evidence rules + §14.5 no-implementation rule + §15 Rigby SIGN policy)
- `docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md` (§14.3 6-arc COMPLETED)
- `docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md` (§14.3 CRITICAL + §5.1 HIGH)
- `docs/research/domains/sports/1599_sports_canonical_summary.md` (xx99 §5 F2 fold rubric exemplar)
- `docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md` (F.B1 F8-CRITICAL)
- `docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md` (F.C4 HIGH)
- `docs/research/domains/revenue/1499_revenue_canonical_summary.md` (D55 Employee split precedent)
- `docs/topics/content-pipeline.md`, `docs/topics/celery-workers.md`, `docs/topics/personal-assistant.md`, `docs/topics/employee-os.md`
- `docs/narratives/CONTENT_PIPELINE.md`
- `docs/PLATFORM_INVENTORY.md` (autoblock: 4 employees; 92 enabled PeriodicTasks; 113 PA tool schemas + 156 handlers; 585 models)
- `docs/PLATFORM_WHAT_IT_IS.md` (narrative anchor)
- Code touchpoints grep-verified at HEAD `c7a3c16e`:
  - `core/services/claims_pack_builder.py:189-192` (SignalCluster consumer)
  - `core/services/publish_gate.py` (0 hits for `discord_notify|AgentMemory|AgentPerformance|CHANNEL_`)
  - `core/services/discord_notifications.py:36-47` (12 channel constants)
  - `core/tasks_content.py:1757/1771/2898/3052/3054` (discord_notify calls)
  - `core/employees/jobs.py:167/388/662/972` (4 AIEmployees)
  - `core/services/sports_content_context.py` + `core/services/domain_content_context.py`
  - Cross-file grep: `SportsBettingBrief` (5 files) + `OutreachDraft` (16 files) + `ContentEngagement` (27 files including docs)

### 20.2 Docs inspected

Same as §20.1 doc list.

### 20.3 Grep patterns used (parent-Claude verifier-loop on Cat F cross-domain binary claims)

- `SignalCluster.objects.create` in `core/services/` — 10 files; ZERO Content-domain files ✓
- `SignalCluster` in `core/services/claims_pack_builder.py` — 8 hits at :4/:9/:52/:75/:79/:189/:190/:192 ✓ (READ-only consumer confirmed)
- `SportsBettingBrief` in `core/` — 5 files: tasks.py + models/__init__.py + models_unified_system.py + tasks_content.py + migrations/0242 ✓ (5-file WRITE-ONLY-FORGOTTEN footprint confirmed)
- `OutreachDraft` in `core/` — 16 files ✓ (PA-tool schema + beat exists; ZERO outbound infrastructure confirmed)
- `ContentEngagement` in repo — 27 files (mostly docs); ZERO code-side `ContentEngagement.objects.create` on publish rails confirmed ✓
- `AIEmployee\(` in `core/employees/jobs.py` — 4 hits at :167/:388/:662/:972; ZERO Content Employee ✓
- `discord_notify|CHANNEL_` in `core/services/publish_gate.py` — 0 hits ✓ (PublishGate ZERO auto-broadcast)
- `AgentMemory|AgentPerformance` in `core/services/publish_gate.py` — 0 hits ✓ (learning-loop OUTPUT ABSENT)
- `discord_notify` in `core/tasks_content.py` — 5 hits at :1757/:1771/:2898/:3052/:3054 (podcast + embed paths, not SelfBlog publish) ✓
- `CHANNEL_[A-Z_]+ =` in `core/services/discord_notifications.py` — 12 constants at :36-47 ✓ (S1604 §8.6 12-channels CONFIRMED)
- `blogsApi\.|deliverablesApi\.|newsletterApi\.` in `frontend/src/lib/api.ts` — 2 hits (blogsApi at :3921 + deliverablesApi at :4095); `newsletterApi` 0 hits ✓ (F1 fold: initial Cat F "3 adapters" claim CORRECTED to 2 pre-Rigby-SIGN)
- `SportsContentContextBuilder|sports_content_context` — 20 files; grep confirms 2 code files exist ✓ (S1504 §5.1 hot-path infrastructure at HEAD)
- Class check for `ForcedPublishEvent|AutoPublishEvent|PublishGateEvent|PublishEvent|AuditEvent|BroadcastLog|RestPublishEvent|ContentLearningLoopEvent` — 0 hits across `*.py` (inherited S1605 §20.3 verification) ✓
- `auto_publish_approved_blogs` in `core/celery.py` — 0 hits ✓ (S1605 F1 fold verified beat runtime-ABSENT)

### 20.3a First-class anchor (S1604 F10 propagation continued)

**Cat F anchor (post-Rigby-SIGN F1-F10 folds landed pre-commit):** *"Content integrates with the platform via SEVEN cross-domain surfaces (6 runtime + 1 governance layer per F2 fold). Cat F evidence maturity: Content ↔ Signal Engine (WORKING consumer, coherent island); Content ↔ Sports (PARTIAL: write-only-forgotten + hot-path-choke); Content ↔ Revenue (EXPERIMENTAL: pattern class 2-of-2 ZERO outbound per F3 rebucketing); Content ↔ Memory (input STABLE + output PARTIAL via PA-tool `_record_content_feedback` bridge per F6 fold); Content ↔ Discord (PARTIAL: fire-and-forget, no gate integration); Content ↔ Frontend (INTEGRATED API + ISLAND auth); Content ↔ Employee OS (PARTIAL via Rigby Documentation Manager overlap per F10 fold; dedicated D55-style analog ABSENT). xx99 posture selection resolves the four D65-analog axes across these surfaces via §20.6 evidence plan."*

### 20.4 Cross-arc handoffs

**Received by Cat F S1606 (this audit):**
- Cat A S1601: SignalCluster READ-only consumer contract; DocumentEmbedding RAG; T1 RAG-SCOPE riskiest; T5 LEARNING-LOOP-BRIDGE open.
- Cat B S1602: ZERO PA-tool outbound; queue_agent_task landmine; v1 PARTIALLY-ADOPTED-LIVE-SECONDARY.
- Cat C S1604: PublishGate SelfBlog-only; triple-gate composition missing; correction loops absent.
- Cat D S1603: 3-category variant taxonomy; factory partial adoption; 2 legitimate bypasses.
- Cat E S1605: 4-tool split TACTICAL; xx99 anchor LOCKED Candidate C; T.15.E2 CRITICAL; T.15.E4 auto_publish ABSENT + F1 fold correction to S1604 D.14.C5.
- S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN CRITICAL.
- S1504 §5.1 SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS HIGH.
- S1402 F.B1 OutreachDraft ZERO outbound F8-CRITICAL.
- S1403 F.C4 ContentEngagement docstring drift HIGH.
- S1502 §14.3 SignalCluster consumer 6-arc COMPLETED (Content is 5th consumer).
- S1499 D55 Revenue Employee + Income/Jobs Employee JobContract split precedent.

**Emitted by Cat F S1606 (this audit) to xx99 S1699:**
- §20.6 posture-decision evidence plan per D65a/D65b/D65c/D65e four-axis framing (LOAD-BEARING).
- §19 T1/T2 cross-arc queue consolidation (22 T1 items ranked + 26 T2 items + 5 T3 + 5 T4).
- §17 duplicate/overlapping systems consolidation (6 items).
- §14 Known Drift matrix (7 items).
- §15 Known Technical Debt matrix (10 items — 4 CRITICAL + 6 HIGH).
- §16 Boundary Violations (7 items).
- §18 Ownership Gaps (10 items).
- Cross-arc CORRECTION owed for `auto_publish "daily 6 AM"` claim propagation to 5 docs (S1605 F1 fold continues).

### 20.5 Rigby SIGN fold notes

**SIGN Cycle 1 — 2026-07-02** on fresh isolation pin `pa-8cfafefb67864f83` (Rigby-side `session_tool.create_fresh`; retired at S1606 close via `session_tool.retire` per `feedback_session_tool_retire_works.md`). 3-batch SIGN pattern per memory rule `feedback_rigby_sign_worker_instability_recovery.md` — Batch A (4 headline pressure-tests A1-A4) + Batch B (3 mid-tier B1-B3) + Batch C (2 remaining C1-C2 + final consolidated verdict C3). Rigby confidence: **Batch A 0.78 HIGH; Batch B 0.70 MED-HIGH; Batch C 0.83 HIGH; Final consolidated 0.82 HIGH.**

**SIGN outcome:** **SIGN-with-edits at High confidence overall (0.82)** → **F1-F10 folds landed pre-commit at S1606 close**. Cat F ready for xx99 §5 consumption post-folds.

**Riskiest finding across A/B/C batches** (Rigby final consolidated): Batch B B1 §9.4 "output-side WRITE absent" over-strong claim missed the `_record_content_feedback` PA-tool AgentMemory bridge at `td_handlers_content.py:184` (F6 fold). Close second: Batch A A2 pattern class 3-of-3 rebucketing — BlockchainAuditBrief mis-placed at Content ↔ Revenue instead of Sports (F3 fold).

**Most important future research** (Rigby final consolidated):
1. xx99 §5 D65e-E1 posture selection with Cat F §17.6 hypothesis + scope-boundary contract properly consumed.
2. Cross-arc Group 1300 Memory ADR to formalize learning-loop bridge contract (auto-close-loop vs PA-tool manual-close-loop posture).
3. Sports variant consumer-or-remove disposition — cross-arc Group 1500 T1.h + Cat F §9.2 evidence.
4. Chris-gated Content Employee analog decision — T3 slot per F9 fold demotion (severity mismatch resolved).

**F1-F10 folds landed pre-commit:**

- **F1 — §1.1 §6.3 §20.3 `newsletterApi` claim CORRECTED (Cat F self-caught via targeted grep pre-Rigby-SIGN Batch A completion).** Cat F draft claimed "3 API adapters (blogsApi + deliverablesApi + newsletterApi)"; grep-verified `newsletterApi` returns 0 hits in `frontend/src/lib/api.ts`; only `blogsApi` at :3921 + `deliverablesApi` at :4095 exist as Content-cross-boundary adapters. Newsletter frontend surface limited to public subscriber signup at `views_newsletter.py:19-77`. Landed in §1.1 headline + §6.3 + §20.3.

- **F2 — §1.1 seven-surface framing clarification (Batch A A1).** Added definitional clarification: "surface" spans BOTH runtime data-flow integrations (6 surfaces) AND platform governance/ownership interfaces (Employee OS as governance-layer surface). Employee OS explicitly labeled "(governance layer)" in §1.1 bullet 7 + §1.3 maturity table + §3 canonical entry points. Observability/audit treated as cross-cutting within each surface, NOT as separate 8th surface. Landed in §1.1.

- **F3 — §1.1 pattern class 3-of-3 rebucketing (Batch A A2).** Cat F draft claimed "pattern class 3-of-3 (OutreachDraft + Newsletter + BlockchainAuditBrief-analog) all lack outbound delivery at Content ↔ Revenue surface." Rigby SIGN A2 caught internal inconsistency — BlockchainAuditBrief is a Sports-domain orphan variant (Cat D §1 category 3 alongside SportsBettingBrief), NOT Revenue-adjacent. **Corrected framing:** at Content ↔ Revenue surface the pattern is **2-of-2 (OutreachDraft + Newsletter)** — both content-generation-only with ZERO outbound. BlockchainAuditBrief pattern-class stays at Content ↔ Sports surface as orphan variant. Broader cross-arc "content output lacks outbound rail/consumption path" spans 4 total variants across 2 domains but does NOT collapse into single "3-of-3 unified delivery domain" claim. Landed in §1.1 + §9.3 + §17.6 hypothesis + §19 T1 #17 rephrase.

- **F4 — §20.6 "4 axes × 7 surfaces" claim tighten + concrete PASS/PARTIAL/FAIL thresholds (Batch A A3).** Rigby SIGN A3 caught overstated matrix claim. Rephrased to "4 axes evaluated across 7 surfaces as applicable" + retained §20.6.5 cross-axis matrix + added concrete PASS/PARTIAL/FAIL thresholds per 1-2 key criteria per axis (D65a container ownership + factory adoption; D65b gate scope + composition contract; D65c correction coverage + learning-loop closure; D65e auth uniformity + audit uniformity). Landed in §20.6 opening scope-clarification block + §20.6.1-.4 F2 scoring rubric expansion.

- **F5 — §17.6 Candidate C extension reframed as Cat F hypothesis (Batch A A4).** Rigby SIGN A4 caught overreach vs S1605 F9 LOCKED anchor. Reframed §17.6 from architectural commitment to Cat F hypothesis with explicit scope boundaries (what Candidate C cross-domain extension does NOT cover: Employee OS + Signal Engine + Revenue delivery-domain-ownership + ClaimsPack). Explicit selection contract: adoption only if PASS across required surfaces per §20.6.4 evidence gate. Cat E anchor sentence LOCKED remains authoritative for Cat E-scoped surfaces (PA-tool + REST + Frontend). Landed in §17.6.

- **F6 — §9.4 "OUTPUT-side WRITE absent" claim rephrase to PARTIAL bridge (Batch B B1).** Rigby SIGN B1 caught over-strong "0-hit AgentMemory|AgentPerformance" claim missing the `_record_content_feedback` PA-tool bridge at `td_handlers_content.py:184`. Verified independently via grep — 8 call sites at :557/:592/:637/:1184/:1337/:1370/:1399/:1438 all write AgentMemory `memory_type='feedback'` for PA-driven content approve/publish/complete/archive actions. **Corrected framing:** auto-close-loop from PublishGate/panel path ABSENT + PARTIAL PA-tool feedback bridge via `_record_content_feedback` for PA-driven actions. §9.4 verdict revised from "OUTPUT ABSENT" to "PARTIAL at output". §13 maturity + §9.4 evidence + §1.1 headline + §7.4 Flow M all updated. Landed in §1.1 + §9.4 + §7.4 + §13.

- **F7 — T.15.F6 severity split (Batch B B2).** Rigby SIGN B2 flagged classification issue — "unified outbound-delivery domain ABSENT" mixed active debt condition with proposed unification. **Split:** §15 T.15.F6 records DEBT CONDITION (CRITICAL - outbound rails missing across Newsletter + OutreachDraft + Sports orphan variants); §19 T1 #17 records solution candidate ("unified outbound-delivery domain" is ONE candidate among cross-arc ownership variations; xx99 §5 evidence plan resolves). Landed in §15 T.15.F6 + §19 T1 #17 rephrase.

- **F8 — §14 D.14.F1 explicit "S1605 owns runtime probe" acknowledgment (Batch B B3).** Rigby SIGN B3 flagged hygiene risk — Cat F should not present itself as re-verifying runtime. Explicit note added: "Runtime verification performed in S1605 (Batch A F1 fold via ops_tool.celery_task_history 30d = 0 events + scheduled_tasks_tool = 0 tasks); Cat F only propagates correction per parent F11 consolidation-lens boundary rule and does NOT re-verify." 5 doc PRs owed at xx99 §7 anchor-updates (not re-verified at Cat F scope). Landed in §14 D.14.F1.

- **F9 — §19 T1 ranking corrections (Batch C C1).** Rigby SIGN C1 caught 3 classification issues: (a) #17 R.CONTENT.UNIFIED-OUTBOUND-DELIVERY-DOMAIN "unified domain" phrasing was solution/ADR not research; **rephrased** to R.CONTENT.OUTBOUND-DELIVERY-CONSUMPTION-RAILS-GAP (research condition) with "unified outbound-delivery domain" as one candidate solution among cross-arc ownership variations. (b) #21 R.CONTENT.CROSS-DOMAIN-EMPLOYEE-ANALOG had severity mismatch (§15 T.15.F5 MEDIUM vs §19 elevated to T1); **demoted to T3** per Rigby recommendation (Content Employee analog is NOT hard dependency for CRITICAL T1s #1-#20). (c) #22 R.CONTENT.POSTURE was meta-item not conventional research; **renamed** to R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E (ADR-packaging requirement for xx99, not "research"). Landed in §19.1 T1 table.

- **F10 — §9.7 Content Employee ABSENT verdict softened to PARTIAL (Batch C C2).** Rigby SIGN C2 flagged "ABSENT" too absolute — Documentation Manager JobContract at `core/employees/jobs.py:187-280` IS Rigby-owned and Content-adjacent operationally (docs cascade + docs corpus certification). **Corrected verdict:** PARTIAL — Employee OS exists for docs/content-adjacent ops via Rigby Documentation Manager; ABSENT for dedicated content publishing/management employee analog (D55-style). §1.1 bullet + §1.3 maturity table + §9.7 evidence + §13 maturity all updated. Landed in §1.1 + §1.3 + §9.7 + §13.

**D48 preemptive stability-probe gate 15th arm outcome:** Batches A + B + C all substantive on fresh isolation pin + final consolidated verdict single-message follow-up clean. **TEN-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606 CONFIRMED** — extends 14-arc pattern to 15-arc + S1606 clean. Codification-ready-STRENGTHENED-FURTHER for playbook v3 §15 with 10-consecutive-fully-clean sub-pattern (from 9-consecutive at S1605 close).

**Fresh isolation pin `pa-8cfafefb67864f83` retired at S1606 close via `session_tool.retire` (per `feedback_session_tool_retire_works.md`).** Confirmation: `{"action":"retire","conversation_id":"pa-8cfafefb67864f83","retired":true,"updated_count":2}`.

### 20.6 Posture-decision evidence plan for xx99 (LOAD-BEARING; per parent §3 F "posture-decision evidence plan owed to xx99 per D65-analog four-axis framing"; per S1599 §5 F2 fold rubric exemplar)

**Scope clarification per Rigby SIGN Batch A F4 fold:** §20.6 evaluates **4 axes across 7 surfaces as applicable** (NOT a full 4×7=28-cell axis×surface matrix). Each axis lists per-surface applicability at §20.6.5; each axis evaluates postures using PASS/PARTIAL/FAIL rubric on the surfaces where the axis applies (per §20.6.5 matrix "N/A" cells). Concrete PASS/PARTIAL/FAIL thresholds are called out per axis on 1-2 key criteria (F4 fold).

Per playbook §14.5 no-implementation rule + parent F11 boundary rule + xx99 §5 posture-decision evidence plan pattern from S1599 (F2 fold rubric adoption): Cat F does NOT select. Cat F produces evidence plan for xx99 consumption. xx99 selects the posture in Chris-gated ADR round.

**Structure per S1599 §5 F2 fold rubric + S1500 D62 propagation:**

1. **Posture success criteria per axis** (integration vs island) — drawn from S1274 §12.3 baseline + P1-P5 evidence.
2. **Evidence FOR each posture** — cite P1-P5 §N.M per criterion.
3. **Evidence AGAINST each posture** — cite P1-P5 §N.M per criterion.
4. **Operational cost estimate per posture** — P1 (large; multi-quarter) vs P0 (small; single-arc).
5. **Failure-modes-if-criteria-not-met** — per posture, per axis.
6. **F2-fold scoring rubric with PASS/PARTIAL/FAIL thresholds per criterion** — adopted from S1506 §20.6 §F per S1599 §10.2 codify-ready.
7. **Explicit "Chris-gated selection" tag** — xx99 does NOT pick; ADR does.

#### 20.6.1 Axis D65a — Deliverable canonicalization

**Question:** Is Deliverable the canonical content container across domains, with variants expressed as typed subkinds (or metadata), OR are variants first-class siblings with independent schemas and lifecycles?

**Postures:**
- **Integration posture:** All content-shaped outputs become Deliverable subkinds (typed) or Deliverable rows with metadata; variants retire OR extend as Deliverable subclasses.
- **Island posture:** Variants remain first-class independent schemas with own lifecycles; Deliverable stays as base with optional forward FK to select variants (SelfBlog + PodcastEpisode current pattern).

**Success criteria per posture:**

| Criterion | Integration posture criterion (PASS threshold) | Island posture criterion (PASS threshold) |
|-----------|-----------------------------------------------|-------------------------------------------|
| Container ownership clarity | Single canonical container schema | Per-variant schema clarity |
| Cross-domain analytical unification | Unified Deliverable queries span all content types | Per-variant analytical queries acceptable |
| Factory adoption completeness | 100% variant creation routes through factory or factory-extension | Factory scope stays base-only; variants own creation |
| Lifecycle transition uniformity | Unified state machine for Deliverable status | Per-variant state machines acceptable |
| Cross-domain audit uniformity | Unified DeliverableEvent stream covers all writes | Per-variant event streams acceptable |

**Evidence per criterion:**

| Criterion | Evidence FOR integration | Evidence AGAINST integration | Evidence FOR island | Evidence AGAINST island |
|-----------|-------------------------|------------------------------|---------------------|-------------------------|
| Container ownership | 47-file Deliverable adoption at HEAD (Cat D §5) | 5 variants zero-reverse-FK at HEAD (Cat D §1 headline) | Variants have own status semantics (Cat D §1) | SportsBettingBrief + BlockchainAuditBrief unfinished/orphan (Cat D §1 category 3) |
| Cross-domain analytics | Deliverable factory + base contract stable (Cat D §5) | Variant queries currently work at Revenue/Sports domain | Variant lifecycle independence acceptable (Cat D §8) | Cross-arc SportsBettingBrief consumer ABSENT (S1504 §14.3) |
| Factory adoption | 47 create sites at HEAD; only 2 bypasses (Cat D §5) | Variants bypass factory entirely (Cat D §5) | Bypasses documented + legitimate (Cat D §5) | Variant creation drift risk (Cat D T2) |
| Lifecycle uniformity | Cat C PublishGate SelfBlog-only extendable to variants (Cat C §17.4) | Variant-specific gates needed per-domain (Cat C §17.4) | Per-variant gate acceptable (Cat C §17.4) | Triple-gate composition contract MISSING (Cat D §17.4 T.15.6 + Cat C T1) |
| Cross-domain audit | DeliverableEvent partial coverage extendable (Cat E T.15.E5) | update/create/append/delete NOT written (Cat E T.15.E5) | Per-variant events acceptable | 8 event models absent (Cat F §10) |

**Operational cost per posture:**

- **Integration:** P1 (multi-quarter). Requires: factory-extension for variants OR variant retirement + Deliverable subclass model design; migration of 4+ variant models to unified schema OR careful preserve-semantics migration; PublishGate variant-extension; unified event stream; audit trail retrofit for update/create/append/delete DeliverableEvent writes.
- **Island:** P0 (single-arc). Requires: DOCUMENT variant taxonomy (Cat D 3-category) as canonical; RETIRE unfinished orphan variants (SportsBettingBrief + BlockchainAuditBrief consumer-or-remove ADR); LEAVE standalone-by-design (OutreachDraft + ClosePack) in Revenue-owned domain.

**Failure modes if criteria not met:**

- **Integration:** silent variant-schema divergence; multi-quarter partial adoption; cross-boundary FK bugs; migration-window state instability.
- **Island:** persistent write-only-forgotten pattern extends; cross-domain analytics gap widens; variant lifecycle drift; retention/archival ad-hoc.

**F2 scoring rubric (concrete PASS thresholds per key criterion per Rigby F4 fold):**

- **Container ownership PASS threshold:** 100% content-shaped outputs land as Deliverable subkinds OR Deliverable rows; 0 residual island variants at HEAD. PARTIAL if 2 island variants remain post-migration; FAIL if >2 remain.
- **Factory adoption PASS threshold:** 100% variant + Deliverable creation routes through factory OR factory-extension; 0 bypasses. PARTIAL if ≤2 documented bypasses (current HEAD state); FAIL if >2.

Per remaining criterion, xx99 evaluates each posture at PASS / PARTIAL / FAIL based on evidence FOR + AGAINST. Sum across 5 criteria; posture with more PASS or fewer FAIL wins.

**Chris-gated selection tag:** *"Cat F does NOT select D65a posture. xx99 §5 consolidates + ranks + writes Chris-gated ADR post-arc."*

#### 20.6.2 Axis D65b — PublishGate canonicalization

**Question:** Is PublishGate a single canonical gate with variant/channel-specific policies, OR multiple gate classes/threshold systems per variant/channel?

**Postures:**
- **Integration posture:** Single canonical PublishGate class + per-variant + per-channel policy configuration + unified triple-gate composition contract (factory 5-gate → PublishGate 4-threshold → variant-specific gates unified per resolvable state machine).
- **Island posture:** Per-variant + per-channel gate classes acceptable; SelfBlog-only PublishGate at HEAD preserved; triple-gate composition remains "coexist but unresolved."

**Success criteria per posture:**

| Criterion | Integration criterion (PASS threshold) | Island criterion (PASS threshold) |
|-----------|--------------------------------------|-----------------------------------|
| Gate scope | PublishGate gates all Deliverable-variants | PublishGate stays SelfBlog-only |
| Threshold consistency | Unified threshold configuration across variants | Per-variant thresholds acceptable |
| Composition contract clarity | Single canonical composition state machine (factory → publish gate → variant gate) | Independent gates acceptable |
| Cross-channel uniformity | Same gate applies to Discord + Newsletter + Frontend | Per-channel policies acceptable |
| Audit coverage | Unified PublishGateEvent stream covers all gate decisions | Per-channel events acceptable |

**Evidence per criterion:**

| Criterion | Evidence FOR integration | Evidence AGAINST integration | Evidence FOR island | Evidence AGAINST island |
|-----------|-------------------------|------------------------------|---------------------|-------------------------|
| Gate scope | Cat D structural evidence variants share Deliverable base (Cat D §4) | PublishGate SelfBlog-only at HEAD (Cat C §1.1) | SelfBlog-only preserves current semantics (Cat C §1.1) | Variants have zero gate at HEAD (Cat C §9.3-9.6) |
| Threshold consistency | 4-threshold class constants easily extended (Cat C §5.1) | Variant-specific tuning may require per-variant thresholds | Per-variant tuning independence | Threshold externalization ABSENT (Cat C T3) |
| Composition contract | Triple-gate 4-candidate framework at Cat C §17.4 | 3 systems entrenched; composition drift high risk (Cat D §17.4 T.15.6) | Independent gates preserve variant SoC | No canonical statement of precedence at HEAD (Cat C §17.4) |
| Cross-channel uniformity | Cat C 3 rails (Frontend + Discord + Newsletter) share content-model | Discord broadcast has ZERO gate integration (Cat C §1.1) | Per-channel policies exist (12 Discord channels) | Fire-and-forget rails hard to gate (Cat C §8.6) |
| Audit coverage | Unified event stream enables analysis + calibration | PublishGateEvent ABSENT at HEAD (Cat C T2 R.PUBLISHGATE-EVENT-TELEMETRY) | Per-channel events sufficient | 8 event models absent (Cat F §10) |

**Operational cost:**

- **Integration:** P1 (multi-quarter). Requires: PublishGate variant-extension (T4); unified composition state machine (Cat C T1 R.TRIPLE-GATE-COMPOSITION-CONTRACT); PublishGateEvent model + telemetry landing (Cat C T2); cross-channel policy config landing.
- **Island:** P0 (single-arc). Requires: DOCUMENT triple-gate composition contract as-is (Cat C §17.4 4-candidate framework); ADR selecting Candidate 1/2/3/4; per-channel policies documented.

**Failure modes if criteria not met:**

- **Integration:** silent gate divergence; cross-channel drift; migration state instability; audit trail retrofit unfinished.
- **Island:** persistent triple-gate ambiguity; silent-quality-regression risk (Cat C T2 CALIBRATION-INVESTIGATION); per-channel divergence.

**F2 scoring rubric (concrete PASS thresholds per key criterion per Rigby F4 fold):**

- **Gate scope PASS threshold:** PublishGate covers all Deliverable-variants OR variant-covered by variant-specific gates AND unified composition contract. PARTIAL if scope stays SelfBlog-only + variants have zero gate (current HEAD state); FAIL if drift widens.
- **Composition contract PASS threshold:** Single canonical composition state machine documented + one canonical resolvable path per gate combination. PARTIAL if 4-candidate framework selected at xx99 but state machine not yet defined; FAIL if MISSING at HEAD (current state).

Per remaining criterion, xx99 evaluates each posture at PASS / PARTIAL / FAIL. Sum across 5 criteria; posture with more PASS or fewer FAIL wins.

**Chris-gated selection tag:** *"Cat F does NOT select D65b posture. xx99 §5 consolidates + ranks + writes Chris-gated ADR post-arc."*

#### 20.6.3 Axis D65c — Lifecycle transition ownership (factory / rails / correction)

**Question:** Is there a single canonical transition orchestrator (e.g., publish rails / lifecycle engine) OR do variants own their own transition rails?

**Postures:**
- **Integration posture:** Single canonical lifecycle-engine orchestrates transitions across Deliverable + variants + cross-domain rails (Discord + Newsletter + Frontend); post-publish correction loops land as unified `ContentLifecycleEngine` service.
- **Island posture:** Variants + rails own their own transitions; per-rail correction acceptable; post-publish correction remains rail-specific (Discord edit_message + newsletter erratum + frontend unpublish).

**Success criteria per posture:**

| Criterion | Integration criterion (PASS threshold) | Island criterion (PASS threshold) |
|-----------|--------------------------------------|-----------------------------------|
| Transition ownership | Single orchestrator owns lifecycle | Per-variant/per-rail orchestrators acceptable |
| Post-publish correction coverage | 100% surfaces have retract/errata/edit path | Best-effort per-rail correction acceptable |
| Force-bypass audit trail | Unified ForcedPublishEvent covers all force=true invocations | Per-rail audit acceptable |
| Learning-loop closure | Unified ContentLearningLoopBridge closes verdict → memory | Per-rail learning acceptable |
| Cross-boundary lifecycle uniformity | Same state machine spans PublishGate → Discord → Newsletter | Per-rail state machines acceptable |

**Evidence per criterion:**

| Criterion | Evidence FOR integration | Evidence AGAINST integration | Evidence FOR island | Evidence AGAINST island |
|-----------|-------------------------|------------------------------|---------------------|-------------------------|
| Transition ownership | Cat E deliverable_tool set_status contract precedent (Cat E §11.3) | Each rail currently independent (Cat C §9) | Per-rail SoC | Post-publish correction ABSENT structurally (Cat C §16.1 T.15.C1) |
| Correction coverage | Unified retract path enables errata compliance | Discord fire-and-forget hard to correct (Cat C §8.6) | Per-rail correction acceptable | ZERO correction paths at HEAD (Cat C §1.1 + Cat F §7.5) |
| Force-bypass audit | Cat E force-bypass audit requirement extends across surfaces (Cat E T1 R.FORCE-BYPASS-AUTH-BOUNDARY) | force=true bypass affordance widens actor scope (Cat E T.15.E3) | Per-rail audit is simpler | ForcedPublishEvent ABSENT at HEAD (Cat E §10.2) |
| Learning-loop closure | Unified bridge closes verdicts + scores + attribution → memory | S1601 T5 intentional decoupling at Cat A boundary | Per-rail learning simpler | ContentEngagement docstring drift extends (S1403 F.C4 + Cat F §9.4) |
| Cross-boundary uniformity | State machine simplifies debugging + audit | Per-rail state machines exist + work | Independent semantics per rail | Cross-boundary asymmetry: PA-tool auth vs REST zero-auth (S1605 T.15.E2) |

**Operational cost:**

- **Integration:** P1 (multi-quarter). Requires: `ContentLifecycleEngine` service design; `ContentLearningLoopBridge` cross-arc Group 1300 ADR; unified `ForcedPublishEvent + AutoPublishEvent + PublishGateEvent + BroadcastLog + RestPublishEvent` event stream; retrofit into existing rails.
- **Island:** P0 (single-arc). Requires: per-rail audit-trail owner ADR; per-rail correction path decision (accept immutable-once-published OR build per-rail retract).

**Failure modes if criteria not met:**

- **Integration:** partial-orchestrator drift; incomplete rail retrofit; state machine divergence during migration.
- **Island:** persistent post-publish correction absence (compliance risk); silent force-bypass audit gap; learning-loop never closes.

**F2 scoring rubric (concrete PASS thresholds per key criterion per Rigby F4 fold):**

- **Correction coverage PASS threshold:** 100% publish surfaces (SelfBlog + variants + Discord + Newsletter) have retract/errata/edit path. PARTIAL if ≥1 surface has correction; FAIL if 0 (current HEAD state — CRITICAL structural gap).
- **Learning-loop closure PASS threshold:** PublishGate scores + reviewer verdicts + author attribution all bridge to AgentMemory/AgentPerformance via unified event stream OR PA-tool bridge. PARTIAL if only PA-tool `_record_content_feedback` bridge exists (current HEAD state per F6 fold); FAIL if 0 bridges.

Per remaining criterion, xx99 evaluates each posture at PASS / PARTIAL / FAIL. Sum across 5 criteria; posture with more PASS or fewer FAIL wins.

**Chris-gated selection tag:** *"Cat F does NOT select D65c posture. xx99 §5 consolidates + ranks + writes Chris-gated ADR post-arc."*

#### 20.6.4 Axis D65e — Rigby PA-tool surface unification + cross-boundary enforcement centralization

**Question:** Is Rigby's tool surface + REST + Frontend contract preserved as 4-tool + 3-surface split with shared enforcement, OR consolidated per surface?

**Postures:**
- **Integration posture (Cat E anchor sentence LOCKED per S1605 F9):** *"Preserve the 4-tool interface, but centralize enforcement (auth/audit/scope/gates) so the split can't produce divergent behavior."* Cat F EXTENDS: enforcement centralization spans PA-tool + REST + Frontend + Discord + Newsletter + Memory-learning-loop.
- **Island posture:** 4-tool split + REST + Frontend surfaces preserved with per-surface enforcement; asymmetric auth accepted (with role-gate ADR); no cross-boundary unified layer.

**Success criteria per posture:**

| Criterion | Integration criterion (PASS threshold) | Island criterion (PASS threshold) |
|-----------|--------------------------------------|-----------------------------------|
| Auth boundary uniformity | UnifiedContentAuthLayer covers PA-tool + REST + Frontend | Per-surface auth (with ADR) acceptable |
| Audit trail uniformity | Unified event stream covers all publish paths | Per-surface audit acceptable |
| Workspace scoping consistency | Mandatory dispatcher-level scoping | Handler-level opt-in acceptable |
| Cross-boundary gate integration | PublishGate applies at all surfaces | Per-surface gate ADR acceptable |
| Force-bypass control | Unified admin-only force policy | Per-surface force policy acceptable |

**Evidence per criterion:**

| Criterion | Evidence FOR integration | Evidence AGAINST integration | Evidence FOR island | Evidence AGAINST island |
|-----------|-------------------------|------------------------------|---------------------|-------------------------|
| Auth uniformity | PA-tool has AssistantProfile allowlist STABLE (Cat E §1.1) | Cat E anchor LOCKED Candidate C ratified (S1605 F9) | Per-surface auth simpler at each surface | REST + Frontend ZERO auth boundary (S1605 T.15.E2 CRITICAL) |
| Audit uniformity | ToolCallRecord partial coverage extendable (Cat E §1.1) | Per-surface audit acceptable if trail present | Per-surface acceptable | REST-side + Frontend ZERO audit at HEAD (Cat E §1.1 + §10.2) |
| Workspace scoping | Handler-level opt-in with silent-degrade risk (Cat E T.15.E1) | Cat A UNK-1 workspace-scope pattern extends | Handler-level exists + works when populated | Silent-degrade cross-tenant risk (T1 R.CONTENT.RAG-SCOPE + Cat E T.15.E1) |
| Gate integration | Discord broadcast lacks gate integration (Cat C §1.1) | Per-rail gate acceptable | Fire-and-forget preserves rail simplicity | Zero cross-boundary gate at HEAD (Cat F §9.5) |
| Force-bypass control | Cat E force-bypass T1 requires unified admin policy | force=true affordance in Frontend (Cat E T.15.E3 HIGH) | Per-surface force policy acceptable | ContentStudioTab hardcodes force=true; no role gate (Cat E T.15.E3) |

**Operational cost:**

- **Integration:** P1 (multi-arc). Requires: UnifiedContentAuthLayer service design; unified audit event models (Cat F §10 8-model landing); mandatory dispatcher-level scoping migration; gate-integration wiring across rails; unified force policy.
- **Island:** P0 (single-arc). Requires: per-surface auth ADR (REST + Frontend); per-surface audit event landing; per-surface force policy documentation.

**Failure modes if criteria not met:**

- **Integration:** partial enforcement drift; migration-window auth-boundary hole; per-surface retrofit inconsistency.
- **Island:** persistent asymmetric auth (Cat E T.15.E2 CRITICAL preserves); force-bypass widen scope; cross-tenant silent-degrade risk continues.

**F2 scoring rubric (concrete PASS thresholds per key criterion per Rigby F4 fold):**

- **Auth uniformity PASS threshold:** UnifiedContentAuthLayer or shared decorator covers PA-tool + REST + Frontend. PARTIAL if ≥2 surfaces have consistent auth (e.g., PA-tool has dispatcher allowlist); FAIL if 1 or 0 surfaces have auth boundary (current HEAD state — REST + Frontend both ZERO auth per S1605 T.15.E2 CRITICAL).
- **Audit uniformity PASS threshold:** Unified event stream covers PA-tool + REST + Frontend publish paths (8 event models per §10 Cat F). PARTIAL if partial coverage exists (current HEAD state — ToolCallRecord PA-side + DeliverableEvent partial); FAIL if only 1 partial writer.

Per remaining criterion, xx99 evaluates each posture at PASS / PARTIAL / FAIL. Sum across 5 criteria; posture with more PASS or fewer FAIL wins.

**Chris-gated selection tag:** *"Cat F does NOT select D65e posture. xx99 §5 consolidates + ranks + writes Chris-gated ADR post-arc. Cat E anchor sentence LOCKED for Candidate C provides pre-xx99 lean anchor per S1605 F9 fold; Cat F HYPOTHESIS + SCOPE-BOUNDED per F5 fold — Candidate C cross-domain extension is a hypothesis to be tested at §20.6 evidence, NOT a Cat F architectural commitment (§17.6 scope boundaries apply)."*

#### 20.6.5 Cross-axis matrix — seven-surface × four-axis posture-decision framing

Cat F consolidates each cross-domain surface × each D65-axis for xx99 §5 consumption:

| Surface | D65a Deliverable canonicalization | D65b PublishGate canonicalization | D65c Lifecycle transition | D65e Enforcement centralization |
|---------|-----------------------------------|-----------------------------------|---------------------------|--------------------------------|
| Signal Engine | N/A (read-only consumer) | N/A (no gate scope) | N/A (no transition on Signal side) | N/A (dispatcher-side already unified per Cat E) |
| Sports | Cat D §1 category 3 orphan bucket; consumer-or-remove | N/A (zero gate; zero rail) | Consumer-or-remove owns transition | Would apply if variants gain rails post-consumer-ADR |
| Revenue | Cat D §1 category 2 standalone; OutreachDraft + ClosePack cross-arc | N/A (zero gate on delivery path) | Delivery domain ownership Chris-gated | Applies IF pattern class 3-of-3 unifies as OutboundDeliveryDomain |
| Memory | N/A (input side read only; ContentEngagement docstring drift) | N/A (learning-loop bridge is not a gate) | Learning-loop bridge is transition-adjacent | Applies IF bridge lands as unified event-consuming service |
| Discord | N/A (broadcast is not a Deliverable) | Broadcast gate integration ADR owed | Broadcast retract path ABSENT (T.15.F10) | Applies IF broadcast wraps in unified event layer |
| Frontend | Applies for envelope→object surface (BlogViewerPage on SelfBlog) | Applies for gate-driven UX (canPublish unification) | Applies for approve/publish + retract UX | Cat E anchor LOCKED Candidate C directly |
| Employee OS | N/A (no Content Employee at HEAD) | N/A | Employee JobContract precedent D55 | Applies IF Content Employee analog materializes with JobContract that spans Content authority |

**xx99 §5 consumption note:** xx99 selects postures via evidence plan above; xx99 does NOT compress the four axes into a single "integration vs island" choice. Chris-gated ADR round at post-arc resolves each axis + cross-cutting decisions independently per S1599 §5 F2 fold rubric exemplar.

### 20.7 Unresolved unknowns

- UNK-F1: Are there Content-adjacent Discord channels beyond the 12 constants at `discord_notifications.py:36-47` that Cat F might have missed?
- UNK-F2: Is the pattern class 3-of-3 (OutreachDraft + Newsletter + BlockchainAuditBrief-analog) genuinely a unified delivery domain, OR does OutreachDraft belong strictly to Revenue delivery vs Newsletter to Content-adjacent vs Blockchain to Sports-adjacent (three separate domains)?
- UNK-F3: Does the Content Employee analog to D55 actually match Content domain scope, or does the Documentation Manager job on RIGBY handle sufficiently cover Content-adjacent authority?
- UNK-F4: Cross-arc Group 1300 Memory arc closure state — has S1300 completed, and if yes, does it record ContentLearningLoopBridge as owed?
- UNK-F5: If integration posture selected at xx99 for D65a Deliverable canonicalization, is retirement of SportsBettingBrief + BlockchainAuditBrief preferred over migration to Deliverable subclass? (Cat D T2 dispositions suggest possible but no decision.)

### 20.8 Verifier-loop provenance

**Pre-Explore verifier-loop:** Cat F consumed 5 sibling audits verbatim (S1601 + S1602 + S1603 + S1604 + S1605) + 4 cross-arc handoffs (S1504 + S1502 + S1402 + S1403 + S1499 D55). Each sibling audit's §20.5 fold notes + §20.4 handoffs matrix consumed as evidence.

**Post-Explore verifier-loop:** Explore-agent sweeps NOT spawned this session per S1606 punch list allowance ("Cat F may use fewer than 6 Explore sub-agents"). Instead: targeted parent-Claude grep verification of load-bearing cross-domain binary claims via §20.3 grep patterns list. All grep verifications executed against HEAD `c7a3c16e` (post-S1605 merge).

**Post-verifier corrections landing at Cat F draft:**
- P0-CORRECTION-CATF1: Employee count at `core/employees/jobs.py` verified 4 (RIGBY + PLATFORM_AUDITOR + CHIEF_OF_STAFF + BUG_TRIAGE_SPECIALIST) — CLAUDE.md narrative says 3 (Documentation Manager as Rigby + Platform Auditor + Chief of Staff); drift documented at D.14.F3 as inherited from S1499 doctor warning.
- P0-CORRECTION-CATF2: SportsBettingBrief footprint verified 5 files (tasks.py + models/__init__.py + models_unified_system.py + tasks_content.py + migrations/0242) — Cat F confirms S1504 §14.3 CRITICAL zero-consumer at HEAD.
- P0-CORRECTION-CATF3: OutreachDraft footprint verified 16 files including PA-tool schema + beat + views + tests + migrations — Cat F confirms S1402 F.B1 F8-CRITICAL zero-outbound at HEAD.
- P0-CORRECTION-CATF4: `publish_gate.py` grep `AgentMemory|AgentPerformance|discord_notify|CHANNEL_` returns 0 hits — Cat F confirms S1604 §1.1 headline PublishGate ZERO auto-broadcast + Cat A S1601 T5 learning-loop OUTPUT ABSENT.
- P0-CORRECTION-CATF5: 12 CHANNEL_ constants verified at `discord_notifications.py:36-47` — Cat F confirms Cat C §8.6 12-channel count.
- P0-CORRECTION-CATF6: S1605 F1 fold `auto_publish_approved_blogs` runtime-verified ABSENT propagates to Cat F §14 D.14.F1 without re-verification (Cat F is consolidation lens; runtime probe was S1605-owned).

**Verifier-loop resolution:** all load-bearing cross-domain binary claims grep-verified at HEAD `c7a3c16e` before Cat F ships to Rigby SIGN.

---

*End of Session 1606 Cat F child audit. LAST child under Group 1600. Route to Rigby SIGN cycle 1 via fresh isolation pin per playbook §15 + F1-Fn folds landed pre-commit per §20.5. Next session: S1699 xx99 canonical summary (fourth application of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second + S1599 third).*
