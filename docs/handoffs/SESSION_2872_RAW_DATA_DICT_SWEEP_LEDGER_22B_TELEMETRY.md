# Session 2872 — Ledger #22b raw_data_dict sweep + schema-drift telemetry

**Date:** 2026-07-21
**Prior session:** S2871 (Ledger #22 + #23 + #24 tool-surface triple)
**Next session:** S2873
**PR shipped:** #3365 (`a54998be4`) — 30 files, +308/-46

## What shipped

**Rigby Tool Gap Ledger #22b** — broader `raw_data_dict` standardization sweep. Extends S2871 PR #3363 (which shipped the `LegacySpiderData.raw_data_dict` property + 16 initial migrations). This session covered the remaining backlog.

### Migration scope

44 crash-risk callsites migrated across 30 files from `raw = X.raw_data or {}` → `raw = X.raw_data_dict`. The old pattern silently failed on list-form LegacySpiderData rows because list is truthy: `[] or {}` returns `[]`, then `.get()` raises `AttributeError`.

Callsite breakdown (all confirmed LegacySpiderData readers via queryset context sweep):

| Directory | Sites | Files |
|---|---:|---|
| `core/tasks*.py` | 8 | `tasks.py` (1), `tasks_ops.py` (3), `tasks_misc.py` (4) |
| `core/views_*.py` | 4 | `views_spider_intelligence.py` (2), `views_project_intelligence.py` (2) |
| `core/models_*.py` | 1 | `models_situation_triggers.py:298` (line 383 write-path snapshot kept per property docstring) |
| `core/services/` | 13 | `autonomous_loop.py` (2), `smart_trending_service.py` (1), `signal_aggregation_service.py` (2), `persona_agent_context.py` (1), `ml_scoring_engine.py` (3), `collective_intelligence.py` (1), `congress_sync.py` (1), `ops_autopilot/revenue.py` (2), `discord_bot.py` (1) |
| `core/agents/` | 17 | `analysis/opportunity_scoring_agent.py` (2), `base_agent.py` (1), `narrative/narrative_drift_coordinator.py` (1), `narrative/trend_break_detector_agent.py` (2), `stocks/stock_analyst_agent.py` (3), `stocks/institutional_watcher_agent.py` (1), `stocks/market_anomaly_detector_agent.py` (2), `stocks/market_movement_monitor_agent.py` (1), `stocks/market_intelligence_coordinator.py` (1), `blockchain/blockchain_audit_coordinator.py` (1), `markets/line_movement_analyzer.py` (1), `legal/legal_doc_drafter_agent.py` (1) |
| `core/management/commands/` | 1 | `backfill_huggingface_items.py` (1) |
| **Total** | **44** | **29 files** |

### Scope discipline (Category triage)

Rigby's pre-code SIGN Q1 F-AGREE established the discipline:

- **Category A (crash-risk):** unguarded `raw = X.raw_data or {}` on LegacySpiderData readers → **44 sites migrated** ✅
- **Category B (already `isinstance(..., dict)`-guarded):** ~8-10 sites in `td_handlers_content.py`, `tasks_content.py`, `views_spider_data.py`, `views_spider_dashboard.py`, `marketplace_discovery_service.py`, `platform_intelligence_briefing.py`, `spider_intelligence.py`, `living_project_service.py`, `content_diversity_orchestrator.py` → **SKIPPED** (cosmetic churn)
- **Category C (different model):** `persistence.models.SpiderData` in `views_odds_sports.py`, `Opportunity` in `intelligence/*` + `income_builder.py` + `revenue_opportunities_consumer.py`, `research` in `project_research_bridge.py`, duck-typed `model_registry.py` → **SKIPPED** (belongs to wish-list #2 + #3 for allowlist extension)

### Rigby Q4 zoom-out fold shipped — schema-drift telemetry

Extended the property with rate-limited debug telemetry to prevent silent data drops:

`core/models_unified_system.py:29-49` — module-level counter + helper:
```python
_NON_DICT_RAW_DATA_COUNTER: dict[str, int] = {}
_NON_DICT_RAW_DATA_LOG_INTERVAL = 100

def _record_non_dict_raw_data(instance, raw) -> None:
    spider_name = getattr(instance, 'spider_name', '<unknown>') or '<unknown>'
    _NON_DICT_RAW_DATA_COUNTER[spider_name] = _NON_DICT_RAW_DATA_COUNTER.get(spider_name, 0) + 1
    count = _NON_DICT_RAW_DATA_COUNTER[spider_name]
    if count == 1 or count % _NON_DICT_RAW_DATA_LOG_INTERVAL == 0:
        logger.debug(
            "LegacySpiderData.raw_data_dict fallback: spider=%s type=%s count=%d",
            spider_name, type(raw).__name__, count,
        )
```

`core/models_unified_system.py:3820-3833` — property invokes helper on fallback:
```python
raw = self.raw_data
if isinstance(raw, dict):
    return raw
_record_non_dict_raw_data(self, raw)
return {}
```

Rationale (Rigby's exact fold): "`raw_data_dict` is good as a safety shim, but canonicalizing it everywhere can create silent failure modes. If a spider (or legacy row) starts emitting list-form raw_data unexpectedly, `raw_data_dict` returns `{}` and downstream logic may quietly treat the row as 'empty' instead of failing loudly. That trades a crash (bad) for a silent data drop (also bad, harder to detect)."

Rate limit: first fallback + every 100th per spider_name emits a debug log; every fallback increments the counter. Property is the right telemetry choke-point (Rigby Q4b F-AGREE) — captures every downstream use; upstream-only telemetry would miss legacy rows.

## Test evidence

New file: `core/tests/test_s2872_ledger_22b_raw_data_dict_sweep.py` — 11 tests across 3 test classes:

- `MigratedCallsitesListFormTests` (3): spot-checks that `models_situation_triggers.SituationTrigger.evaluate()` + `signal_aggregation_service._extract_url_from_spider_data()` + `_extract_text_from_spider_data()` no longer crash when row holds list-form `raw_data`
- `DictFormNoRegressionTests` (2): confirms dict-form rows still extract values correctly (happy path preserved)
- `NonDictTelemetryTests` (6): counter increments on non-dict, doesn't increment on dict, first-hit log emitted, rate limit works (101 hits = 2 log lines), NoneType recorded correctly (in-memory instance since DB has NOT NULL), helper directly invokable

**Combined regression suite (S2869 + S2870 + S2871 + S2872): 60/60 pass.**

## Discovery arc

### Pre-code SIGN cycle

Claude's initial survey: 8 sites in 5 files ("safe minimal set").

Rigby's Q2 caution triggered a narrow re-sweep — files that contain BOTH `LegacySpiderData` AND `raw_data or {}`. Result: 44 sites in 30 files. Claude's initial estimate had significantly under-counted because it stopped at the files 00-START explicitly named without doing the follow-up pattern-search.

Q4 zoom-out surfaced the biggest fold — telemetry addition. Reshaped the property to instrument fallback rather than silently returning `{}`.

Q1 F-AGREE established Category B/C skip discipline.
Q3 F-AGREE confirmed the SituationTrigger `[raw_data]` default semantic is preserved (dict-form: unchanged; list-form: becomes `[{}]`, preserving single-item-list control flow).
Q5 F-DISAGREE (correctly) rejected the lint-style unit test as brittle.

### Post-code SIGN cycle

All 4 questions F-AGREE with tool_runs evidence:

- Q1: `orm_inspect_tool.describe_model` + `filter` + `count_by(field='spider_name')` — 15,618 rows load cleanly post-change
- Q2: `repo_tool.search path='core/' query='raw_data or {}'` returns only 7 files, all in expected buckets (test docstrings, write-path, Category B/C, ambiguous duck-typed) — no unguarded LegacySpiderData readers remain
- Q3: telemetry code path verified via targeted grep against file lines
- Q4a: 44-edit atomic ship justified (mechanical fix, full regression pass); Q4b: property is correct telemetry location; Q4c: no pushback beyond keeping telemetry debug-level (already done)

**Recommendation to Chris:** ship. Chris ratified.

## Working loop observations at S2872

- `feedback_verify_rigby_tool_runs_before_trusting_sign` fired 2× — both SIGN cycles grounded in tool_runs evidence.
- `feedback_zoom_out_ask_per_rigby_sign` yielded 2 usable folds: (1) telemetry addition (biggest fold — reshaped property design); (2) scope-broadening via Rigby's Q2 caution (8→44 sites).
- `feedback_claude_rigby_agree_first_chris_yes_no` applied — presented Chris one recommendation after Claude+Rigby agreement.
- `feedback_engineering_bias_over_audit` — this was a net-new engineering ship, not an audit.
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) applied post-merge: `make recycle-all` clean, `sha=a54998be4d59, surviving=none`.
- `feedback_read_full_rigby_response_not_just_tail` — I initially truncated Rigby's pre-code SIGN body with `tail -200`; re-fetched to read the full F-verdict prose.

## New Rigby-observed tool-surface gaps (candidates for future ledger entries)

Both flagged during S2872 post-code SIGN tool_runs:

1. **`orm_inspect_tool` can't JSON-type filter/count JSONField rows.** No `jsonb_typeof`-style predicate available. Meant Rigby couldn't quantify list-form prevalence via tool alone (had to trust test fixtures). Would enable direct queries like "count LegacySpiderData rows where raw_data is not a dict."

2. **`repo_tool.read_file` line caps on large files.** Rigby couldn't `read_file` `core/models_unified_system.py` directly ("file too large: 554359 bytes") — had to rely on `search` anchors. Awkward for verifying specific line ranges when file is too big.

Neither logged to the Ledger yet; watch for second-trigger before promoting.

## Not shipped at S2872 (deferred)

- **Wish-list #2 — SpiderData (canonical, non-legacy) → orm_inspect allowlist** (~15 min)
- **Wish-list #3 — Opportunity → orm_inspect allowlist** (~15 min)
- **Category B cosmetic migrations** — ~8-10 already-guarded sites for consistency-only; would touch `td_handlers_content.py`, `tasks_content.py`, `views_spider_data.py`, `views_spider_dashboard.py`, `marketplace_discovery_service.py`, `platform_intelligence_briefing.py`, `spider_intelligence.py`, `living_project_service.py`, `content_diversity_orchestrator.py`. Rigby F-AGREE'd deferring as cosmetic churn.
- All prior deferred items from S2871 / S2868 / S2867 / etc still carried (see 00-START-NEXT-SESSION.md §Step 2)

## D6 moratorium still in force

No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks. Chris redirected mid-session onto character-os Rigby integration (research question, not scope expansion — no arc opened).

## Twin canonical representations

- **Repo canonical (Claude-authored):** PR #3365 `a54998be4` — 30 files, +308/-46
- **Workspace canonical (Rigby-authored via `deliverable_tool.append`):** Rigby Tool Gap Ledger `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` updated — #22b marked `shipped_in_pr_S2872`
- **Handoff (current file):** `docs/handoffs/SESSION_2872_RAW_DATA_DICT_SWEEP_LEDGER_22B_TELEMETRY.md`
- **A4 Constraints refresh:** `00-START-NEXT-SESSION.md` §A4 Constraints (updated at close)
