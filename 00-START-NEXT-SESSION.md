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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1505 close:**

- **ACTIVE ARC PIN:** `pa-791b3db549a64e54` (Group 1500 arc pin; minted at S1500 open, retained per playbook §16 for entire Group 1500 arc — carries P6 sequence + P7 xx99).
- **`tools/pa_local.sh:128` already at `pa-791b3db549a64e54`** — no line-128 rotation needed at S1506 open.
- **Retired at S1505 close:** SIGN isolation pin `pa-546de7ebe8c8b885` (S1505 Full SIGN pin; retired via `session_tool.retire` at S1505 close — `updated_count: 5, retired: true`).
- **Retired at S1504 close:** SIGN isolation pin `pa-af2bf7f2d1a0ef61` (S1504 Full SIGN pin).
- **Retired at S1503 close:** SIGN isolation pin `pa-8ce5f949bed5e093` (S1503 Full SIGN pin).
- **Retired at S1502 close:** SIGN isolation pin `pa-64c019d7e6685d31` (S1502 Full SIGN pin).
- **Retired at S1501 close:** SIGN isolation pin `pa-a39069230ab64450` (S1501 Full SIGN pin).
- **Retired at S1500 open:** Group 1400 arc pin `pa-34d43795e1b24bd3` (was already retired at S1499 close per D53).
- **Retired at S1499 close:** `pa-877f1919efaa48e4` (S1499 SIGN isolation pin).
- **Retired at S1406 close:** `pa-8660ea7cfecd4bc6`.
- **Retired earlier:** `pa-4bdd5ad264674ce8` + `pa-637331c5f9574a10` (S1405); `pa-87ee24cd0d3947ce` (S1404); `pa-fba0c4c81fba4922` (S1403); `pa-4a0a28edcb7a45ec` (S1402); `pa-16d8b24d30e7a7d8` (S1401); `pa-aa54193f240f4846` + `pa-4fc3329d0db6484f` (S1399 Group 1300 arc-close).

Use `tools/pa_local.sh` for all chats — line 128 already pointing at active Group 1500 arc pin.

## READ THIS SECOND — S1505 CAT E LANDED; S1506 CAT F QUEUED NEXT (LAST CHILD BEFORE XX99)

Session 1505 shipped the fifth child audit under Group 1500 Sports/DBAO/Intelligence: **Category E Sports Frontend Surface Audit**. Doc landed at `docs/research/domains/sports/1505_sports_frontend_surface_audit.md` (1,009 lines after F1-F5 folds, `status: draft`, `category: child_audit`, `subdomain_category: E`, playbook §11.2 20-section template + six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 5 load-bearing claims — all 5 verified CORRECT by Rigby Q8 grep pass at cycle 1 batch 3 — plus 3 verifier-loop corrections applied to Explore agent conflicts pre-SIGN).

**Fifth sibling to apply D62 = (a) 4-item pre-brief mini-schema per surface upfront** — extends D62 propagation-upfront validation from S1504 4-sibling pattern to S1505 5-sibling pattern by producing consistent evidence shape (§4.2) without schema drift.

**Rigby Full SIGN cycle 1 SIGN-with-edits at High confidence** via fresh isolation pin `pa-546de7ebe8c8b885` — 4 substantive SIGN turns (1 warmup ping via `cockpit_tool.worker_health` + `infra_health_tool.dependency_matrix` + 3 SIGN batches Q1-Q3 architectural + Q4-Q6 architectural + Q7-Q9 grep-verified); **zero worker-instability observed across all 4 turns — D48 8th arm — three consecutive fully-clean arms S1503+S1504+S1505 pattern**. **Confidence upgrade Medium → High** at cycle 1 batch 3 after Rigby Q8 grep-verified all 5 load-bearing file:line claims independently pre-final-verdict (BettingPage.tsx = 3,023 lines; `BettingTab` union at line 14 declares 11 identifiers / `tabs` array lines 16-26 renders 9 nav; DEAD-RENDER-PATH conditionals at lines 968/975/2080/2298; `live_betting_opportunities` `@permission_classes([IsAuthenticated])` at `views_odds_sports.py:580` + `get_betting_intelligence` `@permission_classes([IsAuthenticated])` at `views_odds_sports.py:2056` + urls.py 3085 + 3099 mappings; `SportsBettingBrief.objects` 2-writer-0-reader). **F1-F5 folds landed at commit-time** (F1 §14.3 auth-drift wording tightening from frontend "assumes AllowAny" to two-sided drift class; F2 §15.5 elevated MED → HIGH structural debt "no API contract source-of-truth" as parent cause behind AUTH-DRIFT + inline interfaces + tab-count doc drift + read-path fragility; F3 §14.3 added "Verified-in-repo anchors" subsection; F4 §14.3 named tab-consumer identification; F5 §14.1 MOCK-DATA-CONSUMER intent-neutrality nuance). **Cycle 2 SIGN-clean at High confidence anticipated post-fold-land** — pattern-consistent with S1501+S1502+S1503+S1504 cycle-1-predict-cycle-2 accuracy. **Do-not-regress notes for PR:** preserve §2.1 Cat E contract statement (5 guarantees + 11 non-guarantees) + preserve F1-F5 folds per §20.8 detailed enumeration.

**D48 preemptive stability-probe gate 8th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505 8-arc pattern — further strengthens immediate codification recommendation from S1504 7-arc threshold with three-consecutive-fully-clean arms sub-pattern (S1503+S1504+S1505). **Recommendation:** xx99 (S1599) §10.2 codifies D48 into playbook v3 §15 alongside D45 titles-only recovery + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent + parent-Claude Rigby ORM probe BEFORE-SIGN pattern (2-arc evidence base held at S1505 close: S1503 first-applied + S1504 second-applied; S1505 did not apply because Cat E didn't have a beat-schedule zero-fire question to probe — pattern generalizes to specific claim classes not all audits) + S1504 addition: SIGN cycle 1 batch 1 verdict-text re-request recovery pattern (1-arc at S1505 close; S1505 did not extend because initial prompt framed "give me VERDICT TEXT" explicitly, preventing the tool-heavy response pattern — candidate for playbook v3 §15 as preventive framing rule rather than recovery pattern).

**Load-bearing findings owed to xx99 (S1599) via Cat F evidence plan (11):**

1. **CRITICAL architectural — `/ws/dbao/` broadcasts random mock data, not sports-derived state.** `core/new_pages_consumer.py:310-331` populates payload via `random.randint()` + `random.uniform()` for every metric field. **NEW pattern class for the arc: MOCK-DATA-CONSUMER** — distinct from S1504 WRITE-ONLY-FORGOTTEN + S1503 ZERO-FIRE-BEAT + S1502 PROVENANCE-STAMP-ABSENT. Here: no real data is touched at any point. F5 intent-neutrality fold: may be intentional demo/placeholder but operational-confusion / integration-signaling hazard stands.

2. **HIGH architectural — `markets` + `bankroll` DEAD-RENDER-PATH tabs.** `BettingTab` TypeScript union at `BettingPage.tsx:14` declares 11 tab identifiers; `tabs` array at lines 16-26 renders only 9 nav buttons; verifier-loop confirms the remaining 2 ARE wired at the render layer (query hooks at lines 968/975 + JSX conditionals at 2080/2298) but with no tab button, they are unreachable via UI navigation. **NEW pattern class: DEAD-RENDER-PATH.** Fifth distinguishing pattern shape after S1501–S1504.

3. **HIGH operational — 2 permission-floor inconsistencies** between frontend read-path expectations and backend IsAuthenticated decorators. Frontend calls `bettingApi.liveOpportunities()` → `GET /api/v1/sports/live-opportunities/` (urls.py:3085 → IsAuthenticated at views_odds_sports.py:580) + `bettingApi.intelligence()` → `GET /api/v1/sports/betting-intelligence/` (urls.py:3099 → IsAuthenticated at views_odds_sports.py:2056). Frontend has no client-side auth gate + api.ts:48-56 only triggers logout on 401 for auth endpoints. Silent 401 on Top Plays / Sharp Action / Arbitrage tab families. F1 fold two-sided drift class. F4 fold tab-consumer identification.

4. **HIGH architectural — S1504 §14.3 SportsBettingBrief write-only-and-forgotten CONFIRMED at frontend AND REST endpoint.** `get_betting_brief` at `views_odds_sports.py:3237-3265` calls coordinator on-the-fly; never queries persisted model.

5. **HIGH architectural — Zero WebSocket subscription from BettingPage despite defined sports WS routes.** `sports/routing.py:7-11` registers 3 consumers but BettingPage (3,023 lines) has zero WS references. Live Odds tab misnamed — 30s polling at `BettingPage.tsx:961`.

6. **MED-HIGH POSTURE-DECISION-PENDING** — Zero Cat E → Signal Engine emission path (extends 4-arc pattern to 5-arc pattern).

7. **MED architectural — BettingPage is SOLE frontend sports data consumer (zero cross-domain leak).** Positive isolation signal for Cat F island-vs-integrated posture evidence.

8. **MED operational — BettingPage.tsx = 3,023 lines god-component** (14 useQuery + 17+ useState + 5 inline sub-components + 11 inline TS interfaces).

9. **HIGH per S1504 §15.12 F4-fold sibling precedent — Zero dedicated test coverage.**

10. **MED architectural — Zero client-side state persistence.**

11. **MED — No CODEOWNERS row for BettingPage.tsx.**

**Cat E maturity verdict** per §13: **PARTIAL (mixed — WORKING at read-side tabs; DEAD-RENDER-PATH at markets/bankroll; MOCK-DATA-CONSUMER at /ws/dbao/; AUTH-DRIFT at 2 endpoints; NO-REALTIME across all tabs)** — fifth distinguishing maturity shape after S1501 fragile-contract-at-ingestion + S1502 armed-but-under-instrumented + S1503 armed-but-zero-fire + S1504 mixed-brief-generation-persistence-forgotten-HOT-PATH-CHOKE.

**Session close artifacts committed at S1505 close:**

```
docs/research/domains/sports/1505_sports_frontend_surface_audit.md  [new; 1009 lines; SIGN-with-edits cycle 1 folds F1-F5 landed at High confidence]
docs/research/ARCHITECTURE_INDEX.md                                 [modified — v31 → v32; §1.35 + §8 timeline S1505 row + v32 preamble]
docs/research/OPEN_ARCS.md                                          [modified — current-child field advanced; Recent reconciliations 2026-07-02 (S1505 close) entry]
docs/handoffs/SESSION_1505_SPORTS_CAT_E_AUDIT.md                    [new — S1505 handoff]
00-START-NEXT-SESSION.md                                            [modified — this file; P6 default lean advanced to S1506]
```

Handoff: `docs/handoffs/SESSION_1505_SPORTS_CAT_E_AUDIT.md`.

### NEXT-SESSION MISSION — CATEGORY F CHILD AUDIT (S1506) — LAST CHILD BEFORE XX99

**Recommended path: `Continue research group 1500: Category F — Cross-Domain Integration Lens & Posture Decision Framing`**.

Sixth and LAST child audit under Group 1500 before xx99 canonical summary. Per parent §5 "Ordering rationale": Cat F runs LAST because it consumes P1–P5 evidence to build the posture-decision evidence plan owed to xx99 per D59.

**Cat F scope per parent §3.F:**
- DBAO product-line materialization surface (PostgreSQL `dbao` schema, `/ws/dbao/` WebSocket namespace, `VITE_DBAO_API_URL` env-var namespace, `X-DBAO-Client` header convention)
- `intelligence/realtime_engine.py`, `intelligence/views.py:44` `sports_intelligence` feature flag
- `_impl_collect_sports_odds_intelligence` Discord bridge
- Signal Engine integration gap (`sports_odds` not a `SignalCluster.pattern_type` per S1274 §14 Finding #6)
- Memory Domain (S1300) learning-loop path (UNKNOWN — no bridge surfaced)
- `MLPrediction` / `BettingOutcomeVerifier` feedback gap

**Load-bearing observations to inherit from S1505:**
- Cat E §2.1 Cat E contract statement — 11 items Cat E does NOT guarantee. S1506 verifies whether Cat F cross-domain consumers rely on any of these non-guaranteed behaviors.
- Cat E §14.1 MOCK-DATA-CONSUMER at `/ws/dbao/` — **S1506 CRITICAL evidence plan item:** DBAO product-line footprint audit — does DBAO carry any real state anywhere in the platform, or is it entirely a naming convention with no runtime data? xx99-load-bearing.
- Cat E §14.5 zero WebSocket subscription — S1506 evaluates sports WS routes ownership (staged for future use / legacy with no owner / delete candidate).
- Cat E §14.3 AUTH-DRIFT two-sided framing — S1506 design-preparation candidate for canonical resolution (backend AllowAny migration vs frontend UI error handling).
- Cat E §14.6 Signal Engine emission absence at frontend read-out extends 4-arc pattern to 5-arc pattern — S1506 owes arc-close synthesis to xx99.
- Cat E §14.8 zero Memory Domain bridge extends 4-arc pattern to 5-arc pattern — S1506 owes POSTURE-DECISION framing.
- Cat E §9.3 positive isolation signal for Cat F (BettingPage sole sports consumer) — S1506 island-posture evidence weight.
- Cat E §4.2 humanApi cross-domain sharing on design-posture axis (d) — S1506 island-posture cost estimate raised above prior siblings.
- Cat E §7.1 F1-fold explicit call-chain block pattern — S1506 pattern candidate to replicate for cross-domain integration flow.

Session flow at S1506 open:

1. `context-kit orient` (session-open protocol).
2. Confirm `service_context: local` via `platform_config_tool overview` on arc pin `pa-791b3db549a64e54`.
3. Check if S1505 artifact set merged to `main` between sessions.
4. If not yet merged: complete Chris merge + PR merge.
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
6. Chris ratifies P6 kickoff via `Continue research group 1500: Category F` (short command).
7. Draft P6 audit at `docs/research/domains/sports/1506_sports_cross_domain_integration_lens_and_posture_decision_framing_audit.md` per playbook §11.2 20-section template.
8. Launch 6 parallel Explore sub-agents per playbook §13 evidence sweep for Category F scope only. Key: DBAO product-line footprint sweep + Signal Engine emission gap + Memory Domain bridge investigation + `sports_intelligence` feature flag reach + `_impl_collect_sports_odds_intelligence` Discord bridge reach.
9. **Apply §5 pre-brief 4-item mini-schema per surface** per D62 = (a) propagate upfront (Chris-ratified S1501 open). Cite S1501 §4.6 + S1502 §4.8 + S1503 §4.4 + S1504 §4.4 + S1505 §4.2 as sibling exemplars (**five-sibling exemplar pattern now**).
10. Answer all 28 canonical questions (§9) — cite, reference, or `UNKNOWN`.
11. **Build posture-decision evidence plan** per D59 — Cat F's load-bearing xx99 deliverable. NOT posture selection; evidence plan for Chris's post-arc decision.
12. Route to Rigby per §15 stage table — Full SIGN on child audits; fresh SIGN isolation pin per §15; **D48 preemptive stability-probe gate — 8th-arm CODIFICATION-READY at S1505 close; S1506 would be 9th arm continuing the pattern** (recommended for xx99 codification at S1599 with 9-arc evidence base + four-consecutive-clean-arms sub-pattern S1503+S1504+S1505+S1506 if held).
13. Fold SIGN-with-edits into P6 doc.
14. Session close: handoff + PR + docs cascade.

**Not next:** xx99 (S1599) — runs after S1506 lands. S1599 is the canonical summary consuming P1-P6 evidence.

**Also queued at future sessions:**
- S1599 xx99 canonical summary after P6 lands (third application of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second);
- Subsequent PRs from Group 1400 §7 anchor-updates (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499);
- CLAUDE.md 3-employees narrative anchor drift (still flagged); `verify_doc_claims --only-drift` verifier subsequent PR;
- Post-arc follow-on PRs from S1503+S1504+S1505 findings: `daily_betting_digest` beat-restoration OR intentional-deferral documentation + `SportsBettingBrief` consumer-or-remove decision + `/ws/dbao/` MOCK-DATA-CONSUMER remove-or-relocate decision + `markets`+`bankroll` DEAD-RENDER-PATH restore-or-delete decision + 2 AUTH-DRIFT endpoints AllowAny-migrate OR frontend-error-handling.

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1505 artifact set is on `main` between sessions
4. If not yet merged: Chris merge + PR merge
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
6. Chris ratifies P6 kickoff (S1506 Category F default lean per parent §5 sequence)
7. Execute P6 audit per playbook §11.2 + §13 + §5 pre-brief schema propagation (D62 continuation with 5 sibling exemplars: S1501 §4.6 + S1502 §4.8 + S1503 §4.4 + S1504 §4.4 + S1505 §4.2)

---

## PA / Rigby context

- **Arc pin at session start:** `pa-791b3db549a64e54` (Group 1500 arc pin; already active in `tools/pa_local.sh:128`; carries Group 1500 arc-open context through P6 sequence + P7 xx99 per playbook §16 retain rule).
- **S1505 SIGN routing:** Full SIGN cycle 1 ran on fresh isolation pin `pa-546de7ebe8c8b885` per playbook §15 stage table (retired at S1505 close via `session_tool.retire` with `force=true` — `updated_count: 5, retired: true, previously_active: true`); cycle 2 SIGN-clean anticipated post-fold-land at PR-merge or Chris-invoked follow-up.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505 8-session confirmed — D48 CODIFICATION-READY at 8-arc threshold, three-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505):** if Rigby generic-errors on turn 1 of a fresh SIGN pin, apply D45 recovery pattern preemptively — warmup-ping first (ultra-short "confirm ready" probe), then batched titles-only SIGN 2-3 findings per prompt. S1505 marked the 8-arc threshold with entirely clean stability probe + zero worker-instability across 4 substantive SIGN turns; xx99 §10.2 codifies into playbook v3 §15 with strengthened 8-arc evidence base + three-consecutive-fully-clean-arms sub-pattern. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.
- **Non-standard pa_chat.py invocation for fresh SIGN pin:** `tools/pa_local.sh` hardcodes `--conversation` — for fresh SIGN pin, use direct pa_chat.py invocation with env vars: `PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-token> .venv/bin/python tools/pa_chat.py "$(cat /tmp/msg.txt)" --tools --conversation <fresh-pin-id>` — write prompt to file first to avoid shell backtick interpretation.
- **New at S1505: Rigby Q8 grep-verified confidence-upgrade pattern.** When Rigby grep-verifies all load-bearing file:line claims independently at cycle 1 batch 3 (before final verdict), confidence upgrades Medium → High cleanly. Pattern candidate for playbook v3 §15 addition. First applied S1505; 1-arc evidence base. Requires audit doc to have file:line-heavy claims that grep-verify quickly.
- **Continued at S1505: Rigby ORM probe as parent-Claude verifier-loop tool BEFORE draft integration — S1505 non-application note.** The BEFORE-SIGN ORM probe pattern (first applied S1503, second applied S1504) did NOT apply cleanly to S1505 because Cat E has less beat-schedule scope + no primary "did this task fire?" ORM claim to verify. Cat E's load-bearing claims were file:line grep-verifiable and were verified by parent-Claude direct reads before draft integration + independently re-verified by Rigby Q8 grep pass at cycle 1 batch 3. 2-arc evidence base for BEFORE-SIGN ORM probe pattern holds. Pattern generalizes to specific claim classes not all audits.
- **Continued at S1505: SIGN cycle 1 batch 1 verdict-text re-request recovery pattern — S1505 non-trigger note.** The pattern (first applied S1504) did NOT trigger this session — Rigby's cycle 1 batch 1 delivered verdict text normally per prompt format. 1-arc evidence base holds. S1505 open prompt explicitly framed "give me VERDICT TEXT (not tool exhaustive verification)" up front, preventing the tool-heavy response pattern. Candidate for playbook v3 §15 as preventive framing rule (add "verdict text explicit request" as SIGN batch prompt convention) rather than recovery pattern.

## Repo state at next-session open

- **Branch state (at S1505 close, before merge):** `docs/session-1505-sports-cat-e-audit` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1505 handoff at `docs/handoffs/SESSION_1505_SPORTS_CAT_E_AUDIT.md`. Prior handoffs: SESSION_1504 (Sports Cat D); SESSION_1503 (Sports Cat C); SESSION_1502 (Sports Cat B); SESSION_1501 (Sports Cat A); SESSION_1500 (Sports arc open); SESSION_1499 (Revenue arc-close canonical summary); SESSION_1406 (Cat F final); SESSION_1405 (Cat E); SESSION_1404 (Cat D); SESSION_1403 (Cat C); SESSION_1402 (Cat B); SESSION_1401 (Cat A); SESSION_1400 (Group 1400 arc open); SESSION_1399 (Group 1300 canonical summary — first xx99); SESSION_1300-SESSION_1305 (Group 1300 children).
- **ARCHITECTURE_INDEX version:** v32 (bumped this session with §1.35 S1505 Cat E audit + §8 timeline S1505 row + v32 preamble). Next bump at S1506 close (v32 → v33 for §1.36 Cat F child audit).
- **OPEN_ARCS state:** Group 1500 row current-child field advanced to "S1505 SIGN-with-edits cycle 1 (F1-F5 folds landed, cycle 2 anticipated, commit-gated) + S1506 queued next"; row remains In-progress. Group 1400 remains in Closed section. Next arc-open (post-Group-1500 close at S1599) populates queue with Group 1600 Content / Deliverables / Publishing default lean.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1505 artifact set is on `main` — if yes, next session branches off `main`
- [ ] Run post-merge 4-step docs cascade + `build_docs_provenance` if not yet run per `feedback_docs_cascade_at_every_close.md`
- [ ] Chris ratifies P6 kickoff: default lean is `Continue research group 1500: Category F — Cross-Domain Integration Lens & Posture Decision Framing` (S1506; **LAST child before xx99**)
- [ ] Execute P6 audit per playbook §11.2 20-section template + §13 6-parallel-Explore sweep + §5 pre-brief mini-schema application (D62 continuation with 5 sibling exemplars)
- [ ] **Build posture-decision evidence plan** per D59 — Cat F's load-bearing xx99 deliverable (NOT posture selection; evidence plan for Chris's post-arc decision)
- [ ] Route Full SIGN to fresh isolation pin per playbook §15 with D48 preemptive stability-probe gate (9th-arm reinforcement of CODIFICATION-READY 8-arc pattern; if held-clean → four-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506)

## Reference — where to look

- **S1505 Cat E audit doc:** `docs/research/domains/sports/1505_sports_frontend_surface_audit.md` — 20-section child audit + §2.1 Cat E contract statement (5 guarantees + 11 non-guarantees) + §7.1 F1-analog explicit call-chain block for Top Plays tab + §14 drift matrix + §15 debt matrix with F2 structural debt elevation + §19 F8-fold CRITICAL-tier ranked future-research queue + §20.5 verifier-loop corrections + §20.8 F1-F5 SIGN fold notes + Rigby cycle 1 verdict verbatim
- **S1504 Cat D audit doc:** `docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md` — sibling exemplar for D62 mini-schema + F1 explicit call-chain block + F9 "bridge owns learning writes" default posture statement precedent + §14.3 SportsBettingBrief write-only-and-forgotten (upheld and strengthened at Cat E frontend AND REST endpoint)
- **S1503 Cat C audit doc:** `docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md`
- **S1502 Cat B audit doc:** `docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md`
- **S1501 Cat A audit doc:** `docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md`
- **Group 1500 parent scoping doc:** `docs/research/domains/sports/1500_sports_domain_scoping.md` — arc-open scoping + Phase 0 F.i/F.ii/F.iii second application UNCHANGED + candidate subdomain taxonomy A-F + child mission sequence P1-P7 + D62 = (a) 4-item mini-schema propagation directive
- **Group 1400 canonical summary:** `docs/research/domains/revenue/1499_revenue_canonical_summary.md`
- **Group 1300 canonical summary:** `docs/research/domains/memory/1399_memory_canonical_summary.md` (first formal xx99 canonical summary — precedent for playbook §11.3 §10 template)
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v32:** `docs/research/ARCHITECTURE_INDEX.md` — S1505 §1.35 + §8 timeline S1505 row + v32 preamble
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1500 In-progress section with S1505 SIGN-with-edits current-child field
- **AUDIT_FINDINGS.md #12:** canonical Celery deferred-by-policy list
- **CELERY_AUDIT.md:** canonical Celery inventory
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`

## Doctor warnings to expect

- Inventory freshness (unchanged this session — child audit only, no runtime changes)
- Handoff numbering continuity — S1505 continues arc-numbering convention (S1300 arc-open + S1301-S1305 children + S1399 canonical; S1400 arc-open + S1401-S1406 children + S1499 canonical; S1500 arc-open + S1501-S1506 children + S1599 canonical)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; S1505 doesn't touch narrative anchor)
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1505 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold)
- Group 1400 post-arc §7 anchor-updates still pending (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499)
- `sports_odds` structural gap CONFIRMED at code level AND extended in scope by S1502 §14.3 (Cat B) + S1503 §14.3 (Cat C) + S1504 §14.5 (Cat D) + S1505 §14.6 (Cat E — 5-arc pattern); Category F evidence plan owed at S1506
- **`daily_betting_digest` CRITICAL zero-fire status** — S1504 §14.1 flag still open (not remediated by research audits)
- **`SportsBettingBrief` CRITICAL write-only-and-forgotten status** — S1504 §14.3 upheld and strengthened by S1505 §14.4 (frontend AND REST endpoint layer both bypass persistence)
- **`/ws/dbao/` MOCK-DATA-CONSUMER pattern (S1505 §14.1) — NEW at S1505.** Cat F evidence plan owed at S1506 identifies DBAO product-line footprint audit as CRITICAL tier item
- **`markets` + `bankroll` DEAD-RENDER-PATH tabs (S1505 §14.2) — NEW at S1505.** Post-arc follow-on PR needed: restore nav OR delete conditional blocks + type members
- **2 AUTH-DRIFT endpoints (S1505 §14.3) — NEW at S1505.** Post-arc follow-on PR needed: migrate to AllowAny OR add frontend auth-check + UI error
- **D48 preemptive stability-probe gate 8th-arm CODIFICATION-READY** — S1506 SIGN cycle would be 9th arm; xx99 (S1599) §10.2 owns eventual playbook v3 §15 codification recommendation with strengthened 8-arc evidence base + three-consecutive-fully-clean arms sub-pattern S1503+S1504+S1505 (four-consecutive if S1506 holds clean) + BEFORE-SIGN Rigby ORM probe pattern (2-arc evidence base) + S1504 SIGN cycle 1 batch 1 verdict-text re-request recovery pattern (1-arc; candidate for preventive framing rule per S1505 non-trigger evidence) + S1505 Rigby Q8 grep-verified confidence-upgrade pattern (1-arc).
