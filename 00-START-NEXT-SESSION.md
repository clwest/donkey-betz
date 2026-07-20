# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2846 CLOSE → A4↔A1 SEQUENCING RATIFIED + A1 W1 PHASE 1 + PHASE 2 SHIPPED (2026-07-20; picks up as S2847) — **S2847 OPENS ON PHASE 3 (PA TOOL EXPOSURE + W1.5 DOWNGRADE-TIER) · D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-20 (S2846 close).** Five PRs shipped in-session (four merged, one merged during close ceremony):
- **PR #3303** — drift-lint (`check_pa_tool_drift` mgmt command; 114 tools scanned; 69 DRIFT / 43 CLEAN / 1 MISSING / 1 SOURCE_UNAVAILABLE)
- **PR #3304** — A4↔A1 sequencing RATIFIED (Chris D-verdict option (a): all 4 zoom-out folds accepted + 6-line constraints block codified)
- **PR #3305** — docs cascade refresh after #3304
- **PR #3306** — A1 W1 Phase 1: `LLMCallLog.workspace` FK + composite index + PA-path auto-attribution
- **PR #3307** — A1 W1 Phase 2: BudgetController per-workspace caps + `llm_enforcer` freeze hook

**A1 W1 SaaS substrate now demonstrably ships end-to-end for the PA path:**
- Attribution: PA dispatch → LLMCallLog row with `workspace=Donkey Betz [ACTIVE]` (verified live, S2846)
- Enforcement: frozen workspace blocks non-critical `TestAgent/general`; critical `PersonalAssistant/pa_chat` bypasses (verified live via `LLMEnforcer` runtime hook)
- Fold 2/3/4 guardrails applied inline (cap-keying policy documented in `budget.py` module comment; null-bucket handling explicit in `compute_workspace_spend`; no caching in W1)

**Working loop validated multiple times during S2846:**
- Rigby SIGN #1 (sequencing) — tool-grounded via `LLMCallLog.workspace` FK check + BudgetController.compute_spend signature read
- Rigby SIGN #2 (drift triage) — rubber-stamped; Claude re-fired with tool-grounded directive → Rigby SIGN #3 tool-grounded
- Claude verified Rigby's counter-claim on `active_repo_tool` → real drift-lint blind spot (`(payload or {}).get()` idiom) → fixed in-branch
- Claude verified Rigby's counter-claim on `autopilot_tool` → she was wrong (shallow read of 1800-line function); lint was correct

**Session pin `pa-5eec7b14a3a5482b` RETIRES at S2846 close** (seventy-sixth consecutive per S2770+ pattern). Fresh mint required at S2847 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2847 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-5eec7b14a3a5482b` retired at S2846 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2847-<first-action-context>
# e.g. s2847-a1w15-downgrade-tier, s2847-a1-pa-tool-exposure
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Continue A1 lane (Phase 3 or W1.5)

**A1 W1 substrate is complete for the PA path.** Two natural next chunks:

**Option A — Phase 3: PA tool exposure for cap management (~2–3 hours)**
Currently workspace caps + freezes are set only via Django shell. A `workspace_budget_tool` PA schema + handler would let Chris/Rigby manage caps conversationally:
- `set_cap(workspace_id, daily_cap_usd)` — creates `SystemConfiguration workspace_daily_cap:<uuid>`
- `get_status(workspace_id)` — returns compute_workspace_spend + cap + freeze status
- `clear_freeze(workspace_id)` — calls `BudgetController.clear_workspace_freeze`
- `list_workspaces_with_caps()` — inventory of configured caps
Add to `pa_tool_schemas.py` + `td_handlers_ops.py` (or new `td_handlers_budget.py`). Ship as separate PR; drift-lint should show it CLEAN.

**Option B — W1.5: downgrade-tier (~half day)**
Add `enforce_workspace_downgrade(spend, now, workspace_id)` — mirrors global downgrade-tier. When cap crosses soft threshold (say 70% of daily cap), set `workspace_downgrade_active:<uuid>` flag; `llm_enforcer._call_openai` reads flag + routes to cheaper model instead of blocking. Complements Phase 2's freeze-tier.

**Recommended sequence (Claude lean):** Phase 3 first (PA tool exposure — direct user-value, unblocks Rigby-driven testing of cap management), then W1.5 downgrade-tier. Chris to ratify at S2847 open.

### Step 3 — A4 warm-up under ratified constraints

Slate discipline from S2846 still in force (6-line constraints block below). Once A1 W1 substrate is demonstrably live for real (not just live E2E for one PA call), A4 warm-up work can start:
- Prospect list (5–15 named mid-size AI startups / enterprise AI ops teams)
- 3–5 pilot/concierge intro emails (constraints 4 + 5)
- Discovery via `intelligence_tool signal_clusters(source_spider=<name>)` — unblocked by S2845 fix

**A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force):**

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 Week 1 shipping spend.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth" until drift-lint is shipped (S2846 ✓) AND A1 workspace attribution exists (S2846 ✓ — constraint now RELAXABLE if used carefully).
3. **No capability claims:** A4 outreach must make ZERO claims about per-workspace caps, cost reporting, invoicing, or audit trails until A1 Week 1 ships (S2846 ✓ — enforcement layer in place, but no PA tool exposure yet).
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only (no "productized offering" language during the parallel period).
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3–5 total intros); no expansion without explicit slate change.
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables; allowed responses are one standard reply + optional meeting link only.

### Net-new engineering candidates for S2847

Per `feedback_engineering_bias_over_audit`, list net-new first at every session open.

0. **[SLATED FOR S2847] PA tool exposure for workspace budget management** (Option A above, ~2–3 hours). Highest-leverage next step — unblocks Rigby-driven cap testing + gives Chris conversational surface for what's currently shell-only.

1. **W1.5 downgrade-tier** (Option B above, ~half day). Mirrors global downgrade pattern; complements Phase 2's freeze-tier.

2. **Handler/schema drift-lint triage** — 69 DRIFT entries flagged in S2846. Rigby's SIGN bucketed some (REAL_BUG / SUB_HANDLER_FP / ALIAS_TOLERANT), but only 4/10 sampled were tool-verified before her timebox expired. A tight ~2-3 day arc could bucket + fix the top 10–15 REAL_BUG entries. (Chris interest signal at S2847 open determines priority.)

3. **Additional Rigby Tool Gap Ledger entries surfaced at S2846:**
   - `repo_tool` handler-body-locate timebox limitation (Rigby couldn't find 6/10 handler bodies within her tool timebox during drift triage)
   - Other tool-surface gaps as they surface

### What's forbidden at S2847 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- Multi-source `source_spider` filter (Ledger candidate; ~1 hour)
- SignalCluster naming rewrite (Ledger candidate; ~1 day)
- `huggingface` returns 0 SignalCluster rows (Ledger candidate; ~half day)
- `spider_status_tool.search` empty preview field (Ledger candidate; ~2 hours)
- `spider_status_tool.list` pagination (Ledger candidate; ~2 hours)

---

## S2846 close — what shipped (five PRs)

**Repo canonical (Claude-authored, in merge order):**
- **PR #3303** `81cde1d37` — `core/management/commands/check_pa_tool_drift.py` (drift-lint mgmt command, 404 lines; also rotates tools/pa_local.sh to S2846 pin)
- **PR #3304** `6c350a19b` — `00-START-NEXT-SESSION.md` refresh with A4↔A1 sequencing RATIFIED + 6-line constraints block codified + drift-lint promoted to SHIPPED
- **PR #3305** `7ee53e206` — `docs/INDEX.md` cascade refresh
- **PR #3306** `d6bdfe6cb` — A1 W1 Phase 1: LLMCallLog workspace FK + migration `0389_llmcalllog_workspace_fk_s2846` + threading via optional `user` kwarg + Fold 1 fallback logging in `workspace_resolver`
- **PR #3307** `d8ccd56d4` — A1 W1 Phase 2: BudgetController per-workspace caps (5 new methods) + `llm_enforcer` freeze hook + Fold 2/3/4 guardrails

**Memory (Claude-authored):** No new memory entries needed at S2846; existing rules (`feedback_verify_at_raw_orm_before_trusting_tool_no_data`, `feedback_rigby_tool_gap_ledger`, `feedback_verify_rigby_tool_runs_before_trusting_sign`, `feedback_read_full_rigby_response_not_just_tail`) all reinforced by session evidence.

**Workspace canonical:** No new workspace deliverables. A1 W1 is engineering work, not a ratifiable IOS arc close (per twin-canonical rule — ratifiable = IOS-scoped ADR ratifications, not shipping engineering).

**Runtime impact:**
- LLMCallLog rows from PA-path calls now carry workspace FK (verified live: `chris → Donkey Betz`)
- BudgetController.compute_workspace_spend + enforce_workspace_freeze + is_workspace_frozen wired
- `llm_enforcer.enforce_real_ai` gains freeze hook (verified live: `TestAgent/general` blocked, `PersonalAssistant/pa_chat` bypasses)

**Not shipped at S2846 close (deferred to S2847):**
- Phase 3 PA tool exposure for cap management (Django-shell-only today)
- W1.5 downgrade-tier for workspaces (Phase 2 shipped freeze-tier only)
- Drift-lint triage of the 69 DRIFT entries beyond the 4 Rigby sampled

---

## For fuller A4↔A1 + S2841 discovery context

See:
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` Step 2 (this file, above)
- **S2846 handoff:** `docs/handoffs/SESSION_2846_A1_W1_PHASE1_PHASE2_SHIPPED.md`
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md` (§0–§10)
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md` (§0–§13; §12 = D4 architecture, §13 = D4 picks)
- **Prior session handoffs:** `SESSION_2841_STRATEGIC_DISCOVERY.md`, `SESSION_2842_S2841_RATIFIED_D0_D6.md`, `SESSION_2843_D4_DECOMPOSITION_RATIFIED.md`, `SESSION_2844_D4_PICKS_RATIFIED.md`, `SESSION_2845_S2844_MISDIAGNOSIS_CORRECTED.md`

For older session history (S1–S2840), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
