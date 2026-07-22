# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2890 CLOSE → Playbook v0.9.0 ratified + ops_tool.recent_bridge_calls shipped + parent-workspace multi-Claude coordination rules live (2026-07-22; picks up as S2891) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2890 close).** S2890 shipped three PRs — Playbook v0.9.0 MINOR amendment (rules 3.2.3 + 3.2.4) at PR #3402 (`147dcc9cc`), its close cascade at PR #3403 (`aeda6ec6a`), and the character-os bridge call observability action at PR #3404 (`d2f72c428`). Plus two parent-workspace docs written to `/Users/donkeyking/Donkey_Betz/docs/` (reference sheet + multi-Claude rulebook). Chris drove character-os UI exploration in a parallel Claude terminal for the second half of the session.

- **u-d-b PR #3404** `d2f72c428` — new `ops_tool.recent_bridge_calls` action returns recent `ChatConversation` rows sourced from character-os bridge tools. Detection via `source__startswith='character-os-'`. Answers "what bridge calls hit u-d-b in the last N minutes?" for the operator surface. 13/13 tests pass; live post-merge Rigby dispatch verified.
- **u-d-b PR #3402** `147dcc9cc` — Playbook v0.9.0: PLAYBOOK-3.2.3 (dispatcher-DB `TransactionTestCase`) + PLAYBOOK-3.2.4 (shared-taxonomy branch fortification). First Chapter 3 extension since v0.2.0.
- **Parent workspace docs at `/Donkey_Betz/docs/`:**
  - `2026-07-22_CHARACTER_OS_UI_TO_UDB_REFERENCE_SHEET.md` — 34-route SPA + 9-tool bridge/local classification.
  - `MULTI_CLAUDE_COORDINATION.md` — 11-section rulebook for u-d-b Claude + character-os Claude concurrency.

Full session context: `docs/handoffs/SESSION_2890_OPS_TOOL_RECENT_BRIDGE_CALLS.md`.

---

## S2891 open sequence

### Step 1 (FIRST THING) — Stand by for character-os exploration

Chris continues driving character-os SPA in a parallel Claude terminal. u-d-b Claude's job at S2891 open is to **stand by** and answer narrowly when Chris pings.

Reference substrate to consult when questions land:
- `/Donkey_Betz/docs/2026-07-22_CHARACTER_OS_UI_TO_UDB_REFERENCE_SHEET.md` — surface → endpoint map.
- `/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md` — repo ownership, port hazards, escalation rules.
- `ops_tool.recent_bridge_calls` — dispatch via Rigby to see what character-os just asked u-d-b (window `1h` / `6h` / `24h`, filter by `bridge_tool_name` or `workspace_id`).

Live example dispatch (works today):
```
Rigby, show me the last 5 bridge calls from character-os in the past hour.
```

### Step 2 — Net-new engineering candidates (broader list, per feedback_engineering_bias_over_audit)

Propose 1-3 net-new pieces to Chris at any point when the exploration mode reaches a natural pause. Priority order:

1. **Bridge activity Rigby-facing digest** — extend `recent_bridge_calls` with a natural-language summary shape (e.g. `ops_tool.bridge_activity_digest`) that Rigby narrates instead of returning raw JSON. Useful when Chris asks casually and doesn't want the raw envelope.
2. **Rigby Tool Gap Ledger sweep** — pick 1-2 open engineering_backlog rows from the Donkey Betz workspace and close them. Ledger surfaced at S2888 (`fleet_health` mis-routing, low priority) is the latest carry-forward.
3. **PLAYBOOK-3.2.3/3.2.4 compliance sweep** — grep u-d-b test files for handler-dispatcher tests using plain `TestCase` where `TransactionTestCase` should apply; may catch latent silent regressions.
4. **Explicit `bridge_tool` marker on character-os side** — coordinated via the character-os Claude; addresses ledger row 155 `future_trigger` (source-string sniffing rename risk). Would require cross-repo change: character-os POSTs a `bridge_tool` field alongside `source`, u-d-b's `recent_bridge_calls` prefers it over source parsing.
5. **LLMCallLog cost join for bridge calls** — extend `recent_bridge_calls` with cost data from `LLMCallLog` (requires join key verification). Rigby T1 SIGN Item 3 recommended deferring; verify joinability first.

### What's forbidden at S2891 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC). Rejected at S2887 as architectural mis-fit.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original Step 2 EB.4/C3 scripted dogfood** — Chris pivoted to exploration; scripted dogfood deferred until Chris re-scripts.
- **Testing Discipline chapter candidacy** — ledger row 154 `future_trigger`. Trigger: 2 more test-authoring rules land in §3.2 before Chapter 3 is promoted to FULL, OR one SIGN cycle blocked by ambiguous test-authoring slot.
- **Bridge call observability rename-risk future_trigger** — ledger row 155. Trigger: character-os renames a source string, OR 2+ tools confusion, OR SDK/API-doc drafting stage.
- **R1 fleet reject-mode flip** — deferred; fleet HMAC path dormant per S2887 telemetry.
- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution.
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849.
- `requested_model_id` field split on `LLMCallLog` — migration required.
- `was_policy_reroute` field on `LLMCallLog` — migration required.
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate).
- C4 PD-1 timeout coordination defect + C5 non-realtime bridge invocation + C6 tool catalog — character-os side follow-ons.

---

## Two-Claude concurrency safety envelope (still active from S2889)

Rulebook: `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`.

- Each terminal uses its own Rigby conversation pin — no state collision.
- Different repos, different branches — no git collision.
- **Watch:** character-os Docker postgres previously captured u-d-b's `:5433` via IPv6 wildcard (S2885). `USE_PGBOUNCER=0` still in force in both `.env` files. If character-os side runs `docker compose up`, verify port ownership before restarting u-d-b.
- Shared u-d-b PA endpoint (`http://localhost:8000`) — both Claudes may drive it; surface handles concurrent conversations.

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2890 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2890: zero A4 spend — pure Playbook amendment + engineering.** A1 shipping spend was u-d-b PRs #3402/#3403/#3404.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2890)

See:
- **S2890 handoff (current):** `docs/handoffs/SESSION_2890_OPS_TOOL_RECENT_BRIDGE_CALLS.md`
- **S2889 handoff:** `docs/handoffs/SESSION_2889_PLAYBOOK_V0_9_0_RATIFIED.md`
- **S2888 handoff:** `docs/handoffs/SESSION_2888_TD_ERROR_EXTRACTION.md`
- **S2887 handoff + audit:** `docs/handoffs/SESSION_2887_S2887_SIDE_STEP_GTM_AUDIT.md`
- **S2886 handoff:** `docs/handoffs/SESSION_2886_CORE_CRITICALITY_FIRST_ERROR_ENVELOPE.md`
- **S2885 handoff:** `docs/handoffs/SESSION_2885_CONTENT_ERROR_ENVELOPE.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **Character-os UI → u-d-b reference sheet:** `/Users/donkeyking/Donkey_Betz/docs/2026-07-22_CHARACTER_OS_UI_TO_UDB_REFERENCE_SHEET.md`

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
