# Session 2867 — count_by aggregate group-by action on orm_inspect_tool

**Date:** 2026-07-21
**Session pin:** `pa-f38da01b8355481f` (label `s2867-orm-count-by`)
**PR:** [#3353](https://github.com/clwest/donkey-betz-platform/pull/3353) `f201a7910`
**Slate:** S2867 slate #1 — Rigby Tool Gap Ledger 1st zoom-out fold from S2866

---

## What shipped

`orm_inspect_tool.action='count_by'` — aggregate group-by counts. 5th action on the bounded ORM inspector shipped at S2866. Extends "give me 5 rows for shape inspection" (S2866 `filter`) with "give me the shape of the whole set by <field>" (S2867 `count_by`). Directly answers Chris's original ask paraphrase: *"how many rows match X by day/status/source?"*

### Files touched (5)

| File | Δ | Purpose |
|---|---|---|
| `core/services/pa_tool_schemas.py` | +25 | action enum + `field` + `order_by_count` params |
| `core/services/td_handlers_agents.py` | +140 | `count_by` handler branch + `_validate_groupby_field` + `_coerce_group_value` |
| `core/tests/test_s2867_orm_count_by.py` | new (+414) | 27 pytest cases across 9 classes |
| `core/tests/test_s2866_orm_inspect_tool.py` | ±3 | baseline enum assertion updated for 5th action |
| `tools/pa_local.sh` | ±1 | session pin bump `pa-8005b98ba0524999` → `pa-f38da01b8355481f` |

### Behavior contract

- **Params:** `action='count_by'`, `model` (allowlisted), `field` (required), `filter_kwargs` (optional dict — reuses `_validate_filter_kwargs`), `limit` (default 50, max 500), `order_by_count` (`'desc'|'asc'`, default `'desc'`).
- **Field-type policy:** CharField / non-expensive TextField / IntegerField / BooleanField / DateField grouped as-is; ForeignKey grouped on `<field>_id` attname (matches serializer FK convention, avoids JOIN); DateTimeField auto-buckets to day via `TruncDate`.
- **Response:** `{ok, action, model, field, group_key, total_matching, group_count, returned, truncated, order_by_count, limit, groups:[{value, count}...]}`. Both `field` (caller intent) and `group_key` (actual column — `<fk>_id` or `_count_by_day_bucket`) are exposed.
- **Truncation semantics:** `truncated=false` → `group_count` is exact. `truncated=true` → `group_count = returned + 1` (lower bound). Single flag; no separate `COUNT(DISTINCT)` query issued.

### Rejection paths

- Unknown field → error surfaces the model name
- Sensitive-by-name field → same `_is_sensitive_field_name` check as filter/get
- JSONField → error with nudge ("use `filter_kwargs` with `has_key` + `count_by` on a categorical column instead")
- Expensive text field (per per-model `expensive_text_fields` policy) → error explains unbounded-distinct-value risk
- `filter_kwargs` → runs through existing `_validate_filter_kwargs` (deep chain / sensitive / expensive icontains / in-list cap all inherited)

---

## Discovery arc — 3 SIGN cycles

### Pre-code SIGN — 5 F-AGREE + 1 F-DISAGREE (model-level blocks unnecessary), 0 F-BLOCKING

Rigby verified via 4 `repo_tool` calls (schema/handler read, orm_inspect existing shape). Directly answered:
- Q1 API shape correctness → F-AGREE, with two required guardrails: (a) new `_validate_groupby_field` mirror of filter validator, (b) FK → attname
- Q2 DateTimeField default → F-AGREE, auto-`TruncDate` to day matches Chris's ask
- Q3 FK output → F-AGREE, id-only for v1; batched `value_repr` deferred
- Q4 cardinality caps → F-AGREE, default 50 / max 500 is proportional to filter's row cap
- Q5 model-level blocks → **F-DISAGREE** — none of the 8 allowlisted models warrant block; per-field guards cover the risk
- Q6 zoom-out (5th action vs separate tool) → F-AGREE for v1; carve out to `orm_aggregate_tool` only if multi-field group-by / joins / multi-bucket modes ever ship

### Post-code SIGN round 1 — F-DISAGREE on `group_count_is_lower_bound` naming (minor)

Live dispatches against 827 SignalClusters + 60333 LLMCallLogs:
- **Basic categorical:** 7 pattern_types (trend_emergence=317, demand_spike=238, skill_demand=128, ...) — clean sort
- **DateTimeField auto-day:** 11 distinct day buckets, top day = 2026-06-18 with 61 clusters
- **FK attname:** 60333 LLMCallLogs → 2 workspace groups (59655 null-bucket + 678 attributed to Donkey Betz workspace)
- **JSONField rejection:** correct error with nudge

Rigby folds:
- Q2 (`group_key_note` UX hint) — nice-to-have, deferred to v2 docstring
- Q3 (S2845-analog demo) — confirmed the escape hatch works: `filter_kwargs={source_breakdown__has_key: 'huggingface'}` + `count_by field='pattern_type'` answers the "AI/ML signals by pattern type" case in one call
- Q4 (`group_count_is_lower_bound` unclear) — **F-DISAGREE**, prefer `group_count_exact` or `group_count_truncated`
- Q5 (high-cardinality unindexed column risk) — deferred to v2 docstring; row cap already bounds response size

### Post-code SIGN round 2 — all F-AGREE

Q4 resolution: **dropped** the redundant field entirely rather than rename. Reasoning: it always flipped in lockstep with `truncated`, so keeping both signals was redundant duplication. Docstring now carries the semantic. Rigby's Q1: *"resolves the confusion and removes redundant signaling since it was perfectly coupled to `truncated`."* Q2 zoom-out: *"No new regression signals surfaced from the fold; the shape change is strictly subtractive."*

---

## Working loop observations at S2867

- **`feedback_verify_rigby_tool_runs_before_trusting_sign`** worked as designed all 3 cycles — pre-code Rigby ran 4 `repo_tool` calls to ground her Q1 answer against real handler/schema state; post-code round 1 ran 4 actual `orm_inspect_tool` dispatches against live DB (827 SignalClusters, 60333 LLMCallLogs) before signing off on shapes; post-code round 2 ran one confirmatory dispatch. Zero rubber-stamp SIGNs.
- **`feedback_zoom_out_ask_per_rigby_sign`** produced value both post-code rounds — round 1 named the S2845-analog demo (proving the escape-hatch works via one call) and the high-cardinality risk (folded to v2). Round 2 explicitly re-checked the rejection paths + FK-attname behavior would still hold post-fold.
- **`feedback_claude_stdout_truncation_vs_ui_truncation`** hit — pre-code SIGN response truncated mid-Q5 in my stdout; per the memory rule, I asked Rigby for a Q5+Q6 recovery (small delta call) rather than framing it as "you got cut off." Full response was in Chris's UI throughout.
- **`feedback_local_truth_no_production`** — recycle-after-merge (PLAYBOOK-7.4.4) fired; recycle-BEFORE-live-verify fired between code edit and each post-code SIGN round.
- **No candidate lessons for Playbook amendment this session.** Post-code Q4 F-DISAGREE resolved via drop-vs-rename judgment call — didn't require Chris tie-break per `feedback_claude_rigby_agree_first_chris_yes_no`.

---

## Rigby Tool Gap Ledger update

**Entry:** 1st zoom-out fold from S2866 (count_by aggregate group-by counts) → **Shipped**, `shipped_in_pr_3353`.

## PA tool surface after S2867

| Metric | Before | After |
|---|---|---|
| Tool schemas | 117 | 117 (same tool, more actions) |
| `orm_inspect_tool` actions | 4 | 5 (`list_models`, `describe_model`, `get`, `filter`, `count_by`) |
| Handlers | 160 | 160 (same handler, extended) |
| Test count for orm_inspect_tool | 36 | 63 (36 baseline + 27 new count_by) |

---

## What did NOT ship this session (folded / deferred to S2868+)

1. **Aggregate group-by counts on `orm_inspect_tool`** ← SHIPPED THIS SESSION
2. **Per-model `allowed_fields` explicit allowlist** — 1st trigger only; deferred until real slip-through
3. **Provider-specific composite additions** — reactive; watch for new integrations
4. **S2862 Q5.a bimodal-collector fold** — still 2 triggers, not yet promoted to spec_backlog
5. **SIGN discipline Playbook amendment** — 1st trigger only (S2864)
6. **`group_key_note`** (S2867 post-code Q2 fold) — deferred, v2 docstring only
7. **High-cardinality guardrail warning** (S2867 post-code Q5 fold) — deferred, v2 docstring only

---

## For fuller A1 W1 + W2 arc context (S2846 → S2867)

See:
- **S2867 handoff (current):** `docs/handoffs/SESSION_2867_ORM_COUNT_BY.md`
- **S2866 handoff:** `docs/handoffs/SESSION_2866_ORM_INSPECT_TOOL.md`
- **S2865 handoff:** `docs/handoffs/SESSION_2865_WEB_FETCH_TOOL.md`
- **S2864 handoff:** `docs/handoffs/SESSION_2864_HF_BACKFILL_VIEW_CLEANUP.md`
- **S2863 handoff:** `docs/handoffs/SESSION_2863_HF_HUB_API_SORT_DOWNLOADS.md`
- **S2846 A1 W1 P1/P2 close:** `docs/handoffs/SESSION_2846_A1_W1_PHASE1_PHASE2_SHIPPED.md`
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`

For older session history (S1–S2845), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
