# Session 2897 — `prospecting_queue` empty titles (Ledger Row A) → mitigated

**Date:** 2026-07-22
**PR:** [#3419](https://github.com/clwest/donkey-betz-platform/pull/3419) merged into main at commit `dff09b962`
**Ship shape:** Engineering-first (Option C at S2897 open — Chris ratified). Bug-fix + helper extraction + tests; live post-recycle verification green; Rigby SIGN AGREE across 4 dimensions with one Q3 revision absorbed inline.
**D6 moratorium status:** IN FORCE (no strategic discovery arcs opened this session).

## What shipped

**PR #3419 — S2897 `prospecting_queue` Row A fix.** Two stacked bugs in `core/services/ops_autopilot/revenue.py::OutboundLeadEngine`:

| Bug | Location | Symptom | Root cause |
|---|---|---|---|
| B1 | line 478 title extraction | title always empty when `embedding_text` empty | Python operator-precedence: `a or b if c else ''` parses as `(a or b) if c else ''` |
| B2 | lines 478 + 505-508 (title + scoring text) | financial-spider rows always score flat 45 with empty titles | Wrong-path `raw.get('title', '')` — financial spiders wrap batches under `raw_data = {items: [{title, ...}, ...]}` with no top-level `title` |

Bundled fix (same root: title source resolution): new helper `OutboundLeadEngine._extract_first_item_text(raw, item)` returns `(title, combined_text, title_source)` with fall-through:

1. `top_level` — `raw['title']` if present
2. `items_first` — `raw['items'][0]['title']` for batched-item spiders
3. `embedding` — `item.embedding_text[:80]` fallback
4. `synth` — `{spider}: {data_type} batch (N items)` last-resort label

Used by `evaluate()` for title extraction (with `(+N more)` suffix on batched rows) and by `_score_lead()` for scoring text. Returned rows now include a `title_source` field so operators can see title provenance.

## Session shape (three-part plain-English)

1. **What was done.** Chris ratified Option C (Ledger-row-fix engineering session) over Options A/B at S2897 open. Investigated Row A via Rigby ORM probe → confirmed data-shape mismatch (raw['items'][*] pattern universal across all 6 financial spiders); designed bundled fix (both bugs share the same root); Rigby SIGN AGREE with one absorbed revision; shipped PR + live-verified + post-merge recycled.
2. **Why it matters.** `autopilot_tool.prospecting_queue` was returning 6 leads with empty titles and flat score 45 — blocking operator triage of the outbound-lead engine's output. Operators (Chris, Rigby, downstream LLMs) can now see real lead identity + batch signal + varied scoring. Before this ship: `title: ""`, `score: 45` × 6. After: `title: "Deadline Alert: Calix (CALX) Shareholders ... (+14 more)"`, `score: 55/51/45/45/45`.
3. **What's next.** Row A → mitigated (Ledger entry #26). New deferred Ledger row (entry #27): structural "batched spider rows collapse N leads into one autopilot Opportunity row" — trigger for arc = operator/customer signal ambiguity in triaging batched leads. Row B (`integrity_null_spike_scan` false-positive noise) remains open engineering candidate. Row 161 substrate-arc gate STILL not decided (deferred at S2896 open, deferred at S2897 open in favor of Row A engineering).

## Rigby SIGN cycle summary

**Pre-ship SIGN (design routing, 0 tool_runs — pure design review):** Rigby verified via prior ORM probe (extended probe run at Claude's request after Rigby caught that first probe didn't inspect `raw['items']`). Verdicts:
- **Q1 (scope: bundle vs narrow):** AGREE — bundle both bugs, same root, narrow fix would leave scoring broken.
- **Q2 (batched-items model):** AGREE — log as Ledger candidate / future arc, out-of-scope for Row A.
- **Q3 (title format):** DISAGREE with generic `{spider}: {data_type}` fallback → preferred `{first_title} (+{N-1} more)` when first_title exists. **Absorbed inline** — evaluate() now applies suffix in `items_first` branch; synth only fires when title truly empty.
- **Q4 zoom-out (coupling/risk):** AGREE with mitigations — small unit tests + `title_source` field for future debug. **Both mitigations absorbed.**

**Verification tool_runs (post-recycle live dispatch):** 1 tool_run — `autopilot_tool.prospecting_queue` default. All 6 leads carry non-empty titles + `title_source: items_first` + `(+N more)` suffix where N>1 (+14, +24, +13, +4 for polygon/sec_edgar/financial/finnhub); etherscan single-item row correctly has no suffix.

## Rigby Tool Gap Ledger status (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`)

- **Row A (`prospecting_queue` empty titles)** — **`MITIGATED` at PR #3419 (S2897)** — Ledger entry #26 under Mitigated.
- **Row B (`integrity_null_spike_scan` false-positive noise)** — open. S2895 candidate. Unchanged.
- **Row C (`autopilot_tool.history` selected_fields silent longer-list wipe)** — `mitigated` at PR #3417 (S2896). Unchanged.
- **NEW Row (entry #27, deferred):** "Batched spider rows collapse N leads into one autopilot Opportunity row" — structural. Fix options: (a) explode `raw['items']` into per-item leads at query time in `OutboundLeadEngine.evaluate()`, or (b) change spider intake to write per-item rows. Trigger for arc: operator/customer signal ambiguity in triaging batched leads.

## Zoom-out folds this session

None new. Rigby's Q4 zoom-out ask surfaced a mild coupling risk (schema drift across spiders — some may use `headline`/`name` or nest deeper) but the helper's `isinstance` defensive checks handle it; no fold row required. Same-PR mitigations (tests + `title_source`) absorbed.

## Files touched

- `core/services/ops_autopilot/revenue.py` — +64/-7 lines. Added `_extract_first_item_text` helper on `OutboundLeadEngine` (~45 lines); rewrote `evaluate()` title-extraction block (lines 477-501) to use helper + apply `(+N more)` suffix + synth fallback + add `title_source` to returned lead dict; rewrote `_score_lead()` text extraction (lines 549-553) to use helper's `combined_text`.
- `core/tests/test_s2897_prospecting_queue_titles.py` — new file, 170 lines, 10 tests covering all 4 extraction paths + defensive branches + score integration + evaluate() shape branches. All passing.

## Live verification (post-recycle)

`autopilot_tool.prospecting_queue` default dispatch after `make celery-recycle`:

```json
{
  "queue_size": 6,
  "leads": [
    {"title": "Deadline Alert: Calix, Inc. (CALX) Shareholders Who Lost Money Urged To Contact Glancy Pr (+14 more)", "title_source": "items_first", "source": "polygon_finance", "score": 55, ...},
    {"title": "8-K - Scilex Holding Co (0001820190) (Filer) (+24 more)", "title_source": "items_first", "source": "sec_edgar", "score": 51, ...},
    {"title": "Swatch Gets a Sales Bounce With a Margin Bruise (+13 more)", "title_source": "items_first", "source": "financial", "score": 45, ...},
    {"title": "Amazon cuts some jobs in its artificial general intelligence unit (+4 more)", "title_source": "items_first", "source": "finnhub", "score": 45, ...},
    {"title": "Latest ETH Block: 25,589,917", "title_source": "items_first", "source": "etherscan", "score": 45, ...},
    ...
  ]
}
```

Post-merge recycle done per PLAYBOOK-7.4.4.

## Row 161 substrate-arc gate — status

**Not decided this session.** Chris picked Option C again at S2897 open (parallel to S2896 open). Row 161 substrate-arc gate remains open for S2898. Two consecutive Option-C picks may signal preference; watch at S2898 open whether Chris signals appetite for continued Ledger-row work (Row B) versus opening the substrate arc.

## Sweep progress tracker (Path B ratified S2892)

**Slice 1 — `td_handlers_ops` (17 registered tools):**
- Batches 1-4 (S2892-S2895): 9 tools ✓
- **S2896:** engineering ship (Row C mitigated).
- **S2897 (this session):** engineering ship (Row A mitigated).
- **Remainder:** Slice 1.5b (`autopilot_tool` mutations, ~1 session) + 4 doc/unknown/partial ops tools (~1-2 sessions).

**Gap-map:** unchanged from S2896 (no sweep batch this session).

## What's next — S2898 open sequence

Per Chris's engineering-bias-over-audit rule + Row A close + Row 161 gate still open:

1. **FIRST DECISION POINT — Row 161 substrate-arc gate.** Same three options unchanged. Two consecutive Option-C picks (S2896 + S2897) — Chris may want to re-frame or stick with pattern.
2. **If continue Ledger-row engineering:** Row B (`integrity_null_spike_scan` false-positive noise) is the last remaining open Ledger row from S2895. Highest-signal candidates: allowlist/applicability-rule for expected-null (spider, field) pairs to filter 96 critical spikes at `null_rate=1.0` for `processed_data` + `embedding_text` fields across ~20 spider families.
3. **If continue sweeps:** Slice 1.5b (`autopilot_tool` mutations sweep — 29 actions, needs staged-enforcement session with paired lifecycle scaffolding).
4. **Deferred (D6 moratorium still in force):** No strategic discovery arcs. No R1a-shaped proposals. Docs restructuring arc, W2 #1/#2b/#2c, LLMCallLog field splits, bulk workspace_budget operations, C4/C5/C6 character-os follow-ons all remain queued.

## For fuller sweep context

- **S2896 handoff (prior):** `docs/handoffs/SESSION_2896_AUTOPILOT_HISTORY_WIPE_DIAGNOSTIC.md`
- **S2895 handoff (Row A/B/C surfaced):** `docs/handoffs/SESSION_2895_PA_TOOLS_SWEEP_SLICE_1_5A_AUTOPILOT_READ_ONLY.md`
- **Autopilot tool validation:** `docs/research/tools/validation/autopilot_tool_validation.md`
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
