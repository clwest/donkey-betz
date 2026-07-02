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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1503 close:**

- **ACTIVE ARC PIN:** `pa-791b3db549a64e54` (Group 1500 arc pin; minted at S1500 open, retained per playbook §16 for entire Group 1500 arc — carries P4-P6 sequence + P7 xx99).
- **`tools/pa_local.sh:128` already at `pa-791b3db549a64e54`** — no line-128 rotation needed at S1504 open.
- **Retired at S1503 close:** SIGN isolation pin `pa-8ce5f949bed5e093` (S1503 Full SIGN pin; retired via `session_tool.retire` at S1503 close).
- **Retired at S1502 close:** SIGN isolation pin `pa-64c019d7e6685d31` (S1502 Full SIGN pin).
- **Retired at S1501 close:** SIGN isolation pin `pa-a39069230ab64450` (S1501 Full SIGN pin).
- **Retired at S1500 open:** Group 1400 arc pin `pa-34d43795e1b24bd3` (was already retired at S1499 close per D53).
- **Retired at S1499 close:** `pa-877f1919efaa48e4` (S1499 SIGN isolation pin).
- **Retired at S1406 close:** `pa-8660ea7cfecd4bc6`.
- **Retired earlier:** `pa-4bdd5ad264674ce8` + `pa-637331c5f9574a10` (S1405); `pa-87ee24cd0d3947ce` (S1404); `pa-fba0c4c81fba4922` (S1403); `pa-4a0a28edcb7a45ec` (S1402); `pa-16d8b24d30e7a7d8` (S1401); `pa-aa54193f240f4846` + `pa-4fc3329d0db6484f` (S1399 Group 1300 arc-close).

Use `tools/pa_local.sh` for all chats — line 128 already pointing at active Group 1500 arc pin.

## READ THIS SECOND — S1503 CAT C LANDED; S1504 CAT D QUEUED NEXT

Session 1503 shipped the third child audit under Group 1500 Sports/DBAO/Intelligence: **Category C Sports Wager Tracking & Outcome Verification Audit**. Doc landed at `docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md` (1177 lines after F1-F14 folds, `status: active`, `category: child_audit`, `subdomain_category: C`, playbook §11.2 20-section template + six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 7 load-bearing claims + Rigby ORM probe BEFORE draft integration — 2 Sub-agent 6 errors caught pre-SIGN — first library child audit to apply Rigby ORM probe as parent-Claude verifier-loop tool BEFORE SIGN routing).

**Third sibling to apply D62 = (a) 4-item pre-brief mini-schema per surface upfront** — completes D62 propagation-upfront validation across S1501+S1502+S1503 3-arc pattern by producing consistent evidence shape (§4.4 / §5.6 / §6.6 / §8.6 / §15.16) without schema drift.

**Rigby Full SIGN cycle 1 SIGN-with-edits at High confidence** via fresh isolation pin `pa-8ce5f949bed5e093` — 3 substantive SIGN batches (Q1-Q3 completeness + maturity; Q4-Q6 integration + debt + risk; Q7-Q9 + overall verdict) + 1 stability probe via `cockpit_tool.worker_health` confirming 4 workers online, 0 active tasks; **zero worker-instability observed across all 4 turns — cleanest arm of the D48 6-arc pattern**. Second independent Rigby SIGN cycle 1 batch 3 Q8 ORM probe verified same result as parent-Claude pre-SIGN probe (both returned 0 PeriodicTask + 0 CeleryTaskEvent 30d for both task variants) — CRITICAL §14.1 finding evidence-doubled via two independent probes on two different pins. **F1-F14 folds landed at commit-time** (F1 §5.4 additional Cat C read surfaces addendum; F2 §5.5 Bankroll adjacency touchpoints bounded subsection; F3 §1 executive summary compounding-risk observation Finding 1 + Finding 5 combo + orchestration+idempotency-as-readiness-gate reframe; F4 §14.1 + §20.5 independent Rigby ORM probe block; F5 §14.5 + §15.10 severity MED-HIGH → MED downgrade until divergence proven; F6 §15.13 new debt item timezone correctness on `commence_time`; F7 §15.14 new debt item idempotency + replay safety as PRE-RESTORE-BEAT GATE HIGH-severity; F8 §15.15 new debt item Decimal quantization policy; F9 §14.2 + §14.3 "bridge owns learning writes" default posture statement extending S1502 F3 pattern; F10 §19.1 CRITICAL tier reorganization — beat-schedule remediation + concurrency-safety hardening both promoted to CRITICAL as PRE-RESTORE-BEAT GATE; F11 §19.2 #5 new research item operational cadence study; F12 fixture identity strategy already at §19.4 no move; F13 §19.3 #9 new research item operator tooling PA tool + management command; F14 §5.5 dual-Bankroll footnote clarifying `Bankroll` PLUS `BankrollManagement` sports/models.py:1032). **Cycle 2 SIGN-clean at High confidence anticipated post-fold-land** — pattern-consistent with S1501 + S1502 cycle-1-predict-cycle-2 accuracy. **Do-not-regress notes for PR:** preserve §2.1 Cat C contract statement + preserve F9 "bridge owns learning writes" framing throughout §14.2 + §14.3 (do NOT backslide to "MISSING integration" defect language) + preserve F4 independent Rigby ORM probe block in §14.1 + §20.5 + preserve F7 idempotency-as-pre-restore-beat-gate framing in §15.14 + §19.1 (do NOT let CRITICAL #1 land without CRITICAL #2 landing first) + preserve F10 §19.1 CRITICAL tier ordering.

**D48 preemptive stability-probe gate 6th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502+S1503 6-arc pattern — cleanest arm — strengthens immediate codification recommendation from S1502 5-arc threshold. **Recommendation:** xx99 (S1599) §10.2 codifies D48 into playbook v3 §15 alongside D45 titles-only recovery + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent + **new S1503 addition: parent-Claude Rigby ORM probe BEFORE-SIGN pattern** per S1499 §10 meta-methodology.

**Load-bearing findings owed to xx99 (S1599) via Cat F evidence plan:**

1. **CRITICAL operational — `verify_betting_outcomes` unscheduled AND zero-fire (biggest per Rigby SIGN cycle 1 Q6).** Grep of `core/celery.py` returns zero + grep of `docs/AUDIT_FINDINGS.md` §12 canonical deferred list returns zero + BOTH independent Rigby ORM probes returned 0 PeriodicTask + 0 CeleryTaskEvent 30d for both task variants (`core.tasks.verify_betting_outcomes` + `sports.verify_betting_outcomes`). Docstring at `core/tasks.py:6129` claims "Runs every 2 hours" — phantom behavior. S1244 PR #2687 fixed sports-queue parity but did NOT restore beat entry.

2. **HIGH architectural POSTURE-DECISION-PENDING per S1502 F3 precedent — Zero Cat C → Cat B outcome-feedback loop.** Bridge reads `MLPrediction.was_correct` but does not write it; separate task `evaluate_ml_predictions` at `core/tasks.py:6192` owns that field. Answers S1502 §1 Finding 6 explicitly. F9 fold "bridge owns learning writes" default posture.

3. **HIGH architectural POSTURE-DECISION-PENDING per S1502 F2 precedent — Zero Cat C → Signal Engine emission.** Extends S1274 §14 Finding #6 into Cat C consumer side.

4. **MED-HIGH operational — Two task definitions for same feature (`core.tasks` + `sports.tasks`).**

5. **MED (F5 fold downgrade from MED-HIGH) — Discord `/bankroll` reads `Bankroll` model (not `BettingStats`) — dual aggregation surface.**

6. **MED-HIGH POSTURE-DECISION-PENDING per S1502 F4 precedent — Zero Cat C → Memory Domain (S1300) bridge beyond `AgentMemory` + `UserAgentLearning`.**

7. **MED architectural — `PlacedWagerLeg.event_id` string coupling to Odds API dict return shape (replicates S1502 §1 Finding 3 pattern).**

8. **MED POSTURE-DECISION-PENDING — Cat C is a leaf domain (zero inbound FKs); structural signature of "sports as island".**

9. **MED-HIGH operational — Zero test coverage across `core/tests/` for Cat C surface.**

10. **MED operational — No concurrency control on `_settle_wager()`.**

**Cat C maturity verdict** per doc §13: **PARTIAL (armed but zero-fire)** — third distinguishing maturity shape after S1501 "WORKING (fragile contract) at ingestion, PARTIAL at normalization" + S1502 "PARTIAL (armed but under-instrumented)".

**Session close artifacts committed at S1503 close:**

```
docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md  [new; 1177 lines; SIGN-with-edits cycle 1 folds landed at High confidence]
docs/research/ARCHITECTURE_INDEX.md                                                     [modified — v29 → v30; §1.33 + §8 timeline S1503 row + v30 preamble]
docs/research/OPEN_ARCS.md                                                              [modified — current-child field advanced; Recent reconciliations 2026-07-02 (S1503 close) entry]
docs/handoffs/SESSION_1503_SPORTS_CAT_C_AUDIT.md                                        [new — S1503 handoff]
00-START-NEXT-SESSION.md                                                                [modified — this file; P4 default lean advanced to S1504]
```

Handoff: `docs/handoffs/SESSION_1503_SPORTS_CAT_C_AUDIT.md`.

### NEXT-SESSION MISSION — CATEGORY D CHILD AUDIT (S1504)

**Recommended path: `Continue research group 1500: Category D — Sports Betting Content Pipeline`**.

Fourth child audit under Group 1500. Per parent §5 "Ordering rationale": Cat D depends on Cat A+B+C data + prediction surfaces (previously landed) — betting brief + digest generation + Discord `/odds` + intelligence bridge. Constrains Category F content-integration posture criteria.

**Cat D scope per parent §3.D:**
- `SportsContentContextBuilder` (`core/services/sports_content_context.py:27`)
- Celery task `generate_daily_betting_brief` (`core/tasks.py:6188`; beat @ 07:00 MT via `core/celery.py:783`)
- Celery task `daily_betting_digest` (`core/tasks.py:6102`)
- Discord `/odds` command (`core/services/discord_bot.py:1108`)
- Sports-scoped intelligence hook `_impl_collect_sports_odds_intelligence` (`core/tasks_financial.py:1815,1824`) posting to Discord `#market-intelligence`

**Load-bearing observations to inherit from S1503:**
- Cat C §2.1 Cat C contract statement — 9 items Cat C does NOT guarantee. S1504 verifies whether Cat D daily-betting-brief consumes Cat C data and whether integration path fills or extends Cat C's non-guarantees.
- Cat C §5.4 additional Cat C read surfaces list (`core/views_odds_sports.py` + `core/services/td_handlers_content.py` read path + `core/services/sports_content_context.py`) — **all 3 surfaces are in Cat D scope**; deep-audit at Cat D. Especially `sports_content_context.py` is Cat D's core scoping surface.
- Cat C §14.1 CRITICAL beat-schedule zero-fire pattern — S1504 must verify Cat D `generate_daily_betting_brief` beat state via analogous 3-axis probe (grep `core/celery.py` for beat entry + grep `docs/AUDIT_FINDINGS.md` §12 for intentional-deferral status + Rigby ORM probe on `PeriodicTask` + `CeleryTaskEvent 30d`). Parent §3.D claims beat @ 07:00 MT; S1504 verifies via ORM.
- Cat C §7.1 F1-fold explicit call-chain block — replicate at Cat D for `generate_daily_betting_brief` call graph (beat → task → context builder → LLM synthesis → Deliverable / Discord write path).
- Cat C §19 rank order for Cat F consumption.

Session flow at S1504 open:

1. `context-kit orient` (session-open protocol).
2. Confirm `service_context: local` via `platform_config_tool overview` on arc pin `pa-791b3db549a64e54`.
3. Check if S1503 artifact set merged to `main` between sessions.
4. If not yet merged: complete Chris merge + PR merge.
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
6. Chris ratifies P4 kickoff via `Continue research group 1500: Category D` (short command).
7. Draft P4 audit at `docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md` per playbook §11.2 20-section template.
8. Launch 6 parallel Explore sub-agents per playbook §13 evidence sweep for Category D scope only.
9. **Apply §5 pre-brief 4-item mini-schema per surface** per D62 = (a) propagate upfront (Chris-ratified S1501 open). Cite S1501 §4.6 + S1502 §4.8 + S1503 §4.4 as sibling exemplars (three-sibling exemplar pattern now).
10. **Apply Cat C §14.1 3-axis beat-schedule verification pattern to Cat D tasks** (`generate_daily_betting_brief`, `daily_betting_digest`, intelligence hook) — Rigby ORM probe BEFORE draft integration per S1503 pattern.
11. Answer all 28 canonical questions (§9) — cite, reference, or `UNKNOWN`.
12. Route to Rigby per §15 stage table — Full SIGN on child audits; fresh SIGN isolation pin per §15; **D48 preemptive stability-probe gate — 6th-arm CODIFICATION-READY at S1503 close; S1504 would be 7th arm continuing the pattern** (recommended for xx99 codification at S1599 with 7-arc evidence base).
13. Fold SIGN-with-edits into P4 doc.
14. Session close: handoff + PR + docs cascade.

**Not next:** Category F (P6). It runs LAST.

**Also queued at future sessions:**
- S1505 Category E Frontend Sports Surface + S1506 Category F Cross-Domain Integration Lens & Posture Decision Framing (D57 sequence);
- S1599 xx99 canonical summary after P1-P6 land (third application of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second);
- Subsequent PRs from Group 1400 §7 anchor-updates (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499);
- CLAUDE.md 3-employees narrative anchor drift (still flagged); `verify_doc_claims --only-drift` verifier subsequent PR.

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1503 artifact set is on `main` between sessions
4. If not yet merged: Chris merge + PR merge
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
6. Chris ratifies P4 kickoff (S1504 Category D default lean per parent §5 sequence)
7. Execute P4 audit per playbook §11.2 + §13 + §5 pre-brief schema propagation (D62 continuation with 3 sibling exemplars: S1501 §4.6 + S1502 §4.8 + S1503 §4.4)
8. **Apply Cat C §14.1 3-axis beat-schedule verification pattern to Cat D tasks + Rigby ORM probe BEFORE draft integration** per new S1503 pattern

---

## PA / Rigby context

- **Arc pin at session start:** `pa-791b3db549a64e54` (Group 1500 arc pin; already active in `tools/pa_local.sh:128`; carries Group 1500 arc-open context through P4-P7 sequence per playbook §16 retain rule).
- **S1503 SIGN routing:** Full SIGN cycle 1 ran on fresh isolation pin `pa-8ce5f949bed5e093` per playbook §15 stage table (retired at S1503 close via `session_tool.retire`); cycle 2 SIGN-clean anticipated post-fold-land at PR-merge or Chris-invoked follow-up.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (S1405+S1406+S1499+S1501+S1502+S1503 6-session confirmed — D48 CODIFICATION-READY at 6-arc threshold, cleanest arm at S1503):** if Rigby generic-errors on turn 1 of a fresh SIGN pin, apply D45 recovery pattern preemptively — warmup-ping first (ultra-short "confirm ready" probe), then batched titles-only SIGN 2-3 findings per prompt. S1503 marked the 6-arc threshold with entirely clean stability probe + zero worker-instability across all 4 substantive SIGN turns; xx99 §10.2 codifies into playbook v3 §15 with strengthened 6-arc evidence base. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.
- **Non-standard pa_chat.py invocation for fresh SIGN pin:** `tools/pa_local.sh` hardcodes `--conversation` — for fresh SIGN pin, use direct pa_chat.py invocation with env vars: `PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-token> .venv/bin/python tools/pa_chat.py "$(cat /tmp/msg.txt)" --tools --conversation <fresh-pin-id>` — write prompt to file first to avoid shell backtick interpretation.
- **New at S1503: Rigby ORM probe as parent-Claude verifier-loop tool BEFORE draft integration** — for CRITICAL load-bearing claims (especially zero-fire task classifications, PeriodicTask absence, dead-code claims), route ORM probe via Rigby (`scheduled_tasks_tool` + `ops_tool.celery_task_history`) BEFORE writing the claim into the draft. Extends verifier-loop tool chain. First applied S1503 for §14.1 zero-fire finding; pattern candidate for playbook v3 §14 evidence-rules addition.

## Repo state at next-session open

- **Branch state (at S1503 close, before merge):** `docs/session-1503-sports-cat-c-audit` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1503 handoff at `docs/handoffs/SESSION_1503_SPORTS_CAT_C_AUDIT.md`. Prior handoffs: SESSION_1502 (Sports Cat B); SESSION_1501 (Sports Cat A); SESSION_1500 (Sports arc open); SESSION_1499 (Revenue arc-close canonical summary); SESSION_1406 (Cat F final); SESSION_1405 (Cat E); SESSION_1404 (Cat D); SESSION_1403 (Cat C); SESSION_1402 (Cat B); SESSION_1401 (Cat A); SESSION_1400 (Group 1400 arc open); SESSION_1399 (Group 1300 canonical summary — first xx99); SESSION_1300-SESSION_1305 (Group 1300 children).
- **ARCHITECTURE_INDEX version:** v30 (bumped this session with §1.33 S1503 Cat C audit + §8 timeline S1503 row + v30 preamble). Next bump at S1504 close (v30 → v31 for §1.34 Cat D child audit).
- **OPEN_ARCS state:** Group 1500 row current-child field advanced to "S1503 SIGN-with-edits cycle 1 (folds landed, cycle 2 anticipated, commit-gated) + S1504 queued next"; row remains In-progress. Group 1400 remains in Closed section. Next arc-open (post-Group-1500 close) populates queue with Group 1600 Content / Deliverables / Publishing default lean.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1503 artifact set is on `main` — if yes, next session branches off `main`
- [ ] Run post-merge 4-step docs cascade + `build_docs_provenance` if not yet run per `feedback_docs_cascade_at_every_close.md`
- [ ] Chris ratifies P4 kickoff: default lean is `Continue research group 1500: Category D — Sports Betting Content Pipeline` (S1504)
- [ ] Execute P4 audit per playbook §11.2 20-section template + §13 6-parallel-Explore sweep + §5 pre-brief mini-schema application (D62 continuation with 3 sibling exemplars) + **Cat C §14.1 3-axis beat-schedule verification pattern applied to Cat D tasks + Rigby ORM probe BEFORE draft integration**
- [ ] Route Full SIGN to fresh isolation pin per playbook §15 with D48 preemptive stability-probe gate (7th-arm reinforcement of CODIFICATION-READY 6-arc pattern)

## Reference — where to look

- **S1503 Cat C audit doc:** `docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md` — 20-section child audit + §2.1 Cat C contract statement + §14 drift matrix + §15 debt matrix + §19 CRITICAL-tier reorganized ranked future-research queue + §20.5 two independent Rigby ORM probes evidence-doubled + §20.8 F1-F14 SIGN fold notes + Rigby cycle 1 verdict verbatim
- **S1502 Cat B audit doc:** `docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md` — sibling exemplar for D62 mini-schema + F1 explicit call-chain block + F3/F2/F4 posture-decision-pending framing precedents
- **S1501 Cat A audit doc:** `docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md` — sibling exemplar; §2.1 Cat A contract statement is Cat D's load-bearing input via Cat B + Cat C
- **Group 1500 parent scoping doc:** `docs/research/domains/sports/1500_sports_domain_scoping.md` — arc-open scoping + Phase 0 F.i/F.ii/F.iii second application UNCHANGED + candidate subdomain taxonomy A-F + child mission sequence P1-P7 + D62 = (a) 4-item mini-schema propagation directive
- **Group 1400 canonical summary:** `docs/research/domains/revenue/1499_revenue_canonical_summary.md` — arc-close synthesis + T1-T10 follow-on queue + Employee OS ownership resolution (post-arc phase inheritance)
- **Group 1300 canonical summary:** `docs/research/domains/memory/1399_memory_canonical_summary.md` (first formal xx99 canonical summary — precedent for playbook §11.3 §10 template)
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§9 canonical questions + §11.1 parent template + §11.2 child template + §11.3 xx99 canonical summary template + §13 evidence sweep + §15 SIGN + §16 arc-close + §17 graduation + §22 next-arc queue)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v30:** `docs/research/ARCHITECTURE_INDEX.md` — S1503 §1.33 + §8 timeline S1503 row + v30 preamble
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1500 In-progress section with S1503 SIGN-with-edits current-child field
- **AUDIT_FINDINGS.md #12:** canonical Celery deferred-by-policy list (`verify_betting_outcomes` grep-verified NOT on list — load-bearing for S1503 §14.1 CRITICAL classification; verified pattern reusable for Cat D S1504 tasks)
- **CELERY_AUDIT.md:** canonical Celery inventory — row 469-470 confirms both `verify_betting_outcomes` variants have empty beat column
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`

## Doctor warnings to expect

- Inventory freshness (unchanged this session — child audit only, no runtime changes)
- Handoff numbering continuity — S1503 continues arc-numbering convention (S1300 arc-open + S1301-S1305 children + S1399 canonical; S1400 arc-open + S1401-S1406 children + S1499 canonical; S1500 arc-open + S1501-S1506 children + S1599 canonical)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; S1503 doesn't touch narrative anchor)
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1503 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold)
- Group 1400 post-arc §7 anchor-updates still pending (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499)
- `sports_odds` structural gap CONFIRMED at code level AND extended in scope by S1502 §14.3 (Cat B consumer side) AND extended further by S1503 §14.3 (Cat C consumer side — zero SignalCluster emissions from wager settlements / streaks / arb verification); Category F evidence plan owed at S1506
- **`verify_betting_outcomes` CRITICAL zero-fire status** — flagged at S1503 §14.1 but NOT remediated by this audit (research not implementation). Post-arc follow-on PR needed per S1503 §19.1 CRITICAL tier: (i) restore beat entry with correct cadence; (ii) concurrency-safety hardening (`select_for_update()` + `@transaction.atomic()` OR task-level lock) as PRE-RESTORE-BEAT GATE — must land BEFORE beat restoration per F7 fold.
- **D48 preemptive stability-probe gate 6th-arm CODIFICATION-READY** — S1504 SIGN cycle would be 7th arm; xx99 (S1599) §10.2 owns eventual playbook v3 §15 codification recommendation with strengthened 6-arc evidence base + parent-Claude Rigby ORM probe BEFORE-SIGN pattern (new at S1503) as additional codification candidate.
