---
title: "S1600 Content / Deliverables / Publishing — Parent Architecture Scoping (Group 1600 mission plan)"
status: active (parent — all Chris decisions locked 2026-07-02: D63 D64 D65a D65b D65c D66 D67 D68 via one "agree all + D-6=(a)" ratification round; governance decision `2c469638-643d-4477-a8ea-1766b552eebe` acted; Rigby pre-ratification pressure-test folded via F1-F12 into §3/§5/§7/§8/§12 wording; Rigby Light SIGN cycle 1 → cycle 2 SIGN-clean at High confidence 2026-07-02 → F1-F12 folds landed at commit-time — F1 §3 Cat A ClaimsPack boundary rule; F2 §3 Cat C/D crisp boundary rules; F3 §5 P3↔P4 swap (Cat D before Cat C); F4 §8 D65 split into D65a Deliverable-canonicalization + D65b PublishGate-canonicalization + D65c Lifecycle-transition-ownership; F5 §7 anti-scope 12→18 items; F6 §12.4 discriminative-value tightening with required decision-discriminative proof + disconfirming evidence item; F7 §12.5 Deliverable Lifecycle Traceability Table 10→12 stages with normalization/canonicalization + eligibility/packaging-gate stages; F8 one-sentence boundary rule per category; F9 binary posture framing with mushy-hybrid disallowed; F10 D66 dependency-clause embedding; F11 §3 Cat E feedback-hazard note; F12 ClaimsPack centrality preserved via F1 boundary rule)
authority: parent-doc for Group 1600 research arc + THIRD application of Chris's Phase 0 3-step methodology (Domain Definition / Existing Knowledge Inventory / Success Criteria) — playbook v3 §11.1 template promotion TRIGGERED per S1599 §12.4 discriminative-value criterion (4 of 4 evidence types satisfied); this arc applies methodology unchanged for third-trigger confirmation + adopts D62 = (a) 6-sibling exemplar mini-schema propagation-upfront pattern per S1599 §10.2 codify-ready candidate
category: parent_scoping
session: 1600
date: 2026-07-02
decisions_locked: 2026-07-02 (D63 D64 D65a D65b D65c D66 D67 D68 via "agree all + D-6=(a)" ratification round; governance decision `2c469638-643d-4477-a8ea-1766b552eebe` marked `acted`)
domain_slug: content
research_group: 1600
authors: Claude Code (Chris directed via short command "Let's do Group 1600 next, I want to get all of the research done" at S1600 open)
supersedes: none
related:
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                             # process — §11.1 template applied here for the third time
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md                    # OS — arc-open contract §8
  - docs/research/OPEN_ARCS.md                                            # arc manifest — Group 1500 → Group 1600 handoff
  - docs/research/ARCHITECTURE_INDEX.md                                    # v34 → v35 bump proposed downstream at S1600 close
  - docs/research/platform/cross_domain_integration_audit.md              # S1274 15-finding baseline; §12.3 island-vs-integrated posture precedent (analog D59)
  - docs/research/domains/memory/1300_memory_domain_scoping.md            # parent-with-children exemplar (S1300)
  - docs/research/domains/memory/1399_memory_canonical_summary.md         # first formal xx99 canonical summary (S1399)
  - docs/research/domains/revenue/1400_revenue_domain_scoping.md          # first application of Phase 0 F.i/F.ii/F.iii methodology (S1400) — trigger 1 of two-triggers rule
  - docs/research/domains/revenue/1499_revenue_canonical_summary.md       # second xx99 canonical summary + second §11.3 §10 template application
  - docs/research/domains/sports/1500_sports_domain_scoping.md            # second application of Phase 0 F.i/F.ii/F.iii methodology (S1500) — trigger 2 of two-triggers rule
  - docs/research/domains/sports/1599_sports_canonical_summary.md         # third xx99 canonical summary + third §11.3 §10 template application + §12.4 discriminative-value criterion check 4-of-4 evidence types satisfied → playbook v3 §11.1 promotion TRIGGERS
  - docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md  # S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN + §5.1 SportsContentContextBuilder HOT-PATH-CHOKE cross-arc handoff
  - docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md  # S1402 F.B1 revenue arc found ZERO outbound channel — cross-arc pattern to verify for content publishing
  - docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md  # S1403 F.C4 ContentEngagement docstring drift
  - docs/topics/content-pipeline.md                                       # Session 1147 topic doc — pattern still valid, specific numbers may drift
  - docs/PLATFORM_INVENTORY.md                                            # runtime counts anchor
  - docs/PLATFORM_WHAT_IT_IS.md                                           # narrative anchor
scope: Phase 0 domain-definition — decide whether Group 1600 is a single canonical audit or a parent-with-children research arc; produce candidate subdomain taxonomy grounded in verified runtime surface; propose child mission sequence for Chris to lock; frame (do NOT decide) the analog D59 load-bearing question — is Deliverable a canonical container OR a base with parallel-schema-siblings each with own PublishGate/lifecycle? — as the arc's lens question owed to xx99 canonical summary as evidence plan, not recommendation
non_goals:
  - the audit itself (that begins after Chris picks parent-vs-single + locks §5 sequence)
  - answering the 28 playbook canonical questions (that is the audit's job)
  - resolving the analog D59 posture at Phase 0 (requires child evidence sweeps; posture decision framing + evidence plan only — Chris gates actual selection post-arc after xx99 evidence lands)
  - any implementation proposal (this is scoping, not architecture design)
  - non-Content Deliberation output surfaces without a research-worthy question (e.g., legacy PDF exports without a pattern to investigate)
  - external companion project scope (`BILLING_MONETIZATION_SYSTEM.md` from ai-content-studio — matches S1400/S1500 pattern)
  - Content Pipeline v1 legacy runner details beyond identifying "v2 canonical vs v1 legacy" boundary (that is a child audit's job)
  - Deliverable schema migration proposals (this is scoping, not migration)
  - Content Deliberation LLM provider selection (product decision, not architecture)
delegates_to:
  - S1300 Memory Domain (learning-loop path for reviewer verdicts + PublishGate scores + author-attribution feedback into Memory arc — Category F sub-question if promoted)
  - Group 1500 Sports arc-close T1.h R.D4 SportsBettingBrief consumer-or-remove disposition (cross-arc — Group 1600 evidence should inform T1.h decision; if Group 1600 selects integration posture, SportsBettingBrief remains parallel model with sibling contract; if island posture, sports domain owns disposition alone)
  - Group 1400 Revenue arc-close F.B1 outreach delivery ADR (cross-arc — OutreachDraft is parallel deliverable-shaped model; Group 1600 evidence informs whether OutreachDraft should adopt Deliverable canonical shape or remain parallel)
owner: claude (Chris directed at S1600 open via short command "Let's do Group 1600 next, I want to get all of the research done")
verifier_loop: Rigby Light SIGN cycle 1 SIGN-with-edits 2026-07-02 → 12 folds landed (F1-F12; taxonomy no-break) → cycle 2 SIGN-clean at High confidence 2026-07-02 (matches S1500 cycle-1-predict-cycle-2 pattern). Two "do not regress" notes for PR: (i) preserve §5 P3↔P4 F3 swap Cat D BEFORE Cat C explicit dependency clauses; (ii) preserve §8 D65a/D65b/D65c three-orthogonal-axis split preventing agree-all masking
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/platform/cross_domain_integration_audit.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/topics/content-pipeline.md
---

# Session 1600 — Content / Deliverables / Publishing Domain Taxonomy Proposal (Phase 0)

> **What this doc is.** A scoping deliverable produced *before* any
> Content domain audit begins. Chris typed the short command
> "Let's do Group 1600 next, I want to get all of the research done"
> at S1600 open — the D63-analog launch verdict per playbook §22
> next-arc queue default (Group 1500 closed at S1599). This doc
> opens the arc by (a) recording the six proposed Chris-ratified
> verdicts D63-D68 (pending Rigby pre-ratification pressure-test),
> (b) demonstrating from verified runtime evidence that Content /
> Deliverables / Publishing is much larger than any single
> subsystem view captures — a 1-canonical-base + 5-parallel-variant
> model surface (Deliverable + SelfBlog + OutreachDraft + ClosePack +
> SportsBettingBrief + BlockchainAuditBrief) + 6-service pipeline
> (ClaimsPack + ContentWriter + 3-reviewer panel + DecisionEnforcer
> + PublishGate) + 3-Rigby-tool surface (deliverable_tool +
> content_tool + blog_tool + newsletter_tool) + Discord broadcast
> chain + BlogViewerPage/ContentPage frontend + 6-Celery-beat
> schedule, (c) proposing a candidate subdomain taxonomy Chris can
> inspect and edit, and (d) framing the analog D59 load-bearing
> question — "is Deliverable a canonical container, or a base with
> parallel-schema-siblings each with own PublishGate/lifecycle?" —
> as the arc's lens question with **posture decision framing +
> evidence plan** as the deliverable owed to xx99, NOT posture
> recommendation (D65-analog refinement anticipated pre-lock).
>
> **What this doc is not.** The audit itself. A design proposal. A
> recommendation about *how* Content should work. Not a posture
> selection between Deliverable-canonical and parallel-siblings —
> that decision is Chris-gated per D65-analog and requires child
> evidence sweeps that have not yet run. Every claim below cites
> either an existing research doc (S1273 / S1274 / S1300 / S1399 /
> S1400 / S1499 / S1500 / S1504 / S1506 / S1599) or a verified
> file:line at the current `main` HEAD (`82e8efe6`).

---

## 1. Why Phase 0

The Group 1500 Sports/DBAO/Intelligence arc closed at S1599 as the
**third successful parent-with-children application** (following
Group 1300 Memory closed at S1399 + Group 1400 Revenue closed at
S1499). All three prior arcs opened with Phase 0 scoping doctrine:
Group 1300 established the pattern (S1300 parent scoping → 5-child
arc → S1399 canonical summary); Group 1400 refined it by applying
Chris's Phase 0 F.i/F.ii/F.iii 3-step methodology (D29 Chris-locked
at S1400 open) as a first empirical application proposed for
playbook v3 §11.1 template addition on the two-triggers rule;
Group 1500 applied it unchanged as the second trigger per D58; and
S1599 §12.4 discriminative-value criterion check **satisfied all 4
evidence types** (Scope confusion prevented via D60 + Rework
reduced via §11.4 F.ii boundary + Cleaner arc close via 6-of-6
SIGN-with-edits + Chris-lock efficiency via single agree-all
round D56-D61) → **playbook v3 §11.1 template promotion TRIGGERS**
per Rigby SIGN cycle 1 Q7 fold. Group 1600 is the **third
application** of the methodology and adopts D62 = (a) 6-sibling
exemplar mini-schema propagation-upfront pattern per S1599 §10.2
codify-ready candidate.

The playbook §22 domain queue row for Group 1600 is (inferred from
S1499 §8 + S1599 §12.7 forward reference):

> **1600** — Content / Deliverables / Publishing — resolves how
> Content Deliberation v2 pipeline + Deliverable canonical container
> + PublishGate output rail integrate across 5 parallel deliverable-
> shaped models (SelfBlog + OutreachDraft + ClosePack +
> SportsBettingBrief + BlockchainAuditBrief) + cross-arc handoffs
> from Group 1400 Revenue (OutreachDraft F.B1 delivery MISSING) +
> Group 1500 Sports (SportsBettingBrief WRITE-ONLY-FORGOTTEN
> S1504 §14.3 + SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS
> S1504 §5.1) + Group 1300 Memory (learning-loop feedback).

The label carries three coordinated nouns ("Content / Deliverables /
Publishing") — the same signal that predicted parent-with-children
shape for Groups 1300 ("Memory / Knowledge / Embeddings"), 1400
("Revenue / Outreach / Engagement"), and 1500 ("Sports / DBAO /
Intelligence"). Whether that pattern-match holds — and if so, what
the correct subdomain decomposition is — is the first-order Phase 0
question.

There is a **second-order** Phase 0 question specific to Group 1600
that requires a D59-analog treatment (following Chris's ratified
methodology): **is Deliverable a canonical container that all
content-shaped outputs subclass/relate to, OR is it a base with
parallel-schema-siblings each with own PublishGate/lifecycle?**
This decision point has structural evidence both directions at
HEAD `82e8efe6`:

- **Integration posture evidence FOR:** Deliverable base model at
  `core/models_deliverables.py:84` with 50+ fields, `publish_intent`
  enum per Rigby Session 1094 memory rule
  (`feedback_publish_intent_enum.md`), workspace FK, tags,
  source_operation FK, content_format, initiative FK; central
  factory `deliverable_factory.py:1269` consolidating 23+ scattered
  creation calls; `deliverable_tool` PA gateway with 18 supported
  actions; 5-gate quality check (media_stub / smoke_pattern /
  min_length / template_leak / no_relevance) at
  `deliverable_factory.py:46-74`; DeliverableAppend + DeliverableExport
  + DeliverableEvent + ContentPacket supporting models.
- **Island / parallel-siblings posture evidence FOR:** 5 parallel
  deliverable-shaped models exist (SelfBlog + OutreachDraft +
  ClosePack + SportsBettingBrief + BlockchainAuditBrief) with own
  `publish_ready` / `status` / lifecycle fields; SelfBlog has its
  own quality gate at `models_unified_system.py:20708-20728`
  (quality_score / novelty_score / structure_score / publish_ready /
  gate_notes) distinct from Deliverable base gate; PublishGate at
  `publish_gate.py:27` operates on SelfBlog-shaped inputs (per docstring)
  not Deliverable base; content_review_panel_v2 dispatches to reviewer
  functions with SelfBlog-adjacent output shape; SportsBettingBrief
  operates in complete isolation from Deliverable base (S1504 §14.3
  WRITE-ONLY-FORGOTTEN pattern confirmed at 2-writer / 0-reader).

That posture-decision point is currently the platform's largest
structural question about content authorship, review, and publish
lifecycle. Phase 0 must decide how to route that question through
the arc: does xx99 owe an evidence-based posture recommendation, or
does xx99 owe a posture decision framing + evidence plan that
leaves the actual selection to Chris in a post-arc T-slot?

**Proposed D65-analog answer:** Phase 0 frames the posture question
and specifies the evidence plan; children gather the evidence; xx99
consolidates the evidence into a Chris-gated decision brief; Chris
picks the posture in a post-arc ADR. This preserves Phase 0's
scoping-only discipline (playbook §8 rule: parent is not a design
proposal) and matches the S1500 D59 pattern that produced a clean
S1599 arc-close per S1599 §12.4 discriminative-value criterion
check.

The playbook (S1274 §2 rule 3) explicitly permits and encourages
this shape:

> If the domain is bigger than expected, splitting into sub-groups
> is fine. Do not force a single session to cover a multi-subsystem
> domain.

The load-bearing questions for Phase 0:

1. **Is Content one domain, or a parent capability composed of
   several subdomains that each warrant their own child audit?**
2. **What does the posture-decision evidence plan look like for
   Group 1600 xx99 to consolidate — and which children own which
   pieces of evidence?**
3. **What cross-arc handoffs must Group 1600 explicitly own vs
   delegate back to their originating arcs?** (S1504 §14.3
   SportsBettingBrief WRITE-ONLY-FORGOTTEN + S1504 §5.1
   SportsContentContextBuilder HOT-PATH-CHOKE + S1402 F.B1 revenue
   OutreachDraft delivery-MISSING + S1403 F.C4 ContentEngagement
   docstring drift — these are all Content-adjacent findings owed
   by Group 1400+1500 to Group 1600 as evidence-plan inputs.)

---

## 2. What existing inventory already tells us

Five research artifacts + one topic doc already say something
material about the Content / Deliverables / Publishing surface.
Each is cited, not restated, per playbook §7.

### 2.1 `docs/topics/content-pipeline.md` (Session 1147) — Content Deliberation v2 Pipeline

Topic doc last-reviewed for drift labeling at Session 1147
(2026-05-25). Pipeline shape (per doc §Pipeline Overview):

```
SpiderData (72h) + SignalClusters (active)
  → ClaimsPack (deterministic claim IDs)
    → ContentWriterAgent (draft citing [C-xxxxxxxxxx])
      → 3-Reviewer Panel (Skeptic + FactCheck + DomainPersona)
        → DecisionEnforcer (PUBLISH / REVISE / KILL)
          → Rewrite pass (if REVISE)
            → PublishGate (quality/novelty/structure scoring)
              → SelfBlog (with stats_snapshot['deliberation'])
```

**Drift indicator:** doc last-reviewed 2026-05-25; Rigby SIGN cycle
1 Q7 fold pattern per S1599 §10 warns that specific numbers (claim
caps, deliberation thresholds, reviewer count) may drift.

### 2.2 S1504 §14.3 CRITICAL — `SportsBettingBrief` WRITE-ONLY-FORGOTTEN pattern

`docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md`
§14.3 (S1504 close 2026-07-02):

> **CRITICAL: `SportsBettingBrief` write-only-and-forgotten.** 2
> writers (Cat D shim at `core/tasks_content.py:3150` + Session 1000
> multi-desk at `core/tasks.py:12187`), 0 readers (grep-verified
> pre-SIGN). REST endpoint `get_betting_brief` at
> `core/views_odds_sports.py:3237` (`AllowAny`) bypasses persisted
> model + calls coordinator directly. NEW pattern class for the arc.

Concrete Group 1600 evidence-plan input:
- The `SportsBettingBrief` model is a **parallel deliverable-shaped
  variant** that exists outside the Deliverable canonical container
  (per `models_unified_system.py:18394` sibling to Deliverable at
  `models_deliverables.py:84`). Whether SportsBettingBrief SHOULD
  adopt Deliverable canonical shape (integration posture) or SHOULD
  remain parallel with own contract (island posture) is a **Group
  1600 posture-decision** question, NOT a Group 1500 remediation
  question. Group 1500 T1.h R.D4 SportsBettingBrief consumer-or-
  remove is currently gated on T1.a Group 1500 posture selection;
  Group 1600 evidence may re-scope T1.h into a Group 1600 posture-
  aligned decision instead.

### 2.3 S1504 §5.1 HIGH — `SportsContentContextBuilder` HOT-PATH-CHOKE-BYPASS pattern

`docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md`
§5.1 (S1504 close 2026-07-02):

> `SportsContentContextBuilder` at `core/services/sports_content_
> context.py:27` is HOT-PATH-CHOKE-POINT for content/PA subsystem;
> BYPASSED by Cat D Discord fast path (`/odds` + digest +
> intelligence-hook all read TheOddsSpider directly). Three consumers
> marked FIRST-CLASS: content_review_panel_v2 + content_review_panel
> + unified_pa_entrypoint.

Concrete Group 1600 evidence-plan input:
- The bypass is a Content-side design question, not a Sports-side
  one: does content_review_panel_v2 canonical dispatch OWN the
  contract that all sports-content generation must route through
  `SportsContentContextBuilder`, OR is direct-to-spider access at
  Discord surface intentional for latency? Group 1500 T2.c R.SPORTS.
  DISCORD-REFACTOR is currently posture-tied to T1.a; Group 1600
  evidence may re-scope T2.c into a Group 1600 posture-aligned
  decision instead.

### 2.4 S1402 F.B1 CONFIRMED HIGH — Revenue outreach delivery ZERO outbound channel

`docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md`
§14 F.B1 (S1402 close 2026-07-01):

> **CONFIRMED HIGH: ZERO outbound channel exists.** grep-negative
> at HEAD `beda00e5` for `send_outreach|dispatch_outreach|sendgrid|
> postmark|mailgun|smtplib` (0 mainline hits, only archive/external/
> ai_core). `OutreachDraft` composition path works; delivery path
> MISSING.

Concrete Group 1600 evidence-plan input:
- `OutreachDraft` is another **parallel deliverable-shaped variant**
  (per `core/models_outreach.py:18`) with own `status` lifecycle +
  approval workflow. Whether OutreachDraft SHOULD adopt Deliverable
  canonical shape + inherit its PublishGate + delivery contract
  (integration posture) OR remain parallel (island posture) is a
  **Group 1600 posture-decision** question that affects the R.B1
  Group 1400 delivery ADR scope. If integration posture chosen at
  xx99: R.B1 becomes "Deliverable delivery contract extends to
  OutreachDraft variant"; if island posture: R.B1 remains "OutreachDraft
  own delivery contract, no shared framework."

### 2.5 S1403 F.C4 HIGH — ContentEngagement docstring drift (Group 1400)

`docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md`
§14 F.C4 (S1403 close 2026-07-01):

> **F.C4 HIGH docstring:** `ContentEngagement` docstring at
> `core/models_content_engagement.py:XX` claims "closes learning loop"
> for content consumption feedback → author-attribution — but no FK
> bridge exists (`ContentEngagement` → any AgentPerformance /
> ContentAuthor / Deliverable link). Docstring drift.

Concrete Group 1600 evidence-plan input:
- `ContentEngagement` is a fourth-axis engagement model that
  overlaps with Deliverable + SelfBlog reader-side but writer-side
  drifts from claim. Whether Group 1600 SHOULD own the "reader-
  engagement → author-attribution → learning-loop" pipeline
  (integration posture connects ContentEngagement to Deliverable +
  SelfBlog author FK; author attributes back to AgentPerformance
  via AgentMemory + AgentKnowledgeSource per Group 1300 Memory arc)
  OR whether reader-engagement remains a parallel-tracked signal
  (island posture) — is a **Group 1600 posture-decision** question.

### 2.6 S1599 §7.4 — Group 1500 NEW `docs/topics/sports-betting.md` recommendation

`docs/research/domains/sports/1599_sports_canonical_summary.md`
§7.4 recommendation (S1599 close 2026-07-02):

> NEW `docs/topics/sports-betting.md` — Group 1500 arc-close topic
> doc (analog to Group 1300 memory topic doc + Group 1400 revenue-
> pipeline topic doc; first-inventory landing per C2 cross-cutting
> criterion from §5.C). Post-arc PR; consumes P1-P6 audits + xx99
> §3.1 + §3.2 + §3.4 as source-of-truth.

Concrete Group 1600 evidence-plan input:
- Same recommendation would apply to Group 1600 arc-close (NEW
  `docs/topics/content-pipeline.md` REFRESH from Session 1147 to
  Group 1600 xx99 baseline). Group 1600 xx99 §7 anchor-update
  recommendations will include topic-doc landing per C2 cross-
  cutting criterion.

---

## 3. Candidate subdomain taxonomy

The proposed subdomain decomposition. Chris ratifies via D63-D68
lock. Six candidate categories (A-F) matching the pattern-match to
S1500 6-category shape (5 architecturally distinct pillars + 1
cross-domain integration lens as LAST child). Every category cites
runtime file:line evidence at HEAD `82e8efe6`.

### A — ClaimsPack + Content Deliberation Pipeline (v2)

**Boundary rule (F1 Rigby fold pre-lock — ClaimsPack centrality):**
Cat A owns *claims/evidence assembly + deliberation mechanics* —
pre-publication truth machinery. Cat A does NOT own publish gating
or external publish actions (those belong to Cat C). ClaimsPack is
centrally load-bearing for Content in a way it is not for Sports;
this boundary rule prevents A/B/C bleed where ClaimsPack drifts into
gate scope.

**Scope.** The v2 content generation pipeline: evidence assembly
(`ClaimsPackBuilder` at `core/services/claims_pack_builder.py:51` —
reads SpiderData 72h + SignalClusters active + DocumentEmbedding
RAG user documents; cap 20 claims sorted by freshness) →
deterministic claim ID generation (`make_claim_id` at
`core/services/content_claims.py:23` — `C-{sha256}[:10]`) → draft
generation (`ContentWriterAgent` at `core/agents/content_writer_
agent.py:100` with `_build_intelligent_system_prompt` at :281 +
`_build_content_prompt` at :1913 + 4 spider-data injection paths
per topic doc §50-59) → v2 pipeline orchestration
(`ContentDeliberationRunner` at `core/services/content_deliberation_
runner.py:21`).

**Load-bearing question owed to xx99 (D65-analog evidence plan):**
- Does the ClaimsPack claim-ID scheme actually enforce citation
  end-to-end, or does the FactCheckReviewer catch uncited claims
  post-hoc as the only enforcement layer? (Citation integrity
  posture.)
- What runs in production today? Grep of `core/celery.py` for
  content-generation beat entries returns `generate-operator-edge-
  newsletter` (Fri 06:00 Denver `content` queue) + `generate-
  outreach-drafts-daily` (07:30 Denver `content` queue,
  originating S1402/S1225 P2 revenue arc) + `cleanup-stale-content`
  (10:05 daily default queue) — NO dedicated "v2 content
  deliberation daily" beat entry. Is v2 deliberation strictly
  on-demand via ConversationOrchestrator, or is there a beat entry
  that I'm missing? (v2 pipeline runtime posture.)

**Cross-arc references.** S1502 §14.3 SignalCluster.pattern_type
gap (P11 6-arc consumer-side COMPLETED per S1599 §4.11) —
ClaimsPack reads SignalClusters filtered by `status='active'` at
`claims_pack_builder.py:76-77` but has no sports pattern_type
exposure; Group 1500 T2.a R.SPORTS.SIGNAL-ENGINE-BRIDGE is
integration-posture-gated on shim design + island-posture-gated on
sports-native aggregator design. If Group 1600 selects integration
posture (Deliverable canonical), ClaimsPack signal-consumption
extends unchanged. If island posture, ClaimsPack signal-consumption
remains as-is + parallel-sibling aggregators emit their own
deliverable variants that bypass ClaimsPack.

### B — Content Reviewers + Decision Enforcement

**Boundary rule (F8 Rigby fold — one-sentence boundary discipline):**
Cat B owns *pre-publish gating: whether the draft passes reviewer
verdicts + decision-enforcement contract*. Cat B does NOT own the
downstream quality thresholds or publish rails (Cat C) nor the
Deliverable base object model or lifecycle states (Cat D).

**Scope.** The 3-reviewer panel + decision enforcement layer:
`SkepticReviewer` (SKEPTIC_SYSTEM prompt at `core/services/content_
review_panel_v2.py:88`) + `FactCheckReviewer` (FACTCHECK_SYSTEM at
:107) + `DomainPersonaReviewer` (DOMAIN_SYSTEM_TEMPLATE at :124
— dispatched only if `confidence >= 0.2`) + `run_reviews` dispatch
function at :208 → `DecisionEnforcerAgent` at
`core/agents/decision_enforcer_agent.py:60` (PUBLISH / REVISE / KILL
verdicts extracted from `ExecutionMandate.chosen_path`; fallback
logic at `content_deliberation_runner.py:266-284` — all-PASS →
PUBLISH / any-FAIL → REVISE / default → REVISE) → single rewrite
pass (max 1 iteration at `content_deliberation_runner.py:107-116`)
→ synthetic-FAIL failure handling (invalid reviewer output or LLM
exception at `content_review_panel_v2.py:69-83, 191-192`).

**Load-bearing question owed to xx99 (D65-analog evidence plan):**
- Are reviewers pure-function (prompt-based dispatch, no class) or
  class-based? Explore Agent 1 sweep found function-based dispatch
  at `run_reviews(draft, claims_pack, topic, domain)` at :208 with
  prompt-string constants per reviewer. Is this a design choice for
  hot-swap-flexibility, or drift from an earlier class-based design
  that was refactored?
- Two content_review_panel files exist: `content_review_panel_v2.py`
  (v2 canonical) + `content_review_panel.py` (v1 legacy — instantiates
  DomainContentContextBuilder at :82-85). Which is the canonical
  runtime path? What's the migration plan? (v1-vs-v2 canonicalization
  posture.)

**Cross-arc references.** S1502 F5 fold ArbitrageOpportunity kept-as-
drift precedent (S1502 §14.4 F5 fold): parallel-model dormancy is
kept-as-drift when "reads like we meant to persist." Cat B analog:
if `content_review_panel.py` v1 legacy reads like we meant to migrate,
posture-decision-pending is the correct classification not drift.

### C — PublishGate + Publish Rails

**Boundary rule (F2 Rigby fold pre-lock — Cat C vs Cat D crisp
separation):** Cat C answers *"what happens at the boundary?"* —
gates, thresholds, eligibility, publish destinations, rails, failure
modes, post-publish correction loops (errata/retract/republish). Cat
C does NOT own the Deliverable base object model, variants, or
lifecycle states (those belong to Cat D). This rule prevents the
common scope-magnet where PublishGate becomes "just another
Deliverable stage" and drifts into Cat D scope.

**Scope.** The quality-gate + publish-rail output layer: `PublishGate`
at `core/services/publish_gate.py:27` (thresholds QUALITY_THRESHOLD
0.70, NOVELTY_THRESHOLD 0.60, STRUCTURE_THRESHOLD 0.55,
MYTHOLOGY_THRESHOLD 0.15 — all hardcoded class constants at lines
44-49) → decision paths (publish / enhance / internal_only —
operational-title bypass at :124-134) → SelfBlog persistence
(`core/models_unified_system.py:20611` with `stats_snapshot`
JSONField at :20742 populated per `content_deliberation_runner.
py:355`) → external publish rails: Discord broadcast (`core/services/
discord_notifications.py:36-47` — CHANNEL_BOARDROOM 1448819855557136595
+ CHANNEL_MARKET_ALERTS + CHANNEL_STOCK_ALERTS + CHANNEL_BLOCKCHAIN_
ALERTS + CHANNEL_PODCAST_LIBRARY + CHANNEL_STATUS + 6 more channel
constants) + Newsletter (`generate-operator-edge-newsletter` beat @
Fri 06:00 Denver `content` queue with dry_run=True default per S1228
P3) + Frontend BlogViewerPage (`frontend/src/pages/BlogViewerPage.
tsx:45` reads `/api/v1/research/self-blog/{blogId}/` + approve/publish
mutations at `blogsApi.ts:3921-3962`).

**Load-bearing question owed to xx99 (D65-analog evidence plan):**
- What actually reaches an external audience? Newsletter beat is
  dry_run=True by default (S1228 P3 comment at `celery.py:423`);
  what's the promotion path to live publishing? Grep of production
  code for `sendgrid|mailgun|postmark|smtplib` returns only auth
  email path at `core/auth_views_enhanced.py` — no content-broadcast
  outbound. Same negative pattern as S1402 F.B1 revenue outreach
  delivery ZERO outbound channel. (Publishing outbound-channel
  posture — extends S1402 F.B1 pattern to content publishing.)
- Do PublishGate thresholds match SelfBlog `publish_ready` field
  semantics at `models_unified_system.py:20708-20728`? SelfBlog
  has own quality_score + novelty_score + structure_score fields
  distinct from PublishGate.evaluate() output. Is this
  Explore-Agent-1 "PublishGate operates on SelfBlog-shaped inputs"
  reading accurate, or does PublishGate also gate other deliverable
  variants (SportsBettingBrief, BlockchainAuditBrief, etc.)?
  (Publish-gate-scope posture.)

**Cross-arc references.** S1402 F.B1 ZERO outbound channel HIGH:
verified same pattern applies to content publishing at HEAD 82e8efe6.
Whether Group 1600 xx99 §8 T-slot inherits Group 1400 R.B1 outreach
delivery ADR OR sports Group 1500 delegates T1 remediation to
Group 1600 depends on posture selection at D65-analog.

### D — Deliverable Base + Specialized Variants

**Boundary rule (F2 Rigby fold pre-lock — Cat D vs Cat C crisp
separation):** Cat D answers *"what IS the object?"* — Deliverable
base + variants + schemas + lifecycle states + identity/dedupe/merge
policy + variant typing + title/slug normalization + initiative
linking/ownership attribution. Cat D does NOT own gates or publish
rails (those belong to Cat C).

**Scope.** The persistence container layer: `Deliverable` base
model at `core/models_deliverables.py:84` (50+ fields including
`status` CharField choices draft/ready/published/archived default
ready at :353-358; `publish_intent` enum internal_only/publish_
candidate/publish_required default internal_only at :131-136 per
Rigby Session 1094 memory rule `feedback_publish_intent_enum.md`;
workspace FK at :165-173; `tags` ArrayField at :143-148;
`source_operation` FK to WorkspaceOperation at :210-217; `initiative`
FK at :176-183 Session 862; `content_format` CharField at :240-245)
+ central creation factory `deliverable_factory.py:1269` consolidating
23+ scattered `Deliverable.objects.create` calls (still 35 files
platform-wide with grep matches — factory partially adopted) + 5-gate
quality check (`DeliverableGatedError` at `deliverable_factory.py:46-74`
with reason codes gate_1_media_stub / gate_2_smoke_pattern / gate_3_min_
length / gate_4_template_leak / gate_5_no_relevance) + supporting
models (DeliverableAppend at `core/models_deliverable_appends.py:35`
per Session 1098 streaming idempotency; DeliverableExport at
`core/models_deliverables.py:474`; DeliverableEvent at :561;
ContentPacket at :617 grouping deliverables from pipeline runs).

**Parallel deliverable-shaped variants** (5): `SelfBlog` at
`core/models_unified_system.py:20611` + `OutreachDraft` at
`core/models_outreach.py:18` (Group 1400 revenue lane) + `ClosePack`
at `core/models_close_pack.py:20` (Group 1400 revenue lane) +
`SportsBettingBrief` at `core/models_unified_system.py:18394`
(Group 1500 sports lane) + `BlockchainAuditBrief` at
`core/models_unified_system.py:18435` (blockchain audit lane).

**Load-bearing question owed to xx99 (D65-analog evidence plan)
— THIS IS THE ARC HEADLINE QUESTION:** Is Deliverable a canonical
container that all content-shaped outputs SHOULD subclass/relate to
(integration posture) OR is it a base with parallel-schema-siblings
each with own PublishGate/lifecycle (island posture)? Concrete
posture evidence axes:
- **A1 Deliverable canonicalization scope** — should all 5 parallel
  variants adopt Deliverable base + `publish_intent` enum, OR should
  parallel variants remain independent with own lifecycles?
- **A2 PublishGate canonicalization scope** — should PublishGate at
  `publish_gate.py:27` be extended to gate all deliverable variants,
  OR should each variant have own quality gate (SelfBlog has one,
  Deliverable factory has 5-gate check, SportsBettingBrief has
  neither)?
- **A3 Central factory scope** — should `deliverable_factory.py:1269`
  become sole creation gateway (35→1 files with `.objects.create`),
  OR should scattered creation remain valid alternate ingestion?
- **A4 `publish_intent` enum coverage** — does the enum belong on
  Deliverable base only, or on every parallel variant?

**Cross-arc references.** S1504 §14.3 SportsBettingBrief WRITE-ONLY-
FORGOTTEN HIGH inherited. S1402 F.B1 OutreachDraft delivery MISSING
HIGH inherited. S1499 D55 (ii) Revenue Employee + Income/Jobs
Employee JobContract split precedent — whether Group 1600 selects
integration posture (Deliverable canonical) has implications for
Employee OS ownership questions.

### E — Rigby-Facing Content PA Tooling + Approval UX

**Boundary rule (F8 Rigby fold — one-sentence boundary discipline):**
Cat E owns *how Rigby + Chris interact with the content pipeline via
PA-tool actions + frontend approval mutations*. Cat E does NOT own
the underlying object model (Cat D), gate semantics (Cat C), or
reviewer verdicts (Cat B).

**Cat E feedback-hazard note (F11 Rigby fold Content-specific
divergence):** Cat E is downstream by default in the P1→P6 sequence,
but Rigby's tool-surface investigation may emit constrained
"must-have" findings that require a bounded correction pass in Cat C
or Cat D (no re-scope). If such findings surface, xx99 §5 evidence
plan records the correction; Cat B/C/D audits are NOT re-opened.

**Scope.** Rigby's PA-tool interface + operator approval UX:
`deliverable_tool` PA schema at `core/services/pa_tool_schemas.py:
3389-3460` + handler `_handle_deliverable_direct` at
`core/services/td_handlers_content.py:84` + dispatcher registration
at `core/services/tool_dispatcher.py:479` (18 supported actions:
list, detail, create, update, append, search, save, unsave, stats,
duplicates, set_status, normalize, export_pdf, bulk_archive,
link_initiative, unlink_initiative + 2 aliases per Explore Agent 2
sweep) → content_tool + blog_tool Session 1077 split (`_handle_
content_review` at :235 with actions list/stats/details/publish/
archive/complete + Session 1075 aliases approve→publish reject→
archive; `_handle_blog_direct` at :162) → newsletter_tool schema at
`pa_tool_schemas.py:3498-3550` (prepare/outline/validate/metrics/
list_issues/config/sources) → frontend approval UX at
`frontend/src/pages/BlogViewerPage.tsx:45` (approve/publish
mutations via `blogsApi.ts:3921-3962`).

**Load-bearing question owed to xx99 (D65-analog evidence plan):**
- Are the 3 Rigby-tool paths (deliverable_tool + content_tool +
  blog_tool) unified surfaces for the same underlying Deliverable
  container (integration posture) or 3 parallel PA APIs each with
  own state model (island posture)? The Session 1077 split is
  scoped ("blog_tool split from content_tool") — is this a design
  intent or drift?
- Does approve→publish mutation at `BlogViewerPage.tsx:45` actually
  set SelfBlog `publish_ready=True` + trigger downstream broadcast,
  OR does it just update a UI-visible status? What's the runtime
  contract for Chris's approval-click? (Approval-UX posture.)
- Rigby memory rules relevant:
  `feedback_deliverable_tool_use_append_for_large_payloads.md`
  (payloads >~6kB use append not update — silent fallback bug);
  `feedback_deliverable_status_via_content_complete.md` (status
  transitions go through content_tool.content_complete not
  deliverable_tool.update); `feedback_deliverable_create_defaults_
  to_completed.md` (new rows default status=completed regardless
  of explicit param). Are these known-drift patterns POSTURE-
  DECISION-PENDING or is there design intent to unify?

**Cross-arc references.** S1502 F.B2 PA registry gap 2-of-4 agents
missing HIGH — same pattern might apply here to content-tool
registry coverage. S1505 §15.5 F2 fold "no API contract source-of-
truth" HIGH structural debt — same pattern applies to deliverable_
tool + content_tool + blog_tool contract source-of-truth.

### F — Cross-Domain Integration Lens + Posture Decision Framing (LOAD-BEARING LAST CHILD)

**Scope.** The lens category (analog to Group 1500 Cat F). Consumes
P1-P5 sibling audits (S1601 Cat A + S1602 Cat B + S1603 Cat C +
S1604 Cat D + S1605 Cat E) and produces the posture-decision
evidence plan owed to xx99 (S1699) per D65-analog. Cross-domain
integration surfaces inventoried:

- **Content ↔ Signal Engine** (Cat A ClaimsPack reads SignalClusters;
  P11 6-arc consumer-side pattern COMPLETED per S1599 §4.11 shows
  sports has zero SignalCluster emit — cross-arc question: does
  Content own the "outputs emit SignalCluster" contract or is it
  domain-local?).
- **Content ↔ Sports** (S1504 §14.3 SportsBettingBrief WRITE-ONLY-
  FORGOTTEN + S1504 §5.1 SportsContentContextBuilder HOT-PATH-
  CHOKE-BYPASS + Cat D SportsBettingBrief parallel-model +
  BlockchainAuditBrief analog).
- **Content ↔ Revenue** (S1402 F.B1 OutreachDraft delivery MISSING +
  S1403 F.C4 ContentEngagement docstring drift + Cat D OutreachDraft
  + ClosePack parallel-models).
- **Content ↔ Memory** (learning-loop path — reviewer verdicts +
  PublishGate scores + author attribution → AgentPerformance →
  AgentMemory; S1300 canonical summary owes cross-arc integration
  scope).
- **Content ↔ Discord** (broadcast rails via `discord_notifications.
  py:36-47` channel constants; Cat C PublishGate outputs).
- **Content ↔ Frontend** (BlogViewerPage + ContentPage + newsletter
  frontend + deliverablesApi + blogsApi).
- **Content ↔ Employee OS** (D55 Revenue Employee + Income/Jobs
  Employee JobContract split precedent per S1499; is there a
  Content Employee analog?).

**Load-bearing deliverable owed to xx99 (D65-analog):** The
posture-decision evidence plan analog to S1506 §20.6. Structure
per S1600 §12.1 F.iii item 3:
- Integration posture success criteria (drawn from S1274 §12.3
  baseline + P1-P5 evidence). Concrete list.
- Island posture success criteria. Concrete list.
- Evidence FOR each posture drawn from child audits (cite P1-P5
  §N.M per criterion).
- Evidence AGAINST each posture drawn from child audits.
- Operational cost estimate for each posture (P1 vs P0 grade).
- Failure-modes-if-criteria-not-met table.
- F2-fold scoring rubric with PASS/PARTIAL/FAIL thresholds per
  criterion (adopted from S1506 §20.6 §F per S1599 §10.2 codify-
  ready).
- **Explicit "Chris-gated selection" tag** on the brief — xx99
  does NOT pick.

### Explicit non-candidates

- **v1 legacy Content Pipeline internals beyond identifying v1-vs-v2
  boundary.** Belongs in Cat B scope as boundary question, not a
  dedicated child. If v1 vs v2 canonicalization posture requires
  substantive investigation, escalate to Cat B follow-on.
- **Non-content Deliverable variants beyond the 5 identified
  (SelfBlog + OutreachDraft + ClosePack + SportsBettingBrief +
  BlockchainAuditBrief).** If additional parallel-model variants
  surface during Cat D audit, include; otherwise scope-bound.
- **Content Deliberation LLM provider selection.** Product decision,
  not architecture — per §7 anti-scope.
- **Deliverable schema migration proposals.** Design, not scoping —
  per §7 anti-scope.
- **PDF/DOCX/HTML export machinery internals.** deliverable_tool
  export_pdf action registered but export machinery is not a
  research-worthy question at Group 1600 scope. Deferred to
  post-arc T-slot if child evidence reveals load-bearing pattern.

---

## 4. Parent-vs-single recommendation

**Recommendation: parent-with-children arc, 6 children (A-F).**

Evidence supporting parent-with-children shape:

1. **The label carries three coordinated nouns.** "Content /
   Deliverables / Publishing" pattern-matches Groups 1300 (Memory /
   Knowledge / Embeddings), 1400 (Revenue / Outreach / Engagement),
   and 1500 (Sports / DBAO / Intelligence) — all three prior arcs
   closed successfully as parent-with-children per D57-analog.

2. **The runtime surface exceeds single-audit scope.** Inventory
   sweep at HEAD 82e8efe6 confirms: 6+ services in `core/services/`
   (`claims_pack_builder.py` + `content_deliberation_runner.py` +
   `content_review_panel_v2.py` + `content_review_panel.py` v1 +
   `publish_gate.py` + `deliverable_factory.py` + `content_scoring_
   service.py` + `sports_content_context.py` + others); 6+ models
   (Deliverable base + 5 parallel variants) + supporting models
   (DeliverableAppend + DeliverableExport + DeliverableEvent +
   ContentPacket); 4 Rigby PA-tool surfaces (deliverable_tool +
   content_tool + blog_tool + newsletter_tool); 6+ Celery beat
   entries (`generate-operator-edge-newsletter` + `generate-outreach-
   drafts-daily` + `cleanup-stale-content` + `initiative-activity-
   tick` + `cleanup-boardroom-junk` + `cleanup-junk-initiatives`);
   Frontend BlogViewerPage + ContentPage + blogsApi + deliverablesApi
   + newsletter_tool; Discord broadcast chain with 10+ channel
   constants. A single-audit shape cannot cover this depth in one
   session per playbook §17 graduation criteria (300-500 word
   Executive Summary + 20 sections × ~6 evidence anchors per section
   ≈ 120+ evidence anchors owed).

3. **The load-bearing lens question is structural, not diagnostic.**
   Cat D analog D59 "is Deliverable canonical or parallel-siblings"
   is a posture-decision framing that requires evidence from ALL 5
   child audits (Cat A pipeline generates deliverable-shaped outputs;
   Cat B reviewers gate deliverable-shaped inputs; Cat C PublishGate
   operates on SelfBlog-shaped inputs; Cat D Deliverable base +
   parallel variants; Cat E Rigby tools operate on Deliverable
   canonical) before xx99 can consolidate into a Chris-gated
   decision brief. A single audit cannot both gather evidence AND
   consolidate.

4. **Three prior arcs' cross-arc handoffs owe evidence to Group
   1600.** S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN +
   S1504 §5.1 SportsContentContextBuilder HOT-PATH-CHOKE + S1402
   F.B1 OutreachDraft delivery MISSING + S1403 F.C4 ContentEngagement
   docstring drift + S1502 §14.3 SignalCluster.pattern_type gap
   (6-arc consumer-side COMPLETED). If Group 1600 is single-audit,
   these findings' Content-owned decisions collapse into audit
   scope; the audit is forced to make posture selections without
   Chris-lock. Parent-with-children preserves Chris-lock
   discipline.

**Alternative rejected: single-audit-then-defer-crosscuts.** Would
require the single audit to defer 5+ cross-arc handoffs to post-arc
T-slots; xx99 canonical summary would not exist to consolidate
cross-cuts, forcing each T-slot into isolated ADR without
integration-view. This is the shape Group 1400 rejected via D22
Chris ratification at S1400 open.

---

## 5. Child mission sequence (Chris-locked pending — proposed D66-analog)

**Proposed sequence for Chris ratification** — analog to S1500 D57
child mission sequence. Sequential dependencies + capacity
consideration + Cat F LAST (consumes P1-P5 evidence per playbook
§14 lens-child pattern from S1500). **F3 Rigby fold pre-lock: P3↔P4
swap — Cat D moved BEFORE Cat C because PublishGate semantics depend
on "what gets gated" and variant-specific lifecycle differences.
Running Cat C without Cat D's canonical object-model decision would
force PublishGate scope conclusions to retro-edit after Cat D closes.
D66 dependency clause per fold F10: "We run Cat X before Cat Y
because Y consumes X's canonical decision."**

| Slot | Session | Category | Subdomain | Rationale (dependency-explicit per F10 fold) |
|------|---------|----------|-----------|----------------------------------------------|
| P1 | S1601 | A | ClaimsPack + Content Deliberation Pipeline (v2) | First child — pipeline is Content generation head; establishes evidence baseline for Cat B/C/D consumption. Cat A canonical decision: what claims + which sources ground the deliberation? |
| P2 | S1602 | B | Content Reviewers + Decision Enforcement | We run Cat B before Cat C because Cat C's gate semantics consume Cat B's canonical review-verdict contract. Cat B canonical decision: how do reviewer verdicts + DecisionEnforcer produce PUBLISH/REVISE/KILL? |
| **P3** | S1603 | **D** | **Deliverable Base + Specialized Variants** | **F3 Rigby fold pre-lock — moved from P4→P3.** We run Cat D before Cat C because Cat C's gate/rails semantics consume Cat D's canonical object-model decision (D65a-analog). Cat D headline decision: is Deliverable a canonical container OR a base with parallel-schema-siblings each with own PublishGate/lifecycle? |
| **P4** | S1604 | **C** | **PublishGate + Publish Rails** | **F3 Rigby fold pre-lock — moved from P3→P4.** We run Cat C after Cat D because gate semantics (D65b-analog) + lifecycle transition ownership (D65c-analog) are grounded in Cat D's canonical object-model outcome. Cat C canonical decision: is PublishGate a single canonical gate with variant/channel-specific policies OR multiple gate classes per variant/channel? |
| P5 | S1605 | E | Rigby-Facing Content PA Tooling + Approval UX | We run Cat E after Cat D + Cat C because tool-surface contract consumes canonical object-model + gate-semantic decisions. Cat E canonical decision: is Rigby's tool surface (deliverable_tool + content_tool + blog_tool + newsletter_tool) 4 parallel APIs OR 1 unified API? |
| P6 | S1606 | F | Cross-Domain Integration Lens & Posture Decision Framing | **LAST child — consumes P1-P5 evidence + produces xx99 posture-decision evidence plan per D65a/D65b/D65c-analog three-axis framing** |
| P7 | S1699 | xx99 | Canonical summary | **Consumes P1-P6 outputs + resolves contradictions + produces Chris-gated posture-decision brief per D65a/D65b/D65c (evidence-consolidation across 3 axes, NOT posture selection) + applies playbook §11.3 §10 meta-methodology (FOURTH application after S1399 first + S1499 second + S1599 third)** |

**Dependency rationale (per playbook §14 sequencing rules + F10 fold
explicit dependency clauses):**
- **P1 (Cat A) before P2 (Cat B):** reviewers consume pipeline output.
- **P2 (Cat B) before P3 (Cat D):** Cat D variant-lifecycle-state
  investigation needs Cat B's PUBLISH/REVISE/KILL verdict contract
  established.
- **P3 (Cat D) before P4 (Cat C):** F3 fold — Cat C gate/rails
  investigation needs Cat D's canonical object-model decision on
  D65a Deliverable-canonicalization.
- **P4 (Cat C) before P5 (Cat E):** Rigby tool surface + approval
  UX contract needs Cat C's gate semantics + publish rails decision
  on D65b PublishGate-canonicalization.
- **P5 (Cat E) before P6 (Cat F):** Cross-domain lens needs full
  P1-P5 evidence corpus to produce three-axis posture-decision
  evidence plan.
- **P6 (Cat F) before P7 (S1699 xx99):** xx99 consolidates the lens
  output verbatim + resolves cross-child contradictions across all
  3 axes.

**Capacity consideration.** Playbook §17 graduation criteria: each
child audit 20-section template × ~6 evidence anchors per section ≈
120+ evidence anchors per audit. Chris's ratified capacity per
session: 1 child audit + close-out. Total sessions: 7 (S1601 →
S1606 + S1699). Parallels S1500 arc's 7-session shape (S1500 open +
S1501-S1506 children + S1599 close).

---

## 6. Parked candidate issues

Issues surfaced during Phase 0 sweep that don't fit the current
child mission sequence — Chris-gated deferrals to post-arc T-slots
OR later arcs.

### 6.1 v1 vs v2 content_review_panel canonicalization (Cat B scope)

Two files exist: `content_review_panel_v2.py` (v2 canonical dispatch
function-based) + `content_review_panel.py` (v1 legacy instantiates
DomainContentContextBuilder at :82-85). Which is the canonical
runtime path? Session 1077 blog_tool split, Session 1075 approve/reject
aliases suggest active development on v2 side. Cat B scope owns the
v1-vs-v2 boundary question; parked until Cat B audit lands.

### 6.2 Newsletter dry_run=True default promotion path

`generate-operator-edge-newsletter` beat @ Fri 06:00 Denver `content`
queue with `dry_run=True` default (S1228 P3 comment at `core/celery.
py:423`). What's the operational path to promote dry_run to live?
Explore Agent 2 sweep did not identify the promotion trigger.
Parked to Cat C scope; if Cat C audit reveals no promotion path,
escalate to xx99 §5 posture-decision evidence plan §C1-analog.

### 6.3 5-gate DeliverableGatedError vs PublishGate 4-threshold canonicalization

`deliverable_factory.py:46-74` implements 5-gate check (media_stub +
smoke_pattern + min_length + template_leak + no_relevance) at
Deliverable creation time. PublishGate at `publish_gate.py:27`
implements 4-threshold check (quality + novelty + structure +
mythology) at post-content-deliberation. Are these two gate systems
canonically-related (Deliverable creation gate covers input-quality;
PublishGate covers output-quality) OR drift-related (two competing
gate systems that should merge)? Parked to Cat D scope; if Cat D
audit reveals drift, escalate to xx99 §5 A2-analog "PublishGate
canonicalization scope" evidence.

### 6.4 Content Employee analog to Revenue Employee + Income/Jobs Employee (D55)

S1499 D55 (ii) established two sibling JobContracts for Revenue arc
(Revenue Employee + Income/Jobs Employee). Is there a Content Employee
analog owed by Group 1600? Cat F scope owns as evidence-plan input;
delegate to Employee OS post-arc T-slot only if Cat F evidence
surfaces need.

### 6.5 Cross-arc SportsBettingBrief / OutreachDraft disposition ownership

Group 1500 T1.h R.D4 SportsBettingBrief consumer-or-remove is
currently posture-tied to Group 1500 T1.a. Group 1400 R.B1 OutreachDraft
delivery ADR is a T5 Group 1400 follow-on. Should Group 1600 own the
posture-aligned re-scope of these decisions (if D65-analog integration
posture selected, both become Deliverable canonical shape) OR should
they remain owned by originating arcs (S1500 T1.h and S1400 R.B1)?
Parked to Cat D scope; xx99 §9 delegated-arcs cross-links resolve
final ownership.

### 6.6 `docs/topics/content-pipeline.md` refresh vs new topic doc landing

Session 1147 topic doc last-reviewed 2026-05-25 with pointer noting
"pattern still valid; specific numbers may drift." Should Group 1600
xx99 §7.4 anchor-update recommend a REFRESH of existing topic doc
(preserves lineage) OR a NEW `docs/topics/content-domain.md` first-
inventory landing (matches Group 1300 memory + Group 1400 revenue-
pipeline + Group 1500 sports-betting pattern)? Parked to xx99 scope;
Cat F evidence plan recommendation drives.

---

## 7. Anti-scope

Bounded OUT of Group 1600 arc per Chris-gated D67-analog. **F5 Rigby
fold pre-lock: 6 additional Content-adjacent scope-magnets bounded
out explicitly (items #13-#18) to prevent scope-drag during audits.**

1. **v1 legacy Content Pipeline deep-dive.** Cat B owns the v1-vs-v2
   boundary question; anything beyond boundary belongs in post-arc
   T-slot OR later arc.

2. **Non-content-shaped Deliverable variants** (e.g., dashboard
   widgets that use Deliverable model as ephemeral container without
   Content Deliberation lineage). If discovered, delegate to
   originating domain arc.

3. **Content Deliberation LLM provider selection** — product decision,
   not architecture. Per S1500 D60 precedent for Odds API vendor
   selection.

4. **Deliverable schema migration proposals.** Scoping is not
   migration; if xx99 selects integration posture, migration planning
   is a post-arc T-slot design-preparation ADR.

5. **PDF/DOCX/HTML export machinery internals.** deliverable_tool
   `export_pdf` action registered but export machinery is not
   research-worthy at Group 1600 scope. Post-arc T-slot if child
   evidence reveals load-bearing pattern.

6. **External-publish rail Vercel/Next.js integration.** If Cat C
   audit reveals PublishGate outputs need external rendering, delegate
   to a hypothetical Group 1700 Observability/Rendering arc rather
   than adopt Vercel-specific integration in Cat C scope.

7. **Podcast library publishing pipeline** (CHANNEL_PODCAST_LIBRARY
   at `discord_notifications.py:47` Session 496). If Cat C audit
   reveals podcast-content generation is under active development,
   delegate to separate arc rather than adopt into Group 1600 scope.

8. **Content Deliberation prompt engineering.** Reviewer prompt
   templates (`content_review_panel_v2.py:88, 107, 124`) are content
   of the reviewers, not architecture. Post-arc T-slot if Cat B audit
   reveals prompt-template drift is a load-bearing pattern.

9. **Ops Autopilot content generation.** Any content-shaped outputs
   from `ops_autopilot/` services (revenue attribution, initiative
   summaries) belong in Group 1400 T5 post-arc T-slot delegation
   OR later arc, not Group 1600.

10. **Mobile-app content-viewing surface beyond web frontend.**
    Defer to relevant child if surfaces; not primary scope.

11. **External companion project scope** (`BILLING_MONETIZATION_
    SYSTEM.md` from ai-content-studio treated as design context, not
    runtime — matches S1400/S1500 precedent).

12. **Content Deliberation MYTHOLOGY threshold policy** — Session
    1003 threshold-lowering discussion at `publish_gate.py:456-462`
    is a governance-policy question, not architecture. Post-arc
    T-slot if Cat C audit reveals load-bearing drift.

13. **Content indexing / discoverability surfaces (F5 Rigby fold).**
    content_list/search/detail routes; library browsing; initiative
    linking beyond FK reference. Stealth choke-point that creates UX
    pressure to widen scope. Intentionally out; escalate to post-arc
    T-slot if Cat E audit reveals load-bearing pattern.

14. **Search/ranking + retrieval boosts (F5 Rigby fold).**
    Content discovery quality is a black hole. If Cat A audit reveals
    ClaimsPack retrieval-relevance drift affects deliberation
    outcomes, escalate to post-arc T-slot OR delegate to a Group 1700
    Observability/Retrieval arc.

15. **Permissions / roles / moderation policy (F5 Rigby fold).**
    Who can approve, publish, archive; role-based UI; admin-only
    paths. Metastasizes into a product/security project. Even if
    surfaces during Cat E audit, name it as out-of-scope unless
    already implemented and being merely inventoried.

16. **Notification fanout policy (F5 Rigby fold).**
    Discord/email/push notification strategy. Cat C owns publish
    rails contract but does NOT own notification-fanout strategy.
    Explicit anti-scope. If Cat C audit reveals notification drift,
    escalate to post-arc T-slot.

17. **Attribution + analytics instrumentation expansion (F5 Rigby
    fold).** Opens/clicks/read-time telemetry expansion. Creeps in
    under "engagement loop" (adjacent to S1403 F.C4 ContentEngagement
    finding). Explicit anti-scope beyond what Cat B/D audits reveal
    as load-bearing.

18. **Template system / formatting internals + channel integrations
    beyond current rail (F5 Rigby fold — combined per Rigby's
    response).** Markdown → HTML template system, section templates,
    newsletter formatting internals; adding NEW publish destinations
    (Substack/Beehiiv/Buttondown/etc.); template authoring OR template
    marketplace. Extends anti-scope #5 (PDF/DOCX/HTML export
    machinery). Even if integrations exist, explicit anti-scope
    "adding new publish destinations."

---

## 8. Decisions recorded (Chris-locked pending — proposed D63-D68 analog)

**Proposed D-set for Chris ratification via "agree all + D-N=(a)"
round after Rigby pre-ratification pressure-test.** Matches S1500
D56-D61 pattern. **F4 Rigby fold pre-lock: D65 split into three
orthogonal axes D65a/D65b/D65c** because a single D65 attempting to
carry container-canonicalization + gate-canonicalization + factory/
rails-canonicalization in one question makes "agree" hide
disagreement on any single axis. Split enables clean per-axis
ratification.

| D-number (proposed) | Question | Proposed answer (Chris ratifies) |
|---------------------|----------|----------------------------------|
| D63 | Domain slug | `content` |
| D64 | Arc shape | Parent-with-children (P1-P6 children + P7 xx99 at S1699) |
| **D65a** | **Load-bearing question — Deliverable canonicalization (F4 fold)** | Taxonomy + **posture decision framing + evidence plan** — "Is Deliverable the canonical content container across domains, with variants expressed as typed subkinds (or metadata), OR are variants first-class siblings with independent schemas and lifecycles?" (analog to S1500 D59; NOT posture selection at Phase 0). Binary posture framing per F9 fold — mushy hybrid disallowed unless evidence forces it. |
| **D65b** | **Load-bearing question — PublishGate canonicalization (F4 fold)** | Taxonomy + posture decision framing + evidence plan — "Is PublishGate a single canonical gate with variant/channel-specific policies, OR multiple gate classes/threshold systems per variant/channel?" NOT posture selection at Phase 0. Binary posture framing per F9 fold. |
| **D65c** | **Load-bearing question — Lifecycle transition ownership (factory/rails; F4 fold)** | Taxonomy + posture decision framing + evidence plan — "Is there a single canonical transition orchestrator (e.g., publish rails/lifecycle engine) OR do variants own their own transition rails?" NOT posture selection at Phase 0. Binary posture framing per F9 fold. |
| D66 | Child mission sequence (F3 Rigby fold P3↔P4 swap; F10 dependency-clause embedding) | P1 Cat A ClaimsPack + Content Deliberation Pipeline v2 → P2 Cat B Content Reviewers + Decision Enforcement → **P3 Cat D Deliverable Base + Specialized Variants (moved from P4 per F3 fold)** → **P4 Cat C PublishGate + Publish Rails (moved from P3 per F3 fold)** → P5 Cat E Rigby-Facing Content PA Tooling + Approval UX → P6 Cat F Cross-Domain Integration Lens & Posture Decision Framing (LAST) → P7 S1699 xx99 canonical summary (fourth application of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second + S1599 third) |
| D67 | Anti-scope + bound-outs | §7 anti-scope list (18 items after F5 fold — added #13-#18: content indexing/discoverability + search/ranking + permissions/moderation + notification fanout + attribution/analytics expansion + template system/channel integrations) including Ops Autopilot content generation, mobile-app content-viewing beyond web, external companion project scope, LLM provider selection product decision, prompt engineering as content-not-architecture, MYTHOLOGY threshold policy as governance-not-architecture, podcast library as separate arc |
| D68 | Methodology version | Phase 0 F.i/F.ii/F.iii methodology applied per playbook v3 §11.1 (promotion TRIGGERED per S1599 §12.4 discriminative-value criterion 4 of 4 evidence types satisfied); if playbook v3 not yet formally codified, methodology applied unchanged from S1400/S1500 second-and-third-trigger applications (per D58 precedent). D62 = (a) 6-sibling exemplar mini-schema propagation-upfront pattern per S1599 §10.2 codify-ready adopted at Phase 0 for all children. F8+F10 folds adopted: one-sentence boundary rule per category + D66 dependency clauses embedded in §5 table |

**Rigby pre-ratification pressure-test folds LANDED at commit-time
(pre-Chris-lock):**
- **F1 Cat A ClaimsPack boundary rule** — added explicit "Cat A owns
  claims/evidence assembly + deliberation mechanics; Cat C owns
  publish gating + external publish actions" sentence to §3 Cat A.
- **F2 Cat C vs Cat D crisp separation** — added "Cat D = what IS
  the object; Cat C = what happens at the boundary" boundary rules
  to §3 Cat C + Cat D.
- **F3 P3↔P4 swap** — Cat D moved before Cat C per Cat D's canonical
  object-model decision precedes Cat C's gate-semantic decision;
  §5 table updated with explicit dependency clauses per F10 fold.
- **F4 D65 split into D65a/D65b/D65c** — three orthogonal posture-
  decision axes (container/gate/lifecycle-orchestrator) prevent
  agree-all masking unresolved design posture on any axis.
- **F5 §7 anti-scope 6 additional items** — bounded out content
  indexing/discoverability + search/ranking + permissions/moderation
  + notification fanout + attribution/analytics expansion + template
  system/channel integrations beyond current rail.
- **F6 §12.4 discriminative-value tightening** — required
  "decision-discriminative" proof + required "disconfirming" evidence
  item added to §12.4 criterion.
- **F7 §12.5 Deliverable Lifecycle Traceability Table 12-stage
  expansion** — added normalization/canonicalization + eligibility/
  packaging-gate stages distinct from "publish" per Rigby fold.
- **F8 one-sentence boundary rule per category** — added to Cat A/B/
  C/D/E; Cat F absorbs cross-domain lens role already.
- **F9 binary posture framing with mushy-hybrid disallowed** — D65a/
  D65b/D65c each require binary integration-vs-island posture; hybrid
  disallowed unless evidence forces it.
- **F10 D66 dependency-clause embedding** — every §5 row includes
  "We run Cat X before Cat Y because Y consumes X's canonical
  decision" dependency clause.
- **F11 Cat E feedback-hazard note** — Cat E may emit constrained
  "must-have" findings requiring bounded correction in C/D; no
  re-scope of C/D audits. Added to §3 Cat E.
- **F12 ClaimsPack centrality** — F1 covers via explicit boundary
  rule (ClaimsPack not buried as sub-bullet without discipline).

---

## 9. Next step

After Chris ratifies D63-D68 via "agree all + D-N=(a)" round:

1. **Commit + PR** — this doc lands to `main` with docs cascade.
2. **S1601 Cat A opens next session** — ClaimsPack + Content
   Deliberation Pipeline v2 child audit per playbook §11.2 20-section
   template + 6-parallel-Explore-sweep per §13 + parent-Claude
   verifier-loop per §14 on load-bearing pre-Explore claims.
3. **D62 = (a) 6-sibling exemplar mini-schema propagation-upfront
   pattern applies at S1601 open** — 4-item pre-brief mini-schema per
   surface upfront so P1-P6 children apply uniformly and xx99 §5
   consolidates consistently (matches S1500 D62 pattern, promoted to
   playbook v3 §5 per S1599 §10.2 candidate).
4. **Post-arc anticipated:** ~7 sessions to close (S1601 → S1606 +
   S1699); matches S1500 7-session pace + S1400 7-session pace.

---

## 10. Phase 0 F.i — Domain Definition (Chris methodology third application 2026-07-02)

**F.i answers "what IS this domain?"** — the boundary question.
Per D58 second-application precedent (S1500 open) + D68 third-
application (this doc), methodology applied unchanged from S1400 D29
first application to preserve v3 promotion trigger integrity per
S1599 §12.4 discriminative-value criterion check (4 of 4 evidence
types satisfied → playbook v3 §11.1 promotion TRIGGERS).

### 10.1 Content is bounded by

- **Content Deliberation v2 pipeline** (`ClaimsPackBuilder` +
  `ContentWriterAgent` + 3-reviewer panel + `DecisionEnforcerAgent` +
  `PublishGate`) → **Deliverable/SelfBlog persistence** → **Publish
  rails** (Discord broadcast + Newsletter + BlogViewerPage frontend +
  Rigby PA-tool approval UX).
- **Deliverable canonical container** + 5 parallel-variant models
  (SelfBlog + OutreachDraft + ClosePack + SportsBettingBrief +
  BlockchainAuditBrief).
- **Rigby PA-tool surface** (deliverable_tool + content_tool +
  blog_tool + newsletter_tool).
- **Publishing outbound channels** (Discord + Newsletter + Frontend
  BlogViewerPage/ContentPage/newsletter frontend).

### 10.2 Content is NOT bounded by

- **Non-content Deliverable variants** (dashboard widgets, ephemeral
  containers) — belong in domain arc that created them.
- **Ops Autopilot content generation** — belongs in Group 1400
  Revenue T5 post-arc T-slot.
- **Prompt engineering as content generation** — reviewer prompt
  templates are content-of-reviewers, not architecture.
- **LLM provider selection** — product decision, not architecture.
- **Mobile-app content-viewing surface** — defer to relevant child
  audit if surfaces.
- **External companion project scope** — treated as design context
  per S1400/S1500 precedent.
- **v1 Content Pipeline internals beyond boundary identification** —
  Cat B scope owns boundary question; deeper investigation belongs
  in post-arc T-slot OR later arc.

### 10.3 Companion domains (integration surfaces, not owned by Content)

- **Signal Engine** (`SignalCluster.pattern_type` — Group 1300+ or
  Group 1700 Observability if opened; Content owns ClaimsPack signal-
  consumption contract not signal-emission).
- **Sports** (`SportsBettingBrief` + `SportsContentContextBuilder` —
  Group 1500 owns runtime; Content owns cross-arc posture-decision
  on parallel-vs-canonical container).
- **Revenue** (`OutreachDraft` + `ClosePack` + `ContentEngagement` —
  Group 1400 owns runtime; Content owns cross-arc posture-decision
  on parallel-vs-canonical container).
- **Memory** (learning-loop feedback path — Group 1300 owns; Content
  owns cross-arc integration scope IF Cat F evidence surfaces need).
- **Discord** (broadcast rails — Discord bot owns transport; Content
  owns publish-rail contract).
- **Frontend** (BlogViewerPage + ContentPage + REST endpoints — owned
  by Frontend surface OR by Content Cat E depending on posture
  selection at D65-analog).

---

## 11. Phase 0 F.ii — Existing Knowledge Inventory (Chris methodology third application 2026-07-02)

**F.ii answers "what do we already know, and what evidence
foundation does that provide?"** — the inheritance question. Per
D58 + D68 methodology, unchanged from S1400/S1500 application.

### 11.1 Inherited findings (cross-arc)

Group 1600 Cat F evidence plan will consume + resolve these findings
per playbook §14 lens-child rule:

| Source arc | Finding | Severity | Cross-arc posture-decision relevance |
|-----------|---------|----------|-------------------------------------|
| S1274 | §14 Finding #6 SignalCluster.pattern_type gap | HIGH | Content ClaimsPack consumption contract owes Cat A investigation |
| S1273 | §3.10 Sports Intelligence LIGHT | LIGHT→MODERATE (Group 1500 closed S1599) | Group 1600 receives S1504 §14.3 SportsBettingBrief cross-arc handoff for Cat D posture-decision |
| S1274 | §12.3 P1 Product/Architecture Decision Point (island vs integrated posture) | HIGH | Precedent for D65-analog framing pattern; Group 1600 D65 analog "is Deliverable canonical or parallel-siblings" is same shape |
| S1402 | §14 F.B1 Revenue outreach delivery ZERO outbound channel | HIGH | Content Cat C PublishGate + Publish Rails scope inherits pattern verification for content publishing |
| S1403 | §14 F.C4 ContentEngagement docstring drift | HIGH | Content Cat B + Cat D scope inherits "reader-engagement → author-attribution → learning-loop" investigation |
| S1502 | §14.3 SignalCluster pattern_type consumer-side gap (Cat B) | HIGH POSTURE-DECISION-PENDING | Content ClaimsPack consumption contract Cat A investigation continues cross-arc pattern |
| S1504 | §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN | CRITICAL | Cat D headline evidence for D65-analog posture-decision |
| S1504 | §5.1 SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS | HIGH | Cat B + Cat F cross-arc handoff for content-review-canonical-dispatch investigation |
| S1499 | D55 (ii) Revenue Employee + Income/Jobs Employee JobContract split | (decision) | Content Employee analog owed as Cat F evidence-plan input if surfaces |

### 11.2 F.ii does NOT try to answer

- **Whether v2 Content Deliberation pipeline supersedes v1 legacy.**
  That is Cat B audit's job (boundary question, not deep dive).
- **Whether specific PublishGate thresholds are correct.** That is
  a governance-policy question, not architecture per §12 anti-scope.
- **Whether specific Discord channel IDs are current.** That is a
  Discord bot ownership question, not Content ownership.
- **Whether specific reviewer prompt templates are effective.** That
  is content-of-reviewers, not architecture per §12 anti-scope.
- **Whether SportsBettingBrief SHOULD be integrated into Deliverable
  canonical shape.** That is Cat D + Cat F evidence-plan + xx99
  consolidation → Chris post-arc ADR. Phase 0 frames, xx99 evidences,
  Chris picks.
- **Whether OutreachDraft SHOULD be integrated into Deliverable
  canonical shape.** Same as SportsBettingBrief — Chris post-arc
  ADR path.
- **Whether ContentEngagement docstring drift is a defect or design.**
  Same — Cat B + Cat D evidence per D65-analog posture-decision plan.

---

## 12. Phase 0 F.iii — Success Criteria (Chris methodology third application 2026-07-02)

**F.iii answers "What does 'the arc closed cleanly' look like?"** —
the concrete deliverables and quality bars that xx99 must produce
before Chris ratifies arc closure per playbook §17.

Per D65-analog (proposed pending Chris ratification), Group 1600
F.iii differs from Group 1500 F.iii in one specific way: **xx99 owes
evidence-consolidated posture-decision framing + Chris-gated decision
brief on "Deliverable canonical container vs parallel-schema-siblings
each with own PublishGate/lifecycle" question, NOT posture selection.**
The rest of the F.iii shape matches S1500 (and by transitive precedent,
S1400 F.iii).

### 12.1 Arc-close deliverables (owed to xx99 canonical summary)

1. **All 6 child audits closed** with playbook §11.2 20-section
   template + all 28 canonical questions answered (cite, reference,
   or `UNKNOWN`) + Rigby SIGN-with-edits folded.

2. **Cross-cutting patterns identified** per playbook §11.3 §5 —
   findings that recur across ≥2 children with severity flag.

3. **xx99 §5 posture-decision evidence brief** — the load-bearing
   deliverable per D65-analog. Structure:
   - Integration posture success criteria (from D65-analog baseline +
     P1-P6 evidence). Concrete list.
   - Island posture success criteria. Concrete list.
   - Evidence FOR each posture drawn from child audits (cite P1-P6
     §N.M per criterion).
   - Evidence AGAINST each posture drawn from child audits.
   - Operational cost estimate for each posture (P1 vs P0 grade).
   - Failure-modes-if-criteria-not-met table per posture.
   - **F2-fold scoring rubric with PASS/PARTIAL/FAIL thresholds per
     criterion** — adopted from S1506 §20.6 §F precedent per S1599
     §10.2 codify-ready candidate.
   - **Explicit "Chris-gated selection" tag** on the brief — xx99
     does NOT pick.

4. **Consolidated domain shape map** per playbook §11.3 §2 — single
   map covering all six categories + Deliverable canonical container
   + 5 parallel-variant models + PublishGate output rail +
   Rigby PA-tool surface + Discord broadcast chain + frontend.

5. **Resolved contradictions** per playbook §11.3 §3 — where P1
   and P2 disagreed (or P4 and P5, etc.), the canonical answer +
   rationale.

6. **Anchor-update recommendations** per playbook §11.3 §5:
   - Concrete edits to `PLATFORM_INVENTORY.md` §3.N Content category
     (subdivide if warranted; refine coverage rating).
   - Concrete edits to `PLATFORM_WHAT_IT_IS.md` (Content narrative
     addition if the arc reveals canonical framing).
   - Concrete `docs/topics/content-pipeline.md` refresh OR new
     `docs/topics/content-domain.md` first-inventory landing (§6.6
     parked question resolves at xx99).
   - `ARCHITECTURE_INDEX.md` §1.N registrations for each child +
     xx99 + §3 domain map + §5 gap + §7 decision matrix + §8 timeline
     + §9 roadmap.

7. **Follow-on research queue** per playbook §11.3 §7 — post-arc
   T1-T10 unified tier structure (matching S1499 + S1599 T1-T10
   shape). Categories:
   - **T1 (highest):** post-arc ADR for D65-analog posture selection
     (Chris-gated), any P1-critical umbrella ADRs, cross-arc handoff
     ADRs (S1504 §14.3 SportsBettingBrief disposition, S1402 F.B1
     OutreachDraft delivery).
   - **T2:** design-preparation follow-ons (posture-tied).
   - **T3:** Employee OS follow-ons if the arc surfaces Content
     Employee JobContract questions (D55-analog).
   - **T4:** cleanup PRs from F1 / F4-CANDIDATE observations.
   - **T5:** optional / low-priority.

8. **Cross-arc delegation cross-links** to S1300 (Memory — learning-
   loop path) + Group 1500 (Sports — T1.h SportsBettingBrief
   disposition re-scope) + Group 1400 (Revenue — R.B1 OutreachDraft
   delivery re-scope).

9. **Change log of the arc** per playbook §11.3 §8 — which children
   shipped, in what order, what Rigby SIGN verdict, what edits
   folded.

10. **Playbook §11.3 §10 meta-methodology section** — **FOURTH
    application** of the "What This Research Taught Us About How
    to Do Research" template (after S1399 first, S1499 second,
    S1599 third). Per Chris directive S1399 close 2026-07-01, every
    xx99 carries this section. Content: 10.1 what worked, 10.2
    codify-to-playbook-v3 candidates (with §20 two-triggers threshold
    check), 10.3 anti-patterns to avoid, 10.4 playbook itself
    suggestions, 10.5 xx99 template suggestions (optional).

### 12.2 Quality bars (xx99 clean-close criteria)

Per playbook §17 graduation criteria + Group 1400 + Group 1500 arc-
close precedents:

- **No child audit ships with `UNKNOWN` on a load-bearing 28-Q
  question without a Rigby cycle.** Cheap `UNKNOWN` is allowed
  per §14 (edge cases); load-bearing `UNKNOWN` must be Rigby-
  pressure-tested.

- **All Rigby SIGN cycles folded.** No FLAG-EDIT or must-fix
  outstanding at xx99 open.

- **Zero merge-blocking drift** in autoblock-refreshed anchors
  after xx99 PR merge.

- **Docs cascade complete** per `feedback_docs_cascade_at_every_close.md`
  (build_docs_index → build_rag_corpus →
  sync_docs_index_to_documents → embed_documents --all-unembedded +
  build_docs_provenance).

- **xx99 §5 posture-decision brief has explicit "Chris-gated
  selection" tag.** No posture recommendation smuggled in via
  hedged phrasing.

### 12.3 Rigby caution folds (from anticipated pre-ratification pressure-test)

Rigby's cycle-1 cautions to fold here (anticipated per S1500 + S1400
pre-ratification pattern):

- **Caution 1 (repeatability + discriminative value for promotion):**
  xx99 §10.2 must explicitly demonstrate that the Phase 0 F.i/F.ii/
  F.iii methodology *produced discriminative value* — i.e., prevented
  a scope confusion / reduced rework / produced a cleaner close than
  a mechanical single audit would have. §12.4 defines what
  "discriminative value" looks like concrete for this arc.

- **Caution 2 (not over-loading Phase 0 with posture selection):**
  D65-analog folded. Phase 0 frames the posture question and
  specifies the evidence plan; children gather the evidence; xx99
  consolidates; Chris picks in a post-arc ADR.

- **Caution 3 (Content scope-magnet):** Anticipated Rigby caution
  analog to D60 Intelligence scope-magnet warning — Content is
  adjacent to every domain and could scope-drag to include reviewer
  prompt engineering, LLM provider selection, PublishGate threshold
  policy, etc. §7 anti-scope enumerates 12 explicit bound-outs.

### 12.4 Discriminative-value criterion for playbook v3 §11.1 promotion (fourth application)

Per Rigby SIGN cycle 1 Q7 fold precedent from S1500 §12.4 (matching
S1599 §10.2 codify): xx99 §10.2 must present concrete evidence that
the F.i/F.ii/F.iii methodology produced discriminative value for
Group 1600. Candidate evidence types (matches S1500 §12.4 four types):

- **Scope confusion prevented.** Evidence: Phase 0 §3 non-candidates
  + §7 anti-scope caught a category that a mechanical single-audit
  shape would have merged into scope (e.g., Ops Autopilot content
  generation bounded out per §7 #9; podcast library bounded out per
  §7 #7; prompt engineering bounded out per §7 #8).

- **Rework reduced.** Evidence: Phase 0 §11.4 F.ii "what F.ii does
  NOT try to answer" prevented a child from re-inventorying a
  surface xx99 would have to consolidate anyway.

- **Cleaner arc close.** Evidence: Phase 0 §12 F.iii success
  criteria matched what xx99 actually produced without post-hoc
  criteria adjustment.

- **Chris-lock efficiency.** Evidence: single "agree all + D-N=(a)"
  ratification round versus multi-round negotiation. Chris post-arc
  ratifies via same "agree all + D-6=(a)" pattern as S1500 D56-D61.

If xx99 §10.2 cannot demonstrate at least 3 of these 4 evidence
types concretely, **including at least one of (Scope confusion
prevented) OR (Cleaner arc close)** (Rigby SIGN cycle 1 Q7 fold
precedent from S1500 §12.4 — prevents promotion passing on softer
points alone), promotion should NOT trigger even if methodology was
applied unchanged.

**F6 Rigby fold pre-lock: third-application tightening to prevent
soft-pass at inventory-only bar.** At third application, the
methodology must prove it still finds sharp edges, not merely
catalogs. Group 1600 xx99 §10.2 must additionally demonstrate:

- **Required "decision-discriminative" proof (F6 fold — one
  counterfactual resolved):** xx99 evidence table must include at
  least one row shaped as "We had two plausible postures (P vs Q).
  Evidence E forced selection of P and rejection of Q." Applied to
  D65a-analog or D65b-analog or D65c-analog — one counterfactual
  minimum.
- **Required "disconfirming" evidence item (F6 fold — overturn a
  previously plausible assumption):** xx99 must show at least one
  evidence item that overturns a previously plausible assumption
  (analog to Appendix overturning Explore Agent 2 UNVERIFIED claims
  in this doc; proves method still finds sharp edges).
- **Optional micro-rule (F6 fold — one "scope confusion prevented"
  example must be specific):** If §10.2 leans on "scope confusion
  prevented," at least one example must be concrete: before/after —
  what confusion, what boundary sentence prevented it, what would
  have been rediscovered at xx99 close absent the boundary rule.

Third-application tightening prevents playbook v3 §11.1 promotion
from passing on catalog-shape evidence alone; enforces the
methodology's discriminative power at the arc-close bar.

**Note re: playbook v3 promotion status:** S1599 §12.4 discriminative-
value criterion check **already triggered** playbook v3 §11.1
template promotion per Rigby SIGN cycle 1 Q7 fold. Group 1600 is the
THIRD application under the same D58/D68 methodology-unchanged
pattern; discriminative-value criterion check at xx99 close (with
F6 fold tightening) confirms whether the third application also
produced discriminative value at the arc-close bar or whether the
pattern requires refinement.

### 12.5 Group-1600-specific F.iii artifact requirement

Per playbook precedent (S1400 §12.5 + S1500 §12.5 established this
pattern), Group 1600 F.iii carries one arc-specific concrete
deliverable:

**§12.5 artifact: Deliverable Lifecycle Traceability Table.** xx99
produces a single-row-per-lifecycle-stage table.

**F7 Rigby fold pre-lock: 12-stage lifecycle** (was 10; added
normalization/canonicalization stage + eligibility/packaging-gate
stage per Rigby's Content-specific pattern-match). Analog to S1500
§12.5 Q8 fold that added "fixture/entity identity resolution" stage
for sports; Content adds analog canonicalization + eligibility
stages:

1. Evidence assembly (Cat A ClaimsPack)
2. Draft generation (Cat A ContentWriter)
3. Review verdict (Cat B 3-reviewer panel)
4. Decision enforcement (Cat B DecisionEnforcer)
5. **NEW — Normalization / canonicalization (F7 fold):** variant
   typing (what kind of deliverable is this?) + title/slug
   normalization + initiative linking / ownership attribution +
   dedupe/merge policy ("is this the same artifact as X?"). If not
   named, resurfaces as "why do we have 3 objects that look identical
   but behave differently?"
6. **NEW — Eligibility / packaging gate (F7 fold — distinct from
   publish gate):** "Ready" content often needs metadata + formatting
   + channel packaging to become "publishable." State boundary
   "eligible_for_publish" is load-bearing even if formatting
   internals are anti-scoped.
7. Publish gate (Cat C PublishGate)
8. Persistence (Cat D — Deliverable base + variants)
9. External publish (Cat C rails — Discord broadcast + Newsletter +
   frontend BlogViewerPage)
10. Reader engagement (S1403 F.C4 ContentEngagement scope; posture-
    dependent whether owned by Cat C rail or Cat D variant lifecycle)
11. Author attribution (learning-loop preparation; posture-dependent)
12. Learning-loop feedback (S1300 Memory arc cross-arc handoff;
    posture-dependent scope)

**Post-publish correction loop (F7 fold — optional additional
consideration):** If errata / retract / republish exists anywhere
in the runtime, it's a Cat C rail concern. If Cat C evidence
surfaces load-bearing correction pattern, xx99 §12.5 table augments
with post-publish correction stage; otherwise scope-bounded.

For each stage: current owner (agent/service/model), file:line
anchor, integration-posture requirement (D65a/D65b/D65c-aligned per
axis), island-posture requirement (D65a/D65b/D65c-aligned per axis),
evidence citation from P1-P6 audits.

This table is the concrete artifact that makes the D65a/D65b/D65c-
analog three-axis posture-decision brief legible to Chris in one
view. Matches S1500 §12.5 Sports Domain Lifecycle Traceability
Table pattern extended with F7 fold's Content-specific stages 5+6.

### 12.6 What F.iii does NOT try to answer

- **Whether the arc will close cleanly.** F.iii sets the bar;
  execution against the bar is child + xx99 scope.

- **Whether posture will resolve to integration or island.** D65-
  analog routes to Chris post-arc.

- **Whether playbook v3 §11.1 promotion actually triggers.** S1599
  §12.4 already triggered; Group 1600 xx99 §10.2 confirms whether
  the pattern holds at third application.

---

## Appendix — Frontmatter provenance

**Source-of-truth chain for this doc.**

- **Playbook §11.1 template applied verbatim.** Sections §1-§9
  match template exactly (with §5 renamed "Child mission sequence"
  per S1400/S1500 precedent). §10-§12 additions per Chris's Phase 0
  F.i/F.ii/F.iii methodology directive (S1400 D29; Group 1600 D68
  applies UNCHANGED for three-triggers rule per playbook v3 §11.1
  TRIGGERED at S1599 §12.4).

- **Ratified decisions D63-D68** — Chris ratification PENDING via
  governance decision (matches S1500 governance decision
  `81d7467e-add6-420f-aee9-60b67d7867e8` pattern) — `decision_create`
  action + `decision_decide` action (approve → status acted) via
  Rigby PA tool surface on fresh S1600 arc pin
  `pa-f52acf3f8d394faa` (minted this session via
  `session_tool.create_fresh`; `tools/pa_local.sh:128` updated from
  retired Group 1500 arc pin `pa-791b3db549a64e54` to fresh S1600
  pin).

- **Runtime evidence sources.** All §2 evidence table entries + §3
  candidate subdomain taxonomy file:line cites verified against
  `main` HEAD `82e8efe6` via two parallel Explore sub-agent sweeps
  executed at S1600 open (Content Pipeline surface + Deliverables +
  Publishing surface). Every file:line cite survives a repeat grep
  at commit time. Verifier-loop pre-SIGN corrections applied per
  playbook §14 on 3 load-bearing claims:
  - PublishGate class existence + threshold constants verified at
    `core/services/publish_gate.py:27, 44-49` — Explore Agent 1
    correct, Explore Agent 2 UNVERIFIED claim overturned.
  - Discord broadcast surface verified at `core/services/discord_
    notifications.py:36-47` — CHANNEL_BOARDROOM + CHANNEL_MARKET_
    ALERTS + CHANNEL_STOCK_ALERTS + 8 additional channel constants
    confirmed; Explore Agent 2 UNVERIFIED claim overturned.
  - Content-related Celery beat entries verified at `core/celery.
    py:176, 433, 460` — `cleanup-stale-content` + `generate-operator-
    edge-newsletter` + `cleanup-junk-initiatives` confirmed; matches
    Explore Agent 2 sweep table.

- **Rigby pre-ratification pressure-test PENDING.** Fresh S1600 arc
  pin owed pressure-test round; anticipated 3-4 folds per S1500 +
  S1400 precedent.

- **Companion anchors.** Frontmatter lists 6 anchors per playbook
  §23 anchor discipline rule.

- **Verifier loop.** `pending-SIGN` — fresh SIGN isolation pin owed
  after this doc lands + Rigby pre-SIGN pressure-test round + Chris
  D-lock ratification.

- **Path B chosen at session open.** Chris typed "Let's do Group
  1600 next, I want to get all of the research done" per
  00-START-NEXT-SESSION.md line 91 next-session mission options
  (option d Group 1600 arc open per §22 default lean). Sequential
  single-arc discipline per memory rule
  `feedback_no_parallel_research_arcs.md` — Group 1500 closed at
  S1599, Group 1600 opens at S1600 clean sequential.

**Session count.** S1600 handoff numbering aligns with Chris's
arc-numbering convention: S1600 (arc open) → S1601-S1606 (P1-P6
children) → S1699 (xx99 canonical summary). S1607-S1698 skipped by
intent per arc-numbering discipline.
