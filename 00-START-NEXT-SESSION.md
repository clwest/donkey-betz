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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1403 close:**

- **Active arc pin:** `pa-34d43795e1b24bd3` ("Session 1400 — Revenue research group (kickoff)"). Retained through S1401 + S1402 + S1403 per D31/D33/D35/D37; will carry S1404 → S1406 + S1499 continuity throughout Group 1400 arc. Do NOT retire mid-arc.
- **Recently retired at S1403 close:** `pa-fba0c4c81fba4922` (S1403 SIGN isolation pin; retire post-PR-merge via `session_tool.retire`).
- **Retired earlier at S1402 close:** `pa-4a0a28edcb7a45ec` (S1402 SIGN pin).
- **Retired earlier at S1401 close:** `pa-16d8b24d30e7a7d8` (S1401 SIGN pin).
- **Retired earlier at S1400 open:** `pa-aa54193f240f4846` (Group 1300 arc pin S1300-S1399) + `pa-4fc3329d0db6484f` (S1399 SIGN pin).
- **Next SIGN pin:** mint fresh isolation pin per playbook §15 stage table for S1404 Child D full-SIGN cycle 1.

Use `tools/pa_local.sh` for all chats unless you have a reason to override.

## READ THIS SECOND — GROUP 1400 REVENUE IN-PROGRESS; S1404 CHILD D IS NEXT MISSION

Session 1403 shipped the third Group 1400 child audit at `docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md` (Category C Engagement Inbound; 20-section playbook §11.2 template; Rigby SIGN-clean cycle 2 High confidence after cycle 1 fold — must-fix #1 empirically closed via parent-Claude Django ORM `.count()` + must-fix #2 withdrawn as Rigby's turn-1 narrative artifact + 4 Q-answer folds cycle 1 + 3 Q-answer folds cycle 2 + 2 nice-to-have folds). ARCHITECTURE_INDEX v21 → v22 bump landed same-commit (added §1.25 for S1403 child audit + §8 timeline S1403 row).

**Load-bearing S1403 outputs to inherit at S1404 open:**

- **F.C1 ingestion path missing (CONFIRMED HIGH at CODE + RUNTIME LOCAL, PROD unknown):** `EngagementEvent.objects.count() = 0` empirically confirms; extends S1402 F.B3 with `EngagementEvent.opportunity` FK second-writer-gap. Category D Meeting creation from EngagementEvent triggers presupposes this ingestion path — S1404 must design its Meeting-trigger flow WITH the F.B1→F.C1 sequential-ADR pair-design as a dependency.
- **F.C6 `run_ops_autopilot` deferred-by-policy (CONFIRMED via joint Rigby ops probe + parent-Claude direct read):** the beat wrapper is defined at `core/tasks.py:13090` with declared 10min cadence docstring but NOT registered as PeriodicTask (0 of 92 enabled rows; 30d `celery_task_history` → 0 firings); intentionally deferred per AUDIT_FINDINGS.md #12 gating (`core/celery.py:507-509` + `:633-634`). Ad-hoc PA-tool invocation LIVE at `td_handlers_ops.py:1643,1674`. Rigby cycle 2 Q1 lean **(iii) separate ADR outside G1400 arc** for enable-decision — cross-category impact spans all 6 Category A/B/C/D/E/F policy hooks. Category D policy hook `_policy_meeting_engine` (`core/services/ops_autopilot/core.py:~2240`) also fires only via same operator-initiated path, not autonomous cadence.
- **F.C2 corrected axis map (dual-sub-agent verified):** three independent surfaces — canonical EngagementEvent axis (runtime-empty at LOCAL), session-aggregation axis EngagementMetrics+OpportunityInteraction (WebSocket-consumer at `revenue_opportunities_consumer.py:849/527/694`), ContentEngagement (orthogonal). S1404 Meeting creation via `get_meeting_suggestions` reads from EngagementEvent axis — inherits the runtime-empty caveat.
- **F.C3 OpportunityInteraction F2 orphan-write CONFIRMED at `views_opportunities.py:56-65`:** REST `quick_apply()` omits `engagement_session` FK; runtime blast radius LOCAL = ZERO (0 rows). If Category D has REST-vs-WebSocket dual paths for Meeting creation, watch for the same pattern.
- **F.C4 ContentEngagement docstring drift + F.C5 EngagementAutonomyEngine "reply context builder" drift — both CONFIRMED:** documentation aspirational vs runtime. Category D should treat all model + service docstrings as claims requiring runtime verification.
- **T.C8 tool-surface gap** (three-checkbox: ToolCallRecord query + bounded ORM count + prod DB reach): Rigby cycle 2 Q8 lean **IMMEDIATE arc-support tools** (low-risk, high-leverage). Chris/Rigby should decide arc-open whether to land these tools before S1404 execution — they'd remove the local-only verifier-loop constraint that surfaced at S1403.

**Load-bearing methodology outputs of S1403 (inherit at S1404):**

- **Parent-Claude alternate-path direct-verification** — S1403 executed 11 direct-read + Rigby-joint checkpoints (up from S1402's 9). When Rigby's `db_health_tool` returned indeterminate `row_count=-1` (pg_class ANALYZE estimate) for must-fix #1, parent-Claude ran the count via `.venv/bin/python manage.py shell -c "from core.models_engagement import EngagementEvent; print(EngagementEvent.objects.count())"` on local env. Extends S1402 D.B7 joint-methodology from "confirmation" to "alternate-path direct-verification when Rigby tool returns indeterminate." If S1404 runs into same tool-surface gap, use same pattern (unless T.C8 arc-support tools land first).
- **Rigby cycle 2 withdraws own cycle-1 must-fix** — first library audit where Rigby explicitly accepted parent-Claude pushback on a must-fix that originated in her turn-1 narrative artifact (placeholder-stall from truncated read_file mid-fetch) rather than audit content. Extends verifier-loop from "hypothesis-correction / severity-correction / runtime-liveness-confirmation" to "audit-vs-narrative-artifact discrimination." Sets pattern: parent-Claude pushback on must-fix classification is a legitimate cycle-2 fold move when the must-fix originates in Rigby's response artifact not audit content. If S1404 SIGN cycle 1 truncation recurs at Rigby's tool layer, use recovery pattern from S1402 (verbatim + inference + independent probe/read verification) — do NOT ask Rigby to regenerate verbatim (fails on token budget).
- **Memory-rule cross-reference discipline** — S1403 triggered `feedback_audit_findings_12_canonical_celery_deferred_list.md` pre-SIGN to correctly classify F.C6 as INHERITED-BY-POLICY (not a new bug) before SIGN routing. If S1404 surfaces any Celery-task-invocation dormancy finding, cross-reference AUDIT_FINDINGS.md #12 immediately — same-day discovery of policy-deferred vs actual-orphan discrimination.

**Session close artifacts committed at S1403 close (this session):**

```
docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md   [new; 801 lines / ~11,149 words; status: draft → active on merge]
docs/research/ARCHITECTURE_INDEX.md                                       [modified — v21 → v22; §1.25 S1403 row added; §8 timeline S1403 row added; frontmatter v22 preamble]
docs/research/OPEN_ARCS.md                                                [modified — Group 1400 In-progress row current-child field rotated; owner-pin retained through S1403; §Recent reconciliations 2026-07-01 (S1403 close) entry added]
00-START-NEXT-SESSION.md                                                  [modified — this file]
docs/handoffs/SESSION_1403_REVENUE_ENGAGEMENT_INBOUND.md                  [new — session handoff]
```

Handoff: `docs/handoffs/SESSION_1403_REVENUE_ENGAGEMENT_INBOUND.md`.

### NEXT-SESSION MISSION — S1404 Child D (Meeting + Close)

Per Group 1400 parent doc §5 child mission sequence + §12.1 Category D row + §3 Category D evidence surface:

- **Session ID.** S1404.
- **Slot.** P4 (fourth child; consumes S1401 + S1402 + S1403 outputs at the seam where EngagementEvent triggers Meeting creation).
- **Category.** D — Meeting + Close.
- **Branch.** `docs/session-1404-revenue-meeting-close` off `main` post-S1403 merge.
- **Playbook §15 SIGN routing.** Full 20-section SIGN with fresh isolation pin per §15 stage table (S1404 SIGN pin minted at mid-session).
- **Playbook §13 sub-agent sweep.** 6 parallel Explore agents covering:
  1. **`Meeting` model** (`core/models_meeting.py:18`) — schema, writers, readers, lifecycle, docstring-vs-runtime drift check.
  2. **`ClosePack` model** (`core/models_close_pack.py:20`) — schema, assembly path, trigger conditions. Resolves S1273 §10.3 UNKNOWN #3.
  3. **`OpportunityAction` model** — relationship to Meeting/ClosePack; if it exists as a Meeting/ClosePack-adjacent surface.
  4. **`HumanAttentionItem` interlock** — approval-required conversion path; resolves S1274 §2.4 line 294 "Revenue → HumanAttention MISSING" classification.
  5. **`MeetingEngine`** (`core/services/ops_autopilot/engagement.py:~475` — sibling to EngagementEngine + EngagementAutonomyEngine per Agent 2 S1403 sweep). Read/write graph + policy hook wiring at `_policy_meeting_engine` (`core.py:~2240`).
  6. **Integrity audit design** — S1274 §5.10 flagged Outreach/Engagement/Meeting/Close tight-coupling as LOW-severity by design; Category D produces the integrity audit design proposal for the 4-model orphan-record risk (not implementation — design-preparation).
- **Playbook §11.2 20-section template.** Full 20 sections; category D questions from parent §12.1 answered explicitly.

### Category D F.iii questions to answer (parent §12.1)

- When does an EngagementEvent trigger a Meeting (auto vs manual)?
- How is ClosePack assembled + triggered? Resolves S1273 §10.3 UNKNOWN #3.
- Where does HumanAttention interlock (approval-required conversion)? Resolves S1274 §2.4 line 294 MISSING.
- What does the integrity audit design look like (S1274 §5.10 orphan-record risk)?
- **INHERITED from S1403:** Given F.C1 (EngagementEvent runtime-empty) + F.C6 (autonomous cadence deferred), how does Category D reason about Meeting-trigger runtime liveness? Meeting creation from Engagement presupposes engagement rows exist AND the trigger cadence fires. Both are runtime-empty/dormant in probed env.

### Two open decisions gating S1404 launch

- **D38 — Launch cadence.** (i) Launch S1404 next session (default lean; matches S1301–S1305 + S1401 D30 + S1402 D34 + S1403 D36 rhythm); (ii) parallelize S1404 + S1405 via isolation-pin split (unusual — Chris explicit call only). **Default lean: OPTION (i) — sequential.**
- **D39 — Arc pin retention.** (i) Retain `pa-34d43795e1b24bd3` for S1404 (default lean; matches D31/D33/D35/D37 retention rhythm); (ii) mint fresh pin (Chris explicit call only). **Default lean: OPTION (i) — retain.**

Optional third decision surfacing at S1404 open:

- **D40 (optional) — T.C8 tool-surface gap timing.** Rigby S1403 cycle 2 Q8 sharpened lean: **IMMEDIATE if it blocks verifier-loop / runtime-liveness confirmation; otherwise bundle with Group 1700 Observability.** Three checkboxes: (a) ToolCallRecord query surface — needed if S1404 wants 30d PA-tool usage counts for Meeting/MeetingEngine actions; (b) bounded ORM row-count — needed if S1404 verifier-loop hits an indeterminate DB probe (S1403 pattern with EngagementEvent `.count()`); (c) prod DB RPC configuration (PA_DB_HEALTH_RPC_URL + PA_DB_HEALTH_RPC_CLIENT_TOKEN) — needed if S1404 wants to confirm PROD Meeting/ClosePack row counts (S1403 blocked here). Options: (i) land (a)+(b)+(c) BEFORE S1404 execution — removes local-only verifier-loop constraint fully; (ii) land only what's blocking S1404 specifically after §13 sub-agent sweep reveals which gaps matter; (iii) defer full set to Group 1700 Observability (matches parent §12.4 deferred adjacent arcs). Chris explicit call at S1404 open; default lean if no explicit Chris pick = (ii) minimal-blocking landing.

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview` (per Rigby local trap)
3. Check if S1403 artifact set was committed + merged to `main` between sessions — if yes, S1404 branches off `main`
4. Verify `pa-34d43795e1b24bd3` retention status (`session_tool.health_check`); expected `recommendation: continue`
5. Retire `pa-fba0c4c81fba4922` (S1403 isolation pin) via `session_tool.retire` if not yet retired post-merge
6. Resolve D38 (launch cadence) + D39 (arc pin retention) + optionally D40 (T.C8 tool timing) with Chris via arc pin (D38+D39 default leans align with prior discipline — likely fast "agree all"; D40 warrants explicit Chris pick)
7. Create branch `docs/session-1404-revenue-meeting-close` off `main`
8. Read parent doc §12.1 Category D row + §3 Category D evidence surface + §11.4 (15 inherited findings — do NOT rediscover) as the mission spec
9. Read S1401 §9 integration map + S1402 §9 integration map + S1403 §9 integration map + S1403 F.C1 (ingestion missing — Meeting-trigger presupposition) + S1403 F.C6 (autonomous cadence deferred — Meeting policy hook dormancy)
10. Launch playbook §13 6-parallel-Explore sweep on the 6 evidence surfaces named above
11. Draft `docs/research/domains/revenue/1404_revenue_meeting_close_audit.md` per playbook §11.2 20-section template
12. Route to Rigby with full SIGN per playbook §15 stage table (full 9-question audit SIGN, not light)
13. Fold Rigby SIGN edits + Chris ratification + commit + PR

---

## PA / Rigby context

- **Arc pin at session start:** `pa-34d43795e1b24bd3` (Group 1400 continuity — do NOT retire mid-arc; retires at S1499 canonical summary close or at Chris explicit direction).
- **S1403 SIGN pin retirement:** `pa-fba0c4c81fba4922` should be retired post-PR-merge via `session_tool.retire` (playbook §15 fresh isolation pin retirement rule).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin `pa-34d43795e1b24bd3`).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.

## Repo state at next-session open

- **Branch state (at S1403 close, before merge):** `docs/session-1403-revenue-engagement-inbound` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1403 handoff at `docs/handoffs/SESSION_1403_REVENUE_ENGAGEMENT_INBOUND.md`. Prior handoffs: SESSION_1402 (Group 1400 Child B Outreach); SESSION_1401 (Group 1400 Child A Opportunity Discovery); SESSION_1400 (Group 1400 arc open); SESSION_1300–SESSION_1305 (Group 1300 children); SESSION_1399 (Group 1300 xx99 canonical summary).
- **ARCHITECTURE_INDEX version:** v22 (bumped this session with §1.25 S1403 + §8 timeline row + v22 preamble). Next bump at S1404 close.
- **OPEN_ARCS state:** Group 1400 row in "In-progress" section, current-child field = "S1403 SIGN-clean cycle 2 (commit-gated) + S1404 queued next."

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1403 artifact set is on `main` — if yes, S1404 branches off `main`; if no, continues stacking on `docs/session-1403-revenue-engagement-inbound`
- [ ] Verify `pa-34d43795e1b24bd3` health via `session_tool.health_check` (expect `recommendation: continue`)
- [ ] Retire `pa-fba0c4c81fba4922` (S1403 isolation pin) if still active
- [ ] Resolve D38 (S1404 launch cadence: sequential vs parallel-with-S1405) + D39 (arc pin retention: retain vs fresh mint) + optionally D40 (T.C8 tool-surface gap timing) with Chris via arc pin
- [ ] Create branch `docs/session-1404-revenue-meeting-close` off `main`
- [ ] Read parent doc §12.1 Category D row + §3 Category D evidence surface + §11.4 inherited findings + S1401 §9 + S1402 §9 + S1403 §9 integration maps + S1403 F.C1 (ingestion missing — Meeting-trigger presupposition) + S1403 F.C6 (autonomous cadence deferred)
- [ ] Launch playbook §13 6-parallel-Explore sweep on the 6 evidence surfaces named in §NEXT-SESSION MISSION above
- [ ] Draft `1404_revenue_meeting_close_audit.md` per playbook §11.2 20-section template
- [ ] Route to Rigby with full SIGN (9 canonical questions) per playbook §15 stage table
- [ ] Fold SIGN cycle edits + Chris ratification + commit + PR

## Reference — where to look

- **Group 1400 parent scoping doc:** `docs/research/domains/revenue/1400_revenue_domain_scoping.md` — start here for anything Group 1400
- **Group 1400 parent §5 mission sequence:** locked as A → B → C → D → E → F → xx99 (D24 + D25)
- **Group 1400 parent §3 Category D evidence surface:** Meeting + ClosePack + OpportunityAction + HumanAttention interlock + MeetingEngine + integrity audit design (S1274 §5.10)
- **Group 1400 parent §11.4 inherited findings:** 15 findings — do NOT rediscover
- **Group 1400 parent §12.1 Category D questions:** what S1404 audit must answer
- **S1401 Child A audit:** `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` — Category A ↔ Category B seam evidence at §9 integration map
- **S1402 Child B audit:** `docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md` — Category B ↔ Category C seam evidence + §14 D.B7 evaluate dead-code + §19 R.B1 delivery ADR (F.B1)
- **S1403 Child C audit:** `docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md` — Category C ↔ Category D seam evidence at §9 integration map (Engagement → Meeting READ-only surface via `EngagementAutonomyEngine.get_meeting_suggestions` at `engagement.py:832`; write direction is Category D scope); §14 D.C6 `run_ops_autopilot` deferred-by-policy; §19 R.C1 F.C1 ingestion path ADR (CENTRAL — sequential pair with F.B1); §19 R.C7 Governance §3.23 crossover (bundle with G1700)
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template for S1404 audit + §13 6-parallel-Explore sweep + §14 evidence rules + §15 full-SIGN stage table + §16 commit policy)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v22:** `docs/research/ARCHITECTURE_INDEX.md`
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1400 In-progress row
- **AUDIT_FINDINGS.md #12:** canonical Celery deferred-by-policy list — cross-reference before classifying any Celery-task-dormancy finding
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Whole-platform architecture inventory §3.32 + §4.9:** Revenue Pipeline row + cross-domain flow (S1273 v2 Rigby-added)
- **Cross-domain integration audit §2.4 + §3.7 + §5.10 + §9.6 + §14 finding #36:** S1274 findings inherited by Group 1400

## Doctor warnings to expect

- Inventory freshness (stale) — `python manage.py generate_platform_inventory --write` to refresh; S1403 does not update inventory rows (research audit only)
- Handoff numbering continuity — legitimate; S1306-S1398 skipped by intent per Rigby lean at S1300 close; Chris's arc-numbering convention preserved for Group 1400 (S1401-S1406 + S1499)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 is older than latest handoff (informational; S1399 §7 proposed narrative updates for a subsequent PR; Group 1400 does not touch narrative anchor)
- Docs cascade — run 4-step cascade (build_docs_index → build_rag_corpus → sync_docs_index_to_documents → embed_documents) + build_docs_provenance after S1403 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`
