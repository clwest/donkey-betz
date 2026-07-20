# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2849 CLOSE → A1 W2 #2a SHIPPED; W2 SLATE OPEN (2026-07-20; picks up as S2850) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-20 (S2849 close).** One code PR shipped:
- **PR #3313** — A1 W2 #2a: workspace default cap + backfill. `set_default_cap`/`get_default_cap`/`backfill_defaults` PA tool actions; `get_effective_workspace_daily_cap()` in BudgetController with `explicit|default|unset` source tag; `list_caps include_defaults=true` shows every workspace with effective cap. Ship state: **16/16 workspaces now under enforcement at $5/day**, default_cap=$5.0, autopilot cycle iterates all 16 explicit caps (was 0 before).

**A1 W2 leg opens.** #2a completes the enforcement-substrate leg — every existing workspace has an explicit cap so autopilot's caps-only iteration (`_policy_budget_controller` at `core/services/ops_autopilot/core.py:1451`) actually fires per-workspace freeze/downgrade for the 16-workspace population.

**Working loop validated at S2849:**
- Rigby SIGN #1-#4 pre-code (12+ `repo_tool` calls; 3 substantive zoom-out folds; 1 F-BLOCKING adopted then withdrawn on evidence)
- Reframe A signed after ORM revealed 0.1% attribution rate: W1 complete as-designed (PA-path only + NULL-bucket global); W2 re-ordered to `#2a defaults+backfill → #3 reporting → #1 UX polish → #4 A4`
- Live E2E via Rigby caught 2 GPT function-calling bugs (empty include list + zero cap coercion); both fixed same-PR
- Zero rubber-stamps; audit trail verified via ORM cross-check (1× `workspace_default_cap_set` + 16× `workspace_cap_set`)

**Session pin `pa-507d1264765f4bf3` RETIRES at S2849 close** (seventy-ninth consecutive per S2770+ pattern). Fresh mint required at S2850 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2850 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-507d1264765f4bf3` retired at S2849 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2850-<first-action-context>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — W2 #3 Reporting scoping (recommended lean)

**#2a substrate is COMPLETE.** Rigby's ranked W2 slate has **#3 Reporting** as the next natural leap: daily/weekly per-workspace spend rollups. Reframed at S2849 as "budget status & enforcement reporting" (not "spend analytics") because attribution is still ~0.1% platform-wide.

**Concrete shape candidates for #3 (need Rigby SIGN before ratifying):**
- New PA tool action `workspace_budget_tool.spend_report` — args: `workspace_id | all`, `window: '24h'|'7d'|'30d'`, returns `[{workspace_id, name, spend, cap, effective_cap, cap_source, is_frozen, is_downgraded, enforcement_events_count}]`
- Or: new tool `workspace_reporting_tool` with actions `daily_rollup`, `weekly_rollup`, `enforcement_history` (audit trail slicing)
- Or: extend `autopilot_tool.budget_report` (existing global-spend report) with a per-workspace section

Recommend opening S2850 with a scoping SIGN dispatch on the #3 shape: Rigby ranks by (a) does it need new schema/index? (b) query-cost, (c) does it duplicate any existing `LLMCallLog` aggregation. Do NOT jump into implementation without ratification.

### Step 3 — Net-new engineering candidates for S2850

Per `feedback_engineering_bias_over_audit`, list net-new first at every session open.

0. **[SLATED FOR S2850] W2 #3 Reporting scoping** (Step 2 above). Highest-leverage next step — reporting is what makes enforcement observable.

1. **PA tool for AutopilotAction querying** (Rigby E2E STEP 13 gap from S2849) — no PA surface for `AutopilotAction.filter(policy='workspace_budget_tool')`; operators drop to Django shell to see "who did what." Small addition (~2 hours) as `governance_tool` extension or new `ops_audit_tool` action.

2. **Live E2E of llm_enforcer hot-path model swap** — verify a downgraded workspace routes non-critical LLM calls to `gpt-5-mini` in a single Rigby session (requires orchestrating the periodic cycle or manual override + live dispatch). ~1 hour. Deferred at S2848 close and S2849 close.

3. **`set_cap` immediate enforcement** (S2848 STEP 2 observation) — currently config-only; operator setting a tight cap on already-over-spend workspace has to wait ~10 min for autopilot cycle. Small addition (~1 hour): call `enforce_workspace_freeze` + `enforce_workspace_downgrade` immediately after `set_workspace_daily_cap` in the handler. Only ship if Chris directs.

4. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. A1 W1 substrate is now demonstrably complete AND per-workspace enforcement is live for 16/16 workspaces at $5/day. A4 outreach can start claiming enforcement substrate + operator surface + audit trail accurately. See §A4 Constraints below.

### What's forbidden at S2850 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending #3 completion or Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- Multi-source `source_spider` filter (Ledger candidate; ~1 hour)
- SignalCluster naming rewrite (Ledger candidate; ~1 day)
- `huggingface` returns 0 SignalCluster rows (Ledger candidate; ~half day)
- `spider_status_tool.search` empty preview field (Ledger candidate; ~2 hours)
- `spider_status_tool.list` pagination (Ledger candidate; ~2 hours)
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2849 close for #2a accuracy)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **After #2a:** every workspace including A4 now has $5/day default; operator can raise/lower via `set_cap` OR change the default via `set_default_cap` + `backfill_defaults`.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth" until drift-lint is shipped (S2846 ✓) AND A1 workspace attribution exists (S2846 ✓). **After #2a:** enforcement is now demonstrably live for all 16 existing workspaces at ratified default cap.
3. **No capability claims:** A4 outreach must make ZERO claims about invoicing, cost export, or SLA guarantees until further W2 items ship. **After #2a (2026-07-20):** claims about "per-workspace daily caps at operator-configurable default with backfill, auto-enforcement at 70% soft / 100% hard tiers with hysteresis, and full audit trail" are now accurate.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only (no "productized offering" language during the parallel period).
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros); no expansion without explicit slate change.
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables; allowed responses are one standard reply + optional meeting link only.

---

## S2849 close — what shipped (one code PR + one docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3313** `60ec5f75e` — A1 W2 #2a defaults + backfill (squash of `a74a9bdbc` + `167a9b34d`)
- **PR `<this docs cascade>`** — S2849 handoff + docs cascade refresh

**Memory (Claude-authored):** No new memory entries needed at S2849; existing rules all reinforced by session evidence.

**Workspace canonical:** Twin workspace mirror (content mirror + ratification envelope) — Rigby writes via PA tool per `feedback_rigby_writes_workspace_deliverables` at close.

**Runtime impact:**
- 3 new `workspace_budget_tool` actions (schema action-set grows 6 → 9); 1 handler surface additions
- 4 new `BudgetController` methods (default cap get/set, effective cap resolver, backfill orchestrator)
- 1 new `AutopilotAction` type (`workspace_default_cap_set`); 1 migration (`0391`)
- 16/16 workspaces now enforce at $5/day (was 0/16)
- Default cap `workspace_default_daily_cap=$5.0` in SystemConfiguration

**Not shipped at S2849 close (deferred to S2850 or later):**
- W2 #3 Reporting (Step 2 above)
- PA tool for AutopilotAction querying (Rigby E2E STEP 13 gap)
- Immediate-enforcement variant of set_cap (S2848 observation still open)
- Live E2E of llm_enforcer hot-path model swap
- W2 #1 UX polish / #2b templates / #2c ownership transfer / #4 A4 warm-up

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2849)

See:
- **S2849 handoff (current):** `docs/handoffs/SESSION_2849_A1_W2_DEFAULTS_BACKFILL_SHIPPED.md`
- **S2848 handoff:** `docs/handoffs/SESSION_2848_A1_W1_5_DOWNGRADE_TIER_SHIPPED.md`
- **S2847 handoff:** `docs/handoffs/SESSION_2847_A1_W1_PHASE3_SHIPPED.md`
- **S2846 handoff:** `docs/handoffs/SESSION_2846_A1_W1_PHASE1_PHASE2_SHIPPED.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md` (§0-§10)
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md` (§0-§13; §12 = D4 architecture, §13 = D4 picks)
- **Prior arc handoffs:** `SESSION_2841_STRATEGIC_DISCOVERY.md`, `SESSION_2842_S2841_RATIFIED_D0_D6.md`, `SESSION_2843_D4_DECOMPOSITION_RATIFIED.md`, `SESSION_2844_D4_PICKS_RATIFIED.md`, `SESSION_2845_SIGNAL_CLUSTER_SOURCE_FILTER_FIX.md`

For older session history (S1-S2840), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
