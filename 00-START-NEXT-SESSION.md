# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2863 CLOSE → HF Hub API sort=downloads shipped (2026-07-21; picks up as S2864) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2863 close).** Chris-selected S2863 slate #1 (Rigby Tool Gap Ledger #13, Rigby-recommended at S2862 close) shipped as **one PR / one commit**:

- **PR #3345** `90c293aee` — S2863 slate #1: `sort=trending` → `sort=downloads` at all 3 HuggingFaceSpider sites
  - `ai_core/spiders/specialized/huggingface_spider.py:87,144,200` — sort-param swap, 2-line explanatory comment at each site referencing this ledger entry + live-verified date.
  - Root cause: HF Hub API `sort=trending` returns HTTP 400 on `/api/models`, `/api/datasets`, `/api/spaces` (verified live 2026-07-21). Spider was catching the exception and falling back to `_get_curated_topics()` — never hitting the live API.
  - Fix: `sort=downloads` returns HTTP 200 with populated items. Compositional close of the S2862 arc (S2862 fixed routing to the class path; S2863 fixed the actual API call).
  - 7 new pytest cases (`test_s2863_huggingface_sort_downloads.py`) across 3 classes: `SortParamRegressionTests` (3, mock cached_get), `SourceCodeGuardTests` (1, regex source-guard), `LiveHubAPIContractTests` (3, real HF API, network-required, skip on failure).
  - Post-recycle E2E (live HF Hub API, `max_results=20`): **20/20 items** with populated title+description, **2827 chars** extractable text (vs 588 curated-fallback at S2862 close; 0 pre-S2862). Top model: `sentence-transformers/all-MiniLM-L6-v2` · 241M downloads.

**Working loop validated at S2863:**
- 1-turn pre-code SIGN (Q1 F-BLOCKING delegated to Claude live-curl per PA tool-surface limit — this itself became Ledger #15; Q2–Q4 AGREE-TO-BUILD grounded via `repo_tool`; Q5 zoom-out AGREE)
- 1-turn post-code SIGN (AGREE-TO-SHIP on all 5 F-BLOCKING Qs, grounded via `repo_tool.read_file` on both changed files + downstream ordering search — 0 coupling found)
- Post-recycle live E2E confirmed HF spider run yields 20 live items at 100% populated title+description

**Rigby Tool Gap Ledger updates (via Rigby PA tool per `feedback_rigby_writes_workspace_deliverables`):**
- Entry #13 (HF sort=trending → HTTP 400) moved to Shipped, status `shipped_in_pr_3345`, PR/commit/date embedded.
- **NEW open entry #14:** `core/views_spider_intelligence.py:1217` HF description workaround becomes safe no-op on live-item path. Cleanup candidate; ~10–15 lines. Status `deferred_from_s2863_per_rigby_q5b`.
- **NEW open entry #15:** PA tool-surface capability gap — no raw HTTP fetch capability; `intelligence_tool.search` + `web_search` return `synthetic_fallback`, blocking pre-code API contract checks. Directly hit at S2863 Q1. Status `open`.

**Session pin `pa-687d4e1e220f4f11` (labeled `s2863-hf-api-sort`) RETIRES at S2863 close.** Fresh mint required at S2864 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2864 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-687d4e1e220f4f11` retired at S2863 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2864-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2864

Per `feedback_engineering_bias_over_audit`, list net-new first.

0. **NEW at S2863 close — Rigby Tool Gap Ledger #14 (Rigby-recommended for S2864 slate #1):**
   - **`views_spider_intelligence.py:1217` HF description-reconstruction workaround** — now safe no-op on live-item happy path (verified post-code SIGN Q3). Cleanup pass ~10–15 lines. Small blast radius (1 file). Closes the S2862+S2863 arc completely. Very tight trigger.

1. **NEW at S2863 close — Rigby Tool Gap Ledger #15** — PA-surface capability gap: no raw HTTP fetch capability. `intelligence_tool.search` + `web_search` return `synthetic_fallback` for URL queries. Every future API-contract check has to route via Claude+curl. ~1–2 hr to add a minimal `web_fetch_tool` that returns status + JSON/text. Not urgent, but keeps forcing off-tool workarounds.

2. **Ledger #11 — Durable non-cascading audit table for deletes** — S2860 v1 uses `logger.warning('[DELIVERABLE_DELETE]')` as the audit trail because `DeliverableEvent` CASCADEs. A dedicated append-only DB table (e.g., `DeliverableDeleteAudit`) would give durable structured queries. Deferred; awaits compliance/audit trigger or genuine forensic need.

3. **`simulate_enforcement` auto-clear-after-N-seconds** (S2857 first-trigger fold) — currently `dry_run=false` writes flags that persist until operator calls `clear_freeze`/`clear_downgrade`. Consider optional `auto_clear_after_seconds` param. Deferred — awaits explicit ask.

4. **`enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger) — de-duplicate the 4-item action-type list between `td_handlers_ops.py:4362` and `ops_autopilot/budget.py`. ~1 hr refactor. Not urgent until a fifth type is added.

5. **`actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, 1st trigger — MIGRATION required). Deferred until schema-migration budget opens.

6. **`EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger). Deferred — awaits second independent trigger before Playbook amendment.

7. **`list_caps include_defaults=true` remaining perf costs** (S2858 concern 5, 1st trigger). Not urgent until fleet size makes it a slow ticket.

8. **Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859 1st trigger observed — needs 2nd/3rd independent trigger). Governed change per Playbook §14.2 threshold.

9. **Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"** — deeper substrate driver behind repeated exemption pressure. Requires UI/product decision. Watch for 3rd/4th independent trigger.

10. **Fold C from S2861 close: shared JSONField projection helper** — extract `project_jsonfields(row, selected_paths, allowed_prefixes, cap)`. First trigger observed at S2861. Needs second tool trigger before build.

11. **Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params** — `autopilot_tool.history` now has 3 opt-in payload knobs. If operator UI hides schema helptext, advanced params ship "invisible."

12. **Q5.a bimodal collector architecture** (S2862 first trigger) — URL-path via `collect_spider_data_sync` + `normalize_item` vs spider-class path via `registry.get_spider_class` + `_run_spider_adapter`. When a spider exists in both, URL path silently wins. Only 2/54 URL-path spiders currently drop (huggingface removed S2862; openmeteo still open). `future_trigger`.

13. **Q5.b normalize_item ownership principle** — "when a spider has a class, prefer class-owned transformation; reserve `normalize_item` for URL-only sources." Design principle logged; no code action yet. `future_trigger`.

14. **openmeteo → SignalCluster drop (fold-carry from S2862)** — only other URL-path spider dropping to 0 text (numeric weather forecast). Fixing routing alone wouldn't help; needs product decision on whether we want weather signals + what synthesis rules.

15. **Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855: `model_kind` dimension, `EMBEDDING_COSTS`+`MODEL_PRICES` unification, `pricing_catalog_version` field on LLMCallLog, LLMCallLog↔CostTracking schema-level provenance column.

16. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. See A4 Constraints below for the full capability list after S2863.

### What's forbidden at S2864 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Multi-source `source_spider` filter (Ledger candidate; ~1 hour)
- SignalCluster naming rewrite (Ledger candidate; ~1 day)
- `spider_status_tool.search` empty preview field (Ledger #2; ~2 hours)
- `spider_status_tool.list` pagination (Ledger #1; ~2 hours)
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2863 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`. S2857: operator can now verify enforcement without touching real spend via `simulate_enforcement`. S2858: post-clear re-flag likelihood inline on clear_* responses; list_caps read surface no longer degrades linearly with workspace count. S2859: `deliverable_tool.create` with `deliverable_type='ratification_record'` lands with verbatim title + no spurious diagnostic mark. S2860: Rigby can permanently delete deliverables directly via `deliverable_tool.delete` — two-factor gated, published-guarded, cascade-previewed, WARNING-audit-logged. S2861: Rigby can trim `autopilot_tool.history include_evidence=true` responses to specific top-level keys via `selected_fields=["evidence.<key>", "result.<key>"]`. S2862: huggingface → SignalCluster drop resolved — HF spider runs now produce extractable text; A4 AI/ML signal-cluster discovery restored (curated fallback). **S2863: HuggingFaceSpider now hits the LIVE HF Hub API — 20/20 items with populated title+description, 2827 chars extractable text (5x the curated-fallback payload) — A4 `intelligence_tool.signal_clusters source_spider='huggingface'` now returns live-data-backed AI/ML clusters, not curated topics.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail — cycle-triggered vs operator-triggered attributed correctly + auto_events_count vs operator_events_count now visible per-workspace in the fleet report; (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total — now cleanly filtered to enforcer-forced downgrades only; (i) all billing paths route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls priced at effective_model rates; (j) analytics-plane cost attribution correct; display fallbacks use canonical rates with explicit `estimated: true` flag; embedding pricing SoT preserved; (k) autopilot audit history (`autopilot_tool.history include_evidence=true`) surfaces evidence + result JSONField values inline for operators inspecting trigger / actor_user_id / reason; (l) operators + demo audiences can trigger the freeze + downgrade enforcer against a synthetic spend value via `workspace_budget_tool.simulate_enforcement`; (m) operators can inspect post-clear re-flag likelihood inline on clear_freeze/clear_downgrade responses; (n) workspace_budget_tool.list_caps read surface no longer degrades linearly with workspace count; (o) governance/ratification records land clean via `deliverable_tool.create` (deliverable_type=ratification_record); (p) hard delete of a deliverable is a first-class operator action via `deliverable_tool.delete`; (q) `autopilot_tool.history include_evidence=true` supports `selected_fields=["evidence.<key>", "result.<key>"]` for top-level JSON projection; (r) HuggingFace AI/ML signals enter SignalCluster aggregation — 22 rows/7d that previously dropped to 0 signals now yield 1+ signal per run with entity_tokens matching AI/ML domain; **(s) `intelligence_tool.signal_clusters source_spider='huggingface'` returns LIVE Hub API data (not curated fallback) — 20 items/run, 100% with populated title+description, top items reflect real-world downloads (241M+ for top model).**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2863 close — what shipped (one PR, one commit + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3345** `90c293aee` — S2863 slate #1: `sort=trending` → `sort=downloads` at 3 sites + 7 pytest cases
- **PR `<this docs cascade>`** — S2863 handoff + 00-START-NEXT-SESSION refresh + pa_local.sh pin bump

**Workspace canonical:** Rigby Tool Gap Ledger #13 marked shipped (`shipped_in_pr_3345`); new open entries #14 (view-layer workaround cleanup) + #15 (raw HTTP fetch tool-surface gap) added. Ledger updated by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables`.

**Runtime impact:**
- huggingface spider hits the live HF Hub API instead of curated fallback.
- E2E verified: 20/20 items with populated title+description; 2827 chars extractable text (~5x the curated-fallback payload from S2862 close); category distribution 10 models + 5 datasets + 5 spaces.
- A4 `intelligence_tool.signal_clusters source_spider='huggingface'` restored to live-data-backed AI/ML discovery.

**Not shipped at S2863 close (deferred to S2864 or later):**
- Ledger #14 view-layer HF workaround removal (Rigby-recommended next-slate lead)
- Ledger #15 PA raw HTTP fetch tool capability
- openmeteo signal fix (product decision)
- All prior deferred items from S2862/S2861/S2859/S2858/S2857/S2856

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2863)

See:
- **S2863 handoff (current):** `docs/handoffs/SESSION_2863_HF_HUB_API_SORT_DOWNLOADS.md`
- **S2862 handoff:** `docs/handoffs/SESSION_2862_HUGGINGFACE_SIGNAL_EXTRACTION_FIX.md`
- **S2861 handoff:** `docs/handoffs/SESSION_2861_AUTOPILOT_SELECTED_FIELDS_SHIPPED.md`
- **S2860 handoff:** `docs/handoffs/SESSION_2860_DELIVERABLE_TOOL_DELETE_SHIPPED.md`
- **S2859 handoff:** `docs/handoffs/SESSION_2859_DELIVERABLE_TOOL_GOTCHAS_LEDGER_8_9_SHIPPED.md`
- **S2858 handoff:** `docs/handoffs/SESSION_2858_CLEAR_STATUS_CONTEXT_AND_LIST_CAPS_N1_SHIPPED.md`
- **S2857 handoff:** `docs/handoffs/SESSION_2857_SIMULATE_ENFORCEMENT_SHIPPED.md`
- **S2856 handoff:** `docs/handoffs/SESSION_2856_AUTOPILOT_HISTORY_EVIDENCE_AND_ENFORCEMENT_SPLIT_SHIPPED.md`
- **S2855 handoff:** `docs/handoffs/SESSION_2855_PRICING_CANON_PHASE_2A_SHIPPED.md`
- **S2854 handoff:** `docs/handoffs/SESSION_2854_PRICING_CANON_PHASE_1_SHIPPED.md`
- **S2853 handoff:** `docs/handoffs/SESSION_2853_W2_3_2_DOWNGRADE_SAVINGS_SHIPPED.md`
- **S2852 handoff:** `docs/handoffs/SESSION_2852_LIST_CAPS_AUTH_TIGHTENED.md`
- **S2851 handoff:** `docs/handoffs/SESSION_2851_A1_W2_3_1_ENFORCEMENT_REPORT_SHIPPED.md`
- **S2850 handoff:** `docs/handoffs/SESSION_2850_A1_W2_ENFORCEMENT_CORRECTNESS_LEG.md`
- **S2849 handoff:** `docs/handoffs/SESSION_2849_A1_W2_DEFAULTS_BACKFILL_SHIPPED.md`
- **S2848 handoff:** `docs/handoffs/SESSION_2848_A1_W1_5_DOWNGRADE_TIER_SHIPPED.md`
- **S2847 handoff:** `docs/handoffs/SESSION_2847_A1_W1_PHASE3_SHIPPED.md`
- **S2846 handoff:** `docs/handoffs/SESSION_2846_A1_W1_PHASE1_PHASE2_SHIPPED.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`

For older session history (S1-S2845), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
