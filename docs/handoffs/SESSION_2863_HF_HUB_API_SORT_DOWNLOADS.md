# Session 2863 — HuggingFace Hub API sort=downloads (Rigby Tool Gap Ledger #13)

**Date:** 2026-07-21
**HEAD at close:** `90c293aee` (code merge) + docs cascade merge
**PR:** [#3345](https://github.com/clwest/donkey-betz-platform/pull/3345)
**Prior session:** [SESSION_2862](SESSION_2862_HUGGINGFACE_SIGNAL_EXTRACTION_FIX.md)
**Session pin retired at close:** `pa-687d4e1e220f4f11` (labeled `s2863-hf-api-sort`)

---

## TL;DR

Shipped the Chris-selected S2863 slate #1 (Rigby Tool Gap Ledger #13, Rigby-recommended at S2862 close) as **one PR / one commit**. Swaps `sort=trending` → `sort=downloads` at all 3 HuggingFaceSpider Hub API sites so the spider actually reaches the live API instead of falling back to `_get_curated_topics()`.

**Fix shape:** 3-site config swap in a single file (`ai_core/spiders/specialized/huggingface_spider.py`), 26 lines net. No migration. No new normalization. Compositional follow-on to S2862 (which restored the routing to the class-based path); this session restores the actual API call.

- **Config swap** — `sort: 'trending'` → `sort: 'downloads'` at lines :87 (models), :144 (datasets), :200 (spaces). Each site gets a 2-line comment referencing this ledger entry + live-verified date.
- **`_fetch_spaces` docstring extended** — `/api/spaces` items don't populate `downloads` (returned as None), but the server still accepts `sort=downloads` with HTTP 200 and yields a deterministic ordering. Item payloads stay well-formed because `_fetch_spaces` builds descriptions from `sdk` + `likes`, not `downloads`.
- **7 pytest cases** across 3 test classes (`test_s2863_huggingface_sort_downloads.py`):
  - `SortParamRegressionTests` (3): mock `cached_get`; assert each `_fetch_*` passes `sort=downloads` with `direction: -1`.
  - `SourceCodeGuardTests` (1): regex-grep the spider source; assert no `sort: 'trending'` assignment remains.
  - `LiveHubAPIContractTests` (3): real HF Hub API probe for /models, /datasets, /spaces; skips if unreachable.
  - **7/7 pass in 0.396s** (including live network tests).
- **Rigby SIGN loop:** pre-code 1-turn (Q1 F-BLOCKING delegated to Claude live-curl per PA tool-surface limit — this itself became Ledger #15; Q2-Q5 AGREE-TO-BUILD grounded via `repo_tool`); post-code 1-turn (AGREE-TO-SHIP on all 5 F-BLOCKING Qs, grounded via `repo_tool.read_file` on both changed files + downstream ordering search — 0 coupling found).

**Post-recycle E2E (live HF Hub API, `max_results=20`):**
- **20/20 items** (10 models + 5 datasets + 5 spaces), all with populated `title` + `description`.
- **2827 chars** total extractable text (vs 588 from curated fallback at S2862 close; 0 pre-S2862 URL-collector path).
- Top model: `sentence-transformers/all-MiniLM-L6-v2` · 241M downloads.

---

## Why this slate

Chris-selected the Rigby-recommended slate #1 from the S2862 close: Ledger #13 (HuggingFaceSpider API params obsolete). Continuous with S2862's arc: get HF live data to actually flow instead of the curated-fallback path.

Per `feedback_engineering_bias_over_audit` — this was a net-new engineering fix (spider producing live data at expected volume), not an audit of existing infrastructure.

## Working-loop notes

- **Q1 F-BLOCKING routed to Claude:** Rigby's `intelligence_tool.search` + `web_search` both return `method: "synthetic_fallback"` — she cannot pre-verify HTTP status codes against real endpoints via her tool surface. Rigby honestly flagged the limit and recommended Claude execute the live probe. **This limit is now Ledger #15** (open) — a real PA-surface capability gap distinct from all prior entries.
- **Zoom-out per `feedback_zoom_out_ask_per_rigby_sign`:** both pre-code and post-code SIGN cycles included Q5 zoom-out. Post-code Q5(b) surfaced the Ledger #14 candidate (view-layer HF workaround cleanup). Rigby recommended NOT bundling it into this PR — kept scope-clean, easier reversibility, safer as follow-on after observing prod runs.
- **Live-network test pattern:** `LiveHubAPIContractTests.setUpClass` probes once with a 10s timeout; on failure, entire class skips cleanly. Keeps CI green when offline; validates contract when online.

## What shipped

**Code PR (`90c293aee`):**
- `ai_core/spiders/specialized/huggingface_spider.py` — 3 sort-param swaps, comment updates, `_fetch_spaces` docstring extended.
- `core/tests/test_s2863_huggingface_sort_downloads.py` — 7 pytest cases (created).

**Workspace mirror (via Rigby PA tool per `feedback_rigby_writes_workspace_deliverables`):**
- Rigby Tool Gap Ledger (`5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`) updated:
  - Entry #13 → Shipped section, status `shipped_in_pr_3345`, PR/commit/date recorded, E2E numbers embedded.
  - **New open entry #14:** `views_spider_intelligence.py:1217` HF description workaround cleanup (deferred_from_s2863_per_rigby_q5b).
  - **New open entry #15:** PA-surface capability gap — no raw HTTP fetch (open).

**Docs cascade (this handoff + refreshed 00-START + pa_local.sh pin bump):** ships as separate PR post-code merge.

## Not shipped at S2863 close (deferred)

- **Ledger #14** (`views_spider_intelligence.py:1217` HF workaround removal) — deferred per Rigby Q5(b); revisit after prod-run observation.
- **Ledger #15** (raw HTTP fetch capability on PA surface) — deferred; not blocking A1/A4 work, but candidate for a future slate.
- All prior deferred items from S2862/S2861/S2860/S2859/S2858/S2857/S2856 stay deferred (see 00-START-NEXT-SESSION.md).

## Runtime impact

Compositional close of the S2862 arc:

| Metric | Pre-S2862 (URL-collector path) | Post-S2862, Pre-S2863 (class path + `sort=trending`) | Post-S2863 (class path + `sort=downloads`) |
|---|---|---|---|
| Items returned by HF spider run | ~10 (via `normalize_item`, no title/desc) | 10 (curated fallback — API 400) | **20 live items** |
| Items with populated title+description | 0/10 | 10/10 (curated) | **20/20 (live)** |
| Extractable text chars | 0 | 588 | **2827** |
| SignalCluster contribution | dropped | curated-only | live-data-backed |
| A4 `intelligence_tool.signal_clusters source_spider='huggingface'` | empty | curated only | **live AI/ML signals** |

A4 capability list from 00-START `A4 Constraints §3(r)` now fully live: HF AI/ML signals enter SignalCluster from real Hub data.

---

## Handoff-callout forward-carry (per Rigby Q5(c))

- **Live network tests are flaky by nature:** the `probe + SkipTest` pattern in `LiveHubAPIContractTests.setUpClass` is load-bearing. Reuse it when adding real-API tests to other spiders; don't inline network calls in individual `test_*` methods.
- **HF Hub API contract as of 2026-07-21:** `sort=trending` returns HTTP 400 (all 3 endpoints); `sort=downloads` is the currently-supported ordering. This is embedded in the comments at each fix site + the test file header. If HF flips again, both the comments and the guard test will surface the change.
- **Curated-fallback triggers on `len(all_items) == 0`:** any future "0 HF items in cluster" incident should first check `curl 'https://huggingface.co/api/models?sort=downloads&direction=-1&limit=1'` before assuming spider logic broke. The fallback masks API-shape regressions silently.
- **Bimodal collector architecture (S2862 Q5.a fold) still open:** URL-path via `SPIDER_TARGET_URLS` + `collect_spider_data_sync` vs class-path via `registry.get_spider_class` + `_run_spider_adapter`. When both exist, URL path silently wins. Only 2/54 URL-path spiders currently drop (huggingface removed at S2862; openmeteo still open). Not urgent, `future_trigger` per Rigby.

## Rigby-Ledger-refresh consequence

- **Open:** 7 entries (#1, #2, #4, #5, #7, #14, #15).
- **Shipped:** 2 entries (#3, #13).
- **Delta this session:** −1 open (#13 → shipped), +2 open (#14 view-layer cleanup, #15 PA raw-HTTP-fetch gap).

## S2864 open sequence (draft — see 00-START-NEXT-SESSION.md for full)

1. Session-open atomic mint (retire `pa-687d4e1e220f4f11`).
2. List net-new engineering candidates per `feedback_engineering_bias_over_audit`. Rigby-recommended slate lead: Ledger #14 (view-layer HF workaround removal) — small, safe, closes the S2862+S2863 arc completely.
3. D6 moratorium still in force.

---

## References

- **S2863 PR:** [#3345](https://github.com/clwest/donkey-betz-platform/pull/3345) — code fix (`90c293aee`)
- **S2863 docs cascade PR:** filled at merge — this handoff + 00-START refresh + pa_local.sh pin bump
- **S2862 handoff (prior):** `docs/handoffs/SESSION_2862_HUGGINGFACE_SIGNAL_EXTRACTION_FIX.md`
- **Rigby Tool Gap Ledger:** deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` in workspace `b4503364-2573-4401-9e28-61a739e0ce50` (Donkey Betz)
- **Constitutional governance:** Playbook v0.8.0 (`docs/ENGINEERING_PLAYBOOK.md`, tag `playbook-v0.8.0`, 205 rules)
- **A4 warm-up constraints:** current `00-START-NEXT-SESSION.md` §A4 Constraints
