---
title: "Content Category E — Rigby-Facing PA Tooling + Operator Approval UX (Child Audit)"
status: active
authority: research
research_group: 1600
domain_slug: content
session: 1605
category: child_audit
child_slot: P5
generated: 2026-07-02
last_verified: 2026-07-02
dependencies_on:
  - Group 1600 parent (1600_content_domain_scoping.md — Cat E boundary at §3 E; F8 fold one-sentence boundary discipline; F11 Cat E feedback-hazard note downstream-by-default P1→P6 sequence)
  - Group 1600 P1 S1601 (1601_content_claims_pack_deliberation_pipeline_v2_audit.md — Document workspace FK RAG-SCOPE cross-tenant risk UNK-1; SelfBlog.objects.create bypass at runner:401)
  - Group 1600 P2 S1602 (1602_content_reviewers_decision_enforcement_audit.md — Cat B pattern class extended to Cat E for content_review handler shared code path)
  - Group 1600 P3 S1603 (1603_content_deliverable_base_variants_audit.md — Cat D canonical decision D65a: Deliverable base + 5 parallel variants + zero Deliverable subclass FK from variant models; extends to Cat E tool-surface acting on base Deliverable + zero-variant-touch by design)
  - Group 1600 P4 S1604 (1604_content_publish_gate_publish_rails_audit.md — T.15.C6 force=true audit-trail gap; D.14.C5 auto_publish_approved_blogs beat audit-trail gap; T.15.C14 frontend auth contract implicit + no PublishGate-side auth check; T.15.C2 CRITICAL newsletter live-send infrastructure MISSING extends S1402 F.B1)
  - Group 1500 P4 S1504 (1504_sports_betting_content_pipeline_audit.md — cross-arc SportsBettingBrief WRITE-ONLY-FORGOTTEN CRITICAL; Cat E does not expose Sports variant surface)
  - Group 1400 P2 S1402 (1402_revenue_outreach_composition_delivery_audit.md — F.B1 OutreachDraft delivery ZERO outbound extends to Newsletter tool per S1604 F7; Cat E inherits pattern-class 2-of-2)
delegates_to:
  - Cat F S1606 — cross-domain integration lens (consumes Cat E evidence for D65e posture + tool-surface unification decision)
  - xx99 S1699 — canonical summary (D65a/D65b/D65c/D65e posture-decision evidence brief; T1 R.CONTENT.RIGBY-TOOL-SURFACE-UNIFICATION resolution owner; T1 R.CONTENT.FORCE-BYPASS-AUTH-BOUNDARY new Cat E-owned)
verifier_loop: parent-Claude verifier-loop (playbook §14 rule) 24 pre-Explore + 8 post-Explore + 2 Rigby-runtime-probe (auto_publish beat runtime probe via ops_tool + scheduled_tasks_tool) load-bearing binary claims all grep-verified against HEAD `f5065624`. **Rigby SIGN Cycle 1 SIGN-with-edits at High confidence overall (Batch A 0.84 + Batch B 0.80 + Batch C 0.82 + final consolidated 0.83) → SIGN-clean-post-folds at High confidence** on fresh isolation pin `pa-b1b26f4f35474df8` (Rigby-side create_fresh; retired at S1605 close via session_tool.retire). **F1-F10 folds landed pre-commit.** D48 preemptive stability-probe gate 14th arm HELD CLEAN across 3 batches + final-verdict — **NINE-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605 CONFIRMED** — codification-ready-STRENGTHENED-FURTHER for playbook v3 §15.
---

# Session 1605 — Group 1600 Cat E: Rigby-Facing PA Tooling + Operator Approval UX (Child Audit)

## 1. Executive Summary

Cat E is the fifth child audit under Group 1600 (Content Domain), executing per parent D66 P5 slot after Cat A (S1601 ClaimsPack) + Cat B (S1602 Reviewers) + Cat D (S1603 Deliverable Base) + Cat C (S1604 PublishGate). Cat E answers the parent-scoped boundary question — *how Rigby + Chris interact with the content pipeline via PA-tool actions + frontend approval mutations*. Cat E does **NOT** own the underlying object model (Cat D S1603), gate semantics (Cat C S1604), reviewer verdicts (Cat B S1602), or ClaimsPack/deliberation mechanics (Cat A S1601).

The parent §5 P5 canonical decision question — *"is Rigby's tool surface (deliverable_tool + content_tool + blog_tool + newsletter_tool) 4 parallel APIs OR 1 unified API?"* — resolves as a **layered answer at HEAD**: unified at dispatcher layer + 4 parallel-schema contracts at PA-tool layer + shared handler code paths at implementation layer. Cat E records this as D65e-analog evidence for xx99 (§1.2 axes). **Rigby SIGN Batch A F2 fold (2026-07-02) — xx99-consumption phrasing sentence: "One dispatcher, four tool contracts, shared handler core."**

### 1.1 Headline findings

- **All 4 Cat E PA-tool surfaces are canonically registered at HEAD.** `core/services/tool_dispatcher.py` registers `content_tool` → `_handle_content` at `:476`, `deliverable_tool` → `_handle_deliverable_direct` at `:479`, `blog_tool` → `_handle_blog_direct` at `:490`, `newsletter_tool` → `_handle_newsletter` at `:521`. Schemas at `core/services/pa_tool_schemas.py:3288` (content_tool) + `:3392` (deliverable_tool) + `:3464` (blog_tool) + `:3501` (newsletter_tool) are symmetric with registrations — zero orphan-schema or orphan-registration gaps. **D65e-B2 evidence: tool-registration coverage complete.**

- **Session 1077 split rationale is TACTICAL, not STRUCTURAL.** Schema-comment provenance at `pa_tool_schemas.py:3389` ("Focused deliverable_tool split from content_tool") + `:3461` (blog_tool split) + `td_handlers_content.py:82` (focused handlers). **Split motivation: reduce GPT-5.2 function-calling confusion via smaller schemas per tool** (matches `tool_dispatcher.py:478` comment). No dedicated S1077 audit doc exists at HEAD (grep `docs/handoffs/SESSION_1077*` returns 0 hits). This means the parent §3 E load-bearing question — *"is the Session 1077 split design intent or drift?"* — resolves as **design intent for LLM-side clarity, NOT structural separation of concerns**. The 3 focused tools + parent content_tool + newsletter_tool coexist as 4 canonical surfaces sharing 2 handler modules (`td_handlers_content.py` + `td_handlers_newsletter.py`) and 3 shared internal helpers (`_handle_content_review`, `_handle_deliverables`, `_handle_blog_query`).

- **Dispatcher is a UNIFIED single-entrypoint surface.** `ToolDispatcher.execute()` at `tool_dispatcher.py:584` is THE async entrypoint for all Cat E calls. Auth is enforced BEFORE handler dispatch via `AssistantProfile.get_allowed_tools()` at `:687-720` — returns `ToolResult(ok=False, error_code='TOOL_PERMISSION_DENIED')` at `:702-705` if tool not in allowed set. Response envelope is `ToolResult` dataclass at `:163-174` (`{ok, tool, latency_ms, error_code, error_message, trace_id, result}`) — no silent failures across timeout (`:841-868`) + exception (`:870-897`) + permission-denied paths. **D65e-B3 evidence: dispatcher layer is unified; parallel-API surface is at schema+handler layer only.**

- **Workspace scoping is HANDLER-LEVEL + OPT-IN, NOT DISPATCHER-MANDATORY.** `_handle_deliverables` at `td_handlers_agents.py:1580-1624` resolves workspace via (1) explicit `payload.workspace_id`, (2) fallback `AssistantProfile.workspace_id`. **AssistantProfile lookup failure silently degrades to unscoped query with warning log** at `:1594-1600` — the exception branch logs "PA deliverable query will run unscoped and may return cross-workspace results" but the query proceeds anyway. **CONFIRMS S1601 UNK-1 (Document workspace FK RAG-SCOPE cross-tenant risk) has an analog in Cat E deliverable_tool surface: silent-degrade to cross-workspace results on AssistantProfile lookup failure. T.15.E1 HIGH.**

- **Frontend approval UX is a bare status-flip with ZERO downstream auth enforcement.** `views_research_demo.py:900` (approve_self_blog_api) + `:942` (publish_self_blog_api) carry ONLY `@require_http_methods(["POST"])` — **ZERO `@login_required`, ZERO `@permission_required`, ZERO `@user_passes_test`, ZERO in-body `request.user.is_staff` check**. Approve endpoint sets `blog.status='approved'` at `:918`; publish endpoint sets `blog.status='published'` at `:979`. Neither modifies `publish_ready` field. PublishGate enforcement lives only at `:966` (`if not force and not blog.publish_ready`) — but skipped entirely on `force=true`. **T.15.C14 (Cat E-owned per S1604 cross-arc handoff) CONFIRMED-STRENGTHENED at HEAD: no backend role gate exists on either endpoint. Any authenticated session with a blog_id can approve/publish any blog. Cat E flags as T.15.E2 CRITICAL.**

- **ContentStudioTab frontend hardcodes `force=true` with NO admin gating — NEW HIGH Cat E-owned finding.** `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx:2215` calls `blogsApi.publish(blog.id, true)` — hardcoded `force=true` on the workspace UI Publish button. Contrasts BlogViewerPage.tsx:396 (`publishMutation.mutate(false)`) which hardcodes `force=false`. No role check gates the ContentStudioTab button; no confirmation dialog; no admin-only conditional render. **Any workspace user with access to ContentStudioTab can bypass PublishGate quality checks. Frontend-side asymmetric bypass is undocumented in narrative anchors + topic docs.** Also `canPublish` inconsistent: ContentStudioTab allows publish on `draft` OR `approved` at `:2238` vs BlogViewerPage `approved`-only at `:394`. **T.15.E3 HIGH Cat E-owned; escalates S1604 T.15.C6 audit-trail gap from admin-only concern to any-authenticated-user bypass concern.**

- **Cat E audit-trail is Trilevel: NONE at dispatch + NONE at REST + PARTIAL at deliverable_tool.** ToolCallRecord at `core/models_tool_calls.py:19` persists agent tool calls (agent_name/tool_name/parameters/result_summary/latency_ms/success) — captures PA tool invocations but **does NOT capture direct REST endpoint calls** (`views_research_demo.py:900/:943` bypass PA/ToolDispatcher entirely). DeliverableEvent at `core/models_deliverables.py:561-614` is written by (a) `detail` action at `td_handlers_agents.py:1868-1876` (`synthesis_viewed`); (b) `save` action at `:1944-1948` (`deliverable_saved`); (c) `set_status` action at `:2938-2946` (`status_transition` with metadata.ctx). **`update` action status changes do NOT audit** — silently bypass DeliverableEvent (`:2216-2221` write status directly via `save(update_fields=['status'])`). **ZERO ForcedPublishEvent, AutoPublishEvent, PublishGateEvent, PublishEvent, AuditEvent, AdminActionLog models exist at HEAD** (grep `class (ForcedPublishEvent|AutoPublishEvent|PublishGateEvent|PublishEvent|AuditEvent)` returns 0 hits across all `*.py` files). Cat E confirms all 5 S1604-flagged audit-trail gaps at HEAD.

- **Newsletter tool is CONTENT-GENERATION rail — S1604 F7 CONFIRMED-STRENGTHENED at HEAD.** `_handle_newsletter` at `td_handlers_newsletter.py:25-44` implements all 7 advertised actions (`prepare/outline/validate/metrics/list_issues/config/sources`). **NO handler for publish, send, dispatch, or delivery.** Grep across newsletter path (`td_handlers_newsletter.py` + `services/newsletter_publisher.py` + `services/newsletter_sources.py` + `tasks_content.py:4234-4413` `_impl_generate_operator_edge_newsletter`) returns **0 hits for `sendgrid|mailgun|postmark|smtplib|SMTP|send_mail|EmailMessage|EmailMultiAlternatives`**. `NewsletterSubscriber` model exists at `models_newsletter.py:8-31` (used by public signup endpoint at `views_newsletter.py:19-77`) but **newsletter tool NEVER queries it**. Cross-arc pattern class 2-of-2 (Newsletter + OutreachDraft both content-generation-only) — F8-CRITICAL pattern class extends per S1604 T.15.C2. Newsletter beat locked at `dry_run=True` since S1222 P6 (>4mo elapsed; `core/celery.py:436`); zero Rigby-visible flip mechanism.

- **`auto_publish_approved_blogs` beat schedule GAP — NEW HIGH Cat E-owned finding beyond S1604 D.14.C5; RUNTIME-CONFIRMED ABSENT via Rigby SIGN Batch A F1 fold.** Task defined at `core/tasks.py:8056-8079` (`@shared_task(name='core.tasks.auto_publish_approved_blogs')`); queue routing at `core/settings.py:1394` (`'queue': 'content'`). **grep `auto_publish_approved_blogs` in `core/celery.py` returns 0 hits — no `beat_schedule` entry at HEAD.** At least 5 docs claim "daily 6 AM" cadence (`docs/topics/celery-workers.md:163`, `docs/topics/content-pipeline.md:176/189`, `docs/narratives/CONTENT_PIPELINE.md:240`, S1604 §7.4 body, `SESSION_1033_VALUE_CHAIN_COMPLETION.md:86`). **Rigby SIGN Batch A F1 fold (2026-07-02) — RUNTIME-VERIFIED via `ops_tool.celery_task_history` filter=auto_publish_approved_blogs 30d = 0 events + `scheduled_tasks_tool` filter=auto_publish_approved_blogs = 0 tasks (0 filtered from 92 total_enabled). Beat is CONFIRMED ABSENT at HEAD; no PeriodicTask ORM row exists; task NEVER FIRES. All 5 doc claims are DRIFT-CONFIRMED-STALE.** **S1604 D.14.C5 auto-publish audit-trail gap is MOOT because no auto-publish event ever fires** — cross-arc CORRECTION owed to S1604 §7.4 F6 fold + 5 doc PRs owed to remove the "daily 6 AM" claim. **T.15.E4 severity remains HIGH but state changes from "contested/UNKNOWN" to "CONFIRMED absent; task never fires; cross-arc correction owed."**

- **Deliverable memory-rule traps status matrix at HEAD:**
  - `feedback_deliverable_create_defaults_to_completed.md` — **CONFIRMED at HEAD as DESIGN** (not bug). `td_handlers_agents.py:2052` hardcodes `status='completed'` in `create_deliverable()` factory call. S1248 P2b fix documented at `:2091-2107` (return top-level `status` field for caller-visible echo + optional `return_detail` for follow-up verification). No explicit `status` param accepted from payload.
  - `feedback_deliverable_status_via_content_complete.md` — **CONFIRMED at HEAD as DESIGN + AUDIT-TRAIL GAP.** `update` action accepts `status` param directly + saves via `obj.save(update_fields=['status'])` at `:2216-2221` — no DeliverableEvent written. Only `set_status` action writes audit trail (`:2846-2966`) but whitelists `completed↔ready` transitions only + requires `reason` on `completed→ready`. Callers wanting audit trail MUST use `content_tool.content_complete` alias which routes through `_handle_content_review` at `td_handlers_content.py:610-653` and sets `deliverable.status='completed'` + persists `feedback` to `metadata['complete_reason']` + calls `_record_content_feedback(action='complete')`.
  - `feedback_llm_autofills_boolean_params_with_false.md` — **FIXED S1227** at 5 sites: `has_initiative` at `:1692-1699` (truthy-only + `'false'` sentinel), `orphans` at `:1712-1715`, `show_all` at `:1631`, `saved` at `:1652-1654`, `exclude_archived` at `:2635-2637`. Zero residual `is not None` checks on boolean filter params at HEAD.
  - `feedback_deliverable_tool_use_append_for_large_payloads.md` — **UNKNOWN at HEAD** — no code path grepped that silently falls back from `update` to `list` on payload size >6kB. Memory rule may be stale from an earlier session (Session 1176 marker); T2 R.CONTENT.DELIVERABLE-TOOL-APPEND-VERIFY suggested to formally close the memory rule with either a repro test or a stale-rule retirement PR.

### 1.2 Decisions this audit records (D65e-analog handoff to xx99)

Per playbook §14.5 no-implementation rule, Cat E **does not** select the posture. It records evidence for the xx99 posture-decision brief per D65e (Rigby PA-tool surface unification scope) — a fourth axis alongside Cat A/B/C/D's D65a/D65b/D65c.

- **D65e evidence axes for xx99:**
  - **E1 Tool-schema unification scope** — 4 canonical schemas at HEAD (content_tool/deliverable_tool/blog_tool/newsletter_tool). Design intent per S1077 comments is "focused" schemas to reduce GPT-5.2 function-calling confusion, NOT structural separation of concerns. Cat E records evidence + posture-decision candidates (§17.5 for xx99 D65e consumption).
  - **E2 Tool-registration coverage** — 4-of-4 registered at `tool_dispatcher.py:476/479/490/521`; symmetric with schemas. No orphan-schema or orphan-registration gaps. **VERIFIED CLEAN at HEAD.**
  - **E3 Handler consolidation** — `td_handlers_content.py` (Cat E-core) + `td_handlers_newsletter.py` (Cat E-newsletter) + 3 shared internal helpers (`_handle_content_review`, `_handle_deliverables`, `_handle_blog_query`). `blog_tool` action set MAPS via ACTION_MAP at `:165-169` and bridges to `_handle_content_review` at `:179` with `review_payload`. `content_tool` action set uses ACTION_ALIASES at `:4309-4325` and CONTENT_REVIEW_MAP at `:4356-4367` to dispatch to `_handle_content_review` at `:4372`. **Both focused tools' publish/approve paths converge on the same handler code.**
  - **E4 Approval-UX contract** — 2 frontend surfaces (BlogViewerPage, ContentStudioTab) hitting the same 2 REST endpoints (`views_research_demo.py:900`, `:942`) with **asymmetric `force` semantics** (BlogViewerPage hardcodes `force=false`; ContentStudioTab hardcodes `force=true`). ZERO backend role gate. ZERO frontend admin-only conditional render.
  - **E5 Audit trail** — Trilevel: NONE at REST endpoints + NONE at auto_publish beat + PARTIAL at deliverable_tool (`set_status` + `detail` + `save` write DeliverableEvent; `update` + `create` + `append` + `delete` do NOT). ToolCallRecord captures PA-side but NOT REST-side.
  - **E6 Auth boundary** — Dispatcher-side gate via `AssistantProfile.get_allowed_tools()`; REST-side ZERO decorator + ZERO in-body role check. Cross-boundary asymmetry.
  - **E7 Workspace scoping** — Handler-level opt-in; silent-degrade on AssistantProfile lookup failure per E1 finding. Consumes S1601 UNK-1 pattern.

- **Cross-arc handoff records (Cat E receives + emits):**
  - **RECEIVES from Cat A S1601**: UNK-1 Document workspace FK RAG-SCOPE cross-tenant risk. Cat E confirms analog at `td_handlers_agents.py:1594-1600` deliverable_tool silent-degrade; T.15.E1 HIGH.
  - **RECEIVES from Cat B S1602**: content_review_tool handler shared by blog_tool bridge + content_tool alias; Cat E confirms canonical dispatch integrity.
  - **RECEIVES from Cat C S1604**: T.15.C6 (force=true audit-trail gap) — Cat E owns tool-surface + admin visibility (T.15.E3 escalates from admin-only to any-user); D.14.C5 (auto_publish beat audit-trail gap) — Cat E confirms + escalates (T.15.E4 beat schedule missing altogether); T.15.C14 (frontend auth contract implicit) — Cat E owns tool-surface + endpoint audit (T.15.E2 CRITICAL frontend + endpoint both lack auth boundary).
  - **RECEIVES from Cat D S1603**: canonical Deliverable base + 5 parallel variants. Cat E confirms deliverable_tool touches base Deliverable only; zero variant-model FK from Cat E schemas.
  - **RECEIVES from S1402 F.B1**: OutreachDraft delivery ZERO outbound; Cat E confirms newsletter extends 2-of-2 pattern class (F8-CRITICAL) — pattern class validated across 2 domains + 2 rails.
  - **EMITS to Cat F S1606**: D65e evidence for cross-domain lens; xx99 R.CONTENT.RIGBY-TOOL-SURFACE-UNIFICATION T1 recommendation.
  - **EMITS to xx99 S1699**: D65e 7-axis evidence brief + T1 R.CONTENT.RIGBY-TOOL-SURFACE-UNIFICATION + T1 R.CONTENT.FORCE-BYPASS-AUTH-BOUNDARY (NEW Cat E-owned) + T1 R.CONTENT.AUTO-PUBLISH-BEAT-SCHEDULE (NEW Cat E-owned).

### 1.3 Maturity verdict

**Cat E overall: PARTIAL.** The dispatcher + ToolResult envelope + AssistantProfile allowlist auth + ToolCallRecord telemetry constitute STABLE tool-execution infrastructure. The 4 focused schemas + Session 1077 split + shared handler dispatch are WORKING as designed with substantive documentation gaps. The frontend approval UX is PARTIAL — 2 surfaces + asymmetric force semantics + no confirmation dialog + no role gate + no audit trail; usable but non-canonical. The REST endpoint auth boundary is EXPERIMENTAL — implicit-session-only + zero decorator + zero in-body check; safe only under strict trust assumption on frontend + middleware. Newsletter tool is EXPERIMENTAL — dry_run indefinitely parked + zero live-send infra + Rigby-invisible promotion path. Cross-arc auto_publish beat is UNKNOWN — scheduled per 5 docs but not present in canonical schedule at HEAD.

### 1.4 Cat E authority scope reminder (parent F8 boundary)

Cat E is the *"how Rigby + Chris interact with the content pipeline via PA-tool actions + frontend approval mutations"* category per parent F8 Rigby fold. Cat E owns:

- All 4 canonical PA-tool surfaces (schema + registration + handler + dispatch chain + auth boundary + response envelope).
- Frontend approval mutation contract (BlogViewerPage + ContentStudioTab + shared blogsApi).
- REST endpoint audit trail + role gate + admin bypass visibility.
- Tool-side audit-trail model (ToolCallRecord coverage + DeliverableEvent coverage + gaps).
- Workspace scoping enforcement at handler layer + cross-tenant risk consumption.
- **Cat E does NOT own**: Deliverable base object model (Cat D); SelfBlog variant persistence (Cat D); PublishGate scoring or class-constant thresholds (Cat C); reviewer verdicts + DecisionEnforcer (Cat B); ClaimsPack + deliberation pipeline (Cat A).

### 1.5 Rigby PA-tool + approval-UX enforcement-authority contract (four-item mini-schema per surface upfront — D62 propagation)

Per parent D68 F8/F10 folds — this is the **fifth sibling** of Group 1600 to propagate the 4-item pre-brief mini-schema per surface upfront (after S1601 first + S1602 second + S1603 third + S1604 fourth). Each Cat E surface gets a 4-item mini-brief at first mention.

**Four canonical Cat E PA-tool surfaces (each with mini-schema):**

**1. `content_tool`** — parent aggregate schema retained post-S1077 split.
- **Purpose:** Umbrella tool exposing 30+ mixed content actions (content review, blog generation, deliverables sub-actions, newsletter delegation, metadata queries).
- **Advertised actions (:3288-3387):** `content_stats, content_list, content_detail, content_search, content_recent, content_approve, content_reject, content_complete` (8 review-side) + `generate_blog, generate_newsletter, bulk_archive, bulk_archive_published, run_cleanup, deliverable_*` (11 mutation-side) + `podcasts, series, content_studio, initiative_doc` (4 metadata) = **30+ actions total**.
- **Handler:** `_handle_content` at `td_handlers_content.py:4294-4495` — routes via ACTION_ALIASES (`approve→content_approve`, `reject→content_reject`, `complete→content_complete` + `mark_complete/mark_completed/done` aliases at `:4309-4325`) and CONTENT_REVIEW_MAP (`content_approve→approve`, `content_reject→reject`, `content_complete→complete` at `:4356-4367`) → dispatches to `_handle_content_review` at `:4372`.
- **Registration:** `tool_dispatcher.py:476` `self.register("content_tool", self._handle_content)`.

**2. `deliverable_tool`** — Session 1077 focused split for Deliverable CRUD + governance.
- **Purpose:** Rigby-facing CRUD + governance for base Deliverable model (S1603 Cat D canonical). NOT variant-aware; touches base Deliverable only.
- **Advertised actions (:3402):** 16 (`list, detail, create, update, append, search, save, unsave, stats, duplicates, set_status, normalize, export_pdf, bulk_archive, link_initiative, unlink_initiative`) + 2 unadvertised (`delete, cleanup`) = **18 total**.
- **Handler:** `_handle_deliverable_direct` at `td_handlers_content.py:84` gateway → routes to `_handle_deliverables` at `td_handlers_agents.py:1530` for 14 actions + `_handle_bulk_archive` at `td_handlers_content.py:4613` + `_handle_deliverable_initiative_link` at `:118` for link/unlink.
- **Registration:** `tool_dispatcher.py:479` `self.register("deliverable_tool", self._handle_deliverable_direct)`.

**3. `blog_tool`** — Session 1077 focused split for SelfBlog operations.
- **Purpose:** Rigby-facing SelfBlog operations (approve→publish, reject→archive per S1075 aliases). Bridges to shared `_handle_content_review` for state changes.
- **Advertised actions (:3474):** 8 (`stats, list, detail, search, recent, approve, reject, generate`).
- **Handler:** `_handle_blog_direct` at `td_handlers_content.py:162-182` → ACTION_MAP at `:165-169` (`approve→approve`, `reject→reject`, others map to self) → bridges to `_handle_content_review('content_review_tool', review_payload, user_id, trace_id)` at `:179`. `approve` action ultimately dispatches to `_handle_blog_query` `publish` branch at `:1312-1353` which enforces `publish_ready=True` filter at `:1318` and sets `blog.status='published'` at `:1334`.
- **Registration:** `tool_dispatcher.py:490` `self.register("blog_tool", self._handle_blog_direct)`.

**4. `newsletter_tool`** — Operator Edge newsletter PA surface.
- **Purpose:** Newsletter issue lifecycle (prepare/outline/validate/metrics/list/config/sources). CONTENT-GENERATION rail per S1604 F7; no publish/send/dispatch action.
- **Advertised actions (:3515-3521):** 7 (`prepare, outline, validate, metrics, list_issues, config, sources`).
- **Handler:** `_handle_newsletter` at `td_handlers_newsletter.py:25-44`; 7 action branches; creates 4 Deliverable rows per issue (markdown / HTML / checklist / subject_preheader artifact_types at `:121-239`); uses base Deliverable model (not a 6th variant per Cat D).
- **Registration:** `tool_dispatcher.py:521` `self.register("newsletter_tool", self._handle_newsletter)`.

**Three actors participate in Cat E dispatch; two enforce.**

- **`ToolDispatcher` is ENFORCEMENT.** `tool_dispatcher.py:584` async `execute()` entrypoint + auth gate at `:687-720` via `AssistantProfile.get_allowed_tools()`. All 4 Cat E surfaces route through here. Returns `ToolResult(ok=False, error_code='TOOL_PERMISSION_DENIED')` on gate miss. No Cat E bypass.
- **Cat E handlers are IMPLEMENTATION.** Handlers implement action dispatch + payload validation + workspace scoping (opt-in) + response shaping. NOT authoritative for auth (trust dispatcher). Handler-side workspace scoping is opt-in — `AssistantProfile.workspace_id` fallback silently degrades on lookup failure per `_handle_deliverables:1594-1600`. **Cat E flags this as T.15.E1 HIGH.**
- **REST endpoints are PARALLEL ENFORCEMENT — ZERO AUTH.** `views_research_demo.py:900` (approve) + `:942` (publish) carry only `@require_http_methods(["POST"])` — no `@login_required`, no role check, no workspace check. Frontend hardcodes `force=false` at BlogViewerPage:396 but `force=true` at ContentStudioTab:2215 — asymmetric bypass affordance with ZERO role gate. **Cat E flags this as T.15.E2 CRITICAL + T.15.E3 HIGH.**

---

## 2. Domain Purpose

**Cat E is the Rigby PA-tool surface + operator approval UX layer of the Content Domain.** Its purpose is to expose Cat A/B/C/D's canonical objects, verdicts, gates, and rails to two operators — Rigby (via PA function-calling) and Chris (via frontend approval UI) — as a bounded, auditable, workspace-scoped set of actions.

**Cat E answers:** *"How can Rigby take action on content?"* and *"How can Chris review, approve, and publish content?"* The answers should be — but as this audit shows, are not fully — canonical (one blessed action set per intent), safe (auth-gated + workspace-scoped), audited (every mutation trails an event row), and observable (Rigby can see all state via read actions; Chris can see PublishGate + workflow status via UI).

**Cat E does NOT answer:** *"What is a Deliverable?"* (Cat D S1603), *"What is a review verdict?"* (Cat B S1602), *"What is PublishGate?"* (Cat C S1604), or *"Where do claims come from?"* (Cat A S1601).

**Cat E is downstream by default** per parent F11 fold — the P5 slot after Cat C means gate semantics are fixed; Cat E consumes rather than shapes them. Cat E may emit constrained "must-have" findings requiring bounded correction passes in earlier categories (no re-scope); these surface in §19 T1 recommendations.

---

## 3. Canonical Entry Points

Four PA-tool schemas + one shared dispatcher + two REST endpoints + two frontend approval surfaces.

| Layer | Entry Point | File:Line | Notes |
|-------|-------------|-----------|-------|
| PA schema | `content_tool` | `core/services/pa_tool_schemas.py:3288` | Umbrella; 30+ actions. Aliased actions handled at handler layer. |
| PA schema | `deliverable_tool` | `core/services/pa_tool_schemas.py:3392` | Session 1077 focused split; 16 advertised + 2 unadvertised. |
| PA schema | `blog_tool` | `core/services/pa_tool_schemas.py:3464` | Session 1077 focused split; 8 actions; S1075 aliases (approve→publish, reject→archive). |
| PA schema | `newsletter_tool` | `core/services/pa_tool_schemas.py:3501` | 7 actions; content-generation rail only (no send). |
| Dispatcher | `ToolDispatcher.execute()` | `core/services/tool_dispatcher.py:584` | Async entrypoint for all PA tool calls. |
| Dispatcher gate | `AssistantProfile.get_allowed_tools()` | `core/services/tool_dispatcher.py:687-720` | Pre-handler allowlist enforcement. |
| Handler | `_handle_content` | `core/services/td_handlers_content.py:4294` | content_tool router; ACTION_ALIASES + CONTENT_REVIEW_MAP. |
| Handler | `_handle_deliverable_direct` | `core/services/td_handlers_content.py:84` | deliverable_tool gateway → `_handle_deliverables`. |
| Handler | `_handle_blog_direct` | `core/services/td_handlers_content.py:162` | blog_tool gateway → bridges to `_handle_content_review`. |
| Handler | `_handle_newsletter` | `core/services/td_handlers_newsletter.py:25` | newsletter_tool router; 7 action branches. |
| Shared helper | `_handle_content_review` | `core/services/td_handlers_content.py:235` | Cross-tool state-change handler (publish/archive/complete). |
| Shared helper | `_handle_deliverables` | `core/services/td_handlers_agents.py:1530` | Cross-tool Deliverable CRUD handler. |
| Shared helper | `_handle_blog_query` | `core/services/td_handlers_content.py:1200` | SelfBlog query + publish action branch (approve→publish alias). |
| REST | `approve_self_blog_api` | `core/views_research_demo.py:900-939` | POST `/api/v1/research/self-blog/<uuid>/approve/`. No auth decorator. |
| REST | `publish_self_blog_api` | `core/views_research_demo.py:942-1000` | POST `/api/v1/research/self-blog/<uuid>/publish/`. No auth decorator. `force=true` bypass at `:966-971`. |
| REST URL | approve path | `core/urls.py:3223` | `path('api/v1/research/self-blog/<uuid:blog_id>/approve/', ...)` |
| REST URL | publish path | `core/urls.py:3224` | `path('api/v1/research/self-blog/<uuid:blog_id>/publish/', ...)` |
| Frontend | BlogViewerPage | `frontend/src/pages/BlogViewerPage.tsx:45` | Approve/publish mutations at `:81` (`approveMutation`) + `:93` (`publishMutation`). Hardcodes `force=false` at `:396`. |
| Frontend | ContentStudioTab | `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx:2198-2225` | Same mutations; hardcodes `force=true` at `:2215`. |
| Frontend API | `blogsApi.approve` | `frontend/src/lib/api.ts:3931-3934` | HTTP POST `/v1/research/self-blog/${blogId}/approve/`. |
| Frontend API | `blogsApi.publish` | `frontend/src/lib/api.ts:3936-3940` | HTTP POST `/v1/research/self-blog/${blogId}/publish/` with `{ force }` body. |

---

## 4. Major Models

Cat E acts on Cat D-owned models. No Cat E-owned model exists at HEAD. This section maps model touch surface.

### 4.1 Read/write model touch matrix

| Model | Cat E Touch | Ownership | File:Line |
|-------|-------------|-----------|-----------|
| `Deliverable` (base) | R/W via deliverable_tool + newsletter_tool | Cat D S1603 | `core/models_deliverables.py:84-130` |
| `DeliverableEvent` (audit) | W via `set_status` + `detail` + `save` actions | Cat D S1603 | `core/models_deliverables.py:561-614` |
| `SelfBlog` | R/W via blog_tool + content_tool review-side | Cat D S1603 | `core/models_unified_system.py:20611-20770` |
| `AssistantProfile` | R for workspace resolution + allowed-tools gate | PA infra (Cat E-adjacent) | `core/models_assistant.py` |
| `ProjectWorkspace` | R for workspace FK resolution | Workspace domain | (workspace model) |
| `Initiative` | R for `link_initiative`/`unlink_initiative` FK ops | Initiative domain | (initiative model) |
| `NewsletterSubscriber` | **NOT queried by Cat E** — public signup only | Newsletter public-side | `core/models_newsletter.py:8-31` |
| `ToolCallRecord` | W (persisted per PA tool call) | PA telemetry infra | `core/models_tool_calls.py:19-131` |
| `ForcedPublishEvent` | **DOES NOT EXIST** at HEAD | — (Cat E T1 candidate) | (0 grep hits) |
| `AutoPublishEvent` | **DOES NOT EXIST** at HEAD | — (Cat E T1 candidate) | (0 grep hits) |
| `PublishGateEvent` | **DOES NOT EXIST** at HEAD | — (Cat C T2 R.CONTENT.PUBLISHGATE-EVENT-TELEMETRY per S1604) | (0 grep hits) |

### 4.2 Cat D variant touch analysis

Per Cat D S1603 §5, 5 parallel variants exist (SelfBlog + OutreachDraft + ClosePack + SportsBettingBrief + BlockchainAuditBrief). Cat E touches:

- **SelfBlog** — YES via blog_tool + content_tool review + newsletter_tool (only-as-Deliverable-artifact).
- **OutreachDraft** — NO via Cat E tools. Owned by revenue-side PA tools (out of Cat E scope).
- **ClosePack** — NO via Cat E tools. Owned by revenue-side PA tools.
- **SportsBettingBrief** — NO via Cat E tools. S1504 §14.3 flags SportsBettingBrief WRITE-ONLY-FORGOTTEN; Cat E confirms absence at PA layer.
- **BlockchainAuditBrief** — NO via Cat E tools.

**Cat E touches ONLY 1-of-5 Cat D variants directly (SelfBlog). Newsletter tool creates base Deliverable rows (not a 6th variant per S1603 Cat D + confirmed by E3).**

---

## 5. Major Services

Cat E is service-thin. There is no `RigbyToolSurfaceService` or `ApprovalUXService` at HEAD. The service layer is implicit in the handler + dispatcher code.

### 5.1 Direct Cat E service surface

| Component | Role | File:Line | Line Count |
|-----------|------|-----------|-----------|
| `ToolDispatcher` class | Central PA-tool router + auth gate + envelope | `core/services/tool_dispatcher.py:1-2500+` | 2500+ (multi-purpose) |
| `td_handlers_content.py` | Content-side PA tool handlers | `core/services/td_handlers_content.py` | 4600+ |
| `td_handlers_newsletter.py` | Newsletter-side PA tool handlers | `core/services/td_handlers_newsletter.py` | 300+ |
| `td_handlers_agents.py` | Shared deliverable/agent handlers | `core/services/td_handlers_agents.py` | 3000+ |
| `pa_tool_schemas.py` | Central PA tool schema registry | `core/services/pa_tool_schemas.py` | 5500+ |

### 5.2 Downstream service dependencies (Cat E consumes)

- `deliverable_factory.py` (Cat D-owned) — `create_deliverable()` called from `_handle_deliverables` create branch at `td_handlers_agents.py:2050`.
- `publish_gate.py` (Cat C-owned) — NOT called directly from Cat E handlers; consumed indirectly via `SelfBlog.publish_ready` field check.
- `content_deliberation_runner.py` (Cat A-owned) — NOT called from Cat E handlers.
- `discord_notifications.py` (Cat C-owned) — NOT called from Cat E handlers; per S1604 §5.3 Discord broadcast is post-publish decoupled.

### 5.3 Missing service candidates (§19 T1 candidates)

- No `RigbyToolAuditService` centralizing tool-invocation audit + admin visibility.
- No `ApprovalUXAuthService` centralizing frontend approval role gate.
- No `AutoPublishBeatMonitor` verifying beat cadence + firing telemetry.

### 5.4 Shared handler dispatch analysis (D65e-E3 evidence)

Both focused tools (blog_tool + content_tool) converge on `_handle_content_review` for state-changing actions:

```
blog_tool.approve → _handle_blog_direct:168 → _handle_content_review:179
                                              ↓ ACTION_ALIASES:261 (approve→publish)
                                              ↓ elif action == 'publish': _handle_blog_query:1312
                                              ↓ filter publish_ready=True at :1318
                                              ↓ blog.status='published' at :1334
                                              ↓ save(update_fields=['status']) at :1335

content_tool.content_approve → _handle_content:4372 → _handle_content_review with alias-mapped action
                                                     ↓ same publish branch
```

**Convergence at `_handle_content_review` is DESIGN.** Session 1077 split was schema-side, not handler-side. Both focused tools share the same state-transition code.

### 5.5 Shared helper cross-tool contamination check

Grep for any handler that directly touches `SelfBlog.status='published'` outside the shared helper convergence path:

- `td_handlers_content.py:1334` (via `_handle_blog_query`) — canonical shared path.
- `views_research_demo.py:979` (REST publish endpoint) — REST path, NOT dispatcher path.
- `core/tasks.py:8074` (`auto_publish_approved_blogs` task body) — beat path.

**3 canonical writers to `SelfBlog.status='published'` at HEAD.** No orphan writers found via grep. This is CLEAN.

---

## 6. Major APIs and Interfaces

Cat E has **3 API layers** — PA-tool (via ToolDispatcher), REST (via views_research_demo), and Frontend (via blogsApi). Each with own auth model.

### 6.1 PA-tool layer

- **Auth model:** `AssistantProfile.get_allowed_tools()` per-user allowlist at `tool_dispatcher.py:687-720`. Rigby default profile carries content_tool/deliverable_tool/blog_tool/newsletter_tool in allowed set.
- **Envelope:** `ToolResult` dataclass at `tool_dispatcher.py:163-174`.
- **Fail-loud:** timeout at `:841`, exception at `:870`, permission-denied at `:702`. No silent failures.
- **Trace:** `trace_id` propagated end-to-end; `latency_ms` recorded per call.

### 6.2 REST layer

- **Auth model:** IMPLICIT session + Django middleware. Zero `@login_required` / `@permission_required` / `@user_passes_test` / in-body `is_staff` check on either approve or publish endpoint.
- **Envelope:** `JsonResponse` with `{success, message, blog: {id, title, status}}` on success or `{success, error, gate_notes?}` on failure.
- **Fail-loud:** try/except with `logger.error` at `:938` (approve) + `:998` (publish). Returns 500 on unexpected exception.
- **Trace:** logger info at `:921` (approve) + `:982` (publish) with title + blog_id.

### 6.3 Frontend layer

- **Auth model:** Cookies via `axios withCredentials: true` at `frontend/src/lib/api.ts:23` + optional token header via interceptor at `:34-36`. No frontend role gate.
- **Envelope:** react-query mutation with typed response.
- **Fail-loud:** No `onError` handler on approve or publish mutation at BlogViewerPage:81/93. Errors bubble to component-level error render at :425-429.
- **Trace:** No frontend trace correlation with backend.

### 6.4 Cross-layer contract asymmetries

| Concern | PA-tool | REST | Frontend | Consistency? |
|---------|---------|------|----------|--------------|
| Auth | Allowlist per user | ZERO decorator | Cookies + optional token | **INCONSISTENT** |
| Role gate | Allowlist implicit | ZERO | ZERO | **INCONSISTENT** |
| Workspace scope | Opt-in handler-level (silent degrade) | ZERO | ZERO | **INCONSISTENT** |
| Force bypass | N/A | `force=true` body param | Hardcoded per surface | **ASYMMETRIC** |
| Audit trail | DeliverableEvent for 3 actions | `logger.info` only | react-query cache invalidation only | **INCONSISTENT** |
| Response envelope | `ToolResult` dataclass | `JsonResponse` dict | react-query typed | **PATTERN-SIMILAR** |

### 6.5 Four-item mini-schema per REST endpoint (D62 propagation)

**1. `approve_self_blog_api`** — `views_research_demo.py:900-939`
- **Purpose:** Session 833 — approve a self-blog for publishing (draft → approved status transition).
- **Method + URL:** `POST /api/v1/research/self-blog/<uuid:blog_id>/approve/`
- **Auth:** ZERO decorator + ZERO body check. Implicit session-only. **T.15.E2 CRITICAL.**
- **State change:** `blog.status = 'approved'` at `:918`; `blog.save()` at `:919`; `logger.info` at `:921`. Does NOT touch `publish_ready`.

**2. `publish_self_blog_api`** — `views_research_demo.py:942-1000`
- **Purpose:** Session 833 — publish an approved self-blog. Can also direct-publish draft if `force=true`.
- **Method + URL:** `POST /api/v1/research/self-blog/<uuid:blog_id>/publish/` + `{force?: boolean}` body.
- **Auth:** ZERO decorator + ZERO body check. **T.15.E2 CRITICAL.**
- **State change:** `blog.status = 'published'` at `:979`; `blog.save()` at `:980`; `logger.info` at `:982`. Does NOT touch `publish_ready`. PublishGate enforcement at `:966-971` (skipped if `force=true`); draft-must-be-approved at `:973` (skipped if `force=true`).

### 6.6 Four-item mini-schema per Frontend approval surface (D62 propagation)

**1. `BlogViewerPage`** — `frontend/src/pages/BlogViewerPage.tsx:45-433`
- **Purpose:** Direct blog viewer with inline approve/publish action for a single blog.
- **Approve button:** `:381` `approveMutation.mutate()` — no confirmation, no force. Only shown if `blog.status === 'draft'` at `:379`.
- **Publish button:** `:396` `publishMutation.mutate(false)` — hardcodes `force=false`, no confirmation. Only shown if `blog.status === 'approved'` at `:394`.
- **Role gate:** ZERO. No `useAuth()`, `useCurrentUser()`, or role-conditional render. Any authenticated user with route access can trigger.

**2. `ContentStudioTab`** — `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx:2198-2400`
- **Purpose:** Workspace content-studio tab embedded in Workspace page; batch approval + publish across many blogs.
- **Approve button:** `:2200` `approveMutation`. Shown if `canApprove` (i.e., `currentStatus === 'draft'`) at `:2237`.
- **Publish button:** `:2393` `canPublish && ...` — `canPublish` allows `draft` OR `approved` at `:2238`, and Publish button calls `blogsApi.publish(blog.id, true)` at `:2215` — **hardcodes `force=true` bypass**.
- **Role gate:** ZERO. Same trust boundary as BlogViewerPage. Any workspace user with tab access can bypass PublishGate on any listed blog. **T.15.E3 HIGH.**

---

## 7. Runtime Flows

### 7.1 Flow A — Rigby PA-tool blog approval + publish

```
Rigby chat message: "publish blog abc123"
  ↓
POST /api/pa/chat/ (pa_chat.py:115)
  ↓
PA worker (Celery pa queue)
  ↓
unified_pa_entrypoint.py:552 process_message()
  ↓
PA_USE_FUNCTION_CALLING=true → _run_agentic_loop() at :1371
  ↓
GPT-5.2 returns tool_call: blog_tool {action: 'approve', blog_id: 'abc123'}
  ↓
ToolDispatcher.execute() at tool_dispatcher.py:584
  ↓
Auth gate: AssistantProfile.get_allowed_tools() at :687 — blog_tool in allowed → PASS
  ↓
_handle_blog_direct at td_handlers_content.py:162
  ↓
ACTION_MAP at :165 → 'approve' maps to 'approve'
  ↓
_handle_content_review('content_review_tool', {action: 'approve', blog_id: 'abc123'}, user_id, trace_id) at :179
  ↓
ACTION_ALIASES at :261 → 'approve' → 'publish'
  ↓
_handle_blog_query at :1312 elif action == 'publish' branch
  ↓
base_qs.filter(id=blog_id, status__in=['approved', 'pending_review'], publish_ready=True) at :1318
  ↓
IF blog is None (e.g., publish_ready=False):
    return {error: 'blog not eligible'}
IF blog found:
    blog.status = 'published' at :1334
    blog.save(update_fields=['status']) at :1335
    _record_content_feedback(action='publish') at :1337-1345
  ↓
Return ToolResult(ok=True, tool='blog_tool', trace_id, result={...})
  ↓
GPT-5.2 continues agentic loop → produces final message
```

**Audit surface:** ToolCallRecord persists agent_name='PA' + tool_name='blog_tool' + parameters + result_summary + latency_ms + success. `_record_content_feedback` writes ContentEngagement row (per S1602/S1603 handler code).

### 7.2 Flow B — Chris frontend BlogViewerPage publish

```
Chris clicks Publish button at BlogViewerPage.tsx:396
  ↓
publishMutation.mutate(false) at :396 → mutation triggers
  ↓
mutationFn at :95: blogsApi.publish(blogId, false)
  ↓
axios POST /v1/research/self-blog/${blogId}/publish/ body={force: false}
  ↓ (withCredentials: true; Django middleware auth via session cookie)
  ↓
core/urls.py:3224 → publish_self_blog_api at views_research_demo.py:943
  ↓
@require_http_methods(["POST"]) — HTTP method check ONLY. No auth decorator.
  ↓
IF blog.status == 'published': return 400 'already published'
IF not force AND not blog.publish_ready: return 400 with gate_notes
IF blog.status == 'draft' AND not force: return 400 'must approve first'
  ↓
blog.status = 'published' at :979
blog.save() at :980
logger.info at :982
  ↓
Return 200 {success: true, message, blog: {id, title, status}}
  ↓
Frontend onSuccess at :98: queryClient.invalidateQueries(['blog', blogId] + ['blogs-page'])
```

**Audit surface:** ONLY `logger.info` at `:982`. ZERO ForcedPublishEvent (not applicable — force=false). NO event model persisted.

### 7.3 Flow C — Chris ContentStudioTab publish (force=true bypass)

```
Chris clicks Publish button at ContentStudioTab.tsx:2393
  ↓
publishMutation.mutate() → mutationFn calls blogsApi.publish(blog.id, true) at :2215
  ↓ (HARDCODED force=true; no confirmation dialog; no admin gate)
  ↓
axios POST /v1/research/self-blog/${blogId}/publish/ body={force: true}
  ↓
publish_self_blog_api at :943
  ↓
IF blog.status == 'published': return 400 (still enforced)
IF not force AND not blog.publish_ready: SKIPPED (force=true)
IF blog.status == 'draft' AND not force: SKIPPED (force=true)
  ↓
blog.status = 'published' at :979 (even if publish_ready=False and status='draft')
blog.save() at :980
logger.info at :982 (does NOT log force=true)
  ↓
Return 200 as before
```

**Audit surface:** ZERO ForcedPublishEvent. ZERO log line documenting `force=true` was used. Ephemeral. **T.15.E3 HIGH.**

### 7.4 Flow D — auto_publish_approved_blogs beat (contested cadence)

```
Beat scheduler (contested cadence — see §14 drift) triggers task
  ↓
core.tasks.auto_publish_approved_blogs @ core/tasks.py:8056
  ↓
blogs = SelfBlog.objects.filter(status='approved', publish_ready=True) at :8066
  ↓
FOR blog in blogs:
    blog.status = 'published' at :8074
    blog.save(update_fields=['status']) at :8075
    published_ids.append(str(blog.id))
    logger.info at :8077
  ↓
Return {published: count, blog_ids: [...]}
```

**Audit surface:** ONLY `logger.info` per blog. ZERO AutoPublishEvent. Task return dict is not persisted. **D.14.C5 handoff CONFIRMED-STRENGTHENED as T.15.E4.**

**Contested cadence:** Task defined + queue-routed but NOT in `core/celery.py` beat_schedule at HEAD. Docs claim "daily 6 AM" (5 sources); grep of celery.py returns 0 hits. **Cat E T.15.E4 HIGH — either docs drift or PeriodicTask ORM row exists outside canonical sync. Rigby runtime probe owed.**

### 7.5 Flow E — Newsletter dry_run parked (S1604 F7 CONFIRMED)

```
generate-operator-edge-newsletter beat @ Fri 06:00 Denver, content queue @ core/celery.py:433-438
  kwargs: {'dry_run': True} at :436 (hardcoded since S1222 P6)
  ↓
_impl_generate_operator_edge_newsletter at tasks_content.py:4234
  ↓
IF dry_run: early return at :4291 with {success: True, dry_run: True, ...}
  ↓ (LLM never runs, ContentWriterAgent never invoked)
IF not dry_run: (unreachable at HEAD)
  ↓
ContentWriterAgent generates content
  ↓
Deliverable rows created (Cat E: newsletter_tool prepare action creates 4 artifact rows per issue)
  ↓ (STOPS — no send infrastructure)
```

**Audit surface:** ZERO email send. ZERO subscriber query. ZERO delivery telemetry. **T.15.C2 CRITICAL confirmed by Cat E.**

---

## 8. Data Ownership and Lifecycle

Cat E does not own primary data — it exposes Cat D-owned Deliverable + SelfBlog lifecycle transitions via 4 tool surfaces.

### 8.1 Ownership matrix

| Data | Read Owner | Write Owner (creation) | Write Owner (transition) | Cat E Role |
|------|------------|-----------------------|--------------------------|-----------|
| Deliverable base | Cat D + Cat E | Cat D factory + Cat E create | Cat E set_status/update/append | R+W consumer |
| SelfBlog | Cat D | Cat A (pipeline runner) + Cat E create | Cat B/C/E (approve/publish) | R+W consumer |
| DeliverableEvent | Cat D | Cat E (3 actions) + Cat D signals | — (append-only) | Partial writer |
| SelfBlog.publish_ready | Cat C | Cat C (`publish_gate.apply_to_blog`) | Cat A fast-path (S1008) | Read-only consumer |
| SelfBlog.status | Cat C + Cat E | Cat A pipeline | Cat E (all 3 paths: PA + REST + beat) | Primary writer at transition |
| ContentEngagement | Cat B (S1602) | Cat B/C/E `_record_content_feedback` | (append-only) | Writer via shared helper |
| ToolCallRecord | PA infra | PA infra (auto per call) | (append-only) | Passive consumer |

### 8.2 Lifecycle mutation matrix (SelfBlog.status)

| Transition | Cat E Path | Cat E-side Audit | Notes |
|------------|-----------|------------------|-------|
| draft → approved | REST approve endpoint | logger.info only | No DeliverableEvent (SelfBlog not Deliverable-backed) |
| approved → published | REST publish (force=false) | logger.info only | PublishGate gate enforced |
| draft → published (force=true) | REST publish (force=true) | logger.info only | **Skips PublishGate + approve step** |
| approved → published (auto) | auto_publish beat | logger.info only | **Contested cadence — see T.15.E4** |
| — → retracted | **DOES NOT EXIST** | — | S1604 T.15.C1 CRITICAL structural gap; Cat E confirms no tool action + no REST endpoint + no beat |

### 8.3 Lifecycle mutation matrix (Deliverable.status)

| Transition | Cat E Path | Cat E-side Audit | Notes |
|------------|-----------|------------------|-------|
| — → completed (create) | deliverable_tool create | Factory signal (Cat D) | Hardcodes 'completed' regardless of caller intent |
| completed → ready (set_status) | deliverable_tool set_status | DeliverableEvent `status_transition` | `reason` required |
| ready → completed (set_status) | deliverable_tool set_status | DeliverableEvent `status_transition` | `reason` optional |
| any → any (update action) | deliverable_tool update | **NO AUDIT** | Silent bypass via `save(update_fields=['status'])` at :2216-2221 |
| any → completed (content_complete alias) | content_tool.content_complete | `_record_content_feedback('complete')` | Canonical audited path per memory rule |

**Whitelist gap:** update action can silently move status through any pair of values (not whitelisted to completed↔ready like set_status). This is DESIGN at HEAD per S1248 P2b but represents an unshaped audit surface. Cat E flags as **T.15.E5 MEDIUM.**

---

## 9. Integrations With Other Domains

Cat E integrates inbound with Content domain (Cat A/B/C/D outputs) and outbound with adjacent domains (PA infra, Frontend, Workspace, Initiative, Newsletter). Cat E does not integrate outbound with external systems (no SendGrid/mailgun/Discord/etc. calls from Cat E code).

### 9.1 Inbound integrations (Cat E consumes)

| Source | Integration | File:Line | Direction | Health |
|--------|------------|-----------|-----------|--------|
| Cat A S1601 | SelfBlog created by pipeline runner | `content_deliberation_runner.py:401` | Cat E reads via blog_tool | WORKING |
| Cat B S1602 | DecisionEnforcer PUBLISH verdict + _record_content_feedback | `td_handlers_content.py:1337-1345` | Cat E writes ContentEngagement | WORKING |
| Cat C S1604 | PublishGate `publish_ready` field | `td_handlers_content.py:1318` filter | Cat E enforces (blog_tool + REST) | WORKING |
| Cat D S1603 | Deliverable base + SelfBlog variant | (multiple sites) | Cat E R/W | WORKING |
| PA infra | AssistantProfile.get_allowed_tools | `tool_dispatcher.py:687-720` | Cat E consumes for auth | WORKING |
| PA infra | ToolCallRecord persistence | `models_tool_calls.py:19` | Cat E passive | WORKING |

### 9.2 Outbound integrations (Cat E emits)

| Target | Integration | File:Line | Direction | Health |
|--------|------------|-----------|-----------|--------|
| Cat D | DeliverableEvent writes | `td_handlers_agents.py:1868/1944/2938` | Cat E writes | WORKING (partial coverage) |
| Cat D | Deliverable creation via factory | `td_handlers_agents.py:2050` | Cat E → factory | WORKING |
| Cat B | ContentEngagement via _record_content_feedback | `td_handlers_content.py:1337` | Cat E writes | WORKING |
| Frontend | REST endpoint response envelopes | `views_research_demo.py:922/983` | Cat E → frontend | WORKING (ambiguous auth) |
| Initiative | link_initiative/unlink_initiative FK writes | `td_handlers_content.py:139/152` | Cat E → Initiative model | WORKING |

### 9.3 Missing integrations (Cat E gap)

| Target | Missing Integration | Owner | Impact |
|--------|--------------------|-------|--------|
| Audit domain | ForcedPublishEvent write on force=true | Cat E T1 | T.15.E3 admin visibility gap |
| Audit domain | AutoPublishEvent write on beat firing | Cat E T1 | T.15.E4 beat firing invisibility |
| Audit domain | RestPublishEvent for REST endpoint calls | Cat E T2 | ToolCallRecord doesn't cover REST |
| Newsletter subscriber | NewsletterSubscriber query on newsletter_tool | Newsletter domain T1 | Newsletter tool can't scope to subscriber list |
| Content-domain broadcast | Discord broadcast on tool-driven approve/publish | Cat C-owned (deferred) | Post-publish broadcast is Cat C boundary |

### 9.4 Cross-arc handoffs owed to Cat E (RECEIVED)

- **From Cat A S1601 (UNK-1):** Document workspace FK RAG-SCOPE cross-tenant risk. Cat E consumes → T.15.E1 (deliverable_tool silent-degrade).
- **From Cat C S1604 (T.15.C6):** force=true audit trail. Cat E consumes → T.15.E3 escalation from admin-only to any-user.
- **From Cat C S1604 (D.14.C5):** auto_publish beat audit trail. Cat E consumes → T.15.E4 escalation to beat schedule gap.
- **From Cat C S1604 (T.15.C14):** frontend auth contract implicit. Cat E confirms + owns → T.15.E2 CRITICAL.

### 9.5 Cross-arc handoffs Cat E emits (TO Cat F + xx99)

- **To Cat F S1606:** D65e 7-axis evidence for cross-domain lens; tool-surface unification posture axes.
- **To xx99 S1699:** T1 R.CONTENT.RIGBY-TOOL-SURFACE-UNIFICATION + T1 R.CONTENT.FORCE-BYPASS-AUTH-BOUNDARY + T1 R.CONTENT.AUTO-PUBLISH-BEAT-SCHEDULE.

---

## 10. Event Flows

Cat E is EVENT-THIN. Three event surfaces exist; five are missing.

### 10.1 Existing event writers (Cat E-adjacent)

| Event Model | Written By Cat E? | Trigger | File:Line |
|-------------|------------------|---------|-----------|
| DeliverableEvent (`synthesis_viewed`) | YES | detail action | `td_handlers_agents.py:1868` |
| DeliverableEvent (`deliverable_saved`) | YES | save action | `td_handlers_agents.py:1944` |
| DeliverableEvent (`status_transition`) | YES | set_status action | `td_handlers_agents.py:2938` |
| ToolCallRecord | YES (auto via ToolDispatcher) | Every PA tool call | `models_tool_calls.py:19` |
| ContentEngagement | YES via `_record_content_feedback` | publish/archive/complete via shared helper | (Cat B S1602-owned model) |

### 10.2 Missing event writers (Cat E T1 + T2)

| Missing Event | Should Fire On | Severity | Cat E Recommendation |
|---------------|---------------|----------|---------------------|
| ForcedPublishEvent | REST publish endpoint force=true | HIGH | T1 R.CONTENT.FORCE-PUBLISH-AUDIT-TRAIL (extends S1604 T2) |
| AutoPublishEvent | auto_publish_approved_blogs beat firing | MEDIUM | T2 R.CONTENT.AUTO-PUBLISH-BEAT-AUDIT-TRAIL (S1604-inherited) |
| RestPublishEvent | Every REST approve/publish call | MEDIUM | T2 R.CONTENT.REST-PUBLISH-AUDIT-TRAIL |
| PublishGateEvent | Every gate evaluation | HIGH (Cat C-owned; Cat E flags) | S1604 T2 R.CONTENT.PUBLISHGATE-EVENT-TELEMETRY |
| DeliverableUpdateEvent | Deliverable update action (status changes) | MEDIUM | T2 R.CONTENT.DELIVERABLE-UPDATE-AUDIT |

---

## 11. Existing Documentation

Cat E documentation coverage is LIGHT. No canonical Cat E topic doc exists.

### 11.1 Cat E-adjacent topic docs

- **`docs/topics/personal-assistant.md`** — mentions content_tool at :50-60 as a gateway tool; names deliverable_tool + blog_tool as Session 1077 focused splits. Does NOT enumerate action sets. Does NOT document workspace scoping semantics or memory-rule traps.
- **`docs/topics/content-pipeline.md`** — mentions PublishGate + gates but not Cat E tool surface. Newsletter mentioned only in beat schedule table.
- **`docs/topics/agent-system.md`** — general agent framework docs; does not cover Cat E specifically.
- **`docs/topics/celery-workers.md:163`** — claims `auto_publish_approved_blogs (daily 6AM)` — **drift candidate** flagged in §14.

### 11.2 Cat E-adjacent handoffs

- **SESSION_1077** — no handoff doc found at HEAD (grep `docs/handoffs/SESSION_1077*` returns 0 hits). Split provenance lives only in schema comments.
- **SESSION_1075** — approve/reject aliases; no dedicated handoff doc found at HEAD.
- **SESSION_1227** — DELIVERABLE_TOOL_AUDIT_46_AND_LLM_AUTOFILL_ROOT_CAUSE — comprehensive; covers 4 PRs + LLM autofill class-of-bug + rollback levers.
- **SESSION_1247** — PA_TOOL_GAP_AUDIT_PLUS_2_FINDINGS_FIXED_AND_P2_DEFERRED — Cat E-adjacent.
- **SESSION_1248** — P2A_P2B_SHIPPED_PLUS_LOCAL_PROD_PARITY_THEME_NAMED — create-defaults-to-completed fix.
- **SESSION_1228** — AUTOFILL_SWEEP_PLUS_BEAT_TZ_FIXES — covers bulk_archive + cleanup gate.
- **SESSION_1170** — content_complete action introduction.

### 11.3 Memory rules (Cat E-load-bearing)

- `feedback_deliverable_tool_use_append_for_large_payloads.md` — Session 1176 origin; **UNKNOWN status at HEAD** (no code repro).
- `feedback_deliverable_status_via_content_complete.md` — CONFIRMED at HEAD as design.
- `feedback_deliverable_create_defaults_to_completed.md` — CONFIRMED at HEAD as design.
- `feedback_llm_autofills_boolean_params_with_false.md` — FIXED at 5 sites.
- `feedback_auto_followup_false_suppresses_banner.md` — Cat E-adjacent; PA infra.

### 11.4 Prior audits touching Cat E

- **`docs/audit-2026/04-content-pipeline.md`** — April 2026 audit; touches PublishGate + newsletter beat context. Does not audit Cat E tool surface.
- **S1604 Cat C audit** — repeatedly hands off to Cat E S1605 (5 explicit cross-arc handoffs at §20.4).

### 11.5 Documentation gaps (Cat E T1)

- No canonical Cat E topic doc.
- No S1077 audit doc despite the split being the primary rationale for the 4-tool surface.
- No documented Rigby workspace-scoping expectation (opt-in vs mandatory).
- No documented `force=true` admin-only expectation vs actual any-user reality.
- Beat schedule doc drift on auto_publish_approved_blogs.

---

## 12. Research Coverage

**Verdict: LIGHT.** Cat E is mentioned across S1604 handoffs and S1227/S1247/S1248/S1228 but has no dedicated audit prior to this one. The 4-tool surface has been the subject of tactical fixes (autofill, create defaults, aliases) but not a canonical audit.

**Coverage matrix:**
- ClaimsPack + pipeline — CANONICAL (S1601)
- Reviewers + DecisionEnforcer — CANONICAL (S1602)
- Deliverable base + variants — CANONICAL (S1603)
- PublishGate + rails — CANONICAL (S1604)
- **Rigby PA-tool + approval UX — LIGHT (this audit; first canonical pass)**

---

## 13. Architecture Maturity

**Cat E overall: PARTIAL** per §1.3. Component breakdown:

| Cat E Component | Maturity | Evidence |
|-----------------|----------|----------|
| ToolDispatcher + ToolResult envelope | STABLE | Session-tested infrastructure; ~2500 LOC; multi-purpose |
| AssistantProfile allowlist auth | STABLE | Consistent gate; used across all 152 PA tool handlers |
| ToolCallRecord telemetry | STABLE | Consistent per-call persistence; queryable |
| 4 canonical tool schemas | WORKING | Registered + dispatched + audited by memory rules |
| Session 1077 split shared handlers | WORKING | No dedicated audit doc but 4 sessions of tactical fixes |
| Workspace scoping (deliverable_tool) | PARTIAL | Silent-degrade on AssistantProfile failure |
| REST endpoint auth boundary | EXPERIMENTAL | Zero decorator; implicit trust |
| Frontend approval UX | PARTIAL | 2 surfaces + asymmetric force + no confirmation + no role gate |
| Newsletter tool | EXPERIMENTAL | Dry-run indefinitely parked; no live-send infra |
| auto_publish beat visibility | UNKNOWN | Docs claim schedule; canonical beat_schedule doesn't have it |
| Cat E-side audit trail | PARTIAL | 3 DeliverableEvent triggers + 0 ForcedPublish/AutoPublish/RestPublish events |

---

## 14. Known Drift

Documented claims that diverge from HEAD runtime.

| # | Claim | Source | Reality at HEAD | Verdict |
|---|-------|--------|-----------------|---------|
| D.14.E1 | `auto_publish_approved_blogs` runs daily 6 AM | docs/topics/celery-workers.md:163; content-pipeline.md:176/189; narratives/CONTENT_PIPELINE.md:240; S1604 §7.4; SESSION_1033:86 | `core/celery.py` beat_schedule has 0 matches for the task **+ Rigby SIGN Batch A F1 fold RUNTIME-CONFIRMED via ops_tool.celery_task_history 30d = 0 events + scheduled_tasks_tool = 0 filtered from 92 total_enabled** | **DRIFT CONFIRMED** — 5 docs stale; no PeriodicTask ORM row; task NEVER fires; cross-arc CORRECTION owed to S1604 D.14.C5 |
| D.14.E2 | Newsletter beat is a "2-Friday burn-in" | `celery.py:418-423` comment (S1222 P6) | >4 months elapsed since burn-in comment; no promotion PR | **DRIFT** — burn-in overrun (inherited from S1604 D.14.C2) |
| D.14.E3 | S1075 approve/reject aliases documented | schema comments | No dedicated handoff doc; provenance in code comments only | **LIGHT DRIFT** — documentation gap |
| D.14.E4 | S1077 focused split rationale documented | schema comments at pa_tool_schemas.py:3389/3461 | No handoff doc; rationale in code comments only | **DRIFT** — documentation gap |
| D.14.E5 | `feedback_deliverable_tool_use_append_for_large_payloads.md` describes a live bug | Memory rule | No code path found matching the described silent fallback | **UNKNOWN DRIFT** — memory rule may be stale from S1176 |
| D.14.E6 | Frontend BlogViewerPage is "the" approval UX | Implicit via primary route | ContentStudioTab is the actual workspace-side approval UX + hardcodes different force semantics | **DRIFT** — 2 surfaces coexist with asymmetric behavior |
| D.14.E7 | Session 1077 as "structural separation of concerns" | Implicit narrative | Split is tactical (LLM function-calling clarity), not structural | **DRIFT** — narrative framing off; per schema comments |
| D.14.E8 | Newsletter tool has publish action per schema description | Implicit via `Prepare ... for Substack/Beehiiv` | No publish/send/dispatch handler branch | **DRIFT** — schema description implies more than handler delivers |

---

## 15. Known Technical Debt

Cat E-owned debt matrix. Severity: CRITICAL / HIGH / MEDIUM / LOW.

| # | Finding | Type | Severity | Evidence | Cat E-owned? |
|---|---------|------|----------|----------|--------------|
| **T.15.E1** | **deliverable_tool workspace-scoping silent-degrade on AssistantProfile lookup failure** | boundary_violation | **CRITICAL if AssistantProfile absence/failure is reachable for ordinary users; otherwise HIGH** | `td_handlers_agents.py:1594-1600` — exception handler logs "cross-workspace results" but query proceeds unscoped. **Rigby SIGN Batch B F5 fold (2026-07-02) — severity precision + framing precision: S1601 UNK-1 analog is accurate as PATTERN CLASS (workspace scoping not guaranteed; failure leads to cross-tenant surface), but NOT SAME BUG CLASS. S1601 UNK-1 = "missing workspace FK / RAG-scope unsafe by design"; T.15.E1 = "scoping exists but silently degrades on lookup failure." Same failure outcome (cross-tenant exposure), different trigger mechanics (absence vs fallback). CRITICAL escalation gate: does missing AssistantProfile occur for non-staff users in normal state (new users; migrations; deleted profile rows)? If yes → CRITICAL cross-tenant disclosure pathway. If only rare (transient DB errors, misconfig) → HIGH.** | YES — Cat E-owned |
| **T.15.E2** | **REST approve/publish endpoints have ZERO auth decorator + ZERO in-body role check** | technical_debt (auth) | **CRITICAL if routable to any non-staff session; downgrade only if proven behind staff-only network/auth wall** | `views_research_demo.py:900/942` — only @require_http_methods; grep for `@login_required\|@permission_required\|@user_passes_test\|is_staff` returns 0 hits in these functions. Extends S1604 T.15.C14 MEDIUM to CRITICAL for Cat E surface. **Rigby SIGN Batch A F3 fold (2026-07-02) — severity precision: CRITICAL default posture; downgrade only if runtime probe confirms endpoints are behind auth-enforcing middleware or reverse-proxy IP allowlist. Default Django AuthenticationMiddleware populates `request.user` but does NOT block anonymous; CSRF middleware reduces some vectors but does NOT establish authorization.** | YES — Cat E-owned |
| **T.15.E3** | **ContentStudioTab hardcodes force=true bypass with ZERO role gate + ZERO confirmation — bypass affordance + authorization gap** | technical_debt (frontend + authorization) | **HIGH** | `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx:2215` — `blogsApi.publish(blog.id, true)` in mutation; no admin conditional render; contrasts BlogViewerPage:396 `force=false`. **Rigby SIGN Batch A F4 fold (2026-07-02) — delta precision from S1604 T.15.C6: S1604 T.15.C6 was primarily "bypass observability/audit gap"; Cat E T.15.E3 is "bypass affordance + authorization gap" — E3 widens actor scope from "someone who knows to use force" (admin path) into "any authenticated workspace user who can click Publish in ContentStudioTab." E3 escalates by expanding who can trigger the bypass, not just who can see it later.** | YES — Cat E-owned |
| **T.15.E4** | **auto_publish_approved_blogs beat schedule MISSING from core/celery.py** | missing_connection | **HIGH** | `core/tasks.py:8056` task defined; `core/settings.py:1394` queue-routed; ZERO matches in `core/celery.py` beat_schedule. Contested by 5 doc claims of "daily 6 AM." Cross-arc with Cat C S1604 D.14.C5 (audit-trail gap moot if beat doesn't fire). | YES — Cat E-owned (Rigby runtime probe owed) |
| **T.15.E5** | **deliverable_tool update action status changes bypass DeliverableEvent audit — audit-invisible dual writer (policy bypass)** | audit-invisible dual writer (policy bypass) | **HIGH** | `td_handlers_agents.py:2216-2221` — update saves `update_fields=['status']` without writing DeliverableEvent. Only set_status writes audit trail with whitelist + reason. **Rigby SIGN Batch B F6 fold (2026-07-02) — severity upgrade MEDIUM → HIGH + label precision: memory rule feedback_deliverable_status_via_content_complete.md is GUIDANCE not HARD GATE; system has (a) two writers to same field with different policy semantics (whitelist+reason vs arbitrary), (b) audit-invisible path usable accidentally/intentionally by agents+operators, (c) shadow channel for status changes breaks status-based reports meaning. This is governance boundary violation (§16.3), not MEDIUM UX/doc debt — HIGH because undermines auditability + makes post-incident reconstruction unreliable.** | YES — Cat E-owned |
| **T.15.E6** | **Cat E has ZERO ForcedPublishEvent + ZERO RestPublishEvent + ZERO PublishGateEvent + ZERO AutoPublishEvent — no event/audit model layer for publishing decisions** | audit_trail_gap (systemic) | **HIGH** | grep across `*.py` returns 0 matches for all 4 model class definitions. Cat E flags 4-model event-audit gap as unified debt (single T-item covers). **Rigby SIGN Batch B F7 fold (2026-07-02) — composite HIGH kept + anti-dup cross-link: S1604 T2 identified publish-rail audit trail REQUIREMENTS (force-publish + auto-publish trails). Cat E T.15.E6 establishes tooling/UX surfaces that actually invoke publish (PA tool + REST + frontend) and OWNS the observability primitives gap as implementation-level deficiency. Ownership shift matters: Cat E recommendation becomes "build unified audit/event instrumentation layer covering PA + REST + frontend" NOT just "PublishGate should log something." T.15.E6 consolidates S1604 trail requirements at the tool-surface layer.** | YES — Cat E-owned (composite; not duplicate of S1604 T2) |
| **T.15.E7** | **ToolCallRecord does NOT record direct REST endpoint calls** | audit_trail_gap | **MEDIUM** | ToolCallRecord captures ToolDispatcher.execute() calls; REST endpoints bypass dispatcher entirely. `views_research_demo.py:900/942` produce zero rows. | YES — Cat E-owned |
| **T.15.E8** | **Newsletter tool schema advertises "Prepare ... for Substack/Beehiiv" but handler is content-generation only** | boundary_violation (advertising) | **MEDIUM** | `pa_tool_schemas.py:3515-3521` implies delivery; `td_handlers_newsletter.py:25-44` has 7 non-delivery action branches; 0 sendgrid/mailgun/postmark hits across newsletter path. Extends S1604 T.15.C2 CRITICAL to Cat E advertising side. **Rigby SIGN Batch C F8 fold (2026-07-02) — MEDIUM kept + explicit cross-link: T.15.E8 = advertising/contract boundary violation (schema over-promises); CRITICAL upstream belongs to S1604 T.15.C2 (live-send infrastructure missing) as capability gap. Re-rating E8 HIGH conflates "tool copy misleading" with "infra missing." Suggested micro-edit: rephrase schema description as "prepare publish-ready markdown/HTML and checklist for manual posting to Substack/Beehiiv" (explicitly non-delivery). Closes E8 without touching E-side live-send infra which is C2 CRITICAL for xx99 posture.** | YES — Cat E-owned |
| **T.15.E9** | **canPublish semantics inconsistent between frontend surfaces — potential intent leak / policy bypass signal** | inconsistency + authorization surrogate | **HIGH (if ContentStudioTab is accessible to non-admin users; MEDIUM if staff-only)** | ContentStudioTab:2238 allows `draft` OR `approved`; BlogViewerPage:394 requires `approved`. No single canonical eligibility contract. **Rigby SIGN Batch C F10 fold (2026-07-02) — severity upgrade MEDIUM → HIGH by default. Reasoning: on face "draft OR approved" vs "approved-only" is MEDIUM UX drift, BUT in this audit context it functions as intent leak / policy bypass signal. If ContentStudioTab was intended as admin tooling, allowing draft publish is policy breach aligned with T.15.E3 bypass-by-default posture. Per T.15.E3 evidence, ContentStudioTab has ZERO role gate — HIGH becomes default posture. Severity gate: HIGH when ContentStudioTab accessible to non-admin users; MEDIUM only if staff-only + properly gated (currently NOT).** | YES — Cat E-owned |
| **T.15.E10** | **No canonical Cat E topic doc + no S1077 audit doc** | documentation_debt | **MEDIUM** | grep `docs/handoffs/SESSION_1077*` returns 0 hits; grep `docs/topics/pa-tool-surface*` returns 0 hits. Session 1077 provenance lives only in schema comments. | YES — Cat E-owned |
| **T.15.E11** | **No confirmation dialog on publish (BlogViewerPage or ContentStudioTab)** | ux_debt | **LOW** | `BlogViewerPage.tsx:396` mutation triggers on single click; delete has confirmation at `:140-184` but publish doesn't. | YES — Cat E-owned |
| **T.15.E12** | **No onError handler on approve/publish mutations at BlogViewerPage** | ux_debt | **LOW** | `:81-90` (approve) + `:93-102` (publish) have onSuccess only. Errors bubble to component-level render at `:425-429`. No toast. | YES — Cat E-owned |
| **T.15.E13** | **Memory rule `feedback_deliverable_tool_use_append_for_large_payloads.md` is UNKNOWN state at HEAD** | documentation_debt | **LOW** | No code path repro found; memory rule may be stale from S1176. | YES — Cat E-owned |

---

## 16. Boundary Violations

Cat E cross-boundary touches that require flagging.

### 16.1 Frontend + REST auth boundary asymmetry (T.15.E2 CRITICAL)

Frontend attaches auth via cookies + optional token; backend endpoints have zero auth decorator. If frontend routing were bypassed (e.g., via direct API call from any authenticated session), any user with a valid session token could approve/publish any blog by ID. **CRITICAL boundary violation** — the trust boundary depends entirely on implicit assumptions (frontend routing + Django middleware) that aren't defensive.

### 16.2 ContentStudioTab force=true bypass with no admin gate (T.15.E3 HIGH)

`ContentStudioTab.tsx:2215` invokes the admin-bypass path with no role check. Combined with §16.1, any workspace user can drive draft→published transitions arbitrarily. Boundary violation of the intended admin-only nature of `force=true`.

### 16.3 deliverable_tool update bypasses status-audit whitelist (T.15.E5 MEDIUM)

`set_status` is the canonical audited status writer with whitelisted transitions (completed↔ready + reason field). `update` action accepts arbitrary status changes without writing DeliverableEvent. Two writers to the same field with different audit + policy semantics is a boundary violation of the "one canonical writer" principle.

### 16.4 REST endpoint bypasses PA-tool ToolCallRecord audit (T.15.E7 MEDIUM)

Cat E has two dispatch paths for the same underlying state transition (SelfBlog draft→published). PA path via ToolDispatcher writes ToolCallRecord. REST path via views_research_demo does not. Boundary violation: same effect, different audit surface.

### 16.5 Newsletter tool advertising boundary (T.15.E8 MEDIUM)

Schema description at `pa_tool_schemas.py:3515-3521` mentions "publish-ready markdown/HTML" and "Substack/Beehiiv" — implying delivery infrastructure. Handler at `td_handlers_newsletter.py:25-44` provides 7 non-delivery actions. **Schema-vs-handler advertising boundary violation.**

---

## 17. Duplicate or Overlapping Systems

### 17.1 Four tools sharing two handler modules

The Session 1077 split created 4 schemas (content_tool + deliverable_tool + blog_tool + newsletter_tool) but only 2 handler modules (`td_handlers_content.py` + `td_handlers_newsletter.py`). blog_tool + content_tool review-side both dispatch to `_handle_content_review`. This is DESIGN per S1077 comments (LLM function-calling clarity), not drift. **Not a duplicate — a documented layered pattern.**

### 17.2 Two frontend approval UX surfaces (T.15.E9)

BlogViewerPage + ContentStudioTab both call the same 2 REST endpoints with different force semantics + different canPublish rules. **Genuine duplicate with drift** — needs canonicalization.

### 17.3 Two writers to SelfBlog.status='published'

- PA path: `td_handlers_content.py:1334` via `_handle_blog_query`
- REST path: `views_research_demo.py:979` via `publish_self_blog_api`
- Beat path: `core/tasks.py:8074` via `auto_publish_approved_blogs`

**Three canonical writers.** All operate on the same field. Two have PublishGate enforcement (PA + REST); one has publish_ready pre-filter (beat). No shared helper. **Boundary risk if semantics diverge between paths.** Not currently a duplicate — a triple canonical writer pattern that requires ongoing consistency discipline.

### 17.4 Two audit writers on Deliverable.status transitions

- `set_status` — writes DeliverableEvent
- `update` — does NOT write DeliverableEvent

**Duplicate + missing** — the audit boundary is not consistent. §16.3 boundary violation.

### 17.5 D65e-E1 candidate resolution paths for tool-surface unification (xx99 consumption)

Per playbook §14.5 no-implementation rule, Cat E does not select. Cat E records 4 candidate resolution paths for xx99 D65e-E1 consumption:

**Candidate A — Preserve 4-tool split; document as canonical.** Cost: LOW. Benefit: minimal disruption; documents S1077 decision; enables Cat E topic doc. Risk: LOW (does not change runtime); tool-surface remains as-is.

**Candidate B — Consolidate to unified content_tool; deprecate focused splits.** Cost: HIGH (breaks LLM function-calling clarity per S1077 rationale). Benefit: single canonical schema; simpler documentation. Risk: HIGH (may regress Rigby's tool-selection reliability).

**Candidate C — Preserve 4-tool split + add shared audit + auth + workspace layer.** Cost: MEDIUM (build shared enforcement layer). Benefit: closes T.15.E1/T.15.E5/T.15.E7 with one investment. Risk: LOW (layer wraps existing dispatch).

**Candidate D — Preserve 4-tool split + retire content_tool umbrella (leave only focused).** Cost: MEDIUM (deprecation migration). Benefit: eliminates schema overlap between content_tool + focused splits; forces canonical usage. Risk: MEDIUM (may leave gap for content-generation actions currently exposed via content_tool.generate_blog / .generate_newsletter). **Rigby SIGN Batch C F9 fold (2026-07-02) — Candidate D SHOULD NOT SURVIVE to xx99 D65e evidence brief. Rationale: Candidate D increases fragmentation + removes the only "unified" conceptual surface WITHOUT first establishing a replacement enforcement layer. It's a de-risking regression — you'd be hardening by deleting a unifying abstraction while the underlying enforcement drift remains.**

**xx99 D65e consumption:** xx99 selects the posture; Cat E does not. **Rigby SIGN Batch C F9 fold (2026-07-02) — xx99 anchor sentence LOCKED-IN for D65e evidence brief: *"Preserve the 4-tool interface, but centralize enforcement (auth/audit/scope/gates) so the split can't produce divergent behavior."* This is Candidate C in one sentence; Cat E records as the pre-xx99 lean anchor; Chris ratifies at xx99 close.**

---

## 18. Ownership Gaps

| Component | Current Owner | Should Be | Gap |
|-----------|--------------|-----------|-----|
| REST publish endpoint auth boundary | UNOWNED (implicit trust) | Cat E + Auth domain | T.15.E2 CRITICAL |
| ContentStudioTab force=true governance | UNOWNED | Cat E + Frontend | T.15.E3 HIGH |
| auto_publish beat cadence + schedule | Cat C (S1604 F6) + Cat E (visibility) | Beat governance domain | T.15.E4 HIGH |
| ForcedPublishEvent / RestPublishEvent | UNOWNED | Cat E T1 | T.15.E6 HIGH |
| Cat E-side documentation | UNOWNED (light coverage across 6 handoffs) | Cat E | T.15.E10 MEDIUM |
| Rigby workspace-scoping expectation | UNOWNED | Cat E + PA infra | T.15.E1 HIGH |
| Newsletter live-send infrastructure | UNOWNED | Newsletter domain (cross-arc with Cat C) | T.15.E8 + T.15.C2 CRITICAL |

---

## 19. Recommended Future Research

**T1 (must complete before xx99):**

- **T1 R.CONTENT.RIGBY-TOOL-SURFACE-UNIFICATION** (Cat E-owned NEW) — D65e-E1 posture decision: preserve 4-tool split (Candidate A/C/D) vs consolidate (Candidate B). Cat E contributes 4-candidate resolution framework at §17.5 for xx99 D65e consumption. **Uncertainty: MED; Risk: LOW; Unblocks: canonical Cat E topic doc; ends decade of drift on the split.**

- **T1 R.CONTENT.FORCE-BYPASS-AUTH-BOUNDARY** (Cat E-owned NEW) — T.15.E2 CRITICAL + T.15.E3 HIGH. Extends S1604 T.15.C6 + T.15.C14. Decisions owed: (a) where is the role gate for approve/publish (frontend? middleware? in-body decorator?); (b) is `force=true` admin-only, and if yes how enforced; (c) should ContentStudioTab hardcode `force=true` at all or expose a toggle. **Uncertainty: MED; Risk: HIGH; Unblocks: workspace multi-tenant safety; end of implicit-auth trust.**

- **T1 R.CONTENT.AUTO-PUBLISH-BEAT-SCHEDULE** (Cat E-owned NEW) — T.15.E4 HIGH. Rigby runtime probe of `ops_tool.celery_task_history` on `auto_publish_approved_blogs` over last 30d + `PeriodicTask.objects.filter(task='core.tasks.auto_publish_approved_blogs')` ORM probe. Decisions owed: (a) does the beat fire at all; (b) if yes, at what cadence; (c) if not, docs are stale (remove daily-6-AM claim from 5 docs) or beat should be added to canonical schedule. **Uncertainty: HIGH pre-probe; Risk: MED-HIGH; Unblocks: S1604 D.14.C5 audit-trail conclusion validity.**

- **T1 R.CONTENT.DELIVERABLE-WORKSPACE-SILENT-DEGRADE** (Cat E-owned NEW) — T.15.E1 HIGH. Decisions owed: (a) is silent-degrade to unscoped acceptable; (b) if not, should exception raise or default to empty; (c) is Rigby workspace-scoping expectation opt-in or mandatory. **Uncertainty: LOW; Risk: HIGH; Unblocks: S1601 UNK-1 partial resolution.**

**T2 (post-xx99):**

- **T2 R.CONTENT.CAT-E-TOPIC-DOC** — write canonical `docs/topics/pa-tool-surface.md` covering 4-tool split rationale + shared handler dispatch + memory-rule matrix + workspace scoping expectation + force bypass admin contract. Closes T.15.E10.

- **T2 R.CONTENT.FORCE-PUBLISH-AUDIT-TRAIL** — persist ForcedPublishEvent on every `force=true` REST invocation (per S1604 T2 R.CONTENT.FORCE-PUBLISH-AUDIT-TRAIL; Cat E confirms + endorses). Extends to record source (frontend surface) + user_id + gate_state at time of bypass.

- **T2 R.CONTENT.REST-PUBLISH-AUDIT-TRAIL** — persist RestPublishEvent on every REST publish call (both force + non-force). Closes T.15.E7 gap between PA + REST dispatch audit.

- **T2 R.CONTENT.DELIVERABLE-UPDATE-AUDIT** — either whitelist update-action status transitions like set_status OR route all status changes through set_status. Closes T.15.E5 boundary violation.

- **T2 R.CONTENT.CONFIRM-PUBLISH-DIALOG** — add publish confirmation dialog matching delete affordance. Closes T.15.E11.

- **T2 R.CONTENT.CANPUBLISH-UNIFICATION** — canonicalize canPublish eligibility rule across BlogViewerPage + ContentStudioTab. Closes T.15.E9.

- **T2 R.CONTENT.APPEND-LARGE-PAYLOAD-VERIFY** — write repro test for `feedback_deliverable_tool_use_append_for_large_payloads.md` memory rule; retire if stale. Closes T.15.E13.

- **T2 R.CONTENT.NEWSLETTER-SCHEMA-DESCRIPTION-TIGHTEN** — reword newsletter_tool schema description to match content-generation-only reality; closes T.15.E8 boundary violation without touching live-send infrastructure (which is T.15.C2 CRITICAL for xx99 posture).

---

## 20. Appendix

### 20.1 Files inspected

- `core/services/pa_tool_schemas.py` (excerpts around :3288, :3392, :3464, :3501)
- `core/services/tool_dispatcher.py` (registration at :476/479/490/521; execute at :584; auth at :687-720; ToolResult at :163-174)
- `core/services/td_handlers_content.py` (`_handle_deliverable_direct` at :84; `_handle_blog_direct` at :162; `_handle_content_review` at :235; `_handle_blog_query` publish branch at :1312-1353; `_handle_content` at :4294-4495)
- `core/services/td_handlers_newsletter.py` (`_handle_newsletter` at :25-44; 7 action branches)
- `core/services/td_handlers_agents.py` (`_handle_deliverables` at :1530; workspace scoping at :1580-1624; action branches at :1824-2969)
- `core/services/unified_pa_entrypoint.py` (`_run_agentic_loop` at :1371; PA_USE_FUNCTION_CALLING gate at :684)
- `core/views_research_demo.py` (`approve_self_blog_api` at :900-939; `publish_self_blog_api` at :942-1000)
- `core/urls.py` (routes at :3223 approve + :3224 publish)
- `core/tasks.py` (`auto_publish_approved_blogs` at :8056-8079)
- `core/celery.py` (newsletter beat at :433-438; auto_publish absent)
- `core/settings.py` (queue routing at :1394)
- `core/models_deliverables.py` (Deliverable base at :84; DeliverableEvent at :561-614)
- `core/models_unified_system.py` (SelfBlog schema at :20611-20770)
- `core/models_newsletter.py` (NewsletterSubscriber at :8-31)
- `core/models_tool_calls.py` (ToolCallRecord at :19-131)
- `frontend/src/pages/BlogViewerPage.tsx` (mutations at :81/:93; buttons at :381/:396)
- `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx` (mutations at :2200/:2215; canPublish at :2238)
- `frontend/src/lib/api.ts` (blogsApi.approve at :3931; blogsApi.publish at :3936)

### 20.2 Docs inspected

- `docs/research/domains/content/1600_content_domain_scoping.md` (§3 E scope + F8 fold + §5 D66 P5 slot + §12 F.iii)
- `docs/research/domains/content/1601-1604_content_*.md` (sibling audits)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 template + §13 Explore sweep + §14 evidence rules + §15 Rigby SIGN)
- `docs/topics/personal-assistant.md`, `docs/topics/content-pipeline.md`, `docs/topics/celery-workers.md`
- `docs/narratives/CONTENT_PIPELINE.md`
- `docs/handoffs/SESSION_1077*` (0 hits — provenance gap)
- `docs/handoffs/SESSION_1227*`, `SESSION_1247*`, `SESSION_1248*`, `SESSION_1228*`, `SESSION_1170*` (Cat E-adjacent)
- Rigby memory rules relevant to Cat E (4 rules)

### 20.3 Grep patterns used (parent-Claude verifier-loop)

- `self\.register\("(content_tool|blog_tool|newsletter_tool|deliverable_tool)"` — 4 hits ✓
- `class (ForcedPublishEvent|AutoPublishEvent|PublishGateEvent|PublishEvent|AuditEvent)\b` — 0 hits ✓ (all absent)
- `auto_publish_approved_blogs|auto-publish-approved-blogs` in `core/celery.py` — 0 hits ✓ (beat schedule absent)
- `auto_publish_approved_blogs` across repo — hits in tasks.py:8056 + settings.py:1394 + 5 docs (drift claim confirmed)
- `sendgrid|mailgun|postmark|smtplib|SMTP|send_mail|EmailMessage` in newsletter path — 0 hits ✓
- `blogsApi\.publish\(blog\.id, true\)` in ContentStudioTab — 1 hit at :2215 ✓
- `@login_required|@permission_required|@user_passes_test` in views_research_demo.py — 0 hits ✓ (auth absent)
- `td_handlers_agents.py:1594-1600` unscoped-query warning branch — verified via direct read ✓

### 20.3a First-class anchor (S1604 F10 propagation)

**Cat E anchor:** *"PA-tool + REST + Frontend are 3 parallel dispatch surfaces to the same content mutations. Only PA-tool has dispatcher-level auth + workspace scoping + ToolCallRecord audit. REST + Frontend rely on implicit-session trust. Cat E fixes require closing this asymmetry via a shared auth+audit+scope layer OR explicit endpoint-level decorators + PublishEvent persistence."*

### 20.4 Cross-arc handoffs

**Received by Cat E S1605 (this audit):**
- Cat A S1601 UNK-1 → T.15.E1
- Cat C S1604 T.15.C6 → T.15.E3 escalation
- Cat C S1604 D.14.C5 → T.15.E4 escalation
- Cat C S1604 T.15.C14 → T.15.E2 CRITICAL
- Cat D S1603 canonical Deliverable base → confirmed clean boundary
- S1402 F.B1 → confirmed 2-of-2 pattern class with Newsletter (F8-CRITICAL)

**Emitted by Cat E S1605 (this audit) to Cat F + xx99:**
- To Cat F S1606: D65e 7-axis evidence for cross-domain lens
- To xx99 S1699: T1 R.CONTENT.RIGBY-TOOL-SURFACE-UNIFICATION + T1 R.CONTENT.FORCE-BYPASS-AUTH-BOUNDARY + T1 R.CONTENT.AUTO-PUBLISH-BEAT-SCHEDULE + T1 R.CONTENT.DELIVERABLE-WORKSPACE-SILENT-DEGRADE

### 20.5 Rigby SIGN fold notes

**SIGN Cycle 1 — 2026-07-02** on fresh isolation pin `pa-b1b26f4f35474df8` (Rigby-side create_fresh). 3-batch SIGN pattern per memory rule `feedback_rigby_sign_worker_instability_recovery.md` — Batch A (4 headline pressure-tests) + Batch B (3 mid-tier findings) + Batch C (3 remaining findings + final consolidated verdict). Rigby confidence: **Batch A 0.84 HIGH; Batch B 0.80 HIGH; Batch C 0.82 HIGH; Final consolidated 0.83 HIGH.**

**SIGN outcome:** SIGN-with-edits at High confidence overall → **SIGN-clean-post-folds at High confidence** (F1-F10 folds landed pre-commit).

**Riskiest finding across A/B/C batches** (Rigby final consolidated): T.15.E2 REST endpoints ZERO auth decorator + ZERO in-body role check. Close second: T.15.E3 ContentStudioTab hardcodes force=true with ZERO role gate + ZERO confirmation.

**Most important future research** (Rigby final consolidated):
1. Prove/falsify external auth wall for `/api/v1/research/self-blog/*` (proxy rules, middleware, staff-only routing). If none, treat as open CRITICAL security bug.
2. Confirm role model for ContentStudioTab (admin-only vs any workspace member) and whether it is the "primary" publish surface.
3. Quantify reachability of T.15.E1 scoping-degrade path (AssistantProfile absence/failure incidence) — can a normal user hit it?
4. Inventory "dual writers" for status and publish actions (T.15.E5 class) — every path that mutates `status` or publish without producing DeliverableEvent / publish event.

**F1-F10 folds landed pre-commit:**

- **F1 — T.15.E4 auto_publish_approved_blogs beat runtime-verified ABSENT** (Batch A A4). Rigby ran `ops_tool.celery_task_history` filter=auto_publish_approved_blogs 30d = **0 events** + `scheduled_tasks_tool` filter=auto_publish_approved_blogs = **0 tasks (0 filtered from 92 total_enabled)**. Beat CONFIRMED ABSENT at HEAD; no PeriodicTask ORM row; task NEVER FIRES. All 5 doc claims of "daily 6 AM" are DRIFT-CONFIRMED-STALE. Cross-arc CORRECTION owed to S1604 D.14.C5 (audit-trail gap MOOT because event never fires). Landed in §1.1 headline + §14 D.14.E1 verdict.

- **F2 — D65e phrasing sentence** (Batch A A1). xx99-consumption phrase locked: "One dispatcher, four tool contracts, shared handler core." Landed in §1.

- **F3 — T.15.E2 severity precision** (Batch A A2). Rephrased as "CRITICAL if routable to any non-staff session; downgrade only if proven behind staff-only network/auth wall." Default Django AuthenticationMiddleware populates `request.user` but does NOT block anonymous; CSRF middleware reduces some vectors but does NOT establish authorization. Landed in §15 T.15.E2 evidence.

- **F4 — T.15.E3 delta precision** (Batch A A3). Explicit fold: S1604 T.15.C6 was primarily "bypass observability/audit gap"; Cat E T.15.E3 is "bypass affordance + authorization gap" — E3 widens actor scope from "someone who knows to use force" (admin path) into "any authenticated workspace user who can click Publish in ContentStudioTab." Landed in §15 T.15.E3 evidence.

- **F5 — T.15.E1 severity precision + framing precision** (Batch B B1). Analog framing: S1601 UNK-1 is PATTERN CLASS analog (workspace scoping not guaranteed → cross-tenant surface) but NOT SAME BUG CLASS (S1601 = "missing FK by design"; E1 = "scoping exists but silently degrades"). Severity gate: CRITICAL if AssistantProfile absence reachable for ordinary users; HIGH otherwise. Landed in §15 T.15.E1 evidence.

- **F6 — T.15.E5 severity upgrade MEDIUM → HIGH + label precision** (Batch B B2). Label changed from "audit_trail_gap" to "audit-invisible dual writer (policy bypass)." Memory rule feedback_deliverable_status_via_content_complete.md is GUIDANCE not HARD GATE. Two writers to same field with different policy semantics + audit-invisible path + shadow channel = governance boundary violation, not MEDIUM UX/doc debt. Landed in §15 T.15.E5 evidence.

- **F7 — T.15.E6 composite kept HIGH + anti-dup cross-link to S1604 T2** (Batch B B3). Anti-dup framing: S1604 T2 identified publish-rail audit trail REQUIREMENTS; Cat E T.15.E6 establishes tooling/UX surfaces that actually invoke publish AND owns observability primitives gap as implementation-level deficiency. Ownership shift matters: Cat E recommendation becomes "build unified audit/event instrumentation layer covering PA + REST + frontend." Landed in §15 T.15.E6 evidence.

- **F8 — T.15.E8 MEDIUM kept + explicit cross-link + micro-edit** (Batch C C1). E8 = advertising/contract boundary violation (schema over-promises); CRITICAL upstream belongs to S1604 T.15.C2 (live-send infrastructure missing) as capability gap. Suggested schema micro-edit: rephrase description as "prepare publish-ready markdown/HTML and checklist for manual posting to Substack/Beehiiv" (explicitly non-delivery). Closes E8 without touching Cat E-side live-send infra which is C2 CRITICAL for xx99 posture. Landed in §15 T.15.E8 evidence.

- **F9 — §17.5 Candidate D "should not survive" + xx99 anchor sentence LOCKED-IN** (Batch C C2). Candidate D (preserve+retire content_tool umbrella) SHOULD NOT SURVIVE to xx99 D65e evidence brief — it increases fragmentation + removes only unified conceptual surface without replacement enforcement layer (de-risking regression). xx99 anchor sentence LOCKED: *"Preserve the 4-tool interface, but centralize enforcement (auth/audit/scope/gates) so the split can't produce divergent behavior."* This is Candidate C in one sentence; Cat E records as pre-xx99 lean anchor; Chris ratifies at xx99 close. Landed in §17.5.

- **F10 — T.15.E9 severity upgrade MEDIUM → HIGH by default** (Batch C C3). Rationale: on face "draft OR approved" vs "approved-only" is MEDIUM UX drift, but per T.15.E3 evidence ContentStudioTab has ZERO role gate — E9 functions as intent leak / policy bypass signal. Severity gate: HIGH when ContentStudioTab accessible to non-admin users; MEDIUM only if staff-only + properly gated (currently NOT). Landed in §15 T.15.E9 evidence.

**D48 preemptive stability-probe gate 14th arm outcome:** Batches A + B + C all substantive on fresh isolation pin + final consolidated verdict single-message follow-up clean. **NINE-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605 CONFIRMED** — extends 13-arc pattern to 14-arc + S1605 clean. Codification-ready-STRENGTHENED-FURTHER for playbook v3 §15 with 9-consecutive-fully-clean sub-pattern.

**Rigby-side runtime probes executed during SIGN cycle 1 (Batch A A4):**
- `ops_tool.celery_task_history` filter=auto_publish_approved_blogs window=30d → 0 events
- `scheduled_tasks_tool` filter=auto_publish_approved_blogs → 0 tasks (0 filtered from 92 total_enabled)

These probes ADD load-bearing runtime evidence beyond code-layer grep — the audit's HEAD `f5065624` grep of `core/celery.py` returned 0 hits, and Rigby's independent runtime probes confirmed the beat is ABSENT from PeriodicTask ORM + NEVER FIRES. F1 fold captures this evidence chain.

**Fresh isolation pin `pa-b1b26f4f35474df8` retired at S1605 close via `session_tool.retire` (per feedback_session_tool_retire_works.md).**

### 20.6 Unresolved unknowns

- UNK-E1: `auto_publish_approved_blogs` fires at all? Rigby ops_tool runtime probe owed.
- UNK-E2: memory rule `feedback_deliverable_tool_use_append_for_large_payloads.md` — is trap live or stale?
- UNK-E3: does Django middleware inject `request.user` such that unauthenticated POSTs to approve/publish return 401 before hitting endpoint body? Or do they proceed with `AnonymousUser`?
- UNK-E4: are there any content tests covering approve/publish endpoint auth? grep for `test_approve_self_blog_api` + `test_publish_self_blog_api` recommended.
- UNK-E5: PeriodicTask ORM row for `auto_publish_approved_blogs` — exists at Railway? Cannot determine from local codebase.

### 20.7 Verifier-loop provenance

24 pre-Explore + 8 post-Explore load-bearing binary claims grep-verified against HEAD `f5065624`. All Explore-side claims independently verified via direct file:line reads before inclusion. Post-Explore parent-Claude corrections:

- **P0-CORRECTION-1**: E5 initial claim that content_tool might be unregistered → corrected to CONFIRMED-REGISTERED at `tool_dispatcher.py:476` via direct grep. All 4 Cat E tools registered.
- **P0-CORRECTION-2**: E6 UNKNOWN on auto_publish beat schedule → parent-Claude verified as CONFIRMED-ABSENT from `core/celery.py`; escalated to T.15.E4 HIGH new finding beyond E6 report.
- **P0-CORRECTION-3**: E4 finding of ContentStudioTab `force=true` hardcode → parent-Claude verified at HEAD `:2215` via direct grep; escalated to T.15.E3 HIGH new finding.

---

*End of Session 1605 Cat E child audit. Route to Rigby SIGN cycle 1 via fresh isolation pin per playbook §15.*
