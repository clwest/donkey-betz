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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1502 close:**

- **ACTIVE ARC PIN:** `pa-791b3db549a64e54` (Group 1500 arc pin; minted at S1500 open, retained per playbook §16 for entire Group 1500 arc — carries P3-P6 sequence + P7 xx99).
- **`tools/pa_local.sh:128` already at `pa-791b3db549a64e54`** — no line-128 rotation needed at S1503 open.
- **Retired at S1502 close:** SIGN isolation pin `pa-64c019d7e6685d31` (S1502 Full SIGN pin; retired via `session_tool.retire` at S1502 close).
- **Retired at S1501 close:** SIGN isolation pin `pa-a39069230ab64450` (S1501 Full SIGN pin; retired via `session_tool.retire` at S1501 close).
- **Retired at S1500 open:** Group 1400 arc pin `pa-34d43795e1b24bd3` (was already retired at S1499 close per D53).
- **Retired at S1499 close:** `pa-877f1919efaa48e4` (S1499 SIGN isolation pin).
- **Retired at S1406 close:** `pa-8660ea7cfecd4bc6`.
- **Retired earlier:** `pa-4bdd5ad264674ce8` + `pa-637331c5f9574a10` (S1405); `pa-87ee24cd0d3947ce` (S1404); `pa-fba0c4c81fba4922` (S1403); `pa-4a0a28edcb7a45ec` (S1402); `pa-16d8b24d30e7a7d8` (S1401); `pa-aa54193f240f4846` + `pa-4fc3329d0db6484f` (S1399 Group 1300 arc-close).

Use `tools/pa_local.sh` for all chats — line 128 already pointing at active Group 1500 arc pin.

## READ THIS SECOND — S1502 CAT B LANDED; S1503 CAT C QUEUED NEXT

Session 1502 shipped the second child audit under Group 1500 Sports/DBAO/Intelligence: **Category B Sports Prediction & Analytics Agents Audit**. Doc landed at `docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md` (1981 lines after F1-F12 folds, `status: active`, `category: child_audit`, `subdomain_category: B`, playbook §11.2 20-section template + six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 7 load-bearing claims — 0 sub-agent errors caught pre-SIGN this pass cleaner than S1501's 3; sub-agent reports were internally consistent).

**Second sibling to apply D62 = (a) 4-item pre-brief mini-schema per surface upfront** — validates D62 propagation-upfront directive at second sibling by producing consistent evidence shape (§4.8 / §5.4 / §6.6 / §8.6 / §15.2) without schema drift from S1501.

**Rigby Full SIGN cycle 1 SIGN-with-edits at Medium confidence** via fresh isolation pin `pa-64c019d7e6685d31` — 3 substantive SIGN batches (Q1-Q3 completeness + maturity; Q4-Q6 integration + debt + risk; Q7-Q9 + overall verdict + F10/F11 UNKNOWN resolutions) + 1 stability probe via `cockpit_tool.worker_health`; **zero worker-instability observed across all 4 turns**. **F1-F12 folds landed at commit-time** (F1 §7.1 explicit call-chain block + §19 rank re-order PA registry rank 5→4; F2 §1 Finding 5 SignalCluster reframed to POSTURE-DECISION-PENDING per S1274 §12.3; F3 §1 Finding 6 outcome-feedback-loop reframed to POSTURE-DECISION-PENDING; F4 §1 Finding 7 Memory Domain bridge reframed to POSTURE-DECISION-PENDING; F5 §1 Finding 4 ArbitrageOpportunity dormant triple KEPT AS DRIFT per Rigby; F6 §15 fixture-identity added as debt #12; F7 §1 operational-vs-architectural risk axis; F8 §1 Finding 9 continue-on-error reframed to INTENTIONAL-OR-DRIFT NEEDING CONTRACT STATEMENT per S1501 F6 precedent; F9 Session-1205 language softened; F10 SportsBettingBrief model verified via grep + §4.6 subsection added; F11 REST endpoint router registration verified via grep of `core/urls.py:3083-3128`; F12 §5.1 direct-consume filter cite tightened). **Rigby Full SIGN cycle 2 SIGN-clean at High confidence** — cycle 1 prediction accurate. **Do-not-regress notes for PR:** keep §2.1 Cat B contract statement + preserve posture-decision-pending framing throughout §1 Findings 5-7 + preserve F1 explicit call-chain block + F6 fixture-identity debt #12 + F7 operational-vs-architectural risk axis.

**D48 preemptive stability-probe gate 5th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502 5-arc pattern — strengthens immediate codification recommendation from S1501 4-arc threshold. **Recommendation:** xx99 (S1599) §10.2 codifies D48 into playbook v3 §15 alongside D45 titles-only recovery + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent per S1499 §10 meta-methodology.

**Load-bearing findings owed to xx99 (S1599) via Cat F evidence plan:**

1. **Coordinator `.run()` vs `.execute()` asymmetry (HIGH operational risk — biggest per Rigby SIGN cycle 1 Q6).** 4 of 5 coordinator agents bypass Layer 1 `AgentExecution` telemetry; only `SportsOddsAnalyst.run()` at `sports_betting_coordinator.py:122` writes telemetry (Session 1206 inline comment). "False green" monitoring risk.
2. **PA tool registry gap (MED-HIGH operational risk).** `sports_odds_analyst` + `arbitrage_detector` absent from `tool_dispatcher.py:302-305` (only 4 of 6 sports agents registered).
3. **Direct-consume filter is post-fetch in-memory dict filter, NOT ORM query (HIGH cascade from S1501 §14.1).** Couples to spider dict-return shape, not persisted `SpiderData.data_type` enum. Cascade risk if Cat A fixes S1501 §14.1 enum drift.
4. **`ArbitrageDetector` does NOT persist to `sports.models.ArbitrageOpportunity` despite admin+serializer+viewset triple (MED-HIGH DRIFT).** F5 fold KEPT AS DRIFT per Rigby cycle 1.
5. **`SignalCluster.pattern_type` still lacks sports types + Cat B write side absent (HIGH architectural risk — biggest per Rigby cycle 1 verdict; POSTURE-DECISION-PENDING per F2 fold).** Materializes S1274 §14 Finding #6 on Cat B consumer side; extends S1501 §14.1 Cat A producer-side scope.
6. **Zero Cat B → Cat C outcome-to-agent learning loop (MED-HIGH architectural risk; POSTURE-DECISION-PENDING per F3 fold).** Cat C S1503 owns `BettingOutcomeVerifier`; verifies whether outcomes route back to Cat B for calibration.
7. **Zero Memory Domain (S1300) bridge (MED architectural risk; POSTURE-DECISION-PENDING per F4 fold).**
8. **`LineMovementAnalyzer` + `PredictionMarketAnalyst` scope-boundary (MED — Owed to xx99 reconciliation).**
9. **Coordinator "continue on error" failure semantics undocumented (MED — INTENTIONAL-OR-DRIFT NEEDING CONTRACT STATEMENT per F8 fold).**

**Cat B maturity verdict** per doc §13: **PARTIAL (armed but under-instrumented)**.

**Session close artifacts committed at S1502 close:**

```
docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md  [new; 1981 lines; SIGN-clean cycle 2 at High confidence]
docs/research/ARCHITECTURE_INDEX.md                                              [modified — v28 → v29; §1.32 + §8 timeline S1502 row + v29 preamble]
docs/research/OPEN_ARCS.md                                                       [modified — current-child field advanced; Recent reconciliations 2026-07-02 (S1502 close) entry]
docs/handoffs/SESSION_1502_SPORTS_CAT_B_AUDIT.md                                  [new — S1502 handoff]
00-START-NEXT-SESSION.md                                                         [modified — this file; P3 default lean advanced to S1503]
```

Handoff: `docs/handoffs/SESSION_1502_SPORTS_CAT_B_AUDIT.md`.

### NEXT-SESSION MISSION — CATEGORY C CHILD AUDIT (S1503)

**Recommended path: `Continue research group 1500: Category C — Sports Wager Tracking & Outcome Verification`**.

Third child audit under Group 1500. Parallel-safe with P1/P2 per parent §5 "Ordering rationale" (Cat C is user-facing consumer). Includes `BettingOutcomeVerifier` outcome→feedback gap flag that feeds Cat F evidence per parent §3.C.

**Cat C scope per parent §3.C:**
- `PlacedWager` model (`core/models_betting.py:13`)
- `PlacedWagerLeg` model (`core/models_betting.py:108`; multi-leg parlay support)
- `BettingStats` model (`core/models_betting.py:163`; W/L, ROI, streaks aggregated per user/sport)
- `BettingOutcomeVerifier` service (`core/services/betting_outcome_verifier.py:21`)
- Celery task `verify_betting_outcomes` (`core/tasks.py:6122`)
- Discord `/bankroll` command (`core/services/discord_bot.py:1404`)

**Load-bearing observations to inherit from S1502:**
- Cat B §1 Finding 6 outcome-feedback-loop MISSING (POSTURE-DECISION-PENDING per F3 fold). S1503 verifies whether `BettingOutcomeVerifier` writes outcomes back to Cat B (`MLPrediction.was_correct`) AND whether it routes them into any next-generation prediction context. Missing bridge is load-bearing "sports as island" evidence for Cat F.
- Cat B §4.1 MLPrediction inventory — Cat C reads via `PlacedWager.game` FK for settlement; verify pattern.
- Cat B §2.1 "does NOT guarantee" list — Cat C P3 verifies whether Cat C fills or extends the outcome-feedback + fixture-identity gaps.
- Cat B §7.1 F1-fold explicit call-chain block is a pattern to replicate at Cat C for its beat schedule / task / service call graph.
- Cat B §14.1 coordinator `.run()` vs `.execute()` asymmetry — verify whether `verify_betting_outcomes` (Cat C task) has its own version of the pattern.

Session flow at S1503 open:

1. `context-kit orient` (session-open protocol).
2. Confirm `service_context: local` via `platform_config_tool overview` on arc pin `pa-791b3db549a64e54`.
3. Check if S1502 artifact set merged to `main` between sessions.
4. If not yet merged: complete Chris merge + PR merge.
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
6. Chris ratifies P3 kickoff via `Continue research group 1500: Category C` (short command).
7. Draft P3 audit at `docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md` per playbook §11.2 20-section template.
8. Launch 6 parallel Explore sub-agents per playbook §13 evidence sweep for Category C scope only.
9. **Apply §5 pre-brief 4-item mini-schema per surface** per D62 = (a) propagate upfront (Chris-ratified S1501 open). Cite S1501 §4.6 + S1502 §4.8 as sibling exemplars.
10. Answer all 28 canonical questions (§9) — cite, reference, or `UNKNOWN`.
11. Route to Rigby per §15 stage table — Full SIGN on child audits; fresh SIGN isolation pin per §15; **D48 preemptive stability-probe gate — 5th-arm CODIFICATION-READY at S1502 close; S1503 would be 6th arm continuing the pattern** (recommended for xx99 codification at S1599 with 6-arc evidence base).
12. Fold SIGN-with-edits into P3 doc.
13. Session close: handoff + PR + docs cascade.

**Not next:** Category F (P6). It runs LAST.

**Also queued at future sessions:**
- S1504-S1506 children (D57 sequence);
- S1599 xx99 canonical summary after P1-P6 land (third application of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second);
- Subsequent PRs from Group 1400 §7 anchor-updates (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499);
- CLAUDE.md 3-employees narrative anchor drift (still flagged); `verify_doc_claims --only-drift` verifier subsequent PR.

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1502 artifact set is on `main` between sessions
4. If not yet merged: Chris merge + PR merge
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
6. Chris ratifies P3 kickoff (S1503 Category C default lean per parent §5 sequence)
7. Execute P3 audit per playbook §11.2 + §13 + §5 pre-brief schema propagation (D62 continuation with 2 sibling exemplars: S1501 §4.6 + S1502 §4.8)

---

## PA / Rigby context

- **Arc pin at session start:** `pa-791b3db549a64e54` (Group 1500 arc pin; already active in `tools/pa_local.sh:128`; carries Group 1500 arc-open context through P3-P7 sequence per playbook §16 retain rule).
- **S1502 SIGN routing:** Full SIGN cycles 1 + 2 ran on fresh isolation pin `pa-64c019d7e6685d31` per playbook §15 stage table (retired at S1502 close). Child audit SIGN routing is Full SIGN on fresh isolation pin per §15.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (S1405+S1406+S1499+S1501+S1502 5-session confirmed — D48 CODIFICATION-READY at 5-arc threshold):** if Rigby generic-errors on turn 1 of a fresh SIGN pin, apply D45 recovery pattern preemptively — warmup-ping first (ultra-short "confirm ready" probe), then batched titles-only SIGN 2-3 findings per prompt. S1502 marked the 5-arc threshold; xx99 §10.2 codifies into playbook v3 §15 with strengthened 5-arc evidence base. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.
- **Non-standard pa_chat.py invocation for fresh SIGN pin:** `tools/pa_local.sh` hardcodes `--conversation` — for fresh SIGN pin, use direct pa_chat.py invocation with env vars: `PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-token> .venv/bin/python tools/pa_chat.py "$(cat /tmp/msg.txt)" --tools --conversation <fresh-pin-id>` — write prompt to file first to avoid shell backtick interpretation.

## Repo state at next-session open

- **Branch state (at S1502 close, before merge):** `docs/session-1502-sports-cat-b-audit` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1502 handoff at `docs/handoffs/SESSION_1502_SPORTS_CAT_B_AUDIT.md`. Prior handoffs: SESSION_1501 (Sports Cat A); SESSION_1500 (Sports arc open); SESSION_1499 (Revenue arc-close canonical summary); SESSION_1406 (Cat F final); SESSION_1405 (Cat E); SESSION_1404 (Cat D); SESSION_1403 (Cat C); SESSION_1402 (Cat B); SESSION_1401 (Cat A); SESSION_1400 (Group 1400 arc open); SESSION_1399 (Group 1300 canonical summary — first xx99); SESSION_1300-SESSION_1305 (Group 1300 children).
- **ARCHITECTURE_INDEX version:** v29 (bumped this session with §1.32 S1502 Cat B audit + §8 timeline S1502 row + v29 preamble). Next bump at S1503 close (v29 → v30 for §1.33 Cat C child audit).
- **OPEN_ARCS state:** Group 1500 row current-child field advanced to "S1502 SIGN-clean cycle 2 (commit-gated) + S1503 queued next"; row remains In-progress. Group 1400 remains in Closed section. Next arc-open (post-Group-1500 close) populates queue with Group 1600 Content / Deliverables / Publishing default lean.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1502 artifact set is on `main` — if yes, next session branches off `main`
- [ ] Run post-merge 4-step docs cascade + `build_docs_provenance` if not yet run per `feedback_docs_cascade_at_every_close.md`
- [ ] Chris ratifies P3 kickoff: default lean is `Continue research group 1500: Category C — Sports Wager Tracking & Outcome Verification` (S1503)
- [ ] Execute P3 audit per playbook §11.2 20-section template + §13 6-parallel-Explore sweep + §5 pre-brief mini-schema application (D62 continuation with 2 sibling exemplars)
- [ ] Route Full SIGN to fresh isolation pin per playbook §15 with D48 preemptive stability-probe gate (6th-arm reinforcement of CODIFICATION-READY 5-arc pattern)

## Reference — where to look

- **S1502 Cat B audit doc:** `docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md` — 20-section child audit + §2.1 Cat B contract statement + §14 drift matrix + §15 debt matrix + §19 10-item ranked future-research queue + §20.5 F1-F12 SIGN fold notes + cycle 2 verdict verbatim
- **S1501 Cat A audit doc:** `docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md` — sibling exemplar; §2.1 Cat A contract statement is Cat B's load-bearing input
- **Group 1500 parent scoping doc:** `docs/research/domains/sports/1500_sports_domain_scoping.md` — arc-open scoping + Phase 0 F.i/F.ii/F.iii second application UNCHANGED + candidate subdomain taxonomy A-F + child mission sequence P1-P7 + D62 = (a) 4-item mini-schema propagation directive
- **Group 1400 canonical summary:** `docs/research/domains/revenue/1499_revenue_canonical_summary.md` — arc-close synthesis + T1-T10 follow-on queue + Employee OS ownership resolution (post-arc phase inheritance)
- **Group 1300 canonical summary:** `docs/research/domains/memory/1399_memory_canonical_summary.md` (first formal xx99 canonical summary — precedent for playbook §11.3 §10 template)
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§9 canonical questions + §11.1 parent template + §11.2 child template + §11.3 xx99 canonical summary template + §13 evidence sweep + §15 SIGN + §16 arc-close + §17 graduation + §22 next-arc queue)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v29:** `docs/research/ARCHITECTURE_INDEX.md` — S1502 §1.32 + §8 timeline S1502 row + v29 preamble
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1500 In-progress section with S1502 SIGN-clean current-child field
- **AUDIT_FINDINGS.md #12:** canonical Celery deferred-by-policy list
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`

## Doctor warnings to expect

- Inventory freshness (unchanged this session — child audit only, no runtime changes)
- Handoff numbering continuity — S1502 continues arc-numbering convention (S1300 arc-open + S1301-S1305 children + S1399 canonical; S1400 arc-open + S1401-S1406 children + S1499 canonical; S1500 arc-open + S1501-S1506 children + S1599 canonical)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; S1502 doesn't touch narrative anchor)
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1502 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold)
- Group 1400 post-arc §7 anchor-updates still pending (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499)
- `sports_odds` structural gap CONFIRMED at code level AND extended in scope by S1502 §14.3 (materialized on Cat B consumer side — enum absence + write path absence); Category F evidence plan owed at S1506
- **D48 preemptive stability-probe gate 5th-arm CODIFICATION-READY** — S1503 SIGN cycle would be 6th arm; xx99 (S1599) §10.2 owns eventual playbook v3 §15 codification recommendation with strengthened 5-arc evidence base
