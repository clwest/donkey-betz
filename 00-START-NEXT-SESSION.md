# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 1800 CLOSED AT S1899; NEXT = GROUP 1900 EVENT ARCHITECTURE ARC-OPEN

Group 1800 HumanAttention / Feedback / Learning arc CLOSED at S1899 xx99 canonical summary — SIXTH formal xx99 canonical summary in the Research OS library after S1399 Memory + S1499 Revenue + S1599 Sports + S1699 Content + S1799 Observability. **Arc pin `pa-ae5931ea706b4537` retired at S1899 close per playbook §16.**

- **Active arc pin state after S1899 close:** NONE — Group 1800 arc pin `pa-ae5931ea706b4537` retired. `tools/pa_local.sh:137` owed rotation to Group 1900 arc pin (when arc-open) OR reset to null-arc default.
- **Retired at S1899 close:** Group 1800 arc pin `pa-ae5931ea706b4537` (Sessions 1800-1806 + S1899 HumanAttention/Feedback/Learning arc; 8-doc arc; retired via `session_tool.retire` at S1899 close per playbook §16 to keep pin ledger tidy).
- **Retired at prior arc closes:** See `tools/pa_local.sh` comment block for full ledger (S1799 Group 1700 + S1699 Group 1600 + S1599 Group 1500 + S1499 Group 1400 + S1399 Group 1300).

## READ THIS THIRD — S1899 GROUP 1800 XX99 CANONICAL SUMMARY LANDED; NEXT = GROUP 1900 EVENT / INTEGRATION / RUNTIME ARCHITECTURE ARC-OPEN

Session 1899 shipped the **Group 1800 xx99 canonical summary + arc close** at `docs/research/domains/human_attention/1899_human_attention_canonical_summary.md` (`status: draft`, `category: canonical_summary`, `session: 1899`, `child_slot: xx99`, `domain_slug: human_attention`, `research_group: 1800`, `authority: canonical summary for Group 1800 HumanAttention / Feedback / Learning research arc — playbook §11.3 12-section template SIXTH application`; 961 lines post-SIGN folds; playbook §11.3 12-section canonical-summary template SIXTH application + §11.3 §10 meta-methodology template SIXTH application; **SIXTH formal xx99 canonical summary in the Research OS library**).

**Rigby SIGN cycle 1 SIGN-with-edits at High confidence 0.80 2026-07-04** on arc pin `pa-ae5931ea706b4537`. **Seven Rigby SIGN cycle 1 folds landed pre-commit:** Q1 fold #1 §10.2 MC-3 hardening (operational utility-rate definition + independence-of-triggers reframe + failure-mode guardrail) + Q2 fold #2 §4.6 CX-6 vs §4.2 CX-2 discriminator + Q3 fold #3 §5.3 defer-post-T0/Gate safe default + Q3 folds #4-#7 §5.2 four-option UNDERMINE additions (A contract-enforcement gap + B boundary trust-gap + C seam-count multiplier + D triple-simultaneous-re-audit burden). **MC-1 + MC-2 NOT premature per Rigby verdict; only MC-3 required hardening.** **D48 31st arm turn 1 CLEAN; 26-consecutive-fully-clean-arms sub-pattern EXTENDED at S1899 close** per single-batch 4-question criterion — MC-2 CODIFICATION-CONFIRMED milestone extended from 25 → 26 consecutive at S1899.

### Meta-methodology promotions delivered at S1899 close (per playbook §11.3 §10 SIXTH application)

- **MC-1 (Playbook §14 verifier-loop REQUIRED)** — **CODIFICATION-CONFIRMED**. Two independent triggers met: (a) S1799 §10.2 CODIFICATION-READY promotion path completed at Group 1700 close; (b) Group 1800 durable-at-six application caught 4 independent parent-drift finds (§4.10 CX-10).
- **MC-2 (D48 25-consecutive-fully-clean-arms sub-pattern)** — **CODIFICATION-CONFIRMED**. 25-consecutive milestone achieved at S1806 close; extended to 26-consecutive at S1899 close (D48 31st arm turn 1 CLEAN).
- **MC-3 (F5 correlation-primitive HYPOTHESIS box discipline under utility-rate-vs-pass-rate framing)** — **CODIFICATION-CONFIRMED**. SIGN-hardened with operational utility-rate definition + truly-independent-triggers + failure-mode guardrail. Utility rate 5/5 across 5 applications; pass rate 1/5 (HAI_item_id PASS + 4 domain-internal FAILs).
- **MC-4 (arc-pin routing durable-by-sixth-application under six-child arcs)** — **CODIFICATION-READY** candidate promoted. Awaits second-arc durability check.
- **MC-5 (Playbook §11.2 20-section child template durable at ELEVENTH consecutive application overall)** — **CODIFICATION-READY** candidate promoted.
- **MC-6/MC-7/MC-8/MC-9** all **CODIFICATION-CANDIDATE** new: Cat F CONSOLIDATION child pattern for six-child arcs + R-slot next-step-gating fold + durable-at-N test-gap arc-close diagnostic + silent-by-design failure mode audit lens.

### xx99 §5 D80 four-option posture-decision brief

- **Framing recommendation:** "with-assumptions-pending-fix" (each option annotated with named pre-conditions to satisfy pre-selection) OR **defer-post-T0/Gate as safe default** (Rigby SIGN cycle 1 Q3 fold #3 — Chris zero-assumptions governance path). Both Chris-gated; xx99 does not select.
- **F7 CRITICAL constraint (S1806 arc-close):** All four options are BLOCKED at HEAD by compound learning-loop coupling breaks (§4.2 CX-2). No option can be cleanly selected until R.HAI.LOOP-COUPLING-REPAIR + R.HAI.DUPLICATE-FILE-COLLISION-CONSOLIDATION land per §8.1 T0/Gate.
- **Options A/B/C/D** each with SUPPORT + UNDERMINE evidence from S1801-S1806 (see §5.2). UNDERMINE angles hardened via Rigby SIGN cycle 1 Q3 folds #4-#7.

### xx99 §8 follow-on queue (Group 1800 unified 47-item queue)

- **T0/Gate 6 items:** R.HAI.LEARNING-PLANE-CONTRACT-ADR joint Group 1300 + Group 1800 + R.HAI.DUPLICATE-FILE-COLLISION-CONSOLIDATION + R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE + R.HAI.RETENTION-UNIFIED-ADR durable-at-five + R.HAI.SOURCE-KIND-ENUM-ADR joint schema-change + R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES Group 1900 handoff.
- **T1 CRITICAL/HIGH 12 items:** Producer-side personalization enforcement + cross-domain HAI-consumer closure + verify-beat restoration + verification-loop scope/coupling ADRs + non-sports verifier skeleton + two-preference-model consolidation + personalization-plane consolidation + auto-approve contract + observability signal bundle + STATUS_WATCHING stuck-item monitor + non-bridge UserAgentLearning writer routing.
- **T2 MED 14 items + T3 LOW-MED 15 items = 29 items** covering LearningOrchestrator registry + external-bridge naming + two-layer lifecycle contract + F5 fix/deprecation + observability + PA tool surfaces + admin + test coverage + verification_profit money-typing + terminology glossary + migration cleanup.

### Session close artifacts committed at S1899 close

```
docs/research/domains/human_attention/1899_human_attention_canonical_summary.md            [new; 961 lines post-SIGN folds; playbook §11.3 12-section SIXTH application + §11.3 §10 meta-methodology SIXTH application]
docs/research/ARCHITECTURE_INDEX.md                                                        [modified — v57 → v58 with §1.61 S1899 registration + line-6 v58 preamble; v57 preamble preserved]
docs/research/OPEN_ARCS.md                                                                 [modified — Group 1800 In-progress + Awaiting summary → Closed transition]
docs/handoffs/SESSION_1899_HUMAN_ATTENTION_XX99_CANONICAL_SUMMARY.md                       [new — S1899 handoff]
00-START-NEXT-SESSION.md                                                                   [modified — this file; S1899 close; next-session priority = Group 1900 Event Architecture arc-open]
tools/pa_local.sh                                                                          [pending — arc pin `pa-ae5931ea706b4537` retired via session_tool.retire; wrapper line 137 owed rotation to Group 1900 arc pin OR null-arc default]
```

Handoff: `docs/handoffs/SESSION_1899_HUMAN_ATTENTION_XX99_CANONICAL_SUMMARY.md`.

### NEXT-SESSION MISSION — GROUP 1900 EVENT / INTEGRATION / RUNTIME ARCHITECTURE ARC-OPEN (playbook §22 default lean OR Chris D-override)

Per playbook §22 default queue lean after Group 1800 close: **Group 1900 Event / Integration / Runtime Architecture arc-open scoping**. Downstream of S1274 §11.1 EventBus adoption. Inherits Group 1700 delegation of event bus / routing / schema versioning per D2 ratification at S1700 open. Inherits Group 1800 T0/Gate R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES handoff (source_kind enum + six-plane learning-surface event-emission gap + HAI event candidates: `record_decision` + `record_verification` + `auto_approve` + `auto_escalate` transitions).

**xx99 §10 meta-methodology CODIFICATION-READY promotion candidates delivered at S1899 close (for Group 1900 parent scoping consumer):**

- **MC-4** — arc-pin routing durable-by-sixth-application under six-child arcs (CODIFICATION-READY at S1899 close). Group 1900 will be seventh consecutive-application observation opportunity IF Group 1900 is a six-child arc.
- **MC-5** — Playbook §11.2 20-section child template durable at ELEVENTH consecutive application overall (CODIFICATION-READY at S1899 close). Group 1900 child audits will be twelfth-consecutive-application observation opportunity.

**Session flow at next-session open:**

1. `context-kit orient` (session-open protocol per memory rule).
2. Check if S1899 artifact set + cascade refresh PR merged to `main`.
3. If not yet merged: Chris merge + PR merge.
4. Run post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (may be batched into Group 1900 arc-open PR per Chris preference).
5. Mint fresh Group 1900 arc pin via Rigby `session_tool.create_fresh` OR use null-arc default per Chris directive.
6. Update `tools/pa_local.sh:137` with new Group 1900 arc pin OR reset to null-arc default.
7. Verify `service_context: local` via `platform_config_tool overview` on new arc pin.
8. Route Rigby light SIGN pressure-test pre-lock per playbook §15 stage-table parent row (default: optional; Chris decides).
9. Draft S1900 Group 1900 parent scoping per playbook §11.1 SIXTH application (after S1400/S1500/S1600/S1700/S1800 five-consecutive).
10. Land Chris D-verdicts D81-D8N (or however parent proposes) via "agree all + D-N=(a)" round OR per-verdict override.
11. Bump ARCHITECTURE_INDEX v58 → v59 with §1.62 S1900 registration + line-6 v59 preamble.
12. Move OPEN_ARCS Group 1900 row from Not-started → In-progress.
13. Write S1900 handoff + overwrite `00-START-NEXT-SESSION.md` to point at P1 next-child per D3-analog cadence ratification.

**Not next (unless Chris specifies):** any specific implementation work per playbook §14.5 no-implementation rule. All Group 1800 T-slot items (R0-R12 across Cat A-F children) remain post-arc Chris-gated items awaiting T0/Gate + T1 execution ordering.

**Chris D-override option:** If Chris prefers a different next-arc (e.g., a T-slot execution arc instead of Group 1900 open, or a different research group), state at session open per playbook §22 D-override discretion.

### Post-arc queued items (Chris-gated; inherited from Group 1800 arc close at S1899 + prior arcs)

- **From Group 1800 (S1899 close):** T0/Gate 6-item ADR bundle (R.HAI.LEARNING-PLANE-CONTRACT-ADR + R.HAI.DUPLICATE-FILE-COLLISION-CONSOLIDATION + R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE + R.HAI.RETENTION-UNIFIED-ADR + R.HAI.SOURCE-KIND-ENUM-ADR + R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES) + T1 12 items + T2 14 items + T3 15 items = 47 total unified follow-on queue.
- **From Group 1700 (S1799) xx99 §8.1 T0/Gate** — R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.OBSERVABILITY.D74-SPINE-POSTURE. R.OBSERVABILITY.RETENTION-UNIFIED-ADR pairs with Group 1800 R.HAI.RETENTION-UNIFIED-ADR — recommend unified cross-arc retention ADR bundle.
- **From Group 1700 (S1799) xx99 §8.2 T1 CRITICAL/HIGH** (9 items).
- **From Group 1700 (S1799) xx99 §8.3 T2/T3** (38 items).
- **From Group 1600 (S1699) xx99 §8.1 T0/Gate** — R.CONTENT.XX99-ADR-BUNDLE.
- **From Group 1500 (S1599)** — R.SPORTS.POSTURE + R.DBAO.CODENAME + T1.3 (S1805 R1 verify-beat-restoration) inheritance.
- **From Group 1400 (S1499)** — T1-T10.
- **From Group 1300 (S1399)** — 21 follow-on items (includes Cat H write-authority framework ADR that S1802/S1803/S1805 partially closes).
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600); inherited.
- **5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift** — owed to Group 1700 xx99 anchor-update PR (unresolved).

**FIRST THING next session open:**

1. `context-kit orient`
2. Check if S1899 artifact set + cascade refresh PR are on `main`
3. Chris merge + PR merge if not
4. Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into Group 1900 arc-open PR)
5. Mint fresh Group 1900 arc pin OR use null-arc default per Chris directive
6. Verify `service_context: local` on new arc pin OR null-arc pin
7. Execute Group 1900 Event / Integration / Runtime Architecture parent scoping per playbook §11.1 SIXTH application

---

## PA / Rigby context

- **Arc pin at session start:** NONE — Group 1800 arc pin `pa-ae5931ea706b4537` RETIRED at S1899 close per playbook §16. `tools/pa_local.sh:137` owed rotation to new Group 1900 arc pin (when arc-open) OR reset to null-arc default.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 137; owed rotation).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 31st arm CLEAN at S1899 close):** 31 arms; **26-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN EXTENDED at S1899 close — MC-2 CODIFICATION-CONFIRMED milestone extended** per single-batch-4-question criterion. D48 32nd arm anticipated at Group 1900 parent scoping SIGN if Chris routes light SIGN.
- **SIGN routing precedent from S1801-S1806 arc-pin durable-by-sixth-application (CODIFICATION-READY at S1899 close per MC-4; established as arc-standard for future 6-child arcs):** Group 1900 will be seventh-consecutive-application observation opportunity IF Group 1900 is a six-child arc — CODIFICATION-CONFIRMED promotion candidate at Group 1900 close.

## Repo state at next-session open

- **Branch state (2026-07-04 post-S1899):** `main` at HEAD `3b903c7a` at S1899 session open; S1899 close artifact set pending Chris commit-gate on new branch `research/session-1899-human-attention-xx99-canonical-summary`.
- **Head-commit ledger (2026-07-03/04 activity, oldest → newest, culminating at S1899 close):**
  - `47ab77f1` — PR #2850 S1799 Group 1700 Observability xx99 canonical summary + arc-close
  - `eef2280f` — PR #2851 S1800 parent scoping + arc-open discipline
  - `0c2288f6` — PR #2852 S1800 docs cascade refresh
  - `b66158a5` — PR #2853 S1801 Cat A HAI Core child audit
  - `9885ab01` — PR #2854 S1801 docs cascade refresh
  - `d2b58e94` — PR #2855 S1802 Cat B FeedbackProcessor child audit
  - `69cf2dd1` — PR #2856 S1802 docs cascade refresh
  - `3c200651` — PR #2857 S1803 Cat C Learning bridges child audit
  - `40d575d6` — PR #2858 S1803 docs cascade refresh
  - `c8db3837` — PR #2859 S1804 Cat D HumanPreference child audit
  - `3ff12391` — PR #2860 S1804 docs cascade refresh
  - `5e575747` — PR #2861 S1805 Cat E S746 verification loop child audit
  - `eb6d5fcd` — PR #2862 S1805 docs cascade refresh
  - `8743bfeb` — PR #2863 S1806 Cat F Adjacent / Separation Boundaries CONSOLIDATION child audit
  - `3b903c7a` — PR #2864 S1806 docs cascade refresh (current `main` HEAD)
  - _(S1899 commit — this session)_ — S1899 xx99 canonical summary + Group 1800 arc close + INDEX v57 → v58 + OPEN_ARCS transition + handoff + start-here + arc pin retire
- **Handoff continuity:** S1899 handoff at `docs/handoffs/SESSION_1899_HUMAN_ATTENTION_XX99_CANONICAL_SUMMARY.md`. Prior: SESSION_1806 (Cat F CONSOLIDATION) / SESSION_1805 (Cat E S746 verification) / SESSION_1804 (Cat D HumanPreference) / SESSION_1803 (Cat C Learning bridges) / SESSION_1802 (Cat B FeedbackProcessor) / SESSION_1801 (Cat A HAI Core) / SESSION_1800 (arc-open parent scoping) / SESSION_1799 (Group 1700 xx99).
- **ARCHITECTURE_INDEX version:** v58 (bumped this session with §1.61 S1899 registration + line-6 v58 preamble; v57 preamble preserved).
- **OPEN_ARCS state:** Group 1800 row moved In-progress + Awaiting summary → Closed. Groups 1700/1600/1500/1400/1300 remain Closed. Group 1900 in Not-started §22 queue awaiting arc-open at next-session.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Check if S1899 artifact set + cascade refresh PR are on `main`
- [ ] Chris merge + PR merge if not
- [ ] Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into Group 1900 arc-open close)
- [ ] Mint fresh Group 1900 arc pin OR use null-arc default per Chris directive
- [ ] Update `tools/pa_local.sh:137` with new Group 1900 arc pin OR reset to null-arc default
- [ ] Verify `service_context: local` on new pin
- [ ] Execute Group 1900 Event / Integration / Runtime Architecture parent scoping per playbook §11.1 SIXTH application
- [ ] Land Chris D-verdicts D81-D8N per taxonomy Chris ratifies via "agree all + D-N=(a)" round
- [ ] Route Rigby light SIGN cycle 1 if Chris opts in per playbook §15 stage-table parent row default (optional)
- [ ] Bump ARCHITECTURE_INDEX v58 → v59 with §1.62 S1900 registration
- [ ] Move OPEN_ARCS Group 1900: Not-started → In-progress
- [ ] Prepare P1 next-session per D3-analog cadence ratification

## Reference — where to look

- **S1899 xx99 canonical summary:** `docs/research/domains/human_attention/1899_human_attention_canonical_summary.md`
- **S1806 Cat F CONSOLIDATION child audit doc:** `docs/research/domains/human_attention/1806_human_attention_cat_f_adjacent_separation_boundaries_child_audit.md`
- **S1805 Cat E S746 verification loop child audit doc:** `docs/research/domains/human_attention/1805_human_attention_cat_e_verification_loop_child_audit.md`
- **S1804 Cat D HumanPreference child audit doc:** `docs/research/domains/human_attention/1804_human_attention_cat_d_human_preference_child_audit.md`
- **S1803 Cat C Learning bridges child audit doc:** `docs/research/domains/human_attention/1803_human_attention_cat_c_learning_bridges_child_audit.md`
- **S1802 Cat B FeedbackProcessor child audit doc:** `docs/research/domains/human_attention/1802_human_attention_cat_b_feedback_processor_child_audit.md`
- **S1801 Cat A HAI Core child audit doc:** `docs/research/domains/human_attention/1801_human_attention_cat_a_human_attention_item_core_audit.md`
- **S1800 parent scoping doc:** `docs/research/domains/human_attention/1800_human_attention_domain_scoping.md`
- **Prior xx99 canonical summaries:** `1799_observability_canonical_summary.md` + `1699_content_canonical_summary.md` + `1599_sports_canonical_summary.md` + `1499_revenue_canonical_summary.md` + `1399_memory_canonical_summary.md`
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`.
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`.
- **ARCHITECTURE_INDEX v58:** `docs/research/ARCHITECTURE_INDEX.md` — S1899 §1.61 + line-6 v58 preamble.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1800 Closed row.
- **S1273 baseline:** `docs/research/platform_architecture_inventory.md` §3.16 HumanAttention row + §4.7 canonical round-trip narrative.
- **S1274 baseline:** `docs/research/platform/cross_domain_integration_audit.md` §3.3 CRITICAL Failure Cluster → HAI + §3.8 MEDIUM Signal Pattern → HAI + §2 integration map.
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1899 = xx99 canonical summary; S1900 next.
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff.
- Docs cascade — cascade PR pending Chris merge; post-S1899 cascade will be batched into arc-close PR OR standalone follow-up per Chris preference.
- **CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift** — inherited from Group 1700 xx99 anchor-update PR (unresolved).
- Group 1400/1500/1600/1700/1800 post-arc §7 anchor-updates still pending (inherited).
- Group 1400/1500/1600/1700 T1 CRITICAL remediation queues still pending; Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE + Group 1700 paired T0/Gate (RETENTION-UNIFIED-ADR + D74-SPINE-POSTURE) + Group 1800 T0/Gate 6-item bundle all gating.
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600).
- **5 doc PRs still owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **D48 31st arm turn 1 CLEAN at S1899 close** — **26-consecutive-fully-clean-arms sub-pattern EXTENDED at S1899 close** per single-batch-4-question criterion.
- **Playbook v3 §11.2 template ELEVENTH application at S1806 close** — child template durable at eleven-consecutive-applications. CODIFICATION-READY promoted at S1899 close per MC-5.
- **Playbook v3 §14 verifier-loop REQUIRED CODIFICATION-CONFIRMED at S1899 close (MC-1)** — enforced arc-wide at S1801-S1806 durable-at-six catching 4 independent parent-drift finds.
- **Arc pin `pa-ae5931ea706b4537` RETIRED at S1899 close** per playbook §16.
- **SIGN isolation pin routing pattern (durable-by-sixth-application CONFIRMED at S1806; MC-4 CODIFICATION-READY promoted at S1899 close):** established as arc-standard behavior for future 6-child arcs; will be documented explicitly at Group 1900 arc-open.
- **Group 1800 row IN-PROGRESS + AWAITING SUMMARY → CLOSED transition at S1899 close** — arc runtime target 8/8 sessions ACHIEVED.
