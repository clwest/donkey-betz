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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1404 close:**

- **Active arc pin:** `pa-34d43795e1b24bd3` ("Session 1400 — Revenue research group (kickoff)"). Retained through S1401 + S1402 + S1403 + S1404 per D31/D33/D35/D37/D39; will carry S1405 → S1406 + S1499 continuity throughout Group 1400 arc. Do NOT retire mid-arc.
- **Recently retired at S1404 close:** `pa-87ee24cd0d3947ce` (S1404 SIGN isolation pin; retire post-PR-merge via `session_tool.retire`).
- **Retired earlier at S1403 close:** `pa-fba0c4c81fba4922` (S1403 SIGN pin).
- **Retired earlier at S1402 close:** `pa-4a0a28edcb7a45ec` (S1402 SIGN pin).
- **Retired earlier at S1401 close:** `pa-16d8b24d30e7a7d8` (S1401 SIGN pin).
- **Retired earlier at S1400 open:** `pa-aa54193f240f4846` (Group 1300 arc pin S1300-S1399) + `pa-4fc3329d0db6484f` (S1399 SIGN pin).
- **Next SIGN pin:** mint fresh isolation pin per playbook §15 stage table for S1405 Child E full-SIGN cycle 1.

Use `tools/pa_local.sh` for all chats unless you have a reason to override.

## READ THIS SECOND — GROUP 1400 REVENUE IN-PROGRESS; S1405 CHILD E IS NEXT MISSION

Session 1404 shipped the fourth Group 1400 child audit at `docs/research/domains/revenue/1404_revenue_meeting_close_audit.md` (Category D Meeting + Close; 20-section playbook §11.2 template; Rigby SIGN-clean cycle 2 High confidence after 4 must-fix folds cycle 1 + 2 nice-to-have folds cycle 2 — T.D5 CANDIDATE → F.D10 CONFIRMED HIGH promotion via joint Rigby broader-grep + parent-Claude direct-read disambiguation at revenue.py:1100-1180 + F.D7/F.D8/F.D9 parent-doc anchor corrections landing at commit-time + Q1-Q9 answers all folded). ARCHITECTURE_INDEX v22 → v23 bump landed same-commit (added §1.26 for S1404 child audit + §8 timeline S1404 row + frontmatter v23 preamble with load-bearing findings).

**Load-bearing S1404 outputs to inherit at S1405 open:**

- **F.D1 Meeting-trigger runtime liveness at LOCAL = ZERO CONFIRMED HIGH CODE + RUNTIME LOCAL** (Django ORM probe: Meeting=0, ClosePack=0, EngagementEvent=0). PROD unknown per T.C8(c). Category E Revenue Attribution readers may hit the same runtime-dormant seams — expect zero attribution rows at LOCAL.
- **F.D4 Revenue → HumanAttention CONFIRMED MISSING HIGH ARC-WIDE (extends B + C + D):** zero writers from any Meeting/ClosePack path create HAI; runtime probe confirms only 2 of 3061 HAI rows are from ops_autopilot (`_policy_revenue_pipeline` monitoring, NOT approval-interlock). Category E xx99 synthesis owns arc-wide HAI missing conclusion.
- **F.D10 ClosePack state machine PARTIAL CONFIRMED HIGH (paired with F.D6 Meeting analog):** writers exist for `draft` (default at `:991`), `approved` (`:1073` in `approve_pack`), `expired` (`:1173` bulk `.update()` in `ClosePackAutonomyEngine.evaluate`); `sent`/`won`/`lost` unreachable. Category E should probe `OpportunityRevenue` / `OpportunityOutcome` state machines for the same over-modeled-STATUS_CHOICES pattern.
- **F.D7 + F.D8 + F.D9 parent-doc drift corrections landing at S1404 commit-time** — parent §3.D updated to split ClosePack "writer" vs "monitoring" surfaces (CloseTheDealEngine vs ClosePackAutonomyEngine); remove MeetingCoordinatorAgent from Cat D primary systems (it's executive-agent facilitation); move OpportunityAction + OpportunityTask from Cat D to Cat A parallel action/task-state axis.

**Load-bearing methodology outputs of S1404 (inherit at S1405):**

- **Parent-Claude verifier-loop extended to 12 checkpoints** (up from S1403's 11). New pattern: **joint Rigby broader-grep + parent-Claude direct-read disambiguation for substring-ambiguous grep hits.** If S1405 encounters a Rigby grep with mixed `.create()` writes + `.filter()` READS, use same pattern.
- **First library audit to surface parent-doc drift as a load-bearing must-fix cluster** — 3 corrections in one audit (F.D7/F.D8/F.D9). Extends S1401 5-sub-agent-correction methodology from lateral-only (agent-vs-agent) to include upward-directed (parent-doc drift catches). If S1405 surfaces parent-doc drift, cross-reference this pattern for pre-SIGN routing.
- **§20.10 "Anchor corrections to upstream parent" subsection** — new subsection type. If S1405 surfaces parent-doc drift, use same immediate-fold discipline.
- **§20.11 Arc trajectory statement (Rigby verbatim):** "With Categories A/B/C/D now converging on (i) missing Revenue → HumanAttention approval/interlock, (ii) ownership gaps, and (iii) runtime-liveness breaks preventing Meeting/ClosePack from being populated, S1499 should synthesize a single 'activate the revenue lifecycle + enforce approval/attention gating' remediation plan." Category E adds attribution-lens findings to this trajectory.

**Session close artifacts committed at S1404 close (this session):**

```
docs/research/domains/revenue/1404_revenue_meeting_close_audit.md   [new; 1706 lines / ~13,369 words; status: draft → active on merge]
docs/research/ARCHITECTURE_INDEX.md                                  [modified — v22 → v23; §1.26 S1404 row added; §8 timeline S1404 row added; frontmatter v23 preamble]
docs/research/OPEN_ARCS.md                                           [modified — Group 1400 In-progress row current-child field rotated; owner-pin retained through S1404; §Recent reconciliations 2026-07-01 (S1404 close) entry added]
00-START-NEXT-SESSION.md                                             [modified — this file]
docs/handoffs/SESSION_1404_REVENUE_MEETING_CLOSE.md                  [new — session handoff]
```

Handoff: `docs/handoffs/SESSION_1404_REVENUE_MEETING_CLOSE.md`.

### NEXT-SESSION MISSION — S1405 Child E (Revenue Attribution + Analytics)

Per Group 1400 parent doc §5 child mission sequence + §12.1 Category E row + §3 Category E evidence surface:

- **Session ID.** S1405.
- **Slot.** P5 (fifth child; consumes S1401 + S1402 + S1403 + S1404 outputs at the seam where Meeting/ClosePack outcomes feed Revenue Attribution).
- **Category.** E — Revenue Attribution + Analytics.
- **Branch.** `docs/session-1405-revenue-attribution-analytics` off `main` post-S1404 merge.
- **Playbook §15 SIGN routing.** Full 20-section SIGN with fresh isolation pin per §15 stage table (S1405 SIGN pin minted at mid-session).
- **Playbook §13 sub-agent sweep.** 6 parallel Explore agents covering:
  1. **`OpportunityRevenue` model** (`models_unified_system.py:2613`) — schema, writers, readers, lifecycle, docstring-vs-runtime drift check, state-machine completeness (F.D10 lens application).
  2. **`OpportunityOutcome` model** (`models_unified_system.py:3394`) — schema, writers, readers, lifecycle, same F.D10 state-machine lens.
  3. **`OpportunityContent` model** (`models_unified_system.py:2805`) — schema + Cat E ownership.
  4. **`ops_autopilot/revenue.py` attribution logic + `ops_autopilot/impact.py`** — top-level revenue module + ImpactEvent emission (write/read registry); resolves S1274 §2.4 STRONG classification for Revenue → Observability.
  5. **`intelligence/revenue_integration.py` + `intelligence/revenue_tracking_bridge.py` + `learning_bridges/revenue_attribution_bridge.py`** — attribution bridges; resolves S1274 §4.3 Learning-bridge writes registry.
  6. **`views_revenue.py` + `views_revenue_analytics.py` + `views_revenue_tracking.py` + 4 frontend routes (revenue, revenue-dashboard, revenue-opportunities, opportunity-detail) + Celery beat `calculate-daily-revenue-metrics`** — 3 view files + 4 routes; resolves S1274 §14 finding #36 ownership gap (Cat E owns arc-wide ownership synthesis per D28).
- **Playbook §11.2 20-section template.** Full 20 sections; category E questions from parent §12.1 answered explicitly.

### Category E F.iii questions to answer (parent §12.1)

- What is the revenue attribution algorithm (`ops_autopilot/revenue.py`)? Resolves S1273 §3.32 UNKNOWN drift.
- How does `ImpactEvent` emission work (write/read registry)? Resolves S1274 §2.4 STRONG classification.
- How do 4 frontend routes + 3 view files serve distinct vs overlapping needs?
- What is the runtime owner recommendation (resolves S1274 §14 finding #36 HIGH)?
- **INHERITED from S1404:** Given F.D1 (Meeting/ClosePack runtime-empty at LOCAL) + F.D3 (ClosePack MANUAL trigger only) + F.D4 (arc-wide HAI missing) + F.D10 (ClosePack state machine PARTIAL — sent/won/lost unreachable), how does Category E reason about Revenue Attribution runtime liveness? Revenue attribution presupposes ClosePack `sent` → `won`/`lost` transitions that don't fire in code today.

### Two open decisions gating S1405 launch

- **D41 — Launch cadence.** (i) Launch S1405 next session (default lean; matches S1301–S1305 + S1401 D30 + S1402 D34 + S1403 D36 + S1404 D38 rhythm); (ii) parallelize S1405 + S1406 via isolation-pin split (unusual — Chris explicit call only). **Default lean: OPTION (i) — sequential.**
- **D42 — Arc pin retention.** (i) Retain `pa-34d43795e1b24bd3` for S1405 (default lean; matches D31/D33/D35/D37/D39 retention rhythm); (ii) mint fresh pin (Chris explicit call only). **Default lean: OPTION (i) — retain.**

Optional third decision surfacing at S1405 open:

- **D43 (optional) — T.C8 tool-surface gap timing.** Rigby S1404 cycle 1 Q8 sharpened lean: **LAND NOW pre-S1405.** Three checkboxes: (a) ToolCallRecord query surface — needed if S1405 wants 30d PA-tool usage counts for Revenue/Attribution actions; (b) bounded ORM row-count — needed if S1405 verifier-loop hits an indeterminate DB probe (S1403/S1404 pattern with EngagementEvent/Meeting/ClosePack `.count()`); (c) prod DB RPC configuration (PA_DB_HEALTH_RPC_URL + PA_DB_HEALTH_RPC_CLIENT_TOKEN) — needed if S1405 wants to confirm PROD Meeting/ClosePack row counts (S1403 + S1404 blocked here). Options: (i) land (a)+(b)+(c) BEFORE S1405 execution — removes local-only verifier-loop constraint fully (Rigby's SIGN cycle 1 Q8 lean at S1404); (ii) land only what's blocking S1405 specifically after §13 sub-agent sweep reveals which gaps matter; (iii) defer full set to Group 1700 Observability. Chris explicit call at S1405 open; default lean if no explicit Chris pick = (i) LAND NOW per Rigby S1404 cycle 1 Q8 lean.

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview` (per Rigby local trap)
3. Check if S1404 artifact set was committed + merged to `main` between sessions — if yes, S1405 branches off `main`
4. Verify `pa-34d43795e1b24bd3` retention status (`session_tool.health_check`); expected `recommendation: continue`
5. Retire `pa-87ee24cd0d3947ce` (S1404 isolation pin) via `session_tool.retire` if not yet retired post-merge
6. Resolve D41 (launch cadence) + D42 (arc pin retention) + optionally D43 (T.C8 tool timing) with Chris via arc pin (D41+D42 default leans align with prior discipline — likely fast "agree all"; D43 warrants explicit Chris pick given Rigby's S1404 cycle 1 Q8 lean was already "LAND NOW")
7. Create branch `docs/session-1405-revenue-attribution-analytics` off `main`
8. Read parent doc §12.1 Category E row + §3 Category E evidence surface + §11.4 (15 inherited findings — do NOT rediscover) as the mission spec
9. Read S1401 §9 + S1402 §9 + S1403 §9 + S1404 §9 integration maps + S1404 F.D1 (runtime empty — Cat E attribution readers hit same runtime-dormant seams) + S1404 F.D4 (arc-wide HAI missing — Cat E synthesis owns) + S1404 F.D10 (ClosePack state machine PARTIAL — probe OpportunityRevenue/OpportunityOutcome for same pattern)
10. Launch playbook §13 6-parallel-Explore sweep on the 6 evidence surfaces named above
11. Draft `docs/research/domains/revenue/1405_revenue_attribution_analytics_audit.md` per playbook §11.2 20-section template
12. Route to Rigby with full SIGN per playbook §15 stage table (full 9-question audit SIGN, not light)
13. Fold Rigby SIGN edits + Chris ratification + commit + PR

---

## PA / Rigby context

- **Arc pin at session start:** `pa-34d43795e1b24bd3` (Group 1400 continuity — do NOT retire mid-arc; retires at S1499 canonical summary close or at Chris explicit direction).
- **S1404 SIGN pin retirement:** `pa-87ee24cd0d3947ce` should be retired post-PR-merge via `session_tool.retire` (playbook §15 fresh isolation pin retirement rule).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin `pa-34d43795e1b24bd3`).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.

## Repo state at next-session open

- **Branch state (at S1404 close, before merge):** `docs/session-1404-revenue-meeting-close` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1404 handoff at `docs/handoffs/SESSION_1404_REVENUE_MEETING_CLOSE.md`. Prior handoffs: SESSION_1403 (Group 1400 Child C Engagement Inbound); SESSION_1402 (Group 1400 Child B Outreach); SESSION_1401 (Group 1400 Child A Opportunity Discovery); SESSION_1400 (Group 1400 arc open); SESSION_1300–SESSION_1305 (Group 1300 children); SESSION_1399 (Group 1300 xx99 canonical summary).
- **ARCHITECTURE_INDEX version:** v23 (bumped this session with §1.26 S1404 + §8 timeline row + v23 preamble). Next bump at S1405 close.
- **OPEN_ARCS state:** Group 1400 row in "In-progress" section, current-child field = "S1404 SIGN-clean cycle 2 (commit-gated) + S1405 queued next."

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1404 artifact set is on `main` — if yes, S1405 branches off `main`; if no, continues stacking on `docs/session-1404-revenue-meeting-close`
- [ ] Verify `pa-34d43795e1b24bd3` health via `session_tool.health_check` (expect `recommendation: continue` or `suggest_fresh` — if suggest_fresh, disclose to Chris; arc-continuity discipline still applies)
- [ ] Retire `pa-87ee24cd0d3947ce` (S1404 isolation pin) if still active
- [ ] Resolve D41 (S1405 launch cadence: sequential vs parallel-with-S1406) + D42 (arc pin retention: retain vs fresh mint) + optionally D43 (T.C8 tool-surface gap timing — Rigby's S1404 cycle 1 Q8 lean was LAND NOW) with Chris via arc pin
- [ ] Create branch `docs/session-1405-revenue-attribution-analytics` off `main`
- [ ] Read parent doc §12.1 Category E row + §3 Category E evidence surface + §11.4 inherited findings + S1401 §9 + S1402 §9 + S1403 §9 + S1404 §9 integration maps + S1404 F.D1 (runtime empty — Cat E readers) + S1404 F.D4 (arc-wide HAI missing — Cat E synthesis owns) + S1404 F.D10 (ClosePack state machine PARTIAL — extend lens to OpportunityRevenue/OpportunityOutcome)
- [ ] Launch playbook §13 6-parallel-Explore sweep on the 6 evidence surfaces named in §NEXT-SESSION MISSION above
- [ ] Draft `1405_revenue_attribution_analytics_audit.md` per playbook §11.2 20-section template
- [ ] Route to Rigby with full SIGN (9 canonical questions) per playbook §15 stage table
- [ ] Fold SIGN cycle edits + Chris ratification + commit + PR

## Reference — where to look

- **Group 1400 parent scoping doc:** `docs/research/domains/revenue/1400_revenue_domain_scoping.md` — start here for anything Group 1400
- **Group 1400 parent §5 mission sequence:** locked as A → B → C → D → E → F → xx99 (D24 + D25)
- **Group 1400 parent §3 Category E evidence surface:** OpportunityRevenue + OpportunityOutcome + OpportunityContent + ops_autopilot/revenue.py + ops_autopilot/impact.py + revenue_integration.py + revenue_tracking_bridge.py + revenue_attribution_bridge.py + 3 view files + 4 frontend routes + Celery beat calculate-daily-revenue-metrics
- **Group 1400 parent §11.4 inherited findings:** 15 findings — do NOT rediscover
- **Group 1400 parent §12.1 Category E questions:** what S1405 audit must answer
- **S1401 Child A audit:** `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` — Category A ↔ Category B seam evidence at §9 integration map
- **S1402 Child B audit:** `docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md` — Category B ↔ Category C seam evidence + §14 D.B7 evaluate dead-code + §19 R.B1 delivery ADR (F.B1)
- **S1403 Child C audit:** `docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md` — Category C ↔ Category D seam evidence at §9 integration map (Engagement → Meeting READ-only surface via `EngagementAutonomyEngine.get_meeting_suggestions` at `engagement.py:832`; write direction is Category D scope); §14 D.C6 `run_ops_autopilot` deferred-by-policy; §19 R.C1 F.C1 ingestion path ADR (CENTRAL — sequential pair with F.B1); §19 R.C7 Governance §3.23 crossover (bundle with G1700)
- **S1404 Child D audit:** `docs/research/domains/revenue/1404_revenue_meeting_close_audit.md` — Category D ↔ Category E seam evidence at §9 integration map (Meeting/ClosePack → Revenue Attribution PARKED at §9 rows 6+7; Cat E owns write registry); §14 D.D4/D.D8 F.D4 HAI arc-wide MISSING + F.D10 state-machine PARTIAL; §19 R.D6 HAI interlock ADR (stacked with F.B1 → F.C1); §19 R.D8 integrity audit design + CI guard smoke test (implementation POST F.B1/F.C1); §20.10 anchor corrections to upstream parent
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template for S1405 audit + §13 6-parallel-Explore sweep + §14 evidence rules + §15 full-SIGN stage table + §16 commit policy)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v23:** `docs/research/ARCHITECTURE_INDEX.md`
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1400 In-progress row
- **AUDIT_FINDINGS.md #12:** canonical Celery deferred-by-policy list — cross-reference before classifying any Celery-task-dormancy finding
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Whole-platform architecture inventory §3.32 + §4.9:** Revenue Pipeline row + cross-domain flow (S1273 v2 Rigby-added)
- **Cross-domain integration audit §2.4 + §3.7 + §5.10 + §9.6 + §14 finding #36:** S1274 findings inherited by Group 1400 (Cat E owns §14 #36 ownership synthesis per D28)

## Doctor warnings to expect

- Inventory freshness (stale) — `python manage.py generate_platform_inventory --write` to refresh; S1404 does not update inventory rows (research audit only)
- Handoff numbering continuity — legitimate; S1306-S1398 skipped by intent per Rigby lean at S1300 close; Chris's arc-numbering convention preserved for Group 1400 (S1401-S1406 + S1499)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 is older than latest handoff (informational; S1399 §7 proposed narrative updates for a subsequent PR; Group 1400 does not touch narrative anchor)
- Docs cascade — run 4-step cascade (build_docs_index → build_rag_corpus → sync_docs_index_to_documents → embed_documents) + build_docs_provenance after S1404 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`
