# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 1800 IN-PROGRESS; NEXT = S1805 P5 CAT E S746 VERIFICATION LOOP + record_verification TRIGGER DISCOVERY + WRITER INVENTORY

The local wrapper at `tools/pa_local.sh:137` points at Group 1800 arc pin. **Active arc pin state after S1804 close:**

- **Active Group 1800 arc pin: `pa-ae5931ea706b4537`** (retained per playbook §16 through Group 1800 close at S1899). `tools/pa_local.sh:137` unchanged.
- **No SIGN isolation pin minted at S1804 open** (S1801+S1802+S1803 arc-pin routing precedent applied — durable-by-fourth-application; established as arc-standard behavior). `tools/pa_local.sh` wrapper default routes through arc pin cleanly.
- **Retired at S1801 close:** SIGN isolation pin `pa-43b5b8154c8e42d7` (minted via `session_tool.create_fresh` at S1801 open; retired at S1801 close per playbook §16 to keep pin ledger tidy).
- **Retired at S1799 close:** Group 1700 arc pin `pa-e7fbacc996b34b44` (Sessions 1700-1706 + S1799 Observability arc; 8-doc arc; retired via `session_tool.retire` at S1799 close per playbook §16).
- **Retired earlier at prior arc closes:** See `tools/pa_local.sh` comment block lines 26-140 for full ledger.

## READ THIS THIRD — S1804 CAT D CHILD AUDIT LANDED; NEXT = S1805 P5 CAT E S746 VERIFICATION LOOP + record_verification TRIGGER DISCOVERY + WRITER INVENTORY (FIFTH CHILD UNDER GROUP 1800)

Session 1804 shipped the **Group 1800 Cat D HumanPreference + F5 never-saved bug + reader inventory child audit** at `docs/research/domains/human_attention/1804_human_attention_cat_d_human_preference_child_audit.md` (`status: active`, `category: child_audit`, `session: 1804`, `child_slot: P4`, `domain_slug: human_attention`, `research_group: 1800`, `authority: child-audit for Category D per parent §5 D78 sequence + FOURTH child under Group 1800`; 828 lines post-SIGN folds; playbook §11.2 20-section template NINTH application overall + FOURTH under Group 1800).

**Rigby SIGN cycle 1 SIGN-with-edits at High confidence 0.86 2026-07-03** on arc pin `pa-ae5931ea706b4537`. **F1 two-part-bug reframing + F3 severity-phrasing tightening + F4 "by construction" two-orphan-paths phrasing + §1 "non-functional personalization loop that appears functional" biggest-architectural-risk framing + §20.10 search-strategy-breadth evidence + R0 systemic-elevation-fold folds landed pre-commit.** **D48 28th arm turn 1 CLEAN; 23rd consecutive-fully-clean-arms sub-pattern CONFIRMED** per single-batch 4-question criterion (S1799 §10.2 MC-2 CODIFICATION-READY promotion path advances toward CODIFICATION-CONFIRMED).

### 10 load-bearing findings F1-F10 (S1804 §14)

- **F1 (HIGH)** F5 is a TWO-PART BUG not one; parent §5 D78 P4 wording obsolete. Part A: `topic_weights` NEVER computed anywhere in the codebase. Part B: `source_weights` computed at `human_interface_service.py:732-736` but LOST because `update_learned_stats()` @ `models_human_interface.py:334-358` uses `.save(update_fields=['approval_rate', 'total_decisions', 'avg_decision_time_ms', 'updated_at'])` — source_weights EXPLICITLY excluded.
- **F2 (MED)** Reader inventory: 1 real read of source_weights @ `human_interface_service.py:717` with fallback 1.0 → silent identity mult; ZERO reads of topic_weights anywhere; ZERO frontend reads; 3 false-positive local dicts in spider_priority_engine + recommendation_engine + orchestration.
- **F3 (MED)** F5 severity MED silent no-op at HEAD (Rigby-tightened phrasing: fallback identity multiplier prevents user-visible break); UPGRADE-TO-HIGH pathway architecturally wired once fix ships.
- **F4 (HIGH)** Signal chain BROKEN with two orphan cases by construction — Case 1 FeedbackProcessor post_save scoped to Group 1300; Case 2 auto-approve @ `human_attention_lifecycle.py:279-325` bypasses `record_decision()` — Q2-orphan-case parallel to S1802 durable-at-two under Group 1800.
- **F5 (MED)** `user_pref_id` HYPOTHESIS FOURTH application → DISPROVED-CROSS-SYSTEM (ZERO grep hits). Running tally 1 pass / 3 disprove across 4 applications. **THIRD CONSECUTIVE F5 negative outcome**. MC-3 CODIFICATION-READY promotion path DOES NOT advance; meta-methodology finding for xx99 §10 STRENGTHENS with utility-rate-vs-pass-rate framing recommendation.
- **F6 (MED)** Notification-plane fields DEAD CODE at HumanPreference; older push-notification model coexists at `core/models_push_notifications.py`.
- **F7 (MED)** Asymmetric read+serialize surface (`_calculate_priority_score()` reads source_weights only; `get_preferences()` serializes topic_weights only).
- **F8 (LOW)** Zero PA tool surface (verified via Rigby SIGN Q1 miss-vector rule-out — `preferences` tool @ `pa_tool_schemas.py:4167` routes at UserProfile NOT HumanPreference).
- **F9 (LOW)** Zero admin + zero tests + zero custom manager (durable-at-four).
- **F10 (SPECULATIVE)** Duplicate CreateModel across migrations 0143 + 0179.

### 13 known technical debt D1-D13

D1 HIGH F5 two-part fix | D2 MED signal chain gap | D3 MED no periodic recompute beat | D4 MED CASCADE user-delete (durable-at-four) | D5 MED JSONField no schema enforcement | D6 MED SAVED-FOREVER retention (durable-at-four) | D7 MED notification-plane DEAD | D8 MED trusted_agents+blocked_sources zero readers | D9 LOW-MED zero tests (durable-at-four) | D10 LOW no composite indexes | D11 LOW zero PA tool surface | D12 LOW-SPEC duplicate CreateModel | D13 LOW no admin + no CODEOWNERS.

### R0-R12 recommended future research (post-SIGN Chris-gate ordering: R0 → R1 → R2 → balance)

R0 (POST-ARC HIGH — Rigby SIGN cycle 1 ELEVATED from per-field fix to systemic scope-decision ADR — path A make HumanPreference real vs path B deprecate/merge into UserAgentLearning) | R1 two-preference-model consolidation ADR | R2 personalization-plane consolidation ADR (HumanPreference vs UserAgentLearning) | R3 signal chain wiring | R4 trusted_agents+blocked_sources enforcement | R5 notification-plane wiring/removal | R6 PA tool surface | R7 retention posture ADR unified Group 1800 durable-at-four | R8 JSONField schema enforcement | R9 composite index | R10 test suite | R11 CODEOWNERS + admin | R12 duplicate migration investigation.

**Session close artifacts committed at S1804 close:**

```
docs/research/domains/human_attention/1804_human_attention_cat_d_human_preference_child_audit.md   [new; 828 lines post-SIGN folds; child audit NINTH application overall + FOURTH under Group 1800]
docs/research/domains/human_attention/1800_human_attention_domain_scoping.md                       [modified — §2.6 F5 row #4 flipped to VERIFIED-PARTIAL-AT-CHILD with cross-system-primitive DISPROVEN]
docs/research/ARCHITECTURE_INDEX.md                                                                [modified — v54 → v55 with §1.58 S1804 registration + §8 timeline S1804 row + line-6 v55 preamble; v54 preamble preserved]
docs/research/OPEN_ARCS.md                                                                         [modified — Group 1800 In-progress row current-child S1803→S1804 + next-expected S1805]
docs/handoffs/SESSION_1804_HUMAN_ATTENTION_CAT_D_HUMAN_PREFERENCE_AUDIT.md                        [new — S1804 handoff]
00-START-NEXT-SESSION.md                                                                           [modified — this file; S1804 close; next-session priority = S1805 P5 Cat E]
```

Handoff: `docs/handoffs/SESSION_1804_HUMAN_ATTENTION_CAT_D_HUMAN_PREFERENCE_AUDIT.md`.

### NEXT-SESSION MISSION — S1805 P5 CAT E S746 VERIFICATION LOOP + record_verification TRIGGER DISCOVERY + WRITER INVENTORY CHILD AUDIT

Per D78 P5 slot + parent §5 sequence: **S1805 Cat E S746 verification loop + `record_verification` trigger discovery + writer inventory child audit** — fifth child under Group 1800. Applies playbook §11.2 20-section child template + §13 6-parallel-Explore + §14 verifier-loop REQUIRED (CODIFICATION-READY per S1799 §10.2 MC-1) pre-Explore + post-Explore + §15 Rigby SIGN cycle 1 (D48 29th arm; 24th consecutive-fully-clean-arms sub-pattern anticipated).

**Cat E scope per parent §3.E:**
- `HumanAttentionItem.verification_outcome` + `verified_at` + `verification_profit` + `event_completed_at` fields per S1273 §3.16 catalog.
- `HumanAttentionItem.record_verification(outcome, profit)` writer per S1274 §4.7 narrative.
- **Triggers UNDOCUMENTED per S1273 debt catalog** — grep-verify who calls `record_verification` at HEAD + when + from what execution context.
- **F5 correlation-primitive `verification_id` HYPOTHESIS FIFTH child verification** — verify at HEAD (parent §5 primitive row #5).
- S746 completeness — is the verification loop actually running end-to-end at HEAD, or is it partially wired?
- Cross-cat with Cat A — if verification is triggered by event completion, which producer paths emit event-completion signals?

**Load-bearing question at Cat E:** does S746 verification loop run end-to-end at HEAD (with a real trigger surface), OR is `record_verification()` orphaned code awaiting a producer? Answer determines D80 posture evidence.

**S1804 F5 durability check DISPROVED cross-system for user_pref_id (THIRD CONSECUTIVE after S1802 + S1803) — S1805 tests the pattern holds FOURTH consecutive time:** if S1805 verifies `verification_id` as a cross-system primitive with cross-domain read coverage similar to S1801 F5 HAI_item_id evidence — the primitive-box discipline confirms a mixed pattern (2 of 5 passing). If NOT — the pattern of naming primitives that don't survive cross-system verification becomes a strengthened-durable-at-four-instances meta-methodology finding for the xx99 §5 posture-decision brief + §10 retrospective (utility-rate-vs-pass-rate CODIFICATION-CONFIRMED framing).

**Session flow at next-session open:**

1. `context-kit orient` (session-open protocol per memory rule).
2. Check if S1804 artifact set + cascade refresh PR merged to `main`.
3. If not yet merged: Chris merge + PR merge.
4. Run post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (may be batched into S1805 close PR per Chris preference).
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-ae5931ea706b4537` (D48 29th arm start).
6. Skip fresh SIGN isolation pin per S1801+S1802+S1803+S1804 arc-pin routing precedent (durable-by-fourth-application; established as arc-standard).
7. Fire 6-parallel-Explore sub-agent sweep per playbook §13 on HumanAttentionItem verification fields + `record_verification` writer + trigger discovery + S746 flow reconstruction + Cross-cat with Cat A producers + cross-arc handoffs.
8. Apply pre-Explore + post-Explore verifier-loop discipline per playbook §14 REQUIRED.
9. Draft S1805 Cat E audit doc per playbook §11.2 20-section child template.
10. Route Rigby SIGN cycle 1 (single-batch 4-question pattern; D48 29th arm; 24th consecutive-fully-clean-arms sub-pattern anticipated).
11. Land F1-Fn folds pre-commit.
12. No SIGN isolation pin retire unless minted (arc-pin routing precedent).
13. Update ARCHITECTURE_INDEX v55 → v56 with §1.59 S1805 registration + §8 timeline S1805 row + line-6 v56 preamble.
14. Update OPEN_ARCS Group 1800 In-progress row: current-child updated S1804 → S1805.
15. Update parent scoping doc §2.6 F5 `verification_id` HYPOTHESIS → VERIFIED-AT-CHILD IF cross-system verified, OR HYPOTHESIS REMAINS IF domain-internal.
16. Write S1805 handoff + overwrite this `00-START-NEXT-SESSION.md` to point at S1806 P6 Cat F next-session priority.

**Not next (unless Chris specifies):** any specific implementation work per playbook §14.5 no-implementation rule. All D-slots + R-slots (R0-R12) from S1804 remain post-arc T-slot items alongside S1803 + S1802 + S1801 R-slots.

### Post-arc queued items (Chris-gated; inherited from S1804 + S1803 + S1802 + S1801 + prior arcs)

- **From S1804 (this arc close):** R0-R12 with post-SIGN Chris-gate ordering R0 → R1 → R2 → balance (Rigby architecture-leverage ranking — R0 systemic scope-decision ADR path A vs path B elevated as Q4 top priority; parallels S1803 Q4-driven R0 elevation — durable-at-two).
- **From S1803:** R0-R11 with post-SIGN Chris-gate ordering R0 → R1 → R2 → balance.
- **From S1802:** R1-R10 with post-SIGN Chris-gate ordering R6 → R4 → R7 → R1.
- **From S1801:** R1 HAI retention posture ADR + R2 preference-aware producer factory + R3 auto-approve blocked_sources validation + R4 two-layer debt resolution + R5 S746 verification-trigger auto-scheduler + R6 deferred-until auto-reopen + R7 bulk decide upgrade + R8 legacy field migration + R9 F5 HumanPreference fix + R10 cross-domain HAI-consumer wiring.
- **From Group 1700 xx99 §8.1 T0/Gate** — R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.OBSERVABILITY.D74-SPINE-POSTURE.
- **From Group 1700 xx99 §8.2 T1 CRITICAL/HIGH** (9 items).
- **From Group 1700 xx99 §8.3 T2/T3** (38 items).
- **From Group 1600 xx99 §8.1 T0/Gate** — R.CONTENT.XX99-ADR-BUNDLE.
- **From Group 1500 (S1599)** — R.SPORTS.POSTURE + R.DBAO.CODENAME.
- **From Group 1400 (S1499)** — T1-T10.
- **From Group 1300 (S1399)** — 21 follow-on items (includes Cat H write-authority framework ADR that S1802 partially closes on the Cat B writer side + S1803 partially closes on the Cat C writer side).
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600); inherited.
- **5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift** — owed to Group 1700 xx99 anchor-update PR (unresolved).

**FIRST THING next session open:**

1. `context-kit orient`
2. Check if S1804 artifact set + cascade refresh PR are on `main`
3. Chris merge + PR merge if not
4. Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into S1805 close PR)
5. Verify `service_context: local` on arc pin `pa-ae5931ea706b4537` (D48 29th arm start)
6. Skip fresh SIGN isolation pin per S1801+S1802+S1803+S1804 arc-pin routing precedent (durable-by-fourth-application)
7. Execute S1805 P5 Cat E S746 verification loop + record_verification trigger discovery + writer inventory audit per playbook §11.2 20-section template + §13 6-parallel-Explore + §14 verifier-loop REQUIRED + §15 SIGN cycle 1
8. Land Rigby SIGN folds pre-commit

---

## PA / Rigby context

- **Arc pin at session start:** `pa-ae5931ea706b4537` (Group 1800 arc pin; in service through Group 1800 close at S1899). `tools/pa_local.sh:137` points at active arc pin — no rotation needed until S1899 close.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 156).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 28th arm HOLDING CLEAN at S1804 close):** 28 arms; 23-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN CONFIRMED at S1804 close per single-batch-4-question criterion. D48 29th arm start at S1805 open; 24th consecutive-fully-clean-arms sub-pattern anticipated at S1805 P5 Cat E SIGN.
- **SIGN routing via arc pin precedent from S1801 + S1802 + S1803 + S1804 (durable-by-fourth-application; established as arc-standard):** `tools/pa_local.sh` wrapper defaults to routing through arc pin. No fresh isolation pin minting required. All four prior child openings tested arc-pin routing successfully — no worker instability observed. **Established as arc-standard behavior**; will document explicitly at Group 1800 xx99 close as durable-by-fourth-application-across-four-child-arcs.

## Repo state at next-session open

- **Branch state (2026-07-03 post-S1804):** `main` at HEAD `40d575d6`; S1804 branch `research/session-1804-cat-d-human-preference-audit` pending Chris merge.
- **Head-commit ledger (2026-07-03 activity, oldest → newest):**
  - `47ab77f1` — PR #2850 S1799 Group 1700 Observability xx99 canonical summary + arc-close
  - `eef2280f` — PR #2851 S1800 parent scoping + arc-open discipline
  - `0c2288f6` — PR #2852 S1800 docs cascade refresh
  - `b66158a5` — PR #2853 S1801 Cat A HAI Core child audit
  - `9885ab01` — PR #2854 S1801 docs cascade refresh
  - `d2b58e94` — PR #2855 S1802 Cat B FeedbackProcessor + HumanFeedbackRecord child audit
  - `69cf2dd1` — PR #2856 S1802 docs cascade refresh
  - `3c200651` — PR #2857 S1803 Cat C Learning bridges + duplicate-service inventory child audit
  - `40d575d6` — PR #2858 S1803 docs cascade refresh (current main HEAD)
  - (S1804 commit — this session) — S1804 Cat D child audit + parent §2.6 F5 row #4 flip + INDEX v55 + OPEN_ARCS + handoff + start-here
- **Handoff continuity:** S1804 handoff at `docs/handoffs/SESSION_1804_HUMAN_ATTENTION_CAT_D_HUMAN_PREFERENCE_AUDIT.md`. Prior: SESSION_1803 (Cat C Learning bridges audit) / SESSION_1802 (Cat B FeedbackProcessor audit) / SESSION_1801 (Cat A HAI Core audit) / SESSION_1800 (arc-open parent scoping) / SESSION_1799 (Observability xx99).
- **ARCHITECTURE_INDEX version:** v55 (bumped this session with §1.58 S1804 registration + §8 timeline S1804 row + line-6 v55 preamble; v54 preamble preserved). Next bump at S1805 close (v55 → v56 with §1.59 S1805 registration).
- **OPEN_ARCS state:** Group 1800 row IN-PROGRESS; current-child field updated S1803 → S1804. Groups 1700/1600/1500/1400/1300 Closed.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Check if S1804 artifact set + cascade refresh PR are on `main`
- [ ] Chris merge + PR merge if not
- [ ] Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into S1805 close)
- [ ] Verify `service_context: local` on arc pin `pa-ae5931ea706b4537` (D48 29th arm start)
- [ ] Skip fresh SIGN isolation pin per S1801+S1802+S1803+S1804 arc-pin routing precedent (durable-by-fourth-application)
- [ ] Execute S1805 P5 Cat E S746 verification loop + record_verification trigger discovery + writer inventory audit per playbook §11.2 + §13 + §14 REQUIRED + §15 SIGN cycle 1
- [ ] Land Rigby SIGN folds pre-commit
- [ ] Bump ARCHITECTURE_INDEX v55 → v56 with §1.59 S1805 registration
- [ ] Update OPEN_ARCS Group 1800 In-progress row: current-child updated S1804 → S1805
- [ ] Update parent scoping doc §2.6 F5 `verification_id` HYPOTHESIS → VERIFIED-AT-CHILD IF cross-system verified

## Reference — where to look

- **S1804 child audit doc:** `docs/research/domains/human_attention/1804_human_attention_cat_d_human_preference_child_audit.md` — playbook §11.2 20-section template NINTH application overall + FOURTH under Group 1800; 10 findings F1-F10 + 13 debt D1-D13 (D1 HIGH F5 two-part; F1+F4 HIGH) + R0-R12 with post-SIGN Chris-gate ordering R0→R1→R2→balance + §20.6 SIGN fold record + §20.7 F5 methodology interpretation note extended with utility-rate framing + §20.8 field-usage matrix + §20.10 search-strategy-breadth evidence.
- **S1803 child audit doc:** `docs/research/domains/human_attention/1803_human_attention_cat_c_learning_bridges_child_audit.md` — playbook §11.2 20-section template EIGHTH application overall + THIRD under Group 1800.
- **S1802 child audit doc:** `docs/research/domains/human_attention/1802_human_attention_cat_b_feedback_processor_child_audit.md` — playbook §11.2 20-section template SEVENTH application overall + SECOND under Group 1800.
- **S1801 child audit doc:** `docs/research/domains/human_attention/1801_human_attention_cat_a_human_attention_item_core_audit.md` — playbook §11.2 20-section template SIXTH application overall + FIRST under Group 1800.
- **S1800 parent scoping doc:** `docs/research/domains/human_attention/1800_human_attention_domain_scoping.md` — playbook §11.1 parent template FIFTH application; D75-D80 Chris-locked; §2.6 F5 row #1 HAI_item_id VERIFIED-AT-CHILD (S1801) + row #2 feedback_record_id VERIFIED-PARTIAL-AT-CHILD cross-system-primitive DISPROVEN (S1802) + row #3 learning_event_id VERIFIED-PARTIAL-AT-CHILD cross-system-primitive DISPROVEN (S1803) + row #4 user_pref_id VERIFIED-PARTIAL-AT-CHILD cross-system-primitive DISPROVEN (S1804 this session); row #5 remains HYPOTHESIS awaiting Cat E child.
- **S1799 xx99 canonical summary (fifth arc-close):** `docs/research/domains/observability/1799_observability_canonical_summary.md`.
- **Prior xx99 canonical summaries:** `1699_content_canonical_summary.md` + `1599_sports_canonical_summary.md` + `1499_revenue_canonical_summary.md` + `1399_memory_canonical_summary.md`.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`.
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`.
- **ARCHITECTURE_INDEX v55:** `docs/research/ARCHITECTURE_INDEX.md` — S1804 §1.58 + line-6 v55 preamble + §8 timeline S1804 row.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1800 In-progress row (current-child S1804).
- **S1273 baseline:** `docs/research/platform_architecture_inventory.md` §3.16 HumanAttention row + §4.7 canonical round-trip narrative.
- **S1274 baseline:** `docs/research/platform/cross_domain_integration_audit.md` §3.3 CRITICAL Failure Cluster → HAI + §3.8 MEDIUM Signal Pattern → HAI.
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.
- **Cat E canonical entry points for S1805 consumption:** HumanAttentionItem verification fields per S1273 §3.16 + `record_verification(outcome, profit)` writer + trigger discovery via grep of `record_verification` callers at HEAD + S746 flow reconstruction.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1804 = Cat D fourth child; S1805 P5 Cat E next child.
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff.
- Docs cascade — cascade PR pending Chris merge; post-S1804 cascade will be batched into S1805 close PR OR standalone follow-up per Chris preference.
- **CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift** — inherited from Group 1700 xx99 anchor-update PR (unresolved).
- Group 1400/1500/1600/1700 post-arc §7 anchor-updates still pending (inherited).
- Group 1400/1500/1600/1700 T1 CRITICAL remediation queues still pending; Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE + Group 1700 paired T0/Gate (RETENTION-UNIFIED-ADR + D74-SPINE-POSTURE) still gating.
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600).
- **5 doc PRs still owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **D48 28th arm HOLDING CLEAN at S1804 close** — 23rd consecutive-fully-clean-arms sub-pattern CONFIRMED per single-batch-4-question criterion; 24th anticipated at S1805 P5 Cat E SIGN.
- **Playbook v3 §11.2 template NINTH application at S1804** — child template durable at nine-consecutive-applications (S1601 + S1701 + S1801 first-under-arc + S1602 + S1702 second-under-arc + S1801/S1802/S1803/S1804 four under Group 1800).
- **Playbook v3 §14 verifier-loop REQUIRED promotion (S1799 §10.2 MC-1 CODIFICATION-READY):** enforced at S1804 pre-Explore + post-Explore + post-SIGN Q1 miss-vector rule-out grep; also caught parent §5 D78 P4 HYPOTHESIS wording drift at pre-Explore.
- **F5 correlation-primitive `user_pref_id` HYPOTHESIS FIFTH application DISPROVED-CROSS-SYSTEM at S1804 close** — HYPOTHESIS REMAINS at parent §2.6 row #4 with cross-system-primitive DISPROVEN; MC-3 CODIFICATION-READY promotion path DOES NOT advance at S1804 close (THIRD CONSECUTIVE negative outcome); primitive-box DISCIPLINE itself STRENGTHENED as meta-methodology CANDIDATE for xx99 §10 promotion to CODIFICATION-CONFIRMED under utility-rate-vs-pass-rate framing (utility rate 4/4 across 4 applications; pass rate 1/4 does not reflect discipline utility).
- **Arc pin `pa-ae5931ea706b4537` in service** through Group 1800 close at S1899; retire owed at S1899 close per playbook §16.
- **SIGN isolation pin routing pattern (durable-by-fourth-application):** S1801 + S1802 + S1803 + S1804 all routed SIGN via arc pin with no fresh isolation pin minted; established as arc-standard behavior; will document explicitly at Group 1800 xx99 close.
