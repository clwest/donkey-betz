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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1401 close:**

- **Active arc pin:** `pa-34d43795e1b24bd3` ("Session 1400 — Revenue research group (kickoff)"). Retained through S1401 per D31 lock; will carry S1402 → S1406 + S1499 continuity throughout Group 1400 arc. Do NOT retire mid-arc.
- **Recently retired at S1401 close:** `pa-16d8b24d30e7a7d8` (S1401 SIGN isolation pin; retire post-PR-merge via `session_tool.retire`).
- **Retired earlier at S1400 open:** `pa-aa54193f240f4846` (Group 1300 arc pin S1300-S1399) + `pa-4fc3329d0db6484f` (S1399 SIGN pin).
- **Next SIGN pin:** mint fresh isolation pin per playbook §15 stage table for S1402 Child B full-SIGN cycle 1.

Use `tools/pa_local.sh` for all chats unless you have a reason to override.

## READ THIS SECOND — GROUP 1400 REVENUE IN-PROGRESS; S1402 CHILD B IS NEXT MISSION

Session 1401 shipped the first Group 1400 child audit at `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` (Category A Opportunity Discovery + Scoring; 20-section playbook §11.2 template; Rigby SIGN-clean cycle 2 High confidence after 4-fold cycle 1). ARCHITECTURE_INDEX v19 → v20 bump landed same-commit (added §1.22 for S1400 parent scoping + §1.23 for S1401 child audit + §8 timeline S1400 + S1401 rows).

**Load-bearing S1401 outputs to inherit at S1402 open:**

- **Sports lane resolved (§12.1 Q6):** `intelligence/sports_opportunity_generator.py:83` writes `OpportunityTracking`, not mainline `Opportunity`. S1274 §2.4 line 270 MISSING remains ACCURATE for mainline — refinement is "separate lane" wording rather than "missing implementation."
- **NEW dual opportunity representation drift (§14 D6 + §19 R1 umbrella):** 5 consumer sites in `consumers_base.py` (lines 1696, 1730, 2541, 2557, 2597) stream from `intelligence_engine.get_current_opportunities()` in-memory realtime source, not persistent Django `Opportunity`. Rigby SIGN cycle 1 grep broadened the finding from 1 site to 5.
- **F1 provenance-filter drift + F3 Redis-only durability + F2 orphan-write cluster all CANDIDATE HIGH** per S1399 §4 methodology inheritance.
- **Orchestrator vs ExecutionPipeline COMPLEMENTARY** (Agent 2 direct read overrode Agent 6 duplication flag; not consolidation candidate).
- **NEW debt T5:** `core/settings.py` `task_routes` defines `score_opportunities_from_spider_data` TWICE at line 1277 (`long_running`) + line 1484 (`content`); later wins → effective queue `content`. Follow-on cleanup PR needed (design-preparation, not audit).
- **Ownership gap CONFIRMED** (S1274 §14 #36 inherited HIGH); deferred to Child E per D28.
- **Maturity WORKING** (S1273 baseline preserved) + **Coverage LIGHT** (matches parent §11.3; upgrade candidate at S1499 xx99).

**Load-bearing methodology outputs of S1401 (inherit at S1402):**

- **Parent-Claude verifier-loop pre-SIGN discipline** — S1401 corrected 5 sub-agent claims BEFORE Rigby SIGN (Agent 3 beat-schedule negative claim + orchestrator-overlap flag + publisher-line correction + dual-representation surfaced + Celery duplicate surfaced). Pattern: catch evidence overreach parent-side first so Rigby SIGN cycles focus on substantive edges. Extend to S1402.
- **Rigby-side grep-expansion of dual-representation finding** — S1401 v1 named 1 consumer site; Rigby cycle 1 grep found 5. Follow-on pattern: expect Rigby to broaden hypothesis scope when the finding is a search-pattern class (not a single-instance bug).

**Session close artifacts committed at S1401 close (this session):**

```
docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md   [new; 6,500+ words after folds; status: draft → active on merge]
docs/research/ARCHITECTURE_INDEX.md                                                  [modified — v19 → v20; §1.22 S1400 + §1.23 S1401 rows added; §8 timeline S1400 + S1401 rows added; frontmatter last_verified + owner + v20 change note]
docs/research/OPEN_ARCS.md                                                           [modified — Group 1400 In-progress row current-child field rotated; frontmatter last_updated with S1401 close reconciliation; Recent reconciliations 2026-07-01 (S1401 close) entry added]
00-START-NEXT-SESSION.md                                                             [modified — this file]
docs/handoffs/SESSION_1401_REVENUE_OPPORTUNITY_DISCOVERY_SCORING.md                  [new — session handoff]
```

Handoff: `docs/handoffs/SESSION_1401_REVENUE_OPPORTUNITY_DISCOVERY_SCORING.md`.

### NEXT-SESSION MISSION — S1402 Child B (Outreach Composition + Delivery)

Per Group 1400 parent doc §5 child mission sequence + §12.1 Category B row + §10.2 Category B evidence surface:

- **Session ID.** S1402.
- **Slot.** P2 (second child; consumes S1401 Category A output at the seam where scored Opportunity rows become outreach targets).
- **Category.** B — Outreach Composition + Delivery.
- **Branch.** `docs/session-1402-revenue-outreach-composition-delivery` off `main` post-S1401 merge.
- **Playbook §15 SIGN routing.** Full 20-section SIGN with fresh isolation pin per §15 stage table (S1402 SIGN pin minted at mid-session).
- **Playbook §13 sub-agent sweep.** 6 parallel Explore agents covering: (1) models `OutreachDraft` (`core/models_outreach.py:18`) + related sequencer state models if any; (2) `core/services/ops_autopilot/outreach_generation.py:92 OpportunityDraftGenerator` composition path (does it use single-shot LLM OR the Content Deliberation reviewer chain — resolves S1273 §10.3 UNKNOWN via Category B lens); (3) `core/services/ops_autopilot/revenue.py:605 OutreachSequencer` scheduling behavior + queue routing; (4) outbound channel service (email? LinkedIn API? Discord? Rigby DM? — resolves S1273 §10.3 UNKNOWN #2 + S1274 §2.4 line 293 MISSING); (5) Outreach → Engagement seam (`OutreachDraft` → `EngagementEvent` transition; where does an OutreachDraft "become" an engagement metric — writer/reader graph); (6) Docs + prior research + drift/debt/ownership/maturity for Category B specifically (mirror S1401 Agent 5 + Agent 6 pattern).
- **Playbook §11.2 20-section template.** Full 20 sections; category B questions from parent §12.1 answered explicitly.

### Category B F.iii questions to answer (parent §12.1)

- How does `OpportunityDraftGenerator` compose outreach (single-shot LLM vs Content Deliberation reviewer chain)?
- Where does outreach actually get SENT (email? LinkedIn? Discord? Rigby DM?) — resolves S1273 §10.3 UNKNOWN #2 + S1274 §2.4 line 293 MISSING.
- How does `OutreachSequencer` scheduling work?

### Two open decisions gating S1402 launch

- **D32 — Launch cadence.** (i) Launch S1402 next session (default lean; matches S1301–S1305 rhythm + S1401 outcome); (ii) parallelize S1402 + S1403 via isolation-pin split (unusual — Chris explicit call only). **Default lean: OPTION (i) — sequential.**
- **D33 — Arc pin retention.** (i) Retain `pa-34d43795e1b24bd3` for S1402 (default lean; matches S1301-S1399 + S1401 retention rhythm); (ii) mint fresh pin (Chris explicit call only). **Default lean: OPTION (i) — retain.**

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview` (per Rigby local trap)
3. Check if S1401 artifact set was committed + merged to `main` between sessions — if yes, S1402 branches off `main`
4. Verify `pa-34d43795e1b24bd3` retention status (`session_tool.health_check`); expected `recommendation: continue`
5. Retire `pa-16d8b24d30e7a7d8` (S1401 isolation pin) via `session_tool.retire` if not yet retired post-merge
6. Resolve D32 (launch cadence) + D33 (arc pin retention) with Chris via arc pin (both default leans align with prior discipline — likely fast "agree all")
7. Create branch `docs/session-1402-revenue-outreach-composition-delivery` off `main`
8. Read parent doc §12.1 Category B row + §10.2 Category B evidence surface + §11.4 (15 inherited findings — do NOT rediscover) as the mission spec
9. Read S1401 §9 integration map + §14 D6 dual representation + §19 R1 umbrella (Category B may inherit R1 sub-questions on outreach outbound-channel provenance)
10. Launch playbook §13 6-parallel-Explore sweep on the 6 evidence surfaces named above
11. Draft `docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md` per playbook §11.2 20-section template
12. Route to Rigby with full SIGN per playbook §15 stage table (full 9-question audit SIGN, not light)
13. Fold Rigby SIGN edits + Chris ratification + commit + PR

---

## PA / Rigby context

- **Arc pin at session start:** `pa-34d43795e1b24bd3` (Group 1400 continuity — do NOT retire mid-arc; retires at S1499 canonical summary close or at Chris explicit direction).
- **S1401 SIGN pin retirement:** `pa-16d8b24d30e7a7d8` should be retired post-PR-merge via `session_tool.retire` (playbook §15 fresh isolation pin retirement rule). Retire from any active conversation using `--conversation pa-16d8b24d30e7a7d8`.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin `pa-34d43795e1b24bd3`).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.

## Repo state at next-session open

- **Branch state (at S1401 close, before merge):** `docs/session-1401-revenue-opportunity-discovery-scoring` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1401 handoff at `docs/handoffs/SESSION_1401_REVENUE_OPPORTUNITY_DISCOVERY_SCORING.md`. Prior handoffs: SESSION_1400 (Group 1400 arc open parent scoping); SESSION_1300–SESSION_1305 (Group 1300 children); SESSION_1399 (Group 1300 xx99 canonical summary).
- **ARCHITECTURE_INDEX version:** v20 (bumped this session with §1.22 S1400 + §1.23 S1401 + timeline rows). Next bump at S1402 close.
- **OPEN_ARCS state:** Group 1400 row in "In-progress" section, current-child field = "S1401 SIGN-clean cycle 2 (commit-gated) + S1402 queued next."

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1401 artifact set is on `main` — if yes, S1402 branches off `main`; if no, continues stacking on `docs/session-1401-revenue-opportunity-discovery-scoring`
- [ ] Verify `pa-34d43795e1b24bd3` health via `session_tool.health_check` (expect `recommendation: continue`)
- [ ] Retire `pa-16d8b24d30e7a7d8` (S1401 isolation pin) if still active
- [ ] Resolve D32 (S1402 launch cadence: sequential vs parallel-with-S1403) + D33 (arc pin retention: retain vs fresh mint) with Chris via arc pin
- [ ] Create branch `docs/session-1402-revenue-outreach-composition-delivery` off `main`
- [ ] Read parent doc §12.1 Category B row + §10.2 Category B evidence surface + §11.4 inherited findings + S1401 §9 integration map + §14 D6 + §19 R1 umbrella
- [ ] Launch playbook §13 6-parallel-Explore sweep on the 6 evidence surfaces named in §NEXT-SESSION MISSION above
- [ ] Draft `1402_revenue_outreach_composition_delivery_audit.md` per playbook §11.2 20-section template
- [ ] Route to Rigby with full SIGN (9 canonical questions) per playbook §15 stage table
- [ ] Fold SIGN cycle edits + Chris ratification + commit + PR

## Reference — where to look

- **Group 1400 parent scoping doc:** `docs/research/domains/revenue/1400_revenue_domain_scoping.md` — start here for anything Group 1400
- **Group 1400 parent §5 mission sequence:** locked as A → B → C → D → E → F → xx99 (D24 + D25)
- **Group 1400 parent §10.2 Category B evidence surface:** `OutreachDraft` + `OpportunityDraftGenerator` + `OutreachSequencer` + outbound channel (currently UNKNOWN)
- **Group 1400 parent §11.4 inherited findings:** 15 findings — do NOT rediscover
- **Group 1400 parent §12.1 Category B questions:** what S1402 audit must answer
- **S1401 Child A audit:** `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` — Category A ↔ Category B seam evidence at §9 integration map + §14 drift + §19 R1 umbrella
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template for S1402 audit + §13 6-parallel-Explore sweep + §14 evidence rules + §15 full-SIGN stage table + §16 commit policy)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v20:** `docs/research/ARCHITECTURE_INDEX.md`
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1400 In-progress row
- **Group 1300 canonical summary (recently closed):** `docs/research/domains/memory/1399_memory_canonical_summary.md` — F1-F4 methodology inherited into Group 1400 diagnostic lenses
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Whole-platform architecture inventory §3.32 + §4.9:** Revenue Pipeline row + cross-domain flow (S1273 v2 Rigby-added)
- **Cross-domain integration audit §2.4 + §3.7 + §5.10 + §9.6 + §14 finding #36:** S1274 findings inherited by Group 1400

## Doctor warnings to expect

- Inventory freshness (stale) — `python manage.py generate_platform_inventory --write` to refresh; S1401 does not update inventory rows (research audit only)
- Handoff numbering continuity — legitimate; S1306-S1398 skipped by intent per Rigby lean at S1300 close; Chris's arc-numbering convention preserved for Group 1400 (S1401-S1406 + S1499)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 is older than latest handoff (informational; S1399 §7 proposed narrative updates for a subsequent PR; Group 1400 does not touch narrative anchor)
- Docs cascade — run 4-step cascade (build_docs_index → build_rag_corpus → sync_docs_index_to_documents → embed_documents) + build_docs_provenance after S1401 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`
