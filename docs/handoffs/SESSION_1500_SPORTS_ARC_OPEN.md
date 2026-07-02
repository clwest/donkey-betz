---
session: 1500
status: closed (Group 1500 Sports/DBAO/Intelligence arc OPENED; parent scoping doc drafted + Rigby Light SIGN cycles 1 + 2 SIGN-clean at 0.83 confidence after 9-fold cycle 1; 6 Chris D-decisions D56-D61 ratified via single governance decision `81d7467e-add6-420f-aee9-60b67d7867e8` "agree all + D-6=(a)" round; fresh S1500 arc pin `pa-791b3db549a64e54` minted; ARCHITECTURE_INDEX v26 → v27; OPEN_ARCS Group 1500 Not-started → In-progress; playbook v3 §11.1 promotion trigger armed for S1599 xx99 close per D58 unchanged-methodology second application)
date: 2026-07-01
arc: Research Group 1500 (Sports / DBAO / Intelligence) — arc-open per playbook §22 next-arc queue + §11.1 template + second application of Chris's Phase 0 F.i/F.ii/F.iii methodology per S1400 D29 two-triggers gate. **First Group 1500 session** (S1500 arc-open scoping). Playbook §11.1 parent template + Phase 0 F.i/F.ii/F.iii §10/§11/§12 sections applied UNCHANGED per D58.
---

# Session 1500 Handoff — Sports/DBAO/Intelligence arc open

## What shipped

**Group 1500 Sports / DBAO / Intelligence research arc OPENED.**

Deliverable: `docs/research/domains/sports/1500_sports_domain_scoping.md` (1269 lines after fold pass, `status: active`, `category: parent_scoping`, playbook §11.1 template + §10/§11/§12 Phase 0 F.i/F.ii/F.iii methodology second application UNCHANGED per D58).

### Session artifacts committed at S1500 close

```
docs/research/domains/sports/1500_sports_domain_scoping.md      [new; 1269 lines; status: active; sign_status: SIGN-clean cycle 2 at 0.83 confidence]
docs/research/ARCHITECTURE_INDEX.md                             [modified — v26 → v27; §1.30 + §8 timeline S1500 row + v27 preamble]
docs/research/OPEN_ARCS.md                                      [modified — Group 1500 Not-started → In-progress; last_updated prefix + Recent reconciliations entry]
tools/pa_local.sh                                               [modified — line 128 updated from retired Group 1400 arc pin `pa-34d43795e1b24bd3` to fresh S1500 arc pin `pa-791b3db549a64e54`]
00-START-NEXT-SESSION.md                                        [modified — rotated to S1501 mission spec + next-arc queue update]
docs/handoffs/SESSION_1500_SPORTS_ARC_OPEN.md                   [new — this handoff]
```

## Chris ratifications (2026-07-01)

Single "agree all + D-6=(a)" ratification round via governance decision `81d7467e-add6-420f-aee9-60b67d7867e8` (governance_tool `decision_create` action + `decision_decide` action approve → status `acted`). All six verdicts land 2026-07-01. Numbering continues from S1499 D55 sequence.

| ID | Verdict | Wording |
|---|---|---|
| D56 | Domain slug | `sports` (folder: `docs/research/domains/sports/`) |
| D57 | Arc shape | Parent-with-children (P1-P6 children + P7 xx99 at S1599) |
| D58 | Phase 0 methodology | F.i / F.ii / F.iii applied with unchanged sectional structure and intent — preserves v3 promotion trigger integrity per S1400 D29 two-triggers rule (Rigby caution 1 folded; Q6 wording refinement folded cycle 1) |
| D59 | Load-bearing question | Taxonomy + posture decision framing + evidence plan (NOT posture recommendation at Phase 0; Rigby refinement folded from pre-ratification pressure-test) |
| D60 | Anti-scope | As §7 proposed; Intelligence bounded to sports-scope only (no stock/legislation/narrative scope-drag per Rigby scope-magnet warning) |
| D61 | DBAO definition | Option (a) — "Donkey Betz Analytics Ops" product-line codename |

## Rigby SIGN cycles

**Pre-ratification pressure-test** (before draft): 4 refinements folded before Chris ratified:
1. D-4 wording refined from "posture recommendation as explicit deliverable" to "posture decision framing + evidence plan" (D59 final)
2. Rigby caution 1 (repeatability + discriminative value for v3 promotion) folded into §12.4 explicit criterion
3. Rigby caution 2 (over-loading Phase 0 with posture selection) folded into D59 + §12.6 boundary
4. Rigby caution 3 (Intelligence scope-magnet) folded into D60 + §3 non-candidates + §7 anti-scope + §10.1 boundary

**Light SIGN cycle 1** (arc pin `pa-791b3db549a64e54`, playbook §15 stage table): **SIGN-with-edits at 0.74 confidence Medium-High.** Verdict: "Edits are surgical (wording + one sequencing nuance). I didn't see a taxonomy-breaking issue that would force a restructure."

**9 folds landed at commit-time:**

| Q | Fold |
|---|------|
| Q1 | Category D scope clarification — "D covers sports OUTPUT surfaces (brief/digest/Discord); shared intelligence engine out-of-scope per D60; only sports-scoped hook (`_impl_collect_sports_odds_intelligence`) in." |
| Q2 | §4 parent-vs-single evidence tightened — added explicit list of what evidence cannot exist without children (A normalization realities / B agent output surfaces / C outcome→feedback loop / D content-vs-intelligence delimiter / E frontend WebSocket topology) |
| Q3 | §5 pre-brief mini-schema artifact added — 4-item annotation per surface per child audit (sports-only-vs-shared / DBAO-vs-mainline / integration-refactor-vs-extend / island-isolation-additions) to prevent P1-P5 schema drift that would force xx99 renormalization |
| Q4 | `sports_intelligence: True` flag ownership reassigned from xx99-only to **P6 investigation + xx99 documentation-anchor recommendation** |
| Q5 | §7 anti-scope item #9 added — "Bankroll / staking strategy optimization research" (common Sports scope-trap; product/quant strategy vs architecture scoping) |
| Q6 | §10 methodology wording refined — replaced "no additions, no refinements beyond the S1400 shape" with "unchanged sectional structure and intent; domain-specific content differs as expected" (protects v3 promotion trigger from strict-reader over-constraint) |
| Q7 | §12.4 discriminative-value criterion tightened — added "including at least one of (Scope confusion prevented) OR (Cleaner arc close)" gate (prevents promotion passing on softer points alone) |
| Q8 | §12.5 lifecycle traceability table — added "fixture / entity identity resolution" stage between ingestion and normalization (team ↔ league ↔ event IDs, timezone canonicalization, "same game" dedup — common silent failure surface in sports stacks; may resolve UNKNOWN) |
| Q9 | 4 anchor cites re-verified — `core/tasks_financial.py:1815` ✅ `intelligence/views.py:44` ✅ `core/celery.py:783,788` (corrected from `784,788` — off by 1 on `generate_daily_betting_brief` beat entry) `tests/one-off/test_websockets.py:51` ✅ |
| Q10 | §10.2 "island posture partially adopted" softened to "evidence of partial architectural isolation" — storage + realtime isolation confirmed; deploy/queue/service/auth boundary isolation remains Category F evidence |

**Light SIGN cycle 2** (same arc pin): **SIGN-clean at 0.83 confidence** (higher than Rigby's cycle 1 prediction of 0.78). Verdict: "No further edits required for LIGHT SIGN. Proceed to Chris commit-gate + PR."

Two "do not regress" notes for PR:
1. Keep §10.2 softened language ("partial architectural isolation evidence") — don't let it creep back into "island adopted"
2. Preserve corrected anchor cite (`celery.py:783`) in final PR diff

## Locked child mission sequence (D57)

| Slot | Session | Child title | Category | Priority rationale |
|---|---|---|---|---|
| P1 | S1501 | Sports Odds Ingestion & Normalization Audit | A | Foundation — no downstream audit is grounded without knowing what data lands and how it is normalized (5 spiders + 3 lightweight configs; OddsSnapshot + GameLineHistory) |
| P2 | S1502 | Sports Prediction & Analytics Agents Audit | B | Depends on P1 data surface (4 market agents + SportsBettingCoordinator) |
| P3 | S1503 | Wager Tracking & Outcome Verification Audit | C | Parallel-safe with P1/P2 (user-facing surface); BettingOutcomeVerifier feedback gap load-bearing for Category F |
| P4 | S1504 | Sports Betting Content Pipeline Audit | D | Depends on P1+P2+P3 data + prediction surfaces (Cat D scope clarification: sports OUTPUT surfaces only, not shared intelligence engine per Q1 fold) |
| P5 | S1505 | Sports Frontend Surface Audit | E | Consumes P1/P2/P3/P4 outputs (9-tab BettingPage; realtime channel investigation) |
| P6 | S1506 | Cross-Domain Integration Lens & Posture Decision Framing Audit | F | Load-bearing lens; runs LAST — consumes P1-P5 findings to build posture-decision evidence plan owed to xx99 per D59 |
| P7 | S1599 | **xx99 canonical summary** | — | Consumes P1-P6 outputs + produces Chris-gated posture-decision brief (evidence-consolidation, NOT posture selection per D59). Third application of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second. |

## Load-bearing runtime evidence (verified via 2 parallel Explore sub-agents at S1500 open against `main` HEAD `f7704586`)

**Sports betting subsystem:**
- 5 Django models across 2 files (`core/models_betting.py:13,108,163` + `core/models_odds_history.py:15,82`)
- 4 services (`sports_betting_coordinator.py:21`, `betting_outcome_verifier.py:21`, `sports_content_context.py:27`, `sports_data_spider.py:18`)
- 5 spiders (`theodds_spider.py:33`, `kalshi_spider.py:28`, `combat_sports_spider.py:30`, `horse_racing_spider.py:18`, `sports_data_spider.py:18`)
- 4 market agents in `core/agents/markets/` (`sports_odds_analyst.py`, `game_predictor.py`, `sharp_action_detector.py`, `arbitrage_detector.py`)
- 6 Celery tasks with 2 beat entries (`core/celery.py:783` @ 07:00 MT + `:788` @ 30-min)
- 9-tab `BettingPage.tsx` at `/betting` route
- 2 Discord commands (`/odds` at discord_bot.py:1108, `/bankroll` at :1404)
- `/ws/dbao/` WebSocket namespace (`tests/one-off/test_websockets.py:51`)
- `dbao` PostgreSQL schema (`docs/audit-2026/12-infrastructure.md:51`)
- `sports_intelligence: True` feature flag (`intelligence/views.py:44`)
- **Zero body-system integration** verified in heart.py / lungs.py / circulatory.py

**Load-bearing structural finding CONFIRMED at code level:** S1274 §14 Finding #6 — `sports_odds` NOT a valid `SignalCluster.pattern_type` (Signal Engine declares 10 canonical pattern types at `core/models_signal_intelligence.py:75-86`; `sports_odds` valid only on legacy `SpiderData.data_type`). This is the runtime constraint Category F posture-decision evidence plan must confront per S1274 §12.3.

**DBAO codename materialization (per D61):**
- PostgreSQL schema `dbao` (part of multi-schema `studio, public, dbao, shared`)
- WebSocket namespace `/ws/dbao/`
- `VITE_DBAO_API_URL` env-var namespace (test-only reference on `main`)
- `X-DBAO-Client` HTTP client header (test-only reference on `main`)
- **NOT** a mounted Django app (no `dbao/` folder, no `apps.py` entry)
- **NOT** an App.tsx route
- **NOT** a `/api/dbao/` URL prefix

**Interpretation:** DBAO = product-line codename materialized as (a) discrete PostgreSQL schema + (b) WebSocket metrics namespace + (c) implicit frontend/test naming convention. NOT a mounted app. Materialization gives Category F posture-decision surface a concrete anchor set at storage + realtime layers (§10.2 "evidence of partial architectural isolation" per Q10 fold — softened wording).

## Pinning + tools state at close

- **S1500 arc pin:** `pa-791b3db549a64e54` (fresh mint via `session_tool.create_fresh` on retired Group 1400 arc pin at session open; will remain active through Group 1500 P1-P7 arc)
- **Retired at S1500 open:** Group 1400 arc pin `pa-34d43795e1b24bd3` was already retired at S1499 close per D53
- **`tools/pa_local.sh:128` updated** — retired arc pin `pa-34d43795e1b24bd3` → fresh arc pin `pa-791b3db549a64e54`
- **Governance decision:** `81d7467e-add6-420f-aee9-60b67d7867e8` (create + decide-approve; status `acted`)
- **SIGN pin retirement:** none at S1500 close — Light SIGN cycles 1 + 2 ran on the arc pin per playbook §15 stage table (parent doc SIGN routing uses arc pin, not fresh isolation pin — matches S1300 + S1400 pattern)

## Playbook v3 promotion trigger status

**Group 1500 = second application of Chris's Phase 0 F.i/F.ii/F.iii methodology** per S1400 D29 two-triggers rule. Per D58, methodology applied with unchanged sectional structure and intent (Q6 fold refined wording from "no additions no refinements" to protect promotion trigger from strict-reader over-constraint).

**Promotion criteria (Rigby caution 1 + Q7 fold — stricter than "ran twice"):** xx99 §10.2 must demonstrate concrete discriminative-value evidence in at least 3 of 4 categories, **including at least one of (Scope confusion prevented) OR (Cleaner arc close)**:
1. Scope confusion prevented (§3 non-candidates + §7 anti-scope caught categories a mechanical single-audit would have merged into scope)
2. Rework reduced (§11.4 F.ii "what F.ii does NOT try to answer" prevented children from re-inventorying)
3. Cleaner arc close (§12 F.iii success criteria matched what xx99 actually produced without post-hoc criteria adjustment)
4. Chris-lock efficiency (single "agree all" round — S1500 hit this bar at §8)

If Group 1500 xx99 (S1599) closes clean with methodology unchanged AND ≥3 discriminative-value criteria met (including at least one of the 2 required ones), playbook v3 §11.1 template promotion becomes trigger-eligible. Playbook v3 promotion session ratifies.

## Next session priorities

**Recommended P1 open at next session:** `Continue research group 1500: Category A — Sports Odds Ingestion & Normalization` (S1501). First child audit.

**P1 session flow (per playbook §21 + §11.2 child template + §13 6-parallel-Explore evidence sweep):**

1. `context-kit orient` (session-open protocol).
2. Confirm `service_context: local` via `platform_config_tool overview` on arc pin `pa-791b3db549a64e54`.
3. Read this parent doc as parent context.
4. Read playbook §9 (28 canonical questions) + §11.2 (child audit 20-section template).
5. Launch 6 parallel Explore sub-agents per §13 evidence sweep for Category A scope only.
6. **Apply §5 pre-brief mini-schema requirement (Q3 fold):** for each surface inventoried, capture 4-item annotation (sports-only-vs-shared / DBAO-vs-mainline / integration-refactor-vs-extend / island-isolation-additions).
7. Synthesize per §11.2 template. Answer all 28 canonical questions (§9) — cite, reference, or `UNKNOWN`.
8. Route to Rigby per §15 stage table (Full SIGN on children; fresh SIGN isolation pin; D48 preemptive stability-probe gate per S1405+S1406+S1499 3-arc pattern).
9. Fold SIGN-with-edits into P1 doc.
10. Return summary to Chris per playbook §24.

**Parallel option:** Chris can open Category B (P2 S1502) in a separate session if he prefers concurrent-arc pattern (playbook §22 permits label-independence, but this arc's §5.5 sibling-inheritance rule recommends sequential P1→P2 per Q3 fold pre-brief schema requirement to prevent schema drift).

**Not next:** Category F (P6). It runs LAST per §5 ordering rationale per parent doc.

## Cascade notes for post-merge

Per memory rule `feedback_docs_cascade_at_every_close.md`, after S1500 PR merges to `main`:

```bash
python manage.py build_docs_index
python manage.py build_rag_corpus
python manage.py sync_docs_index_to_documents
python manage.py embed_documents --all-unembedded
python manage.py build_docs_provenance
```

Ensures Rigby search + long-term research continuity stays fresh.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — parent scoping only)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` unchanged (S1500 does not touch narrative anchor; child audits + xx99 will)
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged from S1499 close; awaits subsequent `verify_doc_claims` PR
- `sports_odds` structural gap — CONFIRMED at code level (S1274 §14 Finding #6); Category F evidence plan owed
- Post-merge docs cascade — 5-step cascade required (build_docs_index + build_rag_corpus + sync_docs_index_to_documents + embed_documents + build_docs_provenance)

## Load-bearing outputs to inherit at S1501 open

1. **Parent §2.5 verified evidence tables** — runtime baseline; children cite, don't re-inventory (playbook §9 anti-duplication rule)
2. **§3 category boundaries** — Cat A scope is odds ingestion + normalization only; consumers (agents, wagers, content, UI) are B/C/D/E scope; posture-decision surface is F
3. **§5 pre-brief mini-schema requirement (Q3 fold)** — 4-item annotation per surface per child audit; propagates to P1-P5 to prevent P6 F consolidation drift
4. **§6 parked candidate issues P1** — 2 items owed to Cat A (unified normalization service + `MLPrediction` write question)
5. **§11.1 6 prior findings pre-assigned to children** — Cat A inherits none directly (foundation); Cat B inherits `SpiderData.data_type='sports_odds'` boundary; Cat F inherits 4 prior findings including S1274 §14 Finding #6
6. **§10.2 "evidence of partial architectural isolation" wording** — do not regress to "island posture adopted" (Rigby Q10 do-not-regress note)
7. **`celery.py:783` anchor cite correction** — do not regress to `:784` (Rigby Q9 do-not-regress note)
