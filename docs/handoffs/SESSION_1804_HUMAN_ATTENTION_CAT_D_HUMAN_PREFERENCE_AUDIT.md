---
session: 1804
status: closed (S1804 Group 1800 Cat D HumanPreference + F5 never-saved bug + reader inventory child audit LANDED — FOURTH child under Group 1800; NINTH application overall of playbook §11.2 20-section child template; Rigby SIGN cycle 1 SIGN-with-edits at High confidence 0.86 2026-07-03 on arc pin pa-ae5931ea706b4537; F1 two-part-bug reframing + F3 severity-phrasing tightening + F4 "by construction" two-orphan-paths phrasing + §1 "non-functional personalization loop that appears functional" biggest-architectural-risk framing + §20.10 search-strategy-breadth evidence + R0 systemic-elevation-fold folds landed pre-commit; F5 correlation-primitive `user_pref_id` HYPOTHESIS FOURTH application → HYPOTHESIS REMAINS with cross-system-primitive DISPROVEN; THIRD CONSECUTIVE F5 negative outcome after S1802 feedback_record_id + S1803 learning_event_id — running tally 1 pass / 3 disprove across 4 applications; meta-methodology finding candidate for xx99 §10 STRENGTHENS with utility-rate-vs-pass-rate framing; MC-3 CODIFICATION-READY promotion path DOES NOT advance; D48 28th arm turn 1 CLEAN; 23rd consecutive-fully-clean-arms sub-pattern CONFIRMED per single-batch 4-question criterion; no fresh SIGN isolation pin minted per S1801+S1802+S1803 arc-pin routing precedent — durable-by-fourth-application, established as arc-standard behavior)
date: 2026-07-03
arc: Research Group 1800 (HumanAttention / Feedback / Learning) — FOURTH child audit S1804 P4 Cat D HumanPreference + F5 never-saved bug + reader inventory (NINTH application overall of playbook §11.2 20-section child template)
category: research (playbook §11.2 child template NINTH application + §13 6-parallel-Explore + §14 verifier-loop REQUIRED CODIFICATION-READY pre-Explore + post-Explore + post-SIGN Q1 miss-vector rule-out grep + §15 SIGN cycle 1 single-batch 4-question)
head_commit_before: 40d575d6 (main HEAD post-S1803 close + docs cascade merge)
head_commit_after: (this session's commit — S1804 branch `research/session-1804-cat-d-human-preference-audit`)
authors: Claude Code (Chris directed via short command "start research group 1804" — interpreted per playbook §21 short-command intent as S1804 child under Group 1800 D78 P4 slot; Rigby confirmed interpretation on arc pin pa-ae5931ea706b4537; Rigby SIGN-with-edits verdict at High confidence 0.86 acceptance)
---

# Session 1804 — Group 1800 Cat D HumanPreference + F5 Never-Saved Bug + Reader Inventory Child Audit

> **Fourth child audit under Group 1800.** Playbook §11.2 20-section child template NINTH application overall. Applies playbook §14 verifier-loop REQUIRED CODIFICATION-READY (S1799 §10.2 MC-1) pre-Explore + post-Explore + post-SIGN Q1 miss-vector rule-out grep. Applies playbook §15 SIGN cycle 1 single-batch 4-question pattern (S1799 §10.2 MC-2 CODIFICATION-READY promotion path advances toward CODIFICATION-CONFIRMED at 23-consecutive-fully-clean-arms sub-pattern CONFIRMED). Applies F5 correlation-primitive HYPOTHESIS box discipline FIFTH application at child audit (S1700 parent + S1800 parent + S1801 Cat A + S1802 Cat B + S1803 Cat C + S1804 Cat D). **MC-3 CODIFICATION-READY promotion path DOES NOT advance at S1804 close — `user_pref_id` disproved as cross-system primitive (THIRD CONSECUTIVE negative outcome after S1802 feedback_record_id + S1803 learning_event_id) — meta-methodology finding candidate for xx99 §10 STRENGTHENS with utility-rate-vs-pass-rate CODIFICATION-CONFIRMED framing.**

## What shipped

### 1. S1804 child audit doc

- **`docs/research/domains/human_attention/1804_human_attention_cat_d_human_preference_child_audit.md`** (828 lines post-SIGN folds)
- `status: active` post Rigby SIGN cycle 1 SIGN-with-edits at High confidence 0.86 2026-07-03 on arc pin `pa-ae5931ea706b4537`
- `authority: child-audit for Category D per parent §5 D78 sequence + FOURTH child under Group 1800`
- `category: child_audit`, `session: 1804`, `child_slot: P4`, `domain_slug: human_attention`, `research_group: 1800`, `head_commit: 40d575d6`
- Applies playbook §11.2 20-section template NINTH application overall + FOURTH under Group 1800
- F1 two-part-bug reframing + F3 severity-phrasing tightening + F4 "by construction" two-orphan-paths phrasing + §1 biggest-architectural-risk framing + §20.10 search-strategy-breadth evidence + R0 systemic-elevation-fold folds landed pre-commit

### 2. Parent scoping doc §2.6 F5 row #4 flip

- **`docs/research/domains/human_attention/1800_human_attention_domain_scoping.md`** modified: §2.6 F5 row #4 (`user_pref_id`) flipped from HYPOTHESIS → VERIFIED-PARTIAL-AT-CHILD with cross-system-primitive DISPROVEN. Full evidence: ZERO grep hits for `user_pref_id|user_preference_id|preference_id` across ALL `.py` files at HEAD `40d575d6`; F1 TWO-PART BUG reframing corrects parent HYPOTHESIS wording — `topic_weights` NEVER computed anywhere + `source_weights` computed at `human_interface_service.py:732-736` but EXCLUDED from `update_learned_stats()` `.save(update_fields=[…])` scope at `models_human_interface.py:356-358`.

### 3. ARCHITECTURE_INDEX v54 → v55

- **`docs/research/ARCHITECTURE_INDEX.md`** modified:
  - Line 6 v55 preamble added with S1804 body detail; v54 preamble preserved below.
  - **§1.58 `domains/human_attention/1804_human_attention_cat_d_human_preference_child_audit.md`** — new section added ABOVE §1.57 with full title / purpose / status / research type / boundary rule / F1-F10 / D1-D13 / R0-R12 / cross-arc handoffs / verifier-loop discipline / dependencies / recommended next reads / overall importance / distinguishing property fields per §1.55/§1.56/§1.57 pattern.
  - **§8 timeline row S1804** added above S1803 row with load-bearing headline detail.

### 4. OPEN_ARCS Group 1800 In-progress row

- **`docs/research/OPEN_ARCS.md`** modified: Group 1800 In-progress row current-child updated S1803 → S1804 + next-expected S1805 P5 Cat E. Row preserves S1803 and prior-child references as continuity context.

### 5. Handoff + start-here

- **`docs/handoffs/SESSION_1804_HUMAN_ATTENTION_CAT_D_HUMAN_PREFERENCE_AUDIT.md`** — this document.
- **`00-START-NEXT-SESSION.md`** — overwritten to point at S1805 P5 Cat E S746 verification-loop + `record_verification` trigger discovery + writer inventory child audit as next-session mission.

## Cat D surface at HEAD `40d575d6`

- **HumanPreference model** @ `core/models_human_interface.py:268-358` (14 fields across three planes)
- **Governance plane (WORKING):** `auto_approve_low_risk` + `require_review_above_confidence` + `review_depth` + `trusted_agents` + `blocked_sources` — 2 of 5 fields ACTUALLY read at `human_attention_lifecycle.py:248-249,272`; 3 (trusted_agents + blocked_sources + review_depth) writable but zero readers.
- **Learning plane (BROKEN per F1):** `topic_weights` (JSONField dict, F1A NEVER computed) + `source_weights` (JSONField dict, F1B computed at `human_interface_service.py:735-736` but EXCLUDED from update_fields at `models_human_interface.py:356-358`) + `avg_decision_time_ms` + `approval_rate` + `total_decisions` (latter 3 WORKING via `update_learned_stats()` :344-354).
- **Notification plane (DEAD CODE per F6):** `preferred_channel` + `quiet_hours_start` + `quiet_hours_end` + `min_urgency_to_notify` — defined but NEVER READ from HumanPreference anywhere; older push-notification model at `core/models_push_notifications.py` reads its own `quiet_hours_enabled` Boolean via `push_notification_service.py:232` + `proactive_engine.py`.
- **Writer inventory:** `HumanInterfaceService.update_preferences()` @ `human_interface_service.py:543-561` (explicit user write via PUT /api/human/preferences/; allowlist 8 fields) + `HumanInterfaceService._update_preferences_from_decision()` @ `:724-738` (implicit source_weights mutation; F1B loss) + `HumanInterfaceService.get_preferences()` @ `:521-541` (implicit create via get_or_create) + `HumanPreference.update_learned_stats()` @ `models_human_interface.py:334-358` (model method; 3 stat fields).
- **Reader inventory:** `HumanInterfaceService._calculate_priority_score()` @ `:714-720` (source_weights read with fallback 1.0; F2 real) + `get_preferences()` @ :527-541 (REST response serializer; topic_weights only per F7 asymmetry) + `HumanAttentionLifecycleService._auto_approve_low_risk_items()` @ `human_attention_lifecycle.py:248-249,272` (governance-plane reads: auto_approve_low_risk + require_review_above_confidence).
- **Signal chain (BROKEN per F4):** HumanFeedbackRecord.post_save @ `models_feedback_processing.py:372-392` fires FeedbackProcessor but does NOT call `update_learned_stats()` (Case 1 by construction); auto_approve_item @ `human_attention_lifecycle.py:279-325` creates HumanFeedbackRecord directly, bypasses `record_decision()` (Case 2 by construction — Q2-orphan-case parallel to S1802 durable-at-two under Group 1800).
- **Zero PA tool surface** (verified via Rigby SIGN Q1 miss-vector rule-out — `preferences` tool @ `pa_tool_schemas.py:4167` routes at UserProfile / UserPersonalContext, NOT HumanPreference).
- **Zero admin registration + zero tests + zero custom manager** — durable-at-four-consecutive-children under Group 1800.
- **Migration lineage:** `0143_session_686_human_interface_layer.py:76-97` (initial CreateModel) + `0179_workspace_triggers_session_785.py:211-272` (DUPLICATE CreateModel with AddField for `user` OneToOneField at :682-689; F10 investigation warranted).

## Rigby SIGN cycle 1 verdict

- **Cycle 1 verdict: SIGN-with-edits at High confidence 0.86 (2026-07-03) on arc pin `pa-ae5931ea706b4537`.** No fresh SIGN isolation pin minted per S1801+S1802+S1803 arc-pin routing precedent — durable-by-fourth-application; established as arc-standard behavior.
- **Rigby CONFIRM verdicts** (per-question):
  - Q1 (miss-vector inventory completeness): CONFIRM at Medium-High with 3 high-probability miss vectors to explicitly rule out (celery/mgmt-command backfills + HumanPreference signals + PA-tool indirect naming) — landed as §20.10 addition post-SIGN.
  - Q2 (F1 two-part-bug reframing architectural correctness): CONFIRM at High — reframing is correct; parent §5 D78 P4 wording is imprecise for both parts.
  - Q3 (F5 severity MED vs HIGH at HEAD): CONFIRM at High with phrasing tightening — "MED at HEAD because fallback identity multiplier prevents user-visible break; HIGH once weights are actively used and non-identity affects ranking."
  - Q4 (compound-impact F4+F5 architectural risk): CONFIRM at High with framing elevation — "A non-functional personalization loop that appears functional" adopted verbatim into §1; R0 elevated from per-field fix to systemic scope-decision ADR between path A (make real) vs path B (deprecate/merge).
- **6 folds landed pre-commit:**
  - Fold #1 (§1 biggest-architectural-risk framing verbatim) — "A non-functional personalization loop that appears functional" captures F1+F3+F4 compound impact.
  - Fold #2 (F3 severity phrasing tightened) — Rigby's exact phrasing + extended with downstream-consumption evidence (`_calculate_priority_score()` returns float stored on HAI rows + drives queue ordering per S1801 Cat A HAI producer paths).
  - Fold #3 (F4 "by construction" two-orphan-paths phrasing) — call-chain unambiguity requirement met with explicit "does not update HumanPreference by construction" framing for both Case 1 + Case 2.
  - Fold #4 (R0 systemic-elevation-fold) — R0 elevated from "fix the F5 bug" to systemic scope-decision ADR between path A vs path B.
  - Fold #5 (§20.10 search-strategy-breadth evidence) — post-SIGN Q1 miss-vector rule-out grep results catalogued.
  - Fold #6 (Parent §5 D78 P4 hypothesis fold acknowledged) — F1 already carries the corrected two-part framing; this fold makes acknowledgment explicit in §20.6 ledger.
- **D48 27th arm HOLDING CLEAN at S1803 close → 28th arm turn 1 CLEAN at S1804 SIGN cycle 1** — 23rd-consecutive-fully-clean-arms sub-pattern CONFIRMED per single-batch 4-question criterion (S1799 §10.2 MC-2 CODIFICATION-READY promotion path advances toward CODIFICATION-CONFIRMED).

## 10 load-bearing findings F1-F10 with severity

- **F1 (HIGH)** F5 is a TWO-PART BUG, not one; parent §5 D78 P4 wording is obsolete — `topic_weights` NEVER computed anywhere in the codebase (zero writer sites); `source_weights` IS computed at `human_interface_service.py:732-736` but LOST because `update_learned_stats()` @ `models_human_interface.py:334-358` uses `.save(update_fields=['approval_rate', 'total_decisions', 'avg_decision_time_ms', 'updated_at'])` — source_weights EXPLICITLY excluded.
- **F2 (MED)** Reader inventory: 1 real read of source_weights at `human_interface_service.py:717` with fallback 1.0 → silent identity multiplication given F1B; ZERO reads of topic_weights anywhere; ZERO frontend reads; 3 false-positive local-dict variables in `spider_priority_engine.py` + `recommendation_engine.py` + `ai_core/intelligence/orchestration.py`.
- **F3 (MED)** F5 severity at HEAD = MED silent no-op (Rigby-tightened phrasing: fallback identity multiplier prevents user-visible break); UPGRADE-TO-HIGH pathway architecturally wired once F5 fix ships.
- **F4 (HIGH)** Signal chain BROKEN with two orphan cases by construction — Case 1 FeedbackProcessor post_save scoped to Group 1300 write plane (does NOT touch HumanPreference); Case 2 auto-approve @ `human_attention_lifecycle.py:279-325` bypasses `record_decision()` (Q2-orphan-case parallel to S1802 durable-at-two).
- **F5 (MED)** `user_pref_id` HYPOTHESIS FOURTH application → DISPROVED-CROSS-SYSTEM (ZERO grep hits); THIRD CONSECUTIVE F5 negative outcome; running tally 1 pass / 3 disprove; MC-3 CODIFICATION-READY promotion path DOES NOT advance.
- **F6 (MED)** Notification-plane fields DEAD CODE at HumanPreference; older push-notification model coexists.
- **F7 (MED)** Asymmetric read + serialize surface (`_calculate_priority_score()` reads source_weights only; `get_preferences()` serializes topic_weights only).
- **F8 (LOW)** Zero PA tool surface (verified via Rigby SIGN Q1 miss-vector rule-out).
- **F9 (LOW)** Zero admin + zero tests + zero custom manager (durable-at-four).
- **F10 (SPECULATIVE)** Duplicate CreateModel across migrations 0143 + 0179.

## 13 known technical debt D1-D13

D1 HIGH F5 two-part fix | D2 MED signal chain gap | D3 MED no periodic recompute beat | D4 MED CASCADE user-delete no audit trail (durable-at-four) | D5 MED JSONField no schema enforcement | D6 MED SAVED-FOREVER retention (durable-at-four) | D7 MED notification-plane DEAD CODE | D8 MED trusted_agents+blocked_sources zero readers | D9 LOW-MED zero tests (durable-at-four) | D10 LOW no composite indexes | D11 LOW zero PA tool surface | D12 LOW-SPEC duplicate CreateModel investigation | D13 LOW no admin + no CODEOWNERS.

## R0-R12 recommended future research (post-SIGN Chris-gate ordering R0 → R1 → R2 → balance)

R0 (POST-ARC HIGH — Rigby SIGN cycle 1 elevated) F5 fix scope-decision ADR + SYSTEMIC learning-plane contract question — path A make HumanPreference real vs path B deprecate/merge into UserAgentLearning | R1 two-preference-model consolidation ADR | R2 personalization-plane consolidation ADR | R3 signal chain wiring | R4 trusted_agents+blocked_sources enforcement | R5 notification-plane wiring/removal | R6 PA tool surface | R7 retention posture ADR (unified Group 1800 durable-at-four) | R8 JSONField schema enforcement | R9 composite index | R10 test suite | R11 CODEOWNERS + admin | R12 duplicate migration investigation.

## Session close artifacts committed at S1804 close

```
docs/research/domains/human_attention/1804_human_attention_cat_d_human_preference_child_audit.md   [new; 828 lines post-SIGN folds; child audit NINTH application overall + FOURTH under Group 1800]
docs/research/domains/human_attention/1800_human_attention_domain_scoping.md                       [modified — §2.6 F5 row #4 flipped to VERIFIED-PARTIAL-AT-CHILD with cross-system-primitive DISPROVEN]
docs/research/ARCHITECTURE_INDEX.md                                                                [modified — v54 → v55 with §1.58 S1804 registration + §8 timeline S1804 row + line-6 v55 preamble; v54 preamble preserved]
docs/research/OPEN_ARCS.md                                                                         [modified — Group 1800 In-progress row current-child S1803→S1804 + next-expected S1805]
docs/handoffs/SESSION_1804_HUMAN_ATTENTION_CAT_D_HUMAN_PREFERENCE_AUDIT.md                        [new — S1804 handoff]
00-START-NEXT-SESSION.md                                                                           [modified — this file; S1804 close; next-session priority = S1805 P5 Cat E]
```

## Meta-methodology finding for xx99 §10 (STRENGTHENED at S1804 close)

**Fourth application of the F5 correlation-primitive HYPOTHESIS box discipline. THIRD CONSECUTIVE DISPROVED-CROSS-SYSTEM outcome.**

Aggregate across 4 applications: 1 pass (S1801 HAI_item_id) / 3 disprove (S1802 feedback_record_id + S1803 learning_event_id + S1804 user_pref_id). All three DISPROVED-CROSS-SYSTEM outcomes had ZERO cross-domain reader hits (S1802: 0 outside Cat B; S1803: 4 hits across 2 files all in ai_core/intelligence/; S1804: 0 hits anywhere).

**Utility-rate-vs-pass-rate framing recommendation for xx99 §10:**

- Every application produced actionable finding (either primitive-verified or boundary-verified). Utility rate 4/4.
- Pass rate 1/4 does NOT reflect discipline utility; it reflects the underlying reality that most primitives are domain-internal.
- The discipline is a valid research tool in TWO modes: **PASS = primitive verified as architectural spine; FAIL = primitive verified as domain-internal boundary.** Both modes produce audit findings.
- **Recommendation for xx99 §10:** Promote MC-3 from CODIFICATION-READY (pending pass rate) to CODIFICATION-CONFIRMED (based on utility rate). The discipline earns its keep whether primitives pass or fail.
- **Refinement candidate for playbook v3:** "primitive-box HYPOTHESIS is a valid research tool with two-mode outcome semantics: PASS = architectural-spine verified; FAIL = domain-internal-boundary verified. Both modes produce audit findings; playbook does NOT require pass to advance CODIFICATION status."

## Next-session mission

**S1805 P5 Cat E S746 verification loop + `record_verification` trigger discovery + writer inventory child audit** — fifth child under Group 1800 per parent §5 D78 P5 slot. Applies playbook §11.2 20-section child template + §13 6-parallel-Explore + §14 verifier-loop REQUIRED (CODIFICATION-READY per S1799 §10.2 MC-1) pre-Explore + post-Explore + §15 Rigby SIGN cycle 1 (D48 29th arm; 24th consecutive-fully-clean-arms sub-pattern anticipated).

Cat E scope per parent §3.E:
- `HumanAttentionItem.verification_outcome` + `verified_at` + `verification_profit` + `event_completed_at` fields per S1273 §3.16 catalog.
- `HumanAttentionItem.record_verification(outcome, profit)` writer per S1274 §4.7 narrative.
- **Triggers UNDOCUMENTED per S1273 debt catalog** — who calls `record_verification` and when? Cat E's load-bearing discovery question.
- F5 correlation-primitive `verification_id` HYPOTHESIS FIFTH child verification (parent §2.6 row #5).

Cat E inherits from S1801 Cat A §14 D5 record_verification observability signal gap (HIGH — promoted MED→HIGH at S1801 SIGN) + S1802 Cat B §7.1 auto-approve path bypass Q2-orphan-case pattern + S1803 Cat C §14 F10 4 non-bridge cross-domain writers to catalog + S1804 Cat D §14 F4 auto-approve bypass durable-at-two pattern.

## Post-arc queued items (Chris-gated; inherited from S1804 + S1803 + S1802 + S1801 + prior arcs)

- **From S1804 (this arc close):** R0-R12 with post-SIGN Chris-gate ordering R0 → R1 → R2 → balance (Rigby architecture-leverage — R0 systemic scope-decision ADR path A vs path B elevated as Q4 top priority).
- **From S1803:** R0-R11 with ordering R0 → R1 → R2 → balance.
- **From S1802:** R1-R10 with ordering R6 → R4 → R7 → R1.
- **From S1801:** R1-R10 HAI plane retention + preference-aware producer factory + auto-approve blocked_sources validation + etc.
- **From Group 1700 xx99 §8.1 T0/Gate** — R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.OBSERVABILITY.D74-SPINE-POSTURE.
- **From Group 1700 xx99 §8.2 T1 CRITICAL/HIGH** (9 items).
- **From Group 1700 xx99 §8.3 T2/T3** (38 items).
- **From Group 1600 xx99 §8.1 T0/Gate** — R.CONTENT.XX99-ADR-BUNDLE.
- **From Group 1500 (S1599)** — R.SPORTS.POSTURE + R.DBAO.CODENAME.
- **From Group 1400 (S1499)** — T1-T10.
- **From Group 1300 (S1399)** — 21 follow-on items.
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600); inherited.
- **5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift** — owed to Group 1700 xx99 anchor-update PR (unresolved).
