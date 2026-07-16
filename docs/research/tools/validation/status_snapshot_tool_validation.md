# `status_snapshot_tool` — Validation Report (S2796)

**Tool:** `status_snapshot_tool`
**Schema:** `core/services/pa_tool_schemas.py:563`
**Handler:** `core/services/td_handlers_ops.py:4289` (`_handle_status_snapshot`)
**Register site:** `core/services/tool_dispatcher.py:460`
**Session:** S2796 (Slice 1 of `td_handlers_ops` validation)
**HEAD at validation:** `0c38718b0`
**Ship shape:** Doc-only (per S2796 Chris directive "validation quickest"). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (per gap-map classifier — non-action-multiplexed schema)
**Rigby SIGN:** S2796 T1 SIGN-WITH-EDITS; 6-section template per Rigby Z3; evidence per Rigby Z1 edit A.

---

## 1. Purpose / when-to-use

`status_snapshot_tool` is the "how is the system doing right now" one-shot answer. 12-section snapshot covering initiatives, PA tool calls, latest HeartBeat health, spider ingest, conversations, signal clusters, Celery task volume, error detections, blogs, actuator counts (initiatives activated / decisions made / deliverables created), plus a lightweight `ops` block (version SHA + slo_breaches count). Cached 60s server-side to keep the 12-query fan-out cheap.

Distinct from `ops_tool.overview` — `ops_tool.overview` is production-reliability-scoped (version + SLOs + failures + noise); `status_snapshot_tool` is broader-scoped (business/content/actuator + reliability). Distinct from `diagnostics_tool` — `diagnostics_tool` is per-component inventory audit; `status_snapshot_tool` is a fixed 12-section dashboard.

## Covered actions

`status_snapshot_tool` has **no `action` parameter** — the schema exposes only `sections` (optional array of section names). Classifier logic at `core/services/pa_tools_gap_map.py:228-231` treats non-action-multiplexed tools with a `Covered actions` heading as `validated_full` if any evidence is present. The following backtick-enumerated identifiers stand in for the flat "invocation surface" of the tool per Rigby SIGN Z1 edit A (F1):

- `status_snapshot` (default invocation, no params) — **in scope this ship** — verified live at S2796 T1 (see §Evidence). Returns the full 12-section snapshot.
- `sections` param filtering — runtime-not-executed. Handler code at `td_handlers_ops.py:4289-4470` was not traced to confirm whether the `sections` param actually filters (needs handler audit for follow-up PR).

## 3. Schema notes

- **Required:** none (`required: []` implicit — no required marker in schema).
- **Optional params:**
  - `sections` — array of strings; schema documents `agents / spiders / initiatives / health / activity` as candidates. Behavior when passed is deferred (see §2).
- **Schema description lint (per S2795 F5):** none flagged.
- **Cache:** server-side 60s via `django.core.cache.cache.get('pa:status_snapshot')`. Callers get stale-within-60s data but no cache-age field is surfaced. **DOC-note follow-up: consider surfacing `cache_age_seconds` or `cache_hit: true/false` in response for observability.**

## 4. Golden-path examples

**Broad system dashboard (S2796 T1 usage):**

```
status_snapshot_tool                       # returns 12-section snapshot, cached 60s
```

**Executive-summary answers:** invoke with no params when asked "how is the system doing?", "give me a summary", or "system overview". The 12 sections cover most first-order operator questions.

## 5. Failure / empty-state / pagination notes

- **Per-section fail-soft:** each of the 12 sections wraps its query in `try/except`; a section that fails returns `{'error': str(e)}` in place of expected shape. Rigby's caller must check per-section rather than assume top-level success.
- **Empty state:** sections return `{'count': 0}` or equivalent zero-counts when nothing is present in the 24h window (e.g. `conversations_24h.count = 0` observed at S2796 T1).
- **No pagination:** fixed-shape snapshot; no `limit` or `offset` params.
- **Cache staleness:** stale-up-to-60s. No indication in response when serving cached vs fresh.

## 6. Evidence

### 6.1 Observed run — this ship

**S2796 T1 evidence-capture dispatch** (`bash tools/pa_local.sh` → Rigby `status_snapshot_tool` invocation):

```json
{
  "initiatives": {"active": 5, "updated_24h": 0},
  "tool_calls_24h": {"total": 10, "failed": 0},
  "health": {"status": "healthy", "score": 87.5, "age_minutes": 7.7},
  "spiders_24h": {"items": 226, "active_spiders": 68},
  "conversations_24h": {"count": 0},
  "signal_clusters": {"active": 14},
  "celery_24h": {"total": 3032, "failed": 0},
  "errors_24h": {"count": 0},
  "blogs_24h": {"total": 0, "published": 0},
  "actuators_24h": {
    "initiatives_activated": 0,
    "blogs_publish_ready": 0,
    "decisions_made": 158,
    "deliverables_created": 4
  },
  "generated_at": "2026-07-16T02:36:17.233601+00:00",
  "ops": {"version_sha_short": "dev", "slo_breaches": 0}
}
```

**Response returned in 104ms** (from `Tool Runs (verbose)` block). 12 sections present. No per-section errors. `generated_at` ISO-8601 UTC — freshness surfaced.

**Observed anomaly:** `ops.version_sha_short = "dev"` while `git rev-parse --short HEAD = 0c38718b0`. Local dev environment resolves `version_sha_short` from a different source than `ops_tool.version` (which correctly returned `0c38718b0492` at the same session). **DOC-note follow-up: reconcile the two version-source paths (S2796 F4 candidate for next slice PR body).**

### 6.2 Runtime-not-executed — this ship

- `sections=[...]` filtering — not exercised; handler filtering behavior for this param is unverified.

---

## Related

- **S2795 gap map:** `docs/audits/PA_TOOLS_GAP_MAP_S2795.md`.
- **S2795 handoff:** `docs/handoffs/SESSION_2795_PA_TOOLS_GAP_MAP.md`.
- **S2796 zoom-out folds:** ledger rows 65-68.
- **Related tools:** `ops_tool.overview` (reliability-scoped counterpart), `diagnostics_tool.*` (per-component audit).
