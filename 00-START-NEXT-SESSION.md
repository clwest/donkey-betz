# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2851 CLOSE → A1 W2 #3.1 ENFORCEMENT_REPORT SHIPPED (2026-07-20; picks up as S2852) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-20 (S2851 close).** One code PR shipped:
- **PR #3318** `c9396276e` — A1 W2 #3.1: `workspace_budget_tool.enforcement_report`. New PA tool action, zero migration. Per each in-scope workspace, returns cap + effective_cap + cap_source + freeze/downgrade state + enforcement_events_count + last_enforcement_at over a sliding window (24h/7d/30d). Optional `include_spend` adds attributed_spend_usd + calls. Optional `include_null_bucket` (default true) surfaces the null-workspace substrate that per-workspace caps don't govern. Ratified shape from S2850 SIGN #3/#4. Auth: staff sees all, non-staff auto-scoped to owned workspaces, unauthenticated returns null_bucket only. Framed as **fleet auditability over time** — point-of-action trust stays with `set_cap.enforcement_fired` (S2850 #3.0a).

**A1 W2 enforcement-observability leg CLOSED** (following on from S2850's enforcement-correctness leg).

**Working loop validated at S2851:**
- 1 Rigby SIGN cycle (Q1..Q4), tool-grounded (~5 `repo_tool` calls with file+line evidence)
- 5 Rigby verdicts, all substantive: Q1 REVISE (Python-side aggregation, not JSONB GROUP BY) / Q2 DISAGREE-defer (savings section to #3.2, keeps ratified shape clean) / Q3 REVISE (auto-scope non-staff / staff sees all / unauth returns null_bucket only; also flagged latent overexposure in current list_caps) / Q4a REVISE (reframe to fleet auditability, not point-of-action trust) / Q4b DEFER (auto-vs-operator event split needs evidence.trigger completeness validation first)
- 1 PA-surface E2E with 2 real `workspace_budget_tool` runs (41ms + 57ms) — Donkey Betz row confirmed 17 events matching ORM ground truth
- Zero rubber-stamps
- No Chris ratification needed — ratified shape from S2850 unchanged; only internal strategy + auth model REVISEd

**Session pin `pa-00c6b29d0db74e90` RETIRES at S2851 close.** Fresh mint required at S2852 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2852 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-00c6b29d0db74e90` retired at S2851 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2852-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2852

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **W2 #3.2 downgrade-savings section** — extension of S2851 #3.1 report. Add per-workspace `downgrade_calls_count` (`LLMCallLog.filter(workspace_id=…, model_id=BUDGET_DOWNGRADE_MODEL, created_at__gte=cutoff).count()`) + estimated cost savings vs `gpt-5.2` pricing. **Blocked on** having a canonical price-table in code (single source-of-truth); consider wiring `LLMPricing` or equivalent module first, then this becomes a ~1-hour add. Would immediately answer "did S2850 #3.0c save us money?" — the visible payoff of the correctness leg.

2. **Tighten `list_caps(include_defaults=true)` cross-workspace read** (S2851 Rigby Q3 finding) — currently iterates `ProjectWorkspace.objects.all()` at `td_handlers_ops.py:3950` with no auth gate; any tool caller can see all workspace names + spend. Apply the same auth model as #3.1 (auto-scope non-staff, staff sees all). ~30 min. Note: `include_defaults=false` path uses `controller.list_workspace_caps()` (only workspaces with explicit caps) — still un-gated, same fix.

3. **Auto-vs-operator event split for `enforcement_report`** (S2851 Q4b deferred) — add `auto_events` + `operator_events` counts per row using `evidence.trigger` from S2850 #3.0a. **Blocked on** validating evidence-completeness — confirm `trigger` is written on every `enforce_workspace_freeze` / `enforce_workspace_downgrade` / auto-clear path before publishing split counts. ~1 hr audit + ~1 hr code.

4. **PA-surface path to E2E-test llm_enforcer hot-path swap** (S2850 Ledger #2 — carried forward) — Rigby's calling agent is always `PersonalAssistant`, which bypasses workspace freeze/downgrade. To exercise the enforcer as a non-PA agent (for customer demos or operator verification), Claude currently drops to Django shell. Small addition (~2 hrs) — new PA tool action like `budget_tool.simulate_enforcement`.

5. **`autopilot_tool.history` expose evidence + result JSON** (S2850 Ledger #1 — carried forward) — currently returns row summary fields only. Operators can't see the `evidence.trigger` / `evidence.actor_user_id` / `result.reason` fields. Small addition (~1 hr): add `include_evidence=false` optional param.

6. **`clear_freeze`/`clear_downgrade` post-clear spend context** (carried forward from S2851 slate) — currently `clear_freeze` just deletes the flag; operator would have to re-call `get_status` afterwards. Inline the spend + re-flag likelihood in the response. ~30 min.

7. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. After S2850+S2851, the substrate story is now: per-workspace enforcement fires immediately + audit trail is correct + tracking is accurate + fleet auditability is visible via `enforcement_report`. A4 outreach can accurately claim substrate-completeness.

### What's forbidden at S2852 (D6 moratorium still in force)

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2851 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail (both cycle-triggered and operator-triggered attributed correctly); (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; **(f) fleet auditability via `workspace_budget_tool.enforcement_report` — operator can see per-workspace enforcement history over 24h/7d/30d, including which workspaces are currently frozen/downgraded, how many enforcement events fired, and when the last one fired.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2851 close — what shipped (one code PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3318** `c9396276e` — A1 W2 #3.1 `workspace_budget_tool.enforcement_report`
- **PR `<this docs cascade>`** — S2851 handoff + 00-START-NEXT-SESSION refresh + docs cascade

**Memory (Claude-authored):** No new memory entries at S2851; existing rules all reinforced by session evidence.

**Workspace canonical:** Content mirror + ratification envelope written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables`.

**Runtime impact:**
- New PA tool action `workspace_budget_tool.enforcement_report` available; existing 9 actions unchanged
- Zero migration; zero index change; zero enforcement-behavior change
- After recycle-after-merge (per PLAYBOOK-7.4.4), workers serve the new schema + handler
- 16/16 workspaces still enforce at $5/day (state unchanged from S2849 close)

**Not shipped at S2851 close (deferred to S2852 or later):**
- W2 #3.2 downgrade-savings section (blocked on canonical price-table wire)
- Tighten `list_caps` cross-workspace read (S2851 Rigby Q3 latent overexposure finding)
- Auto-vs-operator event split for `enforcement_report` (Q4b — needs evidence.trigger completeness validation)
- PA-surface E2E path for llm_enforcer hot-path (S2850 Ledger #2)
- `autopilot_tool.history` evidence surface (S2850 Ledger #1)

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2851)

See:
- **S2851 handoff (current):** `docs/handoffs/SESSION_2851_A1_W2_3_1_ENFORCEMENT_REPORT_SHIPPED.md`
- **S2850 handoff:** `docs/handoffs/SESSION_2850_A1_W2_ENFORCEMENT_CORRECTNESS_LEG.md`
- **S2849 handoff:** `docs/handoffs/SESSION_2849_A1_W2_DEFAULTS_BACKFILL_SHIPPED.md`
- **S2848 handoff:** `docs/handoffs/SESSION_2848_A1_W1_5_DOWNGRADE_TIER_SHIPPED.md`
- **S2847 handoff:** `docs/handoffs/SESSION_2847_A1_W1_PHASE3_SHIPPED.md`
- **S2846 handoff:** `docs/handoffs/SESSION_2846_A1_W1_PHASE1_PHASE2_SHIPPED.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`

For older session history (S1-S2845), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
