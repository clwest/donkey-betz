# SESSION 2980 — Theme Signals UX Upgrade (source-diversified evidence + action chips + Build-only toggle) + Workflow-Shape Codification Draft

**HEAD at close:** `fb2dffe99` (PR #3615 merged; docs cascade PR TBD)

**Branch shape:**
- `feat/s2980-theme-signals-diversify-action-buildonly` → main (merged, branch deleted)

**Deliverables (this session):**
- **S2980 spec:** `f3cc9499-9990-4924-81a4-6edba3f1457a` — S2980 Theme Signals UX Upgrade — Source-Diversified Evidence + Action Chips + Build-Only Toggle (Implementation Spec) — Rigby-drafted, **seventh walk** of the Rigby-drafted-spec origination variant.
- **S2980 workflow-shape source deliverable (NEW artifact class):** `e8429049-300f-4725-8d02-a79c285ed720` — S2980 Workflow Shape — Deliverable-Spec-to-Ship Recipe (Playbook amendment source) — Rigby-drafted after mid-session Chris interrupt. 18,716 chars. Category: engineering_spec / document. **Chris deferred formal Playbook amendment ratification to a future session** — this doc is the SOURCE, not the ratified rule set.

**Support conversation:** `pa-323b267495764a04` (S2980 pin, Chris-minted at S2979 close)

---

## Three-part summary (Chris-facing)

**What was done.** Fixed the "Buildable cards look all-Bluesky" complaint AND the "Buildable cards say Research/Watch" complaint in one PR (#3615). Root cause of the evidence bias was NOT walk-order at the row level (that was my initial hypothesis); it was **item-level walk bias inside the FIRST row** — a single Bluesky row carrying 7+ items in its `raw_data['items']` was saturating `MAX_EVIDENCE=7` before the extractor even touched the sibling kickstarter/producthunt rows in the same cluster. Fix: new `_round_robin_across_row_buckets` helper interleaves items one per row per pass. Also canonicalized the 5-value `so_what` field down to a 3-value `action` enum (build / research / watch) per spec, and added a server-side `?build_only=true` filter driving an `All | Build-only` toggle on the Buildable tab. Then Chris interrupted mid-cascade — before I ran session close, he said "this workflow needs to become the new normal in the Playbook" — so Rigby and I drafted a **workflow-shape source deliverable** (e8429049) capturing the exact recipe of what just happened, phase-by-phase, with turn-by-turn timeline. Chris ratified deferring formal Playbook amendment to a future session.

**How it improves the platform.** Before: 2 of 5 Buildable cards showed 100% single-source evidence (Bluesky-heavy) despite the cluster's `source_breakdown` naming 3 sources; 0 of 5 Buildable cards were labeled pure `build` (Chris's complaint "the tab reads Buildable but is mostly Research/Watch"). After: every one of the 5 Buildable cards improved source diversification (Claude/Code knowledge gap went 100% single-source → 2 sources with top 57%; Galaxy/Samsung went 2 sources with top 57% → 5 sources with top 29%). Action chip is now Build/Research/Watch on every card — Build-only toggle filters to just the actionable-now items (5→1 on current corpus, which surfaces the Chatgpt/Openai opportunity_window as the only true Build card). Beyond the code: we now have a workspace deliverable capturing the workflow recipe that made this land cleanly, so future sessions can copy the shape instead of re-deriving it and future Playbook amendments have a canonical source to codify from.

**Next session first action.** Wait for Chris. Sensible next-arc candidates: (a) **Formal Playbook amendment cycle** for the workflow-shape deliverable — fresh session, cleaner head, full T1/T2/T3/T4 SIGN + D1..D7 verdict cycle per governance framework. Deliverable `e8429049-…` is the input. (b) **Phase B Theme Signals "Why now" LLM summarizer** — still open from S2978. (c) **Phase B who-benefits/who-loses** — still open from S2978. (d) **Rigby memory-store cap investigation** — still open from S2979. Reframe fold trigger count = **11** (S2969→S2980). Rigby-drafted-spec variant now at **seven walks** (S2973+S2974+S2975+S2977+S2978+S2979+S2980).

---

## What made this session unusual: mid-flight workflow-shape interrupt

The S2969–S2979 pattern was: one PR ships, close cascade runs, done. S2980 broke that shape at turn ~18: after A2 SIGN passed and I was reporting "code done, waiting on ship approval," Chris said **"Do not run cascade until you check in with me."** His follow-up (turn ~19): "I realized this needs to become the new normal in the Playbook but I wanted to do it in this session because you and Rigby are oriented and will know exactly how to lay-out the steps behind the scenes to help each other."

Two things happened as a result:

1. **Chris ratified ship-then-codify** (Option 1 of a plain-english framing I routed): PR #3615 shipped first (~4 turns), then Rigby and I drafted the workflow-shape deliverable (~5 turns) while both agents were still oriented on the S2980 flow.

2. **Rigby recommended deferring formal ratification** to a future session. Reason: this is meta-process; running the formal Playbook amendment cycle (T1/T2/T3/T4 SIGN + workspace amendment envelope + D1..D7 verdicts per v0.8.0 shape) with a fresh session gives a clean-head review AND respects the constitutional discipline ("direct-to-code bypass for methodology changes = constitutional violation" per project_playbook_v0_1_0_ratified). Chris agreed.

**Candidate fold (NEW at S2980):** "Chris pause-pre-cascade lets meta-work happen while both agents are oriented — cheaper than reconstructing shape in a fresh session." Trigger count: **1** (S2980). Watch for second walk.

---

## Sample findings (pre-T1 SIGN, real corpus)

### Buildable tab distribution (7d, before code)

| Metric | Value | Notes |
|---|---|---|
| total_scanned | 71 | Same 7-day corpus as S2978+S2979 |
| total_survived (Buildable) | 5 | Unchanged shape |
| Buildable `so_what` distribution | research=2, watch=2, build/trade=1 | **0 pure `build` cards** — Chris's complaint validated |
| Investable pattern_type distribution | trend_emergence=19 (66%), opportunity_window=4, demand_spike=4, others=2 | Overwhelmingly watch-class |

### Per-card evidence source distribution (first 5 Buildable, before code)

| Card | Evidence sources (before) | Top source % | Diagnosis |
|---|---|---|---|
| Claude, Code knowledge gap | `{Bluesky:7}` | **100%** | Bluesky row had 7+ items; saturated MAX before other rows touched |
| Claude, Code emerging trend | `{Bluesky:7}` | **100%** | Same shape |
| Chatgpt, Openai opportunity window | `{TechCrunch:4, VentureBeat:1, TheVerge:2}` | 57% | TheVerge/TechCrunch rows walked first |
| Galaxy, Samsung emerging trend | `{ArsTechnica:4, TheVerge:3}` | 57% | Two rows saturated MAX; 3 rows never touched |
| Christopher, Nolan demand spike | `{Polygon Gaming:5, Variety:2}` | 71% | Polygon Gaming row walked first with 5+ items |

### Source-breakdown vs actual row-source distribution (root-cause probe)

| Cluster | source_breakdown | spider_data_ids rows | evidence sources (before) |
|---|---|---|---|
| Claude, Code knowledge gap | 3 keys | 3 rows, 3 distinct sources | **7 items all from ONE row** |
| Chatgpt, Openai opportunity window | 4 keys | 4 rows, 4 distinct sources | 3 sources present but 1 dominates |

**Root cause locked at pre-code phase:** the extractor's `for row in ...: for item in row.raw_data['items']: ...` loop stopped at MAX=7 based on item count, not row count. A single high-item row saturated the buffer. Round-robin at the ROW level (one item per row per pass) fixes it — sample verified this would produce 3+2+2 distribution for the (7-item bluesky + 3-item kickstarter + 2-item producthunt) shape.

---

## Shipped changes (PR #3615, merge SHA `fb2dffe99`)

### `core/services/theme_signals_service.py` (185-line delta)

- **New helper `_normalize_row_items(row, items, max_items)`** — replaces the old `_extract_evidence_from_row_items`. Returns a fresh per-row normalized list capped at `max_items` (was: appended to a shared `out` list, breaking encapsulation).
- **New helper `_round_robin_across_row_buckets(row_buckets, max_total)`** — pure function; interleaves one item per non-empty bucket per pass until `max_total` filled or all empty. Preserves within-bucket walk order. Deterministic across runs.
- **New helper `_build_row_buckets_in_cluster_order(spider_data_ids, row_by_id, max_items)`** — iterates `spider_data_ids` list explicitly (not queryset iteration) so row order is deterministic per Rigby T1 F-BLOCKER. Applied identically in both `extract_evidence_from_cluster` (single) and `_prefetch_evidence_for_clusters` (batch) so behavior can't drift.
- **New `_PATTERN_TO_ACTION` map (10 entries)** — canonical 3-value enum (`build | research | watch`) per spec §Mapping. Collapses `build/trade → build` (opportunity_window) and `trade → watch` (market_movement). Replaces the prior 5-value `_SO_WHAT_ACTION` dict (dead code removed).
- **New `pattern_type_to_action(pattern_type)` public helper** — one source of truth; used by both `cluster_to_card` (card contract) and `get_theme_signals` (build_only filter).
- **`cluster_to_card`** — field rename `so_what` → `action` (Chris D-verdict: clean rename, no dual-emit).
- **`get_theme_signals`** — new `build_only: bool = False` param. Filter applied AFTER route + gate pass, BEFORE `limit_c` cap. New `gate_reasons.build_only_filtered` counter always present in payload (0 when filter off).
- **Payload** now emits `build_only` boolean echo.

### `core/views_theme_signals.py` (17-line delta)

- New `_parse_bool` helper accepts `true`/`1`/`yes`/`on` case-insensitive.
- Passes `build_only` query param through to `get_theme_signals`.
- Endpoint docstring updated with all three spec deliverable IDs (63ec4d1d / c4602ccd / f3cc9499).

### `frontend/src/components/theme-signals/ThemeSignalCard.tsx` (32-line delta)

- New `ThemeSignalAction` TS type (`'build' | 'research' | 'watch'`).
- `ThemeSignalCardData.so_what: string` → `ThemeSignalCardData.action: ThemeSignalAction`.
- `SO_WHAT_STYLE` (5 entries) → `ACTION_STYLE` (3 entries): build=emerald, research=blue, watch=slate.
- Chip render `card.so_what` → `card.action`.

### `frontend/src/pages/workspace/tabs/theme-signals/ThemeSignalsTab.tsx` (122-line delta)

- New `buildOnly` local state, default false.
- `effectiveBuildOnly = activeTab === 'buildable' && buildOnly` — toggle only meaningful on Buildable tab (Investable dominated by watch/research; toggle would filter to ~0).
- `queryKey` now includes `effectiveBuildOnly` — auto-refetches on toggle.
- `signalsApi.themeSignals` call now passes `build_only: effectiveBuildOnly || undefined` — avoids `build_only=false` query noise.
- Inline `All | Build-only` toggle group next to sub-tab switcher; only renders when `activeTab === 'buildable'`. Uses `role="group"` + `aria-pressed` for a11y.
- Empty-state message now branches on `effectiveBuildOnly` — includes a "switch to All" inline button.
- Gate-stats debug panel shows `Build-only filtered` count when filter is on.

### `frontend/src/lib/api.ts` (3-line delta)

- `themeSignals` params extended with `build_only?: boolean`.

### `core/tests/test_theme_signals.py` (264-line delta — +24 net new tests)

**CardShapeTests additions:**
- Updated `test_so_what_action_mapped_from_pattern_type` → `test_action_mapped_from_pattern_type` (asserts opportunity_window collapses to `build`).
- New `test_card_contract_does_not_emit_so_what` (Chris D-verdict regression guard).
- New `test_action_defaults_to_watch_for_unknown_pattern_type`.

**ThemeSignalsEndpointTests additions:**
- Updated `test_endpoint_returns_payload_shape` to include `build_only` in expected keys.
- New `test_endpoint_accepts_build_only_query_param` (verifies echo + `build_only_filtered` counter present).

**New `PatternToActionMappingTests` (7 tests):** all-10-canonical, opportunity_window→build, market_movement→watch, knowledge_gap→research, user_need→build, trend_emergence→watch, unknown→watch fallback (empty + None variants).

**New `RoundRobinBucketTests` (7 tests):** interleaves-two-full-buckets, preserves-within-bucket-walk-order, respects-max-total-cap, drains-remaining-when-one-empties, stable-across-runs, empty-buckets-returns-empty, single-bucket-behaves-like-pass-through.

**New `EvidenceDiversificationE2ETests` (3 tests):** multi_row_cluster_diversifies_evidence (exact 8+3+2 live failure shape → 3+2+2 output distribution), single_source_cluster_returns_full_evidence (round-robin degrades gracefully to pass-through), row_iteration_order_follows_spider_data_ids (Rigby T1 F-BLOCKER regression guard).

**New `BuildOnlyFilterTests` (4 tests):** default_returns_both_build_and_research, build_only_true_returns_only_build_cards, build_only_records_filtered_count, build_only_false_matches_default.

**Total:** 106/106 tests pass (was 82 baseline).

---

## SIGN cycle log

### T1 SIGN (with pre-code sampling findings + zoom-out ask)

Routed to Rigby with: (a) pre-code sample findings (per-card evidence source distribution + root-cause probe), (b) full implementation plan (backend + frontend + tests), (c) one open decision routed to Chris with plain-english framing (rename vs dual-emit), (d) EXPLICIT verify instructions (specific file/line ranges to read), (e) zoom-out ask (over-fitting to n=5 corpus? row-level vs source-level round-robin? coupling risk?).

Rigby T1 verdict: **AGREE overall, 2 F-BLOCKERS.**

**F-BLOCKER 1 (deterministic row ordering):** flagged that Django `filter(id__in=…)` does not guarantee row ordering; asked me to iterate rows in explicit `spider_data_ids` order in BOTH extraction paths. Correctly caught — my plan said "preserve current DB-fetch order" which was underspecified. **Applied** via new `_build_row_buckets_in_cluster_order` helper.

**F-BLOCKER 2 (round-robin in BOTH paths):** flagged that both `extract_evidence_from_cluster` (single) and `_prefetch_evidence_for_clusters` (batch) needed the same diversification to prevent future drift. **Applied** — both paths share the same three-step recipe (`_build_row_buckets` → `_round_robin` → `sort_by_relevance`).

**Soft-blocker (dual-emit):** flagged that "grep says no external consumers" isn't proof of no external consumers (hypothetical mobile client, external API caller). Recommended dual-emit for one transition PR as safer mitigation. **Escalated to Chris** with plain-english framing.

Tool_runs: 4 substantive `repo_tool.read_file` invocations. Zero rubber-stamps confirmed.

Rigby zoom-out answers: row-level round-robin is correct unit given the actual bug shape; source-level grouping would risk mixing semantics; coupling risk minimal (presentation-only change).

### Chris D-verdict (rename vs dual-emit)

Ratified **Option 1 (clean rename)** — rationale: "we control all known call sites, platform is pre-prod, no credible external client risk for theme-signals right now." Added explicit regression test ask: "assert `so_what` is not present in serialized card payload." **Applied** — `test_card_contract_does_not_emit_so_what`.

### A2 SIGN (with F-BLOCKER verification + zoom-out ask)

Routed to Rigby with: (a) shipped diff stat, (b) test results (106/106), (c) F-BLOCKER verification asks with exact file/line pointers ("read theme_signals_service.py lines 218-280 and confirm both paths now iterate spider_data_ids"), (d) 4 post-implementation asks (mapping correctness, filter placement, test thoroughness, UI toggle scoping), (e) zoom-out ask (coupling / defaults / missed callers / fresh-eyes pushback).

Rigby A2 verdict: **AGREE, no F-BLOCKERS, no soft-blockers.**

Both T1 F-BLOCKERS verified resolved with tool_run evidence:
- F-BLOCKER 1: cited `_build_row_buckets_in_cluster_order` line 299-318, confirmed both `extract_evidence_from_cluster` (line 353) and `_prefetch_evidence_for_clusters` (line 387-389) use it.
- F-BLOCKER 2: confirmed shared 3-step recipe in both paths.

All 4 post-implementation asks verified:
- Mapping matches spec (all 10 pattern_types → canonical enum).
- `build_only` filter applied at correct point (after route+gate, before limit).
- Tests thorough (one optional post-merge add flagged: "bad-then-good row edge case").
- UI toggle only renders on Buildable tab; queryKey correctly includes `effectiveBuildOnly`.

Tool_runs: 5 substantive `repo_tool.read_file` invocations. Zero rubber-stamps confirmed.

Rigby zoom-out answers: coupling risk low (presentation-only); Build-only default `false` is correct ("All is discovery, Build-only is power filter — toggle makes disagreement explicit and cheap"); `so_what` removal risk minimal within inspected code.

### Chris pause-pre-cascade + workflow-codification interrupt

After A2 SIGN passed, Chris interrupted with "Do not run cascade until you check in with me" then followed with the workflow-codification opportunity. Routed him a **per-PR summary + explicit "still open before close" checklist** (per feedback_per_pr_summary_signals_close_readiness) + asked ship-order preference. Chris ratified Option 1 (ship then codify) + granted merge permission.

### Chris D-verdict (workflow codification)

After Rigby drafted deliverable e8429049-… and I appended 3 refinements (Verified Premises + Artifact Map in Phase 2, self-execute-vs-route-to-Rigby heuristic in Phase 1, S2980 turn-by-turn timeline), Chris ratified: **initiative-creation default = "optional for single PR"** (as drafted); **defer formal Playbook amendment ratification** (as Rigby recommended); **close cascade** (proceed).

---

## Live-verify (post-merge, at HEAD `fb2dffe99`)

Django `Client(HTTP_HOST='localhost').force_login(chris).get('/api/theme-signals/', ...)`:

| Probe | Result |
|---|---|
| Buildable default status / cards / scanned | 200 / 5 / 71 |
| Buildable + build_only=true status / cards / filtered_out | 200 / **1** / **4** |
| Investable status / cards | 200 / 20 |
| Card contract has `action` field | ✅ (all cards) |
| Card contract has `so_what` field | ❌ (removed — Chris regression guard verified live) |
| `action` distribution on first 5 Investable | build=2, watch=3 (opportunity_window → build, trend_emergence → watch — correct) |
| Only Buildable Build-only survivor | `"Chatgpt, Openai opportunity window"` — pattern=opportunity_window → action=build |
| `gate_reasons.build_only_filtered` when off | 0 (default) |
| `gate_reasons` keys include `build_only_filtered` | ✅ |

### Before/after diversification (all 5 Buildable cards)

| Card | S2979 evidence | S2980 evidence | Improvement |
|---|---|---|---|
| Claude, Code knowledge gap | `{Bluesky:7}` (100%) | `{Bluesky:3, Product Hunt:4}` | 1→2 sources, top 100%→57% |
| Claude, Code emerging trend | `{Bluesky:7}` (100%) | `{Bluesky:3, Product Hunt:4}` | 1→2 sources, top 100%→57% |
| Chatgpt, Openai opportunity window | `{TC:4, VB:1, TheVerge:2}` (57%) | `{TC:2, VB:1, TheVerge:2, Securityweek:2}` | 3→4 sources, top 57%→29% |
| Galaxy, Samsung emerging trend | `{AT:4, TheVerge:3}` (57%) | `{NewsAPI:1, TheVerge:2, Lifehacker:2, WIRED:1, AT:1}` | 2→5 sources, top 57%→29% |
| Christopher, Nolan demand spike | `{PG:5, Variety:2}` (71%) | `{PG:2, Variety:3, TC:2}` | 2→3 sources, top 71%→43% |

**Every one of the 5 Buildable cards improved diversification.** Chris's complaint fully resolved on current corpus.

**Not verified this session (Chris optional follow-up):** browser DOM smoke on `/workspace?tab=intelligence&sub=theme-signals` — click one Bluesky evidence row, one Reuters row; verify `All | Build-only` toggle visually flips card list. Django Client can't exercise DOM state.

---

## Workflow-shape source deliverable (`e8429049-300f-4725-8d02-a79c285ed720`)

Full body: **18,716 chars**, category `engineering_spec`, type `document`, pinned, workspace Donkey Betz (`b4503364-…`).

### Structure

1. **Purpose + Governing feedback references** (10 feedback memory pointers all cited).
2. **Roles contract** — Chris (D-verdicts), Claude (implementation), Rigby (independent verifier).
3. **Phase 0-9 recipe:**
   - Phase 0: Session open / orientation
   - Phase 1: Spec receipt + pre-code discovery (with routing heuristic: Claude self-executes vs routes to Rigby)
   - Phase 2: Draft implementation plan (with mandatory "Verified Premises" + "Artifact Map" sections)
   - Phase 3: T1 SIGN request (Claude → Rigby)
   - Phase 4: T1 verdict processing (Rigby → Claude)
   - Phase 5: Joint recommendation to Chris (Claude + Rigby aligned)
   - Phase 6: Implement (Claude executes)
   - Phase 7: A2 SIGN request (Claude → Rigby)
   - Phase 8: Ship (merge + recycle + live verify)
   - Phase 9: Close cascade (only on Chris signal)
4. **Initiative + deliverable usage** — Chris ratified: initiative optional for single PR; mandatory when work spans >1 PR/session.
5. **SIGN templates** — T1 request/response + A2 request/response (copy/paste).
6. **Common failure modes** — 5 patterns with prevention notes.
7. **Friction + tribal knowledge zoom-out** — biggest silent-absorbed friction, what MUST be in eventual Playbook amendment.
8. **S2980 as example timeline** — 30-turn table (actor / phase / action) + metrics (turns-to-first-code, tool_runs count, F-BLOCKER cycles).

### Chris ratification status

- **Initiative-creation default:** ratified as "optional for single PR" (as drafted).
- **Formal Playbook amendment:** **deferred to a future session** — Rigby's recommendation ("this is meta-process; run the formal T1/T2/T3/T4 SIGN + workspace amendment envelope + D1..D7 verdict cycle with fresh orientation") accepted.

**S2981 (or later) opens with the option to run the formal ratification cycle on this deliverable.**

### Rigby optional additional refinement (not blocking)

Rigby suggested expanding the "Common failure modes" section with more specific tool-level mitigations (`make recycle-all` + `ops_tool.version` check + dual-emit-escape-hatch monitoring). Non-blocking — can be folded into the formal amendment cycle when it runs.

---

## Candidate folds surfaced (NOT codified)

Continuation of S2979 ledger; only new/updated entries listed:

4. **"Deliverable-as-spec first walk validates the workflow reframe."** Trigger count: **11** (S2969–S2980). Eleven-trigger corpus.
9. **"Rigby-drafted spec deliverable is a first-class origination path."** Trigger count: **7** (S2973, S2974, S2975, S2977, S2978, S2979, **S2980**). Seven-walk corroboration.
11. **"Sample-before-plan cuts T1 revision cycles to zero."** Trigger count: **6** (S2974, S2975, S2977, S2978, S2979, **S2980**). S2980: pre-plan Django shell sampling isolated root cause (item-level walk bias) vs my initial hypothesis (row-level walk bias); T1 asked the right questions because plan was grounded in real data. Sixth-walk corroboration.

**NEW at S2980:**

21. **"Chris pause-pre-cascade lets meta-work happen while both agents are oriented — cheaper than reconstructing shape in a fresh session."** Trigger count: **1** (S2980 — Chris interrupted after A2 SIGN passed, before I ran cascade; workflow-shape codification happened in 5 extra turns with both agents still oriented on the flow). Flag: watch for second walk. If it walks again, this becomes a Playbook rule candidate — "Chris interrupt right after A2 SIGN is a valid meta-work insertion point, not a workflow violation."

22. **"Workflow codification lives as a workspace deliverable BEFORE it becomes a Playbook amendment."** Trigger count: **1** (S2980 — deliverable e8429049 created as SOURCE for future formal amendment cycle). Flag: the artifact class "workflow-shape source deliverable" is distinct from "spec deliverable" and from "ratification record." Watch for second walk (next session's Playbook amendment cycle will reference e8429049 as input).

23. **"Rigby's own memory-limit heuristic drives artifact consolidation guidance."** Trigger count: **1** (S2980 — Rigby's draft explicitly recommended `deliverable_tool.append` over spawning many small deliverables, citing her memory-store constraints as design pressure). Flag: platform-imposed constraints become process guidance. Watch for second walk.

---

## Substrate ledger updates (deferred; requires separate arc)

- **Rigby Tool Gap Ledger candidate (rolled forward from S2979):** `remember_tool` "Memory limit reached (200 items)" while current_count=1753 — still unresolved. S2980 didn't hit this path but Rigby cited memory constraints when recommending the `deliverable_tool.append` pattern, suggesting the underlying issue is still relevant. Belongs on Donkey Betz workspace `b4503364-…` per `feedback_rigby_tool_gap_ledger`.

- **Playbook amendment cycle input:** deliverable `e8429049-…` is the source. When Chris opens the formal cycle, run T1/T2/T3/T4 SIGN + workspace amendment envelope + D1..D7 verdict per v0.8.0 shape. Target chapter: Ch 6 Governance (extends PLAYBOOK-6.10.x rules on SIGN discipline / fold-authoring / evidence admission).

---

## Twin-pointer docs card (per feedback_twin_pointer_docs_at_boundaries)

| Artifact | Repo path | Workspace UI |
|---|---|---|
| S2980 handoff | `docs/handoffs/SESSION_2980_THEME_SIGNALS_UX_UPGRADE.md` | n/a — repo-only |
| S2980 spec deliverable | n/a — workspace-only | Donkey Betz `b4503364-…` → deliverable `f3cc9499-9990-4924-81a4-6edba3f1457a` |
| S2980 workflow-shape source deliverable (NEW class) | n/a — workspace-only | Donkey Betz `b4503364-…` → deliverable `e8429049-300f-4725-8d02-a79c285ed720` |
| Shipped code | PR #3615 (merged, branch deleted); HEAD `fb2dffe99` | https://github.com/clwest/donkey-betz-platform/pull/3615 |
| Support conversation | n/a — chat-only | `pa-323b267495764a04` |
| Prior session | `docs/handoffs/SESSION_2979_THEME_SIGNALS_EVIDENCE_FIRST.md` | n/a |
