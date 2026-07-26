# SESSION 2979 — Theme Signals Evidence-First Card UI (Phase A refinement)

**HEAD at close:** `45e2bc69e` (PR #3613 merged; docs cascade PR TBD)

**Branch shape:**
- `feat/s2979-theme-signals-evidence-first` → main (merged, branch deleted)

**Deliverables:**
- S2979 spec: `c4602ccd-a973-424f-8bc5-dcc16f797430` — S2978 Theme Signals v1 (Phase A) — Evidence-first card UI spec — Rigby-drafted, **sixth walk** of the Rigby-drafted-spec origination variant.
- S2979 decision trail note: `4088978f-d135-4e13-ac7f-008e0cc06f37` — Chris A→B flip captured (pinned, engineering_spec).

**Support conversation:** `pa-08fb0194b6004311` (S2979 pin, Chris-minted at S2978 close)

---

## Three-part summary (Chris-facing)

**What was done.** Fixed the 12% of Theme Signals evidence links that were unclickable (Bluesky `at://` URIs), canonicalized source labels (was mixed `yahoo_finance` + `Yahoo Finance` drift → now unified `Yahoo Finance`), and added top-3-with-`View all N →`-expand + empty-state UX per spec `c4602ccd`. Chris initially ratified spec Option A ("prefer sample_signals"); I flagged (via plain-english decision framing) that sampling showed sample_signals had 34% source/url mismatch rate on real data vs the current spider_data_ids path; Chris flipped to Option B (spider_data_ids primary + sample_signals as fallback for empty-primary cases). PR #3613 merged in single shot. Live-verify: 0 `at://` URLs remaining (was 28), 100% https, first card = "Claude, Code knowledge gap" with clickable `https://bsky.app/profile/…/post/…` links.

**How it improves the platform.** Before: the Theme Signals cards Chris shipped in S2978 had 7 evidence links each, but 12% of those links (all Bluesky, 28/238 items) were `at://` protocol URIs that browsers can't open — clicking did nothing. Source labels drifted (`yahoo_finance` and `Yahoo Finance` shown side-by-side depending on how each item was tagged upstream), making the cards look inconsistent. After: every evidence link is a clickable https URL; every source shows a consistent human-readable label (`Bluesky`, `Product Hunt`, `Yahoo Finance`, `Hacker News`, etc.); each card defaults to top-3 evidence with a `View all N →` expand to see the rest — less visual noise on scan, full detail one click away. Also hardened: URL scheme allowlist drops `javascript:` / `data:` / `file:` / etc. defensively (Rigby T1 same-PR soft-blocker; no such URLs in current corpus but the rendering surface now refuses them if a future spider ever ships one).

**Next session first action.** Wait for Chris. Sensible follow-up candidates (all Phase B / next-arc territory, do not proactively dispatch): (a) **Phase B "Why now" LLM summarizer** — replace the deterministic template with LLM-generated 1-2 sentence summary; still open from S2978; (b) **Phase B who-benefits/who-loses** — sector map + example tickers for Investable cards; (c) **sub-tab persistence via localStorage** — trivial follow-up flagged at S2978 A2; (d) UI browser smoke — click a Bluesky evidence row + a Reuters row on `/workspace?tab=intelligence&sub=theme-signals` to visually confirm the expand toggle + external-link behavior. Reframe fold trigger count = **10** (S2969→S2979). Rigby-drafted-spec variant now at **six walks** (S2973+S2974+S2975+S2977+S2978+S2979).

---

## Findings from sampling (pre-T1 SIGN)

### Evidence-URL audit (238 items across both tabs, 7d, pre-code)

| Metric | Value | Notes |
|---|---|---|
| Total evidence items | 238 | across all surviving cards in both tabs |
| URL schemes | https: 210 (88%) · **at: 28 (12%)** | all `at://` from Bluesky items — unclickable in browsers |
| Source-label drift | `yahoo_finance: 33` + `Yahoo Finance: 13` | same spider ships two forms — extractor code `item.get('source') or row.spider_name` is non-deterministic |
| `Discussion \| Link` hits in `evidence.title` | 0 | that artifact only lives in `sample_signals.text` (which we don't render on the primary path) |
| `sample_signals` URL/source mismatches | 80/238 (34%) | e.g. `source='kickstarter'` with `url='https://producthunt.com/…'`; lower integrity than primary path |
| `sample_signals` per cluster | ≤3 items each | upstream cap at `signal_aggregation_service.py:662`; blob text (no separate title field), truncated to 100 chars |
| First card ("Claude, Code knowledge gap") evidence[0] | `at://did:plc:wz6zzj7u6chymzcjoutnumdc/app.bsky.feed.post/3mriadu4jnr2j` | browsers don't open this — that's the "not shown" impression Chris was seeing |

### Spec-diverging decision (Option A vs Option B)

Spec §Data assumptions asked for `sample_signals`-first with `spider_data_ids` as fallback. Sampling showed the opposite quality gradient. Routed to Chris via plain-english decision framing:
- **Option A (spec as-written):** switch to `sample_signals`-first → cards drop from 7 clean items to 3 messy items with 34% source/url mismatch. Bluesky still broken.
- **Option B (my + Rigby's recommendation):** keep `spider_data_ids` primary + `sample_signals` fallback for empty-primary cases + URL sanitization (Bluesky `at://` → `https://bsky.app/…`) + source label map + top-3 collapse + empty-state row. Spec intent preserved, implementation corrected by data.

Chris ratified A first, then flipped to B after re-reading Rigby's + my recommendations. No code was written between the flip-flop. Deliverable `4088978f-d135-4e13-ac7f-008e0cc06f37` records the trail (Rigby's memory-store was at limit so she pinned it as an engineering_spec instead).

---

## Shipped changes (PR #3613, merge SHA `45e2bc69e`)

### `core/services/evidence_display.py` (new, 233 lines)

- `SOURCE_DISPLAY_LABELS` — raw slug → human-readable display label map (32 entries covering current corpus). Titlecase fallback splits on `_ - \s+` so `polygon_gaming` → `Polygon Gaming` without needing an explicit entry, and inputs already display-ready (`Yahoo Finance`) round-trip correctly.
- `format_source_label(raw)` — map lookup (case-insensitive) with titlecase fallback. Canonicalizes the observed `yahoo_finance` + `Yahoo Finance` drift into one form.
- `sanitize_evidence_url(url)` — transforms Bluesky `at://did:*/app.bsky.feed.post/<rkey>` to `https://bsky.app/profile/<did>/post/<rkey>`. Http/https allowlist drops everything else defensively (Rigby T1 XSS-shape defense). Returns `None` for unsafe schemes.
- `normalize_evidence_text(text)` — display-only cleanup: strip `Discussion | Link` (case-insensitive), collapse whitespace, trim. Used only by sample_signals fallback path (primary path items are clean upstream).
- `normalize_evidence_row(title, url, source, published)` — shape one evidence row against the card contract. Applies URL sanitize + source label + text normalization. Returns `None` when both title and URL are empty after normalization.
- `evidence_from_sample_signals(sample_signals, max_items)` — convert `{url, text, source}` per-signal dicts to evidence contract; used as fallback when primary yields empty.
- `sort_evidence_by_relevance(evidence)` — stable sort by (url_missing, title_placeholder). Clickable + real-titled items float to top. Preserves extractor walk order among ties.

### `core/services/theme_signals_service.py` (95-line delta)

- `_extract_evidence_from_row_items` — routes each item through `normalize_evidence_row`. Behavior change (spec-aligned per Rigby A2 call-out): items with title present but URL sanitized-away now render as unclickable snippets (`url=None`) instead of being dropped. Zero rows affected in current corpus; defensive for future spider drift.
- `extract_evidence_from_cluster` — primary path unchanged. Fallback: `evidence_from_sample_signals` when primary yields empty. Apply `sort_evidence_by_relevance` before return.
- `_prefetch_evidence_for_clusters` — same primary/fallback logic. Batch prefetch preserved (single `LegacySpiderData.objects.filter(id__in=...)` for union of survivor spider_data_ids).

### `frontend/src/components/theme-signals/ThemeSignalCard.tsx` (92-line delta)

- Top-3 evidence visible by default (constant `DEFAULT_EVIDENCE_VISIBLE = 3`).
- `View all N →` / `Show less` toggle button when `evidence.length > 3`. Local `useState` — no persistence (sub-tab persistence still queued from S2978 A2).
- Empty-state row: `"No evidence items available yet."` — defensive UX; strict gate normally filters these upstream.
- Null-URL guard: renders `<div>` snippet (with `·` marker) instead of `<a href={null}>` when a sanitized URL comes through as `null`.
- `ThemeSignalEvidence.url` type widened to `string | null`.
- Section header now `Evidence (top 3)` when >0 items.

### `core/tests/test_evidence_display.py` (new, 42 tests)

Coverage: URL sanitizer (Bluesky did:plc / did:web transform + scheme allowlist + `javascript:`/`data:`/`file:`/`vbscript:` rejection + non-Bluesky at:// rejection + missing netloc), source-label mapping (known slug / titlecase fallback with underscore / hyphen / whitespace splitters / case-insensitive lookup / drift-collapse), text normalization (Discussion|Link case-insensitive strip + mixed spacing + whitespace collapse + trim), sample_signals conversion (shape mapping / Bluesky URL transform inside fallback / Discussion|Link stripping inside fallback / cap at max_items / empty inputs / non-dict entry skip), relevance sort (clickable first / real title first / tie preservation).

### `core/tests/test_theme_signals.py` (7 new tests + 1 updated)

- Updated `test_source_falls_back_to_spider_name_when_item_has_no_source` for new display-label semantics (`hackernews` → `Hacker News`).
- New `test_primary_path_transforms_bluesky_at_uri_to_bsky_app`.
- New `test_primary_path_drops_unsafe_scheme_url_but_keeps_title`.
- New `test_primary_path_formats_source_label`.
- New `test_falls_back_to_sample_signals_when_spider_data_ids_yields_empty`.
- New `test_falls_back_to_sample_signals_when_no_spider_data_ids`.
- New `test_spider_data_ids_preferred_over_sample_signals_when_both_populated` (regression guard).
- New `test_evidence_relevance_sort_clickable_first`.

**Total:** 82/82 tests pass.

---

## SIGN cycle log

### T1 SIGN (with sampling findings + zoom-out ask)

Routed 4 open questions to Rigby: (1) rejecting spec Option A directives based on sampling, (2) URL sanitization scope, (3) source-label map maintainability, (4) top-3 collapse density risk.

Rigby T1 verdict: **AGREE overall, no F-BLOCKERS**. Two same-PR mitigations flagged:
- Scheme allowlist (http/https only) — soft-blocker for XSS-shape defense. **Applied**.
- Backend relevance sort so top-3 = best 3 — **applied** as `sort_evidence_by_relevance`.

Rigby suggested moving the helpers to a small utility module rather than burying them in `theme_signals_service.py` — **applied** as `core/services/evidence_display.py`.

### Chris D-verdict

- **First verdict:** Option A (ship spec as-written).
- **Flip:** Chris re-read and switched to Option B a few minutes later. "flip to B, I am SOOO SORRY! I have a lot on my brain and must of not understood my own thoughts lol." No code written between the flip-flop.
- **Trail note:** Rigby captured as pinned deliverable `4088978f-…` (memory-store at capacity).

### A2 SIGN (with grep spot-check for predicate drift)

`grep` outside tests: zero external callers of `extract_evidence_from_cluster` / `_prefetch_evidence_for_clusters` / `_extract_evidence_from_row_items`. Card contract (title, url, source, published) unchanged; `url` typed `string | null` on frontend admits sanitized-away rows.

Live-verify shipped inline: 0 `at://` remaining (was 28), source labels canonicalized (`Yahoo Finance: 46` = 33+13 merged), first card ("Claude, Code knowledge gap") first evidence URL now `https://bsky.app/…`.

Rigby A2 verdict: **AGREE, no F-BLOCKERS**. 4 optional same-PR polish asks: (1) regex precompile — already done at module import; (2) label map location — leave as-is (services/ is coherent, promote to core/utils/ only when a second consumer appears); (3) semantic change (title-kept + null-URL) — call out in PR summary (**done**); (4) recency tie-breaker in sort — deferred, published often missing.

Rigby ops-suggestion at merge: "one API smoke call to confirm evidence.url is never at:// and scheme allowlist is enforced" — **done** via post-merge Django Client probe.

---

## Live-verify (post-merge, at HEAD `45e2bc69e`)

Django `Client(HTTP_HOST='localhost').force_login(chris).get('/api/theme-signals/', {tab, days, limit})`:

| Probe | Result |
|---|---|
| Buildable status / cards / scanned | 200 / **5** / 71 |
| Investable status / cards | 200 / **20** |
| `at://` URLs across both tabs | **0** (was 28) |
| null URLs (unclickable snippets) | **0** (nothing lost to scheme allowlist) |
| First buildable card title | `"Claude, Code knowledge gap"` (matches spec's exact example) |
| First buildable evidence[0] | source=`"Bluesky"`, url=`"https://bsky.app/profile/did:plc:wz6zzj7u6chymzcjoutnumdc/po…"` |
| Investable first card | `"Berlin, Pride opportunity window"`, evidence=7, who_benefits_who_loses.status=`coming_in_phase_b` (unchanged from S2978) |
| API integrity spot-check (both first cards) | All URL schemes ∈ {https}; zero snake_case source labels; top-3 all clickable + all real titles |

**Not verified this session (Chris follow-up):** browser click test on `/workspace?tab=intelligence&sub=theme-signals` — Rigby flagged this as the "single extra probe" if you want UX-only confidence. The Django Client can't exercise expand-toggle DOM state or actual browser link opening.

---

## Candidate folds surfaced (NOT codified)

Continuation of S2978 ledger; only new/updated entries listed:

4. **"Deliverable-as-spec first walk validates the workflow reframe."** Trigger count: **10** (S2969–S2979). Ten-trigger corpus.
9. **"Rigby-drafted spec deliverable is a first-class origination path."** Trigger count: **6** (S2973, S2974, S2975, S2977, S2978, **S2979**). Six-walk corroboration.
11. **"Sample-before-plan cuts T1 revision cycles to zero."** Trigger count: **5** (S2974, S2975, S2977, S2978, **S2979**). S2979: pre-plan URL scheme audit predicted 12% of URLs unclickable + labels drift; live-verify matched exactly (0 `at://` after fix, `Yahoo Finance` merged to 46). Fifth-walk corroboration.

**NEW at S2979:**

19. **"Chris ratification flip pre-code is cheap; ratification flip post-code is expensive."** Trigger count: **1** (S2979 — Chris ratified A, flipped to B within minutes, zero code written between). Flag: when I catch a spec divergence, route Chris the decision framing BEFORE implementation begins so a flip costs zero rework. Same pattern as sample-before-plan (fold 11) but for decisions, not data. Watch for second walk.

20. **"Rigby memory-store capacity forces trail notes into deliverables."** Trigger count: **1** (S2979 — `remember_tool` returned "Memory limit reached (200 items). current_count: 1753, max_items: 200" → Rigby captured trail note as pinned engineering_spec deliverable instead). Flag: memory-store enforcement is currently blocking new writes but the substrate has 1753 items despite max_items=200 — suggests silent limit-bypass elsewhere or the max_items enforcement is a soft-cap in code that hard-fails on new writes only. Log for Rigby Tool Gap Ledger. Watch for second trigger.

---

## Substrate ledger updates (deferred; requires separate arc)

- **Rigby Tool Gap Ledger candidate:** `remember_tool` "Memory limit reached (200 items)" while current_count=1753 — investigate soft vs hard cap enforcement; either raise limit, prune old entries, or fix the enforcement code path. Belongs on the Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` per `feedback_rigby_tool_gap_ledger`.

---

## Twin-pointer docs card (per feedback_twin_pointer_docs_at_boundaries)

| Artifact | Repo path | Workspace UI |
|---|---|---|
| S2979 handoff | `docs/handoffs/SESSION_2979_THEME_SIGNALS_EVIDENCE_FIRST.md` | n/a — repo-only |
| S2979 spec deliverable | n/a — workspace-only | Donkey Betz `b4503364-…` → deliverable `c4602ccd-a973-424f-8bc5-dcc16f797430` |
| S2979 decision trail note | n/a — workspace-only | Donkey Betz `b4503364-…` → deliverable `4088978f-d135-4e13-ac7f-008e0cc06f37` (pinned) |
| Shipped code | PR #3613 (merged, branch deleted); HEAD 45e2bc69e | https://github.com/clwest/donkey-betz-platform/pull/3613 |
| Support conversation | n/a — chat-only | `pa-08fb0194b6004311` |
| Prior session | `docs/handoffs/SESSION_2978_THEME_SIGNALS_V1.md` | n/a |
