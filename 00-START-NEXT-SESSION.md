# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2888 CLOSE → Ledger #13 `_handler_error` extraction shipped (u-d-b PR #3400 `82191482a`, -70 net lines) (2026-07-22; picks up as S2889) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2888 close).** S2888 shipped the S2887-queued Ledger #13 extraction as a single-PR slate. Rigby SIGN was TOOL-GROUNDED AGREE (7 `repo_tool` calls). Chris chose (B) close-now after PR #3400 merged — Playbook v0.9.0 amendment + EB.4+C3 dogfood queue to S2889.

- **u-d-b PR #3400** `82191482a` — extract `_handler_error` to `core/services/td_error.py`. 6 handler files each drop their file-local copy; canonical module carries the 5-key envelope contract + full taxonomy + adopter enumeration + frozen-contract note + "NOT ops gateway" warning. `td_handlers_ops.py` gets a 1-line adjacency note above its file-local `_tool_error` (3-key gateway envelope, stays local). Regression: 100/100 pass (test_s2879 → test_s2886 + test_zoom_out_tool_2780). Net diff: +71 / -141 = **-70 lines**.

Full session context: `docs/handoffs/SESSION_2888_TD_ERROR_EXTRACTION.md`.
Sidecar: Rigby Tool Gap Ledger got 1 new entry (`fleet_health` mis-routing for non-fleet targets, low priority) — deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` in Donkey Betz workspace.

---

## S2889 open sequence

### Step 1 (FIRST THING) — Playbook v0.9.0 amendment cycle

2 rules at 2nd trigger from S2886. Both ratifiable in a single MINOR amendment (v0.9.0) — 2-rule slate matches v0.7.0's shape.

1. **Fold 1: `TransactionTestCase` discipline for dispatcher-DB tests.** S2885 (1st) + S2886 (2nd). Rule shape: "Handler tests that require `setUp`-created ORM fixtures to be visible to `ToolDispatcher.execute_sync` MUST inherit from `TransactionTestCase`, not `TestCase`." Candidate slot: **PLAYBOOK-6.10.11** or **PLAYBOOK-7.4.5**.
2. **Fold 2: Shared-taxonomy branch fortification.** S2885 (1st) + S2886 (2nd). Rule shape: "When multiple return branches within a single handler emit the same `error_code`, the migrated-envelope test MUST assert either the distinguishing `action` field or a message-body substring to prevent false-pass on branch-crossing." Candidate slot: EXTENDS **PLAYBOOK-6.10.9** or fresh sibling rule.

Amendment envelope goes in `docs/research/implementation/RATIFICATION_2026-07-XX_PLAYBOOK_V0_9_0.md` following the v0.8.0 template. Chris D-verdict required.

### Step 2 — Live UI dogfood of EB.4 + C3 (Character OS side)

Reference-customer verification loop. Requires character-os SPA running. Open the running character-os SPA at `http://localhost:5173` (per character-os `scripts/start-local-real.sh`; the S2887 audit doc's `:5174` reference was aspirational):

1. Navigate to `/settings/engine-connections`.
2. Configure a connection: URL = u-d-b's PA endpoint (`http://localhost:8000`), token = a fresh DRF token for Chris's user on u-d-b, label = "Local u-d-b".
3. Hit `test_ping` — expect 200 with real latency. (Verified reachable at S2888 close: `/health/ping/` 200 in 3ms, `/api/pa/chat/` GET 401 auth-gated.)
4. Start a realtime session with a spokesperson.
5. Ask a question that would trigger `consult_engine` (portfolio-level context question).
6. Verify a fresh `Asset(role=BRIDGE_ANSWER)` appears in `/workspace/assets/?role=bridge_answer` with the answer in `inline_content`.

This is the audit's ratified reference customer path. If any step fails, the failure IS the next item to fix.

### Step 3 — Net-new engineering candidates for S2889 (broader list)

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **Carried from S2888 close — Playbook v0.9.0 amendment cycle.** See Step 1.
2. **Carried from S2888 close — EB.4 + C3 live dogfood.** See Step 2.
3. **Carried from S2887 close — Character OS side C4 PD-1 timeout fix.** Sev-1 defect: Django `MediaEngineClient` 60s timeout fires before media-engine's ~63s Runway poll. Blocks reliable realtime session start in real mode. Character OS-side only.
4. **Carried from S2887 close — Character OS side C5 non-realtime bridge invocation + C6 tool catalog.** Follow-on from audit §3.2.
5. **NEW at S2888 close — Rigby Tool Gap Ledger review.** 1 new entry accreted at S2888 (`fleet_health` mis-routing for non-fleet targets, low priority). Total open engineering_backlog rows in Donkey Betz workspace: 4. Consider a slate PR that picks 1-2 open ledger items.
6. **Carried from S2886 — everything from S2886 open Step 4** items 5-47, unchanged.

### What's forbidden at S2889 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC). Rejected at S2887 as architectural mis-fit.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution.
- R1 fleet reject-mode flip — deferred; fleet HMAC path dormant per S2887 telemetry finding.
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849.
- `requested_model_id` field split on `LLMCallLog` — migration required.
- `was_policy_reroute` field on `LLMCallLog` — migration required.
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate).

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2888 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2888: zero A4 spend — pure substrate refactor. A1 shipping spend was u-d-b PR #3400.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2888)

See:
- **S2888 handoff (current):** `docs/handoffs/SESSION_2888_TD_ERROR_EXTRACTION.md`
- **S2887 handoff + audit:** `docs/handoffs/SESSION_2887_S2887_SIDE_STEP_GTM_AUDIT.md`, `docs/investigations/2026-07-22_RIGBY_SAAS_AND_COS_BRIDGE_GTM_GAP_AUDIT.md`
- **S2886 handoff:** `docs/handoffs/SESSION_2886_CORE_CRITICALITY_FIRST_ERROR_ENVELOPE.md`
- **S2885 handoff:** `docs/handoffs/SESSION_2885_CONTENT_ERROR_ENVELOPE.md`
- **S2884 handoff:** `docs/handoffs/SESSION_2884_AGENTS_NEWSLETTER_CRITICAL_SLICE.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
