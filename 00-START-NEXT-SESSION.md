# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 1800 IN-PROGRESS; NEXT = S1806 P6 CAT F ADJACENT / SEPARATION BOUNDARIES (SIXTH AND LAST CHILD; xx99 S1899 NEXT AFTER)

The local wrapper at `tools/pa_local.sh:137` points at Group 1800 arc pin. **Active arc pin state after S1805 close:**

- **Active Group 1800 arc pin: `pa-ae5931ea706b4537`** (retained per playbook §16 through Group 1800 close at S1899). `tools/pa_local.sh:137` unchanged.
- **No SIGN isolation pin minted at S1805 open** (S1801+S1802+S1803+S1804 arc-pin routing precedent applied — durable-by-fifth-application; established as arc-standard behavior). `tools/pa_local.sh` wrapper default routes through arc pin cleanly.
- **Retired at S1801 close:** SIGN isolation pin `pa-43b5b8154c8e42d7` (minted via `session_tool.create_fresh` at S1801 open; retired at S1801 close per playbook §16 to keep pin ledger tidy).
- **Retired at S1799 close:** Group 1700 arc pin `pa-e7fbacc996b34b44` (Sessions 1700-1706 + S1799 Observability arc; 8-doc arc; retired via `session_tool.retire` at S1799 close per playbook §16).
- **Retired earlier at prior arc closes:** See `tools/pa_local.sh` comment block lines 26-140 for full ledger.

## READ THIS THIRD — S1805 CAT E CHILD AUDIT LANDED; NEXT = S1806 P6 CAT F ADJACENT / SEPARATION BOUNDARIES (SIXTH AND LAST CHILD UNDER GROUP 1800; xx99 S1899 NEXT AFTER)

Session 1805 shipped the **Group 1800 Cat E S746 verification loop + `record_verification` trigger discovery + writer inventory child audit** at `docs/research/domains/human_attention/1805_human_attention_cat_e_verification_loop_child_audit.md` (`status: draft`, `category: child_audit`, `session: 1805`, `child_slot: P5`, `domain_slug: human_attention`, `research_group: 1800`, `authority: child-audit for Category E per parent §5 D78 sequence + FIFTH child under Group 1800`; 787 lines post-SIGN folds; playbook §11.2 20-section template TENTH application overall + FIFTH under Group 1800).

**Rigby SIGN cycle 1 SIGN-with-edits at High confidence 0.83 2026-07-04** on arc pin `pa-ae5931ea706b4537`. **§1 partial-liveness sharper-framing (Rigby verbatim adopted) + F1 severity scoping-clarification (LOW architectural WHEN SCOPED STRICTLY to beat-drift) + §7.4 three-plane manual/automated/learning liveness table addition + R0 dual-sub-decision R0a-scope + R0b-coupling-contract reshape + §20.9 Reddit/Bluesky/admin/mgmt-command/periodic-task/ops-hook miss-vector rule-out extended folds landed pre-commit.** **D48 29th arm turn 1 CLEAN; 24th consecutive-fully-clean-arms sub-pattern CONFIRMED** per single-batch 4-question criterion (S1799 §10.2 MC-2 CODIFICATION-READY promotion path continues advancing toward CODIFICATION-CONFIRMED).

### 10 load-bearing findings F1-F10 (S1805 §14)

- **F1 (CRITICAL op + LOW arch WHEN SCOPED)** Parent §5 D78 P5 wording is DOUBLY OBSOLETE — (a) S1503 already documented `betting_outcome_verifier.py:413` as automated trigger; (b) `verify_betting_outcomes` @ `core/tasks.py:6121-6184` has NO beat_schedule entry per grep of `core/celery.py:1-1200` returning zero matches. S1503 §1 Finding 1 ORM probe confirmed 0 CeleryTaskEvent rows in 30d for both variants.
- **F2 (CRITICAL)** Verification chain architecturally live but RUNTIME DEAD for automated path. REST endpoint at `views_human_interface.py:245` is SOLE live trigger + bypasses learning bridge entirely per F4/F8.
- **F3 (HIGH)** Verification chain SPORTS-ONLY. `BettingOutcomeVerifier` @ `betting_outcome_verifier.py:59-63` hard-filters `item_type='arbitrage'`. Non-sports HAI producers (revenue + content + failure clusters + predictions) have NO verifier at HEAD.
- **F4 (HIGH)** `record_verification()` emits NO signal / NO event / NO log — S1801 D5 durable-at-two under Group 1800. Plain `self.save()` at `models_human_interface.py:227`.
- **F5 (MED)** `verification_id` HYPOTHESIS FIFTH application → HYPOTHESIS REMAINS with cross-system-primitive DISPROVEN. FOURTH CONSECUTIVE F5 negative outcome. Utility rate 5/5 vs pass rate 1/5. MC-3 CODIFICATION-READY promotion path DOES NOT advance; meta-methodology finding for xx99 §10 STRENGTHENS to CODIFICATION-CONFIRMED-CANDIDATE.
- **F6 (HIGH)** STATUS_WATCHING has no expiry / stuck-item monitoring / auto-close pathway.
- **F7 (MED)** Two task variants coexist (`core.tasks.verify_betting_outcomes` + `sports.verify_betting_outcomes`) — S1503 §1 Finding 4 durable-at-two under Group 1800.
- **F8 (MED)** Learning-loop coupling FRAGILE via orchestrator layer — `SportsBettingLearningBridge.record_arbitrage_outcome()` only reachable via unscheduled `BettingOutcomeVerifier` orchestration; REST endpoint verifications skip learning bridge entirely.
- **F9 (LOW-MED)** Zero test coverage — durable-at-five-consecutive-children under Group 1800.
- **F10 (LOW)** Zero admin registration + no coverage-query surface for stuck-WATCHING items — durable-at-five.

### 14 known technical debt D1-D14

D1 CRITICAL (verify_betting_outcomes NO beat schedule per S1503 §1 Finding 1 durable-at-two) | D2 HIGH (S1801 D5 durable-at-two) | D3 HIGH (sports-only scope) | D4 HIGH (STATUS_WATCHING no expiry) | D5 HIGH (REST verifications skip learning bridge) | D6 MED (two task variants) | D7 MED (verification_profit Float vs Decimal typing) | D8 MED (no composite index) | D9 MED (verification_notes + event_completed_at serialization drift) | D10 MED (zero PA tool surface) | D11 LOW-MED (zero tests durable-at-five) | D12 LOW-MED (SAVED-FOREVER retention durable-at-five) | D13 LOW (zero admin durable-at-five) | D14 LOW (docstring drift at core/tasks.py:6129).

### R0-R12 recommended future research (post-SIGN Chris-gate ordering: R0 → R1 → R2 → balance)

**R0 (POST-ARC HIGH — Rigby SIGN cycle 1 systemic-elevation FOLD; DUAL-SUB-DECISION reshape)** S746 verification-loop contract ADR — single R0 package with TWO sub-decisions: **R0a Verification-loop scope ADR** (sports-only vs generalizable-to-all-HAI-domains posture) + **R0b Verification-loop coupling/contract ADR** (event emission + learning trigger + scheduling + retention/monitoring + downstream consumer registry) bundled per Rigby SIGN cycle 1 Q4 fold to prevent Chris approving scope while deferring coupling. | R1 beat schedule restoration ADR | R2 verification learning-loop coupling redesign (post_save signal on writer) | R3 STATUS_WATCHING stuck-item monitoring beat task + auto-close | R4 non-sports verifier skeleton | R5 admin surface + coverage-query dashboard | R6 PA tool surface for verification loop | R7 test coverage on writer + settlement logic | R8 two-task-variant reconciliation ADR | R9 verification_profit money-typing migration (Float→Decimal) | R10 docstring drift fix | R11 F5 primitive-box discipline codification meta-methodology | R12 record_verification consumer registry.

**Session close artifacts committed at S1805 close:**

```
docs/research/domains/human_attention/1805_human_attention_cat_e_verification_loop_child_audit.md   [new; 787 lines post-SIGN folds; child audit TENTH application overall + FIFTH under Group 1800]
docs/research/domains/human_attention/1800_human_attention_domain_scoping.md                       [modified — §2.6 F5 row #5 flipped to VERIFIED-PARTIAL-AT-CHILD with cross-system-primitive DISPROVEN]
docs/research/ARCHITECTURE_INDEX.md                                                                [modified — v55 → v56 with §1.59 S1805 registration + §8 timeline S1805 row + line-6 v56 preamble; v55 preamble preserved]
docs/research/OPEN_ARCS.md                                                                         [modified — Group 1800 In-progress row current-child S1804→S1805 + next-expected S1806]
docs/handoffs/SESSION_1805_HUMAN_ATTENTION_CAT_E_VERIFICATION_LOOP_AUDIT.md                        [new — S1805 handoff]
00-START-NEXT-SESSION.md                                                                           [modified — this file; S1805 close; next-session priority = S1806 P6 Cat F]
```

Handoff: `docs/handoffs/SESSION_1805_HUMAN_ATTENTION_CAT_E_VERIFICATION_LOOP_AUDIT.md`.

### NEXT-SESSION MISSION — S1806 P6 CAT F ADJACENT / SEPARATION BOUNDARIES CHILD AUDIT (SIXTH AND LAST CHILD; xx99 S1899 NEXT AFTER)

Per D78 P6 slot + parent §5 sequence: **S1806 Cat F Adjacent / Separation Boundaries child audit** — sixth and LAST child under Group 1800 before S1899 xx99 canonical summary. Applies playbook §11.2 20-section child template + §13 6-parallel-Explore + §14 verifier-loop REQUIRED (CODIFICATION-READY per S1799 §10.2 MC-1) pre-Explore + post-Explore + §15 Rigby SIGN cycle 1 (D48 30th arm; 25th consecutive-fully-clean-arms sub-pattern anticipated).

**Cat F scope per parent §3.F (sub-slotted per S1706 SIGN F2 fold precedent):**
- **F.a External-domain LearningBridges** (RedditLearningBridge + BlueskyLearningBridge in `ai_core/intelligence/`) — external social signal ingestion; boundary between internal-domain signals and external-social signals.
- **F.b Cross-domain HAI-consumer integration gaps** (S1274 §3.3 + §3.8 + Body Systems / Signal Engine / Revenue / Observability all MISSING HAI-consumer integrations; ~5+ gap catalog).
- **F.c PA-tool learning integration** (PALearningInsightsService + Rigby PA-tool patterns from Group 1600 Content Cat E S1605 tactical-split precedent). Boundary between HAI-learning surface and PA-learning surface.
- **F.d Duplicate learning service inventory** (AgentLearningService + AgentLearningSystem + AgentLearningEngine + PersistentLearningEngine coexistence — dedup catalog + canonical verdict). Follows S1273 §5.13 dedup pattern.
- **F.e Terminology boundary** ("feedback" vs "learning" vs "signal" vs "preference" vs "personalization" vs "verification" — 6 overlapping-but-distinct terms across the arc). Recommendation for xx99 §5 posture-decision brief per S1706 Cat F F8 PERMEABLE-boundary precedent.

**Load-bearing question at Cat F:** consolidates the 5-cat audits into arc-close evidence brief for xx99 §5 posture-decision brief input; catalogs cross-domain HAI-consumer gaps for future arc handoffs; issues terminology recommendation per S1706 F8 PERMEABLE-boundary precedent.

**S1805 F5 durability check DISPROVED cross-system for verification_id (FOURTH CONSECUTIVE after S1802 + S1803 + S1804). S1806 Cat F is a consolidation audit and does NOT test another F5 primitive** — F5 arc completes at S1805 for Group 1800 with running tally 1 pass / 4 disprove. xx99 §10 meta-methodology promotion to CODIFICATION-CONFIRMED under utility-rate-vs-pass-rate framing is the load-bearing consumption of the F5 arc.

**Session flow at next-session open:**

1. `context-kit orient` (session-open protocol per memory rule).
2. Check if S1805 artifact set + cascade refresh PR merged to `main`.
3. If not yet merged: Chris merge + PR merge.
4. Run post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (may be batched into S1806 close PR per Chris preference).
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-ae5931ea706b4537` (D48 30th arm start).
6. Skip fresh SIGN isolation pin per S1801+S1802+S1803+S1804+S1805 arc-pin routing precedent (durable-by-fifth-application; established as arc-standard).
7. Fire 6-parallel-Explore sub-agent sweep per playbook §13 on Cat F sub-slots F.a-F.e.
8. Apply pre-Explore + post-Explore verifier-loop discipline per playbook §14 REQUIRED.
9. Draft S1806 Cat F audit doc per playbook §11.2 20-section child template.
10. Route Rigby SIGN cycle 1 (single-batch 4-question pattern; D48 30th arm; 25th consecutive-fully-clean-arms sub-pattern anticipated).
11. Land F1-Fn folds pre-commit.
12. No SIGN isolation pin retire unless minted (arc-pin routing precedent).
13. Update ARCHITECTURE_INDEX v56 → v57 with §1.60 S1806 registration + §8 timeline S1806 row + line-6 v57 preamble.
14. Update OPEN_ARCS Group 1800 In-progress row: current-child updated S1805 → S1806. **After S1806 close: In-progress → Awaiting summary** (all 6 children shipped; xx99 S1899 canonical summary owes close).
15. Write S1806 handoff + overwrite this `00-START-NEXT-SESSION.md` to point at S1899 xx99 canonical summary next-session priority.

**Not next (unless Chris specifies):** any specific implementation work per playbook §14.5 no-implementation rule. All D-slots + R-slots (R0-R12) from S1805 remain post-arc T-slot items alongside S1804 + S1803 + S1802 + S1801 R-slots.

### Post-arc queued items (Chris-gated; inherited from S1805 + S1804 + S1803 + S1802 + S1801 + prior arcs)

- **From S1805 (this arc close):** R0-R12 with post-SIGN Chris-gate ordering R0 → R1 → R2 → balance. **R0 elevated to DUAL-SUB-DECISION ADR** (R0a scope + R0b coupling/contract) per Rigby SIGN cycle 1 Q4 fold — parallels S1804 R0 systemic-elevation (path A vs path B) + S1803 R0 elevation (unified learning-plane contract) — **durable-at-three-consecutive-children R0-elevation pattern under Group 1800.**
- **From S1804 R0-R12** — parallel post-arc T-slot inheritance.
- **From S1803 R0-R11 + S1802 R1-R10 + S1801 R1-R10** — inherited.
- **From Group 1700 xx99 §8.1 T0/Gate** — R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.OBSERVABILITY.D74-SPINE-POSTURE.
- **From Group 1700 xx99 §8.2 T1 CRITICAL/HIGH** (9 items).
- **From Group 1700 xx99 §8.3 T2/T3** (38 items).
- **From Group 1600 xx99 §8.1 T0/Gate** — R.CONTENT.XX99-ADR-BUNDLE.
- **From Group 1500 (S1599)** — R.SPORTS.POSTURE + R.DBAO.CODENAME.
- **From Group 1400 (S1499)** — T1-T10.
- **From Group 1300 (S1399)** — 21 follow-on items (includes Cat H write-authority framework ADR that S1802 partially closes on Cat B writer + S1803 partially closes on Cat C writer + S1805 partially closes on Cat E writer via record_verification decoupling anchor).
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600); inherited.
- **5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift** — owed to Group 1700 xx99 anchor-update PR (unresolved).

**FIRST THING next session open:**

1. `context-kit orient`
2. Check if S1805 artifact set + cascade refresh PR are on `main`
3. Chris merge + PR merge if not
4. Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into S1806 close PR)
5. Verify `service_context: local` on arc pin `pa-ae5931ea706b4537` (D48 30th arm start)
6. Skip fresh SIGN isolation pin per S1801+S1802+S1803+S1804+S1805 arc-pin routing precedent (durable-by-fifth-application)
7. Execute S1806 P6 Cat F Adjacent / Separation Boundaries audit per playbook §11.2 20-section template + §13 6-parallel-Explore + §14 verifier-loop REQUIRED + §15 SIGN cycle 1
8. Land Rigby SIGN folds pre-commit

---

## PA / Rigby context

- **Arc pin at session start:** `pa-ae5931ea706b4537` (Group 1800 arc pin; in service through Group 1800 close at S1899). `tools/pa_local.sh:137` points at active arc pin — no rotation needed until S1899 close.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 156).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 29th arm HOLDING CLEAN at S1805 close):** 29 arms; 24-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN CONFIRMED at S1805 close per single-batch-4-question criterion. D48 30th arm start at S1806 open; 25th consecutive-fully-clean-arms sub-pattern anticipated at S1806 P6 Cat F SIGN.
- **SIGN routing via arc pin precedent from S1801 + S1802 + S1803 + S1804 + S1805 (durable-by-fifth-application; established as arc-standard):** `tools/pa_local.sh` wrapper defaults to routing through arc pin. No fresh isolation pin minting required. All five prior child openings tested arc-pin routing successfully — no worker instability observed. **Established as arc-standard behavior**; will document explicitly at Group 1800 xx99 close as durable-by-sixth-application-across-six-child-arcs after S1806 close.

## Repo state at next-session open

- **Branch state (2026-07-04 post-S1805):** `main` at HEAD `3ff12391`; S1805 branch `research/session-1805-cat-e-verification-loop-audit` pending Chris merge.
- **Head-commit ledger (2026-07-03/04 activity, oldest → newest):**
  - `47ab77f1` — PR #2850 S1799 Group 1700 Observability xx99 canonical summary + arc-close
  - `eef2280f` — PR #2851 S1800 parent scoping + arc-open discipline
  - `0c2288f6` — PR #2852 S1800 docs cascade refresh
  - `b66158a5` — PR #2853 S1801 Cat A HAI Core child audit
  - `9885ab01` — PR #2854 S1801 docs cascade refresh
  - `d2b58e94` — PR #2855 S1802 Cat B FeedbackProcessor + HumanFeedbackRecord child audit
  - `69cf2dd1` — PR #2856 S1802 docs cascade refresh
  - `3c200651` — PR #2857 S1803 Cat C Learning bridges + duplicate-service inventory child audit
  - `40d575d6` — PR #2858 S1803 docs cascade refresh
  - `c8db3837` — PR #2859 S1804 Cat D HumanPreference + F5 never-saved bug + reader inventory child audit
  - `3ff12391` — PR #2860 S1804 docs cascade refresh (current main HEAD)
  - (S1805 commit — this session) — S1805 Cat E child audit + parent §2.6 F5 row #5 flip + INDEX v56 + OPEN_ARCS + handoff + start-here
- **Handoff continuity:** S1805 handoff at `docs/handoffs/SESSION_1805_HUMAN_ATTENTION_CAT_E_VERIFICATION_LOOP_AUDIT.md`. Prior: SESSION_1804 (Cat D HumanPreference) / SESSION_1803 (Cat C Learning bridges) / SESSION_1802 (Cat B FeedbackProcessor) / SESSION_1801 (Cat A HAI Core) / SESSION_1800 (arc-open parent scoping) / SESSION_1799 (Observability xx99).
- **ARCHITECTURE_INDEX version:** v56 (bumped this session with §1.59 S1805 registration + §8 timeline S1805 row + line-6 v56 preamble; v55 preamble preserved). Next bump at S1806 close (v56 → v57 with §1.60 S1806 registration).
- **OPEN_ARCS state:** Group 1800 row IN-PROGRESS; current-child field updated S1804 → S1805. Groups 1700/1600/1500/1400/1300 Closed. **After S1806 close: Group 1800 In-progress → Awaiting summary; xx99 S1899 canonical summary owes close.**

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Check if S1805 artifact set + cascade refresh PR are on `main`
- [ ] Chris merge + PR merge if not
- [ ] Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into S1806 close)
- [ ] Verify `service_context: local` on arc pin `pa-ae5931ea706b4537` (D48 30th arm start)
- [ ] Skip fresh SIGN isolation pin per S1801+S1802+S1803+S1804+S1805 arc-pin routing precedent (durable-by-fifth-application)
- [ ] Execute S1806 P6 Cat F Adjacent / Separation Boundaries audit per playbook §11.2 + §13 + §14 REQUIRED + §15 SIGN cycle 1
- [ ] Land Rigby SIGN folds pre-commit
- [ ] Bump ARCHITECTURE_INDEX v56 → v57 with §1.60 S1806 registration
- [ ] Update OPEN_ARCS Group 1800: current-child S1805 → S1806 (after close: In-progress → Awaiting summary)
- [ ] Prepare for S1899 xx99 canonical summary as the immediate-next mission after S1806 close

## Reference — where to look

- **S1805 child audit doc:** `docs/research/domains/human_attention/1805_human_attention_cat_e_verification_loop_child_audit.md` — playbook §11.2 20-section template TENTH application overall + FIFTH under Group 1800; 10 findings F1-F10 + 14 debt D1-D14 (D1 CRITICAL verify_betting_outcomes NO beat + F1+F2 CRITICAL + F3+F4+F6 HIGH) + R0-R12 with post-SIGN Chris-gate ordering R0→R1→R2→balance + §7.4 three-plane manual/automated/learning liveness table + §20.6 SIGN fold record + §20.7 F5 methodology interpretation note extended with utility-rate framing + §20.9 miss-vector rule-out extended per Rigby Q1 weakest-part critique + §20.10 D48 29th arm post-SIGN update.
- **S1804 child audit doc:** `docs/research/domains/human_attention/1804_human_attention_cat_d_human_preference_child_audit.md` — playbook §11.2 20-section template NINTH application overall + FOURTH under Group 1800.
- **S1803 child audit doc:** `docs/research/domains/human_attention/1803_human_attention_cat_c_learning_bridges_child_audit.md` — playbook §11.2 20-section template EIGHTH application overall + THIRD under Group 1800.
- **S1802 child audit doc:** `docs/research/domains/human_attention/1802_human_attention_cat_b_feedback_processor_child_audit.md` — playbook §11.2 20-section template SEVENTH application overall + SECOND under Group 1800.
- **S1801 child audit doc:** `docs/research/domains/human_attention/1801_human_attention_cat_a_human_attention_item_core_audit.md` — playbook §11.2 20-section template SIXTH application overall + FIRST under Group 1800.
- **S1800 parent scoping doc:** `docs/research/domains/human_attention/1800_human_attention_domain_scoping.md` — playbook §11.1 parent template FIFTH application; D75-D80 Chris-locked; §2.6 F5 rows #1 VERIFIED-AT-CHILD (S1801) + row #2/#3/#4/#5 VERIFIED-PARTIAL-AT-CHILD cross-system-primitive DISPROVEN (S1802/S1803/S1804/S1805 this session).
- **S1503 sports Cat C audit doc:** `docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md` — §1 Finding 1 CRITICAL verify_betting_outcomes NEVER FIRES + Finding 2 Cat B → Cat C decoupling + Finding 3 SignalCluster emission gap.
- **S1799 xx99 canonical summary (fifth arc-close):** `docs/research/domains/observability/1799_observability_canonical_summary.md`.
- **Prior xx99 canonical summaries:** `1699_content_canonical_summary.md` + `1599_sports_canonical_summary.md` + `1499_revenue_canonical_summary.md` + `1399_memory_canonical_summary.md`.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`.
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`.
- **ARCHITECTURE_INDEX v56:** `docs/research/ARCHITECTURE_INDEX.md` — S1805 §1.59 + line-6 v56 preamble + §8 timeline S1805 row.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1800 In-progress row (current-child S1805).
- **S1273 baseline:** `docs/research/platform_architecture_inventory.md` §3.16 HumanAttention row + §4.7 canonical round-trip narrative.
- **S1274 baseline:** `docs/research/platform/cross_domain_integration_audit.md` §3.3 CRITICAL Failure Cluster → HAI + §3.8 MEDIUM Signal Pattern → HAI.
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.
- **Cat F canonical entry points for S1806 consumption:** F.a Reddit/Bluesky bridges @ `ai_core/intelligence/` + F.b S1274 §3.3+§3.8 cross-domain HAI-consumer gaps + F.c PALearningInsightsService + F.d duplicate learning-service inventory (AgentLearningService + AgentLearningSystem + AgentLearningEngine + PersistentLearningEngine) + F.e terminology boundary matrix.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1805 = Cat E fifth child; S1806 P6 Cat F next child (sixth and LAST before xx99).
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff.
- Docs cascade — cascade PR pending Chris merge; post-S1805 cascade will be batched into S1806 close PR OR standalone follow-up per Chris preference.
- **CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift** — inherited from Group 1700 xx99 anchor-update PR (unresolved).
- Group 1400/1500/1600/1700 post-arc §7 anchor-updates still pending (inherited).
- Group 1400/1500/1600/1700 T1 CRITICAL remediation queues still pending; Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE + Group 1700 paired T0/Gate (RETENTION-UNIFIED-ADR + D74-SPINE-POSTURE) still gating.
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600).
- **5 doc PRs still owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **D48 29th arm HOLDING CLEAN at S1805 close** — 24th consecutive-fully-clean-arms sub-pattern CONFIRMED per single-batch-4-question criterion; 25th anticipated at S1806 P6 Cat F SIGN.
- **Playbook v3 §11.2 template TENTH application at S1805** — child template durable at ten-consecutive-applications (S1601 + S1701 + S1801 first-under-arc + S1602 + S1702 second-under-arc + S1801/S1802/S1803/S1804/S1805 five under Group 1800).
- **Playbook v3 §14 verifier-loop REQUIRED promotion (S1799 §10.2 MC-1 CODIFICATION-READY):** enforced at S1805 pre-Explore + post-Explore + post-SIGN Q1 miss-vector rule-out grep; also caught parent §5 D78 P5 DOUBLY-OBSOLETE wording drift at pre-Explore.
- **F5 correlation-primitive `verification_id` HYPOTHESIS FIFTH application DISPROVED-CROSS-SYSTEM at S1805 close** — HYPOTHESIS REMAINS at parent §2.6 row #5 with cross-system-primitive DISPROVEN; MC-3 CODIFICATION-READY promotion path DOES NOT advance at S1805 close (FOURTH CONSECUTIVE negative outcome); primitive-box DISCIPLINE itself STRENGTHENED as meta-methodology CANDIDATE for xx99 §10 promotion to **CODIFICATION-CONFIRMED under utility-rate-vs-pass-rate framing** (utility rate 5/5 across 5 applications; pass rate 1/5 does not reflect discipline utility).
- **Arc pin `pa-ae5931ea706b4537` in service** through Group 1800 close at S1899; retire owed at S1899 close per playbook §16.
- **SIGN isolation pin routing pattern (durable-by-fifth-application):** S1801 + S1802 + S1803 + S1804 + S1805 all routed SIGN via arc pin with no fresh isolation pin minted; established as arc-standard behavior; will document explicitly at Group 1800 xx99 close.
- **After S1806 close: Group 1800 transitions from In-progress to Awaiting summary** — all 6 children (S1801-S1806) shipped; xx99 S1899 canonical summary owes close.
