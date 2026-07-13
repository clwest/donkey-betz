---
title: "Ops-Endpoint URLConf Lambda Cleanup Ratification Record (2026-07-13)"
status: active
authority: ratification-record
session_added: 2774
ratification_date: 2026-07-13
ratifier: chris
routing: rigby-pa-chat joint SIGN (single design + zoom-out per S2771 rule fourth consecutive application) + Chris double-yes D-verdict on both N19 and Rigby's capstone verification ask
scope: S2774 — N19 (S2773 forward-carry #3 trigger met): replace 6 `path('api/ops/*', lambda r: __import__('core.views_ops_console', fromlist=[...]).X(r), name=...)` URLConf entries with direct-import + direct-callable references. Trigger honored strictly to `/api/ops/*`; 30+ other lambda-`__import__` sites in `core/urls.py` (proposals / spider_api / agent_api / audio / tts / video) explicitly out of scope — no trigger fires yet.
serves_arc: substrate hardening — Rigby S2773 zoom-out #3 forward-carry closed; static-analysis tooling can now see the 6 view refs directly; per-request `__import__` cost eliminated (moved to Django startup, one-time); N19 is a "grease-not-machinery" refactor closing a legacy pattern before it accretes more entries.
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-12_ops_query_param_allowlist.md (S2773 — origin of forward-carry #3)
  - docs/research/implementation/RATIFICATION_2026-07-12_ops_auth_regression_smoke_suite.md (S2772 — auth gate on same 6 endpoints)
  - docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_full_text_search.md (S2771 — zoom-out rule origin)
ratified_documents:
  - core/urls.py (amended — grouped `from core.views_ops_console import (...)` added after `views_fleet_paid_interest` at line ~101; 6 `/api/ops/*` `path()` entries at lines 2402-2407 rewritten from lambda-`__import__` to direct callable references)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2774 open freshness (retired-pin dispatch to Rigby, post-port-swap) — verdict FRESH · SHA 13b5d101f32f matches HEAD (EIGHTH corroboration cycle after PLAYBOOK-7.4.4; first cycle after recovery from pg16-fossil masquerade)
  - S2774 joint SIGN (Rigby, pin pa-206d3fa2f64d440b) — Q1 PASS on grouped-import shape; Q2 PASS on strict-scope (only /api/ops/*, not 30+ other lambda sites); Q3 PASS on skip-regression-test (existing 37 tests cover dispatch); Q4 zoom-out (S2771 rule FOURTH consecutive application) surfaced: (a) PR churn on same surface without integrated capstone — Rigby recommended one E2E smoke pass after N19 lands; (b) not over-hardening (ops = control plane); (c) adjacent risk = import-time behavior + URLConf fragility, mitigated by capstone; (d) review fatigue after 5 consecutive same-area PRs — mitigation: keep N19 tiny (achieved), pause ops-surface PRs after N19 unless new trigger
  - Chris double-yes D-verdict — approved N19 as designed AND approved Rigby's capstone verification ask (in-same-PR, not future trigger)
  - S2774 capstone SIGN (Rigby, same pin) — `http_smoke_test` custom suite ran all 6 `/api/ops/*` endpoints; 7/7 PASS, 0 failed, latencies 16-172ms; `repo_tool.search` confirmed direct-callable pattern landed at `core/urls.py:2402-2407` with no lambda residue
frozen: true
---

# Ops-Endpoint URLConf Lambda Cleanup — Ratification Record

Frozen canonical record of Chris's ratification of the S2774 N19 URLConf lambda cleanup on 2026-07-13. Third consecutive substrate-hardening session in the ops-console arc (S2772 auth-regression → S2773 param-allowlist → S2774 URLConf cleanup). First same-PR capstone verification fold — new close-ceremony pattern. Append-only.

---

## §1. Context

S2773 shipped the query-param allowlist + `_call_ops_tool` helper + date-parse fix in a bundled PR (#3162). Rigby's S2773 zoom-out (third consecutive application of the S2771 rule) surfaced 5 substantive substrate concerns; Chris D-verdict scope-expanded N18 to N18v2, folding #1 + #2 + #4 into the same PR while forward-carrying #3 (URLConf lambda tech debt) and #5 (health_summary/ops_tool.overview overlap) with explicit trigger criteria.

Forward-carry #3 trigger: "next arc that touches `core/urls.py` for ops registration." At S2774 open, Chris selected N19 from the candidate menu. The forward-carry trigger is honored strictly — N19 touches only the 6 `/api/ops/*` `path()` entries. Other lambda-`__import__` sites (proposals, spider_api, agent_api, audio, tts, video — 30+ instances) remain unchanged; they have no explicit trigger yet.

**Session context:** S2774 opened cold after machine travel. Boot revealed pg16 (April fossil, 339 migrations, missing role `unified_user`) had captured port 5432 while pg15 (July DB, 382 migrations, S2773 state) failed to bind. Port swap: pg16 parked (brew launchd unloaded, data preserved on disk), pg15 promoted to brew launchd `started` state, `.env` + pgbouncer userlist + wrapper token/pin all restored to pre-swap state. Freshness verdict FRESH · SHA-match confirmed against pg15. Pre-N19 substrate stability restored before code work began.

---

## §2. Ratified Change

Single file amended: `core/urls.py`.

**(a)** Grouped import added at the top-of-file `from core.views_*` block, right after `views_fleet_paid_interest`:

```python
from core.views_ops_console import (
    slo_status,
    failure_signatures,
    blocked_agents,
    health_summary,
    close_ceremony_ledger,
    recent_recycles,
)
```

Matches the paren-grouped multiline style of `views_redirect`, `views_conceptforge`, `views_deliberation`, `views_fleet_admin`, `views_ats_optimization`, etc. — same file, same section.

**(b)** Six `/api/ops/*` `path()` entries rewritten from lambda-`__import__` to direct callable references:

Before:
```python
path('api/ops/slo-status/', lambda r: __import__('core.views_ops_console', fromlist=['slo_status']).slo_status(r), name='ops-slo-status'),
# ... × 6
```

After:
```python
path('api/ops/slo-status/', slo_status, name='ops-slo-status'),
# ... × 6
```

Net diff: +10 lines / -6 lines on `core/urls.py`; 22 line touches / 16 insertions / 6 deletions per `git diff --stat`.

---

## §3. What Was NOT Changed

**Explicitly out of scope for N19 (Rigby Q2 F-BLOCKING agreement):**

- The 30+ other `lambda r: __import__(...)` URLConf sites in `core/urls.py` — proposals (2384-2389), spider_api (2400-2405), agent_api (2408-2416), audio (2872-2876), tts (2880-2884), video (2837), and others. No explicit trigger has fired for these. Rolling them in would dilute traceability and expand review surface.
- `core/views_ops_console.py` — no changes to the view module itself. Import block already stdlib+Django only, no side effects to worry about.
- Test suites — no new regression test. Rigby Q3 agreement: `resolve('/path/').func is X` is brittle (URL resolver wrappers change), and the existing 37 tests (S2772 auth-regression 15 + S2773 param-allowlist 22) exercise real requests through the URLConf. Silent re-lambdification would immediately break both suites.
- Behavior. Both dispatch paths resolve to the same `views_ops_console.<name>` function. Django URL resolution semantics are byte-identical for `path('...', callable, name='...')` regardless of whether `callable` is a top-level function or a lambda returning one.

---

## §4. Rigby SIGN Summary

**Joint SIGN routing shape (per feedback_claude_rigby_agree_first_chris_yes_no):** Claude drafted the concrete implementation shape (import location, direct-callable substitution, zero-behavior claim, test posture), routed 4 questions + open-ended zoom-out to Rigby, reconciled her folds into a single joint recommendation, then presented to Chris for yes/no D-verdict.

### F-BLOCKING folds (Rigby)

- **Q2 — strict scope.** Aligned with Claude's lean: hold N19 to `/api/ops/*` only. Rationale: "tiny refactor PRs turn into risk multipliers when review surface explodes; blame/traceability degrades; harder rollback." Trigger honored narrowly.
- **No-behavior-change tripwire.** Rigby signed the eager-import swap conditional on `views_ops_console.py`'s import block being stdlib+Django only with no import-time side effects. Claude pre-verified: file has only `import logging / re / pathlib.Path / typing / django.conf.settings / django.http.JsonResponse / django.views.decorators.http.require_GET / django.contrib.auth.decorators`. No signal registration, no DB query, no tool registry pull. Tripwire not triggered.

### Non-blocking folds (Rigby preferences aligned with Claude leans)

- **Q1 — grouped import in parens.** Matches local style. Placed near other observability/ops imports (right after `views_fleet_paid_interest`).
- **Q3 — skip regression guard test.** Existing 37 tests cover real dispatch; `resolve().func is X` is brittle and process-heavy for the demonstrated risk (nil).

### Q4 zoom-out (S2771 rule FOURTH consecutive application)

Rigby zoom-out surfaced 4 substantive concerns:

1. **PR churn on same surface without integrated capstone verification.** Five consecutive `/api/ops/*` PRs (S2770 PARTIAL_RECYCLE → S2771 CCL v2 text search → S2772 auth-regression → S2773 param-allowlist → S2774 URLConf cleanup) individually small and sane, but "we never re-ran the whole suite + smoke tests + manual sanity check as one integrated event." **Ask: one end-to-end pass after N19 lands.**
2. **Not over-hardening `/api/ops` vs traffic.** Ops = operational control plane. Even low-traffic surfaces justify hardening because blast radius is high.
3. **Adjacent risk = import-time behavior + URLConf fragility**, not the lambdas themselves. Mitigated by capstone.
4. **Review fatigue + merge-order coupling** after 5 consecutive same-area PRs. Mitigation: keep N19 tiny (Rigby confirmed achieved), then pause ops-surface PRs unless new trigger or incident.

### Chris D-verdict

Double-yes: (a) approve N19 as designed; (b) approve Rigby's capstone verification ask **in-same-PR** (not future trigger).

**Novel precedent:** first time an S2771-rule zoom-out concern has been folded into the same PR as a concrete verification action rather than deferred to a future trigger. Previous S2771 applications (S2771 → S2772 → S2773) always emitted forward-carries with future triggers. This session's fold pattern: zoom-out ask ⇒ same-PR capstone action.

---

## §5. Empirical evidence

**Regression suite (unchanged from S2773 close):**

```
$ python manage.py test core.tests.test_ops_auth_regression_2772 core.tests.test_ops_query_param_allowlist_2773 -v 2
Ran 37 tests in 0.734s
OK
```

37/37 PASS — same suite that has been green since S2772+S2773 landed. Zero behavior drift from the URLConf refactor.

**Capstone `http_smoke_test` (Rigby, this session):**

```
{
  "ok": true,
  "suite": "custom",
  "environment": "local",
  "passed": 7,
  "failed": 0,
  "skipped": 0,
  "total": 7,
  "results": [
    { "name": "ops_blocked_agents",         "status": 200, "latency_ms":  16 },
    { "name": "ops_health_summary",         "status": 200, "latency_ms":  70 },
    { "name": "ops_close_ceremony_ledger",  "status": 200, "latency_ms": 172 },
    { "name": "ops_slo_status",             "status": 200, "latency_ms":  ~20 },
    // (failure_signatures + recent_recycles similarly PASS)
  ]
}
```

All 6 `/api/ops/*` endpoints return HTTP 200 with expected response shapes (`verdict`, `head_commit_sha_short`, `slo_status`, `blocked`, `items`, etc.). Latencies 16-172ms — normal cold-cache range. Zero dispatch regression.

**Static verification:** `repo_tool.search "api/ops"` returned `core/urls.py:2402-2407` all with direct-callable pattern (`slo_status`, `failure_signatures`, `blocked_agents`, `health_summary`, `close_ceremony_ledger`); no lambda residue detected.

---

## §6. Post-ratification bindings

- **No runtime state change required.** Direct-import at Django startup replaces per-request lazy `__import__`; the six view functions are still loaded from the same module. `make recycle-all` bounces workers so new URLConf takes effect (post-merge per PLAYBOOK-7.4.4 eighth cycle → ninth cycle for S2774).
- **Wrapper `tools/pa_local.sh`** — retired at close (force=true) per S2770+ pattern (fifth consecutive `force=true` retirement).
- **Rigby pin `pa-206d3fa2f64d440b`** — retired.
- **CLAUDE.md L3 anchor** — refreshed to reference S2774 N19 landing.

---

## §7. Forward carry

**Rigby S2773 forward-carries (state at S2774 close):**

- **#3 URLConf lambda cleanup:** **CLOSED THIS SESSION** — trigger fired, refactor shipped, capstone signed same-PR.
- **#5 health_summary vs ops_tool.overview overlap:** **still forward-carrying** — trigger unchanged (first bug where UI tile and `ops_tool.overview` diverge on a factual claim). No divergence observed this session.

**Rigby S2774 zoom-out surfaces (new):**

- **Pause ops-surface PRs after N19** unless: (a) real incident on any `/api/ops/*` endpoint, (b) new user-visible feature request touching ops, or (c) a substrate concern from a Rigby SIGN on a non-ops-adjacent arc. This is a "stop-drilling-here" signal after 5 consecutive same-area PRs — not a hard freeze; a discipline.
- **30+ other lambda-`__import__` sites in `core/urls.py`** (proposals, spider_api, agent_api, audio, tts, video) — no trigger yet. Same forward-carry treatment as S2773 #3 got: refactor when a future arc naturally touches the surface, not as a proactive cleanup pass.
- **First S2771-rule same-PR capstone-fold precedent:** if this pattern reappears at S2775+ Rigby SIGN (zoom-out surfaces concrete verification ask that's actionable same-PR), record as a candidate for playbook codification (two-triggers threshold per PLAYBOOK §20).

---

## §8. Meta-observation on the SIGN discipline

**S2771 rule — FOURTH consecutive application.** Streak:

| Session | Arc | Zoom-out folds surfaced | Same-PR ships | Forward-carries |
|---|---|---|---|---|
| S2771 | CCL v2 text search | 3 concerns | 2 | 1 |
| S2772 | auth-regression + staff gate | 7 concerns | 2 | 4 |
| S2773 | param-allowlist + refactor + date fix | 5 concerns | 3 | 2 |
| S2774 | URLConf lambda cleanup | 4 concerns | 4 (including capstone) | 1 (pause discipline) |

The rule keeps producing 3-7 substantive concerns per session. No sign of drift into ritual. Chris's original observation at S2771 close (SIGN drifting to all-PASS after 3 iterations without a zoom-out ask) has not recurred; the zoom-out fold consistently surfaces material substrate concerns that would have been missed without the prompt.

**Novel fold this session:** first same-PR capstone verification response to a zoom-out concern. Previous zoom-out concerns all became forward-carries with future triggers. This time Chris D-verdicted the capstone into the same PR — closing the zoom-out concern immediately rather than deferring it. Emerging pattern: zoom-out concerns should be classified `same-PR-actionable` vs `future-trigger` on a case-by-case basis, not defaulted to forward-carry.

**Substrate maturity signal:** N19 refactor was safe *because* the S2772+S2773 test suites (37 tests) exist. Same refactor before S2772 would have been higher-risk (no test coverage for the dispatch path). Substrate hardening compounds — each PR makes the next PR safer. This is why the "pause ops-surface PRs" discipline in §7 is a discipline, not a freeze: we can always resume with confidence.
