# `get_system_alerts` — Validation Report (S2906)

**Tool:** `get_system_alerts`
**Schema:** `core/services/pa_tool_schemas.py:745`
**Handler:** `core/services/td_handlers_agents.py:4822` (`_handle_system_alerts`)
**Register site:** `core/services/tool_dispatcher.py:415`
**Session:** S2906 (Path B systematic sweep — Slice 2 batch 2 of `td_handlers_agents`, first actionless-shape batch post-substrate)
**HEAD at validation:** `e59320017`
**Ship shape:** Doc-only + same-PR handler fix (S2796 shape). Regression tests deferred; handler fix carries the drift mitigation.
**Category upgrade target:** `untested` → `validated_full` (actionless — no schema `action` enum to iterate).
**Rigby SIGN:** S2906 T0 SIGN AGREE-with-edits (same-PR handler fix directed by T0 SIGN §C) + S2906 T1 SIGN AGREE-with-1-edit (B: legacy `severity_threshold` unknown-value normalization — folded same-PR; 9 verification tool_runs; zoom-out: drift as systemic trend candidate). Post-fold branch coverage validated via 8-case simulation.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Filtered read over active system alerts and warnings emitted by the BodyCoordinator across the 9 body systems. Answers "what's currently unhealthy or degraded on the platform?" filtered by severity threshold. Use when the user asks about alerts, warnings, or wants a focused view narrower than a full `get_body_vitals` snapshot.

Distinct from `get_body_vitals` (this batch — full per-system vitals; `alerts` is one of several output slices) and from `diagnostics_tool` (validated_full — infra-side diagnostic surface). `get_system_alerts` is the specialized "just show me the alerts" filter over the BodyCoordinator alert stream.

## Covered actions

**This tool is actionless by schema design** — `schema_action_count=0` per T1a harness artifact (`docs/audits/pa_tools/harness_output/get_system_alerts.json`), no `action` enum declared in the schema at `pa_tool_schemas.py:750-756`.

Therefore `## Covered actions` is intentionally empty. S2906 batch 2 validates **(a)** actionless doc shape under T1b template v1, **(b)** `TOOL_DEFAULTS` READ_ONLY applicability when there is no action enum to iterate, and **(c)** schema-vs-handler drift detection — this tool exhibits param-name + enum-domain drift documented in §5 below, with a same-PR handler mitigation shipped this batch.

## 3. Schema notes

- **Required:** none.
- **Optional (declared):** `severity` (string, enum: `critical, high, medium, low`) and `limit` (int, default 10).
- **Handler-actual (pre-S2906 fix):** read `severity_threshold` (string, enum: `info, warning, critical`) and ignored `limit` entirely — see §5 drift finding.
- **Handler-actual (post-S2906 fix, this batch):** accepts BOTH `severity` (schema-declared, preferred) and `severity_threshold` (legacy fallback). Schema enum values `critical/high/medium/low` map into the handler's internal `info/warning/critical` domain per documented mapping. `limit` remains handler-side ignored (see §5 fix scope).
- **Handler-side default:** `severity_threshold='warning'` (equivalent to schema `severity='medium'` post-mapping).

## 4. Golden-path examples

**"Show me all alerts at warning+ severity" (default):**

```
get_system_alerts
```

**"Only critical alerts" (schema-preferred):**

```
get_system_alerts  severity=critical
```

**"Medium and above" (schema-preferred):**

```
get_system_alerts  severity=medium
```

**Legacy shape (still supported post-fix):**

```
get_system_alerts  severity_threshold=warning
```

## 5. Failure / empty-state / pagination notes

- **No pagination** — single-shot alerts read; the `limit` schema param is not consumed by the handler (see §5 fix scope caveat).
- **Response shape** — `{severity_threshold: <mapped-internal-value>, alert_count: <int>, alerts: [...]}`. Each alert dict carries `severity` (info/warning/critical) plus system-specific payload from BodyCoordinator.
- **Empty-alerts state** — `{severity_threshold: '<value>', alert_count: 0, alerts: []}`. Not an error path.
- **Invalid `severity` value (schema domain)** — post-fix handler tolerates unknown schema-enum values by falling through to the default threshold (`warning`); no exception raised. Fallback via `_SEVERITY_SCHEMA_TO_INTERNAL.get(raw_severity, 'warning')`.
- **Invalid `severity_threshold` value (legacy domain)** — post-Rigby-T1-SIGN-B-edit: unknown legacy values (e.g. `severity_threshold='HIGH'`) also normalize to `'warning'` rather than falling through to `threshold_idx = 0` (which would have silently downgraded to `info`). Pre-fix pre-edit handler had the same forgiving `severity_order.index(...) if ... in severity_order else 0` behavior; post-edit both paths converge on the same historical `warning` default.
- **No latency measurement in this ship** — T1a harness produced no artifact rows (actionless).

**Drift finding — schema/handler param-name + enum-domain mismatch (same-PR mitigated this batch):**

- Schema at `pa_tool_schemas.py:750-756` declares `severity` with enum `critical/high/medium/low`.
- Handler at `td_handlers_agents.py:4832` (pre-S2906) read `severity_threshold` with enum `info/warning/critical`.
- **Two independent divergences:** (a) param name (`severity` vs `severity_threshold`); (b) enum domain (4 marketing/industry-standard levels vs 3 log-level-standard levels).
- **Real operator impact (pre-fix):** an LLM-authored tool_call following the schema would pass `severity='critical'`. The pre-fix handler read `payload.get('severity_threshold', 'warning')` — the schema-conformant call would be silently ignored, and the handler would run at the default `warning` threshold. Zero-error silent-drift class.
- **Class:** schema-handler-contract-divergence with silent fallthrough. Distinct from the other batch drift finds (`web_search` + `get_body_vitals` = handler-reads-undeclared-params; this one = handler-reads-differently-named-param and-different-enum-domain).
- **This ship — same-PR handler fix (per Rigby T0 SIGN AGREE-with-edits §C):**
  1. Handler now reads BOTH `severity` (preferred) and `severity_threshold` (legacy fallback), with `severity` winning when both are present.
  2. Schema enum values map into the handler's internal domain per this table:
     - `critical` → `critical` (both domains have this level).
     - `high` → `warning` (mapped up from log-level `warning`).
     - `medium` → `warning`.
     - `low` → `info`.
  3. Schema left as-is (no enum change). Legacy `severity_threshold` still supported for callers pinned to the old contract.
- **`limit` fix scope:** NOT fixed this batch. Schema declares `limit` (default 10) but handler ignores it entirely. Deferred as separate Ledger candidate — same class as the `web_search` `limit` handling but inverted (there handler reads undeclared limit; here handler ignores declared limit). Same-PR fix scope kept tight to the load-bearing drift (severity domain) per Rigby T0 SIGN.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

- **Mutating actions:** none. Read-only alert filter — `body_vitals.get_all_vitals()` computes against current BodyCoordinator state; handler filters the `alerts` slice in-memory.
- **Safety metadata:** `get_system_alerts` seeded in `TOOL_DEFAULTS` at S2906 with `default_safety_class='READ_ONLY'`. Applicability=always (LUNGS substrate always available; falls back to empty alerts list on absence).

## 6. Evidence

### 6.1 T1a harness artifact — this ship

`docs/audits/pa_tools/harness_output/get_system_alerts.json` at HEAD `fc5bca145` (harness run 2026-07-23):

```json
{
  "actions": [],
  "harness_version": "v1",
  "schema_action_count": 0,
  "tool_name": "get_system_alerts"
}
```

Expected shape for actionless tools — zero rows. The drift finding surfaced via handler-trace + schema-diff reading during S2906 doc authoring, not from harness output.

### 6.2 Handler-trace evidence — this ship

**Pre-fix handler** at `td_handlers_agents.py:4822-4852` (as of HEAD `e59320017`):

- Line 4830: `from core.services.body_vitals import get_body_vitals_service`.
- Line 4832: `severity_threshold = payload.get('severity_threshold', 'warning')` — legacy param name.
- Line 4835: `all_vitals = vitals.get_all_vitals()`.
- Lines 4837-4846: severity-order index computation + filtering.
- Lines 4848-4852: response envelope with `severity_threshold`, `alert_count`, `alerts`.

**Post-fix handler** shipped this PR — see PR body for exact diff. Key change: bidirectional param-name acceptance + explicit enum-domain mapping. No behavioral regression for legacy callers.

### 6.3 Runtime-not-executed — this ship

Actionless — no live dispatch was required for S2906 sweep-batch validation. Post-fix handler behavior verified via Rigby T1 SIGN cycle (see §Related pointer).

---

## 6a. Next stress test (S2907 pointer)

Per Rigby S2906 T0 SIGN zoom-out AGREE-with-edits: S2907 sweep batch commits to including a **small-actionful, all-read-only** tool (2-3 actions) to stress-test the handler-trace-evidence-required-for-`## Covered actions`-authoring claim under non-trivial action enumeration.

---

## Related

- **Ledger candidates surfaced this ship:**
  - **`get_system_alerts` `limit` schema-declared-but-handler-ignored** — Rigby Tool Gap Ledger candidate. Deferred (not fixed same-PR); scope kept tight to the load-bearing severity-domain drift per Rigby T0 SIGN §C. Sibling ledger candidates from this batch: `web_search` silent-limit-expansion + `get_body_vitals` silent-parameter-invisibility.
- **Adjacent tools:**
  - `get_body_vitals` (this batch) — parent LUNGS-family read; alerts are one slice of the full vitals return.
  - `check_resource_budget` (this batch) — LUNGS-family specialized budget gate.
  - `diagnostics_tool` (validated_full, S2894) — infra-side diagnostics; different substrate.
  - `status_snapshot_tool` (validated_full, S2894) — broader overview; may include alert count in summary section.
- **Substrate context:** part of S2906 4-actionless batch validating the actionless doc shape post-S2905 mixed-safety pattern batch. Batch peers: `check_resource_budget`, `get_body_vitals`, `web_search`.
- **Prior work:** BodyCoordinator alert stream + `body_vitals.get_all_vitals()` predate the systematic sweep; no prior validation doc. First entry into the validated corpus this session.
