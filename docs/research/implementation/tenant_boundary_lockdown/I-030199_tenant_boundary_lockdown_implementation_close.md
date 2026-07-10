---
title: "I-0301 Tenant Boundary Lockdown — HTTP + AllowAny Surface Remediation + Failure-Data Safety Contract — Implementation Close"
status: draft
authority: arc-close-draft  # becomes 'arc-close-frozen' after Chris ratification
session_added: 2742
session_close_drafted: 2742
last_updated: 2026-07-10
arc_id: I-0301
arc_close_date: 2026-07-10
arc_workspace: "RUR-C1 Tenant Boundary Lockdown"
arc_workspace_id: fcd7e683-3bfe-4d35-9704-0e54dd587ea1
parent_campaign: RUR-C1 (Tenant Boundary Lockdown)
parent_program: RUR (Real User Readiness)
parent_program_doc: docs/research/implementation/real_user_readiness/CAMPAIGN.md
parent_program_ratification: docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md
parent_arc_scoping: docs/research/implementation/tenant_boundary_lockdown/I-0301_scoping.md
parent_arc_scoping_ratifier: chris
parent_arc_scoping_ratification_date: 2026-07-10
sibling_arcs_status:
  - I-0302 (Object-Level Authorization) — NOT YET OPENED (unblocked by I-0301 Phase 2 close)
  - I-0303 (Async Tenant-Boundary Enforcement) — NOT YET OPENED (unblocked by I-0301 Phase 2 close)
downstream_unlocks_active:
  - RUR-C2 (Async State + Fail-Loud + Traceability) — unblocked at I-0301 Phase 2 close (2026-07-10)
  - I-0302 — unblocked at I-0301 Phase 2 close (2026-07-10)
  - I-0303 — unblocked at I-0301 Phase 2 close (2026-07-10)
parent_close_gate:
  - RUR-C1 parent closes ONLY when I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression suite (per Chris Q2 D-verdict recorded at parent ratification)
  - I-0301 close does NOT close RUR-C1
---

# I-0301 Tenant Boundary Lockdown — Arc Implementation Close

> **DRAFT arc close — pending Rigby SIGN + Chris ratification.**
> On ratification, this doc becomes `authority: arc-close-frozen`. The arc is preserved as-shipped; any post-close work happens via new sub-arcs or a follow-on program.

---

## §1. Executive Summary

I-0301 is the first arc under the Real User Readiness campaign, opened S2742 and closed S2742 (single-day arc). It ships the substrate that every subsequent RUR arc will emit failures through: the ratified Failure-Data Safety Contract, the enforcement layers implementing it (DRF handler + Django middleware), the regression test suite validating it, the CI-blocking coverage machinery preventing drift, and the first tranche of AllowAny endpoint remediation directly under RUR-C1 scope.

Arc outcome (of the 27 grep-caught AllowAny entry points at HEAD `0825df46`, using the mutually-exclusive taxonomy in §3):

- **18 Remediated** (`AllowAny → IsAuthenticated`)
- **4 Deleted** (autonomous_system stub endpoints removed entirely)
- **1 Intentionally Public** (nervous `IsResponsive` — frozen with regression guardrails as the sole retained public health-check)
- **4 Deferred** (2 sports Bucket A pending schema audit + 2 token-gated Bucket A2 pending substrate verify — unchanged pre-existing state)

Safety-contract substrate live; drift-detection machinery active; sibling arcs I-0302 + I-0303 + RUR-C2 unblocked.

The arc did NOT close its parent campaign. RUR-C1 (Tenant Boundary Lockdown) requires I-0301 + I-0302 + I-0303 to all pass shared cross-tenant regression per Chris Q2 D-verdict; only I-0301 has landed.

---

## §2. Phase-by-Phase Outcomes

### Phase 1 — Audit Ledger (CLOSED 2026-07-10)

**Deliverable:** `1ca36f84-ae40-415c-b482-768415d13fd9` in workspace `fcd7e683` (RUR-C1 Tenant Boundary Lockdown).

- Static AllowAny grep at HEAD `0825df46`: **26 occurrences across 8 files** — matched the S2740 audit snapshot exactly.
- Dynamic-permission audit per Rigby SIGN §1 material amendment: **+1 additional** (`AgentExecutionViewSet.get_permissions()` returning `AllowAny` conditionally on `input_data__game_id` query param).
- **Denominator: 27 known AllowAny entry points.**
- Bucket classification: A=2 / A2=2 / B=12 / C=4 (preliminary) / D=7.
- Rigby ledger SIGN: **SIGN-PASS** (8/8 focus areas). No material amendments.
- Non-DRF public views (718 `@csrf_exempt` in 106 files) noted as follow-on scope; not enumerated in this ledger.

### Phase 2 — Safety Contract Draft + Rigby SIGN + Chris Ratification (CLOSED 2026-07-10)

**Deliverable:** [`failure_data_safety_contract.md`](failure_data_safety_contract.md) — `frozen: true`.
**Ratification record:** [`RATIFICATION_2026-07-10_i0301_safety_contract.md`](../RATIFICATION_2026-07-10_i0301_safety_contract.md).

Contract structure (12 sections, 423 lines):
- §1 Scope + Non-Scope
- §2 Governing Principles P1-P5
- §3 User-Facing Error Envelope (7 permitted fields; 14 prohibited items)
- §4 `reason_code` enum (14 entries with default English human_message copy)
- §5 `support_code` format (`RUR-<COMPONENT>-<yyMMdd>-<opaque-hex>`, 16-bit entropy, 12-value component enum)
- §6 Operator-side envelope + tenant-scoped `trace_lookup` access rule
- §7 Component coverage (DRF + non-DRF + template + streaming + async status + WebSocket)
- §8 Four-layer enforcement (DRF handler + Django middleware + template + regression suite)
- §9 Regression suite schema
- §10 Amendment discipline

Rigby SIGN: **SIGN-WITH-EDITS** (11/12 PASS, 1 material amendment: §3.2 unconditional prompts/conversation prohibition — TIGHTENS the contract).

Chris ratification: 2026-07-10, contract frozen as-amended.

(Note: the "3 material amendments" referenced elsewhere in project history are the S2742 scoping-doc amendments — a separate Chris D-verdict earlier that day — not this Phase 2 contract amendment.)

### Phase 3 — HTTP Remediation (CLOSED 2026-07-10)

Executed across 5 stages, 6 PRs:

| Stage | PR | Outcome |
|---|---|---|
| Stage 1 — Substrate + CI | #3085 | `core/security/` package (support_code + reason_codes + error_envelope) + `tests/security/test_failure_envelope_conformance.py` (29 tests) + `.github/workflows/security-conformance.yml` (CI-blocking) + settings wiring |
| Stage 2a — content_learning | #3086 | 4 endpoints AllowAny → IsAuthenticated (platform-wide aggregates; no scoping needed) |
| Stage 2b PR A — intelligence | #3087 | 7 endpoints remediated with per-view design: ActionPlanPersistenceView DB replaces filesystem globs; ViewGeneratedFileView exact-basename ownership check; RevenueMetricsView per-user scoping; ownership 404 on foreign-owned rows |
| Stage 2b PR B — agents @action | #3088 | `AgentExecutionViewSet.with_results` action-level `AllowAny` decorator removed; action re-inherits from the class-level `IsAuthenticated`. Evidence pass confirmed the ViewSet is not routed in `core/urls.py`; source-level fix stands as defense-in-depth against a future re-route. Remaining dynamic `get_permissions()` path handled in Stage 3 PR B. |
| Stage 3 PR A — autonomous + nervous | #3089 | 4 autonomous_system endpoints DELETED entirely; 4 nervous auth-gated; NervousIsResponsive frozen as Bucket A with regression guardrails |
| Stage 3 PR B — agents get_permissions | #3090 | Bucket D dynamic AllowAny path collapsed to unconditional IsAuthenticated |

**Discovered substrate divergence (Stage 2c candidate):** `core.api_responses.APIResponseEnvelope` emits a different JSON error shape and intercepts auth failures before DRF handler fires. Both shapes are safe; unification has cross-platform blast radius (36+ call sites + frontend TSX). Documented as follow-on arc candidate.

### Phase 4 — Coverage Denominator Machinery (SHIPPED 2026-07-10)

**PR #3092.**

- `enumerate_public_http_endpoints` management command (recursive URL walker; import-safe; deterministic sorted JSON)
- `regenerate_endpoint_snapshot` management command (fails fast on unclassified AllowAny per Rigby SIGN Q4)
- `tests/security/http_endpoint_snapshot.json` — pinned baseline (2,261 endpoints, 203 AllowAny)
- `tests/security/test_endpoint_drift.py` — 5 drift categories including **HARD-FAIL invariant** on NON-AllowAny → AllowAny regression
- CI workflow extended to trigger on any `urls.py` / `views.py` change

**Discovery at scale:** 203 AllowAny endpoints in the wild vs 27 my Phase 1 grep found. Validates Rigby SIGN §1 material amendment (dynamic-permission audit) at scale. Mechanism: the grep matched only class-attribute `permission_classes = [AllowAny]` declarations; it missed function-based DRF views declaring permissions via `@api_view` + `@permission_classes([AllowAny])` decorators. 176 additional AllowAny paths surfaced when the enumerator walked resolver metadata and read the DRF-attached `cls` on function callbacks.

Rigby Phase 4 SIGN: **SIGN-PASS** (5/5 questions PASS). 4 material amendments + 3 must-haves folded in during implementation.

---

## §3. Metrics + Coverage

### Endpoint remediation counts (mutually-exclusive bins per Rigby S2742 close SIGN §6)

#### 27 grep-caught AllowAny entry points at HEAD `0825df46`

Every endpoint below is in exactly one bin. Sum: 18 + 4 + 1 + 4 = 27.

| Bin | Count | Endpoints |
|---|---|---|
| **Remediated** (`AllowAny → IsAuthenticated`) | **18** | 4 content_learning views (Stage 2a) + 7 intelligence views (Stage 2b PR A) + 4 nervous views Feel/Vitals/History/Consumers (Stage 3 PR A) + 1 nervous Status view (Stage 3 PR A source-level fix — the view is not URL-routed but its class attribute still flipped to IsAuthenticated as defense-in-depth) + 1 agents `get_permissions()` dynamic path collapse (Stage 3 PR B) + 1 agents `@action` `with_results` decorator override removal (Stage 2b PR B — action re-inherits from the class-level `IsAuthenticated`) |
| **Deleted** | **4** | 4 autonomous_system endpoints (Start/Status/Pause/Resume) — view classes + URL routes + frontend `autonomousApi` calls all removed at Stage 3 PR A |
| **Intentionally Public** (`AllowAny` retained with justification) | **1** | nervous `IsResponsive` — Bucket A frozen with regression suite guardrails (constant-shape response; no UUIDs; no version / queue-depth / dependency-health hints) at Stage 3 PR A |
| **Deferred** (unchanged pre-existing state) | **4** | 2 sports viewsets (Bucket A — schema audit not shipped) + 2 token-gated views (Bucket A2 — token substrate verification not shipped: `public_changelog` + `public_intelligence`) |

**Note on de facto dead code:** two of the remediated endpoints (nervous Status + agents `with_results`) belong to view classes not registered on any active router in `core/urls.py`. Their source-level `AllowAny → IsAuthenticated` change is still counted as remediated because it hardens the class in case a future PR re-routes it. Neither is "not routed" as its own bin — they are remediated at the code level, and their public-surface exposure is zero regardless.

#### Enumerator-caught AllowAny at Phase 4 snapshot

| Category | Count | Notes |
|---|---|---|
| Total endpoints in `http_endpoint_snapshot.json` | 2,261 | Full Django URL resolver enumeration |
| AllowAny endpoints in snapshot | 203 | Baseline; grandfathered by drift test |
| Delta vs the 27 grep-caught | +176 | Function-based DRF views via `@api_view` + `@permission_classes` decorators; class-attribute grep did not catch them |
| Explicitly hardened in this arc | 18 | The Remediated count above |
| Explicitly Deleted in this arc | 4 | Reduces the snapshot AllowAny population |
| Grandfathered pre-existing AllowAny remaining in snapshot | 181 | 203 − 18 remediated − 4 deleted = 181. Drift test blocks NEW additions and NON-AllowAny → AllowAny regressions; does NOT force reclassification of the 181 pre-existing. Follow-on program candidate. |

### Test suite (final)

| Suite | Tests | Purpose |
|---|---|---|
| `test_failure_envelope_conformance.py` | 29 | Contract §9 substrate: envelope shape + prohibited content probes + support_code format + layer coverage + exhaustive enum |
| `test_bucket_b_remediation.py` | ~24 (parametrized) | Anonymous rejection on all remediated B/C endpoints + prohibited-content probes |
| `test_bucket_a_public_endpoints.py` | 5 | Frozen public health-check contract (NervousIsResponsive) |
| `test_endpoint_drift.py` | 5 | Coverage machinery drift detection |
| **Total** | **70/70 pass** | CI-blocking via `security-conformance.yml` |

### Grandfathered pre-existing AllowAny count

**181 AllowAny endpoints remain in the Phase 4 snapshot as pre-existing state** (203 total − 22 explicitly touched by this arc [18 Remediated + 4 Deleted] = 181). The drift test blocks NEW AllowAny additions and NON-AllowAny → AllowAny regressions; it does NOT force reclassification of the 181 grandfathered. Follow-on work required to progressively classify + remediate. Explicit non-goal of I-0301 (would extend scope beyond the arc's charter).

---

## §4. SIGN Cycle History

| Cycle | Date | Reviewer | Verdict | Material Amendments |
|---|---|---|---|---|
| Parent campaign initial (S2741) | 2026-07-10 | Rigby | SIGN-with-amendments | 7 applied |
| Parent campaign re-SIGN (S2741 amendments) | 2026-07-10 | Rigby | SIGN-PASS | 1 material clarification applied |
| I-0301 scoping (S2742) | 2026-07-10 | Rigby | SIGN-with-amendments | 3 material + ~10 non-material applied |
| I-0301 scoping ratification (Chris D-verdict) | 2026-07-10 | Chris | APPROVE ALL 3 MATERIAL | — |
| Phase 1 audit ledger | 2026-07-10 | Rigby | SIGN-PASS | 0 material |
| Phase 2 safety contract | 2026-07-10 | Rigby | SIGN-WITH-EDITS | 1 material (§3.2 unconditional prohibition) + 4 non-material applied |
| Phase 2 safety contract ratification (Chris) | 2026-07-10 | Chris | RATIFIED | — |
| Phase 3 Stage 1 substrate | 2026-07-10 | Rigby | SIGN-WITH-EDITS | 2 material (Q7 CI-in-Stage-1 + Q5 middleware invariant) applied |
| Phase 3 Stage 2b remediation | 2026-07-10 | Rigby | SIGN-WITH-EDITS | 1 material (Q3 exact-basename match) + Q10 2-PR split applied |
| Phase 3 Stage 3 | 2026-07-10 | Rigby | SIGN-PASS | 5 small amendments folded |
| Phase 4 coverage machinery | 2026-07-10 | Rigby | SIGN-PASS | 4 material + 3 must-haves folded |

---

## §5. Follow-on Scope (recorded, out of I-0301)

### Stage 2c — Envelope Unification (open follow-on)

`core.api_responses.APIResponseEnvelope` emits `{success: False, error: {code, message}}` shape via `api_unauthorized` / `api_forbidden` / etc. helpers. Auth middleware intercepts anonymous requests before DRF's exception handler fires, so the safety-contract envelope from `core.security.error_envelope` does not apply to auth-rejection responses.

Both shapes are safe (no tenant / substrate leakage). Not uniform. Envelope unification has cross-platform blast radius (36+ call sites + frontend TSX parsing `body.error.code` and `body.success`).

Candidate as its own arc or as Stage 2c within a re-opened I-0301 successor.

### Grandfathered 181 pre-existing AllowAny endpoints

Of the 203 AllowAny endpoints in the Phase 4 snapshot, this arc explicitly touched 22 (18 Remediated + 4 Deleted). The remaining **181** are pre-existing state grandfathered by the drift test. The drift test blocks NEW AllowAny additions and NON-AllowAny → AllowAny regressions; it does NOT force reclassification of the 181 grandfathered endpoints. Progressive classification work is a follow-on program.

### NervousStatusView + AgentExecutionViewSet — orphan classes

Both classes remain in the source tree with `permission_classes = [IsAuthenticated]` (hardened in Phase 3) but neither is registered on any active router in `core/urls.py`. Their public-surface exposure is zero. Class deletion is outside I-0301 scope; recorded here so a future orphan-cleanup arc has provenance.

### Non-DRF public views (718 `@csrf_exempt` in 106 files)

Broader "non-DRF public views" audit stream. Follow-on candidate.

### `NervousHistoryView` `id` field UUID exposure

Rigby Stage 3 SIGN Q2 amendment (deferred, non-blocking): consider stripping the `id` field from the response even for authenticated users. UUID exposure is a general anti-pattern; not required for arc close.

### RUR-C6 `trace_lookup` code-level RBAC

Contract §6.2.4 accepts alpha-level procedural enforcement. Code-level `supported_workspace_ids` RBAC system is a follow-on before self-serve (post-alpha).

---

## §6. Downstream Unlock Status

| Downstream | Status | Unlocked by |
|---|---|---|
| RUR-C2 (Async State + Fail-Loud + Traceability) — I-0400 slot | UNBLOCKED, not yet opened | I-0301 Phase 2 close (safety contract ratified) |
| I-0302 (Object-Level Authorization) | UNBLOCKED, not yet opened | I-0301 Phase 2 close |
| I-0303 (Async Tenant-Boundary Enforcement) | UNBLOCKED, not yet opened | I-0301 Phase 2 close |

### Parent close gate

**RUR-C1 (parent) does NOT close on I-0301 close.** Per Chris Q2 D-verdict at parent campaign ratification: RUR-C1 closes only when I-0301 + I-0302 + I-0303 all pass the shared cross-tenant regression suite.

Sequence to RUR-C1 close:
1. Open + close I-0302 (Object-Level Authorization)
2. Open + close I-0303 (Async Tenant-Boundary Enforcement)
3. Shared cross-tenant regression suite green across all three arcs
4. RUR-C1 parent ratification + close

---

## §7. Playbook + Contract Alignment

Arc executed under the ratified Real User Readiness constitutional CAMPAIGN.md + the ratified Failure-Data Safety Contract. Every implementation PR conformed to:

- Contract §3.1 permitted-field allowlist
- Contract §3.2 prohibited-content invariants
- Contract §8 four-layer enforcement discipline
- Contract §10 amendment discipline (no in-arc contract mutations)
- Playbook PLAYBOOK-6.10.6 verify-before-build (every stage led with existing-implementation analysis)
- Playbook Cat A discipline (extended existing substrate; no parallel surface duplication)
- Rigby-SIGN-first pattern for every substantive design decision (per S2741 collaboration model)

No PLAYBOOK rule violations recorded.

---

## §8. Chris Ratification Contract for Arc Close

This close doc is `authority: arc-close-draft` until Chris ratifies. Ratification requires Chris D-verdict on:

1. All Phase 1–4 outcomes as reported
2. Follow-on scope §5 correctly recorded
3. Grandfathered baseline (181 pre-existing AllowAny) accepted as-is with drift-blocked-going-forward posture
4. Downstream unlock §6 correctly reflected (RUR-C1 parent close condition preserved)

On ratification:
- Frontmatter transitions: `authority: arc-close-frozen`, adds ratification metadata
- Ratification record `RATIFICATION_2026-07-10_i0301_arc_close.md` created
- I-0301 scoping §13 Phase 5 marked CLOSED
- Parent CAMPAIGN.md §4 Campaign Map I-0301 row updated (RUR-C1 remains open pending I-0302 + I-0303)
- Docs cascade run with safe targeting

---

## §9. Cross-References

- Parent program CAMPAIGN: [`real_user_readiness/CAMPAIGN.md`](../real_user_readiness/CAMPAIGN.md)
- Parent program ratification: [`RATIFICATION_2026-07-10_real_user_readiness.md`](../RATIFICATION_2026-07-10_real_user_readiness.md)
- Arc scoping: [`I-0301_scoping.md`](I-0301_scoping.md)
- Safety contract: [`failure_data_safety_contract.md`](failure_data_safety_contract.md)
- Safety contract ratification: [`RATIFICATION_2026-07-10_i0301_safety_contract.md`](../RATIFICATION_2026-07-10_i0301_safety_contract.md)
- Phase 1 audit ledger: workspace `fcd7e683` deliverable `1ca36f84-ae40-415c-b482-768415d13fd9`
- Substrate PRs: #3085, #3086, #3087, #3088, #3089, #3090, #3092
- Scoping-ratification + Phase-1-close PRs: #3079, #3081
- Safety-contract-draft + ratification PRs: #3082, #3083
- Prior arc closes (sibling ratification records for cadence reference):
  - `RATIFICATION_2026-07-06_first_queue.md`
  - `RATIFICATION_2026-07-07_second_arc_I-0200.md`

---

## §10. Rigby Close SIGN Outcome + Post-SIGN Amendments

Rigby close SIGN 2026-07-10 (S2742): initial verdict **SIGN-BLOCKED** on 3 material metric/arithmetic/terminology issues in §1 + §3 + follow-on wording. Verdict was not on implementation completeness — Phase 1–4 outcomes and downstream unlock accuracy all PASSED — only on the accounting shape of the close doc.

Material amendments applied post-SIGN (all correctness fixes; none change D-verdicts, program scope, dependencies, hard gates, or Wave 1 authorization):

1. **§1 executive summary outcome sentence rewritten** into the mutually-exclusive taxonomy (18 Remediated / 4 Deleted / 1 Intentionally Public / 4 Deferred = 27) matching §3.
2. **§3 endpoint remediation counts rewritten** with clean mutually-exclusive bins (Remediated `AllowAny → IsAuthenticated` / Deleted / Intentionally Public / Deferred). No overlapping categories. Arithmetic checks: 18 + 4 + 1 + 4 = 27 grep-caught endpoints; 22 (18 + 4) of 203 snapshot-AllowAny explicitly touched by the arc; 181 grandfathered.
3. **Terminology normalized** throughout: "dead-gated" no longer used ambiguously; nervous Status and agents `with_results` reframed as "remediated at source-level; not URL-routed (public-surface exposure zero either way)"; §5 "dead code preserved" reworded to "orphan classes."

Non-material tweaks applied:
- Phase 2 "3 material amendments" clarified as scoping-doc amendments (a separate Chris D-verdict on the same day), not the Phase 2 contract amendment (which was 1).
- Phase 3 Stage 2b PR B row: replaced "reclassified to Bucket C dead-gated" with "action-level override removed; source-level fix stands even though ViewSet not routed."
- Phase 4 mechanism explanation: dropped the specific `WrappedAPIView` name and softened to "function-based DRF views via `@api_view` + `@permission_classes` decorators."

Re-SIGN request sent to Rigby post-amendments; ratification-block resolves on her PASS on the corrected doc.

---

**End of I-0301 Tenant Boundary Lockdown implementation close (draft; pending Rigby re-SIGN confirmation + Chris ratification).**
