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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1604 close:**

- **ACTIVE ARC PIN:** `pa-f52acf3f8d394faa` (Group 1600 arc pin; minted at S1600 open via `session_tool.create_fresh`; **retained through P7 xx99 at S1699** per playbook §16 arc-continuity rule — carries Group 1600 context through S1605 Cat E + S1606 Cat F + S1699 xx99).
- **`tools/pa_local.sh:128` already at `pa-f52acf3f8d394faa`** — no line-128 rotation needed at S1605 open.
- **Retired at S1604 close:** SIGN isolation pin `pa-4ce64003711de4f1` (Rigby `session_tool.retire`).
- **Retired earlier at S1603 close:** SIGN isolation pin `pa-8af9063864bf4a7f`.
- **Retired earlier at S1602 close:** SIGN isolation pin `pa-1c5298d807d7a1d2`.
- **Retired earlier at S1601 close:** SIGN isolation pin `pa-9f075a024552b663`.
- **Retired earlier at S1599 close:** Group 1500 arc pin `pa-791b3db549a64e54`.
- **Retired earlier at S1506/S1505/S1504/S1503/S1502/S1501 closes:** SIGN isolation pins `pa-c2cdbd5c0b8c451b` / `pa-546de7ebe8c8b885` / `pa-af2bf7f2d1a0ef61` / `pa-8ce5f949bed5e093` / `pa-64c019d7e6685d31` / `pa-a39069230ab64450`.
- **Retired earlier at S1499 close:** Group 1400 arc pin `pa-34d43795e1b24bd3` + SIGN isolation pin `pa-877f1919efaa48e4`.
- **Retired earlier:** `pa-8660ea7cfecd4bc6` (S1406); `pa-4bdd5ad264674ce8` + `pa-637331c5f9574a10` (S1405); `pa-87ee24cd0d3947ce` (S1404); `pa-fba0c4c81fba4922` (S1403); `pa-4a0a28edcb7a45ec` (S1402); `pa-16d8b24d30e7a7d8` (S1401); `pa-aa54193f240f4846` + `pa-4fc3329d0db6484f` (S1399 Group 1300 arc-close).

Use `tools/pa_local.sh` for all chats — line 128 already pointing at active Group 1600 arc pin.

## READ THIS SECOND — S1604 GROUP 1600 CAT C LANDED; S1605 CAT E QUEUED NEXT

Session 1604 shipped the **Group 1600 Cat C PublishGate + Publish Rails child audit** at `docs/research/domains/content/1604_content_publish_gate_publish_rails_audit.md` (`status: active`, `category: child_audit`, `session: 1604`, `child_slot: P4`, `domain_slug: content`, `research_group: 1600`, `authority: research`; playbook §11.2 20-section template + six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 22 pre-Explore + 6 post-Explore + 4 SIGN-fold sub-verifier load-bearing binary claims all grep-verified against HEAD `20c75efd`). Applies parent D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront at §4.8 + §5.6 + §6.5 + §8.5 per parent D68 F8/F10 folds — **fourth sibling of Group 1600 to propagate the pattern upfront** after S1601 first + S1602 second + S1603 third.

**Parent §3 C boundary question answered:** *"what happens at the boundary?"* — gates, thresholds, eligibility, publish destinations, rails, failure modes, post-publish correction loops.

- **D65b HEADLINE evidence:** PublishGate is **SelfBlog-only at HEAD**. Verified via `publish_gate.py:279/:632/:641` SelfBlog imports + zero variant model imports; publish-gate-scope posture at code layer = SelfBlog-only + narrow (island posture).
- **D65c HEADLINE evidence:** post-publish correction loops **STRUCTURALLY ABSENT**. 0 grep hits for errata/retract/unpublish/revoke.publish/delete_broadcast/discord.edit_message in Cat C surfaces; SelfBlog STATUS_CHOICES has no retracted value; Discord fire-and-forget; **CRITICAL structural gap T.15.C1.**
- **F2 fold — 4-actor enforcement-authority contract codified at §1.5** (first-class boundary rule): PublishGate = advisory + REST endpoint = enforcement + force=true = admin bypass + auto_publish beat = fourth-actor bypass.
- **Triple-gate composition contract MISSING (S1603 T.15.6 inherited) — Cat C RESOLUTION-SIDE 4-CANDIDATE FRAMEWORK at §17.4** for xx99 D65b B4 consumption. Cat C does NOT select posture per playbook §14.5.
- **F7 fold — Newsletter reframe as CONTENT-GENERATION rail NOT PUBLISH rail** (dry_run since S1222 P6 >4mo; 0 SendGrid/mailgun/postmark hits; extends S1402 F.B1 pattern class F8-CRITICAL).
- **F1 fold — SelfBlog-block-specific evidence-precision:** SelfBlog class body :20611-20790 has 27 fields; NONE contain `metadata`; `_check_envelope` DEAD CODE for SelfBlog.

**Rigby SIGN cycle 1 SIGN-with-edits at High confidence** (Batch A High + Batch B Medium-High + Batch C High) → **SIGN-clean-post-folds at High confidence** on fresh isolation pin `pa-4ce64003711de4f1` (retired at S1604 close via `session_tool.retire`). **F1-F14 folds landed pre-commit:**

- **F1** §4.2.2 SelfBlog-block-specific evidence-precision tightening.
- **F2** §1.5 enforcement-authority first-class boundary contract (4-actor).
- **F3** §3.10a `publish_ready` writer callout (canonical + redundant).
- **F4** §3.10b gate-evaluation trigger + failure modes 5-trigger table.
- **F5** §5.3.1 proven-negative Discord wiring 4-actor sweep table.
- **F6** §7.4 auto_publish_approved_blogs body precision (in-model save + no shared helper + no AutoPublishEvent + log-line-only audit trail).
- **F7** §5.4 Newsletter reframe as content-generation-rail NOT publish-rail.
- **F8** §4.5 zero-events extended verification against generic-name patterns.
- **F9** §14 drift-vs-debt clarification.
- **F10** §20.3a first-class anchor "publishing is DB state transition with no guaranteed outbound side-effects."
- **F11** R.CONTENT.EXHAUSTIVE-PUBLISH-MUTATIONS-SWEEP promoted to §7 anchor recommendation + §19 T2.
- **F12** §15 CRITICAL-vs-HIGH severity rubric preamble.
- **F13** §19 T2 R.CONTENT.PUBLISHGATE-CALIBRATION-INVESTIGATION concrete corpus action.
- **F14** §7.4 evaluate_unscored_blogs first-pass-only clarification.

**D48 preemptive stability-probe gate 13th-arm outcome:** Batches A/B/C substantive on fresh isolation pin + final-verdict single-question follow-up clean. **Eight-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604 CONFIRMED** — extends 12-arc pattern to 13-arc + S1604. Codification-ready-STRENGTHENED-FURTHER for playbook v3 §15 with 8-consecutive-fully-clean sub-pattern.

**Session close artifacts committed at S1604 close:**

```
docs/research/domains/content/1604_content_publish_gate_publish_rails_audit.md   [new; child audit; F1-F14 folds landed pre-commit]
docs/research/ARCHITECTURE_INDEX.md                                              [modified — v38 → v39; §1.42 registration + §8 timeline S1604 row + v39 preamble]
docs/research/OPEN_ARCS.md                                                       [modified — Group 1600 row current-child S1603 → S1604 + S1603/S1604 landed sub-markers + frontmatter S1604 close preamble]
docs/handoffs/SESSION_1604_CONTENT_CAT_C_AUDIT.md                                [new — S1604 handoff]
00-START-NEXT-SESSION.md                                                         [modified — this file]
```

Handoff: `docs/handoffs/SESSION_1604_CONTENT_CAT_C_AUDIT.md`.

### NEXT-SESSION MISSION — S1605 CAT E RIGBY-FACING CONTENT PA TOOLING + APPROVAL UX

**Recommended path:** `Continue research group 1605` (short command per playbook §21).

Fifth child under Group 1600. Per D66 P5 slot: S1605 Cat E owns **Rigby PA-tool interface + operator approval UX** — the tool-surface contract for content-side operations.

**Cat E scope (per parent §3 E):** `deliverable_tool` PA schema at `core/services/pa_tool_schemas.py:3389-3460` + handler `_handle_deliverable_direct` at `core/services/td_handlers_content.py:84` (18 supported actions) → `content_tool` + `blog_tool` Session 1077 split (`_handle_content_review` at :235; `_handle_blog_direct` at :162) → `newsletter_tool` schema at `pa_tool_schemas.py:3498-3550` (prepare/outline/validate/metrics/list_issues/config/sources) → frontend approval UX at `frontend/src/pages/BlogViewerPage.tsx:45` (approve/publish mutations via `blogsApi.ts:3921-3962`).

**Boundary rule per parent F8 fold:** Cat E owns *how Rigby + Chris interact with the content pipeline via PA-tool actions + frontend approval mutations*. Cat E does NOT own the underlying object model (Cat D), gate semantics (Cat C), or reviewer verdicts (Cat B).

**Load-bearing inheritance from Cat C S1604 (§20.4 cross-arc handoffs):**

- **CONSUME:** `force=true` bypass audit trail T.15.C6 MEDIUM — Cat E owns tool-surface contract for `force=true` invocation logging + admin surface.
- **CONSUME:** auto_publish_approved_blogs beat audit trail D.14.C5 MEDIUM — Cat E owns admin visibility into auto-publish events.
- **CONSUME:** Rigby PA-tool contract on publish-rail actions — Cat E owns final tool-side fix for `content_tool.content_complete` alias (S1603 memory rule `feedback_deliverable_status_via_content_complete.md`).
- **CONSUME:** frontend auth contract T.15.C14 MEDIUM — Cat E owns REST endpoint role/permission verification + BlogViewerPage auth flow.
- **CONSUME:** `deliverable_tool.set_status` publish-rail relevance — S1603 memory rule `feedback_deliverable_create_defaults_to_completed.md` — Cat E owns tool-schema fix.
- **CONSUME as UNK-1 (S1601 riskiest overall):** Document workspace FK schema RAG-SCOPE cross-tenant risk — Cat E owns tool-surface investigation for RAG boundaries.

**Alternative near-term (Chris-gated pre-S1605):** T1 R.CONTENT.RAG-SCOPE cross-arc verification via Memory arc — resolves S1601 riskiest overall finding pre-S1605 if Chris prioritizes closing the riskiest overall finding first before continuing the D66 sequence.

Session flow at S1605 open:

1. `context-kit orient` (session-open protocol per memory rule).
2. Confirm `service_context: local` via `platform_config_tool overview` on arc pin `pa-f52acf3f8d394faa`.
3. Check if S1604 artifact set merged to `main` between sessions.
4. If not yet merged: Chris merge + PR merge.
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
6. Chris ratifies P5 kickoff via `Continue research group 1605` (S1605 default lean).
7. Draft S1605 audit at `docs/research/domains/content/1605_content_rigby_pa_tooling_approval_ux_audit.md` per playbook §11.2 20-section template + six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on load-bearing pre-Explore claims + D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront per parent D68 F8/F10 folds adopted.
8. Route to Rigby per §15 stage table — Full SIGN + fresh SIGN isolation pin per §15; **D48 preemptive stability-probe gate 14th arm** (if held-clean → nine-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605 anticipated).
9. Fold SIGN-with-edits into S1605 doc.
10. Session close: handoff + PR + docs cascade.

**Not next:** any specific implementation work per playbook §14.5 no-implementation rule. Posture selection is Chris-gated post-arc ADR per D65a/D65b/D65c.

**Also queued at future sessions:**

- **S1606 Cat F Cross-Domain Integration Lens & Posture Decision Framing** child audit (LAST — consumes P1-P5 evidence + produces xx99 §5 D65a/D65b/D65c three-axis posture-decision evidence plan).
- **S1699 xx99 canonical summary** (**fourth application** of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second + S1599 third).
- **Post-arc Chris-gated ADRs (T1 owed):** R.CONTENT.RAG-SCOPE (S1601 riskiest overall) + R.CONTENT.CITATION-INTEGRITY (S1602 CONFIRMED HIGH) + R.CONTENT.CAT-B-TRUNCATION (S1602 NEW HIGH) + R.CONTENT.CAT-B-SPAWN-TASKS (S1602 NEW HIGH latent-landmine) + R.CONTENT.CAT-B-OUTBOUND (S1602 NEW HIGH extends S1402 F.B1) + R.CONTENT.VARIANT-CATEGORIZATION-CLARIFICATION (S1603 F12 T1) + R.CONTENT.CANONICAL-CREATION-CONTRACT (S1603 F13 T1) + R.CONTENT.OUTREACHDRAFT-DELIVERY (S1603 F14 T1 F8-CRITICAL) + R.CONTENT.TRIPLE-GATE-COMPOSITION-CONTRACT (S1603 F11 → S1604 Cat C RESOLUTION-SIDE 4-candidate framework at §17.4) + **R.CONTENT.PUBLISHGATE-SCOPE-CANONICALIZATION** (S1604 NEW T1 D65b B1) + **R.CONTENT.POST-PUBLISH-CORRECTION-LOOPS** (S1604 NEW T1 CRITICAL D65c C2) + **R.CONTENT.NEWSLETTER-LIVE-SEND-PATH** (S1604 NEW T1 CRITICAL D65c C1 extends S1402 F.B1 pattern class) + R.CONTENT.VARIANT-CANONICALIZATION + R.CONTENT.DELIVERABLE-FACTORY-VARIANT-EXTENSION + R.CONTENT.POSTURE (three-axis D65a/D65b/D65c integration-vs-island posture selection — consumes xx99 §5 verbatim) + cross-arc re-scope decisions on Group 1500 T1.h SportsBettingBrief consumer-or-remove + Group 1400 R.B1 OutreachDraft delivery ADR.

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1604 artifact set is on `main` between sessions
4. If not yet merged: Chris merge + PR merge
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
6. Chris ratifies P5 S1605 kickoff (S1605 default lean per parent §5 sequence) — OR chooses alternative near-term T1 R.CONTENT.RAG-SCOPE cross-arc verification
7. Execute S1605 Cat E audit per playbook §11.2 20-section template + 6-parallel-Explore sweep + D62 = (a) 6-sibling exemplar mini-schema propagation-upfront per D68 F8/F10 folds

---

## PA / Rigby context

- **Arc pin at session start:** `pa-f52acf3f8d394faa` (Group 1600 arc pin; already active in `tools/pa_local.sh:128`; retained through P7 xx99 at S1699 per playbook §16 arc-continuity rule).
- **S1604 SIGN routing:** Full SIGN cycle 1 SIGN-with-edits at High confidence (Batch A High + Batch B Medium-High + Batch C High) → **SIGN-clean-post-folds at High confidence** on fresh isolation pin `pa-4ce64003711de4f1` (retired at S1604 close); F1-F14 folds landed pre-commit; 3-batch SIGN pattern + 1 final-verdict single-question follow-up per memory rule `feedback_rigby_sign_worker_instability_recovery.md`. Full SIGN Q1-Q9 pressure-test owed at each subsequent child audit + S1699 xx99.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 13-arc CODIFICATION-READY-STRENGTHENED-FURTHER at S1604 close):** S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604 13-arc pattern confirmed. **Eight-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604 CONFIRMED at S1604 close.** D48 preemptive stability-probe gate 14th arm anticipated at S1605 open; nine-consecutive-fully-clean-arms sub-pattern anticipated if held clean. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.

## Repo state at next-session open

- **Branch state (at S1604 close, before merge):** `docs/session-1604-content-cat-c-audit` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1604 handoff at `docs/handoffs/SESSION_1604_CONTENT_CAT_C_AUDIT.md`. Prior handoffs: SESSION_1603 (Content Cat D); SESSION_1602 (Content Cat B); SESSION_1601 (Content Cat A); SESSION_1600 (Content arc-open parent scoping); SESSION_1599 (Sports arc-close canonical summary); SESSION_1506 (Sports Cat F); SESSION_1505 (Sports Cat E); SESSION_1504 (Sports Cat D); SESSION_1503 (Sports Cat C); SESSION_1502 (Sports Cat B); SESSION_1501 (Sports Cat A); SESSION_1500 (Sports arc open); SESSION_1499 (Revenue arc-close); SESSION_1406 → SESSION_1400 (Revenue arc); SESSION_1399 (Group 1300 canonical summary).
- **ARCHITECTURE_INDEX version:** v39 (bumped this session with §1.42 S1604 registration + §8 timeline S1604 row + v39 preamble). Next bump at S1605 Cat E close.
- **OPEN_ARCS state:** Group 1600 row current-child advanced S1603 → S1604 this commit. Group 1500 remains in Closed section. Group 1400 remains in Closed section. Group 1300 remains in Closed section.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1604 artifact set is on `main` — if yes, next session branches off `main`
- [ ] Run post-merge 4-step docs cascade + `build_docs_provenance` if not yet run per `feedback_docs_cascade_at_every_close.md`
- [ ] Chris ratifies P5 kickoff: default lean is `Continue research group 1605` (S1605 Cat E; **fifth child audit under Group 1600**) OR alternative T1 R.CONTENT.RAG-SCOPE cross-arc verification
- [ ] Execute S1605 Cat E audit per playbook §11.2 20-section template + 6-parallel-Explore sweep + D62 = (a) 6-sibling exemplar mini-schema propagation-upfront per D68 F8/F10 folds
- [ ] **Apply Cat E boundary rule per F8 fold:** Cat E owns *how Rigby + Chris interact with the content pipeline via PA-tool actions + frontend approval mutations*; Cat E does NOT own the underlying object model (Cat D), gate semantics (Cat C), or reviewer verdicts (Cat B).
- [ ] **CONSUME as D65-analog evidence:** S1604 T.15.C6 force=true audit trail + D.14.C5 auto-publish audit trail + T.15.C14 frontend auth contract + Rigby memory rules 4 items.
- [ ] Route S1605 to Rigby per playbook §15 with D48 preemptive stability-probe gate (14th arm; if held-clean → nine-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605)
- [ ] Handoff SESSION_1605 + PR + docs cascade

## Reference — where to look

- **S1604 audit doc:** `docs/research/domains/content/1604_content_publish_gate_publish_rails_audit.md` — Cat C child audit; playbook §11.2 20-section template + D62 4-item mini-schema at §4.8/§5.6/§6.5/§8.5; §1.5 4-actor enforcement-authority contract; §14 Known Drift matrix (8 items); §15 Known Technical Debt matrix (15 items — 2 CRITICAL + 5 HIGH + 7 MED + 2 LOW); §16 Boundary Violations with §16.1 CRITICAL post-publish-correction gap; §17 Duplicate/Overlapping systems including §17.4 4-candidate resolution framework for T.15.6 triple-gate composition contract MISSING; §19 Recommended Future Research with 5 T1 items; §20.3a xx99 anchor recommendations + §20.4 cross-arc handoffs + §20.5 Rigby SIGN fold notes (F1-F14 detailed).
- **S1603 audit doc:** `docs/research/domains/content/1603_content_deliverable_base_variants_audit.md` — Cat D sibling; §14.3 triple-gate composition contract MISSING + §16.2 factory bypasses + §16.3 Cat A pipeline bypasses fully consumed by S1604 (§17.4 4-candidate resolution framework Cat C-side owned).
- **S1602 audit doc:** `docs/research/domains/content/1602_content_reviewers_decision_enforcement_audit.md` — Cat B sibling; §14/§15/§16.1 handoffs fully consumed by S1604 §16.5 DecisionEnforcer PUBLISH mandate.
- **S1601 audit doc:** `docs/research/domains/content/1601_content_claims_pack_deliberation_pipeline_v2_audit.md` — Cat A sibling; §9.1 SelfBlog.objects.create bypass fully consumed by S1604 §7.1 flow trace + §16.4 boundary evidence.
- **S1600 parent scoping doc:** `docs/research/domains/content/1600_content_domain_scoping.md` — Cat E boundary F8 fold + §3 E scope + Cat E canonical decision (D-analog); D66 mission sequence at §5 (P5 slot).
- **S1599 xx99 canonical summary:** `docs/research/domains/sports/1599_sports_canonical_summary.md` — playbook v3 §11.1 template promotion TRIGGERED per §12.4.
- **S1500 parent scoping doc:** `docs/research/domains/sports/1500_sports_domain_scoping.md` — D56-D61 precedent.
- **S1400 parent scoping doc:** `docs/research/domains/revenue/1400_revenue_domain_scoping.md` — first application of Chris's Phase 0 methodology.
- **S1499 revenue canonical summary:** `docs/research/domains/revenue/1499_revenue_canonical_summary.md`.
- **S1399 memory canonical summary:** `docs/research/domains/memory/1399_memory_canonical_summary.md` — first xx99 canonical summary.
- **Cross-arc handoffs owed to Group 1600:** S1504 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN CRITICAL + S1504 §5.1 SportsContentContextBuilder HOT-PATH-CHOKE-BYPASS HIGH + S1402 F.B1 Revenue OutreachDraft delivery ZERO outbound channel HIGH F8-upgraded to CRITICAL by S1603 (Cat C confirms extends to newsletter S1604 T.15.C2 CRITICAL) + S1403 F.C4 ContentEngagement docstring drift HIGH CONFIRMED at HEAD (Cat C confirms no learning loop S1604 T.15.C8 HIGH) + S1502 §14.3 SignalCluster pattern_type consumer-side gap 6-arc COMPLETED (S1602 §9.3 CONFIRMED extension to Cat B; S1604 §9.7 confirms Cat C also consume-only, no emit) + S1499 D55 (ii) Revenue Employee + Income/Jobs Employee JobContract split precedent + S1500 D59 posture-decision framing precedent (D65-analog) + S1274 §12.3 P1 Product/Architecture Decision Point precedent.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v39:** `docs/research/ARCHITECTURE_INDEX.md` — S1604 §1.42 + §8 timeline S1604 row + v39 preamble.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1600 row current-child S1603 → S1604 this commit + S1603/S1604 landed sub-markers.
- **Content pipeline topic doc:** `docs/topics/content-pipeline.md` — Session 1147 topic doc; drift-labeled pattern-still-valid; drift candidates flagged in S1601 + S1602 + S1603 + S1604 §14 for post-xx99 validator rig-up.
- **Prior audit:** `docs/audit-2026/04-content-pipeline.md` — April 2026 audit (referenced in S1601 §11.3 + S1602 §11.2 + S1603 §11 + S1604 §11.4; §10 novelty/structure calibration OPEN truth gap inherited as S1604 T2 R.CONTENT.PUBLISHGATE-CALIBRATION-INVESTIGATION with F13 concrete corpus action).
- **Patents:** `docs/patents/DISCLOSURE_D_CLAIMS_BASED_DELIBERATION.md` (ClaimsPack architecture provenance) + `docs/patents/DISCLOSURE_E_PUBLISH_GATE_FINISHING_LOOP.md` (PublishGate provenance — S1604 §11.6 confirms accurate at HEAD; SelfBlog-centric model assumption verified) + `docs/patents/DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md` (Cat B-primary DecisionEnforcer provenance; §5 Layer 2 operational claim at :140 invalidated by S1602 §15.3).
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1604 continues arc-numbering convention (S1300 arc-open + S1301-S1305 children + S1399 canonical; S1400 arc-open + S1401-S1406 children + S1499 canonical; S1500 arc-open + S1501-S1506 children + S1599 canonical; **S1600 arc-open + S1601 first child + S1602 second child + S1603 third child + S1604 fourth child** + S1605-S1606 children + S1699 canonical queued).
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; S1604 doesn't touch narrative anchor; xx99 S1699 §7 anchor-update recommendations will name refresh candidates).
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1604 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`.
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold).
- Group 1400 post-arc §7 anchor-updates still pending (inherited from S1499).
- Group 1500 post-arc §7 anchor-updates still pending (inherited from S1599).
- Group 1500 T1 CRITICAL remediation queue still pending (R.C1 verify_betting_outcomes beat-restoration; R.D1 daily_betting_digest beat-restoration OR §12 deferred-list; R.D3 zero-test-coverage; R.D4 SportsBettingBrief consumer-or-remove; R.D5 two-writer dedup — inherited from S1599).
- **Cross-arc re-scope owed (updated by S1604):** Group 1500 T1.h R.D4 SportsBettingBrief consumer-or-remove disposition may be re-scoped by Group 1600 D65b posture selection at S1699 close (S1604 §9.3 SportsBettingBrief publish rail MISSING CONFIRMED at HEAD; T.15.C3 HIGH); Group 1400 R.B1 OutreachDraft delivery ADR: same pattern class extends to Newsletter (S1604 §9.2 + §5.4 F7 reframe; T.15.C2 CRITICAL).
- **D48 preemptive stability-probe gate 13th-arm CONFIRMED at S1604 close** — eight-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604 CODIFICATION-READY-STRENGTHENED-FURTHER for playbook v3 §15.
- **Playbook v3 §11.1 template promotion status:** already TRIGGERED at S1599 close per §12.4 discriminative-value criterion. Group 1600 fourth application of Chris's Phase 0 methodology confirms whether pattern holds at S1699 xx99 close via §12.4 F6-fold-tightened criterion.
