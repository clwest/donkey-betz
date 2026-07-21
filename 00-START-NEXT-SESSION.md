# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2862 CLOSE → huggingface → SignalCluster drop FIXED (2026-07-21; picks up as S2863) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2862 close).** Chris-selected S2862 slate #1 (Rigby Tool Gap Ledger #3, S2845-open) shipped as **one PR / one commit**:

- **PR #3343** `fbfe10ff7` — S2862 slate #1: remove `'huggingface'` from `SPIDER_TARGET_URLS`
  - Routing config: `'huggingface': [...]` entry deleted from `ai_core/spiders/real_data_collector.py:104`; replaced with 12-line self-documenting comment block naming root cause + fall-through path + test file breadcrumb.
  - Root cause (grounded): HF Hub API items expose `modelId`/`id`/`pipeline_tag` but no `title`/`name`/`description`; `normalize_item()` field mappings can't populate readable text; extraction returns 0 chars; every signal dropped before clustering (22 rows/7d → 0 SignalCluster contributions).
  - Fix routes execution through the else-branch at `core/tasks_spiders.py:158`, invoking `HuggingFaceSpider.fetch_data()` which already builds items with title/summary/description.
  - 6 new pytest cases (`test_s2862_huggingface_signal_extraction.py`); 6/6 pass in 192s.
  - Post-merge E2E: 10/10 items now have title+description+summary, 588 chars extracted text, 1 SignalCluster candidate with 5 entity_tokens (mistral/llms/llama/stable/generation) — verified even under HF API HTTP 400 fallback path.

**Working loop validated at S2862:**
- 2-turn pre-code SIGN (turn 1: 7 grounded reads, Q4 F-BLOCKING on ORM sweep; turn 2: Claude ran ORM sweep = only 2/54 URL-path spiders drop, huggingface + openmeteo; AGREE-TO-BUILD Option C on all 5 Qs)
- 1 post-code SIGN (5 grounded reads including cross-repo consumer grep; AGREE-TO-SHIP on all 5 F-BLOCKING Qs; Q4 mods applied — "intentionally NOT re-added" phrasing + test-file breadcrumb)
- Post-recycle E2E confirmed huggingface spider run yields extractable text + reaches clustering

**Rigby Tool Gap Ledger updates (via Rigby PA tool per `feedback_rigby_writes_workspace_deliverables`):**
- Entry #3 (huggingface drop) moved to Shipped entries with status `shipped_in_pr_3343`
- **NEW open entry #13:** HuggingFaceSpider API params obsolete — `sort=trending` returns HTTP 400 on `/api/models`, `/api/datasets`, `/api/spaces`. Move to `sort=downloads`. ~30 min fix.

**Session pin `pa-95e7256e4f3d40cd` (labeled `s2862-open`) RETIRES at S2862 close.** Fresh mint required at S2863 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2863 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-95e7256e4f3d40cd` retired at S2862 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2863-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2863

Per `feedback_engineering_bias_over_audit`, list net-new first.

0. **NEW at S2862 close — Rigby Tool Gap Ledger #13 (Rigby-recommended for S2863 slate #1):**
   - **HuggingFaceSpider API params obsolete** — `sort=trending` on `/api/models`+`/datasets`+`/spaces` returns HTTP 400. Move to `sort=downloads` at `ai_core/spiders/specialized/huggingface_spider.py:86`. ~30 min fix. Small blast radius (1 file). Completes the S2862 arc by getting the LIVE HF API data flowing (not just the fallback curated topics). Tight trigger. Slate lead.

1. **Ledger #11 — Durable non-cascading audit table for deletes** — S2860 v1 uses `logger.warning('[DELIVERABLE_DELETE]')` as the audit trail because `DeliverableEvent` CASCADEs on the row. A dedicated append-only DB table (e.g., `DeliverableDeleteAudit`) would give durable structured queries. Deferred; awaits compliance/audit trigger or genuine forensic need. Not urgent.

2. **`simulate_enforcement` auto-clear-after-N-seconds** (S2857 first-trigger fold) — currently `dry_run=false` writes flags that persist until operator calls `clear_freeze`/`clear_downgrade`. Consider optional `auto_clear_after_seconds` param so a demo doesn't leave a workspace frozen if the operator forgets to clean up. Deferred — awaits explicit ask.

3. **`enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger) — de-duplicate the 4-item action-type list between `td_handlers_ops.py:4362` and `ops_autopilot/budget.py` write sites. ~1 hr refactor. Not urgent until a fifth type is added.

4. **`actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, 1st trigger — MIGRATION required). Deferred until schema-migration budget opens.

5. **`EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger) — `actor_user_id` + `trigger` + `simulated` (and growing) currently piped as kwargs on both enforce_ methods. Consolidate into an `EnforcementContext` dataclass. Deferred — awaits second independent trigger before Playbook amendment.

6. **`list_caps include_defaults=true` remaining perf costs** (S2858 concern 5, 1st trigger) — spend computation + is_frozen/is_downgraded lookups still per-row after PR #3334 batched the name lookup. Not urgent until fleet size makes it a slow ticket.

7. **Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859 1st trigger observed — needs 2nd/3rd independent trigger before adding types like `governance_charter`, `session_handoff`). Governed change per constant docstring; Playbook §14.2 threshold applies.

8. **Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"** — deeper substrate driver behind repeated exemption pressure. Requires UI/product decision (filterable diagnostic view? severity levels?). Watch for a 3rd/4th independent trigger before proposing a same-PR fix; NOT ready for slate — record only.

9. **NEW at S2861 close — Fold C: shared JSONField projection helper** — extract `project_jsonfields(row, selected_paths, allowed_prefixes, cap)` utility. First trigger observed at S2861 in `autopilot_tool.history`. Needs second tool trigger before build.

10. **NEW at S2861 close — Fold D: operator-surface discoverability for advanced PA-tool params** — `autopilot_tool.history` now has 3 opt-in payload knobs (`limit`, `include_evidence`, `selected_fields`); if operator UI hides schema helptext, advanced params ship "invisible."

11. **NEW at S2862 close — Q5.a bimodal collector architecture** (URL-path via `collect_spider_data_sync` + `normalize_item` vs spider-class path via `registry.get_spider_class` + `_run_spider_adapter`). When a spider exists in both, URL path silently wins — the HF failure mode. First trigger observed at S2862; only 2/54 URL-path spiders currently drop. `future_trigger` per Rigby Q5.

12. **NEW at S2862 close — Q5.b normalize_item ownership principle** — "when a spider has a class, prefer class-owned transformation; reserve `normalize_item` for URL-only sources." Design principle logged, no code action yet. `future_trigger`.

13. **NEW at S2862 close — openmeteo → SignalCluster drop (fold-carry)** — Only other URL-path spider dropping to 0 text (numeric weather forecast). Fixing routing alone wouldn't help; needs product decision on whether we want weather signals + what synthesis rules.

14. **NEW at S2862 close — `views_spider_intelligence.py:1217-1233` HF special-case removal** — Post-Option C stabilization, the HF description-reconstruction workaround guarded by `not description` becomes a no-op. Cleanup pass candidate; NOT blocking.

15. **Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855: `model_kind` dimension, `EMBEDDING_COSTS`+`MODEL_PRICES` unification, `pricing_catalog_version` field on LLMCallLog, LLMCallLog↔CostTracking schema-level provenance column.

16. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. See A4 Constraints below for the full capability list after S2862.

### What's forbidden at S2863 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Multi-source `source_spider` filter (Ledger candidate; ~1 hour)
- SignalCluster naming rewrite (Ledger candidate; ~1 day)
- `spider_status_tool.search` empty preview field (Ledger candidate; ~2 hours)
- `spider_status_tool.list` pagination (Ledger candidate; ~2 hours)
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2862 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`. S2857: operator can now verify enforcement without touching real spend via `simulate_enforcement`. S2858: post-clear re-flag likelihood inline on clear_* responses; list_caps read surface no longer degrades linearly with workspace count. S2859: `deliverable_tool.create` with `deliverable_type='ratification_record'` lands with verbatim title + no spurious diagnostic mark. S2860: Rigby can permanently delete deliverables directly via `deliverable_tool.delete` — two-factor gated, published-guarded, cascade-previewed, WARNING-audit-logged. S2861: Rigby can trim `autopilot_tool.history include_evidence=true` responses to specific top-level keys via `selected_fields=["evidence.<key>", "result.<key>"]`. **S2862: huggingface → SignalCluster drop resolved — HF spider runs now produce extractable text; A4 AI/ML signal-cluster discovery restored via `intelligence_tool.signal_clusters source_spider='huggingface'` (fully live once S2863 fixes HF Hub API `sort=trending` HTTP 400).**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail — cycle-triggered vs operator-triggered attributed correctly + auto_events_count vs operator_events_count now visible per-workspace in the fleet report; (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total — now cleanly filtered to enforcer-forced downgrades only; (i) all billing paths route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls priced at effective_model rates; (j) analytics-plane cost attribution correct; display fallbacks use canonical rates with explicit `estimated: true` flag; embedding pricing SoT preserved; (k) autopilot audit history (`autopilot_tool.history include_evidence=true`) surfaces evidence + result JSONField values inline for operators inspecting trigger / actor_user_id / reason; (l) operators + demo audiences can trigger the freeze + downgrade enforcer against a synthetic spend value via `workspace_budget_tool.simulate_enforcement`; (m) operators can inspect post-clear re-flag likelihood inline on clear_freeze/clear_downgrade responses; (n) workspace_budget_tool.list_caps read surface no longer degrades linearly with workspace count; (o) governance/ratification records land clean via `deliverable_tool.create` (deliverable_type=ratification_record); (p) hard delete of a deliverable is a first-class operator action via `deliverable_tool.delete`; (q) `autopilot_tool.history include_evidence=true` supports `selected_fields=["evidence.<key>", "result.<key>"]` for top-level JSON projection; **(r) HuggingFace AI/ML signals now enter SignalCluster aggregation — 22 rows/7d that previously dropped to 0 signals now yield 1+ signal per run with entity_tokens matching AI/ML domain (mistral/llms/llama/etc.); `intelligence_tool.signal_clusters` with `source_spider='huggingface'` returns non-empty results within ~24h post-merge.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2862 close — what shipped (one PR, one commit + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3343** `fbfe10ff7` — S2862 slate #1: remove `huggingface` from `SPIDER_TARGET_URLS` + 6 pytest cases
- **PR `<this docs cascade>`** — S2862 handoff + 00-START-NEXT-SESSION refresh + docs cascade

**Workspace canonical:** Rigby Tool Gap Ledger #3 marked shipped (`shipped_in_pr_3343`); new open entry #13 added for HF API param fix. Content mirror + ratification envelope written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables`.

**Runtime impact:**
- huggingface spider runs now produce properly-shaped items; A4 AI/ML signal-cluster discovery restored.
- E2E verified: 10/10 items with title+description+summary; 588 chars extracted text; 1 SignalCluster candidate with 5 entity_tokens.

**Not shipped at S2862 close (deferred to S2863 or later):**
- HF Hub API `sort=trending` HTTP 400 fix (Ledger #13) — Rigby-recommended next-slate lead
- openmeteo signal fix (product decision)
- `views_spider_intelligence.py` HF special-case cleanup
- All prior deferred items from S2861/S2859/S2858/S2857/S2856

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2862)

See:
- **S2862 handoff (current):** `docs/handoffs/SESSION_2862_HUGGINGFACE_SIGNAL_EXTRACTION_FIX.md`
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
