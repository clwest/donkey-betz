# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2853 CLOSE → W2 #3.2 DOWNGRADE-SAVINGS SHIPPED (2026-07-20; picks up as S2854) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-20 (S2853 close).** One code PR shipped:
- **PR #3322** `fcffd2dd9` — `workspace_budget_tool.enforcement_report` gains opt-in `include_downgrade_savings` flag. Per-workspace + top-level fleet totals for downgrade-model usage + estimated savings vs pre-downgrade `gpt-5.2` rates. Answers "did S2850 policy-triggered downgrade save us money?". Ships a scoped `core/services/ops_autopilot/pricing.py` module that surfaces (and explicitly does NOT resolve) a pre-existing 3-way price-site divergence in the repo — whole-repo pricing canonicalization refactor deferred as separate arc.

**Working loop validated at S2853:**
- 1 Rigby pre-code design ping (task `ce7f8eb5…`) — 4Q, conditional-YES with 5 refinements, all adopted verbatim
- 1 Rigby SIGN cycle on the diff (task `cd585bdb…`) — tool-grounded via 7+ `repo_tool` calls; **caught a BLOCKING KeyError bug** (dict build/read key mismatch — would have exploded on first PA call); fixed → AGREE-TO-SHIP
- 1 pre-merge E2E direct handler invocation
- 1 post-merge PA E2E via Rigby (task `489e9fe8…`) — workers on `fcffd2dd9` serving new code; all 4 new fields present per-workspace + top-level totals populated
- Zero rubber-stamps; `tool_runs` verified non-empty on all 3 dispatches
- No Chris ratification needed (additive, opt-in, backward-compat)

**Session pin `pa-99ad8aeca6e7477e` RETIRES at S2853 close.** Fresh mint required at S2854 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2854 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-99ad8aeca6e7477e` retired at S2853 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2854-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2854

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **Whole-repo pricing-canonicalization refactor** (NEW at S2853) — S2853 surfaced 3 divergent gpt-5-mini price sites (`llm_enforcer.py:697-701` $0.50/$1.50 per 1M; `base_agent.py:2592` $3.00/$12.00 per 1M — 6× higher; a 4th unknown estimator wrote the single real `LLMCallLog.cost=$0.000399` observed row). Reconciling to a single MODEL_PRICES source of truth unlocks: (a) accurate whole-fleet cost claims; (b) makes S2853's `ops_autopilot/pricing.py` re-pointable to canonical instead of scoped-adapter; (c) removes the "diagnostic estimate only" caveat from `downgrade_savings_note`. ~4-6 hrs (audit all price sites → design canonical shape → migrate call sites → backfill test coverage). Would benefit from Rigby SIGN on canonical module shape BEFORE code.

2. **Auto-vs-operator event split for `enforcement_report`** (S2851 Q4b deferred) — add `auto_events` + `operator_events` counts per row using `evidence.trigger` from S2850 #3.0a. **Blocked on** validating evidence-completeness — confirm `trigger` is written on every `enforce_workspace_freeze` / `enforce_workspace_downgrade` / auto-clear path before publishing split counts. ~1 hr audit + ~1 hr code.

3. **PA-surface path to E2E-test llm_enforcer hot-path swap** (S2850 Ledger #2 — carried forward) — Rigby's calling agent is always `PersonalAssistant`, which bypasses workspace freeze/downgrade. To exercise the enforcer as a non-PA agent (for customer demos or operator verification), Claude currently drops to Django shell. Small addition (~2 hrs) — new PA tool action like `budget_tool.simulate_enforcement`.

4. **`autopilot_tool.history` expose evidence + result JSON** (S2850 Ledger #1 — carried forward) — currently returns row summary fields only. Operators can't see the `evidence.trigger` / `evidence.actor_user_id` / `result.reason` fields. Small addition (~1 hr): add `include_evidence=false` optional param.

5. **`clear_freeze`/`clear_downgrade` post-clear spend context** (carried forward from S2852 slate) — currently `clear_freeze` just deletes the flag; operator would have to re-call `get_status` afterwards. Inline the spend + re-flag likelihood in the response. ~30 min.

6. **N+1 in `list_caps` include_defaults=False path** (S2852 Rigby Q4 finding) — `ProjectWorkspace.objects.get(id=wid)` inside loop at `td_handlers_ops.py:4013`. Batch with `filter(id__in=[…]).in_bulk(field_name='id')` prefetch. ~30 min. Pre-existing.

7. **`was_downgraded` flag on `LLMCallLog`** (NEW deferred at S2853) — migration required. Would let S2853's `downgrade_savings` distinguish enforcer-forced from natively-mini calls (removes OVER-estimate caveat). Design: nullable `was_downgraded` bool + `pre_downgrade_model_id` char field on `LLMCallLog`; enforcer sets both on the downgrade code path. ~1-2 hrs code + 1 migration.

8. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. After S2850+S2851+S2852+S2853, the substrate story is now: per-workspace enforcement fires immediately + audit trail correct + tracking accurate + fleet auditability visible + read surfaces auth-scoped + **downgrade savings estimate visible per-workspace + fleet-total** (NEW). A4 outreach can accurately claim substrate-completeness with a real dollar-savings figure.

### What's forbidden at S2854 (D6 moratorium still in force)

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2853 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail (both cycle-triggered and operator-triggered attributed correctly); (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report` — operator can see per-workspace enforcement history over 24h/7d/30d, including which workspaces are currently frozen/downgraded, how many enforcement events fired, and when the last one fired; (g) read surfaces auth-scoped — staff sees all, non-staff auto-scoped to owned workspaces, unauth returns empty + note; **(h) downgrade savings estimate visible per-workspace + fleet-total via `include_downgrade_savings=true` (diagnostic estimate — OVER-reports true policy savings until `was_downgraded` flag lands).**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2853 close — what shipped (one code PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3322** `fcffd2dd9` — enforcement_report `include_downgrade_savings` opt-in + scoped `ops_autopilot/pricing.py`
- **PR `<this docs cascade>`** — S2853 handoff + 00-START-NEXT-SESSION refresh + docs cascade

**Memory (Claude-authored):** No new memory entries at S2853; all rules reinforced by session evidence (Rigby-first comms; verify tool_runs; zoom-out ask; docs cascade at every close; recycle after merge; Claude directs / Rigby executes / Claude verifies; Rigby writes workspace deliverables).

**Workspace canonical:** Content mirror written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables`.

**Runtime impact:**
- `enforcement_report` with `include_downgrade_savings=true`: new top-level `downgrade_model_totals` + `downgrade_savings_note` + 4 per-workspace `downgrade_model_*` fields
- Default path (flag not set) shape unchanged — full backward-compat
- Zero migration; zero enforcement-behavior change
- After recycle-after-merge (per PLAYBOOK-7.4.4), workers serve new handler at SHA `fcffd2dd9`
- 16/16 workspaces still enforce at $5/day (state unchanged from S2849 close)
- Real observed savings on Donkey Betz workspace over 30d: 1 gpt-5-mini call, actual $0.000399, estimated $0.00261275 savings vs gpt-5.2 — trivial magnitude but the surface works; expected magnitude will grow as more workspaces hit downgrade tier

**Not shipped at S2853 close (deferred to S2854 or later):**
- Whole-repo pricing-canonicalization refactor (surfaced anew by this ship)
- Auto-vs-operator event split for `enforcement_report` (Q4b — needs evidence.trigger completeness validation)
- PA-surface E2E path for llm_enforcer hot-path (S2850 Ledger #2)
- `autopilot_tool.history` evidence surface (S2850 Ledger #1)
- N+1 in `list_caps` include_defaults=False path (S2852 Rigby Q4 finding)
- `was_downgraded` flag on `LLMCallLog` (migration required — would remove OVER-estimate caveat from S2853's savings note)

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2853)

See:
- **S2853 handoff (current):** `docs/handoffs/SESSION_2853_W2_3_2_DOWNGRADE_SAVINGS_SHIPPED.md`
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
