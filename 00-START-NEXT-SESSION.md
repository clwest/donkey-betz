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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1504 close:**

- **ACTIVE ARC PIN:** `pa-791b3db549a64e54` (Group 1500 arc pin; minted at S1500 open, retained per playbook §16 for entire Group 1500 arc — carries P5-P6 sequence + P7 xx99).
- **`tools/pa_local.sh:128` already at `pa-791b3db549a64e54`** — no line-128 rotation needed at S1505 open.
- **Retired at S1504 close:** SIGN isolation pin `pa-af2bf7f2d1a0ef61` (S1504 Full SIGN pin; retired via `session_tool.retire` at S1504 close — `updated_count: 5, retired: true`).
- **Retired at S1503 close:** SIGN isolation pin `pa-8ce5f949bed5e093` (S1503 Full SIGN pin).
- **Retired at S1502 close:** SIGN isolation pin `pa-64c019d7e6685d31` (S1502 Full SIGN pin).
- **Retired at S1501 close:** SIGN isolation pin `pa-a39069230ab64450` (S1501 Full SIGN pin).
- **Retired at S1500 open:** Group 1400 arc pin `pa-34d43795e1b24bd3` (was already retired at S1499 close per D53).
- **Retired at S1499 close:** `pa-877f1919efaa48e4` (S1499 SIGN isolation pin).
- **Retired at S1406 close:** `pa-8660ea7cfecd4bc6`.
- **Retired earlier:** `pa-4bdd5ad264674ce8` + `pa-637331c5f9574a10` (S1405); `pa-87ee24cd0d3947ce` (S1404); `pa-fba0c4c81fba4922` (S1403); `pa-4a0a28edcb7a45ec` (S1402); `pa-16d8b24d30e7a7d8` (S1401); `pa-aa54193f240f4846` + `pa-4fc3329d0db6484f` (S1399 Group 1300 arc-close).

Use `tools/pa_local.sh` for all chats — line 128 already pointing at active Group 1500 arc pin.

## READ THIS SECOND — S1504 CAT D LANDED; S1505 CAT E QUEUED NEXT

Session 1504 shipped the fourth child audit under Group 1500 Sports/DBAO/Intelligence: **Category D Sports Betting Content Pipeline Audit**. Doc landed at `docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md` (1078 lines after F1-F11 folds, `status: active`, `category: child_audit`, `subdomain_category: D`, playbook §11.2 20-section template + six parallel Explore sub-agents per §13 + parent-Claude verifier-loop per §14 on 5 load-bearing claims — 4 verifier-loop corrections applied pre-SIGN — plus parent-Claude Rigby ORM probe BEFORE draft integration on 3 Cat D task beat states — **second library application** of S1503-first-applied BEFORE-SIGN pattern).

**Fourth sibling to apply D62 = (a) 4-item pre-brief mini-schema per surface upfront** — extends D62 propagation-upfront validation from S1503 3-sibling pattern to S1504 4-sibling pattern by producing consistent evidence shape (§4.4 / §5.6 / §6.6 / §8.6 / §15.16) without schema drift.

**Rigby Full SIGN cycle 1 SIGN-with-edits at Medium-High confidence** via fresh isolation pin `pa-af2bf7f2d1a0ef61` — 4 substantive SIGN turns (1 warmup + 3 SIGN batches Q1-Q3 + Q4-Q6 + Q7-Q9); **zero worker-instability observed across all 4 turns — D48 7th arm matches S1503 6th-arm cleanest arm pattern**. **First library child audit where Rigby SIGN cycle 1 batch 1 required verdict-text re-request** — initial response was tool-heavy (10 `repo_tool.search` calls verifying claims) without substantive verdict summary; recovery via one-line "please give me the Q1/Q2/Q3 verdict text" ping delivered normally. Recovery pattern candidate for playbook v3 §15 alongside D45 titles-only recovery pattern. **F1-F11 folds landed at commit-time** (F1 §1 Finding 6 + §7.2 `run_all_desks_intelligence` cross-domain writer bridge elevation; F2 §5.1 + §7.6 + §13.2 SportsContentContextBuilder HOT-PATH-CHOKE-POINT reframe from TRANSITIVELY-COUPLED; F3 §4.2 LegacySpiderData shared-table Cat B/C bridge surface risk elevation; F4 §1 Finding 9 zero test coverage promoted MED-HIGH → HIGH + §15.12 → CRITICAL + §19.1 #3; F5 §15.5 digest idempotency PRE-RESTORE-BEAT gate promoted MED-HIGH → CRITICAL + §19.1 #2; F6 §1 Finding 5 + §14.2 + §15.3 docstring cadence drift demoted HIGH → MED; F7 §1 exec-summary risk ordering strengthened; F8 §19.1 CRITICAL tier reordered to 5-item dependency ordering; F9 §13 maturity verdict tightened to distinguish WORKING (fire-verified) from PRESENT + SCHEDULED (runtime not verified beyond Celery SUCCESS counts) + §19.2 #8 new operational instrumentation task; F10 §1 exec-summary opening rewritten from "owed to xx99" placeholder to concrete handoff target; F11 §14.4 + §14.5 + §19.2 #6 + §19.4 #14-15 "no owning bridge implementation was located" clarifier). **Cycle 2 SIGN-clean at High confidence anticipated post-fold-land** — pattern-consistent with S1501 + S1502 + S1503 cycle-1-predict-cycle-2 accuracy. **Do-not-regress notes for PR:** preserve §2.1 Cat D contract statement + preserve F1-F11 folds per §20.8 detailed enumeration.

**D48 preemptive stability-probe gate 7th-arm CODIFICATION-READY** for playbook v3 §15 per S1405+S1406+S1499+S1501+S1502+S1503+S1504 7-arc pattern — further strengthens immediate codification recommendation from S1503 6-arc threshold. **Recommendation:** xx99 (S1599) §10.2 codifies D48 into playbook v3 §15 alongside D45 titles-only recovery + provenance-stamp ORM probe + parent-Claude 12/12 checkpoint precedent + parent-Claude Rigby ORM probe BEFORE-SIGN pattern (S1503 first-applied, S1504 second-applied — 2-arc evidence base) + **new S1504 addition: SIGN cycle 1 batch 1 verdict-text re-request recovery pattern**.

**Load-bearing findings owed to xx99 (S1599) via Cat F evidence plan (10):**

1. **CRITICAL operational — `daily_betting_digest` unscheduled AND zero-fire (biggest per Rigby SIGN cycle 1 Q6).** Grep of `core/celery.py` returns zero + grep of `docs/AUDIT_FINDINGS.md` §12 canonical deferred list returns zero + Rigby ORM probe returned 0 fires in 30d. Docstring at `core/tasks_financial.py:1912` claims "Scheduled to run at 8 AM MST daily" — phantom behavior. S1503 §14.1 pattern replicated in Cat D scope.

2. **CRITICAL architectural — `SportsBettingBrief` write-only-and-forgotten.** Two writer sites (`core/tasks_content.py:3150` Cat D + `core/tasks.py:12187` Session 1000 multi-desk), zero reader sites (grep-verified pre-SIGN). REST endpoint `get_betting_brief` at `core/views_odds_sports.py:3237` (`AllowAny`) bypasses persisted model + calls coordinator directly. NEW pattern class for the arc.

3. **HIGH POSTURE-DECISION-PENDING per S1502 F3 / S1503 F9 precedent — Zero Cat D → Cat B outcome-feedback loop.** F11 fold clarifier "no owning bridge implementation was located."

4. **HIGH POSTURE-DECISION-PENDING per S1502 F2 / S1503 §14.3 precedent — Zero Cat D → Signal Engine emission.** F11 fold clarifier.

5. **MED (F6 fold demote from HIGH) — `generate_daily_betting_brief` docstring "twice daily" vs runtime once-daily.**

6. **MED-HIGH operational + architectural (F1 fold elevation) — Cross-domain writer bridge to `SportsBettingBrief` via `run_all_desks_intelligence` without dedup.** Session 1000 multi-desk pipeline as second writer path.

7. **MED architectural — Discord `/odds` + digest + intelligence-hook BYPASS `SportsContentContextBuilder`.** Two disconnected content-generation surfaces (F2 fold reframe HOT-PATH-CHOKE-POINT for content/PA + BYPASSED for Discord fast path).

8. **MED POSTURE-DECISION-PENDING per S1502 F4 precedent — Zero Cat D → Memory Domain (S1300) bridge.** F11 fold clarifier.

9. **HIGH → CRITICAL (F4 fold promote) — Zero dedicated test coverage as reliability-risk multiplier.**

10. **MED operational — No PA tool for triggering brief / digest / manual regeneration.**

**Cat D maturity verdict** per §13 F9 fold: **PARTIAL (mixed — WORKING (beat + 30d fire evidence) at brief-generation; PRESENT + SCHEDULED (runtime not verified beyond Celery SUCCESS counts) at intelligence-hook + `/odds`; BROKEN/DORMANT at digest; WRITE-ONLY-FORGOTTEN at brief-persistence; HOT-PATH-CHOKE-POINT for content/PA — BYPASSED by Cat D Discord fast path)** — fourth distinguishing maturity shape after S1501 "WORKING (fragile contract) at ingestion, PARTIAL at normalization" + S1502 "PARTIAL (armed but under-instrumented)" + S1503 "PARTIAL (armed but zero-fire)".

**Session close artifacts committed at S1504 close:**

```
docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md  [new; 1078 lines; SIGN-with-edits cycle 1 folds landed at Medium-High confidence]
docs/research/ARCHITECTURE_INDEX.md                                         [modified — v30 → v31; §1.34 + §8 timeline S1504 row + v31 preamble]
docs/research/OPEN_ARCS.md                                                  [modified — current-child field advanced; Recent reconciliations 2026-07-02 (S1504 close) entry]
docs/handoffs/SESSION_1504_SPORTS_CAT_D_AUDIT.md                            [new — S1504 handoff]
00-START-NEXT-SESSION.md                                                    [modified — this file; P5 default lean advanced to S1505]
```

Handoff: `docs/handoffs/SESSION_1504_SPORTS_CAT_D_AUDIT.md`.

### NEXT-SESSION MISSION — CATEGORY E CHILD AUDIT (S1505)

**Recommended path: `Continue research group 1500: Category E — Frontend Sports Surface`**.

Fifth child audit under Group 1500. Per parent §5 "Ordering rationale": Cat E depends on Cat A+B+C+D data + prediction + content surfaces (previously landed) — 9-tab BettingPage layout + `/betting` route + WebSocket channel investigation + interaction contract with Cat A/B/C/D. Constrains Category F cross-domain integration posture criteria.

**Cat E scope per parent §3.E:**
- `/betting` route (`frontend/src/App.tsx:89`)
- `BettingPage.tsx` 9-tab layout (`frontend/src/pages/BettingPage.tsx:16-26`) — Hub, Today's Games, Top Plays, Sharp Action, Arbitrage, Watching, Live Odds, My Wagers, Records
- API integration to Categories A–D backend surfaces (5 REST endpoints at `/api/v1/betting/*` all `AllowAny` per Cat D §3.3)
- WebSocket channel investigation (`/ws/dbao/` is DBAO metrics channel per parent §3.E, not tab-scoped realtime; tab-level realtime update behavior UNKNOWN)
- Interaction contract with Cat A/B/C/D surfaces

**Load-bearing observations to inherit from S1504:**
- Cat D §2.1 Cat D contract statement — 10 items Cat D does NOT guarantee. S1505 verifies whether BettingPage consumers rely on any Cat D non-guaranteed behaviors (especially phantom digest schedule + write-only-forgotten SportsBettingBrief + zero Signal Engine emission).
- Cat D §3.3 5 REST endpoints at `/api/v1/betting/*` uniformly `AllowAny` (matches S1503 §14.7 pattern) — S1505 verifies whether frontend enforces client-side auth or relies on server AllowAny.
- Cat D §5.1 F2-fold HOT-PATH-CHOKE-POINT observation (`SportsContentContextBuilder` for content/PA + BYPASSED by Discord fast path) — S1505 checks whether BettingPage frontend adds a third content-generation path or reuses one of these.
- Cat D §14.5 Signal Engine emission absence — S1505 checks whether BettingPage reads `SignalCluster` or is coupled to Discord/DB directly.
- Cat D §19.2 #7 operational cadence study `run_all_desks_intelligence` beat state — deferred to S1505 or S1506 investigation.
- Cat D §7.1 F1-fold explicit call-chain block for `generate_daily_betting_brief` — pattern candidate to replicate for BettingPage fetch → API → coordinator call-chain.

Session flow at S1505 open:

1. `context-kit orient` (session-open protocol).
2. Confirm `service_context: local` via `platform_config_tool overview` on arc pin `pa-791b3db549a64e54`.
3. Check if S1504 artifact set merged to `main` between sessions.
4. If not yet merged: complete Chris merge + PR merge.
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
6. Chris ratifies P5 kickoff via `Continue research group 1500: Category E` (short command).
7. Draft P5 audit at `docs/research/domains/sports/1505_sports_frontend_surface_audit.md` per playbook §11.2 20-section template.
8. Launch 6 parallel Explore sub-agents per playbook §13 evidence sweep for Category E scope only.
9. **Apply §5 pre-brief 4-item mini-schema per surface** per D62 = (a) propagate upfront (Chris-ratified S1501 open). Cite S1501 §4.6 + S1502 §4.8 + S1503 §4.4 + S1504 §4.4 as sibling exemplars (**four-sibling exemplar pattern now**).
10. Answer all 28 canonical questions (§9) — cite, reference, or `UNKNOWN`.
11. Route to Rigby per §15 stage table — Full SIGN on child audits; fresh SIGN isolation pin per §15; **D48 preemptive stability-probe gate — 7th-arm CODIFICATION-READY at S1504 close; S1505 would be 8th arm continuing the pattern** (recommended for xx99 codification at S1599 with 8-arc evidence base).
12. Fold SIGN-with-edits into P5 doc.
13. Session close: handoff + PR + docs cascade.

**Not next:** Category F (P6). It runs LAST.

**Also queued at future sessions:**
- S1506 Category F Cross-Domain Integration Lens & Posture Decision Framing (D57 sequence — LAST child before xx99);
- S1599 xx99 canonical summary after P1-P6 land (third application of playbook §11.3 §10 meta-methodology template after S1399 first + S1499 second);
- Subsequent PRs from Group 1400 §7 anchor-updates (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499);
- CLAUDE.md 3-employees narrative anchor drift (still flagged); `verify_doc_claims --only-drift` verifier subsequent PR.

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1504 artifact set is on `main` between sessions
4. If not yet merged: Chris merge + PR merge
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
6. Chris ratifies P5 kickoff (S1505 Category E default lean per parent §5 sequence)
7. Execute P5 audit per playbook §11.2 + §13 + §5 pre-brief schema propagation (D62 continuation with 4 sibling exemplars: S1501 §4.6 + S1502 §4.8 + S1503 §4.4 + S1504 §4.4)

---

## PA / Rigby context

- **Arc pin at session start:** `pa-791b3db549a64e54` (Group 1500 arc pin; already active in `tools/pa_local.sh:128`; carries Group 1500 arc-open context through P5-P7 sequence per playbook §16 retain rule).
- **S1504 SIGN routing:** Full SIGN cycle 1 ran on fresh isolation pin `pa-af2bf7f2d1a0ef61` per playbook §15 stage table (retired at S1504 close via `session_tool.retire` — `updated_count: 5, retired: true`); cycle 2 SIGN-clean anticipated post-fold-land at PR-merge or Chris-invoked follow-up.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (S1405+S1406+S1499+S1501+S1502+S1503+S1504 7-session confirmed — D48 CODIFICATION-READY at 7-arc threshold, cleanest arms at S1503+S1504):** if Rigby generic-errors on turn 1 of a fresh SIGN pin, apply D45 recovery pattern preemptively — warmup-ping first (ultra-short "confirm ready" probe), then batched titles-only SIGN 2-3 findings per prompt. S1504 marked the 7-arc threshold with entirely clean stability probe + zero worker-instability across 4 substantive SIGN turns; xx99 §10.2 codifies into playbook v3 §15 with strengthened 7-arc evidence base. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.
- **Non-standard pa_chat.py invocation for fresh SIGN pin:** `tools/pa_local.sh` hardcodes `--conversation` — for fresh SIGN pin, use direct pa_chat.py invocation with env vars: `PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-token> .venv/bin/python tools/pa_chat.py "$(cat /tmp/msg.txt)" --tools --conversation <fresh-pin-id>` — write prompt to file first to avoid shell backtick interpretation.
- **New at S1504: SIGN cycle 1 batch 1 verdict-text re-request recovery pattern.** If Rigby's initial batch 1 response is tool-heavy (many `repo_tool.search` verifications) without substantive verdict text summary, recovery is one-line "please give me the Q1/Q2/Q3 verdict text" ping — she delivers verdict text normally on the follow-up. This is distinct from D45 titles-only recovery (which addresses worker-instability generic-error on turn 1); this is a "verbose verification-only response" recovery. First applied S1504; pattern candidate for playbook v3 §15 addition.
- **Continued at S1504: Rigby ORM probe as parent-Claude verifier-loop tool BEFORE draft integration** — second library application (S1503 first-applied). For CRITICAL load-bearing claims (especially zero-fire task classifications, PeriodicTask absence, dead-code claims), route ORM probe via Rigby (`scheduled_tasks_tool` + `ops_tool.celery_task_history`) BEFORE writing the claim into the draft. 2-arc evidence base at S1504 close; would strengthen to 3-arc evidence base at S1505 open if applied to Cat E surfaces (though Cat E has less beat-schedule scope — pattern likely doesn't generalize to frontend audits).

## Repo state at next-session open

- **Branch state (at S1504 close, before merge):** `docs/session-1504-sports-cat-d-audit` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1504 handoff at `docs/handoffs/SESSION_1504_SPORTS_CAT_D_AUDIT.md`. Prior handoffs: SESSION_1503 (Sports Cat C); SESSION_1502 (Sports Cat B); SESSION_1501 (Sports Cat A); SESSION_1500 (Sports arc open); SESSION_1499 (Revenue arc-close canonical summary); SESSION_1406 (Cat F final); SESSION_1405 (Cat E); SESSION_1404 (Cat D); SESSION_1403 (Cat C); SESSION_1402 (Cat B); SESSION_1401 (Cat A); SESSION_1400 (Group 1400 arc open); SESSION_1399 (Group 1300 canonical summary — first xx99); SESSION_1300-SESSION_1305 (Group 1300 children).
- **ARCHITECTURE_INDEX version:** v31 (bumped this session with §1.34 S1504 Cat D audit + §8 timeline S1504 row + v31 preamble). Next bump at S1505 close (v31 → v32 for §1.35 Cat E child audit).
- **OPEN_ARCS state:** Group 1500 row current-child field advanced to "S1504 SIGN-with-edits cycle 1 (F1-F11 folds landed, cycle 2 anticipated, commit-gated) + S1505 queued next"; row remains In-progress. Group 1400 remains in Closed section. Next arc-open (post-Group-1500 close) populates queue with Group 1600 Content / Deliverables / Publishing default lean.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1504 artifact set is on `main` — if yes, next session branches off `main`
- [ ] Run post-merge 4-step docs cascade + `build_docs_provenance` if not yet run per `feedback_docs_cascade_at_every_close.md`
- [ ] Chris ratifies P5 kickoff: default lean is `Continue research group 1500: Category E — Frontend Sports Surface` (S1505)
- [ ] Execute P5 audit per playbook §11.2 20-section template + §13 6-parallel-Explore sweep + §5 pre-brief mini-schema application (D62 continuation with 4 sibling exemplars)
- [ ] Route Full SIGN to fresh isolation pin per playbook §15 with D48 preemptive stability-probe gate (8th-arm reinforcement of CODIFICATION-READY 7-arc pattern)

## Reference — where to look

- **S1504 Cat D audit doc:** `docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md` — 20-section child audit + §2.1 Cat D contract statement (5 guarantees + 10 non-guarantees) + §7.1 F1-analog explicit call-chain block for `generate_daily_betting_brief` + §14 drift matrix + §15 debt matrix + §19 F8-fold CRITICAL-tier reordered ranked future-research queue + §20.5 Rigby ORM probe log + §20.8 F1-F11 SIGN fold notes + Rigby cycle 1 verdict verbatim
- **S1503 Cat C audit doc:** `docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md` — sibling exemplar for D62 mini-schema + F1 explicit call-chain block + F9 "bridge owns learning writes" default posture statement precedent + §14.1 CRITICAL zero-fire pattern + §15.14 F7 fold PRE-RESTORE-BEAT gate concept
- **S1502 Cat B audit doc:** `docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md` — sibling exemplar for D62 mini-schema + F1 explicit call-chain block + F3/F2/F4 posture-decision-pending framing precedents
- **S1501 Cat A audit doc:** `docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md` — sibling exemplar; §2.1 Cat A contract statement is Cat D's load-bearing input via Cat B
- **Group 1500 parent scoping doc:** `docs/research/domains/sports/1500_sports_domain_scoping.md` — arc-open scoping + Phase 0 F.i/F.ii/F.iii second application UNCHANGED + candidate subdomain taxonomy A-F + child mission sequence P1-P7 + D62 = (a) 4-item mini-schema propagation directive
- **Group 1400 canonical summary:** `docs/research/domains/revenue/1499_revenue_canonical_summary.md` — arc-close synthesis + T1-T10 follow-on queue + Employee OS ownership resolution (post-arc phase inheritance)
- **Group 1300 canonical summary:** `docs/research/domains/memory/1399_memory_canonical_summary.md` (first formal xx99 canonical summary — precedent for playbook §11.3 §10 template)
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§9 canonical questions + §11.1 parent template + §11.2 child template + §11.3 xx99 canonical summary template + §13 evidence sweep + §15 SIGN + §16 arc-close + §17 graduation + §22 next-arc queue)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v31:** `docs/research/ARCHITECTURE_INDEX.md` — S1504 §1.34 + §8 timeline S1504 row + v31 preamble
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1500 In-progress section with S1504 SIGN-with-edits current-child field
- **AUDIT_FINDINGS.md #12:** canonical Celery deferred-by-policy list (`daily_betting_digest` grep-verified NOT on list — load-bearing for S1504 §14.1 CRITICAL classification; pattern reusable for Cat E if any frontend polling task has similar drift shape)
- **CELERY_AUDIT.md:** canonical Celery inventory
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`

## Doctor warnings to expect

- Inventory freshness (unchanged this session — child audit only, no runtime changes)
- Handoff numbering continuity — S1504 continues arc-numbering convention (S1300 arc-open + S1301-S1305 children + S1399 canonical; S1400 arc-open + S1401-S1406 children + S1499 canonical; S1500 arc-open + S1501-S1506 children + S1599 canonical)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; S1504 doesn't touch narrative anchor)
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1504 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold)
- Group 1400 post-arc §7 anchor-updates still pending (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499)
- `sports_odds` structural gap CONFIRMED at code level AND extended in scope by S1502 §14.3 (Cat B consumer side) AND extended further by S1503 §14.3 (Cat C consumer side) AND extended further by S1504 §14.5 (Cat D consumer side — zero SignalCluster emissions from top-plays / sharp-signals / arbitrage); Category F evidence plan owed at S1506
- **`daily_betting_digest` CRITICAL zero-fire status** — flagged at S1504 §14.1 but NOT remediated by this audit (research not implementation). Post-arc follow-on PR needed per S1504 §19.1 CRITICAL tier: (i) restore beat entry with correct cadence OR document intentional deferral in `docs/AUDIT_FINDINGS.md` §12; (ii) idempotency + replay safety hardening as PRE-RESTORE-BEAT GATE — must land BEFORE beat restoration per F5 fold (matches S1503 §15.14 F7 pattern).
- **`SportsBettingBrief` CRITICAL write-only-and-forgotten status** — flagged at S1504 §14.3 but NOT remediated by this audit. Post-arc follow-on PR needed: either (a) build reader consumer (dashboard / API / PA tool that queries persisted briefs), or (b) remove the persistence path and document "brief output is Discord + REST ephemeral only." Currently 2 writers + 0 readers is dead-weight state.
- **D48 preemptive stability-probe gate 7th-arm CODIFICATION-READY** — S1505 SIGN cycle would be 8th arm; xx99 (S1599) §10.2 owns eventual playbook v3 §15 codification recommendation with strengthened 7-arc evidence base + parent-Claude Rigby ORM probe BEFORE-SIGN pattern (2-arc evidence base at S1504 close: S1503 first-applied + S1504 second-applied) + new S1504 addition: SIGN cycle 1 batch 1 verdict-text re-request recovery pattern (candidate for playbook v3 §15 as distinct from D45 titles-only worker-instability recovery).
