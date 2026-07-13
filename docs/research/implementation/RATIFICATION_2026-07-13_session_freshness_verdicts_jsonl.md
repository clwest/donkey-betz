---
title: "Session-Open Freshness Verdicts JSONL Persistence Ratification Record (2026-07-13)"
status: active
authority: ratification-record
session_added: 2775
ratification_date: 2026-07-13
ratifier: chris
routing: rigby-pa-chat joint SIGN (single design + zoom-out per S2771 rule FIFTH consecutive application) + Chris D-verdict yes
scope: S2775 — N15 (session-open freshness verdicts persisted to JSONL for PLAYBOOK-7.4.4 trend detection). Extracts `_compute_process_staleness` from `OpsHandler` to module-level `core.services.process_freshness.compute_process_staleness`; adds `_record_session_freshness` helper to `session_lifecycle` that fires at `open` post-success; adds `session_lifecycle history` reader. Zero `/api/ops/*` surface change — ops-surface pause discipline honored.
serves_arc: substrate hardening — meta-observability for PLAYBOOK-7.4.4 (post-merge recycle rule). Ninth-close-cycle corroboration ladder to date has been eyeballed one session at a time; N15 turns the signal into a persisted trend surface so future MINOR/MAJOR Playbook amendments (e.g., threshold tightening, new trigger criteria) have empirical evidence at their back.
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-13_ops_urlconf_lambda_cleanup.md (S2774 — most recent close; established same-PR capstone fold precedent)
  - docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_6_0.md (S2766 — PLAYBOOK-7.4.4 codification; the rule N15 makes observable)
  - docs/research/implementation/RATIFICATION_2026-07-12_ops_query_param_allowlist.md (S2773 — S2771-rule application streak)
ratified_documents:
  - core/services/process_freshness.py (NEW — 176 lines; module-level `compute_process_staleness()` extracted from `OpsHandler._compute_process_staleness` with byte-identical return shape)
  - core/services/td_handlers_ops.py (amended — 148-line method body replaced with 8-line delegating wrapper that imports + calls the extracted function)
  - core/management/commands/session_lifecycle.py (amended — added `FRESHNESS_LOG_PATH` constant, `history` subcommand, `_record_session_freshness` fail-soft helper, hook call in `_handle_open` post-success)
  - core/tests/test_session_freshness_2775.py (NEW — 10 tests: 3 extraction-shape, 4 recorder behavior + fail-soft, 3 history reader)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2775 open freshness (retired-pin dispatch to Rigby, post-pin-mint) — verdict FRESH · SHA `b3139325831a` matches HEAD (NINTH corroboration cycle after PLAYBOOK-7.4.4; second cycle after pg16→pg15 port-swap recovery documented at S2774)
  - S2775 joint SIGN (Rigby, pin pa-77bdf04032204741) — Q1 YES on hook point (session_lifecycle open post-success, not pa_local.sh dispatch); Q2 MOSTLY YES on row shape with one fold (add `head_commit_age_seconds` for time-based drift analysis); Q3 YES on module-level extraction over instance-method call; Q4 agree defer close-time capture to v2; zoom-out (S2771 rule FIFTH consecutive application) surfaced 4 substantive concerns — (a) two-concern risk in `session_lifecycle` acceptable if telemetry stays subordinate + private, (b) misread mitigation via commit message language, (c) alternative substrates (beat/cron/standalone) not worth it for v1, (d) fail-soft + atomic append confirmed as designed
  - Chris D-verdict yes on the joint recommendation (all leans + `head_commit_age_seconds` fold)
  - S2775 capstone SIGN (Rigby, same pin) — `http_smoke_test` custom suite 6/6 PASS on all `/api/ops/*` endpoints (slo-status, failure-signatures, blocked-agents, health-summary, close-ceremony-ledger, recent-recycles) at 5-172ms latencies; `ops_tool.version` still returns `staleness_verdict=FRESH` + full expected shape (head_commit_sha, head_commit_timestamp, celery_workers_status, daphne_pid, daphne_pid_age_seconds, daphne_started_before_head_commit) — extraction is transparent
frozen: true
---

# Session-Open Freshness Verdicts JSONL Persistence — Ratification Record

Frozen canonical record of Chris's ratification of the S2775 N15 session-open freshness JSONL persistence on 2026-07-13. First non-ops-surface engineering session since the ops-console arc streak (S2770→S2774). Ninth-close-cycle post-PLAYBOOK-7.4.4-codification. Append-only.

---

## §1. Context

PLAYBOOK-7.4.4 was ratified at S2766 (v0.6.0 MINOR) after a corroboration ladder of 4 negative signals (STALE_BOTH at next-session-open S2758–S2761 pre-convention) + 3 positive signals (FRESH · SHA-match S2763–S2765 post-convention). The rule says: close-ceremony PRs MUST include a post-merge `make recycle-all` so local processes match HEAD SHA before the next session opens.

Post-codification cycles (S2766→S2774, eight sessions) have all shown FRESH · SHA-match at session-open freshness dispatch. Each verdict has been eyeballed one session at a time and mentioned in the session-open protocol block of `00-START-NEXT-SESSION.md`, but the signal has never been persisted to a durable surface. Consequences:

- No trend data. Future amendments (e.g., tighter thresholds, new PLAYBOOK-7.4.x rules) can't cite empirical evidence.
- Corroboration ladder assembly is manual — each amendment cycle re-reads handoffs to reconstruct the streak.
- The N11 PARTIAL_RECYCLE tile (S2770) only fires on live divergence; historical PARTIAL_RECYCLE events don't accrue as evidence.

N15 turns the freshness verdict into a persisted per-session-open row. Trend queries become trivial (`session_lifecycle history --limit 100`), amendment evidence bases become empirical, and the corroboration ladder pattern becomes machine-readable.

**Trigger discipline:** N15 is deliberately **non-ops-surface** — no new `/api/ops/*` endpoint, no new PA tool action, no new view. The S2774 forward-carry ("pause ops-surface PRs after N19 unless real incident / user-visible feature request / non-ops-adjacent Rigby SIGN") is honored. N15 extends `session_lifecycle` (already a management-command surface) and adds one new service module.

---

## §2. Ratified Change

Four files (+2 new, ~2 amended, -0):

**(a) NEW `core/services/process_freshness.py` (176 lines)**

Module-level `compute_process_staleness() -> Dict[str, Any]` extracted verbatim from `OpsHandler._compute_process_staleness`. Return shape byte-identical to pre-extraction. Same threshold rule (process is stale iff `create_time < HEAD commit timestamp`). Same UNKNOWN fallback semantics for missing git/psutil. Same `staleness_fix` hint on non-FRESH verdicts.

**(b) AMENDED `core/services/td_handlers_ops.py`**

`OpsHandler._compute_process_staleness` reduced from 148-line method body to 8-line delegating wrapper:

```python
def _compute_process_staleness(self) -> Dict[str, Any]:
    """Delegates to core.services.process_freshness.compute_process_staleness. ..."""
    from core.services.process_freshness import compute_process_staleness
    return compute_process_staleness()
```

Preserves method for `_ops_version()` caller + test suite compatibility. Zero behavior change to `ops_tool.version`.

**(c) AMENDED `core/management/commands/session_lifecycle.py`**

Additions:

- Module-level `FRESHNESS_LOG_PATH = Path("logs/session_freshness.jsonl")` constant.
- `history` subparser + `_handle_history(log_path, limit)` method that reads the JSONL back for eyeballing (`python manage.py session_lifecycle history --limit N`).
- Private `_record_session_freshness(new_pin, label, context, log_path=None) -> Dict[str, Any]` fail-soft helper that calls `compute_process_staleness()`, builds a lean row, appends to the JSONL. On exception: logs warning + writes to stderr + returns `{}`. Never propagates.
- Hook call inserted into `_handle_open()` immediately after the wrapper-rewrite success line prints. Passes `context='session_open'`. Prints a one-line summary of the captured verdict.

**(d) NEW `core/tests/test_session_freshness_2775.py` (10 tests)**

- 3 extraction-shape tests (`ComputeProcessStalenessShapeTests`): verdict key present + enum-valid; head metadata carried on non-UNKNOWN paths; `OpsHandler` wrapper delegates to extracted function via patch.
- 4 recorder tests (`RecordSessionFreshnessTests`): writes row with expected fields; counts stale celery workers correctly; fail-soft on compute exception (no propagation, no partial file); appends multiple rows correctly.
- 3 history reader tests (`HistorySubcommandTests`): graceful message on missing log; reads rows back with correct fields; `--limit` shows most-recent-N only.

---

## §3. What Was NOT Changed

**Explicitly out of scope for N15 v1 (Rigby Q4 agreement):**

- **Close-time freshness capture.** `_handle_close()` and `_handle_close --retire-only` do NOT record freshness rows. Trigger deferred to v2 when trend interpretation shows value. Would require a decision about which step of close ceremony to fire at (pre-retire? post-mint? post-wrapper-rewrite?).
- **PA-tool read action.** No new `ops_tool.recent_freshness_verdicts` action or `/api/ops/freshness-history/` endpoint. Reader is management-command only. Deferred to v2 pending trigger (e.g., Rigby needing to query trend during a SIGN pass).
- **UI tile.** No Command Center or Workspace tile. Consistent with `feedback_workspace_over_command_center_for_new_ui` (extend Workspace when trigger fires), gated on N15 accumulating enough rows to make a tile meaningful.
- **Row schema evolution.** No versioning field on the row. If schema needs to change, add a `schema_version: 2` field then; unversioned rows treated as `schema_version: 1`. Small upfront cost we're not paying.
- **Concurrent-write locking.** Local single-user pre-prod context — no concurrent session-open scenario exists. Naive `open('a')` + single-line write is atomic enough at this scale.

---

## §4. Rigby SIGN Summary

**Joint SIGN routing shape (per feedback_claude_rigby_agree_first_chris_yes_no):** Claude drafted the design (hook point, row shape, extraction pattern, test posture), routed 3 F-BLOCKING + 1 NON-BLOCKING + open-ended zoom-out to Rigby, folded her one row-shape refinement into the recommendation, then presented Chris one joint recommendation for D-verdict.

### F-BLOCKING folds (Rigby)

- **Q1 hook point placement — YES agree.** `session_lifecycle open` post-success is the semantic "session opened" event; `pa_local.sh` dispatch is noisier + not that event. Aligned.
- **Q2 row shape — MOSTLY YES with 1 fold.** Add `head_commit_age_seconds` (or `head_commit_time`) so trend analysis can bin verdicts by time-since-deploy. Rejected `staleness_fix` hint + `daphne_started_before_head_commit` (redundant with verdict + ages). Claude adopted `head_commit_age_seconds` as more directly interpretable for drift analysis than raw ISO string.
- **Q3 extract vs instantiate — YES agree (extract).** Module-level function avoids tool-handler lifecycle coupling + cleaner testing. Rigby: "keep OpsHandler method as 1-line wrapper for compatibility." Adopted verbatim.

### Non-blocking folds (Rigby preference aligned with Claude lean)

- **Q4 close-time capture — agree NO for v1.** Deferred to v2 with named `context='session_close'` + documented hook point.

### Q4 zoom-out (S2771 rule FIFTH consecutive application)

Rigby zoom-out surfaced 4 substantive concerns:

1. **Two-concern risk in `session_lifecycle`.** Adding freshness telemetry could dilute the command's charter (pin+wrapper). **Rigby resolution: acceptable** if helper stays private (`_record_session_freshness`, not exposed as separate subcommand) + JSONL clearly framed as "trend telemetry, not control plane" in the file docstring + row `context` field. All folded into implementation.
2. **Misread risk on first STALE row.** First STALE row could look like N15 broke something rather than N15 successfully DETECTING pre-existing drift. **Mitigation:** commit message + PR body explicitly frame N15 as "adds logging of detected staleness; does not change computation or verdict thresholds" (adopted below).
3. **Alternative substrates.** Beat task / cron / standalone script would decouple from `session_lifecycle` but add scheduling complexity and drift from the "session opened" semantic. **Not worth it for v1.** Aligned.
4. **Atomicity + hook order.** Freshness write must happen AFTER wrapper rewrite (mint fully committed) and be fail-soft. Naive `open('a')` sufficient locally (no concurrent-open scenario). Both adopted in implementation.

### Chris D-verdict

Yes on the joint recommendation. Single directive: "yes go ahead."

**Meta:** S2771 rule FIFTH consecutive application. Streak still producing 3-4 substantive concerns per session with concrete implementation folds. No drift into ritual. Non-ops-surface arc validates the rule extends beyond the ops-console iterations that established it.

---

## §5. Empirical evidence

**N15 unit suite:**

```
$ python manage.py test core.tests.test_session_freshness_2775 --noinput -v 2
Ran 10 tests in 0.157s
OK
```

**Full ops regression stack (S2772+S2773+N15):**

```
$ python manage.py test core.tests.test_ops_auth_regression_2772 core.tests.test_ops_query_param_allowlist_2773 core.tests.test_session_freshness_2775 --noinput
Ran 47 tests in 0.829s
OK
```

**Live E2E via shell (real compute against real process table):**

```python
row = cmd._record_session_freshness(
    new_pin='pa-77bdf04032204741',
    label='s2775-n15-e2e-verify',
    context='session_open',
)
# {'ts': '2026-07-13T22:17:47.013096+00:00',
#  'session_label': 's2775-n15-e2e-verify',
#  'pin': 'pa-77bdf04032204741',
#  'context': 'session_open',
#  'verdict': 'FRESH',
#  'head_sha_short': 'b3139325831a',
#  'head_commit_age_seconds': 1968,
#  'daphne_pid_age_seconds': 1952,
#  'celery_worker_count': 5,
#  'celery_stale_count': 0}
```

`session_lifecycle history` reads it back:

```
[SESSION_LIFECYCLE] freshness history (1 of 1 rows shown):
  2026-07-13T22:17:47.013096+00:00  FRESH  head=b3139325831a  celery_stale=0/5  label=s2775-n15-e2e-verify
```

**Rigby capstone `http_smoke_test` (custom suite, all 6 `/api/ops/*`):**

```
{
  "ok": true,
  "suite": "custom",
  "environment": "local",
  "passed": 6,
  "failed": 0,
  "skipped": 0,
  "total": 6
}
```

All endpoints HTTP 200 at 5-172ms latencies. `ops_tool.version` continues to return `staleness_verdict=FRESH` with the full expected shape (extraction is transparent to the tool handler).

---

## §6. Post-ratification bindings

- **First natural hook fire:** S2776 open when Chris runs `python manage.py session_lifecycle open --label s2776-<slot>`. Row will land at `logs/session_freshness.jsonl` with `context='session_open'`.
- **`logs/session_freshness.jsonl`** is gitignored (`logs/` in `.gitignore`) — not shipped in PR. Test row from live E2E was written locally only.
- **Wrapper `tools/pa_local.sh`** — currently points at active S2775 pin `pa-77bdf04032204741`. Will be retired (force=true, sixth consecutive) at S2775 close.
- **CLAUDE.md L3 anchor** — refreshed to reference S2775 N15 landing.
- **`_compute_process_staleness` OpsHandler method** — retained as 1-line wrapper. Any future direct callers (test suite, external tool paths) continue to work unchanged.

---

## §7. Forward carry

**Rigby S2774 forward-carries (state at S2775 close):**

- **Pause ops-surface PRs** discipline — **still held**. N15 is non-ops-surface; the streak breaks on the type of surface touched (management command + service module + tests), not on session count. Ops-surface unblock triggers unchanged: real incident, user-visible feature, or non-ops-adjacent Rigby SIGN.
- **30+ other lambda-`__import__` sites in `core/urls.py`** — still forward-carrying, no trigger.
- **Rigby S2773 forward-carry #5 (health_summary vs ops_tool.overview overlap)** — still forward-carrying, no divergence observed this session.
- **First S2771-rule same-PR capstone-fold precedent** (S2774 novel) — S2775 does NOT re-apply the pattern; Rigby's zoom-out surfaced 4 concerns but all were **mitigations folded into design** (helper stays private, commit message language, atomic append), not new same-PR verification actions. Precedent stands as a case-by-case classification, not a new default.

**Rigby S2775 zoom-out surfaces (new):**

- **N15 v2 candidates** (unblock triggers pending): close-time freshness capture (`context='session_close'`); PA-tool read action for Rigby SIGN queries; Command Center or Workspace tile after ~30-50 rows accumulate. None land now; each waits for a real user-visible ask or Rigby SIGN concern.
- **Misread mitigation validation.** First real STALE row (if/when observed at some future session-open) will exercise the "logging of DETECTED, not INTRODUCED" framing. If the misread happens anyway, add a `Detected by N15 — pre-existing drift, not N15 regression` note to that session's opening block.
- **Row schema evolution readiness.** If a v2 field is added to the row (e.g., pgbouncer PID, migration count), plan the schema versioning add at same time — small upfront cost avoids ad-hoc mixed-schema JSONL.

---

## §8. Meta-observation on the SIGN discipline

**S2771 rule — FIFTH consecutive application.** Streak now:

| Session | Arc | Zoom-out folds surfaced | Same-PR ships | Forward-carries |
|---|---|---|---|---|
| S2771 | CCL v2 text search | 3 concerns | 2 | 1 |
| S2772 | auth-regression + staff gate | 7 concerns | 2 | 4 |
| S2773 | param-allowlist + refactor + date fix | 5 concerns | 3 | 2 |
| S2774 | URLConf lambda cleanup | 4 concerns | 4 (incl. capstone) | 1 (pause discipline) |
| S2775 | freshness verdicts JSONL | 4 concerns | 4 (all mitigations folded) | 0 |

**Novel this session:** first non-ops-surface arc since the streak began. All 4 zoom-out concerns folded into design-time mitigations rather than deferring anything. This is a distinct pattern from S2774's same-PR capstone verification fold — both close their zoom-out concerns same-PR but via different mechanisms (S2774: new verification action; S2775: design-time mitigation). Emerging classification: zoom-out concerns can be `same-PR-actionable` (new verification), `same-PR-mitigatable` (design fold), or `future-trigger` (forward-carry).

**Substrate maturity signal:** N15 was possible in one session BECAUSE the underlying `_compute_process_staleness` code has been stable for 8 sessions (S2759+). Extraction is safe when the extractee is well-tested — the 37 existing tests + `ops_tool.version` in daily use since S2759 give high confidence the shape is stable. Substrate hardening compounds not just within ops-console but across whole-platform surfaces.

**Meta-observability precedent.** N15 is the first substrate-hardening ship whose value depends on OTHER sessions accumulating data over time. All prior close-cycle ships (S2770→S2774) delivered immediate observable value on the same session they landed. N15 lands the mechanism; the value lands over future sessions as the trend surface fills. This is a distinct class of substrate work (mechanism-now, value-later) worth naming for future arc planning.
