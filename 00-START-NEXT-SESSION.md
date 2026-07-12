# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2769 CLOSED — CCL v2 SEARCH + FILTER RATIFIED

**Refreshed 2026-07-11 (SESSION 2769 CLOSED — N8 shipped. `close_ceremony_ledger` view extended with 5 filter params + `total_available`; frontend gains compact filter row + "Show up to 50" expand button + empty-state card. Opportunistic fix: `_DATE_LINE_RE` broadened to accept YAML `date:` frontmatter (S2767+) alongside `**Date:**` markdown (older) — 3 recent sessions previously invisible to date filters. Fourth close-cycle post-PLAYBOOK-7.4.4-codification.)**

**S2769 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **`core/views_ops_console.py`** — `close_ceremony_ledger` accepts `session_min / session_max / envelope_only / date_from / date_to`; returns new `total_available`. `_parse_int_param` + `_parse_date_param` helpers extracted. `_DATE_LINE_RE` broadened.
- **`frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`** — new `LedgerFilters` state; compact filter row above Recent Close-Ceremonies; "showing X of Y matches" header; "Show up to 50" expand button; empty-state card. LedgerRow behavior unchanged (hover-preview + click-to-open drawer preserved).
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_search_filter.md`
- **Handoff:** `docs/handoffs/SESSION_2769_CCL_V2_SEARCH_FILTER_RATIFIED.md`
- **CLAUDE.md L3 anchor:** refreshed to S2769; L7 constitutional anchor unchanged (Playbook v0.6.0 still latest)
- **Docs cascade:** 4-step complete + provenance rebuild
- **Post-merge:** `make recycle-all` invoked per PLAYBOOK-7.4.4 (fourth cycle)

---

## THE PIVOT — WHY THIS SHIP MATTERS

The S2767 v2 ledger was capped at 10 rows. At 961 total handoffs on disk and growing ~1/session, every session past S2758 was invisible unless the operator hand-crafted a URL. N8 makes the surface durable — filter by session range or date, tick envelope-only, expand to 50 on demand.

Rigby verified the same 5 GET variants that Django shell smoke covered — count + `total_available` match on every one. The `total_available` field is the durable UX handle: any capped list surface should return both the returned count AND the pre-limit matching size so the UI can distinguish "you hit the exact set" from "there are more you can't see."

**Live ledger:** three observability layers (Ops Health tile + Staleness Warnings + Recent Recycles) + one constitutional rule (PLAYBOOK-7.4.4) + one operator surface for context re-load (CCL v2 with hover-preview + drawer + **now filter/search**) + one machine-observable per-role recycle diff (N7).

---

## S2770 CANDIDATES (Chris selects at open)

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`; Workspace-scoped per `feedback_workspace_over_command_center_for_new_ui`)

- **N9** — Phase 2 dedicated `/api/ops/doc-preview/` endpoint (upgrade CCL v2 from full-doc-fetch to first-N-lines) — still no bandwidth signal from CCL v2 hover; N8 filter may now drive more traffic worth measuring
- **N11** — `ops_tool.health_summary` cross-reference: if newest recycle has `partial_recycle=true` AND any process is stale, verdict = `PARTIAL_RECYCLE` (new tile state) — codes a branch for a not-yet-observed condition
- **N12 (new)** — CCL v2 filter presets dropdown ("last 20", "this arc", "envelope-having only") — depends on watching whether operator clicks "Show up to 50" then "clear" repeatedly (two-trigger threshold not met yet)
- **N13 (new)** — repo-wide handoff-date-format normalizer (`**Date:**` → YAML `date:`) as a one-off pass so future date-filter regexes stay simple — nice-to-have hygiene
- **N10 (deferred)** — partial-recycle UI badge — gated on observing at least one real partial-recycle event in the log

### Housekeeping

- **Candidate 1** — S2761 smoke test `/api/ops/health-summary/` (~20m)
- **Candidate 2** — S2758 D2 canonical `AgentExecution` vs `AgentTaskExecution` decision (needs Rigby joint SIGN)
- **Candidate 3** — S2758 D4 HIGH-RISK task file wiring extension (REPORT-ONLY PR)

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

## SESSION PIN — S2769 RETIRED (fresh mint required at S2770 open)

**Pin history (S2769):**

- `pa-465ff14a830f49f9` (label `s2769-ccl-v2-search-filter`) minted S2769 open; **retired at S2769 close**

**Wrapper `tools/pa_local.sh` still points at `pa-465ff14a830f49f9` (retired)** — intended failure mode forces S2770 first-action fresh mint.

**S2770 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read the S2769 envelope §4 (Rigby SIGN summary) + §5 (empirical smoke tests) — the 5-variant HTTP smoke pattern is worth studying
# Skim the amended close_ceremony_ledger view + the new filter row in OpsConsoleTab.tsx

# Freshness check. Should be FRESH · SHA-match at S2769 close SHA — this is the SEVENTH close-cycle since recycle-after-merge adopted and the FOURTH cycle AFTER PLAYBOOK-7.4.4 codification.
bash tools/pa_local.sh "S2770 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5 (should show S2769 close at top with N7 fields intact)"

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops
#   - filter row above Recent Close-Ceremonies renders
#   - type 2765 in session-min → "showing X of Y matches" appears
#   - tick envelope-only → intersection with any other active filter
#   - clear → returns to "last 10"

# Mint fresh pin scoped to selected S2770 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

---

## OPEN RUNTIME ITEMS (from S2769 close)

1. **S2761 smoke test** — Candidate 1
2. **S2758 D2 canonical decision** — Candidate 2
3. **S2758 D4 HIGH-RISK wiring extension** — Candidate 3
4. **P0.5 cost-threshold advance-to-freeze**
5. **P0.75 CI billing**
6. **PA celery worker bounce**
7. **RUR-C2 open eligible**
8. **S2758 D1 process_pa_chat_task payload strip**
9. **S2758 D5 local shim retirement**
10. **HMAC signing of `x-acting-user-id`**
11. **N9 / N11 / N12 / N13 net-new engineering** — see Candidates above
12. **Memory rule promotion audit**
13. **First observed partial-recycle event** — trigger for N10 UI badge

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` + `/frontend/` — S2769 artifacts:**

- **Amended backend view:** `core/views_ops_console.py::close_ceremony_ledger`
- **Amended frontend surface:** `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_search_filter.md`
- **Handoff:** `docs/handoffs/SESSION_2769_CCL_V2_SEARCH_FILTER_RATIFIED.md`
- **Predecessor envelopes:** S2763 v1 + S2767 v2 in the same folder
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2769
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** `localhost:8000/workspace?tab=system&sub=ops` — Recent Close-Ceremonies section now has filter row + "Show up to 50" expand

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2769 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| Playbook rule count | 202 |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 Phase 3 stage 2 first pass CLOSED · S2755→S2768 diagnostic infra + operator surfaces + governance CLOSED · **S2769 CCL v2 search+filter CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-465ff14a830f49f9` (retired at S2769 close) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-465ff14a830f49f9` (retired; forces fresh mint at S2770 open) |
| Live infra state | S2755→S2768 diagnostic infra + operator surfaces + Playbook v0.6.0 + CCL v2 hover-preview/drawer + N7 recycle emitter enriched + **CCL v2 search+filter** operational |
| Next move | Chris selects at S2770 open |

---

## Recommended session-open protocol (S2770)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2769 envelope `RATIFICATION_2026-07-11_ccl_v2_search_filter.md` §4 (Rigby SIGN) + §5 (smoke tests) — the 5-variant HTTP smoke pattern is worth studying
4. Skim the amended `close_ceremony_ledger` view + new filter row in `OpsConsoleTab.tsx`
5. **Freshness + tile eyeball (single-round-trip)** — see S2770 open sequence in §SESSION PIN above
6. If `staleness_verdict != FRESH` → escalate to Chris (fourth-cycle PLAYBOOK-7.4.4 violation)
7. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
8. Present candidate menu to Chris (highlight N9/N11/N12/N13 net-new leans)
9. Chris directs S2770 P0 selection
10. Mint fresh pin with candidate-scoped label
11. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2770:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L3 refreshed to S2769; L7 constitutional anchor unchanged)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.6.0 (latest ratified)
3. [`docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_search_filter.md`](docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_search_filter.md) — S2769 envelope (this session)
4. [`docs/handoffs/SESSION_2769_CCL_V2_SEARCH_FILTER_RATIFIED.md`](docs/handoffs/SESSION_2769_CCL_V2_SEARCH_FILTER_RATIFIED.md) — S2769 handoff
5. [`docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger_v2.md`](docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger_v2.md) — S2767 v2 predecessor
6. [`docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md`](docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md) — S2763 v1 predecessor
7. `core/views_ops_console.py::close_ceremony_ledger` — amended this session
8. `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — amended this session
