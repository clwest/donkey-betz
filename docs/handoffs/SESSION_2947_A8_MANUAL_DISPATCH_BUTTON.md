# SESSION 2947 — A8 Manual Dispatch Button (Shape C)

**Date:** 2026-07-24
**Status:** CLOSED — PR #3533 merged, live-verified end-to-end
**HEAD at close:** `5fb5db1a4`
**Merge commit:** `5fb5db1a4` (squash-merge of feat/s2947-a8-manual-dispatch-button)
**Twin mirrors:**
- Content: `07dd725f-7404-4cc1-b474-9bb638da42db` (Architecture & Research, category `initiative_phase_doc`)
- Ratification: `5e69fdb5-ad4f-4e6b-b9e3-b1124cc53f4d` (Architecture & Research, `deliverable_type='ratification_record'`, category `governance`)
- Both diagnostic-flag-cleared via ORM per known bug.

---

## What shipped

Operator-facing "Dispatch now" button in the Workspace Signal Dispatches tab. Chris picked A8 as S2947 first-action after plain-English framing of the 5 deferred-queue candidates carried forward from S2946. Directly amplifies the S2946 diversity-denominator lift (more active clusters → more useful surface to dispatch against).

**Shape C ratified** (paste-in cluster UUID + inline resolve preview + rule auto-pick) over Shape A (two text inputs, debug-tool feel) and Shape B (~2 hrs full dropdown). **No `force` param in the API surface** — UI is safer than CLI by default.

## Files shipped

- **NEW** `SignalDispatchService.create_manual_dispatch` (+126 in `core/services/signal_dispatch_service.py`) — shared manual-dispatch logic. Structured error dict with `error_code` catalog.
- **REWRITE** `core/management/commands/dispatch_signal.py` (-80 net) — thin wrapper over the new service method. Behavior-identical to the pre-S2947 CLI.
- **NEW** `signal_dispatches_manual` view (POST) + `signal_dispatch_resolve_cluster` view (GET) in `core/views_signal_dispatch.py` (+129).
- **NEW** 2 URL routes in `core/urls.py`:
  - `POST /api/v1/agents/signal-dispatches/manual/`
  - `GET /api/v1/agents/signal-dispatches/resolve-cluster/<uuid:cluster_id>/`
- **NEW** `ManualDispatchModal` component + "Dispatch now" header button in `frontend/src/pages/workspace/tabs/SignalDispatchesTab.tsx` (+282).
- **NEW** `agentsApi.signalDispatchesManual()` + `agentsApi.signalDispatchResolveCluster()` in `frontend/src/lib/api.ts` (+5).
- **NEW** 11 regression tests in `core/tests/test_s2934_signal_dispatch_harness.py` (+153). 25/25 pass.

## Rigby T1 SIGN (with tool_runs evidence — non-rubber-stamp)

Rigby used `repo_tool.read_file` + `repo_tool.search` to verify claims against actual code:

**Design invariants — 5/5 PASS:**
1. Shape C ratified (paste UUID + inline resolve + auto-rule-pick) — PASS
2. No `force` param in API surface — PASS (test asserts `force=True` body still gets 409)
3. CLI/API behavior parity (same service method) — PASS
4. Structured `error_code` catalog — PASS
5. Idempotent 5-min guard always active — PASS

**VERIFY-1 (no CLI behavior dropped):** PASS — guard window / --force / --sync / --rule-key semantics + pattern_type mismatch message all preserved.
**VERIFY-2 (URL namespace collision):** PASS — 3 signal-dispatches routes, all expected.

**Zoom-out (Z1-Z4):**
- Z1 (manual+auto daily-cap surprises): AGREE non-blocking
- Z2 (cost/rate-limiting story): AGREE non-blocking
- **Z3 (AllowAny on POST mutation): AGREE F-BLOCKING** → fixed same-PR (commit `d53054ff8`, changed to `IsAuthenticated`)
- Z4 (queue backlog / CSRF / UX feedback): AGREE non-blocking

## Chris D0

"Ratify, merge it" — after plain-English summary of the ship + Rigby SIGN outcomes.

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

1. **Recycled** — `make celery-recycle` (workers matched HEAD `5fb5db1a4`) + `make stop && make start` (daphne restart for new URL routes).
2. **Frontend rebuilt** — `npm run build` produced new bundle (`sha=5fb5db1a4` in `__manifest.json`). Chris hard-refreshed browser to pick up the new JS.
3. **Live-verified end-to-end** against active cluster `0cd4f30d-f8a2-4ca1-81d0-945e44442b9d` (Opus, Claude opportunity window; pattern=opportunity_window; strength=0.66; confidence=1.00):
   - RESOLVE returned 1 matching rule: `opportunity_window__opportunity_scoring` → OpportunityScoringAgent
   - `create_manual_dispatch` executed successfully — dispatch `8d548726-4ca3-48ff-812e-4e2e980533ac` ran on long_running worker in ~20s, outcome='succeeded', error=''
   - Guard correctly blocked immediate re-fire on same cluster+rule (returned `guard_blocked` with `existing_dispatch_id=8d548726`)
   - CLI `--force` bypass path still works (test row `70d17361-b9c7-4460-8546-0a4f0d1c4644` cleaned up to `failed` to avoid extra LLM cost)
4. **Manual dispatch count:** 1 → 2 (delta +1, matches expectation).

## Rigby Tool Gap Ledger

No new formal entries. Known deliverable-tool diagnostic-flag bug re-hit twice (both mirrors) and re-worked-around via ORM as expected.

## Governance-worthy pattern candidate (first trigger only)

Rigby's zoom-out surfaced: **"Any endpoint that can trigger spend (LLM fan-out / Celery dispatch) must tighten mutation permissions in the same PR; `AllowAny` is never acceptable on spend mutations."** S2947 A8 is trigger #1 (fixed same-PR at Z3). Watch for corroboration in another PR before proposing a playbook amendment.

## Deferred queue additions from S2947

- **A8 zoom-out Z1** — UI hint about manual+auto shared daily-cap consumption (informative). Only ship if operators hit surprising cap blocks.
- **A8 zoom-out Z2** — Cost estimate / rate-limiting story for the modal. Deferred to when spend from manual dispatches becomes non-trivial.
- **A8 zoom-out Z4** — Queue backlog handling / CSRF surface polish / "queued" success toast. Reactive.

## Reference

- **S2947 shipped code:**
  - `core/services/signal_dispatch_service.py:308-434` — `create_manual_dispatch` method
  - `core/views_signal_dispatch.py:88-193` — POST + resolve views
  - `frontend/src/pages/workspace/tabs/SignalDispatchesTab.tsx:117-322` — ManualDispatchModal
- **S2946 upstream:** `docs/handoffs/SESSION_2946_A6_DIVERSITY_DENOMINATOR.md` — the /3 lift this button surfaces
- **S2934 A4 precedent:** `docs/handoffs/` — original observability tab that this augments
