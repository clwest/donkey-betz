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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1400 open:**

- **Active arc pin:** `pa-34d43795e1b24bd3` ("Session 1400 — Revenue research group (kickoff)"). Carries S1400 parent scoping context; will carry S1401 → S1406 + S1499 continuity throughout Group 1400 arc. Do NOT retire mid-arc.
- **Recently retired:** `pa-aa54193f240f4846` (Group 1300 arc pin S1300-S1399; retired at S1400 open via `session_tool.retire force=true` — `updated_count: 29`) + `pa-4fc3329d0db6484f` (S1399 SIGN pin; retired at S1399 close — `updated_count: 2`).
- **Next SIGN pin:** to be minted per-child at each S1401-S1406 mid-session Rigby full SIGN cycle per playbook §15 stage table.

Use `tools/pa_local.sh` for all chats unless you have a reason to override.

## READ THIS SECOND — GROUP 1400 REVENUE OPEN; S1401 CHILD A IS NEXT MISSION

Session 1400 opened Group 1400 Revenue arc + shipped the Phase 0 parent scoping doc at `docs/research/domains/revenue/1400_revenue_domain_scoping.md` (1363 lines, `status: active`, `category: parent_scoping`). **9 arc-open decisions Chris-locked across three "agree all" ratification rounds**: D21 (short-command launch), D23 (parent-with-children), D24 (child mission sequence A→B→C→D→E→F→xx99), D25 (F.i — full Category F Income/Jobs lane child audit as S1406), D26 (revenue-facing ops_autopilot only IN scope), D27 (§15 stage table SIGN routing), D28 (Child E owns Opportunity → Initiative wiring per Rigby Must-fix #2), D29 (Yes-two-triggers — Group 1400 pilots Chris's Phase 0 methodology; playbook v3 promotion at Group 1500 close if unchanged).

**Load-bearing Group 1400 shape (Chris-locked 2026-07-01):**

- 6 children + xx99: **S1401 A** (Opportunity Discovery + Scoring) → **S1402 B** (Outreach Composition + Delivery) → **S1403 C** (Engagement Inbound) → **S1404 D** (Meeting + Close) → **S1405 E** (Revenue Attribution + Analytics) → **S1406 F** (Income/Jobs lane) → **S1499 xx99** (canonical summary + Revenue Lifecycle Traceability Table).
- 17 revenue-related Django models + 10+ services + 3 agents + 1 WebSocket consumer + 1 EventBus event + 1 Celery beat + 4 view files + 4 frontend routes + 9-file Income/Jobs adjacency (see parent §2.4 + §10.1 for full census).
- 15 inherited findings from S1273/S1274/S1399 (see parent §11.4) — inherit, don't rediscover.
- Chris's Phase 0 F.i/F.ii/F.iii methodology first application at parent §10/§11/§12; playbook v3 §11.1 template addition proposed at parent §9.5; promotion trigger = Group 1500 second application unchanged.

**Session close artifacts committed at S1400 open (this session):**

```
docs/research/domains/revenue/1400_revenue_domain_scoping.md   [new, 1363 lines]
docs/research/OPEN_ARCS.md                                     [modified — Group 1400 In-progress row + Not-started queue rotation + Recent reconciliations 2026-07-01 S1400 open entry]
tools/pa_local.sh                                              [modified — line 115 pin rotation + header ledger]
00-START-NEXT-SESSION.md                                       [modified — this file]
docs/handoffs/SESSION_1400_REVENUE_RESEARCH_GROUP_PARENT_SCOPING.md   [new — session handoff]
```

Handoff: `docs/handoffs/SESSION_1400_REVENUE_RESEARCH_GROUP_PARENT_SCOPING.md`.

### NEXT-SESSION MISSION — S1401 Child A (Opportunity Discovery + Scoring)

Per Group 1400 parent doc §5 child mission sequence + §12.1 Category A row + §10.2 Category A evidence surface:

- **Session ID.** S1401.
- **Slot.** P1 (first child; widest surface; grounds every downstream child's evidence).
- **Category.** A — Opportunity Discovery + Scoring.
- **Branch.** `docs/session-1401-revenue-opportunity-discovery-scoring` off `main` post-S1400 merge.
- **Playbook §15 SIGN routing.** Full 20-section SIGN with fresh isolation pin per §15 stage table (S1401 SIGN pin minted at mid-session).
- **Playbook §13 sub-agent sweep.** 6 parallel Explore agents covering: (1) models `Opportunity`, `OpportunityScore`, `OpportunityDigest`, `OpportunityPredictionAccuracy`, `OpportunityInteraction`; (2) `OpportunityPipelineOrchestrator` + `OpportunityExecutionPipeline` + `opportunity_scorer.py` orchestration path; (3) `OpportunityScoringAgent` + `OpportunityPipelineAgent` behavior + prompt path; (4) `intelligence/opportunity_storage.py` + `spider_opportunity_connector.py` + `sports_opportunity_generator.py` production paths; (5) `ml_pipeline/opportunity_categorizer.py` model integration; (6) `OpportunityScannerConsumer` WebSocket + `OPPORTUNITY_SCORED` EventBus publisher/consumer graph.
- **Playbook §11.2 20-section template.** Full 20 sections; category A questions from parent §12.1 answered explicitly.

### Two open decisions gating S1401 launch

- **D30 — Launch cadence.** (i) Launch S1401 next session (default lean; matches S1301-S1305 rhythm from Group 1300); (ii) parallelize S1401 + S1402 via isolation-pin split (unusual — Chris explicit call only). **Default lean: OPTION (i) — sequential.**
- **D31 — Arc pin retention.** (i) Retain `pa-34d43795e1b24bd3` for S1401 (default lean; matches S1301-S1399 retention rhythm); (ii) mint fresh pin (Chris explicit call only). **Default lean: OPTION (i) — retain.**

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview` (per Rigby local trap)
3. Check if S1400 artifact set was committed + merged to `main` between sessions — if yes, S1401 branches off `main`
4. Verify `pa-34d43795e1b24bd3` retention status (`session_tool.health_check`); expected `recommendation: continue` given fresh thread state
5. Resolve D30 (launch cadence) + D31 (arc pin retention) with Chris via arc pin (both default leans align with prior Group 1300 discipline — likely a fast "agree all" round)
6. Create branch `docs/session-1401-revenue-opportunity-discovery-scoring` off `main`
7. Read parent doc §12.1 Category A row + §10.2 Category A evidence surface as the mission spec
8. Read parent doc §11.4 to know which 15 findings are inherited (do NOT rediscover)
9. Launch playbook §13 6-parallel-Explore sweep on the 6 evidence surfaces named above
10. Draft `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` per playbook §11.2 20-section template
11. Route to Rigby with full SIGN per playbook §15 stage table (full 28-question audit SIGN, not light)
12. Fold Rigby SIGN edits + Chris ratification + commit + PR

---

## PA / Rigby context

- **Arc pin at session start:** `pa-34d43795e1b24bd3` (Group 1400 continuity — do NOT retire mid-arc; retires at S1499 canonical summary close or at Chris explicit direction).
- **S1400 open SIGN pins:** none minted (Light SIGN cycles 1 + 2 ran on arc pin directly; per playbook §15 Light SIGN routing does not require isolation-pin).
- **Retired at S1400 open:** `pa-aa54193f240f4846` (Group 1300 arc pin S1300-S1399, retired via `session_tool.retire force=true`, `updated_count: 29`). `pa-4fc3329d0db6484f` (S1399 SIGN pin, retired at S1399 close).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin, updated to `pa-34d43795e1b24bd3` at S1400 open).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.

## Repo state at next-session open

- **Branch state (at S1400 close, before merge):** `docs/session-1400-revenue-research-group` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1400 handoff at `docs/handoffs/SESSION_1400_REVENUE_RESEARCH_GROUP_PARENT_SCOPING.md`. Prior handoffs: SESSION_1300 through SESSION_1305 for Group 1300 children + SESSION_1399 for Group 1300 xx99 canonical summary.
- **ARCHITECTURE_INDEX version:** v18 (last bumped at S1399 close). Next bump at S1499 canonical summary close per playbook §16.
- **OPEN_ARCS state:** Group 1400 row in "In-progress" section, current-child field = "S1401 queued next" per this doc's D30/D31 lock.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1400 artifact set is on `main` — if yes, S1401 branches off `main`; if no, continues stacking on `docs/session-1400-revenue-research-group`
- [ ] Verify `pa-34d43795e1b24bd3` health via `session_tool.health_check` (expect `recommendation: continue` given kickoff-fresh state)
- [ ] Resolve D30 (S1401 launch cadence: sequential vs parallel-with-S1402) + D31 (arc pin retention: retain vs fresh mint) with Chris via arc pin
- [ ] Create branch `docs/session-1401-revenue-opportunity-discovery-scoring` off `main`
- [ ] Read parent doc §12.1 Category A row + §10.2 Category A evidence surface + §11.4 inherited findings (do NOT rediscover) before launching sub-agents
- [ ] Launch playbook §13 6-parallel-Explore sweep on the 6 evidence surfaces named in §NEXT-SESSION MISSION above
- [ ] Draft `1401_revenue_opportunity_discovery_scoring_audit.md` per playbook §11.2 20-section template
- [ ] Route to Rigby with full SIGN (28 canonical questions) per playbook §15 stage table
- [ ] Fold SIGN cycle edits + Chris ratification + commit + PR

## Reference — where to look

- **Group 1400 parent scoping doc:** `docs/research/domains/revenue/1400_revenue_domain_scoping.md` — start here for anything Group 1400
- **Group 1400 parent §5 mission sequence:** locked as A → B → C → D → E → F → xx99
- **Group 1400 parent §10 F.i Domain Definition:** what Group 1400 covers (5 Chris-question answers + 7 overlap table)
- **Group 1400 parent §11 F.ii Existing Knowledge Inventory:** 15 inherited findings — do NOT rediscover
- **Group 1400 parent §12 F.iii Success Criteria:** what "done" looks like per child + xx99 traceability artifact
- **Group 1400 parent §9.5 playbook v3 proposal:** codify Chris's Phase 0 methodology at playbook v3 §11.1 template (promotion gated on Group 1500 second application unchanged)
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template for S1401 audit + §13 6-parallel-Explore sweep + §14 evidence rules + §15 full-SIGN stage table + §16 commit policy)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v18:** `docs/research/ARCHITECTURE_INDEX.md`
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1400 In-progress row
- **Group 1300 canonical summary (recently closed):** `docs/research/domains/memory/1399_memory_canonical_summary.md` — F1-F4 methodology outputs inherited into Group 1400 diagnostic lenses
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Whole-platform architecture inventory §3.32 + §4.9:** Revenue Pipeline row + cross-domain flow (S1273 v2 Rigby-added)
- **Cross-domain integration audit §2.4 + §3.7 + §5.10 + §9.6 + §14 finding #36:** S1274 findings inherited by Group 1400 (see parent §11.4)

## Doctor warnings to expect

- Inventory freshness (stale) — `python manage.py generate_platform_inventory --write` to refresh; S1400 does not update inventory rows (Phase 0 scoping only)
- Handoff numbering continuity — legitimate; S1306-S1398 skipped by intent per Rigby lean at S1300 close ("Plan for a 1399 canonical summary once the 1300-series research is complete"); Chris's arc-numbering convention preserved for Group 1400 (S1401-S1406 + S1499)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 is older than latest handoff (informational; S1399 §7 proposed narrative updates for a subsequent PR; Group 1400 does not touch narrative anchor)
- Docs cascade — run 4-step cascade (build_docs_index → build_rag_corpus → sync_docs_index_to_documents → embed_documents) + build_docs_provenance after S1400 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`
