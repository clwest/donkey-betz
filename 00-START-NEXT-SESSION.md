# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2857 CLOSE → `workspace_budget_tool.simulate_enforcement` SHIPPED (2026-07-20; picks up as S2858) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-20 (S2857 close).** One code PR shipped:

- **PR #3331** `52cf41287` — S2857 slate #1: new PA-tool action `workspace_budget_tool.simulate_enforcement`. Operators + customer demos can now fire the workspace freeze + downgrade enforcer against a synthetic daily-spend value without needing Django shell (Rigby's `PersonalAssistant` calling agent bypasses freeze at `core/llm_enforcer.py:271` `_critical_agents`). Rigby pre-code SIGN mods adopted same-PR: `evidence.simulated=True` marker + `enforcement_report.include_simulated` opt-in filter (default false — protects `operator_events_count` from demo pollution). Rigby post-code SIGN caught missing `math.isfinite()` guard for nan/inf; fix applied inline before ship + 2 new test cases.

**Working loop validated at S2857:**
- 1 Rigby pre-code SIGN cycle (1 turn: AGREE-TO-BUILD on Q1/Q2/Q4, DISAGREE-with-mods on Q3 → adopted; 9 tool_runs across `repo_tool` grounding checks)
- 1 Rigby post-code SIGN cycle (1 turn: 6 independent `repo_tool.read_file` verifications on the actual staged hunks; DISAGREE-TO-SHIP on Q3 nan/inf; fix + 2 test cases applied inline)
- 26 new pytest cases across 5 classes + 43 pre-existing S2856 + pricing_catalog tests pass (69 total green)
- Post-recycle Rigby E2E on `52cf41287` confirmed all 3 dry-run decision tiers on `chris-personal` workspace (below cap → no_op; at 80% cap → `would_set_downgrade`; above cap → `would_freeze + would_set_downgrade`); validation error correctly returned for `-1.0`
- Chris ratified the slate at open ("go ahead with simulate_enforcement") per `feedback_claude_rigby_agree_first_chris_yes_no` — Rigby's Q3 mods (evidence.simulated + report filter + nan/inf guard) are scope-preserving refinements landed same-PR.

**Session pin `pa-cda874e3ee284874` RETIRES at S2857 close.** Fresh mint required at S2858 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2858 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-cda874e3ee284874` retired at S2857 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2858-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2858

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **`clear_freeze`/`clear_downgrade` post-clear spend context** (carried from S2857) — currently `clear_freeze` just deletes the flag; inline the spend + re-flag likelihood in the response so operator doesn't have to re-call `get_status`. ~30 min. **My recommendation for S2858 slate #1.**

2. **N+1 in `list_caps include_defaults=False` path** (S2852 Rigby Q4 pre-existing finding) — `ProjectWorkspace.objects.get(id=wid)` inside loop at `td_handlers_ops.py:4013`. Batch with `filter(id__in=[…]).in_bulk(field_name='id')` prefetch. ~30 min. Could bundle with #1.

3. **`workspace_budget_tool.simulate_enforcement` — live-path with auto-clear-after-N-seconds** (S2857 first-trigger fold if user asks). Currently `dry_run=false` writes flags that persist until operator calls `clear_freeze`/`clear_downgrade`. Consider optional `auto_clear_after_seconds` param so a demo doesn't leave a workspace frozen if the operator forgets to clean up. Deferred — awaits explicit ask.

4. **`selected_fields` param for `autopilot_tool.history include_evidence`** (S2856 slate #3 Rigby Q5c zoom-out fold, first trigger observed — deferred until second trigger before Playbook amendment) — structured field selection over the JSONField payload. Blocked until concrete need surfaces.

5. **`enforcement_action_types` shared constant** (S2856 pre-code Q5b, first trigger observed) — de-duplicate the 4-item action-type list between `td_handlers_ops.py:4362` and `ops_autopilot/budget.py` write sites. ~1 hr refactor. Not urgent until a fifth type is added.

6. **`actor_user_id` as first-class column on `AutopilotAction`** (S2856 pre-code Q5a, first trigger — MIGRATION required). Deferred until schema-migration budget opens.

7. **`EnforcementContext` dataclass consolidation** (S2857 post-code Q5, first trigger observed) — `actor_user_id` + `trigger` + `simulated` (and growing) currently piped as kwargs on both enforce_ methods. Consolidate into an `EnforcementContext` dataclass. **Deferred** — awaits second independent trigger before Playbook amendment.

8. **Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855: `model_kind` dimension, `EMBEDDING_COSTS`+`MODEL_PRICES` unification, `pricing_catalog_version` field on LLMCallLog, LLMCallLog↔CostTracking schema-level provenance column. None currently justified without a specific reconciliation trigger.

9. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. The substrate story now includes: per-workspace enforcement immediate + accurate audit trail + accurate tracking + fleet auditability + auth-scoped reads + downgrade savings estimate + Claude Haiku billing bug fixed + policy-downgraded calls priced correctly + analytics-plane attribution correct + display fallbacks canonical + embedding pricing SoT preserved + enforcer-forced downgrades cleanly distinguishable + operator vs autopilot enforcement events cleanly distinguishable + evidence/reason surfacing on autopilot audit history + **operators + demo audiences can trigger enforcer against synthetic spend without shell access (PR #3331)**.

### What's forbidden at S2858 (D6 moratorium still in force)

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2857 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`. **S2857: operator can now verify enforcement without touching real spend via `simulate_enforcement`.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail — cycle-triggered vs operator-triggered attributed correctly + auto_events_count vs operator_events_count now visible per-workspace in the fleet report; (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total — now cleanly filtered to enforcer-forced downgrades only; (i) all billing paths route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls priced at effective_model rates; (j) analytics-plane cost attribution correct; display fallbacks use canonical rates with explicit `estimated: true` flag; embedding pricing SoT preserved; (k) autopilot audit history (`autopilot_tool.history include_evidence=true`) surfaces evidence + result JSONField values inline for operators inspecting trigger / actor_user_id / reason; **(l) operators + demo audiences can trigger the freeze + downgrade enforcer against a synthetic spend value via `workspace_budget_tool.simulate_enforcement` — dry-run reveals decisions + thresholds without state writes; live path writes real flags with `evidence.simulated=True` marker (excluded from fleet report by default). Rigby's PersonalAssistant caller no longer needs Django shell to verify enforcement machinery.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2857 close — what shipped (one code PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3331** `52cf41287` — S2857 A1 W2 #4: `workspace_budget_tool.simulate_enforcement` (+ `enforcement_report.include_simulated` + additive `simulated=False` kwarg on enforce_ methods + 26 new tests + Rigby SIGN Q3 nan/inf guard)
- **PR `<this docs cascade>`** — S2857 handoff + 00-START-NEXT-SESSION refresh + docs cascade

**Memory (Claude-authored):** No new memory entries at S2857; all rules reinforced by session evidence (verify Rigby tool_runs; zoom-out ask; belt-and-suspenders same-PR pattern; docs cascade at every close; recycle after merge; Claude directs / Rigby executes / Claude verifies; Rigby writes workspace deliverables; read full Rigby response not just tail).

**Workspace canonical:** Content mirror + ratification envelope to be written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables` at S2857 close-cascade.

**Runtime impact of PR #3331:**
- `workspace_budget_tool.simulate_enforcement` returns freeze + downgrade decisions (would_freeze / would_set_downgrade / would_clear_downgrade / no_op variants) + computed thresholds; dry_run=true default is read-only; dry_run=false invokes real enforce_ methods with synthetic spend
- `enforcement_report include_simulated=false` (default) excludes `evidence.simulated=True` rows from `operator_events_count` / `auto_events_count` — demo/verification traffic no longer pollutes fleet counts
- `enforce_workspace_freeze` + `enforce_workspace_downgrade` gain `simulated=False` kwarg — kwarg default preserves prior behavior; when True, adds `evidence['simulated']=True` on both set and clear branches

**Not shipped at S2857 close (deferred to S2858 or later):**
- Slate #2 `clear_freeze`/`clear_downgrade` post-clear spend context
- Slate #3 N+1 in `list_caps`
- `simulate_enforcement` auto-clear-after-N-seconds (first-trigger fold, deferred)
- `EnforcementContext` dataclass consolidation (first-trigger fold, deferred)
- Phase 2B pricing (4 items)

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2857)

See:
- **S2857 handoff (current):** `docs/handoffs/SESSION_2857_SIMULATE_ENFORCEMENT_SHIPPED.md`
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
