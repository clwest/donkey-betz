# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2845 CLOSE → S2844 MISDIAGNOSIS CORRECTED + SIGNALCLUSTER SOURCE-FILTER FIX SHIPPED (2026-07-20; picks up as S2846) — **S2846 OPENS ON A4↔A1 SEQUENCING (deferred from S2845 open) · D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-20 (S2845 close).** S2845 opened on the deferred A4↔A1 sequencing decision (§12.4 of S2841 Pressure-Test Addendum). Claude preliminary lean: sequential A1-first + light-touch A4 pipeline warm-up. Routed to Rigby for joint SIGN with tool-grounded substrate verification. Rigby verdict: AGREE with sequential A1-first, refined to "A4 pipeline warm-up (prospect list + intro emails) in parallel BUT NOT full engagement packaging until A1 Week 1 substrate ships." Substrate verification confirmed `LLMCallLog.workspace` FK is NOT present, per-workspace cost cap is global not workspace-scoped, Ledger export not shipped — all consistent with the ~1–5 day Week 1 estimate holding.

**Mid-session pivot.** Chris interrupted before ratifying sequencing to reopen the S2844 SignalCluster finding: "did we conclude 'no data' correctly, or were we looking in the wrong spot?" Four-layer investigation dispatched (spider ingest / raw items / aggregation pipeline / SignalCluster surface). **Rigby's tool surface (`spider_status_tool`) reads the LEGACY plane (`LegacySpiderData` 15k rows) and returns empty `preview` fields.** ORM-direct probe found:
- Real content IS in `LegacySpiderData.raw_data['items'][*].title` — samples included "Claude Code uses Bun in Rust", "GPT-5.6 30-year proof", "Anthropic Mythos", "Chinese Deepseek"
- 140 of 619 SignalCluster rows in 30d (22.6%) have AI-adjacent sources in `source_breakdown` — including "Anthropic, Mythos demand spike" mixing hackernews + wired + theverge + techcrunch + government
- **S2844 conclusion was WRONG.** Data exists, is being clustered, and is reachable via `source_breakdown__has_key` filter

**Root cause of the S2844 miss:** `intelligence_tool` schema restricted the shared `source` param to enum `["kb", "spider", "web"]` (for the search action). The `signal_clusters` handler at `td_handlers_core.py:3487` already supported filtering `source_breakdown__has_key=<spider_name>`, but GPT-5.2 could never call it with a spider name because the schema wouldn't accept one. Description at line 3414 said "source (spider name)" but the enum contradicted it.

**Fix shipped in-session (~15 lines, 2 files, ~1 hour):**
- `core/services/pa_tool_schemas.py` — added dedicated `source_spider` param (no enum) to intelligence_tool schema; updated `signal_clusters` description
- `core/services/td_handlers_core.py:3487` — reads `source_spider` first; falls back to `source` for backward-compat (still guards against enum values `kb`/`spider`/`web`)

**E2E verified live** via post-recycle PA dispatch: `intelligence_tool` `signal_clusters` with `source_spider='hackernews'` returned 8 clusters (matches ORM ~10), sample cluster "Anthropic, Mythos demand spike" with mixed AI-adjacent + broader sources. `filters_applied.source_spider='hackernews'` echoed correctly.

**New memory recorded** — `feedback_verify_at_raw_orm_before_trusting_tool_no_data`: When a PA tool-surface probe returns thin/empty results, verify at raw ORM layer before concluding data doesn't exist. Extends `feedback_verify_rigby_tool_runs_before_trusting_sign`. S2844 close would have queued a 5-day AI-source-pipeline build on a phantom problem; ORM probe caught it at S2845 with a 15-line fix.

**Session pin `pa-e0053042f1ad40ca` RETIRED at S2845 close** (seventy-fifth consecutive per S2770+ pattern). Fresh mint required at S2846 open.

---

## S2846 open sequence

**S2846 opens on A4↔A1 sequencing decision (deferred from S2845).** D6 discovery moratorium still in force.

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

`pa-e0053042f1ad40ca` retired at S2845 close. Run atomic close BEFORE any PA dispatch:

```bash
python manage.py session_lifecycle close --label s2846-<first-action-context>
# e.g. s2846-a1-ledger-week1, s2846-a4-prospect-list
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Ratify sequencing decision + kick off Week 1 substrate

**Pending ratification from S2845:** Claude+Rigby joint recommendation is **sequential A1-first with A4 pipeline warm-up (prospect list + 3–5 intro emails) in parallel; full A4 engagement packaging waits until A1 Week 1 substrate is demonstrably in place.**

Substrate verification findings (from S2845 Rigby SIGN §2, tool-grounded):
- `LLMCallLog.workspace` FK: NOT present in `core/models_llm_routing.py:297`; no partial migration
- Per-workspace cost cap: GLOBAL cap machinery exists (`core/services/ops_autopilot/budget.py:238–506` three-tier controller), no `workspace_daily_cap` / `workspace_budget` symbols; Week 1 must extend not just wire
- Ledger export: NOT shipped (planned for Week 2–3)
- Duration reality check: `docs/COST_SURVIVAL_AUDIT.md` §A effort table quotes ~1 working day for FK + ExternalAPICallLog telemetry — real Week 1 could collapse to ~2–3 days if scoped tight (FK + workspace-aware cost cap only; defer Ledger export to Week 2)

**S2846 first action once ratified:** open A1 Ledger Bet Week 1 with `LLMCallLog.workspace` FK migration + per-workspace cost cap extension (following IOS Existing Implementation Analysis discipline per `feedback_cycle_1a_verify_before_build`).

### Step 3 — Concurrent A4 pipeline warm-up (light-touch)

- Prospect list construction (5–15 named mid-size AI startups / enterprise AI ops teams)
- **Now unblocked by S2845 fix:** `intelligence_tool` `signal_clusters` with `source_spider='hackernews'` / `'devto'` / `'techcrunch_startups'` / `'producthunt'` / `'huggingface'` / `'mit_tech_review'` / `'arstechnica'` returns AI-tooling market signals as discovery substrate
- Combine with `kb_tool` research on named companies + Chris-known network
- Draft 3–5 cold intro emails framed as "we're shipping the audit substrate this week; want to be a design partner?"

### Net-new engineering candidates queued (deferred, not blocking A1/A4)

Per `feedback_engineering_bias_over_audit`, list net-new candidates first at every session open.

1. **SignalCluster naming rewrite** — current cluster names use top-2 frequent tokens ("Comments, Score emerging trend"), producing semantically opaque labels even when underlying signals are strong (e.g. "Anthropic, Mythos" naming works — "Comments, Score" naming doesn't). `signal_aggregation_service.py:312` already extracts `_extract_entity_tokens`; naming should prefer entity tokens over raw frequency. ~1 day. Would materially improve `intelligence_tool` `signal_clusters` discovery UX.

2. **Multi-source `source_spider` filter** — S2845 shipped single-source filter (`source_breakdown__has_key`). Multi-source (`has_any_keys`) would let one call return "all AI-adjacent clusters" in one shot instead of Rigby looping 14x. ~1 hour. Ship when A4 prospect research needs it.

3. **`huggingface` returns 0 SignalCluster rows despite 24 spider runs/7d** — aggregation pipeline drops it somewhere (likely `is_processed=False` + `embedding_text=''` combo per `_fetch_recent_spider_data` at line 262). Investigate + fix if we want the huggingface signal (which is high-value for AI-tooling discovery). ~half day. Wait until A4 prospect research needs it to prioritize.

4. **`spider_status_tool.search` returns empty `preview` field** — the tool at core reads `LegacySpiderData` but doesn't surface `raw_data['items'][*].title`. Rigby has no way to keyword-check spider items. Would make Rigby's investigation capability materially better. ~2 hours. Consider bundling with (1).

### What's forbidden at S2846 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- AI-source SignalCluster pipeline as originally scoped (3–5 days) — **RETIRED at S2845 as based on the S2844 misdiagnosis.** Real gap was tool-surface, now fixed. If aggregation coverage needs expanding, candidates (1)/(3)/(4) above are the actual work.

---

## S2845 close — what shipped

**Repo canonical (Claude-authored):**
- `core/services/pa_tool_schemas.py` (intelligence_tool schema — `source_spider` param added)
- `core/services/td_handlers_core.py` (signal_clusters handler — reads `source_spider` first, falls back to `source`)
- `00-START-NEXT-SESSION.md` (this file — rewritten for S2846 open)

**Memory (Claude-authored):**
- `feedback_verify_at_raw_orm_before_trusting_tool_no_data.md` — new feedback rule; indexed in `MEMORY.md`

**Runtime impact:** `intelligence_tool` `signal_clusters` now accepts spider-name filter. Post-merge `make recycle-all` per PLAYBOOK-7.4.4 / `feedback_recycle_after_merge`. Docs cascade run at close per `feedback_docs_cascade_at_every_close`.

**Not shipped at S2845 close (deferred to S2846):**
- No workspace mirror — this is an engineering bug fix, not a ratifiable arc close (per twin-canonical rule)
- No A4↔A1 sequencing D-verdict — Chris pivoted to SignalCluster investigation before ratifying
- No PR merge yet — pending Chris greenlight at close

---

## For fuller S2841 discovery + D4 execution context

See:
- Parent: `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md` (§0–§10)
- Addendum: `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md` (§0–§13; §12 = D4 architecture, §13 = D4 picks)
- S2841 handoff: `docs/handoffs/SESSION_2841_STRATEGIC_DISCOVERY.md`
- S2842 handoff: `docs/handoffs/SESSION_2842_S2841_RATIFIED_D0_D6.md`
- S2843 handoff: `docs/handoffs/SESSION_2843_D4_DECOMPOSITION_RATIFIED.md`
- S2844 handoff: `docs/handoffs/SESSION_2844_D4_PICKS_RATIFIED.md`

For older session history (S1–S2840 series), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
