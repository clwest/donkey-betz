---
session: 1501
status: closed (Group 1500 Sports/DBAO/Intelligence arc — first child audit shipped; Category A Sports Odds Ingestion & Normalization audit landed at `docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md` — playbook §11.2 20-section template + 6 parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 5 load-bearing claims — 3 sub-agent errors caught pre-SIGN; Rigby Full SIGN cycle 1 SIGN-with-edits at Medium-High confidence on fresh isolation pin `pa-a39069230ab64450` → F1-F7 folds landed at commit-time → Rigby Full SIGN cycle 2 SIGN-clean at High confidence — cycle 1 prediction accurate; D48 preemptive stability-probe gate 4th arm — CODIFICATION-READY for playbook v3 §15 per S1405+S1406+S1499+S1501 4-arc pattern; D62 = (a) propagate upfront ratified by Chris at S1501 open — 4-item pre-brief mini-schema applied per surface; Group 1500 arc pin `pa-791b3db549a64e54` RETAINED per playbook §16; fresh SIGN pin `pa-a39069230ab64450` retired at S1501 close via `session_tool.retire`; ARCHITECTURE_INDEX v27 → v28)
date: 2026-07-01
arc: Research Group 1500 (Sports / DBAO / Intelligence) — first child audit under parent §5 mission sequence; P1 slot Category A Odds Ingestion & Normalization
authors: Claude Code (Chris directed via short command "Continue research group 1500: Category A")
---

# Session 1501 — Category A Sports Odds Ingestion & Normalization Audit

## What shipped

- **New audit doc:** `docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md` (1361 lines after F1-F7 folds; `status: active`, `category: child_audit`, `subdomain_category: A`, `authority: child-audit for Category A per parent §5 sequence + first sibling to apply the pre-brief mini-schema per D62 = (a) propagate upfront`).
- **ARCHITECTURE_INDEX v27 → v28:** §1.31 for S1501 child audit + §8 timeline S1501 row + frontmatter v28 preamble.
- **OPEN_ARCS updated:** Group 1500 row current-child field advanced "S1500 arc-open + S1501 queued next" → "S1501 SIGN-clean cycle 2 (commit-gated) + S1502 queued next"; row remains In-progress; last_updated frontmatter refreshed with S1501 close narrative; Recent reconciliations 2026-07-01 (S1501 close) entry added.
- **This handoff.**

## Chris ratifications this session

- **D62 = (a) propagate upfront** at S1501 open. 4-item pre-brief mini-schema (sports-only-vs-shared / DBAO-vs-mainline / integration-refactor-vs-extend / island-isolation-additions) propagates to P1-P5 children. Matches Rigby's cycle-1 fold rationale: prevents sibling schema drift, bounded 4-item annotation cost per surface, keeps P6/F focused on posture-decision brief rather than re-extraction.
- P1 audit merge (commit-gate expected via "commit it" 2026-07-01).

## Load-bearing findings owed to xx99 (S1599) posture-decision brief via Cat F evidence plan

1. **Silent choices-enum violation on `SpiderData` writes (HIGH — riskiest operational finding per Rigby SIGN cycle 1 Q6).** `SpiderData.data_type` at `persistence/models.py:693-712` declares 14 valid choices; `'sports_odds'` is NOT in the list. Same drift on `SpiderData.source_platform` at `persistence/models.py:641-663` (writes `'theodds'` and `'kalshi'`; neither in enum). Django CharField `choices=` validates only at Form/Admin layer, not at `Model.save()`, so writes silently persist. Cat B agents filter on `data_type == 'sports_odds'` (the string that isn't in the enum). Materializes S1274 §14 Finding #6 at code level AND extends its scope from `SignalCluster.pattern_type` (S1274 framing) to `SpiderData` itself.

2. **No unified normalization service (parent §6 P1-parked issue #1 grep-verified NEGATIVE — ARCHITECTURE-DECISION-PENDING per Rigby SIGN cycle 1 Q5 fold).** `grep -r "def.*normaliz.*odds\|class.*OddsNormaliz\|class.*Coordinator.*Odds" core/services/` returned 0 matches. Reclassified from HIGH to architecture-decision-pending because §2.1 Cat A contract statement confirms normalization is NOT part of Cat A's Cat B contract.

3. **Dual-store `SpiderData` vs `OddsSnapshot`/`GameLineHistory` (posture-decision-pending, LOW-MED per Rigby Q4 fold).** Not "duplicate models" — `SpiderData` = semantic/log surface; `OddsSnapshot` = UI-read-model surface. Whether a canonicalizer is required is a Cat F posture decision, not a Cat A prescription.

4. **`snapshot_odds_for_line_movement` dormant vs docstring (MEDIUM, reframed as "unimplemented expectation" per Rigby Q8 fold).** Docstring at `core/tasks_financial.py:2144` says "Runs every 20 minutes"; grep-verified NEGATIVE on `core/celery.py:37-797` — no beat entry.

5. **Discord docstring drift (LOW).** `_impl_collect_sports_odds_intelligence` docstring at `tasks_financial.py:1817` says `#market-intelligence`; `send_betting_digest` hardcodes `CHANNEL_BOARDROOM` at `discord_notifications.py:40`.

Additional observations (see doc §14, §15 for full drift + debt matrices):

- Fixture / entity identity resolution across TheOdds `event_id` and Kalshi `ticker` unresolved (Rigby Q8 fold surface — conditional MED-HIGH under any xx99 intent for cross-book aggregation per Rigby Q7).
- `SportsDataSpider` half-shipped persistence layer (`fetch_and_store_data()` at `ai_core/spiders/sports_data_spider.py:317-334` has placeholder DB write logic).
- 3× `SportsOddsSpider` mock configs in `ai_core/spiders/lightweight_spider_system.py:330-332` publish to Redis every 60s without documented gating.
- No retention policy on `OddsSnapshot` / `GameLineHistory`; unbounded row growth risk.

## Cat A maturity verdict

**WORKING (fragile contract) at ingestion, PARTIAL at normalization** (per doc §13 + Rigby SIGN cycle 1 Q2 fold F1). Not STABLE (silent choices-enum drift). Not CANONICAL (no source-of-truth doc pre-S1501). Continuous-language alignment per S1274 EventBus lesson.

## Rigby SIGN cycle history

- **Fresh isolation pin minted at S1501 open:** `pa-a39069230ab64450` via `session_tool.create_fresh(scope=global, title="S1501 Cat A P1 audit Full SIGN")` on arc pin `pa-791b3db549a64e54`.
- **D48 preemptive stability-probe gate applied:** ultra-short "confirm ready" probe first → returned `ready` clean → proceeded to substantive SIGN.
- **3 substantive SIGN batches** (titles-only + severity + one-sentence rationale per Q per Rigby SIGN worker-instability recovery pattern): batch 1 Q1-Q3 (completeness + maturity); batch 2 Q4-Q6 (integration/debt/risk); batch 3 Q7-Q9 + overall verdict.
- **Cycle 1 verdict:** SIGN-with-edits at Medium-High confidence. Cycle 2 prediction: SIGN-clean at High after F1-F7 folds.
- **F1-F7 folds landed at commit-time** — see doc §20.5 for verbatim per-fold notes.
- **Cycle 2 verdict:** SIGN-clean at High confidence. Cycle 1 prediction accurate.
- **Rigby cycle-2 most-accurate part:** "risk framing + contract clarity — the Cat A contract statement (F7) combined with the 'WORKING (fragile contract)' maturity call (F1) and the enum/choices issue held as top debt (F4/F5) makes the audit read operationally true and hard to misinterpret."
- **Rigby cycle-2 weakest part:** "posture-decision surfaces still depend on downstream evidence quality (even after the reframe): the doc is now correctly labeled 'decision pending,' but it's still inherently less conclusive than the ingestion/enum findings until the new downstream-consumer inventory is executed."
- **Rigby cycle-2 do-not-regress notes for PR + post-arc anchor updates:** keep §2.1 Cat A contract statement intact; preserve posture-decision-pending framing throughout §9 Q15 + §17; preserve enum-resolution HIGH severity in §15 debt #1 + §19 rank #2.
- **Zero worker-instability observed** across all 4 substantive turns on `pa-a39069230ab64450`. **D48 4th arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501 4-arc pattern.

## D48 stability-probe gate — CODIFICATION-READY at 4-arc threshold

Per S1499 §10 meta-methodology recommendation, the D48 preemptive stability-probe gate (mint fresh pin → ultra-short "confirm ready" ping → if clean, proceed to substantive SIGN in titles-only batches) hits its 4th consecutive successful arm at S1501 close. The S1499 recommendation was that D48 be codified into playbook v3 §15 at the 4-arc threshold. **S1501 marks that threshold.** Recommended for immediate codification alongside D45 titles-only recovery pattern + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent. xx99 (S1599) §10 meta-methodology section owns the eventual codification recommendation as the arc's fourth application confirming pattern.

## Cat A → Cat B (S1502) inheritance

- **§2.1 Cat A contract statement** (F7 fold) — what Cat A guarantees today vs what it explicitly does NOT guarantee. Cat B P2 verifies whether Cat B contract fills those gaps or extends them.
- **§14.1 silent choices-enum violations** — S1502 verifies whether Cat B agents' `data_type == 'sports_odds'` filters compensate for or extend the enum drift.
- **§19 rank order** — for Cat F consumption; enum resolution HIGH #2 + Downstream consumer inventory HIGH #3.
- **§4 4-item mini-schema per surface** — pattern for Cat B to replicate on the agent surfaces it inventories.
- **Fixture / entity identity across TheOdds `event_id` and Kalshi `ticker`** — unresolved at Cat A; Cat B P2 confirms whether agent-layer reconciliation exists.

## Chris directives folded

- **D62 = (a) propagate upfront** (2026-07-01 S1501 open) — 4-item pre-brief mini-schema propagates to P1-P5 upfront rather than P6/F extracting retroactively.
- Memory rules honored: `feedback_session_open_with_orient.md` (session-open protocol first tool call); `feedback_pa_chat_local_override.md` (verified `service_context: local` via Rigby `platform_config_tool overview` before first pa_chat); `feedback_pa_local_verify_ownership.md` (verified pa_local.sh:128 pinned to arc pin `pa-791b3db549a64e54` + token ownership); `feedback_rigby_sign_worker_instability_recovery.md` (D48 preemptive stability-probe gate applied at fresh pin mint; titles-only batched SIGN); `feedback_docs_cascade_at_every_close.md` (post-merge 4-step cascade + `build_docs_provenance` required after S1501 PR merges); `feedback_session_tool_retire_works.md` (SIGN pin retirement at close).

## Repo state at session close

- Branch: `docs/session-1501-sports-cat-a-audit` (based on `main` HEAD `c7dac6d9`).
- Files changed:
  ```
  docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md  [new; 1361 lines; status: active; sign_status: SIGN-clean cycle 2 at High confidence]
  docs/research/ARCHITECTURE_INDEX.md                                              [modified — v27 → v28; §1.31 registration + §8 timeline S1501 row + v28 preamble]
  docs/research/OPEN_ARCS.md                                                       [modified — current-child field advanced; Recent reconciliations 2026-07-01 (S1501 close) entry added; last_updated frontmatter refreshed]
  docs/handoffs/SESSION_1501_SPORTS_CAT_A_AUDIT.md                                  [new — this file]
  00-START-NEXT-SESSION.md                                                         [modified — P2 default lean advanced from S1501 to S1502]
  ```
- Chris commit-gate expected via "commit it" 2026-07-01.
- Post-merge: 4-step docs cascade + `build_docs_provenance` per `feedback_docs_cascade_at_every_close.md`.

## What's next (S1502 default lean)

**S1502 Category B — Sports Prediction & Analytics Agents Audit.** Per parent §5 D57 sequence P2 slot. Inventory: `core/agents/markets/sports_odds_analyst.py` + `game_predictor.py` + `sharp_action_detector.py` + `arbitrage_detector.py` (4 market agents) + `SportsBettingCoordinator` service at `core/services/sports_betting_coordinator.py:21` (orchestrator + unified brief generator). Cat A P1 doc §2.1 Cat A contract statement is Cat B's load-bearing input — verifies whether Cat B's contract to downstream fills or extends Cat A's "does NOT guarantee" list.

## Group 1500 arc status

- S1500 (parent scoping) — SHIPPED 2026-07-01 (parent §11.1 template + Phase 0 F.i/F.ii/F.iii methodology second application unchanged per D58; 6 D-decisions locked via governance decision `81d7467e-add6-420f-aee9-60b67d7867e8`)
- **S1501 (Category A Odds Ingestion & Normalization) — SHIPPED 2026-07-01 (this session)**
- S1502 (Category B Prediction/Analytics Agents) — QUEUED NEXT
- S1503 (Category C Wager Tracking & Outcome Verification) — queued
- S1504 (Category D Betting Content Pipeline) — queued
- S1505 (Category E Frontend Sports Surface) — queued
- S1506 (Category F Cross-Domain Integration Lens & Posture Decision Framing — LAST) — queued
- S1599 (xx99 canonical summary — third application of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second) — queued

## D48 stability-probe gate arc-4 codification-readiness — recommendation

**S1501 marks the 4th consecutive successful arm** (S1405 first application → S1406 clean stability probe + 10 CONFIRM verdicts → S1499 xx99 recovery via titles-only batches → S1501 clean probe + zero worker-instability across 4 substantive turns). Per S1499 §10 meta-methodology second-application recommendation, D48 was on 3-arc-threshold pending 4th arm to codify. **S1501 provides that 4th arm.** Recommendation: xx99 (S1599) §10.2 codifies D48 into playbook v3 §15 alongside D45 titles-only recovery + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent per S1499 §10 meta-methodology.
