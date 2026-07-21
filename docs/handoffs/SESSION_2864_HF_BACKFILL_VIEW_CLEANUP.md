# Session 2864 — HF backfill + view-layer workaround removal (Rigby Tool Gap Ledger #14)

**Date:** 2026-07-21
**Session pin:** `pa-f78ff19b2ce0496c` (labeled `s2864-hf-view-cleanup`)
**Retires at close:** yes → S2865 opens with fresh mint
**PR:** #3347 (`5cb39c4af`)
**Fold classification:** S2864 arc = **arc_close_ok** (Ledger #14 closed with real closure)

---

## What shipped

Backfill migration + view-layer workaround removal, together closing Rigby Tool Gap Ledger #14 (originally logged at S2863 close as "safe no-op cleanup candidate," reclassified mid-session to "confirmed load-bearing → root-cause fix via historical-row enrichment").

### Files (PR #3347)
1. **`core/management/commands/backfill_huggingface_items.py`** (new, ~165 lines) — enrich pre-S2862 `LegacySpiderData` HuggingFace items in-place with `title`/`url`/`description` in the same pipe format the view was reconstructing at read time. Item-level guard skips post-S2862 class-path items + already-backfilled rows. Batched commits (default 100), `--dry-run` + `--limit N` supported.
2. **`core/tests/test_s2864_huggingface_backfill.py`** (new, 167 lines) — 11 pytest cases across 2 classes:
   - `ItemEnrichmentTests` (7) — `enrich_item()` correctness for pre-S2862, post-S2862, no-id, spaces URL, id-fallback, idempotent, empty-metadata edge cases.
   - `CommandIntegrationTests` (4) — command persistence, dry-run, idempotent second run, mixed rows.
3. **`core/views_spider_intelligence.py`** (22-line deletion) — remove HF description block (was 1217-1233) + HF URL block (was 1239-1241). GitHub URL block preserved (out of scope).

### Local execution
- **Backfill dry-run:** rows_scanned=562, rows_updated=23, items_enriched=460, items_skipped_has_title=59, items_skipped_no_id=0.
- **Backfill real run:** identical counts. Idempotent (second run would enrich 0).
- **Post-run ORM verify:** 519/519 items (100%) have title+description populated across all HF rows-with-items.
- **Tests:** `pytest core/tests/test_s2864_huggingface_backfill.py -v` → **11/11 passed in 193s**.
- **E2E:** `curl /api/spider-intelligence/feed/?source=huggingface&limit=10` → **10/10 items** with populated title+url+description post-cleanup.

---

## Discovery arc (why this session went through 2 pivots)

**Pivot 1 (safe no-op → F-BLOCKING revert):**
- Original plan (per S2863 close): remove `views_spider_intelligence.py:1217-1233` HF description block + 1239-1241 HF URL block as "safe no-op on live-item happy path."
- Pre-code SIGN Q1-Q4 AGREE-TO-BUILD (Rigby verified spider CLASS code populates description).
- Coded. E2E on 5 items looked fine.
- Post-code SIGN Q4 **F-DELEGATED-TO-CLAUDE** (Rigby: "I can't ORM-verify historical rows"). Claude ran the delegated ORM sweep: **115/120 sampled items had empty description**, including today's URL-scraper-path row `d628f03c-0d92-496a-b43a-26d188483e7b` (`sentence-transformers/all-MiniLM-L6-v2`, `sort=downloads&limit=20`).
- Reverted. Workaround was NOT dead code — it was load-bearing for pre-S2862 historical rows.

**Pivot 2 (normalize_item HF branch → discovered dead-code destination):**
- Rigby+Claude joint-agreed (per `feedback_claude_rigby_agree_first_chris_yes_no`) to add HF-specific normalization to `real_data_collector.py:normalize_item`.
- Started design. Traced `SPIDER_TARGET_URLS` — `huggingface` NOT present. Confirmed via `git log`: **S2862 (commit `fbfe10ff7`, merged today 09:28 CST) already removed `huggingface` from `SPIDER_TARGET_URLS`**.
- **New HF ingestion no longer routes through `normalize_item`.** It routes through `HuggingFaceSpider.fetch_data` (class path) which already builds rich items.
- ORM verified: 2 HF rows created AFTER S2862 merge (14:29 UTC + 15:31 UTC) both have `title`/`url`/`description` populated on every item.
- **normalize_item HF branch would be dead code** — no runtime effect. Aborted design.

**Pivot 3 (backfill migration = actual closure):**
- Presented to Chris: (a) backfill / (b) abort / (c) different slate.
- Chris D-verdict: **(a) backfill**.
- Design → SIGN → code → tests → local run → E2E → view-cleanup → SIGN → merge.

---

## Working loop observations at S2864

### Rigby Q4 F-DELEGATED-TO-CLAUDE caught the F-BLOCKING

Rigby's post-code SIGN Q4 in pivot #1 correctly flagged "I can't ORM-verify historical rows; Claude should run this specific query." Claude ran it. The result reversed the pre-code SIGN's `AGREE-TO-BUILD` verdict on Q1 (which had been grounded on spider CLASS code — the right code, wrong data source). This is exactly what `feedback_verify_rigby_tool_runs_before_trusting_sign` + Rigby Tool Gap Ledger #15 (PA tool-surface lacks raw HTTP/DB inspection) exist to catch — and the working loop did catch it, at the cost of one revert cycle.

### Pre-code SIGN blind spot: "does field X populate?" needs BOTH code-path AND data-source verification

**Lesson to codify (Rigby Q5 candidate):** *"When a proposed code deletion depends on 'field X is populated,' pre-code SIGN MUST verify field population at the ACTUAL persisted/served source of truth (ORM), not just at the code path that COULD populate it."*

- Pivot 1's pre-code Q1 verified: "spider class code sets `description` at lines 105-118." Correct.
- Pivot 1's pre-code Q1 did NOT verify: "does the persisted DB reflect that today?" — because pre-S2862 rows didn't come through that code path.
- Rigby's Q4 delegation to Claude at POST-code caught the miss.
- Better: at pre-code SIGN, F-DELEGATE the ORM sweep BEFORE coding.

Watch for 2nd/3rd trigger before codifying as PLAYBOOK amendment.

### S2862 Q5.a bimodal-collector fold: 2nd independent trigger

- **1st trigger (S2862):** URL-path `parse_json_api` + `normalize_item` silently won over class-path `_run_spider_adapter` when HF was in `SPIDER_TARGET_URLS`. Ingested items lacked `title`/`description`/`url`, causing `SignalAggregationService._extract_text_from_spider_data` to yield 0 chars and drop all clusters.
- **2nd trigger (S2864):** Pre-S2862 URL-path items persisted in DB lack same fields; view-layer workaround was reconstructing at read time. Rigby recommends **promoting to spec_backlog/initiative**: *"collector paths must converge on a single normalized schema; no view-layer spider special casing."*
- Not yet a PLAYBOOK amendment (per `future_trigger` at S2862 Q5 → 2nd trigger = promote to tracked backlog per Rigby Q4 at post-code SIGN).

### Format drift risk (acknowledged as historical-compat layer)

Backfilled pre-S2862 items use pipe format: `"Task: X | Library: Y | Tags: a, b, c | N downloads | N likes"`. Post-S2862 class-path items use narrative: `"AI model for {pipeline_tag}. Downloads: N. Likes: N."`. Two formats coexist in the DB indefinitely. Not a bug — historical compatibility. If unified format becomes needed, remedy is a re-normalization pass, NOT reintroducing view-layer hacks.

---

## Rigby Tool Gap Ledger updates

- **#14 (HF view-layer workaround cleanup)** — moved to **Shipped**, status `shipped_in_pr_3347`. Original assumption ("safe no-op") corrected via post-code Q4 F-DELEGATED ORM check. Root-cause fix landed via backfill (`backfill_huggingface_items` management command + view-cleanup).
- **#15 (PA raw HTTP fetch tool)** — remains open. Rigby's inability to raw-HTTP/ORM-inspect is what forced Claude to run the F-DELEGATED ORM check. Also blocked pre-code API-contract verification at S2863 Q1.

Ledger updated by Rigby via PA `deliverable_tool` per `feedback_rigby_writes_workspace_deliverables`.

---

## S2865 next slate — Rigby-recommended lead

Chris to select at open. Candidates (per `feedback_engineering_bias_over_audit`, net-new engineering first):

0. **NEW at S2864 close** — **Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.** Two triggers now observed. Rigby Q5 recommendation. Small doc/deliverable, ~30 min. Sets up next investigation trigger.
1. **Ledger #15 — PA raw HTTP fetch tool** (~1-2 hr). Would let Rigby verify API contracts + inspect DB directly without Claude ORM delegation. Directly reduces future SIGN-cycle friction. Twice bit at S2863 (Q1 delegated) + S2864 (post-code Q4 delegated).
2. **Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate). Watch for 2nd/3rd trigger; not codified this session.
3. Deferred slate from 00-START-NEXT-SESSION §S2864 candidates (items 2-16, unchanged).

**Session pin `pa-f78ff19b2ce0496c` (labeled `s2864-hf-view-cleanup`) RETIRES at S2864 close.** Fresh mint required at S2865 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## Twin pointers (per `feedback_twin_pointer_docs_at_boundaries`)

**Repo:**
- Handoff: `docs/handoffs/SESSION_2864_HF_BACKFILL_VIEW_CLEANUP.md` (this file)
- Backfill command: `core/management/commands/backfill_huggingface_items.py`
- Tests: `core/tests/test_s2864_huggingface_backfill.py`
- View-cleanup: `core/views_spider_intelligence.py` (deleted 22 lines around former 1217-1241)

**Workspace (Rigby-authored via PA tool per `feedback_rigby_writes_workspace_deliverables`):**
- Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`
- Rigby Tool Gap Ledger (deliverable) — entries #14 moved to Shipped, #15 remains open
- S2864 close summary (deliverable) — content mirror of this handoff
- S2864 ratification envelope (deliverable, `deliverable_type='ratification_record'`, `category='governance'`)
