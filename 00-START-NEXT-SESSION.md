# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2872 CLOSE → Ledger #22b sweep shipped (2026-07-21; picks up as S2873) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2872 close).** Rigby Tool Gap Ledger #22b (broader `raw_data_dict` sweep) — Chris ratified at S2872 open while doing his own character-os repo dive; Claude+Rigby executed:

- **PR #3365** `a54998be4` — S2872 slate (30 files, +308/-46)
  - **44 crash-risk callsites migrated** across 30 files from `raw = X.raw_data or {}` → `raw = X.raw_data_dict`. Old pattern silently failed on list-form LegacySpiderData rows: list is truthy → passes `or {}` guard → `.get()` crashes with AttributeError. Files: 12 agent + 6 service + 3 tasks_* + 2 views + 1 model + 1 mgmt cmd + 3 core/tasks.
  - **Rigby Q4 zoom-out fold shipped:** `LegacySpiderData.raw_data_dict` property now emits rate-limited debug telemetry on fallback (first hit + every 100th per spider_name). Trades silent-data-drop for observable-schema-drift. Helper `_record_non_dict_raw_data` + counter `_NON_DICT_RAW_DATA_COUNTER` at `core/models_unified_system.py:29-49`.
  - New test file `core/tests/test_s2872_ledger_22b_raw_data_dict_sweep.py` — 11 tests across 3 test classes (migrated call-paths list-form + dict-form correctness + telemetry).
  - Combined regression suite (S2869 + S2870 + S2871 + S2872): **60/60 pass**.

**Scope discipline (Rigby Q1 F-AGREE):**
- **Category A (crash-risk):** unguarded `raw = X.raw_data or {}` on LegacySpiderData readers → **44 sites migrated** ✅
- **Category B (already `isinstance(..., dict)`-guarded):** ~8-10 sites → **SKIPPED** (cosmetic churn deferred). Files: `td_handlers_content.py`, `tasks_content.py`, `views_spider_data.py`, `views_spider_dashboard.py`, `marketplace_discovery_service.py`, `platform_intelligence_briefing.py`, `spider_intelligence.py`, `living_project_service.py`, `content_diversity_orchestrator.py`.
- **Category C (different model):** `persistence.models.SpiderData`, `Opportunity`, etc → **SKIPPED** (belongs to wish-list #2 + #3).

**Discovery arc — 2 SIGN cycles:**
- Pre-code SIGN: Rigby F-AGREE with 2 folds — (a) Q2 caution triggered narrow re-sweep, expanding scope from Claude's initial 8-site estimate to 44 confirmed sites; (b) Q4 zoom-out surfaced telemetry addition (biggest fold — reshaped property design).
- Post-code SIGN: F-AGREE all 4 questions with live tool_runs evidence — `orm_inspect_tool` confirms LegacySpiderData reads work (15,618 rows, dict-form loads clean); `repo_tool.search` confirms remaining `raw_data or {}` hits are ONLY in Category B/C/write-path/tests (no unguarded reader regressions).

**Working loop observations at S2872:**
- `feedback_verify_rigby_tool_runs_before_trusting_sign` fired 2×.
- `feedback_zoom_out_ask_per_rigby_sign` yielded 2 usable folds — both applied.
- `feedback_claude_rigby_agree_first_chris_yes_no` — presented Chris one recommendation.
- `feedback_engineering_bias_over_audit` — net-new engineering ship (not audit).
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge (`sha=a54998be4d59, surviving=none`).
- `feedback_read_full_rigby_response_not_just_tail` — initially truncated with `tail -200`; re-fetched for full F-verdict prose.
- Chris redirected mid-session onto character-os Rigby integration (research question grounded in `consult_engine.py` — NOT a scope expansion; no arc opened).
- No candidate lessons for Playbook amendment this session.

**New Rigby-observed tool-surface gaps (candidates for future ledger entries, NOT logged yet — watch for second-trigger):**
1. `orm_inspect_tool` can't JSON-type filter/count JSONField rows (no `jsonb_typeof` predicate). Blocked direct list-form prevalence quantification.
2. `repo_tool.read_file` line caps on large files (e.g. `core/models_unified_system.py` at 554359 bytes returned "file too large" — had to rely on search anchors for verification).

**Rigby Tool Gap Ledger updates (via Rigby PA per `feedback_rigby_writes_workspace_deliverables`):**
- Deliverable ID `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
- **#22b** → `shipped_in_pr_S2872` (44 sites / 30 files / telemetry fold shipped)

**Session pin `pa-de1eb1fdbd3540f3` (labeled `s2872-ledger-22b-raw-data-dict-sweep`) RETIRES at S2872 close.** Fresh mint required at S2873 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

**Character-os Rigby integration research (mid-session, per Chris directive):** DBZ's `/api/pa/chat/` endpoint doesn't recognize `source='character-os-consult-engine'` or context payload (`spokesperson_id`, `workspace_id`). 5 gap tiers identified for future work: (1) caller recognition, (2) panel-shaped response contract, (3) persona translation activation, (4) per-caller tool allowlist, (5) reverse channel. Not opened as an arc under D6 moratorium — parked for post-moratorium consideration.

---

## S2873 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

Wrapper pin rewritten at S2872 close. If needed at S2873 open:

```bash
python manage.py session_lifecycle close --label s2873-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2873

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2872 close — SpiderData (canonical) → orm_inspect allowlist** (wish-list #2 from S2871). ~15 min. High value for cross-checking canonical spider data model when APIs disagree.

2. **NEW at S2872 close — Opportunity → orm_inspect allowlist** (wish-list #3 from S2871). ~15 min. High-value model for revenue-side inspection.

3. **NEW at S2872 close — `orm_inspect_tool` JSONField type predicate** (Rigby-observed gap #1). Would enable direct queries like "count LegacySpiderData rows where raw_data is not a dict" via a `jsonb_typeof`-style predicate. 1st trigger only — watch for 2nd before promoting.

4. **NEW at S2872 close — `repo_tool.read_file` large-file paging** (Rigby-observed gap #2). Currently rejects files >~500KB. Could add pagination or lazy-load semantics. 1st trigger only — watch for 2nd.

5. **Ledger #5 — schema/handler drift detection lint / CI wiring** (~2 hr). Command exists at `core/management/commands/check_pa_tool_drift.py` (S2846-authored, 403 lines) but never wired to CI enforcement. Also worth reconciling pre-existing drift reports before flipping to enforce mode.

6. **Carried from S2872 — Category B cosmetic `raw_data_dict` migration** (~30 min). ~8-10 already-`isinstance(..., dict)`-guarded sites in `td_handlers_content.py`, `tasks_content.py`, `views_spider_data.py`, `views_spider_dashboard.py`, `marketplace_discovery_service.py`, `platform_intelligence_briefing.py`, `spider_intelligence.py`, `living_project_service.py`, `content_diversity_orchestrator.py`. Deferred as cosmetic; consistency-only. Skip unless explicit Chris pick.

7. **Ledger #16 — close-ceremony twin-mirror enforcement gap** (S2863). Ranked fix candidates: (a) explicit close-checklist gate (~15 min); (b) hard-enforce in `session_lifecycle close` — refuse close without both deliverable IDs (~2 hr); (c) nightly audit task for recent handoffs missing mirrors (~1 hr).

8. **Carried — Exemption-list telemetry (Rigby zoom-out from S2868 slate #1)**. Add counts-by-code/type instrumentation for `diagnostic_status='cleared'` so we can detect exemption-list-junk-drawer risk over time. 1st trigger only — watch for 2nd before opening.

9. **Carried — Stale-cleared row GC (Rigby zoom-out from S2868 slate #1)**. Optional sweep for `diagnostic_status='cleared'` rows >180 days old that could be fully NULLed. Deferred until UI clutter becomes real.

10. **Carried — `group_key_note` UX hint on `count_by`** (S2867 Q2 fold). Nice-to-have string like `"FK grouped on attname <field>_id"`. 1st trigger; watch for 2nd.

11. **Carried — High-cardinality guardrail on `count_by`** (S2867 Q5 fold). Optional soft-warning when `total_matching` exceeds a threshold. 1st trigger; deferred until slow-query experience report.

12. **Carried — Per-model `allowed_fields` explicit allowlist on `orm_inspect_tool`** (S2866 fold, still 1st trigger). Mitigates euphemistic-name slip-through class.

13. **Carried — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.** Still 2 independent triggers, not promoted. ~30 min doc/deliverable.

14. **Carried — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate). 1st trigger only from S2864; watch for 2nd/3rd.

15. **Carried — Provider-specific composite additions.** Reactive; watch for new integrations.

16. **Carried — `simulate_enforcement` auto-clear-after-N-seconds** (S2857 fold). Deferred; awaits explicit ask.

17. **Carried — `enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger).

18. **Carried — `actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, MIGRATION required). Deferred until schema-migration budget opens.

19. **Carried — `EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger).

20. **Carried — `list_caps include_defaults=true` remaining perf costs** (S2858, 1st trigger).

21. **Carried — Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859 1st trigger observed; S2868 shipped 4 additions — this is now the 2nd cycle).

22. **Carried — Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

23. **Carried — Fold C from S2861 close: shared JSONField projection helper**.

24. **Carried — Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

25. **Carried — openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

26. **Carried — Middleware `log_injected_params` spec candidate** (S2870 Q6 zoom-out fold). Compare GPT-5.2's function-call payload against operator utterance for un-mentioned filter values; log-only mode first, strip mode later for high-risk tools. Rigby-recommended pattern-checklist framing, not blanket Playbook rule. 1st trigger only from S2870 — watch for 2nd.

27. **Carried — Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

28. **Carried — A4 warm-up under ratified constraints** — S2846 6-line block still in force. A4 capabilities extended at S2871: see A4 Constraints below.

29. **Carried — Character-os Rigby integration (5-gap analysis from S2872 mid-session, D6 moratorium hold)** — DBZ's `/api/pa/chat/` endpoint doesn't recognize `source='character-os-consult-engine'` / `spokesperson_id` / `workspace_id`. Cheapest safety wins: (a) caller recognition (~30 min), (d) per-caller tool allowlist (~1 hr). Biggest UX wins: (b) panel-shaped response contract (~1-2 hr), (c) persona translation activation (~1 hr). Largest scope: (e) reverse channel (`character_os_tool` in Rigby's surface). Parked under D6 moratorium; unlock requires Chris directive.

### What's forbidden at S2872 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2871 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`. S2857: operator can now verify enforcement without touching real spend via `simulate_enforcement`. S2858: post-clear re-flag likelihood inline on clear_* responses; list_caps read surface no longer degrades linearly with workspace count. S2859: `deliverable_tool.create` with `deliverable_type='ratification_record'` lands with verbatim title + no spurious diagnostic mark. S2860: Rigby can permanently delete deliverables directly via `deliverable_tool.delete` — two-factor gated, published-guarded, cascade-previewed, WARNING-audit-logged. S2861: Rigby can trim `autopilot_tool.history include_evidence=true` responses to specific top-level keys via `selected_fields=["evidence.<key>", "result.<key>"]`. S2862: huggingface → SignalCluster drop resolved — HF spider runs now produce extractable text; A4 AI/ML signal-cluster discovery restored (curated fallback). S2863: HuggingFaceSpider now hits the LIVE HF Hub API — 20/20 items with populated title+description, 2827 chars extractable text — A4 `intelligence_tool.signal_clusters source_spider='huggingface'` now returns live-data-backed AI/ML clusters, not curated topics. S2864: view-layer HF workaround removed after backfill enriched 460 pre-S2862 items; A4 feed queries for `source=huggingface` no longer require spider-name string-matching at read time. S2865: Rigby can now raw-HTTP GET/POST arbitrary http/https URLs via `web_fetch_tool` — closes the twice-bit F-DELEGATED verification gap. S2866: Rigby can now inspect any of 8 allowlisted DB models directly via `orm_inspect_tool` — closes the S2845-class false-negative gap where a tool surface reports 'no data' but rows exist under a different filter path. S2867: Rigby can now aggregate rows by any allowlisted field (single-value / FK-attname / DateTimeField-auto-day-bucket) via `orm_inspect_tool action='count_by'`. S2868: (1) 4 additional deliverable_types exempt from `missing_initiative_id` diagnostic — Rigby's own Tool Gap Ledger (engineering_backlog) no longer flagged; ratification/engineering/session-scoped artifacts land clean by default. (2) Rigby can operator-clear a `missing_initiative_id` diagnostic via `deliverable_tool.clear_diagnostic` with sticky sentinel semantics — subsequent updates don't re-fire while alignment state is unchanged; workspace_mismatch still fires on transition. (3) Empty deliverable_type strings normalize to 'document' at write time. (4) `spider_status_tool.list` paginated with `limit/offset/total/has_more` + registry union — Rigby can iterate the full 90-spider inventory reliably; never-run spiders (reddit + sports_injuries) visible with `status='never_run'`; per-row `in_registry` triage flag. S2869: (1) `spider_status_tool.search` preview field now falls back to raw_data extraction when embedding_text is empty — huggingface / devto / techcrunch_startups / hackernews rows no longer return empty previews. (2) `intelligence_tool.signal_clusters` `source_spider` accepts string OR list — list form uses `has_any_keys` union filter, so multi-spider cluster discovery is one call instead of N sequential dispatches; middleware-stringified list recovery via json.loads. S2870: (1) `intelligence_tool.signal_clusters` `pattern_type` schema uses `anyOf: [{string enum}, {null}]` shape — GPT-5.2 now has a proper 'no filter' payload option and no longer default-injects `pattern_type='demand_spike'` when operator omits it. All three filter param descriptions (pattern_type / min_confidence / window_hours) explicitly forbid default-fill. Rigby dispatch of `signal_clusters source_spider='hackernews'` (no other filters) went from count=0 (pre-code) to count=30 (post-code). (2) `spider_data_bridge.py` list-form raw_data guard — 5 callsites in the learning bridge no longer crash with AttributeError when a LegacySpiderData row has list-form raw_data. **S2871: (1) `LegacySpiderData.raw_data_dict` @property promoted from S2870 file-local helper — every LegacySpiderData reader can now access `.raw_data_dict` for a dict-form-guaranteed accessor (returns {} for list-form / null / non-dict). Model's own `get_searchable_text()` migrated to use the property (was a self-crash site). 16 external callsites across 12 files migrated (proactive_intelligence, views_spider_feed, tasks_financial, ai_core/intelligence/consumers, views_spider_intelligence, workflow_engine, tasks_conversations, signals/trigger_signals, tasks, views_stock_intelligence). Broader ~30-site sweep logged as ledger #22b. (2) LegacySpiderData now inspectable via `orm_inspect_tool` — 9-model allowlist (was 8). Live: `count_by field='spider_name'` returns 15,610 rows across 51 spiders. (3) `repo_tool` search action now uses conditional wall-clock timeouts — repo-wide default keeps 10s/5s (UX protection); narrowed (path or file_type) unlocks 30s/10s. Structured `error_code='search_timeout_repo_wide'` or `'search_timeout_narrowed'` on timeout + `narrowing_hint` with `suggested_paths` on repo-wide.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail — cycle-triggered vs operator-triggered attributed correctly + auto_events_count vs operator_events_count now visible per-workspace in the fleet report; (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total — now cleanly filtered to enforcer-forced downgrades only; (i) all billing paths route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls priced at effective_model rates; (j) analytics-plane cost attribution correct; display fallbacks use canonical rates with explicit `estimated: true` flag; embedding pricing SoT preserved; (k) autopilot audit history (`autopilot_tool.history include_evidence=true`) surfaces evidence + result JSONField values inline for operators inspecting trigger / actor_user_id / reason; (l) operators + demo audiences can trigger the freeze + downgrade enforcer against a synthetic spend value via `workspace_budget_tool.simulate_enforcement`; (m) operators can inspect post-clear re-flag likelihood inline on clear_freeze/clear_downgrade responses; (n) workspace_budget_tool.list_caps read surface no longer degrades linearly with workspace count; (o) governance/ratification records land clean via `deliverable_tool.create` (deliverable_type=ratification_record); (p) hard delete of a deliverable is a first-class operator action via `deliverable_tool.delete`; (q) `autopilot_tool.history include_evidence=true` supports `selected_fields=["evidence.<key>", "result.<key>"]` for top-level JSON projection; (r) HuggingFace AI/ML signals enter SignalCluster aggregation; (s) `intelligence_tool.signal_clusters source_spider='huggingface'` returns LIVE Hub API data (not curated fallback); (t) `/api/spider-intelligence/feed/?source=huggingface` returns canonical items with title+url+description for historical + new rows without view-layer spider-name matching; (u) Rigby can raw-fetch arbitrary http/https URLs via `web_fetch_tool`; (v) Rigby can inspect any of 8 allowlisted Django models directly via `orm_inspect_tool` (now 9 with LegacySpiderData at S2871); (w) Rigby can aggregate any allowlisted model's rows by a single field via `orm_inspect_tool action='count_by'`; (x) 4 new deliverable_types exempt from missing_initiative_id diagnostic (engineering_backlog / engineering_record / code_review / session_handoff) — Rigby's Tool Gap Ledger + session engineering artifacts land clean by default; (y) Rigby can operator-clear the missing_initiative_id diagnostic via `deliverable_tool.clear_diagnostic` with sticky sentinel semantics (subsequent updates don't re-fire while alignment state is unchanged); (z) `spider_status_tool.list` paginated + unions with the spider registry — full 90-spider inventory iterable via limit/offset/total/has_more, never-run spiders explicitly surfaced with status='never_run', per-row in_registry boolean for operator triage; (aa) `spider_status_tool.search` preview field non-empty for items-shape and top-level-title raw_data spiders (title → name → id fallback chain, best-effort inline, not a shared helper); (bb) `intelligence_tool.signal_clusters` `source_spider` param accepts string OR list — list-form multi-spider cluster discovery is one call instead of N sequential dispatches; middleware-stringified list recovery hardening. (cc) `intelligence_tool.signal_clusters` filter injection hardened — `pattern_type` schema `anyOf: [enum, null]` + descriptions explicitly forbid default-fill on all three filter params (`pattern_type`, `min_confidence`, `window_hours`); Rigby's `signal_clusters` dispatch with `source_spider` filter only no longer over-filters to zero from GPT-5.2 auto-injected defaults. (dd) `spider_data_bridge.py` no longer crashes with AttributeError on list-form `LegacySpiderData.raw_data` — 5 callsites guarded via `_safe_dict()` helper. **(ee) `LegacySpiderData.raw_data_dict` @property is the canonical guarded accessor for spider raw_data reads across the platform; model's own `get_searchable_text()` uses it; 16 external callsites migrated; broader sweep of ~30 remaining sites logged as ledger #22b. (ff) `LegacySpiderData` now inspectable via `orm_inspect_tool` (9-model allowlist); Rigby can independently verify spider-data prevalence / list-form distribution / spider mix without file-system reads. (gg) `repo_tool` search action distinguishes narrowed (path/file_type present) from repo-wide invocations — narrowed gets 30s/10s budget, repo-wide keeps 10s/5s; timeout errors return structured `error_code` + narrowing hint with `suggested_paths` for operator recovery.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2872 close — what shipped (one PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3365** `a54998be4` — S2872 slate: Ledger #22b sweep + telemetry (30 files, +308/-46)
- **PR `<this docs cascade>`** — S2872 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for S2873 open

**Workspace canonical:** Rigby Tool Gap Ledger updated by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables` (entry #22b marked `shipped_in_pr_S2872` + 2 new observed tool-surface gaps noted). Confirmed via `deliverable_tool.append`.

**Runtime impact:**
- 44 crash-risk callsites on LegacySpiderData readers migrated from `raw = X.raw_data or {}` → `raw = X.raw_data_dict`. List-form rows no longer crash on `.get()` in any migrated site.
- `LegacySpiderData.raw_data_dict` property now emits rate-limited debug telemetry on fallback (first hit + every 100th per spider_name). Schema drift observable via `_NON_DICT_RAW_DATA_COUNTER`.
- Combined regression suite (S2869 + S2870 + S2871 + S2872): 60/60 pass.
- PA tool schemas unchanged (no new drift from `check_pa_tool_drift`).

**Not shipped at S2872 close (deferred to S2873 or later):**
- SpiderData + Opportunity → orm_inspect allowlist (wish-list from S2871)
- `orm_inspect_tool` JSONField type predicate (new S2872 gap #1, 1st trigger)
- `repo_tool.read_file` large-file paging (new S2872 gap #2, 1st trigger)
- Category B cosmetic `raw_data_dict` migration (~8-10 already-guarded sites)
- Character-os Rigby integration (5-gap analysis parked under D6 moratorium)
- Ledger #5 / #16 (remaining open ledger items from prior sessions)
- All prior deferred items from S2871/S2868/S2867/S2866/S2862/S2861/etc still carried

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2872)

See:
- **S2872 handoff (current):** `docs/handoffs/SESSION_2872_RAW_DATA_DICT_SWEEP_LEDGER_22B_TELEMETRY.md`
- **S2871 handoff:** `docs/handoffs/SESSION_2871_RAW_DATA_DICT_PROPERTY_ORM_INSPECT_LEGACY_SPIDER_DATA_CONDITIONAL_TIMEOUT.md`
- **S2870 handoff:** `docs/handoffs/SESSION_2870_INJECTION_HARDENING_AND_RAW_DATA_GUARD.md`
- **S2869 handoff:** `docs/handoffs/SESSION_2869_SPIDER_SEARCH_PREVIEW_AND_SIGNAL_CLUSTERS_MULTISOURCE.md`
- **S2868 handoff:** `docs/handoffs/SESSION_2868_DELIVERABLE_DIAGNOSTIC_AND_SPIDER_STATUS_PAGINATION.md`
- **S2867 handoff:** `docs/handoffs/SESSION_2867_ORM_COUNT_BY.md`
- **S2866 handoff:** `docs/handoffs/SESSION_2866_ORM_INSPECT_TOOL.md`
- **S2865 handoff:** `docs/handoffs/SESSION_2865_WEB_FETCH_TOOL.md`
- **S2864 handoff:** `docs/handoffs/SESSION_2864_HF_BACKFILL_VIEW_CLEANUP.md`
- **S2863 handoff:** `docs/handoffs/SESSION_2863_HF_HUB_API_SORT_DOWNLOADS.md`
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
