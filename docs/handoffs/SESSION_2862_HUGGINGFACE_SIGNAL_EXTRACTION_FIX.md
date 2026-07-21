# Session 2862 — HuggingFace → SignalCluster Drop Fixed (Rigby Tool Gap Ledger #3)

**Date:** 2026-07-21
**HEAD at close:** `fbfe10ff7`
**PR:** [#3343](https://github.com/clwest/donkey-betz-platform/pull/3343)
**Prior session:** [SESSION_2861](SESSION_2861_AUTOPILOT_SELECTED_FIELDS_SHIPPED.md)
**Session pin retired at close:** `pa-95e7256e4f3d40cd` (labeled `s2862-open`)

---

## TL;DR

Shipped the Chris-selected S2862 slate #1 (Rigby Tool Gap Ledger #3, S2845-open, Rigby-recommended at S2861 close) as **one PR / one commit**. Removes `'huggingface'` from `SPIDER_TARGET_URLS` so `execute_spider_task` falls through to `HuggingFaceSpider.fetch_data()` instead of the generic URL-collector path whose `normalize_item()` couldn't map HF Hub API's `modelId`/`id` fields to `title`/`description`, dropping every huggingface signal before clustering.

**Fix shape:** routing config delete (12-line dict entry → 12-line explanatory comment). No migration. No new normalization logic. Uses existing `HuggingFaceSpider` code that already builds items with `title`/`summary`/`description` populated.

- **Config change** — `ai_core/spiders/real_data_collector.py:104-115` removes the `'huggingface': ['https://huggingface.co/api/models?...']` entry from `SPIDER_TARGET_URLS`, replaces it with a self-documenting comment block naming root cause + fall-through destination + regression test file.
- **6 pytest cases** (`test_s2862_huggingface_signal_extraction.py`) across 3 test classes covering (a) HuggingFaceSpider output shape, (b) pre-fix bug repro + post-fix success text extraction, (c) routing regression (not-in-dict + registry-resolves + spider-exposes-fetch_data). **6/6 pass in 192s.**
- **Rigby SIGN loop:** pre-code 2-turn AGREE-TO-BUILD (Q1-Q3 turn 1, Q4 F-BLOCKING resolved turn 2 after Claude ran ORM sweep + Q5 zoom-out reprompt); post-code 1-turn AGREE-TO-SHIP on all 5 F-BLOCKING Qs.

Post-recycle E2E confirmed: 10/10 items now have title+description+summary, extracted text = 588 chars (pre-fix: 0), 1 SignalCluster candidate with 5 entity_tokens (mistral/llms/llama/stable/generation) — verified even under the current HF API HTTP 400 fallback path.

---

## Why this slate

At S2861 close Rigby flagged huggingface → SignalCluster drop (Ledger #3, S2845-open) as top-of-list for S2862. Rationale: real data loss in A4-critical AI/ML domain; ~half-day fix estimate; concrete measurable outcome (SignalCluster contributions from huggingface source). Chris ratified in the S2862 slate selection.

The suspected root cause at S2861 open ("`is_processed=False` + `embedding_text=''` gate at `signal_aggregation_service.py:262`") turned out to be **wrong**. Claude's grounded ORM sweep at S2862 open showed all 5 comparison spiders (huggingface + hackernews + devto + medium + kaggle) had identical `is_processed=True + embedding_text=''` state — the gate isn't where huggingface drops.

Real root cause is upstream at `ai_core/spiders/real_data_collector.py:507` — `normalize_item()` maps `title` from `[title|name|headline|position|role]` and `description` from `[description|summary|body|content|excerpt|tagline]`. HF Hub API items expose `modelId`/`id`/`pipeline_tag`/`tags`/`downloads`/`likes` — none of those field names. So normalized items land with 0 readable text; `_extract_text_from_spider_data` returns `''`; `_extract_signals` skips the row entirely.

Confirmed platform-wide via ORM sweep of all 54 URL-path spiders: only 2 drop on extraction — `huggingface` (this PR fixes) and `openmeteo` (numeric weather forecast; product decision needed, logged as Rigby Tool Gap Ledger fold-carry).

---

## What shipped

### 1. Routing config change (`ai_core/spiders/real_data_collector.py:100-115`)

Removed:
```python
'huggingface': ['https://huggingface.co/api/models?sort=downloads&direction=-1&limit=20'],
```

Replaced with a self-documenting 12-line comment block:
```python
# S2862: intentionally NOT re-added. HF Hub API items expose
# `modelId`/`id` but no `title`/`name`/`description`, so the shared
# `normalize_item()` field mappings (title <- title|name|headline|
# position|role, description <- description|summary|body|content|
# excerpt|tagline) never populate anything readable, and downstream
# `SignalAggregationService._extract_text_from_spider_data()` gets
# 0-char text, dropping every signal before clustering (22 rows/7d
# -> 0 SignalCluster contributions). Falling through to the else
# branch at core/tasks_spiders.py:158 invokes HuggingFaceSpider.fetch_data()
# (ai_core/spiders/specialized/huggingface_spider.py) which builds
# items with title/summary/description already populated. Regression
# tests: core/tests/test_s2862_huggingface_signal_extraction.py.
```

The `"intentionally NOT re-added"` phrasing was Rigby's Q4 post-code mod — prevents a future session from re-adding the URL entry after seeing "hmm, huggingface is missing here."

### 2. Test envelope (`core/tests/test_s2862_huggingface_signal_extraction.py`, NEW, 247 lines)

3 test classes / 6 test cases — matches Rigby's Q3 mods:

**`HuggingFaceSpiderOutputShapeTests`**
- `test_output_items_have_title_and_description` — patches `cached_get` with canned HF Hub API sample responses for `/models`, `/datasets`, `/spaces`; asserts ≥ half of items have `title` and `description`, ALL have `summary` (mod #1: "at least half" rather than "every item")

**`TextExtractionBeforeAndAfterFixTests`** (mod #2: split into pre-fix + post-fix)
- `test_pre_fix_url_normalized_items_yield_empty_text` — synthetic LegacySpiderData row with URL-path-shape items (id/modelId/tags/likes but no title/summary/description); asserts `_extract_text_from_spider_data` returns `''` (documents the bug)
- `test_post_fix_spider_items_yield_text_and_signal` — synthetic row with HuggingFaceSpider-shape items (title/summary/description populated); asserts text non-empty AND `_extract_signals` returns ≥1 signal

**`RoutingRegressionTests`**
- `test_huggingface_removed_from_spider_target_urls` — bare `assertNotIn`
- `test_huggingface_still_resolves_via_registry` — `SpiderRegistry().get_spider_class('huggingface')` returns `HuggingFaceSpider` (guarantees the else-branch at `tasks_spiders.py:158` has a class to run)
- `test_huggingface_class_exposes_fetch_data` — `HuggingFaceSpider` has `fetch_data` but does NOT have `fetch`/`scrape`/`collect_data` (guarantees `_run_spider_adapter` at `core/tasks.py:1198` dispatches to the correct branch)

**Test result:** 6/6 pass in 192.55s.

---

## Rigby SIGN loop (validated at S2862)

### Pre-code SIGN — 2 turns

**Turn 1** — 5 F-BLOCKING Qs on root cause / fix shape / test plan / blast radius / zoom-out. Rigby's tool_runs: 7 grounded reads (real_data_collector.py :400-620 for parse_json_api + normalize_item; tasks_spiders.py :120-240 for the routing branch; signal_aggregation_service.py :330-480 for extraction; huggingface_spider.py :1-258 for output shape; 3 grep searches for consumer verification).

Verdicts:
- **Q1 (root cause)** — AGREE, confirmed drop is `normalize_item` field-mapping miss, NOT the S2861-open guess of `is_processed`/`embedding_text` gate
- **Q2 (fix shape)** — AGREE-TO-BUILD Option C (remove URL entry). Rejected Option A (`id` mapping → title-clobber foot-gun for other APIs), B (source-specific dispatch layer premature), D (text-fallback would introduce noise/junk clusters)
- **Q3 (test plan)** — AGREE-WITH-MODS: (1) require "at least half have title" not "every item"; (2) split extraction test into pre-fix bug-doc + post-fix success; (3) regression test the routing else-branch
- **Q4 (blast radius)** — **F-BLOCKING** — Rigby had no ORM tool to sweep other spiders; asked Claude to run
- **Q5 (zoom-out)** — truncated in Claude's stdout window (persisted response caps at ~30KB); requires reprompt

**Turn 2** — Claude ran Q4 ORM sweep: 54 URL-path spiders swept, only 2 drop text extraction (huggingface + openmeteo). Routed results + Q5 reprompt to Rigby with clean question envelope. Rigby's turn-2 tool_runs: 5 more grounded reads (real_data_collector.py :80-200 + :400-620, tasks_spiders.py :130-220, signal_aggregation_service.py :360-480, huggingface_spider.py :1-258 full). Verdicts:
- **Q4** — AGREE, ship HF only, openmeteo → fold-carry (numeric data would need separate product decision on weather signals)
- **Q5.a (bimodal architecture)** — `future_trigger` — 2/54 drops isn't enough corroboration for a migration program; principle logged
- **Q5.b (normalize_item ownership)** — `future_trigger` — principle: "when a spider has a class, prefer class-owned transformation"

**Net:** AGREE-TO-BUILD on all 5 Qs after 2 turns.

### Post-code SIGN — 1 turn

5 F-BLOCKING Qs verifying diff matches plan / test envelope matches Q3 mods / blast radius verification / comment-block audit trail quality / any same-PR-mitigatable folds. Rigby's tool_runs: 5 grounded reads on the actual diff (real_data_collector.py :90-170, test_s2862 :1-247, 3 grep searches on `SPIDER_TARGET_URLS` + `'huggingface'` consumers including `views_spider_intelligence.py:1205-1275` inspection of HF special-case description-builder).

Verdicts:
- **Q1** — AGREE (diff clean, openmeteo untouched, comment block points to fall-through)
- **Q2** — AGREE (all 3 Q3 mods applied)
- **Q3** — AGREE (no other test asserts HF membership; `views_spider_intelligence.py:1218` HF special-case works with description present, so no regression)
- **Q4** — AGREE-WITH-MODS (ship-worthy; 2 non-blocking clarity nits: add "intentionally NOT re-added" phrasing + test-file breadcrumb)
- **Q5** — `no_concern` (nothing same-PR-mitigatable outstanding); classified 2 rejected considerations

**Net:** AGREE-TO-SHIP on all 5. Q4 mods applied (12-line comment updated with both).

---

## Post-merge E2E

Ran `_impl_execute_single_spider(spider_name='huggingface')` through the recycled worker state (via `python manage.py shell`):

```
Task result: success=True  item_count=10  data_id=2d588811-373e-494f-8cc0-e0e9bc10c041

New row 2d588811-373e-494f-8cc0-e0e9bc10c041
  raw_data keys: ['items', 'source', 'dedup_stats']
  items count: 10
  items with title: 10/10
  items with description: 10/10
  items with summary: 10/10
  first item keys: ['url', 'link', 'tags', 'title', 'source', 'summary',
                    'category', 'data_type', 'timestamp', 'description']
  first item title: 'Text Generation Models'
  extracted text length: 588 chars
  extracted text preview: 'Text Generation Models LLMs for text generation like
                          Llama, Mistral, GPT...'
  signals produced: 1
  first signal entities: ['mistral', 'llms', 'stable', 'generation', 'llama']
```

**Compare pre-fix** (row from before merge): 20 items, 0 with title, 0 chars extracted text, 0 signals.

### Caveat — HF API returning HTTP 400

During E2E the HuggingFace Hub API calls all returned HTTP 400:
```
WARNING huggingface_spider: Error fetching HuggingFace models: HTTP 400
WARNING huggingface_spider: Error fetching HuggingFace datasets: HTTP 400
WARNING huggingface_spider: Error fetching HuggingFace spaces: HTTP 400
```

Likely cause: `HuggingFaceSpider.fetch_data()` sends `params={'sort': 'trending', 'direction': -1}` (see `ai_core/spiders/specialized/huggingface_spider.py:85-90`). HF Hub API accepts `sort=downloads`/`likes`/`lastModified` — `sort=trending` appears to be deprecated. The spider falls through to `_get_curated_topics()` (line 229-258) which returns 10 curated dicts.

**This is a DIFFERENT bug from S2862**, surfaced at E2E. The routing fix is verified even under this worst-case fallback path — meaning when the fallback fires, signals still reach clustering (verified above); when the HF API is fixed, signals still reach clustering (guaranteed by same fix path).

Logged as **Rigby Tool Gap Ledger new entry #13**: HuggingFaceSpider API params obsolete → HTTP 400 on models/datasets/spaces; fix by moving to `sort=downloads`. Estimated ~30 min. **Slate candidate for S2863.**

---

## Zoom-out folds recorded

### Future_trigger (Rigby Q5 verdicts)

1. **Q5.a — bimodal collector architecture** (URL-path via `collect_spider_data_sync` + `normalize_item` vs spider-class path via `registry.get_spider_class` + `_run_spider_adapter`). Both write `LegacySpiderData` rows with different normalization behavior. When a spider exists in both paths (URL entry + registered class), URL path wins silently — the exact HF failure mode. Only 2/54 URL-path spiders currently drop — not enough corroboration for a broader migration program.
   - Fold text: "Membership-based routing is brittle when a spider exists in both paths; introduce an explicit routing contract (e.g., `handler=url|class`) when a second instance occurs."

2. **Q5.b — normalize_item ownership**. Central `normalize_item()` at `real_data_collector.py:507` is generic best-effort; specialized spiders (like `HuggingFaceSpider`) already own richer transformation. Principle logged.
   - Fold text: "When a spider has a class, prefer class-owned transformation; reserve `normalize_item` for URL-only sources."

### Fold-carry (deferred, not stapled to this PR)

3. **openmeteo drop** — Only other URL-path spider dropping to 0 text. Numeric weather forecast data (`{latitude, longitude, elevation, generationtime_ms}` — no headlines). Fixing routing alone wouldn't help; needs product decision on whether we want weather signals + if yes what synthesis rules. Logged as Rigby Tool Gap Ledger fold-carry.

4. **`views_spider_intelligence.py:1217-1233` HF special-case** — Reconstructs description from `pipeline_tag`+`library_name`+`tags`+`downloads`+`likes` when raw item description is empty. After Option C stabilizes and HF rows land with proper description, this workaround becomes a no-op (guarded by `not description`). Can be removed in a future cleanup pass; NOT blocking, NOT this PR.

### New fold discovered at E2E (Rigby Tool Gap Ledger entry #13)

5. **HuggingFaceSpider API params obsolete** — `sort=trending` on `/api/models`, `/api/datasets`, `/api/spaces` returns HTTP 400. Move to `sort=downloads`. ~30 min fix. Slate candidate for S2863.

---

## S2862 close — what shipped (one PR, one commit + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3343** `fbfe10ff7` — S2862 slate #1: remove huggingface from SPIDER_TARGET_URLS + 6 pytest cases
- **PR `<this docs cascade>`** — S2862 handoff + 00-START-NEXT-SESSION refresh + docs cascade

**Workspace canonical:** Content mirror + ratification envelope written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables` at S2862 close-cascade. Rigby Tool Gap Ledger #3 marked shipped (moved to Shipped entries with status `shipped_in_pr_3343`); new open entry #13 added for HF API param fix.

**Runtime impact:**
- huggingface spider runs now produce `LegacySpiderData` rows with items properly shaped (`title`+`summary`+`description` populated), yielding non-empty extracted text and signals that reach clustering (588 chars → 1 signal in worst-case E2E, expected higher with live HF API).
- A4 AI/ML signal-cluster capability restored — `intelligence_tool.signal_clusters` with `source_spider='huggingface'` should now return non-empty results within ~24h of merge (subject to HF API HTTP 400 fix in S2863).

**Not shipped at S2862 close (deferred to S2863 or later):**
- HuggingFaceSpider `sort=trending` HTTP 400 fix (Ledger #13, ~30 min) — Rigby-recommended next-slate lead
- openmeteo signal fix (product decision needed)
- `views_spider_intelligence.py` HF special-case removal (no-op after Option C stabilizes)
- All prior deferred items from S2861/S2859/S2858/S2857/S2856

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2862)

See:
- **S2862 handoff (current):** `docs/handoffs/SESSION_2862_HUGGINGFACE_SIGNAL_EXTRACTION_FIX.md`
- **S2861 handoff:** `docs/handoffs/SESSION_2861_AUTOPILOT_SELECTED_FIELDS_SHIPPED.md`
- **S2860 handoff:** `docs/handoffs/SESSION_2860_DELIVERABLE_TOOL_DELETE_SHIPPED.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`

For older session history, see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
