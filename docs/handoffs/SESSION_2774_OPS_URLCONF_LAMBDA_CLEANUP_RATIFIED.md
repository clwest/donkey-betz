---
session: 2774
date: 2026-07-13
title: "Ops-endpoint URLConf lambda cleanup + same-PR capstone verification ratified"
status: complete
outcome: shipped
scope: net-new-engineering-N19-plus-capstone
canonical_authority: repo_canonical
ratification_envelope: docs/research/implementation/RATIFICATION_2026-07-13_ops_urlconf_lambda_cleanup.md
---

# Session 2774 — Ops-endpoint URLConf lambda cleanup ratified

## §1. TL;DR

Chris selected N19 from the S2774 candidate menu — the S2773 forward-carry #3 (URLConf `lambda r: __import__(...)` tech debt on the 6 `/api/ops/*` routes). Rigby's zoom-out (per S2771 rule, **fourth consecutive application**) surfaced one concrete new ask: run a same-PR end-to-end capstone verification after 5 consecutive `/api/ops/*` PRs without an integrated pass. Chris double-yes'd both — N19 as designed AND capstone in-same-PR. Novel precedent: **first time a zoom-out concern has been folded into the same PR as a concrete verification action rather than deferred to a future trigger.**

Shipped: `core/urls.py` amended (+10 / -6 lines) — grouped `from core.views_ops_console import (...)` near other `views_*` imports; 6 lambda-`__import__` `path()` entries rewritten to direct callable references. Zero behavior change. 37/37 regression tests PASS in 0.734s. Capstone `http_smoke_test` 7/7 PASS through Rigby, all 6 `/api/ops/*` endpoints returning HTTP 200 at 16-172ms.

**Ninth close-cycle post-PLAYBOOK-7.4.4-codification.** Third consecutive substrate-hardening session in the ops-console arc (S2772 auth-regression → S2773 param-allowlist → S2774 URLConf cleanup). S2771 rule holds for the fourth time.

Meta-important session-open discovery: pg16 (April fossil DB) had captured port 5432 after machine travel, masquerading as the real DB. Full recovery documented — pg15 promoted to brew launchd, pg16 parked with data preserved.

## §2. Timeline

| Time (approx) | Event | Reference |
|---|---|---|
| S2774 open | machine came up cold post-travel; `make status` all-down | this session |
| Restart attempt #1 | `make restart` failed — postgres role `unified_user` missing on port 5432 | daphne server.log |
| DB triage | discovered pg15 (July DB, 382 migrations) blocked from binding 5432 by pg16 (April fossil, 339 migrations) | pg15 error log |
| Port swap | pg16 stopped + parked; pg15 promoted to `brew services start`ed; `.env` + pgbouncer + wrapper restored | this session |
| pg16 artifact cleanup | on port 5434: dropped token, chat conversation, DATABASE OWNER reverted, postgres role `chris` dropped (Django user row inert, 240 FK deps) | this session |
| Freshness check | verdict FRESH · SHA `13b5d101f32f` matches HEAD (EIGHTH corroboration cycle after PLAYBOOK-7.4.4) | pin above |
| N19 selected | Chris: "start with N19, still under the correct parent work" | this session |
| Pin minted | `pa-206d3fa2f64d440b` scoped to `s2774-n19-ops-urlconf-lambda-cleanup` | `session_lifecycle open` |
| Joint SIGN + zoom-out | Rigby: F-BLOCKING Q2 strict scope + no-behavior-change tripwire; PASS on Q1/Q3; Q4 zoom-out surfaced 4 concerns (fourth consecutive S2771 rule) | pin above |
| Chris double-yes | approve N19 as designed AND fold Rigby's capstone verification in-same-PR (not future trigger) | this session |
| Code edit | 2 edits on `core/urls.py`: import block insert + 6 lambda→direct refs | this session |
| Regression suite | 37/37 PASS (test_ops_auth_regression_2772 + test_ops_query_param_allowlist_2773) in 0.734s | pytest |
| Capstone via Rigby | `http_smoke_test` custom suite: 7/7 PASS, all 6 ops endpoints HTTP 200 at 16-172ms; `repo_tool.search` confirmed no lambda residue | pin above |
| Envelope + handoff | this doc + `RATIFICATION_2026-07-13_ops_urlconf_lambda_cleanup.md` | close ceremony |
| Docs cascade + provenance | 4-step + `build_docs_provenance` | close ceremony |
| PR + admin merge | (filled at merge) | GitHub |
| Post-merge recycle-all | `make recycle-all` per PLAYBOOK-7.4.4 (ninth cycle) | this session |
| Pin retire | `pa-206d3fa2f64d440b` retired with force=true | `session_tool.retire` |

## §3. What shipped

**Single file amended:** `core/urls.py` (+10 / -6 lines, 22 line touches per `git diff --stat`).

**(a)** Grouped import added right after `views_fleet_paid_interest` (line ~101):

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

**(b)** Six `/api/ops/*` `path()` entries at lines 2402-2407 rewritten from:

```python
path('api/ops/slo-status/', lambda r: __import__('core.views_ops_console', fromlist=['slo_status']).slo_status(r), name='ops-slo-status'),
```

…to:

```python
path('api/ops/slo-status/', slo_status, name='ops-slo-status'),
```

Zero behavior change. Eager import at Django startup replaces per-request `__import__`; both dispatch to the same `views_ops_console.<name>` function. `views_ops_console.py` import block is stdlib+Django only, no side effects on eager load — verified pre-refactor.

**Out of scope (Rigby Q2 F-BLOCKING):**

- The 30+ other `lambda r: __import__(...)` sites in `core/urls.py` (proposals, spider_api, agent_api, audio, tts, video). No trigger has fired. Rolling them in would dilute traceability and expand review surface.

**No new tests.** Existing 37 tests (S2772 auth-regression 15 + S2773 param-allowlist 22) exercise real requests through the URLConf — silent re-lambdification would immediately break both suites.

## §4. Rigby SIGN Summary

**Routing:** joint SIGN pre-Chris (per feedback_claude_rigby_agree_first_chris_yes_no). Claude drafted implementation shape → Rigby returned F-BLOCKING folds + non-blocking preferences + Q4 zoom-out → reconciled joint recommendation → Chris D-verdict.

**F-BLOCKING:**
- Q2 strict scope: /api/ops/* only, no fold-in of 30+ other lambda sites. ✓
- No-behavior-change tripwire: eager-import approved conditional on views_ops_console.py having no import-time side effects. Verified stdlib+Django only. ✓

**Non-blocking:**
- Q1 grouped import in parens near other `views_*` imports. ✓
- Q3 skip regression guard test — `resolve().func is X` brittle; 37 tests cover dispatch. ✓

**Q4 zoom-out (S2771 rule fourth consecutive):**
1. PR churn on same surface without integrated capstone → **capstone verification recommended after N19 lands.** ★
2. Not over-hardening `/api/ops` (control plane justifies).
3. Adjacent risk = import-time behavior + URLConf fragility, mitigated by capstone.
4. Review fatigue + merge-order coupling → pause ops-surface PRs after N19 unless new trigger.

**Chris D-verdict:** double-yes. N19 as designed + capstone in-same-PR (novel — first same-PR fold of a zoom-out concern).

**Capstone SIGN (Rigby, same pin):** `http_smoke_test` 7/7 PASS + `repo_tool.search` confirmed direct-callable pattern landed. All 6 ops endpoints HTTP 200 at 16-172ms latency. Zero drift.

## §5. Post-merge browser eyeball (Chris)

- Hard-refresh `localhost:8000/workspace?tab=system&sub=ops` → tile should render identically (staff view). All 6 ops endpoints return unchanged shapes.
- Curl smoke: `curl -H "Cookie: sessionid=..." http://localhost:8000/api/ops/close-ceremony-ledger/?debug=1` should still return HTTP 400 `code='unknown_query_params'` (S2773 allowlist intact through the refactor).

## §6. Twin-Pointer Card

📁 **Repo `/docs/` + `/core/` — S2774 artifacts:**

- **Amended backend module:** `core/urls.py` (grouped import at line ~101; 6 direct-callable path entries at 2402-2407)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-13_ops_urlconf_lambda_cleanup.md`
- **Handoff:** `docs/handoffs/SESSION_2774_OPS_URLCONF_LAMBDA_CLEANUP_RATIFIED.md`
- **Predecessor envelopes:** S2769 (CCL v2 filters), S2771 (text search + meta-critique + S2771 rule origin), S2772 (auth-regression), S2773 (param-allowlist + S2773 forward-carry #3 origin)
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2774
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** ops-console tab unchanged; all 6 endpoints continue to work identically.

## §7. Current Repository State

| Field | Value |
|---|---|
| Branch | `main` (post-merge) |
| HEAD | (filled at merge — post-S2774 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| Playbook rule count | 202 |
| RUR-C1 state | S2755→S2773 CLOSED · **S2774 N19 URLConf cleanup + same-PR capstone CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-206d3fa2f64d440b` (retired at S2774 close, force=true, FIFTH consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-206d3fa2f64d440b` (retired; forces fresh mint at S2775 open) |
| Live infra state | S2755→S2773 diagnostic infra + Playbook v0.6.0 + CCL v2 hover/drawer/filter/search + N7 recycle emitter + N11 PARTIAL_RECYCLE tile + N16 auth-regression + staff gate + N18v2 allowlist + helper refactor + date fix + **N19 URLConf cleanup** operational |
| Postgres :5432 | **pg15** (July DB, 382 migrations, S2773+N19 state) — brew launchd `started`, survives reboot |
| Postgres pg16 | Parked (April fossil, data preserved on disk, plist unloaded) |
| Next move | Chris selects at S2775 open |

## §8. What This Session Taught About Doing Sessions

**Machine-travel recovery is not a Makefile — it's a triage.** Chris's opening framing ("kill and restart all makefiles") assumed a normal cold boot. Actual state: pg16 fossil DB had captured port 5432; pg15 (real DB) couldn't bind and was in brew `error` state. Six symptoms rolled out sequentially (missing `unified_user` role → stale wrapper token → missing conversations → 3-month schema drift → 44 unapplied migrations → missing `core_ops_run` table) before the port-collision root cause surfaced. Lesson: when session-open freshness is failing in unusual ways (not just stale processes), *check port ownership + brew services status BEFORE running the standard restart drill*.

**Same-PR capstone fold is a new pattern.** Previous S2771-rule applications (S2771→S2772→S2773) always emitted zoom-out concerns as forward-carries with future triggers. This session, Chris D-verdict'd Rigby's capstone verification ask into the SAME PR as the primary change. Emerging classification: zoom-out concerns should be labeled `same-PR-actionable` vs `future-trigger` on a case-by-case basis, not defaulted to forward-carry.

**Substrate hardening compounds.** N19 was safe *because* S2772's auth-regression tests + S2773's param-allowlist tests already existed. Same refactor without them would have been higher-risk. Each substrate PR makes the next one safer. This is why the "pause ops-surface PRs" discipline in the forward-carry section is a discipline, not a freeze — resumption is safe when a real trigger arrives.

**Wrapper-token drift traceability.** The wrapper's Session 1098/1165 comments assumed a chris/donkeyking user rename history that no longer matched the current pg15 DB state. Neither the wrapper nor the memory rules had a canonical "here's what the local user is right now" pointer. Consider adding a runtime check to `pa_local.sh` that verifies the token maps to a live user + surfaces the username at first invocation of each session (feedback candidate; not codified this session).
