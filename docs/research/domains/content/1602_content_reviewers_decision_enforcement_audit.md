---
title: "Content Cat B — Reviewers + Decision Enforcement (Child Audit)"
status: active
session: 1602
generated: 2026-07-02
domain_slug: content
research_group: 1600
category: child_audit
child_slot: P2
authority: child-audit
head_commit: ed212c51
sibling_arc: 1601 (Content Cat A ClaimsPack + Deliberation Pipeline v2 audit)
parent: docs/research/domains/content/1600_content_domain_scoping.md
related:
  - docs/research/domains/content/1600_content_domain_scoping.md (S1600 parent scoping — §3 B boundary + Q1/Q2 load-bearing questions)
  - docs/research/domains/content/1601_content_claims_pack_deliberation_pipeline_v2_audit.md (S1601 Cat A sibling audit — §14/§15/§20.6 cross-arc handoffs to Cat B)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md (§11.2 20-section child template + §13 six-parallel-Explore + §14 verifier-loop + §15 SIGN policy + §16 commit policy)
  - docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md (structural precedent + D62 4-item mini-schema exemplar)
  - docs/research/domains/sports/1502_sports_signal_aggregation_audit.md (§14.3 SignalCluster pattern_type consumer-side gap precedent)
  - docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md (§14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN precedent + F.B1 delivery ZERO outbound channel precedent)
  - docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md (F.B1 delivery ZERO outbound channel pattern check)
  - docs/patents/DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md (Cat B-primary DecisionEnforcer patent provenance)
  - docs/topics/content-pipeline.md (Session 1147 topic doc — Cat B §3/§4/§5 coverage)
verifier_loop:
  pre_explore: 7 load-bearing claims verified by direct file:line read before Explore fire (see §20.1)
  post_explore: 3 load-bearing binary claims verified by direct grep after Explore return (see §20.4)
  rigby_sign: SIGN-with-edits at High confidence (7 folds F1-F7 landed pre-commit — see §20.5); fresh SIGN isolation pin pa-1c5298d807d7a1d2 retired at S1602 close
delegates_to:
  - S1604 Cat C PublishGate + Publish Rails — inherits Cat B decision → PublishGate hand-off contract
  - S1603 Cat D Deliverable Base — inherits Cat B write to SelfBlog.stats_snapshot['deliberation'] persistence handoff
  - S1605 Cat E Rigby-Facing Content PA Tooling — inherits Cat B ZERO PA-tool coverage on reviewer verdicts + mandate
  - S1606 Cat F Cross-Domain Integration Lens — inherits Cat B ZERO outbound learning-loop / memory / signal-engine / Discord feedback
  - S1699 xx99 — Cat B evidence input to D65a (SelfBlog canonicalization) + D65b (citation-integrity policy) + D65c (lifecycle-transition ownership)
---

# Session 1602 — Group 1600 Cat B: Content Reviewers + Decision Enforcement

> **Scope (parent §3 B).** 3-reviewer panel (`SkepticReviewer` + `FactCheckReviewer` + `DomainPersonaReviewer` conditional) + `run_reviews` dispatch function + `DecisionEnforcerAgent` + synthetic-FAIL failure handling + single rewrite pass. Cat B owns *pre-publish gating: whether the draft passes reviewer verdicts + decision-enforcement contract*. Cat B does NOT own downstream quality thresholds (Cat C, S1604) or Deliverable base object model (Cat D, S1603).

---

## 1. Executive Summary

**Cat B is WORKING but NOT STABLE.** The 3-reviewer panel + DecisionEnforcerAgent + single rewrite pass form the pre-publish gating layer of Content Deliberation Pipeline v2. All three **v2 deliberation deployment paths** (REST `POST /api/v1/research/self-blog/generate-v2/` at `core/views_research_demo.py:1106-1145`, PA tool `blog_tool.generate` at `core/services/td_handlers_content.py:162-182`, Celery task `generate_self_blog_deliberation_task` at `core/tasks.py:5758-5761` → `core/tasks_content.py:2399-2605` instantiates runner at :2540) traverse Cat B's v2 panel. **v1 direct-write via `ContentWriterAgent` at `core/agents/content_writer_agent.py:1376-1377` (guarded by `ENABLE_CONTENT_REVIEW=True` at :62) instantiates v1 `ContentReviewPanel` and does NOT touch Cat B's v2 panel or DecisionEnforcerAgent auto-trigger.** (F3 fold pre-commit — Rigby Batch A/C Q2 tightening.) Verdicts land in `SelfBlog.stats_snapshot['deliberation']` at `core/services/content_deliberation_runner.py:381-389` + Cat B contract lands in `ContractRecord` at `core/conversation_orchestrator.py:1341-1343`. Not STABLE because three HIGH/CRITICAL structural findings surfaced during the audit.

**Two parent §3 B load-bearing questions resolved:**

- **Q1 Reviewer dispatch shape (parent §3 B "Are reviewers pure-function or class-based?"):** Reviewers are **PURE-FUNCTION, MODULE-LEVEL DISPATCH**, not class-based. v2 uses module-level constants `SKEPTIC_SYSTEM` at `content_review_panel_v2.py:88`, `FACTCHECK_SYSTEM` at :107, `DOMAIN_SYSTEM_TEMPLATE` at :124, and a `run_reviews(draft, claims_pack, topic, domain)` dispatch function at :208-256. No `SkepticReviewer` / `FactCheckReviewer` / `DomainPersonaReviewer` classes exist. Design intent per module docstring lines 1-10: prompt-string constants + dispatch function = hot-swap-flexibility avoiding v1 class rewrite. **Owed to xx99 §5 D65-analog evidence plan.**

- **Q2 v1 vs v2 canonicalization posture (parent §6.1 parked issue):** v2 (`content_review_panel_v2.py`, 256 lines, module-level) is **CANONICAL FOR THE DELIBERATION PIPELINE**. `content_deliberation_runner.py:225` imports `from core.services.content_review_panel_v2 import run_reviews, _detect_domain` — v1 is not imported by the pipeline. **BUT v1 (`content_review_panel.py`, 350 lines, class-based `ContentReviewPanel` at :61) is NOT dormant** — grep-confirmed live secondary consumer at `core/agents/content_writer_agent.py:1376-1377` inside `if ENABLE_CONTENT_REVIEW:` guard (flag hardcoded `True` at :62). v1 fires on ContentWriterAgent's direct-write path (bypassing v2 pipeline). **Classification: PARTIALLY-ADOPTED-LIVE-SECONDARY** — analog to S1274 EventBus "partially adopted" pattern but with LIVE (not dormant) secondary consumer. Cat B canonicalization decision (post-arc D65-analog): keep dual-path (v1 for single-blog writes + v2 for deliberation) OR retire v1 by rerouting `ContentWriterAgent._maybe_run_review()` through v2 `run_reviews`. Owed to xx99 §5 D65-analog evidence plan.

**Cat B canonical decision (parent §5 D66 P2 slot):** How do reviewer verdicts + DecisionEnforcer produce PUBLISH/REVISE/KILL? **Answer:** Runtime resolves via two-tier priority at `content_deliberation_runner.py:266-284` — Tier 1 mandate `chosen_path` keyword-match (PUBLISH / KILL / REVISE) from `ExecutionMandate` produced by `DecisionEnforcerAgent` auto-triggered inside `ConversationOrchestrator.generate_conversation(conversation_type='critique')` at `core/conversation_orchestrator.py:1247-1284` (dual-trigger: line 1247 primary when `decision_summary` present + line 1273 fallback when `decision_summary` missing on debate/planning/critique types); Tier 2 fallback on reviewer-verdict aggregate (all-PASS → PUBLISH, any-FAIL → REVISE, default → REVISE); Cat A post-decision downgrade gate at :99-103 flips PUBLISH → REVISE when `claims_count == 0`. Mandate model is `gpt-5.2` at `core/agents/decision_enforcer_agent.py:372` with `max_completion_tokens=2000` at :374; reviewers use `gpt-4.1-mini` at `content_review_panel_v2.py:162` with `temp=0.3, max_tokens=1500`.

**Headline findings ranked for xx99 §5 evidence plan (three-axis D65a/D65b/D65c input):**

1. **HIGH — CONFIRMED (extends S1601 §15.1 UNK-2 to fully resolved):** End-to-end citation integrity across Cat A + Cat B is **LLM-prompt-only**, with ZERO code-side per-claim `[C-xxxxxxxxxx]` regex/typed-constraint verification anywhere. Cat A's `claims_count == 0` gate at `content_deliberation_runner.py:99-103` is a binary presence check, not per-claim. Cat B's FactCheckReviewer prompt at `content_review_panel_v2.py:107-122` says "Verify every claim ID [C-xxxxxxxxxx] in the draft maps to a URL in the claims data" + "Flag any factual assertion without a [C-...] marker as unsourced" — but this executes as LLM inference with no verifier function, no `validate_review_payload` per-claim rule at :27-66, no `_call_llm_reviewer` regex post-check at :143-192. Hallucinated / misattributed citations pass both gates. **Owed to xx99 D65b citation-integrity policy evidence plan (T1 R.CONTENT.CITATION-INTEGRITY).**

2. **HIGH — Silent draft truncation at 8000 chars in v2 reviewers (extends S1601 §15.2 F2 fold silent-partial-source pattern to Cat B).** At `content_review_panel_v2.py:236`, `draft[:8000]` silently slices the user_content prompt. Reviewers PASS/FAIL on partial evidence without truncation visibility, warning log, or `top_issues` entry. `_impl_generate_self_blog_deliberation_task` at `core/tasks_content.py:2399-2605` targets `word_count=1500` per default; 1500 words ≈ 9000-10500 chars including markdown → **majority of production drafts exceed the truncation threshold**. Reviewers evaluate first 80% only. Same "truth/evidence integrity degradation without explicit degraded-status contract" pattern S1601 F2 elevated MEDIUM → HIGH. **Owed to xx99 D65b evidence plan.**

3. **HIGH (latent-landmine) — `queue_agent_task` MISSING from `core/tasks.py` (grep-verified zero definitions).** `DecisionEnforcerAgent.spawn_tasks_from_mandate` at `core/agents/decision_enforcer_agent.py:444-477` imports `from core.tasks import queue_agent_task` at :456 and calls `queue_agent_task.delay(...)` at :460 with LLM-picked `agent_name`. Grep across repo returns four consumers (`decision_enforcer_agent.py:456,460`; `auto_spawner_service.py:321,323`) + one **fallback log line at `core/services/auto_spawner_service.py:337`: `logger.warning("queue_agent_task not available")`**. **F5 fold pre-commit correction (Rigby Batch B/C Q4-#5 grep-verified):** `decision_enforcer_agent.py:455-476` DOES wrap the import + `.delay()` call in a broad `try/except Exception` guard at :474-476 which logs `Failed to spawn tasks: {e}` and returns empty `task_ids`. The failure is **exception-swallowed silently** — no user-visible symptom, no unhandled crash. Combined with (a) no `agent_name` validation against `AgentRouter.AGENT_MAP` (blast-radius: LLM hallucinated agent names) + (b) grep-verified ZERO production callers of `spawn_tasks_from_mandate` (only `enforce_decision_after_synthesis(auto_spawn=True)` at :481 which is not called from runner or orchestrator) → classification is **HIGH latent-landmine, not CRITICAL active bug** (F6 severity fold Rigby Batch B/C Q5). Two candidate posture-decision fixes owed to xx99 D65c lifecycle-transition ownership: (i) define missing `queue_agent_task` in `core/tasks.py` (WORKING → STABLE) + validate `agent_name in AGENT_MAP` OR (ii) retire `spawn_tasks_from_mandate` entirely and route mandate through a Cat E surface (mandate → Rigby's `governance_tool.decision_promote` at `pa_tool_schemas.py:3162-3230`). Adjacent evidence: DecisionEnforcerAgent execution mandates DO get persisted to `ContractRecord.contract_data` regardless of spawn outcome — decision itself is durable; only task-spawning limb is broken. Rigby Batch B/C grep-verified patent operational claim invalidation at `DISCLOSURE_F.md:140` ("creates `queue_agent_task.delay()`").

4. **HIGH — Cat B mandate + reviewer verdicts have ZERO outbound channel to Rigby PA tool surface (extends S1402 F.B1 ZERO-outbound pattern to content Cat B).** Grep-confirmed at `core/services/pa_tool_schemas.py`: `blog_tool.generate` / `content_tool.generate_blog` return only Celery `task_id`; NO PA-tool schema exposes reviewer verdicts, `top_issues`, `required_changes`, or `ExecutionMandate.chosen_path` / `reason` / `decision_owner`. The only readback surface is REST `/api/blog/<uuid>/deliberation/` at `core/views_deliberation.py:320-386` (returns `review_verdicts` + `decision` fields at :379-380). **Rigby cannot inspect a Cat B verdict via PA tool at all.** Same write-only-forgotten pattern as S1402 F.B1 Revenue OutreachDraft delivery. **Owed to Cat E S1605 as the surface-owner + xx99 D65a-integration-posture input (Rigby ↔ Cat B integration cost).**

5. **MEDIUM — ConversationOrchestrator hardcodes critique-conversation agents (EditorAgent + ContentStrategyAgent) at `content_deliberation_runner.py:252-253`, NOT domain-aware.** This contradicts v2's DomainPersonaReviewer conditional pattern (domain-aware when `confidence >= 0.2` at v2 :201). Two review layers run in the same call — a domain-aware v2 panel (Skeptic + FactCheck + optional DomainPersona) THEN a domain-blind orchestrator critique (EditorAgent + ContentStrategyAgent) that itself auto-triggers DecisionEnforcerAgent. Design boundary between "direct reviewer panel" and "orchestrated critique conversation" is unclear. Owed to xx99 §6 for boundary clarification.

6. **MEDIUM — Rewrite pass = single iteration only, no convergence loop, no post-rewrite decision re-invocation.** At `content_deliberation_runner.py:107-116`, if `decision == 'REVISE'` a single `_rewrite_draft` fires; if it fails/returns None, original draft is preserved (per `:115-116` warning-log branch). Post-rewrite, `DecisionEnforcerAgent` is NOT re-invoked to re-evaluate the rewritten text. Blog lands in `needs_enhancement` (:167 Session 1007 comment) status. Downstream recovery envelope depends on the `auto_enhance_blogs` beat entry existence (deferred to Cat C S1604 investigation).

7. **MEDIUM — DeliberationSession retention is unbounded.** `core/models_deliberation.py:20-95` defines the model with `created_at` + `updated_at` but no TTL / archival / retention policy. Migration lineage: `0232` (2026-02-08 Phase 1 introduction) + `0283` (2026-03-03 adds `failure_reason_code` + `failure_detail`). Cascade: `DeliberationTurn` CASCADE + `ContractRecord` CASCADE + `DocVersion` SET_NULL. Table grows monotonically across the three Cat B deployment paths. Owed to xx99 §7 anchor-update recommendations.

**Verifier-loop record.** 7 pre-Explore load-bearing claims verified by direct file:line read before six parallel Explore sub-agents per §13 fired (§20.1 record). Six Explores returned. 3 post-Explore load-bearing binary claims verified by direct grep after Explore return per §14 "grep-verify binary claims before shipping to Rigby" rule (§20.4 record) — result: (a) `queue_agent_task` MISSING confirmed; (b) `gpt-5.2` model-string is valid internal ID across 14 files, Explore SPECULATIVE flag RETRACTED; (c) v1 ContentReviewPanel classification refined from "dormant" to PARTIALLY-ADOPTED-LIVE-SECONDARY based on ContentWriterAgent consumer + `ENABLE_CONTENT_REVIEW=True` guard.

**D62 4-item mini-schema per surface applied upfront** (per S1600 parent D68 F8/F10 folds; second sibling of Group 1600 after S1601 first to propagate) at §4.8 (models), §5.6 (services), §6.5 (APIs), §8.5 (data ownership). Columns aligned to Group 1600's three posture axes: (a) canonical vs parallel-sibling vs shared-container (D65a Deliverable canonicalization); (b) pre-publish (Cat B) vs cross-boundary vs downstream (F1 boundary discipline); (c) integration posture requirement; (d) island posture requirement.

**D48 preemptive stability-probe gate 11th arm** — Rigby SIGN cycle 1 to fire on fresh isolation pin at §20.5 commit; if held clean → six-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602 anticipated, extending 10-arc precedent codification-ready per S1599 §10.2 6-candidate codify list.

---

## 2. Domain Purpose

Cat B is the **pre-publish gating layer of Content Deliberation Pipeline v2**. Between Cat A (ClaimsPack + draft generation) and Cat C (PublishGate + publish rails), Cat B answers three questions per draft:

1. **Are the claims cited?** (`FactCheckReviewer` verdict on citation coverage — LLM prompt-based, not code-enforced per §1 finding #1.)
2. **Is the draft grounded in evidence rather than hallucinated?** (`SkepticReviewer` verdict on hallucination-risk + generic-filler + logical-leaps.)
3. **Does the draft demonstrate domain expertise?** (`DomainPersonaReviewer` conditional verdict — fires only when `_detect_domain(topic)` returns non-'general' domain with `confidence >= 0.2` at `content_review_panel_v2.py:201`.)

Then it forces a **structured decision** (PUBLISH / REVISE / KILL) via `DecisionEnforcerAgent` (patent provenance `docs/patents/DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md`) rather than letting the deliberation trail off in an ambiguous state. If REVISE, one rewrite pass fires (single iteration, no convergence loop per §1 finding #6).

**Boundary rule (parent §3 B F1 fold — Cat B/C/D crisp separation):**
- Cat B owns *whether the draft passes reviewer verdicts + decision-enforcement contract*.
- Cat B does NOT own downstream quality thresholds (Cat C: `PublishGate.QUALITY_THRESHOLD=0.70` + `NOVELTY_THRESHOLD=0.60` + `STRUCTURE_THRESHOLD=0.55` + `MYTHOLOGY_THRESHOLD=0.15` per `publish_gate.py:44-49`).
- Cat B does NOT own the Deliverable base object model, variants, or lifecycle states (Cat D: `Deliverable` at `models_deliberables.py:84` + parallel variants including `SelfBlog`).

**Cross-boundary handoffs Cat B owns:**
- **Cat A → Cat B (inbound):** `draft_text` (str) + `claims_pack` (`ClaimsPack` object or None; `to_prompt_block()` yields empty string when None) + `topic` (str) + optional pre-detected `domain` (str).
- **Cat B → Cat A (outbound rewrite loop):** `required_changes` (List[str]) extracted from each reviewer at `content_deliberation_runner.py:290-293` → packed into `context['review_feedback']` at :319 + `context['original_draft']` at :318 for `ContentWriterAgent` REWRITE MODE dispatch (Session 1098 PR-A explicit context-key contract).
- **Cat B → Cat C (outbound decision handoff):** `decision` (PUBLISH / REVISE / KILL) extracted at runner :97-105 → consumed by Step 8 `PublishGate.apply_to_blog(blog)` at :138-160.
- **Cat B → Cat D (outbound persistence):** `deliberation_meta` dict at runner :381-389 → written to `SelfBlog.stats_snapshot['deliberation']` at :415 (single write per S1601 F5 fold).

---

## 3. Canonical Entry Points

Six canonical entry points define the Cat B execution surface. Every pre-publish gating decision traverses at least one; the deliberation pipeline traverses all six.

| # | Entry Point | File:Line | Type | Description |
|---|-------------|-----------|------|-------------|
| 3.1 | `run_reviews(draft, claims_pack, topic, domain)` | `core/services/content_review_panel_v2.py:208-256` | Module-level function (Q1 resolution) | v2 reviewer panel dispatch. Fires Skeptic + FactCheck always; DomainPersona conditional on `_detect_domain` non-'general' AND `confidence >= 0.2`. Returns `List[dict]` of verdict payloads. |
| 3.2 | `_detect_domain(topic)` | `content_review_panel_v2.py:195-205` | Module-level function | Wraps `DomainContentContextBuilder.detect_domain(topic)` at `core/services/domain_content_context.py:141` (returns `confidence = min(max_score / 5.0, 1.0)` — keyword-count-based, 5+ matches = full confidence). Applies `confidence >= 0.2` gate. Returns domain string or None. |
| 3.3 | `DecisionEnforcerAgent.execute(task, context)` | `core/agents/decision_enforcer_agent.py:180-282` | `BaseAgent` subclass | Reads `context['debate_messages']` + `context['synthesis']` + `context['topic']`; calls `_call_llm_for_decision` at :360 with `gpt-5.2` model + `max_completion_tokens=2000`; parses result into `ExecutionMandate` at `_parse_mandate` :394-442; returns `AgentResult` with mandate dict + tasks_spawned count. |
| 3.4 | `ContentDeliberationRunner._run_review_conversation(draft_text, claims_pack, topic)` | `core/services/content_deliberation_runner.py:223-264` | Method | Cat B orchestration: calls `run_reviews` at :228 → builds review_summary block at :230-239 → calls `ConversationOrchestrator.generate_conversation(conversation_type='critique', num_turns=4, ...)` at :251-259 → extracts `session_id` + `mandate_dict` at :261-262. |
| 3.5 | `ContentDeliberationRunner._extract_decision(mandate_dict, review_results)` — **Cat B-OWNED** (F2 fold pre-commit) | `content_deliberation_runner.py:266-284` | Method | Two-tier decision resolution: Tier 1 `mandate_dict['chosen_path']` keyword-match (PUBLISH / KILL / REVISE) at :270-273 → Tier 2 reviewer-verdict aggregate (all-PASS → PUBLISH, any-FAIL → REVISE) at :276-281 → default REVISE at :284. **F2 fold framing (Rigby Batch A/C Q1 tightening):** Cat B-OWNED decision extraction, not "runner glue". Cat B canonical output (PUBLISH/REVISE/KILL keyword) is produced HERE. |
| 3.6 | `ContentDeliberationRunner._rewrite_draft(topic, draft_text, review_results, claims_pack, voice)` | `content_deliberation_runner.py:286-336` | Method | Single-iteration rewrite. Extracts `feedback_lines` from `review_results[].required_changes[:3]` at :291-293; returns None if empty at :295-296; else fires `ContentWriterAgent.execute` with REWRITE MODE context (`context['original_draft']` + `context['review_feedback']` per Session 1098 PR-A comment at :307-310). |

**Auto-trigger surface (Cat B via ConversationOrchestrator):** `ConversationOrchestrator._enforce_decision` at `core/conversation_orchestrator.py:1550-1630`. Two invocation paths per `_enforce_decision` call sites at :1247-1249 (primary — when `decision_summary` extracted) + :1268-1284 (fallback — when `decision_summary` missing AND `conversation_type in ('debate', 'planning', 'critique')`). Guard at :1578 filters `conversation_type not in ('debate', 'analytical', 'critique', 'planning')`. Flag: `ENABLE_DECISION_ENFORCEMENT = True` (hardcoded) at :54. Runner fires this by passing `conversation_type='critique'` at :255.

**Boundary caution (extends S1601 F6 fold to Cat B):** verification-report endpoint `deliberation_verification_report()` at `core/views_deliberation.py:394-566` inspects execution verdicts + evidence stats + trace stats. If future refactor moves per-claim citation checks into this endpoint (currently absent per §1 finding #1), Cat B ownership extends to that endpoint despite REST-layer implementation. Currently: read-only Phase 0-3 verification without per-claim inspection.

---

## 4. Major Models

### 4.1 `ExecutionMandate` (Cat B-owned; transient dataclass, persisted as `ContractRecord.contract_data` dict)

Location: `core/contracts/execution_mandate.py:76-412`.

Frozen-dataclass fields (required + optional):
- Required: `chosen_path` (str), `reason` (str), `decision_owner` (str), `kill_criteria` (List[str]), `deadline` (str), `experiments` (List[str]).
- Optional: `rejected_paths` (Dict[str, str] default={}), `acknowledged_risks` (List[str] default=[]), `confidence` (float default=0.6), `confidence_reason` (str default=''), `spawned_tasks` (List[SpawnedTask] default=[]), `status` (`MandateStatus` enum default=ACTIVE), `source_conversation_id` (Optional[str]), `source_synthesis_id` (Optional[str]), `created_at` (str ISO), `created_by` (str default='DecisionEnforcerAgent').

Validation gates at `validate()` (:183-240): 10 rules including chosen_path specificity + weasel-phrase blocking (14 forbidden phrases: "further analysis", "consider", "TBD", "should validate", "needs investigation", etc.) + reason evidence length + decision_owner presence + kill_criteria measurability (regex `\d|<|>|%|within|after|before`) + deadline presence + experiments count ≥ 1 + confidence_reason required when confidence < 0.5. Raises `ValueError`; called via `create()` classmethod at :329-368.

Persistence contract: NOT a Django model. In-memory dataclass produced by DecisionEnforcerAgent → serialized via `.to_dict()` at :242-277 → written to `ContractRecord.contract_data` at `conversation_orchestrator.py:1341-1343` via `ContractRecord.objects.create(session=deliberation_session, contract_type='execution', contract_data=execution_mandate.to_dict(), trace_id='')`. Also snapshot-mirrored into `SelfBlog.stats_snapshot['deliberation']` at `content_deliberation_runner.py:381-389`.

### 4.2 `MandateStatus` (Cat B-owned enum)

Location: `core/contracts/execution_mandate.py:51-65`. Values: ACTIVE / PAUSED / KILLED / COMPLETED / SUPERSEDED. Default: ACTIVE (set at Mandate construction). **F4 fold pre-commit correction (Rigby Batch B/C Q4-#3 grep-verified):** Contract SUPPORTS post-construction transitions via `mark_killed(reason)` at `execution_mandate.py:404-407` (sets `self.status = MandateStatus.KILLED` + appends `f"KILLED: {reason}"` to acknowledged_risks) + `mark_completed()` at :409-411 (sets `self.status = MandateStatus.COMPLETED`). **However, NO caller in the deliberation flow invokes them.** Grep-verified `mark_killed|mark_completed` returns only the definition sites — zero call sites in `content_deliberation_runner.py` / `conversation_orchestrator.py` / `decision_enforcer_agent.py`. Correct classification: **dormant state machine (contract supports transitions but deliberation flow doesn't drive them), not missing machinery.** State advancement wiring is Cat E / Cat F ownership decision.

### 4.3 `SpawnedTask` (Cat B-owned dataclass)

Location: `core/contracts/execution_mandate.py:77-94`. Fields: `task_id` (Optional[str], populated after `queue_agent_task.delay()` return), `agent` (str), `action` (str), `deadline` (Optional[str]), `depends_on` (List[str]), `priority` (int 1=highest, 5=lowest). Feeds `DecisionEnforcerAgent.spawn_tasks_from_mandate` at `decision_enforcer_agent.py:444-477`. **See §1 finding #3: `queue_agent_task` MISSING → spawn crashes with unhandled `ImportError`.**

### 4.4 `DeliberationSession` (shared cross-Cat: orchestrator-owned + reviewer-verdict-populated)

Location: `core/models_deliberation.py:20-95`. Django model, UUID PK. Fields: `id` (UUID), `session_type` (choices hivemind/conceptforge/agent/composite default=hivemind), `objective` (TextField), `participants` (JSONField list), `status` (choices pending/active/completed/failed default=pending, db_index=True), `evidence_pack` (JSONField dict; reviewer-verdict + claim-source landing zone), `trace` (JSONField dict; session-trace + contract snapshots), `parent_session` (self FK SET_NULL), `trace_id` (CharField 64 db_index=True), `failure_reason_code` (CharField choices 7 codes — TIMEOUT/LLM_UPSTREAM/EMPTY_TURN/TOOL_ERROR/GATE_REJECT/DRAFT_FAILED/UNKNOWN — migration 0283 db_index=True), `failure_detail` (TextField — migration 0283), `created_at` / `updated_at` / `completed_at`.

Reverse relations: `turns` (`DeliberationTurn` CASCADE), `contracts` (`ContractRecord` CASCADE), `doc_versions` (`DocVersion` SET_NULL), `agent_sessions` (`AgentSession` SET_NULL), `conceptforge_runs` SET_NULL, `hivemind_sessions` SET_NULL.

Indexes (migration 0232 + 0283): `-created_at`, `status`, `trace_id`, `failure_reason_code`.

**Retention: unbounded (§1 finding #7). No TTL, no archival command, no cleanup task.**

### 4.5 `DeliberationTurn` + `ContractRecord` + `DocVersion` (shared cross-Cat)

`DeliberationTurn` at `models_deliberation.py:163-202`: FK to DeliberationSession CASCADE, `turn_number` (unique per session), `agent_name`, `role`, `content` (TextField + auto SHA256 content_hash), `contract_state` (JSONField nullable snapshot), `trace_id`, `created_at`. Cat B contribution: `run_reviews` verdicts do NOT persist as `DeliberationTurn` rows — the review conversation happens INSIDE `ConversationOrchestrator.generate_conversation()`, which persists Editor + ContentStrategy critique turns, not Skeptic/FactCheck/Domain verdicts.

`ContractRecord` at `models_deliberation.py:205-234`: FK to DeliberationSession CASCADE, `contract_type` (choices research/synthesis/execution), `contract_data` (JSONField dict — stores `ExecutionMandate.to_dict()` when `contract_type='execution'`), `trace_id`. No unique constraint — multiple ContractRecords per session possible.

`DocVersion` at `models_deliberation.py:237-271`: FK to DeliberationSession SET_NULL. Auxiliary version tracking; not core to Cat B verdict flow.

### 4.6 `SelfBlog.stats_snapshot['deliberation']` (Cat D-owned model, Cat B writes)

Location: `core/models_unified_system.py:20611` (SelfBlog model), `stats_snapshot` JSONField at :20742. Cat B populates `stats_snapshot['deliberation']` at `content_deliberation_runner.py:381-389` via `deliberation_meta = { 'session_id': session_id, 'decision': decision, 'claims_count': ..., 'sources_count': ..., 'reviewers': [...], 'review_verdicts': ['PASS'|'REVISE'|'FAIL', ...], 'gate_result': None }`. Written at :415 inside `SelfBlog.objects.create(...)`. Cat C PublishGate updates `stats_snapshot['deliberation']['gate_result']` later (Cat C S1604 owns that step). **This is the sole downstream-consumer-readable Cat B verdict persistence.**

### 4.7 Reviewer verdict schema (Cat B-owned in-memory only; not persisted)

`validate_review_payload` at `content_review_panel_v2.py:27-66` defines required keys: `{reviewer, verdict, top_issues, required_changes, suggested_edits, confidence}`. Verdict enum: `{PASS, REVISE, FAIL}`. Issue type enum: `{missing_citation, weak_claim, hallucination_risk, generic, tone, structure, reviewer_error}`. Severity enum: `{low, med, high}`. **Not a Django model — validation applies to per-call return list only.** Persistence loss: `top_issues` details + `suggested_edits` are discarded after `_extract_decision` reads verdicts; only aggregated `['PASS'|'REVISE'|'FAIL', ...]` verdict list lands in `SelfBlog.stats_snapshot['deliberation']['review_verdicts']`.

### 4.8 D62 model surface mini-schema (four-item, propagated upfront per parent D68 F8/F10)

| Surface | (a) canonical/parallel-sibling/shared-container | (b) pre-publish/cross-boundary/downstream | (c) integration posture requirement | (d) island posture requirement |
|---------|--------------------------------------------------|-------------------------------------------|-------------------------------------|---------------------------------|
| `ExecutionMandate` (dataclass; persisted as ContractRecord) | canonical (single mandate schema) | pre-publish + cross-boundary (spawn tasks may reach outside Cat B) | remains canonical; migrate `spawn_tasks_from_mandate` to Cat E `governance_tool.decision_promote` | parallel-sibling per lane (Content mandate + Revenue mandate + Sports mandate) |
| `DeliberationSession` (shared container) | shared-container (Cat A orchestration + Cat B verdicts co-tenant) | cross-boundary (all Cat A/B contract persistence) | canonical; add per-lane subtype (`session_type='content_v2'`) | parallel-sibling per lane |
| `MandateStatus` enum | canonical | pre-publish + downstream (transitions may extend into Cat C/D) | canonical; add lifecycle transition rules | per-variant enum |
| `SelfBlog.stats_snapshot['deliberation']` | parallel-sibling (Cat B writes here bypassing `deliverable_factory` — S1601 §9.1 D65a evidence input; F1 canonicalization-debt reframe) | downstream (Cat D-owned; Cat B is upstream writer) | migrate write to `Deliverable.metadata` canonical path | keep write-to-SelfBlog + add write-to-Deliverable when Cat D variants adopt |

---

## 5. Major Services

### 5.1 `content_review_panel_v2` (module-level dispatch; CANONICAL for deliberation pipeline)

File: `core/services/content_review_panel_v2.py`, 256 lines. Architecture: NO classes; module-level constants + helpers + dispatch function. Design intent per module docstring lines 1-10: parallel v2 path avoiding v1 class rewrite. Model choice hardcoded: `gpt-4.1-mini` at :162 + `temp=0.3` + `max_tokens=1500`.

Components:
- Schema constants at :19-24: `REQUIRED_REVIEW_KEYS`, `VALID_VERDICTS`, `VALID_ISSUE_TYPES`, `VALID_SEVERITIES`.
- `validate_review_payload(data) -> (bool, List[str])` at :27-66: structural validation only (no per-claim regex per §1 finding #1).
- `_make_fail_payload(reviewer_name, reason) -> dict` at :69-83: synthetic FAIL payload (verdict='FAIL', confidence=0.0, top_issues=[{type:'reviewer_error', severity:'high'}]).
- Reviewer system prompts at :88 (`SKEPTIC_SYSTEM`), :107 (`FACTCHECK_SYSTEM`), :124 (`DOMAIN_SYSTEM_TEMPLATE`).
- `_call_llm_reviewer(system_prompt, user_content, reviewer_name)` at :143-192: LLM call via `LLMProviderRegistry.complete(provider='openai', model_id='gpt-4.1-mini', ...)`. Catches 4 exception types (LLMRequest failure, JSONDecodeError, validation error, generic Exception) → returns synthetic FAIL payload. **All 4 branches map to same "reviewer_error" tag → downstream `panel_failed` detection at runner :372-378 requires ALL reviewers to fail with reviewer_error.**
- `_detect_domain(topic) -> Optional[str]` at :195-205: wraps `DomainContentContextBuilder.detect_domain(topic)`; applies `confidence >= 0.2` gate.
- `run_reviews(draft, claims_pack, topic, domain)` at :208-256: dispatch. Constructs `user_content` at :230-236 including `draft[:8000]` **silent truncation (§1 finding #2 HIGH)**. Always fires Skeptic (:241) + FactCheck (:244); DomainPersona (:250-254) conditional. Returns List[dict].

### 5.2 `content_review_panel` (v1 legacy; PARTIALLY-ADOPTED-LIVE-SECONDARY)

File: `core/services/content_review_panel.py`, 350 lines. Architecture: class-based `ContentReviewPanel` at :61 with lazy-loaded dependencies (DomainContentContextBuilder at :80-86, SpiderContextBuilder at :89-96, ConversationOrchestrator at :99-106).

Design pattern: 2-agent critique conversation (EditorAgent + first-available domain expert from `DOMAIN_REVIEW_AGENTS` dict at :44 — 10 domains → 2 agents each). Injects spider intelligence (`_get_spider_context` at :208-226 with `hours=48, max_trends=5`). Uses `ConversationOrchestrator.generate_conversation(conversation_type='critique', num_turns=4, ...)` at :268-280. Decision extraction fallback tree at :287-331: mandate `chosen_path` (:299-306, confidence 0.85/0.80/0.75) → `decision_summary.decision` (:308-317, confidence 0.70/0.65/0.60) → last-3-message keyword scan (:319-328, confidence 0.50/0.50) → default 'revise' 0.40 (:331). Fallback decision='draft' on any exception at :160-167.

**Consumer inventory (post-Explore grep-verified):**
- Live secondary consumer: `core/agents/content_writer_agent.py:1376-1377` inside `if ENABLE_CONTENT_REVIEW:` guard (flag=True hardcoded at :62). Fires on ContentWriterAgent direct-write path (non-deliberation blog writes).
- Test-only consumer: `core/tests/test_content_review_panel.py:12,25` (unit test).
- v2 module docstring at :9 acknowledges v1 as "parallel v2 path" — `content_deliberation_runner.py:225` does NOT import v1.

**Classification: PARTIALLY-ADOPTED-LIVE-SECONDARY.** Not dormant (S1274 EventBus lesson prevented "dormant" mislabel via post-Explore grep). Q2 canonicalization posture per parent §6.1 remains **open evidence to xx99 D65-analog decision**: keep dual-path (v1 for single-blog + v2 for deliberation) OR retire v1 by rerouting ContentWriterAgent through v2 `run_reviews` (would collapse dispatch to v2 while preserving 2-agent critique via orchestrator direct call). Design cost of dual-path: same domain-detection logic implemented twice (v1 :173-183 + v2 :195-205); same 2-agent critique implemented twice (v1 :232-281 + runner :251-259).

### 5.3 `DecisionEnforcerAgent` (Cat B-owned; class-based BaseAgent subclass)

File: `core/agents/decision_enforcer_agent.py`, 526 lines. Class-def at :60 extends `BaseAgent`. Class attributes: `name='DecisionEnforcerAgent'`, `description='Forces decisive action after debate...'`, `specialization='decision enforcement'`, `output_category=OutputCategory.DECISION`.

System prompt at :82-173: enforces decisiveness. Bans 7 weasel phrases at :96-103 (Further analysis / More research / Consider exploring / Should validate / Needs investigation / Productive discussion / We should look into). Requires JSON output with 12 required keys (chosen_path, reason, decision_owner, confidence, confidence_reason, experiments, kill_criteria, deadline, rejected_paths, acknowledged_risks, spawned_tasks).

`execute(task, context)` at :180-282: reads `debate_messages` / `synthesis` / `topic` from context; validates non-empty at :210-217; builds debate summary via `_summarize_debate` at :284-324 (truncates each agent contribution at 500 chars :319, limits to 4 agents :321-322); extracts hints via `extract_experiments_from_debate` + `extract_kill_criteria_from_debate` at :223-224; calls `_call_llm_for_decision` at :360-392; parses via `_parse_mandate` at :394-442; returns `AgentResult(success=True, data={mandate, mandate_markdown, topic, debate_length, tasks_spawned})`.

`_call_llm_for_decision(prompt)` at :360-392: uses `get_openai_client()` at :364 (Anthropic-factory pattern applies to OpenAI too per memory rule `feedback_openai_client_factory.md`); model `gpt-5.2` at :372; `max_completion_tokens=2000` at :374 (**passes memory rule `feedback_gpt5_max_completion_tokens_floor.md` 4000-floor threshold — MAY UNDERRUN**); JSON extraction handles 3 formats (direct parse :382 → markdown-fenced :385-387 → object-in-content :389-391). Raises `ValueError` at :392 if all three fail.

`_parse_mandate(decision_json, debate_messages, synthesis)` at :394-442: deadline default 7 days at :406; "Nd" relative deadline parser at :407-410; SpawnedTask reconstruction at :413-420 (no AgentRouter.AGENT_MAP validation — blast radius per §1 finding #3); ExecutionMandate construction at :422-437; validate() call at :440.

`spawn_tasks_from_mandate(mandate)` at :444-477: **CRITICAL runtime bug per §1 finding #3.** Imports `queue_agent_task` at :456 from core.tasks WITHOUT try/except guard; fires `queue_agent_task.delay(agent_name=spawned.agent, ...)` at :460. Grep-verified missing definition. Contrast: `core/services/auto_spawner_service.py:321-337` DOES have `try/except ImportError` fallback with `logger.warning("queue_agent_task not available")` at :337 — precedent that other callers know this task can be absent.

Utility function `enforce_decision_after_synthesis(debate_messages, synthesis, topic, auto_spawn=False)` at :481-526: convenience wrapper; auto_spawn=True triggers spawn_tasks_from_mandate + returns task_ids in result dict. Not called from runner (grep-verified).

### 5.4 `ContentDeliberationRunner` review orchestration slice (Cat A owner; Cat B lens)

File: `core/services/content_deliberation_runner.py`, 453 lines. Cat A owns the class (`run_blog` orchestration); Cat B lens applies to Steps 3-5 covered by §3.4-§3.6 above. Cat B-relevant runtime flow:
- Step 3 `_run_review_conversation` at :223-264 (§3.4).
- Step 4 `_extract_decision` at :266-284 (§3.5) — Tier 1 mandate keyword-match / Tier 2 reviewer-verdict aggregate / Tier 3 default REVISE.
- Step 4b post-decision Cat A downgrade at :99-105: `if decision == 'PUBLISH' and claims_count == 0: decision = 'REVISE'`. Cat A owns the gate check.
- Step 5 rewrite at :107-116 (§3.6) — single-iteration; on exception logs warning + preserves original draft at :115-116.
- Step 7 blog save at :127-135 → `_save_blog` at :351-422 including `deliberation_meta` construction at :381-389 + persistence at :401-416.
- Panel-failed detection at :372-378: ALL reviewers must fail with reviewer_error tag → status='draft' + gate_notes='panel_failed'.

### 5.5 `ConversationOrchestrator._enforce_decision` (Cat B decision-production substrate — F1 fold pre-commit)

**F1 fold framing tightening (Rigby Batch A/C Q1 tightening):** The orchestrator critique conversation + auto-triggered `_enforce_decision` is NOT "just another review layer" — it is the **substrate where DecisionEnforcerAgent actually produces the ExecutionMandate that drives Cat B's PUBLISH/REVISE/KILL decision**. The runner passes reviewer verdicts + draft as input; the orchestrator's critique-conversation transcript + fallback-summary-from-last-3-messages become DecisionEnforcerAgent's `context['debate_messages']` + `context['synthesis']`; the resulting mandate is Cat B's canonical output. Treating this as "Cat B wiring inside orchestrator" understates its centrality — this IS where Cat B's mandate is minted.

File: `core/conversation_orchestrator.py`, 2184 lines. Not god-service per §5.6 line-count check (< 3000 lines threshold from playbook §13 Agent 2 focus).

Cat B-relevant surface:
- Flag `ENABLE_DECISION_ENFORCEMENT = True` at :54 (hardcoded).
- Primary invocation at :1247-1249: `if ENABLE_DECISION_ENFORCEMENT and decision_summary: mandate_result = self._enforce_decision(...)`.
- Fallback invocation at :1268-1284: when `decision_summary` missing AND `conversation_type in ('debate', 'planning', 'critique')` — synthesizes fallback summary from last N messages then re-invokes `_enforce_decision`.
- Guard at :1578: `if conversation_type not in ('debate', 'analytical', 'critique', 'planning'): return early`.
- Method `_enforce_decision` def at :1550-1630: instantiates DecisionEnforcerAgent + calls `.execute()` + parses AgentResult + persists to ContractRecord at :1341-1343.
- Adjacent flag `ENABLE_SYNTHESIS_CONTRACT` at :1303 fires for same conversation_type set.

**Design intent per module docstring not read fully.** Session 873 comment reference at :1559 ("Prefrontal Cortex") ties this to `docs/patents/DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md` §5 Layer 2 provenance.

### 5.6 D62 service surface mini-schema (four-item, propagated upfront)

| Surface | (a) canonical/parallel-sibling/shared-container | (b) pre-publish/cross-boundary/downstream | (c) integration posture requirement | (d) island posture requirement |
|---------|--------------------------------------------------|-------------------------------------------|-------------------------------------|---------------------------------|
| `content_review_panel_v2` (module dispatch) | canonical for deliberation | pre-publish (owns reviewer verdicts) | canonical + add v1 retirement | parallel-sibling per lane |
| `content_review_panel` v1 (class) | parallel-sibling (PARTIALLY-ADOPTED-LIVE-SECONDARY) | pre-publish (owns single-blog reviews) | retire; migrate ContentWriterAgent to v2 | keep as fallback; add v3 for other lanes |
| `DecisionEnforcerAgent` | canonical (across ALL debate/critique/planning) | cross-boundary (spawns Celery tasks reaching outside Cat B) | canonical; add AGENT_MAP validation + Cat E surface for mandate readback | per-lane subclass |
| `ConversationOrchestrator._enforce_decision` | canonical (Cat B wiring via orchestrator) | pre-publish (owns mandate auto-trigger) | canonical; parameterize agent1/agent2 to be domain-aware | per-conversation-type subclass |

---

## 6. Major APIs and Interfaces

### 6.1 REST endpoints

| # | Endpoint | File:Line | Cat B relevance | Verdict/mandate exposure |
|---|----------|-----------|-----------------|--------------------------|
| 6.1.1 | `POST /api/v1/research/self-blog/generate-v2/` | `core/views_research_demo.py:1106-1145` (`generate_v2_blog_api`) | Trigger surface | Returns `task_id` only. No embedded verdict/mandate data. Client polls via 6.1.2. |
| 6.1.2 | `GET /api/v1/research/self-blog/tasks/<task_id>/` | `core/views_research_demo.py:1149-1200` | Task-status poll | Returns `blog_id` when Celery task complete. No embedded deliberation metadata. |
| 6.1.3 | `GET /api/deliberation/sessions/` | `core/views_deliberation.py:51-90` | List (Session 962 Phase 1) | Returns list with `turn_count`, `contract_count`, `blog` lookup via `_get_blog_for_session` at :25-47 (reverse-looks up SelfBlog via `stats_snapshot['deliberation']['session_id']` — verdict = `decision`, quality_score, structure_score, publish_ready). Only available if blog persisted. |
| 6.1.4 | `GET /api/deliberation/sessions/<session_id>/` | `core/views_deliberation.py:93-114` | Full session | Participants + `evidence_pack` + `trace` (raw); no reviewer-verdict summary. |
| 6.1.5 | `GET /api/blog/<uuid>/deliberation/` | `core/views_deliberation.py:320-386` (`blog_deliberation_detail`) | **CRITICAL Cat B readback surface** | Full deliberation replay: turns + contracts + trace + evidence_pack + `review_verdicts` list at :380 + `decision` field at :379 (from `stats_snapshot['deliberation']`). Execution contract data at :366-370. Only reader of Cat B verdicts. |
| 6.1.6 | `GET /api/deliberation/sessions/<uuid>/verification-report/` | `core/views_deliberation.py:394-566` (`deliberation_verification_report`) | S1601 F6 boundary caution | Phase 0-3 verification. Returns contract count + execution verdict summary + evidence stats + trace stats. NO reviewer verdicts exposed. |
| 6.1.7 | `GET /api/deliberation/failure-stats/` | `core/views_deliberation.py:570-601` | Failure-reason breakdown | Aggregates `failure_reason_code` counts. No reviewer data. |

### 6.2 PA tools

| Tool | Schema file:line | Handler file:line | Cat B relevance | Coverage gap |
|------|-----------------|-------------------|-----------------|--------------|
| `blog_tool.generate` | `pa_tool_schemas.py:3464+` | `td_handlers_content.py:162-182` `_handle_blog_direct` → `:1480-1505` `_handle_generate_blog` | Trigger surface | Returns Celery `task_id`. No verdict/mandate embedded. |
| `content_tool.generate_blog` | `pa_tool_schemas.py:3291-3370` | `td_handlers_content.py:235-400+` `_handle_content_review` | Trigger surface | Same — task_id only. |
| `content_tool.publish` / `content_tool.approve` | `pa_tool_schemas.py:3291-3370` | `td_handlers_content.py:235-400+` | Post-decision (Cat C surface) | Checks `blog.publish_ready` flag; does not surface reviewer verdicts. |
| `governance_tool.decision_promote` / `.decision_reject` / `.decision_decide` / `.decision_list` | `pa_tool_schemas.py:3162-3230` | (Session 1163) | Adjacent Cat B (mandate governance) | Handles decision-authority items but NOT Cat B reviewer verdicts or DecisionEnforcerAgent mandate output. |
| `agent_tool.run_agent agent_name=DecisionEnforcerAgent` | `pa_tool_schemas.py` (agent_tool schema) | `AGENT_MAP` (grep-verified DecisionEnforcerAgent registered) | Direct trigger | Would bypass ConversationOrchestrator wiring. Grep does NOT find production callers using this path — only test/orchestrator. |

**PA-tool cover map (§1 finding #4 HIGH):**

| Cat B piece | PA tool surface | Status | Gap |
|-------------|-----------------|--------|-----|
| Reviewer verdicts (Skeptic + FactCheck + Domain) | None | REST 6.1.5 only | **MISSING** |
| ExecutionMandate `chosen_path` / `reason` / `decision_owner` | None | REST 6.1.5 only | **MISSING** |
| `top_issues` + `required_changes` per reviewer | None | Discarded post-`_extract_decision`; NOT persisted | **MISSING + PERSISTENCE LOSS** |
| Rewrite trigger | Implicit in `blog_tool.generate` (Celery task chain) | Not queryable | **MISSING** |
| Synthetic-FAIL rate | None | No metrics endpoint | **MISSING** |

### 6.3 Celery tasks + beat schedule

| Task | File:Line | Beat entry? | Cat B involvement |
|------|-----------|-------------|-------------------|
| `generate_self_blog_deliberation_task` | `core/tasks.py:5758-5761` (wrapper) → `core/tasks_content.py:2399-2605` `_impl_generate_self_blog_deliberation_task` (instantiates runner at :2540) | ZERO — grep-verified no beat entry in `core/celery.py` | Full Cat A + B + C + D traverse. Queue: `content`. Budget-tier 3 (`ops_autopilot/budget.py:1076`). soft_time_limit=480s, time_limit=540s. |
| `queue_agent_task` | **MISSING FROM `core/tasks.py`** (grep-verified zero definitions) | N/A | §1 finding #3 CRITICAL — `DecisionEnforcerAgent.spawn_tasks_from_mandate` imports but definition absent. |

**Beat entries grep confirmed ZERO for reviewer panel + DecisionEnforcerAgent + deliberation.** Cat B is strictly on-demand — three trigger paths per §1 (REST 6.1.1 + PA tool 6.2.blog_tool.generate + Celery task 6.3.generate_self_blog_deliberation_task via direct `.delay()`). Adjacent beat entries (`generate-operator-edge-newsletter` Fri 06:00 + `generate-outreach-drafts-daily` 07:30 + `cleanup-stale-content` 10:05) do NOT share Cat B machinery per grep-verified separate call chains.

### 6.4 Management commands / WebSocket consumers / Discord / Frontend

- **Management commands:** ZERO commands to fire Cat B in isolation (grep of `core/management/commands/` for `review_panel|deliberation|decision_enforcer|content_review` returns only `verify_surgical_moves.py` — audit-only reader of models, does not trigger pipeline).
- **WebSocket consumers:** ZERO. Grep of `core/consumers*.py` for reviewer verdicts + mandate + deliberation returns zero matches.
- **Discord bot commands:** ZERO. Grep of `core/services/discord_bot.py` (11,676 lines, 96 commands, 25 Cog classes) for `decision_enforcer|review_panel|content_review_panel|deliberation|mandate` returns zero matches.
- **Frontend:** `frontend/src/pages/BlogViewerPage.tsx:36-65` fetches `/api/v1/research/self-blog/{blogId}/` at :45; receives `stats_snapshot` as `Record<string, unknown>` at :8 (generic); renders as key-value pairs at :56-57 (first 8 entries only). **NO special rendering** for reviewer verdicts / mandate / DecisionEnforcer output. Grep of `frontend/src/` for `review_verdicts|mandate|deliberation` returns zero component-level matches.

### 6.5 D62 API surface mini-schema (four-item, propagated upfront)

| Surface | (a) canonical/parallel-sibling/shared-container | (b) pre-publish/cross-boundary/downstream | (c) integration posture requirement | (d) island posture requirement |
|---------|--------------------------------------------------|-------------------------------------------|-------------------------------------|---------------------------------|
| REST `/api/blog/<uuid>/deliberation/` | canonical (sole Cat B readback) | pre-publish + downstream (spans A/B/C/D data) | canonical + add SelfBlog-agnostic wrapper for other Deliverable variants | parallel-sibling per lane (`/api/sportsbrief/<id>/deliberation/`, etc.) |
| `blog_tool` / `content_tool.generate_blog` PA trigger | parallel-sibling (redundant with 3 other trigger paths per S1601 Q2) | pre-publish (Cat B trigger only) | canonical + add verdict readback action | per-lane blog_tool + brief_tool + outreach_tool |
| `governance_tool.decision_*` (Session 1163) | canonical (adjacent Cat B decision-authority) | cross-boundary (extends beyond Cat B to Cat E governance) | canonical + extend to Cat B mandate lifecycle transitions | parallel per-domain governance |
| Missing: verdict-readback PA tool | (§1 finding #4) | pre-publish (Cat B verdict exposure) | ADD as canonical (`content_tool.review_verdicts`) | per-lane verdict action |

---

## 7. Runtime Flows

### 7.1 Cat B review + decide slice (start-to-end)

Steps aligned to `content_deliberation_runner.py:83-116`. Cat B slice spans Steps 3-5 of the 9-step Cat A+B+C runner (Steps 1-2 = Cat A; Steps 3-5 = Cat B; Steps 6-9 = Cat A + Cat C + Cat D).

```
STEP 3 — Review conversation orchestration (runner :83-95, _run_review_conversation :223-264)
├─ 3.a run_reviews(draft_text, claims_pack, topic, domain=None) at v2 :208-256
│  ├─ Auto-detect domain at v2 :247-249 if not supplied: _detect_domain(topic) at v2 :195-205
│  │  └─ DomainContentContextBuilder.detect_domain(topic) at domain_content_context.py:141
│  │     └─ confidence = min(max_score/5.0, 1.0)  # keyword-count-based
│  ├─ Build user_content at v2 :230-236
│  │  └─ SILENT TRUNCATION: draft[:8000] at v2 :236 (§1 finding #2 HIGH)
│  ├─ Fire SkepticReviewer at v2 :241 via _call_llm_reviewer(SKEPTIC_SYSTEM, user_content, 'SkepticReviewer')
│  │  └─ model=gpt-4.1-mini, temp=0.3, max_tokens=1500 (v2 :156-158, 162)
│  │  └─ On 4 failure branches → _make_fail_payload synthetic FAIL
│  ├─ Fire FactCheckReviewer at v2 :244 (same LLM-call shape)
│  │  └─ FACTCHECK_SYSTEM prompt at v2 :107-122 says "verify [C-xxxxxxxxxx] maps to URL"
│  │     └─ LLM prompt-only enforcement (§1 finding #1 HIGH CONFIRMED — no code-side regex)
│  ├─ Fire DomainPersonaReviewer at v2 :252-254 IF domain != 'general' AND confidence >= 0.2
│  │  └─ DOMAIN_SYSTEM_TEMPLATE.format(domain=domain) at v2 :251
│  └─ Return List[dict] — 2 or 3 verdicts (LOW numeric drift per §14)
├─ 3.b Build review_summary_lines at runner :230-239 (serialize each verdict as "Reviewer: VERDICT — top 3 issues")
├─ 3.c ConversationOrchestrator.generate_conversation at runner :251-259
│  ├─ Hardcoded agent1=EditorAgent + agent2=ContentStrategyAgent at runner :252-253 (§1 finding #5 MED)
│  ├─ conversation_type='critique' at :255 (triggers _enforce_decision auto-invocation)
│  ├─ num_turns=4 at :256
│  ├─ topic includes reviews block + draft[:3000] at :245-249 (second silent truncation)
│  └─ Orchestrator internal loop:
│     ├─ 4 turns Editor/ContentStrategy critique
│     ├─ Session 873 flag ENABLE_DECISION_ENFORCEMENT=True at orchestrator :54
│     ├─ Post-conversation: extract decision_summary from messages
│     ├─ IF decision_summary present at orchestrator :1247: call _enforce_decision at :1249
│     ├─ ELSE IF critique/debate/planning at :1268-1273: fallback synthesize from last-3-msgs + _enforce_decision
│     ├─ _enforce_decision at :1550-1630:
│     │  └─ DecisionEnforcerAgent(user=...).execute(task=..., context={debate_messages, synthesis, topic})
│     │     ├─ Model gpt-5.2 at decision_enforcer_agent.py:372
│     │     ├─ max_completion_tokens=2000 at :374 (may underrun per memory rule floor 4000)
│     │     ├─ Parse JSON via _parse_mandate at :394-442
│     │     └─ Return AgentResult(data={mandate: ExecutionMandate.to_dict(), ...})
│     └─ Persist to ContractRecord.contract_data at orchestrator :1341-1343
│        └─ ContractRecord.objects.create(session=deliberation_session, contract_type='execution', ...)
└─ Return (review_results, session_id, mandate_dict) at runner :264

STEP 4 — _extract_decision(mandate_dict, review_results) at runner :266-284
├─ Tier 1: mandate_dict['chosen_path'] keyword-match at :270-273 → PUBLISH / KILL / REVISE
├─ Tier 2: reviewer-verdict aggregate at :276-281
│  ├─ all-PASS → PUBLISH
│  └─ any-FAIL → REVISE
└─ Tier 3: default REVISE at :284

STEP 4b — Cat A post-decision downgrade at runner :99-105
└─ IF decision == 'PUBLISH' AND claims_count == 0: decision = 'REVISE' (Cat A gate)

STEP 5 — Conditional single-iteration rewrite at runner :107-116
├─ IF decision == 'REVISE': _rewrite_draft(topic, draft_text, review_results, claims_pack, voice) at :110
│  ├─ Extract feedback_lines from review_results[].required_changes[:3] at :290-293
│  ├─ IF feedback_lines empty: return None at :295-296
│  ├─ ContentWriterAgent.execute(task, context={original_draft, review_feedback, ...}) at :322-327
│  │  └─ REWRITE MODE dispatch per Session 1098 PR-A comment at :307-310
│  └─ Return (rewrite_text, generated_content) or None
├─ IF rewrite returns (new_draft, new_content): swap draft_text at :112-113 + increment revisions at :114
└─ ELSE: log warning at :115-116 + preserve original draft
   └─ NO CONVERGENCE LOOP (§1 finding #6 MED) — DecisionEnforcerAgent NOT re-invoked post-rewrite
```

### 7.2 Failure branches (Cat B slice)

1. **ClaimsPack build fails** (Cat A Step 1, runner :54-60) → log warning, continue with `claims_pack=None`. Cat B reviewers still run on draft WITHOUT claims data (graceful degrade at v2 :226-228 — `claims_block=''` if `claims_pack is None`).
2. **Draft generation fails** (Cat A Step 2, runner :62-77) → return `result['status']='draft'`, abort pipeline (cannot review empty draft). Failure fields: `failure_reason_code='DRAFT_FAILED'`.
3. **v2 `run_reviews` LLM failure per reviewer** (v2 :187-192) → 4 exception types → synthetic FAIL payload with `top_issues=[{type:'reviewer_error', severity:'high'}]`. Downstream `_extract_decision` treats reviewer_error same as any FAIL → forces REVISE.
4. **All reviewers synthetic-FAIL panel-failed** (runner :372-378) → `status='draft'`, `gate_notes='panel_failed'`. Blog persists but Cat C PublishGate skipped.
5. **ConversationOrchestrator critique conversation fails** (runner :83-95, catches Exception) → `result['decision']='REVISE'`, `mandate_dict=None`. Step 4 falls through to reviewer-verdict aggregate Tier 2.
6. **DecisionEnforcerAgent LLM failure** (`decision_enforcer_agent.py:270-282`) → returns `AgentResult(success=False, error=str(e))`. Bubbles up through orchestrator; runner sees no mandate_dict; Step 4 Tier 2 fallback fires.
7. **DecisionEnforcerAgent validation failure** (:260-269 ValueError from `mandate.validate()`) → returns AgentResult(success=False, message=f"Decision rejected: ..."). Same downstream path as (6).
8. **`spawn_tasks_from_mandate` ImportError** (§1 finding #3 HIGH latent-landmine per F5+F6 folds) — `queue_agent_task` missing → ImportError at decision_enforcer_agent.py:456 → **exception-swallowed by broad `try/except Exception` at :455/:474-476** (F5 fold correction). Silent failure logs `Failed to spawn tasks: {e}` and returns empty task_ids at :477. Grep confirms `enforce_decision_after_synthesis(auto_spawn=True)` at :481 is only caller of `spawn_tasks_from_mandate` (:521-524). No production callers found — code path exists but appears never-exercised. Deferred to xx99 for dispositional call: retire the dead-code path OR fix `queue_agent_task` + add validation.
9. **Rewrite pass fails** (runner :115-116) → log warning, keep original draft, continue pipeline. Blog persists at `needs_enhancement` status. No auto-retry.

---

## 8. Data Ownership and Lifecycle

### 8.1 Cat B-owned data

- **`ExecutionMandate` dataclass** (transient in-memory; serialized as `ContractRecord.contract_data` JSONField). Owner: `DecisionEnforcerAgent`. Lifecycle: constructed via `create()` classmethod → validated → persisted via `to_dict()` → NOT updated after persistence (no lifecycle transitions coded).
- **Reviewer verdict payloads** (transient in-memory List[dict]; NOT persisted individually — only aggregate `['PASS'|'REVISE'|'FAIL', ...]` list lands in `SelfBlog.stats_snapshot['deliberation']['review_verdicts']`). Owner: `run_reviews` module dispatch. **Persistence loss: `top_issues` details + `required_changes` + `suggested_edits` discarded post-`_extract_decision`.**
- **`MandateStatus` enum values** (ACTIVE / PAUSED / KILLED / COMPLETED / SUPERSEDED). Owner: `DecisionEnforcerAgent`. Lifecycle transitions NOT coded — status is write-once at Mandate construction, never updated.

### 8.2 Cat B writes (to other Cat-owned models)

- **`ContractRecord`** (Cat A / orchestrator-owned model). Cat B writes rows with `contract_type='execution'` + `contract_data=ExecutionMandate.to_dict()` at `conversation_orchestrator.py:1341-1343`. CASCADE deletion with parent `DeliberationSession`.
- **`SelfBlog.stats_snapshot['deliberation']`** (Cat D-owned model; single write per S1601 F5 fold). Cat B populates `deliberation_meta` dict at `content_deliberation_runner.py:381-389`. Cat C PublishGate later updates `stats_snapshot['deliberation']['gate_result']`.

### 8.3 Cat B reads (from other Cat-owned models)

- **`ClaimsPack` object** (Cat A-owned, transient not persisted). Cat B reads via `claims_pack.to_prompt_block()` at v2 :228 + `claims_pack.claims` at runner :100 (for downgrade gate).
- **`draft_text` + `generated_content` dict** (Cat A-owned transient). Cat B reads at v2 :236 (silent 8000-char truncation).
- **`DomainContentContextBuilder.detect_domain(topic)` output** (shared cross-Cat). Cat B reads confidence + domain via `_detect_domain` at v2 :195-205.
- **`AgentRouter.AGENT_MAP` — NOT READ.** DecisionEnforcerAgent `spawn_tasks_from_mandate` at :460 does NOT validate `spawned.agent` against AGENT_MAP before `queue_agent_task.delay(agent_name=spawned.agent, ...)`. Blast radius per §1 finding #3.

### 8.4 Retention + lifecycle findings

- **`DeliberationSession` retention unbounded** (§1 finding #7 MED). No TTL, no archival. Table grows monotonically. Migration 0283 added `failure_reason_code` + `failure_detail` for classification but no cleanup task references either field.
- **`ContractRecord` retention** = same as parent `DeliberationSession` (CASCADE).
- **`SelfBlog.stats_snapshot['deliberation']` retention** = same as parent `SelfBlog`. No separate lifecycle.
- **Reviewer verdict `top_issues` details** — retention = ZERO (never persisted). Debugging Cat B post-hoc requires replay from ConversationOrchestrator turn traces (`DeliberationTurn.content` at `models_deliberation.py:163-202`) but Skeptic/FactCheck/Domain verdicts do NOT fire as DeliberationTurn rows — they fire inside `run_reviews` which is not turn-tracked by orchestrator (orchestrator tracks the SUBSEQUENT critique conversation, not the preceding reviewer panel).

### 8.5 D62 data-ownership mini-schema (four-item, propagated upfront)

| Surface | (a) canonical/parallel-sibling/shared-container | (b) pre-publish/cross-boundary/downstream | (c) integration posture requirement | (d) island posture requirement |
|---------|--------------------------------------------------|-------------------------------------------|-------------------------------------|---------------------------------|
| `ExecutionMandate` (Cat B-owned transient + ContractRecord dict) | canonical (single schema) | pre-publish + cross-boundary (spawn tasks reach outside Cat B) | make status field lifecycle-transitional; add explicit COMPLETED/KILLED updater | keep parallel per lane |
| Reviewer verdict payloads (Cat B-owned transient; discarded) | parallel-sibling (2 or 3 verdicts per run) | pre-publish | ADD persistence (Cat B-owned `ReviewerVerdict` model or extend `DeliberationTurn.role='reviewer'` rows) | keep transient; no persistence |
| `SelfBlog.stats_snapshot['deliberation']` (Cat D-owned; Cat B writes) | parallel-sibling to Deliverable.metadata (S1601 §9.1 D65a evidence input; F1 canonicalization-debt) | downstream (Cat D owns; Cat B upstream writer) | migrate write to `Deliverable.metadata` canonical path via `deliverable_factory` | keep write-to-SelfBlog; add per-variant write |
| `DeliberationSession` (shared container; Cat A + Cat B co-tenant; unbounded retention) | shared-container | cross-boundary | ADD TTL + archival policy; parameterize `session_type` for per-lane subtypes | parallel-sibling per lane (each lane owns own retention) |

---

## 9. Integrations With Other Domains

### 9.1 INBOUND (Cat B consumes)

- **Cat A → Cat B (claims_pack + draft).** `claims_pack` (or None) + `draft_text` + `topic` passed to `run_reviews` at v2 :228. Cat B graceful-degrades when `claims_pack=None` (empty claims_block, reviewers still fire). Cat A's `claims_count > 0` gate at runner :99-105 is Cat A's post-decision downgrade — not a Cat B input gate.
- **Cat A → Cat B (rewrite loop return).** `context['review_feedback']` + `context['original_draft']` at runner :318-319 → ContentWriterAgent REWRITE MODE. Session 1098 PR-A comment at :307-310 pins the contract explicitly.
- **`ConversationOrchestrator` critique conversation → `DecisionEnforcerAgent`.** Auto-trigger sites at orchestrator :1247-1249 (primary) + :1268-1284 (fallback). Cat B is downstream consumer of orchestrator's decision_summary output OR fallback last-N-messages synthesis.
- **`DomainContentContextBuilder.detect_domain` → v2 `_detect_domain`.** Confidence semantics: `min(max_score/5.0, 1.0)` at `domain_content_context.py:141` — keyword-count-based (5+ matches = full confidence). Threshold `>= 0.2` at v2 :201 gates DomainPersonaReviewer dispatch. Topic doc `content-pipeline.md:75` documents the threshold correctly but does NOT document the underlying keyword-count algorithm (documentation gap per §11.4).

### 9.2 OUTBOUND (Cat B emits)

- **Cat B → Cat A rewrite loop.** `required_changes` (List[str]) per reviewer → feedback_lines[:3] → `context['review_feedback']` → ContentWriterAgent REWRITE MODE. **Sole feedback consumer.** Grep confirms no other consumer of `required_changes` or `top_issues` outside runner `_rewrite_draft` path.
- **Cat B → Cat C PublishGate.** `decision` (PUBLISH / REVISE / KILL) + `blog` object → Step 8 `PublishGate.apply_to_blog(blog)` at runner :138-160. Cat C consumes decision keyword + blog full_text / sections / meta_description / tags / stats_snapshot; Cat C does NOT consume reviewer `top_issues` or `required_changes` (independent re-evaluation via quality/novelty/structure thresholds at `publish_gate.py:44-49`).
- **Cat B → Cat D SelfBlog persistence.** `deliberation_meta` dict at runner :381-389 → `SelfBlog.stats_snapshot['deliberation']` at :415. Single write per S1601 F5 fold. Cat D S1603 will own the Deliverable-canonicalization posture decision for this write.
- **Cat B → cross-domain task spawn (DECAYED / DEAD CODE).** `DecisionEnforcerAgent.spawn_tasks_from_mandate` at :444-477 imports missing `queue_agent_task` from core.tasks — no production callers found (grep-verified) — code path exists but not exercised. Owed to xx99 §5 for dispositional decision.

### 9.3 CROSS-DOMAIN (write-only-forgotten / integration gaps)

- **Cat B ↔ Learning-loop / Memory (Group 1300).** ZERO connection grep-verified. DecisionEnforcerAgent mandate outcomes + reviewer verdicts never write to `AgentMemory` / `AgentPerformance` / `LearningPattern`. No FK from AgentPerformance to `mandate_id` / DecisionEnforcerAgent execution. `DeliberationSession` has no FK to memory-domain models. **Pattern: write-only-forgotten (extends S1502 §14.3 SignalCluster pattern_type consumer-side gap COMPLETED 6-arc pattern to Cat B learning-loop side).**
- **Cat B ↔ Signal Engine.** Reviewer verdicts (PASS/REVISE/FAIL) do NOT contribute back to `SignalCluster` health / scoring. Cat B consumes SignalClusters transitively via ClaimsPack (Cat A reads at `claims_pack_builder.py:76-77`) but does not emit verdicts back. **Same write-only-forgotten pattern.**
- **Cat B ↔ Discord.** ZERO. DecisionEnforcerAgent spawned_tasks priority + mandate decisions not broadcast to Discord. `discord_notifications.py:36-47` has 10+ CHANNEL_* constants; NONE receive Cat B events per grep.
- **Cat B ↔ Revenue (S1402 F.B1 pattern check).** **CONFIRMED same pattern.** Cat B mandate + verdicts have NO outbound channel (see §6.4 Rigby / PA-tool coverage gap #4). Same write-only-forgotten pattern as S1402 F.B1 Revenue OutreachDraft delivery ZERO outbound channel HIGH. **Extends S1402 F.B1 pattern to content Cat B — CONFIRMED HIGH.**
- **Cat B ↔ Employee OS.** No Content Employee analog exists (parent §6.4 parked issue). DecisionEnforcerAgent is a floating agent, not owned by an `AIEmployee` per `core/employees/jobs.py`. Cat F S1606 evidence-plan input.
- **Cat B ↔ Frontend.** BlogViewerPage renders `stats_snapshot` generically (no verdict-specific UI). Grep-verified.

### 9.4 Cross-arc pattern matches (updated)

| Pattern | Source | Cat B applicability | Status |
|---------|--------|---------------------|--------|
| S1274 EventBus "dormant" vs "partially adopted" | S1274 | v1 `ContentReviewPanel` — post-Explore grep prevented dormant mislabel | CONFIRMED PARTIALLY-ADOPTED-LIVE-SECONDARY (§5.2) |
| S1502 §14.3 SignalCluster consumer-side gap 6-arc COMPLETED | S1502 → S1601 §9.2 | Cat B learning-loop consumer-side gap — reviewer verdicts never feed back to Signal/Memory | CONFIRMED (§9.3) |
| S1601 §15.2 F2 fold silent partial-source (MEDIUM → HIGH) | S1601 F2 | v2 `draft[:8000]` silent truncation | CONFIRMED HIGH (§1 finding #2) |
| S1402 F.B1 ZERO outbound channel HIGH | S1402 | Cat B mandate + verdicts have zero PA-tool / Discord / notification surface | CONFIRMED HIGH (§1 finding #4) |
| S1601 §15.1 UNK-2 LLM-prompt-only citation | S1601 UNK-2 | Extended to end-to-end A+B — Cat B FactCheckReviewer is LLM prompt only | CONFIRMED HIGH (§1 finding #1) |
| S1501 D62 4-item mini-schema | S1501 → S1600 D68 F8/F10 | Applied at §4.8 + §5.6 + §6.5 + §8.5 upfront | APPLIED |

---

## 10. Event Flows

Sequential events fired during a single `ContentDeliberationRunner.run_blog(topic, voice)` invocation, Cat B slice:

```
1. runner.run_blog(topic, voice) called via one of three entry paths:
   - REST: POST /api/v1/research/self-blog/generate-v2/ (views_research_demo.py:1106)
   - PA:   blog_tool.generate no-topic → _handle_generate_blog (td_handlers_content.py:1480)
   - Task: generate_self_blog_deliberation_task.delay() (tasks.py:5758)
     └─ tasks_content.py:2540 → ContentDeliberationRunner().run_blog(topic, voice)

2. [Cat A Step 1] claims_pack = get_claims_pack_builder().build(topic)
   - Optional (Cat B tolerates None)

3. [Cat A Step 2] draft_text, generated_content = self._generate_draft(topic, claims_pack, voice)
   - ContentWriterAgent.execute
   - On empty draft: return with failure_reason_code='DRAFT_FAILED'

4. [Cat B Step 3] self._run_review_conversation(draft_text, claims_pack, topic)
   4a. domain = _detect_domain(topic)  # v2 :195-205
   4b. review_results = run_reviews(draft_text, claims_pack, topic, domain)  # v2 :208-256
       - fires SkepticReviewer (gpt-4.1-mini)
       - fires FactCheckReviewer (gpt-4.1-mini)
       - fires DomainPersonaReviewer if domain != 'general' AND confidence >= 0.2 (gpt-4.1-mini)
       - each: draft[:8000] SILENT TRUNCATION (§1 finding #2)
       - failure branches → synthetic FAIL payload
   4c. review_summary_lines built at runner :230-239
   4d. conv_result = ConversationOrchestrator.generate_conversation(
         agent1=EditorAgent, agent2=ContentStrategyAgent (hardcoded, §1 finding #5),
         conversation_type='critique', num_turns=4, topic=review_block+draft[:3000])
       ├─ 4 orchestrator turns
       ├─ ENABLE_DECISION_ENFORCEMENT=True + critique → _enforce_decision auto-triggered
       ├─ _enforce_decision → DecisionEnforcerAgent.execute
       │  ├─ _summarize_debate + hint extraction
       │  ├─ LLM call gpt-5.2 max_completion_tokens=2000
       │  ├─ _parse_mandate → ExecutionMandate (with validate())
       │  └─ return AgentResult(data={mandate: mandate.to_dict(), ...})
       └─ ContractRecord.objects.create(contract_type='execution', contract_data=...)
          at orchestrator :1341-1343
   4e. session_id, mandate_dict extracted at runner :261-262

5. [Cat B Step 4] decision = self._extract_decision(mandate_dict, review_results)  # runner :266-284
   Tier 1: mandate_dict['chosen_path'] keyword match → PUBLISH / KILL / REVISE
   Tier 2: reviewer verdict aggregate → all-PASS/PUBLISH, any-FAIL/REVISE
   Tier 3: default REVISE

6. [Cat B/A boundary] Downgrade gate at runner :99-105
   IF decision=='PUBLISH' AND claims_count==0: decision = 'REVISE'

7. [Cat B Step 5] IF decision=='REVISE': rewrite = self._rewrite_draft(...)  # runner :107-116
   - Single iteration
   - feedback_lines from review_results[].required_changes[:3]
   - ContentWriterAgent REWRITE MODE via context keys
   - On empty feedback / failure: preserve original draft

8. [Cat A Step 6] IF session_id AND claims_pack: self._append_claims_to_evidence(session_id, claims_pack)
   - evidence_pack_builder.append_source + append_claims

9. [Cat B/D handoff Step 7] blog = self._save_blog(...)  # runner :351-422
   - deliberation_meta at :381-389 (session_id, decision, claims_count, sources_count, reviewers, review_verdicts)
   - SelfBlog.objects.create(stats_snapshot={'deliberation': deliberation_meta}) at :415

10. [Cat C Step 8] IF decision=='PUBLISH' AND blog: gate_result = self._run_publish_gate(blog)  # runner :137-160
    - Cat C ownership (S1604 audit scope)

11. [Cat B → Cat E boundary — ABSENT] No PA-tool notification, no Discord broadcast, no WebSocket stream.
    (§9.3 write-only-forgotten pattern)
```

**Not fired in production event flow:** `DecisionEnforcerAgent.spawn_tasks_from_mandate` at :444-477 (dead-code per §7.2 branch 8 grep-verified).

---

## 11. Existing Documentation

### 11.1 Topic doc coverage

`docs/topics/content-pipeline.md` (Session 1147, "drift-labeled") covers Cat B at:
- Line 9 "3-reviewer panel" (LOW drift — actual: 2-or-3 conditional).
- Lines 67-81 3-Reviewer Panel section: SkepticReviewer + FactCheckReviewer + DomainPersonaReviewer named; verdict shape `{verdict, top_issues, required_changes, confidence}` documented.
- Line 75 DomainPersonaReviewer confidence threshold `>= 0.2` (CLEAN — matches v2 :201).
- Line 79 synthetic-FAIL handling ("Invalid reviewer output → synthetic FAIL verdict (never skipped)"; matches v2 :69-83).
- Line 81 LLM model `gpt-4.1-mini` (CLEAN — matches v2 :162).
- Lines 83-87 DecisionEnforcer + ExecutionMandate + forbidden phrases.
- Lines 89-91 rewrite pass single iteration (CLEAN — matches runner :107-116).
- Lines 160-164 v1/v2 coexistence documented; v2 endpoint named.

**Silent on:**
- Per-claim `[C-xxxxxxxxxx]` regex enforcement (correctly silent per §1 finding #1 — no such enforcement exists).
- 8000-char draft truncation at v2 :236 (docs claim reviewers see full draft; NOT documented as silent-partial).
- DecisionEnforcer timeout / gpt-5.2 model / max_completion_tokens=2000 (docs silent on DecisionEnforcerAgent model choice).
- `queue_agent_task` MISSING from core/tasks.py (docs cite it as if it exists).
- `DomainContentContextBuilder.detect_domain` confidence semantics (`min(match_count/5.0, 1.0)` at :141 — algorithm not documented).

### 11.2 Prior audit coverage

`docs/audit-2026/04-content-pipeline.md` April 2026 audit:
- STAGE 3 (lines 66-81) — 3-Reviewer panel + confidence threshold + synthetic-FAIL.
- STAGE 4 (lines 83-91) — editorial debate via ConversationOrchestrator + EditorAgent + ContentStrategyAgent + 4 turns + ExecutionMandate.
- STAGE 5 (lines 93-100) — REVISE → single rewrite via `_rewrite_draft`.
- Truth gap §10 note: "Reviewer verdicts: Not stored in DeliberationSession metadata (0 sessions have review_verdicts)" — matches §4.5 persistence-loss finding.
- Pipeline decisions sampled: 3 REVISE / 0 PUBLISH / 0 KILL — low sample; most pre-v2 blogs.

### 11.3 Patent disclosures

`docs/patents/DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md` — **Cat B-primary patent provenance:**
- §5 Layer 2 lines 101-141: DecisionEnforcerAgent (528 lines — matches runtime 526) + forbidden phrases + ExecutionMandate structure (12 fields) + fallback decision-enforcement fallback pattern (lines 1265-1298 orchestrator per audit-2026 — matches :1247-1284 runtime).
- §5 Layer 3 lines 142-194: Governance escalation (`HumanAttentionItem`) + watch-and-verify mode.
- §6 Novelty at line 140: "creates `queue_agent_task.delay()` with context including `mandate_id`, `mandate_owner`, `deadline`, `priority`" — **patent claim assumes `queue_agent_task` exists; §1 finding #3 MISSING invalidates the operational claim.**
- §6 Novelty lines 227-239: Forbidden-phrase blocking + ExecutionMandate kill criteria + ML override tracking + disagreement-as-alpha.

`docs/patents/DISCLOSURE_D_CLAIMS_BASED_DELIBERATION.md` — Cat A-primary; Cat B secondary through FactCheckReviewer claim-ID validation at §5 Step 3 lines 66-81 + synthetic-FAIL at line 63.

### 11.4 Prior handoffs

Cat B-relevant handoff sessions found via grep of `docs/handoffs/` for `DecisionEnforcerAgent | ContentReviewPanel | content_review_panel | SkepticReviewer | FactCheckReviewer | DomainPersonaReviewer | ExecutionMandate`:
- **SESSION_872**: DecisionEnforcerAgent introduction ("missing prefrontal cortex" per docstring lines 5-11). 9 PRs merged.
- **SESSION_873**: `ENABLE_DECISION_ENFORCEMENT` flag flip; auto-trigger wiring.
- **SESSION_960**: critique auto-trigger + fallback path.
- **SESSION_961**: v1 `ContentReviewPanel` introduction; 6-stage class-based flow.
- **SESSION_962**: `DeliberationSession` model landing (migration 0232).
- **SESSION_963**: `EvidencePackBuilder` at `evidence_pack_builder.py` landing.
- **SESSION_964**: Full v2 six-step deliberation pipeline arc — Cat A + Cat B + Cat C integration.
- **SESSION_988**: LLM provider registry migration (`core.llm_providers` → `core.services.llm_provider_registry`).
- **SESSION_1077**: blog_tool split from content_tool.
- **SESSION_1098** PR-A: rewrite mode explicit context keys per runner :307-310 comment.
- **SESSION_1147**: topic doc `content-pipeline.md` refresh.
- **SESSION_1163**: `governance_tool` consolidation.
- **SESSION_1600**: Group 1600 arc open + parent scoping.
- **SESSION_1601**: Group 1600 Cat A audit + §20.6 Cat B handoffs.

### 11.5 Narrative + inventory anchor Cat B coverage

- `docs/PLATFORM_WHAT_IT_IS.md` § Content Pipeline (lines 234-248) — 3-reviewer panel + DecisionEnforcer + rewrite documented. § "The Unique Stuff (The IP)" item 2 (lines 393-394): "Multi-Reviewer Deliberation with Synthetic-FAIL Fallback" IP claim.
- `docs/PLATFORM_INVENTORY.md` — DecisionEnforcerAgent registered in Agents section (Group 1600 count preserved by autoblock refresh via `refresh_doc_inventory_blocks`).

### 11.6 Prior research library entries

- S1601 sibling audit (§5 services + §6 APIs + §9 integrations + §14 drift + §15 debt Cat B-tagged rows).
- S1600 parent scoping §3 B (Cat B boundary + Q1/Q2).
- S1501-S1506 sports arc — no direct Cat B analog (sports has DecisionEnforcer via `betting_content` lane but not the 3-reviewer panel).
- S1401-S1406 revenue arc — S1402 F.B1 ZERO outbound channel precedent (cross-arc pattern match §9.4).
- S1274 EventBus lesson — applied to v1 classification (§5.2).

---

## 12. Research Coverage

### 12.1 What S1602 adds beyond S1601 + patents + topic doc

- **Q1 dispatch shape resolution** (parent §3 B open at S1600). Pure-function + module-level; NOT class-based. (§1 + §5.1)
- **Q2 v1 vs v2 canonicalization posture** (parent §6.1 open at S1600). v2 canonical for deliberation pipeline; v1 PARTIALLY-ADOPTED-LIVE-SECONDARY. (§1 + §5.2)
- **S1601 §15.1 UNK-2 fully resolved.** End-to-end citation integrity across A+B is LLM-prompt-only — CONFIRMED HIGH. (§1 finding #1)
- **S1601 §15.2 F2 silent partial-source pattern extended.** 8000-char draft truncation matches pattern — CONFIRMED HIGH. (§1 finding #2)
- **S1402 F.B1 ZERO outbound channel pattern extended to Cat B.** CONFIRMED HIGH. (§1 finding #4 + §9.3)
- **NEW CRITICAL bug: `queue_agent_task` MISSING.** Not covered by any prior audit, patent, or handoff. (§1 finding #3)
- **NEW MED: hardcoded critique agents.** Not covered. (§1 finding #5)
- **NEW MED: single-iteration rewrite pass, no convergence, no re-invoked mandate.** Not covered as debt (topic doc documents as feature). (§1 finding #6)
- **NEW MED: DeliberationSession retention unbounded.** Not covered by audit-2026 or S1601. (§1 finding #7)
- **NEW MED: `_detect_domain` confidence keyword-count algorithm undocumented.** Topic doc silent on `min(match_count/5.0, 1.0)`. (§9.1 + §11.4)
- **v2 reviewer verdict schema persistence-loss** (top_issues + required_changes + suggested_edits discarded post-`_extract_decision`). (§4.5 + §4.7)

### 12.2 What remains uncovered (deferred)

- **Runtime failure rate of synthetic-FAIL verdicts** — no metrics endpoint. Deferred to Cat E S1605 (ops observability) or dedicated Cat B ops audit post-arc.
- **DecisionEnforcer real-world mandate frequency** (does it ever produce PUBLISH vs REVISE? Audit-2026 says 3 REVISE / 0 PUBLISH / 0 KILL sampled). Deferred to Cat C S1604 (PublishGate real-world outcomes).
- **v1 ContentReviewPanel real-world usage rate** (how often is ContentWriterAgent direct-write path called vs deliberation runner?). Deferred to Cat E S1605 tool-surface investigation.
- **`spawn_tasks_from_mandate` production usage rate** (grep says dead-code; runtime tracing would confirm). Deferred to xx99 §5 for dispositional call.
- **`gpt-5.2` model tuning** — used across 14 files; is DecisionEnforcerAgent's use consistent with platform-wide behavior? Deferred to LLM routing audit.

---

## 13. Architecture Maturity

Per-piece maturity verdict with evidence:

| Cat B piece | Verdict | Supporting evidence |
|-------------|---------|---------------------|
| v2 reviewer panel (Skeptic + FactCheck + Domain conditional) | **WORKING** | Deployed via all 3 trigger paths (S1601 Q2 confirmed). NOT STABLE: (a) LLM-prompt-only citation contract unverified (§1 #1); (b) silent 8000-char truncation (§1 #2). |
| DecisionEnforcerAgent | **WORKING** | Session 872 introduction; auto-triggers via ConversationOrchestrator :1247/:1273. NOT STABLE: (c) `spawn_tasks_from_mandate` unhandled ImportError on missing `queue_agent_task` (§1 #3 CRITICAL); (d) no AGENT_MAP validation on LLM-picked agent names. |
| Rewrite pass (single-iteration) | **PARTIAL** | Executes once at runner :107-116; no convergence loop; DecisionEnforcer NOT re-invoked post-rewrite; blog lands in `needs_enhancement` per Session 1007 comment :167. Recovery envelope depends on external `auto_enhance_blogs` beat (Cat C S1604 scope). |
| v1 `ContentReviewPanel` | **PARTIALLY-ADOPTED-LIVE-SECONDARY** | Grep-verified live consumer at ContentWriterAgent :1376-1377 under `ENABLE_CONTENT_REVIEW=True` guard (:62). v2 pipeline uses v2 exclusively (runner :225). Dual-path architecture — not dormant per S1274 lesson. |
| Synthetic-FAIL payload contract | **STABLE** | Deterministic (v2 :69-83); 4 exception branches (v2 :167, :182-183, :188-189, :190-192) all map to same payload; consumer well-tested (test_content_review_panel.py exists); doc `content-pipeline.md:79` accurately describes. |
| `MandateStatus` enum lifecycle | **PARTIAL (dormant state machine)** | Enum defined at execution_mandate.py :51-65; `mark_killed` at :404-407 + `mark_completed` at :409-411 CODED but ZERO callers in deliberation flow (F4 fold pre-commit — Rigby Batch B/C Q4-#3 grep-verified). Contract in patent (DISCLOSURE_F §5 Layer 2) supports transitions; deliberation flow doesn't drive them. |
| Confidence/deadline defaults | **PARTIAL** | Default 7 days at :406; "Nd" parser at :407-410; default confidence 0.6 at :432. Works but no config; not environment-tunable. |
| `DeliberationSession` retention | **PARTIAL** | Model + failure classification (migration 0283) STABLE; retention policy ABSENT. Table grows monotonically. |

**Overall Cat B maturity: WORKING (deployed, three trigger paths, verdicts persist, decision extraction robust) but NOT STABLE (three HIGH/CRITICAL structural findings + one CRITICAL runtime bug).**

---

## 14. Known Drift

Doc-vs-runtime drift with severity + cross-arc precedent alignment.

| # | Doc claim (file:line) | Runtime reality (file:line + observed) | Severity | Cross-arc precedent |
|---|----------------------|----------------------------------------|----------|---------------------|
| 14.1 | `docs/topics/content-pipeline.md:9` "3-reviewer panel" | 2 or 3 reviewers per run (Skeptic + FactCheck + optional Domain per v2 :247-254) | LOW numeric | S1502 §14.3 pattern (numeric drift, no consumer impact) |
| 14.2 | `content-pipeline.md:75` "confidence >= 0.2" | Confirmed at v2 :201 | CLEAN | verified |
| 14.3 | `content-pipeline.md:91` "rewrites once" | Confirmed at runner :107-116 single-iteration | CLEAN | verified |
| 14.4 | `content-pipeline.md:79` synthetic-FAIL never-skip | Confirmed at v2 :69-83 payload + :167/:182-183/:188-189/:190-192 exception branches | CLEAN | verified |
| 14.5 | `content-pipeline.md:81` "gpt-4.1-mini" reviewers | Confirmed at v2 :162 | CLEAN | verified |
| 14.6 | `DISCLOSURE_F.md:140` "creates `queue_agent_task.delay()`" (patent operational claim) | `queue_agent_task` MISSING FROM core/tasks.py (grep-verified) | HIGH semantic | S1274 EventBus dormant-vs-partial adjudication — patent claim doesn't match runtime |
| 14.7 | `content-pipeline.md` silent on 8000-char truncation | `draft[:8000]` at v2 :236 silently truncates | HIGH semantic (documentation absence + silent behavior) | S1601 §15.2 F2 silent-partial-source pattern |
| 14.8 | `content-pipeline.md` silent on DomainContentContextBuilder confidence algorithm | `confidence = min(max_score/5.0, 1.0)` at `domain_content_context.py:141` — keyword-count-based | MED (algorithm undocumented) | Documentation coverage gap only |
| 14.9 | v2 module docstring :4 "3 structured reviewers" | 2 or 3 dispatched | LOW internal-doc | matches 14.1 |
| 14.10 | `audit-2026/04-content-pipeline.md` §10 "0 sessions have review_verdicts" | Reviewer top_issues + required_changes never persisted; only aggregate verdicts land in `SelfBlog.stats_snapshot['deliberation']['review_verdicts']` | MED gap (not drift — design absence) | matches §4.5 persistence-loss finding |
| 14.11 | `content-pipeline.md` silent on hardcoded critique agents | `content_deliberation_runner.py:252-253` hardcodes EditorAgent + ContentStrategyAgent | MED (documentation absence) | matches §1 finding #5 |
| 14.12 | `DISCLOSURE_F` ExecutionMandate status lifecycle transitions | No coded transitions — status write-once at construction | MED (patent-vs-runtime) | Same class as 14.6 |

**Post-xx99 validator rig-up candidates** — 14.6 (patent claim invalidated by missing task) + 14.7 (silent truncation) + 14.11 (hardcoded critique agents) + 14.12 (lifecycle transitions).

---

## 15. Known Technical Debt

### 15.1 HIGH — CONFIRMED: end-to-end LLM-prompt-only citation contract (extends S1601 §15.1 UNK-2)

Cat A `claims_count > 0` at runner :99-105 is binary; Cat B FactCheckReviewer at v2 :107-122 is LLM prompt-only. NO code-side per-claim `[C-xxxxxxxxxx]` regex / URL-map validator in either category. Hallucinated / misattributed citations pass both gates. Owed to xx99 D65b evidence plan (T1 R.CONTENT.CITATION-INTEGRITY).

Rationale: **truth/evidence integrity across A+B is LLM-verified, not code-enforced.** Impact: any blog published via v2 pipeline could cite non-existent evidence links without code-level detection.

Cross-arc precedent: S1601 §15.1 UNK-2 → S1602 resolved to CONFIRMED HIGH.

### 15.2 HIGH — Silent draft truncation at 8000 chars (extends S1601 §15.2 F2 fold)

`draft[:8000]` at v2 :236 silently slices user_content prompt without warning / log / top_issues entry. 1500-word target drafts exceed threshold → reviewers PASS/FAIL on partial evidence. Same "truth/evidence integrity degradation without explicit degraded-status contract" pattern S1601 F2 elevated MEDIUM → HIGH.

Owed to xx99 D65b evidence plan.

### 15.3 HIGH (latent-landmine) — `queue_agent_task` MISSING task definition (exception-swallowed dead-code path)

`DecisionEnforcerAgent.spawn_tasks_from_mandate` at :444-477 imports `queue_agent_task` at :456 **inside a broad `try/except Exception` block at :455 + :474-476** (F5 fold pre-commit — Rigby Batch B/C Q4-#5 correction). Grep-verified missing definition in `core/tasks.py`. `auto_spawner_service.py:337` has explicit `logger.warning("queue_agent_task not available")` fallback; decision_enforcer's exception handler logs `Failed to spawn tasks: {e}` at :475 and returns empty `task_ids` at :477 — **failure is exception-swallowed silently; no unhandled crash; no user-visible symptom**. Grep-verified NO production callers of `spawn_tasks_from_mandate` (only `enforce_decision_after_synthesis(auto_spawn=True)` at :481 which is not called from runner or orchestrator) — code path exists but appears never-exercised. Combined severity: **HIGH latent-landmine, not CRITICAL active bug** (F6 severity fold Rigby Batch B/C Q5 re-rank). Preserved rationale: invalidates patent operational claim at `DISCLOSURE_F.md:140` ("creates `queue_agent_task.delay()`") + becomes live with a trivial config flip (classic landmine). Two disposition options for xx99 §5:
- (i) Define `queue_agent_task` in `core/tasks.py` + add `agent_name in AGENT_MAP` validation before `.delay()`.
- (ii) Retire `spawn_tasks_from_mandate` + route mandate through Cat E `governance_tool.decision_promote` surface (aligns with Session 1163 governance consolidation).

### 15.4 HIGH — Cat B mandate + verdicts ZERO outbound channel to Rigby (extends S1402 F.B1)

No PA tool surfaces reviewer verdicts / `top_issues` / `required_changes` / mandate `chosen_path` / `reason` / `decision_owner`. Only readback: REST `/api/blog/<uuid>/deliberation/`. Same write-only-forgotten pattern as S1402 F.B1. Owed to Cat E S1605 + xx99 D65a integration-posture input.

### 15.5 MED — Hardcoded critique agents (EditorAgent + ContentStrategyAgent), not domain-aware

`content_deliberation_runner.py:252-253` hardcodes agents; contradicts v2 DomainPersonaReviewer conditional pattern. Two review layers (v2 domain-aware panel + orchestrator domain-blind critique) run in one call. Boundary confusion.

### 15.6 MED — Single-iteration rewrite; no convergence; DecisionEnforcer not re-invoked

`runner :107-116` executes rewrite once if REVISE; no while-loop; DecisionEnforcer not called on rewritten text. Blog lands in `needs_enhancement` (Session 1007). Recovery depends on external `auto_enhance_blogs` beat (Cat C scope).

### 15.7 MED — Reviewer verdict persistence loss

Only aggregate `review_verdicts` (PASS/REVISE/FAIL list) lands in `SelfBlog.stats_snapshot['deliberation']`. `top_issues` + `required_changes` + `suggested_edits` discarded post-`_extract_decision`. Post-hoc debug requires replaying `DeliberationTurn` rows which cover the SUBSEQUENT critique conversation, not the preceding reviewer panel.

### 15.8 MED — DeliberationSession unbounded retention

No TTL / archival / cleanup task. Table grows monotonically across three Cat B deployment paths.

### 15.9 MED — Hardcoded LLM model + params, no config

v2 :162 (`gpt-4.1-mini`, temp 0.3, max_tokens 1500) + decision_enforcer_agent.py:372 (`gpt-5.2`, max_completion_tokens 2000). Different models for reviewers vs mandate. DecisionEnforcer's `max_completion_tokens=2000` may underrun per memory rule `feedback_gpt5_max_completion_tokens_floor.md` (floor 4000).

### 15.10 LOW — `_detect_domain` confidence 0.2 threshold is a magic number (unvalidated tuning knob)

Documented at topic doc :75 but no rationale, no tuning trail, no config knob. Impacts whether 3rd reviewer fires. **F7 fold pre-commit (Rigby Batch B/C Q5 severity re-rank MED → LOW):** a single threshold constant is not automatically debt; classified as **LOW ("tuning knob without design justification")** unless/until empirical evidence of systematic reviewer mis-selection surfaces. If misclassification rate evidence surfaces post-arc, escalate to MED.

### 15.11 LOW — `_call_llm_reviewer` 4-exception-branch synthetic-FAIL hides root cause

v2 :187-192 maps all 4 exception types (JSONDecodeError, LLMError, validation error, generic Exception) to same "reviewer_error" tag. Intended graceful degradation but hides root cause for debugging.

### 15.12 LOW — v2 module docstring line 4 numeric drift

"3 structured reviewers" but code yields 2 or 3. Same as §14.1.

---

## 16. Boundary Violations

### 16.1 Cat B → Cat D SelfBlog persistence write (canonicalization-debt reframe per S1601 F1)

`SelfBlog.objects.create(stats_snapshot={'deliberation': deliberation_meta})` at `content_deliberation_runner.py:415` writes to Cat D-owned model bypassing `deliverable_factory.py:1269` canonical creation path. Same reframe as S1601 F1 fold: canonicalization-debt Cat B/D flag as **D65a evidence input, NOT proof of intentional island architecture**. Chris / xx99 selects posture intent at post-arc ADR; Cat B does not editorialize D65a decision.

**Do-not-regress phrasing (owed to PR review):** preserve F5-equivalent phrasing "Cat B writes to Cat D-owned `SelfBlog.stats_snapshot['deliberation']` at runner :415 — canonicalization debt, evidence input to D65a, NOT proof of intentional island architecture."

### 16.2 Cat B → Cat A rewrite loop (bounded, contract-explicit — NOT a violation)

`context['review_feedback']` + `context['original_draft']` at runner :318-319 is Session 1098 PR-A explicit contract. Cat B owns the feedback contract; Cat A owns ContentWriterAgent REWRITE MODE dispatch. Boundary is well-defined via context keys. Not a violation; documented pattern.

### 16.3 ConversationOrchestrator critique auto-trigger inside Cat B slice (bounded — NOT a violation)

Orchestrator's `_enforce_decision` fires DecisionEnforcerAgent during Cat B `_run_review_conversation`. Wiring is per orchestrator design (Session 873); Cat B consumes the outcome without owning the trigger. Boundary preserved.

### 16.4 `spawn_tasks_from_mandate` cross-scope task queue (BROKEN — §15.3 CRITICAL)

`decision_enforcer_agent.py:460` `queue_agent_task.delay(agent_name=spawned.agent, ...)` would spawn tasks reaching outside Cat B scope if `queue_agent_task` existed. Currently: dead-code path. Disposition owed to xx99 §5.

### 16.5 v1 ContentReviewPanel spider-context injection (bounded — parallel-sibling boundary)

v1 `_get_spider_context` at :208-226 injects SpiderContextBuilder output into critique conversation. v2 does NOT inject spider context. v1 vs v2 dispatch boundary is architectural, not violation. Q2 canonicalization posture decision owed to xx99 D65-analog.

---

## 17. Duplicate or Overlapping Systems

### 17.1 v1 `ContentReviewPanel` vs v2 `content_review_panel_v2` (per §5.2 + Q2 resolution)

Two review dispatch paths coexist:
- v1 (class-based, 2-agent critique + spider context injection + ConversationOrchestrator) — live secondary consumer at ContentWriterAgent direct-write.
- v2 (module-level, 3-reviewer panel + ClaimsPack + no spider context) — canonical for deliberation pipeline.

Same domain-detection logic implemented twice (v1 :173-183 wraps DomainContentContextBuilder + v2 :195-205 wraps + gates confidence >= 0.2).

Same 2-agent critique conversation implemented in two places:
- v1 :232-281 uses ConversationOrchestrator directly for the CritiqueConversation.
- runner :251-259 uses ConversationOrchestrator with hardcoded EditorAgent + ContentStrategyAgent.

Canonicalization posture: **posture-decision-pending** per parent §6.1 parked issue. Owed to xx99 D65-analog.

### 17.2 Cat B reviewer verdict schema vs `DeliberationTurn` payload schema

`validate_review_payload` at v2 :27-66 defines reviewer verdict shape (`reviewer`, `verdict`, `top_issues`, `required_changes`, `suggested_edits`, `confidence`). Separate from `DeliberationTurn.content` (TextField + auto SHA256 `content_hash`) + `DeliberationTurn.contract_state` (JSONField nullable snapshot). Reviewer verdicts do NOT persist as DeliberationTurn rows — schema-level duplication is masked by the fact that reviewer verdicts never land in DeliberationTurn shape. If future refactor persists reviewer verdicts, schema alignment decision is owed.

### 17.3 5-gate DeliverableGatedError vs Cat B reviewer verdicts (parent §6.3 parked issue)

`deliverable_factory.py:46-74` implements 5-gate check (media_stub + smoke_pattern + min_length + template_leak + no_relevance) at Deliverable creation time. Cat B reviewer panel implements 3-reviewer check at post-draft. Same design intent (quality gate) but different scope + timing. Cat D S1603 owns the canonicalization decision.

---

## 18. Ownership Gaps

Per Cat B piece, ownership row per playbook §9 canonical question #25:

| Piece | Design owner | Runtime owner | Ops owner | Doc owner |
|-------|--------------|---------------|-----------|-----------|
| v2 reviewer panel | Session 964 (v2 pipeline arc); Session 961 (Cat A + Cat B combined intro) | BaseAgent + runner | UNDEFINED | topic doc §11.1 (Session 1147) |
| FactCheckReviewer citation contract | Session 964 (implicit via v2 prompt) | v2 :107-122 LLM prompt execution | UNDEFINED | topic doc silent on per-claim regex absence |
| DecisionEnforcerAgent | Session 872 (docstring) + patent DISCLOSURE_F | `decision_enforcer_agent.py:180-282` + orchestrator wiring :1550-1630 | UNDEFINED | topic doc §11.1 (Session 1147) + patent |
| Rewrite pass | Session 1098 PR-A (comment) | runner :286-336 | UNDEFINED | topic doc §11.1 (Session 1147) |
| Synthetic-FAIL | Session 964 (v2 arc) | v2 :69-83 + exception handlers | UNDEFINED | topic doc §11.1 accurate |
| ConversationOrchestrator `_enforce_decision` wiring | Session 873 (flag) + Session 960 (fallback path) | orchestrator :1247/:1273 | UNDEFINED | topic doc silent on wiring path |
| ExecutionMandate schema | Session 872 + patent DISCLOSURE_F | execution_mandate.py + validate() | UNDEFINED | patent primary |
| `spawn_tasks_from_mandate` | Session 872 (docstring intent); patent :140 (aspirational) | decision_enforcer_agent.py:444-477 (BROKEN per §15.3) | UNDEFINED | patent claims exist; runtime absent |
| DeliberationSession retention | Session 962 (introduction) | Django ORM + migration 0283 | UNDEFINED (no cleanup task) | model docstring |
| `_detect_domain` 0.2 threshold | Session 964 (implicit) | v2 :201 | UNDEFINED | topic doc :75 documents value; algorithm undocumented |

**Ops ownership is UNDEFINED across all Cat B pieces.** No explicit oncall / SLA / escalation path. Parent §6.4 Content Employee analog remains posture-decision-pending. Cat F S1606 evidence-plan input.

---

## 19. Recommended Future Research

Ranked queue for xx99 §5 evidence plan + post-arc T-slot allocation.

### 19.1 T1 — CRITICAL / HIGH — post-arc ADRs owed

| T-slot | Debt/Finding | Rationale | Precedent |
|--------|--------------|-----------|-----------|
| R.CONTENT.RAG-SCOPE | §1 finding S1601 #1 (Rigby-verified riskiest overall) — extended by S1602 via workspace-scope Cat B verdict inheritance | Riskiest overall Group 1600 finding; cross-tenant/workspace exposure | S1601 F4 fold RIGHIEST tag |
| R.CONTENT.CITATION-INTEGRITY | §15.1 CONFIRMED HIGH — end-to-end LLM-prompt-only citation contract | Structural absence of code-side per-claim verifier across A+B | S1601 §15.1 UNK-2 → S1602 CONFIRMED |
| R.CONTENT.CAT-B-TRUNCATION | §15.2 HIGH — silent 8000-char draft truncation | Reviewers PASS/FAIL on partial evidence without contract | S1601 F2 fold pattern extended |
| R.CONTENT.CAT-B-SPAWN-TASKS | §15.3 CRITICAL — `queue_agent_task` MISSING; unhandled ImportError pathway | Two dispositions (fix vs retire); patent operational claim invalidated | NEW at S1602 |
| R.CONTENT.CAT-B-OUTBOUND | §15.4 HIGH — ZERO PA-tool / Discord / notification channel for verdicts + mandate | Same write-only-forgotten pattern as S1402 F.B1 | S1402 F.B1 pattern extended |

### 19.2 T2 — MED — post-arc follow-on

- R.CONTENT.CAT-B-HARDCODED-CRITIQUE: parameterize orchestrator critique agents to be domain-aware.
- R.CONTENT.CAT-B-REWRITE-CONVERGENCE: multi-iteration rewrite with re-invoked DecisionEnforcer.
- R.CONTENT.CAT-B-VERDICT-PERSISTENCE: add `ReviewerVerdict` model OR extend `DeliberationTurn.role='reviewer'` rows to preserve top_issues + required_changes.
- R.CONTENT.CAT-B-SESSION-RETENTION: TTL / archival policy for `DeliberationSession`.
- R.CONTENT.CAT-B-MODEL-CONFIG: environment-tunable model + temp + max_tokens for reviewer + DecisionEnforcer.
- R.CONTENT.CAT-B-DOMAIN-THRESHOLD-TRAIL: document 0.2 tuning rationale + config knob.

### 19.3 T3 — LOW — post-arc

- R.CONTENT.CAT-B-DOCSTRING: fix v2 :4 numeric drift (2-or-3, not 3).
- R.CONTENT.CAT-B-EXCEPTION-CLASSIFICATION: distinguish exception types in synthetic-FAIL for debug clarity.

### 19.4 Post-xx99 anchor-update recommendations owed

- `docs/topics/content-pipeline.md` refresh: add 8000-char truncation caveat + hardcoded critique agents + `queue_agent_task` disposition + `_detect_domain` algorithm note.
- `docs/PLATFORM_INVENTORY.md` — Cat B piece coverage in Services table.
- `docs/patents/DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md`:140 — reconcile patent operational claim vs runtime `queue_agent_task` absence.

### 19.5 Cross-arc handoffs owed

- **To S1603 Cat D:** Cat B write to `SelfBlog.stats_snapshot['deliberation']` at runner :415 is D65a evidence input (§16.1 canonicalization-debt reframe).
- **To S1604 Cat C:** Cat B `decision` → PublishGate boundary; `blog.status='needs_enhancement'` recovery envelope depends on Cat C `auto_enhance_blogs` beat (verify existence).
- **To S1605 Cat E:** Cat B ZERO PA-tool coverage on verdicts + mandate (§15.4); resolution owed by Cat E surface.
- **To S1606 Cat F:** Cat B ZERO learning-loop / memory / signal-engine / Discord outbound (§9.3); cross-domain integration lens.
- **To S1699 xx99:** three axes evidence inputs — D65a (SelfBlog canonicalization write-bypass) + D65b (LLM-prompt-only citation contract) + D65c (lifecycle-transition ownership — MandateStatus never transitions, DecisionEnforcerAgent + spawn_tasks_from_mandate ownership gap).

### 19.6 T-slot ranking table (updated with S1602 findings)

| Rank | T-slot | Group | S1601 rank | S1602 rank | Note |
|------|--------|-------|------------|------------|------|
| #1 | R.CONTENT.RAG-SCOPE | Group 1600 | #1 (Rigby-verified riskiest) | #1 preserved | S1601 F4 elevation |
| #2 | R.CONTENT.CITATION-INTEGRITY | Group 1600 | #2 | #2 preserved | S1602 fully CONFIRMED |
| #3 | R.CONTENT.CAT-B-TRUNCATION | Group 1600 | N/A | **NEW #3 HIGH** | Silent partial-source pattern extended; F6 fold pre-commit moved to #3 |
| #4 | R.CONTENT.CAT-B-SPAWN-TASKS | Group 1600 | N/A | **NEW #4 HIGH latent-landmine** | Patent operational claim invalidated + exception-swallowed silent failure. Severity CRITICAL → HIGH per F6 fold Rigby Batch B/C Q5 (exception-swallowed at :455/:474-476 + zero production callers). Below CAT-B-TRUNCATION because latent (no user-visible impact) vs TRUNCATION (active partial-source review pathway). |
| #5 | R.CONTENT.CAT-B-OUTBOUND | Group 1600 | N/A | **NEW #5 HIGH** | S1402 F.B1 pattern extended |
| #6 | R.CONTENT.SIGNAL-PATTERN-TYPE-CONTRACT | Group 1600 | #3 | #6 shifted down | S1502 §14.3 6-arc pattern |

---

## 20. Appendix

### 20.1 Pre-Explore parent-Claude verifier-loop record (7 load-bearing claims)

Per playbook §14 "trust but verify" rule, parent Claude verified 7 load-bearing pre-Explore claims by direct file:line read before firing the 6 parallel Explore sub-agents.

1. `SKEPTIC_SYSTEM` at `content_review_panel_v2.py:88` — VERIFIED. Module-level constant, not class-based.
2. `FACTCHECK_SYSTEM` at `content_review_panel_v2.py:107` — VERIFIED. Module-level constant. **Key finding surfaced:** LLM prompt-only per-claim `[C-xxxxxxxxxx]` enforcement (no regex verifier).
3. `DOMAIN_SYSTEM_TEMPLATE` at `content_review_panel_v2.py:124` — VERIFIED. Module-level template. Conditional dispatch at :247-254; confidence gate at :201.
4. `run_reviews` dispatch function at `content_review_panel_v2.py:208` — VERIFIED. Module-level function; Q1 resolution.
5. `DecisionEnforcerAgent` class-def at `core/agents/decision_enforcer_agent.py:60` — VERIFIED. BaseAgent subclass; system_prompt at :82; `execute` at :180; `_call_llm_for_decision` at :360 with `gpt-5.2` model at :372 and `max_completion_tokens=2000` at :374.
6. Fallback logic at `content_deliberation_runner.py:266-284` — VERIFIED. Two-tier: mandate keyword-match :270-273 + reviewer verdict aggregate :276-281 + default REVISE :284.
7. Rewrite pass at `content_deliberation_runner.py:107-116` — VERIFIED. Single-iteration; `_rewrite_draft` at :286-336; feedback empty-guard at :295-296; REWRITE MODE context keys :311-320.

### 20.2 Six-parallel-Explore sub-agent fire record

Per playbook §13, six parallel Explore sub-agents fired in single tool-use block:
- Agent 1 — Models + Persistence. Returned ExecutionMandate + MandateStatus + SpawnedTask + DeliberationSession/Turn/ContractRecord/DocVersion inventory + persistence flow + retention findings.
- Agent 2 — Services + Runtime Flows. Returned v2/v1 service inventory + runtime flow diagram + v1 vs v2 consumer grep + DecisionEnforcer wiring + god-service check (no service > 3000 lines).
- Agent 3 — APIs, Tools, Tasks, Commands. Returned REST endpoints (6.1.1-6.1.7) + PA tool coverage gaps + Celery task chain + ZERO Discord/WebSocket/frontend Cat B UI + PA-tool cover map.
- Agent 4 — Integrations + Cross-Domain. Returned inbound/outbound integration map + cross-domain handoffs (memory/signal engine/Discord/revenue/Employee OS) + missing edges + S1402 F.B1 pattern-match confirmation.
- Agent 5 — Documentation + Prior Research. Returned topic doc coverage + audit-2026 coverage + patent disclosure references + prior handoff inventory + drift candidates + explicit "already covered by X" pointers.
- Agent 6 — Drift + Debt + Ownership + Maturity. Returned drift matrix + debt matrix + ownership row + maturity verdict + top-3 riskiest findings + cross-arc precedent alignment.

Parent-Claude synthesis merged findings into §3-§20 with duplicate-finding merge + conflict resolution via direct file:line reads + load-bearing claim spot-check + UNKNOWN honesty per playbook §14.

### 20.3 D62 mini-schema surface application (four-item, propagated upfront per D68 F8/F10)

Second sibling of Group 1600 (after S1601 first) to propagate D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront. Applied at:
- §4.8 (Major Models mini-schema): ExecutionMandate + DeliberationSession + MandateStatus + SelfBlog.stats_snapshot['deliberation'].
- §5.6 (Major Services mini-schema): v2 module dispatch + v1 class + DecisionEnforcerAgent + ConversationOrchestrator._enforce_decision.
- §6.5 (Major APIs mini-schema): REST `/api/blog/<uuid>/deliberation/` + blog_tool/content_tool.generate + governance_tool + missing verdict-readback PA tool.
- §8.5 (Data Ownership mini-schema): ExecutionMandate + reviewer verdict payloads + SelfBlog.stats_snapshot['deliberation'] + DeliberationSession.

Columns aligned to Group 1600's three posture axes per parent D68 F8/F10 folds. Extends 6-arc Group 1500 pattern (S1501-S1506) to Group 1600 second sibling application.

### 20.4 Post-Explore parent-Claude verifier-loop record (3 load-bearing binary claims)

Per playbook §14 "grep-verify binary claims before shipping to Rigby" rule, parent Claude verified 3 post-Explore load-bearing binary claims by direct grep after Explore return.

1. **`queue_agent_task` missing from `core/tasks.py`** — Agent 4 + Agent 6 claim CONFIRMED via `Grep queue_agent_task`. Results: 7 hits total — `decision_enforcer_agent.py:456,460` (unguarded import + call) + `auto_spawner_service.py:321,323,337` (guarded import + call + explicit fallback log line: `logger.warning("queue_agent_task not available")`) + docs references (`agent-system.md:178`, `DISCLOSURE_F.md:140`). ZERO hits in `core/tasks.py`. **CONFIRMED CRITICAL** (§1 finding #3 + §15.3).

2. **`gpt-5.2` model string is/is-not valid internal ID** — Agent 2 flagged SPECULATIVE. Grep of `core/` for `gpt-5\.2|gpt-5-2|gpt-5_2` returns 14 files including `core/employees/jobs.py`, `core/agents/base_agent.py`, `core/services/llm_provider_registry.py`, `core/models_llm_routing.py`, `core/agents/decision_enforcer_agent.py`. **Model string is a valid internal LLM routing target across the platform. Agent 2 SPECULATIVE flag RETRACTED.** Not a bug; standard platform-wide model choice.

3. **v1 `ContentReviewPanel` dormant vs live** — Agent 2 claim "dormant in canonical flow but active via ContentWriterAgent flag." Grep of `core/` for `ContentReviewPanel|content_review_panel[^_]` returns 4 core hits: `content_writer_agent.py:1376-1377` (live instantiation inside `if ENABLE_CONTENT_REVIEW:` guard) + `test_content_review_panel.py:12,25` (test only) + `content_review_panel_v2.py:9` (module docstring reference) + `content_review_panel.py:61,217` (class def + self-reference). Grep of `core/` for `ENABLE_CONTENT_REVIEW` returns `content_writer_agent.py:62 ENABLE_CONTENT_REVIEW = True` + `:1374 if ENABLE_CONTENT_REVIEW:`. **Classification refined to PARTIALLY-ADOPTED-LIVE-SECONDARY** — Agent 2's "dormant in canonical flow" is accurate for the deliberation pipeline; but the "PARTIALLY-ADOPTED-DORMANT" label from Agent 6 was too weak. S1274 EventBus dormant-vs-partial lesson properly applied — v1 is live secondary consumer, not dormant.

### 20.5 Rigby SIGN cycle 1 fold notes (recorded post-SIGN)

**Fresh SIGN isolation pin:** `pa-1c5298d807d7a1d2` minted 2026-07-02 per playbook §15. Full SIGN Q1-Q9 pressure-test executed in 4 turns (3 batches + 1 final-verdict follow-up).

Batching per memory rule `feedback_rigby_sign_worker_instability_recovery.md`: 3-batch SIGN pattern (Batch A/C Q1-Q3 boundary/overstatement/understatement + Batch B/C Q4-Q6 intentional-separation/debt/riskiest + Batch C/C Q7-Q9 top-3-ranking/factual-errors/final-verdict) to prevent turn-2 stall on 965-line audit.

**Batch A/C outcome:** Substantive SIGN response. Q1 no missed Cat B parts; F1 tightening (Cat B decision-production substrate framing at §5.5) + F2 tightening (`_extract_decision` Cat B-OWNED tag at §3.5) + F3 caveat (§1 "all v2 deliberation deployment paths" scope, v1 direct-write excluded). Q2 no maturity overstatements confirmed. Q3 no understatements — actively cautioned against upgrading DecisionEnforcerAgent to STABLE.

**Batch B/C outcome:** Substantive SIGN response with 2 grep-verified factual corrections:
- **F4 (Q4-#3):** MandateStatus `mark_killed` at execution_mandate.py:404-407 + `mark_completed` at :409-411 EXIST — the "no coded transitions" claim was WRONG. Reframed as "dormant state machine (contract supports transitions but deliberation flow doesn't drive them), not missing machinery."
- **F5 (Q4-#5):** `spawn_tasks_from_mandate` at decision_enforcer_agent.py:455-476 DOES wrap import+call in broad `try/except Exception` guard (:474-476 catches + logs `Failed to spawn tasks: {e}`) — the "unhandled ImportError crashes caller" claim was WRONG. Reframed as "exception-swallowed silent failure with no user-visible symptom."
- Q5 severity re-ranks: **F6** §15.3 CRITICAL → HIGH latent-landmine (preserving landmine + patent-claim-invalidation rationale); **F7** §15.10 MED → LOW (unvalidated tuning knob without misclassification evidence).

**Batch C/C outcome:** Partial SIGN. Rigby deflected to doc-summary + offered to address Q7-Q9 later (worker-load pressure — not full stall per `feedback_rigby_sign_worker_instability_recovery.md` since prior 2 turns were substantive). Grep-verified additional claims (panel_failed at runner :93/:377, REST endpoint routing at urls.py:3230, blog_deliberation_detail at views_deliberation.py:322+, blog_tool.generate at td_handlers_content.py:170-175) confirming §6.1/§6.2 accuracy. **Follow-up single-question turn** to pin `pa-1c5298d807d7a1d2` requesting explicit Q9 verdict returned in <10 seconds:

> **"SIGN-with-edits (7 folded) — High confidence."**

**F1-F7 folds landed pre-commit:**

- **F1** (§5.5 title + paragraph) — ConversationOrchestrator critique conversation reframed from "Cat B wiring" to "**Cat B decision-production substrate** — where the ExecutionMandate driving Cat B's PUBLISH/REVISE/KILL is actually minted." Preserves patent DISCLOSURE_F §5 Layer 2 provenance.
- **F2** (§3.5 canonical entry point row) — `_extract_decision` at runner :266-284 explicitly tagged **Cat B-OWNED** decision extraction, not "runner glue" / "Cat A-owned runner method with Cat B lens."
- **F3** (§1 Exec Summary line 3-4) — "All three v2 deliberation deployment paths (REST + PA tool + Celery task) traverse Cat B's v2 panel. v1 direct-write via ContentWriterAgent instantiates v1 ContentReviewPanel and does NOT touch Cat B's v2 panel or DecisionEnforcerAgent auto-trigger." (Preserves the WORKING-not-STABLE headline; scopes trigger-path claim.)
- **F4** (§4.2 MandateStatus paragraph + §13 lifecycle row) — Reframed to "dormant state machine (contract supports mark_killed/mark_completed transitions at :404-411; no caller in deliberation flow invokes them), not missing machinery." Cross-arc precedent: S1274 EventBus "partially adopted" analog.
- **F5** (§1 finding #3 + §7.2 branch 8 + §15.3) — Reframed to "exception-swallowed silent failure via broad try/except at :455/:474-476; no unhandled crash; no user-visible symptom."
- **F6** (§15.3 severity header + §19.6 T-slot rank #3/#4 rows) — CRITICAL → HIGH latent-landmine severity flip. Preserves "invalidates patent operational claim at DISCLOSURE_F.md:140 + trivially-triggerable landmine" rationale.
- **F7** (§15.10 severity header + paragraph) — MED → LOW unvalidated-tuning-knob classification. Preserves "if empirical misclassification evidence surfaces post-arc, escalate to MED" caveat.

**Two "do not regress" phrasings owed to PR review:** (i) preserve F5 "exception-swallowed silent failure via broad try/except at :455/:474-476; no user-visible symptom" phrasing at §1 finding #3 + §15.3; (ii) preserve F4 "dormant state machine (contract supports transitions but no caller in deliberation flow invokes them), not missing machinery" phrasing at §4.2 + §13.

**SIGN isolation pin retired at S1602 close** via Rigby `session_tool.retire conversation_id=pa-1c5298d807d7a1d2` — retired=true expected.

**D48 preemptive stability-probe gate 11th arm outcome:** Batches A/C + B/C held clean on fresh isolation pin (2 substantive turns produced 7 grep-verified folds); Batch C/C partial (worker-load deflection, not full jam per memory rule 2-substantive-turns threshold); final-verdict single-question turn returned in <10 seconds cleanly. **Six-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602 CONFIRMED** — extends 10-arc pattern S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506+S1601 to 11-arc + S1602. Codification-ready-STRENGTHENED for playbook v3 §15 per S1599 §10.2 6-candidate codify list.

### 20.6 Cross-arc handoffs to sibling + xx99

- **To S1603 Cat D (P3):** Cat B write to `SelfBlog.stats_snapshot['deliberation']` at runner :415 = D65a evidence input; F1-analog canonicalization-debt reframe applies. `deliverable_factory.py` bypass mirrors S1601 §9.1.
- **To S1604 Cat C (P4):** Cat B `decision` → PublishGate hand-off + `blog.status='needs_enhancement'` recovery envelope depends on Cat C `auto_enhance_blogs` beat existence. Cat B does NOT own retry loop.
- **To S1605 Cat E (P5):** Cat B ZERO PA-tool coverage on verdicts + mandate. Cat E owns resolution — either (i) add `content_tool.review_verdicts` action or (ii) route mandate via `governance_tool.decision_promote` extension.
- **To S1606 Cat F (P6):** Cat B ZERO outbound learning-loop / memory / signal-engine / Discord feedback. Cross-domain lens applies.
- **To S1699 xx99:** three axes evidence inputs per D65a/D65b/D65c framing:
  - D65a Deliverable-canonicalization scope — Cat B write-to-SelfBlog bypass = canonicalization-debt input, not proof of island posture.
  - D65b PublishGate + citation-integrity policy — Cat B FactCheckReviewer LLM-prompt-only + Cat A `claims_count > 0` binary = end-to-end citation contract absence CONFIRMED.
  - D65c Lifecycle-transition ownership — Cat B `MandateStatus` never transitions post-construction + `spawn_tasks_from_mandate` orphaned + verdict persistence-loss = fragmented ownership.

### 20.7 Frontmatter compliance

- `status: draft` (per playbook §16 default; flips to `active` when Chris says commit).
- `session: 1602`, `child_slot: P2`, `domain_slug: content`, `research_group: 1600`, `authority: child-audit`, `head_commit: ed212c51` (Group 1600 arc HEAD after S1601 close + docs cascade).
- `related:` populated with 9 references.
- `delegates_to:` 5 downstream targets.
- `verifier_loop:` pre_explore (7 claims) + post_explore (3 binary claims) + rigby_sign (pending fresh pin at commit).

### 20.8 Playbook §14 evidence-rules compliance

- File:line citations for all load-bearing claims — DONE.
- Direct source verification for important findings — DONE (pre-Explore + post-Explore verifier loops).
- Unknowns marked honestly — 4 UNKs deferred to §12.2.
- No speculation as fact — SPECULATIVE flags used (Agent 2 gpt-5.2 flag surfaced + retracted).
- Count conflicts vs `PLATFORM_INVENTORY.md` — no conflicts introduced.
- No implementation during research — DONE (this is a research doc; no code / migration / PR).
- Grep-verified binary claims before shipping — DONE (§20.4).

---

**End of S1602 audit.**
