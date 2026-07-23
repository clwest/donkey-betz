# `paid_interest_status` — Validation Report (S2913)

**Tool:** `paid_interest_status`
**Schema:** `core/services/pa_tool_schemas.py:916`
**Handler:** `core/services/td_handlers_core.py:188` (`_handle_paid_interest_status`)
**Register site:** `core/services/tool_dispatcher.py` (via `CoreHandlersMixin`)
**Session:** S2913 (Path B systematic sweep — Slice 3 batch 1 of `td_handlers_core`, opens the core-slice sweep)
**HEAD at validation:** `cff587f50` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated (full)` — actionless READ_ONLY tool; the S2905/S2912 actionless-classifier at `pa_tools_gap_map.py:439-442` auto-derives full when a `## Covered actions` heading is present.
**Rigby SIGN:** S2913 T0 SIGN AGREE-with-edits (batch 1 composition + actionless-only opener shape ratified via Q1 (c)→(b) grep-first-then-actionless; per-Q4 zoom-out concerns tracked as forward-carry). S2913 T1 SIGN AGREE-with-edits (V1 side-effect-free scan clean + V2 explicit-action-pinning applied to 3 sibling tools + V3 Concern C 1st-instance forward-carry note + V4 default-drift-risk mitigated by explicit pinning).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Return the Decision 13 demand-gate trigger state for a fleet app's paid-interest signal (default target: `signal-studio`). Answers "is signal-studio ready for paid launch / legal review yet?" and "how many paid-interest signups do we have in the last 90 days?"

Distinct from `fleet_health` (which probes each app's `/api/health` over HTTP) and `db_health_tool` (which introspects DB migration + row-count state). `paid_interest_status` is a pure config + ORM read against `APP_TRIGGER_CONFIG` and `PaidInterest` rows via `core.services.fleet_paid_interest.evaluate_trigger_state`. No HTTP, no Celery, no writes.

## Covered actions

**Actionless schema** — no `action` enum. Only invocation shape is bare-payload (or optional `app_slug` + `manual_override` overrides).

- `<bare>` — **in scope this ship** — actionless shape validated via metadata + handler trace. Harness `actions=[]` per current v2 harness posture on actionless tools (see §6.2). Response envelope: `{app_slug, trigger_state, last_signal_at, total_signals, last_90d_signals, count_threshold, high_value_threshold_usd, has_high_value_signal}`.

## 3. Schema notes

- **No required params.** `action` field absent from schema — pure actionless.
- **Optional:** `app_slug` (str; default `'signal-studio'`) — must match a registered key in `APP_TRIGGER_CONFIG` at `core.services.fleet_paid_interest`.
- **Optional:** `manual_override` (bool; default `False`) — when `True`, response reports `trigger_state='manually_overridden'` regardless of underlying signal counts. Used to answer hypothetical "what would the override look like" questions without committing to a real override.

## 4. Golden-path examples

**"Is signal-studio ready for paid launch?"**

```
paid_interest_status
```

Returns default-app state — `trigger_state` = `not_yet` | `ready` | `manually_overridden` — with counts + thresholds inline.

**"Check the override framing for signal-studio:"**

```
paid_interest_status  manual_override=true
```

Returns the same envelope with `trigger_state='manually_overridden'` — does not persist any override state.

**"Check a different registered fleet app:"**

```
paid_interest_status  app_slug=<slug>
```

## 5. Failure / empty-state / pagination notes

- **Unregistered `app_slug`** — the delegate `evaluate_trigger_state` at `fleet_paid_interest.py` looks up `APP_TRIGGER_CONFIG[app_slug]`; unknown slugs return a state envelope with defaults (documented at the delegate — not re-derived here to avoid drift).
- **Zero PaidInterest rows** — `last_90d_signals=0` + `has_high_value_signal=False` + `trigger_state='not_yet'`. Consistent shape; no error.
- **Bare payload** — everything defaults; response uses `signal-studio` as target. Not a fail-loud path.
- **`manual_override=True` on an unregistered app** — still returns `trigger_state='manually_overridden'` because the override is framing, not underlying-state derivation.
- Actionless schema → **no "unknown action" failure mode** (see §6.2 harness note).

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness paid_interest_status` at HEAD `cff587f50` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `<actionless>` | — | — | — | — (not enumerated by v2 harness; see §6.2) |

Artifact: `docs/audits/pa_tools/harness_output/paid_interest_status.json` — records `actions=[]`, `schema_action_count=0`, `harness_version=v2`. Matches the shape shipped for `universal_agent_tool` at S2912 (actionless schema).

### 6.2 Actionless harness posture — not-live-fire, but read-safe

Per S2912 §5a precedent for `universal_agent_tool`: the v2 auto-harness (`pa_tool_validate_harness`) enumerates dispatches by iterating the tool's `action` enum. Actionless tools yield `schema_action_count=0` and `actions=[]` — the harness records the shape but does NOT dispatch. This is the same posture that landed at S2912 for `universal_agent_tool`.

**Distinction from `universal_agent_tool`:** `paid_interest_status` is classified `READ_ONLY / always` in `TOOL_DEFAULTS`, not `MUTATION / conditional`. Live exercise is safe — no LLM cost, no fan-out to AGENT_MAP agents, no async dispatch. This ship stays contract-only for harness-posture consistency with the actionless-tool precedent; a future substrate arc (S2912 §5a `dry_run` add-flag pattern, or an actionless-tool harness extension `_run_actionless`) can close the live-fire gap.

**Post-merge verification** is contract-level (schema/handler/`TOOL_DEFAULTS` alignment) + worker recycle freshness per PLAYBOOK-7.4.4, NOT live dispatch.

---

## Related

- **Adjacent tools:**
  - `fleet_health` — probes each app's `/api/health` over HTTP (`probe_fleet` in `core.management.commands.fleet_health_rollup`); different concern from paid-interest-gate readback.
  - `db_health_tool` — DB migration / row-count / pgvector introspection; different concern from paid-interest-gate readback.
- **Substrate context:** first tool in Slice 3 batch 1. Peers this batch: `platform_awareness_tool` + `persona_tool` + `platform_config_tool` (all 3 mixed-safety scoped-to-READ_ONLY-subset via per-action records).
- **Metadata seed:** 1 `TOOL_DEFAULTS` record at `core/services/tool_action_metadata.py` this ship (actionless — no per-action entries). Follows `universal_agent_tool` (S2912) TOOL_DEFAULTS precedent for actionless schemas. Does NOT increment the S2905 metadata-pattern-selection lint counter.
- **Actionless harness posture:** matches `universal_agent_tool` (S2912). Future substrate arc could extend v2 harness with an `_run_actionless` path or adopt the S2912 §5a `dry_run` add-flag pattern; not opened as substrate arc per D6 moratorium.
- **Session 1138 (Decision 13) provenance:** the demand-gate framing, `APP_TRIGGER_CONFIG` structure, and `evaluate_trigger_state` delegate live at `core.services.fleet_paid_interest` — that module is authoritative for the trigger algorithm; this tool is a thin PA-surface adapter.
