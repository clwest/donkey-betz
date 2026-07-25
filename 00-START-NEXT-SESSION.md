# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2951 CLOSED. A1 WEDGE RATIFIED: **Reliability Audit** paid engagement at $500-$2,500 tiered. Chris D-verdict "Ship the Reliability Audit wedge" after live-orchestration proof (deliverable `83ee227e`): 7 specialist agents + brainstorm panel independently converged on "production-grade agent ops + governance layer" positioning. Enabling infra shipped in PR #3543: **new `agent_job_status` PA tool** (per Rigby's request), **ThinkingAgent async-context fix** (took 4 iterations — real root cause was sync ORM inside think() failing under asyncio.run; fix scopes `DJANGO_ALLOW_ASYNC_UNSAFE=true` around the call), and **`market_intelligence_agent` added to run_agent enum**. Wedge scoping deliverable `7870eca9` has 6-step methodology + 3-tier pricing + 9-gate wedge-critical vs deferrable map + smallest shippable Phase 1 slice. Real capability findings surfaced: brainstorm_tool.create claims panel but dispatches ThinkingAgent alone (Ledger candidate), CompetitorAnalysisAgent needs LangSmith/Langfuse/Helicone/Arize spider sources (data gap), deliverable_tool diagnostic-flag bug re-hit 3x (Ledger #31 still open).

**Refreshed 2026-07-24 (S2951 close).** Gap-map headline: `100 validated_full / 0 untested` (unchanged — infra + wedge ratification, not PA-tools sweep).

**PRs shipped this session:**
- u-d-b PR **#3543** — S2951 A1 infra: agent_job_status + ThinkingAgent async fix + market_intelligence_agent enum (4 files, +143/-9).

**Twin mirrors shipped this session:**
- Content mirror: `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6` (Donkey Betz workspace, `initiative_phase_doc`, diagnostic cleared via ORM) — A1 Wedge Scoping.
- Ratification envelope: `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b` (Architecture & Research workspace, `ratification_record`, `category='governance'`, diagnostic already null).
- Also: A1 v2 live-orchestration deliverable `83ee227e-451e-40af-bc71-d04faf20dcee` (Donkey Betz workspace, `market_research`, diagnostic cleared).

**Files shipped this session:**
- **MODIFIED** `core/agents/thinking_agent.py` (+53/-9) — extract `_execute_sync()`, DJANGO_ALLOW_ASYNC_UNSAFE scoped fix.
- **MODIFIED** `core/services/pa_tool_schemas.py` (+30) — `agent_job_status` schema + `market_intelligence_agent` enum.
- **MODIFIED** `core/services/td_handlers_agents.py` (+58) — `_handle_agent_job_status` method.
- **MODIFIED** `core/services/tool_dispatcher.py` (+2) — register both new handlers.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- Recycled after PR #3543 merge (`make celery-recycle`). Rigby confirmed `agent_job_status` visible + brainstorm dispatch returns `in_progress` (no immediate async error) + `market_intelligence_agent` in enum.

**Governance:** A1 wedge ratified by Chris. Twin mirrors done.

**Rigby Tool Gap Ledger new candidates:** (a) `brainstorm_tool.create` naming lie (says panel, dispatches ThinkingAgent alone), (b) `MarketIntelligenceCoordinator` should be renamed `StockMarketIntelligenceCoordinator` or general queries routed elsewhere, (c) `deliverable_tool.create` diagnostic-flag bug (Ledger #31) re-hit 3x this session.

Full session context: `docs/handoffs/SESSION_2951_A1_INFRA_AND_WEDGE_RATIFIED.md`.

---

## S2952 open sequence

**S2952 first-action = A1 Phase 1 implementation start.** Wedge scoping is done (deliverable `7870eca9`). No more scoping unless Chris explicitly redirects.

### Universal open sequence

1. **Live-verify infra still healthy:**
   - `agent_job_status` still in tool list: `bash tools/pa_local.sh "list your tools" 2>&1 | grep agent_job_status`
   - Brainstorm dispatch works: quick dispatch + `agent_job_status` poll
   - Signal-dispatch pipeline still healthy: `SignalCluster.objects.filter(status='active').count()` ≥ 9
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline `100 validated_full / 0 untested`.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2952 pin (retired at S2951 close cascade).
4. **Route Chris's 4 open questions from scoping doc to Rigby SIGN.** Then start Phase 1 gate implementation.

### Chris's 4 open questions (from scoping deliverable `7870eca9`)

Answer these BEFORE opening Phase 1 code:

1. **Minimum evidence standard** we promise? (e.g., "includes run IDs + failure signature samples" vs "metrics only")
2. **Default turnaround SLA** we can consistently hit without heroics?
3. Sell as **agent-system audit** (end-to-end) or **toolchain reliability audit** (tools/contracts) first?
4. **Legal posture** for handling customer logs (retention window, deletion guarantee, allowed data types)?

### A1 Phase 1 first-slice (per scoping deliverable)

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

**Phase 1 methodology (6 steps, per scoping doc):**
1. Scope card — 1 page, define audit boundary
2. Snapshot metrics — current-state ops telemetry
3. Failure signatures + root causes
4. Tool reliability matrix (tool → success rate → top errors → mitigation)
5. Governance posture (guardrails, kill switches, budget caps, access boundaries)
6. Ratified remediation plan (PLAYBOOK-style)

**Phase 1 estimated:** 1 kickoff (30-60m) + 1 delivery walkthrough (30m) + async revision.

### Deferred queue (updated at S2951 close)

**S2951 additions:**
- **Fix MarketIntelligenceCoordinator misrouting** — rename to `StockMarketIntelligenceCoordinator` OR investigate why enum add didn't cause Rigby to route to `market_intelligence_agent` in v2 orchestration.
- **Fix brainstorm_tool.create naming/behavior mismatch** — either rename to reflect single-ThinkingAgent behavior, OR actually implement multi-participant panel.
- **CompetitorAnalysisAgent spider coverage gap** — add LangSmith/Langfuse/Helicone/Arize sources for competitive intel in the agent-ops space.

**Signal-dispatch queue (from S2950 close, carry forward):**
- **(A11)** 6th signal-dispatch rule (`sentiment_shift` or `market_movement`) — no volume evidence gathered yet.
- **(NEW-6)** Fair-share round-robin scanning in `scan_and_dispatch()` — flagged as `future_trigger` (2 sessions).
- **(NEW-7)** Persist `per_rule_diagnostics` per `scan_run_id`.
- **(NEW-8)** Per-pattern effectiveness attribution for reused agents.

**Long-standing (from S2950 close, carry forward):**
- **(D)** Docs restructuring arc — Chris-ratified, still queued.
- **(B)** Slice 5-hardening — 3-4 executable invariants deferred at S2928.
- **(E)** Tier 2 lint promotion — envelope-JSON top-level-key parse.
- **(H)** generate_newsletter dry_run default flip.
- **(I)** bulk_archive statuses autofill robustness — 2nd trigger at S2945.
- **Envelope enhancement** (record-only S2942) — `verify_hint` + `would_write_count` for dry_run.
- **Close-ceremony ledger-flip checklist** (meta-fix, record-only S2942).
- **Deliverable v1 template retrofit** (record-only S2943).

---

## What's forbidden at S2952 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2951 new forbidden entries:** none.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2951 additions to the deferred queue:**
- **MarketIntelligenceCoordinator rename to `StockMarketIntelligenceCoordinator`** — real fix requires cascade check (Celery beat, PA tools, other agents referencing name). ~30 min.
- **`brainstorm_tool.create` refactor to actual multi-participant panel** — real re-implementation. Session-scope work.
- **CompetitorAnalysisAgent spider sources** — LangSmith/Langfuse/Helicone/Arize spider adapters.

**Long-standing (carry forward from S2950):**
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

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) are adjacent-domain net-new engineering, not sweep work.

**Total remaining sweep tools: 0.**

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force)

1. **Spend lane:** A4 warm-up uses separate budget lane/cap; must NOT consume A1 shipping spend. **S2951: minor A4-adjacent spend on live orchestration** (7 specialists + brainstorm panel = ~5 min agent compute for capability audit).
2. **Evidence tag:** All A4 artifacts labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up constrained to fixed timebox + fixed send count (3-5 total intros).
6. **No bespoke follow-ups.**

---

## For fuller context (S2846 → S2951)

See:
- **S2951 handoff (current):** `docs/handoffs/SESSION_2951_A1_INFRA_AND_WEDGE_RATIFIED.md`
- **S2951 shipped code:**
  - `core/agents/thinking_agent.py:1140-1230` — refactored `execute()` + `_execute_sync()` with DJANGO_ALLOW_ASYNC_UNSAFE scoped fix
  - `core/services/pa_tool_schemas.py:1362` — market_intelligence_agent enum add
  - `core/services/pa_tool_schemas.py:5709-5738` — agent_job_status schema
  - `core/services/td_handlers_agents.py:6620-6685` — `_handle_agent_job_status` method
  - `core/services/tool_dispatcher.py:363-404` — handler registrations
- **S2951 A1 wedge scoping deliverable:** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **S2951 A1 wedge ratification envelope:** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **S2951 A1 v2 live-orchestration deliverable:** `83ee227e-451e-40af-bc71-d04faf20dcee`
- **S2950 handoff:** `docs/handoffs/SESSION_2950_A10_5TH_DISPATCH_RULE.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
