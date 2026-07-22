# Session 2888 — Ledger #13 `_handler_error` extraction to `core/services/td_error.py`

**Date:** 2026-07-22
**Session pin (retired at close):** `pa-737cca9206044b06` (labeled `s2888-td-error-extract`; minted at S2887 close)
**Prior pin retired at S2887 close (not this session):** `pa-4ba45f26c2234a8c`
**Slate label:** S2888 Step 1 — Ledger #13 `td_error.py` extraction (single PR, substrate-only).
**PRs shipped (1 total, merged to origin):**
- u-d-b PR #3400 `82191482a` — extract `_handler_error` to `core/services/td_error.py`

---

## What Chris asked for at session open

"Please begin."

Then: "Yes please proceed" — ratifying the S2887-close first-action (Ledger #13 extraction) with no side-step.

Mid-session decision point after PR #3400 shipped: (A) push through Step 2 Playbook v0.9.0 amendment / (B) close now / (C) push through Step 3 EB.4+C3 dogfood. Chris chose (B).

---

## What shipped

### Ledger #13 — `_handler_error` extraction

PR #3400 (`82191482a`) — factored out the byte-shape-identical `_handler_error` helper from 6 handler files into a canonical `core/services/td_error.py`. The 6-adopter gate Rigby locked at S2875 met at S2886 close (6/6); extraction had been queued for S2887 but pushed one session by the GTM side-step.

**Adopters (all `core/services/`):**
- `td_handlers_governance.py` — S2879 (origin)
- `td_handlers_ops.py` — S2879 (origin)
- `td_handlers_agents.py` — S2884
- `td_handlers_newsletter.py` — S2884
- `td_handlers_content.py` — S2885
- `td_handlers_core.py` — S2886 (6/6 gate met)

**Canonical module contents:**
- 5-key envelope `{success: False, error_code, error, action, **fields}` with `-> Dict[str, Any]` annotation (5-file majority; ops was the outlier without it).
- Full S2879 4-code + S2882 5-code taxonomy: `invalid_params` / `not_found` / `unknown_action` / `dependency_missing` / `permission_denied`.
- Enumeration of all 6 originating adopters + landing sessions (Ledger #22 sunset arc audit trail centralized).
- Frozen-contract note (additive `**fields` safe; required-shape changes require new helper name or fresh SIGN).
- Loud "NOT ops gateway `_tool_error`" warning.

**`td_handlers_ops.py` also got a 1-line adjacency note above its file-local `_tool_error`** (3-key gateway envelope, 12 gateway-layer adopters, stays local per S2875 Q3=A). Prevents future cross-wiring of the two helpers.

**Net diff:** +71 / -141 = **-70 lines**.

### Rigby SIGN cycle (single turn, tool-grounded)

Q1 (byte-identity gate): TOOL-GROUNDED AGREE via 1 `repo_tool.search` + 6 `repo_tool.read_file` calls (independent verification of all 6 adopter HEAD copies).

Q_zoom_out (mandatory per `feedback_zoom_out_ask_per_rigby_sign`), 4 substantive ships:
- **(a) Coupling accretion / escape hatch** — treat `_handler_error` as frozen contract; additive `**fields` metadata safe; required-shape changes need new helper name or fresh SIGN. **Shipped: module docstring §"Contract stability".**
- **(b) Docstring evidence preservation** — centralize the 6-adopter enumeration in shared module docstring so Ledger #22 sunset-arc bookkeeping isn't scattered across git-blame. **Shipped: module docstring §"Adopter enumeration".**
- **(c) `_tool_error` co-existence footgun** — loud "NOT ops gateway" warning in shared module + 1-line adjacency note above ops's `_tool_error`. **Shipped: both.**
- **(d) Fresh push-back** — "byte-identical" is overclaim without hash-compare; reworded to "function-body identical" in the commit message + PR body + this handoff.

Empty `tool_runs` would have been the rubber-stamp signal per Chris's S2777 directive. Rigby's dispatch had 7 tool calls — verifiably substantive.

### Regression suite

Combined error-envelope suite: **100 tests / 100 pass** across `test_s2879_governance_ops_error_envelope` → `test_s2886_core_error_envelope` + `test_zoom_out_tool_2780`. 2 skipped are the pre-existing `MESSAGING_TOOL_ALLOW_SEND=False` gate (unchanged from baseline). Runtime ~39s.

### Post-merge recycle

`make recycle-all` ran after merge per PLAYBOOK-7.4.4. Clean recycle recorded at `82191482a8f2` (surviving=none).

---

## Sidecar findings during the session

### Rigby fleet_health tool-selection quality issue

Character-os Claude Code dispatched an EB.5 dogfood pre-flight reachability probe to Rigby via u-d-b's PA `/api/pa/chat/` on the shared S2888 pin. Rigby routed to `fleet_health` even though character-os isn't a fleet app (R1a rejected at S2887). She caught the mis-fit in her response text but the tool call still fired.

Correct probe was a direct HTTP GET. From this shell post-recycle:
- u-d-b `/health/ping/` → 200 OK in 3ms (`{"ok": true}`)
- u-d-b `/api/pa/chat/` GET → 401 in 2ms (auth-gated as expected; POST with fresh DRF token works)

So character-os EB.5 → u-d-b IS reachable; Rigby just picked the wrong tool to prove it.

Logged as an entry to the Rigby Tool Gap Ledger (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`) via Rigby-dispatched `deliverable_tool.append` per `feedback_rigby_writes_workspace_deliverables`. 1373 chars appended. Low priority; not blocking.

### Test-DB cleanup lesson

Interrupted a background test run mid-teardown by trying to inspect the same DB. Left 10 stale `test_unified_donkey_betz` connections. Recovery: `pg_terminate_backend` all sessions on the test DB via Django ORM, then re-run. Not a Playbook fold — one-off environmental cleanup.

---

## S2889 open sequence (queued at close)

### Step 1 (FIRST THING) — Playbook v0.9.0 amendment cycle

2 rules at 2nd trigger from S2886:

1. **Fold 1: `TransactionTestCase` discipline for dispatcher-DB tests.** S2885 (1st) + S2886 (2nd). Rule shape: handler tests that require `setUp`-created ORM fixtures to be visible to `ToolDispatcher.execute_sync` MUST inherit from `TransactionTestCase`, not `TestCase`. Candidate slot: **PLAYBOOK-6.10.11** or **PLAYBOOK-7.4.5**.
2. **Fold 2: Shared-taxonomy branch fortification.** S2885 (1st) + S2886 (2nd). Rule shape: when multiple return branches within a single handler emit the same `error_code`, the migrated-envelope test MUST assert either the distinguishing `action` field or a message-body substring to prevent false-pass on branch-crossing. Candidate slot: EXTENDS **PLAYBOOK-6.10.9** or fresh sibling rule.

Both ratifiable in a single MINOR amendment cycle (v0.9.0) — 2-rule slate is within the shape ratified for v0.7.0 (2-rule) and v0.8.0 (1-rule).

### Step 2 — Live UI dogfood of EB.4 + C3 (Character OS side)

Reference-customer verification loop. Requires character-os SPA running. Full flow in S2888 open sequence Step 3 (unchanged).

### Step 3 — Broader net-new engineering candidates

Per `feedback_engineering_bias_over_audit`, list net-new first:
1. Playbook v0.9.0 — see Step 1.
2. EB.4 + C3 live dogfood — see Step 2.
3. Character OS C4 PD-1 timeout fix (Sev-1 defect, character-os-side only).
4. Character OS C5 non-realtime bridge invocation + C6 tool catalog.
5. Rigby Tool Gap Ledger review — 1 new entry accreted this session (`fleet_health` mis-routing for non-fleet targets, low priority). Consider a slate PR that picks 1-2 open ledger items.
6. Carried from S2886 open Step 4 items 5-47, unchanged.

### What's forbidden at S2889 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC). Rejected at S2887 as architectural mis-fit.

---

## A4 warm-up ledger

Zero A4 spend this session — pure substrate refactor. A1 shipping spend was PR #3400.

Constraint set (a)…(uu) as ratified at S2887 close — no additions this session.
