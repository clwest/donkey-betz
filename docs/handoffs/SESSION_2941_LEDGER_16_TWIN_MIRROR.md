# Session 2941 — Ledger #16 Twin-Mirror Enforcement (substrate ship)

**Date:** 2026-07-24
**Branch merged:** `s2941-ledger-16-twin-mirror-enforcement` → `main` via PR #3517 at SHA `c250b49b6`
**Wrapper pin (S2941):** `pa-8404da67fc524073` — bumped to next pin at close cascade
**Session ratification:** Chris D-verdict RATIFIED at T0 ("Ship it.") + T1 via admin-merge. Rigby T0 SIGN AGREE (HYBRID + service-extraction) + T1 SIGN AGREE with 1 F-BLOCKING resolved before commit.

**Twin mirrors (dogfooding — first live-in-force use of the new gate):**
- **Content mirror:** `0fbbe1aa-44f5-425c-8788-936971cfbf41` (Architecture & Research workspace, category `initiative_phase_doc`)
- **Ratification envelope:** `be7265d9-6e44-4d75-a268-e81ff15a927e` (Architecture & Research workspace, `deliverable_type='ratification_record'`)

---

## What shipped

**PR #3517** (merge SHA `c250b49b6`) — extends `session_lifecycle close` with a pre-transaction twin-mirror enforcement gate. Refuses to proceed unless the operator provides BOTH `--content-mirror-id` + `--ratification-envelope-id` (verified against the DB) OR passes `--allow-no-mirror` (logged for audit). Skipped for `--retire-only` (recovery path, not ratification).

### Files

- **NEW** `core/services/twin_mirror_enforcement.py` (~180 LOC) — public API `assert_twin_mirror_at_close(content_mirror_id, ratification_envelope_id, allow_no_mirror) -> MirrorVerificationResult`. Isolates all deliverable-type semantics from the CLI so `session_lifecycle` stays deliverable-agnostic per Rigby T0 zoom-out.
- **MODIFIED** `core/management/commands/session_lifecycle.py`:
  - Added 3 CLI flags to close subparser (`--content-mirror-id`, `--ratification-envelope-id`, `--allow-no-mirror`).
  - Extended `_handle_close` signature (3 keyword-only args, default None/False — backward-compat).
  - Enforcement call runs **pre-`transaction.atomic()`** so refuse → clean rollback (no `_retire_pin`, no `_create_fresh_conversation`, no wrapper rewrite).
  - Post-close stdout audit line: `[TWIN-MIRROR VERIFIED]` (with IDs + titles) or `[TWIN-MIRROR ALLOW_NO_MIRROR]` for shell-history grep.
- **NEW** `core/tests/test_session_lifecycle_twin_mirror.py` (~420 lines) — 20 tests total:
  - 15 direct-service tests (`TwinMirrorServiceTests`).
  - 7 CLI-integration tests (`SessionLifecycleCloseIntegrationTests`) — refuse-path integration tests assert wrapper file untouched + prior pin still `session_active=True` (clean rollback proof).
- **MODIFIED** `core/tests/test_session_lifecycle_command.py` — 2 pre-existing close-path tests updated to pass `--allow-no-mirror` (they exercise retire/mint/rewrite behavior, not twin-mirror behavior).

### Failure modes gated

- Both flags missing → refuse with actionable multi-line message.
- Only one ID → refuse (names the missing flag).
- Mutex violation (both IDs + `--allow-no-mirror`) → refuse.
- Malformed UUID on either side → refuse.
- Row missing in Deliverable table → refuse.
- Either row `diagnostic_status='diagnostic'` → refuse.
- Envelope row with `deliverable_type != 'ratification_record'` → refuse.
- Same UUID for both IDs (Rigby T1 F-BLOCKING) → refuse.

---

## Live-verification (post-merge, per PLAYBOOK-7.4.4 + local-truth rule)

Post-merge `make recycle-all` clean at `sha=c250b49b62a3` (`surviving=none`).

Then two direct CLI invocations against the real wrapper:

1. `python manage.py session_lifecycle close --dry-run --allow-no-mirror --label smoke-s2941` → clean dry-run output (`no DB or wrapper writes will be performed`).
2. `python manage.py session_lifecycle close --dry-run --label smoke-s2941-refuse` → correct `CommandError`:
   ```
   Ledger #16: close requires twin-mirror verification.
     Provide BOTH --content-mirror-id <UUID> AND --ratification-envelope-id <UUID>
     OR pass --allow-no-mirror to skip (logged for audit).
     See docs/PA_TOOL_AUDIT.md and `feedback_twin_deliverable_at_every_ratification`
     for the twin-mirror contract.
   ```

The S2941 close cascade itself is the third live-verification — the first time the new gate refuses/allows in force on a real close ceremony (this handoff's own ceremony passes `--content-mirror-id 0fbbe1aa-… --ratification-envelope-id be7265d9-…`).

---

## SIGN + D-verdict trail

### T0 SIGN (Rigby)

Tool-grounded: `repo_tool.read_file` on `session_lifecycle.py` line 520–720. Substantive 4/4 answers:

- **Ask 1 (F-BLOCKING) — A / B / hybrid:** RECOMMEND HYBRID with narrow trigger (refuse only when label matches ratification-signal pattern). Justified by S2937/S2938/S2939 skip mechanism = ceremony sequencing under time pressure, not technical inability.
- **Ask 2 (F-BLOCKING) — scope:** `_handle_close` only. Do NOT extend `_handle_open` — different failure surface, higher blast radius.
- **Ask 3 (non-blocking) — tests:** SHIP the regression test (refuse/allow/escape paths + mocking spies over mutation methods).
- **Ask 4 (ZOOM-OUT) — coupling risk:** Extract to `core/services/twin_mirror_enforcement.py` service; keep `session_lifecycle` deliverable-agnostic. Prevents semantic sprawl across the management command.

### T0 D-verdict (Chris)

**RATIFY** — "Ship it."

### T1 SIGN (Rigby, post-implementation review)

Tool-grounded: 4 `repo_tool.read_file` calls covering service, session_lifecycle changes, and test file. AGREE 4/4 with 1 F-BLOCKING + 2 non-blocking:

- **F-BLOCKING (Ask 1a):** Same UUID for both IDs currently escapes verification (only checked row exists + `deliverable_type='ratification_record'` — if passed same envelope row twice, "verified" passes). Ledger #16 semantically requires TWO DISTINCT artifacts. **RESOLVED before commit** — added same-ID check + regression test `test_refuses_when_both_ids_are_the_same`.
- **Non-blocking (Ask 3):** CLI plumbing test for mutex path. **ADDED** — `test_close_refuses_when_mutex_violated_via_cli`.
- **Non-blocking (Ask 4 ZOOM-OUT):** Shipped shape is effectively "pure-A for all non-retire-only closes," not the label-heuristic hybrid described at T0. Intentional — silent-skip failure mode requires explicit choice at every close is the minimum viable fix — but merits observation. Operator-habituation risk: if `--allow-no-mirror` becomes routine, gate degrades. Recorded as **fold-candidate for potential Ledger #16b** (trigger: 3+ closes routinely using `--allow-no-mirror` without cascade-only justification).

### T1 D-verdict (Chris)

**RATIFY** via admin-merge as PR #3517 at `c250b49b6`.

---

## Test coverage summary

35 tests pass end-to-end via `python manage.py test core.tests.test_session_lifecycle_command core.tests.test_session_lifecycle_twin_mirror --keepdb`:

- **15 direct-service tests** (`TwinMirrorServiceTests`): each failure-mode + verified path.
- **7 CLI-integration tests** (`SessionLifecycleCloseIntegrationTests`): refuse-no-flags / allow-no-mirror / verified / wrong-envelope-type / mutex / retire-only-bypass.
- **13 pre-existing tests** (`test_session_lifecycle_command.py`): all still pass (2 updated to add `--allow-no-mirror`).

---

## Governance

None this session. D6 moratorium unchanged. No Playbook amendments proposed. Zoom-out fold-candidate (pure-A drift observation) recorded here in §T1-SIGN — not promoted to Playbook amendment yet (single trigger; watch for corroboration).

## Rigby Tool Gap Ledger

No new formal entries. No candidates surfaced this session.

## Ledger #16 status

**Substrate: LIVE-IN-FORCE at `c250b49b6`.** The 3-trigger corroboration (S2937 + S2938 + S2939) that opened Ledger #16 is now discharged by the enforcement gate. Retroactive backfill for S2937/S2938/S2939 was already executed at S2939 close (6 mirrors via ORM per `scripts/backfill_s2818_s2824_workspace_mirrors.py` pattern).

---

## Follow-up (S2942 open sequence)

See `00-START-NEXT-SESSION.md` for full priorities. Suggested first-action candidates (all deferred from S2940 queue — Ledger #16 close does not open new engineering work):

- **(A8)** Signal Dispatches "Manual dispatch" button (Rigby S2934 zoom-out fold — ~30 min UI).
- **(A9)** Fourth signal-dispatch rule — `demand_spike` (250 clusters) or `skill_demand` (131 clusters).
- **(A6)** SignalCluster promotion audit — only 0.58% of clusters active.
- **(F)** Dry-run substrate design (Ledger #38) — enables live mutation verification of Slice 7 batch 2a/2b mutations retroactively.
- **(H)** Ledger #41 candidate — teach gap-map classifier to distinguish live-verified vs analyzed-only actions.
- **(D)** Docs restructuring arc — unblocked at S2800, still queued.
