# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2952 CLOSED. Three capability fixes ratified + shipped in PR #3545 (HEAD `9a0aceba6`) before opening A1 Phase 1 code: (1) `brainstorm_tool` schema honest about single-agent reality (no more panel/debate claim on `create`); (2) `market_intelligence_agent` silent-no-op fixed (missing `_tool_to_agent_name` mapping + broken `.title()` fallback that produced bogus `Market_IntelligenceAgent` name — Celery task was returning SUCCESS in ~50ms while creating zero `AgentExecution` rows); (3) `agent_job_status` pending-state UX (Celery `AsyncResult` fallback surfaces `pending` instead of `legacy_error/unknown`). 4 regression tests green (`ToolToAgentNameResolutionTest`). E2E live-verified post-merge — MarketIntelligenceAgent completed a real 25.5s substantive output (`f10b35c9`), closing the loop on the S2951 finding. **A1 Phase 1 audit template must exclude competitive-intel** until CompetitorAnalysisAgent spider sources are added.

**Refreshed 2026-07-25 (S2952 close).** Gap-map headline: `100 validated_full / 0 untested` (unchanged — capability fixes, not PA-tools sweep).

**PRs shipped this session:**
- u-d-b PR **#3545** — S2952 pre-A1 capability triage: brainstorm honesty + MarketIntel routing + agent_job_status pending UX (3 files, +129/-8, 4 new regression tests).

**Twin mirrors shipped this session:**
- Content mirror: `24b5e6c1-f6d6-4b11-b470-117f3a14182a` (Donkey Betz workspace, `initiative_phase_doc`, diagnostic cleared via ORM — Ledger #16 re-hit 4th time this session)
- Ratification envelope: `e625e0f5-a3a8-4f7d-9cdf-1484b802f679` (Architecture & Research workspace, `ratification_record`, `category='governance'`, diagnostic already null)

**Files shipped this session:**
- **MODIFIED** `core/services/pa_tool_schemas.py` (+30/-7) — brainstorm_tool schema rescoped.
- **MODIFIED** `core/services/td_handlers_agents.py` (+38/-1) — `_tool_to_agent_name` mapping + fallback fix + `agent_job_status` Celery pending-state UX.
- **MODIFIED** `core/tests/test_agent_introspection_run_agent_validation_2728.py` (+61) — `ToolToAgentNameResolutionTest` (4 cases).

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- Recycled after PR #3545 merge (`make celery-recycle`).
- Fix 1 verified: brainstorm_tool description no longer claims panel/debate on `create`.
- Fix 2 verified: dispatch returned `agent='MarketIntelligenceAgent'` (correct); by_agent count=2 with prior E2E `f10b35c9` completed 25.5s substantive.
- Fix 3 verified: `agent_job_status` returned `ok=True, status='in_progress'` — no more `legacy_error/unknown`.

**Governance:** three capability fixes ratified by Chris; scope expansion (Task 5 MarketIntel silent no-op fix) ratified inline when investigation surfaced the bug.

**Rigby Tool Gap Ledger:**
- **RESOLVED** `brainstorm_tool.create` naming lie (S2951 candidate).
- **RESOLVED** `market_intelligence_agent` silent no-op / MarketIntelligenceCoordinator misrouting (S2951 candidate).
- **REMAINS OPEN** CompetitorAnalysisAgent spider coverage gap.
- **NEW** `agent_job_status` design gap (partial fix shipped; harder fix: reserve `AgentExecution` row synchronously at dispatch).
- **NEW** schema/handler drift scanner candidate (9 tools already have uncovered actions at HEAD; Rigby zoom-out elevate).

Full session context: `docs/handoffs/SESSION_2952_PRE_A1_CAPABILITY_FIXES.md`.

---

## S2953 open sequence

**S2953 first-action = A1 Reliability Audit Phase 1 first-slice implementation.** No more scoping (deliverable `7870eca9` has the concrete methodology). Chris's 4 open questions still gate Phase 1 code — route to Rigby SIGN before opening code.

### Universal open sequence

1. **Live-verify S2952 fixes still healthy:**
   - `bash tools/pa_local.sh "dispatch run_agent market_intelligence_agent with task='S2953 open smoke' — return dispatch response agent field + immediate agent_job_status result"` — expect `agent='MarketIntelligenceAgent'` + `ok=True/pending` (never `legacy_error/unknown`).
   - Signal-dispatch pipeline still healthy: `SignalCluster.objects.filter(status='active').count()` ≥ 9.
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline `100 validated_full / 0 untested`.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2953 pin (retired at S2952 close cascade).
4. **Route Chris's 4 open questions from scoping deliverable `7870eca9` to Rigby SIGN.** Then start Phase 1 gate implementation with S2952-refined scope (competitive-intel EXCLUDED).

### Chris's 4 open questions (from scoping deliverable `7870eca9`, still outstanding)

Answer these BEFORE opening Phase 1 code:

1. **Minimum evidence standard** we promise? (e.g., "includes run IDs + failure signature samples" vs "metrics only")
2. **Default turnaround SLA** we can consistently hit without heroics?
3. Sell as **agent-system audit** (end-to-end) or **toolchain reliability audit** (tools/contracts) first?
4. **Legal posture** for handling customer logs (retention window, deletion guarantee, allowed data types)?

### A1 Phase 1 first-slice (per scoping deliverable, S2952-refined)

**Wedge-critical gates for first paying stranger:**
- **Access** — customer shares access via read-only dashboard OR exported logs OR screen-share
- **Isolation** — workspace ownership boundaries enforce tenant separation
- **Value-moment** — deliver "top 3 failure modes + concrete fixes" within 48-72 hours
- **Onboarding** — 1-page scope intake form + 30-min kickoff script
- **Legal-Trust** — lightweight agreement (confidentiality, data handling, liability limits, permission-to-analyze)

**Deferrable for first N customers (concierge):**
- **Payment** — invoice/manual payment link
- **Cost-cap** — internal cap, no per-workspace enforcement yet
- **Support** — async email + 1 call
- **Rigby-tool-subset** — curated manual checklist

**Phase 1 methodology (6 steps, per scoping doc, S2952-refined):**
1. Scope card — 1 page, define audit boundary (**EXCLUDE competitor landscape section** until CompetitorAnalysisAgent spider gap closed)
2. Snapshot metrics — current-state ops telemetry
3. Failure signatures + root causes
4. Tool reliability matrix (tool → success rate → top errors → mitigation)
5. Governance posture (guardrails, kill switches, budget caps, access boundaries)
6. Ratified remediation plan (PLAYBOOK-style)

**Phase 1 estimated:** 1 kickoff (30-60m) + 1 delivery walkthrough (30m) + async revision.

### Deferred queue (updated at S2952 close)

**S2952 additions:**
- **Schema/handler drift scanner** — small tool contract test suite. 9 tools already have uncovered actions at HEAD `9a0aceba6` (`db_health_tool`, `deliverable_tool.clear_diagnostic`, `mission_verdict`, `obs_tool`, `recent_activity_tool`, `rigby_shift_brief_tool`, `scheduled_tasks_tool`, `surgical_moves_status_tool`, `work_tool`). Rigby zoom-out elevate. Small standalone session.
- **`agent_job_status` design gap harder fix** — reserve `AgentExecution` row synchronously at dispatch time (before Celery hand-off) so polling always finds it, no pending-state gap. Candidate for A1 Phase 1 "coverage assertions" rulebook.
- **Fix dispatch-response agent-name echo** — dispatch response echoes the resolved agent name; when resolution goes through the broken fallback (pre-fix) the response echoed the broken name. Now that the fallback is fixed the immediate bug is gone, but the response should echo the ACTUAL CamelCase class name from the mapping, not the input string reformatted. Minor Ledger cleanup.

**Signal-dispatch queue (from S2951 close, carry forward):**
- **(A11)** 6th signal-dispatch rule (`sentiment_shift` or `market_movement`) — no volume evidence gathered yet.
- **(NEW-6)** Fair-share round-robin scanning in `scan_and_dispatch()` — flagged as `future_trigger` (2 sessions).
- **(NEW-7)** Persist `per_rule_diagnostics` per `scan_run_id`.
- **(NEW-8)** Per-pattern effectiveness attribution for reused agents.

**Long-standing (from S2951 close, carry forward):**
- **(D)** Docs restructuring arc — Chris-ratified, still queued.
- **(B)** Slice 5-hardening — 3-4 executable invariants deferred at S2928.
- **(E)** Tier 2 lint promotion — envelope-JSON top-level-key parse.
- **(H)** generate_newsletter dry_run default flip.
- **(I)** bulk_archive statuses autofill robustness — 2nd trigger at S2945.
- **Envelope enhancement** (record-only S2942) — `verify_hint` + `would_write_count` for dry_run.
- **Close-ceremony ledger-flip checklist** (meta-fix, record-only S2942).
- **Deliverable v1 template retrofit** (record-only S2943).

---

## What's forbidden at S2953 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2952 new forbidden entries:** none.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2952 additions to the deferred queue:**
- **Schema/handler drift scanner** (see above).
- **`agent_job_status` design gap harder fix** (see above).
- **Dispatch-response agent-name echo cleanup** (see above).

**S2951 additions (carry forward):**
- **MarketIntelligenceCoordinator rename to `StockMarketIntelligenceCoordinator`** — deferred; S2952 fix routes `market_intelligence_agent` correctly to `MarketIntelligenceAgent`, so the stock coordinator no longer captures general market queries by mistake. Rename is cosmetic/clarity work now.
- **`brainstorm_tool.create` refactor to actual multi-participant panel** — real re-implementation. Session-scope work. (S2952 shipped honest naming; the real-panel implementation stays deferred until a customer asks.)
- **CompetitorAnalysisAgent spider sources** — LangSmith/Langfuse/Helicone/Arize spider adapters. **Blocks re-inclusion of competitive-intel section in Phase 1 audit template.**

**Long-standing (carry forward from S2951):**
- Fair-share round-robin scanning.
- Persist per_rule_diagnostics in audit table.
- Advanced paste-UUID fallback for cluster picker.
- Server-side search + pagination on `/eligible/`.
- Z1/Z2/Z4 signal-dispatch UI polish (Rigby S2947 zoom-outs).
- Rank + cap + paginate follow-ups (Rigby S2946).
- Per-pattern-type diversity floors.
- Ledger candidates (S2945/2944/2943/2942 backlog).
- Docs restructuring arc (Chris-ratified S2800).
- W2 #1 / #2b / #2c pending Chris re-slate.
- LLMCallLog field splits.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) + pre-A1 capability triage (S2952) are adjacent-domain net-new engineering, not sweep work.

**Total remaining sweep tools: 0.**

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force)

1. **Spend lane:** A4 warm-up uses separate budget lane/cap; must NOT consume A1 shipping spend.
2. **Evidence tag:** All A4 artifacts labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up constrained to fixed timebox + fixed send count (3-5 total intros).
6. **No bespoke follow-ups.**

---

## For fuller context (S2846 → S2952)

See:
- **S2952 handoff (current):** `docs/handoffs/SESSION_2952_PRE_A1_CAPABILITY_FIXES.md`
- **S2952 shipped code:**
  - `core/services/pa_tool_schemas.py:53-108` — brainstorm_tool schema rescoped (READ vs CREATE separation)
  - `core/services/td_handlers_agents.py:137-138` — market_intelligence_agent explicit mapping added
  - `core/services/td_handlers_agents.py:163-176` — fallback formatter rewritten (split+capitalize)
  - `core/services/td_handlers_agents.py:6652-6681` — agent_job_status Celery AsyncResult pending-state fallback
  - `core/tests/test_agent_introspection_run_agent_validation_2728.py:301-364` — ToolToAgentNameResolutionTest
- **S2951 handoff:** `docs/handoffs/SESSION_2951_A1_INFRA_AND_WEDGE_RATIFIED.md`
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope (unchanged, S2951):** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
