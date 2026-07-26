# SESSION 2977 — SEC form_type interleave + rebuild_embedding_text

**HEAD at close:** `8de4c0fac` (PR #3608 merged; docs cascade PR TBD)

**Branch shape:**
- `feat/s2977-sec-form-type-interleave` → main (merged, branch deleted)

**Deliverables:**
- S2977 spec: `4e4534db-0e30-48b9-8cc5-e4a5e182aa54` — Engineering Spec (S2977) — Rigby-drafted per Chris ratification, **fourth walk** of the Rigby-drafted-spec origination variant. Status flipped to `completed` at close.

**Support conversation:** `pa-5ad154766ca64d2d` (fresh S2977 pin, Chris-minted)

---

## Three-part summary (Chris-facing)

**What was done.** Eighth walk of the reframe pattern. Chris handed spec `4e4534db` deferring TheOdds and asking to verify SEC + Top News + Investing embedding + searchability. Sampled sec_edgar + 6 news + 4 investing spiders via Django ORM BEFORE writing any code. Found News/Investing are already healthy (real user-facing keyword hits: yahoo_finance 'stock'=191, financial 'earnings'=52, reuters 'election'=2, bbc 'election'=4, google_news 'election'=13). Found ONE real extractor mismatch in SEC: raw_data holds 384 8-Ks + 94 10-Qs + 25 10-Ks in 7d, but `LegacySpiderData.get_searchable_text` caps `items[:20]` and 8-Ks (filed ~20× more frequently) dominate the top slice — so 10-K/10-Q never make it into `embedding_text` and searches for those form types return zero real hits. Shipped Path B fix (Chris-ratified): spider-side round-robin interleave in `sec_spider.py` + new bounded `rebuild_embedding_text` command that re-extracts `embedding_text` for existing rows using the interleave logic (without touching the stored embedding vector, since no real search path uses it). Merged as PR #3608 with `--admin` per billing gate; workers recycled per PLAYBOOK-7.4.4; live-verified.

**How it improves the platform.** Before: SEC keyword search for "10-K" returned 3 hits (all boilerplate mentions), "10-Q" returned 1. After: **"10-K" returns 13 real filings, "10-Q" returns 23 real filings**, "8-K" unchanged at 54 (no regression). Users searching for annual/quarterly filings now find the actual documents. The `rebuild_embedding_text` command is generic — future extractor / spider fixes can use it to refresh existing-row searchability without a full re-embed.

**Next session first action.** Wait for Chris. Follow-up seeds queued: (a) **sec_spider Form 4 / S-1 / 13F-HR fetch** — spider's FILING_TYPES advertises 6 types but fetch loop covers 3; small (~10 line) mini-PR; (b) **rebuild_embedding_text --dump-old-jsonl** — Rigby A2 F-BLOCKER mitigation for pre-apply snapshot (belt-and-suspenders since rollback is already deterministic given raw_data immutability); (c) **theodds auth-failure fix** — still open from S2972–S2975, needs THE_ODDS_API_KEY rotation; (d) **remoteok pre-dedup filter** — still open from S2975. Reframe fold trigger count = **8** (S2969→S2977).

---

## Findings from sampling

### News + Investing = healthy
Feed Explorer keyword hits (7d, `embedding_status='present'`, HEAD `058ef69b0`):

| Spider | Query | Hits |
|---|---|---|
| yahoo_finance | 'stock' | 191 |
| yahoo_finance | 'earnings' | 27 |
| financial | 'stock' | 199 |
| financial | 'earnings' | 52 |
| financial | 'Fed rate' | 2 |
| reuters_rss | 'earnings' | 2 |
| reuters_rss | 'inflation' | 1 |
| reuters_rss | 'election' | 2 |
| bbc | 'election' | 4 |
| bbc | 'earnings' | 1 |
| google_news | 'election' | 13 |
| google_news | 'earnings' | 1 |
| polygon_finance | 'earnings' | 8 |
| polygon_finance | 'stock' | 57 |

No dominant failure mode. All 78 sampled NO_ITEMS rows across 11 spiders classify as Class 2 (success_empty polls). Zero extractor mismatch, zero hidden sentinels, zero error envelopes.

### SEC = extractor mismatch (root cause)
- 7d raw_data across 24 embedded sec_edgar rows: **384 items marked `form_type='8-K'`, 94 as `10-Q`, 25 as `10-K`**.
- Pre-fix `embedding_text` scan across those 24 rows: '8-K' contained in 23 rows, '10-K' in **0 rows**, '10-Q' in **1 row**, 'Form 4' in **0 rows**.
- Root cause verified with `top20_ft` vs `full_ft` audit: 5-of-6 sampled rows had **20-of-20 top slots occupied by 8-Ks** — the extractor's `items[:20]` cap drops every 10-K/10-Q. The only outlier was a 16-item row where 3 10-Qs made it into top-20 but were still lost to the joined-text 4000-char cap.
- Additional discovery: `ai_core/spiders/specialized/sec_spider.py` FILING_TYPES advertises 6 types (8-K, 10-K, 10-Q, 4, S-1, 13F-HR) but fetch loop on line 60 covers only 3 (8-K, 10-K, 10-Q). Form 4 / S-1 / 13F-HR are never fetched.

---

## Shipped changes (PR #3608, merge SHA `8de4c0fac`)

### 1. `ai_core/spiders/specialized/sec_spider.py` — form_type interleave

Replaced global `sort by filed_at desc` (line 87) with round-robin interleave via new static method `_interleave_by_form_type`. Preserves per-type filed_at desc ordering. Single-type input degrades to unchanged sorted list. Missing/empty `filed_at` retains the prior string-sort fallback — no new datetime parsing introduced (Rigby T1 guardrail).

### 2. `core/management/commands/rebuild_embedding_text.py` — new bounded command (184 lines)

Re-extracts `embedding_text` for existing rows using the current `get_searchable_text` output without touching the stored embedding vector. For sec_edgar, re-interleaves `raw_data['items']` before extracting so pre-fix rows gain form_type diversity in-place (otherwise Path B would be a no-op for existing rows since raw_data ordering is unchanged). Truncates to 1000 chars to match backfill (`generate_entry_embedding`) semantics — future re-embed cycles don't churn. Skips sentinel rows (owned by `retriage_no_items` / `cleanup_stale_no_items`). Skips rows where new extractor returns empty (would look like data loss).

Dry-run default; `--spider` required; `--days 7` default; `--limit` + `--apply` supported.

### 3. `core/tests/test_signals_ui_api.py` — 15 new tests

- **SECSpiderInterleaveTests (5)**: mixed-types-land-in-top-20 / single-type-degrades / per-type-order-preserved / missing-filed_at-string-fallback / empty-input-returns-empty.
- **RebuildEmbeddingTextCommandTests (10)**: dry-run-no-write / apply-updates / vectors-untouched / sec-prefix-row-gets-diversity (verifies the re-interleave in-command works on pre-fix raw_data) / skips-sentinels / skips-empty-extractor-output / days-window-scope / spider-scope / limit-caps-scan / (implicit) apply-writes-truncated-1000ch.

Full suite: **79/79 pass** (`USE_PGBOUNCER=0 python manage.py test core.tests.test_signals_ui_api --keepdb`).

---

## Live-verify (post-apply)

Command executed against prod DB (HEAD `8de4c0fac`):
```bash
$ python manage.py rebuild_embedding_text --spider sec_edgar --apply
=== rebuild_embedding_text spider=sec_edgar window=7d mode=APPLY ===
  scanned:       24
  unchanged:     5  (new text == old text)
  would update:  19  (new text differs and is non-empty)
  would empty:   0  (new extractor returns nothing — SKIPPED)
  updated: 19
```

Feed Explorer keyword hits (post-apply):

| Query | Before | After | Delta |
|---|---|---|---|
| `10-K` | 3 (boilerplate) | **13** | +10 real filings |
| `10-Q` | 1 | **23** | +22 real filings |
| `8-K` | 54 | 54 | unchanged — no regression |
| `Form 4` | 1 (boilerplate) | 1 | spider doesn't fetch — follow-up seed |
| `Annual Report` | 1 | 1 | label-not-content in curated fallback |
| `Quarterly Report` | 1 | 1 | same |

---

## SIGN cycle log

### T1 (pre-implementation, Rigby tool-grounded via repo_tool — 8 real tool calls)
- **Correctness: AGREE** + 2 guardrails (single-type fallback, string filed_at fallback baked into implementation)
- **Safety: AGREE** + 1 watch: `core/tasks_financial.py:1029` uses `items[:5]` on sec_edgar — will see different mix post-fix (acceptable per Rigby, no invariant break)
- **Retriage/backfill: F-BLOCKER** — must lock policy. Two paths surfaced:
  - Path A (fix + wait) vs Path B (fix + one-shot re-extract)
  - **Chris ratified Path B** via plain-english decision framing
- **Zoom-out: AGREE** + 2 folds (recorded):
  - **Fold A (T1)** — ordering-as-proxy-for-representation debt: per-spider ordering hacks may become a pattern; future trigger if another spider hits the same dominant-subtype issue
  - **Fold B (T1)** — non-deterministic per-item `timestamp=datetime.now()` in sec_spider hinders dedup

### A2 (post-ship, Rigby tool-grounded via repo_tool — 10 real tool calls)
- **Metric integrity: AGREE** (reclassification not concealment; length semantics preserved)
- **Grep spot-check: AGREE** — verified 13 `embedding_text__icontains` consumers across content/agents/services; only `tasks_financial.py:1029` has sec_edgar branching (already flagged in T1)
- **Reversibility: F-BLOCKER** — no pre-apply snapshot for 19 updated rows. **Assessed as paper-only**: rollback path IS deterministic (raw_data is immutable; reverting extractor code + re-running command reproduces old text). **Follow-up seed logged**: add `--dump-old-jsonl <path>` snapshot flag for belt-and-suspenders.
- **Zoom-out: AGREE** + 2 folds (recorded):
  - **Fold C (A2)** — vector/text divergence debt: `rebuild_embedding_text` refreshes keyword-search surface only; vectors may remain out of sync until a true re-embed exists
  - **Fold D (A2)** — SEC payload non-determinism corroborated (matches T1 Fold B)

Rigby tool_runs across T1 + A2: **18 substantive repo_tool searches + reads**. Not rubber-stamp.

---

## Follow-up seeds (Chris picks whether to open)

1. **sec_spider Form 4 / S-1 / 13F-HR fetch loop expansion** — small mini-PR (~10 line change in fetch_data loop) + tests + retriage post-merge.
2. **rebuild_embedding_text --dump-old-jsonl** (Rigby A2 F-BLOCKER mitigation) — persists old→new pairs as JSONL before writing. ~30 min follow-up.
3. **Per-item `timestamp=datetime.now()` cleanup in sec_spider** — replace with filing-time-based or omit; hinders dedup auditability. Separate cleanup arc.
4. **`SECSpider.name='sec'` vs registry key `'sec_edgar'` mismatch** — latent risk; not a bug at HEAD.
5. **Extractor-coupling debt (Rigby T1 Fold A)** — if a second spider hits the same dominant-subtype-crowds-out-minority issue, promote to a generic extractor-side solution.
6. **theodds auth-failure fix** (STILL OPEN from S2972–S2975) — Chris rotation required.
7. **remoteok pre-dedup filter** (STILL OPEN from S2975) — spider stores API legal preamble as unique item.
8. **Deliverable-as-spec fold @ trigger 8** — reframe pattern now walked 8 times (S2969→S2977) across 4 Rigby-drafted variants (S2973 + S2974 + S2975 + S2977). Playbook rule candidate ready when Chris says so.

---

## Session cost this session

- ~4 PA dispatches (fetch-spec / T1 SIGN / A2 SIGN / A2-verdict-repeat / deliverable-update)
- 1 code PR shipped (planned via SIGN; no revision cycles)
- No v2 subprocess dispatches
- Live-verify inline (didn't wait for beat schedule)
- Rigby tool_runs 18 substantive across T1 + A2 (well above rubber-stamp signal threshold)

Comparable to S2975 (also ~4-6 dispatches / 1-3 PRs). Sampling-before-code kept the SIGN cycles compact.
