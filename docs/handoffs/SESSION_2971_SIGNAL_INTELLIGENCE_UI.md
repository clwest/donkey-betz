# SESSION 2971 — Signal Intelligence UI (Workspace tab) shipped

**HEAD at close:** `c9cb67cad` (PR #3597 merged; docs cascade PR TBD)
**Branch shape:**
- `feat/s2971-signal-intelligence-ui` → main (merged, branch deleted)

**Deliverable:** `ade9339f-c41f-48a5-9ce8-fa8beee696cc` — "Signal Intelligence UI (Donkey Betz) — Engineering Spec (Signals Dashboard + Spider Feed Explorer + Cluster Explorer scaffolding)"

**Support conversation:** `pa-ab10ffdb0e5f4597`

---

## Three-part summary (Chris-facing)

**What was done.** Built the Signal Intelligence UI Chris asked for as a spec — three views (Dashboard / Feed Explorer / Cluster Explorer) reachable from Workspace → Intelligence → Signals. Backend adds 4 thin HTTP endpoints reusing existing service functions (aggregate, feed, embedding coverage) plus extended cluster filters; frontend adds a single Workspace sub-tab with a shared 24h/7d/30d window selector and drill-down drawers. Shipped in **one PR** (#3597, HEAD `c9cb67cad`, +2119 / -1) after Rigby T1 SIGN → fold three concerns → A2 SIGN → merge with `--admin` → recycle → in-shell live-verify (all 4 endpoints returned 200 with real data: 447 clusters, 4 aggregation buckets, 16,874 feed rows, 4,022/16,874 = 23.8% embedding coverage matching session-open baseline).

**How it improves the platform.** Before: to inspect spider ingestion, embedding coverage, or signal clusters, Chris had to open Django shell or scrape PA-tool output. After: `/workspace?tab=intelligence&sub=signals` gives him a real operator surface — filter feed rows by data_type + spider + embedding-status, browse clusters by min_confidence + source spider + keyword, see ingestion + coverage + cluster summary at a glance. This is the same data the platform runs on, but presented as a first-class UI instead of a shell script. Reuses `LegacySpiderData` (the plane the backfill drains) so numbers here match numbers Rigby quotes.

**Next session first action.** Wait for Chris — the reframe held for the **third walk** (S2969, S2970, S2971 all followed spec-pointer → SIGN → implement → live-verify → close). Fold candidate #4 from S2970 promotes to trigger count 3 (spec-driven session shape); watch S2972 for a fourth to consider a Playbook rule proposal.

---

## The workflow reframe: third walk

S2969 established the pattern. S2970 validated it once (RSS-first spider fixes). S2971 validates it again (Signal Intelligence UI). Same shape each time:

1. Chris pastes a Deliverable ID + support conversation ID.
2. Claude reads the spec, does a targeted "existing implementation analysis" (Cycle 1A verify-before-build).
3. T1 SIGN to Rigby with reuse-first plan + explicit zoom-out ask.
4. Fold Rigby's F-BLOCKERs and route-placement concerns.
5. Implement backend → tests → frontend → build check.
6. A2 SIGN with file+line evidence.
7. Merge with `--admin`, `make recycle-all`.
8. Live-verify in-shell (Django `Client().force_login` for auth-gated routes).
9. Rigby verifies from her tool surface (with the known limitation her `web_fetch_tool` can't carry session cookies — 401 confirms routing + auth wire).
10. Docs cascade + wrapper pin bump.

Cost per session in this shape: roughly minimal (a handful of PA calls, no v2 subprocess dispatches).

---

## Rigby's T1 folds (all three accepted, all shipped)

1. **Route placement — Workspace tab, not standalone `/signals`.** Rigby cited `frontend/src/App.tsx` explicit note "All cockpit routes now redirect to Workspace tabs" plus existing `/boardroom` and `/governance` redirects, and the `intelligence` primary tab's existing sub-panel pattern. Reachable at `/workspace?tab=intelligence&sub=signals`; `signals` legacy alias added to `legacyTabMapping` for future rail shortcut.

2. **Extract pure `spider_feed.py` helper.** Don't call `_handle_spider_status` from HTTP (wrong layer). New `core/services/spider_feed.py` with `query_spider_feed(filters) -> {items, total, offset, limit, has_more}` — both future tool callers and the new REST endpoint share one query implementation.

3. **`get_queryset()` override, not custom FilterSet.** `DjangoFilterBackend` can't express JSONField `has_key`, computed cutoffs, or icontains-OR. Kept it for `pattern_type` + `status` (declarative), added imperative parsing for `window_hours` / `min_confidence` / `source_spider` / `query`.

Rigby also raised 8 non-blocking implementation gotchas at T1 ACK — all folded:
- JSONField `keywords` icontains stringifies (fine for v1)
- `source_breakdown__has_key` correct shape for source_spider matching
- Empty `window_hours` no-ops
- `IsAuthenticated` on all new views
- Feed helper returns `{items, total, offset, limit, has_more}` with stable `-created_at`
- Frontend `setSearchParams(prev => ...)` pattern respected (not yet using URL persistence per spec §8 nice-to-have)
- Times via `Intl.DateTimeFormat('en-US', { timeZone: 'America/Denver' })`
- Tests assert new list fields + empty-filter no-op

Rigby A2 SIGN verdict: **AGREE, no F-BLOCKERS**. Two minor nits (embedding-status label wording; potential future GIN index on keywords) noted for post-v1.

---

## Live-verify results (post-merge + recycle)

In-shell via `django.test.Client().force_login(chris_superuser)`:

| Endpoint | Status | Payload highlights |
|---|---|---|
| `GET /api/signals/aggregate/?days_back=7` | 200 | 4 buckets (news/financial/tech/ai_ml), 447 actionable / 581 total, 25 distinct spiders |
| `GET /api/signals/feed/?limit=3` | 200 | total=16874, pagination shape correct |
| `GET /api/signals/embedding-coverage/` | 200 | 4022 / 16874 = 23.8% (matches session-open baseline; backfill continues draining) |
| `GET /api/v1/signal-clusters/?window_hours=720&min_confidence=0.5&page_size=3` | 200 | count=447, new list fields (`signal_count`, `source_breakdown`, `keywords`) present |

Test suite: `USE_PGBOUNCER=0 python manage.py test core.tests.test_signals_ui_api -v0 --keepdb` → **29/29 pass** in 0.36s.

---

## Shipped code

**Backend (`core/`)**
- `services/spider_feed.py` (NEW, 182 lines): `query_spider_feed()` + `get_spider_feed_detail()` pure helpers.
- `views/signals_ui.py` (NEW, 171 lines): 4 DRF function-views under `/api/signals/*`.
- `tests/test_signals_ui_api.py` (NEW, 313 lines, 29 tests).
- `views_audit_api.py` (EDIT): `SignalClusterViewSet.get_queryset()` override — window_hours, min_confidence, source_spider, query.
- `serializers_audit.py` (EDIT): `SignalClusterListSerializer` gains `signal_count`, `total_signals`, `source_breakdown`, `keywords`.
- `urls.py` (EDIT): imports + 4 endpoint paths.

**Frontend (`frontend/src/`)**
- `lib/api.ts` (EDIT): `signalsApi` + typed params.
- `pages/WorkspacePageNew.tsx` (EDIT): `signals` sub-tab entry + `signals` legacy alias + `<SignalsTab />` render branch.
- `pages/workspace/tabs/signals/SignalsTab.tsx` (NEW): parent with view switcher + window selector.
- `pages/workspace/tabs/signals/SignalsDashboardView.tsx` (NEW): 3 widgets.
- `pages/workspace/tabs/signals/SignalsFeedView.tsx` (NEW): table + filters + row drawer with JSON collapsers.
- `pages/workspace/tabs/signals/SignalsClustersView.tsx` (NEW): table + filters + cluster drawer.
- `pages/workspace/tabs/signals/formatters.ts` (NEW): MST/MDT time formatters.

---

## Data-plane note (deferred)

The build uses `LegacySpiderData` (spec §5.1 field names match; backfill drains against it). The canonical `persistence.SpiderData` has extended scoring fields (`relevance_score`, `opportunity_score`, `quality_score`, `urgency_score`) but uses `content` + `structured_data` where LegacySpiderData uses `raw_data` + `processed_data`. Migrating the Signal Intelligence UI to `persistence.SpiderData` is a separate arc — not blocking, not urgent.

---

## Candidate folds surfaced this session (NOT codified)

**Trigger count building toward Playbook rules — do NOT amend without a second trigger unless otherwise noted:**

Carrying forward from S2969/S2970:

1. **Soft-key-vs-LLM-schema-gate.** **Trigger count: 1** (S2968 PR #3589). No new instance at S2971.
2. **"We're building a duplicate of a thing we already have" pattern.** **Trigger count: 2** (S2968). No new instance at S2971.
3. **"Auditability primitive already exists in a different plane" pattern.** **Trigger count: 1** (S2969). No new instance at S2971.
4. **"Deliverable-as-spec first walk validates the workflow reframe."** **Trigger count: 3** (S2969 + S2970 + S2971). Three-trigger corpus reached. If S2972 continues the pattern, this promotes to a Playbook rule proposal about spec-driven session shape. Watch for the fourth.
5. **"Live-verify surfaces the real root cause the observability layer was designed to expose."** **Trigger count: 1** (S2970). No new instance at S2971.
6. **"Post-merge live-verify reveals scope-adjacent infra bug; scope-in a flag-gated fix, don't defer."** **Trigger count: 1** (S2970). No new instance at S2971.

New at S2971:

7. **"Route-placement is a settable expectation, not a spec constraint."** Spec §3.1 offered `/signals` OR `/intelligence/signals`. Rigby's tool-grounded read of App.tsx pushed to a THIRD option (Workspace sub-tab) that better matched Chris's directive. Zoom-out ask about route surface (per `feedback_zoom_out_ask_per_rigby_sign`) directly surfaced this. **Trigger count: 1** (S2971). Watch for a second.

8. **"Rigby web_fetch_tool can't authenticate against Django session-cookie endpoints."** Verification of auth-gated new endpoints stayed on Claude's side (Django `Client().force_login`); Rigby's tool-surface probe returns 401 (correct behavior, wrong verification vehicle). Flagged to her as a ledger candidate; not adding yet — waiting for a second occurrence. **Trigger count: 1** (S2971).

---

## Candidate follow-ups (Chris picks whether to open)

- **Rail shortcut for `/signals`.** Legacy alias `signals: { primary: 'intelligence', sub: 'signals' }` already wired in `WorkspacePageNew.tsx`. Only need a `<NavLink to="/workspace?tab=signals">` entry in `frontend/src/components/layout/Sidebar.tsx:55`. ~5 min.
- **Per-view window selector.** Current build shares one 24h/7d/30d window across Dashboard/Feed/Clusters. If Chris wants independent windows per view, store `dashboard_window` / `feed_window` / `clusters_window` in search params. Rigby's recommendation at A2 SIGN: keep shared for v1; only iterate if a real complaint surfaces.
- **URL persistence for filter state.** Spec §8 nice-to-have. Feed and Cluster Explorer filter state currently lives in component state; deep-linking requires plumbing every filter to `useSearchParams`.
- **"Create Initiative from Cluster" button.** Spec §8 nice-to-have. Wires cluster detail drawer to `work_tool.initiative_create` via PA.
- **Migrate to `persistence.SpiderData`.** Would give the Feed Explorer access to relevance/opportunity/quality scoring fields. Separate arc.
- **sports_injuries keyword tuning** (from S2970 open) — unchanged.
- **Worker egress validation arc (broader)** (from S2970 open) — unchanged.

---

## Post-close addendum

**Backfill drain continuing:** at session open, coverage was 4022/16874 = 23.8%. Backfill Beat task (`backfill-spider-embeddings`) is enabled with `last_run_at=2026-07-26 05:00 UTC`, `total_run_count=650`. Recent 24h: 162 embedded of 624 new rows. Should continue draining organically; check `/api/signals/embedding-coverage/` in future sessions to watch the trend.

---

## What's forbidden at S2972 (carry-forward)

All prior forbidden entries carry forward. Nothing new at S2971.

- Do not automatically merge S2968 PR-B.
- Do not proactively dispatch v2 test runs at session open.
- Do not chase spider parsing bugs for reddit / sports_injuries (fixed S2970).
- Do not flip `SPIDER_USE_THREADED_DNS_RESOLVER` off in this env.

---

## For fuller context (S2846 → S2971)

- **S2971 handoff (current):** `docs/handoffs/SESSION_2971_SIGNAL_INTELLIGENCE_UI.md`
- **S2971 shipped code:** PR #3597 (`feat(s2971): Signal Intelligence UI — Workspace tab (backend + sub-panel)`)
- **S2971 spec deliverable:** `ade9339f-c41f-48a5-9ce8-fa8beee696cc`
- **S2971 support conversation:** `pa-ab10ffdb0e5f4597`
- **S2970 handoff:** `docs/handoffs/SESSION_2970_PR_B_RSS_FIRST.md`
- **S2969 handoff:** `docs/handoffs/SESSION_2969_SPIDER_DIAGNOSTIC_PERSISTENCE.md`
- **S2968 handoff:** `docs/handoffs/SESSION_2968_OPTION_BETA_AND_REFRAME.md`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
