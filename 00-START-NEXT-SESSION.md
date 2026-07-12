# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2771 CLOSED — CCL v2 FULL-TEXT SEARCH RATIFIED

**Refreshed 2026-07-11 (SESSION 2771 CLOSED — N14 shipped. `close_ceremony_ledger` gains `text` query param + `text_match_count` per item + `applied_filters` echo + `skipped_count` (Rigby follow-up guardrails in same PR). Frontend filter row gains 200ms-debounced search input + match-count chip. 961 handoffs now grep-searchable. Sixth close-cycle post-PLAYBOOK-7.4.4-codification.)**

**S2771 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **`core/views_ops_console.py`** — text param with two-phase filter (cheap filters build set, then optional full-body text scan); response gains `applied_filters` echo dict + conditional `skipped_count` field (Rigby meta-critique addressed in same PR).
- **`frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`** — `LedgerFilters` extended with `text`; 200ms debounced text state; text input in the S2769 filter row; `text_match_count?: number` on `CloseCeremonyItem`; match-count chip in LedgerRow header.
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_full_text_search.md`
- **Handoff:** `docs/handoffs/SESSION_2771_CCL_V2_FULL_TEXT_SEARCH_RATIFIED.md`
- **CLAUDE.md L3 anchor:** refreshed to S2771; L7 unchanged
- **Docs cascade:** 4-step + provenance rebuild
- **Post-merge:** `make recycle-all` invoked per PLAYBOOK-7.4.4 (sixth cycle)

---

## THE PIVOT — WHY THIS SHIP MATTERS

Two intertwined ships in one PR:

**Primary:** N14 makes 961 handoffs searchable. When Chris (or Claude) asks "which sessions talked about PLAYBOOK-7.4.4?" the ledger answers in <1s. Case-insensitive substring; cheap filters run first for perf; hover-preview + drawer navigation from S2767 still work.

**Meta:** Chris asked "is Rigby rubber-stamping?" mid-session. Legitimate observation — 3 straight all-PASS SIGN cycles. Honest read: mostly (1) my proposals got sharper after S2767, (2) we're in a known groove, (3) Rigby has accumulated institutional model of what fits this codebase (Chris's insight), and (4) some rubber-stamp drift IS creeping in.

**Response:** solicited open-ended zoom-out critique from Rigby post-code. She raised 4 substantive concerns: unversioned params, silent fail-soft IO, prod topology assumptions, ops-surface security drift. Her concrete follow-up ask (`applied_filters` echo + `skipped_count`) shipped in the same PR — 8 backend lines, zero UI change. Structural concerns (#3 + #4) recorded as forward-carry.

**Lesson codified:** the quality of SIGN pushback is a function of the question asked. Three-fold design SIGN with well-articulated leans → PASSes. Open-ended zoom-out → 4 substantive concerns. Going forward, at least one dimension per session should be an open-ended zoom-out ask.

---

## S2772 CANDIDATES (Chris selects at open)

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`; Workspace-scoped per `feedback_workspace_over_command_center_for_new_ui`)

- **N9** — dedicated `/api/ops/doc-preview/` endpoint (Phase 2 upgrade of CCL v2 hover) — check if N14 traffic on `/api/platform/doc-content/` now produces a measurable bandwidth signal
- **N15** — session-open freshness verdicts persisted to JSONL (like `recycle_events.jsonl`) — meta-observability for PLAYBOOK-7.4.4 trend detection
- **N16 (new)** — ops-endpoint auth-regression smoke suite (Rigby meta-critique #4 mitigation) — assert every `/api/ops/*` returns 401 without auth; catches drift
- **N17 (new)** — session_number pill in the search chip when text is set — small UX polish for N14 (currently only match count shown)

### Deferred (waiting on signal)

- **N10** — partial-recycle UI badge on Recent Recycles rows (no observed real partial yet)
- **First real N11 PARTIAL_RECYCLE fire** (watching)
- **N12** — CCL v2 filter presets dropdown (two-trigger threshold still not met)
- **Prod-topology index** (Rigby meta-critique #3) — do NOT proactively build; wait for topology change or first "scan is slow" observation

### Housekeeping

- **Candidate 1** — S2761 smoke test `/api/ops/health-summary/` (~20m)
- **Candidate 2** — S2758 D2 canonical `AgentExecution` vs `AgentTaskExecution` decision (needs Rigby joint SIGN)
- **Candidate 3** — S2758 D4 HIGH-RISK task file wiring extension (REPORT-ONLY PR)
- **Candidate 4 (new)** — repo-wide handoff-date-format normalizer (N13 from S2769) — one-shot hygiene script; low urgency

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

## SESSION PIN — S2771 RETIRED (fresh mint required at S2772 open)

**Pin history (S2771):**

- `pa-bef24c8c42d3461c` (label `s2771-ccl-v2-full-text-search`) minted S2771 open; **retired at S2771 close (with force=true per S2770 observation)**

**Wrapper `tools/pa_local.sh` still points at `pa-bef24c8c42d3461c` (retired)** — intended failure mode forces S2772 first-action fresh mint.

**S2772 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read the S2771 envelope §4 (Rigby SIGN summary — note the meta-critique method) + §7 (forward-carry substrate concerns)
# Skim the two-phase filter body in close_ceremony_ledger + the 200ms debounce pattern in OpsConsoleTab.tsx

# Freshness check. Should be FRESH · SHA-match at S2771 close SHA — this is the NINTH close-cycle since recycle-after-merge adopted and the SIXTH cycle AFTER PLAYBOOK-7.4.4 codification.
bash tools/pa_local.sh "S2772 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5 (should show S2771 close at top; all N7-enriched)"

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops
#   - CCL v2 filter row still works; new 'search text…' input after date range
#   - Type PLAYBOOK-7.4.4 → row filter + N matches chip on each row
#   - clear button resets text along with other filters
#   - LedgerRow hover-preview + drawer still work (S2767 regression check)

# Mint fresh pin scoped to selected S2772 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

**Rigby retire observation:** at S2770 close and S2771 close, `session_tool.retire` refused to retire the currently-bound pin without `force=true`. Earlier close-cycles (S2767/S2768/S2769) succeeded without force. Behavior change observed but source unknown; workaround (`force=true`) is stable. Add to feedback memory if it recurs at S2772 close.

---

## OPEN RUNTIME ITEMS (from S2771 close)

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
12. **N9 / N15 / N16 / N17 net-new engineering** — see Candidates above
13. **Memory rule promotion audit**
14. **First observed partial-recycle event** — trigger for N10 UI badge + first N11 tile fire
15. **Rigby retire force-true behavior** — third occurrence → codify workaround
16. **Rigby meta-critique #3 (prod topology)** + **#4 (ops security drift)** — recorded as forward-carry

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` + `/frontend/` — S2771 artifacts:**

- **Amended backend view:** `core/views_ops_console.py::close_ceremony_ledger`
- **Amended frontend surface:** `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_full_text_search.md`
- **Handoff:** `docs/handoffs/SESSION_2771_CCL_V2_FULL_TEXT_SEARCH_RATIFIED.md`
- **Predecessor envelopes:** S2763 v1, S2767 v2 hover/drawer, S2769 v2 filters, S2770 N11 tile — same folder
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2771
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** `localhost:8000/workspace?tab=system&sub=ops` — full-text search now live; ops-console pattern at 6 consecutive shipped surfaces

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2771 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| Playbook rule count | 202 |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 Phase 3 stage 2 first pass CLOSED · S2755→S2770 diagnostic infra + operator surfaces + governance CLOSED · **S2771 CCL v2 full-text search CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-bef24c8c42d3461c` (retired at S2771 close, force=true) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-bef24c8c42d3461c` (retired; forces fresh mint at S2772 open) |
| Live infra state | S2755→S2770 diagnostic infra + Playbook v0.6.0 + CCL v2 hover/drawer/filter + N7 recycle emitter enriched + N11 PARTIAL_RECYCLE tile alerting + **N14 full-text search + applied_filters echo + skipped_count** operational |
| Next move | Chris selects at S2772 open |

---

## Recommended session-open protocol (S2772)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2771 envelope §4 (Rigby SIGN — note the meta-critique method for future sessions) + §7 (forward-carry substrate concerns #3 + #4)
4. Skim the two-phase filter body + 200ms debounce pattern
5. **Freshness + tile eyeball** — see S2772 open sequence in §SESSION PIN above
6. If `staleness_verdict != FRESH` → escalate to Chris (sixth-cycle PLAYBOOK-7.4.4 violation OR possible first genuine PARTIAL_RECYCLE)
7. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
8. Present candidate menu with **at least one open-ended zoom-out ask** in the Rigby SIGN (per S2771 lesson)
9. Chris directs S2772 P0 selection
10. Mint fresh pin with candidate-scoped label
11. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2772:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L3 refreshed to S2771; L7 constitutional anchor unchanged)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.6.0 (latest ratified)
3. [`docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_full_text_search.md`](docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_full_text_search.md) — S2771 envelope (this session)
4. [`docs/handoffs/SESSION_2771_CCL_V2_FULL_TEXT_SEARCH_RATIFIED.md`](docs/handoffs/SESSION_2771_CCL_V2_FULL_TEXT_SEARCH_RATIFIED.md) — S2771 handoff
5. [`docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_search_filter.md`](docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_search_filter.md) — S2769 predecessor
6. [`docs/research/implementation/RATIFICATION_2026-07-11_health_summary_partial_recycle.md`](docs/research/implementation/RATIFICATION_2026-07-11_health_summary_partial_recycle.md) — S2770 predecessor
7. `core/views_ops_console.py::close_ceremony_ledger` — amended this session
8. `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — amended this session
