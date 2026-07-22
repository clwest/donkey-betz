# `workspace_budget_tool` — Validation Report (S2894)

**Tool:** `workspace_budget_tool`
**Schema:** `core/services/pa_tool_schemas.py:3600`
**Handler:** `core/services/td_handlers_ops.py:4295` (`_handle_workspace_budget`)
**Register site:** `core/services/tool_dispatcher.py:542`
**Session:** S2894 (Path B systematic sweep — Slice 1 Batch 3 of `td_handlers_ops`, single-tool batch per Chris D-verdict on Rigby zoom-out SIGN — mutation-heavy tools warrant single-tool isolation)
**HEAD at validation:** `492fc2c35`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (every action in the schema `action` enum exercised live).
**Rigby SIGN:** S2894 T1 SIGN — Rigby recommended Option A (single-tool batch, canary containment, staff-write dry-run gating), Chris ratified. Substantive zoom-out returned (see §5a + Ledger #2 methodology signal).

---

## 1. Purpose / when-to-use

Per-workspace LLM spend cap management. Answers "what is workspace X's cap and current 24h spend, is it currently frozen or downgraded, why did enforcement fire, what happens when spend crosses 70%/100% of cap, roll a default cap across workspaces missing one." Complements `autopilot_tool.budget_report` (global spend) and the automatic `enforce_workspace_freeze` / `enforce_workspace_downgrade` autopilot cycle by giving operators direct read + write access to the same substrate the enforcer operates against.

Caps are stored in `SystemConfiguration` under `workspace_daily_cap:<uuid>` and enforced by `BudgetController` against the last-24h `LLMCallLog` spend for that workspace (sliding window, not calendar day). Two enforcement tiers: at 70% of cap the workspace is DOWNGRADED (routed to `BUDGET_DOWNGRADE_MODEL`, currently `gpt-5-mini`) with hysteresis auto-clear at 60%; at 100% of cap the workspace is FROZEN (non-critical LLM calls blocked). Freeze wins over downgrade.

Applies only to workspace-attributed `LLMCallLog` rows (currently the PA path). The NULL-workspace bucket (agents, spiders, embeddings, background tasks) is governed by GLOBAL budget controls, not per-workspace.

## Covered actions

- `get_default_cap` — **in scope this ship** — verified live. Returns the global default cap (currently $5.00). No auth. Read-only. Response includes explanatory note: default is a LAZY fallback for `get_status` / `list_caps` display; autopilot enforcement iterates only workspaces with EXPLICIT caps.
- `list_caps` — **in scope this ship** — verified live in both default (explicit-only) and `include_defaults=true` modes. Returns 16 workspaces with explicit caps in default mode; auto-scoped to caller's owned workspaces for non-staff (staff sees all). Response includes `default_cap`, `enforcement_tier`, `scope_note`, `window_note`, `null_bucket_note`.
- `get_status` — **in scope this ship** — verified live on Agent-Testing (canary) baseline + after mutations + on Donkey Betz (read-only diagnostic for Ledger #1). Returns `cap` (nullable), `effective_cap`, `cap_source` (`explicit`|`default`|`unset`), `default_cap`, sliding `daily_total` + `daily_calls` + `hourly_total` + `hourly_calls`, `is_frozen`, `is_downgraded`, `enforcement_tier`.
- `enforcement_report` — **in scope this ship** — verified live in max-diagnostics mode (`window=24h`, all include-flags true) fleet-wide + scoped to Donkey Betz (`window=7d`, `include_simulated=true`). Returns per-workspace rows with `enforcement_events_count`, `auto_events_count` vs `operator_events_count` split (S2856), `last_enforcement_at`, `attributed_spend_usd`, `calls`, optional downgrade savings estimate. NOTE: attribution is best-effort — `workspace_id` extracted from `AutopilotAction.evidence` JSON (no FK column).
- `set_cap` — **in scope this ship** (canary: Agent-Testing) — verified live with `daily_cap_usd=100.0` (high cap, no enforcement fired). Response includes `previous_cap`, `changed` bool, immediate `enforcement_fired` payload (S2850 — freeze + downgrade action dicts written this call, null when threshold not crossed), `warning`. Idempotency verified: second call with same value returned `changed=false`. Requires `workspace_id` + `daily_cap_usd > 0`. Owner-or-staff.
- `simulate_enforcement` — **in scope this ship** (dry_run=true only) — verified live twice: `simulated_daily_spend_usd=75.0` on $100 cap → `would_set_downgrade=true`, `freeze_decision=no_op_below_cap`; `simulated_daily_spend_usd=150.0` → `would_freeze=true` + `would_set_downgrade=true`. Dry-run mode returns thresholds + decisions + `note` explicitly stating no state written, no AutopilotAction rows created. Requires `workspace_id` + `simulated_daily_spend_usd ≥ 0`. Owner-or-staff.
- `clear_cap` — **in scope this ship** (canary: Agent-Testing) — verified live. Response includes `cleared: true` + explanatory note: freeze flag (if any) is NOT cleared by clear_cap; explicit `clear_freeze` required. Requires `workspace_id`. Owner-or-staff.
- `backfill_defaults` — **in scope this ship** (dry_run=true only) — verified live with defaults (no daily_cap_usd override). Plan response: `total_workspaces=16, planned=1, wrote=0, skipped_existing=15, skipped_excluded=0, skipped_not_included=0, errors=0` with per-workspace `would_write` details. Only Agent-Testing had `previous_cap: null` (after clear_cap earlier in this session) and appeared in the `planned` bucket. STAFF ONLY. Optional `daily_cap_usd` (override), `force` (overwrite existing caps), `include_workspace_ids`, `exclude_workspace_ids` allowlists.
- `clear_freeze` — **NOT exercised this ship** — mutation intentionally deferred. Would require first intentionally setting the freeze state (which requires either real over-cap spend or `simulate_enforcement` with `dry_run=false`) — outside canary containment scope. Schema-and-handler contract documented; behavior unverified.
- `clear_downgrade` — **NOT exercised this ship** — same rationale as `clear_freeze`.
- `set_default_cap` — **NOT exercised this ship** — global staff-only write with fleet-wide blast radius (changes the default cap surfaced via `cap_source='default'` for every unconfigured workspace). Deferred per canary containment protocol.

**Coverage summary:** 8 of 11 actions exercised live (all 4 reads + 4 of 7 mutations, including the highest-blast-radius one `backfill_defaults` in dry_run mode). 3 mutations documented but deferred to a dedicated staged-enforcement session because verifying them requires first creating the freeze/downgrade state they clear.

## 3. Schema notes

- **Required:** `action` (enum: `set_cap, get_status, clear_freeze, clear_downgrade, list_caps, clear_cap, get_default_cap, set_default_cap, backfill_defaults, enforcement_report, simulate_enforcement` — 11 values).
- **Conditional required at handler level:**
  - `workspace_id` for `set_cap, get_status, clear_freeze, clear_downgrade, clear_cap, simulate_enforcement`; optional narrowing filter for `enforcement_report`; ignored for `list_caps, get_default_cap, set_default_cap, backfill_defaults`.
  - `daily_cap_usd > 0` for `set_cap, set_default_cap`; optional override for `backfill_defaults`.
  - `simulated_daily_spend_usd ≥ 0` for `simulate_enforcement`.
- **Optional:** `window` (`24h`|`7d`|`30d` for `enforcement_report`, default `24h`), `include_spend` (default false), `include_null_bucket` (default true), `include_downgrade_savings` (default false), `include_defaults` (default false for `list_caps`), `include_simulated` (default false for `enforcement_report`), `dry_run` (default true for `backfill_defaults` + `simulate_enforcement`), `force` (default false for `backfill_defaults`), `include_workspace_ids`, `exclude_workspace_ids`.
- **Auth model:**
  - Reads (`get_status`, `list_caps`, `get_default_cap`, `enforcement_report`): auto-scoped to caller's owned workspaces for non-staff; staff sees all workspaces (S2852). Unauthenticated callers get an empty list + `scope_note` for `list_caps` / `enforcement_report`.
  - Owner-or-staff mutations (`set_cap`, `clear_cap`, `clear_freeze`, `clear_downgrade`, `simulate_enforcement`): caller must own the workspace OR be staff.
  - Staff-only mutations (`set_default_cap`, `backfill_defaults`): staff required regardless of workspace ownership.
- **Audit trail:** Every mutation writes an `AutopilotAction` row with `policy='workspace_budget_tool'`, symmetric with the automatic `enforce_workspace_freeze` + `enforce_workspace_downgrade` audit trail. `simulate_enforcement` rows written when `dry_run=false` carry `evidence.simulated=True` + `trigger='simulate_enforcement'` + `actor_user_id`, and are excluded from `enforcement_report` by default (S2857).
- **Schema description lint:** clean — extensive prose covering enforcement tiers, hysteresis, cap sources, sliding-window semantics, NULL-bucket boundary, dry_run/force gating on `backfill_defaults`, simulate_enforcement decision shape. No gap map lint flags (no `actions_not_mentioned_in_description`, `no_required`, or `no_properties`).

## 4. Golden-path examples

**Read the global default:**

```
workspace_budget_tool  action=get_default_cap
```

**List every workspace with an explicit cap (fleet audit):**

```
workspace_budget_tool  action=list_caps
workspace_budget_tool  action=list_caps  include_defaults=true   # show effective caps for everyone
```

**Check one workspace's cap + spend + enforcement state:**

```
workspace_budget_tool  action=get_status  workspace_id=<uuid>
```

**Fleet enforcement audit — who's over cap, when did enforcement last fire:**

```
workspace_budget_tool  action=enforcement_report  window=24h
workspace_budget_tool  action=enforcement_report  window=7d  include_spend=true  include_downgrade_savings=true
```

**Set / update / remove a per-workspace cap:**

```
workspace_budget_tool  action=set_cap  workspace_id=<uuid>  daily_cap_usd=50.0
workspace_budget_tool  action=clear_cap  workspace_id=<uuid>
```

**Preview enforcement decisions before real writes:**

```
workspace_budget_tool  action=simulate_enforcement  workspace_id=<uuid>  simulated_daily_spend_usd=75.0
workspace_budget_tool  action=simulate_enforcement  workspace_id=<uuid>  simulated_daily_spend_usd=150.0  dry_run=false   # WARNING: writes real flags
```

**Roll a default cap out to unconfigured workspaces (staff only):**

```
workspace_budget_tool  action=backfill_defaults                                    # dry_run=true default
workspace_budget_tool  action=backfill_defaults  dry_run=false                     # real writes
workspace_budget_tool  action=backfill_defaults  dry_run=false  daily_cap_usd=10.0 # override default for this run
workspace_budget_tool  action=backfill_defaults  dry_run=false  force=true         # overwrite existing caps
```

**Unfreeze / un-downgrade a workspace (after intentional intervention or false-positive enforcement):**

```
workspace_budget_tool  action=clear_freeze     workspace_id=<uuid>
workspace_budget_tool  action=clear_downgrade  workspace_id=<uuid>
```

## 5. Failure / empty-state / staleness / attribution notes

- **Explicit-cap requirement for autopilot enforcement:** `get_default_cap` note surfaces this: the default cap is a LAZY fallback for `get_status` / `list_caps` display ONLY. Autopilot enforcement iterates workspaces with EXPLICIT caps. Workspaces relying on `cap_source='default'` will NOT be enforced by the autopilot cycle. Call `backfill_defaults` to bring them under enforcement.
- **`set_cap` inline enforcement (S2850):** `set_cap` returns an `enforcement_fired` payload that surfaces any freeze/downgrade action written by this call's immediate re-check against the sliding 24h spend. Null when threshold not crossed. This is the "point-of-action trust surface" — `enforcement_report` is the historical view but attribution there is best-effort (evidence JSON parse).
- **Idempotency:** `set_cap` with the same value returns `changed=false` + `previous_cap` matching `cap`. `backfill_defaults` is idempotent per-workspace (skips existing caps unless `force=true`). `simulate_enforcement` `dry_run=true` is idempotent by design.
- **`clear_cap` does NOT clear freeze/downgrade** — response explicitly notes this. Freeze/downgrade flags are separately-keyed SystemConfig rows and must be cleared with `clear_freeze` / `clear_downgrade` explicitly. Removing a cap does not exempt an already-flagged workspace from active enforcement.
- **`clear_freeze` / `clear_downgrade` `status_context` block (S2858 PR#1):** when Rigby returns from either, the response embeds `{daily_total, effective_cap, cap_source, spend_pct_of_cap, re_flag_likely, re_flag_reason, refire_threshold, refire_threshold_pct_of_cap, enforcement_note}` so operators know whether the flag will immediately re-fire without a follow-up `get_status`. `re_flag_likely` is computed against the EXPLICIT cap only — when `cap_source != 'explicit'`, `re_flag_likely=False` + reason explains enforcement won't re-fire until an explicit cap is set.
- **`enforcement_report` attribution caveat:** `workspace_id` is extracted from `AutopilotAction.evidence` JSON (no FK column). If evidence lacks the field, the event is not attributed. `attributed_spend_usd` is the workspace-attributed subset only — the NULL-workspace bucket is reported separately when `include_null_bucket=true` (default).
- **Downgrade savings estimation (S2856):** `include_downgrade_savings=true` filters to `LLMCallLog.was_downgraded=True`, counting only enforcer-forced downgrades. Rows created before the S2856 deploy default to `was_downgraded=False` and are excluded, so windows straddling that boundary UNDER-report. Diagnostic estimate; `LLMCallLog.cost` remains authoritative for per-call cost.
- **PA path critical-agents bypass:** `llm_enforcer.py:271` `_critical_agents` list exempts the `PersonalAssistant` caller from freeze — Rigby's own calls will not be blocked by freeze flags even when the workspace's freeze flag is set. `simulate_enforcement` was added specifically for operators/customer demos to test enforcement without needing to make non-PA calls (see §5a for containment implication).
- **Window semantics:** sliding — `daily_total` = last 24h, not calendar day. `hourly_total` = last 1h. Response includes `window_note` to prevent misinterpretation.
- **Empty-state on unauthenticated callers:** `list_caps` / `enforcement_report` return empty rows + explanatory `scope_note` — silent success, not error.
- **Latency:** all read + write actions observed 3-77ms. No outliers.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1 — S2893 pattern extended)

**Mutating actions:** 7 of 11 — `set_cap`, `clear_cap`, `clear_freeze`, `clear_downgrade`, `set_default_cap`, `backfill_defaults`, `simulate_enforcement` (when `dry_run=false`).

**Blast-radius classification:**

| Action | Auth | Scope | Blast radius | Containment used this ship |
|---|---|---|---|---|
| `set_cap` | owner or staff | 1 workspace | Immediate re-check may fire freeze/downgrade against real 24h spend | Canary (Agent-Testing) + high cap ($100) to guarantee no enforcement fires |
| `clear_cap` | owner or staff | 1 workspace | Removes explicit cap; workspace falls back to `cap_source='default'` (unenforced) | Canary + verify post-state via `get_status` |
| `clear_freeze` | owner or staff | 1 workspace | Immediately unblocks non-critical LLM calls | NOT exercised — would require first inducing the freeze |
| `clear_downgrade` | owner or staff | 1 workspace | Immediately restores primary model routing | NOT exercised — would require first inducing the downgrade |
| `simulate_enforcement` (`dry_run=false`) | owner or staff | 1 workspace | Writes real freeze/downgrade flags AND real AutopilotAction rows | Kept `dry_run=true` throughout — verified decision shape without writes |
| `set_default_cap` | STAFF ONLY | GLOBAL | Changes effective cap for every workspace without explicit cap (via `cap_source='default'` fallback in display, plus visible in `backfill_defaults` planning) | NOT exercised — fleet-wide blast radius |
| `backfill_defaults` (`dry_run=false`) | STAFF ONLY | Multi-workspace | Writes explicit caps to N workspaces; brings them under autopilot enforcement | Kept `dry_run=true` — plan-only shape verified |

**Protocol applied this ship (extends S2893 canary+revert pattern):**

1. **Baseline read** — `get_status` on canary workspace to record pre-mutation state.
2. **Canary-only writes** — Agent-Testing workspace (`59af4248-70b9-4472-8062-810452446698`) for all mutations. Off-limits: Donkey Betz (`b4503364-2573-4401-9e28-61a739e0ce50`), all Real User Readiness / Capability Integration Campaign / RUR-C1 workspaces.
3. **Safety-margin arguments** — `set_cap` with `daily_cap_usd=100.0` chosen so 24h spend of 0.0 stays far below 70% downgrade threshold. `simulate_enforcement` `dry_run=true` mandatory. `backfill_defaults` `dry_run=true` mandatory.
4. **Revert** — `clear_cap` at end restores canary to pre-mutation state (`cap_source='default'`).
5. **Verify** — final `get_status` confirms revert. `AutopilotAction` rows written during canary writes are legitimate audit trail; no cleanup needed.
6. **Explicit deferral for staged-enforcement mutations** — `clear_freeze` / `clear_downgrade` require first inducing the state via `simulate_enforcement dry_run=false` OR real over-cap spend. Documented but deferred to a dedicated staged-enforcement session where the induce → verify → clear cycle can be tested end-to-end without leaving Agent-Testing in an enforced state on close.

**Rigby SIGN zoom-out (methodology signal):** "action-count budgeting" as batch-shape driver risks bundling unrelated tools just to hit a batch-size target — leading to shallow coverage on mutation gates. Sweep methodology should explicitly permit single-tool batches when the tool has high governance weight (7 mutations, staff-only paths, global-blast-radius actions). The dry_run/confirm/canary+revert belt-and-suspenders pattern is correct but ceremony-expensive — the methodology should standardize a canary-workspace + revert protocol so every mutation tool test looks the same and doesn't require reinventing containment each batch. **This batch corroborates the pattern** — running workspace_budget_tool alone kept containment discipline high and surfaced 2 substantive Ledger candidates in ~15 dispatches. See §Ledger candidates below + zoom-out fold row 159 in the parent ledger.

## 6. Evidence

### 6.1 Observed runs — this ship

Rigby's live dispatches at S2894 T1 (2026-07-22, HEAD `492fc2c35`, pin `pa-82627c4b92c84709`):

**`get_default_cap` (8ms):**

```json
{"action": "get_default_cap", "default_cap": 5.0,
 "note": "default is a LAZY fallback for get_status/list_caps display. Autopilot enforcement iterates only workspaces with EXPLICIT caps — call backfill_defaults to bring workspaces under enforcement"}
```

**`list_caps` (70ms, default explicit-only mode):**

```json
{"action": "list_caps", "count": 16,
 "workspaces": [
   {"workspace_id": "19807888-862e-4a1a-b15d-f6c95b97e5a1",
    "workspace_name": "Morning Brief",
    "cap": 5.0, "effective_cap": 5.0, "cap_source": "explicit",
    "daily_total": 0.0, "is_frozen": false, "is_downgraded": false},
   // ...15 more (Donkey Betz, Agent-Testing, campaign workspaces, Architecture & Research, etc.)
 ]}
```

All 16 workspaces have `cap=5.0` explicit. Response also emitted `default_cap: 5.0`, `enforcement_tier: downgrade_and_freeze`, `scope_note: "staff scope — all workspaces"`, `window_note`, `null_bucket_note`.

**`list_caps` `include_defaults=true` (77ms):** same 16 rows returned in this run (all workspaces already have explicit caps; the include_defaults union path was exercised but produced the same result set because no `cap_source='default'` or `unset'` rows existed in the fleet at this moment).

**`enforcement_report` `window=24h` max-diagnostics (34ms):** returned 16 per-workspace rows, all with `is_frozen=false, is_downgraded=false`. Substantive finding on Donkey Betz — see Ledger #1 below.

**`get_status` (10ms, Agent-Testing baseline):**

```json
{"action": "get_status", "workspace_id": "59af4248-...", "workspace_name": "Agent-Testing",
 "cap": 5.0, "effective_cap": 5.0, "cap_source": "explicit", "default_cap": 5.0,
 "daily_total": 0.0, "daily_calls": 0, "hourly_total": 0.0, "hourly_calls": 0,
 "is_frozen": false, "is_downgraded": false,
 "enforcement_tier": "downgrade_and_freeze"}
```

**`set_cap` (15ms, Agent-Testing → $100):**

```json
{"action": "set_cap", "workspace_id": "59af4248-...", "workspace_name": "Agent-Testing",
 "cap": 100.0, "previous_cap": 5.0, "changed": true,
 "daily_total": 0.0, "is_frozen": false,
 "enforcement_fired": {"freeze": null, "downgrade": null},
 "warning": null}
```

**`get_status` (9ms, Agent-Testing post-set_cap):** `cap: 100.0, cap_source: "explicit"` — verified write.

**`set_cap` idempotency check (7ms, Agent-Testing → $100 again):**

```json
{"cap": 100.0, "previous_cap": 100.0, "changed": false,
 "enforcement_fired": {"freeze": null, "downgrade": null}, "warning": null}
```

**`simulate_enforcement` dry_run (3ms, simulated_daily_spend_usd=75.0):**

```json
{"thresholds": {"cap_usd": 100.0, "downgrade_set_threshold_usd": 70.0,
                "downgrade_clear_threshold_usd": 60.0,
                "soft_limit_pct": 0.7, "clear_pct": 0.6,
                "currently_frozen": false, "currently_downgraded": false},
 "freeze_decision": "no_op_below_cap",
 "downgrade_decision": "would_set_downgrade",
 "note": "dry_run=true — no state written and no AutopilotAction rows created. ...",
 "freeze_action": null, "downgrade_action": null}
```

**`simulate_enforcement` dry_run (3ms, simulated_daily_spend_usd=150.0):**

```json
{"thresholds": {"cap_usd": 100.0, "downgrade_set_threshold_usd": 70.0, ...},
 "freeze_decision": "would_freeze",
 "downgrade_decision": "would_set_downgrade",
 "freeze_action": null, "downgrade_action": null}
```

**`clear_cap` (6ms, Agent-Testing):**

```json
{"action": "clear_cap", "workspace_id": "59af4248-...", "cleared": true,
 "note": "freeze flag (if any) is NOT cleared — call clear_freeze explicitly to unfreeze"}
```

**`get_status` final (5ms, Agent-Testing post-clear_cap):**

```json
{"cap": null, "effective_cap": 5.0, "cap_source": "default", "default_cap": 5.0,
 "daily_total": 0.0, "is_frozen": false, "is_downgraded": false}
```

Verified revert — Agent-Testing back to `cap_source='default'`.

**`backfill_defaults` dry_run (8ms):**

```json
{"action": "backfill_defaults", "dry_run": true, "default_cap": 5.0,
 "total_workspaces": 16, "planned": 1, "wrote": 0,
 "skipped_existing": 15, "skipped_excluded": 0, "skipped_not_included": 0, "errors": 0,
 "details": [
   {"workspace_id": "b4503364-...", "workspace_name": "Donkey Betz",
    "action": "skipped_existing", "previous_cap": 5.0},
   // ...14 more skipped_existing rows
   {"workspace_id": "59af4248-...", "workspace_name": "Agent-Testing",
    "action": "would_write", "previous_cap": null, "new_cap": 5.0}
 ],
 "note": "DRY RUN — no writes performed. Pass dry_run=false to apply."}
```

Only Agent-Testing appears in the `planned` bucket (because clear_cap earlier in the session left it with `cap_source='default'` and `previous_cap: null`). Confirms plan-shape correctness.

**Sharpening probes — Donkey Betz read-only diagnostics (Ledger #1):**

**`get_status` (16ms, Donkey Betz):**

```json
{"workspace_name": "Donkey Betz", "cap": 5.0, "effective_cap": 5.0, "cap_source": "explicit",
 "daily_total": 12.523748, "daily_calls": 634,
 "hourly_total": 1.413308, "hourly_calls": 83,
 "is_frozen": false, "is_downgraded": false,
 "enforcement_tier": "downgrade_and_freeze"}
```

**Finding:** DBZ is at 2.5× its explicit cap ($12.52 vs $5.00) yet neither frozen nor downgraded.

**`enforcement_report` scoped (31ms, DBZ, window=7d, include_simulated=true):**

```json
{"workspace_id": "b4503364-...", "workspace_name": "Donkey Betz",
 "cap_usd": 5.0, "cap_source": "explicit",
 "is_frozen": false, "is_downgraded": false,
 "enforcement_events_count": 17,
 "auto_events_count": 6, "operator_events_count": 11,
 "last_enforcement_at": "2026-07-20T20:35:16.427122+00:00",
 "attributed_spend_usd": 30.904011, "calls": 1522,
 "downgrade_model_calls_count": 0}
```

**Finding:** Enforcement HAS fired 17 times in the 7d window (6 auto + 11 operator), most recently 2026-07-20T20:35Z — ~2 days before this validation run. Yet current DBZ freeze + downgrade flags are both false. `downgrade_model_calls_count=0` means no gpt-5-mini enforcer-forced calls in the window either (though this could be S2856 boundary artifact for calls predating the `was_downgraded=True` flag).

**Interpretation of the DBZ anomaly:** three possible buckets, discriminator NOT run this ship (would require `autopilot_tool.history` — reserved for Slice 1.5 — or ORM query on `AutopilotAction` filtered by `evidence__workspace_id`):

- **(b) Enforcement runs but doesn't persist flags** — enforcement fires (17 events), writes AutopilotAction rows, but the actual `workspace_freeze_active:<uuid>` / `workspace_downgrade_active:<uuid>` SystemConfig row never gets written OR gets cleared immediately by downstream logic.
- **(c) Spend calculation mismatch** — `get_status.daily_total` (which computed $12.52) reads from one LLMCallLog query filter; the enforcer's decision path (which decided the 17 events without persisting flags) uses a different filter. Both agree "spend exists" but disagree on the enforceable subset.
- **(d) Hysteresis clear** — clearing at 60% cap ($3.00), yet current spend is $12.52 = 250% of cap, well above any clear threshold. Ruled OUT unless a separate clear path exists.
- **(e) PA critical-agents bypass on both fronts** — PA path is exempted from freeze at call time (documented); if the enforcer's spend-side query ALSO excludes PA calls, the "enforceable spend" would be near zero and enforcement events would resolve to `no_op_below_cap`. But then why 17 events? Suggests the events are `operator_events_count` (11 of 17) written by workspace_budget_tool calls, not by autopilot decisions.

Discriminator probe (deferred): read the most recent `AutopilotAction` row for DBZ and check `evidence.daily_total` at decision time + the row's `action_type` (`workspace_budget_freeze` vs `workspace_freeze_cleared` vs no-op). That call requires either `autopilot_tool.history` (Slice 1.5) or a direct ORM query.

### 6.2 Runtime-not-executed — this ship

- **`clear_freeze`** — schema+handler contract documented, behavior NOT exercised. Would require inducing the freeze state first (via `simulate_enforcement dry_run=false` or intentional over-cap spend).
- **`clear_downgrade`** — same rationale as `clear_freeze`.
- **`set_default_cap`** — global staff-only write, blast radius touches every workspace via `cap_source='default'` fallback. Deferred.
- **`backfill_defaults` `dry_run=false`** — mass write, staff-only. Deferred.
- **`simulate_enforcement` `dry_run=false`** — writes real freeze/downgrade flags + AutopilotAction rows. Deferred.
- **`enforcement_report` `window=30d`** — only 24h and 7d windows exercised.
- **`list_caps` with `include_defaults=true` producing rows with `cap_source='default'` or `unset'`** — could not observe this shape live because at time of this ship every workspace in the fleet already had an explicit cap.
- **Non-staff auth path** — every mutation exercised by a staff user (`chris`, `is_staff=true`, `is_superuser=true`). Owner-not-staff path (a non-staff user mutating a workspace they own) NOT exercised.
- **Unauthenticated read** — reads by unauthenticated callers (expected empty rows + scope_note) NOT exercised.

---

## Related

### Ledger candidates surfaced this ship

1. **`workspace_budget_tool.get_status` + `enforcement_report` — DBZ enforcement/attribution divergence.** Donkey Betz workspace shows `daily_total=$12.52` against explicit `cap=$5.00` (2.5× over) with `is_frozen=false, is_downgraded=false`. `enforcement_report` scoped to DBZ over 7d shows 17 enforcement events (6 auto + 11 operator) with `last_enforcement_at=2026-07-20T20:35Z` (~2 days pre-validation). Current flags don't reflect enforcement having run. Three possible buckets (b/c/e in §6.1); discriminator requires `AutopilotAction.evidence.daily_total` at decision time from the most recent DBZ row — not exercised this ship. **Priority:** substantive — this is the trust surface the tool is meant to protect, and it's out of contract. **Route:** Rigby Tool Gap Ledger deliverable `5c84e75a-…`.

2. **`messaging_tool` lacks a send surface** — Rigby noted at SIGN routing that `messaging_tool` is read-only (`list_threads` / `get` only), so she cannot proactively route a decision to Chris via async DM. In practice the "Claude→Rigby→Chris" pattern still works because Chris reads Rigby's chat response in the shared thread, but the workflow assumes a routing capability the tool doesn't provide. Surfaced as tool-surface friction during Batch 3 Chris-yes/no routing. **Priority:** methodology / substrate — not blocking today, but eventually a `messaging_tool.send` action (or an explicit "Rigby cannot DM operators, use in-thread reply pattern" note in the tool's schema description) would eliminate the confusion. **Route:** Rigby Tool Gap Ledger deliverable `5c84e75a-…`.

### Zoom-out fold row (from Rigby SIGN §4 pushback)

- **Row 159 candidate — mutation-heavy tools warrant single-tool batches + canary-revert protocol standardization.** Rigby's SIGN §4 zoom-out: "the sweep is trending toward action-count budgeting becoming the unit of work, which creates pressure to bundle unrelated tools just to hit a batch-size target. That's how we end up with shallow 'checked the box' validations." Corroborated by S2894 execution — running workspace_budget_tool alone (11 actions, 7 mutations) kept containment discipline high and surfaced 2 substantive Ledger candidates in ~15 dispatches. Batch cadence should distinguish read-heavy handlers (bundle 4 tools) from mutation-heavy tools (single-tool batches by default). Canary-workspace + revert protocol should promote from ad-hoc per-batch to a first-class sweep-methodology section. Classification: `same_pr_mitigatable` — the pattern is codified in §5a of THIS doc; further sweep-methodology promotion pending 1-2 more mutation-heavy tool corroborations.

### S2894 handoff

- `docs/handoffs/SESSION_2894_PA_TOOLS_SWEEP_SLICE_1_BATCH_3.md` (this session's handoff)

### Related tools

- `autopilot_tool` (RESERVED Slice 1.5) — automatic enforcement cycle; the counterpart substrate. `autopilot_tool.budget_report` reports GLOBAL spend, complement to this tool's per-workspace scope.
- `governor_tool` (S2893 validated_full) — agent-level circuit-breaker governance; different substrate but shares the "operator + autopilot both write to the same audit trail" pattern.
- `llm_enforcer.py` — the actual freeze/downgrade decision code path; `_critical_agents` bypass at `core/llm_enforcer.py:271` is load-bearing to interpreting the DBZ anomaly.
- `AutopilotAction` model — the audit substrate both this tool and the autopilot cycle write to.
