# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2850 CLOSE → A1 W2 ENFORCEMENT-CORRECTNESS LEG SHIPPED; #3.1 SLATED (2026-07-20; picks up as S2851) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-20 (S2850 close).** Two code PRs shipped:
- **PR #3315** — A1 W2 #3.0a: `set_cap` immediate enforcement. `workspace_budget_tool.set_cap` now fires `enforce_workspace_freeze` + `enforce_workspace_downgrade` immediately after writing the cap. Operator no longer waits ~10 min for the autopilot cycle. Both enforce methods gained optional `(actor_user_id, trigger)` params — when passed, AutopilotAction rows attribute to `agent_name='workspace_budget_tool'` with `evidence.trigger='operator_set_cap_immediate'` + `evidence.actor_user_id`. Autopilot cycle caller unchanged. Auto-clear-on-hysteresis branch also gets operator attribution when caused by an operator cap-raise (Rigby SIGN #4 Q2).
- **PR #3316** — A1 W2 #3.0c: llm_enforcer records ACTUAL model called, not requested. Fixes a silent tracking failure since S2848 W1.5 — every downgraded LLM call was persisting `LLMCallLog.model_id='gpt-5.2'` with gpt-5.2 pricing even though the API payload correctly sent `'model': 'gpt-5-mini'`. `_call_openai` + `_call_claude` now surface `effective_model` in their return dicts; caller reads it. Empirical impact: same 1721-token call cost recorded $0.003012 pre-fix vs $0.000399 post-fix — the actual API call was gpt-5-mini either way, only the tracking was wrong.

**A1 W2 enforcement-correctness leg CLOSED.** Rigby's SIGN #3 zoom-out reshaped the S2850 slate mid-session: "reporting is probably NOT the highest leverage next move ... higher-leverage adjacent work is *making enforcement behavior obvious and trustworthy at the point of action*." Chris ratified Reframe B (insert #3.0a + #3.0b ahead of #3.1). #3.0b E2E (Claude via Django shell) caught the tracking bug that led to #3.0c. Chris ratified Reframe C (insert #3.0c) after Rigby SIGN #5.

**Working loop validated at S2850:**
- 5 Rigby SIGN cycles, all tool-grounded (~20+ `repo_tool` calls total, real file+line evidence)
- One substantive zoom-out (SIGN #2 (c)) that reshaped the slate
- Three Rigby pushbacks incorporated: SIGN #4 Q2 (auto-clear operator attribution), SIGN #5 Q3.1 (semantic-shift docs inline), SIGN #5 Q3.3 (do NOT set `was_fallback=True`)
- Two Chris ratifications (Reframe B, Reframe C)
- Zero rubber-stamps; one real bug caught in E2E and fixed same-session
- Audit trail ORM-verified for every operator-triggered enforcement row (`evidence.trigger` + `evidence.actor_user_id` + `result.reason` cross-checked)

**Session pin `pa-abbd3c22650348b3` RETIRES at S2850 close** (eightieth consecutive per S2770+ pattern). Fresh mint required at S2851 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2851 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-abbd3c22650348b3` retired at S2850 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2851-a1-w2-3-1-reporting
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — W2 #3.1 `workspace_budget_tool.enforcement_report` (recommended lean — spec is IMPLEMENTATION-READY)

**No new scoping SIGN needed** — Rigby signed off on the shape in S2850 SIGN #3 (b) and refined it in SIGN #4. Chris deferred #3.1 to S2851 explicitly at S2850 close: "it's going to be a bigger step, let's start fresh."

**Ratified shape:**

Action: `workspace_budget_tool.enforcement_report`

Args (all optional):
- `workspace_id: string` (omit = all)
- `window: "24h" | "7d" | "30d"` (default `"24h"`)
- `include_spend: boolean` (default `false` — enforcement-forward; spend labeled as "attributed subset")
- `include_null_bucket: boolean` (default `true`)

Return shape:
```json
{
  "window": "24h|7d|30d",
  "note": "Spend numbers are workspace-attributed subset only; null-bucket reflects unattributed spend.",
  "null_bucket": { "spend_usd": <n>, "calls": <n> },
  "rows": [
    {
      "workspace_id": "uuid",
      "workspace_name": "string",
      "cap_usd": <n> | null,
      "effective_cap_usd": <n> | null,
      "cap_source": "explicit|default|unset",
      "attributed_spend_usd": <n> | null,
      "calls": <n> | null,
      "is_frozen": bool,
      "is_downgraded": bool,
      "enforcement_events_count": <n>,
      "last_enforcement_at": "iso8601|null"
    }
  ]
}
```

**Now-trustworthy inputs unlocked by S2850 #3.0c:** `LLMCallLog.model_id` reflects actual model called. #3.1 can optionally add per-workspace `downgrade_calls_count` (calls where `model_id=BUDGET_DOWNGRADE_MODEL`) and estimated cost savings vs `gpt-5.2` pricing. Consider whether to include in the base ship or a follow-up.

**Estimated scope:** ~2-3 hours, 1 PR. Zero migration. Reads existing indexes.

**Pre-code SIGN recommended:** Rigby confirms the query strategy (aggregation approach, index coverage for `AutopilotAction.filter(action_type__in=[...], created_at__gte=...)` in the window) + confirms whether to include the downgrade-savings section in v1 or defer.

### Step 3 — Net-new engineering candidates for S2851

Per `feedback_engineering_bias_over_audit`, list net-new first at every session open.

0. **[SLATED FOR S2851] W2 #3.1 enforcement_report** (Step 2 above). Highest-leverage — completes the ratified W2 sequence and makes S2850's enforcement work observable.

1. **PA-surface path to E2E-test llm_enforcer hot-path swap** (S2850 Ledger #2) — Rigby's calling agent is always `PersonalAssistant`, which bypasses workspace freeze/downgrade. To exercise the enforcer as a non-PA agent (for customer demos or operator verification), Claude currently drops to Django shell. Small addition (~2 hrs) — new PA tool action like `budget_tool.simulate_enforcement` that internally calls `enforcer.enforce_real_ai(agent_name='__budget_test__', ...)` with a test agent name explicitly whitelisted out of the critical-agents set.

2. **`autopilot_tool.history` expose evidence + result JSON** (S2850 Ledger #1) — currently returns row summary fields only (`agent_name`, `policy`, `action_type`, `timestamps`). Operators can't see the `evidence.trigger` / `evidence.actor_user_id` / `result.reason` fields that carry operator-triggered context. Small addition (~1 hr): add `include_evidence=false` optional param to `autopilot_tool.history`; when true, include full JSON. Useful for #3.1 report row detail views.

3. **`set_cap` immediate enforcement variant for `clear_freeze`/`clear_downgrade`** — parallel to #3.0a. Currently `clear_freeze` just deletes the flag; operators would need to run `get_status` afterwards to confirm state. Could inline a spend recompute + report if the cap is still below spend (i.e., "you cleared the freeze but spend is still above cap; it'll re-fire on the next cycle"). Small addition (~30 min).

4. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. After S2850, the substrate story is now: per-workspace enforcement fires on the spot + audit trail is correct + tracking is accurate. A4 outreach can accurately claim "policy routing to gpt-5-mini reduces cost 7-8x per downgraded call, tracked truthfully in every audit row."

### What's forbidden at S2851 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending #3.1 completion or Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` (S2850 SIGN #5 Q3.1 follow-up if operators actually need the requested-vs-effective distinction) — migration required
- `was_policy_reroute` field on `LLMCallLog` (S2850 SIGN #5 Q3.3 follow-up if any consumer needs to distinguish policy downgrade from error fallback) — migration required
- Multi-source `source_spider` filter (Ledger candidate; ~1 hour)
- SignalCluster naming rewrite (Ledger candidate; ~1 day)
- `huggingface` returns 0 SignalCluster rows (Ledger candidate; ~half day)
- `spider_status_tool.search` empty preview field (Ledger candidate; ~2 hours)
- `spider_status_tool.list` pagination (Ledger candidate; ~2 hours)
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2850 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (now fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth" until drift-lint is shipped (S2846 ✓) AND A1 workspace attribution exists (S2846 ✓). After S2850 #3.0c: cost tracking accurately reflects actual model used on every LLM call including downgraded ones.
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail (both cycle-triggered and operator-triggered attributed correctly); (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only (no "productized offering" language during the parallel period).
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros); no expansion without explicit slate change.
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables; allowed responses are one standard reply + optional meeting link only.

---

## S2850 close — what shipped (two code PRs + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3315** `d2941c51b` — A1 W2 #3.0a set_cap immediate enforcement
- **PR #3316** `22dc1a23f` — A1 W2 #3.0c llm_enforcer effective_model tracking fix
- **PR `<this docs cascade>`** — S2850 handoff + 00-START-NEXT-SESSION refresh + docs cascade

**Memory (Claude-authored):** No new memory entries needed at S2850; existing rules all reinforced by session evidence.

**Workspace canonical:** Content mirror written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables`. Two Rigby Tool Gap Ledger entries added.

**Runtime impact:**
- `workspace_budget_tool.set_cap` now returns `enforcement_fired` payload; existing consumers unaffected (additive field)
- 2 new `evidence.trigger` values recorded on freeze/downgrade rows: `'operator_set_cap_immediate'` (from #3.0a) — cycle-attributed rows now include `evidence.trigger='autopilot_cycle'` (new field, additive)
- `result.reason` values on `workspace_downgrade_cleared` rows: `'auto_hysteresis'` (unchanged) or `'operator_cap_change_hysteresis'` (new, S2850 #3.0a)
- `LLMCallLog.model_id` semantic shift: now = actual model called (post-downgrade), not requested. Downstream aggregations that treated it as "requested model" will silently shift semantics.
- 16/16 workspaces still enforce at $5/day (state unchanged from S2849 close)

**Not shipped at S2850 close (deferred to S2851 or later):**
- W2 #3.1 enforcement_report (Chris deferred at close — "bigger step, start fresh")
- PA-surface E2E path for llm_enforcer hot-path (S2850 Ledger #2)
- `autopilot_tool.history` evidence surface (S2850 Ledger #1)
- W2 #1 UX polish / #2b templates / #2c ownership transfer / #4 A4 warm-up

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2850)

See:
- **S2850 handoff (current):** `docs/handoffs/SESSION_2850_A1_W2_ENFORCEMENT_CORRECTNESS_LEG.md`
- **S2849 handoff:** `docs/handoffs/SESSION_2849_A1_W2_DEFAULTS_BACKFILL_SHIPPED.md`
- **S2848 handoff:** `docs/handoffs/SESSION_2848_A1_W1_5_DOWNGRADE_TIER_SHIPPED.md`
- **S2847 handoff:** `docs/handoffs/SESSION_2847_A1_W1_PHASE3_SHIPPED.md`
- **S2846 handoff:** `docs/handoffs/SESSION_2846_A1_W1_PHASE1_PHASE2_SHIPPED.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md` (§0-§10)
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md` (§0-§13; §12 = D4 architecture, §13 = D4 picks)
- **Prior arc handoffs:** `SESSION_2841_STRATEGIC_DISCOVERY.md`, `SESSION_2842_S2841_RATIFIED_D0_D6.md`, `SESSION_2843_D4_DECOMPOSITION_RATIFIED.md`, `SESSION_2844_D4_PICKS_RATIFIED.md`, `SESSION_2845_SIGNAL_CLUSTER_SOURCE_FILTER_FIX.md`

For older session history (S1-S2840), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
