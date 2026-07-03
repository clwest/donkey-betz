---
title: "Content Category C — PublishGate + Publish Rails (Child Audit)"
status: active
authority: research
research_group: 1600
domain_slug: content
session: 1604
category: child_audit
child_slot: P4
generated: 2026-07-02
last_verified: 2026-07-02
dependencies_on:
  - Group 1600 parent (1600_content_domain_scoping.md — Cat C boundary at §3 C; F2 fold; F3 fold P3↔P4 swap; §6.2 newsletter dry_run parked; §6.3 5-gate vs 4-threshold parked)
  - Group 1600 P1 S1601 (1601_content_claims_pack_deliberation_pipeline_v2_audit.md — SelfBlog.objects.create bypass at runner:401; deliberation JSONField writer)
  - Group 1600 P2 S1602 (1602_content_reviewers_decision_enforcement_audit.md — stats_snapshot['deliberation'] Cat B writer at runner:415; queue_agent_task landmine)
  - Group 1600 P3 S1603 (1603_content_deliverable_base_variants_audit.md — Cat D structural islands + T.15.6 triple-gate composition contract MISSING + 16.2 factory bypasses + 16.3 Cat A pipeline bypasses)
  - Group 1500 P4 S1504 (1504_sports_betting_content_pipeline_audit.md — §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN pattern precedent + §5.1 SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS)
  - Group 1400 P2 S1402 (1402_revenue_outreach_composition_delivery_audit.md — F.B1 OutreachDraft delivery ZERO outbound; F8-upgraded to CRITICAL by S1603)
  - Group 1400 P3 S1403 (1403_revenue_engagement_inbound_audit.md — F.C4 ContentEngagement docstring drift CONFIRMED at HEAD)
delegates_to:
  - Cat E S1605 — approval-UX contract (Rigby PA tool + BlogViewerPage auth); post-publish workflow if any lands
  - Cat F S1606 — cross-domain integration lens (consumes Cat C evidence for D65b/D65c posture)
  - xx99 S1699 — canonical summary (D65a/D65b/D65c posture-decision evidence brief; T1 R.CONTENT.TRIPLE-GATE-COMPOSITION-CONTRACT resolution owner)
verifier_loop: parent-Claude verifier-loop (playbook §14 rule) 22 pre-Explore + 6 post-Explore + 4 SIGN-fold sub-verifier grep-checks all grep-verified against HEAD `20c75efd`. Rigby SIGN cycle 1 SIGN-with-edits at High confidence overall → **SIGN-clean-post-folds at High confidence** on fresh isolation pin `pa-4ce64003711de4f1` (retired at S1604 close). F1-F14 folds landed pre-commit. D48 preemptive stability-probe gate 13th arm HELD CLEAN across 3 batches + final-verdict — **eight-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604 CONFIRMED** — codification-ready-STRENGTHENED-FURTHER for playbook v3 §15.
---

# Session 1604 — Group 1600 Cat C: PublishGate + Publish Rails (Child Audit)

## 1. Executive Summary

Cat C is the fourth child audit under Group 1600 (Content Domain) after the F3 Rigby fold pre-lock reordering swap moved Cat C from P3 → P4 because Cat C's gate/rails semantics consume Cat D's canonical object-model decision (D65a-analog). This audit answers the parent-scoped boundary question *"what happens at the boundary?"* — gates, thresholds, eligibility, publish destinations, rails, failure modes, post-publish correction loops. Cat C does **NOT** own the Deliverable base object model, variants, or lifecycle states (those belong to Cat D S1603).

### 1.1 Headline findings

- **PublishGate is SelfBlog-only at HEAD.** `PublishGate.evaluate(blog)` at `core/services/publish_gate.py:112` and `apply_to_blog(blog)` at `:579` operate on `SelfBlog` instances exclusively. `SelfBlog` is imported at three sites (`:279` for novelty title-lookup, `:632` for the `evaluate_blog(blog_id)` convenience function, `:641` for `evaluate_all_drafts()` batch). No other variant models (SportsBettingBrief, BlockchainAuditBrief, OutreachDraft, ClosePack, Deliverable base) are ever imported into `publish_gate.py`. **D65b HEADLINE evidence contribution: publish-gate-scope posture is SelfBlog-only + narrow (island posture) at code layer.**

- **Triple-gate composition contract MISSING — Cat C RESOLUTION-SIDE RECORDED** (Cat D S1603 T.15.6 flagged; Cat C owns). Three structurally-independent quality-gate systems co-exist: (a) `deliverable_factory.py:358-411` 5-gate creation-time check (media_stub / smoke_pattern / min_length / template_leak / no_relevance), (b) `publish_gate.py:44-49` 4-threshold post-deliberation check (QUALITY 0.70 / NOVELTY 0.60 / STRUCTURE 0.55 / MYTHOLOGY 0.15), (c) `SelfBlog.quality_score` / `SelfBlog.novelty_score` / `SelfBlog.structure_score` schema fields on the variant itself (persisted at `models_unified_system.py:20709-20719`). No canonical precedence statement, no unified state machine specifying which gate reviews at which lifecycle stage, no observable failure mode when gates disagree. **F7+F11 Rigby fold reframe from S1603 preserved: the debt is "composition contract missing" not "too many gates".** Cat C records four candidate resolution paths (§17.4) for xx99 D65b consumption.

- **Publish rails are asymmetric.** Three rails exist for the SelfBlog variant only — (a) Frontend approve/publish endpoints at `views_research_demo.py:901-1000` (WORKING; enforced by `publish_ready` check at `:966` with `force=true` override); (b) Discord broadcast service at `discord_notifications.py:32-2319` (PARTIAL; 12 channel constants at `:36-47` with 11 unique Discord IDs — Session 460 comment at `:44` documents deliberate `CHANNEL_MARKET_ALERTS` = `CHANNEL_OPPORTUNITIES` ID reuse; PublishGate itself never calls `discord_notify` — gate decisions do NOT auto-broadcast); (c) Newsletter beat `generate-operator-edge-newsletter` at `celery.py:433` (EXPERIMENTAL; `dry_run=True` at `:436` per Session 1222 P6 2-Friday burn-in; task saves output as `Deliverable` NOT `SelfBlog` at `tasks_content.py:4353-4390`; ZERO SendGrid/mailgun/postmark/SMTP wiring in newsletter path — grep-verified). SportsBettingBrief has **0 publish rails** (write-only-forgotten CONFIRMED at HEAD via S1504 §14.3 + S1603 T.15.2). BlockchainAuditBrief has **0 Cat C-owned rails** (Discord alert path via `agents/blockchain/transaction_monitor_agent.py:795` bypasses gate). OutreachDraft has **0 outbound rail** (S1402 F.B1 F8-CRITICAL CONFIRMED at HEAD). ClosePack Cat C posture UNKNOWN (Revenue-domain-owned).

- **Newsletter dry_run promotion path UNKNOWN — Cat C SURFACES for D65c handoff.** `celery.py:436` hardcoded `kwargs: {'dry_run': True}` since Session 1222 P6 audit B2 re-enable. Comment at `:422-423` documents the intent "update kwargs to `{}` or `{'dry_run': False}` to promote to live publishing." Migration `0364` explicitly sets `dry_run=True` as "safe-by-default" (matches static entry). **Zero code path flipping to live-send at HEAD** (grep `dry_run.*[Ff]alse` in celery.py + tasks_content.py newsletter path returns only the comment line at celery.py:423 itself). **Zero live-send infrastructure**: grep `sendgrid|mailgun|postmark|smtplib|SMTP|EmailBackend` in `_impl_generate_operator_edge_newsletter` at `tasks_content.py:4234-4413` returns 0 hits — same pattern class as S1402 F.B1 OutreachDraft delivery ZERO outbound (F8 CRITICAL). Newsletter has been in EXPERIMENTAL dry_run posture for at least the burn-in window (S1222 P6 to present = >4mo). **D65c evidence contribution.**

- **Post-publish correction loops STRUCTURALLY ABSENT — Cat C-owned gap.** Grep across `core/` for `errata|retract|unpublish|revoke.*publish|delete_broadcast|discord.*edit_message` returns 0 hits in Cat C surfaces. `SelfBlog` `STATUS_CHOICES` at `models_unified_system.py:20639-20645` has no `retracted` / `unpublished` / `errata` value. Discord broadcasts are fire-and-forget at `discord_notifications.py:98-113` (`requests.post` with `timeout=10`; catches `Timeout` at `:107` and `RequestException` at `:110`; no retry, no message-ID persistence, no `BroadcastLog` model). **Once a SelfBlog is published or a Discord message fires, there is no code path to correct, retract, or amend.** Severity: **CRITICAL** structural gap (Cat C-owned).

- **Envelope validation DEAD CODE for SelfBlog** (F0-CORRECTION post-Explore verifier finding). `publish_gate.py:552-577` `_check_envelope(blog)` reads `blog.metadata['envelope']`, but **SelfBlog has no `metadata` model field** at `models_unified_system.py:20611-20770` (verified: only `stats_snapshot` JSONField at `:20742` exists; grep across `:20611-20770` returns zero `metadata` field declaration). `getattr(blog, 'metadata', None)` at `publish_gate.py:558` returns `None`, function returns empty string at `:560`. Session 960 Phase 0 aspirational code, never wired to SelfBlog persistence. **Safe (silent None fallback) but never fires.** Cat C-owned.

- **Newsletter task saves to `Deliverable`, NOT `SelfBlog`.** `_impl_generate_operator_edge_newsletter` at `tasks_content.py:4353-4390` creates a `Deliverable` row (not a `SelfBlog`). **PublishGate never touches the newsletter Deliverable.** This is a structural gap in the publish-gate contract: newsletter content bypasses the quality-gate entirely (it's dry_run-gated instead). If newsletter promotes to live-send, no PublishGate-analog exists for the newsletter Deliverable.

- **`force=true` bypass at REST publish endpoint** (Session 998). `views_research_demo.py:966` gates SelfBlog `status='published'` transition on `blog.publish_ready`; `force=true` body param at `:954` skips the check. **Cat C boundary rule surfaced**: PublishGate is advisory + REST endpoint is enforcement + admin/Rigby-side `force=true` is bypass. No `force=true` audit trail is persisted.

- **Redundant writer to `publish_ready`.** `PublishGate.apply_to_blog` at `:603` writes `blog.publish_ready = (result.decision == 'publish')`. `content_deliberation_runner.py:151` ALSO writes `blog.publish_ready = True` on Session 1008 fast-path (only if decision='PUBLISH' AND gate result is 'publish'). This is corroborative-not-conflicting (both paths write True in the same success condition), but it means two independent code paths flip `publish_ready` in the deliberation pipeline. If a future refactor changes the semantics at one site, the other diverges silently.

### 1.2 Decisions this audit records (D65b-analog + D65c-analog handoff to xx99)

Per playbook §14.5 no-implementation rule, Cat C **does not** select the posture. It records evidence for the xx99 posture-decision brief per D65b (PublishGate canonicalization scope) + D65c (lifecycle transition ownership + post-publish correction loop ownership).

- **D65b evidence axes for xx99:**
  - **B1 PublishGate scope canonicalization** — SelfBlog-only vs. extend to all Deliverable-variants (D65a-consuming). Current at HEAD: SelfBlog-only (verified §4 + §5).
  - **B2 Threshold canonicalization** — 4 thresholds are class constants (Session 1009/1003/864 tuning history); no per-env / per-content-type override mechanism at HEAD (§5.1 verified).
  - **B3 Operational-title-pattern canonicalization** — 25 regex patterns (11 original + 14 Session 1246 F1 additions per `publish_gate.py:58-85`); no config-file externalization; test-artifact false-positive risk documented (Session 1247).
  - **B4 Triple-gate composition contract MISSING** — Cat C records 4 candidate resolution paths (§17.4) but does not select.

- **D65c evidence axes for xx99:**
  - **C1 Newsletter dry_run promotion path UNKNOWN** — code lacks the flip; live-send infrastructure absent (§9.2).
  - **C2 Post-publish correction loops MISSING** — no model, no service, no event, no status enum value; Cat C-owned gap.
  - **C3 Discord broadcast audit trail MISSING** — no `BroadcastLog`, no message-ID persistence, no retry queue; failure modes silent (§8.6).
  - **C4 Frontend `force=true` bypass audit trail** — session-authenticated but no `force_publish_events` persisted; §15 T.15.C6.
  - **C5 REST-endpoint approve/publish contract vs. Rigby PA-tool** — canonical approve→publish alias registered per Session 1075/1077 (delegated to Cat E S1605 tool-surface audit); Cat C flags cross-arc.

- **Cross-arc handoff records (Cat C receives + emits):**
  - **RECEIVES from Cat D S1603**: T.15.6 triple-gate composition contract MISSING (Cat C owns resolution recording; §17.4 4-candidate framework).
  - **RECEIVES from Cat A S1601**: SelfBlog.objects.create bypass at `content_deliberation_runner.py:401` — Cat C confirms gate is advisory + post-hoc; SelfBlog exists BEFORE gate runs (§7.1 flow trace).
  - **RECEIVES from Cat B S1602**: DecisionEnforcer produces PUBLISH/REVISE/KILL mandate; Cat C confirms gate only runs when decision='PUBLISH' at `content_deliberation_runner.py:138`; REVISE and KILL bypass gate entirely (§7.1).
  - **RECEIVES from S1504 §14.3**: SportsBettingBrief WRITE-ONLY-FORGOTTEN — Cat C confirms no publish rail exists for SportsBettingBrief; extends Cat D T.15.2 CRITICAL.
  - **RECEIVES from S1402 F.B1**: OutreachDraft delivery ZERO outbound — Cat C confirms same pattern class extends to newsletter and (if extended posture selected) to blog+podcast rails.
  - **RECEIVES from S1403 F.C4**: ContentEngagement docstring drift — Cat C confirms no post-publish feedback loop from Discord/Newsletter/Frontend to `ContentEngagement`; extends Cat D §14.1.
  - **EMITS to Cat E S1605**: post-publish approval UX + `force=true` bypass audit trail + Rigby PA-tool contract on publish-rail actions.
  - **EMITS to Cat F S1606**: three axis D65b/D65c evidence for cross-domain lens.
  - **EMITS to xx99 S1699**: D65b + D65c evidence + T1 R.CONTENT.TRIPLE-GATE-COMPOSITION-CONTRACT canonicalization owner recommendation.

### 1.3 Maturity verdict

**Cat C overall: PARTIAL.** The core `PublishGate` class + `apply_to_blog` contract is STABLE (Session 862 origin; four+ threshold tunings landed 864/997/1000C/1003/1004/1009; no regressions detected at HEAD). But three downstream rails are stratified: Frontend approve/publish is WORKING (user-facing; enforced), Discord broadcast integration is PARTIAL (service exists + zero broadcast triggered from PublishGate), Newsletter is EXPERIMENTAL (dry_run indefinitely parked), and post-publish correction is MISSING (structural gap). Cross-arc SportsBettingBrief / BlockchainAuditBrief / OutreachDraft publish rails are all MISSING or Revenue/Sports/Blockchain-domain-owned outside Cat C scope.

### 1.4 Cat C authority scope reminder (parent F2 boundary)

Cat C is the *"what happens at the boundary?"* category per parent F2 Rigby fold. Cat C owns:

- All quality-gate + publish-rail output-layer surfaces (PublishGate, apply_publish_gate mgmt command, evaluate_unscored_blogs task, publish REST endpoint enforcement, publish-rail beat schedule).
- Publish destinations + rails + failure modes (Discord broadcast integration in gate context; Newsletter beat gate; Frontend approve/publish contract enforcement).
- Post-publish correction loops (errata/retract/republish — currently absent).
- **Cat C does NOT own**: Deliverable base object model (Cat D); SelfBlog variant persistence schema (Cat D flags); reviewer verdicts / DecisionEnforcer contract (Cat B); Rigby PA-tool surface (Cat E); ClaimsPack + deliberation pipeline mechanics (Cat A). Where Cat C surfaces cross-boundaries, `§16 Boundary Violations` records the touch-point + owner.

### 1.5 Enforcement-authority contract (F2 Rigby fold — first-class boundary rule)

**Three actors participate in the publish-eligibility decision; only one is authoritative.**

- **`PublishGate` is ADVISORY.** The class at `publish_gate.py:27` scores + suggests + writes back to SelfBlog fields (via `apply_to_blog:597-615`), but does not itself gate any external side-effect. Blog can exist + be edited + be re-scored + get any decision arbitrarily; nothing external happens as a direct consequence of `PublishGate.evaluate` running.
- **REST publish endpoint is ENFORCEMENT.** `views_research_demo.py:966-971` is the actual code line that gates `status='published'` transition on `blog.publish_ready`. Session 998 point of enforcement. If `publish_ready=False`, the endpoint returns 400 + `gate_notes` in error body.
- **`force=true` REST body param is ADMIN BYPASS.** `views_research_demo.py:954` accepts `force=true`; if present, `:966-971` check is skipped. **No `ForcedPublishEvent` audit trail is persisted** — bypass is ephemeral (T.15.C6 MEDIUM).
- **`auto_publish_approved_blogs` beat at `tasks.py:8056-8079` is a FOURTH actor** that bypasses BOTH `PublishGate` AND REST endpoint. It flips `status='published'` in-model directly via `save(update_fields=['status'])` at `:8075` on any SelfBlog matching `status='approved' + publish_ready=True`. No shared publish helper; no `AutoPublishEvent`; only log line `[AUTO-PUBLISH]` at `:8077`. This is a legitimate automation path (blogs already gate-passed) but bypasses REST audit trail (D.14.C5 MEDIUM).

**Boundary contract restated for xx99 consumption:** PublishGate is a *scoring service*, not a *gate*. The gate lives at the REST endpoint. Admin bypass lives at `force=true`. Automated bypass lives at the beat task. **All four actors must be audited, and post-publish irreversibility (§16.1) applies to any of the four causing a state transition to `published`.**

---

## 2. Domain Purpose

### 2.1 What is PublishGate + Publish Rails?

PublishGate is Session 862's quality-gate infrastructure sitting immediately downstream of the v2 Content Deliberation Pipeline. When ContentWriterAgent → 3-reviewer panel → DecisionEnforcer produces a `decision='PUBLISH'` mandate for a SelfBlog, PublishGate scores the draft on four dimensions (quality, novelty, structure, mythology) and issues a terminal classification: `publish` / `enhance` / `internal_only`. On `publish`, downstream automation promotes the blog to `status='approved'` + `publish_ready=True`; on `enhance`, EditorAgent takes another pass; on `internal_only`, the blog is retained as a build-log-style artifact.

The **publish rails** are the outbound-side channels that carry approved content to external audiences:
- **Frontend approve/publish**: `BlogViewerPage.tsx:45` + `blogsApi.ts:3921-3962` mutations flip `status='published'` via REST endpoint at `views_research_demo.py:943-1000`.
- **Discord broadcast**: `discord_notifications.py` service publishes to 12 channels (11 unique IDs); PublishGate itself does NOT call Discord — broadcast is upstream (agent-side) and NOT gated by PublishGate for SelfBlogs.
- **Newsletter**: `generate-operator-edge-newsletter` Celery beat at `celery.py:433` produces a Deliverable (not a SelfBlog) on Fridays 06:00 Denver; `dry_run=True` gates the outbound send since Session 1222 P6.

### 2.2 What Cat C is NOT

Cat C is not about *deciding what content to write* (that's Cat A ClaimsPack + Cat B reviewers). Cat C is not about *what the object IS* (that's Cat D — Deliverable base + variants). Cat C is not about *how Rigby operates the surface* (that's Cat E). Cat C is only about *how content leaves the system at the boundary + what happens when it's out*.

### 2.3 Historic session timeline

Cat C's structure grew across 12+ sessions. Full timeline in §12.4 handoff pointer table.

- **Session 862** — PublishGate origin (`publish_gate.py` created; migration `0206_session_862_content_intelligence.py` added `quality_score`, `novelty_score`, `structure_score`, `content_type`, `publish_ready`, `gate_notes` fields to `SelfBlog`).
- **Session 864** — Operational-title auto-classify + STRUCTURE_THRESHOLD lowered from 0.65 to 0.55.
- **Session 997** — Mythology cap at 'enhance' via `MythologyDetectionService` integration.
- **Session 998** — REST publish endpoint enforcement + `force=true` override.
- **Session 1000C** — Publish decision → `status='approved'` promotion path (§7.4 auto_publish_approved_blogs beat).
- **Session 1003** — MYTHOLOGY_THRESHOLD lowered from 0.5 to 0.15 (mythology detection too aggressive; blocking all AI-generated content).
- **Session 1004** — Novelty algorithm strengthened; cumulative-penalty exact-match -0.25.
- **Session 1008** — Content deliberation runner Session 1008 fast-path: gate 'publish' → status='approved' + publish_ready=True + content_type='public' (redundant writer to apply_to_blog).
- **Session 1009** — QUALITY_THRESHOLD raised from 0.65 back toward 0.75 (settled at 0.70 at HEAD).
- **Session 1033** — Deliverable quality-scoring backfill (`score_unscored_deliverables` task); EditorAgent finishing loop.
- **Session 1075/1077** — blog_tool split from content_tool; approve→publish alias added.
- **Session 1147** — `content-pipeline.md` topic doc landed.
- **Session 1222 P6** — Newsletter beat re-enabled with `dry_run=True` 2-Friday burn-in.
- **Session 1228 P3** — Newsletter Denver-TZ crontab fix (`hour=6` Denver = 12:00 UTC MDT / 13:00 UTC MST).
- **Session 1246 F1** — Operational-title patterns expanded to cover E2E test artifacts (BLOGTOOL_E2E_v1, Verify Your, Platform QA Pass N, e2e_/smoke_/qa pass N/test run/integration|regression test).
- **Session 1247** — Audit caught 3 test artifacts stuck `publish_ready` for 175-358h.

---

## 3. Canonical Entry Points

### 3.1 Core service class

- `core/services/publish_gate.py:27` — `class PublishGate` (668 lines total file; class body :27-627).

### 3.2 Convenience module functions (in `publish_gate.py`)

- `evaluate_blog(blog_id: str) -> GateResult` at `:630`.
- `evaluate_all_drafts() -> List[Tuple[str, GateResult]]` at `:639`.
- `get_gate_summary() -> dict` at `:654`.

### 3.3 GateResult dataclass

- `core/services/publish_gate.py:14-24` — `@dataclass class GateResult` — fields: `decision` (str: publish/enhance/internal_only), `quality_score` (float), `novelty_score` (float), `structure_score` (float), `content_type` (str: public/internal/strategic), `notes` (str), `mythology_score` (float, default 1.0), `suggested_category` (Optional[str]).

### 3.4 SelfBlog-side gate-related fields (Cat D-owned; Cat C reads/writes)

Verified via `models_unified_system.py:20611-20770` sweep:

- `quality_score` at `:20709-20712` (FloatField 0-1).
- `novelty_score` at `:20713-20716` (FloatField 0-1).
- `structure_score` at `:20717-20720` (FloatField 0-1).
- `content_type` at `:20698` (CharField, choices per SelfBlog CATEGORY_CHOICES incl. `blog`, `build_log`, `internal_note`, `playbook`, `dossier`, `audit`, `research_brief`).
- `gate_notes` at `:20725` (TextField, semi-structured `; `-delimited).
- `publish_ready` at `:20721-20724` (BooleanField default False; help_text "if passed PublishGate checks").
- `status` at `:20706` (CharField(20), choices per STATUS_CHOICES at `:20639-20645`; default `draft`; db_index=True).
- `stats_snapshot` at `:20742` (JSONField default dict; help_text "System stats when blog was generated"; consumed by `_check_research_backing` reading `.deliberation.claims_count`).
- **VERIFIED F0-CORRECTION: SelfBlog has NO `metadata` field.** Sweep `:20611-20770` returned zero `metadata = models.<...>` declaration. `_check_envelope` at `publish_gate.py:552-577` is dead code for SelfBlog.

### 3.5 REST endpoints — publish rail

Verified via `core/views_research_demo.py` reads:

- **`POST /api/v1/research/self-blog/<uuid:blog_id>/approve/`** at `core/views_research_demo.py:901` → `approve_self_blog_api()` — status `draft`/`pending_review`/`needs_enhancement` → `approved`. No PublishGate call.
- **`POST /api/v1/research/self-blog/<uuid:blog_id>/publish/`** at `:943` → `publish_self_blog_api()` — status `approved` → `published`. **Session 998 PublishGate enforcement**: `if not force and not blog.publish_ready` at `:966` returns 400 with `gate_notes` in error body. `force=true` at `:954` bypasses the check.
- **`POST /api/v1/research/self-blog/<uuid:blog_id>/enhance/`** at `:1004` → `enhance_self_blog_api()` — triggers async `enhance_blog_task` Celery task (EditorAgent); does NOT invoke PublishGate directly.
- **Additional read endpoints (Cat E-adjacent; not Cat C boundary):** blog list, detail, delete, related — Cat E will own contract audit; Cat C flags cross-boundary.

### 3.6 Management commands — publish rail

- **`core/management/commands/apply_publish_gate.py`** — 248 lines. Manual invocation. Modes: `--all`, `--drafts-only`, `--blog-id <UUID>`, `--summary`, `--dry-run`, `--reclassify` (auto-categories internal content). Idempotent (re-run overwrites scores). **NOT beat-scheduled** at HEAD (grep in `celery.py` beat_schedule returns zero `apply_publish_gate` references).

### 3.7 Celery tasks + beat schedule — publish rail

- **`generate-operator-edge-newsletter`** at `core/celery.py:433` — task `core.tasks.generate_operator_edge_newsletter` → `_impl_generate_operator_edge_newsletter` at `tasks_content.py:4234`. Cron: `crontab(hour=6, minute=0, day_of_week='friday')` at `:435` — Fri 06:00 Denver (12:00 UTC MDT / 13:00 UTC MST per Session 1228 P3). Queue: `content`. **kwargs: `{'dry_run': True}`** at `:436` (Session 1222 P6 burn-in). Options: `expires: 3600`.
- **`evaluate_unscored_blogs`** at `core/tasks.py:8017-8061` — batch task; iterates `SelfBlog.objects.filter(quality_score__isnull=True)`; applies `PublishGate().apply_to_blog(blog)`; no dry_run semantics; runs on `content-review-automation` beat per Session 1000C. Verified via grep.
- **`auto_enhance_blogs` + `reevaluate_enhanced_blogs` + `auto_publish_approved_blogs`** — Session 1000C content-review-automation triad (per `docs/topics/content-pipeline.md:166-190`). Runs on cadence covering all-blogs sweep (2h) + enhancement pipeline + auto-publish.
- **`cleanup_stale_content`** at `celery.py:176` — daily 10:05 AM; filters `status__in=['ready', 'draft']`. Not publish-rail per-se but cleans partially-through-pipeline artifacts.
- **`sweep_diagnostic_deliverables`** and **`score_unscored_deliverables`** — publish-adjacent; Cat D-owned per S1603 §7.3.

### 3.8 PA tools — publish rail contract (Cat E-adjacent; Cat C boundary)

Cat E owns full tool-surface audit (S1605). Cat C flags:
- `content_tool` gateway at `td_handlers_content.py:4294-4473` — actions: `content_approve` (→ `content_review_tool:approve`), `content_reject` (→ `:reject`), `content_complete` (→ `:complete`; Session 1170 terminal state; NOT external-publish; internal-analysis-only marker); `generate_blog` (→ `generate_blog_tool` writer); `generate_newsletter` (direct Celery dispatch to `core.tasks.generate_operator_edge_newsletter`).
- `blog_tool` at `td_handlers_content.py:162-182` — `approve`/`reject` aliases, `stats`/`list`/`detail`/`search`/`recent`, `generate`.
- `newsletter_tool` at `td_handlers_newsletter.py:25-163` — actions: `prepare` (transforms issue Deliverable → 3 publish-ready artifacts: markdown/HTML/checklist; does NOT invoke PublishGate), `outline`/`validate`/`metrics`/`list_issues`/`config`/`sources`.
- `deliverable_tool` at `td_handlers_content.py:84-161` — publish-rail-relevant actions: `set_status` (can flip to `published`/`completed`; memory rule `feedback_deliverable_status_via_content_complete.md` — routes through `content_tool.content_complete` for completed status), `export_pdf` (publish-rail per S1603 §6.5 D62 pre-brief), `link_initiative`/`unlink_initiative` (publish-side organization).

### 3.9 Frontend surface (Cat E-adjacent; Cat C boundary)

- `frontend/src/pages/BlogViewerPage.tsx:81-102` — `approveMutation` calls `blogsApi.approve(blogId)`; `publishMutation` calls `blogsApi.publish(blogId, force)`. No client-side gate preview (gate is server-authoritative).
- `frontend/src/lib/api.ts:3921-3962` — `blogsApi.approve` / `blogsApi.publish` REST wrappers.

### 3.10a `publish_ready` writer surface — canonical + redundant (F3 Rigby fold)

Two independent code paths write `SelfBlog.publish_ready`:

- **Canonical writer**: `PublishGate.apply_to_blog` at `publish_gate.py:603` — `blog.publish_ready = (result.decision == 'publish')`. Called from mgmt cmd, evaluate_unscored_blogs beat, content_writer_agent auto-run, and tasks_content.py self-blog gen.
- **Redundant Session 1008 fast-path writer**: `content_deliberation_runner.py:151` — `blog.publish_ready = True`, called only within the PUBLISH-branch at `runner.py:138-152`.

**Non-conflicting today** (both write True in the same success condition) but **divergence hazard** if future refactor changes semantics at one site (D.14.C4 LOW).

### 3.10b Gate-evaluation triggers + failure modes (F4 Rigby fold)

Cat C-owned gate is evaluable from FIVE trigger surfaces:

| Trigger | File:line | Cadence | Failure mode |
|---------|-----------|---------|--------------|
| Manual mgmt cmd `apply_publish_gate` | `apply_publish_gate.py` (248 lines) | on-demand (manual invocation) | If never run: gate silently skipped. No SLA. |
| `evaluate_unscored_blogs` beat | `tasks.py:8017-8061` | 2h cycle | First-pass-only (see §7.4 F14 clarification) |
| `content_deliberation_runner._run_publish_gate` | `runner.py:140` | Per-decision (only if PUBLISH) | Wrapped in try/except at `:139-159`; failure logs warning + blog persists un-gated |
| `content_writer_agent` auto-run | `content_writer_agent.py:1451-1458` | Per-agent-invocation | Failure logs warning; does not block |
| `tasks_content.py` self-blog gen | `tasks_content.py:2345-2355` | Per-task-fire | Exception → warning log; blog stays draft |

**Cross-cutting failure modes:**
- Celery worker down → `evaluate_unscored_blogs` + `auto_publish_approved_blogs` beats silently drop.
- Task retry policy not verified at HEAD — no `autoretry_for=` decorators grepped on gate tasks (T.15.C4 test-coverage gap).
- Idempotency: gate is idempotent (re-run overwrites same fields). `auto_publish_approved_blogs` is idempotent (query filters `status='approved'` so re-published blogs are excluded next run).

### 3.10 Discord broadcast service

- `core/services/discord_notifications.py:32-2319` — `class DiscordNotifier` (or equivalent singleton). 12 channel constants at `:36-47`:

| Constant | Discord ID | Session | Public/Internal |
|----------|-----------|---------|-----------------|
| `CHANNEL_DREAMS` | `1448809858274033684` | (foundational) | Internal (agent dreams) |
| `CHANNEL_CONVERSATIONS` | `1448809914783895583` | (foundational) | Internal (agent conversations) |
| `CHANNEL_STATUS` | `1448809955326169149` | (foundational) | Internal (system status) |
| `CHANNEL_LEARNING` | `1448819275459465257` | (foundational) | Internal (agent learning) |
| `CHANNEL_BOARDROOM` | `1448819855557136595` | (foundational) | Internal (executive decisions) |
| `CHANNEL_OPPORTUNITIES` | `1448867150948335777` | Session 424 | **Public-ish** (high-value opportunity alerts) |
| `CHANNEL_GALLERY` | `1449059813765021859` | Session 430 | User (gallery image delivery) |
| `CHANNEL_PROFILE` | `1449059839581098135` | Session 430 | User (profile channel) |
| `CHANNEL_MARKET_ALERTS` | `1448867150948335777` | Session 460 | **Public** (SEC filings; **shares ID with OPPORTUNITIES** per comment) |
| `CHANNEL_STOCK_ALERTS` | `1450589539562426418` | Session 461 | **Public** (stock audit alerts) |
| `CHANNEL_BLOCKCHAIN_ALERTS` | `1450589795058192465` | Session 461 | **Public** (blockchain audit alerts) |
| `CHANNEL_PODCAST_LIBRARY` | `1451601597007134821` | Session 496 | **Public** (podcast library) |

**F0-VERIFIED: 12 constants; 11 unique Discord IDs; `CHANNEL_OPPORTUNITIES` + `CHANNEL_MARKET_ALERTS` deliberately share ID `1448867150948335777` per Session 460 comment "shares with opportunities".**

---

## 4. Major Models

### 4.1 `GateResult` dataclass

`core/services/publish_gate.py:14-24`. Transient dataclass — not persisted. Fields listed in §3.3.

**Persistence path:** After PublishGate evaluates a SelfBlog, `apply_to_blog` at `:597-603` copies GateResult fields to SelfBlog model fields + saves. GateResult itself is discarded.

**Field-parity check** (verified via read):

| GateResult field | SelfBlog persisted field | apply_to_blog line |
|------------------|-------------------------|---------------------|
| `decision` | (transformed into `status` + `publish_ready` semantics; not directly persisted) | :603, :605-615 |
| `quality_score` | `SelfBlog.quality_score` | :598 |
| `novelty_score` | `SelfBlog.novelty_score` | :599 |
| `structure_score` | `SelfBlog.structure_score` | :600 |
| `content_type` | `SelfBlog.content_type` | :601 |
| `notes` | `SelfBlog.gate_notes` (potentially concatenated with envelope-notes at :595) | :602 |
| `mythology_score` | **NOT PERSISTED** — mythology score is transient/log-only | (no persistence at HEAD) |
| `suggested_category` | Overrides `SelfBlog.category` if current is `blog` at :618-620 | :618-620 |

**Finding: `mythology_score` is not persisted.** After a blog's mythology score gates the decision (line 458 `if mythology_score < MYTHOLOGY_THRESHOLD`), the score itself is only logged at `:174` and never persisted to SelfBlog. Later analysis (e.g., "which blogs had mythology risk over time?") requires re-running the gate. **T.15.C7 in §15.**

### 4.2 SelfBlog model — Cat C-relevant field surface

**Cat D-owned model** at `core/models_unified_system.py:20611+`. Cat C reads + writes these fields:

| Field | Line | Type | Cat C read | Cat C write | Notes |
|-------|------|------|-----------|-------------|-------|
| `id` | (implicit UUIDField) | UUID | ✓ (evaluate_blog(blog_id)) | ✗ | |
| `title` | :20693 | CharField(255) | ✓ (operational-title check + novelty; publish_gate.py:186-194, :288-290) | ✗ | Lowercased for regex match |
| `meta_description` | :20730 | TextField | ✓ (full text) | ✗ | |
| `intro` | :20731 | TextField | ✓ (full text + quality-score bonus at :239-240) | ✗ | |
| `sections` | :20732 | JSONField | ✓ (section variety scoring at :344-355; structure-score) | ✗ | List of `{header, content}` dicts |
| `conclusion` | :20733 | TextField | ✓ (full text + quality-score bonus at :243-244) | ✗ | |
| `full_text` | :20735 | TextField | ✓ | ✗ | Fallback text |
| `word_count` | :20739 | IntegerField | ✓ (quality-score hard-reject <300 at :230-232) | ✗ | Cached (may re-compute at :229) |
| `category` | :20698 | CharField (choices) | ✓ (`_classify_content_type` internal signal at :419-425; `_suggest_category` at :505-517) | ✓ (`_suggest_category` overrides `category` if currently `blog` at :618-620) | |
| `metadata` | **NOT DEFINED** | — | ✗ (dead: :558 `getattr(blog, 'metadata', None)` returns None) | ✗ | **F0-CORRECTION: envelope validation is dead code** |
| `stats_snapshot` | :20742 | JSONField (default dict) | ✓ (`_check_research_backing` reads `.deliberation.claims_count` at :519-527) | ✗ | Read-only from Cat C; Cat A writes via `content_deliberation_runner.py:381-416`; Cat B extends `.deliberation` per S1602 §16.1 |
| `quality_score` | :20709 | FloatField(0-1) | ✓ (persisted by apply_to_blog) | ✓ (:598) | Cat D T.15.6 triple-scoring |
| `novelty_score` | :20713 | FloatField(0-1) | ✓ | ✓ (:599) | Cat D T.15.6 |
| `structure_score` | :20717 | FloatField(0-1) | ✓ | ✓ (:600) | Cat D T.15.6 |
| `content_type` | :20698 | CharField | ✓ | ✓ (:601) | public / internal / strategic |
| `gate_notes` | :20725 | TextField | ✓ (returned in publish-endpoint error body at :970) | ✓ (:602; appended with envelope notes at :595) | Semi-structured `; `-delimited |
| `publish_ready` | :20721 | BooleanField | ✓ (REST publish gate at views_research_demo.py:966) | ✓ (apply_to_blog:603 + content_deliberation_runner.py:151 redundant writer) | Cat C-owned enforcement flag |
| `status` | :20706 | CharField(20) | ✓ (state machine input at :605-615) | ✓ (`draft`→`draft`/`needs_enhancement`/`approved`) | Cat D T.14.4 status='completed' 5th value NOT applicable to SelfBlog (SelfBlog has own STATUS_CHOICES) |
| `mythology_score` | **NOT DEFINED** | — | (transient; discarded) | ✗ | T.15.C7 not-persisted |

**§4.2.1 SelfBlog STATUS_CHOICES verification:**

Verified via `models_unified_system.py:20639-20706` grep sweep. `STATUS_CHOICES = [` at `:20639`; `status = models.CharField(...)` at `:20706`. Choices values were not read line-by-line in this audit — flagged as UNK-1 for post-Explore verification if Rigby SIGN requests it.

**§4.2.2 SelfBlog class body has NO `metadata` field — VERIFIED F0-CORRECTION + F1 Rigby fold proof-precision tightening**

Grep sweep across **SelfBlog class body (`:20611-20790`)** enumerated 27 model-field declarations (id / workspace / trace_id / project / initiative / dream / initiative_stage / title / author / category / content_type / status / quality_score / novelty_score / structure_score / publish_ready / gate_notes / meta_description / intro / sections / conclusion / tags / full_text / tone / word_count / stats_snapshot / created_at + additional fields at `:20748+`). **NONE of the SelfBlog-declared fields is `metadata = models.<FieldType>(...)`.** Only `stats_snapshot = models.JSONField(default=dict, ...)` at `:20742` is JSONField-typed; the "Generation metadata" text at `:20737` is a section-header comment, not a field declaration.

**F1 Rigby fold proof-precision correction pre-fold**: earlier draft phrased this as "models_unified_system.py has no metadata field," which is misleading — the file DOES contain `metadata = models.JSONField(default=dict)` fields at `:1191, :1249, :3096, :3468` on OTHER model classes (verified via Rigby SIGN Batch A independent grep). **The narrower + correct claim is: SelfBlog class body specifically does NOT declare `metadata`.** The bounded-grep evidence in §20.3 verifier-loop entry #23 is grep-verified against the SelfBlog block; earlier phrasing in this section is now tightened.

Consequence: `publish_gate.py:552-577` `_check_envelope(blog)` is dead code for SelfBlog. `getattr(blog, 'metadata', None)` at `:558` returns None; function returns empty string at `:560`. Session 960 Phase 0 aspirational infrastructure; never wired to SelfBlog persistence.

### 4.3 Variant models with own quality/publish-state fields (Cat D-owned; Cat C boundary)

- **SportsBettingBrief** at `core/models_unified_system.py:18394-18427` — fields include `brief_date`, `predictions`, `arbitrage_opportunities`, `sharp_action_alerts`, etc. **No `publish_ready`, no `quality_score`, no `content_type` fields** (verified S1603 §4.2 + Explore 1 F11.1). **Not gated by PublishGate.**
- **BlockchainAuditBrief** at `core/models_unified_system.py:18435-18466` — similar shape. **No publish-state fields.** **Not gated by PublishGate.**
- **OutreachDraft** at `core/models_outreach.py:18` — has `status` (`draft`/`approved`/`sent`), no `publish_ready`, no quality-scoring fields. Revenue-domain-owned; Cat C flags cross-arc gap.
- **ClosePack** at `core/models_close_pack.py:20` — has `status` and lifecycle FKs; Revenue-domain-owned; publish-rail contract UNKNOWN for Cat C.
- **Deliverable** base at `core/models_deliverables.py:84` — has `quality_score`, `status`, `publish_intent` enum (Cat D-owned). **Not gated by PublishGate at HEAD.** Cat D T.15.5 factory-bypass migration would still land Deliverable outside PublishGate scope; extending PublishGate to Deliverable base would be a D65b posture selection.

### 4.4 NewsletterSubscriber model (partial persistence)

- **`NewsletterSubscriber`** at `core/models_newsletter.py:8-31` — persisted subscriber list (email, source, referral, UTM tracking). **No `NewsletterIssue` model** at HEAD (Explore 1 F7.1 grep-verified: `grep 'class NewsletterIssue|class OperatorEdgeNewsletter'` returns 0 hits).
- **`_impl_generate_operator_edge_newsletter` at `tasks_content.py:4353-4390`** saves newsletter output as a **`Deliverable`** row (not a SelfBlog, not a NewsletterIssue). **Structural finding: newsletter is a Deliverable-shaped artifact stored without a dedicated variant model + without PublishGate + without live-send infrastructure.** Newsletter is thus **Cat D-owned as a Deliverable + Cat C-owned as a rail**.

### 4.5 Missing persistence models — Cat C-owned structural gap (F8 Rigby fold — verified against generic naming patterns)

Bespoke class names — grep-verified 0 hits:

- **`PublishGateEvent`** — 0 hits. No per-decision event persistence; gate outcomes are only logged at `publish_gate.py:174` (line "PublishGate: {title}... -> {decision} (Q:..., N:..., S:..., M:...)"). §5.5 debt T.15.C1.
- **`BlogPublishedEvent`** — 0 hits.
- **`ContentBroadcastEvent`** — 0 hits.
- **`BroadcastLog` / `DiscordMessage`** — 0 hits. Discord broadcasts fire-and-forget.
- **`NewsletterIssue`** — 0 hits. Newsletter issues are Deliverables; no dedicated model.
- **`BlogErratum` / `RetractionEvent`** — 0 hits. No post-publish correction model. §16.1 CRITICAL.

**F8 Rigby fold — proven-negative extended to generic-name patterns:**

Also grep-verified across `core/` for generic patterns that could indicate SelfBlog-side publish-rail audit-trail models under different naming conventions: `Broadcast|discord_message_id|published_at|outbound|notification_log|DeliverableEvent` — 75 total occurrences across 20 files. Sampled key candidates:

- `core/signals/deliverable_status_signals.py` — Deliverable-side status transitions ONLY (0 `SelfBlog` references at HEAD — grep-verified). Does not audit SelfBlog publishes.
- `core/models_deliverables.py` — `DeliverableEvent` is Cat D-owned; audits Deliverable state transitions, NOT SelfBlog publishes.
- `core/models_content_pipeline.py` — pipeline-run-scoped models; not publish-rail audit trail.
- `core/models_narrative_drift.py` — narrative drift telemetry; not publish-rail.
- `core/models_ai_series.py` — series metadata; not publish-rail.

**Verdict:** No SelfBlog-side publish-rail audit trail exists under bespoke OR generic naming at HEAD. Log lines are the only observability signal. §10 event-flow gap CONFIRMED via extended verification per Rigby fold F8.

### 4.6 Cat C-relevant migrations

- **`core/migrations/0206_session_862_content_intelligence.py`** — Session 862 origin migration. Added 6 fields to SelfBlog (`quality_score`, `novelty_score`, `structure_score`, `content_type`, `publish_ready`, `gate_notes`). Modified STATUS_CHOICES to add `needs_enhancement` + `pending_review`. Modified CATEGORY_CHOICES to add internal-content categories (`build_log`, `internal_note`, `playbook`, `dossier`).
- **`core/migrations/0364_...`** — Newsletter beat re-enable migration; sets `PeriodicTask` row `enabled=True` + `kwargs={'dry_run': True}` matching static entry per Session 1222 P6 comment at `celery.py:418-423`. Referenced in §2.3 timeline.
- **No follow-up migrations** at HEAD for `mythology_score` persistence, `metadata` field addition, `NewsletterIssue` model, `BroadcastLog` model, or post-publish correction model. Backfill migrations for retroactive scoring of pre-existing SelfBlogs: 0 grep hits.

### 4.7 Docstring vs code alignment (drift check)

| Surface | Docstring claim | Runtime reality | Drift? |
|---------|-----------------|-----------------|--------|
| `PublishGate.evaluate` at :112 | "Evaluate a SelfBlog for publishing readiness" | Verified SelfBlog-only at HEAD | none |
| `apply_to_blog` at :579 | Comment "Session 1000C: Promote publish-ready blogs to 'approved'" | Verified :613-615 does exactly that | none |
| `PublishGate` class :27 | "Quality gate for content before publishing. Evaluates: 1. Content quality 2. Novelty 3. Structure 4. Content type" | Runtime evaluates 4 dimensions **plus** mythology (:143); docstring understates by 1 dimension | **MINOR** drift — mythology missing from summary bullets |
| `MYTHOLOGY_THRESHOLD` comment :47-49 | "Lowered from 0.5 — MythologyDetectionService gives 0.55-1.0 risk on ALL AI-generated content, blocking every blog from publishing." | MythologyDetectionService at `mythology/services.py` active at HEAD; loads patterns from DB (`MythPattern.objects.filter(is_active=True)` at :53); no deprecation | none |
| `_check_research_backing` docstring at :521 | "Returns -1 if no deliberation metadata (non-pipeline blog), else claims_count" | Verified; caller at :146-149 penalizes only on `claims_count == 0`, so -1 skips penalty | none |
| Discord channel constants Session comments | Session 424/430/460/461/496 dated origins | Constants present; sessions ratified; no evidence of rename/archive | none |
| Newsletter beat comment at celery.py:417-423 | "Session 1222 P6 (audit B2) — re-enabled with dry_run=True for the 2-Friday burn-in ... After burn-in passes, update kwargs to {} or {'dry_run': False} to promote to live publishing." | **DRIFT** — burn-in was 2 weeks; current elapsed ~4+ months since S1222; kwargs still `{'dry_run': True}` at :436; no promotion PR/handoff found | **DRIFT** — burn-in overrun; codified in D.14.C2 |
| Comment at publish_gate.py:552-577 `_check_envelope` | "Session 960 Phase 0: Check for AgentOutputEnvelope in blog metadata" | **DRIFT** — SelfBlog has no `metadata` field; function always returns empty string; DEAD CODE | **DRIFT** — codified in D.14.C3 |
| Session 1246 F1 comment lines 51-85 | "tightened from initial pass after smoke-test" | Verified — 14 additions to OPERATIONAL_TITLE_PATTERNS covering E2E/QA/smoke/verify_your patterns | none |

### 4.8 Pre-brief mini-schema — D62 = (a) 6-sibling exemplar applied

Per parent D68 F8/F10 folds — **fourth Group 1600 sibling to propagate the pattern upfront** after S1601 first + S1602 second + S1603 third. The D65-analog evidence contribution mini-schema per model surface:

| Surface | Ownership axis | Cat D decides? | Cat C posture-decision handoff |
|---------|---------------|---------------|--------------------------------|
| **PublishGate class** | Behavioural (gate mechanics) | NO | Cat C owns; D65b B1 scope canonicalization (SelfBlog-only vs. extend to variants) |
| **`apply_to_blog` SelfBlog-side field mutations** | Structural (schema fields) | YES (Cat D flagged in S1603 §17.2 triple quality-scoring) | Cat C confirms Cat D's structural framing; D65b B4 triple-gate composition contract MISSING |
| **`_check_envelope` dead code** | Structural (schema — SelfBlog missing `metadata` field) | YES (Cat D flags; per S1603 §4.7 no drift at HEAD in the model itself — Cat C surfaces envelope-side gap) | Cat C flags; D65c evidence for envelope contract sunset OR field-addition decision |
| **`mythology_score` not persisted** | Behavioural | Neither Cat D nor Cat C sole-owner; joint | Cat C owns proposal; D65b B2 threshold canonicalization consequence |

---

## 5. Major Services

### 5.1 `core/services/publish_gate.py` (668 lines, WITHIN god-service threshold)

**Class `PublishGate` at `:27`. Class body :27-627.**

Public methods:
- `evaluate(blog) -> GateResult` at `:112-176` — orchestrator; runs operational-title bypass check, then scores 4 dimensions, then makes decision, then suggests category.
- `apply_to_blog(blog, save=True) -> GateResult` at `:579-626` — runs `evaluate`, appends envelope-check notes, writes GateResult fields to SelfBlog + status flip + optional save.

Private scoring methods:
- `_is_operational_title(title) -> bool` at `:178-194` — regex match on 25 patterns at `:58-85` (11 original + 14 Session 1246 F1 additions).
- `_get_full_text(blog) -> str` at `:196-214` — concatenates title/meta/intro/sections/conclusion/full_text lowercased.
- `_score_quality(blog, full_text) -> float` at `:216-265` — word-count + intro + conclusion + sections + placeholder-text penalties.
- `_score_novelty(blog, full_text) -> float` at `:267-330` — cumulative-penalty title similarity against existing `SelfBlog.objects.exclude(id=blog.id).filter(status__in=['approved', 'published']).values_list('title', flat=True)[:200]`; Session 1004 strengthened.
- `_score_structure(blog, full_text) -> float` at `:332-389` — section variety + engagement elements + balance.
- `_classify_content_type(blog, full_text) -> (str, float)` at `:391-436` — internal/public/strategic classification via signals.
- `_make_decision(quality, novelty, structure, content_type, type_confidence, mythology_score) -> (str, str)` at `:438-497` — final publish/enhance/internal_only decision.
- `_suggest_category(blog, content_type, decision) -> Optional[str]` at `:499-517` — category suggestion.
- `_check_research_backing(blog) -> int` at `:519-527` — reads `blog.stats_snapshot['deliberation']['claims_count']`.
- `_score_mythology(blog, full_text) -> float` at `:529-550` — delegates to `MythologyDetectionService` at `mythology/services.py`.
- `_check_envelope(blog) -> str` at `:552-577` — **DEAD CODE for SelfBlog** (F0-CORRECTION); reads non-existent `blog.metadata['envelope']`.

Module-level convenience:
- `evaluate_blog(blog_id: str) -> GateResult` at `:630-636`.
- `evaluate_all_drafts() -> List[Tuple[str, GateResult]]` at `:639-651`.
- `get_gate_summary() -> dict` at `:654-668`.

**God-service check:** 668 lines — WITHIN 3000-line threshold. No refactor recommended.

**Threshold immutability:** `QUALITY_THRESHOLD` / `NOVELTY_THRESHOLD` / `STRUCTURE_THRESHOLD` / `MYTHOLOGY_THRESHOLD` are class constants at `:44-49`. No subclass override mechanism at HEAD, no per-env config, no runtime-tunable feature flag. Changing thresholds requires code edit + PR.

### 5.2 PublishGate call graph (16 files reference the class)

Verified via grep `PublishGate|publish_gate|apply_to_blog|evaluate_blog|GateResult` across `core/` (`files_with_matches`):

| Caller file | Purpose |
|-------------|---------|
| `core/settings.py` | Config reference (grep hit; likely unused import or feature-flag reference) |
| `core/services/publish_gate.py` | Own def |
| `core/services/content_deliberation_runner.py` | `_run_publish_gate(blog)` invoked at `:140`; called only if `decision='PUBLISH'` at `:138`; §7.1 flow |
| `core/tasks_content.py` | Self-blog generation task; PublishGate() invoked after blog save at `:2345-2355`; exception → warning log |
| `core/services/td_handlers_ops.py` | Publish-side operations handler; used for `publish_ready` filter + SLO stats at `:563, :3906, :3923` |
| `core/services/td_handlers_content.py` | Publish-rail handler; approve→publish alias, filters `publish_ready` at :756, :809, :1318 |
| `core/agents/content_writer_agent.py` | Auto-runs PublishGate when decision='publish' at `:1451-1458`; logs warning if failure |
| `core/agents/editor_agent.py` | EditorAgent enhancement loop — post-enhance re-runs gate |
| `core/services/content_classifier.py` | Content-type classification shared helper |
| `core/tasks.py` | `evaluate_unscored_blogs` batch task at `:8017-8061`; iterates unscored SelfBlogs |
| `core/tasks_misc.py` | Publish-rail-adjacent tasks; details TBD |
| `core/views_research_demo.py` | REST publish endpoint at `:943-1000`; enforcement + `force=true` |
| `core/models_unified_system.py` | Field references (SelfBlog.publish_ready + gate_notes + quality_score) |
| `core/tests/test_phase4_content_deliberation.py` | Phase 4 v2 deliberation tests (ClaimsPack + review + decision); **NO dedicated PublishGate unit tests** verified — coverage gap flagged in §12.2 |
| `core/migrations/0206_session_862_content_intelligence.py` | Origin migration |
| `core/management/commands/apply_publish_gate.py` | Manual mgmt command |

**Finding:** 16 files reference PublishGate; only 1 test file transitively touches it (via Phase 4 pipeline tests) — no dedicated gate unit tests. §12.2 debt.

### 5.3 Discord broadcast service `core/services/discord_notifications.py` (2,319 lines)

12 channel constants at `:36-47` (Discord IDs table in §3.10). Public content-broadcast methods (Explore 2 F4):

| Method | Line | Channel | Purpose |
|--------|------|---------|---------|
| `send_content_opportunity` | :953 | `CHANNEL_OPPORTUNITIES` | Trending topics + satire angles |
| `send_daily_digest` | :990 | `CHANNEL_BOARDROOM` | Daily briefing |
| `send_market_digest` | :911 | `CHANNEL_MARKET_ALERTS` | SEC filings summary |
| `send_sec_filing_alert` | :845 | `CHANNEL_MARKET_ALERTS` | Individual filings |
| `send_podcast` | :~1275 | `CHANNEL_GALLERY` (Session 430) | Podcast delivery (verified via Explore 4 `tasks_content.py:1757-1784` broadcast) |
| `send_blockchain_alert` | (referenced) | `CHANNEL_BLOCKCHAIN_ALERTS` | Blockchain audit alerts |
| `send_boardroom_decision` | :446 | `CHANNEL_BOARDROOM` | Executive decisions |
| `send_weekly_synthesis` | :742 | `CHANNEL_BOARDROOM` | Weekly executive |

Internal/status methods (`CHANNEL_STATUS`, `CHANNEL_LEARNING`, `CHANNEL_DREAMS`, `CHANNEL_CONVERSATIONS`): `send_spider_activity` (:267), `send_system_status` (:403), `send_status` (:238), `send_knowledge` (:199).

**Failure handling** (Explore 2 F5): `requests.post()` at `:98`; `timeout=10`; catches `Timeout` at `:107` and `RequestException` at `:110`; logs and returns False. **No retry logic. No exponential backoff. No queue fallback. Rate-limit 429 responses logged as generic API errors at `:104`.** **No message-ID persistence** — broadcast is fire-and-forget with no audit trail.

**Critical finding: PublishGate does NOT call Discord.** Grep `discord_notify|CHANNEL_` inside `publish_gate.py` returns 0 hits. **Blog publish decisions do NOT auto-broadcast to Discord.** Where Discord broadcast IS triggered for content-adjacent artifacts (podcasts, blockchain alerts, market alerts), the call site is upstream — in agents (`transaction_monitor_agent.py:795`, `smart_contract_auditor_agent.py:971`) or task handlers (`tasks_content.py:1757-1784` podcast delivery), not in the publish rail.

**Content-triggered Discord broadcasts inventory:**
- Podcast delivery — `tasks_content.py:1757-1784` → `CHANNEL_PODCAST_LIBRARY` (well-wired).
- Blockchain alerts — 2 sites in `agents/blockchain/` (well-wired).
- Sports betting briefs — **ZERO Discord wiring** (verified via Explore 4).
- Newsletter — no Discord broadcast (newsletter is email/subscriber-shaped).
- Blog publishing — **ZERO Discord wiring** from publish rail.

### 5.3.1 Proven-negative Discord wiring on SelfBlog publish — F5 Rigby fold

Rigby SIGN Batch B flagged that "0 hits in `publish_gate.py`" is grep-negative only + does not prove "SelfBlog publish → Discord side-effect is absent." F5 fold extends the proof to all four publish-decision actor surfaces (§1.5 enforcement contract):

| Actor | File:line | Discord/notification refs | Verdict |
|-------|-----------|---------------------------|---------|
| **`PublishGate.evaluate` + `apply_to_blog`** | `publish_gate.py:112, :579-626` | 0 hits for `discord_notify\|CHANNEL_` | Zero side-effect on gate outcome |
| **REST publish endpoint** `publish_self_blog_api` | `views_research_demo.py:943-1000` | **0 hits for `discord\|CHANNEL_\|notification\|broadcast\|publish_signal`** (verified via targeted grep on file) | Zero side-effect on status→published transition |
| **`auto_publish_approved_blogs` beat** | `core/tasks.py:8056-8079` | 0 hits for Discord/notification — body only calls `blog.save(update_fields=['status'])` at `:8075` + `logger.info` at `:8077` | Zero side-effect |
| **Post-save signals on SelfBlog** | `core/signals/*.py` | Grep-verified: `core/signals/deliverable_status_signals.py` has 0 SelfBlog references; no `pre_save\|post_save` signal handler grepped for SelfBlog publish transition | Zero side-effect |

**Proven-negative verdict:** at HEAD, NO code path from any of the four publish-decision actors (PublishGate / REST endpoint / auto_publish beat / post-save signals) triggers a Discord broadcast, notification helper, or shared publish hook on SelfBlog `status='published'` transition. This is confirmed cross-surface — not just the gate class. **Structural gap for Cat C**: publish is a DB state transition with zero guaranteed outbound side-effects (§7 anchor recommendation F10).

### 5.4 Newsletter service `core/tasks.py:5765` + `core/tasks_content.py:4234-4413` (F7 Rigby fold — Newsletter is a CONTENT-GENERATION rail, NOT a PUBLISH rail)

**F7 Rigby fold semantic reframe:** The newsletter beat produces a `Deliverable` at `tasks_content.py:4353-4390` but does NOT actually deliver to subscribers. Until live-send infrastructure lands (T.15.C2 CRITICAL), the beat is a **content generation rail** (generates outbound-audience-shaped content) not a **publish rail** (transmits to audience). Distinction matters for xx99 D65c C1 evidence: promotion from `dry_run=True` → `False` alone does NOT enable delivery, because the outbound path is missing regardless. The current dry_run gate is a documented-intent placeholder around a structurally-incomplete rail.


**`generate_operator_edge_newsletter`** — Celery task wrapper at `tasks.py:5765` delegates to `_impl_generate_operator_edge_newsletter` at `tasks_content.py:4234`.

Flow:
1. **Lock acquire** at `:4256` — Redis cache key `operator_edge_running` with 600s TTL prevents concurrent runs.
2. **Evidence gather** at `:4264` — `_gather_newsletter_evidence()` clusters SignalCluster objects (72-hour window, top 5 limit).
3. **Dry-run gate** at `:4291-4300` — `if dry_run: return {'dry_run': True, ...}` — exits before LLM call.
4. **LLM content assembly** at `:4283-4341` — routes to ContentWriterAgent with `OPERATOR_EDGE_TEMPLATE` prompt.
5. **Save as `Deliverable`** at `:4353-4390` — creates `Deliverable` row (NOT SelfBlog) with `status='ready'`. **PublishGate is NEVER invoked on the newsletter Deliverable.**

**Email sending path: ABSENT.** Grep across `_impl_generate_operator_edge_newsletter` for `sendgrid|mailgun|postmark|smtplib|SMTP` returns 0 hits (verified via Explore 4 F2). Only `core/services/bpaas/build_packet_schema.py:307` mentions "Email (SMTP)" as **MVP-required but not implemented** (a schema artifact, not runtime code). `core/auth_views_enhanced.py` (auth email path) does not appear in newsletter grep sweep — even auth may use a non-SMTP backend at HEAD.

**Newsletter status quo:** Task generates content → saves Deliverable → **stops**. No email transmission. Deliverable is available for manual dispatch (Rigby PA-tool or admin review) or an unimplemented send handler. **§14.C2 drift; §15 T.15.C2.**

### 5.5 `apply_publish_gate` management command

`core/management/commands/apply_publish_gate.py` (248 lines). Full flow (verified via Explore 2 F3 + partial grep):

- **Trigger:** Manual (`manage.py apply_publish_gate --flag`). **NOT beat-scheduled** at HEAD.
- **Target selection:**
  - `--all` — every SelfBlog
  - `--drafts-only` — `SelfBlog.objects.filter(status='draft')`
  - `--blog-id <UUID>` — single blog
  - `--summary` — no mutations; stats only via `get_gate_summary()`
- **Modes:**
  - `--dry-run` — evaluate but don't save (calls `apply_to_blog(blog, save=False)` at Explore 2 finding)
  - `--reclassify` — auto-reclassify internal content categories (`internal_note` / `playbook` / `build_log`)
- **Idempotency:** Re-running is safe (overwrites scores).

**Coverage risk:** manual-only + no beat backup + no CI health-check means gate can silently go unrun. Test artifacts stuck `publish_ready` for 175-358h in Session 1247 audit indicate historical gaps. **§15 T.15.C5 MEDIUM.**

### 5.6 Pre-brief mini-schema — Service surface (D62 = (a) 6-sibling exemplar applied)

Per parent D68 F8/F10 folds — Cat C surface enumerated with ownership + posture-decision handoff:

| Service | Owner | Cat C decides? | Cross-arc handoff |
|---------|-------|---------------|--------------------|
| `PublishGate` class | Cat C | YES — B1/B2/B3/B4 (D65b axes) | xx99 xr T1 R.CONTENT.TRIPLE-GATE-COMPOSITION-CONTRACT |
| `_check_envelope` dead code | Cat C — sunset OR wire | YES — decide sunset vs. add `metadata` field to SelfBlog | Cat D-adjacent (schema owner) |
| `MythologyDetectionService` integration | Mythology-domain-owned (external) | NO for detection logic; YES for threshold/gate consequence | Mythology-domain audit owed if scoring behaviour changes |
| Discord broadcast integration | Cat C boundary (broadcast trigger site) + Ops-domain-owned (broadcast service) | Partial — Cat C owns publish-rail wiring; Ops owns service | Cross-arc lens; possible Group 1700 Observability |
| Newsletter beat + service | Cat C rail-side (dry_run gate + promotion path) + Cat D content-side (Deliverable) | YES — C1 (D65c axis) | xx99 owner recommendation |
| `apply_publish_gate` mgmt command | Cat C | YES — coverage strategy (beat vs. manual) | Cat C-owned §19 T2 recommendation |
| Frontend approve/publish REST endpoint | Cat C (enforcement) + Cat E (approval UX) | Boundary shared | Cat E S1605 owns tool-side; Cat C flags `force=true` audit-trail gap |

---

## 6. Major APIs and Interfaces

### 6.1 REST endpoints — publish rail

Already inventoried in §3.5. Cat C boundary points:
- **Approve** endpoint at `:901` — no PublishGate call; simple status flip.
- **Publish** endpoint at `:943` — `publish_ready` check + `force=true` override.
- **Enhance** endpoint at `:1004` — async task; not Cat C.

**§6.1.1 Missing REST endpoints (Cat C-owned gaps):**
- `POST /retract/<blog_id>` — no such endpoint at HEAD.
- `POST /errata/<blog_id>` — no such endpoint.
- `POST /republish/<blog_id>` — no such endpoint.
- No admin endpoint for `force=true` audit trail retrieval.

### 6.2 PA tool schemas + handlers

Already inventoried in §3.8. Cat E S1605 owns the tool-surface audit contract; Cat C flags cross-boundary:
- `content_tool` publish actions (approve/reject/complete) map to `content_review_tool`.
- `newsletter_tool.prepare` creates 3 Deliverables (markdown/HTML/checklist) at `td_handlers_newsletter.py:121-163` — does **NOT** invoke PublishGate.
- `deliverable_tool.set_status` can flip Deliverable to `published`/`completed` outside PublishGate scope (Cat D-side memory-rule drift documented in S1603 §11.5).

**§6.2.1 Rigby memory-rule cross-references (Cat C-relevant):**

- `feedback_deliverable_status_via_content_complete.md` (Session 1184) — status transitions via `content_tool.content_complete` NOT `deliverable_tool.update`. Cat C-adjacent boundary; Cat E owns final tool-contract fix.
- `feedback_deliverable_create_defaults_to_completed.md` (Session 1241) — new deliverables default `status=completed` regardless of param. Cat C-adjacent; conflicts with publish_intent semantics.
- `feedback_publish_intent_enum.md` (Session 1094) — Rigby recommended enum design; not deployed at HEAD; publish_intent lives on Deliverable base only, not on any variant model (S1603 §4.7 verified).
- `feedback_gpt5_max_completion_tokens_floor.md` — relevant to LLM-driven ContentWriterAgent + newsletter LLM path; not Cat C-side per-se.

### 6.3 Frontend consumers (boundary confirmation only; Cat E owns)

- `frontend/src/pages/BlogViewerPage.tsx:45+` — approve/publish mutations already inventoried at §3.9.
- `frontend/src/lib/api.ts:3921-3962` — `blogsApi.approve` / `blogsApi.publish` REST wrappers.
- Cat E S1605 will own full frontend approval-UX audit; Cat C flags:
  - Frontend has NO client-side gate-preview UI at HEAD.
  - Backend is fully server-authoritative for gate enforcement.
  - `force=true` toggle in `blogsApi.publish(blogId, force)` is exposed to admin flow but audit trail is absent.

### 6.4 WebSocket / real-time consumers

**Grep-verified 0 hits** for `blog_published|selfblog_published|publish_gate_result` in `core/consumers*.py`. No real-time broadcast of gate decisions or publish events. **§10 event-flow gap.**

### 6.5 Pre-brief mini-schema — API surface (D62 = (a) 6-sibling exemplar applied)

| Surface | Actions | Publish-rail role | Cat C decides? |
|---------|---------|-------------------|-----------------|
| REST `/publish/` | POST + `force=true` | Enforcement (gate check + admin override) | YES — C4 audit-trail gap (D65c) |
| REST `/approve/` | POST | Pre-publish status flip | Cat C boundary; Cat E-side UX |
| REST `/enhance/` | POST | Triggers EditorAgent loop | Cat A-adjacent; Cat C confirms not-in-scope |
| REST missing `/retract/` | — | Post-publish correction | **Cat C gap** — C2 |
| PA `content_tool.approve/publish` | — | Rigby-side mirror | Cat E owns contract |
| PA `newsletter_tool.prepare` | — | Newsletter Deliverable creation | Cat C-adjacent; **does NOT invoke PublishGate** |
| WebSocket `blog_published` | — | Real-time event broadcast | **Cat C gap** — no consumer at HEAD |
| Frontend approve/publish | — | User-driven state transitions | Cat E-side UX; Cat C-side enforcement contract |

---

## 7. Runtime Flows

### 7.1 Canonical content-deliberation → PublishGate flow (Cat A → Cat B → Cat C)

Verified via `content_deliberation_runner.py:120-170` direct read + Explore 2 F2.

```
1. ClaimsPack build (Cat A owned)                             → runner.py :54-60
2. Draft generation (ContentWriterAgent)                      → runner.py :66
3. 3-Reviewer panel + ConversationOrchestrator debate         → runner.py :84-264 (Cat B owned)
4. Rewrite on REVISE (one pass)                               → runner.py :107-116
5. **SelfBlog.objects.create** (Cat A pipeline bypass         → runner.py :401-416
   per S1603 §16.3 T.15.1)                                       (status='pending_review' if PUBLISH decision, else 'needs_enhancement')
6. **PublishGate** — ONLY IF decision == 'PUBLISH'            → runner.py :138-157 (Cat C owned)
   6a. _run_publish_gate(blog) invokes apply_to_blog          → runner.py :140
   6b. GateResult produced                                    → gate.py :112-176
   6c. IF gate_result.decision == 'publish':
       blog.status = 'approved' (Session 1008 fast-path)      → runner.py :149
       blog.content_type = 'public'                           → runner.py :150
       blog.publish_ready = True                              → runner.py :151 (REDUNDANT WRITER; see §14.C4)
       blog.save(update_fields=['status', 'content_type', 'publish_ready'])
   6d. ELSE (enhance / internal_only):
       blog.gate_notes = gate_result.notes                    → runner.py :155
       blog.save(update_fields=['gate_notes'])
7. Status mapping                                             → runner.py :161-169
   IF decision == 'KILL': status='killed'
   ELIF decision == 'REVISE': status='needs_enhancement'
```

**Key finding:** PublishGate is invoked ONLY on `decision == 'PUBLISH'` at `runner.py:138`. **REVISE and KILL decisions BYPASS the gate entirely.** Blog is created at :128 BEFORE gate runs at :140. Gate is advisory + post-hoc, not authoritative. Session 998 REST-endpoint enforcement at `views_research_demo.py:966` is the actual authority — with `force=true` bypass.

### 7.2 Manual publish flow (Rigby / admin)

```
1. Rigby / admin invokes `apply_publish_gate --blog-id <UUID>` OR
   `manage.py apply_publish_gate --drafts-only` OR
   `evaluate_unscored_blogs` beat task fires
2. PublishGate().apply_to_blog(blog) invoked                  → gate.py :579-626
   2a. Operational-title check (bypass if match)              → gate.py :123-134
   2b. Score 4 dimensions (quality/novelty/structure/mythology) → gate.py :140-143
   2c. Research-backing penalty if claims_count == 0          → gate.py :146-149
   2d. Content-type classification                            → gate.py :152
   2e. Decision                                               → gate.py :155-158
   2f. Category suggestion                                    → gate.py :161
   2g. Envelope check (dead code for SelfBlog)                → gate.py :593
   2h. Field mutations                                        → gate.py :598-603
   2i. Status transition                                      → gate.py :605-615
   2j. Category override if `blog.category == 'blog'`          → gate.py :618-620
   2k. Save                                                   → gate.py :622-624
3. Return GateResult (transient; discarded)
```

### 7.3 REST publish flow (frontend / admin)

```
1. User clicks "Publish" in BlogViewerPage.tsx
2. Frontend calls blogsApi.publish(blogId, force?)             → api.ts :3921-3962
3. Backend receives POST /api/v1/research/self-blog/<UUID>/publish/
4. publish_self_blog_api()                                    → views_research_demo.py :943
5. Enforcement:                                               → :966
   - If not force AND not blog.publish_ready: 400 + gate_notes
   - If status=='published': 400 already published
   - If status=='draft' AND not force: 400 must be approved
6. status = 'published'                                       → :979
7. blog.save()                                                → :980
8. Return 200 { success: true, blog: {...} }
```

**§7.3.1 `force=true` bypass semantics:** `force=true` skips both (a) `publish_ready` check AND (b) status-must-be-approved check. Admin/Rigby can leap `draft` → `published` in one call. **No audit trail** — no `ForcedPublishEvent` model, no logging of `force=true` invocations at `:965-971`. §15 T.15.C6.

### 7.4 Content-review-automation beat cadence (Session 1000C)

Per `docs/topics/content-pipeline.md:166-190` + Explore 3 F3-F4:

- **`evaluate_unscored_blogs`** — 2h cycle. Iterates `SelfBlog.objects.filter(quality_score__isnull=True)`; applies gate; saves scores. **F14 Rigby fold clarification**: works for FIRST-PASS scoring only (filter is `quality_score__isnull=True`). **NOT a continuous re-eval** — silently misses (a) blogs edited after initial gate (content changes not reflected in scoring); (b) threshold-change re-scoring (Session 862 → 864 → 997 → 1003 → 1004 → 1009 tuning history required manual `apply_publish_gate --all` runs to reprocess corpus); (c) mythology-detection-pattern-DB-updates (new `MythPattern` rows do NOT auto-rescore historical blogs). Coverage gap acknowledged; T.15.C5 companion.
- **`auto_enhance_blogs`** — EditorAgent runs on `status='needs_enhancement'` blogs; saves (`save=True` default).
- **`reevaluate_enhanced_blogs`** — post-enhance re-runs gate.
- **`auto_publish_approved_blogs`** — daily 6 AM sweep at `core/tasks.py:8056-8079` (Session 1000C). Body verified at HEAD: filters `SelfBlog.objects.filter(status='approved', publish_ready=True)` at `:8066`; iterates + flips `blog.status = 'published'` + `blog.save(update_fields=['status'])` at `:8074-8075` **IN-MODEL DIRECTLY**; NO shared publish helper is called; NO event emitted; only log line `[AUTO-PUBLISH] Published blog: {title[:60]}` at `:8077` — greppable but not structured audit trail. **F6 Rigby fold precision (verified via direct read)**: bypasses REST endpoint's `publish_self_blog_api` at `views_research_demo.py:943` entirely. Idempotent (query filters `status='approved'` so re-published blogs excluded next run). Automated publish path — legitimate but auditability-lacking.
- Enhancement guard via `stats_snapshot['enhancement_count']` capped at 3 rounds.

**§7.4.1 Auto-publish path bypasses `force=true` audit-trail concern:** the auto_publish_approved_blogs beat task can flip `status='published'` without going through `views_research_demo.py:943` REST endpoint. Blogs auto-flip without frontend interaction. **§14.C5 drift + audit-trail gap.**

### 7.5 Newsletter generation flow

Verified via `tasks_content.py:4234-4413` (Explore 2 F5 + Explore 4 F2):

```
1. Beat fires Fri 06:00 Denver                                → celery.py :433-438
2. Task acquires Redis lock                                   → :4256
3. _gather_newsletter_evidence() clusters SignalClusters      → :4264
4. If dry_run=True (default):                                 → :4291-4300
   return {'dry_run': True, ...} — exits without LLM
5. LLM prompt assembly + ContentWriterAgent invocation        → :4283-4341
6. Save as Deliverable (NOT SelfBlog, NOT NewsletterIssue)    → :4353-4390
7. Return {success: True, deliverable_id: <UUID>}
```

**Deliverable persists; no email send; no PublishGate call.**

### 7.6 Discord broadcast flow (content-adjacent only)

Verified from Explore 4 F1:

```
Podcast delivery path:
  tasks_content.py generate_podcast task
  → discord_notify.send_podcast(episode)
  → _send_message(CHANNEL_PODCAST_LIBRARY, embed=<podcast_embed>)
  → requests.post(discord_webhook, timeout=10)
  → fire-and-forget

Blockchain alert path:
  transaction_monitor_agent.py:795 → discord_notify.send_blockchain_alert(alert['alert'])
  smart_contract_auditor_agent.py:971 → discord_notify.send_blockchain_alert()
  → _send_message(CHANNEL_BLOCKCHAIN_ALERTS)
  → fire-and-forget

Blog publish path:
  publish_self_blog_api() at views_research_demo.py:943
  → SelfBlog.save(status='published')
  → NO Discord broadcast triggered
```

### 7.7 Post-publish correction flow

**NOT DEFINED at HEAD.** No code path exists for retract/errata/republish/unpublish/delete-Discord-message. §16.1 CRITICAL structural gap.

---

## 8. Data Ownership and Lifecycle

### 8.1 Data owned exclusively by Cat C

- **GateResult dataclass** — transient; not persisted.
- **PublishGate class constants** (`QUALITY_THRESHOLD` / `NOVELTY_THRESHOLD` / `STRUCTURE_THRESHOLD` / `MYTHOLOGY_THRESHOLD` at `:44-49`) — mutable via code edit only.
- **OPERATIONAL_TITLE_PATTERNS array** at `:58-85` — 25 regex patterns.
- **INTERNAL_SIGNALS / PUBLIC_SIGNALS / TECHNICAL_INDICATORS** at `:88-110` — classification signal arrays.
- **Publish-rail beat schedule** — `generate-operator-edge-newsletter` at `celery.py:433` + Session 1000C content-review-automation triad.
- **REST publish endpoints** — `views_research_demo.py:901, :943, :1004`.
- **`apply_publish_gate` management command** at `core/management/commands/apply_publish_gate.py`.

### 8.2 Data consumed by Cat C (from other domains)

- **SelfBlog schema fields** (from Cat D-owned model at `models_unified_system.py:20611+`) — read-only for gate scoring; Cat C writes back subset (§4.2 table).
- **DecisionMandate output** (from Cat B-owned `DecisionEnforcerAgent`) — `content_deliberation_runner.py:138` reads `decision == 'PUBLISH'` gate condition.
- **ClaimsPack + deliberation JSONField** (from Cat A-owned pipeline) — `_check_research_backing` reads `stats_snapshot['deliberation']['claims_count']` at `:519-527`.
- **SignalCluster rows** (from Signal Engine) — newsletter task consumes at `_gather_newsletter_evidence()` at `tasks_content.py:4264` (72-hour window, top 5).
- **MythPattern DB rows** (from Mythology domain) — `MythologyDetectionService._load_patterns()` at `mythology/services.py:53` filters `is_active=True`.
- **Ex-mythology risk_score** (from Mythology domain external service).

### 8.3 Data produced by Cat C (for other domains)

- **SelfBlog field writes** (to Cat D-owned model): `quality_score` / `novelty_score` / `structure_score` / `content_type` / `gate_notes` / `publish_ready` / `status` / `category`.
- **Deliverable rows** (for newsletter output) — `_impl_generate_operator_edge_newsletter` at `tasks_content.py:4353-4390`; Cat D-owned model receives Cat C-generated content.
- **Log lines** at `publish_gate.py:174` (gate outcome) — consumed by observability (grep-able for retrospective analysis; no telemetry pipeline).
- **Discord broadcast side-effects** — no persistence at HEAD; ephemeral.

### 8.4 Lifecycle state machine (Cat C-side transitions)

Cat C-observed SelfBlog status transitions (from `apply_to_blog:605-615` + `content_deliberation_runner.py:149,167` + REST endpoint at `views_research_demo.py:979`):

```
draft ──gate:internal_only──> draft (unchanged; may re-fire)
draft ──gate:enhance──> needs_enhancement
draft ──gate:publish──> approved (Session 1000C promotion)
pending_review ──gate:enhance──> needs_enhancement
pending_review ──gate:publish──> approved
pending_review ──gate:internal_only──> draft
needs_enhancement ──gate:publish──> approved
needs_enhancement ──enhance_blog_task──> (rescored via reevaluate_enhanced_blogs)
approved ──auto_publish_approved_blogs beat OR REST /publish/──> published
draft ──REST /publish/ force=true──> published  (BYPASS)
approved ──REST /publish/──> published  (enforcement path)
published ──[NO TRANSITIONS]──> published
killed ──[NO TRANSITIONS]──> killed
```

**§8.4.1 Cat C-owned state transitions:** `draft/pending_review/needs_enhancement → approved` (via `apply_to_blog`); `approved → published` (via REST or auto_publish beat). **No `published → *` transitions at HEAD.**

**§8.4.2 Missing states:**
- `retracted` — no state; §16.1 gap.
- `errata` — no state.
- `unpublished` — no state (there is no way to un-publish).

### 8.5 Pre-brief mini-schema — Lifecycle stages (D62 = (a) 6-sibling exemplar applied)

Per parent D68 F8/F10 folds — 12-stage traceability table extended from Cat D S1603 §8.5 (Cat D-owned stages 1-8; Cat C-owned stages 9-11; Cat D-observes stage 12):

| Stage | Owner | Cat C role | Cross-arc handoff |
|-------|-------|-----------|--------------------|
| **1. Object creation** (SelfBlog.create) | Cat A pipeline (S1601) / Cat D (S1603 §16.3) | Cat C observes | S1603 T.15.1 factory bypass documented |
| **2. Initial persistence** | Cat D | Cat C observes | none |
| **3. Content generation** | Cat A pipeline | Cat C observes | none |
| **4. Review** | Cat B | Cat C observes; consumes final `decision` | S1602 §5 review-verdict panel |
| **5. Decision enforcement** | Cat B | Cat C consumes `decision='PUBLISH'` mandate at `runner.py:138` | S1602 §14.3 DecisionEnforcer canonical decision |
| **6. Rewrite loop (REVISE)** | Cat A + EditorAgent | Cat C observes; NOT gated at rewrite (only on final PUBLISH) | none |
| **7. Publish-eligibility scoring** | **CAT C** | **CAT C owns** — `_score_quality/novelty/structure/mythology` at `publish_gate.py:140-143` | none |
| **8. Publish-decision** | **CAT C** | **CAT C owns** — `_make_decision` at `:438-497` | D65b B4 composition contract MISSING |
| **9. Publish-eligibility (packaging-gate)** | **CAT C** | **CAT C owns** — `apply_to_blog` field writes + status flip + `publish_ready=True` at `:597-615` | Cat D contributes `publish_intent` enum value as input (unused for SelfBlog) |
| **10. Publish (external rails)** | **CAT C** | **CAT C owns** — REST endpoint at `views_research_demo.py:943` + auto_publish_approved_blogs beat + newsletter beat + Discord broadcast trigger sites | Discord broadcast triggered externally to gate (not from `publish_gate.py`) |
| **11. Post-publish state** | **CAT C** | **CAT C owns** — but MISSING at HEAD | D65c C2 gap |
| **12. Long-term retention** | Cat D | Cat C observes | Cat D-owned via `sweep_diagnostic_deliverables` etc. |

**Extension of Cat D S1603 §8.5:** Cat D-owned stages 1-8 + 12; Cat C-owned stages 9-11 (as flagged at Cat D S1603 §8.5 note "stages 9-11 are Cat C-owned; Cat D contributes `publish_intent` enum value as input to Cat C"). Cat D observations at HEAD confirm SelfBlog doesn't carry `publish_intent` — the variant coverage-gap surfaced in S1603 T.15.7.

### 8.6 Failure modes at each rail

- **Frontend approve/publish:** DB save failure → 500. No retry, no queue. Idempotent — safe to retry client-side.
- **Discord broadcast:** Network timeout (10s) or HTTP 4xx/5xx → log error + return False. **No retry, no dead-letter queue.** Rate-limit 429 responses handled generically. **Silent failure — no downstream signal.**
- **Newsletter beat:** ContentWriterAgent failure → return `{'success': False, 'error': ...}`. Task-level Celery retry not confirmed at HEAD (Explore 2 F12 flagged as untested).
- **PublishGate exception:** `content_deliberation_runner.py:158-159` catches with `logger.warning`; blog persists at gate-failure state.

---

## 9. Integrations With Other Domains

### 9.1 Content → Discord

Explored in §5.3 + §7.6. Content-adjacent broadcast triggers:
- Podcast delivery ✓ (well-wired)
- Blockchain alerts ✓ (well-wired via agents/blockchain/)
- Market alerts ✓ (via `send_sec_filing_alert` at :845)

**Content → Discord PUBLISH gap:** SelfBlog publish decisions do NOT auto-broadcast. If Group 1600 selects "extended integration posture" at D65b, Cat C would need a new broadcast trigger at the publish rail. Currently: unowned decision.

### 9.2 Content → Newsletter (email subscribers)

Explored in §5.4 + §7.5. Newsletter task saves Deliverable + does NOT send. Live-send infrastructure ABSENT. Dry_run gate parked indefinitely. **D65c C1 evidence — Cat C-owned handoff to xx99.**

**Cross-arc pattern:** S1402 F.B1 OutreachDraft delivery ZERO outbound + Cat C Newsletter delivery ZERO outbound = same pattern class extending. Group 1400 R.B1 OutreachDraft delivery ADR + potential R.CONTENT.NEWSLETTER-DELIVERY ADR could share posture.

### 9.3 Content → Sports (SportsBettingBrief)

`views_odds_sports.py:3237` `get_betting_brief` REST endpoint calls `SportsBettingCoordinator.generate_brief()` directly (Explore 4 F3) + returns JSON. **Bypasses persisted `SportsBettingBrief` model.** No PublishGate, no Discord broadcast, no rail. Two production writers exist (`tasks_content.py:3149-3163`, `tasks.py:12186-12187`); zero readers found via grep (S1504 §14.3 + S1603 T.15.2 CRITICAL CONFIRMED at HEAD).

**Cross-arc handoff:** Group 1500 T1.h R.D4 SportsBettingBrief consumer-or-remove decision. Cat C confirms no publish rail exists; posture decision at Group 1600 D65 may re-scope Group 1500 T1.h remediation.

### 9.4 Content → Blockchain (BlockchainAuditBrief)

Discord alert path is agent-side (`transaction_monitor_agent.py:795`, `smart_contract_auditor_agent.py:971`) + `tasks_ops.py:1928`. Does NOT flow through PublishGate. `BlockchainAuditBrief` model exists as ephemeral intelligence storage; no publish rail.

### 9.5 Content → Revenue (OutreachDraft, ClosePack)

OutreachDraft delivery ZERO outbound — S1402 F.B1 F8-CRITICAL CONFIRMED at HEAD. No SendGrid/mailgun/postmark/SMTP wiring. Approval workflow at `views_outreach.py:50` flips status='approved' + no downstream automation. Cat C owns nothing here; Revenue-domain-owned entirely.

### 9.6 Content → Memory (learning loop)

**MISSING.** ContentEngagement docstring at `models_pipeline_feedback.py:373-378` claims "Connects back to series/episodes to close the learning loop" but grep confirms:
- No `SelfBlog` FK on ContentEngagement (S1603 §14.1 CONFIRMED HIGH).
- Zero references to `AgentPerformance` / `AgentMemory` in `publish_gate.py` (verified).
- Zero references to `ContentEngagement` in `content_deliberation_runner.py` (verified).
- No `PublishGateEvent` for downstream learning.

**Structural gap:** Published blogs do NOT feed agent learning. §14.C6 drift + §15 T.15.C8.

### 9.7 Content → Signal Engine

Content consumes SignalClusters (newsletter evidence gather). Content does NOT emit SignalClusters. Post-publish signal creation: zero. Same directional asymmetry as Sports domain (S1599 §4.11 P11 6-arc consumer-side pattern COMPLETED). **§9.7 finding parallels S1599 §4.11.**

### 9.8 Domain map summary

Per playbook §13 Agent 4:

| Domain | Direction | Mechanism | Load-bearing? | Status |
|--------|-----------|-----------|---------------|--------|
| **Cat A ClaimsPack** | ← | ClaimsPack → deliberation → gate condition input | YES | Working |
| **Cat B Reviewers** | ← | DecisionEnforcer PUBLISH/REVISE/KILL mandate | YES (gate only fires on PUBLISH) | Working |
| **Cat D Deliverable/SelfBlog** | ↔ | SelfBlog persistence + publish_intent enum (Cat D) | YES (structural) | S1603 T.15.6 open |
| **Cat E Rigby PA tool** | → | approve/publish alias; deliverable_tool.set_status | YES (surface) | Cat E S1605 owns |
| **Cat F Cross-domain lens** | → | Consumes P1-P5 for xx99 evidence brief | YES | S1606 pending |
| **Sports** | → | SportsBettingBrief; no rail | Weak | S1504 §14.3 CRITICAL |
| **Blockchain** | ← | BlockchainAuditBrief; Discord agent-side | Weak | Alerts wire, brief unowned |
| **Revenue** | — | OutreachDraft ZERO outbound; publish rail absent | None | S1402 F.B1 CRITICAL |
| **Discord** | ↓ | Podcast delivery + market/blockchain alerts (Ops-domain owned service) | Weak | Broadcast triggered upstream, not from gate |
| **Newsletter (email)** | ↓ | Beat → Deliverable → NO SEND | None | EXPERIMENTAL dry_run |
| **Memory (AgentPerformance)** | — | MISSING learning loop | Critical gap | §14.C6 |
| **Signal Engine** | ← | Consume only; NO emit | Weak | §9.7 |
| **Mythology** | ← | MythologyDetectionService gate at :49 | YES | Working |
| **Observability (Group 1700)** | — | MISSING PublishGateEvent + BroadcastLog + telemetry | Critical gap | §12.4 |

---

## 10. Event Flows

### 10.1 Events emitted by Cat C

**None at HEAD.** No `PublishGateEvent`, no `BlogPublishedEvent`, no `ContentBroadcastEvent`, no `NewsletterSentEvent`, no `DiscordBroadcastEvent`, no `PublishRetractEvent`.

Log lines emit at `publish_gate.py:174` (single-line gate outcome) + `:125` (operational-title bypass) + `:149` (research penalty applied) + `:543` (mythology score high risk) — greppable but not structured events.

### 10.2 Events Cat C SHOULD emit (gaps per S1274 §6 pattern)

Per S1274 §6 event-flow gap analysis pattern:

- **`PublishGateEvent`** — every gate decision (publish/enhance/internal_only) should be a persisted event with decision + scores + rationale. Rationale: Observability/telemetry (Group 1700 pending); enable post-hoc analysis of gate calibration; support Rigby SIGN of gate outcomes without re-running.
- **`BlogPublishedEvent`** — when SelfBlog transitions to `status='published'`, emit event so downstream domains (Memory learning loop; Signal Engine post-publish signal; Cat E dashboards) can subscribe.
- **`ContentBroadcastEvent`** — Discord + Newsletter broadcast attempts + successes + failures should be persisted for audit trail.
- **`ForcedPublishEvent`** — every `force=true` invocation at REST endpoint should be persisted for compliance audit.
- **`PublishRetractEvent`** — when post-publish correction lands (currently missing), event needed.

### 10.3 Django signals in publish rail

`core/signals/deliverable_status_signals.py:17` mentions Deliverable `published → ready` transition (unpublish-for-edits pattern documented) — Cat D-owned; NOT extended to SelfBlog at HEAD. **No SelfBlog signal handlers at Cat C surface.**

---

## 11. Existing Documentation

### 11.1 Topic docs

- **`docs/topics/content-pipeline.md`** (Session 1147; last reviewed 2026-05-25) — covers PublishGate §8 (thresholds + operational-title + content-type classification + gate decision), SelfBlog gate-fields §9, Content Review Automation §3 (Session 1000C beat triad), Content Finishing Loop §5 (draft→pending_review→needs_enhancement→approved→published). **Drift-flagged** in doc header. **25+-day drift window** at S1604 open. **Missing coverage:** newsletter publish-rail, Discord-broadcast rail, post-publish correction loops, unified publish-intent-enum discipline, cross-variant publish-rail scope. §11.5 candidate for refresh vs. new topic doc landing per parent §6.6 parked issue.

- **Other topic docs cross-checked:** `docs/topics/agent-system.md`, `docs/topics/personal-assistant.md`, `docs/topics/spider-network.md`, `docs/topics/frontend.md`, `docs/topics/infrastructure.md` — **no dedicated PublishGate coverage** in any. Per Explore 5 F1.

### 11.2 DATABASE_MODEL_REFERENCE.md coverage

- Neither `SelfBlog` nor `NewsletterSubscriber` nor `NewsletterIssue` (missing model) nor gate-related fields are documented in `docs/DATABASE_MODEL_REFERENCE.md` at HEAD (per Explore 5 F5). **Drift window: >3 months** (reference is Session 737/1012 snapshot). Cross-arc with S1603 T.15.10 — Cat D flagged same drift for Deliverable + 5 variants.

### 11.3 Session handoffs bearing on Cat C

12+ sessions bearing on Cat C — full timeline in §2.3. Session lineage:

- **Session 862** — PublishGate origin (SESSION_862 handoff; migration 0206).
- **Session 864** — operational-title auto-classify + STRUCTURE_THRESHOLD lowered.
- **Session 997** — mythology cap at 'enhance'.
- **Session 998** — REST publish endpoint enforcement + `force=true`.
- **Session 1000C** — publish → approved promotion + content-review-automation triad.
- **Session 1003** — MYTHOLOGY_THRESHOLD lowered 0.5 → 0.15.
- **Session 1004** — novelty algorithm strengthened.
- **Session 1008** — content_deliberation_runner Session 1008 fast-path.
- **Session 1009** — QUALITY_THRESHOLD raised toward 0.75 (settled 0.70).
- **Session 1033** — score_unscored_deliverables backfill + EditorAgent finishing loop.
- **Session 1075/1077** — blog_tool split + approve→publish alias.
- **Session 1147** — content-pipeline.md topic doc landed.
- **Session 1222 P6** — newsletter re-enable + dry_run burn-in (SESSION_1222_CARRYOVER_QUEUE_CLEAR.md).
- **Session 1228 P3** — newsletter Denver TZ fix (SESSION_1228_AUTOFILL_SWEEP_PLUS_BEAT_TZ_FIXES.md).
- **Session 1246 F1** — operational-title E2E patterns expansion.
- **Session 1247** — audit caught 3 test artifacts stuck publish_ready 175-358h.

### 11.4 Prior audit coverage

- **`docs/audit-2026/04-content-pipeline.md`** (April 6 2026) — v2 Deliberation Pipeline coverage; §4 Execution Chain + §6.3 PublishGate scores + §8 Failure Modes + §10 Truth Gaps (including OPEN: "PublishGate calibration — avg novelty=0.0 and structure=0.0 suggest scoring may be broken or thresholds too strict"). **Newsletter is "Substack manual provider" per §9; Content Packets "built but never used."** Truth gaps status: UNRESOLVED at S1604 open. §14.C3 drift.

### 11.5 Rigby memory rules relevant to Cat C

Cross-referenced in §6.2.1. Cat C-adjacent memory rules:
- `feedback_deliverable_status_via_content_complete.md` — status transitions via content_tool.content_complete; Cat E-owned final fix.
- `feedback_deliverable_create_defaults_to_completed.md` — new deliverable status=completed default; publish-intent conflict.
- `feedback_publish_intent_enum.md` — enum design; not deployed.
- `feedback_deliverable_tool_use_append_for_large_payloads.md` — silent-fallback bug on large payloads; Cat E-owned.

### 11.6 Patent disclosures

- **`docs/patents/DISCLOSURE_E_PUBLISH_GATE_FINISHING_LOOP.md`** — PublishGate provenance (4-dimensional gate + finishing loop). **Patent assumes SelfBlog-centric model** — no mention of multi-variant publish rails. Cat C confirms accurate at HEAD (§4.7 no drift).
- **`docs/patents/DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md`** — Cat B-primary; Cat C reads DecisionMandate output. §5 Layer 2 operational claim at :140 partially invalidated by S1602 §15.3 landmine; Cat C-side impact: gate only fires on PUBLISH decision, so landmine at REVISE/KILL branches doesn't reach Cat C.

---

## 12. Research Coverage

### 12.1 Domain-inventory rows

S1273 §3.N domain map — Cat C fits under "Content Pipeline" row + "Publish Rails" if promoted. No new inventory row needed.

### 12.2 Test coverage

- **`core/tests/test_phase4_content_deliberation.py`** — Phase 4 v2 pipeline tests (ClaimsPack + review + decision + rewrite); **no dedicated `test_publish_gate.py`** at HEAD (verified via Grep). §15 T.15.C4 MEDIUM.
- **No `test_apply_publish_gate.py`** for management command.
- **No `test_discord_notifications.py`** for broadcast service (Cat C boundary).
- **No `test_newsletter_beat.py`** for `_impl_generate_operator_edge_newsletter`.
- **No `test_publish_rail_e2e.py`** for approve/publish REST → status flip.

### 12.3 Cross-arc research

- **Group 1300 Memory** — learning-loop expected but MISSING at Cat C.
- **Group 1400 Revenue** — S1402 F.B1 + S1403 F.C4 CONFIRMED at HEAD.
- **Group 1500 Sports** — S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN CONFIRMED at HEAD.
- **Group 1500 P11 SignalCluster** — same directional asymmetry (§9.7 consume-only).
- **Group 1700 Observability** — MISSING GROUP; Cat C surfaces telemetry gap.

### 12.4 Coverage classification (playbook §12)

| Area | Coverage | Confidence | Rationale |
|------|----------|------------|-----------|
| PublishGate class + methods | STABLE | High | 668 lines; class body verified; 12+ sessions of tuning history documented |
| Threshold semantics | STABLE | High | 4 constants verified; tuning history in comments matches handoffs |
| Operational-title bypass | STABLE | High | 25 patterns verified; Session 1246 F1 additions codified |
| Discord broadcast service | PARTIAL | Med | Service functional; PublishGate integration MISSING; no audit trail |
| Newsletter beat + service | EXPERIMENTAL | Med | dry_run indefinitely parked; no live-send infra; saves as Deliverable |
| Frontend approve/publish | WORKING | Med | REST endpoint enforces; frontend UX exists; auth contract implicit |
| Post-publish correction | MISSING | High | 0 code paths at HEAD (grep-verified) |
| Envelope validation | DEAD CODE | High | Missing SelfBlog `metadata` field |
| Cross-arc publish rails | PARTIAL | Med | SportsBettingBrief 0 rails; OutreachDraft 0 outbound; BlockchainAudit Discord-only |
| Learning loop (Content → Memory) | MISSING | High | Grep-verified 0 hits for AgentPerformance/AgentMemory in Cat C surfaces |
| Test coverage | PARTIAL | High | Phase 4 tests exist; no dedicated gate + rail unit tests |
| Documentation coverage | PARTIAL | High | Topic doc + patent E cover gate mechanics; rail gaps + newsletter + Discord + correction NOT covered |

---

## 13. Architecture Maturity

Per playbook §12 classification: EXPERIMENTAL / PARTIAL / WORKING / STABLE / CANONICAL. Justified with evidence:

| Surface | Maturity | Evidence |
|---------|----------|----------|
| `PublishGate` class + threshold + operational-title | **STABLE** | 12+ sessions of tuning history; no drift at HEAD (§4.7); class body 668 lines; well-tested via Phase 4 pipeline |
| `apply_to_blog` field mutations | **STABLE** | :597-615 verified; Session 1000C promotion + Session 1008 fast-path both working |
| `apply_publish_gate` management command | **WORKING** | 248 lines; multiple modes + idempotent + not beat-scheduled (manual invocation gap) |
| `evaluate_unscored_blogs` beat | **WORKING** | 2h cycle; iterates unscored SelfBlogs; Session 1000C content-review-automation triad |
| Frontend approve/publish REST | **WORKING** | Session 998 enforcement + `force=true` bypass; user-facing; auth-contract implicit |
| Discord broadcast integration (Cat C surface) | **PARTIAL** | Service functional; gate does not call Discord; audit trail absent; content-adjacent broadcast (podcast/blockchain/market) well-wired but bypasses gate |
| Newsletter beat + service | **EXPERIMENTAL** | dry_run=True indefinitely parked >4mo; no live-send infrastructure; task saves Deliverable + stops |
| Post-publish correction loops | **MISSING** | 0 code paths; no `retracted` state value; Cat C-owned structural gap |
| Envelope validation | **DEAD CODE** | Missing SelfBlog `metadata` field; Session 960 Phase 0 aspirational |
| Learning loop (Content → Memory) | **MISSING** | 0 references from Cat C surfaces |
| `mythology_score` persistence | **MISSING** | Transient GateResult field; not persisted to SelfBlog at HEAD |
| Cross-arc SportsBettingBrief publish rail | **MISSING** | S1504 §14.3 CRITICAL confirmed |
| Cross-arc BlockchainAuditBrief publish rail | **MISSING** (Cat C-side) | Alerts wire agent-side; brief unowned |
| Cross-arc OutreachDraft delivery | **MISSING** | S1402 F.B1 CRITICAL confirmed |

**Overall Cat C maturity: PARTIAL** — dominant SelfBlog-side gate machinery is STABLE + WORKING, but downstream rails have severe asymmetry (Discord PARTIAL, Newsletter EXPERIMENTAL, post-publish MISSING). Cross-variant coverage is zero. Learning-loop feedback and event-flow surfaces are structurally absent.

---

## 14. Known Drift

Q23-Q27 drift matrix per playbook §12 finding_type + severity.

**F9 Rigby fold — drift-vs-debt clarification:** Drift = doc/code mismatch (docstring claims X; runtime does Y). Debt = missing capability/robustness (feature/model/test/observability is absent). Items may appear in both matrices when a docstring claim is materially false AND a capability gap exists (T.15.C11 `_check_envelope` is one such item — dead code both misdocuments intent AND leaves envelope-validation unwired). xx99 consumers: treat drift + debt as separate axes; do NOT double-count severity.

### 14.1 Docstring vs runtime — PublishGate class

- **`PublishGate` docstring at :30-40** claims "Evaluates: 1. Content quality 2. Novelty 3. Structure 4. Content type" (4 dimensions). Runtime evaluates 5 dimensions (adds mythology at `:143` via `_score_mythology`). **Minor docstring drift.** Severity: **LOW** (misleading but non-breaking). Owner: Cat C.

### 14.2 Docstring vs runtime — `_check_envelope`

- **D.14.C3 `_check_envelope` DEAD CODE** — `publish_gate.py:552-577` reads non-existent `blog.metadata` field on SelfBlog. Session 960 Phase 0 aspirational infrastructure never wired to SelfBlog persistence. Safe silent None fallback but never fires. **Severity: MEDIUM** (dead code; potential future confusion). Owner: Cat C. **Decision path:** either add `metadata` JSONField to SelfBlog (Cat D-adjacent schema change) OR remove `_check_envelope` method.

### 14.3 Newsletter dry_run indefinite parking

- **D.14.C2 Newsletter `dry_run=True` overrun** — `celery.py:436` set at Session 1222 P6 for "2-Friday burn-in"; still `True` at HEAD after >4-month elapsed. Comment at `:422-423` documents promotion path but zero PR/handoff flips it. Grep `dry_run.*[Ff]alse` in newsletter path returns 0 hits at HEAD. **Severity: HIGH** (drift; documented intent unrealized; live-send infrastructure also absent so promotion requires more than kwarg flip). Owner: Cat C.

### 14.4 Auto-publish beat bypasses `force=true` audit trail

- **D.14.C5 auto_publish_approved_blogs beat can bypass REST endpoint** — daily 6 AM sweep flips `status='published'` on approved+publish_ready blogs directly. **Bypasses `views_research_demo.py:943` REST endpoint entirely.** `force=true` is not applicable (blogs already gate-passed) but there's also no `AutoPublishEvent` audit trail. **Severity: MEDIUM** (drift + audit-trail gap). Owner: Cat C.

### 14.5 Cross-arc: ContentEngagement docstring drift (Cat D-inherited)

- **D.14.C6 ContentEngagement docstring drift** — inherited from Cat D S1603 §14.1 (originally S1403 F.C4). Docstring at `models_pipeline_feedback.py:373-378` claims "closes learning loop" but no FK to SelfBlog / AgentPerformance / AgentMemory. **CONFIRMED at HEAD.** Cat C-side impact: post-publish learning loop MISSING. Severity: **HIGH**. Owner: cross-arc (Group 1300 Memory OR Group 1700 Observability); Cat C flags.

### 14.6 audit-2026/04 §10 OPEN truth gap — Novelty/Structure scoring calibration

- **D.14.C3b PublishGate calibration OPEN truth gap** — April 6 2026 audit noted "avg novelty=0.0 and structure=0.0 suggest scoring may be broken or thresholds too strict." Status: UNRESOLVED at S1604 open. **Severity: HIGH** if scoring is genuinely broken (would suggest systematic gate failures); MEDIUM if thresholds are simply too strict for corpus. Owner: Cat C follow-on (T2 recommendation in §19).

### 14.7 Docstring vs runtime — MythologyDetectionService integration

- **PublishGate.MYTHOLOGY_THRESHOLD comment at :47-49** references "MythologyDetectionService gives 0.55-1.0 risk on ALL AI-generated content." At Session 1003 (comment context) this was the case. **At HEAD, `MythologyDetectionService` at `mythology/services.py:19-100` is active** (loads patterns from `MythPattern.objects.filter(is_active=True)` at :53). No deprecation; comment context accurate. **No drift.**

### 14.8 Drift matrix summary

| ID | Item | Type | Severity | Owner |
|----|------|------|----------|-------|
| D.14.C1 | PublishGate class docstring understates 4→5 dimensions (mythology) | drift | LOW | Cat C |
| D.14.C2 | Newsletter dry_run overrun (>4mo since burn-in) | drift | HIGH | Cat C |
| D.14.C3 | `_check_envelope` dead code (SelfBlog missing `metadata`) | drift | MEDIUM | Cat C |
| D.14.C3b | PublishGate novelty/structure calibration open truth gap (audit-2026/04 §10) | drift (open) | HIGH | Cat C follow-on |
| D.14.C4 | Redundant `publish_ready` writer at `content_deliberation_runner.py:151` + `publish_gate.py:603` | drift (redundant writer, non-breaking) | LOW | Cat C |
| D.14.C5 | auto_publish_approved_blogs beat bypasses REST audit trail | drift + audit-trail gap | MEDIUM | Cat C |
| D.14.C6 | ContentEngagement docstring drift (cross-arc; Cat C-side impact = MISSING learning loop) | drift | HIGH | Cross-arc (Group 1300 / 1700) |
| D.14.C7 | 12 Discord channel constants; deliberate ID reuse `CHANNEL_OPPORTUNITIES` = `CHANNEL_MARKET_ALERTS` (Session 460 comment) | not-drift (deliberate) | N/A | Cat C confirms non-drift |

---

## 15. Known Technical Debt

Q26 debt matrix per playbook §12.

**F12 Rigby fold — severity rubric preamble:** CRITICAL = irreversible external side-effect without corrective mechanism (once fired, cannot be undone or amended; content mistakes become permanent liability). HIGH = internal correctness/coverage gap OR missing outbound infrastructure without side-effects today (structural absences that block downstream capability but don't cause harm at HEAD). MEDIUM = audit-trail gap OR contract-implicit-not-explicit (correctable in ORM/logs but not in structured records). LOW = documentation/labelling drift with no functional impact. Applied consistently across T.15.C1-C15.

| ID | Item | Type | Severity | Evidence | Cat C owner? |
|----|------|------|----------|----------|--------------|
| T.15.C1 | **Post-publish correction loops STRUCTURALLY MISSING** | missing_connection | **CRITICAL** | 0 grep hits for `errata|retract|unpublish|revoke.*publish|delete_broadcast|discord.*edit_message` in Cat C surfaces. `SelfBlog.STATUS_CHOICES` has no `retracted`/`unpublished` value. Discord broadcasts fire-and-forget. Once content is public, no code path to correct. | YES — Cat C-owned |
| T.15.C2 | **Newsletter live-send infrastructure MISSING** | missing_connection | **CRITICAL** | 0 grep hits for `sendgrid|mailgun|postmark|smtplib|SMTP` in `_impl_generate_operator_edge_newsletter` at `tasks_content.py:4234-4413`. Same pattern class as S1402 F.B1 OutreachDraft delivery ZERO outbound (F8-upgraded to CRITICAL). Cat C-side impact: newsletter beat runs indefinitely in dry_run without ever emailing subscribers. | YES — Cat C-owned |
| T.15.C3 | **Cross-arc SportsBettingBrief publish rail MISSING** | missing_connection | **HIGH** | S1504 §14.3 + S1603 T.15.2 CRITICAL. `get_betting_brief` at `views_odds_sports.py:3237` bypasses persisted model. No PublishGate for briefs. | Cross-arc (Cat C + Group 1500 T1.h) |
| T.15.C4 | **NO dedicated PublishGate unit tests** | technical_debt | HIGH | 0 hits for `test_publish_gate.py`; only Phase 4 pipeline tests transitively touch gate. `apply_publish_gate` mgmt command untested. `discord_notifications` untested (Cat C boundary). Newsletter `_impl_generate_operator_edge_newsletter` untested. | YES — Cat C-owned |
| T.15.C5 | **`apply_publish_gate` manual-only coverage** | technical_debt | MEDIUM | Not beat-scheduled at HEAD. `evaluate_unscored_blogs` beat covers unscored SelfBlogs but doesn't re-run gate on edited-post-gate content. Session 1247 caught test artifacts stuck publish_ready 175-358h. | YES — Cat C-owned |
| T.15.C6 | **`force=true` publish endpoint has no audit trail** | technical_debt (audit-trail gap) | MEDIUM | `views_research_demo.py:966-971` accepts `force=true` bypass but doesn't persist `ForcedPublishEvent`. Admin invocations are ephemeral. | YES — Cat C-owned |
| T.15.C7 | **`mythology_score` not persisted** | technical_debt | MEDIUM | GateResult.mythology_score at `publish_gate.py:23` computed but never written to SelfBlog. Historical analysis requires re-running gate. Post-publish correction on mythology grounds is opaque. | YES — Cat C-owned |
| T.15.C8 | **Content → Memory learning loop MISSING** | missing_connection | HIGH | Zero references to `AgentPerformance` / `AgentMemory` in Cat C surfaces. ContentEngagement docstring drift (D.14.C6) codified. Published blog engagement does NOT feed agent learning. | Cross-arc (Cat C + Group 1300 Memory) |
| T.15.C9 | **Discord broadcast audit trail MISSING** | technical_debt | MEDIUM | No `BroadcastLog` / `DiscordMessage` / `DiscordBroadcastEvent` model. `discord_notifications.py:98-113` fire-and-forget. Post-publish "did the broadcast succeed?" question is unanswerable at data layer. | YES — Cat C-owned |
| T.15.C10 | **Triple-gate composition contract MISSING** (Cat C RESOLUTION-SIDE) | boundary_violation | HIGH | Inherited from S1603 T.15.6. Cat C owns 4-candidate resolution framework (§17.4). D65b B4 evidence axis. | YES — Cat C-owned (resolution) |
| T.15.C11 | **`_check_envelope` dead code for SelfBlog** | technical_debt | LOW | D.14.C3. Safe silent None fallback; wastes CPU cycles + confuses readers. | YES — Cat C-owned |
| T.15.C12 | **`stats_snapshot['deliberation']` conflicting-writers hazard** | technical_debt | MEDIUM | Two writers documented (Explore 1 F3.1/F3.2): `content_deliberation_runner.py:381-416` writes NESTED with `deliberation` key; `tasks_content.py:2281-2307` writes FLAT (no `deliberation`). `_check_research_backing` reads only nested path; FLAT-writer blogs report `claims_count=0` → PublishGate silently penalizes quality by 0.20 (`publish_gate.py:148`). Silent quality-score regression on ScheduledTask-generated blogs. | Cross-arc (Cat C reads; Cat A/D writers) |
| T.15.C13 | **PublishGate class-constant thresholds are code-locked** | technical_debt | MEDIUM | No per-env / per-content-type / feature-flag override. Changing thresholds requires code edit + deploy. Session 862/864/997/1003/1004/1009 tuning history all done via code commits. | YES — Cat C-owned |
| T.15.C14 | **Frontend auth contract implicit; no PublishGate-side auth check** | technical_debt (implicit contract) | MEDIUM | `BlogViewerPage.tsx:81-100` mutations trust backend; `views_research_demo.py:943-1000` publish endpoint has `@require_http_methods(["POST"])` decorator but no visible role/permission check in the function body. Cat E S1605 will own tool-surface audit; Cat C flags. | Cross-arc (Cat C + Cat E S1605) |
| T.15.C15 | **audit-2026/04 §10 PublishGate calibration open truth gap** | technical_debt (unresolved) | HIGH | avg novelty=0.0 + avg structure=0.0 finding UNRESOLVED at S1604 open. Root cause: broken scoring OR thresholds too strict for corpus. | YES — Cat C follow-on (T2) |

---

## 16. Boundary Violations

Q24, §16 per playbook.

### 16.1 Cat C-owned structural gap — post-publish correction loops

**No boundary violation** per-se but **structural absence**:
- No `PublishRetractEvent` model.
- No `PublishErratum` model.
- No `SelfBlog.status` enum values for `retracted` / `errata` / `unpublished`.
- No `POST /retract/<blog_id>` REST endpoint.
- No Discord `edit_message` / `delete_message` API integration.
- No newsletter erratum-issue flow.
- No frontend UI for post-publish correction.

**Verdict:** Cat C-owned structural gap. **CRITICAL** (T.15.C1). Requires xx99 D65c C2 decision to build.

### 16.2 Cat C boundary respected by publish_gate.py

- Grep-verified 0 direct calls to `Deliverable.objects.<...>` inside `publish_gate.py`. Clean.
- Grep-verified 0 direct calls to `discord_notify` inside `publish_gate.py`. Clean (gate is separated from broadcast).
- Grep-verified 0 direct writes to `stats_snapshot` inside `publish_gate.py`. Read-only.
- Grep-verified `SelfBlog.objects.<...>` calls inside `publish_gate.py`: only at `:284` (novelty title-lookup), `:634` (evaluate_blog), `:646` (evaluate_all_drafts), `:660-666` (get_gate_summary). All read-only OR helper-scoped. Clean.

**Verdict:** Cat C class is well-bounded internally. External wiring around it (redundant writer at runner:151; force=true bypass at views:966; auto-publish beat bypass) is where the boundary tension lives.

### 16.3 Cat D S1603 boundary re-confirmation

Per S1603 §16.1: "Cat C intrusion into Cat D factory: does `deliverable_factory.py` reach into PublishGate? — grep-verified NO direct `PublishGate(...)` / `.evaluate(...)` calls in factory. Clean boundary." Cat C confirms at HEAD: no factory→gate calls. Boundary respected.

### 16.4 Cat A S1601 boundary — SelfBlog creation before gate

Per S1601 §9.1 + S1603 §16.3 T.15.1: `content_deliberation_runner.py:401` creates SelfBlog directly via `SelfBlog.objects.create` — Cat A pipeline bypasses Cat D factory. **Cat C-side impact:** blog exists BEFORE gate runs (verified §7.1 flow). Gate is advisory + post-hoc; if creation-time factory bypass changes semantics, gate contract is affected. **Cross-boundary observability question:** if Cat D factory adopts variants (D65a integration posture), does the resulting `create_selfblog_via_factory(...)` invoke PublishGate mid-flow? xx99 D65a-consuming decision.

### 16.5 Cat B S1602 boundary — DecisionEnforcer input to gate condition

`content_deliberation_runner.py:138` reads `decision == 'PUBLISH'` gate condition — the input is Cat B-owned. Cat C confirms Cat B contract at HEAD: only PUBLISH mandate triggers gate; REVISE/KILL bypass. **Verdict:** clean boundary.

### 16.6 S1602 §15.3 `spawn_tasks_from_mandate` landmine — Cat C lens

Per S1602 §15.3: `DecisionEnforcerAgent.spawn_tasks_from_mandate` at `decision_enforcer_agent.py:455-476` imports missing `queue_agent_task`. **Cat C-side impact:** gate only fires on PUBLISH decision at `runner.py:138`; if `spawn_tasks_from_mandate` is called at the REVISE/KILL branches (not the PUBLISH branch), the landmine doesn't reach Cat C surfaces. But if any future refactor moves the spawn call into the PUBLISH branch, Cat C would inherit the failure. **Cross-boundary observability handoff:** Cat B-owned resolution.

### 16.7 Discord broadcast integration — Cat C-adjacent, Ops-domain-owned service

`discord_notifications.py` is Cat C-adjacent (publish rail) but the service class is Ops-domain-owned (per Explore 3 F4). Where content-adjacent broadcasts fire — podcast delivery (`tasks_content.py:1757-1784`), blockchain alerts (`agents/blockchain/`), market alerts (`send_sec_filing_alert`) — the call sites live outside `publish_gate.py`. **Cat C boundary:** owns the publish-rail *contract* (which broadcasts should fire on gate-pass; currently zero) but does NOT own the *service*. Verdict: clean boundary respected + evidence gap (no gate → broadcast wiring).

---

## 17. Duplicate or Overlapping Systems

Q23 per playbook §17.

### 17.1 Triple quality-scoring systems (inherited from S1603 §17.2)

- **`Deliverable.quality_score`** at `models_deliverables.py:256-259` (Cat D-owned; 0.0-1.0 base model field).
- **`SelfBlog.quality_score`** at `models_unified_system.py:20709-20712` (Cat D-owned schema field on variant).
- **`GateResult.quality_score`** at `publish_gate.py:18` (Cat C-owned dataclass output; transient).

**Three parallel scoring systems.** Cat C confirmation extends S1603 §17.2: no unified source; no sync logic; `Deliverable.quality_score` scored by Session 1033 `score_unscored_deliverables` task; `SelfBlog.quality_score` scored by PublishGate + write; `GateResult.quality_score` scored per-invocation and discarded. Over time, these three fields DIVERGE.

**Cat C RESOLUTION-SIDE evidence for T.15.C10:**

### 17.2 Newsletter Deliverable vs SelfBlog Deliverable overlap

- Newsletter beat saves output as `Deliverable` at `tasks_content.py:4353-4390` (not SelfBlog, not NewsletterIssue).
- ContentDeliberation-generated blogs save as SelfBlog at `content_deliberation_runner.py:401` (not Deliverable).
- Both are "content-shaped artifacts" but persist to different tables with different lifecycles.
- **Verdict:** parallel-schema-siblings pattern (extends S1603 §17.4 five-variant analysis to newsletter-as-sixth variant).

### 17.3 Redundant `publish_ready` writers

- `publish_gate.py:603` writes `blog.publish_ready = (result.decision == 'publish')` (canonical writer via `apply_to_blog`).
- `content_deliberation_runner.py:151` writes `blog.publish_ready = True` (Session 1008 fast-path).
- Both fire on gate-pass; corroborate but do not conflict. **Verdict:** redundant writer; not-drift-at-HEAD; hazard if future refactor changes semantics at one site.

### 17.4 Triple-gate composition contract — CAT C-RESOLUTION-SIDE 4-CANDIDATE FRAMEWORK

**Inherited from Cat D S1603 T.15.6 (HIGH boundary_violation).** Cat C flags 4 candidate resolution paths for xx99 D65b B4 consumption (posture-decision framing, NOT posture selection per playbook §14.5 no-implementation rule):

**Candidate A — Composition contract with canonical precedence.**
State that `deliverable_factory:5-gate` is creation-time validation (structural integrity), `PublishGate:4-threshold` is publish-eligibility (content quality), and `SelfBlog:quality_score` fields are variant-level cached scores derived from PublishGate. Document the state machine: creation → factory 5-gate → deliberation → PublishGate 4-threshold → SelfBlog field write. Add invariant: `SelfBlog.quality_score == last GateResult.quality_score`.

**Candidate B — Unify to single canonical gate.**
Retire `deliverable_factory:5-gate` (Session 951-era; predates deliberation pipeline). Merge structural checks into PublishGate (mythology score already handles some of this). SelfBlog fields become source-of-truth for scoring. Requires migration + factory refactor.

**Candidate C — Split by variant type.**
Deliverable factory 5-gate remains for base Deliverable (all variants); PublishGate remains for SelfBlog only; Sport/Blockchain variants get their own gates (or explicit no-gate posture). Formalize the SelfBlog-only scope as canonical + accept variant-specific gates in Cat D-side extensions.

**Candidate D — Composition contract with observability.**
Add `PublishGateEvent` telemetry + factory-gate telemetry + variant-quality-score telemetry (T.15.C1 + T.15.C9 companion). Observability lets us CATCH gate-disagreement without collapsing gates. Preserves separation-of-concerns per F7+F11 Rigby fold.

**xx99 D65b B4 posture decision must select A/B/C/D + rationale.** Cat C does not select.

### 17.5 Newsletter beat kwargs `dry_run=True` vs live-send code path

- Beat config sets `dry_run=True` at `celery.py:436`.
- `_impl_generate_operator_edge_newsletter` at `tasks_content.py:4291-4300` exits early on `dry_run=True`.
- **No live-send code path exists at HEAD** (SendGrid/mailgun/postmark 0 hits).
- Flipping `dry_run=False` would NOT enable delivery — it would trigger the ContentWriterAgent + save-as-Deliverable + still-no-send path.
- **Verdict:** dry_run gate is dry_run vs dry_run overlap — both paths lead to no email send. Documentation drift + structural infrastructure gap.

---

## 18. Ownership Gaps

Q25 per playbook.

| Area | Current owner | Clarity | Cat C-flagged issue |
|------|---------------|---------|---------------------|
| PublishGate class + methods | Cat C | CLEAR | Threshold constants immutable; §14.C13 |
| 4 thresholds (Q/N/S/M) | Cat C class constants | CLEAR | No per-env override; Session-locked tuning history |
| Operational-title patterns | Cat C class constants | CLEAR | 25 patterns; Session 1246 F1 additions; Cat E may need surface to test |
| Content-type classification signals (INTERNAL_SIGNALS / PUBLIC_SIGNALS / TECHNICAL_INDICATORS) | Cat C class constants | CLEAR | Not-drift; frozen semantics per Session 862 |
| GateResult dataclass | Cat C | CLEAR | Transient; mythology_score not persisted |
| Discord broadcast integration wiring | UNCLEAR | UNCLEAR | Service (Ops-domain) exists; gate does not call; where should call live? Cat C flags for xx99 D65b handoff |
| Newsletter dry_run promotion path | UNCLEAR | UNCLEAR | Owner never identified; parent parked §6.2; Cat C surfaces for D65c C1 |
| Newsletter live-send infrastructure | UNCLEAR (probably Revenue-adjacent) | UNCLEAR | 0 SendGrid/mailgun/postmark hits at HEAD; extends S1402 F.B1 pattern |
| Frontend approve/publish UX | Cat E S1605 (final owner) + Cat C (enforcement contract) | CLEAR | Cat E owns tool-side; Cat C owns REST-side |
| `force=true` bypass audit trail | Cat C | CLEAR (deferred) | T.15.C6; no ForcedPublishEvent |
| Auto-publish beat audit trail | Cat C | CLEAR (deferred) | D.14.C5; no AutoPublishEvent |
| Post-publish correction loops | UNOWNED | MISSING | T.15.C1 CRITICAL; xx99 D65c C2 |
| Envelope validation | Cat C — sunset OR wire | CLEAR (deferred) | T.15.C11; Cat D-adjacent if wired |
| Mythology scoring | Mythology-domain (external service); Cat C consumes | CLEAR | Not-drift; T.15.C7 persistence gap |
| SelfBlog `stats_snapshot['deliberation']` conflicting writers | Cat A (nested writer) + Cat D (schema owner) + Cat C (reader) | UNCLEAR | T.15.C12 silent quality-score regression on ScheduledTask blogs |
| `mythology_score` persistence | Cat C-owned proposal | CLEAR (deferred) | T.15.C7 |
| Cross-arc SportsBettingBrief publish rail | Sports-domain (S1500) + Cat C flags | UNCLEAR | T.15.C3 + S1504 §14.3 CRITICAL |
| Cross-arc BlockchainAuditBrief publish rail | Blockchain-domain (unaudited) + Discord-alert-side | UNCLEAR | Cat C observes; Cat D S1603 flagged |
| Cross-arc OutreachDraft delivery | Revenue-domain (S1402) | UNCLEAR | S1402 F.B1 CRITICAL |
| Content → Memory learning loop | UNOWNED (potential Group 1300 OR Group 1700) | MISSING | T.15.C8 HIGH |
| Discord broadcast audit trail | UNOWNED | MISSING | T.15.C9 MEDIUM |
| `apply_publish_gate` mgmt command coverage | Cat C | CLEAR (deferred) | T.15.C5 no beat backup |
| PublishGate telemetry / observability | UNOWNED (potential Group 1700) | MISSING | Cross-arc handoff |
| PublishGate test coverage | Cat C | CLEAR (deferred) | T.15.C4 no dedicated tests |
| audit-2026/04 §10 open truth gap | Cat C follow-on | CLEAR (deferred) | T.15.C15 novelty/structure calibration OPEN |

---

## 19. Recommended Future Research

Q28. Ranked by architectural uncertainty × risk × unblocked flows.

### Top-tier (T1 — evidence bearing on xx99 D65a/D65b/D65c posture selection)

- **T1 R.CONTENT.TRIPLE-GATE-COMPOSITION-CONTRACT** (inherited T1 from S1603 F11) — Cat C RESOLUTION-SIDE owner. Cat C contributes 4-candidate framework at §17.4 for xx99 D65b B4 consumption. **Uncertainty: HIGH; Risk: HIGH; Unblocks: quality-scoring canonicalization + factory-vs-gate boundary discipline.**

- **T1 R.CONTENT.PUBLISHGATE-SCOPE-CANONICALIZATION** (Cat C-owned NEW) — D65b B1 posture decision: SelfBlog-only (island) vs. extend to all Deliverable-variants (integration). Cat C contributes evidence §4.3 (variant models with no publish-state fields) + §5.1 (SelfBlog-only imports) + §9.3-9.6 (cross-arc variant analysis). **Uncertainty: HIGH; Risk: HIGH; Unblocks: variant-quality-gate contract + cross-arc publish-rail decisions.**

- **T1 R.CONTENT.POST-PUBLISH-CORRECTION-LOOPS** (Cat C-owned NEW — CRITICAL) — D65c C2 posture decision + design owner. Cat C contributes evidence: 0 retract/errata/unpublish code paths (§16.1); Discord fire-and-forget; SelfBlog STATUS_CHOICES has no `retracted` value; newsletter Deliverable has no correction path. Decision requires: (a) should content be immutable-once-published (accept correction absence); (b) build model + service + REST + UI + Discord edit_message wire-up + newsletter erratum-issue path. **Uncertainty: HIGH; Risk: CRITICAL (post-publish compliance / errata / retraction); Unblocks: production-safety + Cat C maturity from PARTIAL → WORKING.**

- **T1 R.CONTENT.NEWSLETTER-LIVE-SEND-PATH** (Cat C-owned NEW — CRITICAL — extends S1402 F.B1 pattern class) — D65c C1 posture decision + design owner. Cat C contributes evidence: dry_run indefinite parking (D.14.C2 HIGH); 0 live-send infrastructure (T.15.C2 CRITICAL); newsletter beat saves Deliverable + stops. Decision requires: (a) should newsletter promote to live-send; (b) if yes, where does SendGrid/mailgun/postmark wire-up live (Revenue-adjacent per S1402 pattern OR Cat C-owned NEW). **Uncertainty: HIGH; Risk: CRITICAL-BUSINESS (if newsletter is on subscriber-conversion revenue path); Unblocks: subscriber-audience rail + revenue outbound.**

- **T1 R.CONTENT.OUTREACHDRAFT-DELIVERY** (inherited from S1603 F14 T1) — cross-arc extends S1402 F.B1. Cat C confirms same pattern class extends to newsletter (Cat C-side) — **Cat C strengthens the case for a unified outbound-delivery domain** (Content + Revenue + Employee OS sharing?). **Uncertainty: LOW (already scoped in Group 1400 R.B1 + now Group 1600 Cat C); Risk: HIGH-BUSINESS; Unblocks: multiple outbound rails.**

### Second-tier (T2 — Cat C-native remediation)

- **T2 R.CONTENT.PUBLISHGATE-CALIBRATION-INVESTIGATION** (audit-2026/04 §10 OPEN truth gap — D.14.C3b HIGH) — root-cause analysis for "avg novelty=0.0 + avg structure=0.0" finding. Determine: broken scoring OR thresholds too strict for corpus. **F13 Rigby fold concrete next action**: reproduce/calibrate with a fixed test corpus (12+ representative SelfBlogs across content_type public/internal/strategic + at least one operational-title-bypass exemplar) and record expected score ranges per dimension; compare to current runtime distribution; classify as (a) broken scoring (fix required) OR (b) thresholds too strict for corpus (recalibrate or accept). **Uncertainty: MED (scoring logic verified; corpus stats unknown at HEAD); Risk: HIGH (silent-quality-regression if broken); Unblocks: gate calibration confidence.**

- **T2 R.CONTENT.MYTHOLOGY-SCORE-PERSISTENCE** (T.15.C7) — add `SelfBlog.mythology_score` field OR persist as `PublishGateEvent`. Enables historical analysis, retrospective correction, calibration validation. **Uncertainty: LOW; Risk: LOW; Unblocks: mythology-detection quality feedback loop.**

- **T2 R.CONTENT.PUBLISHGATE-EVENT-TELEMETRY** (T.15.C1 + T.15.C9) — add `PublishGateEvent` model persisting every gate decision + scores + rationale; add `ContentBroadcastEvent` persisting Discord + Newsletter broadcasts. Enables audit trail + observability + calibration analysis + T2 R.CONTENT.PUBLISHGATE-CALIBRATION-INVESTIGATION uplift. **Uncertainty: LOW; Risk: LOW; Unblocks: telemetry maturity + Group 1700 Observability arc coverage.**

- **T2 R.CONTENT.APPLY-PUBLISH-GATE-BEAT** (T.15.C5) — schedule `apply_publish_gate --all` on a slow cadence (weekly? daily?) to reprocess published-then-edited content + retry test artifacts stuck publish_ready. Session 1247 caught the stuck-artifact pattern; this closes the observability gap. **Uncertainty: LOW; Risk: LOW; Unblocks: gate coverage under manual-only workflow.**

- **T2 R.CONTENT.FORCE-PUBLISH-AUDIT-TRAIL** (T.15.C6) — persist `ForcedPublishEvent` on every `force=true` REST invocation. Enables compliance audit + retrospective analysis of admin bypass frequency. **Uncertainty: LOW; Risk: LOW; Unblocks: audit trail.**

- **T2 R.CONTENT.AUTO-PUBLISH-BEAT-AUDIT-TRAIL** (D.14.C5) — persist `AutoPublishEvent` on every daily auto-publish flip. Companion to T.15.C6. **Uncertainty: LOW; Risk: LOW; Unblocks: audit trail parity.**

- **T2 R.CONTENT.CHECK-ENVELOPE-DEAD-CODE** (T.15.C11 D.14.C3) — decision: sunset `_check_envelope` OR add `metadata` JSONField to SelfBlog + backfill. **Uncertainty: LOW; Risk: LOW; Unblocks: dead-code removal + envelope validation actual use.**

- **T2 R.CONTENT.STATS-SNAPSHOT-DELIBERATION-CANONICALIZATION** (T.15.C12) — cross-arc with Cat A. Formalize the nested `stats_snapshot['deliberation']` contract; migrate ScheduledTask writer to write nested shape; add schema validation. **Uncertainty: MED; Risk: MED (silent-quality-regression today); Unblocks: gate-scoring accuracy on non-pipeline blogs.**

- **T2 R.CONTENT.PUBLISHGATE-UNIT-TESTS** (T.15.C4) — add `test_publish_gate.py` + `test_apply_publish_gate.py` + `test_newsletter_beat.py` + `test_discord_notifications.py` + `test_publish_rail_e2e.py`. Ensures regression coverage. **Uncertainty: LOW; Risk: LOW; Unblocks: safe refactor of gate mechanics.**

- **T2 R.CONTENT.EXHAUSTIVE-PUBLISH-MUTATIONS-SWEEP** (F-NEW Rigby fold from SIGN Batch B + F11 Rigby fold promotion to §7 anchor recommendation) — enumerate every code path that can set `SelfBlog.status='published'` OR any variant equivalent (Deliverable `status='published'`, SelfBlog `publish_ready=True`, OutreachDraft `status='sent'`, etc.) into a canonical table: **mutator → entry point → authorization context → audit artifact → side-effects**. Resolves multiple audit findings simultaneously (D.14.C5 auto-publish audit-trail + T.15.C6 force=true audit-trail + §10 event-flow gap + §16.1 post-publish-correction preconditions). Also generates the direct evidence needed for post-publish correction loops (§16.1 T.15.C1 CRITICAL) — cannot correct what you cannot enumerate. **Uncertainty: LOW (audit-style enumeration); Risk: LOW; Unblocks: T.15.C1 CRITICAL post-publish correction feasibility + T.15.C6 audit-trail feasibility + xx99 D65c C2/C3/C4 direct evidence input.** **F11 promotion: this becomes §7 anchor-update recommendation as well, not just T2.**

### Third-tier (T3 — post-arc T-slot)

- **T3 R.CONTENT.PUBLISH-RAIL-TOPIC-DOC** — NEW `docs/topics/publish-rail.md` (or extend content-pipeline.md). Covers PublishGate + Newsletter + Discord + Frontend approve/publish + post-publish correction. Consumes S1604 + Cat E + Cat F + xx99. **xx99 §7 anchor-update recommendation.**

- **T3 R.CONTENT.NEWSLETTER-ISSUE-MODEL** — decide: promote newsletter Deliverable to first-class `NewsletterIssue` model OR keep as Deliverable variant. Companion to T1 R.CONTENT.NEWSLETTER-LIVE-SEND-PATH.

- **T3 R.CONTENT.PUBLISHGATE-THRESHOLD-OVERRIDE** (T.15.C13) — extract thresholds to config file OR feature-flag OR per-content-type override. Enables tuning without deploy.

- **T3 R.CONTENT.DATABASE-MODEL-REFERENCE-REFRESH** — add SelfBlog + Deliverable + variants + `NewsletterSubscriber` + missing `NewsletterIssue` + `PublishGateEvent` (if T2 lands) to `DATABASE_MODEL_REFERENCE.md`. Cross-arc with S1603 T.15.10.

- **T3 R.CONTENT.DISCORD-CHANNEL-CONSTANT-REVIEW** — 12 constants but 11 unique IDs; deliberate reuse Session 460. Revisit if Group 1700 Observability arc surfaces observability-per-channel concerns.

### Fourth-tier (T4 — deferred cross-arc)

- **T4 R.CONTENT.PUBLISHGATE-VARIANT-EXTENSION** (if D65a integration posture selected at xx99) — extend PublishGate to gate all Deliverable-variants + variant-specific policies (SelfBlog, OutreachDraft, ClosePack, SportsBettingBrief, BlockchainAuditBrief). Requires Cat D T1 R.CONTENT.VARIANT-CANONICALIZATION decision first.

- **T4 R.CONTENT.CONTENT-ENGAGEMENT-LEARNING-LOOP-BRIDGE** — cross-arc with Group 1300 Memory / Group 1700 Observability. Cat D S1603 §14.1 + Cat C §14.C6 both flag S1403 F.C4 drift. Would restore learning-loop closure.

- **T4 R.CONTENT.SPORTSBETTINGBRIEF-CONSUMER-OR-REMOVE-RAIL** (cross-arc with Group 1500 T1.h) — if consumer decision is "keep", add publish rail (PublishGate + Discord + storage). If "remove", drop model. Cat C confirms zero rail at HEAD.

- **T4 R.CONTENT.BLOCKCHAINAUDITBRIEF-CONSUMER-OR-REMOVE-RAIL** — same pattern class.

- **T4 R.CONTENT.CROSS-BOUNDARY-QUEUE-AGENT-TASK-LANDMINE** (S1602 §15.3) — Cat C observer; Cat B owner.

*(F14 fold analog: T1 R.CONTENT.OUTREACHDRAFT-DELIVERY inherited; no move to T2 needed here.)*

---

## 20. Appendix

### 20.1 Files inspected

Full sweep list (Agent 1-6 aggregate):

**Core code:**
- `core/services/publish_gate.py` (1-668 — full read; primary artifact)
- `core/services/content_deliberation_runner.py` (:120-170, :350-450 — Cat A pipeline PublishGate call site)
- `core/services/discord_notifications.py` (:32-2319 — channels + 2 shared IDs; broadcast service)
- `core/services/artifact_envelope.py` (envelope contract used by dead-code `_check_envelope`)
- `core/services/td_handlers_content.py` (:84-161, :162-182, :235-268, :4294-4473 — content_tool + blog_tool + deliverable_tool)
- `core/services/td_handlers_ops.py` (:563, :3906, :3923 — publish_ready filters)
- `core/services/td_handlers_newsletter.py` (:25-163 — newsletter_tool)
- `core/services/tool_dispatcher.py` (dispatcher registrations)
- `core/services/pa_tool_schemas.py` (:3288-3330 content_tool + :3498-3550 newsletter_tool)
- `core/services/content_classifier.py` (content-type classification helper)
- `core/agents/content_writer_agent.py` (:1451-1458 — auto-gate on decision='publish')
- `core/agents/editor_agent.py` (enhancement loop)
- `core/models_unified_system.py` (:18394-18466 SportsBettingBrief + BlockchainAuditBrief no publish-state; :20611-20770 SelfBlog fields sweep; :20639-20645 STATUS_CHOICES; :20706-20742 gate fields)
- `core/models_deliverables.py` (:256-259 Deliverable.quality_score cross-scoring)
- `core/models_outreach.py` (:18-150 OutreachDraft no outbound)
- `core/models_close_pack.py` (:20-80 ClosePack Cat C UNKNOWN)
- `core/models_newsletter.py` (:8-31 NewsletterSubscriber; no NewsletterIssue)
- `core/models_pipeline_feedback.py` (:370-449 ContentEngagement docstring drift confirmed cross-arc)
- `core/views_research_demo.py` (:901-1000 approve/publish/enhance REST endpoints)
- `core/views_odds_sports.py` (:3237 get_betting_brief bypass verification)
- `core/views_outreach.py` (:50 outreach_approve endpoint)
- `core/tasks.py` (:5765 generate_operator_edge_newsletter wrapper; :8017-8061 evaluate_unscored_blogs beat task; :12186-12187 SportsBettingBrief write)
- `core/tasks_content.py` (:1757-1784 podcast Discord delivery; :2281-2307 ScheduledTask flat stats_snapshot writer; :3149-3163 SportsBettingBrief write; :4234-4413 newsletter task)
- `core/tasks_misc.py` (publish-adjacent tasks)
- `core/tasks_ops.py` (:1928 blockchain alert Discord delivery)
- `core/celery.py` (:414-438 newsletter beat entry with dry_run; :176, :290 cleanup/archive; :433-435 crontab Fri 06:00 Denver)
- `core/urls.py` (routing verification)
- `core/management/commands/apply_publish_gate.py` (mgmt command; 248 lines)
- `core/signals/deliverable_status_signals.py` (:17 Deliverable published→ready)
- `core/tests/test_phase4_content_deliberation.py` (Phase 4 v2 tests; no dedicated PublishGate tests)
- `core/services/bpaas/build_packet_schema.py` (:307 SMTP MVP-required-but-not-implemented)
- `core/auth_views_enhanced.py` (auth email path; contrast reference)
- `mythology/services.py` (:19-100 MythologyDetectionService active)
- `agents/blockchain/transaction_monitor_agent.py` (:795 discord_notify.send_blockchain_alert)
- `agents/blockchain/smart_contract_auditor_agent.py` (:971 discord_notify.send_blockchain_alert)
- `frontend/src/pages/BlogViewerPage.tsx` (:45+, :81-100 approve/publish mutations)
- `frontend/src/lib/api.ts` (:3921-3962 blogsApi)

**Migrations (Cat C-relevant):**
- `core/migrations/0206_session_862_content_intelligence.py` (Session 862 origin)
- `core/migrations/0364_...` (Newsletter beat re-enable; kwargs dry_run=True)

**Docs:**
- `docs/topics/content-pipeline.md` (Session 1147; drift-flagged)
- `docs/audit-2026/04-content-pipeline.md` (April 2026; §10 truth gap OPEN)
- `docs/patents/DISCLOSURE_E_PUBLISH_GATE_FINISHING_LOOP.md` (Cat C provenance)
- `docs/patents/DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md` (Cat B provenance; Cat C consumes decision)
- `docs/research/domains/content/1600_content_domain_scoping.md` (parent Cat C scope + F2 fold + F3 fold)
- `docs/research/domains/content/1601_content_claims_pack_deliberation_pipeline_v2_audit.md` (Cat A sibling; §9.1 SelfBlog.create bypass)
- `docs/research/domains/content/1602_content_reviewers_decision_enforcement_audit.md` (Cat B sibling; §16.1 stats_snapshot deliberation writer + §15.3 queue_agent_task landmine)
- `docs/research/domains/content/1603_content_deliverable_base_variants_audit.md` (Cat D sibling; T.15.6 triple-gate composition contract MISSING inherited)
- `docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md` (§14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN precedent)
- `docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md` (F.B1 OutreachDraft delivery ZERO outbound; F8-upgraded to CRITICAL by S1603)
- `docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md` (F.C4 ContentEngagement docstring drift CONFIRMED at HEAD)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template + §13 6-parallel-Explore + §14 verifier-loop + §15 SIGN policy + §16 commit policy)
- `docs/PLATFORM_INVENTORY.md` (no PublishGate mention; 12 discord channels; 91 beat rows)
- `docs/PLATFORM_WHAT_IT_IS.md` (Session 1223 refresh)
- Rigby memory rule files:
  - `feedback_deliverable_status_via_content_complete.md`
  - `feedback_deliverable_create_defaults_to_completed.md`
  - `feedback_publish_intent_enum.md`
  - `feedback_deliverable_tool_use_append_for_large_payloads.md`

### 20.2 Grep patterns used (key binary-claim verifications)

```
# PublishGate call graph
rg -n 'PublishGate|publish_gate|apply_to_blog|evaluate_blog|evaluate_all_drafts|GateResult' core   # 16 files

# Envelope contract absence
rg -n '^    metadata\s*=\s*models\.' core/models_unified_system.py   # 0 hits between :20611-20770 → SelfBlog has NO metadata field
rg -n 'metadata\[.*envelope' core/   # 0 hits — no writer

# Newsletter live-send infrastructure absence
rg -n 'sendgrid|mailgun|postmark|smtplib|SMTP|EmailBackend' core/tasks_content.py   # 0 hits in newsletter section
rg -n 'dry_run.*[Ff]alse' core/celery.py core/tasks_content.py   # only comment at celery.py:423

# Post-publish correction absence
rg -n 'errata|retract|unpublish|revoke.*publish|delete_broadcast|discord.*edit_message' core/   # 0 hits in Cat C surfaces

# Discord channel constants + shared ID
rg -n 'CHANNEL_[A-Z_]+ =' core/services/discord_notifications.py   # 12 constants at :36-47
# Both 1448867150948335777: CHANNEL_OPPORTUNITIES + CHANNEL_MARKET_ALERTS

# PublishGate → Discord absence
rg -n 'discord_notify|CHANNEL_' core/services/publish_gate.py   # 0 hits (gate does not broadcast)

# Event-flow gaps
rg -n 'class PublishGateEvent|class BlogPublishedEvent|class ContentBroadcastEvent|class BroadcastLog|class DiscordMessage|class NewsletterIssue|class ForcedPublishEvent|class AutoPublishEvent|class PublishRetractEvent|class BlogErratum' core   # 0 hits (except NewsletterSubscriber which is not Issue)

# Content → Memory learning loop
rg -n 'AgentPerformance|AgentMemory|ContentEngagement' core/services/publish_gate.py core/services/content_deliberation_runner.py core/tasks_content.py   # 0 hits in Cat C surfaces

# Content → Signal Engine
rg -n 'SignalCluster.objects.create|emit_signal_cluster' core/services/publish_gate.py core/services/content_deliberation_runner.py   # 0 hits (consume-only)

# WebSocket real-time gap
rg -n 'blog_published|selfblog_published|publish_gate_result' core/consumers   # 0 hits

# Variant publish-state field parity
rg -n 'publish_ready|quality_score' core/models_unified_system.py | awk -F: '$2 >= 18394 && $2 <= 18500'   # 0 hits on SportsBettingBrief + BlockchainAuditBrief

# Deliverable factory 5-gate + PublishGate 4-threshold + SelfBlog own quality fields = triple gate (S1603 T.15.6)
# All three sites verified at HEAD:
# publish_gate.py:44-49                  (4-threshold PublishGate)
# deliverable_factory.py:358-411          (5-gate creation-time factory check per S1603)
# models_unified_system.py:20709-20719    (SelfBlog own quality fields)

# apply_publish_gate beat coverage
rg -n 'apply_publish_gate' core/celery.py   # 0 hits (not beat-scheduled)
```

### 20.3 Verifier-loop notes (pre-Explore + post-Explore)

**Pre-Explore verifier-loop (parent-Claude, playbook §14 rule):**

22 load-bearing binary claims from parent S1600 §3 C + Cat C scope grep-verified before spawning Explore sub-agents:

| # | Claim | Verified | Correction? |
|---|-------|----------|-------------|
| 1 | `PublishGate` class at `publish_gate.py:27` | ✓ | none |
| 2 | 4 thresholds at `:44-49` (Q 0.70 / N 0.60 / S 0.55 / M 0.15) | ✓ | none |
| 3 | Operational-title bypass at `:124-134` | ✓ | corrected: check at `:178-194`; bypass invoked from `evaluate` at `:123-134` |
| 4 | Operational-title patterns at `:58-85` | ✓ | none (25 patterns: 11 original + 14 Session 1246 F1) |
| 5 | `apply_to_blog` at `:579` writes SelfBlog fields | ✓ | none |
| 6 | Discord channel constants at `:36-47` | ✓ | none (12 constants) |
| 7 | Newsletter beat at `celery.py:433` | ✓ | none |
| 8 | Newsletter kwargs `dry_run=True` at `:436` | ✓ | none |
| 9 | Newsletter task at `core.tasks.generate_operator_edge_newsletter` | ✓ | delegates to `_impl_...` at `tasks_content.py:4234` |
| 10 | BlogViewerPage.tsx approve/publish mutations at `frontend/src/pages/BlogViewerPage.tsx:45` | ✓ | (mutations at `:81-100`) |
| 11 | blogsApi at `frontend/src/lib/api.ts:3921-3962` | ✓ | none |
| 12 | 16 files reference PublishGate | ✓ | none |
| 13 | SessionBlog fields `quality_score`/`novelty_score`/`structure_score` at `models_unified_system.py:20708-20728` | ✓ | corrected to :20709-20720 |
| 14 | `publish_ready` at `:20721-20724` | ✓ | none |
| 15 | `gate_notes` at `:20725` | ✓ | none |
| 16 | `status` at `:20706` | ✓ | none |
| 17 | `stats_snapshot` at `:20742` | ✓ | none |
| 18 | Session 862 origin migration `0206_session_862_content_intelligence.py` | ✓ | none |
| 19 | Session 1222 P6 newsletter re-enable comment at `celery.py:417-423` | ✓ | none |
| 20 | Session 1228 P3 Denver TZ fix comment at `celery.py:425-432` | ✓ | none |
| 21 | `MythologyDetectionService` at `mythology/services.py:19-100` active | ✓ | none |
| 22 | `apply_publish_gate` mgmt command at `core/management/commands/apply_publish_gate.py` | ✓ | none |

**Post-Explore verifier-loop (parent-Claude, playbook §14 rule):**

6 load-bearing binary claims from Explore Agent findings grep-verified after Explore return + before shipping to Rigby:

| # | Claim | Source | Verified | Correction? |
|---|-------|--------|----------|-------------|
| 23 | SelfBlog has NO `metadata` field at HEAD | Explore 1 F4.1 | ✓ (:20611-20770 sweep zero `metadata = models.<...>`) | Confirmed — `_check_envelope` dead code for SelfBlog |
| 24 | `views_research_demo.py:966` publish_ready check + `force=true` override | Explore 3 | ✓ (direct read `:965-971`) | Confirmed — Session 998 enforcement point |
| 25 | `content_deliberation_runner.py:138` PublishGate only fires on decision='PUBLISH' | Explore 2 | ✓ (direct read `:138-157`) | Confirmed — REVISE/KILL bypass gate; F0 correction: gate at :140 not :138 (:138 is the condition) |
| 26 | Redundant `publish_ready=True` writer at `content_deliberation_runner.py:151` + `apply_to_blog:603` | Explore 2 + parent verifier | ✓ (direct read) | Confirmed — redundant-not-conflicting |
| 27 | Newsletter task saves as Deliverable not SelfBlog at `tasks_content.py:4353-4390` | Explore 2 + Explore 4 | ✓ (Explore 2 direct verification) | Confirmed |
| 28 | Zero SendGrid/mailgun/postmark hits in newsletter path | Explore 4 F2 + parent grep | ✓ | Confirmed — only `bpaas/build_packet_schema.py:307` mentions SMTP as MVP-required-not-implemented |

### 20.3a Anchor-update recommendations for xx99 §7 consumption (F10 + F11 Rigby fold)

**F10 Rigby fold — first-class anchor rule to prevent xx99 from assuming "publish = distributed":**

> **Publishing is currently a DB state transition with no guaranteed outbound side-effects.** Auditability + correction are therefore structurally absent + must be added before any rail becomes "real." (Evidence: §1.5 four-actor enforcement contract + §5.3.1 F5-proven-negative sweep + §7.6 Discord broadcast triggered externally to gate + §5.4 F7 newsletter is content-generation-rail-not-publish-rail + §16.1 T.15.C1 CRITICAL post-publish correction MISSING.)

**F11 Rigby fold — promote R.CONTENT.EXHAUSTIVE-PUBLISH-MUTATIONS-SWEEP to §7 anchor recommendation** (originally new T2 in §19; now surfaces as top-tier anchor for xx99 §7 consumption):

> Every SelfBlog `status='published'` or variant equivalent mutation should be enumerated in a canonical **mutator → entry point → authorization context → audit artifact → side-effects** table. This is the pre-requisite for post-publish correction feasibility (T.15.C1 CRITICAL), audit-trail construction (T.15.C6 / D.14.C5), and event-flow decisions (§10 gap). xx99 D65c C2/C3/C4 evidence depends on this enumeration.

### 20.4 Cross-Arc Handoffs (§20.6 per playbook)

**Cat C RECEIVES from:**
- **Cat D S1603 T.15.6** — triple-gate composition contract MISSING (HIGH boundary_violation) → Cat C owns resolution recording; 4-candidate framework §17.4 for xx99 D65b B4 consumption
- **Cat A S1601 §9.1** — SelfBlog.objects.create bypass at `content_deliberation_runner.py:401` → Cat C confirms gate is advisory + post-hoc; SelfBlog exists BEFORE gate runs (§7.1 flow trace)
- **Cat B S1602 §14** — DecisionEnforcer produces PUBLISH/REVISE/KILL mandate → Cat C confirms gate only runs on PUBLISH at `runner.py:138`; REVISE and KILL bypass gate entirely
- **Cat B S1602 §16.1** — stats_snapshot['deliberation'] Cat B writer at `runner.py:415` → Cat C reads at `_check_research_backing:519-527`; Cat A + Cat D + Cat B tri-writer contract needs canonicalization (T.15.C12)
- **Cat B S1602 §15.3** — queue_agent_task landmine at `decision_enforcer_agent.py:455-476` → Cat C observes; NOT reached under normal PUBLISH-only gate firing but cross-boundary observability handoff
- **S1504 §14.3** — SportsBettingBrief WRITE-ONLY-FORGOTTEN CRITICAL → Cat C confirms no publish rail exists for SportsBettingBrief; extends Cat D T.15.2 CRITICAL; T.15.C3
- **S1402 F.B1** — OutreachDraft delivery ZERO outbound CRITICAL (F8-upgraded) → Cat C confirms same pattern class extends to newsletter (T.15.C2); pattern class strengthened
- **S1403 F.C4** — ContentEngagement docstring drift → Cat C confirms no post-publish learning loop; extends Cat D §14.1; T.15.C8

**Cat C EMITS to:**
- **Cat E S1605** — post-publish approval UX + `force=true` audit trail + auto-publish beat audit trail + Rigby PA-tool contract on publish-rail actions; frontend auth contract (T.15.C14 shared)
- **Cat F S1606** — three-axis D65b/D65c evidence for cross-domain lens; consume Cat C §17.4 4-candidate framework
- **xx99 S1699** — D65b B1-B4 + D65c C1-C5 evidence + T1 recommendations R.CONTENT.TRIPLE-GATE-COMPOSITION-CONTRACT + R.CONTENT.PUBLISHGATE-SCOPE-CANONICALIZATION + R.CONTENT.POST-PUBLISH-CORRECTION-LOOPS + R.CONTENT.NEWSLETTER-LIVE-SEND-PATH + inherited R.CONTENT.OUTREACHDRAFT-DELIVERY

**Cat C UNKs surfaced for downstream:**
- **UNK-C1** — Newsletter dry_run promotion path unknown (D65c C1 → xx99 owned)
- **UNK-C2** — Post-publish correction loops absent (D65c C2 → xx99 owned)
- **UNK-C3** — Discord broadcast audit trail absent (D65c C3 → xx99 owned)
- **UNK-C4** — `force=true` bypass audit trail absent (D65c C4 → xx99 owned)
- **UNK-C5** — audit-2026/04 §10 novelty/structure calibration OPEN (T2 R.CONTENT.PUBLISHGATE-CALIBRATION-INVESTIGATION owed)
- **UNK-C6** — SelfBlog STATUS_CHOICES exact value list not fully enumerated in this audit (verified STATUS_CHOICES exists at :20639 but individual choice values not read line-by-line; flagged for potential Rigby SIGN request)

### 20.5 Rigby SIGN fold notes

**SIGN cycle 1 completed on fresh isolation pin `pa-4ce64003711de4f1` — SIGN-with-edits at High confidence overall + High Batch C + Medium-High Batch B + High Batch A + High final-verdict single-question follow-up. Final verdict: SIGN-clean-post-folds at High confidence.** 3-batch pattern per `feedback_rigby_sign_worker_instability_recovery.md` (~8 findings per batch + 1 final-verdict Q).

F1-F14 folds landed pre-commit:

| # | Fold | Location | Rigby framing |
|---|------|----------|---------------|
| F1 | §4.2.2 proof-precision tightening | §4.2.2 | "SelfBlog class body specifically lacks metadata" not "models file lacks metadata"; independently grep-verified against SelfBlog block :20611-20790 (27 fields enumerated; zero contain `metadata = models.<...>`) |
| F2 | §1.5 enforcement-authority contract | §1.5 (NEW) | First-class boundary rule: PublishGate=advisory + REST endpoint=enforcement + force=true=admin bypass + auto_publish beat=fourth-actor bypass — 4-actor contract |
| F3 | §3.10a publish_ready writer callout | §3.10a (NEW) | canonical apply_to_blog:603 + redundant Session 1008 fast-path runner:151; non-conflicting today; divergence hazard |
| F4 | §3.10b gate-evaluation trigger + failure modes | §3.10b (NEW) | 5-trigger surface table + cross-cutting failure modes (Celery down, retry policy, idempotency) |
| F5 | §5.3.1 Discord proven-negative sweep | §5.3.1 (NEW) | 4-actor table: PublishGate + REST endpoint + auto_publish beat + post-save signals — all zero Discord side-effect verified |
| F6 | §7.4 auto_publish precision | §7.4 (updated) | Beat body verified at HEAD: flips status in-model via `save(update_fields=['status'])`; no shared helper; no AutoPublishEvent; log-line-only |
| F7 | §5.4 Newsletter reframe | §5.4 (updated) | Newsletter is CONTENT-GENERATION rail, NOT PUBLISH rail — until live-send lands, dry_run promotion alone doesn't enable delivery |
| F8 | §4.5 zero-events extended verification | §4.5 (updated) | Grep sample of Broadcast/discord_message_id/published_at/outbound/notification_log/DeliverableEvent (75 hits across 20 files) — none Cat C publish-rail audit-trail model; deliverable_status_signals.py 0 SelfBlog refs |
| F9 | §14 drift-vs-debt clarification | §14 open (NEW) | Drift = doc/code mismatch; Debt = missing capability/robustness; may overlap when both apply |
| F10 | §20.3a first-class anchor rule | §20.3a (NEW) | "Publishing is DB state transition with no guaranteed outbound side-effects" — xx99 §7 consumption anchor |
| F11 | §20.3a mutation-sweep anchor + §19 T2 elevation | §20.3a + §19 T2 (NEW) | R.CONTENT.EXHAUSTIVE-PUBLISH-MUTATIONS-SWEEP promoted to §7 anchor + §19 T2 |
| F12 | §15 severity rubric preamble | §15 open (NEW) | CRITICAL = irreversible external side-effect w/o corrective mechanism; HIGH = internal correctness gap or missing outbound infra; MEDIUM = audit-trail gap; LOW = doc drift |
| F13 | §19 T2 calibration concrete action | §19 T2 (updated) | Reproduce with 12+ representative SelfBlogs fixed test corpus; classify broken-scoring vs threshold-recalibrate |
| F14 | §7.4 evaluate_unscored_blogs semantics | §7.4 (updated) | First-pass-only via `quality_score__isnull=True`; NOT continuous re-eval; edited/rescoring/pattern-DB-update gaps acknowledged |

**Pre-Rigby-SIGN Chris D45-analog gate:** Chris has NOT ratified S1604 posture as final at this session; per playbook §14.5 no-implementation rule, Cat C does not select D65b/D65c posture (evidence only). Chris-ratification remains xx99 S1699 Chris-gated ADR sequence.

### 20.6 D48 preemptive stability-probe gate (13th arm) — OUTCOME

**Held clean through Batch A + B + C + final-verdict single-question follow-up.** Pattern per playbook §15 codification-ready-STRENGTHENED at S1603 close now EXTENDS to 13-arc + seven-consecutive-fully-clean-arms sub-pattern becomes **eight-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604 CONFIRMED**. Rigby SIGN isolation pin `pa-4ce64003711de4f1` retired at S1604 close via `session_tool.retire`.

Pattern codification-ready-STRENGTHENED-FURTHER for playbook v3 §15 based on 8-consecutive-clean-arms evidence — the SIGN routing structure (3-batch + 1 final-verdict) + fresh isolation pin per child + explicit fold enumeration per batch is a robust workflow at 13-arc scale.

### 20.7 Appendix — Frontmatter provenance

- **Session:** 1604
- **Category:** child_audit
- **Domain slug:** content
- **Research group:** 1600
- **Child slot:** P4 (F3 fold — moved from P3→P4 because Cat C consumes Cat D's canonical decision D65a-analog)
- **Authority:** research
- **Status:** active (SIGN-clean-post-folds; pre-Chris-ratify per playbook §16 draft-first workflow — Chris explicit "commit it" instruction pending)
- **Verifier loop:** 22 pre-Explore + 6 post-Explore + 4 SIGN-fold sub-verifier grep-checks (F1 SelfBlog block metadata absence; F5 REST endpoint Discord absence; F6 auto_publish_approved_blogs body precision; F8 generic-name patterns) — all grep-verified against HEAD `20c75efd`. Rigby SIGN status: **SIGN-clean-post-folds at High confidence** on fresh isolation pin `pa-4ce64003711de4f1` (retired at S1604 close). D48 13th-arm preemptive stability-probe gate held clean; eight-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604 CONFIRMED.
- **Dependencies:** Group 1600 parent (1600_content_domain_scoping.md); S1601 Cat A; S1602 Cat B; S1603 Cat D; S1504 Sports Cat D precedent; S1402 Revenue Cat B; S1403 Revenue Cat C.
- **Delegates to:** Cat E S1605; Cat F S1606; xx99 S1699.
- **HEAD SHA at draft time:** `20c75efd` (S1603 docs cascade merge; per commit `docs: refresh RAG cascade artifacts after S1603 Group 1600 Cat D audit merge (#2824)`).
- **D62 pre-brief mini-schema applied upfront:** §4.8 (Models), §5.6 (Services), §6.5 (APIs), §8.5 (Lifecycle) — **fourth Group 1600 sibling to propagate the D62 pre-brief-upfront pattern per parent D68 F8/F10 folds**.
