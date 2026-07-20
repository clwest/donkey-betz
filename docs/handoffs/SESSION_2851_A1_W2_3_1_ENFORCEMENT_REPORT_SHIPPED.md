# Session 2851 — A1 W2 #3.1 `enforcement_report` shipped

**Date:** 2026-07-20
**Merge:** PR #3318 `c9396276e` — main
**Session pin:** `pa-abbd3c22650348b3` (retired at S2850 close) → `pa-00c6b29d0db74e90` (minted at S2851 open)
**Label:** `s2851-a1-w2-3-1-reporting`
**Moratorium:** D6 still in force — this ships within ratified S2850 shape; no strategic-discovery expansion.

---

## What shipped

One code PR, zero migration, single tool-surface action:

### `workspace_budget_tool.enforcement_report`

Fleet auditability over time. For each in-scope workspace, returns per-workspace cap + effective_cap + cap_source + freeze/downgrade state + enforcement_events_count + last_enforcement_at over a sliding window (`24h` / `7d` / `30d`).

**Args (all optional):**
- `workspace_id: string` — omit to return all in-scope workspaces
- `window: "24h" | "7d" | "30d"` — defaults to `"24h"`
- `include_spend: boolean` — defaults to `false`; when `true`, per-row `attributed_spend_usd` + `calls` from LLMCallLog joined by workspace FK
- `include_null_bucket: boolean` — defaults to `true`; when `true`, top-level `null_bucket` reports spend + calls for `workspace=NULL` LLMCallLog rows (the substrate per-workspace caps don't govern)

**Return shape** (matches ratified spec from S2850 SIGN #3/#4):

```json
{
  "action": "enforcement_report",
  "window": "24h|7d|30d",
  "window_hours": 24,
  "cutoff": "iso8601",
  "scope_note": "…",
  "note": "…best-effort JSON attribution + reframe to fleet auditability…",
  "row_count": <n>,
  "rows": [
    {
      "workspace_id": "uuid",
      "workspace_name": "string",
      "cap_usd": <n> | null,
      "effective_cap_usd": <n> | null,
      "cap_source": "explicit|default|unset",
      "is_frozen": bool,
      "is_downgraded": bool,
      "enforcement_events_count": <n>,
      "last_enforcement_at": "iso8601|null",
      "attributed_spend_usd": <n> | null,
      "calls": <n> | null
    }
  ],
  "spend_note": "…(only when include_spend=true)…",
  "null_bucket": { "spend_usd": <n>, "calls": <n> }
}
```

**Data sources (no new tables, no migration):**
- Enforcement events: `AutopilotAction` filtered on `action_type in {workspace_budget_freeze, workspace_freeze_cleared, workspace_downgrade_set, workspace_downgrade_cleared}` + `created_at >= cutoff`; workspace_id extracted from `evidence` JSON.
- Cap state: `SystemConfiguration['workspace_daily_cap:<uuid>']` + `SystemConfiguration['workspace_default_daily_cap']` via `BudgetController.get_effective_workspace_daily_cap`.
- Freeze/downgrade flags: `SystemConfiguration['workspace_freeze_active:<uuid>']` + `SystemConfiguration['workspace_downgrade_active:<uuid>']` via `BudgetController.is_workspace_{frozen,downgraded}`.
- Attributed spend: `LLMCallLog.filter(workspace_id__in=…, created_at__gte=…)` aggregated by `workspace_id`, using the `(workspace, -created_at)` index.
- Null bucket: `LLMCallLog.filter(workspace__isnull=True, created_at__gte=…)` aggregated.

**Auth model:** Read-only. Staff sees all workspaces; non-staff auto-scoped to workspaces they own (`workspace.user_id == request.user.id`); unauthenticated returns `null_bucket` + note only (row_count=0), so the tool still surfaces something rather than 403-ing.

---

## S2851 pre-code SIGN outcomes (5 questions, all tool-grounded)

| # | Ask | Rigby verdict | Applied? |
|---|-----|---------------|----------|
| Q1 | Query strategy: single-query SQL group-by vs Python aggregation vs N+1 | **REVISE → (a′)** single narrow query + Python aggregation | Yes — avoids JSONB group-by execution plans on `evidence->>'workspace_id'` (no functional index exists) |
| Q2 | Include downgrade-savings section in v1? | **DISAGREE — defer to #3.2** | Yes — keeps ratified shape clean; foot-gun avoided (no canonical price table wired) |
| Q3 | Auth model — (a) none / (b) staff-only / (c) auto-scope | **REVISE → (c)** with unauth returning null_bucket only | Yes — list_caps' current unauthenticated cross-workspace read is a latent overexposure; do not replicate here; separate follow-up to tighten list_caps |
| Q4a | Is a report the right vehicle for "trust at point of action"? | **REVISE — reframe as fleet-auditability-over-time** | Yes — reflected in schema description + response `note`; point-of-action trust stays with `set_cap.enforcement_fired` (S2850 #3.0a) |
| Q4b | Split `enforcement_events_count` into (auto_events, operator_events) using `evidence.trigger`? | **DEFER — needs evidence-completeness validation first** | Yes — deferred to #3.2 or later; would risk misleading counts if `trigger` isn't written on every enforcement write path |

**No-rubber-stamp confirmation from Rigby:** She independently verified `_handle_workspace_budget:3841`, the current `list_caps` open-read pattern at `:3945-3999`, `AutopilotAction.Meta.indexes:580-583`, `LLMCallLog.workspace` FK + `(workspace,-created_at)` index at `:391`, and `AutopilotConfig.BUDGET_DOWNGRADE_MODEL='gpt-5-mini'` at `config.py:298`. Real `repo_tool` calls (~5 with file+line evidence), not rubber-stamps.

---

## Verification (all local per `feedback_local_truth_no_production`)

**ORM ground truth (S2850 test-generated enforcement rows):**
- 17 enforcement rows in last 24h across 1 workspace (Donkey Betz, `b4503364-2573-4401-9e28-61a739e0ce50`)
- Types present: `workspace_budget_freeze`, `workspace_downgrade_cleared`, `workspace_downgrade_set`, `workspace_freeze_cleared`

**Direct handler E2E (via `ToolDispatcher._handle_workspace_budget` in Django shell):**
- **Staff, window=24h, include_spend=true:** row_count=16, Donkey Betz top row = 17 events + $3.51 attributed_spend + 168 calls ✓
- **Unauthenticated:** row_count=0, `null_bucket = {spend_usd: 8.66, calls: 1454}` ✓
- **Non-staff (`s2798_onboarding_test`):** row_count=1 (only owned workspace) ✓
- **Invalid window (`99h`):** clean error `invalid window '99h' — must be one of "24h", "7d", "30d"` ✓
- **Single workspace_id filter (staff):** row_count=1, 17 events, `last_enforcement_at` timestamp matches ORM `Max(created_at)` ✓
- **7d window:** shape identical to 24h, events unchanged (17 — all test events are within 24h anyway) ✓

**PA-surface E2E (via Rigby, post-`make celery-recycle`):**
- Rigby invoked `workspace_budget_tool.enforcement_report` twice: 41ms (24h + include_spend) + 57ms (7d + include_spend)
- Donkey Betz row confirms `enforcement_events_count: 17` matches ORM ground truth ✓
- Full response shape matches ratified spec: `window`, `note`, `null_bucket`, `rows[]` ✓
- `note` includes both the best-effort JSON attribution caveat + the fleet-auditability reframe ✓
- Real `tool_runs` non-empty (per `feedback_verify_rigby_tool_runs_before_trusting_sign`) — Rigby actually exercised the surface, not simulated

---

## Runtime impact

- New PA tool action available under `workspace_budget_tool.enforcement_report`. Existing 9 actions unchanged.
- Zero migration; zero index change. Queries use existing `AutopilotAction (action_type, -created_at)` + `LLMCallLog (workspace, -created_at)` indexes.
- No enforcement behavior change. No `LLMCallLog` semantic shift. No new evidence/result fields.
- After recycle-after-merge, workers serve the new schema + handler from `main` at `c9396276e`.

---

## What's NOT in this PR (deferred per SIGN)

- **#3.2 downgrade-savings section** — per-workspace `downgrade_calls_count` + estimated cost savings vs `gpt-5.2` pricing. Blocked on: canonical price-table wired into a single source-of-truth (right now inline pricing lives in a couple places).
- **Auto-vs-operator event split** — separate `auto_events` + `operator_events` in row shape, using `evidence.trigger` from S2850 #3.0a. Blocked on: evidence-completeness validation — need to confirm `trigger` is written on every enforcement write path before publishing split counts.
- **Tighten `list_caps` cross-workspace read** — currently `list_caps(include_defaults=true)` iterates `ProjectWorkspace.objects.all()` with no auth gate. Rigby flagged as latent overexposure at S2851 Q3. Separate follow-up PR.

---

## Rigby Tool Gap Ledger updates

None new this session. `enforcement_report` closes the S2850 slate item without new gaps.

---

## Working loop at S2851

- 1 pre-code SIGN cycle (Q1..Q4), tool-grounded (5 `repo_tool` calls with file+line evidence)
- Rigby REVISE on Q1 caught a real perf risk (JSONB GROUP BY on unindexed extract)
- Rigby DISAGREE on Q2 caught a scope-change (savings section wasn't in the ratified shape)
- Rigby REVISE on Q3 caught latent overexposure in current `list_caps`
- Rigby REVISE on Q4a reframed the report's role (fleet auditability, not point-of-action trust)
- Rigby DEFER on Q4b caught coupling risk (evidence.trigger not yet verified everywhere)
- 1 PA-surface E2E with real `tool_runs` (2 tool invocations) confirming shape + counts match ORM
- Zero rubber-stamps
- No Chris ratification needed — ratified shape from S2850 unchanged; only internal strategy + auth model REVISEd

---

## Anchors touched

- `core/services/pa_tool_schemas.py` — `workspace_budget_tool` schema: enum + 3 new params (`window`, `include_spend`, `include_null_bucket`) + description block
- `core/services/td_handlers_ops.py` — new `enforcement_report` branch in `_handle_workspace_budget` (lines ~4231-4400)
- `tools/pa_local.sh` — session pin rotation (managed by `session_lifecycle close`)

## For fuller A1 W2 arc context (spans S2846 → S2851)

- **S2851 handoff (this):** `docs/handoffs/SESSION_2851_A1_W2_3_1_ENFORCEMENT_REPORT_SHIPPED.md`
- **S2850 handoff:** `docs/handoffs/SESSION_2850_A1_W2_ENFORCEMENT_CORRECTNESS_LEG.md`
- **S2849 handoff:** `docs/handoffs/SESSION_2849_A1_W2_DEFAULTS_BACKFILL_SHIPPED.md`
- **S2848 handoff:** `docs/handoffs/SESSION_2848_A1_W1_5_DOWNGRADE_TIER_SHIPPED.md`
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
