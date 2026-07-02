---
title: "S1601 Group 1600 Cat A — ClaimsPack + Content Deliberation Pipeline v2 (Child Audit)"
status: active (Rigby SIGN cycle 1 SIGN-with-edits at Medium confidence 2026-07-02 on fresh isolation pin pa-9f075a024552b663; F1-F6 folds landed pre-commit; Chris ratified P1 kickoff via "Continue research group 1601" short command per playbook §21)
authority: child-audit for Category A per parent §5 D66 sequence + first child under Group 1600; applies D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront per parent D68 F8/F10 folds
category: child_audit
session: 1601
date: 2026-07-02
domain_slug: content
research_group: 1600
child_slot: P1
parent_doc: docs/research/domains/content/1600_content_domain_scoping.md
head_commit: 94292140
authors: Claude Code (Chris directed via short command "Continue research group 1601")
supersedes: none
related:
  - docs/research/domains/content/1600_content_domain_scoping.md              # parent scoping — Cat A boundary F1 fold + Q1/Q2 load-bearing questions
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                 # §11.2 20-section child template + §13 six-parallel-Explore + §14 verifier-loop + §15 SIGN
  - docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md  # first-child structural precedent under Group 1500 + D62 4-item mini-schema exemplar
  - docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md  # F.B1 delivery ZERO outbound channel pattern — inherited pattern check for content publishing (Cat C-primary but Cat A inbound)
  - docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md       # §5.1 SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS + §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN — cross-arc handoffs to Cat A investigation
  - docs/research/platform/cross_domain_integration_audit.md                   # S1274 §2 integration map baseline + P11 SignalCluster pattern_type gap precedent
  - docs/topics/content-pipeline.md                                            # Session 1147 topic doc — drift indicators + specific-numbers-may-drift label
  - docs/audit-2026/04-content-pipeline.md                                     # Apr 2026 audit — full pipeline execution chain + truth gaps
  - docs/patents/DISCLOSURE_D_CLAIMS_BASED_DELIBERATION.md                    # patent provenance for ClaimsPack architecture
  - docs/patents/DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md       # patent provenance for DecisionEnforcer (Cat B boundary — Cat A's ClaimsPack feeds this)
  - docs/PLATFORM_INVENTORY.md                                                 # runtime counts anchor
  - docs/PLATFORM_WHAT_IT_IS.md                                                # narrative anchor
scope: Cat A per parent §3 F1 fold — claims/evidence assembly + deliberation mechanics (pre-publication truth machinery). Owns ClaimsPackBuilder + content_claims module + ContentWriterAgent + ContentDeliberationRunner v2 pipeline entry + evidence_pack_builder + DeliberationSession/Turn/ContractRecord/DocVersion persistence. Does NOT own publish gating (Cat C) or Deliverable base object model (Cat D) or 3-reviewer panel prompts / DecisionEnforcer internals (Cat B).
boundary_rule: |
  Cat A owns *claims/evidence assembly + deliberation mechanics* — pre-publication truth machinery.
  Cat A does NOT own publish gating or external publish actions (Cat C).
  Cat A does NOT own Deliverable base object model, variants, or lifecycle states (Cat D).
  Cat A does NOT own the 3-reviewer panel prompts or DecisionEnforcer internals (Cat B) — Cat A exports draft + claims_pack to Cat B via `run_reviews(draft_text, claims_pack, topic, domain)` and consumes Cat B's PUBLISH/REVISE/KILL verdict via `ExecutionMandate.chosen_path`; the handoff surface is in-scope for Cat A but the verdict machinery is not.
load_bearing_questions:
  - Q1 (parent §3 Cat A "Citation integrity posture"): Does the ClaimsPack claim-ID scheme actually enforce citation end-to-end, or does the FactCheckReviewer catch uncited claims post-hoc as the only enforcement layer?
  - Q2 (parent §3 Cat A "v2 pipeline runtime posture"): What runs in production today — is the v2 pipeline strictly on-demand via ConversationOrchestrator, or is there a beat entry that has been missed?
verifier_loop: |
  Pre-Explore load-bearing claims verified via file:line direct read before firing sub-agents (2026-07-02):
    - ClaimsPackBuilder at claims_pack_builder.py:51 (confirmed)
    - make_claim_id at content_claims.py:23 returns f'C-{sha256[:10]}' (confirmed)
    - ContentDeliberationRunner at content_deliberation_runner.py:21 (confirmed; run_blog at :24; rewrite pass at :107-116; decision fallback at :266-284; citation-integrity guard at :99-103)
    - ContentWriterAgent at content_writer_agent.py:207 (confirmed via grep '^class ContentWriterAgent')
    - Zero ContentDeliberationRunner beat entries in core/celery.py (confirmed via grep 'content_deliberation|ContentDeliberationRunner|deliberation_runner' → no matches)
  Six parallel Explore sub-agents fired per playbook §13 (2026-07-02). Findings folded into §3-§20 with attribution.
  Rigby SIGN cycle 1 SIGN-with-edits at Medium confidence on fresh isolation pin pa-9f075a024552b663 (2026-07-02). Six folds landed pre-commit: F1 SelfBlog canonicalization-debt reframe; F2 silent-partial-source severity MEDIUM → HIGH; F3 RAG scope explicit cross-tenant/workspace framing; F4 RAG scope = riskiest overall Cat A finding elevation; F5 fix "ZERO writes to Cat B/C/D" Exec Summary contradiction; F6 verification-report endpoint boundary pin. See §20.5.
methodology_ratifications:
  - D63 slug=content (Chris-locked S1600)
  - D64 parent-with-children (Chris-locked S1600)
  - D65a/b/c three-axis posture-decision framing owed to xx99 (Chris-locked S1600)
  - D66 P1 S1601 = Cat A (Chris-locked S1600)
  - D67 anti-scope 18 items (Chris-locked S1600)
  - D68 methodology unchanged + D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront + F8 one-sentence boundary rule per surface + F10 dependency clauses (Chris-locked S1600)
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/topics/content-pipeline.md
---

# Session 1601 — Group 1600 Cat A: ClaimsPack + Content Deliberation Pipeline v2 (Child Audit)

> **What this doc is.** A child audit under the Group 1600
> Content / Deliverables / Publishing arc. First child (P1) per
> parent §5 D66 sequence. Applies playbook §11.2 20-section template
> to the Content Deliberation v2 pipeline's claims/evidence assembly
> layer + deliberation mechanics — pre-publication truth machinery
> only. Every load-bearing claim cites `file:line` at HEAD `94292140`
> (main branch, post-S1600 arc-open merge). Every load-bearing
> negative claim ("no beat entry", "no consumer", "no reader") is
> grep-verified with the grep pattern cited in §20.
>
> **What this doc is not.** A deep-dive on the 3-reviewer panel
> (Cat B), PublishGate thresholds (Cat C), Deliverable base object
> model (Cat D), Rigby tool-surface interactions (Cat E), or
> cross-domain integration lens (Cat F). Cat A's boundary rule per
> F1 fold: claims/evidence assembly + deliberation mechanics only.
> Handoffs to sibling children are noted at the boundary; not
> traversed.

---

## 1. Executive Summary

**Cat A is the pre-publication truth machinery of the Content
Deliberation v2 pipeline.** It owns four services (~1,043 LOC),
one dataclass module (~102 LOC), one 2,419-line agent, and four
persisted models with ZERO cross-boundary FKs:

- `ClaimsPackBuilder` (`core/services/claims_pack_builder.py:51`)
  assembles evidence from three sources (LegacySpiderData 72h +
  SignalCluster status='active' + DocumentEmbedding RAG).
- `content_claims` (`core/services/content_claims.py`) provides the
  deterministic `C-{sha256}[:10]` claim ID scheme + `ClaimsPack` /
  `SpiderClaim` dataclasses.
- `EvidencePackBuilder`
  (`core/services/evidence_pack_builder.py:19`) persists evidence
  incrementally into `DeliberationSession.evidence_pack` (schema
  `evidence-pack-v1`).
- `ContentWriterAgent`
  (`core/agents/content_writer_agent.py:207`) generates the draft
  with claim-block prompt injection.
- `ContentDeliberationRunner`
  (`core/services/content_deliberation_runner.py:21`) orchestrates
  the 9-step pipeline that hands off to Cat B (review conversation +
  DecisionEnforcer), Cat C (PublishGate), and Cat D (SelfBlog
  persistence).

Persistence layer: `DeliberationSession` (`core/models_deliberation.py:20`),
`DeliberationTurn` (:163), `ContractRecord` (:205), `DocVersion` (:237).
`ClaimsPack` and `SpiderClaim` are ephemeral dataclasses. Evidence
pack is embedded JSON in `DeliberationSession.evidence_pack` — no
separate table.

**The two parent §3 Cat A load-bearing questions — RESOLVED:**

**Q1 (Citation integrity posture) — Cat A enforces citation at the
input side, not the output side.** The pipeline has ONE citation-
integrity guardrail owned by Cat A code:
`content_deliberation_runner.py:99-103` downgrades PUBLISH → REVISE
if `claims_count == 0`. This is a binary all-or-nothing guard on
*ClaimsPack presence*, not a per-claim `[C-xxxxxxxxxx]`-in-draft
verification. No Cat A code path checks the draft text for
individual claim ID coverage before PUBLISH.

Cat B's `FactCheckReviewer` (per `docs/topics/content-pipeline.md:74`
and S1274 patent DISCLOSURE_D) is the intended per-claim citation
validator on the output side — but its enforcement is prompt-based
(LLM check), not code-enforced. **Consequence:** end-to-end citation
integrity is a two-gate policy — Cat A's `claims_count > 0` code
gate + Cat B's LLM-verified per-claim gate — with no code-level
per-claim verification in either layer. **HIGH-severity structural
observation** owed to xx99 as evidence for the D65b PublishGate-
canonicalization axis (single gate vs per-variant/channel).

**Q2 (v2 pipeline runtime posture) — Strictly on-demand.
Grep-verified via three exhaustive sweeps** (`core/celery.py`,
`core/management/commands/`, `core/consumers*.py`,
`core/services/discord_bot.py`):

- **Zero beat entries** fire `ContentDeliberationRunner.run_blog()`.
- **One REST endpoint:** `POST /api/v1/research/self-blog/generate-v2/`
  at `core/views_research_demo.py:1106-1145`.
- **One PA tool action:** `blog_tool action=generate` (no `topic`
  param → v2 path) at `core/services/td_handlers_content.py:1480-1505`.
- **One Celery task chain:** `generate_self_blog_deliberation_task`
  at `core/tasks.py:5758-5761` → `_impl_generate_self_blog_deliberation_task`
  at `core/tasks_content.py:2399-2601` (instantiates runner at :2540).
  Queue: `content`. Budget-tier 3 (deferable under pressure per
  `core/services/ops_autopilot/budget.py:1076`).
- **Zero management commands, zero WebSocket consumers, zero
  Discord bot commands** trigger v2.

Adjacent lanes that do NOT share machinery with v2 (grep-verified):
`generate-operator-edge-newsletter` beat (Friday 06:00 Denver,
`dry_run=True`) uses signal clusters + newsletter template, not
ClaimsPack. `generate-outreach-drafts-daily` beat (07:30 Denver)
uses `OpportunityDraftGenerator`, not v2. Both are Cat C/D adjacent
and outside the F1 boundary.

**Cat A's boundary is clean at the F1 fold cut-line.** Cross-boundary
handoffs are limited to three canonical surfaces (Cat B via
`run_reviews` + `ConversationOrchestrator`; Cat C via
`PublishGate.apply_to_blog`; Cat D via `SelfBlog.objects.create`)
+ three data-source reads (LegacySpiderData 72h, SignalCluster
active, DocumentEmbedding cosine). **ZERO writes to Cat B / Cat C-owned
tables; ONE write to Cat D (`SelfBlog.objects.create` at
`content_deliberation_runner.py:401`) as the persistence handoff**
(per Rigby SIGN cycle 1 F5 fold — corrected from earlier
"ZERO writes to Cat B/C/D-owned tables" phrasing which contradicted
the persistence handoff Cat A explicitly performs). ZERO FKs from
`DeliberationSession` to Cat B/C/D models (grep-verified:
`ForeignKey.*ContentReview` / `ForeignKey.*PublishGate` /
`ForeignKey.*Deliverable` in `core/models_deliberation.py` all
return no matches).

**Biggest structural gaps identified pre-SIGN (severities per
playbook §12; Rigby SIGN cycle 1 elevation folded at #2, riskiest-of-set
elevated to #1 per F2/F4 folds):**

1. **[RISKIEST — Rigby SIGN F4 fold] RAG user-document scoping is
   not workspace-enforced — cross-tenant / cross-workspace data
   exposure risk.** `_from_user_documents` at
   `claims_pack_builder.py:245` calls
   `DocumentEmbedding.cosine_similarity_search(query_vector,
   limit=10, min_similarity=0.4)` with NO explicit `user_id` or
   `workspace_id` parameter. `DocumentEmbedding.cosine_similarity_search`
   at `content/models.py:879-887` (Rigby-verified line range)
   filters `document__file_path__isnull=False` — orphan exclusion
   only. **HIGH — cross-tenant/workspace evidence leak risk**:
   pipeline could ground drafts in another workspace's / user's
   documents — security + trust failure mode. Rigby cycle 1 Q6
   named this as *the single riskiest Cat A finding*. Owed to
   xx99 D65a evidence plan; T1 R.CONTENT.RAG-SCOPE post-arc ADR.
2. **Per-claim citation-in-draft verification is absent code-side**
   — `make_claim_id` is deterministic on input; `run_blog:99-103`
   only checks non-empty ClaimsPack; Cat B FactCheckReviewer is
   LLM-based prompt check. Net: end-to-end citation integrity is
   LLM-verified, not code-enforced. **HIGH** — owed to xx99 D65b
   evidence plan; T1 R.CONTENT.CITATION-INTEGRITY post-arc ADR.
3. **[Rigby SIGN F2 fold — elevated MEDIUM → HIGH] Silent partial-
   source failure = truth/evidence integrity degradation without
   an explicit degraded-status contract.**
   `claims_pack_builder.py:70-85` swallows each of three source
   exceptions with `logger.warning` and proceeds with
   degraded/partial claims list. The Step 4b downgrade only fires
   at `claims_count == 0`. Partial-source failures (e.g.,
   SignalCluster query fails, spider data + user documents
   succeed) produce a smaller-but-nonempty ClaimsPack silently
   and pass the gate. Cat A can lose an entire evidence lane
   without any degraded-status signal to Cat B/C/D consumers.
   **HIGH** per Rigby cycle 1 Q5 rationale: "can cause materially
   incorrect outputs without visibility".
4. **RAG user-document scoping** — see #1 (top-ranked HIGH).
5. **Direct ORM reads bypass service layer** — Cat A reads
   `LegacySpiderData.objects.filter(...)` at
   `claims_pack_builder.py:117`, `SignalCluster.objects.filter(...)`
   at :192, and `DeliberationSession.objects.get(...)` at
   `content_deliberation_runner.py:343` directly rather than via
   domain service accessors. **MEDIUM** — coupling risk owed to
   xx99 D65a evidence plan.
6. **SignalCluster consumer-side `pattern_type` gap CONFIRMED for
   Cat A** — S1502 §14.3 6-arc consumer-side gap holds: `grep
   pattern_type` in `claims_pack_builder.py` returns 0 matches.
   Cat A reads `sample_signals` array + `status='active'` but
   never filters by `pattern_type`. Extends S1502 pattern to Cat A
   scope. **MEDIUM** (Rigby cycle 1 Q5 nuance: MEDIUM defensible
   if pattern_type is safety/quality-routing; could be LOW if
   analytics-only) — canonical contract gap owed to xx99 D65a
   evidence plan.
7. **`SpiderData` vs `LegacySpiderData` naming drift** — parent §3
   Cat A + topic doc reference `SpiderData`; runtime reads
   `LegacySpiderData` at `core/models_unified_system.py:3691` (~8,177
   rows). Semantically identical; naming-only drift for xx99 §7
   reconciliation. **LOW**.
8. **Rewrite pass hard-capped at 1 iter** —
   `content_deliberation_runner.py:107-116` has no configurable
   loop count; single rewrite is the entire recovery envelope. Not
   a bug — a design-envelope observation for xx99 D65c evidence
   plan (lifecycle transition ownership). **LOW/POSTURE-DECISION-PENDING**.

**HEADLINE for xx99 D65a evidence plan (Rigby SIGN F1 fold —
reframed):** Cat A writes directly to `SelfBlog.objects.create` at
`content_deliberation_runner.py:401`, NOT to
`Deliverable.objects.create` or the central `deliverable_factory`.
This is **canonicalization debt Cat A flags as D65a evidence input,
NOT proof of a deliberately-chosen island architecture.** Absent an
explicit design-decision ADR recorded elsewhere, the runtime write
is a debt/legacy integration gap; the D65a posture-decision brief
consumes this evidence but Chris/xx99 selects intent (integration
vs island) — not the runtime observation alone.

**Best next research (Cat B S1602):** inherit Cat A's claim-ID
scheme + resolve whether `FactCheckReviewer` performs per-claim
`[C-xxxxxxxxxx]` regex enforcement or LLM-verbal check. If LLM-verbal
only, the citation-integrity contract is "LLM-verified, not code-
enforced" and xx99 D65b evidence plan consumes this as a two-gate
policy observation.

---

## 2. Domain Purpose

**Q1 — What is Cat A for?** Cat A assembles the factual evidence
(ClaimsPack) that grounds Content Deliberation v2 output and runs
the deliberation orchestration through to Cat B/C/D handoff.

**Q2 — What problem does Cat A solve?** Ungrounded LLM content
generation is untrusted content. Cat A's answer: source every
factual claim to spider-collected, signal-detected, or user-uploaded
evidence; attach a deterministic 10-hex claim ID; inject the
claim block into the writer prompt; and downgrade any draft that
lacks evidence entirely. Cat A does NOT claim to verify that each
claim ID appears in the final draft — that is Cat B's job per
current design. What Cat A does provide: source-of-truth
traceability via `C-{sha256}[:10]`, evidence-pack persistence via
`DeliberationSession.evidence_pack` JSONField (schema `evidence-pack-v1`),
and orchestration of the 9-step deliberation flow.

### 2.1 Cat A contract statement (per parent F1 fold)

**Cat A owns:**

- Claims/evidence assembly — ClaimsPackBuilder + content_claims
  module + EvidencePackBuilder (write side, not the JSONField
  schema definition).
- Draft generation — ContentWriterAgent with claims-block prompt
  injection at `content_deliberation_runner.py:186-187` (via
  `ClaimsPack.to_prompt_block()`).
- Deliberation orchestration — ContentDeliberationRunner's 9-step
  pipeline including the Cat A → Cat B/C/D handoff surfaces.
- Session envelope — DeliberationSession + DeliberationTurn +
  ContractRecord + DocVersion (persistence layer for the
  deliberation record).
- Citation-integrity guardrail — Step 4b PUBLISH → REVISE downgrade
  at `content_deliberation_runner.py:99-103` if `claims_count == 0`.

**Cat A does NOT own:**

- Publish gating (Cat C — PublishGate class + thresholds).
- Deliverable base object model (Cat D — Deliverable + parallel
  variants).
- 3-reviewer panel prompts + DecisionEnforcer verdict extraction
  internals (Cat B — content_review_panel_v2 +
  decision_enforcer_agent).
- Rigby tool-surface (Cat E — deliverable_tool / content_tool /
  blog_tool / newsletter_tool).
- Cross-domain integration lens (Cat F — LAST child S1606).

---

## 3. Canonical Entry Points

**Q3 — What are the canonical entry points?** Cat A is triggered
via three surfaces + one internal dispatch. Grep-verified per §20.

### 3.1 Celery tasks (in-scope for Cat A)

| Task | Decorator | file:line | Queue | Purpose |
|---|---|---|---|---|
| `generate_self_blog_deliberation_task` | `@shared_task(bind=True, soft_time_limit=480, time_limit=540)` | `core/tasks.py:5758-5761` | `content` | Wrapper task; delegates to `_impl_generate_self_blog_deliberation_task` |
| `_impl_generate_self_blog_deliberation_task` | (private impl) | `core/tasks_content.py:2399-2601` | `content` | Instantiates `ContentDeliberationRunner()` at :2540; calls `.run_blog(topic, voice)` |

**Beat schedule entries firing v2: ZERO.** Grep verified across
`core/celery.py` for `content_deliberation`, `ContentDeliberationRunner`,
`deliberation_runner`, `claims_pack`, `content_pipeline`, `v2`,
`generate_self_blog_deliberation` — no matches other than the
`reap-zombie-work` unrelated cleanup task (`core/celery.py:587`,
targets `DeliberationSession` age-out only, does not fire runs).

**Budget policy:** `_impl_generate_self_blog_deliberation_task` is
classified as budget Tier 3 (heavy LLM consumer) at
`core/services/ops_autopilot/budget.py:1076`; deferable under
budget pressure (`DEFERABLE` frozenset) with downscope knobs
`max_reviewers` (3→1→0) and `max_topics` (3→1→0) at :1113-1116, :1139.

### 3.2 REST endpoints

| Route | View | file:line | Fires v2? |
|---|---|---|---|
| `POST /api/v1/research/self-blog/generate-v2/` | `generate_v2_blog_api()` | `core/views_research_demo.py:1106-1145` | Yes — dispatches `generate_self_blog_deliberation_task.delay()` |
| `GET /api/blog/<uuid>/deliberation/` | `blog_deliberation_detail()` | `core/views_deliberation.py:322-386` | No — read-only session detail |
| `GET /api/deliberation/sessions/` etc. | 8 read-only endpoints | `core/views_deliberation.py:51-561` | No — read-only inspection |

Grep-verified negative: no other route in `core/urls*.py` matches
`deliberation.*blog.*generate` or `blog.*generate.*deliberation`.

### 3.3 PA tools

| Tool | Action | Handler | file:line | Fires v2? |
|---|---|---|---|---|
| `blog_tool` | `generate` (no `topic` param → v2 path) | `_handle_generate_blog()` | `core/services/td_handlers_content.py:1480-1505` | Yes — dispatches `generate_self_blog_deliberation_task.delay(tone=tone)` |
| `blog_tool` | `generate` (with `topic`) | same | same | No — dispatches `generate_blog_with_topic_task.delay(topic, tone)` (v1) |
| `blog_tool` | `stats\|list\|detail\|search\|recent\|approve\|reject` | `_handle_blog_direct` | `core/services/td_handlers_content.py:162-182` | No — reads only |
| `deliverable_tool` | any action | `_handle_deliverable_direct` | `core/services/td_handlers_content.py:84-116` | No — pure CRUD |
| `content_tool` | (discontinued Session 1077 blog_tool split) | — | — | Deprecated |

### 3.4 Management commands

| Command | file:line | Fires v2? |
|---|---|---|
| `write_self_blog` | `core/management/commands/write_self_blog.py:1-100` | No — uses `ContentWriterAgent.execute()` directly (v1 path only) |

Grep-verified negative: no other command in
`core/management/commands/` matches `deliberation|claims|content_pipeline`
patterns firing v2.

### 3.5 WebSocket + Discord

Grep-verified negatives:

- `grep 'ContentDeliberationRunner|ClaimsPackBuilder' core/consumers*.py` → 0 matches.
- `grep 'ContentDeliberationRunner|ClaimsPackBuilder|run_blog' core/services/discord_bot.py` → 0 matches.
- `grep 'from core.tasks import generate_self_blog_deliberation_task' core/services/discord_bot.py` → 0 matches.

### 3.6 ConversationOrchestrator dispatch (internal to v2 pipeline)

Grep-verified: `core/conversation_orchestrator.py` does NOT
call `ContentDeliberationRunner.run_blog()`. Rather,
ContentDeliberationRunner calls `ConversationOrchestrator.generate_conversation`
at `content_deliberation_runner.py:242-259` **internally** to run
the review conversation (Cat A → Cat B handoff surface). Orchestrator
is *called by* Cat A, not the entry to Cat A.

### 3.7 Load-bearing Q2 resolution (parent §3 Cat A)

**v2 pipeline is strictly on-demand.** Three trigger surfaces (REST,
PA tool, direct `.delay()` dispatch). Zero beat automation. Zero
Discord/WebSocket triggers. Answer confirmed grep-verified across
five sweeps.

---

## 4. Major Models

**Q4 — What are the major models?** Cat A owns 4 persisted models
+ 2 non-persistent dataclasses; reads 3 external data-source
models; embeds evidence pack as JSONField.

### 4.1 `DeliberationSession` — `core/models_deliberation.py:20`

**Purpose.** Unifying envelope for the deliberation record —
groups HiveMindSession, ConceptForgeRun, and content-deliberation
agent sessions under one canonical row.

**Key fields.** UUID PK; `status` ∈ {pending/active/completed/failed};
`evidence_pack` JSONField (schema `evidence-pack-v1`); `trace`
JSONField; `parent_session` self-FK (related_name='children');
timestamps.

**Cleanup.** `reap-zombie-work` beat at `core/celery.py:587-591`
(every 15 min, `crontab(minute=15)`, `queue='default'`,
`expires=3600`); reaps `status='active'` sessions older than 60
minutes to `status='failed'`, `failure_reason_code='ZOMBIE_REAPED'`.
No age-based archival. Failed sessions persist indefinitely at DB
level.

**Cross-boundary FKs.** ZERO — grep-verified: `ForeignKey.*ContentReview`,
`ForeignKey.*PublishGate`, `ForeignKey.*Deliverable` return no
matches in `core/models_deliberation.py`.

### 4.2 `DeliberationTurn` — `core/models_deliberation.py:163`

Individual agent turn within a session. FK → `DeliberationSession`
(CASCADE, related_name='turns'). Fields: `turn_number`, `agent_name`,
`content`, `content_hash`. No independent cleanup — cascade-deleted
with parent session.

### 4.3 `ContractRecord` — `core/models_deliberation.py:205`

Persisted contract (Research / Synthesis / Execution). FK →
`DeliberationSession` (CASCADE). Field: `contract_data` JSONField.
Cascade-deleted with session.

### 4.4 `DocVersion` — `core/models_deliberation.py:237`

Version history for agent-written documents; FK →
`DeliberationSession` (SET_NULL, nullable). Fields: `doc_path`,
`version_number`, `content_snapshot`. Persists independently if
parent session deleted. `unique_together = ('doc_path', 'version_number')`.

### 4.5 Non-persistent dataclasses

| Dataclass | file:line | Purpose |
|---|---|---|
| `SpiderClaim` | `core/services/content_claims.py:30` | Single sourced claim (claim_id, claim_text, source_url, source_title, source_author, published_at, retrieved_at, spider_name, freshness_hours, evidence_excerpt, confidence, claim_type) |
| `ClaimsPack` | `core/services/content_claims.py:48` | Bundle of `SpiderClaim`s + sources list + stats dict; ephemeral; passed to writer + review panel as prompt context |

### 4.6 Read-only external data sources

| Model | file:line | App | Read pattern | Retention (Cat A view) |
|---|---|---|---|---|
| `LegacySpiderData` | `core/models_unified_system.py:3691` | `core` | `.objects.filter(created_at__gte=now-72h).order_by('-created_at')[:200]` at `claims_pack_builder.py:117` | 72h soft SLA (Cat A read window); no cleanup task; ~8,177 rows total |
| `SignalCluster` | `core/models_signal_intelligence.py:29` | `core` | `.objects.filter(status='active').order_by('-detected_at')[:50]` at `claims_pack_builder.py:192` | Managed by signal-studio; lifecycle {detecting/active/triggered/decayed/archived} |
| `DocumentEmbedding` | `content/models.py:707` | `content` | `.cosine_similarity_search(query_vector, limit=10, min_similarity=0.4)` at `claims_pack_builder.py:245` | CASCADE with parent `Document`; no independent cleanup |

### 4.7 Evidence pack persistence

`EvidencePackBuilder` at `core/services/evidence_pack_builder.py:19`
does NOT create separate DB rows. All evidence is appended to
`DeliberationSession.evidence_pack` JSONField using schema version
`evidence-pack-v1`. Methods: `init_pack` (:22), `append_source`
(:50), `append_claims` (:79), `append_contradiction` (:106),
`append_internal_refs` (:127), `append_memory_retrievals` (:149),
`finalize` (:169), singleton via `get_evidence_pack_builder()` (:183).
Total lines: 187.

### 4.8 4-item pre-brief mini-schema per model (D62 fold — D65a/b/c axes)

Per parent D68 F8/F10 folds, propagate the D62 mini-schema upfront
so all sibling P2-P6 children apply uniformly and xx99 §5
consolidates consistently. Columns aligned to Group 1600's three
posture axes (D65a container / D65b gate / D65c lifecycle).

| Model / dataclass | (a) canonical vs parallel-sibling vs shared-container (D65a) | (b) pre-publish (Cat A) vs cross-boundary vs downstream (F1) | (c) integration posture requirement (if Deliverable canonical + PublishGate canonical + single orchestrator) | (d) island posture requirement (parallel-schema-siblings + variant gates + variant rails) |
|---|---|---|---|---|
| `DeliberationSession` | content-canonical (Cat A owns) | pre-publish envelope | Under integration: session persists as-is; no new FK to Deliverable needed unless xx99 D65c decides orchestrator owns session → deliverable transition. | Under island: no change; sibling variants may spawn their own session-shaped envelopes with divergent schemas. |
| `DeliberationTurn` | content-canonical (Cat A owns) | pre-publish nested | Integration: no change. | Island: no change. |
| `ContractRecord` | content-canonical (Cat A owns) | pre-publish nested | Integration: no change; contracts remain internal to session. | Island: sibling variants may need own contract-record analog. |
| `DocVersion` | content-canonical (Cat A owns) | pre-publish nested | Integration: no change. | Island: no change. |
| `ClaimsPack` (dataclass) | content-parallel-sibling (ephemeral; passed by value) | pre-publish input | Integration: ClaimsPack flows into canonical Deliverable as structured `claims_pack` field (nested JSON) or new `DeliverableClaimsPack` row + FK. | Island: ClaimsPack remains ephemeral; parallel-sibling variants may embed different-shaped claim structures. |
| `SpiderClaim` (dataclass) | shared-container (elements within ClaimsPack) | pre-publish input | Integration: embedded in canonical Deliverable.claims_evidence (JSON array). | Island: siblings may use their own claim-shape. |
| `evidence_pack` JSONField | content-canonical (embedded in DeliberationSession) | pre-publish nested | Integration: schema `evidence-pack-v1` becomes canonical evidence-pack contract across all variant-owned sessions. | Island: siblings may define their own evidence-pack schema versions. |
| `LegacySpiderData` (read) | shared-container (data source, upstream) | pre-publish input | Not owned by Cat A; upstream Spider domain. | Same. |
| `SignalCluster` (read) | shared-container (data source, upstream) | pre-publish input | Not owned by Cat A; upstream Signal Engine. If integration selected on the signal side, ClaimsPackBuilder consumption contract may formalize as typed Protocol. | Not owned by Cat A. |
| `DocumentEmbedding` (read) | shared-container (data source, upstream) | pre-publish input | Not owned by Cat A; RAG domain. If integration selected on the RAG side, workspace_id enforcement becomes contract requirement (see §14 drift D3). | Not owned by Cat A. |

---

## 5. Major Services

**Q5 — What are the major services?**

### 5.1 Cat A service inventory

| Service | file:line | Class | Line count | Purpose |
|---|---|---|---|---|
| `ClaimsPackBuilder` | `core/services/claims_pack_builder.py:51` | `ClaimsPackBuilder` | 301 total | Assembles ClaimsPack from three sources; singleton via `get_claims_pack_builder()` at :29 |
| `ContentDeliberationRunner` | `core/services/content_deliberation_runner.py:21` | `ContentDeliberationRunner` | 453 total | Orchestrates 9-step pipeline; factory via `get_content_deliberation_runner()` at :451 |
| `content_claims` (module) | `core/services/content_claims.py` | dataclasses + helpers | 102 total | `_normalize_url` (:16), `make_claim_id` (:23), `SpiderClaim` (:30), `ClaimsPack` (:48), `.to_prompt_block()` (:58), `.to_evidence_sources()` (:70), `.to_evidence_claims()` (:90) |
| `EvidencePackBuilder` | `core/services/evidence_pack_builder.py:19` | `EvidencePackBuilder` | 187 total | Persists incrementally into `DeliberationSession.evidence_pack`; singleton via `get_evidence_pack_builder()` at :183 |
| `ContentWriterAgent` | `core/agents/content_writer_agent.py:207` | `ContentWriterAgent(BaseAgent)` | 2,419 total | Draft generation with citation prompt; REWRITE_MODE detector at :318-319 |

**Total Cat A LOC:** 3,462 (301 + 453 + 102 + 187 + 2,419).

**God-service check.** Only `content_writer_agent.py` at 2,419 lines
approaches concern but stays under the 3,000-line playbook §12
threshold. All services < 3,000. **CLEAN.**

### 5.2 ClaimsPackBuilder method inventory

| Method | file:line | Purpose |
|---|---|---|
| `get_claims_pack_builder()` | :29 | Singleton accessor |
| `_tokenize_topic(topic)` | :37 | Split topic into >3-char words (pattern from spider_intelligence.py) |
| `_matches_topic(text, tokens)` | :43 | True if text contains any topic token |
| `build(topic, max_claims=20)` | :54 | Full assembly: 3 sources → dedupe → freshness sort → cap 20 |
| `_from_spider_data(tokens, seen_urls)` | :110 | LegacySpiderData 72h read; factual/speculative claim_type by description presence |
| `_from_signal_clusters(tokens, seen_urls)` | :186 | SignalCluster status='active' read; speculative claim_type |
| `_from_user_documents(topic, seen_urls)` | :224 | DocumentEmbedding cosine search; factual claim_type |
| `_unique_sources(claims)` | :287 | Deduplicated source metadata for `ClaimsPack.sources` |

### 5.3 ContentDeliberationRunner method inventory

| Method | file:line | Purpose |
|---|---|---|
| `run_blog(topic, voice)` | :24 | Canonical 9-step orchestrator; returns `{status, selfblog_id, deliberation_session_id, decision, gate_result, summary}` |
| `_generate_draft(topic, claims_pack, voice)` | :178 | Draft via `ContentWriterAgent.execute()` + Session 1001 operational-context injection at :189-196 |
| `_run_review_conversation(draft_text, claims_pack, topic)` | :223 | Runs `content_review_panel_v2.run_reviews` then `ConversationOrchestrator.generate_conversation` for critique |
| `_extract_decision(mandate_dict, review_results)` | :266 | Extract PUBLISH/REVISE/KILL from `ExecutionMandate.chosen_path` or fallback (all PASS → PUBLISH / any FAIL → REVISE / default REVISE) |
| `_rewrite_draft(topic, draft_text, review_results, claims_pack, voice)` | :286 | One rewrite pass with `context['original_draft']` + `context['review_feedback']` (Session 1098 REWRITE_MODE detector) |
| `_append_claims_to_evidence(session_id, claims_pack)` | :338 | Append ClaimsPack sources + claims to `DeliberationSession.evidence_pack` via `EvidencePackBuilder` |
| `_save_blog(...)` | :351 | `SelfBlog.objects.create(...)` with `stats_snapshot['deliberation']` metadata (session_id, decision, claims_count, sources_count, reviewers, review_verdicts, gate_result placeholder) |
| `_sanitize_tags(tags, max_tags)` | :425 | Strip prompt-leaked (`_TAG_BLACKLIST_FRAGMENTS`), oversized (>50 char), or empty tags |
| `_run_publish_gate(blog)` | :443 | Cat A → Cat C handoff: `PublishGate().apply_to_blog(blog)` |
| `get_content_deliberation_runner()` | :451 | Factory function |

### 5.4 Dependency chain — cross-domain imports out of Cat A

| Cat A file:line | Import | Target domain | Classification |
|---|---|---|---|
| `content_deliberation_runner.py:55` | `from core.services.claims_pack_builder import get_claims_pack_builder` | Cat A | intra-Cat |
| `content_deliberation_runner.py:180` | `from core.agents.content_writer_agent import ContentWriterAgent` | Cat A | intra-Cat |
| `content_deliberation_runner.py:191` | `from core.tasks import _build_operational_context` | core.tasks (shared telemetry builder) | **cross-module (see §5.5)** |
| `content_deliberation_runner.py:225` | `from core.services.content_review_panel_v2 import run_reviews, _detect_domain` | Cat B | Cat A → Cat B handoff surface |
| `content_deliberation_runner.py:242` | `from core.conversation_orchestrator import ConversationOrchestrator` | Cat A (Cat A owns deliberation mechanics; orchestrator is Cat A-internal per parent §3 Cat A scope) | intra-Cat |
| `content_deliberation_runner.py:340` | `from core.models_deliberation import DeliberationSession` | Cat A | intra-Cat |
| `content_deliberation_runner.py:341` | `from core.services.evidence_pack_builder import get_evidence_pack_builder` | Cat A | intra-Cat |
| `content_deliberation_runner.py:356` | `from core.models_unified_system import SelfBlog` | Cat D | **Cat A → Cat D handoff (SelfBlog.objects.create; see §5.5 headline)** |
| `content_deliberation_runner.py:445` | `from core.services.publish_gate import PublishGate` | Cat C | Cat A → Cat C handoff (routine) |
| `claims_pack_builder.py:21` | `from core.services.content_claims import ClaimsPack, SpiderClaim, make_claim_id` | Cat A | intra-Cat |
| `claims_pack_builder.py:114` | `from core.models_unified_system import LegacySpiderData` | Data source (Spider domain read) | data source |
| `claims_pack_builder.py:190` | `from core.models_signal_intelligence import SignalCluster` | Data source (Signal Engine read) | data source |
| `claims_pack_builder.py:228` | `from core.services.embedding_service import get_embedding_service` | Memory / RAG utility | data source utility |
| `claims_pack_builder.py:242` | `from content.models import DocumentEmbedding` | Data source (RAG read) | data source |

### 5.5 Session 1001 operational-context injection (evidence-grounding surface)

`_generate_draft` at `content_deliberation_runner.py:189-196`:

```python
# Session 1001: Inject real operational telemetry
try:
    from core.tasks import _build_operational_context
    operational_context = _build_operational_context()
    if operational_context:
        research += f"\n\n{operational_context}"
except Exception as e:
    logger.warning(f"[Phase 4] Operational context injection failed: {e}")
```

`_build_operational_context()` at `core/tasks.py:5560` returns a
markdown block with 72h telemetry from `AgentExecution`,
`CeleryTaskEvent`, `HeartBeat`, `AgentDecisionSummary`. Intent
per SESSION_1001 handoff (2026-02-13): prevent hallucinated
operational claims by giving the writer real metrics to cite.

**Classification.** Not a boundary leak; intentional evidence-
grounding pattern extending Cat A's citation contract to runtime
telemetry alongside spider/signal/RAG evidence. Failure mode is
`logger.warning` silent-swallow (see §15.2). **Adjacent-module
dependency** (Cat A imports lazily from `core.tasks`) — worth
flagging in §16 for xx99 D65a evidence-plan review of whether
`_build_operational_context` should live in `core/services/` (Cat
A-owned) rather than `core/tasks.py` (shared).

### 5.6 4-item pre-brief mini-schema per service (D62 fold)

| Service | (a) canonical vs parallel-sibling vs shared-container (D65a) | (b) pre-publish (Cat A) vs cross-boundary vs downstream (F1) | (c) integration posture requirement | (d) island posture requirement |
|---|---|---|---|---|
| `ClaimsPackBuilder` | content-canonical (Cat A owns) | pre-publish; three-source assembly | Integration: ClaimsPack becomes canonical evidence contract across all variants (SelfBlog + OutreachDraft + SportsBettingBrief + ClosePack + BlockchainAuditBrief). Consumption contract formalizes as typed Protocol. | Island: parallel-sibling variants each build own claims-pack-analog; ClaimsPackBuilder remains SelfBlog-primary. |
| `ContentDeliberationRunner` | content-canonical (Cat A owns) | pre-publish orchestrator; 9-step pipeline | Integration: runner becomes canonical Cat A → Cat B/C/D transition orchestrator; D65c axis grounds here. | Island: siblings own own deliberation runners with variant-specific step sequences. |
| `content_claims` module | content-canonical (Cat A owns) | pre-publish shared library | Integration: `make_claim_id` becomes cross-variant canonical ID scheme. | Island: siblings may adopt own ID schemes. |
| `EvidencePackBuilder` | content-canonical (Cat A owns) | pre-publish evidence writer | Integration: `evidence-pack-v1` schema becomes canonical across all variants; migration path to `evidence-pack-v2` requires Chris-gated ADR. | Island: sibling variants may use their own evidence-pack schemas. |
| `ContentWriterAgent` | content-parallel-sibling (agent — shared across content generation paths incl. OpportunityDraftGenerator via S1402) | pre-publish draft; also used by non-v2 lanes | Integration: agent becomes canonical draft generator; all variant-owning services delegate through it. | Island: siblings may adopt own draft generators (OpportunityDraftGenerator at `ops_autopilot/outreach_generation.py:340` already does — S1402 precedent). |
| `ConversationOrchestrator` (used by Cat A) | Cat A-adjacent (deliberation mechanics per parent §3 Cat A scope) | pre-publish review conversation dispatch | Integration: canonical review-conversation entry across all variants. | Island: siblings may bypass orchestrator with variant-specific review dispatch. |

---

## 6. Major APIs and Interfaces

**Q6 — What are the major APIs?**

### 6.1 REST — 1 write + 8 read

| Endpoint | Method | file:line | Purpose | Fires v2? |
|---|---|---|---|---|
| `/api/v1/research/self-blog/generate-v2/` | POST | `core/views_research_demo.py:1106-1145` | Dispatch v2 pipeline | Yes |
| `/api/blog/<uuid>/deliberation/` | GET | `core/views_deliberation.py:322-386` | Blog's linked DeliberationSession | Read |
| `/api/deliberation/sessions/` | GET | `core/views_deliberation.py:51-90` | List sessions | Read |
| `/api/deliberation/sessions/<uuid>/` | GET | `core/views_deliberation.py:94-114` | Session detail | Read |
| `/api/deliberation/sessions/<uuid>/turns/` | GET | `core/views_deliberation.py:118-142` | Turn list | Read |
| `/api/deliberation/sessions/<uuid>/contracts/` | GET | `core/views_deliberation.py:145-170` | Contract list | Read |
| `/api/deliberation/sessions/<uuid>/evidence/` | GET | `core/views_deliberation.py:220-239` | Evidence pack | Read |
| `/api/deliberation/sessions/<uuid>/trace/` | GET | `core/views_deliberation.py:243-259` | Session trace | Read |
| `/api/deliberation/sessions/<uuid>/replay/` | GET | `core/views_deliberation.py:263-314` | Full replay | Read |
| `/api/deliberation/sessions/<uuid>/verification-report/` | GET | `core/views_deliberation.py:394-561` | Verification report — **Rigby SIGN F6 boundary caution:** if this endpoint performs substantive verification (claim/citation checks, evidence-pack schema validation) beyond presentation, its semantics remain **Cat A truth-machinery** even though implemented in views. If it is presentation-only (rendering already-persisted verification state), treat as read-side observability. Cat E S1605 should confirm boundary shape. | Read (see boundary caution) |

### 6.2 WebSocket

Grep-verified: 0 consumers reference `ContentDeliberationRunner` or
`ClaimsPackBuilder`. **Not a Cat A surface.**

### 6.3 PA tools

See §3.3. `blog_tool action=generate` (no `topic`) is the only PA
surface that fires v2. Handler at
`core/services/td_handlers_content.py:1480-1505`.

### 6.4 Discord bot commands

Grep-verified: 0 commands in `core/services/discord_bot.py` fire
v2. **Not a Cat A surface.** (Note: `/odds` and adjacent broadcast
commands are Cat C output rails, out of Cat A scope.)

### 6.5 4-item pre-brief mini-schema per external surface (D62 fold)

| Surface | (a) canonical vs parallel-sibling vs shared-container (D65a) | (b) pre-publish (Cat A) vs cross-boundary vs downstream (F1) | (c) integration posture | (d) island posture |
|---|---|---|---|---|
| `POST /api/v1/research/self-blog/generate-v2/` | canonical-Cat-A entry | pre-publish trigger | Integration: extends to accept variant-type param so canonical Deliverable branches by variant. | Island: siblings own their own generate endpoints (`generate-outreach-drafts-daily` beat + `generate_v2_sports_brief` if created). |
| `blog_tool action=generate` | canonical-Cat-A entry | pre-publish trigger | Integration: unifies with other tool surfaces (D65a canonical tool contract). | Island: parallel PA tools (deliverable_tool, content_tool, blog_tool, newsletter_tool) preserve current 4-surface split — Cat E scope. |
| `generate_self_blog_deliberation_task` Celery task | canonical-Cat-A internal | pre-publish orchestration | Integration: extends to accept `variant_type` param. | Island: siblings own their own task-shim wrappers. |
| Read endpoints (deliberation sessions) | canonical-Cat-A read surface | pre-publish observability | Integration: unified read schema across variant-owning sessions. | Island: siblings own their own read schemas. |

---

## 7. Runtime Flows

**Q9 — What are the major runtime flows?**

### 7.1 Flow A — Canonical v2 pipeline (`ContentDeliberationRunner.run_blog`)

Entry: `run_blog(topic, voice)` at `content_deliberation_runner.py:24`.

```
Step 1 — ClaimsPack build (try/except graceful)
  ├─ get_claims_pack_builder() → ClaimsPackBuilder singleton at :29
  └─ ClaimsPackBuilder.build(topic) at :54
     ├─ _from_spider_data(tokens, seen_urls) at :110
     │  └─ LegacySpiderData.objects.filter(created_at__gte=now-72h) at :117
     ├─ _from_signal_clusters(tokens, seen_urls) at :186
     │  └─ SignalCluster.objects.filter(status='active') at :192
     ├─ _from_user_documents(topic, seen_urls) at :224
     │  └─ DocumentEmbedding.cosine_similarity_search(query_vector, limit=10, min_similarity=0.4) at :245
     └─ Sort by freshness (retrieved_at desc), cap at max_claims (default 20)

Step 2 — Draft via ContentWriterAgent (with Session 1001 telemetry injection)
  ├─ _generate_draft(topic, claims_pack, voice) at :178
  ├─ Build research = ClaimsPack.to_prompt_block() at :187 (formats [C-xxxxxxxxxx] markers)
  ├─ Session 1001 operational context inject at :189-196 (silent-warn on failure)
  ├─ ContentWriterAgent.execute(task, context, scifi_context={}, spider_context={}) at :208
  │  └─ _build_intelligent_system_prompt() at content_writer_agent.py:281
  │  └─ _build_content_prompt() at :1913 (citation rules require [C-xxxxxxxxxx] markers)
  │  └─ _generate_content() at :2093 (OpenAI call)
  └─ Return (full_text, generated_content)

Step 3 — Review conversation via ConversationOrchestrator (Cat A → Cat B handoff)
  ├─ _run_review_conversation(draft_text, claims_pack, topic) at :223
  ├─ run_reviews(draft_text, claims_pack, topic, domain) at :228 → content_review_panel_v2
  │  └─ [Cat B — 3-reviewer panel: SkepticReviewer + FactCheckReviewer + DomainPersonaReviewer conditional]
  ├─ orchestrator.generate_conversation(agent1=EditorAgent, agent2=ContentStrategyAgent,
  │    topic=critique_topic, conversation_type='critique', num_turns=4) at :251-259
  │  └─ Persists DeliberationSession + Turns; runs DecisionEnforcerAgent internally (Cat B)
  └─ Return (review_results, session_id, mandate_dict)

Step 4 — Extract decision at :97 → _extract_decision at :266
  ├─ Try mandate_dict.chosen_path keyword search for PUBLISH/KILL/REVISE at :270-273
  ├─ Fallback: all-PASS → PUBLISH, any-FAIL → REVISE at :276-281
  └─ Default → REVISE at :284

━━━ Step 4b — LOAD-BEARING CITATION-INTEGRITY GUARD (Cat A's own defense) ━━━
  claims_count = len(claims_pack.claims) if claims_pack else 0    # :100
  if decision == 'PUBLISH' and claims_count == 0:                 # :101
      logger.info("[Phase 4] Downgrading PUBLISH → REVISE: no research claims backing content")
      decision = 'REVISE'                                          # :103

Step 5 — Rewrite pass (max 1 iter, REVISE-only)
  ├─ if decision == 'REVISE': at :108
  ├─ _rewrite_draft(topic, draft_text, review_results, claims_pack, voice) at :110
  │  └─ Session 1098 REWRITE_MODE detector: context['original_draft'] + context['review_feedback']
  └─ result['summary']['revisions'] = 1 if rewrite succeeds

Step 6 — Append ClaimsPack to evidence pack (if session_id and claims_pack)
  ├─ _append_claims_to_evidence(session_id, claims_pack) at :121
  ├─ session = DeliberationSession.objects.get(id=session_id) at :343
  ├─ builder.append_source(session, source) for each in claims_pack.to_evidence_sources() at :347
  └─ builder.append_claims(session, claims_pack.to_evidence_claims()) at :349

Step 7 — Save blog to SelfBlog (Cat A → Cat D handoff via model create)
  ├─ _save_blog(...) at :128 → :351
  ├─ SelfBlog.objects.create(...) at :401 with stats_snapshot['deliberation'] metadata
  └─ Return blog

Step 8 — PublishGate (only if decision == 'PUBLISH'; Cat A → Cat C handoff)
  ├─ _run_publish_gate(blog) at :140 → :443
  ├─ PublishGate().apply_to_blog(blog) at :448
  │  └─ [Cat C — QUALITY/NOVELTY/STRUCTURE/MYTHOLOGY thresholds]
  ├─ If gate.decision == 'publish': blog.status='approved', content_type='public', publish_ready=True
  └─ Else: blog.gate_notes = gate_result.notes, blog.save(update_fields=['gate_notes'])

Step 9 — Status mapping (final state)
  ├─ if result['status'] != 'published':
  │  ├─ decision == 'KILL' → status='killed'
  │  ├─ decision == 'REVISE' → status='needs_enhancement' (Session 1007 auto-revision loop)
  │  └─ else → status='draft'
  └─ Return result
```

### 7.2 Flow B — REST entry (`POST /api/v1/research/self-blog/generate-v2/`)

`generate_v2_blog_api()` at `core/views_research_demo.py:1106-1145`
dispatches `generate_self_blog_deliberation_task.delay(topic, tone)`
onto the `content` queue. Async response includes `task_id` and
2-5 min ETA message. Downstream execution follows Flow A.

### 7.3 Flow C — PA tool entry (`blog_tool action=generate`)

`_handle_generate_blog()` at `td_handlers_content.py:1480-1505`
branches on `topic` param presence:

- **No topic:** dispatch `generate_self_blog_deliberation_task.delay(tone=tone)` → Flow A (v2 path).
- **With topic:** dispatch `generate_blog_with_topic_task.delay(topic, tone)` → v1 path (not Cat A).

### 7.4 Flow D — Failure envelope

Cat A's failure handling is uniformly graceful:

- Step 1 (ClaimsPack): three source exceptions swallowed as
  `logger.warning`, pipeline continues with degraded/empty ClaimsPack.
- Step 2 (Draft): `RuntimeError` raised at `content_deliberation_runner.py:71`
  → `result['failure_reason_code'] = 'DRAFT_FAILED'` → early return.
- Step 3 (Review): panel exception swallowed at :91-94, decision
  defaults to REVISE.
- Step 4b (Citation guard): fires deterministically after Step 4.
- Step 5 (Rewrite): failure swallowed at :115-116, original draft used.
- Step 6 (Evidence append): failure swallowed at :122-123.
- Step 7 (SelfBlog save): failure logged at :133-135 → early return.
- Step 8 (PublishGate): failure swallowed at :158-159.

**Result:** the pipeline nearly always returns a `SelfBlog` row
(unless Step 2 or Step 7 hard-fails); the row's `status` reflects
the truest state achievable in the failure envelope. This is
intentional graceful-degradation per Session 964, but produces
silent-partial-failure risk flagged in §15.

---

## 8. Data Ownership and Lifecycle

**Q16-Q18 — What data does Cat A own, consume, produce?**

### 8.1 Data owned by Cat A (write side)

- `DeliberationSession` (rows created via `ConversationOrchestrator.generate_conversation` at Step 3; enriched via `EvidencePackBuilder` at Step 6).
- `DeliberationTurn` (created by orchestrator internals; Cat A instantiates via orchestrator).
- `ContractRecord` (created when Cat A's session captures Research/Synthesis/Execution contracts).
- `DocVersion` (agent-written document versions; Cat A-adjacent, sparse usage).
- `evidence_pack` JSONField (embedded in `DeliberationSession`; `evidence-pack-v1` schema).

### 8.2 Data consumed by Cat A (read side)

- `LegacySpiderData` (72h read window; `data_type` polyglot — no filter applied at Cat A read).
- `SignalCluster` (`status='active'` filter; **no `pattern_type` filter — see §14.3 drift**).
- `DocumentEmbedding` (cosine similarity search via `embedding_service`; **no workspace_id/user_id scoping enforced at Cat A read — see §14.4 drift**).

### 8.3 Data produced by Cat A (for other domains)

- `SelfBlog` row with `stats_snapshot['deliberation']` metadata
  (Cat D). Metadata contract: `{session_id, decision, claims_count,
  sources_count, reviewers, review_verdicts, gate_result}`.
  **HEADLINE for D65a evidence plan** — Cat A writes to SelfBlog
  (parallel-variant) directly, bypassing `deliverable_factory` and
  the 5-gate `DeliverableGatedError` chain (see §16).

### 8.4 Retention

| Data | Retention | Cleanup mechanism |
|---|---|---|
| `DeliberationSession` (status=active) | 60-min zombie window | `reap-zombie-work` beat at `core/celery.py:587` fires every 15 min |
| `DeliberationSession` (status=failed/completed) | Indefinite | None — no age-based archival |
| `DeliberationTurn` | Cascade with session | Cascade-deleted with parent |
| `ContractRecord` | Cascade with session | Cascade-deleted with parent |
| `DocVersion` | SET_NULL from session | Persists if session deleted |
| `LegacySpiderData` (Cat A read) | 72h soft SLA at read time | No cleanup task (verified via grep) |
| `ClaimsPack`, `SpiderClaim` | Ephemeral (in-memory) | GC on function return |

### 8.5 4-item pre-brief mini-schema per data owned (D62 fold)

| Data | (a) canonical vs parallel-sibling vs shared-container (D65a) | (b) pre-publish (Cat A) vs cross-boundary vs downstream (F1) | (c) integration posture | (d) island posture |
|---|---|---|---|---|
| `DeliberationSession` (write) | content-canonical | pre-publish; also referenced downstream via `stats_snapshot['deliberation'].session_id` | Integration: session becomes canonical envelope for all variant deliberations. | Island: sibling variants may spawn own envelope models. |
| `evidence_pack` JSONField | content-canonical (nested) | pre-publish evidence record | Integration: `evidence-pack-v1` becomes canonical schema across variants; xx99 D65c evidence for lifecycle-transition ownership. | Island: siblings may define own evidence-pack schemas. |
| `SelfBlog` (write via `SelfBlog.objects.create`) | content-parallel-sibling (D65a HEADLINE) | Cat A → Cat D boundary write | Integration: SelfBlog subclasses/relates to canonical Deliverable; `deliverable_factory` becomes mandatory path. | Island: SelfBlog remains schema-parallel to Deliverable base; scattered `.objects.create` remains valid alternate ingestion. |
| `LegacySpiderData` (read) | shared-container upstream | pre-publish input | Integration: Spider domain formalizes consumption contract as typed Protocol. | Island: current read pattern preserved. |
| `SignalCluster` (read) | shared-container upstream | pre-publish input | Integration: `pattern_type` consumer contract formalizes (S1502 §14.3 6-arc). | Island: current pattern-agnostic read preserved. |
| `DocumentEmbedding` (read) | shared-container upstream | pre-publish input | Integration: workspace_id scoping formalizes as canonical RAG contract requirement. | Island: current no-scope read preserved (accepts cross-tenant risk). |

---

## 9. Integrations With Other Domains

**Q14 + Q17 + Q18 + Q21 + Q22 — Integration map.**

### 9.1 Cat A integration summary

| Domain | Direction | Cat A anchor | Contract shape | Posture-relevance (D65a/b/c) |
|---|---|---|---|---|
| Signal Engine | inbound | `claims_pack_builder.py:192` | `SignalCluster.objects.filter(status='active').order_by('-detected_at')[:50]`; keyword match; **NO `pattern_type` filter** | D65a — S1502 §14.3 6-arc consumer-side gap CONFIRMED for Cat A |
| Memory / RAG | inbound | `claims_pack_builder.py:245` | `DocumentEmbedding.cosine_similarity_search(query_vector, limit=10, min_similarity=0.4)`; **NO workspace_id/user_id scope** | D65a — canonical contract gap; cross-tenant leak risk |
| Spider Network | inbound | `claims_pack_builder.py:117` | `LegacySpiderData.objects.filter(created_at__gte=now-72h)[:200]`; no `data_type` filter | D65a — direct ORM read; should be service-layer for canonical contract |
| Cat B (Review) | outbound | `content_deliberation_runner.py:225-259` | `run_reviews(draft_text, claims_pack, topic, domain)` + `orchestrator.generate_conversation(...)` | canonical handoff |
| Cat C (PublishGate) | outbound | `content_deliberation_runner.py:445-448` | `PublishGate().apply_to_blog(blog)` → `GateResult` dataclass | canonical handoff |
| Cat D (Deliverable) | outbound | `content_deliberation_runner.py:401` | **`SelfBlog.objects.create(...)` — NOT `Deliverable.objects.create` NOR `deliverable_factory`** | D65a HEADLINE — canonicalization-debt evidence input to Chris-gated posture-decision brief (per Rigby SIGN F1 fold; NOT proof of intentional island choice absent an explicit design ADR) |
| Cat A internal telemetry | inbound | `content_deliberation_runner.py:191` | `from core.tasks import _build_operational_context` — Session 1001 injection | adjacent-module dependency; posture-decision on relocation |
| Sports Domain | not applicable | grep-verified | 0 matches for `SportsBettingBrief\|SportsContentContextBuilder` in `claims_pack_builder.py` | intentional domain isolation |
| Revenue Domain | not applicable | grep-verified | 0 matches for `OutreachDraft\|ClosePack` in `claims_pack_builder.py` | intentional domain isolation |
| Employee OS | not applicable | grep-verified | 0 matches for `JobContract\|mission_runner` in `content_deliberation_runner.py`, `claims_pack_builder.py` | intentional decoupling |
| Memory / Learning-loop | not applicable | grep-verified | 0 matches for `AgentMemory\|AgentPerformance\|AgentLearning` in Cat A files | S1300 canonical summary owes cross-arc integration scope per parent §3 Cat F |

### 9.2 Signal Engine `pattern_type` consumer-side gap CONFIRMED

- `grep pattern_type core/services/claims_pack_builder.py` → 0 matches (Agent 4 verified).
- `SignalCluster.pattern_type` field is settable at write time
  (defined in migration 0211_session_900_signal_intelligence.py:174)
  but Cat A does not read it.
- S1502 §14.3 6-arc COMPLETED consumer-side gap extends to Cat A.
- xx99 §5 D65a evidence plan item: canonical consumption contract
  should formalize whether `pattern_type` is Cat A's required read
  field (integration posture) or ignored (island posture).

### 9.3 Cross-tenant / cross-workspace RAG data exposure risk (HIGH; Rigby-elevated riskiest finding — F3+F4 folds)

- `_from_user_documents` at `claims_pack_builder.py:245` calls
  `DocumentEmbedding.cosine_similarity_search(query_vector, limit=10,
  min_similarity=0.4)` with NO explicit `user_id` or `workspace_id`.
- `DocumentEmbedding.cosine_similarity_search` at
  `content/models.py:879-887` (Rigby-verified line range) filters
  only `document__file_path__isnull=False` (orphan-chunk exclusion).
- **Explicit risk framing (per Rigby SIGN F3 fold):** this is a
  **cross-tenant / cross-workspace data exposure risk** — the
  pipeline could ground Cat A drafts in another workspace's or
  user's documents, i.e., cite chunks from evidence that Cat A
  should not have permission to see. Security + trust failure
  mode.
- **UNKNOWN pending Cat E or Memory arc verification** (UNK-1):
  does `Document` model have a `workspace_id` FK that, if absent
  from the call, permits cross-tenant chunk return? If yes,
  HIGH-severity RAG leak. If Document is globally scoped by
  design, this remains a canonical contract that xx99 §5 D65a
  evidence plan must ratify explicitly.
- **Rigby-verdict:** **THE single riskiest Cat A finding overall**
  (SIGN cycle 1 Q6). Elevated to top of §19 T1 queue as
  R.CONTENT.RAG-SCOPE per F4 fold. Severity remains HIGH
  regardless of downstream arc-decision.

### 9.4 Employee OS decoupling

Cat A has no `JobContract` reference. Whether a Content Employee
analog to S1499 D55 (ii) Revenue Employee + Income/Jobs Employee
JobContract split is owed is a **Cat F evidence-plan question** per
parent §3 Cat F. Cat A merely records the current-state decoupling
as verified.

### 9.5 Learning-loop absence

No writes to `AgentMemory`, `AgentPerformance`, or `AgentLearning`
from Cat A. Reviewer verdicts (`stats_snapshot['deliberation'].review_verdicts`)
are persisted on the SelfBlog row but no downstream Cat A code
propagates them to a learning-loop record. Cross-arc handoff to
Group 1300 Memory owed at xx99 §9.

---

## 10. Event Flows

**Q19 + Q20 — Events emitted / owed.**

### 10.1 Events currently emitted by Cat A

Grep-verified: Cat A does NOT emit `SignalCluster`, `Signal`,
`EventBus` publish, or any pub/sub event. All Cat A output flows
via:

- SelfBlog row creation (state — not event).
- Evidence pack JSONField append (state — not event).
- Logger messages (`logger.info`, `logger.warning`) at pipeline
  step boundaries (observability; not consumed).

### 10.2 Events owed by Cat A (S1274 §6 gaps)

Per S1274 EventBus wiring-partially-adopted finding (referenced
S1273 §3.10 and Group 1500 T2.a R.SPORTS.SIGNAL-ENGINE-BRIDGE
posture-decision-pending):

- **Owed at posture selection:** if D65a integration posture
  selected, ContentDeliberationRunner may need to emit
  `deliberation.completed` (with session_id, decision, blog_id) as
  an EventBus event for Cat B/C/D/E consumers to observe. Currently
  logged only.
- **Owed at posture selection:** SelfBlog persistence may need to
  emit `content.published` for Discord broadcast rails + Newsletter
  + learning-loop. Currently direct method call chain (Cat A →
  Cat C.apply_to_blog inline).

xx99 §5 D65b evidence plan should carry the event-vs-inline-call
posture decision.

---

## 11. Existing Documentation

**Q10 — What existing documentation exists?**

### 11.1 Topic docs

- **`docs/topics/content-pipeline.md`** (Session 1147, 2026-05-25).
  Covers full 6-step v2 pipeline with claim-ID scheme,
  3-reviewer panel, DecisionEnforcer, rewrite pass, PublishGate,
  SelfBlog persistence. Last-reviewed 1147. Frontmatter warns
  "pattern still valid; specific numbers may drift." Nine numeric
  drift candidates flagged in §14.

### 11.2 Handoffs (Cat A-relevant)

| Handoff | Session | Cat A relevance |
|---|---|---|
| `SESSION_964_CONTENT_DELIBERATION_PIPELINE.md` | 964 | Foundational — introduced entire v2 pipeline; ClaimsPackBuilder + 3-reviewer panel + ContentDeliberationRunner + DecisionEnforcer integration + `stats_snapshot['deliberation']` persistence |
| `SESSION_1001_BLOG_TELEMETRY_GROUNDING.md` | 1001 | Adjacent truth-control — `_build_operational_context` injection; ContentDeliberationRunner:189-196 |
| `SESSION_1098_WRAP_CANARY_GREEN.md` | 1098 | REWRITE_MODE detector via `context['original_draft']` + `context['review_feedback']`; ContentDeliberationRunner:286 rewrite path |
| `SESSION_993_PA_CAPABILITY_GAPS.md` | 993 | Wired `blog_tool action=generate` as PA v2 trigger |
| `SESSION_997_MYTHOLOGY_PUBLISHGATE.md` | 997 | Cat C-primary; mythology score wired into pipeline (Cat A → Cat C handoff) |
| `SESSION_998_GOVERNANCE_HARDENING.md` | 998 | Cat C/D-primary; author tracking + `publish_ready` enforcement; SelfBlog fields set at all creation paths incl. deliberation |
| `SESSION_886_CONTENT_FEEDBACK_LOOP.md` | 886 | BlogPerformanceContextBuilder injects past performance into future generation (Cat A-adjacent) |
| `SESSION_891_DOMAIN_CONTENT_CONTEXT.md` | 891 | Domain context auto-detection; Session 1103 suppresses when evidence present (Cat A-adjacent) |
| `SESSION_1002_SPIDER_CONTEXT_FABRICATION_FIX.md` | 1002 | Closes URL inversion path (Cat A adjacent to writer fabrication defense) |

### 11.3 Prior research library

- **`docs/audit-2026/04-content-pipeline.md`** (2026-04-06) — Full
  pipeline execution chain documented with stage-by-stage breakdown.
  §4 "Execution Chain — The v2 Deliberation Pipeline" (lines 35-131)
  details STAGE 1 (claims assembly) through STAGE 6 (PublishGate).
  §8 failure modes note "Empty ClaimsPack → publish without evidence"
  with mitigation ("Decision enforcer: PUBLISH + 0 claims → REVISE").
  §10 truth gap: reviewer verdicts not stored in
  `DeliberationSession` metadata at time of audit (pre-S1598/S1599
  evidence-capture fix). Maturity verdict "WORKING (On-Demand)".
- **`docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md`**
  — ContentWriterAgent used in `OpportunityDraftGenerator`
  (`core/services/ops_autopilot/outreach_generation.py:340`)
  single-shot LLM composition; does NOT use v2 pipeline. Represents
  alternative content-generation path that bypasses Cat A per
  intent.
- **`docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md`
  §5.1 SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS** —
  Discord fast path bypasses SportsContentContextBuilder; blog slow
  path uses it via DomainContentContextBuilder → content_review_panel_v2
  → PA lazy-load. Extends S1274 finding of disconnected content-generation
  surfaces. **Not owned by Cat A** but noted for Cat F evidence
  plan.
- **`docs/research/platform_architecture_inventory.md`** — Cat A
  covered under §3.14 Content / Deliberation Pipeline (coverage
  MODERATE, maturity WORKING for deliberation; PARTIAL for delivery
  + enhancement seam).

### 11.4 Patents

- **`docs/patents/DISCLOSURE_D_CLAIMS_BASED_DELIBERATION.md`** —
  Load-bearing patent claim: "A 9-step content deliberation pipeline
  that (1) assembles deterministic evidence claims (`C-{sha256(url+title)[:10]}`)
  from 3 source tiers, (2) enforces citation during generation via
  inline `[C-xxxxxxxxxx]` markers with explicit citation rules,
  (3) validates through 3 structurally independent reviewers
  (skeptic/fact-check/domain), (4) handles reviewer failures with
  synthetic FAIL verdicts, and (5) blocks publication without
  citations (`claims_count > 0`)." Direct patent provenance for
  Cat A architecture.
- **`docs/patents/DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md`**
  — Cat B-primary (DecisionEnforcer forces PUBLISH/REVISE/KILL);
  Cat A integration point is Step 4 of the 9-step pipeline.
- **`docs/patents/EXECUTIVE_SUMMARY_WS2.md`** — Cat A differentiator:
  "Pre-generation citation injection (not post-hoc fact-checking) +
  synthetic failure verdicts (never skip a review) + two-gate
  publication (reviewers AND evidence)."

### 11.5 Narrative docs

- **`docs/narratives/CONTENT_PIPELINE.md`** (Session 1158,
  2026-05-25) — Living narrative documenting 6-step pipeline +
  milestone timeline. Session 964 = full v2 introduction; Session
  988 = LLM Provider Registry migration; Sessions 990/1001/1002/1103
  = truth controls; Sessions 997/1000C = PublishGate hardening +
  automation.

---

## 12. Research Coverage

**Q13 — Research coverage classification.** Per playbook §12:

- **NONE:** no meaningful docs beyond code/comments.
- **LIGHT:** brief mention in one doc.
- **MODERATE:** covered but with gaps.
- **HEAVY:** thoroughly documented but not yet canonical.
- **CANONICAL:** authoritative + reference-quality.

**Cat A verdict: HEAVY approaching CANONICAL for the Cat A scope
alone.**

**Evidence:**

- Topic doc (`content-pipeline.md`) covers all 6 pipeline steps
  with drift-labeled numeric constants.
- 6 Cat-A-relevant handoffs (964, 1001, 1098, 993, 997, 998) +
  4 adjacent (886, 891, 1002, 1103).
- 2 patents (Disclosure D + F, plus WS2 summary) directly cite
  Cat A architecture.
- 1 prior audit (`04-content-pipeline.md`, Apr 2026) with runtime
  evidence + failure modes + truth gaps.
- 1 narrative doc (Session 1158 living) with milestone timeline.
- Prior research artifacts cite Cat A patterns (S1402 revenue
  audit references ContentWriterAgent; S1504 sports audit
  identifies Cat A boundary).

**Coverage gaps** (narrow design questions, not missing docs):

- No runtime cost-per-blog-pipeline-run telemetry aggregation.
- No cross-reviewer agreement metrics published post-S1598/S1599
  evidence-capture fix.
- No workspace-scoping formalization on RAG source.
- No pattern_type consumer contract formalization on SignalCluster
  source.
- No canonical evidence-pack schema versioning ADR.

---

## 13. Architecture Maturity

**Q12 — Architecture maturity classification.** Per playbook §12:

- **EXPERIMENTAL / PARTIAL / WORKING / STABLE / CANONICAL.**

| Cat A surface | Maturity | Evidence |
|---|---|---|
| `ClaimsPackBuilder` | **WORKING** | 301-line service, 7 methods, singleton pattern, test coverage in `test_phase4_content_deliberation.py`; no known runtime failures at HEAD; sources 3-source assembly |
| `content_claims` module | **STABLE** | 102-line dataclass module; `make_claim_id` deterministic; patent-referenced (Disclosure D); low churn since Session 964 |
| `EvidencePackBuilder` | **STABLE** | 187-line service; schema `evidence-pack-v1` established; no known runtime failures |
| `ContentWriterAgent` | **WORKING** (approaching STABLE) | 2,419-line agent; multi-mode (base / rewrite / diagnostic / directed); Session 1098 REWRITE_MODE detector + Session 1103 evidence-first override; test coverage in `test_content_deliberation_rewrite_context.py` + `test_priority_enforcement.py`; largest Cat A component but well-factored |
| `ContentDeliberationRunner` | **WORKING** | 453-line orchestrator; 9-step pipeline; graceful failure envelope at every step; single beat entry pending (currently on-demand only per Q2 resolution) |
| Persistence layer (DeliberationSession + 3 kin) | **STABLE** | 4 models with clean FK graph; zombie reap policy; embedded evidence pack |

**Overall Cat A maturity: WORKING** (production-serving, no known
CRITICAL defects, five identified structural gaps at MEDIUM-HIGH
severity per §15 that constrain elevation to STABLE).

---

## 14. Known Drift

**Q27 — What is drift?** Documented vs code deltas.

### 14.1 `SpiderData` vs `LegacySpiderData` naming (LOW)

- **Doc claim** (parent §3 Cat A line 366): "reads SpiderData 72h".
- **Doc claim** (topic doc line 27): "SpiderData (72h)".
- **Runtime** (`claims_pack_builder.py:9, 114-117`): reads
  `LegacySpiderData` from `core.models_unified_system:3691`.
- **Drift class:** naming-only; semantically identical (`SpiderData`
  is the historical alias for `LegacySpiderData` per S1148 rename
  arc).
- **Severity:** LOW.
- **Remediation:** xx99 §7 anchor-update to reconcile
  `PLATFORM_INVENTORY.md` + `content-pipeline.md` topic doc + parent
  §3 Cat A to canonical `LegacySpiderData` name.

### 14.2 ContentDeliberationRunner module docstring boundary drift (LOW)

- **Doc claim** (`content_deliberation_runner.py:1-13` module
  docstring): "Full pipeline: Spider signals → ClaimsPack →
  ContentWriter draft → 3-reviewer panel → DecisionEnforcer →
  PublishGate → SelfBlog with stats_snapshot['deliberation']".
- **F1 fold** (parent §3 Cat A): Cat A does NOT own PublishGate;
  that belongs to Cat C.
- **Runtime:** Cat A code (Step 8 at :138-159) invokes PublishGate
  as a boundary handoff, not as owned machinery. Docstring frames
  Cat C machinery as if Cat A-owned.
- **Severity:** LOW (boundary-language drift; runtime behavior is
  correct).
- **Remediation:** at post-arc T-slot (not this session per
  playbook §14 no-implementation rule), update module docstring to
  reflect F1 fold boundary language.

### 14.3 SignalCluster `pattern_type` consumer-side gap (MEDIUM)

- **Doc claim** (parent §3 Cat A + S1502 §14.3): SignalCluster is a
  Cat A consumption surface.
- **Runtime** (`claims_pack_builder.py:186-222`):
  `SignalCluster.objects.filter(status='active')` + keyword match;
  **`grep pattern_type claims_pack_builder.py` → 0 matches.**
- **Drift class:** consumer-side canonical contract gap; S1502
  §14.3 6-arc COMPLETED pattern extends to Cat A.
- **Severity:** MEDIUM.
- **Remediation:** xx99 §5 D65a evidence plan item — canonical
  consumption contract on SignalCluster.pattern_type ratified at
  post-arc ADR.

### 14.4 DocumentEmbedding RAG scoping absence — cross-tenant/workspace data exposure risk (HIGH; Rigby F3+F4 folds)

- **Doc claim** (parent §3 Cat A): "DocumentEmbedding RAG user
  documents" implies per-user scoping.
- **Runtime** (`claims_pack_builder.py:245`): calls
  `DocumentEmbedding.cosine_similarity_search(query_vector,
  limit=10, min_similarity=0.4)` with NO `user_id` or `workspace_id`.
- **`DocumentEmbedding.cosine_similarity_search`** at
  `content/models.py:879-887` (Rigby-verified): filters only
  `document__file_path__isnull=False` (orphan exclusion).
- **Drift class:** canonical scoping-contract gap; **cross-tenant /
  cross-workspace data exposure risk** — Cat A can ground drafts
  in evidence Cat A should not have permission to see.
- **Severity:** HIGH regardless of downstream Document workspace
  FK verification. Rigby SIGN cycle 1 Q6: THE single riskiest
  Cat A finding overall.
- **Remediation:** xx99 §5 D65a evidence plan item; T1
  R.CONTENT.RAG-SCOPE post-arc ADR (top of §19 queue). Pre-xx99:
  Cat E S1605 or Memory arc S1300-adjacent may verify Document
  schema (UNK-1). If Document has workspace FK and current absence
  is intentional (e.g., document-level enforcement in cosine
  search), scope-contract must be formalized as canonical.

### 14.5 v2 pipeline runtime posture drift (LOW-INFO)

- **Doc claim** (some prior handoff phrasings): v2 pipeline is
  "the default" or "beat-scheduled".
- **Runtime:** grep-verified across 5 sweeps — v2 is strictly
  on-demand (Q2 resolution §3.7). Zero beat entries.
- **Drift class:** informational — runtime is more constrained than
  narrative suggests.
- **Severity:** LOW.
- **Remediation:** xx99 §7 anchor-update to reflect strictly-on-demand
  runtime.

### 14.6 Topic doc numeric drift candidates (var. LOW-MEDIUM)

Per topic doc frontmatter warning "specific numbers (claim caps,
deliberation thresholds, reviewer count) may drift". Explore
Agent 3 cross-check verifies most numeric claims currently MATCH
runtime. Candidates for post-xx99 validator rig-up:

| Doc claim | Location | Runtime constant | Status |
|---|---|---|---|
| "Max 20 claims" | topic doc:30 | `max_claims=20` default at `claims_pack_builder.py:54` | MATCH |
| "72h SpiderData window" | topic doc:27 | `timedelta(hours=72)` at `claims_pack_builder.py:116` | MATCH |
| "10 hex claim ID `C-xxxxxxxxxx`" | topic doc:32 | `hashlib.sha256(...).hexdigest()[:10]` at `content_claims.py:26` | MATCH |
| "3-reviewer panel" | topic doc:69 | 3 reviewers, DomainPersona conditional | MATCH (nuance: 2-3 dispatched depending on domain confidence >= 0.2) |
| "Domain confidence >= 0.2 threshold" | topic doc:75 | Cat B scope — Explore Agent 3 report |  Cat B verification owed |
| "48h freshness check" | topic doc:74 | Cat B scope (FactCheckReviewer) | Cat B verification owed |
| PublishGate thresholds (quality 0.75, novelty 0.60, structure 0.55) | topic doc:95-101 | Cat C scope — MATCH per Explore Agent 3 | Cat C verification |
| "3-round enhancement cap" | topic doc:178 | Cat C/D scope (SelfBlog.stats_snapshot['enhancement_count']) | Cat C/D verification |

**Severity per candidate:** LOW (all currently MATCH runtime; drift
watch, not current defect).

---

## 15. Known Technical Debt

**Q26 — What is technical debt?** Ranked by playbook §12 severity.

### 15.1 Per-claim citation-in-draft verification is absent (HIGH)

- **Location:** end-to-end Cat A + Cat B contract; Cat A owns the
  "claims present" check at `content_deliberation_runner.py:99-103`,
  Cat B FactCheckReviewer is designated per-claim validator per
  topic doc + patent Disclosure D.
- **Evidence:** `grep '\[C-' core/services/content_deliberation_runner.py
  core/services/claims_pack_builder.py core/services/content_claims.py` →
  matches only `ClaimsPack.to_prompt_block` at `content_claims.py:64`
  (writer-side injection) + `_TAG_BLACKLIST_FRAGMENTS` at
  `content_deliberation_runner.py:105` (unrelated). No regex-based
  per-claim in-draft citation verifier exists in Cat A.
- **Cat B enforcement is LLM prompt-based** per topic doc:74
  ("check freshness < 48h") — not runtime regex.
- **Remediation posture:** POSTURE-DECISION-PENDING per D65b
  evidence plan. If canonical PublishGate posture selected,
  citation-verifier moves to PublishGate. If per-variant gates,
  Cat A adds `_verify_citations_in_draft` step between Step 4b and
  Step 5.
- **Severity:** HIGH.

### 15.2 Silent partial-source failure — truth/evidence integrity degradation without explicit degraded-status contract (HIGH; Rigby F2 fold — elevated MEDIUM → HIGH)

- **Location:** `claims_pack_builder.py:70-85` (three try/except
  blocks) + `content_deliberation_runner.py:99-103` (single
  claims_count == 0 downgrade gate).
- **Evidence:** Three try/except blocks catch `Exception` for each
  of `_from_spider_data`, `_from_signal_clusters`,
  `_from_user_documents` with `logger.warning(...)` and no
  `failure_reason_code` set. Cat A gate downstream fires only when
  `claims_count == 0`.
- **Consequence:** partial-source failures produce degraded but
  non-empty ClaimsPack that passes Step 4b guard silently. Cat A
  can lose an entire evidence lane (e.g., SignalCluster fails
  entirely) without any degraded-status signal reaching Cat B/C/D
  consumers or `stats_snapshot['deliberation']` telemetry. Only
  the all-three-sources-fail case triggers the downgrade.
- **Severity:** **HIGH** per Rigby SIGN cycle 1 Q5 rationale —
  "truth/evidence integrity degradation without an explicit
  degraded-status contract" + "can cause materially incorrect
  outputs without visibility". Elevated from prior MEDIUM
  classification.
- **Remediation:** add per-source failure telemetry to
  `ClaimsPack.stats` (e.g., `source_failures: {'spider_data':
  '<err>', ...}`) so downstream can observe partial-failure state
  and cause + optional Cat B reviewer prompt injection of failure
  context + explicit degraded-status contract on
  `stats_snapshot['deliberation']`.

### 15.3 RAG scope enforcement absent — cross-tenant/workspace data exposure risk (HIGH; Rigby-elevated riskiest overall)

See §9.3 + §14.4 for full framing. **Rigby SIGN cycle 1 Q6: THE
single riskiest Cat A finding overall.** Severity HIGH regardless
of downstream Document workspace FK verification (per Rigby F3
fold — no longer "contingent"). Elevated to top of §19 T1 queue
as R.CONTENT.RAG-SCOPE per F4 fold.

### 15.4 Direct ORM reads bypass service layer (MEDIUM)

- **Location:** `claims_pack_builder.py:117` (LegacySpiderData),
  :192 (SignalCluster); `content_deliberation_runner.py:343`
  (DeliberationSession).
- **Evidence:** all three reads use `.objects.filter(...)` or
  `.objects.get(...)` directly rather than service-layer accessor
  (e.g., no `spider_data_service.get_recent(hours=72)` accessor).
- **Consequence:** high coupling risk — schema/index changes in
  Spider/Signal Engine/deliberation domains directly break Cat A.
- **Remediation posture:** POSTURE-DECISION-PENDING per D65a
  evidence plan.
- **Severity:** MEDIUM.

### 15.5 SignalCluster `pattern_type` consumer-side gap (MEDIUM)

See §9.2, §14.3. Extension of S1502 §14.3 6-arc COMPLETED pattern.

### 15.6 Rewrite pass hard-capped at 1 iter, no config knob (LOW / POSTURE-DECISION-PENDING)

- **Location:** `content_deliberation_runner.py:107-116`.
- **Evidence:** `grep 'MAX_REWRITE\|REWRITE_MAX\|max_rewrite'
  core/services/content_deliberation_runner.py` → 0 matches. Single
  hard-coded rewrite.
- **Consequence:** REVISE-decision blogs get one shot at recovery;
  bounded recovery envelope.
- **Remediation posture:** POSTURE-DECISION-PENDING per D65c
  lifecycle-transition-ownership evidence plan (whether recovery
  loops count is variant-owned or canonical).
- **Severity:** LOW / POSTURE-DECISION-PENDING.

### 15.7 `_run_review_conversation` panel-failure quiet fallback (LOW)

- **Location:** `content_deliberation_runner.py:91-94`.
- **Evidence:** `except Exception as e: logger.warning(...);
  result['decision'] = 'REVISE'` — no `failure_reason_code` set on
  panel failure.
- **Consequence:** downstream cannot distinguish "REVISE because
  reviewers said so" from "REVISE because panel crashed".
- **Remediation:** add `result['panel_failure'] = str(e)` or
  `failure_reason_code = 'PANEL_FAILED'` for observability.
- **Severity:** LOW.

### 15.8 No cleanup task for `DeliberationSession` failed/completed rows (LOW / POSTURE-DECISION-PENDING)

- **Evidence:** only `reap-zombie-work` targets DeliberationSession
  (active → failed at 60min); no age-based archival for
  failed/completed rows.
- **Consequence:** DeliberationSession table growth unbounded.
- **Remediation:** POSTURE-DECISION-PENDING per xx99 evidence plan;
  if learning-loop integration (Group 1300) requires session
  history retention, current absence is intentional.
- **Severity:** LOW / POSTURE-DECISION-PENDING.

### 15.9 Session 1001 operational-context injection module boundary (LOW)

- **Location:** `content_deliberation_runner.py:189-196` imports
  from `core.tasks._build_operational_context`.
- **Evidence:** `_build_operational_context` at `core/tasks.py:5560`
  is a private-underscore module-level function; not a service class.
- **Consequence:** Cat A depends on private helper in shared task
  module; refactor risk if `core/tasks.py` reorganized.
- **Remediation posture:** POSTURE-DECISION-PENDING — should this
  helper move into `core/services/` as `operational_context_service`?
- **Severity:** LOW.

### 15.10 ContentWriterAgent size (LOW)

- **Location:** `core/agents/content_writer_agent.py` (2,419 lines).
- **Evidence:** 18+ methods; multi-mode (base / rewrite / diagnostic
  / directed); prompt building split across `_build_intelligent_system_prompt`
  + `_build_content_prompt` + 4 spider injection helpers +
  `_execute_rewrite`.
- **Consequence:** approaches god-service concern threshold (3,000
  line playbook §12 threshold not yet crossed).
- **Remediation posture:** LOW today; watch trend; if crosses
  3,000, escalate to Cat B S1602 or post-arc T-slot for structural
  refactor ADR.
- **Severity:** LOW.

---

## 16. Boundary Violations

**Q24 — What services violate boundaries?**

### 16.1 F1-boundary compliance verification (Rigby SIGN F1 + F5 folds applied)

Grep-verified across `content_deliberation_runner.py`,
`claims_pack_builder.py`, `content_claims.py`, `evidence_pack_builder.py`,
`content_writer_agent.py`:

- **Cat A → Cat C boundary:** ONE routine handoff at
  `content_deliberation_runner.py:445` (`from
  core.services.publish_gate import PublishGate` +
  `gate.apply_to_blog(blog)`). No writes to Cat C-owned tables;
  Cat A does not touch PublishGate internal thresholds.
  **CLEAN routine handoff.**
- **Cat A → Cat D boundary (F5 fold — corrected framing):** ONE
  `SelfBlog.objects.create` at `content_deliberation_runner.py:401`.
  Bypasses `deliverable_factory` and the 5-gate
  `DeliverableGatedError` chain. Per Rigby SIGN F1 fold, this is
  **canonicalization debt Cat A flags as D65a evidence input**,
  NOT proof of intentional island architecture. Absent an
  explicit design-decision ADR, the runtime write is a
  debt/legacy integration gap; Chris/xx99 D65a brief consumes
  this evidence but selects posture intent — Cat A does not
  editorialize. **HEADLINE for D65a evidence plan.**
- **Cat A → Cat B boundary:** `content_review_panel_v2.run_reviews`
  + `ConversationOrchestrator.generate_conversation` at :225-259.
  Cat A hands off draft + ClaimsPack + topic + domain; Cat B
  internals (SkepticReviewer, FactCheckReviewer, DomainPersonaReviewer,
  DecisionEnforcerAgent) run inside Cat B and Cat A consumes the
  results. **CLEAN routine handoff.**

**Writes summary (F5 fold — corrected from earlier "ZERO writes
to Cat B/C/D" phrasing which contradicted the persistence
handoff):** ZERO writes to Cat B/C-owned tables + ONE write to
Cat D (`SelfBlog.objects.create` at :401) as the persistence
handoff. Grep-verified via `.objects.create` sweep in Cat A files —
only `SelfBlog.objects.create` matches; no `Deliverable`,
`ContentReview`, or `PublishGate` writes.

### 16.2 Adjacent-module dependency (Cat A → core.tasks)

Session 1001 operational-context injection at
`content_deliberation_runner.py:191` imports
`_build_operational_context` from `core/tasks.py`. Classified as
**adjacent-module dependency, not boundary violation**. Rationale:
`core/tasks.py` is a shared task module (not domain-owned per
DOC_LIFECYCLE §2c); helper is telemetry-gathering (not Cat B/C/D
domain machinery). Whether the helper should relocate is D65a
evidence plan question (§15.9).

### 16.3 No cross-domain writes

Grep-verified: `.objects.create` calls in Cat A scope hit only
`SelfBlog` (Cat D) at :401 (documented handoff) and
`DeliberationSession` internally via ConversationOrchestrator. No
writes to Cat B / Cat C / Sports / Revenue / Memory / Employee OS
tables.

---

## 17. Duplicate or Overlapping Systems

**Q23 — What models/services overlap with other domains?**

### 17.1 ContentWriterAgent overlap with OpportunityDraftGenerator

- **Overlap:** `ContentWriterAgent.execute()` is used by both:
  - Cat A `_generate_draft` at `content_deliberation_runner.py:208`
    (v2 blog pipeline).
  - S1402 revenue arc `OpportunityDraftGenerator.generate()` at
    `core/services/ops_autopilot/outreach_generation.py:340`
    (outreach draft path).
- **Overlap classification:** intentional shared draft generator.
  Not a duplicate.
- **Posture-relevance:** D65a evidence — if integration posture
  selected, all variant-writing services should route through
  ContentWriterAgent canonical entry (already the case). If island
  posture selected, siblings retain freedom to adopt own writers
  (as OpportunityDraftGenerator does when it bypasses ClaimsPack
  + review panel entirely).

### 17.2 v1 vs v2 content_review_panel (Cat B scope, Cat A adjacent)

- **`content_review_panel_v2.py`** — v2 canonical dispatch, used by
  Cat A `_run_review_conversation`.
- **`content_review_panel.py`** — v1 legacy, instantiates
  `DomainContentContextBuilder` at :82-85. Reader path unclear
  from Cat A scope.
- **Classification:** parked to Cat B S1602 per parent §6.1
  "v1 vs v2 content_review_panel canonicalization".

### 17.3 SelfBlog vs Deliverable parallel-variant overlap

- **SelfBlog** (`core/models_unified_system.py:20611`) is a
  parallel-schema-sibling to `Deliverable`
  (`core/models_deliverables.py:84`). Both have publish-ready +
  status + quality fields; SelfBlog has own quality/novelty/
  structure/mythology score fields; Deliverable has 5-gate factory
  check.
- **Cat D-primary** — deferred to S1603 Cat D per D66 sequence.
  Cat A merely records that Cat A writes to SelfBlog directly
  (not Deliverable) as D65a evidence.

### 17.4 `SpiderData` vs `LegacySpiderData` alias

See §14.1. Alias, not duplicate.

---

## 18. Ownership Gaps

**Q25 — What ownership is unclear?**

### 18.1 `_build_operational_context` helper

- Lives in `core/tasks.py:5560`, imported by Cat A at
  `content_deliberation_runner.py:191`. Ownership question: is this
  a Cat A responsibility (belongs in `core/services/` as
  `operational_context_service`) or a shared telemetry helper (belongs
  in `core/tasks.py` or a new `core/services/telemetry_service.py`)?
- **Ownership verdict:** UNCLEAR — POSTURE-DECISION-PENDING per §15.9.

### 18.2 SignalCluster consumer contract

- No formalized Protocol / typed interface defines which fields Cat A
  requires from SignalCluster. Docstring at `claims_pack_builder.py:4-9`
  is informal.
- **Ownership verdict:** should be Cat A-owned per parent §3 Cat A
  "ClaimsPack signal-consumption contract"; formalization owed to
  xx99 D65a evidence plan.

### 18.3 RAG scope contract

- No formalized workspace/user scoping enforcement on
  DocumentEmbedding read at `claims_pack_builder.py:245`.
- **Ownership verdict:** should be Cat A-owned (as consumer) OR
  Memory RAG domain-owned (as source) — canonical placement pending
  cross-arc S1300 or Cat E S1605 investigation.

### 18.4 Evidence pack schema versioning

- `evidence-pack-v1` string constant in `evidence_pack_builder.py`;
  no ADR governing migration path to `evidence-pack-v2`.
- **Ownership verdict:** should be Cat A-owned per persistence-layer
  ownership; canonical schema evolution ADR owed to xx99 §5 D65b
  evidence plan.

### 18.5 Rewrite loop count policy

- Hard-coded 1-iter cap at `content_deliberation_runner.py:107-116`;
  no ADR governing whether this is variant-adaptive.
- **Ownership verdict:** POSTURE-DECISION-PENDING per D65c
  lifecycle-transition-ownership.

### 18.6 Dormant module ownership on `content_claims` + `content_review_panel_v2`

- Both files last-touched by the Session 964 commit
  (`0c986d5a` per `git log`) which introduced the entire v2
  pipeline. `content_claims.py` (102 lines) has zero subsequent
  changes; `content_review_panel_v2.py` (Cat B-owned but Cat A
  handoff surface) has minimal churn since S964.
- `ContentDeliberationRunner` has recent maintenance (Session
  1098 rewrite context, Session 1103 evidence-first mode);
  `ClaimsPackBuilder` had S1148 `LegacySpiderData` rename churn.
- **Ownership verdict:** DORMANT STEWARDSHIP for `content_claims`
  + partial for `content_review_panel_v2`; no current owner tag
  in module docstring, no TODO owner line. If the S964 author
  context-switches or leaves, these modules become
  effectively-orphaned.
- **Remediation posture:** post-arc T-slot — add
  `# Owner:` line at module docstring per playbook §16 ownership
  hygiene. Not urgent because both modules are STABLE (see §13);
  more a documentation-hygiene item than a defect.

---

## 19. Recommended Future Research

**Q28 — What should be researched next?** Ranked by architectural
uncertainty × risk × unblocked flows.

### 19.1 S1602 Cat B (next child under Group 1600)

**Load-bearing inheritance from S1601:**

- Confirm FactCheckReviewer enforcement mechanism (LLM prompt vs
  regex vs typed constraint) on per-claim `[C-xxxxxxxxxx]` citation
  in draft — resolves S1601 §15.1 HIGH gap.
- Confirm 3-reviewer panel dispatch shape + synthetic-FAIL semantics
  + `DomainPersonaReviewer` conditional threshold.
- Verify v1 vs v2 content_review_panel canonicalization posture
  per parent §6.1.
- Inherit S1601 §14 drift matrix + §15 debt matrix rows tagged
  "Cat B-owned verification needed".

### 19.2 S1603 Cat D (P3 per D66 sequence, moved from P4 per F3 fold)

- Deliverable base + 5 parallel-variant scope; Cat A provides
  D65a-analog evidence via §9.1 (SelfBlog.objects.create bypass of
  deliverable_factory) as headline input for Cat D's canonical
  posture-decision framing.
- Cat D inherits S1601 §16.1 boundary observation.

### 19.3 S1604 Cat C (P4 per D66 sequence)

- PublishGate + Publish Rails; Cat A provides D65b-analog evidence
  via §7.1 Step 8 handoff + §15.1 citation-integrity guard placement
  question.

### 19.4 S1605 Cat E (P5)

- Rigby PA-tool surface; inherit S1601 §3.3 `blog_tool` handler
  boundary + S1601 §14.4 RAG scope question if Document workspace FK
  not yet verified.

### 19.5 S1606 Cat F (P6 — LAST child)

- Cross-domain integration lens; consume S1601 §9 integration map +
  §14 drift + §15 debt + §17.1 ContentWriterAgent cross-domain
  overlap; produce D65a/b/c three-axis posture-decision evidence
  plan for xx99.

### 19.6 Post-arc T-slots (Chris-gated) — Rigby-ranked Q7 top-3 elevated to top of queue

Rigby SIGN cycle 1 Q7 rank per risk × architectural uncertainty
× unblocked-flows rubric:

- **T1 R.CONTENT.RAG-SCOPE (RANK #1 — Rigby-verified riskiest
  overall).** Ratify workspace / cross-tenant scoping contract
  on DocumentEmbedding read. Verify Document workspace FK schema
  (UNK-1) + add enforcement at query boundary if scoping absent.
  Consumes S1601 §9.3 + §14.4 + §15.3.
  Cross-tenant / cross-workspace evidence-exposure risk = the
  single highest-priority Cat A follow-on.
- **T1 R.CONTENT.CITATION-INTEGRITY (RANK #2).** Codify per-claim
  citation verifier (code-side regex vs LLM prompt) per D65b
  posture selection. Confirm Cat B FactCheckReviewer enforcement
  mechanism (UNK-2). Consumes S1601 §15.1. Unblocked via Cat A
  code-side implementation even if Cat B remains prompt-based.
- **T2 R.CONTENT.SIGNAL-PATTERN-TYPE-CONTRACT (RANK #3).**
  Formalize SignalCluster.pattern_type consumer contract for
  Cat A. Consumes S1601 §14.3 + §15.5. Extends S1502 §14.3
  6-arc COMPLETED.
- **T3 R.CONTENT.EVIDENCE-PACK-SCHEMA-ADR:** ratify evidence-pack
  schema versioning + migration path. Consumes S1601 §18.4.
- **T4 R.CONTENT.OPERATIONAL-CONTEXT-RELOCATION:** move
  `_build_operational_context` to `core/services/` (or ratify
  current placement). Consumes S1601 §15.9 + §18.1.
- **T5 R.CONTENT.LEARNING-LOOP-BRIDGE:** wire Cat A output
  (reviewer verdicts + PublishGate scores + author attribution) to
  Group 1300 Memory learning loop. Consumes S1601 §9.5. Rigby
  SIGN cycle 1 Q4(b): current absence is intentional decoupling
  under Cat A boundary; T-slot open only if S1300 arc requires
  explicit content → memory feedback contract.

---

## 20. Appendix

### 20.1 Files inspected

**Cat A source:**

- `core/services/claims_pack_builder.py` (301 lines)
- `core/services/content_claims.py` (102 lines)
- `core/services/content_deliberation_runner.py` (453 lines)
- `core/services/evidence_pack_builder.py` (187 lines)
- `core/agents/content_writer_agent.py` (2,419 lines)
- `core/models_deliberation.py` (270 lines — 4 model definitions)

**Cat A-adjacent (read to establish boundary):**

- `core/tasks.py` :5560, :5758-5761 (task shim + operational context)
- `core/tasks_content.py` :2399-2601 (impl task)
- `core/services/td_handlers_content.py` :84-116, :162-182, :1480-1505 (PA tool handlers)
- `core/views_research_demo.py` :1106-1145 (REST v2 dispatch)
- `core/views_deliberation.py` :51-561 (read endpoints)
- `core/services/ops_autopilot/budget.py` :1076, :1113-1116, :1139 (budget tier)
- `core/celery.py` :433-438, :587-591 (adjacent beats; zombie reap)
- `core/models_signal_intelligence.py` :29 (SignalCluster model)
- `core/models_unified_system.py` :3691, :20611 (LegacySpiderData; SelfBlog)
- `content/models.py` :707, :857-887 (DocumentEmbedding)
- `core/conversation_orchestrator.py` :902, :1012, :1574 (generate_conversation entry)
- `core/services/content_review_panel_v2.py` :88, :107, :124, :208 (Cat B boundary — for handoff shape only)
- `core/services/publish_gate.py` :27, :579 (Cat C boundary — for handoff shape only)

**Docs inspected:**

- `docs/research/domains/content/1600_content_domain_scoping.md` (parent scoping — 1502 lines)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§9, §11.2, §12, §13, §14, §15, §16)
- `docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md` (structural precedent)
- `docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md` (cross-arc handoff)
- `docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md` (cross-arc handoff)
- `docs/topics/content-pipeline.md` (Session 1147 topic doc)
- `docs/audit-2026/04-content-pipeline.md` (April 2026 audit)
- `docs/patents/DISCLOSURE_D_CLAIMS_BASED_DELIBERATION.md`
- `docs/patents/DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md`
- `docs/patents/EXECUTIVE_SUMMARY_WS2.md`
- `docs/narratives/CONTENT_PIPELINE.md`
- 9 handoffs per §11.2

### 20.2 Grep patterns used (verifier front-run)

Load-bearing binary claims — grep patterns that yielded the cited
result:

| Claim (§) | Pattern | File(s) | Result |
|---|---|---|---|
| §3.1 zero beat entries fire v2 (§3.7 Q2) | `content_deliberation\|ContentDeliberationRunner\|deliberation_runner\|claims_pack\|content_pipeline\|generate_self_blog_deliberation` | `core/celery.py` | Only unrelated `reap-zombie-work` comment; no beat entries fire v2 |
| §3.4 no mgmt command fires v2 | `deliberation\|claims\|content_pipeline\|content_writer` | `core/management/commands/*.py` | Only `write_self_blog.py` (v1 path); no v2 command |
| §3.5 no WS/Discord fires v2 | `ContentDeliberationRunner\|ClaimsPackBuilder\|run_blog` | `core/consumers*.py`, `core/services/discord_bot.py` | 0 matches |
| §3.6 orchestrator doesn't call run_blog | `ContentDeliberationRunner\|run_blog` | `core/conversation_orchestrator.py` | 0 matches |
| §9.1 no Sports consumption | `SportsBettingBrief\|SportsContentContextBuilder` | `core/services/claims_pack_builder.py` | 0 matches |
| §9.1 no Revenue consumption | `OutreachDraft\|ClosePack` | `core/services/claims_pack_builder.py` | 0 matches |
| §9.1 no Employee OS coupling | `JobContract\|mission_runner` | `core/services/content_deliberation_runner.py`, `core/services/claims_pack_builder.py` | 0 matches |
| §9.1 no learning-loop write | `AgentMemory\|AgentPerformance\|AgentLearning` | Cat A files | 0 matches |
| §9.2 no pattern_type read | `pattern_type` | `core/services/claims_pack_builder.py` | 0 matches |
| §14.4 no workspace_id in RAG call | (see §9.3 call site) | `core/services/claims_pack_builder.py:245` | Verified via direct read of call signature |
| §15.1 no in-draft citation regex | `\[C-` | `core/services/content_deliberation_runner.py`, `claims_pack_builder.py`, `content_claims.py` | Only `to_prompt_block` injection; no in-draft verifier |
| §15.6 no rewrite loop config | `MAX_REWRITE\|REWRITE_MAX\|max_rewrite` | `core/services/content_deliberation_runner.py` | 0 matches |
| §16 no cross-domain writes | `\.objects\.create` | Cat A files | Only `SelfBlog.objects.create` at :401 (documented Cat D handoff) |
| §16 no ContentReview / Deliverable / PublishGate FK from Cat A models | `ForeignKey.*ContentReview\|ForeignKey.*PublishGate\|ForeignKey.*Deliverable` | `core/models_deliberation.py` | 0 matches |

### 20.3 Unresolved unknowns

- **UNK-1:** Does `Document` model have `workspace_id` FK enforcing
  workspace scope, or is DocumentEmbedding globally scoped by
  design? (Affects §14.4 severity assessment.) Cat E S1605 or
  Group 1300 Memory arc verification pending.
- **UNK-2:** Does `FactCheckReviewer` perform regex `[C-xxxxxxxxxx]`
  check on draft text, or LLM prompt verbal check only? (Affects
  §15.1 HIGH — moves to Cat B S1602 scope.)
- **UNK-3:** Does `evaluate_unscored_blogs` beat (2h at :10 per
  topic doc:172) fire against SelfBlog rows created by Cat A v2
  pipeline? (Cat C-primary; noted for Cat C S1604.)
- **UNK-4:** Are cross-reviewer agreement metrics captured
  post-S1598/S1599 evidence-capture fix? (Prior audit §10 line 229
  flagged this as truth gap; verification for Cat B S1602.)

### 20.4 Conflicts between sources

- **`SpiderData` vs `LegacySpiderData`** — parent §3 + topic doc
  vs runtime naming (see §14.1). Reconcile at xx99 §7.
- **v2 pipeline "beat-scheduled" vs strictly-on-demand** —
  narrative doc vs runtime (see §14.5). Reconcile at xx99 §7.

### 20.5 Verifier-loop corrections + Rigby SIGN fold notes

**Verifier-loop pre-SIGN corrections:**

- Explore Agent 5 initially classified `ContentWriterAgent` line
  count from patent claim ("~298 lines"); parent audit direct read
  confirms 2,419 lines. Corrected at §5.1.
- Explore Agent 5 flagged prior audit (`04-content-pipeline.md`)
  finding "verdicts not stored in session metadata"; parent audit
  notes this predates S1598/S1599 evidence-capture fix. Cat A
  current-state observation deferred to Cat B S1602 verification
  (UNK-4).

**Rigby SIGN fold notes** (SIGN cycle 1 SIGN-with-edits at Medium
confidence on fresh isolation pin `pa-9f075a024552b663`, 2026-07-02):

- **F1 fold — SelfBlog.objects.create framing.** Reframed from
  "direct code-side evidence for the island posture" to
  "**canonicalization debt Cat A flags as D65a evidence input,
  NOT proof of intentional island architecture**". Applied to §1
  Exec Summary HEADLINE for D65a + §9.1 integration map table
  Cat D row + §16.1 Cat A → Cat D boundary paragraph. Rationale
  per Rigby Q4(a): absent an explicit design-decision ADR, the
  runtime write is debt/legacy integration gap, not deliberately-
  chosen architecture. Chris/xx99 selects posture intent.
- **F2 fold — Silent partial-source failure severity elevation.**
  Elevated from MEDIUM to **HIGH** at §1 Exec Summary item 3 +
  §15.2. Rationale per Rigby Q5: "truth/evidence integrity
  degradation without an explicit degraded-status contract" +
  "can cause materially incorrect outputs without visibility".
  Cat A can lose an entire evidence lane silently and still pass
  the `claims_count == 0` gate.
- **F3 fold — RAG scope explicit cross-tenant/workspace framing.**
  Applied at §1 Exec Summary item 1 + §9.3 + §14.4 + §15.3.
  Reframed from "scope contingent on Document workspace FK" to
  "**cross-tenant / cross-workspace data exposure risk**":
  pipeline could ground drafts in evidence Cat A should not have
  permission to see — security + trust failure mode. Severity
  remains HIGH regardless of downstream Document workspace FK
  verification.
- **F4 fold — RAG scope elevated to riskiest overall Cat A
  finding.** Applied at §1 Exec Summary item 1 (renumbered from
  #3 to #1 with "RISKIEST" tag) + §19.6 T-slot queue reordering
  (R.CONTENT.RAG-SCOPE now RANK #1 with Rigby-verified riskiest
  tag). Rationale per Rigby Q6.
- **F5 fold — Fix "ZERO writes to Cat B/C/D" contradiction.**
  Corrected at §1 Exec Summary + §16.1 writes-summary paragraph.
  Original phrasing "ZERO writes to Cat B/C/D-owned tables"
  contradicted the persistence handoff explicitly listed in the
  same paragraph. New phrasing: "**ZERO writes to Cat B/C-owned
  tables; ONE write to Cat D (`SelfBlog.objects.create` at
  `content_deliberation_runner.py:401`) as the persistence
  handoff**". Rigby Q8 caught the internal contradiction; F5
  fold prevents a Rigby-grep-verification failure at Cat A
  boundary language.
- **F6 fold — Verification-report endpoint boundary caution
  pinned.** Added at §6.1 verification-report row. If endpoint
  performs substantive verification (claim/citation checks,
  evidence-pack schema validation) beyond presentation, its
  semantics remain Cat A truth-machinery even though implemented
  in views. Cat E S1605 confirms boundary shape. Rigby Q1 edge
  caution + Q9 missing-area note.

**Two "do not regress" notes for PR** (per Rigby SIGN discipline):
(i) preserve F5 "ZERO writes to Cat B/C-owned tables; ONE write
to Cat D (SelfBlog)" phrasing at §1 + §16.1 — do not silently
revert to "ZERO writes to Cat B/C/D-owned tables"; (ii) preserve
F1 "canonicalization debt / NOT proof of intentional island
architecture" phrasing at §1 HEADLINE + §9.1 + §16.1 — do not
silently revert to "direct code-side evidence for island posture"
language which editorializes the D65a posture selection Chris
gates at post-arc ADR.

**Rigby Final Verdict (cycle 1, 2026-07-02):**
- **Overall confidence:** Medium
- **Most accurate part:** Cat A boundary inventory + Q1/Q2 load-bearing question resolution with correct file:line anchors (`content_deliberation_runner.py:99-103`, `claims_pack_builder.py:245`, `content/models.py:879-887`, `content_deliberation_runner.py:401`)
- **Weakest part:** Boundary-language precision in Exec Summary around writes/ownership (F5 fold addresses)
- **Missing area:** Verification-report endpoint boundary tightening (F6 fold addresses)
- **Overstated maturity:** RAG scoping + silent partial-source failure prevent Cat A end-to-end truth guarantees from qualifying as STABLE (F2 + F4 folds address by elevating severity + risk framing)
- **Understated maturity:** `content_claims.make_claim_id` + ClaimsPack dataclass contract can reasonably be STABLE as bounded local mechanisms (§13 already classifies as STABLE — Rigby confirms wording is correct)
- **Biggest architectural risk:** RAG scope (cross-tenant/workspace data exposure risk) (F3 + F4 folds land)
- **Most important next research:** T1 R.CONTENT.RAG-SCOPE (F4 fold reorders §19.6 to rank #1)
- **What Claude got wrong:** "ZERO writes to Cat B/C/D-owned tables" claim is incorrect given the Cat D persistence handoff (F5 fold corrects)
- **What must change before canonical:** F1-F6 folds landed pre-commit; no NEEDS-MORE outstanding
- **Final verdict:** **SIGN-with-edits (six folds folded pre-commit — see F1-F6)**

**D48 preemptive stability-probe gate 10th-arm outcome:** SIGN
cycle 1 held clean at Medium confidence in three turns on fresh
isolation pin `pa-9f075a024552b663`. No worker instability observed;
no pin retirement + re-mint needed. Rigby SIGN worker-instability
recovery playbook (`feedback_rigby_sign_worker_instability_recovery.md`)
NOT triggered — sub-pattern extension anticipated to
five-consecutive-fully-clean-arms **S1503+S1504+S1505+S1506+S1601**
per D48 gate expectation at S1600 open.

### 20.6 Cross-arc handoffs owed to sibling children

- **To S1602 Cat B:** verify FactCheckReviewer per-claim citation
  enforcement mechanism (§15.1 UNK-2). Verify 3-reviewer panel
  DomainPersonaReviewer conditional threshold (§14 topic doc:75).
  Verify v1 vs v2 content_review_panel canonicalization (§17.2).
- **To S1603 Cat D:** consume §9.1 SelfBlog.objects.create bypass
  of deliverable_factory as D65a HEADLINE evidence input. Consume
  §17.3 SelfBlog vs Deliverable parallel-variant overlap.
- **To S1604 Cat C:** consume §7.1 Step 8 PublishGate handoff +
  §15.1 citation-integrity guard placement question as D65b
  evidence.
- **To S1605 Cat E:** consume §3.3 blog_tool handler boundary +
  §14.4 RAG scope question. Verify Document workspace FK (UNK-1).
- **To S1606 Cat F:** consume §9 integration map + §14 drift +
  §15 debt + §17.1 ContentWriterAgent cross-domain overlap.
- **To S1699 xx99:** consume §19.6 T1-T5 follow-on queue as post-
  arc T-slot inputs. Consume §14.1 naming reconciliation for
  §7 anchor-update recommendations. Consume §12.5 lifecycle stages
  1-2 (evidence assembly + draft generation — Cat A rows of the
  12-stage F7-fold-expanded Deliverable Lifecycle Traceability
  Table).
