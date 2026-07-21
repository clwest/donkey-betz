# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2866 CLOSE → bounded ORM inspector shipped (2026-07-21; picks up as S2867) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2866 close).** Chris-selected S2866 slate #1 (Rigby Tool Gap Ledger #3, bounded ORM row inspector) shipped as **one PR / one commit** — natural counterpart to S2865's `web_fetch_tool` (external endpoint verify → this = internal DB verify):

- **PR #3351** `f52c1d854` — S2866 slate #1: `orm_inspect_tool` schema + handler + registration + tests (5 files, +907 lines)
  - `core/services/pa_tool_schemas.py` (+100 lines) — `orm_inspect_tool` schema after `web_fetch_tool`.
  - `core/services/td_handlers_agents.py` (+390 lines) — `_handle_orm_inspect` next to `_handle_web_fetch`.
  - `core/services/tool_dispatcher.py` (+2 lines) — registration.
  - `core/tests/test_s2866_orm_inspect_tool.py` (new, 414 lines) — 36 pytest cases across 9 classes, 36/36 passed in 113ms.
  - `tools/pa_local.sh` — session pin bump `pa-ba8b342e1f12484d` → `pa-8005b98ba0524999`.

**Discovery arc — 3 SIGN cycles (one more than S2865):**
- Pre-code SIGN caught 1 F-BLOCKING (JSONField default for LLMCallLog/AutopilotAction/OpsRun) + 4 F-AGREE folds (order_by, per-model policy, startswith/istartswith, expensive-field guardrails).
- Post-code SIGN round 1 caught real bug: naive `'token' in name.lower()` substring-matched `prompt_tokens`/`total_tokens`. Word-boundary fix + regression tests shipped.
- Post-code SIGN round 2 all F-AGREE — redaction fix verified, real-data `source_breakdown__has_key='hackernews'` returned 65 rows populated with actual values.

**Working loop observations at S2866:**
- `feedback_verify_rigby_tool_runs_before_trusting_sign` worked as designed all 3 cycles — pre-code Rigby ran `deliverable_tool.detail(b5a22ea7)` + `repo_tool.search(db_health_tool)` before Q1/Q5 answers; post-code round 1 caught over-redaction via live `describe_model` inspection that would have shipped broken redaction.
- `feedback_zoom_out_ask_per_rigby_sign` produced value both post-code rounds — named the "aggregate group-by counts" next-rung gap + euphemistic-name slip-through class. Both folded as v2 docstring notes.
- Case 2 (S2845 has_key demo returned 0 rows) — framing F-BLOCKING that resolved to "tool did the right thing." Ground-truth ORM check: 827 SignalClusters, 0 with `source_breakdown.huggingface` — the tool proved persisted-state truth instead of us chasing a phantom. Perfect illustration of what the tool is FOR.
- No candidate lessons for Playbook amendment this session.

**Rigby Tool Gap Ledger updates (via Rigby PA tool per `feedback_rigby_writes_workspace_deliverables`):**
- **Entry #3** (bounded ORM inspector) moved to Shipped, `shipped_in_pr_3351`.

**Session pin `pa-8005b98ba0524999` (labeled `s2866-orm-inspector-tool`) RETIRES at S2866 close.** Fresh mint required at S2867 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2867 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-8005b98ba0524999` retired at S2866 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2867-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2867

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2866 close — Aggregate group-by counts on `orm_inspect_tool`.** Rigby post-code round 1 zoom-out named this as the next diagnostic rung after row inspection. "Give me 5 rows" is great for shape; "how many rows match X by day/status/source?" is the next question. ~2-3 hr scope, single-PR. Would add `action='count_by'` with field + optional filter_kwargs. **First independent trigger observed.** Watch for 2nd/3rd trigger before opening.

2. **NEW at S2866 close — Per-model `allowed_fields` explicit allowlist on `orm_inspect_tool`.** Rigby post-code round 2 zoom-out surfaced euphemistic-name slip-through class (`opaque`/`blob`/`payload`/`header_value`). Mitigation: replace global sensitive-name heuristic with per-model explicit `allowed_fields` list. **First trigger.** Deferred until a real slip-through occurs; JSONField-omission-default currently covers the highest-risk case.

3. **NEW at S2866 close — Provider-specific composite additions.** Round-2 fold surfaced provider-specific names (`slack_signing_secret`, `github_pat`, `openai_key`, etc.). Some added inline (`x_api_key`, `openai_key`, `anthropic_key`, `github_pat`, `auth_header`, `session_key`). Watch for others as new integrations land.

4. **Carried from S2865 — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.** Still two independent triggers, not yet promoted. Small doc/deliverable, ~30 min. Principle: "collector paths must converge on a single normalized schema; no view-layer spider special casing."

5. **Carried — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate). 1st trigger observed at S2864. Watch for 2nd/3rd trigger; not codified this session either.

6. **Ledger #11 — Durable non-cascading audit table for deletes** — deferred; awaits compliance/audit trigger.

7. **`simulate_enforcement` auto-clear-after-N-seconds** (S2857 first-trigger fold) — deferred; awaits explicit ask.

8. **`enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger). Not urgent until a fifth type is added.

9. **`actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, 1st trigger — MIGRATION required). Deferred until schema-migration budget opens.

10. **`EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger). Deferred — awaits second independent trigger.

11. **`list_caps include_defaults=true` remaining perf costs** (S2858 concern 5, 1st trigger). Not urgent until fleet size makes it a slow ticket.

12. **Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859 1st trigger observed).

13. **Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

14. **Fold C from S2861 close: shared JSONField projection helper**.

15. **Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

16. **openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

17. **Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

18. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. See A4 Constraints below for the full capability list after S2866.

### What's forbidden at S2867 (D6 moratorium still in force)

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2866 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`. S2857: operator can now verify enforcement without touching real spend via `simulate_enforcement`. S2858: post-clear re-flag likelihood inline on clear_* responses; list_caps read surface no longer degrades linearly with workspace count. S2859: `deliverable_tool.create` with `deliverable_type='ratification_record'` lands with verbatim title + no spurious diagnostic mark. S2860: Rigby can permanently delete deliverables directly via `deliverable_tool.delete` — two-factor gated, published-guarded, cascade-previewed, WARNING-audit-logged. S2861: Rigby can trim `autopilot_tool.history include_evidence=true` responses to specific top-level keys via `selected_fields=["evidence.<key>", "result.<key>"]`. S2862: huggingface → SignalCluster drop resolved — HF spider runs now produce extractable text; A4 AI/ML signal-cluster discovery restored (curated fallback). S2863: HuggingFaceSpider now hits the LIVE HF Hub API — 20/20 items with populated title+description, 2827 chars extractable text — A4 `intelligence_tool.signal_clusters source_spider='huggingface'` now returns live-data-backed AI/ML clusters, not curated topics. S2864: view-layer HF workaround removed after backfill enriched 460 pre-S2862 items; A4 feed queries for `source=huggingface` no longer require spider-name string-matching at read time — clean canonical shape across all HF rows (historical + new). S2865: Rigby can now raw-HTTP GET/POST arbitrary http/https URLs via `web_fetch_tool` — closes the twice-bit F-DELEGATED verification gap (S2863 Q1 + S2864 Q4). **S2866: Rigby can now inspect any of 8 allowlisted DB models directly via `orm_inspect_tool` — closes the S2845-class false-negative gap where a tool surface reports 'no data' but rows exist under a different filter path. External endpoint verify (S2865 `web_fetch_tool`) + internal DB verify (S2866 `orm_inspect_tool`) together cover the F-DELEGATED verification surface.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail — cycle-triggered vs operator-triggered attributed correctly + auto_events_count vs operator_events_count now visible per-workspace in the fleet report; (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total — now cleanly filtered to enforcer-forced downgrades only; (i) all billing paths route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls priced at effective_model rates; (j) analytics-plane cost attribution correct; display fallbacks use canonical rates with explicit `estimated: true` flag; embedding pricing SoT preserved; (k) autopilot audit history (`autopilot_tool.history include_evidence=true`) surfaces evidence + result JSONField values inline for operators inspecting trigger / actor_user_id / reason; (l) operators + demo audiences can trigger the freeze + downgrade enforcer against a synthetic spend value via `workspace_budget_tool.simulate_enforcement`; (m) operators can inspect post-clear re-flag likelihood inline on clear_freeze/clear_downgrade responses; (n) workspace_budget_tool.list_caps read surface no longer degrades linearly with workspace count; (o) governance/ratification records land clean via `deliverable_tool.create` (deliverable_type=ratification_record); (p) hard delete of a deliverable is a first-class operator action via `deliverable_tool.delete`; (q) `autopilot_tool.history include_evidence=true` supports `selected_fields=["evidence.<key>", "result.<key>"]` for top-level JSON projection; (r) HuggingFace AI/ML signals enter SignalCluster aggregation — 22 rows/7d that previously dropped to 0 signals now yield 1+ signal per run with entity_tokens matching AI/ML domain; (s) `intelligence_tool.signal_clusters source_spider='huggingface'` returns LIVE Hub API data (not curated fallback) — 20 items/run, 100% with populated title+description; (t) `/api/spider-intelligence/feed/?source=huggingface` returns canonical items with title+url+description for historical + new rows without view-layer spider-name matching — 519/519 items now populated post-backfill. (u) Rigby can raw-fetch arbitrary http/https URLs via `web_fetch_tool` (GET/POST, JSON parse, headers, params, 60s timeout cap, 2MB response cap, text-MIME-only body_text decode, loopback allowed by default via `allow_private_networks=true`). **(v) Rigby can inspect any of 8 allowlisted Django models directly via `orm_inspect_tool` (actions: list_models/describe_model/get/filter; safe lookups incl. has_key/has_keys for JSONField verification; per-model policy with high-sensitivity JSONField-default-omission; two-layer sensitive-field detection with word-boundary matching + composite substrings; recursive JSON key redaction; expensive-text-field query-cost guardrails; row cap 200, string trunc 4KB) — post-merge live-verified against SignalCluster/LLMCallLog/Deliverable with real S2845-shape has_key filter returning 65 rows.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2866 close — what shipped (one PR, one commit + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3351** `f52c1d854` — S2866 slate #1: `orm_inspect_tool` schema + handler + registration + tests (5 files, +907 lines)
- **PR `<this docs cascade>`** — S2866 handoff + 00-START-NEXT-SESSION refresh + pa_local.sh pin bump

**Workspace canonical:** Rigby Tool Gap Ledger #3 marked shipped (`shipped_in_pr_3351`). Ledger update + S2866 close summary + ratification envelope written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables`.

**Runtime impact:**
- Rigby has a bounded ORM row inspector for the first time — S2845-class false-negative gap closed.
- 117 total PA tool schemas (was 116); `_tool_handlers` count 160.
- Post-merge live dispatches proved E2E: 8 models discoverable via `list_models`, `describe_model LLMCallLog` returns clean field types with token counters correctly NOT flagged sensitive, `filter SignalCluster has_key='hackernews'` returned 65 rows with populated `source_breakdown` values, all reject paths (non-allowlist, unsafe lookup, deep chain, expensive text field) correct.

**Not shipped at S2866 close (deferred to S2867 or later):**
- Aggregate group-by counts on orm_inspect_tool (1st trigger — S2866 Q_ZOOM_OUT round 1)
- Per-model explicit `allowed_fields` (1st trigger — S2866 Q_ZOOM_OUT round 2)
- S2862 Q5.a fold promotion to spec_backlog
- SIGN-discipline Playbook amendment (1st trigger only — S2864)
- openmeteo signal fix (product decision)
- All prior deferred items from S2865/S2864/S2863/S2862/S2861/S2859/S2858/S2857/S2856

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2866)

See:
- **S2866 handoff (current):** `docs/handoffs/SESSION_2866_ORM_INSPECT_TOOL.md`
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
