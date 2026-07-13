---
session: 2776
date: 2026-07-13
title: "PA wrapper token/pin ownership verification ratified"
status: complete
outcome: shipped
scope: net-new-engineering-N21-non-ops-surface
canonical_authority: repo_canonical
ratification_envelope: docs/research/implementation/RATIFICATION_2026-07-13_pa_wrapper_ownership_check.md
---

# Session 2776 — PA wrapper token/pin ownership verification ratified

## §1. TL;DR

Chris selected N21 (`pa_local.sh` wrapper token/pin ownership check) as the second arc of the calendar day after S2775 shipped clean. Second consecutive non-ops-surface session; ops-surface pause discipline still held.

Shipped: (a) new `core/views_pa_whoami.py` (54-line bounded 3-field GET view with sharp 5-point test docstring); (b) `core/urls.py` grouped import + `/api/pa/whoami/` route entry; (c) new `core/management/commands/verify_pa_wrapper_ownership.py` (190-line single-concern command with 0/2/3/4 exit contract); (d) `tools/pa_local.sh` ~20-line bash prelude with `PA_LOCAL_ALLOW_MISMATCH=1` escape hatch; (e) 9-test suite locking view + command contracts.

9/9 N21 unit PASS in 0.38s. Full 4-suite stack (S2772 + S2773 + S2775 + S2776) 56/56 PASS in 1.19s. Live E2E: cold cache → prelude ran verify → cache written · warm cache → silent skip. Rigby capstone 7/7 PASS at 14-90ms across `/api/ops/*` + `/api/pa/whoami/`.

**FIRST F-BLOCKING DISAGREE in the S2771-rule streak.** Rigby pushed back on Claude's Q1 lean (extend `session_lifecycle status`) with substrate-simplicity argument — dedicated command instead. Chris explicitly aligned: "I also agree with Rigby on trying to prevent swiss army knife effects." Validates the S2771 rule genuinely surfaces substantive folds. Six consecutive applications of the rule; classification pattern now has three-in-a-row explicit categorization.

Also this session: **N15 mechanism-now/value-later shipped first natural payoff.** `session_lifecycle open` at S2776 mint dropped the first automatic row to `logs/session_freshness.jsonl` (FRESH · head aa3dccc509b6 · 5/5 celery fresh). Trend surface is live.

## §2. Timeline

- **22:33** S2776 open — first-natural N15 hook fire fired at pin mint: `freshness: FRESH · head=aa3dccc509b6 · celery_stale=0/5`. Wrapper repointed to `pa-bc40ba1f5dd343f4`. Same session flow as S2775 close (no new open ceremony — continuous session per Chris's "ship s2775 then start n21" directive).
- **22:35** Routed N21 draft design to Rigby: 3 F-BLOCKING + 1 NON-BLOCKING + open-ended zoom-out with explicit classification ask.
- **22:40** Rigby response: DISAGREED with Claude Q1 (dedicated command, not session_lifecycle extension); AGREED Q2 with fold (dedicated `/api/pa/whoami/` + sharp 5-point test); MOSTLY AGREED Q3 with fold (`verified_user_id` in cache contents); AGREED Q4 (silent v1); zoom-out with 1 same-PR-actionable + 2 same-PR-mitigatable + 1 future-trigger.
- **22:45** Presented joint recommendation to Chris. D-verdict: "Yes on the shape. I also agree with Rigby on trying to prevent swiss army knife effects." — first explicit Chris alignment with a Rigby F-BLOCKING disagreement.
- **22:50** Wrote `core/views_pa_whoami.py` + inserted URL entry + import. Wrote `core/management/commands/verify_pa_wrapper_ownership.py`.
- **22:55** Wrote `tools/pa_local.sh` bash prelude (per-pin cache gate + escape hatch). Wrote `core/tests/test_pa_wrapper_ownership_2776.py` (9 tests).
- **23:00** First test run failed with UUID/JSON serialization errors — user PK is UUID; view was returning raw UUID; command was comparing UUID to string. Fixed: normalize both sides to `str()` at boundaries. 9/9 PASS in 0.38s.
- **23:07** Full 4-suite regression: 56/56 in 1.19s.
- **23:10** `make recycle-all` to load N21 URL locally. Cold-cache live E2E: `[pa_local] ✓ token=chris · pin=pa-bc40ba1f5dd343f4 · pin_owner=chris` + cache file written. Warm-cache: silent skip.
- **23:15** Rigby capstone: 7/7 PASS on all 6 `/api/ops/*` + `/api/pa/whoami/`. `ops_tool.version` FRESH · head aa3dccc509b6 · post-recycle state.
- **23:20** Wrote ratification envelope + this handoff. Docs cascade + PR bundle next.

## §3. Empirical Evidence

### N21 unit tests

```
$ python manage.py test core.tests.test_pa_wrapper_ownership_2776 --noinput
Ran 9 tests in 0.380s
OK
```

Tests:
- `PaWhoamiViewTests`: bounded 3-field payload (3), rejects unauthenticated, GET-only
- `VerifyPaWrapperOwnershipCommandTests`: success writes cache, mismatch=exit 2, missing token=exit 3, whoami rejection=exit 3, orphan pin=exit 4, --json flag emits success payload

### Full 4-suite regression

```
$ python manage.py test test_ops_auth_regression_2772 \
    test_ops_query_param_allowlist_2773 test_session_freshness_2775 \
    test_pa_wrapper_ownership_2776 --noinput
Ran 56 tests in 1.190s
OK
```

### Live E2E (cold cache → verify → cache)

```
$ rm -rf ~/.claude-pa-verified
$ bash tools/pa_local.sh "N21 live E2E check — say ok"
[pa_local] ✓ token=chris · pin=pa-bc40ba1f5dd343f4 · pin_owner=chris
ok

$ cat ~/.claude-pa-verified/pa-bc40ba1f5dd343f4.json
{"pin": "pa-bc40ba1f5dd343f4",
 "verified_user_id": "e0c9d44b-a876-4b30-b0da-e4d0b10006f6",
 "verified_username": "chris",
 "verified_at": "2026-07-13T23:11:39.103966+00:00"}
```

### Live E2E (warm cache → silent skip)

```
$ bash tools/pa_local.sh "second call"
# no [pa_local] line
```

### Rigby capstone

```json
{"ok": true, "suite": "custom", "passed": 7, "failed": 0, "total": 7}
```

All 6 `/api/ops/*` endpoints + `/api/pa/whoami/` at 14-90ms latencies.

### First natural N15 row

`session_lifecycle open` at S2776 mint fired the N15 hook automatically:

```
[SESSION_LIFECYCLE] open complete:
  ...
  freshness: FRESH · head=aa3dccc509b6 · celery_stale=0/5
```

Row landed in `logs/session_freshness.jsonl` — first mechanism-now/value-later payoff for N15.

## §4. Key Decisions

- **Dedicated command over `session_lifecycle` extension** — Rigby DISAGREED with Claude's original lean. Substrate-simplicity: identity/auth axis is different from pin+wrapper+freshness. Refactor trigger codified in docstring.
- **`/api/pa/whoami/` with sharp 5-point test** — Read-only · Deterministic · No side effects · Bounded output schema · Directly needed for toolchain correctness. Codified in module docstring to prevent `/api/pa/*` becoming a second ops-surface.
- **Per-pin file cache** — auto-invalidates on rotation. `verified_user_id` recorded in contents for N21 v2 wrapper-side compare.
- **Fail-loud default with escape hatch** — `PA_LOCAL_ALLOW_MISMATCH=1` env var → warn-and-continue. Preserves recovery-time objective while giving emergency unblock.
- **UUID normalization at boundaries** — user PK is UUID; view + command normalize to str at wire boundary. Works for both UUID and int PK conventions.

## §5. Rigby SIGN summary

**Streak now 6 consecutive (S2771 rule):**

| # | F-BLOCKING | Non-blocking | Zoom-out | Disagreements |
|---|---|---|---|---|
| S2771 | 2 folds | — | 3 concerns | 0 |
| S2772 | 3 folds | 1 | 7 concerns | 0 |
| S2773 | 4 folds | 0 | 5 concerns | 0 |
| S2774 | 2 folds | 0 | 4 concerns → 4 same-PR-actionable | 0 |
| S2775 | 3 folds | 0 | 4 concerns → 4 same-PR-mitigatable | 0 |
| **S2776** | **3 folds (1 DISAGREE)** | **1** | **4 concerns → 1+2+1 mixed** | **1** |

**Emerging classification** now has THREE triggers of `same-PR-actionable` (S2774 all-4 + S2776 concern a — refactor trigger for `session_lifecycle`), THREE triggers of `same-PR-mitigatable` (S2775 all-4 + S2776 concerns c and d — escape hatch + 5-point test), and TWO triggers of `future-trigger` (S2772/S2773 forward-carries prefigure it, S2776 concern b — Python entrypoint alternative). Two-triggers threshold under PLAYBOOK-6.10 satisfied for two of three classes independently.

## §6. Forward carry

- **Ops-surface pause discipline still held** — N21 non-ops-surface; ops streak break was on surface type only.
- **N21 v2 candidates** (all deferred): wrapper-side user_id compare against cache · TTL on cache · `logs/wrapper_ownership.jsonl` trend log.
- **`session_lifecycle` refactor trigger:** codified in command docstring — third flag hitting API or wrapper cache → split into `session_lifecycle` + `toolchain_doctor`.
- **`/api/pa/*` future-endpoint audit trigger** — every proposal must satisfy the sharp 5-point test.
- **Zoom-out classification codification candidate** — three triggers now for two classes independently; Playbook v0.7.0 MINOR or v0.6.1 PATCH candidate. Queued for memory-rule promotion audit.
- **N15 v2 candidates** (from S2775) — unchanged; still deferred pending trend row accumulation.

## §7. Files changed

- `core/views_pa_whoami.py` (NEW, +54 lines)
- `core/urls.py` (amended, +import + path entry with comment)
- `core/management/commands/verify_pa_wrapper_ownership.py` (NEW, +190 lines)
- `tools/pa_local.sh` (amended, +20-line bash prelude + wrapper pin rotation to S2776)
- `core/tests/test_pa_wrapper_ownership_2776.py` (NEW, 9 tests)
- `docs/research/implementation/RATIFICATION_2026-07-13_pa_wrapper_ownership_check.md` (NEW envelope)
- `docs/handoffs/SESSION_2776_PA_WRAPPER_OWNERSHIP_CHECK_RATIFIED.md` (NEW, this handoff)
- `00-START-NEXT-SESSION.md` (rewritten for S2777 open)
- `CLAUDE.md` L3 anchor (refreshed to S2776)

## §8. Post-merge checklist

- [ ] `make recycle-all` per PLAYBOOK-7.4.4 (eleventh close-cycle — first double-cycle same calendar day)
- [ ] Docs cascade (4-step + provenance)
- [ ] Verify second natural N15 row lands at S2777 open (streak of natural rows)
- [ ] Retire S2776 pin (`session_tool.retire ... force=true`) — seventh consecutive
- [ ] `~/.claude-pa-verified/pa-bc40ba1f5dd343f4.json` will be orphaned by pin rotation; harmless — new pin at S2777 mints new cache entry
