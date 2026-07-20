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

### Step 2 — A4↔A1 sequencing RATIFIED (S2846) + open Week 1 substrate

**Ratified 2026-07-20 (S2846):** Chris D-verdict = **option (a)** — sequential A1-first + A4 pipeline warm-up (prospect list + 3–5 intro emails) in parallel; full A4 engagement packaging BLOCKED until A1 Week 1 substrate demonstrably ships. All four of Rigby's zoom-out folds (spend / evidence / narrative / operational coupling) accepted; her 6-line constraints block codified below as slate discipline (no renegotiation midstream).

**A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified):**

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 Week 1 shipping spend.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth" until drift-lint is shipped (S2846 ✓) AND A1 workspace attribution exists.
3. **No capability claims:** A4 outreach must make ZERO claims about per-workspace caps, cost reporting, invoicing, or audit trails until A1 Week 1 ships.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only (no "productized offering" language during the parallel period).
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3–5 total intros); no expansion without explicit slate change.
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables; allowed responses are one standard reply + optional meeting link only.

Substrate verification findings (from S2845 Rigby SIGN §2, tool-grounded, still standing):
- `LLMCallLog.workspace` FK: NOT present in `core/models_llm_routing.py:297`; no partial migration
- Per-workspace cost cap: GLOBAL cap machinery exists (`core/services/ops_autopilot/budget.py:238–506` three-tier controller), no `workspace_daily_cap` / `workspace_budget` symbols; Week 1 must extend not just wire
- Ledger export: NOT shipped (planned for Week 2–3)
- Duration reality check: `docs/COST_SURVIVAL_AUDIT.md` §A effort table quotes ~1 working day for FK + ExternalAPICallLog telemetry — real Week 1 could collapse to ~2–3 days if scoped tight (FK + workspace-aware cost cap only; defer Ledger export to Week 2)

**Next S2846 action:** open A1 Ledger Bet Week 1 with `LLMCallLog.workspace` FK migration + per-workspace cost cap extension (following IOS Existing Implementation Analysis discipline per `feedback_cycle_1a_verify_before_build`).

### Step 3 — Concurrent A4 pipeline warm-up (light-touch)

- Prospect list construction (5–15 named mid-size AI startups / enterprise AI ops teams)
- **Now unblocked by S2845 fix:** `intelligence_tool` `signal_clusters` with `source_spider='hackernews'` / `'devto'` / `'techcrunch_startups'` / `'producthunt'` / `'huggingface'` / `'mit_tech_review'` / `'arstechnica'` returns AI-tooling market signals as discovery substrate
- Combine with `kb_tool` research on named companies + Chris-known network
- Draft 3–5 cold intro emails framed as "we're shipping the audit substrate this week; want to be a design partner?"

### Net-new engineering candidates for S2846

Per `feedback_engineering_bias_over_audit`, list net-new candidates first at every session open. Chris directive S2845 close 2026-07-20: promote (0) to first slate item; treat Rigby's tool-surface gaps as first-class product work per new memory rule `feedback_rigby_tool_gap_ledger`.

0. **[SHIPPED S2846 · PR #3303]** Handler/schema drift lint — `python manage.py check_pa_tool_drift`. Static AST analysis of every `PA_TOOL_SCHEMAS` entry against its registered `ToolDispatcher` handler; reports HANDLER_ONLY_PARAM / SCHEMA_ONLY_PARAM / HANDLER_ONLY_ACTION / SCHEMA_ONLY_ACTION / MISSING_HANDLER / SOURCE_UNAVAILABLE. First-run scan: 114 tools · **69 DRIFT · 43 CLEAN · 1 MISSING (run_agent) · 1 SOURCE_UNAVAILABLE (research_and_create_tool)**. Documented LIMITATIONS: sub-handler-routing false-positive class (`sp = dict(payload); return self._handle_other(sp)` — MVP doesn't chase). Real bugs surfaced already: `autopilot_tool` (6 hp params handler reads, schema hides), `active_priority_tool` (hp=`trigger_source`), and others. Triage of the 69 DRIFT entries deferred to a separate arc / drip via the Rigby Tool Gap Ledger.

Additional candidates queued (deferred; ledger tracks all Rigby tool gaps — see workspace `b4503364-2573-4401-9e28-61a739e0ce50` deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` "Rigby Tool Gap Ledger"):

1. **SignalCluster naming rewrite** — current cluster names use top-2 frequent tokens ("Comments, Score emerging trend"), producing semantically opaque labels even when underlying signals are strong. `signal_aggregation_service.py:312` already extracts `_extract_entity_tokens`; naming should prefer entity tokens over raw frequency. ~1 day. Would materially improve `intelligence_tool` `signal_clusters` discovery UX.

2. **Multi-source `source_spider` filter** — S2845 shipped single-source filter. Multi-source (`has_any_keys`) would let one call return "all AI-adjacent clusters" in one shot instead of Rigby looping 14x. ~1 hour. Ship when A4 prospect research needs it. (Ledger entry.)

3. **`huggingface` returns 0 SignalCluster rows despite 24 spider runs/7d** — aggregation pipeline drops it somewhere (likely `is_processed=False` + `embedding_text=''` combo per `_fetch_recent_spider_data` at line 262). ~half day. Wait until A4 prospect research needs it. (Ledger entry.)

4. **`spider_status_tool.search` returns empty `preview` field** — reads `LegacySpiderData` but doesn't surface `raw_data['items'][*].title`. Rigby has no way to keyword-check spider items. ~2 hours. Consider bundling with (1). (Ledger entry.)

5. **`spider_status_tool.list` pagination** — returns 44/88 spiders with no offset param; drove false-negative "spider not found" reporting in S2845 Layer 1 probe. ~2 hours. (Ledger entry.)

Two-plane audit (`LegacySpiderData` 15k rows vs `SpiderData` 111k rows — one gets writes, the other is dead substrate for AI-adjacent content) is a real problem but bigger. Probably 3–5 day arc when ready. Not queued as candidate; parked for post-A1-Week-1.

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
- `feedback_rigby_tool_gap_ledger.md` — new feedback rule (Chris directive S2845 close): Rigby tool-limitation flags become ledger entries in workspace `b4503364-...` "Rigby Tool Gap Ledger" deliverable, NOT silent workarounds; her tool surface IS the A1/A4 product substrate

**Workspace canonical (Rigby-authored per `feedback_rigby_writes_workspace_deliverables`):**
- "Rigby Tool Gap Ledger" deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` (`deliverable_type='engineering_backlog'`, `category='platform'`) with 5 seed entries from S2845 discoveries. Post-create ORM cleanup applied (stripped "Rigby: " title prefix, cleared `diagnostic_status`/`diagnostic_code` per known `deliverable_tool.create` gotchas).

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
