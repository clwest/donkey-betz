# SESSION 2948 — NEW-4 Cluster Picker (Shape B) + Postbuild Template Sync

**Date:** 2026-07-24
**Status:** CLOSED — PR #3536 merged, workers recycled
**HEAD at close:** `<filled at close cascade>`
**Merge commit:** squash of `feat/s2948-cluster-picker`
**Twin mirrors:**
- Content: `2bfac487-5869-4f26-90d0-8146a0ce0cf3` (Architecture & Research, category `initiative_phase_doc`)
- Ratification: `242deb77-e58c-41ce-a19f-765fb9d41ad0` (Architecture & Research, `deliverable_type='ratification_record'`, category `governance`)
- Both diagnostic-flag-cleared via ORM per known bug.

---

## What shipped

**S2948 NEW-4 (Shape B upgrade)** — replaces the paste-UUID input in the `ManualDispatchModal` (S2947 A8) with a searchable two-column cluster picker. Chris hit the exact ergonomic gap Shape C left ("I don't have a UUID to search for…") within **minutes** of the S2947 A8 ship — S2948 closes that gap by removing the need to know cluster UUIDs at all.

**Chris pre-ratified the ship** ("if you have the context and everything ship it now"), so no pre-merge Rigby SIGN cycle — post-merge verification with Rigby tool_runs evidence instead. Rigby read `views_signal_dispatch.py:88-193` + `generate-manifest.mjs` to verify the endpoint filters + template sync logic before the twin mirrors were created.

**Bonus fix bundled:** postbuild template auto-sync (removes the manual step surfaced in the S2947 close cascade).

## Files shipped

- **NEW** `signal_dispatches_eligible` view in `core/views_signal_dispatch.py` (+118) — GET `/api/v1/agents/signal-dispatches/eligible/` endpoint. Filters active + strength≥0.5 + confidence≥0.5 clusters, only surfaces those with matching rules, default-hides guard-blocked-only clusters.
- **MODIFIED** `core/urls.py` (+2) — new route registered.
- **NEW** 7 regression tests in `core/tests/test_s2934_signal_dispatch_harness.py` (+79) — `TestSignalDispatchesEligibleEndpoint` covers filter semantics, sort order, pattern_type filter, matching_rules population, guard-block default-hidden + include_blocked flag surface, limit cap.
- **REWRITE** `ManualDispatchModal` in `frontend/src/pages/workspace/tabs/SignalDispatchesTab.tsx` (~130 net delta) — two-column layout (`max-w-2xl`), searchable cluster list (left) + selected preview + rule + submit (right). Rule auto-selects when exactly one match. Refresh button in header (30s staleTime on the eligible query).
- **MODIFIED** `frontend/src/lib/api.ts` (+3) — `agentsApi.signalDispatchesEligible(params)`.
- **MODIFIED** `frontend/scripts/generate-manifest.mjs` (+38) — postbuild step that auto-syncs `core/templates/index.html` bundle hashes from `dist/index.html`. Non-fatal: warns and skips on regex miss, doesn't break the build.
- **MODIFIED** `core/templates/index.html` — first auto-synced write.

## Test evidence

- **32/32 signal-dispatch tests pass** (25 pre-existing S2934+S2947 A8 + 7 new S2948 NEW-4).
- `npm run build` produced fresh bundle (`index-DkcB0JTx.js` + `index-Ct_coWOI.css`) and auto-synced the template — verified by the `[generate-manifest] Synced …` log line.
- Backend + daphne bounced post-merge to load new URL route + template.

## Post-merge SIGN (Rigby, tool_runs evidence)

Rigby used `repo_tool.read_file` (non-rubber-stamp per `feedback_verify_rigby_tool_runs_before_trusting_sign`):
- Read `core/views_signal_dispatch.py:88-193` — verified endpoint filters + guard-block default-hidden semantics
- Read `frontend/scripts/generate-manifest.mjs` — verified sync happens after manifest write, non-fatal wrapper

**Design invariants (implicit — pre-ratified ship):**
1. Cluster picker replaces paste input, no paste fallback in v1 (Shape B commitment) — PASS
2. Guard-blocked clusters auto-hidden from default picker view — PASS
3. Rule auto-select preserved from S2947 A8 behavior — PASS
4. Postbuild sync non-fatal (build never blocked by sync failure) — PASS
5. No API surface changes beyond `/eligible/` (POST + resolve unchanged) — PASS

## Chris pre-ratification

"If you have the context and everything ship it now, if it's easier for me to start a new terminal we can do that" — verbatim invitation to ship in this session. Ratification is implicit in the "ship it now" directive.

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

1. **Recycled** — `make celery-recycle` (workers matched HEAD after S2948 merge).
2. **Daphne bounced** — `make stop && make start` to pick up new URL route.
3. **Frontend rebuilt** — `npm run build` auto-synced template (`[generate-manifest] Synced …`).
4. **Live-verify pending Chris's first click** — post-merge Chris will open the modal, verify:
   - Cluster list populates with the 7 eligible clusters observed at S2948 open
   - Filter typing narrows the list
   - Clicking a cluster shows preview + auto-selected rule
   - Dispatch button submits and new row appears in the tab

## Governance-worthy pattern candidate (Rigby zoom-out on Shape C → Shape B loop speed)

Rigby's zoom-out on the "Chris hit the paste-UUID gap within minutes of S2947 A8 ship" observation — is there a governance lesson around _"when Shape MVP will inevitably surface an ergonomic gap on first-use, ship the ergonomic upgrade in the same session"_?

**Analysis:** the S2947 A8 → S2948 NEW-4 loop took ~30 min from "I don't have a UUID" to "shipped, merged, recycled." That's a good outcome, but it also validates that Shape C was under-scoped — the paste-UUID input was a debug tool in operator clothing. **Pattern candidate:** when Rigby flags an ergonomic concern in SIGN (Z2 zoom-out at S2947 was "cost/rate-limiting" but Z-nothing was "operator won't have UUIDs handy"), Claude should probe: "will the operator need to look this up elsewhere before using this?" If yes, that's a Shape B requirement, not a follow-up.

**Trigger status:** #1 (S2947→S2948 loop). Watch for corroboration on a second Shape MVP → same-session ergonomic upgrade before proposing a playbook rule.

## Rigby Tool Gap Ledger

No new formal entries. Known `deliverable_tool.create` diagnostic-flag bug re-hit twice (both S2948 mirrors) and re-worked-around via ORM as expected.

## Deferred queue additions from S2948

_(None — S2948 closed one deferred item cleanly.)_

## Reference

- **S2948 shipped code:**
  - `core/views_signal_dispatch.py:141-238` — `signal_dispatches_eligible` view
  - `frontend/src/pages/workspace/tabs/SignalDispatchesTab.tsx:117-317` — ManualDispatchModal v2 (2-column picker)
  - `frontend/scripts/generate-manifest.mjs:104-139` — postbuild template auto-sync
- **S2947 upstream:** `docs/handoffs/SESSION_2947_A8_MANUAL_DISPATCH_BUTTON.md` — the Shape C paste-UUID modal this replaces
- **PR #3535** — manual template-hash fix from S2947 close (superseded by S2948 auto-sync)
