# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2858 CLOSE → clear_* status_context + list_caps N+1 fix SHIPPED (2026-07-20; picks up as S2859) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-20 (S2858 close).** Chris-ratified bundle shipped as **two split PRs** (Rigby Q4 recommended split for blame localization):

- **PR #3333** `96e4798d4` — S2858 PR#1: inline `status_context` block on `clear_freeze` / `clear_downgrade` responses. Operators no longer have to re-call `get_status` to know if the flag will immediately re-fire. New `_status_context()` private helper encodes enforcer semantics: `re_flag_likely` computed against EXPLICIT cap only (not effective), so when `cap_source != 'explicit'` the bool is False + reason explains enforcement won't re-fire until `set_cap`/`backfill_defaults`. Notes flag "state flip only" so operators don't misread `cleared=true` as remediation.
- **PR #3334** `7a7bea22f` — S2858 PR#2: eliminate N+1 in `workspace_budget_tool.list_caps include_defaults=false`. Was: `ProjectWorkspace.objects.get()` per row. Now: two-pass batching — pass 1 collects `(row, uuid)` tuples + valid uuids; single `filter(id__in=uuids).values_list('id','name')` builds name dict; pass 2 uses dict lookup. Wire shape preserved (workspace_id stays string, missing rows → None-name).

**Working loop validated at S2858:**
- 1 combined pre-code SIGN cycle covering both PRs (6 grounded `repo_tool.read_file` calls, Q4 DISAGREE-with-mods → SPLIT PRs adopted, Q5 zoom-out surfaced 6 concerns with 4 folded same-PR into PR#1)
- 2 post-code SIGN cycles: PR#1 (7 grounded reads, AGREE-TO-SHIP all 5), PR#2 (3 grounded reads, AGREE-TO-SHIP all 5)
- 18 new pytest cases (12 PR#1 + 6 PR#2) + 26 S2857 regression = **44 total green**
- Post-recycle Rigby E2E: PR#1 confirmed `status_context` block wired end-to-end on `chris-personal` workspace; PR#2 confirmed `list_caps` returns 16 workspaces with intact wire shape
- Two new memory rules captured: `feedback_claude_stdout_truncation_vs_ui_truncation` + `feedback_per_pr_summary_signals_close_readiness`

**Session pin `pa-ce93e07302c946cf` RETIRES at S2858 close.** Fresh mint required at S2859 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2859 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-ce93e07302c946cf` retired at S2858 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2859-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2859

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **`simulate_enforcement` auto-clear-after-N-seconds** (S2857 first-trigger fold) — currently `dry_run=false` writes flags that persist until operator calls `clear_freeze`/`clear_downgrade`. Consider optional `auto_clear_after_seconds` param so a demo doesn't leave a workspace frozen if the operator forgets to clean up. Deferred — awaits explicit ask.

2. **`selected_fields` param for `autopilot_tool.history include_evidence`** (S2856 slate #3 Rigby Q5c zoom-out fold, first trigger observed — deferred until second trigger before Playbook amendment) — structured field selection over the JSONField payload. Blocked until concrete need surfaces.

3. **`enforcement_action_types` shared constant** (S2856 pre-code Q5b, first trigger observed) — de-duplicate the 4-item action-type list between `td_handlers_ops.py:4362` and `ops_autopilot/budget.py` write sites. ~1 hr refactor. Not urgent until a fifth type is added.

4. **`actor_user_id` as first-class column on `AutopilotAction`** (S2856 pre-code Q5a, first trigger — MIGRATION required). Deferred until schema-migration budget opens.

5. **`EnforcementContext` dataclass consolidation** (S2857 post-code Q5, first trigger observed) — `actor_user_id` + `trigger` + `simulated` (and growing) currently piped as kwargs on both enforce_ methods. Consolidate into an `EnforcementContext` dataclass. **Deferred** — awaits second independent trigger before Playbook amendment.

6. **`list_caps include_defaults=true` remaining perf costs** (S2858 Q5 concern 5, first trigger observed — deferred) — spend computation + is_frozen/is_downgraded lookups still per-row after PR #3334 batched the name lookup. Not urgent until fleet size makes it a slow ticket. Would extend the two-pass pattern from PR#2 to also batch SystemConfiguration reads.

7. **Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855: `model_kind` dimension, `EMBEDDING_COSTS`+`MODEL_PRICES` unification, `pricing_catalog_version` field on LLMCallLog, LLMCallLog↔CostTracking schema-level provenance column. None currently justified without a specific reconciliation trigger.

8. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. The substrate story now includes: per-workspace enforcement immediate + accurate audit trail + accurate tracking + fleet auditability + auth-scoped reads + downgrade savings estimate + Claude Haiku billing bug fixed + policy-downgraded calls priced correctly + analytics-plane attribution correct + display fallbacks canonical + embedding pricing SoT preserved + enforcer-forced downgrades cleanly distinguishable + operator vs autopilot enforcement events cleanly distinguishable + evidence/reason surfacing on autopilot audit history + operators + demo audiences can trigger enforcer against synthetic spend without shell access + **post-clear status_context inline on clear_* responses (no follow-up get_status needed) + list_caps read surface no longer degrades linearly with workspace count (PR #3333 + PR #3334)**.

### What's forbidden at S2859 (D6 moratorium still in force)

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2858 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`. S2857: operator can now verify enforcement without touching real spend via `simulate_enforcement`. **S2858: post-clear re-flag likelihood inline on clear_* responses; list_caps read surface no longer degrades linearly with workspace count.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail — cycle-triggered vs operator-triggered attributed correctly + auto_events_count vs operator_events_count now visible per-workspace in the fleet report; (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total — now cleanly filtered to enforcer-forced downgrades only; (i) all billing paths route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls priced at effective_model rates; (j) analytics-plane cost attribution correct; display fallbacks use canonical rates with explicit `estimated: true` flag; embedding pricing SoT preserved; (k) autopilot audit history (`autopilot_tool.history include_evidence=true`) surfaces evidence + result JSONField values inline for operators inspecting trigger / actor_user_id / reason; (l) operators + demo audiences can trigger the freeze + downgrade enforcer against a synthetic spend value via `workspace_budget_tool.simulate_enforcement` — dry-run reveals decisions + thresholds without state writes; live path writes real flags with `evidence.simulated=True` marker (excluded from fleet report by default); **(m) operators can now inspect post-clear re-flag likelihood inline on clear_freeze/clear_downgrade responses (no follow-up get_status call needed); status_context block encodes enforcer semantics with re_flag_likely tied to EXPLICIT cap only + explicit reason string; (n) workspace_budget_tool.list_caps read surface no longer degrades linearly with workspace count — batched name lookup via single filter().values_list() query regardless of row count.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2858 close — what shipped (two code PRs + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3333** `96e4798d4` — S2858 PR#1: clear_freeze/clear_downgrade status_context (+ `_status_context()` private helper + schema prose updates + 12 new tests)
- **PR #3334** `7a7bea22f` — S2858 PR#2: list_caps N+1 fix via batched name lookup (+ 6 new tests including query-count assertion)
- **PR `<this docs cascade>`** — S2858 handoff + 00-START-NEXT-SESSION refresh + docs cascade

**Memory (Claude-authored) — 2 new entries at S2858:**
- `feedback_claude_stdout_truncation_vs_ui_truncation` — Claude stdout truncation ≠ UI truncation; full response usually visible to Chris in Chat UI. Re-request only for Claude's execution context. Extends `feedback_read_full_rigby_response_not_just_tail`.
- `feedback_per_pr_summary_signals_close_readiness` — after every merged PR in a multi-PR slate, surface a summary WITH an explicit "still open before close" checklist. Chris uses these mid-flight summaries as decision points. Extends `feedback_session_close_three_part_summary`.

**Workspace canonical:** Content mirror + ratification envelope written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables` at S2858 close-cascade.

**Runtime impact:**
- **PR #3333:** `clear_freeze` + `clear_downgrade` responses now embed a `status_context` block with 9 fields (`daily_total`, `effective_cap`, `cap_source`, `spend_pct_of_cap`, `re_flag_likely`, `re_flag_reason`, `refire_threshold`, `refire_threshold_pct_of_cap`, `enforcement_note`) so operators don't have to re-call `get_status` to know if the flag will re-fire. `re_flag_likely` mirrors enforcer semantics (explicit-cap-only). Note strings flag "state flip only" so `cleared=true` isn't misread as remediation.
- **PR #3334:** `workspace_budget_tool.list_caps include_defaults=false` scales O(1) on ProjectWorkspace name queries regardless of row count (was N+1). Two-pass batching: pass 1 collects `(row, uuid)` tuples + valid uuids; single `filter(id__in=uuids).values_list('id','name')`; pass 2 uses dict lookup. Wire shape preserved (workspace_id stays string, missing rows still yield None-name).

**Not shipped at S2858 close (deferred to S2859 or later):**
- Q5 concern 5 (list_caps include_defaults=true remaining per-row perf costs beyond N+1 fixed here)
- `simulate_enforcement` auto-clear-after-N-seconds (first-trigger fold)
- `EnforcementContext` dataclass consolidation (first-trigger fold)
- `selected_fields` for `autopilot_tool.history include_evidence` (first-trigger fold)
- Phase 2B pricing (4 items)

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2858)

See:
- **S2858 handoff (current):** `docs/handoffs/SESSION_2858_CLEAR_STATUS_CONTEXT_AND_LIST_CAPS_N1_SHIPPED.md`
- **S2857 handoff:** `docs/handoffs/SESSION_2857_SIMULATE_ENFORCEMENT_SHIPPED.md`
- **S2856 handoff:** `docs/handoffs/SESSION_2856_AUTOPILOT_HISTORY_EVIDENCE_AND_ENFORCEMENT_SPLIT_SHIPPED.md`
- **S2855 handoff:** `docs/handoffs/SESSION_2855_PRICING_CANON_PHASE_2A_SHIPPED.md`
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
