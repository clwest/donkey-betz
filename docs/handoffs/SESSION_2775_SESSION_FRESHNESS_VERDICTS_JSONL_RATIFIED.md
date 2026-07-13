---
session: 2775
date: 2026-07-13
title: "Session-open freshness verdicts persisted to JSONL ratified"
status: complete
outcome: shipped
scope: net-new-engineering-N15-non-ops-surface
canonical_authority: repo_canonical
ratification_envelope: docs/research/implementation/RATIFICATION_2026-07-13_session_freshness_verdicts_jsonl.md
---

# Session 2775 — Session-open freshness verdicts JSONL ratified

## §1. TL;DR

Chris selected N15 (session-open freshness verdicts persisted to JSONL) from the S2775 candidate menu — the meta-observability substrate for PLAYBOOK-7.4.4 trend detection. First non-ops-surface arc since the ops-console streak (S2770→S2774). Ninth close-cycle post-PLAYBOOK-7.4.4-codification.

Shipped: (a) new `core/services/process_freshness.py` (176 lines) — module-level `compute_process_staleness()` extracted from `OpsHandler._compute_process_staleness` with byte-identical return shape; (b) `OpsHandler._compute_process_staleness` reduced to 8-line delegating wrapper; (c) `session_lifecycle.py` amended with `history` subcommand + private `_record_session_freshness` fail-soft helper + hook call in `_handle_open` post-success; (d) 10-test suite (`core/tests/test_session_freshness_2775.py`) — 3 extraction-shape + 4 recorder + 3 history reader; 10/10 PASS in 0.157s.

47/47 tests PASS across S2772+S2773+N15 suite in 0.829s. Rigby capstone `http_smoke_test` 6/6 PASS on `/api/ops/*` (5-172ms latencies) — extraction transparent to `ops_tool.version`.

Rigby SIGN (S2771 rule FIFTH consecutive application) surfaced 4 substantive concerns; ALL 4 folded into design-time mitigations rather than same-PR verification action or forward-carry. Novel classification pattern this session: zoom-out concerns can be `same-PR-actionable`, `same-PR-mitigatable`, or `future-trigger` — S2775 is the first `same-PR-mitigatable` exemplar.

**Non-ops-surface confirmed** — no new `/api/ops/*` endpoint, no new PA tool action, no new view. S2774 ops-surface pause discipline honored on session type, not just surface count.

## §2. Timeline

- **21:20** Session opened cold via `context-kit orient` + `00-START-NEXT-SESSION.md`. Verified HEAD `b31393258` matches S2774 close, pg15 owns port 5432 under brew launchd. Wrapper still points at retired S2774 pin — intentional fresh-mint gate.
- **21:25** Presented S2775 candidate menu to Chris (net-new engineering: N15/N17/N21; ops-surface pause active). Chris selected N15, deferring N21 to post-context-check.
- **21:35** Minted fresh pin `pa-77bdf04032204741` scoped to N15 label. Wrapper repointed. Rigby freshness dispatch verified FRESH · SHA `b3139325831a`. S2772+S2773 regression suite 37/37 PASS in 0.657s.
- **21:45** Read S2774 envelope §4 (Rigby SIGN summary) + §7 (forward-carry with pause discipline). Read `session_lifecycle.py` + `td_handlers_ops.py::_compute_process_staleness` to plan extraction.
- **21:52** Routed N15 draft design to Rigby: 3 F-BLOCKING + 1 NON-BLOCKING + open-ended zoom-out. Rigby returned aligned on all F-BLOCKING with one row-shape fold (add `head_commit_age_seconds`) + 4 zoom-out mitigations.
- **21:58** Presented joint recommendation to Chris. Chris D-verdict: "yes go ahead."
- **22:05** Wrote `core/services/process_freshness.py`. Refactored `OpsHandler._compute_process_staleness` to delegating wrapper.
- **22:10** Amended `session_lifecycle.py`: added `FRESHNESS_LOG_PATH` constant, `history` subparser + `_handle_history`, private `_record_session_freshness` helper, hook call in `_handle_open` post-commit success.
- **22:12** Wrote `core/tests/test_session_freshness_2775.py` (10 tests). N15 suite 10/10 PASS in 0.157s. Full ops stack (S2772+S2773+N15) 47/47 PASS in 0.829s.
- **22:17** Live E2E via management shell: `_record_session_freshness` write path executed against real process table, wrote first real row to `logs/session_freshness.jsonl` — verdict FRESH · head `b3139325831a` · 5/5 celery fresh. `session_lifecycle history` reads it back.
- **22:20** Rigby capstone `http_smoke_test` 6/6 PASS on `/api/ops/*` — extraction transparent.
- **22:25** Wrote ratification envelope + this handoff. CLAUDE.md L3 refresh pending. Docs cascade + PR bundle next.

## §3. Empirical Evidence

### N15 unit tests

```
$ python manage.py test core.tests.test_session_freshness_2775 --noinput -v 2
System check identified no issues (0 silenced).
test_ok_verdict_carries_head_metadata ... ok
test_ops_handler_wrapper_delegates_to_extracted_function ... ok
test_returns_verdict_key ... ok
test_limit_shows_only_most_recent ... ok
test_missing_log_prints_graceful_message ... ok
test_reads_back_rows ... ok
test_appends_multiple_rows ... ok
test_counts_stale_celery_workers ... ok
test_fail_soft_on_compute_exception ... ok
test_writes_row_with_expected_fields ... ok
----------------------------------------------------------------------
Ran 10 tests in 0.157s
OK
```

### Full ops regression stack (S2772+S2773+N15)

```
$ python manage.py test core.tests.test_ops_auth_regression_2772 core.tests.test_ops_query_param_allowlist_2773 core.tests.test_session_freshness_2775 --noinput
Ran 47 tests in 0.829s
OK
```

### Live freshness capture (real compute against real process table)

```json
{
  "ts": "2026-07-13T22:17:47.013096+00:00",
  "session_label": "s2775-n15-e2e-verify",
  "pin": "pa-77bdf04032204741",
  "context": "session_open",
  "verdict": "FRESH",
  "head_sha_short": "b3139325831a",
  "head_commit_age_seconds": 1968,
  "daphne_pid_age_seconds": 1952,
  "celery_worker_count": 5,
  "celery_stale_count": 0
}
```

### Rigby capstone

```json
{"ok": true, "suite": "custom", "environment": "local",
 "passed": 6, "failed": 0, "skipped": 0, "total": 6}
```

All 6 `/api/ops/*` endpoints returning HTTP 200 at 5-172ms. `ops_tool.version` returns unchanged shape (staleness_verdict=FRESH, head_commit_sha=b3139325831a7c51067ce56eecc4925915d9fd5a, celery_workers_status list, daphne_pid/pid_age fields all present).

## §4. Key Decisions

- **Hook point:** `session_lifecycle open` post-success — the deterministic "session opened" event. Not `pa_local.sh` dispatch (noisier, not the semantic event). Rigby Q1 F-BLOCKING YES agree.
- **Row shape:** lean (~200 bytes) with `head_commit_age_seconds` added at Rigby's Q2 fold. Trend analysis can bin verdicts by time-since-deploy. Rejected `staleness_fix` hint + `daphne_started_before_head_commit` as redundant.
- **Extraction pattern:** module-level function, not instance-method call. `OpsHandler._compute_process_staleness` becomes 8-line wrapper. Zero coupling of `session_lifecycle` to tool dispatcher lifecycle.
- **Close-time capture:** deferred to v2. Would require decision about which close-ceremony step to fire at (pre-retire? post-mint?). Rigby Q4 agree defer.
- **Storage:** `logs/session_freshness.jsonl` (gitignored). No schema versioning yet — add on first v2 field.

## §5. Rigby SIGN summary

**Streak now 5 consecutive (S2771 rule):**

| # | F-BLOCKING | Non-blocking | Zoom-out |
|---|---|---|---|
| S2771 | 2 folds | — | 3 concerns → 2 same-PR + 1 forward-carry |
| S2772 | 3 folds | 1 | 7 concerns → 2 same-PR + 4 forward-carry |
| S2773 | 4 folds | 0 | 5 concerns → 3 same-PR + 2 forward-carry |
| S2774 | 2 folds | 0 | 4 concerns → 4 same-PR (incl. capstone verification) |
| **S2775** | **3 folds** | **0** | **4 concerns → 4 same-PR (all design-time mitigations)** |

**Emerging classification** (proposed after S2775): zoom-out concerns fall into three response categories:
1. `same-PR-actionable` — new verification action folded into same PR (S2774 precedent: capstone smoke test)
2. `same-PR-mitigatable` — design-time changes fold in (S2775 precedent: private helper, commit language, atomic append)
3. `future-trigger` — forward-carry with explicit trigger criteria (S2772/S2773 precedent)

**Two triggers, one class each so far.** Two-triggers threshold per PLAYBOOK-6.10 not yet met on the classification itself; queue for third occurrence before proposing codification.

## §6. Forward carry

Ops-surface pause discipline still held. N15 broke a "type of surface" streak (5 ops-console iterations → 1 substrate/telemetry ship), not the pause itself. Ops-surface unblock triggers unchanged.

**N15 v2 candidates** (all deferred to future trigger):
- Close-time freshness capture (`context='session_close'`)
- PA-tool read action for Rigby SIGN queries
- Command Center / Workspace tile after ~30-50 rows accumulate

**N15 misread mitigation validation** — first real STALE row (if/when observed) will exercise the "logging DETECTED, not INTRODUCED" framing. Add explicit `Detected by N15 — pre-existing drift, not N15 regression` note to that session's opening if misread happens anyway.

## §7. Files changed

- `core/services/process_freshness.py` (NEW, +176 lines)
- `core/services/td_handlers_ops.py` (amended, method body → 8-line wrapper)
- `core/management/commands/session_lifecycle.py` (amended, +history subparser + freshness helper + hook)
- `core/tests/test_session_freshness_2775.py` (NEW, +10 tests)
- `docs/research/implementation/RATIFICATION_2026-07-13_session_freshness_verdicts_jsonl.md` (NEW, ratification envelope)
- `docs/handoffs/SESSION_2775_SESSION_FRESHNESS_VERDICTS_JSONL_RATIFIED.md` (NEW, this handoff)
- `00-START-NEXT-SESSION.md` (rewritten for S2776 open)
- `CLAUDE.md` L3 anchor (refreshed to S2775)
- `tools/pa_local.sh` (S2775 pin `pa-77bdf04032204741`; retired at close)

## §8. Post-merge checklist

- [ ] `make recycle-all` per PLAYBOOK-7.4.4 (tenth close-cycle)
- [ ] Docs cascade (4-step + provenance)
- [ ] Verify `logs/session_freshness.jsonl` populates naturally at S2776 open
- [ ] Retire S2775 pin (`session_tool.retire ... force=true`) — sixth consecutive force=true retirement per S2770+ pattern
