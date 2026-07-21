# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2868 CLOSE → 2-item Rigby-picked slate shipped (2026-07-21; picks up as S2869) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2868 close).** Chris-selected 2-item slate (Rigby-recommended at session open) shipped as **two PRs / two commits**:

- **PR #3356** `a7e90d1c3` — S2868 slate #1: deliverable diagnostic misfire fix (7 files, +735/-13)
  - Rigby Tool Gap Ledger entries #7 + #17 + #18 (grouped — same substrate)
  - RC1: `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT` grew from `{ratification_record}` to 5 types (added `engineering_backlog`, `engineering_record`, `code_review`, `session_handoff`)
  - RC2: new `deliverable_tool.clear_diagnostic` action sets `diagnostic_status='cleared'` sticky sentinel; update-path re-eval respects it for `missing_initiative_id` (workspace_mismatch still fires on transition)
  - RC3: empty `deliverable_type` string normalizes to `'document'` at create-site
  - Backfill: 18 historical rows of the 4 newly-exempt types migrated to `cleared` sentinel (idempotent management command)
  - 20 pytest cases across 3 test classes

- **PR #3357** `c1ac926b9` — S2868 slate #2: `spider_status_tool.list` pagination + registry union (3 files, +302/-8)
  - Rigby Tool Gap Ledger entry #1
  - Pagination envelope: `limit/offset/total/has_more/total_spiders` (last as backward-compat alias)
  - Registry union: `include_registry=true` default surfaces never-run spiders (reddit + sports_injuries) with `status='never_run'`
  - Orphan filter: `include_orphans=true` default keeps legacy spider_names in DB but absent from registry
  - Per-row `in_registry` boolean for triage
  - 14 pytest cases

**Discovery arc — 5 SIGN cycles across both slates:**
- Slate #1 pre-code SIGN: 4 F-AGREE + 0 F-DISAGREE + 0 F-BLOCKING (Rigby narrowed 9 candidate exemption types to 4 after ORM telemetry review; kept `initiative_phase_doc` OUT per 93%-correctly-linked data)
- Slate #1 post-code SIGN round 1: partial pass — RC1 + RC3 verified, RC2 blocked by 2 mid-cycle bugs (gateway whitelist + UUID JSON serialization)
- Slate #1 post-code SIGN round 3: all pass, sticky sentinel verified end-to-end
- Slate #2 pre-code SIGN: 4 F-AGREE (Rigby confirmed downstream truncation via her own live `_truncated: {shown: 44, total: 88}` dispatch)
- Slate #2 post-code SIGN: 5 F-AGREE, ship it

**Working loop observations at S2868:**
- `feedback_verify_rigby_tool_runs_before_trusting_sign` produced grounded SIGNs across both slates via `repo_tool.read_file` + live `orm_inspect_tool` / `spider_status_tool.list` dispatches.
- `feedback_zoom_out_ask_per_rigby_sign` surfaced 2 fold candidates in slate #1 — same-PR backfill applied, telemetry deferred as Ledger candidate.
- `feedback_claude_stdout_truncation_vs_ui_truncation` hit twice on slate #2 dispatches — recovered by asking Rigby to re-run missing dispatches individually.
- **Two mid-cycle bugs caught by live dispatch, not local Django checks** — reinforces the working-loop pattern: unit tests + module load pass ≠ live PA gateway chain works.
- No candidate lessons for Playbook amendment this session.

**Rigby Tool Gap Ledger updates (via Rigby PA tool per `feedback_rigby_writes_workspace_deliverables`):**
- **#1** → `shipped_in_pr_3357`
- **#7 + #17 + #18** (grouped) → `shipped_in_pr_3356`
- Ledger content: 10,292 → 11,473 chars (2 resolution sections added by Rigby)

**Session pin `pa-2cc2f1c5102c4836` (labeled `s2868-slate-pick`) RETIRES at S2868 close.** Fresh mint required at S2869 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2869 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-2cc2f1c5102c4836` retired at S2868 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2869-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2869

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **Ledger #2 — `spider_status_tool.search` empty preview field** (~2 hr). Returns items with empty `preview` field despite `LegacySpiderData.raw_data['items'][*].title` having full content. Forces Claude ORM probe for keyword-check.

2. **Ledger #4 — `intelligence_tool.signal_clusters` multi-source filter** (~1 hr). Single-source `source_spider` filter only (has_key); no multi-source (has_any_keys) for parallel querying. Rigby loops 14x for AI-adjacent cluster discovery.

3. **Ledger #5 — schema/handler drift detection lint** (~2 hr). Currently `slated_for_S2846` but never landed. Recurrence risk: repeatable false-negative "no data" conclusions across every tool where handler capability + schema advertising drift (S2844 misdiagnosis root cause).

4. **Ledger #16 — close-ceremony twin-mirror enforcement gap** (S2863). Ranked fix candidates: (a) explicit close-checklist gate (~15 min); (b) hard-enforce in `session_lifecycle close` — refuse close without both deliverable IDs (~2 hr); (c) nightly audit task for recent handoffs missing mirrors (~1 hr).

5. **NEW at S2868 close — Exemption-list telemetry (Rigby zoom-out from slate #1).** Add counts-by-code/type instrumentation for `diagnostic_status='cleared'` so we can detect exemption-list-junk-drawer risk over time. 1st trigger only — watch for 2nd before opening.

6. **NEW at S2868 close — Stale-cleared row GC (Rigby zoom-out from slate #1).** Optional sweep for `diagnostic_status='cleared'` rows >180 days old that could be fully NULLed. Deferred until UI clutter becomes real.

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

18. **Carried — Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859 1st trigger observed; S2868 shipped 4 additions — this is the 2nd cycle).

19. **Carried — Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

20. **Carried — Fold C from S2861 close: shared JSONField projection helper**.

21. **Carried — Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

22. **Carried — openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

23. **Carried — Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

24. **Carried — A4 warm-up under ratified constraints** — S2846 6-line block still in force. A4 capabilities extended at S2868: see A4 Constraints below.

### What's forbidden at S2869 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2868 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`. S2857: operator can now verify enforcement without touching real spend via `simulate_enforcement`. S2858: post-clear re-flag likelihood inline on clear_* responses; list_caps read surface no longer degrades linearly with workspace count. S2859: `deliverable_tool.create` with `deliverable_type='ratification_record'` lands with verbatim title + no spurious diagnostic mark. S2860: Rigby can permanently delete deliverables directly via `deliverable_tool.delete` — two-factor gated, published-guarded, cascade-previewed, WARNING-audit-logged. S2861: Rigby can trim `autopilot_tool.history include_evidence=true` responses to specific top-level keys via `selected_fields=["evidence.<key>", "result.<key>"]`. S2862: huggingface → SignalCluster drop resolved — HF spider runs now produce extractable text; A4 AI/ML signal-cluster discovery restored (curated fallback). S2863: HuggingFaceSpider now hits the LIVE HF Hub API — 20/20 items with populated title+description, 2827 chars extractable text — A4 `intelligence_tool.signal_clusters source_spider='huggingface'` now returns live-data-backed AI/ML clusters, not curated topics. S2864: view-layer HF workaround removed after backfill enriched 460 pre-S2862 items; A4 feed queries for `source=huggingface` no longer require spider-name string-matching at read time. S2865: Rigby can now raw-HTTP GET/POST arbitrary http/https URLs via `web_fetch_tool` — closes the twice-bit F-DELEGATED verification gap. S2866: Rigby can now inspect any of 8 allowlisted DB models directly via `orm_inspect_tool` — closes the S2845-class false-negative gap where a tool surface reports 'no data' but rows exist under a different filter path. S2867: Rigby can now aggregate rows by any allowlisted field (single-value / FK-attname / DateTimeField-auto-day-bucket) via `orm_inspect_tool action='count_by'`. **S2868: (1) 4 additional deliverable_types exempt from `missing_initiative_id` diagnostic — Rigby's own Tool Gap Ledger (engineering_backlog) no longer flagged; ratification/engineering/session-scoped artifacts land clean by default. (2) Rigby can operator-clear a `missing_initiative_id` diagnostic via `deliverable_tool.clear_diagnostic` with sticky sentinel semantics — subsequent updates don't re-fire while alignment state is unchanged; workspace_mismatch still fires on transition. (3) Empty deliverable_type strings normalize to 'document' at write time. (4) `spider_status_tool.list` paginated with `limit/offset/total/has_more` + registry union — Rigby can iterate the full 90-spider inventory reliably; never-run spiders (reddit + sports_injuries) visible with `status='never_run'`; per-row `in_registry` triage flag.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail — cycle-triggered vs operator-triggered attributed correctly + auto_events_count vs operator_events_count now visible per-workspace in the fleet report; (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total — now cleanly filtered to enforcer-forced downgrades only; (i) all billing paths route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls priced at effective_model rates; (j) analytics-plane cost attribution correct; display fallbacks use canonical rates with explicit `estimated: true` flag; embedding pricing SoT preserved; (k) autopilot audit history (`autopilot_tool.history include_evidence=true`) surfaces evidence + result JSONField values inline for operators inspecting trigger / actor_user_id / reason; (l) operators + demo audiences can trigger the freeze + downgrade enforcer against a synthetic spend value via `workspace_budget_tool.simulate_enforcement`; (m) operators can inspect post-clear re-flag likelihood inline on clear_freeze/clear_downgrade responses; (n) workspace_budget_tool.list_caps read surface no longer degrades linearly with workspace count; (o) governance/ratification records land clean via `deliverable_tool.create` (deliverable_type=ratification_record); (p) hard delete of a deliverable is a first-class operator action via `deliverable_tool.delete`; (q) `autopilot_tool.history include_evidence=true` supports `selected_fields=["evidence.<key>", "result.<key>"]` for top-level JSON projection; (r) HuggingFace AI/ML signals enter SignalCluster aggregation; (s) `intelligence_tool.signal_clusters source_spider='huggingface'` returns LIVE Hub API data (not curated fallback); (t) `/api/spider-intelligence/feed/?source=huggingface` returns canonical items with title+url+description for historical + new rows without view-layer spider-name matching; (u) Rigby can raw-fetch arbitrary http/https URLs via `web_fetch_tool`; (v) Rigby can inspect any of 8 allowlisted Django models directly via `orm_inspect_tool`; (w) Rigby can aggregate any allowlisted model's rows by a single field via `orm_inspect_tool action='count_by'`. **(x) 4 new deliverable_types exempt from missing_initiative_id diagnostic (engineering_backlog / engineering_record / code_review / session_handoff) — Rigby's Tool Gap Ledger + session engineering artifacts land clean by default. (y) Rigby can operator-clear the missing_initiative_id diagnostic via `deliverable_tool.clear_diagnostic` with sticky sentinel semantics (subsequent updates don't re-fire while alignment state is unchanged). (z) `spider_status_tool.list` paginated + unions with the spider registry — full 90-spider inventory iterable via limit/offset/total/has_more, never-run spiders explicitly surfaced with status='never_run', per-row in_registry boolean for operator triage.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2868 close — what shipped (two PRs + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3356** `a7e90d1c3` — S2868 slate #1: deliverable diagnostic misfire fix (7 files, +735/-13)
- **PR #3357** `c1ac926b9` — S2868 slate #2: `spider_status_tool.list` pagination (3 files, +302/-8)
- **PR `<this docs cascade>`** — S2868 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump

**Workspace canonical:** Rigby Tool Gap Ledger updated by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables` (entries #1 + #7/#17/#18 marked shipped, 2 resolution sections added). S2868 close ratification envelope created by Rigby (deliverable ID recorded in handoff).

**Runtime impact:**
- `deliverable_tool` action enum: 17 → 18 (added `clear_diagnostic`).
- `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`: 1 → 5 types.
- 18 historical deliverable rows migrated to `cleared` sentinel via backfill.
- `spider_status_tool.list` returns 90 (was 88) with `include_registry=true` default — 2 registered-but-never-ran spiders now visible.
- Full 90-spider inventory paginated + iterable.

**Not shipped at S2868 close (deferred to S2869 or later):**
- Ledger #2 / #4 / #5 / #16 (remaining open ledger items)
- Exemption-list telemetry + stale-cleared row GC (both 1st-trigger folds from S2868 zoom-out)
- All prior deferred items from S2867 (`group_key_note`, high-cardinality guardrail) + S2866 (`allowed_fields`) + S2862 Q5.a fold + others carried

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2868)

See:
- **S2868 handoff (current):** `docs/handoffs/SESSION_2868_DELIVERABLE_DIAGNOSTIC_AND_SPIDER_STATUS_PAGINATION.md`
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
