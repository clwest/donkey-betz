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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1601 close:**

- **ACTIVE ARC PIN:** `pa-f52acf3f8d394faa` (Group 1600 arc pin; minted at S1600 open via `session_tool.create_fresh`; **retained through P7 xx99 at S1699** per playbook §16 arc-continuity rule — carries Group 1600 context through S1602 Cat B + S1603 Cat D + S1604 Cat C + S1605 Cat E + S1606 Cat F + S1699 xx99).
- **`tools/pa_local.sh:128` already at `pa-f52acf3f8d394faa`** — no line-128 rotation needed at S1602 open.
- **Retired at S1601 close:** SIGN isolation pin `pa-9f075a024552b663` (Rigby `session_tool.retire`: `updated_count: 3, retired: true, is_current_bound: false, previously_active: true`).
- **Retired earlier at S1599 close:** Group 1500 arc pin `pa-791b3db549a64e54`.
- **Retired earlier at S1506/S1505/S1504/S1503/S1502/S1501 closes:** SIGN isolation pins `pa-c2cdbd5c0b8c451b` / `pa-546de7ebe8c8b885` / `pa-af2bf7f2d1a0ef61` / `pa-8ce5f949bed5e093` / `pa-64c019d7e6685d31` / `pa-a39069230ab64450`.
- **Retired earlier at S1499 close:** Group 1400 arc pin `pa-34d43795e1b24bd3` + SIGN isolation pin `pa-877f1919efaa48e4`.
- **Retired earlier:** `pa-8660ea7cfecd4bc6` (S1406); `pa-4bdd5ad264674ce8` + `pa-637331c5f9574a10` (S1405); `pa-87ee24cd0d3947ce` (S1404); `pa-fba0c4c81fba4922` (S1403); `pa-4a0a28edcb7a45ec` (S1402); `pa-16d8b24d30e7a7d8` (S1401); `pa-aa54193f240f4846` + `pa-4fc3329d0db6484f` (S1399 Group 1300 arc-close).

Use `tools/pa_local.sh` for all chats — line 128 already pointing at active Group 1600 arc pin.

## READ THIS SECOND — S1601 GROUP 1600 CAT A LANDED; S1602 CAT B QUEUED NEXT

Session 1601 shipped the **Group 1600 Cat A ClaimsPack + Content Deliberation Pipeline v2 child audit** at `docs/research/domains/content/1601_content_claims_pack_deliberation_pipeline_v2_audit.md` (1,792 lines after F1-F6 folds; `status: active`, `category: child_audit`, `session: 1601`, `child_slot: P1`, `domain_slug: content`, `research_group: 1600`, `authority: child-audit`; playbook §11.2 20-section template + six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 6 load-bearing pre-Explore claims (all 6 verified pre-Explore fire); applies parent D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront at §4.8 + §5.6 + §6.5 + §8.5 per parent D68 F8/F10 folds — **first sibling of Group 1600 to propagate the pattern upfront**).

**Two parent §3 Cat A load-bearing questions resolved:**

- **Q1 Citation integrity posture** — Cat A enforces `claims_count == 0` gate only at `core/services/content_deliberation_runner.py:99-103`; NO per-claim `[C-xxxxxxxxxx]`-in-draft regex verifier code-side. Cat B `FactCheckReviewer` is LLM prompt-based, not code-enforced. **Net: two-gate policy is LLM-verified, not code-enforced.** Owed to xx99 D65b evidence plan.
- **Q2 v2 pipeline runtime posture** — **strictly on-demand**; grep-verified ZERO beat entries fire `ContentDeliberationRunner.run_blog()`; three triggers only: REST `POST /api/v1/research/self-blog/generate-v2/` at `core/views_research_demo.py:1106-1145`; PA tool `blog_tool action=generate` (no topic) at `core/services/td_handlers_content.py:1480-1505`; Celery task `generate_self_blog_deliberation_task.delay()` at `core/tasks.py:5758-5761`. Adjacent lanes (newsletter, outreach) do NOT share v2 pipeline machinery.

**Rigby SIGN cycle 1 SIGN-with-edits at Medium confidence** on fresh isolation pin `pa-9f075a024552b663` (retired at S1601 close). **F1-F6 folds landed pre-commit:**

- **F1** SelfBlog canonicalization-debt reframe (§1 HEADLINE + §9.1 + §16.1) — `SelfBlog.objects.create` at `content_deliberation_runner.py:401` bypass of `deliverable_factory` = canonicalization debt Cat A flags as D65a evidence input, NOT proof of intentional island architecture.
- **F2** Silent partial-source failure severity MEDIUM → HIGH (§1 item 3 + §15.2) — Rigby rationale: "truth/evidence integrity degradation without explicit degraded-status contract".
- **F3** RAG scope explicit cross-tenant/workspace framing (§1 item 1 + §9.3 + §14.4 + §15.3) — pipeline could ground drafts in evidence Cat A should not have permission to see.
- **F4** RAG scope = riskiest overall Cat A finding elevation (§1 item 1 renumbered #3 → #1 with RIGHIEST tag; §19.6 T1 queue reordered R.CONTENT.RAG-SCOPE #1).
- **F5** Fix "ZERO writes to Cat B/C/D" Exec Summary contradiction (§1 + §16.1) — corrected to "ZERO writes to Cat B/C; ONE write to Cat D (SelfBlog.objects.create at :401) as persistence handoff".
- **F6** Verification-report endpoint boundary caution pin at `core/views_deliberation.py:394-561` (§6.1).

**D48 preemptive stability-probe gate 10th-arm outcome:** SIGN cycle 1 held clean in three batches on fresh isolation pin; no worker instability observed; **five-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601 CONFIRMED** per D48 gate expectation at S1600 open. Codification-ready for playbook v3 §15 per S1599 §10.2 6-candidate codify list.

**Session close artifacts committed at S1601 close:**

```
docs/research/domains/content/1601_content_claims_pack_deliberation_pipeline_v2_audit.md    [new; 1792 lines; child audit]
docs/research/ARCHITECTURE_INDEX.md                                                          [modified — v35 → v36; §1.39 registration + §8 timeline S1601 row + v36 preamble]
docs/research/OPEN_ARCS.md                                                                   [modified — Group 1600 row current-child S1601 → S1602 + frontmatter S1601 close preamble]
docs/handoffs/SESSION_1601_CONTENT_CAT_A_AUDIT.md                                            [new — S1601 handoff]
00-START-NEXT-SESSION.md                                                                     [modified — this file]
```

Handoff: `docs/handoffs/SESSION_1601_CONTENT_CAT_A_AUDIT.md`.

### NEXT-SESSION MISSION — S1602 CAT B CONTENT REVIEWERS + DECISION ENFORCEMENT

**Recommended path:** `Continue research group 1602` (short command per playbook §21).

Second child under Group 1600. Per D66 P2 slot: S1602 Cat B owns the pipeline canonical-decision on **"how do reviewer verdicts + DecisionEnforcer produce PUBLISH/REVISE/KILL?"**.

**Cat B scope (per parent §3):** 3-reviewer panel (`SkepticReviewer` + `FactCheckReviewer` + `DomainPersonaReviewer` conditional) + `run_reviews` dispatch function + `DecisionEnforcerAgent` + synthetic-FAIL failure handling + single rewrite pass. **Boundary rule per parent F8 fold:** Cat B owns *pre-publish gating: whether the draft passes reviewer verdicts + decision-enforcement contract*. Cat B does NOT own downstream quality thresholds (Cat C) or Deliverable base object model (Cat D).

**Load-bearing questions for Cat B (per parent §3 B):**

- Are reviewers pure-function (prompt-based dispatch, no class) or class-based? Confirm dispatch shape at `content_review_panel_v2.py:208`.
- Two `content_review_panel` files exist: `content_review_panel_v2.py` (v2 canonical) + `content_review_panel.py` (v1 legacy instantiates `DomainContentContextBuilder` at :82-85). Which is the canonical runtime path? What's the migration plan? (v1-vs-v2 canonicalization posture per parent §6.1 parked issue.)

**Load-bearing inheritance from S1601 (§20.6 cross-arc handoffs to S1602):**

- **Resolve UNK-2:** verify FactCheckReviewer per-claim `[C-xxxxxxxxxx]` citation enforcement mechanism (LLM prompt vs regex vs typed constraint) on draft text. This is the **remaining half of S1601 HIGH-severity §15.1 gap** — S1601 established Cat A does NOT do code-side per-claim verification; S1602 confirms whether Cat B does.
- Verify 3-reviewer panel dispatch shape + synthetic-FAIL semantics + `DomainPersonaReviewer` conditional threshold (confidence ≥ 0.2 per topic doc `content-pipeline.md:75`).
- Inherit S1601 §14 drift matrix + §15 debt matrix rows tagged "Cat B-owned verification needed".

**Alternative near-term (Chris-gated pre-S1602):** T1 R.CONTENT.RAG-SCOPE cross-arc verification via Cat E S1605 or Memory arc — **resolves S1601 riskiest overall finding** (Document workspace FK schema UNK-1) pre-S1602 if Chris prioritizes closing the riskiest finding first before continuing the D66 sequence.

Session flow at S1602 open:

1. `context-kit orient` (session-open protocol per memory rule).
2. Confirm `service_context: local` via `platform_config_tool overview` on arc pin `pa-f52acf3f8d394faa`.
3. Check if S1601 artifact set merged to `main` between sessions.
4. If not yet merged: Chris merge + PR merge.
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
6. Chris ratifies P2 kickoff via `Continue research group 1602` (S1602 default lean).
7. Draft S1602 audit at `docs/research/domains/content/1602_content_reviewers_decision_enforcement_audit.md` per playbook §11.2 20-section template + six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on load-bearing pre-Explore claims + D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront per parent D68 F8/F10 folds adopted.
8. Route to Rigby per §15 stage table — Full SIGN + fresh SIGN isolation pin per §15; **D48 preemptive stability-probe gate 11th arm** (if held-clean → six-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602 anticipated).
9. Fold SIGN-with-edits into S1602 doc.
10. Session close: handoff + PR + docs cascade.

**Not next:** any specific implementation work per playbook §14.5 no-implementation rule. Posture selection is Chris-gated post-arc ADR per D65a/D65b/D65c.

**Also queued at future sessions:**

- **S1603 Cat D Deliverable Base + Specialized Variants** child audit (F3 fold: moved from P4→P3 — HEADLINE child; consumes S1601 §9.1 SelfBlog.objects.create bypass as D65a HEADLINE evidence input).
- **S1604 Cat C PublishGate + Publish Rails** child audit (F3 fold: moved from P3→P4).
- S1605 Cat E Rigby-Facing Content PA Tooling + Approval UX child audit (resolves S1601 UNK-1 Document workspace FK schema → T1 R.CONTENT.RAG-SCOPE).
- S1606 Cat F Cross-Domain Integration Lens & Posture Decision Framing child audit (LAST — consumes P1-P5 evidence + produces xx99 §5 D65a/D65b/D65c three-axis posture-decision evidence plan).
- S1699 xx99 canonical summary (**fourth application** of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second + S1599 third).
- **Post-arc Chris-gated ADRs (T1 owed):** R.CONTENT.RAG-SCOPE (Rigby-verified riskiest overall) + R.CONTENT.CITATION-INTEGRITY + R.CONTENT.POSTURE (three-axis D65a/D65b/D65c integration-vs-island posture selection — consumes xx99 §5 verbatim) + cross-arc re-scope decisions on Group 1500 T1.h SportsBettingBrief consumer-or-remove + Group 1400 R.B1 OutreachDraft delivery ADR.

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1601 artifact set is on `main` between sessions
4. If not yet merged: Chris merge + PR merge
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
6. Chris ratifies P2 S1602 kickoff (S1602 default lean per parent §5 sequence) — OR chooses alternative near-term T1 R.CONTENT.RAG-SCOPE cross-arc verification
7. Execute S1602 Cat B audit per playbook §11.2 20-section template + 6-parallel-Explore sweep + D62 = (a) 6-sibling exemplar mini-schema propagation-upfront per D68 F8/F10 folds

---

## PA / Rigby context

- **Arc pin at session start:** `pa-f52acf3f8d394faa` (Group 1600 arc pin; already active in `tools/pa_local.sh:128`; retained through P7 xx99 at S1699 per playbook §16 arc-continuity rule).
- **S1601 SIGN routing:** Full SIGN cycle 1 SIGN-with-edits at Medium confidence on fresh isolation pin `pa-9f075a024552b663` (retired at S1601 close); F1-F6 folds landed pre-commit; three-batch SIGN pattern per memory rule `feedback_rigby_sign_worker_instability_recovery.md`. Full SIGN Q1-Q9 pressure-test owed at each subsequent child audit + S1699 xx99.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 10-arc CODIFICATION-READY at S1601 close):** S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506+S1601 10-arc pattern confirmed. **Five-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601 CONFIRMED at S1601 close.** D48 preemptive stability-probe gate 11th arm anticipated at S1602 open; six-consecutive-fully-clean-arms sub-pattern anticipated if held clean. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.

## Repo state at next-session open

- **Branch state (at S1601 close, before merge):** `docs/session-1601-content-cat-a-audit` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1601 handoff at `docs/handoffs/SESSION_1601_CONTENT_CAT_A_AUDIT.md`. Prior handoffs: SESSION_1600 (Content arc-open parent scoping); SESSION_1599 (Sports arc-close canonical summary); SESSION_1506 (Sports Cat F); SESSION_1505 (Sports Cat E); SESSION_1504 (Sports Cat D); SESSION_1503 (Sports Cat C); SESSION_1502 (Sports Cat B); SESSION_1501 (Sports Cat A); SESSION_1500 (Sports arc open); SESSION_1499 (Revenue arc-close); SESSION_1406 → SESSION_1400 (Revenue arc); SESSION_1399 (Group 1300 canonical summary).
- **ARCHITECTURE_INDEX version:** v36 (bumped this session with §1.39 S1601 registration + §8 timeline S1601 row + v36 preamble). Next bump at S1602 Cat B close.
- **OPEN_ARCS state:** Group 1600 row current-child advanced S1601 → S1602 this commit. Group 1500 remains in Closed section. Group 1400 remains in Closed section. Group 1300 remains in Closed section.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1601 artifact set is on `main` — if yes, next session branches off `main`
- [ ] Run post-merge 4-step docs cascade + `build_docs_provenance` if not yet run per `feedback_docs_cascade_at_every_close.md`
- [ ] Chris ratifies P2 kickoff: default lean is `Continue research group 1602` (S1602 Cat B; **second child audit under Group 1600**) OR alternative T1 R.CONTENT.RAG-SCOPE cross-arc verification
- [ ] Execute S1602 Cat B audit per playbook §11.2 20-section template + 6-parallel-Explore sweep + D62 = (a) 6-sibling exemplar mini-schema propagation-upfront per D68 F8/F10 folds
- [ ] **Apply Cat B boundary rule per F8 fold:** Cat B owns pre-publish gating (reviewer verdicts + decision-enforcement contract); Cat B does NOT own downstream quality thresholds (Cat C) or Deliverable base object model (Cat D)
- [ ] Route S1602 to Rigby per playbook §15 with D48 preemptive stability-probe gate (11th arm; if held-clean → six-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602)
- [ ] Handoff SESSION_1602 + PR + docs cascade

## Reference — where to look

- **S1601 audit doc:** `docs/research/domains/content/1601_content_claims_pack_deliberation_pipeline_v2_audit.md` — 1792-line child audit; playbook §11.2 20-section template + D62 4-item mini-schema at §4.8/§5.6/§6.5/§8.5; §14 Known Drift matrix; §15 Known Technical Debt matrix with F2 severity elevation; §16 Boundary Violations with F1 SelfBlog reframe + F5 writes-summary correction; §19 Recommended Future Research with F4 T1 R.CONTENT.RAG-SCOPE elevation; §20.5 Rigby SIGN fold notes (F1-F6).
- **S1600 parent scoping doc:** `docs/research/domains/content/1600_content_domain_scoping.md` — Cat A boundary F1 fold + Q1/Q2 load-bearing questions + D66 mission sequence.
- **S1599 xx99 canonical summary:** `docs/research/domains/sports/1599_sports_canonical_summary.md` — playbook v3 §11.1 template promotion TRIGGERED per §12.4.
- **S1500 parent scoping doc:** `docs/research/domains/sports/1500_sports_domain_scoping.md` — D56-D61 precedent.
- **S1400 parent scoping doc:** `docs/research/domains/revenue/1400_revenue_domain_scoping.md` — first application of Chris's Phase 0 methodology.
- **S1499 revenue canonical summary:** `docs/research/domains/revenue/1499_revenue_canonical_summary.md`.
- **S1399 memory canonical summary:** `docs/research/domains/memory/1399_memory_canonical_summary.md` — first xx99 canonical summary.
- **Cross-arc handoffs owed to Group 1600:** S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN CRITICAL + S1504 §5.1 SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS HIGH + S1402 F.B1 Revenue OutreachDraft delivery ZERO outbound channel HIGH + S1403 F.C4 ContentEngagement docstring drift HIGH + S1502 §14.3 SignalCluster pattern_type consumer-side gap 6-arc COMPLETED (S1601 §9.2 CONFIRMED extension to Cat A scope) + S1499 D55 (ii) Revenue Employee + Income/Jobs Employee JobContract split precedent + S1500 D59 posture-decision framing precedent (D65-analog) + S1274 §12.3 P1 Product/Architecture Decision Point precedent.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v36:** `docs/research/ARCHITECTURE_INDEX.md` — S1601 §1.39 + §8 timeline S1601 row + v36 preamble.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1600 row current-child S1601 → S1602 this commit.
- **Content pipeline topic doc:** `docs/topics/content-pipeline.md` — Session 1147 topic doc; drift-labeled pattern-still-valid; nine numeric drift candidates flagged in S1601 §14 for post-xx99 validator rig-up.
- **Prior audit:** `docs/audit-2026/04-content-pipeline.md` — April 2026 audit (referenced in S1601 §11.3).
- **Patents:** `docs/patents/DISCLOSURE_D_CLAIMS_BASED_DELIBERATION.md` (ClaimsPack architecture provenance) + `docs/patents/DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md` (Cat B-primary DecisionEnforcer provenance).
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1601 continues arc-numbering convention (S1300 arc-open + S1301-S1305 children + S1399 canonical; S1400 arc-open + S1401-S1406 children + S1499 canonical; S1500 arc-open + S1501-S1506 children + S1599 canonical; **S1600 arc-open + S1601 first child** + S1602-S1606 children + S1699 canonical queued).
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; S1601 doesn't touch narrative anchor; xx99 S1699 §7 anchor-update recommendations will name refresh candidates).
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1601 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`.
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold).
- Group 1400 post-arc §7 anchor-updates still pending (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499).
- Group 1500 post-arc §7 anchor-updates still pending (`PLATFORM_INVENTORY.md` §3.10 subdivision + DBAO subgroup conditional on T1.b R.DBAO.CODENAME verdict + `PLATFORM_WHAT_IT_IS.md` Sports narrative refresh + NEW `docs/topics/sports-betting.md` first-inventory landing per C2 cross-cutting gate + `.github/CODEOWNERS` 6 sports runtime files).
- **Group 1500 T1 CRITICAL remediation queue still pending (post-arc T1):** R.C1 verify_betting_outcomes beat-restoration ← R.C2 pre-restore-beat concurrency-safety hardening; R.D1 daily_betting_digest beat-restoration OR §12 deferred-list entry ← R.D2 idempotency hardening; R.D3 zero-test-coverage reliability multiplier; R.D4 SportsBettingBrief consumer-or-remove ← T1.a; R.D5 two-writer dedup.
- **Cross-arc re-scope owed (updated by S1601):** Group 1500 T1.h R.D4 SportsBettingBrief consumer-or-remove disposition may be re-scoped by Group 1600 D65a posture selection at S1699 close — S1601 §9.1 `SelfBlog.objects.create` bypass evidence input to D65a per Rigby F1 fold reframe; Group 1400 R.B1 OutreachDraft delivery ADR may be re-scoped similarly.
- **D48 preemptive stability-probe gate 10th-arm CONFIRMED at S1601 close** — five-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601 CODIFICATION-READY for playbook v3 §15.
- **Playbook v3 §11.1 template promotion TRIGGERED at S1599 close** per §12.4 discriminative-value criterion. Group 1600 third application; §12.4 F6-fold-tightened criterion at S1699 close confirms whether pattern holds at third application via required decision-discriminative proof + required disconfirming evidence item.
