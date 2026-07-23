# T1a — Auto-Harness Build

**Parent:** [S2900 substrate arc scoping](S2900_substrate_arc_scoping.md)
**Session estimate:** ≤2 sessions (scaffold + harden). MVP discipline is a hard cap per parent §5.
**Depends on:** T1c completion (in-class boundary decision + Action Metadata Map location).
**Blocks:** T1b (template extraction needs stable T1a output schema before rigidifying).

---

## 1. Goal

Build `pa_tool_validate_harness` — a Django management command that, given a PA tool name, enumerates the schema's `action` enum, dispatches read-only actions in-process against the local dispatcher, captures response + latency + tool_runs shape, and emits a structured JSON artifact.

Primary savings vector: **eliminate human dispatch + manual note-taking** for the ~76 remaining tools in the sweep. Not: exhaustive integration coverage. Not: HTTP-layer or auth-boundary validation. Not: golden-file regression suites.

## 2. Non-goals (per parent §2 + §5)

- **Not** an HTTP-surface tester. In-process against `ToolDispatcher._tool_handlers` directly.
- **Not** an auth-boundary tester. Runs as the harness caller's identity; auth-gated actions are classified `WRITE_GATED` and validated at schema-edge only.
- **Not** a mutation exerciser. `WRITE_GATED` + `SIDE_EFFECT` actions are inspected for schema + permission surface, never executed with real side effects.
- **Not** a replacement for `http_smoke_test`. Output schema is superset-compatible so harness output can *feed* smoke tests, but harness does not itself replay them.

## 3. Per-action safety classifier (Rigby Fold Q1)

Every action in a tool's `action` enum gets classified:

| Class | Auto-execute? | Behavior |
|---|:-:|---|
| `READ_ONLY` | yes | Full dispatch with minimal safe args. Capture response + latency. |
| `WRITE_GATED` | no | Schema-edge only. Assert 400/403/expected-error shape. No real mutation. |
| `SIDE_EFFECT` | no | Documented + skipped. Requires human-authored validation entry. |

Default classification is **conservative** — if unclassified, treat as `WRITE_GATED` (do-not-execute). Per-tool classification lives in the Action Metadata Map (§4).

## 4. Action Metadata Map (Rigby Fold Q4 micro-thread)

**Location:** in code, adjacent to `ToolDispatcher` (exact path decided during T1a scaffold). **Not** in per-tool doc frontmatter.

**Shape (per-tool, per-action):**

```python
{
    "safety": "READ_ONLY" | "WRITE_GATED" | "SIDE_EFFECT",
    "auth_required": None | "owner" | "staff",
    "env_required": None | ["local"] | ["redis"] | ["celery"] | ["external:<name>"],
    "mutation": bool,
    "notes": str | None,
}
```

**Population strategy for T1a v1:** bootstrap from the existing per-tool validation docs where they document the surface (22 tools). New tools swept post-T1a get metadata authored alongside the validation doc (T1b template will include a metadata-map hook).

**Interaction with T1c:** T1c produces the initial bucket-triage. Tools bucketed "close with a short note" contribute no metadata (they don't run in the harness). Tools bucketed "promote to full sweep" get metadata authored during their sweep session.

## 5. Output-schema contract (Rigby Fold Q3)

Stable minimal shape — changes to this contract require substrate-arc-scoped SIGN:

```json
{
  "tool_name": "workspace_budget_tool",
  "harness_version": "v1",
  "dispatched_at": "2026-07-22T00:00:00Z",
  "actions": [
    {
      "action": "list",
      "safety_class": "READ_ONLY",
      "input_profile": "minimal_safe_args_v1",
      "expected_outcome": "success",
      "status_code": 200,
      "latency_ms": 15,
      "response_shape_keys": ["count", "workspaces", "total_spend_usd"],
      "notes": null
    },
    {
      "action": "set_daily_cap",
      "safety_class": "WRITE_GATED",
      "input_profile": "schema_edge_only",
      "expected_outcome": "auth_deny_expected",
      "status_code": 403,
      "latency_ms": 3,
      "response_shape_keys": ["error", "code"],
      "notes": "requires owner auth; harness validates schema+auth-edge only"
    }
  ]
}
```

**Superset-compatibility criterion:** any field the `http_smoke_test` runner needs to replay an action MUST be reconstructable from this artifact + the schema. If a field is needed and missing, add it to the contract (via substrate-arc SIGN); do not silently extend per-tool.

## 6. Ship shape

- Django management command: `python manage.py pa_tool_validate_harness <tool_name>` (single tool) OR `--all-in-class` (all in-class tools per T1c bucket).
- Output artifact written to `docs/audits/pa_tools/harness_output/<tool_name>_<timestamp>.json` (git-tracked; small enough).
- Gap-map lint extension: `docs/audits/PA_TOOLS_GAP_MAP.md` gains a "harness coverage" column derived from artifact presence + freshness (age of artifact vs. tool schema HEAD hash).
- Doc-only ship acceptable (per S2796 shape); regression tests deferred to a later substrate row unless a real regression surface emerges during T1a use.

## 7. Anti-scope-creep watchlist

If any of these come up during T1a execution, **defer to a follow-on substrate row** — do not expand T1a scope:

- Async / Celery task waiting + result polling
- Pagination cursor exercising
- Golden-file diff regression harness
- Multi-user auth-context exercising
- Live rate-limit interaction
- Cross-tool orchestration chains

Each of these has real value; none is T1a MVP.
