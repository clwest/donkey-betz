---
session: 1605
status: closed (Group 1600 Cat E Rigby-Facing PA Tooling + Approval UX child audit LANDED at S1605; playbook §11.2 20-section template + 6-parallel-Explore per §13 + parent-Claude verifier-loop per §14 on 24 pre-Explore + 8 post-Explore + 2 Rigby-runtime-probe load-bearing binary claims all grep-verified against HEAD `f5065624`; D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront at §1.5 + §6.5 + §6.6 per parent D68 F8/F10 folds — **fifth sibling of Group 1600 to propagate the pattern upfront** after S1601 first + S1602 second + S1603 third + S1604 fourth; Rigby SIGN cycle 1 SIGN-with-edits at High confidence (Batch A 0.84 + Batch B 0.80 + Batch C 0.82 + final consolidated 0.83) → **SIGN-clean-post-folds at High confidence** on fresh isolation pin `pa-b1b26f4f35474df8` (retired at S1605 close via `session_tool.retire`); **F1-F10 folds landed pre-commit** including F1 T.15.E4 auto_publish_approved_blogs beat runtime-verified ABSENT + F3 T.15.E2 CRITICAL severity precision + F4 T.15.E3 delta precision from S1604 T.15.C6 + F5 T.15.E1 severity+framing precision + F6 T.15.E5 upgrade MEDIUM → HIGH + F7 T.15.E6 anti-dup cross-link + F9 §17.5 Candidate D SHOULD NOT SURVIVE + xx99 anchor sentence LOCKED + F10 T.15.E9 upgrade MEDIUM → HIGH; **D48 preemptive stability-probe gate 14th-arm outcome — NINE-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605 CONFIRMED**; ARCHITECTURE_INDEX v39 → v40; OPEN_ARCS Group 1600 row S1604 → S1605 advance; `tools/pa_local.sh:128` unchanged — Group 1600 arc pin `pa-f52acf3f8d394faa` retained through S1699 xx99)
date: 2026-07-02
arc: Research Group 1600 (Content / Deliverables / Publishing) — fifth child audit under D66 P5 slot
---

# Session 1605 — Group 1600 Cat E: Rigby-Facing PA Tooling + Operator Approval UX (Child Audit)

## What shipped

- **New audit doc:** `docs/research/domains/content/1605_content_rigby_pa_tooling_approval_ux_audit.md` (952 lines; playbook §11.2 20-section template; F1-F10 folds landed pre-commit).
- **ARCHITECTURE_INDEX:** v39 → v40 with §1.43 S1605 registration + line-6 preamble bump.
- **OPEN_ARCS:** Group 1600 row preamble advance S1604 → S1605.
- **Rigby SIGN cycle 1:** SIGN-with-edits at High confidence (Batch A 0.84 + Batch B 0.80 + Batch C 0.82 + final consolidated 0.83) → **SIGN-clean-post-folds at High confidence** on fresh isolation pin `pa-b1b26f4f35474df8` (retired at close).
- **D48 preemptive stability-probe gate 14th arm:** HELD CLEAN across 3 batches + final-verdict → NINE-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605 CONFIRMED.

## Key findings

- **D65e HEADLINE evidence for xx99 (fourth axis alongside D65a/D65b/D65c):** Parent §5 P5 canonical decision "4 parallel APIs OR 1 unified API?" resolves LAYERED at HEAD — unified at dispatcher layer (`tool_dispatcher.py:584` single async `execute()` + `AssistantProfile.get_allowed_tools()` gate at `:687-720` + `ToolResult` envelope at `:163-174`) + 4 parallel-schema contracts at PA-tool layer (`content_tool` at `:3288` + `deliverable_tool` at `:3392` + `blog_tool` at `:3464` + `newsletter_tool` at `:3501` — all 4 canonically registered at `tool_dispatcher.py:476/:479/:490/:521`) + shared handler code paths at implementation layer (`_handle_content_review` + `_handle_deliverables` + `_handle_blog_query`).

- **NEW CRITICAL T.15.E2:** REST approve/publish endpoints at `views_research_demo.py:900/:942` have ZERO `@login_required` + ZERO `@permission_required` + ZERO in-body `request.user.is_staff` check. Extends S1604 T.15.C14 MEDIUM to CRITICAL for Cat E surface (per F3 severity precision fold: CRITICAL if routable to any non-staff session; downgrade only if proven behind staff-only network/auth wall).

- **NEW HIGH T.15.E3:** `ContentStudioTab.tsx:2215` hardcodes `blogsApi.publish(blog.id, true)` — force=true bypass with ZERO role gate + ZERO confirmation dialog. Contrasts BlogViewerPage.tsx:396 hardcoded `force=false`. Per F4 delta precision fold: T.15.E3 is "bypass affordance + authorization gap" vs S1604 T.15.C6 "bypass observability/audit gap" — E3 widens actor scope from admin-path to any-authenticated-workspace-user.

- **NEW HIGH T.15.E4 runtime-verified via Rigby SIGN Batch A F1 fold:** `auto_publish_approved_blogs` beat CONFIRMED ABSENT — `ops_tool.celery_task_history` filter=auto_publish_approved_blogs 30d = **0 events** + `scheduled_tasks_tool` filter=auto_publish_approved_blogs = **0 tasks (0 filtered from 92 total_enabled)**. Task defined at `core/tasks.py:8056-8079` + queue-routed at `core/settings.py:1394` but **NOT in `core/celery.py` beat_schedule** + **no PeriodicTask ORM row exists**. **5 doc claims of "daily 6 AM"** (`docs/topics/celery-workers.md:163` + `docs/topics/content-pipeline.md:176/189` + `docs/narratives/CONTENT_PIPELINE.md:240` + S1604 §7.4 + `SESSION_1033:86`) are **DRIFT-CONFIRMED-STALE**. **Cross-arc CORRECTION owed to S1604 D.14.C5 audit-trail gap is MOOT because no auto-publish event ever fires.**

- **NEW HIGH T.15.E1:** `deliverable_tool` workspace-scoping silent-degrade at `td_handlers_agents.py:1594-1600` on `AssistantProfile` lookup failure — warning logged but query proceeds unscoped. Per F5 severity+framing fold: confirms S1601 UNK-1 pattern-class analog (workspace scoping not guaranteed → cross-tenant surface) but NOT same-bug-class (S1601 = "missing FK by design"; E1 = "scoping exists but silently degrades on lookup failure"). Severity gate: CRITICAL if AssistantProfile absence reachable for ordinary users; HIGH otherwise.

- **NEW HIGH T.15.E5 (upgraded MEDIUM → HIGH per F6 fold):** `deliverable_tool.update` action status changes bypass `DeliverableEvent` audit — `td_handlers_agents.py:2216-2221` saves `update_fields=['status']` without writing audit event. Only `set_status` writes audit trail with whitelist + reason. Label change: "audit-invisible dual writer (policy bypass)" — governance boundary violation, not MEDIUM UX/doc debt.

- **NEW HIGH T.15.E6 composite (per F7 anti-dup fold):** ZERO `ForcedPublishEvent` + ZERO `AutoPublishEvent` + ZERO `PublishGateEvent` + ZERO `RestPublishEvent` model classes exist at HEAD (grep-verified). Cat E owns observability primitives gap at PA/REST/frontend surface layer — differentiated from S1604 T2 which owns publish-rail audit-trail requirements (Cat E recommendation: build unified audit/event instrumentation layer covering PA + REST + frontend).

- **NEW HIGH T.15.E9 (upgraded MEDIUM → HIGH per F10 fold):** `canPublish` semantics inconsistent — `ContentStudioTab:2238` allows `draft` OR `approved`; `BlogViewerPage:394` requires `approved`. Given T.15.E3 confirmed ContentStudioTab has ZERO role gate, canPublish inconsistency functions as intent leak / policy bypass signal.

- **§17.5 4-candidate resolution framework for xx99 D65e-E1** — Candidate A preserve+document / B consolidate to unified content_tool / C preserve+add shared enforcement layer / D preserve+retire content_tool umbrella. Cat E does NOT select posture per playbook §14.5. Per F9 Rigby fold: **Candidate D SHOULD NOT SURVIVE** to xx99 D65e evidence brief (it increases fragmentation + removes unified conceptual surface without replacement enforcement layer — de-risking regression). **xx99 anchor sentence LOCKED:** *"Preserve the 4-tool interface, but centralize enforcement (auth/audit/scope/gates) so the split can't produce divergent behavior."*

## Rigby SIGN cycle 1 details

- **Fresh isolation pin:** `pa-b1b26f4f35474df8` (Rigby-side `session_tool.create_fresh`; seed: "S1605 Cat E child audit — Rigby PA-tool + Approval UX — SIGN cycle 1").
- **Batching:** 3-batch SIGN pattern per memory rule `feedback_rigby_sign_worker_instability_recovery.md`. Batch A (4 headline pressure-tests: D65e framing + T.15.E2 CRITICAL + T.15.E3 NEW HIGH + T.15.E4 beat schedule) + Batch B (3 mid-tier findings: T.15.E1 + T.15.E5 + T.15.E6) + Batch C (3 remaining + consolidated final verdict: T.15.E8 + §17.5 candidates + T.15.E9).
- **Confidences:** Batch A 0.84 HIGH + Batch B 0.80 HIGH + Batch C 0.82 HIGH + final consolidated 0.83 HIGH.
- **Rigby-side runtime probes during Batch A A4 (F1 fold evidence):** `ops_tool.celery_task_history` + `scheduled_tasks_tool` — both confirm `auto_publish_approved_blogs` ABSENT.
- **10 folds landed pre-commit (F1-F10)** documented in §20.5 of audit doc.
- **Retirement:** `session_tool.retire conversation_id=pa-b1b26f4f35474df8` at close (updated_count 5; retired true).

## Cross-arc handoffs emitted

- **To Cat F S1606:** D65e 7-axis evidence for cross-domain lens (E1 tool-schema unification + E2 tool-registration coverage + E3 handler consolidation + E4 approval-UX contract + E5 audit trail + E6 auth boundary + E7 workspace scoping).
- **To xx99 S1699:** T1 R.CONTENT.RIGBY-TOOL-SURFACE-UNIFICATION + T1 R.CONTENT.FORCE-BYPASS-AUTH-BOUNDARY + T1 R.CONTENT.AUTO-PUBLISH-BEAT-SCHEDULE (cross-arc CORRECTION to S1604) + T1 R.CONTENT.DELIVERABLE-WORKSPACE-SILENT-DEGRADE.
- **Cross-arc CORRECTION owed to S1604 D.14.C5:** auto_publish_approved_blogs beat runtime-verified ABSENT via Rigby probes — S1604 audit-trail gap is MOOT because event never fires. S1604 §7.4 F6 fold body precision should be re-scoped from "in-model save + log-line-only audit trail" to "task defined but beat schedule MISSING + never fires."

## Repo state at close

- **Branch state:** `docs/session-1605-content-cat-e-audit` PR opens to `main` on push.
- **Files touched this session:**
  - `docs/research/domains/content/1605_content_rigby_pa_tooling_approval_ux_audit.md` [new; 952 lines; F1-F10 folds landed]
  - `docs/research/ARCHITECTURE_INDEX.md` [modified — v39 → v40 preamble + §1.43 S1605 registration]
  - `docs/research/OPEN_ARCS.md` [modified — line-6 preamble advance S1604 → S1605]
  - `docs/handoffs/SESSION_1605_CONTENT_CAT_E_AUDIT.md` [new — this file]
  - `00-START-NEXT-SESSION.md` [modified — S1606 Cat F next queued]

## Group 1600 arc state at S1605 close

- **Children completed:** S1601 Cat A + S1602 Cat B + S1603 Cat D + S1604 Cat C + **S1605 Cat E (this session)** = 5-of-6.
- **Children remaining:** S1606 Cat F Cross-Domain Integration Lens + Posture Decision Framing (LAST — consumes P1-P5 evidence).
- **Canonical summary:** S1699 xx99 queued (fourth application of playbook §11.3 §10 meta-methodology template).
- **Arc pin retention:** `pa-f52acf3f8d394faa` retained through P6 Cat F + P7 xx99 per playbook §16 arc-continuity rule.

## D48 stability-probe pattern advancement

- **13-arc pattern at S1604 close:** S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604.
- **14-arc pattern at S1605 close:** above + S1605.
- **Eight-consecutive-fully-clean-arms sub-pattern at S1604 close:** S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604.
- **NINE-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN at S1605 close (this session):** S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605 CONFIRMED.
- **Codification status:** codification-ready-STRENGTHENED-FURTHER for playbook v3 §15 with 9-consecutive-fully-clean sub-pattern (from 8-consecutive at S1604 close).

## Follow-ups + open risks

- **Post-merge 4-step docs cascade + `build_docs_provenance`** owed per memory rule `feedback_docs_cascade_at_every_close.md`.
- **Cross-arc CORRECTION owed:** S1604 §7.4 F6 fold text should be re-scoped from "in-model save + log-line-only audit trail" to "task defined but beat schedule MISSING + never fires." (Deferred to xx99 canonical summary or Cat C follow-on PR.)
- **5 doc PRs owed** to remove "daily 6 AM" claim for `auto_publish_approved_blogs` from: `docs/topics/celery-workers.md:163`, `docs/topics/content-pipeline.md:176/189`, `docs/narratives/CONTENT_PIPELINE.md:240`, S1604 §7.4 body, `SESSION_1033_VALUE_CHAIN_COMPLETION.md:86`. (Deferred to next docs cleanup session.)
- **Rigby most important future research** (final consolidated verdict):
  1. Prove/falsify external auth wall for `/api/v1/research/self-blog/*` (proxy rules, middleware, staff-only routing).
  2. Confirm role model for ContentStudioTab (admin-only vs any workspace member).
  3. Quantify reachability of T.15.E1 scoping-degrade path (AssistantProfile absence incidence).
  4. Inventory "dual writers" for status and publish actions (T.15.E5 class).
- **CLAUDE.md 3-vs-4 employees narrative drift** — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited).
- **Group 1400 + Group 1500 post-arc §7 anchor-updates** still pending (inherited).

## Next session

- **Recommended:** `Continue research group 1606` (S1606 Cat F Cross-Domain Integration Lens + Posture Decision Framing — LAST child under Group 1600).
- **Alternative:** Chris-gated pre-S1606 T1 R.CONTENT.RAG-SCOPE cross-arc verification via Memory arc or Cat E T.15.E1 cross-tenant risk investigation.
