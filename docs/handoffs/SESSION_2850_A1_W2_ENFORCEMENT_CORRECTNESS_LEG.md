# Session 2850 Handoff — A1 W2 enforcement-correctness leg (#3.0a + #3.0c)

**Session ID:** 2850
**Date:** 2026-07-20
**Session pin:** `pa-abbd3c22650348b3` (label `s2850-a1-w2-reporting-scoping`) — RETIRES at close
**Prior session pin:** `pa-507d1264765f4bf3` (retired at S2849 close)
**Next session:** S2851 will atomic-mint fresh pin per `feedback_session_open_atomic_mint_before_pa_dispatch`

**Merge commits in order:** `d2941c51b` → `22dc1a23f` (squashed to PRs `#3315` + `#3316`)

---

## Executive summary

**A1 W2 enforcement-correctness leg shipped as two PRs plus one caught bug.** Session opened on the recommended lean of "W2 #3 Reporting scoping" and Rigby's zoom-out on SIGN #3 reframed the slate: enforcement correctness first, observability second. Chris ratified **Reframe B** (insert #3.0a set_cap immediate enforcement + #3.0b llm_enforcer hot-path E2E ahead of #3.1 report).

**#3.0a (PR #3315)** wires immediate freeze/downgrade into `workspace_budget_tool.set_cap` so operators don't wait ~10 min for the autopilot cycle. Per Rigby SIGN #4 Q2, the auto-clear-on-hysteresis branch also attributes to the operator when caused by an operator cap-raise. ORM-verified end-to-end.

**#3.0b E2E revealed a real bug.** Rigby's zoom-out was more right than she knew: the enforcer's downgrade routing works correctly at the wire (API payload sends `'model': 'gpt-5-mini'` for downgraded workspaces), but the LLMCallLog + CostTracking persistence layer was silently recording `model_id='gpt-5.2'` and gpt-5.2 pricing on every downgraded call since S2848 W1.5. Any report on downgrade activity via LLMCallLog would have shown zero downgrades even when they were actively firing. Cost savings under-reported by ~7.5× per downgraded call.

**#3.0c (PR #3316)** fixes the tracking bug: `_call_openai` and `_call_claude` now surface `effective_model` in their return dicts; the caller reads that field into the `model` variable that gets persisted. Semantic shift documented inline (`model_id` now = actual model called, not requested). Per Rigby SIGN #5 Q3, `was_fallback` intentionally NOT set true on policy-triggered downgrades (that flag is error-fallback semantics; policy routing needs its own future field to avoid confusing SLO/alerting readers).

**Working loop stayed on shape:** Claude EIA → Rigby SIGN pressure-tests with tools → joint recommendation to Chris → Chris ratifies → Claude ships → Rigby E2E-verifies → Claude ORM-cross-checks. Zero rubber-stamps; one substantive zoom-out that reshaped the slate (Rigby SIGN #3 zoom-out); one E2E-caught bug that led to a same-session follow-up PR (#3.0c).

**Not shipped this session (deferred to S2851):** #3.1 `workspace_budget_tool.enforcement_report` — Chris explicit deferral at S2850 close because "it's going to be a bigger step, let's start fresh." Shape is already signed off (Rigby SIGN #3 (b) + SIGN #4 aggregation notes); S2851 opens with implementation-ready spec.

---

## What shipped

### PR #3315 (squash merge `d2941c51b`) — #3.0a set_cap immediate enforcement

**BudgetController** (`core/services/ops_autopilot/budget.py`):
- `enforce_workspace_freeze(spend, now, workspace_id, actor_user_id=None, trigger='autopilot_cycle')` — new optional params. When `actor_user_id` passed, the AutopilotAction row is attributed to `agent_name='workspace_budget_tool'` / `policy='workspace_budget_tool'` with `evidence.trigger` + `evidence.actor_user_id`. Threshold + idempotency logic UNCHANGED regardless of actor.
- `enforce_workspace_downgrade(spend, now, workspace_id, actor_user_id=None, trigger='autopilot_cycle')` — same treatment. BOTH branches (set-on-cross-up AND auto-clear-on-hysteresis) get the operator override when `actor_user_id` is passed. Auto-clear on cap-raise records `result.reason='operator_cap_change_hysteresis'` vs the background `'auto_hysteresis'` path (Rigby SIGN #4 Q2).

**workspace_budget_tool handler** (`core/services/td_handlers_ops.py:4002`):
- `set_cap` action after `set_workspace_daily_cap`: calls both `enforce_workspace_freeze` + `enforce_workspace_downgrade` with `actor_user_id=user_id`, `trigger='operator_set_cap_immediate'`. Reuses the existing `compute_workspace_spend` call (no extra query).
- Return payload gains `enforcement_fired: {freeze, downgrade}` — dict or null per action so operators see exactly what fired.

**Schema** (`core/services/pa_tool_schemas.py:3375`):
- `set_cap` description gains one sentence describing the immediate enforcement + the new `enforcement_fired` return field.

**Autopilot cycle caller** (`core/services/ops_autopilot/core.py:1467-1478`): UNCHANGED. It doesn't pass `actor_user_id`, so `enforce_*` defaults preserve original autopilot attribution.

### PR #3316 (squash merge `22dc1a23f`) — #3.0c llm_enforcer model tracking fix

**llm_enforcer** (`core/llm_enforcer.py`):
- `_call_openai` return dict now includes `'effective_model': effective_model` — surfacing the actual model that was used (post budget downgrade).
- `_call_claude` return dict adds `'effective_model': 'claude-3-haiku'` for symmetry (currently constant; ready if Anthropic-side routing ever varies).
- Caller at `line 347-370` reads `model = response.get('effective_model', <default>)` instead of hardcoding `'gpt-5.2'` / `'claude-3-haiku'`.

**Semantic shift documented inline:** `LLMCallLog.model_id` + `CostTracking.service` now = ACTUAL model called (post-downgrade), not the originally-requested model. If a future report needs the requested-vs-effective split, add a `requested_model_id` field via migration.

**Intentionally NOT changed:** `was_fallback=True` on downgraded rows. Per Rigby SIGN #5 Q3, downgrades are policy routing, not error fallback — overloading that flag risks confusing SLO/alerting readers. Deferred to a future `was_policy_reroute` field if needed.

---

## Working loop evidence

**Rigby SIGN cycles:** 5 total.
- **SIGN #1** (initial): W2 #3 Reporting shape ranking. 10 `repo_tool` grounding calls (1 timed out at 10s), ranked A/B/C with A recommended (`workspace_budget_tool.spend_report` action). Body truncated at ~132 chars.
- **SIGN #2** (follow-up): finish (b) shape + deliver (c) zoom-out. Rigby delivered concrete action name (`enforcement_report`), args schema, return shape, and — critically — the zoom-out that reframed the slate: "reporting is probably NOT the highest leverage next move ... higher-leverage adjacent work is *making enforcement behavior obvious and trustworthy at the point of action*, not building a report."
- **SIGN #3** (Reframe B agreement): AGREE on inserting #3.0a + #3.0b ahead of #3.1. Preserves Chris's ratified W2 order (#3 reporting still ships) but delivers enforcement leverage first.
- **SIGN #4** (pre-code diff shape for #3.0a): AGREE with two clarifications. Q1: stay with existing `action_type` (slice by `evidence.trigger`), don't fork the enum. Q2: auto-clear branch ALSO gets operator attribution when `actor_user_id` passed — "any state transition it performs (set or clear) should write an AutopilotAction with that same attribution + trigger, regardless of branch." This clarification prevented a subtle audit-trail hole.
- **SIGN #5** (Reframe C on #3.0b finding): AGREE on inserting #3.0c. Three pushbacks: (Q3.1) semantic shift on `model_id` — acceptable if documented, consider `requested_model_id` split later; (Q3.2) apply fix uniformly across providers so cost computation always uses effective model; (Q3.3) do NOT set `was_fallback=True` — that's error-fallback semantics, not policy semantics. Chris ratified.

**Ratifications:** Two — Chris ratified Reframe B (slate insert #3.0a+#3.0b) after SIGN #3, ratified Reframe C (insert #3.0c) after SIGN #5.

**E2E verifications:**
- **#3.0a E2E** (Rigby via PA tools on Donkey Betz workspace, daily spend $2.61):
  - `set_cap $0.01` → `enforcement_fired.freeze` populated (workspace_budget_freeze), `enforcement_fired.downgrade` populated (workspace_downgrade_set), `is_frozen=true`
  - Rows 88 + 89 written with `agent=workspace_budget_tool`, `policy=workspace_budget_tool`, `evidence.trigger='operator_set_cap_immediate'`, `evidence.actor_user_id=Chris` — ORM-verified
  - `set_cap $5.0` (restore) → `enforcement_fired.downgrade=workspace_downgrade_cleared`; row 91 written with `result.reason='operator_cap_change_hysteresis'`, operator attribution preserved — SIGN #4 Q2 satisfied
- **#3.0b E2E** (Claude via Django shell — PA path can't fire non-PA agent calls, tool gap flagged; see Rigby Tool Gap Ledger):
  - State: forced Donkey Betz into downgrade via cap $3.50 (spend $3.07 = 87% of cap)
  - Fired `enforcer.enforce_real_ai(agent_name='TestBudgetVerification', task_type='e2e_check', user=chris)`
  - Enforcer log confirmed correct routing: `[BudgetController] Downgrading e2e_check from gpt-5.2 → gpt-5-mini`
  - API payload sent to OpenAI confirmed: `'model': 'gpt-5-mini'`
  - **BUG DETECTED:** `LLMCallLog.model_id='gpt-5.2'`, cost=$0.003012 (gpt-5.2 pricing) — WRONG on both counts
- **#3.0c E2E** (post-fix re-run):
  - Same call: `LLMCallLog.model_id='gpt-5-mini'`, cost=$0.000399 — 7.5× lower, matches actual gpt-5-mini pricing
  - Enforcer log: `✅ REAL AI RESPONSE generated - openai/gpt-5-mini - 1721 tokens (1047ms)`

**Deploy shape:** 3 recycle-all invocations (before #3.0a E2E, after #3.0a merge, after #3.0c merge), per PLAYBOOK-7.4.4 constitutional rule.

---

## Rigby Tool Gap Ledger — new entries this session

1. **`autopilot_tool.history` doesn't return `evidence` or `result` JSON fields.** The summary rows show `agent_name`, `policy`, `action_type`, `timestamps` — enough to confirm attribution but not the `evidence.trigger` / `evidence.actor_user_id` / `result.reason` fields that carry the operator-triggered context. Forces ORM cross-check for any audit content. Surfaced during #3.0a STEP 3 verification.

2. **No PA-surface path to E2E-test the llm_enforcer hot-path swap.** Rigby's calling agent is `PersonalAssistant`, which is explicitly in `_critical_agents` and bypasses the workspace freeze/downgrade check. To exercise the enforcer as a non-PA agent, Claude had to drop to Django shell. This is a legitimate verification gap for A1 SaaS demos — a customer wanting to prove enforcement works can't easily do it via the operator surface.

Both flagged in this session's handoff; Rigby writes to the Ledger workspace (`b4503364-2573-4401-9e28-61a739e0ce50` `deliverable_type='engineering_backlog'`) at S2851 open or end-of-arc close per `feedback_rigby_tool_gap_ledger`.

---

## Runtime state at S2850 close

- **Workspaces under enforcement:** 16/16 at $5/day cap (unchanged from S2849 close). Donkey Betz workspace state cleaned up post-E2E: cap=$5.0, is_frozen=False, is_downgraded=False.
- **New AutopilotAction rows written this session:** ~8 (workspace_cap_set, workspace_budget_freeze, workspace_downgrade_set, workspace_freeze_cleared, workspace_downgrade_cleared × 2 — all attributed to `agent_name='workspace_budget_tool'`, evidence.actor_user_id=Chris).
- **BudgetController signature changes are additive/backwards-compatible.** Autopilot cycle caller at `core.py:1467-1478` still works without passing new params.
- **llm_enforcer semantic shift:** `LLMCallLog.model_id` now reflects effective model. Any downstream consumer that assumed it was the requested model will silently pick up the new semantics.

---

## What's queued for S2851

### Primary lean: W2 #3.1 `workspace_budget_tool.enforcement_report`

Shape signed off in SIGN #3 (b) + refined in SIGN #4:

**Action:** `workspace_budget_tool.enforcement_report`
**Args (all optional):**
- `workspace_id: string` (omit = all)
- `window: "24h" | "7d" | "30d"` (default `"24h"`)
- `include_spend: boolean` (default `false` — enforcement-forward; spend is "attributed subset")
- `include_null_bucket: boolean` (default `true`)

**Return shape:**
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
      "attributed_spend_usd": <n> | null,   // renamed from spend_usd to hedge misread
      "calls": <n> | null,
      "is_frozen": bool,
      "is_downgraded": bool,
      "enforcement_events_count": <n>,      // AutopilotAction rows in window
      "last_enforcement_at": "iso8601|null"
    }
  ]
}
```

**Now-trustworthy inputs (unlocked by #3.0c):** `LLMCallLog.model_id` can be aggregated by actual model — `#3.1` should include per-workspace `downgrade_calls_count` (calls where `model_id=BUDGET_DOWNGRADE_MODEL`) and estimated cost savings vs `gpt-5.2` pricing. Optional add-on to the row shape once #3.1 base is in.

**Estimated scope:** ~2-3 hours (1 PR). Zero migration. Reads existing indexes.

### Secondary candidates (do NOT open unless Chris redirects)

- W2 #1 UX polish (surface `enforcement_fired` + `enforcement_report` in workspace UI) — pending #3.1
- W2 #2b cap templates — pending W2 completion
- W2 #4 A4 warm-up — S2846 6-line block still in force; A1 substrate now includes enforcement correctness + accurate cost tracking
- Two S2850 Ledger entries above (`autopilot_tool.history` evidence surface + PA E2E path for enforcer hot-path)
- All S2849-carried ledger candidates still open

### Forbidden at S2851 (D6 moratorium still in force)

No new strategic-discovery arcs. No opportunity-portfolio expansions. No evaluation-framework rework. No layer-boundary design arcs.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2850)

- **S2849 handoff:** `docs/handoffs/SESSION_2849_A1_W2_DEFAULTS_BACKFILL_SHIPPED.md` — W2 #2a defaults + backfill
- **S2848 handoff:** `docs/handoffs/SESSION_2848_A1_W1_5_DOWNGRADE_TIER_SHIPPED.md`
- **S2847 handoff:** `docs/handoffs/SESSION_2847_A1_W1_PHASE3_SHIPPED.md`
- **S2846 handoff:** `docs/handoffs/SESSION_2846_A1_W1_PHASE1_PHASE2_SHIPPED.md`
- **A4↔A1 ratification:** `00-START-NEXT-SESSION.md` §A4 Constraints
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`

For older session history (S1-S2840), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
