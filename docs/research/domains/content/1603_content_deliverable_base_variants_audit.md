---
title: "S1603 Content / Deliverables / Publishing — Cat D: Deliverable Base + Specialized Variants (Child Audit)"
status: active
authority: child-audit
category: child_audit
session: 1603
date: 2026-07-02
domain_slug: content
research_group: 1600
child_slot: P3
authors: Claude Code (Chris directed via short command "Continue research group 1603")
verifier_loop: |
  Playbook §11.2 20-section template applied. Six parallel Explore sub-agents
  per §13 (A1 Models, A2 Services + Runtime, A3 APIs + Tools + Tasks + Cmds,
  A4 Integrations, A5 Docs + Prior Research, A6 Drift + Debt + Maturity).
  Parent-Claude verifier-loop per §14 applied on 22 pre-Explore load-bearing
  binary claims (all grep-verified against HEAD `b8269101`) + 6 post-Explore
  load-bearing binary claims. **1 pre-Explore drift correction** (F0-analog):
  parent §3 D cited central factory at `deliverable_factory.py:1269`; actual
  `def create_deliverable(` at :752 (line :1269 is `Deliverable.objects.create`
  call inside the function body — content-hash dedupe branch). **1
  post-Explore correction** (F0b-analog): Explore A6 initially flagged
  content_hash as dead-write; direct-read confirms content_hash IS queried in
  the factory's 72h dedup branch at :961-970 — CORRECTED to "used for
  factory-internal 72h dedup + external duplicate detection open question".
  D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface
  upfront applied at §4.8 (deliverable_type enum) + §5.6 (factory branches)
  + §6.5 (deliverable_tool actions) + §8.5 (lifecycle stages) per parent D68
  F8/F10 folds — third sibling of Group 1600 to propagate the pattern
  upfront after S1601 first + S1602 second. **Rigby SIGN cycle 1 verdict:
  SIGN-with-edits (18 folded) at Medium-High confidence (0.75 → High after
  F1 resolution)** on fresh isolation pin `pa-8af9063864bf4a7f` (batch A/B/C
  substantive on turn count 3-4; final-verdict single-question follow-up
  clean; retire at S1603 close per playbook §15). **F1-F18 folds landed
  pre-commit** (§20.5 for details): F1 shadow-`create_deliverable` in
  `real_job_execution_consumer.py:200` **RESOLVED as name-collision** (demo
  WebSocket consumer returning plain dicts; never touches ORM; NOT a factory
  bypass; factory adoption metric ~98% REMAINS ACCURATE); F2 additional
  Cat D-adjacent services (`deliverable_envelope.py`, `conversation_deliverable_extractor.py`,
  `platform_event_view.py`, `deliverables_consumer.py`) inventoried in §5;
  F3 5 mgmt commands using factory added to §7.4; F4 Deliverable base
  maturity explicit "current-scope definition"; F6 D65a reframed to
  3-category classification (envelope-integrated / standalone-by-design /
  unfinished-orphan); F7 triple-gate reframed as "separation-of-concerns
  lacking composition contract"; F8 OutreachDraft delivery upgraded HIGH →
  CRITICAL; F9 SelfBlog bypass nuanced to "consistency-not-breakage IF
  envelope canonical"; F11 T.15.6 reframed as "composition contract
  missing" not "too many gates"; F12 NEW T1 R.CONTENT.VARIANT-CATEGORIZATION-CLARIFICATION;
  F13 NEW T1 R.CONTENT.CANONICAL-CREATION-CONTRACT; F14 OutreachDraft
  delivery T2 → T1; F15 over-binary claims softened; F16 Cat D-vs-Cat C
  boundary tightened; F17 F1 resolved before commit (Option 1 per Rigby
  verdict); F18 maturity provisional rewound (F1 resolved). D48 preemptive
  stability-probe gate 12th arm CONFIRMED — seven-consecutive-fully-clean-arms
  sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603 CONFIRMED.
owner: claude (drafted S1603)
supersedes: none
related:
  - docs/research/domains/content/1600_content_domain_scoping.md              # parent — §3 D Cat D scope + D66 P3 slot + boundary rule (F2 fold)
  - docs/research/domains/content/1601_content_claims_pack_deliberation_pipeline_v2_audit.md   # Cat A sibling — §9.1 SelfBlog.objects.create bypass at runner:401 D65a HEADLINE input
  - docs/research/domains/content/1602_content_reviewers_decision_enforcement_audit.md         # Cat B sibling — §16.1 Cat B write to SelfBlog.stats_snapshot['deliberation'] at runner:415 D65a HEADLINE input
  - docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md                 # S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN pattern precedent + §5.1 HOT-PATH-CHOKE-BYPASS
  - docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md          # S1402 F.B1 OutreachDraft delivery ZERO outbound channel — Cat D cross-arc handoff
  - docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md                     # S1403 F.C4 ContentEngagement docstring drift — Cat D cross-arc handoff
  - docs/research/domains/sports/1599_sports_canonical_summary.md                              # third xx99 canonical summary + §11.3 §10 meta-methodology template
  - docs/research/domains/revenue/1499_revenue_canonical_summary.md                            # second xx99 + D55 (ii) JobContract split precedent
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                                   # §11.2 20-section template + §13 six-parallel-Explore + §14 verifier-loop + §15 SIGN policy
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md                                          # OS — child-audit contract §8
  - docs/research/ARCHITECTURE_INDEX.md                                                          # v37 → v38 bump at S1603 commit
  - docs/research/OPEN_ARCS.md                                                                    # Group 1600 row current-child S1603 → S1604 at S1603 commit
  - docs/patents/DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md                         # §5 Layer 2 claim :140 invalidation extends to Cat D task-spawn concern
  - docs/topics/content-pipeline.md                                                                # Session 1147 topic doc — drift-labeled; SelfBlog-centric, no Deliverable base coverage
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
---

# Session 1603 — Content / Deliverables / Publishing Cat D: Deliverable Base + Specialized Variants (Child Audit)

## 1. Executive Summary

Cat D is the **canonical container question** for Group 1600: is
`Deliverable` (`core/models_deliverables.py:84`) the sole canonical
content-shaped output container across the platform, or is it a base
with **five structurally-independent parallel-schema-siblings** each
carrying its own lifecycle, quality gate, and publish semantics? At
`main` HEAD `b8269101` the evidence is unambiguous on the *structural*
axis: **all five parallel variants — `SelfBlog`
(`models_unified_system.py:20611`), `OutreachDraft`
(`models_outreach.py:18`), `ClosePack` (`models_close_pack.py:20`),
`SportsBettingBrief` (`models_unified_system.py:18394`),
`BlockchainAuditBrief` (`models_unified_system.py:18435`) — are
islands.** Grep across `core/` for `ForeignKey.*Deliverable` returns
**zero** reverse-FKs. The direction is uni-directional: `Deliverable`
FKs *to* `SelfBlog` and `PodcastEpisode` (Session 862, at :192-207),
and no variant carries a reverse FK back to `Deliverable`. This is
D65a's HEADLINE structural fact for xx99 evidence.

Cat D's runtime posture on the *behavioural* axis is more nuanced.
The central factory `deliverable_factory.create_deliverable`
(**`core/services/deliverable_factory.py:752`** — parent §3 D cited
`:1269`, which is actually the `Deliverable.objects.create(**kwargs)`
call inside the factory's atomic-transaction block; F0 pre-Explore
drift correction) is **partially adopted**: 47 files carry
`Deliverable.objects.create` matches (92 total lines including
tests, migrations, docs). Of those, **only 2 production Deliverable
bypasses** were identified — `core/views_deliverables.py:305`
(user-initiated clone) and `core/services/workflow_orchestration_agent.py:5107`
(morning-brief WorkflowAgent). Every other non-test, non-migration
production creator either (a) routes through the factory or (b) creates
a *different model* (variant) that does not use the factory at all.

The factory itself enforces a **5-gate quality check** (`_should_create_deliverable`
at :358 with `gate_1_media_stub` / `gate_2_smoke_pattern` /
`gate_3_min_length` / `gate_4_template_leak` / `gate_5_no_relevance`
reason_codes; `DeliverableGatedError` at :46-74), a **72h content-hash
dedupe** (:955-970 — F0b post-Explore correction: NOT dead-write; the
factory *does* query `Deliverable.objects.filter(content_hash=c_hash)`
inside the atomic transaction), a **72h title-window dedupe**
(:934-953), a **provenance-parent dedupe** (:906-927), a
**publish-intent resolver** (`resolve_publish_intent` at :605 — 4
"publishing" agents mapped, all else defaults `internal_only`), and
a **Session 1199 PR-D hard exception** (`DeliverableProvenanceMissingError`
at :77 / raised at :1058) for non-PA-direct callers missing
`parent_execution_id`. The factory's *scope* is unambiguously Cat D;
the *variants' bypass of it* is Cat D's biggest drift.

**Cat D's headline finding for D65a evidence plan (F6 Rigby fold —
neutral taxonomy, NOT normative integration blocker):** at the
structural layer, the five variants + Deliverable base form a
mixed classification. Following Rigby's SIGN Batch B correction,
D65a evidence is best expressed as a **3-category variant
taxonomy** rather than a binary island-vs-canonical claim:

1. **Envelope→Object integrated** (Deliverable has forward FK;
   lifecycle governed by Deliverable contract). Confirmed at HEAD:
   `Deliverable.self_blog` FK at :192-199 + `Deliverable.podcast_episode`
   FK at :200-207 (Session 862). Two objects fit this category.
2. **Standalone-by-design first-class entities** (independent
   lifecycle; may optionally link to Deliverable later). Likely
   fit at HEAD: `OutreachDraft` + `ClosePack` (revenue-operational
   records with independent status lifecycles + active consumer
   surface within revenue domain). Category assignment PROVISIONAL —
   confirming intent requires a T1 R.CONTENT.VARIANT-CATEGORIZATION-CLARIFICATION
   evidence exercise (§19 T1).
3. **Unfinished / orphan outputs** (write-only-forgotten, no clear
   read-path, no tooling surface, no retention posture). Fit at
   HEAD: `SportsBettingBrief` (S1504 §14.3 CRITICAL pattern
   confirmed) + `BlockchainAuditBrief` (identical pattern class).

**`SelfBlog` is unique** — hybrid case with active read paths (PA
tools + frontend BlogViewerPage + REST endpoints) but 16+ direct
`.objects.create` sites that bypass factory canonicalization.
Category assignment: envelope-integrated per Session 862 FK but
factory-adoption divergent. Cat F S1606 owns categorization
resolution.

At the **factory layer**: 98%+ Deliverable base adoption (2
legitimate production bypasses — `views_deliverables.py:305` clone
+ `workflow_orchestration_agent.py:5107` morning-brief), 0% variant
coverage. Rigby SIGN Batch A flagged `real_job_execution_consumer.py:99`
`create_deliverable` as potential shadow-factory concern; **F1
RESOLVED at parent-Claude direct-read verification**: the method at
`real_job_execution_consumer.py:200` returns plain dicts for demo
WebSocket UI simulation, never touches ORM. **Name collision, not
factory bypass. Factory adoption metric REMAINS ACCURATE.**

Cat F S1606 will consolidate the 3-category taxonomy + factory
adoption evidence into xx99 §5's three-axis Chris-gated decision
brief per D65a/D65b/D65c; Cat D does not select the posture (per
§14.5 no-implementation rule).

**Cat D's second-order finding** — extending S1504 §14.3
WRITE-ONLY-FORGOTTEN pattern class — is that **three of five
variants (`SportsBettingBrief` + `BlockchainAuditBrief` + the
implied SelfBlog side of variant-consumer imbalance) share the
write-only-forgotten pattern**. `ClosePack` alone breaks the
pattern with 30+ reader queries in the revenue domain (Agent 4
sweep). `OutreachDraft` has active status-transition readers
(approval/rejection lifecycle) but **zero delivery** — S1402 F.B1
CONFIRMED at HEAD (`grep send_outreach|dispatch_outreach|sendgrid|
postmark|mailgun|smtplib` returns 0 mainline production hits).

**Cat D's biggest open unknown (UNK-1 §15):** whether the
Session 1248 P2b workaround for `feedback_deliverable_create_defaults_to_completed`
(td_handlers_agents.py :2052 hardcodes `status='completed'`, :2091-2109
comment documents echo-actual-status + opt-in `return_detail=True`
follow-up fetch pattern) fully resolves the memory-rule concern OR
whether the underlying schema-vs-runtime status-value drift remains
live. Cat E S1605 owns final verification via PA-tool contract
sweep; Cat D flags for cross-arc handoff.

**Cat D top-3 future research recommendations** (§19 T-slot ranking):
(T1 R.CONTENT.VARIANT-CANONICALIZATION) run the D65a-decision-brief
integration-vs-island selection post-xx99 as Chris-gated ADR;
(T2 R.CONTENT.DELIVERABLE-FACTORY-VARIANT-EXTENSION) if D65a selects
integration, extend `deliverable_factory` semantics to variants
(introduce polymorphic variant-shim OR mandate all variant creates
go through factory); (T3 R.CONTENT.TRIPLE-GATE-UNIFICATION) resolve
the 5-gate (factory) vs 4-threshold (PublishGate) vs SelfBlog-own-
gate triple-gate architecture identified in §14.3 (parked issue
§6.3 in parent — now with Cat D evidence).

**Rigby SIGN cycle 1 pending at session-close.** Fresh isolation pin
minted at SIGN time per playbook §15; SIGN batches A/B/C per memory
rule `feedback_rigby_sign_worker_instability_recovery.md`. D48
preemptive stability-probe gate 12th arm anticipated. Playbook §14
verifier-loop preserved 22 pre-Explore binary claims + 6 post-Explore
binary claims all grep-verified before draft.

---

## 2. Domain Purpose

**Purpose (playbook §9 Q1).** Cat D owns the **persistence container
layer** of the Content / Deliverables / Publishing domain: the base
`Deliverable` model that acts as an envelope for agent-produced
outputs, the central factory that gates + normalizes + de-duplicates
their creation, and the five parallel-schema-siblings that live
alongside Deliverable with independent lifecycles.

**Problem it solves (playbook §9 Q2).** Before Session 862, agent
outputs were scattered across ad-hoc model rows with no consistent
metadata contract, no dedupe policy, and no provenance chain. The
canonical container (Deliverable) unified quality scoring, workspace
attribution, initiative linkage, and export machinery under a single
schema. Before Session 1169 Layer C Phase 1, quality-gate rejection
was a silent-None return; the typed `DeliverableGatedError` exception
(with structured `reason_code`) resolved that. Before Session 1195
Plan C Phase 1, orphaned deliverables (missing initiative_id or
workspace_mismatch) accumulated silently; the `diagnostic_status` +
TTL sweep introduced auto-archive with grep-friendly `[ORPHAN-DELIVERABLE]`
log line. The **remaining problem Cat D exists to answer** is the
D65a posture question: given that the platform grew *both* a canonical
container *and* five parallel-schema-siblings organically, is that
future-canonical or transitional-drift?

**What Cat D does NOT own** (per parent §3 D F2 fold boundary rule):
- Gates at the boundary (`PublishGate` thresholds) — Cat C S1604.
- Publish rails (Discord broadcast, Newsletter, Frontend
  BlogViewerPage) — Cat C S1604.
- Reviewer verdicts + decision enforcement — Cat B S1602 (owned).
- PA-tool + approval UX surface contracts — Cat E S1605.
- ClaimsPack + Content Deliberation pipeline internals — Cat A
  S1601 (owned).
- Cross-domain posture-decision-brief consolidation — Cat F S1606
  (LAST child).

Cat D answers only "**what IS the object, at what points do
identities converge/diverge, and what is the lifecycle state
machine?**"

---

## 3. Canonical Entry Points

Q3: canonical entry points for Deliverable + variants at HEAD.

### 3.1 Base model

- **`Deliverable`** at `core/models_deliverables.py:84` — 42 core
  fields + 5 Session 1195 diagnostic fields = 47 total. `db_table =
  'core_deliverables'`; 10 indexes at :401-420 including composite
  `['diagnostic_status', 'diagnostic_expires_at']` for daily TTL
  sweep.

### 3.2 Five parallel variants

- **`SelfBlog`** at `core/models_unified_system.py:20611` — content
  pipeline output; status choices `[draft, pending_review,
  needs_enhancement, approved, published]` at :20706; own quality
  gate fields (`quality_score` / `novelty_score` / `structure_score`
  / `publish_ready` / `gate_notes`) at :20708-20728; `stats_snapshot`
  JSONField at :20742 (S1602 §16.1 write target for
  `['deliberation']` packet).
- **`OutreachDraft`** at `core/models_outreach.py:18` — outreach
  variant; status `[draft, approved, rejected, sent, replied,
  expired]` at :86; NO quality-gate fields; FK graph:
  `spider_data_id` (UUIDField, soft), `opportunity`, `parent_draft`
  (self-FK), `user`, `trace_id`.
- **`ClosePack`** at `core/models_close_pack.py:20` — close/revenue
  variant; status `[draft, approved, sent, won, lost, expired]` at
  :74; NO quality-gate fields; FK graph: `opportunity`,
  `outreach_draft`, `user`.
- **`SportsBettingBrief`** at `core/models_unified_system.py:18394`
  — betting analysis variant; NO status field, only `brief_date` +
  `sport_filter`; NO quality-gate fields.
- **`BlockchainAuditBrief`** at `core/models_unified_system.py:18435`
  — blockchain audit variant; NO status field; NO quality-gate
  fields.

### 3.3 Central factory + supporting entry points

- **`create_deliverable`** at `core/services/deliverable_factory.py:752`
  — the canonical creation gateway. Parent §3 D cited `:1269`; that
  is the `Deliverable.objects.create(**kwargs)` call *inside* the
  factory's atomic-transaction block at the tail of the function
  (F0 pre-Explore drift correction — recorded here for §20
  verifier-loop notes).
- **`resolve_publish_intent`** at `deliverable_factory.py:605` —
  Session 1095 explicit-arg → per-agent table → default resolver;
  4 "publishing" agents mapped (`InitiativePipeline`,
  `ContentWriterAgent`, `BlogWriterAgent`, `EditorAgent`) → all
  else `internal_only`.
- **`DeliverableGatedError`** class at `deliverable_factory.py:46-74`
  — typed quality-gate rejection with 5 reason_codes.
- **`DeliverableProvenanceMissingError`** class at
  `deliverable_factory.py:77` — Session 1199 PR-D hard exception
  flip.

### 3.4 Supporting models (Cat D-owned)

- **`DeliverableExport`** at `core/models_deliverables.py:474` — 8
  fields; 5 export_format choices `[pdf, docx, html, markdown,
  json]`; CASCADE on Deliverable delete.
- **`DeliverableCollection`** at `core/models_deliverables.py:525`
  — user-curated M2M grouping; `is_public` flag; distinct from
  `ContentPacket` (see §3.6).
- **`DeliverableEvent`** at `core/models_deliverables.py:561` — 8
  event_type choices including Session 1095 `status_transition`
  written by `core/signals/deliverable_status_signals.py`; consumed
  by Stage 3 Evaluation Dashboard for ATR-24h.
- **`ContentPacket`** at `core/models_deliverables.py:617` — 8
  fields; pipeline-run-scoped; `ContentPacketItem` at :678 with
  10 role choices + unique constraint `(packet, deliverable)` at
  :716.
- **`DeliverableAppend`** at `core/models_deliverable_appends.py:35`
  — Session 1098 streaming idempotency; unique constraint
  `(deliverable, call_id, chunk_index)` at :130-135; status choices
  `[pending, committed, failed, superseded]`.

### 3.5 REST endpoints (Cat D-owned reads/writes)

Deliverable CRUD via `core/views_deliverables.py`:
- `list_deliverables` at :52 (GET); `get_deliverable` at :169;
  `save_deliverable` at :214; `unsave_deliverable` at :267;
  `delete_deliverable` at :250; `clone_deliverable` at :295 (POST —
  factory bypass; see §16.2); `templateize_deliverable` at :350;
  `export_deliverable` at :378; `link_deliverable_workspace` at
  :508; `get_deliverable_stats` at :546; `get_deliverable_types`
  at :648; `record_deliverable_event` at :1018.

SelfBlog CRUD via `core/views_research_demo.py` (routed at
`core/urls.py:3213-3219`):
- `self_blog_api` (POST `/api/v1/research/self-blog/`);
  `self_blog_list_api`; `self_blog_by_id_api`;
  `related_self_blogs_api`.

OutreachDraft CRUD via `core/views_outreach.py` (routed at
`core/urls.py:1817-1821`):
- `outreach_inbox_view`; `outreach_generate_view`;
  `outreach_metrics_view`; `outreach_approve_view`;
  `outreach_reject_view`.

SportsBettingBrief endpoint: `get_betting_brief` at
`core/views_odds_sports.py:3237` (AllowAny) — **bypasses persisted
model + calls `SportsBettingCoordinator.generate_brief()`
transiently** (S1504 §14.3 pattern extension verified at HEAD).

ClosePack REST endpoints: **NONE FOUND** at HEAD (grep-verified).

BlockchainAuditBrief REST endpoints: **NONE FOUND** at HEAD
(grep-verified).

### 3.6 PA tools (Cat D-adjacent — Cat E owns tool-surface contract)

Registered in `core/services/tool_dispatcher.py`:
- `deliverable_tool` at :479 → `_handle_deliverable_direct`
  (`td_handlers_content.py:84`); 18 actions per schema
  `pa_tool_schemas.py:3389-3460`.
- `content_tool` at :476 → `_handle_content_review`
  (`td_handlers_content.py:235`); actions
  `list/stats/details/publish/archive/complete` + Session 1075
  aliases `approve→publish`, `reject→archive`.
- `blog_tool` at :490 → `_handle_blog_direct`
  (`td_handlers_content.py:162`); actions
  `stats/list/detail/search/recent/approve/reject/generate`.
- `newsletter_tool` at :521 → `_handle_newsletter`
  (`td_handlers_newsletter.py:25`); 7 actions per schema
  `pa_tool_schemas.py:3511-3513`.

---

## 4. Major Models

Q4-Q5. Structured inventory follows the 6-sibling exemplar 4-item
pre-brief mini-schema propagation-upfront pattern per parent D68 F8/F10
folds (D62 = (a)) — applied at §4.8, §5.6, §6.5, §8.5.

### 4.1 Deliverable base — 47 fields grouped by function

Field buckets grouped from Agent 1 sweep at
`core/models_deliverables.py:84-393`. Full field list preserved in
sweep artifact; summary here:

- **Identity (5 fields)** — `id` UUIDField PK (:108); `title`
  CharField[255] (:109); `slug` SlugField[280] unique (:113); Session
  843 orchestration trio `trace_id` UUIDField (:151), `parent_object_type`
  CharField[50] (:155), `parent_object_id` UUIDField (:159).
- **Classification (5)** — `deliverable_type` CharField choices
  `[document/image/video/audio/code/analysis/report/template/research/strategy/plan/script]`
  at :120; `publish_intent` CharField choices
  `[internal_only/publish_candidate/publish_required]` default
  `internal_only` at :131 (Session 1095); `category` CharField[100]
  db_index (:137); `tags` ArrayField (:143); `content_format`
  CharField choices `[text/markdown/html/json/python/typescript/javascript]`
  (:240).
- **Lifecycle/status (5)** — `status` CharField choices
  `[draft/ready/published/archived]` default `ready` at :353 (see
  §14.4 for runtime "completed" 5th value discussion); `is_saved`
  (:266); `is_template` (:271); `is_starred` (:276); `is_pinned`
  (:333).
- **Provenance/attribution (8)** — `workspace` FK ProjectWorkspace
  SET_NULL (:165); Session 862 FK trio `initiative`/`dream`/`self_blog`
  (:176-199); `podcast_episode` FK (:200); `source_operation` FK
  WorkspaceOperation (:210); `agent_name` CharField[100] (:218);
  `agent_task` TextField (:223); `user` FK CASCADE (:227).
- **Content (4)** — `content` TextField (:237); `preview_content`
  TextField (:246); `thumbnail_url` URLField (:250); (with
  `content_format` from Classification).
- **Quality (2)** — `quality_score` FloatField (:256);
  `confidence_score` FloatField (:260).
- **Library (3)** — `clone_count` IntegerField (:280); `cloned_from`
  FK self SET_NULL (:284); (with `is_saved`/`is_template` from
  Lifecycle).
- **Execution (4)** — `execution_time_ms` (:294); `llm_cost` Decimal
  (:298); `tool_calls` JSONField list (:304); `raw_output` JSONField
  dict (:308).
- **Metadata (1)** — `metadata` JSONField dict (:314).
- **Sensitivity (2)** — `data_sensitivity` CharField choices
  `[public/internal/confidential/restricted]` (:326 Session G2);
  (with `is_pinned` from Lifecycle).
- **Dedup (1)** — `content_hash` CharField[32] db_index (:339
  Session 325).
- **Session 1195 Plan C Phase 1 diagnostic (5)** —
  `diagnostic_status`, `diagnostic_code`, `diagnostic_payload`,
  `diagnostic_marked_at`, `diagnostic_expires_at` at :370-389.
- **Timestamps (2)** — `created_at` auto_now_add db_index (:392);
  `updated_at` auto_now (:393).

### 4.2 The five parallel variants — comparative shape

| Variant | File:Line | Status field | Own quality gate | Reverse FK to `Deliverable` | `publish_intent` enum | S1504-analog WRITE-ONLY? |
|---------|-----------|--------------|------------------|-----------------------------|-----------------------|-------------------------|
| **`SelfBlog`** | `models_unified_system.py:20611` | 5-value at :20706 | YES (5 fields :20708-20728) | NO | NO | NO (active PA-tool + REST + frontend readers) |
| **`OutreachDraft`** | `models_outreach.py:18` | 6-value at :86 | NO | NO | NO | PARTIAL (28+ status-transition reads; ZERO outbound delivery = S1402 F.B1) |
| **`ClosePack`** | `models_close_pack.py:20` | 6-value at :74 | NO | NO | NO | NO (30+ readers in revenue domain) |
| **`SportsBettingBrief`** | `models_unified_system.py:18394` | none | NO | NO | NO | **YES CRITICAL** (S1504 §14.3 pattern confirmed at HEAD: 2 writers, 0 readers; REST bypasses persisted model) |
| **`BlockchainAuditBrief`** | `models_unified_system.py:18435` | none | NO | NO | NO | **YES CRITICAL** (1 writer, 0 readers — identical S1504-analog dead-code pattern) |

**Row 3 column (reverse FK) is grep-verified negative across `core/`:**
`ForeignKey.*Deliverable` and `ForeignKey('core.Deliverable'` return
zero matches. **All five variants are structural islands relative
to Deliverable base.** The only directed edges are
`Deliverable.self_blog` FK → SelfBlog at :192-199 and
`Deliverable.podcast_episode` FK → PodcastEpisode at :200-207
(Session 862). No variant reciprocates.

**Row 5 column (`publish_intent`):** grep of `publish_intent` in
`core/models_unified_system.py`, `core/models_outreach.py`,
`core/models_close_pack.py` returns **zero matches**. `publish_intent`
enum lives only on `Deliverable` base (`core/models_deliverables.py:131-136`).

### 4.3 Supporting models

| Model | File:Line | Fields | Constraint | Session |
|-------|-----------|--------|------------|---------|
| `DeliverableExport` | `models_deliverables.py:474` | 8 | CASCADE on Deliverable | pre-S843 |
| `DeliverableCollection` | `models_deliverables.py:525` | 7 (+ M2M `deliverables`) | `is_public` flag | pre-S843 |
| `DeliverableEvent` | `models_deliverables.py:561` | 7 | db_index `event_type` + `-created_at` | S1095 added `status_transition` event_type |
| `ContentPacket` | `models_deliverables.py:617` | 8 | pipeline-run scope | pre-S843 |
| `ContentPacketItem` | `models_deliverables.py:678` | 7 | unique `(packet, deliverable)` at :716 | pre-S843 |
| `DeliverableAppend` | `models_deliverable_appends.py:35` | 13 | unique `(deliverable, call_id, chunk_index)` at :130 | S1098 streaming idempotency |

### 4.4 Enum classes (top-of-file)

At `core/models_deliverables.py` above line 84:
- `DeliverableType` (:31-45) — 12 values
  `[DOCUMENT/IMAGE/VIDEO/AUDIO/CODE/ANALYSIS/REPORT/TEMPLATE/RESEARCH/STRATEGY/PLAN/SCRIPT]`
  (verified via `grep deliverable_type` at :102, :120, :403, :436).
- `ContentFormat` (:47-56) — 7 values
  `[TEXT/MARKDOWN/HTML/JSON/PYTHON/TYPESCRIPT/JAVASCRIPT]`.
- `PublishIntent` (:58-82) — 3 values
  `[INTERNAL_ONLY/PUBLISH_CANDIDATE/PUBLISH_REQUIRED]`.

### 4.5 Identity + dedup + merge policy

- **Slug uniqueness** — enforced via `unique=True` on the field at
  :114; `save()` auto-generates from `slugify(title)` at :439-448
  with counter-suffix collision resolution.
- **`content_hash`** — computed at `_content_hash` factory helper
  (:119-125 of deliverable_factory.py): `SHA256(normalize(title) +
  normalize(content[:2000]) + normalize(agent_name))` truncated to
  32 hex chars.
- **72h content-hash dedup query** — factory :955-970 (**F0b
  post-Explore correction: this is NOT dead-write; the factory
  actively queries `Deliverable.objects.filter(content_hash=c_hash,
  created_at__gte=hash_window).order_by('-created_at').first()` and
  returns the existing row on match**). This preserves the dedup
  contract for scheduled-task-produced identical content.
- **4h title dedup query** — factory :934-953 (same agent + same
  title within 4h → return existing).
- **Provenance-parent dedup query** — factory :906-927 (same
  `parent_object_type + parent_object_id` → return existing).
- **Trace-id provenance** — `trace_id` UUIDField at :151 db_indexed
  for cross-artifact linking (Session 843); `parent_object_type` +
  `parent_object_id` soft-FK pattern (:155-162) — parent §3 D
  noted; grep confirms `parent_object_type='conversation'` used
  live at `conversation_deliverable_extractor.py:385` and
  `conversation_initiative_pipeline.py:565`.
- **Clone chain** — `cloned_from` self-FK at :284; `clone_count`
  IntegerField at :280 incremented at `views_deliverables.py:331`.
- **Explicit merge helpers** — NONE FOUND at HEAD (grep-verified in
  `core/services/` and `core/admin*.py`).

### 4.6 Migration lineage (recent 5)

`ls -la core/migrations/ | grep -i deliverable` at HEAD:
1. `0360_session_1195_deliverable_diagnostic_fields.py` (2026-06-21) — adds Session 1195 Plan C Phase 1 diagnostic fields + composite sweep index.
2. `0337_deliverable_appends.py` (2026-04-17) — creates DeliverableAppend model + unique constraint.
3. `0333_add_deliverable_publish_intent.py` (2026-04-17) — adds `publish_intent` enum field + db_index; Session 1095 backfill sets 122 rows to `INTERNAL_ONLY` default.
4. `0325_deliverable_content_hash.py` (2026-04-08) — adds `content_hash` CharField + db_index.
5. `0309_deliverable_workspace_fk.py` (2026-03-16) — adds workspace FK.

### 4.7 Docstring vs code alignment (drift check)

`Deliverable` base docstring at :85-105 claims:
- ✅ "consistent metadata" — title, type, category, tags all present
- ✅ "quality metrics" — quality_score, confidence_score present
- ✅ "library features" — is_saved / is_template / cloned_from / clones present
- ✅ "export capabilities" — DeliverableExport model exists
- ✅ "developer traceability" — tool_calls JSONField, raw_output JSONField present

No docstring drift on Deliverable base. Compare with S1403 F.C4
ContentEngagement docstring drift precedent — Cat D's Deliverable
docstring is faithful to runtime.

### 4.8 Pre-brief mini-schema (D62 = (a) 6-sibling exemplar applied)

Following S1504 §4.4 exemplar template (adopted per S1599 §10.2
codify-ready + parent D68 F8/F10 folds), this section pre-briefs the
4 axes of Cat D's evidence surface upfront so that Cat A/B/C/E/F
siblings + xx99 can consume consistently.

| Axis | Layer | Cat D-owned scope | Cross-arc consumer |
|------|-------|--------------------|--------------------|
| **A1 — Deliverable canonicalization scope** | Structural (models + FKs) | ALL 5 variants ISLAND at reverse-FK layer (grep-verified). Only uni-directional `Deliverable → SelfBlog` + `Deliverable → PodcastEpisode`. | xx99 D65a evidence: **island posture confirmed at structural layer**. |
| **A2 — PublishGate canonicalization scope** | Behavioural (gates) | Cat D flags but does NOT own: 5-gate factory + 4-threshold PublishGate + SelfBlog own quality fields = triple-gate architecture. | Cat C S1604 owns resolution. Cat D contributes evidence to xx99 D65b. |
| **A3 — Central factory scope** | Behavioural (creation) | `create_deliverable` at :752 is canonical; 2 legitimate production bypasses (clone view + WorkflowOrchestrationAgent); ZERO variant models use factory. | xx99 D65c: **integration posture at Deliverable factory layer; island posture at variant creation layer**. |
| **A4 — `publish_intent` enum coverage** | Structural (schema surface) | Only on Deliverable base :131-136. Zero grep hits in variant model files. | xx99 D65a: **structural blocker for integration posture without variant schema extension**. |

---

## 5. Major Services

Q5 continued. Runtime flow at §7; service inventory here.

### 5.1 `core/services/deliverable_factory.py` (1,455 lines, WITHIN god-service threshold)

Top-level exports (Agent 2 sweep verified):
- Exception classes: `DeliverableGatedError` (:46), `DeliverableProvenanceMissingError` (:77).
- Content processing: `_content_hash` (:119), `_normalize_whitespace` (:247), `_truncate_at_word` (:252), `_looks_like_prompt_body` (:267), `build_semantic_research_title` (:273).
- Quality + title: `_should_create_deliverable` (:358 — 5 gates), `_detect_blocked_content` (:416), `_clean_deliverable_title` (:468).
- Publish intent: `resolve_publish_intent` (:605).
- Provenance: `_resolve_caller_fingerprint` (:649), `_is_pa_direct_context` (:668), `_synthesize_pa_execution_receipt` (:676).
- **Core factory** (canonical creation gateway): `create_deliverable` (:752).
- Workspace helpers: `_get_default_user` (:1317), `_get_or_create_unassigned_workspace_id` (:1334), `_get_active_workspace_id` (:1428).
- Initiative alignment: `_evaluate_initiative_alignment` (:1377).

### 5.2 `core/services/content_deliberation_runner.py` (v2 canonical dispatch)

Owned by Cat A S1601 but Cat D flag: **`SelfBlog.objects.create` at
:401** with `stats_snapshot={'deliberation': deliberation_meta}` at
:415. Verified at HEAD (grep + direct read). This is the D65a
HEADLINE evidence input — Cat A pipeline creates SelfBlog directly
without going through Deliverable factory canonicalization. S1601
§9.1 handoff CONFIRMED.

### 5.3 `core/signals/deliverable_status_signals.py` (242 lines)

Two Django signal handlers on Deliverable (Agent 2 sweep):
- `stash_prior_status` at :111 — `@receiver(pre_save,
  sender='core.Deliverable')` caches old status on
  `instance._prior_status` before save.
- `record_status_transition` at :133 — `@receiver(post_save,
  sender='core.Deliverable')` writes DeliverableEvent row for
  status transitions; classifies transition via `classify_transition`
  at :83 (forward / backward / same / unknown). Session 1252 PR 2
  whitelist keys `[reason, actor_user_id, trace_id, source,
  ops_run_id, error_signature]` from ephemeral
  `instance._transition_context`. Session 1250 PR 5 enqueues Rigby
  Event Intake if `settings.RIGBY_EVENT_INTAKE_ENABLED` (default
  False).

Both handlers connected via `core/signals/__init__.py:31-35`
called from AppConfig.ready(). Defensive: neither breaks save on
signal exception.

### 5.4 `core/services/deliverable_append_service.py` (Session 1098 streaming)

DeliverableAppend write handler (called from PA-tool append action).
Session 1098 streaming idempotency at
`services/deliverable_append_service.py:214`. Contract not deep-dived
here — Cat E owns tool-surface contract; Cat D owns model + unique
constraint.

### 5.4a Cat D-adjacent lifecycle/identity services (F2 Rigby fold)

Rigby SIGN Batch A surfaced additional Cat D-adjacent services that
encode object-shape, identity, or lifecycle semantics — not model
files, but load-bearing for "what IS a Deliverable at the boundary
of persistence":

- **`core/services/deliverable_envelope.py`** — Deliverable envelope
  contract service; wraps ORM writes with envelope metadata semantics.
- **`core/services/conversation_deliverable_extractor.py`** —
  extracts Deliverable rows from conversation surfaces; uses
  `parent_object_type='conversation'` soft-FK (verified at :385).
- **`core/services/platform_event_view.py`** — Deliverable-adjacent
  event surface; interacts with DeliverableEvent stream.
- **`core/deliverables_consumer.py`** — WebSocket consumer for
  deliverable-shaped async messages.

**NOT Cat D-adjacent (F1 Rigby fold RESOLVED):**
`core/real_job_execution_consumer.py:200` has an `async def
create_deliverable(self, job)` method that shares the name of
`deliverable_factory.create_deliverable` but returns a **plain
Python dict** (`{"job_id": ..., "job_title": ..., "status":
"completed", ...}`) for demo WebSocket UI simulation. It never
touches the Django ORM and never persists a Deliverable row. This
is a **name collision, not a shadow factory bypass** — verified via
direct-read of the method body at :200-237. Factory adoption metric
of 98%+ REMAINS ACCURATE.

### 5.5 God-service check

Line counts at HEAD for top files involved in Deliverable
creation/lifecycle (Agent 2 verified):

| File | Lines | God-service flag (>3000) | Cat D relevance |
|------|-------|--------------------------|-----------------|
| `core/tasks.py` | 13,470 | **YES** | Multiple beat entries touching Deliverable/variants; not Cat D-owned refactoring scope |
| `core/services/discord_bot.py` | 11,677 | **YES** | Discord broadcast at Cat C boundary; not Cat D |
| `core/services/workflow_orchestration_agent.py` | 5,424 | **YES** | Contains factory-bypass at :5107 (see §16.2) |
| `core/tasks_content.py` | 4,418 | **YES** | Content pipeline + SelfBlog writes; not Cat D refactoring scope |
| `core/services/deliverable_factory.py` | 1,455 | NO (well within) | **Cat D-primary — scoped and focused** |

Cat D-primary factory is well within the god-service threshold. The
4 god-services are Cat A/B/C/E-adjacent — not Cat D remediation
targets.

### 5.6 Pre-brief mini-schema — Factory branches (D62 = (a))

25-branch flow through `create_deliverable` (:752-1314) grouped for
Cat A/B/C/E/F consumption:

| Branch | Line range | Purpose | Cross-arc consumer |
|--------|------------|---------|--------------------|
| Agent canonicalization | :806 | Session 1226 P1 `_canonicalize_agent_name` | Cat B verdict recording |
| Gate check (5 gates) | :838-853 | 5-gate + `DeliverableGatedError` | Cat B/C boundary |
| Workspace validation | :876-901 | S1206 B2 pre-write validate | Cat E workspace-parity |
| Provenance dedupe | :906-927 | Same parent_object → return existing | Cat A pipeline idempotency |
| Title dedupe (4h) | :934-953 | Same agent+title → return existing | Cat A/E |
| Content-hash dedupe (72h) | :955-970 | `content_hash` filter query | Cat A pipeline idempotency |
| User + workspace auto-assign | :973-1007 | S1091 sentinel Unassigned | Cat E orphan handling |
| Trigger-source inference | :1009-1021 | metadata.trigger_source | Cat E |
| Provenance receipt / raise | :1029-1063 | Session 1199 PR-D hard exception | Cat B agent-dispatch contract |
| BLOCKED detection + status override | :1065-1073 | S1206 B3 status='blocked' | Cat B/C |
| Title cleaning | :1077 | 26 prefix + 13 verbs + 7 instruction patterns | Cat E UX |
| Slug generation | :1083-1087 | base_slug-{uuid8} | — |
| Initiative inference | :1108-1138 | S1198 §6.2 + S1199 tool_context | Cat E |
| Kwargs build + publish_intent resolve | :1141-1159 | `resolve_publish_intent` | Cat C PublishGate consumption |
| Initiative validation | :1178-1205 | Drop link + WARN if not found | Cat E |
| Orphan diagnostic marking | :1221-1246 | S1195 Plan C Phase 1 TTL | Cat E orphan sweep |
| content_hash storage | :1248-1250 | `kwargs['content_hash']` | Cat D dedup (§4.5) |
| Atomic create | :1268-1269 | `Deliverable.objects.create(**kwargs)` | — |
| Post-create logging | :1270-1275 | `[DeliverableFactory] Created` | Cat E observability |
| Orphan diagnostic emission | :1278-1307 | `[ORPHAN-DELIVERABLE]` WARN | Cat E monitoring |

---

## 6. Major APIs and Interfaces

Q6. Full surface inventory from Agent 3 sweep.

### 6.1 REST endpoints — already inventoried in §3.5

Twelve Deliverable CRUD endpoints (`core/views_deliverables.py`),
four SelfBlog endpoints (`core/views_research_demo.py`), five
OutreachDraft endpoints (`core/views_outreach.py`), one bypassing
SportsBettingBrief endpoint (`core/views_odds_sports.py:3237`),
zero ClosePack REST endpoints, zero BlockchainAuditBrief REST
endpoints.

### 6.2 PA tool schemas + handlers — already inventoried in §3.6

18-action `deliverable_tool`, 6+aliases `content_tool`, 8-action
`blog_tool`, 7-action `newsletter_tool`. Full mappings in §3.6.

### 6.3 Frontend consumers (boundary confirmation only; Cat E owns)

- **`frontend/src/pages/BlogViewerPage.tsx:45`** reads
  `/api/v1/research/self-blog/{blogId}/` — verified.
- **`frontend/src/lib/api.ts:3921-3962`** `blogsApi` with
  `list/get/delete/approve/publish/related` — approve/publish
  mutations verified at :3931-3940.
- Multiple frontend consumers reference `deliverable*` per Agent 4
  sweep; Cat E S1605 owns.

### 6.4 Rigby memory-rule cross-references (Cat D-owned tool-side drift)

Grep-verified against HEAD:
- **`feedback_deliverable_create_defaults_to_completed.md`** —
  `td_handlers_agents.py:2052` hardcodes `status='completed'`
  (verified). :2091-2109 comment (Session 1248 P2b) documents the
  workaround: (i) always echo actual stored `status` as top-level
  field (BC-safe); (ii) opt-in `return_detail=True` triggers
  follow-up detail fetch. **Partially-resolved via workaround, not
  underlying fix.** Cat E owns underlying schema/runtime drift
  resolution.
- **`feedback_deliverable_status_via_content_complete.md`** —
  verified. `content_tool.content_complete` at
  `td_handlers_content.py:260-267` (alias table) is the canonical
  status→completed path; `deliverable_tool.update` silently drops
  status changes.
- **`feedback_deliverable_tool_use_append_for_large_payloads.md`**
  — payload size threshold ~6-7kB. UNKNOWN if implementation
  branches on size or if it's a silent fallback bug. Cat E S1605
  scope.
- **`feedback_publish_intent_enum.md`** (Session 1094 Rigby
  architectural guidance) — enum implementation verified at
  Deliverable :131-136. Only on base; NOT on variants (§4.2 A4
  axis).
- **`feedback_deliverable_workspace.md`** — Deliverable has
  workspace FK; variant workspace FK coverage varies (SelfBlog has
  workspace FK; SportsBettingBrief + BlockchainAuditBrief lack
  workspace attribution entirely).

### 6.5 Pre-brief mini-schema — `deliverable_tool` 18 actions (D62 = (a))

Per `pa_tool_schemas.py:3389-3460` + Session 1248 workaround comments:

| Action | Bucket | Cat D relevance | Cross-arc consumer |
|--------|--------|-----------------|--------------------|
| `list` / `search` / `detail` / `stats` | Read | Reads Deliverable table via ORM | Cat E UX + observability |
| `create` | Write | Routes through factory (:2015+ in td_handlers_agents.py) | Cat D-canonical |
| `update` / `append` | Write | S1176 memory-rule: `append` for >6kB payloads | Cat E S1605 open |
| `save` / `unsave` | State | is_saved boolean toggle | Cat E UX |
| `set_status` (S1248 P2b) | State | Surgical status flip completed↔ready with reason | Cat E S1605 |
| `duplicates` | Audit | Groups by (agent_name / title / trace_id) | Cat E ops |
| `normalize` | Migrate | Session 1226 P1 dry-run alias-map canonicalization | Cat D + Cat E |
| `export_pdf` | Publish rail | Cat C S1604 boundary | Cat C |
| `bulk_archive` | State | dry_run=true default; requires confirm=true | Cat E |
| `link_initiative` / `unlink_initiative` | Provenance | Session 862 initiative FK write | Initiative pipeline |
| `has_initiative` / `orphans` (filters) | Read | Boolean filters — see `feedback_llm_autofills_boolean_params_with_false.md` memory rule (Session 1227) | Cat E |
| `show_all` (flag) | Read | Bypass autofill | Cat E |

---

## 7. Runtime Flows

Q9. Cat D flows.

### 7.1 Canonical Deliverable creation (via factory)

Step-by-step from agent output arriving at `create_deliverable`
through to persisted row (numbers = deliverable_factory.py line).

1. **Entry** at :752 with kwargs (title, content, agent_name, +
   options).
2. Agent canonicalization at :806.
3. Factory-entry instrumentation log `[DELIVERABLE-FACTORY-ENTRY]`
   at :821-835.
4. 5-gate check at :838-853 via `_should_create_deliverable` (:358).
   Reject → `DeliverableGatedError` (:46) if `raise_on_gated=True`;
   else return None (legacy contract, Session 1169 Layer C Phase 1
   Phase 2 migrations still in flight).
5. Workspace validation at :876-901 (S1206 B2).
6. Provenance dedupe query at :906-927 (parent_object match →
   idempotent return + optional content update).
7. Title dedupe query at :934-953 (4h window).
8. Content-hash dedupe query at :955-970 (72h window). **F0b
   correction: this is queried, not dead-write.**
9. User auto-assign at :973-974 if none passed.
10. Workspace auto-assign at :980-1007 (active → Unassigned
    sentinel fallback).
11. Trigger-source inference at :1009-1021.
12. Provenance receipt: at :1029-1063 either synthesize PA-direct
    AgentExecution receipt (Session 1184 PR-B) or raise
    `DeliverableProvenanceMissingError` (Session 1199 PR-D hard
    exception flip).
13. BLOCKED content detection at :1065-1073; status='blocked' if
    detected.
14. Title cleaning at :1077 via `_clean_deliverable_title` (:468).
15. Slug generation at :1083-1087.
16. Initiative inference at :1108-1138 (read-only, best-effort).
17. Kwargs build + publish_intent resolution at :1141-1159 via
    `resolve_publish_intent` (:605).
18. Initiative validation at :1178-1205.
19. Orphan diagnostic marking at :1221-1246 via
    `_evaluate_initiative_alignment` (:1377) + Session 1195 TTL.
20. content_hash storage at :1248-1250.
21. **Atomic create** at :1268-1269:
    `Deliverable.objects.create(**kwargs)` inside
    `transaction.atomic()`.
22. Post-create logging at :1270-1275.
23. Diagnostic emission `[ORPHAN-DELIVERABLE]` WARN at :1278-1307
    if diagnostic flagged.
24. Signal fires: `stash_prior_status` (pre_save, cached) +
    `record_status_transition` (post_save, DeliverableEvent write).
25. Return persisted `Deliverable` instance.

### 7.2 Variant creation flows (all bypass factory)

**SelfBlog canonical path** —
`content_deliberation_runner.py:401` (Cat A owns pipeline; Cat D
flags the bypass at Cat D scope).
```
Phase 4 SelfBlog write:
  SelfBlog.objects.create(
    title=..., author='ContentDeliberation',
    category='blog', content_type=..., status=...,
    gate_notes=..., meta_description=..., intro=...,
    sections=..., conclusion=..., tags=...,
    full_text=..., tone=..., stats_snapshot={'deliberation': deliberation_meta}
  )
```
No factory gates applied. No `publish_intent` set. No `content_hash`
computed. Independent quality-gate fields set from Cat C
PublishGate output on the SelfBlog model. **This is the D65a
HEADLINE evidence input.**

**SportsBettingBrief** — 2 writer sites (Cat D shim
`tasks_content.py:3150` + Session 1000 multi-desk `tasks.py:12187`).
0 readers (S1504 §14.3 CRITICAL CONFIRMED at HEAD). REST endpoint
`get_betting_brief` at `views_odds_sports.py:3237` bypasses persisted
model.

**BlockchainAuditBrief** — 1 writer at `tasks.py:12240`. 0 readers.
Same dead-code pattern as SportsBettingBrief.

**OutreachDraft** — 4 writer sites (2 tests + 2 production at
`services/ops_autopilot/outreach_generation.py:491` + `revenue.py:812`).
28+ status-transition readers (Agent 4 sweep). But ZERO outbound
delivery: `grep send_outreach|dispatch_outreach|sendgrid|postmark|
mailgun|smtplib` returns 0 mainline production hits. **S1402 F.B1
CONFIRMED at HEAD as extension of S1402 pattern.**

**ClosePack** — 1 writer at `services/ops_autopilot/revenue.py:991`.
30+ readers in revenue domain (`revenue.py:1018/1040/1115/1119/…`
per Agent 4). **Structurally an island BUT healthy consumer ratio**
— unique among the five variants.

### 7.3 Cat D-relevant Celery tasks + beat

From Agent 3 sweep at `core/tasks.py` + `core/tasks_content.py`:

- `sweep_diagnostic_deliverables` at :707 — daily TTL sweep flipping
  `diagnostic_status='diagnostic'` rows with expired TTL to
  `status='archived'` (Session 1195 Plan C Phase 1).
- `auto_archive_stale_deliverables` at :11749 — 3-day default
  archive.
- `check_orphan_deliverables` at :11756 — orphan monitoring.
- `score_unscored_deliverables` at :8202 — quality-scoring backfill
  (Session 1033).
- `sweep_selfblog_dry_run` (referenced in inventory) — SelfBlog
  publishing dry-run sweep.

Beat entries at `core/celery.py` involving content/variants: 5+
including `generate-operator-edge-newsletter` (Fri 06:00 Denver
`content` queue), `generate-outreach-drafts-daily`,
`cleanup-stale-content`, `cleanup-boardroom-junk`,
`cleanup-junk-initiatives`. Beat cadence not deep-inventoried
(Agent 3 report marked "cadence/queue/dry_run defaults TBD"); Cat E
S1605 or ops-oriented Cat E follow-on may consolidate.

### 7.4 Management commands (Cat D-scoped)

Per Agent 3 + F3 Rigby fold sweep:

**Deliverable-lifecycle commands:**
- `audit_deliverable_endpoints.py` — S1194 AC1 drift audit.
- `backfill_deliverable_initiative_links.py` — S1196.
- `backfill_deliverable_workspaces.py` — orphan → workspace.
- `backfill_deliverables.py` — obsolete feature audit.
- `cleanup_content_quality.py`.
- `fix_selfblog_categories.py`.
- `fix_workspace_deliverables.py`.
- `produce_content.py`.
- `sweep_diagnostic_deliverables.py`.
- `write_self_blog.py` — meta: system writes about itself.

**Factory-adopter commands (F3 Rigby fold — Cat D-adjacent
ingestion points that create Deliverables via the canonical
factory; add to factory adoption count):**
- `register_external_repo.py` — external repo intake creates
  Deliverable.
- `import_patent_disclosures.py` — patent disclosure ingestion
  creates Deliverable.
- `refresh_repo_context.py` — repo-context refresh writes
  Deliverable.
- `draft_repo_verifier_claims.py` — repo-verifier claims writes
  Deliverable.
- `survey_external_repo.py` — external repo survey writes
  Deliverable.

These 5 mgmt commands + factory-adopter services
(`core/tasks_content.py`, `core/views_workspace_templates.py:315`,
`core/models_document_registry.py`, `core/agents/base_agent.py`,
`core/agents/workflow_agent.py`) collectively confirm factory
adoption is **broad and healthy** — not concentrated in a small
number of callers. Factory metric 98%+ REMAINS ACCURATE with
broader corroboration.

---

## 8. Data Ownership and Lifecycle

Q16-Q18. Data-ownership per model + lifecycle state machine.

### 8.1 Data owned exclusively by Cat D

- **Deliverable base** — all 47 fields.
- **Supporting models** — DeliverableExport (474), DeliverableCollection
  (525), DeliverableEvent (561), ContentPacket (617),
  ContentPacketItem (678), DeliverableAppend (35).
- **DeliverableGatedError + DeliverableProvenanceMissingError**
  contract exceptions.
- **`create_deliverable` central factory** — the 25-branch flow at
  §5.6.
- **`_content_hash` + `_clean_deliverable_title` +
  `build_semantic_research_title` + `resolve_publish_intent`** —
  the normalization + dedup + intent-resolution logic.
- **Django signals** on Deliverable — `stash_prior_status`,
  `record_status_transition`.

### 8.2 Data consumed by Cat D (from other domains)

- `ProjectWorkspace` (from Workspace domain) — Deliverable FK at
  :165.
- `Initiative` (from Initiative pipeline) — Deliverable FK at :176
  Session 862.
- `AgentDream` (from Dreams pipeline) — Deliverable FK at :184
  Session 862.
- `PodcastEpisode` (from Podcast studio) — Deliverable FK at :200
  Session 862.
- `WorkspaceOperation` (from Workspace domain) — Deliverable FK at
  :210.
- `AgentExecution` (from agent-dispatch) — soft FK via
  `parent_object_type='agent_execution'` + `parent_object_id`
  (Session 843).
- `UnifiedUser` (from auth) — Deliverable FK at :227.

### 8.3 Data produced by Cat D (for other domains)

- Deliverable rows consumed by:
  - Cat C S1604 (PublishGate reads for gating).
  - Cat E S1605 (PA-tool `deliverable_tool.list/detail/…`).
  - Frontend `DeliverablesPage`, `DeliverablesTable`.
  - Session 1195 diagnostic sweep beat task.
- DeliverableEvent rows consumed by:
  - Stage 3 Evaluation Dashboard (ATR-24h).
  - Session 1250 PR 5 Rigby Event Intake (opt-in).
- DeliverableAppend rows consumed by:
  - PA-tool streaming path.

### 8.4 Lifecycle state machine

Deliverable `status` field (choices `[draft, ready, published,
archived]` at :353-358, default `ready`) + Session 1206 B3 sentinel
`status='blocked'` at factory :1256 + Session 1248 P2b PA-tool
`status='completed'` written by td_handlers_agents.py:2052 (5th
runtime value not declared in model choices — see §14.4).

Canonical transitions (per Session 1095 + Session 1252 whitelist):
- `draft → ready` (author confirms; PA `set_status`).
- `ready → published` (Cat C publish rail action).
- `ready → blocked` (Cat B review flag; factory sentinel).
- `published → ready` (bounce-back for edits).
- `any → archived` (Session 1195 TTL sweep OR manual).
- `any → completed` (PA-tool workaround per §14.4).

DeliverableEvent `status_transition` rows carry
`metadata={from, to, direction, reason, actor_user_id, trace_id,
source, ops_run_id, error_signature}` (whitelist from Session 1252
PR 2).

Variant lifecycles are independent per §4.2 status column. No
canonical cross-variant state machine exists.

### 8.5 Pre-brief mini-schema — Lifecycle stages (D62 = (a))

Extending parent S1600 F7 fold (10→12-stage Deliverable Lifecycle
Traceability Table) applied per Cat D scope:

| Stage | Owner | Cat D role | Cross-arc handoff |
|-------|-------|------------|--------------------|
| **1. Trigger** | Caller (agent / PA / task) | Cat D receives kwargs | — |
| **2. Normalization** | Cat D (`_clean_deliverable_title`, `_normalize_whitespace`) | Owned | — |
| **3. Gate** | Cat D (5-gate) | Owned | Cat B reviewer input |
| **4. Provenance-attach** | Cat D (`_synthesize_pa_execution_receipt` OR raise) | Owned | — |
| **5. Dedup** | Cat D (3 dedup queries: parent / title-4h / content-hash-72h) | Owned | — |
| **6. Initiative alignment** | Cat D (`_evaluate_initiative_alignment`) | Owned | Initiative pipeline |
| **7. Persist (canonicalization)** | Cat D (`Deliverable.objects.create`) | Owned | — |
| **8. Signal fan-out** | Cat D (Django signals) | Owned | DeliverableEvent, Rigby Intake |
| **9. Publish-eligibility (packaging-gate)** | Cat C S1604 | Cat D contributes `publish_intent` value | Cat C reads |
| **10. Publish (external rails)** | Cat C S1604 | Cat D observes | Discord, Newsletter, Frontend |
| **11. Post-publish state** | Cat C S1604 | Cat D writes status transition | — |
| **12. Archive / TTL** | Cat D (Session 1195 sweep) | Owned | Session 1195 beat |

Boundary rule (per parent F2 fold): stages 1-8 + 12 are Cat D-owned;
stages 9-11 are Cat C-owned; Cat D contributes `publish_intent`
enum value as input to Cat C.

---

## 9. Integrations With Other Domains

Q14, Q17, Q18, Q21, Q22. Integration edge table from Agent 4 sweep.

| Source → Target | FK type | Direction | Strength | Consumer count | Evidence |
|-----------------|---------|-----------|----------|----------------|----------|
| Deliverable → Workspace | Hard FK SET_NULL | Deliv→WS | **WEAK** | ~27 `.deliverables` reverse refs, low query volume | :165-173; Session 862 |
| Deliverable → Initiative | Hard FK SET_NULL | Deliv→Init | **STRONG** | 4 consumers; Session 1195 sweep indexes it | :176-183 Session 862 |
| Deliverable → AgentDream | Hard FK SET_NULL | Deliv→Dream | **WEAK** | 0 consumers found | :184-191 Session 862 |
| Deliverable → SelfBlog | Hard FK SET_NULL | Deliv→SB (uni) | **STRONG (uni)** | 1 read via td_handlers_content.py:519 as deliverable_id proxy | :192-199 Session 862; **NO reverse FK from SelfBlog** |
| Deliverable → PodcastEpisode | Hard FK SET_NULL | Deliv→PE | **WEAK** | 0 consumers | :200-207 Session 862 |
| Deliverable → WorkspaceOperation | Hard FK SET_NULL | Deliv→Op | **WEAK** | 0 consumers via reverse | :210-217 |
| Deliverable → AgentExecution | Soft FK (str+UUID) | Deliv→Exec | **STRONG** | 3+ test consumers via `parent_object_type` (Session 843) | :151-162 |
| Deliverable → User | Hard FK CASCADE | Deliv→User | **STRONG** | 20+ queries platform-wide | :227-234 |
| **SelfBlog → Deliverable (reverse)** | **NONE** | **MISSING** | **MISSING** | 0 (grep-negative) | **D65a HEADLINE** |
| **OutreachDraft → Deliverable** | NONE | MISSING | MISSING | 0 | D65a evidence |
| **ClosePack → Deliverable** | NONE | MISSING | MISSING | 0 | D65a evidence |
| **SportsBettingBrief → Deliverable** | NONE | MISSING | MISSING | 0 | D65a evidence |
| **BlockchainAuditBrief → Deliverable** | NONE | MISSING | MISSING | 0 | D65a evidence |
| SelfBlog → Initiative | Hard FK SET_NULL | SB→Init | **STRONG (variant)** | Session 862 pattern replicated | `models_unified_system.py:20668-20675` |
| SelfBlog → Dream | Hard FK SET_NULL | SB→Dream | WEAK | — | `models_unified_system.py:20676-20683` |

**Cross-arc integration verifications at HEAD:**

- **S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN** —
  CONFIRMED. 2 writers, 0 readers. Grep of
  `SportsBettingBrief\.objects\.\(?filter\|get\|first\|last\|latest\)`
  returns empty.
- **S1402 F.B1 OutreachDraft delivery MISSING** — CONFIRMED at
  HEAD. Grep of `send_outreach|dispatch_outreach|sendgrid|postmark|
  mailgun|smtplib` returns 0 production hits.
- **S1403 F.C4 ContentEngagement docstring drift** — CONFIRMED at
  HEAD. `ContentEngagement` at `models_pipeline_feedback.py:370-449`
  FKs to `AISeries`, `SeriesEpisode`, `ContentPackage` only —
  **zero FK to Deliverable, SelfBlog, or AgentPerformance**.
  Docstring claim of "closes learning loop" not implementable via
  current schema.
- **`publish_intent` variant coverage** — MISSING. Enum only on
  Deliverable base :131-136.

Integration strength summary (Cat D perspective):
- STRONG: 4 (Initiative, AgentExecution-soft, User, SelfBlog uni-dir)
- WEAK: 5 (Dream, PodcastEpisode, WorkspaceOperation, SelfBlog-Dream, Workspace)
- MISSING: 5 (reverse FKs from all 5 variants back to Deliverable)
- UNKNOWN: 0 (all integrations grep-verified)

---

## 10. Event Flows

Q19, Q20.

### 10.1 Events emitted by Cat D

- **DeliverableEvent `status_transition`** (Session 1095) — written
  by `record_status_transition` signal handler at
  `deliverable_status_signals.py:133`. Metadata whitelist per
  Session 1252 PR 2. Consumed by Stage 3 Evaluation Dashboard
  (ATR-24h) + optional Rigby Event Intake (Session 1250 PR 5).
- **DeliverableEvent `deliverable_saved`** — written from
  `save_deliverable` view at `views_deliverables.py:214`.
- **DeliverableEvent `deliverable_exported`** — written from
  `export_deliverable` view at :378.
- **DeliverableEvent `synthesis_viewed` / `shared` / `task_created`
  / `followup_created` / `action_taken`** — written from various
  read/interaction paths (see :569-581 enum).
- **`[ORPHAN-DELIVERABLE]`** structured log line at factory
  :1278-1307 (Session 1195 grep-friendly telemetry).
- **`[DELIVERABLE-FACTORY-ENTRY]`** structured log line at factory
  :821-835 (S1226 observability).
- **`[INFERENCE-MATCH]`** log line at factory :1108-1138 (Session
  1198 §6.2 initiative-inference observability).

### 10.2 Events Cat D SHOULD emit (gaps per S1274 §6)

- **Variant creation events** — currently only base Deliverable
  writes to DeliverableEvent. Five variants have zero event
  fan-out. **Gap for D65a integration posture:** under integration,
  variant creations should be observable via unified event stream.
- **Variant status transitions** — same gap for status transitions
  on OutreachDraft (approve→reject→sent→replied), ClosePack (won→lost),
  SelfBlog (draft→approved). Currently only Deliverable base tracks
  transitions.

---

## 11. Existing Documentation

Q10. Documentation coverage from Agent 5 sweep.

### 11.1 Topic docs

- `docs/topics/content-pipeline.md` (Session 1147) — **v2 pipeline
  + SelfBlog-centric**; does NOT cover Deliverable base schema,
  variant enumeration, or lifecycle. Drift-flagged.
- `docs/topics/personal-assistant.md` — likely covers
  `deliverable_tool`; not deep-read this sweep.
- `docs/topics/initiative-pipeline.md` — Initiative FK chain to
  Deliverable per Session 862 handoff.
- **GAP:** no dedicated `docs/topics/deliverable-subsystem.md` or
  equivalent primer covering Deliverable + 5 variants + lifecycle.

### 11.2 DATABASE_MODEL_REFERENCE.md coverage

- `SelfBlog` at line 337 — model name + 549 records; **no field
  table**.
- **No Deliverable entry, no OutreachDraft, no ClosePack, no
  SportsBettingBrief, no BlockchainAuditBrief entries.** Reference
  doc is a Session 737/1012 snapshot; not refreshed for Cat D
  scope.

### 11.3 Session handoffs bearing on Cat D

- **Session 843** — Orchestration Contract (`trace_id` +
  `parent_object_type` + `parent_object_id`).
- **Session 862** — Content Flow Unification real FKs (Deliverable
  → Initiative + Dream + SelfBlog + PodcastEpisode).
- **Session 1091** — sentinel "Unassigned" workspace fallback.
- **Session 1094-1095** — `publish_intent` enum architectural
  guidance + migration 0333 backfill.
- **Session 1075/1077** — content_tool / blog_tool split +
  approve/reject aliases.
- **Session 1098** — DeliverableAppend streaming idempotency.
- **Session 1169** — DeliverableGatedError typed exception Layer C
  Phase 1.
- **Session 1184** — DeliverableProvenanceMissingError PR-B soft
  WARN.
- **Session 1195** — Plan C Phase 1 Initiatives-First Backbone
  diagnostic_status TTL.
- **Session 1199** — DeliverableProvenanceMissingError PR-D hard
  exception flip.
- **Session 1206** — B2 (workspace pre-write validate) + B3
  (BLOCKED detection sentinel status).
- **Session 1226** — P1 agent name canonicalization + rewrites.
- **Session 1227** — LLM boolean-autofill silent-filter memory
  rule.
- **Session 1248** — P2b PA-tool `create_deliverable` status
  round-trip workaround.
- **Session 1250** — PR 5 Rigby Event Intake opt-in.
- **Session 1252** — PR 2 status_transition metadata whitelist.

### 11.4 Prior audit coverage

- **S1600 parent scoping** — §3 D Cat D boundary rule + §5 P3 slot
  + §6 parked issue 6.3 (5-gate vs 4-threshold) + §6.5 (SportsBettingBrief
  / OutreachDraft cross-arc disposition ownership).
- **S1601 Cat A audit** — §9.1 SelfBlog.objects.create bypass at
  runner:401 (D65a HEADLINE evidence input).
- **S1602 Cat B audit** — §16.1 Cat B write to
  `SelfBlog.stats_snapshot['deliberation']` at runner:415 (D65a
  HEADLINE evidence input).
- **S1504 Cat D (Sports)** — §14.3 SportsBettingBrief
  WRITE-ONLY-FORGOTTEN pattern (Cat D-analog precedent).
- **S1402 Revenue F.B1** — OutreachDraft delivery MISSING.
- **S1403 Revenue F.C4** — ContentEngagement docstring drift.
- **S1499 Revenue canonical** — D55 (ii) JobContract split
  precedent.
- **S1599 Sports canonical** — §11.3 §10 meta-methodology template
  third application.
- **S1274 cross-domain integration audit** — §12.3 P1
  Product/Architecture Decision Point precedent (analog D59).

### 11.5 Rigby memory rules relevant to Cat D

Already inventoried in §6.4: `feedback_deliverable_create_defaults_to_completed`,
`feedback_deliverable_status_via_content_complete`,
`feedback_deliverable_tool_use_append_for_large_payloads`,
`feedback_publish_intent_enum`, `feedback_deliverable_workspace`.

---

## 12. Research Coverage

Q13 classification per playbook §12.

**DEEP** — Very thorough coverage:
- Cat D scope has 12 handoff sessions with load-bearing decisions
  (§11.3).
- Two prior Group 1600 child audits (S1601 + S1602) inventoried
  handoffs to Cat D scope.
- Three cross-arc prior audits (S1504 + S1402 + S1403) framed
  Cat D-relevant cross-domain findings.
- Five Rigby memory rules cover tool-side drift.
- Factory + gates + provenance system trace across 10+ Session
  refactors.
- **Gap:** no canonical "Deliverable-subsystem primer" topic doc.
  §7 xx99 recommendation will name this.

Cat D coverage rating: **DEEP** (justifies the child audit at S1603
scope rather than deferring to xx99 consolidation).

---

## 13. Architecture Maturity

Q12 classification per playbook §12.

| Subsystem | Maturity | Evidence |
|-----------|----------|----------|
| **Deliverable base model** | **WORKING** (not CANONICAL yet — F4 Rigby fold explicit definition) | Docstring matches runtime; publish_intent enum backfilled 122 rows; Session 1195 diagnostic sweep live; all claimed features (quality metrics, library features, export capabilities, developer traceability) present. **Definition: "WORKING = operationally used successfully in production with known structural debt items."** Not yet CANONICAL because D65a posture is unresolved (variant linkage not first-class) — canonical rating premature. IF D65a variant linkage is counted as functional requirement, rating shifts to PARTIAL-CANONICAL. |
| **`create_deliverable` central factory** | **PARTIAL** (Deliverable side) | 5-gate + 3 dedup queries + provenance receipt + orphan sweep all live; 98%+ Deliverable adoption **corroborated by F3 fold (5 factory-adopter mgmt commands + 5 factory-adopter services surfaced by Rigby SIGN Batch A)**; 2 legitimate production bypasses remain (§16.2); F1 shadow-method concern RESOLVED (name collision only). **Adoption side of "PARTIAL"** is at Deliverable base level. **PARTIAL** because canonical goal was "gateway for all content-shaped creates" and variants completely bypass. |
| **5 parallel variants collectively** | **EXPERIMENTAL** | Two dead-code variants (SportsBettingBrief + BlockchainAuditBrief); one delivery-broken variant (OutreachDraft); one healthy variant (ClosePack — but structurally an island); SelfBlog most-adopted but 16+ independent write sites. No unified variant contract. |
| **PA tool surface (deliverable_tool + content_tool + blog_tool + newsletter_tool)** | **WORKING** (partial coverage) | 4 tool registrations, 39+ actions total; Session 1248 P2b workaround for status defaults; Session 1176 memory-rule silent-fallback bug in `update` action still open. Cat E S1605 will finalize maturity assessment. |
| **Supporting models (Append, Export, Event, Collection, Packet)** | **STABLE** | All Session 1098 / pre-S843 vintage; DeliverableEvent status_transition landed S1095; DeliverableAppend idempotency constraint healthy. |

**Overall Cat D maturity verdict: WORKING** — the container layer
works; the canonicalization goal is unresolved (D65a posture pending
xx99 decision).

---

## 14. Known Drift

Q23-Q27 drift matrix per playbook §12 finding_type + severity.

### 14.1 Docstring vs runtime — Deliverable base

**No drift** at HEAD. Deliverable base docstring at :85-105 claims
match implementation (verified in §4.7).

### 14.2 Docstring vs runtime — cross-arc

- **D.14.1 S1403 F.C4 ContentEngagement docstring drift** — inherited
  from Revenue arc; **CONFIRMED at HEAD**. `ContentEngagement`
  docstring claims "closes learning loop" but schema at
  `models_pipeline_feedback.py:370-449` has zero FK to Deliverable
  / SelfBlog / AgentPerformance. **Severity: HIGH** (drift; blocks
  learning-loop). Owner: Cat D flags but Cross-arc handoff to
  Group 1300 Memory (xx99 §9 delegated arc) OR to a hypothetical
  Group 1700 Observability arc.

### 14.3 5-gate vs 4-threshold gate architecture

- **D.14.2 Triple-gate architecture** —
  `deliverable_factory.py:358-411` implements 5-gate check
  (`gate_1_media_stub` / `gate_2_smoke_pattern` / `gate_3_min_length`
  / `gate_4_template_leak` / `gate_5_no_relevance`) at creation
  time. `publish_gate.py:27` implements 4-threshold check
  (quality/novelty/structure/mythology) at post-content-deliberation.
  SelfBlog carries own quality-score fields at `models_unified_system.py:20708-20728`.
  **Three parallel scoring systems.** Severity: **HIGH** (duplicate
  model + boundary_violation between Cat C and Cat D + Session 1033
  score_unscored_deliverables backfill still cleaning legacy rows).
  Cat D contributes evidence; Cat C S1604 owns resolution.
  Escalated per parent parked issue §6.3.

### 14.4 status field runtime "completed" 5th value

- **D.14.3 status='completed' runtime 5th value** — Deliverable
  model declares `STATUS_CHOICES = [draft, ready, published,
  archived]` at :347-352. Django `ChoiceField` validates on
  form/admin input only, not direct `.save()`. Runtime accepts
  `status='completed'` — Session 1248 P2b PA-tool workaround at
  `td_handlers_agents.py:2052` hardcodes it. Comment at :2093-2109
  documents the two-part fix (echo actual stored status + opt-in
  return_detail). **Severity: MEDIUM** (drift; partially-resolved
  via workaround). Owner: Cat D flags schema+runtime divergence;
  Cat E S1605 owns final PA-tool contract fix.

### 14.5 content_hash coverage

- **D.14.4 content_hash query-scope open question** — factory
  queries `content_hash` for 72h dedup at :955-970 (F0b post-Explore
  correction). Grep across `core/` for external
  `Deliverable.objects.filter(content_hash=...)` outside the factory
  returns 0 matches. So content_hash serves factory-internal dedup
  only. **Not drift, but a scope question:** should external callers
  (bulk-scripts, admin, migrations) also use content_hash for
  cross-reference? Currently no cross-reference use. Severity: **LOW**
  (design question, not bug).

### 14.6 Clone chain

- **D.14.5 `clone_count` incremented but never queried** — grep
  confirms `clone_count` incremented at
  `views_deliverables.py:331` (clone action) but never queried for
  ranking/analysis. Metadata-only field. Severity: **LOW** (dead
  metric, not blocking).

### 14.7 parent_object_type coverage

- **D.14.6 `parent_object_type='conversation'` live coverage
  verified** — used at `conversation_deliverable_extractor.py:385`
  + `conversation_initiative_pipeline.py:565`. Test coverage at
  `test_provenance_conversation_threading.py:120-125`. **NOT drift**
  — active production path. Severity: N/A (verified working).

### 14.8 Drift matrix summary

| ID | Item | Type | Severity | Owner |
|----|------|------|----------|-------|
| D.14.1 | ContentEngagement docstring drift (inherited) | drift | HIGH | Cross-arc (Group 1300 / 1700) |
| D.14.2 | Triple-gate architecture (5-gate + 4-threshold + own gate) | duplicate_model + boundary_violation | HIGH | Cat C S1604 (Cat D flags) |
| D.14.3 | Deliverable.status runtime "completed" 5th value | drift | MEDIUM | Cat E S1605 (Cat D flags) |
| D.14.4 | content_hash cross-reference scope open | drift (scope) | LOW | Cat D |
| D.14.5 | clone_count dead metric | technical_debt | LOW | Cat D |

---

## 15. Known Technical Debt

Q26 debt matrix per playbook §12.

| ID | Item | Type | Severity | Evidence | Cat D owner? |
|----|------|------|----------|----------|--------------|
| T.15.1 | **SelfBlog canonical write bypasses factory (16 sites) — F9 Rigby fold nuance** | boundary_violation | **HIGH-if-canonical-envelope-violated / MEDIUM-if-consistency-only** | grep `SelfBlog\.objects\.create` = 10 production sites incl. `content_deliberation_runner.py:401` (S1601 §9.1); 6 test sites. No factory routing. **F9 Rigby fold reframe (Batch B):** severity depends on whether SelfBlog bypasses cause duplicate content / broken linking / divergent lifecycle (→ HIGH) OR whether Deliverable envelope canonical still holds + SelfBlog writes are "consistency-only" concern (→ MEDIUM). Evidence at HEAD suggests **HIGH is defensible** because factory-owned invariants (`content_hash` dedup, `publish_intent` resolution, provenance receipt synthesis, orphan diagnostic marking) are ALL skipped on the SelfBlog write path. | YES — Cat D scope |
| T.15.2 | **`SportsBettingBrief` WRITE-ONLY-FORGOTTEN** (inherited S1504 §14.3) | dead_code | **CRITICAL** | 2 writers (`tasks_content.py:3150` + `tasks.py:12187`); no readers **found via `rg` across core/** at HEAD (grep method disclosed per F15 fold). REST endpoint `get_betting_brief` at `views_odds_sports.py:3237` bypasses persisted model. | Cross-arc (Cat D + Group 1500 T1.h) |
| T.15.3 | **`BlockchainAuditBrief` WRITE-ONLY-FORGOTTEN** | dead_code | **HIGH** | 1 writer (`tasks.py:12240`); no readers **found via `rg` across core/** at HEAD (grep method disclosed per F15 fold). Same S1504 pattern class extension. | Cross-arc (Cat D + blockchain domain owed) |
| T.15.4 | **`OutreachDraft` delivery MISSING** (inherited S1402 F.B1) — **F8 Rigby fold upgrade** | missing_connection | **CRITICAL** (F8 upgrade from HIGH) | Composition + status-transition paths active (28+ reads). No outbound delivery **found via `rg` across core/** for `send_outreach|dispatch_outreach|sendgrid|postmark|mailgun|smtplib` (grep method disclosed per F15 fold). **F8 Rigby fold Batch B: upgraded HIGH → CRITICAL** because if OutreachDraft exists to drive outbound revenue, "delivery missing" is business-critical, not just technical debt. | Cross-arc (Cat D + Group 1400 R.B1) |
| T.15.5 | **Central factory partial adoption** — **F1 RESOLVED + F3+F5 fold refinement** | technical_debt | MEDIUM | 92 total `Deliverable.objects.create` matches; 2 legitimate production Deliverable bypasses (`views_deliverables.py:305` clone + `workflow_orchestration_agent.py:5107` morning-brief). **F1 Rigby fold RESOLVED:** `real_job_execution_consumer.py:99` shadow method is name-collision only (returns plain dict for demo WebSocket UI; never touches ORM; verified via direct-read at :200-237). **F3 Rigby fold corroboration:** 5 factory-adopter mgmt commands + 5 factory-adopter services surfaced by Rigby SIGN Batch A confirm broad factory adoption. Factory adoption ~98% REMAINS ACCURATE. | YES — Cat D scope |
| T.15.6 | **Triple-gate composition contract MISSING** (5-gate factory + 4-threshold PublishGate + SelfBlog own gate) — **F7+F11 Rigby fold reframe** | boundary_violation (not duplicate_model) | HIGH | See D.14.2 above. Escalated from parent §6.3 parked issue. **F7+F11 Rigby fold Batch B reframe:** the debt isn't "too many gates" (each gate has a legitimate separation-of-concerns rationale — creation-time validation, publish-quality thresholds, variant-specific review). The debt is **"composition contract missing"** — no canonical statement of gate precedence, no unified state machine specifying which gate reviews at which lifecycle stage, no observable failure mode when gates disagree. Cat D flags; Cat C S1604 owns resolution. | Cross-arc (Cat D + Cat C S1604) |
| T.15.7 | **`publish_intent` variant coverage MISSING** | missing_connection | MEDIUM | Only on Deliverable base; grep-negative on 5 variants. Structural blocker for integration posture. | YES — Cat D scope (evidence input for D65a) |
| T.15.8 | **DeliverableCollection vs ContentPacket semantic overlap** | duplicate_model | LOW | Both group deliverables. Distinct semantics (user-M2M vs pipeline-scoped) but naming overlap. | YES — Cat D scope |
| T.15.9 | **NO canonical "Deliverable-subsystem" topic doc** | technical_debt | MEDIUM | Session 1147 `content-pipeline.md` is v2/SelfBlog-centric; no primer for Deliverable + 5 variants + lifecycle. | YES — Cat D §7 xx99 recommendation |
| T.15.10 | **DATABASE_MODEL_REFERENCE.md missing Deliverable + variant entries** | drift (doc) | MEDIUM | Reference is Session 737/1012 snapshot; no schema entries for any Cat D-owned model. | YES — Cat D §7 xx99 recommendation |
| T.15.11 | **PA-tool `deliverable_tool.update` silent-fallback bug on >6-7kB payloads** (memory-rule `feedback_deliverable_tool_use_append_for_large_payloads.md`) | technical_debt | MEDIUM | Documented drift; underlying fix pending. | Cat E S1605 (Cat D flags) |
| T.15.12 | **`clone_count` dead metric** | technical_debt | LOW | Written but never queried. | Cat D |

---

## 16. Boundary Violations

Q24, §16 per playbook.

### 16.1 Cat C intrusion into Cat D factory

- **Check:** does `deliverable_factory.py` reach into PublishGate?
- **Verification:** grep-verified NO direct `PublishGate(...)` /
  `.evaluate(...)` calls in factory. Clean boundary. Factory
  contributes `publish_intent` enum value only; Cat C reads it.
- **Verdict:** NO VIOLATION. ✓

### 16.2 Cat D factory bypassed by production code

- **`core/views_deliverables.py:305`** clone_deliverable view:
  `Deliverable.objects.create` directly. **HIGH** priority to
  migrate to factory (would gain gate coverage + provenance). User-
  facing; explicit S1091 workspace inheritance at :313-314.
- **`core/services/workflow_orchestration_agent.py:5107`** morning-
  brief WorkflowAgent: `Deliverable.objects.create` directly.
  MEDIUM priority (internal agent). Should migrate.
- **Verdict:** T.15.5 debt item; TWO legitimate bypasses, not
  systemic bypass. Cat D-owned remediation.

### 16.3 Cat A pipeline bypasses Cat D factory for variant write

- **`core/services/content_deliberation_runner.py:401`**
  `SelfBlog.objects.create` directly. **HIGH** as boundary-crossing
  question: Cat A owns pipeline BUT canonically-container SelfBlog
  variant should route through unified factory to gain factory
  semantics.
- **Verdict:** T.15.1 debt item + T.15.7 missing_connection
  (variant coverage). D65a-analog posture-decision input for xx99.

### 16.4 Cat B / Cat E intrusion into Cat D

- **Check:** grep for reviewer-panel or PA-tool-handler logic in
  factory. NO matches. Clean boundary.
- **AgentExecution.objects.create at factory :724** — this is the
  `_synthesize_pa_execution_receipt` provenance synthesis. NOT
  intrusion; it's the factory's own contract obligation (Session
  1184 PR-B).
- **Verdict:** NO VIOLATION. ✓

### 16.5 S1602 §15.3 spawn_tasks_from_mandate landmine — Cat D lens

Extends S1602 §15.3 finding into Cat D scope. **`DecisionEnforcerAgent.spawn_tasks_from_mandate`
at `decision_enforcer_agent.py:455-476`** imports missing
`queue_agent_task` (verified S1602). If Cat D owns Deliverable
lifecycle transitions AND task spawning is part of the transition
contract, then this missing task is a Cat D concern. However, the
current architecture has Cat B owning the spawn contract; Cat D
observes status via signal handlers (§10.1). **Verdict:**
cross-boundary observability question; Cat D contributes evidence
for xx99 boundary re-scoping. No new Cat D-owned action here.

---

## 17. Duplicate or Overlapping Systems

Q23 per playbook §17.

### 17.1 DeliverableCollection vs ContentPacket

- **DeliverableCollection** at :525 — user-curated M2M grouping;
  `is_public` flag; user-initiated.
- **ContentPacket** at :617 — pipeline-run-scoped; workflow-driven;
  agent-initiated.
- **Semantics distinct BUT naming overlap risk.** Severity: LOW
  (T.15.8). May justify a rename or clarifying docstring.

### 17.2 Triple quality-scoring systems

- **Deliverable.quality_score** at `models_deliverables.py:256-259`
  (0.0-1.0 base model field).
- **SelfBlog.quality_score** at `models_unified_system.py:20709-20712`
  (0.0-1.0 variant field).
- **PublishGate GateResult.quality_score** at `publish_gate.py`
  (dataclass output, not persisted to model; stored in SelfBlog
  gate_notes text field).
- **Three parallel systems** with no unified source. Session 1033
  `score_unscored_deliverables` task scores base Deliverable; Cat C
  PublishGate scores SelfBlog; SelfBlog own writer sets fields
  independently. Severity: HIGH (T.15.6 triple-gate); Cat C S1604
  owns resolution.

### 17.3 Deliverable.self_blog FK vs SelfBlog independent lifecycle

- **Structure:** `Deliverable.self_blog` at :192-199 is 1:M
  nullable FK (one SelfBlog can be linked from many Deliverables;
  Deliverable can have zero-or-one SelfBlog link).
- **Reality:** SelfBlog created independently via
  `content_deliberation_runner.py:401`; Deliverable→SelfBlog link
  is optional/not-canonically-established.
- **Verdict:** parallel-sibling structural pattern (NOT
  canonical-container pattern). D65a HEADLINE evidence.

### 17.4 5 variants collectively — overlap analysis

All five carry `title` or `title`-equivalent; all carry
`created_at`; all carry some form of `user` FK (directly or via
`opportunity`); most carry `status`; NONE carry `publish_intent`.
Duplicate schema surface exceeds 60% but each is stored in a
separate table with independent lifecycle. Whether this is:
- **integration debt** (should collapse to Deliverable base via
  polymorphism or shared abstract model), OR
- **island by-design** (each variant has semantics justifying
  independent evolution) — is the D65a posture decision.

---

## 18. Ownership Gaps

Q25 per playbook.

| Area | Current owner | Clarity | Cat D-flagged issue |
|------|---------------|---------|---------------------|
| Deliverable base model schema | Cat D | CLEAR | — |
| `create_deliverable` factory | Cat D | CLEAR | — |
| 5-gate policy | Cat D | CLEAR | Cross-arc with Cat C (T.15.6 triple-gate) |
| DeliverableEvent status_transition | Cat D (signal) + Session 1250 opt-in Rigby Intake | CLEAR | — |
| DeliverableAppend streaming contract | Cat E (PA-tool)-adjacent + Cat D (schema) | CLEAR | — |
| SelfBlog write path | Cat A pipeline (S1601 §9.1) | **MISALIGNED** | Should be Cat D canonical if integration posture |
| SelfBlog quality gate fields | SelfBlog owner (variant) + Cat C PublishGate writer | UNCLEAR | Overlaps Deliverable.quality_score AND PublishGate.quality_score |
| SportsBettingBrief creation | Sports domain (S1504) | CLEAR | But dead-code writer; consumer-or-remove owed |
| BlockchainAuditBrief creation | Blockchain domain (unaudited) | UNCLEAR | Dead-code; owner should reclaim or Cat D archives |
| OutreachDraft delivery | Revenue domain (S1402) | UNCLEAR | ZERO outbound; owner never identified |
| ClosePack lifecycle | Revenue domain | CLEAR | Healthy consumer ratio |
| `publish_intent` enum semantics | Cat D | CLEAR | But 0 variant adoption = D65a evidence |
| Session 1195 diagnostic_status TTL sweep | Cat D (`sweep_diagnostic_deliverables` at tasks.py:707) | CLEAR | — |
| `content_hash` cross-reference use | Cat D (factory-internal) | UNCLEAR | External use undefined |
| `deliverable_tool.update` silent-fallback bug | Cat E S1605 | CLEAR (deferred) | Memory-rule filed |
| `queue_agent_task` (S1602 §15.3) landmine | Cat B | CLEAR | Cross-boundary observability question for Cat D |

---

## 19. Recommended Future Research

Q28. Ranked by architectural uncertainty × risk × unblocked flows.

### Top-tier (T1 — evidence bearing on xx99 D65a/D65b/D65c posture selection)

- **T1 R.CONTENT.VARIANT-CATEGORIZATION-CLARIFICATION** (F12 Rigby
  fold NEW) — **bridge artifact for xx99 D65a consumption**.
  Define the 3-category variant taxonomy as an evidence-backed
  classification with concrete criteria: (a) envelope→object
  integrated (forward FK; Deliverable contract governs lifecycle);
  (b) standalone-by-design first-class (independent lifecycle; may
  optionally link later); (c) unfinished/orphan (write-only-forgotten
  pattern). For each of the 5 variants, state current bucket + read-path
  evidence + tooling surface + consumer + retention posture.
  **Uncertainty: LOW (evidence-gathering, not design); Risk: LOW;
  Unblocks: xx99 D65a Chris-gated decision brief.** Cat D-owned
  (per §1 headline finding).
- **T1 R.CONTENT.CANONICAL-CREATION-CONTRACT** (F13 Rigby fold NEW)
  — Factory + shadow paths reconciliation. Enumerate all Deliverable
  + variant creation funnels; document the invariants applied by
  each (content_hash dedup, provenance receipt, publish_intent
  resolution, orphan diagnostic marking, workspace auto-assign);
  identify parity gaps. **Uncertainty: LOW (audit-style enumeration);
  Risk: LOW; Unblocks: Cat E S1605 tool contract + xx99 factory
  adoption metrics.** Cat D-owned.
- **T1 R.CONTENT.VARIANT-CANONICALIZATION** — post-xx99 Chris-gated
  ADR selecting D65a Deliverable-canonicalization posture. Cat D
  contributes structural + factory + variant evidence documented in
  this audit (§4.2 / §9 / §16.3 / §17.4). **Uncertainty: HIGH;
  Risk: HIGH; Unblocks: 5 variant remediations + factory-canonical
  scope + PA-tool contract simplification.**
- **T1 R.CONTENT.DELIVERABLE-FACTORY-VARIANT-EXTENSION** — if D65a
  selects integration posture, extend `deliverable_factory`
  semantics to variants (polymorphic variant-shim OR mandate all
  variant creates route through factory). Cat D-owned design
  preparation post-ADR. **Uncertainty: MED (design shape unclear);
  Risk: MED (retro-fitting existing variants); Unblocks: 16
  SelfBlog.objects.create sites + variant `publish_intent` coverage
  + unified event stream.**
- **T1 R.CONTENT.TRIPLE-GATE-COMPOSITION-CONTRACT** (F11 rename from
  R.CONTENT.TRIPLE-GATE-UNIFICATION) — resolve the composition
  contract MISSING for factory 5-gate + PublishGate 4-threshold +
  SelfBlog-own-gate. Escalated from parent §6.3 parked issue with
  Cat D evidence. **F7+F11 Rigby fold reframe:** the debt is not
  "too many gates" (each has legitimate SoC rationale) but "no
  canonical statement of precedence, no unified state machine, no
  observable failure mode when gates disagree." **Uncertainty: HIGH
  (three parallel systems, each entrenched); Risk: HIGH (may
  require migration); Unblocks: Cat C S1604 scope + quality-scoring
  canonicalization.** Cat C owns resolution; Cat D contributes
  evidence.
- **T1 R.CONTENT.OUTREACHDRAFT-DELIVERY** (F14 Rigby fold — upgraded
  from T2 to T1 per Batch B business-criticality) — ZERO outbound
  channel; delivery ADR owed. Cat D contributes S1402 F.B1
  CONFIRMED at HEAD evidence. **Uncertainty: LOW (already scoped
  in Group 1400 R.B1); Risk: HIGH-BUSINESS (revenue-critical if
  OutreachDraft is on outbound revenue path); Unblocks: revenue
  outbound rail.** Cross-arc (Cat D + Group 1400 R.B1).

### Second-tier (T2 — Cat D-native remediation)

- **T2 R.CONTENT.CENTRAL-FACTORY-BYPASS-MIGRATION** — migrate 2
  legitimate Deliverable bypasses (`views_deliverables.py:305` clone
  view + `workflow_orchestration_agent.py:5107` morning-brief) to
  factory. Trivial from a code standpoint (add `create_deliverable`
  call); non-trivial to preserve semantics (clone semantics may
  require extending factory with a `cloned_from` kwarg branch).
  **Uncertainty: LOW; Risk: LOW; Unblocks: 100% factory adoption
  for Deliverable base.**
- **T2 R.CONTENT.SPORTSBETTINGBRIEF-DISPOSITION** (cross-arc with
  Group 1500 T1.h) — consumer-or-remove decision. Cat D contributes
  "WRITE-ONLY-FORGOTTEN CONFIRMED at HEAD" evidence + REST endpoint
  bypasses persisted model verification.
- **T2 R.CONTENT.BLOCKCHAINAUDITBRIEF-DISPOSITION** — same pattern
  class as SportsBettingBrief; owner reclaim OR archive decision.
- **T2 R.CONTENT.DELIVERABLE-STATUS-COMPLETED-DRIFT** — Session
  1248 P2b workaround for `td_handlers_agents.py:2052` status
  hardcode. Fully-resolve underlying schema+runtime drift (either
  add 'completed' to STATUS_CHOICES OR remove PA-tool hardcode).
  Cat E S1605 owns.

*(F14 fold: R.CONTENT.OUTREACHDRAFT-DELIVERY moved from T2 → T1
above per Rigby SIGN Batch B business-critical framing.)*

### Third-tier (T3 — post-arc T-slot)

- **T3 R.CONTENT.DELIVERABLE-TOPIC-DOC** — NEW
  `docs/topics/deliverable-and-variants.md` primer. Covers
  Deliverable base + 5 variants + lifecycle + factory + gates.
  Consumes this audit + Cat E + Cat F evidence as source. xx99 §7
  recommendation.
- **T3 R.CONTENT.DATABASE-MODEL-REFERENCE-REFRESH** — add Deliverable
  + 5 variants + supporting models to DATABASE_MODEL_REFERENCE.md
  with field tables. xx99 §7 recommendation.
- **T3 R.CONTENT.CLONE-COUNT-USAGE-OR-REMOVE** — decide whether
  `clone_count` is worth surfacing (e.g., in ranking) or drop the
  field. T.14.5.
- **T3 R.CONTENT.DELIVERABLECOLLECTION-VS-CONTENTPACKET-RENAME** —
  resolve semantic-vs-naming overlap.
- **T3 R.CONTENT.CONTENT_HASH-EXTERNAL-SCOPE** — decide whether
  `content_hash` should be queryable outside factory (e.g., for
  admin de-duplication tooling).

### Fourth-tier (T4 — deferred cross-arc)

- **T4 R.CONTENT.CAT-B-QUEUE-AGENT-TASK-CROSS-BOUNDARY** —
  cross-boundary follow-up on S1602 §15.3 landmine. Cat D observer;
  Cat B owner.
- **T4 R.CONTENT.CONTENTENGAGEMENT-LEARNING-LOOP-BRIDGE** —
  cross-arc with Group 1300 Memory OR Group 1700 Observability.
  Cat D flags S1403 F.C4 drift.

---

## 20. Appendix

### 20.1 Files inspected

Full sweep list (Agent 1-6 aggregate):

**Core code:**
- `core/models_deliverables.py` (:1-720)
- `core/models_unified_system.py` (:18394-18466, :20611-20763)
- `core/models_outreach.py` (:18-150)
- `core/models_close_pack.py` (:20-80)
- `core/models_deliverable_appends.py` (:35-155)
- `core/models_pipeline_feedback.py` (:370-449 for ContentEngagement drift)
- `core/services/deliverable_factory.py` (:1-1455)
- `core/services/content_deliberation_runner.py` (:390-449 for SelfBlog write)
- `core/services/publish_gate.py` (:27-49 for 4-threshold check boundary)
- `core/services/deliverable_append_service.py` (:214 for streaming)
- `core/services/pa_tool_schemas.py` (:3389-3460, :3498-3550)
- `core/services/td_handlers_content.py` (:84, :162, :235-268, :519)
- `core/services/td_handlers_agents.py` (:2040-2110 for status='completed' hardcode)
- `core/services/td_handlers_newsletter.py` (:25)
- `core/services/tool_dispatcher.py` (:476, :479, :490, :521)
- `core/signals/deliverable_status_signals.py` (:83, :111, :133)
- `core/views_deliverables.py` (multiple endpoints per §3.5, :305 clone bypass)
- `core/views_research_demo.py` (SelfBlog endpoints)
- `core/views_outreach.py` (OutreachDraft endpoints)
- `core/views_odds_sports.py` (:3237 get_betting_brief)
- `core/services/workflow_orchestration_agent.py` (:5107 factory bypass)
- `core/tasks.py` (Deliverable-adjacent tasks; god-service)
- `core/tasks_content.py` (SelfBlog + SportsBettingBrief writes)
- `core/urls.py` (routing verification)
- `core/celery.py` (beat entries)
- `frontend/src/pages/BlogViewerPage.tsx` (:45)
- `frontend/src/lib/api.ts` (:3921-3962 blogsApi)

**Migrations (recent 5):**
`0309`, `0325`, `0333`, `0337`, `0360`.

**Docs:**
- `docs/topics/content-pipeline.md`
- `docs/DATABASE_MODEL_REFERENCE.md`
- `docs/research/domains/content/1600_content_domain_scoping.md`
- `docs/research/domains/content/1601_content_claims_pack_deliberation_pipeline_v2_audit.md`
- `docs/research/domains/content/1602_content_reviewers_decision_enforcement_audit.md`
- `docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md`
- `docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md`
- `docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md`
- `docs/research/domains/sports/1599_sports_canonical_summary.md`
- `docs/research/domains/revenue/1499_revenue_canonical_summary.md`
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`
- `docs/PLATFORM_INVENTORY.md`
- `docs/PLATFORM_WHAT_IT_IS.md`
- 5 Rigby memory files under `~/.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/`.

### 20.2 Grep patterns used

Key binary-claim grep-verifications:
```
rg -n 'class SelfBlog\(models.Model\)|class SportsBettingBrief\(models.Model\)|class BlockchainAuditBrief\(models.Model\)' core/models_unified_system.py
rg -n 'class OutreachDraft\(models.Model\)|class ClosePack\(models.Model\)|class DeliverableAppend\(models.Model\)' core/
rg -n 'ForeignKey.*Deliverable|ForeignKey\(.core.Deliverable' core/   # NO MATCHES — confirms island posture
rg -n 'publish_intent' core/models_unified_system.py core/models_outreach.py core/models_close_pack.py   # NO MATCHES on variants
rg -n 'filter\(content_hash=|content_hash=\w+\)\.exists' core/   # 1 match at models_unified_system.py:15814 (unrelated model — image provenance) — Deliverable factory content_hash IS used at factory.py:961 (F0b correction)
rg -n 'Deliverable\.objects\.create' -l   # 47 files (92 total lines including tests/docs)
rg -n 'send_outreach|dispatch_outreach|sendgrid|postmark|mailgun|smtplib' core/ | grep -v archive | grep -v external | grep -v ai_core   # 0 hits — S1402 F.B1 CONFIRMED at HEAD
rg -n 'SportsBettingBrief\.objects\.(filter|get|first|last|latest)' core/   # 0 hits — S1504 §14.3 CONFIRMED at HEAD
```

### 20.3 Verifier-loop notes (pre-Explore + post-Explore)

**Pre-Explore verifier-loop (parent-Claude, playbook §14 rule):**
22 load-bearing binary claims from parent S1600 §3 D + Cat D scope
grep-verified before spawning Explore sub-agents:

| Claim | Verified | Correction? |
|-------|----------|-------------|
| Deliverable base at models_deliverables.py:84 | ✓ | none |
| publish_intent at :131-136 default INTERNAL_ONLY | ✓ | none |
| workspace FK at :165-173 | ✓ | none |
| tags ArrayField at :143-148 | ✓ | none |
| source_operation FK at :210-217 | ✓ | none |
| initiative FK at :176-183 Session 862 | ✓ | none |
| content_format at :240-245 | ✓ | none |
| status CharField at :353-358 default 'ready' | ✓ | none |
| DeliverableGatedError at :46-74 | ✓ | none |
| DeliverableExport at :474 | ✓ | none |
| DeliverableEvent at :561 | ✓ | none |
| ContentPacket at :617 | ✓ | none |
| SelfBlog at models_unified_system.py:20611 | ✓ | none |
| SelfBlog quality gate at :20708-20728 | ✓ | none |
| SportsBettingBrief at models_unified_system.py:18394 | ✓ | none |
| BlockchainAuditBrief at models_unified_system.py:18435 | ✓ | none |
| OutreachDraft at models_outreach.py:18 | ✓ | none |
| ClosePack at models_close_pack.py:20 | ✓ | none |
| DeliverableAppend at models_deliverable_appends.py:35 | ✓ | none |
| S1601 §9.1 SelfBlog.objects.create at runner:401 | ✓ | none |
| S1602 §16.1 stats_snapshot at runner:415 | ✓ | none |
| **Central factory at deliverable_factory.py:1269** | ✗ | **F0 DRIFT: actual `def create_deliverable(` at :752; :1269 is `Deliverable.objects.create(**kwargs)` call inside the function body (content-hash dedupe / atomic-transaction block).** |

**Post-Explore verifier-loop:**
6 additional binary claims from Explore sub-agent reports
grep-verified before draft finalization:

| Claim | Verified | Correction? |
|-------|----------|-------------|
| **content_hash dead-write (Agent 6)** | ✗ | **F0b CORRECTION: content_hash IS queried at factory :955-970 for 72h dedup. Corrected in §4.5 + §7.1 step 8 + §14.5 to "used for factory-internal 72h dedup; external cross-reference use undefined".** |
| NO reverse FK to Deliverable across `core/` (Agent 1 + 4) | ✓ | none — confirms structural island posture |
| publish_intent only on Deliverable base (Agent 4) | ✓ | none — confirms grep-negative on all variant models |
| td_handlers_agents.py:2052 hardcodes status='completed' (Agent 3 memory-rule sweep) | ✓ | Session 1248 P2b comment at :2091-2109 documents workaround; recorded as "partially-resolved via workaround" in §14.4 |
| 4 god-services >3000 lines (Agent 2) | ✓ | wc -l confirms tasks.py 13,470 / discord_bot.py 11,677 / workflow_orchestration_agent.py 5,424 / tasks_content.py 4,418; deliverable_factory.py 1,455 within threshold |
| S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN at HEAD | ✓ | 2 writers, 0 readers grep-verified — CONFIRMED |
| S1402 F.B1 OutreachDraft delivery MISSING at HEAD | ✓ | 0 production hits for send/dispatch/sendgrid/postmark/mailgun/smtplib — CONFIRMED |

### 20.4 Unresolved unknowns (UNK matrix)

| ID | Question | Owner |
|----|----------|-------|
| UNK-1 | Does Session 1248 P2b workaround for `status='completed'` fully resolve the memory-rule concern, or does the underlying schema-vs-runtime drift persist? | Cat E S1605 |
| UNK-2 | What is the operational path from Newsletter beat `dry_run=True` default (S1228 P3 at celery.py:423) to live publishing? | Cat C S1604 |
| UNK-3 | `feedback_deliverable_tool_use_append_for_large_payloads.md` — is >6-7kB payload truncation a threshold branch or silent fallback bug? | Cat E S1605 |
| UNK-4 | 5-gate (factory) vs 4-threshold (PublishGate) vs SelfBlog-own-gate — canonical or drift? | Cat C S1604 + xx99 |
| UNK-5 | Is BlockchainAuditBrief still needed at HEAD, or archive-candidate? | Blockchain domain owner (unaudited) |

### 20.5 Rigby SIGN fold notes

**Cycle 1 verdict: SIGN-with-edits (18 folded) at Medium-High
confidence (0.75).** Fresh isolation pin `pa-8af9063864bf4a7f`
minted via `session_tool.create_fresh` at S1603 SIGN routing. Standard
9-question pressure-test batched A/B/C + final-verdict single-question
follow-up per memory rule
`feedback_rigby_sign_worker_instability_recovery.md`. D48 preemptive
stability-probe gate 12th arm CONFIRMED — batches A/B/C all
substantive on isolation pin; final-verdict clean; no pin-poisoning
symptoms. **Seven-consecutive-fully-clean-arms sub-pattern
S1503+S1504+S1505+S1506+S1601+S1602+S1603 CONFIRMED** — extends
D48 codification-ready-STRENGTHENED evidence.

**F0/F0b — Pre-Explore + Post-Explore verifier-loop corrections
(pre-SIGN):**
- **F0 (pre-Explore drift):** parent S1600 §3 D cited central
  factory at `deliverable_factory.py:1269`; actual `def
  create_deliverable(` at :752. Line :1269 is `Deliverable.objects.create(**kwargs)`
  inside function body atomic-transaction block. Corrected in
  §3.3 + §7.1 step 21 + verifier_loop frontmatter.
- **F0b (post-Explore correction):** Explore Agent 6 initially
  flagged `content_hash` as dead-write. Direct-read at
  `deliverable_factory.py:955-970` confirms
  `Deliverable.objects.filter(content_hash=c_hash, created_at__gte=hash_window)`
  is the factory's 72h dedup query — NOT dead-write. Corrected in
  §4.5 + §7.1 step 8 + §14.5 to "used for factory-internal 72h
  dedup; external cross-reference use undefined".

**F1-F18 — Rigby SIGN cycle 1 folds (batch A/B/C + final verdict):**

- **F1 RESOLVED — shadow `create_deliverable` in
  `real_job_execution_consumer.py:99/200`.** Rigby SIGN Batch A
  flagged as potential hidden factory bypass; parent-Claude
  direct-read verification at :200-237 confirms the method returns
  a plain Python dict for demo WebSocket UI simulation; never
  touches Django ORM; never persists Deliverable row. **Name
  collision, not factory bypass.** Factory adoption metric of 98%+
  REMAINS ACCURATE. Recorded at §5.4a + §13 (T.15.5) + §1
  Executive Summary. This resolves Rigby's Option-1 must-change
  condition per Batch C Q9 verdict (allows confidence upgrade
  0.75 → High).
- **F2 — Cat D-adjacent services surfaced by Rigby SIGN Batch A.**
  Added `core/services/deliverable_envelope.py` +
  `core/services/conversation_deliverable_extractor.py` +
  `core/services/platform_event_view.py` + `core/deliverables_consumer.py`
  to §5.4a as Cat D-adjacent lifecycle/identity services (not
  models, but load-bearing for "what IS a Deliverable at the
  boundary of persistence").
- **F3 — Factory-adopter mgmt commands surfaced by Rigby SIGN
  Batch A.** Added 5 mgmt commands
  (`register_external_repo.py`, `import_patent_disclosures.py`,
  `refresh_repo_context.py`, `draft_repo_verifier_claims.py`,
  `survey_external_repo.py`) + 5 factory-adopter services
  (`core/tasks_content.py`, `core/views_workspace_templates.py:315`,
  `core/models_document_registry.py`, `core/agents/base_agent.py`,
  `core/agents/workflow_agent.py`) to §7.4 as evidence of broad
  healthy factory adoption. Corroborates 98%+ metric.
- **F4 — Deliverable base maturity explicit definition
  (Rigby SIGN Batch A Q2).** Reframed §13 rating from unqualified
  "WORKING" to "WORKING (current-scope definition: operationally
  used successfully in production with known structural debt);
  PARTIAL-CANONICAL if D65a variant linkage counted as functional
  requirement." Prevents inflated maturity optics.
- **F5 — Factory adoption sites reconciliation.** Cross-checked
  factory adopters Rigby surfaced vs Agent 2's original count.
  All Rigby-surfaced sites are LEGITIMATE factory callers, not
  bypasses. 98%+ Deliverable adoption metric verified.
- **F6 — D65a "island posture" reframe to 3-category neutral
  taxonomy (Rigby SIGN Batch B Q4).** Rewrote §1 Executive Summary
  headline finding to distinguish (a) envelope→object integrated
  (Deliverable→SelfBlog, Deliverable→PodcastEpisode via Session
  862 forward FKs) vs (b) standalone-by-design first-class
  (OutreachDraft, ClosePack provisional) vs (c) unfinished/orphan
  (SportsBettingBrief, BlockchainAuditBrief). Prevents S1274
  EventBus-style over-interpretation of structural absence as
  functional gap.
- **F7 — Triple-gate reframe as "separation of concerns lacking
  composition contract" (Rigby SIGN Batch B Q4).** Recorded at
  §14.3 + §17.2 + T.15.6. The debt is not "too many gates" but
  "no canonical composition contract statement."
- **F8 — T.15.4 OutreachDraft delivery upgrade HIGH → CRITICAL
  (Rigby SIGN Batch B Q5).** Business-critical if OutreachDraft
  is on outbound revenue path. Updated §15 debt matrix + T-slot.
- **F9 — T.15.1 SelfBlog canonical bypass severity nuance (Rigby
  SIGN Batch B Q5).** Reframed severity to "HIGH-if-canonical-
  envelope-violated / MEDIUM-if-consistency-only". Evidence at
  HEAD suggests HIGH defensible because factory invariants are ALL
  skipped on SelfBlog write path (content_hash dedup, publish_intent
  resolution, provenance receipt, orphan diagnostic).
- **F10 — T.15.5 factory adoption description update (Rigby SIGN
  Batch B Q5).** Incorporated F1 resolution + F3 corroboration into
  T.15.5 evidence field.
- **F11 — T.15.6 triple-gate reframe as boundary_violation + "composition
  contract missing" (Rigby SIGN Batch B).** Type changed from
  duplicate_model to boundary_violation. Reframed §15 debt matrix.
- **F12 — NEW T1 R.CONTENT.VARIANT-CATEGORIZATION-CLARIFICATION
  (Rigby SIGN Batch C Q7).** Bridge artifact for xx99 D65a
  consumption. Added to §19 top-tier.
- **F13 — NEW T1 R.CONTENT.CANONICAL-CREATION-CONTRACT (Rigby SIGN
  Batch C Q7).** Factory + creation-funnels reconciliation. Added
  to §19 top-tier.
- **F14 — R.CONTENT.OUTREACHDRAFT-DELIVERY upgrade T2 → T1 (Rigby
  SIGN Batch C Q7).** Revenue-critical business impact. Moved to
  §19 top-tier.
- **F15 — Over-binary claims softened (Rigby SIGN Batch C Q8).**
  Changed "zero/never/missing" language in §15 T.15.2/T.15.3/T.15.4
  to "no evidence found via `rg` across core/" with grep method
  explicitly disclosed. Preserves confidence while acknowledging
  search scope.
- **F16 — Cat D-vs-Cat C boundary tightened (Rigby SIGN Batch C
  Q8).** §14.3 + §17.2 wording softened from "resolve" to
  "flag as multiple lifecycle authorities without composition
  contract"; Cat D contributes evidence, Cat C S1604 owns
  resolution. Explicit boundary reinforcement.
- **F17 — F1 RESOLVED before commit (Rigby SIGN Batch C Q9 must-change
  Option 1).** Chose Option 1 (resolve F1) over Option 2
  (disclaimer + provisional marking). Confidence upgrade 0.75 →
  High per Rigby's condition.
- **F18 — Maturity provisional rewound (F1 resolved).** No
  provisional flags needed because F1 investigation completed
  before commit. §13 maturity verdicts stand as-refined by F4/F6/F9.

**Isolation pin retirement:** `pa-8af9063864bf4a7f` retire at
S1603 close per playbook §15 via `session_tool.retire`
(memory rule `feedback_session_tool_retire_works.md`).

**Arc pin continuity:** `pa-f52acf3f8d394faa` (Group 1600 arc pin)
retained through S1604 Cat C + S1605 Cat E + S1606 Cat F + S1699
xx99 per playbook §16 arc-continuity rule.

### 20.6 Cross-arc handoffs owed to Cat C S1604 + Cat E S1605 + Cat F S1606 + xx99 S1699

- **To Cat C S1604 (PublishGate + Publish Rails):**
  - §14.3 Triple-gate architecture (T.15.6) — resolve 5-gate vs
    4-threshold vs SelfBlog-own-gate.
  - §8.4 lifecycle stages 9-11 (publish-eligibility + publish +
    post-publish) owned by Cat C.
  - UNK-2 Newsletter dry_run promotion path.
  - UNK-4 gate canonicalization.
- **To Cat E S1605 (Rigby-Facing PA Tooling + Approval UX):**
  - §14.4 `status='completed'` runtime drift — full resolution via
    PA-tool contract fix (T.15.11 already flagged in Cat E scope).
  - UNK-1 Session 1248 P2b workaround assessment.
  - UNK-3 `deliverable_tool.update` silent-fallback bug.
  - Cat E owns final PA-tool contract sweep.
- **To Cat F S1606 (Cross-Domain Integration Lens + Posture
  Decision):**
  - §4.2 five-variant structural-island confirmation (D65a HEADLINE).
  - §9 integration edge table (5 MISSING reverse FKs = D65a
    HEADLINE evidence).
  - §16.3 SelfBlog canonical bypass (D65a HEADLINE evidence input).
  - §13 maturity verdict per subsystem.
  - §17.4 five-variant overlap analysis.
- **To xx99 S1699 (Canonical Summary):**
  - §19 T1 recommendations feed §5 Chris-gated decision brief
    (D65a/D65b/D65c three-axis posture selection).
  - §14.8 drift matrix + §15 debt matrix consolidate with Cat A/B/C/E
    equivalent matrices.
  - §11 documentation gaps feed §7 anchor-update recommendations
    (topic-doc landing + DATABASE_MODEL_REFERENCE refresh).
  - §20.4 UNK-1 through UNK-5 promote to §6 unresolved unknowns
    → §8 follow-on queue.
  - **Playbook §11.3 §10 meta-methodology fourth application** at
    xx99 — Group 1600 as fourth application of Chris's Phase 0
    methodology + third application of D62 = (a) 6-sibling exemplar
    mini-schema propagation-upfront pattern.

### 20.7 Frontmatter provenance

Session 1603 (this doc):
- **Frontmatter `status: active`** at draft time; will remain
  `active` on Chris-lock (per playbook §16 draft→active flip
  convention for child audits).
- **`authority: child-audit`** — per playbook §11.2 stage-scoped
  routing.
- **`category: child_audit`** — Group 1600 third child under D66
  P3 slot per F3 fold (Cat D moved from P4→P3 because Cat C
  consumes Cat D's canonical decision D65a-analog).
- **`session: 1603`** — third child audit after S1601 first + S1602
  second.
- **`domain_slug: content`** — per parent D63 lock.
- **`research_group: 1600`** — per parent D64 lock.
- **`child_slot: P3`** — per parent D66 F3 fold.
- **`verifier_loop`** field records F0 pre-Explore drift correction +
  F0b post-Explore correction + pending Rigby SIGN cycle 1.
- **`owner: claude`** — drafted S1603.
- **`supersedes: none`** — first Cat D audit.

---
