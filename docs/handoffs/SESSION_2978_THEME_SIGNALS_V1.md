# SESSION 2978 — Theme Signals v1 (Phase A)

**HEAD at close:** `3946c958f` (PR #3611 merged; docs cascade PR TBD)

**Branch shape:**
- `feat/s2978-theme-signals-v1` → main (merged, branch deleted)

**Deliverables:**
- S2978 spec: `63ec4d1d-9425-468b-815c-b4e571e3fe44` — Initiative Spec: Theme Signals v1 (Combined feed; Buildable default; Investable tab; 7-day window) — Rigby-drafted, **fifth walk** of the Rigby-drafted-spec origination variant. Status flipped to `completed` at close.
- Initiative: `6153a03e-274a-49c7-a5b4-03b5016cd249` — Theme Signals v1 (the first initiative created since S2977 PR #3610 fixed the `owner_id` regression).

**Support conversation:** `pa-7f71227079334330` (S2978 pin, Chris-minted at S2977 close)

---

## Three-part summary (Chris-facing)

**What was done.** Shipped the Theme Signals v1 product-tier UI on top of `SignalCluster` per the ratified spec. New Intelligence → Theme Signals sub-tab in Workspace with two sub-tabs: **Buildable** (default) and **Investable**. Strict quality gate (title-block regex + evidence density ≥3 sources OR ≥5 items + confidence ≥0.60 Buildable / ≥0.65 Investable). 5-point card contract: title / why-now / evidence (3-7 links) / so-what action / confidence + drivers. Investable variant adds a "Coming in Phase B" placeholder for who-benefits/who-loses. Backend service + endpoint + 35 tests + frontend tab + card component + wiring, all in single PR #3611.

**How it improves the platform.** Before: `SignalCluster` was reachable only via the raw Signal Explorer (spider-oriented, ops-facing) — nothing product-shaped that answered "should I build this?" or "should I trade this?". After: `/workspace?tab=intelligence&sub=theme-signals` shows curated cards that route by source composition + catalyst keywords, filtered by strict gate to keep the "junk cluster" noise out entirely. Live-verified on prod DB (HEAD `06f2a5b7d`): Buildable=5 cards (at min gate), Investable=20 cards (limit-capped), 7 real evidence links per card with working URLs into the source articles. The prior "Discussion, Link opportunity window" boilerplate clusters no longer surface — they get title-blocked upstream.

**Next session first action.** Wait for Chris. Sensible follow-up candidates (all Phase B / next-arc territory, do not proactively dispatch): (a) **Phase B "Why now" generator** — replace the deterministic template with an LLM summarizer + sub-tab persistence via localStorage; (b) **Phase B who-benefits/who-loses** — sector map + example tickers for Investable cards; (c) **Cluster improvement arc** — the strict gate suppressed 21/70 for evidence density and 9/70 for blocked titles, so raw cluster quality is the biggest lever for Buildable headroom; (d) **theodds auth-failure fix** — still open from S2972–S2975. Reframe fold trigger count = **9** (S2969→S2978).

---

## Findings from sampling (pre-T1 SIGN)

### SignalCluster corpus (7d at HEAD `06f2a5b7d`)
- 70 total clusters across 7 pattern types (`trend_emergence` 28, `demand_spike` 21, `opportunity_window` 8, `skill_demand` 6, `knowledge_gap` 4, `sentiment_shift` 2, `content_gap` 1).
- Field shape (verified via `orm_inspect_tool`): `name`, `pattern_type`, `keywords` (list), `source_breakdown` (dict spider→count), `confidence` (float), `spider_data_ids` (list of UUIDs), `detected_at`.
- **304/304 `spider_data_ids` resolve via `core.models_unified_system.LegacySpiderData`** (the legacy 15-column variant). The persistence variant referenced by the model docstring (`persistence.LegacySpiderData`) is not importable in this repo — clusters unambiguously point at the legacy class.

### Strict-gate simulation (pre-implementation)
With tightened title-block pattern (catching `^discussion,\s*link`, `^comments,\s*score`) + evidence density ≥3 sources OR ≥5 items + confidence ≥0.60/0.65:

| Tab | Cards surviving | Gate reasons (7d) |
|---|---|---|
| Buildable | 5 (exactly at ≥5 acceptance threshold, zero headroom) | 9 title / 9 evidence / 37 routed_other_tab |
| Investable | 20 (limit-capped; total pool much larger) | 7 title / 9 evidence / 11 routed_other_tab |

Sim confirmed Phase A is viable on current data; Phase B (better clustering/summarization) is the lever to grow Buildable headroom.

### Frontend surface
- `frontend/src/App.tsx` had zero "signal" references before this session — no existing product-tier signals surface (only the ops-facing `SignalsTab` at S2971 under Intelligence).
- Workspace 5-primary-tab model (Home / Work / Build / Intelligence / System) uses sub-tabs; new tab landed as `intelligence › theme-signals`.

---

## Shipped changes (PR #3611, merge SHA `3946c958f`)

### Backend

**`core/services/theme_signals_service.py`** (new, ~370 LOC):
- Constants (spec-lifted): `BUILDABLE_SOURCES` (15 tech/dev spiders), `INVESTABLE_SOURCES` (12 finance/news/SEC), `CATALYST_KEYWORDS` (SEC/filings + earnings + macro + capital-structure), `BLOCKED_TITLE_PATTERNS` (regex list) + `BLOCKED_LEAD_TOKENS` for token-count heuristic, `MIN_SOURCES=3`, `MIN_ITEMS=5`, `MIN_CONF_BUILDABLE=0.60`, `MIN_CONF_INVESTABLE=0.65`, `MAX_EVIDENCE=7`.
- `route_cluster(cluster) -> Literal['buildable', 'investable', 'neither']` — Investable wins ties.
- `passes_quality_gate(cluster, route, min_confidence_override) -> (bool, str)` — returns reason code (`ok`/`title_blocked`/`evidence_fail`/`conf_fail`/`routed_neither`) for observability.
- `extract_evidence_from_cluster(cluster, max_items=7)` — flattens `LegacySpiderData.raw_data['items']` with title/url fallback chain. Skips items missing both title AND url. Uses `raw_data_dict` property when available (list-shaped `raw_data` defense per T1b non-blocking).
- `_prefetch_evidence_for_clusters(clusters)` — batch-fetches all `LegacySpiderData` rows in ONE query, builds `{cluster_id: [evidence]}` map. Eliminates N+1 across survivors loop (A2 SIGN Z-A2 fold #1, `same_pr_mitigatable`).
- `cluster_to_card(cluster, tab, evidence_override=None)` — shapes 5-point card. Investable adds `who_benefits_who_loses: {status: 'coming_in_phase_b', message: ...}` (D2 placeholder).
- `get_theme_signals(tab='buildable', days=7, limit=20, min_confidence=None)` — public entrypoint. Returns `{tab, days, limit, min_confidence_applied, cards, total_scanned, total_survived, gate_reasons}`.

**`core/views_theme_signals.py`** (new, ~65 LOC):
- `GET /api/theme-signals/?tab=buildable&days=7&limit=20&min_confidence=0.6`
- Session-authenticated (`IsAuthenticated`) — matches `/api/signals/*` auth.
- Params clamped: `days` 1-30, `limit` 1-50, `min_confidence` 0.0-1.0.

**`core/urls.py`**: +1 import + 1 path entry (`path('api/theme-signals/', _theme_signals, name='theme-signals')`).

**`core/tests/test_theme_signals.py`** (new, 35 tests, 5 test classes):
- `RoutingTests` (4): investable-wins-ties, catalyst-kw-forces-investable, pure-buildable, no-matching-sources-routes-neither
- `QualityGateTests` (10): all title-block families + evidence density boundaries + confidence thresholds (Buildable + Investable) + `routed_neither` reason + `min_confidence_override`
- `EvidenceExtractionTests` (5): multi-row flattening, skip-missing-title-and-url, cap at max, **list-shaped raw_data returns [] gracefully** (T1b non-blocking), source-fallback-to-spider-name
- `CardShapeTests` (5): Buildable has-no-who-benefits / Investable has-Phase-B-placeholder / why-now-note-present / why-now-includes-source-names / so-what-mapped-from-pattern-type
- `GetThemeSignalsTests` (8): tab default = buildable / Buildable ≥5 / Investable ≥5 / Investable placeholders / gate-reasons breakdown / days + limit clamped / min-confidence override expands survivors
- `ThemeSignalsEndpointTests` (3): endpoint requires auth (401/403 without session) / Investable returns cards + shape / payload shape complete

### Frontend

**`frontend/src/pages/workspace/tabs/theme-signals/ThemeSignalsTab.tsx`** (new, ~160 LOC):
- Sub-tab switcher (Buildable / Investable) with icons (Sparkles / TrendingUp).
- `useQuery` fetch via `signalsApi.themeSignals({tab, days: 7, limit: 20})`.
- Loading skeleton + empty state ("No cards passed the strict quality gate — try again in 24h").
- Refresh button.
- Collapsed-by-default gate-reasons debug panel (scanned / shown / min-conf + per-reason breakdown).

**`frontend/src/components/theme-signals/ThemeSignalCard.tsx`** (new, ~140 LOC):
- Renders 5-point contract: title (with break-words), why_now + Phase B note tooltip, evidence links (up to 7 with ExternalLink icons, line-clamp-2 + break-words per A2 SIGN non-blocking), so-what badge (color-coded by action), confidence + drivers.
- Investable variant renders dashed "Who benefits / who loses" panel with "Coming in Phase B" message.

**`frontend/src/lib/api.ts`**: `signalsApi.themeSignals({tab, days, limit, min_confidence})` method added.

**`frontend/src/pages/workspace/tabs/index.ts`**: export `ThemeSignalsTab`.

**`frontend/src/pages/WorkspacePageNew.tsx`**: import `ThemeSignalsTab` + `Sparkles` from lucide + sub-tab entry `{ id: 'theme-signals', label: 'Theme Signals', icon: Sparkles }` under Intelligence + render conditional.

---

## Live-verify (post-apply, post-recycle at HEAD `3946c958f`)

```python
>>> from django.urls import reverse
>>> reverse('theme-signals')
'/api/theme-signals/'
>>> from core.services.theme_signals_service import get_theme_signals
>>> b = get_theme_signals(tab='buildable', days=7, limit=20)
>>> i = get_theme_signals(tab='investable', days=7, limit=20)
>>> len(b['cards']), len(i['cards'])
(5, 20)
```

Sample Buildable card:
- title: `'Claude, Code knowledge gap'`
- why_now: `'Knowledge gap surfacing across 3 source(s): bluesky, kickstarter, producthunt. 3 item(s) observed.'`
- why_now_note: `'(Phase A template — expanded in Phase B)'`
- so_what: `'research'` (knowledge_gap → research per action map)
- confidence: `0.75`, drivers: `'bluesky × 1, kickstarter × 1, producthunt × 1'`
- 7 evidence items with real URLs (bluesky posts, kickstarter projects, producthunt entries)
- `who_benefits_who_loses` absent (correct for Buildable variant)

Sample Investable card:
- title: `'Berlin, Pride opportunity window'`
- so_what: `'build/trade'` (opportunity_window)
- 7 evidence items
- `who_benefits_who_loses: {'status': 'coming_in_phase_b', 'message': 'Sector + example tickers coming in Phase B'}`

---

## SIGN cycle log

### T1 (Rigby, tool_runs = 8 substantive)
- **AGREE** on plan shape (D1-D4 respected, routing/gate/patterns align with spec).
- **F-BLOCKER (real)** on evidence lookup: my plan assumed `SpiderData` — Rigby's ORM probe showed 0/3 UUIDs resolved there, confirmed real target is `LegacySpiderData` via `core/views/signals_ui.py:11` docstring reference. Field mapping needed adjustment (`source_url` not `url`, `spider_name` not `source`, title lives in `raw_data['items']`).
- **F-BLOCKER (cosmetic, dropped)** on endpoint callable naming.
- **Non-blocking asks**: MIN_CONF_* as query param (accepted); gate-reasons debug privacy (declined per single-tenant pre-prod).
- **Zoom-out folds** (per PLAYBOOK-6.10.7):
  - Z1 `same_pr_mitigatable`: service duplicates concept from `signal_aggregation_service.py` → keep standalone + add TODO(Phase B) unification pointer at top of file. **Applied.**
  - Z2 `future_trigger`: "Why now" template risks bad first impression if Phase B slips → add subtle "(Phase A template — expanded in Phase B)" secondary text. **Applied.**

### T1b (Rigby, tool_runs = 4)
- **AGREE**, no F-BLOCKER.
- Verified: `LegacySpiderData` importable from `core.models_unified_system`; empirically probed 6 spider families for `raw_data['items']` shape.
- **Non-blocking asks** (both applied):
  - Use `row.raw_data_dict` property to defend against list-shaped payloads.
  - Add explicit test for list-shaped `raw_data` → returns `[]` cleanly.

### A2 (Rigby, tool_runs = 4 substantive)
- **AGREE**, no F-BLOCKER.
- Verified: DB corpus consistent with acceptance numbers; sample cards meet all 5 spec contract points; Investable placeholder present.
- **Non-blocking asks** (both `same_pr_mitigatable`, both applied):
  - Batch-prefetch `LegacySpiderData` for all survivors in ONE query (avoids up to 20 sequential lookups per response).
  - Card overflow guards (`break-words` on titles + `min-w-0` on flex children).
- **Zoom-out folds:**
  - Z-A2 #1 `same_pr_mitigatable` (N+1 query fetch): **Applied via `_prefetch_evidence_for_clusters`.**
  - Z-A2 #2 `future_trigger` (sub-tab default-on-mount, no persistence): recorded as follow-up seed.

**Ratio: 3 SIGN cycles, ~16 tool_runs across cycles.**

---

## Reframe pattern tally
- S2969 → S2970 → S2971 → S2972 → S2973 → S2974 → S2975 → S2977 → **S2978** = **ninth walk** of the reframe pattern (Chris hands spec → Claude samples state → propose → Rigby SIGN pressure-tests → ship → Rigby A2 SIGN).
- **Fifth walk of the Rigby-drafted-spec origination variant** (S2973 + S2974 + S2975 + S2977 + S2978).

---

## Files touched

**Added:**
- `core/services/theme_signals_service.py`
- `core/views_theme_signals.py`
- `core/tests/test_theme_signals.py`
- `frontend/src/pages/workspace/tabs/theme-signals/ThemeSignalsTab.tsx`
- `frontend/src/components/theme-signals/ThemeSignalCard.tsx`

**Modified:**
- `core/urls.py` (+1 import + 1 path)
- `frontend/src/lib/api.ts` (+1 method on `signalsApi`)
- `frontend/src/pages/workspace/tabs/index.ts` (+1 export)
- `frontend/src/pages/WorkspacePageNew.tsx` (+1 import + Sparkles icon + sub-tab + render conditional)

**Total:** 9 files, 1187 insertions.

---

## Follow-up seeds (deferred to future arcs — do NOT dispatch proactively)

1. **Phase B "Why now" generator** — replace deterministic template with LLM summarizer. Would drop the `why_now_note` and improve card quality. Requires a small LLM call per card (or per cluster, cached).
2. **Phase B who-benefits/who-loses** — sector map + example tickers for Investable cards. Needs per-catalyst-keyword → sector mapping + optional ticker DB linkage.
3. **Sub-tab persistence via localStorage** (A2 SIGN Z-A2 fold #2, `future_trigger`) — remember Buildable vs Investable across page reloads.
4. **Cluster quality improvements** — biggest lever for Buildable headroom. 21/70 clusters fail evidence density; better dedup + summarization would grow the pool.
5. **Compose theme_signals_service constants with `signal_aggregation_service.py` source classification** (T1 zoom-out Z1, `future_trigger`) — currently duplicated; unify once product-tier gate stabilises.
6. **`theodds` auth-failure fix** — still open from S2972–S2975, needs `THE_ODDS_API_KEY` rotation.
7. **`remoteok` pre-dedup filter** — still open from S2975.
