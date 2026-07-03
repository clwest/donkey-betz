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

## READ THIS SECOND — GROUP 1600 CLOSED AT S1699; WRAPPER PIN ROTATION OWED AT NEXT-SESSION-OPEN

The local wrapper at `tools/pa_local.sh` hardcodes the token + conversation. **Active arc pin state after S1699 close:**

- **NO ACTIVE ARC PIN.** Group 1600 arc pin `pa-f52acf3f8d394faa` **RETIRED at S1699 close** via `session_tool.retire force=true` (currently-bound-thread refusal + explicit override per playbook §16 final-arc-close discipline; `updated_count: 30, retired: true`).
- **`tools/pa_local.sh:128` currently points at retired pin `pa-f52acf3f8d394faa`.** **Rotation to a fresh arc pin required BEFORE first PA dispatch on the new arc.**
- **Retired at S1699 close:** SIGN isolation pin `pa-846b6c4a532947c3` (Rigby `session_tool.retire`; `updated_count: 9, retired: true`).
- **Retired earlier at S1606 close:** SIGN isolation pin `pa-8cfafefb67864f83`.
- **Retired earlier at S1605-S1601 closes:** SIGN isolation pins `pa-b1b26f4f35474df8` + `pa-4ce64003711de4f1` + `pa-8af9063864bf4a7f` + `pa-1c5298d807d7a1d2` + `pa-9f075a024552b663`.
- **Retired earlier at S1599 close:** Group 1500 arc pin `pa-791b3db549a64e54`.
- **Retired earlier at S1499 close:** Group 1400 arc pin `pa-34d43795e1b24bd3` + SIGN isolation pin `pa-877f1919efaa48e4`.

**Wrapper pin rotation protocol at next-session-open:**
1. Chris ratifies next research group (default lean per playbook §22 = Chris-gated).
2. Mint fresh arc pin via Rigby `session_tool.create_fresh` from a temporary bootstrap conversation OR direct-invocation.
3. Update `tools/pa_local.sh:128` to new arc pin.
4. Verify `service_context: local` via `platform_config_tool overview` on new pin.

## READ THIS THIRD — GROUP 1600 CANONICAL SUMMARY LANDED (LAST SESSION UNDER GROUP 1600); NEXT RESEARCH GROUP CHRIS-GATED

Session 1699 shipped the **Group 1600 Content / Deliverables / Publishing canonical summary (P7 xx99)** at `docs/research/domains/content/1699_content_canonical_summary.md` (`status: active (SIGN-with-edits post-folds)`, `category: canonical_summary`, `session: 1699`, `child_slot: P7`, `domain_slug: content`, `research_group: 1600`, `authority: research`; 2017 lines; playbook §11.3 12-section template + §11.3 §10 meta-methodology template **fourth application** after S1399 first + S1499 second + S1599 third). **P7 xx99 canonical summary — Group 1600 CLOSED.**

**§5 four-axis Chris-gated posture-decision evidence brief consumes Cat F §20.6 verbatim** (Rigby SIGN Batch A Q1 fidelity 0.93):

- **§5.1 D65a** Deliverable canonicalization (integration vs island).
- **§5.2 D65b** PublishGate canonicalization (SelfBlog-only vs extend + composition contract).
- **§5.3 D65c** Lifecycle transition ownership (single canonical orchestrator vs per-rail; post-publish correction ABSENT CRITICAL).
- **§5.4 D65e** Rigby PA-tool surface unification + cross-boundary enforcement centralization (Cat E anchor LOCKED Candidate C per S1605 F9 + Cat F extends as HYPOTHESIS per §17.6 F5 fold).
- **§5.5** Seven-surface × four-axis cross-axis matrix (Cat F §20.6.5 verbatim).
- **§5.6** Consolidated Chris-gated selection tag summary (each axis: Chris-gated ADR post-arc picks).
- **§5.7** Five resolved cross-child contradictions.

**§8 follow-on queue:** T0/Gate + T1(20) + T2(26) + T3(5) + T4(5) + T5. T0/Gate R.CONTENT.XX99-ADR-BUNDLE blocks 20 T1 items. T1 #1 R.CONTENT.RAG-SCOPE = Cat A riskiest overall per S1601 F4.

**§10 fourth-application meta-methodology** confirms F.i/F.ii/F.iii methodology durable at third-application; F6 fold third-application tightening satisfied via F3 P3↔P4 swap decision-discriminative counterfactual + F1 Cat F self-caught grep 0-hit disconfirming evidence. **§10.2** codify-ready candidates for playbook v3: D48 (15-arc pattern + 11-consecutive-fully-clean sub-pattern) + D62 (6-of-6 sequence completed) + F2-fold rubric second-application + F1 during-SIGN grep-verification + cross-arc CORRECTION propagation + F9 binary posture framing + F10 dependency-clauses.

**Rigby SIGN cycle 1 SIGN-with-edits at 0.80 overall confidence (Batch A 0.88 + Batch B 0.82 + Batch C 0.80)** on fresh isolation pin `pa-846b6c4a532947c3` (retired at S1699 close). **F1-F4 folds landed pre-commit:**

- **F1** — §7.4 5-source doc-PR list REPLACED with S1605 F1 verbatim 5 sources (celery-workers.md:163 + content-pipeline.md:176/189 + narratives/CONTENT_PIPELINE.md:240 + S1604 §7.4 body + SESSION_1033_VALUE_CHAIN_COMPLETION.md:86).
- **F2** — §8.1 T1 restructured (R.CONTENT.XX99-ADR-BUNDLE moved from T1 #1 to T0/Gate; R.CONTENT.CROSS-DOMAIN-EMPLOYEE-ANALOG demoted from T1 to T3; T1 count 22 → 20; §8 renumbered §8.1-§8.6).
- **F3** — §3 domain shape Memory row tightened from "OUTPUT-PARTIAL" to "INPUT STABLE; OUTPUT ABSENT (except PA-tool feedback bridge PARTIAL)" per Cat F §9.4 verbatim.
- **F4** — §4.5 + §4.6 labeled "2-child cross-cutting pattern (narrow recurrence)".

**D48 preemptive stability-probe gate 16th arm HOLDING CLEAN — ELEVEN-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699 CONFIRMED per batch-processing criterion.** Codification-ready-STRENGTHENED-FURTHER for playbook v3 §15.

**Session close artifacts committed at S1699 close:**

```
docs/research/domains/content/1699_content_canonical_summary.md    [new; canonical summary; F1-F4 folds landed pre-commit; 2017 lines; LAST session under Group 1600]
docs/research/ARCHITECTURE_INDEX.md                                 [modified — v41 → v42; §1.45 registration + line-6 preamble bump]
docs/research/OPEN_ARCS.md                                          [modified — Group 1600 row MOVED from In-progress to Closed; line-6 preamble bump; In-progress marked "*(none)*"]
docs/handoffs/SESSION_1699_CONTENT_CANONICAL_SUMMARY.md             [new — S1699 handoff]
00-START-NEXT-SESSION.md                                             [modified — this file; Group 1600 CLOSED]
```

Handoff: `docs/handoffs/SESSION_1699_CONTENT_CANONICAL_SUMMARY.md`.

### NEXT-SESSION MISSION — CHRIS-GATED NEXT RESEARCH GROUP

**Chris-gated at session open per playbook §22 default queue lean.** Options include:

- **Group 1700** — next research group per §22 default queue lean (topic TBD; Chris ratifies at open).
- **Post-arc T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E** — Chris-gated posture-decision ADR bundle for D65a/D65b/D65c/D65e resolution (blocks 20 T1 items downstream).
- **T1 #1 R.CONTENT.RAG-SCOPE** — near-term T1 landing (Cat A riskiest overall per S1601 F4; workspace/cross-tenant scoping ratification cross-arc via Memory arc verification of Document workspace FK).
- **5 doc PRs for auto_publish "daily 6 AM" cross-arc CORRECTION** — per §7.4 (5 specific target files including handoff/topic/narrative sources).
- **Post-arc Chris-gated cross-arc handoffs:** Group 1500 T1.h SportsBettingBrief consumer-or-remove + Group 1400 R.B1 OutreachDraft delivery ADR (posture-tied to D65a).

Session flow at next-session open:

1. `context-kit orient` (session-open protocol per memory rule).
2. Chris ratifies next research group / next T1 landing.
3. If new research group: mint fresh arc pin via Rigby `session_tool.create_fresh`; update `tools/pa_local.sh:128`.
4. Confirm `service_context: local` via `platform_config_tool overview` on new pin.
5. Check if S1699 artifact set merged to `main` between sessions.
6. If not yet merged: Chris merge + PR merge.
7. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
8. Chris ratifies next mission per session-open protocol.

**Not next (unless Chris specifies):** any specific implementation work per playbook §14.5 no-implementation rule. Posture selection is Chris-gated post-arc ADR per D65a/D65b/D65c/D65e.

### Post-arc queued items (Chris-gated)

- **T0/Gate:** R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E — four-axis posture-decision ADR bundle.
- **T1 (20 items):** RAG-SCOPE + citation integrity + force-bypass + Cat B truncation/spawn/outbound + Variant categorization + canonical creation + triple-gate composition + PublishGate scope + post-publish correction + Newsletter live-send + OutreachDraft delivery + Rigby tool surface + auto-publish beat + workspace silent-degrade + Cat F origin outbound-delivery + unified auth + unified event stream + learning-loop bridge.
- **T3 (Cat F §19.3):** CROSS-DOMAIN-EMPLOYEE-ANALOG demoted per F9 fold severity mismatch.
- **Cross-arc:** Group 1500 T1.h SportsBettingBrief consumer-or-remove ADR re-scope + Group 1400 R.B1 OutreachDraft delivery ADR re-scope.
- **Group 1400 + Group 1500 + Group 1300 post-arc §7 anchor-updates + T1 CRITICAL remediation queues** still pending (inherited).

**FIRST THING next session open:**
1. `context-kit orient`
2. Chris ratifies next research group / next T1 landing
3. If new research group: mint fresh arc pin + rotate `tools/pa_local.sh:128`
4. Confirm `service_context: local` via `platform_config_tool overview`
5. Check if S1699 artifact set is on `main` between sessions
6. If not yet merged: Chris merge + PR merge
7. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
8. Execute next mission per Chris ratification

---

## PA / Rigby context

- **Arc pin at session start:** NONE (Group 1600 arc pin `pa-f52acf3f8d394faa` retired at S1699 close; new arc pin owed at next-session-open when Chris ratifies next research group). `tools/pa_local.sh:128` still points at retired pin — **rotation required before first PA dispatch.**
- **S1699 SIGN routing:** Full SIGN cycle 1 SIGN-with-edits at 0.80 confidence (Batch A 0.88 + B 0.82 + C 0.80) on fresh isolation pin `pa-846b6c4a532947c3` (retired at S1699 close via `session_tool.retire`; `updated_count: 9, retired: true`); F1-F4 folds landed pre-commit; 3-batch A/B/C SIGN pattern + Q3/Q5/Q9 cleanup turns per memory rule `feedback_rigby_sign_worker_instability_recovery.md`.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128; line 128 currently points at retired pin, rotation required at next-session open).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 16-arc CODIFICATION-READY-STRENGTHENED-FURTHER at S1699 close):** S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699 16-arc pattern confirmed. **ELEVEN-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699 CONFIRMED at S1699 close per batch-processing criterion.** D48 preemptive stability-probe gate 17th arm anticipated at next-session open on fresh arc pin. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.

## Repo state at next-session open

- **Branch state (at S1699 close, before merge):** `docs/session-1699-content-canonical-summary` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1699 handoff at `docs/handoffs/SESSION_1699_CONTENT_CANONICAL_SUMMARY.md`. Prior handoffs: SESSION_1606 (Content Cat F LAST child); SESSION_1605 → SESSION_1601 (Content Cat E/A/B/D/C children); SESSION_1600 (Content arc-open parent scoping); SESSION_1599 (Sports arc-close canonical summary); SESSION_1506 → SESSION_1500 (Sports arc); SESSION_1499 → SESSION_1400 (Revenue arc); SESSION_1399 (Memory Group 1300 canonical summary).
- **ARCHITECTURE_INDEX version:** v42 (bumped this session with §1.45 S1699 registration + line-6 preamble bump). Next bump at next-session artifact merge.
- **OPEN_ARCS state:** Group 1600 row MOVED from In-progress (marked "*(none)*") to Closed (before Group 1500 row per newer-at-top convention); Group 1500 remains in Closed; Group 1400 remains in Closed; Group 1300 remains in Closed.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Chris ratifies next research group / next T1 landing (Chris-gated at session open)
- [ ] If new research group: mint fresh arc pin via Rigby `session_tool.create_fresh` + rotate `tools/pa_local.sh:128`
- [ ] Confirm `service_context: local` via `platform_config_tool overview` on new pin
- [ ] Check if S1699 artifact set is on `main` — if yes, next session branches off `main`
- [ ] **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
- [ ] Execute next mission per Chris ratification

## Reference — where to look

- **S1699 canonical summary doc:** `docs/research/domains/content/1699_content_canonical_summary.md` — 12-section template + §11.3 §10 meta-methodology fourth application; §5 posture-decision brief consumes Cat F §20.6 verbatim; §8 T0/Gate + T1(20) + T2 + T3 + T4 + T5; §10 fourth-application meta-methodology with 7 codify-ready candidates.
- **S1606 audit doc:** `docs/research/domains/content/1606_content_cross_domain_integration_lens_audit.md` — Cat F LAST child audit; §20.6 LOAD-BEARING 4-axis × 7-surface posture-decision evidence plan.
- **S1605-S1601 audit docs:** Cat A/B/C/D/E child audits.
- **S1600 parent scoping doc:** `docs/research/domains/content/1600_content_domain_scoping.md`.
- **S1599 xx99 canonical summary (third application exemplar):** `docs/research/domains/sports/1599_sports_canonical_summary.md`.
- **S1499 xx99 canonical summary (second application exemplar):** `docs/research/domains/revenue/1499_revenue_canonical_summary.md`.
- **S1399 xx99 canonical summary (first application exemplar):** `docs/research/domains/memory/1399_memory_canonical_summary.md`.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.3 canonical summary template + §11.3 §10 meta-methodology template).
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`.
- **ARCHITECTURE_INDEX v42:** `docs/research/ARCHITECTURE_INDEX.md` — S1699 §1.45 + line-6 preamble.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1600 row moved to Closed section.
- **Content pipeline topic doc:** `docs/topics/content-pipeline.md` — drift-labeled pattern-still-valid; cross-arc CORRECTION owed for `auto_publish "daily 6 AM"` at :176/:189 per §7.4.
- **Narrative:** `docs/narratives/CONTENT_PIPELINE.md` — cross-arc CORRECTION owed for `auto_publish "daily 6 AM"` at :240 per §7.4.
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1699 closes Group 1600 numbering (S1600 arc-open + S1601-S1606 children + S1699 xx99); S1607-S1698 skipped by intent per arc-numbering discipline.
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; S1699 §7.2 defers narrative addition to Chris-gated ADR).
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1699 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`.
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold).
- Group 1400 + Group 1500 + Group 1300 post-arc §7 anchor-updates still pending (inherited).
- Group 1400 + Group 1500 T1 CRITICAL remediation queues still pending.
- **NEW 5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4 (celery-workers.md:163 + content-pipeline.md:176/189 + narratives/CONTENT_PIPELINE.md:240 + S1604 §7.4 body + SESSION_1033_VALUE_CHAIN_COMPLETION.md:86).
- **Wrapper pin rotation owed at `tools/pa_local.sh:128`** before next-session first PA dispatch (currently at retired pin `pa-f52acf3f8d394faa`).
- **D48 preemptive stability-probe gate 16th-arm CONFIRMED at S1699 close** — 11-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699 CODIFICATION-READY-STRENGTHENED-FURTHER for playbook v3 §15.
- **Playbook v3 §11.1 template promotion:** TRIGGERED at S1599 close per §12.4 discriminative-value criterion; Group 1600 fourth application confirms methodology durable; formal codification into v3 docs is a separate follow-up per Chris ratification.
