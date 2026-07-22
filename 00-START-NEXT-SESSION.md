# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2891 CLOSE → ops_tool.bridge_activity_digest shipped + Tool Gap Ledger reconciliation (Rigby-executed) + zoom-out fold row 156 persisted (2026-07-22; picks up as S2892) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2891 close).** S2891 shipped one code PR — the Rigby-narratable `ops_tool.bridge_activity_digest` action (PR #3406 `26c3a8b4c`) — plus Rigby executed same-session Tool Gap Ledger reconciliation (rows #20 + #21 moved from Open to Shipped with S2870 marker), and one zoom-out fold row appended to `logs/zoom_out_classifications.jsonl` (row 156, `future_trigger`).

- **u-d-b PR #3406** `26c3a8b4c` — new `ops_tool.bridge_activity_digest` action. Delegates to `_ops_recent_bridge_calls` for filter + scoping + qs computation; reshapes into narrative + structured_facts. Sample narrative from live post-merge dispatch: *"In the last 6h, character-os called u-d-b 2 times — 2 consult_engine. Median latency 4565ms. Most recent 151 min ago via consult_engine asking 'What single word best describes u-d-b Rigby?' (user chris)."* 13/13 tests pass; S2890 regression 13/13 pass; live post-merge Rigby dispatch verified.
- **Tool Gap Ledger reconciliation** — Rigby's F-BLOCKING at joint SIGN caught that both #20 (signal_clusters filter defaults) and #21 (spider_data_bridge crash) were already shipped in S2870 slate. Ledger deliverable `5c84e75a-…` updated via `deliverable_tool.update`; Open entries now = #5 + #16 only.
- **Zoom-out fold row 156** — `bridge_activity_digest_plus_ledger_stalesweep`, `future_trigger`. Trigger for close-ceremony ledger-staleness gate: 2+ more incidents of proposed-ledger-row-already-shipped surfacing during joint SIGN.

**Workspace twin mirrors (Rigby-authored per feedback_rigby_writes_workspace_deliverables):**
- Content mirror: `23d89586-4505-42de-8e05-e6279926e05e` (initiative_phase_doc, engineering)
- Ratification envelope: `22ded284-8bd5-480e-a207-b2700fb2a890` (ratification_record, governance)

Full session context: `docs/handoffs/SESSION_2891_BRIDGE_ACTIVITY_DIGEST.md`.

---

## S2892 open sequence

### Step 1 (FIRST THING) — Stand by for character-os exploration

Chris continues driving character-os SPA in a parallel Claude terminal. u-d-b Claude's job at S2892 open is to **stand by** and answer narrowly when Chris pings.

Reference substrate to consult when questions land:
- `/Donkey_Betz/docs/2026-07-22_CHARACTER_OS_UI_TO_UDB_REFERENCE_SHEET.md` — surface → endpoint map.
- `/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md` — repo ownership, port hazards, escalation rules.
- `ops_tool.recent_bridge_calls` — dispatch via Rigby to see what character-os just asked u-d-b (raw items[] envelope).
- `ops_tool.bridge_activity_digest` — S2891 new action for casual asks. Rigby returns one-sentence narrative + minimal structured_facts.

Live example dispatches (both work today):
```
Rigby, show me the last 5 bridge calls from character-os in the past hour.       ← raw items[]
Rigby, what has character-os been up to in the last 6 hours?                     ← digest narrative
```

### Step 2 — Net-new engineering candidates (per feedback_engineering_bias_over_audit)

Propose 1-3 net-new pieces to Chris at any point when the exploration mode reaches a natural pause. Priority order:

1. **PLAYBOOK-3.2.3/3.2.4 compliance sweep** — grep u-d-b test files for handler-dispatcher tests using plain `TestCase` where `TransactionTestCase` should apply; may catch latent silent regressions. Carried forward from S2891.
2. **Explicit `bridge_tool` marker on character-os side** — coordinated via the character-os Claude; addresses ledger row 155 `future_trigger` (source-string sniffing rename risk). Would require cross-repo change: character-os POSTs a `bridge_tool` field alongside `source`, u-d-b's `recent_bridge_calls` + `bridge_activity_digest` prefer it over source parsing.
3. **LLMCallLog cost join for bridge calls** — extend `recent_bridge_calls` + `bridge_activity_digest` with cost data from `LLMCallLog` (requires join key verification). Rigby S2890 SIGN Item 3 recommended deferring; verify joinability first.
4. **Rigby Tool Gap Ledger sweep round 2** — pick from remaining open entries #5 (handler/schema drift detection lint, ~2 hr, `slated_for_S2846`) or #16 (twin-mirror close-ceremony enforcement, ~15 min–2 hr).
5. **Close-ceremony ledger-staleness pre-check** — same-session mitigation candidate from S2891 zoom-out fold row 156. Deferred pending trigger accumulation (needs 2 more incidents before rule proposal).

### What's forbidden at S2892 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC). Rejected at S2887 as architectural mis-fit.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original Step 2 EB.4/C3 scripted dogfood** — Chris pivoted to exploration; scripted dogfood deferred until Chris re-scripts.
- **Testing Discipline chapter candidacy** — ledger row 154 `future_trigger`. Trigger: 2 more test-authoring rules land in §3.2 before Chapter 3 is promoted to FULL, OR one SIGN cycle blocked by ambiguous test-authoring slot.
- **Bridge call observability rename-risk future_trigger** — ledger row 155. Trigger: character-os renames a source string, OR 2+ tools confusion, OR SDK/API-doc drafting stage.
- **Close-ceremony ledger-staleness gate** — zoom-out ledger row 156 `future_trigger`. Trigger: 2+ more incidents of proposed-ledger-row-already-shipped OR one incident of already-shipped ledger row surviving past pre-code verification into implementation.
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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2891 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2891: zero A4 spend — pure engineering + governance.** A1 shipping spend was u-d-b PR #3406 (digest) + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2891)

See:
- **S2891 handoff (current):** `docs/handoffs/SESSION_2891_BRIDGE_ACTIVITY_DIGEST.md`
- **S2890 handoff:** `docs/handoffs/SESSION_2890_OPS_TOOL_RECENT_BRIDGE_CALLS.md`
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
