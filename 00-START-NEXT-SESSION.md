# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2767 CLOSED — CLOSE-CEREMONY LEDGER v2 RATIFIED

**Refreshed 2026-07-11 (SESSION 2767 CLOSED — N4 shipped. Frontend-only edit to `OpsConsoleTab.tsx`: `LedgerRow` component with hover-preview tooltip + click-to-open via lazy-loaded `DocumentViewer` drawer. Zero new backend routes — reuses the pre-existing public-by-design `/api/platform/doc-content/` endpoint (`auth_middleware.py:436`). First close-cycle after PLAYBOOK-7.4.4 codification: `make recycle-all` dogfooded successfully.)**

**S2767 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **`frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`** — new `LedgerRow` component (private, hover-preview + click-to-open behaviors); new `LazyDocumentViewer = lazy(...)` module-level import; new `DocContentResponse` interface + `PREVIEW_LINE_LIMIT/HOVER_DEBOUNCE_MS/PREVIEW_STALE_TIME_MS` constants; new `viewerDoc` state on `OpsConsoleTab`; Suspense-wrapped drawer at return root. Existing copy-path buttons demoted to small secondary chips.
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger_v2.md`
- **Handoff:** `docs/handoffs/SESSION_2767_CLOSE_CEREMONY_LEDGER_V2_RATIFIED.md`
- **CLAUDE.md L3 anchor:** refreshed to reference S2767; L7 constitutional anchor unchanged (Playbook v0.6.0 still latest ratified version)
- **Docs cascade:** 4-step complete (index → corpus → sync → embed) + provenance rebuild
- **Post-merge:** `make recycle-all` invoked per PLAYBOOK-7.4.4 (first cycle where recycle-after-merge is constitutional force, not just memory rule)

---

## THE PIVOT — WHY THIS SHIP MATTERS

S2745 established: bias net-new engineering over "audit what's built." The S2755→S2765 streak was diagnostic infra + operator surfaces (still substrate, but user-visible). S2766 was a Playbook amendment (docs-only). **S2767 broke back to net-new UI at the very next open** — hover-preview + click-to-open transforms the Recent Close-Ceremonies section from a copy-path list into a fast context re-load surface.

**Second-order:** this is the first close-cycle where PLAYBOOK-7.4.4 is CONSTITUTIONAL, not memory. Every close-ceremony PR from now on MUST end with `make recycle-all` unless the merge diff qualifies for the mechanical waiver (docs/frontend-only merges). S2767 is frontend-only and thus WAIVER-ELIGIBLE — but we invoked the recycle anyway to accumulate a corroboration data point on the rule under its post-codification dogfooding scope.

**Live ledger:** three observability layers govern stale-process triage (Ops Health tile + Staleness Warnings + Recent Recycles) + one constitutional rule requiring the recycle timing (PLAYBOOK-7.4.4) + one operator surface for post-session context re-load (Recent Close-Ceremonies v2 with hover-preview + drawer nav).

---

## S2768 CANDIDATES (Chris selects at open)

### Net-new engineering (⭐ recommended first per `feedback_engineering_bias_over_audit`)

- **N6** — Command Center home tile mirror of Ops Health (3-card grid at Workspace Home)
- **N7** — extend `recycle-all` emitter with worker PIDs before/after; use this to detect partial recycles
- **N8 (new)** — Recent Close-Ceremonies row search / filter (by session number range, envelope-only, date range) — surfaces the value of v2 further as the ledger grows past 10 entries
- **N9 (new)** — Post-S2767 Phase 2 candidate — dedicated `/api/ops/doc-preview/` endpoint returning only first N lines (upgrade from Option A to Option B once measured hover-storm bandwidth justifies it)

### Housekeeping

- **Candidate 1** — S2761 smoke test `/api/ops/health-summary/` (~20m)
- **Candidate 2** — S2758 D2 canonical AgentExecution vs AgentTaskExecution decision (needs Rigby joint SIGN)
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

- **Memory rule promotion audit** — sweep MEMORY.md for other operator memories that have hit the two-triggers threshold and could be candidates for future MINOR amendments. Not urgent; future arc-close closeout item.

---

## SESSION PIN — S2767 RETIRED (fresh mint required at S2768 open)

**Pin history (S2767):**

- `pa-d2f1f7bd302f47d2` (label `s2767-close-ceremony-ledger-v2`) minted S2767 open; **retired at S2767 close**

**Wrapper `tools/pa_local.sh:539` still points at `pa-d2f1f7bd302f47d2` (retired)** — intended failure mode forces S2768 first-action fresh mint.

**S2768 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read the S2767 envelope §4 (Rigby SIGN summary) + §5 (empirical smoke tests)
# Skim the new LedgerRow component in frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx (~150 lines added)

# Freshness check + tile eyeball. Should be FRESH · SHA match at S2767 close SHA — this is the FIFTH close-cycle since the recycle-after-merge convention adopted (SECOND cycle AFTER codification).
bash tools/pa_local.sh "S2768 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5 (should show S2767 close + S2766 close + S2765 close as top three entries)"

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops
#   - verify existing sections still render (Ops Health tile, SLO, Signatures, Blocked, Recent Recycles)
#   - hover a Recent Close-Ceremonies row → tooltip with first 10 lines
#   - click a row → DocumentViewer drawer opens with handoff
#   - click envelope chip → drawer opens with envelope
#   - copy chips still copy paths (regression check)

# Mint fresh pin scoped to selected S2768 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

---

## OPEN RUNTIME ITEMS (from S2767 close)

Same as S2767 close open items, with N4 removed (shipped) and two additions:

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
11. **N6 / N7 / N8 / N9 net-new engineering** — see Candidates above
12. **Memory rule promotion audit** — sweep for MINOR amendment candidates

---

## Twin-pointer card

📁 **Repo `/docs/` + `/frontend/` — S2767 artifacts:**

- **Frontend edit:** `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` (LedgerRow + LazyDocumentViewer + Suspense)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger_v2.md`
- **Handoff:** `docs/handoffs/SESSION_2767_CLOSE_CEREMONY_LEDGER_V2_RATIFIED.md`
- **Predecessor envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md` (S2763 v1)
- **DocumentViewer component:** `frontend/src/components/platform/DocumentViewer.tsx` (S818, reused unchanged)
- **doc-content backend:** `core/views_platform_command.py:1226` (S818, reused unchanged)
- **Auth-exempt registration:** `core/auth_middleware.py:436`
- **Playbook constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2767
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** `localhost:8000/workspace?tab=system&sub=ops` — Recent Close-Ceremonies section now hover-previewable + click-to-open

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2767 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| Playbook rule count | 202 |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 Phase 3 stage 2 first pass CLOSED · S2755→S2766 diagnostic infra + operator surfaces + governance CLOSED · **S2767 close-ceremony ledger v2 CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-d2f1f7bd302f47d2` (retired at S2767 close) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-d2f1f7bd302f47d2` (retired; forces fresh mint at S2768 open) |
| Live infra state | S2755→S2766 diagnostic infra + operator surfaces + Playbook v0.6.0 + **S2767 CCL v2 hover-preview + docs viewer nav** operational |
| Next move | Chris selects at S2768 open — see Candidates above |

---

## Recommended session-open protocol (S2768)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2767 envelope `RATIFICATION_2026-07-11_close_ceremony_ledger_v2.md` §4 (Rigby SIGN) + §5 (empirical smoke tests)
4. Skim the new `LedgerRow` component in `OpsConsoleTab.tsx` (~150 lines added)
5. **Freshness + findings + tile eyeball (single-round-trip)** — see S2768 open sequence in §SESSION PIN above
6. If `staleness_verdict != FRESH` → **rule violation of PLAYBOOK-7.4.4 the second session after codification; escalate to Chris**
7. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
8. Present candidate menu to Chris (highlight N6/N7/N8/N9 net-new leans)
9. Chris directs S2768 P0 selection
10. Mint fresh pin with candidate-scoped label
11. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2768:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L3 refreshed to S2767; L7 constitutional anchor unchanged at Playbook v0.6.0)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.6.0 (latest ratified)
3. [`docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger_v2.md`](docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger_v2.md) — S2767 envelope (this session)
4. [`docs/handoffs/SESSION_2767_CLOSE_CEREMONY_LEDGER_V2_RATIFIED.md`](docs/handoffs/SESSION_2767_CLOSE_CEREMONY_LEDGER_V2_RATIFIED.md) — S2767 handoff
5. [`docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md`](docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md) — S2763 v1 envelope (predecessor)
6. [`docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_6_0.md`](docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_6_0.md) — Playbook v0.6.0 envelope (constitutional context for the recycle rule)
7. `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — Ops Console tab (edited this session)
8. `frontend/src/components/platform/DocumentViewer.tsx` — reused unchanged
9. `core/views_platform_command.py` — `doc_content_view` reused unchanged
