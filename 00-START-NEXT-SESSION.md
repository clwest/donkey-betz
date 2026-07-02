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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1405 close:**

- **Active arc pin:** `pa-34d43795e1b24bd3` ("Session 1400 — Revenue research group (kickoff)"). Retained through S1401 + S1402 + S1403 + S1404 + S1405 per D31/D33/D35/D37/D39/D42; will carry S1406 + S1499 continuity throughout Group 1400 arc. Do NOT retire mid-arc.
- **Recently retired at S1405 close:** `pa-4bdd5ad264674ce8` (S1405 first SIGN isolation pin — jammed after 2 substantive turns via placeholder-stall + generic-error pattern; retired mid-session `updated_count: 10, retired: true`) + `pa-637331c5f9574a10` (S1405 batched-retry SIGN pin — worker instability blocked Batches 2-3; retirement queued post-PR-merge per playbook §15).
- **Retired earlier at S1404 close:** `pa-87ee24cd0d3947ce` (S1404 SIGN pin).
- **Retired earlier at S1403 close:** `pa-fba0c4c81fba4922` (S1403 SIGN pin).
- **Retired earlier at S1402 close:** `pa-4a0a28edcb7a45ec` (S1402 SIGN pin).
- **Retired earlier at S1401 close:** `pa-16d8b24d30e7a7d8` (S1401 SIGN pin).
- **Retired earlier at S1400 open:** `pa-aa54193f240f4846` (Group 1300 arc pin S1300-S1399) + `pa-4fc3329d0db6484f` (S1399 SIGN pin).
- **Next SIGN pin:** mint fresh isolation pin per playbook §15 stage table for S1406 Child F full-SIGN cycle 1.

Use `tools/pa_local.sh` for all chats unless you have a reason to override.

## READ THIS SECOND — GROUP 1400 REVENUE IN-PROGRESS; S1406 CHILD F IS NEXT MISSION

Session 1405 shipped the fifth Group 1400 child audit at `docs/research/domains/revenue/1405_revenue_attribution_analytics_audit.md` (Category E Revenue Attribution + Analytics; 20-section playbook §11.2 template; **Rigby SIGN cycle 1 PARTIAL** — Batch 1 F.E1-F.E3 substantive pressure-test delivered; Batches 2-3 blocked by worker instability across 2 SIGN pins; D45 Chris ratification option (ii) accepted Batch 1 as SIGN-with-edits verdict; batches 2-3 deferred to follow-up SIGN addendum). ARCHITECTURE_INDEX v23 → v24 bump landed same-commit (added §1.27 for S1405 child audit + §8 timeline S1405 row + frontmatter v24 preamble). Two parent-doc anchor corrections landed at commit-time per S1404 §20.10 pattern (F.E4 frontend routes + F.E6 attribution algorithm location).

**Load-bearing S1405 outputs to inherit at S1406 open:**

- **F.E1 CONFIRMED HIGH (arc-wide 3-model over-modeled STATUS_CHOICES):** ClosePack (S1404) + OpportunityRevenue + OpportunityOutcome. Combined 16 declared / 6 reachable / 10 UNREACHABLE (62%). Category F should probe `FreelanceOpportunity` + related models for same pattern.
- **F.E2 CONFIRMED HIGH (new drift class — 4 phantom-field references, MUST-FIX per Rigby Batch 1):** Readers/writers reference fields that don't exist in schema; deterministic runtime errors, latent per F.D1 empty-tables pattern. Category F should probe the 10-file `intelligence/` Income/Jobs lane for same pattern.
- **F.E3 CONFIRMED HIGH (dual-representation drift extends S1401 D6 to Revenue; Rigby framing refinement folded):** Two revenue pipelines (core + intelligence/). Framing decision at R.E-3 ADR: intentional dual-schema (missing explicit contract) vs drift (missing integration). Category F likely inherits — 9 intelligence/ files may be parallel schema to core.
- **F.E4 + F.E6 parent-doc anchor corrections landed at S1405 commit-time.** F.E4: 4 frontend routes named in parent §3.E DO NOT EXIST; actual revenue features via `/analytics` + `/intelligence` routes. F.E6: attribution algorithm at `core/services/ops_autopilot/impact.py:1233-1290` `MultiTouchAttributor._attribute_event`, NOT `ops_autopilot/revenue.py`.
- **F.E7 refines F.D4 (code-exists-but-dormant, arc-wide):** HAI writers EXIST at 6 sites in `core/services/ops_autopilot/core.py` but RUNTIME-DORMANT via F.C6 (`run_ops_autopilot` deferred per AUDIT_FINDINGS.md #12).
- **F.E10 CONFIRMED HIGH runtime owner ABSENT arc-wide (S1274 §14 #36):** Zero JobContract / AGENT_MAP / task_routes / dedicated queue for revenue. Only PA tool `revenue_tracker_tool`. Cat E owned first half of arc-wide synthesis; Cat F owns second half (Income/Jobs lane) per D28.

**Load-bearing methodology outputs of S1405 (inherit at S1406):**

- **Parent-Claude verifier-loop 12/12 checkpoints CONFIRM** — matches S1404's 12-checkpoint count. **New pattern: broadened-grep with model-context disambiguation** (F.E1 `outcome='partial'` broadened grep found 2 hits at `tasks.py:6631` + `tasks_misc.py:162`; both PilotExecution model, unrelated to OpportunityOutcome; sub-agent claim UPHELD).
- **First library audit to ship with PARTIAL Rigby SIGN cycle 1** — worker instability across two fresh isolation pins blocked Batches 2-3 (F.E4-F.E10). D45 option (ii) accepted Batch 1 as SIGN-with-edits verdict; parent-Claude 12/12 verifier-loop as compensating quality gate.
- **First library audit to fold Rigby framing refinement at commit-time on dual-representation drift** — F.E3 gained "possible intentional dual-schema" alternative interpretation + R.E-3 ADR scope revised to two-part.
- **Rigby SIGN worker-instability failure mode documented** — placeholder-stall + generic-error pattern after 2 substantive turns; recovery pattern: mint fresh pin + reduce prompt size + explicit verdict-body request. Memory rules triggered: `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md`.

**Session close artifacts committed at S1405 close (this session):**

```
docs/research/domains/revenue/1405_revenue_attribution_analytics_audit.md   [new; 1489 lines / ~8.8k words; sign_status: SIGN-with-edits cycle 1 partial]
docs/research/domains/revenue/1400_revenue_domain_scoping.md                [modified — F.E4 + F.E6 anchor corrections at §3.E + §12.1]
docs/research/ARCHITECTURE_INDEX.md                                          [modified — v23 → v24; §1.27 S1405 row added; §8 timeline S1405 row added; frontmatter v24 preamble]
docs/research/OPEN_ARCS.md                                                   [modified — Group 1400 In-progress row current-child field rotated; owner-pin retained through S1405; §Recent reconciliations 2026-07-01 (S1405 close) entry added]
00-START-NEXT-SESSION.md                                                     [modified — this file]
docs/handoffs/SESSION_1405_REVENUE_ATTRIBUTION_ANALYTICS.md                  [new — session handoff]
```

Handoff: `docs/handoffs/SESSION_1405_REVENUE_ATTRIBUTION_ANALYTICS.md`.

### NEXT-SESSION MISSION — S1406 Child F (Freelance / Gig Opportunity subsystem — Income/Jobs lane per D25 F.i lock)

Per Group 1400 parent doc §5 child mission sequence + §12.1 Category F row + §3 Category F evidence surface + D25 F.i lock:

- **Session ID.** S1406.
- **Slot.** P6 (sixth child; consumes S1401 + S1402 + S1403 + S1404 + S1405 outputs).
- **Category.** F — Freelance / Gig Opportunity subsystem / Income-Jobs lane.
- **Branch.** `docs/session-1406-revenue-freelance-gig-income-jobs` off `main` post-S1405 merge.
- **Playbook §15 SIGN routing.** Full 20-section SIGN with fresh isolation pin per §15 stage table (S1406 SIGN pin minted at mid-session).
- **Playbook §13 sub-agent sweep.** 6 parallel Explore agents covering:
  1. **`FreelanceOpportunity` model** (`models_autonomous_situations.py:352`) — schema, writers, readers, lifecycle, docstring-vs-runtime drift, F.E1 STATUS_CHOICES lens application.
  2. **`intelligence/ai_job_matcher.py` + `intelligence/ai_job_application_pipeline.py`** — job matching + application pipeline; who invokes at runtime?
  3. **`intelligence/agent_income_tools.py` + `intelligence/income_builder.py` + `intelligence/income_builder_automation.py`** — income tooling; F.E3 dual-representation pattern check for intelligence-side models.
  4. **`intelligence/income_builder_connector.py` + `intelligence/income_spider_orchestrator.py` + `intelligence/job_income_bridge.py`** — connectors + orchestrator + bridge; write/read registry.
  5. **`intelligence/job_scanner_consumer.py` + `intelligence/ai_resume_generator.py`** — job scanner consumer + resume generator; production-invoked or dormant?
  6. **Cross-arc ownership synthesis** — F.E10 ownership arc-wide synthesis: F.E10 Cat E half + Cat F Income/Jobs lane ownership recommendation (JobContract + AGENT_MAP + task_routes + dedicated queue). Resolves parent D28 Cat E + Cat F combined arc-wide synthesis.

- **Playbook §11.2 20-section template.** Full 20 sections; category F questions from parent §12.1 answered explicitly.

### Category F F.iii questions to answer (parent §12.1)

- Is the Income/Jobs lane (`FreelanceOpportunity` + 9-file `intelligence/` adjacency) actively driving income or dormant?
- Who produces FreelanceOpportunity rows?
- What is `income_builder_automation` + `income_spider_orchestrator` + `job_income_bridge` doing at runtime?
- Is `ai_resume_generator` production-invoked?
- **INHERITED from S1405:** How does Category F reason about F.E10 arc-wide runtime-owner-absent finding? Does Income/Jobs lane have its own ownership signals (JobContract / AGENT_MAP / task_routes / dedicated queue)?
- **INHERITED from S1405:** Does Income/Jobs lane exhibit F.E1 STATUS_CHOICES over-modeling? F.E2 phantom fields? F.E3 dual-representation drift?

### Two open decisions gating S1406 launch

- **D46 — Launch cadence.** (i) Launch S1406 next session (default lean; matches S1301–S1305 + S1401 D30 + S1402 D34 + S1403 D36 + S1404 D38 + S1405 D41 rhythm); (ii) parallelize S1406 + S1499 xx99 canonical summary (unusual — S1499 depends on S1406 completion per parent §5, so parallel is impossible). **Default lean: OPTION (i) — sequential.**
- **D47 — Arc pin retention.** (i) Retain `pa-34d43795e1b24bd3` for S1406 (default lean; matches D31/D33/D35/D37/D39/D42 retention rhythm; last child before S1499 xx99); (ii) mint fresh pin (Chris explicit call only). **Default lean: OPTION (i) — retain.**

Optional third + fourth decisions surfacing at S1406 open:

- **D48 (optional) — S1405 follow-up SIGN addendum timing.** Rigby SIGN worker instability blocked Batches 2-3 (F.E4-F.E10) at S1405. Three options: (i) retry follow-up SIGN as a separate PR pre-S1406 (adds Rigby SIGN addendum to §20.9 of S1405 audit); (ii) fold Batch 2-3 retry into S1406 opening SIGN if worker-stability signal is positive; (iii) defer to S1499 xx99 synthesis if worker instability persists. Chris explicit call at S1406 open.
- **D49 (optional) — T.C8 tool-timing carried from S1404.** Same three-checkbox surface (a) ToolCallRecord query + (b) bounded ORM row-count + (c) prod DB RPC config. S1405 D43 lean was minimal-blocking; S1406 may bring same evaluation. Default lean if no explicit Chris pick = (ii) minimal-blocking, matching S1405 discipline.

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview` (per Rigby local trap)
3. Check if S1405 artifact set was committed + merged to `main` between sessions — if yes, S1406 branches off `main`
4. Verify `pa-34d43795e1b24bd3` retention status (`session_tool.health_check`); expected `recommendation: continue` (or `strongly_recommend_fresh` per S1405 signal — disclose to Chris but retain per arc-continuity discipline)
5. Retire `pa-637331c5f9574a10` (S1405 batched-retry SIGN pin) via `session_tool.retire` if not yet retired post-merge
6. Resolve D46 (launch cadence) + D47 (arc pin retention) + optionally D48 (S1405 follow-up SIGN addendum timing) + D49 (T.C8 tool timing) with Chris via arc pin (D46+D47 default leans align with prior discipline — likely fast "agree all"; D48 warrants explicit Chris pick given Rigby SIGN worker-instability signal from S1405)
7. Create branch `docs/session-1406-revenue-freelance-gig-income-jobs` off `main`
8. Read parent doc §12.1 Category F row + §3 Category F evidence surface + §11.4 (15 inherited findings — do NOT rediscover) as the mission spec + D25 F.i lock (Income/Jobs lane, not just FreelanceOpportunity model)
9. Read S1401 §9 + S1402 §9 + S1403 §9 + S1404 §9 + S1405 §9 integration maps + S1405 F.E10 (arc-wide runtime-owner-absent; Cat F owns second half of synthesis) + S1405 F.E1 (STATUS_CHOICES lens) + S1405 F.E3 (dual-representation lens for intelligence-side models)
10. Launch playbook §13 6-parallel-Explore sweep on the 6 evidence surfaces named above
11. Draft `docs/research/domains/revenue/1406_revenue_freelance_gig_income_jobs_audit.md` per playbook §11.2 20-section template
12. Route to Rigby with full SIGN per playbook §15 stage table (full 9-question audit SIGN, not light); if worker instability recurs, apply S1405 D45 batched-recovery pattern preemptively
13. Fold Rigby SIGN edits + Chris ratification + commit + PR

---

## PA / Rigby context

- **Arc pin at session start:** `pa-34d43795e1b24bd3` (Group 1400 continuity — do NOT retire mid-arc; retires at S1499 canonical summary close or at Chris explicit direction).
- **S1405 SIGN pin retirement:** `pa-637331c5f9574a10` should be retired post-PR-merge via `session_tool.retire` (playbook §15 fresh isolation pin retirement rule).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin `pa-34d43795e1b24bd3`).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (S1405 lesson):** if Rigby generic-errors after 2 substantive turns on a fresh SIGN pin, apply S1405 D45 batched-recovery pattern preemptively — mint fresh pin + reduce prompt size to titles-only + explicit verdict-body request. Memory rules `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.

## Repo state at next-session open

- **Branch state (at S1405 close, before merge):** `docs/session-1405-revenue-attribution-analytics` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1405 handoff at `docs/handoffs/SESSION_1405_REVENUE_ATTRIBUTION_ANALYTICS.md`. Prior handoffs: SESSION_1404 (Group 1400 Child D Meeting + Close); SESSION_1403 (Group 1400 Child C Engagement Inbound); SESSION_1402 (Group 1400 Child B Outreach); SESSION_1401 (Group 1400 Child A Opportunity Discovery); SESSION_1400 (Group 1400 arc open); SESSION_1300–SESSION_1305 (Group 1300 children); SESSION_1399 (Group 1300 xx99 canonical summary).
- **ARCHITECTURE_INDEX version:** v24 (bumped this session with §1.27 S1405 + §8 timeline row + v24 preamble). Next bump at S1406 close (v25).
- **OPEN_ARCS state:** Group 1400 row in "In-progress" section, current-child field = "S1405 SIGN-with-edits cycle 1 partial (commit-gated per D45) + S1406 queued next."

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1405 artifact set is on `main` — if yes, S1406 branches off `main`; if no, continues stacking on `docs/session-1405-revenue-attribution-analytics`
- [ ] Verify `pa-34d43795e1b24bd3` health via `session_tool.health_check` (expect `continue` or `strongly_recommend_fresh` — if latter, disclose to Chris; arc-continuity discipline still applies)
- [ ] Retire `pa-637331c5f9574a10` (S1405 batched-retry SIGN pin) if still active
- [ ] Resolve D46 (S1406 launch cadence: sequential) + D47 (arc pin retention: retain) + optionally D48 (S1405 follow-up SIGN addendum timing) + D49 (T.C8 tool timing) with Chris via arc pin
- [ ] Create branch `docs/session-1406-revenue-freelance-gig-income-jobs` off `main`
- [ ] Read parent doc §12.1 Category F row + §3 Category F evidence surface + §11.4 inherited findings + S1401 §9 + S1402 §9 + S1403 §9 + S1404 §9 + S1405 §9 integration maps + S1405 F.E10 (arc-wide ownership) + S1405 F.E1 (STATUS_CHOICES lens) + S1405 F.E3 (dual-representation lens)
- [ ] Launch playbook §13 6-parallel-Explore sweep on the 6 evidence surfaces named in §NEXT-SESSION MISSION above
- [ ] Draft `1406_revenue_freelance_gig_income_jobs_audit.md` per playbook §11.2 20-section template
- [ ] Route to Rigby with full SIGN (9 canonical questions) per playbook §15 stage table; apply S1405 D45 batched-recovery preemptively if worker instability recurs
- [ ] Fold SIGN cycle edits + Chris ratification + commit + PR

## Reference — where to look

- **Group 1400 parent scoping doc:** `docs/research/domains/revenue/1400_revenue_domain_scoping.md` — start here for anything Group 1400
- **Group 1400 parent §5 mission sequence:** locked as A → B → C → D → E → F → xx99 (D24 + D25)
- **Group 1400 parent §3 Category F evidence surface:** FreelanceOpportunity + 9-file `intelligence/` adjacency (ai_job_matcher + ai_job_application_pipeline + agent_income_tools + income_builder + income_builder_automation + income_builder_connector + income_spider_orchestrator + job_income_bridge + job_scanner_consumer + ai_resume_generator)
- **Group 1400 parent §11.4 inherited findings:** 15 findings — do NOT rediscover
- **Group 1400 parent §12.1 Category F questions:** what S1406 audit must answer
- **S1401 Child A audit:** `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md`
- **S1402 Child B audit:** `docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md`
- **S1403 Child C audit:** `docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md`
- **S1404 Child D audit:** `docs/research/domains/revenue/1404_revenue_meeting_close_audit.md`
- **S1405 Child E audit:** `docs/research/domains/revenue/1405_revenue_attribution_analytics_audit.md` — Category E ↔ Category F seam evidence at §9 integration map (F.E10 arc-wide ownership gap Cat E half; Cat F owns second half); §14 F.E1 (STATUS_CHOICES lens for FreelanceOpportunity) + §14 F.E2 (phantom-field lens for intelligence-side 10-file surface) + §14 F.E3 (dual-representation lens for intelligence-side models); §19 R.E-1 (Revenue Employee JobContract ADR) + R.E-10 (S1499 xx99 unified plan candidates 5 tracks)
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template for S1406 audit + §13 6-parallel-Explore sweep + §14 evidence rules + §15 full-SIGN stage table + §16 commit policy)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v24:** `docs/research/ARCHITECTURE_INDEX.md`
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1400 In-progress row
- **AUDIT_FINDINGS.md #12:** canonical Celery deferred-by-policy list — cross-reference before classifying any Celery-task-dormancy finding
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Whole-platform architecture inventory §3.32 + §4.9:** Revenue Pipeline row + cross-domain flow (S1273 v2 Rigby-added)
- **Cross-domain integration audit §2.4 + §3.7 + §5.10 + §9.6 + §14 finding #36:** S1274 findings inherited by Group 1400 (Cat E owns first half of §14 #36 ownership synthesis; Cat F owns second half per D28)

## Doctor warnings to expect

- Inventory freshness (stale) — `python manage.py generate_platform_inventory --write` to refresh; S1405 does not update inventory rows (research audit only)
- Handoff numbering continuity — legitimate; S1306-S1398 skipped by intent per Rigby lean at S1300 close; Chris's arc-numbering convention preserved for Group 1400 (S1401-S1406 + S1499)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 is older than latest handoff (informational; S1399 §7 proposed narrative updates for a subsequent PR; Group 1400 does not touch narrative anchor)
- Docs cascade — run 4-step cascade (build_docs_index → build_rag_corpus → sync_docs_index_to_documents → embed_documents) + build_docs_provenance after S1405 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`
