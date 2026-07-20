# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2848 CLOSE → A1 W1 SUBSTRATE COMPLETE (2026-07-20; picks up as S2849) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-20 (S2848 close).** One code PR shipped:
- **PR #3311** — A1 W1.5: workspace downgrade-tier + Phase 2 auto-wire back-fill. `enforce_workspace_downgrade` at 70% cap with 60% hysteresis; back-wires Phase 2's `enforce_workspace_freeze` (which had no automatic caller since S2846); operator `clear_downgrade` action; 6 new AutopilotAction types (2 W1.5 + 4 Phase 2/3 backfill).

**A1 W1 SaaS substrate is now feature-complete for the PA path.** Four phases shipped across three sessions:
- **Phase 1 (S2846)** — attribution: `LLMCallLog.workspace` FK + PA-path auto-attribution
- **Phase 2 (S2846)** — enforcement plumbing: per-workspace freeze methods + `llm_enforcer` hot-path
- **Phase 3 (S2847)** — operator surface: `workspace_budget_tool` with 5 actions + auth + audit
- **Phase W1.5 (S2848)** — soft downgrade tier + Phase 2 auto-wire back-fill + `clear_downgrade` action

**Working loop validated at S2848:**
- Rigby SIGN #1 pre-code (task `984fe4c2`) — tool-grounded via 4 `repo_tool` calls (T1-T4); F-BLOCKING DISAGREE on Q4 (per-workspace `downgrade_pct`) adopted verbatim; 5 zoom-out folds, 3 shipped in-branch (hysteresis + fail-soft + zombie-safe)
- Live E2E via Rigby (task `1400c384`) — exercised 6 tool actions + audit trail verification; caught 1 Phase 3 designed-behavior observation (set_cap is config-only)
- Zero rubber-stamps; one F-BLOCKING pushback + one anomaly-pause (Rigby correctly halted at STEP 2 for design-question observation before continuing)

**Session pin `pa-1a4d45c9a947423d` RETIRES at S2848 close** (seventy-eighth consecutive per S2770+ pattern). Fresh mint required at S2849 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2849 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-1a4d45c9a947423d` retired at S2848 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2849-<first-action-context>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — A1 W2 scoping (recommended lean)

**A1 W1 substrate is COMPLETE.** The next natural leap is A1 W2 — but W2 was defined in the S2841 pressure-test addendum as a scope block that depends on W1 being finished. Time to un-shelve W2 scope.

**W2 candidates in rough priority order** (need Rigby SIGN before ratifying):
1. **Operator UX polish** — dashboard/status surface for workspace budget state (a Workspace tab, per `feedback_workspace_over_command_center_for_new_ui`, showing spend + cap + tier per workspace with quick actions)
2. **Multi-workspace policy** — cap templates, default cap for new workspaces, ownership transfer semantics
3. **Reporting** — daily/weekly per-workspace spend rollups (queryable via new PA tool action or new tool)
4. **A4 warm-up execution** — under S2846-ratified constraints, now that operator surface + auto-enforce are both live

Recommend opening S2849 with a scoping SIGN dispatch on the W2 candidate slate: Rigby ranks by leverage-per-day + risk, joint recommendation to Chris. Do NOT jump into implementation without ratification.

### Step 3 — Net-new engineering candidates for S2849

Per `feedback_engineering_bias_over_audit`, list net-new first at every session open.

0. **[SLATED FOR S2849] A1 W2 scoping** (Step 2 above). Highest-leverage next step — opens the W2 leg with proper Rigby pressure-test before code.

1. **Drift-lint triage** — 69 DRIFT entries flagged in S2846; still un-bucketed beyond the 4 Rigby sampled + workspace_budget_tool (which is CLEAN after Phase 3 and W1.5). ~2-3 day arc if Chris directs.

2. **`set_cap` immediate enforcement** (Rigby E2E STEP 2 observation, S2848) — currently config-only; operator setting a tight cap on already-over-spend workspace has to wait ~10 min for autopilot cycle to fire the flag. Small addition (~1 hour): call `enforce_workspace_freeze` + `enforce_workspace_downgrade` immediately after `set_workspace_daily_cap` in the handler. Only ship if Chris directs.

3. **Live E2E of llm_enforcer hot-path model swap** — verify a downgraded workspace routes non-critical LLM calls to `gpt-5-mini` in a single Rigby session (requires orchestrating the periodic cycle or manual override + live dispatch). ~1 hour. Deferred at S2848 close.

4. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. A1 W1 substrate is now demonstrably complete end-to-end; A4 outreach can start claiming operator surface + auto-enforce + audit trail accurately. See §A4 Constraints below.

### What's forbidden at S2849 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- Multi-source `source_spider` filter (Ledger candidate; ~1 hour)
- SignalCluster naming rewrite (Ledger candidate; ~1 day)
- `huggingface` returns 0 SignalCluster rows (Ledger candidate; ~half day)
- `spider_status_tool.search` empty preview field (Ledger candidate; ~2 hours)
- `spider_status_tool.list` pagination (Ledger candidate; ~2 hours)
- Bulk `workspace_budget_tool` operations (Ledger candidate from S2847)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2848 close for W1.5 accuracy)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **After W1.5:** operator can now cap A4-workspace directly via `workspace_budget_tool.set_cap` AND expect auto-enforcement at 70% (downgrade) / 100% (freeze) on the next periodic cycle.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth" until drift-lint is shipped (S2846 ✓) AND A1 workspace attribution exists (S2846 ✓). **After W1.5:** full A1 W1 substrate is live — enforcement + attribution + operator surface all demonstrably shipped end-to-end.
3. **No capability claims:** A4 outreach must make ZERO claims about invoicing, cost export, or SLA guarantees until A1 W2 ships. **After W1.5 (2026-07-20):** claims about "per-workspace daily caps with owner/staff-gated management + auto-enforcement at 70% soft / 100% hard tiers with hysteresis + full audit trail" are now accurate.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only (no "productized offering" language during the parallel period).
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros); no expansion without explicit slate change.
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables; allowed responses are one standard reply + optional meeting link only.

---

## S2848 close — what shipped (one code PR + one docs cascade)

**Repo canonical (Claude-authored, in merge order):**
- **PR #3311** `b5e7b3e98` — A1 W1.5 downgrade-tier + Phase 2 auto-wire back-fill
- **PR `<this docs cascade>`** — S2848 handoff + docs cascade refresh

**Memory (Claude-authored):** No new memory entries needed at S2848; existing rules all reinforced by session evidence (see handoff §Memory hits + adherence).

**Workspace canonical:** Twin workspace mirror (content mirror + ratification envelope for this engineering ship) — Rigby writes via PA tool per `feedback_rigby_writes_workspace_deliverables` at close.

**Runtime impact:**
- 158 tool handlers still (workspace_budget_tool action count went from 5 → 6 but is one handler); schema description grew
- SystemConfiguration `workspace_downgrade_active:*` prefix keys now first-class managed via PA tool + autopilot cycle
- 6 new AutopilotAction.ACTION_TYPES registered (2 W1.5 + 4 Phase 2/3 backfill)
- New autopilot cycle iteration: per-workspace-cap loop in `_policy_budget_controller`

**Not shipped at S2848 close (deferred to S2849 or later):**
- W2 scope (Step 2 above)
- Drift-lint triage of the 69 DRIFT entries
- Immediate-enforcement variant of set_cap (Rigby E2E observation)
- Live E2E of llm_enforcer hot-path model swap

---

## For fuller A1 W1 arc context (spans S2846 → S2848)

See:
- **S2848 handoff (current):** `docs/handoffs/SESSION_2848_A1_W1_5_DOWNGRADE_TIER_SHIPPED.md`
- **S2847 handoff:** `docs/handoffs/SESSION_2847_A1_W1_PHASE3_SHIPPED.md`
- **S2846 handoff:** `docs/handoffs/SESSION_2846_A1_W1_PHASE1_PHASE2_SHIPPED.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md` (§0-§10)
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md` (§0-§13; §12 = D4 architecture, §13 = D4 picks)
- **Prior arc handoffs:** `SESSION_2841_STRATEGIC_DISCOVERY.md`, `SESSION_2842_S2841_RATIFIED_D0_D6.md`, `SESSION_2843_D4_DECOMPOSITION_RATIFIED.md`, `SESSION_2844_D4_PICKS_RATIFIED.md`, `SESSION_2845_SIGNAL_CLUSTER_SOURCE_FILTER_FIX.md`

For older session history (S1-S2840), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
