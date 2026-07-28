---
title: "ADR-0007 — Layered Envelope Policy (Refines ADR-0006 §3.2)"
adr_id: ADR-0007
slug: layered-envelope-policy
status: accepted
authority: design-decision
proposed: 2026-07-27
ratified: 2026-07-27
ratifier: chris
chris_ratification: "yes author ADR-0007" 2026-07-27 — after S3005 spec-invalidation discovery + Claude+Rigby joint recommendation per feedback_claude_rigby_agree_first_chris_yes_no. Three-part plain-English framing routed per PLAYBOOK-7.7.3 (do-we-lose-anything / more-work-later / ≤1 decision).
supersedes: (none)
superseded_by: (none)
refines: ADR-0006 §3.2   # non-schema field — grep target for amendment linkage
intake_id: (none — direct S3005 discovery)
arc_ref: (none — orthogonal to Cycle-0/1)
source_refs:
  - docs/adr/ADR-0006-typed-error-envelope-contract-non-provisional.md §3 (delegates to ADR-0005 §3.1-§3.5)
  - docs/adr/ADR-0005-typed-error-envelope-contract.md §2 line 25 (baseline claim "EXCEPTION_HANDLER absent" — invalid at HEAD 85fffdfc1)
  - docs/adr/ADR-0005-typed-error-envelope-contract.md §3.2 (Family B declared as SoT emission shape — refined by this ADR)
  - docs/adr/ADR-0005-typed-error-envelope-contract.md §4.1 T-ENVELOPE-2 (three-path spec — invalidated at HEAD; superseded by this ADR's Decision)
  - core/security/error_envelope.py:72-114 (build_user_facing_envelope — Family E emission at HEAD)
  - core/security/error_envelope.py:248-305 (drf_exception_handler — Layer 1 wiring)
  - core/security/error_envelope.py:313-365 (RURErrorEnvelopeMiddleware — Layer 2 wiring)
  - core/settings.py:747 (REST_FRAMEWORK EXCEPTION_HANDLER wiring to Family E emitter)
  - core/settings.py:295 (MIDDLEWARE inclusion of RURErrorEnvelopeMiddleware)
  - core/api_responses.py:15-234 (APIResponseEnvelope — Family B; success + error methods)
  - docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md (I-0301 safety-contract §3 user-facing envelope + §8.1 Layer 1 enforcement — Family E's authorizing contract)
  - PR #3085 (I-0301 Phase 3 Stage 1 substrate — shipped Family E handler + middleware, predates ADR-0005 ratification)
reversibility: 5
  # Docs-only. Rollback: git revert removes ADR-0007. ADR-0006 §3.2 returns
  # to its ADR-0005-delegated shape without amendment. No runtime code, no
  # DB migration. Existing Family E emission continues; existing Family B
  # emission continues. The deprecation posture on APIResponseEnvelope.error
  # is annotation-only until a T-slot arc implements migration.
sign_cycle_1: (pending — dispatched to Rigby T1 pre-merge per PLAYBOOK-7.7.2)
sign_cycle_1_pin: pa-330f207235344b8f
companion_docs:
  - docs/adr/ADR-0006-typed-error-envelope-contract-non-provisional.md
  - docs/adr/ADR-0005-typed-error-envelope-contract.md
  - docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md
  - docs/handoffs/SESSION_3005_ADR_0007_LAYERED_ENVELOPE_POLICY.md
owner: claude (S3005 v1 draft; Chris ratified before draft per direct S3005 dispatch)
---

# ADR-0007 — Layered Envelope Policy (Refines ADR-0006 §3.2)

## 1. Status

**Accepted** — Chris ratified 2026-07-27 via "yes author ADR-0007" following joint Claude+Rigby recommendation per `feedback_claude_rigby_agree_first_chris_yes_no`. Rigby SPEC-INVALIDATION AGREE'd + A4 (reconciliation-ADR-first) recommended after independent tool-verification of the discovery (see §2.3).

**Refines ADR-0006 §3.2** — does NOT supersede. ADR-0006 §3.1 (γ mechanism), §3.3 (SHAPE-BLIND interceptor retention), §3.4 (nested UX policy), §3.5 (F-C-VIP-1 scope-tightening) remain canonical without modification. Only §3.2's "Family B as SoT emission shape" declaration is refined by the layered policy below.

## 2. Context

### 2.1 The discovery

At S3005 open (2026-07-27), Chris directed execution of ADR-0005 §4.1 T-ENVELOPE-2 ("Backend `EXCEPTION_HANDLER` choice + per-endpoint Family B adoption ramp"). The spec named three paths:

- (a) custom `EXCEPTION_HANDLER` at `REST_FRAMEWORK` settings-level that wraps Family A → Family B
- (b) middleware-level normalization at `core/auth_middleware.py`
- (c) per-endpoint APIResponseEnvelope adoption without global normalization

Pre-execution probe at HEAD `85fffdfc1` (via `grep EXCEPTION_HANDLER core/settings.py`) revealed **an `EXCEPTION_HANDLER` is already wired** at `core/settings.py:747` → `core.security.error_envelope.drf_exception_handler`, and `RURErrorEnvelopeMiddleware` is already installed at `core/settings.py:295`. Both shipped in PR #3085 (`40959cd66`, S1115-era) as "I-0301 Phase 3 Stage 1 — Failure-Data Safety Contract substrate."

### 2.2 The shape mismatch

The wired handler emits a shape (call it Family E) that is materially different from ADR-0006 §3.2's declared Family B:

**Family E** (safety-contract envelope, `core/security/error_envelope.py:72-114`):
```json
{
  "support_code": "MISSING-abc12",
  "reason_code": "not_found",
  "human_message": "The requested resource could not be found.",
  "retryable": false,
  "terminal_state": "TERMINAL",
  "timestamp": "2026-07-27T20:00:00Z",
  "retry_after_seconds": 60
}
```

**Family B** (APIResponseEnvelope, `core/api_responses.py:15-234`):
```json
{
  "success": false,
  "error": {
    "code": "generic_error",
    "message": "An error occurred",
    "details": { ... }
  }
}
```

Family E is emitted implicitly on every DRF exception (via `EXCEPTION_HANDLER`) and every uncaught non-DRF exception (via middleware). Family B is emitted explicitly at ~14 opt-in consumer call-sites via `APIResponseEnvelope.error()`. Both coexist at HEAD. ADR-0005 §2 line 25 baseline claim "EXCEPTION_HANDLER absent = Family A dominance mechanism" is invalid at HEAD.

### 2.3 Rigby joint-diagnosis verification

Rigby T1-equivalent independent verification (S3005, PLAYBOOK-7.7.2) via 8 real tool_runs across two turns confirmed:

- Handler + middleware wiring at HEAD (`core/settings.py:747` + `:295`)
- Family E shape at `core/security/error_envelope.py:72-114`; Family B shape at `core/api_responses.py:15-234`
- Baseline mismatch: ADR-0005's "EXCEPTION_HANDLER absent" claim is invalid at HEAD (verified via `git_info` + `grep`)
- Consumer surface: Family B has few explicit callers (~14); Family E has few explicit callers but massive implicit surface (every DRF exception + every uncaught non-DRF exception)

**Rigby SPEC-INVALIDATION classification: AGREE.** T-ENVELOPE-2 as scoped in ADR-0005 §4.1 is invalid because paths (a) and (b) are already shipped (pointing at Family E, not Family B), and path (c) already exists as APIResponseEnvelope opt-in.

**Rigby joint recommendation: A4 (reconciliation ADR first).** Reasoning: substrate-level contract conflict needs explicit ratified policy before implementation changes; silent proceeding risks breaking either ADR-0006's contract or the I-0301 safety-contract §8.1.

### 2.4 Constraint — I-0301 safety-contract §8.1 is HIGH-severity

The Family E emitter is authorized by the I-0301 Failure-Data Safety Contract §8.1 (ratified 2026-07-10 per `docs/research/implementation/RATIFICATION_2026-07-10_i0301_safety_contract.md`). Its shape enforces:

- **§3.2:** `human_message` MUST use ratified default English copy; NEVER echo exception `detail`.
- **§5.1:** `support_code` component enum is fixed.
- **§6.1:** operator envelope emitted to `OpsRunEvent.detail` (best-effort per Rigby SIGN Q9).

Any policy that "retires Family E" without a new safety-contract successor would violate §8.1 substrate. This ADR MUST NOT propose Family E retirement without safety-contract-level ratification. This is a HIGH-severity constraint on the reconciliation shape.

## 3. Decision

**Adopt a LAYERED envelope policy.** Error responses and success responses have distinct canonical envelope shapes, aligned to what already ships at HEAD and to the I-0301 safety-contract §8.1 constraint.

### 3.1 Family E is the canonical ERROR-RESPONSE SoT

`build_user_facing_envelope` at `core/security/error_envelope.py:72-114` is the ratified SoT for HTTP error responses (4xx/5xx status codes). The shape `{support_code, reason_code, human_message, retryable, terminal_state, timestamp, retry_after_seconds?}` is preserved verbatim per I-0301 §3.

Emission surfaces — the construction function `build_user_facing_envelope` is the SoT (per safety-contract §8 line 317: "any response body that reaches a user without passing through at least one enforcement layer's construction is a contract violation"; §8.4 is the Regression Suite that validates conformance, not the construction layer itself — the four enforcement layers §8.1-§8.3 all invoke the same construction function):

- **DRF exception path (Layer 1 per safety-contract §8.1)** — `EXCEPTION_HANDLER` at `core/settings.py:747` → `drf_exception_handler`. Automatic; no per-endpoint code needed.
- **Non-DRF exception path (Layer 2 per §8.2)** — `RURErrorEnvelopeMiddleware.process_exception` at `core/security/error_envelope.py:336-365`. Automatic for uncaught exceptions.
- **Template overrides (Layer 3 per §8.3)** — HTML 4xx/5xx templates conform to §3.1 envelope shape.
- **Explicit view-code emission (authorized via §8.4 construction-boundary)** — direct call to `build_user_facing_envelope(reason_code=..., ...)` wrapped in `JsonResponse(envelope, status=...)` or `Response(envelope, status=...)`. Required for view code that emits an error inline (not via `raise`) — most T-ENVELOPE-2-DEPRECATION migration targets fall into this category. Regression suite §9.2 validates SHAPE regardless of construction path.

### 3.2 Family B is the canonical SUCCESS-RESPONSE SoT

`APIResponseEnvelope.success()` + `APIResponseEnvelope.paginated()` at `core/api_responses.py:15-51` + `:100-140` are the ratified SoT for HTTP success responses (2xx status codes). The shape `{success: true, data, meta?, message}` is preserved verbatim.

Emission surface: explicit call in view code per-endpoint.

### 3.3 APIResponseEnvelope.error() and error-adjacent helpers are DEPRECATED

The following methods on `APIResponseEnvelope` at `core/api_responses.py` are DEPRECATED as of this ADR's ratification. They emit Family B error shape, which is NOT the canonical error-response SoT per §3.1:

- `APIResponseEnvelope.error()` (`:53-98`)
- `APIResponseEnvelope.unauthorized()` (`:142-149`)
- `APIResponseEnvelope.forbidden()` (`:151-158`)
- `APIResponseEnvelope.not_found()` (`:160-167`)
- `APIResponseEnvelope.validation_error()` (`:169-180`)
- `APIResponseEnvelope.rate_limited()` (`:182-189`)
- `APIResponseEnvelope.server_error()` (`:191-204`)
- Module-level helpers: `api_error`, `api_unauthorized`, `api_forbidden`, `api_not_found`, `api_validation_error` (`:212-234`)

**Deprecation posture** — annotation-only until a T-slot arc implements migration (§4.3). Existing callers continue to work; new code MUST use Family E via `build_user_facing_envelope` or the safety-contract §8.1 automatic emission path.

### 3.4 ADR-0006 §3.2 refinement scope

ADR-0006 §3 delegates to ADR-0005 §3.1-§3.5. This ADR refines ONLY §3.2 ("SoT emission shape — Family B `APIResponseEnvelope`") and does not touch §3.1 (γ mechanism), §3.3 (SHAPE-BLIND interceptor), §3.4 (nested UX policy), or §3.5 (F-C-VIP-1 scope-tightening).

The refinement: where ADR-0005 §3.2 declares "Adopt `APIResponseEnvelope` at `core/api_responses.py:15-234` as the SoT emission shape," this ADR refines to "Adopt `build_user_facing_envelope` at `core/security/error_envelope.py:72-114` as the ERROR-RESPONSE SoT emission shape (Family E); retain `APIResponseEnvelope.success()` + `.paginated()` as the SUCCESS-RESPONSE SoT (Family B, success methods only)."

### 3.5 T-ENVELOPE-2 CLOSED; new T-slot introduced

ADR-0005 §4.1 T-ENVELOPE-2 ("Backend `EXCEPTION_HANDLER` choice + per-endpoint Family B adoption ramp") is **CLOSED as already-shipped** — both handler + middleware were installed by PR #3085 (I-0301 substrate) predating ADR-0005 ratification. Paths (a) and (b) both landed pointing at Family E (safety-contract) rather than Family B (`APIResponseEnvelope`).

This ADR introduces a **new T-slot T-ENVELOPE-2-DEPRECATION** (see §4.3) to migrate the extant Family B error call-sites to Family E per §3.3 deprecation. This is separate governance — CLOSED T-slot marks what shipped; new T-slot marks what remains.

## 4. Consequences

### 4.1 What this ADR enables at HEAD

- Runtime behavior at HEAD `85fffdfc1` is **already conformant** to §3.1 + §3.2. No PR needed to bring runtime into alignment.
- ADR corpus reflects reality: Family E's shipped-and-authorized posture is now documented at the ADR layer, not just at the safety-contract layer.
- Future T-slot arcs (T-ENVELOPE-4, T-ENVELOPE-5, T-ENVELOPE-6) can reference ADR-0007 for shape decisions without re-litigating.

### 4.2 What this ADR obligates every consumer to do

- **New code:** MUST use Family E for error responses (via `build_user_facing_envelope` or the automatic exception paths). MUST NOT introduce new call-sites of `APIResponseEnvelope.error()` or its adjacent helpers.
- **Existing code:** existing 108 Family B error call-sites (per §4.3 fresh-grep) are NOT required to migrate immediately. PR reviewers SHOULD flag new callers of deprecated methods.
- **Documentation:** ADR-0006 §3.2 body gets a note pointing to ADR-0007 as the refinement. Docstrings on `APIResponseEnvelope.error()` + adjacent methods + module helpers get `.. deprecated::` markers with ADR-0007 pointer. Class-level docstring on `APIResponseEnvelope` gets a scope banner ("canonical for SUCCESS responses only; error helpers deprecated"). All docs edits land in this ADR's ratification PR.
- **Regression prevention:** a lint / code-review gate (ruff custom rule OR simple CI grep check) banning new usages of deprecated helpers outside `core/api_responses.py` MUST be authored as part of T-ENVELOPE-2-DEPRECATION (§4.3). Purpose: prevent Family B error-shape re-growth after this ADR ratifies the layered policy.

### 4.3 Follow-on T-slot introduced

- **T-ENVELOPE-2-DEPRECATION** (replaces T-ENVELOPE-2): migrate the extant Family B error call-sites to Family E. Fresh grep at HEAD `85fffdfc1` returned **108 call-sites across 5 files**:
  - `core/views_platform_integrations.py` — 62 call-sites
  - `core/views_auto_distribution.py` — 25 call-sites
  - `core/auth_middleware.py` — 10 call-sites
  - `core/views_revenue_analytics.py` — 8 call-sites
  - `core/views_odds_sports.py` — 3 call-sites

  Estimate: **4-6 sessions** once policy is ratified (revised up from initial "2-3 sessions" after fresh grep surfaced 108, not ~14; batch per view file, with `views_platform_integrations.py`'s 62 sites likely spanning 2-3 of those sessions alone). Per-call-site pattern is `APIResponseEnvelope.error(message, error_code, status_code=X)` → `JsonResponse(build_user_facing_envelope(reason_code=Y), status=X)` where `Y` is chosen from `DRF_EXCEPTION_REASON_MAP` values.

  **Sub-task**: author lint / CI-grep gate per §4.2 to prevent Family B error-shape regression during and after migration.

  **Out of scope**: `core/api_helpers.py` (separate module) also exports `api_error` / `api_success` used by `core/views_ab_testing.py`, `core/views_learning_loop.py`, `core/views_rag_observability.py`, and `core/error_messages.py`. This is a different substrate; disposition is a future arc, not part of T-ENVELOPE-2-DEPRECATION.

  *(Close-notes below are execution records, not policy changes.)*

  **T-ENVELOPE-2-DEPRECATION CLOSED at S3011** (PRs #3695 / #3696 / #3697 / #3698 / #3699 / #3700 / #3691 / #3692 — all 108 sites across the 5 files above migrated to `emit_error_envelope()`; str(e) body-leak lint added).

  **T-ENVELOPE-3 (successor arc) CLOSED at S3012.** The out-of-scope `core/api_helpers.py` disposition mentioned above completed in 4 PRs:
  - PR #3701 (`04bc553ea`) — `core/views_ab_testing.py` 36 sites migrated (10 wired goals + 26 dead A/B testing handlers retained pending HALF_BUILT_FEATURES_AUDIT deletion).
  - PR #3702 (`3cffe6f0d`) — `core/views_learning_loop.py` 24 sites migrated (15 auth guards + 9 mixed).
  - PR #3703 (`055bd8734`) — `core/views_rag_observability.py` 12 sites migrated + bundled `status_code=` kwarg bug fix (behavior restoration: 10 endpoints were silently 500-ing due to `api_error` rejecting the kwarg; now correctly return 401/403/500).
  - PR 4 (this PR) — `api_error()` function retired from `core/api_helpers.py`. Zero real callers remained after PRs 1-3. `agents/views_monitoring.py`'s `api_error` is a DIFFERENT function (`core.api_responses.api_error`) — out of T-ENVELOPE-3 scope.

  S3011 audit reality-check: original audit counted 92 caller sites across 4 primary + 6 minor files; real callers were 72 (11 tasks_conversations + 6 minor files were all false positives — variable names + string literal error-type labels).

  `core/error_messages.py` uses a different helper (`parse_api_error`) — out of scope.

### 4.4 What this ADR does NOT change

- **γ mechanism** (ADR-0005/0006 §3.1) — unchanged. Layer 1 (QueryClient default onError) + Layer 2 (top-level ErrorBoundary) + Layer 3 (per-hook opt-in) continue to be shape-agnostic per §3.3.
- **SHAPE-BLIND interceptor** (ADR-0005/0006 §3.3) — unchanged. `api.ts:63-82` continues to read `status` + `URL` substring only. Family E consumption by the frontend requires no interceptor change.
- **Nested UX policy** (ADR-0005/0006 §3.4) — unchanged. SessionExpiredModal + authFailureStore (S3004) continue to work independently of envelope shape.
- **F-C-VIP-1 scope-tightening** (ADR-0005/0006 §3.5) — unchanged. VIP-expiry UX (S3003 T-VIP-1 + S3004 §3.5 UX widening) is shipped and independent.
- **Families A/C/D presence** (ADR-0005 §2 line 71-74) — unchanged. This ADR ratifies Family E as the canonical ERROR-RESPONSE SoT; it does NOT force Family A/C/D retirement. Their coexistence per γ Layer 1 shape-agnostic handling remains valid.

### 4.5 Docs cascade

At ADR PR merge:

- `docs/INDEX.md` gains a new ADR-0007 entry (autogen per `build_docs_index`).
- `docs/_provenance.json` gains ADR-0007 provenance metadata.
- ADR-0007 body embedded via `embed_documents --all-unembedded`.
- ADR-0006 body gets an in-place note at §3.2 pointing to ADR-0007 as the refinement.
- `core/api_responses.py` docstrings on the deprecated methods get `@deprecated` markers pointing to ADR-0007.
- Twin-mirror per `feedback_twin_deliverable_at_every_ratification` — content mirror + ratification envelope created by Rigby in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`.

## 5. Alternatives considered

### 5.1 A1 — "Family E IS the actual SoT; retire Family B entirely" (rejected)

Rewrite ADR-0006 §3.2 to declare Family E as SoT for BOTH error AND success responses. Retire APIResponseEnvelope. Migrate 108+ Family B call-sites to build a hypothetical `build_success_envelope` in `core.security.error_envelope`.

**Rejected because:** (1) Family E is deliberately an ERROR envelope — its fields `support_code`, `reason_code`, `retryable`, `terminal_state` have no semantic meaning for success responses; it does not model success payloads (`data`, `meta`, pagination); (2) forcing success-response shape into an error-envelope substrate loses semantic clarity; (3) unnecessary migration churn on 108+ Family B success + error call-sites that already work correctly for their respective domains.

### 5.2 A3 — "Reset to Family B EVERYWHERE; retire Family E" (rejected)

Retire safety-contract handler, migrate all exception-path emission to APIResponseEnvelope shape.

**Rejected because:** (1) violates I-0301 safety-contract §8.1 — Family E's `human_message` copy-safety enforcement + support_code enum + retryable/terminal_state semantics are load-bearing for the safety-contract; (2) requires safety-contract-level ratification to unwind (this ADR is not authorized to touch that substrate); (3) implicit surface is massive (every DRF exception + every uncaught non-DRF exception) — migration blast radius unbounded; (4) removes a working substrate to replace it with a less-capable one.

### 5.3 In-place amendment of ADR-0006 §3.2 (rejected)

Directly edit ADR-0006 §3.2 body to describe the layered policy, without a new ADR-0007.

**Rejected because:** violates ADR-0001 §3.6 supersede discipline. ADR content is truth-history — governance-relevant changes come via new ADRs. Rigby's zoom-out guidance during joint diagnosis: "prefer new ADR if the intended end-state is layered / multi-domain, because it formally inventories and dispositions the substrates." The end-state IS layered (§3.1 + §3.2), so a new ADR is the right shape.

### 5.4 Defer the reconciliation to future arc (rejected)

Leave the doc-vs-runtime drift unresolved; proceed with S3005 as different-arc work.

**Rejected because:** every future ADR-0005/0006 T-slot arc (T-ENVELOPE-4 migration, T-ENVELOPE-5 interceptor elevation, T-ENVELOPE-6 telemetry) inherits the ambiguity. Each would need to answer "which envelope shape are we targeting?" independently. Ratifying now is 1 session; deferring compounds cost across N future arcs. Also violates the substrate-first workflow lean established in S3003→S3004 (fix the substrate before shipping downstream UX).

## 6. Reversibility

**Reversibility scale (per ADR-0001 §3.5): 5 (trivially reversible).**

Rollback method:

1. `git revert <ADR-0007-merge-commit-sha>` — removes ADR-0007 file + reverts the ADR-0006 §3.2 in-place note + reverts the `core/api_responses.py` `@deprecated` docstring markers.
2. `docs/INDEX.md` + `docs/_provenance.json` unflip via revert (or re-run `build_docs_index` + `build_docs_provenance`).
3. `DocumentEmbedding` rows for the removed file — orphan cleanup per ADR-0004 §6 F21 precedent.

**No irreversible operations. No DB migration. No feature flag change. No runtime code change. No API surface change. No Celery task change.**

Deprecation of `APIResponseEnvelope.error()` and adjacents is annotation-only; existing callers continue to function at revert.

**Rollback triggers:**
- Rigby SIGN post-merge returns BLOCKED verdict (unlikely; T1 SIGN pre-merge).
- Chris explicit override.
- Discovery that Family E's I-0301 authorization does not actually extend to non-exception explicit-error emission (unlikely; safety-contract §8.1 applies broadly).

**Post-rollback state:**
- ADR-0006 §3.2 returns to Family-B-as-SoT declaration.
- ADR-0007 removed from corpus.
- Docstring deprecation markers reverted.
- Runtime behavior unchanged (Family E still emits from EXCEPTION_HANDLER + middleware; Family B still emits from `APIResponseEnvelope.*` callers).

## 7. Provenance

- **Author.** Claude Code, S3005 opening session, 2026-07-27.
- **Chris ratification.** "yes author ADR-0007" 2026-07-27 via Rigby PA chat, following joint Claude+Rigby recommendation per `feedback_claude_rigby_agree_first_chris_yes_no`. Three-part plain-English framing (do-we-lose-anything / more-work-later / ≤1 decision) per PLAYBOOK-7.7.3 + `feedback_plain_english_decision_framing_for_chris`.
- **Rigby joint diagnosis.** T1-equivalent SPEC-INVALIDATION verification + A4 recommendation (reconciliation ADR first) via 8 real tool_runs across two turns. AGREE on all 4 verifications (handler wiring / shape comparison / baseline mismatch / consumer surface). Recommended new ADR (vs amend) for layered end-state.
- **Session context.** S3005 opened with Chris directive "start s3005 with option A" (T-ENVELOPE-2). Spec-invalidation surfaced in first 5 minutes of code probing per `feedback_cycle_1a_verify_before_build`. Redirect to A4 (reconciliation ADR) proposed + ratified before any implementation touched.

### 7.1 Consumed sources (verified at HEAD `85fffdfc1`)

- `core/settings.py:747` — EXCEPTION_HANDLER wiring (direct file read).
- `core/settings.py:295` — RURErrorEnvelopeMiddleware in MIDDLEWARE list (direct file read).
- `core/security/error_envelope.py:72-114` — Family E build function (direct file read).
- `core/security/error_envelope.py:248-305` — Layer 1 drf_exception_handler (direct file read).
- `core/security/error_envelope.py:313-365` — Layer 2 RURErrorEnvelopeMiddleware (direct file read).
- `core/api_responses.py:15-234` — APIResponseEnvelope class + module helpers (direct file read).
- `docs/adr/ADR-0005-typed-error-envelope-contract.md` §2 line 25, §3.2, §4.1 T-ENVELOPE-2 (direct file read).
- `docs/adr/ADR-0006-typed-error-envelope-contract-non-provisional.md` §3 (direct file read).
- `PR #3085 commit 40959cd66` — Family E substrate shipment (git log --diff-filter=A verification).
- ADR-0001 §3.6 (supersede/lifecycle discipline).

## 8. Follow-on ADRs

This ADR introduces one new T-slot (§4.3) and does not spawn immediate follow-on ADRs. Candidate future ADRs, dependent on T-ENVELOPE-2-DEPRECATION execution:

- **ADR-N (safety-contract §5.1 support_code enum expansion)** — if migration surfaces new reason_codes not in the existing enum. Requires I-0301 safety-contract successor.
- **ADR-N (Family A/C/D final disposition)** — currently ADR-0005 §2 tolerates their coexistence via γ Layer 1 shape-agnostic handling. If a future arc wants to migrate all error emission through Family E, that's a separate substrate-level decision.
- **ADR-N (frontend authFailureStore variant expansion for reason_code discrimination)** — currently the S3004 authFailureStore branches on the `X-VIP-Expired` header only; a future arc could branch on Family E `reason_code` values for finer-grained modal variants. Not required by this ADR.

## 9. Amendment linkage

This ADR refines **ADR-0006 §3.2**. The `refines:` frontmatter field (non-schema) is added as a grep target; readers looking for "what amended ADR-0006 §3.2" can find this ADR via `grep -r "refines: ADR-0006" docs/adr/`. ADR-0006 body gets an in-place note at §3.2 pointing to ADR-0007 in the same PR that ratifies this ADR.

Future readers of ADR-0006 §3.2 MUST consult ADR-0007 for the current-truth policy. ADR-0005 §3.2 remains as truth-history; readers seeing that citation should follow the supersede chain to ADR-0006 then to ADR-0007.
