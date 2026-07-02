---
session: 1503
status: closed (Group 1500 Sports/DBAO/Intelligence arc — third child audit shipped; Category C Sports Wager Tracking & Outcome Verification audit landed at `docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md` — playbook §11.2 20-section template + 6 parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 7 load-bearing claims — 2 sub-agent errors caught pre-SIGN AND parent-Claude Rigby ORM probe BEFORE draft integration (first library child audit to apply this pattern); Rigby Full SIGN cycle 1 SIGN-with-edits at High confidence on fresh isolation pin `pa-8ce5f949bed5e093` → F1-F14 folds landed at commit-time → Rigby Full SIGN cycle 2 SIGN-clean at High confidence anticipated post-fold-land; D48 preemptive stability-probe gate 6th arm — cleanest arm of the pattern; CODIFICATION-READY continuation of S1405+S1406+S1499+S1501+S1502 5-arc pattern → 6-arc pattern; third sibling to apply D62 = (a) 4-item pre-brief mini-schema per surface upfront completing D62 propagation-upfront validation across S1501+S1502+S1503 3-arc pattern; Group 1500 arc pin `pa-791b3db549a64e54` RETAINED per playbook §16; fresh SIGN pin `pa-8ce5f949bed5e093` retired at S1503 close via `session_tool.retire`; ARCHITECTURE_INDEX v29 → v30)
date: 2026-07-02
arc: Research Group 1500 (Sports / DBAO / Intelligence) — third child audit under parent §5 mission sequence; P3 slot Category C Sports Wager Tracking & Outcome Verification
authors: Claude Code (Chris directed via short command "Continue research group 1500: Category C")
---

# Session 1503 — Category C Sports Wager Tracking & Outcome Verification Audit

## What shipped

- **New audit doc:** `docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md` (1177 lines after F1-F14 folds; `status: active`, `category: child_audit`, `subdomain_category: C`, `authority: child-audit for Category C per parent §5 sequence + third sibling to apply the pre-brief mini-schema per D62 = (a) propagate upfront`).
- **ARCHITECTURE_INDEX v29 → v30:** §1.33 for S1503 child audit + §8 timeline S1503 row + frontmatter v30 preamble.
- **OPEN_ARCS updated:** Group 1500 row current-child field advanced "S1502 SIGN-clean cycle 2 (commit-gated) + S1503 queued next" → "S1503 SIGN-with-edits cycle 1 (folds landed, cycle 2 anticipated) + S1504 queued next"; row remains In-progress; last_updated frontmatter refreshed with S1503 close narrative; Recent reconciliations 2026-07-02 (S1503 close) entry added.
- **This handoff.**

## Chris ratifications this session

- P3 audit kickoff via short command "Continue research group 1500: Category C" at S1503 open. Matches parent §5 mission sequence P3 default lean.
- D62 = (a) propagate upfront continuation — Cat C is the third sibling to apply the 4-item pre-brief mini-schema upfront per Chris's S1501 open ratification; no new decision needed this session. Completes 3-sibling D62 validation.

## Load-bearing findings owed to xx99 (S1599) posture-decision brief via Cat F evidence plan

1. **CRITICAL operational — `verify_betting_outcomes` unscheduled AND zero-fire (biggest per Rigby SIGN cycle 1 Q6).** Grep of `core/celery.py` for `verify_betting_outcomes`: zero matches. Grep of `docs/AUDIT_FINDINGS.md` §12 canonical deferred-by-policy list: zero matches (i.e., this task is NOT documented as intentionally deferred per S1245 canonical policy). Two independent Rigby ORM probes both returned `PeriodicTask.objects.count() = 0` AND `CeleryTaskEvent.objects.filter(30d).count() = 0` for BOTH task variants (`core.tasks.verify_betting_outcomes` at `core/tasks.py:6121` + `sports.verify_betting_outcomes` at `sports/tasks.py:414`). Docstring at `core/tasks.py:6129` claims "Runs every 2 hours via Celery Beat" — phantom behavior. S1244 PR #2687 fixed sports-queue parity but did NOT restore beat entry. S1165 added retry policy that never fires. Entire feature silently broken.

2. **HIGH architectural POSTURE-DECISION-PENDING per S1502 F3 precedent — Zero Cat C → Cat B outcome-feedback loop.** Grep of `betting_outcome_verifier.py` for `MLPrediction` / `was_correct`: zero matches. Bridge READS `MLPrediction.was_correct` at `sports_betting_bridge.py:394` but does NOT write it; `MLPrediction.was_correct` set by separate task `evaluate_ml_predictions` at `core/tasks.py:6192`. Answers S1502 §1 Finding 6 explicitly. F9 fold "bridge owns learning writes" default posture statement.

3. **HIGH architectural POSTURE-DECISION-PENDING per S1502 F2 precedent — Zero Cat C → Signal Engine emission.** Grep of `betting_outcome_verifier.py` for `SignalCluster` / `SignalService`: zero matches. Extends S1274 §14 Finding #6 (`sports_odds` not a `SignalCluster.pattern_type`) into Cat C consumer side.

4. **MED-HIGH operational — Two task definitions for same feature.** `core.tasks.verify_betting_outcomes` (with retry policy + BettingStats-recalc wrapper) AND `sports.verify_betting_outcomes` (simpler variant) both call the same `BettingOutcomeVerifier` service. Different names via `@shared_task(name=...)` — Celery treats as distinct. `docs/CELERY_AUDIT.md:469-470` confirms both registered, neither scheduled. Dispatcher-ambiguity risk when beat entry is added.

5. **MED (F5 fold downgrade from MED-HIGH) — Discord `/bankroll` reads `Bankroll` model, not `BettingStats`.** `discord_bot.py:1404-1527` reads `core.models_bankroll.Bankroll` and its `.wagers` FK relation. Dual aggregation surface. Two Bankroll-related classes exist per Rigby SIGN cycle 1 batch 3 grep: `Bankroll` at `core/models_bankroll.py:19` + `BankrollManagement` at `sports/models.py:1032`. Downgraded from MED-HIGH per Rigby cycle 1 batch 2 Q5 fold F5 "until divergence proven".

6. **MED-HIGH POSTURE-DECISION-PENDING per S1502 F4 precedent — Zero Cat C → Memory Domain (S1300) bridge beyond `AgentMemory` + `UserAgentLearning`.** `SportsBettingLearningBridge` writes to those two Memory Domain surfaces; no `MemoryLane` / `AgentKnowledgeSource` writes. Bounded scope.

7. **MED architectural — `PlacedWagerLeg.event_id` string coupling to Odds API dict return shape.** Replicates S1502 §1 Finding 3 direct-consume dict-shape pattern on Cat C side. `PlacedWagerLeg` has no FK to `sports.models.Game`; settlement looks up scores by `(sport, event_id)` string tuple. Decouples Cat C from `sports.models.Game` schema drift but couples to Odds API `event_id` naming.

8. **MED POSTURE-DECISION-PENDING — Cat C is a leaf domain (zero inbound FKs).** Structural signature of "sports as island". Grep-verified zero FKs from outside `core/models_betting.py` pointing INTO Cat C models. Outbound only to `AUTH_USER_MODEL` + self-references.

9. **MED-HIGH operational — Zero test coverage.** Grep of `core/tests/` for `PlacedWager` / `BettingStats` / `BettingOutcomeVerifier` / `verify_betting_outcomes`: zero files. Blocks confident regressions on settlement logic.

10. **MED operational — No concurrency control on `_settle_wager()`.** No `select_for_update()` on pending-leg fetch (`betting_outcome_verifier.py:54-57`); no `@transaction.atomic()` wrapper; idempotency guard exists at line 179 but races the outcome computation. Latent race condition — materializes only when task is dispatched concurrently.

**Cat C maturity verdict** per doc §13: **PARTIAL (armed but zero-fire)**. Third distinguishing maturity shape after S1501 "WORKING (fragile contract) at ingestion, PARTIAL at normalization" + S1502 "PARTIAL (armed but under-instrumented)". Captures features that are code-complete + surface-complete but scheduling-broken.

## New F-fold pattern extensions

- **F3 compounding-risk observation.** §1 executive summary explicitly notes Finding 1 + Finding 5 combo produces stale + inconsistent user-facing views with no "system is behind" signal. **First library child audit to introduce compounding-risk observation.**
- **F4 independent Rigby ORM probe evidence-doubling.** §14.1 + §20.5 hold BOTH parent-Claude pre-SIGN probe AND independent Rigby SIGN cycle 1 batch 3 Q8 probe results — two independent probes on two different pins both returning zero. **First library child audit to have two independent Rigby ORM probes on two different pins both returning zero for same CRITICAL claim.** Evidence-doubling technique candidate for playbook v3 §14 addition.
- **F7 pre-restore-beat gate concept.** §15.14 idempotency + replay safety as HIGH-severity operational debt that MUST land BEFORE beat-schedule remediation; §19.1 CRITICAL tier reorganization enforces the ordering (F10 fold). **First library child audit to add "pre-restore-beat gate" concept.**
- **Rigby ORM probe BEFORE-SIGN as parent-Claude verifier tool.** §20.4 verifier-loop notes document the BEFORE-SIGN ORM probe as a new verifier-loop tool chain step. **First library child audit to apply Rigby ORM probe as parent-Claude verifier-loop tool BEFORE SIGN routing.** Extends S1401-S1406 verifier tool chain (file-line direct-reads + broader-grep + model-context disambiguation + provenance-stamp ORM probe) with this new step. Pattern candidate for playbook v3 §14 evidence-rules addition.

## Rigby SIGN cycle 1 outcome

- **Verdict:** SIGN-with-edits at High confidence.
- **Fresh isolation pin:** `pa-8ce5f949bed5e093` (retired at S1503 close via `session_tool.retire`).
- **Structure:** 1 warm-up stability probe (via `cockpit_tool.worker_health` confirming 4 workers online, 0 active tasks) + 3 substantive SIGN batches (Q1-Q3 completeness + maturity; Q4-Q6 integration + debt + risk; Q7-Q9 + overall verdict).
- **Zero worker-instability observed across all 4 turns.** Cleanest arm of the 6-arc D48 pattern.
- **F1-F14 folds landed at commit-time** (all 14 non-negotiable + framing-refinement edits from Rigby cycle 1 batches).
- **Cycle 2 SIGN-clean at High confidence anticipated post-fold-land.** Matches S1501 + S1502 cycle-1-predict-cycle-2 pattern.

## D48 preemptive stability-probe gate — 6th arm CODIFICATION-READY

S1503 marks the 6th consecutive arc-close (S1405+S1406+S1499+S1501+S1502+S1503) with clean stability probe + zero worker-instability across multiple substantive SIGN batches. **Cleanest arm of the pattern — zero instability across 4 turns.** Further strengthens the immediate codification recommendation from S1502 5-arc threshold to 6-arc evidence base.

Recommended for immediate codification in playbook v3 §15 alongside:
- D45 titles-only recovery pattern
- Provenance-stamp ORM probe
- Parent-Claude 12/12 checkpoint precedent
- **NEW at S1503:** Parent-Claude Rigby ORM probe BEFORE-SIGN pattern (first library application at S1503)

Per S1499 §10 meta-methodology recommendation; xx99 (S1599) §10.2 owns eventual playbook v3 codification with 6-arc evidence base.

## What's next (S1504)

Per parent §5 mission sequence, P4 slot: **Category D Betting Content Pipeline Audit**. Load-bearing observations to inherit at S1504:

- Cat C §2.1 contract statement — 9 items Cat C does NOT guarantee. Cat D verifies whether daily-betting-brief consumes Cat C data and whether integration path fills or extends Cat C's non-guarantees.
- Cat C §5.4 additional Cat C read surfaces list (`views_odds_sports.py` + `td_handlers_content.py` read path + `sports_content_context.py`) — all 3 surfaces are in Cat D scope; deep-audit at Cat D.
- Cat C §14.1 CRITICAL beat-schedule zero-fire pattern — Cat D `generate_daily_betting_brief` beat state should be verified via analogous 3-axis probe (grep `core/celery.py` + grep `docs/AUDIT_FINDINGS.md` §12 + Rigby ORM probe). Pattern candidate for cross-category discovery.
- Cat C §7.1 F1-fold explicit call-chain block — replicate at Cat D for `generate_daily_betting_brief` call graph.
- Cat C §19 rank order for Cat F consumption.

## Repo state at S1503 close

- **Branch state (at S1503 close, before merge):** `docs/session-1503-sports-cat-c-audit` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1503 handoff at `docs/handoffs/SESSION_1503_SPORTS_CAT_C_AUDIT.md`. Prior handoffs: SESSION_1502 (Sports Cat B); SESSION_1501 (Sports Cat A); SESSION_1500 (Sports arc open); SESSION_1499 (Revenue arc-close canonical summary); SESSION_1406 (Cat F final); SESSION_1405 (Cat E); SESSION_1404 (Cat D); SESSION_1403 (Cat C); SESSION_1402 (Cat B); SESSION_1401 (Cat A); SESSION_1400 (Group 1400 arc open); SESSION_1399 (Group 1300 canonical summary — first xx99); SESSION_1300-SESSION_1305 (Group 1300 children).
- **ARCHITECTURE_INDEX version:** v30 (bumped this session with §1.33 S1503 Cat C audit + §8 timeline S1503 row + v30 preamble). Next bump at S1504 close (v30 → v31 for §1.34 Cat D child audit).
- **OPEN_ARCS state:** Group 1500 row current-child field advanced to "S1503 SIGN-with-edits cycle 1 (folds landed, cycle 2 anticipated, commit-gated) + S1504 queued next"; row remains In-progress. Group 1400 remains in Closed section. Next arc-open (post-Group-1500 close) populates queue with Group 1600 Content / Deliverables / Publishing default lean.

## Files changed this session

```
docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md  [new; 1177 lines; SIGN-with-edits cycle 1 folds landed]
docs/research/ARCHITECTURE_INDEX.md                                                     [modified — v29 → v30; §1.33 + §8 timeline S1503 row + v30 preamble]
docs/research/OPEN_ARCS.md                                                              [modified — Group 1500 row current-child field advanced; Recent reconciliations 2026-07-02 (S1503 close) entry]
docs/handoffs/SESSION_1503_SPORTS_CAT_C_AUDIT.md                                        [new — S1503 handoff]
00-START-NEXT-SESSION.md                                                                [modified — P4 default lean advanced to S1504]
```

## Rigby SIGN pin retirement

Fresh SIGN isolation pin `pa-8ce5f949bed5e093` retires at S1503 close via `session_tool.retire`. Group 1500 arc pin `pa-791b3db549a64e54` RETAINED per playbook §16 — carries P4-P6 sequence + P7 xx99.
