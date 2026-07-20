# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2854 CLOSE → PRICING CANONICALIZATION PHASE 1 SHIPPED (2026-07-20; picks up as S2855) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-20 (S2854 close).** One code PR shipped:
- **PR #3324** `73ed79281` — 7-way LLM-token pricing divergence collapsed into single source of truth at `core/services/pricing_catalog.py`. Every billing path (LLMCallLog write sites) reroutes through it. Ships **two real correctness fixes visible in production**: (1) Claude Haiku billing bug (was blended $0.25/1M on total tokens; now correctly split $0.25 input / $1.25 output — silently under-charged every Claude call on enforcer path); (2) Enforcer downgrade path (was hardcoded to gpt-5.2 rates even on gpt-5-mini downgrades since S2848 W1.5 — silent OVER-charge on every policy-downgraded call, ~3.3× too high). Display-only estimators annotated NOT BILLING, deferred to Phase 2.

**Working loop validated at S2854:**
- 1 Rigby pre-code design SIGN (task `c2cf8bb8…`) — 4Q + zoom-out; 8 `repo_tool` verifications; Rigby DISAGREED with Chris's initial B lean, recommended C+ split via coordination-trap argument; ratified verbatim by Chris
- 1 Rigby SIGN cycle on the diff (task `e23ec606…`) — 4Q + zoom-out; 10 `repo_tool` verifications; caught nothing to change; AGREE-TO-SHIP with one comment-wording refinement (applied)
- 15 new pytest cases + 38 pre-existing cost-related tests all green
- Pre-merge E2E direct handler + post-merge PA E2E via Rigby both confirm S2853 `downgrade_savings` figures ($0.000399 / $0.00301175 / $0.00261275) preserved through canonical module — full backward-compat
- Zero rubber-stamps; `tool_runs` verified non-empty on both dispatches
- Chris ratified scope shift via joint Claude+Rigby recommendation per `feedback_claude_rigby_agree_first_chris_yes_no`

**Session pin `pa-8e19c6fc3afe4396` RETIRES at S2854 close.** Fresh mint required at S2855 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2855 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-8e19c6fc3afe4396` retired at S2854 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2855-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2855

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **Phase 2 pricing canonicalization** (S2854 continuation) — migrate display estimators (`base_agent._call_openai:2593` + `_track_llm_analytics:2825`, `views_agent_dashboard.py:141`, `views_analytics.py:316`) to canonical `calculate_cost()`; reconcile `LLMCallLog.cost` ↔ `CostTracking.estimated_cost_usd` cost provenance semantics; add fact-table dimension for source-of-truth. Also: `core/management/commands/triage_spider_embeddings.py` embedding `* 0.02` inline (Rigby noted at SIGN as out-of-scope for Phase 1 but corpus-completeness item). ~3-5 hrs. Would benefit from Rigby SIGN on the "cost means" semantics BEFORE code.

2. **`was_downgraded` flag on `LLMCallLog`** (deferred from S2854) — migration required. Would let S2853's `downgrade_savings` distinguish enforcer-forced from natively-mini calls (final removal of OVER-estimate caveat). Design: nullable `was_downgraded` bool + `pre_downgrade_model_id` char field on `LLMCallLog`; enforcer sets both on the downgrade code path. ~1-2 hrs code + 1 migration + Rigby SIGN cycle.

3. **`autopilot_tool.history` expose evidence + result JSON** (S2850 Ledger #1, deferred from S2854) — currently returns row summary fields only. Operators can't see the `evidence.trigger` / `evidence.actor_user_id` / `result.reason` fields. Small addition (~1 hr): add `include_evidence=false` optional param.

4. **Auto-vs-operator event split for `enforcement_report`** (S2851 Q4b, still deferred) — add `auto_events` + `operator_events` counts per row using `evidence.trigger` from S2850 #3.0a. **Blocked on** validating evidence-completeness — confirm `trigger` is written on every `enforce_workspace_freeze` / `enforce_workspace_downgrade` / auto-clear path before publishing split counts. ~1 hr audit + ~1 hr code.

5. **PA-surface path to E2E-test llm_enforcer hot-path swap** (S2850 Ledger #2 — carried forward) — Rigby's calling agent is always `PersonalAssistant`, which bypasses workspace freeze/downgrade. To exercise the enforcer as a non-PA agent (for customer demos or operator verification), Claude currently drops to Django shell. Small addition (~2 hrs) — new PA tool action like `budget_tool.simulate_enforcement`.

6. **`clear_freeze`/`clear_downgrade` post-clear spend context** (carried forward from S2852 slate) — currently `clear_freeze` just deletes the flag; operator would have to re-call `get_status` afterwards. Inline the spend + re-flag likelihood in the response. ~30 min.

7. **N+1 in `list_caps` include_defaults=False path** (S2852 Rigby Q4 finding) — `ProjectWorkspace.objects.get(id=wid)` inside loop at `td_handlers_ops.py:4013`. Batch with `filter(id__in=[…]).in_bulk(field_name='id')` prefetch. ~30 min. Pre-existing.

8. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. After S2853+S2854, the substrate story is now: per-workspace enforcement fires immediately + audit trail correct + tracking accurate + fleet auditability visible + read surfaces auth-scoped + downgrade savings estimate visible + **Claude Haiku billing bug fixed + policy-downgraded calls now correctly priced**. A4 outreach can accurately claim substrate-completeness (with a slightly reduced OVER-estimate caveat on savings note).

### What's forbidden at S2855 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Multi-source `source_spider` filter (Ledger candidate; ~1 hour)
- SignalCluster naming rewrite (Ledger candidate; ~1 day)
- `huggingface` returns 0 SignalCluster rows (Ledger candidate; ~half day)
- `spider_status_tool.search` empty preview field (Ledger candidate; ~2 hours)
- `spider_status_tool.list` pagination (Ledger candidate; ~2 hours)
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2854 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail (both cycle-triggered and operator-triggered attributed correctly); (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total; **(i) all billing paths (LLMCallLog write sites) route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls now priced at effective_model rates (previously hardcoded to gpt-5.2).**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2854 close — what shipped (one code PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3324** `73ed79281` — pricing canonicalization Phase 1 (C+): canonical module + billing-path migrations + Haiku fix + downgrade correctness fix + display annotations
- **PR `<this docs cascade>`** — S2854 handoff + 00-START-NEXT-SESSION refresh + docs cascade

**Memory (Claude-authored):** No new memory entries at S2854; all rules reinforced by session evidence (Rigby-first comms; verify tool_runs; zoom-out ask; docs cascade at every close; recycle after merge; Claude directs / Rigby executes / Claude verifies; Rigby writes workspace deliverables).

**Workspace canonical:** Content mirror written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables`.

**Runtime impact:**
- `pricing_catalog` module now imports cleanly from `llm_enforcer` + `llm_provider_registry` (all 5 providers) + `ops_autopilot/pricing` (as shim) at import time
- gpt-5.2 enforcer path: uncached math unchanged; cached math unchanged; downgrade path NEWLY CORRECT (was silent over-charge)
- gpt-5-mini enforcer path: unchanged
- Claude Haiku enforcer path: NEWLY CORRECT (was silent under-charge)
- Router path OpenAI provider: gpt-5-mini +3.33× / gpt-5.2 -2.86× per call (aligned to enforcer's canonical rates)
- Migration 0392 applied — defensive no-op locally since LLMModel table is empty; will realign existing rows in any environment where they exist
- After recycle-after-merge, workers on SHA `73ed79281` serve canonical module

**Not shipped at S2854 close (deferred to S2855 or later):**
- Phase 2 of pricing canonicalization arc (display estimators + LLMCallLog↔CostTracking provenance reconciliation)
- Slate #2 `was_downgraded` flag on `LLMCallLog` (migration required)
- Slate #3 `autopilot_tool.history include_evidence` param
- All prior S2853-deferred items still queued (auto-vs-operator event split, PA-surface E2E for enforcer hot-path, N+1 in list_caps, clear_freeze spend context)

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2854)

See:
- **S2854 handoff (current):** `docs/handoffs/SESSION_2854_PRICING_CANON_PHASE_1_SHIPPED.md`
- **S2853 handoff:** `docs/handoffs/SESSION_2853_W2_3_2_DOWNGRADE_SAVINGS_SHIPPED.md`
- **S2852 handoff:** `docs/handoffs/SESSION_2852_LIST_CAPS_AUTH_TIGHTENED.md`
- **S2851 handoff:** `docs/handoffs/SESSION_2851_A1_W2_3_1_ENFORCEMENT_REPORT_SHIPPED.md`
- **S2850 handoff:** `docs/handoffs/SESSION_2850_A1_W2_ENFORCEMENT_CORRECTNESS_LEG.md`
- **S2849 handoff:** `docs/handoffs/SESSION_2849_A1_W2_DEFAULTS_BACKFILL_SHIPPED.md`
- **S2848 handoff:** `docs/handoffs/SESSION_2848_A1_W1_5_DOWNGRADE_TIER_SHIPPED.md`
- **S2847 handoff:** `docs/handoffs/SESSION_2847_A1_W1_PHASE3_SHIPPED.md`
- **S2846 handoff:** `docs/handoffs/SESSION_2846_A1_W1_PHASE1_PHASE2_SHIPPED.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`

For older session history (S1-S2845), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
