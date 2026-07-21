# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2855 CLOSE → PRICING CANONICALIZATION PHASE 2A SHIPPED (2026-07-20; picks up as S2856) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-20 (S2855 close).** One code PR shipped:
- **PR #3326** `464985198` — 4 remaining display-only estimator sites + one embedding-cost inline formula migrated to canonical `pricing_catalog.calculate_cost`. Ships **two real correctness fixes visible in production**: (1) `base_agent._track_llm_analytics` was hardcoding `service='gpt-5-mini'` in CostTracking — every gpt-5.2 tool-using agent call was silently mis-attributed to gpt-5-mini + mispriced at $3/$12 per 1M (matched neither model). Now uses `self._last_llm_model` instance attr (avoiding subclass signature break) with fallback chain. (2) `base_agent._call_openai` accumulated cost display had same wrong rates — now canonical.

**Two display fallback estimators (`views_agent_dashboard`, `views_analytics`)** migrated from made-up blended rates ($0.375/1M and $10/1M) to canonical `calculate_cost('gpt-5-mini', tokens, 0, 0)` + explicit `estimated: true` JSON flag. Neither endpoint has any current frontend consumer (grep-verified) — additions fully backward-compatible.

**Embedding cost — single-source-of-truth preserved (Rigby zoom-out fold).** Rigby pre-code SIGN pushed back on adding `text-embedding-3-small` to `pricing_catalog.MODEL_PRICES`. `EMBEDDING_COSTS` already exists in `embedding_service.py:37-41` — Chat vs embedding pricing kept structurally separate. `triage_spider_embeddings.py` now imports from `embedding_service` directly.

**Docstring reconciliation** on `LLMCallLog` (billing plane) + `CostTracking` (analytics plane) — non-overlap invariant asserted; base_agent direct-client → CostTracking only; router/enforcer/embedding paths → LLMCallLog only.

**Working loop validated at S2855:**
- 1 Rigby pre-code design SIGN cycle (3 turns: initial + 2 follow-ups after Rigby's prose hedged "no repo_tool access" while her tool_runs showed 8 real repo_tool calls — called out per `feedback_verify_rigby_tool_runs_before_trusting_sign`)
- 1 Rigby post-code diff SIGN cycle (1 turn) — AGREE-TO-SHIP conditional on Q4 frontend grep; Claude closed Q4 independently
- 23 total `repo_tool` verifications across pre + post SIGN
- 25 pytest cases pass (17 pre-existing + 8 new across 4 new test classes) + 88 pass across broader cost surface
- Pre-recycle test suite + post-recycle Rigby E2E both confirm S2853 downgrade_savings + Phase 1 canonical rates preserved
- Chris ratified scope shift via joint Claude+Rigby recommendation per `feedback_claude_rigby_agree_first_chris_yes_no`

**Session pin `pa-dcbe01aef77b48d3` RETIRES at S2855 close.** Fresh mint required at S2856 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2856 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-dcbe01aef77b48d3` retired at S2855 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2856-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2856

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **`was_downgraded` flag on `LLMCallLog`** (deferred from S2854+S2855) — migration required. Would let S2853's `downgrade_savings` distinguish enforcer-forced from natively-mini calls (final removal of OVER-estimate caveat). Design: nullable `was_downgraded` bool + `pre_downgrade_model_id` char field on `LLMCallLog`; enforcer sets both on the downgrade code path. ~1-2 hrs code + 1 migration + Rigby SIGN cycle.

2. **`autopilot_tool.history` expose evidence + result JSON** (S2850 Ledger #1, deferred from S2854+S2855) — currently returns row summary fields only. Operators can't see the `evidence.trigger` / `evidence.actor_user_id` / `result.reason` fields. Small addition (~1 hr): add `include_evidence=false` optional param.

3. **Auto-vs-operator event split for `enforcement_report`** (S2851 Q4b, still deferred) — add `auto_events` + `operator_events` counts per row using `evidence.trigger` from S2850 #3.0a. **Blocked on** validating evidence-completeness — confirm `trigger` is written on every `enforce_workspace_freeze` / `enforce_workspace_downgrade` / auto-clear path before publishing split counts. ~1 hr audit + ~1 hr code.

4. **PA-surface path to E2E-test llm_enforcer hot-path swap** (S2850 Ledger #2 — carried forward) — Rigby's calling agent is always `PersonalAssistant`, which bypasses workspace freeze/downgrade. To exercise the enforcer as a non-PA agent (for customer demos or operator verification), Claude currently drops to Django shell. Small addition (~2 hrs) — new PA tool action like `budget_tool.simulate_enforcement`.

5. **`clear_freeze`/`clear_downgrade` post-clear spend context** (carried forward from S2852 slate) — currently `clear_freeze` just deletes the flag; operator would have to re-call `get_status` afterwards. Inline the spend + re-flag likelihood in the response. ~30 min.

6. **N+1 in `list_caps` include_defaults=False path** (S2852 Rigby Q4 finding) — `ProjectWorkspace.objects.get(id=wid)` inside loop at `td_handlers_ops.py:4013`. Batch with `filter(id__in=[…]).in_bulk(field_name='id')` prefetch. ~30 min. Pre-existing.

7. **Phase 2B pricing arc (only if reconciliation need surfaces)** — 4 deferred items from S2855 (see close doc §Not shipped): `model_kind` dimension, `EMBEDDING_COSTS`+`MODEL_PRICES` unification, `pricing_catalog_version` field on LLMCallLog, LLMCallLog↔CostTracking schema-level provenance column. Each individually small; none currently justified without a specific reconciliation trigger.

8. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. After S2853+S2854+S2855, the substrate story is now: per-workspace enforcement fires immediately + audit trail correct + tracking accurate + fleet auditability visible + read surfaces auth-scoped + downgrade savings estimate visible + Claude Haiku billing bug fixed + policy-downgraded calls correctly priced + **analytics-plane cost attribution now correct (was hardcoded to gpt-5-mini) + display fallbacks now canonical + embedding pricing SoT preserved**. A4 outreach can accurately claim full-substrate correctness across billing plane, analytics plane, and display fallbacks.

### What's forbidden at S2856 (D6 moratorium still in force)

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2855 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail (both cycle-triggered and operator-triggered attributed correctly); (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total; (i) all billing paths (LLMCallLog write sites) route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls now priced at effective_model rates (previously hardcoded to gpt-5.2); **(j) analytics-plane (CostTracking) cost attribution now correct — every gpt-5.2 tool-using agent call is attributed to gpt-5.2 in CostTracking rows (pre-S2855 was silently rewritten to gpt-5-mini); display fallback estimators use canonical rates with explicit `estimated: true` flag; embedding pricing single-source-of-truth preserved (embedding_service.EMBEDDING_COSTS).**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2855 close — what shipped (one code PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3326** `464985198` — pricing canonicalization Phase 2A: analytics plane migration + display fallback canonicalization + embedding-cost SoT preservation + docstring reconciliation
- **PR `<this docs cascade>`** — S2855 handoff + 00-START-NEXT-SESSION refresh + docs cascade

**Memory (Claude-authored):** No new memory entries at S2855; all rules reinforced by session evidence (Rigby-first comms; verify tool_runs; zoom-out ask; docs cascade at every close; recycle after merge; Claude directs / Rigby executes / Claude verifies; Rigby writes workspace deliverables; read full Rigby response not just tail).

**Workspace canonical:** Content mirror to be written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables` at S2856 open.

**Runtime impact:**
- `base_agent._call_openai` sets `self._last_llm_model` before every `_track_llm_analytics` call — subsequent CostTracking rows correctly attributed to `gpt-5.2` (tool-using agents) or `gpt-5-mini` (text-only) instead of universally `gpt-5-mini`
- `base_agent._call_openai` `_accumulated_cost` display now priced at canonical rates
- `views_agent_dashboard.agent_costs_data` + `views_analytics.cost_breakdown` fallback rates canonical + `estimated: true` flag; real per-call cost aggregates still supersede fallback
- `triage_spider_embeddings.py` dry-run cost estimate now imports from `embedding_service.EMBEDDING_COSTS` (single source of truth)
- After recycle-after-merge, workers on SHA `464985198` serve canonical module across billing plane + analytics plane + display fallbacks

**Not shipped at S2855 close (deferred to S2856 or later):**
- Phase 2B candidates (4 items): `model_kind` dimension, `EMBEDDING_COSTS`+`MODEL_PRICES` unification, `pricing_catalog_version` field, LLMCallLog↔CostTracking schema-level provenance column
- Slate #1 `was_downgraded` flag on `LLMCallLog` (migration required)
- Slate #2 `autopilot_tool.history include_evidence` param
- All prior S2854-deferred items still queued (auto-vs-operator event split, PA-surface E2E for enforcer hot-path, N+1 in list_caps, clear_freeze spend context)

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2855)

See:
- **S2855 handoff (current):** `docs/handoffs/SESSION_2855_PRICING_CANON_PHASE_2A_SHIPPED.md`
- **S2854 handoff:** `docs/handoffs/SESSION_2854_PRICING_CANON_PHASE_1_SHIPPED.md`
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
