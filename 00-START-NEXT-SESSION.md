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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1402 close:**

- **Active arc pin:** `pa-34d43795e1b24bd3` ("Session 1400 — Revenue research group (kickoff)"). Retained through S1401 + S1402 per D31/D33/D35; will carry S1403 → S1406 + S1499 continuity throughout Group 1400 arc. Do NOT retire mid-arc.
- **Recently retired at S1402 close:** `pa-4a0a28edcb7a45ec` (S1402 SIGN isolation pin; retire post-PR-merge via `session_tool.retire`).
- **Retired earlier at S1401 close:** `pa-16d8b24d30e7a7d8` (S1401 SIGN pin).
- **Retired earlier at S1400 open:** `pa-aa54193f240f4846` (Group 1300 arc pin S1300-S1399) + `pa-4fc3329d0db6484f` (S1399 SIGN pin).
- **Next SIGN pin:** mint fresh isolation pin per playbook §15 stage table for S1403 Child C full-SIGN cycle 1.

Use `tools/pa_local.sh` for all chats unless you have a reason to override.

## READ THIS SECOND — GROUP 1400 REVENUE IN-PROGRESS; S1403 CHILD C IS NEXT MISSION

Session 1402 shipped the second Group 1400 child audit at `docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md` (Category B Outreach Composition + Delivery; 20-section playbook §11.2 template; Rigby SIGN-clean cycle 2 High confidence after 2 must-fix + D.B7 dead-code fold cycle 1 + 5 Q-answer folds cycle 2). ARCHITECTURE_INDEX v20 → v21 bump landed same-commit (added §1.24 for S1402 child audit + §8 timeline S1402 row).

**Load-bearing S1402 outputs to inherit at S1403 open:**

- **F.B3 engagement feedback loop missing (CONFIRMED HIGH):** `EngagementEvent.outreach_draft` FK schema exists at `core/models_engagement.py:55-59` but **zero writer sites for EngagementEvent** (`EngagementEvent.objects.create|EngagementEvent(` grep → class definition only). Category C S1403 inherits the **entire seam build-out** as its central deliverable — not a seam-verify but a whole-seam design.
- **No OUTREACH_* event streams** exist (`event_bus.py:21-31` has zero outreach-related `EventStream` values). S1403 may recommend adding as design-preparation (e.g., `OUTREACH_REPLIED` as a Category C ingestion trigger).
- **F.B1 delivery path missing (CONFIRMED HIGH):** Category B does not send outreach. This affects Category C's engagement ingestion premise — reply/click/open ingestion presupposes a sent outreach; the seam must be designed WITH R.B1 delivery ADR (or as pre-work that lands before delivery ships).
- **F.B4 cadence declared but not realized at runtime:** OutreachSequencer's declared 4-touch cadence has no runtime realization. Only Touch 1 fires. This means Category C only sees Touch 1 outreach in production data — engagement metrics should be scoped accordingly.
- **F.B2 CONFIRMED F2 orphan-write writer-site at `revenue.py:812-829`** (runtime blast radius ZERO due to F.B4). Category C should watch for the same pattern in its own writer sites (e.g., `EngagementEvent.objects.create(...)` calls when the ingestion path is built).
- **Composition path RESOLVED as single-shot LLM** — `OpportunityDraftGenerator.render_email` at `outreach_generation.py:340`. No Content Deliberation, no reviewer chain. Uses `get_openai_client()` factory + `gpt-5-mini` + `max_completion_tokens=4000`.

**Load-bearing methodology outputs of S1402 (inherit at S1403):**

- **Parent-Claude verifier-loop pre-SIGN discipline** — S1402 promoted 2 sub-agent findings BEFORE Rigby SIGN (Agent 6 → CONFIRMED writer-site F2 via direct read of `revenue.py:812-829`; Agent 4 → docstring-vs-runtime lifecycle divergence via `models_outreach.py:10` docstring). Extend to S1403.
- **Rigby ops probe mid-Cycle 1** — first library audit where Rigby ops probe + parent-Claude direct read jointly CONFIRMED a runtime-liveness finding (F.B4 / D.B7 / T.B5). Extends verifier-loop from "hypothesis correction" to "runtime-liveness confirmation via ops telemetry." If Category C needs to confirm/refute dead code, use the same pattern: `celery_task_history` + `PeriodicTask.filter` + PA tool exposure grep + repo-wide invocation grep.
- **SIGN storage truncation recovery** — first library audit where SIGN cycle 1 seed got truncated at Rigby's tool layer. Reconstructed via verbatim excerpt + evidence-based inference + independent probe/read verification. If truncation recurs at S1403, use the same recovery pattern; do NOT ask Rigby to regenerate verbatim (fails on token budget).

**Session close artifacts committed at S1402 close (this session):**

```
docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md   [new; 7,835+ words after folds; status: draft → active on merge]
docs/research/ARCHITECTURE_INDEX.md                                                  [modified — v20 → v21; §1.24 S1402 row added; §8 timeline S1402 row added; frontmatter v21 preamble]
docs/research/OPEN_ARCS.md                                                           [modified — Group 1400 In-progress row current-child field rotated; owner-pin retained through S1402; §Recent reconciliations 2026-07-01 (S1402 close) entry added]
00-START-NEXT-SESSION.md                                                             [modified — this file]
docs/handoffs/SESSION_1402_REVENUE_OUTREACH_COMPOSITION_DELIVERY.md                  [new — session handoff]
```

Handoff: `docs/handoffs/SESSION_1402_REVENUE_OUTREACH_COMPOSITION_DELIVERY.md`.

### NEXT-SESSION MISSION — S1403 Child C (Engagement Inbound)

Per Group 1400 parent doc §5 child mission sequence + §12.1 Category C row + §10.2 Category C evidence surface:

- **Session ID.** S1403.
- **Slot.** P3 (third child; consumes S1401 + S1402 outputs at the seam where OutreachDraft-state transitions surface engagement signal).
- **Category.** C — Engagement Inbound.
- **Branch.** `docs/session-1403-revenue-engagement-inbound` off `main` post-S1402 merge.
- **Playbook §15 SIGN routing.** Full 20-section SIGN with fresh isolation pin per §15 stage table (S1403 SIGN pin minted at mid-session).
- **Playbook §13 sub-agent sweep.** 6 parallel Explore agents covering:
  1. **4 engagement models** — `EngagementEvent` (`core/models_engagement.py:18`), `EngagementMetrics` (`core/models_engagement_metrics.py:14`), `OpportunityInteraction` (`core/models_engagement_metrics.py:164`), `ContentEngagement` (`core/models_pipeline_feedback.py:370`). Which is canonical? What's the event stream vs aggregate axis (parent §12.1 Category C hypothesis map)?
  2. **`EngagementEngine`** (`core/services/ops_autopilot/engagement.py:255-440`) — inbox / classify_event / draft_reply / approve_reply / disqualify / get_metrics_report / evaluate. Read/write graph.
  3. **`EngagementAutonomyEngine`** — autonomy gating + default state.
  4. **Ingestion path (F.B3 build-out CENTRAL scope inherited from S1402)** — the reply/click/open → EngagementEvent write path DOES NOT EXIST at HEAD `beda00e5`. S1403 must design (a) webhook receiver / polling task shape, (b) event-bus stream (`OUTREACH_REPLIED`/`OUTREACH_OPENED`/`OUTREACH_CLICKED`), (c) writer contract to `EngagementEvent` + `outreach_draft` FK population.
  5. **Category C → EngagementMetrics aggregation direction** — reads/writes graph; how does raw EngagementEvent become rolled-up EngagementMetrics?
  6. **Docs + prior research + drift/debt/ownership/maturity for Category C** (mirrors S1401 Agent 5 + Agent 6 + S1402 Agent 6 pattern).
- **Playbook §11.2 20-section template.** Full 20 sections; category C questions from parent §12.1 answered explicitly.

### Category C F.iii questions to answer (parent §12.1)

- Which of the 4 engagement models is canonical (`EngagementEvent`, `EngagementMetrics`, `OpportunityInteraction`, `ContentEngagement`)?
- What is the event stream vs aggregate axis?
- What does `EngagementAutonomyEngine` gate + what is the default state?
- **INHERITED from S1402:** How would the reply/click/open ingestion path be designed given F.B1 (no delivery) + F.B3 (no writer sites)? This becomes the central design-preparation question for S1403 given S1402's F.B3 finding.

### Two open decisions gating S1403 launch

- **D36 — Launch cadence.** (i) Launch S1403 next session (default lean; matches S1301–S1305 + S1401 + S1402 rhythm); (ii) parallelize S1403 + S1404 via isolation-pin split (unusual — Chris explicit call only). **Default lean: OPTION (i) — sequential.**
- **D37 — Arc pin retention.** (i) Retain `pa-34d43795e1b24bd3` for S1403 (default lean; matches D31/D33/D35 retention rhythm); (ii) mint fresh pin (Chris explicit call only). **Default lean: OPTION (i) — retain.**

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview` (per Rigby local trap)
3. Check if S1402 artifact set was committed + merged to `main` between sessions — if yes, S1403 branches off `main`
4. Verify `pa-34d43795e1b24bd3` retention status (`session_tool.health_check`); expected `recommendation: continue`
5. Retire `pa-4a0a28edcb7a45ec` (S1402 isolation pin) via `session_tool.retire` if not yet retired post-merge
6. Resolve D36 (launch cadence) + D37 (arc pin retention) with Chris via arc pin (both default leans align with prior discipline — likely fast "agree all")
7. Create branch `docs/session-1403-revenue-engagement-inbound` off `main`
8. Read parent doc §12.1 Category C row + §10.2 Category C evidence surface + §11.4 (15 inherited findings — do NOT rediscover) as the mission spec
9. Read S1401 §9 integration map + S1402 §9 integration map + S1402 F.B3 (engagement seam missing) + S1402 §14 D.B7 (evaluate dead-code confirmation)
10. Launch playbook §13 6-parallel-Explore sweep on the 6 evidence surfaces named above
11. Draft `docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md` per playbook §11.2 20-section template
12. Route to Rigby with full SIGN per playbook §15 stage table (full 9-question audit SIGN, not light)
13. Fold Rigby SIGN edits + Chris ratification + commit + PR

---

## PA / Rigby context

- **Arc pin at session start:** `pa-34d43795e1b24bd3` (Group 1400 continuity — do NOT retire mid-arc; retires at S1499 canonical summary close or at Chris explicit direction).
- **S1402 SIGN pin retirement:** `pa-4a0a28edcb7a45ec` should be retired post-PR-merge via `session_tool.retire` (playbook §15 fresh isolation pin retirement rule).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin `pa-34d43795e1b24bd3`).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.

## Repo state at next-session open

- **Branch state (at S1402 close, before merge):** `docs/session-1402-revenue-outreach-composition-delivery` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1402 handoff at `docs/handoffs/SESSION_1402_REVENUE_OUTREACH_COMPOSITION_DELIVERY.md`. Prior handoffs: SESSION_1401 (Group 1400 Child A Opportunity Discovery + Scoring); SESSION_1400 (Group 1400 arc open parent scoping); SESSION_1300–SESSION_1305 (Group 1300 children); SESSION_1399 (Group 1300 xx99 canonical summary).
- **ARCHITECTURE_INDEX version:** v21 (bumped this session with §1.24 S1402 + §8 timeline row + v21 preamble). Next bump at S1403 close.
- **OPEN_ARCS state:** Group 1400 row in "In-progress" section, current-child field = "S1402 SIGN-clean cycle 2 (commit-gated) + S1403 queued next."

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1402 artifact set is on `main` — if yes, S1403 branches off `main`; if no, continues stacking on `docs/session-1402-revenue-outreach-composition-delivery`
- [ ] Verify `pa-34d43795e1b24bd3` health via `session_tool.health_check` (expect `recommendation: continue`)
- [ ] Retire `pa-4a0a28edcb7a45ec` (S1402 isolation pin) if still active
- [ ] Resolve D36 (S1403 launch cadence: sequential vs parallel-with-S1404) + D37 (arc pin retention: retain vs fresh mint) with Chris via arc pin
- [ ] Create branch `docs/session-1403-revenue-engagement-inbound` off `main`
- [ ] Read parent doc §12.1 Category C row + §10.2 Category C evidence surface + §11.4 inherited findings + S1401 §9 integration map + S1402 F.B3 (missing engagement writer) + S1402 §14 D.B7 (dead-code confirmation)
- [ ] Launch playbook §13 6-parallel-Explore sweep on the 6 evidence surfaces named in §NEXT-SESSION MISSION above
- [ ] Draft `1403_revenue_engagement_inbound_audit.md` per playbook §11.2 20-section template
- [ ] Route to Rigby with full SIGN (9 canonical questions) per playbook §15 stage table
- [ ] Fold SIGN cycle edits + Chris ratification + commit + PR

## Reference — where to look

- **Group 1400 parent scoping doc:** `docs/research/domains/revenue/1400_revenue_domain_scoping.md` — start here for anything Group 1400
- **Group 1400 parent §5 mission sequence:** locked as A → B → C → D → E → F → xx99 (D24 + D25)
- **Group 1400 parent §10.2 Category C evidence surface:** 4 engagement-shape models + `EngagementEngine` + `EngagementAutonomyEngine`
- **Group 1400 parent §11.4 inherited findings:** 15 findings — do NOT rediscover
- **Group 1400 parent §12.1 Category C questions:** what S1403 audit must answer
- **S1401 Child A audit:** `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` — Category A ↔ Category B seam evidence at §9 integration map
- **S1402 Child B audit:** `docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md` — Category B ↔ Category C seam evidence at §9 integration map (Outreach → EngagementEvent MISSING WRITER PATH — S1403 central deliverable); §14 D.B7 evaluate dead-code confirmation; §19 R.B5 engagement ingestion path (S1403 owns)
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template for S1403 audit + §13 6-parallel-Explore sweep + §14 evidence rules + §15 full-SIGN stage table + §16 commit policy)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v21:** `docs/research/ARCHITECTURE_INDEX.md`
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1400 In-progress row
- **Group 1300 canonical summary (recently closed):** `docs/research/domains/memory/1399_memory_canonical_summary.md` — F1-F4 methodology inherited into Group 1400 diagnostic lenses
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Whole-platform architecture inventory §3.32 + §4.9:** Revenue Pipeline row + cross-domain flow (S1273 v2 Rigby-added)
- **Cross-domain integration audit §2.4 + §3.7 + §5.10 + §9.6 + §14 finding #36:** S1274 findings inherited by Group 1400

## Doctor warnings to expect

- Inventory freshness (stale) — `python manage.py generate_platform_inventory --write` to refresh; S1402 does not update inventory rows (research audit only)
- Handoff numbering continuity — legitimate; S1306-S1398 skipped by intent per Rigby lean at S1300 close; Chris's arc-numbering convention preserved for Group 1400 (S1401-S1406 + S1499)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 is older than latest handoff (informational; S1399 §7 proposed narrative updates for a subsequent PR; Group 1400 does not touch narrative anchor)
- Docs cascade — run 4-step cascade (build_docs_index → build_rag_corpus → sync_docs_index_to_documents → embed_documents) + build_docs_provenance after S1402 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`
