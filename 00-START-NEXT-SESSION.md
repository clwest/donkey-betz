# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2773 CLOSED — OPS QUERY-PARAM ALLOWLIST + REFACTOR + DATE FIX RATIFIED

**Refreshed 2026-07-12 (SESSION 2773 CLOSED — N18v2 shipped (Chris-approved scope expansion from N18). `close_ceremony_ledger` + 5 sibling ops endpoints now enforce query-param allowlist with 400 + `code='unknown_query_params'` body. `_call_ops_tool` helper replaces 4-copy `_Proxy` boilerplate. `_parse_date_param` uses `datetime.date.fromisoformat` (fixes silent bug that accepted `2026-99-99`). 22 new tests + 15 S2772 tests = 37/37 PASS. Rigby zoom-out (third application of S2771 rule) surfaced 5 concerns; 3 shipped same-PR. Eighth close-cycle post-PLAYBOOK-7.4.4-codification.)**

**S2773 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1), 4 clean commits on branch (per Rigby Q4), squash-merged:**

- **Commit 1:** extract `_call_ops_tool` helper (Rigby Q3 #1, zero behavior change)
- **Commit 2:** allowlist constants + `_reject_unknown_query_params` helper wired into all 6 endpoints (Rigby Q3 #2 + Q1 MODIFY body shape)
- **Commit 3:** `_parse_date_param` calendar validation via `fromisoformat` (Rigby Q3 #4 correctness fix)
- **Commit 4:** new test file `test_ops_query_param_allowlist_2773.py` (22 tests, Rigby Q2 MODIFY charter separation)

- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-12_ops_query_param_allowlist.md`
- **Handoff:** `docs/handoffs/SESSION_2773_OPS_QUERY_PARAM_ALLOWLIST_RATIFIED.md`
- **CLAUDE.md L3 anchor:** refreshed to S2773; L7 unchanged
- **Docs cascade:** 4-step + provenance rebuild
- **Post-merge:** `make recycle-all` invoked per PLAYBOOK-7.4.4 (eighth cycle)

---

## THE PIVOT — WHY THIS SHIP MATTERS

Substrate hardening arc continues. S2772 shipped auth-regression tests + staff gate on the auth boundary. S2773 ships the query-param boundary: every `/api/ops/*` endpoint now rejects unknown query params with a machine-stable `code`. The debug shortcut `?raw=1` that Rigby warned about in S2771 meta-critique is now impossible without a code change + test update.

Simultaneously: `_call_ops_tool` cleans up 4x-duplicated `_Proxy` boilerplate (Rigby zoom-out #1), and `_parse_date_param` gets real calendar validation (Rigby zoom-out #4 — real bug that had lived from S2769 through S2772). These weren't in the original N18 scope; they landed because Chris D-verdict'd on Rigby's zoom-out.

**Meta:** third consecutive application of the S2771 workflow rule. Rigby's SIGN keeps producing 5-7 substantive concerns per session when I include an open-ended zoom-out ask. The pattern is stable: ~3 concerns ship same-PR, remainder forward-carry with explicit trigger criteria. No sign of the rule aging into ritual.

---

## S2774 CANDIDATES (Chris selects at open)

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

- **N9** — dedicated `/api/ops/doc-preview/` endpoint (upgrade CCL v2 hover) — still no measured bandwidth signal
- **N15** — session-open freshness verdicts persisted to JSONL — meta-observability for PLAYBOOK-7.4.4 trend detection
- **N17** — session_number pill in the search chip when text is set — small UX polish
- **N19 (new)** — URLConf lambda `__import__` cleanup for `/api/ops/*` routes (Rigby S2773 zoom-out #3 forward-carry). Refactor 6 lambda-imports to direct imports. **Trigger already met** — natural pairing with next arc touching `core/urls.py` for ops.
- **N20 (new)** — access-logging enrichment for ops endpoints (Rigby S2772 meta-critique #4 refinement — never got its own N number). Would surface `user_id + query_params + duration + status` per ops call. **Trigger deferred** — auth_middleware already logs at INFO; not urgent while single-user.

### Deferred (waiting on triggers, not just calendar)

- **N10** — partial-recycle UI badge on Recent Recycles rows (gated on observing at least one real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching — 6 clean N7 entries in a row)
- **Q3 #3 (URLConf lambda tech debt)** — trigger: next arc touching `core/urls.py` for ops registration → now N19 above
- **Q3 #5 (health_summary/ops_tool.overview overlap)** — trigger: first bug where UI tile and `ops_tool.overview` diverge on a factual claim

### Housekeeping

- **Candidate 1** — S2761 smoke test `/api/ops/health-summary/` (~20m)
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

## SESSION PIN — S2773 RETIRED (fresh mint required at S2774 open)

**Pin history (S2773):**

- `pa-c15a7532e20b4fee` (label `s2773-ccl-query-param-allowlist`) minted S2773 open; **retired at S2773 close (force=true, fourth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-c15a7532e20b4fee` (retired)** — intended failure mode forces S2774 first-action fresh mint.

**S2774 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2773 envelope §4 (three-round SIGN pattern — design + zoom-out + implementation) + §7 (forward-carry with triggers)
# Skim the four commits on the merged branch — cleanest S2xxx close-ceremony structure to date

# Freshness check. Should be FRESH · SHA-match at S2773 close SHA — ELEVENTH close-cycle since recycle-after-merge adopted; EIGHTH cycle after PLAYBOOK-7.4.4 codification.
bash tools/pa_local.sh "S2774 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5 (should show S2773 close at top; all N7-enriched)"

# Regression check: run BOTH ops test suites locally
python manage.py test core.tests.test_ops_auth_regression_2772 core.tests.test_ops_query_param_allowlist_2773

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops
#   - Everything renders normally for you (staff)
#   - Curl an ops endpoint with ?debug=1 to see the 400 unknown_query_params response

# Mint fresh pin scoped to selected S2774 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

---

## OPEN RUNTIME ITEMS (from S2773 close)

1. **S2761 smoke test** — Candidate 1
2. **S2758 D2 canonical decision** — Candidate 2
3. **S2758 D4 HIGH-RISK wiring extension** — Candidate 3
4. **N13 handoff-date-format normalizer** — Candidate 4
5. **P0.5 cost-threshold advance-to-freeze**
6. **P0.75 CI billing**
7. **PA celery worker bounce**
8. **RUR-C2 open eligible**
9. **S2758 D1 process_pa_chat_task payload strip**
10. **S2758 D5 local shim retirement**
11. **HMAC signing of `x-acting-user-id`**
12. **N9 / N15 / N17 / N19 / N20 net-new engineering** — see Candidates above
13. **Memory rule promotion audit**
14. **First observed partial-recycle event** — trigger for N10 UI badge + first N11 tile fire
15. **Rigby S2773 forward-carry #3 (URLConf lambdas)** — now N19; **#5 (health_summary overlap)** — trigger set

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` — S2773 artifacts:**

- **Amended backend module:** `core/views_ops_console.py` (helper + allowlists + reject helper + date fix + policy docstring refresh)
- **New test file:** `core/tests/test_ops_query_param_allowlist_2773.py` (22 tests)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-12_ops_query_param_allowlist.md`
- **Handoff:** `docs/handoffs/SESSION_2773_OPS_QUERY_PARAM_ALLOWLIST_RATIFIED.md`
- **Predecessor envelopes:** S2769 (CCL v2 filters), S2771 (text search + meta-critique origin), S2772 (auth-regression + zoom-out validated first time)
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2773
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** ops-console tab unchanged for staff; 400 on unknown params for anyone probing.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2773 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| Playbook rule count | 202 |
| RUR-C1 state | S2755→S2772 CLOSED · **S2773 ops query-param allowlist + refactor + date fix CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-c15a7532e20b4fee` (retired at S2773 close, force=true) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-c15a7532e20b4fee` (retired; forces fresh mint at S2774 open) |
| Live infra state | S2755→S2772 diagnostic infra + Playbook v0.6.0 + CCL v2 hover/drawer/filter/search + N7 recycle emitter + N11 PARTIAL_RECYCLE tile + N16 auth-regression suite + staff gate + **N18v2 allowlist + helper refactor + date fix** operational |
| Next move | Chris selects at S2774 open |

---

## Recommended session-open protocol (S2774)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2773 envelope §4 (three-round SIGN pattern) + §7 (forward-carry with explicit triggers)
4. Skim the 4-commit history on the S2773 branch — cleanest close-ceremony structure to date
5. **Freshness + tile eyeball + BOTH ops test suites** — see S2774 open sequence in §SESSION PIN above
6. If `staleness_verdict != FRESH` → escalate to Chris (eighth-cycle PLAYBOOK-7.4.4 violation OR possible first genuine PARTIAL_RECYCLE)
7. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
8. Present candidate menu with **at least one open-ended zoom-out ask in the Rigby SIGN** (per S2771 rule, validated 3 sessions in a row)
9. Chris directs S2774 P0 selection
10. Mint fresh pin with candidate-scoped label
11. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2774:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L3 refreshed to S2773; L7 unchanged)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.6.0 (latest ratified)
3. [`docs/research/implementation/RATIFICATION_2026-07-12_ops_query_param_allowlist.md`](docs/research/implementation/RATIFICATION_2026-07-12_ops_query_param_allowlist.md) — S2773 envelope
4. [`docs/handoffs/SESSION_2773_OPS_QUERY_PARAM_ALLOWLIST_RATIFIED.md`](docs/handoffs/SESSION_2773_OPS_QUERY_PARAM_ALLOWLIST_RATIFIED.md) — S2773 handoff
5. [`docs/research/implementation/RATIFICATION_2026-07-12_ops_auth_regression_smoke_suite.md`](docs/research/implementation/RATIFICATION_2026-07-12_ops_auth_regression_smoke_suite.md) — S2772 predecessor
6. `core/views_ops_console.py` — amended this session (helper + allowlists + reject helper + date fix + policy docstring)
7. `core/tests/test_ops_query_param_allowlist_2773.py` — new this session
