# Session 2938 — Ledger #5 Schema-vs-Handler Consistency Lint (Tier 1 MVP)

**Date:** 2026-07-24
**Branch:** main
**HEAD at close:** `6ce7c0501` (PR #3512 merge SHA)
**PR shipped:** [#3512](https://github.com/clwest/donkey-betz-platform/pull/3512) — admin-merged squash

---

## Chris D-verdict at S2938 T0

**Path B ratified.** Slice 7 Batch 2a (3 mutation-tool validation docs) paused for one session to promote Ledger #5 schema-vs-handler consistency lint to substrate. Batch 2a re-queues to S2939+ with the lint now in-force at pre-flight.

**Reason:** 3-cycle promotion threshold met at S2937 close (schema-under-describes-handler drift surfaced at S2935 recent_activity/surgical_moves realignment + S2936 blog/feedback §5c.1 + S2937 rigby_shift_brief PARTIAL DRIFT + Ledger #39 rigby_work_queue docstring stale). Lint promotion buys durable detection for remaining 6 Slice 7 tools + all future PA-tool additions.

---

## What shipped (PR #3512, merge SHA `6ce7c0501`)

**Code:**
- `core/services/pa_tools_gap_map.py` (+132 lines) — Ledger #5 substrate: constants for negative-claim patterns + evidence signatures + number-word map + `lint_schema_vs_handler()` function.
- `core/management/commands/build_pa_tool_audit.py` (+40 lines) — `_load_handler_module()` helper (per-file cache keyed by absolute path; silent-fail on OSError/SyntaxError) + `_inspect()` wiring to capture `handler_source` + `handler_docstring`.
- `core/tests/test_pa_tools_gap_map_ledger_5.py` (new, 181 lines) — 11 contracts across 3 classes.

**Two new lints emitted:**
1. `handler_drift_action_count` — flags docstring-vs-enum action-count disagreement (e.g. "four actions" but enum has 5).
2. `handler_drift_negative_claim_{dispatch,mutation,feature_flag}` — flags negative claims contradicted by handler source (celery primitives / curated service-layer functions / ORM writes / settings-env reads).

**Auto-gen doc regen (`--include-validation-xref` shape):**
- `docs/PA_TOOL_AUDIT.md` (+2 lint tags on `rigby_work_item` row + validated_full count advance 89→92 from S2937 PR #3510 landing).
- `docs/audits/PA_TOOLS_GAP_MAP.md` (same 2-tag delta).

---

## Live backfill results (117 tools)

| Lint tag | Hit count | Tools flagged |
|---|---|---|
| `handler_drift_action_count` | 1 | `rigby_work_item` (docstring says "four actions", enum has 5 since `delegate` was added Session 1250 PR 8) |
| `handler_drift_negative_claim_dispatch` | 1 | `rigby_work_item` (docstring says "No agent dispatch" but `_rigby_work_item_delegate` calls `rigby_mission_delegation.delegate_work_item` which async-dispatches) |

**Zero false positives across the remaining 115 wired tools.** Both hits are the exact Ledger #39 case that S2937 §5c.1 sweep surfaced manually — the lint would have caught it before manual detection was needed.

---

## Rigby SIGN cycle

**T0 SIGN AGREE** (tool-grounded — 4 substantive tool_runs pulling handler source + grepping dispatch primitives + opening gap_map + locating audit command; per `feedback_verify_rigby_tool_runs_before_trusting_sign`):

- **Q1 AGREE:** Tier 1 scope (2 lints) is right MVP boundary — not smaller (1 lint drops action-count OR negative-claim coverage) not larger (Tier 2 envelope-JSON is separate ship).
- **Q2 AGREE:** extend existing "Schema quality lints" section with `handler_drift_*` prefix. No new section for MVP.
- **Q3 REFINED (F-BLOCKING):**
  - Add negative-claim patterns: "does not dispatch" / "doesn't dispatch" / "side-effect free". **Incorporated.**
  - Broaden dispatch evidence to catch curated service-layer functions since celery primitives may live one call deep from the handler (e.g. `rigby_mission_delegation.delegate_work_item`). **Incorporated — new test Contract 7 locks the Ledger #39 shape.**
- **ZO AGREE** (per `feedback_zoom_out_ask_per_rigby_sign`): Tier 2 (envelope-JSON top-level-key parse) defer is right; scope-appropriate absent Chris bundling ask.

**Post-merge verify PASS on both tasks:**
- Task 1: Both `handler_drift_*` tags render on `rigby_work_item` row in PA_TOOL_AUDIT.md:158 + PA_TOOLS_GAP_MAP.md:165 + both summary blocks.
- Task 2: `rigby_work_item action=list` returned clean `disabled_response` (flag OFF as expected). Recycled workers register tool cleanly post-merge.

---

## Deferred to separate ships

- **Tier 2** — envelope-JSON top-level-key parse against schema description text. Would catch the `rigby_shift_brief` PARTIAL DRIFT (schema names 6 subsections but envelope has 4 undocumented top-level fields: `ok`/`summary_text`/`traffic_light`/`metadata`). Per Rigby ZO AGREE: separate ship absent Chris bundling ask.
- **Tier 3** — semantic-distance between description prose ("suggested next action") and envelope field names (`next_action`). Too fuzzy for MVP; needs curated corpus.

---

## Post-merge recycle (per PLAYBOOK-7.4.4)

Clean recycle at `sha=6ce7c0501964` via `make recycle-all` (surviving=none). Rigby verification confirms tool surface healthy post-recycle.

---

## Gap-map ratchet

- `validated_full`: 89 → 92 (+3 from S2937 PR #3510 landing).
- `untested`: 9 → 6 (-3, same reason).
- **New lint tags:** `handler_drift_action_count: 1` + `handler_drift_negative_claim_dispatch: 1`.
- Total per-tool docs: 109 (unchanged).

---

## Test coverage

- 50 total gap-map tests pass (`test_pa_tools_gap_map_2795` 39 existing + `test_pa_tools_gap_map_ledger_5` 11 new). Zero regressions.
- 11 new contracts across 3 classes:
  - `ActionCountDriftTests` (5 contracts) — number word / digit / silent-cases / no-enum.
  - `NegativeClaimDriftTests` (5 contracts) — apply_async / service-layer / ORM save / settings read / silent honest case.
  - `BuildGapMapIntegrationTests` (1 contract) — `lint_schema` + `lint_schema_vs_handler` merged into `row['lints']`.

---

## Governance

None this session. D6 moratorium unchanged. Zero new forbidden-entry candidates.

---

## Rigby Tool Gap Ledger

No new entries this session. Ledger #5 promoted to substrate per this ship.

---

## Files changed

```
core/management/commands/build_pa_tool_audit.py  |  40 +++
core/services/pa_tools_gap_map.py                | 132 ++++++++-
core/tests/test_pa_tools_gap_map_ledger_5.py     | 181 +++++++++++++++ (new)
docs/PA_TOOL_AUDIT.md                            |  14 +-
docs/audits/PA_TOOLS_GAP_MAP.md                  |   4 +-
5 files changed, 363 insertions(+), 8 deletions(-)
```
