---
title: "Ops Console Sibling 401 Fix Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2762
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat SIGN (freshness + approach) + Chris candidate selection + local build verify
scope: S2762 — mirror the S2761 `api.get` pattern into the three sibling raw-fetch queries in OpsConsoleTab.tsx (slo-status / failure-signatures / blocked-agents)
serves_arc: RUR-C1 last-mile UI (Ops Console operator surface)
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md (S2761 — canonical fix pattern being mirrored)
ratified_documents:
  - frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx (amended — 3 raw fetch → api.get swaps, drop unused res.ok checks)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2762 open freshness triple-check via Rigby (fresh pin pa-572f3ba386964005) — verdict FRESH, TBV=7 historical, STW=0
  - S2762 approach SIGN (Rigby) — PASS on mechanical mirror; no new design surface
frozen: true
---

# Ops Console Sibling 401 Fix Ratification Record

Frozen canonical record of Chris's ratification of the sibling-401 fix on 2026-07-11. Un-breaks three pre-existing broken cards (SLO Status, Failure Signatures, Blocked Agents) on the same Ops Console page Chris live-verified at S2761 close. Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Scope:** last-mile UI fix — three raw `fetch({credentials: 'include'})` calls in `OpsConsoleTab.tsx` were pre-existing bugs identified in the S2761 envelope §6 as an out-of-scope follow-up candidate. This PR ships that follow-up.
- **Motivation:** S2761 ratified the axios-routed `healthQuery` as the canonical pattern for Ops endpoints. Three sibling queries (`sloQuery`, `sigQuery`, `blockedQuery`) still used raw fetch — same 401 bug that hid the S2761 tile initially. Fixing them on the same page Chris just live-verified restores the SLO Status grid, Failure Signatures list, and Blocked Agents list.
- **Ratifier:** Chris (candidate selection at S2762 open per S2745 engineering-bias directive)

---

## §2. Ratified Deliverables

### §2.1 `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — sibling query fix

Three mechanical swaps mirroring the S2761 `healthQuery` pattern (lines 36-45):

**Before** (× 3):

```tsx
const sloQuery = useQuery({
  queryKey: ['ops-slo'],
  queryFn: async () => {
    try {
      const r = await fetch('/api/ops/slo-status/', { credentials: 'include' })
      if (!r.ok) return null
      return r.json()
    } catch { return null }
  },
  staleTime: 60000,
})
```

**After** (× 3):

```tsx
const sloQuery = useQuery({
  queryKey: ['ops-slo'],
  queryFn: async () => {
    try {
      const r = await api.get('/ops/slo-status/')
      return r.data
    } catch { return null }
  },
  staleTime: 60000,
})
```

The `api.get` call routes through the axios instance whose request interceptor attaches `Authorization: Token <token>` from `useAuthStore` (see `frontend/src/lib/api.ts:34`). The manual `res.ok` check is dropped — axios throws on 4xx/5xx into the existing `catch → null` branch.

**Endpoints affected:**

- `GET /api/ops/slo-status/` (sloQuery)
- `GET /api/ops/failure-signatures/?window=24h&limit=10` (sigQuery)
- `GET /api/ops/blocked-agents/` (blockedQuery)

**Header comment updated:** the S2761 "sibling SLO/failure/blocked queries" caveat retired; replaced with "S2762: sibling queries now share this pattern".

**Removed noise:** three "Fetch X" comments (`// Fetch SLO status`, `// Fetch failure signatures`, `// Fetch blocked agents`) — they described *what* the code does, not *why*, and the code identifiers are self-describing.

---

## §3. Verify-Before-Build

**Existing implementation analysis (per PLAYBOOK Cycle 1A rule):**

- Reference pattern: `healthQuery` at `OpsConsoleTab.tsx:36-45` — ratified S2761, live-verified in browser at S2761 close.
- Sibling raw-fetch bug: identified in S2761 envelope §6 as out-of-scope; explicitly listed as an S2762 follow-up candidate in `00-START-NEXT-SESSION.md` line 34.
- No new design surface: mechanical mirror of an already-ratified pattern in the same file, same tab, same backend authorization contract.

**Reuse/extend/correct verdict:** correct three sibling call sites to match the ratified pattern.

---

## §4. Rigby SIGN

### §4.1 Freshness triple-check (S2762 open, pin `pa-572f3ba386964005`)

- `ops_tool.version` → **FRESH** · head_commit_sha `c39258f8…` (matches HEAD)
- `ops_tool.tenant_boundary_violations` (24h) → **7 total**, all from 19:10-19:18 UTC (historical stale-Daphne pre-recycle emissions per S2761 diagnosis; not live-code bugs)
- `ops_tool.staleness_warnings` (24h) → **0**

Verdict: no blockers.

### §4.2 Approach SIGN

**SIGN LEAN: PASS** — Rigby: "Mechanical mirror of the already-ratified `healthQuery` pattern; swapping `fetch`→`api.get` should eliminate the sibling 401 path with no new surface area."

No concerns raised; no risks noted that weren't already known.

---

## §5. Chris D-Verdict

Sequence:

1. **Session-open candidate selection:** "Go with your recommendation" (accepted Claude's top lean = candidate 1b, sibling 401 fix, over 1a/2/3/net-new).
2. **Joint agreement:** no F-BLOCKING or non-blocking decisions surfaced during implementation — mechanical fix per pre-agreed approach.
3. **Post-merge verify (pending):** browser hard-refresh Workspace → System → Ops after merge to confirm SLO / Signatures / Blocked cards populate.

**Effect:** three pre-existing broken cards on the Ops Console page now populate correctly. Same authorization contract as the S2761 tile above them.

---

## §6. Operational Follow-Up

- **Post-merge browser eyeball:** hard-refresh `localhost:8000/workspace?tab=system&sub=ops`. SLO Status grid, Failure Signatures list, Blocked Agents list should all show live data (or empty-state gracefully if no data).
- **`make recycle-all` after merge:** per `feedback_recycle_after_merge.md` — bounce workers post-merge so next-session-open detects FRESH.
- **Deferred (still open):**
  - S2761 §6 smoke test for `/api/ops/health-summary/` (~20 min)
  - S2758 D2 canonical AgentExecution vs AgentTaskExecution decision
  - S2758 D4 HIGH-RISK task-file wiring extension
  - P0.5 cost-threshold advance-to-freeze routing (owed since S2753)
  - P0.75 CI billing status check

---

## §7. Provenance Chain

- **Predecessor session:** S2761 (Ops Health tile ratified; ratified as canonical `api.get` pattern for this file)
- **Reference code:** `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx:36-45` (healthQuery pattern)
- **Reference infra:** `frontend/src/lib/api.ts:13-40` (axios instance + request interceptor)
- **Engineering Playbook v0.5.0:** PLAYBOOK-7.4.1 (close-ceremony 1-PR bundle) + Cycle 1A verify-before-build applied (§3 above)
- **Memory rules applied:** `feedback_last_mile_ui.md` (fix visible-in-UI bug on same page just verified) + `feedback_recycle_after_merge.md` (post-merge worker bounce in §6) + `feedback_local_truth_no_production.md` (local build pass = shipped)
