---
title: "I-0301 Tenant Boundary Lockdown Arc Close Ratification Record (2026-07-10)"
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
ratified_document: docs/research/implementation/tenant_boundary_lockdown/I-030199_tenant_boundary_lockdown_implementation_close.md
ratified_document_head_at_ratification: d3a299fc
sign_sessions:
  - S2742 — Rigby close SIGN initial: SIGN-BLOCKED (3 material metric/arithmetic/terminology amendments); re-SIGN: SIGN-PASS
supersedes: none (first I-0301 arc-close ratification)
superseded_by: (open; not expected — frozen arc close)
frozen: true
arc_state:
  phase_1_audit_ledger: closed
  phase_2_safety_contract: closed (ratified)
  phase_3_http_remediation: closed
  phase_4_coverage_machinery: closed
  phase_5_arc_close: closed (this record)
  arc_status: CLOSED
downstream_unlocks:
  - RUR-C2 (Async State + Fail-Loud + Traceability) — I-0400 arc slot — UNBLOCKED at Phase 2 close, awaiting Chris authorization to open
  - I-0302 (Object-Level Authorization) — UNBLOCKED at Phase 2 close, awaiting Chris authorization to open
  - I-0303 (Async Tenant-Boundary Enforcement) — UNBLOCKED at Phase 2 close, awaiting Chris authorization to open
parent_campaign_close_gate:
  - RUR-C1 parent close requires I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression suite per Chris Q2 D-verdict at parent CAMPAIGN ratification
  - RUR-C1 remains OPEN post-I-0301-close
---

# I-0301 Tenant Boundary Lockdown Arc Close Ratification Record

This file is the **frozen** canonical record of Chris's ratification of the I-0301 arc close on 2026-07-10. It captures the ratified close doc, the Rigby SIGN cycle (block + re-SIGN PASS), the mutually-exclusive endpoint remediation taxonomy, the downstream unlocks activated, and the explicit non-unlocks recorded to prevent scope drift. It is append-only history; do NOT edit after commit.

---

## §1. Context

- **Ratification date:** 2026-07-10 (America/Denver operator timezone)
- **Arc:** I-0301 (HTTP + AllowAny Surface Remediation + Failure-Data Safety Contract)
- **Ratified document:** [`I-030199_tenant_boundary_lockdown_implementation_close.md`](tenant_boundary_lockdown/I-030199_tenant_boundary_lockdown_implementation_close.md)
- **Ratified document HEAD at ratification:** `d3a299fc` (draft close doc merge PR #3093)
- **Parent arc workspace:** `fcd7e683-3bfe-4d35-9704-0e54dd587ea1` (`RUR-C1 Tenant Boundary Lockdown`)
- **Parent campaign workspace:** `638e9e90-47b4-4bd4-a872-bf16181cf3b5` (`Real User Readiness Campaign`)
- **Prior state:** close doc was `status: draft` / `authority: arc-close-draft`. Ratification upgrades to `status: active` / `authority: arc-close-frozen` / `frozen: true`.

---

## §2. Ratified Document Frontmatter Upgrade

| Field | Pre-ratification | Post-ratification |
|---|---|---|
| `status` | `draft` | `active` |
| `authority` | `arc-close-draft` | `arc-close-frozen` |
| `frozen` | (absent) | `true` |
| `session_arc_ratified` | (absent) | `2742` |
| `arc_ratification_date` | (absent) | `2026-07-10` |
| `arc_ratifier` | (absent) | `chris` |
| `arc_ratification_record` | (absent) | this record's path |

---

## §3. Rigby SIGN Cycle Summary

### Initial verdict: SIGN-BLOCKED

10-item pressure test 2026-07-10 (S2742). Items 2, 3 (with wording nit), 4 (with correction nit), 5 (conceptually correct with mechanism care), 7, 8, 9, 10 all PASSED. Items 1 and 6 FAILED on material metric/arithmetic/terminology issues that would make Chris ratification misleading:

- **Item 1 fail:** "21 of 27 grep-caught AllowAny entry points hardened" was not consistent with the §3 metrics table below it. Included items that are not hardenings in the same sense (deletion, Bucket A retention, dead-code preserved).
- **Item 6 fail:** §3 endpoint remediation counts table had internally inconsistent categories, mixed "dead-gated" with "not routed" with "auth-gated" ambiguously, and did not present mutually-exclusive bins.

### Material amendments applied post-SIGN

1. **§1 executive summary rewritten** with mutually-exclusive taxonomy: 18 Remediated + 4 Deleted + 1 Intentionally Public + 4 Deferred = 27 grep-caught endpoints.
2. **§3 endpoint remediation counts rewritten** with clean bins (Remediated `AllowAny → IsAuthenticated` / Deleted / Intentionally Public / Deferred). Arithmetic verified: 27 grep-caught reconciled + 203 snapshot-AllowAny → 22 explicitly touched → 181 grandfathered.
3. **Terminology normalized:** "dead-gated" retired; nervous Status + agents `with_results` reframed as "remediated at source-level; not URL-routed (public-surface exposure zero either way)"; §5 "dead code preserved" reworded to "orphan classes."

Non-material tweaks:
- Phase 2 "3 material amendments" clarified as scoping-doc amendments not the Phase 2 contract amendment.
- Phase 3 Stage 2b PR B row rephrased away from Bucket C dead-gated confusion.
- Phase 4 mechanism dropped the specific `WrappedAPIView` name and softened to "function-based DRF views via `@api_view` + `@permission_classes` decorators."

### Re-SIGN verdict: SIGN-PASS

"No further edits required before Chris ratification."

None of the applied amendments changed a D-verdict, program scope, dependency graph, hard gate, or Wave 1 authorization. All were correctness fixes to the close-doc accounting shape.

---

## §4. Arc Outcome (Mutually-Exclusive Taxonomy)

### 27 grep-caught AllowAny entry points at HEAD `0825df46`

| Bin | Count | Endpoints |
|---|---|---|
| **Remediated** (`AllowAny → IsAuthenticated`) | 18 | 4 content_learning views (Stage 2a) + 7 intelligence views (Stage 2b PR A) + 4 nervous Feel/Vitals/History/Consumers (Stage 3 PR A) + 1 nervous Status (Stage 3 PR A; class attribute flipped even though not URL-routed) + 1 agents `get_permissions()` collapse (Stage 3 PR B) + 1 agents `@action` `with_results` override removal (Stage 2b PR B) |
| **Deleted** | 4 | 4 autonomous_system endpoints — view classes + URL routes + frontend `autonomousApi` calls all removed at Stage 3 PR A |
| **Intentionally Public** (`AllowAny` retained with justification) | 1 | nervous `IsResponsive` — Bucket A frozen with regression suite guardrails (constant-shape / no UUIDs / no version-queue-dependency hints) at Stage 3 PR A |
| **Deferred** (unchanged pre-existing state) | 4 | 2 sports viewsets Bucket A + 2 token-gated views Bucket A2 (public_changelog + public_intelligence) |

**Total: 18 + 4 + 1 + 4 = 27 ✓**

### 203 AllowAny in Phase 4 snapshot

- Total endpoints in `http_endpoint_snapshot.json`: 2,261
- AllowAny endpoints in snapshot: 203
- Delta vs 27 grep-caught: +176 (function-based DRF views via `@api_view` + `@permission_classes` decorators; class-attribute grep did not catch them)
- Explicitly touched by this arc: 22 (18 Remediated + 4 Deleted)
- **Grandfathered pre-existing AllowAny remaining: 181**

Drift test blocks NEW additions and NON-AllowAny → AllowAny regressions; does NOT force reclassification of the 181 grandfathered. Progressive classification is a follow-on program (not I-0301 scope).

---

## §5. Chris D-Verdict Package (2026-07-10 S2742)

Chris ratification-package items in close doc §8 accepted as reported:

1. **All Phase 1–4 outcomes as reported.** RATIFIED.
   - Phase 1 audit ledger (deliverable 1ca36f84 in workspace fcd7e683) with 27 endpoint denominator + bucket classification A=2/A2=2/B=12/C=4/D=7. Rigby SIGN-PASS.
   - Phase 2 safety contract (frozen) with 12 sections + 1 material amendment (§3.2 unconditional prompts prohibition). Rigby SIGN-WITH-EDITS then Chris-ratified.
   - Phase 3 HTTP remediation across 5 stages / 6 PRs (#3085, #3086, #3087, #3088, #3089, #3090). Rigby SIGN each stage.
   - Phase 4 Coverage Denominator Machinery (#3092) — 2,261 endpoints enumerated; 203 AllowAny grandfathered; drift test blocks new additions + hard-fails regressions.

2. **Follow-on scope §5 correctly recorded.** RATIFIED.
   - Stage 2c envelope unification (open follow-on)
   - 181 grandfathered AllowAny progressive classification (follow-on program)
   - NervousStatusView + AgentExecutionViewSet orphan class deletion (follow-on)
   - Non-DRF public views (718 `@csrf_exempt` in 106 files) audit stream (follow-on)
   - NervousHistoryView `id` field UUID exposure hardening (follow-on)
   - RUR-C6 `trace_lookup` code-level RBAC (follow-on before self-serve)

3. **Grandfathered 181 pre-existing AllowAny accepted as-is** with drift-blocked-going-forward posture. RATIFIED.

4. **Downstream unlock §6 correctly reflected.** RATIFIED. RUR-C1 parent close condition preserved (requires I-0301 + I-0302 + I-0303 per Chris Q2 D-verdict at parent CAMPAIGN ratification).

---

## §6. Downstream Unlocks

Each requires separate Chris authorization to open:

### §6.1 — RUR-C2 (Async State + Fail-Loud + Traceability) — I-0400 arc slot

**UNBLOCKED at Phase 2 close (2026-07-10).** Scope per parent CAMPAIGN §4:
- Canonical `OpsRunEvent` failure emission via decorator on top-20 volume tasks
- Standardize `PENDING → RUNNING → SUCCEEDED | FAILED | CANCELLED`
- Propagate `support_code + reason_code + trace_id` to UI via error envelope conforming to the I-0301 safety contract
- Deterministic postcondition verification (Chris Q6 D-verdict)
- `trace_lookup` management command implementation

### §6.2 — I-0302 Object-Level Authorization

**UNBLOCKED at Phase 2 close.** RUR-C1 second child arc. Scope per parent CAMPAIGN §4:
- Prove ownership enforcement on Deliverable, Initiative, ChatConversation, AgentExecution, Document
- Per-model leakage tests

I-0302 remediation surfaces MUST conform to the I-0301 safety contract when returning errors.

### §6.3 — I-0303 Async Tenant-Boundary Enforcement

**UNBLOCKED at Phase 2 close.** RUR-C1 third child arc.

I-0303 async status endpoints returning failure MUST conform to the I-0301 safety contract per §7.5 of the contract.

---

## §7. Not Unlocked by This Ratification

Explicit non-unlocks (scope drift prevention):

- Does NOT close RUR-C1 parent (needs I-0301 + I-0302 + I-0303 per Chris Q2 D-verdict at parent CAMPAIGN ratification)
- Does NOT open I-0302, I-0303, or RUR-C2 (each requires separate Chris authorization)
- Does NOT open any Wave 2 arc (RUR-C3 Execution Convergence + RUR-C5 Channels Auth Hardening still blocked on Wave 1 close, which requires RUR-C1 parent close)
- Does NOT open Wave 3 (RUR-C4 Idempotency + RUR-C6 Cost Enforcement)
- Does NOT open Wave 4 (RUR-C7 Golden Path Alpha validator)
- Does NOT authorize the follow-on programs recorded in §5 of the close doc
- Does NOT amend the ratified Failure-Data Safety Contract
- Does NOT change any element of the ratified parent CAMPAIGN.md

---

## §8. Cross-References

- Ratified close doc: [`tenant_boundary_lockdown/I-030199_tenant_boundary_lockdown_implementation_close.md`](tenant_boundary_lockdown/I-030199_tenant_boundary_lockdown_implementation_close.md)
- Parent arc scoping: [`tenant_boundary_lockdown/I-0301_scoping.md`](tenant_boundary_lockdown/I-0301_scoping.md)
- Safety contract (ratified): [`tenant_boundary_lockdown/failure_data_safety_contract.md`](tenant_boundary_lockdown/failure_data_safety_contract.md)
- Safety contract ratification: [`RATIFICATION_2026-07-10_i0301_safety_contract.md`](RATIFICATION_2026-07-10_i0301_safety_contract.md)
- Parent program CAMPAIGN: [`real_user_readiness/CAMPAIGN.md`](real_user_readiness/CAMPAIGN.md)
- Parent program ratification: [`RATIFICATION_2026-07-10_real_user_readiness.md`](RATIFICATION_2026-07-10_real_user_readiness.md)
- Phase 1 audit ledger deliverable: `1ca36f84-ae40-415c-b482-768415d13fd9` in workspace `fcd7e683-3bfe-4d35-9704-0e54dd587ea1`
- Substrate PRs: #3085 (Stage 1), #3086 (Stage 2a), #3087 (Stage 2b PR A), #3088 (Stage 2b PR B), #3089 (Stage 3 PR A), #3090 (Stage 3 PR B), #3092 (Phase 4)
- Scoping-ratification + Phase-1-close PRs: #3079, #3081
- Safety-contract-draft + ratification PRs: #3082, #3083
- Draft close doc PR: #3093
- Sibling ratification records:
  - `RATIFICATION_2026-07-06_first_queue.md` (Cycle 1 backlog band)
  - `RATIFICATION_2026-07-07_second_arc_I-0200.md` (I-0200 RAG Corpus arc selection)
  - `RATIFICATION_2026-07-10_real_user_readiness.md` (parent program ratification)
  - `RATIFICATION_2026-07-10_i0301_safety_contract.md` (safety contract ratification)

---

**End of I-0301 Tenant Boundary Lockdown Arc Close Ratification Record. This file is frozen; do NOT edit after commit.**
