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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1501 close:**

- **ACTIVE ARC PIN:** `pa-791b3db549a64e54` (Group 1500 arc pin; minted at S1500 open, retained per playbook §16 for entire Group 1500 arc — carries P2-P6 sequence + P7 xx99).
- **`tools/pa_local.sh:128` already at `pa-791b3db549a64e54`** — no line-128 rotation needed at S1502 open.
- **Retired at S1501 close:** SIGN isolation pin `pa-a39069230ab64450` (S1501 Full SIGN pin; retired via `session_tool.retire` at S1501 close).
- **Retired at S1500 open:** Group 1400 arc pin `pa-34d43795e1b24bd3` (was already retired at S1499 close per D53).
- **Retired at S1499 close:** `pa-877f1919efaa48e4` (S1499 SIGN isolation pin).
- **Retired at S1406 close:** `pa-8660ea7cfecd4bc6`.
- **Retired earlier:** `pa-4bdd5ad264674ce8` + `pa-637331c5f9574a10` (S1405); `pa-87ee24cd0d3947ce` (S1404); `pa-fba0c4c81fba4922` (S1403); `pa-4a0a28edcb7a45ec` (S1402); `pa-16d8b24d30e7a7d8` (S1401); `pa-aa54193f240f4846` + `pa-4fc3329d0db6484f` (S1399 Group 1300 arc-close).

Use `tools/pa_local.sh` for all chats — line 128 already pointing at active Group 1500 arc pin.

## READ THIS SECOND — S1501 CAT A LANDED; S1502 CAT B QUEUED NEXT

Session 1501 shipped the first child audit under Group 1500 Sports/DBAO/Intelligence: **Category A Sports Odds Ingestion & Normalization Audit**. Doc landed at `docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md` (1361 lines after F1-F7 folds, `status: active`, `category: child_audit`, `subdomain_category: A`, playbook §11.2 20-section template + six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 5 load-bearing claims — 3 sub-agent errors caught pre-SIGN and recorded §20.4).

**Chris ratified D62 = (a) propagate upfront at S1501 open** — 4-item pre-brief mini-schema (sports-only-vs-shared / DBAO-vs-mainline / integration-refactor-vs-extend / island-isolation-additions) propagates to P1-P5 children upfront rather than P6/F extracting retroactively. Matches Rigby's cycle-1 fold rationale: prevents sibling schema drift, bounded 4-item annotation cost per surface, keeps P6/F focused on posture-decision brief.

**Rigby Full SIGN cycle 1 SIGN-with-edits at Medium-High confidence** via fresh isolation pin `pa-a39069230ab64450` — 3 substantive SIGN batches (Q1-Q3 completeness + maturity; Q4-Q6 integration + debt + risk; Q7-Q9 + overall verdict) + 1 stability probe; **zero worker-instability observed across all 4 turns**. **F1-F7 folds landed at commit-time** (F1 §13 "WORKING (fragile contract) at ingestion, PARTIAL at normalization" qualifier; F2 §9 Q15 + §1 exec posture-decision-pending reframe cites S1274 §12.3 two-legitimate-postures precedent; F3 §17 dual-store SpiderData=semantic/log vs OddsSnapshot=UI-read-model clarification; F4 §15 debt severity adjustments — #1 HIGH confirmed / #2 → ARCHITECTURE-DECISION-PENDING / #6 LOW → MEDIUM; F5 §19 rank enum-resolution HIGH #2 + new HIGH #3 Downstream consumer inventory; F6 §14.3 unimplemented-expectation reframe; F7 §2.1 NEW Cat A contract statement — "Cat A guarantees today" vs "Cat A explicitly does NOT guarantee"). **Rigby Full SIGN cycle 2 SIGN-clean at High confidence** — cycle 1 prediction accurate. **Do-not-regress notes for PR:** keep §2.1 Cat A contract statement intact; preserve posture-decision-pending framing throughout §9 Q15 + §17; preserve enum-resolution HIGH severity in §15 debt #1 + §19 rank #2.

**D48 preemptive stability-probe gate 4th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501 4-arc pattern — clean stability probe + zero worker-instability across 4 substantive SIGN batches this session. **Recommendation:** xx99 (S1599) §10.2 codifies D48 into playbook v3 §15 alongside D45 titles-only recovery + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent per S1499 §10 meta-methodology.

**Load-bearing findings owed to xx99 (S1599) via Cat F evidence plan:**

1. **Silent choices-enum violation on `SpiderData` writes (HIGH — riskiest operational finding per Rigby SIGN cycle 1 Q6).** `SpiderData.data_type` at `persistence/models.py:693-712` declares 14 valid choices; `'sports_odds'` is NOT one of them. Same drift on `SpiderData.source_platform` at `persistence/models.py:641-663` (writes `'theodds'`/`'kalshi'` — not in enum). Django CharField `choices=` validates only in Forms/Admin, not at `Model.save()`, so writes silently persist. Materializes S1274 §14 Finding #6 at code level AND extends its scope from `SignalCluster.pattern_type` (S1274 framing) to `SpiderData` itself.
2. **No unified normalization service (parent §6 P1-parked issue #1 grep-verified NEGATIVE — ARCHITECTURE-DECISION-PENDING per Rigby SIGN cycle 1 Q5 fold).** Not automatic HIGH because §2.1 Cat A contract statement confirms normalization is NOT part of Cat A's Cat B contract.
3. **Dual-store `SpiderData` vs `OddsSnapshot`/`GameLineHistory`** = posture-decision-pending intentional read-optimized-vs-semantic separation (Rigby Q4 fold — not a defect).
4. **`snapshot_odds_for_line_movement` dormant vs docstring** — docstring at `core/tasks_financial.py:2144` says "Runs every 20 minutes"; grep-verified NEGATIVE on `core/celery.py:37-797` — no beat entry. Reframed as "unimplemented expectation" per Rigby Q8 fold.
5. **Discord docstring drift** — `_impl_collect_sports_odds_intelligence` at `tasks_financial.py:1817` says `#market-intelligence`; `send_betting_digest` hardcodes `CHANNEL_BOARDROOM` at `discord_notifications.py:40`.

**Cat A maturity verdict** per doc §13: **WORKING (fragile contract) at ingestion, PARTIAL at normalization**.

**Session close artifacts committed at S1501 close:**

```
docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md  [new; 1361 lines; SIGN-clean cycle 2 at High confidence]
docs/research/ARCHITECTURE_INDEX.md                                              [modified — v27 → v28; §1.31 + §8 timeline S1501 row + v28 preamble]
docs/research/OPEN_ARCS.md                                                       [modified — current-child field advanced; Recent reconciliations 2026-07-01 (S1501 close) entry]
docs/handoffs/SESSION_1501_SPORTS_CAT_A_AUDIT.md                                  [new — S1501 handoff]
00-START-NEXT-SESSION.md                                                         [modified — this file; P2 default lean advanced to S1502]
```

Handoff: `docs/handoffs/SESSION_1501_SPORTS_CAT_A_AUDIT.md`.

### NEXT-SESSION MISSION — CATEGORY B CHILD AUDIT (S1502)

**Recommended path: `Continue research group 1500: Category B — Sports Prediction & Analytics Agents`**.

Second child audit under Group 1500. Depends on S1501 Cat A data surface inventory (per parent §5 anti-scope: "Do NOT parallelize P1 and P2 speculatively; P2 needs P1's data-surface inventory as citation source"). Cat A P1 §2.1 Cat A contract statement is Cat B's load-bearing input — verifies whether Cat B's contract to downstream fills or extends Cat A's "does NOT guarantee" list.

**Cat B scope per parent §3.B:**
- `core/agents/markets/sports_odds_analyst.py`
- `core/agents/markets/game_predictor.py`
- `core/agents/markets/sharp_action_detector.py`
- `core/agents/markets/arbitrage_detector.py`
- `SportsBettingCoordinator` service at `core/services/sports_betting_coordinator.py:21` (orchestrator + unified daily/nightly brief generation)

**Load-bearing observations to inherit from S1501:**
- All 4 agents filter `data_type == 'sports_odds'` from `SpiderData` (direct-consume pattern). S1502 verifies whether this filter compensates for or extends the silent choices-enum drift from S1501 §14.1.
- Agent write surface (do agents write `MLPrediction`? auto-create initiatives? emit `SignalCluster` rows?) is parent §6 P1-parked issue that S1502 owns.
- `SportsBettingCoordinator` is Cat B — not Cat A. S1501 §5.2 verified it does NOT touch ingestion.

Session flow at S1502 open:

1. `context-kit orient` (session-open protocol).
2. Confirm `service_context: local` via `platform_config_tool overview` on arc pin `pa-791b3db549a64e54`.
3. Check if S1501 artifact set merged to `main` between sessions.
4. If not yet merged: complete Chris merge + PR merge.
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
6. Chris ratifies P2 kickoff via `Continue research group 1500: Category B` (short command).
7. Draft P2 audit at `docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md` per playbook §11.2 20-section template.
8. Launch 6 parallel Explore sub-agents per playbook §13 evidence sweep for Category B scope only.
9. **Apply §5 pre-brief 4-item mini-schema per surface** per D62 = (a) propagate upfront (Chris-ratified S1501 open). Cite S1501's application as sibling exemplar.
10. Answer all 28 canonical questions (§9) — cite, reference, or `UNKNOWN`.
11. Route to Rigby per §15 stage table — Full SIGN on child audits; fresh SIGN isolation pin per §15; **D48 preemptive stability-probe gate — 4th-arm CODIFICATION-READY at S1501 close; S1502 would be 5th arm continuing the pattern** (recommended for xx99 codification at S1599).
12. Fold SIGN-with-edits into P2 doc.
13. Session close: handoff + PR + docs cascade.

**Not next:** Category F (P6). It runs LAST.

**Also queued at future sessions:**
- S1503-S1506 children (D57 sequence);
- S1599 xx99 canonical summary after P1-P6 land (third application of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second);
- Subsequent PRs from Group 1400 §7 anchor-updates (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499);
- CLAUDE.md 3-employees narrative anchor drift (still flagged); `verify_doc_claims --only-drift` verifier subsequent PR.

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1501 artifact set is on `main` between sessions
4. If not yet merged: Chris merge + PR merge
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
6. Chris ratifies P2 kickoff (S1502 Category B default lean per parent §5 sequence)
7. Execute P2 audit per playbook §11.2 + §13 + §5 pre-brief schema propagation (D62 continuation)

---

## PA / Rigby context

- **Arc pin at session start:** `pa-791b3db549a64e54` (Group 1500 arc pin; already active in `tools/pa_local.sh:128`; carries Group 1500 arc-open context through P1-P7 sequence per playbook §16 retain rule).
- **S1501 SIGN routing:** Full SIGN cycles 1 + 2 ran on fresh isolation pin `pa-a39069230ab64450` per playbook §15 stage table (retired at S1501 close). Child audit SIGN routing is Full SIGN on fresh isolation pin per §15.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (S1405+S1406+S1499+S1501 4-session confirmed — D48 CODIFICATION-READY):** if Rigby generic-errors on turn 1 of a fresh SIGN pin, apply D45 recovery pattern preemptively — warmup-ping first (ultra-short "confirm ready" probe), then batched titles-only SIGN 2-3 findings per prompt. S1501 marked the 4-arc threshold; xx99 §10.2 codifies into playbook v3 §15. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.
- **Non-standard pa_chat.py invocation for fresh SIGN pin:** `tools/pa_local.sh` hardcodes `--conversation` — for fresh SIGN pin, use direct pa_chat.py invocation with env vars: `PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-token> .venv/bin/python tools/pa_chat.py "$(cat /tmp/msg.txt)" --tools --conversation <fresh-pin-id>` — write prompt to file first to avoid shell backtick interpretation.

## Repo state at next-session open

- **Branch state (at S1501 close, before merge):** `docs/session-1501-sports-cat-a-audit` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1501 handoff at `docs/handoffs/SESSION_1501_SPORTS_CAT_A_AUDIT.md`. Prior handoffs: SESSION_1500 (Sports arc open); SESSION_1499 (Revenue arc-close canonical summary); SESSION_1406 (Cat F final); SESSION_1405 (Cat E); SESSION_1404 (Cat D); SESSION_1403 (Cat C); SESSION_1402 (Cat B); SESSION_1401 (Cat A); SESSION_1400 (Group 1400 arc open); SESSION_1399 (Group 1300 canonical summary — first xx99); SESSION_1300-SESSION_1305 (Group 1300 children).
- **ARCHITECTURE_INDEX version:** v28 (bumped this session with §1.31 S1501 Cat A audit + §8 timeline S1501 row + v28 preamble). Next bump at S1502 close (v28 → v29 for §1.32 Cat B child audit).
- **OPEN_ARCS state:** Group 1500 row current-child field advanced to "S1501 SIGN-clean cycle 2 (commit-gated) + S1502 queued next"; row remains In-progress. Group 1400 remains in Closed section. Next arc-open (post-Group-1500 close) populates queue with Group 1600 Content / Deliverables / Publishing default lean.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1501 artifact set is on `main` — if yes, next session branches off `main`
- [ ] Run post-merge 4-step docs cascade + `build_docs_provenance` if not yet run per `feedback_docs_cascade_at_every_close.md`
- [ ] Chris ratifies P2 kickoff: default lean is `Continue research group 1500: Category B — Sports Prediction & Analytics Agents` (S1502)
- [ ] Execute P2 audit per playbook §11.2 20-section template + §13 6-parallel-Explore sweep + §5 pre-brief mini-schema application (D62 continuation)
- [ ] Route Full SIGN to fresh isolation pin per playbook §15 with D48 preemptive stability-probe gate (5th-arm reinforcement of CODIFICATION-READY 4-arc pattern)

## Reference — where to look

- **S1501 Cat A audit doc:** `docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md` — 20-section child audit + §2.1 Cat A contract statement + §14 drift matrix + §15 debt matrix + §19 10-item ranked future-research queue + §20.5 F1-F7 SIGN fold notes + cycle 2 verdict verbatim
- **Group 1500 parent scoping doc:** `docs/research/domains/sports/1500_sports_domain_scoping.md` — arc-open scoping + Phase 0 F.i/F.ii/F.iii second application UNCHANGED + candidate subdomain taxonomy A-F + child mission sequence P1-P7 + D62 = (a) 4-item mini-schema propagation directive
- **Group 1400 canonical summary:** `docs/research/domains/revenue/1499_revenue_canonical_summary.md` — arc-close synthesis + T1-T10 follow-on queue + Employee OS ownership resolution (post-arc phase inheritance)
- **Group 1300 canonical summary:** `docs/research/domains/memory/1399_memory_canonical_summary.md` (first formal xx99 canonical summary — precedent for playbook §11.3 §10 template)
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§9 canonical questions + §11.1 parent template + §11.2 child template + §11.3 xx99 canonical summary template + §13 evidence sweep + §15 SIGN + §16 arc-close + §17 graduation + §22 next-arc queue)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v28:** `docs/research/ARCHITECTURE_INDEX.md` — S1501 §1.31 + §8 timeline S1501 row + v28 preamble
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1500 In-progress section with S1501 SIGN-clean current-child field
- **AUDIT_FINDINGS.md #12:** canonical Celery deferred-by-policy list
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`

## Doctor warnings to expect

- Inventory freshness (unchanged this session — child audit only, no runtime changes)
- Handoff numbering continuity — S1501 continues arc-numbering convention (S1300 arc-open + S1301-S1305 children + S1399 canonical; S1400 arc-open + S1401-S1406 children + S1499 canonical; S1500 arc-open + S1501-S1506 children + S1599 canonical)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; S1501 doesn't touch narrative anchor)
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1501 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold)
- Group 1400 post-arc §7 anchor-updates still pending (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499)
- `sports_odds` structural gap CONFIRMED at code level AND extended in scope by S1501 §14.1 (now includes `SpiderData.data_type` + `SpiderData.source_platform` + `SignalCluster.pattern_type`); Category F evidence plan owed at S1506
- **D48 preemptive stability-probe gate 4th-arm CODIFICATION-READY** — S1502 SIGN cycle would be 5th arm; xx99 (S1599) §10.2 owns eventual playbook v3 §15 codification recommendation
