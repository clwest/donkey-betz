# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2847 CLOSE → A1 W1 PHASE 3 SHIPPED (2026-07-20; picks up as S2848) — **S2848 OPENS ON W1.5 DOWNGRADE-TIER · D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-20 (S2847 close).** One code PR shipped:
- **PR #3309** — A1 W1 Phase 3: `workspace_budget_tool` — PA-manageable per-workspace budget cap + freeze management (5 actions: `set_cap` / `get_status` / `clear_freeze` / `list_caps` / `clear_cap`)

**A1 W1 SaaS substrate now feature-complete for the PA path:**
- Attribution (Phase 1, S2846) — `LLMCallLog.workspace` FK + PA-path auto-attribution
- Enforcement (Phase 2, S2846) — per-workspace caps + `llm_enforcer` freeze hook
- Operator surface (Phase 3, S2847) — `workspace_budget_tool` with auth + audit trail
- Only W1.5 downgrade-tier remains before A1 W1 is finished for A1 W2 scope

**Working loop validated at S2847:**
- Rigby SIGN #1 (pre-code) — tool-grounded via 6 `repo_tool` reads (BudgetController API grep + method extract + OpsHandlersMixin location); returned AGREE Q1-Q5 + REFINE Q6 + 5 substantive zoom-out concerns
- All F-BLOCKING folds adopted before code (auth + mutation audit)
- Live E2E via Rigby caught 2 bugs (UUID JSON serialization + `action_type` CharField overflow), fixed in-branch, re-verified
- Zero rubber-stamps this session; one F-BLOCKING pushback (auth + audit trail) adopted verbatim

**Session pin `pa-c944dd9ec7b94428` RETIRES at S2847 close** (seventy-seventh consecutive per S2770+ pattern). Fresh mint required at S2848 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2848 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-c944dd9ec7b94428` retired at S2847 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2848-<first-action-context>
# e.g. s2848-a1-w15-downgrade-tier, s2848-drift-lint-triage
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — W1.5 downgrade-tier (recommended lean)

**A1 W1 substrate is complete for the PA path except this last tier.** W1.5 mirrors Phase 2's freeze-tier — add a soft threshold that routes to a cheaper model BEFORE the hard freeze cuts in. Shape:

- `BudgetController.enforce_workspace_downgrade(spend, now, workspace_id)` — sets `SystemConfiguration key='workspace_downgrade_active:<uuid>'` when workspace spend crosses soft threshold (proposed: 70% of workspace cap, mirroring global `BUDGET_SOFT_LIMIT_PCT` = 0.70)
- `BudgetController.is_workspace_downgraded(workspace_id) -> bool` — hot-path check for `llm_enforcer`
- `BudgetController.clear_workspace_downgrade(workspace_id, actor_user_id=None)` — symmetric with `clear_workspace_freeze`
- `llm_enforcer._call_openai` extension — when target workspace is downgraded (and not frozen), swap requested model for `AutopilotConfig.BUDGET_DOWNGRADE_MODEL` before the API call
- `workspace_budget_tool.get_status.enforcement_tier` — flips from `'freeze_only'` to `'freeze_and_downgrade'` when workspace is downgrade-eligible (already forward-compat from Phase 3)
- **Design question for Rigby SIGN:** expose downgrade threshold via tool (new action or extend set_cap with optional `downgrade_pct` param), or keep threshold as global `AutopilotConfig` constant?

Estimated ~half day. One PR. Drift-lint must stay CLEAN. Live E2E: simulate spend at 70% of cap → verify workspace_downgrade_active flag written → dispatch a non-critical LLM call → verify llm_enforcer routed to downgrade model → clear_downgrade → dispatch same call → verify original model routed.

### Step 3 — A4 warm-up under ratified constraints

Slate discipline from S2846 still in force (6-line constraints block below). A1 W1 substrate is now demonstrably live end-to-end for the PA path — constraint 2 (evidence tag) and constraint 3 (no capability claims) are RELAXABLE for A4 outreach if carefully worded around Phase 3's operator surface. A4 warm-up work can start:
- Prospect list (5–15 named mid-size AI startups / enterprise AI ops teams)
- 3–5 pilot/concierge intro emails (constraints 4 + 5 still in force)
- Discovery via `intelligence_tool signal_clusters(source_spider=<name>)` — unblocked by S2845 fix

**A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force):**

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 Week 1 shipping spend. **After Phase 3:** operator can now cap the A4-workspace directly via `workspace_budget_tool.set_cap`.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth" until drift-lint is shipped (S2846 ✓) AND A1 workspace attribution exists (S2846 ✓). **After Phase 3:** operator surface exists — outreach can accurately describe cap management.
3. **No capability claims:** A4 outreach must make ZERO claims about per-workspace caps, cost reporting, invoicing, or audit trails until A1 Week 1 ships. **After Phase 3 (2026-07-20):** cap enforcement + audit trail + operator surface all shipped — claims about "per-workspace daily caps with owner/staff-gated management" are now accurate. Claims about "invoicing" remain out of scope (not shipped).
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only (no "productized offering" language during the parallel period).
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3–5 total intros); no expansion without explicit slate change.
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables; allowed responses are one standard reply + optional meeting link only.

### Net-new engineering candidates for S2848

Per `feedback_engineering_bias_over_audit`, list net-new first at every session open.

0. **[SLATED FOR S2848] W1.5 downgrade-tier** (Step 2 above, ~half day). Highest-leverage next step — completes A1 W1 substrate before A1 W2. Direct extension of Phase 3 work.

1. **Handler/schema drift-lint triage** — 69 DRIFT entries flagged in S2846. Rigby's SIGN bucketed some (REAL_BUG / SUB_HANDLER_FP / ALIAS_TOLERANT), but only 4/10 sampled were tool-verified before her timebox expired. A tight ~2-3 day arc could bucket + fix the top 10–15 REAL_BUG entries. (Chris interest signal at S2848 open determines priority.)

2. **AutopilotAction.ACTION_TYPES choices cleanup** — Phase 3 introduced `'workspace_cap_set'`, `'workspace_cap_cleared'`, `'workspace_freeze_cleared'` action_type values that are not in the model's `ACTION_TYPES` tuple (same precedent as S2846's `'workspace_budget_freeze'`). Low-priority cleanup PR to add all 4 to choices tuple in a docs+choices cascade.

3. **Additional Rigby Tool Gap Ledger entries surfaced at S2847:**
   - Bulk `workspace_budget_tool` operations (Rigby Q7 fold #5) — bulk_set_cap / set_cap_by_prefix for multi-workspace tenants
   - Rigby's `Duplicate tool call signature detected` PA safety mechanism bailed on iteration 4 during E2E of workspace_budget_tool full lifecycle (7 steps) — she completed 3 tool calls then loop broke. Not a tool bug; a PA-loop-limit note for multi-step operational scripts.

### What's forbidden at S2848 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- Multi-source `source_spider` filter (Ledger candidate; ~1 hour)
- SignalCluster naming rewrite (Ledger candidate; ~1 day)
- `huggingface` returns 0 SignalCluster rows (Ledger candidate; ~half day)
- `spider_status_tool.search` empty preview field (Ledger candidate; ~2 hours)
- `spider_status_tool.list` pagination (Ledger candidate; ~2 hours)

---

## S2847 close — what shipped (one code PR + one docs cascade)

**Repo canonical (Claude-authored, in merge order):**
- **PR #3309** `5ccd3ca26` — A1 W1 Phase 3: `workspace_budget_tool` (5 actions + auth + mutation audit + enforcement_tier forward-compat + timebox note + set-under-freeze warning); `BudgetController.set_workspace_daily_cap` + `clear_workspace_daily_cap` + `list_workspace_caps`; `clear_workspace_freeze` gains `actor_user_id` audit hook
- **PR `<this docs cascade>`** — S2847 handoff + docs cascade refresh

**Memory (Claude-authored):** No new memory entries needed at S2847; existing rules all reinforced by session evidence (see handoff §Memory).

**Workspace canonical:** No new workspace deliverables. Phase 3 is engineering work, not a ratifiable IOS arc close (per twin-canonical rule — ratifiable = IOS-scoped ADR ratifications, not shipping engineering).

**Runtime impact:**
- 158 tool handlers registered (up from 156 pre-Phase-3)
- SystemConfiguration `workspace_daily_cap:*` + `workspace_freeze_active:*` prefix keys now first-class managed via PA tool (previously shell-only)
- 5 AutopilotAction rows written during E2E — all with `actor_user_id` in evidence

**Not shipped at S2847 close (deferred to S2848):**
- W1.5 downgrade-tier (Step 2 above)
- Drift-lint triage of the 69 DRIFT entries beyond the 4 Rigby sampled
- Bulk workspace_budget_tool operations

---

## For fuller A4↔A1 + S2841 discovery context

See:
- **S2847 handoff (current):** `docs/handoffs/SESSION_2847_A1_W1_PHASE3_SHIPPED.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` Step 3 (this file, above)
- **S2846 handoff:** `docs/handoffs/SESSION_2846_A1_W1_PHASE1_PHASE2_SHIPPED.md`
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md` (§0–§10)
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md` (§0–§13; §12 = D4 architecture, §13 = D4 picks)
- **Prior session handoffs:** `SESSION_2841_STRATEGIC_DISCOVERY.md`, `SESSION_2842_S2841_RATIFIED_D0_D6.md`, `SESSION_2843_D4_DECOMPOSITION_RATIFIED.md`, `SESSION_2844_D4_PICKS_RATIFIED.md`, `SESSION_2845_SIGNAL_CLUSTER_SOURCE_FILTER_FIX.md`, `SESSION_2846_A1_W1_PHASE1_PHASE2_SHIPPED.md`

For older session history (S1–S2840), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
