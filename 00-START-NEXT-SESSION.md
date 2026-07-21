# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2856 CLOSE → AUTOPILOT.HISTORY EVIDENCE + ENFORCEMENT_REPORT AUTO/OPERATOR SPLIT SHIPPED (2026-07-20; picks up as S2857) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-20 (S2856 close).** Two code PRs shipped in the S2856 window:

- **PR #3328** `725b71f2f` (earlier in-window) — S2856 slate #1: `was_downgraded` + `pre_downgrade_model_id` fields on `LLMCallLog` + `enforce_real_ai` singleton stale-flag reset. Removed the OVER-estimate caveat from S2853's `downgrade_savings`.
- **PR #3329** `4b7d29927` (this session) — S2856 slate #2 + #3 bundle: `autopilot_tool.history include_evidence` opt-in param surfaces `evidence` + `result` JSONField values per row (was previously hidden — operators had to drop to Django shell to see `trigger` / `actor_user_id` / `reason`). `enforcement_report` per-workspace rows gain `auto_events_count` + `operator_events_count` using `evidence.actor_user_id` presence as the decision rule; `enforcement_events_count` preserved as sum for back-compat. Bundled schema copy-edit to `include_downgrade_savings` description (was stale since PR #3328 — still said "OVER-reports" but was_downgraded fixed that).

**Working loop validated at S2856 for PR #3329:**
- 1 Rigby pre-code design SIGN cycle (1 turn: AGREE-TO-BUILD on all Q1–Q5 with 9 tool_runs = repo_tool + workspace_budget_tool + deliverable_tool)
- 1 Rigby post-code diff SIGN cycle (1 turn: AGREE-TO-SHIP on all Q1–Q5 with 4 independent repo_tool diff verifications on the actual staged hunks; optional Q3 belt-and-suspenders comment applied inline)
- 10 new pytest cases pass (2 new classes) + 33 pre-existing S2856 + pricing_catalog tests pass (43/43 in 0.811s)
- Post-recycle Rigby E2E on `4b7d29927` confirms new keys populate: Donkey Betz workspace shows `enforcement_events_count: 17 = auto_events_count: 6 + operator_events_count: 11` (sum invariant holds)
- Chris ratified the bundle scope via joint Claude+Rigby recommendation per `feedback_claude_rigby_agree_first_chris_yes_no`

**Stale START-NEXT caveat caught early:** The S2855 close doc listed slate #1 as pending, but PR #3328 had already shipped it in a prior session on the same S2856 label (retired pin `pa-42d61f82953a4e48`). Investigation caught this before wasted work.

**Session pin `pa-cd83950450f3466c` RETIRES at S2856 close.** Fresh mint required at S2857 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2857 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-cd83950450f3466c` retired at S2856 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2857-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2857

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **`budget_tool.simulate_enforcement`** (S2850 Ledger #2 carry) — new PA tool action to exercise the enforcer hot-path as a non-PA agent. Rigby's calling agent is always `PersonalAssistant` which bypasses workspace freeze/downgrade. For customer demos or operator verification the current workaround is Django shell. ~2 hrs. **My recommendation for S2857.**

2. **`clear_freeze`/`clear_downgrade` post-clear spend context** (carried forward) — currently `clear_freeze` just deletes the flag; inline the spend + re-flag likelihood in the response so the operator doesn't have to re-call `get_status`. ~30 min.

3. **N+1 in `list_caps include_defaults=False` path** (S2852 Rigby Q4 pre-existing finding) — `ProjectWorkspace.objects.get(id=wid)` inside loop at `td_handlers_ops.py:4013`. Batch with `filter(id__in=[…]).in_bulk(field_name='id')` prefetch. ~30 min.

4. **`selected_fields` param for `autopilot_tool.history include_evidence`** (S2856 slate #3 Rigby Q5c zoom-out fold, first trigger observed — deferred until second trigger before Playbook amendment) — introduce structured field selection over the JSONField payload so consumers can request only what they need without full evidence + result blobs. Blocked until concrete need surfaces (i.e. any consumer complaining about payload size).

5. **`enforcement_action_types` shared constant** (S2856 pre-code Q5b, first trigger observed) — de-duplicate the 4-item action-type list between `td_handlers_ops.py:4362` and `ops_autopilot/budget.py` write sites. ~1 hr refactor. Not urgent until a fifth type is added.

6. **`actor_user_id` as first-class column on `AutopilotAction`** (S2856 pre-code Q5a, first trigger observed — MIGRATION required) — the `evidence.actor_user_id` contract is now a first-class read semantic that drives the enforcement_report split. Long-term this wants to be an explicit column. Deferred until schema-migration budget opens or a second trigger surfaces.

7. **Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855: `model_kind` dimension, `EMBEDDING_COSTS`+`MODEL_PRICES` unification, `pricing_catalog_version` field on LLMCallLog, LLMCallLog↔CostTracking schema-level provenance column. None currently justified without a specific reconciliation trigger.

8. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. The substrate story now includes: per-workspace enforcement immediate + accurate audit trail + accurate tracking + fleet auditability + auth-scoped reads + downgrade savings estimate + Claude Haiku billing bug fixed + policy-downgraded calls priced correctly + analytics-plane attribution correct + display fallbacks canonical + embedding pricing SoT preserved + **enforcer-forced downgrades cleanly distinguishable (was_downgraded, PR #3328) + operator vs autopilot enforcement events cleanly distinguishable in fleet report + evidence/reason surfacing on autopilot audit history (PR #3329)**.

### What's forbidden at S2857 (D6 moratorium still in force)

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2856 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail — cycle-triggered vs operator-triggered attributed correctly + **auto_events_count vs operator_events_count now visible per-workspace in the fleet report**; (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total — **now cleanly filtered to enforcer-forced downgrades only (PR #3328 `was_downgraded=True`)**; (i) all billing paths route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls priced at effective_model rates; (j) analytics-plane cost attribution correct; display fallbacks use canonical rates with explicit `estimated: true` flag; embedding pricing SoT preserved; **(k) autopilot audit history (`autopilot_tool.history include_evidence=true`) now surfaces evidence + result JSONField values inline for operators inspecting trigger / actor_user_id / reason.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2856 close — what shipped (two code PRs + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3328** `725b71f2f` — S2856 slate #1 `was_downgraded` (prior in-window session)
- **PR #3329** `4b7d29927` — S2856 slate #2 + #3 bundle: `autopilot_tool.history include_evidence` + `enforcement_report` auto/operator split + bundled `include_downgrade_savings` schema copy-edit
- **PR `<this docs cascade>`** — S2856 handoff + 00-START-NEXT-SESSION refresh + docs cascade

**Memory (Claude-authored):** No new memory entries at S2856; all rules reinforced by session evidence (verify Rigby tool_runs; zoom-out ask; docs cascade at every close; recycle after merge; Claude directs / Rigby executes / Claude verifies; Rigby writes workspace deliverables; read full Rigby response not just tail).

**Workspace canonical:** Content mirror to be written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables` at S2856 close-cascade.

**Runtime impact of PR #3329:**
- `autopilot_tool.history include_evidence=true` returns `evidence` + `result` JSONField values per row — first-class read semantic on why an action fired and who triggered it (operator vs autopilot)
- `enforcement_report` per-workspace rows carry `auto_events_count` + `operator_events_count` — fleet auditability now cleanly distinguishes autopilot cycle enforcement from operator-forced enforcement via `workspace_budget_tool`
- Response `note` field carries the split-rule explainer (`bool(evidence.actor_user_id) → operator`)
- `include_downgrade_savings` schema description updated to reflect PR #3328's semantics; no more "OVER-reports" caveat

**Not shipped at S2856 close (deferred to S2857 or later):**
- Slate #4 `budget_tool.simulate_enforcement`
- Slate #5 `clear_freeze`/`clear_downgrade` spend context
- Slate #6 N+1 in `list_caps`
- Slate #7 Phase 2B pricing (4 items)
- Rigby zoom-out folds Q5a/Q5b/Q5c (first triggers observed; each awaits second trigger before Playbook promotion)

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2856)

See:
- **S2856 handoff (current):** `docs/handoffs/SESSION_2856_AUTOPILOT_HISTORY_EVIDENCE_AND_ENFORCEMENT_SPLIT_SHIPPED.md`
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
