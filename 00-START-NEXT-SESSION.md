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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1606 close:**

- **ACTIVE ARC PIN:** `pa-f52acf3f8d394faa` (Group 1600 arc pin; minted at S1600 open via `session_tool.create_fresh`; **retained through P7 xx99 at S1699** per playbook §16 arc-continuity rule — carries Group 1600 context through S1699 xx99 which is the LAST session under Group 1600).
- **`tools/pa_local.sh:128` already at `pa-f52acf3f8d394faa`** — no line-128 rotation needed at S1699 open.
- **Retired at S1606 close:** SIGN isolation pin `pa-8cfafefb67864f83` (Rigby `session_tool.retire`; `updated_count: 2, retired: true`).
- **Retired earlier at S1605 close:** SIGN isolation pin `pa-b1b26f4f35474df8`.
- **Retired earlier at S1604 close:** SIGN isolation pin `pa-4ce64003711de4f1`.
- **Retired earlier at S1603 close:** SIGN isolation pin `pa-8af9063864bf4a7f`.
- **Retired earlier at S1602 close:** SIGN isolation pin `pa-1c5298d807d7a1d2`.
- **Retired earlier at S1601 close:** SIGN isolation pin `pa-9f075a024552b663`.
- **Retired earlier at S1599 close:** Group 1500 arc pin `pa-791b3db549a64e54`.
- **Retired earlier at S1506/S1505/S1504/S1503/S1502/S1501 closes:** SIGN isolation pins `pa-c2cdbd5c0b8c451b` / `pa-546de7ebe8c8b885` / `pa-af2bf7f2d1a0ef61` / `pa-8ce5f949bed5e093` / `pa-64c019d7e6685d31` / `pa-a39069230ab64450`.
- **Retired earlier at S1499 close:** Group 1400 arc pin `pa-34d43795e1b24bd3` + SIGN isolation pin `pa-877f1919efaa48e4`.

Use `tools/pa_local.sh` for all chats — line 128 already pointing at active Group 1600 arc pin.

## READ THIS SECOND — S1606 CAT F LANDED (LAST CHILD); S1699 XX99 CANONICAL SUMMARY QUEUED NEXT (LAST SESSION UNDER GROUP 1600)

Session 1606 shipped the **Group 1600 Cat F Cross-Domain Integration Lens & Posture Decision Framing child audit** at `docs/research/domains/content/1606_content_cross_domain_integration_lens_audit.md` (`status: active`, `category: child_audit`, `session: 1606`, `child_slot: P6`, `domain_slug: content`, `research_group: 1600`, `authority: research`; playbook §11.2 20-section template + evidence-consolidation lens per S1606 punch list allowance "fewer than 6 Explore sub-agents" + parent-Claude verifier-loop per §14 on load-bearing cross-domain binary claims grep-verified against HEAD `c7a3c16e`). **Sixth and LAST child audit under Group 1600 — six-child arc closes with S1606 Cat F.** Applies parent D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront at §1.5 — **sixth and LAST sibling of Group 1600 to propagate the pattern upfront** completing 6-of-6 sequence after S1601 first + S1602 second + S1603 third + S1604 fourth + S1605 fifth.

**Parent §3 F boundary question answered:** *"cross-domain integration surfaces + posture-decision evidence plan owed to xx99 per D65-analog four-axis framing?"* — seven cross-domain integration surfaces inventoried (6 runtime + 1 governance layer per F2 fold) with structurally-asymmetric integration maturity + §20.6 LOAD-BEARING posture-decision evidence plan produced.

- **§20.6 LOAD-BEARING posture-decision evidence plan for xx99 S1699** — 4 axes D65a/D65b/D65c/D65e evaluated across 7 surfaces as applicable per F4 fold + F2 scoring rubric PASS/PARTIAL/FAIL thresholds per key criterion per axis (S1599 §5 F2 fold rubric exemplar). §20.6.5 cross-axis matrix maps each axis × each of 7 surfaces with applicability marker. Explicit Chris-gated selection tag per axis.
- **Seven cross-domain integration surfaces inventoried:** Signal Engine (WORKING consumer coherent island) + Sports (PARTIAL write-only-forgotten + hot-path-choke) + Revenue (EXPERIMENTAL pattern class 2-of-2 ZERO outbound per F3 fold) + Memory (input STABLE + output PARTIAL via PA-tool feedback bridge per F6 fold) + Discord (PARTIAL fire-and-forget no gate integration) + Frontend (INTEGRATED API + ISLAND auth + 2 API adapters per F1 fold) + Employee OS governance layer (PARTIAL via Rigby Documentation Manager per F10 fold).
- **§19.1 T1 ranking consolidates 22 items:** #1-#16 sibling-inherited (RAG-SCOPE riskiest + citation integrity + Cat B truncation/spawn/outbound + Variant categorization + canonical creation + triple-gate + PublishGate scope + post-publish correction + newsletter live-send + OutreachDraft delivery + Rigby tool surface + force-bypass + auto-publish beat + workspace silent-degrade) + #17-#22 Cat F origin (OUTBOUND-DELIVERY-CONSUMPTION-RAILS-GAP per F9 rephrase + UNIFIED-CONTENT-AUTH-LAYER per F5 hypothesis + UNIFIED-EVENT-STREAM + LEARNING-LOOP-BRIDGE promoted from S1601 T5 per F6 fold + CROSS-DOMAIN-EMPLOYEE-ANALOG demoted to T3 per F9 fold severity mismatch + XX99-ADR-BUNDLE renamed from POSTURE per F9 fold).
- **Cross-arc CORRECTION landed via S1605 F1 fold consumption:** auto_publish_approved_blogs beat runtime-verified ABSENT at S1605; 5 doc claims of "daily 6 AM" DRIFT-CONFIRMED-STALE; S1604 D.14.C5 audit-trail gap MOOT because beat never fires; per Cat F F8 fold explicit "S1605 owns runtime probe; Cat F only propagates correction."

**Rigby SIGN cycle 1 SIGN-with-edits at High confidence overall (Batch A 0.78 + Batch B 0.70 + Batch C 0.83 + final consolidated 0.82)** on fresh isolation pin `pa-8cfafefb67864f83` (retired at S1606 close via `session_tool.retire`; `updated_count: 2, retired: true`). **F1-F10 folds landed pre-commit:**

- **F1** — §1.1 §6.3 §20.3 `newsletterApi` claim CORRECTED (Cat F self-caught via targeted grep; only 2 Content-cross-boundary adapters at HEAD not 3).
- **F2** — §1.1 seven-surface framing clarification (Employee OS labeled "governance layer").
- **F3** — §1.1 pattern class 3-of-3 REBUCKETING to 2-of-2 at Content ↔ Revenue (BlockchainAuditBrief stays Sports-orphan not Revenue-adjacent).
- **F4** — §20.6 "4 axes × 7 surfaces" tighten + concrete PASS/PARTIAL/FAIL thresholds per key criterion per axis.
- **F5** — §17.6 Candidate C extension reframed as Cat F hypothesis with explicit scope boundaries.
- **F6** — §9.4 OUTPUT-side WRITE ABSENT rephrased to PARTIAL PA-tool feedback bridge via `_record_content_feedback` at `td_handlers_content.py:184` (8 call sites).
- **F7** — T.15.F6 severity split (debt condition + solution T1 #17).
- **F8** — §14 D.14.F1 explicit "S1605 owns runtime probe".
- **F9** — §19 T1 ranking corrections (rephrase #17 + demote #21 to T3 + rename #22).
- **F10** — §9.7 Content ↔ Employee OS ABSENT verdict softened to PARTIAL (Documentation Manager JobContract Content-adjacent overlap).

**D48 preemptive stability-probe gate 15th-arm outcome:** Batches A/B/C substantive on fresh isolation pin + final-verdict single-question follow-up clean. **TEN-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606 CONFIRMED** — extends 14-arc pattern to 15-arc + S1606. Codification-ready-STRENGTHENED-FURTHER for playbook v3 §15 with 10-consecutive-fully-clean sub-pattern (from 9-consecutive at S1605 close).

**Session close artifacts committed at S1606 close:**

```
docs/research/domains/content/1606_content_cross_domain_integration_lens_audit.md   [new; child audit; F1-F10 folds landed pre-commit; LAST child under Group 1600]
docs/research/ARCHITECTURE_INDEX.md                                                [modified — v40 → v41; §1.44 registration + line-6 preamble]
docs/research/OPEN_ARCS.md                                                         [modified — Group 1600 line-6 preamble advance S1605 → S1606]
docs/handoffs/SESSION_1606_CONTENT_CAT_F_AUDIT.md                                  [new — S1606 handoff]
00-START-NEXT-SESSION.md                                                            [modified — this file]
```

Handoff: `docs/handoffs/SESSION_1606_CONTENT_CAT_F_AUDIT.md`.

### NEXT-SESSION MISSION — S1699 XX99 CANONICAL SUMMARY (LAST SESSION UNDER GROUP 1600)

**Recommended path:** `Close research group 1699` OR `Start research group 1699` (short command per playbook §21).

**S1699 is the LAST session under Group 1600.** Per D66 P7 slot: S1699 xx99 canonical summary consumes Cat F §20.6 four-axis posture-decision evidence plan verbatim + §17 duplicate/overlapping systems consolidation + §19 T1/T2 cross-arc queue + resolves cross-child contradictions + writes Chris-gated posture-decision brief per D65a/D65b/D65c/D65e (evidence-consolidation across 4 axes, **NOT posture selection**).

**S1699 xx99 is the FOURTH application of playbook §11.3 §10 meta-methodology template** after S1399 first + S1499 second + S1599 third. Non-negotiable per Chris directive S1399 close 2026-07-01: §10 "What This Research Taught Us About How to Do Research" with 5 subsections (10.1 What worked + 10.2 What to codify into playbook v3 per §20 two-triggers rule + 10.3 Anti-patterns to avoid + 10.4 Suggestions for the playbook itself + 10.5 Suggestions for future canonical summaries).

**xx99 canonical summary sections per playbook §11.3:**

1. Executive Summary (500-800 words).
2. What This Arc Answered (per-child rollup: which of 28 canonical questions each child answered).
3. Consolidated Domain Shape (single map/diagram; reader's mental model).
4. Cross-Cutting Patterns (themes visible only across multiple children).
5. Resolved Contradictions (Chris-gated posture-decision brief per D65a/D65b/D65c/D65e — evidence-consolidation NOT posture selection).
6. Unresolved Unknowns.
7. Anchor-Update Recommendations.
   - §7.1 PLATFORM_INVENTORY.md.
   - §7.2 PLATFORM_WHAT_IT_IS.md.
   - §7.3 ARCHITECTURE_INDEX.md.
   - §7.4 Other affected docs (including 5 doc PRs for `auto_publish "daily 6 AM"` staleness + `docs/topics/content-pipeline.md` refresh + `docs/topics/cross-domain-integration.md` NEW landing recommendation).
8. Follow-On Research Queue (ranked next-mission list).
9. Cross-Links to Delegated Arcs.
10. **What This Research Taught Us About How to Do Research** (fourth application meta-methodology; non-negotiable).
    - §10.1 What worked.
    - §10.2 What to codify into playbook v3 (per §20 two-triggers rule; D48 15th arm codification will finalize here).
    - §10.3 What didn't work / anti-patterns to avoid.
    - §10.4 Suggestions for the playbook itself.
    - §10.5 Suggestions for future canonical summaries (optional).
11. Arc Change Log (S1600 arc-open + S1601-S1606 children + S1699 close; each session Rigby verdict + fold count).
12. Appendix — Provenance.

**Boundary rule per playbook §10:** xx99 does NOT re-open earlier children. Consumes only.

Session flow at S1699 open:

1. `context-kit orient` (session-open protocol per memory rule).
2. Confirm `service_context: local` via `platform_config_tool overview` on arc pin `pa-f52acf3f8d394faa`.
3. Check if S1606 artifact set merged to `main` between sessions.
4. If not yet merged: Chris merge + PR merge.
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
6. Chris ratifies P7 kickoff via `Close research group 1699` (S1699 default lean).
7. Draft S1699 xx99 canonical summary at `docs/research/domains/content/1699_content_canonical_summary.md` per playbook §11.3 template + §11.3 §10 meta-methodology template (fourth application).
8. Route to Rigby per §15 stage table — Full SIGN + fresh SIGN isolation pin per §15; **D48 preemptive stability-probe gate 16th arm** (if held-clean → eleven-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699 anticipated).
9. Fold SIGN-with-edits into S1699 doc.
10. Session close: retire Group 1600 arc pin `pa-f52acf3f8d394faa`; handoff + PR + docs cascade.

**Not next:** any specific implementation work per playbook §14.5 no-implementation rule. Posture selection is Chris-gated post-arc ADR per D65a/D65b/D65c/D65e.

**Also queued at future sessions (post-xx99 Chris-gated ADRs — T1 owed):** R.CONTENT.RIGBY-TOOL-SURFACE-UNIFICATION (S1605 D65e-E1 posture) + R.CONTENT.FORCE-BYPASS-AUTH-BOUNDARY (S1605 T1 CRITICAL) + R.CONTENT.AUTO-PUBLISH-BEAT-SCHEDULE (S1605 T1 — cross-arc CORRECTION to S1604 D.14.C5) + R.CONTENT.DELIVERABLE-WORKSPACE-SILENT-DEGRADE (S1605 T1) + R.CONTENT.RAG-SCOPE (S1601 riskiest overall) + R.CONTENT.CITATION-INTEGRITY (S1602 CONFIRMED HIGH) + R.CONTENT.CAT-B-TRUNCATION + R.CONTENT.CAT-B-SPAWN-TASKS + R.CONTENT.CAT-B-OUTBOUND + R.CONTENT.VARIANT-CATEGORIZATION-CLARIFICATION + R.CONTENT.CANONICAL-CREATION-CONTRACT + R.CONTENT.OUTREACHDRAFT-DELIVERY + R.CONTENT.TRIPLE-GATE-COMPOSITION-CONTRACT + R.CONTENT.PUBLISHGATE-SCOPE-CANONICALIZATION + R.CONTENT.POST-PUBLISH-CORRECTION-LOOPS + R.CONTENT.NEWSLETTER-LIVE-SEND-PATH + R.CONTENT.VARIANT-CANONICALIZATION + R.CONTENT.DELIVERABLE-FACTORY-VARIANT-EXTENSION + **R.CONTENT.OUTBOUND-DELIVERY-CONSUMPTION-RAILS-GAP (Cat F origin per F9)** + **R.CONTENT.UNIFIED-CONTENT-AUTH-LAYER (Cat F hypothesis per F5)** + **R.CONTENT.UNIFIED-EVENT-STREAM (Cat F origin)** + **R.CONTENT.LEARNING-LOOP-BRIDGE (Cat F promotes from S1601 T5 per F6)** + **R.CONTENT.CROSS-DOMAIN-EMPLOYEE-ANALOG (Cat F T3 per F9 demotion)** + **R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E (Cat F ADR-packaging)** + cross-arc re-scope decisions on Group 1500 T1.h SportsBettingBrief consumer-or-remove + Group 1400 R.B1 OutreachDraft delivery ADR.

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1606 artifact set is on `main` between sessions
4. If not yet merged: Chris merge + PR merge
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
6. Chris ratifies P7 S1699 kickoff (S1699 default lean per parent §5 sequence — LAST session under Group 1600)
7. Execute S1699 xx99 canonical summary per playbook §11.3 template + fourth application of §11.3 §10 meta-methodology template

---

## PA / Rigby context

- **Arc pin at session start:** `pa-f52acf3f8d394faa` (Group 1600 arc pin; already active in `tools/pa_local.sh:128`; retained through P7 xx99 at S1699 per playbook §16 arc-continuity rule; retired at S1699 close as final Group 1600 close).
- **S1606 SIGN routing:** Full SIGN cycle 1 SIGN-with-edits at High confidence overall (Batch A 0.78 + Batch B 0.70 + Batch C 0.83 + final consolidated 0.82) on fresh isolation pin `pa-8cfafefb67864f83` (retired at S1606 close); F1-F10 folds landed pre-commit; 3-batch SIGN pattern + 1 final-verdict single-question follow-up per memory rule `feedback_rigby_sign_worker_instability_recovery.md`. Full SIGN Q1-Q9 pressure-test owed at S1699 xx99.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 15-arc CODIFICATION-READY-STRENGTHENED-FURTHER at S1606 close):** S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606 15-arc pattern confirmed. **TEN-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606 CONFIRMED at S1606 close.** D48 preemptive stability-probe gate 16th arm anticipated at S1699 open; eleven-consecutive-fully-clean-arms sub-pattern anticipated if held clean. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.

## Repo state at next-session open

- **Branch state (at S1606 close, before merge):** `docs/session-1606-content-cat-f-audit` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1606 handoff at `docs/handoffs/SESSION_1606_CONTENT_CAT_F_AUDIT.md`. Prior handoffs: SESSION_1605 (Content Cat E); SESSION_1604 (Content Cat C); SESSION_1603 (Content Cat D); SESSION_1602 (Content Cat B); SESSION_1601 (Content Cat A); SESSION_1600 (Content arc-open parent scoping); SESSION_1599 (Sports arc-close canonical summary); SESSION_1506 → SESSION_1500 (Sports arc); SESSION_1499 → SESSION_1400 (Revenue arc); SESSION_1399 (Group 1300 canonical summary).
- **ARCHITECTURE_INDEX version:** v41 (bumped this session with §1.44 S1606 registration + line-6 preamble). Next bump at S1699 xx99 close → v42.
- **OPEN_ARCS state:** Group 1600 line-6 preamble advanced S1605 → S1606 this commit; row remains In-progress until S1699 xx99 close moves to Closed section. Group 1500 remains in Closed section. Group 1400 remains in Closed section. Group 1300 remains in Closed section.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1606 artifact set is on `main` — if yes, next session branches off `main`
- [ ] Run post-merge 4-step docs cascade + `build_docs_provenance` if not yet run per `feedback_docs_cascade_at_every_close.md`
- [ ] Chris ratifies P7 kickoff: default lean is `Close research group 1699` (S1699 xx99 Canonical Summary; **LAST session under Group 1600**)
- [ ] Execute S1699 xx99 canonical summary per playbook §11.3 template + **fourth application of §11.3 §10 meta-methodology template** (after S1399 first + S1499 second + S1599 third)
- [ ] **Consume Cat F §20.6 four-axis posture-decision evidence plan verbatim** into §5 Chris-gated posture-decision brief per D65a/D65b/D65c/D65e (evidence-consolidation NOT posture selection)
- [ ] Consume 5 sibling audits (S1601-S1605) + Cat F (S1606) full evidence
- [ ] Apply xx99 boundary rule per playbook §10: xx99 does NOT re-open earlier children
- [ ] Route S1699 to Rigby per playbook §15 with D48 preemptive stability-probe gate (16th arm; if held-clean → eleven-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699 anticipated)
- [ ] Handoff SESSION_1699 + PR + docs cascade
- [ ] **Retire Group 1600 arc pin `pa-f52acf3f8d394faa` at S1699 close** (final Group 1600 close)

## Reference — where to look

- **S1606 audit doc:** `docs/research/domains/content/1606_content_cross_domain_integration_lens_audit.md` — Cat F child audit; playbook §11.2 20-section template + D62 4-item mini-schema at §1.5; §14 Known Drift matrix (7 items); §15 Known Technical Debt matrix (10 items — 4 CRITICAL + 6 HIGH); §16 Boundary Violations (7 items); §17 Duplicate/Overlapping Systems (6 items); §18 Ownership Gaps (10 items); §19 Recommended Future Research with 22 T1 items ranked + 26 T2 + 5 T3 + 5 T4; §20.3a first-class anchor; §20.5 Rigby SIGN fold notes (F1-F10 detailed) + D48 15th arm outcome; **§20.6 LOAD-BEARING posture-decision evidence plan for xx99 (D65a/D65b/D65c/D65e four-axis × 7-surface with F2 scoring rubric); §20.6.5 cross-axis matrix**.
- **S1605 audit doc:** `docs/research/domains/content/1605_content_rigby_pa_tooling_approval_ux_audit.md` — Cat E sibling; §17.5 4-candidate framework + xx99 anchor sentence LOCKED per F9.
- **S1604 audit doc:** `docs/research/domains/content/1604_content_publish_gate_publish_rails_audit.md` — Cat C sibling; §17.4 4-candidate framework for triple-gate composition.
- **S1603 audit doc:** `docs/research/domains/content/1603_content_deliverable_base_variants_audit.md` — Cat D sibling; 3-category variant taxonomy F6 fold.
- **S1602 audit doc:** `docs/research/domains/content/1602_content_reviewers_decision_enforcement_audit.md` — Cat B sibling.
- **S1601 audit doc:** `docs/research/domains/content/1601_content_claims_pack_deliberation_pipeline_v2_audit.md` — Cat A sibling; UNK-1 riskiest overall.
- **S1600 parent scoping doc:** `docs/research/domains/content/1600_content_domain_scoping.md` — parent scoping; §5 D66 P6 slot; §12.1 xx99 deliverables owed.
- **S1599 xx99 canonical summary:** `docs/research/domains/sports/1599_sports_canonical_summary.md` — **F2 fold rubric exemplar consumed at Cat F §20.6**.
- **Cross-arc handoffs owed to Group 1600 xx99:** S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN CRITICAL + S1504 §5.1 SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS HIGH + S1402 F.B1 Revenue OutreachDraft delivery ZERO outbound F8-CRITICAL + S1403 F.C4 ContentEngagement docstring drift HIGH CONFIRMED at HEAD + S1502 §14.3 SignalCluster pattern_type consumer-side gap 6-arc COMPLETED.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.3 canonical summary template + §11.3 §10 meta-methodology template — non-negotiable per Chris directive S1399).
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`.
- **ARCHITECTURE_INDEX v41:** `docs/research/ARCHITECTURE_INDEX.md` — S1606 §1.44 + line-6 preamble.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1600 line-6 preamble advance S1605 → S1606 (row remains In-progress until S1699 xx99 close).
- **Content pipeline topic doc:** `docs/topics/content-pipeline.md` — drift-labeled pattern-still-valid; drift candidates flagged in S1601-S1605 §14 + Cat F §14; **CROSS-ARC CORRECTION owed for auto_publish "daily 6 AM" claim at :176/:189.**
- **Narrative:** `docs/narratives/CONTENT_PIPELINE.md` — **CROSS-ARC CORRECTION owed for auto_publish "daily 6 AM" claim at :240.**
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1606 continues arc-numbering convention (S1600 arc-open + S1601 first + S1602 second + S1603 third + S1604 fourth + S1605 fifth + **S1606 sixth and LAST child** + S1699 xx99 canonical queued as LAST session).
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; S1606 doesn't touch narrative anchor; xx99 S1699 §7 anchor-update recommendations will name refresh candidates).
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1606 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`.
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold).
- Group 1400 post-arc §7 anchor-updates still pending (inherited from S1499).
- Group 1500 post-arc §7 anchor-updates still pending (inherited from S1599).
- Group 1500 T1 CRITICAL remediation queue still pending.
- **NEW 5 doc PRs owed** to remove "daily 6 AM" claim for `auto_publish_approved_blogs` from 5 doc sources — deferred to xx99 §7 anchor-updates.
- **D48 preemptive stability-probe gate 15th-arm CONFIRMED at S1606 close** — TEN-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606 CODIFICATION-READY-STRENGTHENED-FURTHER for playbook v3 §15.
- **Playbook v3 §11.1 template promotion status:** already TRIGGERED at S1599 close per §12.4 discriminative-value criterion. Group 1600 sixth application of Chris's Phase 0 methodology confirms pattern holds; xx99 S1699 close will finalize with §10 meta-methodology fourth-application signal.
