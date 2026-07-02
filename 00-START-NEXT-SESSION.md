# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. If you don't override `PA_API_URL`, every call goes to prod. The `.env` file's `PA_API_TOKEN` is also the **production** token.

### The correct LOCAL invocation
```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=<local-chris-token>      \
.venv/bin/python tools/pa_chat.py "message" --conversation <id>
```

**Before your first `pa_chat.py` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1506 close:**

- **ACTIVE ARC PIN:** `pa-791b3db549a64e54` (Group 1500 arc pin; minted at S1500 open, retained per playbook §16 for entire Group 1500 arc — carries P7 xx99 canonical summary).
- **`tools/pa_local.sh:128` already at `pa-791b3db549a64e54`** — no line-128 rotation needed at S1599 open.
- **Retired at S1506 close:** SIGN isolation pin `pa-c2cdbd5c0b8c451b` (S1506 Full SIGN pin; retired via `session_tool.retire` at S1506 close).
- **Retired at S1505 close:** SIGN isolation pin `pa-546de7ebe8c8b885` (S1505 Full SIGN pin).
- **Retired at S1504 close:** SIGN isolation pin `pa-af2bf7f2d1a0ef61` (S1504 Full SIGN pin).
- **Retired at S1503 close:** SIGN isolation pin `pa-8ce5f949bed5e093` (S1503 Full SIGN pin).
- **Retired at S1502 close:** SIGN isolation pin `pa-64c019d7e6685d31` (S1502 Full SIGN pin).
- **Retired at S1501 close:** SIGN isolation pin `pa-a39069230ab64450` (S1501 Full SIGN pin).
- **Retired at S1500 open:** Group 1400 arc pin `pa-34d43795e1b24bd3` (was already retired at S1499 close per D53).
- **Retired at S1499 close:** `pa-877f1919efaa48e4` (S1499 SIGN isolation pin).
- **Retired at S1406 close:** `pa-8660ea7cfecd4bc6`.
- **Retired earlier:** `pa-4bdd5ad264674ce8` + `pa-637331c5f9574a10` (S1405); `pa-87ee24cd0d3947ce` (S1404); `pa-fba0c4c81fba4922` (S1403); `pa-4a0a28edcb7a45ec` (S1402); `pa-16d8b24d30e7a7d8` (S1401); `pa-aa54193f240f4846` + `pa-4fc3329d0db6484f` (S1399 Group 1300 arc-close).

Use `tools/pa_local.sh` for all chats — line 128 already pointing at active Group 1500 arc pin.

## READ THIS SECOND — S1506 CAT F LANDED; S1599 XX99 CANONICAL SUMMARY QUEUED NEXT (LAST — ARC-CLOSE)

Session 1506 shipped the **sixth and LAST child audit** under Group 1500 Sports/DBAO/Intelligence: **Category F Cross-Domain Integration Lens & Posture Decision Framing Audit**. Doc landed at `docs/research/domains/sports/1506_sports_cross_domain_integration_lens_and_posture_decision_framing_audit.md` (1,345 lines pre-fold + F1-F2 folds landed at commit-time, `status: draft`, `category: child_audit`, `subdomain_category: F`, playbook §11.2 20-section template + six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 6 load-bearing pre-Explore claims — all 6 verified CORRECT against source before draft integration).

**LOAD-BEARING for D59 posture-decision evidence plan owed to xx99 canonical summary** — §20.6 produces the evidence-plan framing (7 integration criteria A1-A7 + 7 island criteria B1-B7 + 4 cross-cutting C1-C4 + failure-mode table D + cost asymmetry summary E + F2-fold scoring rubric with PASS/PARTIAL/FAIL thresholds F) with explicit "Chris-gated selection" tag. xx99 consumes this plan verbatim into §5 posture-decision brief; Chris ratifies post-arc via ADR per D59.

**Sixth and FINAL sibling applies D62 = (a) 4-item pre-brief mini-schema per surface upfront** — **6-sibling exemplar pattern COMPLETED** across S1501+S1502+S1503+S1504+S1505+S1506. xx99 §10.2 codify-to-playbook-v3 candidate for playbook v3 §5 promotion.

**Rigby Full SIGN cycle 1 SIGN-with-edits at High confidence** via fresh isolation pin `pa-c2cdbd5c0b8c451b` — 3 substantive SIGN turns (Batch 1 Q1-Q5 + Batch 2 Q6-Q10 + Batch 3 Q11-Q16 + Q15 §20.6 evidence-plan structural review + Q16 overall verdict); zero worker-instability observed across all 3 turns — **D48 9th arm — four consecutive fully-clean arms S1503+S1504+S1505+S1506 sub-pattern**. **F1-F2 folds landed at commit-time** (F1 §14.5 anchor-set tightening: `/odds` + `/futures` + `/slip` explicit bypass + `/arb` shared-agent exclusion at section body per Rigby Q5 Batch 1 edit; F2 §20.6 §F scoring rubric + threshold minima for xx99 consumption-readiness per Rigby Q15 Batch 3 edit). **Cycle 2 SIGN-clean at High confidence anticipated post-fold-land** — pattern-consistent with S1501-S1505 cycle-1-predict-cycle-2 5-of-5 arc precedent. **Do-not-regress notes for PR:** preserve §2.1 Cat F contract statement (5 guarantees + 11 non-guarantees) + preserve F1-F2 folds per §20.8 detailed enumeration + preserve §20.9 6-arc consumer-side pattern completion + preserve §20.10 6-sibling exemplar pattern completion for D62 = (a).

**D48 preemptive stability-probe gate 9th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506 9-arc pattern — further strengthens immediate codification recommendation from S1505 8-arc threshold with four-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506. **Recommendation:** xx99 (S1599) §10.2 codifies D48 into playbook v3 §15 alongside D45 titles-only recovery + BEFORE-SIGN Rigby ORM probe pattern (2-arc evidence base S1503+S1504; not applied S1505 or S1506 because no beat-schedule zero-fire claims — pattern generalizes to specific claim classes not all audits) + S1504 SIGN cycle 1 batch 1 verdict-text re-request recovery pattern (1-arc; S1505 + S1506 non-trigger notes per explicit preventive prompt framing) + S1505 Rigby Q8 grep-verified confidence-upgrade pattern (1-arc).

**Load-bearing findings owed to xx99 (S1599) via §20.6 evidence plan (14):**

1. **CRITICAL architectural — DBAO NAMING-CONVENTION-WITHOUT-MATERIALIZATION.** Six declared artifacts (schema/2 WS routes/env-vars/header) + zero runtime state + 2 unimplemented handler stubs. NEW pattern class for the arc.

2. **CRITICAL architectural — DECOUPLED-VERIFICATION-SYSTEMS at BettingOutcomeVerifier ↔ MLPrediction.** Two verification systems fully independent; zero cross-reference. NEW pattern class.

3. **HIGH architectural — Sports ↔ Signal Engine 6-arc consumer-side pattern COMPLETED.** Extends 5-arc S1502-S1505 to 6-arc. §20.9 codified.

4. **HIGH architectural — DECLARED-FEATURE-FLAG-GATES-NOTHING at `sports_intelligence`.** Hardcoded True at 2 sites, consulted nowhere. NEW pattern class.

5. **HIGH architectural — Discord HOT-PATH-CHOKE bypass** at `/odds` + `/futures` + `/slip` extends S1504 REST-side pattern to Discord side.

6. **HIGH architectural — Sports ↔ Memory PARTIAL bridge** (2/4 market agent coverage; 0 AgentKnowledgeSource writes).

7. **HIGH operational — `/ws/dbao-dashboard/` sibling route surfaced.** S1505 §14.1 MOCK-DATA-CONSUMER footprint expands 1 route → 2 routes.

8. **HIGH operational — DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT** at `_impl_collect_sports_odds_intelligence`. NEW pattern class.

9. **MED-HIGH — SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION** at `RealtimeIntelligenceEngine` cross-domain loops (hardcoded demo). NEW pattern class.

10. **MED-HIGH — LATENT-ZERO-FIRE at `RealtimeIntelligenceEngine`** deepens S1503 §14.1 ZERO-FIRE-BEAT (no beat, no @shared_task, manual start_skynet only).

11. **MED — Frontend IntelligencePage does not consume sports despite flag claim.**

12. **MED architectural — DUAL-COORDINATOR-BYPASS** at `_impl_collect_sports_odds_intelligence` (bypasses both coordinator AND intelligence engine).

13. **MED — CODEOWNERS compound gap** across 6 sports runtime files.

14. **MED — `docs/topics/sports-betting.md` gap remains after 6 audits.**

**Cat F maturity verdict** per §13: **PARTIAL (mixed; multi-axis; four-axis compound shape)** — sixth distinguishing maturity shape after S1501 fragile-contract-at-ingestion + S1502 armed-but-under-instrumented + S1503 armed-but-zero-fire + S1504 mixed-brief-generation-persistence-forgotten-HOT-PATH-CHOKE + S1505 mixed-WORKING-DEAD-RENDER-MOCK-AUTH-NO-REALTIME.

**Session close artifacts committed at S1506 close:**

```
docs/research/domains/sports/1506_sports_cross_domain_integration_lens_and_posture_decision_framing_audit.md  [new; 1345 lines pre-fold + F1-F2 folds landed at commit-time; SIGN-with-edits cycle 1 at High confidence]
docs/research/ARCHITECTURE_INDEX.md                                 [modified — v32 → v33; §1.36 + §8 timeline S1506 row + v33 preamble]
docs/research/OPEN_ARCS.md                                          [modified — current-child field advanced; Recent reconciliations 2026-07-02 (S1506 close) entry]
docs/handoffs/SESSION_1506_SPORTS_CAT_F_AUDIT.md                    [new — S1506 handoff]
00-START-NEXT-SESSION.md                                            [modified — this file; P7 xx99 default lean advanced to S1599]
```

Handoff: `docs/handoffs/SESSION_1506_SPORTS_CAT_F_AUDIT.md`.

### NEXT-SESSION MISSION — S1599 XX99 CANONICAL SUMMARY (P7 — LAST — ARC-CLOSE)

**Recommended path: `Start research group 1500: xx99`** OR `Close research group 1500` (short command per playbook §21 — both resolve to canonical-summary drafting).

Seventh and FINAL slot under Group 1500. Per parent §5 sequence: xx99 consumes P1-P6 evidence + resolves contradictions + produces the Chris-gated posture-decision brief per D59 (evidence-consolidation, NOT posture selection) + applies playbook §11.3 §10 meta-methodology (third application after S1399 first + S1499 second).

**xx99 scope per parent §12.1 arc-close deliverables:**

1. Consolidated Executive Summary + Domain Shape + Cross-Cutting Patterns (~13 pattern classes from arc catalog).
2. **§5 Posture-Decision Evidence Brief** (D59 load-bearing) — consumes §20.6 Cat F evidence plan verbatim + P1-P5 evidence with F2-fold scoring rubric applied per criterion.
3. **§7 Anchor-Update Recommendations** — concrete edits to `PLATFORM_INVENTORY.md` §3.10 + NEW `docs/topics/sports-betting.md` first landing + ARCHITECTURE_INDEX §5 gap entries consolidated (Group 1500 → closed).
4. **§8 Follow-On Research Queue T1-T10 unified tier structure** matching S1499 T1-T10 shape.
5. **§10 meta-methodology template third application:** 10.1 what worked; 10.2 codify-to-playbook-v3 candidates with §20 two-triggers threshold; 10.3 anti-patterns; 10.4 playbook suggestions; 10.5 xx99 template suggestions.
6. **§12.5 Sports Domain Lifecycle Traceability Table** — xx99 assembles full table with rows filled from P1-P6 evidence (odds ingestion → fixture / entity identity resolution → normalization → prediction → user wager → outcome verification → learning-loop feedback → signal aggregation gap).
7. **§12.4 discriminative-value criterion check** for playbook v3 §11.1 template promotion (Chris caution 1 fold from parent scoping).
8. **Cross-arc delegations** to S1300 Memory (if integration posture) + Group 1600 Content (if Chris opens).
9. Playbook §11.3 12-section template applied.

**Load-bearing S1506 outputs to inherit at S1599:**

- §20.6 posture-decision evidence plan verbatim into xx99 §5 posture-decision brief.
- §20.7 Sports Domain Lifecycle Traceability Table stub → xx99 assembles full table with all 6 P1-P6 audit rows filled.
- §20.3 5 new pattern classes → xx99 §4 cross-cutting patterns consolidates with S1501-S1505 pattern classes into ~13-class arc catalog.
- §20.9 6-arc consumer-side pattern completion → xx99 anchor for Signal Engine posture criterion (§20.6 §A1 / §B1).
- §20.10 6-sibling exemplar pattern completion → xx99 §10.2 codify-to-playbook-v3 candidate for D62 = (a) mini-schema propagation.
- §19 T1-T5 tier-ordered future research → xx99 §8 arc-wide T1-T10 unified tier structure consolidation.
- §14 drift matrix + §15 debt matrix + §17 duplicate/overlapping systems + §18 ownership gaps → xx99 §6 unresolved unknowns + §7 anchor-update recommendations.

Session flow at S1599 open:

1. `context-kit orient` (session-open protocol).
2. Confirm `service_context: local` via `platform_config_tool overview` on arc pin `pa-791b3db549a64e54`.
3. Check if S1506 artifact set merged to `main` between sessions.
4. If not yet merged: complete Chris merge + PR merge.
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
6. Chris ratifies P7 kickoff via `Start research group 1500: xx99` OR `Close research group 1500` (short command).
7. Draft xx99 at `docs/research/domains/sports/1599_sports_canonical_summary.md` per playbook §11.3 12-section template.
8. **Load and consolidate** §20.6 posture-decision evidence plan from S1506 (Cat F) + §2.1 contract statements from all 6 siblings + §14 drift matrices + §15 debt matrices + §17 duplicates + §18 ownership gaps + §19 future research from all 6 siblings.
9. **Assemble Sports Domain Lifecycle Traceability Table** per parent §12.5.
10. **Apply F2-fold scoring rubric** across P1-P6 evidence corpus to §5 posture-decision brief.
11. **§10 meta-methodology third application** per Chris directive S1399 close 2026-07-01.
12. **§12.4 discriminative-value criterion check** per parent §12.4 + Rigby SIGN cycle 1 Q7 fold — must demonstrate ≥3 of 4 evidence types including at least one of (scope confusion prevented) OR (cleaner arc close) before playbook v3 §11.1 promotion triggers.
13. Route to Rigby per §15 stage table — Light SIGN + potentially Full SIGN if xx99 triggers major cross-references; fresh SIGN isolation pin per §15; **D48 preemptive stability-probe gate 10th arm** (if held-clean → five-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1599).
14. Fold SIGN-with-edits into xx99 doc.
15. **Arc close:** Group 1500 arc pin `pa-791b3db549a64e54` retires per playbook §16 D53 arc-close discipline (matches S1499 pattern).
16. Session close: handoff + PR + docs cascade.
17. **Post-arc T-slot follow-ons queued:** all 14 Cat F findings + prior sibling findings queued per §8 T1-T10 tier structure.

**Not next:** any specific implementation work per playbook §14 no-implementation rule. Posture selection is Chris-gated post-arc ADR per D59.

**Also queued at future sessions:**

- Chris-gated posture-decision ADR (post-xx99; T1 highest per Group 1400 precedent).
- DBAO codename resolution ADR (D61 parent parked candidate; T1 or T2).
- Subsequent PRs from Group 1400 §7 anchor-updates (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499).
- CLAUDE.md 3-employees narrative anchor drift (still flagged); `verify_doc_claims --only-drift` verifier subsequent PR.
- Post-arc follow-on PRs from all 6 Cat A-F findings: `daily_betting_digest` beat-restoration OR intentional-deferral documentation + `SportsBettingBrief` consumer-or-remove decision + `/ws/dbao/` + `/ws/dbao-dashboard/` MOCK-DATA-CONSUMER remove-or-relocate decision + `markets`+`bankroll` DEAD-RENDER-PATH restore-or-delete decision + 2 AUTH-DRIFT endpoints AllowAny-migrate OR frontend-error-handling + `send_query_status`+`handle_run_analytics` stub removal or implementation + `x-dbao-client` CORS whitelist removal + VITE/EXPO DBAO env-var cleanup + DBAODashboardView cleanup + `_impl_collect_sports_odds_intelligence` docstring or channel fix + duplicate `sports_intelligence` hardcoded literal cleanup + Discord surface refactor to route through SportsBettingCoordinator + `RealtimeIntelligenceEngine` bootstrap decision + CODEOWNERS assignment for sports runtime files + sports test coverage backfill.

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1506 artifact set is on `main` between sessions
4. If not yet merged: Chris merge + PR merge
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
6. Chris ratifies P7 xx99 kickoff (S1599 default lean per parent §5 sequence)
7. Execute S1599 xx99 canonical summary per playbook §11.3 12-section template + §10 meta-methodology third application + §12.5 Sports Domain Lifecycle Traceability Table + F2-fold scoring rubric applied across P1-P6 evidence + §12.4 discriminative-value criterion check

---

## PA / Rigby context

- **Arc pin at session start:** `pa-791b3db549a64e54` (Group 1500 arc pin; already active in `tools/pa_local.sh:128`; carries Group 1500 arc-open context through P7 xx99 per playbook §16 retain rule).
- **S1506 SIGN routing:** Full SIGN cycle 1 ran on fresh isolation pin `pa-c2cdbd5c0b8c451b` per playbook §15 stage table (retired at S1506 close via `session_tool.retire`); cycle 2 SIGN-clean anticipated post-fold-land at PR-merge or Chris-invoked follow-up.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506 9-session confirmed — D48 CODIFICATION-READY at 9-arc threshold, four-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506):** if Rigby generic-errors on turn 1 of a fresh SIGN pin, apply D45 recovery pattern preemptively — warmup-ping first (ultra-short "confirm ready" probe), then batched titles-only SIGN 2-3 findings per prompt. S1506 marked the 9-arc threshold with entirely clean stability probe + zero worker-instability across 3 substantive SIGN turns; xx99 §10.2 codifies into playbook v3 §15 with strengthened 9-arc evidence base + four-consecutive-fully-clean-arms sub-pattern. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.
- **Non-standard pa_chat.py invocation for fresh SIGN pin:** `tools/pa_local.sh` hardcodes `--conversation` — for fresh SIGN pin, use direct pa_chat.py invocation with env vars: `PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-token> .venv/bin/python tools/pa_chat.py "$(cat /tmp/msg.txt)" --tools --conversation <fresh-pin-id>` — write prompt to file first to avoid shell backtick interpretation.
- **Continued at S1506: Rigby ORM probe as parent-Claude verifier-loop tool BEFORE draft integration — S1506 non-application note.** The BEFORE-SIGN ORM probe pattern (first applied S1503, second applied S1504, non-applied S1505) did NOT apply cleanly to S1506 because Cat F has no primary "did this task fire?" ORM claim to verify — the load-bearing claims were file:line grep-verifiable (all 6 verified pre-SIGN via parent-Claude direct reads before draft integration). 2-arc evidence base for BEFORE-SIGN ORM probe pattern holds; pattern generalizes to specific claim classes not all audits.
- **Continued at S1506: SIGN cycle 1 batch 1 verdict-text re-request recovery pattern — S1506 non-trigger note.** The pattern (first applied S1504) did NOT trigger this session — Rigby's cycle 1 Batch 1 delivered verdict text normally per explicit "give me VERDICT TEXT" framing (preventive-framing pattern replication from S1505). 1-arc evidence base holds; S1505+S1506 non-trigger observations reinforce candidate for playbook v3 §15 as preventive framing rule.
- **Continued at S1506: Rigby Q8 grep-verified confidence-upgrade pattern — S1506 non-trigger note.** The pattern (first applied S1505) did NOT trigger this session — file:line claims were verified pre-SIGN via parent-Claude verifier-loop rather than intra-SIGN grep by Rigby. 1-arc evidence base holds. Pattern generalizes to audits with heavy file:line-verifiable load-bearing claims.

## Repo state at next-session open

- **Branch state (at S1506 close, before merge):** `docs/session-1506-sports-cat-f-audit` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1506 handoff at `docs/handoffs/SESSION_1506_SPORTS_CAT_F_AUDIT.md`. Prior handoffs: SESSION_1505 (Sports Cat E); SESSION_1504 (Sports Cat D); SESSION_1503 (Sports Cat C); SESSION_1502 (Sports Cat B); SESSION_1501 (Sports Cat A); SESSION_1500 (Sports arc open); SESSION_1499 (Revenue arc-close canonical summary); SESSION_1406 (Cat F final); SESSION_1405 (Cat E); SESSION_1404 (Cat D); SESSION_1403 (Cat C); SESSION_1402 (Cat B); SESSION_1401 (Cat A); SESSION_1400 (Group 1400 arc open); SESSION_1399 (Group 1300 canonical summary — first xx99); SESSION_1300-SESSION_1305 (Group 1300 children).
- **ARCHITECTURE_INDEX version:** v33 (bumped this session with §1.36 S1506 Cat F audit + §8 timeline S1506 row + v33 preamble). Next bump at S1599 close (v33 → v34 for §1.37 canonical summary + arc-close markers).
- **OPEN_ARCS state:** Group 1500 row current-child field advanced to "S1506 SIGN-with-edits cycle 1 (F1-F2 folds landed, cycle 2 anticipated, commit-gated) + S1599 xx99 canonical summary queued next (LAST)"; **all 6 child audits complete**; row remains In-progress. At S1599 close, row moves In-progress → Closed section per playbook §16. Group 1400 remains in Closed section. Next arc-open (post-Group-1500 close at S1599) populates queue with Group 1600 Content / Deliverables / Publishing default lean per playbook §22.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1506 artifact set is on `main` — if yes, next session branches off `main`
- [ ] Run post-merge 4-step docs cascade + `build_docs_provenance` if not yet run per `feedback_docs_cascade_at_every_close.md`
- [ ] Chris ratifies P7 kickoff: default lean is `Start research group 1500: xx99` OR `Close research group 1500` (S1599; **LAST — arc-close**)
- [ ] Execute S1599 xx99 canonical summary per playbook §11.3 12-section template + §10 meta-methodology third application (after S1399 first + S1499 second)
- [ ] **Consume §20.6 Cat F posture-decision evidence plan verbatim** into xx99 §5 posture-decision brief with F2-fold scoring rubric applied across P1-P6 evidence corpus
- [ ] **Assemble Sports Domain Lifecycle Traceability Table** per parent §12.5 with rows filled from P1-P6 evidence
- [ ] **§12.4 discriminative-value criterion check** for playbook v3 §11.1 template promotion (must demonstrate ≥3 of 4 evidence types including at least one of scope-confusion-prevented OR cleaner-arc-close per Rigby SIGN cycle 1 Q7 fold from parent scoping)
- [ ] Route xx99 to Rigby per playbook §15 with D48 preemptive stability-probe gate (10th-arm reinforcement of CODIFICATION-READY 9-arc pattern; if held-clean → five-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1599)
- [ ] **Arc close:** Group 1500 arc pin `pa-791b3db549a64e54` retires per playbook §16 D53 arc-close discipline (matches S1499 pattern)
- [ ] Handoff SESSION_1599 + PR + docs cascade
- [ ] Post-arc: queue Group 1600 open OR other post-arc work per §22 domain queue

## Reference — where to look

- **S1506 Cat F audit doc:** `docs/research/domains/sports/1506_sports_cross_domain_integration_lens_and_posture_decision_framing_audit.md` — 20-section child audit + §2.1 Cat F contract statement (5 guarantees + 11 non-guarantees) + §7.1-7.6 six runtime flows + §14 drift matrix (12 items with 5 NEW pattern classes) + §15 debt matrix with F1-F2 folds landed + §17 duplicate/overlapping systems (5 items) + §18 ownership gaps (4 items compound) + §19 T1-T5 tier-ordered future research + **§20.6 POSTURE-DECISION EVIDENCE PLAN** (D59 load-bearing deliverable — 7 integration criteria A1-A7 + 7 island criteria B1-B7 + 4 cross-cutting C1-C4 + failure-mode table D + cost asymmetry summary E + F2-fold scoring rubric with thresholds F + explicit "Chris-gated selection" tag) + §20.7 Sports Domain Lifecycle Traceability Table stub + §20.8 F1-F2 SIGN fold notes with cycle 1 verdict + §20.9 6-arc consumer-side pattern completion + §20.10 6-sibling exemplar pattern completion for D62 = (a)
- **S1505 Cat E audit doc:** `docs/research/domains/sports/1505_sports_frontend_surface_audit.md`
- **S1504 Cat D audit doc:** `docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md`
- **S1503 Cat C audit doc:** `docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md`
- **S1502 Cat B audit doc:** `docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md`
- **S1501 Cat A audit doc:** `docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md`
- **Group 1500 parent scoping doc:** `docs/research/domains/sports/1500_sports_domain_scoping.md` — arc-open scoping + Phase 0 F.i/F.ii/F.iii second application UNCHANGED + candidate subdomain taxonomy A-F + child mission sequence P1-P7 + D62 = (a) 4-item mini-schema propagation directive
- **Group 1400 canonical summary:** `docs/research/domains/revenue/1499_revenue_canonical_summary.md` (playbook §11.3 §10 second application — precedent for S1599)
- **Group 1300 canonical summary:** `docs/research/domains/memory/1399_memory_canonical_summary.md` (first formal xx99 canonical summary — original precedent for playbook §11.3 §10 template)
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v33:** `docs/research/ARCHITECTURE_INDEX.md` — S1506 §1.36 + §8 timeline S1506 row + v33 preamble
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1500 In-progress section with S1506 SIGN-with-edits current-child field + S1599 xx99 queued next
- **AUDIT_FINDINGS.md #12:** canonical Celery deferred-by-policy list
- **CELERY_AUDIT.md:** canonical Celery inventory
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`

## Doctor warnings to expect

- Inventory freshness (unchanged this session — child audit only, no runtime changes)
- Handoff numbering continuity — S1506 continues arc-numbering convention (S1300 arc-open + S1301-S1305 children + S1399 canonical; S1400 arc-open + S1401-S1406 children + S1499 canonical; S1500 arc-open + S1501-S1506 children + **S1599 canonical queued next**)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; S1506 doesn't touch narrative anchor); xx99 (S1599) §7 anchor-update recommendations will name refresh candidates
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1506 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold)
- Group 1400 post-arc §7 anchor-updates still pending (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499)
- `sports_odds` structural gap CONFIRMED at code level AND completed as 6-arc consumer-side pattern by S1502 §14.3 (Cat B) + S1503 §14.3 (Cat C) + S1504 §14.5 (Cat D) + S1505 §14.6 (Cat E) + S1506 §14.3 (Cat F) — xx99 §5 posture-decision brief §A1 / §B1 owns
- **`daily_betting_digest` CRITICAL zero-fire status** — S1504 §14.1 flag still open (not remediated by research audits)
- **`SportsBettingBrief` CRITICAL write-only-and-forgotten status** — S1504 §14.3 upheld + strengthened by S1505 §14.4 + Cat F §9.1 REST endpoint bypass confirmed
- **`/ws/dbao/` + `/ws/dbao-dashboard/` MOCK-DATA-CONSUMER pattern (S1505 §14.1 + S1506 §14.7 sibling route expansion) — footprint expands 1 route → 2 routes.** Post-arc follow-on PR needed: cover both routes
- **`markets` + `bankroll` DEAD-RENDER-PATH tabs (S1505 §14.2)** — Post-arc follow-on PR needed
- **2 AUTH-DRIFT endpoints (S1505 §14.3)** — Post-arc follow-on PR needed
- **NAMING-CONVENTION-WITHOUT-MATERIALIZATION at DBAO (S1506 §14.1 — NEW at S1506).** Load-bearing for D61 codename resolution ADR — Chris-gated post-arc T-slot
- **DECOUPLED-VERIFICATION-SYSTEMS at BettingOutcomeVerifier ↔ MLPrediction (S1506 §14.2 — NEW at S1506).** Post-arc T2 design-preparation follow-on for wager↔prediction reconciliation
- **DECLARED-FEATURE-FLAG-GATES-NOTHING at `sports_intelligence` (S1506 §14.4 — NEW at S1506).** Post-arc T2 either wire flag or remove
- **DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT at `_impl_collect_sports_odds_intelligence` (S1506 §14.8 — NEW at S1506).** Post-arc T4 cleanup
- **SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION at RealtimeIntelligenceEngine cross-domain loops (S1506 §14.9 — NEW at S1506).** Post-arc T2 either implement or rename/remove
- **LATENT-ZERO-FIRE at RealtimeIntelligenceEngine (S1506 §14.10)** — Post-arc T3 bootstrap decision
- **CODEOWNERS compound gap across 6 sports runtime files (S1506 §18.1)** — Post-arc T4 cleanup
- **`docs/topics/sports-betting.md` gap after 6 audits (S1506 §19.5)** — xx99 §7 anchor-update recommendation lands topic doc
- **D48 preemptive stability-probe gate 9th-arm CODIFICATION-READY** — S1599 xx99 SIGN cycle would be 10th arm; xx99 (S1599) §10.2 owns eventual playbook v3 §15 codification recommendation with strengthened 9-arc evidence base + four-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506 (five-consecutive if S1599 holds clean) + BEFORE-SIGN Rigby ORM probe pattern (2-arc evidence base) + S1504 SIGN cycle 1 batch 1 verdict-text re-request recovery pattern (1-arc; S1505+S1506 non-trigger observations reinforce candidate for preventive framing rule) + S1505 Rigby Q8 grep-verified confidence-upgrade pattern (1-arc; S1506 non-trigger note).
