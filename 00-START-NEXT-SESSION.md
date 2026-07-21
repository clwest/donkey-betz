# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2867 CLOSE → count_by aggregate action shipped (2026-07-21; picks up as S2868) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2867 close).** Chris-selected S2867 slate #1 (Rigby Tool Gap Ledger 1st zoom-out fold from S2866, aggregate group-by counts) shipped as **one PR / one commit**:

- **PR #3353** `f201a7910` — S2867 slate #1: `count_by` action on `orm_inspect_tool` (5 files, +598/-9 lines)
  - `core/services/pa_tool_schemas.py` (+25) — action enum + `field` + `order_by_count` params.
  - `core/services/td_handlers_agents.py` (+140) — `count_by` handler branch + `_validate_groupby_field` + `_coerce_group_value`.
  - `core/tests/test_s2867_orm_count_by.py` (new, +414) — 27 pytest cases across 9 classes.
  - `core/tests/test_s2866_orm_inspect_tool.py` (±3) — baseline enum assertion updated for 5th action.
  - `tools/pa_local.sh` — session pin bump `pa-8005b98ba0524999` → `pa-f38da01b8355481f`.

**Discovery arc — 3 SIGN cycles:**
- Pre-code SIGN: 5 F-AGREE + 1 F-DISAGREE (Rigby pushed back on model-level blocks — per-field guards suffice) + 0 F-BLOCKING. Verified against source via 4 `repo_tool` calls.
- Post-code SIGN round 1 (live dispatch against 827 SignalClusters + 60333 LLMCallLogs): shapes correct, S2845-analog demo verified in one call, Q4 F-DISAGREE on `group_count_is_lower_bound` naming.
- Post-code SIGN round 2 all F-AGREE — applied Q4 fold by **dropping** the redundant field entirely (it always flipped with `truncated`; docstring carries the semantic). "Strictly subtractive shape change."

**Working loop observations at S2867:**
- `feedback_verify_rigby_tool_runs_before_trusting_sign` produced grounded SIGNs all 3 cycles (repo_tool grounding pre-code, live orm_inspect_tool dispatches post-code).
- `feedback_zoom_out_ask_per_rigby_sign` named the S2845-analog demo + high-cardinality risk in round 1, re-checked rejection paths + FK-attname in round 2.
- `feedback_claude_stdout_truncation_vs_ui_truncation` hit — pre-code SIGN truncated in Claude stdout mid-Q5; recovered by asking Rigby for Q5+Q6 delta (not re-framing as "you got cut off").
- No candidate lessons for Playbook amendment this session.

**Rigby Tool Gap Ledger updates (via Rigby PA tool per `feedback_rigby_writes_workspace_deliverables`):**
- **1st zoom-out fold from S2866** (aggregate group-by counts) → **Shipped**, `shipped_in_pr_3353`.

**Session pin `pa-f38da01b8355481f` (labeled `s2867-orm-count-by`) RETIRES at S2867 close.** Fresh mint required at S2868 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2868 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-f38da01b8355481f` retired at S2867 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2868-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2868

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2867 close — `group_key_note` UX hint on `count_by`** (S2867 post-code Q2 fold). Nice-to-have string like `"FK grouped on attname <field>_id"` or `"DateTimeField grouped by TruncDate(field)"` inline in the response. **First independent trigger observed.** Watch for 2nd trigger before opening; the existing `group_key` + `describe_model` combo already carries the info.

2. **NEW at S2867 close — High-cardinality guardrail on `count_by`** (S2867 post-code Q5 fold). Optional soft-warning when `total_matching` exceeds a threshold on a large table, nudging the caller to filter first. **First trigger.** Deferred until a slow-query experience report; row cap already bounds response size.

3. **Carried — Per-model `allowed_fields` explicit allowlist on `orm_inspect_tool`** (S2866 fold, still 1st trigger). Mitigates euphemistic-name slip-through class.

4. **Carried — Provider-specific composite additions.** Reactive; watch for new integrations.

5. **Carried — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.** Still 2 independent triggers, not promoted. ~30 min doc/deliverable.

6. **Carried — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate). 1st trigger only from S2864; watch for 2nd/3rd.

7. **Ledger — Multi-source `source_spider` filter** (~1 hour).

8. **Ledger #2 — `spider_status_tool.search` empty preview field** (~2 hours).

9. **Ledger #1 — `spider_status_tool.list` pagination** (~2 hours).

10. **Ledger #11 — Durable non-cascading audit table for deletes** — deferred; awaits compliance/audit trigger.

11. **`simulate_enforcement` auto-clear-after-N-seconds** (S2857 fold) — deferred; awaits explicit ask.

12. **`enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger).

13. **`actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, MIGRATION required). Deferred until schema-migration budget opens.

14. **`EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger).

15. **`list_caps include_defaults=true` remaining perf costs** (S2858, 1st trigger).

16. **Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859 1st trigger observed).

17. **Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

18. **Fold C from S2861 close: shared JSONField projection helper**.

19. **Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

20. **openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

21. **Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

22. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. See A4 Constraints below for the full capability list after S2867.

### What's forbidden at S2868 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2867 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`. S2857: operator can now verify enforcement without touching real spend via `simulate_enforcement`. S2858: post-clear re-flag likelihood inline on clear_* responses; list_caps read surface no longer degrades linearly with workspace count. S2859: `deliverable_tool.create` with `deliverable_type='ratification_record'` lands with verbatim title + no spurious diagnostic mark. S2860: Rigby can permanently delete deliverables directly via `deliverable_tool.delete` — two-factor gated, published-guarded, cascade-previewed, WARNING-audit-logged. S2861: Rigby can trim `autopilot_tool.history include_evidence=true` responses to specific top-level keys via `selected_fields=["evidence.<key>", "result.<key>"]`. S2862: huggingface → SignalCluster drop resolved — HF spider runs now produce extractable text; A4 AI/ML signal-cluster discovery restored (curated fallback). S2863: HuggingFaceSpider now hits the LIVE HF Hub API — 20/20 items with populated title+description, 2827 chars extractable text — A4 `intelligence_tool.signal_clusters source_spider='huggingface'` now returns live-data-backed AI/ML clusters, not curated topics. S2864: view-layer HF workaround removed after backfill enriched 460 pre-S2862 items; A4 feed queries for `source=huggingface` no longer require spider-name string-matching at read time. S2865: Rigby can now raw-HTTP GET/POST arbitrary http/https URLs via `web_fetch_tool` — closes the twice-bit F-DELEGATED verification gap. S2866: Rigby can now inspect any of 8 allowlisted DB models directly via `orm_inspect_tool` — closes the S2845-class false-negative gap where a tool surface reports 'no data' but rows exist under a different filter path. External endpoint verify (S2865) + internal DB verify (S2866) together cover the F-DELEGATED verification surface. **S2867: Rigby can now aggregate rows by any allowlisted field (single-value / FK-attname / DateTimeField-auto-day-bucket) via `orm_inspect_tool action='count_by'` — closes the "how many rows match X by day/status/source?" ask that motivated the S2866 zoom-out fold. Post-merge live-verified: 7 pattern_types on 827 SignalClusters; 11 day-buckets on same set; 2 workspace groups on 60333 LLMCallLogs including null bucket; JSONField rejection with nudge-to-`has_key`.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail — cycle-triggered vs operator-triggered attributed correctly + auto_events_count vs operator_events_count now visible per-workspace in the fleet report; (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total — now cleanly filtered to enforcer-forced downgrades only; (i) all billing paths route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls priced at effective_model rates; (j) analytics-plane cost attribution correct; display fallbacks use canonical rates with explicit `estimated: true` flag; embedding pricing SoT preserved; (k) autopilot audit history (`autopilot_tool.history include_evidence=true`) surfaces evidence + result JSONField values inline for operators inspecting trigger / actor_user_id / reason; (l) operators + demo audiences can trigger the freeze + downgrade enforcer against a synthetic spend value via `workspace_budget_tool.simulate_enforcement`; (m) operators can inspect post-clear re-flag likelihood inline on clear_freeze/clear_downgrade responses; (n) workspace_budget_tool.list_caps read surface no longer degrades linearly with workspace count; (o) governance/ratification records land clean via `deliverable_tool.create` (deliverable_type=ratification_record); (p) hard delete of a deliverable is a first-class operator action via `deliverable_tool.delete`; (q) `autopilot_tool.history include_evidence=true` supports `selected_fields=["evidence.<key>", "result.<key>"]` for top-level JSON projection; (r) HuggingFace AI/ML signals enter SignalCluster aggregation; (s) `intelligence_tool.signal_clusters source_spider='huggingface'` returns LIVE Hub API data (not curated fallback); (t) `/api/spider-intelligence/feed/?source=huggingface` returns canonical items with title+url+description for historical + new rows without view-layer spider-name matching; (u) Rigby can raw-fetch arbitrary http/https URLs via `web_fetch_tool`; (v) Rigby can inspect any of 8 allowlisted Django models directly via `orm_inspect_tool`. **(w) Rigby can aggregate any allowlisted model's rows by a single field via `orm_inspect_tool action='count_by'` (CharField/TextField/IntegerField/BooleanField/DateField grouped as-is; ForeignKey grouped on `<field>_id` attname avoiding JOIN; DateTimeField auto-buckets to day via `TruncDate`; JSONField / sensitive-by-name / expensive-text-field rejected with clear errors; response cardinality bounded default 50 / max 500 with truncation semantics on the single `truncated` flag). Post-merge live-verified: 4 dispatches against real DB shapes correct, S2845-analog escape hatch works via `has_key` filter + count_by in one call.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2867 close — what shipped (one PR, one commit + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3353** `f201a7910` — S2867 slate #1: `count_by` action on `orm_inspect_tool` (5 files, +598/-9 lines)
- **PR `<this docs cascade>`** — S2867 handoff + 00-START-NEXT-SESSION refresh

**Workspace canonical:** Rigby Tool Gap Ledger 1st zoom-out fold from S2866 marked shipped (`shipped_in_pr_3353`). Ledger update + S2867 close summary + ratification envelope written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables`.

**Runtime impact:**
- `orm_inspect_tool` now supports 5 actions (was 4). New action `count_by` closes the "row count by field" diagnostic-rung gap.
- 27 new tests added; 63 total for orm_inspect_tool (36 baseline + 27 count_by).
- Post-merge live dispatches proved E2E: 7 pattern_types on 827 SignalClusters via categorical grouping, 11 day-buckets via DateTimeField auto-day, 2 workspace groups on 60333 LLMCallLogs via FK-attname (including null bucket), JSONField rejection with actionable nudge.

**Not shipped at S2867 close (deferred to S2868 or later):**
- `group_key_note` UX hint (1st trigger — S2867 Q2 zoom-out)
- High-cardinality guardrail warning (1st trigger — S2867 Q5 zoom-out)
- Per-model `allowed_fields` (still 1st trigger from S2866)
- S2862 Q5.a fold promotion to spec_backlog
- SIGN-discipline Playbook amendment (still 1st trigger only — S2864)
- openmeteo signal fix (product decision)
- All prior deferred items from S2866/S2865/S2864/S2863/S2862/S2861/S2859/S2858/S2857/S2856

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2867)

See:
- **S2867 handoff (current):** `docs/handoffs/SESSION_2867_ORM_COUNT_BY.md`
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
