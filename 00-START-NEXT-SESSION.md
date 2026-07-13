# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2774 CLOSED — OPS URLConf LAMBDA CLEANUP + SAME-PR CAPSTONE RATIFIED

**Refreshed 2026-07-13 (SESSION 2774 CLOSED — N19 shipped. `core/urls.py` amended: grouped `from core.views_ops_console import (…)` added near other `views_*` imports; 6 `/api/ops/*` `path()` entries at 2402-2407 rewritten from lambda-`__import__` to direct callable references. Zero behavior change. Existing 37 tests (S2772+S2773) PASS in 0.734s. Rigby capstone `http_smoke_test` 7/7 PASS at 16-172ms. FIRST same-PR fold of a zoom-out concern (novel precedent). Ninth close-cycle post-PLAYBOOK-7.4.4-codification. S2771 rule fourth consecutive application — no drift into ritual.)**

**S2774 shipped as 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **Code change:** `core/urls.py` (+10/-6 lines). Grouped import block + 6 lambda→direct callable refs.
- **No new tests.** Existing 37 tests validate dispatch. Rigby Q3 F-PASS.
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-13_ops_urlconf_lambda_cleanup.md`
- **Handoff:** `docs/handoffs/SESSION_2774_OPS_URLCONF_LAMBDA_CLEANUP_RATIFIED.md`
- **CLAUDE.md L3 anchor:** refreshed to S2774; L7 unchanged
- **Docs cascade:** 4-step + provenance rebuild
- **Post-merge:** `make recycle-all` invoked per PLAYBOOK-7.4.4 (ninth cycle)

---

## SESSION-OPEN INFRA STORY (S2774) — TRAVEL RECOVERY DISCOVERY

Machine came up cold after travel. Standard `make restart` failed because:

- pg16 (April fossil DB, 339 migrations) came up first and captured port 5432
- pg15 (July DB, 382 migrations, S2773+N19 state) was blocked from binding 5432
- Django `.env` said `unified_user` — role missing on pg16, present on pg15
- pgbouncer cached the login-failure on pg16 and refused all new connections
- Wrapper token was tied to a Django `chris` user that existed on pg15 only

Six symptoms surfaced before the port-collision root cause emerged. **Recovery:**
- Stop pg16 → free 5432
- Start pg15 → binds 5432 cleanly
- pg15 now under brew launchd `started` (survives reboot)
- pg16 parked: plist unloaded, data preserved on disk as archive
- `.env` + pgbouncer userlist + wrapper token/pin all reverted to pre-swap state
- Freshness verdict FRESH · SHA `13b5d101f32f` confirmed against pg15

**Lesson for S2775 open:** if `make restart` fails in an unusual pattern (missing roles, cached auth errors, missing conversations), run `brew services list | grep postgres` and `lsof -iTCP:5432` BEFORE the standard restart drill. Port ownership + brew status is the fast path to distinguishing "cold boot" from "fossil DB masquerading as real."

---

## THE PIVOT — WHY THIS SHIP MATTERS

Substrate hardening arc continues. S2772 shipped auth-regression + staff gate. S2773 shipped query-param allowlist + refactor + date fix. S2774 shipped URLConf lambda cleanup — Rigby's S2773 forward-carry #3 trigger fired ("next arc touching `core/urls.py` for ops registration"). Static analysis tooling can now see the 6 view refs directly instead of through a `__import__` lambda; per-request import cost eliminated (moved to Django startup, one-time).

Novel precedent this session: **first same-PR fold of an S2771-rule zoom-out concern.** Rigby raised "no integrated capstone after 5 consecutive `/api/ops/*` PRs" — Chris D-verdict'd it into the same PR rather than forward-carry with a future trigger. Emerging classification: zoom-out concerns should be labeled `same-PR-actionable` vs `future-trigger` on a case-by-case basis.

**Meta discipline:** Rigby's zoom-out flagged "pause ops-surface PRs after N19 unless real trigger." Not a freeze; a discipline. Resumption is safe because substrate compounds — 37 tests + smoke suite make the next refactor lower-risk.

---

## S2775 CANDIDATES (Chris selects at open)

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

**Note discipline:** ops-surface PRs paused per Rigby S2774 zoom-out. Unblock triggers: real incident on any `/api/ops/*` endpoint; new user-visible feature request touching ops; substrate concern from Rigby SIGN on a non-ops-adjacent arc.

- **N9** — dedicated `/api/ops/doc-preview/` endpoint (upgrade CCL v2 hover) — still no measured bandwidth signal AND now gated by ops-surface pause
- **N15** — session-open freshness verdicts persisted to JSONL — meta-observability for PLAYBOOK-7.4.4 trend detection. **Non-ops-surface — not gated.**
- **N17** — session_number pill in the search chip when text is set — small UX polish. **Non-ops-surface — not gated.**
- **N20** — access-logging enrichment for ops endpoints (Rigby S2772 meta-critique #4 refinement — never got its own N number). Would surface `user_id + query_params + duration + status` per ops call. **Trigger deferred** — auth_middleware already logs at INFO; not urgent while single-user AND now gated by ops-surface pause
- **N21 (new)** — `pa_local.sh` runtime user-check: verify token maps to a live user + surface username at first invocation of each session. Would have caught the S2774 chris/donkeyking wrapper drift in seconds. **Non-ops-surface — not gated.** (Feedback candidate mentioned in S2774 §8)

### Deferred (waiting on triggers, not just calendar)

- **N10** — partial-recycle UI badge on Recent Recycles rows (gated on observing at least one real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching — 7 clean N7 entries in a row now including S2774)
- **Q3 #5 (health_summary/ops_tool.overview overlap)** — trigger unchanged: first bug where UI tile and `ops_tool.overview` diverge on a factual claim
- **30+ other lambda-`__import__` sites in `core/urls.py`** (proposals, spider_api, agent_api, audio, tts, video) — no trigger yet. Same treatment as S2773 #3 got: refactor when a future arc naturally touches the surface, not proactive cleanup

### Housekeeping

- **Candidate 1** — S2761 smoke test `/api/ops/health-summary/` (~20m) — ops-surface, gated by pause
- **Candidate 2** — S2758 D2 canonical `AgentExecution` vs `AgentTaskExecution` decision (needs Rigby joint SIGN)
- **Candidate 3** — S2758 D4 HIGH-RISK task file wiring extension (REPORT-ONLY PR)
- **Candidate 4** — N13 handoff-date-format normalizer (hygiene one-shot)

### Still owed

- **P0.5** — Cost-threshold advance-to-freeze routing (owed since S2753)
- **P0.75** — CI billing status check
- **PA celery worker bounce** — Rigby stall fix #3119 still not activated
- **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1
- **S2758 D1 process_pa_chat_task payload strip** — deferred
- **S2758 D5 local shim retirement** — depends on D2 canonical decision
- **HMAC signing of `x-acting-user-id` header** — Phase 2 §6 limitation

### Post-S2766 owed

- **Memory rule promotion audit** — sweep MEMORY.md for two-trigger candidates for future MINOR amendments

---

## SESSION PIN — S2774 RETIRED (fresh mint required at S2775 open)

**Pin history (S2774):**

- `pa-206d3fa2f64d440b` (label `s2774-n19-ops-urlconf-lambda-cleanup`) minted S2774 open; **retired at S2774 close (force=true, FIFTH consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-206d3fa2f64d440b` (retired)** — intended failure mode forces S2775 first-action fresh mint.

**S2775 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2774 envelope §4 (Rigby SIGN summary) + §7 (forward-carry with pause discipline)
# Skim the S2774 close-ceremony bundle for the same-PR capstone fold pattern

# Freshness check. Should be FRESH · SHA-match at S2774 close SHA — NINTH close-cycle after PLAYBOOK-7.4.4 codification.
bash tools/pa_local.sh "S2775 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5 (should show S2774 close at top; all N7-enriched)"

# Regression check: run BOTH ops test suites locally (still green from S2774)
python manage.py test core.tests.test_ops_auth_regression_2772 core.tests.test_ops_query_param_allowlist_2773

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops
#   - Everything renders normally for you (staff)
#   - All 6 ops endpoints still return same shapes as pre-N19

# Mint fresh pin scoped to selected S2775 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

---

## OPEN RUNTIME ITEMS (from S2774 close)

1. **N9 / N15 / N17 / N20 / N21 net-new engineering** — see Candidates above
2. **S2761 smoke test** — ops-surface (gated)
3. **S2758 D2 canonical decision** — needs Rigby joint SIGN
4. **S2758 D4 HIGH-RISK wiring extension** — REPORT-ONLY
5. **N13 handoff-date-format normalizer** — hygiene one-shot
6. **P0.5 cost-threshold advance-to-freeze**
7. **P0.75 CI billing**
8. **PA celery worker bounce**
9. **RUR-C2 open eligible**
10. **S2758 D1 process_pa_chat_task payload strip**
11. **S2758 D5 local shim retirement**
12. **HMAC signing of `x-acting-user-id`**
13. **Memory rule promotion audit**
14. **First observed partial-recycle event** — trigger for N10 UI badge + first N11 tile fire
15. **Rigby S2774 forward-carry: pause ops-surface PRs** — unblock triggers listed under Net-new engineering §
16. **30+ other lambda-`__import__` sites** — refactor when future arc naturally touches
17. **Rigby S2773 forward-carry #5 (health_summary overlap)** — trigger unchanged
18. **Postgres cleanup follow-ups:**
    - Decide whether to `brew uninstall postgresql@16` (data preserved as archive)
    - Decide whether to drop pg15's `test_unified_donkey_betz` DB or leave for future test runs

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` — S2774 artifacts:**

- **Amended backend module:** `core/urls.py` (grouped import ~line 101 + 6 direct-callable path entries at 2402-2407)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-13_ops_urlconf_lambda_cleanup.md`
- **Handoff:** `docs/handoffs/SESSION_2774_OPS_URLCONF_LAMBDA_CLEANUP_RATIFIED.md`
- **Predecessor envelopes:** S2769 (CCL v2 filters), S2771 (text search + meta-critique origin + S2771 rule origin), S2772 (auth-regression), S2773 (param-allowlist + S2773 forward-carry #3 origin)
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2774
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** ops-console tab unchanged for staff; all 6 endpoints continue to work identically.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2774 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| Playbook rule count | 202 |
| RUR-C1 state | S2755→S2773 CLOSED · **S2774 N19 URLConf cleanup + same-PR capstone CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-206d3fa2f64d440b` (retired at S2774 close, force=true) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-206d3fa2f64d440b` (retired; forces fresh mint at S2775 open) |
| Live infra state | S2755→S2773 diagnostic infra + Playbook v0.6.0 + CCL v2 hover/drawer/filter/search + N7 recycle emitter + N11 PARTIAL_RECYCLE tile + N16 auth-regression suite + staff gate + N18v2 allowlist + helper refactor + date fix + **N19 URLConf cleanup** operational |
| Postgres :5432 | **pg15** (July DB, 382 migrations, S2774 state) — brew launchd `started`, survives reboot |
| Postgres pg16 | Parked (April fossil, data preserved on disk, plist unloaded) |
| Next move | Chris selects at S2775 open |

---

## Recommended session-open protocol (S2775)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2774 envelope §4 (Rigby SIGN summary with fourth consecutive S2771 rule application) + §7 (forward-carry with pause discipline)
4. Skim the S2774 close-ceremony bundle — first same-PR capstone fold as template
5. **Freshness + regression + browser eyeball** — see S2775 open sequence in §SESSION PIN above
6. If `staleness_verdict != FRESH` → escalate to Chris (ninth-cycle PLAYBOOK-7.4.4 violation OR possible first genuine PARTIAL_RECYCLE)
7. **Check `brew services list | grep postgres` FIRST** if freshness fails in unusual pattern (missing roles / stale conversations) — port-collision root cause is the fast path
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu with **at least one open-ended zoom-out ask in the Rigby SIGN** (per S2771 rule, validated 4 sessions in a row); consider **classifying zoom-out concerns as `same-PR-actionable` vs `future-trigger`** per S2774 novel precedent
10. Chris directs S2775 P0 selection
11. Mint fresh pin with candidate-scoped label
12. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2775:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L3 refreshed to S2774; L7 unchanged)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.6.0 (latest ratified)
3. [`docs/research/implementation/RATIFICATION_2026-07-13_ops_urlconf_lambda_cleanup.md`](docs/research/implementation/RATIFICATION_2026-07-13_ops_urlconf_lambda_cleanup.md) — S2774 envelope
4. [`docs/handoffs/SESSION_2774_OPS_URLCONF_LAMBDA_CLEANUP_RATIFIED.md`](docs/handoffs/SESSION_2774_OPS_URLCONF_LAMBDA_CLEANUP_RATIFIED.md) — S2774 handoff
5. [`docs/research/implementation/RATIFICATION_2026-07-12_ops_query_param_allowlist.md`](docs/research/implementation/RATIFICATION_2026-07-12_ops_query_param_allowlist.md) — S2773 predecessor
6. `core/urls.py` — amended this session (grouped import + 6 direct-callable paths)
7. `core/views_ops_console.py` — unchanged this session; policy docstring §3 still authoritative
