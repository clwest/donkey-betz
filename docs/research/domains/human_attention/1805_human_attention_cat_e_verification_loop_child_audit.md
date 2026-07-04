---
title: "Group 1800 Cat E — S746 verification loop + record_verification trigger discovery + writer inventory child audit"
session: 1805
child_slot: P5
domain_slug: human_attention
research_group: 1800
category: child_audit
authority: child-audit for Category E per parent §5 D78 sequence + FIFTH child under Group 1800
head_commit: 3ff12391
status: draft
date: 2026-07-04
last_verified: 2026-07-04
authors: Claude Code (Chris directed via short command "start research group 1805" — interpreted per playbook §21 short-command intent as S1805 child under Group 1800 D78 P5 slot; Rigby confirmed service_context: local on arc pin pa-ae5931ea706b4537 via platform_config_tool overview at session open)
prior_children:
  - 1801_human_attention_cat_a_human_attention_item_core_audit.md (S1801 Cat A HAI Core)
  - 1802_human_attention_cat_b_feedback_processor_child_audit.md (S1802 Cat B FeedbackProcessor)
  - 1803_human_attention_cat_c_learning_bridges_child_audit.md (S1803 Cat C Learning bridges)
  - 1804_human_attention_cat_d_human_preference_child_audit.md (S1804 Cat D HumanPreference)
parent: 1800_human_attention_domain_scoping.md
delegates_to: []
related_arcs:
  - 1500 Sports (S1503 Cat C wager tracking + outcome verification — §1 Finding 1 CRITICAL scheduling drift identified verify_betting_outcomes NEVER FIRES; already documented automated trigger and Cat B → Cat C decoupling)
  - 1300 Memory (UserAgentLearning + AgentMemory write surfaces consumed via SportsBettingLearningBridge — closed at S1399)
  - 1400 Revenue (opportunity outcomes never verified post-close — closed at S1499)
  - 1600 Content (content performance never verified post-publish — closed at S1699)
  - 1700 Observability (failure cluster HAI never verified — closed at S1799)
  - 1900 Event Architecture (no event emission from record_verification; STATUS_VERIFIED transitions have no post_save handler — not yet opened)
playbook_application: §11.2 20-section child template TENTH application overall + FIFTH under Group 1800
verifier_loop: §14 verifier-loop REQUIRED CODIFICATION-READY (S1799 §10.2 MC-1) — pre-Explore + post-Explore performed; pre-Explore verifier CAUGHT parent §5 D78 P5 HYPOTHESIS wording drift (parent claim "triggers UNDOCUMENTED per S1273 debt catalog" is doubly obsolete — (a) S1503 already documented `betting_outcome_verifier.py:413` as automated trigger; (b) verify_betting_outcomes has NO beat schedule entry so the "automated trigger" is code-defined but never runs — see F1 for corrected two-part-drift framing); post-Explore verifier resolved Agent-2 vs Agent-6 contradiction on beat schedule via direct read of `core/celery.py:710-747` (Agent 6 mistook `process_human_attention_lifecycle` at line 719 for `verify_betting_outcomes`; Agent 2 was correct — verify_betting_outcomes has zero beat entry); post-Explore verifier also confirmed F5 `verification_id` primitive box grep = ONE hit at `intelligence/api/advisor_network_api.py:315` verified to be a DIFFERENT (advisor track record) verification object (not HAI); F5 correlation-primitive HYPOTHESIS DISPROVED-CROSS-SYSTEM (FOURTH CONSECUTIVE F5 negative outcome after S1802 feedback_record_id + S1803 learning_event_id + S1804 user_pref_id); post-SIGN Rigby cycle 1 Q1 miss-vector rule-out grep at §20.9 extended to Reddit/Bluesky non-sports bridges + Discord + management-commands + admin/staff-utility surfaces (all zero matches for `record_verification`); Rigby SIGN cycle 1 SIGN-with-edits verdict at High 0.83 confidence 2026-07-04 with §1 partial-liveness sharper-framing fold + F1 severity scoping-clarification fold + §7.4 three-plane table addition + R0 dual-sub-decision reshape
sign_status: SIGN-with-edits at High confidence 0.83 (2026-07-04) via Rigby SIGN cycle 1 single-batch 4-question on arc pin pa-ae5931ea706b4537 per S1801+S1802+S1803+S1804 arc-pin routing precedent (durable-by-fifth-application; established as arc-standard behavior); §1 partial-liveness biggest-architectural-risk phrasing fold + F1 severity clarification (LOW architectural WHEN SCOPED strictly to beat-drift; broader liveness is F1+F3+F4+R2 compound) + §7.4 three-plane manual/automated/learning table added + R0 reshape to dual-sub-decision R0a-scope + R0b-coupling-contract + §20.9 Reddit/Bluesky bridge non-caller rule-out fold landed pre-commit; D48 29th arm turn 1 CLEAN; 24th consecutive-fully-clean-arms sub-pattern CONFIRMED per single-batch 4-question criterion
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/domains/human_attention/1800_human_attention_domain_scoping.md
  - docs/research/domains/human_attention/1801_human_attention_cat_a_human_attention_item_core_audit.md
  - docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md
  - docs/research/platform_architecture_inventory.md
  - docs/research/platform/cross_domain_integration_audit.md
owner: claude
---

# Group 1800 Cat E — S746 verification loop + record_verification trigger discovery + writer inventory (Child Audit)

## 1. Executive Summary

Cat E is the S746 verification-loop surface: `HumanAttentionItem` verification-tier fields (`verification_outcome`, `verified_at`, `verification_profit`, `verification_notes`, `event_completed_at`) at `core/models_human_interface.py:155-163`; the sole writer `HumanAttentionItem.record_verification(outcome, profit, notes)` @ `:216-227`; the two callers discovered at HEAD — `core/views_human_interface.py:245` (user-driven REST endpoint) and `core/services/betting_outcome_verifier.py:413` (code-defined automated trigger, but see F1/F2 for scheduling gap); and the downstream learning-bridge consumer `SportsBettingLearningBridge.record_arbitrage_outcome()` @ `core/learning_bridges/sports_betting_bridge.py:555-598` which reads `verification_profit` + `verification_outcome` at :573-574. This child audit reproduces the parent §5 D78 P5 load-bearing questions Q1-Q4 at HEAD `3ff12391`, resolves parent §5 wording drift discovered at pre-Explore, extends S1801 Cat A D5 (record_verification learning-loop decoupling MED→HIGH promotion) to the arc-scope surface, and inventories the cross-domain verification chain — sports arbitrage is the ONLY end-to-end wired path, non-sports domains have no verifier at all.

**Headline verdicts:**

- **F1 (CRITICAL operational + LOW architectural WHEN SCOPED STRICTLY TO BEAT-DRIFT — see clarification below) — Parent §5 D78 P5 HYPOTHESIS wording is a two-part drift, not a single missing-doc; verify_betting_outcomes is defined-but-unscheduled per S1503 §1 Finding 1.** Parent §5 D78 P5 claim "Triggers UNDOCUMENTED per S1273 debt catalog" is doubly obsolete: (a) S1503 `docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md:511-514, 580, 625, 648` already documented `core/services/betting_outcome_verifier.py:413` as the automated trigger — so at the DOC level, the trigger was documented in Group 1500 (closed S1599) before Group 1800 opened; (b) more consequentially, at the RUNTIME level the automated trigger DOES NOT FIRE — `verify_betting_outcomes` @ `core/tasks.py:6121-6184` has docstring at `:6129` claiming "Runs every 2 hours via Celery Beat" but grep of `core/celery.py:1-1200` for `verify_betting_outcomes` returns **zero matches**; S1503 §1 Finding 1 confirmed with ORM probe that `PeriodicTask.objects.filter(task__in=[...]).count() == 0` AND `CeleryTaskEvent.objects.filter(task_name__in=[...], event_time__gte=now-30d).count() == 0` for both `core.tasks.verify_betting_outcomes` AND `sports.verify_betting_outcomes` variants. **Parent §5 wording must be reframed:** the P5 load-bearing question at HEAD is not "who calls?" (2 callers exist), it is "is the automated caller reachable?" (no — beat schedule missing). Parent §2.6 F5 row #5 should update accordingly. **Severity split clarification (Rigby SIGN cycle 1 fold):** F1 architectural severity is LOW **only when F1 is strictly scoped to the beat-schedule-drift** (bounded 3-5-line fix: add a `beat_schedule` entry pointing at one of the two task variants). Broader-liveness architectural risk is the compound of F1 + F3 (sports-only scope) + F4 (learning-loop decoupled) + R2 (coupling redesign) — restoring the beat schedule alone would fire the task but the loop would still be sports-only AND still skip learning propagation for REST-endpoint verifications. The "partial-liveness" biggest-architectural-risk framing below owns that compound picture; F1 in isolation remains a bounded operational patch.

- **F2 (CRITICAL) — Verification chain is architecturally live but RUNTIME DEAD for the automated path.** Combining F1 with the SPORTS-ONLY scope (F3): the automated code path from event-completion → score fetch → `record_verification()` → `SportsBettingLearningBridge.record_arbitrage_outcome()` → `UserAgentLearning` + `AgentMemory` writes is fully defined at HEAD (`betting_outcome_verifier.py` 480 lines + `sports_betting_bridge.py` 696 lines) but fires ZERO times per 30-day telemetry window. **The REST endpoint at `views_human_interface.py:245` is the SOLE live trigger** and it bypasses the learning bridge entirely — REST handler creates no `SportsBettingLearningBridge` call. Manual user verification updates `HumanAttentionItem` state but nothing downstream reads it in the same request cycle. Result: the "only round-trip learning loop" per S1274 §4.7 canonical narrative is architecturally DEFINED but data-DEAD. Severity CRITICAL operational + LOW architectural (bounded 3-5-line fix per S1503 §1 Finding 1 to add beat entry). Downgraded from CRITICAL-architectural because the code path is complete — only the scheduler is missing.

- **F3 (HIGH) — Verification chain is SPORTS-ONLY; non-sports HAI producers have NO verifier at HEAD.** `BettingOutcomeVerifier` @ `core/services/betting_outcome_verifier.py:59-63` hard-filters `HumanAttentionItem.objects.filter(status=STATUS_WATCHING, item_type='arbitrage')`. Non-sports HAI producers create verification-eligible items but no verifier consumes them: (a) revenue opportunity HAI @ `human_attention_bridge.py:256` never verifies whether opportunity converted; (b) content quality HAI @ `human_attention_bridge.py:430` never verifies whether content performed; (c) failure cluster HAI @ `human_attention_bridge.py:307` never verifies whether flagged failure was real; (d) prediction outcome tracking via `provenance_tracker.py:718,826` creates ml_prediction HAI but verification chain is separate (evaluate_ml_predictions at `tasks.py:6192` — not integrated with HAI verification surface). **Architectural risk: HIGH** — the S746 loop was designed as generalizable to all HAI items but has never been extended past sports arbitrage. **Operational risk: MED** (non-sports items may accumulate in STATUS_WATCHING indefinitely — see F6). Cross-cat parallel with S1803 §14 Cat C bridge-scope-narrow finding.

- **F4 (HIGH) — record_verification() emits NO signal / NO event / NO log line (S1801 D5 durable-at-two; extends to Cat E writer surface).** S1801 Cat A audit MED→HIGH-promoted D5 on this exact finding for the writer @ `core/models_human_interface.py:216-227`. Cat E confirms + extends: (a) writer performs plain `self.save()` at `:227` with no post_save receiver on HumanAttentionItem filtering `status=STATUS_VERIFIED` or `verification_outcome__isnull=False` — grep confirmed zero receivers via Explore Agent 2; the sole post_save handler @ `core/signals_push_notifications.py:14` filters `created=True AND urgency='critical'` and does not fire on verification transitions; (b) NO logger call inside record_verification (compared with peer `record_decision()` @ `:184-214` which similarly has no logging); (c) NO HAI_item_id in any structured log line at the verification boundary. Consequence: even IF F1 is fixed (beat schedule restored), REST-endpoint-driven verifications will NEVER touch the learning bridge because the bridge is only called from inside `BettingOutcomeVerifier._create_learning_records()` @ `:473-476`, not from `record_verification()` itself. **The learning-loop hook lives one layer above the writer — coupling is fragile.** F4 severity HIGH architectural (structural blocker for cross-domain learning-loop extensibility); durable-at-two-child-audits pattern (S1801 D5 + S1805 F4).

- **F5 (MED) — F5 correlation-primitive `verification_id` HYPOTHESIS FIFTH application → HYPOTHESIS REMAINS. Cross-system primitive DISPROVED. FOURTH CONSECUTIVE F5 negative outcome.** grep `verification_id|verification_pk|verification_uuid|verified_id` across ALL `.py` files at HEAD `3ff12391` returned **ONE hit**: `intelligence/api/advisor_network_api.py:315`. Direct verification at :300-323 confirmed the hit is a DIFFERENT verification object — `self.service.verify_advisor_track_record(advisor_id, verification_data)` at :308-311 returns an advisor-network `Verification` object (NOT HumanAttentionItem); the `verification.id` at :315 references the advisor track record verification's PK. Cross-system HAI primitive: **DISPROVED**. Matches S1802 `feedback_record_id` DISPROVED-CROSS-SYSTEM + S1803 `learning_event_id` DISPROVED-CROSS-SYSTEM + S1804 `user_pref_id` DISPROVED-CROSS-SYSTEM patterns. **FOURTH CONSECUTIVE F5 HYPOTHESIS-DISPROVED-CROSS-SYSTEM outcome.** Only S1801 `HAI_item_id` verified as bona fide cross-system primitive (8-10 domains). Running tally: **1 pass / 4 disprove across 5 applications.** MC-3 CODIFICATION-READY promotion path DOES NOT advance at S1805 close — fourth consecutive negative outcome; xx99 §10 meta-methodology candidate STRENGTHENS to CODIFICATION-CONFIRMED-CANDIDATE with utility-rate-vs-pass-rate framing (utility rate 5/5 across 5 applications catches durable structural pattern; pass rate 1/5 does not reflect discipline utility — see §20.9 methodology interpretation note extended).

- **F6 (HIGH) — STATUS_WATCHING has NO expiry / stuck-item monitoring / auto-close pathway.** HumanAttentionItem 8-state lifecycle @ `core/models_human_interface.py:36-54` includes `STATUS_WATCHING` (line 43, S746) as transient pre-verification state. HumanAttentionLifecycleService auto-dismiss ladder @ `core/services/human_attention_lifecycle.py` (LOW 72h, MEDIUM 48h, etc.) applies ONLY to `status='pending'` — grep confirmed zero application to `status='watching'`. `verify_betting_outcomes` even when it does fire only handles `item_type='arbitrage'` per F3. Result: (a) sports arbitrage items whose events were CANCELLED or whose scores failed to fetch remain in STATUS_WATCHING indefinitely; (b) non-sports items entered via `DECISION_WATCH` (per user judgment) never verify at all; (c) no beat task logs stuck-watching items. `core/services/human_interface_service.py:197-200` reports `watching_count` as a raw statistic but no threshold/alert. **Runtime consequence:** the STATUS_WATCHING backlog grows monotonically. **Operational risk: HIGH.** **Architectural risk: MED** (bounded fix: extend auto-dismiss ladder + add stuck-watching beat task).

- **F7 (MED) — Two task variants coexist at HEAD: `core.tasks.verify_betting_outcomes` + `sports.verify_betting_outcomes`; neither scheduled; different retry policies.** S1503 §1 Finding 4 documented both variants: `core.tasks.verify_betting_outcomes` @ `core/tasks.py:6121-6184` (bind=True, max_retries=2, Session-1165 budget-gated retry policy, BettingStats-recalc wrapper at :6141-6156) vs `sports.verify_betting_outcomes` @ `sports/tasks.py:414-441` (no retry, no BettingStats wrapper). Both call the same `BettingOutcomeVerifier().verify_all_pending()` at their cores. Task registry treats them as two distinct tasks (per S1503 §1 Finding 4 `name=` kwarg on `sports/tasks.py:414`). Neither has a beat schedule entry. If F1 fix picks one variant naively, retry semantics + BettingStats-recalc will silently differ from the other. **Operational risk: MED-HIGH** (F1-fix ambiguity); **architectural risk: MED** (Django-app-ownership drift adjacent to xx99 parked DBAO-schema question in parent §6.4).

- **F8 (MED) — Learning-loop coupling is FRAGILE — record_arbitrage_outcome() only reachable via the (unscheduled) BettingOutcomeVerifier orchestration.** `SportsBettingLearningBridge.record_arbitrage_outcome()` @ `core/learning_bridges/sports_betting_bridge.py:555-598` reads `arb_item.verification_profit` + `arb_item.verification_outcome` at :573-574 and writes `UserAgentLearning` + `AgentMemory`. The bridge is called from `BettingOutcomeVerifier._create_learning_records()` @ `core/services/betting_outcome_verifier.py:473-476` — this is the ONLY caller at HEAD. REST-endpoint-driven verifications @ `views_human_interface.py:245` skip the bridge entirely. If a future non-sports verifier is written (F3 fix), it must NEW-CALL the bridge or a parallel bridge — the coupling is not through the writer but through the orchestrator. **Consequence for D80 posture-decision brief:** even if S746 "runs end-to-end" per parent load-bearing question, "end-to-end" today means "when BettingOutcomeVerifier fires (which it doesn't) and only for arbitrage items." REST manual users get NO learning-loop coverage.

- **F9 (LOW-MED) — Zero test coverage on record_verification writer; zero test coverage on watch → verify state transition; durable-at-five test-gap pattern.** No test file matches `record_verification|STATUS_VERIFIED|STATUS_WATCHING|BettingOutcomeVerifier|verify_arb` under `core/tests/*.py` per Explore Agent 1 + Agent 6 verified. S1801 F9 + S1802 F9 + S1803 F9 + S1804 F9 pattern (durable-at-four → durable-at-five with S1805 F9). Parent §5 D78 debt inheritance pattern. **Runtime consequence:** F1 fix ships without regression coverage; any future change to `record_verification()` writer ships blind. Cat F.d (canonical-summary consolidation) inherits.

- **F10 (LOW) — Zero admin registration for HumanAttentionItem; no verified-items admin view; no coverage-query surface for the Cat E dimension.** Django admin @ `core/admin.py` (100 lines inspected via Explore Agent 6) registers UnifiedUser + SystemConfiguration + PlatformMetrics + GeneratedProject — zero registration for HumanAttentionItem. `core/services/human_interface_service.py:197-208` provides an in-service aggregation (verification_outcome counts + verification_profit sum) called from `get_user_statistics()` @ :260+ but there is no dedicated coverage-query surface reporting **% of HAI rows in WATCHING that never got verified** — the stuck-watching visibility gap (F6) has no monitoring surface. S1801 F9 admin-gap durable-at-five.

**Biggest architectural risk (Rigby SIGN cycle 1 fold framing at High 0.83 confidence 2026-07-04):** **A partial-liveness verification loop — manual verification updates state, automated settlement is unscheduled, and learning propagation is absent/decoupled — so the system *appears operational* while verified truth never reliably reaches downstream optimizers, and no monitoring surfaces the gap.** Rigby-tightened phrasing preserves the durable-at-two pattern thesis (false-confidence loops) while being more precise than "runtime-dead" (the REST/manual path IS live, but only for state updates — not for learning propagation). Compound F1 + F2 + F3 + F4 + F6: the loop's code is fully written, its writer is defined, its consumer bridge exists, the routing/retry policy is configured, but (a) the automated scheduler entry does not exist so the loop fires ZERO times per 30-day telemetry window; (b) manual REST-endpoint verifications DO update state but skip the learning bridge because coupling lives one layer above the writer (F4/F8); (c) the loop is defined only for sports arbitrage — non-sports domains cannot verify at all; (d) items stuck in WATCHING accumulate silently. Downstream systems optimize against MISSING truth. This is the S1804 §1 "non-functional personalization loop that appears functional" pattern durable-at-two under Group 1800 — Cat D (learning-plane dead due to persistence bug) + Cat E (partial-liveness loop with false-confidence signature). Both are silent-by-design failures that mask their own detection. See §7.4 for the three-plane manual/automated/learning breakdown that makes the partial-liveness claim precise.

**Biggest gaps for future research:** (a) R0 verification-loop scope-decision ADR (SYSTEMIC — sports-only vs generalizable-to-all-domains posture, adjacent to D80 four-option posture from parent §5); (b) R1 beat schedule restoration ADR (F1 fix vs S1503 §1 Finding 1 T-slot inheritance — Chris-gate for cadence + variant selection); (c) R2 verification learning-loop coupling redesign ADR (move learning-bridge invocation from orchestrator to post-writer signal, so REST + automated + future-non-sports paths all fire uniformly); (d) R3 STATUS_WATCHING stuck-item monitoring beat task + auto-close pathway; (e) R4 non-sports verifier skeleton (revenue opportunity outcomes, content performance, failure cluster resolution); (f) R5 admin surface + coverage-query dashboard; (g) R6 PA tool surface for verification loop (Rigby cannot query stuck-watching items or verify manually via tools at HEAD); (h) R7 test coverage on record_verification writer + BettingOutcomeVerifier settlement logic; (i) R8 two-task-variant reconciliation ADR (which variant survives, which deprecates).

Runtime maturity classification: **EXPERIMENTAL** — sports arbitrage code path defined but SCHEDULER MISSING (zero fires in 30d per S1503 §1 Finding 1); non-sports domain paths MISSING; learning loop DECOUPLED (S1801 D5 + F4); zero telemetry per F4; zero tests per F9; no admin/monitoring per F10. Advance to PARTIAL requires: (a) beat schedule restoration; (b) learning-loop signal wiring (F4/R2 fix); (c) stuck-watching monitoring (F6/R3 fix); to WORKING requires: (d) non-sports verifier + test coverage.

## 2. Domain Purpose

**Q1 What is the S746 verification loop and what is it responsible for?** The S746 verification loop is a lifecycle sub-mechanism on `HumanAttentionItem` that tracks whether a human decision to "watch" a predicted outcome ended up being correct. It captures four data points via `HumanAttentionItem.record_verification(outcome, profit, notes)` @ `core/models_human_interface.py:216-227`: (a) `verification_outcome` — 5-value enum {pending, won, lost, push, cancelled}; (b) `verification_profit` — nullable float dollar amount; (c) `verification_notes` — free text; (d) `verified_at` + `event_completed_at` — timestamps. The loop's purpose is to close the round-trip from "human chose WATCH on a prediction" (via `record_decision(decision='watch')` @ `:184-214` which transitions status pending → WATCHING and sets verification_outcome=VERIFY_PENDING) back to "outcome is now known" (via `record_verification()` which transitions WATCHING → VERIFIED). At HEAD `3ff12391`, the loop's practical scope is sports arbitrage — the sole scheduled-but-unfiring automated trigger @ `core/services/betting_outcome_verifier.py:59-63,413` filters `item_type='arbitrage'`. The REST endpoint @ `core/views_human_interface.py:213-257` is domain-agnostic (accepts arbitrary HAI id) but has no automated backfill for non-sports items.

**Q2 What are the biggest gaps in this domain today?** The most load-bearing gap is F1 (scheduler drift — automated trigger defined but never fires) combined with F3 (sports-only scope — no non-sports verifier exists). Additional gaps: F4 learning-loop hook fragile via orchestrator coupling not post-writer signal (extends S1801 D5); F6 no expiry or monitoring on stuck-WATCHING items; F9 zero test coverage on writer + settlement logic; F10 no admin registration; F8 REST-endpoint verifications skip learning bridge. The S746 loop as currently shaped is the "only round-trip w/ learning" per S1274 §4.7 canonical narrative, but that narrative describes an intended architecture that has never fully run in production at HEAD (per S1503 §1 Finding 1 30-day telemetry).

## 3. Canonical Entry Points

### 3.1 Model fields (HumanAttentionItem verification tier)

- `verification_outcome` @ `core/models_human_interface.py:155-159` — CharField(max_length=20), null+blank, choices=VERIFICATION_CHOICES. Verified via Read at HEAD.
- `verified_at` @ `:160` — DateTimeField, null+blank.
- `verification_profit` @ `:161` — FloatField, null+blank. (Note: S1503 §2 flags "profit as float" is architectural risk — betting money should be DecimalField per PlacedWager pattern; Cat E inherits this typing gap.)
- `verification_notes` @ `:162` — TextField, blank (not null).
- `event_completed_at` @ `:163` — DateTimeField, null+blank.
- **VERIFY_ enum** @ `:83-89` — 5-value: `VERIFY_PENDING='pending'`, `VERIFY_WON='won'` (label "Would Have Won"), `VERIFY_LOST='lost'` (label "Would Have Lost"), `VERIFY_PUSH='push'` (label "Push (No Action)"), `VERIFY_CANCELLED='cancelled'` (label "Event Cancelled"). Enum consumed only within HumanAttentionItem — grep confirmed zero cross-model reuse.

### 3.2 Writer method on model

- `HumanAttentionItem.record_verification(outcome, profit, notes)` @ `core/models_human_interface.py:216-227` — the SOLE model writer for Cat E fields. Signature: `def record_verification(self, outcome: str, profit: float = None, notes: str = '')`. Body assigns 4 fields + timestamps + `self.status = self.STATUS_VERIFIED` @ :226 + plain `self.save()` @ :227 (no update_fields, no post_save signal receivers). Docstring: `"Session 746: Record the verification outcome for a watched item. Call this after the event has completed to track whether it would have been profitable."`

### 3.3 Producer method that arms the verification loop

- `HumanAttentionItem.record_decision(decision, feedback, confidence)` @ `core/models_human_interface.py:184-214` — the writer that ARMS the verification loop. When called with `decision=DECISION_WATCH` (line 192-194), sets `self.status = STATUS_WATCHING` + `self.verification_outcome = VERIFY_PENDING`. This is the sole entry point that transitions HAI into the pre-verification state.

### 3.4 Automated trigger path (defined but unscheduled)

- Service: `BettingOutcomeVerifier` @ `core/services/betting_outcome_verifier.py:22-481` (~460 lines). Header docstring @ :1-10: "Closes the feedback loop for sports betting: (1) Finds pending PlacedWagerLeg records where games should be finished (2) Finds HumanAttentionItem records in 'watching' status (arb verification) (3) Fetches completed scores from The Odds API (4) Settles wagers and verifies arb items (5) Creates learning records via SportsBettingLearningBridge."
- Filter query @ :59-63: `HumanAttentionItem.objects.filter(status=HumanAttentionItem.STATUS_WATCHING, item_type='arbitrage')` — **sports-only per F3**.
- Verifier method: `_verify_arb_item(self, item, score_lookup)` @ :376-415. Outcome computation @ :392-410 compares home_score vs away_score to determine winning side; `_calculate_arb_profit()` computes profit from payload stakes + odds. Rule @ :406: `outcome='won'` if profit>0 else `'push'` if profit==0 else `'lost'`.
- Writer call @ :413: `item.record_verification(outcome=outcome, profit=profit, notes=notes)`.
- Learning-bridge call @ `_create_learning_records()` :473-476: invokes `SportsBettingLearningBridge.record_arbitrage_outcome()` — see 3.7.
- Celery task @ `core/tasks.py:6121-6184`: `verify_betting_outcomes(self)`. Decorator: `@shared_task(bind=True, max_retries=2, default_retry_delay=300, queue='default')`. Task routing override @ `core/settings.py:1385`: `'core.tasks.verify_betting_outcomes': {'queue': 'sports'}`. Retry policy: Session-1165 budget-gated (`check_retry_budget` + `compute_retry_countdown` @ :6169-6184).
- **Beat schedule: MISSING** — grep of `core/celery.py:1-1200` for `verify_betting_outcomes` returns zero matches; `docs/CELERY_AUDIT.md:469-470` inventory confirms empty beat column for both task variants; S1503 §1 Finding 1 ORM probe: 0 CeleryTaskEvent rows in 30d. Docstring @ :6129 claims "Runs every 2 hours via Celery Beat" — phantom cadence (F1 core evidence).

### 3.5 REST endpoint trigger path (user-driven, live)

- View class: `AttentionVerifyView` @ `core/views_human_interface.py:213-257`.
- Decorator @ :212: `@method_decorator([csrf_exempt, login_required], name='dispatch')`.
- URL routing: grep confirms mount at `POST /api/human/attention/{id}/verify/` (docstring @ :12-13; frontend caller confirms `/human/attention/{itemId}/verify/` @ `frontend/src/lib/api.ts:1640-1641`).
- Input schema @ :225-230: `outcome` (required str), `profit` (optional float), `notes` (optional str). **Enum validation MISSING** — outcome value is not checked against VERIFY_ enum before writer call.
- State guard @ :238-242: rejects with 400 if `item.status != STATUS_WATCHING`.
- Writer call @ :245: `item.record_verification(outcome=outcome, profit=profit, notes=notes)`.
- Response @ :253-256: returns 4 fields (verification_outcome, verification_profit, verified_at + timestamps).
- **NO learning bridge call in the REST handler** — user-driven verifications skip the SportsBettingLearningBridge coupling entirely.

### 3.6 Second automated trigger variant (also unscheduled)

- Task @ `sports/tasks.py:414-441`: `sports.verify_betting_outcomes` (per S1503 §1 Finding 4; not re-verified in this audit — inherit S1503 evidence).
- Distinct from `core.tasks.verify_betting_outcomes` — same body (both call `BettingOutcomeVerifier().verify_all_pending()`) but no retry policy, no BettingStats-recalc wrapper.
- **Beat schedule: also MISSING** (S1503 §1 Finding 1 confirmed both variants have zero CeleryTaskEvent rows in 30d).

### 3.7 Downstream learning-bridge consumer

- Bridge method: `SportsBettingLearningBridge.record_arbitrage_outcome(arb_item)` @ `core/learning_bridges/sports_betting_bridge.py:555-598`.
- Reads `arb_item.verification_profit` @ :573 (`actual_profit = arb_item.verification_profit or 0`) + `arb_item.verification_outcome` @ :574 (`outcome = arb_item.verification_outcome`).
- Writes `UserAgentLearning` + `AgentMemory` rows (per Explore Agent 4 verified; specific write sites at bridge :555-598).
- Sole caller: `BettingOutcomeVerifier._create_learning_records()` @ `betting_outcome_verifier.py:473-476` — **not called from REST endpoint per §3.5**.

### 3.8 Serialization surfaces (readers on Cat E fields)

- `core/services/human_interface_service.py:116-120` — full 5-field export (verification_outcome + verified_at + verification_profit + verification_notes NOT included — 4 fields listed here + event_completed_at). Called from GET /api/human/attention/{id}/ serializer.
- `core/services/human_interface_service.py:197-208` — aggregation surface: counts by verification_outcome (excluding null) @ :199-203 + sum verification_profit @ :207-208. Called from `get_user_statistics()` @ :260+.
- `core/views_human_interface.py:130-133` — GET /api/human/attention/{id}/ response includes 4 verification fields.
- `core/views_human_interface.py:253-256` — POST /api/human/attention/{id}/verify/ response echoes 3 fields.
- `core/views_platform_command.py:750-752, 822-824` — platform command view serialization.
- **Asymmetric surface (F7 candidate — durable-at-two under Group 1800 with S1804 F7):** the `verification_notes` field is stored @ :162 but not consistently serialized to REST responses. `event_completed_at` is stored @ :163 but leaked only in `human_interface_service.py:120`, not in views. See §14 drift.

### 3.9 API surface for the loop (not covered in §3.5)

- `GET /api/human/attention/{id}/` @ `core/views_human_interface.py:84-135` — reads 4 verification fields into response.
- `GET /api/human/attention/stats/` @ `core/views_human_interface.py:139-150` — invokes service aggregation (§3.8).
- No dedicated GET endpoint for "list stuck-watching items" or "list verified items with outcome X" — F6/F10 monitoring gap.

## 4. Major Models

### 4.1 `HumanAttentionItem` (verification tier only — full model catalog in S1801 Cat A)

- Cat E scope: 5 fields listed in §3.1 + writer `record_verification()` + reader/producer `record_decision()` when decision=WATCH.
- Meta @ `:165-172`: no verification-specific index. Existing indexes: `(user, status)`, `(user, urgency)`, `(source_type,)`, `(created_at,)`. **No composite (user, verification_outcome)** — F10 monitoring-gap contributor (queries filtering stuck-watching by user require full user-scoped scan).
- Migration lineage: `core/migrations/0179_workspace_triggers_session_785.py:99-116` — initial CreateModel with all 5 verification fields inline. No AlterField/AddField migrations found post-0179 (grep across `core/migrations/*.py` for `verification_outcome|verification_profit|verified_at` returned zero non-0179 hits at HEAD).
- No FK relationship from any other model back to HumanAttentionItem specifically for verification. HumanAttentionItem is terminal for the verification-tier relationship — no VerificationLog table, no VerificationTrigger table, no Verification-tier N:1 dependent models.
- **VERIFY_ enum reuse: ZERO cross-model.** Grep of `VERIFY_PENDING|VERIFY_WON|VERIFY_LOST|VERIFY_PUSH|VERIFY_CANCELLED` outside `core/models_human_interface.py` returned zero matches.

### 4.2 Related models referenced by verification path

- `PlacedWager` + `PlacedWagerLeg` @ `core/models_betting.py` — Cat B/C sports models (S1503 audit territory); consumed by `BettingOutcomeVerifier` for settlement but NOT written by `record_verification()` — settlement logic runs pre-verification via a DIFFERENT method on the verifier (`_settle_wager()` per S1503 §2). Cat E and PlacedWager settlement are TWO ORTHOGONAL surfaces of the same beat task.
- `UserAgentLearning` @ `core/models_agent_persistence.py` (or equivalent) — written by SportsBettingLearningBridge downstream of verification.
- `AgentMemory` @ `core/models_agent_persistence.py` — written by SportsBettingLearningBridge downstream of verification.

## 5. Major Services

### 5.1 `BettingOutcomeVerifier` (core verifier — sports-only)

- File: `core/services/betting_outcome_verifier.py:22-481` (~460 lines).
- Purpose per header: closes S746 verification loop for sports betting. Two surfaces: (a) `PlacedWagerLeg` settlement + `PlacedWager` status transitions (S1503 Cat C scope); (b) `HumanAttentionItem` arbitrage verification (Cat E scope).
- Entry point: `verify_all_pending()` @ :30-99 — orchestrator that runs both surfaces.
- Cat E surface method: `_verify_arb_item(item, score_lookup)` @ :376-415. Outcome logic @ :392-410; profit computation @ `_calculate_arb_profit()` @ :417-453 (per Explore Agent 2 report); writer call @ :413.
- Learning-record creation: `_create_learning_records()` @ :455-480 (per S1503 §2 + this audit Explore Agent 2). Calls `SportsBettingLearningBridge.record_wager_outcome()` for settled wagers AND `.record_arbitrage_outcome()` for verified arb items (bridge method inventory).
- **Sports-only scope enforced by filter at :59-63** — see F3 for cross-domain implication.

### 5.2 `SportsBettingLearningBridge` (learning consumer)

- File: `core/learning_bridges/sports_betting_bridge.py` (~696 lines per S1503 audit; not re-inspected in this audit).
- Cat E-relevant method: `record_arbitrage_outcome(arb_item)` @ :555-598 — reads verification_profit + verification_outcome @ :573-574; writes UserAgentLearning + AgentMemory.
- Peer method: `record_wager_outcome(wager)` @ :488-551 (per S1503) — writes UserAgentLearning + AgentMemory with `source_type='betting_outcome_verification'` @ :546.
- Sole caller of both bridge methods: `BettingOutcomeVerifier._create_learning_records()` — coupling per F8.

### 5.3 `HumanInterfaceService` (aggregation reader)

- File: `core/services/human_interface_service.py`.
- Cat E-relevant methods: `_get_stats()` includes verification_outcome dict + verification_profit sum via :199-208; `get_user_statistics()` @ :260+ calls the aggregation.
- Called from GET /api/human/attention/stats/ view.

### 5.4 `HumanAttentionLifecycleService` (auto-approve; adjacent surface)

- File: `core/services/human_attention_lifecycle.py`.
- **NOT** a Cat E component — governs auto-approve for STATUS_PENDING items per Cat A (S1801). Included here as **explicit NON-participant** in verification loop: `_auto_approve_low_risk_items()` handles the pending→acted transition, not pending→watching or watching→verified. See F6 for the stuck-watching gap this creates.

### 5.5 Non-participants (explicit NOT-Cat-E)

- `FeedbackProcessor` @ `core/services/feedback_processor.py` — Cat B territory (S1802). Grep of `record_verification|verification_outcome|STATUS_WATCHING|STATUS_VERIFIED` across `feedback_processor.py` and `models_feedback_processing.py`: zero matches. Cat B does NOT participate in verification loop.
- Non-sports learning bridges (RedditLearningBridge, BlueskyLearningBridge, etc. @ `ai_core/intelligence/`) — Cat F.a territory (S1806). Grep of Cat E field names across these bridges: zero matches per Explore Agent 4 domain classification table. These bridges are producer-side external social bridges, not verification consumers.

## 6. Major APIs and Interfaces

### 6.1 REST endpoints

- `POST /api/human/attention/{id}/verify/` — user-driven writer; see §3.5.
- `GET /api/human/attention/{id}/` — full item serialization including verification fields; see §3.8.
- `GET /api/human/attention/stats/` — aggregation surface; see §3.8.
- **NO endpoint** for: list-stuck-watching-items, list-verified-items-by-outcome, list-user's-verification-history, cancel-watching-item, re-open-verified-item. F10 monitoring/UX gap.

### 6.2 WebSocket consumers

- **ZERO Cat E-specific WS consumers** per Explore Agent 3 grep of `core/consumers*.py`, `core/websockets*.py`. No push notification fires on STATUS_VERIFIED transition. No live update stream for verification outcomes.

### 6.3 PA tool surface (Rigby)

- **ZERO Cat E PA tools** per Explore Agent 3 grep of `core/services/pa_tool_schemas.py` + `core/services/td_handlers*.py`. Adjacent hits (`verify_deploy` @ `td_handlers_core.py:837-849`) are unrelated deploy verification.
- Rigby CAN issue `record_decision(decision='watch')` via existing HAI decision tool (PA tool schema @ `pa_tool_schemas.py:3197-3207` per Explore Agent 2). Rigby CANNOT: manually verify (`record_verification`), query stuck-watching items, aggregate verification outcomes per-user, or subscribe to verification events.
- **Contrast with S1801 Cat A tool surface** — Cat A HAI decision tools exist. Cat E writer surface is entirely absent. R6 candidate.

### 6.4 Discord bot integration

- **ZERO Cat E-specific Discord commands** per Explore Agent 3 grep of `core/services/discord_bot.py`. Adjacent hits (`link_account` verification-code, Session 429) are unrelated account linking.
- Sports Discord commands `/bet`, `/resolve`, `/slip`, `/bankroll` (S1503 territory) write to `Bankroll` model (Discord surface), not to `PlacedWager` (core surface). This is S1503 §1 Finding 5 dual-aggregation drift; Cat E is peripheral — the `/resolve` command per S1503 does not invoke `HumanAttentionItem.record_verification()`.

### 6.5 Management commands

- **ZERO Cat E management commands** per Explore Agent 3 grep of `core/management/commands/*.py`. Adjacent matches (`ops_verify.py`, `verify_doc_claims.py`, `verify_surgical_moves.py`) are unrelated to sports/HAI verification. No `manage.py verify_pending_arb_items`, no `manage.py list_stuck_watching`, no `manage.py backfill_verification_outcomes`. F10 monitoring gap + no operator remediation path.

### 6.6 Frontend surface

- Frontend API caller @ `frontend/src/lib/api.ts:1640-1641` — `humanAttentionApi.verify(itemId, outcome, profit?, notes?) → POST /human/attention/{itemId}/verify/`.
- Consuming component: NOT located via grep of `frontend/src/**/*.ts*` for verification field names (per Explore Agent 3 — likely a Modal/Dialog component not yet in the RAG index or the endpoint is unused UI-side). **F10 frontend-visibility gap candidate** — needs live probe.

## 7. Runtime Flows

### 7.1 Automated flow (defined but unscheduled per F1)

```
[phantom-cadence: docstring claims "every 2 hours" — beat schedule MISSING]
Celery Beat NOT-fires → verify_betting_outcomes @ tasks.py:6121
    → BettingOutcomeVerifier().verify_all_pending() @ betting_outcome_verifier.py:30-99
        → 1. PlacedWagerLeg settlement (S1503 Cat C scope; not Cat E)
        → 2. HAI arbitrage verification (Cat E):
            → filter HAI.objects.filter(status=WATCHING, item_type='arbitrage') @ :59-63
            → for each: _verify_arb_item(item, score_lookup) @ :376-415
                → determine outcome from score_lookup + payload @ :392-410
                → compute profit via _calculate_arb_profit() @ :417-453
                → item.record_verification(outcome, profit, notes) @ :413
                    → HAI.record_verification() @ models_human_interface.py:216-227:
                        → set verification_outcome, verification_profit, verification_notes
                        → set verified_at + event_completed_at (both = timezone.now())
                        → set status = STATUS_VERIFIED
                        → self.save()  [NO signal, NO event, NO log — F4]
        → 3. _create_learning_records() @ :455-480:
            → SportsBettingLearningBridge.record_arbitrage_outcome(item) @ :555-598:
                → read verification_profit + verification_outcome @ :573-574
                → write UserAgentLearning + AgentMemory
        → 4. BettingStats.recalculate() @ tasks.py:6141-6156 (per-user, O(n) rescan)
```

**Runtime reality:** step 1-4 have run **ZERO TIMES in the last 30 days** per S1503 §1 Finding 1. The flow is fully coded, would work under normal invocation, but no scheduler entry means no invocation.

### 7.2 REST-driven flow (live, but skips learning bridge)

```
User (frontend) → POST /api/human/attention/{id}/verify/ {outcome, profit, notes}
    → AttentionVerifyView.post() @ views_human_interface.py:213-257
        → state guard: reject if item.status != STATUS_WATCHING @ :238-242
        → item.record_verification(outcome, profit, notes) @ :245
            → HAI.record_verification() @ models_human_interface.py:216-227:
                [same body as automated flow — sets fields + STATUS_VERIFIED + save()]
                [NO signal, NO event, NO log line — F4]
        → return 200 with 4-field response @ :253-256
    [NO SportsBettingLearningBridge call — F8 coupling breakage]
    [NO BettingStats.recalculate() call]
```

**Runtime reality:** this path IS live. Manual REST-driven verifications DO update HAI state. But learning bridge coupling and BettingStats recalculation live inside `BettingOutcomeVerifier` orchestration, not inside `record_verification()` — so REST manual users' data does not flow to UserAgentLearning/AgentMemory. **F8 severity MED.**

### 7.3 Watch arming flow (functioning; user-driven only)

```
User (frontend or PA tool) → POST /api/human/attention/{id}/decide/ {decision='watch'}
    → HumanInterfaceService.record_decision() @ human_interface_service.py:295-353
        → HAI.record_decision(decision='watch') @ models_human_interface.py:184-214
            → status = STATUS_WATCHING @ :193
            → verification_outcome = VERIFY_PENDING @ :194
            → decided_at = timezone.now()
            → time_to_decision_ms computed if viewed_at set
            → self.save() @ :214
```

Not called automatically anywhere at HEAD. Users OR Rigby-via-PA-tool @ `pa_tool_schemas.py:3197-3207` (per Explore Agent 2) can arm the loop. Automated watch-arming (e.g., auto-watch high-value arbitrage detections without human review) does not exist at HEAD.

### 7.4 Three-plane manual/automated/learning liveness table (Rigby SIGN cycle 1 fold — added to make partial-liveness precise)

The verification loop has three distinct planes; each has its own liveness state at HEAD `3ff12391`. The compound picture below is what §1 headline "partial-liveness" refers to.

| Plane | What runs on it | Trigger surface | Runtime liveness at HEAD | Consequence |
|---|---|---|---|---|
| **1. Manual verification (state update)** | User-driven REST endpoint; PA-tool candidate (R6) | `POST /api/human/attention/{id}/verify/` @ `views_human_interface.py:213-257` | **LIVE** — verifications executed by users DO update HAI state (5 fields + STATUS_VERIFIED transition); response returns 200 with 4 fields | State reflects real user judgment; but downstream doesn't know it changed (F4 no signal) |
| **2. Automated verification (event-completion-driven)** | Sports arbitrage settlement + learning-record-creation | `verify_betting_outcomes` @ `core/tasks.py:6121-6184` invoked by Celery Beat | **DEAD** — task defined; beat_schedule entry MISSING (F1); ZERO CeleryTaskEvent rows in 30d per S1503 §1 Finding 1 (both variants) | No automated settlement; sports arbitrage HAI items stuck in WATCHING indefinitely unless manually verified via REST |
| **3. Learning propagation (verified → learning bridge)** | SportsBettingLearningBridge.record_arbitrage_outcome() → UserAgentLearning + AgentMemory writes | Sole call site: `BettingOutcomeVerifier._create_learning_records()` @ `betting_outcome_verifier.py:473-476` | **ABSENT/DECOUPLED** — coupling to orchestrator layer, not to writer; REST-driven verifications SKIP learning bridge entirely (F4/F8) | Even if plane 2 is restored, plane 3 remains coupled to sports-only orchestrator; non-sports verifiers + manual users still bypass learning; requires R2 coupling redesign |

**Reading:** The system LOOKS operational (plane 1 works). It ISN'T operational as a feedback loop (plane 2 doesn't fire; plane 3 is coupled to plane 2's orchestrator not to the writer). The "partial" in partial-liveness is precisely: **one of three planes is live**. This distinction is what F1's LOW-architectural severity scoping depends on — F1's fix restores plane 2 but leaves plane 3 broken and plane 1 still bypasses plane 3.

## 8. Data Ownership and Lifecycle

### 8.1 Cat E owns

- 5 fields on HumanAttentionItem (§3.1) — mutually exclusive with any other model's field ownership at HEAD.
- Writer method `record_verification()` (§3.2) — one code location.
- Verifier orchestration for sports arbitrage (§5.1, §7.1) — `BettingOutcomeVerifier._verify_arb_item()` + downstream bridge call.

### 8.2 Cat E does NOT own

- The transition INTO STATUS_WATCHING — that is Cat A (S1801) via `record_decision(decision='watch')`.
- Learning writes — those are Cat C bridges (S1803) via `SportsBettingLearningBridge.record_arbitrage_outcome()`.
- Score-fetching from external API — that is Cat A adjacent (spider network) via `TheOddsSpider.fetch_scores()`.
- BettingStats recalculation — that is S1503 Cat C sports scope.

### 8.3 Lifecycle

- Row creation: HAI created via a producer @ `human_attention_bridge.py` or similar (Cat A scope). Verification fields default null; `verification_outcome` default null (not VERIFY_PENDING); status defaults STATUS_PENDING.
- Watch arming: `record_decision(decision='watch')` transitions status pending → WATCHING + sets verification_outcome=VERIFY_PENDING. This is the SOLE entry into pre-verification state.
- Verification: `record_verification()` transitions WATCHING → VERIFIED + sets 4 fields + timestamps. Only invoked from the 2 callers listed §3.4 + §3.5.
- **NO auto-close for stuck-WATCHING items** — F6. Auto-dismiss ladder is pending-only.
- **NO re-verification** — once VERIFIED, no code path re-verifies or reverts. Enum choices include `VERIFY_CANCELLED` but no path uses it for post-cancel handling of the HAI row itself.

### 8.4 Retention

- HumanAttentionItem retention is Cat A scope (S1801 D6 SAVED-FOREVER debt — inherited by Cat E; verified HAI items are never deleted). See §14/§15 for the retention posture item durable-at-five (S1801 + S1802 + S1803 + S1804 + S1805 all inherit the SAVED-FOREVER default).

## 9. Integrations With Other Domains

### 9.1 Domain classification table (verification-loop lens)

Per Explore Agent 4 verified + independently sanity-checked at HEAD via grep patterns:

| Domain (Group) | HAI Producer | Verifier | Consumer | Classification | Notes |
|---|---|---|---|---|---|
| **Sports/DBAO (1500)** | ✓ arbitrage_detection @ human_attention_bridge.py:210 | ✓ BettingOutcomeVerifier @ betting_outcome_verifier.py:59-63 (**but zero fires in 30d — F1**) | ✓ SportsBettingLearningBridge @ sports_betting_bridge.py:555-598 | **DEFINED-BUT-DEAD** | Only fully wired path. F1 scheduling gap makes it runtime-dead. |
| **Sports/Prediction (1500)** | ✓ ml_prediction @ provenance_tracker.py:718,826 | ✗ None (separate task `evaluate_ml_predictions` @ tasks.py:6192) | ✗ None on Cat E side | **BROKEN** | Predictions have their own evaluation but never write verification_outcome — S1503 §1 Finding 2 durable-at-two under Group 1800. |
| **Revenue (1400)** | ✓ system_alert @ human_attention_bridge.py:256 | ✗ None | ✗ None | **BROKEN** | Opportunity HAI created but no post-close verification — R4 candidate. |
| **Content (1600)** | ✓ content:{content_type} @ human_attention_bridge.py:430 | ✗ None | ✗ None | **BROKEN** | Content quality HAI created; no performance verification post-publish. |
| **Observability (1700)** | ✓ diagnostic + system_alert @ human_attention_bridge.py:307 | ✗ None | ✗ None | **BROKEN** | Failure cluster HAI created; aggregation exists (`human_interface_service.py:199-208`) but no verification chain. |
| **Employee OS (1200)** | ✓ agent_execution + agent_output @ human_attention_bridge.py | ✗ None | ✗ None | **BROKEN** | Mission/execution HAI created; no outcome verification. |
| **Memory (1300)** | N/A | N/A | ✓ Consumes verification outcomes via SportsBettingLearningBridge → UserAgentLearning + AgentMemory | **N/A-CONSUMER** | AgentMemory is written TO by sports verifier (through the sports bridge); not a Cat E producer. |
| **Governance (1200)** | ✓ pilot_gate @ human_attention_bridge.py | ✗ None | ✗ None | **BROKEN** | Gate approval HAI created; no decision-outcome verification feedback. |
| **Signal Engine (1900)** | N/A | N/A | ✗ None | **MISSING** | Sports outcomes do not emit SignalCluster rows (S1503 §1 Finding 3). |
| **Ad Attribution** | ✗ None | N/A | N/A | **MISSING** | Not a HAI producer. |

**Sole DEFINED-BUT-DEAD path: sports arbitrage.** All other domains are BROKEN (producer exists, verifier + consumer absent). This is the "sports as island" pattern durable at S1503 §1 Findings 1-3 extending into Cat E scope. **Load-bearing evidence for D80 posture-decision brief.**

### 9.2 Inbound cross-domain reads (of verification tier fields)

- `sports_betting_bridge.py:573-574` — reads verification_profit + verification_outcome. Consumer path.
- `human_interface_service.py:199-208` — reads verification_outcome + verification_profit for aggregation. Serving-plane.
- `views_human_interface.py:130-133, 253-256` — reads for REST serialization.
- `views_platform_command.py:750-752, 822-824` — reads for platform command view serialization.
- **NO reads outside these 4 sites at HEAD.** F5 primitive `verification_id` disproved-cross-system reinforces this — no correlation-primitive naming means no cross-system query surface.

### 9.3 Outbound writes (cross-domain effects of verification)

- Direct: STATUS_VERIFIED transition + 5 fields set + timestamps. No FKs updated. No related-model writes triggered by `record_verification()` itself (per F4 — no signal receivers).
- Indirect (only through automated path — F8 fragile coupling): `BettingOutcomeVerifier._create_learning_records()` → `SportsBettingLearningBridge` writes UserAgentLearning + AgentMemory. But this is the orchestrator's write, not the writer method's — the coupling is fragile.
- **NO SignalCluster emission** (S1503 §1 Finding 3 durable-at-two under Group 1800).
- **NO MLPrediction.was_correct update** (S1503 §1 Finding 2 durable-at-two under Group 1800).
- **NO event emission** on STATUS_VERIFIED transition (S1801 D5 durable-at-two under Group 1800).

## 10. Event Flows

### 10.1 Events emitted (F4 — none)

- `record_verification()` does not emit any signal, event, or log line per F4. Direct grep of `models_human_interface.py:216-227` confirms plain `self.save()` with no post_save receiver hooked to the STATUS_VERIFIED transition.
- Cat E surface emits nothing at HEAD.

### 10.2 Events consumed (via automated orchestrator only)

- `BettingOutcomeVerifier.verify_all_pending()` runs on Celery Beat trigger — WHEN SCHEDULED. Currently unscheduled per F1.
- No other event/signal-driven entry into the verification chain at HEAD.

### 10.3 Events SHOULD emit (recommendation per S1274 §6 pattern)

- `verification.recorded` — payload includes HAI_item_id (S1801 F5 canonical primitive), outcome enum value, profit (if applicable), source_type. R2 candidate — this would enable REST endpoint verifications to fire the learning bridge downstream via signal/consumer wiring, breaking the F8 orchestrator-coupling brittleness.
- `verification.stuck` — periodic beat task detects items stuck in WATCHING > threshold (e.g., 72h post `event_completed_at` expected) and emits event for lifecycle team. R3 candidate — closes F6 monitoring gap.
- **Cross-arc handoff to Group 1900 Event Architecture.** Both events fit the pattern from S1274 §6 event-gap catalog. Group 1900 delegation cited in parent §5 anti-scope.

## 11. Existing Documentation

### 11.1 Topic docs

- **ZERO dedicated topic doc for S746 verification loop** per Explore Agent 5 grep. `docs/topics/personal-assistant.md`, `docs/topics/agent-system.md`, `docs/topics/spider-network.md` returned zero matches for verification/S746/watch_and_verify/record_verification. F10 documentation-coverage gap.

### 11.2 Handoff cross-references

Top 5 by relevance per Explore Agent 5:

1. `docs/handoffs/SESSION_995_BETTING_OUTCOME_VERIFICATION.md` — direct origin session. Established BettingOutcomeVerifier service + beat schedule (nominally) + record_verification wiring + SportsBettingLearningBridge writes.
2. `docs/handoffs/SESSION_1801_HUMAN_ATTENTION_CAT_A_HAI_CORE_AUDIT.md` — S1801 D5 promotion MED→HIGH on record_verification learning-loop decoupling.
3. `docs/handoffs/SESSION_1503_SPORTS_CAT_C_AUDIT.md` — S1503 §1 Finding 1 CRITICAL scheduling drift; Finding 2 Cat B → Cat C decoupling; Finding 3 SignalCluster emission gap.
4. `docs/handoffs/SESSION_1804_HUMAN_ATTENTION_CAT_D_HUMAN_PREFERENCE_AUDIT.md` — Cat D covers HumanPreference (adjacent surface); inherited claim about zero preference-respecting producers.
5. `docs/handoffs/SESSION_1506_SPORTS_CAT_F_AUDIT.md` — S1506 Cat F cross-domain integration lens; references S1503 findings.

Additional inherited: SESSION_1165_COO_BACKLOG_TRIPLE_MUST_CLOSE (retry-policy addition for `verify_betting_outcomes` — evidence the retry policy was maintained even after schedule silently dropped).

### 11.3 Research library entries

- `docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md` — S1503 §1 Finding 1 (CRITICAL scheduling drift) + Finding 2 (Cat B → Cat C decoupling) + Finding 3 (SignalCluster gap) + §2.1 Cat C contract statement (verbatim excerpt in S1503:145-165). Cat E is scope-adjacent to S1503 Cat C — S1503 owns the settlement side of `verify_betting_outcomes`, S1805 owns the verification side.
- `docs/research/domains/human_attention/1801_human_attention_cat_a_human_attention_item_core_audit.md` — S1801 D5 exact wording per Explore Agent 2 verified (:1289-1310): "record_verification() model method updates 6 fields + saves; NO signal fired, NO event emitted, NO log line with HAI_item_id... Impact: Cat B (FeedbackProcessor) does NOT see verification outcomes. Cat C learning bridges cannot key on verification profit/loss signals... Severity: HIGH (SIGN cycle 1 fold 2026-07-03). Rationale: this is the ONLY purported round-trip surface with learning per S1274 §4.7 canonical narrative, yet the current implementation drops both the correlation primitive (no HAI_item_id emitted) and any eventing (no signal / no HumanFeedbackRecord). The entire S746 verification loop is DECOUPLED from the learning pipeline."
- `docs/research/platform/cross_domain_integration_audit.md` §4.7 — canonical round-trip narrative referenced but NOT-cited-with-trigger-source. Drift row candidate.

### 11.4 Narrative anchors

- `docs/PLATFORM_WHAT_IT_IS.md` — grep zero matches for verification/record_verification/S746. Narrative silent per Explore Agent 5.
- `docs/PLATFORM_INVENTORY.md` §3.16 parallel row — inventory row lists `HumanAttentionLifecycleService` @ line 306; no explicit S746 or "verification loop" narrative claim. Grep hit at line 2101 is for `doc_claim_verification.py` (unrelated doc-claims verifier).

**Coverage classification (Playbook §12):** LIGHT-TO-MODERATE with HIGH operational-drift-buried-in-S1503. Rationale: (a) topic-doc absent; (b) S1503 covers ~half (settlement + learning bridge); (c) S1801 covers writer surface; (d) S995 origin handoff exists; (e) narrative anchors silent; (f) inventory silent on verification loop specifically. F10 documentation-coverage gap.

## 12. Research Coverage

**Rated LIGHT-TO-MODERATE** per §11.4 rationale. S1805 Cat E promotes to **MODERATE** — this audit is the first dedicated research pass on the verification loop as a distinct Category surface (S1503 was sports-scoped; S1801 was Cat A writer-adjacent; neither owned the verification chain end-to-end). Post-S1899 canonical summary this can be re-classified to DEEP if xx99 §7 anchor-updates land per playbook §16.

## 13. Architecture Maturity

**Rated EXPERIMENTAL** per §1 headline verdicts. Verification loop is:

- (a) sports arbitrage code path DEFINED but SCHEDULER MISSING (F1) — code runs zero times in 30d;
- (b) non-sports domain paths MISSING (F3);
- (c) learning-loop hook DECOUPLED via orchestrator coupling not post-writer signal (F4/F8);
- (d) zero telemetry per F4 (durable-at-two with S1801 D5);
- (e) zero tests per F9 (durable-at-five with S1801/S1802/S1803/S1804 F9);
- (f) no admin registration + no coverage-query surface per F10;
- (g) STATUS_WATCHING has no stuck-item monitoring per F6.

**Advance to PARTIAL** requires: (i) beat schedule restoration (F1 fix, per S1503 §1 Finding 1 recommendation); (ii) learning-loop signal wiring (F4/R2 fix); (iii) stuck-watching monitoring (F6/R3 fix). **Advance to WORKING** requires: (iv) non-sports verifier + test coverage (F3/R4); (v) documented sports-only-vs-generalizable posture decision (R0/D80 four-option analog).

## 14. Known Drift

### 14.1 Parent §5 D78 P5 wording drift (F1 evidence)

- **Parent claim:** "Triggers UNDOCUMENTED per S1273 debt catalog" — parent §5 P5 row.
- **Reality doc-level:** S1503 `docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md:511-514, 580, 625, 648` documented `betting_outcome_verifier.py:413` as automated trigger, published at S1599 arc close (2026-07-02 timeline).
- **Reality runtime-level:** Beat schedule for `verify_betting_outcomes` is MISSING per grep of `core/celery.py:1-1200`; both variants (`core.tasks.` + `sports.`) have 0 CeleryTaskEvent rows in 30d per S1503 §1 Finding 1 ORM probe. Docstring @ `core/tasks.py:6129` claims phantom "every 2 hours" cadence.
- **Severity: HIGH drift.** Parent §5 P5 rewrite needed at commit; parent §2.6 F5 row #5 status update owed to xx99 anchor-update commit.

### 14.2 S1273 platform_architecture_inventory.md drift (F1 corollary)

- S1273 `docs/research/platform_architecture_inventory.md:1372` asks "who calls `record_verification`?" implying undocumented triggers.
- At HEAD 2 real callers exist. S1273 stale relative to S1503 close.
- **Severity: MED drift.** xx99 anchor-update should touch S1273 §3.16 row.

### 14.3 S1274 cross_domain_integration_audit.md §4.7 drift

- S1274 §4.7 canonical round-trip narrative describes HAI → FeedbackProcessor → learning surfaces, but does not cite `betting_outcome_verifier.py:413` as the round-trip trigger for the verification tier.
- S1274 was written pre-S1503, so this is age-drift rather than error. Cross-arc handoff via xx99.
- **Severity: LOW drift.** xx99 anchor-update noteworthy but not blocking.

### 14.4 Docstring drift @ core/tasks.py:6129

- Docstring: "Runs every 2 hours via Celery Beat. Idempotent — skips already-settled wagers and already-verified items."
- Reality: no beat schedule; zero fires. Docstring describes a state the code does not achieve at HEAD.
- **Severity: MED.** Per playbook §14 grep-verify-binary-claims rule — the docstring makes a testable positive claim ("Runs every 2 hours") that ORM disproves.
- Fix: (a) remove/rewrite docstring (align to reality — "Beat schedule MISSING as of S1503 §1 Finding 1; manual dispatch only"); OR (b) add beat entry (F1 fix per R1).

### 14.5 Field serialization asymmetry (F7 candidate — durable-at-two under Group 1800)

- `verification_notes` @ :162 exists but not consistently serialized across REST endpoints. Grep of the field name across `views_human_interface.py`, `views_platform_command.py` returned zero direct include-in-response-body matches (per Explore Agent 3 report — only 4 of 5 fields serialized in REST responses).
- `event_completed_at` @ :163 exists but leaked only in `human_interface_service.py:120`, not in views.
- Parallel to S1804 F7 (asymmetric read+serialize surface durable-at-two under Group 1800).

## 15. Known Technical Debt

| ID | Severity | Title | Evidence |
|---|---|---|---|
| **D1** | **CRITICAL** | verify_betting_outcomes has NO beat schedule (both variants zero-fire in 30d) — S1503 §1 Finding 1 durable-at-two under Group 1800 | `core/celery.py:1-1200` grep zero matches for verify_betting_outcomes; docstring @ `core/tasks.py:6129` phantom; S1503 §1 Finding 1 ORM probe evidence |
| **D2** | **HIGH** | record_verification emits NO signal/event/log (S1801 D5 durable-at-two under Group 1800) | `core/models_human_interface.py:216-227` plain `self.save()` at :227; zero post_save receivers filtering STATUS_VERIFIED; F4 |
| **D3** | **HIGH** | Verification chain SPORTS-ONLY — no verifier for revenue/content/observability/employee-os HAI producers | `betting_outcome_verifier.py:59-63` hard-filter item_type='arbitrage'; §9.1 domain classification table |
| **D4** | **HIGH** | STATUS_WATCHING has no expiry / stuck-item auto-close pathway | `human_attention_lifecycle.py` auto-dismiss ladder scoped to STATUS_PENDING only; F6 |
| **D5** | **HIGH** | REST-endpoint verifications skip learning bridge — F8 fragile orchestrator coupling | `views_human_interface.py:213-257` has no SportsBettingLearningBridge call; §7.2 |
| **D6** | **MED** | Two task variants (core.tasks + sports.tasks) — F1 fix has ambiguity risk | S1503 §1 Finding 4; §3.4 + §3.6 |
| **D7** | **MED** | verification_profit typed as FloatField, not DecimalField — money-typing drift | `models_human_interface.py:161`; S1503 §2 flags DecimalField as canonical for money |
| **D8** | **MED** | No composite (user, verification_outcome) index — F10 monitoring queries require user-scoped scan | `models_human_interface.py:165-172` Meta.indexes list — none touch verification_outcome |
| **D9** | **MED** | verification_notes and event_completed_at serialization drift across REST endpoints (§14.5) | Explore Agent 3 grep evidence |
| **D10** | **MED** | Zero PA tool surface for verification loop (R6 candidate) | `pa_tool_schemas.py` grep; Explore Agent 3 |
| **D11** | **LOW-MED** | Zero tests on record_verification writer + BettingOutcomeVerifier settlement logic (durable-at-five with S1801/S1802/S1803/S1804 F9) | `core/tests/*.py` grep zero matches for record_verification|STATUS_VERIFIED|BettingOutcomeVerifier |
| **D12** | **LOW-MED** | HumanAttentionItem retention posture UNIFIED SAVED-FOREVER default (durable-at-five with S1801/S1802/S1803/S1804 D6) | inherited from S1801 D6; verified HAI items never deleted |
| **D13** | **LOW** | Zero admin registration for HumanAttentionItem — no verified-items admin view (durable-at-five with S1801/S1802/S1803/S1804 F9) | `core/admin.py` grep zero HumanAttentionItem register |
| **D14** | **LOW** | Docstring drift @ `core/tasks.py:6129` — phantom "every 2 hours" cadence | §14.4 |

## 16. Boundary Violations

### 16.1 Fragile-coupling boundary (F8)

- `SportsBettingLearningBridge.record_arbitrage_outcome()` is coupled to the orchestrator (`BettingOutcomeVerifier`) not to the writer (`record_verification()`). This creates a boundary violation: any caller of `record_verification()` that is NOT `BettingOutcomeVerifier` (specifically REST endpoint at HEAD, or future non-sports verifiers, or PA-tool-driven manual verifications R6) will silently skip the learning bridge.
- **Fix category:** signal-driven decoupling per R2 recommendation. Emit `verification.recorded` from `record_verification()` writer; consumers (learning bridges, stats aggregators, telemetry) subscribe. This is exactly the S1274 §6 event-emission-gap pattern.

### 16.2 Sports-only enforcement inside the sports domain (not a violation per se)

- `BettingOutcomeVerifier` @ :59-63 hard-filters `item_type='arbitrage'`. This is legitimate scope — the verifier is sports-arbitrage-specific by design. But it means non-sports domains cannot verify without a NEW verifier service. This is F3 architectural scope, not F8-style boundary violation.
- **Fix category:** either (a) generalize BettingOutcomeVerifier via strategy pattern (probably too invasive); OR (b) add domain-specific verifiers (RevenueOpportunityVerifier, ContentPerformanceVerifier, FailureClusterVerifier) each hooked to `record_verification()` for their domain. R4 candidate.

## 17. Duplicate or Overlapping Systems

### 17.1 Two task variants (F7 / D6)

- `core.tasks.verify_betting_outcomes` @ `core/tasks.py:6121-6184` — with retry policy + BettingStats-recalc wrapper.
- `sports.verify_betting_outcomes` @ `sports/tasks.py:414-441` — simpler, no retry, no BettingStats.
- Both call the same `BettingOutcomeVerifier().verify_all_pending()`.
- S1503 §1 Finding 4 flagged this as MED-HIGH drift. Cat E inherits.

### 17.2 Adjacent verification-tier fields on OTHER models (NOT the same system)

- `core/models_diagnostic_pipeline.py:442, 487` — has `verified_at` field + writer method on a diagnostic-pipeline audit trail. NOT related to HAI verification loop.
- `core/models_audit_tracking.py:170, 230, 306, 347` — has `verified_at` + `evidence_verified_at` on audit-tracking rows. NOT related.
- `core/models_unified_system.py:13739, 13891, 13937, 14058, 14060, 14073` — has `verified_at` on unified-system rows. NOT related.
- `ai_core/models/implementation_tracking.py:162` — has `verified_at` on implementation tracking. NOT related.
- `mythology/models.py:312` — has `verified_at` on mythology objects. NOT related.
- `intelligence/api/advisor_network_api.py:315` — `verification.id` refers to advisor-track-record `Verification` object (F5 primitive box hit — verified NOT-HAI).
- **Naming collision severity: LOW.** Multiple domains use "verified" naming for their own audit trails — no cross-system contamination risk because each model owns its fields. F10 documentation-clarity concern (a doc reader might confuse them), NOT a code-level boundary violation.

### 17.3 Adjacent verification systems (parallel-purpose)

- `evaluate_ml_predictions` task @ `core/tasks.py:6192` — separate task that evaluates `MLPrediction.was_correct` (S1503 §1 Finding 2 evidence). Runs on a DIFFERENT beat cadence. This is a parallel evaluation pipeline, not a duplicate of Cat E — S1273 §5+ cross-domain overlap catalog inheritance.
- `doc_claim_verification.py` — verifies doc claims against runtime state (Session 1099). Wholly unrelated to HAI verification loop.

## 18. Ownership Gaps

### 18.1 Cat E writer ownership

- `HumanAttentionItem.record_verification()` @ `core/models_human_interface.py:216-227` — no CODEOWNERS entry. Git log at commit `dc3774f0` (Session 995) is the last significant change to the method. No maintenance commits since.

### 18.2 BettingOutcomeVerifier ownership

- `core/services/betting_outcome_verifier.py` — no CODEOWNERS entry. Session 995 author. Retry policy addition Session 1165 (per S1503 §1 Finding 1 inheritance evidence). **Zero maintenance commits since 1165** despite S1503 §1 Finding 1 CRITICAL status.
- **Ownership gap: OPERATIONAL.** No one is watching the CRITICAL scheduling drift. S1503 §1 Finding 1 T-slot inheritance is unresolved.

### 18.3 REST endpoint ownership

- `AttentionVerifyView` @ `views_human_interface.py:213-257` — no CODEOWNERS entry. Adjacent to Cat A REST surface (S1801 owner).

### 18.4 Learning bridge ownership

- `SportsBettingLearningBridge` @ `sports_betting_bridge.py` — S1503 Cat C ownership scope (Group 1500 closed at S1599). Cross-arc ownership handoff: S1503 T-slot inheritance owed post-S1899.

## 19. Recommended Future Research

Ranked per playbook §19 by architectural uncertainty × risk × unblocked flows. Post-SIGN Chris-gate ordering may re-rank per Rigby architecture-leverage view.

### R0 (POST-ARC HIGH — Rigby SIGN cycle 1 systemic-elevation FOLD; dual-sub-decision reshape per Rigby cycle 1 Q4 fold)

**S746 verification-loop contract ADR — single R0 package with TWO explicit sub-decisions** for xx99 §5 posture-brief consumption (Rigby SIGN cycle 1 fold: monolithic scope-only R0 would be too vague to gate effectively; two-independent-ADRs would let Chris approve scope while deferring coupling, leaving "partial-liveness" pattern unresolved — one R0 with two sub-decisions is the cleanest gating artifact):

- **R0a — Verification-loop scope ADR.** Is S746 verification a **sports-only settlement** concern (arbitrage prediction resolution + wager settlement — the current SCOPE-BUT-DEAD-AT-HEAD shape) OR is it the platform's **general verification/outcome-labeling contract** for any HAI item with an event-completion-driven objective outcome (revenue opportunity conversion, content performance measurement, failure-cluster resolution, prediction-outcome integration)? Adjacent to parent §5 D80 four-option posture. If sports-only: F3 is intentional and downstream planes reshape accordingly. If general: F3/R4 open a family of non-sports verifier services.
- **R0b — Verification-loop coupling/contract ADR.** What MUST happen on `record_verification()` (or equivalent post-verification state transition) regardless of R0a scope choice: (i) emit an observable event / signal / metric; (ii) update/trigger learning propagation (or explicitly declare "no learning" for this HAI class as a valid outcome); (iii) ensure scheduling exists for automated verification paths where the class permits; (iv) define retention posture + monitoring for STATUS_WATCHING backlog; (v) route to a canonical downstream consumer registry.

**Why single R0 with dual sub-decisions:** If R0a and R0b are separated into two independent ADRs, Chris may approve R0a (sports-only) while deferring R0b — leaving the "partial-liveness" pattern (§1 headline framing) still-present under the sports-only shape. If they are monolithic without sub-structure, the ADR becomes too vague to gate on. Dual sub-decisions preserve the coupling between scope and contract per Rigby SIGN cycle 1 fold.

Compound with S1804 R0 (F5 fix scope-decision ADR); together these form the paired "learning-plane surface" decisions for xx99 §5 posture brief. **Elevation candidate parallel to S1802 R6 → R4 → R7 → R1 + S1803 R0 + S1804 R0 patterns — durable-at-three-consecutive-children under Group 1800.**

### R1 Beat schedule restoration ADR (F1 fix)

- Chris-gate for cadence (2h? 4h? during-game-window-only?) + variant selection (core.tasks or sports.tasks).
- Requires D8 concurrency safety fix pre-restoration per S1503 §1 Finding 10 dependency.
- Inherits S1503 §1 Finding 1 T-slot. Bounded 3-5-line implementation.

### R2 Verification learning-loop coupling redesign ADR (F4/F8 fix)

- Move `SportsBettingLearningBridge.record_arbitrage_outcome()` invocation from `BettingOutcomeVerifier._create_learning_records()` orchestrator layer to a post_save signal on HAI STATUS_VERIFIED transition (or explicit signal emitted from `record_verification()`).
- Consumes S1274 §6 event-emission pattern.
- Enables REST endpoint verifications + PA-tool-driven verifications + future non-sports verifiers to all reach learning bridge uniformly.
- Cross-arc handoff to Group 1900 Event Architecture for signal contract.

### R3 STATUS_WATCHING stuck-item monitoring beat task + auto-close pathway (F6 fix)

- Extend `HumanAttentionLifecycleService` auto-dismiss ladder to include STATUS_WATCHING with a threshold (e.g., 72h past `event_completed_at` expected + no verification).
- Emit `verification.stuck` event per R2 for cross-domain visibility.
- Closes F6/D4.

### R4 Non-sports verifier skeleton

- Chris-gates: (a) revenue opportunity outcome verifier (opportunity converted? deal closed?); (b) content performance verifier (engagement/traffic/conversion post-publish?); (c) failure cluster verifier (flagged failure was real vs transient?); (d) prediction outcome verifier (integrate with `evaluate_ml_predictions` at `tasks.py:6192`? or keep separate?).
- Prerequisite: R2 coupling redesign so new verifiers can subscribe to writer-emitted signals.
- Closes F3/D3 for a bounded subset of non-sports domains.

### R5 Admin surface + coverage-query dashboard

- Register HumanAttentionItem in Django admin per S1801 D6-admin-adjacent debt.
- Add coverage-query surface: % HAI in WATCHING never verified, stuck-item age distribution, per-domain verification rate.
- Closes F10/D13.

### R6 PA tool surface for verification loop (Rigby integration)

- Tools: `verification_tool.verify(item_id, outcome, profit, notes)` for manual verification via Rigby; `verification_tool.list_stuck_watching()` for monitoring; `verification_tool.stats()` for aggregation.
- Cross-arc with S1804 R6 (PA tool surface for HumanPreference) — durable-at-two under Group 1800 gap pattern.
- Closes F8-adjacent (Rigby cannot debug stuck-watching without ORM access at HEAD) + D10.

### R7 Test coverage on record_verification writer + BettingOutcomeVerifier settlement logic

- Unit tests for writer field-set semantics.
- Integration tests for automated flow (7.1) end-to-end when beat schedule restored.
- Integration tests for REST flow (7.2).
- Closes F9/D11 for Cat E surface; durable-at-five test-gap pattern inherits.

### R8 Two-task-variant reconciliation ADR

- Chris-gates: keep both? Deprecate `sports.verify_betting_outcomes`? Consolidate into single canonical `core.tasks.verify_betting_outcomes`?
- Inherits S1503 §1 Finding 4 T-slot.
- Closes F7/D6.

### R9 verification_profit money-typing migration (D7 fix)

- Migrate FloatField → DecimalField(max_digits=12, decimal_places=2) per PlacedWager pattern.
- Inherits S1503 §2 typing consistency scope.
- Closes D7. LOW-MED risk (migration + backfill).

### R10 Docstring drift fix @ `core/tasks.py:6129`

- Either fix beat schedule (R1) OR rewrite docstring to match reality.
- Bounded 1-line commit.
- Closes D14.

### R11 verification_id primitive-box discipline codification

- **Meta-methodology.** F5 FOURTH consecutive negative outcome (S1802 + S1803 + S1804 + S1805). Utility-rate-vs-pass-rate framing strengthens for xx99 §10 promotion to CODIFICATION-CONFIRMED — utility rate 5/5 across 5 applications (each caught a durable structural pattern about naming discipline) despite pass rate 1/5.
- xx99 §10 candidate; not S1805 scope.

### R12 record_verification learning-loop consumer registry

- Enumerate all consumers of verification_outcome / verification_profit at HEAD (currently: SportsBettingLearningBridge only).
- Cross-domain gap inventory: which OTHER consumers SHOULD exist? Signal Engine, MLPrediction calibration, Body Systems, Revenue Attribution.
- Closes R4-adjacent architecture-mapping for D80 xx99 posture brief.

## 20. Appendix

### 20.1 Files inspected

- `core/models_human_interface.py` @ HEAD `3ff12391` — verified verification-tier fields + record_verification writer + record_decision producer + STATUS enums + VERIFY_ enums.
- `core/services/betting_outcome_verifier.py` — verified via Explore Agent 2 (whole-file read, ~460 lines).
- `core/tasks.py:6121-6184` — verified verify_betting_outcomes task definition + retry policy + BettingStats wrapper.
- `core/celery.py:710-747` — direct read to resolve Agent 2 vs Agent 6 beat-schedule contradiction. Confirmed :719 is `process_human_attention_lifecycle`, not verify_betting_outcomes.
- `core/views_human_interface.py:213-257` — verified AttentionVerifyView REST endpoint per Explore Agent 2.
- `core/learning_bridges/sports_betting_bridge.py:555-598` — verified record_arbitrage_outcome consumer per Explore Agent 2 + Agent 4.
- `core/services/human_interface_service.py:116-208` — verified aggregation surface per Explore Agent 3.
- `intelligence/api/advisor_network_api.py:300-323` — verified F5 primitive hit is non-HAI advisor track record.
- `docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md` — verified §1 Finding 1 CRITICAL scheduling drift + Finding 2 Cat B→Cat C decoupling + Finding 3 SignalCluster gap + §2.1 Cat C contract statement.
- `docs/research/domains/human_attention/1801_human_attention_cat_a_human_attention_item_core_audit.md` — verified D5 exact wording per Explore Agent 2.
- `docs/research/domains/human_attention/1800_human_attention_domain_scoping.md` — parent scoping doc §3.E + §5 D78 P5 + §6.2 parked candidate item.
- `docs/research/domains/human_attention/1804_human_attention_cat_d_human_preference_child_audit.md` — S1804 pattern reference for §11.2 template application.

### 20.2 Docs inspected

- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 (20-section template), §13 (6-parallel Explore), §14 (verifier-loop evidence rules), §15 (SIGN routing stage-scoped table), §16 (commit policy), §17 (graduation criteria), §22 (initial queue).
- `docs/CELERY_AUDIT.md:469-470` — cited via S1503 evidence for beat-schedule-absent confirmation on both task variants.
- `docs/AUDIT_FINDINGS.md` §12 canonical Celery deferred list — S1503 §1 Finding 1 verified `verify_betting_outcomes` is NOT on this list (task is not intentionally deferred; it is silently drifted).

### 20.3 Grep patterns used

Pre-Explore verifier-loop:
- `record_verification|\.record_verification\(` — found 2 HAI-scoped callers + docs matches.
- `verification_outcome|verified_at|verification_profit|event_completed_at` — grep-verified all references at HEAD.
- `verification_id|verification_pk|verification_uuid` — grep confirmed 1 hit at `intelligence/api/advisor_network_api.py:315` (verified non-HAI).
- `VERIFY_PENDING|VERIFY_WON|VERIFY_LOST|VERIFY_PUSH|VERIFY_CANCELLED` — grep zero cross-model reuse.

Post-Explore verifier-loop:
- `verify_betting_outcomes|verify_pending_wagers|betting_outcome_verifier|BettingOutcomeVerifier|verify_arb` across `core/celery.py` — grep zero matches confirming NO beat schedule entry (resolves Agent 2 vs Agent 6 contradiction in Agent 2's favor).
- Direct read of `core/celery.py:710-747` verified :719 = `process_human_attention_lifecycle`.

Explore sub-agent sweeps (per playbook §13):
- Agent 1 Models: enumerated 5 verification-tier fields + Meta indexes + migration lineage + coverage-query surface.
- Agent 2 Services: traced automated + REST flows end-to-end; caught S1801 D5 anchor.
- Agent 3 APIs/Tools/Tasks: enumerated external surface + confirmed zero PA tool + zero WS + zero admin registration.
- Agent 4 Integrations: produced domain classification table with STRONG/WEAK/BROKEN/MISSING labels.
- Agent 5 Docs+Research: cross-referenced S995 + S1801 + S1503 + narrative anchors.
- Agent 6 Drift/Debt/Maturity: catalogued 6-debt list + confirmed F5 primitive DISPROVED-cross-system.

### 20.4 Unresolved unknowns

- **UNKNOWN:** Which frontend component consumes `humanAttentionApi.verify()` @ `frontend/src/lib/api.ts:1640-1641`. Grep did not locate the consuming Modal/Dialog. F10-adjacent — needs live probe post-arc.
- **UNKNOWN:** Whether the sports.verify_betting_outcomes variant was a scoping/migration attempt (moving Cat C surface into sports Django app) OR a duplicate-then-forgot pattern. S1503 §1 Finding 4 flagged; Cat E inherits UNKNOWN. R8 investigation candidate.
- **UNKNOWN:** Historical CeleryTaskEvent evidence — S1503 §1 Finding 1 ORM probe is bounded by CELERY_TASK_EVENT_RETENTION_DAYS (default 30) AND age of earliest CeleryTaskEvent row. Whether `verify_betting_outcomes` has EVER fired in production is undetermined without archival evidence.
- **UNKNOWN:** Whether `record_verification()` has EVER been called via REST endpoint by a real user at HEAD. `_verify_arb_item()` calls via the (unfiring) automated path — zero. REST endpoint calls — untelemetried per F4 + F10.

### 20.5 Conflicts between sources

- **Explore Agent 2 vs Agent 6 beat-schedule contradiction.** Agent 6 asserted `core/celery.py:719` registers `verify_betting_outcomes` as beat task. Agent 2 asserted NO beat entry exists. **Resolved via direct read of `core/celery.py:710-747`:** :719 is `process_human_attention_lifecycle` (HAI lifecycle expire/dismiss task). Agent 2 correct; Agent 6 misread. Per playbook §14 "trust but verify" — parent-agent verification caught the load-bearing error before it landed in the doc.
- **S1273 vs S1503 vs S1805 on trigger documentation status.** S1273 (older) says triggers undocumented; S1503 (newer, closed S1599) documented; S1805 confirms + extends. Reality wins per playbook §14; S1273 stale.

### 20.6 SIGN fold record (populated post-cycle 1 — 2026-07-04)

**Rigby SIGN cycle 1 verdict:** SIGN-with-edits at High confidence 0.83 on arc pin `pa-ae5931ea706b4537` (no fresh isolation pin per S1801+S1802+S1803+S1804 arc-pin-routing precedent durable-by-fifth-application).

**Rigby SIGN cycle 1 response headers (verbatim):**

- **Overall confidence:** High (0.83).
- **Most accurate part:** F1/F2 core diagnosis — parent wording obsolete + automated verification path not scheduled + Agent 2/6 contradiction resolved by direct celery.py read. Strong: surfacing "complete-on-paper but dead-in-runtime" as headline risk.
- **Weakest part:** Completeness around non-sports verification producers/callers (Discord/manual/admin/ops-hook coverage) because verification tends to hide behind alternate interfaces — highest miss-vector.
- **Missing area:** Explicit check for periodic tasks / management commands / ops hooks that trigger verification outside Celery beat.
- **Overstated maturity risk:** "Architecturally complete" could be softened — the loop is complete for state updates but not complete as a feedback loop.
- **Understated maturity risk:** No-monitoring impact might be bigger than framed — no heartbeat/metric for WATCHING backlog can silently accumulate operator debt.
- **Biggest architectural risk (Rigby-preferred phrasing):** "A loop that gives false confidence — it looks wired (endpoint exists, fields exist, tasks exist), but in practice it's unscheduled, unobserved, and doesn't feed learning — so failures persist indefinitely and downstream systems optimize against missing truth."
- **Most important next research:** Decide + codify the contract — what is "verification" in the platform (sports-only vs general outcome labeling)? Then enforce scheduling + observability + learning event emission on every verified transition.
- **What Claude got wrong (or most likely wrong):** Any implication "REST endpoint live = system not dead" undercuts the core claim. Right distinction: "manual verification exists; automated verification is dead; learning feedback is dead."
- **What must change before canonical:** One small table separating three planes — (1) manual REST/UI works; (2) automated beat dead; (3) learning propagation decoupled.

**Folds landed pre-commit (6 substantive edits):**

- **Fold 1 (§1 biggest-architectural-risk framing):** Replaced "architecturally complete but runtime-dead" with Rigby's sharper "partial-liveness verification loop" framing: manual verifies state, automated settlement unscheduled, learning propagation absent/decoupled → system appears operational while verified truth never reliably reaches downstream optimizers, monitoring gap. Preserves durable-at-two false-confidence pattern thesis; more precise than "runtime-dead" (REST/manual IS live for state updates).
- **Fold 2 (F1 severity scoping-clarification):** Added explicit clarification that F1 architectural severity is LOW **only when F1 is strictly scoped to the beat-schedule-drift** (bounded 3-5-line fix). Broader-liveness architectural risk is F1+F3+F4+R2 compound. Prevents undercutting the compound-risk framing in §1 headline.
- **Fold 3 (§7.4 three-plane table added):** New sub-section under §7 Runtime Flows introducing three-plane manual/automated/learning liveness table. Makes "partial-liveness" claim precise + hard to misread. Ties F1 severity scoping back to plane 2 vs plane 3 distinction.
- **Fold 4 (R0 dual-sub-decision reshape):** Reshaped R0 from single scope-decision ADR to single R0 with dual sub-decisions R0a-scope + R0b-coupling-contract. Rationale: two-independent-ADRs would let Chris approve scope while deferring coupling (partial-liveness pattern persists); monolithic without sub-structure would be too vague to gate on effectively. Dual sub-decisions preserve the scope↔contract coupling per Rigby SIGN cycle 1 fold.
- **Fold 5 (§20.9 miss-vector rule-out extended per Rigby Q1 guidance):** Extended search-strategy-breadth evidence to explicitly rule out Reddit/Bluesky external social bridges + Discord command handlers + admin/staff utilities + management commands + periodic-task registrations + ops hooks as `record_verification` callers. Preemptively closes the "highest miss-vector" gap Rigby flagged in her weakest-part critique. Confidence: HIGH that Cat E callers at HEAD number exactly 2 (REST + BettingOutcomeVerifier).
- **Fold 6 (frontmatter sign_status + verifier_loop update):** Bumped both frontmatter fields to reflect SIGN-with-edits + High 0.83 confidence + six folds landed + D48 29th arm turn 1 CLEAN + 24th consecutive-fully-clean-arms sub-pattern CONFIRMED.

**Q1 miss-vector completeness:** Rigby flagged non-sports producer/caller completeness as highest miss-vector. §9.1 domain classification table + §20.9 extended miss-vector rule-out (Reddit/Bluesky bridges + admin actions + management commands + ops hooks) close the gap pre-commit. Confidence HIGH that sports-only claim + 2-caller claim survive independent grep verification.

**Q2 F1 severity:** Rigby noted the LOW-architectural label needs explicit scoping to beat-drift-only OR should promote to MED. Fold 2 chose the explicit-scoping route + added compound-risk clarification connecting to §1 partial-liveness framing.

**Q3 biggest-architectural-risk sharper phrasing:** Rigby's "partial-liveness" phrasing preserves durable-at-two false-confidence-loop pattern while being more precise than "runtime-dead" — REST path IS live for state updates. Fold 1 adopted verbatim.

**Q4 R0 shape (single R0 with dual sub-decisions):** Rigby recommended R0a-scope + R0b-coupling packaged as single ADR to preserve coupling. Fold 4 adopted verbatim + preserved coupling rationale in R0 prose.

**D48 29th arm turn 1 status:** CLEAN. Single-batch 4-question pattern delivered SIGN-with-edits with substantive folds + no worker-instability signal. **24th consecutive-fully-clean-arms sub-pattern CONFIRMED** per single-batch 4-question criterion (S1799 §10.2 MC-2 CODIFICATION-READY promotion path continues to advance toward CODIFICATION-CONFIRMED at xx99 §10).

### 20.7 F5 correlation-primitive HYPOTHESIS box FIFTH application methodology note (extended)

Following the utility-rate-vs-pass-rate framing introduced at S1804 §20.7 (with S1802 + S1803 + S1804 evidence), S1805 extends the pattern to FOURTH-consecutive-disprove:

**Running tally across 5 applications:**

| Application | Primitive | Cross-system verdict | Utility (caught structural pattern) |
|---|---|---|---|
| S1801 (P1 Cat A) | `HAI_item_id` | **VERIFIED** cross-system (8-10 domains) | YES — canonical cross-domain correlation primitive |
| S1802 (P2 Cat B) | `feedback_record_id` | **DISPROVED** cross-system | YES — caught write-boundary FeedbackProcessor is internal-only-primitive-namer |
| S1803 (P3 Cat C) | `learning_event_id` | **DISPROVED** cross-system | YES — caught learning-plane primitive-naming is over-eager |
| S1804 (P4 Cat D) | `user_pref_id` | **DISPROVED** cross-system | YES — caught preference-plane primitive is under-cited (dict-only access) |
| S1805 (P5 Cat E) | `verification_id` | **DISPROVED** cross-system (1 non-HAI hit rules out) | YES — caught verification-plane primitive is entirely absent from HAI |

**Utility rate: 5/5. Pass rate: 1/5.**

**Meta-methodology finding candidate for xx99 §10 CODIFICATION-CONFIRMED promotion:** The F5 correlation-primitive HYPOTHESIS box discipline is durable-at-five (durable-at-five-consecutive-applications with FOUR consecutive negative outcomes). The value is not in the pass rate but in the utility rate — even DISPROVED outcomes are load-bearing because they surface which primitives the codebase actually names vs which are wishful thinking about cross-system correlation. The pattern of naming primitives that don't survive cross-system verification is itself a durable domain-shape finding: **the round-trip learning surfaces of Group 1800 have exactly ONE canonical cross-system correlation primitive (HAI_item_id), and every other candidate primitive is subordinate to the HAI foreign key at the write-boundary**. This is the load-bearing architectural observation from the F5 arc of Group 1800.

**Promotion recommendation:** MC-3 CODIFICATION-CONFIRMED at xx99 §10 with utility-rate-vs-pass-rate framing baked into playbook v3 §9 evidence-rules. Chris-gate.

### 20.8 Field-usage matrix (for xx99 §5 posture-decision brief input)

| Field | Read sites | Write sites | Serialization sites | Governance | Runtime status |
|---|---|---|---|---|---|
| `verification_outcome` | 4 (bridge + service + views) | 2 (writer via 2 callers) | 4 REST endpoints | none | **LIVE via REST; DEAD via automated (F1)** |
| `verification_profit` | 3 (bridge + service + views) | 2 (writer via 2 callers) | 4 REST endpoints | none | **LIVE via REST; DEAD via automated (F1)** |
| `verification_notes` | 1 (bridge indirect via item) | 2 (writer via 2 callers) | 0 in views (F7 asymmetry) | none | Stored, not surfaced |
| `verified_at` | 3 (bridge + service + views) | 1 (writer only) | 4 REST endpoints | none | **LIVE via REST; DEAD via automated (F1)** |
| `event_completed_at` | 1 (service only) | 1 (writer only) | 1 (service only) | none | **Under-surfaced** (§14.5) |

### 20.9 Search-strategy-breadth evidence (S1804 §20.10 pattern extension)

Per Rigby SIGN cycle 1 Q1 miss-vector rule-out precedent from S1804 §20.10, S1805 pre-emptively rules out miss-vectors for record_verification callers. **Extended post-SIGN per Rigby Q1 weakest-part critique (non-sports producer/caller completeness = highest miss-vector).**

- **Celery task callers** — grep `verify_betting|record_verification|BettingOutcomeVerifier` across `core/tasks*.py` + `sports/tasks.py` — only 2 task hits (`core.tasks.verify_betting_outcomes` + `sports.verify_betting_outcomes`), both routing to same service, neither scheduled.
- **Management command callers** — grep `record_verification` across `core/management/commands/*.py` — zero. Adjacent management commands (`ops_verify.py`, `verify_doc_claims.py`, `verify_surgical_moves.py`) confirmed unrelated to HAI verification loop per Explore Agent 3.
- **Signal receivers** — grep `record_verification` inside `@receiver` decorators — zero.
- **PA tool handlers** — grep `record_verification|verification_outcome` inside `core/services/td_handlers*.py` — zero for HAI verification loop; only unrelated `verify_deploy` handler @ `td_handlers_core.py:837-849`.
- **Discord commands** — grep `record_verification|verification_outcome` across `core/services/discord_bot.py` — zero. Adjacent Discord command hits (`link_account` @ :2577-2598) are unrelated account-linking verification-code.
- **API view handlers** — grep across `core/views*.py` — 2 hits (`views_human_interface.py:245` writer; `views_platform_command.py:750-752, 822-824` reader). No hidden view handler.
- **Non-sports learning bridges (Rigby Q1 extended check)** — grep `record_verification|verification_outcome` across `ai_core/intelligence/reddit_learning_bridge.py` + `bluesky_learning_bridge.py` + other `core/learning_bridges/*.py` non-sports bridges — zero. External social bridges have their own domain-specific verification patterns (S1803 Cat C evidence) and do NOT call `HumanAttentionItem.record_verification()`.
- **Admin/staff utilities (Rigby Q1 extended check)** — grep `record_verification|verification_outcome` across `core/admin*.py` + `core/staff*.py` — zero. No admin action or bulk-utility triggers verification.
- **Periodic-task registrations (Rigby Q1 extended check)** — grep `record_verification|verify_betting_outcomes` across `docs/PLATFORM_INVENTORY.md` PeriodicTask section + Rigby's `celery_task_history` ORM probe surface — zero PeriodicTask rows for either variant of `verify_betting_outcomes` (S1503 §1 Finding 1 ORM probe evidence).
- **Ops hooks (Rigby Q1 extended check)** — grep `record_verification` across `core/services/ops_*.py` + `core/tasks_ops.py` — zero.

**Confidence: HIGH that Cat E callers of record_verification at HEAD number exactly 2 (REST + BettingOutcomeVerifier). Miss-vectors ruled out per Rigby SIGN cycle 1 Q1 weakest-part critique + extended non-sports coverage.**

### 20.10 D48 arm 29 (S1805 P5 Cat E) — post-SIGN update 2026-07-04

D48 arm state at S1805 P5 Cat E SIGN: **arm 29 turn 1 CLEAN**. Rigby SIGN cycle 1 delivered SIGN-with-edits at High 0.83 confidence via single-batch 4-question pattern on arc pin `pa-ae5931ea706b4537` — no worker-instability signal; substantive folds landed but no jam/generic-error pattern. **24th consecutive-fully-clean-arms sub-pattern CONFIRMED** per single-batch 4-question criterion (S1801-S1804 durable-at-four established → S1805 extends to durable-at-five). S1799 §10.2 MC-2 CODIFICATION-READY promotion path continues to advance toward CODIFICATION-CONFIRMED at Group 1800 xx99 §10.

**Arc-pin routing precedent extension:** S1805 marks the FIFTH consecutive child audit under Group 1800 to route SIGN via arc pin without minting a fresh isolation pin — durable-by-fifth-application. Cross-check: no fresh isolation pin was minted at S1805 open per S1801+S1802+S1803+S1804 precedent; no worker instability observed. Arc-standard behavior confirmed at fifth application. Will document explicitly at Group 1800 xx99 close as durable-by-fifth-application-across-five-child-arcs.

### 20.11 Frontmatter provenance

- Playbook §11.2 20-section template TENTH application overall + FIFTH under Group 1800 (S1801 first + S1802 second + S1803 third + S1804 fourth + S1805 fifth).
- Playbook §13 6-parallel Explore applied (Agent 1-6 outputs consumed).
- Playbook §14 verifier-loop REQUIRED performed pre-Explore + post-Explore (see §20.3 grep patterns).
- Playbook §15 Rigby SIGN cycle 1 pending — will use single-batch 4-question pattern via arc pin pa-ae5931ea706b4537 per S1801+S1802+S1803+S1804 arc-pin-routing precedent (durable-by-fourth-application).
- Playbook §16 commit policy: default draft; Chris-gated commit after SIGN folds.

*End of S1805 Cat E child audit.*
