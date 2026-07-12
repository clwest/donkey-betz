# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2772 CLOSED — OPS AUTH-REGRESSION SUITE + STAFF GATE RATIFIED

**Refreshed 2026-07-12 (SESSION 2772 CLOSED — N16 shipped. `/api/ops/*` endpoints now require `is_staff` alongside `@login_required`; module policy docstring codifies 6-rule ops-endpoint scope; 15 Django tests lock the contract. Rigby's Q3 open-ended zoom-out — first application of S2771 workflow rule — produced 7 substantive concerns; 3 shipped same-PR (docstring policy + staff gate + inventory guard), 4 forward-carry with explicit triggers. Seventh close-cycle post-PLAYBOOK-7.4.4-codification.)**

**S2772 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **`core/views_ops_console.py`** — module-level ops-endpoint scope policy docstring (Rigby Q3 #1); new `_ops_staff_only` decorator (Rigby Q3 #2, Chris-approved); `@_ops_staff_only` added on all 6 endpoints.
- **`core/tests/test_ops_auth_regression_2772.py`** (new) — 15 tests: 6 anon-blocks + 6 non-staff-blocks + 1 staff-happy-path canary + 2 route-inventory guards (Rigby Q3 #7). All pass in 0.581s.
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-12_ops_auth_regression_smoke_suite.md`
- **Handoff:** `docs/handoffs/SESSION_2772_OPS_AUTH_REGRESSION_SMOKE_SUITE_RATIFIED.md`
- **CLAUDE.md L3 anchor:** refreshed to S2772; L7 unchanged
- **New memory:** `feedback_zoom_out_ask_per_rigby_sign.md` — validated on first use
- **Docs cascade:** 4-step + provenance rebuild
- **Post-merge:** `make recycle-all` invoked per PLAYBOOK-7.4.4 (seventh cycle)

---

## THE PIVOT — WHY THIS SHIP MATTERS

Two intertwined ships:

**Primary — substrate hardening.** Rigby's S2771 meta-critique #4 flagged that `/api/ops/*` endpoints accumulate visibility and drift into "debug everything." N16 ships the concrete mitigation: staff gate on all 6 endpoints + policy docstring + 15 auth-regression tests. Test-shipping session breaks the S2755→S2771 operator-surface streak. Non-admin users (when they arrive) will no longer see ops data.

**Meta — S2771 workflow rule validated on first use.** The "open-ended zoom-out ask per Rigby SIGN" discipline (introduced at S2771 close after Chris observed drift) produced 7 substantive concerns on the Q3 fold — the largest single SIGN response of the arc. 2 shipped same-PR (docstring + inventory guard), 1 escalated to Chris same-turn (staff gate — approved), 4 recorded as forward-carry with EXPLICIT trigger criteria (not "someday"). Rule saved as `feedback_zoom_out_ask_per_rigby_sign.md`.

**Live ledger:** three observability layers + one constitutional rule + one context-reload surface (CCL v2 hover/drawer/filter/search) + one evidence-to-alert loop (N7 → N11 tile alert) + **one hardened auth boundary (N16 staff gate + inventory guard tests)**.

---

## S2773 CANDIDATES (Chris selects at open)

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`; Workspace-scoped per `feedback_workspace_over_command_center_for_new_ui`)

- **N9** — dedicated `/api/ops/doc-preview/` endpoint (Phase 2 upgrade of CCL v2 hover)
- **N15** — session-open freshness verdicts persisted to JSONL (like `recycle_events.jsonl`) — meta-observability for PLAYBOOK-7.4.4 trend detection
- **N17** — session_number pill in the search chip when text is set — small UX polish for N14
- **N18 (new — Rigby Q3 #4 addressable)** — explicit query-param allowlist for `close_ceremony_ledger`; reject unknown params with 400. Companion to N16's staff gate — closes another exfiltration vector.

### Deferred (waiting on triggers, not just calendar)

- **N10** — partial-recycle UI badge on Recent Recycles rows (gated on observing at least one real partial-recycle event in `logs/recycle_events.jsonl`)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #3 (health-summary sub-call composition)** — trigger: future ops endpoint that composes another's REST route rather than handler function
- **Q3 #4 (query-param allowlist)** — trigger: 2nd endpoint reaching ≥4 optional params. `close_ceremony_ledger` already has 7 — reconsider addressing now via N18.
- **Q3 #5 (search DoS/injection limits)** — trigger: first observed high-freq operator search OR 2nd search endpoint
- **Q3 #6 (access logging)** — trigger: 2nd staff user grant

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

## SESSION PIN — S2772 RETIRED (fresh mint required at S2773 open)

**Pin history (S2772):**

- `pa-6ca91be75701425f` (label `s2772-ops-auth-regression-smoke`) minted S2772 open; **retired at S2772 close (force=true required per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-6ca91be75701425f` (retired)** — intended failure mode forces S2773 first-action fresh mint.

**S2773 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2772 envelope §4 (Rigby SIGN summary — note the zoom-out fold pattern) + §7 (forward-carry with explicit triggers)
# Skim the module policy docstring + _ops_staff_only decorator in views_ops_console.py

# Freshness check. Should be FRESH · SHA-match at S2772 close SHA — this is the TENTH close-cycle since recycle-after-merge adopted and the SEVENTH cycle AFTER PLAYBOOK-7.4.4 codification.
bash tools/pa_local.sh "S2773 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5 (should show S2772 close at top; all N7-enriched)"

# Regression check: run the N16 test suite locally to confirm no drift
python manage.py test core.tests.test_ops_auth_regression_2772 -v 2

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops
#   - You (Chris, is_staff=True) should still see everything normally
#   - If you happen to be logged out or in a different profile, ops calls return 401 (auth_middleware) or 302 (redirect)

# Mint fresh pin scoped to selected S2773 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

**Rigby retire pattern:** third consecutive `force=true` required (S2770/S2771/S2772). Rule is stable — see `feedback_session_tool_retire_needs_force_true`. Continue to phrase retire dispatches with `force=true` explicit.

---

## OPEN RUNTIME ITEMS (from S2772 close)

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
12. **N9 / N15 / N17 / N18 net-new engineering** — see Candidates above
13. **Memory rule promotion audit**
14. **First observed partial-recycle event** — trigger for N10 UI badge + first N11 tile fire
15. **Rigby S2772 Q3 #3-#6 forward-carry** — see Deferred (waiting on triggers)

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` — S2772 artifacts:**

- **Amended backend module:** `core/views_ops_console.py` (policy docstring + `_ops_staff_only` + 6 decorated endpoints)
- **New test file:** `core/tests/test_ops_auth_regression_2772.py` (15 tests)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-12_ops_auth_regression_smoke_suite.md`
- **Handoff:** `docs/handoffs/SESSION_2772_OPS_AUTH_REGRESSION_SMOKE_SUITE_RATIFIED.md`
- **Trigger context (S2771 meta-critique):** `docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_full_text_search.md`
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2772
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** ops-console tab unchanged in appearance for Chris (staff); non-staff users would now hit login-redirect.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2772 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| Playbook rule count | 202 |
| RUR-C1 state | S2755→S2771 diagnostic infra + operator surfaces + governance CLOSED · **S2772 ops-auth regression + staff gate CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-6ca91be75701425f` (retired at S2772 close, force=true) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-6ca91be75701425f` (retired; forces fresh mint at S2773 open) |
| Live infra state | S2755→S2771 diagnostic infra + Playbook v0.6.0 + CCL v2 hover/drawer/filter/search + N7 recycle emitter enriched + N11 PARTIAL_RECYCLE tile + **N16 auth-regression suite + staff gate** operational |
| Next move | Chris selects at S2773 open |

---

## Recommended session-open protocol (S2773)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2772 envelope §4 (Rigby SIGN — note the Q3 zoom-out fold pattern; this is the S2771 workflow rule in practice) + §7 (forward-carry with explicit triggers)
4. Skim the module policy docstring + `_ops_staff_only` decorator
5. **Freshness + tile eyeball + N16 test regression check** — see S2773 open sequence in §SESSION PIN above
6. If `staleness_verdict != FRESH` → escalate to Chris (seventh-cycle PLAYBOOK-7.4.4 violation OR possible first genuine PARTIAL_RECYCLE)
7. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
8. Present candidate menu with **at least one open-ended zoom-out ask in the Rigby SIGN** (per S2771 rule, S2772-validated)
9. Chris directs S2773 P0 selection
10. Mint fresh pin with candidate-scoped label
11. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2773:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L3 refreshed to S2772; L7 unchanged)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.6.0 (latest ratified)
3. [`docs/research/implementation/RATIFICATION_2026-07-12_ops_auth_regression_smoke_suite.md`](docs/research/implementation/RATIFICATION_2026-07-12_ops_auth_regression_smoke_suite.md) — S2772 envelope
4. [`docs/handoffs/SESSION_2772_OPS_AUTH_REGRESSION_SMOKE_SUITE_RATIFIED.md`](docs/handoffs/SESSION_2772_OPS_AUTH_REGRESSION_SMOKE_SUITE_RATIFIED.md) — S2772 handoff
5. [`docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_full_text_search.md`](docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_full_text_search.md) — S2771 (trigger for N16)
6. `core/views_ops_console.py` (module policy docstring + `_ops_staff_only`) — amended this session
7. `core/tests/test_ops_auth_regression_2772.py` — new this session (regression check pattern)
