# Session 2869 — spider_status_tool.search preview fallback + intelligence_tool.signal_clusters multi-source filter

**Date:** 2026-07-21
**Prior session:** S2868 (deliverable diagnostic misfire fix + spider_status_tool.list pagination)
**Next session:** S2870
**Slate:** Chris-selected 2-item slate (Rigby Tool Gap Ledger #2 + #4, grouped by substrate overlap); shipped as single PR

**Merge commit (main):**
- `cf9dcf572` PR #3359 — S2869 slate (5 files, +345/-5)

**D6 moratorium status:** still in force — pure engineering execution against the Rigby Tool Gap Ledger, zero strategic discovery.

---

## What shipped

### PR #3359 — S2869 slate (Ledger #2 + #4, grouped)

Both entries improve Rigby's data-query surface and share the tool-dispatch handler layer (`td_handlers_ops.py` + `td_handlers_core.py` + `pa_tool_schemas.py`). Bundled per Chris's "if they fit together, group them" directive at S2869 open.

#### Ledger #2 — spider_status_tool.search preview fallback

- **Symptom.** `preview` field in `spider_status_tool.search` results read only `r.embedding_text[:200]`. For huggingface / devto / techcrunch_startups rows where `embedding_text` is empty (verified via S2869 pre-code SIGN sampling), preview returned empty — forcing operators to run a follow-up `detail` action or drop to raw ORM for a keyword check.
- **Fix.** `td_handlers_ops.py:6547-6577` — when `embedding_text` is empty AND `raw_data` is a dict, best-effort extract from `raw_data['items'][0].get('title'|'name'|'id')` (items-shape spiders) then fall back to top-level `raw_data.get('title'|'name')`. Inline in the search handler; NOT a shared helper (per Rigby zoom-out Fold 1 — raw_data extraction is best-effort and should not become a codified contract).
- **Deferred.** `raw_data__icontains` query filter extension deferred per Rigby Q2 F-AGREE — perf footgun on the ~1.14M-row SpiderData table.

Schema (`pa_tool_schemas.py:5166`): `query` param description now notes preview fallback + best-effort caveat.

#### Ledger #4 — intelligence_tool.signal_clusters multi-source filter

- **Symptom.** `source_spider` filter only accepted a single string and used `source_breakdown__has_key`. Multi-spider cluster discovery (e.g., Rigby's 14x AI-adjacent loop across huggingface + hackernews + producthunt + techcrunch + devto + reddit + ...) required N sequential dispatches.
- **Fix.** `td_handlers_core.py:3487-3517` — `source_spider` now accepts string OR list. Single string preserves `has_key` behavior; list uses `source_breakdown__has_any_keys` union filter. Handler hardening per Rigby Q4 F-AGREE: if middleware stringifies a list (starts with `[`), attempt `json.loads` recovery; filter non-string / empty entries from the list before applying.

Schema (`pa_tool_schemas.py:3993`): `source_spider` param is now `anyOf: [{type:string}, {type:array,items:{type:string}}]`.

### Test coverage

14 pytest cases across 2 classes in `core/tests/test_s2869_search_preview_and_multisource.py`:

- **SpiderStatusSearchPreviewFallbackTests (7 cases):**
  - `p1_embedding_text_still_wins_when_populated`
  - `p2_items_title_fallback_when_embed_empty`
  - `p3_items_id_fallback_when_no_title`
  - `p4_top_level_title_fallback_when_no_items`
  - `p5_empty_when_no_extractable_text`
  - `p6_list_raw_data_does_not_crash_returns_empty`
  - `p7_preview_truncated_to_200_chars`
- **SignalClustersMultiSourceFilterTests (7 cases):**
  - `m1_string_source_spider_preserves_has_key_behavior`
  - `m2_list_source_spider_unions_via_has_any_keys`
  - `m3_list_source_spider_dedupes_via_orm`
  - `m4_json_stringified_list_from_middleware_coerced`
  - `m5_empty_list_falls_through_to_no_filter`
  - `m6_list_with_non_string_items_filtered_out`
  - `m7_list_with_only_invalid_items_falls_through`

All 14 pass locally. `check_pa_tool_drift` shows pre-existing drift on both tools but zero new drift from S2869 changes.

### Live E2E verification (S2869 post-code SIGN via Rigby)

**#2 verified across 3 spiders (previews now non-empty):**
- huggingface: `sentence-transformers/all-MiniLM-L6-v2`, `Text Generation Models`, `sentence-transformers/all-MiniLM-L6-v2`
- devto: `I've Spent 10+ Years in Software Engineering...`, `Top 7 Featured DEV Posts of the Week`, `AI And Code Ownership...`
- techcrunch_startups: `Bluecore Energy raises $10M...`, `Colossal Biosciences reportedly in talks...`, `Inference startup Infinity raises $15M...`

**#4 verified via Rigby's own live dispatches (Call A + Call B):**
- Call A (`source_spider='hackernews'`, single string): count=5 (non-zero, filter works)
- Call B (`source_spider=['hackernews','huggingface']`, list form): count=10 unique, superset of Call A → has_any_keys union + ORM-dedupe both confirmed

---

## Working loop observations at S2869

- **`feedback_verify_rigby_tool_runs_before_trusting_sign` fired twice:**
  - Turn 1 pre-code: Rigby dispatched `spider_status_tool.search` + `spider_status_tool.detail` on 4 spiders to ground Q1 (raw_data shape stability). Tool_runs non-empty, evidence-driven SIGN.
  - Turn 3 post-code: Rigby initially returned F-BLOCKING on #4 due to count=0 in her live dispatch. Independent verification via `python manage.py shell` direct handler dispatch showed count=5 + correct list union — root cause was GPT-5.2 auto-injecting `pattern_type='demand_spike'` default that filtered to zero. Rigby's F-BLOCKING was overcautious rubber-stamp behavior on my acceptance criterion (I asked her to match specific IDs from my shell test, but her dispatch had one extra filter). Recovered via clarification turn; Rigby F-AGREE'd on the actual correctness signals in her own data.

- **`feedback_zoom_out_ask_per_rigby_sign` yielded 3 fold candidates:**
  - Fold 1: preview fallback should be best-effort, not schema (applied — kept extraction inline, not a shared helper)
  - Fold 2: raw_data icontains perf footgun (applied — deferred to future ledger)
  - Fold 3: list-input coercion risk from middleware (applied — added json.loads recovery in handler)

- **Two new ledger candidates surfaced mid-cycle:**
  - **#20** — signal_clusters filter defaults auto-injected by dispatch layer. Pattern_type schema is enum-only (no null path); GPT-5.2 rubber-stamps `pattern_type='demand_spike'` + `min_confidence=0.6` + `window_hours=168` when omitted. Over-filters to zero. Blocked Rigby's initial #4 verification.
  - **#21** — `spider_data_bridge.py:93` crashes on list-form `raw_data` (`AttributeError: 'list' object has no attribute 'get'`). Surfaced by S2869 test fixture 6. Learning bridge silently fails for that row. Cheap ~5-line guard fix.
  - Both logged as ledger open entries by Rigby (see below).

- **`feedback_claude_stdout_truncation_vs_ui_truncation` hit once** — pre-code SIGN response truncated in my terminal above the tool_runs separator; recovered via targeted re-request filtered with `sed '/--- Tool Runs (verbose) ---/,$d'`.

- **Rigby memory limit reached:** Rigby's `remember_tool` reported current_count=1240, max_items=200 when trying to log the new ledger candidates as memory. Rerouted to workspace deliverable update (per `feedback_rigby_writes_workspace_deliverables`). Memory pruning is a separate hygiene item.

- **No candidate lessons for Playbook amendment this session.**

---

## Rigby Tool Gap Ledger updates (via Rigby PA per `feedback_rigby_writes_workspace_deliverables`)

- **Deliverable ID:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
- **Entry #2** → `shipped_in_pr_3359` with resolution section
- **Entry #4** → `shipped_in_pr_3359` with resolution section
- **NEW #20** — signal_clusters dispatch auto-injected defaults (open, medium priority)
- **NEW #21** — spider_data_bridge list-form raw_data crash (open, low priority)
- Ledger content: 11,473 → 13,630 chars

## S2869 close ratification envelope (via Rigby per `feedback_twin_deliverable_at_every_ratification`)

- **Deliverable ID:** `a45d108a-c4ce-45b3-a66c-b284509cf94a`
- **Title:** `RATIFICATION_20260721_S2869_LEDGER_2_AND_4_SHIPPED`
- **Workspace:** Donkey Betz (`b4503364-2573-4401-9e28-61a739e0ce50`)
- **deliverable_type / category:** `ratification_record` / `governance`
- **Status:** `ready`

---

## Runtime impact

- `spider_status_tool.search` preview field now non-empty for items-shape and top-level-title raw_data spiders (huggingface / devto / techcrunch_startups / hackernews confirmed via S2869 SIGN sampling).
- `intelligence_tool.signal_clusters` `source_spider` param accepts string OR list; list callers get union filter in one call.
- PA tool schemas: `spider_status_tool.query` description + `intelligence_tool.source_spider` param shape updated. No new drift from `check_pa_tool_drift`.

---

## Session pin state

- **S2869 open pin:** `pa-c75328a89aef48c8` (labeled `s2869-spider-search-preview-and-signal-clusters-multisource`) — minted at S2869 open, committed at S2869 open via PR #3359 (wrapper included in code PR bundle).
- **S2869 close pin:** to be minted at session_lifecycle close for next session (S2870).

---

## Not shipped at S2869 close (deferred to S2870 or later)

- **Ledger #5** — schema/handler drift detection CI wiring (command exists at `core/management/commands/check_pa_tool_drift.py`, S2846-authored, 403 lines; not currently in CI as enforcement — worth investigating whether landing = wiring to `.github/workflows/` or expanding coverage).
- **Ledger #16** — close-ceremony twin-mirror enforcement gap (S2863 ledger item).
- **NEW #20** — signal_clusters dispatch auto-inject fix (schema nullability + middleware defaults).
- **NEW #21** — spider_data_bridge list-form raw_data guard.
- All prior S2867/S2866/S2862/S2861 folds still carried forward.
