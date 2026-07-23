# `check_resource_budget` — Validation Report (S2906)

**Tool:** `check_resource_budget`
**Schema:** `core/services/pa_tool_schemas.py:687`
**Handler:** `core/services/td_handlers_agents.py:4796` (`_handle_check_budget`)
**Register site:** `core/services/tool_dispatcher.py:414`
**Session:** S2906 (Path B systematic sweep — Slice 2 batch 2 of `td_handlers_agents`, first actionless-shape batch post-substrate)
**HEAD at validation:** `e59320017`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (actionless — no schema `action` enum to iterate).
**Rigby SIGN:** S2906 T0 SIGN AGREE-with-edits + S2906 T1 SIGN AGREE (9 verification tool_runs, all A/B/C/D/E sections; zoom-out: "systemic drift trend candidate, not yet substrate-arc trigger") — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Pre-flight budget check against the LUNGS body-system oxygen substrate. Answers "would this operation exceed a spend or token cap?" before dispatch. Returns a `can_proceed` boolean plus a `warning` / `recommendation` payload so the caller can decide to skip, downgrade, or continue.

Distinct from `cost_telemetry_tool` (which reports actual historical spend from `LLMCallLog` — the "how much did I spend?" surface) and from `workspace_budget_tool` (per-workspace budget rows, staff-authored caps). `check_resource_budget` is the ambient "are we OK to run this?" gate against the LUNGS oxygen model.

## Covered actions

**This tool is actionless by schema design** — `schema_action_count=0` per T1a harness artifact (`docs/audits/pa_tools/harness_output/check_resource_budget.json`), no `action` enum declared in the schema at `pa_tool_schemas.py:692-703`. The dispatch surface is a single implicit "check-budget" call parameterized by `estimated_tokens` and `estimated_cost`.

Therefore `## Covered actions` is intentionally empty. S2906 batch 2 validates **(a)** actionless doc shape under T1b template v1, **(b)** `TOOL_DEFAULTS` READ_ONLY applicability when there is no action enum to iterate, and **(c)** schema-vs-handler consistency (this tool is the cleanest of the batch — no drift).

## 3. Schema notes

- **Required:** none (all params optional; zero-arg call is valid — returns budget status for a null-op).
- **Optional (declared):** `estimated_tokens` (int) and `estimated_cost` (number, USD).
- **Defaults:** both default to 0 when omitted at handler (`payload.get('estimated_tokens', 0)`, line 4806).
- **Handler-to-service pass-through:** handler delegates to `body_vitals.check_budget(estimated_tokens, estimated_cost)` at line 4810 — LUNGS body-system substrate owns the actual gate logic.

## 4. Golden-path examples

**"Can I run a 5000-token prompt against gpt-5.2?":**

```
check_resource_budget  estimated_tokens=5000  estimated_cost=0.05
```

**"Just tell me the current budget status" (zero-arg baseline):**

```
check_resource_budget
```

## 5. Failure / empty-state / pagination notes

- **No pagination** — single-shot gate check; returns one budget-status envelope.
- **No failure exception path** — handler is fail-open; `body_vitals.check_budget` returns a dict with defaults (`status='unknown'`, `oxygen_level=0`, `can_proceed=True`) if the underlying LUNGS substrate is unreachable.
- **Response shape** — `{estimated_tokens, estimated_cost, budget_status, oxygen_level, can_proceed, warning, recommendation}`. `oxygen_level` is the LUNGS-model instantaneous oxygen-capacity metric (integer 0-100 scale typical).
- **Silent behavior:** `can_proceed=True` when the LUNGS substrate returns no gate signal — permissive default. Callers relying on this tool as a hard-gate should also inspect `warning`/`recommendation` rather than trusting `can_proceed` alone.
- **No latency measurement in this ship** — T1a harness produced no artifact rows (actionless).

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

- **Mutating actions:** none. Read-only pre-flight check — `body_vitals.check_budget` computes against current LUNGS state, does not persist a gate decision.
- **Safety metadata:** `check_resource_budget` seeded in `TOOL_DEFAULTS` at S2906 with `default_safety_class='READ_ONLY'`. Applicability=always (LUNGS substrate always available; falls back to `can_proceed=True` on absence).

## 6. Evidence

### 6.1 T1a harness artifact — this ship

`docs/audits/pa_tools/harness_output/check_resource_budget.json` at HEAD `fc5bca145` (harness run 2026-07-23):

```json
{
  "actions": [],
  "harness_version": "v1",
  "schema_action_count": 0,
  "tool_name": "check_resource_budget"
}
```

Expected shape for actionless tools — zero rows.

### 6.2 Handler-trace evidence — this ship

Handler at `td_handlers_agents.py:4796-4820`:

- Line 4804: `from core.services.body_vitals import get_body_vitals_service` — LUNGS substrate service.
- Lines 4806-4807: read `estimated_tokens` and `estimated_cost` with 0-defaults.
- Line 4810: `budget = vitals.check_budget(estimated_tokens, estimated_cost)` — delegation.
- Lines 4812-4820: response envelope carries `budget_status`, `oxygen_level`, `can_proceed`, `warning`, `recommendation` — all sourced from the `body_vitals.check_budget` return dict with `.get()` fallbacks.

### 6.3 Runtime-not-executed — this ship

Actionless — no live dispatch was required for S2906 sweep-batch validation. Cross-family reference: `get_body_vitals_validation.md` (this batch) validates the parent LUNGS substrate service via a sibling tool; `check_resource_budget` is a specialized read against the same service.

---

## 6a. Next stress test (S2907 pointer)

Per Rigby S2906 T0 SIGN zoom-out AGREE-with-edits: S2907 sweep batch commits to including a **small-actionful, all-read-only** tool (2-3 actions) to stress-test the handler-trace-evidence-required-for-`## Covered actions`-authoring claim under non-trivial action enumeration.

---

## Related

- **Ledger candidates surfaced this ship:** none unique to this tool. `check_resource_budget` is the drift-clean member of the batch — schema and handler are consistent.
- **Adjacent tools:**
  - `cost_telemetry_tool` (S2905 batch 1) — historical actual spend from `LLMCallLog`. Different question class: `check_resource_budget` = "should I run this?" vs `cost_telemetry_tool` = "how much did I spend?"
  - `get_body_vitals` (this batch) — parent LUNGS-family read; `check_budget` is the specialized budget-only slice.
  - `workspace_budget_tool` (validated_full, S2894) — per-workspace budget rows; staff-authored caps.
- **Substrate context:** part of S2906 4-actionless batch. Batch peers: `get_body_vitals`, `get_system_alerts`, `web_search`.
- **Prior work:** LUNGS body-system integration predates the sweep; no prior validation doc. First entry into the validated corpus this session.
