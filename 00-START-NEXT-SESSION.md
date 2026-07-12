# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2770 CLOSED — PARTIAL_RECYCLE VERDICT RATIFIED

**Refreshed 2026-07-11 (SESSION 2770 CLOSED — N11 shipped. `health_summary` composition now makes a fifth backend call to `recent_recycles` limit=1; verdict overrides to `PARTIAL_RECYCLE` when base is `STALE_*` AND newest recycle has `partial_recycle=true`. Frontend verdict enum extended additively; amber tile + warning row surfaces surviving processes. Closes the S2768 N7 evidence-to-alert loop. Fifth close-cycle post-PLAYBOOK-7.4.4-codification.)**

**S2770 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **`core/views_ops_console.py`** — `health_summary` gains `recent_recycles` sub-call + verdict override logic + conditional `partial_recycle_details` field. Typing imports added.
- **`frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`** — `OpsHealthSummary.verdict` extended with `'PARTIAL_RECYCLE'`; new optional `partial_recycle_details` field; amber tile color mapping; new warning row below tile header listing surviving_processes + recycle sha + "run `make recycle-all` to fix".
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_health_summary_partial_recycle.md`
- **Handoff:** `docs/handoffs/SESSION_2770_HEALTH_SUMMARY_PARTIAL_RECYCLE_RATIFIED.md`
- **CLAUDE.md L3 anchor:** refreshed to S2770; L7 constitutional anchor unchanged
- **Docs cascade:** 4-step + provenance rebuild
- **Post-merge:** `make recycle-all` invoked per PLAYBOOK-7.4.4 (fifth cycle)

---

## THE PIVOT — WHY THIS SHIP MATTERS

S2761 (base Ops Health tile) → S2765 (recycle timeline) → S2766 (PLAYBOOK-7.4.4 constitutional rule) → S2768 (N7 per-role recycle diff) → **S2770 (N11 evidence-to-alert loop closed).**

The recycle log has recorded per-role PID diffs since S2768. The `partial_recycle` boolean was purely informational — an operator would have had to scroll through JSONL to see it. As of N11, when the newest recycle was partial AND processes are still stale, the Ops Health tile turns AMBER and tells the operator exactly which processes survived, the recycle SHA involved, and what command to run.

**Verdict override is strict AND semantics:** the override never fires when the tile is already FRESH (no operator pain to surface) or UNKNOWN (nothing diagnosable). It fires only when both stale processes AND evidence of a partial recycle coincide. A subsequent clean recycle (partial=false in the newest event) automatically un-alarms.

**Live ledger:** three observability layers (Ops Health tile now amber-capable + Staleness Warnings + Recent Recycles with N7 enrichment) + one constitutional rule (PLAYBOOK-7.4.4) + one context-reload surface (CCL v2 with filter/search + hover-preview + drawer) + **one closed evidence-to-alert loop (N7 → N11)**.

---

## S2771 CANDIDATES (Chris selects at open)

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`; Workspace-scoped per `feedback_workspace_over_command_center_for_new_ui`)

- **N9** — Phase 2 dedicated `/api/ops/doc-preview/` endpoint (upgrade CCL v2 from full-doc-fetch to first-N-lines) — still no measured bandwidth signal
- **N12** — CCL v2 filter presets dropdown ("last 20", "this arc", "envelope-having only") — two-trigger threshold still not met
- **N13** — repo-wide handoff-date-format normalizer (backfill YAML `date:` on `**Date:**` handoffs) — one-shot hygiene script
- **N14 (new)** — CCL v2 full-text search across handoff bodies (grep for "PLAYBOOK-7.4.4" / "N7" / "tenant boundary" and see every session that mentions it). Small backend scan or index — pick during scoping.
- **N15 (new)** — session-open freshness verdicts persisted to a JSONL (like `recycle_events.jsonl`). Would let us detect trends over time — are cycles getting fresher or staler under PLAYBOOK-7.4.4?

### Deferred (waiting on signal)

- **N10** — partial-recycle UI badge on Recent Recycles rows (gated on observing at least one real partial in the log)
- **N11 aftermath** — first real PARTIAL_RECYCLE tile fire in the wild (watching)

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

## SESSION PIN — S2770 RETIRED (fresh mint required at S2771 open)

**Pin history (S2770):**

- `pa-fa4fcfa52f91490e` (label `s2770-health-summary-partial-recycle`) minted S2770 open; **retired at S2770 close**

**Wrapper `tools/pa_local.sh` still points at `pa-fa4fcfa52f91490e` (retired)** — intended failure mode forces S2771 first-action fresh mint.

**S2771 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read the S2770 envelope §4 (Rigby SIGN summary) + §5 (3-scenario simulation approach)
# Skim the amended health_summary composition + the amber tile mapping in OpsConsoleTab.tsx

# Freshness check. Should be FRESH · SHA-match at S2770 close SHA — this is the EIGHTH close-cycle since recycle-after-merge adopted and the FIFTH cycle AFTER PLAYBOOK-7.4.4 codification.
bash tools/pa_local.sh "S2771 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5 (should show S2770 close at top with N7 fields intact)"

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops
#   - Ops Health tile renders FRESH · green (unchanged happy path)
#   - No amber warning row visible (correct — no partial recycles observed yet)
#   - CCL v2 filter row still works (S2769)
#   - Recent Recycles top entry still shows N7 fields (S2768)

# Mint fresh pin scoped to selected S2771 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

---

## OPEN RUNTIME ITEMS (from S2770 close)

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
11. **N9 / N12 / N13 / N14 / N15 net-new engineering** — see Candidates above
12. **Memory rule promotion audit**
13. **First observed partial-recycle event** — trigger for N10 UI badge and first N11 tile fire

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` + `/frontend/` — S2770 artifacts:**

- **Amended backend view:** `core/views_ops_console.py::health_summary`
- **Amended frontend surface:** `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_health_summary_partial_recycle.md`
- **Handoff:** `docs/handoffs/SESSION_2770_HEALTH_SUMMARY_PARTIAL_RECYCLE_RATIFIED.md`
- **Predecessor envelopes:** S2761 (Ops Health tile), S2765 (recycle timeline), S2768 (N7 emitter), S2769 (CCL v2 filters) — same folder
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2770
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** `localhost:8000/workspace?tab=system&sub=ops` — Ops Health tile now amber-capable; PARTIAL_RECYCLE warning row will surface first partial recycle when it happens.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2770 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| Playbook rule count | 202 |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 Phase 3 stage 2 first pass CLOSED · S2755→S2769 diagnostic infra + operator surfaces + governance CLOSED · **S2770 PARTIAL_RECYCLE verdict CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-fa4fcfa52f91490e` (retired at S2770 close) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-fa4fcfa52f91490e` (retired; forces fresh mint at S2771 open) |
| Live infra state | S2755→S2769 diagnostic infra + Playbook v0.6.0 + CCL v2 hover/drawer/filter + N7 recycle emitter enriched + **N11 PARTIAL_RECYCLE tile alerting** operational |
| Next move | Chris selects at S2771 open |

---

## Recommended session-open protocol (S2771)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2770 envelope §4 (Rigby SIGN) + §5 (3-scenario `unittest.mock.patch` simulation approach — worth studying as a pattern for future override-logic tests)
4. Skim the amended `health_summary` composition + amber tile mapping
5. **Freshness + tile eyeball** — see S2771 open sequence in §SESSION PIN above
6. If `staleness_verdict != FRESH` → escalate to Chris (fifth-cycle PLAYBOOK-7.4.4 violation OR possible first genuine PARTIAL_RECYCLE — check for amber tile + warning row)
7. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
8. Present candidate menu to Chris (highlight N9/N12/N13/N14/N15 net-new leans)
9. Chris directs S2771 P0 selection
10. Mint fresh pin with candidate-scoped label
11. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2771:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L3 refreshed to S2770; L7 constitutional anchor unchanged)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.6.0 (latest ratified)
3. [`docs/research/implementation/RATIFICATION_2026-07-11_health_summary_partial_recycle.md`](docs/research/implementation/RATIFICATION_2026-07-11_health_summary_partial_recycle.md) — S2770 envelope (this session)
4. [`docs/handoffs/SESSION_2770_HEALTH_SUMMARY_PARTIAL_RECYCLE_RATIFIED.md`](docs/handoffs/SESSION_2770_HEALTH_SUMMARY_PARTIAL_RECYCLE_RATIFIED.md) — S2770 handoff
5. [`docs/research/implementation/RATIFICATION_2026-07-11_recycle_emitter_worker_pids.md`](docs/research/implementation/RATIFICATION_2026-07-11_recycle_emitter_worker_pids.md) — S2768 N7 predecessor
6. [`docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_search_filter.md`](docs/research/implementation/RATIFICATION_2026-07-11_ccl_v2_search_filter.md) — S2769 predecessor
7. `core/views_ops_console.py::health_summary` — amended this session
8. `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — amended this session
