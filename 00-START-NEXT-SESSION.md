# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2869 CLOSE → 2-item Chris-picked slate shipped (2026-07-21; picks up as S2870) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2869 close).** Chris-selected 2-item slate (Rigby Tool Gap Ledger #2 + #4, grouped by substrate overlap) shipped as **one PR / one commit**:

- **PR #3359** `cf9dcf572` — S2869 slate (5 files, +345/-5)
  - Rigby Tool Gap Ledger entries #2 + #4 (grouped — both touch tool-dispatch handler layer)
  - **#2 fix**: `spider_status_tool.search` preview field falls back to `raw_data['items'][0].{title|name|id}` → top-level `{title|name}` when `embedding_text` is empty. Inline in the search handler; NOT a shared helper (per Rigby zoom-out Fold 1). `raw_data icontains` query extension deferred (perf footgun per Rigby Q2).
  - **#4 fix**: `intelligence_tool.signal_clusters` `source_spider` param accepts string OR list. String preserves `has_key`; list uses `has_any_keys` union. Middleware-stringified list recovery via `json.loads`. Non-string/empty list entries filtered before apply.
  - Schema updates in `pa_tool_schemas.py` (query description + source_spider anyOf shape).
  - Wrapper pin bump (`tools/pa_local.sh`) folded into the code PR — retired `s2868-slate-pick` pin, minted `pa-c75328a89aef48c8`.
  - 14 pytest cases across 2 test classes (7 preview + 7 multi-source).

**Discovery arc — 3 SIGN cycles:**
- Pre-code SIGN: 5 F-AGREE / 0 F-DISAGREE / 0 F-BLOCKING (Rigby confirmed raw_data shape across 4 spiders via `spider_status_tool.search + detail` dispatches; recommended defer raw_data icontains; recommended string-or-list on source_spider; requested handler hardening for JSON-stringified list from middleware).
- Post-code SIGN round 1: partial — #2 F-AGREE (live-verified across 3 spiders); #4 F-BLOCKING due to Rigby's dispatch returning count=0. Root cause: GPT-5.2 auto-injected `pattern_type='demand_spike'` + `min_confidence=0.6` + `window_hours=168` defaults that filter to zero. Direct handler dispatch via `python manage.py shell` confirmed fix works (count=5 with just `source_spider='hackernews'`; count=10 with list form + list is superset of single-source).
- Post-code SIGN round 3: F-AGREE on #4 after clarifying acceptance criteria — Rigby re-verified using her own dispatch data (Call A count=5, Call B count=10 unique superset).

**Working loop observations at S2869:**
- `feedback_verify_rigby_tool_runs_before_trusting_sign` fired twice — pre-code Rigby grounded Q1 via 4-spider live dispatches; post-code Rigby's initial F-BLOCKING was overcautious rubber-stamp on my miscalibrated acceptance criterion (asked her to match my shell-test IDs when her dispatch had extra filter defaults). Independent Django-shell verification proved the code correct.
- `feedback_zoom_out_ask_per_rigby_sign` yielded 3 fold candidates — all applied: (1) preview inline, not helper; (2) raw_data icontains deferred; (3) list-input coercion recovery via json.loads.
- `feedback_claude_stdout_truncation_vs_ui_truncation` hit once — recovered via `sed '/--- Tool Runs (verbose) ---/,$d'` filter.
- **Two new ledger candidates surfaced mid-cycle** (both logged by Rigby into workspace deliverable, out of scope for this slate):
  - **#20** — signal_clusters filter defaults auto-injected by dispatch (pattern_type enum-only, no null path; blocked Rigby's initial #4 verification)
  - **#21** — `spider_data_bridge.py:93` crashes on list-form raw_data (test fixture 6 surfaced it)
- Rigby memory limit reached (`remember_tool` current_count=1240, max_items=200) — memory pruning is a separate hygiene item.
- No candidate lessons for Playbook amendment this session.

**Rigby Tool Gap Ledger updates (via Rigby PA per `feedback_rigby_writes_workspace_deliverables`):**
- Deliverable ID `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
- **#2** → `shipped_in_pr_3359`
- **#4** → `shipped_in_pr_3359`
- **NEW #20** — signal_clusters dispatch auto-injected defaults (open, medium priority)
- **NEW #21** — spider_data_bridge list-form raw_data crash (open, low priority)
- Ledger content: 11,473 → 13,630 chars

**Session pin `pa-c75328a89aef48c8` (labeled `s2869-spider-search-preview-and-signal-clusters-multisource`) RETIRES at S2869 close.** Fresh mint required at S2870 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2870 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-c75328a89aef48c8` retired at S2869 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2870-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2870

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2869 close — Ledger #20 — signal_clusters dispatch auto-inject fix**. GPT-5.2 auto-injects `pattern_type='demand_spike'` + `min_confidence=0.6` + `window_hours=168` on signal_clusters when omitted. `pattern_type` schema enum has no null path so GPT-5.2 cannot "send nothing." Over-filters to zero. Two possible fixes: (a) make `pattern_type` schema nullable (schema-side); (b) ensure omitted optional filters don't default-inject at tool-dispatcher middleware. ~1-2 hr.

2. **NEW at S2869 close — Ledger #21 — spider_data_bridge list-form raw_data guard**. `spider_data_bridge.py:93` crashes with `AttributeError: 'list' object has no attribute 'get'` when a LegacySpiderData row has `raw_data` as a list. Cheap ~5-line guard fix: `rd = raw_data if isinstance(raw_data, dict) else {}`. ~15 min.

3. **Ledger #5 — schema/handler drift detection lint / CI wiring** (~2 hr). Command exists at `core/management/commands/check_pa_tool_drift.py` (S2846-authored, 403 lines) but never wired to CI enforcement. Fix scope: add `.github/workflows/check-pa-tool-drift.yml` running the lint in `--strict` mode; consider adding to pre-commit as well. Also worth verifying pre-existing DRIFT reports (S2869 saw drift on both spider_status_tool and intelligence_tool) — resolve or explicitly annotate before flipping to enforce mode.

4. **Ledger #16 — close-ceremony twin-mirror enforcement gap** (S2863). Ranked fix candidates: (a) explicit close-checklist gate (~15 min); (b) hard-enforce in `session_lifecycle close` — refuse close without both deliverable IDs (~2 hr); (c) nightly audit task for recent handoffs missing mirrors (~1 hr).

5. **Carried — Exemption-list telemetry (Rigby zoom-out from S2868 slate #1)**. Add counts-by-code/type instrumentation for `diagnostic_status='cleared'` so we can detect exemption-list-junk-drawer risk over time. 1st trigger only — watch for 2nd before opening.

6. **Carried — Stale-cleared row GC (Rigby zoom-out from S2868 slate #1)**. Optional sweep for `diagnostic_status='cleared'` rows >180 days old that could be fully NULLed. Deferred until UI clutter becomes real.

7. **Carried — `group_key_note` UX hint on `count_by`** (S2867 Q2 fold). Nice-to-have string like `"FK grouped on attname <field>_id"`. 1st trigger; watch for 2nd.

8. **Carried — High-cardinality guardrail on `count_by`** (S2867 Q5 fold). Optional soft-warning when `total_matching` exceeds a threshold. 1st trigger; deferred until slow-query experience report.

9. **Carried — Per-model `allowed_fields` explicit allowlist on `orm_inspect_tool`** (S2866 fold, still 1st trigger). Mitigates euphemistic-name slip-through class.

10. **Carried — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.** Still 2 independent triggers, not promoted. ~30 min doc/deliverable.

11. **Carried — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate). 1st trigger only from S2864; watch for 2nd/3rd.

12. **Carried — Provider-specific composite additions.** Reactive; watch for new integrations.

13. **Carried — `simulate_enforcement` auto-clear-after-N-seconds** (S2857 fold). Deferred; awaits explicit ask.

14. **Carried — `enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger).

15. **Carried — `actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, MIGRATION required). Deferred until schema-migration budget opens.

16. **Carried — `EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger).

17. **Carried — `list_caps include_defaults=true` remaining perf costs** (S2858, 1st trigger).

18. **Carried — Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859 1st trigger observed; S2868 shipped 4 additions — this is now the 2nd cycle).

19. **Carried — Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

20. **Carried — Fold C from S2861 close: shared JSONField projection helper**.

21. **Carried — Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

22. **Carried — openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

23. **Carried — Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

24. **Carried — A4 warm-up under ratified constraints** — S2846 6-line block still in force. A4 capabilities extended at S2869: see A4 Constraints below.

### What's forbidden at S2870 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2869 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`. S2857: operator can now verify enforcement without touching real spend via `simulate_enforcement`. S2858: post-clear re-flag likelihood inline on clear_* responses; list_caps read surface no longer degrades linearly with workspace count. S2859: `deliverable_tool.create` with `deliverable_type='ratification_record'` lands with verbatim title + no spurious diagnostic mark. S2860: Rigby can permanently delete deliverables directly via `deliverable_tool.delete` — two-factor gated, published-guarded, cascade-previewed, WARNING-audit-logged. S2861: Rigby can trim `autopilot_tool.history include_evidence=true` responses to specific top-level keys via `selected_fields=["evidence.<key>", "result.<key>"]`. S2862: huggingface → SignalCluster drop resolved — HF spider runs now produce extractable text; A4 AI/ML signal-cluster discovery restored (curated fallback). S2863: HuggingFaceSpider now hits the LIVE HF Hub API — 20/20 items with populated title+description, 2827 chars extractable text — A4 `intelligence_tool.signal_clusters source_spider='huggingface'` now returns live-data-backed AI/ML clusters, not curated topics. S2864: view-layer HF workaround removed after backfill enriched 460 pre-S2862 items; A4 feed queries for `source=huggingface` no longer require spider-name string-matching at read time. S2865: Rigby can now raw-HTTP GET/POST arbitrary http/https URLs via `web_fetch_tool` — closes the twice-bit F-DELEGATED verification gap. S2866: Rigby can now inspect any of 8 allowlisted DB models directly via `orm_inspect_tool` — closes the S2845-class false-negative gap where a tool surface reports 'no data' but rows exist under a different filter path. S2867: Rigby can now aggregate rows by any allowlisted field (single-value / FK-attname / DateTimeField-auto-day-bucket) via `orm_inspect_tool action='count_by'`. S2868: (1) 4 additional deliverable_types exempt from `missing_initiative_id` diagnostic — Rigby's own Tool Gap Ledger (engineering_backlog) no longer flagged; ratification/engineering/session-scoped artifacts land clean by default. (2) Rigby can operator-clear a `missing_initiative_id` diagnostic via `deliverable_tool.clear_diagnostic` with sticky sentinel semantics — subsequent updates don't re-fire while alignment state is unchanged; workspace_mismatch still fires on transition. (3) Empty deliverable_type strings normalize to 'document' at write time. (4) `spider_status_tool.list` paginated with `limit/offset/total/has_more` + registry union — Rigby can iterate the full 90-spider inventory reliably; never-run spiders (reddit + sports_injuries) visible with `status='never_run'`; per-row `in_registry` triage flag. **S2869: (1) `spider_status_tool.search` preview field now falls back to raw_data extraction when embedding_text is empty — huggingface / devto / techcrunch_startups / hackernews rows no longer return empty previews. (2) `intelligence_tool.signal_clusters` `source_spider` accepts string OR list — list form uses `has_any_keys` union filter, so multi-spider cluster discovery is one call instead of N sequential dispatches; middleware-stringified list recovery via json.loads.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail — cycle-triggered vs operator-triggered attributed correctly + auto_events_count vs operator_events_count now visible per-workspace in the fleet report; (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total — now cleanly filtered to enforcer-forced downgrades only; (i) all billing paths route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls priced at effective_model rates; (j) analytics-plane cost attribution correct; display fallbacks use canonical rates with explicit `estimated: true` flag; embedding pricing SoT preserved; (k) autopilot audit history (`autopilot_tool.history include_evidence=true`) surfaces evidence + result JSONField values inline for operators inspecting trigger / actor_user_id / reason; (l) operators + demo audiences can trigger the freeze + downgrade enforcer against a synthetic spend value via `workspace_budget_tool.simulate_enforcement`; (m) operators can inspect post-clear re-flag likelihood inline on clear_freeze/clear_downgrade responses; (n) workspace_budget_tool.list_caps read surface no longer degrades linearly with workspace count; (o) governance/ratification records land clean via `deliverable_tool.create` (deliverable_type=ratification_record); (p) hard delete of a deliverable is a first-class operator action via `deliverable_tool.delete`; (q) `autopilot_tool.history include_evidence=true` supports `selected_fields=["evidence.<key>", "result.<key>"]` for top-level JSON projection; (r) HuggingFace AI/ML signals enter SignalCluster aggregation; (s) `intelligence_tool.signal_clusters source_spider='huggingface'` returns LIVE Hub API data (not curated fallback); (t) `/api/spider-intelligence/feed/?source=huggingface` returns canonical items with title+url+description for historical + new rows without view-layer spider-name matching; (u) Rigby can raw-fetch arbitrary http/https URLs via `web_fetch_tool`; (v) Rigby can inspect any of 8 allowlisted Django models directly via `orm_inspect_tool`; (w) Rigby can aggregate any allowlisted model's rows by a single field via `orm_inspect_tool action='count_by'`; (x) 4 new deliverable_types exempt from missing_initiative_id diagnostic (engineering_backlog / engineering_record / code_review / session_handoff) — Rigby's Tool Gap Ledger + session engineering artifacts land clean by default; (y) Rigby can operator-clear the missing_initiative_id diagnostic via `deliverable_tool.clear_diagnostic` with sticky sentinel semantics (subsequent updates don't re-fire while alignment state is unchanged); (z) `spider_status_tool.list` paginated + unions with the spider registry — full 90-spider inventory iterable via limit/offset/total/has_more, never-run spiders explicitly surfaced with status='never_run', per-row in_registry boolean for operator triage. **(aa) `spider_status_tool.search` preview field non-empty for items-shape and top-level-title raw_data spiders (title → name → id fallback chain, best-effort inline, not a shared helper). (bb) `intelligence_tool.signal_clusters` `source_spider` param accepts string OR list — list-form multi-spider cluster discovery is one call instead of N sequential dispatches; middleware-stringified list recovery hardening.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2869 close — what shipped (one PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3359** `cf9dcf572` — S2869 slate: Ledger #2 + #4 (5 files, +345/-5) — includes wrapper pin bump for s2869 open
- **PR `<this docs cascade>`** — S2869 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for s2870 open

**Workspace canonical:** Rigby Tool Gap Ledger updated by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables` (entries #2 + #4 marked shipped, 2 new entries #20 + #21 added). S2869 close ratification envelope created by Rigby (deliverable ID recorded in handoff).

**Runtime impact:**
- `spider_status_tool.search` preview field: non-empty for items-shape and top-level-title raw_data spiders (verified live on huggingface / devto / techcrunch_startups).
- `intelligence_tool.signal_clusters` `source_spider` param: accepts string OR list; list form applies `source_breakdown__has_any_keys` union filter.
- PA tool schemas updated for both changes; no new drift from `check_pa_tool_drift`.

**Not shipped at S2869 close (deferred to S2870 or later):**
- Ledger #5 / #16 (remaining open ledger items from prior sessions)
- NEW #20 (signal_clusters dispatch auto-inject fix) + NEW #21 (spider_data_bridge list-form crash guard) — both surfaced mid-S2869
- All prior deferred items from S2867/S2866/S2862/S2861/etc still carried

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2869)

See:
- **S2869 handoff (current):** `docs/handoffs/SESSION_2869_SPIDER_SEARCH_PREVIEW_AND_SIGNAL_CLUSTERS_MULTISOURCE.md`
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
