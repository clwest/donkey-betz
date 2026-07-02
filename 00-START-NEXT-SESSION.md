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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1406 close:**

- **Active arc pin:** `pa-34d43795e1b24bd3` ("Session 1400 — Revenue research group (kickoff)"). Retained through S1401 + S1402 + S1403 + S1404 + S1405 + S1406 per D31/D33/D35/D37/D39/D42/D47; will carry S1499 xx99 canonical summary continuity to arc-close. **Retire at S1499 close** per playbook §16 arc-close discipline.
- **Recently retired at S1406 close (post-PR-merge):** `pa-8660ea7cfecd4bc6` (S1406 SIGN isolation pin — batches 1-3 substantive delivered; batch 4 blocked by worker instability recurrence; SIGN-with-edits cycle 1 accepted per D50).
- **Retired earlier at S1405 close:** `pa-4bdd5ad264674ce8` + `pa-637331c5f9574a10` (S1405 SIGN pins — worker instability blocked batches 2-3; deferred to S1406 fold per D45 then to S1499 per D51).
- **Retired earlier at S1404 close:** `pa-87ee24cd0d3947ce`.
- **Retired earlier at S1403 close:** `pa-fba0c4c81fba4922`.
- **Retired earlier at S1402 close:** `pa-4a0a28edcb7a45ec`.
- **Retired earlier at S1401 close:** `pa-16d8b24d30e7a7d8`.
- **Retired earlier at S1400 open:** `pa-aa54193f240f4846` (Group 1300 arc pin) + `pa-4fc3329d0db6484f` (S1399 SIGN pin).
- **Next SIGN pin:** mint fresh isolation pin per playbook §15 stage table for S1499 xx99 canonical summary Q10-Q13 SIGN.

Use `tools/pa_local.sh` for all chats unless you have a reason to override.

## READ THIS SECOND — GROUP 1400 6-CHILD ARC COMPLETE; S1499 XX99 CANONICAL SUMMARY IS ARC-CLOSE MISSION

Session 1406 shipped the sixth (and final) Group 1400 child audit at `docs/research/domains/revenue/1406_revenue_freelance_gig_income_jobs_audit.md` (Category F Freelance / Gig — Income-Jobs lane per D25 F.i Chris-lock; 20-section playbook §11.2 template; **Rigby SIGN-with-edits cycle 1 substantive** — batches 1-3 F.F1-F.F10 all pressure-tested with 0 severity FLIPS + 10 framing refinements + 2 severity upgrades folded at commit-time [F.F6 MUST-FIX + F.F9 HIGH]; batch 4 S1405 F.E4-F.E10 deferred addendum BLOCKED by worker-instability recurrence; **D51 Chris ratification** defers batch 4 to S1499 xx99 synthesis per D48 fallback [iii]). ARCHITECTURE_INDEX v24 → v25 bump landed same-commit (added §1.28 for S1406 child audit + §8 timeline S1406 row + frontmatter v25 preamble). No parent-doc anchor corrections at S1406 commit-time — parent §3.F + §12.1 Cat F + §11.4 all preserved as accurate.

**6-child Group 1400 arc COMPLETE.** S1400 arc-open + S1401 Cat A + S1402 Cat B + S1403 Cat C + S1404 Cat D + S1405 Cat E + S1406 Cat F all shipped. S1499 xx99 canonical summary is the arc-close mission.

**Load-bearing S1406 outputs to inherit at S1499 open:**

- **F.F1 CONFIRMED HIGH (arc-wide F.E2 extension, worse-than-E variant):** `core/tasks_ops.py:2239-2251` writes FreelanceOpportunity with 5 phantom fields UNGUARDED. Runtime FieldError guaranteed if triggered. WORSE than S1405 F.E2's hasattr-guarded 4 phantom fields.
- **F.F2 CONFIRMED HIGH (arc-wide F.E3 extension, multi-writer variant):** 20 files call `Opportunity.objects.create()`. `intelligence/spider_decision_bridge.py` dominant at 2630/2631 rows (99.96%). `income_spider_orchestrator.py:462` produces 0 rows via provenance stamp locally. No canonical write-authority contract. **S1499 T7 owns write-authority framework track.**
- **F.F3 CONFIRMED HIGH (completes F.E10 arc-wide synthesis, Cat F half):** Zero JobContract / AGENT_MAP / dedicated PA tool / dedicated queue for the 10-file Income/Jobs lane. Completes arc-wide ownership synthesis. **S1499 T6 owns Income/Jobs Employee JobContract ADR track (paired with S1405 T2 Revenue Employee).**
- **F.F6 MUST-FIX (arc-wide learning-loop-missing, Cat F leg; Rigby SIGN Batch 2 upgrade):** Rigby verdict: "north-star blocker; without outcomes cannot tune prompts, ranking, or ROI."
- **F.F9 HIGH (LLM max_tokens floor risk; UPGRADED via parent-Claude direct-verify):** `core/llm_enforcer.py:232` confirmed `downgrade_model = 'gpt-5-mini'` wired + downgrade log active at line 446-450. Silent-empty risk ACTIVE.
- **Full 10 F.F findings:** see S1406 audit §14 + handoff for F.F1-F.F10 complete list. Arc-wide 5-pillar convergence COMPLETE at Cat F level (S1499 owns unified remediation plan, not pattern-identification).

**Load-bearing methodology outputs of S1406 (inherit at S1499):**

- **Parent-Claude verifier-loop 12/12 checkpoints CONFIRM** (10 CONFIRM + 2 DISAMBIGUATION) — matches S1404 + S1405 12-checkpoint count. **New pattern: provenance-stamp ORM probe as disambiguation tool** — extends S1401-S1405 verifier-loop tool chain (file-line direct-reads, broader-grep, model-context disambiguation) with ORM-provenance disambiguation.
- **First application of S1405 D48 stability-probe gate WORKS.** Fresh SIGN pin first-turn generic-error triggered warmup-ping recovery pattern; Rigby responded substantively. Three batches delivered before Batch 4 hit worker instability. Verdict: stability-probe gate + warmup-ping pattern recover pins after first-turn generic-errors.
- **First library audit to complete arc-wide 5-pillar convergence at child-audit level** (rather than deferring pattern-identification to xx99). S1499 owns unified remediation plan (10 tracks T1-T10 = 5 from S1405 + 5 from S1406), not pattern-identification.
- **Rigby SIGN worker-instability confirmed as 2-session pattern (S1405 + S1406).** Recovery: warmup-ping + batched 3-4 findings per prompt + ultra-short titles-only. Memory rule `feedback_rigby_sign_worker_instability_recovery.md` triggered.

**Session close artifacts committed at S1406 close (this session):**

```
docs/research/domains/revenue/1406_revenue_freelance_gig_income_jobs_audit.md   [new; 1390 + ~50 fold-edit lines; sign_status: SIGN-with-edits cycle 1 substantive]
docs/research/ARCHITECTURE_INDEX.md                                             [modified — v24 → v25; §1.28 S1406 row + §8 timeline row + v25 preamble]
docs/research/OPEN_ARCS.md                                                      [modified — Group 1400 current-child field advanced; frontmatter last_updated bumped; reconciliation note added]
00-START-NEXT-SESSION.md                                                        [modified — this file]
docs/handoffs/SESSION_1406_REVENUE_FREELANCE_GIG_INCOME_JOBS.md                 [new — session handoff]
```

Handoff: `docs/handoffs/SESSION_1406_REVENUE_FREELANCE_GIG_INCOME_JOBS.md`.

### NEXT-SESSION MISSION — S1499 xx99 Group 1400 Revenue Canonical Summary (arc-close)

Per Group 1400 parent doc §5 mission sequence P7 slot + playbook §11.3 canonical summary template + Chris directive 2026-07-01 (playbook §11.3 §10 second application after S1399 close):

- **Session ID.** S1499.
- **Slot.** P7 (final Group 1400 session; arc-close per playbook §17 graduation criteria).
- **Category.** xx99 canonical summary (synthesizes P1-P6 outputs; resolves contradictions between siblings; produces §12.5 Revenue Lifecycle Traceability Table).
- **Branch.** `docs/session-1499-revenue-canonical-summary` off `main` post-S1406 merge.
- **Playbook §11.3 template.** Full 12-section canonical summary:
  1. Executive Summary (500-800 words)
  2. What This Arc Answered
  3. Consolidated Domain Shape (with §12.5 Revenue Lifecycle Traceability Table)
  4. Cross-Cutting Patterns (arc-wide 5-pillar convergence validated + F1/F2/F3/F4 S1399 methodology hits)
  5. Resolved Contradictions
  6. Unresolved Unknowns
  7. Anchor-Update Recommendations (PLATFORM_INVENTORY + PLATFORM_WHAT_IT_IS + ARCHITECTURE_INDEX + new `docs/topics/revenue-pipeline.md`)
  8. Follow-On Research Queue (10 tracks T1-T10 unified from S1405 + S1406 + prioritized ranking)
  9. Cross-Links to Delegated Arcs
  10. **What This Research Taught Us About How to Do Research (second application after S1399 close)**
  11. Arc Change Log
  12. Appendix — Provenance

- **Playbook §15 SIGN routing.** Full SIGN Q10-Q13 for canonical summary on fresh isolation pin (mint at S1499 mid-session). Preserve verifier-loop discipline (12+ checkpoints per S1404/S1405/S1406 precedent). Apply S1405 D48 stability-probe gate preemptively (matches S1406 pattern).
- **Playbook §13 6-parallel-Explore sweep.** NOT REQUIRED for xx99 per playbook §11.3 bounded-work rule (canonical summary consumes child outputs, doesn't re-audit).

### Category xx99 questions to answer (parent §12.1 parent-level questions + Chris methodology directive)

- Which of the 15 inherited findings from S1274 changed under child-audit evidence (CONFIRMED / CANDIDATE / DOWNGRADED / RESOLVED across all 6 children)?
- What are Revenue's F1/F2/F3/F4 diagnostic-lens hits (S1399 methodology inheritance) — cross-arc?
- What integration seams did children discover that S1274 didn't name?
- What is the arc-wide runtime owner recommendation (aggregating Cat E Revenue Employee + Cat F Income/Jobs Employee proposals)?
- What are the D23-D28 + post-D28 decisions that need Chris lock before Group 1400 → post-arc design-preparation phase?
- **Chris directive 2026-07-01 (adopted at S1399 close):** every xx99 canonical summary includes §10 "What This Research Taught Us About How to Do Research" — second application after S1399. Codify what worked (verifier-loop discipline expansion S1401-S1406, D48 stability-probe gate, provenance-stamp ORM probe, D45 recovery + warmup-ping pattern, Rigby SIGN batched-recovery) into playbook v3 §14 candidates per two-triggers threshold (S1500 second application ratifies).

### Open decisions gating S1499 launch

- **D52 — Launch cadence.** (i) Launch S1499 next session (default lean; matches D30/D34/D36/D38/D41/D46 rhythm across S1401-S1406); (ii) delay for post-S1406 review. **Default lean: OPTION (i) — sequential.**
- **D53 — Arc pin retention.** (i) Retain `pa-34d43795e1b24bd3` through S1499 close (default lean — matches D31/D33/D35/D37/D39/D42/D47 retention; arc-close discipline); (ii) mint fresh (Chris explicit call only). **Default lean: OPTION (i) — retain through S1499 close, then retire per playbook §16 arc-close discipline.**
- **D54 — S1405 F.E4-F.E10 deferred addendum handling at S1499.** (i) fold into xx99 §5 Resolved Contradictions synthesis (default lean — matches D51 defer-to-S1499 rationale); (ii) attempt fresh SIGN pin for pressure-test at S1499 mid-session; (iii) skip if worker-instability persists. **Default lean: OPTION (i) — synthesis fold at §5.**
- **D55 — Employee OS synthesis.** Aggregate Cat E R.E-1 Revenue Employee + Cat F R.F-1 Income/Jobs Employee proposals into (i) single merged "Revenue-plus-Income" Employee, (ii) two sibling JobContracts, (iii) three-tier structure (Revenue + Income + Ops Autopilot). Chris explicit call at S1499. **No default lean — Chris ratifies.**

Optional:

- **D56 (optional) — Post-arc design-preparation phase.** After S1499 close, launch design-preparation phase for T1-T10 ADRs? Sequential vs parallel? Chris ratifies.
- **D57 (optional) — T.C8 tool-timing final disposition.** Inherited from S1404/S1405/S1406 minimal-blocking discipline. S1499 last chance to fold into arc; otherwise deferred to post-arc queue.

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview` (per Rigby local trap)
3. Check if S1406 artifact set was committed + merged to `main` between sessions — if yes, S1499 branches off `main`
4. Verify `pa-34d43795e1b24bd3` retention status (`session_tool.health_check`); expected `strongly_recommend_fresh` — disclose to Chris but retain per arc-close discipline (retire at S1499 close only)
5. Retire `pa-8660ea7cfecd4bc6` (S1406 SIGN pin) via `session_tool.retire` if not yet retired post-merge
6. Resolve D52 (launch cadence) + D53 (arc pin retention) + D54 (S1405 F.E4-F.E10 fold) + **D55 (Employee OS synthesis)** with Chris via arc pin. D52+D53+D54 default leans align with prior discipline — likely fast "agree all"; D55 warrants explicit Chris pick.
7. Create branch `docs/session-1499-revenue-canonical-summary` off `main`
8. Read S1401 §9 + S1402 §9 + S1403 §9 + S1404 §9 + S1405 §9 + S1406 §9 integration maps + all 6 §14 findings surfaces + §19 follow-on queues (10 tracks total) + parent §12.5 F.iii artifact requirement
9. Draft `docs/research/domains/revenue/1499_revenue_canonical_summary.md` per playbook §11.3 12-section template (including §10 second application after S1399)
10. Route to Rigby with SIGN Q10-Q13 per playbook §15 stage table on fresh isolation pin; apply S1405 D48 stability-probe gate preemptively (mints fresh pin + warmup-ping + batched titles-only first substantive turn)
11. Fold Rigby SIGN edits + Chris ratification + commit + PR
12. **Arc close per playbook §16:** retire `pa-34d43795e1b24bd3` arc pin at S1499 close + move OPEN_ARCS Group 1400 row from In-progress → Closed section + update ARCHITECTURE_INDEX to add §1.29 for S1499 + §8 timeline row + frontmatter v26 preamble

---

## PA / Rigby context

- **Arc pin at session start:** `pa-34d43795e1b24bd3` (Group 1400 continuity through arc-close; retire at S1499 close per playbook §16).
- **S1406 SIGN pin retirement:** `pa-8660ea7cfecd4bc6` should be retired post-PR-merge via `session_tool.retire` (playbook §15 fresh isolation pin retirement rule).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin `pa-34d43795e1b24bd3`).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (S1405+S1406 2-session confirmed):** if Rigby generic-errors on turn 1 of a fresh SIGN pin, apply S1405 D45 recovery pattern preemptively — warmup-ping first (ultra-short "confirm ready" probe), then batched titles-only SIGN 3-4 findings per prompt, then substantive Q10-Q13 pressure-test. If instability persists after 2 fresh pins, D48 fallback (iii): defer to next arc synthesis or accept SIGN-with-edits cycle 1 as verdict. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.
- **Non-standard pa_chat.py invocation for fresh SIGN pin:** the `tools/pa_local.sh` wrapper hardcodes `--conversation pa-34d43795e1b24bd3` at the end. To send to a fresh SIGN pin, use direct pa_chat.py invocation with env vars: `PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-token> .venv/bin/python tools/pa_chat.py "$(cat /tmp/msg.txt)" --tools --conversation <fresh-pin-id>` — write prompt to file first to avoid shell backtick interpretation.

## Repo state at next-session open

- **Branch state (at S1406 close, before merge):** `docs/session-1406-revenue-freelance-gig-income-jobs` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1406 handoff at `docs/handoffs/SESSION_1406_REVENUE_FREELANCE_GIG_INCOME_JOBS.md`. Prior handoffs: SESSION_1405 (Group 1400 Child E Attribution + Analytics); SESSION_1404 (Group 1400 Child D Meeting + Close); SESSION_1403 (Group 1400 Child C Engagement Inbound); SESSION_1402 (Group 1400 Child B Outreach); SESSION_1401 (Group 1400 Child A Opportunity Discovery); SESSION_1400 (Group 1400 arc open); SESSION_1300-SESSION_1305 (Group 1300 children); SESSION_1399 (Group 1300 xx99 canonical summary).
- **ARCHITECTURE_INDEX version:** v25 (bumped this session with §1.28 S1406 + §8 timeline row + v25 preamble). Next bump at S1499 close (v26).
- **OPEN_ARCS state:** Group 1400 row current-child field = "6-child arc complete: S1406 SIGN-with-edits cycle 1 substantive (commit-gated per D50) + S1499 xx99 queued next." At S1499 close, row moves In-progress → Closed section with S1499 canonical summary listed as arc-closing doc.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1406 artifact set is on `main` — if yes, S1499 branches off `main`; if no, continues stacking on `docs/session-1406-revenue-freelance-gig-income-jobs`
- [ ] Verify `pa-34d43795e1b24bd3` health via `session_tool.health_check` (expect `continue` or `strongly_recommend_fresh` — if latter, disclose to Chris; arc-close discipline still applies through S1499 close)
- [ ] Retire `pa-8660ea7cfecd4bc6` (S1406 SIGN pin) if still active
- [ ] Resolve D52 (launch cadence: sequential) + D53 (arc pin retention: retain through S1499 close) + D54 (S1405 F.E4-F.E10 fold: at §5 synthesis) + **D55 (Employee OS synthesis: single-merged vs two-sibling vs three-tier)** with Chris via arc pin. D55 warrants explicit Chris pick.
- [ ] Create branch `docs/session-1499-revenue-canonical-summary` off `main`
- [ ] Read all 6 child audit §9 integration maps + §14 findings + §19 follow-on queues + parent §12.5 F.iii artifact requirement + S1401-S1406 arc-wide 5-pillar convergence context
- [ ] Draft `1499_revenue_canonical_summary.md` per playbook §11.3 12-section template (including §10 "What This Research Taught Us About How to Do Research" second application after S1399)
- [ ] Route to Rigby with SIGN Q10-Q13 per playbook §15 stage table on fresh isolation pin; apply S1405 D48 stability-probe gate preemptively
- [ ] Fold SIGN cycle edits + Chris ratification + commit + PR
- [ ] **Arc close per playbook §16:** retire `pa-34d43795e1b24bd3` arc pin at S1499 close + move OPEN_ARCS Group 1400 row from In-progress → Closed section + update ARCHITECTURE_INDEX to add §1.29 for S1499 + §8 timeline row + frontmatter v26 preamble

## Reference — where to look

- **Group 1400 parent scoping doc:** `docs/research/domains/revenue/1400_revenue_domain_scoping.md` — start here for anything Group 1400
- **Group 1400 parent §5 mission sequence:** locked as A → B → C → D → E → F → xx99 (D24 + D25)
- **Group 1400 parent §12.5 F.iii artifact requirement:** Revenue Lifecycle Traceability Table — S1499 owns
- **S1401 Child A audit:** `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md`
- **S1402 Child B audit:** `docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md`
- **S1403 Child C audit:** `docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md`
- **S1404 Child D audit:** `docs/research/domains/revenue/1404_revenue_meeting_close_audit.md`
- **S1405 Child E audit:** `docs/research/domains/revenue/1405_revenue_attribution_analytics_audit.md` — 5-track S1499 unified remediation plan candidates at §19 R.E-1 through R.E-7
- **S1406 Child F audit:** `docs/research/domains/revenue/1406_revenue_freelance_gig_income_jobs_audit.md` — 5-track S1499 additions at §19 R.F-1 through R.F-7 (total 10 tracks T1-T10)
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.3 12-section canonical summary template + §15 SIGN Q10-Q13 for xx99 + §16 arc-close discipline + §17 graduation criteria)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v25:** `docs/research/ARCHITECTURE_INDEX.md` — S1406 §1.28 + timeline row landed same-commit
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1400 In-progress row (final child complete + S1499 xx99 queued)
- **AUDIT_FINDINGS.md #12:** canonical Celery deferred-by-policy list — cross-reference before classifying any Celery-task-dormancy finding
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Whole-platform architecture inventory §3.32 + §4.9:** Revenue Pipeline row (S1273 v2)
- **Cross-domain integration audit §2.4 + §3.7 + §5.10 + §9.6 + §14 finding #36:** S1274 findings inherited by Group 1400 — S1499 §5 aggregates status
- **S1399 canonical summary:** `docs/research/domains/memory/1399_memory_canonical_summary.md` — first application of playbook §11.3 §10 meta-methodology; template for S1499

## Doctor warnings to expect

- Inventory freshness (stale) — `python manage.py generate_platform_inventory --write` to refresh; S1406 does not update inventory rows (research audit only)
- Handoff numbering continuity — legitimate; S1306-S1398 skipped by intent per Rigby lean at S1300 close; Chris's arc-numbering convention preserved for Group 1400 (S1401-S1406 + S1499)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 is older than latest handoff (informational; S1499 §7 will propose narrative updates for subsequent PR; Group 1400 does not touch narrative anchor mid-arc)
- Docs cascade — run 4-step cascade (build_docs_index → build_rag_corpus → sync_docs_index_to_documents → embed_documents) + build_docs_provenance after S1406 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`
