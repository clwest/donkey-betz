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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1500 open:**

- **ACTIVE ARC PIN:** `pa-791b3db549a64e54` (S1500 arc pin; minted at S1500 open via `session_tool.create_fresh` titled "S1500 Group 1500 Sports/DBAO/Intelligence arc open — Phase 0 second application"). Carries Group 1500 arc-open context through P1-P7 sequence.
- **`tools/pa_local.sh:128` already updated** to `pa-791b3db549a64e54` — no line-128 rotation needed at S1501 open.
- **Retired at S1500 open:** Group 1400 arc pin `pa-34d43795e1b24bd3` (was already retired at S1499 close per D53).
- **Recently retired at S1499 close:** `pa-877f1919efaa48e4` (S1499 SIGN isolation pin).
- **Retired at S1406 close:** `pa-8660ea7cfecd4bc6`.
- **Retired earlier:** `pa-4bdd5ad264674ce8` + `pa-637331c5f9574a10` (S1405); `pa-87ee24cd0d3947ce` (S1404); `pa-fba0c4c81fba4922` (S1403); `pa-4a0a28edcb7a45ec` (S1402); `pa-16d8b24d30e7a7d8` (S1401); `pa-aa54193f240f4846` + `pa-4fc3329d0db6484f` (S1399 Group 1300 arc-close).

Use `tools/pa_local.sh` for all chats — line 128 already pointing at active S1500 arc pin.

## READ THIS SECOND — GROUP 1500 SPORTS/DBAO/INTELLIGENCE ARC OPENED; S1501 CHILD A QUEUED

Session 1500 opened Research Group 1500 Sports / DBAO / Intelligence per playbook §22 next-arc queue. Parent scoping doc landed at `docs/research/domains/sports/1500_sports_domain_scoping.md` (1269 lines after fold pass, `status: active`, `category: parent_scoping`, playbook §11.1 template + Chris's Phase 0 F.i/F.ii/F.iii methodology **second application UNCHANGED per D58** — preserves v3 promotion trigger integrity per S1400 D29 two-triggers rule).

**All 6 arc-open decisions Chris-locked in single "agree all + D-6=(a)" ratification round via governance decision `81d7467e-add6-420f-aee9-60b67d7867e8`:**
- D56 slug = `sports`
- D57 arc shape = parent-with-children (P1-P6 + P7 xx99)
- D58 methodology UNCHANGED (Rigby caution 1 folded → §12.4 stricter discriminative-value criterion)
- D59 load-bearing question = taxonomy + **posture decision framing + evidence plan** (NOT posture recommendation — Rigby pre-ratification refinement folded)
- D60 anti-scope + Intelligence bounded to sports-scope only (D60 Rigby scope-magnet warning folded)
- D61 DBAO = "Donkey Betz Analytics Ops" product-line codename (option (a))

**Rigby Light SIGN cycles:** cycle 1 SIGN-with-edits at 0.74 confidence → 9 surgical folds landed → cycle 2 SIGN-clean at 0.83 confidence (higher than her cycle 1 prediction of 0.78; two do-not-regress notes for PR: keep §10.2 softened "partial architectural isolation" language + preserve corrected `celery.py:783` anchor cite).

**Load-bearing runtime evidence anchored at S1500 open (verified via 2 parallel Explore sub-agents against `main` HEAD `f7704586`):** Sports subsystem = 5 models + 4 services + 5 spiders + 4 market agents + 6 Celery tasks (2 beat) + 9-tab BettingPage + 2 Discord commands + `/ws/dbao/` WebSocket + `dbao` PostgreSQL schema + `sports_intelligence` feature flag; zero body-system integration. **Load-bearing structural finding CONFIRMED at code level:** S1274 §14 Finding #6 — `sports_odds` NOT a valid `SignalCluster.pattern_type` (Signal Engine declares 10 pattern types at `core/models_signal_intelligence.py:75-86`; `sports_odds` valid only on legacy `SpiderData.data_type`) — Category F posture-decision evidence plan owes.

**Locked child mission sequence (D57):**

| Slot | Session | Child title | Category |
|---|---|---|---|
| P1 | S1501 | Sports Odds Ingestion & Normalization Audit | A |
| P2 | S1502 | Sports Prediction & Analytics Agents Audit | B |
| P3 | S1503 | Wager Tracking & Outcome Verification Audit | C |
| P4 | S1504 | Sports Betting Content Pipeline Audit | D |
| P5 | S1505 | Sports Frontend Surface Audit | E |
| P6 | S1506 | Cross-Domain Integration Lens & Posture Decision Framing Audit | F (LAST) |
| P7 | S1599 | xx99 canonical summary | — |

**Session close artifacts committed at S1500 close:**

```
docs/research/domains/sports/1500_sports_domain_scoping.md      [new; 1269 lines; status: active; sign_status: SIGN-clean cycle 2 at 0.83]
docs/research/ARCHITECTURE_INDEX.md                             [modified — v26 → v27; §1.30 + §8 timeline S1500 row + v27 preamble]
docs/research/OPEN_ARCS.md                                      [modified — Group 1500 Not-started → In-progress]
tools/pa_local.sh                                               [modified — line 128 fresh S1500 arc pin]
00-START-NEXT-SESSION.md                                        [modified — this file]
docs/handoffs/SESSION_1500_SPORTS_ARC_OPEN.md                   [new — S1500 handoff]
```

Handoff: `docs/handoffs/SESSION_1500_SPORTS_ARC_OPEN.md`.

### NEXT-SESSION MISSION — CATEGORY A CHILD AUDIT (S1501)

**Recommended path: `Continue research group 1500: Category A — Sports Odds Ingestion & Normalization`**.

First child audit under Group 1500. Foundation for downstream audits.

Session flow at P1 open:

1. `context-kit orient` (session-open protocol).
2. Confirm `service_context: local` via `platform_config_tool overview` on arc pin `pa-791b3db549a64e54`.
3. Check if S1500 artifact set merged to `main` between sessions.
4. If not yet merged: complete Chris merge + PR merge.
5. **Run post-merge 5-step docs cascade** per `feedback_docs_cascade_at_every_close.md`: `build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `embed_documents --all-unembedded` → `build_docs_provenance`.
6. Chris ratifies P1 kickoff via `Continue research group 1500: Category A` (short command).
7. Draft P1 audit at `docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md` per playbook §11.2 20-section child template.
8. Launch 6 parallel Explore sub-agents per playbook §13 evidence sweep for Category A scope only.
9. **Apply §5 pre-brief mini-schema per parent Q3 fold** — for each surface inventoried, capture 4-item annotation (sports-only-vs-shared / DBAO-vs-mainline / integration-refactor-vs-extend / island-isolation-additions).
10. Answer all 28 canonical questions (§9) — cite, reference, or `UNKNOWN`.
11. Route to Rigby per §15 stage table — Full SIGN on child audits; fresh SIGN isolation pin per playbook §15; D48 preemptive stability-probe gate per S1405+S1406+S1499 3-arc pattern.
12. Fold SIGN-with-edits into P1 doc.
13. Session close: handoff + PR + docs cascade.

**Parallel alternative:** Chris can open Category B (S1502) concurrently, but this arc's §5 sibling-inheritance rule + Q3 pre-brief schema requirement recommends sequential P1→P2 to prevent schema drift.

**Not next:** Category F (P6). It runs LAST.

**Also queued at future sessions:**
- Any of S1502-S1506 children (D57 sequence);
- S1599 xx99 canonical summary after P1-P6 land (third application of playbook §11.3 §10 meta-methodology template);
- Subsequent PRs from Group 1400 §7 anchor-updates (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499 post-arc phase);
- CLAUDE.md 3-employees narrative anchor drift (still flagged); `verify_doc_claims --only-drift` verifier subsequent PR.

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1500 artifact set merged to `main` between sessions
4. If not yet merged: Chris merge + PR merge
5. **Run post-merge 5-step docs cascade** per `feedback_docs_cascade_at_every_close.md`
6. Chris ratifies P1 kickoff (S1501 Category A default lean per parent §5 sequence)
7. Execute P1 audit per playbook §11.2 + §13 + §5 pre-brief schema propagation

---

## PA / Rigby context

- **Arc pin at session start:** `pa-791b3db549a64e54` (Group 1500 arc pin; already active in `tools/pa_local.sh:128`).
- **S1500 SIGN routing:** Light SIGN cycles 1 + 2 ran on arc pin per playbook §15 stage table (parent doc SIGN routing uses arc pin, not fresh isolation pin — matches S1300 + S1400 pattern). Child audit SIGN routing is Full SIGN on fresh isolation pin per §15.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (S1405+S1406+S1499 3-session confirmed):** if Rigby generic-errors on turn 1 of a fresh SIGN pin, apply D45 recovery pattern preemptively — warmup-ping first (ultra-short "confirm ready" probe), then batched titles-only SIGN 2-3 findings per prompt. D48 stability-probe gate CODIFICATION-READY at 3-arc use if Group 1500 replicates. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.
- **Non-standard pa_chat.py invocation for fresh SIGN pin:** `tools/pa_local.sh` hardcodes `--conversation` — for fresh SIGN pin, use direct pa_chat.py invocation with env vars: `PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-token> .venv/bin/python tools/pa_chat.py "$(cat /tmp/msg.txt)" --tools --conversation <fresh-pin-id>` — write prompt to file first to avoid shell backtick interpretation.

## Repo state at next-session open

- **Branch state (at S1500 close, before merge):** `docs/session-1500-sports-arc-open` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1500 handoff at `docs/handoffs/SESSION_1500_SPORTS_ARC_OPEN.md`. Prior handoffs: SESSION_1499 (Revenue arc-close canonical summary); SESSION_1406 (Cat F final); SESSION_1405 (Cat E); SESSION_1404 (Cat D); SESSION_1403 (Cat C); SESSION_1402 (Cat B); SESSION_1401 (Cat A); SESSION_1400 (Group 1400 arc open); SESSION_1399 (Group 1300 canonical summary — first xx99); SESSION_1300-SESSION_1305 (Group 1300 children).
- **ARCHITECTURE_INDEX version:** v27 (bumped this session with §1.30 S1500 parent scoping + §8 timeline S1500 row + v27 preamble). Next bump at S1501 close (v27 → v28 for §1.31 Cat A child audit).
- **OPEN_ARCS state:** Group 1500 row moved Not-started → In-progress this session. Group 1400 remains in Closed section. Next arc-open (post-Group-1500 close) populates queue with Group 1600 Content / Deliverables / Publishing default lean.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1500 artifact set is on `main` — if yes, next session branches off `main`
- [ ] Run post-merge 5-step docs cascade if not yet run per `feedback_docs_cascade_at_every_close.md`
- [ ] Chris ratifies P1 kickoff: default lean is `Continue research group 1500: Category A — Sports Odds Ingestion & Normalization` (S1501)
- [ ] Execute P1 audit per playbook §11.2 20-section template + §13 6-parallel-Explore sweep + §5 pre-brief mini-schema application (Q3 fold requirement)
- [ ] Route Full SIGN to fresh isolation pin per playbook §15 with D48 preemptive stability-probe gate

## Reference — where to look

- **Group 1500 parent scoping doc:** `docs/research/domains/sports/1500_sports_domain_scoping.md` — arc-open scoping + Phase 0 F.i/F.ii/F.iii second application UNCHANGED + candidate subdomain taxonomy A-F + child mission sequence P1-P7
- **Group 1400 canonical summary:** `docs/research/domains/revenue/1499_revenue_canonical_summary.md` — arc-close synthesis + T1-T10 follow-on queue + Employee OS ownership resolution (post-arc phase inheritance)
- **Group 1400 parent scoping doc:** `docs/research/domains/revenue/1400_revenue_domain_scoping.md` (precedent for Phase 0 F.i/F.ii/F.iii first application)
- **Group 1300 canonical summary:** `docs/research/domains/memory/1399_memory_canonical_summary.md` (first formal xx99 canonical summary — precedent for playbook §11.3 §10 template)
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§9 canonical questions + §11.1 parent template + §11.2 child template + §11.3 xx99 canonical summary template + §13 evidence sweep + §15 SIGN + §16 arc-close + §17 graduation + §22 next-arc queue)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v27:** `docs/research/ARCHITECTURE_INDEX.md` — S1500 §1.30 + §8 timeline + v27 preamble
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1500 In-progress section
- **AUDIT_FINDINGS.md #12:** canonical Celery deferred-by-policy list
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`

## Doctor warnings to expect

- Inventory freshness (unchanged this session — parent scoping only)
- Handoff numbering continuity — S1500 continues arc-numbering convention (S1300 arc-open + S1301-S1305 children + S1399 canonical; S1400 arc-open + S1401-S1406 children + S1499 canonical; S1500 arc-open + S1501-S1506 children + S1599 canonical)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; S1500 doesn't touch narrative anchor)
- Docs cascade — run 5-step cascade + `build_docs_provenance` after S1500 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold)
- Group 1400 post-arc §7 anchor-updates still pending (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499)
- `sports_odds` structural gap CONFIRMED at code level (S1274 §14 Finding #6); Category F evidence plan owed at S1506
