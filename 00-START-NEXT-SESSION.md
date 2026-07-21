# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2861 CLOSE → `autopilot_tool.history selected_fields` SHIPPED (2026-07-21; picks up as S2862) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2861 close).** Chris-selected S2861 slate #1 (S2856 Q5c zoom-out fold, Rigby Tool Gap Ledger #6) shipped as **one PR / one commit**:

- **PR #3341** `54e9d5779` — S2861 slate #1: `autopilot_tool.history selected_fields` projection
  - Schema: new `selected_fields: array<string>` on `autopilot_tool`; dot-notation `evidence.<key>` / `result.<key>` only; max 20 paths; ignored unless `include_evidence=true`; response echoes server-accepted list post-validation.
  - Handler: allowlist tuple `_ALLOWED_PROJECTION_PREFIXES = ('evidence', 'result')` for future extension; cap-then-validate; both prefixes projected when set; missing keys silently omitted; non-dict src defensively demoted to `{}`.
  - v1 = **Option C**: top-level projection only; nested dicts/lists returned verbatim when top-level key selected (matches cycle-log rows at `ops_autopilot/core.py:353`).
  - 13 new pytest cases (`test_s2861_autopilot_selected_fields.py`); 49/49 pass across S2856 + S2857 + S2861 in ~198s.

**Working loop validated at S2861:**
- 2-turn pre-code SIGN + concurrence check (turn 1: 5 grounded reads; Q1 F-BLOCKING on payload-shape verification; turn 2: I verified write-sites at `budget.py:295-310` + `budget.py:475-508` + `core.py:337-356`; revealed mixed flat/nested → Option C selected; AGREE-TO-BUILD on all 5 Qs)
- 1 post-code SIGN (4 grounded diff reads; AGREE-TO-SHIP on all 5 F-BLOCKING Qs; 3 non-blocking future-trigger folds recorded)
- Post-recycle Rigby E2E confirmed all 3 dispatch shapes (baseline / projection / gate-off) end-to-end on Donkey Betz workspace

**Session pin `pa-d982a2e9f84a4381` (labeled `s2861-open`) RETIRES at S2861 close.** Fresh mint required at S2862 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2862 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-d982a2e9f84a4381` retired at S2861 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2862-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2862

Per `feedback_engineering_bias_over_audit`, list net-new first.

0. **Zoom-out flag surfaced at S2861 open by Rigby (Chris to consider for slate #1):**
   - **huggingface → SignalCluster drop (Rigby Tool Gap Ledger #3)** — real data loss in A4-critical AI/ML domain (~half day fix; suspected `is_processed=False` + `embedding_text=''` gate at `signal_aggregation_service.py:262`). Rigby ranked ABOVE deferred list items #4/#6 at S2861 slate selection. Chose #3 selected_fields at S2861 for tighter trigger; huggingface fix now top-of-list for S2862.

1. **Ledger #11 — Durable non-cascading audit table for deletes** — S2860 v1 uses `logger.warning('[DELIVERABLE_DELETE]')` as the audit trail because `DeliverableEvent` CASCADEs on the row. A dedicated append-only DB table (e.g., `DeliverableDeleteAudit`) would give durable structured queries. Deferred; awaits compliance/audit trigger or genuine forensic need. Not urgent.

2. **`simulate_enforcement` auto-clear-after-N-seconds** (S2857 first-trigger fold) — currently `dry_run=false` writes flags that persist until operator calls `clear_freeze`/`clear_downgrade`. Consider optional `auto_clear_after_seconds` param so a demo doesn't leave a workspace frozen if the operator forgets to clean up. Deferred — awaits explicit ask.

3. **`enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger) — de-duplicate the 4-item action-type list between `td_handlers_ops.py:4362` and `ops_autopilot/budget.py` write sites. ~1 hr refactor. Not urgent until a fifth type is added.

4. **`actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, 1st trigger — MIGRATION required). Deferred until schema-migration budget opens.

5. **`EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger) — `actor_user_id` + `trigger` + `simulated` (and growing) currently piped as kwargs on both enforce_ methods. Consolidate into an `EnforcementContext` dataclass. Deferred — awaits second independent trigger before Playbook amendment.

6. **`list_caps include_defaults=true` remaining perf costs** (S2858 concern 5, 1st trigger) — spend computation + is_frozen/is_downgraded lookups still per-row after PR #3334 batched the name lookup. Not urgent until fleet size makes it a slow ticket.

7. **Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859 1st trigger observed — needs 2nd/3rd independent trigger before adding types like `governance_charter`, `session_handoff`). Governed change per constant docstring; Playbook §14.2 threshold applies.

8. **Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"** — deeper substrate driver behind repeated exemption pressure. Requires UI/product decision (filterable diagnostic view? severity levels?). Watch for a 3rd/4th independent trigger before proposing a same-PR fix; NOT ready for slate — record only.

9. **NEW at S2861 close — Fold C: shared JSONField projection helper** — extract `project_jsonfields(row, selected_paths, allowed_prefixes, cap)` utility. First trigger observed at S2861 in `autopilot_tool.history`. Needs second tool trigger before build (per `same_pr_mitigatable=false`).

10. **NEW at S2861 close — Fold D: operator-surface discoverability for advanced PA-tool params** — `autopilot_tool.history` now has 3 opt-in payload knobs (`limit`, `include_evidence`, `selected_fields`); if operator UI hides schema helptext, advanced params ship "invisible." Partial same-PR mitigation via schema cross-references. Full mitigation needs UI/product surface work.

11. **NEW at S2861 close — Fold E: `selected_fields` dedupe / echo normalization** — duplicates preserved; non-string entries `str()`-coerced (e.g., `None` → `"None"`). Safe but potentially confusing. Watch for operator confusion signal before shipping.

12. **Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855: `model_kind` dimension, `EMBEDDING_COSTS`+`MODEL_PRICES` unification, `pricing_catalog_version` field on LLMCallLog, LLMCallLog↔CostTracking schema-level provenance column. None currently justified without a specific reconciliation trigger.

13. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. See A4 Constraints below for the full capability list after S2861.

### What's forbidden at S2862 (D6 moratorium still in force)

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2861 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`. S2857: operator can now verify enforcement without touching real spend via `simulate_enforcement`. S2858: post-clear re-flag likelihood inline on clear_* responses; list_caps read surface no longer degrades linearly with workspace count. S2859: `deliverable_tool.create` with `deliverable_type='ratification_record'` lands with verbatim title + no spurious diagnostic mark. S2860: Rigby can permanently delete deliverables directly via `deliverable_tool.delete` — two-factor gated, published-guarded, cascade-previewed, WARNING-audit-logged. **S2861: Rigby can trim `autopilot_tool.history include_evidence=true` responses to specific top-level keys via `selected_fields=[\"evidence.<key>\", \"result.<key>\"]` — no more dumping full JSONField blobs for narrow provenance queries.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail — cycle-triggered vs operator-triggered attributed correctly + auto_events_count vs operator_events_count now visible per-workspace in the fleet report; (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total — now cleanly filtered to enforcer-forced downgrades only; (i) all billing paths route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls priced at effective_model rates; (j) analytics-plane cost attribution correct; display fallbacks use canonical rates with explicit `estimated: true` flag; embedding pricing SoT preserved; (k) autopilot audit history (`autopilot_tool.history include_evidence=true`) surfaces evidence + result JSONField values inline for operators inspecting trigger / actor_user_id / reason; (l) operators + demo audiences can trigger the freeze + downgrade enforcer against a synthetic spend value via `workspace_budget_tool.simulate_enforcement` — dry-run reveals decisions + thresholds without state writes; live path writes real flags with `evidence.simulated=True` marker (excluded from fleet report by default); (m) operators can now inspect post-clear re-flag likelihood inline on clear_freeze/clear_downgrade responses (no follow-up get_status call needed); status_context block encodes enforcer semantics with re_flag_likely tied to EXPLICIT cap only + explicit reason string; (n) workspace_budget_tool.list_caps read surface no longer degrades linearly with workspace count — batched name lookup via single filter().values_list() query regardless of row count; (o) governance/ratification records land clean via `deliverable_tool.create` (deliverable_type=ratification_record) — no auto-title-prefix, no spurious missing_initiative_id diagnostic hiding the row from the workspace UI, no manual Django-shell cleanup required; (p) hard delete of a deliverable is a first-class operator action via `deliverable_tool.delete` — safe by default (dry-run preview shows cascade counts), two-factor gated for the live path (dry_run=false + confirm=true), published rows protected by explicit allow_published+reason escape hatch, every delete WARNING-audited with full context (deliverable_id / user_id / trace_id / cascades / reason); **(q) `autopilot_tool.history include_evidence=true` supports `selected_fields=[\"evidence.<key>\", \"result.<key>\"]` for top-level JSON projection — operators can request specific provenance fields (e.g., `evidence.actor_user_id`, `evidence.trigger`, `result.reason`) instead of full JSONField dumps; response echoes server-accepted paths post-validation.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2861 close — what shipped (one PR, one commit + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3341** `54e9d5779` — S2861 slate #1: expose `autopilot_tool.history selected_fields` projection
- **PR `<this docs cascade>`** — S2861 handoff + 00-START-NEXT-SESSION refresh + docs cascade

**Workspace canonical:** Content mirror + ratification envelope written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables` at S2861 close-cascade. Ledger entry #6 marked complete; folds C/D/E recorded as future-trigger candidates.

**Runtime impact:**
- `autopilot_tool.history` gains 3rd opt-in payload knob (`selected_fields`) alongside `limit` + `include_evidence`. Backward-compatible: absent/empty preserves prior S2856 behavior.
- GPT-5.2 can now issue narrow provenance queries (`selected_fields=['evidence.actor_user_id', 'result.reason']`) instead of dumping full JSONField blobs.
- Cycle-log rows with deeply nested payloads (evidence at `core.py:353` = `{k:v for k,v in results.items()}`) are supported via Option C: top-level projection returns nested value verbatim.

**Not shipped at S2861 close (deferred to S2862 or later):**
- Huggingface → SignalCluster drop fix (Ledger #3) — Rigby-recommended next-slate lead
- Ledger #11 durable delete audit table (no compliance trigger)
- All prior deferred items from S2859/S2858/S2857/S2856
- Fold C shared projection helper (needs 2nd trigger)
- Fold D operator-surface discoverability (UI work outside PA slate)

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2861)

See:
- **S2861 handoff (current):** `docs/handoffs/SESSION_2861_AUTOPILOT_SELECTED_FIELDS_SHIPPED.md`
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
