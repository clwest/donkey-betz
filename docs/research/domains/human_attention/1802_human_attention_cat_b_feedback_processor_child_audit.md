---
title: "Group 1800 Category B — FeedbackProcessor + HumanFeedbackRecord + record_decision + post_save signal child audit"
status: active
authority: child-audit for Category B per parent §5 D78 sequence + SECOND child under Group 1800
category: child_audit
session: 1802
child_slot: P2
domain_slug: human_attention
research_group: 1800
head_commit: 9885ab01
last_verified: 2026-07-03
owner: Claude Code (S1802) + Rigby (SIGN-with-edits High confidence 0.82 2026-07-03 on arc pin pa-ae5931ea706b4537; F1/F4-severity/F5/Q4 folds landed pre-commit)
verifier_loop: |
  Pre-Explore: 5 parent §3.B canonical entry-point claims verified vs HEAD (models_human_interface.py:230-265,
  models_feedback_processing.py:33-434, human_interface_service.py:295-353 + :740-762,
  human_attention_lifecycle.py:298-347, models_feedback_processing.py:372-392); 4 line-range drifts + 1
  URL-pattern drift + 1 method-name drift catalogued as pre-Explore F-drift items (rolled up into §14 F1-F3).
  Post-Explore: 6-parallel-Explore reports reconciled via direct file reads at HEAD 9885ab01; F5
  feedback_record_id cross-domain grep returned ZERO hits outside Cat B (contrast S1801 F5 HAI_item_id
  8-10 domains) → HYPOTHESIS REMAINS (not VERIFIED-AT-CHILD); MC-3 CODIFICATION-READY promotion path
  DOES NOT advance at S1802 close.
  Post-SIGN (Rigby cycle 1 High confidence 0.82 SIGN-with-edits 2026-07-03): additional grep confirmation
  landed for Q1 miss-check — core/tasks.py + core/management/commands/ + core/admin.py all returned
  ZERO matches for HumanFeedbackRecord|record_decision|FeedbackProcessor|process_human_feedback,
  reinforcing "primary human-facing mutation surface" scope claim. F1 language softened from "ONLY" to
  "primary mutation surface at HEAD 9885ab01." F4 severity clarified as HIGH-conditional-on-contract-intent.
  §20.7 §20.7 clarification framed as methodology interpretation note (not new canonical rule). Q4
  R-slot Chris-gate ordering updated to Rigby's architecture-leverage ranking (R6 → R4 → R7 → R1).
  D48 26th arm turn 1 (platform_config overview) + turn 2 (Rigby SIGN batch) + turn 3 (Q4/verdict
  completion) all confirmed CLEAN — 21st consecutive-fully-clean-arms sub-pattern advancing.
seventh_application_note: |
  Playbook §11.2 20-section child template SEVENTH application overall (after S1601/S1701/S1801
  first-under-arc + S1602/S1702 second-under-arc + additional Group 1700 applications) + SECOND under
  Group 1800 (after S1801 P1 Cat A HumanAttentionItem Core). Applies §14 verifier-loop REQUIRED
  pre-Explore + post-Explore + §13 6-parallel-Explore + §15 SIGN cycle 1 single-batch 4-question
  pattern (D48 26th arm; 21st consecutive-fully-clean-arms sub-pattern anticipated).
---

# Group 1800 Category B — Feedback Processing Child Audit

> **First child audit** under Group 1800 was S1801 P1 (HumanAttentionItem Core). This is the **second child**, applying the same playbook §11.2 20-section template to Category B (FeedbackProcessor + HumanFeedbackRecord + `record_decision` + `post_save` signal wire). Boundary rule: Cat B owns the decision-recording surface + FeedbackProcessor classifier + `fed_to_ml` lifecycle. Cat B does NOT own the HAI model itself (Cat A, S1801), LearningBridges (Cat C, S1803), HumanPreference `update_learned_stats` (Cat D, S1804), or S746 verification writers (Cat E, S1805).

## 1. Executive Summary

Category B is the **canonical decision-recording plane** connecting a human's action on a HumanAttentionItem (Cat A) to downstream learning writes into Group 1300 Memory (AgentLearning + LearningInsight). At HEAD `9885ab01`, Cat B comprises **1 Django model** (`HumanFeedbackRecord`, `core/models_human_interface.py:230-265`), **1 service class** (`FeedbackProcessor`, `core/models_feedback_processing.py:33-330`), **2 producer methods** (`HumanInterfaceService.record_decision` @ `core/services/human_interface_service.py:295-353` and `HumanAttentionLifecycleService.auto_approve_item` @ `core/services/human_attention_lifecycle.py:298-347`), and **1 post_save signal receiver** (`process_human_feedback_signal` @ `core/models_feedback_processing.py:372-392`). One additional cross-domain consumer imports the FeedbackProcessor singleton: `core/services/agent_feedback_service.py:101-102`. There is exactly **ONE** post_save receiver on `HumanFeedbackRecord`.

The two producer sites BOTH write `HumanFeedbackRecord.objects.create(...)` at column `:325` in their respective files — a striking coincidence flagged as an information-only signal, not a coupling risk. Both producers share the same `fed_to_ml=False` default (:256) and rely on the same signal wire to invoke FeedbackProcessor. The signal handler @ `:372-392` is **synchronous + blocking + best-effort** (Exception caught @ `:391` and logged only; no Celery retry, no re-emit).

Six load-bearing findings F1–F8 (below §14) and ten technical debts D1–D10 (§15) surface, plus ten recommended future-research items R1–R10 (§19). The three biggest are: **F4 (HIGH) auto_approve_item creates HumanFeedbackRecord without calling _feed_to_ml → auto-approved rows are stuck at `fed_to_ml=False` FOREVER**; **F7 (HIGH) observability signal gap on `record_decision` decision path + FeedbackProcessor exception swallow** (parallel to S1801 D5 learning-loop-decoupling pattern applied to record_decision); and **F5 (MED) feedback_record_id is DOMAIN-INTERNAL only** (parent §2.6 row #2 HYPOTHESIS REMAINS at HYPOTHESIS — MC-3 two-triggers threshold does NOT advance at S1802 close).

**Q1-Q5 (parent §3.B) verdicts:**
- **Q1** Classifier semantics — inline positive/negative keyword-set matching @ `:156-157` (5 positive keywords + 5 negative keywords); NO standalone `classify_positive_negative` method. **PARTIAL — ad-hoc but functional.**
- **Q2** `fed_to_ml` lifecycle — flips False→True ONLY via `_feed_to_ml` @ `:756-759` scoped to `attention_item=item, fed_to_ml=False`. Auto-approve path never calls `_feed_to_ml`. **INCOMPLETE — auto-approve orphans confirmed.**
- **Q3** AgentLearning WRITER contract — FeedbackProcessor writes AgentLearning @ `:240` (positive) + `:296` (negative) and LearningInsight @ `:257` + `:314` via lazy properties, with Agent resolution silent-skip on name mismatch @ `:234-238` + `:291-293`. **BEST-EFFORT — no cross-domain contract enforcement.**
- **Q4** Round-trip completeness (S1274 §4.7 "only round-trip w/ learning") — round-trip write side WIRED (record_decision → HFR → signal → FeedbackProcessor → AgentLearning+LearningInsight). Downstream READ consumer of AgentLearning UNKNOWN at Cat B scope; Q4 flagged SPECULATIVE for Step 5 verification (R7 slot). **WRITE-COMPLETE, READ-UNVERIFIED.**
- **Q5** Retention posture — ZERO cleanup/delete sites for HumanFeedbackRecord across `core/`. **SAVED-FOREVER** — divergent from LLMCallEvent 30-day baseline; parallel to S1801 F6/D7 HAI retention finding.

Category B maturity verdict: **PARTIAL** (not STABLE). Operational wiring is present but three MED/HIGH debts (D2 preference-respect gap, D4 observability signal absence, D6 auto-approve fed_to_ml orphan) plus retention divergence prevent STABLE. Research coverage: **LIGHT** across all four sub-topics (model + FeedbackProcessor + record_decision + post_save wire).

## 2. Domain Purpose

**Question #1 — What does Cat B do?** Cat B is the closed-loop **feedback recorder** for the HumanAttention plane: when a human takes a decision on an attention item (approve, reject, defer, modify, etc.), or when the auto-escalate ladder auto-approves a low-risk item, Cat B (a) persists a `HumanFeedbackRecord` row snapshotting the decision + the ML context at decision time; (b) fires a Django `post_save` signal that invokes `FeedbackProcessor.process_human_feedback`; (c) classifies the decision as positive or negative via a 5-keyword-list rule; (d) writes an `AgentLearning` row plus a `LearningInsight` row into Group 1300 Memory territory keyed to the resolved Agent identity. Cat B is architecturally the ONLY round-trip narrative through which the HAI plane feeds forward into agent learning (per S1274 §4.7).

**Question #2 — Why does this domain exist at HEAD?** The `HumanFeedbackRecord` model was introduced in migration `0143_session_686_human_interface_layer` (Session 686) alongside the HAI model itself as the "record ML context at decision time for downstream learning" surface. The `FeedbackProcessor` service arrived at Session 861 (per docstrings @ `:253`, `:310`, `:375-376`, `:392`, `:398`, `:419`, `:430`, `:434`) to provide the classifier + signal wire + learning-writer path. The `_feed_to_ml` bridge @ `:740-762` was staged as a placeholder for a future model-router integration (currently logs-only per `:749-752` "For now, just log the feedback"), with the `fed_to_ml` flag as its progression sentinel. `agent_feedback_service.py:101-102` imports the FeedbackProcessor singleton to reuse the classifier on `AgentExecutionMemory.user_rating` events (secondary signal receiver @ `:395-419`).

## 3. Canonical Entry Points

Verified at HEAD `9885ab01`. Line ranges confirmed by direct file reads during pre-Explore + post-Explore verifier-loop (see §14 F1-F3 for parent §3.B drift catalog).

| Concept | File:Line at HEAD | Notes |
|---------|-------------------|-------|
| **HumanFeedbackRecord model** | `core/models_human_interface.py:230-265` | 36-line class body; ends @ `:265` before blank :266 (parent §3.B said :230-266, immaterial 1-line drift). |
| **FeedbackProcessor service class** | `core/models_feedback_processing.py:33-330` | Class definition starts @ `:33` (parent §3.B said `:122-180, 216-330` — those are METHOD ranges within the class; parent conflates class location with method locations). |
| **`process_human_feedback` method** | `core/models_feedback_processing.py:122-180` | Entry point invoked by post_save signal handler. |
| **`_reinforce_positive` method** | `core/models_feedback_processing.py:216-272` | Writes AgentLearning + LearningInsight via lazy properties. |
| **`_learn_from_negative` method** | `core/models_feedback_processing.py:274-330` | Writes AgentLearning + LearningInsight; higher confidence 0.9 vs 0.8. |
| **`process_pipeline_feedback` method** | `core/models_feedback_processing.py:84-120` (approx) | Secondary path for PipelineStageFeedback events (outside Cat B round-trip). |
| **`process_execution_feedback` method** | `core/models_feedback_processing.py:182-214` (approx) | Secondary path for AgentExecutionMemory events (invoked by second signal). |
| **`get_feedback_processor` singleton getter** | `core/models_feedback_processing.py:337-341` | Cached FeedbackProcessor instance. |
| **`process_human_feedback_signal` receiver** | `core/models_feedback_processing.py:372-392` | `@receiver(post_save, sender='core.HumanFeedbackRecord')`; guard `if not created: return` @ `:379`. |
| **`process_execution_memory_signal` receiver** | `core/models_feedback_processing.py:395-419` | Second receiver on `AgentExecutionMemory`; shares FeedbackProcessor singleton. |
| **`connect_feedback_signals` module hook** | `core/models_feedback_processing.py:423-430` | Called from `core/apps.py:56` in AppConfig.ready(); no-op (signals connect via decorators). |
| **`HumanInterfaceService.record_decision`** | `core/services/human_interface_service.py:295-353` | Creates HFR @ `:325`, calls `_feed_to_ml` @ `:344` CONDITIONALLY (only if `item.ml_prediction and item.human_overrode_ml`). |
| **`HumanInterfaceService._feed_to_ml`** | `core/services/human_interface_service.py:740-762` | Parent §3.B said :738 — 2-line drift. Filters `attention_item=item, fed_to_ml=False` @ `:756-758` then `.update(fed_to_ml=True, fed_at=timezone.now())`. |
| **`HumanAttentionLifecycleService.auto_approve_item`** | `core/services/human_attention_lifecycle.py:298-347` | Wrapped in `transaction.atomic()` @ `:316`; creates HFR @ `:325`. Does NOT call `_feed_to_ml`. |
| **REST endpoint (recording path)** | `core/urls.py` → `core/views_human_interface.py:546` (URL) + `:157-181` (view) | `path('api/human/attention/<uuid:item_id>/decide/', AttentionDecideView.as_view())` — parent §3.B said `/api/human/decisions/<id>/record/` which is INCORRECT (see §14 F1). Correct path at HEAD is `/api/human/attention/{id}/decide/`. |
| **PA tool (Rigby-visible)** | `core/services/pa_tool_schemas.py:5199` (schema) + `core/epa_handlers_tools.py:5004-5134` (handler) | `human_decisions_tool` — actions include `decide`, `batch_decide`, `auto_execute`. |
| **AppConfig ready hook** | `core/apps.py:56-57` | Imports + calls `connect_feedback_signals()` at Django ready() time. |

**Not owned by Cat B (out-of-scope per parent §3.B boundary rule):**
- HAI model @ `core/models_human_interface.py:20-227` — Cat A (audited S1801).
- HumanAttentionLifecycleService beat orchestration surface @ `core/services/human_attention_lifecycle.py:36-297` — Cat A.
- LearningBridge subclasses — Cat C (audit slot S1803).
- HumanPreference model + `update_learned_stats` — Cat D (audit slot S1804).
- S746 verification writers (`record_verification`) — Cat E (audit slot S1805).

## 4. Major Models

### 4.1 `HumanFeedbackRecord` (`core/models_human_interface.py:230-265`)

**Ownership:** Cat B (this audit).

**Fields (12 total):**

| Field | Type | Default | Null/Blank | :line | Notes |
|-------|------|---------|------------|-------|-------|
| `attention_item` | ForeignKey → `HumanAttentionItem` | — | — | :233-237 | CASCADE delete; `related_name='feedback_records'`. |
| `user` | ForeignKey → `settings.AUTH_USER_MODEL` | — | — | :238 | CASCADE delete. |
| `decision` | CharField(max_length=20) | — | — | :241 | Free-string; classifier uses 5-keyword lists @ `:156-157` in FeedbackProcessor. |
| `feedback_text` | TextField | `''` (via blank=True) | blank | :242 | User-authored feedback body. |
| `confidence` | FloatField | — | null, blank | :243 | User's confidence in decision. |
| `ml_task_type` | CharField(max_length=50) | — | null, blank | :246 | ML context snapshot @ decision time. |
| `ml_models_used` | JSONField | — | null, blank | :247 | ML context snapshot. |
| `ml_prediction` | JSONField | — | null, blank | :248 | ML context snapshot. |
| `ml_confidence` | FloatField | — | null, blank | :249 | ML context snapshot. |
| `human_agreed_with_ml` | BooleanField | — | null | :252 | Override-analysis field. |
| `confidence_delta` | FloatField | — | null, blank | :253 | Override-analysis field. |
| `fed_to_ml` | BooleanField | `False` | — | :256 | Learning-status flag; flipped True by `_feed_to_ml` @ human_interface_service.py:759. |
| `fed_at` | DateTimeField | — | null, blank | :257 | Timestamp when `fed_to_ml` flipped True. |
| `created_at` | DateTimeField(auto_now_add=True) | now | — | :259 | |

**Meta @ `:261-262`:**
```python
class Meta:
    ordering = ['-created_at']
```
**NO `unique_together`, NO `indexes`.** See §15 D9 for missing-index debt candidate.

**FK graph:**
- Inbound: `HumanFeedbackRecord.attention_item` FK to `HumanAttentionItem` (Cat A domain). CASCADE on HAI delete.
- Inbound: `HumanFeedbackRecord.user` FK to auth user (foreign domain). CASCADE on user delete.
- Outbound: None. AgentLearning + LearningInsight rows created downstream do NOT hold a FK back to the originating HumanFeedbackRecord — signal-based loose coupling.

**Migration lineage:** Created in `core/migrations/0143_session_686_human_interface_layer.py` (Session 686) alongside HAI, HumanPreference, and adjacent models. `fed_to_ml` and `fed_at` are baseline fields from the initial migration; no subsequent field-level migrations touch this model at HEAD.

### 4.2 Downstream write targets (foreign, referenced only)

Cat B FeedbackProcessor writes to two Group 1300 Memory models. Cat B AUDITS the WRITER contract; it does NOT own these models.

| Model | File:Line | Owning domain | Writer :line in Cat B code |
|-------|-----------|---------------|-----------------------------|
| `AgentLearning` | `core/models_unified_system.py` (per lazy import @ models_feedback_processing.py:232, 289) | Group 1300 Memory | `models_feedback_processing.py:240` (positive) + `:296` (negative). |
| `LearningInsight` | `core/models.py` (per lazy import @ models_feedback_processing.py:67) | Group 1300 Memory (per S1274 §4.7 canonical narrative) | `models_feedback_processing.py:257` (positive) + `:314` (negative). |
| `AgentMemory` | `core/models_agent_memory.py` (per lazy import @ models_feedback_processing.py:78) | Group 1300 Memory | NO write site in FeedbackProcessor at HEAD — dead import. See §15 D10. |

## 5. Major Services

### 5.1 `FeedbackProcessor` (`core/models_feedback_processing.py:33-330`)

**Purpose:** Classify HumanFeedbackRecord signals as positive/negative and write reinforcement records into AgentLearning + LearningInsight. Singleton (`_feedback_processor` global @ `:334`; `get_feedback_processor()` accessor @ `:337-341`).

**Method inventory (verified):**

| Method | :line | Signature | Return |
|--------|-------|-----------|--------|
| `__init__` | (implicit) | — | — |
| Lazy `AgentLearning` property | :51-60 | `@property` | Model class or `None` (try/except import). |
| Lazy `LearningInsight` property | :62-71 | `@property` | Model class or `None`. |
| Lazy `AgentMemory` property | :73-82 | `@property` | Model class or `None`. |
| `process_pipeline_feedback` | :84 | `(stage, rating, agent_name, context, feedback_text)` | bool |
| `process_human_feedback` | :122 | `(attention_item_id, decision, feedback_text=None, agent_name=None, ml_prediction=None, human_agreed_with_ml=None)` | bool |
| `process_execution_feedback` | :182 | `(agent_name, user_rating, task_type, feedback_text, execution_context)` | bool |
| `_reinforce_positive` | :216-272 | `(agent_name, task_context, context, feedback_text)` | bool |
| `_learn_from_negative` | :274-330 | `(agent_name, task_context, context, feedback_text)` | bool |

**Classifier semantics @ `:156-157` inside `process_human_feedback`:**
```python
is_positive = decision in ['approve', 'approved', 'accept', 'publish', 'completed']
is_negative = decision in ['reject', 'rejected', 'decline', 'failed', 'needs_work']
```
No standalone `classify_positive_negative` method exists at HEAD (parent §3.B language is aspirational — see §14 F3). Classification is inline; neutral (3-star, or decision not in either list) is a log-only no-op with no learning write.

**Agent resolution pattern @ `:234-238` (positive) + `:291-293` (negative):**
```python
agent = Agent.objects.filter(name__iexact=agent_name).first()
if not agent:
    agent = Agent.objects.filter(name__icontains=agent_name.replace('Agent', '')).first()
if agent:
    AgentLearning.objects.create(...)
```
**Silent-skip on Agent None** — no AgentLearning row created, no telemetry emitted. See §15 D5 for observability gap.

**Exception handling:**
- `_reinforce_positive` @ `:270-272` catches Exception, logs error, returns False.
- `_learn_from_negative` @ `:328-330` catches Exception, logs error, returns False.
- Signal receiver @ `:391-392` catches Exception, logs error, no re-raise, no retry.
**All failures are silent to callers.**

### 5.2 `HumanInterfaceService.record_decision` (`core/services/human_interface_service.py:295-353`)

**Purpose:** REST-facing method for a human's decision on a HAI. Verified body flow:

1. **:317** Fetch `HumanAttentionItem` scoped to `user=self.user`. Returns error dict on `DoesNotExist`.
2. **:322** `item.record_decision(decision, feedback, confidence)` — HAI model method (Cat A). Sets `decision`, `decision_feedback`, `confidence`, `status=acted`, `decided_at`, computes `human_overrode_ml`, `time_to_decision_ms`.
3. **:325-337** `HumanFeedbackRecord.objects.create(...)` with `attention_item`, `user`, `decision`, `feedback_text`, `confidence`, `ml_task_type`, `ml_models_used`, `ml_prediction`, `ml_confidence`, `human_agreed_with_ml=not item.human_overrode_ml if item.ml_prediction else None`, `confidence_delta=(confidence - item.ml_confidence) if confidence and item.ml_confidence else None`. **Triggers post_save signal synchronously.**
4. **:340** `self._update_preferences_from_decision(item)` — updates HumanPreference `topic_weights`/`source_weights` (F5 governance bug territory — Cat D scope).
5. **:343-344** Conditional `self._feed_to_ml(item)` — ONLY if `item.ml_prediction and item.human_overrode_ml`.
6. **:346** `logger.info` — only observability emit (see §15 D4).
7. **:348-353** Return `{'success': True, 'item_id': ..., 'decision': ..., 'human_overrode_ml': ...}`.

**No `transaction.atomic()` guard.** See §15 D1.

### 5.3 `HumanAttentionLifecycleService.auto_approve_item` (`core/services/human_attention_lifecycle.py:298-347`)

**Purpose:** Auto-escalate ladder's terminal auto-approve action for low-risk HAI items. Verified body flow:

1. **:316** Enter `transaction.atomic()`.
2. **:318-322** Set `item.decision='approve'`, `item.decision_feedback=reason`, `item.status='acted'`, `item.decided_at=timezone.now()`, `item.save()`. **No `update_fields=[...]` — writes entire row (S1801 D1 pattern applied here too).**
3. **:325-334** `HumanFeedbackRecord.objects.create(attention_item=item, user=item.user, decision='approve', feedback_text=reason, confidence=1.0, ml_prediction=item.ml_prediction, ml_confidence=item.ml_confidence, human_agreed_with_ml=True if item.ml_recommendation == 'approve' else None)`. **Triggers post_save signal.**
4. **:337** `self._maybe_trigger_orchestration(item)` — potential downstream orchestration wiring.
5. **:338-347** Return `{'success': True, ..., 'orchestration_triggered': ...}`.

**Does NOT call `_feed_to_ml`.** Auto-approved rows stay `fed_to_ml=False` FOREVER unless overridden by a subsequent record_decision. See §14 F4 (HIGH) and §15 D6.

### 5.4 `HumanInterfaceService._feed_to_ml` (`core/services/human_interface_service.py:740-762`)

**Purpose:** Placeholder ML feedback path. Body:

1. **:742-745** Lazy-import + instantiate `get_agent_model_router`.
2. **:749-752** `logger.info` describing override (currently placeholder — "This would update model scores based on human corrections / For now, just log the feedback").
3. **:756-759** `HumanFeedbackRecord.objects.filter(attention_item=item, fed_to_ml=False).update(fed_to_ml=True, fed_at=timezone.now())`.
4. **:761-762** Exception caught, logs warning, no re-raise.

**Observation:** The `fed_to_ml` progression sentinel is genuine, but the router integration is aspirational (`# For now, just log the feedback`). See §17 duplicate-service consideration for interaction with Cat C AgentLearningService and Cat D update_learned_stats.

## 6. Major APIs and Interfaces

### 6.1 REST

| Path | Method | View | :line | Owner |
|------|--------|------|-------|-------|
| `/api/human/attention/<uuid:item_id>/decide/` | POST | `AttentionDecideView` | `views_human_interface.py:157-181` (view) + `:546` (URL) | Cat B **CORRECTED FROM parent §3.B** — parent §3.B said `POST /api/human/decisions/<id>/record/` which is INCORRECT (see §14 F1). |
| `/api/human/attention/bulk-decide/` | POST | `BulkAttentionDecideView` | `views_human_interface.py:469-530` + `:543` | Cat B (bulk variant; loops calling `record_decision`). |
| `/api/human/attention/<uuid:item_id>/defer/` | POST | `AttentionDeferView` | `views_human_interface.py:188-209` + `:547` | Cat A (defer state on HAI, not a feedback record). |
| `/api/human/attention/<uuid:item_id>/verify/` | POST | `AttentionVerifyView` | `views_human_interface.py:217-257` + `:548` | Cat E (S746 verification path). |
| `/api/human/attention/<uuid:item_id>/execute/` | POST | `AttentionExecuteActionView` | `views_human_interface.py:270-307` + `:549` | Cat A (Mission Control execute path). |

Cat B's **primary human-facing mutation surface at HEAD `9885ab01`** is these two REST entry points (decide + bulk-decide). All other `/api/human/attention/*` endpoints belong to Cat A or Cat E. Additional writer/consumer verification via `core/tasks.py` + `core/management/commands/` + `core/admin.py` grep (post-SIGN Q1 miss-check) returned ZERO matches for `HumanFeedbackRecord|record_decision|FeedbackProcessor|process_human_feedback` — no Celery task, no management command, no Django admin writes HFR directly at HEAD. If a future writer is introduced (e.g., a backfill/reconcile command), it must be added to this catalog.

### 6.2 PA tools (Rigby surface)

| Tool | Schema :line | Handler :line | Actions |
|------|--------------|---------------|---------|
| `human_decisions_tool` | `core/services/pa_tool_schemas.py:5199` (referenced @ :3163 in Cog listing) | `core/epa_handlers_tools.py:5004-5134` | `decide`, `batch_decide`, `auto_execute` — all route to `HumanInterfaceService.record_decision`. |
| `boardroom_tool` (deprecated) | `core/services/pa_tool_schemas.py:5075` | `core/epa_handlers_tools.py:5004-5134` (shared) | Superseded by `human_decisions_tool`. |

Rigby can CREATE HumanFeedbackRecord rows via the PA tool. There is **no PA tool for READING HumanFeedbackRecord as a governance audit trail** — see §18 ownership gap 5.

### 6.3 WebSocket consumers

None. Verified via grep of `core/consumers*.py` — no matches for `HumanFeedbackRecord`, `record_decision`, or `feedback_processing`. Attention stream uses REST polling.

### 6.4 Celery tasks + Beat schedule

| Task | :line | Beat cadence | Queue | Cat B relevance |
|------|-------|--------------|-------|-----------------|
| `core.tasks.process_human_attention_lifecycle` | `core/tasks.py:7248-7284` | every 10 min | default | Cat A — Cat B is only tangentially involved (this task manages HAI lifecycle; may indirectly trigger `auto_approve_item` which then creates HFR). |

**No Cat B-owned Celery task exists.** The post_save signal @ `:372-392` runs synchronously in the caller's process — see §10 event flow + §15 D3 (no retry queue).

### 6.5 Management commands

None. Verified `ls core/management/commands/` — no commands mentioning `feedback`, `decision`, or `HumanFeedbackRecord`. See §18 ownership gap 3 (no orphan cleanup command).

### 6.6 Discord surface

| Command | :line | Notes |
|---------|-------|-------|
| Inline `record_decision()` call | `core/services/discord_bot.py:11251` | Called when a human responds to an attention notification via Discord; not a dedicated `/decide` slash command. |

### 6.7 Frontend

Frontend caller references to `/api/human/attention/{itemId}/decide/` and `/api/human/attention/bulk-decide/` live in `frontend/src/appManifest.ts` (endpoint catalog). Specific React components (Approve/Reject/Defer buttons) render inside Boardroom UI; not audited in depth per Cat B code-only scope.

## 7. Runtime Flows

### 7.1 Flow A — REST `record_decision` (human overrides ML)

```
frontend → POST /api/human/attention/{item_id}/decide/
    → AttentionDecideView (views_human_interface.py:157-181)
        → HumanInterfaceService(request.user).record_decision(item_id, decision, feedback, confidence)
            → HumanAttentionItem.objects.get(id, user)                       [:317]
            → item.record_decision(decision, feedback, confidence)           [:322]  # updates HAI status
            → HumanFeedbackRecord.objects.create(...)                        [:325-337]
                ⚡ SYNC post_save signal fires
                    → process_human_feedback_signal(created=True)            [:372-392]
                        → get_feedback_processor()                            [:383]
                        → processor.process_human_feedback(item_id, decision, ...)  [:384]
                            → HumanAttentionItem.objects.get(id)             [:147-149]  # RE-FETCH — no cache
                            → classify inline: is_positive / is_negative      [:156-157]
                            → if is_positive:  _reinforce_positive(agent_name, task_type, ctx, text)  [:165]
                                    → Agent.objects.filter(name__iexact) or fallback icontains  [:234-238]
                                    → AgentLearning.objects.create(learning_type='positive_feedback', confidence_score=0.8, ...)  [:240-252]
                                    → LearningInsight.objects.create(insight_type='positive_reinforcement', confidence_score=0.8, ...)  [:257-266]
                            → if is_negative:  _learn_from_negative(agent_name, task_type, ctx, text)  [:173]
                                    → Agent.objects.filter(...)               [:291-293]
                                    → AgentLearning.objects.create(learning_type='negative_feedback', confidence_score=0.9, ...)  [:296-308]
                                    → LearningInsight.objects.create(insight_type='improvement_needed', confidence_score=0.9, ...)  [:314-324]
            → self._update_preferences_from_decision(item)                   [:340]  # Cat D territory (HumanPreference)
            → if item.ml_prediction and item.human_overrode_ml:              [:343]
                → self._feed_to_ml(item)                                     [:344]
                    → get_agent_model_router()                               [:743-745]  # placeholder
                    → logger.info(f"ML Feedback: ...")                       [:749-752]
                    → HumanFeedbackRecord.objects.filter(attention_item=item, fed_to_ml=False).update(fed_to_ml=True, fed_at=now)  [:756-759]
            → logger.info(f"Human decision recorded: {decision} on {title}")  [:346]
            → return {'success': True, 'item_id': ..., 'decision': ..., 'human_overrode_ml': ...}
```

**Total DB writes per decision:** 1 HAI update + 1 HFR insert + 0-2 AgentLearning inserts + 0-2 LearningInsight inserts + 0-1 HFR update (fed_to_ml flip) + N HumanPreference updates (Cat D scope).

### 7.2 Flow B — auto-approve_item (Cat A → Cat B → Cat B signal)

```
HumanAttentionLifecycleService.auto_escalate_item OR bulk auto-approve caller
    → HumanAttentionLifecycleService(user).auto_approve_item(item, reason)  [:298-347]
        ↳ transaction.atomic():                                              [:316]
            → item.decision = 'approve'; item.decision_feedback = reason; item.status='acted'; item.decided_at=now  [:318-321]
            → item.save()                                                    [:322]  # NO update_fields
            → HumanFeedbackRecord.objects.create(attention_item, user, decision='approve', feedback_text=reason, confidence=1.0, ml_prediction, ml_confidence, human_agreed_with_ml=...)  [:325-334]
                ⚡ SYNC post_save signal fires
                    → process_human_feedback_signal(created=True)            [:372-392]
                        → processor.process_human_feedback('approve', ..., agent_name=None)
                        → classifier: is_positive=True (decision='approve' matches @ :156)
                        → _reinforce_positive(agent_name=None, ...)          [:165]
                        → Agent.objects.filter(name__iexact=None).first() → returns None
                        → SILENT-SKIP: AgentLearning NOT created; LearningInsight NOT created  [see D8]
                        → return True
            → self._maybe_trigger_orchestration(item)                        [:337]
        return {'success': True, ..., 'orchestration_triggered': ...}
```

**Total DB writes per auto-approve:** 1 HAI update + 1 HFR insert + 0 AgentLearning + 0 LearningInsight (silent-skip on agent_name=None) + 0 HFR update (never flipped True — auto-approve **NEVER** calls `_feed_to_ml`). **HFR row stuck `fed_to_ml=False` forever.**

### 7.3 Flow C — Rigby PA tool decide

```
Rigby PA session → LLM function call: human_decisions_tool(action='decide', item_id, decision, feedback)
    → epa_handlers_tools.py:5004-5134 dispatcher
        → HumanInterfaceService(pa_user).record_decision(item_id, decision, feedback, confidence)
            → [same as Flow A]
```

### 7.4 Flow D — Second post_save receiver (cross-arc)

```
AgentExecutionMemory.user_rating set (Cat C / Group 1300 territory)
    → save()
        ⚡ post_save signal fires
            → process_execution_memory_signal(created=True)                  [:395-419]
                → if not instance.user_rating: return                         [:403]
                → processor.process_execution_feedback(agent_name, user_rating, task_type, ...)  [:408]
                    → classify: is_positive (star 4-5) / is_negative (1-2)   [inside :182 body]
                    → _reinforce_positive OR _learn_from_negative
```

Not strictly Cat B — this is Group 1300's AgentExecutionMemory feedback path — but it SHARES the FeedbackProcessor singleton. See §17 duplicate-service consideration and §16 boundary violation candidate.

## 8. Data Ownership and Lifecycle

### 8.1 HumanFeedbackRecord row lifecycle

| Transition | Owner | :line | Notes |
|-----------|-------|-------|-------|
| Created with `fed_to_ml=False` | `record_decision` OR `auto_approve_item` | human_interface_service.py:325 + human_attention_lifecycle.py:325 | Both writer sites at column :325 by coincidence. |
| `fed_to_ml`: False → True + `fed_at` written | `_feed_to_ml` | human_interface_service.py:759 | Batch `.update()` on `.filter(attention_item=item, fed_to_ml=False)`. Only triggered by `record_decision` when human overrode ML @ :343. **NEVER triggered by auto-approve path.** |
| Row read by post_save signal handler | `process_human_feedback_signal` (via instance) | models_feedback_processing.py:373-392 | Reads instance fields; re-fetches HAI @ :147. |
| Row read for `record_decision`'s stats @ :215 | `HumanInterfaceService.get_feedback_stats` (or similar) | human_interface_service.py:215 | Read-only aggregation. |
| Row read for `HumanPreference.update_learned_stats` @ models_human_interface.py:339 | Cat D (HumanPreference) | :339 | Filter by user; stat aggregation. |
| Row deleted | **NONE** | — | **NO delete site at HEAD.** Retention: SAVED-FOREVER. Parallel to S1801 F6/D7 HAI retention. |
| Row updated (fields other than fed_to_ml/fed_at) | **NONE** | — | Immutable after create except for fed_to_ml/fed_at. |

### 8.2 Retention verdict — SAVED-FOREVER

Verified via grep at HEAD:
- `HumanFeedbackRecord.*\.delete\(` → ZERO matches across `core/` + `ai_core/` + `intelligence/`.
- `HumanFeedbackRecord\.objects\.filter.*delete` → ZERO matches.
- `cleanup.*HumanFeedbackRecord` / `retention.*HumanFeedbackRecord` → ZERO matches.
- No management command mentions HumanFeedbackRecord.
- No Celery beat task deletes HumanFeedbackRecord.
- No `_impl_cleanup_boardroom_junk`-style path applies (that path @ `core/tasks_ops.py:39-97` per S1801 §15.7 D7 is scoped to spider_action + arbitrage + `[Learned]` junk categories — not HumanFeedbackRecord).

**Retention posture: SAVED-FOREVER.** Divergent from LLMCallEvent 30-day baseline (`CELERY_TASK_EVENT_RETENTION_DAYS=30` per S1801 §9). Parallel to S1801 F6/D7 finding for HAI. See §14 F6 and §15 D7 (retention posture debt).

### 8.3 Downstream row lifecycle (AgentLearning + LearningInsight)

Cat B **writes** but does NOT **own** these. Retention + read-consumer questions are Group 1300 Memory territory. Q4 round-trip completeness at HEAD is UNVERIFIED for the READ side (see §14 F8 SPECULATIVE + §19 R7).

## 9. Integrations With Other Domains

### 9.1 Cross-domain writer contract

| Target | Domain | Cat B writer :line | Boundary status |
|--------|--------|--------------------|-----------------|
| `AgentLearning.objects.create` | Group 1300 Memory | models_feedback_processing.py:240, 296 | **CROSSES BOUNDARY** — direct `.objects.create()` in Cat B code without adapter/service layer. Lazy-loaded via `@property` guards. |
| `LearningInsight.objects.create` | Group 1300 Memory (per S1274 §4.7) | models_feedback_processing.py:257, 314 | **CROSSES BOUNDARY** — same pattern. |
| `Agent.objects.filter` (read-only) | Group 1300 Memory (canonical agent registry) | models_feedback_processing.py:234, 237, 291, 293 | RESPECTED — read-only. |
| `HumanAttentionItem.objects.get` | Cat A (HAI core) | models_feedback_processing.py:147-149 | RESPECTED — read-only lookup for context enrichment. |

Cat B respects READ boundaries but **directly writes to Group 1300 Memory models**. Refactoring AgentLearning or LearningInsight schema would break Cat B. See §16 boundary violation.

### 9.2 Inbound importers of Cat B

| Importer | :line | Purpose |
|----------|-------|---------|
| `core/apps.py:56-57` | AppConfig ready() hook | Calls `connect_feedback_signals()` at Django startup. |
| `core/services/agent_feedback_service.py:101-102` | AgentFeedbackService thumbs-up/down path | Imports `get_feedback_processor` to invoke `process_execution_feedback` on `AgentFeedback.rating` events. |
| `core/models_feedback_processing.py` (internal) | Self-imports HAI @ :147 | Read-only. |

Only **ONE** cross-service importer of the FeedbackProcessor singleton at HEAD: `agent_feedback_service.py`. All other invocations flow through the two post_save signal receivers.

### 9.3 Inbound readers of HumanFeedbackRecord

Verified via grep of `HumanFeedbackRecord.objects.filter|HumanFeedbackRecord.objects.get|HumanFeedbackRecord.objects.all`:

| Reader | :line | Domain | Purpose |
|--------|-------|--------|---------|
| `core/services/human_interface_service.py:215` | Cat B | Feedback stats aggregation (fed_to_ml=True count). |
| `core/services/human_interface_service.py:756` | Cat B | `_feed_to_ml` writer scope. |
| `core/models_human_interface.py:339` | Cat D (HumanPreference `update_learned_stats`) | Filter by user for preference-learning aggregation. |
| `intelligence/tasks.py` (metadata flag `'feedback_recorded': True`) | Group 1300/1600 territory | INDIRECT — no direct `.objects.filter()`; only metadata presence flag noted. |

**Cross-domain read of HumanFeedbackRecord: essentially ZERO.** Only Cat D peeks (single site, aggregate). Confirms F5 verdict: **feedback_record_id is DOMAIN-INTERNAL** (see §14 F5).

### 9.4 Cross-arc handoffs

- **Group 1300 Memory (S1300-S1399):** Cat B WRITES `AgentLearning` + `LearningInsight`. S1399 §3 (per Explore Agent 5) delegates "Cat H ↔ Cat B write-authority + TTL policy" as a follow-on ADR to post-S1399. **S1802 finalizes the Cat B side of the writer contract.** Consumer/reader side (does anyone READ these rows for ML training?) remains SPECULATIVE — see §19 R7.
- **Group 1400 Revenue / Group 1500 Sports / Group 1600 Content / Group 1700 Observability:** No direct integration observed. HumanFeedbackRecord.id does not surface in these domains' code paths at HEAD.
- **S1801 Cat A:** Established `HumanFeedbackRecord.attention_item` FK contract; auto_approve_item writer @ :325 was noted in S1801 §26 as "Cat B territory" for full audit here.
- **S1804 Cat D (queued):** `update_learned_stats` @ HumanInterfaceService `_update_preferences_from_decision` (called @ :340 in record_decision path) is the F5 governance bug territory. Cat B invokes it but does not own it.

### 9.5 Cross-domain gap parallel to S1274

Per S1274 §3.3 + §3.8, five cross-domain HAI-consumer integrations are MISSING at HEAD (Body Systems / Signal Engine / Revenue / Observability / failure-cluster aggregator). Cat B **inherits** these gaps because HumanFeedbackRecord is Cat A's downstream row — no cross-domain producer would create HFRs; they'd need to first create HAI rows. See §14 F8 (S1274 baseline still MISSING).

## 10. Event Flows

### 10.1 Signal-driven event: `post_save(HumanFeedbackRecord, created=True)`

- **Registration:** `@receiver(post_save, sender='core.HumanFeedbackRecord')` @ `models_feedback_processing.py:372` (decorator-based auto-connect on module import).
- **Handler:** `process_human_feedback_signal(sender, instance, created, **kwargs)` @ `:373-392`.
- **Guard:** `if not created: return` @ `:379` — updates do not re-fire. But HumanFeedbackRecord has no field-update pathway other than `.update(fed_to_ml=True, ...)` (which does not fire model-level post_save on QuerySet.update by default).
- **Sync/Async:** **SYNCHRONOUS + BLOCKING.** No `.delay()`, no `apply_async`, no Celery boundary. Blocks the calling `.objects.create()` until FeedbackProcessor completes or exception is caught.
- **Error handling:** `try/except Exception as e: logger.error(...)` @ `:391-392`. Silent swallow. **No re-raise. No retry.**
- **Side effects:** Up to 2 DB writes (AgentLearning + LearningInsight); zero writes on Agent None (silent-skip).

### 10.2 Signal-driven event: `post_save(AgentExecutionMemory, created)`

Second receiver @ `:395-419` on `AgentExecutionMemory`. Guard: `if not instance.user_rating: return` @ `:403`. Invokes `processor.process_execution_feedback(...)` @ `:408-417`. This is **cross-arc** (AgentExecutionMemory is Group 1300 Memory territory) but SHARES the FeedbackProcessor singleton. See §16 boundary violation candidate and §17 duplicate-service consideration.

### 10.3 Signal-driven event: `post_save(PipelineStageFeedback, created)` (implied)

The presence of `process_pipeline_feedback_signal` @ `models_feedback_processing.py:350` (per pre-Explore grep) implies a THIRD post_save receiver on `PipelineStageFeedback` at approximately :349-370. This model is Group 1600 Content territory; the receiver reuses the FeedbackProcessor singleton. **Cross-arc signal handler concentration inside models_feedback_processing.py** — three post_save receivers, three distinct sender domains, one shared classifier. See §17 duplicate service consideration.

### 10.4 No explicit event emit for observability

- `record_decision` @ `:346` emits `logger.info` only — no event, no signal, no observability call.
- FeedbackProcessor methods emit `logger.info`/`logger.error` on success/failure but do not surface events to a monitoring system.
- No `HAI_item_id` or `feedback_record_id` structured log line for cross-service correlation (parallel to S1801 D5 `record_verification` learning-loop decoupling — see §15 D4).

## 11. Existing Documentation

### 11.1 Topic docs coverage

Per Explore Agent 5: NO dedicated topic doc for Cat B. Adjacent coverage lives in:
- `docs/topics/personal-assistant.md` — mentions PA feedback surface tangentially.
- `docs/topics/agent-system.md` — mentions AgentLearning surface tangentially.
- `docs/topics/body-systems.md` / `docs/topics/celery-workers.md` — no direct Cat B content.

**Verdict: NONE-to-LIGHT topic doc coverage.** See §14 F7 or §19 R-slot for a "publish topic doc after arc close" recommendation.

### 11.2 Handoffs touching Cat B

- **S686 (migration 0143):** Original creation of HumanFeedbackRecord alongside HAI.
- **S861 (FeedbackProcessor birth):** FeedbackProcessor + signal wire + `_reinforce_positive`/`_learn_from_negative` classifier arrived. Docstrings inside `models_feedback_processing.py` cite "Session 861" repeatedly.
- **S1300-S1399 (Group 1300 Memory arc):** AgentLearning + LearningInsight writer contract delegated to post-S1399 ADR. S1802 closes the Cat B side of this delegation.
- **S1800 (parent scoping):** Cat B scope defined @ parent §3.B; F5 `feedback_record_id` HYPOTHESIS row #2 registered @ §2.6.
- **S1801 (Cat A HAI Core):** Boundary rule §26 explicitly defers FeedbackProcessor internals + post_save signal to Cat B (S1802). Noted `HumanFeedbackRecord.objects.create` @ human_attention_lifecycle.py:325 as Cat B's writer; F5 correlation-primitive HAI_item_id VERIFIED-AT-CHILD across 8-10 domains established the pattern for S1802's `feedback_record_id` verification.

### 11.3 Research library

- **`docs/research/platform_architecture_inventory.md` §3.16** — cites FeedbackProcessor at :1341-1343 ("classifies HumanFeedbackRecord positive/negative post_save → creates AgentLearning + LearningInsight (only round-trip w/ learning)"). Cites HumanFeedbackRecord at :1330-1331 ("ML context snapshot; fed_to_ml flag").
- **`docs/research/platform_architecture_inventory.md` §4.7** — "canonical round-trip narrative" claim ("only round-trip w/ learning" per S1273 §2.5). Verified aligned with HEAD wiring; consumer side of round-trip UNVERIFIED (§14 F8 SPECULATIVE).
- **`docs/research/platform/cross_domain_integration_audit.md` §3.3 + §3.8** — S1274 baseline cross-domain gaps; Cat B inherits.
- **`docs/research/governance_authority_evolution.md` §1.4** — F5 HumanPreference never-saved bug (Cat D territory; adjacent).

## 12. Research Coverage

Per playbook §12:

| Sub-topic | Verdict | Evidence |
|-----------|---------|----------|
| HumanFeedbackRecord model | **LIGHT** | Cited in S1273 §3.16 + §4.7; no dedicated audit. |
| FeedbackProcessor service | **LIGHT** | Cited in S1273 §3.16 + §4.7; no classifier semantics audit. |
| record_decision surface | **LIGHT** | Cited in S1273 §3.16; parent §3.B lists surface but incorrectly labels URL path. |
| post_save signal wire | **LIGHT** | Cited in S1273 §4.7 narrative; no runtime-flow / retry / error-handling analysis. |
| **Cat B overall (this audit closes)** | **DEEP-post-S1802** | This audit brings Cat B from LIGHT → DEEP research coverage. |

## 13. Architecture Maturity

Per playbook §12:

| Sub-topic | Verdict | Evidence |
|-----------|---------|----------|
| HumanFeedbackRecord model | **WORKING** | Model exists, tested via signal integration; but missing composite indexes (§15 D9) prevent STABLE. |
| FeedbackProcessor service | **WORKING** | Functional classifier + writer path; but silent-skip on Agent None (§15 D8) + no test coverage grep found + no retry (§15 D3) prevent STABLE. |
| record_decision surface | **PARTIAL** | Operational for REST + PA + Discord callers; but no transaction guard (§15 D1) + no preference validation (§15 D2) + no observability signal (§15 D4) prevent WORKING. |
| post_save signal | **WORKING** | Signal registered + guard-on-created; but silent exception swallow (§15 D3) prevents STABLE. |
| auto_approve_item Cat B path | **PARTIAL** | Wired but `fed_to_ml=False` orphan case (§15 D6) is a data-quality break. |
| **Cat B overall** | **PARTIAL** | See §1 executive summary rationale. Three MED/HIGH debts + retention divergence prevent STABLE. |

## 14. Known Drift

### F1 (MED) — Parent §3.B URL pattern INCORRECT at HEAD

**Claim:** parent §3.B says `POST /api/human/decisions/<id>/record/`.
**HEAD:** `POST /api/human/attention/<uuid:item_id>/decide/` @ `core/views_human_interface.py:546` (URL registration) + `:157-181` (view body).
**Impact:** Parent-scoping URL pattern drift. Not a code bug — the code is correct — but the parent doc names a non-existent URL. Cat B audit corrects this in §3 + §6.1.
**Fold owed:** Parent scoping §3.B URL correction (single-line edit; S1802 close artifact).

### F2 (LOW) — Parent §3.B line ranges (four minor drifts)

1. HumanFeedbackRecord :230-266 → HEAD :230-265 (1-line drift; :266 is a blank between classes).
2. FeedbackProcessor "class :122-180, 216-330" → HEAD class starts at :33; :122 is `process_human_feedback` method; :216 is `_reinforce_positive` method; :274 is `_learn_from_negative` method; class body ends near :330.
3. `record_decision :295-353, 738` → HEAD :295-353 confirmed; `:738` reference is 2 lines off (actual `_feed_to_ml` @ :740; :738 is `_update_preferences_from_decision` tail body region).
4. `auto_approve_item :325-334` (parent Cat A §3.A) → HEAD auto_approve_item method starts at :298 but its HumanFeedbackRecord writer IS at :325-334 (parent used the writer-line range as the method range — imprecise but not wrong).

**Impact:** LOW. Purely descriptive line-range imprecision. Audit corrects in §3.

### F3 (LOW-MED) — "classify_positive_negative" method does NOT exist

**Claim:** parent §3.B lists "FeedbackProcessor + classify_positive_negative + fed_to_ml lifecycle" as the scope.
**HEAD:** No standalone `classify_positive_negative` method exists on FeedbackProcessor. Classification is inline @ `models_feedback_processing.py:156-157` inside `process_human_feedback`:
```python
is_positive = decision in ['approve', 'approved', 'accept', 'publish', 'completed']
is_negative = decision in ['reject', 'rejected', 'decline', 'failed', 'needs_work']
```
**Impact:** LOW-MED. Boundary clarification, not a functional gap. Audit corrects in §3 + §5.1.

### F4 (HIGH) — `auto_approve_item` creates HumanFeedbackRecord WITHOUT calling `_feed_to_ml`

**Evidence:** Full method body @ `core/services/human_attention_lifecycle.py:298-347` reviewed directly. Body includes: `transaction.atomic()` → HAI field updates + `item.save()` → `HumanFeedbackRecord.objects.create(...)` → `_maybe_trigger_orchestration` → return. **No `_feed_to_ml` invocation anywhere in the method.**
**Consequence:** Every auto-approved item produces a HumanFeedbackRecord with `fed_to_ml=False`. That row NEVER flips to True because the only writer of `fed_to_ml=True` is `_feed_to_ml` @ `human_interface_service.py:756-759`, and `_feed_to_ml` is only called from `record_decision` @ `:344` conditionally (only if human overrode ML).
**At scale:** If auto-escalate ladder auto-approves N items per day, N HumanFeedbackRecord rows accumulate with `fed_to_ml=False` FOREVER. There is no orphan-cleanup task, no dashboard alert, no retention window (§14 F6).
**Severity: HIGH — conditional on contract intent.** This is HIGH if the intended contract is "every human decision (including auto-approve) produces ML training feedback." If the intended contract is "auto-approve is workflow hygiene only, NOT ML training signal," this downgrades to **MED (field-semantics mislabeling debt)** — the fields `fed_to_ml`/`fed_at` implicitly promise a lifecycle that auto-approve intentionally opts out of, and the fix becomes adding `flow_source` (or `is_training_signal`) to HumanFeedbackRecord rather than wiring `_feed_to_ml` into auto_approve. **Contract intent is UNKNOWN at HEAD — no docstring, no ADR, no session handoff pins it down.** This ambiguity IS the biggest architectural risk per Rigby SIGN cycle 1 ("semantic ambiguity of 'feedback' vs 'decision bookkeeping'") and is a prerequisite Chris-gated question for R4 remediation. See §15 D6 for the corresponding D-slot.
**Recommended remediation:** Option A — call `_feed_to_ml` (or a lighter-weight `fed_to_ml=True` update) inside `auto_approve_item` after the HFR create. Option B — accept the divergence and add `flow_source` field to HumanFeedbackRecord distinguishing manual-override rows (fed_to_ml lifecycle applies) from auto-approve rows (fed_to_ml is N/A). Option C — leave as-is and treat `fed_to_ml=False` on auto-approve rows as expected; document in a topic doc. **Chris-gated ratification requires an explicit contract statement first ("is auto-approve HFR ML training signal — yes / no?") before any of the three options can be selected.** Ratification is post-arc T-slot per playbook §14.5 no-implementation rule.

### F5 (MED) — `feedback_record_id` is DOMAIN-INTERNAL, NOT cross-system (HYPOTHESIS REMAINS)

**Parent §2.6 row #2 HYPOTHESIS:** "feedback_record_id is the trigger event for FeedbackProcessor post_save signal; classified positive/negative; consumed once then fed_to_ml=True."
**S1802 verification protocol** (mirrors S1801 F5 HAI_item_id VERIFIED-AT-CHILD template):
- Grep `feedback_record_id|HumanFeedbackRecord\.id|feedback_record\b` across all `**/*.py` in the repo at HEAD `9885ab01`.
- Results:
  - Zero hits for `feedback_record_id` in `core/` or `ai_core/` or `intelligence/` outside of documentation.
  - The only production match for `feedback_record` is `core/services/operating_rhythm.py:431, 464` — where `feedback_record` refers to `FounderFeedback` (a DIFFERENT model, not `HumanFeedbackRecord`).
- No cross-domain code path references `HumanFeedbackRecord.id` as a primitive; `AgentLearning` and `LearningInsight` rows do NOT hold FKs back.

**Verdict:** `feedback_record_id` is DOMAIN-INTERNAL to Cat B only. It is NOT a cross-system correlation primitive at HEAD.

**F5 HYPOTHESIS BOX status at S1802 close:** **HYPOTHESIS REMAINS.** Parent §2.6 row #2 stays as HYPOTHESIS (not upgraded to VERIFIED-AT-CHILD like row #1 HAI_item_id was at S1801).

**MC-3 CODIFICATION-READY promotion path impact:** S1799 §10.2 MC-3 CODIFICATION-CANDIDATE two-triggers threshold met at S1801 close (HAI_item_id VERIFIED cross-system). The intended THIRD-application durability test at S1802 (feedback_record_id) does NOT support the same finding. MC-3 promotion path DOES NOT advance to CODIFICATION-READY at S1802 close. **The pattern the primitive HYPOTHESIS box discipline codifies is the DISCIPLINE OF NAMING + VERIFYING primitives ahead of child audits — not that every named primitive MUST verify. A HYPOTHESIS that fails verification is still a valid research outcome.** The primitive-box discipline itself remains CODIFICATION-CANDIDATE pending further arc-level durability checks (Cat C, D, E remaining under Group 1800; plus future arcs).

**Severity: MED.** Not a code bug — the round-trip works fine using `attention_item_id` (HAI_item_id) as the correlation primitive. The finding is a **methodology outcome**: F5 HYPOTHESIS box discipline correctly identified `feedback_record_id` as a candidate primitive but child evidence at S1802 disproved cross-system usage. Parent §2.6 row #2 should be updated at S1802 close (see §20 fold record).

### F6 (MED) — Retention SAVED-FOREVER divergent from LLMCallEvent baseline

Parallel to S1801 F6 for HAI. Evidence in §8.2. Divergent from `CELERY_TASK_EVENT_RETENTION_DAYS=30` baseline. Cat B inherits the retention-posture debt originally identified for HAI. Recommended follow-on: pair R-slot with S1801 R1 into a single "HumanAttention plane retention posture ADR."

### F7 (HIGH) — Observability signal gap on decision path (parallel to S1801 D5)

`record_decision` @ `:346` emits only `logger.info(f"Human decision recorded: {decision} on {item.title}")`. FeedbackProcessor `_reinforce_positive`/`_learn_from_negative` methods emit `logger.info`/`logger.error` on outcome; signal handler `try/except Exception as e: logger.error(...)` @ `:391-392` swallows failures. **There is no structured event emit tagged with `HAI_item_id` or `feedback_record_id` visible to observability.**

**Parallel to S1801 D5:** S1801 promoted `record_verification` learning-loop decoupling from MED → HIGH via Rigby SIGN Q3 because HAI verification writes emit no signal/event/HAI_item_id log. Same pattern applies to `record_decision` here — decision writes emit no correlated observability event. If FeedbackProcessor fails silently (Agent None silent-skip @ D8, exception swallow @ D3), a decision looks successful from the frontend perspective but produces no learning signal downstream. **No user-facing alert. No dashboard row. No forensic trace.**

**Severity: HIGH.** Learning-loop debt at the HAI plane's canonical round-trip is the same class of debt as S1801 D5. See §15 D4 for the corresponding D-slot.

### F8 (LOW SPECULATIVE) — Q4 round-trip Step 5 consumer UNVERIFIED

Cat B WRITE-side of the round-trip is VERIFIED (record_decision → HFR → signal → FeedbackProcessor → AgentLearning + LearningInsight). **The Step 5 READ side — does downstream ML training code READ these AgentLearning + LearningInsight rows for actual agent adaptation? — is UNVERIFIED at Cat B scope.** This belongs to Cat C (LearningBridges) + Group 1300 Memory territory. Flagged SPECULATIVE per playbook §14 evidence rules. See §19 R7 for the follow-on research slot.

### F9 (LOW-MED) — Cross-arc Group 1700 timeline drift (inherited)

Per start-here doc §Doctor warnings: `§8 timeline table drift` — missing rows for S1605 + S1606 + S1699 (Group 1600). Cat B doesn't originate this drift but the Cat B audit does not close it either — inherited to Group 1600 xx99 anchor-update PR queue.

### Rolled-in / not-reported

- No test-coverage claim made for FeedbackProcessor at HEAD — grep of `core/tests/` found no dedicated `test_feedback_processor.py`. Flagged as UNKNOWN in §20 rather than as an F-slot.

## 15. Known Technical Debt

Deduplicated + severity-classified from Explore reports.

| D-slot | Severity | Location | Description |
|--------|----------|----------|-------------|
| **D1** | MED | `human_interface_service.py:295-353` | `record_decision` has NO `transaction.atomic()` guard around HFR create + preference update + `_feed_to_ml`. Race + partial-failure surface. Contrast with `auto_approve_item` @ `human_attention_lifecycle.py:316` which IS wrapped in `transaction.atomic()`. |
| **D2** | MED | `models_feedback_processing.py` (no imports) + `human_interface_service.py:295-353` + `human_attention_lifecycle.py:298-347` | Zero preference-respect across Cat B writer surface. No `HumanPreference` import in `models_feedback_processing.py`; `blocked_sources` / `trusted_agents` / `review_depth` are not consulted before HumanFeedbackRecord create. Parallel to S1801 D2 (43-producer zero-preference-respect finding for HAI writers). |
| **D3** | MED | `models_feedback_processing.py:391-392` | Signal handler `try/except Exception as e: logger.error(...)` — silent swallow, no re-raise, no Celery retry. `_reinforce_positive` + `_learn_from_negative` exception handlers @ `:270-272` + `:328-330` do the same. If FeedbackProcessor fails on classifier or write, feedback is silently orphaned. |
| **D4** | HIGH | `human_interface_service.py:346` + `models_feedback_processing.py:253, 310, 391` | Observability signal gap on `record_decision` — only `logger.info`. FeedbackProcessor emits `logger.info`/`logger.error` but no structured event with `HAI_item_id` or `feedback_record_id`. Parallel to S1801 D5 (`record_verification` decoupling HIGH). Blocks learning-loop forensics + dashboard visibility. |
| **D5** | LOW-MED | `models_feedback_processing.py:234-238, 291-293` | Agent resolution silent-skip on `Agent.objects.filter(name__iexact=agent_name).first()` → None + fallback icontains → None. AgentLearning + LearningInsight rows are silently NOT created; no telemetry. FeedbackProcessor returns True. Round-trip appears complete but produced zero downstream writes. |
| **D6** | HIGH-conditional | `human_attention_lifecycle.py:298-347` | `auto_approve_item` creates HumanFeedbackRecord without calling `_feed_to_ml` → auto-approved HFR rows are stuck at `fed_to_ml=False` FOREVER. Q2 orphan class confirmed. **Severity HIGH if the intended contract is "every human decision produces ML training feedback"; MED if the contract is "auto-approve is workflow hygiene only, not ML signal."** Contract intent is UNKNOWN at HEAD (no docstring, no ADR). See §14 F4 + Rigby SIGN cycle 1 "semantic ambiguity of 'feedback' vs 'decision bookkeeping'" biggest-architectural-risk finding. Whether to fix by calling `_feed_to_ml`, adding a `flow_source` field, or accepting the divergence is a Chris-gated ADR (§19 R4). |
| **D7** | MED | HFR retention posture | SAVED-FOREVER — zero delete sites. Divergent from LLMCallEvent 30-day baseline. Pair with S1801 F6/D7 (HAI SAVED-FOREVER) into a single HumanAttention plane retention posture ADR (§19 R1). |
| **D8** | LOW-MED | `agent_feedback_service.py:101-102` + `models_feedback_processing.py` cross-arc receivers | Three post_save receivers concentrated inside `models_feedback_processing.py` (HumanFeedbackRecord @ :372, AgentExecutionMemory @ :395, PipelineStageFeedback @ :350) sharing one FeedbackProcessor singleton. Not strictly a debt if intentional consolidation; but the file is titled `models_feedback_processing.py` yet holds Cat C + Group 1300 + Group 1600 receivers. See §16 boundary violation candidate. |
| **D9** | LOW | `models_human_interface.py:261-262` | HumanFeedbackRecord `Meta` declares only `ordering = ['-created_at']`. No `unique_together`, no `indexes`. Batch update @ `human_interface_service.py:756-758` filters `(attention_item, fed_to_ml=False)` without composite index. At current volume, unlikely to bite; at scale (N per day for months), full-scan risk. |
| **D10** | LOW | `models_feedback_processing.py:73-82, 78` | `AgentMemory` lazy-imported via `@property` but no `.objects.create()` call site inside file. Dead property. Refactor debt. Also `connect_feedback_signals()` @ `:423-430` is a no-op (signals auto-connect via decorators) called from `apps.py:56` — refactor debt. |

## 16. Boundary Violations

### 16.1 Cat B → Group 1300 Memory direct writes

FeedbackProcessor writes `AgentLearning` + `LearningInsight` via `.objects.create()` inside Cat B code (`models_feedback_processing.py:240, 257, 296, 314`). No adapter/service delegation layer. Refactoring either target model requires Cat B changes. **Verdict: BOUNDARY VIOLATION.** Recommended remediation: introduce an `AgentLearningWriter` service (or reuse `AgentLearningService`) that Cat B calls, so schema changes stay behind a stable API. Post-arc T-slot per playbook §14.5.

### 16.2 File-title / receiver-scope mismatch

`core/models_feedback_processing.py` holds three post_save receivers with three distinct sender domains:
- HumanFeedbackRecord (Cat B) @ :372
- AgentExecutionMemory (Group 1300 Memory) @ :395
- PipelineStageFeedback (Group 1600 Content) @ :350 (inferred)

The file's title implies a "feedback processing" scope but the receiver mix crosses three arcs. Not a functional bug but a **code-organization boundary blur** — should signal handlers live in per-domain signal registries, or is FeedbackProcessor deliberately the shared classifier? Post-arc topic-doc question.

### 16.3 `auto_approve_item` writes at Cat A → Cat B boundary

`human_attention_lifecycle.py` is Cat A (per parent §3.A). Its `auto_approve_item` @ :298 creates HumanFeedbackRecord (Cat B model) at :325. **Cat A writes into Cat B's model space directly.** Alternative: HumanAttentionLifecycleService could call `HumanInterfaceService.record_decision(...)` with `decision='approve'` and `confidence=1.0`, letting Cat B own its own creation path. Not a strict violation (Cat A owns the trigger; Cat B owns the model), but a mild layering blur worth documenting.

## 17. Duplicate or Overlapping Systems

### 17.1 FeedbackProcessor singleton reused across three sender domains

Same instance handles HumanFeedbackRecord + AgentExecutionMemory + PipelineStageFeedback. Whether this is duplication or intentional consolidation depends on ratification. If FeedbackProcessor is intended to be THE canonical classifier across all learning-signal sources, this is not duplication. If each domain should own its own classifier, this is duplication. Post-arc question for xx99 §5 posture-decision brief input.

### 17.2 `_feed_to_ml` vs `AgentLearningService` (Cat C, S1803 scope)

`_feed_to_ml` @ `human_interface_service.py:740-762` is placeholder-only ("For now, just log the feedback"). Cat C's AgentLearningService (audit slot S1803) may already implement the router-integration wiring intended for `_feed_to_ml`. Duplicate-service inventory owed to Cat C or xx99 §5.

### 17.3 `connect_feedback_signals` no-op

`connect_feedback_signals()` @ `:423-430` is a no-op (signals auto-connect via decorators) but is still called from `apps.py:56`. Refactor debt. See §15 D10.

## 18. Ownership Gaps

| # | Gap | Detail |
|---|-----|--------|
| 1 | `fed_to_ml=False` orphan detection | No management command, no dashboard, no Celery task surfaces stale rows. See §15 D6. |
| 2 | HumanFeedbackRecord retention deletion | Zero deletion path at HEAD. See §14 F6 + §15 D7. |
| 3 | HumanFeedbackRecord orphan cleanup command | No `manage.py cleanup_human_feedback` or equivalent. §6.5 confirmed. |
| 4 | Round-trip Step 5 read consumer | Who reads AgentLearning + LearningInsight rows after Cat B writes them? Cat C or Group 1300 territory but never verified end-to-end. See §14 F8 + §19 R7. |
| 5 | PA-tool read view for governance audit trail | Rigby can CREATE HumanFeedbackRecord via `human_decisions_tool` decide/batch_decide, but there is NO PA tool for READING the historic feedback ledger (fed_to_ml distribution, per-agent aggregates, per-decision-type histograms). Rigby cannot inspect the plane she writes into. |
| 6 | Auto-approve `_feed_to_ml` wire | Ownership of the auto-approve → `_feed_to_ml` connection is UNOWNED — neither Cat A `auto_approve_item` nor Cat B `record_decision` sees auto-approve rows through the fed_to_ml lifecycle. See §14 F4 + §15 D6. |
| 7 | Cross-domain `feedback_record_id` propagation | If future arcs decide feedback_record_id SHOULD become a cross-system primitive (D-slot verdict OWEs to xx99 §5 posture brief), no ownership defined for propagation writes. |

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows per playbook §12.

| R-slot | Title | Rationale |
|--------|-------|-----------|
| **R1** | HumanAttention plane retention posture ADR (paired w/ S1801 R1) | Pair `HumanFeedbackRecord` SAVED-FOREVER (this audit F6/D7) + `HumanAttentionItem` SAVED-FOREVER (S1801 F6/D7) into one ADR spec. Compare against LLMCallEvent 30-day baseline. Ratification is Chris-gated post-arc. |
| **R2** | Preference-aware feedback factory | Wrap HumanFeedbackRecord creation in a validation layer that consults `HumanPreference.blocked_sources` + `trusted_agents`. Direct parallel to S1801 R2. |
| **R3** | auto_approve validation gate against blocked_sources | Preflight validation before `auto_approve_item` writes HFR. Direct parallel to S1801 R3. |
| **R4** | Auto-approve → `_feed_to_ml` wire OR flow_source field | Chris-gated ADR: fix Q2 orphan by wiring `_feed_to_ml` OR by adding a `flow_source: enum` field. See §14 F4 for options. |
| **R5** | FeedbackProcessor Celery retry queue | Signal handler exception swallow → replace with Celery retry via `apply_async` w/ retry policy. Restore observability of failed feedback processing. |
| **R6** | Observability signal on `record_decision` + FeedbackProcessor emit | Structured event with `feedback_record_id` + `HAI_item_id` + classifier outcome + downstream write count. Parallel to S1801 D5 remediation path. |
| **R7** | Q4 round-trip Step 5 consumer verification (Cat C / Group 1300 scope) | Do the AgentLearning + LearningInsight rows written by FeedbackProcessor ever get READ for actual ML training or personalization? S1274 §4.7 "only round-trip w/ learning" claim requires Step 5 verification to hold. Cat C audit slot S1803 should answer. |
| **R8** | Agent resolution fail-loud | Replace silent-skip on Agent None with structured warning + telemetry. Currently invisible AgentLearning misses look like round-trip success. |
| **R9** | Composite indexes on HumanFeedbackRecord | Add `models.Index(fields=['attention_item', 'fed_to_ml'])` + `models.Index(fields=['user', 'fed_to_ml'])`. Migration. |
| **R10** | `connect_feedback_signals` + `AgentMemory` dead-code cleanup | Small refactor PR. `connect_feedback_signals` is a no-op; `AgentMemory` lazy import unused. Minor. |

Cross-referenced to S1801 R-slots: R1 pairs with S1801 R1 (retention ADR bundle). R2 mirrors S1801 R2 (preference-aware producer factory). R3 mirrors S1801 R3 (auto-approve blocked_sources validation). R4 is new to Cat B. R5-R10 are Cat B specific.

**Chris-gate ordering (post-SIGN cycle 1 — Rigby's architecture-leverage ranking):** **R6 → R4 → R7 → R1**. Rationale: R6 (observability signal on record_decision + FeedbackProcessor emit) is highest leverage across Cat A + Cat B — lets us prove whether feedback is flowing and correlate outcomes. R4 (auto-approve → _feed_to_ml wire OR flow_source field) should follow AFTER a crisp contract statement (Rigby: "otherwise you risk wiring the wrong intent"). R7 (round-trip Step 5 consumer verification) depends on R6 to validate/measure and avoid "paper verification." R1 (HAI plane retention ADR) is important but best set once event semantics + observability are clarified so retention policy isn't set blind. **If Chris is in "governance first" mode, R1 can be moved earlier.** R2 / R3 / R5 / R8 / R9 / R10 remain as unranked follow-ons behind the top-4 gate order.

## 20. Appendix

### 20.1 Files inspected

| File | :lines read | Purpose |
|------|-------------|---------|
| `core/models_human_interface.py` | :230-278 (HumanFeedbackRecord + HumanPreference start) | Cat B model. |
| `core/models_feedback_processing.py` | :1-434 (whole file via targeted reads at :33, :122-180, :216-330, :350-434) | FeedbackProcessor + signal receivers + module hooks. |
| `core/services/human_interface_service.py` | :23, :215, :295-360, :525, :525-762 (targeted reads) | record_decision + `_feed_to_ml` + stats. |
| `core/services/human_attention_lifecycle.py` | :36, :298-347 | auto_approve_item. |
| `core/services/agent_feedback_service.py` | :101-112 (cited by Explore Agent 2) | Cross-service FeedbackProcessor consumer. |
| `core/apps.py` | :56-57 | AppConfig.ready() → `connect_feedback_signals`. |
| `core/views_human_interface.py` | :9-14 (header), :44-80, :91-181, :217-307, :469-530, :534-561 (URL registration) | REST endpoints. |
| `core/services/pa_tool_schemas.py` | :5075, :5199, :3163 (per Explore Agent 3) | PA tool schemas. |
| `core/epa_handlers_tools.py` | :5004-5134 (per Explore Agent 3) | PA tool dispatcher. |
| `core/tasks.py` | :7248-7284 (per Explore Agent 3) | HAI lifecycle beat task. |
| `core/services/discord_bot.py` | :11251 (per Explore Agent 3) | Discord inline record_decision reference. |
| `core/services/operating_rhythm.py` | :431, :464 | FounderFeedback (adjacent — filtered OUT of Cat B scope per grep review). |
| `core/migrations/0143_session_686_human_interface_layer.py` | :54-75 (per Explore Agent 1) | HumanFeedbackRecord initial migration. |

### 20.2 Docs inspected

- `docs/research/domains/human_attention/1800_human_attention_domain_scoping.md` — parent §3.B Cat B scope + §2.6 F5 HYPOTHESIS box row #2 + §5 P2 slot definition.
- `docs/research/domains/human_attention/1801_human_attention_cat_a_human_attention_item_core_audit.md` — S1801 §26 boundary rule + §9-10 F5 HAI_item_id verification precedent (SIXTH application overall).
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` — §11.2 20-section child template + §13 6-parallel-Explore + §14 evidence rules + §15 SIGN policy + §16 commit policy.
- `docs/research/platform_architecture_inventory.md` §3.16 + §4.7 — S1273 baseline for HumanAttention + canonical round-trip narrative.
- `docs/research/platform/cross_domain_integration_audit.md` §3.3 + §3.8 + §4.7 — S1274 baseline for cross-domain gaps.
- `docs/research/domains/memory/1399_memory_canonical_summary.md` — S1399 §3 delegation of "Cat H ↔ Cat B write-authority + TTL policy" ADR (per Explore Agent 5).
- `docs/handoffs/SESSION_1801_HUMAN_ATTENTION_CAT_A_HAI_CORE_AUDIT.md` — S1801 handoff.

### 20.3 Grep patterns used

Exhaustive list of load-bearing greps run during pre-Explore + post-Explore verifier-loop:

```
HumanFeedbackRecord\.objects\.create|HumanFeedbackRecord\(
_feed_to_ml\b|fed_to_ml\s*=\s*True|\.fed_to_ml\b
process_human_feedback\b|get_feedback_processor\b|FeedbackProcessor\(
HumanFeedbackRecord.*\.delete\(|HumanFeedbackRecord\.objects\.filter.*delete|cleanup.*HumanFeedbackRecord|retention.*HumanFeedbackRecord
HumanPreference|blocked_sources|trusted_agents  (scoped to models_feedback_processing.py — zero hits)
feedback_record_id|HumanFeedbackRecord\.id|feedback_record\b  (F5 cross-domain verification — zero prod-code hits outside operating_rhythm.py FounderFeedback)
connect_feedback_signals|models_feedback_processing  (scoped to apps.py)
```

### 20.4 Unresolved unknowns

- **U1** — FeedbackProcessor test coverage at HEAD: no dedicated `test_feedback_processor.py` found in `core/tests/` grep. Whether integration tests exercise the signal handler is UNKNOWN. Flagged for R-slot follow-up.
- **U2** — Q4 round-trip Step 5 downstream consumer of AgentLearning + LearningInsight: UNVERIFIED at Cat B scope; S1803 Cat C should answer.
- **U3** — Whether `_feed_to_ml` router placeholder-log path is intentional deferral or forgotten TODO — Session 861 docstring says "For now, just log the feedback" but no follow-on session ratified next-step. Chris-visible flag.
- **U4** — `PipelineStageFeedback` post_save receiver inferred @ :350 not directly read in this audit (out-of-scope for Cat B; Group 1600 Content territory). Boundary noted, not audited.

### 20.5 Conflicts between sources

- **Parent §3.B vs HEAD URL:** parent says `/api/human/decisions/<id>/record/`; HEAD has `/api/human/attention/{id}/decide/`. HEAD wins (F1).
- **Parent §3.B FeedbackProcessor location vs HEAD:** parent conflates method line ranges with class line range. HEAD (:33 for class; :122 + :216 + :274 for methods) wins (F2 + F3).
- **S1273 §3.16 "WORKING/MODERATE maturity" claim vs S1802 verdict:** S1273 rated maturity higher than this audit's PARTIAL verdict. Not strict conflict — the D2 + D4 + D6 debts + retention divergence justify the PARTIAL downgrade at Cat B granularity. S1273 was at broader domain granularity.

### 20.6 Verifier-loop corrections

**Rigby SIGN cycle 1 outcome (2026-07-03 on arc pin `pa-ae5931ea706b4537`):** SIGN-with-edits at High confidence (0.82). Four folds landed pre-commit.

| Fold | Source | Change landed |
|------|--------|---------------|
| **F1 (Q1 miss-check softening)** | Rigby SIGN Q1: "don't claim REST surface is 'ONLY X endpoints' unless verifier-loop includes route grep + tasks/management commands/admin utilities" | §6.1 language softened from "Cat B owns exactly TWO REST entry points" to "Cat B's **primary human-facing mutation surface at HEAD `9885ab01`** is these two REST entry points" + explicit additional grep evidence (core/tasks.py + core/management/commands/ + core/admin.py all returned ZERO matches — no Celery task, no management command, no Django admin writes HFR at HEAD). Locked to HEAD `9885ab01` — future writers must be added. |
| **F4 severity clarification (Q2)** | Rigby SIGN Q2: "F4 (auto_approve never feeds ML): conditional HIGH → could be MED if intended semantics are 'auto-approve is not ML feedback.'" | §14 F4 body + §15 D6 severity classification updated from HIGH to **HIGH-conditional-on-contract-intent**. Added Chris-gated prerequisite: "an explicit contract statement first ('is auto-approve HFR ML training signal — yes / no?') before any of the three remediation options can be selected." Also referenced Rigby's "semantic ambiguity of 'feedback' vs 'decision bookkeeping'" as the biggest architectural risk. |
| **F5 §20.7 clarification framing (Q3)** | Rigby SIGN Q3: "§20.7 clarification is acceptable if clearly framed as a methodology interpretation note and not presented as a newly-canonical rule" | §20.7 MC-3 section rewrapped with explicit framing sentence: "**Methodology interpretation note (this audit's read; NOT a new canonical rule)**." Codification-ratification path pushed to xx99 §5 posture-decision brief input + playbook §20 two-triggers-rule ratification. |
| **Q4 R-slot Chris-gate ordering** | Rigby SIGN Q4 architecture-leverage ranking | §19 R-slot table amended with explicit **R6 → R4 → R7 → R1** post-SIGN Chris-gate ordering block. R2/R3/R5/R8/R9/R10 marked as unranked follow-ons. |
| **F7 (no change)** | Rigby SIGN Q2: "F7 keep HIGH — it's not double-counting; severity is about impact not novelty" | No change. F7 remains HIGH per severity impact. |

**F1 evidence grep additions (post-SIGN):**
- `grep -r 'HumanFeedbackRecord\|record_decision\|FeedbackProcessor\|process_human_feedback' core/tasks.py` → ZERO matches.
- `grep -r 'HumanFeedbackRecord\|record_decision\|FeedbackProcessor\|process_human_feedback' core/management/commands/` → ZERO matches.
- `grep -r 'HumanFeedbackRecord\|record_decision\|FeedbackProcessor' core/admin.py` → ZERO matches.

**Post-SIGN D48 arm status:** 26th arm turns 1-3 all CLEAN (platform_config overview; SIGN batch; Q4 + verdict completion). 21st consecutive-fully-clean-arms sub-pattern advancing.

### 20.7 F5 correlation-primitive HYPOTHESIS box status (per S1799 §10.2 MC-3)

**Row #2 `feedback_record_id` verification outcome at S1802 close:**

- Working definition (from parent §2.6): "HumanFeedbackRecord.id — per-feedback-record UUID. Written by HumanInterfaceService.record_decision(). Points at HAI via FK."
- **Actual writers verified at HEAD:** TWO — `record_decision` @ `human_interface_service.py:325` AND `auto_approve_item` @ `human_attention_lifecycle.py:325`. Parent §2.6 undercounted (single-writer claim).
- **HYPOTHESIS component 1** ("trigger event for FeedbackProcessor post_save signal"): **VERIFIED** — signal @ `models_feedback_processing.py:372-392` fires on every HFR create.
- **HYPOTHESIS component 2** ("classified positive/negative"): **VERIFIED** — inline classifier @ `:156-157`.
- **HYPOTHESIS component 3** ("consumed once then fed_to_ml=True"): **PARTIALLY VERIFIED** — `_feed_to_ml` @ `:756-759` flips fed_to_ml=True BUT only from `record_decision` conditional path @ `:344`. Auto-approve path never flips it. Q2 orphan case.
- **HYPOTHESIS component 4** (cross-system primitive like HAI_item_id): **DISPROVEN** — grep confirms `feedback_record_id` / `HumanFeedbackRecord.id` do NOT propagate cross-domain at HEAD. Domain-internal only.

**Aggregate verdict:** `feedback_record_id` HYPOTHESIS is PARTIALLY VERIFIED at Cat B internals level BUT NOT VERIFIED as a cross-system primitive. Parent §2.6 row #2 status remains **HYPOTHESIS** (not upgraded to VERIFIED-AT-CHILD). Alternatively, could be labeled **VERIFIED-DOMAIN-INTERNAL-ONLY** to distinguish from HAI_item_id's VERIFIED-CROSS-SYSTEM status.

**MC-3 CODIFICATION-READY promotion at S1802 close:** DOES NOT ADVANCE.

**Methodology interpretation note (this audit's read; NOT a new canonical rule):** the two-triggers threshold is interpretable as referring to the discipline of NAMING + VERIFYING at scoping time (which both S1700 and S1800 arcs did), NOT to two primitives both verifying as cross-system. On that read, the primitive-box discipline itself remains CODIFICATION-CANDIDATE; a Cat C `learning_event_id` verification at S1803 may (or may not) provide the durability check that promotes the discipline to CODIFICATION-READY. This audit does NOT canonicalize this interpretation — it flags the ambiguity for xx99 §5 posture-decision brief input and playbook §20 two-triggers-rule ratification. See §10.2 in S1799 xx99 for the MC-3 codification path spec.

### 20.8 Appendix — HumanFeedbackRecord writer inventory (2 sites) + AgentLearning writer inventory (2 sites) + LearningInsight writer inventory (2 sites)

Producer catalog for Cat B round-trip:

**HumanFeedbackRecord producer sites (grep-verified, all `*.py` at HEAD `9885ab01`):**
1. `core/services/human_attention_lifecycle.py:325` — auto_approve_item body (inside `transaction.atomic()`).
2. `core/services/human_interface_service.py:325` — record_decision body (no `transaction.atomic()`).

**AgentLearning producer sites in Cat B code (foreign write into Group 1300 territory):**
1. `core/models_feedback_processing.py:240` — `_reinforce_positive` positive_feedback @ confidence 0.8.
2. `core/models_feedback_processing.py:296` — `_learn_from_negative` negative_feedback @ confidence 0.9.

**LearningInsight producer sites in Cat B code (foreign write into Group 1300 territory):**
1. `core/models_feedback_processing.py:257` — positive_reinforcement insight @ confidence 0.8.
2. `core/models_feedback_processing.py:314` — improvement_needed insight @ confidence 0.9.

**FeedbackProcessor invocation sites at HEAD:**
1. `core/models_feedback_processing.py:384` (signal handler for HumanFeedbackRecord) — Cat B.
2. `core/models_feedback_processing.py:407` (signal handler for AgentExecutionMemory) — cross-arc.
3. `core/models_feedback_processing.py:360` (implied third signal handler for PipelineStageFeedback) — cross-arc.
4. `core/services/agent_feedback_service.py:101-102` (cross-service import + call to `process_execution_feedback`) — cross-arc.

**Total production write footprint per Cat B round-trip on human override (positive-classified):** 1 HAI update + 1 HFR insert + 1 HFR update (fed_to_ml flip) + 1 AgentLearning insert + 1 LearningInsight insert + N HumanPreference updates = ~5-6 DB writes per decision, all synchronous.

**Total production write footprint per Cat B round-trip on auto-approve (positive-classified but agent_name=None from lifecycle service):** 1 HAI update + 1 HFR insert + 0 fed_to_ml flip + 0 AgentLearning (silent-skip on Agent None) + 0 LearningInsight (silent-skip on Agent None) = 2 DB writes per auto-approve. The auto-approve round-trip is **structurally incomplete** — writes the HFR row but produces zero downstream learning signal. Q2 + Q4 debt combined.

### 20.9 Post-SIGN fold summary (populated 2026-07-03 post Rigby SIGN cycle 1)

See §20.6 for the full four-fold ledger. Summary:

- **F1 fold** — REST surface language softened + additional grep evidence landed (core/tasks.py + core/management/commands/ + core/admin.py all ZERO).
- **F4 severity fold** — HIGH → HIGH-conditional-on-contract-intent. Chris-gated contract clarification required before remediation option selection.
- **F5 §20.7 framing fold** — Methodology interpretation note explicitly labeled as non-canonical.
- **Q4 R-slot ordering fold** — R6 → R4 → R7 → R1 Chris-gate ordering documented per Rigby architecture-leverage ranking.
- **F7 no-change confirmed** — HIGH severity retained per Rigby: not double-counting; severity is about impact.

**Biggest architectural risk (per Rigby SIGN cycle 1 explicit call):** "semantic ambiguity of 'feedback' vs 'decision bookkeeping'." Whether HumanFeedbackRecord mixes human decision provenance + ML training signal + pipeline quality feedback determines whether F4/F7-class issues keep reappearing. Prerequisite Chris-gated question for R4 remediation. Elevated to xx99 §5 posture-decision brief input.
