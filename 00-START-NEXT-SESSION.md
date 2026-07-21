# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2870 CLOSE → 2-item slate shipped (2026-07-21; picks up as S2871) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2870 close).** Rigby Tool Gap Ledger #20 + #21 grouped (both surfaced mid-S2869; both harden PA tool-surface reliability); shipped as **one PR / one commit**:

- **PR #3361** `8abb12f0f` — S2870 slate (3 files, +229/-8)
  - **#20 fix**: `intelligence_tool.signal_clusters` schema hardening — `pattern_type` bare enum → `anyOf: [{type: 'string', enum: [...]}, {type: 'null'}]` (mirrors S2869 `source_spider` shape). All three filter descriptions (`pattern_type` / `min_confidence` / `window_hours`) explicitly forbid default-fill. Handler unchanged (already tolerates None/0/'' as no-op).
  - **#21 fix**: `spider_data_bridge.py` list-form `raw_data` guard — new file-local `_safe_dict(rd) -> dict` helper + 5 callsite migrations (Option 21A per S2869 Fold 1: file-local, not shared util).
  - 18 pytest cases across 2 test classes (9 SignalClustersInjectionHardening + 9 SpiderDataBridgeSafeDict). S2869 regression 14/14.

**Discovery arc — 3 SIGN cycles:**
- Pre-code SIGN: Q1 grounded live via 3 Rigby `signal_clusters` dispatches → count=0 with `filters_applied.pattern_type='demand_spike'` + `min_confidence=0.6` + `window_hours=168` confirmed root cause. Q4/Q5 blocked by tool limitations → became ledger candidates #23 + #24.
- Round 2 (revised proposal): Claude self-served Q5 grep → found #21 pattern is **not one-off** (~14 sites, 8 files). Revised approach: anyOf-null on #20 (description-only insufficient per Q1 evidence); Option 21A on #21 + ledger #22 for the 13-site sweep.
- Post-code SIGN round 3: F-AGREE with live evidence — post-code dispatch confirmed `pattern_type=null` preserved + **count=30** (vs pre-code count=0) with `source_spider='hackernews'`; explicit filter still works (count=12).

**Working loop observations at S2870:**
- `feedback_verify_rigby_tool_runs_before_trusting_sign` fired 3× — every SIGN F-AGREE backed by tool_runs evidence from Rigby.
- `feedback_verify_at_raw_orm_before_trusting_tool_no_data` fired 2× — Rigby's tool-surface limitations (LegacySpiderData not in orm_inspect allowlist; repo_tool 10s timeout) blocked Q4/Q5 → Claude self-served via file-system Grep. Both blockers became ledger candidates.
- `feedback_zoom_out_ask_per_rigby_sign` yielded 3 usable folds — all applied: (1) escalate #20 fix from description-only to anyOf-null shape; (2) Option 21A + ledger #22 for cross-file sweep; (3) middleware `log_injected_params` as future spec candidate (not Playbook amendment yet).
- `feedback_claude_stdout_truncation_vs_ui_truncation` fired 2× — recovered via `sed '/--- Tool Runs (verbose) ---/,$d'` filter.
- **New at S2870:** Rigby's tool dispatcher shim still emits numeric defaults on `window_hours` + `min_confidence` even when set to null-ish. Handler tolerance masks it for correct callers; injection pattern remains real. Deferred to future observation-driven middleware work.
- No candidate lessons for Playbook amendment this session.

**Rigby Tool Gap Ledger updates (via Rigby PA per `feedback_rigby_writes_workspace_deliverables`):**
- Deliverable ID `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
- **#20** → `shipped_in_pr_S2870`
- **#21** → `shipped_in_pr_S2870`
- **NEW #22** — raw_data isinstance guard needed at ~13 remaining sites (8 files) — grep evidence in S2870 handoff
- **NEW #23** — LegacySpiderData missing from `orm_inspect_tool` allowlist
- **NEW #24** — `repo_tool` 10s timeout blocks repo-wide greps

**Session pin `pa-2459cc90df584f5f` (labeled `s2870-slate-injection-hardening-and-raw-data-guard`) RETIRES at S2870 close.** Fresh mint required at S2871 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2871 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

Wrapper pin rewritten at S2870 close. If needed at S2871 open:

```bash
python manage.py session_lifecycle close --label s2871-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2871

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2870 close — Ledger #22 — raw_data isinstance guard sweep** (~13 sites, 8 files). Mechanical: extend the S2870 `_safe_dict` pattern (or inline `isinstance(rd, dict)`) to remaining callsites. If shared util is warranted (second-file trigger per S2869 Fold 1), promote to `core/learning_bridges/base.py` or similar. ~40-line PR + regression tests. ~1 hr.

2. **NEW at S2870 close — Ledger #23 — extend `orm_inspect_tool` allowlist**. Add `LegacySpiderData` + other frequently-verified models (SpiderItemHash, ContentBrief?) to the 8-model allowlist. Unblocks Rigby's independent verification path for spider-data questions. ~30 min.

3. **NEW at S2870 close — Ledger #24 — `repo_tool` timeout raise or grep alternative**. Either raise timeout to 30s+ or add a `repo_grep` action that streams results. Unblocks Rigby's cross-file pattern searches. ~1 hr.

4. **Ledger #5 — schema/handler drift detection lint / CI wiring** (~2 hr). Command exists at `core/management/commands/check_pa_tool_drift.py` (S2846-authored, 403 lines) but never wired to CI enforcement. Also worth reconciling pre-existing drift reports before flipping to enforce mode.

5. **Ledger #16 — close-ceremony twin-mirror enforcement gap** (S2863). Ranked fix candidates: (a) explicit close-checklist gate (~15 min); (b) hard-enforce in `session_lifecycle close` — refuse close without both deliverable IDs (~2 hr); (c) nightly audit task for recent handoffs missing mirrors (~1 hr).

6. **Carried — Exemption-list telemetry (Rigby zoom-out from S2868 slate #1)**. Add counts-by-code/type instrumentation for `diagnostic_status='cleared'` so we can detect exemption-list-junk-drawer risk over time. 1st trigger only — watch for 2nd before opening.

7. **Carried — Stale-cleared row GC (Rigby zoom-out from S2868 slate #1)**. Optional sweep for `diagnostic_status='cleared'` rows >180 days old that could be fully NULLed. Deferred until UI clutter becomes real.

8. **Carried — `group_key_note` UX hint on `count_by`** (S2867 Q2 fold). Nice-to-have string like `"FK grouped on attname <field>_id"`. 1st trigger; watch for 2nd.

9. **Carried — High-cardinality guardrail on `count_by`** (S2867 Q5 fold). Optional soft-warning when `total_matching` exceeds a threshold. 1st trigger; deferred until slow-query experience report.

10. **Carried — Per-model `allowed_fields` explicit allowlist on `orm_inspect_tool`** (S2866 fold, still 1st trigger). Mitigates euphemistic-name slip-through class.

11. **Carried — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.** Still 2 independent triggers, not promoted. ~30 min doc/deliverable.

12. **Carried — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate). 1st trigger only from S2864; watch for 2nd/3rd.

13. **Carried — Provider-specific composite additions.** Reactive; watch for new integrations.

14. **Carried — `simulate_enforcement` auto-clear-after-N-seconds** (S2857 fold). Deferred; awaits explicit ask.

15. **Carried — `enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger).

16. **Carried — `actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, MIGRATION required). Deferred until schema-migration budget opens.

17. **Carried — `EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger).

18. **Carried — `list_caps include_defaults=true` remaining perf costs** (S2858, 1st trigger).

19. **Carried — Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859 1st trigger observed; S2868 shipped 4 additions — this is now the 2nd cycle).

20. **Carried — Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

21. **Carried — Fold C from S2861 close: shared JSONField projection helper**.

22. **Carried — Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

23. **Carried — openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

24. **NEW at S2870 close — Middleware `log_injected_params` spec candidate** (Q6 zoom-out fold). Compare GPT-5.2's function-call payload against operator utterance for un-mentioned filter values; log-only mode first, strip mode later for high-risk tools. Rigby-recommended pattern-checklist framing, not blanket Playbook rule. 1st trigger only from S2870 — watch for 2nd.

25. **Carried — Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

26. **Carried — A4 warm-up under ratified constraints** — S2846 6-line block still in force. A4 capabilities extended at S2870: see A4 Constraints below.

### What's forbidden at S2871 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2870 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`. S2857: operator can now verify enforcement without touching real spend via `simulate_enforcement`. S2858: post-clear re-flag likelihood inline on clear_* responses; list_caps read surface no longer degrades linearly with workspace count. S2859: `deliverable_tool.create` with `deliverable_type='ratification_record'` lands with verbatim title + no spurious diagnostic mark. S2860: Rigby can permanently delete deliverables directly via `deliverable_tool.delete` — two-factor gated, published-guarded, cascade-previewed, WARNING-audit-logged. S2861: Rigby can trim `autopilot_tool.history include_evidence=true` responses to specific top-level keys via `selected_fields=["evidence.<key>", "result.<key>"]`. S2862: huggingface → SignalCluster drop resolved — HF spider runs now produce extractable text; A4 AI/ML signal-cluster discovery restored (curated fallback). S2863: HuggingFaceSpider now hits the LIVE HF Hub API — 20/20 items with populated title+description, 2827 chars extractable text — A4 `intelligence_tool.signal_clusters source_spider='huggingface'` now returns live-data-backed AI/ML clusters, not curated topics. S2864: view-layer HF workaround removed after backfill enriched 460 pre-S2862 items; A4 feed queries for `source=huggingface` no longer require spider-name string-matching at read time. S2865: Rigby can now raw-HTTP GET/POST arbitrary http/https URLs via `web_fetch_tool` — closes the twice-bit F-DELEGATED verification gap. S2866: Rigby can now inspect any of 8 allowlisted DB models directly via `orm_inspect_tool` — closes the S2845-class false-negative gap where a tool surface reports 'no data' but rows exist under a different filter path. S2867: Rigby can now aggregate rows by any allowlisted field (single-value / FK-attname / DateTimeField-auto-day-bucket) via `orm_inspect_tool action='count_by'`. S2868: (1) 4 additional deliverable_types exempt from `missing_initiative_id` diagnostic — Rigby's own Tool Gap Ledger (engineering_backlog) no longer flagged; ratification/engineering/session-scoped artifacts land clean by default. (2) Rigby can operator-clear a `missing_initiative_id` diagnostic via `deliverable_tool.clear_diagnostic` with sticky sentinel semantics — subsequent updates don't re-fire while alignment state is unchanged; workspace_mismatch still fires on transition. (3) Empty deliverable_type strings normalize to 'document' at write time. (4) `spider_status_tool.list` paginated with `limit/offset/total/has_more` + registry union — Rigby can iterate the full 90-spider inventory reliably; never-run spiders (reddit + sports_injuries) visible with `status='never_run'`; per-row `in_registry` triage flag. S2869: (1) `spider_status_tool.search` preview field now falls back to raw_data extraction when embedding_text is empty — huggingface / devto / techcrunch_startups / hackernews rows no longer return empty previews. (2) `intelligence_tool.signal_clusters` `source_spider` accepts string OR list — list form uses `has_any_keys` union filter, so multi-spider cluster discovery is one call instead of N sequential dispatches; middleware-stringified list recovery via json.loads. **S2870: (1) `intelligence_tool.signal_clusters` `pattern_type` schema uses `anyOf: [{string enum}, {null}]` shape — GPT-5.2 now has a proper 'no filter' payload option and no longer default-injects `pattern_type='demand_spike'` when operator omits it. All three filter param descriptions (pattern_type / min_confidence / window_hours) explicitly forbid default-fill. Rigby dispatch of `signal_clusters source_spider='hackernews'` (no other filters) went from count=0 (pre-code) to count=30 (post-code). (2) `spider_data_bridge.py` list-form raw_data guard — 5 callsites in the learning bridge no longer crash with AttributeError when a LegacySpiderData row has list-form raw_data.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail — cycle-triggered vs operator-triggered attributed correctly + auto_events_count vs operator_events_count now visible per-workspace in the fleet report; (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total — now cleanly filtered to enforcer-forced downgrades only; (i) all billing paths route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls priced at effective_model rates; (j) analytics-plane cost attribution correct; display fallbacks use canonical rates with explicit `estimated: true` flag; embedding pricing SoT preserved; (k) autopilot audit history (`autopilot_tool.history include_evidence=true`) surfaces evidence + result JSONField values inline for operators inspecting trigger / actor_user_id / reason; (l) operators + demo audiences can trigger the freeze + downgrade enforcer against a synthetic spend value via `workspace_budget_tool.simulate_enforcement`; (m) operators can inspect post-clear re-flag likelihood inline on clear_freeze/clear_downgrade responses; (n) workspace_budget_tool.list_caps read surface no longer degrades linearly with workspace count; (o) governance/ratification records land clean via `deliverable_tool.create` (deliverable_type=ratification_record); (p) hard delete of a deliverable is a first-class operator action via `deliverable_tool.delete`; (q) `autopilot_tool.history include_evidence=true` supports `selected_fields=["evidence.<key>", "result.<key>"]` for top-level JSON projection; (r) HuggingFace AI/ML signals enter SignalCluster aggregation; (s) `intelligence_tool.signal_clusters source_spider='huggingface'` returns LIVE Hub API data (not curated fallback); (t) `/api/spider-intelligence/feed/?source=huggingface` returns canonical items with title+url+description for historical + new rows without view-layer spider-name matching; (u) Rigby can raw-fetch arbitrary http/https URLs via `web_fetch_tool`; (v) Rigby can inspect any of 8 allowlisted Django models directly via `orm_inspect_tool`; (w) Rigby can aggregate any allowlisted model's rows by a single field via `orm_inspect_tool action='count_by'`; (x) 4 new deliverable_types exempt from missing_initiative_id diagnostic (engineering_backlog / engineering_record / code_review / session_handoff) — Rigby's Tool Gap Ledger + session engineering artifacts land clean by default; (y) Rigby can operator-clear the missing_initiative_id diagnostic via `deliverable_tool.clear_diagnostic` with sticky sentinel semantics (subsequent updates don't re-fire while alignment state is unchanged); (z) `spider_status_tool.list` paginated + unions with the spider registry — full 90-spider inventory iterable via limit/offset/total/has_more, never-run spiders explicitly surfaced with status='never_run', per-row in_registry boolean for operator triage; (aa) `spider_status_tool.search` preview field non-empty for items-shape and top-level-title raw_data spiders (title → name → id fallback chain, best-effort inline, not a shared helper); (bb) `intelligence_tool.signal_clusters` `source_spider` param accepts string OR list — list-form multi-spider cluster discovery is one call instead of N sequential dispatches; middleware-stringified list recovery hardening. **(cc) `intelligence_tool.signal_clusters` filter injection hardened — `pattern_type` schema `anyOf: [enum, null]` + descriptions explicitly forbid default-fill on all three filter params (`pattern_type`, `min_confidence`, `window_hours`); Rigby's `signal_clusters` dispatch with `source_spider` filter only no longer over-filters to zero from GPT-5.2 auto-injected defaults. (dd) `spider_data_bridge.py` no longer crashes with AttributeError on list-form `LegacySpiderData.raw_data` — 5 callsites guarded via `_safe_dict()` helper.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2870 close — what shipped (one PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3361** `8abb12f0f` — S2870 slate: Ledger #20 + #21 (3 files, +229/-8)
- **PR `<this docs cascade>`** — S2870 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for S2871 open

**Workspace canonical:** Rigby Tool Gap Ledger updated by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables` (entries #20 + #21 marked shipped, 3 new entries #22 + #23 + #24 added). S2870 close ratification envelope to be created by Rigby (deliverable ID recorded in handoff).

**Runtime impact:**
- `intelligence_tool.signal_clusters` `pattern_type` schema uses anyOf-null shape; descriptions on all three filter params explicitly forbid default-fill. Live Rigby dispatch verified: `pattern_type=null` preserved in `filters_applied` (didn't snap back to `demand_spike`).
- `spider_data_bridge.py` 5 callsites guarded via `_safe_dict()` — list-form `LegacySpiderData.raw_data` no longer raises AttributeError.
- PA tool schemas updated for #20; no new drift from `check_pa_tool_drift`.

**Not shipped at S2870 close (deferred to S2871 or later):**
- Ledger #22 (raw_data sweep for 13 remaining sites) — waits on second-file trigger or Chris pick
- Ledger #23 (LegacySpiderData in orm_inspect allowlist)
- Ledger #24 (repo_tool timeout raise)
- Ledger #5 / #16 (remaining open ledger items from prior sessions)
- All prior deferred items from S2867/S2866/S2862/S2861/etc still carried

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2870)

See:
- **S2870 handoff (current):** `docs/handoffs/SESSION_2870_INJECTION_HARDENING_AND_RAW_DATA_GUARD.md`
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
