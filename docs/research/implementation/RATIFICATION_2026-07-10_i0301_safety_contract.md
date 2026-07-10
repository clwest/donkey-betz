---
title: "I-0301 Failure-Data Safety Contract Ratification Record (2026-07-10)"
status: active
authority: ratification-record
session_added: 2742
ratification_date: 2026-07-10
ratifier: chris
routing: rigby-pa-chat SIGN + Chris direct in-session ratification
program_id: RUR
parent_arc: I-0301
parent_arc_workspace: fcd7e683-3bfe-4d35-9704-0e54dd587ea1
parent_arc_workspace_name: "RUR-C1 Tenant Boundary Lockdown"
parent_campaign: RUR-C1 (Tenant Boundary Lockdown)
parent_campaign_workspace: 638e9e90-47b4-4bd4-a872-bf16181cf3b5
parent_campaign_workspace_name: "Real User Readiness Campaign"
parent_program_doc: docs/research/implementation/real_user_readiness/CAMPAIGN.md
parent_program_ratification: docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md
phase_1_audit_ledger: 1ca36f84-ae40-415c-b482-768415d13fd9
ratified_document: docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md
ratified_document_head_at_ratification: 19e8c090
sign_sessions:
  - S2742 — Rigby SIGN-WITH-EDITS (11/12 PASS, 1 material amendment applied + 4 non-material tightenings)
supersedes: none (first I-0301 safety contract ratification)
superseded_by: (open; later revisions point here)
frozen: true
downstream_unlocks:
  - Phase 3 (HTTP Remediation) — I-0301 first code-touching phase
  - RUR-C2 (Async State + Fail-Loud + Traceability) — I-0400 arc slot
  - I-0302 (Object-Level Authorization) — RUR-C1 second child
  - I-0303 (Async Tenant-Boundary Enforcement) — RUR-C1 third child
---

# I-0301 Failure-Data Safety Contract Ratification Record

This file is the **frozen** canonical record of Chris's ratification of the I-0301 Failure-Data Safety Contract on 2026-07-10. It captures the ratified document, the Rigby SIGN cycle summary, the material amendment classification, and the four downstream unlocks that this ratification enables. It is append-only history; do NOT edit after commit.

Future revisions to the safety contract require a new ratification record dated on the amendment date, which references this record as its `supersedes` predecessor.

---

## §1. Context

- **Ratification date:** 2026-07-10 (America/Denver operator timezone)
- **Arc:** I-0301 (HTTP + AllowAny Surface Remediation + Failure-Data Safety Contract)
- **Parent campaign:** RUR-C1 (Tenant Boundary Lockdown)
- **Parent program:** RUR (Real User Readiness)
- **Ratified document:** [`failure_data_safety_contract.md`](tenant_boundary_lockdown/failure_data_safety_contract.md)
- **Ratified document HEAD at ratification:** `19e8c090` (the safety contract draft PR merge, post-Rigby-SIGN amendments applied)
- **Parent arc workspace:** `fcd7e683-3bfe-4d35-9704-0e54dd587ea1` (`RUR-C1 Tenant Boundary Lockdown`)
- **Parent campaign workspace:** `638e9e90-47b4-4bd4-a872-bf16181cf3b5` (`Real User Readiness Campaign`)
- **Phase 1 audit ledger deliverable:** `1ca36f84-ae40-415c-b482-768415d13fd9` in the arc workspace

---

## §2. Ratified Document Frontmatter Upgrade

The safety contract frontmatter was upgraded as part of this ratification:

| Field | Pre-ratification | Post-ratification |
|---|---|---|
| `status` | `draft` | `active` |
| `authority` | `contract-draft` | `contract-frozen` |
| `frozen` | (absent) | `true` |
| `session_ratified` | (absent) | `2742` |
| `ratification_date` | (absent) | `2026-07-10` |
| `ratifier` | (absent) | `chris` |
| `ratification_record` | (absent) | `docs/research/implementation/RATIFICATION_2026-07-10_i0301_safety_contract.md` |
| `phase` | `Phase 2` | `Phase 2 (CLOSED at ratification 2026-07-10)` |
| `frozen_on` | `(pending Chris ratification post-Rigby-SIGN-PASS)` | `2026-07-10` |
| `downstream_unlocks_on_freeze` | 3 items marked "may open" | 4 items marked "NOW UNBLOCKED" |

---

## §3. Rigby SIGN Cycle Summary

### Twelve-focus-area pressure-test (2026-07-10, S2742)

Overall verdict: **SIGN-WITH-EDITS** — 11 of 12 focus areas PASS; 1 material amendment required + 4 non-material tightenings applied.

**Focus areas and verdicts:**

| Check | Focus | Verdict |
|---|---|---|
| 1 | §1 Scope + Non-Scope boundary | PASS + one non-material clarification |
| 2 | §2 Governing Principles P1-P5 | PASS |
| 3 | §3.1 Permitted Fields (7 fields) | PASS + one non-material tightening |
| 4 | §3.2 Prohibited Content (14 items) | **FAIL on one item** — 1 MATERIAL amendment |
| 5 | §3.3 Length + Locale (500-char cap) | PASS |
| 6 | §4 reason_code enum (14 entries) | PASS + one non-material differentiator |
| 7 | §5 support_code format | PASS |
| 8 | §6 Operator envelope + tenant-scoped access | PASS — procedural alpha enforcement accepted |
| 9 | §7 Component coverage (6 sub-sections) | PASS + one non-material SSE clause |
| 10 | §8 Enforcement layering (4 layers) | PASS |
| 11 | §9 Regression suite schema | WEAK, not blocking — non-material tightenings |
| 12 | §10 Amendment discipline | PASS |

### Material amendment applied

**§3.2 Prohibited Content — unconditional prompts/conversation prohibition.**

Prior draft carried an ambiguous "unless explicitly classified as `safe` at the field level" clause. No such field-level classification mechanism exists anywhere in the contract, making the clause untestable and creating a loophole for silent "safe" reclassifications during Phase 3 implementation.

Rigby SIGN §4 verdict: FAIL. Amendment removes the loophole and makes prompts / conversation contents **unconditionally prohibited** in the user-facing envelope.

**Classification:** the amendment TIGHTENS the contract. It does NOT relax any protection. It does NOT change a D-verdict, program scope, dependency graph, hard gate, or Wave 1 authorization. It refines one prohibition line within the ratified constitutional envelope of the parent Real User Readiness campaign.

Applied in the ratified document at §3.2 with an inline note pointing at Rigby SIGN §4.

### Non-material tightenings applied

Per Rigby SIGN allowance, applied without Chris escalation:

1. **§1.1** — one sentence added noting 200-status async endpoints that encode failure in body are in-scope (avoids reader misinterpretation that "any non-2xx" means only non-2xx)
2. **§3.1 timestamp** — "server-generated" explicit (must not be echoed from client input)
3. **§4** — differentiator sentence between `invalid_input` (parse/schema failure) and `validation_error` (business-rule failure)
4. **§7.4** — Phase 3 must audit for SSE surfaces first; wrapper implementation mandatory only if any exist in alpha path
5. **§9.2** — regression suite tightened: JSON-schema allowlist validation is primary, regex substring checks are secondary defense-in-depth; UUID rule simplified from "foreign UUIDs" (harder to compute) to "no UUID anywhere in body" (stronger and simpler)

---

## §4. Downstream Unlocks

This ratification unblocks four independent downstream work streams. Each requires separate Chris authorization to open; ratification of this contract is the precondition, not the trigger.

### §4.1 — Phase 3: HTTP Remediation (I-0301, first code-touching phase)

Phase 3 opens I-0301's first implementation activity. Per the scoping §8:

- Replace `AllowAny` with `IsAuthenticated` for Bucket B endpoints (12)
- Apply minimal safe queryset scoping where scoping §7.1 allowance applies
- Delete or `DEBUG`-gate Bucket C endpoints (4 pending caller-graph proof)
- Base DRF exception handler + Django middleware + template overrides + regression suite scaffolding, all conforming to this contract
- `support_code` generation per §5 of this contract
- Regression suite `tests/security/test_failure_envelope_conformance.py` scaffolded + first tests pass
- CI-blocking on any conformance failure

Phase 3 is scoped to endpoints classified in the Phase 1 audit ledger (`1ca36f84-...`). Bucket A + A2 pass through with justification comments; Bucket D endpoints get evidence bundles before reclassification.

### §4.2 — RUR-C2 (Async State + Fail-Loud + Traceability) — I-0400 slot

Per parent CAMPAIGN §9.1 Boundary Before RUR-C2 Opens: RUR-C2 opens only when the failure-data safety contract is established AND Rigby SIGN-confirmed. Both conditions are now met at ratification.

RUR-C2 scope per parent CAMPAIGN §4:
- Canonical `OpsRunEvent` failure emission via decorator on top-20 volume tasks
- Standardize `PENDING → RUNNING → SUCCEEDED | FAILED | CANCELLED`
- Propagate `support_code + reason_code + trace_id` to UI **via error envelope conforming to this contract**
- Deterministic postcondition verification (Chris Q6 D-verdict)
- Scope EXCLUSION: SRE dashboards, infra metrics, platform-wide observability

The `trace_lookup` management command specified in §6.3 of this contract lives in RUR-C2 implementation scope.

### §4.3 — I-0302: Object-Level Authorization

RUR-C1 second child arc. Scope per parent CAMPAIGN §4:

- Prove ownership enforcement on Deliverable, Initiative, ChatConversation, AgentExecution, Document
- Via explicit permission logic OR verified queryset/service-layer scoping
- Per-model leakage tests

I-0302 remediation surfaces MUST conform to this contract when returning error responses.

### §4.4 — I-0303: Async Tenant-Boundary Enforcement

RUR-C1 third child arc. Scope per parent CAMPAIGN §4:

- Trusted user/workspace identity at task boundaries
- Re-verify ownership against committed DB state
- Reject unsafe/incomplete dispatches
- User-A → user-B negative tests

I-0303 remediation surfaces MUST conform to this contract when returning error responses to users (via the async status endpoints covered in §7.5 of this contract).

---

## §5. Not Unlocked by This Ratification

Explicit non-scope of this ratification (to prevent scope drift):

- Does NOT close RUR-C1 (parent needs all three children — I-0301 + I-0302 + I-0303 — to close per Chris Q2 D-verdict)
- Does NOT open Wave 2 (RUR-C3 Execution Convergence + RUR-C5 Channels Auth Hardening) — those still wait for Wave 1 close
- Does NOT authorize starting Phase 3 implementation without a Chris authorization step
- Does NOT authorize `trace_lookup` code-level RBAC — the alpha-level procedural fallback per §6.2.4 of the contract is accepted for alpha; code-level RBAC is a follow-on before self-serve
- Does NOT amend the parent CAMPAIGN.md (parent already contains the safety contract SIGN prerequisite at §9.1; no re-ratification of parent needed)
- Does NOT authorize implementation code in this session — Phase 3 remains a distinct Chris D-verdict

---

## §6. Cross-References

- **Ratified contract:** [`tenant_boundary_lockdown/failure_data_safety_contract.md`](tenant_boundary_lockdown/failure_data_safety_contract.md)
- **Parent arc scoping:** [`tenant_boundary_lockdown/I-0301_scoping.md`](tenant_boundary_lockdown/I-0301_scoping.md)
- **Parent campaign (constitutional):** [`real_user_readiness/CAMPAIGN.md`](real_user_readiness/CAMPAIGN.md)
- **Parent program ratification:** [`RATIFICATION_2026-07-10_real_user_readiness.md`](RATIFICATION_2026-07-10_real_user_readiness.md)
- **Phase 1 audit ledger deliverable:** `1ca36f84-ae40-415c-b482-768415d13fd9` in workspace `fcd7e683-3bfe-4d35-9704-0e54dd587ea1`
- **Sibling ratification records:**
  - `RATIFICATION_2026-07-06_first_queue.md` (Cycle 1 backlog band ratification, pre-RUR)
  - `RATIFICATION_2026-07-07_second_arc_I-0200.md` (RAG Corpus Substrate Maturity arc selection)
  - `RATIFICATION_2026-07-10_real_user_readiness.md` (parent program ratification, same date)

---

**End of I-0301 Failure-Data Safety Contract Ratification Record. This file is frozen; do NOT edit after commit.**
