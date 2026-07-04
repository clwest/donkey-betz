---
title: "Group 1800 Cat D — HumanPreference + F5 never-saved bug + reader inventory child audit"
session: 1804
child_slot: P4
domain_slug: human_attention
research_group: 1800
category: child_audit
authority: child-audit for Category D per parent §5 D78 sequence + FOURTH child under Group 1800
head_commit: 40d575d6
status: draft
authors: Claude Code (Chris directed via short command "start research group 1804" — interpreted per playbook §21 short-command intent as S1804 child under Group 1800 D78 P4 slot; Rigby confirmed interpretation + service_context: local on arc pin pa-ae5931ea706b4537)
prior_children:
  - 1801_human_attention_cat_a_human_attention_item_core_audit.md (S1801 Cat A)
  - 1802_human_attention_cat_b_feedback_processor_child_audit.md (S1802 Cat B)
  - 1803_human_attention_cat_c_learning_bridges_child_audit.md (S1803 Cat C)
parent: 1800_human_attention_domain_scoping.md
delegates_to: []
related_arcs:
  - 1200 Governance (S1269 §1.4 F5 finding root — HumanPreference in per-human governance-plane inventory; §2.4 row 30 topic_weights/source_weights NEVER POPULATED)
  - 1300 Memory (UserAgentLearning as parallel per-user personalization surface — closed at S1399)
  - 1400 Revenue (opportunity qualification does NOT read HumanPreference — closed at S1499)
  - 1500 Sports (recommendation does NOT read HumanPreference — closed at S1599)
  - 1600 Content (deliberation/reviewer routing does NOT read HumanPreference — closed at S1699)
  - 1700 Observability (no telemetry emitted on HumanPreference updates — closed at S1799)
  - 1900 Event Architecture (no event bus integration — not yet opened)
playbook_application: §11.2 20-section child template NINTH application overall + FOURTH under Group 1800
verifier_loop: §14 verifier-loop REQUIRED CODIFICATION-READY (S1799 §10.2 MC-1) — pre-Explore + post-Explore performed; pre-Explore verifier CAUGHT parent §5 D78 P4 HYPOTHESIS wording drift (F5 root cause is NOT "set locally but never .save()d" — see F1 for corrected two-part-bug framing); post-Explore verifier confirmed `user_pref_id` primitive box grep = ZERO hits across ALL .py files (F5 correlation-primitive HYPOTHESIS DISPROVED-CROSS-SYSTEM; THIRD CONSECUTIVE F5 negative outcome after S1802 feedback_record_id + S1803 learning_event_id); Rigby SIGN cycle 1 Q1 miss-vector rule-out (celery/mgmt-command backfills + HumanPreference signals + PA-tool indirect naming) added post-SIGN at §20.10
sign_status: SIGN-with-edits at High confidence 0.86 (2026-07-03) via Rigby SIGN cycle 1 single-batch 4-question on arc pin pa-ae5931ea706b4537 per S1801+S1802+S1803 arc-pin routing precedent (durable-by-third-application; established as arc-standard behavior); F1 Q2-yes-with-refinement + F3 severity-phrasing tightening + F4 "by construction" two-orphan-paths phrasing + §1 "non-functional personalization loop that appears functional" biggest-architectural-risk framing + §20.10 search-strategy-breadth evidence + R0 systemic-elevation-fold landed pre-commit; D48 28th arm turn 1 CLEAN; 23rd consecutive-fully-clean-arms sub-pattern CONFIRMED per single-batch 4-question criterion
---

# Group 1800 Cat D — HumanPreference + F5 never-saved bug + reader inventory (Child Audit)

## 1. Executive Summary

Cat D is the per-user preference surface: `HumanPreference` model @ `core/models_human_interface.py:268-358`, its sole computed writer `HumanPreference.update_learned_stats()` @ `:334-358`, the source_weights mutation site @ `core/services/human_interface_service.py:724-738`, and the F5 topic_weights/source_weights never-saved bug catalogued by S1269 §1.4 governance research + S1273 §3.16 inventory row + S1274 §4.5 MEDIUM integration gap. This child audit reproduces F5 at HEAD `40d575d6`, inventories readers, catalogs governance-plane vs learning-plane vs notification-plane field usage, and answers parent §5 P4 Cat D load-bearing questions Q1-Q3.

**Headline verdicts:**

- **F1 (HIGH) — F5 is a TWO-PART BUG, not one; parent §5 HYPOTHESIS wording needs a fold.** At HEAD `40d575d6`, `HumanPreference.update_learned_stats()` @ `core/models_human_interface.py:334-358` NEVER computes `topic_weights` OR `source_weights`. Meanwhile `_update_preferences_from_decision()` @ `core/services/human_interface_service.py:724-738` computes source_weights on line 735-736 (per-decision 5% boost, capped at 2.0), assigns to `pref.source_weights`, then IMMEDIATELY calls `pref.update_learned_stats()` at line 738 — which uses `.save(update_fields=['approval_rate', 'total_decisions', 'avg_decision_time_ms', 'updated_at'])` at models_human_interface.py:356-358. **`source_weights` is explicitly EXCLUDED from update_fields**, so the local mutation on line 736 is silently discarded. The parent §5 HYPOTHESIS wording ("sets locally but never `.save()`d") is imprecise for both parts: `topic_weights` isn't set locally at all (never computed anywhere in the repo); `source_weights` IS set locally but the `.save()` call is scoped to exclude it via update_fields. Rewrite recommended at parent §2.6 row #4.

- **F2 (MED) — Reader inventory: 1 real READ site for source_weights + ZERO for topic_weights + 3 false-positive local-dict variables.** Real read: `_calculate_priority_score()` @ `core/services/human_interface_service.py:714-720` reads `pref.source_weights.get(source_type, 1.0)` with fallback 1.0 → silent identity multiplication given F1B never persists. Zero READ sites for topic_weights anywhere in the codebase (`grep -rn '\.topic_weights\|topic_weights\[' core/ ai_core/ intelligence/`). False positives: `spider_priority_engine.py:288-330` uses a local `topic_weights` variable for project analysis (NOT reading HumanPreference); `recommendation_engine.py:337-383` uses a local `source_weights` hardcoded dict for A/B test variants (NOT reading HumanPreference); `ai_core/intelligence/orchestration.py` likewise local. Frontend readers: **ZERO** — grep of `frontend/src/**/*.ts*` for `topic_weights|source_weights|topicWeights|sourceWeights` returned 0 matches. `get_preferences()` @ `human_interface_service.py:521-541` serializes `topic_weights` to REST response body (line 537) but does NOT serialize `source_weights` — asymmetric API surface.

- **F3 (MED) — F5 severity determination at HEAD = MED (silent no-op).** Because source_weights never populates, `.get(source_type, 1.0)` at :717 always returns 1.0 → identity multiplication → NO current user-facing personalization impact. Parent §3.D Q2 branch: "If zero readers, F5 is silently no-op (governance-visible only)" — the reality is nuanced: ONE reader exists (line 717) but its read is a silent no-op given F1B never persists. Impact classification: MED-severity governance-visible surface with UPGRADE-TO-HIGH pathway if F5 fix ships (line 717 becomes live personalization affecting HumanAttentionItem priority ranking).

- **F4 (HIGH) — Signal chain BROKEN: HumanFeedbackRecord.post_save does NOT invoke `HumanPreference.update_learned_stats()`.** The FeedbackProcessor post_save signal at `core/models_feedback_processing.py:372-392` fires on HumanFeedbackRecord create and calls `FeedbackProcessor.process_human_feedback()`, which writes AgentLearning + LearningInsight (Group 1300 territory). **It does NOT call `update_learned_stats()`.** The ONLY caller of `update_learned_stats()` at HEAD is `_update_preferences_from_decision()` @ `human_interface_service.py:738`, reached synchronously from `record_decision()` @ :340. **Auto-approve path bypass:** `HumanAttentionLifecycleService._auto_approve_low_risk_items()` @ `human_attention_lifecycle.py:223-296` calls `auto_approve_item()` @ :279 which creates HumanFeedbackRecord directly @ :325 — **and NEVER calls `record_decision()` or `_update_preferences_from_decision()`**. So auto-approved decisions fire FeedbackProcessor but NEVER trigger `update_learned_stats()`. Parallel to S1802 Q2 orphan case (auto-approve path bypasses `_feed_to_ml` flip). Q2-orphan case parallel is now durable-at-two-child-audits across Group 1800.

- **F5 (MED) — F5 correlation-primitive `user_pref_id` HYPOTHESIS box FOURTH application → HYPOTHESIS REMAINS. Cross-system-primitive DISPROVEN.** grep `user_pref_id|user_preference_id|preference_id` across ALL `.py` files at HEAD `40d575d6` = **ZERO hits**. `HumanPreference.id` (implicit BigAutoField PK) is NEVER referenced as an identifier variable anywhere in the codebase. Cross-system-primitive status: **DISPROVEN**. Matches S1802 `feedback_record_id` DISPROVED-CROSS-SYSTEM + S1803 `learning_event_id` DISPROVED-CROSS-SYSTEM patterns. **THIRD CONSECUTIVE F5 HYPOTHESIS-DISPROVED-CROSS-SYSTEM outcome.** Only S1801 `HAI_item_id` verified as bona fide cross-system primitive (8-10 domains). Running tally: 1 pass / 3 disprove across 4 applications. **MC-3 CODIFICATION-READY promotion path DOES NOT advance at S1804 close** — third consecutive negative outcome; xx99 §10 meta-methodology candidate strengthens (see §14 F5 for full analysis + §20.7 methodology interpretation note).

- **F6 (MED) — Notification-plane fields DEAD CODE.** Three HumanPreference fields defined but NEVER READ from HumanPreference anywhere: `preferred_channel` @ `models_human_interface.py:303-307`, `quiet_hours_start` + `quiet_hours_end` @ `:296-297`, `min_urgency_to_notify` @ `:298-302`. Grep of `quiet_hours|preferred_channel|min_urgency_to_notify` across all `.py` files finds 18 files — but ALL non-model/non-migration hits point at OLDER separate preference models (`core/models_push_notifications.py` + `core/proactive_engine.py` + `core/models_unified_system.py`), NOT HumanPreference. **Two-preference-model coexistence hypothesis:** the older push-notification-scope preferences model coexists with the newer HumanPreference model; neither reads the other's fields. Investigation warranted (see F6 §17 for boundary-violation catalog).

- **F7 (MED) — Asymmetric read + serialize surface.** `_calculate_priority_score()` @ :715-722 READS source_weights only (never topic_weights). `get_preferences()` @ :521-541 SERIALIZES `topic_weights` only (line 537) to REST response (NEVER serializes source_weights). Result: source_weights is the READ half (never SERIALIZED to user); topic_weights is the SERIALIZE half (never READ for scoring). Two half-functions layered on the wrong fields. If F5 fix computes both fields, the current read+serialize surfaces would immediately mis-align.

- **F8 (LOW) — HumanPreference has ZERO PA tool surface.** No `HumanPreference` tool schema found in `core/services/pa_tool_schemas.py`; no handler in `core/services/td_handlers*.py`; no PA route. Rigby cannot read or write HumanPreference via tools at HEAD. Contrast with HumanAttentionItem (Cat A) which HAS tool surface. Governance-plane fields (`auto_approve_low_risk`, `trusted_agents`, `blocked_sources`, `require_review_above_confidence`) are user-managed via REST API `/api/human/preferences/` only; Rigby has no observability into user's HumanPreference state.

- **F9 (LOW) — Zero admin registration; zero test coverage; zero custom manager.** HumanPreference is NOT registered in Django admin (grep of `core/admin*.py`). Zero tests in `core/tests*.py` or `tests/*.py` exercise HumanPreference or `update_learned_stats()`. No custom Manager or QuerySet on the model. Migration lineage: `0143_session_686_human_interface_layer.py` (initial CreateModel) + `0179_workspace_triggers_session_785.py` (DUPLICATE CreateModel — see F10). Parallels S1801 F9 + S1802 F9 + S1803 F9 test-gap pattern (durable-at-four-consecutive-children).

- **F10 (SPECULATIVE) — Duplicate CreateModel across migrations 0143 + 0179.** Migration `0143_session_686_human_interface_layer.py:76-97` CreateModel HumanPreference. Migration `0179_workspace_triggers_session_785.py:211-272` ALSO CreateModel HumanPreference with identical field definitions. SPECULATIVE — could be spurious `makemigrations` artifact OR a schema-reconciliation pattern. If both migrations execute, Django would fail (table already exists) — so one of the two is likely non-executing or dependency-scoped elsewhere. Investigation warranted (parallel to S1803 F4 duplicate FILES).

**Biggest architectural risk (Rigby SIGN cycle 1 fold framing):** **A non-functional personalization loop that appears functional.** The dangerous part is not that weights are dead — it's that the system silently falls back to identity multipliers at `human_interface_service.py:717` and continues operating with degraded ranking, which MASKS the failure (no error, no user visible break), PREVENTS detection (fallback is a valid float), and INVITES product decisions to be made based on a loop that isn't real. This is the compound risk of F1 + F3 + F4 together: the code path is architecturally live, the data feeding it is dead, and the failure mode is silent by design.

**Biggest gaps for future research:** (a) F5 fix scope-decision ADR — R0 top priority (Rigby SIGN cycle 1 fold elevated as SYSTEMIC learning-plane contract question, not just per-field bug); (b) two-preference-model drift consolidation ADR — R1; (c) personalization-plane consolidation (HumanPreference vs UserAgentLearning) ADR — R2; (d) signal chain wiring (post_save → update_learned_stats) — R3; (e) `trusted_agents` + `blocked_sources` enforcement wiring — R4; (f) 3 notification fields wiring OR removal — R5; (g) PA tool surface for HumanPreference — R6.

Runtime maturity classification: **PARTIAL** — governance-plane fields WORK (`auto_approve_low_risk` at `human_attention_lifecycle.py:248-249`; `require_review_above_confidence` at :272); learning-plane fields BROKEN (topic_weights + source_weights per F1); notification-plane fields DEAD (per F6); signal chain BROKEN (per F4); zero tests (per F9). Governance surface holds the maturity from EXPERIMENTAL to PARTIAL; nothing else works enough to advance to WORKING.

## 2. Domain Purpose

**Q1 What is HumanPreference and what is it responsible for?** HumanPreference is a per-user OneToOneField-scoped model @ `core/models_human_interface.py:268-358` that stores **both explicit user preferences AND system-learned statistics**. It has three planes of fields:

- **Governance plane (working):** `auto_approve_low_risk` (Boolean, default False), `require_review_above_confidence` (Float, default 0.95), `review_depth` (Choice), `trusted_agents` (JSONField list), `blocked_sources` (JSONField list). These fields are user-controllable via REST API and gate downstream lifecycle behavior.

- **Learning plane (broken per F1):** `topic_weights` (JSONField dict, default `{}`), `source_weights` (JSONField dict, default `{}`), `avg_decision_time_ms` (int), `approval_rate` (float), `total_decisions` (int). The first two are the F5-affected weights; the latter three are computed correctly by `update_learned_stats()`.

- **Notification plane (dead per F6):** `preferred_channel` (Choice), `quiet_hours_start` + `quiet_hours_end` (TimeField), `min_urgency_to_notify` (Choice). Defined but not read from HumanPreference anywhere at HEAD.

**Q2 What are the biggest gaps in this domain today?** The most load-bearing gap is F5 — the learning plane is silently dead. Additional gaps: signal chain from HumanFeedbackRecord to `update_learned_stats()` is broken (F4); notification plane is dead code / potentially superseded by an older push-notification model (F6); no PA tool surface for Rigby (F8); zero test coverage (F9). Q3 is well-covered in §14/§15.

## 3. Canonical Entry Points

### 3.1 Model definition

- `core/models_human_interface.py:268-358` (HumanPreference class). Verified at HEAD `40d575d6` via Read + Rigby ORM spot-check on 2026-07-03.
- Class docstring: `"Human preference settings - both explicit and learned."` (`:269`).
- 14 fields inventoried in §4.1 below.

### 3.2 Writer methods on the model itself

- `update_learned_stats()` @ `core/models_human_interface.py:334-358` — the ONLY computed writer on the model class. Verified via Read. Computes `approval_rate` (line 344-345), `total_decisions` (line 346), `avg_decision_time_ms` (line 353-354). **Does NOT compute `topic_weights` OR `source_weights`.** Saves via `.save(update_fields=['approval_rate', 'total_decisions', 'avg_decision_time_ms', 'updated_at'])` at lines 356-358.
- `__str__` @ `:331-332` — computes nothing.
- No other methods defined on the class.

### 3.3 Writer sites outside the model

- `HumanInterfaceService._update_preferences_from_decision()` @ `core/services/human_interface_service.py:724-738` — the SOLE non-explicit-user-request writer. Called only from `record_decision()` @ :340. Mutates `pref.source_weights` in-memory @ :735-736 then calls `pref.update_learned_stats()` @ :738 (F1B bug — mutation discarded).
- `HumanInterfaceService.update_preferences()` @ `human_interface_service.py:543-561` — explicit user preference writer via PUT `/api/human/preferences/`. Uses ALLOWLIST `['quiet_hours_start', 'quiet_hours_end', 'min_urgency_to_notify', 'preferred_channel', 'review_depth', 'auto_approve_low_risk', 'trusted_agents', 'blocked_sources']` at line 549-552. **`topic_weights` and `source_weights` explicitly EXCLUDED from user-updatable fields** (line 549-552).
- `HumanInterfaceService.get_preferences()` @ :521-541 — implicitly WRITES via `get_or_create` at line 525 (creates HumanPreference row on first access with defaults).
- `HumanInterfaceService._update_preferences_from_decision()` also uses `get_or_create` at :728.

### 3.4 Reader sites

- `HumanInterfaceService._calculate_priority_score()` @ `core/services/human_interface_service.py:714-720` — the SOLE runtime read of source_weights. Fallback `.get(source_type, 1.0)` on line 717 → silent identity multiplication given F1B never persists.
- `get_preferences()` @ :521-541 — REST API serializer read. Reads all fields for response body @ :527-541 including topic_weights (line 537) but NOT source_weights (F7 asymmetric surface).
- `HumanAttentionLifecycleService._auto_approve_low_risk_items()` @ `core/services/human_attention_lifecycle.py:248-250` — reads `HumanPreference.objects.filter(auto_approve_low_risk=True)` for the beat-scheduled auto-approve gate.
- `HumanAttentionLifecycleService._auto_approve_low_risk_items()` @ `:272` — reads `user_pref.require_review_above_confidence` for the ML confidence threshold filter.

### 3.5 API surface

- `GET /api/human/preferences/` @ URL `core/views_human_interface.py:560` → View `PreferencesView.get()` @ `core/views_human_interface.py:438-446` → Service `get_preferences()` @ `human_interface_service.py:521-541`. Auth `@login_required` @ `views_human_interface.py:40`.
- `PUT /api/human/preferences/` @ URL `core/views_human_interface.py:560` → View `PreferencesView.put()` @ :448-459 → Service `update_preferences()` @ :543-561.
- No dedicated DRF ModelSerializer for HumanPreference (manual dict construction @ :527-541).

### 3.6 Signal chain (broken per F4)

- `models_feedback_processing.py:372-392` — `post_save` signal on HumanFeedbackRecord → calls `FeedbackProcessor.process_human_feedback()` @ `:122`. **Does NOT call `HumanPreference.update_learned_stats()`.**
- No `post_save` / `pre_save` / `post_delete` / `pre_delete` signal registered on HumanPreference itself.

## 4. Major Models

### 4.1 `HumanPreference` (`core.HumanPreference`)

- **File:** `core/models_human_interface.py:268-358` verified at HEAD `40d575d6`.
- **Field-by-field inventory** (14 fields):

| Field | Type | Line | Default | null | blank | choices |
|-------|------|------|---------|------|-------|---------|
| id (implicit) | BigAutoField | (Django default) | auto | F | F | — |
| user | OneToOneField(AUTH_USER_MODEL) | 289-293 | — | F | F | related_name='human_preferences', on_delete=CASCADE |
| quiet_hours_start | TimeField | 296 | None | T | T | — |
| quiet_hours_end | TimeField | 297 | None | T | T | — |
| min_urgency_to_notify | CharField | 298-302 | 'medium' | F | F | HumanAttentionItem.URGENCY_CHOICES |
| preferred_channel | CharField | 303-307 | 'discord' | F | F | CHANNEL_CHOICES: discord/web/email |
| review_depth | CharField | 310-314 | 'standard' | F | F | REVIEW_DEPTH_CHOICES: quick/standard/thorough |
| auto_approve_low_risk | BooleanField | 315 | False | F | F | — |
| require_review_above_confidence | FloatField | 316 | 0.95 | F | F | — |
| trusted_agents | JSONField(list) | 319 | `[]` | F | F | — |
| blocked_sources | JSONField(list) | 320 | `[]` | F | F | — |
| topic_weights | JSONField(dict) | 323 | `{}` | F | F | — |
| source_weights | JSONField(dict) | 324 | `{}` | F | F | — |
| avg_decision_time_ms | IntegerField | 325 | None | T | T | — |
| approval_rate | FloatField | 326 | None | T | T | — |
| total_decisions | IntegerField | 327 | 0 | F | F | — |
| updated_at | DateTimeField | 329 | — | F | F | auto_now=True |

- **Meta class:** NONE defined. No indexes, no unique_together, no ordering, no db_table override.
- **Manager:** default Django Manager (`.objects`). No custom manager or QuerySet.
- **Related name:** `user.human_preferences` (OneToOne inverse).

### 4.2 Related models referenced by writer/reader sites

- **HumanAttentionItem** (`core.HumanAttentionItem`) @ `core/models_human_interface.py:20-227` — Cat A owns. Cat D reads `HumanAttentionItem.objects.filter(user=self.user, time_to_decision_ms__isnull=False)` @ `models_human_interface.py:349-352` inside `update_learned_stats()` for avg_decision_time_ms computation.
- **HumanFeedbackRecord** (`core.HumanFeedbackRecord`) @ `core/models_human_interface.py:230-265` — Cat B owns. Cat D reads `HumanFeedbackRecord.objects.filter(user=self.user)` @ `models_human_interface.py:339` inside `update_learned_stats()` for approval_rate + total_decisions computation.
- **AgentLearning** + **UserAgentLearning** (Group 1300 territory) — HumanPreference does NOT write to these. Cat C bridges write UserAgentLearning autonomously (per S1803 §14 F5); HumanPreference-driven learning would be a THIRD write plane if F5 were fixed. Interlocks with S1803 R6 non-bridge writers.

### 4.3 Migration lineage

- **0143_session_686_human_interface_layer.py:76-97** — initial CreateModel HumanPreference with all 14 fields.
- **0179_workspace_triggers_session_785.py:211-272** — DUPLICATE CreateModel HumanPreference with identical field definitions + AddField for `user` OneToOneField @ :682-689. **F10 SPECULATIVE:** if both migrations execute, Django would fail on CreateModel — one of the two is likely non-executing due to dependency scope. Requires archaeological investigation (git blame / migration graph analysis).

### 4.4 Retention / lifecycle posture

- **HumanPreference is SAVED-FOREVER.** No cleanup task, no expiry, no batch-delete found. Grep for `HumanPreference.objects.delete|HumanPreference.objects.filter.*delete` returns zero non-CASCADE hits.
- **CASCADE risk on user deletion** — OneToOneField(user, on_delete=CASCADE) @ :291 means hard-delete of a User row cascades to delete HumanPreference. No soft-delete handling. No pre_delete audit log signal. **Parallel S1801 F6/D7 + S1802 F6/D7 + S1803 D7 patterns; retention posture now durable-at-four-consecutive-children across Group 1800.**

## 5. Major Services

### 5.1 `HumanInterfaceService` (`core.services.human_interface_service.HumanInterfaceService`)

- **File:** `core/services/human_interface_service.py` — 784 LOC (below 3000-line god-service threshold).
- **HumanPreference-touching methods:**
  - `get_preferences()` @ :521-541 — implicit-write via `get_or_create` at :525; reads all 14 fields for REST response body (line 527-541). **F7 asymmetric surface:** serializes topic_weights (line 537) but NOT source_weights.
  - `update_preferences()` @ :543-561 — explicit user writer; allowlist at :549-552 restricts to 8 fields; excludes learning-plane weights.
  - `_calculate_priority_score()` @ :691-722 — reads `source_weights` @ :717 for HumanAttentionItem priority score multiplication. Fallback `.get(source_type, 1.0)` on line 717 → silent identity multiplication given F1B.
  - `_update_preferences_from_decision()` @ :724-738 — the F1B site. Mutates source_weights in-memory (line 732-736) then calls `pref.update_learned_stats()` (line 738) which discards the mutation via `.save(update_fields=[...])` scope.
  - `record_decision()` @ :295-353 — triggers `_update_preferences_from_decision()` at :340 (per-decision).

### 5.2 `HumanAttentionLifecycleService` (`core.services.human_attention_lifecycle.HumanAttentionLifecycleService`)

- **File:** `core/services/human_attention_lifecycle.py` — Cat A primary surface; Cat D reader for auto-approve gate.
- **HumanPreference-touching methods:**
  - `_auto_approve_low_risk_items()` @ :223-296 — reads `HumanPreference.objects.filter(auto_approve_low_risk=True)` @ :248-249 for user allowlist; reads `user_pref.require_review_above_confidence` @ :272 for threshold.
  - `auto_approve_item()` @ :298 — creates HumanFeedbackRecord directly at :325. **F4 bypass:** does NOT call `HumanInterfaceService.record_decision()` and therefore does NOT trigger `_update_preferences_from_decision()` → `update_learned_stats()`. Auto-approved items fire FeedbackProcessor signal (Cat B) but never contribute to user's learned stats on HumanPreference.

### 5.3 `FeedbackProcessor` (`core.models_feedback_processing.FeedbackProcessor`)

- **File:** `core/models_feedback_processing.py:33-330` — Cat B owns (per S1802 §5).
- **HumanPreference interaction:** NONE. FeedbackProcessor writes AgentLearning + LearningInsight (Group 1300 territory) but does NOT touch HumanPreference. F4 signal chain gap confirmed.

### 5.4 God-service check (>3000 lines)

- `human_interface_service.py`: 784 LOC — below threshold.
- `human_attention_lifecycle.py`: 728 LOC — below threshold.
- `recommendation_engine.py`: 910 LOC — below threshold; local `source_weights` dict (§14 F2 false positive).
- `spider_priority_engine.py`: 477 LOC — below threshold; local `topic_weights` variable (§14 F2 false positive).
- No god-service found in HumanPreference ecosystem.

## 6. Major APIs and Interfaces

### 6.1 REST endpoints touching Cat D

| Method | Path | View | Service | Fields R/W | Auth |
|--------|------|------|---------|------------|------|
| GET | `/api/human/preferences/` | `PreferencesView.get()` @ `views_human_interface.py:438-446` | `get_preferences()` @ `human_interface_service.py:521-541` | Reads 13 of 14 (all except source_weights per F7) | login_required @ `views_human_interface.py:40` |
| PUT | `/api/human/preferences/` | `PreferencesView.put()` @ `views_human_interface.py:448-459` | `update_preferences()` @ `human_interface_service.py:543-561` | Writes ALLOWLIST 8 fields @ :549-552 | login_required |
| POST | `/api/human/attention/<uuid:item_id>/decide/` | `AttentionDecideView.post()` @ `views_human_interface.py:157-181` | `record_decision()` @ `human_interface_service.py:295-353` → `_update_preferences_from_decision()` @ :340 | Writes (attempted) source_weights per F1B | login_required |
| GET | `/api/human/attention/` | `AttentionStreamView.get()` | `get_attention_stream()` → `_calculate_priority_score()` @ :691-722 (indirect Cat D read) | Reads source_weights indirectly | login_required |

- URL registration @ `core/views_human_interface.py:560` (verified by Agent 3).

### 6.2 WebSocket surface

- **NONE.** Grep of `core/consumers*.py` returns zero HumanPreference references (Agent 3 verified).

### 6.3 PA tool surface

- **NONE at HEAD** per F8. No `HumanPreference` schema in `pa_tool_schemas.py`; no handler in `td_handlers*.py`. Rigby cannot list / read / update HumanPreference via tools. Contrast HumanAttentionItem (Cat A) which has full tool surface. **Debt candidate — R6.**

### 6.4 Management commands

- **NONE dedicated to HumanPreference.** Grep of `core/management/commands/*.py` for HumanPreference returns zero matches (Agent 3 verified).

### 6.5 Celery / Beat surface

- **NONE dedicated to HumanPreference.** No `update_all_learned_stats` beat, no periodic recompute task. The only Cat-D-adjacent beat is `process_human_attention_lifecycle` (Cat A / Cat B territory) at 10-min cadence which triggers `_auto_approve_low_risk_items()` @ `human_attention_lifecycle.py:120-124` which READS HumanPreference (§3.4) but does not write.
- **Debt candidate — D3** parallel S1802 D-candidate #2.

### 6.6 Serializers

- **No dedicated DRF ModelSerializer** for HumanPreference. Manual dict serialization @ `human_interface_service.py:527-541`. Asymmetric per F7.

### 6.7 Discord bot integration

- **NONE direct.** `core/services/discord_bot.py` (11k+ LOC) has zero HumanPreference references (Agent 3 verified). `preferred_channel` field default 'discord' but never consumed by the Discord bot code path.

### 6.8 Frontend consumers

- REST endpoints consumed: `GET /api/human/preferences/` + `PUT /api/human/preferences/` (SPECULATIVE — specific React hook/component not identified by Agent 3 sweep; frontend grep pathway partially blocked by node_modules depth; UNKNOWN precise mount point).

## 7. Runtime Flows

### 7.1 Canonical Cat D runtime flow (explicit decision path)

```
User acts on HAI via Boardroom UI
  → POST /api/human/attention/<uuid>/decide/ 
    → AttentionDecideView.post() @ views_human_interface.py:157-181
      → HumanInterfaceService.record_decision() @ human_interface_service.py:295-353
        → creates HumanFeedbackRecord @ :325 (Cat B WRITER)
        → post_save signal fires → FeedbackProcessor.process_human_feedback() (Cat B territory — writes AgentLearning + LearningInsight)
        → _update_preferences_from_decision(item) @ :340 (Cat D writer)
          → get_or_create HumanPreference @ :728
          → if item.source_type: mutate pref.source_weights in-memory @ :732-736 (5% boost cap 2.0)
          → pref.update_learned_stats() @ :738
            → HumanFeedbackRecord.objects.filter(user=self.user).exists() @ models_human_interface.py:339-341
            → compute approval_rate, total_decisions @ :344-346
            → compute avg_decision_time_ms @ :349-354
            → self.save(update_fields=['approval_rate', 'total_decisions', 'avg_decision_time_ms', 'updated_at']) @ :356-358
            → source_weights mutation LOST (excluded from update_fields) — F1B
        → _feed_to_ml(item) @ :344 (only if human_overrode_ml) — logs only, writes fed_to_ml=True to HumanFeedbackRecord
```

### 7.2 Auto-approve runtime flow (F4 signal chain gap)

```
Celery Beat every 10 min:
  process_human_attention_lifecycle
    → HumanAttentionLifecycleService.process_lifecycle()
      → _auto_approve_low_risk_items() @ human_attention_lifecycle.py:223-296
        → HumanPreference.objects.filter(auto_approve_low_risk=True) @ :248-249 (Cat D READER)
        → candidate HAI filter @ :257-266
        → for each candidate:
          → check pref.require_review_above_confidence threshold @ :272
          → auto_approve_item(item) @ :279
            → HumanFeedbackRecord.objects.create(...) @ :325 (DIRECT Cat B writer)
            → post_save signal fires → FeedbackProcessor.process_human_feedback() (Cat B territory)
            → **AUTO-APPROVE PATH BYPASS:** does NOT call HumanInterfaceService.record_decision() or _update_preferences_from_decision() or update_learned_stats()
        → HumanPreference stays STALE for auto-approved decisions
```

### 7.3 Priority-score read flow (F1B silent no-op)

```
Create HAI via any producer path (S1801 catalog)
  → HumanInterfaceService.create_attention_item()
    → _calculate_priority_score(urgency, ml_confidence, source_type) @ :691-722
      → HumanPreference.objects.get(user=self.user) @ :716 (Cat D READER)
      → source_weight = pref.source_weights.get(source_type, 1.0) @ :717
      → score *= source_weight @ :718 (identity multiplication given F1B)
      → return score
```

## 8. Data Ownership and Lifecycle

- **Owner:** Cat D owns HumanPreference model + `update_learned_stats()` writer + `_update_preferences_from_decision()` writer + reader inventory. Cat D does NOT own HumanAttentionItem (Cat A) or HumanFeedbackRecord + FeedbackProcessor (Cat B) or LearningBridges (Cat C).
- **Lifecycle:** Created lazily via `get_or_create` on first access at `human_interface_service.py:525` or :547 or :728. SAVED-FOREVER (no cleanup). Cascade-deleted only when User is hard-deleted via OneToOneField(on_delete=CASCADE) @ `models_human_interface.py:291`.
- **Writer plane:** Explicit user writes via `update_preferences()` allowlist (8 fields). Implicit-computed writes via `update_learned_stats()` (3 fields). One partial in-memory write via `_update_preferences_from_decision()` (source_weights — DISCARDED per F1B).
- **Reader plane:** Priority scoring @ :717 (source_weights). Auto-approve gate @ `human_attention_lifecycle.py:248-249` (auto_approve_low_risk). ML confidence filter @ :272 (require_review_above_confidence). REST API serialize @ :527-541 (all fields except source_weights).

## 9. Integrations With Other Domains

### 9.1 Cross-arc handoff table (verified at HEAD)

| Domain | Group | Handoff type | Verified at HEAD | Reader/writer | Evidence |
|--------|-------|--------------|-----------------|---------------|----------|
| Governance | 1200 (S1269) | HumanPreference in per-human governance-plane inventory + F5 finding root | YES | S1269 §1.4 F5 framing + §2.4 row 30 "topic_weights/source_weights NEVER POPULATED" (Agent 5 verified §549-551 + Agent 6 confirmed §207) | Confirmed |
| Memory | 1300 (S1399) | UserAgentLearning as parallel per-user personalization surface | YES (parallel; not integrated) | S1399 §7.4 delegates Cat C learning-bridge WRITERS to Group 1800; UserAgentLearning is Group 1300 territory canonical per-user learning surface | Adjacent, not integrated |
| Revenue | 1400 (S1499) | opportunity qualification does NOT read HumanPreference | YES | Grep zero hits in revenue-domain code | MISSING integration |
| Sports | 1500 (S1599) | sports recommendation does NOT read HumanPreference | YES | Grep zero hits in sports-domain code | MISSING integration |
| Content | 1600 (S1699) | content deliberation / reviewer routing does NOT read HumanPreference | YES | `content_idea_pipeline.py` + content services grep zero matches | MISSING integration |
| Observability | 1700 (S1799) | no telemetry emitted on HumanPreference updates | YES | Grep zero telemetry/observability callsite in HumanPreference update path | MISSING integration |
| Event Architecture | 1900 (unopened) | no event bus integration | YES | No event emission in `_update_preferences_from_decision()` | Delegated to Group 1900 |

### 9.2 D80 posture evidence contribution (load-bearing for xx99 §5 four-option brief)

- **Autonomous vs HAI-mediated split for Cat D:** N/A — HumanPreference does not have a bridge writer plane. It is a user preference surface, not a signal producer. But its READERS at :717 + `human_attention_lifecycle.py:248-249,272` demonstrate that HumanPreference is a CONSUMER of governance-plane user intent, not a producer of learning signals.
- **F5 cross-system verification result:** `user_pref_id` DISPROVED-CROSS-SYSTEM (third consecutive F5 negative outcome after S1802 + S1803). Contribution to xx99 §5 posture-decision brief: consistent with the emerging pattern that Cat B/C/D primitives are domain-internal, while ONLY Cat A `HAI_item_id` operates as architectural spine.

### 9.3 Cross-domain HAI-consumer integration gap intersections

- Parent §3.D Q3 (governance intersection) — S1269 §1.4 F5 finding surfaces HumanPreference as governance-plane inventory row 30. Governance-plane fields (`auto_approve_low_risk` + `require_review_above_confidence`) are the enforcement contract downstream from user preference. F5 does NOT block governance enforcement (auto_approve gate at `human_attention_lifecycle.py:248-249` uses only Boolean field), but F5 DOES block personalization signals from feeding back into HumanPreference for future governance calibration. Governance-plane operates on user's explicit choice; learning-plane operates on user's implicit engagement — the two planes are architecturally separable and F5 affects only the second.

### 9.4 UserAgentLearning parallel surface

- **Group 1300 UserAgentLearning** (per S1803 §14 Cat C findings) is the canonical per-user learning surface: 22 write sites across 9 LearningBridge subclasses + 4 non-bridge writers. HumanPreference `topic_weights` + `source_weights` are a SECOND intended per-user learning surface — but F1 leaves them dead. **Personalization-plane consolidation ADR (R2) determines** whether HumanPreference should be revived as an independent personalization plane OR consolidated into UserAgentLearning per Group 1300 canonical.

## 10. Event Flows

- **Signals registered on HumanPreference:** NONE. No `post_save` / `pre_save` / `post_delete` / `pre_delete` receivers for HumanPreference. Confirmed via Agent 1 + Agent 6 sweeps.
- **Signals TARGETING HumanPreference (F4 signal chain gap):** HumanFeedbackRecord.post_save @ `models_feedback_processing.py:372-392` fires FeedbackProcessor but NOT `update_learned_stats()`. Intended-but-missing signal chain: HumanFeedbackRecord.post_save → HumanPreference.update_learned_stats() to close the F5 learning loop.
- **EventBus event candidates:** HumanPreference.update_learned_stats() COULD emit `human.preference.updated` on save (interlocks with Group 1900 Event Architecture arc). Not proposed here per playbook §14.5 no-implementation rule.
- **Debt candidate — D2 signal wiring.**

## 11. Existing Documentation

Per Agent 5 sweep:

- **S1269 governance research** (`docs/research/governance_authority_evolution.md`):
  - §1.4 F5 framing @ :126-131: "Human governance is the only round-trip with learning." (F5 CLAIM per S1269 is the ROUND-TRIP thesis; the "topic_weights/source_weights NEVER POPULATED" note is at §2.4 row 30 @ :207 per Agent 6 quote, and §5.3 gaps + §549-551 per Agent 5 quote.)
  - §10.7 P3 cleanup priority for F5 topic_weights/source_weights fix.
- **S1273 platform_architecture_inventory.md** §3.16 HumanAttention row @ :156-158: HumanPreference cited with "NEVER POPULATED (F5 finding, governance research §1.4)" callout linking S1273 to S1269. §4.7 canonical round-trip narrative @ :328 references HumanPreference.update_learned_stats() with "fields set locally, not saved" — Agent 5 quote.
- **S1274 cross_domain_integration_audit.md** §2.6 row 4 @ :329: OVERCOUPLED HumanPreference ↔ UserAgentLearning. §4.5 @ :661-671: MEDIUM-severity integration gap "HumanPreference.topic_weights / source_weights — Set but Never Saved". §7.5 audit findings row 17 @ :1503: recommends Learning persistence audit.
- **S1275 authority_enforcement_design_space.md** @ :398: HumanPreference in per-human governance-scoped fields list alongside AssistantProfile.role.
- **S1801 Cat A audit** (this arc): references HumanPreference in verifier_loop passage as F5 inheritance from parent scope, does NOT audit HumanPreference itself.
- **S1802 Cat B audit** (this arc): confirms `HumanInterfaceService.record_decision()` calls `update_learned_stats()` conditionally at `human_interface_service.py:340`; does NOT audit HumanPreference itself.
- **S1803 Cat C audit** (this arc): confirms Cat C bridges bypass HumanPreference entirely (100% autonomous to UserAgentLearning); does NOT audit HumanPreference itself.
- **S1800 parent scoping doc** §3.D @ :479-503 (Cat D scope + boundary rule + Q1-Q3) + §2.6 row #4 @ :333 (user_pref_id HYPOTHESIS row for this audit's F5 verification target).
- **docs/topics/content-pipeline.md**: cites UserAgentLearning as per-user personalization (parallel surface to HumanPreference's intended role — R2 consolidation ADR candidate).
- **docs/handoffs/**: S1800/S1801/S1802/S1803 handoffs mention HumanPreference as inherited-from-parent + downstream-delegated-to-Cat-D.
- **CLAUDE.md + PLATFORM_WHAT_IT_IS.md + PLATFORM_INVENTORY.md:** HumanPreference appears in inventory Database Models section (585 models total per autoblock); not featured in narrative anchor. Consistent with LIGHT/MODERATE coverage.

## 12. Research Coverage

- **Classification (per playbook §12):** **LIGHT-to-MODERATE** at HEAD pre-S1804 → **DEEP** at S1804 close.
- **Rationale pre-S1804:** F5 existence confirmed by 3 prior sessions (S1269, S1273, S1274). Model field inventory documented. Writer method identified. But reader inventory was UNKNOWN across all prior sessions. Governance-plane implications SPECULATIVE. Personalization impact UNKNOWN.
- **Rationale post-S1804:** F5 root cause verified (two-part bug at HEAD, corrected wording). Reader inventory landed (1 real read of source_weights, ZERO reads of topic_weights). Governance-plane impact analyzed (F5 does NOT block governance enforcement; F5 blocks personalization only). Cross-domain integration gaps catalogued (Groups 1400/1500/1600/1700/1900 all MISSING integration). F5 severity determined (MED silent no-op at HEAD, UPGRADE-TO-HIGH pathway if fix ships).

## 13. Architecture Maturity

- **Classification (per playbook §12):** **PARTIAL** — governance-plane holds; learning + notification + signal-chain do not.
- **Evidence:**
  - Governance-plane WORKS: `auto_approve_low_risk` read at `human_attention_lifecycle.py:248-249` gates real behavior; `require_review_above_confidence` read at :272 filters ML confidence real threshold.
  - Learning-plane BROKEN per F1: two-part bug; no persistent topic_weights or source_weights ever.
  - Notification-plane DEAD per F6: 3 fields defined but zero HumanPreference readers; potentially superseded by older push-notification model.
  - Signal chain BROKEN per F4: HumanFeedbackRecord.post_save fires but not into HumanPreference.
  - Zero tests per F9 across four consecutive children (S1801/S1802/S1803/S1804 durable-at-four).
- **Path to WORKING:** F5 fix (compute + save both fields) + signal chain wire (F4 fix) + notification-plane consolidation (F6 fix or delete) + basic test coverage (F9 fix). Not a small ticket — a scoped ADR arc.

## 14. Known Drift

### F1 (HIGH) — F5 is a TWO-PART BUG, not one; parent §5 HYPOTHESIS wording needs a fold

- **Parent §5 D78 P4 wording @ `docs/research/domains/human_attention/1800_human_attention_domain_scoping.md:487-489`:** "Writer: `HumanPreference.update_learned_stats()` — sets weights locally but never `.save()`s (F5 finding from governance research §1.4)."
- **Runtime at HEAD `40d575d6`:**
  - Part A: `topic_weights` is NEVER computed anywhere in the repo. Grep of `.topic_weights\s*=|topic_weights\[` across `core/` + `ai_core/` + `intelligence/` returns exactly ONE assignment site — the JSONField default `topic_weights = models.JSONField(default=dict)` at `models_human_interface.py:323`. NO computed writer.
  - Part B: `source_weights` IS computed at `human_interface_service.py:732-736`:
    ```python
    if item.source_type:
        weights = pref.source_weights
        current = weights.get(item.source_type, 1.0)
        weights[item.source_type] = min(2.0, current * 1.05)
        pref.source_weights = weights
    pref.update_learned_stats()
    ```
    The local mutation ATTEMPTS to persist via `.save()`, but `update_learned_stats()` at `models_human_interface.py:356-358` uses `.save(update_fields=['approval_rate', 'total_decisions', 'avg_decision_time_ms', 'updated_at'])` — **`source_weights` EXPLICITLY excluded from update_fields**.
- **Correct parent §5 wording:** should read something like: "`HumanPreference.update_learned_stats()` @ `core/models_human_interface.py:334-358` does NOT compute topic_weights OR source_weights and saves via narrow update_fields whitelist. `_update_preferences_from_decision()` @ `core/services/human_interface_service.py:724-738` computes source_weights in-memory but the mutation is discarded when it immediately calls `update_learned_stats()` (whose `.save(update_fields=[...])` scope excludes source_weights). Two-part bug: topic_weights never computed AND source_weights computed but excluded from save scope."
- **Severity: HIGH.** Two-part bug is architecturally distinct from one-part bug — fix strategies differ (Part A needs computation logic; Part B needs one-line update_fields change).

### F2 (MED) — Reader inventory: 1 real read for source_weights, ZERO reads for topic_weights, 3 false positives

- **Real reads (2 sites — same field):**
  - `human_interface_service.py:717` — `source_weight = pref.source_weights.get(source_type, 1.0)` inside `_calculate_priority_score()`. Silent no-op given F1B.
  - `human_interface_service.py:732` — `weights = pref.source_weights` inside `_update_preferences_from_decision()`. Read-modify-write pattern; local mutation persisted by F1B never lands.
- **Zero reads for topic_weights.** Confirmed via `grep -rn '\.topic_weights\|topic_weights\[' core/ ai_core/ intelligence/` at HEAD.
- **False positives (surfaced by Agent 4 broader grep):**
  - `core/services/spider_priority_engine.py:288-330` — computes a LOCAL `topic_weights` dict for project analysis; does NOT read HumanPreference.
  - `core/services/recommendation_engine.py:337-383` — uses a LOCAL `source_weights` hardcoded dict for A/B test variants (personal / collaborative / complementary / trending / temporal); does NOT read HumanPreference. Confirms per-domain personalization is being re-implemented locally because HumanPreference weights are dead.
  - `ai_core/intelligence/orchestration.py` — Agent 4 flagged as a candidate; verified at HEAD to be local variable use (not HumanPreference read).
- **Frontend reader inventory:** Zero. Agent 4 grep of `frontend/src/**/*.ts*` for `topic_weights|source_weights|topicWeights|sourceWeights` returned zero matches.
- **Serialization asymmetry (F7 companion):** `get_preferences()` @ :521-541 serializes `topic_weights` at :537 to REST response but NOT `source_weights` — inverse of read pattern.

### F3 (MED) — F5 severity at HEAD = MED silent no-op (Rigby SIGN cycle 1 phrasing tightening)

- Parent §3.D Q2 binary framing: "If zero readers, F5 is silently no-op (governance-visible only). If readers exist, F5 is silently miscomputing personalization."
- Actual reality: **1 reader exists (line 717), but its read is a silent no-op given F1B never persists.**
- **Severity phrasing (Rigby SIGN cycle 1 fold — post-cycle-1 tightening):** MED at HEAD **because the fallback identity multiplier `.get(source_type, 1.0)` @ :717 prevents any user-visible break** (score * 1.0 = unchanged score → HAI queue ordering identical to no-personalization baseline); HIGH **once weights are actively used AND non-identity multipliers affect ranking** (i.e., once F5 fix ships AND downstream consumers act on the newly-persisted values). The MED-vs-HIGH distinction hinges on **whether the ranking output is downstream-consumed** — verified at `_calculate_priority_score()` @ :691-722 returns a float score which is stored on HAI rows and drives queue ordering (per S1801 Cat A HAI producer paths). Consumption is CONFIRMED live (not logged/unused); only the input signal is dead. UPGRADE-TO-HIGH pathway is architecturally wired; only data feeding it is missing.
- Rationale (unchanged): silent identity multiplication at HEAD is architecturally MED; but the code path IS wired to affect user-facing HumanAttentionItem priority ranking. Severity assessment must distinguish CURRENT impact (MED) from POTENTIAL impact if unblocked (HIGH).

### F4 (HIGH) — Signal chain BROKEN: two orphan cases; both bypass HumanPreference BY CONSTRUCTION (Rigby SIGN cycle 1 fold — call-chain unambiguity requirement)

Both orphan cases below are structurally-wired-not-to-update-HumanPreference — this is the "by construction" framing Rigby requested. Each case is an architectural code-path choice, not an accidental miss.

- **Case 1 — FeedbackProcessor post_save bypass (does not update HumanPreference by construction):**
  - Call chain: `models_feedback_processing.py:372-392` `@receiver(post_save, sender='core.HumanFeedbackRecord')` → `FeedbackProcessor.process_human_feedback()` @ `models_feedback_processing.py:122` → writes `AgentLearning` + `LearningInsight` (Group 1300 territory per S1802 §5 Cat B verified) → returns without touching HumanPreference.
  - **By construction:** FeedbackProcessor code path is SCOPED to Group 1300 write plane (AgentLearning + LearningInsight). It has no import of HumanPreference and no reference to `update_learned_stats()`. Grep verified.
  - Intent gap: parent §5 P4 dependency clause "P2 for FeedbackProcessor→HumanPreference.update_learned_stats trigger chain" describes the INTENDED architecture that does not exist at HEAD.

- **Case 2 — Auto-approve bypass (does not update HumanPreference by construction; Q2-orphan-case parallel to S1802):**
  - Call chain: Celery Beat every 10 min → `process_human_attention_lifecycle` → `HumanAttentionLifecycleService.process_lifecycle()` @ `human_attention_lifecycle.py:120-124` → `_auto_approve_low_risk_items()` @ `:223-296` → for each candidate: `auto_approve_item(item)` @ `:279` → `HumanFeedbackRecord.objects.create(...)` @ `:325` (DIRECT model create) → returns without calling `HumanInterfaceService.record_decision()`.
  - Post-create: HumanFeedbackRecord.post_save fires (see Case 1 → routes to FeedbackProcessor → Group 1300 writes).
  - **By construction:** `HumanAttentionLifecycleService` is scoped to lifecycle-state transitions (pending → auto-approved / expired / escalated); it has no dependency injection of `HumanInterfaceService` and no reference to `_update_preferences_from_decision()` or `update_learned_stats()`. Grep verified (`recompute|backfill|update_learned_stats|_update_preferences_from_decision` in `human_attention_lifecycle.py` returns zero hits at HEAD).
  - Intent gap: auto-approved decisions ARE user's implicit preference signal — they SHOULD contribute to learned stats — but the code path is architecturally split.

- **Sole caller of `update_learned_stats()`:** `_update_preferences_from_decision()` @ `human_interface_service.py:738` — reached ONLY via `record_decision()` @ :340 which is triggered by user's explicit decision via POST `/api/human/attention/<uuid>/decide/`. All other decision paths bypass by construction.
- **Severity: HIGH.** Signal chain gap breaks the round-trip learning claim from S1269 §1.4 F5 thesis.

### F5 (MED) — F5 correlation-primitive `user_pref_id` HYPOTHESIS FOURTH application — HYPOTHESIS REMAINS. Cross-system-primitive DISPROVEN.

- **Parent §2.6 row #4 HYPOTHESIS:** `user_pref_id = HumanPreference.id` — per-user preference row identifier; written by `update_learned_stats()`.
- **Verification at HEAD:** grep `user_pref_id|user_preference_id|preference_id` across ALL `.py` files at HEAD `40d575d6` = **ZERO hits**. `HumanPreference.id` (implicit BigAutoField PK) is NEVER referenced as an identifier variable anywhere in the codebase.
- **Cross-system-primitive status: DISPROVEN.**
- **Meta-methodology tally after four applications:**
  - S1801 P1 Cat A `HAI_item_id`: **PASSED** (verified across 8-10 domains).
  - S1802 P2 Cat B `feedback_record_id`: **DISPROVED-CROSS-SYSTEM** (zero cross-domain readers).
  - S1803 P3 Cat C `learning_event_id`: **DISPROVED-CROSS-SYSTEM** (4 hits across 2 files, all `ai_core/intelligence/` domain-internal).
  - S1804 P4 Cat D `user_pref_id`: **DISPROVED-CROSS-SYSTEM** (zero hits anywhere).
- **THIRD CONSECUTIVE F5 HYPOTHESIS-DISPROVED-CROSS-SYSTEM outcome.** Running tally: 1 pass / 3 disprove across 4 applications.
- **MC-3 CODIFICATION-READY promotion path DOES NOT advance at S1804 close.** Third consecutive negative outcome strengthens the meta-methodology candidate for xx99 §10 (see §20.7 for full interpretation note).
- **Pattern observation:** Cat A HAI_item_id is a cross-domain identifier because HAI is the platform's canonical user-attention primitive with a wide producer surface; Cat B/C/D primitives (feedback_record_id, learning_event_id, user_pref_id) are all domain-internal PKs whose consumers stay within their write domain. The primitive-box discipline is confirmed as a valid research tool (hypothesis-testing works) even when hypotheses fail — that IS the finding.

### F6 (MED) — Notification-plane fields DEAD CODE at HumanPreference; older push-notification model coexists

- **HumanPreference notification fields:** `preferred_channel` @ :303-307, `quiet_hours_start` + `quiet_hours_end` @ :296-297, `min_urgency_to_notify` @ :298-302. All defined; NONE are READ from HumanPreference anywhere in the codebase.
- **Grep of `quiet_hours|preferred_channel|min_urgency_to_notify` across all `.py` files returns 18 files** — but the non-model/non-migration hits point at OLDER separate preference models:
  - `core/models_push_notifications.py` — separate model with own `quiet_hours_enabled` Boolean + hour fields (per Agent 6 report).
  - `core/services/push_notification_service.py` — READS the older model, not HumanPreference (line 232 per Agent 6).
  - `core/proactive_engine.py` — READS the older model.
  - `core/models_unified_system.py` + `core/super_platform/autonomy_engine.py` — additional coexisting preference-adjacent surfaces.
  - Migrations 0033 / 0052 / 0127 / 0143 / 0179 all touch some preference schema.
- **Two-preference-model coexistence hypothesis:** the older push-notification-scope preferences model coexists with newer HumanPreference; neither reads the other's fields at HEAD. This is a Cat D-adjacent boundary violation — Cat D notification-plane fields are dead code candidates that either need to be wired OR deleted in favor of the older push-notification model.
- **Severity: MED.** Not a runtime bug, but active codebase drift: two models representing overlapping concepts with no consolidation ADR.
- **Debt: D7.**

### F7 (MED) — Asymmetric read + serialize surface for source_weights vs topic_weights

- `_calculate_priority_score()` @ :715-722 READS `source_weights` only (never `topic_weights`).
- `get_preferences()` @ :521-541 SERIALIZES `topic_weights` only (line 537) to REST response body (NEVER serializes `source_weights`).
- Result: source_weights is the READ half (never SERIALIZED to user); topic_weights is the SERIALIZE half (never READ for scoring). Two half-functions layered on the WRONG fields — an F5 fix that computes both fields would immediately break the read/serialize asymmetry.
- **Debt: implicit in R0 fix scoping.**

### F8 (LOW) — Zero PA tool surface

- No `HumanPreference` schema in `core/services/pa_tool_schemas.py`. Agent 3 verified via grep.
- No handler in `core/services/td_handlers*.py` or `td_registry*.py`.
- No PA route touching HumanPreference.
- Rigby cannot LIST / READ / UPDATE HumanPreference via PA tools at HEAD.
- Contrast: HumanAttentionItem (Cat A) has PA tool surface per S1801.
- **Debt: D11.**

### F9 (LOW) — Zero admin + zero tests + zero custom manager

- No Django admin registration for HumanPreference.
- Zero tests found in `core/tests*.py` or `tests/*.py` (Agent 6 grep verified).
- No custom Manager or QuerySet on the model.
- Parallel S1801/S1802/S1803 test-gap pattern — **durable-at-four-consecutive-children under Group 1800**.
- **Debt: D9 test coverage + D13 admin + ownership visibility.**

### F10 (SPECULATIVE) — Duplicate CreateModel across migrations 0143 + 0179

- `0143_session_686_human_interface_layer.py:76-97` — CreateModel HumanPreference (Agent 1 verified).
- `0179_workspace_triggers_session_785.py:211-272` — DUPLICATE CreateModel HumanPreference with identical field definitions + AddField for `user` OneToOneField @ :682-689.
- SPECULATIVE — likely a schema-reconciliation migration artifact. If both migrations execute in the standard graph, Django would raise `django.db.utils.ProgrammingError: relation already exists`. One of the two is likely non-executing due to dependency scope or was retroactively synthesized.
- Not a runtime bug (Rigby ORM read confirms HumanPreference table exists and works). But an archaeological concern for migration graph integrity.
- **Debt: D12 investigation warranted.**

## 15. Known Technical Debt

### D1 (HIGH) — F5 two-part bug (F1 companion)

- Part A: topic_weights never computed.
- Part B: source_weights computed but excluded from update_fields.
- Fix scope: compute topic_weights logic + add source_weights to update_fields OR remove `update_fields=[...]` scope entirely.
- **Post-arc R0 scoping ADR required.**

### D2 (MED) — Signal chain gap (F4 companion)

- `HumanFeedbackRecord.post_save` should trigger `HumanPreference.update_learned_stats()` on every HFR create, not just explicit decision path.
- Fix scope: add signal receiver at `models_feedback_processing.py` OR add call in `auto_approve_item()` at `human_attention_lifecycle.py:325`.
- Parallel to S1802 D-candidate #2 signal-chain gap. Durable-at-two under Group 1800.

### D3 (MED) — No beat-scheduled periodic recompute of learned stats

- If `record_decision()` path is bypassed (auto-approve, external decision recording), learned stats stay stale.
- Fix scope: add beat task (~ hourly or daily) to recompute `update_learned_stats()` for all active users.
- Parallels S1803 D-candidate #3 pattern.

### D4 (MED) — OneToOneField(user, on_delete=CASCADE) with no audit trail or soft-delete

- Hard-delete of User cascades to delete HumanPreference row silently.
- No pre_delete signal to log deletion. No soft-delete flag.
- Parallel S1801 F6/D7 + S1802 F6/D7 + S1803 D-candidate CASCADE-orphan pattern. **Durable-at-four under Group 1800.**

### D5 (MED) — JSONField default=dict / default=list with no schema enforcement

- 4 fields (`trusted_agents`, `blocked_sources`, `topic_weights`, `source_weights`) accept ANY JSON shape silently.
- No pydantic/schema validation on `update_preferences()` writes for these fields.
- Silent data drift into free-form dicts/lists.
- Parallel S1803 D-candidate JSONField pattern.

### D6 (MED) — SAVED-FOREVER retention posture

- No cleanup task, no expiry, no batch-delete for HumanPreference rows.
- Rows survive user soft-deletion; only User hard-delete triggers CASCADE cleanup.
- Parallel S1801 F6/D7 + S1802 F6/D7 + S1803 D7. **Durable-at-four under Group 1800 — same retention question landing on same answer four times.**
- R7 retention posture ADR paired with prior S1801 R1 + S1802 R1 + S1803 R7.

### D7 (MED) — Notification-plane fields DEAD CODE (F6 companion)

- 3 fields defined but never READ from HumanPreference: `preferred_channel`, `quiet_hours_start/end`, `min_urgency_to_notify`.
- Older push-notification model coexists at `core/models_push_notifications.py` reading its own quiet-hours fields.
- Fix scope: consolidation ADR (which model is canonical?) — R1.

### D8 (MED) — `trusted_agents` + `blocked_sources` writable but zero readers

- Fields serialized in API response + user-updatable via PUT — but no service enforces trust/block semantics on HAI creation, notification routing, or decision gates.
- Governance intent unfulfilled.
- Fix scope: enforcement wiring — R4.

### D9 (LOW-MED) — Zero test coverage on HumanPreference + `update_learned_stats()`

- Parallels S1801/S1802/S1803 test-gap pattern. **Durable-at-four under Group 1800.**
- Fix scope: basic unit tests — R10.

### D10 (LOW) — No composite indexes

- `HumanPreference.objects.filter(auto_approve_low_risk=True)` at `human_attention_lifecycle.py:248-249` runs full-table scan on every 10-min beat.
- Fix scope: `db_index=True` on `auto_approve_low_risk` OR composite index in Meta.
- Parallel S1803 D9.

### D11 (LOW) — Zero PA tool surface (F8 companion)

- Fix scope: add HumanPreference tool + handler + list/get/update actions — R6.

### D12 (LOW-SPECULATIVE) — Duplicate CreateModel migrations (F10 companion)

- 0143 vs 0179 duplicate CreateModel — archaeological investigation warranted.

### D13 (LOW) — Zero admin registration + no CODEOWNERS entry

- No admin surface for troubleshooting user preference issues.
- No explicit DRI in .github/CODEOWNERS (grep returned no matches).
- Fix scope: add to CODEOWNERS + register in admin — R11.

## 16. Boundary Violations

### 16.1 Older push-notification preference model coexistence

- **HumanPreference** (`core/models_human_interface.py:268-358`) — created S686 (migration 0143 + duplicate in 0179).
- **Older push-notification preference model** (`core/models_push_notifications.py` + related session-scoped migrations 0033 / 0052 / 0127) — predates S686.
- Both models represent user notification preferences with overlapping but non-identical field shapes (Boolean `quiet_hours_enabled` in older; TimeField `quiet_hours_start`+`quiet_hours_end` in newer).
- Neither model reads the other's fields at HEAD.
- **Boundary violation:** two-model coexistence with zero consolidation ADR; older model still reads its own fields in `push_notification_service.py` + `proactive_engine.py`; newer model's notification fields (F6) are dead.

### 16.2 Local `topic_weights` / `source_weights` variables in unrelated services (F2 false positives)

- `spider_priority_engine.py:288-330` — LOCAL `topic_weights` dict for project analysis; NOT HumanPreference read.
- `recommendation_engine.py:337-383` — LOCAL `source_weights` hardcoded dict for A/B test variants; NOT HumanPreference read.
- These aren't boundary VIOLATIONS per se (services are free to have local variables), but they DEMONSTRATE that per-domain personalization is being re-implemented locally because HumanPreference weights are dead. If F5 were fixed, these local implementations would compete with HumanPreference as source-of-truth — future consolidation candidate.

### 16.3 Non-Cat-D writers to HumanPreference

- **CLEAN.** All writers to HumanPreference originate from Cat D-scoped surfaces:
  - `HumanInterfaceService.update_preferences()` (Cat D — explicit user path).
  - `HumanInterfaceService.get_preferences()` (Cat D — implicit get_or_create).
  - `HumanInterfaceService._update_preferences_from_decision()` (Cat D — implicit computed).
  - `HumanPreference.update_learned_stats()` (Cat D — model method).
- No Cat A / Cat B / Cat C service writes directly to HumanPreference.

## 17. Duplicate or Overlapping Systems

### 17.1 HumanPreference vs older push-notification preference model (F6 companion)

- Two coexisting user preference models with overlapping notification concerns.
- No consolidation ADR at HEAD.
- Consolidation ADR — R1 top priority after R0 F5 fix.

### 17.2 HumanPreference vs UserAgentLearning (Group 1300 territory)

- HumanPreference's learning-plane fields (topic_weights, source_weights) are intended per-user personalization but broken per F1.
- UserAgentLearning (Group 1300 per S1803 §14 Cat C) is the canonical per-user learning surface: 22 write sites across 9 LearningBridge subclasses + 4 non-bridge writers.
- Neither surface reads the other at HEAD.
- Personalization-plane consolidation ADR — R2.

### 17.3 Duplicate CreateModel migrations 0143 + 0179 (F10 companion)

- Same class in two migrations. Investigation — R12.

## 18. Ownership Gaps

- **CODEOWNERS:** No entry for `core/models_human_interface.py` or `core/services/human_interface_service.py` (Agent 6 grep returned zero matches).
- **Django admin:** No admin registration.
- **Git blame:** All non-Merge commits touching HumanPreference model definition originate from Session 686 (`97f6550e` initial), Session 746 (`20731be1` enhancements), Session ~1000 (`c854b111` Boardroom UX). No named individual DRI in commit metadata.
- **Cross-arc ownership:** Governance-plane (`auto_approve_low_risk`, `require_review_above_confidence`) is Cat D-scoped but READ by Cat A HumanAttentionLifecycleService; learning-plane (topic_weights, source_weights) is Cat D-scoped but has no active reader; notification-plane is Cat D-scoped but potentially superseded by older push-notification model.
- **Recommendation:** R11 CODEOWNERS entry + admin registration + explicit ownership doc.

## 19. Recommended Future Research

Post-arc T-slot items — Chris-gated per playbook §14.5 no-implementation rule. Ordered by architecture leverage (highest first).

### R0 (POST-ARC, HIGH — Rigby SIGN cycle 1 elevation) — F5 fix scope-decision ADR + SYSTEMIC learning-plane contract question

- **Rigby SIGN cycle 1 elevation framing:** R0 is not just "fix the F5 bug." It is a **systemic scope-decision ADR** between two mutually-exclusive alternatives:
  - **(A) Make HumanPreference real** — compute topic_weights, fix source_weights save, wire signal chain, add observability signal on updates, define retention posture, add tests. Position HumanPreference as an INDEPENDENT per-user personalization plane distinct from UserAgentLearning.
  - **(B) Deprecate / merge HumanPreference into UserAgentLearning / unified personalization plane** — retire the learning-plane fields on HumanPreference; migrate `_calculate_priority_score()` @ :717 to read UserAgentLearning; keep HumanPreference for governance-plane only.
- Without an ADR that picks one, ANY F5 fix risks becoming a localized patch that does not survive the next refactor. The pattern of dead personalization + silent identity-multiplier fallback (see §1 biggest architectural risk framing) is a SYSTEMIC gap in the platform's end-to-end contract for "learning → preference → prioritization."
- **Detailed fix scope IF path A is chosen:** (a) compute topic_weights from HumanFeedbackRecord topic classification aggregation, (b) fix source_weights save by adding to `update_fields` in `update_learned_stats()` OR removing update_fields scope entirely, (c) wire signal chain from `HumanFeedbackRecord.post_save` → `HumanPreference.update_learned_stats()` (F4 Case 1 fix), (d) add auto-approve path call in `auto_approve_item()` @ `human_attention_lifecycle.py:325` (F4 Case 2 Q2-orphan-case fix), (e) add observability signal on save, (f) define retention posture.
- **Detailed migration scope IF path B is chosen:** (a) audit UserAgentLearning per-user aggregation to verify coverage parity for source_type / topic dimensions, (b) migrate `_calculate_priority_score()` @ :717 to read UserAgentLearning-derived weights, (c) retire HumanPreference `topic_weights` + `source_weights` fields with backwards-compat migration, (d) trigger cross-arc handoff to Group 1300 Memory arc (post-close territory).
- Interlocks with: S1802 R4 F5 durability meta-methodology posture + S1803 R6 non-bridge writer routing + this session's R1 (two-preference-model consolidation) / R2 (HumanPreference-vs-UserAgentLearning consolidation) — R2 is the DELEGATED half of R0's path B.
- **Top priority under xx99 §5 posture-decision brief** — Group 1800 arc-close should elevate R0 as T0/Gate under xx99 §8, parallel to S1803 R0.

### R1 (POST-ARC, HIGH) — Two-preference-model consolidation ADR (F6 companion)

- Scope: pick canonical (HumanPreference OR older push-notification model); migrate consumers; deprecate the other.
- Blocks: any notification-plane feature work.

### R2 (POST-ARC, HIGH) — Personalization-plane consolidation ADR (HumanPreference vs UserAgentLearning)

- Scope: is HumanPreference an independent personalization plane or should it be consolidated into UserAgentLearning (Group 1300 canonical)?
- If independent: fix F5 + wire read consumers.
- If consolidated: retire HumanPreference learning fields; migrate priority scoring at `human_interface_service.py:717` to read UserAgentLearning.
- Interlocks with S1803 R6 non-bridge writer routing.

### R3 (POST-ARC, MED) — Signal chain wiring (F4 fix)

- Scope: add `post_save` receiver on HumanFeedbackRecord that calls `update_learned_stats()`, OR add batch beat task.
- Interlocks with R0.

### R4 (POST-ARC, MED) — `trusted_agents` + `blocked_sources` enforcement wiring

- Scope: HumanAttentionItem producer paths + notification routing should read `blocked_sources`; agent execution filter or dispatch should read `trusted_agents`.
- Governance intent fulfillment.

### R5 (POST-ARC, MED) — Notification-plane fields wiring OR removal

- Scope: `preferred_channel` + `quiet_hours_start/end` + `min_urgency_to_notify` — either wire consumers or delete fields. Interlocks with R1.

### R6 (POST-ARC, MED) — PA tool surface for HumanPreference (F8 fix)

- Scope: `human_preference_tool` schema + handler with list/get/update actions parallel to Cat A HumanAttentionItem tool.
- Rigby observability + user-preference troubleshooting from Rigby side.

### R7 (POST-ARC, MED) — Retention posture ADR

- Scope: SAVED-FOREVER vs date-based retention vs on-user-soft-delete cleanup. Paired with S1801 R1 + S1802 R1 + S1803 R7 as **unified Group 1800 retention posture ADR** (durable-at-four).

### R8 (POST-ARC, MED) — JSONField schema enforcement (D5 companion)

- Scope: pydantic or Django-model-validator for `trusted_agents`, `blocked_sources`, `topic_weights`, `source_weights` shape.

### R9 (POST-ARC, LOW-MED) — Composite index on `auto_approve_low_risk` (D10 companion)

- Scope: `db_index=True` OR Meta index for beat-query at `human_attention_lifecycle.py:248-249`.

### R10 (POST-ARC, LOW) — Test suite for HumanPreference + `update_learned_stats()`

- Scope: unit tests for the writer + integration test for signal chain (post R3). Parallel S1801 R + S1802 R + S1803 R test-gap items.

### R11 (POST-ARC, LOW) — CODEOWNERS entry + admin registration

- Scope: add `.github/CODEOWNERS` entry for `core/models_human_interface.py` + `core/services/human_interface_service.py`; register HumanPreference in `core/admin*.py` with list_display + readonly_fields for weight audit.

### R12 (POST-ARC, LOW) — Duplicate CreateModel migrations investigation (F10 companion)

- Scope: archaeological analysis of 0143 vs 0179 migration graph; document canonical creation site; potentially remove non-executing duplicate.

## 20. Appendix

### 20.1 Files inspected (grep-verified)

- `core/models_human_interface.py:1-490` (HumanAttentionItem + HumanFeedbackRecord + HumanPreference + HumanControlAction models).
- `core/services/human_interface_service.py:1-784` (HumanInterfaceService).
- `core/services/human_attention_lifecycle.py:1-728` (HumanAttentionLifecycleService).
- `core/services/spider_priority_engine.py:1-477` (F2 false-positive verification).
- `core/services/recommendation_engine.py:1-910` (F2 false-positive verification).
- `ai_core/intelligence/orchestration.py` (F2 false-positive verification).
- `core/models_feedback_processing.py:33-392` (FeedbackProcessor + signal receiver — F4 verification).
- `core/views_human_interface.py:40-560` (REST view routing).
- `core/migrations/0143_session_686_human_interface_layer.py:76-97` (initial CreateModel).
- `core/migrations/0179_workspace_triggers_session_785.py:211-272, 682-689` (duplicate CreateModel — F10).
- `core/models_push_notifications.py` (older-preference model coexistence — F6 verification).
- `core/services/push_notification_service.py:232` (older-preference model reader — F6 verification).
- `core/proactive_engine.py` (older-preference model reader — F6 verification).
- `docs/research/governance_authority_evolution.md:126-131, 207, 549-560` (S1269 F5 root — Agent 5 + Agent 6).
- `docs/research/platform_architecture_inventory.md:156-158, 328` (S1273 §3.16 row + §4.7 round-trip narrative).
- `docs/research/platform/cross_domain_integration_audit.md:329, 661-671, 1503` (S1274 §2.6 + §4.5 + §7.5 row 17).
- `docs/research/authority_enforcement_design_space.md:398` (S1275 governance-plane inventory).
- `docs/research/domains/human_attention/1800_human_attention_domain_scoping.md:333, 479-503` (parent §2.6 F5 row + §3.D scope).
- `docs/research/domains/human_attention/1801_human_attention_cat_a_human_attention_item_core_audit.md` (S1801 Cat A inheritance).
- `docs/research/domains/human_attention/1802_human_attention_cat_b_feedback_processor_child_audit.md` (S1802 Cat B trigger chain).
- `docs/research/domains/human_attention/1803_human_attention_cat_c_learning_bridges_child_audit.md` (S1803 Cat C bridge bypass).

### 20.2 Docs inspected

Cross-referenced above in §11.

### 20.3 Grep patterns used

- `HumanPreference` (28 hits — model + services + migrations + tests + docs).
- `topic_weights|source_weights` (7 files at HEAD — model + service + false-positive local vars + 2 migrations).
- `.topic_weights\|topic_weights\[|topic_weights\.get\(` (READ inventory F2).
- `.source_weights\|source_weights\[|source_weights\.get\(` (READ inventory F2).
- `topicWeights|sourceWeights` (frontend camelCase — zero hits).
- `user_pref_id|user_preference_id|preference_id` (F5 primitive box grep — zero hits).
- `update_learned_stats|_update_preferences_from_decision` (writer chain — 4 sites confirmed).
- `auto_approve|record_decision|HumanFeedbackRecord` in `human_attention_lifecycle.py` (F4 signal chain verification).
- `quiet_hours|preferred_channel|min_urgency_to_notify|blocked_sources|trusted_agents` (F6 dead-code + two-preference-model verification — 18 files).
- Migration-file grep for `CreateModel.*HumanPreference|migrations.CreateModel.*HumanPreference` (F10 duplicate CreateModel).
- `grep -rn '@receiver.*HumanPreference'` (F4 signal registration — zero receivers on HumanPreference).

### 20.4 Unresolved unknowns

- **Frontend UI reader mount point** for `/api/human/preferences/` GET response — SPECULATIVE per Agent 3 (React hook / component not traced).
- **Migration 0143 vs 0179 execution order** — SPECULATIVE per F10; requires migration graph analysis (`python manage.py showmigrations core` output at HEAD).
- **`ai_core/intelligence/orchestration.py` local variable** — Agent 4 flagged as candidate; F2 verification confirms local variable, but the exact line reference not captured in this audit — deferred to R0 fix scoping.
- **`_feed_to_ml()` at `human_interface_service.py:740-762` intended behavior** — comment "Feed human override back to ML system" suggests writer to AgentLearning; implementation only logs + flips fed_to_ml flag. Cat B territory per S1802; not further investigated here.
- **Rigby ORM check of HumanPreference row count in local DB** — not performed; F1 verification relied on code inspection + Rigby's spot-check of `update_learned_stats()` behavior + grep sweeps. If DB row-level inspection surfaces topic_weights populated on ANY row (via admin edit, data seed, or unknown writer), F1 Part A verdict may need refinement.

### 20.5 Conflicts between sources

- **Parent §5 D78 P4 HYPOTHESIS wording vs HEAD reality (F1 fold).** Documented as landing pre-commit in `verifier_loop` frontmatter. Parent §2.6 F5 row #4 also owes a language update to reflect DISPROVED-CROSS-SYSTEM status.
- **Agent 2 pre-Explore reported 5 callers of `update_learned_stats()` (`:161`, `:525`, `:545`, `:716`, `:728`, `:738`).** Post-Explore verifier grep at `update_learned_stats|_update_preferences_from_decision` returned ONE `update_learned_stats()` caller: `:738`. The other line numbers Agent 2 cited are `get_or_create` / `objects.get` sites for HumanPreference, NOT calls to `update_learned_stats()`. **Verdict-side error corrected in this audit.**
- **Agent 4 flagged `human_interface_service.py:344` as the `_update_preferences_from_decision` call site.** Post-Explore verifier confirms actual call is at `:340`. Off-by-4 line-cite drift; corrected in this audit.

### 20.6 Verifier-loop corrections (Rigby SIGN cycle 1 fold record — LANDED PRE-COMMIT)

- SIGN cycle 1 routed via arc pin `pa-ae5931ea706b4537` per S1801 + S1802 + S1803 arc-pin routing precedent (durable-by-third-application; established as arc-standard behavior). No fresh SIGN isolation pin minted.
- **Cycle 1 verdict: SIGN-with-edits at High confidence 0.86 (2026-07-03).**
- **Cycle 1 fold record — 6 folds landed pre-commit:**
  - **Fold #1 — §1 biggest-architectural-risk framing added.** Rigby's phrasing "A non-functional personalization loop that appears functional" adopted verbatim as §1 Executive Summary paragraph before the "Biggest gaps" section. Load-bearing framing that captures F1+F3+F4 compound impact (code path live, data dead, failure silent).
  - **Fold #2 — F3 severity phrasing tightened.** Rigby requested "MED at HEAD because fallback identity multiplier prevents user-visible break; HIGH once weights are actively used and non-identity affects ranking." Adopted verbatim + extended with downstream-consumption evidence (`_calculate_priority_score()` returns float stored on HAI rows and drives queue ordering per S1801 Cat A HAI producer paths).
  - **Fold #3 — F4 "by construction" two-orphan-paths phrasing added.** Rigby requested unambiguous call-chain phrasing per orphan. Adopted with explicit "does not update HumanPreference by construction" framing for both Case 1 (FeedbackProcessor scoped to Group 1300 write plane) and Case 2 (HumanAttentionLifecycleService scoped to lifecycle-state transitions), with grep verification cited inline.
  - **Fold #4 — R0 systemic-elevation-fold.** Rigby elevated R0 from "fix the F5 bug" to "systemic scope-decision ADR" between path A (make HumanPreference real) vs path B (deprecate/merge into UserAgentLearning). Adopted with detailed fix scope per path and delegation to R2 as R0-path-B's operational half.
  - **Fold #5 — §20.10 search-strategy-breadth evidence note added.** Rigby requested explicit statement about grep patterns + scope used for reader/writer inventories. Post-SIGN Q1 miss-vector rule-out grep results catalogued in new §20.10.
  - **Fold #6 — Parent §5 D78 P4 hypothesis fold acknowledged.** Rigby confirmed the "sets locally but never saved" wording is partially obsolete — F1 already carries the corrected two-part framing; this fold makes the acknowledgment explicit in §20.6 ledger for parent §2.6 row #4 update at S1804 close.
- **D48 27th arm HOLDING CLEAN at S1803 close → 28th arm turn 1 CLEAN at S1804 SIGN cycle 1** — 23rd-consecutive-fully-clean-arms sub-pattern CONFIRMED per single-batch 4-question criterion (S1799 §10.2 MC-2 CODIFICATION-READY promotion path advances toward CODIFICATION-CONFIRMED).

### 20.7 F5 methodology interpretation note (extending S1803 §20.7)

**Fourth application of the correlation-primitive HYPOTHESIS box discipline. Third consecutive DISPROVED-CROSS-SYSTEM outcome.**

The S1804 F5 verification of `user_pref_id` completes the FOURTH application of the primitive-box discipline (S1801 HAI_item_id + S1802 feedback_record_id + S1803 learning_event_id + S1804 user_pref_id). Aggregate: 1 pass / 3 disprove. All three DISPROVED-CROSS-SYSTEM outcomes had ZERO cross-domain reader hits (feedback_record_id: 0 across .py files outside Cat B; learning_event_id: 4 hits across 2 files in ai_core/intelligence/ only; user_pref_id: 0 hits anywhere).

The pattern that emerges: **the primitive-box discipline is a valid research tool even (perhaps especially) when hypotheses fail.** Naming a primitive with the shape "does this ID variable appear as a cross-system correlation key?" generates a hypothesis; failed hypothesis = the primitive is domain-internal (its PK does not travel outside the domain). This is not a failure of research; it's the evidence that arc scoping was correct — Cat B/C/D primitives ARE domain-internal, and the audit surfaces the boundary that already exists.

**Meta-methodology finding for xx99 §10 (candidate):**

- **CLAIM:** The correlation-primitive HYPOTHESIS box discipline (S1799 §10.2 MC-3) is a durable research tool that operates in TWO modes: (1) hypothesis PASSES → primitive verified as architectural spine; (2) hypothesis FAILS → primitive verified as domain-internal. Both outcomes are valid research.
- **EVIDENCE:** 4 applications across S1801-S1804; 1 pass / 3 fail; every application produced actionable finding (either primitive-verified or boundary-verified). Never a wasted hypothesis.
- **RECOMMENDATION for xx99 §10:** Promote MC-3 from CODIFICATION-READY (pending pass rate) to CODIFICATION-CONFIRMED (based on utility rate). The discipline earns its keep whether primitives pass or fail — the discipline itself is what matters, not the pass rate.
- **REFINEMENT candidate:** playbook v3 addition — "primitive-box HYPOTHESIS is a valid research tool with two-mode outcome semantics: PASS = architectural-spine verified; FAIL = domain-internal-boundary verified. Both modes produce audit findings; playbook does NOT require pass to advance CODIFICATION status."

### 20.8 Appendix — HumanPreference field-usage matrix (planes summary)

| Field | Plane | Written by | Read by | Status |
|-------|-------|-----------|---------|--------|
| user | Identity | get_or_create | joined everywhere | WORKING |
| quiet_hours_start | Notification | update_preferences allowlist | Nothing at HEAD | DEAD (F6) |
| quiet_hours_end | Notification | update_preferences allowlist | Nothing at HEAD | DEAD (F6) |
| min_urgency_to_notify | Notification | update_preferences allowlist | Nothing at HEAD | DEAD (F6) |
| preferred_channel | Notification | update_preferences allowlist | Nothing at HEAD | DEAD (F6) |
| review_depth | Governance | update_preferences allowlist | Nothing at HEAD | DEAD (candidate) |
| auto_approve_low_risk | Governance | update_preferences allowlist | human_attention_lifecycle.py:248-249 | WORKING |
| require_review_above_confidence | Governance | update_preferences allowlist | human_attention_lifecycle.py:272 | WORKING |
| trusted_agents | Governance | update_preferences allowlist | Nothing at HEAD | DEAD (D8) |
| blocked_sources | Governance | update_preferences allowlist | Nothing at HEAD | DEAD (D8) |
| topic_weights | Learning | NOTHING (F1A) | Serialized only in get_preferences() response @ :537 | BROKEN (F1A) |
| source_weights | Learning | _update_preferences_from_decision mutation @ :735-736 (LOST per F1B) | _calculate_priority_score @ :717 | BROKEN (F1B; silent no-op reader) |
| avg_decision_time_ms | Learning | update_learned_stats @ :353-354 | Serialized in get_preferences() response | WORKING |
| approval_rate | Learning | update_learned_stats @ :345-346 | Serialized in get_preferences() response | WORKING |
| total_decisions | Learning | update_learned_stats @ :346 | Serialized in get_preferences() response | WORKING |
| updated_at | System | auto_now on every save | Serialized in get_preferences() response | WORKING |

**Aggregate:** 6 of 16 fields WORKING (2 governance + 3 stats + 1 system); 4 DEAD notification-plane; 2 BROKEN learning-plane; 2 DEAD governance-intent (trusted_agents + blocked_sources); 1 DEAD-candidate governance (review_depth); user OneToOne WORKING as identity join.

### 20.10 Search-strategy breadth evidence (Rigby SIGN cycle 1 Q1 miss-vector rule-out — LANDED PRE-COMMIT)

Rigby SIGN cycle 1 Q1 asked for three high-probability miss vectors to be explicitly ruled out before calling reader/writer inventories complete. Post-SIGN grep executed at HEAD `40d575d6`:

**Miss vector 1 — Celery tasks / management commands that recompute or backfill preferences:**
- Grep `recompute|backfill.*preference|preference.*backfill` across all `.py` files → 5 hits: `core/tasks.py`, `core/services/workflow_orchestration_agent.py`, `core/services/priority/governor.py`, `core/services/auto_kpi_tracking.py`, `core/migrations/0201_session_861_spider_aggregation.py`. NONE are HumanPreference-related (matched on `recompute` / `backfill` in unrelated auto_kpi + priority governor + workflow ops contexts).
- Grep `preference|weights` in `core/management/commands/*.py` → 5 files (`test_prompt_layer.py`, `assign_memories_to_rooms.py`, `register_creative_agents.py`, `create_workflow_templates.py`, `connect_all_agents.py`). NONE are HumanPreference-related.
- **Verdict: NO management command or Celery task recomputes HumanPreference stats at HEAD.**

**Miss vector 2 — Signals (post_save / pre_save / post_delete / pre_delete) that touch HumanPreference outside main service:**
- Grep `@receiver.*HumanPreference|@receiver.*human_preference|post_save.*HumanPreference|pre_save.*HumanPreference|post_delete.*HumanPreference|pre_delete.*HumanPreference` across all `.py` files → **ZERO hits**.
- **Verdict: NO signal receivers registered on HumanPreference at HEAD. F4 signal-chain-broken finding fully verified.**

**Miss vector 3 — PA tool surfaces via indirect naming (e.g., "preferences" endpoints not using HumanPreference model name):**
- Grep `preference|preferences` in `core/services/pa_tool_schemas.py` → 1 file (the schemas file itself) with matches at line 2137 (`memory_tool` "save this preference" — memory categorization, NOT HumanPreference), lines 2156, 2159 (memory `category: preference` value), lines 4167-4178 (`profile_tool` actions `preferences|update_preferences|desk_preferences` routing to **UserProfile / UserPersonalContext** — a DIFFERENT model surface, NOT HumanPreference).
- **Verdict: PA tool `preferences` naming routes at UserProfile / UserPersonalContext, NOT HumanPreference. F8 zero-PA-tool-surface finding fully verified.**

**HumanPreference footprint across repo — verified complete:**
- Grep `HumanPreference|human_preferences|human_preference` across the repo → 28 files total. Non-doc files: 5 (all inventoried in §5 + §20.1):
  - `core/services/human_interface_service.py` (Cat D primary service)
  - `core/models_human_interface.py` (model definition)
  - `core/services/human_attention_lifecycle.py` (Cat D auto-approve reader)
  - `core/migrations/0143_session_686_human_interface_layer.py` (initial migration)
  - `core/migrations/0179_workspace_triggers_session_785.py` (duplicate CreateModel — F10)
- All 5 non-doc code files are already inventoried. Docs footprint (23 files) all match S1269/S1273/S1274/S1275/S1800-S1803 research library plus 2 archive docs (superseded 2026-05) plus this new S1804 doc plus 2 supporting docs (DESIGNS/HUMAN_INTERFACE_LAYER.md + EMPLOYEE_OS_PRIMITIVES.md).

**Combined verdict:** the reader + writer inventories in §3 + §4 + §5 + §14 are complete at HEAD `40d575d6`. F1 + F2 + F4 + F8 findings hold with grep-verified evidence per playbook §14 CODIFICATION-READY.

### 20.9 Frontmatter provenance

- `head_commit: 40d575d6` — verified at session open via `git rev-parse HEAD`.
- `session: 1804` — assigned per playbook §21 short-command intent by Chris directive "start research group 1804"; interpreted as S1804 P4 Cat D under Group 1800 per start-here doc + parent §5 D78 P4 slot.
- `child_slot: P4` — parent §5 D78 P4 Cat D assignment.
- `authors:` — Claude Code + Rigby collaboration per Chris-directs-Rigby-executes-Claude-verifies protocol; Rigby confirmed service_context: local + F1 pre-Explore finding on arc pin `pa-ae5931ea706b4537` at 2026-07-03.
- `playbook_application:` — NINTH application overall of §11.2 20-section child template (S1601 + S1701 + S1801 first-under-arc + S1602 + S1702 second-under-arc + S1801/S1802/S1803 additional under Group 1800 + S1804 this session — Group 1800 fourth-under-arc); durable-at-nine-consecutive-applications.
- `verifier_loop:` — pre-Explore verifier CAUGHT parent §5 P4 HYPOTHESIS wording drift (F1); post-Explore verifier CONFIRMED `user_pref_id` primitive-box DISPROVED-CROSS-SYSTEM. CODIFICATION-READY per S1799 §10.2 MC-1 sustained at S1804.
- `sign_status:` — pending SIGN cycle 1 on arc pin per S1801+S1802+S1803 arc-pin routing precedent (durable-by-third-application; established as arc-standard).
