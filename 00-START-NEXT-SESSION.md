# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2864 CLOSE → HF backfill + view-layer workaround removal shipped (2026-07-21; picks up as S2865) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2864 close).** Chris-selected S2864 slate #1 (Rigby Tool Gap Ledger #14, originally logged at S2863 close as "safe no-op cleanup" and mid-session reclassified to "confirmed load-bearing → root-cause fix via historical enrichment") shipped as **one PR / one commit** after two mid-session pivots:

- **PR #3347** `5cb39c4af` — S2864 slate #1: backfill migration + view-layer workaround removal
  - `core/management/commands/backfill_huggingface_items.py` (new) — enrich pre-S2862 `LegacySpiderData` HF items with `title`/`url`/`description` in the same pipe format the view was reconstructing at read time. Idempotent, batched, dry-run supported.
  - `core/views_spider_intelligence.py` (-22 lines) — delete HF description block (was 1217-1233) + HF URL block (was 1239-1241). GitHub URL block preserved.
  - `core/tests/test_s2864_huggingface_backfill.py` (new, 167 lines) — 11 pytest cases across 2 classes, 11/11 passed in 193s.
  - Local backfill executed: rows_scanned=562, rows_updated=23, items_enriched=460, items_skipped_has_title=59, items_skipped_no_id=0. Post-run ORM verify: 519/519 items (100%) have title+description.
  - E2E verify: `curl /api/spider-intelligence/feed/?source=huggingface&limit=10` → 10/10 items populated post-cleanup.

**Discovery arc — 2 pivots to reach the ship-able landing:**
- **Pivot 1 (safe no-op → F-BLOCKING revert):** Coded original view-cleanup based on pre-code SIGN AGREE-TO-BUILD. Rigby's post-code Q4 **F-DELEGATED-TO-CLAUDE** ORM check found 115/120 sampled historical items had empty description. Reverted — workaround was load-bearing for pre-S2862 rows.
- **Pivot 2 (normalize_item HF branch → discovered dead-code destination):** Started designing HF-specific branch in `real_data_collector.py:normalize_item`. Traced `git log` — S2862 already removed `huggingface` from `SPIDER_TARGET_URLS`, so `normalize_item` no longer runs for HF. Would be dead code. Aborted.
- **Pivot 3 (backfill = actual closure):** Chris D-verdict RATIFIED. Enrich historical rows so view-workaround can be safely deleted. Ship. ✅

**Working loop observations at S2864:**
- Rigby's Q4 F-DELEGATED-TO-CLAUDE at post-code SIGN caught the F-BLOCKING that pre-code SIGN Q1 (verified on wrong data source) missed. Working loop worked — at cost of one revert cycle.
- Lesson candidate: *"When a proposed code deletion depends on 'field X is populated,' pre-code SIGN MUST verify field population at the ACTUAL persisted/served source of truth (ORM), not just at the code path that COULD populate it."* Watch for 2nd/3rd trigger before Playbook amendment.

**Rigby Tool Gap Ledger updates (via Rigby PA tool per `feedback_rigby_writes_workspace_deliverables`):**
- **Entry #14** (HF view-layer workaround cleanup) moved to Shipped, `shipped_in_pr_3347`.
- **Entry #15** (PA raw HTTP fetch tool) remains open — Rigby's inability to raw-HTTP/ORM inspect forced Claude to run the F-DELEGATED ORM check that caught the F-BLOCKING. Twice bit now (S2863 Q1 + S2864 post-code Q4). Bumped priority as candidate lead for S2865.

**S2862 Q5.a bimodal-collector fold: 2nd independent trigger.** Rigby recommends promoting to spec_backlog/initiative: *"collector paths must converge on a single normalized schema; no view-layer spider special casing."* Not a Playbook amendment yet — small tracked-backlog entry.

**Session pin `pa-f78ff19b2ce0496c` (labeled `s2864-hf-view-cleanup`) RETIRES at S2864 close.** Fresh mint required at S2865 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2865 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-f78ff19b2ce0496c` retired at S2864 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2865-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2865

Per `feedback_engineering_bias_over_audit`, list net-new first.

0. **NEW at S2864 close — Rigby Tool Gap Ledger #15 (Rigby-recommended for S2865 slate #1)** — **PA raw HTTP fetch tool**. Twice bit now (S2863 Q1 + S2864 post-code Q4 both required Claude off-tool workarounds because Rigby can't raw-HTTP/ORM inspect). Minimal `web_fetch_tool` returning status + JSON/text. ~1-2 hr scope. Directly reduces future SIGN-cycle friction.

1. **NEW at S2864 close — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.** Two independent triggers now observed. Rigby Q5 recommendation. Small doc/deliverable, ~30 min. Sets up next investigation trigger. Principle: "collector paths must converge on a single normalized schema; no view-layer spider special casing."

2. **NEW at S2864 close — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate). 1st trigger observed at S2864. Watch for 2nd/3rd trigger; not codified this session.

3. **Ledger #11 — Durable non-cascading audit table for deletes** — S2860 v1 uses `logger.warning('[DELIVERABLE_DELETE]')` as the audit trail because `DeliverableEvent` CASCADEs. A dedicated append-only DB table (e.g., `DeliverableDeleteAudit`) would give durable structured queries. Deferred; awaits compliance/audit trigger or genuine forensic need.

4. **`simulate_enforcement` auto-clear-after-N-seconds** (S2857 first-trigger fold) — currently `dry_run=false` writes flags that persist until operator calls `clear_freeze`/`clear_downgrade`. Consider optional `auto_clear_after_seconds` param. Deferred — awaits explicit ask.

5. **`enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger) — de-duplicate the 4-item action-type list between `td_handlers_ops.py:4362` and `ops_autopilot/budget.py`. ~1 hr refactor. Not urgent until a fifth type is added.

6. **`actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, 1st trigger — MIGRATION required). Deferred until schema-migration budget opens.

7. **`EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger). Deferred — awaits second independent trigger before Playbook amendment.

8. **`list_caps include_defaults=true` remaining perf costs** (S2858 concern 5, 1st trigger). Not urgent until fleet size makes it a slow ticket.

9. **Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859 1st trigger observed — needs 2nd/3rd independent trigger).

10. **Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"** — deeper substrate driver behind repeated exemption pressure. Requires UI/product decision. Watch for 3rd/4th independent trigger.

11. **Fold C from S2861 close: shared JSONField projection helper** — extract `project_jsonfields(row, selected_paths, allowed_prefixes, cap)`. First trigger observed at S2861. Needs second tool trigger before build.

12. **Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params** — `autopilot_tool.history` now has 3 opt-in payload knobs. If operator UI hides schema helptext, advanced params ship "invisible."

13. **openmeteo → SignalCluster drop (fold-carry from S2862)** — only other URL-path spider dropping to 0 text (numeric weather forecast). Fixing routing alone wouldn't help; needs product decision on whether we want weather signals + what synthesis rules.

14. **Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855: `model_kind` dimension, `EMBEDDING_COSTS`+`MODEL_PRICES` unification, `pricing_catalog_version` field on LLMCallLog, LLMCallLog↔CostTracking schema-level provenance column.

15. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. See A4 Constraints below for the full capability list after S2864.

### What's forbidden at S2865 (D6 moratorium still in force)

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2864 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`. S2857: operator can now verify enforcement without touching real spend via `simulate_enforcement`. S2858: post-clear re-flag likelihood inline on clear_* responses; list_caps read surface no longer degrades linearly with workspace count. S2859: `deliverable_tool.create` with `deliverable_type='ratification_record'` lands with verbatim title + no spurious diagnostic mark. S2860: Rigby can permanently delete deliverables directly via `deliverable_tool.delete` — two-factor gated, published-guarded, cascade-previewed, WARNING-audit-logged. S2861: Rigby can trim `autopilot_tool.history include_evidence=true` responses to specific top-level keys via `selected_fields=["evidence.<key>", "result.<key>"]`. S2862: huggingface → SignalCluster drop resolved — HF spider runs now produce extractable text; A4 AI/ML signal-cluster discovery restored (curated fallback). S2863: HuggingFaceSpider now hits the LIVE HF Hub API — 20/20 items with populated title+description, 2827 chars extractable text — A4 `intelligence_tool.signal_clusters source_spider='huggingface'` now returns live-data-backed AI/ML clusters, not curated topics. **S2864: view-layer HF workaround removed after backfill enriched 460 pre-S2862 items; A4 feed queries for `source=huggingface` no longer require spider-name string-matching at read time — clean canonical shape across all HF rows (historical + new).**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail — cycle-triggered vs operator-triggered attributed correctly + auto_events_count vs operator_events_count now visible per-workspace in the fleet report; (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total — now cleanly filtered to enforcer-forced downgrades only; (i) all billing paths route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls priced at effective_model rates; (j) analytics-plane cost attribution correct; display fallbacks use canonical rates with explicit `estimated: true` flag; embedding pricing SoT preserved; (k) autopilot audit history (`autopilot_tool.history include_evidence=true`) surfaces evidence + result JSONField values inline for operators inspecting trigger / actor_user_id / reason; (l) operators + demo audiences can trigger the freeze + downgrade enforcer against a synthetic spend value via `workspace_budget_tool.simulate_enforcement`; (m) operators can inspect post-clear re-flag likelihood inline on clear_freeze/clear_downgrade responses; (n) workspace_budget_tool.list_caps read surface no longer degrades linearly with workspace count; (o) governance/ratification records land clean via `deliverable_tool.create` (deliverable_type=ratification_record); (p) hard delete of a deliverable is a first-class operator action via `deliverable_tool.delete`; (q) `autopilot_tool.history include_evidence=true` supports `selected_fields=["evidence.<key>", "result.<key>"]` for top-level JSON projection; (r) HuggingFace AI/ML signals enter SignalCluster aggregation — 22 rows/7d that previously dropped to 0 signals now yield 1+ signal per run with entity_tokens matching AI/ML domain; (s) `intelligence_tool.signal_clusters source_spider='huggingface'` returns LIVE Hub API data (not curated fallback) — 20 items/run, 100% with populated title+description; **(t) `/api/spider-intelligence/feed/?source=huggingface` returns canonical items with title+url+description for historical + new rows without view-layer spider-name matching — 519/519 items now populated post-backfill.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2864 close — what shipped (one PR, one commit + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3347** `5cb39c4af` — S2864 slate #1: backfill command + tests + view-cleanup (3 files, +332 -22)
- **PR `<this docs cascade>`** — S2864 handoff + 00-START-NEXT-SESSION refresh + pa_local.sh pin bump

**Workspace canonical:** Rigby Tool Gap Ledger #14 marked shipped (`shipped_in_pr_3347`); Ledger entry #15 remains open (bumped priority as S2865 candidate lead). Ledger + S2864 close summary + ratification envelope written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables`.

**Runtime impact:**
- 460 pre-S2862 HF items enriched in-place with title/url/description.
- 519/519 HF items now have canonical fields populated (100% coverage).
- View-layer HF spider-name string matching removed — feed handler is now purely generic.
- HF-arc closed: S2862 (route forward through class path) + S2863 (fix `sort=downloads`) + S2864 (backfill historical + remove workaround) compose.

**Not shipped at S2864 close (deferred to S2865 or later):**
- Ledger #15 PA raw HTTP fetch tool (Rigby-recommended next-slate lead)
- S2862 Q5.a fold promotion to spec_backlog
- SIGN-discipline Playbook amendment (1st trigger only)
- openmeteo signal fix (product decision)
- All prior deferred items from S2863/S2862/S2861/S2859/S2858/S2857/S2856

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2864)

See:
- **S2864 handoff (current):** `docs/handoffs/SESSION_2864_HF_BACKFILL_VIEW_CLEANUP.md`
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
