# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2768 CLOSED — RECYCLE-ALL EMITTER ENRICHED WITH WORKER PIDS

**Refreshed 2026-07-11 (SESSION 2768 CLOSED — N7 shipped. New `scripts/emit_recycle_event.py` stdlib helper snapshots the 7 canonical worker pidfiles BEFORE and AFTER `make restart`, computes `partial_recycle` + `surviving_processes`, appends enriched JSONL to `logs/recycle_events.jsonl`. Reader handler `_ops_recent_recycles` passes new fields through when present; old rows still parse. Backward-compatible additive schema. Third close-cycle post-PLAYBOOK-7.4.4-codification.)**

**S2768 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **`scripts/emit_recycle_event.py`** (new, +190 lines) — stdlib-only, two subcommands: `snapshot` prints per-role pidfile PIDs to stdout; `emit --before <path>` snapshots after, computes partial + surviving, appends enriched JSONL. Includes defensive newline-prepend against truncated prior lines.
- **`Makefile`** (amended) — `recycle-all` drops the `restart` dependency; becomes sequential: `snapshot → $(MAKE) restart → emit`. Falls back to legacy S2765 printf shape if the Python script is missing.
- **`core/services/td_handlers_ops.py`** (amended, +12 lines in `_ops_recent_recycles`) — copies `pids_before / pids_after / partial_recycle / surviving_processes` from parsed events into the returned per-item dict when present.
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_recycle_emitter_worker_pids.md`
- **Handoff:** `docs/handoffs/SESSION_2768_RECYCLE_EMITTER_WORKER_PIDS_RATIFIED.md`
- **CLAUDE.md L3 anchor:** refreshed to reference S2768; L7 constitutional anchor unchanged
- **Docs cascade:** 4-step complete (index → corpus → sync → embed) + provenance rebuild
- **Post-merge:** `make recycle-all` invoked per PLAYBOOK-7.4.4 (third cycle) — first post-N7-merge recycle emits enriched entry into the log

---

## THE PIVOT — WHY THIS SHIP MATTERS

PLAYBOOK-7.4.4 requires post-merge recycle so workers match HEAD SHA. Before N7, the JSONL log recorded "recycle happened" but not "recycle succeeded per-role." A silently-failed worker restart would pass PLAYBOOK-7.4.4's evidence check while leaving a real stale process behind. N7 closes that gap — partial recycles become first-class facts in the log the constitutional rule uses as evidence.

The seven canonical roles (`daphne` + 5 celery workers + `celery_beat`) are the full local recycle set. Any role's PID matching before/after → surviving process → `partial_recycle: true`. Waivers still waive the rule; they don't redefine the invariant.

**Live ledger:** three observability layers (Ops Health tile + Staleness Warnings + Recent Recycles) + one constitutional rule (PLAYBOOK-7.4.4) + one operator surface for context re-load (Close-Ceremony Ledger v2) + **one machine-observable per-role recycle diff** (S2768 N7).

---

## S2769 CANDIDATES (Chris selects at open)

### Net-new engineering (⭐ recommended first per `feedback_engineering_bias_over_audit`; Workspace-scoped per `feedback_workspace_over_command_center_for_new_ui`)

- **N8** — CCL v2 row search / filter (session-range, envelope-only, date-range) — scales the ledger past 10 entries
- **N9** — Phase 2 dedicated `/api/ops/doc-preview/` endpoint (upgrade CCL v2 Option A → Option B once hover-storm bandwidth measurable)
- **N10 (new — first partial-recycle badge trigger)** — extend Ops Console Recent Recycles render with 🟡 badge on `partial_recycle=true` rows + hover-tooltip listing `surviving_processes`. Note: needs at least one observed partial-recycle entry in the log before shipping (two-trigger threshold for a UI change on a real signal). Watch for one across S2769–S2775 arc.
- **N11 (new)** — `ops_tool.health_summary` cross-reference: if the newest recycle has `partial_recycle=true` AND any process reports `started_before_head_commit=true`, surface as a distinct `PARTIAL_RECYCLE` verdict on the health tile (currently maps to `STALE_CELERY`/`STALE_DAPHNE`).

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

- **Memory rule promotion audit** — sweep MEMORY.md for other operator memories that have hit the two-triggers threshold and could be candidates for future MINOR amendments.

---

## SESSION PIN — S2768 RETIRED (fresh mint required at S2769 open)

**Pin history (S2768):**

- `pa-3cb29f52e461401a` (label `s2768-recycle-emitter-worker-pids`) minted S2768 open; **retired at S2768 close**

**Wrapper `tools/pa_local.sh` still points at `pa-3cb29f52e461401a` (retired)** — intended failure mode forces S2769 first-action fresh mint.

**S2769 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read the S2768 envelope §4 (Rigby SIGN) + §5 (smoke tests) — pay attention to §4.4 post-smoke verify
# Skim scripts/emit_recycle_event.py + the amended Makefile recycle-all body

# Freshness check + tile eyeball. Should be FRESH · SHA-match at S2768 close SHA — this is the SIXTH close-cycle since the recycle-after-merge convention adopted (THIRD cycle AFTER codification).
bash tools/pa_local.sh "S2769 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5 (should show S2768 close at top with new N7 fields, then S2767/S2766/S2765 in legacy shape)"

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops
#   - all existing sections still render (Ops Health tile, SLO, Signatures, Blocked, Recent Recycles, Recent Close-Ceremonies)
#   - Recent Recycles for the S2768 close entry should carry pids_before/pids_after/partial_recycle/surviving_processes in the JSON response (no UI badge yet — deferred per Q3)

# Mint fresh pin scoped to selected S2769 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

---

## OPEN RUNTIME ITEMS (from S2768 close)

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
11. **N8 / N9 / N10 / N11 net-new engineering** — see Candidates above
12. **Memory rule promotion audit**
13. **NEW (post-S2768) — first observed partial-recycle event** — trigger for N10 UI badge; watch the log across upcoming close-cycles

---

## Twin-pointer card

📁 **Repo `/docs/` + `/scripts/` + `/core/` + `Makefile` — S2768 artifacts:**

- **New helper script:** `scripts/emit_recycle_event.py`
- **Amended Makefile target:** `Makefile::recycle-all`
- **Amended reader handler:** `core/services/td_handlers_ops.py::_ops_recent_recycles`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_recycle_emitter_worker_pids.md`
- **Handoff:** `docs/handoffs/SESSION_2768_RECYCLE_EMITTER_WORKER_PIDS_RATIFIED.md`
- **Predecessor envelope (JSONL emitter):** `docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_recent_recycles.md` (S2765)
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2768
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** `localhost:8000/workspace?tab=system&sub=ops` — Recent Recycles section will surface new fields in the API response once the S2768-close row lands (no UI badge yet)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2768 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| Playbook rule count | 202 |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 Phase 3 stage 2 first pass CLOSED · S2755→S2767 diagnostic infra + operator surfaces + governance + CCL v2 CLOSED · **S2768 recycle emitter enriched CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-3cb29f52e461401a` (retired at S2768 close) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-3cb29f52e461401a` (retired; forces fresh mint at S2769 open) |
| Live infra state | S2755→S2767 diagnostic infra + operator surfaces + Playbook v0.6.0 + CCL v2 + **S2768 recycle emitter per-role PID diff** operational |
| Next move | Chris selects at S2769 open |

---

## Recommended session-open protocol (S2769)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2768 envelope `RATIFICATION_2026-07-11_recycle_emitter_worker_pids.md` §4 (Rigby SIGN) + §5 (smoke tests)
4. Skim `scripts/emit_recycle_event.py` + the amended Makefile `recycle-all`
5. **Freshness + findings + tile eyeball (single-round-trip)** — see S2769 open sequence in §SESSION PIN above
6. If `staleness_verdict != FRESH` → escalate to Chris (third-cycle PLAYBOOK-7.4.4 violation)
7. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
8. Present candidate menu to Chris (highlight N8/N9/N10/N11 net-new leans)
9. Chris directs S2769 P0 selection
10. Mint fresh pin with candidate-scoped label
11. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2769:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L3 refreshed to S2768; L7 constitutional anchor unchanged at Playbook v0.6.0)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.6.0 (latest ratified)
3. [`docs/research/implementation/RATIFICATION_2026-07-11_recycle_emitter_worker_pids.md`](docs/research/implementation/RATIFICATION_2026-07-11_recycle_emitter_worker_pids.md) — S2768 envelope (this session)
4. [`docs/handoffs/SESSION_2768_RECYCLE_EMITTER_WORKER_PIDS_RATIFIED.md`](docs/handoffs/SESSION_2768_RECYCLE_EMITTER_WORKER_PIDS_RATIFIED.md) — S2768 handoff
5. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_recent_recycles.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_recent_recycles.md) — S2765 predecessor envelope
6. [`docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_6_0.md`](docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_6_0.md) — Playbook v0.6.0 envelope (constitutional context)
7. `scripts/emit_recycle_event.py` — new helper (this session)
8. `Makefile` (recycle-all target) — amended this session
9. `core/services/td_handlers_ops.py::_ops_recent_recycles` — amended this session
