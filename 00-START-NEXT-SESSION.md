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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1600 open:**

- **ACTIVE ARC PIN:** `pa-f52acf3f8d394faa` (Group 1600 arc pin; minted at S1600 open via `session_tool.create_fresh`; retained per playbook §16 through P7 xx99 at S1699).
- **`tools/pa_local.sh:128` already at `pa-f52acf3f8d394faa`** — no line-128 rotation needed at S1601 open.
- **Retired at S1599 close:** Group 1500 arc pin `pa-791b3db549a64e54` (retained through S1500 → S1501 → S1502 → S1503 → S1504 → S1505 → S1506 → S1599 per playbook §16 arc-continuity rule; retired at arc-close via `session_tool.retire`).
- **Retired earlier at S1506 close:** SIGN isolation pin `pa-c2cdbd5c0b8c451b`.
- **Retired earlier at S1505 close:** SIGN isolation pin `pa-546de7ebe8c8b885`.
- **Retired earlier at S1504 close:** SIGN isolation pin `pa-af2bf7f2d1a0ef61`.
- **Retired earlier at S1503 close:** SIGN isolation pin `pa-8ce5f949bed5e093`.
- **Retired earlier at S1502 close:** SIGN isolation pin `pa-64c019d7e6685d31`.
- **Retired earlier at S1501 close:** SIGN isolation pin `pa-a39069230ab64450`.
- **Retired earlier at S1499 close:** Group 1400 arc pin `pa-34d43795e1b24bd3` + SIGN isolation pin `pa-877f1919efaa48e4`.
- **Retired earlier:** `pa-8660ea7cfecd4bc6` (S1406); `pa-4bdd5ad264674ce8` + `pa-637331c5f9574a10` (S1405); `pa-87ee24cd0d3947ce` (S1404); `pa-fba0c4c81fba4922` (S1403); `pa-4a0a28edcb7a45ec` (S1402); `pa-16d8b24d30e7a7d8` (S1401); `pa-aa54193f240f4846` + `pa-4fc3329d0db6484f` (S1399 Group 1300 arc-close).

Use `tools/pa_local.sh` for all chats — line 128 already pointing at active Group 1600 arc pin.

## READ THIS SECOND — S1600 GROUP 1600 CONTENT ARC OPENED; S1601 CAT A QUEUED NEXT

Session 1600 shipped the **Group 1600 Content / Deliverables / Publishing arc-open parent scoping doc** at `docs/research/domains/content/1600_content_domain_scoping.md` (1,502 lines; `status: active`, `category: parent_scoping`, `session: 1600`, `domain_slug: content`, `research_group: 1600`, `authority: parent-doc`; playbook §11.1 parent scoping template applied verbatim + Chris's Phase 0 F.i/F.ii/F.iii methodology **third application** at §10/§11/§12 per D68 UNCHANGED — playbook v3 §11.1 template promotion **already TRIGGERED at S1599 close** per §12.4 discriminative-value criterion 4-of-4 evidence types satisfied; Group 1600 confirms whether pattern holds at third application via §12.4 F6-fold-tightened criterion at S1699 close).

**8 Chris decisions D63-D68 ratified via single "agree all + D-6=(a)" round** — governance decision `2c469638-643d-4477-a8ea-1766b552eebe` `acted`:

- **D63** slug = `content`
- **D64** parent-with-children (P1-P6 + P7 xx99 at S1699)
- **D65a** Deliverable canonicalization posture-decision framing (canonical container vs parallel-schema-siblings)
- **D65b** PublishGate canonicalization posture-decision framing (single canonical gate vs per-variant/channel)
- **D65c** Lifecycle transition ownership (factory/rails) posture-decision framing (canonical orchestrator vs variant-owned rails)
- **D66** child mission sequence per F3 Rigby fold P3↔P4 swap: **P1 Cat A → P2 Cat B → P3 Cat D (moved from P4) → P4 Cat C (moved from P3) → P5 Cat E → P6 Cat F → P7 xx99**
- **D67** §7 anti-scope 18 items (F5 fold 12→18)
- **D68** methodology unchanged per D58 + D62=(a) + F8/F10 folds adopted

**Rigby Light SIGN cycle 1 → cycle 2 SIGN-clean at High confidence** on fresh S1600 arc pin `pa-f52acf3f8d394faa`. **F1-F12 folds landed at commit-time** — F1 §3 Cat A ClaimsPack boundary rule; F2 §3 Cat C/D crisp boundary rules; F3 §5 P3↔P4 swap Cat D BEFORE Cat C; F4 §8 D65 split into D65a/D65b/D65c three orthogonal axes preventing agree-all masking; F5 §7 anti-scope 12→18 items; F6 §12.4 discriminative-value tightening with required decision-discriminative proof + required disconfirming evidence item; F7 §12.5 Deliverable Lifecycle Traceability Table 10→12 stages; F8 one-sentence boundary rule per category; F9 binary posture framing with mushy-hybrid disallowed; F10 D66 dependency-clause embedding; F11 §3 Cat E feedback-hazard note; F12 ClaimsPack centrality preserved via F1.

**Session close artifacts committed at S1600 close:**

```
docs/research/domains/content/1600_content_domain_scoping.md              [new; 1502 lines; parent Phase 0 scoping]
docs/research/ARCHITECTURE_INDEX.md                                       [modified — v34 → v35; §1.38 registration + §8 timeline S1600 row]
docs/research/OPEN_ARCS.md                                                [modified — Group 1600 Not-started → In-progress section]
docs/handoffs/SESSION_1600_CONTENT_ARC_OPEN.md                            [new — S1600 handoff]
tools/pa_local.sh                                                         [modified — line 128 rotated to pa-f52acf3f8d394faa]
00-START-NEXT-SESSION.md                                                  [modified — this file]
```

Handoff: `docs/handoffs/SESSION_1600_CONTENT_ARC_OPEN.md`.

### NEXT-SESSION MISSION — S1601 CAT A CLAIMSPACK + CONTENT DELIBERATION PIPELINE V2

**Recommended path:** `Continue research group 1601` (short command per playbook §21).

First child under Group 1600. Per D66 P1 slot: S1601 Cat A owns the pipeline canonical-decision on **"what claims + which sources ground the deliberation?"**. Downstream P2-P6 children + S1699 xx99 consume Cat A evidence baseline.

**Cat A scope (per parent §3):** ClaimsPackBuilder + ContentWriterAgent + ContentDeliberationRunner (v2 pipeline entry). **Boundary rule per F1 fold:** Cat A owns *claims/evidence assembly + deliberation mechanics* (pre-publication truth machinery). Cat A does NOT own publish gating or external publish actions (those belong to Cat C).

**Load-bearing questions for Cat A (per parent §3 A):**
- Does the ClaimsPack claim-ID scheme actually enforce citation end-to-end, or does the FactCheckReviewer catch uncited claims post-hoc as the only enforcement layer? (Citation integrity posture.)
- What runs in production today? v2 pipeline strictly on-demand via ConversationOrchestrator, or is there a beat entry that I'm missing? (v2 pipeline runtime posture.)

Session flow at S1601 open:

1. `context-kit orient` (session-open protocol per memory rule).
2. Confirm `service_context: local` via `platform_config_tool overview` on arc pin `pa-f52acf3f8d394faa`.
3. Check if S1600 artifact set merged to `main` between sessions.
4. If not yet merged: Chris merge + PR merge.
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
6. Chris ratifies P1 kickoff via `Continue research group 1601` (S1601 default lean).
7. Draft S1601 audit at `docs/research/domains/content/1601_content_claims_pack_deliberation_pipeline_v2_audit.md` per playbook §11.2 20-section template + six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 5+ load-bearing pre-Explore claims + **D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront** per D68 F8/F10 folds adopted.
8. Route to Rigby per §15 stage table — Full SIGN + potentially Light SIGN if scope permits; fresh SIGN isolation pin per §15; **D48 preemptive stability-probe gate 10th arm** (if held-clean → five-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601 anticipated).
9. Fold SIGN-with-edits into S1601 doc.
10. Session close: handoff + PR + docs cascade.

**Not next:** any specific implementation work per playbook §14.5 no-implementation rule. Posture selection is Chris-gated post-arc ADR per D65a/D65b/D65c.

**Also queued at future sessions:**

- S1602 Cat B Content Reviewers + Decision Enforcement child audit.
- **S1603 Cat D Deliverable Base + Specialized Variants** child audit (F3 fold: moved from P4→P3 because Cat C's gate/rails semantics consume Cat D's canonical object-model decision D65a-analog; HEADLINE child).
- **S1604 Cat C PublishGate + Publish Rails** child audit (F3 fold: moved from P3→P4 because gate semantics D65b-analog + lifecycle transition ownership D65c-analog are grounded in Cat D's canonical object-model outcome).
- S1605 Cat E Rigby-Facing Content PA Tooling + Approval UX child audit.
- S1606 Cat F Cross-Domain Integration Lens & Posture Decision Framing child audit (LAST — consumes P1-P5 evidence + produces xx99 §5 D65a/D65b/D65c-analog three-axis posture-decision evidence plan per parent §12.1 F.iii item 3).
- S1699 xx99 canonical summary (**fourth application** of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second + S1599 third).
- **Post-arc Chris-gated ADRs (T1 owed):** R.CONTENT.POSTURE (three-axis D65a/D65b/D65c integration-vs-island posture selection — consumes xx99 §5 verbatim) + cross-arc re-scope decisions on Group 1500 T1.h SportsBettingBrief consumer-or-remove + Group 1400 R.B1 OutreachDraft delivery ADR.
- **Playbook v3 §11.1 promotion session:** consumes S1699 §12.4 F6-fold-tightened criterion check + S1599 §10.2 6-candidate codify list (D48 gate + D62 6-sibling + F2-fold rubric + BEFORE-SIGN ORM probe conditional + S1504 verdict-text recovery + S1505 grep-verified confidence upgrade).

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1600 artifact set is on `main` between sessions
4. If not yet merged: Chris merge + PR merge
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
6. Chris ratifies P1 S1601 kickoff (S1601 default lean per parent §5 sequence)
7. Execute S1601 Cat A audit per playbook §11.2 20-section template + 6-parallel-Explore sweep + D62 = (a) 6-sibling exemplar mini-schema propagation-upfront per D68 F8/F10 folds

---

## PA / Rigby context

- **Arc pin at session start:** `pa-f52acf3f8d394faa` (Group 1600 arc pin; already active in `tools/pa_local.sh:128`; carries Group 1600 arc-open context through P1-P6 children + P7 xx99 per playbook §16 retain rule).
- **S1600 SIGN routing:** Light SIGN cycle 1 → cycle 2 SIGN-clean at High confidence on active arc pin (no fresh isolation pin used — matches S1500 Light-SIGN-on-arc-pin pattern for parent scoping doc); F1-F12 folds landed at commit-time. Full SIGN Q10-Q13 pressure-test owed at each subsequent child audit + S1699 xx99.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 9-arc CODIFICATION-READY at S1599 close):** S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506 9-arc pattern confirmed. Four-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506. D48 preemptive stability-probe gate 10th arm anticipated at S1601 Cat A open; five-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601 anticipated if held clean. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.

## Repo state at next-session open

- **Branch state (at S1600 close, before merge):** `docs/session-1600-content-arc-open` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1600 handoff at `docs/handoffs/SESSION_1600_CONTENT_ARC_OPEN.md`. Prior handoffs: SESSION_1599 (Sports arc-close canonical summary); SESSION_1506 (Sports Cat F); SESSION_1505 (Sports Cat E); SESSION_1504 (Sports Cat D); SESSION_1503 (Sports Cat C); SESSION_1502 (Sports Cat B); SESSION_1501 (Sports Cat A); SESSION_1500 (Sports arc open); SESSION_1499 (Revenue arc-close canonical summary); SESSION_1406 → SESSION_1400 (Revenue arc); SESSION_1399 (Group 1300 canonical summary — first xx99).
- **ARCHITECTURE_INDEX version:** v35 (bumped this session with §1.38 S1600 parent scoping + §8 timeline S1600 arc-open row + v35 preamble). Next bump at S1601 Cat A close.
- **OPEN_ARCS state:** Group 1600 row moved Not-started → In-progress this commit. Group 1500 remains in Closed section. Group 1400 remains in Closed section. Group 1300 remains in Closed section.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1600 artifact set is on `main` — if yes, next session branches off `main`
- [ ] Run post-merge 4-step docs cascade + `build_docs_provenance` if not yet run per `feedback_docs_cascade_at_every_close.md`
- [ ] Chris ratifies P1 kickoff: default lean is `Continue research group 1601` (S1601 Cat A; **first child audit under Group 1600**)
- [ ] Execute S1601 Cat A audit per playbook §11.2 20-section template + 6-parallel-Explore sweep + D62 = (a) 6-sibling exemplar mini-schema propagation-upfront per D68 F8/F10 folds
- [ ] **Apply Cat A boundary rule per F1 fold:** Cat A owns claims/evidence assembly + deliberation mechanics; Cat A does NOT own publish gating (Cat C) or object-model decisions (Cat D)
- [ ] Route S1601 to Rigby per playbook §15 with D48 preemptive stability-probe gate (10th arm; if held-clean → five-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601)
- [ ] Handoff SESSION_1601 + PR + docs cascade

## Reference — where to look

- **S1600 parent scoping doc:** `docs/research/domains/content/1600_content_domain_scoping.md` — 1502-line parent Phase 0 scoping; playbook §11.1 template + Chris's Phase 0 F.i/F.ii/F.iii methodology third application per D68 UNCHANGED; §3 candidate subdomain taxonomy A-F with F1-F12 folds landed; §5 D66 mission sequence with F3 P3↔P4 swap; §7 D67 anti-scope 18 items per F5 fold; §8 D63-D68 Chris-locked decisions; §10-§12 F.i/F.ii/F.iii third application; §12.4 F6-fold-tightened discriminative-value criterion; §12.5 F7-fold-expanded 12-stage Deliverable Lifecycle Traceability Table.
- **S1599 xx99 canonical summary:** `docs/research/domains/sports/1599_sports_canonical_summary.md` — 2241-line canonical summary; §12.4 discriminative-value criterion check 4-of-4 evidence types satisfied → playbook v3 §11.1 template promotion TRIGGERED.
- **S1500 parent scoping doc:** `docs/research/domains/sports/1500_sports_domain_scoping.md` — 1269-line parent scoping (D56-D61 precedent).
- **S1400 parent scoping doc:** `docs/research/domains/revenue/1400_revenue_domain_scoping.md` — first parent scoping doc application of Chris's Phase 0 methodology (D29 first-application precedent).
- **S1499 revenue canonical summary:** `docs/research/domains/revenue/1499_revenue_canonical_summary.md` — second §10 meta-methodology application precedent.
- **S1399 memory canonical summary:** `docs/research/domains/memory/1399_memory_canonical_summary.md` — first formal xx99 canonical summary; first §10 meta-methodology application.
- **Cross-arc handoffs owed to Group 1600:** S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN CRITICAL + S1504 §5.1 SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS HIGH + S1402 F.B1 Revenue OutreachDraft delivery ZERO outbound channel HIGH + S1403 F.C4 ContentEngagement docstring drift HIGH + S1502 §14.3 SignalCluster pattern_type consumer-side gap 6-arc COMPLETED + S1499 D55 (ii) Revenue Employee + Income/Jobs Employee JobContract split precedent + S1500 D59 posture-decision framing precedent (D65-analog) + S1274 §12.3 P1 Product/Architecture Decision Point precedent.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v35:** `docs/research/ARCHITECTURE_INDEX.md` — S1600 §1.38 + §8 timeline S1600 arc-open row + v35 preamble.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1600 In-progress section this commit.
- **Content pipeline topic doc:** `docs/topics/content-pipeline.md` — Session 1147 topic doc; drift-labeled pattern-still-valid but specific numbers may drift; xx99 §7 anchor-update recommendation refreshes.
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — parent scoping only; no runtime changes).
- Handoff numbering continuity — S1600 continues arc-numbering convention (S1300 arc-open + S1301-S1305 children + S1399 canonical; S1400 arc-open + S1401-S1406 children + S1499 canonical; S1500 arc-open + S1501-S1506 children + S1599 canonical; **S1600 arc-open** + S1601-S1606 children + S1699 canonical queued).
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; S1600 doesn't touch narrative anchor; xx99 (S1699) §7 anchor-update recommendations will name refresh candidates).
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1600 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`.
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold).
- Group 1400 post-arc §7 anchor-updates still pending (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499).
- Group 1500 post-arc §7 anchor-updates still pending (`PLATFORM_INVENTORY.md` §3.10 subdivision + DBAO subgroup conditional on T1.b R.DBAO.CODENAME verdict + `PLATFORM_WHAT_IT_IS.md` Sports narrative refresh + NEW `docs/topics/sports-betting.md` first-inventory landing per C2 cross-cutting gate + `.github/CODEOWNERS` 6 sports runtime files).
- **Group 1500 T1 CRITICAL remediation queue still pending (post-arc T1):** R.C1 verify_betting_outcomes beat-restoration ← R.C2 pre-restore-beat concurrency-safety hardening; R.D1 daily_betting_digest beat-restoration OR §12 deferred-list entry ← R.D2 idempotency hardening; R.D3 zero-test-coverage reliability multiplier; R.D4 SportsBettingBrief consumer-or-remove ← T1.a; R.D5 two-writer dedup.
- **Cross-arc re-scope owed:** Group 1500 T1.h R.D4 SportsBettingBrief consumer-or-remove disposition may be re-scoped by Group 1600 D65a-analog posture selection at S1699 close; Group 1400 R.B1 OutreachDraft delivery ADR may be re-scoped by Group 1600 D65a-analog posture selection.
- **D48 preemptive stability-probe gate 10th-arm anticipated at S1601 Cat A open** — five-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601 if held clean.
- **Playbook v3 §11.1 template promotion TRIGGERED at S1599 close** per §12.4 discriminative-value criterion. Group 1600 is third application; §12.4 F6-fold-tightened criterion at S1699 close confirms whether pattern holds at third application via required decision-discriminative proof + required disconfirming evidence item.
