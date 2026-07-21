# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2859 CLOSE → `deliverable_tool.create` Ledger #8 + #9 SHIPPED (2026-07-20; picks up as S2860) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-20 (S2859 close).** Chris-selected Ledger entries #8 + #9 (`deliverable_tool.create` gotchas) shipped as **one bundled PR with two commits** (Rigby SIGN Q3 concurred on bundle; Q4 mod folded via split-commit for blame localization):

- **PR #3337** `f0757eabd` — S2859 slate #1: `deliverable_tool.create` substrate fix
  - Commit `14ac6e23c` — fixture-drift fix in `test_deliverable_initiative_diagnostics.py` (owner_id NOT NULL + S1199 PR-D provenance contract). No production code changes; unblocks the A/B/C regression classes locally.
  - Commit `b8b1cd518` — S2859 behavior change:
    - **Ledger #8:** opt-in `preserve_title: bool = False` on `create_deliverable()`; wired from PA tool-surface create path so identifier-like titles (e.g. `RATIFICATION_20260720_...`) land verbatim (no auto-`Rigby:` prefix, no 120-char cap). Aligned latent `kwargs['title'] = title[:500]` truncation to actual `Deliverable.title.max_length = 255` (Rigby post-code Q5.1 fold).
    - **Ledger #9:** `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT = frozenset({'ratification_record'})` skips `missing_initiative_id` diagnostic for governance types. Narrowly scoped — bypasses ONLY the no-initiative-id branch; `workspace_mismatch` integrity check preserved. Same gate applied at update-path re-eval.
    - 12 new pytest cases (6 PreserveTitleTests + 6 RatificationTypeExemptTests).

**Working loop validated at S2859:**
- 1 pre-code SIGN cycle covering both fixes (5 grounded `repo_tool.read_file` calls, AGREE-with-mods on all 5 Qs, 4 mods folded + Q5 zoom-out surfaced 3 concerns — 2 folded same-PR, 1 recorded as future-trigger)
- 1 post-code SIGN cycle (7 grounded reads, AGREE-TO-SHIP on Q1/Q2/Q3, AGREE-WITH-MODS on Q4 → split-commit, Q5.1 title-length mismatch folded same-PR, Q5.2 governance obligation recorded)
- 23 total tests green (12 new + 11 pre-existing that were blocked by fixture drift, now unblocked)
- Post-recycle Rigby E2E confirmed both fixes wired end-to-end on Donkey Betz workspace — title verbatim + no diagnostic mark on ratification_record row

**Session pin `pa-c82f75411b3d45f0` RETIRES at S2859 close.** Fresh mint required at S2860 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2860 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-c82f75411b3d45f0` retired at S2859 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2860-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2860

Per `feedback_engineering_bias_over_audit`, list net-new first.

0. **New Ledger candidates surfaced at S2859 (Chris to pick 1–2 for slate #1):**
   - **`deliverable_tool.delete` action missing** — surfaced during S2859 post-merge E2E. Rigby had to fall back to `content_tool.content_reject` (soft-archive) to clean up a smoke row. For genuine hard-delete cleanup, need a first-class `delete` action. Small (~1-2 hours), self-contained. Adds to Rigby Tool Gap Ledger.
   - **Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"** — deeper substrate driver behind repeated exemption pressure. Requires UI/product decision (filterable diagnostic view? severity levels?). Watch for a 3rd/4th independent trigger before proposing a same-PR fix; NOT ready for slate — record only.

1. **`simulate_enforcement` auto-clear-after-N-seconds** (S2857 first-trigger fold) — currently `dry_run=false` writes flags that persist until operator calls `clear_freeze`/`clear_downgrade`. Consider optional `auto_clear_after_seconds` param so a demo doesn't leave a workspace frozen if the operator forgets to clean up. Deferred — awaits explicit ask.

2. **`selected_fields` param for `autopilot_tool.history include_evidence`** (S2856 slate #3 Rigby Q5c zoom-out fold, first trigger observed — deferred until second trigger before Playbook amendment) — structured field selection over the JSONField payload. Blocked until concrete need surfaces.

3. **`enforcement_action_types` shared constant** (S2856 pre-code Q5b, first trigger observed) — de-duplicate the 4-item action-type list between `td_handlers_ops.py:4362` and `ops_autopilot/budget.py` write sites. ~1 hr refactor. Not urgent until a fifth type is added.

4. **`actor_user_id` as first-class column on `AutopilotAction`** (S2856 pre-code Q5a, first trigger — MIGRATION required). Deferred until schema-migration budget opens.

5. **`EnforcementContext` dataclass consolidation** (S2857 post-code Q5, first trigger observed) — `actor_user_id` + `trigger` + `simulated` (and growing) currently piped as kwargs on both enforce_ methods. Consolidate into an `EnforcementContext` dataclass. **Deferred** — awaits second independent trigger before Playbook amendment.

6. **`list_caps include_defaults=true` remaining perf costs** (S2858 Q5 concern 5, first trigger observed — deferred) — spend computation + is_frozen/is_downgraded lookups still per-row after PR #3334 batched the name lookup. Not urgent until fleet size makes it a slow ticket. Would extend the two-pass pattern from PR#2 to also batch SystemConfiguration reads.

7. **Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859 first-trigger observed — needs 2nd/3rd independent trigger before adding types like `governance_charter`, `session_handoff`). Governed change per constant docstring; Playbook §14.2 threshold applies.

8. **Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855: `model_kind` dimension, `EMBEDDING_COSTS`+`MODEL_PRICES` unification, `pricing_catalog_version` field on LLMCallLog, LLMCallLog↔CostTracking schema-level provenance column. None currently justified without a specific reconciliation trigger.

9. **A4 warm-up under ratified constraints** — S2846 6-line block still in force. See A4 Constraints below for the full capability list after S2859.

### What's forbidden at S2860 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Multi-source `source_spider` filter (Ledger candidate; ~1 hour)
- SignalCluster naming rewrite (Ledger candidate; ~1 day)
- `huggingface` returns 0 SignalCluster rows (Ledger candidate; ~half day)
- `spider_status_tool.search` empty preview field (Ledger candidate; ~2 hours)
- `spider_status_tool.list` pagination (Ledger candidate; ~2 hours)
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2859 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. Every workspace including A4 has $5/day default; operator can raise/lower via `set_cap` (fires immediate enforcement per S2850 #3.0a) or change the default via `set_default_cap` + `backfill_defaults`. S2857: operator can now verify enforcement without touching real spend via `simulate_enforcement`. S2858: post-clear re-flag likelihood inline on clear_* responses; list_caps read surface no longer degrades linearly with workspace count. **S2859: `deliverable_tool.create` with `deliverable_type='ratification_record'` lands with verbatim title + no spurious diagnostic mark — governance close-cascade no longer requires manual ORM cleanup.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** A4 outreach can now accurately claim: (a) per-workspace daily caps at operator-configurable default with backfill; (b) auto-enforcement at 70% soft / 100% hard tiers with hysteresis; (c) full audit trail — cycle-triggered vs operator-triggered attributed correctly + auto_events_count vs operator_events_count now visible per-workspace in the fleet report; (d) immediate enforcement on cap change (no ~10-min wait); (e) policy-triggered model downgrade routes to gpt-5-mini and is truthfully tracked in cost logs; (f) fleet auditability via `workspace_budget_tool.enforcement_report`; (g) read surfaces auth-scoped; (h) downgrade savings estimate visible per-workspace + fleet-total — now cleanly filtered to enforcer-forced downgrades only; (i) all billing paths route through a single canonical pricing catalog with Decimal-typed rates + cached-input support; Claude Haiku billing bug fixed; policy-downgraded calls priced at effective_model rates; (j) analytics-plane cost attribution correct; display fallbacks use canonical rates with explicit `estimated: true` flag; embedding pricing SoT preserved; (k) autopilot audit history (`autopilot_tool.history include_evidence=true`) surfaces evidence + result JSONField values inline for operators inspecting trigger / actor_user_id / reason; (l) operators + demo audiences can trigger the freeze + downgrade enforcer against a synthetic spend value via `workspace_budget_tool.simulate_enforcement` — dry-run reveals decisions + thresholds without state writes; live path writes real flags with `evidence.simulated=True` marker (excluded from fleet report by default); (m) operators can now inspect post-clear re-flag likelihood inline on clear_freeze/clear_downgrade responses (no follow-up get_status call needed); status_context block encodes enforcer semantics with re_flag_likely tied to EXPLICIT cap only + explicit reason string; (n) workspace_budget_tool.list_caps read surface no longer degrades linearly with workspace count — batched name lookup via single filter().values_list() query regardless of row count; **(o) governance/ratification records land clean via `deliverable_tool.create` (deliverable_type=ratification_record) — no auto-title-prefix, no spurious missing_initiative_id diagnostic hiding the row from the workspace UI, no manual Django-shell cleanup required.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2859 close — what shipped (one PR, two commits + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3337** `f0757eabd` — S2859 slate #1: Ledger #8 + #9 substrate fix
  - Commit `14ac6e23c` — fixture drift fix (unblocks A/B/C regression classes)
  - Commit `b8b1cd518` — `preserve_title` opt-in + `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT` frozenset + 12 new tests
- **PR `<this docs cascade>`** — S2859 handoff + 00-START-NEXT-SESSION refresh + docs cascade

**Workspace canonical:** Content mirror + ratification envelope written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables` at S2859 close-cascade. Ledger entries #8 + #9 marked complete + 2 new candidates added (`deliverable_tool.delete` gap + Q5.3 diagnostic-invisibility future-trigger).

**Runtime impact:**
- Every `deliverable_tool.create` call with `deliverable_type='ratification_record'` + explicit title now lands correctly first time — no post-create ORM cleanup step needed at ratification close-cascades.
- Non-PA agent flows unaffected — `preserve_title=False` (default) still runs `_clean_deliverable_title` for raw-prompt-as-title cleanup.
- Workspace_mismatch integrity check preserved for exempt types (a ratification with a real initiative_id + wrong workspace still marks diagnostic).
- Pre-existing latent bug fixed: `kwargs['title']` truncation now matches actual `Deliverable.title.max_length=255` (was diverging at [:500]).

**Not shipped at S2859 close (deferred to S2860 or later):**
- `deliverable_tool.delete` action (new Ledger candidate; ~1-2 hours; surfaced at S2859 post-merge E2E)
- Q5.3 fold — "diagnostic == effectively hidden" substrate work (needs 3rd/4th trigger; NOT ready for slate)
- Second-trigger expansion of `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT` (needs another governance type to hit; Playbook §14.2 threshold)
- All prior deferred items from S2858/S2857/S2856

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2859)

See:
- **S2859 handoff (current):** `docs/handoffs/SESSION_2859_DELIVERABLE_TOOL_GOTCHAS_LEDGER_8_9_SHIPPED.md`
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
