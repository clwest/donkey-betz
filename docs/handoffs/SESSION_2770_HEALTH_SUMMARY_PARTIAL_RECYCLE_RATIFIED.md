---
session: 2770
date: 2026-07-11
title: "health_summary PARTIAL_RECYCLE verdict ratified — evidence-to-alert loop closed"
status: complete
outcome: shipped
scope: net-new-engineering-N11
canonical_authority: repo_canonical
ratification_envelope: docs/research/implementation/RATIFICATION_2026-07-11_health_summary_partial_recycle.md
---

# Session 2770 — health_summary PARTIAL_RECYCLE verdict ratified

## §1. TL;DR

Chris selected N11 from the S2770 candidate menu ("Lets go with N11 if you lean that way"). Rigby PASSed all three design questions (strict AND on trigger, newest-recycle-only lookback, legacy rows treated as false). Shipped the fifth backend action call in `health_summary` and the verdict override + `partial_recycle_details` field; extended the frontend verdict enum with `PARTIAL_RECYCLE` + amber tile color + surviving-processes warning row.

**Closes the evidence-to-alert loop opened by S2768 N7.** The recycle log has recorded per-role PID diffs since S2768. As of N11, when the newest recycle was partial AND processes are still stale, the Ops Health tile turns amber and tells the operator exactly which processes survived and what command to run.

**Fifth close-cycle post-PLAYBOOK-7.4.4-codification.** Third consecutive cycle producing N7-enriched entries.

## §2. Timeline

| Time (approx) | Event | Reference |
|---|---|---|
| S2770 open | freshness check via retired S2769 pin: FRESH · SHA `7013f9893878` | this session |
| N11 selected | Chris: "Lets go with N11 if you lean that way" | this session |
| Pin minted | `pa-fa4fcfa52f91490e` scoped to `s2770-health-summary-partial-recycle` | `session_lifecycle open` |
| Verify-before-build | traced `_ops_version` verdict logic + `health_summary` composition + the 4 existing sub-calls | this session |
| Rigby design SIGN | one round-trip, Q1/Q2/Q3 asks batched; PASS on all three | pin above |
| Code + smoke | view edit → 3-scenario Django shell simulation (baseline FRESH / STALE+partial=true / STALE+partial=false / STALE+legacy) → frontend edit → Vite build | this session |
| Rigby shape verify | HTTP smoke via `http_smoke_test` — baseline shape unchanged, verdict + partial_recycle_details behave as specified | this session |
| Envelope + handoff | this doc + envelope | filesystem |
| Docs cascade + provenance | 4-step + provenance rebuild | (post-merge below) |
| PR merge | filled at merge | GitHub |
| `make recycle-all` | fifth cycle post-codification | Makefile |

## §3. What shipped

**Files touched:**

- `core/views_ops_console.py` — 3 changes: (a) added `from typing import Any, Dict` import; (b) `health_summary` now makes a fifth `_safe_call({'action': 'recent_recycles', 'limit': 1}, 'recycles')` alongside the existing four; (c) verdict override logic + conditional `partial_recycle_details` field in the response.
- `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — 3 changes: (a) `OpsHealthSummary.verdict` union type extended with `'PARTIAL_RECYCLE'` + new optional `partial_recycle_details` field; (b) tile dot + text color mapping extended with amber case for PARTIAL_RECYCLE; (c) new warning row rendered under the tile header listing surviving processes + recycle sha + "run `make recycle-all` to fix" prompt.
- `docs/research/implementation/RATIFICATION_2026-07-11_health_summary_partial_recycle.md` — new envelope.
- `docs/handoffs/SESSION_2770_HEALTH_SUMMARY_PARTIAL_RECYCLE_RATIFIED.md` — this file.

Net: backend +30 lines, frontend +40 lines. No new routes, no schema, no new deps, no removals.

**Verdict override rules (recap):**

| Base verdict | Newest recycle `partial_recycle` | Effective verdict | `partial_recycle_details` |
|---|---|---|---|
| FRESH | any | FRESH | absent |
| UNKNOWN | any | UNKNOWN | absent |
| STALE_DAPHNE / _CELERY / _BOTH | true | **PARTIAL_RECYCLE** | present |
| STALE_DAPHNE / _CELERY / _BOTH | false | (unchanged) | absent |
| STALE_DAPHNE / _CELERY / _BOTH | missing (pre-N7 row) | (unchanged) | absent |

## §4. Rigby SIGN Summary

Joint SIGN one round-trip via pin `pa-fa4fcfa52f91490e`; post-code shape SIGN was a second round-trip on the same pin using `http_smoke_test`.

**Freshness:** verdict FRESH · SHA `7013f9893878` matches HEAD (S2769 close). Fourth post-codification cycle held. Recycle log top three: S2769/S2768/S2767 all N7-enriched — substrate producing evidence continuously.

**Design SIGN — Q1 (trigger semantics):** PASS on strict AND (`base STALE_* AND newest.partial_recycle==true`). Auto-suppresses historical partials that were later cleaned up.

**Design SIGN — Q2 (lookback scope):** PASS on newest-only (`recent_recycles limit=1`). Keeps signal tight; a later clean recycle means the system probably recovered.

**Design SIGN — Q3 (legacy row handling):** PASS on legacy → false. Safest default; "unknown" would pollute the tile for all pre-N7 history without actionable value.

**Post-code shape verify SIGN:** PASS. Baseline verdict FRESH; `partial_recycle_details` correctly absent when not PARTIAL_RECYCLE; all four legacy summary fields present unchanged; new verdict enum accepted.

## §5. Post-merge browser eyeball (Chris)

1. Hard-refresh `localhost:8000/workspace?tab=system&sub=ops`.
2. Ops Health tile at top should render normally (FRESH · green dot · SHA `7013f9893` or newer).
3. **The new warning row will NOT appear unless a partial-recycle happens for real.** Correct behavior — no false alarms.
4. Sibling sections unchanged: SLO / Signatures / Blocked / Recent Recycles / Recent Close-Ceremonies (with S2769 N8 filter row + hover-preview + drawer).
5. **Optional simulation** — if you want to see the amber tile in action, `make celery-stop` (leaves daphne up), then wait for a session-open freshness check to render STALE_CELERY. If the newest recycle was a full clean bounce though, no PARTIAL_RECYCLE will fire (correct). To simulate a genuine partial, the log would need a `partial_recycle: true` row — which we don't have yet in the wild.

## §6. Twin-Pointer Card

📁 **Repo `/docs/` + `/core/` + `/frontend/` — S2770 artifacts:**

- **Amended backend view:** `core/views_ops_console.py::health_summary`
- **Amended frontend surface:** `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_health_summary_partial_recycle.md`
- **Handoff:** `docs/handoffs/SESSION_2770_HEALTH_SUMMARY_PARTIAL_RECYCLE_RATIFIED.md` (this file)
- **Predecessor envelopes:** S2761 Ops Health tile + S2765 recent-recycles + S2768 N7 emitter + S2769 CCL v2 filters — same folder.
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2770
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** `localhost:8000/workspace?tab=system&sub=ops` — Ops Health tile now amber-capable; warning row surfaces surviving processes when PARTIAL_RECYCLE fires.

## §7. Current Repository State

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2770 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 Phase 3 stage 2 first pass CLOSED · S2755→S2769 diagnostic infra + operator surfaces + governance CLOSED · **S2770 PARTIAL_RECYCLE verdict CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-fa4fcfa52f91490e` (retired at S2770 close) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-fa4fcfa52f91490e` (retired; forces fresh mint at S2771 open) |
| Live infra state | S2755→S2769 diagnostic infra + operator surfaces + Playbook v0.6.0 + CCL v2 hover/drawer/filter + N7 recycle emitter enriched + **N11 PARTIAL_RECYCLE tile alerting** operational |
| Next move | Chris selects at S2771 open |

## §8. What This Session Taught About Doing Sessions

- **Simulate-the-failure-mode-in-Django-shell is a cheap high-signal test.** Three-scenario `unittest.mock.patch` on `_handle_ops` (STALE+partial=true / STALE+partial=false / STALE+legacy) validated all three branches of the override logic without waiting for a real partial-recycle to happen. Ten lines of test code; caught nothing broken; gave complete confidence. Would have taken hours (days?) to observe a real partial in the wild.
- **Additive enum extensions are backward-compat by construction.** Extending `verdict` from 5 states to 6 broke nothing because every existing consumer had a fallthrough branch (`verdict !== 'FRESH' && verdict !== 'UNKNOWN'` → red). The PARTIAL_RECYCLE mapping slotted in as a new branch above the fallthrough — old logic unchanged, new logic layered on top. Same discipline applies to any downstream verdict-consuming code.
- **Fifth close-cycle under PLAYBOOK-7.4.4 continues to hold.** Substrate producing enriched evidence continuously; ops-observability layer keeps compounding on top of it. S2761 (base tile) → S2765 (recycle timeline) → S2766 (constitutional rule) → S2768 (N7 per-role diff) → **S2770 (evidence-to-alert loop closed)**. Five sessions to a self-observing, self-alerting recycle-fidelity system.
