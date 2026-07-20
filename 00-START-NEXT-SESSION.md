# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2844 CLOSE → D4 PICKS RATIFIED · SIGNALCLUSTER FIX SHIPPED (2026-07-20; picks up as S2845) — **S2845 OPENS ON A4 ENGAGEMENT #1 SCOPING · D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-20 (S2844 close).** S2844 opened per S2843 directive on the three D4 picks against §12 architecture. Claude preliminary D4-A pick was A2; Rigby SIGN returned DISAGREE with evidence-grounded alternative A4+A1 (Atlas parking rule against A2 as framed; quantified A1 cost-attribution blocker; A3 activation gate). Claude accepted evidence and updated to joint A4+A1 recommendation. Chris pushback reframed GTM as testable platform capability: "can DBZ help me get customers?" Capability probe (3 wedges × 2 variants) returned empty across all three — SignalCluster endpoint returned generic top clusters regardless of query. Rigby zoom-out identified fastest-fix hypothesis (API-contract bug). Chris D-verdicts issued: D4-A = A4 + A1 / D4-B = YES / D4-C = DEFER / run diagnostic. SignalCluster semantic-query fix shipped in-session with two same-session bug catches (initial patch missed source auto-injection from shared search-action schema default; patched via enum-value guard). Fix verified working via ORM probe (8 clusters returned for `query='remote contract'`, 4 for `pattern_type='opportunity_window'`, 20 for `min_confidence=0.7`). Honest finding: interface is fixed but underlying cluster data doesn't contain AI/agent/solopreneur/SMB relevant signals — spiders feeding cluster aggregation are sports/news/gaming/generic-jobs, not AI-community sources. Building AI-source SIGNAL cluster pipeline is a separate 3–5 day project, deferred until A4/A1 wedge execution needs it.

**Docs:** handoff `docs/handoffs/SESSION_2844_D4_PICKS_RATIFIED.md` (NEW); §13 "D4 Picks Ratification (S2844)" appended to `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`; this file rewritten below to reflect ratified D4 execution state. **Workspace mirror:** content mirror + ratification envelope in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` (Rigby-authored per `feedback_rigby_writes_workspace_deliverables`).

**Code shipped:** `core/services/td_handlers_core.py` (signal_clusters handler at line 3456 — added ~40 lines of filter logic + source-filter guard) + `core/services/pa_tool_schemas.py` (intelligence_tool schema — advertises `pattern_type` / `min_confidence` / `window_hours` params).

**Session pin `pa-4a5f86ef64c24366` RETIRED at S2844 close** (seventy-fourth consecutive per S2770+ pattern). Fresh mint required at S2845 open with label reflecting the first A4 scoping action attempted.

---

## S2845 open sequence

**S2845 opens on A4 engagement #1 scoping.** D4 architecture ratified (§12); D4 picks ratified (§13). D6 discovery moratorium still in force. No new strategic arcs, no portfolio expansion, no new evaluation frameworks, no layer-boundary design arcs, no reopening D4.

### Ratified D4 execution state (from §13)

- **D4-A** = A4 (Governance Consulting engagement #1) **paired with A1** (Rigby standalone SaaS) per §12.3 rule
- **D4-B** = YES (Ledger Bet fold — `LLMCallLog.workspace` FK + per-workspace cost cap + Ledger export becomes A1's weeks 1–2 substrate)
- **D4-C** = DEFER (Foundry Phase 2C)

### Step 1 — Session-open atomic mint — **FIRST-ACTION FRESH MINT BEFORE ANY PA DISPATCH**

`pa-4a5f86ef64c24366` retired at S2844 close. Wrapper (`tools/pa_local.sh:563`) still points at it — intended failure mode forcing atomic mint before any PA dispatch. **Do NOT skip this step.**

Run the atomic close command (retires current wrapper pin + mints fresh + rewrites wrapper line 563 — all in one transaction):

```bash
python manage.py session_lifecycle close --label s2845-a4-<first-action-context>
# e.g. s2845-a4-prospect-list, s2845-a4-engagement-scope, s2845-a1-ledger-week1
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh   # should show new pin
```

Only THEN route messages via `bash tools/pa_local.sh "<msg>"`.

### Step 2 — A4 engagement #1 scoping

Recommended first actions (Claude proposes → Rigby joint SIGN → Chris ratifies per `feedback_claude_rigby_agree_first_chris_yes_no`):

1. **Prospect list construction (5–15 named mid-size AI startups / enterprise AI ops teams)** — combine direct spider search (`spider_status_tool.search` on techcrunch / crunchbase / venturebeat / producthunt / github with entity-extraction on returned items) + `kb_tool` research on named companies + Chris-known network. Note: SignalCluster is not the substrate for this today (see §6 of S2844 handoff for why).

2. **Engagement structure** — scope-of-work template, pricing framework ($10–100k range), deliverable shape (audit report / governance readiness assessment / platform reality-check / other), engagement duration (4–8 wks).

3. **Outreach mechanism** — Rigby drafts cold email templates, LinkedIn outreach copy, discovery-call talk track. Chief-of-Staff Employee OS job for orchestration.

### Step 3 — Concurrent A1 Ledger Bet weeks 1–2

D4-B = YES ratified. A1 Ledger Bet substrate weeks 1–2:
- `LLMCallLog.workspace` FK (~1 wk engineering per `docs/COST_SURVIVAL_AUDIT.md` §A)
- Per-workspace cost cap enforcement
- OpsRun / OpsRunEvent / ToolCallRecord as public API surface
- Ledger export (CSV / JSON for customer-facing cost accounting)

**Sequencing between A4 and A1 (concurrent / sequential / gated) is a S2845-open planning decision per §12.4.** Not yet decided. Options to route to Chris via joint Claude+Rigby recommendation:
- **Concurrent:** A4 scoping + A1 Ledger Bet week 1 in parallel (uses Chris-time in both directions; risk of split focus)
- **Sequential A4-first:** A4 engagement scoping this week → first engagement started → A1 Ledger Bet starts once A4 is in delivery phase
- **Sequential A1-first:** A1 Ledger Bet ships first (Chris's product moat strengthens) → A4 engagements use the newly-shipped platform as case study material
- **Gated:** A4 kickoff waits until A1 Ledger Bet week 1 is done (~5 days)

### What's forbidden at S2845 (per D6 discovery moratorium; still in force)

- No new strategic discovery arcs.
- No new opportunity portfolio expansions.
- No new evaluation frameworks.
- No layer-boundary design arcs.
- No re-opening the D4 wedge frame or picks.

Governance work (Playbook amendments, ratification cadence, docs cascades) continues on cadence but is de-prioritized against A4 engagement #1 execution.

### What's queued but deferred (do NOT open at S2845 unless Chris directs)

- **AI-source SignalCluster pipeline** (3–5 days) — build cluster aggregation on github / devto / hackernews / medium / substack / producthunt AI-tagged content; deferred until A4/A1 leadgen actually needs signal-driven prospect finding.
- **Docs restructuring arc** — queued per `project_docs_restructuring_arc_queued` memory; overrides against BettingPage but stays behind wedge execution.

---

## S2844 close — what shipped

**Repo canonical (Claude-authored):**
- `docs/handoffs/SESSION_2844_D4_PICKS_RATIFIED.md` (NEW — SIGN cycle + Chris D-verdicts + ratified picks + code fix summary + provenance)
- `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md` §13 "D4 Picks Ratification (S2844)" appended
- `00-START-NEXT-SESSION.md` (this file — rewrites `S2844 open sequence` into `S2845 open sequence` on A4 engagement scoping)
- `core/services/td_handlers_core.py` (signal_clusters handler filter logic)
- `core/services/pa_tool_schemas.py` (intelligence_tool schema — new params advertised)

**Workspace canonical (Rigby-authored per `feedback_rigby_writes_workspace_deliverables`):**
- Content mirror of S2844 handoff in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`
- Ratification envelope (governance category, deliverable_type `ratification_record`)

**Runtime impact:** SignalCluster gateway now returns semantically-filtered results. Post-merge `make recycle-all` run per PLAYBOOK-7.4.4 / `feedback_recycle_after_merge`. Docs cascade run at close per `feedback_docs_cascade_at_every_close`.

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
