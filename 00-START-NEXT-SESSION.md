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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1599 close:**

- **NO ACTIVE ARC PIN** — Group 1500 arc pin `pa-791b3db549a64e54` retired at S1599 close per playbook §16 D53 arc-close discipline (matches S1499 Revenue arc-close pattern). Next arc pin will be minted at Group 1600 open (default lean per playbook §22) via `session_tool.create_fresh` — OR at whatever Chris-selected next arc opens.
- **`tools/pa_local.sh:128` needs update** at next-arc open — rotate from retired Group 1500 arc pin `pa-791b3db549a64e54` to newly-minted next-arc pin.
- **Retired at S1599 close:** Group 1500 arc pin `pa-791b3db549a64e54` (retained through S1500 → S1501 → S1502 → S1503 → S1504 → S1505 → S1506 → S1599 per playbook §16 arc-continuity rule; retired at arc-close via `session_tool.retire`).
- **Retired at S1506 close:** SIGN isolation pin `pa-c2cdbd5c0b8c451b`.
- **Retired at S1505 close:** SIGN isolation pin `pa-546de7ebe8c8b885`.
- **Retired at S1504 close:** SIGN isolation pin `pa-af2bf7f2d1a0ef61`.
- **Retired at S1503 close:** SIGN isolation pin `pa-8ce5f949bed5e093`.
- **Retired at S1502 close:** SIGN isolation pin `pa-64c019d7e6685d31`.
- **Retired at S1501 close:** SIGN isolation pin `pa-a39069230ab64450`.
- **Retired at S1499 close:** Group 1400 arc pin `pa-34d43795e1b24bd3` + SIGN isolation pin `pa-877f1919efaa48e4` (S1499 Full SIGN pin).
- **Retired earlier:** `pa-8660ea7cfecd4bc6` (S1406); `pa-4bdd5ad264674ce8` + `pa-637331c5f9574a10` (S1405); `pa-87ee24cd0d3947ce` (S1404); `pa-fba0c4c81fba4922` (S1403); `pa-4a0a28edcb7a45ec` (S1402); `pa-16d8b24d30e7a7d8` (S1401); `pa-aa54193f240f4846` + `pa-4fc3329d0db6484f` (S1399 Group 1300 arc-close).

Use `tools/pa_local.sh` for all chats — but rotate line 128 at next-arc open.

## READ THIS SECOND — S1599 XX99 CANONICAL SUMMARY LANDED; GROUP 1500 ARC CLOSED

Session 1599 shipped the **Group 1500 Sports/DBAO/Intelligence arc-close canonical summary** at `docs/research/domains/sports/1599_sports_canonical_summary.md` (2241 lines; `status: active`, `category: canonical_summary`, `child_slot: P7`, `authority: research`; playbook §11.3 12-section template + §10 "What This Research Taught Us About How to Do Research" **third application** after S1399 first + S1499 second per Chris directive S1399 close 2026-07-01).

**Load-bearing deliverables shipped at S1599:**

- **§5 D59 posture-decision evidence brief** with **explicit "Chris-gated selection" tag** — 7 integration criteria A1-A7 + 7 island criteria B1-B7 + 4 cross-cutting C1-C4 + failure-mode table D + cost asymmetry summary E + F2-fold scoring rubric F applied uniformly across P1-P6 evidence corpus. **Aggregate current-state score at HEAD `5a8d3d75`: ALL 22 criteria score FAIL** — load-bearing observation "BOTH postures require substantive investment; neither is a default." Chris post-arc ADR judges which set of PASS-transitions is preferable given cost-asymmetry summary + failure-modes table.
- **§3.4 Four-Axis Compound-Maturity Shape** NEW arc-level maturity framing: (1) DBAO product-line materialization axis = NAMING-CONVENTION-WITHOUT-MATERIALIZATION; (2) Intelligence surface axis = flag DECLARED-GATES-NOTHING + engine LATENT-ZERO-FIRE + REST/frontend DOMAIN-NEUTRAL; (3) Discord sports surface axis = read HOT-PATH-CHOKE-BYPASS + write WORKING + digest DUAL-COORDINATOR-BYPASS; (4) Cross-domain feedback surface axis = DECOUPLED-VERIFICATION-SYSTEMS + PARTIAL-LEARNING-BRIDGE + zero SignalCluster emission.
- **§3.2 Sports Domain Lifecycle Traceability Table** per parent §12.5 F.iii deliverable — 8 stages including fixture/entity identity resolution per Rigby SIGN cycle 1 Q8 fold (UNKNOWN owner + MISSING resolver); 1 stage MISSING (Stage 8 Signal Aggregation — 6-arc consumer-side pattern COMPLETED gap); 5 stages LIVE-BUT-DRIFTING; 1 stage IMPLICIT.
- **§4 Thirteen cross-cutting pattern classes** — 5 NEW at S1506 (P1-P5) + 5 NEW at other categories (P6-P10) + 3 INHERITED (P11 6-arc COMPLETED + P12 5-arc + P13 2-arc).
- **§10 meta-methodology third application** with **§12.4 discriminative-value criterion check: 4 of 4 evidence types satisfied → playbook v3 §11.1 template promotion TRIGGERS.**
- **§10.2 Playbook v3 candidate list (6):** D48 preemptive stability-probe gate 9-arc CODIFICATION-READY → v3 §15; D62=(a) 6-sibling exemplar pattern → v3 §5; F2-fold scoring rubric → v3 §11.3 §5; BEFORE-SIGN Rigby ORM probe → conditional v3 §14; S1504 verdict-text re-request recovery → v3 §15 preventive framing rule; S1505 Rigby Q8 grep-verified confidence-upgrade → v3 §15 SIGN-time verifier-loop tool.
- **§8 T1-T10 follow-on queue with visual blocking dependency graph** — T1 Chris-gated ADRs + CRITICAL remediation sequences; T2 12 design-preparation tracks; T3 6 Employee OS + delegated; T4 11 cleanup PRs; T5 6 optional.
- **§7 Anchor-update recommendations** — `PLATFORM_INVENTORY.md` §3.10 subdivision + DBAO subgroup conditional on T1.b; `PLATFORM_WHAT_IT_IS.md` Sports narrative refresh; NEW `docs/topics/sports-betting.md` (C2 cross-cutting gate); `.github/CODEOWNERS` 6 sports runtime files (post-arc T3).

**Session close artifacts committed at S1599 close:**

```
docs/research/domains/sports/1599_sports_canonical_summary.md              [new; 2241 lines; playbook §11.3 12-section template + §10 meta-methodology third application]
docs/research/ARCHITECTURE_INDEX.md                                        [modified — v33 → v34; §1.37 registration + §8 timeline S1599 arc-close row + frontmatter v34 preamble]
docs/research/OPEN_ARCS.md                                                 [modified — Group 1500 In-progress → Closed section; last_updated header refresh]
docs/handoffs/SESSION_1599_SPORTS_CANONICAL_SUMMARY.md                     [new — S1599 handoff]
00-START-NEXT-SESSION.md                                                   [modified — this file]
```

Handoff: `docs/handoffs/SESSION_1599_SPORTS_CANONICAL_SUMMARY.md`.

### NEXT-SESSION MISSION — CHRIS-GATED ADR + T1 REMEDIATION OR GROUP 1600 OPEN

**Recommended paths** (per playbook §22 domain queue + T1 blocker sequencing):

1. **Chris-gated post-arc ADRs (T1 highest priority per D59 + Group 1400 precedent):**
   - **R.SPORTS.POSTURE ADR** — integration vs island. Consumes xx99 §5 posture-decision brief verbatim + §5.F F2-fold scoring rubric. Blocks 12 T2 tracks + 3 T3 tracks + 2 T4 tracks. Owner: Chris.
   - **R.DBAO.CODENAME ADR** — materialize | demote | archive. D61 parked candidate. Coupled to R.SPORTS.POSTURE (integration posture implies materialize; island posture implies materialize as product-line boundary; neither posture implies archive). Owner: Chris.

2. **T1 CRITICAL remediation sequences** (parallelizable with ADRs):
   - **R.C1 verify_betting_outcomes beat-restoration** ← R.C2 pre-restore-beat concurrency-safety hardening.
   - **R.D1 daily_betting_digest beat-restoration OR §12 deferred-list entry** ← R.D2 idempotency hardening.
   - **R.D3 zero-test-coverage as reliability multiplier** (parallelizable).

3. **Group 1600 arc open (playbook §22 default lean):** Content / Deliverables / Publishing arc. Follows Group 1500 close per playbook §22 domain queue. Would open with parent scoping + Chris's Phase 0 F.i/F.ii/F.iii methodology **third application** per D58 two-triggers pattern (if playbook v3 promotion triggers first, methodology per v3 template).

4. **Playbook v3 §11.1 promotion session:** consumes xx99 §10.2 6-candidate codify list. Codification implementation is a separate post-arc session; xx99 flagged candidates; promotion session decides which land at v3.

**Not next:** implementation PRs from any T2 track (posture-tied blockers); DBAO artifact cleanup PRs (T4 coupled to T1.b); Discord surface refactor (T2 coupled to T1.a); any T3 Employee OS + delegated arc work.

**Session flow at next-session open:**

1. `context-kit orient` (session-open protocol per memory rule).
2. Confirm `service_context: local` via `platform_config_tool overview` on... **no arc pin active** — either Rigby session default or mint fresh pin for next arc (integration posture ADR / Group 1600 open / R.C1 remediation etc.).
3. Check if S1599 artifact set merged to `main` between sessions.
4. If not yet merged: complete Chris merge + PR merge.
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
6. Chris ratifies next-session mission — options ordered by T1 priority:
   - (a) R.SPORTS.POSTURE ADR (highest — blocks 12 T2 tracks).
   - (b) R.DBAO.CODENAME ADR (coupled to (a)).
   - (c) T1 CRITICAL remediation sequences (parallelizable with ADRs; each requires PR + tests).
   - (d) Group 1600 arc open (parent scoping session per §22 default lean).
   - (e) Playbook v3 §11.1 promotion session.

**FIRST THING next session open:**

1. `context-kit orient`.
2. Confirm `service_context: local` via `platform_config_tool overview`.
3. Check if S1599 artifact set is on `main`.
4. If not yet merged: Chris merge + PR merge.
5. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md` (S1599 arc-close docs cascade discipline).
6. Chris ratifies next-session mission.

---

## PA / Rigby context

- **Arc pin at session start:** **NONE ACTIVE** — Group 1500 arc pin `pa-791b3db549a64e54` retired at S1599 close per D53. Next-arc open will mint fresh pin via `session_tool.create_fresh` + rotate `tools/pa_local.sh:128`.
- **S1599 SIGN routing:** Rigby Full SIGN cycle 1 **PENDING** on fresh isolation pin owed at pre-SIGN step per playbook §15 Q10-Q13 canonical-summary pressure-test. Preemptive stability probe (warmup-ping + `cockpit_tool.worker_health` verify 4 workers online) per D48 pattern. **D48 preemptive stability-probe gate 10th arm** anticipated; five-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1599 anticipated if held clean. Cycle 2 SIGN-clean at High confidence anticipated per §11.3 canonical-summary bounded-work + evidence-consolidation-not-new-audit precedent.
- **PA Chat tool:** `tools/pa_local.sh "message"` — but line 128 rotation owed at next-arc open (currently still points at retired Group 1500 pin).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 9-arc CODIFICATION-READY threshold reached):** S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506 9-arc pattern confirmed. Four-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506. If Rigby generic-errors on turn 1 of a fresh SIGN pin, apply D45 recovery pattern preemptively — warmup-ping first (ultra-short "confirm ready" probe), then batched titles-only SIGN 2-3 findings per prompt. Non-triggered across four consecutive arcs S1503-S1506; codified as prevention (D48 preemptive gate) not recovery (D45). Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.

## Repo state at next-session open

- **Branch state (at S1599 close, before merge):** `docs/session-1599-sports-canonical-summary` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1599 handoff at `docs/handoffs/SESSION_1599_SPORTS_CANONICAL_SUMMARY.md`. Prior handoffs: SESSION_1506 (Sports Cat F); SESSION_1505 (Sports Cat E); SESSION_1504 (Sports Cat D); SESSION_1503 (Sports Cat C); SESSION_1502 (Sports Cat B); SESSION_1501 (Sports Cat A); SESSION_1500 (Sports arc open); SESSION_1499 (Revenue arc-close canonical summary); SESSION_1406 (Revenue Cat F); SESSION_1405 (Revenue Cat E); SESSION_1404 (Revenue Cat D); SESSION_1403 (Revenue Cat C); SESSION_1402 (Revenue Cat B); SESSION_1401 (Revenue Cat A); SESSION_1400 (Group 1400 arc open); SESSION_1399 (Group 1300 canonical summary — first xx99).
- **ARCHITECTURE_INDEX version:** v34 (bumped this session with §1.37 S1599 canonical summary + §8 timeline S1599 arc-close row + v34 preamble). Next bump at Group 1600 arc-open OR next major library event.
- **OPEN_ARCS state:** Group 1500 row moved In-progress → Closed section this commit; matches S1499 Revenue arc-close pattern. Next-arc default lean Group 1600 Content / Deliverables / Publishing per playbook §22 domain queue.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1599 artifact set is on `main` — if yes, next session branches off `main`
- [ ] Run post-merge 4-step docs cascade + `build_docs_provenance` per `feedback_docs_cascade_at_every_close.md`
- [ ] Chris ratifies next-session mission — Chris-gated ADR (R.SPORTS.POSTURE + R.DBAO.CODENAME) OR T1 CRITICAL remediation (R.C1/R.D1 zero-fire beat gates) OR Group 1600 arc open OR playbook v3 promotion session
- [ ] If ADR: consume xx99 §5 posture-decision brief verbatim + §5.F F2-fold scoring rubric + §5.E cost asymmetry summary + §5.D failure-modes table
- [ ] If T1 remediation: sequence R.C2 concurrency-safety BEFORE R.C1 verify-beat restoration; sequence R.D2 idempotency BEFORE R.D1 digest-beat restoration; parallelizable R.D3 zero-test-coverage
- [ ] If Group 1600 open: mint fresh arc pin via `session_tool.create_fresh` + rotate `tools/pa_local.sh:128`; apply Chris's Phase 0 F.i/F.ii/F.iii methodology **third application** per D58 two-triggers pattern (methodology per playbook v3 template if promotion triggered post-S1599)
- [ ] If playbook v3 promotion: consume xx99 §10.2 6-candidate codify list; apply §12.4 discriminative-value criterion check verification

## Reference — where to look

- **S1599 xx99 canonical summary:** `docs/research/domains/sports/1599_sports_canonical_summary.md` — 2241-line canonical summary; §1-§12 playbook §11.3 template + §5 D59 posture-decision evidence brief + §10 meta-methodology third application + §12.4 discriminative-value criterion check with 4 of 4 evidence types satisfied.
- **S1506 Cat F audit doc:** `docs/research/domains/sports/1506_sports_cross_domain_integration_lens_and_posture_decision_framing_audit.md` — §20.6 posture-decision evidence plan consumed verbatim into xx99 §5.
- **S1505 Cat E audit doc:** `docs/research/domains/sports/1505_sports_frontend_surface_audit.md`
- **S1504 Cat D audit doc:** `docs/research/domains/sports/1504_sports_betting_content_pipeline_audit.md`
- **S1503 Cat C audit doc:** `docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md`
- **S1502 Cat B audit doc:** `docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md`
- **S1501 Cat A audit doc:** `docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md`
- **Group 1500 parent scoping doc:** `docs/research/domains/sports/1500_sports_domain_scoping.md` — Chris-locked decisions D56-D61 (D57 P1-P6 mission sequence + xx99 P7 slot; D58 methodology UNCHANGED; D59 posture-decision framing NOT selection; D60 Intelligence bound out; D61 DBAO codename option (a) parked); §12.4 discriminative-value criterion + §12.5 F.iii Sports Domain Lifecycle Traceability Table requirement.
- **Group 1400 canonical summary:** `docs/research/domains/revenue/1499_revenue_canonical_summary.md` (playbook §11.3 §10 second application — precedent for S1599 third application).
- **Group 1300 canonical summary:** `docs/research/domains/memory/1399_memory_canonical_summary.md` (first formal xx99 canonical summary — original precedent for playbook §11.3 §10 template).
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v34:** `docs/research/ARCHITECTURE_INDEX.md` — S1599 §1.37 + §8 timeline S1599 arc-close row + v34 preamble.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1500 In-progress → Closed section this commit.
- **AUDIT_FINDINGS.md #12:** canonical Celery deferred-by-policy list — cross-reference for R.C1 verify-beat + R.D1 digest-beat disposition (add to §12 OR restore beat).
- **CELERY_AUDIT.md:** canonical Celery inventory.
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — canonical summary only; no runtime changes).
- Handoff numbering continuity — S1599 continues arc-numbering convention (S1300 arc-open + S1301-S1305 children + S1399 canonical; S1400 arc-open + S1401-S1406 children + S1499 canonical; S1500 arc-open + S1501-S1506 children + **S1599 canonical LANDED**).
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; S1599 §7.2 Sports narrative refresh recommendation post-arc PR).
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1599 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`.
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold).
- Group 1400 post-arc §7 anchor-updates still pending (6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing — inherited from S1499).
- **Group 1500 post-arc §7 anchor-updates (NEW at S1599):** `PLATFORM_INVENTORY.md` §3.10 subdivision + DBAO subgroup conditional on T1.b R.DBAO.CODENAME verdict + `PLATFORM_WHAT_IT_IS.md` Sports narrative refresh + NEW `docs/topics/sports-betting.md` first-inventory landing (C2 cross-cutting gate) + `.github/CODEOWNERS` 6 sports runtime files.
- **Group 1500 T1 CRITICAL remediation queue (NEW at S1599):** R.C1 verify_betting_outcomes beat-restoration ← R.C2 pre-restore-beat concurrency-safety hardening; R.D1 daily_betting_digest beat-restoration OR §12 deferred-list entry ← R.D2 idempotency hardening; R.D3 zero-test-coverage reliability multiplier (parallelizable); R.D4 SportsBettingBrief consumer-or-remove ← T1.a; R.D5 two-writer dedup ← R.D4.
- **D48 preemptive stability-probe gate 10th-arm anticipated at S1599 SIGN cycle** — five-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1599 if held clean.
- **Playbook v3 §11.1 template promotion TRIGGERS** per §12.4 discriminative-value criterion check (4 of 4 evidence types satisfied). Codification implementation is a separate post-arc session; S1599 §10.2 flagged 6 candidates.
