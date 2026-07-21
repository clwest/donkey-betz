# Session 2870 — signal_clusters injection hardening + spider_data_bridge list-form raw_data guard

**Date:** 2026-07-21
**Prior session:** S2869 (spider_status_tool.search preview fallback + intelligence_tool.signal_clusters multi-source filter)
**Next session:** S2871
**Slate:** Rigby Tool Gap Ledger #20 + #21, grouped (both surfaced mid-S2869; both harden PA tool-surface reliability). Shipped as single PR.

**Merge commit (main):**
- `8abb12f0f` PR #3361 — S2870 slate (3 files, +229/-8)

**D6 moratorium status:** still in force — pure engineering execution against the Rigby Tool Gap Ledger, zero strategic discovery.

---

## What shipped

### PR #3361 — S2870 slate (Ledger #20 + #21, grouped)

Both entries surfaced mid-S2869 discovery — grouped because both harden PA tool-surface reliability without changing observable behavior for correct callers.

#### #20 — `intelligence_tool.signal_clusters` filter injection hardening

**Root cause (Rigby pre-code SIGN round 1 Q1 live evidence):** GPT-5.2 auto-injects three filter values when the operator omits them:

- `pattern_type='demand_spike'`
- `min_confidence=0.6`
- `window_hours=168`

Result: `intelligence_tool.signal_clusters source_spider='hackernews'` (no other filters) returns `count=0` because the three injected defaults over-filter the SignalCluster query to zero. This is a reasoning-model behavior — the model interprets typed enum + typed number descriptions as suggestions to fill "helpful" defaults on tool call.

**Fix (schema-only; handler unchanged):**

`core/services/pa_tool_schemas.py:3995-3997`:
- `pattern_type`: bare `{type: 'string', enum: [...]}` → `anyOf: [{type: 'string', enum: [...]}, {type: 'null'}]`. Mirrors S2869 `source_spider` shape.
- `pattern_type` / `min_confidence` / `window_hours` descriptions all updated: "OPTIONAL. Omit entirely when operator did NOT explicitly request... Do not default-fill (e.g. 'demand_spike' / 0.6 / 168) — that over-filters to zero. Pass 0 or omit for no filter."

Handler at `core/services/td_handlers_core.py:3476-3524` unchanged — was already correct:
- `if pattern_type:` line 3477 — None/empty is no-op
- `if min_conf is not None:` line 3481 — None is no-op; 0.0 → `filter(confidence__gte=0.0)` matches all rows (effective no-op)
- `if window_hours:` line 3519 — 0/None is no-op

**Post-code Rigby SIGN round 3 Q1 live evidence:**
- Same call `source_spider='hackernews'` (post-recycle) → **count=30** (contrast: pre-code **count=0**)
- `filters_applied.pattern_type=null` — the schema anyOf-null shape landed; GPT-5.2 no longer snaps to `demand_spike`
- Explicit `pattern_type='demand_spike'` still filters correctly → count=12 (regression protected)

Note: Rigby's tool dispatcher shim currently always emits numeric values on `window_hours` + `min_confidence`, so those two params still get non-null defaults on her calls. But since the handler treats them as no-op at 0/0.0, no over-filtering. Description hardening is a nudge for future evolution; escalation to `"default": null` or middleware strip is deferred until we observe fresh injection incidents.

#### #21 — `spider_data_bridge.py` list-form `raw_data` guard (Option 21A)

**Root cause:** `LegacySpiderData.raw_data` is a `JSONField` — usually dict-shaped but can be list-shaped (S2869 test fixture 6 surfaced this). 5 callsites in `core/learning_bridges/spider_data_bridge.py` do:

```python
raw_data = spider_data.raw_data or {}
items = raw_data.get('items', [])  # AttributeError if raw_data is list
```

**Fix (file-local per S2869 Fold 1 "inline preview, not shared helper"):**

New helper at top of file:
```python
def _safe_dict(raw_data: Any) -> Dict:
    """Return raw_data if it's a dict, else {}."""
    return raw_data if isinstance(raw_data, dict) else {}
```

5 callsites migrated (line numbers post-helper-block insertion):
- Line 99 — `_extract_patterns` (was line 92)
- Line 190 — `_create_agent_learning_entry` (was line 183)
- Line 287 — `_calculate_completeness` (was line 280)
- Line 365 — inline scoring block (was line 358)
- Line 383 — `evaluate_actionability` staticmethod (was line 376)

**Cross-file sweep deferred** to Ledger #22 (13 remaining sites across 8 files — see below). File-local helper matches S2869 Fold 1 philosophy: promote to shared util only when second file needs the same guard.

---

## Discovery arc — 3 SIGN cycles

### Pre-code SIGN round 1 (grounded via 3 live signal_clusters dispatches)

- Q1 (LIVE): 3 dispatches confirmed root cause — omit filters + `source_spider='hackernews'` → count=0 with `pattern_type='demand_spike'` + `min_confidence=0.6` + `window_hours=168` injected; overrides to unrestrictive → count=5
- Q4 blocked: `LegacySpiderData` not in `orm_inspect_tool`'s 8-model allowlist → couldn't quantify list-vs-dict prevalence from Rigby's side (ledger candidate #23)
- Q5 blocked: `repo_tool` 10s timeout too short for repo-wide greps (ledger candidate #24)

### Round 2 (revised proposal after Q1 evidence + Claude self-served Q5)

Claude ran the repo-wide grep directly (Rigby's blocker) and found the #21 pattern is **not one-off**: ~14 crash sites across 8 files. Revised proposals:

- **#20:** schema `anyOf: [enum, null]` on `pattern_type` (mirrors S2869 shape) + description hardening on all three filter params. Description-only alone is insufficient (Q1 evidence).
- **#21:** Option 21A (5 sites in spider_data_bridge.py + file-local helper) ships now; Option 21B (all 14 sites) logged as ledger #22.
- **Zoom-out ask Q6:** middleware `log_injected_params` (compare model payload vs operator utterance) as future spec candidate — not a Playbook amendment yet.

Rigby F-AGREE on both. Ledger #22/#23/#24 logged.

### Post-code SIGN round 3 (live verification of shipped code)

- Q1 (LIVE): post-code dispatch confirmed `pattern_type=null` preserved + count=30 (vs pre-code count=0)
- Q2 (LIVE): explicit `pattern_type='demand_spike'` still filters correctly (regression protected)
- Q3: schema change confirmed active on live stack
- Q4 (zoom-out): mild pushback on Playbook amendment — recommends pattern-recommendation checklist rather than blanket "anyOf-null on any optional param" rule; conditions for adoption: (1) enum/typed numeric defaults observed injected in the wild, (2) "no filter" is a valid common intent

Rigby F-AGREE. Ledger updated (#20 + #21 → shipped_in_pr_S2870; #22/#23/#24 confirmed open).

---

## Working loop observations at S2870

- `feedback_verify_rigby_tool_runs_before_trusting_sign` — Rigby grounded Q1 in **all three** SIGN cycles with live signal_clusters dispatches; no rubber-stamping observed. Every SIGN F-AGREE backed by tool_runs evidence.
- `feedback_verify_at_raw_orm_before_trusting_tool_no_data` — hit twice this session:
  - Rigby's tool-surface limitations (LegacySpiderData not in orm_inspect allowlist; repo_tool timeout) blocked Q4/Q5 verification → Claude self-served via file-system Grep. Both blocked verifications became ledger candidates #23 + #24.
- `feedback_zoom_out_ask_per_rigby_sign` yielded 3 usable fold candidates:
  1. #20 fix scope: schema-only insufficient → escalate to anyOf-null shape (round 2 fold)
  2. #21 fix scope: 14 sites detected → Option 21A + ledger #22 (round 2 fold)
  3. Q6 zoom-out: middleware log-only-then-strip pattern as future spec candidate; **not** Playbook amendment yet
- `feedback_claude_stdout_truncation_vs_ui_truncation` hit twice — recovered via `sed '/--- Tool Runs (verbose) ---/,$d'` filter.
- `feedback_rigby_writes_workspace_deliverables` — Rigby updated Ledger deliverable herself (added #22/#23/#24 entries; marked #20/#21 shipped_in_pr_S2870). Claude did not ORM-direct-write.
- **New at S2870:** Rigby's tool dispatcher shim (her PA test path) still emits numeric defaults on `window_hours` + `min_confidence` even when set to null-ish. Handler tolerance (0.0 gte matches all; 0 window_hours is falsy) masks the issue for correct callers but the injection pattern is real. Deferred to future observation-driven middleware work.

**No candidate lessons for Playbook amendment this session** (Q6 zoom-out landed on pattern-checklist framing, not blanket rule).

---

## Rigby Tool Gap Ledger updates (via Rigby PA)

Deliverable ID `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`

- **#20** → shipped_in_pr_S2870
- **#21** → shipped_in_pr_S2870
- **NEW #22** — raw_data isinstance guard needed at ~13 remaining sites across 8 files (grep evidence: `intelligence/consumers.py:459,476`, `core/tasks_financial.py:750,971,1230,1339`, `ai_core/intelligence/income_builder.py:1328`, `ai_core/intelligence/consumers.py:1873`, `intelligence/opportunity_storage.py:49`, `intelligence/income_spider_orchestrator.py:303,304,348`, `core/views_stock_intelligence.py:119,143,512,726`, `core/views_spider_feed.py:40,464`, `core/tasks.py:5166,5238,5410,5457,5516`, `core/services/proactive_intelligence.py:315,346,378,412`, `core/tasks_content.py:1989`, `core/models_unified_system.py:3806`, `core/signals/trigger_signals.py:107`) — open, medium priority
- **NEW #23** — LegacySpiderData missing from `orm_inspect_tool`'s 8-model allowlist (blocked Rigby's Q4 verification of list-form prevalence) — open, medium priority
- **NEW #24** — `repo_tool` 10s timeout blocks repo-wide greps (blocked Rigby's Q5 verification of #21 crash site count) — open, low priority

---

## Session pin lifecycle

Pin `pa-2459cc90df584f5f` (labeled `s2870-slate-injection-hardening-and-raw-data-guard`) retires at S2870 close.

Fresh mint required at S2871 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## Not shipped at S2870 (deferred to S2871 or later)

- **Ledger #22** — raw_data isinstance guard at 13 remaining sites (Option 21B). ~40 lines mechanical sweep with regression test. Waiting on "second file needs the same guard" trigger per S2869 Fold 1 discipline.
- **Ledger #23** — extend `orm_inspect_tool` allowlist to include LegacySpiderData + other frequently-verified models (candidates from S2869/S2870 SIGN cycles).
- **Ledger #24** — raise `repo_tool` timeout or add repo-wide grep alternative.
- **Ledger #5** — schema/handler drift CI enforcement wiring (still open from S2869 handoff).
- **Ledger #16** — close-ceremony twin-mirror enforcement gap (still open).
- All prior S2867/S2866/S2862/S2861/etc carried items — unchanged.

---

## Substrate verification

- Local tests: 18/18 pass on `core.tests.test_s2870_injection_hardening_and_raw_data_guard`; 14/14 pass on `core.tests.test_s2869_search_preview_and_multisource` (regression)
- `check_pa_tool_drift` — no new drift on `intelligence_tool` (pre-existing drift on shared fields unchanged: `handler reads (schema missing): ['status']` / `schema declares (handler ignores): ['bill_number', 'description', 'odds', 'stake', 'ticker', 'wager_type']`)
- `make celery-recycle` — twice: pre-Rigby-SIGN + post-merge (per PLAYBOOK-7.4.4)
- Live Rigby dispatch verified — pre-code count=0 → post-code count=30 with `pattern_type=null` in `filters_applied`

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2870)

See `00-START-NEXT-SESSION.md` § "For fuller A1 W1 + W2 arc context" for the full handoff chain S2846 → S2870.
